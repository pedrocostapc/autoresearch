# 00 — Leia primeiro

Esse pacote e simples na premissa: **pegar uma dor especifica de um nicho que paga, resolver com SaaS pequeno, cobrar mensalidade.**

Nao e teoria. Nao e visao de longo prazo. E *caixa rapido*. O nome e literal.

## Por que B2B de nicho ate R$ 100k MRR

Esse pacote nao serve pra:

- "Vou criar um SaaS pra todo mundo" (todo mundo = ninguem)
- "Quero ser o proximo Notion" (top de mercado leva 5-10 anos)
- "Vou ganhar dinheiro com app gratis monetizado depois" (sem caixa nao da)

Esse pacote serve pra:

- **B2B**: empresa pagando empresa
- **Nicho especifico**: "contadores que atendem PJs com faturamento ate 360k/ano" e nicho. "Empresas em geral" nao e
- **Ate R$ 100k MRR**: voce cresce ate ai sem precisar de funding, time grande nem complexidade alta. Acima disso, vira outro jogo

R$ 100k MRR = R$ 1.2M/ano. Pra empresario solo ou duo, **e muito dinheiro**.

## A regra das 3 perguntas (de novo, vale repetir)

Antes de mexer em qualquer coisa, voce precisa responder:

### 1. Quem paga?

**Errado:**
- "PMEs"
- "Gestores"  
- "Pequenas empresas"

**Certo:**
- "Contadores autonomos no Brasil que atendem entre 50 e 200 PJs MEI/SIMPLES"
- "Donos de pet shop com 1 a 3 lojas fisicas em capitais"
- "Agencias de marketing digital com 5 a 15 funcionarios faturando R$ 50-200k/mes"

A diferenca: voce consegue **fechar os olhos e visualizar essa pessoa**. Sabe a idade, o stress, a rotina, a ferramenta que ela usa hoje.

### 2. Quanto paga?

Voce precisa saber quanto esse perfil **ja gasta hoje** pra resolver essa dor:

- Em ferramenta SaaS (X reais/mes)
- Em mao de obra (Y horas/mes x salario)
- Em tempo proprio (Z horas/mes — perdas indiretas)

A dor que voce resolve precisa ja estar custando R$ 200-2.000/mes pra essa pessoa. Senao, dificil convencer ela a pagar voce.

### 3. Como achar 100 delas em 30 dias?

Voce precisa de um canal **especifico** que entrega 100 leads desse perfil em 30 dias. Exemplos:

- LinkedIn: search por cargo + tamanho de empresa + cidade
- Grupo de WhatsApp: voce ja esta em algum?
- Instagram: hashtags de nicho?
- Lista pronta: associacao do setor, evento, publicacao especializada
- Indicacao: voce ja conhece 5-10 dessas pessoas pessoalmente?

Se a resposta e "nao sei como achar", **o nicho nao serve**. Achar mil leads de "todo mundo" e facil — nao serve. Achar 100 leads do nicho certo e dificil — serve.

## A ordem importa

```
NICHO → VALIDACAO → MVP → ARQUITETURA → LANDING → BUILD → PAGAMENTO → LANCAMENTO → FEEDBACK → ESCALA
```

Cada etapa **so pode comecar se a anterior deu sinal verde**. 

| Etapa | Sinal verde pra seguir |
|---|---|
| 01 → 02 | Voce respondeu as 3 perguntas com especificidade |
| 02 → 03 | 5+ pessoas disseram "se voce me entregar isso, eu pago R$ X/mes" |
| 03 → 04 | MVP cabe em 14 dias de codificacao |
| 04 → 05 | Stack definida e voce sabe rodar |
| 05 → 06 | Landing publicada (mesmo sem produto) |
| 06 → 07 | Auth e feature core funcionando local |
| 07 → 08 | Voce consegue pagar com cartao de teste e o plano vira "pago" |
| 08 → 09 | Pelo menos 1 cliente pagante de verdade |
| 09 → 10 | 30+ dias com 5+ clientes ativos rodando |

**Pulou etapa? Vai dar errado.** Erro mais comum: pular validacao porque "ja sei que vai dar certo". 90% dos casos: nao da.

