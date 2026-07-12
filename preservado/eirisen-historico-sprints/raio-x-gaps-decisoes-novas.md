# Raio-X Complementar — 8 Gaps das Decisões Novas (10/05/2026)

> **Modo:** read-only puro. NÃO criar branch, NÃO escrever código, NÃO rodar migrations.
> **Output:** relatório em `/home/claude/risen-ai/raio-x-gaps-decisoes-novas.md` + sumário no chat.
> **Tempo estimado:** 30-45 minutos.

---

## Contexto

Já temos raio-x consolidado de billing, persona builder, master prompt e tools (rodado em 10/05/26). Decidimos refatorar de 12 para **17 caixas** (`00-CAIXAS-ESTRUTURA-FINAL.md`). 

Algumas decisões novas levantaram gaps técnicos específicos que o raio-x anterior **não cobriu**. Esse raio-x complementar mapeia só esses gaps.

**Não repete** investigação anterior. Foca apenas nos 8 itens abaixo.

---

## Gaps a investigar

### 1. Referência cruzada entre caixas (FK lógica)

Decisões novas:
- Caixa **Pagamento** centraliza chave PIX/banco. Products, Services, Events vão referenciá-la
- Caixa **Team** vira fonte de profissionais. Services/Events/Forms/Agenda referenciam por nome
- Caixa **Agenda** vincula com profissional do Team via flag

```bash
# Existe padrão de FK lógica entre caixas hoje?
grep -rn "tenant_id\|persona_box_id\|reference\|FK" supabase/migrations/ --include="*.sql" | grep -i "persona_boxes\|cross-box"
```

Reportar:
- Existe alguma caixa hoje que referencia outra?
- Como `services.responsible` ou `forwards.contact` lida com referência hoje (texto livre? UUID?)
- Existe view ou função que faz lookup cruzado entre caixas?
- Recomendação técnica: como modelar Pagamento centralizada sem quebrar tenants existentes

### 2. Lógica condicional em tools (fallback)

Decisão nova: Delivery Items com fallback pra Products.

```bash
grep -rn "query_products\|searchProducts\|tool.*products" supabase/functions/ai-reply/ --include="*.ts" -A 20
```

Reportar:
- Como `query_products` tool é implementada hoje
- Tem alguma tool com lógica condicional ("se A vazio, usa B")?
- O wrapper de tool é genérico ou cada tool tem implementação dedicada?
- Como adicionar fallback `delivery_items → products filtered` impacta o pipeline atual

### 3. UI condicional baseada em valor de outra caixa

Decisão nova: Team com flag `tem_agenda_propria` controla quantas agendas Agenda renderiza.

```bash
grep -rn "useTeamMembers\|team_members\|tem_agenda\|conditional render" src/features/ai-settings/ --include="*.tsx" --include="*.ts"
```

Reportar:
- Existe padrão hoje de uma caixa renderizar baseado em valor de outra?
- Como hooks consomem dados cross-caixa hoje (se consomem)?
- Componentes que renderizam condicionalmente baseado em config de outra entidade

### 4. Resend — estado da integração

Decisão nova: Formulários com OTP via Resend.

Pedro confirmou: Resend API key tá nos secrets das edges.

```bash
# Está sendo usada em alguma edge?
grep -rn "RESEND_API_KEY\|resend.com\|@resend" supabase/functions/ --include="*.ts"
```

```bash
# Helper de email existe?
find supabase/functions/_shared -name "*email*" -o -name "*mail*"
```

```bash
# Template engine de email
grep -rn "handlebars\|eta\|liquid\|template" package.json supabase/functions/_shared/ --include="*.json" --include="*.ts"
```

Reportar:
- `RESEND_API_KEY` está em secrets confirmadamente? (procura `Deno.env.get("RESEND_API_KEY")`)
- Tem helper `_shared/email.ts` ou equivalente?
- Tem template engine pra montar HTML de email?
- Algum exemplo de email transacional rodando hoje (signup confirmation, password reset, etc)?
- Se nada existe, qual seria o setup mínimo (helper + template inline)?

### 5. Geração de PDF — capacidade existente

Decisão nova: Formulários geram PDF assinado ao final.

```bash
# Biblioteca PDF instalada?
grep -rn "pdf-lib\|jspdf\|puppeteer\|pdfmake\|@react-pdf" package.json package-lock.json --include="*.json"
```

```bash
# Edge gerando PDF hoje?
grep -rn "createPdf\|generatePdf\|pdf.*generate\|application/pdf" supabase/functions/ --include="*.ts"
```

Reportar:
- Alguma lib de PDF instalada (front ou edge)?
- Algum recibo/relatório gera PDF hoje?
- Recomendação técnica: lib mais leve pra edge Deno (limites de bundle size)
- Estimativa de complexidade pra adicionar geração de PDF ao Forms (referencial)

### 6. OAuth Google e tokens

