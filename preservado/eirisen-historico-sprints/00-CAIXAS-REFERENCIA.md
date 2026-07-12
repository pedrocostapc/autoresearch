# Caixas do Risen — Referência Completa

> Catálogo de todas as caixas (`persona_boxes`) do sistema com schema, campos, uso pela IA e exemplos.
> Atualizado: 11/05/2026

---

## Visão geral

Cada caixa armazena um tipo de informação do estabelecimento. As caixas dividem-se em 2 tipos de consumo pela IA:

| Tipo | Comportamento | Caixas |
|---|---|---|
| **Inline (no system_prompt)** | Conteúdo inteiro entra no contexto da IA | Establishment, Hours, Links, Pagamento, FAQ, Objections, Delivery Config, Calendar Config, Custom |
| **Tool-only** | IA chama tool específica sob demanda | Products, Services, Team, Forwards, Delivery Items, Delivery Areas, Events |

Razão: caixas grandes/buscáveis vão por tool pra economizar tokens. Caixas pequenas e referência geral vão inline.

---

## SEÇÃO 1 — IDENTIDADE

### 1.1 Establishment (estabelecimento)

**Box type:** `establishment`
**Tipo de consumo:** Inline
**Multi-item:** Não (singleton)
**Tem Excel:** Não

**Campos:**

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `name` | text | Sim | Nome do estabelecimento |
| `cnpj` | text | Não | CNPJ |
| `address_street` | text | Não | Rua/avenida + número |
| `address_neighborhood` | text | Não | Bairro |
| `address_city` | text | Não | Cidade |
| `address_state` | text | Não | UF (sigla) |
| `address_zip` | text | Não | CEP |
| `history` | textarea | Não | História da empresa |
| `differentiator` | textarea | Não | Diferenciais |
| `mission` | textarea | Não | Missão |
| `values` | textarea | Não | Valores |
| Outros campos custom | - | Não | Conforme schema atual |

**Exemplo (EUCA Brasil):**
```json
{
  "name": "EUCA Brasil",
  "address_zip": "39277899",
  "address_city": "Pirapora",
  "address_street": "ROD BR 365, Rua Aeroporto, KM 159",
  "address_neighborhood": "AREA RURAL"
}
```

**Uso pela IA:**
- IA usa `name` na apresentação ("Sou a Risen, da [name]")
- Endereço quando cliente pergunta localização
- História/diferenciais ao explicar a empresa

---

### 1.2 Hours (horários)

**Box type:** `hours`
**Tipo de consumo:** Inline
**Multi-item:** Não (singleton)
**Tem Excel:** Não

**Campos:**

| Campo | Tipo | Descrição |
|---|---|---|
| `weekly_hours` | objeto | 7 dias × 2 turnos cada |
| `holidays_policy` | text | Política de feriados |
| `closed_dates` | array | Datas específicas fechadas |

**Estrutura `weekly_hours`:**
```json
{
  "monday": { "morning_open": "08:00", "morning_close": "12:00",
              "afternoon_open": "13:00", "afternoon_close": "18:00" },
  "tuesday": { ... },
  ...
}
```

**Uso pela IA:**
- Responde "que horas abre/fecha?"
- Ajusta frase de retorno conforme horário (Hours = "Te retornam ainda hoje" vs "Próximo dia útil")

---

### 1.3 Links

**Box type:** `links`
**Tipo de consumo:** Inline
**Multi-item:** Singleton (mas com array dentro)
**Tem Excel:** Não

**Campos fixos (13):**
- `site_url`
- `instagram_url`
- `facebook_url`
- `whatsapp_url`
- `youtube_url`
- `tiktok_url`
- `linkedin_url`
- `google_maps_url`
- `catalog_url`
- `menu_url`
- `booking_url`
- `payment_url`
- `complaints_url`

**Campo array:** `custom_links` (lista `{label, url}`)

**Uso pela IA:**
- Envia link quando cliente pede ("manda o catálogo")
- Direciona pra agendamento online
- Link de pagamento

---

### 1.4 Pagamento

**Box type:** `pagamento`
**Tipo de consumo:** Inline
**Multi-item:** Não (singleton)
**Tem Excel:** Não

