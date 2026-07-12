# Prompt — Nova Conversa: Bug IA respondendo em grupos WhatsApp

> Cole este prompt no início de uma nova conversa Claude.

---

## CONTEXTO RÁPIDO

Sou Pedro, founder do Risen OS — SaaS multi-tenant de CRM WhatsApp com IA. Tenants conectam WhatsApp via Evolution API; IA atende clientes finais nesse número.

**Stack:** React + TypeScript + Tailwind + Supabase + Stripe + shadcn. Dev via Lovable + Claude Code (terminal local).

**Projeto Supabase:** `qbclqjkvovfriuhshkpw`
**Repo:** `pedrocostapc/risen-ai-connect`

---

## O BUG

**A IA passou a responder dentro de grupos do WhatsApp hoje. Preciso parar isso imediatamente.**

Comportamento esperado: IA atende **apenas conversas 1:1** com clientes. Grupos devem ficar visíveis no inbox (com label "GRUPO") mas IA não responde.

Comportamento atual: IA está respondendo em grupos.

---

## INVESTIGAÇÃO QUE JÁ EXISTE — SUF1 (sprint passada)

Há ~2 semanas mergeei **SUF1** que cuidava exatamente disso:

- Migration adicionou `contacts.is_group` e `contacts.whatsapp_jid`
- Adicionou unique index `(tenant_id, whatsapp_jid)`
- **Webhook filter desligando IA pra grupos**
- Grupos aparecem no inbox com label "GRUPO"
- Validado em produção 28/04/26 ("Hospital Teste" — confirmou comportamento)

Então o filtro existia e funcionava. **Algo quebrou recentemente.**

---

## PRs RECENTES QUE PODEM TER QUEBRADO O FILTRO

Hoje (11/05/26) deployei vários PRs. Em ordem cronológica:

| PR | O que muda | Toca em webhook? |
|---|---|---|
| #229 | URLs legíveis pra relatórios | Não |
| #232 | Botão "Assinar agora" PlanHero | Não |
| #233 | Sidebar CRÉDITOS | Não |
| #234 | Caminho C — single source of truth subscriptions | Não |
| **#235** | **Fix query_products + master prompt updates** | **Toca em ai-reply + persona-tools** |
| #236 | Refator Faturamento planos abertos | Não |
| #237 | Trigger DB negocio_mensal default | Não (mas mexeu em DB) |
| #238 | Botão Resetar persona Aba Avançado | Não |
| **#239** | **Hotfix gate provider-webhook** | **SIM — alterou provider-webhook** |

**Suspeito principal: PR #239** — alterou exatamente o `provider-webhook/index.ts` que decide se ai-reply é invocado ou não.

O fix do PR #239 foi:
```typescript
// Antes
if (!cfg.system_prompt || cfg.system_prompt.trim().length < 10) return;

// Depois
const isBlocksMode = cfg.persona_mode === "blocks";
if (!isBlocksMode && (!cfg.system_prompt || cfg.system_prompt.trim().length < 10)) return;
```

Possibilidade: o filtro de grupo do SUF1 ficou ANTES desse gate, e ao mudar a lógica do gate, algum branch que filtrava grupo foi pulado.

Outra possibilidade: PR #235 mexeu em algo do master prompt que removeu a instrução de não responder grupos.

---

## INFORMAÇÕES ÚTEIS DO SISTEMA

### Schema relevante

**Tabela `contacts`:**
- `is_group` (boolean) — true se é grupo
- `whatsapp_jid` (text) — JID do WhatsApp (`grupos terminam em "@g.us"`, individuais em `"@s.whatsapp.net"`)

**Tabela `conversations`:**
- linkada com `contact_id`

**Tabela `messages`:**
- `conversation_id`
- `sender` (contact/agent)
- `manual_send` (boolean)

### Edges relevantes

- `provider-webhook` — recebe mensagens do Evolution, decide se chama ai-reply
- `ai-reply` — gera resposta da IA
- `_shared/persona-tools.ts` — define tools (query_products, query_team, etc)
- `_shared/persona-compiler.ts` — compila system_prompt a partir das caixas

### Fluxo esperado

```
1. Cliente manda msg → Evolution API recebe
2. Evolution chama webhook do Supabase (provider-webhook)
3. provider-webhook:
   - Salva mensagem em messages
   - Verifica is_group da conversation
   - Se grupo → registra mas NÃO chama ai-reply
   - Se 1:1 → chama ai-reply
4. ai-reply gera resposta e envia via Evolution
```

