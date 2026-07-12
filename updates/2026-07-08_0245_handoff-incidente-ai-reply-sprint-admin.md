# HANDOFF — o que a sessão do sprint Super-Admin colocou em produção (08/07 ~02:00-02:40 BRT)

Contexto: Pedro reportou "teste de mensagem não chegou" (~02:35 BRT) logo após o
deploy do ai-reply. Este doc lista TUDO que mudou em prod, como diagnosticar e
como reverter. Escrito pra outra sessão do Claude Code resolver.

## 1. O que está em produção AGORA

### a) Edge `ai-reply` — DEPLOYADA hoje ~02:20 BRT (única edge deployada)
Código = commit `835dc58` do main. Diff completo vs anterior:
`git show 835dc58 -- supabase/functions/ai-reply/index.ts supabase/functions/_shared/ai-config.ts`

Exatamente 3 mudanças:
1. **Check de pausa global** logo após a validação de `tenant_id`/`messages`
   (~linha 230): SELECT de `system_config.ai_globally_paused`
   (id `00000000-...-0001`, maybeSingle). Se `true` → retorna
   `{suppressed:true, reason:"ai_globally_paused"}` 200. Se `false`/null/erro
   → segue normal. **Default da coluna é false** (verificado ao aplicar).
2. **`resolveArchetypePromptMeta`** em `_shared/ai-config.ts`: mesma lógica do
   antigo `resolveArchetypePrompt` (que virou wrapper), só devolve também o
   `id` da versão. ai-reply linha ~450 usa a nova e guarda `archetypeVersionId`.
3. **`archetype_version_id`** adicionado nos 4 INSERTs de `ai_logs` com
   `operation: "reply_suggestion"` (linhas ~843, ~907, ~1072, ~1158). A coluna
   existe em prod (migration aplicada e verificada).

⚠️ ATENÇÃO: o deploy bundla `_shared/` inteiro do working tree. O working tree
estava limpo (tudo commitado) EXCETO `.env`. Mas o deploy também levou TODAS as
mudanças de ai-reply/_shared commitadas no main desde o ÚLTIMO deploy da
função (data desconhecida — pode haver mudanças de outras sessões entre o
último deploy e 835dc58 que nunca tinham ido pro ar). Isso é suspeito nº 2.

Smoke tests que PASSARAM pós-deploy (~02:30):
- POST `{}` → 400 "tenant_id obrigatório" (função sobe)
- POST tenant falso + messages → atravessou o check de pausa, carregou config,
  400 controlado "Nenhum modelo configurado para o tenant" (sem custo)

### b) Migrations aplicadas em prod (Management API, ambas HTTP 200)
1. `20260708120000_admin_audit_log.sql` — tabela admin_audit_log (append-only)
   + 7 triggers de auditoria + helper log_admin_action + RPCs REDEFINIDAS:
   - `admin_approve_evolution_proposal` → agora `(_id uuid, _reason text DEFAULT NULL)`
     (DROP da versão 1-arg; corpo idêntico ao de prod, conferido por dump, + log)
   - `admin_backfill_insights_consent` → `(p_tenant_id, p_reason DEFAULT NULL)`
     **motivo passou a ser OBRIGATÓRIO** (raise se < 5 chars)
   - NOVA `admin_rollback_archetype_version(_version_id, _reason)`
   - Colunas novas: `system_config.ai_globally_paused` (bool NOT NULL DEFAULT
     false), `ai_logs.archetype_version_id` (uuid, nullable)
   - Triggers só disparam com `auth.uid()` presente (ação humana); escrita de
     serviço (cron PTAX, drainer) passa reto. NENHUM trigger em messages/
     conversations/nada do caminho de mensagens.
2. `20260708160000_admin_tenant_360.sql` — **NÃO aplicada** (bloqueada).

