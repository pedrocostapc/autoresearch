# SuperSec — Missão 07 CONCLUÍDA: Patrimônio vivo (censo → ligar, não criar)

Executora. Teste sintético em prod passou inteiro e foi limpo (zero sobras):
NOTEBOOK DELL R$ 5.000 (item is_for_fixed_asset, CFOP 1551) → capturar_imobilizado
→ bem "Computadores e periféricos" 60 meses → rodar_depreciacao(7/2026) →
R$ 83,33 em depreciation_entries + partida D 5.5.1/C 1.2.3.99 no razão (backlink
accounting_entry_id) → idempotente (2ª rodada = 0 bens; unique natural bem×período).

## Commits
- backend `ec592cf` (migration aplicada; cron jobid 32, dia 1º 06:20 UTC)
- front `4f8f83d` (/imobilizado com vida útil editável) + `26fdac3` (card patr)

## Decisões registradas
- Censo primeiro FUNCIONOU: fixed_assets/depreciation_entries já existiam (v3) —
  só 1 coluna aditiva (document_item_id). Captura usa a FLAG do curador v4
  (is_for_fixed_asset), não re-deriva CFOP — uma fonte de verdade.
- useful_life_months=0 = sentinela "indefinida" (coluna NOT NULL na fundação;
  nunca chutar vida útil — página deixa definir e o motor pula 0).
- < R$ 1.200 (RIR 313 II) não imobiliza — pendência 'reclassificar_despesa'
  (a contabilização da 06 já lançou em imobilizado; humano decide).
- CIAP = v2 (Simples não credita — pegadinha 6; Presumido entra com Bloco G).
- Teste sintético com doc processed: INSERT dispara trigger de fase 1 — criar
  doc+item+delete jobs NUMA TRANSAÇÃO só (frota não vê). document_items.cfop é
  NOT NULL.

## Estado: 7 de 12 (6 vivas + 1 dormente)
➡️ Missão 08 (Folha/Encargos/eSocial — o maior bloco restante) — abrindo PELO
CENSO: provisions, provision_items e vizinhas (payroll?, esocial?).
