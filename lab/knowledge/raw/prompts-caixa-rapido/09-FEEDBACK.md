# 09 — Feedback

Os primeiros 10-30 clientes sao seu mapa do tesouro. Esse passo monta o sistema pra extrair tudo deles.

## Por que esse passo importa

Voce vai ouvir muitos feedbacks contradicios:

- "Adicione X"
- "Tira X, ta confuso"
- "Coloca isso de graca"
- "Cobra mais caro"

**Todo mundo ta com a propria razao.** O seu trabalho nao e atender todo mundo — e identificar o **padrao**.

A coisa mais cara em SaaS e construir feature errada. A segunda mais cara e nao construir feature certa porque nao escutou direito. Esse prompt **sistematiza pra voce decidir bem**.

## O que voce sai com esse prompt

`customer-success.md` com:

- Cadencia de contato com clientes (dia 0, 3, 14, 30, etc.)
- Mensagens prontas pra cada momento
- Sistema de organizacao do feedback
- Pergunta-mae (Sean Ellis)
- Sinais de churn antecipado

---

--- COMECO DO PROMPT ---

Voce e um especialista em customer success pra SaaS B2B early-stage. Sua missao: montar um sistema simples e eficaz de feedback continuo dos primeiros 10-30 clientes do meu SaaS.

# Contexto

<nicho>
{COLE NICHO.MD}
</nicho>

<mvp>
{COLE MVP.MD}
</mvp>

Numero atual de clientes pagantes: **{N}**

# Restricoes

- Eu nao tenho equipe — eu mesmo vou conversar com clientes
- Maximo **5h/semana** pra customer success
- Quero conversa real, nao formulario NPS frio
- Quero descobrir:
  1. O que mantem cliente
  2. O que faz cliente cancelar
  3. Qual a proxima feature de maior impacto
  4. Quais clientes viram fundadores leais (multiplicadores)

# O que voce me entrega

## 1. Cadencia de contato (tabela)

| Momento | Tipo | Canal | O que perguntar |
|---|---|---|---|
| Dia 0 (cadastro) | Boas-vindas + 1 pergunta | Email + WhatsApp | "Quantos {clientes/operacoes} voce vai ter no sistema?" |
| Dia 1 (apos primeiro uso real) | Confirmacao | Email | "Conseguiu rodar o {primeiro fluxo}? Travou?" |
| Dia 3 | Check-in | WhatsApp | "Como ta sendo? O que voce ja deixou de fazer no antigo metodo?" |
| Dia 7 | Touchpoint | Email | "Tem alguma coisa que voce esperava encontrar e nao tem?" |
| Dia 14 | Conversa profunda | Call 15min (opcional pra cliente) | Perguntas estruturadas (ver abaixo) |
| Dia 30 | **Sean Ellis test** | Email curto | "Como voce se sentiria se nao pudesse mais usar o {produto}?" |
| Quando solta feature nova | Aviso + check | Email | "Lancei X. Voce pediu? Testou? Gostou?" |
| Quando ele cancela | Saida | WhatsApp | "Posso entender o motivo? (sem tentar reverter forcado)" |
| Mensal | Checkpoint | Email mass | Resumo do que mudou + perguntas abertas |

## 2. Mensagens prontas

Pra cada item da tabela, escreva texto pronto pra colar.

### Dia 0 — Boas-vindas (email)

```
Assunto: {Nome}! Bem-vindo ao {produto} 🎉

Oi {nome},

Sou {seu nome}, fundador do {produto}. Pessoalmente queria te dar boas-vindas.

Ja te deixei tudo pronto. Pra acessar:
{link}

Uma pergunta rapida pra eu te ajudar melhor: quantos {clientes / operacoes / etc.} voce planeja ter no sistema?

Pode responder ja esse email mesmo.

Se travar em qualquer coisa, me chama no whats: {numero}

Abraco
{seu nome}
```

### Dia 3 — Check-in (WhatsApp)

```
{Nome}, td bem?

So pra dar uma confirmada — voce ja conseguiu {primeira acao do produto}?

Se travou em algo me fala. Se ja ta rodando, tambem me conta — ajuda muito a fundacao.
```

### Dia 14 — Conversa profunda (oferece call)

```
{Nome},

Voce esta no {produto} ha 2 semanas. Eu queria te entender melhor:

1. O que voce ja conseguiu fazer aqui que nao fazia antes?
2. Tem algo que ta te frustrando? O que mais?
3. Se voce pudesse trocar UMA coisa do produto, qual seria?

Topa uma chamada de 15min pra eu te ouvir? Mando 2 horarios:
- {opcao 1}
- {opcao 2}

OU se preferir responder por mensagem mesmo, ta otimo.
```

### Dia 30 — Sean Ellis (email curto)

```
Assunto: 1 pergunta rapida

{Nome},

Ja vai 1 mes que voce esta no {produto}.

Quero saber 1 coisa: como voce se sentiria se nao pudesse mais usar o {produto}?

A) Muito decepcionado(a)
B) Um pouco decepcionado(a)
C) Indiferente — eu mudaria pra outra coisa

Me responde so com a letra. Ajuda demais.

Obrigado!
{seu nome}
```

40%+ respondendo "A" = product-market fit.

### Quando o cliente cancela