**21 campos em 5 blocos:**

**Bloco PIX:**
- `tem_pix` (Sim/Não)
- `pix_key`
- `pix_key_type`
- `pix_owner_name`

**Bloco Banco:**
- `tem_banco` (Sim/Não)
- `banco_name`
- `agencia`
- `conta`
- `tipo_conta`
- `cnpj_cpf_titular`

**Bloco Cartão online:**
- `tem_link_pagamento` (Sim/Não)
- `link_pagamento_url`
- `parcelamento_max`

**Bloco Outras formas:**
- `accepts_boleto` (Sim/Não)
- `accepts_dinheiro` (Sim/Não)
- `accepts_cheque` (Sim/Não)

**Bloco Política IA:**
- `ia_pode_passar_pix` (Sim / Não / Confirmar antes)
- `ia_pode_negociar` (Sim/Não)
- `prazo_pagamento_padrao`
- `politica_parcelamento`
- `notes_para_ia` (texto livre)

**Uso pela IA:**
- Passa PIX direto se `ia_pode_passar_pix = "Sim"`
- Pergunta cliente antes se `= "Confirmar antes"`
- Encaminha pro financeiro se `= "Não"`

---

## SEÇÃO 2 — CATÁLOGO (TOOLS)

### 2.1 Products

**Box type:** `products`
**Tipo de consumo:** Tool (`query_products`)
**Multi-item:** Sim
**Tem Excel:** Sim
**Campos obrigatórios:** Apenas `name`

**Estrutura de cada item (17 campos):**

| Bloco | Campo | Descrição |
|---|---|---|
| **Bloco 1** | `name` | Nome do produto (obrigatório) |
| | `sku` | Código/SKU |
| | `brand` | Marca |
| | `category` | Categoria (livre) |
| | `description` | Descrição |
| **Bloco 2** | `price` | Preço normal |
| | `discount_price` | Preço com desconto |
| | `discount_condition` | Condição do desconto |
| | `unit` | Unidade (un, kg, m, etc) |
| **Bloco 3** | `available` | Disponível (Sim / Não / Sob encomenda) |
| | `stock` | Estoque |
| | `available_for_delivery` | Disponível pra delivery (Sim/Não) |
| **Bloco 4** (Atributos) | `prep_time` | Tempo de preparo |
| | `restrictions` | Restrições alimentares |
| | `ingredients` | Ingredientes/composição |
| **Bloco 5** (Variáveis) | `var_1` | Variação livre 1 |
| | `var_2` | Variação livre 2 |
| | `var_3` | Variação livre 3 |

**Como funciona com variações:**
- Catálogo com 6 nomes únicos × 243 variações de cada (caso Euca)
- IA chama `query_products(search: "varão")` → tool retorna 50 items + hint
- Hint: "243 itens. Variações: var_1: 4m, 5m, 6m | var_2: 06mm, 08mm | var_3: SP, RJ, MG"
- IA pergunta refinamento → não chama tool de novo, usa items do contexto

**Retorno da tool:**
```json
{
  "total_matches": 243,
  "returned": 50,
  "truncated": true,
  "hint": "...",
  "items": [
    { "name", "var_1", "var_2", "var_3", "price", "available", ... }
  ]
}
```

---

### 2.2 Services

**Box type:** `services`
**Tipo de consumo:** Tool (`query_services`)
**Multi-item:** Sim
**Tem Excel:** Sim
**Campos obrigatórios:** Apenas `name`

**Estrutura (20 campos em 6 blocos):**

- Nome, SKU, Categoria, Descrição
- Preço, Duração, Unidade
- Disponibilidade, Profissional padrão
- Requer agendamento? (`requires_appointment`)
- Bloco Direcionamento IA:
  - `trigger_keywords` (gatilhos pra IA chamar)
  - `requirements` (pré-requisitos cliente)
  - `dont_offer_when` (quando NÃO ofertar)
  - `ai_notes` (notas pra IA)

**Uso pela IA:**
- Cliente quer marcar consulta → `query_services` busca
- Se `requires_appointment=true` → encadeia com `search_team_slots`

---

