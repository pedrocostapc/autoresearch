# SU7a — Recepção de Mídia (descriptografia + storage + render)

## Contexto

O Risen CRM usa Evolution API (self-hosted, Baileys) como gateway WhatsApp. WhatsApp envia toda mídia (imagem, vídeo, áudio, documento, sticker) com criptografia E2E. Hoje o frontend está recebendo a URL do `.enc` direto do CDN do WhatsApp e tentando renderizar — resultado:

- `<img>` quebra → vira o alt text "Imagem"
- `<video>` mostra player vazio com duração 0:00
- "Abrir arquivo" baixa blob criptografado AES (lixo binário, header tipo `4c f5 ab df 32 0e f2 8c...`)

A descriptografia precisa acontecer no backend antes da mídia ser exibida. Esta sprint resolve **só recepção** — envio manual por humano (SU7b) e IA multimodal (SU7c) ficam para sprints futuras.

**Tentamos a integração nativa S3 do Evolution apontando pro Supabase Storage. Não funciona** (issue #1478 aberta — Evolution usa lib MinIO que não suporta `forcePathStyle: true` exigido pelo Supabase). Por isso o pipeline é manual via edge function, com endpoint `POST /chat/getBase64FromMediaMessage/{instance}`.

---

## Objetivo

Pipeline assíncrono que descriptografa mídia recebida do WhatsApp, sobe pro Supabase Storage privado, e renderiza corretamente no inbox por mimetype.

**Fora de escopo nesta sprint:**
- Envio de mídia (humano ou IA) — fica para SU7b
- Transcrição de áudio, vision em imagem — fica para SU7c (depende do SA1 estar pronto pro billing extra)
- Backfill de mídia histórica — combinado com Pedro: as antigas (em beta) ficam quebradas
- Compressão/transcoding de vídeo — guardar como vier
- Stickers animados (`stickerMessage`) — tratar igual `imageMessage` por enquanto

---

## Decisões arquiteturais (já tomadas — não re-discutir)

1. **Storage**: Supabase Storage, bucket `whatsapp-media`, privado, signed URLs com TTL 1h gerada on-demand via RPC.
2. **Path layout**: `{tenant_id}/{conversation_id}/{message_id}.{ext}` — RLS por tenant nativo via path prefix.
3. **Processamento**: assíncrono — webhook salva message com `media_processing_status='pending'`, dispara edge `process-media` via `EdgeRuntime.waitUntil`, retorna 200 imediato pro Evolution.
4. **Frontend**: hook `useMediaUrl(message_id)` chama RPC, mostra skeleton enquanto pending, render correto por mimetype quando ready, fallback "mídia indisponível" quando failed.
5. **Mídia antiga**: ignorar — não rodar backfill. Mensagens com `media_url` legacy aparecem como failed/indisponível.

---

## Tarefas

### 1. Migration — schema

Adicionar colunas em `messages`:

```sql
-- supabase/migrations/YYYYMMDDHHMMSS_su7a_media_pipeline.sql

ALTER TABLE messages
  ADD COLUMN IF NOT EXISTS media_storage_path text,
  ADD COLUMN IF NOT EXISTS media_mimetype text,
  ADD COLUMN IF NOT EXISTS media_size_bytes bigint,
  ADD COLUMN IF NOT EXISTS media_filename text,
  ADD COLUMN IF NOT EXISTS media_duration_seconds int, -- pra audio/video
  ADD COLUMN IF NOT EXISTS media_processing_status text
    CHECK (media_processing_status IN ('pending', 'processing', 'ready', 'failed')),
  ADD COLUMN IF NOT EXISTS media_processing_error text,
  ADD COLUMN IF NOT EXISTS media_processed_at timestamptz;

CREATE INDEX IF NOT EXISTS idx_messages_media_pending
  ON messages (created_at DESC)
  WHERE media_processing_status IN ('pending', 'processing');

-- A coluna existente media_url fica deprecated mas não dropa (histórico)
COMMENT ON COLUMN messages.media_url IS 'DEPRECATED após SU7a — usar media_storage_path + RPC get_message_media_url';
```

Criar bucket via SQL:

```sql
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'whatsapp-media',
  'whatsapp-media',
  false, -- privado, signed URLs
  104857600, -- 100MB cap (WhatsApp limita 64MB vídeo / 100MB documento)
  NULL -- aceita qualquer mimetype, validação fica na edge
)
ON CONFLICT (id) DO NOTHING;
```

RLS no storage (ler só do próprio tenant, escrever só via service role):

```sql
-- SELECT: usuário lê arquivos do seu tenant
CREATE POLICY "tenant members read own media"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'whatsapp-media'
  AND (storage.foldername(name))[1]::uuid IN (
    SELECT tenant_id FROM tenant_members WHERE user_id = auth.uid()
  )
);

-- INSERT/UPDATE/DELETE: só service_role (edge function)
-- (não criar policy → bloqueia por padrão pra authenticated, service_role bypassa)
```

### 2. RPC `get_message_media_url`

Gera signed URL on-demand. Verifica RLS (usuário tem acesso ao tenant da mensagem).

```sql
CREATE OR REPLACE FUNCTION get_message_media_url(p_message_id uuid)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_storage_path text;
  v_tenant_id uuid;
  v_status text;
  v_signed_url text;
BEGIN
  SELECT m.media_storage_path, c.tenant_id, m.media_processing_status
    INTO v_storage_path, v_tenant_id, v_status
  FROM messages m
  JOIN conversations c ON c.id = m.conversation_id
  WHERE m.id = p_message_id;

  -- check tenant membership
  IF NOT EXISTS (
    SELECT 1 FROM tenant_members
    WHERE user_id = auth.uid() AND tenant_id = v_tenant_id
  ) THEN
    RAISE EXCEPTION 'unauthorized';
  END IF;

  IF v_status != 'ready' OR v_storage_path IS NULL THEN
    RETURN jsonb_build_object(
      'status', v_status,
      'url', null
    );
  END IF;

  -- signed URL TTL 1h
  SELECT (storage.create_signed_url('whatsapp-media', v_storage_path, 3600))->>'signedURL'
    INTO v_signed_url;

  RETURN jsonb_build_object(
    'status', 'ready',
    'url', v_signed_url,
    'expires_at', (now() + interval '1 hour')
  );
END;
$$;

GRANT EXECUTE ON FUNCTION get_message_media_url(uuid) TO authenticated;
```

### 3. Edge function nova: `process-media`

`supabase/functions/process-media/index.ts`

```typescript
// Recebe { message_id, instance_name, evolution_message_id }
// Chama Evolution /chat/getBase64FromMediaMessage
// Decode base64, sobe pro Supabase Storage
// UPDATE messages com path, mimetype, size, status='ready'

import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

interface ProcessMediaPayload {
  message_id: string;
  instance_name: string;
  evolution_message_id: string;
  tenant_id: string;
  conversation_id: string;
}

const MIME_TO_EXT: Record<string, string> = {
  "image/jpeg": "jpg",
  "image/png": "png",
  "image/webp": "webp",
  "image/gif": "gif",
  "video/mp4": "mp4",
  "video/webm": "webm",
  "audio/mpeg": "mp3",
  "audio/mp4": "m4a",
  "audio/ogg": "ogg",
  "audio/webm": "weba",
  "application/pdf": "pdf",
  "application/msword": "doc",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
  "application/vnd.ms-excel": "xls",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
};

function extFromMime(mimetype: string): string {
  return MIME_TO_EXT[mimetype.toLowerCase()] || "bin";
}

serve(async (req) => {
  const payload: ProcessMediaPayload = await req.json();
  const supabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
  );

  // marca como processing
  await supabase
    .from("messages")
    .update({ media_processing_status: "processing" })
    .eq("id", payload.message_id);

  try {
    // buscar credenciais do Evolution pra essa instância
    // (assumindo tabela whatsapp_instances com api_url e api_key)
    const { data: instance, error: instErr } = await supabase
      .from("whatsapp_instances")
      .select("api_url, api_key")
      .eq("instance_name", payload.instance_name)
      .single();

    if (instErr || !instance) throw new Error(`instance not found: ${payload.instance_name}`);

    // chama Evolution
    const evolUrl = `${instance.api_url}/chat/getBase64FromMediaMessage/${payload.instance_name}`;
    const resp = await fetch(evolUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "apikey": instance.api_key,
      },
      body: JSON.stringify({
        message: { key: { id: payload.evolution_message_id } },
        convertToMp4: true, // converte vídeo pra mp4
      }),
    });

    if (!resp.ok) {
      throw new Error(`evolution ${resp.status}: ${await resp.text()}`);
    }

    const result = await resp.json();
    // result: { mediaType, fileName, mimetype, base64, size: { fileLength } }

    if (!result.base64) throw new Error("no base64 in response");

    // decode base64 → Uint8Array
    const binary = Uint8Array.from(atob(result.base64), (c) => c.charCodeAt(0));
    const ext = extFromMime(result.mimetype);
    const storagePath = `${payload.tenant_id}/${payload.conversation_id}/${payload.message_id}.${ext}`;

    // upload Supabase Storage
    const { error: uploadErr } = await supabase.storage
      .from("whatsapp-media")
      .upload(storagePath, binary, {
        contentType: result.mimetype,
        upsert: true,
      });

    if (uploadErr) throw uploadErr;

    // update message
    await supabase
      .from("messages")
      .update({
        media_storage_path: storagePath,
        media_mimetype: result.mimetype,
        media_size_bytes: parseInt(result.size?.fileLength || "0"),
        media_filename: result.fileName,
        media_processing_status: "ready",
        media_processed_at: new Date().toISOString(),
      })
      .eq("id", payload.message_id);

    return new Response(JSON.stringify({ ok: true }), { status: 200 });
  } catch (err) {
    console.error("process-media failed:", err);
    await supabase
      .from("messages")
      .update({
        media_processing_status: "failed",
        media_processing_error: String(err).slice(0, 500),
        media_processed_at: new Date().toISOString(),
      })
      .eq("id", payload.message_id);

    return new Response(JSON.stringify({ ok: false, error: String(err) }), {
      status: 500,
    });
  }
});
```

### 4. Atualizar `provider-webhook`

Detectar mídia no payload, salvar message com pending, disparar `process-media` async via `EdgeRuntime.waitUntil` (sem aguardar) pra retornar 200 rápido pro Evolution.

```typescript
// trecho dentro do handler de MESSAGES_UPSERT em provider-webhook

const MEDIA_TYPES = new Set([
  "imageMessage",
  "videoMessage",
  "audioMessage",
  "documentMessage",
  "stickerMessage",
]);

const messageType = data.messageType; // ou da estrutura do payload Evolution
const isMedia = MEDIA_TYPES.has(messageType);

const insertedMessage = await supabase
  .from("messages")
  .insert({
    // ... campos existentes
    message_type: messageType,
    media_processing_status: isMedia ? "pending" : null,
  })
  .select()
  .single();

if (isMedia) {
  const evolutionMessageId = data.key?.id;
  if (!evolutionMessageId) {
    console.error("media message without key.id, cannot process");
  } else {
    // dispara async, não aguarda
    EdgeRuntime.waitUntil(
      supabase.functions.invoke("process-media", {
        body: {
          message_id: insertedMessage.data.id,
          instance_name: instanceName,
          evolution_message_id: evolutionMessageId,
          tenant_id: tenantId,
          conversation_id: conversationId,
        },
      })
    );
  }
}

// retorna 200 imediato
return new Response("ok", { status: 200 });
```

### 5. Frontend — hook + componente

`src/features/inbox/hooks/useMediaUrl.ts`:

```typescript
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

interface MediaUrlResponse {
  status: "pending" | "processing" | "ready" | "failed";
  url: string | null;
  expires_at?: string;
}

export function useMediaUrl(messageId: string, status: string) {
  return useQuery<MediaUrlResponse>({
    queryKey: ["media-url", messageId],
    queryFn: async () => {
      const { data, error } = await supabase.rpc("get_message_media_url", {
        p_message_id: messageId,
      });
      if (error) throw error;
      return data as MediaUrlResponse;
    },
    enabled: status === "ready", // só busca URL quando processamento terminou
    staleTime: 50 * 60 * 1000, // 50min — signed URL dura 1h
    refetchInterval: 55 * 60 * 1000, // refresh antes de expirar
  });
}
```

`src/features/inbox/components/MessageMedia.tsx`:

```tsx
import { useMediaUrl } from "../hooks/useMediaUrl";
import { FileIcon, AlertCircle, Loader2 } from "lucide-react";

interface MessageMediaProps {
  messageId: string;
  mimetype: string | null;
  filename: string | null;
  status: "pending" | "processing" | "ready" | "failed" | null;
}

export function MessageMedia({ messageId, mimetype, filename, status }: MessageMediaProps) {
  const { data, isLoading } = useMediaUrl(messageId, status || "");

  if (status === "pending" || status === "processing" || isLoading) {
    return (
      <div className="flex items-center gap-2 p-3 rounded bg-muted/30 text-muted-foreground text-sm">
        <Loader2 className="w-4 h-4 animate-spin" />
        Processando mídia…
      </div>
    );
  }

  if (status === "failed" || !data?.url) {
    return (
      <div className="flex items-center gap-2 p-3 rounded bg-muted/30 text-muted-foreground text-sm">
        <AlertCircle className="w-4 h-4" />
        Mídia indisponível
      </div>
    );
  }

  const url = data.url;
  const mt = (mimetype || "").toLowerCase();

  if (mt.startsWith("image/")) {
    return (
      <img
        src={url}
        alt={filename || "imagem"}
        className="rounded max-w-xs max-h-80 cursor-pointer object-cover"
        onClick={() => window.open(url, "_blank")}
      />
    );
  }

  if (mt.startsWith("video/")) {
    return (
      <video controls className="rounded max-w-xs max-h-80" preload="metadata">
        <source src={url} type={mt} />
      </video>
    );
  }

  if (mt.startsWith("audio/")) {
    return <audio controls src={url} className="max-w-xs" />;
  }

  // documento
  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center gap-2 p-3 rounded bg-muted/30 hover:bg-muted/50 text-sm"
    >
      <FileIcon className="w-4 h-4" />
      <span className="truncate">{filename || "Abrir arquivo"}</span>
    </a>
  );
}
```

Substituir o render atual de mensagens com mídia (procurar `media_url` ou texto "Imagem" hardcoded no inbox) por `<MessageMedia ... />`. Verificar onde está renderizando hoje — provavelmente em `src/features/inbox/components/MessageBubble.tsx` ou similar.

### 6. Refresh em tempo real

Quando `process-media` termina, o frontend precisa saber pra trocar o skeleton pelo render. Duas opções:

a) Subscription Supabase Realtime no `messages` filtrando por conversation_id. Quando UPDATE chega com `media_processing_status='ready'`, React Query invalida a query da mensagem e refaz o render. **Recomendado** se já tem subscription do inbox rodando — é só adicionar o campo no select.

