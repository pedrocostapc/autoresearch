# Prompt pro Core — Concierge Bridge (webhook + fila de aprovações)

> Cole o bloco abaixo numa aba do Core (risencore). Ele constrói o "ouvido 24/7"
> que faltava: o app manda o clique de aprovação pro Core, o Core guarda numa fila
> durável, e um executor local (na máquina 24/7, senha no Bitwarden) envia.
> Origem: sessão financaspedro (concierge do Pedro).

---

## PROMPT (colar no Core)

CORE — nova capability de plataforma: **Concierge Bridge** (fila de ações que o Pedro autoriza num app e um executor local roda). Primeiro consumidor: financaspedro (respostas de e-mail que o Pedro clica pra enviar). É genérico de propósito — qualquer app da frota vai poder enfileirar "o Pedro clicou/aprovou X → executa" (pagar boleto, responder, etc.), então entra como capability do Core, não gambiarra de um app.

Regra de ouro do Core mantida: **Core stateless pra dado sensível**. A fila guarda só o REGISTRO da aprovação (`app`, `kind`, `ref`, `choice`, `meta` não-sensível) — NUNCA credencial/senha/token de terceiro. Quem executa (envia o e-mail, paga) é o braço local, com segredo vindo do Bitwarden ao vivo.

### 1) Migration (prod-gated: mostra → valida → aplica)
Tabela `concierge_actions`:
- `id uuid primary key default gen_random_uuid()`
- `app text not null`                 -- ex: 'financaspedro'
- `kind text not null`                -- ex: 'email_reply'
- `ref text not null`                 -- id do item no app, ex: 'ferias-fernanda-07-2026'
- `choice text`                       -- ex: 'concordar' | 'duvida' | 'recusar'
- `meta jsonb not null default '{}'`  -- ex: {"para":"dp@rochacontab.com.br","assunto":"..."}
- `status text not null default 'pending'`  -- pending | done | failed | ignored
- `result text`                       -- msg curta do executor (ok/erro)
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`

Índice: `(status, created_at)`. Anti-duplicata: índice único parcial em `(app, ref, choice)` onde `status='pending'` (evita enfileirar o mesmo clique 2x).
**Habilita Realtime na tabela** (adicionar à publication `supabase_realtime`) — assim o executor local recebe o INSERT na hora, sem polling. É o que faz virar "webhook de verdade".

### 2) Secret compartilhado
Gera um token forte `CONCIERGE_TOKEN` (32+ bytes). **Guarda no Bitwarden** (projeto/cofre do core E um espelho no cofre financaspedro — o app vai precisar) — NUNCA no chat. Seta no Core:
`supabase secrets set CONCIERGE_TOKEN=<valor> --project-ref hjclvuzugdbpvnomvtpn`

### 3) Edge functions (Deno) — autenticadas por token (padrão v1-notify → `--no-verify-jwt`)
Todas exigem header `x-concierge-token: <CONCIERGE_TOKEN>` (401 se faltar/errar). Envelope de resposta no padrão do Core.

- **`v1-concierge-inbox`** (POST) — o WEBHOOK. Body `{app, kind, ref, choice, meta}`.
  Valida token → INSERT status='pending' (se já existe pending igual, retorna o existente, idempotente) → `{ok:true, id}`.
- **`v1-concierge-pending`** (GET) — pro executor local. `?app=financaspedro` opcional. Retorna as linhas `status='pending'` (id, app, kind, ref, choice, meta, created_at).
- **`v1-concierge-ack`** (POST) — pro executor local. Body `{id, status, result}` (status ∈ done|failed|ignored) → UPDATE + `updated_at=now()`.

Deploy:
`supabase functions deploy v1-concierge-inbox --project-ref hjclvuzugdbpvnomvtpn --no-verify-jwt`
(idem pending e ack).

### 4) Contrato pra eu (sessão financaspedro) plugar depois
Me devolve confirmado: (a) URLs das 3 fns, (b) que o `CONCIERGE_TOKEN` está no Bitwarden do cofre financaspedro (por nome/secret-id, sem valor), (c) Realtime ligado na tabela e qual o schema/nome exato pra subscribe (`realtime` channel: `concierge_actions`). Com isso eu: no financaspedro, faço o `/api/responder` (server-side) chamar `v1-concierge-inbox`; e troco o executor local pra escutar o Realtime do Core (ou dar fallback em `v1-concierge-pending`) e enviar via SMTP (senha Bitwarden), depois `v1-concierge-ack`.

Retrocompat/aditivo, provider (Core) sobe primeiro. Sem segredo no chat.
