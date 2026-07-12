# Exemplo Completo — PontoFiscal

> Vale 30 minutos do seu tempo ler isso antes de comecar. Esse e um exemplo ficticio mas realista de como o pacote inteiro se aplica. Quando voce voltar pros prompts, eles vao fazer mais sentido.

## Quem e o "criador"

**Andrea**, 34 anos, contadora ha 12 anos, sao paulo. Tem escritorio proprio com 2 funcionarias. Atende ~80 clientes PJ, sendo 60 SIMPLES NACIONAL e 20 LP.

**Skill tecnica:** baixa. Sabe usar Excel avancado e ferramentas de contador (Domínio, Onvio). Nunca programou. Ja conhece Claude.ai e usa pra escrever email pra clientes.

**Quanto tempo:** 8h/semana (2h por dia, antes do escritorio abrir).

## Dia 1-3 — Nicho + Validacao

Andrea roda `01-NICHO.md` no Claude.ai. Apos a entrevista, sai com 3 candidatos:

```
Nicho 1: contadores autonomos com 50-200 clientes PJ MEI/SIMPLES
Nicho 2: agencias de marketing pequenas (3-10 funcionarios) que precisam emitir muita NF-e por servico
Nicho 3: e-commerces faturando 10-50k/mes que precisam de conciliacao financeira
```

Andrea olha pra dentro: tem rede natural com nicho 1 (colegas contadores no grupo de WhatsApp da regional). Escolhe **nicho 1**.

**Persona:** Carlos, 38 anos, contador autonomo em Campinas, atende 120 clientes PJ MEI/SIMPLES, gasta 12-15h/mes preenchendo planilha de **DAS-MEI a vencer** + lembrando cliente. **Ja perdeu cliente** porque esqueceu de avisar 1 vencimento.

**A dor:** rastrear vencimento de DAS-MEI de 120 clientes, mandar lembrete, conferir pagamento, registrar.

**Quanto Carlos paga hoje:** R$ 0 em ferramenta, mas perde 12-15h/mes (=~R$ 600-900 do tempo dele).

**Quanto pagaria por uma ferramenta que automatiza?** Andrea precisa descobrir.

### Validacao em 7 dias

Andrea roda `02-VALIDACAO.md`. Sai com:

- Hipotese principal: "contadores autonomos com 50+ clientes MEI pagariam R$ 49-99/mes por uma ferramenta que automatiza lembrete de DAS-MEI e registra pagamento, economizando 10h/mes."
- Plano de 7 dias: 50 mensagens de LinkedIn + 12 conversas de 15 min
- Script de descoberta: 6 perguntas focadas em dor

**Resultado real:**
- 47 mensagens enviadas (contadores no grupo + LinkedIn)
- 18 responderam
- 11 conversas de 15 min agendadas e realizadas
- **8 disseram "se existisse, eu pagaria entre R$ 49 e R$ 79/mes"**
- 3 disseram "nao, ja tenho minha planilha"
- Andrea pediu pre-venda pros 8 — **5 transferiram R$ 49 cada** como sinal pra entrar na "Fase Beta" da ferramenta (devolveria se nao entregasse em 30 dias)

**Sinal verde:** R$ 245 ja na conta + 8 pessoas comprometidas.

## Dia 4-7 — MVP cortado

Andrea roda `03-MVP-MINIMO.md`. Saida:

**Promessa nuclear:** "Lembra automaticamente cada cliente seu de pagar o DAS-MEI no vencimento."

**MVP (tem que ter):**
1. Cadastro/login
2. Cadastrar clientes MEI (CNPJ, nome, telefone, email)
3. Configurar quando avisar (ex: 5 dias antes do vencimento, no dia, 2 dias depois se nao pagou)
4. Lembrete automatico via WhatsApp (Z-API) ou email
5. Marcar pagamento manualmente quando confirma
6. Pagamento pelo Stripe — R$ 49/mes pro contador

**Nao tem ainda:**
- Importacao em massa de clientes
- Integracao com Receita Federal pra puxar status
- Geracao automatica de DAS
- Multi-usuario (so 1 contador por conta)

**Nunca vai ter:**
- Calculo de imposto (e contador, ele ja sabe)
- Substituir Domínio/Onvio

**Modelo:** R$ 49/mes, primeiro mes gratis (mas com cartao cadastrado = pre-autorizado).

## Dia 8-9 — Arquitetura

Andrea roda `04-ARQUITETURA.md`. Saida:

```
Stack: Next.js + Supabase + Stripe + Resend + Z-API (WhatsApp)
Tabelas:
  - users (auth via Supabase, plano paid|free)
  - subscriptions (cache Stripe)
  - clientes_mei (do contador — multi-tenant via user_id)
  - lembretes (a cada vencimento, gera os lembretes agendados)
  - log_lembretes (registro do que foi enviado)

Estrutura de pastas: { padrao Next.js (marketing) (app) }
Variaveis de ambiente: 8 chaves
Ordem de construir: 12 etapas
Definicao de pronto: contador cadastra cliente, configura lembrete, recebe email no dia, paga R$ 49.
```

## Dia 10-11 — Landing

Andrea roda `05-LANDING.md`. Saida:

**Hero (titulo):** "Lembrete de DAS-MEI no automatico, pra todos os seus clientes."  
**Subtitulo:** "Voce cadastra. A gente lembra. Cliente paga. Voce nao perde mais cliente por esquecer."

**Codigo Next.js + Tailwind + shadcn:** Claude entrega 7 componentes (Hero, Dor, Solucao, Para quem e, Preco, FAQ, CTA) prontos.

Andrea publica no Vercel. Dominio: pontofiscal.com.br (R$ 40 de domain).

**Subiu mesmo sem produto pronto.** Os 8 leads recebem o link, comecam a compartilhar com colegas. Sobe lista de espera de mais 23 contadores.

## Dia 12-25 — Build

Andrea abre Claude Code. Roda `06-BUILD.md` em 3 partes (A = setup, B = auth + feature core, C = pagamento — esse e o `07-PAGAMENTO.md`).

**Andrea, contadora sem experiencia tecnica, conseguiu fazer porque:**

- Claude Code criou TODOS os arquivos
- Ela seguiu 1 etapa por dia (2h/dia)
- Quando travou em algo (configurar webhook do Stripe, criar tabela do Supabase), ela perguntou pro Claude e ele explicou em portugues simples
- Toda etapa que terminava: `git commit` (Claude Code sugeria a mensagem)

Linha do tempo dia a dia:

| Dia | O que fez | Tempo |
|---|---|---|
| 12 | Criou conta Supabase + projeto + tabelas (com SQL pronto do Claude) | 1h |
| 13 | Criou conta Stripe + produto + preco | 1h |
| 14 | Setup Next.js + variaveis de ambiente + Supabase client | 2h |
| 15 | Auth (signup/login/logout) | 2h |
| 16 | Layout area logada + bloqueio de feature | 1h |
| 17-18 | Cadastro de clientes MEI + listagem | 4h |
| 19 | Configuracao de lembrete (5d antes, no dia, etc.) | 2h |
| 20 | Cron de envio de lembretes (Vercel cron) | 2h |
| 21 | Integracao Z-API pra mandar WhatsApp | 2h |
| 22 | Stripe checkout (`07-PAGAMENTO.md`) | 2h |
| 23 | Webhook do Stripe + atualizacao de plan | 2h |
| 24 | Customer Portal + pagina /billing | 1h |
| 25 | Smoke test fim a fim com cartao de teste | 2h |

**Total: ~24 horas em 14 dias.** Custo: R$ 0 alem do que ja paga (Claude Pro).

## Dia 26 — Primeiro cliente real

Andrea abre o Stripe em modo producao. Manda mensagem pros 5 que ja pagaram R$ 49 sinal:

> "Oi pessoal! Pontofiscal ta pronto pra voces testarem. Mandando email com cadastro agora. R$ 49 que voces pagaram entram como credito do mes 1. Qualquer travada, me avisa direto."

5 contadores cadastram. **3 importam clientes (manual mesmo) e configuram lembretes nos primeiros 2 dias.** 1 desiste no meio (nao tinha tempo). 1 promete fazer no fim de semana.

No dia 28, **primeiro DAS-MEI lembrado automaticamente:** sistema mandou WhatsApp pra cliente do Carlos avisando "DAS-MEI vence em 5 dias". Cliente pagou. Carlos viu no painel "pago" e ficou impressionado.

No dia 30, mais 4 contadores da lista de espera entram. Total: 9 clientes.

**MRR mes 1: R$ 9 x R$ 49 = R$ 441.**

## Dia 31-60 — Lancamento + feedback

Andrea roda `08-LANCAMENTO.md` mais formalmente. Saida:

- 2 posts no LinkedIn (1 sobre a dor, 1 sobre o lancamento)
- Mensagem pra 5 grupos de WhatsApp da regional (com cuidado pra nao fazer spam)
- Indicacoes dos 9 primeiros clientes — 5 indicaram colegas
- 1 post no Instagram (pequeno publico mas ela tem)
- Anuncio LinkedIn R$ 200 — segmentado por "contador" + "cidade SP/Campinas"

