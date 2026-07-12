# Diagnóstico de fricção — onde o Pedro perde tempo e repete as mesmas coisas

> Gerado em 2026-06-12 pela sessão autoresearch, a pedido do Pedro ("ver onde
> tenho mais dificuldades, onde sempre tenho que ficar falando a mesma coisa").
> Fonte: mineração de ~2.300 mensagens do Pedro em 13 projetos de Claude Code
> (transcripts completos em `~/.claude/projects/`, 2026-05-12 → 2026-06-12),
> por 4 analistas paralelos. Relatórios brutos por projeto ficaram nos agentes;
> este é o consolidado priorizado.

## O padrão geral

O Pedro opera como **gerente de uma fábrica de Claudes**: define o negócio com
precisão (domínio fiscal BR, regras de tenant, números de SPE), valida
resultado com olho de QA — mas gasta a maior parte das mensagens em **três
papéis que deveriam ser automatizados**:

1. **Carteiro entre sessões** — cola contexto, status-reports e até chaves de
   um Code pro outro; quando esquece, projeto quebra ("ele nem soube dissoo").
2. **Operador de git por procuração** — dita o ritual commit→PR→merge→push→
   deploy toda sessão e cobra do outro lado ("ja esta em main? fez push?").
3. **Fiscal de status** — "rodou? me da o resumo?", "ta funcionando?",
   "voce consultou os agentes?".

A dor dominante **não é técnica, é de protocolo**: autonomia mal contratada,
contexto re-colado à mão, rituais sem automação.

## Top dores (frequência × dor, consolidado dos 4 relatórios)

### 1. Contexto re-explicado toda sessão → CLAUDE.md por repo (a maior alavanca)
Em TODOS os projetos ele re-cola/re-dita: o modelo de deploy ("Lovable só
publica o que está em main" — 4 projetos), refs do Supabase, UUIDs/emails de
tenants ("todos meus clientes hoje sao beta" dito 4+), regras de negócio
(regime de caixa da Risen, CNPJ = fonte da verdade, quem paga o quê),
vocabulário ("o nome do app é Super Sec" 2× seguidas), o protocolo de gates,
e o bloco "Atualização de contexto" do cérebro (colado 4× em 10–11/06).
**Repos sem CLAUDE.md ou com CLAUDE.md incompleto: risen-ai-connect (kernel),
super-secretaria-functions (kernel SuperSec), newrisenos, risencore,
pedro-obras (zero — as "REGRAS OBRIGATÓRIAS" vivem em prompts colados).**

### 2. Ritual git/deploy ditado e cobrado manualmente → skill `/entregar`
As mesmas 6 regras re-declaradas e, quando esquecidas, viram incidente:
diff antes de commit (+OK explícito), `git add` com paths NUNCA `-A`
(incidente real 18/05), branch-check antes de editar, push pós-merge
("Regra nova... Não acumular"), `--no-verify-jwt` no deploy do ai-reply
(causou 401 em produção 2×), cópia de migrations/MDs pra `prompts/`.
Solução: skill de entrega com checklist embutido + hook bloqueando
`git add -A` e commit na main + worktree por sessão (3 incidentes de
trabalho misturado entre sessões paralelas no mesmo checkout).

### 3. Incidente "IA parou de responder" → skill/runbook `/ia-caiu`
**11 ocorrências** entre ai-connect (7) e risencrm (4), incluindo outage de
15h+ em cliente real e o Vanderlei (R$2M/mês) 6h sem resposta. Cada vez o
diagnóstico é reconstruído do zero. A árvore já está mapeada nos transcripts
(ai_logs → system_api_keys → gates do provider-webhook → verify_jwt →
créditos → crons → Evolution). O inbox tem inclusive o runbook embrionário
(`CRM Whats/Arquivos Para Bugs/IA para de responder/00-FLUXO-RESPOSTA-IA.md`).

### 4. Contrato de autonomia mal definido → settings.json + matriz de gates
O pico emocional do corpus: "inferno!!! pra que voce ta perguntando toda
vez????" (SuperSec 09/06) — mas o mesmo Pedro instituiu gates manuais e dá
autorizações em branco ad-hoc que não persistem ("autoriza tudo"). Ele chegou
a tentar extrair de um Code a config de bypass de outro. Solução: allowlist
formal por projeto (`.claude/settings.json`) + matriz explícita no CLAUDE.md:
*auto* (branch, testes, deploy preview) vs *gate* (merge main, migration
destrutiva, gasto novo).

### 5. Segredos colados no chat → ROTACIONAR + concluir Bitwarden
Em claro nos transcripts: SUPABASE_SERVICE_ROLE_KEY, ANTHROPIC_API_KEY
(sk-ant-...), 2+ PATs `sbp_`, token DigitalOcean, token Cloudflare (2×),
tskey Tailscale, chave SSH privada, senha sudo. A centralização no Bitwarden
foi iniciada (10-11/06) mas travou no meio; a rotação fica eternamente
"pendente". **Risco real num produto que guarda dado fiscal de terceiros.**
Regra a fixar em todo CLAUDE.md: segredo nunca no chat — `.env.local`/cofre,
Claude lê do caminho.

### 6. "Consulta a spec primeiro" (REGRA Nº 1 do SuperSec) → skill `consulta-spec`
"A que mais errei" (admissão do próprio Claude): decidir sem consultar os 57
agentes de contabilidade + catálogo de tabelas. O Pedro vira o lembrete
humano ("voce consultou os agentes?... voce tem que consultar"). Os agentes
já têm localização canônica em `lab/agents/contabilidade/` — falta o gatilho.

### 7. Visibilidade do que rodou → status push, não pull
"rodou? me da o resumo?", "montou meu dashboard?", "como sei o que está sendo
trabalhado?" (2× em 24h, gerou a UI do cérebro em 12/06). Complemento que
falta: relatório automático do worker noturno em `updates/` ao fim da janela
+ notificação só quando precisa de decisão dele.

### Fricções de comunicação (baratas de resolver, alto ganho)
- Respostas em PT-BR, nomear ferramenta por FUNÇÃO e não por engine
  ("sonnet é nome de engine. fala a funcao").
- Opções como lista numerada curta; exemplos concretos; tabela quando pedir
  tabela ("voce nao fez tabela").
- Não deixar trabalho pela metade ("voce fica sempre deixando algo pra tras,
  e nunca acaba!") — terminar o escopo antes de encerrar.
- Ele não compõe comandos de shell: nunca pedir pra ele rodar comando
  multi-linha; um comando por vez ou fazer pelo Code.

## O que ele domina (não automatizar, alimentar)

Domínio fiscal/operacional BR, regras de negócio por tenant, olho de QA de
dado real ("esses dados estao errados" no olho), desenho de gates de
segurança, o padrão briefing/handoff que ele inventou sozinho
(BRIEFING-CORE.md, VOCABULARIO-RISEN.md). As melhores correções do corpus
vêm daí — o sistema deve dar a ele dados pra validar, não tarefas de operação.

## Cruzamento com o banco de ativos (inbox + lab + skills-library)

- O inbox que ele acabou de despejar contém **a resposta de várias dores**:
  `00-FLUXO-IMPLEMENTACAO.md` é o protocolo de gates dele já documentado
  (vira skill e seção de CLAUDE.md); `00-FLUXO-RESPOSTA-IA.md` é o embrião
  do runbook `/ia-caiu`; o pack `skills/` (15 skills fullstack) e os 6
  agentes C-Level são material legítimo (C-Level já instalado em
  `~/.claude/agents/`).
- Os 57 agentes de contabilidade atacam a dor #6 (são a spec a consultar).
- Da skills-library (20k), a shortlist de 11/06 já apontou candidatas de
  PDF/WhatsApp/Supabase — mas **nenhuma skill pronta resolve as dores #1-#5;
  todas pedem material próprio** (CLAUDE.mds e skills sob medida). O valor
  do banco externo é tático; o valor estratégico está nos protocolos que o
  próprio Pedro já inventou e que ninguém escreveu em arquivo.

## Plano de ação proposto (ordem de impacto)

1. **CLAUDE.md kernel nos 5 repos** (ai-connect, super-secretaria-functions,
   newrisenos, risencore, pedro-obras): deploy model, refs/IDs canônicos,
   tenants, regras de negócio, protocolo de gates, regras de comunicação,
   regra de segredos, ponte pro cérebro. ~30% das mensagens dele evaporam.
2. **Rotacionar os segredos vazados** + concluir push Bitwarden + regra
   "nunca colar valor no chat" em todo CLAUDE.md.
3. **Skill `/entregar`** (commit→PR→merge→push→deploy com checklist) + hook
   anti `git add -A`/commit-na-main + worktrees para sessões paralelas.
4. **Skill `/ia-caiu`** no ai-connect com a árvore de diagnóstico pronta.
5. **Matriz de autonomia** em settings.json por repo (mata os "inferno!!!").
6. **Status push do worker noturno** (update automático + notificação).
7. Triagem do inbox (inventário em `2026-06-12-inventario-inbox.md`) —
   ingere os packs bons, tira dados de cliente do cérebro, descarta
   duplicatas com OK do Pedro.