### 2.3 Team (equipe)

**Box type:** `team`
**Tipo de consumo:** Tool (`query_team`)
**Multi-item:** Sim
**Tem Excel:** Sim

**Estrutura (21 campos em 4 blocos):**

- Nome, Cargo, Setor
- WhatsApp, Email, Foto
- Status (ativo/inativo)
- `ai_can_forward` (IA pode encaminhar?)
- `has_own_calendar` (tem agenda própria?)
- Especialidades, Idiomas
- Horário de atendimento custom

**Privacidade:**
- Se `ai_can_forward="Não"` → tool omite o membro
- Mobile fica privado nesse caso

**Uso pela IA:**
- Cliente pede "quero falar com vendedor" → `query_team(sector: "vendas")`
- Encerramento 3 msgs sempre menciona cargo + nome + link wa.me

---

### 2.4 Forwards (parceiros externos)

**Box type:** `forwards`
**Tipo de consumo:** Tool (`query_forwards`)
**Multi-item:** Sim
**Tem Excel:** Sim

**Estrutura (14 campos em 4 blocos):**

- Nome, Empresa, Categoria
- WhatsApp, Email, Telefone
- Especialidade
- Notas IA

**Diferença de Team:**
- Forwards = pessoa/empresa **EXTERNA** que o estabelecimento indica
- Team = pessoa **INTERNA** do estabelecimento

**Privacidade:** WhatsApp sempre visível (diferente de Team).

**Uso pela IA:**
- Cliente precisa de algo que estabelecimento não faz mas tem indicação
- IA passa link wa.me + apresentação

---

### 2.5 Delivery Items

**Box type:** `delivery_items`
**Tipo de consumo:** Tool (`query_delivery_items`)
**Multi-item:** Sim
**Tem Excel:** Sim

**Estrutura:**
- Mesmo schema que Products (reuso)
- Diferença: representa o cardápio/menu específico de delivery
- Se vazio: fallback automático pra Products filtrado por `available_for_delivery="Sim"`

**Uso pela IA:**
- "Qual o cardápio?" → `query_delivery_items`
- Se empty → tool faz fallback Products

---

### 2.6 Delivery Areas

**Box type:** `delivery_areas`
**Tipo de consumo:** Tool (`query_delivery_areas`)
**Multi-item:** Sim
**Tem Excel:** Sim

**Estrutura (10 campos):**

| Campo | Descrição |
|---|---|
| `neighborhood` | Bairro/Região |
| `city` | Cidade |
| `zip_start` | CEP inicial |
| `zip_end` | CEP final |
| `delivery_fee` | Taxa de entrega |
| `eta_minutes` | Tempo estimado (min) |
| `minimum_order` | Pedido mínimo nesta área |
| `max_distance_km` | Distância máxima |
| `restrictions` | Atende com restrição |
| `ai_notes` | Observações pra IA |

**⚠️ Bug conhecido:** valor `delivery_fee` armazenado como reais (`7080` = R$7.080), mas tool/IA pode interpretar como centavos. Investigação pendente.

**Uso pela IA:**
- Cliente fala bairro/CEP → tool busca match
- IA confirma taxa + tempo + pedido mínimo

---

### 2.7 Events

**Box type:** `events`
**Tipo de consumo:** Tool (`query_events`)
**Multi-item:** Sim
**Tem Excel:** Sim

**Estrutura:**
- Nome do evento
- Data, Local, Capacidade
- Pacotes (incluso/não incluso)
- Preços
- Restrições

**Uso pela IA:**
- Cliente quer locação/festa → `query_events`
- IA mostra opções + encaminha pra responsável

---

## SEÇÃO 3 — REGRAS E CONFIGURAÇÕES

### 3.1 FAQ

**Box type:** `faq`
**Tipo de consumo:** Inline
**Multi-item:** Sim (mas no contexto)
**Tem Excel:** Sim

**Estrutura por item:**
- Pergunta
- Resposta
- Categoria
- `trigger_keywords` (gatilhos)

**Uso pela IA:**
- Quando cliente faz pergunta que bate com FAQ, IA responde direto
- Sem tool — todas FAQs vão inline

---

### 3.2 Objections

