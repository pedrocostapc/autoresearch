# SuperSec — ESTEIRA COMPLETA: 11/11 missões construtivas fechadas (08-12/07)

Executora encerrando o plano `docs/esteira/plano-execucao/` (LEIAME seguido à risca).
Canal COMUNICACAO-INTERNA.md fechado com `--- FIM ---`.

## Placar
01 Fiscalização ✓ · 02 Societário/Empréstimos ✓ · 03 Cartões (dormente por decisão) ·
04 Calendário/Pendências ✓ · 05 Fiscal DAS ✓ · 06 Contabilização/Razão ✓ (modelo v3) ·
07 Patrimônio ✓ · 08 Folha/Encargos/eSocial ✓ · 09 Obrigações ✓ · 10 Fechamento/
Auditor ✓ · 11 Gerencial/Entrega ✓. Missão 12 (calibração com docs reais) fica
ABERTA — é iterativa com o Pedro (roteiro: OFX → boletos → PIX → holerite → NFS-e).

## A prova final que resume a esteira
Cruzamento do auditor (missão 10) sobre dado real: Σ das 127 NFs × Σ das partidas
no razão = 38.084.833 = 38.084.833 centavos — diff 0,00%. O caminho inteiro
(frota lê → movedor classifica → curador extrai → contabilização lança → auditor
confere) fecha AO CENTAVO.

## Páginas novas no ar (Vercel)
/razao · /imobilizado · /folha · /fechamento · /gerencial + Hoje (2 blocos) +
Obrigações Acessórias (lista viva) + Impostos (confronto DAS). Painel Ao Vivo:
7 curadores + 10 agentes acesos + cartões dormente.

## Bugs reais mortos no caminho (pro histórico)
1. ledger NOT NULLs + índice único installment (missão 02). 2. Clobber do movedor
em doc processed (early-exit, arbitragem). 3. address JSONB / MG-NOTA / smallint
anexo (tipos da ficha). 4. accounting_entries da spec × modelo v3 (censo!).
5. Curador holerite NUNCA materializava payslip (payment_date NOT NULL mudo).
6. Faixas INSS dos agentes eram 2025; tabela viva 2026 decide.
7. bank_statement_lines.posted_at (não transaction_date).

## Regras que ficaram (bastão)
Censo antes de criar · spec cede à realidade · teste confere o EFEITO na tabela
destino · sb() engole erro (rodar run() local pra ver HTTPError) · installment_number
em N parcelas · NOT NULLs e uniques de EXPRESSÃO antes de materializar · tabela
decide contra prompt de agente · pendência nomeada, nunca chute.

## Pendências herdadas (fora da esteira)
- 125 NFs sem emission_date (partidas caíram em created_at) + Solar NF 250
  (rename R$145 × item R$5.019) — dados, com a supervisora.
- v2 nomeadas: Presumido fiscal (PIS/COFINS/IRPJ tri), apuração caixa, ST/monofásico,
  CIAP, gerador SPED, HE/adicionais da folha, transmissão eSocial (A1), balancete.
