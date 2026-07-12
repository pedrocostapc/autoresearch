# changelog

Curator memory. Newest entries at the top. Each entry: date, action, items affected.

## 2026-06-11

- **Wiki sync (~13h)** após sessão das pontes + lote 1 da fábrica:
  mapa-projetos (lote 1 aplicado: 40 personas v1 não publicadas; agentes
  canônicos em lab/agents/; pontes CLAUDE.md no SuperSec e ai-connect),
  decisoes-ativas (+ nº 8 ponte obrigatória, nº 9 mostro→valida→aplica no
  banco eirisen), pendencias-globais (seed superado pelo lote 1; nova ação
  Pedro: publicar lote 1 no admin). Nota de processo: a sessão do lote 1
  registrou só em memória, não em updates/ — o sync veio da memória.
- **Brain build (Pedro: "preocupa em construir o cérebro")**:
  - Scope of lab/ broadened: brain of the whole org, two scoring tracks
    (research = val_bpb; domain = real use via ../updates/). CLAUDE.md updated.
  - Ingested 114 Claude Code subagents (57 contabilidade + 57 advocacia,
    Bravy/ASV Digital) from ~/Downloads zips into `agents/{contabilidade,advocacia}/`,
    all `candidate` in new `agents/catalog.tsv`. Pack READMEs → `knowledge/raw/`.
    5 names exist in both domains as different, domain-adapted versions — kept both.
  - Wiki seeded: mapa-projetos, padrao-central, decisoes-ativas,
    pendencias-globais (sources: ../updates/2026-06-11_*).
  - First curation output: `knowledge/outputs/2026-06-11-shortlist-skills.md`
    from skills-library catalog.tsv. Key finding: zero Brazil-specific skills
    in the 20k directory — the 114 own agents are unique material.
- Lab initialized: folder structure, CLAUDE.md schema, empty scoreboard.

## 2026-06-11 ~13h10 (sessão worker noturno)

- Pedro decidiu pôr o desktop do escritório (DESKTOP-8H46QNV: Ryzen 9 5900XT,
  24 GB, RTX 3060 Ti 8 GB, Windows) para trabalhar fora do expediente via
  Tailscale (convite gerado). Escrito
  `knowledge/outputs/playbook-worker-noturno-desktop.md` (Tailscale + OpenSSH
  + WSL2/CUDA + janela 19h–6h30 via Task Scheduler). Carga noturna ainda não
  decidida: OCR SuperSec (Paddle CUDA) vs loop autoresearch. Pendências
  espelhadas em wiki/pendencias-globais.md.

## 2026-06-11 ~19h (sessão worker noturno, parte 2)

- ACESSO FECHADO: `ssh desktop-wsl` (alias no Mac → risen@100.83.140.76,
  Tailscale SSH). GPU + torch/cuda verificados por dentro. ACL do tailnet
  ssh check→accept e auth key feitos via API com aprovação do Pedro.
  OpenSSH nativo do Windows abandonado (bug de localização PT-BR).
  Detalhes/armadilhas: playbook-worker-noturno-desktop.md (atualizado) e
  ../updates/2026-06-11_1905_acesso-desktop-wsl-fechado.md.
- Pendente: carga noturna real (job.sh é placeholder) e revogação da API key.

## 2026-06-11 ~21h50 (sessão worker noturno, parte 3 — implantação)

- Gatilho: cliente novo no SuperSec com ~20k arquivos → prioridade invertida
  p/ OCR-GPU primeiro. TUDO implantado por SSH a partir do Mac:
  - pdf-engine GPU no desktop-wsl (systemd, paddlepaddle-gpu cu126,
    PADDLE_DEVICE=gpu). /ocr testado: conf 94,6, engine=paddle.
  - Funnel público https://desktop-wsl.tail4f0062.ts.net (ACL nodeAttr
    aprovado pelo Pedro) + fleet-status v3 deployada (aprovado) — desktop
    ONLINE no dashboard /admin do SuperSec.
  - Despachante ~/night/job.sh (fila>treino, histerese 100/20, QUEUE_OVERRIDE
    manual até existir queue-status).
  - Branch gpu-3060ti-8gb no fork (DEPTH 4, seq 512, vocab 4096, TinyStories
    via prepare_tinystories.py) clonado em ~/autoresearch; smoke test em tmux.
- Detalhes e pendências: ../updates/2026-06-11_2145_desktop-gpu-implantado.md

## 2026-06-12 ~13h30 (worker noturno, parte 4 — robustez + tetos)

