# Risen — Estrutura Final das Caixas (10/05/2026)

> Documento de referência. Resultado das decisões de produto tomadas em 10/05/26.
> Substitui a estrutura antiga de 12 caixas. Base pra escopo das próximas sprints.

---

## Sumário

- **17 caixas** organizadas em 4 seções visuais
- **8 caixas com Excel** pra import em massa
- **3 caixas com perguntas** (Sim/Não, dropdowns, multipla escolha)
- **2 caixas com texto curto** (campos planos)
- **1 caixa de texto livre**
- **3 caixas form especializado** (sem Excel, mas estruturadas: Formulários, Agenda, Pagamento)

Princípios:
- **Apenas o essencial é obrigatório** (geralmente só Nome)
- **Dropdown como default** quando resposta é finita
- **Bloco "Direcionamento IA"** em todas as caixas multi-item
- **Reuso de dados** — Products serve Delivery, Services/Events servem Agenda, Team é fonte única de profissionais

---

## Mapa visual das seções

```
SEÇÃO IDENTIDADE
├── 1. Establishment      (texto curto)
├── 2. Hours              (perguntas)
├── 3. Links              (texto curto)
└── 4. Pagamento          (perguntas)        [NOVA]

SEÇÃO O QUE VOCÊ OFERECE
├── 5. Products           (Excel)
├── 6. Services           (Excel)
├── 7. Delivery Items     (Excel - opcional, fallback Products)  [NOVA]
├── 8. Delivery Areas     (Excel)            [NOVA]
├── 9. Delivery Config    (perguntas)        [NOVA]
└── 10. Events            (perguntas)

SEÇÃO ATENDIMENTO
├── 11. Team              (Excel) — modelo de 20 campos pronto
├── 12. Forwards          (Excel)
├── 13. FAQ               (Excel)
├── 14. Objections        (Excel)
├── 15. Formulários       (form especializado, sem Excel) [NOVA]
└── 16. Agenda            (form especializado, sem Excel) [NOVA]

SEÇÃO PERSONALIZE
└── 17. Custom            (texto livre, multi-row)
```

---

## Categorização por tipo de input

### Caixas com Excel pra baixar (8)
1. Products
2. Services
3. Delivery Items
4. Delivery Areas
5. Team
6. Forwards
7. FAQ
8. Objections

### Caixas com perguntas (Sim/Não, dropdowns) (3)
1. Hours
2. Pagamento
3. Delivery Config
4. Events

### Caixas com texto curto / campos planos (2)
1. Establishment
2. Links

### Caixas form especializado (sem Excel, lógica própria) (2)
1. Formulários (perguntas configuráveis + OTP)
2. Agenda (integração Google Calendar)

### Caixa texto livre (1)
1. Custom

---

# SEÇÃO 1: IDENTIDADE

## 1. Establishment (singleton, texto curto)

| Bloco | Campo | Tipo | Obrigatório |
|---|---|---|---|
| **Básico** | Nome | texto | ✅ |
| | CNPJ | texto | ❌ |
| | Razão social | texto | ❌ |
| **Endereço** | Logradouro | texto | ❌ |
| | Número | texto | ❌ |
| | Complemento | texto | ❌ |
| | Bairro | texto | ❌ |
| | Cidade | texto | ❌ |
| | Estado | UF | ❌ |
| | CEP | texto | ❌ |
| **Sobre** | Descrição (1-2 linhas) | texto | ❌ |
| | Ano de fundação | número | ❌ |
| | Diferenciais | texto CSV | ❌ |
| | Missão/valores | texto livre | ❌ |
| **Operação** | Atendimento | dropdown Loja física/Online/Híbrido | ❌ |
| | Política de troca/devolução | texto livre | ❌ |

---

## 2. Hours (singleton, perguntas)

Por dia da semana, com suporte a 2 turnos (almoço fechado):

| Por dia (Segunda → Domingo) | Campo | Tipo |
|---|---|---|
| | Fechado o dia | Sim/Não |
| | Abre 1º turno | hora |
| | Fecha 1º turno | hora |
| | Abre 2º turno (opcional) | hora |
| | Fecha 2º turno (opcional) | hora |
| **Especiais** | Feriados | texto livre |
| | Datas comemorativas com horário diferente | texto livre |
| | Observações | texto |

