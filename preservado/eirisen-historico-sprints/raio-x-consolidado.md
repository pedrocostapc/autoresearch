# Raio-X Consolidado — Estado atual completo do Risen OS

> **Modo:** read-only puro. NÃO criar branch, NÃO escrever código, NÃO rodar migrations, NÃO fazer alterações.
> **Output:** relatório estruturado em `/home/claude/risen-ai/raio-x-consolidado.md` + sumário no chat.

---

## Por que esse raio-x

Pedro está prestes a tomar decisões estratégicas grandes (assinatura recorrente, evolução do prompt builder, RAG com tools, importação de 30k itens, master prompt no super admin). Antes de qualquer escopo, precisa do estado real do sistema **em todas as áreas que importam**.

Esse raio-x consolida 4 frentes:
- **A.** Billing / Stripe / cobrança recorrente
- **B.** Persona builder (caixas) e schemas internos
- **C.** Master prompt e arquitetura de prompt
- **D.** Tool calling, RAG e capacidade da IA buscar info on-demand

---

## A. Billing / Stripe / Cobrança

### A.1 Schema de banco — tabelas relacionadas a billing

Listar e descrever cada uma:
- `tenants.credits_cents` — existe? Como é atualizado?
- `tenant_ledger` — schema completo. Quem escreve? Cron diário ou tempo real?
- `tenant_credit_lots` — schema. Como FIFO é consumido?
- `credit_purchases` — schema. Liga com Stripe?
- `tenant_subscriptions` (ou similar) — existe? Schema?
- Outras tabelas relacionadas (planos, courtesy, trial, recharges, audit)?

Para cada: colunas, tipos, defaults, FKs, RLS policies.

### A.2 RPCs de cobrança

Listar todas em `supabase/migrations/`:
- `debit_credits`
- `apply_credit_grant`
- `has_sufficient_credits`
- `try_acquire_auto_recharge_slot`
- `calculate_transcription_cost` (SU7c-1)
- `check_and_reserve_system_budget`
- Outras?

Para cada: assinatura, o que faz, quem chama (qual edge ou trigger).

### A.3 Stripe — integrações existentes

Procurar em `supabase/functions/`:
- Edge `stripe-webhook` — existe? O que processa? Quais eventos?
- Edge `stripe-checkout` ou similar — cria session?
- Edge `stripe-customer-portal` — gerencia assinatura?
- Outras edges importando Stripe?

Procurar em `src/`:
- Tela de billing/subscription? Caminho?
- Botão "Upgrade" ou "Adicionar crédito"?
- Componente de checkout?

Verificar secrets: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_ID_*` configurados? (lista nomes que aparecem, não os valores)

### A.4 Plans / pricing

Procurar:
- Tabela `plans` ou `subscription_plans`?
- Constantes hardcoded em `_shared/plans.ts` ou similar?
- Os 3 planos do memory (Iniciante R$19,90 / Crescimento R$49,90 / Negócio R$99,90) existem como dados?
- Anuais (50% off) existem?
- Add-ons (extra seats, instances, storage) existem?

### A.5 Courtesy / Trial / Auto-recharge

- Courtesy: tabela ou campo? Cron mensal? Lógica de "não-acumulativa"?
- Trial: flag `trial_started_at` em tenants? Cron expira após 30d ou consume 1GB? R$3 AI credit aplicado em onboarding?
- Auto-recharge: coluna `auto_recharge_enabled`? Edge dispara quando saldo baixo? Threshold? Stripe charge automático? Consentimento explícito?

### A.6 UI de billing

Listar telas em `/src/features/`:
- `/billing` ou equivalente — existe? Mostra saldo, histórico, recharge?
- Onboarding com cadastro de cartão?
- Página de planos com upgrade?
- Página admin pra ver receita/MRR?

### A.7 Cobrança real em produção — está acontecendo?

```sql
-- Volume de débitos últimos 30 dias
SELECT COUNT(*), SUM(amount_cents)
FROM tenant_ledger
WHERE entry_type IN ('debit','ai_usage')
  AND created_at > NOW() - INTERVAL '30 days';

