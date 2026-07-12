# SuperSec — Missão 04 CONCLUÍDA: Motor Calendário/Pendências vivo e provado

Executora. Bateria final em prod passou inteira:
- Julho/2026: EFD-Contribuições 14/07 (10º dia útil), DAS 20/07 (unidade Simples =
  RISEN MIDIA), PIS/COFINS 24/07 (25 = sábado → ANTECIPOU sozinho), IRPJ/CSLL T2 31/07.
- Setembro: DAS 20/09 (domingo) → 18/09. Outubro: IRPJ/CSLL T3 → 30/10 (31 = sábado).
- FGTS/GPS/eSocial omitidos HONESTAMENTE (zero employees ativos no banco — aparecem
  sozinhos quando a folha nascer).
- Pendências jun/2026: Extrato e NF-entrada em gap (ALTA · D-10); hoje_resumo com
  as chaves calendario (4) e pendencias_docs (5).

## Commits
- backend `5b43dc1` + fixes `28ca7e5` (address JSONB) + `53e0e7c` (regex feriados) —
  migration re-aplicada 2x pela supervisora.
- front `5930772` pushado (blocos "Vence este mês" + "Faltam documentos" na página
  Hoje; card `cal` ativo). worker-avisos (D-3 sem guia) + movedor early-exit em prod.

## REGRAS NOVAS pro bastão
- **Grupo de consulta que mistura linhas-dado com linhas-NOTA exige guarda de formato
  no consumidor** (ex.: 'MG-NOTA' explodiu cast); melhor ainda: nota vai em
  referencia_grupo.descricao, nunca como item (mea culpa da supervisora, regra dela).
- `company_units.address` é JSONB com chave `uf` — usar `address->>'uf'`.
- Helpers de dia útil prontos pra todo mundo: `fx_feriados(ano,uf)`, `fx_ajusta_util
  (data, antecipa|prorroga|nao_ajusta, feriados)`, `fx_ultimo_dia_util`,
  `fx_n_esimo_dia_util` — Agente Fiscal (05) e Obrigações (09) devem REUSAR.
- Validação barata: aritmética de helpers dá pra provar por SELECT read-only em prod
  ANTES de pedir re-apply.

## ➡️ Missão 05 (Agente Fiscal DAS) — RECADO APROVADO (Pedro+supervisora)
Com a unidade Presumido descoberta: **v1 DAS-first POR UNIDADE (só a Simples =
RISEN MIDIA / crt=1), sem misturar regimes numa apuração**. Unidade Presumido
(PC CONSTRUTORA) fica nomeada pra v2: PIS/COFINS cumulativo 3,65% + IRPJ/CSLL
trimestral pela presunção — tabelas `presuncao-presumido` e
`pis-cofins-aliquotas-cumulativo` JÁ EXISTEM. É o coração do produto: confronto
guia calculada × lida completo na página Impostos.
