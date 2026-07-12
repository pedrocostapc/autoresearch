# 04 — Atendimento

> Substitui: Manychat, Chatbot.com, Botconversa, Take Blip, scripts pagos.

## Por que substituir

Boa parte dos "bots" que voce paga sao **arvores de decisao com 8 mensagens**. Voce paga R$ 100-700/mes pelo construtor visual + integracao com WhatsApp/Instagram.

Claude responde melhor com **1 prompt + base de conhecimento da sua empresa em arquivo `.md`**. Mais rapido pra construir, mais flexivel, mais natural pro cliente.

## Comparativo de custo (Brasil, 2026)

| Ferramenta | Plano | Mensal | Limite |
|---|---|---|---|
| Manychat | Pro | US$ 15 (~R$ 85) | 1.000 contatos |
| Manychat | Pro | US$ 35 (~R$ 195) | 5.000 contatos |
| Chatbot.com | Starter | US$ 52 (~R$ 285) | 1.000 contatos |
| Botconversa | Pro | R$ 297/mes | ilimitado |
| Take Blip | varia | R$ 500-3.000/mes | varia |

vs. **Claude Pro (R$ 110/mes) + integracao via API** (custo por uso, ~R$ 0,005-0,02 por resposta):

| Volume | Custo total Claude estimado |
|---|---|
| 100 atendimentos/mes | R$ 110 (Pro suficiente) |
| 1.000 atendimentos/mes | R$ 130 (Pro + ~R$ 20 API) |
| 5.000 atendimentos/mes | R$ 200 (Pro + ~R$ 90 API) |
| 20.000 atendimentos/mes | R$ 500 (Pro + ~R$ 400 API) |

Pra volume baixo/medio, economia de **R$ 100-2.500/mes**.

## Volume que cabe (e quando NAO substituir)

| Volume | Decisao |
|---|---|
| < 500 atendimentos/mes | Substitui de boa, manual ou semi-automatico |
| 500-3.000/mes | Substitui com integracao API + webhook (vale o esforco) |
| 3.000-10.000/mes | Avalia: Claude funciona, mas operacao 24/7 vira ponto |
| 10.000+/mes | Provavel manter ferramenta especializada |

## A logica deste prompt

3 partes:

### Parte A — Construir base de conhecimento (`base.md`)
Roda 1 vez. O Claude te entrevista. Saida: arquivo com tudo que o atendimento precisa saber.

### Parte B — Modo manual (sem integracao)
Voce copia mensagem, cola junto da base, recebe resposta, copia pro WhatsApp.

### Parte C — Modo automatico (com integracao)
Webhook do WhatsApp Business / Z-API conectado ao Claude API. Resposta automatica com escalacao humana quando necessario.

---

## Parte A — Construir base de conhecimento

Esse e o passo mais importante. **Sem `base.md` boa, qualquer atendimento e ruim** (humano ou Claude).

--- COMECO PROMPT A ---

Voce vai me ajudar a construir o arquivo `base.md` que sera usado em todo atendimento ao cliente. Esse arquivo precisa ter TUDO que um atendente novato precisaria saber pra responder bem 90% das duvidas.

Me entreviste, **uma pergunta por vez**, ate cobrir os 16 topicos abaixo. Pra cada resposta minha, voce escreve a versao "limpa" no `base.md` que vamos construindo. No final, me mostra o arquivo completo formatado.

# Topicos a cobrir

## Sobre a empresa
1. Nome oficial e nome comercial (se diferentes)
2. O que vende (produto/servico em 3 linhas — sem marketinges)
3. Historia minima (quando comecou, em que cidade, qto tem de mercado) — pra contextualizar
4. Quem voce **NAO** atende (filtra publico errado economiza tempo de todo mundo)

## Sobre o produto/servico
5. Catalogo principal (top 5-10 produtos/servicos com preco)
6. Faixa de preco geral
7. Formas de pagamento aceitas
8. Prazos: entrega? execucao? agendamento?

## Politicas
9. Politica de troca/devolucao (em quantos dias? em que condicao?)
10. Politica de cancelamento
11. Garantia (quanto tempo, o que cobre, o que NAO cobre)
12. Politica de privacidade resumida (LGPD)

## Operacao
13. Canais oficiais (site, instagram, whatsapp, email — qual e qual)
14. Horario de atendimento humano (e o que o cliente faz fora desse horario)
15. Endereco fisico (se tem) ou se e 100% online

## Comunicacao
16. Tom de voz (cole o `marca.md` se tiver, ou descreva: amigavel/tecnico/formal)
17. **FAQ** — perguntas que clientes mais fazem, com a resposta pronta. Pelo menos 15 perguntas.

# Formato do `base.md`