---

## O QUE PRECISA SER FEITO

### Etapa 1 — Diagnóstico (Code investiga)

1. Lê `provider-webhook/index.ts` atual (pós PR #239)
2. Procura por filtro `is_group` ou similar
3. Confirma se filtro existe e em qual ponto
4. Compara com versão pré PR #239 (git log/blame)
5. Verifica `ai-reply` — tem algum filtro próprio de grupo?
6. Reporta achados

### Etapa 2 — Fix

Recoloca o filtro de grupo no lugar certo (provider-webhook OU ai-reply, conforme diagnóstico).

### Etapa 3 — Validação

- Build/tsc verde
- Deploy edge
- Smoke teste: cliente manda msg em grupo → IA não responde
- Smoke teste: cliente manda msg 1:1 → IA responde

---

## SQL PRA RODAR DE CARA (paralelo à investigação Code)

```sql
-- 1. Mensagens em grupos com resposta IA nas últimas 2h
SELECT 
  t.name AS tenant,
  c.id AS conv_id,
  contact.is_group,
  m.sender,
  m.manual_send,
  LEFT(m.text, 100) AS text_preview,
  m.created_at
FROM messages m
JOIN conversations c ON c.id = m.conversation_id
JOIN contacts contact ON contact.id = c.contact_id
JOIN tenants t ON t.id = m.tenant_id
WHERE contact.is_group = true
  AND m.sender = 'agent'
  AND (m.manual_send IS NULL OR m.manual_send = false)
  AND m.created_at > NOW() - INTERVAL '2 hours'
ORDER BY m.created_at DESC
LIMIT 20;
```

```sql
-- 2. Quantos tenants estão afetados?
SELECT 
  t.name AS tenant,
  COUNT(DISTINCT c.id) AS grupos_com_ia
FROM messages m
JOIN conversations c ON c.id = m.conversation_id
JOIN contacts contact ON contact.id = c.contact_id
JOIN tenants t ON t.id = m.tenant_id
WHERE contact.is_group = true
  AND m.sender = 'agent'
  AND (m.manual_send IS NULL OR m.manual_send = false)
  AND m.created_at > NOW() - INTERVAL '24 hours'
GROUP BY t.name
ORDER BY grupos_com_ia DESC;
```

---

## PROMPT PRO CLAUDE CODE

Quando o novo Claude (no chat) processar este contexto, ele vai gerar um prompt pro Claude Code. Sugestão de prompt inicial:

```
Bug urgente — IA passou a responder em grupos WhatsApp depois do PR #239.

SUF1 (mergeada ~28/04/26) implementou filtro pra IA não responder grupos:
- contacts.is_group e contacts.whatsapp_jid
- Filtro em provider-webhook

Hoje, PR #239 alterou provider-webhook pra corrigir outro bug (gate de 
system_prompt em persona_mode=blocks). Possivelmente quebrou o filtro de grupos.

Investiga ANTES de propor fix:

1. provider-webhook/index.ts ATUAL:
   - Há filtro is_group?
   - Em qual ponto da função?
   - Filtro está antes ou depois do return early do gate?

2. git log + git blame provider-webhook/index.ts:
   - Quando o filtro is_group foi adicionado (SUF1)?
   - Está preservado no PR #239?

3. Cruza com SQL: tenants afetados nas últimas 24h

4. ai-reply tem filtro próprio de grupo? Backup defensivo?

Reporta achados antes de propor fix.

Branch: hotfix/ia-no-grupos
```

---

## SUA TAREFA AGORA (Claude da nova conversa)

1. Leia este prompt inteiro
2. Faça perguntas se algo não estiver claro
3. Receba os outputs SQL do Pedro
4. Oriente Pedro a colar o prompt pro Code (Etapa 1)
5. Valide achados, oriente fix
6. Acompanhe até deploy + smoke teste

**Estilo de comunicação:** Pedro prefere respostas curtas, objetivas. Sem ficar repetindo coisas que ele já sabe.

---

## ANEXOS RECOMENDADOS

Quando começar a nova conversa, anexe também:

- `00-ESTADO-SESSAO-11-05.md` (estado consolidado do projeto)
- `00-CAIXAS-REFERENCIA.md` (referência das caixas)

Pra ter contexto completo do sistema.

---

**Fim do prompt.**
