# Skills.sh → biblioteca local + localização dos 57 agentes

> **Criado:** 2026-06-11 05:59 — sessão Claude Code em `/Users/pedrocosta/Dev/autoresearch`
> **Propósito desta pasta:** `updates/` é o canal de comunicação entre sessões. Cada arquivo = um resumo datado do que foi feito/decidido.

## O que foi pedido

1. Olhar o que tem neste projeto (autoresearch) e o que está sendo conversado nas outras duas sessões do Claude Code.
2. Entender o https://www.skills.sh/ — como filtrar e baixar skills.
3. **Baixar TODAS as skills do skills.sh para ter localmente**, para depois a curadoria organizar.
4. Localizar os 57 agentes "da pasta da supersec".

## Contexto levantado

### Este projeto (autoresearch)
Fork do `karpathy/autoresearch`: agente de IA faz pesquisa autônoma overnight em `train.py` (GPT pequeno, treinos de 5 min, métrica BPB, ~100 experimentos/noite). Sem `.claude/` configurado. Deliberadamente minimalista.

### Sessão Super Sec (`/Users/pedrocosta/Dev/risen/super-secretaria-functions`)
SaaS multi-tenant BR de gestão documental/financeira/fiscal para PMEs. Conversas recentes: extração de PDF (pdfplumber), página super admin com agentes editáveis por UI (migration `20260611040000_super_admin_agentes.sql` — tabela `agent_settings` + `admin_agents_overview()`), busca global conectando pedido → NF → boleto → pagamento, previsão de contas fixas recorrentes.

### Sessão Risen AI Connect (`/Users/pedrocosta/Dev/risen/risencrm/risen-ai-connect`)
Login Google/Apple, publicação na Google Play, centralização de API keys no Bitwarden. Tem registry `agent_prompts` (UI editável, versionada) em `risencrm/prompts/agent-prompts/`.

## Descoberta: onde estão os 57 agentes

**NÃO estão na pasta da supersec.** Lá existem só os 4 workers batch (`worker-agent-1..4`). Os 57 estão em:

- `/Users/pedrocosta/Downloads/57 Agents Contabildiade/` — 57 agentes contábeis (Bravy/ASV Digital), formato subagent do Claude Code (`.md` com frontmatter YAML: name, description, tools, model)
- `/Users/pedrocosta/Downloads/57 Agents advocacia/` — ~58 de advocacia, mesmo formato
- Docs de apoio: `/Users/pedrocosta/Downloads/mapeamento-57-agentes*.md` e `00-super-secretaria-projeto-base-v4.md`

O plano (v4 §6) é virarem o repo `super-secretaria-knowledge` (semver, fixtures, pipeline de aprovação quando muda lei) — **hoje vazio**. ⚠️ **Pendência: mover de Downloads para um repo git antes que se percam.**

## skills.sh — o que é e como usar

Diretório aberto de Agent Skills da Vercel. Skills = pastas com `SKILL.md`, compatíveis com Claude Code, Cursor, etc.

```bash
npx skills find <termo>                          # buscar
npx skills add <owner>/<repo> --skill <nome>     # instalar uma
npx skills add <owner>/<repo> -g                 # global (~/.claude/skills/)
npx skills list / update / remove                # gerenciar
```

No site: filtros por tópico, agente compatível e ranking (All Time / Trending / Hot).

## Download em massa — EM ANDAMENTO

Sitemap do skills.sh enumera **20.000 skills em 2.494 repos GitHub**, ordenadas por ranking.

- **Destino:** `/Users/pedrocosta/Dev/skills-library/`
  - `raw/<owner>/<repo>/<skill>/` — arquivos de cada skill
  - `catalog.tsv` — as 20.000 skills com ranking (insumo da curadoria)
  - `download_skills.py`, `download.log`, `repos_done.txt` — script retomável (rodar de novo continua de onde parou)
- **Método:** 1 chamada de API GitHub por repo (gh autenticado) para mapear SKILL.md + arquivos via raw.githubusercontent, 12 threads, pula arquivos >3MB
- **✅ CONCLUÍDO às 14:38 (11/06):** 2.471 repos baixados, 23 indisponíveis (deletados/privados), **87.409 skills, 536 mil arquivos, 5,4GB**. O total passa muito dos 20k do ranking porque cada repo foi baixado por completo (todas as skills dele, não só as ranqueadas).

## Conexão estratégica

Os 57+58 agentes do Pedro já estão praticamente no formato skills.sh (md + frontmatter). Diferença: subagent (`.claude/agents/nome.md`) vs skill (`.claude/skills/nome/SKILL.md`). Próximo passo natural: a curadoria organiza a biblioteca baixada E converte os 115 agentes próprios para o mesmo padrão → `super-secretaria-knowledge` vira um "skills.sh privado", instalável com `npx skills add` (funciona com repo privado).

## Próximos passos

- [x] Aguardar fim do download — concluído 11/06 14:38
- [ ] Mover `57 Agents Contabildiade` + `57 Agents advocacia` de Downloads para repo git (`super-secretaria-knowledge`)
- [ ] Curadoria: organizar `skills-library/` usando `catalog.tsv` como guia de prioridade
- [ ] Decidir skills globais (`~/.claude/skills/`) vs por projeto (`.claude/skills/`)
