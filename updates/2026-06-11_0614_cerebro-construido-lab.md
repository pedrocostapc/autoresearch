# Cérebro construído: lab/ agora é a memória da organização

> Criado: 2026-06-11 06:14 — sessão Claude Code em `/Users/pedrocosta/Dev/autoresearch`

## Diretriz do Pedro nesta sessão

> "preocupa em construir o cérebro. o resto vou fazendo da forma que já venho fazendo."

Divisão de trabalho registrada: **a IA constrói e mantém o cérebro (`lab/`);
o Pedro toca a operação dos produtos.** Está em
`lab/knowledge/wiki/decisoes-ativas.md` (decisão nº 1).

## O que foi construído

1. **`CLAUDE.md` na raiz do autoresearch** — toda sessão nova nesta pasta já
   nasce sabendo: ler `updates/` ao abrir, escrever ao fechar
   (`YYYY-MM-DD_HHMM_<slug>.md`), mapa dos projetos, decisões de custo/git.
   *Sugestão às outras sessões: criar CLAUDE.md equivalente nos seus repos.*
2. **Wiki do cérebro** em `lab/knowledge/wiki/`:
   - `mapa-projetos.md` — estado de Ei Risen, SuperSec, autoresearch, skills-library
   - `padrao-central.md` — gerar→medir→selecionar nas 3 escalas; elo fraco = medição
   - `decisoes-ativas.md` — decisões do Pedro que valem entre sessões
   - `pendencias-globais.md` — página viva consolidando os checklists dos updates.
     **Quem concluir item de lá, marque lá** (não só no próprio update).
3. **114 agentes ingeridos**: os zips de `~/Downloads/57 Agents *` foram
   extraídos para `lab/agents/{contabilidade,advocacia}/` (57+57 subagents
   Claude Code, frontmatter intacto = continuam instaláveis). Ciclo de vida em
   `lab/agents/catalog.tsv` (todos `candidate`). Originais preservados em
   Downloads. 5 agentes existem nos 2 domínios em versões adaptadas distintas.
4. **Primeiro output de curadoria**:
   `lab/knowledge/outputs/2026-06-11-shortlist-skills.md` — candidatas do
   skills.sh por área (PDF/invoice p/ SuperSec, WhatsApp/CRM p/ Ei Risen,
   Supabase, memória p/ o cérebro). **Achado: zero skills Brasil-específicas
   nas 20k** — os 114 agentes próprios são material único; reforça o plano
   `super-secretaria-knowledge`.
5. **Scoring de domínio definido** (`lab/CLAUDE.md`): agentes/skills de
   produto são avaliados por uso real relatado nos `updates/` — se sua sessão
   usar um agente do catálogo e ele funcionar (ou não), diga isso no update;
   o curador converte em promoção/arquivamento.

## Como as outras sessões usam o cérebro

- Precisa de contexto? `lab/knowledge/wiki/` responde antes de perguntar ao Pedro.
- Achou/criou agente, skill, ideia? Jogue em `lab/inbox/` — a triagem normaliza.
- Usou um agente do catálogo? Relate o resultado no seu update.

## Pendências (do cérebro)

- [ ] Curadoria profunda da skills-library quando o download terminar
      (estava em 156/2494 repos às 06:03; retomável: `python3 download_skills.py`)
- [ ] Primeiro health check semanal do lab
- [ ] Avaliar fusão do núcleo comum dos 5 agentes duplicados entre domínios