b) Polling no hook `useMediaUrl` enquanto status='pending'. Pior UX e mais carga.

Implementar (a). Se a subscription do inbox já existe, garantir que o select inclui as novas colunas (`media_storage_path`, `media_mimetype`, `media_size_bytes`, `media_filename`, `media_processing_status`).

---

## Validação / smoke test

1. Criar conversa de teste com tenant Hospital Teste (mesmo padrão do SU5)
2. Enviar do celular pro número conectado: 1 imagem JPEG, 1 vídeo MP4, 1 áudio PTT, 1 PDF
3. Conferir no inbox:
   - Skeleton "Processando mídia…" aparece imediatamente
   - Em ≤10s, todas as 4 mídias renderizam corretamente
   - Imagem abre em nova aba ao clicar
   - Vídeo dá play e tem duração correta
   - Áudio dá play
   - PDF abre em nova aba
4. Conferir no Supabase Storage que os 4 arquivos estão em `whatsapp-media/{tenant_id}/{conversation_id}/`
5. Conferir no DB: `media_processing_status='ready'` em todas, `media_storage_path` preenchido, `media_mimetype` correto
6. Forçar erro: deletar mensagem da Evolution antes de processar → `media_processing_status='failed'`, UI mostra "Mídia indisponível"

## Logs / observabilidade

