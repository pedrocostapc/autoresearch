# Ei Risen — sistema de avisos: fila viva + Bloco B completo (PAUSADO)

## No ar (main + prod), TUDO sob pausa global (system_config.notifications_paused=true)
- **Fila consertada** sem senha em DB: scanner cron (URL hardcoded) → scanner, no fim, dispara o drainer server-a-server (INTERNAL_FUNCTION_SECRET do env). Cron quebrado do drainer removido. A PAUSA controla 100% do envio.
- **Bloco B completo** no notification-scanner:
  - B1: instância caiu (só quem tem movimento + horário comercial 8-20 opt-in) · saldo 2 níveis R$10 (saldo_baixo) → R$0 (balance_zero).
  - B2: resumo 8h básico (resumo_basico, grátis, re-engaja CRM-only) / completo (daily_report, com insights) — split por extracts.
  - B3: cliente esperando POR VENDEDOR 11h/16h30 — RPC notification_waiting_by_seller (backlog 1h-18h, agrupa por dono). Fim do fan-out.
- Templates novos (editáveis /admin/notificações): saldo_baixo, resumo_basico, cliente_esperando_vendedor. Migrações: business_hours + Bloco C cols (alternate_phone_2, use_alternate_phone_2, verified_at, notifications_opted_out).
- **Log de conexão** whatsapp_connection_events já event-driven (webhook connection.update + reconcile + evolution-proxy) + janela-tabela na tela de WhatsApp.

## Regras (fechadas com Pedro): prompts/tenant-notifications/00-regras-avisos-v2.md

## Falta pro GO-LIVE (com Pedro presente)
1. Bloco C: notify enviar pros 2 números (refactor do send em loop) + UI do 2º campo/verificação + handler do opt-out "PARAR" no webhook.
2. Testar no número do Pedro (+5538988161296) — despausar pede OK (trava de prod).
3. Liberar geral: update system_config set notifications_paused=false → 7 tenants verificados passam a receber.

## LEMBRETE do dia (custou tempo)
Deploy de edge SEMPRE do worktree que tem o código (não do risen-ai-connect, que estava no branch avatares). Faxina: pasta risen-ai-connect resetada pro main; código que rodava em prod fora do git foi salvo (message-actions, sync-contact-photos, broadcast-send, 6 migrações); avatares/SEO já estavam no main.
