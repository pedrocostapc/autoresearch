# Risen — Continuidade SU7/SU8 (atualizado pós-SU8.1)

## Status atualizado

| Sprint | Status | Notas |
|---|---|---|
| SU7a | ✅ Mergeado (PR #181) | Recepção mídia funcionando 100% |
| SUF5 | ❌ Não necessário | RLS já estava habilitada |
| SU8.0 | ✅ Backfill apikey deployado | 18/18 instâncias com apikey |
| SU8.1 | ✅ Mergeado (PR #182) | provider-send-message migrado pra wa.crm |
| SU8.2 | 🟡 Próximo | broadcasts (send-now + dispatch-scheduled) |
| SU8.3 | ⏳ Depois | evolution-proxy capturar apikey em INSERT |
| SU8.4 | ⏳ Depois | deleteMessageViaEvolution em provider-webhook |
| SU8.5 | ⏳ Depois | cleanup CRM_API_KEY env |
| SU7b | ⏳ Depois | UI envio mídia (depende SU8.1 ✅) |
| Backfill nomes grupo | ⏳ Tangente | Pedro perguntou sobre "Grupo XXXX" — fica pra depois SU8.2 |

## Contexto

**Risen OS** — CRM SaaS multi-tenant pra WhatsApp. React + TS + Tailwind + Supabase + Stripe + shadcn, dev via Lovable. Self-hosted Evolution API.

- **Project Supabase**: `qbclqjkvovfriuhshkpw`
- **Repo**: `pedrocostapc/risen-ai-connect`
- **Path local**: `/Users/pedrocosta/Dev/risen/risencrm/risen-ai-connect`
- **Evolution direto**: `wa.crm.risenmidia.com.br` (`209.38.147.84`)
- **Proxy CRM (legado)**: `api.crm.risenmidia.com.br` (`64.23.220.240`)

## SU7a — ✅ Mergeado (PR #181)

7 bugs corrigidos: pipeline upload, enum audio+sticker, extractMediaUrl, branch fromMe, header apikey por instância, firewall droplet liberado, fetchAndUpdateGroupName via wa.crm.

## SUF5 — ❌ Dispensado

Memory dizia que `whatsapp_providers` foi droppada em SA2 sem RLS. Falso. SQL real confirmou RLS habilitada com 2 policies (SELECT por tenant, ALL pra owner/admin). `get_user_tenant_id()` funcional.

## SU8.0 — ✅ Backfill apikey concluído

Edge `supabase/functions/backfill-evolution-apikeys/index.ts` (PR #182). One-shot, super_admin only, popula `whatsapp_providers.config.apikey`.

### Achado crítico do shape Evolution v2

Resposta NÃO bate com a doc:
```json
{
  "id": "uuid",
  "name": "instance-name",   // raiz, NÃO instanceName
  "token": "C5B8...",        // apikey está em "token", NÃO "apikey"
  ...
}
```

Edge tem fallback chain. 18/18 populados.

### Como invocar
Dashboard "Test" tab NÃO funciona (passa role postgres). Usar curl com JWT do localStorage do CRM (`sb-qbclqjkvovfriuhshkpw-auth-token` → `access_token`):

```bash
curl -X POST "https://qbclqjkvovfriuhshkpw.supabase.co/functions/v1/backfill-evolution-apikeys" \
  -H "Authorization: Bearer ${JWT}" -H "Content-Type: application/json" -d '{}'
```

## SU8.1 — ✅ Mergeado (PR #182)

`provider-send-message` agora usa `wa.crm` direto pra envio de texto.

### O que mudou
- Endpoint: `https://wa.crm.risenmidia.com.br/message/sendText/{instance}`
- Header: `apikey: <per-instance>` (de `provider.config.apikey`)
- Removido: `CRM_API_BASE`, `Deno.env.get("CRM_API_KEY")`, header `x-api-key`
- Body: simples `{ number, text }`
- Cloud API path 100% intocado

### Helper compartilhado novo
`supabase/functions/_shared/evolution-client.ts` com:
- `EVOLUTION_BASE` constante
- `evolutionConfigFromProvider(provider)` extrator
- `sendTextViaEvolution(cfg, args)` retornando `{ ok, providerMessageId } | { ok: false, status, error }`

Será reusado em SU8.2 (broadcasts).

### Bug latente (não corrigido)
`provider-send-message:169` — `message_type: media_url ? "image" : "text"` hardcoda image. Fica pra SU7b.

### Smoke validado
- Mensagem `Oi` enviada via inbox (Pedro-1296)
- `status='sent'`, `provider_message_id` populado
- Chegou no celular destino
- Confirmado em 2ª instância

## SU8.2 — 🟡 PRÓXIMO

Migrar broadcasts pra `wa.crm` reusando o helper `_shared/evolution-client.ts`.

### Edges a migrar
1. `send-broadcast-now/index.ts` — broadcast manual ("enviar agora")
2. `dispatch-scheduled-broadcasts/index.ts` — cron de broadcasts agendados

Ambos chamam `${CRM_API_BASE}/evolution/instances/{instance}/send` com `x-api-key` global hoje. Substituir por `sendTextViaEvolution` do helper.

### Validação
1. Disparar 1 broadcast manual com 2-3 destinatários
2. Conferir todas as messages criadas com `status='sent'`
3. Esperar 1 broadcast agendado executar (ou disparar manualmente o cron) e validar igual

### Não tocar
- Helper `_shared/evolution-client.ts` — já está completo, só consume
- Lógica de scheduling, fila, rate limit do broadcast

## Endpoints Evolution v2 confirmados (SU7b futuro)

| Tipo | Endpoint | Body |
|---|---|---|
| Texto | `POST /message/sendText/{instance}` | `{ number, text, options? }` |
| Imagem/Vídeo/Doc | `POST /message/sendMedia/{instance}` | `{ number, mediatype, media: <URL ou base64>, caption?, fileName? }` |
| **PTT** (escolha do Pedro) | `POST /message/sendWhatsAppAudio/{instance}` | `{ number, audio, encoding?: true }` |
| Sticker | `POST /message/sendSticker/{instance}` | `{ number, sticker }` |

## Sequência SU8 completa

1. ✅ SU8.0 — backfill apikey
2. ✅ SU8.1 — provider-send-message (PR #182)
3. 🟡 SU8.2 — broadcasts (send-now + dispatch-scheduled)
4. ⏳ SU8.3 — evolution-proxy captura apikey em INSERT (instâncias novas)
5. ⏳ SU8.4 — deleteMessageViaEvolution em provider-webhook
6. ⏳ SU8.5 — cleanup CRM_API_KEY env
7. ⏳ SU7b — UI envio mídia (depende SU8.1 ✅)

## Tangentes pendentes

### Backfill nomes de grupo
Pedro reparou que grupos antigos aparecem como "Grupo 9903" (placeholder). `fetchAndUpdateGroupName` do SU7a só roda em mensagens **novas**. Solução: edge one-shot tipo SU8.0 mas pra `contacts` com `is_group=true` e `name ILIKE 'Grupo %'`. ~1-2h.

Pedro escolheu fazer **depois do SU8.x** completo.

## Backlog depois

- **SA1** (assinatura Stripe + courtesy credit + FIFO + auto-recharge) — receita, prioridade
- **SG1** (Gemini Flash-Lite/Flash/Pro cap 180k)
- **SU7c** (IA multimodal: transcrição áudio + vision + send_image)
- UI/Editorial Noir

## Aprendizados meta

1. Raio-x antes de código. Pedro corrige over-engineering rápido.
2. Memory pode estar desatualizada. Confirmar com SQL.
3. Pedro é direto. Respostas curtas, diff antes de aplicar, smoke antes de merge.
4. Bugs reais vêm em camadas. Não para no primeiro fix sem confirmar logs.
5. Pedro decide produto. Mostra opções com trade-offs.
6. Pedro tem 2 terminais Claude Code: "antigo" tem auth Supabase CLI cacheada, "novo" trava. Operações DB que exigem auth via SQL Editor manual.
7. Migration manual: SQL Editor + INSERT em `supabase_migrations.schema_migrations`.
8. Dashboard "Test" edges = role postgres genérico, não JWT user. Pra super_admin auth = curl com JWT do localStorage.
9. **Sandbox do Claude Code bloqueia push direto na main** — sempre via PR, mesmo housekeeping (.gitignore, etc).
10. **Não salvar raio-x em arquivos** — memory diz "inline only". Se Claude Code salvar em `docs/raiox-*.md`, deletar e pedir inline.

## Secrets em uso

- `EVOLUTION_API_KEY` — master Evolution (criada pra SU8.0)
- `CRM_API_KEY` — proxy CRM (vai virar opcional só pra Cloud API no SU8.5)
- `CRM_API_KE` — typo, mesmo digest do `CRM_API_KEY`. Limpar quando der.

## Status agora

SU8.1 mergeado e validado em produção (2 instâncias). PR #182 fechado, branch deletada. Housekeeping fechado em PR #183 (gitignore + remoção de raio-x soltos).

**Próximo**: prompt SU8.2 — migrar `send-broadcast-now` e `dispatch-scheduled-broadcasts` reusando `_shared/evolution-client.ts` já criado.