### c) Frontend (Vercel, push do main = commit 835dc58)
Só telas de super-admin: ConfirmBlastDialog nas ações de raio global, card
"Pausa geral da IA" em /admin/ai-infra, rollback/confirm em Arquétipos,
motivo no backfill. NADA de tenant tocado.
Commit `ab84979` (página 360) está SÓ LOCAL, não pushed.

### d) NÃO mexido
- Edge `set-system-api-key`: código commitado no main mas **NÃO deployada**
  (Pedro vetou — ver memória project_set_system_api_key_deploy_veto).
- Webhook de entrada, Evolution, envio de mensagens: **zero mudança** — o
  caminho de RECEBER/ENVIAR mensagem não foi tocado; só o de GERAR resposta.

## 2. Diagnóstico do "não chegou" — ordem de suspeitos

1. **Josemac (erro 463)**: número travado pela Meta — RECEBE e NÃO ENVIA — e a
   IA dele foi pausada manualmente (PAUSED_TENANTS + memória
   project_josemac_463_timelock). Se o teste foi nele, o sintoma é o problema
   ANTIGO, não o deploy. Confirmar primeiro qual número foi testado.
2. Mudanças acumuladas de outras sessões que entraram no deploy (ver ⚠️ acima).
3. As 3 mudanças desta sessão (improvável: smoke tests passaram; pausa=false).
4. Horário: ~02:30 BRT — conferir se o webhook sequer recebeu a mensagem
   (`messages` com sender='contact' no intervalo).

Query de diagnóstico (Management API /database/query, read-only):
```sql
SELECT
  (SELECT ai_globally_paused FROM system_config LIMIT 1) AS pausa_global,
  (SELECT count(*) FROM messages WHERE created_at > now()-interval '60 min' AND sender='contact') AS recebidas_1h,
  (SELECT count(*) FROM ai_logs   WHERE created_at > now()-interval '60 min' AND operation='reply_suggestion' AND error IS NULL) AS respostas_1h,
  (SELECT jsonb_agg(jsonb_build_object('t', created_at, 'err', left(error,150), 'tenant', tenant_id))
     FROM ai_logs WHERE created_at > now()-interval '60 min' AND error IS NOT NULL) AS erros_1h;
```
Logs da edge: dashboard Supabase → Functions → ai-reply → Logs (procurar
"[ai-reply] SUPPRESSED: pausa global" — se aparecer, a pausa está ligada e é
só desligar em system_config; se aparecer stack trace, é bug do deploy).

## 3. Rollback do ai-reply (se confirmado que o deploy é a causa)

```bash
# volta ai-reply + ai-config pro estado pré-sprint (commit 8dc5e04)
git checkout 8dc5e04 -- supabase/functions/ai-reply/index.ts supabase/functions/_shared/ai-config.ts
SUPABASE_ACCESS_TOKEN=<bws secret 397251ce-20b0-423d-b31f-b4780170a76f> \
  npx supabase functions deploy ai-reply --no-verify-jwt --project-ref qbclqjkvovfriuhshkpw
git checkout main -- supabase/functions/ai-reply/index.ts supabase/functions/_shared/ai-config.ts
```
⚠️ CAVEAT: isso volta pro `main` de ontem, que pode ser MAIS NOVO que o que
rodava antes (último deploy real da função é anterior, data desconhecida).
Se o problema persistir após rollback, a causa NÃO era o deploy de hoje.

As migrations NÃO precisam de rollback pra restaurar mensagens: nada nelas
toca o caminho de mensagem. Se quiser desativar por precaução só o check:
`UPDATE system_config SET ai_globally_paused = false;` (já é false).

## 4. Estado do sprint (pra continuidade)
Plano: `~/.claude/plans/em-cima-desse-plano-curried-crane.md` (cópia em
prompts/admin-redesign/00-plano-final.md). P0 done+prod; P1a commitado local
(ab84979) aguardando migration 20260708160000; P1b/P2/P3 não começados.
Token Supabase: bws secret `397251ce-20b0-423d-b31f-b4780170a76f` (rotacionado
08/07). Pedro vetou deploy da set-system-api-key.
