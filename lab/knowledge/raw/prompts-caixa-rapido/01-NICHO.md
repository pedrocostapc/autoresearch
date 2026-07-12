# 01 — Nicho

Sair de "tenho uma ideia" pra "esse e meu nicho, esse e o pagador, essa e a dor".

## Antes de rodar

Voce ja leu `00-LEIA-PRIMEIRO.md` e `EXEMPLO-COMPLETO.md`? Se nao, volta. Vai economizar tempo.

## O que voce sai com esse prompt

Um arquivo `nicho.md` na pasta do seu projeto com:

- 3 nichos avaliados objetivamente
- 1 escolhido com persona detalhada
- O canal especifico pra encontrar 100 leads em 30 dias
- A dor central + quanto a pessoa ja gasta resolvendo

---

--- COMECO DO PROMPT ---

Voce e um consultor de produto com 15 anos avaliando ideias de SaaS para empresarios brasileiros. Sua missao agora: me ajudar a achar 3 nichos lucrativos para um SaaS B2B que eu vou lancar nos proximos 30-90 dias.

# Contexto sobre mim

- O que eu faco hoje (negocio principal): {DESCREVA EM 3-5 LINHAS — ex: "Sou contadora ha 12 anos com escritorio em SP, 80 clientes PJ"}

- O que eu domino tecnicamente E profissionalmente (3-5 coisas):
  1. {ex: "Conhecimento profundo de SIMPLES NACIONAL e MEI"}
  2. {ex: "Operacao de escritorio contabil pequeno"}
  3. {ex: "Excel avancado, ferramentas de contador"}
  4. ...

- Acesso/redes que eu tenho (canais privilegiados pra encontrar publico):
  - {ex: "Conheco 30+ contadores no grupo regional"}
  - {ex: "Estou na ABRACOM (associacao)"}
  - {ex: "Tenho conta de LinkedIn ativa no nicho"}

- Tempo disponivel por semana pra esse projeto: {Xh}
  - 5-8h: modo lento
  - 10-15h: modo realista
  - 20+h: modo agressivo

- Capital inicial disponivel: R$ {X}
  - 0-1k: depende de tudo organico
  - 1-5k: pode pagar dominio + 1 mes de anuncio
  - 5k+: mais flexibilidade

- Ja tentei criar SaaS antes? Se sim, o que aprendi: {ex: "Sim, tentei um app de tarefas, parei porque mercado saturado"}

# Restricoes inegociaveis

- B2B (empresa pagando empresa)
- Ticket mensal entre R$ 49 e R$ 499 (caixa rapido — fora dessa faixa, e outro jogo)
- Nicho onde eu consiga 100 leads especificos em 30 dias
- NAO horizontal (Notion-like, CRM generico, planilha-killer-pra-todo-mundo)
- NAO nicho saturado por gigante (gestao de tarefas geral, financas pessoais, dieta)

# Como voce trabalha

## Etapa 1 — Entrevista profunda

Faca 5-7 perguntas pra entender minha vantagem injusta. Pergunte uma de cada vez OU em 2-3 blocos. Espere minha resposta antes de seguir. Foque em:

- Onde eu ja sei sentir a dor de outros (porque eu tambem sinto, ou porque atendo gente que sente)
- Que conexao eu tenho que terceiros nao tem
- Que tipo de cliente ja me liga/escreve com a mesma duvida
- Que ferramenta caraca o pessoal do meu setor usa que ninguem gosta

## Etapa 2 — 3 nichos candidatos

Apos as respostas, me entregue 3 nichos. Pra CADA UM:

```
## Nicho {N}: {NOME ESPECIFICO}

**Quem paga:** {PERSONA — nao "PMEs". Algo como: "Contadora autonoma de 30-50 anos atendendo entre 50 e 200 clientes PJ MEI/SIMPLES, com 1-3 funcionarios"}

**Dor central (1 frase, na voz da persona):** {ex: "Eu perdi cliente porque esqueci de avisar que o DAS-MEI vencia"}

**Como ele resolve hoje:** {ferramenta SaaS X / planilha Y / mao-de-obra / cabeca}

**Quanto ja gasta hoje (R$/mes):** {ex: "0 em ferramenta, mas perde 12-15h/mes que valem R$ 600-900 do tempo dele"}

**Disposicao a pagar (estimativa):** {ex: "R$ 49-99/mes em ferramenta que automatiza isso"}

**Onde achar 100 deles em 30 dias:**
- Canal 1: {ex: "LinkedIn — search 'contador autonomo' SP/SP, ~5k resultados"}
- Canal 2: {ex: "Grupos de WhatsApp regionais (5-10 grupos com ~100 membros cada)"}
- Canal 3: {ex: "ABRACOM tem ~3000 associados"}

**Por que VOCE tem vantagem aqui (linka com meu contexto):** {ex: "Voce ja e contadora com rede, ja vive a dor, conhece a linguagem. Concorrente generico nao consegue copiar isso"}

**Risco principal:** {o que pode dar errado — ex: "Federal pode lancar app gratuito que faz isso (mas ate hoje nao fez)"}

**Score 1-10 (com justificativa de 1 linha):** {nota}
```

## Etapa 3 — Recomendacao final

Recomende **UM** dos 3, com justificativa de 5-8 linhas. Honestamente. Considere:

- Onde voce tem mais vantagem injusta (acesso + conhecimento)
- Onde a dor e mais concreta e urgente (vs. "seria bom ter")
- Onde o canal de aquisicao e mais barato e direto

Se nenhum dos 3 te convencer **com base nas minhas respostas**, fale. Melhor refazer do que comecar errado.

## Etapa 4 — Salvar o nicho.md

Apos eu confirmar a escolha, gere um arquivo `nicho.md` em formato pronto pra eu salvar com:

```markdown
# Nicho: {nome}

## Persona pagante
{detalhamento}

## Dor central
{frase + contexto}

## Solucao proposta (em 1 frase)
{frase}

## Canais de aquisicao
{lista de 3 canais especificos com numero estimado de leads acessiveis}

## Concorrentes diretos (se existirem)
{busca rapida — quem ja faz parecido?}

## Vantagem injusta minha
{por que eu vou conseguir mais que outro}

## Hipoteses a validar no proximo passo
1. {ex: "Persona X paga R$ 49-99/mes por uma ferramenta que automatiza Y"}
2. {ex: "Achar 100 dessas pessoas no LinkedIn em 30 dias e factivel"}
3. {ex: "A dor e suficientemente forte pra ela trocar de planilha"}
```

Comece pela Etapa 1.

--- FIM DO PROMPT ---

---

## Sinal verde pra ir pro `02-VALIDACAO.md`

Voce so segue se respondeu **com especificidade** as 3 perguntas do `00-LEIA-PRIMEIRO.md`:

- [ ] Quem paga: persona com nome, idade, contexto, frase tipica
- [ ] Quanto paga: numero estimado em R$ baseado em ferramenta/tempo gasto hoje
- [ ] Como achar 100: pelo menos 3 canais especificos com numero de leads acessiveis

Se faltou clareza em alguma: **volta a Etapa 1** e refaz. Esse arquivo `nicho.md` vai ser cabecalho de todos os outros — ele tem que estar limpo.

## Erros comuns nessa etapa

| Erro | Como evita |
|---|---|
| Nicho generico ("PMEs") | Cobre persona ate ela ter nome ficticio |
| Vantagem injusta inventada | Passa pela peneira: voce tem cliente desse nicho hoje? rede? |
| Canal "vou criar audiencia" | Demora demais. Use canal frio que voce ja tem acesso |
| Comparar com unicornio ("vou ser o Notion da contabilidade") | Foca caixa rapido, nao concorrencia |
| Escolher 3 nichos parecidos | Forca diversidade — 1 deve ser "fora da caixa" |

## Antes de seguir

Gravou `nicho.md` no Git? Faz commit. E vai pro `02-VALIDACAO.md`.

```bash
git add nicho.md
git commit -m "nicho escolhido: {nome curto}"
```
