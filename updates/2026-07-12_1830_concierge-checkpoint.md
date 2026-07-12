# CHECKPOINT Concierge do Pedro — 2026-07-12 18:30 (retomável do zero)

Escrito pra uma sessão que nasce SEM memória. O "concierge" = eu leio os 7 Gmails do
Pedro, mantenho o app financaspedro (A Pagar / Responder / Minhas / Lara), envio
e-mails por clique no app, monitoro serviços críticos, cuido de Lara/pensão.

## NO AR (funcionando)
- **App financaspedro** (Vercel, estático, deploy = git push main): `~/Dev/financas-pedro`.
  Build: `python3 build_dashboard.py` (lê JSONs em `data/` + `~/Dev/concierge/concierge.db`)
  → `index.html` → push. SEMPRE `node --check` no `<script>` antes do push.
  Abas: 📋 Pendências, 💸 A Pagar, 📨 Responder, 📊 Gastos, 🔎 Investigar, 🔁 Assinaturas,
  **👤 Minhas (NOVA — Despesas PF por categoria, lê do concierge.db)**, 👧 Lara.
- **Banco local** `~/Dev/concierge/concierge.db` (SQLite) = FONTE DA VERDADE. Tabelas:
  categorias, despesas_pf, transacoes_cartao(VAZIA), contas_a_pagar, pensao_*. Git próprio
  em ~/Dev/concierge (commitado). WAL: rodar `PRAGMA wal_checkpoint(TRUNCATE)` antes de commitar.
- **Motor de cliques 24/7**: launchd `com.risen.concierge-arm` roda
  `~/.risen-mail/concierge_realtime.mjs` (WS Supabase Core) → dispara
  `~/.risen-mail/concierge_arm.py` que ENVIA o e-mail escolhido no clique (SMTP, senha do
  Bitwarden) e faz rebuild+push. Core ref hjclvuzugdbpvnomvtpn.
- **Responder** tem 5 e-mails pendentes com 3 versões (concordar/duvida/recusar):
  wamag-nfe-junho, cymi-iptu-imovel, ferp-nf115729, cmcouto-incendio, george-registro-data.
  (arquivo `data/respostas.json`). O Pedro clica → motor envia.
- **A Pagar**: boleto aluguel Madre Lizaura R$2.603,57 venc **14/07** (já pushado).

## CADÊNCIA DO MONITOR (Pedro mudou 12/07) — IMPORTANTE
NÃO rodar de hora em hora. SCAN só em **07h, 10h, 13h, 16h, 19h** (America/Sao_Paulo).
Entre slots: só reagendar quieto (ScheduleWakeup máx 3600s; resposta "⏳"). Controle
`~/.risen-mail/.last_slot`. **Domingo 12/07 PAUSADO** — resume **segunda 13/07 07h**.
O prompt completo do monitor está no último ScheduleWakeup (reusar verbatim).

## PENDÊNCIAS COM DONO
- **[Pedro]** passar a categorização dos 170 estabs do cartão (pessoal×negócio) pra eu
  preencher `transacoes_cartao` e jogar cartão pessoal categorizado na aba Minhas.
  Negócio = anthropic/openai/meta-google ads/tráfego/COGS = EXCLUIR do PF. (não chutar)
- **[Pedro/eu]** HM Publicidade (Humberto, hmpublimulti@gmail.com, Whats 38 9.8837-1850):
  (a) reenviar DETALHAMENTO pendências 2026 (Gov MG/SECOM, 12ª/14ª bi 09/03-05/04, Pirapora
  placas 01/03/17 + Várzea 05/21; FALTA o valor do ORC — só Pedro tem); (b) DECLARAÇÃO
  ELEITORAL escrita pedida 08/07 (frase exata no chat; risco multa); (c) 30ª/32ª bi 99
  Mobilidade ORC-00030 lona×papel.
- **[eu, próximo slot]** monitor normal segunda 07h.

## COMO RETOMAR
1. Ler memórias: concierge-objetivo, concierge-bridge, concierge-db-local,
   despesas-pf-modelo, financaspedro-workflow, contas-diligencia, xgmraw-parenteses-bug.
2. E-mail readonly: `python3 ~/.risen-mail/mail.py {accounts|unread|recent|search|read}`.
   REGRA X-GM-RAW: buscas SEPARADAS, NUNCA "(a OR b)" com parênteses (retorna 0); ASCII.
3. Push pro iPhone: `python3 ~/.risen-mail/push/send.py "titulo" "corpo"`.
4. Segredos: Bitwarden via `bws` (token no Keychain `bws-access-token`). NUNCA no chat/Vercel.
   Token Management Supabase do cofre Core está INVÁLIDO (não sbp_) — se for pro Supabase, PAT novo.
5. Estados: `~/.risen-mail/.critical_alerts.json`, `.rocha_handled.json`, `.onr_handled.json`,
   `.daily_sweep.txt`, `.forrofam_pushed`, `.last_slot`.

## GIT: tudo commitado e pushado (financaspedro e concierge). Nada preso em disco.
