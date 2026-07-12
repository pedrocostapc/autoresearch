# PR5 Sprint Schedule — Webhook receiver Google→CRM + cron pull conciliatório

> **Sync inverso.** Quando alguém edita evento no Google Calendar (tenant, Risen OS, ou outro sistema), CRM detecta e atualiza appointment.
>
> Estimativa: ~1 dia.
> Branch: `schedule-pr5-webhook-sync`

---

## Contexto

PR4 entregou: tabelas appointments + appointment_google_sync, edge push CRM→Google, mutations no front.

**PR5 entrega o sentido inverso (Google→CRM):**
- Edge `google-calendar-webhook` recebe push do Google
- Tabela `webhook_channels` (registra canais de notificação)
- Setup script (registra webhook channel por calendar)
- Cron pull conciliatório (varre eventos a cada X minutos pra cobrir webhook perdido)
- Conflict resolution: last-write-wins via `updated_at`/etag
- Filtro: ignora eventos com `risen_source = "risen_os"` (são do outro sistema)

**Não entrega:**
- Tools IA (PR6)
- Lógica de auto-pick resource (PR6)
- UI de notificações de mudança (futuro)

---

## Arquitetura

```
Tenant edita evento no Google Calendar app
   ↓
Google envia POST → CRM edge webhook
   ↓
Edge identifica:
- Qual tenant via professional_calendars
- Qual appointment via extendedProperties.crm_appointment_id
   ↓
Edge atualiza appointment (last-write-wins via updated_at)
   ↓
appointment_google_sync.last_synced_at atualizado
```

E em paralelo:

```
Cron job roda a cada 10min
   ↓
Pra cada professional_calendar com sync_status != 'pending':
   - Lista eventos modificados desde last_synced_at
   - Pra cada evento com risen_source = 'crm_whats':
     - Compara com appointment local
     - Se Google mais recente → update local
     - Se local mais recente → push Google (re-sync)
```

---

## Schema da tabela `webhook_channels`

Google requer registro de channel pra receber push notifications. Cada channel expira em até 7 dias e precisa ser renovado.

```sql
CREATE TABLE public.webhook_channels (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Identificação
  channel_id text NOT NULL,           -- UUID gerado por nós, identifica o channel no Google
  resource_id text NOT NULL,          -- Retornado pelo Google ao registrar
  
  -- Vinculação
  google_calendar_id text NOT NULL,
  professional_calendar_id uuid NOT NULL 
    REFERENCES public.professional_calendars(id) ON DELETE CASCADE,
  
  -- Expiração
  expiration_at timestamptz NOT NULL,
  
  -- Audit
  created_at timestamptz NOT NULL DEFAULT now(),
  renewed_at timestamptz,
  
  UNIQUE (channel_id),
  UNIQUE (google_calendar_id)
);

CREATE INDEX idx_webhook_channels_expiration 
  ON public.webhook_channels (expiration_at);
CREATE INDEX idx_webhook_channels_calendar 
  ON public.webhook_channels (google_calendar_id);
```

RLS DENY-by-default (igual `appointment_google_sync`). Só service_role acessa.

---

## Edge `google-calendar-webhook`

Recebe POST do Google quando algo muda em algum calendar registrado.

### Headers que Google manda
- `X-Goog-Channel-ID` — identifica o channel
- `X-Goog-Channel-Token` — token de validação (definimos ao registrar)
- `X-Goog-Resource-ID` — recurso afetado
- `X-Goog-Resource-State` — tipo de mudança (`exists`, `not_exists`, `sync`)
- `X-Goog-Resource-URI` — URI do recurso
- `X-Goog-Message-Number` — sequência

### Lógica:

