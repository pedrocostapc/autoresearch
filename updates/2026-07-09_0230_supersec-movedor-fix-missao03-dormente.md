# SuperSec — Fix do Movedor (arbitragem) + missão 03 dormente — PROD PENDENTE: deploy movedor

## Fix do Movedor commitado (`d51e382`) — AGUARDA DEPLOY (supervisora)
- Early-exit total no `processOne`: doc `status='processed'` → carimba a ficha e sai
  ANTES de qualquer classificação/PATCH (raw_data intacto). Guard parcial de status
  removido (redundante). `type` incluído no select. Deno check: só os 6 erros
  pré-existentes (linhas 209/389 + _shared/) — nada novo.
- **REGRA NOVA no bastão (substitui a antiga "não descataloga"): Movedor não toca em
  documento processed — carimba a ficha e sai.** Reprocesso intencional segue vivo
  (reprocessar_documentos reseta status antes).
- [ ] PROD: `supabase functions deploy worker-2-movedor --project-ref abysijyuhvwrczxnwaqg --no-verify-jwt`

## Sanity dos XMLs (instrução da supervisora) — FEITO
- 127 nfe processed: **2 sem raw_data.fiscal** → fase 2 re-enfileirada (attempts=0,
  status pending) pros docs `9c28074d` (SOLAR NF 250) e `8af06d7f` (Ferp NF 113378).
  Curador NFe é idempotente; frota regrava sozinha.
- ⚠️ ACHADO PRA SUPERVISORA: **125 dos 127 não têm raw_data.curador** (mas 123 deles
  TÊM fiscal). nfe.py grava "curador" na l.315 — ou o lote rodou numa versão anterior
  ao bloco "curador", ou o clobber do retry levou o curador e o "andar fiscal"
  (patch separado, l.385) regravou só o fiscal depois. Se a hipótese 2 for real, a
  chave-44/herança pode ter sido perdida nesses docs. Vale ela olhar 2-3 exemplos
  com o contexto da construção do v4. Não mexi além dos 2 da instrução.

## Missão 03 — Cartões: DORMENTE (decisão Pedro/supervisora 09/07)
- Tenant não usa maquininha → card `cart` marcado dormente no painel (front `2506a53`),
  curador não construído, conforme o arquivo da missão previa. Quando ele usar:
  construir com installment_number na agenda 12×.

## Próximo
➡️ Missão 04 (Motor Calendário/Pendências, agentes 25·21) — iniciando em seguida.
Front: cards fisz/soc ativos, cart dormente (commits 1513c9b, bcee2d4, 2506a53).