-- Tenants com saldo positivo
SELECT COUNT(*) FROM tenants WHERE credits_cents > 0;

-- Recharges últimos 30 dias
SELECT COUNT(*), SUM(amount_cents), array_agg(DISTINCT entry_type)
FROM credit_purchases
WHERE created_at > NOW() - INTERVAL '30 days';

-- Algum stripe_payment_intent_id populado?
SELECT COUNT(*)
FROM credit_purchases
WHERE stripe_payment_intent_id IS NOT NULL;
```

Se Stripe IDs aparecem → cobrança Stripe rodou em produção.
Se só `manual_grant` ou similar → cobrança via SQL Editor ainda.

### A.8 Matriz final de billing

Tabela:

| Componente | Status | Onde |
|---|---|---|
| FIFO de créditos | ? | tabela X, RPC Y |
| Stripe checkout | ? | edge Z ou ❌ |
| Webhook Stripe | ? | edge W ou ❌ |
| Cobrança recorrente (assinatura) | ? | ? |
| Auto-recharge | ? | ? |
| Courtesy credit | ? | ? |
| Trial | ? | ? |
| UI billing | ? | ? |

Marcar:
- ✅ funcional em produção
- 🟡 implementado mas não em uso
- 🔴 schema/edge existe mas falta integração
- ❌ inexistente

---

## B. Persona Builder — caixas

### B.1 Schema consolidado das tabelas

```bash
grep -rn "tenant_ai_configs\|persona_boxes\|persona_mode\|ai_models\|ai_logs" supabase/migrations/ --include="*.sql" -l | sort
```

Ler cada migration. Montar schema final consolidado de:
- `tenant_ai_configs` (todas colunas, tipos, defaults, RLS)
- `persona_boxes` (todas colunas, tipos, FKs, índices)
- Quaisquer tabelas relacionadas (`persona_quiz_answers`, etc)

### B.2 Anatomia de cada tipo de caixa

12 ou 13 tipos vistos na UI:
- establishment, hours, links
- services, products, delivery, events
- team, forwards, faq, objections
- custom

Para CADA tipo:
- Tipo TypeScript do `content` (interface/type/zod schema)
- JSON estruturado vs texto livre vs JSONB com formato fixo
- Campos predefinidos ("colunas") por tipo
- UI de edição (formulário próprio, modal específico, ou genérico)
- Exemplo de `content` preenchido (de tests/mocks/seeds se houver)

```bash
# Schemas/validação
grep -rn "boxSchema\|BoxType\|PersonaBoxType" src/ supabase/ --include="*.ts" --include="*.tsx" -l

# Componentes de edição
find src/features/ai-settings -name "*.tsx" | xargs grep -l "BoxEdit\|BoxModal\|BoxForm\|EditBox\|PersonaBox" | head -20

# Formatadores no compilador
grep -rn "format" supabase/functions/_shared/persona-compiler.ts
```

### B.3 Tamanho real das caixas em produção

```sql
-- Quanto cada tipo de caixa está sendo usado
SELECT box_type,
       COUNT(*) AS rows_total,
       AVG(LENGTH(content::text))::int AS content_avg_chars,
       MAX(LENGTH(content::text)) AS content_max_chars,
       SUM(LENGTH(content::text)) AS content_total_chars
