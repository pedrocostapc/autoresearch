# Balanço — financaspedro (concierge financeiro do Pedro)

> App pessoal do Pedro: dashboard financeiro que virou painel-concierge. Repo
> `~/Dev/financas-pedro` (GitHub privado `pedrocostapc/financas-pedro`), host
> Vercel `financaspedro.vercel.app` (scope `risen-midia`), backend próprio +
> Risen Core. NÃO é da suíte comercial — é a ferramenta de comando do Pedro.
> Data: 2026-07-06. Irmão deste: `2026-07-06_1700_core-concierge-bridge-prompt.md`.

## PASSADO (o que a gente fez nestes últimos dias)

**No ar e provado:**
- **App hospedado**: static HTML gerado por `build_dashboard.py` (Python → 1 index.html,
  JSON embutido + BUILD_ID md5). Deploy = `git push main` → Vercel. Abas: Pensão (Lara),
  A Pagar, Responder, Gastos, Investigar, Categorias.
- **Auth por cookie** (middleware.js): login próprio (env `SITE_PASSWORD`/`SITE_TOKEN` no
  Vercel) — porque **Basic Auth não funciona em PWA no iOS**. PWA instalável + **Web Push**
  (VAPID em `~/.risen-mail/push/`, `send.py`), popup "nova versão".
- **Contas a Pagar (pipeline)**: e-mail → `~/.risen-mail/contas_a_pagar.py` (dedup por
  **md5 de conteúdo**) → Dropbox por empresa → `regen_contas.py` (páginas PNG via fitz +
  linha digitável + barcode/QR via zxing) → app com **viewer embedded** (iOS não renderiza
  PDF em iframe) + "copiar código de barras / Pix" dentro do doc.
- **CONCIERGE BRIDGE (a grande entrega de hoje)** — "Pedro clica no app → e-mail é enviado":
  `app /api/responder → Core v1-concierge-inbox (fila durável) → Supabase Realtime → braço
  local concierge_arm.py → SMTP (senha do Bitwarden) → v1-concierge-ack`.
  - Core ref `hjclvuzugdbpvnomvtpn`; fns `v1-concierge-inbox` / `-pending` / `-ack`
    (auth `x-concierge-token`, 401 sem). **Testado ao vivo**: inbox grava, pending lista,
    ack marca, **Realtime empurra o INSERT em sub-segundo**.
  - Secret-ids no **Bitwarden cofre financaspedro** (só ID, nunca valor):
    `CONCIERGE_TOKEN` = `4437a150-caf0-493c-b4f9-b47f01516e12` ·
    `CORE_SERVICE_ROLE_KEY` = `ae3db503-55dc-49f5-9807-b47f01598952`.
  - Braço = `~/.risen-mail/concierge_arm.py` (poll+envio+ack, idempotente) +
    `~/.risen-mail/concierge_realtime.mjs` (listener WS nativo do Node 26 → aciona o braço;
    safety-kick 30s).
- **E-mails reais enviados** (autorizados por clique/chat): honorário Rocha (confirmar
  recebimento) e férias Fernanda. **Fernanda**: contabilidade fez **abono 10 dias + 20 de
  gozo (13/07→01/08, retorno 02/08)** como o Pedro pediu; aviso/recibo pra assinar.

**O que melhorou (estava ruim → arrumado):**
- Envio de e-mail: de "SMTP_PASS no Vercel" (bloqueado, fere a regra Bitwarden) → **Core
  stateless + braço local** (segredo só no Bitwarden).
- Ponte do clique: de **log do Vercel** (frágil, expira em ~1h) → **fila durável no Core**.
- Doc viewer: PDF em iframe (branco no iOS) → páginas como PNG embedded, com "← Voltar".
- "Marcar pago" marcava item errado (id colidia por empresa) → `cid = web||empresa|nome|venc`
  + `stopPropagation`.

## O QUE APRENDEU
- **iOS PWA é traiçoeiro**: Basic Auth não abre caixa; PDF não renderiza em iframe; Web Push
  só via ícone na Home Screen (16.4+). Desenhar sempre pra standalone.
- **Guardrail de segurança** bloqueia (a) segredo → Vercel e (b) instalar persistência
  (launchd) sem OK explícito. É a regra do Pedro sendo cumprida por máquina → **arquitetar
  pra respeitar**: segredo fica local (Bitwarden), persistência/secret-em-Vercel = **o Pedro
  roda** num terminal dele.
- **Node 26 tem `WebSocket` nativo** → dá pra falar Supabase Realtime (Phoenix: phx_join +
  heartbeat 25s) **sem npm**.
- **Core como "ouvido 24/7"**: um webhook de verdade precisa de endpoint sempre-ligado; o
  Core (já 24/7, já broker) é o lugar certo — e a máquina do Pedro fica logada 24h pro braço.
- Dedup de documento = **hash de conteúdo, nunca por valor** (ver [[contas-diligencia]]).

## O QUE ERROU / BUGS
- **DARF INSS 318 quase perdido**: dedup por valor sobrescreveu (318 e 322 = ambos
  R$18.736,72, refs distintas). Corrigido: md5 + sufixo de hash no nome. **RESOLVIDO** — e
  virou regra de ouro do monitor.
- **JS quebrado foi ao ar** uma vez (o `git commit` rodou apesar do `node --check` falhar).
  Corrigido e virou disciplina: **validar `node --check` ANTES do push**. **RESOLVIDO.**
- **Recorrente (ESPREITA sempre)**: em raw string do build (`HTML=r'''...'''`), `\\n` vira
  `\n` literal e `\\"` **quebra o JS**. Usar `\n` simples; nunca `\\"`. Volta toda hora.
- **linkrsn (Supabase ~R$600/mês)**: tentativa de "pausar" falhou (exige free-tier antes) →
  **nada foi mudado**. Decisão (pausar/deletar/mover) ainda **ESPREITA** — só linkrsn.

## PRESENTE (onde cada frente está)
- **App**: no ar, funcional (abas, viewer, push, contas a pagar). ✅
- **Concierge Bridge**: construído e **provado ponta-a-ponta EXCETO** o hop navegador→Core —
  **TRAVADO esperando** o Pedro rodar 1 bloco de terminal que (a) põe `CONCIERGE_TOKEN` no
  Vercel e (b) instala o motor 24/7 (launchd `com.risen.concierge-arm` rodando o listener
  Realtime). Braço + Realtime já testados (sub-segundo). Até lá, fallback por log funciona
  quando o monitor roda.
- **Monitor horário** (ScheduleWakeup ~3600s): docs a pagar, cliques, e-mails p/ responder,
  falhas de pagamento, push. Ativo.
- **Respostas pendentes no app**: `fichar-george-07-2026` (Pedro ainda não clicou).

## FUTURO (pra onde vamos)
- **Próximo passo concreto**: Pedro roda o bloco (token Vercel + launchd) → **teste real de
  ponta a ponta** (clicar no app e ver o e-mail sair em segundos, 24h).
- Depois: monitor passo-4 100% no `concierge_arm` (Core); **aposentar** o `responder_bridge`
  por log (evitar envio duplo).
- **Rumo**: o Concierge Bridge é **capability genérica do Core** — qualquer app da frota vai
  poder enfileirar "Pedro aprovou X → executa" (pagar boleto, responder, etc.). Financaspedro
  é só o primeiro consumidor.
- **Aberto pro Pedro**: linkrsn (decisão de custo); senhas dos PDFs CEMIG/Caixa; assinar o
  aviso/recibo de férias da Fernanda; upgrade Realtime já provado (usar service_role).
