# SU7b — UI de envio de mídia (imagem primeiro)

> Sprint que destrava produto. Backend `provider-send-message` aceita
> `media_url` desde SU8.1, mas o caminho não está completo (sendMedia não
> é chamado, parâmetro fica ignorado). Front não tem botão de anexo.
> Esta sprint fecha as duas pontas pra **imagem**. Áudio, vídeo, doc e
> sticker ficam pra extensões posteriores.

---

## Contexto

### Backend hoje

`provider-send-message/index.ts` já tem assinatura que aceita `media_url`,
mas:

```ts
async function sendViaQRProvider(
  provider: any,
  to: string,
  text: string,
  _media_url?: string  // ← underscore = ignorado
): ...
```

`media_url` é parâmetro fantasma. Mensagem com `media_url` ainda cai em
`sendTextViaEvolution`, que ignora o campo. Resultado: sem caminho de
envio de mídia funcional.

Bug latente herdado: `provider-send-message:169` hardcoda
`message_type: media_url ? "image" : "text"`. Precisa detectar tipo real
(imagem/vídeo/áudio/doc) a partir do mime.

### Front hoje

Componente `MessageThread` renderiza mensagens. `InboxPage` tem o input
de texto. Nenhum botão de anexo, nenhum modal de upload, nenhum preview.

### Endpoints Evolution v2 confirmados

| Tipo | Endpoint | Body |
|---|---|---|
| Imagem/Vídeo/Doc | `POST /message/sendMedia/{instance}` | `{ number, mediatype, media: <URL ou base64>, caption?, fileName? }` |
| PTT (áudio) | `POST /message/sendWhatsAppAudio/{instance}` | `{ number, audio, encoding?: true }` |
| Sticker | `POST /message/sendSticker/{instance}` | `{ number, sticker }` |

### O que SU7b entrega

**Imagem fim-a-fim:**