Em 30 dias adicionais: **+22 clientes**. Total: 31. MRR: R$ 1.519.

Roda `09-FEEDBACK.md`. Cadencia de contato com cada um:

- Dia 0 cadastro: mensagem boas vindas + 1 pergunta ("Quantos clientes MEI voce vai cadastrar?")
- Dia 3: "Ja conseguiu cadastrar? Travou em algo?"
- Dia 14: "Como ta sendo? O que voce mudaria?"
- Dia 30: pergunta-mae ("Como voce se sentiria se nao pudesse mais usar o PontoFiscal?")

**Resultados depois de 60 dias:**

- Pergunta-mae: 12 de 28 respondentes = "muito decepcionado" = **43% — sinal forte de PMF**
- Dores recorrentes (3+):
  1. "Cliente quer comprovante consolidado mensal" → entra em V2
  2. "Importar planilha em massa" → entra em V2
  3. "Marcar 'pago' sem precisar entrar no painel — via mensagem que mandei pro cliente" → entra em V2
- Churn: 2 cancelaram (1 caiu de produto pra "vou usar planilha mesmo", 1 cliente fechou o escritorio)

Churn rate: 2/31 = **6,5%** no mes 2. Aceitavel pra mes 2.

## Dia 61-90 — V2 + escala

Andrea constroi V2 com as 3 features priorizadas. Ainda 2h/dia, agora com mais experiencia: **9 dias de build**.

Lanca V2 pros clientes existentes + posta sobre. **+18 novos clientes em 30 dias** (orgaicos + indicacoes).

**MRR dia 90: R$ 47 x R$ 49 = R$ 2.303.**

## Dia 91 — Decisao de escala

Andrea roda `10-ESCALA.md`. Numeros:

- Tempo desde lancamento: 90 dias
- Total pagantes ja conquistados: 53
- Pagantes ATIVOS: 47
- Churn em 90 dias: 6 (11% acumulado, mensal medio ~3.5%)
- MRR atual: R$ 2.303
- Crescimento mes/mes ultimos 2: +30% (mes2) e +52% (mes3)
- CAC medio: R$ 25 (low — porque indicacao + LinkedIn organico)
- LTV estimado: R$ 49 x ~24 meses (estimativa baseada em churn) = R$ 1.176
- LTV/CAC: 47x — excepcional

Sean Ellis: 43%

**Diagnostico:** PMF consolidado, churn baixo, crescimento forte, LTV/CAC alto.

**Recomendacao Claude:** ESCALAR.

**Plano 90 dias:**
- Aumentar marketing digital (R$ 800/mes em LinkedIn + Meta)
- Lancar plano "Pro" com mais features pra contar com 200+ clientes (R$ 99/mes)
- Construir o que apareceu em 3+ feedback novos
- Contratar 1 atendente part-time pra suporte (10h/sem, R$ 1.500/mes)

## 6 meses depois

Andrea: ~140 clientes pagantes, MRR R$ 7.500. Decide deixar o escritorio em modo "manutencao" (vende metade da carteira pro colega) e foca 30h/sem no PontoFiscal. 

Ano 1: R$ 100k+ recebido. Margem (apos custos): R$ 70k.

**Caixa rapido cumprido.**

## O que aconteceu na sequencia

(opcional, e ilustrativo)

Andrea nao virou unicornio. Em 18 meses chegou em R$ 25k MRR e estabilizou. Bom dinheiro, baixa pressao. Ela contratou 1 dev part-time pra cuidar das features. Ela ainda contadora "principal" do produto — o que e o diferencial enorme em relacao a uma equipe de tech criando ferramenta de contador sem entender o nicho.

## O que voce aprende com isso

1. **Persona ESPECIFICA** vence "publico geral"
2. **Validacao com pre-venda real** vence "achei legal"
3. **MVP cortado ao osso** vence "queria mais features"
4. **Cobrar desde o primeiro dia** vence trial gratuito longo
5. **Indicacao depois do PMF** vence anuncio antes do PMF
6. **Decisao baseada em numeros** (Sean Ellis, churn, LTV/CAC) vence achismo

## Voce nao e a Andrea

Seu caso vai ser diferente. Nicho diferente, dor diferente, ritmo diferente. Mas a **estrutura** e a mesma:

```
Nicho ESPECIFICO → Validacao com R$ na mao → MVP cortado → Build em 14d → Pagamento dia 1 → Lancamento focado → Feedback estruturado → Decisao numerica
```

**Nao pula etapa.** Ate quem tem certeza em "ja sei o nicho" descobre na validacao que o nicho era outro.

Voce tem agora uma cabeca diferente. Vai pro `01-NICHO.md`.