---

## 3. Links (singleton, texto curto)

| Bloco | Campo | Tipo |
|---|---|---|
| **Localização** | Google Maps URL | URL |
| **Redes sociais** | Instagram | texto (@handle) |
| | Facebook | URL |
| | TikTok | texto |
| | LinkedIn | URL |
| | YouTube | URL |
| | X/Twitter | texto |
| **Contato** | Site | URL |
| | Email | email |
| | Telefone fixo | texto |
| | WhatsApp Business | texto |
| **Catálogos** | Catálogo URL | URL |
| | Cardápio URL | URL |
| **Outros** | Lista `{label, url}` | array |

---

## 4. Pagamento (singleton, perguntas) **[NOVA]**

| Bloco | Campo | Tipo |
|---|---|---|
| **PIX** | Tem chave PIX? | Sim/Não |
| | Chave PIX | texto |
| | Titular | texto |
| **Banco** | Banco | texto |
| | Agência | texto |
| | Conta | texto |
| | Tipo | dropdown Corrente/Poupança |
| | Titular | texto |
| **Cartão online** | Tem link de pagamento online? | Sim/Não |
| | URL do link | URL |
| | Plataforma | dropdown Stripe/MercadoPago/Asaas/Outros |
| **Outras formas** | Aceita boleto? | Sim/Não |
| | Aceita débito presencial? | Sim/Não |
| | Aceita crédito presencial? | Sim/Não |
| | Aceita dinheiro? | Sim/Não |
| | Parcelamento | texto livre (ex: "até 12x sem juros") |
| **Política IA** | IA pode informar valor? | Sim/Confirmar/Não |
| | IA pode passar PIX direto? | Sim/Confirmar/Não |
| | IA pode enviar link de pagamento direto? | Sim/Confirmar/Não |
| | Quando escalar pra humano em pagamento | texto |
| | Observações | texto |

---

# SEÇÃO 2: O QUE VOCÊ OFERECE

## 5. Products (multi-item, Excel)

**17 colunas no Excel.** Apenas Nome obrigatório.

| Bloco | Campo | Tipo |
|---|---|---|
| **1. Identificação** | Nome | texto ✅ |
| | SKU | texto |
| | Marca | texto |
| | Categoria | texto livre |
| | Descrição | texto |
| **2. Preço** | Preço normal | número |
| | Preço com desconto | número |
| | Condição do desconto | texto livre |
| | Unidade | texto |
| **3. Disponibilidade** | Disponível? | dropdown Sim/Não/Sob encomenda |
| | Estoque | número |
| | Disponível pra delivery? | dropdown Sim/Não |
| **4. Atributos** | Tempo de preparo | texto (ex: "20min") |
| | Restrições alimentares | texto CSV |
| | Ingredientes/composição | texto livre |
| **5. Variáveis extras** | Var 1, Var 2, Var 3 | texto livre (nome da coluna definido pelo tenant) |

**Princípio:** variantes viram linhas separadas. "Blusa preta" e "blusa laranja" = 2 linhas.

---

## 6. Services (multi-item, Excel)

| Bloco | Campo | Tipo |
|---|---|---|
| **Identificação** | Nome | texto ✅ |
| | Categoria | texto livre |
| | Descrição | texto |
| | Apelidos | texto CSV |
| **Preço** | Preço | número |
| | Preço com desconto | número |
| | Condição do desconto | texto livre |
| | Unidade | texto (sessão/hora/m²/etc) |
| | Aceita orçamento? | dropdown Sim/Não/Sob consulta |
| **Tempo** | Duração estimada (minutos) | número |
| | Requer agendamento? | Sim/Não |
| | Antecedência mínima | texto |
| **Profissional** | Profissional responsável | texto (link Team) |
| | Especialidade necessária | texto |
| **Disponibilidade** | Disponível? | dropdown Sim/Não/Sazonal |
| | Dias da semana | texto CSV |
| **Direcionamento IA** | QUANDO oferecer (palavras-chave) | texto CSV |
| | Pré-requisitos / preparo | texto |
| | NÃO oferecer quando | texto livre |
| | Observações pra IA | texto |

20 campos.

---

## 7. Delivery Items (multi-item, Excel opcional) **[NOVA]**

**Schema idêntico a Products** (17 colunas).

