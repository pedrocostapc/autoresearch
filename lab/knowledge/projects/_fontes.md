# Onde mora a verdade de cada sistema (índice de docs canônicos)

> Varredura de `~/Dev/risen` em 2026-06-13: 663 `.md` fora de node_modules.
> Este índice aponta para os docs canônicos VERIFICADOS de cada sistema — a
> engenharia já está escrita aí, espalhada. O cérebro NÃO recopia: aponta.
> Quando uma sessão precisar entender um sistema, lê a fonte; quando produzir o
> doc-resumo de engenharia, puxa daqui (não da cabeça do Pedro nem de chute).
> ⚠️ Lista inicial — pode haver mais; ampliar conforme aparecem.

## RisenCore (`risencore`)
- `risencore/VOCABULARIO-RISEN.md` — glossário canônico + escopos de escrita + padrões de código
- `Dev/risen/BRIEFING-CORE.md` — estado, vocabulário do Pedro (§2.5), fluxo cross-system (§6), erros (§7)
- `risencore/docs/integracao-crm-risenos-v1.md` — **como o CRM/RisenOS integram com o Core**
- `risencore/docs/barramento-eventos-v1.md` — barramento de eventos
- `risencore/briefings/_LEIA_PRIMEIRO.md` · `briefings/PLANO-SEGURANCA-2026-06-10.md`
- `risencore/CLAUDE.md` · `risencore/README.md`

## CRM / Ei Risen (`risencrm/risen-ai-connect`)
- `~/.claude/projects/-Users-pedrocosta-Dev-risen-risencrm-risen-ai-connect/memory/` — 40+ `project_*.md`/`feedback_*.md` VERIFICADOS (credit gates, persona evolution, insights, security audit, vocab IA/caixas…)
- `prompts/executados/` — docs de SCHEMA e ENGINE reais: `claude-code-si1-fase1-schema.md`, `si1-fase2-engine.md`, `si1-fase3-ui`, `su8-persona-consolidacao.md`, `00-INSTRUCOES-CLAUDE-CODE.md`, etc.
- `prompts/health-sentinel/00-spec.md` · `prompts/encurtador/*` (encurtador eirisen.link)
- `briefings/*` (sprints, jwt-fix, bug-marathon)
- `supabase/functions/` (70+ edge functions) + `supabase/config.toml` (verify_jwt por função) + migrations
- `risen-ai-connect/CLAUDE.md` · `README.md` · `docs/` · `docs/runbooks/`

## SuperSec (`super-secretaria-functions` + `supersec`)
- `super-secretaria-functions/docs/00-super-secretaria-projeto-base-v3.md` — **spec mestre**
- `supersec/docs/design-handoff.md`
- `super-secretaria-functions/CLAUDE.md` · `README.md`

## RisenOS (`risenos/newrisenos`)
- `newrisenos/CLAUDE.md` · `README.md` · (migrations + functions no repo)

## Minha Obra (`minhaobra/pedro-obras`)
- `minhaobra/pedro-obras/CLAUDE.md` · `README.md`
- `minhaobra/pedro-obras/briefings/*` (hotfix-filtros-obras, pos-hotfix, portal-comprador-manual)

## Na Fazenda (`nafazenda/agrogestao`)
- `nafazenda/agrogestao/README.md` — ⚠️ **subdocumentado: só README, sem CLAUDE.md
  nem docs.** A sessão deste projeto precisa escrever o doc de engenharia.

## Outros
- `saas-erp-whats/prompts/pedidosclaude/*` (eventos Evolution)
- `risenagencia/pixel-perfect-replica/README.md`
- `pdf-engine/` · `ss-functions-pdfengine/` — engine de OCR (READMEs + functions)
- `secrets-sync/README.md` — cofre Bitwarden (receita em `lab/skills/subir-chaves-bitwarden.md`)

## Recência — qual doc vale quando há conflito

Os docs evoluem; o cérebro tem que saber o que é fresco. Regras:
- **Git é a data confiável** (quando a decisão foi commitada). Data de arquivo
  mente após checkout/cópia — só usar como fallback (ex.: a pasta `memory/`,
  que não é git, mas é atualizada toda sessão).
- **Mais novo vence.** Quando dois docs se contradizem, o de commit mais recente
  manda. Ex. real (13/06): CRM `CLAUDE.md` mudou em 30/05, mas a `memory/` foi
  atualizada em 12/06 → a `memory/` é a camada viva; o CLAUDE.md já lag.
- **`README.md` quase sempre é placeholder** (datado de quando o repo nasceu) —
  sinal baixo; não tratar como fonte.
- **Doc antigo = risco:** um briefing de abril pode descrever como era ANTES de
  uma mudança de junho. Ao usar, conferir a data contra mudanças posteriores.
- O `lab-sync` carimba data + commit no topo de cada espelho — a recência fica
  registrada automaticamente a cada sync (não chumbar datas neste índice).

## Como usar (regra do curador)
1. Precisa entender um sistema? **Leia a fonte acima** — não invente, não chute.
2. Vai produzir/atualizar o doc de engenharia de um sistema
   (`lab/knowledge/projects/<slug>.md`)? Quem produz é a **sessão daquele
   sistema**, lendo estas fontes + o código; o curador só espelha o resultado.
3. Cross-system (ex.: o CRM usar o Core): a verdade está em
   `risencore/docs/integracao-crm-risenos-v1.md` e `barramento-eventos-v1.md`.
