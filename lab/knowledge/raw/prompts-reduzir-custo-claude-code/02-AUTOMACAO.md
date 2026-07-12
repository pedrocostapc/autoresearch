# 02 — Automacao

> Substitui: Zapier, Make (ex-Integromat), n8n cloud, Pipedream, Workato

## Por que substituir

Boa parte das automacoes do Zapier/Make sao **scripts de 30-100 linhas com dois ifs**. Voce paga R$ 100-800/mes pela interface visual + escala de execucoes.

Com Claude Code voce escreve o script em 10 minutos, agenda no cron do seu Mac/servidor, e nunca mais paga.

## Comparativo de custo (Brasil, 2026)

| Ferramenta | Plano popular | Mensal | Limite tipico |
|---|---|---|---|
| Zapier | Pro | US$ 19,99 (~R$ 110) | 750 tasks/mes |
| Zapier | Team | US$ 69 (~R$ 380) | 2.000 tasks |
| Zapier | Company | US$ 103,50 (~R$ 570) | 50.000 tasks |
| Make | Core | US$ 9 (~R$ 50) | 10.000 ops/mes (mas explode com loop) |
| Make | Pro | US$ 16 (~R$ 88) | 10.000 + recursos |
| n8n cloud | Starter | US$ 20 (~R$ 110) | 5.000 execucoes |

vs. **Claude Pro (R$ 110/mes)**: ja inclui Claude Code. O custo marginal de cada execucao e zero (roda no seu Mac/servidor) ou centavos (se via API).

Economia tipica: R$ 100-700/mes = **R$ 1.200-8.400/ano**.

## Volume que cabe

| Volume | Solucao |
|---|---|
| < 100 execucoes/dia | Cron local no seu Mac |
| 100-1000/dia | VPS de R$ 30/mes (Hetzner, Contabo, OracleCloud free) |
| 1000-10000/dia | VPS dedicada + monitoramento |
| 10000+/dia | Avaliar Cloud Functions / Lambdas (custo ainda baixo) |

## Quando NAO substituir

- Voce **nao tem ninguem** que sabe ler script — a manutencao mata
- Voce precisa de **integrador visual** que outras pessoas mexem
- Sua automacao usa app obscuro com plugin pronto SO no Zapier
- Voce precisa de auditoria/log enterprise (Zapier history, ec.)

## A logica deste prompt

Sao **3 partes**:

- **Parte A** — voce roda 1 vez pra cada zap/scenario que vai migrar (gera codigo)
- **Parte B** — agendamento (cron local ou VPS)
- **Parte C** — monitoramento (saber se quebrou)

---

## Parte A — Reescrever a automacao em script

--- COMECO PROMPT A ---

Voce e um engenheiro de automacao. Sua missao: substituir uma automacao que hoje roda em Zapier/Make/n8n por um script local que rode de graca, com qualidade de producao.

# Automacao atual

- Plataforma origem: {Zapier / Make / n8n / outro}
- Numero do zap/scenario: {se voce sabe — pra referencia}
- Gatilho: {ex: "novo email com assunto X", "linha nova na planilha Y", "pagamento Stripe", "novo lead Meta Ads", "horario X todo dia"}
- Acoes (em ordem):
  1. {acao 1}
  2. {acao 2}
  3. ...

- Volume estimado: {X execucoes por dia/semana/mes}
- Onde vai rodar: {meu Mac / VPS / servidor proprio}

# Restricoes

- Linguagem: {Node.js OU Python — escolha a que faz mais sentido pro caso}
- Tem que ter **log estruturado** (cada execucao gera linha em arquivo `logs/automacao-YYYY-MM.log`)
- Tem que ter **try/catch** com notificacao de erro (email/whatsapp/slack — ver dia)
- Tem que ser **idempotente** (rodar 2x nao duplica saida)
- Variaveis sensiveis em `.env`, nunca hardcoded
- Codigo enxuto: 1 arquivo principal de ate 200 linhas. Se passar disso, refatora em modulos

# O que voce me entrega

## 1. Diagnostico
Em 3-5 linhas: essa automacao da pra fazer com script ou realmente precisa de Zapier?
Seja honesto. Casos que precisam Zapier:
- Gatilho de app obscuro sem API publica (raro, mas existe)
- Necessidade de UI pra outras pessoas configurarem
- SLA enterprise

Se da pra script, segue.

## 2. Estrutura de arquivos a criar

```
automacao-{nome}/
├── automacao.{js|py}
├── lib/
│   ├── {modulo1}.{js|py}
│   └── ...
├── .env.example
├── package.json (se Node) ou requirements.txt (se Python)
├── README.md (como rodar e agendar)
├── logs/.gitkeep
└── cron.example
```