```markdown
# {Nome da Empresa} — Base de conhecimento do atendimento

> Atualizado em: {data}

## Sobre nos
{paragrafo de 3-4 linhas sobre a empresa}

## O que vendemos
{lista enxuta dos top produtos/servicos com preco}

## Para quem nao somos
{lista — economia de tempo}

## Politicas

### Troca e devolucao
{texto direto}

### Cancelamento
{texto}

### Garantia
{texto}

## Atendimento
- Horario humano: {dias e horarios}
- Fora desse horario: {ex: respondemos no proximo dia util}
- Canais oficiais: {lista}

## Tom de voz
{como falamos}

## FAQ

### {Pergunta 1}
{resposta direta, 2-4 linhas}

### {Pergunta 2}
...
```

# Regras

- Resposta no estilo "como o dono da empresa explicaria" — direta, sem jargao
- Sem marketinges ("transforme sua vida")
- FAQ com **resposta pronta**, nao redirecionamento ("entre em contato com a equipe")
- Politicas claras: data, condicao, prazo

Comece pela pergunta 1.

--- FIM PROMPT A ---

---

## Parte B — Atendimento manual (volume baixo)

Cada vez que chega mensagem de cliente, voce roda esse prompt:

--- COMECO PROMPT B ---

Voce e o atendente da empresa abaixo. Sua base de conhecimento esta entre `<base>` e `</base>`. Use SOMENTE essa base.

<base>
{COLE AQUI O CONTEUDO COMPLETO DO base.md}
</base>

# Mensagem do cliente

{COLE A MENSAGEM EXATAMENTE COMO RECEBEU}

# Contexto adicional (se relevante)

- Canal: {whatsapp / instagram dm / email}
- Cliente novo ou recorrente: {novo / recorrente — se sabe}
- Estagio: {primeira mensagem / em conversa ja / pos-venda / cobranca / reclamacao}

# Regras inviolaveis

1. **Responda no tom da `base.md`**
2. **Resposta curta** — maximo 4 linhas, salvo se for tecnica
3. **Se a duvida nao estiver na base, NAO INVENTE**. Diga: "Vou te conectar com a equipe ja, ja chamo aqui." e marca `[ESCALAR]` na primeira linha
4. **Se a pessoa estiver irritada/grosseira**, reconhece e escala: "Entendi, deixa eu chamar uma pessoa pra te atender melhor." `[ESCALAR]`
5. **Cancelamento, reembolso, reclamacao formal**: SEMPRE `[ESCALAR]`
6. **Quando fizer sentido**, ofereca link especifico (catalogo, agendamento, suporte)
7. **Nao prometa prazo, desconto ou condicao** que nao esta na base — escale

# Saida

So a resposta a ser enviada ao cliente. Se for `[ESCALAR]`, comece a resposta com `[ESCALAR]` na primeira linha + frase de transicao educada.

--- FIM PROMPT B ---

### Workflow manual passo-a-passo

```
1. Mensagem chega no WhatsApp/Instagram
2. Voce copia a mensagem
3. Cola no Claude.ai junto do prompt B
4. Confere a resposta gerada (10-20 segundos)
5. Se OK, copia e cola no WhatsApp/Instagram
6. Se [ESCALAR], avisa o time e passa o atendimento
```

Tempo medio por atendimento: 30 segundos (vs. 2-5 minutos quem responde do zero). E mantem qualidade consistente ate quando voce esta cansado.

---

## Parte C — Atendimento automatico (volume medio/alto)

Apos volume passar de ~30 atendimentos/dia, vale automatizar com webhook.

### Stack tipica

- **WhatsApp**: Z-API (R$ 199/mes, instancia ilimitada) ou WhatsApp Cloud API (Meta — gratis ate 1k conversas/mes)
- **Webhook**: servidor Node/Python que recebe mensagem e chama Claude
- **Claude**: API direta com prompt B

### Codigo starter (Node.js)

--- COMECO PROMPT C ---

Voce e um engenheiro fullstack. Sua missao: criar a integracao WhatsApp + Claude pra atender clientes automaticamente, com escalacao humana quando necessario.

# Stack

- WhatsApp via: {Z-API / WhatsApp Cloud API / outro}
- Backend: Node.js + Express (ou Python + FastAPI — escolha o que faz mais sentido)
- LLM: Claude API (modelo Sonnet, e o ideal pra esse caso)
- Hospedagem: {VPS / Vercel Functions / Railway}

# Comportamento esperado

1. Cliente manda mensagem no WhatsApp
2. Z-API/Meta dispara webhook pro nosso backend
3. Backend:
   a. Carrega historico recente do cliente (ultimas 5-10 mensagens dessa thread)
   b. Monta prompt com:
      - Sistema: o conteudo de `base.md`
      - Historico: ultimas mensagens
      - Atual: a mensagem nova do cliente
   c. Chama Claude API
   d. Se a resposta comeca com `[ESCALAR]`:
      - Manda mensagem no Slack/grupo do time alertando + cole o atendimento
      - Manda mensagem no WhatsApp do cliente avisando que humano vai chamar
      - Marca thread como "humano"
   e. Caso contrario, manda a resposta do Claude pro cliente via Z-API/Meta
4. Salva interacao em banco (Postgres simples ou ate SQLite)

# Variaveis sensiveis (em .env)

