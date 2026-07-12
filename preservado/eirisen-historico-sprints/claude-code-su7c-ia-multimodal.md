# SU7c — IA multimodal (áudio + vision + send_image)

> Sprint que torna a IA do bot capaz de processar áudio (transcrição),
> imagem (vision), e enviar imagem do catálogo (tool `send_image`).
> Dividida em 3 etapas internas (SU7c-1, SU7c-2, SU7c-3) que podem ser
> implementadas e mergeadas separadamente ou em conjunto.

---

## Contexto

### Estado pós-SU7b

- Backend `provider-send-message` envia imagem com caption ✅
- Helper `sendMediaViaEvolution` em `_shared/evolution-client.ts` ✅
- Front com botão de anexo + upload pro Supabase Storage ✅
- Bucket `tenant-media` private + signed URL 4h pro envio
- `messages` tem `media_url`, `media_storage_path`, `media_size_bytes`, `media_uploaded_at`, `message_type`

### Recepção de mídia (SU7a, anterior)

- Webhook salva mídia recebida no mesmo bucket `tenant-media`
- `message_type` recebe valores como `audio`, `image`, `video`, `document`
- Render no front com signed URL 1h via hook `useMessageMediaUrl`

### Gap atual

A IA só processa **texto**. Quando cliente manda áudio ou imagem, o
bot ignora ou responde de forma quebrada. Cliente que manda foto da
obra, áudio com pergunta, ou pede catálogo de produtos por imagem —
todos ficam sem resposta automática útil.

### Custo médio por mensagem multimodal

| Etapa | Modelo | Custo |
|---|---|---|
| Transcrição áudio | Whisper API ou faster-whisper self-hosted | ~R$ 0,02/min |
| Vision (imagem) | Claude Sonnet | ~R$ 0,024/imagem |
| Vision (imagem) | GPT-4o mini | ~R$ 0,005/imagem |
| Vision (imagem) | Gemini Flash 2.5 | ~R$ 0,0001/imagem |
| send_image (tool call) | Qualquer | ~R$ 0,002 |

Default recomendado: Whisper + Gemini Flash 2.5 vision = ~R$ 0,02 por
mensagem multimodal. Plano R$ 99 com R$ 10 courtesy comporta ~500
mensagens multimodais/mês dentro do crédito.

---

## Estrutura da sprint

3 etapas internas. Cada uma é um PR separado, mergeado independentemente.
Ordem recomendada: SU7c-1 → SU7c-2 → SU7c-3. Sub-sprints podem rodar em
sequência ou paralelo (não dependem entre si).

| Sub | Entrega | Tamanho | Pré-req |
|---|---|---|---|
| **SU7c-1** | Áudio recebido → transcrição → IA processa o texto | médio | nenhum |
| **SU7c-2** | Imagem recebida → vision → IA responde | médio | nenhum |
| **SU7c-3** | IA envia imagem do catálogo (tool `send_image`) | grande | catálogo de produtos |

---

# SU7c-1 — Áudio recebido → transcrição → IA processa

## Objetivo

Quando cliente envia áudio no WhatsApp, sistema transcreve, salva o texto
junto com a mensagem, e a IA responde como se fosse texto comum.

## Escopo

### IN
- Detector no `provider-webhook` quando `message_type='audio'`
- Helper `transcribeAudio` em `_shared/transcription.ts`
- Coluna nova `messages.transcription` (text, nullable)
- Atualização do contexto que vai pra IA: incluir transcrição quando presente
- Configuração do provider de transcrição via env (default Whisper API)

### OUT
- Síntese de voz na resposta (text-to-speech) — fora de escopo, IA responde texto
- Transcrição de áudio enviado pelo agent (não tem caso de uso)
- Histórico de qualidade da transcrição, métricas de erro

## Pré-requisitos
- Branch: `su7c-1-audio-transcription`
- `OPENAI_API_KEY` configurada nos secrets do Supabase (provavelmente já está pra outras coisas)

## Plano de execução

### Etapa 1 — Raio-x

