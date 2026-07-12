# SuperSec — Missão 06 CONCLUÍDA: Contabilização viva no modelo v3 (127 docs no razão)

Executora. Teste em prod passou:
- NF real (22928 CATALAO AREIA): partida #1 D 1.1.3.01 Mercadorias R$ 3.730,00 /
  C 2.1.1.01 Fornecedores — histórico "NF 22928 — CATALAO IND. COMERCIO DE AREIA
  LTDA", status posted, ΣD=ΣC validado pelo fx_lancar.
- Backlog varrido: 127/127 docs contabilizados pelo contabilizar_pendentes.
- Σ mês × Σ notas: fev e mar batem AO CENTAVO; julho difere R$ 5.019,00 = UM doc
  (ver achado abaixo). Página /razao no ar com partidas agrupadas + Plano de Contas.

## Commits
- backend `3eaad56` (migration v2, aplicada) · front `64a9911` (/razao v2) +
  `1092f85` (card contab). Cron jobid 31 (15min).

## ⚠️ Achados de DADO pra supervisora (não são da missão 06 — contabilização caiu honesta)
1. **125 das 127 NFs estão com emission_date NULL** (nem curador nem llm têm a
   data) — as partidas caíram em created_at (09/07). Quando o dado nascer, basta
   apagar as entries do agente e deixar o cron regravar (reprocesso substitui).
   Cheiro: lote dos XMLs completados por chave-44 não propaga data de emissão.
2. **Solar NF 250 (doc 273b8f7e)**: llm.valor_total NULL (é um dos 2 que perderam
   bloco no clobber do movedor) e nome do arquivo diz "R$ 145,00" mas o único
   item (laje pré-fabricada) soma R$ 5.019,00. Contabilizada pelos itens (honesto).
   Conferir contra o XML original — ou o rename está errado, ou o item.

## Estado: 6 de 12 (5 vivas + 1 dormente)
➡️ Missão 07 (Patrimônio/Imobilizado) — abrindo PELO CENSO, como manda o bastão:
inventário de depreciation_entries, provisions, lalur_records, fixed_assets/assets
ANTES de qualquer linha de código.
