# Espelho de contexto dos projetos

Cada arquivo aqui é uma **cópia automática** do `CLAUDE.md` (ou `AGENTS.md`) de um
projeto, trazida pelo `lab/bin/lab-sync.sh` rodado pela sessão daquele projeto.

- **Fonte da verdade = o repo do projeto.** Aqui é só espelho — **não editar à mão.**
- Sobrescrito a cada sync (não é histórico; é o estado atual).
- O curador (sessão autoresearch) lê esta pasta ao iniciar para ter a visão geral
  verificada de todos os projetos, sem entrar em cada um nem inventar nada.

Como um projeto entra aqui: o Pedro cola o prompt da skill
`lab/skills/sync-projeto-cerebro.md` na aba daquele projeto; a sessão atualiza o
CLAUDE.md do repo a partir do código e roda o sync.

## Projetos esperados (slug → repo)

| slug | repo |
|---|---|
| ai-connect | ~/Dev/risen/risencrm/risen-ai-connect |
| supersec | ~/Dev/risen/super-secretaria-functions |
| newrisenos | ~/Dev/risen/risenos/newrisenos |
| risencore | ~/Dev/risen/risencore |
| pedro-obras | ~/minhaobra/pedro-obras |
| agrogestao | ~/nafazenda/agrogestao  (⚠️ só README hoje) |
| skills-library | ~/Dev/skills-library |

Auxiliares (mapeados, menor prioridade): saas-erp-whats, risenagencia/pixel-perfect-replica,
pdf-engine / ss-functions-pdfengine, supersec (front do SuperSec).

(ainda vazio — preenche conforme você roda o prompt em cada projeto)