FROM persona_boxes
WHERE content IS NOT NULL
GROUP BY box_type
ORDER BY content_max_chars DESC;
```

Importa pra decidir quais caixas viraram problemas reais (Pedro mencionou loja com 30k itens — verificar se algum tenant já tem caixa volumosa).

### B.4 Compilador de prompt

Caminho: `supabase/functions/_shared/persona-compiler.ts` (provável).

Reportar:
- Como cada tipo é traduzido pra markdown
- Se tem branch por `personality_style` (Pessoal/Clínica/Loja/Vendedor)
- Tamanho do prompt final em produção (sample real de algum tenant que tenha tudo preenchido — Construai do Vanderlei provavelmente)

### B.5 Modos persona_mode

```sql
SELECT persona_mode, COUNT(*)
FROM tenant_ai_configs
GROUP BY persona_mode;
```

Distribuição entre `manual` (markdown direto) e `blocks` (caixas). Importa pra saber se features novas tocam ambos ou só blocks.

### B.6 Personality style

```bash
grep -rn "personality_style\|personalityStyle\|Pessoal\|Clínica\|Restaurante\|Loja\|Vendedor" supabase/functions/_shared/ src/features/ai-settings/ --include="*.ts" --include="*.tsx"
```

- Onde armazenado (coluna em qual tabela)
- Valores possíveis (enum, free text, FK?)
- Quantos tenants em cada valor (SQL agregado)
- Como influencia o prompt (template diferente? só uma frase?)

---

## C. Master Prompt e arquitetura de prompt

### C.1 Onde vive o master prompt hoje

Pedro **não sabe**. Investigar:

```bash
# Procurar prompts hardcoded
grep -rn "buildSystemPrompt\|systemPrompt\|MASTER_PROMPT\|baseSystemPrompt" supabase/functions/ --include="*.ts"
```

```bash
# Constantes de prompt
grep -rn "const.*prompt.*=\|const.*PROMPT.*=" supabase/functions/_shared/ --include="*.ts"
```

```bash
# Tabela que armazena prompt?
grep -rn "system_prompt\|master_prompt\|prompt_template" supabase/migrations/ --include="*.sql"
```

Reportar:
- Caminho do arquivo onde master prompt vive (provavelmente hardcoded em `_shared/`)
- Está hardcoded ou vem do banco?
- Tem versionamento?
- Editável via UI super admin? (Pedro confirmou: NÃO)
- Como é injetado no `ai-reply`?

### C.2 Camadas do prompt atual

Pedro tem visão de 4 camadas (master + whatsapp_rules + template + dados). Hoje provavelmente é 1 ou 2. Reportar:
- Quantas camadas existem hoje?
- Qual é a estrutura do system prompt final montado em `ai-reply`?
- Onde entram instruções de canal (WhatsApp: 2 mensagens max, sem markdown pesado, etc)?
- Onde entra `business_context`/`rules` da `tenant_ai_configs`?

### C.3 Tamanho real do prompt em produção

Sample SQL:

```sql
-- Tamanho médio do prompt final por tenant (último log ai_logs com prompt completo)
SELECT tenant_id,
       AVG(input_tokens)::int AS avg_input_tokens,
       MAX(input_tokens) AS max_input_tokens
