# 01 — Copywriting

> Substitui: Jasper, Copy.ai, Writesonic, Rytr, Anyword, e qualquer "AI writer" generico.

## Por que substituir

Essas ferramentas sao **wrappers de LLM com templates pre-feitos**. Elas:

1. Pegam um prompt deles
2. Preenchem com seus inputs
3. Mandam pra um LLM (em muitos casos, **a propria Claude ou GPT da OpenAI**)
4. Te entregam a saida

Voce paga pelo template + interface. **O motor (LLM) voce pode usar direto**.

## Comparativo de custo (Brasil, 2026)

| Ferramenta | Plano popular | Mensal | Anual |
|---|---|---|---|
| Jasper | Creator | US$ 49 (~R$ 270) | US$ 588 (~R$ 3.230) |
| Copy.ai | Pro | US$ 49 (~R$ 270) | US$ 588 |
| Writesonic | Standard | US$ 19 (~R$ 105) | US$ 228 |
| Rytr | Unlimited | US$ 29 (~R$ 160) | US$ 348 |
| Anyword | Starter | US$ 49 (~R$ 270) | US$ 588 |

vs. **Claude Pro (R$ 110/mes)**: cobre **todas** essas funcoes pra 1 a 5 pessoas.

Economia tipica: R$ 100-250/mes por seat = **R$ 1.200-3.000/ano** se voce so usava 1.

## Volume que cabe no Claude

| Volume | Solucao |
|---|---|
| Ate 100 textos/mes | Claude Pro web — perfeito |
| 100-500 textos/mes | Claude Pro web (cabe na assinatura) |
| 500-2000 textos/mes | Pro + uso eventual de API pra automatizar |
| 2000+ textos/mes | API direta + script |

## A logica do prompt deste arquivo

Tem **2 partes**:

### Parte A — Prompt da marca (configura UMA vez)

Esse prompt voce roda **uma vez** e a saida vira `marca.md` — o "brand voice" da ferramenta SaaS, em arquivo proprio.

### Parte B — Prompt de tarefa (toda hora que precisar copy nova)

Esse voce cola junto do `marca.md` pra gerar copy especifica.

---

## Parte A — Configurar o brand voice

Roda 1 vez. Salva em `marca.md`.

--- COMECO PROMPT A ---

Voce e um diretor de marca senior. Sua missao: construir um arquivo `marca.md` completo que captura como minha marca fala, pra que toda copy futura saia consistente.

Vou responder suas perguntas. Faca uma pergunta por vez ate cobrir tudo. No final, gere o arquivo `marca.md` completo em markdown.

# Topicos a cobrir

1. **Empresa** — nome, o que vende, modelo de negocio
2. **Publico** — perfil ideal (idade, profissao, dor principal, contexto de compra)
3. **Problema central** — qual dor profunda voce resolve (na linguagem do publico, nao do MBA)
4. **Solucao** — como voce resolve, em 2-3 linhas humanas
5. **Tom de voz** — escolha 3-4 atributos: tecnico, amigavel, provocador, sobrio, divertido, formal, irreverente, professoral, etc.
6. **Vocabulario** — palavras que voce USA (ex: "operacao", "fechar caixa") e que voce NAO usa (ex: "transformar", "revolucionar", "elevar")
7. **Niveis de formalidade** — voce trata por voce / tu / senhor? como abre conversa? como se despede?
8. **Provas** — clientes ja atendidos, numeros, depoimentos curtos, premios (se houver)
9. **Diferencial real** — o que voce faz que concorrente nao faz / faz pior
10. **Anti-claims** — claims que voce NUNCA usaria (ex: "garanto 100% de retorno", "em 30 dias voce muda de vida")
11. **Exemplos de copy boa** — voce ja escreveu (ou viu) copy desta marca que funcionou bem? Cole 2-3 exemplos
12. **Personagens** — clientes ficticios mas representativos (1-3 personas com nome, contexto, frase tipica)

# Formato da saida

```markdown
# Marca: {NOME}

## Contexto
{empresa, modelo, mercado}

## Quem compra
{personas detalhadas}

## Como falamos
{tom de voz com exemplos}

## Vocabulario
- USAMOS: {lista}
- EVITAMOS: {lista}
- NUNCA: {lista anti-claims}

## Provas
{numeros, clientes, social proof}

## Padroes
- Abertura: {ex: "Direto: ..."}
- Despedida: {ex: "Se fizer sentido, me responde."}
- CTA tipico: {ex: "Conferir agora", "Calcular o meu", "Ver caso completo"}

## Exemplos de copy boa que ja funcionou
{exemplos do usuario}

## Personas
{1-3 personas com nome ficticio}
```

Comece pela pergunta 1.

--- FIM PROMPT A ---

---

## Parte B — Gerar copy especifica

Roda toda hora que precisar.

--- COMECO PROMPT B ---

Voce e um copywriter senior B2B/B2C brasileiro, especialista em conversao. Sua missao: escrever a copy abaixo seguindo a marca definida no arquivo `marca.md` que esta entre `<marca>` e `</marca>`.

<marca>
{COLE AQUI O CONTEUDO DO marca.md}
</marca>

