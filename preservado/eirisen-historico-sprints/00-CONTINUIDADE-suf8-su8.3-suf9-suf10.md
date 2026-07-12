# Risen — Continuidade pós-SUF10d (atualizado 09/05/2026 ~17h BRT)

> Sessão fechou um bloco grande de fixes encadeados:
> SUF8 (paginação inbox) → SU8.3 (apikey em INSERT) → SUF9 (envio pra grupo) →
> SUF10 + 10b + 10c + 10d (rename de grupo propaga). Tudo deployado e validado
> em produção.

---

## Status atualizado

| Sprint | Status | PR | O que entrega |
|---|---|---|---|
| SU7a | ✅ Mergeado anterior | #181 | Recepção mídia |
| SU8.0 | ✅ One-shot | sem PR | Backfill apikey 18/18 |
| SU8.1 | ✅ Mergeado anterior | #182 | provider-send-message via wa.crm |
| SU8.2 | ✅ Mergeado anterior | #184 | Broadcasts via wa.crm |
| **SUF8** | ✅ **Mergeado** | **#185** | **Paginação reversa do inbox** |
| **SU8.3** | ✅ **Mergeado** | **#186** | **Captura apikey ao criar instância** |
| **SUF9** | ✅ **Mergeado** | **#187 + #188** | **Fallback phone → JID pra grupos** |
| **SUF10** | ✅ **Mergeado** | **#189** | **Subject autoritativo + gate amplo** |
| **SUF10b** | ✅ **Mergeado** | **#190** | **TTL 1h reativo via webhook receive** |
| **SUF10c** | ✅ **Mergeado** | **#191 + #193** | **Revalidação no envio CRM (+ fix EarlyDrop)** |
| **SUF10d** | ✅ **Mergeado** | **#194** | **Gate em processManualSend (envio celular/WA Web)** |
| SU8.4 | ⏳ Próximo | — | deleteMessageViaEvolution em provider-webhook |
| SU8.5 | ⏳ Depois | — | Cleanup CRM_API_KEY env |
| SU7b | ⏳ Depois | — | UI envio mídia |

---

## Contexto base

- **Supabase project**: `qbclqjkvovfriuhshkpw`
- **Repo**: `pedrocostapc/risen-ai-connect`
- **Path local**: `/Users/pedrocosta/Dev/risen/risencrm/risen-ai-connect`
- **Evolution direto**: `wa.crm.risenmidia.com.br` (`209.38.147.84`) — self-hosted
- **Proxy CRM (legado)**: `api.crm.risenmidia.com.br` (`64.23.220.240`) — só pra Cloud API
- **Pedro envia mensagens pelo celular** (não pelo CRM). Aprendizado meta-sessão.

---

## SUF8 — Paginação reversa do inbox (PR #185) ✅

### Bug

Conversa CONSTRUAI (`cd9132ea`, 655+ mensagens) não mostrava mensagens novas no inbox. F5 não resolvia.

### Causa

Front fazia `GET /messages?conversation_id=eq.<id>&order=created_at.asc&limit=500`. Postgrest devolvia as 500 **mais antigas** e truncava as novas. Conversas com >500 msgs ficavam congeladas no histórico.

### Fix

- Hook `useMessages` virou `useInfiniteQuery` com `PAGE_SIZE=50`, cursor `lt(created_at)` desc, achatado pra ordem asc no client.
- `useRealtimeMessages` trocou `invalidateQueries` por `setQueryData` (INSERT/UPDATE/DELETE manipulam cache direto). Sem isso, invalidação ingênua quebraria a posição de scroll.
- `MessageThread` ganhou scroll handler no topo (threshold 80px), preservação de `scrollHeight` no prepend, indicadores "carregando mais" / "início da conversa".
- `InboxPage` consome a nova API + `key={selected.id}` pra remontar a thread em troca de conversation.
- 5 testes novos.

### Smoke validado

CONSTRUAI carrega rápida (50 msgs), realtime funciona, scroll up paginou, "início da conversa" apareceu eventualmente.

---

## SU8.3 — Captura apikey ao criar instância (PR #186) ✅

### Bug

Backfill do SU8.0 foi one-shot. Instâncias **novas** criadas após o backfill ficavam sem `config.apikey`. Resultado: envio quebrava com auth error porque o helper `sendTextViaEvolution` exige `apikey` per-instância.

### Achado crítico