```
{Nome}, vi que voce cancelou.

Sem pressao pra voltar. So queria entender em 1 frase: o que faltou pra continuar?

Pode ser sincero — nao vou nem tentar te demover, prometo. So preciso aprender pra melhorar pros proximos.
```

## 3. Sistema de organizacao do feedback

`feedback/`:

```
feedback/
├── conversas/
│   ├── 2026-02-15-carlos-c001.md
│   ├── 2026-02-16-mariana-c003.md
│   └── ...
├── resumo-semanal.md      ← atualiza toda sexta
├── decisoes.md            ← decisoes de roadmap baseadas em feedback
└── churn.md               ← analise de quem saiu
```

Pra cada conversa, formato:

```markdown
## {DATA} — {Cliente} (id)

**Canal:** whatsapp / email / call
**Estagio:** dia X / motivo do contato
**Resumo:** 2-3 linhas
**Tags:** #feature-X #bug #onboarding #preco #elogio
**Acao gerada:** {ou "nenhuma"}

**Trecho relevante (verbatim):**
> "{copia exatamente o que ele disse — usa pra copy depois}"
```

`resumo-semanal.md`:

```markdown
# Resumo da semana — {data inicio} a {data fim}

## Top 3 dores recorrentes
1. {dor X — apareceu em N conversas}
2. ...

## Top 3 elogios recorrentes
1. {elogio X — apareceu em N conversas}
2. ...

## Top 3 features pedidas
1. {feature X — N pedidos independentes}
2. ...

## Casos de churn essa semana
- {cliente — motivo curto}

## Decisoes da semana
- {decisao 1 baseada no feedback}
- {decisao 2}

## Bugs pendentes
- {bug X}
```

## 4. Como decidir o que construir a seguir

Regrinha clara e dura:

> So entra na proxima sprint o que apareceu em **3+ conversas independentes** OU o que esta gerando **churn**.

Tudo o resto: anota e congela. Voce nao constroi pelo loud user. Constroi pelo padrao.

Exemplo pratico (PontoFiscal, mes 2):

```
Pedidos recorrentes:
- "Importar planilha em massa": 12 conversas → ENTRA
- "Marcar pago via mensagem do whats": 8 → ENTRA  
- "Dashboard mensal": 7 → ENTRA
- "Integracao com Domínio": 4 → ENTRA na fila
- "App mobile": 3 → AVALIAR
- "Versao em ingles": 2 → CONGELA
- "Notificacao push": 1 → CONGELA
- "Botão de modo escuro": 1 → CONGELA
```

## 5. Sinais de churn antecipado

Cliente nao avisa que vai sair. Voce ve sinais antes:

```
Sinal 1: Nao logou ha {X} dias
  Acao: Email "Tudo bem? Vi que voce nao tem entrado..."

Sinal 2: Nao usou a feature core ha {Y} dias
  Acao: WhatsApp "Posso te ajudar com {feature core}?"

Sinal 3: Reclamou de bug e nao recebeu resposta em 24h
  Acao: Email pessoal pedindo desculpa + status

Sinal 4: Pediu cancelamento em alguma conversa
  Acao: Liga pessoalmente HOJE, oferece desconto/pausa

Sinal 5: NPS baixo (0-6)
  Acao: Pergunta o motivo especifico em call
```

Adapte os {X} {Y} pro seu caso. Pra PontoFiscal: 5 dias sem login, 3 dias sem usar feature core.

## 6. Programa de fundadores

Os primeiros 10-20 clientes que **respondem feedback + ficam 60+ dias**:

- Tags eles como "fundadores"
- Da preco fixo pro early bird pra sempre
- Entra num grupo privado (whatsapp/discord) com voce
- Ve roadmap antes de todo mundo
- Eles viram fonte de:
  - Indicacoes (qualidade alta)
  - Beta tests
  - Depoimentos pra landing
  - Casos pra venda
  - Co-criacao de feature

Comece a montar.

--- FIM DO PROMPT ---

---

## Atalho — pesquisa rapida em vez de calls

Se voce nao consegue marcar calls, faca **mini-survey via WhatsApp** com 3 perguntas:

```
Oi {nome}! 1 minuto pra ajudar a melhorar o {produto}?

1. De 0 a 10, qto voce indicaria pra um colega?
2. Qual a UMA coisa que voce mudaria?
3. Qual a UMA coisa que te impede de cancelar?

Pode responder com 3 numeros + 2 frases curtas. Vale ouro.
```

Resposta media: 50-70%. Em 30 clientes, voce tem 15-20 dados profundos.

## Erros comuns

1. **Esperar feedback chegar sozinho** — vc tem que sair atras
2. **Construir tudo que pedem** — voce vira "ferramenta sem foco"
3. **Ignorar reclamacao por achar que e cliente "chato"** — chato e quem ainda nao saiu
4. **Esquecer o silencio** — quem nao respondeu 3 mensagens seguidas ja saiu na cabeca dele
5. **Nao registrar feedback verbatim** — frase do cliente vira sua melhor copy

## Antes de seguir

```bash
git add customer-success.md
git commit -m "sistema de feedback definido"
```

Apos 30 dias rodando, voce vai pro `10-ESCALA.md` decidir se escala, pivota ou mata.
