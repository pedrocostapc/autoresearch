# Fluxo de Implementação — Risen OS

> Documento descritivo do processo Pedro ↔ Claude (chat) ↔ Claude Code.
> Validado em 20+ PRs ao longo de Sprint Catalog (11 PRs) e Sprint Schedule (6 PRs + 3 hotfixes).
> Zero bugs em produção após esse fluxo.

---

## Princípio central

**Cada um dos 3 agentes tem função clara:**

| Agente | Função | Por quê |
|---|---|---|
| Pedro | Tomador de decisão arquitetural + supervisor humano | Conhece negócio, clientes, restrições reais. Único que pode autorizar mudanças. |
| Claude (chat) | Tech lead remoto — escopo, escrita de prompts, validação técnica, raio-x | Mantém visão de longo prazo, padrões, dependências entre sprints. Sem acesso direto ao código. |
| Claude Code | Implementador no repo | Acesso ao código real. Lê arquivos, escreve diffs, roda testes, mergeia PRs. |

**A regra de ouro:** ninguém pula etapa do outro. Code não age sem Claude validar. Claude não decide sem Pedro aprovar. Pedro não roda SQL/secret sem ver o conteúdo.

---

## Fluxo padrão pra PR grande (Sprint feature, refactor, schema novo)

```
1. Pedro      → decide o que precisa ("preciso de uma caixa pra X")
2. Claude     → escreve prompt detalhado em arquivo MD
3. Pedro      → cola MD pro Claude Code
4. Claude Code → Etapa 1 (investigação)
                 - grep no código
                 - SELECT no banco
                 - reporta findings + decisões pendentes
5. Pedro      → cola resposta do Code de volta no Claude
6. Claude     → valida cada decisão técnica do Code, ajusta, recomenda
                 - se algo está errado, propõe alternativa
                 - se está bom, dá OK
                 - gera mensagem pronta pra Pedro colar
7. Pedro      → cola validação pro Code
8. Claude Code → implementa Etapas 2-N
9. Claude Code → mostra diff resumido
10. Pedro     → cola diff pro Claude
11. Claude    → valida diff conforme prompt original
12. Claude    → dá OK + lista de SQL/secrets pra Pedro rodar manualmente
13. Pedro     → roda migrations/secrets no SQL Editor (queries separadas)
14. Pedro     → confirma com SELECT
15. Claude    → confere output
16. Claude    → autoriza merge + deploy
17. Claude Code → mergeia + deploya + push main
18. Pedro     → testa no painel (smoke teste)
```

## Fluxo simplificado pra PR pequeno (hotfix, bug fix simples)

Quando muda 1-3 arquivos, sem schema novo, sem novo conceito arquitetural:

```
1. Pedro      → reporta bug ou ajuste pequeno
2. Claude     → texto curto direto no chat (sem MD)
3. Pedro      → cola pro Code
4. Claude Code → investiga + propõe fix em 1 só step (sem Etapa 1 formal)
5. Pedro      → cola pro Claude
6. Claude     → valida + autoriza com mensagem pronta
7. Pedro      → cola pro Code
8. Claude Code → aplica + mostra diff
9. Pedro      → cola diff
10. Claude    → autoriza merge
11. Claude Code → mergeia + deploya
12. Pedro     → testa
```

A diferença: pula MD separado + Etapa 1 formal. Apropriado quando escopo está claro pra todos.

---

## Por que sempre tem Etapa 1 em PRs grandes

Code investiga o código real **antes** de codar e reporta findings. Já descobriu bugs invisíveis pelo simples ato de olhar:

| PR | Bug descoberto na Etapa 1 |
|---|---|
| SUF16 | Conflito de tabela `system_config` que já existia |
| Catalog PR9 | Bug retroativo SUF15 — campo `disponivel_pra_delivery` faltando |
| Schedule PR1 | URL `djwt` errada (esm.sh vs deno.land) |
| Bug Excel | State fantasma em 4 componentes, não só 1 |
| URLs legíveis | Slug já tem UNIQUE — sem ALTER necessário |

Sem Etapa 1, esses bugs entrariam em produção. Custo de 5min de leitura prévia evita rollback de horas.

---

## Por que SQL/secret é manual (Pedro roda)

Migrations, ALTER TYPE, secrets, e configurações críticas **não passam por edge ou trigger automático**. Pedro roda no SQL Editor depois de Claude validar o SQL.

