# Notificações — Bloco C fechado (2º número + OTP por slot)

App: **eirisen** (risencrm/saas-erp-whats). Branch `feat/midia-gatilhos` (avança main direto).

## O que fechou hoje
Bloco C parte 2 — o tenant agora cadastra **2 números** de aviso (dono +
sócio/gerente), cada um com botão "Enviar código pro e-mail". Commit `2c36da8`
em `origin/main` (Lovable publica o front).

- **3 RPCs estendidas** (migrations via Management API, já live):
  - `tenant_save_notification_settings(_use_alternate, _alternate_phone, _enabled_templates, _alternate_phone_2 default null, _use_alternate_2 default false)` — salva o 2º nº, invalida `alternate_phone_2_verified_at` se o número muda.
  - `tenant_verify_alternate_phone_otp(_code, _slot int default 1)` — `_slot=2` marca `alternate_phone_2_verified_at`.
  - `tenant_get_notification_settings()` — passou a devolver `use_alternate_phone_2 / alternate_phone_2 / alternate_phone_2_verified_at`.
  - (DROP+CREATE nas 3 porque a assinatura/retorno mudou.)
- **Front:** `useNotificationSettings.ts` (SaveInput+verify com slot) e
  `SettingsNotificationsTab.tsx` (2º campo de telefone + verificação, `saveInput()` unificado). tsc = 0 erros nesse worktree.
- O código sempre vai pro **e-mail do dono** (send-otp é phone-agnóstico); o slot só diz qual número confirmar.

Partes 1 (`960f30f`, envia pros 2 números verificados em notify-tenant-via-channel) e 3 (`f4519f0`, opt-out por "2" por tipo no webhook) já estavam em main+deployed.

## Estado do sistema de avisos (todo o overhaul)
- Blocos B1/B2/B3 + scanner→drainer + Bloco C — **todos em main + deployed**.
- **PAUSA GLOBAL ATIVA**: `system_config.notifications_paused = true`. Nada
  sai até o Pedro mandar "ativa". Dark-launch: testar com o número dele
  (+55 38 98816-1296 = Risen Mídia) antes.

## Pendente (gated no Pedro, não é código)
1. Testar ponta-a-ponta com o número do Pedro.
2. `notifications_paused = false` no go-live (o classifier bloqueou o unpause pra mim; fazer com ele presente).

## Deploy
- Front: Lovable de origin/main (só conferir se pegou `2c36da8`).
- Edge parte 2: **nada a deployar** (é RPC + front). notify-tenant-via-channel (parte 1) já no ar.
- SEMPRE deployar edge do worktree `wt-midia-gatilhos`, nunca do `risen-ai-connect` (incidente do scanner sem pausa).
