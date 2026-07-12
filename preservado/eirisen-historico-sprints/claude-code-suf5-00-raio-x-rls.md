# SUF5 — Raio-X (RLS em whatsapp_providers)

## Objetivo

**Não escrever código.** Mapear o estado atual de RLS em `whatsapp_providers` antes de habilitar policy. Saída: relatório markdown com 4 seções respondidas raw.

## Contexto

`whatsapp_providers` foi recriada em SA2 sem `ENABLE ROW LEVEL SECURITY`. Hoje qualquer user autenticado lê dados de instâncias de outros tenants — incluindo `config` (que vai ganhar apikey por instância no SU8). Antes do SU8, precisa RLS.

Risco principal: habilitar RLS errado quebra tudo que lê `whatsapp_providers` (inbox, settings, qr-init-session, etc).

## Seções

### 1. Estado atual da tabela

Roda no SQL Editor:

```sql
-- 1.1 RLS está habilitada?
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname='public' AND tablename='whatsapp_providers';

-- 1.2 Tem alguma policy?
SELECT polname, polcmd, polroles::regrole[], pg_get_expr(polqual, polrelid) AS using_expr
FROM pg_policy
WHERE polrelid = 'public.whatsapp_providers'::regclass;

-- 1.3 Estrutura da tabela
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema='public' AND table_name='whatsapp_providers'
ORDER BY ordinal_position;

-- 1.4 Confirma campos sensíveis no config
SELECT id, name, type, jsonb_object_keys(config) AS config_keys
FROM whatsapp_providers
LIMIT 5;
```

Cola os 4 resultados.

### 2. Quem lê whatsapp_providers hoje

Greps em todo o repo:

```
from("whatsapp_providers")
.from('whatsapp_providers')
"whatsapp_providers"
```

Lista cada arquivo + linha + contexto de 2 linhas. Quero saber quantos call sites podem quebrar com RLS errada.

Especialmente importante: separar entre:
- Edges (rodam com `service_role`, RLS bypassa) — não precisa adaptar
- Frontend / hooks React (rodam com JWT do user) — precisa adaptar
- RPCs (precisa ver se são `SECURITY DEFINER` ou `INVOKER`)

### 3. RLS de tabelas similares como referência

Mostre as RLS policies completas de 2 tabelas que JÁ têm RLS funcionando bem com mesmo padrão multi-tenant:

- `conversations`
- `subscriptions` (se existir, senão pega outra com RLS por tenant)

Quero ver:
- Como filtra por tenant (usa `can_access_record`? `users.tenant_id`? outro?)
- SELECT vs INSERT/UPDATE/DELETE separados ou mesma policy
- Se super_admin tem bypass

### 4. Função `can_access_record`

Mostre a definição completa da função `public.can_access_record` (citada no raio-x SU7a). Quero ver os params e a lógica.

Se houver outras funções helper de auth (`is_super_admin`, `is_tenant_member`, etc), mostra elas também.

## Formato

Markdown único, 4 seções. SQL com resultados crus. Greps com paths e linhas. Sem propor código novo.
