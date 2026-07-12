# eirisen: SUPABASE_ACCESS_TOKEN ROTACIONADO + ledger de conexões no ar

**Pra toda sessão que usa o Supabase da frota via Management API — leia isto.**

## 1. SUPABASE_ACCESS_TOKEN foi ROTACIONADO (2026-07-07 ~20h BRT)

- O token antigo (`sbp_17eb…`) **vazou no chat** de uma sessão (bash -x num script
  que o embutia no curl — erro do Claude, admitido) → Pedro gerou novo e **trocou
  no Bitwarden** (mesmo secret `SUPABASE_ACCESS_TOKEN` de sempre).
- **Quem busca AO VIVO do Bitwarden não sente nada** (validado: já respondendo).
- **Quem tiver o valor antigo cacheado em .env/arquivo/sessão → vai tomar 401.**
  Conserto: parar de cachear e buscar do cofre (regra de ouro).
- Pedro deve ter revogado o antigo no painel; se alguma sessão vir o token velho
  ainda FUNCIONANDO, avisar o Pedro pra revogar já.
- Memória do projeto eirisen `reference_apply_migration_management_api` já foi
  corrigida (não existe mais token em .env.local — é Bitwarden ao vivo).

## 2. Atalho novo: `~/Dev/risen/bin/sb.sh` (instalado/revisado pelo Pedro)

Wrapper allowlisted no Claude Code do eirisen (`.claude/settings.local.json`)
que resolve o atrito de permissões do modo auto (comandos que começavam com
`export BWS...` não casavam com as allow rules):

```
sb.sh deploy <ref> <fn...>      # deploy de edge functions
sb.sh query <ref> <arq.json>    # POST /database/query
sb.sh migrate <ref> <arq.json>  # POST /database/migrations
```
Token sempre ao vivo do Bitwarden, nunca cacheado. Também liberado no allowlist:
`ssh/scp -i ~/.ssh/id_ed25519_evolution` (droplets da frota). Outras sessões da
frota podem reusar o mesmo padrão (o script aceita qualquer project-ref).

## 3. Ledger permanente de conexões WhatsApp + tela /admin/conexoes (NO AR)

- Nasceu da pergunta do Pedro ("esse número já passou pelo sistema antes?") no
  caso Josemac/463: agora TODO evento de conexão (pareou/caiu/motivo) grava
  **número do aparelho** (ownerJid via `sender` do envelope da Evolution — era
  o ponto cego) + **tenant_name snapshot** (sobrevive à remoção do tenant;
  FK tenant mudou CASCADE→SET NULL).
- Tela super-admin `/admin/conexoes`: filtros por número/tenant/instância/
  evento/origem. Sidebar "Conexões".
- Validado em prod 23:17 UTC: Chocodoces e OAB já gravando com número.
- Bônus: webhook agora "sara" `whatsapp_providers.phone_number` (vivia null).
- Commits main: 50c9d2e (freio de envio POR NÚMERO — 1968 da Josemac trancado,
  fixo novo nasce livre) + 5e5b112 (ledger+tela). Migration
  `20260707190000_wce_ledger_permanente` aplicada.

## Josemac (contexto vivo, ver update 2026-07-06_1835)

Instância 1968 despareada pelo Pedro (repouso total, melhor pro 463 soltar);
plano em curso = parear o FIXO da loja e migrar as conversas pra ele (Claude
faz a migração quando o Pedro parear); IA de resposta fica OFF (assistente
só de leitura/sugestão); canário diário no VPS vigia o destravamento do 1968.
