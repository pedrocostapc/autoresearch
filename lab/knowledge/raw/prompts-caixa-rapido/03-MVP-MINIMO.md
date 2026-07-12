# 03 — MVP minimo

Cortar tudo o que nao precisa estar na primeira versao.

> O instinto de quase todo fundador: "preciso disso pra parecer profissional". 99% dessas coisas sao adiaveis. Esse prompt corta cirurgicamente.

## Princípio

**O cliente paga pra resolver dor, nao pra usar UI piscante.** A diferenca entre MVP que funciona e MVP que nao funciona nao e quantidade de feature — e clareza da promessa nuclear.

## A regra dos 8 passos

Se o seu MVP nao cabe em 8 passos do usuario (do cadastro ao resultado), voce nao cortou o suficiente.

> No exemplo do PontoFiscal (`EXEMPLO-COMPLETO.md`), os 8 passos foram:
> 1. Cadastra (email + senha)
> 2. Paga R$ 49/mes (cartao)
> 3. Cadastra clientes MEI (1 por 1 mesmo)
> 4. Configura quando avisar (5d antes do vencimento, no dia, etc.)
> 5. Sistema agenda lembretes automaticos
> 6. Cliente recebe WhatsApp/email
> 7. Contador marca pago no painel
> 8. No proximo mes, repete

8 passos exatos. Tudo que nao cabe nisso, ficou em V2.

## O que voce sai com esse prompt

`mvp.md` com:
- Promessa nuclear em 1 frase
- Lista de features em 3 colunas (TER / V2 / NUNCA)
- Fluxo do usuario em ate 8 passos
- Modelo de cobranca decidido
- Riscos conscientes
- Checklist de "esta pronto pra arquitetura"

---

--- COMECO DO PROMPT ---

Voce e um product manager senior conhecido por matar features. Sua missao: pegar a ideia validada e cortar ate sobrar SO o que precisa pra cobrar do primeiro cliente.

# Contexto

Cole o conteudo de `nicho.md` e `validacao.md`:

<nicho>
{COLE AQUI}
</nicho>

<validacao>
{COLE AQUI}
</validacao>

# Restricoes inegociaveis

- O MVP precisa estar pronto em **no maximo 14 dias de codificacao** (cabivel em 2-3h/dia ou 6-8h/dia)
- Quem vai construir: eu + Claude Code (sou {iniciante / intermediario / experiente} em programacao)
- O MVP precisa **cobrar do cliente desde o primeiro dia** (logo, precisa de auth + pagamento)
- Sem mobile app — so web
- Pode usar API externa paga so se for absolutamente essencial pra entregar a promessa nuclear

# O que voce me entrega

## 1. A "promessa nuclear" (1 frase)

Comece com verbo. Sem buzzword. Especifica.

✅ "Lembra automaticamente cada cliente seu de pagar o DAS-MEI no vencimento."
✅ "Gera o demonstrativo mensal de IRPF do cliente em 3 cliques."
✅ "Avisa quando seu cliente pet shop esta no risco de cancelar a assinatura."

❌ "Plataforma inovadora de gestao tributaria com IA."
❌ "Otimize seu tempo com automacao inteligente."

A frase precisa caber numa headline de landing.

## 2. Lista de features em 3 colunas

### TEM QUE TER (MVP)

So o que e essencial pra promessa nuclear funcionar + auth + pagamento + suporte basico.

```
- Auth (signup, login, logout, recuperar senha)
- Pagamento via Stripe (assinatura mensal)
- {feature core 1}
- {feature core 2}
- ...
- Email transacional minimo (confirmacao cadastro, recibo pagamento)
- Pagina de "billing" pra cancelar/atualizar pagamento
```

Maximo 8-10 itens.

### NAO TEM AINDA (V2 — depois dos primeiros clientes)

Coisas que vao aparecer no feedback mas nao bloqueiam pagamento:

```
- Importacao em massa
- Integracoes com sistema X
- Multi-usuario
- App mobile
- Notificacoes push
- Dashboard avancado
- Relatorios PDF
- ...
```