```ts
serve(async (req) => {
  // 1. Valida header X-Goog-Channel-Token
  const token = req.headers.get("X-Goog-Channel-Token");
  if (token !== Deno.env.get("GOOGLE_WEBHOOK_TOKEN")) {
    return new Response("unauthorized", { status: 401 });
  }
  
  // 2. Pega channel_id
  const channelId = req.headers.get("X-Goog-Channel-ID");
  const resourceState = req.headers.get("X-Goog-Resource-State");
  
  // 3. Se for "sync" (notification inicial), só retorna 200
  if (resourceState === "sync") {
    return new Response("ok", { status: 200 });
  }
  
  // 4. Busca webhook_channel
  const { data: channel } = await supabase
    .from("webhook_channels")
    .select("google_calendar_id, professional_calendar_id")
    .eq("channel_id", channelId)
    .single();
  
  if (!channel) {
    return new Response("channel not found", { status: 404 });
  }
  
  // 5. Lista eventos modificados desde last_synced
  const lastSync = await getLastSyncForCalendar(channel.google_calendar_id);
  const events = await listGoogleEvents(channel.google_calendar_id, lastSync);
  
  // 6. Pra cada evento, reconcilia
  for (const event of events) {
    await reconcileEvent(event, channel.professional_calendar_id);
  }
  
  // 7. Atualiza last_synced
  await updateLastSync(channel.google_calendar_id);
  
  return new Response("ok", { status: 200 });
});

async function reconcileEvent(event, professionalCalendarId) {
  const source = event.extendedProperties?.private?.risen_source;
  
  // Ignora eventos do Risen OS
  if (source === "risen_os") return;
  
  const crmAppointmentId = event.extendedProperties?.private?.crm_appointment_id;
  
  if (source === "crm_whats" && crmAppointmentId) {
    // Evento criado por nós, foi editado externamente
    await updateAppointmentFromGoogle(crmAppointmentId, event);
  } else {
    // Evento criado manualmente no Google Calendar pelo tenant
    // Cria appointment local
    await createAppointmentFromGoogle(event, professionalCalendarId);
  }
}
```

### Conflict resolution

```ts
async function updateAppointmentFromGoogle(appointmentId, event) {
  const { data: appt } = await supabase
    .from("appointments")
    .select("*, appointment_google_sync(*)")
    .eq("id", appointmentId)
    .single();
  
  // Compara timestamps
  const localUpdated = new Date(appt.updated_at).getTime();
  const googleUpdated = new Date(event.updated).getTime();
  
  if (googleUpdated > localUpdated) {
    // Google é mais recente — atualiza local
    await supabase.from("appointments").update({
      start_at: event.start.dateTime,
      end_at: event.end.dateTime,
      notes: event.description,
      status: event.status === "cancelled" ? "cancelled" : appt.status,
    }).eq("id", appointmentId);
    
    await supabase.from("appointment_google_sync").update({
      last_synced_at: new Date().toISOString(),
      google_etag: event.etag,
    }).eq("appointment_id", appointmentId);
  }
  // Senão, local é mais recente — não faz nada (push CRM→Google já é feito pela mutation)
}
```

---

## Edge `google-calendar-webhook-setup`

Script pra registrar webhook channel pra um calendar.

Chamado uma vez por cada calendar provisionado (ou na renovação).

```ts
POST /functions/v1/google-calendar-webhook-setup

Body:
{
  professional_calendar_id: string,
  google_calendar_id: string
}

Response:
{
  channel_id: string,
  resource_id: string,
  expiration_at: timestamp
}
```

### Lógica:

```ts
async function setupWebhookChannel(professionalCalendarId, googleCalendarId) {
  const channelId = crypto.randomUUID();
  const token = Deno.env.get("GOOGLE_WEBHOOK_TOKEN");
  const webhookUrl = `${Deno.env.get("SUPABASE_URL")}/functions/v1/google-calendar-webhook`;
  
  const accessToken = await getGoogleAccessToken();
  
  const res = await fetch(
    `https://www.googleapis.com/calendar/v3/calendars/${googleCalendarId}/events/watch`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        id: channelId,
        type: "web_hook",
        address: webhookUrl,
        token: token,
        expiration: Date.now() + 7 * 24 * 60 * 60 * 1000, // 7 dias
      }),
    }
  );
  
  if (!res.ok) {
    throw new Error(`Watch failed: ${await res.text()}`);
  }
  
  const { id, resourceId, expiration } = await res.json();
  
  // Salva no DB
  await supabase.from("webhook_channels").insert({
    channel_id: id,
    resource_id: resourceId,
    google_calendar_id: googleCalendarId,
    professional_calendar_id: professionalCalendarId,
    expiration_at: new Date(parseInt(expiration)).toISOString(),
  });
  
  return { channel_id: id, resource_id: resourceId, expiration_at: expiration };
}
```

---

## Cron pull conciliatório

Roda a cada 10 minutos via Supabase cron (`pg_cron` ou edge schedulada).

### Edge `google-calendar-pull-conciliation`

```ts
serve(async (req) => {
  // 1. Busca todos professional_calendars com sync ativo
  const { data: calendars } = await supabase
    .from("professional_calendars")
    .select("id, google_calendar_id")
    .in("provisioning_status", ["provisioned", "shared"]);
  
  // 2. Pra cada calendar, lista eventos modificados nos últimos 30min
  const cutoff = new Date(Date.now() - 30 * 60 * 1000).toISOString();
  
  for (const cal of calendars) {
    try {
      await pullCalendar(cal, cutoff);
    } catch (e) {
      console.error(`Pull failed for ${cal.id}:`, e);
    }
  }
  
  // 3. Renova webhook channels expirando em <24h
  await renewExpiringChannels();
  
  return new Response("ok");
});

