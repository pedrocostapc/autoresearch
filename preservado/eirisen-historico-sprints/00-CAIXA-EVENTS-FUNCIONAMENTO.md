# Caixa Events — Como Funciona

> Documento técnico sobre a caixa de eventos do Risen.
> Schema, uso, tool, payload.
> Atualizado: 11/05/2026

---

## 1. CONTEXTO E PROPÓSITO

A caixa **Events** representa eventos, festas, locações ou pacotes que o tenant oferece e que tem **data definida** ou **estrutura própria de cotação**.

### Quando usar Events vs outras caixas

| Cenário | Caixa correta |
|---|---|
| Produto físico vendável | Products |
| Serviço com agendamento curto (consulta, sessão) | Services |
| Festa, casamento, evento específico com pacotes | **Events** |
| Locação de espaço por horas | Events |
| Cardápio pra delivery | Delivery Items |

### Casos de uso reais

| Tenant tipo | Exemplos |
|---|---|
| Buffet / Festas | Casamento, Aniversário 15 anos, Festa Infantil |
| Espaço de eventos | Locação Salão A, Locação Área Externa |
| Estúdio fotográfico | Ensaio Gestante, Casamento, Newborn |
| Hotel / Pousada | Pacote Réveillon, Pacote Carnaval, Week-end Romântico |
| Aula / Workshop | Workshop Marketing 14/06, Curso Sommelier 20-22/07 |
| Restaurante temático | Jantar Italiano 30/05, Brunch Domingo |

---

## 2. ARMAZENAMENTO

### Tabela
`persona_boxes`

### Identificação
```
box_type = 'events'
tenant_id = <uuid>
data = JSONB com array de items
is_active = true
```

### Estrutura JSONB

```json
{
  "items": [
    {
      "name": "Casamento Pacote Premium",
      "description": "Pacote completo com decoração, buffet e DJ",
      "date_start": "2026-08-15",
      "date_end": "2026-08-15",
      "location": "Salão Vitória",
      "capacity_min": 50,
      "capacity_max": 200,
      "price": 12000,
      "price_per_person": null,
      "duration": "8 horas",
      "what_includes": "Decoração temática, buffet completo, DJ, cerimonialista",
      "what_excludes": "Bebidas alcoólicas, fotografia",
      "restrictions": "Reserva mínima 60 dias antes",
      "ai_notes": "Sempre confirmar data + número de convidados antes de cotar",
      "available": "Sim",
      "category": "Casamento"
    }
  ]
}
```

---

## 3. CAMPOS POR EVENTO

| Bloco | Campo | Tipo | Descrição |
|---|---|---|---|
| **1 - Identidade** | `name` | text (obrigatório) | Nome do evento |
| | `description` | text | Descrição detalhada |
| | `category` | text | Categoria livre (Casamento, Aniversário, Workshop, etc) |
| **2 - Data e local** | `date_start` | date | Data início (se fixa) |
| | `date_end` | date | Data fim (se mais de 1 dia) |
| | `location` | text | Local do evento |
| **3 - Capacidade** | `capacity_min` | number | Mínimo de pessoas |
| | `capacity_max` | number | Máximo de pessoas |
| | `duration` | text | Duração do evento |
| **4 - Preço** | `price` | number | Preço total (se fixo) |
| | `price_per_person` | number | Preço por pessoa (se variável) |
| **5 - Pacote** | `what_includes` | text | O que inclui |
| | `what_excludes` | text | O que NÃO inclui |
| | `restrictions` | text | Regras, restrições, prazos |
| **6 - Direcionamento IA** | `ai_notes` | text | Notas pra IA usar no atendimento |
| **7 - Status** | `available` | Sim / Não / Sob consulta | Disponibilidade atual |

---

## 4. EVENTO FIXO VS EVENTO RECORRENTE

### Evento com data fixa (data única)

```
name: "Réveillon 2026"
date_start: "2026-12-31"
date_end: "2027-01-01"
price: 850
price_per_person: null
location: "Hotel Praia"
```

IA entende: evento acontece numa data específica.

### Evento recorrente / pacote (sem data fixa)

```
name: "Pacote Casamento Premium"
date_start: null
date_end: null
price: null
price_per_person: 250
capacity_min: 50
capacity_max: 300
```

IA entende: cliente escolhe a data, valor depende do número de convidados.

### Como IA decide o caminho