# Tarefa

Tipo de copy: {ESCOLHA: anuncio Meta Ads / anuncio Google / e-mail de vendas / e-mail de nutricao / post Instagram / carrossel Instagram / post LinkedIn / headline landing / pagina de vendas / sequencia de e-mails / pop-up / SMS / mensagem WhatsApp / outro}

Detalhes da peca:
- {tamanho — caracteres, palavras, slides}
- {canal especifico — qual rede, qual produto da rede}
- {plataforma de destino — onde a copy vai aparecer}

# Objetivo da copy

{O QUE A PESSOA TEM QUE FAZER apos ler — clicar / agendar / comprar / responder / baixar / cadastrar}

# Contexto especifico desta peca

{ex: e a primeira mensagem dessa pessoa OU ela ja viu nossa marca antes OU e remarketing apos abandono OU saiu de uma promocao etc}

# Restricoes adicionais

- {ex: nao mencionar concorrente / nao falar de preco / mencionar prazo de X dias}

# Saida obrigatoria

3 versoes (A, B, C) com hipoteses diferentes do que move a pessoa. Cada versao com:

```
## Versao A — Hipotese: {ex: "medo de continuar perdendo dinheiro com planilha"}

{copy completa}

CTA: {versao especifica do CTA}
Por que essa versao pode funcionar: {1 linha}
Por que pode falhar: {1 linha}
```

Regras de estilo:

1. **Numero especifico vence adjetivo**: "ganho R$ 3.200/mes" vence "ganho muito"
2. **Comece pelo problema do cliente**, nao pela solucao
3. **Use a linguagem do publico**, nao a sua
4. **Sem clichê**: nada de "transforme sua vida", "descubra agora", "voce nao vai acreditar", "revolucione", "garanto"
5. **Sem emoji**, salvo se a marca usar (ver `marca.md`)
6. **CTA com verbo + beneficio**: "Calcular meu primeiro fechamento" vence "Comecar agora"

--- FIM PROMPT B ---

---

## Caso de uso real — Camisa BR

**Marcelo (loja Camisa BR)** rodou Parte A uma vez e gerou esse trecho do `marca.md`:

```markdown
# Marca: Camisa BR

## Como falamos
Tom: amigavel + irreverente + bairrista
Tratamento: voce
Abertura tipica: "Bora pra mais uma cidade?" (nas redes)
                 "Oi! Tudo bem?" (no whatsapp 1:1)

## Vocabulario
- USAMOS: cidade, terra, time, bairro, pegar (no sentido de comprar), pra (em vez de para)
- EVITAMOS: produto (use "camiseta"), adquirir, transformar, revolucione
- NUNCA: "garantia de fama", "diferencial unico"
```

Toda quarta de manha, Marcelo precisa de um post de Instagram sobre alguma cidade. Ele cola Parte B + `marca.md` + tarefa:

> Tipo: post Instagram simples (legenda 5-8 linhas + imagem da camiseta)
> Tema: lancamento BH M (Belo Horizonte)
> Objetivo: gerar interesse, levar pro DM
> Contexto: lancamento de hoje
> Restricoes: mencionar que e producao limitada (50 unidades)

3 versoes saem. Marcelo escolhe a que mais bateu com a alma da marca, ajusta 1-2 palavras se precisar, posta. **Tempo total: 4 minutos.** Antes, no Jasper: 12 minutos + ele tinha que arrumar muita coisa porque o Jasper nao sabia o tom dele.

---

## Quando NAO substituir

| Situacao | Recomendacao |
|---|---|
| Time de 5+ copywriters trabalhando junto com fluxo de revisao | Mantem Jasper Pro com colaboracao |
| Compliance regulado (saude, financas) que exige template aprovado | Mantem ferramenta com aprovacao |
| Volume gigante (5k+ textos/mes) automatizado | Avaliar API direta com infra propria |

Pra 95% das PMEs, o fluxo Parte A + Parte B substitui qualquer Jasper/Copy.ai com economia direta.

## Biblioteca de variantes uteis

Tarefas-tipo que voce pode adaptar:

- **Headline de landing**: "Tipo: headline + subheadline pra hero da landing. 8 palavras maximo no titulo, 16 no subtitulo. Tema: {seu produto}."
- **Anuncio Meta**: "Tipo: anuncio Meta Ads (titulo 90c + corpo 125c). Objetivo: clique pra landing. Tema: {sua oferta}."
- **E-mail de boas-vindas**: "Tipo: primeiro e-mail apos cadastro. 4-7 linhas. Objetivo: gerar primeira acao no produto."
- **Resposta a objecao**: "Tipo: resposta de WhatsApp 3-5 linhas. Cliente disse: '{cole o que ele disse}'. Objetivo: contornar objecao sem ser agressivo."
- **Carrossel Instagram**: "Tipo: carrossel 7 slides. Slide 1 hero, 2-6 conteudo, 7 CTA. Tema: {tema}."
- **Cabecalho de e-mail**: "Tipo: 5 sugestoes de assunto pra e-mail. Maximo 50 caracteres."

Salve as melhores em `prompts/biblioteca.md` pra reusar.