async function pullCalendar(cal, since) {
  const accessToken = await getGoogleAccessToken();
  
  const res = await fetch(
    `https://www.googleapis.com/calendar/v3/calendars/${cal.google_calendar_id}/events?updatedMin=${since}&singleEvents=true`,
    { headers: { Authorization: `Bearer ${accessToken}` } }
  );
  
  const { items } = await res.json();
  
  for (const event of items) {
    await reconcileEvent(event, cal.id);
  }
}
```

### Setup do cron

Via SQL Editor (Pedro roda):

```sql
SELECT cron.schedule(
  'google-calendar-pull-conciliation',
  '*/10 * * * *',  -- a cada 10min
  $$
  SELECT net.http_post(
    url := 'https://qbclqjkvovfriuhshkpw.supabase.co/functions/v1/google-calendar-pull-conciliation',
    headers := jsonb_build_object(
      'Authorization', 'Bearer ' || current_setting('app.settings.service_role_key')
    )
  );
  $$
);
```

---

## Etapa 1 — Confirmações antes de codar

### A. Decisões pendentes

#### A1. GOOGLE_WEBHOOK_TOKEN — gerar e armazenar

Token aleatório longo, armazenado como secret no Supabase. Edge valida headers do Google contra esse token.

**Pedro precisa:**
1. Gerar token (uuid + sha256 ou similar)
2. Adicionar como secret: `supabase secrets set GOOGLE_WEBHOOK_TOKEN=<valor>`

#### A2. Setup automático após provisionamento

Quando `google-calendar-provision` (PR1) provisiona com sucesso, chama `google-calendar-webhook-setup` automático?

**Opções:**

**A — Automático:** edge `google-calendar-provision` chama webhook-setup ao final
- Vantagem: sem ação manual
- Desvantagem: provisioning fica mais lento

**B — Sob demanda:** Setup só rola via cron quando detecta calendar sem channel
- Vantagem: separação de concerns
- Desvantagem: latência inicial (até 10min pra primeiro evento ser detectado)

**C — Botão na UI:** tenant clica "Ativar sync bidirecional" depois de provisionar
- Vantagem: explícito
- Desvantagem: friction extra

**Recomendação: A.** Provisioning + setup atomicamente. Cliente esperar 1-2s a mais é aceitável.

**Mas hotfix no PR1:** edge `google-calendar-provision` ganha chamada interna pra webhook-setup quando provisioning succeeds. Code decide se faz como sub-PR ou no PR5.

#### A3. Renovação automática de channels expirando

Google channel expira em 7 dias. Cron precisa renovar antes.

**Lógica:** cron varre `webhook_channels` com `expiration_at < now() + 1 day`, chama renovação (delete + recreate).

#### A4. Conflict resolution — granularidade

Last-write-wins via timestamps. Mas:
- Tenant edita evento no Google às 14h05
- IA edita appointment no CRM às 14h08
- Push CRM→Google chega às 14h08:30
- Webhook Google→CRM (do 14h05) chega às 14h09

Risco: webhook do 14h05 chega depois e sobrescreve a mudança do 14h08.

**Solução:** comparar **timestamps de origem** (não de chegada). Google `event.updated` vs CRM `appointment.updated_at`. O mais recente vence.

Já está na lógica proposta. **Confirmar.**

#### A5. Eventos criados manualmente no Google Calendar pelo tenant

Tenant abre Google Calendar app, cria evento manual lá ("Reunião do nada"). Webhook detecta.

**Devemos criar appointment local?** 2 opções:

**A — Sim, espelhar:** todo evento no Google vira appointment no CRM
- Vantagem: visibilidade total no painel
- Desvantagem: pode poluir com eventos pessoais

**B — Não, ignorar:** só rastreamos eventos criados pelo CRM (com `risen_source = "crm_whats"`)
- Vantagem: CRM só tem dados que ele criou
- Desvantagem: cliente vê 2 lugares (Google + CRM) com info diferente

**Recomendação: B.** Razões:
- Tenant pode usar Google Calendar pra coisas pessoais (almoço, dentista, etc) — não deve aparecer no CRM
- CRM é fonte de agendamentos comerciais
- Se tenant quiser que CRM saiba, cria via CRM/IA

**Mas:** quando evento criado por nós for editado manualmente no Google, sincamos de volta. Esse é o ponto principal do webhook.

#### A6. Cron interval

10 minutos é razoável? 5min seria mais reativo, 15min menos carga.

**Recomendação: 10min.** Trade-off equilibrado.

#### A7. RLS webhook_channels

DENY-by-default. Só service_role.

#### A8. Service role key acessível no cron

`pg_cron` precisa do service_role key pra autenticar a chamada HTTP. Setting `app.settings.service_role_key` configurado no Supabase.

Pedro pode precisar configurar via SQL.

---

## Aguarda OK + escolhas em A1-A8 antes de prosseguir.

---

## Etapa 2 — Migration

```sql
-- supabase/migrations/<timestamp>_pr5_webhook_channels.sql

