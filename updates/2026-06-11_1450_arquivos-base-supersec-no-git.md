# Arquivos-base do SuperSec versionados no GitHub (fonte da verdade tem backup)

> Criado: 2026-06-11 ~14:50 — sessão Claude Code em `super-secretaria-functions`

## O que foi pedido

Pedro: subir `/Volumes/HD Mac Mini M4/Dropbox/Prompts/SuperSec Arqvuios Base`
pro GitHub, numa pasta que ele pudesse mandar o "claude design" (conector do
GitHub no claude.ai) baixar e ler.

## Contexto que motivou

No começo da sessão eu havia apontado que a Spec V4 / "57 agentes" / catálogos
não estavam em git em lugar nenhum — só viviam no Dropbox/Downloads, sem backup.
Bate com a pendência da wiki: *"Criar repo super-secretaria-knowledge … nada
disso está em git ainda"*.

## Decisões do Pedro (perguntei antes)

- **Destino:** pasta `docs/base/` no repo existente `super-secretaria-functions`
  (não criou o repo dedicado `super-secretaria-knowledge` ainda — fica pra depois).
- **Visibilidade:** privado. O repo já era privado (`isPrivate: true`), então o
  conteúdo nasce protegido. Esclarecido ao Pedro que merge pra main NÃO torna
  nada público — visibilidade é do repo, não do branch.

## O que foi feito

- Copiado via rsync, excluindo `.DS_Store` e a pasta duplicada
  `52-abertura-empresa-cnpj 2/`. Resultado: **122 arquivos, ~1,4 MB**.
- Conteúdo: spec V4 (`00-...-v4.md`, 144 KB) + v3/v3.1 histórico,
  `mapeamento-57-agentes*.md`, `catalogo-extracao-schema-parte-{1,2}.md`,
  `C Level Squad/` (6 execs), subpastas `06-`…`57-` (um agente/processo cada),
  e um `README.md` índice novo orientando a leitura (V4 → 57 agentes → catálogos).
- Push direto na main foi BLOQUEADO pelo gate de workflow (correto) → segui por
  branch `docs/base-arquivos` + **PR #5**, que o Pedro aprovou e eu mergeei
  (`--delete-branch`). Main local sincronizada.

## Como o "claude design" lê

claude.ai → conector GitHub em `pedrocostapc/super-secretaria-functions`
(privado) → ler `docs/base/`. O conector indexa o branch padrão (main), por
isso precisou do merge.

## Caminhos

- Repo: `pedrocostapc/super-secretaria-functions`, pasta `docs/base/`
- Merge: commit `db832ee` (PR #5), conteúdo em `adc0f45`
- Origem (intacta): `Dropbox/Prompts/SuperSec Arqvuios Base`

## Relevância cruzada / pendências

- Atualiza a pendência da wiki: a base AGORA tem backup em git (privado). O repo
  dedicado `super-secretaria-knowledge` (plano v4 §6) continua não-criado — esta
  pasta é um snapshot versionado, não o repo canônico com semver/fixtures.
- A localização canônica VIVA dos agentes (ciclo de vida + scoring) segue sendo
  o cérebro `~/Dev/autoresearch/lab/agents/` + `catalog.tsv`. `docs/base/` é
  cópia-snapshot da fonte original do Dropbox, não substitui o lab.
