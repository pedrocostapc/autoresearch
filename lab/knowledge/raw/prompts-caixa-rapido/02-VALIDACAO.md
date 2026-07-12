# 02 — Validacao

Antes de escrever uma linha de codigo, descobrir se 5 pessoas pagariam.

> Esse e o passo onde 80% das pessoas pulam e perdem 30 dias construindo MVP que ninguem queria. Nao pula.

## A diferenca entre "achei legal" e "validacao real"

| Achei legal | Validacao real |
|---|---|
| "Ah, faria sentido" | "Quanto custa? Como contrato?" |
| "Manda quando estiver pronto" | "Posso ja entrar pra fila? Te dou R$ X agora como sinal" |
| "Tenho um amigo que precisaria" | "Eu uso isso assim que tiver" |
| Resposta cordial | Pergunta de quem ja decidiu |

**So a 2ª coluna conta.** A 1ª e ruido educado.

## O que voce sai com esse prompt

`validacao.md` com:
- 4 hipoteses a validar
- Plano de 7 dias com atividades dia-a-dia
- Script de descoberta (15 min)
- Mensagem de prospec pra LinkedIn/email
- Criterios objetivos pra "validado" ou "nao validado"
- Sinais de morte que aparecem nas conversas

E ao fim dos 7 dias: 3-5 pessoas com R$ na sua conta como sinal.

---

--- COMECO DO PROMPT ---

Voce e um especialista em customer development e validacao de ideias B2B. Sua missao: montar um plano de validacao de **7 dias** pra eu validar (ou matar) o nicho que escolhi.

# Contexto

Cole o conteudo completo de `nicho.md`:

<nicho>
{COLE AQUI}
</nicho>

# Restricoes

- 7 dias corridos
- Maximo 2-3h/dia
- Objetivo: pelo menos **3 pessoas** dizendo "se voce me entregar isso, eu pago R$ X/mes" + idealmente 2 transferindo R$ como sinal de pre-venda
- Eu prefiro NAO sair do whatsapp/linkedin/email — sem evento presencial

# O que voce me entrega

## 1. Hipoteses a validar (no maximo 4)

Formato:

> "Acreditamos que **{persona}** sente **{dor}**, paga R$ **{valor}** hoje em **{solucao}** (ferramenta/tempo/mao-de-obra), e pagaria R$ **{valor}** por uma ferramenta que **{beneficio especifico}**."

Marque a hipotese **MAIS CRITICA** — aquela que se for falsa, mata o produto. Essa e a primeira a testar.

## 2. Plano dia-a-dia

| Dia | Atividade | Tempo | Saida concreta |
|-----|-----------|-------|----------------|

Estrutura sugerida (adapte ao caso):

```
Dia 1: Listar 50-80 leads especificos (LinkedIn search + grupos + lista)
Dia 2: Mensagem de abordagem pros 50 — meta de 10-15 respostas
Dia 3: Marcar 8-12 conversas pros dias 4-6
Dia 4: 4 conversas de descoberta (15min cada)
Dia 5: 4 conversas + ajuste de pitch
Dia 6: 4 conversas + comecar pre-venda com os mais quentes
Dia 7: Decisao final — segue OU pivota OU mata
```

Pra cada dia, objetivos quantitativos. Nao "fazer prospec" — "ate sexta, ter 12 conversas marcadas".

## 3. Script de descoberta (15 min — pra cada conversa)

Texto pronto pra usar. Estrutura:

```
[ABERTURA — 30s]
"Oi {nome}, obrigada por aceitar. Vou ser objetiva: estou pesquisando se faz sentido criar uma ferramenta pra {dor}. Posso te fazer 5 perguntas em 15 minutos pra entender se isso e dor pra voce tambem? Sem pitch nenhum, prometo."

[PERGUNTAS DE DOR — 8min]
1. {ex: "Como voce faz hoje pra {tarefa}?"}
2. {ex: "Quanto tempo isso te toma por mes?"}
3. {ex: "Ja te custou alguma coisa fazer errado/esquecer?"}
4. {ex: "Voce ja tentou alguma ferramenta? Por que parou?"}
5. {ex: "Se isso fosse magicamente resolvido amanha, o que voce faria com esse tempo?"}

[PERGUNTA DE DISPOSICAO — 3min]
6. "Se existisse uma ferramenta que {solucao especifica}, voce pagaria? Quanto faria sentido?"
   - Se diz "depende": cava — depende de que?
   - Se diz numero: "se eu lancar nesse preco, voce me usaria nos primeiros dias?"

[FECHAMENTO + COMPROMISSO — 4min]
7. "Posso te avisar quando tiver beta? Voce topa entrar com {desconto/condicao}?"
8. Se a pessoa disser sim: "Pra eu te garantir vaga no beta, posso te mandar PIX de R$ {49} agora? Devolvo se eu nao entregar em 30 dias."
```