FROM ai_logs
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY tenant_id
ORDER BY max_input_tokens DESC
LIMIT 10;
```

Pedro quer saber: tenant com mais tokens de input está perto de quanto? 30k? 100k? 200k?

### C.4 WhatsApp rules

Onde estão as regras de canal hoje?
- "Máximo 2 mensagens por turno"
- "Sem markdown pesado"
- "Tom mobile"
- "Emojis com parcimônia"

Hardcoded em system prompt? Ou viraram parte de `tenant_ai_configs.rules`? Ou nem existem como instrução explícita?

---

## D. Tool calling e RAG

### D.1 Tools registradas hoje

```bash
grep -rn "tools:" supabase/functions/ai-reply/ --include="*.ts"
grep -rn "tool_use\|tool_result\|toolUseId" supabase/functions/ai-reply/ --include="*.ts"
```

Reportar:
- IA tem tools registradas no payload pro provider Anthropic/OpenAI?
- Quais tools existem? (lista nomes + descrição + schema)
- Em qual loop são chamadas? (vi referência a "tool-calling loop até 5 rounds" no raio-x da SU7c-1)
- Algum exemplo de log mostrando tool call sendo executado?

### D.2 Capacidade RAG existente

- Existe algum mecanismo onde IA consulta banco pra buscar info on-demand?
- Embeddings (pgvector)? Full-text search (tsvector)?
- Ou todo o contexto vai sempre no system prompt?

```bash
grep -rn "pgvector\|embedding\|vector\|tsvector\|to_tsvector" supabase/migrations/ supabase/functions/ --include="*.sql" --include="*.ts"
```

### D.3 Caixas grandes — como sobrevivem hoje

Se algum tenant já tem caixa volumosa (>5000 chars), como o `ai-reply` lida?
- Manda tudo no contexto (custo alto)?
- Trunca?
- Ignora?

```sql
-- Tenant com caixa mais volumosa, e quanto isso adiciona no prompt
WITH big_box AS (
  SELECT tenant_id, box_type, LENGTH(content::text) AS sz
  FROM persona_boxes
  ORDER BY sz DESC
  LIMIT 5
)
SELECT * FROM big_box;
```

### D.4 Capacidade de import de Excel/CSV

```bash
grep -rn "xlsx\|csv\|papaparse\|sheetjs" src/ package.json --include="*.ts" --include="*.tsx" --include="*.json"
```

- Existe import de Excel/CSV em algum lugar?
- Existe edge ou função que processa upload de planilha?
- Componentes de drag-drop file?

---

## Output esperado

```markdown
# Raio-X Consolidado — Risen OS (10/05/2026)

## Sumário executivo
(3-5 linhas dizendo "o que está bom, o que está faltando")

## A. Billing / Stripe
A.1 Schema (5 tabelas mapeadas)
A.2 RPCs (8 listadas)
A.3 Stripe (status: 🟡 schema existe, edges parciais)
A.4 Plans (status)
A.5 Courtesy/Trial/Auto-recharge (status)
A.6 UI billing (caminho)
A.7 Cobrança real em prod (X recharges/mês via Stripe vs Y manuais)
A.8 Matriz consolidada

## B. Persona Builder
B.1 Schema consolidado de tenant_ai_configs e persona_boxes
B.2 Anatomia dos 12 tipos de caixa
B.3 Tamanhos reais
B.4 Compilador
B.5 Distribuição persona_mode
B.6 Personality_style

## C. Master Prompt
C.1 Onde vive (caminho)
C.2 Camadas atuais
C.3 Tamanho real de prompt em prod
C.4 WhatsApp rules (status)

## D. Tool calling / RAG
D.1 Tools registradas (lista)
D.2 Capacidade RAG (status)
D.3 Caixas grandes (como sobrevivem)
D.4 Import Excel/CSV (status)

## Gaps consolidados
| Frente | Gap | Tamanho estimado |
|---|---|---|
| Billing | Falta X | M |
| Persona | Schemas não declarativos | S |
| Master prompt | Hardcoded, não editável | M |
| Tool calling | Inexistente | L |
| RAG | Inexistente | L |
| Excel import | Inexistente | M |

## Recomendação de ordem
(Sugestão de em qual ordem atacar pra desbloquear o que Pedro disse: 30k itens precisando entrar, master prompt no super admin, IA buscar on-demand)
```

---

## Restrições absolutas

- ❌ Nenhuma branch criada
- ❌ Nenhum arquivo modificado
- ❌ Nenhuma migration aplicada
- ❌ Nenhum commit
- ✅ Pode ler qualquer arquivo
- ✅ Pode rodar grep/find/SQL queries
- ✅ Copiar trechos curtos de schema/código pra ilustrar é encorajado
- ✅ Output salvo em arquivo + sumário no chat

Após esse raio-x, Pedro decide as 3-4 sprints prioritárias com base em estado real, não em achismos.
