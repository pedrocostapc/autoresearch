# Sprint Super-Admin do Ei Risen — CONCLUÍDO (exceto P1b, gated)

Sessão de 07-08/07. Plano revisado por 6 agentes C-Level, executado em 4 pushes
no main (Vercel publicou). Detalhes: `risen-ai-connect/prompts/admin-redesign/`.

## No ar
- **P0**: `admin_audit_log` imutável + 7 triggers de auditoria (system_config,
  gates, credit_policy, api_keys, throttle, tenants.deleted_at, publish de
  archetype_versions) + guard de CI `adminAuditCoverage.test.ts`. Confirmação
  escalonada (`ConfirmBlastDialog`): aprovar evolução com DIFF REAL + nº de
  tenants + digitar "publicar"; markup/câmbio/gates/teto; backfill LGPD com
  motivo OBRIGATÓRIO. Rollback de persona 1 clique. **Pausa global da IA**
  (system_config.ai_globally_paused, ai-reply checa fail-fast — deployado e
  smoke-testado). Carimbo `ai_logs.archetype_version_id` por resposta.
- **P1a**: página **360 do cliente** (`/admin/clientes/:id`): assinatura/saldo,
  consumo+**margem** (alerta >60% do MRR), saúde WA+IA, usuários, ativação de
  trial, timeline de admin, **notas+próximo passo** (`tenant_admin_notes`),
  wa.me. Lista clicável + coluna Margem.
- **P2**: sidebar admin em 4 grupos (Clientes/Operação/IA/Plataforma), renomes
  PT (Dashboard→Financeiro, Notificações→Comunicação, AI Infra→Infra de IA,
  Insights Backfill→Ferramentas) com redirects, página **/admin/auditoria**.
- **P3**: zero stubs na UI, ignored price-checks em tabela compartilhada,
  estados de erro (Clientes/Monitor/envios), paginação no histórico de envios.

## Migrations aplicadas em prod (Management API)
20260708120000_admin_audit_log · 20260708160000_admin_tenant_360 ·
20260708200000_admin_ignored_price_checks

## GATED — não fazer sem o Pedro (regra MOTOR vs INTERFACE, memória nova)
- **P1b impersonação**: premissa caiu — `20260504240000` trancou super fora de
  conversations/messages/contacts DE PROPÓSITO. Reabrir = decisão de RLS dele.
- **P1b ações** (crédito cortesia, pausar IA do tenant, estender trial):
  mutações de produção.
- **set-system-api-key**: NÃO deployar (veto explícito; código de audit está
  no main, inerte).
- ai-reply: não re-deployar sem ele.

## Incidente (resolvido, falso alarme)
"Msg não chegou" pós-deploy = auto-envio do próprio Pedro (mesmo número da
instância). ai-reply são: 0 erros, 1.387 sent no dia.

## Backlog com gatilho (do plano)
Equipe/staff UI (gatilho: cutover Risen Staff), NRR/cohorts (>30 clientes),
canário automatizado, JWT impersonation (suporte não-Pedro), export WORM,
cláusula de suporte nos termos (jurídico), processos COO (revisão semanal do
audit, runbook cliente-em-risco, cadência mensal de preço).
