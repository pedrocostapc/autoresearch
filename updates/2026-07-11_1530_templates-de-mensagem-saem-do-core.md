# Decisão do Pedro: templates de mensagem NÃO vivem no Core — vivem em cada app

**Contexto (Hub/agencia, 11/07):** os templates de WhatsApp do Hub (`cobranca_aluguel`,
`cobranca_outdoor`, `orcamento_outdoor`…) hoje moram no Core (`core_msg_templates`,
broker `templates.msg.list/upsert` — migration `risencore-broker/.../20260708030000_msg_templates_core.sql`).
O Pedro decidiu: **template é dado do TENANT → mora no banco do próprio app**, porque
cada app tem seus usuários/tenants editando seus textos. Core volta a ser só
transporte/processador (regra "Core stateless" do CLAUDE.md raiz).

**O que muda no Hub (em andamento nesta sessão):**
- Tela nova "Mensagens & E-mails": um cartão por template, DUAS colunas
  (texto WhatsApp | texto E-mail — mesmo evento, tom diferente), controles
  compartilhados embaixo (formato PDF/link/ambos + anexos), toggle por canal.
- Tabela local de templates no Hub (com seed copiado do Core); o e-mail do
  boleto (hoje texto fixo no `v1-notify` do Core) passa a aceitar corpo do app.
- Gancho novo: emissão de boleto de ALUGUEL (manual + robô dia 25) passa a
  disparar WhatsApp com o template `cobranca_aluguel` (hoje o template existe
  mas NADA o dispara — só sai e-mail).

**Pra quem mexe no Core:** não criar template novo em `core_msg_templates`;
o `templates.msg.*` do broker vira legado quando o Hub migrar. O `v1-notify`
ganha (ou já tem) suporte a corpo custom vindo do app — manter compatibilidade
com os apps que ainda usam o texto padrão (eirisen, supersec etc.).

**Pra outros apps da frota:** replicar o padrão — templates de
mensagem/e-mail por tenant no banco do app, não no Core.
