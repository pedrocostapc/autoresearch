# Vocabulário do Pedro — como ele fala e o que ele quer dizer

> Camada compartilhada do cérebro: **toda sessão, em qualquer projeto, carrega isto.**
> É a tradução "Pedro diz X → quer dizer Y" + a forma de conversar com ele.
> Fonte: agregado de arquivos VERIFICADOS do próprio Pedro (não inferência) —
> `risencore/VOCABULARIO-RISEN.md`, `Dev/risen/BRIEFING-CORE.md §2.5/§6/§7`, e
> correções do Pedro na sessão de 2026-06-13. Itens marcados ⚠️ = a confirmar.
>
> **Como referenciar:** o CLAUDE.md de cada projeto deve apontar pra cá
> (`~/Dev/autoresearch/lab/knowledge/vocabulario-pedro.md`).
> **A engenharia de cada sistema NÃO mora aqui** — mora no próprio projeto e é
> espelhada em `lab/knowledge/projects/<slug>.md` (ver fim deste doc).

## Como o Pedro nomeia os sistemas (forma curta, minúscula)
> Fonte: BRIEFING-CORE.md §2.5

- "o core" = **RisenCore** (`hjclvuzugdbpvnomvtpn`) — agregador central estilo Cosmos.
- "o risenos" / "o os" = o **ERP** (newrisenos).
- "ei risen" / "o crm" / "ai-connect" = **WhatsCRM** (eirisen, atendimento WhatsApp por persona).
- "supersec" / "super secretária" = assistente **fiscal/financeiro** por IA.
- "agência" = Risen Agência · "minha obra" e "na fazenda" = os outros dois apps.

## Arquitetura cross-system (quem usa quem)
> Fonte: VOCABULARIO-RISEN.md + BRIEFING-CORE.md §6

- **Core = central, único.** Os SaaS-cliente (RisenOS, Minha Obra, agência, CRM…)
  **consomem o Core via API key**. Comunicação entre sistemas é sempre via Core,
  a nível de tenant.
- **tenant final** = usuário do SaaS-cliente (ex.: Malttis dentro do RisenOS).
  O Core não conhece tenant final, só billing.
- **catálogo mestre** = `risencore_gtin_products` (no Core, universal por GTIN).
  **catálogo local/mirror** = `gtin_cache` (no SaaS-cliente, cópia diária via cron).
  **produto-tenant** = `products` (no SaaS-cliente, com `tenant_id` + `barcode`).
- **provedor** = serviço externo (BlueSoft Cosmos, Focus NFe, Twilio, Cora, Resend) —
  NUNCA confundir com "fonte" interna.
- Fluxo de mudança cross-system: **o provedor (Core) sobe PRIMEIRO**, depois o app consome.

## Termos que o Pedro usa → o que ele quer dizer

- **"caixa"** = um módulo de treino da persona no CRM (tabela `persona_boxes`):
  dado + instrução de uso daquela capacidade; **caixa vazia = capacidade
  desligada → escala, não improvisa**. (Correção do Pedro, 2026-06-13.)
- **"persona"** = a atendente IA configurada por um arquétipo + as caixas do tenant.
- **"arquétipo"** = o molde geral da persona de um setor (regra geral, sem dado do tenant).
- **Exemplo de desambiguação que ele exige da IA:** cliente de construção diz
  "terra" querendo dizer "areia" — são coisas diferentes; a boa atendente
  clarifica antes de responder. (Pedro, 2026-06-13.)
- ⚠️ Outros termos por confirmar com o Pedro conforme aparecem.

## Como o Pedro quer ser atendido (forma de conversa)
> Fonte: correções recorrentes do Pedro (diagnóstico de fricção, verificado nos transcripts)

- **PT-BR sempre.** Nomear ferramenta pela FUNÇÃO, não pela engine ("gerador de
  relatório", não "Haiku"/"Sonnet"). UI e texto sem jargão em inglês.
- Opções de decisão: **lista numerada curta** ou pergunta com setas. Pediu tabela
  → entregue tabela. Exemplo concreto > abstração.
- **NUNCA deixar escopo pela metade** — terminar antes de encerrar. ("você fica
  sempre deixando algo pra trás" é a reclamação nº 1.)
- Instruções pra ele: **item a item, didático, um comando simples por vez** (ele
  não compõe comando de shell; sugerir o prefixo `!`).
- **Não me faça reexplicar** — se já te ensinei, está num arquivo; leia antes de perguntar.

## O que a IA NÃO faz sozinha (autorização — é justo, não contornar)
> Fonte: BRIEFING-CORE.md §7

- Escrita/migration em **produção** (Management API); **delete de função** em prod.
- Desligar auth (`--no-verify-jwt`), garimpar segredo no banco.
- **Deploy de FRONT** (pipeline do Pedro).
- Editar `settings.json` pra se **auto-conceder permissão**.
- **Segredo NUNCA no chat** — Bitwarden via `secrets-sync` (receita em
  `lab/skills/subir-chaves-bitwarden.md`).

## Erros estruturais que o Pedro já apontou (não repetir)
> Fonte: VOCABULARIO-RISEN.md "erros que Claude comete" + BRIEFING-CORE.md §7 + 2026-06-13

- **Não inventar fato sobre um sistema que você não enxerga.** A sessão que conhece
  o sistema alimenta o cérebro; o curador (autoresearch) organiza o verificado.
- Não renomear/inventar nome sem perguntar.
- Não inventar shape de resposta de provedor (payload interno é do provedor, intacto).
- Sandbox às vezes não persiste delete de arquivo — confirmar com `ls`/`git status`.
- `deno check` tem ~10 erros pré-existentes que NÃO são reais — comparar com o HEAD.

## A engenharia de cada sistema (NÃO mora aqui — ponteiros)

Cada sistema mantém a própria engenharia (tabelas/ligações, funções, configs,
fluxo da IA), espelhada em `lab/knowledge/projects/<slug>.md` pelo `lab-sync`:

- **Core** — fonte canônica: `risencore/VOCABULARIO-RISEN.md` (glossário, escopos
  de escrita, padrões de código).
- **CRM (ai-connect)** — `~/.claude/projects/<repo>/memory/project_*.md` (40+ docs
  verificados: credit gates, persona evolution, insights, etc.) + `supabase/config.toml`
  + `supabase/functions/` (70+ funções).
- Demais (SuperSec, RisenOS, Minha Obra) — a preencher pela sessão de cada um.

> ⚠️ O fluxo "como o sistema sabe que é a IA respondendo (vs humano), e quais os
> parâmetros" é a peça que a sessão autoresearch chutou errado em 2026-06-13.
> Ela tem que ser escrita pela sessão do CRM, do código, e marcada como verdade
> só depois disso.