A pergunta 8 e a mais importante. **A pessoa que paga R$ 49 valida 100x mais que a que diz "topa".**

## 4. Mensagem de prospec (LinkedIn / email)

Texto pronto, **5 linhas no maximo**, sem clichê:

```
Oi {nome},

Sou {seu nome}, {breve credencial relevante}. 
Estou pesquisando se faz sentido criar uma ferramenta pra {dor especifica do nicho}.
Topa uma conversa de 15min essa semana? Sem pitch — so 5 perguntas pra entender como isso e dor pra voce.

Se preferir, mando 2 horarios.
```

Sem "espero que esteja bem", sem "venho por meio desta", sem "permita-me apresentar". Direto.

## 5. Criterios de sucesso (numericos)

Defina objetivamente:

| Criterio | Meta minima | Meta boa |
|---|---|---|
| Mensagens enviadas | 50 | 80 |
| Respostas | 10 | 20 |
| Conversas realizadas | 8 | 12 |
| Disseram "eu pagaria" com valor | 5 | 8 |
| Pre-venda confirmada (R$ recebido) | 2 | 5 |

Se voce bateu **meta minima nos 5 criterios**: validado, segue pro `03-MVP-MINIMO.md`.

Se nao bateu pre-venda mas bateu no resto: **30% de chance de ser ruido educado**. Faca mais 1 semana de pre-venda focada.

Se nao bateu mensagens/respostas: o nicho e bom mas o canal/mensagem esta errado — itera.

Se conversou mas ninguem fez compromisso: **a dor nao e forte**. Pivota ou mata o nicho. Volta pro `01-NICHO.md`.

## 6. Sinais de morte

3-5 padroes que aparecem nas conversas e que indicam "esse nicho nao paga":

1. {ex: "Todos pedem desconto antes mesmo de saber o preco — sinal de que valor percebido e baixo"}
2. {ex: "Todos dizem 'legal' mas nenhum quer falar de novo"}
3. {ex: "Todos ja tentaram e desistiram — saturado"}
4. {ex: "Todos perguntam se 'tem versao gratis' — nao querem pagar"}
5. {ex: "Voce identifica concorrente direto consolidado, todos usam — voce vai brigar com fornecedor estabelecido"}

## 7. O que fazer com a pre-venda

Pessoa transferiu R$ 49? **Voce tem responsabilidade.** Comportamento certo:

- Recibo formal por WhatsApp/email com prazo de entrega (ex: "Beta em 30 dias. Se nao entregar, devolvo automaticamente.")
- NAO usa o dinheiro — coloca em conta separada/segura
- Se em 30 dias voce decide nao seguir, **devolve com uma nota** explicando ("decidi nao seguir, devolvendo seu sinal — obrigado pela confianca")
- Versionando isso em arquivo pra registro

Comece a montar.

--- FIM DO PROMPT ---

---

## Sinal verde pra ir pro `03-MVP-MINIMO.md`

- [ ] 5+ pessoas disseram "eu pagaria R$ X/mes" com numero
- [ ] 2-3 pessoas transferiram sinal real
- [ ] As respostas em "como voce resolve hoje" sao consistentes (a dor existe)
- [ ] Voce achou padrao no preco que aceitam (ex: 70% disseram entre R$ 49-79)

Sem esses checks: **nao constroi**. Volta uma etapa.

## Erros comuns

1. **Pedir opiniao em vez de pre-venda** — opiniao e gratis e ninguem se compromete
2. **Falar do produto antes de ouvir a dor** — vicia a resposta
3. **Aceitar "manda quando estiver pronto" como validado** — nao e
4. **Convencer a pessoa que ela tem o problema** — se ela nao tem, voce esta errado de nicho
5. **Achar que 1-2 conversas validaram** — precisa de 8+ pra ver padrao

## Bonus: como pedir R$ 49 sem parecer estranho

Frase que funciona:

> "Pra eu te garantir vaga no beta com {desconto}, posso te mandar pix de R$ 49? E o sinal pra entrar na fase fechada — devolvo automaticamente se eu nao entregar nos proximos 30 dias."

A pessoa que **transfere** ja virou cliente. A que diz "ah, depois te mando" virou "achou legal".

## Antes de seguir

Gravou `validacao.md`? Tem 5+ "eu pagaria" + 2-3 sinais de pre-venda na conta? Faz commit:

```bash
git add validacao.md
git commit -m "validacao concluida: {N} pre-vendas, R$ {Y} de sinal"
```

Vai pro `03-MVP-MINIMO.md`.
