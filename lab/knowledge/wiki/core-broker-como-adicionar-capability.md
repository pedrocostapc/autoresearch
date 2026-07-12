# Core broker (v1-call) — como adicionar uma capability nova

Escrito pela sessão do Core (risencore) pra quem for plugar um serviço novo no broker
(ex.: a frota de OCR do SuperSec). Repo: `~/Dev/risen/risencore`, ref Supabase `hjclvuzugdbpvnomvtpn`.

## Como o v1-call roteia (fluxo real)
`POST /functions/v1/v1-call` com header API-key do app + `x-risen-product` + `x-risen-tenant-id`,
body `{ target, capability, args, credential? }`:
1. Acha o provedor em `systems` por `slug = target`.
2. Exige **vínculo ativo** em `core_tenant_links` entre (system do app, tenant do app) e o provedor
   → **traduz o tenant** (origem→destino).
3. Acha a capability em `core_capabilities` por `(system_id, name)`.
4. Monta payload `{ capability, tenant, args, credential }`, assina com **HMAC-SHA256 do corpo cru**
   usando `core_capabilities.secret` → header `x-risen-signature`, e faz `POST` no `target_url`.
5. Loga em `core_call_log` (só metadados — **nunca** args/credential).

## Pra registrar uma capability nova (2 passos)
### 1) O provedor = uma edge function que valida o HMAC
Ela verifica a assinatura contra o env `BROKER_HMAC_SECRET` (que TEM que ser igual ao
`core_capabilities.secret` da capability). Esqueleto (copie de `v1-provider-cora`/`v1-provider-govnfse`):
```ts
const raw = await req.text();
const brokerSecret = Deno.env.get('BROKER_HMAC_SECRET');
if (brokerSecret) {
  const sig = req.headers.get('x-risen-signature');
  const exp = hmacHexSHA256(brokerSecret, raw);      // ver helper nos providers
  if (sig !== exp) return 401;
}
const { capability, tenant, args, credential } = JSON.parse(raw);
// ... faz o trabalho, devolve { units, ...dados }  (units = medição no core_call_log)
```
Deploy: `supabase functions deploy v1-ocr-dispatch --no-verify-jwt --project-ref hjclvuzugdbpvnomvtpn`.

### 2) Registrar no banco do Core (systems + core_capabilities)
`core_capabilities` colunas: `system_id, name, description(NOT NULL), args_schema(default {}), target_url, secret, active`.
```sql
-- provedor (uma vez)
insert into systems (slug, name, active) values ('fleet','Frota OCR', true)
  on conflict (slug) do nothing;
-- capabilities (target_url = URL da edge; secret = o BROKER_HMAC_SECRET dela)
insert into core_capabilities (system_id, name, description, target_url, secret, active)
select id, 'ocr_dispatch', 'enfileira OCR', 'https://hjclvuzugdbpvnomvtpn.supabase.co/functions/v1/v1-ocr-dispatch', '<MESMO_BROKER_HMAC_SECRET>', true
  from systems where slug='fleet';
-- idem 'ocr_result'
```
E cada app precisa de um `core_tenant_links` ativo (app ↔ fleet) pra o v1-call liberar.

## Alternativa mais simples (endpoint direto, sem tenant-link)
Pra infra compartilhada (OCR não precisa de tradução de tenant), dá pra ser um endpoint direto
do Core (como `v1-notify`/`v1-fiscal-templates`), roteado pelo `risen-core-proxy` de cada app
(service `core.ocr.dispatch` → `v1-ocr-dispatch`). Menos burocracia (sem systems/links/HMAC),
autentica pela API-key do app. **Recomendo esse caminho pra OCR** — é o que usei no v1-notify.

## Migration em prod do Core = GATED
`fleet_jobs` + `claim_fleet_job` são migration no Supabase do Core → **a sessão do Core aplica**
(mostro→valido→aplico). Manda o SQL que eu aplico, OU eu construo o lado do Core inteiro
(fila + edges + registro) e você faz o worker/máquinas. Secrets do Core: Bitwarden ao vivo.