- Edge `process-media` deve logar: tempo total (download + upload), tamanho do arquivo, mimetype recebido vs detectado, message_id
- Adicionar coluna `media_processing_error` no select do `/admin/dashboard` (futura sprint pode mostrar fila de mídias com falha)

## Ordem de execução

1. Migration (schema + bucket + policies + RPC)
2. Edge `process-media` (deploy + smoke test isolado: invocar manual com message_id existente)
3. Atualizar `provider-webhook` (deploy)
4. Frontend (hook + componente + integração com MessageBubble)
5. Validação end-to-end
6. Commit + PR

## Observações finais

- Não dropar a coluna `media_url` legacy nesta sprint — fica deprecated
- Não implementar backfill histórico (combinado com Pedro)
- `convertToMp4: true` na chamada do Evolution converte vídeos pra MP4 universal — não tirar
- Stickers vão como `imageMessage` no render por enquanto (são WebP, navegador renderiza)
- Tamanho cap: 100MB no bucket (WhatsApp limita 64MB vídeo, 100MB documento — folga suficiente)
- Signed URL TTL 1h: refresh automático no React Query a cada 55min enquanto a mensagem está visível

## O que NÃO fazer nesta sprint (já discutido — não cair em scope creep)

- Envio de mídia pelo atendente humano → SU7b
- AI tool `send_image()` → SU7c
- Transcrição automática de áudio (Whisper) → SU7c
- Vision multimodal em imagem (Claude/Gemini visão) → SU7c
- Catálogo de produtos com imagem → escopo separado
- Compressão/resize de imagem antes de subir → não nesta sprint
- Backfill de mídia histórica → combinado: ignorar (beta)
- Configurar S3 nativo do Evolution → não funciona com Supabase (issue #1478)
