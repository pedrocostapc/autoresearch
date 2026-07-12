# 10 — Escala (ou matar o produto)

Decidir baseado em numero, nao em ego.

## A premissa dura

Apos 60-90 dias rodando seu SaaS, voce tem **dado**. Nao "achismo", nao "feeling". Numero.

Esse passo te forca a olhar pros numeros frios e tomar UMA das 3 decisoes:

1. **ESCALAR** — produto funciona, hora de pisar fundo
2. **PIVOTAR** — algo bom mas precisa ajuste
3. **MATAR/CONGELAR** — aprende, fecha com elegancia, parte pro proximo

A 3 e a mais dificil emocionalmente, e geralmente a mais inteligente economicamente quando os numeros nao batem. Empresario que nao mata produto perdedor fica preso.

## Pre-requisitos

Voce so chega aqui se:

- 60-90 dias desde o lancamento
- Pelo menos 5 clientes pagantes ja conquistados
- 60+ dias com pelo menos 1 desses clientes ativos (sinal de retencao basica)
- Sistema de feedback rodando (`09-FEEDBACK.md`)
- Voce tem dado, nao impressao

Se voce nao tem isso, **nao esta na hora de escalar**. Volta pro prompt 09 e roda mais um ciclo.

## O que voce sai com esse prompt

- Diagnostico baseado em metricas
- 1 das 3 recomendacoes (escalar / pivotar / matar)
- Plano de 90 dias detalhado
- Lista do que NAO fazer
- Decisao de proxima feature de maior impacto

---

--- COMECO DO PROMPT ---

Voce e um operador de SaaS B2B com pratica em decidir entre escalar, pivotar ou matar produto. Sua missao: olhar honestamente os numeros do meu SaaS e me dar UMA recomendacao sem suavizar.

# Contexto numerico

Preencha **com numeros reais**, nao "razoavelmente alto":

## Volume e tempo

- Tempo desde o lancamento: **{N dias}**
- Total de pagantes ja conquistados (alguma vez pagou): **{N}**
- Pagantes ATIVOS hoje: **{N}**
- Pagantes que cancelaram apos virar cliente: **{N} ({X}% acumulado)**

## Receita

- MRR atual (mensalidade dos ativos somada): **R$ {X}**
- MRR final do mes 1: R$ {X}
- MRR final do mes 2: R$ {X}
- MRR final do mes 3: R$ {X}
- Crescimento mes/mes (medio dos ultimos 2): **{X%}**

## Saude (churn e retencao)

- Churn mensal medio: **{X%}**
- Tempo medio de vida ate agora (meses ou estimado): **{N}**
- Pelo menos 1 cliente ja completou 60 dias?: {sim/nao}
- Pelo menos 1 cliente ja completou 90 dias?: {sim/nao}

## Aquisicao

- CAC medio (custo total marketing + tempo / clientes): **R$ {X}**
- Top canal de aquisicao: {indicacao / linkedin organico / linkedin ads / outro}
- Distribuicao por canal (%): {ex: indicacao 40, linkedin 30, organico 20, anuncio 10}

## LTV

- Ticket medio: R$ {X}/mes
- LTV estimado (ticket * 1/churn_mensal): R$ {X}
- LTV/CAC: **{X}** (saudavel acima de 3, otimo acima de 5)

## Sean Ellis test (do prompt 09)

- % "muito decepcionado": **{X%}** (40%+ = PMF)
- Quantos respondentes: {N de quantos enviados}

## Feedback

- Top 3 elogios recorrentes: {de feedback.md}
- Top 3 dores recorrentes: {de feedback.md}
- Top 3 features pedidas: {de feedback.md}

## Sustentabilidade pessoal

- Tempo que voce consegue manter sem receita extra: **{N meses}** (financeiro pessoal)
- Como esta seu animo: {motivado / cansado / em duvida — honesto}

# O que voce me entrega

## 1. Diagnostico (5-8 linhas)

Sua leitura honesta dos numeros. Sem chavoes, sem motivacao barata. So o que os dados dizem.

## 2. Recomendacao — escolha UMA

### A) ESCALAR

Criterios pra recomendacao:
- Sean Ellis 40%+
- Churn mensal < 5%
- LTV/CAC > 3
- Crescimento m/m positivo nos ultimos 2 meses
- MRR > R$ 2k pra justificar foco

Justificativa em 3-5 linhas.

**Plano: o que fazer nos proximos 90 dias pra 3x o MRR.**
- Investimento prioritario: {marketing / produto / time}
- Canais a escalar: {especifico}
- Features prioritarias (do feedback): {top 3}
- O que NAO mexer (nao quebra o que funciona)

### B) PIVOTAR

Criterios:
- Tem clientes pagando MAS:
  - Churn alto (> 8%) OU
  - Sean Ellis 20-40% (dor existe mas oferta errada) OU
  - Crescimento estagnado apesar de marketing

Justificativa.

**Plano: o que mexer.**
- Posicionamento (publico-alvo, copy, preco)?
- Produto (foco diferente do mesmo nicho)?
- Canal (target diferente)?
- Modelo (preco, plano, freemium)?

**Prazo pra esse pivot:** 30-60 dias antes de re-decidir.

### C) MATAR / CONGELAR

Criterios:
- Apos 60-90 dias:
  - MRR estagnado em valor que nao paga seu tempo (ex: < R$ 1.5k com 15h/sem investido)
  - Sean Ellis < 20% (dor errada ou produto errado)
  - Churn alto (10%+)
  - Voce ja gastou animo demais
  - Capital pessoal acabando