Resposta da Evolution v2 não bate com a doc. O campo do apikey vem em `token`, não `apikey`. E o nome em `name` raiz, não `instanceName`. Endpoint de **criação** (`/instance/create`) pode ter shape diferente do `/instance/fetchInstances` usado no backfill.

### Fix

- `_shared/extract-apikey.ts` novo: pure function com fallback chain `token > apikey > hash > key`, recursão em wraps `instance` / `Instance`.
- `evolution-proxy.handleCreateInstance` extrai apikey da response e grava no `config.apikey` no INSERT. Warn truncado se shape inesperado.
- `backfill-evolution-apikeys` migrado pra usar o helper (DRY).
- 19 testes.

### Smoke validado

Criou `whats09051338`. SQL: `has_apikey=true`. Mensagem teste pelo inbox: `status='sent'`, chegou no celular destino.

---

## SUF9 — Envio pra grupos (PRs #187 + #188) ✅

### Bug

Mensagem em grupo falhava com `400 {"error":"Contact has no phone number"}`. Front mostrava mensagem otimista, banco gravava `status='failed'`, `provider_message_id=null`.

### Causa

DM tem `phone='553...'` + `whatsapp_jid='553...@s.whatsapp.net'`. Grupo tem `phone=null` + `whatsapp_jid='...@g.us'`. Validação rígida de phone bloqueava grupos com 400.

A Evolution v2 aceita JID inteiro (`...@g.us`) no campo `number` da `POST /message/sendText`.

### Fix

- `resolveEvolutionRecipient` em `_shared/evolution-client.ts`: ordem é grupo (JID inteiro) > phone (DM) > local-part do JID (fallback) > throw.
- Detecta grupo por **2 sinais**: `is_group=true` OU `whatsapp_jid endsWith '@g.us'`. Não confia só no flag.
- `provider-send-message` SELECTa `whatsapp_jid, is_group` e usa o helper em ambos os paths (retry + new).
- `sendViaQRProvider`: JID passa intacto, phone cru é normalizado pra dígitos.
- 9 testes.

### Bug pós-merge

PR #187 mergeado, mas Pedro tentou de novo e ainda quebrou. Causa: `replace_all` no SELECT só pegou o path de retry — esqueceu o de "new message" porque a indentação era diferente (10 vs 8 espaços). Fix em PR #188.

### Aprendizado meta

Antes de `replace_all` em padrão repetido, sempre `grep -n` antes/depois pra contar matches. Diferenças de indentação podem fazer replace perder ocorrências.

### Smoke validado

Grupo `RSN Fernandinha` (`120363428105763587@g.us`): `status='sent'`, JID inteiro usado. Não-regressão DM (Denise `553891239621`): `status='sent'`, phone usado.

---

## SUF10 + 10b + 10c + 10d — Rename de grupo propaga ✅

### Bug raiz

Pedro renomeou grupo no WhatsApp. CRM continuou mostrando nome velho. Investigação revelou que **3 caminhos** atualizavam `contacts.name` e **todos tinham guard** `LIKE "Grupo ____"`, impedindo sobrescrita de nomes não-placeholder.

E pior: a Evolution **não dispara `groups.upsert`** em rename. Só `messages.upsert`. Confirmado nos logs do `provider-webhook`.

### SUF10 — Subject autoritativo (PR #189)

- `_shared/group-naming.ts` novo: `isSuspectGroupName(name, jid)` cobre null/empty + placeholder regex + JID local-part puro.
- Drop guard `.like("name", "Grupo ____")` dos UPDATEs (subject de `groups.upsert` é autoritativo, sobrescreve direto).
- Gate de invocação: `isGenericGroupName` → `isSuspectGroupName(name, whatsappJid)`. Amplia critério.
- 10 testes.

**Smoke falhou.** Logs mostraram que `groups.upsert` nunca chega em rename. Gate `isSuspectGroupName` retorna `false` pra "RSN Fernandinha" (nome não-suspeito), fallback nem dispara.

### Decisão de produto pós-falha do SUF10

3 opções: (A) edge manual, (B) pg_cron diário, (C) TTL reativo curto.

Eu inflei o "custo" das opções. Pedro pediu números. Calculei: Evolution self-hosted, custo financeiro R$0, custo de carga desprezível mesmo com 1.500 instâncias. Fui mais honesto: custo não era decisor, drift era.

Pedro escolheu **C — TTL reativo 1h**. Drift máximo de 1h, atualiza só em grupos ativos.

### SUF10b — TTL 1h reativo via webhook receive (PR #190)