## 3. Codigo

Crie cada arquivo com codigo real, comentado SO onde ajuda.

Estrutura tipica do `automacao.{js|py}`:

```
1. Carrega .env
2. Inicializa logger
3. main():
   3.1. Le gatilho (busca novidades desde ultima execucao)
   3.2. Pra cada item:
        - executa acoes em sequencia
        - try/catch
        - registra log
   3.3. Salva timestamp da ultima execucao em arquivo state.json
4. notificaErro(err) se necessario
```

## 4. .env.example

Lista todas as variaveis que vou precisar:

```
GMAIL_TOKEN=
SLACK_WEBHOOK_URL=
NOTION_API_KEY=
...
```

## 5. README.md

Inclui:
- Como instalar dependencias
- Como configurar .env
- Como rodar manualmente uma vez (`npm start` / `python automacao.py`)
- Como ver logs
- Como agendar via cron (linha pronta no `cron.example`)
- Como testar sem mandar pra producao (modo `--dry-run`)
- Como reverter pro Zapier se algo der errado (link do zap antigo)

## 6. Criterios de qualidade

Antes de me entregar, garanta:

- [ ] Codigo roda sem erro em primeiro `npm start` / `python automacao.py` apos seguir o README
- [ ] Erro forcado (ex: token errado) nao deixa o script crashar — captura e loga
- [ ] Modo `--dry-run` mostra o que faria sem executar
- [ ] Idempotencia: rodar 2x seguidas nao duplica nada

Faca o trabalho completo. Crie os arquivos. No final, me liste:

1. O que eu preciso configurar manualmente (criar token, autorizar app, etc.) — passos numerados
2. Como rodar o teste manual primeiro
3. Como agendar quando estiver tudo certo

--- FIM PROMPT A ---

---

## Parte B — Agendamento

### Mac/Linux com cron

Apos o Claude gerar o script, voce agenda no cron:

```bash
crontab -e
```

Cola algo assim (exemplo: roda a cada 5 minutos):

```
*/5 * * * * cd /Users/voce/automacao-{nome} && /usr/local/bin/node automacao.js >> logs/cron.log 2>&1
```

Para agendamentos comuns:

| Frequencia | Linha de cron |
|---|---|
| A cada 5 min | `*/5 * * * *` |
| A cada hora | `0 * * * *` |
| Toda hora cheia (08h-18h) | `0 8-18 * * 1-5` (segunda a sexta) |
| Diario 9h | `0 9 * * *` |
| Diario 9h dias uteis | `0 9 * * 1-5` |
| Toda segunda 8h | `0 8 * * 1` |
| Primeiro dia do mes | `0 9 1 * *` |

### Mac com launchd (alternativa mais robusta)

Cron no Mac tem peculiaridades. Alternativa:

```xml
<!-- ~/Library/LaunchAgents/com.voce.automacao.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.voce.automacao</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/node</string>
        <string>/Users/voce/automacao-{nome}/automacao.js</string>
    </array>
    <key>StartInterval</key>
    <integer>300</integer>  <!-- a cada 300s = 5 min -->
    <key>StandardOutPath</key>
    <string>/Users/voce/automacao-{nome}/logs/launchd.out.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/voce/automacao-{nome}/logs/launchd.err.log</string>
</dict>
</plist>
```

Carrega: `launchctl load ~/Library/LaunchAgents/com.voce.automacao.plist`

### VPS (caso volume justifique)

VPS baratas que valem pra esse uso:

- **Hetzner Cloud**: €4,50/mes (~R$ 27) — VPS 2GB RAM
- **Contabo**: R$ 30/mes — 4GB RAM
- **OracleCloud free tier**: gratis — 1GB RAM (cabe scripts simples)

Setup basico (Ubuntu 22.04):
```bash
ssh root@SEU.IP

# Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs git

# Clona seu repo
git clone https://github.com/voce/automacao-{nome}.git
cd automacao-{nome}
npm install
cp .env.example .env
nano .env  # preenche

# Testa
node automacao.js --dry-run

# Agenda
crontab -e
# adiciona linha do cron
```

---

## Parte C — Monitoramento

Voce precisa saber quando a automacao quebrar. 3 opcoes:

### Opcao 1 — Notificacao por email/whatsapp (simples)

Dentro do script, em caso de erro:

```javascript
// Node.js
async function notificaErro(erro) {
  // Slack webhook (gratis, fácil)
  await fetch(process.env.SLACK_WEBHOOK_URL, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      text: `🚨 Automacao {nome} falhou: ${erro.message}`
    })
  })
}
```

