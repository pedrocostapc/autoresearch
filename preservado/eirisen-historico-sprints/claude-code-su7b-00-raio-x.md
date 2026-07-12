# SU7b — Raio-X (envio de mídia pelo atendente)

## Objetivo

**Não escrever código.** Mapear o estado atual antes de implementar envio de mídia pelo CRM. Saída: relatório markdown único com 5 seções respondidas raw.

## Contexto

SU7a destravou recepção/decrypt de mídia (provider-webhook). Agora o atendente humano precisa poder **enviar** foto/vídeo/áudio/PDF direto do inbox, não só pelo celular. Mídia deve subir pro Supabase Storage e depois ser enviada via Evolution API.

Confirmado em SU7a:
- Bucket `tenant-media` privado, RLS por tenant
- Coluna `messages.media_storage_path` populada
- RPC `tenant_storage_status` pra cap check
- Mídia outbound (`manual_send=true`) já renderiza no inbox
- apikey da Evolution vem por instância (não global)

## Seções

### 1. Envio de texto hoje

Mostre `supabase/functions/provider-send-message/index.ts` completo. Quero ver:
- Como autentica o usuário (JWT)
- Como resolve tenant + instância
- Como chama Evolution (qual endpoint, qual header, qual body)
- Como insere em `messages`
- Como trata erro

### 2. UI do input do inbox

Localize o componente que renderiza o input de "Escreva uma mensagem" no inbox. Mostre:
- Caminho do arquivo
- JSX completo do input + botão enviar
- Hook que dispara o envio (`useSendMessage` ou similar) — assinatura e corpo
- Se já existe algum botão de anexo (mesmo que desabilitado)

### 3. Endpoint Evolution pra envio de mídia

Pesquise na doc do Evolution v2:
- Endpoint correto: `/message/sendMedia/{instance}` ou `/message/sendWhatsAppAudio/{instance}` ou outro?
- Body shape esperado (base64? URL? mediatype?)
- Diferença entre tipos: image vs video vs audio vs document
- Tem endpoint específico pra PTT (audio voice note) vs audio normal?

Se não conseguir confirmar pela doc, deixe explícito "preciso testar" e proponha 1 curl de teste.

### 4. Storage atual + tamanho

```sql
-- Quanto cada tenant tem hoje
SELECT tenant_id, used_bytes, cap_bytes, used_pct
FROM (
  SELECT
    t.id AS tenant_id,
    public.tenant_storage_used_bytes(t.id) AS used_bytes,
    (public.tenant_storage_status(t.id)).cap_bytes,
    (public.tenant_storage_status(t.id)).used_pct
  FROM tenants t
) sub
ORDER BY used_pct DESC NULLS LAST
LIMIT 10;

-- Tamanho típico de mídia recebida (referência pra cap do upload)
SELECT
  message_type,
  COUNT(*) AS n,
  ROUND(AVG(media_size_bytes)/1024.0, 1) AS avg_kb,
  ROUND(MAX(media_size_bytes)/1024.0/1024.0, 1) AS max_mb
FROM messages
WHERE media_size_bytes IS NOT NULL
GROUP BY message_type;
```

Cola os 2 resultados.

### 5. Limites WhatsApp + Evolution

Confirme da doc:
- Tamanho máximo por mídia (imagem, vídeo, áudio, doc) no WhatsApp Business / Evolution
- Formatos aceitos por tipo
- Comportamento se passa do limite (Evolution corta? rejeita 4xx? truncate silente?)

## Formato

Markdown único, 5 seções. Trechos de código raw com path + linha. SQL com resultados. "Não encontrei" quando não houver match. Sem propor código novo.

Quando terminar, salva em `docs/sprints/su7b-raio-x.md` no repo ou cola no chat.
