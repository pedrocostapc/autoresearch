# 5 Formas de Reduzir Custo com Claude Code

5 aplicacoes especificas pra cortar gastos em ferramentas SaaS. Implementa hoje, economiza esse mes.

> Este pacote nao e teoria. Sao **5 prompts cirurgicos**, **uma calculadora de ROI** que diz se vale migrar antes de voce mexer, **um checklist de migracao** pra nao perder dado/cliente no caminho, e **scripts/configs prontos** dentro de cada prompt.

## A premissa

Voce paga ferramenta SaaS porque elas resolvem problema. **Boa parte delas sao wrappers de IA + alguma interface**. Quando o Claude Code resolve o mesmo problema, a ferramenta vira custo puro.

Esse pacote ensina a fazer essa troca **com seguranca**: sem perder dado, sem quebrar operacao, sem cancelar antes de ter substituto rodando.

## Faixa de economia tipica

Olhamos 30 PMEs reais (faturamento R$ 100k-2M/ano). Stack tipica de SaaS pago no segmento:

| Categoria | Tipo de ferramenta | Faixa mensal |
|---|---|---|
| Copywriting | Jasper, Copy.ai, Writesonic | R$ 200-500 |
| Automacao | Zapier, Make, n8n cloud | R$ 150-800 |
| BI/Dados | Power BI Pro, Looker Studio Pro | R$ 300-2.000 |
| Atendimento | Manychat, Chatbot.com, Botconversa | R$ 200-700 |
| Documentos | PandaDoc, DocuSign, Notion AI | R$ 150-600 |

**Total tipico:** R$ 1.000 a R$ 4.600/mes. Anual: **R$ 12k a R$ 55k**.

Substituindo por Claude (assinatura Pro R$ 100/mes ou API conforme uso, ~R$ 50-200/mes pra PME):
**economia liquida tipica: R$ 800 a R$ 4.300/mes** = **R$ 9.600 a R$ 51.600/ano**.

> Antes de cancelar nada, leia `00-LEIA-PRIMEIRO.md` e rode `CALCULADORA-ROI.md` pro seu caso.

## Conteudo

| # | Arquivo | Conteudo |
|---|---|---|
| 00 | LEIA-PRIMEIRO | Mentalidade, ordem, o que funciona e o que nao |
| 01 | COPYWRITING | Substitui Jasper/Copy.ai (com prompt de marca + biblioteca) |
| 02 | AUTOMACAO | Substitui Zapier/Make (com codigo Node + agendamento cron) |
| 03 | ANALISE-DE-DADOS | Substitui BI (com prompt de analista + exemplos por setor) |
| 04 | ATENDIMENTO | Substitui Manychat/Chatbot (com base de conhecimento + integracao) |
| 05 | DOCUMENTOS | Substitui PandaDoc/DocuSign (com 8 tipos de documento + assinatura) |
| C1 | CALCULADORA-ROI | Diz em 5 minutos se vale migrar pro seu caso |
| C2 | CHECKLIST-MIGRACAO | 12 passos pra trocar sem perder dado/cliente |

## Ordem recomendada

1. `00-LEIA-PRIMEIRO.md` — premissa e quando NAO substituir
2. `CALCULADORA-ROI.md` — voce sabe se vale antes de mexer
3. `CHECKLIST-MIGRACAO.md` — como migrar cada categoria
4. Os 5 prompts em ordem (01 a 05) ou pulando direto pra categoria de maior gasto

## Onde rodar cada prompt

| Prompt | Onde | Por que |
|---|---|---|
| 01 — Copy | Claude.ai (web) ou Code | Caso a caso, web e mais rapido |
| 02 — Automacao | Claude Code (CLI) | Vai criar arquivo + agendar cron |
| 03 — Dados | Claude Code (CLI) | Roda na pasta com os CSVs |
| 04 — Atendimento | Claude Code pra base + API pra responder | Volume justifica integracao |
| 05 — Documentos | Claude.ai ou Code | Caso a caso |

---

**ASV Digital** — produtos@asv.digital
