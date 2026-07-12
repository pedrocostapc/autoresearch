# Plano — Frota de máquinas como SERVIÇO multi-projeto (via Core)

> Escrito 2026-07-01. Objetivo: qualquer app Risen despachar OCR/extração na frota (custo zero),
> **via Core broker** (regra: inter-sistema sempre via Core, nada app-a-app direto).
> Guia da frota: `lab/knowledge/wiki/frota-de-maquinas.md`. Core ref Supabase: `hjclvuzugdbpvnomvtpn`.

## Princípio-chave (o que mantém simples)
1. **Signed URL** — o app que despacha entrega um **link fetchable** do arquivo (do Storage/Drive DELE).
   A frota só faz `GET` — **nunca guarda credencial de projeto nenhum**. Mata 80% da complexidade
   (não precisa generalizar o `doc-bytes` pra cada OAuth/Drive).
2. **Assíncrono** — OCR/extração é pesado (segundos a minutos). Não cabe em `v1-call` síncrono:
   é **dispatch → job_id → poll/callback**.
3. **Dual-source na transição** — os workers puxam da fila NOVA (Core) **e** da atual (SuperSec) ao
   mesmo tempo. O SuperSec **não é tocado** enquanto o (B) prova.

## Arquitetura
```
  app (qualquer)                Core (broker v1-call)              Frota (4 máquinas)
  ─────────────                 ────────────────────               ──────────────────
  gera signed URL  ──►  v1-ocr-dispatch  ──► insere fleet_jobs ──►  claim_fleet_job (SKIP LOCKED)
                                (Supabase do Core)                  GET source_url → extrai
  poll ◄── v1-ocr-result ◄──── lê fleet_jobs.result ◄────────────  PATCH result + status=done
```

## Fases

### Fase 1 — Fila da frota no Core (Supabase do Core)
- Migration (prod gated: mostro→valido→aplico): tabela **`fleet_jobs`**
  `(id, app_origem, source_url, doc_type, priority, status ['pending'|'claimed'|'done'|'error'],
    claimed_by, claimed_at, finished_at, result jsonb, error, callback_url null, created_at)`.
- RPC **`claim_fleet_job(p_worker)`** — `FOR UPDATE SKIP LOCKED`, re-claim de travados >10min
  (cópia do `claim_extraction_job` do SuperSec).
- Índice por `(status, priority)`.

### Fase 2 — Capability no Core (broker)
- Edge fn **`v1-ocr-dispatch`**: autentica o app (padrão do broker), insere `fleet_jobs`
  (`source_url, doc_type, app_origem`), retorna `{ job_id }`.
- Edge fn **`v1-ocr-result`**: por `job_id`, retorna `{ status, result | error }`.
- Registrar as duas no roteador do **`v1-call`** (⚠️ confirmar no repo do Core como se registra uma
  action nova — dependência, ver "O que preciso").
- (Opcional) **callback**: quando `status→done`, o Core faz `POST callback_url` do app.

### Fase 3 — Worker genérico (dual-source) — a única peça com miolo
- `worker.py` passa a suportar **N filas**. Config `FLEET_QUEUES=supersec,core` (intercala pra não
  matar uma de fome).
- Modo "fila do Core": reivindica via `claim_fleet_job` no `CORE_URL`; baixa via **`GET source_url`**
  (sem `doc-bytes`); escreve o RAW em `fleet_jobs.result` (`PATCH`) + `status=done`.
- Secrets **ao vivo do Bitwarden**: `CORE_URL`, `CORE_SERVICE_KEY` (projeto de cofre do core).
- ~30–50 linhas: abstrair "fonte de fila" (claim + fetch + writeback) e rodar as fontes num laço.

### Fase 4 — Repontar as 4 máquinas
- Atualizar `.env` de cada worker (M1, M3, Ryzen5, 3060ti) com `CORE_URL` + `FLEET_QUEUES=supersec,core`.
  Secrets do Bitwarden (não hardcode).
- Reiniciar o serviço (launchd/systemd — ver guia da frota §8).
- **Teste**: postar um `fleet_job` de exemplo (um PDF via signed URL de teste) e ver o RAW voltar
  em `fleet_jobs.result`.

### Fase 5 — Contrato + snippet pros apps
- Doc curto "como um app despacha OCR": (a) gera signed URL do arquivo; (b) `v1-call {action:
  'v1-ocr-dispatch', source_url, doc_type}` → `job_id`; (c) poll `v1-call {action: 'v1-ocr-result',
  job_id}` até `done`. Publicar no cérebro + `updates/`.

### Fase 6 (opcional, DEPOIS de provado) — SuperSec migra pro Core
- O SuperSec passa a dispatchar via Core também, aposentando a fila local `extraction_jobs`. Unifica
  tudo numa fila só. **Sem pressa** — só quando o (B) estiver rodando redondo.

## Decisões travadas
- **Signed URL** (não OAuth por projeto). **Assíncrono** (dispatch+poll/callback). **Dual-source** na
  transição (SuperSec intacto). **Secrets ao vivo do Bitwarden**. **Prod gated**.

## O que eu preciso pra executar
- Acesso ao repo do **Core** (`~/Dev/risen/risencore`) + secrets do **cofre do core** no Bitwarden
  (service key do Core, `CORE_URL`).
- **Confirmar o padrão do broker `v1-call`** (como uma action nova é registrada/roteada) — é a única
  incógnita; o resto é padrão que já domino (fila + claim + worker + deploy).

## Complexidade / esforço (honesto)
- Fase 1, 2, 5 = fáceis (SQL + 2 edges + doc) → ~meio dia.
- Fase 3 (worker dual-source) = miolo, mas pequena com o signed URL → ~algumas horas.
- Fase 4 = mecânico (já sei mexer nas máquinas).
- **Total: ~1–2 blocos. Médio, não épico.**

## Riscos
- Não quebrar o SuperSec → **dual-source** resolve (a fila atual segue intacta).
- Expiração do signed URL → o app gera com validade folgada; a frota baixa logo (prioridade).
- Segurança → só apps autenticados no broker despacham; `source_url` é signed (acesso limitado/temporário).