**Se `date_start` está preenchido:**
- IA confirma data com cliente
- Verifica disponibilidade
- Cota preço total

**Se `date_start` é null:**
- IA pergunta data desejada
- Pergunta número de convidados
- Calcula preço (price OR price_per_person × convidados)

---

## 5. ACESSO PELA IA

### Tool: `query_events`

**Localização:** `supabase/functions/_shared/persona-tools.ts`

**Input schema (provável):**
```typescript
{
  search?: string;       // texto buscado em nome/descrição/categoria
  date_range_start?: string;  // ISO date - filtra eventos a partir desta data
  date_range_end?: string;    // ISO date - filtra eventos até esta data
  category?: string;     // filtra por categoria
  available_only?: boolean;   // default true
  limit?: number;        // default 50, max 200
}
```

### Como a IA chama

```typescript
// Cliente: "tem festa de casamento?"
query_events({ search: "casamento" })

// Cliente: "tem festa de réveillon?"
query_events({ search: "réveillon" })

// Cliente: "quais pacotes vocês têm pra agosto?"
query_events({ date_range_start: "2026-08-01", date_range_end: "2026-08-31" })
```

### Retorno (padrão Risen pós PR #235)

```json
{
  "total_matches": 3,
  "returned": 3,
  "truncated": false,
  "items": [
    {
      "name": "Pacote Casamento Premium",
      "description": "...",
      "date_start": null,
      "date_end": null,
      "location": "Salão Vitória",
      "capacity_min": 50,
      "capacity_max": 200,
      "price": null,
      "price_per_person": 250,
      "duration": "8 horas",
      "what_includes": "Decoração, buffet, DJ",
      "what_excludes": "Bebidas alcoólicas, fotografia",
      "restrictions": "Reserva mínima 60 dias antes",
      "ai_notes": "Sempre confirmar data + número de convidados antes de cotar",
      "available": "Sim",
      "category": "Casamento"
    }
  ]
}
```

---

## 6. FLUXO DE ATENDIMENTO TÍPICO

### Cenário 1 — Evento com data fixa

```
Cliente: "tem festa de fim de ano?"
IA → query_events({ search: "fim de ano réveillon natal" })
Tool retorna: [Réveillon 2026]

IA: "Sim! Temos o Réveillon 2026 no Hotel Praia, dia 31/12/26 a 01/01/27.
     Pacote completo R$850 por pessoa, com ceia e show.
     Quantas pessoas vão?"

Cliente: "4 pessoas"
IA: "Total: R$3.400 pra 4 pessoas. 
     Quer prosseguir com a reserva? Vou te conectar com o responsável."

→ Encerramento 3 mensagens → query_team setor "eventos"
```

### Cenário 2 — Evento recorrente (cliente escolhe data)

```
Cliente: "quanto custa um casamento aí?"
IA → query_events({ search: "casamento" })
Tool retorna: [Pacote Casamento Premium]

IA: "Temos o Pacote Casamento Premium, R$250 por pessoa (mínimo 50, máximo 200).
     Inclui: decoração temática, buffet, DJ, cerimonialista.
     Não inclui: bebidas alcoólicas, fotografia.
     
     Pra cotar exato, preciso de:
     - Data desejada
     - Número de convidados"

Cliente: "20/03/2027, 120 pessoas"
IA: "Pra 120 pessoas: R$30.000.
     Atende! Reserva mínima 60 dias antes, está OK.
     Quer prosseguir? Vou te conectar com o responsável."

→ Encerramento 3 mensagens
```

---

## 7. DIFERENÇAS DE OUTRAS CAIXAS

### Events vs Products

| Aspecto | Products | Events |
|---|---|---|
| Data | Não tem | Pode ter (date_start/end) |
| Pessoas/Capacidade | Não tem | capacity_min/max |
| Preço | Fixo por unidade | Total OU per_person |
| Pacote incluso | Não tem | what_includes/excludes |
| Tool | query_products | query_events |

### Events vs Services

| Aspecto | Services | Events |
|---|---|---|
| Agendamento | search_team_slots + create_appointment | Manual via encerramento |
| Duração típica | Curto (30min - 2h) | Longo (4h - dias) |
| Profissional | tem_profissional_responsavel | Equipe ou parceiros externos |
| Múltiplas pessoas | Geralmente 1 cliente | Sempre coletivo (festa) |
| Calendar integration | Sim | Não (cotação manual) |

---

