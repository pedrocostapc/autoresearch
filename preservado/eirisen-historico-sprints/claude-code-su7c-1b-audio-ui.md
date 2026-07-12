# SU7c-1b — UI de configuração de áudio + toggle de habilitação

> Sub-sprint final do SU7c-1. Adiciona controles UI pra tenant configurar
> transcrição de áudio (ligar/desligar, comportamento, vocabulário) na
> aba Motor da página `/ia`.

---

## Contexto

SU7c-1 entregou áudio funcional fim-a-fim em produção:
- Deepgram Nova-3 + Whisper fallback
- Cobrança via FIFO (markup 3.3×)
- Confirmação parafraseada por default (`audio_auto_respond=false`)
- Keyword boost via `transcription_keywords`
- Hotfix da duplicação aplicado e validado

**Gap atual:** tenant não tem como mexer nas 2 configs (audio_auto_respond, transcription_keywords) — só via SQL Editor manual. E não existe toggle pra desligar transcrição inteira pro tenant que não quer pagar.

---

## Escopo

### IN
- Migration: coluna nova `tenant_ai_configs.audio_transcription_enabled boolean DEFAULT true`
- `_shared/ai-config.ts`: campo `audioTranscriptionEnabled`
- `provider-webhook`: gate antes de `transcribeAndDispatch` — se desligado, áudio entra no inbox mas IA não processa
- UI: nova seção "Áudio" na aba Motor da página `/ia`, depois de "IA pode criar tarefas" e antes de "Insights de atendimento"
  - Toggle "Transcrever áudios automaticamente" (default ON)
  - Toggle "Responder áudios diretamente quando entender bem" (default OFF)
  - Textarea "Termos do seu negócio"
  - Quando primeiro toggle OFF, esconde os outros 2

### OUT
- Limite mensal de transcrição
- Painel admin de uso/qualidade
- Toggle por conversação (sempre por tenant)

---

## Pré-requisitos