- A 1ª noite (11→12) NÃO treinou: WSL-KeepAlive só com gatilho AtStartup
  nunca rodou (sem reboot). Sessão do desktop consertou (gatilho de tempo
  5min + vmIdleTimeout=-1). WSL agora resiliente e auto-curável.
- SSH admin do Windows destravado via chave desktop-recovery (alias
  desktop-win no Mac; procedência confirmada pelo Pedro + fingerprint).
  Independe do WSL — rede de segurança real.
- Tetos diurnos instalados: GPU-PowerCap-Day 07h/130W, Night 19h/200W
  (Task Scheduler). -pl 130 já aplicado (expediente).
- Despachante relançado capado. job.sh É o despachante (placeholder no
  backup). Detalhes: ../updates/2026-06-11_2145_desktop-gpu-implantado.md

## 2026-06-12 ~16h15 (worker noturno, parte 5 — robustez final)

- Treino morria a cada ~5min: WSL desligava (vmIdleTimeout não honrado).
  Conserto definitivo: tarefa WSL-Holder (wsl-holder.cmd, loop sleep
  infinity, reconecta em 5s). VERIFICADO: serviço estável, GPU 99% sustentada,
  experimentos completando (val_bpb avançando). + GPU-PowerCap-Auto/15min
  (driver reset revertia o teto p/ 220W). Treino contínuo de verdade agora.

## 2026-06-12 ~16h40 (sessão autoresearch — UI do cérebro)

- Criada `lab/ui/` — interface web local para o Pedro acessar o cérebro:
  `server.py` (stdlib puro, zero dependências) + `index.html`.
  Subir: `python3 lab/ui/server.py` → http://localhost:8765.
  Lê lab/ e updates/ ao vivo; única escrita permitida é marcar/desmarcar
  checkbox em wiki/pendencias-globais.md (grava com data, convenção da página).
  Seções: visão geral, pendências (interativas), decisões, updates, wiki,
  agentes (catálogo filtrável + leitura), skills, scoreboard, changelog.
  Detalhes: ../updates/2026-06-12_1640_ui-cerebro.md

## 2026-06-12 ~17h45 (sessão autoresearch — diagnóstico de fricção + inventário do inbox)

- **Mineração dos transcripts**: ~2.300 mensagens do Pedro em 13 projetos
  (~/.claude/projects/, 12/05→12/06) analisadas por 4 agentes paralelos.
  Consolidado priorizado em `knowledge/outputs/2026-06-12-diagnostico-friccao.md`.
  Top dores: contexto re-colado (CLAUDE.md faltando em 5 repos), ritual git
  ditado toda sessão, incidente "IA parou" reconstruído 11×, autonomia mal
  contratada, segredos colados no chat (ROTACIONAR), regra-nº-1 sem gatilho,
  visibilidade pull em vez de push.
- **Inbox inventariado** (Pedro despejou ~1.830 arquivos): plano completo em
  `knowledge/outputs/2026-06-12-inventario-inbox.md`. Ingestões propostas:
  6 agentes C-Level, skill fluxo-implementacao, packs fullstack (15) /
  instagram (6) / fim-das-planilhas (10), referências p/ raw/. Saídas
  propostas (aguardam OK): dados de cliente EUCA/Construbase, ID Visual,
  novo-projeto (26MB de build), duplicatas dos 114 agentes. Flags: 3 .env
  no inbox, pastas vazias "Minha Obra" e "Risen OS".
- Corpus extraído fica em /tmp/pain-mining/ (efêmero; regenerável pelo
  script no update desta sessão).

## 2026-06-12 ~18h (sessão autoresearch — triagem do inbox EXECUTADA)

- Com OK do Pedro (apagar duplicatas/novo-projeto; mover dados pros repos):
  - **Ingerido**: agents/c-level/ (6, no catalog.tsv); skills/
    fluxo-implementacao-3-agentes.md, meta-prompt-gerar-personas.md,
    subir-chaves-bitwarden.md (novo, destilado do secrets-sync);
    packs skills/fullstack-monorepo/ (15), skills/instagram/ (6 ig-*),
    skills/fim-das-planilhas/ (10); knowledge/raw/ ganhou enviesados-...,
    curso-skills-fullstack-prompts/, prompts-caixa-rapido/,
    prompts-reduzir-custo-claude-code/.
  - **Movido pros donos**: EUCA + Construbase → risen-ai-connect/clientes/;
    65 md de sprints → risen-ai-connect/docs/historico-sprints/; runbook
    IA-parou → risen-ai-connect/docs/runbooks/; md de identidade visual →
    risencrm/prompts/ID Visual/; spec v3 → super-secretaria-functions/docs/;
    projeto-instagram (MCPs/dados) → ~/Dev/projeto-instagram/.
  - **Apagado**: novo-projeto/ (26MB build; .env só localhost), Archive 2
    (114 agentes duplicados + zips), binários ID Visual (byte-idênticos ao
    risencrm), 2 cópias do FLUXO-IMPLEMENTACAO.
  - Inbox: vazio (ficam README + "Minha Obra"/"Risen OS" vazias — Pedro não
    sabe origem; aguardam conteúdo).