CREATE TABLE IF NOT EXISTS public.webhook_channels (
  -- ... schema completo conforme spec
);

-- RLS DENY-by-default
ALTER TABLE public.webhook_channels ENABLE ROW LEVEL SECURITY;
-- Nenhuma policy = nenhum acesso via PostgREST. service_role bypassa.
```

Pedro roda no SQL Editor.

---

## Etapa 3 — Secrets + cron

Pedro precisa:

```bash
supabase secrets set GOOGLE_WEBHOOK_TOKEN=<token gerado>
```

E rodar setup do cron no SQL Editor (depois das edges deployadas).

---

## Etapa 4 — Edges

3 edges novas:
- `google-calendar-webhook` (recebe Google push)
- `google-calendar-webhook-setup` (registra channel)
- `google-calendar-pull-conciliation` (cron pull)

Todas reusam `_shared/google-auth.ts` (PR1).

---

## Etapa 5 — Hotfix PR1 (opcional, A2 decision)

Se A2=A (automático), `google-calendar-provision` ganha chamada interna pra webhook-setup ao final.

---

## Etapa 6 — Cleanup + deploy

### Antes do deploy

**1) Migration webhook_channels (Pedro roda).**

**2) Confirma:**
```sql
SELECT COUNT(*) FROM public.webhook_channels;
```

**3) Secret GOOGLE_WEBHOOK_TOKEN setado.**

### Deploy

```bash
gh pr merge <PR> --squash --delete-branch
git checkout main && git pull origin main
supabase functions deploy google-calendar-webhook
supabase functions deploy google-calendar-webhook-setup
supabase functions deploy google-calendar-pull-conciliation
git push origin main
```

### Validação pós-deploy

1. Provisiona calendar via UI ou curl (PR1)
2. Edge webhook-setup roda → channel registrado em webhook_channels
3. Cria evento no Google Calendar app
4. Webhook recebe push (verificar logs)
5. Edita evento no Google Calendar app que foi criado pelo CRM
6. Webhook detecta → appointment local atualiza

---

## Critérios de aceite

- [ ] Etapa 1 confirmação aprovada
- [ ] Migration `webhook_channels`
- [ ] 3 edges deployadas
- [ ] Secret `GOOGLE_WEBHOOK_TOKEN` setado
- [ ] Cron job configurado (10min)
- [ ] Conflict resolution last-write-wins implementado
- [ ] Filtro `risen_source != "risen_os"` aplicado
- [ ] Build/test verde

---

## Restrições

- ❌ Sem tools IA (PR6)
- ❌ Sem UI de notificações
- ❌ Sem espelhamento de eventos criados manualmente no Google (A5=B)
- ✅ Branch: `schedule-pr5-webhook-sync`
- ✅ PR título: `feat(schedule): webhook receiver + cron pull conciliatório (PR5)`

---

## Pós-merge — Próximo: PR6 (Último da Sprint Schedule!)

PR6 entrega:
- Tools IA: `search_team_slots`, `create_appointment`, `reschedule`, `cancel`
- Lógica de auto-pick `resource_id` quando `max_parallel_resources > 1`
- Lógica de buffer antes/depois ao calcular slots
- Compiler `formatCalendarConfig` emite caixas Calendar Config + Calendar Links no contexto
- Helper de `default_duration_minutes` ajustado (puxa de Services/Events)
- Smoke real com tenant cobaia

Após PR6 → **Sprint Schedule COMPLETA**.

---

## O que NÃO fazer neste PR

- ❌ Tools IA (PR6)
- ❌ UI de mudanças
- ❌ Espelhar eventos pessoais do Google (A5=B)
- ❌ Conflict resolution complexa (last-write-wins simples basta)