- Branch: `su7c-1b-audio-ui`
- `main` pós-merge SU7c-1 hotfix (PR #198)
- Build/tsc/vitest verdes

---

## Plano de execução

### Etapa 1 — Raio-x (sem codar)

Reportar antes:

1. **Caminho exato da página `/ia`** que tem aba "Motor" mostrada no print. Provavelmente `src/features/ai-settings/` ou similar. Caminho do componente da aba Motor.
2. **Padrão de form usado.** react-hook-form? zod? Como salva `tenant_ai_configs` hoje?
3. **Onde estão as outras seções da aba** (Identificação, Pausa, IA pode criar tarefas, Insights). Quero que a seção nova seja consistente com elas — mesmo padrão de card, espaçamento, tipografia.
4. **Hook de UPDATE** que persiste alterações em `tenant_ai_configs` (provavelmente `useTenantAIConfig` ou nome similar).

Reportar findings antes de codar.

### Etapa 2 — Migration

Arquivo: `supabase/migrations/<timestamp>_su7c1b_audio_transcription_toggle.sql`

```sql
ALTER TABLE public.tenant_ai_configs
  ADD COLUMN IF NOT EXISTS audio_transcription_enabled boolean NOT NULL DEFAULT true;

COMMENT ON COLUMN public.tenant_ai_configs.audio_transcription_enabled IS
  'SU7c-1b: liga/desliga transcrição automática de áudio. Default true. Quando false, áudios recebidos entram no inbox como mídia normal mas Deepgram não é chamado e IA não responde — operador humano trata.';
```

Aplicar via SQL Editor + INSERT em `supabase_migrations.schema_migrations` (padrão Pedro). Verificação:

```sql
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'tenant_ai_configs'
  AND column_name = 'audio_transcription_enabled';
```

### Etapa 3 — Atualizar `_shared/ai-config.ts`

Adicionar `audioTranscriptionEnabled` ao type `AIConfig`:

```ts
audioTranscriptionEnabled: boolean;
```

Em `getTenantAIConfig`:
```ts
audioTranscriptionEnabled: data.audio_transcription_enabled !== false, // default true
```

### Etapa 4 — Gate no `provider-webhook`

Em `processIncomingMessage`, no ponto onde chama `transcribeAndDispatch`:

```ts
if (messageType === "audio") {
  if (config.audioTranscriptionEnabled) {
    EdgeRuntime.waitUntil(transcribeAndDispatch(...));
  } else {
    console.log(`[transcription] tenant ${tenantId} tem transcrição desligada, skip`);
  }
}
```

Áudio continua entrando no inbox (UI mostra player). Apenas Deepgram não é chamado e IA não dispara resposta.

### Etapa 5 — UI: nova seção "Áudio" na aba Motor

Depois de "IA pode criar tarefas" e antes de "Insights de atendimento". Mesmo padrão de card que as outras seções.

Estrutura visual:

```
┌─ Áudios ─────────────────────────────────────────────────────────┐
│ Como a IA lida com áudios recebidos no WhatsApp.                 │
│                                                                  │
│ ─────────────                                                    │
│                                                                  │
│ Transcrever áudios automaticamente                    [TOGGLE]  │
│ Quando ligado, áudios são transcritos via IA e a                │
│ assistente pode responder com base no conteúdo. O custo da       │
│ transcrição é debitado do seu saldo (~R$ 0,08 por minuto).      │
│ Quando desligado, áudios chegam no inbox mas a assistente        │
│ não responde — você ouve e responde manualmente.                 │
│                                                                  │
│ ─────────────                                                    │
│ [só aparece se primeiro toggle ON]                               │
│                                                                  │
│ Responder direto quando entender bem                  [TOGGLE]  │
│ Quando desligado (recomendado), a assistente sempre              │
│ parafraseia o áudio e pede confirmação antes de tomar            │
│ qualquer ação. Quando ligado, ela responde direto se a           │
│ transcrição vier com alta confiança.                             │
│                                                                  │
│ ─────────────                                                    │
│                                                                  │
│ Termos do seu negócio                                            │
│ Lista de palavras específicas do seu negócio que melhoram a      │
│ precisão da transcrição. Separe por vírgula.                     │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ argamassa, porcelanato, Votoran, MDF                         │ │
│ └──────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

Implementação:

- Toggle 1: bind em `audio_transcription_enabled` (boolean, padrão verde do projeto)
- Toggle 2: bind em `audio_auto_respond` (boolean)
- Textarea: bind em `transcription_keywords` (text[] no banco)
  - Front recebe array, mostra como CSV: `keywords.join(', ')`
  - Front salva: `value.split(',').map(s => s.trim()).filter(Boolean)`
  - Validação zod: cada elemento <= 50 chars, máximo 30 termos

Quando toggle 1 OFF, esconder div com toggle 2 + textarea (animação simples opcional).

Salvar via mesmo botão "Salvar" que já existe no fim da aba Motor (não duplicar).

### Etapa 6 — Smoke

**Cenário A — Toggle transcrição OFF (recurso desligado):**
1. Tenant teste, abre /ia, desliga "Transcrever áudios"
2. Salva
3. Manda áudio do celular pro número
4. SQL: `SELECT transcription FROM messages WHERE message_type='audio' ORDER BY created_at DESC LIMIT 1;` → deve ser `NULL`
5. Logs `[transcription]` deve aparecer "tenant X tem transcrição desligada, skip"
6. IA não responde no WhatsApp
7. Mensagem de áudio aparece no inbox normal

**Cenário B — Toggle ON + auto_respond OFF (default):**
1. Liga toggle de transcrição, deixa auto_respond OFF
2. Manda áudio "que horas vocês abrem"
3. IA confirma parafraseado: "você quer saber nosso horário?"

**Cenário C — Toggle ON + auto_respond ON:**
1. Liga ambos toggles
2. Manda áudio "que horas vocês abrem"
3. IA responde direto: "abrimos das 8h às 18h"

**Cenário D — Keywords:**
1. Adiciona "Votoran, argamassa" no textarea, salva
2. Manda áudio em ambiente ruidoso falando "cimento Votoran"
3. SQL conferindo `transcription` deve ter "Votoran" escrito certo (não "votarán" ou "votado")

### Etapa 7 — Critérios de aceite

- [ ] Migration aplicada
- [ ] `audioTranscriptionEnabled` em `_shared/ai-config.ts` lido corretamente
- [ ] Gate em `provider-webhook` skipa transcrição quando OFF
- [ ] UI renderiza nova seção "Áudio" na aba Motor
- [ ] Toggle 1 OFF esconde toggle 2 + textarea
- [ ] Save persiste em `tenant_ai_configs` corretamente (boolean + array)
- [ ] CSV ⇄ array no textarea funciona em ambas direções (load + save)
- [ ] Build / tsc / vitest verdes
- [ ] Smoke completo (A, B, C, D)
- [ ] Não-regressão: outras seções da aba Motor continuam funcionando

---

## Pós-merge

```bash
gh pr merge <PR> --squash --delete-branch
git checkout main && git pull origin main
# Migration: aplicar via SQL Editor manual antes do deploy
supabase functions deploy provider-webhook
git push origin main
```

Lovable rebuilda front automático após push.

---

## Branch e PR

- Branch: `su7c-1b-audio-ui`
- PR título: `feat(ai): UI de configuração de áudio + toggle de habilitação (SU7c-1b)`
- PR descrição:
  - link pro prompt
  - findings da Etapa 1
  - lista de arquivos tocados
  - smoke executado (4 cenários)
  - print da nova seção UI

---

## Lembretes operacionais

- Migration **antes** do deploy
- `grep -n` antes/depois de `replace_all`
- Logs `[transcription] skip` distintos
- Manter padrão visual consistente com outras seções da aba Motor
- Smoke real fim-a-fim antes de fechar PR
