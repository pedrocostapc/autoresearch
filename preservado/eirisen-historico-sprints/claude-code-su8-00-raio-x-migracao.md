# SU7b/SU8 — Raio-X complementar (migração total pra wa.crm)

## Contexto

Decidido migrar **todo envio** (texto + mídia) do proxy `api.crm` pro Evolution direto `wa.crm`. Recepção já está em wa.crm desde SU7a. Ao final, `provider-send-message` não chama mais `api.crm` em lugar nenhum (exceto talvez Cloud API que é outro path).

**Não escrever código.** Mapear o que precisa mudar.

## Seções

### 1. Apikey por instância (storage)

Hoje em `whatsapp_providers.config` quais campos exatamente existem? Roda no SQL Editor (ofusca valores antes de colar):

```sql
SELECT id, name, type, status,
  jsonb_object_keys(config) AS config_keys
FROM whatsapp_providers
WHERE type = 'qr'
ORDER BY created_at DESC
LIMIT 5;
```

Quero ver se `apikey` ou `instance_token` já está no config. Se não, precisamos popular.

### 2. Como cada instância foi criada hoje

Mostre `supabase/functions/qr-init-session/index.ts` (provavelmente é a edge que cria instância no Evolution e salva o provider). Quero ver:
- Onde o INSERT em `whatsapp_providers` acontece
- Se a apikey retornada pelo Evolution é salva em algum lugar
- Como o Evolution gera apikey (auto ou recebe?)

### 3. Endpoint Evolution v2 pra texto

Confirma da doc:
- `POST /message/sendText/{instance}` body `{ number, text, options? }` header `apikey`
- Resposta retorna `key.id` que vai pro `provider_message_id`

Se diferente, corrige.

### 4. Outras edges que chamam api.crm

Greps:
```
"api.crm.risenmidia"
"CRM_API_KEY"
"x-api-key"
"CRM_API_BASE"
```

Lista TODAS as ocorrências em `supabase/functions/` (arquivo + linha + contexto de 2 linhas). Quero ver quantas edges precisam ser migradas, não só a `provider-send-message`.

### 5. Endpoint Evolution v2 pra cada tipo de mídia

Confirma:
- Imagem/Vídeo/Documento: `POST /message/sendMedia/{instance}`
  - body: `{ number, mediatype: 'image'|'video'|'document', media: <URL ou base64>, fileName?, caption? }`
- PTT (voice note): `POST /message/sendWhatsAppAudio/{instance}`
  - body: `{ number, audio: <URL ou base64>, encoding?: true }`
- Sticker: `POST /message/sendSticker/{instance}`
  - body: `{ number, sticker: <URL ou base64> }`

Se algum diferente, corrige.

### 6. Backfill de apikey nas instâncias existentes

Se a apikey não está em `whatsapp_providers.config` hoje, precisamos buscar pra cada instância existente. Evolution tem endpoint pra listar instâncias:

```
GET /instance/fetchInstances
```

Confirma se isso retorna apikey por instância. Se sim, podemos fazer um script de backfill 1x.

### 7. Cloud API path

`provider-send-message` tem branch pra Cloud API (linhas 309-373 segundo o raio-x anterior). Esse path NÃO usa proxy CRM nem wa.crm — vai direto pra `graph.facebook.com`. Não muda no SU8. Confirma.

## Formato

Markdown único, 7 seções. SQL com resultados. Greps com paths e linhas. "Não encontrei" quando aplicável.