1. **Pipeline de processamento de mensagem recebida no webhook.** Onde fica a chamada `process_ai_reply` (ou nome equivalente) que decide se a IA responde? Reportar caminho.
2. **Como o contexto vai pra IA hoje.** Mensagens são passadas como array `[{role, content}]`. Reportar como `content` é construído pra mensagens texto.
3. **Bucket `tenant-media`.** Confirmar que áudio recebido tem `media_storage_path` e dá pra baixar via service_role (ou signed URL).
4. **OPENAI_API_KEY** disponível no env das edges? Se não, configurar.
5. **Storage do áudio.** Áudio é salvo em qual formato (`.ogg`, `.opus`, `.mp3`)? Whisper aceita.

### Etapa 2 — Migration

```sql
ALTER TABLE messages
  ADD COLUMN IF NOT EXISTS transcription text;

COMMENT ON COLUMN messages.transcription IS
  'Transcrição automática do áudio (SU7c-1). NULL pra mensagens não-áudio. Populado pelo provider-webhook após processamento Whisper.';

CREATE INDEX IF NOT EXISTS idx_messages_audio_pending_transcription
  ON messages (created_at)
  WHERE message_type = 'audio' AND transcription IS NULL;
```

Aplicar via SQL Editor + INSERT em `supabase_migrations.schema_migrations` (padrão Pedro).

### Etapa 3 — Helper de transcrição

`_shared/transcription.ts`:

```ts
export async function transcribeAudio(args: {
  audioUrl: string;          // signed URL do bucket
  language?: string;         // 'pt' default
}): Promise<{ ok: true; text: string } | { ok: false; error: string }> {
  const apiKey = Deno.env.get('OPENAI_API_KEY');
  if (!apiKey) return { ok: false, error: 'OPENAI_API_KEY ausente' };

  // 1. Download do áudio (signed URL)
  const audioRes = await fetch(args.audioUrl);
  if (!audioRes.ok) return { ok: false, error: `download falhou: ${audioRes.status}` };
  const audioBlob = await audioRes.blob();

  // 2. POST multipart pra Whisper API
  const form = new FormData();
  form.append('file', audioBlob, 'audio.ogg');
  form.append('model', 'whisper-1');
  form.append('language', args.language ?? 'pt');

  const res = await fetch('https://api.openai.com/v1/audio/transcriptions', {
    method: 'POST',
    headers: { Authorization: `Bearer ${apiKey}` },
    body: form,
  });

  if (!res.ok) {
    const errText = await res.text();
    return { ok: false, error: `whisper ${res.status}: ${errText.slice(0, 200)}` };
  }

  const data = await res.json();
  return { ok: true, text: data.text ?? '' };
}
```

### Etapa 4 — Integrar no webhook

No handler de `messages.upsert`, após `processIncomingMessage` salvar a row:

```ts
if (message.message_type === 'audio' && message.media_storage_path) {
  EdgeRuntime.waitUntil(
    transcribeAndUpdate(supabase, message).catch(e =>
      console.warn('[transcription] falhou:', e)
    )
  );
}
```

Função `transcribeAndUpdate`:
1. Gera signed URL 5min do bucket
2. Chama `transcribeAudio`
3. Se ok, `UPDATE messages SET transcription = ? WHERE id = ?`
4. Re-dispara o pipeline de AI reply (que agora tem `transcription` disponível)

**Importante:** transcrição é assíncrona. AI reply original pode disparar antes da transcrição. 2 opções:
- **A) AI espera transcrição:** detector no AI reply skipa se `message_type='audio' AND transcription IS NULL`. Após transcrição, função `transcribeAndUpdate` re-dispara AI reply.
- **B) AI responde 2x:** primeiro genérico ("recebi seu áudio, processando..."), depois com transcrição. Mais complexo, pior UX.

Recomendação: **opção A**. Mais limpa.

### Etapa 5 — Atualizar prompt builder da IA

Onde o contexto da conversa é montado pra mandar pra IA, substituir mensagens de áudio:

```ts
// antes (vazio pra áudio)
content: msg.text ?? ''

// depois
content: msg.message_type === 'audio' && msg.transcription
  ? `[áudio transcrito]: ${msg.transcription}`
  : msg.text ?? ''
```

