# SU7a — Raio-X Final (antes do patch)

## Objetivo

**Não escrever código novo nesta etapa.** Só leitura, busca em arquivos e queries SQL. Saída esperada: trechos de código + outputs de query, raw, sem interpretação.

Estamos diagnosticando 4 problemas que vão entrar num único patch:

- **A.** Pipeline de descriptografia de mídia (`uploadMessageMedia`) falhando 100% das vezes — todas as mensagens com mídia dos últimos 3 dias têm `media_storage_path=null`
- **B.** Áudio/PTT/sticker do WhatsApp sumindo no banco (enum `message_type` não aceita esses valores, INSERT 22P02 silencioso)
- **C.** Nome de grupos vindo como placeholder "Grupo XXXX" (4 dígitos do JID) em vez do subject real
- **D.** Billing readiness pro SA2: vendemos storage em GB e retenção em dias. Antes de cliente pagante entrar, o accounting (RPC de cap, cleanup de órfão, retenção por tempo, idempotência de retry) precisa estar coerente.

5 partes abaixo. Responde tudo numa volta. Se algo "não existe / não encontrei", explicita — não pula.

---

## Parte 1 — Logs vivos do `uploadMessageMedia`

A função tem 5 pontos de saída silenciosa, todos com `console.warn` + `return`. Precisamos saber QUAL está disparando.

Buscar nos logs do Supabase (Functions → `provider-webhook` → Logs) as últimas 100 linhas que contenham qualquer um destes prefixos:

```
[uploadMedia]
[webhook] uploadMedia
[STORAGE_CAP_HIT]
[STORAGE_CAP_PROJECTED]
```

Cola raw, sem filtrar. Se houver muito ruído, prioriza linhas de **hoje** (07/05/2026) e **ontem**.

Especificamente quero identificar qual destes 5 warnings aparece:

1. `[uploadMedia] CRM_API_KEY ausente` — env var não configurada
2. `[uploadMedia] Evolution fetch exception` — fetch falhou (timeout, DNS, SSL)
3. `[uploadMedia] Evolution {status} key={id}` — proxy retornou HTTP não-200
4. `[uploadMedia] Evolution resposta não-JSON` — proxy retornou HTML
5. `[uploadMedia] Evolution sem base64 na resposta` — JSON sem o campo esperado

Se nenhum dos 5 aparecer, mas aparecer `[webhook] uploadMedia INICIANDO` sem o `OK` correspondente — significa que a função tá travando antes do warn (ex: timeout do edge worker). Cola isso também.

---

## Parte 2 — Extração de campos do payload no webhook

Mostre:

### 2.1 Linhas 100-200 de `supabase/functions/provider-webhook/index.ts`

Cola raw. Quero ver:
- Como `mediaUrl` é extraído (suspeito: só `imageMessage.url` e `audioMessage.url`)
- Como `whatsappJid` é definido — em grupo vem `key.remoteJid` (jid do grupo) ou `key.participant` (jid do membro)?
- Como `instanceName` chega ao webhook (path da URL? body? header?)
- Como `messageId` é extraído (`key.id`)

### 2.2 Função `mapMessageType` completa

Provavelmente perto da linha 295-316. Cola a função inteira + qualquer constante/tipo que ela use.

### 2.3 Sample real de payload de cada tipo

Roda esta query no SQL Editor (ofusca telefones manualmente antes de colar):

```sql
SELECT message_type, raw_payload
FROM messages
WHERE message_type IN ('image','video','file')
  AND raw_payload IS NOT NULL
  AND created_at > now() - interval '24 hours'
ORDER BY created_at DESC
LIMIT 1;
-- repete trocando 'image' por 'video' e 'file' separadamente, 1 sample de cada
```

Quero ver:
- Estrutura aninhada exata (`data.message.imageMessage`? `data.messageType`?)
- Onde está `mimetype` no payload bruto (pra saber se dá pra detectar tipo sem chamar Evolution)
- Confirmação de que URL `.enc` realmente está em `data.message.{tipo}Message.url`

---

## Parte 3 — Nome de grupos

Reportado: nomes vêm como "Grupo 0326", "Grupo 4501" (4 dígitos do JID). Patch atual tenta resolver via cron 24h, ineficaz pra grupos novos.

### 3.1 Busca no código

Em `supabase/functions/`, procurar por todos os matches:

```
"is_group"
"@g.us"
"findGroupInfos"
"fetchAllGroups"
"groupSubject"
"\"subject\""
"group_metadata"
```

Mostrar arquivo + 15 linhas around de cada match relevante.

### 3.2 Upsert de `contacts`

No `provider-webhook/index.ts`, mostrar o bloco completo onde `contacts` é upserted (provavelmente perto das linhas 350-450 — buscar por `from("contacts")` ou `.upsert(`). Quero ver:

- Como `name` é definido pra grupo vs 1:1
- Se há fallback "Grupo XXXX" hardcoded — onde
- Se já existe chamada a algum endpoint pra buscar o subject real

### 3.3 Cron de 24h