**Lógica de fallback:**
- Se vazia → IA usa Products filtrado por `disponivel_pra_delivery=true`
- Se preenchida → IA usa Delivery Items
- Se preenchida E Products também → prioridade Delivery Items (mais específico)

**Casos de uso:**
- Restaurante com cardápio diferente do delivery
- Loja com itens específicos de delivery
- Cliente que prefere subir só Excel de delivery sem mexer em Products

---

## 8. Delivery Areas (multi-item, Excel) **[NOVA]**

| Bloco | Campo | Tipo |
|---|---|---|
| **Localidade** | Bairro/Região | texto ✅ |
| | Cidade | texto |
| | CEP inicial | texto |
| | CEP final | texto |
| **Logística** | Taxa de entrega | número |
| | Tempo estimado (min) | número |
| | Pedido mínimo nesta área | número |
| | Distância máxima (km) | texto |
| **Direcionamento IA** | Atende com restrição? | dropdown Sim/Não/Sob consulta |
| | Observações | texto |

10 campos.

---

## 9. Delivery Config (singleton, perguntas) **[NOVA]**

| Bloco | Campo | Tipo |
|---|---|---|
| **Operação** | Pedido mínimo geral | número |
| | Taxa de serviço (%) | número |
| | Horário de delivery | texto (pode diferir do horário da loja) |
| | Tempo médio geral (fallback) | texto |
| | Formas de pagamento aceitas | texto CSV |
| **Política** | Política de cancelamento | texto |
| | Política de produto avariado | texto |
| | Política de atraso | texto |
| **Direcionamento IA** | Como informar status do pedido | texto |
| | Quando escalar pra humano (ex: atraso > 30min) | texto |
| | Observações | texto |

11 campos.

---

## 10. Events (multi-pacote, perguntas em accordions)

51 campos divididos em accordions visuais. Cada pacote (auditório, área externa, combo) é uma linha.

### Accordion 1 - Identificação
| Campo | Tipo |
|---|---|
| Nome do pacote | texto ✅ |
| Tipo | dropdown Festa/Locação espaço/Workshop/Reunião/Outro |
| Descrição | texto |
| Apelidos / como cliente chama | texto CSV |

### Accordion 2 - Capacidade
| Campo | Tipo |
|---|---|
| Mínimo de pessoas | número |
| Máximo de pessoas | número |
| Layout do espaço | texto |
| Espaço (m²) | número |

### Accordion 3 - Estrutura
| Campo | Tipo |
|---|---|
| Estacionamento? | dropdown Sim/Não/Pago/Gratuito |
| Vagas de estacionamento | número |
| Acessibilidade PCD | dropdown Sim/Não/Parcial |
| Banheiros (qtd) | número |
| WiFi | Sim/Não |
| Cozinha disponível | dropdown Sim/Não/Equipada |

### Accordion 4 - Equipamentos
| Campo | Tipo |
|---|---|
| Som incluso | dropdown Sim/Não/Sob aluguel |
| Projetor/TV | dropdown Sim/Não/Sob aluguel |
| Microfone | dropdown Sim/Não/Sob aluguel |
| Mesas inclusas (qtd) | número |
| Cadeiras inclusas (qtd) | número |
| Louça/talher/copos | dropdown Sim/Não/Sob aluguel |
| Outros equipamentos extras | texto livre |

### Accordion 5 - Preço
| Campo | Tipo |
|---|---|
| Preço base dia útil | número |
| Preço base final de semana/feriado | número |
| Tabela de preço por faixa | texto livre |
| Preço por tipo de evento | texto livre |
| O que está incluso | texto livre |
| O que é extra (com valores) | texto livre |

### Accordion 6 - Logística
| Campo | Tipo |
|---|---|
| Horário de uso (das X às Y) | texto |
| Limite de som (horário/decibéis) | texto |
| Montagem dia anterior permitida? | dropdown Sim/Não/Depende |
| Custo da montagem dia anterior | número |
| Horário pra entrar dia anterior | texto |

### Accordion 7 - Regras de uso
| Campo | Tipo |
|---|---|
| Decoração na parede | dropdown Sim/Não/Com adesivo específico |
| Fornecedores terceiros liberados? | dropdown Sim/Não/Com aviso |
| Segurança obrigatória? | dropdown Sim/Não/Por conta do cliente |
| Seguro do espaço incluso? | Sim/Não |