Pra IA, áudio fica indistinguível de texto comum (com a marca `[áudio transcrito]`).

### Etapa 6 — Smoke

1. Cliente teste manda áudio no WhatsApp
2. SQL imediato:
   ```sql
   SELECT id, message_type, transcription, created_at
   FROM messages
   WHERE created_at > NOW() - INTERVAL '2 minutes'
   ORDER BY created_at DESC LIMIT 3;
   ```
   Esperado: row com `message_type='audio'`, `transcription` populado em ~5-10s.
3. AI deve responder em texto após transcrição.
4. Logs `[transcription]` em provider-webhook.

## Critérios de aceite SU7c-1
- [ ] Coluna `transcription` criada
- [ ] Áudio recebido tem transcrição populada em <30s
- [ ] AI responde após transcrição com contexto correto
- [ ] Falha de transcrição não trava recebimento de mensagem
- [ ] Não-regressão: áudio enviado pelo CRM (se existir) não é tocado

---

# SU7c-2 — Imagem recebida → vision → IA responde

## Objetivo

Quando cliente envia imagem, IA analisa o conteúdo visual e responde com base
no que viu. Funciona pra fotos de obras, produtos, documentos, etc.

## Escopo

### IN
- Builder do prompt da IA detecta `message_type='image'` e injeta a imagem como input multimodal
- Suporte ao formato multimodal de cada provider (Anthropic, OpenAI, Gemini)
- Default Gemini Flash 2.5 (mais barato), com fallback pra Claude/GPT-4o se cliente prefere

### OUT
- Edição/geração de imagem pela IA — fora de escopo
- Análise de PDF/documento (vira SU7c-extra se tiver demanda)

## Pré-requisitos
- Branch: `su7c-2-image-vision`
- SG1 (Gemini) idealmente já mergeado pra ter Gemini Flash 2.5 como opção. Se não, usar Claude Sonnet ou GPT-4o.

## Plano de execução

### Etapa 1 — Raio-x

1. **Como prompt da IA é montado hoje.** Função/edge que monta `messages: [{role, content}]` pro provider AI.
2. **Configuração de modelo por tenant.** `tenant_ai_configs` tem campo `model_id`? Como mapear modelo escolhido → suporta vision ou não?
3. **Schema do provider.** Cada provider tem formato diferente pra imagem em multimodal:
   - **Anthropic:** `content: [{type: 'image', source: {type: 'base64', media_type, data}}, {type: 'text', text}]`
   - **OpenAI:** `content: [{type: 'image_url', image_url: {url}}, {type: 'text', text}]`
   - **Gemini:** `parts: [{inlineData: {mimeType, data}}, {text}]`
4. **Bucket `tenant-media`.** Imagem é acessível via signed URL ou base64? Provedores aceitam ambos.

### Etapa 2 — Helper de montagem multimodal

`_shared/multimodal-builder.ts`:

```ts
export type MultimodalContent =
  | { type: 'text'; text: string }
  | { type: 'image'; mimeType: string; base64: string };

export async function buildMessageContent(
  message: Message,
  supabase: SupabaseClient,
): Promise<MultimodalContent[]> {
  const blocks: MultimodalContent[] = [];

  if (message.message_type === 'image' && message.media_storage_path) {
    const { data, error } = await supabase.storage
      .from('tenant-media')
      .download(message.media_storage_path);
    if (!error && data) {
      const buffer = await data.arrayBuffer();
      const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));
      blocks.push({
        type: 'image',
        mimeType: data.type || 'image/jpeg',
        base64,
      });
    }
  }

  if (message.text) {
    blocks.push({ type: 'text', text: message.text });
  } else if (message.transcription) {
    blocks.push({ type: 'text', text: `[áudio transcrito]: ${message.transcription}` });
  } else if (message.message_type === 'image') {
    blocks.push({ type: 'text', text: '[imagem sem caption]' });
  }

  return blocks;
}
```

### Etapa 3 — Adapters por provider

`_shared/providers/anthropic-adapter.ts`, `openai-adapter.ts`, `gemini-adapter.ts`:

