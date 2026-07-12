# Mapa dos projetos

> Wiki do cérebro. Mantida pela IA; o humano não edita. Atualizada: 2026-06-11 (tarde).
> Fontes: `updates/2026-06-11_*` (5 resumos) + memória de sessão da fábrica.

**Pontes:** desde 2026-06-11, SuperSec e risen-ai-connect têm seção "cérebro"
nos seus CLAUDE.md (criado no SuperSec; adicionada no ai-connect). Convenção:
todo projeto novo ganha a ponte — copiar a seção do CLAUDE.md do ai-connect.

## Visão de conjunto

Pedro opera dois produtos SaaS e usa este repo (autoresearch + `lab/`) como
**cérebro**: memória organizacional, curadoria de agentes/skills e síntese de
conhecimento entre as sessões paralelas de Claude Code.

| Projeto | Caminho | O que é |
|---|---|---|
| Ei Risen CRM / risen-ai-connect | `~/Dev/risen/risencrm/risen-ai-connect` | CRM com atendimento por personas no WhatsApp |
| SuperSec | `~/Dev/risen/super-secretaria-functions` | SaaS multi-tenant de gestão documental/financeira/fiscal para PMEs |
| autoresearch (este repo) | `~/Dev/autoresearch` | Fork do karpathy/autoresearch + `lab/` (o cérebro) |
| skills-library | `~/Dev/skills-library` | Espelho local das 20k skills do skills.sh (`catalog.tsv` = ranking) |

## Ei Risen — estado

- **Fábrica de Arquétipos** em `risencrm/risen-ai-connect/prompts/archetype-factory/`:
  pipeline taxonomia → template-ouro → geração → portão de qualidade → seed.
  Meta: ~85 setores × 2 estilos (`acolhedora` ref. Feijoada, `direta` ref.
  Betinho) ≈ 170 personas.
- **Lote 1 APLICADO no banco eirisen (2026-06-11):** 20 setores × 2 estilos =
  40 versões v1 com `is_published=false` (changelog "v1 — fábrica de
  arquétipos, lote 1"). Aguarda Pedro publicar no admin + testar no
  persona-simulator. Lote 2 = resto da taxonomia.
- **Acesso a dados eirisen:** leitura via `Dev/risen/risen-read.sh <projeto> "<SELECT>"`;
  escrita via Management API (token em `Dev/risen/.env.local`), sempre
  mostro→valida→aplica com aprovação do Pedro.
- **persona-evolution** já roda em produção (cron dom 04:00); falta fechar a
  medição (metrics_before/after vazias) — é o "val_bpb das personas".
- Catálogo atual: 11 categorias, 22 variações, 10 publicadas, todas as
  variações `padrao` vazias.

## SuperSec — estado

- Recentes: extração de PDF (pdfplumber), página super admin com agentes
  editáveis por UI (tabela `agent_settings`), busca global pedido→NF→boleto→
  pagamento, previsão de contas fixas.
- **114 agentes de domínio** (57 contabilidade + 57 advocacia, Bravy/ASV
  Digital): localização canônica é `lab/agents/{contabilidade,advocacia}/`
  (catálogo: `lab/agents/catalog.tsv`); `~/Downloads/57 Agents *` são cópias
  congeladas dos originais. O CLAUDE.md do SuperSec aponta para cá e ensina o
  uso (copiar para `.claude/agents/` e relatar resultado nos updates).
  Destino planejado: repo `super-secretaria-knowledge` (ainda não existe).

## autoresearch — estado

- Nenhuma rodada noturna executada (sem GPU nesta máquina; `prepare.py` nunca
  rodou). `program.md` modificado localmente (seção "The lab") — manter em
  branch própria antes de pull do upstream.
