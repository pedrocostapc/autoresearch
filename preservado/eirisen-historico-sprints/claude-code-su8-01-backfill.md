# SU8.0 — Backfill apikey por instância

## Objetivo

Popular `whatsapp_providers.config.apikey` em todas as instâncias existentes (18 providers), buscando via `GET /instance/fetchInstances` na Evolution.

Sem isso, SU8.1+ (migração das edges pra wa.crm) não funciona — cada call site precisa da apikey por instância.

## Pré-requisitos confirmados

- ✅ RLS já habilitada em `whatsapp_providers` (descoberto no SUF5 raio-x)
- ✅ Secret `EVOLUTION_API_KEY` adicionado no Supabase (chave master da Evolution)
- ✅ Endpoint Evolution v2 confirmado: `GET https://wa.crm.risenmidia.com.br/instance/fetchInstances` com header `apikey: <EVOLUTION_API_KEY>`
- ✅ Resposta retorna array com `instance.instanceName` e `instance.apikey`

## Tarefas

### 1. Edge function nova: `backfill-evolution-apikeys`

Path: `supabase/functions/backfill-evolution-apikeys/index.ts`

Comportamento:
- Edge one-shot, invocada manualmente pelo super_admin
- Auth: valida JWT + checa `is_super_admin(auth.uid())`. Bloqueia outros usuários com 403.
- Chama `GET https://wa.crm.risenmidia.com.br/instance/fetchInstances` com `apikey: Deno.env.get("EVOLUTION_API_KEY")`
- Pra cada item da resposta:
  - Extrai `instance.instanceName` e `instance.apikey` (ou `instance.token` — confirmar shape no primeiro run)
  - Faz UPDATE em `whatsapp_providers` matching por `config->>'instance_name' = <instanceName>`:
    ```ts
    config = jsonb_set(config, '{apikey}', to_jsonb(<key>::text))
    ```
- Retorna JSON: `{ total_evolution: N, total_db: M, matched: K, updated: K, missing_in_db: [...], missing_in_evolution: [...] }`
- Logs por instância (matched, updated, skipped) via `console.log` + `logSystem` opcionalmente

### 2. Validação shape

Antes de fazer UPDATE em massa, na PRIMEIRA execução:
- Loga o JSON cru da resposta do Evolution (1 instância, ofuscar key) pra confirmar shape exato
- Se shape diferente do esperado (ex: `instance.token` em vez de `instance.apikey`), aborta com erro claro

### 3. Idempotência

- Edge pode ser invocada múltiplas vezes sem duplicar nada
- UPDATE só roda se o `config.apikey` atual for diferente do que vem da Evolution (ou se ausente)
- Log conta `unchanged` separadamente de `updated`

### 4. Smoke test

Depois de deployar:
1. Invocar a edge manualmente (curl ou Dashboard → Edge Functions → Invoke)
2. Esperar resposta com contadores
3. Conferir no SQL:
   ```sql
   SELECT
     COUNT(*) FILTER (WHERE config ? 'apikey') AS com_apikey,
     COUNT(*) FILTER (WHERE NOT (config ? 'apikey')) AS sem_apikey,
     COUNT(*) AS total
   FROM whatsapp_providers
   WHERE type = 'qr';
   ```
   Esperado: `com_apikey = total = 18`, `sem_apikey = 0` (assumindo que todas as 18 instâncias do banco existem na Evolution)

### 5. Não fazer nesta sprint

- ❌ Migrar edges (provider-send-message, send-broadcast-now, etc) — fica pra SU8.1+
- ❌ Mudar `evolution-proxy` pra capturar apikey em criações futuras — fica pra SU8.3
- ❌ Tabela separada `whatsapp_provider_secrets` — RLS já protege `whatsapp_providers`, não precisa
- ❌ Cleanup do `CRM_API_KEY` env — fica pra SU8.5

## Validação antes de aplicar

Mostre o diff completo da nova edge antes de criar. Não deploy sem aprovação.

Quando deploy, mostre output do invoke (com base64 ofuscado se houver).