Justificativa em 3-5 linhas (e mais valioso ser honesto aqui do que gentil).

**Plano: como descontinuar com elegancia.**
- Avisar clientes: prazo de N dias
- Devolver pro-rata se aplicavel
- Manter no ar mais N dias pra exportar dados
- Recomendar concorrente pros clientes
- Comunicacao publica (post de aprendizado)
- Backup de codigo + dados

**O que voce APRENDEU pro proximo SaaS** — em 5-10 linhas estruturadas:
- Sobre o nicho
- Sobre customer development
- Sobre execucao (ritmo, foco, decisoes)
- Sobre voce mesmo
- Erros pra nao repetir

## 3. Plano de 90 dias detalhado (do que voce recomendou)

| Semana | Foco | Atividade | Saida concreta | Metrica |
|---|---|---|---|---|

12-13 semanas. Cada uma com objetivo claro.

## 4. O que NAO fazer

3-5 armadilhas comuns nessa fase, **especificas pro caso**:

Exemplos genericos:
- Comecar a construir as features pedidas pelos loud users (nao representativos)
- Subir preco antes de provar que escalas
- Tentar adicionar segundo nicho antes de dominar o primeiro
- Contratar antes de ter receita pra justificar
- Postergar decisao de matar — vira drama financeiro

## 5. Decisao de proxima feature

Se ESCALAR ou PIVOTAR: qual a proxima feature de maior impacto?

Criterios de priorizacao:
- (a) Apareceu em 3+ feedbacks recorrentes
- (b) Impacta retencao (reduz churn)
- (c) Impacta aquisicao (atrai mais clientes)
- (d) E facil de implementar (1-3 dias)

Lista as features candidatas, pontua cada uma de 1-5 nos criterios, recomenda UMA.

Comece pelo diagnostico.

--- FIM DO PROMPT ---

---

## Heuristicas honestas

| Sinal | O que indica |
|---|---|
| MRR > R$ 5k/mes em 90 dias | Forte sinal — escala |
| MRR < R$ 1k/mes em 90 dias com 15h+/sem investido | Mata ou pivota — nao paga seu tempo |
| Sean Ellis 40%+ | Tem PMF — escala |
| Sean Ellis 20-39% | Dor existe mas oferta errada — pivota |
| Sean Ellis < 20% | Dor errada — mata ou volta pro nicho 1 |
| Churn > 10%/mes | Produto nao retem — NAO ESCALE ate consertar |
| Churn 5-10%/mes | Risco — investiga primeiro |
| Churn < 5%/mes | Excelente — sinal de retencao real |
| LTV/CAC < 3 | Nao tem sentido investir em aquisicao paga ainda |
| LTV/CAC 3-5 | Saudavel — pode escalar com cuidado |
| LTV/CAC > 5 | Otimo — escala com confianca |
| Receita ja paga seu tempo (vs trabalho atual) | Pode focar mais |
| Voce em duvida apos 90 dias com numeros bons | Provavel: produto OK, voce cansado — pausa, ferias, depois decide |

## Como matar bem (pra quem chegar na opcao C)

1. **Voce nao esta falhando — esta aprendendo.** O proximo SaaS sera muito mais rapido por causa desse.

2. **Avisa clientes com 30 dias de antecedencia** — minimo. Devolve pro-rata se eles pagaram em ciclo recente.

3. **Posta publicamente o aprendizado** — costuma virar a melhor pessa de marketing pessoal que voce ja produziu. Formato:
   ```
   Lancei {produto}. Apos 90 dias, decidi descontinuar.
   
   Numeros:
   - {N} clientes
   - R$ {X} MRR
   - Churn {X}%
   
   O que aprendi:
   - {3-5 aprendizados especificos, honestos}
   
   Proximo passo: {o que voce vai fazer agora — outro SaaS? voltar pro negocio? ferias?}
   ```

4. **Mantem o produto no ar mais 30-60 dias em modo "manutencao"** — clientes podem exportar dados.

5. **Recomenda concorrente** — facil ter raiva, mas seu cliente importa mais que seu ego.

6. **Faz backup completo** — codigo, dados (anonimizado), conversas de cliente. Pode ser util no futuro.

## A parte que ninguem fala sobre escalar

Escalar SaaS B2B de nicho NAO e fazer 100x. E fazer 3x cada 6 meses por 3-5 anos. SaaS chato e bonito = R$ 50k MRR em 18-24 meses sustentavel.

Se voce ja tem PMF e churn baixo:

- **Mes 4-6**: dobra MRR (R$ 5k → R$ 10k) com indicacao + canal organico que ja funciona
- **Mes 7-12**: dobra de novo (R$ 10k → R$ 20k+) introduzindo plano upsell + parcerias
- **Mes 13-18**: terceira dobrada com time de 2-3 pessoas

Sem foguete, sem unicornio, sem investidor. **R$ 200k+ MRR em 18 meses na sua mao.**

## Antes de fechar

Salve sua decisao em `decisao-d{N}-{escalar|pivotar|matar}.md`.

```bash
git add decisao-d90-{...}.md
git commit -m "decisao apos 90 dias: {escalar|pivotar|matar}"
```

Voce chegou ao fim dos 10 prompts. **Honestamente:** apenas 30% das pessoas que comecam um SaaS chegam ate aqui. Voce ja esta na frente.

Boa sorte. E o proximo voce faz em metade do tempo.