**Box type:** `objections`
**Tipo de consumo:** Inline
**Multi-item:** Sim
**Tem Excel:** Sim

**Estrutura por item:**
- Objeção comum (texto)
- Contorno/resposta
- Categoria
- `trigger_keywords`

**Exemplo:**
- Objeção: "Tá caro"
- Contorno: "Entendo. Nosso valor reflete X, Y, Z. Posso te mostrar nossas formas de pagamento?"

**Uso pela IA:**
- Cliente externaliza objeção → IA aplica contorno

---

### 3.3 Delivery Config

**Box type:** `delivery_config`
**Tipo de consumo:** Inline
**Multi-item:** Não (singleton form)

**Campos:**
- `pedido_minimo_geral` (R$)
- `horario_delivery` (inicio/fim)
- `politicas_delivery` (texto)
- `escalation_humano` (regras pra escalar)
- `tem_taxa_fixa` (Sim/Não)
- `taxa_fixa_valor`
- `gratis_acima_de` (valor)

**Uso pela IA:**
- Avisa cliente se pedido está abaixo do mínimo
- Confirma horário de delivery
- Aplica taxa fixa quando aplicável

---

### 3.4 Calendar Config

**Box type:** `calendar_config`
**Tipo de consumo:** Inline
**Multi-item:** Não (singleton)

**Campos:**
- `default_slot_duration` (min)
- `slot_buffer` (min entre slots)
- `working_hours_per_profissional`
- `cancellation_policy` (texto)
- `confirmation_required` (boolean)
- `reminder_hours_before`

**Uso pela IA:**
- Limita janelas de busca em `search_team_slots`
- Aplica buffer entre agendamentos
- Informa política de cancelamento

---

### 3.5 Custom

**Box type:** `custom`
**Tipo de consumo:** Inline
**Multi-item:** Sim
**Tem Excel:** Não

**Estrutura por item:**
- `label` (título do bloco)
- `content` (texto livre)
- `category` (opcional)

**Quando usar:**
- Informações específicas do tenant que não cabem nas caixas padrão
- Ex: "Política de devolução", "Como funciona meu serviço de pintura", "Calendário sazonal"

---

## SEÇÃO 4 — RESUMO RÁPIDO

| Caixa | Inline/Tool | Multi-item | Excel | Obrigatório |
|---|---|---|---|---|
| Establishment | Inline | Não | Não | Nome |
| Hours | Inline | Não | Não | - |
| Links | Inline | Não | Não | - |
| Pagamento | Inline | Não | Não | - |
| **Products** | **Tool** | Sim | Sim | Nome |
| **Services** | **Tool** | Sim | Sim | Nome |
| **Team** | **Tool** | Sim | Sim | Nome |
| **Forwards** | **Tool** | Sim | Sim | Nome+WhatsApp |
| **Delivery Items** | **Tool** | Sim | Sim | Nome |
| **Delivery Areas** | **Tool** | Sim | Sim | Bairro/Região |
| **Events** | **Tool** | Sim | Sim | Nome |
| FAQ | Inline | Sim | Sim | - |
| Objections | Inline | Sim | Sim | - |
| Delivery Config | Inline | Não | Não | - |
| Calendar Config | Inline | Não | Não | - |
| Custom | Inline | Sim | Não | - |

---

## SEÇÃO 5 — TOOLS CORRESPONDENTES

| Tool | Caixa | Argumentos |
|---|---|---|
| `query_products` | Products | search, category, available_only, limit |
| `query_services` | Services | search, sector, requires_appointment, limit |
| `query_team` | Team | sector, name, role |
| `query_forwards` | Forwards | search, category |
| `query_delivery_items` | Delivery Items | search, limit |
| `query_delivery_areas` | Delivery Areas | neighborhood, zip |
| `query_events` | Events | date_range, type |
| `search_team_slots` | Calendar Config + Team | service_id, professional_id, date_range |
| `create_appointment` | Calendar | tenant_id, service_id, slot, contact_data |
| `reschedule_appointment` | Calendar | appointment_id, new_slot |
| `cancel_appointment` | Calendar | appointment_id |

---

**Fim do documento.**
