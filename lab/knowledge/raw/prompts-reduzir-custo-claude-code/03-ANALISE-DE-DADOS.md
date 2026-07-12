# 03 — Analise de Dados

> Substitui: Power BI Pro, Looker Studio Pro, Tableau, Metabase pago, e principalmente o **consultor de BI a R$ 5k-15k por dashboard**.

## Por que substituir

Em PME, o problema com BI nao e fazer o dashboard. E **abrir o dashboard**. Depois que o consultor entrega, o painel piscante vira museu. Ninguem abre, ninguem questiona, ninguem cruza dado novo.

O Claude e melhor pra como **PME realmente usa dado**: voce **conversa**. "Qual o ticket medio dos clientes que vieram de indicacao no ultimo trimestre?" Resposta em 30 segundos.

Voce ainda pode ter dashboard automatico (se quiser), mas a parte que importa — **fazer pergunta nova e ter resposta certa rapido** — o Claude entrega 100x mais rapido.

## Comparativo de custo (Brasil, 2026)

| Ferramenta | Plano popular | Mensal (1 seat) | Anual |
|---|---|---|---|
| Power BI Pro | Pro | R$ 50/seat | R$ 600 |
| Power BI Premium per User | Premium PU | R$ 100/seat | R$ 1.200 |
| Looker Studio Pro | Pro | US$ 9/seat (~R$ 50) | R$ 600 |
| Tableau | Creator | US$ 75/seat (~R$ 415) | R$ 5.000 |
| Metabase Cloud | Starter | US$ 85/mes (~R$ 470) | R$ 5.640 |
| Consultor de BI freelancer | dashboard custom | R$ 3-15k por projeto + manutencao | varia |

vs. **Claude Pro (R$ 110/mes)**: o "analista" trabalha 24/7, atende todas as duvidas que voce tem agora ou que terá depois.

Economia media PME: R$ 100-2.000/mes = **R$ 1.200-24.000/ano** (sem contar consultor).

## Volume

| Volume | Solucao |
|---|---|
| < 1 milhao de linhas | Claude le CSV/SQLite direto, sem dor |
| 1-10 milhoes | Claude com SQLite local (consulta SQL gerada por ele) |
| 10-100 milhoes | Claude + DuckDB (gratis) — performa bem |
| 100M+ | Claude conectado a Postgres/BigQuery via prompt SQL |

## A logica deste prompt

Sao **3 modos de uso**:

### Modo 1 — Analise pontual
Claude.ai (web), upload do CSV. Pergunta e responde. Bom pra "preciso saber X agora".

### Modo 2 — Analise recorrente
Claude Code na pasta com os dados. Claude vira seu analista permanente. Voce versiona perguntas e respostas em arquivos `.md`.

### Modo 3 — Dashboard automatico
Script que roda diaria/semanalmente, gera PDF/markdown e manda pro time. Substitui o dashboard piscante do Power BI.

---

## Modo 1 — Analise pontual

--- COMECO PROMPT MODO 1 ---

Voce e um analista de dados senior trabalhando comigo. Tenho dados em CSV (em anexo OU na pasta atual) e quero responder uma pergunta especifica.

# Contexto do negocio

- Setor: {ex: e-commerce de moda / SaaS B2B / clinica / etc.}
- Modelo: {ex: vendas online + atacado + venda direta}
- O dado em maos representa: {ex: vendas dos ultimos 12 meses; leads do Meta Ads; atendimentos do suporte}
- Ja sei que tem essas peculiaridades: {ex: "preco varia por canal — atacado tem desconto"; "alguns clientes tem cadastro duplicado"; etc.}

# Pergunta central

{O QUE VOCE PRECISA RESPONDER, com o maximo de especificidade}

Exemplos boas perguntas:
- "Qual o ticket medio dos clientes vindos de indicacao no Q4 2025?"
- "Tem alguma correlacao entre desconto dado e probabilidade de cliente repetir compra?"
- "Quais sao os 5 produtos com maior margem real (descontando frete e desconto)?"

Exemplos perguntas ruins (refaz):
- "Como ta o negocio?" (vago demais)
- "Faturamento" (de quando? agrupado por que?)

# Como voce trabalha

## Etapa 1 — Reconhecimento dos dados

1. Liste os arquivos disponiveis (ou que recebi)
2. Pra cada arquivo: descreva em 1 linha (numero de linhas, colunas)
3. Confirme comigo: "entendi assim — {confirmacao}. Esta certo? Falta algo?"
4. So depois da minha confirmacao, segue