Decisão nova: Agenda integra com Google Calendar via OAuth.

```bash
# OAuth providers além de email/senha?
grep -rn "supabase.auth.*google\|signInWithOAuth\|google.*oauth" src/ supabase/ --include="*.ts" --include="*.tsx"
```

```bash
# Tabela de tokens OAuth?
grep -rn "oauth_tokens\|google_tokens\|integrations\|access_token.*refresh" supabase/migrations/ --include="*.sql"
```

```bash
# Edges que falam com Google APIs?
grep -rn "googleapis\|google.com/oauth\|google calendar" supabase/functions/ --include="*.ts"
```

Reportar:
- Sign in with Google está habilitado em Supabase Auth?
- Existe alguma integração com Google APIs hoje (Drive, Calendar, Sheets)?
- Tabela pra armazenar refresh_token de OAuth de terceiros existe?
- Quais scopes do Google estão configurados?
- Estimativa: do zero ou tem 50% pronto?

### 7. Tools encadeadas — performance e limites

Decisão nova: Agenda exige IA chamar 4 tools em sequência (`search_services → search_team → get_calendar_slots → create_appointment`).

```bash
# Loop de tool calling
grep -rn "max_iterations\|tool.*loop\|iterations\|rounds" supabase/functions/ai-reply/ --include="*.ts"
```

```sql
-- Quantas tools são chamadas em média por mensagem?
-- (precisa identificar se ai_logs registra tool_uses)
SELECT operation, AVG(input_tokens)::int avg_in, COUNT(*)
FROM ai_logs
WHERE operation = 'chat'
  AND created_at > NOW() - INTERVAL '7 days'
GROUP BY operation;
```

Reportar:
- Limite de iterações do tool loop hoje (raio-x anterior mencionou 5 rounds — confirmar)
- Como o pipeline trata tools que demoram (timeout? circuit breaker?)
- Latência média do `ai-reply` hoje (sample real)
- Se 4 tools encadeadas vão estourar 5 rounds, qual o impacto

### 8. Master prompt declarando caixas dinamicamente

Decisão nova: Master prompt precisa saber quais caixas o tenant tem preenchidas pra orientar uso de tools.

Cenário: Tenant A só tem Products. Tenant B tem Products + Services + Agenda. Master prompt precisa diferenciar.

```bash
# Como tenant_ai_configs influencia o prompt hoje?
grep -rn "buildSystemPrompt\|systemPrompt.*tenant\|tenant.*config.*prompt" supabase/functions/_shared/ --include="*.ts" -A 30
```

Reportar:
- Master prompt hoje é estático ou já varia por tenant?
- Existe injeção dinâmica de "caixas disponíveis" no prompt?
- Como mencionar dinamicamente "Tenant tem caixas Products, Services, Agenda. Use as tools query_products, query_services, get_slots"?
- Recomendação: como fazer master prompt 100% genérico + camada `available_resources` por tenant

---

## Output esperado

```markdown
# Raio-X Gaps das Decisões Novas (10/05/2026)

## Sumário (1 frase por gap)
1. Referência cruzada entre caixas: status
2. Lógica condicional em tools: status
3. UI condicional: status
4. Resend: status
5. PDF: status
6. OAuth Google: status
7. Tools encadeadas: status
8. Master prompt dinâmico: status

## Detalhe por gap

### Gap 1: Referência cruzada entre caixas
- O que existe hoje
- Recomendação técnica
- Esforço estimado

### Gap 2: Lógica condicional em tools
(idem)

### ... (até gap 8)

## Matriz consolidada

| Gap | Status | Esforço | Bloqueia sprint? |
|---|---|---|---|
| 1. FK lógica caixas | ❓ | M | Catalog |
| 2. Tools com fallback | ❓ | S | Catalog |
| 3. UI condicional | ❓ | S | Catalog |
| 4. Resend integração | ❓ | M | Forms |
| 5. PDF geração | ❓ | M | Forms |
| 6. OAuth Google | ❓ | L | Schedule |
| 7. Tools encadeadas | ❓ | M | Schedule |
| 8. Master prompt dinâmico | ❓ | M | Catalog (inicio) |

## Recomendações finais

- O que fazer **antes** da Sprint Catalog (gaps 1, 2, 3, 8)
- O que pode esperar Forms (gaps 4, 5)
- O que pode esperar Schedule (gaps 6, 7)
- Riscos de fazer tudo junto
```

---

## Restrições

- ❌ Nenhuma branch
- ❌ Nenhuma migration
- ❌ Nenhum arquivo modificado
- ✅ Pode ler tudo
- ✅ Pode rodar SQL no projeto
- ✅ Copiar trechos de código pra ilustrar

Pedro vai ler o relatório e decidir:
1. Quais gaps resolver **antes** de começar Sprint Catalog
2. Quais ficam pra resolver durante Forms/Schedule
3. Se a sequência das 3 sprints precisa ser revista