Buscar em `supabase/migrations/`:

```
"cron"
"pg_cron"
"group_name"
"refresh_group"
"backfill_group"
```

Mostrar a definição completa do cron job (se existir) + a função/edge que ele chama.

### 3.4 Estado atual no banco

```sql
SELECT
  COUNT(*) FILTER (WHERE name LIKE 'Grupo %') AS placeholder,
  COUNT(*) FILTER (WHERE name NOT LIKE 'Grupo %' AND is_group = true) AS resolved,
  COUNT(*) FILTER (WHERE is_group = true) AS total_groups
FROM contacts
WHERE is_group = true;
```

(se a coluna não for `is_group`, ajusta pro nome real — checa primeiro com `\d contacts` ou `information_schema.columns`)

---

## Parte 4 — Billing readiness (storage GB + retenção dias)

SA2 vai vender storage e retenção como recursos. Precisamos validar que o accounting está coerente antes do primeiro cliente pagante.

### 4.1 RPC `tenant_storage_used_bytes` e `tenant_storage_status`

Buscar nas migrations a definição de ambas. Cola raw o `CREATE OR REPLACE FUNCTION` completo de cada uma.

Quero confirmar:
- Soma `messages.media_size_bytes` com filtro `WHERE media_storage_path IS NOT NULL`? Ou conta tudo?
- Como o `cap_bytes` é calculado (lê de `subscriptions`? `tenant_settings`?)
- O que retorna quando o tenant não tem subscription ativa

### 4.2 Cron `sa2-cleanup-orphan-media-daily`

Buscar nas migrations a definição do cron e da função `sa2_cleanup_orphan_media()`. Cola raw.

Quero confirmar que o **path** que ele deleta no bucket bate exatamente com o formato gravado pelo `uploadMessageMedia`:

```
<tenant_id>/<message_id>.<ext>
```

Se a função usa outro formato (ex: `<tenant_id>/<conversation_id>/<message_id>`, ou esquece a extensão), órfãos vão acumular.

### 4.3 Retenção por tempo

Buscar em migrations:

```
"retention"
"retention_days"
"expire_messages"
"cleanup_old_messages"
"cleanup_messages"
```

Mostrar:
- Existe cron de retenção rodando hoje? Se sim, qual a função e período
- Onde o `retention_days` por tenant é armazenado (`subscriptions.retention_days`? `tenant_settings`? hardcoded?)
- Se o cleanup remove só a row de `messages`, ou também o objeto no storage

Se NÃO existe cron de retenção ainda, explicita "não encontrado" — isso impacta o roadmap do SA2.

### 4.4 Schema de eventos / system_logs

Buscar tabela usada pra tracking de eventos do tenant (warnings de cap, falhas de upload, etc):

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema='public'
  AND (table_name ILIKE '%log%' OR table_name ILIKE '%event%' OR table_name ILIKE '%audit%');
```

Pra cada tabela retornada, mostrar `\d {nome}` (colunas + tipos).

Hoje quando bate cap, o `uploadMessageMedia` só faz `console.warn`. Pra cliente pagante precisa virar row visível no dashboard. Quero saber se já existe a tabela certa, ou se precisa criar.

---

## Parte 5 — Idempotência e retry

Evolution faz retry de webhook quando recebe não-200 ou timeout. Hoje o `await uploadMessageMedia` blocka 5-10s — alta chance de timeout em alguns casos. Precisamos garantir que retry não duplica linhas em `messages` nem cobra storage 2x.

### 5.1 Constraints únicos em `messages`

```sql
SELECT conname, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid='public.messages'::regclass
  AND contype IN ('u','p','x');
```

Quero ver se existe `UNIQUE (tenant_id, provider_message_id)` ou similar — se não existir, retry duplica.

### 5.2 Lógica de upsert vs insert no webhook

Procurar no `provider-webhook/index.ts` por `from("messages")` — mostrar o bloco onde a inserção acontece. É `.insert()` ou `.upsert(..., { onConflict: ... })`?

### 5.3 Retry / dead letter pra mídia falha

Buscar em todo o repo:

```
"retry_count"
"retry"
"dead_letter"
"failed_media"
```

Quero saber se já existe alguma fila/tabela de retry pra quando `uploadMessageMedia` falhar (ex: decrypt indisponível temporariamente). Se não existe, hoje a mensagem fica eternamente sem mídia — aceitável pra beta, problema pra cliente pagante.

---

## Formato da saída

Markdown único, 5 seções na ordem acima, cada uma respondida com:

- **Trechos de código**: cola raw em blocos com indicação de arquivo + linha
- **Outputs de SQL**: cola tabela ou JSON do resultado
- **"Não encontrei"**: explicita quando não houver match, não chuta resposta

Se algum item exigir acesso que você não tem (ex: SSH ao Evolution droplet), avisa e pula. Não rodar curls externos nesta etapa — só leitura do repo + queries no Supabase.

Quando terminar, salva como `docs/sprints/su7a-raio-x-final.md` no repo (ou cola direto no chat se for mais rápido).