Cada um converte `MultimodalContent[]` no formato esperado.

### Etapa 4 — Detector de modelo com vision

```ts
const VISION_CAPABLE_MODELS = new Set([
  'claude-sonnet-4-20250514',
  'claude-opus-4',
  'gpt-4o',
  'gpt-4o-mini',
  'gemini-flash-2.5',
  'gemini-pro-2.5',
]);

export function modelSupportsVision(modelId: string): boolean {
  return VISION_CAPABLE_MODELS.has(modelId);
}
```

Se modelo configurado **não suporta vision** (ex: cliente colocou `gpt-4o-realtime-preview` ou modelo legado), e mensagem é imagem:
- Fallback: ignora imagem, usa só caption como texto
- Log warn: `[ai-reply] modelo X não suporta vision, ignorando imagem`

### Etapa 5 — Smoke

1. Configurar tenant de teste com Gemini Flash 2.5 (ou Claude Sonnet se SG1 não pronto)
2. Cliente manda imagem com caption "que produto é esse?"
3. Imagem é uma foto de saco de cimento
4. AI responde algo coerente ("é um saco de cimento Votoran 50kg")

## Critérios de aceite SU7c-2
- [ ] AI responde corretamente a imagens recebidas
- [ ] Custo controlado (default Gemini Flash 2.5)
- [ ] Modelo sem vision capability fallback gracioso
- [ ] Não-regressão de mensagens texto

---

# SU7c-3 — IA envia imagem do catálogo (tool `send_image`)

## Objetivo

IA pode chamar uma tool `send_image(product_id_or_query)` que faz lookup
no catálogo de produtos do tenant e envia a imagem pelo CRM.

## Pré-requisito crítico

**Não existe catálogo de produtos hoje.** Esta sub-sprint requer:

1. Schema de tabela `products` (ou `catalog_items`)
2. UI pra o cliente cadastrar produtos
3. Sistema de busca (LIKE simples ou embeddings)

Decisão de produto pendente: **MVP simples ou versão completa?**

### Opção A — MVP simples
- Tabela `products` com schema mínimo: `id, tenant_id, name, image_url, description, sku?, price?`
- UI mínima: tela de cadastro com upload de imagem (reusa SU7b)
- Busca: LIKE em `name` + `description`
- Tool `send_image(query)`: faz LIKE, retorna até 3 candidatos, IA escolhe o melhor pelo nome
- Tamanho: ~2 dias (1 dia schema+UI, 1 dia tool integration)

### Opção B — Versão completa
- Schema completo com categorias, tags, preço, estoque, variações
- Embeddings semânticos (pgvector) pra busca por similaridade
- UI completa com upload em massa, edição, organização
- Tamanho: ~1 semana

Recomendação: **Opção A primeiro**. Valida demanda real, evolui se cliente pedir.

## Escopo da Opção A

### IN
- Migration: tabela `products` simples
- UI: página `/products` com lista + cadastro + edição
- Upload de imagem: reusa edge `upload-message-media` (ou cria `upload-product-image`)
- Tool `send_image` no AI runtime
- Edge dedicada `send-product-image` chamada pela tool

### OUT (Opção A)
- Categorias, tags, variações
- Embeddings, busca semântica
- Importação em massa
- Estoque

## Plano de execução SU7c-3 Opção A

### Etapa 1 — Migration

```sql
CREATE TABLE IF NOT EXISTS products (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  name text NOT NULL,
  description text,
  sku text,
  price_cents bigint,
  image_url text,
  image_storage_path text,
  active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_products_tenant_active ON products (tenant_id, active);
CREATE INDEX idx_products_name_search ON products
  USING gin (to_tsvector('portuguese', name || ' ' || coalesce(description, '')));

-- RLS
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

CREATE POLICY products_tenant_isolation ON products
  FOR ALL USING (tenant_id = get_user_tenant_id());
```

### Etapa 2 — UI básica

Página `/products`:
- Lista paginada de produtos do tenant
- Botão "Novo produto" → modal com:
  - Nome (obrigatório)
  - Descrição (opcional)
  - SKU (opcional)
  - Preço em R$ (opcional)
  - Upload de imagem (reusa flow do SU7b)
  - Ativo (toggle)