### Accordion 8 - Cancelamento
| Campo | Tipo |
|---|---|
| Tem política formal | Sim/Não |
| Antecedência sem multa (dias) | número |
| Multa em cima da hora | texto |
| Reagendamento permitido | dropdown Sim/Não/Com taxa |
| Condições do reagendamento | texto livre |

### Accordion 9 - Contrato
| Campo | Tipo |
|---|---|
| Tem contrato formal | Sim/Não |
| Como envia | dropdown WhatsApp/Email/Presencial |

### Accordion 10 - Direcionamento IA
| Campo | Tipo |
|---|---|
| QUANDO oferecer (palavras-chave) | texto CSV |
| IA pode confirmar disponibilidade? | dropdown Sim/Confirmar/Não |
| IA pode passar valor sem confirmar? | dropdown Sim/Confirmar/Não |
| Profissional responsável | texto (link Team) |
| Backup se responsável tá fora | texto (link Team) |
| Observações pra IA | texto livre |

**Pagamento de Events sai daqui** — vai pra caixa Pagamento (compartilhada).

---

# SEÇÃO 3: ATENDIMENTO

## 11. Team (multi-item, Excel) — modelo de 20 campos

Modelo Excel já existe (Pedro forneceu).

| Bloco | Campo | Tipo |
|---|---|---|
| **Identificação** | Nome completo | texto ✅ |
| | Apelidos | texto CSV |
| | Setor | texto |
| | Cargo | texto |
| | Especialidade | texto |
| | Filial/Unidade | texto |
| **Contato** | Celular | texto E.164 |
| | Tem WhatsApp? | Sim/Não |
| | Telefone fixo/Ramal | texto |
| | Email | email |
| | Tipo do número | dropdown Empresa/Privado |
| | Canal preferido | dropdown WhatsApp/Email/Telefone |
| **Disponibilidade** | Status | dropdown Ativo/Férias/Afastado/Inativo |
| | Horário de atendimento | texto livre |
| | Idiomas | texto CSV |
| | Prioridade | dropdown Alta/Média/Baixa |
| | **Tem agenda própria?** | Sim/Não (vincula com caixa Agenda) |
| **Direcionamento IA** | QUANDO direcionar (palavras-chave) | texto CSV |
| | NÃO direcionar quando | texto CSV |
| | IA pode encaminhar direto? | dropdown Sim/Confirmar/Não |
| | Observações | texto |

21 campos (20 originais + `tem_agenda_propria`).

---

## 12. Forwards (multi-item, Excel)

Contatos **externos** (parceiros, fornecedores, técnicos terceirizados).

| Bloco | Campo | Tipo |
|---|---|---|
| **Identificação** | Nome / Razão social | texto ✅ |
| | Tipo | dropdown Vendedor parceiro/Fornecedor/Técnico externo/Outro |
| | Empresa | texto |
| **Contato** | WhatsApp | texto ✅ |
| | Telefone | texto |
| | Email | email |
| | Site | URL |
| **Especialidade** | O que faz | texto |
| | Categoria | texto |
| | Cobertura geográfica | texto |
| **Direcionamento IA** | QUANDO direcionar | texto CSV |
| | Mensagem prévia (template) | texto |
| | IA pode encaminhar direto? | dropdown Sim/Confirmar/Não |
| | Observações | texto |

14 campos.

---

## 13. FAQ (multi-item, Excel)

| Bloco | Campo | Tipo |
|---|---|---|
| **Pergunta** | Pergunta | texto ✅ |
| | Variações da pergunta | texto CSV |
| | Categoria | texto livre |
| | Tags | texto CSV |
| **Resposta** | Resposta | texto ✅ |
| | Resposta resumida (1 linha) | texto |
| **Direcionamento IA** | Confiança | dropdown Alta/Média/Baixa |
| | Encaminhar pra alguém depois? | texto (link Team) |
| | Observações | texto |
| | Atualizado em | data |

10 campos.

---

## 14. Objections (multi-item, Excel)