1. Backend: `sendMediaViaEvolution` em `_shared/evolution-client.ts` chamando `/message/sendMedia/{instance}`.
2. Backend: `provider-send-message` detecta `media_url`, valida mime, chama `sendMediaViaEvolution` em vez de `sendTextViaEvolution`.
3. Backend: `message_type` correto (`image` quando mime é image/*, `text` quando não tem media_url).
4. Front: botão de anexo no input do inbox.
5. Front: upload da imagem pro Supabase Storage, gera URL pública.
6. Front: preview antes de enviar + caption opcional.
7. Front: render de imagem no `MessageThread` (já recebe via SU7a, então provavelmente já renderiza — confirmar na Etapa 1).

**Não cobre nesta sprint:**

- Áudio PTT (gravação no browser tem complexidade própria — vira SU7b-audio).
- Vídeo, documento, sticker — extensões depois de imagem validada.
- AI mandando imagem (catálogo de produtos) — fica pra SU7c (multimodal).

---

## Escopo

### IN

- `_shared/evolution-client.ts` — helper `sendMediaViaEvolution`.
- `provider-send-message/index.ts` — detecta `media_url`, valida, chama helper certo, seta `message_type` correto.
- Front:
  - Botão de anexo (paperclip icon) no input do inbox.
  - Modal/popover de upload com preview + caption.
  - Função de upload pra Supabase Storage (bucket de mídia).
  - Render de imagem em `MessageThread` (se ainda não renderizar).

### OUT

- Áudio, vídeo, documento, sticker.
- AI multimodal (vision, transcrição).
- Galeria/biblioteca de mídia recente.
- Compressão/redimensionamento client-side.

---

## Pré-requisitos

- Branch nova a partir de `main`: `su7b-ui-image-send`.
- Build + tsc + vitest verdes.
- `main` pós-merge SU8.4a (PR #195).

---

## Plano de execução

### Etapa 1 — Raio-x (sem codar)

Reportar antes de codar:

1. **Bucket de storage de mídia.** Provavelmente criado em SU7a (recepção). Reportar:
   - Nome do bucket
   - Policies RLS (quem pode upload?)
   - Estrutura de paths (ex: `{tenant_id}/{conversation_id}/{filename}`)
   - URL pública ou signed URL?

2. **Como o front lida com mídia recebida hoje.** SU7a deveria ter feito a recepção funcionar:
   - `MessageThread` renderiza imagem? Se sim, qual componente?
   - `media_url` da `messages` é exibida como `<img src=...>` direto, ou tem proxy?
   - Funciona? (testar abrindo conversa que tem mídia recebida)

3. **Componente do input no inbox.** Provavelmente em `src/features/inbox/` ou `src/components/inbox/`. Reportar:
   - Caminho exato
   - Como dispara envio de texto hoje (chama `provider-send-message` direto?)
   - Onde encaixa o botão de anexo

4. **`provider-send-message` hoje.** Confirmar:
   - Path "new message" e "retry" como tratam `media_url`
   - Onde está o `message_type: media_url ? "image" : "text"` hardcoded
   - Se request body do front já manda `media_url` (provavelmente sim, parâmetro existe)

5. **Validação de mime e tamanho.** Existe alguma constante / utility de validação no repo? Se sim, reusar. Se não, criar simples:
   - Imagem: `image/jpeg`, `image/png`, `image/webp`
   - Tamanho máximo: 5 MB (limite WhatsApp pra imagem é ~16 MB; ser conservador no MVP)

Não codar. Reportar findings.

### Etapa 2 — Backend: helper `sendMediaViaEvolution`

Em `_shared/evolution-client.ts`:

```ts
export async function sendMediaViaEvolution(
  cfg: EvolutionConfig,
  args: {
    number: string;
    mediatype: 'image' | 'video' | 'document';
    media: string; // URL pública (preferido) ou base64
    caption?: string;
    fileName?: string;
  },
): Promise<
  | { ok: true; providerMessageId: string }
  | { ok: false; status: number; error: string }
> {
  const url = `${EVOLUTION_BASE}/message/sendMedia/${encodeURIComponent(cfg.instanceName)}`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', apikey: cfg.apikey },
    body: JSON.stringify(args),
  });
  if (!res.ok) {
    const errorText = await res.text();
    return { ok: false, status: res.status, error: errorText };
  }
  const data = await res.json();
  return {
    ok: true,
    providerMessageId: data.key?.id ?? data.messageId ?? '',
  };
}
```

Tratar:
- 4xx/5xx com mensagem clara
- providerMessageId pode estar em campos diferentes — fallback chain igual ao do `sendTextViaEvolution`

### Etapa 3 — Backend: ajustar `provider-send-message`

Lógica:

```ts
// pseudocódigo
if (media_url && isImageMime(media_url)) {
  message_type = 'image';
  result = await sendMediaViaEvolution(cfg, {
    number: recipient,
    mediatype: 'image',
    media: media_url,
    caption: text || undefined, // text vira caption quando há mídia
    fileName: extractFilename(media_url),
  });
} else {
  message_type = 'text';
  result = await sendTextViaEvolution(cfg, { number: recipient, text });
}
```

Helpers:
- `isImageMime(url)` — verifica extensão da URL ou faz HEAD pra pegar Content-Type. Inicial: extensão (`.jpg|.jpeg|.png|.webp`).
- `extractFilename(url)` — última parte do path.

INSERT em `messages` agora seta `message_type` correto + `media_url` correto.

### Etapa 4 — Front: upload pro Supabase Storage

Função utilitária em `src/features/inbox/lib/upload-media.ts` (ou local equivalente):

```ts
export async function uploadMediaForMessage(
  file: File,
  conversationId: string,
  tenantId: string,
): Promise<{ url: string; mime: string; size: number }> {
  // 1. Validar mime + tamanho
  // 2. Path: `${tenantId}/${conversationId}/${Date.now()}-${file.name}`
  // 3. supabase.storage.from(BUCKET).upload(path, file)
  // 4. Pegar publicUrl
  // 5. Retornar { url, mime: file.type, size: file.size }
}
```

Usar bucket descoberto na Etapa 1.

### Etapa 5 — Front: botão de anexo + modal

No componente do input do inbox:

- Botão `<Paperclip />` (lucide-react) ao lado do input.
- Click abre modal/popover com:
  - Input file `accept="image/jpeg,image/png,image/webp"`
  - Preview da imagem após selecionar
  - Textarea pra caption opcional (placeholder "Adicione uma legenda...")
  - Botão "Enviar" (loading state durante upload + envio)
  - Botão "Cancelar"
- Ao enviar:
  1. Chama `uploadMediaForMessage(file, ...)` → pega `url`
  2. Chama `provider-send-message` com `{ conversation_id, text: caption, media_url: url }`
  3. Fecha modal
  4. Limpa caption + file
- Toast de erro se upload ou envio falhar

### Etapa 6 — Front: render de imagem em `MessageThread`

Se Etapa 1 mostrou que já renderiza, pular. Se não:

- Componente `MessageBubble` (ou equivalente) detecta `message_type === 'image'`.
- Renderiza `<img src={message.media_url} className="..." />` com:
  - Max width/height razoáveis pra não estourar layout
  - Click pra abrir lightbox/modal (opcional, pode ficar pra depois)
  - Caption (se `message.text` presente) embaixo da imagem
  - Loading skeleton enquanto carrega

### Etapa 7 — Testes

**Unit (vitest):**
- `sendMediaViaEvolution`: sucesso, 4xx, 5xx
- `isImageMime`: extensões válidas, inválidas, edge cases
- `uploadMediaForMessage`: validação de mime/tamanho (mock supabase storage)

Build / tsc / vitest verdes.

### Etapa 8 — Smoke em produção

1. **Cenário DM:**
   - Abre conversa DM com você mesmo (ou contato de teste)
   - Click anexo → seleciona JPG ~1MB → preview aparece
   - Adiciona caption "teste imagem"
   - Click enviar → loading
   - Imagem aparece no inbox + chega no WhatsApp do destino com caption

2. **Cenário grupo:**
   - Mesmo fluxo num grupo de teste
   - Confirma JID `@g.us` é usado corretamente (graças a SUF9)

3. **Validação de tamanho:**
   - Tenta upload de 10MB → erro client-side antes de tentar envio

4. **Mime inválido:**
   - Tenta upload de `.txt` → bloqueado

5. **Não-regressão de texto:**
   - Manda mensagem só de texto → continua funcionando, `message_type='text'`

SQL pós-smoke:

```sql
SELECT id, sender, text, media_url, message_type, status, provider_message_id, created_at
FROM messages
WHERE created_at > NOW() - INTERVAL '5 minutes'
  AND sender = 'agent'
ORDER BY created_at DESC
LIMIT 5;
```

Esperado: row de imagem com `message_type='image'`, `media_url` populado, `text` = caption (ou null), `status='sent'`, `provider_message_id` populado.

---

## Critérios de aceite

- [ ] Helper `sendMediaViaEvolution` em `_shared/evolution-client.ts` com testes.
- [ ] `provider-send-message` chama helper certo conforme `media_url`.
- [ ] `message_type` correto no INSERT (`image` ou `text`).
- [ ] Botão de anexo no inbox abre modal funcional.
- [ ] Upload pra Supabase Storage funciona, retorna URL pública.
- [ ] Imagem chega no WhatsApp do destino com caption (se houver).
- [ ] Imagem aparece no inbox em tempo real (realtime).
- [ ] Não-regressão: envio de texto puro continua funcionando.
- [ ] Build / tsc / vitest verdes.
- [ ] PR linkando este prompt + findings da Etapa 1.

---

## Notas

- **MVP é só imagem.** Áudio (gravação no browser + encoding base64), vídeo, documento, sticker entram em sub-sprints. Imagem cobre 80% do uso real.
- **Caption opcional, não obrigatória.** WhatsApp aceita imagem sem caption.
- **Upload primeiro, send depois.** Storage upload e envio Evolution são 2 chamadas distintas. Falha no upload não cria mensagem. Falha no envio cria mensagem `failed` com `media_url` populada (permite retry).
- **Mídia recebida vs enviada compartilham bucket.** Mesmo path pattern, mesmo storage. Reusar bucket SU7a.
- **AI multimodal (SU7c) é separado.** AI mandando imagem do catálogo, AI processando imagem recebida — outra sprint.
- **Limite de tamanho conservador.** 5 MB inicial. Pode subir depois se cliente reclamar. WhatsApp aceita até ~16 MB pra imagem.

---

## Pós-merge

```bash
gh pr merge <PR_NUM> --squash --delete-branch
git checkout main && git pull origin main
supabase functions deploy provider-send-message
git push origin main
```

Sem migration nesta sprint.

---

## Branch e PR

- Branch: `su7b-ui-image-send`
- PR título: `feat(inbox): UI de envio de imagem (SU7b)`
- PR descrição:
  - link pra este prompt;
  - findings da Etapa 1 (bucket, render atual, componente do input);
  - lista de arquivos tocados (front + backend);
  - smoke executado com SQL real;
  - prints do inbox (opcional, ajuda review).

---

## Lembretes operacionais

- `grep -n` antes/depois de `replace_all` (lição SUF9).
- `EdgeRuntime.waitUntil(promise)` se algum trabalho ficar em background pós-response (lição SUF10c).
- Logs distintos pra debug (`[send-media]`, `[upload-media]` etc).
- Migration aplicada antes do deploy se schema mudar — não muda nesta sprint.
- Pra esta sprint o **front muda muito** — Lovable buida automático após push em main. Pos-deploy, abrir Lovable preview pra confirmar build verde antes de smoke.