## Mentalidade

### Cobrar e validar

Cliente que cadastrou gratis valida nada. Cliente que **pagou** R$ 1 ja valida MUITO mais. Sempre cobra desde o primeiro dia. Mesmo simbolicamente.

### 80% feito enviado >> 100% feito guardado

Voce vai ter vontade de "deixar mais bonito antes de mostrar". Resista. O que da mais retorno e ouvir o cliente reclamando do feio. Cliente que paga olha pra dor que voce resolve, nao pra UI piscante.

### O proximo SaaS voce faz mais rapido

Esse primeiro vai demorar. O segundo, metade do tempo. O terceiro, um terco. Caixa rapido e musculo, nao loteria.

### Construa pelo padrao, nao pelo loud user

Nos primeiros meses, voce vai ouvir 5 pedidos diferentes de 5 clientes. Resista a construir tudo. **So entra no roadmap o que aparece em 3+ conversas independentes** OU **o que esta gerando churn**. O resto: anota e congela.

### Cobre o que vale, nao o que voce produz

Cliente paga pelo **resultado**, nao pelas horas que voce gastou. Se voce gastou 200h pra fazer e ele economiza 5h/semana com o produto, voce cobra pelo valor das 5h dele, nao pelas 200h suas.

## Custos reais

### Antes do primeiro cliente
- Hosting (Vercel free): R$ 0
- Banco (Supabase free): R$ 0
- Email (Resend free 3k): R$ 0
- Stripe: R$ 0 (so cobra com transacao)
- Dominio: R$ 40/ano
- Claude (pra construir): R$ 110/mes (Pro)

**Total: R$ 110/mes ate ter cliente.**

### Apos 10 clientes pagando ~R$ 100/mes (R$ 1k MRR)
- Vercel Pro (se trafego justifica): R$ 110/mes
- Supabase Pro: R$ 130/mes
- Stripe taxa: ~3.99% + R$ 0,39 por transacao (R$ 40)
- Claude: R$ 110-300/mes (com cliente vem mais uso)
- Email Resend: ainda gratis ou R$ 110/mes
- Dominio + outros: R$ 50/mes

**Total: R$ 500-700/mes**. Margem com R$ 1k MRR: 30-50%. Voce ja paga as ferramentas.

### Apos 50 clientes pagando ~R$ 100/mes (R$ 5k MRR)
- Custos sobem ~R$ 1k-1.5k/mes
- Margem: 70-80%

**Apos R$ 5k MRR, voce comeca a ganhar dinheiro de verdade.** Antes disso, e investimento.

## Quanto tempo vai demorar pra primeira receita?

**Modo agressivo (full-time):**
- Dia 1-3: nicho + validacao
- Dia 4-7: MVP cortado + arquitetura
- Dia 8-21: build + pagamento
- Dia 22-28: lancamento
- Primeiro pagamento: dia 25-30

**Modo realista (com trabalho de dia):**
- 30-45 dias

**Modo lento:**
- 60-90 dias

## Sinais de alarme (quando voce esta indo errado)

| Sinal | O que significa |
|---|---|
| 7+ dias na mesma etapa sem sair | Pulou alguma decisao — volta uma etapa |
| Voce esta "ainda decidindo o nicho" depois de 5 dias | Voce nao tem nicho — relaxa, conversa com gente |
| Build esta com 3 semanas e nada funciona | MVP nao foi cortado o suficiente — corta mais |
| Validacao "todo mundo achou legal" mas ninguem comprometeu R$ | Pediu opiniao em vez de pre-venda |
| Voce nao consegue explicar em 1 frase o que o produto faz | MVP esta bagunca — refoca |
| Voce esta "esperando ficar pronto pra divulgar" | Sintoma classico de paralisia — divulga ja |

## Antes de seguir

1. Le `EXEMPLO-COMPLETO.md` agora. **Vale 30 minutos do seu tempo.** Voce vai ver um SaaS ficticio sendo construido inteiro. Os prompts vao fazer mais sentido depois.
2. Decide modo (agressivo / realista / lento)
3. Marca uma data limite no calendario pro primeiro pagamento

Vai pro `01-NICHO.md`.
