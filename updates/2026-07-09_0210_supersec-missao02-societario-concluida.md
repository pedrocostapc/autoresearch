# SuperSec — Missão 02 CONCLUÍDA: Curador Societário/Empréstimos vivo (2 bugs reais mortos)

Executora da esteira. Sanity final PELA FROTA passou: CCB sintética → processed +
12 payables no ledger (installment 1..12, 10/08/2026→10/07/2027, R$ 13.200,
counterpart = CNPJ do banco). Teste limpo (docs=0, ledger=0, storage limpo).

## Commits
- backend `9a8a027` (curador v1) + `8612fcc` (fix 1) + `97b1737` (fix 2) — push ok.
- front `bcee2d4` (card soc "ativo"). Migration `20260709130000` aplicada (supervisora).

## Os 2 bugs (achados PROVANDO contra o banco — pegadinha nº 1 do LEIAME em ação)
1. `ledger.counterpart_cnpj_cpf` e `company_unit_id` são NOT NULL → lote caía mudo.
   Fix: CNPJ da contraparte = 1º CNPJ do texto que não é nosso; unidade = a do doc
   ou a MATRIZ do tenant; sem unidade → needs_review nomeado.
2. Índice único `ledger_source_doc_installment_uidx` (source_doc, COALESCE(installment,0))
   → 12 parcelas sem installment_number colidiam em (doc,0), 409 no lote inteiro.
   Fix: installment_number = k.

## REGRAS NOVAS pro bastão (valem pras próximas missões)
- **Curador que materializa N linhas de ledger por documento NUMERA installment_number**
  (vale pro Cartões/missão 03 e qualquer parcelamento).
- Técnica de diagnóstico: rodar o `run()` do importer LOCALMENTE com o sb() do worker
  (copiado, com print do HTTPError) contra o doc real — o erro engolido aparece na hora.
- Conferir NOT NULLs e ÍNDICES ÚNICOS (não só constraints!) da tabela-alvo ANTES de
  materializar: `pg_constraint` não mostra unique INDEX parcial/expressão.

## Estado
Missões 01 e 02 concluídas e testadas. ➡️ Missão 03 (Cartões) AGUARDA resposta do
Pedro: usa maquininha? (sim → construir; não → card `cart` dormente e pular pra 04,
como o arquivo da missão prevê). Pergunta feita às 02:05.
