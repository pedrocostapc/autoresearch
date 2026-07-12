# Ei Risen — log de conexão + fila de avisos (dark launch em curso)

## Entregue (main + prod)
- **Log de conexão** `whatsapp_connection_events` (tenant/instância/número/evento/causa/reason_code/origem/quem-clicou) — tabela + RLS (dono lê o seu, super-admin tudo). Janela "Histórico de conexão" na tela de WhatsApp = TABELA com colunas sempre visíveis.
- Wiring event-driven em `provider-webhook` (connection.update, na hora), `reconcile-instance-status` (poll 5min), `evolution-proxy` (quem clica conectar/desconectar no CRM, com user).
- Regras dos avisos v2 fechadas com Pedro — spec em `risencrm/prompts/tenant-notifications/00-regras-avisos-v2.md` (saldo 2 níveis R$10/R$0, resumo 8h básico+completo, cliente-esperando POR VENDEDOR 11h/16h30, horário comercial opt-in 8-20h, opt-out por "PARAR", 2º número).

## Estado da FILA de avisos (morta desde 11/06)
- Causa: crons `notification-scanner`/`notification-drainer` usavam `current_setting('app.functions_url')` = NULL → timeout. GUC via ALTER DATABASE dá permissão negada (42501) → caminho é hardcodar URL no cron (como reconcile).
- **Scanner cron JÁ consertado** (URL hardcoded) + **interruptor de pausa** `system_config.notifications_paused=true` (dark launch: scanner pausado não produz nada).
- **Drainer cron AINDA quebrado de propósito** — precisa do INTERNAL_FUNCTION_SECRET no comando, e a trava de auto-mode barra "secret na cron.job". Fica pro go-live.

## ⚠️ LIÇÃO (custou tempo hoje)
`supabase functions deploy` lê do checkout ATUAL. Eu editei no worktree `wt-midia-gatilhos` mas rodei o deploy de dentro de `risen-ai-connect` (branch avatares, SEM as mudanças) → deployei código VELHO. O scanner sem-pausa rodou e enfileirou 46 avisos reais (drainer quebrado salvou de blast; deletei os 46). **SEMPRE deployar do worktree que tem o código** (cd no worktree antes do deploy). Bundle certo mostra "Uploading asset: connection-events.ts".

## Falta (com OK do Pedro no portão de prod)
Drainer cron (secret) · templates novos · regras no scanner · setting horário-comercial+UI · opt-out PARAR · 2º número. Tudo fica PAUSADO até Pedro testar no número dele (+5538988161296) e mandar liberar (vira notifications_paused=false).
