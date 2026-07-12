# Inventário classificado do inbox — triagem 2026-06-12

> Gerado pelo curador (sessão autoresearch) após o Pedro despejar material
> novo. Base: leitura do CONTEÚDO (não dos nomes). Nada foi movido ainda —
> este é o plano de triagem; execução aguarda OK do Pedro nos itens marcados.
> Total: 12 pastas + 4 .md na raiz; ~1.830 arquivos (26 MB só em novo-projeto/).

## Ingerir no cérebro (não-destrutivo, curador executa)

| Item | O que é | Destino |
|---|---|---|
| `C Level Squad/` (6 agentes) | Squad executivo estilo BMAD (vision-chief, caio, cio, cmo, coo, cto). Já instalados em `~/.claude/agents/` (inbox = fonte canônica). | `lab/agents/c-level/` + catalog.tsv (candidate) |
| `00-FLUXO-IMPLEMENTACAO.md` | O protocolo de gates do Pedro validado em 20+ PRs (Etapa 1 read-only → validação → diff → SQL manual). Ouro: é a dor nº 2 do diagnóstico já documentada. | `lab/skills/fluxo-implementacao-3-agentes.md` |
| `skills/` (15 skills, 204 arquivos) | Pack fullstack TS completo (Turbo+Next+Nest+Prisma, DDD) com scripts e templates. Bem-feito. | `lab/skills/fullstack-monorepo/` (pack instalável, formato original) |
| `projeto-instagram/` → só as 6 skills `ig-*` | Lente de viralização + análises de ganchos/retenção/storytelling/vocabulário + perfil de comunicação. Sinergia com personas Ei Risen. | `lab/skills/instagram/` |
| `Super Sec/Archive 2/skills-fim-das-planilhas-1.0/` | Pack de 10 skills de gestão PME (financeiro/estoque/vendas...) + templates CSV. | `lab/skills/fim-das-planilhas/` |
| `CRM Whats/MD .../meta-prompt-gerar-personas.md` | Candidato a skill (geração de persona de tenant). | `lab/skills/` (avaliar vs Fábrica de Arquétipos) |
| `00 - Vieses Cognitivos aplicados ao Design.md` | Resumo do livro "Enviesados" (8 vieses → design de produto). | `knowledge/raw/` |
| `prompts/`, `modulo-autenticacao/`, `modulo-shared/`, `skills-projeto-modulos/` | Matéria-prima do pack fullstack (prompts geradores, iterações). Valor já destilado nas skills. | `knowledge/raw/curso-skills-fullstack-prompts/` (consolidado) |
| Prompts-caixa-rapido + prompts-reduzir-custo (Super Sec/Archive 2) | Material de curso (micro-SaaS do zero; substituir SaaS por Claude Code). | `knowledge/raw/` (consolidados) |

## Tirar do cérebro — pertence aos projetos (aguarda OK do Pedro)

| Item | Por quê | Destino proposto |
|---|---|---|
| `CRM Whats/EUCA/` (xlsx equipe/FAQ/objeções + 10 jpg cartões + personas) | **Dados de cliente real, com dados pessoais.** | `risen-ai-connect/clientes/euca/` |
| `CRM Whats/Construbase/` (3 xlsx) | Dados de cliente. | pasta do tenant no projeto risen |
| `CRM Whats/ID Visual/` (17 png, svg, fontes) | Assets binários; o md diz que o original vive em `/risencrm/prompts/id visual/` (conferir e descartar cópia). | repo risencrm |
| `CRM Whats/MD - Chat Importacao Midia/` (~65 md de sprints) | Histórico de sprints do ai-connect. | `risen-ai-connect/docs/historico-sprints/` |
| `CRM Whats/Arquivos Para Bugs/.../00-FLUXO-RESPOSTA-IA.md` | Runbook do incidente "IA parou" — embrião da skill `/ia-caiu`. | repo ai-connect (runbooks) + base da skill |
| `Super Sec/00-super-secretaria-projeto-base-v3.md` | Spec mestre do SuperSec. | `super-secretaria-functions/docs/` |
| `novo-projeto/` (1.102 arquivos, 26 MB) | Workspace Turborepo GERADO exercitando as skills (cache .next, node_modules). Output, não conhecimento. | `~/Dev/` se quiser continuar; senão descartar (as skills regeneram) |
| `projeto-instagram/` (MCPs, transcrições, análises) | Código/dados de projeto. | `~/Dev/projeto-instagram/` |

## Descartar (duplicatas — aguarda OK do Pedro)

- `Super Sec/Archive 2/57 Agents *` + ~115 zips + `Archive 2.zip` — **byte-idênticos** a `lab/agents/{contabilidade,advocacia}/` (verificado) + cópia congelada em Downloads.
- `00 - Como Executar o Code e Web Juntos.md` e a 3ª cópia em CRM Whats — idênticos ao `00-FLUXO-IMPLEMENTACAO.md`.

## Flags de segurança

- **3 arquivos `.env` no inbox**: 2 em `novo-projeto/`, 1 em `projeto-instagram/resources/mcps/video-transcricao/` (possível key OpenAI). Verificar/limpar antes de mover; nunca commitar.
- Dados pessoais nos xlsx/jpg da EUCA.
- Conflito de nomenclatura "Risen OS": docs do CRM se intitulam "Risen OS", mas ID Visual define Risen OS como projeto separado (barbearias). Pedro decide o nome canônico.

## Ficam no inbox com nota

- `Minha Obra/` e `Risen OS/` — pastas **vazias** (dump falhou?). Perguntar ao Pedro.
- `README.md` — infra do próprio inbox.