## Etapa 2 — Analise

1. Calcula o que precisa pra responder a pergunta
2. Mostra o **passo a passo** do calculo (qual coluna usou, que filtro aplicou, que agregacao)
3. Pra cada numero importante: traz **contexto** (vs. media historica, vs. outro segmento, vs. periodo anterior)

## Etapa 3 — Saida

Em formato:

```
## Resposta direta
{numero}

## Como cheguei
1. Filtrei tabela X por condicao Y
2. Agrupei por Z
3. Apliquei aggregation W
4. Resultado: {numero}

## O que isso quer dizer (interpretacao)
{2-4 linhas em portugues de dono de empresa, nao de analista}

## Verificacoes que fiz
- Conferi se nao tinha NULL/duplicata distorcendo: {sim/nao + qto}
- Comparei com {X} pra sanity check: {resultado}
- Diferenca relevante: {se houver}

## Pergunta de aprofundamento
{1-2 perguntas que fazem sentido investigar a seguir}
```

# Regras criticas

1. **Nunca invente coluna**. Se a pergunta nao da pra responder com os dados que tem, fala "esse dado nao existe nesse CSV"
2. **Nunca finja precisao maior que o dado tem**. Se tem 50 linhas e voce esta projetando ano, deixa o erro explicito
3. **Numero formato BR** (R$ 1.500,00 e 12,5%)
4. **Pergunta ambigua = pede pra desambiguar antes de calcular**

Pode comecar pela Etapa 1.

--- FIM PROMPT MODO 1 ---

---

## Modo 2 — Analista permanente

Quando voce tem dados que sao atualizados (vendas todo dia, leads toda semana), monta uma estrutura permanente:

```
~/analise-{empresa}/
├── dados/
│   ├── vendas.csv (atualizada toda semana)
│   ├── clientes.csv
│   └── leads.csv
├── perguntas/
│   ├── 2026-01-faturamento-mensal.md
│   ├── 2026-01-cohort-retention.md
│   └── 2026-02-ticket-canal.md
├── recorrentes/
│   ├── faturamento-mes-a-mes.md
│   ├── top-clientes.md
│   └── ...
└── CONTEXTO.md  ← arquivo permanente que voce cola em toda analise
```

Onde `CONTEXTO.md` e o equivalente de `marca.md` mas pra dados:

```markdown
# Contexto do negocio — {Empresa}

## Tabelas e seus significados
- vendas.csv: cada linha e um item vendido (varias linhas por venda quando multi-item)
- clientes.csv: 1 linha por cliente, ja deduplicado
- leads.csv: 1 linha por lead (alguns viram cliente — pra cruzar use email)

## Definicoes
- "venda paga": status = pago E status_estorno != true
- "cliente ativo": pelo menos 1 venda paga nos ultimos 90 dias
- "ticket medio": valor_total medio por cliente, nao por linha

## Peculiaridades conhecidas
- Vendas atacado tem 30% desconto (status_canal = atacado)
- Clientes com mesmo email mas nome diferente costumam ser o mesmo (pediu pra deduplicate)
- Em dezembro de 2025 mudamos forma de calcular frete — comparativos de margem antes/depois ficam estranhos
```

Toda analise nova: voce cola CONTEXTO.md + a pergunta. Em 5 segundos, voce tem o analista alinhado.

---

## Modo 3 — Dashboard automatico (roda sozinho)

Em vez de dashboard visual que ninguem abre, voce gera um **dashboard textual em markdown** automatico — chega no email/slack todo dia/semana/mes.

--- COMECO PROMPT MODO 3 ---

Voce vai me ajudar a montar um script que gera dashboard automatico.

# Setup

- Tipo de relatorio: {diario / semanal / mensal}
- Quem recebe: {email / slack — qual canal}
- Que dados usar: {arquivo X, Y, Z OU banco SQL}
- Que formato: {markdown / pdf / html}

# Conteudo desejado

Liste 5-15 indicadores que voce quer ver toda vez:
- {ex: faturamento ate ontem}
- {ex: top 5 vendedores ate ontem}
- {ex: ranking 10 produtos}
- ...

Pra cada um, defina: como calcula, comparacao com periodo anterior?

# O que voce me entrega

1. Script em Python ou Node.js que:
   - Le os dados (CSV/SQLite/Postgres)
   - Calcula cada indicador
   - Monta um arquivo `dashboard-YYYY-MM-DD.md`
   - Manda por email/slack
   - Loga em `logs/dashboard.log`

