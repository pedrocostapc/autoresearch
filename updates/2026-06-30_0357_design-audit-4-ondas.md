# Auditoria UI/UX — 4 ondas entregues (T1·T3·T6·T2)

Pedro pediu revisitar a UI/UX do sistema todo (auditoria por 4 agentes Sonnet,
backlog em `risencrm/prompts/design-audit/00-backlog.md`) e executar na ordem
"1 3 6 2". Feito hoje, via worktree `wt-midia-gatilhos` → push `feat/midia-gatilhos:main`:

- **T1 Jargão** (de1f669): ~20 telas sem inglês + dicionários DB→PT-BR.
- **T3 Escala** (4599eb7): Contatos "carregar mais"+contador; Financeiro pagina o render.
- **T6 UI morta** (f0f6e67): trocar cartão→portal Stripe (hook useStripePortal); Ficha
  do cliente→ContactDetailPage (Sheet morto removido); dead code do ArchetypeCard.
- **T2 Mobile** (fa56f87): ContactPanel num Sheet (mobile/tablet); rótulo do filtro
  ativo em Tarefas; cards no Financeiro; toggle Kanban/Lista em Negócios.

tsc baseline desse branch = ~180 (não 75). Nada de edge/migration tocado — só front.
Pendente: T4 (nativos→shadcn, window.confirm→AlertDialog), T5 (isDirty), acordeão
Inteligência inchado.