| Bloco | Campo | Tipo |
|---|---|---|
| **Objeção** | Objeção do cliente | texto ✅ |
| | Variações de como aparece | texto CSV |
| | Categoria | dropdown Preço/Qualidade/Entrega/Concorrência/Confiança/Outro |
| **Resposta** | Como rebater | texto ✅ |
| | Argumento principal | texto curto |
| | Prova social / case | texto |
| **Direcionamento IA** | Quando NÃO insistir | texto |
| | Encaminhar pra humano se persistir? | Sim/Não |
| | Profissional responsável | texto (link Team) |
| | Observações | texto |

10 campos.

---

## 15. Formulários (multi-item, form especializado, sem Excel) **[NOVA]**

Cliente cria múltiplos formulários. Cada um tem perguntas configuráveis e termo opcional.

### Schema da caixa Formulários

| Bloco | Campo | Tipo |
|---|---|---|
| **Identificação** | Nome do formulário | texto ✅ |
| | Descrição (cabeçalho que cliente vê) | texto |
| | Tipo | dropdown Locação/Pedido/Cadastro/Reserva/Outro |
| | Apelidos | texto CSV |
| **Perguntas** | Lista de perguntas | array (ver abaixo) |
| **Termos** | Tem termo/contrato? | Sim/Não |
| | Texto do termo | texto longo |
| | Aceite obrigatório? | Sim/Não |
| **Multas e regras** | Tem multas/penalidades? | texto livre |
| | Política de cancelamento | texto livre |
| **Disparo** | Quando IA oferece (palavras-chave) | texto CSV |
| | IA preenche automaticamente? | Sim/Confirmar/Não |
| **Assinatura** | Exige confirmação por OTP? | Sim/Não |
| | Email obrigatório no formulário? | Sim/Não |
| | Texto do email com OTP | texto livre (template) |
| | Validade do OTP (minutos) | número (default 10) |
| | Envia PDF assinado pro cliente no fim? | Sim/Não |
| **Destino** | Pra onde envia preenchido | dropdown Email/WhatsApp interno/Pessoa específica |
| | Email/WhatsApp de destino | texto |
| | Profissional responsável | texto (link Team) |
| | Backup se responsável tá fora | texto (link Team) |
| **Direcionamento IA** | Observações pra IA | texto livre |

### Schema de cada Pergunta (sub-array)

| Campo | Tipo |
|---|---|
| Texto da pergunta | texto ✅ |
| Tipo de resposta | dropdown Texto curto/Texto longo/Número/Email/Telefone/CPF-CNPJ/Data/Hora/Sim-Não/Múltipla escolha/Lista de opções |
| Opções (se múltipla escolha ou lista) | texto CSV |
| Resposta obrigatória? | Sim/Não |
| Página do formulário | número (1, 2, 3...) |
| Observação interna | texto |

### Fluxo de assinatura (OTP via WhatsApp)

```
Cliente preenche formulário no WhatsApp via IA
         ↓
IA: "Pra confirmar, preciso do seu email."
         ↓
Cliente: pedro@email.com
         ↓
IA dispara email com OTP 6 dígitos via Resend
         ↓
IA: "Enviei um código de 6 dígitos. Cole aqui pra confirmar."
         ↓
Cliente: 384729
         ↓
IA valida OTP → marca formulário como assinado
         ↓
Sistema gera PDF com:
  - Resposta completa do formulário
  - Termo aceito
  - OTP usado
  - Timestamp + IP + email confirmado
         ↓
PDF salvo em tenant-media + enviado pro cliente (se toggle ligado) + responsável interno
```

### Tabelas de banco necessárias

```sql
form_responses (
  id uuid PK,
  tenant_id uuid,
  form_id uuid,
  contact_id uuid,
  conversation_id uuid,
  answers jsonb,
  status text (collecting / awaiting_otp / signed / expired),
  email text,
  otp_hash text,
  otp_expires_at timestamptz,
  signed_at timestamptz,
  signed_pdf_url text,
  created_at timestamptz
)
```

### Tools que IA usa

- `start_form(form_id)` — inicia coleta
- `submit_answer(question_id, value)` — registra resposta
- `request_signature(email)` — envia OTP
- `confirm_otp(code)` — valida OTP, marca como assinado, gera PDF

---

## 16. Agenda (multi-row se profissionais com agenda própria, perguntas + integração) **[NOVA]**

### Comportamento por tenant