Cria webhook do Slack: https://api.slack.com/messaging/webhooks (gratis).

### Opcao 2 — Healthcheck

Servico gratuito como [healthchecks.io](https://healthchecks.io) (gratis ate 20 checks):

- Voce cria um check pra cada automacao
- Cada execucao bem sucedida bate em `https://hc-ping.com/SEU_UUID`
- Se nao receber ping em N tempo, ele te avisa (email/slack)

### Opcao 3 — Log centralizado (avancado)

Se voce tem 5+ automacoes, vale uma stack de log unificado (Better Stack, Logtail, gratis ate certo volume).

---

## Caso de uso real — Camisa BR

**Antes (Zapier):**

| Zap | Funcao | Custo |
|---|---|---|
| 1 | Nova venda Stripe → mensagem Slack + linha no Notion | 2 tasks/venda |
| 2 | Nova foto no Drive → post Instagram (via Buffer) | 5 tasks/foto |
| 3 | Email com assunto "duvida" → cria tarefa pro Marcelo | 2 tasks/email |
| 4 | Toda segunda 8h → manda relatorio semanal por email | 1 task/semana |

Volume: ~600 tasks/mes. Plano Zapier Pro: **R$ 110/mes**.

**Depois:**

Marcelo rodou Parte A 4 vezes (uma por automacao). Claude Code gerou:

```
~/automacoes/
├── stripe-to-slack/
├── drive-to-instagram/
├── email-to-tarefa/
└── relatorio-semanal/
```

Cada um com cron rodando. Total de migracao: 6 horas em 2 sabados.

**Custo depois:** R$ 0 (Claude Pro ja paga, scripts rodam no Mac do escritorio).

**Economia:** R$ 110/mes = R$ 1.320/ano.

**Bonus inesperado:** ele agora consegue customizar mais — quando quis adicionar logica condicional ("se valor > R$ 1.000, manda alerta especial"), 5 minutos no Claude Code resolveu. No Zapier seria upgrade de plano.

---

## Erros comuns na migracao

1. **Cancelar Zapier antes do script estar estavel** — espera 7 dias rodando paralelo
2. **Esquecer de variaveis sensiveis no .env** — token vaza no Git, problema serio
3. **Nao ter monitoramento** — script quebra, voce so descobre quando perdeu vendas
4. **Tentar migrar TODAS as automacoes no mesmo dia** — 1 por sabado, com calma
5. **Codigo de 800 linhas em 1 arquivo** — refatora em modulos cedo

---

## Templates de automacoes prontas (rode Parte A com esses)

Cole no campo "Acoes" da Parte A:

### Stripe → Slack + Notion
```
Gatilho: novo evento Stripe (charge.succeeded)
Acoes:
  1. Buscar dados do cliente no Stripe
  2. Mandar mensagem no Slack canal #vendas: nome cliente + valor + produto
  3. Adicionar linha numa base Notion (tabela Vendas)
```

### Email → Tarefa
```
Gatilho: novo email no Gmail com label "todo"
Acoes:
  1. Extrair assunto e remetente
  2. Criar card no Trello/Notion/ClickUp
  3. Marcar email com label "processado"
```

### Drive → Backup local
```
Gatilho: a cada 6 horas
Acoes:
  1. Listar arquivos novos na pasta X do Google Drive
  2. Baixar para pasta local Y
  3. Logar nome dos arquivos baixados
```

### Forms → CRM
```
Gatilho: novo envio Google Forms / Typeform
Acoes:
  1. Validar campos obrigatorios
  2. Adicionar linha em clientes.csv (skill controle-clientes)
  3. Mandar email de boas-vindas
  4. Notificar vendedor responsavel
```

### Relatorio diario
```
Gatilho: 18h todo dia util
Acoes:
  1. Rodar dashboard rapido
  2. Salvar saida em arquivo
  3. Mandar pelo Slack/email pro dono
```

---

## Quando o Claude API custa mais que cron local

Se o seu script chama Claude API a cada execucao (ex: classificar email, gerar resumo), some o custo:

```
Custo Claude API ~ R$ 0,30 por 1k tokens entrada + R$ 1,50 por 1k tokens saida (Claude Sonnet)
Tokens tipicos por execucao: 500-2000
Custo por execucao: R$ 0,001 - 0,005

Se sua automacao roda 1000x/dia:
Custo diario: R$ 1-5
Custo mensal: R$ 30-150
```

Ainda muito mais barato que Zapier Team (R$ 380), mas vale conferir antes.
