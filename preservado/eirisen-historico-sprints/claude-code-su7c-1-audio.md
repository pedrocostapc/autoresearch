# SU7c-1 — Áudio recebido → transcrição → IA processa

> Sub-sprint da SU7c (IA multimodal). Cliente envia áudio no WhatsApp,
> sistema transcreve via Deepgram Nova-3 (Whisper fallback), IA processa
> o texto. Inclui cobrança via FIFO existente, keywords customizáveis
> por tenant, e toggle de confirmação parafraseada.

---

## Contexto

### Estado atual

- Recepção de áudio: webhook salva em `messages` com `message_type='audio'` e `media_storage_path`. Funciona via SU7a.
- Front renderiza áudio com player (signed URL 1h via `useMessageMediaUrl`).
- IA processa **só texto**. Áudios são ignorados pelo prompt builder hoje.

### Gap

Cliente PC Construtora manda áudio "preciso 20 sacos de cimento Votoran" → IA não responde. Operador humano precisa abrir, ouvir, responder. Perde valor da automação.

### Decisões de produto

| # | Decisão | Default |
|---|---|---|
| 1 | Trial (R$3 credit) usa Deepgram normal, consome do crédito | sempre ligado |
| 2 | Keywords customizáveis por tenant (todos planos pagantes) | textarea no painel |
| 3 | Confirmação parafraseada como padrão | toggle libera resposta direta em high confidence |
| 4 | Cobrança apenas em transcrições com confidence > 0.6 | falhas absorvem na plataforma |
| 5 | Sem limite mensal duro — FIFO de crédito (3.0× markup) controla consumo | já existente |

### Engine: Deepgram Nova-3

- Top em PT-BR + ruído (perfil dos áudios — obras, lojas, clínicas)
- Keyword boost nativo (vocabulário customizável via query param)
- ~R$ 0,021/min de áudio (custo plataforma)
- LGPD compliant, DPA disponível, SOC 2
- Fallback automático: Whisper API se Deepgram retornar 5xx ou timeout >10s

---

## Escopo

### IN
- Migration: colunas em `messages` (transcription, confidence, provider, billable, duration) + colunas em `tenant_ai_configs` (audio_auto_respond, transcription_keywords)
- Helper `transcribeAudio` em `_shared/transcription.ts` com adapters Deepgram + Whisper, fallback automático
- Integração no `provider-webhook` quando `message_type='audio'`
- Atualização do prompt builder da IA pra incluir `[áudio transcrito]:` e instrução de confirmação
- Cobrança via sistema FIFO existente (transcrições billable consomem crédito)
- UI nova: textarea de keywords + toggle de auto-respond na tela de configuração de IA do tenant

### OUT
- Áudio enviado pelo agent (não tem caso de uso prioritário)
- Síntese de voz na resposta (TTS) — fica pra sub-sprint futura se demanda surgir
- Métricas/dashboard de qualidade de transcrição — vira sprint própria
- Tradução automática de áudio em outros idiomas

---

## Pré-requisitos

