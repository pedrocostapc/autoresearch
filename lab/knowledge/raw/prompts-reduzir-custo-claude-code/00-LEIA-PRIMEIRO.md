# 00 — Leia primeiro

Esses 5 prompts cortam custo onde o Claude entrega o mesmo valor de uma ferramenta SaaS.

## A logica honesta

Voce nao paga ferramenta SaaS pelo software. Paga por:

1. **Capacidade nucleo** (gerar texto, integrar APIs, montar dashboard, atender cliente, gerar documento)
2. **Interface** (UI bonita, formulario, drag-and-drop)
3. **Compliance** (SOC 2, contrato com SLA, certificacoes)
4. **Conveniencia** (botao na hora, app mobile, time de suporte)

O Claude entrega **(1)** com facilidade. Nao entrega (2), (3) ou (4).

Pergunta de migracao: **voce paga aquela ferramenta principalmente pelo (1) ou pelos outros?**

- Se (1) com pequena variacao: **provavel substituicao com economia grande**.
- Se voce precisa de (2) porque varias pessoas precisam usar: **pesa**.
- Se voce precisa de (3) porque tem cliente enterprise/regulado: **nao migra**.
- Se voce precisa de (4) porque a operacao nao tolera intervalo: **avalia**.

## Onde substituicao funciona muito bem

- Empresa com 1-30 pessoas
- Volume baixo a medio (centenas a alguns milhares de operacoes/mes)
- Pelo menos 1 pessoa do time confortavel com Claude / minimamente tecnica
- Nicho B2B/B2C sem regulacao pesada
- Operacao tolera 30s-2min de "delay" em cenarios assincronos

## Onde NAO substituir

| Situacao | Por que ainda fica com SaaS |
|---|---|
| SLA de milissegundos (chat alta concorrencia) | Latencia da API + complexidade |
| Compliance SOC 2 / HIPAA / LGPD enterprise | Fornecedor precisa ser certificado |
| Time de 50+ pessoas com fluxo colaborativo | UI/permissionamento exigem ferramenta |
| Operacao 24/7 sem ninguem pra rodar | Pode automatizar, mas custo de manutencao sobe |
| Quem mexe nao tem nenhum perfil tecnico | Curva de aprendizado |

Honestidade: **das 5 categorias deste pacote**, em 80%+ das PMEs uma migracao parcial vale ouro. Nao migracao completa de tudo.

## Estrategia recomendada (passos)

### Passo 1 — Calcular ROI antes de mexer

Roda `CALCULADORA-ROI.md` pra cada ferramenta paga. So migra a que:

- Economia mensal > R$ 200
- Volume cabe no Claude (definido por categoria)
- Voce tem 4-8h pra montar a substituicao + 1 semana de teste paralelo

Sem isso, e tempo gasto pra economizar troco.

### Passo 2 — Migrar UMA categoria de cada vez

Erro comum: querer trocar tudo no mesmo mes. Resultado: nada funciona direito, voce volta pra todas as ferramentas, perdeu 3 semanas.

Sequencia que funciona:

1. **Primeira migracao** — escolha a de maior gasto + menor risco operacional
2. Rode em paralelo com a ferramenta antiga por **7-14 dias**
3. Compara qualidade do output, tempo gasto, satisfacao
4. Se passa nos 3 criterios, cancela a ferramenta antiga
5. Migra proxima categoria so depois que essa estabilizou

### Passo 3 — Versionar tudo

Tudo o que voce monta com Claude (prompts, base de conhecimento, scripts) **vai pra Git**. Razao: voce vai melhorar com o tempo, e ter historia importa. Se em 3 meses a saida piorou, voce volta pra versao anterior.

## Ordem sugerida pelas 5 categorias

Por retorno tipico esperado (impacto x esforco):

1. **02 — AUTOMACAO** (Zapier/Make sai caro com volume, Claude resolve maioria com cron)
2. **03 — ANALISE DE DADOS** (BI subutilizado em PME — quase ninguem abre o dashboard)
3. **01 — COPYWRITING** (alta frequencia = ROI rapido)
4. **04 — ATENDIMENTO** (depende muito do volume — calcula antes)
5. **05 — DOCUMENTOS** (ganho menor, mas paga sozinho)

Voce pode pular a ordem se sua categoria de maior gasto for outra.

## Custos reais do Claude (referencia 2026)

- **Claude Pro (web)**: US$ 20/mes (~R$ 110)
  - Suficiente pra 80% dos casos de uso de PME
  - Sem API, sem programacao
  - Volume: alto, mas com limite por sessao

- **Claude Code (CLI)**: usa creditos da sua conta Pro (cabe na assinatura) ou paga por uso da API
  - Quando: quando voce vai criar arquivos, integrar, automatizar
  - Custo tipico PME: R$ 50-300/mes adicional

- **API direta**: paga por token (~R$ 15-90 por 1 milhao de tokens, depende do modelo)
  - Quando: integrar dentro de sistema
  - Volume tipico PME: R$ 50-200/mes

Para a grande maioria das PMEs, **Pro + uso eventual da API resolve com R$ 150-400/mes**. Substitui R$ 1k-4k em ferramenta.

## O que NAO esta nesse pacote

- Substituicao de **CRM completo** (RD Station, HubSpot, Pipedrive). Esses tem mais coisa que so IA — nao migra so com prompt.
- Substituicao de **ferramenta de email marketing** (Mailchimp, RD). Mesma logica.
- Substituicao de **ERP**. Sem chance.
- Substituicao de **plataforma de e-commerce**. Idem.

Foque em ferramenta cuja capacidade nuclear e gerar conteudo / processar dado / integrar / responder pergunta.

## Antes de comecar

1. Rode `CALCULADORA-ROI.md` agora (2 minutos)
2. Le `CHECKLIST-MIGRACAO.md` (5 minutos)
3. Escolhe UMA categoria
4. Vai pro prompt correspondente

Boa migracao.