2. README com como rodar e como agendar via cron (ver prompt 02 — AUTOMACAO)

3. Exemplo de dashboard ja preenchido (com dados ficticios) pra eu ver como vai sair

# Estilo do dashboard

- Comeca com 3 numeros chave (manchete)
- Inclui sempre comparativo com periodo anterior
- Termina com 2-3 alertas/insights (se aplicavel)
- Maximo 1 pagina (se for PDF) ou ~100 linhas (se for markdown)

--- FIM PROMPT MODO 3 ---

---

## Caso de uso real — Camisa BR

### Modo 1 — Pergunta pontual

Marcelo, sabado de manha, querendo decidir se entra ou nao numa campanha de afiliado:

> [cola CSV de vendas + CONTEXTO.md]
> Pergunta: dos clientes que vieram de afiliados nos ultimos 6 meses, quantos compraram mais de 1 vez? Qual o LTV deles vs. clientes vindos de Instagram?

Claude responde em 30 segundos:

```
Resposta direta:
- Clientes de afiliado: 47
  - Compraram 1x: 38 (81%)
  - Compraram 2+: 9 (19%)
  - LTV medio: R$ 287
- Clientes de Instagram: 156
  - Compraram 1x: 95 (61%)
  - Compraram 2+: 61 (39%)
  - LTV medio: R$ 412

Como cheguei: ...

O que isso quer dizer:
Afiliado tras volume mas com pior retencao. Cliente de afiliado custa
~12% (comissao) e gera 30% menos LTV que cliente de Instagram.
Faz sentido afiliado se voce ainda nao tem volume — pra adquirir presenca.
Se ja tem volume, Instagram vale mais o investimento.

Pergunta de aprofundamento:
Os 9 afiliados que repetiram tem alguma caracteristica especifica
(mesmo afiliado de origem? produto especifico)?
```

Marcelo decidiu **nao** entrar na nova campanha de afiliado e botou os R$ 800 que iam pagar comissao em conteudo no Instagram.

Decisao baseada em **5 minutos de analise**.

### Modo 3 — Dashboard semanal

Marcelo configurou um dashboard semanal que roda toda segunda 8h e cai no email dele e da Ana:

```markdown
# Dashboard Camisa BR — Semana 8 a 14 de fev

## Manchete
- Faturamento da semana: R$ 9.847 (+12% vs semana anterior)
- Maior dia: terca (R$ 2.180)
- Ticket medio: R$ 287 (+5%)

## Vendas
- Total: 34 vendas
- Por canal: site 24, atacado 5, whatsapp 5
- Por vendedora: Maria 18, Joana 16

## Estoque
- Critico: FLO-M (3/10), SAL-G (4/10)
- Em transito esta semana: 1 pedido (P0007 — TecidoCo)

## Clientes
- Novos: 8
- Top 3 da semana: Loja Estilo SP (R$ 1.260), Carla M. (R$ 299), Joao S. (R$ 159)
- Inativos novos: 2 (Pedro Almeida, Ana Costa — bater follow-up)

## Alertas
1. FLO-M abaixo do minimo ja faz 4 dias — pedir reposicao urgente
2. Crescimento concentrado em terca — investigar (campanha?)
3. 2 clientes top viraram inativos — fazer reativacao
```

---

## Erros comuns

1. **Pergunta ambigua → numero errado** — sempre confirme entendimento antes de calcular
2. **Comparar pera com banana** — atacado x varejo no mesmo bolo distorce
3. **Pegar so volume e ignorar margem** — vender muito de produto ruim e furada
4. **Dashboard com 50 indicadores** — ninguem le. Maximo 5-10 que importam pro proximo passo
5. **Confiar em numero exato em base pequena** — abaixo de 100 linhas, intervalo de confianca importa

## Quando NAO substituir

| Situacao | Recomendacao |
|---|---|
| 10+ pessoas precisam acessar dashboard com filtro proprio | Mantem Power BI/Looker (UI multi-user) |
| Auditoria SOX/ITGC exige fornecedor certificado | Mantem ferramenta enterprise |
| Volume gigante (50M+ linhas, query frequente) com latencia baixa | Avalia BigQuery/Snowflake — Claude vira camada de pergunta |

Pra 90% das PMEs, o trio **Modo 1 + Modo 2 + Modo 3 substitui completamente Power BI Pro** com ganho de velocidade e flexibilidade.