- Branch: `su7c-1-audio-transcription`
- Build + tsc + vitest verdes
- `main` pós-merge SU7b (#196)
- Secrets configurados:
  - `DEEPGRAM_API_KEY` (Pedro cria conta + gera key)
  - `OPENAI_API_KEY` já existe (fallback)

---

## Plano de execução

### Etapa 1 — Raio-x (sem codar)

Reportar antes de codar:

1. **Sistema de cobrança FIFO atual.** Onde IA registra consumo hoje? Provavelmente:
   - Tabela `ai_logs` ou `ai_usage` que cron diário agrega
   - RPC tipo `record_ai_usage(tenant_id, cost_cents, ...)`
   
   Reportar:
   - Caminho exato do código que registra hoje (ex: edge `ai-reply` chamando uma RPC)
   - Schema da tabela de log
   - Como markup 3.0× é aplicado (na hora do log ou na agregação?)

2. **Pipeline de processamento de mensagem recebida.** Onde fica a chamada que decide se IA responde? Provavelmente edge `ai-reply` ou similar. Reportar:
   - Caminho exato
   - Como contexto é montado (array de mensagens passadas pra IA)
   - Onde `tenant_ai_configs` é lido

3. **Tabela `tenant_ai_configs`.** Schema atual completo. Quero saber:
   - Se já tem campo similar a `audio_auto_respond`
   - Se já tem campo similar a `transcription_keywords` ou `vocabulary`
   - PK, RLS, defaults

4. **Bucket `tenant-media`.** Confirmar que áudios recebidos têm `media_storage_path` populado. Sample SQL:
   ```sql
   SELECT id, message_type, media_storage_path, media_size_bytes, created_at
   FROM messages
   WHERE message_type = 'audio'
   ORDER BY created_at DESC LIMIT 5;
   ```
   Cola resultado.

5. **UI atual de configuração de IA.** Provavelmente em `src/features/ai-settings/`. Reportar componente principal, abas existentes, padrão de form (react-hook-form? zod? shadcn?).

6. **Confirmar `DEEPGRAM_API_KEY` e `OPENAI_API_KEY` configuradas** no env das edges.

Não codar. Reportar findings.

### Etapa 2 — Migration

Arquivo: `supabase/migrations/<timestamp>_su7c_1_audio_transcription.sql`

```sql
-- SU7c-1: transcrição automática de áudio
ALTER TABLE messages
  ADD COLUMN IF NOT EXISTS transcription text,
  ADD COLUMN IF NOT EXISTS transcription_confidence numeric(4,3),
  ADD COLUMN IF NOT EXISTS transcription_provider text,
  ADD COLUMN IF NOT EXISTS transcription_billable boolean,
  ADD COLUMN IF NOT EXISTS transcription_duration_seconds numeric(10,2);

COMMENT ON COLUMN messages.transcription IS
  'Transcrição automática do áudio (SU7c-1). NULL pra mensagens não-áudio ou áudios sem transcrição ainda processada.';
COMMENT ON COLUMN messages.transcription_confidence IS
  'Confidence 0-1 retornado pelo provider. NULL se provider não retorna (Whisper).';
COMMENT ON COLUMN messages.transcription_provider IS
  'Provider usado: deepgram | openai (Whisper).';
COMMENT ON COLUMN messages.transcription_billable IS
  'TRUE quando confidence > 0.6 OU provider não retorna confidence. FALSE absorve no custo da plataforma.';
COMMENT ON COLUMN messages.transcription_duration_seconds IS
  'Duração do áudio em segundos. Usado pra cálculo de custo proporcional.';

-- Index pra dashboard de qualidade futura (não-bloqueante, baixa prioridade)
CREATE INDEX IF NOT EXISTS idx_messages_transcription_provider
  ON messages (transcription_provider, created_at DESC)
  WHERE transcription IS NOT NULL;

-- Tenant config: keywords e toggle de auto-respond
ALTER TABLE tenant_ai_configs
  ADD COLUMN IF NOT EXISTS audio_auto_respond boolean NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS transcription_keywords text;

COMMENT ON COLUMN tenant_ai_configs.audio_auto_respond IS
  'SU7c-1: false = IA sempre confirma transcrição antes de agir. true = IA responde direto quando confidence > 0.85.';
COMMENT ON COLUMN tenant_ai_configs.transcription_keywords IS
  'Termos do negócio do tenant pra keyword boost no Deepgram (separados por vírgula). Ex: "argamassa, porcelanato, Votoran". Reduz erro em vocabulário específico.';
```

Aplicar via SQL Editor + INSERT em `supabase_migrations.schema_migrations` (padrão Pedro). Setar `SUPABASE_DB_PASSWORD` env var pra próximas migrations.

### Etapa 3 — Helper de transcrição

`_shared/transcription.ts`:

```ts
export type TranscriptionResult =
  | {
      ok: true;
      text: string;
      confidence: number | null;
      provider: 'deepgram' | 'openai';
      durationSeconds: number;
    }
  | { ok: false; error: string; provider: 'deepgram' | 'openai' };

export type TranscribeArgs = {
  audioUrl: string;          // signed URL ou URL pública do bucket
  language?: string;          // 'pt-BR' default
  keywords?: string;          // string vinda de tenant_ai_configs.transcription_keywords
};

export async function transcribeAudio(args: TranscribeArgs): Promise<TranscriptionResult> {
  // 1. Tenta Deepgram
  const deepgramResult = await transcribeViaDeepgram(args);
  if (deepgramResult.ok) return deepgramResult;

  // 2. Fallback Whisper se Deepgram falhou (5xx ou timeout)
  console.warn(`[transcription] Deepgram falhou (${deepgramResult.error}), fallback Whisper`);
  const whisperResult = await transcribeViaWhisper(args);
  return whisperResult;
}
```

`_shared/providers/transcription/deepgram.ts`:

```ts
async function transcribeViaDeepgram(args: TranscribeArgs): Promise<TranscriptionResult> {
  const apiKey = Deno.env.get('DEEPGRAM_API_KEY');
  if (!apiKey) {
    return { ok: false, error: 'DEEPGRAM_API_KEY ausente', provider: 'deepgram' };
  }

  // Download bytes
  const audioRes = await fetchWithTimeout(args.audioUrl, { timeoutMs: 10_000 });
  if (!audioRes.ok) {
    return { ok: false, error: `download falhou: ${audioRes.status}`, provider: 'deepgram' };
  }
  const audioBytes = await audioRes.arrayBuffer();
  const contentType = audioRes.headers.get('content-type') ?? 'audio/ogg';

  // Build URL com query params
  const url = new URL('https://api.deepgram.com/v1/listen');
  url.searchParams.set('model', 'nova-3');
  url.searchParams.set('language', args.language ?? 'pt-BR');
  url.searchParams.set('smart_format', 'true');

  if (args.keywords && args.keywords.trim().length > 0) {
    // Cada keyword separadamente, peso 2 por padrão
    const terms = args.keywords.split(',').map(s => s.trim()).filter(Boolean);
    for (const term of terms) {
      url.searchParams.append('keywords', `${term}:2`);
    }
  }

  // POST com bytes direto no body
  const res = await fetchWithTimeout(url.toString(), {
    method: 'POST',
    headers: {
      'Authorization': `Token ${apiKey}`,
      'Content-Type': contentType,
    },
    body: audioBytes,
    timeoutMs: 30_000,
  });

  if (!res.ok) {
    const errText = await res.text();
    return {
      ok: false,
      error: `deepgram ${res.status}: ${errText.slice(0, 200)}`,
      provider: 'deepgram',
    };
  }

  const data = await res.json();
  const alt = data?.results?.channels?.[0]?.alternatives?.[0];
  const text = alt?.transcript ?? '';
  const confidence = typeof alt?.confidence === 'number' ? alt.confidence : null;
  const durationSeconds = typeof data?.metadata?.duration === 'number' ? data.metadata.duration : 0;

  return {
    ok: true,
    text,
    confidence,
    provider: 'deepgram',
    durationSeconds,
  };
}
```

`_shared/providers/transcription/whisper.ts`:

```ts
async function transcribeViaWhisper(args: TranscribeArgs): Promise<TranscriptionResult> {
  const apiKey = Deno.env.get('OPENAI_API_KEY');
  if (!apiKey) {
    return { ok: false, error: 'OPENAI_API_KEY ausente', provider: 'openai' };
  }

  // Download
  const audioRes = await fetchWithTimeout(args.audioUrl, { timeoutMs: 10_000 });
  if (!audioRes.ok) {
    return { ok: false, error: `download falhou: ${audioRes.status}`, provider: 'openai' };
  }
  const audioBlob = await audioRes.blob();

  const form = new FormData();
  form.append('file', audioBlob, 'audio.ogg');
  form.append('model', 'whisper-1');
  form.append('language', (args.language ?? 'pt-BR').slice(0, 2)); // Whisper usa código 2 letras

  const res = await fetchWithTimeout('https://api.openai.com/v1/audio/transcriptions', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${apiKey}` },
    body: form,
    timeoutMs: 60_000,
  });

  if (!res.ok) {
    const errText = await res.text();
    return {
      ok: false,
      error: `whisper ${res.status}: ${errText.slice(0, 200)}`,
      provider: 'openai',
    };
  }

  const data = await res.json();
  return {
    ok: true,
    text: data.text ?? '',
    confidence: null, // Whisper não retorna
    provider: 'openai',
    durationSeconds: 0, // Whisper não retorna duração — calcular do bytes se precisar
  };
}
```

Helper `fetchWithTimeout` simples em `_shared/fetch-utils.ts` se ainda não existe.

### Etapa 4 — Integrar no provider-webhook

No handler de `messages.upsert`, após save da row de áudio:

```ts
if (message.message_type === 'audio' && message.media_storage_path) {
  EdgeRuntime.waitUntil(
    transcribeAndUpdate(supabase, message, tenantConfig).catch(e =>
      console.warn('[transcription] falhou:', e)
    )
  );
}
```

Função `transcribeAndUpdate`:

```ts
async function transcribeAndUpdate(
  supabase: SupabaseClient,
  message: Message,
  tenantConfig: { transcription_keywords: string | null }
) {
  // 1. Signed URL 5min do bucket
  const { data: signed } = await supabase.storage
    .from('tenant-media')
    .createSignedUrl(message.media_storage_path, 300);
  if (!signed) return;

  // 2. Transcrever
  const result = await transcribeAudio({
    audioUrl: signed.signedUrl,
    language: 'pt-BR',
    keywords: tenantConfig.transcription_keywords ?? undefined,
  });

  if (!result.ok) {
    console.warn(`[transcription] failed for msg=${message.id}: ${result.error}`);
    // Não atualiza — mantém transcription=null. AI reply skipa esse áudio.
    return;
  }

  // 3. Determinar billable
  // - confidence null (Whisper) → billable=true (não temos como avaliar)
  // - confidence > 0.6 → billable=true
  // - confidence <= 0.6 → billable=false (absorve no custo)
  const billable = result.confidence === null || result.confidence > 0.6;

  // 4. UPDATE messages
  await supabase
    .from('messages')
    .update({
      transcription: result.text,
      transcription_confidence: result.confidence,
      transcription_provider: result.provider,
      transcription_billable: billable,
      transcription_duration_seconds: result.durationSeconds,
    })
    .eq('id', message.id);

  // 5. Registrar custo no FIFO (apenas se billable)
  if (billable) {
    await recordTranscriptionCost(supabase, {
      tenantId: message.tenant_id,
      durationSeconds: result.durationSeconds,
      provider: result.provider,
    });
  }

  console.log(`[transcription] msg=${message.id} provider=${result.provider} confidence=${result.confidence} billable=${billable} dur=${result.durationSeconds}s`);

  // 6. Re-disparar AI reply agora que tem transcrição
  // (depende de findings da Etapa 1 — pode ser RPC, fetch numa edge, ou setar flag)
  await retriggerAIReply(supabase, message);
}
```

### Etapa 5 — Cobrança no FIFO

Função `recordTranscriptionCost`:

```ts
async function recordTranscriptionCost(
  supabase: SupabaseClient,
  args: { tenantId: string; durationSeconds: number; provider: 'deepgram' | 'openai' }
) {
  // Custos base por provider (em centavos BRL)
  const COST_PER_MINUTE_BRL_CENTS = {
    deepgram: 2.1, // R$ 0,021/min
    openai: 3.0,   // R$ 0,030/min (Whisper)
  };

  const minutes = args.durationSeconds / 60;
  const baseCostCents = minutes * COST_PER_MINUTE_BRL_CENTS[args.provider];
  const markedUpCostCents = Math.ceil(baseCostCents * 3.0); // markup 3.0× existente

  // Chamar RPC existente (descobrir nome exato na Etapa 1)
  await supabase.rpc('record_ai_usage', {
    p_tenant_id: args.tenantId,
    p_cost_cents: markedUpCostCents,
    p_kind: 'transcription',
    p_meta: {
      provider: args.provider,
      duration_seconds: args.durationSeconds,
      base_cost_cents: baseCostCents,
    },
  });
}
```

**Nome da RPC exato vem da Etapa 1.** Se sistema atual debita em outra estrutura (ex: `ai_logs` insert direto), adapta. Se markup 3.0× é aplicado em outro lugar (ex: na agregação diária), tirar daqui pra evitar dupla aplicação.

### Etapa 6 — Atualizar prompt builder da IA

Onde o array de mensagens é montado pra mandar pra IA:

```ts
function buildMessageContent(msg: Message): string {
  if (msg.message_type === 'audio') {
    if (!msg.transcription) {
      // Áudio ainda não transcrito ou falhou
      return '[áudio recebido, transcrição pendente]';
    }
    if (msg.transcription_confidence !== null && msg.transcription_confidence < 0.6) {
      return `[áudio com baixa confiança de transcrição]: ${msg.transcription}`;
    }
    return `[áudio transcrito]: ${msg.transcription}`;
  }
  return msg.text ?? '';
}
```

E o **system prompt** do agent recebe instruções condicionais (lidas de `tenant_ai_configs.audio_auto_respond`):

```
Quando o usuário enviar uma mensagem marcada como [áudio transcrito]:
{{#if audio_auto_respond}}
- Se a confiança de transcrição é alta, você pode responder diretamente.
{{else}}
- Sempre parafraseie a transcrição e peça confirmação antes de qualquer ação executável (criar pedido, agendar, alterar dados).
- Para conversas simples (perguntas, dúvidas), responda direto sem parafrasear.
{{/if}}
- Se vier marcado [áudio com baixa confiança de transcrição], peça pro usuário enviar a mensagem por texto.
- Se vier marcado [áudio recebido, transcrição pendente], peça pra aguardar alguns segundos e tente novamente.
```

Implementação: o builder do system prompt lê `tenant_ai_configs.audio_auto_respond` e inclui o trecho correto.

### Etapa 7 — UI de configuração

No painel `/settings/ai` (ou onde mora a config de IA):

- **Aba "Áudio" nova** (ou seção dentro de aba existente):
  - Toggle "Responder áudios diretamente quando entender bem" (controla `audio_auto_respond`). Default OFF. Helper text: "Quando ligado, a IA responde direto se a transcrição vier com alta confiança. Quando desligado, a IA sempre confirma a transcrição antes de agir."
  - Textarea "Termos do seu negócio" (controla `transcription_keywords`). Placeholder: "argamassa, porcelanato, Votoran, MDF". Helper text: "Lista de termos específicos do seu negócio. Melhora a precisão da transcrição. Separe por vírgula."
  - Botão "Salvar"

Form usa padrão do projeto (react-hook-form + zod, ou padrão equivalente da Etapa 1).

### Etapa 8 — Testes

**Unit (vitest):**
- `transcribeViaDeepgram`: sucesso (mock fetch), 4xx, 5xx, timeout
- `transcribeViaWhisper`: sucesso, 4xx, 5xx
- `transcribeAudio`: tenta Deepgram primeiro, fallback Whisper se 5xx, propaga erro se ambos falham
- Cálculo de billable: confidence > 0.6, < 0.6, null
- `recordTranscriptionCost`: cálculo correto pra Deepgram + Whisper, markup 3.0×
- Builder de content: áudio transcrito, áudio sem transcrição, áudio low confidence

Build / tsc / vitest verdes.

### Etapa 9 — Smoke real

1. **Configurar tenant de teste** via UI: ligar audio_auto_respond=false (default), keywords vazias.
2. **Cliente teste manda áudio** no WhatsApp ("oi, queria saber preço de cimento Votoran").
3. **SQL imediato:**
   ```sql
   SELECT id, message_type, transcription, transcription_confidence, transcription_provider,
          transcription_billable, transcription_duration_seconds, created_at
   FROM messages
   WHERE created_at > NOW() - INTERVAL '2 minutes'
     AND message_type = 'audio'
   ORDER BY created_at DESC LIMIT 3;
   ```
   Esperado: row com transcription populada em ~2-5s, provider='deepgram', confidence presente.

4. **IA deve responder confirmando:** "Entendi que você quer saber o preço de cimento Votoran. Confirmo?"

5. **Toggle ON:** mudar audio_auto_respond=true. Manda outro áudio. IA responde direto sem confirmar.

6. **Keywords:** preenche "Votoran, argamassa, porcelanato". Manda áudio com esses termos pronunciados em ruído. Confidence sobe.

7. **Falha de transcrição:** manda áudio só de barulho. Deepgram retorna confidence baixa. SQL: `transcription_billable=false`. IA: "Não consegui entender bem seu áudio, pode mandar por texto?".

8. **Cobrança:** verifica que `record_ai_usage` foi chamado com kind='transcription' apenas pros billable=true. Conferir saldo do tenant antes/depois.

9. **Logs:** filtrar `[transcription]` em provider-webhook. Confirmar provider, confidence, billable, duration aparecem.

---

## Critérios de aceite

- [ ] Migration aplicada (`messages` + `tenant_ai_configs` com colunas novas)
- [ ] Helper `transcribeAudio` com Deepgram default + Whisper fallback
- [ ] Áudio recebido tem transcrição populada em <30s
- [ ] Cobrança via FIFO existente integrada (markup 3.0× aplicado uma vez)
- [ ] Confidence < 0.6 → não cobra
- [ ] AI reply respeita confidence + toggle audio_auto_respond
- [ ] UI de configuração com toggle + textarea de keywords funcional
- [ ] Logs distintos `[transcription]`
- [ ] Build / tsc / vitest verdes
- [ ] Smoke completo (passos 1-9 da Etapa 9)
- [ ] Não-regressão: mensagens texto continuam funcionando idênticas

---

## Notas

- **Áudio é assíncrono.** AI reply precisa skipar mensagens de áudio sem transcrição AINDA processada (`transcription IS NULL`). Quando `transcribeAndUpdate` finalizar, re-dispara o AI reply.
- **Race condition mínima.** Se cliente manda 2 áudios em sequência, podem disparar 2 transcrições paralelas + 2 AI replies. Aceitável — IA processa contextualizada.
- **Trial não tem regra especial.** Cliente em trial usa Deepgram igual aos pagantes, queima o R$3 conforme uso. Se acabar, IA para de responder até recarregar (comportamento existente).
- **Falhas absorvem custo.** Deepgram retornar 5xx + Whisper também → áudio não transcreve, plataforma não cobra. Cliente vê IA pedindo pra mandar por texto.
- **Keywords não acumulam.** Cada tenant tem sua própria lista. Cliente A não vê termos do cliente B.
- **Limite de tamanho de áudio.** WhatsApp limita áudio a ~16MB / ~10min. Deepgram aceita até 250MB. OK pra todos os casos.
- **LGPD.** Áudio é dado pessoal. Bucket já é private + RLS. Deepgram tem DPA. Whisper (OpenAI) tem DPA. Documentar em política de privacidade que áudios são processados por terceiros pra transcrição.

---

## Pós-merge

```bash
gh pr merge <PR_NUM> --squash --delete-branch
git checkout main && git pull origin main
# Migration: aplicar via SQL Editor manual (lição SUF10b)
# OU se SUPABASE_DB_PASSWORD configurado: supabase db push
supabase functions deploy provider-webhook
git push origin main
```

Confirmar via SQL Editor:
```sql
SELECT column_name FROM information_schema.columns
WHERE table_name = 'messages' AND column_name LIKE 'transcription%';
```

Esperado: 5 rows (transcription, _confidence, _provider, _billable, _duration_seconds).

---

## Branch e PR

- Branch: `su7c-1-audio-transcription`
- PR título: `feat(ai): transcrição de áudio via Deepgram + cobrança FIFO (SU7c-1)`
- PR descrição:
  - link pra este prompt
  - findings da Etapa 1 (RPC de cobrança, pipeline de AI reply, etc)
  - lista de arquivos tocados
  - smoke executado com SQL real e prints de UI

---

## Lembretes operacionais

- Migration **antes** do deploy de edge (lição SUF10b)
- `EdgeRuntime.waitUntil(promise)` pra background work pós-response (lição SUF10c)
- `grep -n` antes/depois de `replace_all` (lição SUF9)
- Logs distintos: `[transcription]`, `[transcription-cost]`
- Setar `SUPABASE_DB_PASSWORD` env var antes da próxima migration pra evitar chumbar SQL Editor