- Bitwarden: pipeline secrets-sync conferido e PRONTO pra subir mais chaves
  (token no Keychain; skill subir-chaves-bitwarden documenta o passo a passo).

## 2026-06-12 ~18h20 (sessão autoresearch — CLAUDE.md kernel nos 5 repos)

- Item nº 1 do plano de fricção executado: risen-ai-connect (+deploy model,
  fatos operacionais, sessões paralelas, comunicação, segredos),
  super-secretaria-functions (+REGRA Nº 1, raw-100%, CNPJ/regime de caixa,
  naming, frota, fechar-sprint), newrisenos (NOVO), pedro-obras (NOVO, com
  as REGRAS OBRIGATÓRIAS que viviam em prompts), risencore (+comunicação/
  segredos). Fonte dos fatos: diagnóstico de fricção 12/06.

## 2026-06-12 ~18h40 (sessão autoresearch — UI do cérebro virou site na tailnet)

- Com OK do Pedro: launchd `com.pedro.cerebro-ui` (UI sobe com o Mac e
  reinicia se cair; log em /tmp/cerebro-ui.log) + `tailscale serve` →
  https://pedros-mac-mini.tail4f0062.ts.net (SOMENTE tailnet; HTTP 200
  verificado). Vercel descartado: dados vivem no Mac e têm info interna.
  Celular: instalar app Tailscale + login risenmidia. Obs.: o próprio Mac
  mini está com DNS do Tailscale desativado localmente (nome não resolve
  daqui; irrelevante pro uso, localhost funciona).

## 2026-06-13 ~17h (sessão autoresearch — análise de persona do CRM APAGADA)

- A análise de personas/conversas do CRM que esta sessão fez em 12-13/06
  (piloto, leitura "100%", régua, 17 boletins, linhas de persona) foi APAGADA
  a pedido do Pedro. Motivo: baseada em entendimento ERRADO do CRM — esta
  sessão não conhece o sistema e tirou conclusões que o Pedro teve que
  corrigir o tempo todo. NÃO registrar mecânica do CRM aqui (também pode
  estar errada).
- LIÇÃO DE GOVERNANÇA (verificada pelo Pedro): a sessão autoresearch (curador)
  NÃO alimenta o cérebro com fatos sobre o CRM — não conhece o sistema. Quem
  alimenta cada domínio é a fonte que sabe a verdade dele (sessão dona do
  sistema / o Pedro), sempre verificado. Curador organiza o verificado, não
  inventa.
- Removidos: outputs/conversas-reais/, outputs/2026-06-12-piloto-treino-personas.md,
  wiki/regua-atendimento-persona.md, updates de persona (1950, 2110, 0613_1130),
  todas as linhas de persona do scoreboard, dados de cliente em /tmp.

## 2026-06-13 ~19h (sessão autoresearch — mecanismo de sync de contexto dos projetos)

- A pedido do Pedro: cada projeto mantém seu próprio CLAUDE.md atualizado A
  PARTIR DO CÓDIGO (pela sessão dona) e manda cópia pro cérebro. Construído
  o LADO DO CÉREBRO (que é meu; não escrevo fato de projeto):
  - `lab/bin/lab-sync.sh <slug>` — copia o CLAUDE.md/AGENTS.md do repo atual
    para `lab/knowledge/projects/<slug>.md` (cabeçalho data+commit; zero IA).
    Smoke test ok.
  - `lab/knowledge/projects/` — espelho vivo (sobrescrito; NÃO é inbox). Índice
    em `_index.md` com o mapa slug→repo.
  - `lab/skills/sync-projeto-cerebro.md` (status active) — contém o PROMPT
    pronto pro Pedro colar na aba de cada projeto; manda a sessão atualizar o
    CLAUDE.md do código (marcando "⚠️ A CONFIRMAR" o que não dá pra verificar)
    e rodar o sync.
  - `lab/CLAUDE.md`: curador agora lê `knowledge/projects/*.md` ao iniciar;
    regra dura registrada (curador não inventa fato de projeto que não enxerga).
