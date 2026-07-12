# SuperSec — Missão 06 v2 (modelo do projeto-base v3) — PROD DA 06 V2

Executora. A v1 da migration bateu em tabela pré-existente: o banco JÁ TINHA a
fundação contábil do projeto-base v3 (accounting_entries cabeçalho +
accounting_entry_lines D/C + chart_of_accounts com reference_code versionado +
FKs de depreciation_entries/provisions/lalur_records). Veredito Pedro+supervisora:
ADOTAR o modelo vivo (escolha A). Migration reescrita (`3eaad56`), página /razao
adaptada pra partida composta (`64a9911`, pushado).

## PROD DA 06 V2 (pra supervisora)
- [ ] `bash scripts/aplicar_migration.sh supabase/migrations/20260711010000_agente_contabilizacao_razao.sql`
      (seed chart_of_accounts ~65 contas + fx_lancar/contabilizar_* + cron 15min;
      commit `3eaad56` — nada da v1 foi aplicado, banco estava intacto)
- Depois: executora testa contabilizar_documento numa NF real das 127, deixa o
  cron varrer o backlog, confere Σ mês × Σ notas na página, acende o `contab`.

## ⚠️ REGRAS NOVAS pro bastão (as 2 do veredito)
1. **Antes de criar tabela de missão: CENSO primeiro** —
   `information_schema.tables` por palavra-chave do domínio. As specs 06-11
   foram escritas SEM o censo das 141 tabelas do projeto-base v3 — onde
   conflitarem, **spec cede à realidade** ("a verdade é o sistema ao vivo").
2. **Missões 07/08: inventariar ANTES de codar** — depreciation_entries,
   provisions, lalur_records e vizinhas (procurar fixed_assets/assets também).
   Provável que metade do schema já exista: o trabalho é LIGAR a esteira ao
   modelo, não criar o modelo.

## Notas técnicas da v2
- fx_lancar valida ΣD=ΣC (exception se não fechar) — partida composta de verdade.
- entry_number sequencial por tenant; status 'posted'; unidade fallback matriz.
- contabilizar_pendentes com exception handler POR DOC (um doc ruim não derruba
  o cron — lição do incidente dos US$419, outra família).
- reference_code semeado só onde o agente 36 dá o código; resto "— a completar"
  na aba Plano de Contas (grupo do referencial RFB não existe no banco).
