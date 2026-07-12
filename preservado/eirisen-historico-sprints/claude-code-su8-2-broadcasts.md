# SU8.2 — Migrar broadcasts pra wa.crm

## Objetivo

Migrar 2 edges que disparam mensagens de broadcast pra usar `_shared/evolution-client.ts` (criado no SU8.1) em vez do proxy `api.crm`:

1. `send-broadcast-now` — botão "enviar agora" no front
2. `dispatch-scheduled-broadcasts` — cron de broadcasts agendados

## Pré-requisitos

- ✅ SU8.0 — apikey populada em `whatsapp_providers.config.apikey`
- ✅ SU8.1 — helper `_shared/evolution-client.ts` com `sendTextViaEvolution` exportado

## Fase 1 — Raio-x antes do código

**Sem escrever código novo.** Mostre raw:

### 1.1 send-broadcast-now

Mostre o arquivo completo. Quero ver:
- Como recebe input (lista de destinatários, texto, instância)
- Loop de envio (sequencial? paralelo? rate limit?)
- INSERT em `messages` por destinatário (estrutura, status inicial)
- Chamada Evolution atual (linhas que tocam `api.crm`)
- Tratamento de erro por destinatário (1 falha = aborta tudo? ou continua?)

### 1.2 dispatch-scheduled-broadcasts

Mostre o arquivo completo. Quero ver:
- Trigger (pg_cron? Supabase scheduled job?)
- Como busca broadcasts agendados pendentes (`scheduled_at <= now()` ou similar)
- Resolve `whatsapp_providers` por broadcast (campo `provider_id`?)
- Reuso de lógica de `send-broadcast-now`? Ou duplica?

### 1.3 Helper SU8.1 status

```
cat supabase/functions/_shared/evolution-client.ts
```

Confirma que `sendTextViaEvolution` e `evolutionConfigFromProvider` estão exportados e funcionais. Se precisar adicionar coisa pro broadcast (ex: helper de rate limit), avisa antes.

### 1.4 Schema da tabela broadcasts

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema='public' AND table_name='broadcasts'
ORDER BY ordinal_position;
```

Quero ver estrutura.

```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema='public' AND table_name='broadcast_recipients'
ORDER BY ordinal_position;
```

(Se essa tabela existir.)

## Fase 2 — Plano de implementação (após raio-x)

Espera meu OK depois do raio-x. Plano provável:

### 2.1 Refactor send-broadcast-now
- Substituir bloco da chamada Evolution pelo helper `sendTextViaEvolution`
- Remover `CRM_API_BASE`, `CRM_API_KEY`, `x-api-key`
- Resolver apikey de `provider.config.apikey`
- Manter loop, rate limit, INSERT em messages, lógica de erro por destinatário (sem mexer em comportamento, só na chamada)

### 2.2 Refactor dispatch-scheduled-broadcasts
- Mesma mudança da 2.1

### 2.3 Decisão pendente (avalia no raio-x)
- Se as 2 edges duplicam a lógica de envio, vale a pena criar 2º helper `_shared/broadcast-client.ts` com o loop + rate limit + retry, ou fica overkill?
- Recomendação default: **NÃO** criar helper de broadcast nesta sprint. Manter loops em cada edge, só migrar a chamada. Ataque incremental.

## Fase 3 — Smoke test

### 3.1 send-broadcast-now
1. Criar broadcast manual com 3 destinatários (de instâncias diferentes se possível)
2. Disparar pelo front
3. Conferir no banco:
   ```sql
   SELECT m.id, m.status, m.provider_message_id, m.text, m.created_at, c.name AS contact_name
   FROM messages m
   JOIN contacts c ON c.id = m.contact_id
   WHERE m.created_at > now() - interval '5 minutes'
     AND m.sender = 'agent'
   ORDER BY m.created_at DESC LIMIT 10;
   ```
4. Esperado: todas as 3 messages com `status='sent'`, `provider_message_id` populado
5. Conferir nos celulares destino

### 3.2 dispatch-scheduled-broadcasts
1. Criar broadcast agendado pra "agora + 2min"
2. Esperar o cron rodar
3. Mesma validação SQL
4. Conferir nos celulares

## Branch e PR

Branch: `feat/su8.2-broadcasts-wa-crm`. PR depois do smoke. Não merge sem aprovação.

## Não fazer nesta sprint

- ❌ Refactor de loop/rate limit/retry — manter como está
- ❌ Helper `broadcast-client.ts` — adiar
- ❌ Migrar `evolution-proxy` (SU8.3)
- ❌ Migrar `deleteMessageViaEvolution` (SU8.4)
- ❌ Cleanup `CRM_API_KEY` (SU8.5)
- ❌ Mexer em mídia (SU7b)

## Output esperado

Comece com raio-x da fase 1. Espera meu OK antes da fase 2.