- Migration: `contacts.last_name_check_at` (timestamptz nullable) + index parcial `WHERE is_group = true`.
- Helper `shouldRevalidateGroupName(lastCheckAt, now?, ttlMs?)` em `_shared/group-naming.ts`. Constante `GROUP_NAME_TTL_MS = 1h`.
- Gate amplia: `isSuspectGroupName OR shouldRevalidateGroupName`.
- `fetchAndUpdateGroupName` carimba `last_name_check_at` no final, **mesmo se nome não mudou** (TTL não martela Evolution).
- 9 testes.

**Problema crítico no deploy:** `supabase db push` falhou (auth error — CLI tenta criar role temp e Pedro não tem CREATEROLE permission). Function deployou mas migration não. SELECT da edge ia quebrar produção pra todas mensagens.

**Resolvido:** aplicação manual via SQL Editor + `INSERT INTO supabase_migrations.schema_migrations`. Padrão pra próxima vez é setar `SUPABASE_DB_PASSWORD` env var.

**Smoke parcialmente funcionou:** outro tenant (`e0c95dbd`) reconciliou. Tenant do Pedro (`bcdd0e10`) continuou velho.

### SUF10c — Revalidação no envio CRM (PR #191 + #193)

Hipótese inicial: caminho de envio pelo CRM (`provider-send-message`) não passa pelo webhook, então nunca dispara o gate.

- Movido `fetchAndUpdateGroupName` pra `_shared/group-name-fetcher.ts`.
- Helper local `maybeRevalidateGroupName` em `provider-send-message` com gate completo.
- Fire-and-forget após sucesso (retry + new).

**Bug pós-deploy:** logs mostraram `EarlyDrop` matando o promise em background antes do `fetchAllGroups` completar. Supabase Edge Runtime mata o worker quando o request HTTP fecha — fire-and-forget puro não sobrevive.

**Fix em PR #193:** trocar `.catch()` solto por `EdgeRuntime.waitUntil(promise.catch(...))`. Forma oficial de fire-and-forget no Supabase Edge.

**Smoke ainda não funcionou.** Logs mostraram que Pedro nunca passa por `provider-send-message` em grupo. Eu assumi errado: ele envia mensagens **pelo celular**, não pelo CRM.

### SUF10d — Gate em processManualSend (PR #194)

Diagnóstico final: webhook tem 2 paths pra `messages.upsert` com `fromMe=true`:

- **Caso 2 (echo CRM):** `isAgentMessage()` true → early return. Esperado.
- **Caso 3 (manual send):** WhatsApp Web ou celular → `processManualSend`. **Sem gate.** É aqui que cai a mensagem do Pedro pelo celular.

Fix:
- `maybeRevalidateGroupName` extraído pra `_shared/group-name-fetcher.ts` (DRY entre 3 callers).
- `processManualSend` agora chama o gate.
- Logs distintos por caller (`[webhook]`, `[webhook-manual-send]`, `[suf10c-debug]`).

**Smoke FINAL funcionou.** Logs:

```
[webhook-manual-send] {"contact_name":"RSN Fernandinha", "is_group":true, "last_name_check_at":null, "is_suspect":false, "should_revalidate":true}
[webhook-manual-send] gate result: { dispatched: true, reason: "ttl_expired" }
[group-name-fetcher] ok jid=120363428105763587@g.us subject="Risen Fernanda" via=whats09051338
```

SQL pós-smoke:

| Tenant | Nome | last_name_check_at |
|---|---|---|
| `bcdd0e10` (Pedro) | "Risen Fernanda" ✅ | populado |
| `e0c95dbd` | "Risen Fernanda" ✅ | populado |
| `ed02eb45` | "2RSN Fernandinha" | null (sem msg na janela) |

`ed02eb45` reconcilia na próxima mensagem que entrar.

---

## Aprendizados meta da sessão

1. **Pedro envia pelo celular, não pelo CRM.** Assumi errado por muito tempo, gastou tempo em SUF10c (que cobre cenário CRM, não o dele). Quando ele falou "eu estou sempre enviando pelo whatsapp no telefone", tudo se reorganizou.

2. **`replace_all` com indentação diferente não pega todas as ocorrências.** Bug do SUF9 #187 (path retry sim, new message não). Sempre `grep -n` antes/depois.

3. **EarlyDrop mata fire-and-forget puro.** No Supabase Edge, qualquer trabalho em background depois de response HTTP deve usar `EdgeRuntime.waitUntil(promise)`. Senão o worker é morto antes de completar.