- **Singleton por padrão**: 1 agenda do estabelecimento (ex: locação Nudeck)
- **Multi-row se cliente quiser**: 1 agenda por profissional (ex: clínica com 5 médicos)
- Quando multi-row, cada agenda usa o flag `tem_agenda_propria` em Team pra renderizar

### Schema

| Bloco | Campo | Tipo |
|---|---|---|
| **Conexão** | Conta Google conectada? | Sim/Não |
| | Email da conta conectada | texto (preenchido após OAuth) |
| | Calendário ativo | dropdown (carrega da Google API) |
| | Status da conexão | badge Ativa/Expirada/Desconectada |
| **Disponibilidade** | Profissional vinculado | texto (link Team, opcional) |
| | Puxar horário de Hours? | Sim/Não |
| | Horário próprio (se Não) | texto |
| | Duração padrão (minutos) | número |
| | Intervalo entre compromissos (minutos) | número |
| | Antecedência mínima | texto (ex: "2h", "1 dia") |
| | Antecedência máxima | texto (ex: "30 dias") |
| | Dias bloqueados | array de datas |
| **Confirmação** | Envia confirmação automática? | Sim/Não |
| | Template da confirmação | texto |
| | Lembrete antes do compromisso? | dropdown 1h antes/1 dia antes/Não |
| **Direcionamento IA** | IA pode agendar direto? | dropdown Sim/Confirmar/Não |
| | IA pode cancelar/reagendar? | dropdown Sim/Confirmar/Não |
| | Quando NÃO agendar | texto |
| | Observações pra IA | texto |

### Reuso com Services/Events

Tipos de compromisso **não duplicam**. IA usa duração que já existe em Services e Events.

Fluxo:
```
Cliente: "agendar retorno com João dia 10/05"
         ↓
1. search_services("retorno") → "Retorno consulta - 15 min"
2. search_team("João") → João da Silva, tem agenda própria
3. get_calendar_slots(joão_id, 10/05, 15min) → slots livres compatíveis
4. IA oferece: "9h, 11h30, 14h. Qual prefere?"
         ↓
Cliente escolhe
         ↓
create_appointment(joão_id, 10/05, 11:30, retorno_id, contato)
         ↓
Sistema cria evento no Google Calendar + salva em appointments
```

### Tools necessárias

- `search_team(query)` — retorna profissional + flag `tem_agenda_propria`
- `get_calendar_slots(team_member_id, date, duration_min)` — Google Calendar API
- `create_appointment(team_member_id, datetime, service_id, contact)` — cria evento
- `cancel_appointment(appointment_id)`
- `reschedule_appointment(appointment_id, new_datetime)`

---

# SEÇÃO 4: PERSONALIZE

## 17. Custom (multi-row, texto livre)

| Campo | Tipo |
|---|---|
| Título | texto ✅ |
| Conteúdo | texto/markdown ✅ |

Multi-row (cliente cria várias). Cap de 4000 tokens somados (limite atual mantido).

---

# Padrão de bloco "Direcionamento IA"

Toda caixa multi-item tem este bloco. É a diferenciação central:

- **Palavras-chave / sinônimos** (como cliente fala, não como empresa cataloga)
- **Quando NÃO usar / restrições** (limites operacionais e éticos)
- **Nível de autonomia da IA** (Sim/Confirmar/Não em cada ação)
- **Profissional responsável** (link Team)
- **Backup** se responsável tá fora
- **Observações livres**

Catálogo simples qualquer um faz. Catálogo que diz pra IA **como agir**, com restrições éticas e palavras-chave do cliente, é o produto.

---

# UX padrão: pergunta em vez de campo

Em todas as caixas (especialmente as com perguntas):

- Cada campo vira uma **pergunta humana**, não label de form
- "Tem estacionamento?" em vez de "Estacionamento (vagas, gratuito?)"
- **Dropdown/botão como default** quando resposta é finita
- Texto livre só quando não cabe estruturado
- Agrupado em **accordions** com **contador de progresso** ("3 de 8 respondidas")
- Componente reusável `<QuestionBlock>` recebe `{field, question, type, options, value, onChange}`
- Schema declarativo das caixas inclui o **texto da pergunta**, não só o nome técnico

Master prompt usa pergunta humana ("Tem estacionamento?") no contexto, não nome técnico do campo.