```
ZAPI_TOKEN=
ZAPI_INSTANCE=
ANTHROPIC_API_KEY=
SLACK_WEBHOOK_URL=
DATABASE_URL=
```

# Estrutura de arquivos

```
atendimento-bot/
├── src/
│   ├── index.{js|py}              # servidor + webhook
│   ├── claude.{js|py}             # chamadas Claude API
│   ├── whatsapp.{js|py}           # Z-API / Meta integration
│   ├── db.{js|py}                 # historico de conversas
│   └── base.md                    # base de conhecimento
├── .env.example
├── package.json (ou requirements.txt)
├── README.md
└── docker-compose.yml (opcional)
```

# Codigo da chamada ao Claude (referencia)

```javascript
import Anthropic from '@anthropic-ai/sdk'
import fs from 'fs'

const client = new Anthropic()
const baseConhecimento = fs.readFileSync('./src/base.md', 'utf-8')

export async function gerarResposta({ historico, mensagemAtual }) {
  const messages = [
    ...historico.map(h => ({ role: h.role, content: h.content })),
    { role: 'user', content: mensagemAtual }
  ]

  const response = await client.messages.create({
    model: 'claude-sonnet-4-6',
    max_tokens: 600,
    system: `Voce e o atendente. Sua base de conhecimento abaixo:

${baseConhecimento}

Regras:
- Responda no tom da base
- Maximo 4 linhas
- Se nao souber, comece resposta com [ESCALAR]
- Cancelamento/reembolso/reclamacao: [ESCALAR] sempre`,
    messages
  })

  return response.content[0].text
}
```

# O que voce me entrega

1. Codigo completo dos arquivos acima, funcional
2. README com:
   - Como conseguir tokens (Z-API e Anthropic)
   - Como configurar webhook no Z-API/Meta
   - Como testar local com `ngrok`
   - Como deployar (Vercel/Railway/VPS)
3. Plano de teste antes de ir pra producao (5 cenarios: pergunta simples, pergunta nao na base, cliente irritado, cancelamento, ambiguidade)

Faca o trabalho completo. Avise no final o que eu preciso fazer manualmente (criar conta Z-API, etc.).

--- FIM PROMPT C ---

---

## Caso de uso real — Camisa BR

**Antes (Manychat):**
- Plano Pro: R$ 195/mes
- Volume: ~600 mensagens/mes (90% perguntas frequentes — tamanho, prazo, troca)
- Bot respondia 60% bem, 40% caia em "fala com humano"

**Migracao:**
1. Marcelo rodou Parte A — gerou `base.md` em 45 minutos (entrevista guiada)
2. Tentou Parte B (manual) por 2 semanas — gostou
3. Volume justificou Parte C — contratou Z-API (R$ 199/mes), montou webhook + Claude (mais 1 dia de trabalho)

**Depois:**
- Z-API: R$ 199/mes
- Claude API: ~R$ 80/mes (~600 mensagens, custo medio R$ 0,01-0,05 por mensagem)
- Total: R$ 280/mes

**Mas:**
- Manychat era R$ 195
- E agora ele tem **CRM de cliente** (banco de historico que era separado), economia de R$ 60/mes do CRM antigo
- Resposta passou a ser de qualidade muito superior (Claude entende contexto)
- Escalacao humana e mais inteligente (so escala quando faz sentido)

**Economia liquida:** ~R$ -25/mes (gastou um pouquinho mais), **mas qualidade de atendimento subiu drasticamente** + ele ganhou flexibilidade de mexer no comportamento sem mexer em construtor visual.

> Esse e um caso onde **a economia direta nao foi enorme, mas o ganho qualitativo justificou** — vale ver caso a caso.

---

## Quando NAO substituir

| Situacao | Recomendacao |
|---|---|
| Volume > 10k atendimentos/mes 24/7 | Avalia ferramenta com SLA |
| Time de atendimento de 10+ pessoas com fluxos complexos | Plataforma multi-agente |
| Compliance LGPD enterprise (banco, plano de saude) | Fornecedor certificado |
| Cliente exige humano em > 60% dos atendimentos | Ferramenta nao resolve, processo precisa mudar |

## Erros comuns

1. **`base.md` ralo** — atendimento ruim, mesmo com Claude
2. **Esquecer de atualizar a base** quando muda preco/politica — Claude responde errado
3. **Nao testar com 20+ casos antes de ligar webhook** — sai gera situacao chata
4. **Webhook sem fallback humano** — quando Claude nao sabe, cliente nao recebe nada
5. **Nao salvar historico** — Claude perde contexto a cada mensagem, conversa fica robotica

## Checklist de qualidade

Antes de ligar pra producao:

- [ ] `base.md` cobre 90% das perguntas que voce ve hoje
- [ ] Voce testou 20+ mensagens reais (algumas dificeis)
- [ ] Tem fallback `[ESCALAR]` claro
- [ ] Time sabe responder quando cair pra humano
- [ ] Tem log de cada conversa (auditoria)
- [ ] Tem botao manual pra desligar caso de erro grave