4. **Custo de chamadas Evolution self-hosted é ~zero.** Não inflar custo na conversa. Quando Pedro perguntou "qual é o custo?", a resposta correta foi R$0 + alguns ms de CPU. Decisor real era drift, não custo.

5. **Quando Pedro corrige ("não é nada disso, deixa de teimar"), parar e reler.** Em vários momentos eu insisti em hipótese errada. Lição: quando ele corrige, voltar pro último ponto que ele confirmou e reanalisar.

6. **Migration + edge devem deployar juntas** (ou migration ANTES de edge se schema mudou). `supabase db push` falhou silenciosamente várias vezes — sempre confirmar via SQL Editor que coluna existe antes de assumir que migration aplicou. Setar `SUPABASE_DB_PASSWORD` resolve pra futuro.

7. **Logs distintos por caller economizam tempo.** No SUF10d, os tags `[webhook]`, `[webhook-manual-send]` e `[suf10c-debug]` permitiram filtrar exatamente qual path disparou. Sem isso, logs viram sopa.

8. **Pedro decide produto. Mostro opções com trade-offs reais (não inflados).**

9. **`fromMe=true` tem 2 sub-casos**: echo do CRM (já gravou no banco) e manual send externo (WA Web/celular). São paths diferentes no webhook.

10. **Lovable buida automático em push de main.** Edges Supabase precisam de `supabase functions deploy` separado. Migration precisa de `supabase db push` ou SQL Editor manual. 3 deploys distintos pra 3 layers.

---

## Estado de infra após esta sessão

### Edges deployadas com mudanças
- `provider-webhook` (105.7kB) — SUF10/10b/10d
- `provider-send-message` (86.8kB) — SUF9/10c
- `evolution-proxy` — SU8.3
- `backfill-evolution-apikeys` — SU8.3 refactor

### Helpers compartilhados em `_shared/`
- `evolution-client.ts` — sendTextViaEvolution, evolutionConfigFromProvider, resolveEvolutionRecipient
- `extract-apikey.ts` — extractApikeyFromEvolutionResponse
- `group-naming.ts` — isSuspectGroupName, shouldRevalidateGroupName, GROUP_NAME_TTL_MS
- `group-name-fetcher.ts` — fetchAndUpdateGroupName, maybeRevalidateGroupName

### Migrations aplicadas
- `20260509150000_suf10b_group_name_ttl` — `contacts.last_name_check_at` + index parcial. Aplicada manualmente via SQL Editor (CLI falhou).

### Schema relevante
- `contacts` agora tem: id, tenant_id, name, phone, email, tags, custom_fields, source, created_at, updated_at, last_contacted_at, is_group, whatsapp_jid, analysis_consent_disclosed_at, analysis_opt_out_at, analysis_consent_source, **last_name_check_at**

### Logs debug ainda no ar
- `[suf10c-debug ...]` em `provider-send-message`
- `[webhook] {...}`, `[webhook-manual-send] {...}` verbose em `provider-webhook`

Foram úteis pra debug, podem ser removidos numa sprint de cleanup futura. Não bloqueiam nada.

### Secrets em uso
- `EVOLUTION_API_KEY` — master Evolution
- `CRM_API_KEY` — proxy CRM (vai virar opcional só pra Cloud API no SU8.5)
- `CRM_API_KE` — typo, mesmo digest. Limpar quando der.

---

## Caso pendente que se autoresolve

Tenant `ed02eb45` ainda tem nome velho `2RSN Fernandinha` no contato `120363428105763587@g.us`. **Não é bug.** Quando uma mensagem dessa instância entrar pelo grupo, gate dispara, reconcilia. Não precisa intervenção.

Backfill retroativo de **todos** os grupos com nomes desatualizados poderia ser uma sprint opcional (SUF10e?) — edge one-shot que itera grupos e dispara fetchAllGroups. Não está priorizado.

---

## Status agora

Conjunto SUF10 fechado de vez. Cobertura completa de revalidação de nome de grupo:

- Mensagem **recebida** em grupo → SUF10b
- Mensagem **enviada pelo CRM** em grupo → SUF10c
- Mensagem **enviada pelo celular/WA Web** em grupo → SUF10d
- Subject vindo via `groups.upsert` (raríssimo, mas suportado) → SUF10

**Próximo prompt:** SU8.4 (deleteMessageViaEvolution em provider-webhook).