## 8. UI DE EDIÇÃO

### No painel CRM

Caixa Events fica em: **Painel → IA → Persona → Bloco Events** (se preenchido)

### Inputs do usuário

- Card por evento (colapsável)
- Modo Excel disponível pra importação em massa
- Campos validados (data formato ISO, números, etc)

### Validações implícitas

- `name` obrigatório
- Se `date_start` preenchido, `date_end` ≥ `date_start`
- Pelo menos um de `price` OU `price_per_person`
- `capacity_min` ≤ `capacity_max`

---

## 9. ENCERRAMENTO ESPERADO

Como toda triagem do Risen, eventos terminam com **3 mensagens separadas** (MSG 1 + MSG 2 + MSG 3):

**MSG 1:** Resumo com bullets:
```
🎉 *Reserva*

• Pacote: Casamento Premium
• Data: 20/03/2027
• Convidados: 120 pessoas
• Total estimado: R$30.000
• Inclui: decoração, buffet, DJ, cerimonialista
• Não inclui: bebidas, fotografia

Tá tudo certo?
```

**MSG 2:** Link wa.me do responsável.

**MSG 3:** Texto puro copiável.

---

## 10. CASOS QUE A CAIXA NÃO COBRE BEM

### Calendar disponibilidade real

Events **NÃO** se integra com Calendar Service Account. Tool só lista eventos, não verifica conflitos.

**Implicação:** se 2 clientes querem casar no mesmo dia, IA não sabe. Encaminha pra humano que confere agenda.

**Solução futura:** integrar Events com Calendar Service Account (sprint maior).

### Preço variável complexo

Não suporta tabela de descontos automáticos por quantidade ou regras condicionais complexas.

**Solução atual:** usar `ai_notes` pra documentar regras textualmente. IA repassa pro humano.

### Múltiplos pacotes do mesmo evento

Se "Casamento" tem 3 pacotes (Básico/Premium/Top), cada um vira **item separado** no JSONB com `name` diferenciador.

---

## 11. INTEGRAÇÕES POTENCIAIS (FUTURAS)

- **Calendar Service Account** — verificar disponibilidade da data
- **Pagamento parcelado** — link Stripe pra sinal + parcelas
- **Contrato digital** — gerar PDF + assinatura OTP (sprint Forms)
- **Galeria de fotos** — anexar fotos de eventos passados (sprint SU7 image send)

---

## 12. EXEMPLO COMPLETO — TENANT BUFFET

### 3 itens cadastrados

```json
{
  "items": [
    {
      "name": "Casamento Pacote Básico",
      "category": "Casamento",
      "price_per_person": 150,
      "capacity_min": 50,
      "capacity_max": 150,
      "what_includes": "Buffet + decoração básica",
      "what_excludes": "DJ, decoração temática, fotografia",
      "available": "Sim",
      "ai_notes": "Pacote pra quem busca economia"
    },
    {
      "name": "Casamento Pacote Premium",
      "category": "Casamento",
      "price_per_person": 250,
      "capacity_min": 50,
      "capacity_max": 200,
      "what_includes": "Buffet, decoração temática, DJ, cerimonialista",
      "what_excludes": "Bebidas alcoólicas, fotografia",
      "available": "Sim",
      "ai_notes": "Mais popular. Sempre oferecer primeiro."
    },
    {
      "name": "Aniversário Infantil",
      "category": "Aniversário",
      "price": 2500,
      "capacity_min": 20,
      "capacity_max": 50,
      "duration": "4 horas",
      "what_includes": "Decoração temática, bolo, salgados, recreador",
      "what_excludes": "Brinquedo inflável",
      "available": "Sim"
    }
  ]
}
```

### Conversa real esperada

```
Cliente: "quero fazer minha festa de casamento"
IA: query_events({ search: "casamento" })
   → retorna 2 pacotes (Básico, Premium)
IA: "Temos 2 opções de casamento:
     
     *Pacote Básico* - R$150/pessoa
     • Buffet + decoração básica
     
     *Pacote Premium* - R$250/pessoa  
     • Buffet + decoração temática + DJ + cerimonialista
     
     Quantos convidados aproximadamente? E qual data você tem em mente?"

Cliente: "uns 100 convidados, agosto"
IA: "Premium pra 100 pessoas dá R$25.000. Posso reservar agosto?
     Preciso da data específica pra confirmar disponibilidade."
```

---

**Fim do documento.**