Razões:
- Migrations em produção têm impacto irreversível
- Secrets vazam se forem hardcoded em PRs
- Supabase managed bloqueia certos comandos (ex: `ALTER DATABASE postgres SET ...`)
- Pedro vê exatamente o que está rodando antes de aceitar
- Falhas ficam óbvias (não silenciosas)

Queries são **separadas** em blocos individuais, uma por bloco de código. Pedro copia query por query.

---

## Por que Claude (chat) escreve em MD

Prompts complexos vão em arquivo separado em `/mnt/user-data/outputs/` por 3 razões:

1. **Compactação de contexto** — se chat compactar, o MD persiste como referência
2. **Acúmulo organizado** — histórico de prompts vira documentação automática
3. **Editabilidade** — Pedro pode pré-ler, anotar, dividir em partes antes de colar

PRs pequenos podem ficar só no chat (sem MD) porque o ciclo de vida é curto.

---

## Anatomia de um prompt MD bem escrito

Cada prompt detalhado tem:

```
# Título (Sprint + número PR)
> TL;DR + estimativa + branch name

## Contexto
- O que veio antes
- O que esse PR adiciona

## Schema/Arquitetura
- Tabelas novas
- Edges novas
- Tools novas

## Etapa 1 — Confirmações antes de codar
A. Verificações (grep, SQL)
B. Decisões pendentes (A1, A2, ... com recomendações)

## Etapas 2-N — Implementação
- Migration
- Edge
- Hooks
- UI
- Deploy

## Critérios de aceite
- Lista de checkboxes

## Restrições
- O que NÃO fazer

## Pós-merge
- Próximo PR
- Smoke teste
```

Code lê esse formato e produz Etapa 1 sem precisar perguntar muito. Reduz back-and-forth.

---

## Como Claude valida diff

Cada diff entregue pelo Code passa por 5 checks:

1. **Escopo:** mudou só o combinado, não foi além?
2. **Decisões anteriores:** respeitou as decisões da Etapa 1?
3. **Padrões:** seguiu pattern já existente no projeto?
4. **Restrições:** evitou o que estava no "NÃO fazer"?
5. **Build/test:** tsc + vitest + bun build OK?

Se algum falhar, peço ajuste antes de autorizar merge.

---

## Como Pedro testa pós-deploy

Pra cada feature mergeada, Pedro tem um roteiro curto (3-5min) de validação visual:

1. Abre o local relevante no painel
2. Confirma elementos visuais novos
3. Testa interação básica (clica, salva, recarrega)
4. Confirma persistência
5. (Se aplicável) Não-regressão das features anteriores

Quando algo dá errado, Pedro reporta na conversa. Vira novo ciclo (bug fix).

---

## Documentos persistentes

Salvos em `/mnt/user-data/outputs/`:

| Tipo | Função |
|---|---|
| `claude-code-<sprint>-pr<n>.md` | Prompts pra Code (execução) |
| `00-SPRINTS-MASTER-*.md` | Estado geral, retoma após compactação |
| `meta-prompt-gerar-personas.md` | Pra outro Claude (criar personas de tenants) |
| `00-CAIXAS-ESTRUTURA-FINAL.md` | Schema das caixas (referência) |
| `00-FLUXO-IMPLEMENTACAO.md` | Este documento |

---

## Sinais de que o fluxo está sendo respeitado

- ✅ Code reporta Etapa 1 antes de tocar código
- ✅ Pedro vê SQL antes de rodar
- ✅ Claude valida cada decisão técnica do Code
- ✅ Diff é mostrado antes do commit
- ✅ Build + test verdes antes de merge
- ✅ Pedro confirma com SELECT após migration
- ✅ Smoke teste pós-deploy

## Sinais de que algo está pulando etapa

- ❌ Code propõe migration sem investigar conflito
- ❌ Pedro roda SQL sem ver o conteúdo antes
- ❌ Claude autoriza diff sem ler
- ❌ Merge antes de tsc/vitest verde
- ❌ Deploy sem confirmação Pedro
- ❌ Smoke teste pulado

---

## Em resumo

**Funcionou em 20+ PRs porque cada agente respeita o outro.**

Pedro não é tech lead — não precisa entender cada detalhe técnico.
Claude (chat) não é developer — não toca código direto.
Code não é arquiteto — não decide sem instrução.

Cada um faz o que faz melhor. O fluxo permite isso.