---

# Tipos de input usados

| Tipo | Quando usar |
|---|---|
| **Sim/Não** | Decisão binária ("Tem estacionamento?") |
| **Sim/Confirmar/Não** | Autonomia da IA (3 níveis) |
| **Dropdown** | Resposta com 3-5 opções fechadas ("Tipo de evento?") |
| **Texto curto** | Nome, código, valor único |
| **Texto livre** | Descrição, observações, contexto |
| **Texto CSV** | Listas (palavras-chave, apelidos, idiomas) |
| **Número** | Quantidade, preço, capacidade |
| **Data/Hora** | Agendamentos |
| **Email/URL/Telefone** | Validações específicas |
| **Array (sub-objetos)** | Perguntas dentro de Formulários, dias bloqueados em Agenda |

---

# Reuso e dependências entre caixas

```
Establishment ──→ contexto base do prompt
Hours ────────→ default de Agenda (se não tem horário próprio)
Pagamento ────→ usado em Products/Services/Events/Formulários
Products ─────→ Delivery Items (fallback)
Services ─────→ Agenda (duração)
Events ───────→ Agenda (duração)
Team ─────────→ Forwards/Services/Events/Formulários/Agenda (campo profissional responsável)
                + flag `tem_agenda_propria` define se Agenda renderiza dele
```

---

# Próximos passos: Sprints sequenciais

Quebrar em 3 sprints:

| Sprint | Caixas | Pré-requisito |
|---|---|---|
| **Catalog** | Establishment, Hours, Links, Pagamento, Products, Services, Delivery Items/Areas/Config, Events, Team, Forwards, FAQ, Objections, Custom (15 caixas) | Nenhum |
| **Forms** | Formulários + assinatura OTP via Resend + PDF (1 caixa) | Resend API key (já está em secrets) |
| **Schedule** | Agenda + Google Calendar OAuth + tools encadeadas (1 caixa) | OAuth Google (Pedro resolve), Sprint Catalog merged (Team com `tem_agenda_propria`) |

**Catalog é a sprint principal** — destrava 30k itens da loja, cobre 15 das 17 caixas, prepara base pra Forms e Schedule.

---

# Lista resumida das mudanças vs estrutura antiga

| Antes (12 caixas) | Depois (17 caixas) |
|---|---|
| establishment | mantida |
| hours | mantida (suporte 2 turnos) |
| links | mantida |
| products | mantida (+ campo delivery, novos atributos) |
| services | mantida (+ profissional responsável, palavras-chave) |
| **delivery** | dividida em 3: Delivery Items, Delivery Areas, Delivery Config |
| events | reescrita (51 campos em accordions) |
| team | expandida (20 campos do modelo Pedro) |
| forwards | reescrita (contatos externos) |
| faq | mantida (+ variações, confiança) |
| objections | mantida (+ variações, escalação) |
| custom | mantida |
| | **Pagamento** (NOVA) |
| | **Formulários** (NOVA) |
| | **Agenda** (NOVA) |

---

# Decisões de produto registradas

1. **Apenas Nome obrigatório** em multi-item caixas
2. **Categoria livre** (cliente preenche o que faz sentido)
3. **Re-import substitui tudo** (sem upsert)
4. **Sem mapeamento inteligente Excel** (cliente baixa modelo, preenche, sobe)
5. **Botão "mande pro time arrumar"** = lead pra serviço de implementação
6. **Variantes = linhas separadas** ("blusa preta" e "blusa laranja" são 2 linhas)
7. **CatalogItemSchema afrouxa price em todas** (Services + Products + Delivery)
8. **Hours suporta 2 turnos** (almoço fechado)
9. **Cada caixa tem seu modelo Excel próprio** (não 1 Excel grande com abas)
10. **OTP via WhatsApp**, não via página externa (cliente nunca sai da conversa)
11. **PDF do formulário enviado ao cliente** ao final (com toggle no schema)
12. **Tipos de compromisso reusam Services/Events** (não duplicam em Agenda)
13. **Todo Excel tem aba "Instruções"** com exemplos (padrão do modelo Team)
14. **Bloco "Direcionamento IA"** em todas as caixas multi-item (palavras-chave + autonomia + restrições)

---

Documento de referência. Pronto para virar input das próximas sprints.
