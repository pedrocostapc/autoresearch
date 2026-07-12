# SuperSec — Missão 05 CONCLUÍDA: Agente Fiscal v1 (DAS) vivo — o confronto fecha o círculo

Executora. `apurar_das(tenant, 6, 2026)` provado em prod: só a unidade Simples
(RISEN MIDIA) apurada — Anexo III faixa 1 (CNAE 73→serviço; fator R n/d com RBT12
zero → nominal 6%), guia CALCULADA R$ 0 com memória passo-a-passo honesta ("SEM
FATURAMENTO — PGDAS-D zero ainda se transmite"), vencimento 2026-07-20 (dia 20 útil,
helpers da missão 04), requires_human_approval=true, IDEMPOTENTE (2 runs → 1 guia).
Contrato do front respeitado (aliquota_efetiva/rbt12_cents/anexo/faixa/...) — a
página Impostos confronta sozinha quando a LIDA chegar pelo CaP.

## Commits
- backend `2f5b8ec` + fix `88c647b` (simples_annexo_preferencial é SMALLINT 1..5)
- front `8b63895` (card fisc ativo) · cron jobid 29 (dia 1º 06:00 UTC)

## Registrado (recado aprovado Pedro+supervisora)
- v1 = DAS-first POR UNIDADE, só crt=1. **NUNCA misturar regimes numa apuração.**
- v2 NOMEADA nas pendências de cada guia: unidade Presumido (PIS/COFINS cumulativo
  3,65% + IRPJ/CSLL trimestral pela presunção — tabelas presuncao-presumido e
  pis-cofins-aliquotas-cumulativo já existem), apuração por CAIXA (regime da RISEN
  MIDIA é caixa; v1 usa emissão), segregações ST/monofásico/ISS-retido.
  Agentes 02/03/04/28/29 são a v2 (a missão 05 já previa).
- Parse das faixas validado read-only ANTES do apply (as 6 do anexo III batem com
  o agente 01; efetiva reproduz o exemplo canônico 14,02%).

## Aprendizado
- `simples_annexo_preferencial` smallint; conferir TIPO das colunas da ficha antes
  de usar em expressão de texto (2º caso: address JSONB).

➡️ Missão 06 (Agente Contabilização/Razão, fontes 37·36) — iniciando.