- Editar produto existente
- Desativar (não deletar)

Componente reusa shadcn: Table, Dialog, Form.

### Etapa 3 — Tool `send_image` no AI

Schema da tool:
```ts
{
  name: 'send_image',
  description: 'Envia uma imagem do catálogo de produtos pro cliente. Use quando o cliente pedir pra ver um produto, ou quando demonstrar um produto for útil pra resposta.',
  parameters: {
    type: 'object',
    properties: {
      query: {
        type: 'string',
        description: 'Nome ou descrição do produto procurado. Ex: "cimento", "tinta branca", "Votoran 50kg".'
      },
      caption: {
        type: 'string',
        description: 'Mensagem que vai junto da imagem.'
      }
    },
    required: ['query']
  }
}
```

Handler:
1. Busca em `products` com tsvector match: `to_tsvector('portuguese', name || ' ' || description) @@ plainto_tsquery('portuguese', query)`
2. Filtra `tenant_id = current_tenant + active = true`
3. Pega top 1 (ranking por relevância)
4. Se nenhum match: retorna pra IA "produto não encontrado"
5. Se encontrar: chama `provider-send-message` com `media_url` + `caption`
6. Retorna pra IA: "imagem enviada: {nome do produto}"

### Etapa 4 — Smoke

1. Cadastra 3 produtos com imagem (cimento Votoran, cimento Itaú, tinta Suvinil)
2. Cliente teste manda "tem cimento Votoran?"
3. AI deve chamar `send_image(query: "cimento Votoran")`
4. Imagem do Votoran chega no celular do cliente
5. SQL confirma row com `media_url` populado, `provider_message_id` populado, `status='sent'`

## Critérios de aceite SU7c-3 (Opção A)
- [ ] Tabela `products` criada com RLS
- [ ] UI funcional pra cadastrar/editar/desativar produtos
- [ ] Tool `send_image` registrada no AI runtime
- [ ] AI consegue mandar imagem do catálogo quando contexto pede
- [ ] Custo: produto não encontrado = 0 envio extra, só IA respondendo "não tenho esse produto"

---

# Pós-merge geral

```bash
gh pr merge <PR_NUM> --squash --delete-branch
git checkout main && git pull origin main

# Aplicar migrations conforme cada sub-sprint:
# SU7c-1: messages.transcription
# SU7c-3: tabela products

supabase functions deploy provider-webhook
# se tiver edge nova:
supabase functions deploy <nome-da-edge>
git push origin main
```

---

# Notas gerais

- **Ordem recomendada:** SU7c-1 → SU7c-2 → SU7c-3. Áudio é o caso de uso mais comum (cliente WhatsApp manda muito áudio), depois imagem (vision), depois catálogo (depende de feature de produtos).
- **SU7c-2 ganha barato com Gemini.** Se SG1 já estiver pronto, custo de imagem cai 50x.
- **SU7c-3 tem decisão de produto pesada.** MVP simples primeiro. Se cliente pedir busca semântica/categorias, evolui.
- **Audit/limites de custo:** SU7c todo aumenta consumo de IA. Pra evitar surpresas, considerar:
  - Toggle por tenant: "permitir áudio/imagem na IA?" default ligado
  - Limite mensal de minutos de áudio transcrito
  - Limite de imagens analisadas por mês
  Esses limites ficam pra SA1 (assinatura) integrar no FIFO de créditos.
- **Catálogo + tool `send_image` pode ser usado fora de IA também.** Ex: operador humano com botão "anexar produto do catálogo". Mas isso é UX pra outra sprint.

---

# Lembretes operacionais

- `grep -n` antes/depois de `replace_all`
- Migration **antes** do deploy de edge
- `EdgeRuntime.waitUntil(promise)` pra background work pós-response
- Logs distintos: `[transcription]`, `[multimodal]`, `[send-image-tool]`
- Smoke real com cliente de teste antes de fechar
- Custos: testar com áudios curtos primeiro, confirmar consumo no Whisper/OpenAI dashboard
