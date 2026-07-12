# UI handoff do SuperSec implementado no front (branch feat/ui-handoff)

> Criado: 2026-06-11 ~18:30 — sessão Claude Code em `super-secretaria-functions`
> (trabalho feito no repo **supersec**, o front)

## Contexto

Pedro montou no claude.ai um pacote de handoff de design (`~/Downloads/handoff`):
README com tokens/telas/padrões + protótipo interativo (HTML/JSX) + docs/base.
A tese: app copy-paste-first (átomo CopyCell), prazo é a hierarquia, competência
é o objeto, imposto é a angústia nº 1. Papel quente, Instrument Serif + Geist +
JetBrains Mono, sem branco puro, sem emoji.

## O que foi feito (5 commits no branch `feat/ui-handoff` do supersec)

1. `558511d` — pacote handoff/ versionado no repo (referência canônica do design).
2. `4c65575` — fundação: tokens ss-* no styles.css (Tailwind v4; shadcn vars
   remapeadas → re-skin global de TODAS as telas pro papel quente), fontes no
   __root, `--ss-accent` por tenant, componentes `src/components/ss/` (SSIcon,
   CopyCell, toast event-driven, SSOverline/Chip/Confidence/Wordmark), sidebar
   nova, **/hoje** reconstruída (régua de prazos com ledger+tax_guides reais,
   fechamento da competência, pra-você-agora, imposto herói, entrou-hoje por canal).
3. `aff37ad` — **/financeiro** = Fila de liquidação (card focado, linha digitável
   gigante, C/P teclado, guias aprovadas na mesma fila, "Semana paga." vazio) e
   **/notas** = split list+painel de cópia campo a campo (chave 44 wide, itens
   nunca em linha única).
4. `2dfe11c` — **/fiscal** = Impostos com confronto REAL (guia extracted do PDF ×
   calculada do apurador, pareadas por competência+tipo), memória de cálculo,
   posição na faixa do Simples, questionamento pronto pro contador; **/conciliacao**
   em 3 baldes (sugestões lado a lado, sem-match, conciliados) com progresso.
5. `9a5d806` — **/revisar** restyled (confiança, motivo, canal; gate por campo
   fica pro próximo bloco — precisa plumbing extracted_fields).

## Princípios seguidos

- Dado 100% real (hoje_resumo, ledger, tax_guides, documents.source,
  reconciliations) — zero número inventado; onde falta dado, a UI diz que falta.
- Funcionalidade existente preservada (modo teclado, proveniência, recorrências,
  previsão de fixas, aprovação humana de guia).
- tsc + eslint + vite build verdes em todos os commits.

## Pendências / próximos blocos

- **Gate do Pedro**: branch NÃO foi pushed (workflow: aprovação antes de push).
  Validar visualmente (bun dev) — em especial o re-skin global das telas antigas
  (login, onboarding, documentos, admin herdam o papel quente via shadcn vars).
- Telas restantes do handoff (§4.6–4.7): modo balcão, pastas, relatórios,
  módulos, parte/pessoa, onboarding, portal do contador, admin.
- Revisão por CAMPO (0.95 fiscal) + fila de remetentes WhatsApp.
- Tipografia: fontes via Google Fonts CDN — se quiser self-host depois, trocar.

## Caminhos

- Repo: `~/Dev/risen/supersec`, branch `feat/ui-handoff` (local)
- Design de referência: `supersec/handoff/` (README_HANDOFF.md + PROTOTIPO/)
- Componentes novos: `supersec/src/components/ss/`

## ADENDO (~19:30) — handoff COMPLETO

Pedro pediu as telas restantes. Feito via 5 subagentes paralelos + balcão na mão:
commit `d007079` cobre pastas, relatórios, módulos, parte/pessoa, cadastros
(fornecedores/clientes/funcionários), documentos + doc/:id (+ dialog/dashboard/
dropzone), login/signup, configurações, admin, e o **modo balcão** (§4.6: painel
dock com busca federada + CopyCells, topbar desktop com ⌘K e toggle; layout
agora tem scroll interno h-dvh). Sem dado inventado; funcionalidade preservada;
tsc/lint/build verdes. Fora do escopo restante: onboarding wizard (herda o
papel quente, redesign do fluxo fica pra depois), portal do contador
(subdomínio, não existe ainda), revisão por campo (extracted_fields).
Branch `feat/ui-handoff` segue local aguardando gate do Pedro.