### NUNCA VAI TER (escopo definido — nao se perde nisso)

Coisas que parecem boa ideia mas que diluem o produto:

```
- Recurso que sai do nicho
- Customizacao excessiva (vira CRM)
- Modulo que outro produto ja faz melhor
- ...
```

## 3. Fluxo do usuario (em ate 8 passos)

Do cadastro ao resultado da promessa nuclear:

```
1. {acao}
2. {acao}
...
8. {resultado / repete}
```

Se passou de 8: corta. Se nao da pra cortar: voce ainda tem feature demais no TEM QUE TER.

## 4. Modelo de cobranca

Decida UM modelo, simples:

- **Plano unico vs. tier:** **plano unico** quase sempre. Tier so se claramente faz sentido pelo uso (ex: ate X clientes = R$ 49, ate Y = R$ 99).
- **Trial?** Recomendado: **0-7 dias** com cartao requerido. Trial mais longo demora pra validar receita.
- **Mensal/anual?** **So mensal no MVP**. Anual depois de 30+ clientes.
- **Setup fee?** **Nao** — pra esse ticket nao faz sentido.
- **Preco:** definido no `validacao.md`. Use o valor que apareceu mais.

Justifique em 2 linhas a escolha.

## 5. Riscos conscientes (o que vai incomodar)

3-5 coisas que **conscientemente** voce decidiu nao ter no MVP. Pra cada uma:

```
**Risco:** {ex: "Clientes vao querer importar planilha em massa"}
**Como vou tratar:** {ex: "Manual mesmo na V1. Aviso na onboarding 'no MVP, cadastro e 1 por 1'."}
**Prazo pra V2:** {ex: "Apos 20 clientes pagantes ou 60 dias"}
```

Salva isso em `riscos-mvp.md` separado.

## 6. Auto-checklist final

Antes de seguir pra arquitetura, confirma:

- [ ] Promessa nuclear cabe em 1 frase com verbo
- [ ] Fluxo do usuario cabe em ate 8 passos
- [ ] Inclui pagamento desde o dia 1
- [ ] Da pra construir em 14 dias com meu nivel de programacao + Claude Code
- [ ] Eu seria capaz de explicar o produto pra um cliente em 30 segundos

Se algum nao bateu, mostre o que precisa cortar mais.

## 7. Salvar mvp.md

Apos finalizar, monte o arquivo `mvp.md`:

```markdown
# MVP: {Nome do produto}

## Promessa nuclear
{frase}

## Features

### TEM QUE TER (MVP)
{lista}

### NAO TEM AINDA (V2)
{lista}

### NUNCA VAI TER
{lista}

## Fluxo do usuario (8 passos)
{lista numerada}

## Modelo de cobranca
- Plano unico R$ {X}/mes
- {Trial / sem trial}
- Mensal apenas

## Riscos conscientes
{ver riscos-mvp.md}

## Definicao de pronto
"O MVP esta pronto quando: {criterio especifico mensuravel}."
```

Comece a montar.

--- FIM DO PROMPT ---

---

## Sinal verde pra ir pro `04-ARQUITETURA.md`

- [ ] `mvp.md` salvo no Git
- [ ] Promessa nuclear cabe na headline da landing
- [ ] 8 passos definidos
- [ ] Modelo de cobranca claro
- [ ] Voce conseguiria explicar o produto em 30s pro vovo

## Erros comuns

1. **MVP com 15 features "pra nao parecer fraco"** — corta mais
2. **Modelo de cobranca complicado** — plano unico no MVP
3. **Trial gratuito longo** — 14+ dias de trial = 30+ dias pra validar receita real
4. **"Eu vou colocar so o login com Google e o cadastro normal"** — escolha UM no MVP
5. **Esquecer pagina de "cancelar assinatura"** — sem isso, churn vira drama de suporte

## Antes de seguir

```bash
git add mvp.md riscos-mvp.md
git commit -m "MVP definido: {promessa nuclear curta}"
```

Vai pro `04-ARQUITETURA.md`.
