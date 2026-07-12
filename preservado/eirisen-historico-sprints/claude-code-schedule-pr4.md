# PR4 Sprint Schedule — Tabela appointments + edge push CRM→Google

> **Backend de agendamentos.** Tabelas `appointments` + `appointment_google_sync` + edge push. Sem UI ainda.
>
> Estimativa: ~1 dia.
> Branch: `schedule-pr4-appointments`

---

## Contexto

PR1-PR3 entregaram: tabela `professional_calendars`, caixas Calendar Config + Calendar Links, UI de provisionamento.

**PR4 entrega backend de agendamentos:**
- Tabela `appointments` (1 row = 1 agendamento)
- Tabela `appointment_google_sync` (mapping CRM ↔ Google event)
- Edge `google-calendar-push` (CRM → Google)
- Mutations no front (useCreateAppointment, useUpdateAppointment, useCancelAppointment)
- Suporte a `resource_id` (cases de capacidade paralela conforme hotfix Calendar Config)

**Não entrega:**
- Painel visual de appointments (futura sprint UI)
- Webhook receiver Google → CRM (PR5)
- Cron pull conciliatório (PR5)
- Tools IA (PR6)

---

## Schema da tabela `appointments`

```sql
CREATE TABLE public.appointments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
  
  -- Identificação do agendamento
  professional_id text,
  -- ↑ ID do item dentro de persona_boxes.data.items (caixa Team).
  --   Nullable pra eventos do estabelecimento (locação de espaço, etc).
  service_id text,
  -- ↑ Idem pra item de Services. Opcional.
  resource_id text,
  -- ↑ Identificador de recurso paralelo (ex: "machine_01"). 
  --   Sistema gera/escolhe automático quando max_parallel_resources > 1.
  
  -- Cliente
  customer_name text NOT NULL,
  customer_phone text NOT NULL,
  customer_email text,
  
  -- Tempo
  start_at timestamptz NOT NULL,
  end_at timestamptz NOT NULL,
  
  -- Status e metadata
  status text NOT NULL DEFAULT 'confirmed'
    CHECK (status IN ('confirmed', 'rescheduled', 'cancelled', 'no_show', 'completed')),
  notes text,
  cancellation_reason text,
  
  -- Origem
  created_via text NOT NULL DEFAULT 'ai_whatsapp'
    CHECK (created_via IN ('ai_whatsapp', 'manual_crm', 'manual_google_cal')),
  created_by_user_id uuid REFERENCES auth.users(id),
  
  -- Audit
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  cancelled_at timestamptz,
  
  -- Constraints
  CONSTRAINT appointments_time_valid CHECK (end_at > start_at),
  CONSTRAINT appointments_cancellation_consistent 
    CHECK (
      (status = 'cancelled' AND cancelled_at IS NOT NULL)
      OR (status != 'cancelled' AND cancelled_at IS NULL)
    )
);

CREATE INDEX idx_appointments_tenant_start ON public.appointments (tenant_id, start_at);
CREATE INDEX idx_appointments_professional ON public.appointments (tenant_id, professional_id) WHERE professional_id IS NOT NULL;
CREATE INDEX idx_appointments_resource ON public.appointments (tenant_id, resource_id) WHERE resource_id IS NOT NULL;
CREATE INDEX idx_appointments_status ON public.appointments (tenant_id, status);
CREATE INDEX idx_appointments_phone ON public.appointments (tenant_id, customer_phone);

CREATE TRIGGER appointments_updated_at
  BEFORE UPDATE ON public.appointments
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
```

## Schema `appointment_google_sync`

```sql
CREATE TABLE public.appointment_google_sync (
  appointment_id uuid PRIMARY KEY REFERENCES public.appointments(id) ON DELETE CASCADE,
  
  -- Google
  google_event_id text NOT NULL,
  google_calendar_id text NOT NULL,
  
  -- Sync state
  last_synced_at timestamptz NOT NULL DEFAULT now(),
  sync_status text NOT NULL DEFAULT 'synced'
    CHECK (sync_status IN ('synced', 'pending', 'error')),
  error_message text,
  
  -- Etag pra conflict detection (PR5 webhook usa)
  google_etag text,
  
  UNIQUE (google_calendar_id, google_event_id)
);

CREATE INDEX idx_appt_sync_status ON public.appointment_google_sync (sync_status);
CREATE INDEX idx_appt_sync_event ON public.appointment_google_sync (google_event_id);
```

## Edge `google-calendar-push`

Responsável por sincronizar CRM → Google. Recebe `appointment_id` + `action`:

```ts
POST /functions/v1/google-calendar-push

Body:
{
  appointment_id: string,
  action: 'create' | 'update' | 'delete'
}

Response:
{
  success: boolean,
  google_event_id?: string,
  google_etag?: string,
  error_message?: string
}
```

### Lógica:

**Action `create`:**
1. Lê appointment + professional_calendar (busca calendar do profissional ou estabelecimento)
2. Constroi evento Google:
   ```json
   {
     "summary": "[serviço]: [nome do cliente]",
     "description": "Telefone: [phone]\nServiço: [service_label]\nObservações: [notes]",
     "start": { "dateTime": start_at, "timeZone": tenant_timezone },
     "end": { "dateTime": end_at, "timeZone": tenant_timezone },
     "extendedProperties": {
       "private": {
         "risen_source": "crm_whats",
         "crm_appointment_id": appointment_id,
         "resource_id": resource_id
       }
     }
   }
   ```
3. POST `/calendar/v3/calendars/{calendarId}/events`
4. Insert `appointment_google_sync` com `google_event_id` retornado

**Action `update`:**
1. Lê sync existente pra pegar `google_event_id`
2. PUT `/calendar/v3/calendars/{calendarId}/events/{eventId}`
3. Atualiza `last_synced_at` + `google_etag`

**Action `delete`:**
1. DELETE `/calendar/v3/calendars/{calendarId}/events/{eventId}`
2. Marca `sync_status = 'synced'` (não deleta a row, mantém pra histórico)
3. Appointment status já está como 'cancelled'

---

## Etapa 1 — Confirmações antes de codar

### A. Schema das tabelas — confirma cobertura

Olha o schema proposto acima. Conferir se cobre:
- Capacidade paralela (resource_id) ✓
- Cancelamento com motivo ✓
- Múltiplas origens (ai_whatsapp / manual_crm / manual_google_cal) ✓
- Constraint de tempo válido ✓
- Audit completo ✓

### B. Decisões pendentes

#### B1. Trigger DB vs chamada explícita pela aplicação

Documento original da Sprint Schedule mencionava "trigger automático push em mudança de appointment".

**Opções:**

**A — Trigger DB chamando edge via `pg_net`:**
- AFTER INSERT/UPDATE/DELETE → trigger chama HTTP
- Vantagem: automático, garante consistência
- Desvantagem: complexidade, rate limits, falhas silenciosas, difícil debugar

**B — Aplicação chama edge explicitamente:**
- Cada mutation no front (useCreateAppointment, etc) chama edge depois de inserir
- Vantagem: contexto da aplicação, retry visível ao user, fácil debug
- Desvantagem: lógica espalhada (mas centralizável em hook)

**Recomendação: B (aplicação chama).** Razões:
- Trigger DB chamando edge HTTP é anti-pattern (failure modes complexos)
- Aplicação tem contexto pra mostrar erro ao user, fazer retry, etc
- Não tem precedente de trigger HTTP no projeto
- PR5 cuida do inverso (Google → CRM via webhook + cron) que é assíncrono natural

**Confirmar.** Se Pedro preferir trigger DB, ajusto.

#### B2. `professional_id` opcional permitido?

Casos sem profissional específico:
- Locação de espaço (calendar é do estabelecimento)
- Festa em salão de eventos
- Aluguel de chopeira (resource paralelo)

**Confirmar:** nullable. Schema declara assim.

#### B3. Lookup do calendar pra push

Edge precisa saber qual Google Calendar usar pra cada appointment. Lógica:

1. Se `professional_id` informado → busca `professional_calendars` por `linked_professional_id = professional_id`
2. Se `professional_id` null → busca `professional_calendars` com `link_type = 'establishment'`
3. Se múltiplos calendars do estabelecimento (raro) → primeiro encontrado
4. Se nenhum → erro "Nenhum calendário linkado pra esse profissional/estabelecimento"

#### B4. Suporte a múltiplos calendars por appointment (caso piscina + salão)

Hipótese: cliente reserva combo "Salão + Piscina" → evento aparece em 2 calendars.

**Opções:**
- A) Schema atual: 1 appointment = 1 calendar. Combo vira 2 appointments separados.
- B) Schema novo: 1 appointment com array de `google_calendar_ids[]`.

**Recomendação: A.** Razões:
- Combo é raro
- Schema simples cobre 95% dos casos
- Quando precisar (PR6 ou futuro), implementa lógica de criar 2 appointments linkados

**Confirmar.**

#### B5. Resource_id — quem escolhe?

Quando `max_parallel_resources > 1`:

**Opções:**
- A) Aplicação escolhe ao criar appointment (lógica: busca primeiro resource livre, atribui)
- B) Vazio, sistema preenche automático quando push pra Google
- C) Cliente do tenant escolhe na UI

**Recomendação: A (aplicação escolhe).** Razões:
- Lógica fica no momento da criação (centralizada)
- UI/IA não precisa expor detalhe do resource pro cliente final ("vou marcar pra máquina 03")
- Pode mudar resource depois sem afetar cliente

Mas: **lógica de "escolher resource livre" é complexa.** Vai pra PR6 (tools IA). PR4 só armazena o campo, deixa null.

Logo:
- PR4 = schema permite `resource_id`, mas mutations não atribuem ainda
- PR6 = lógica em `create_appointment` busca resource livre e preenche

**Confirmar.**

#### B6. Notification ao cliente do tenant

Quando appointment é criado, o profissional/estabelecimento já vê no Google Calendar dele (porque calendar é compartilhado).

**Sem email/notification extra nesta PR.** Email vai pelo próprio Google Calendar (que notifica owner automaticamente quando evento é criado).

**Confirmar.**

#### B7. Tabela `appointments` deve ter `service_id`?

Service em Services tem `id` em `data.items`. Reference text.

Casos:
- Cliente marca "corte de cabelo com Maria" → `professional_id = maria_id`, `service_id = corte_id`
- Cliente aluga chopeira → `professional_id = null`, `service_id = chopp_id` (ou null)

**Confirmar.** Schema declara nullable.

#### B8. Customer fields — opcional `customer_email`?

Telefone é obrigatório (vem do WhatsApp). Email opcional.

**Confirmar.**

#### B9. Status enum — completude

Proposta: `confirmed / rescheduled / cancelled / no_show / completed`

- `confirmed` = criado, ainda não passou da data
- `rescheduled` = (DEPRECATED? rescheduling é update normal do start/end)
- `cancelled` = cancelado, com `cancelled_at` e `cancellation_reason`
- `no_show` = cliente não compareceu
- `completed` = atendimento realizado (PR futuro pode disparar status update via cron)

**Decisão:** remover `rescheduled` (não faz sentido, update altera start/end direto).

Status final: `confirmed / cancelled / no_show / completed`.

**Confirmar.**

#### B10. RLS

Mesmo pattern de `professional_calendars`:
```sql
USING (
  tenant_id = public.get_user_tenant_id()
  OR public.is_super_admin(auth.uid())
)
```

Insert/Update/Delete: admin/owner do tenant. Edges via service_role bypassam.

**Confirmar.**

---

## Aguarda OK + escolhas em B1-B10 antes de prosseguir.

---

## Etapa 2 — Migrations

**1) Tabela appointments:**

Arquivo `<timestamp>_pr4_appointments.sql` com schema completo + RLS + 4 policies.

**2) Tabela appointment_google_sync:**

Arquivo separado, schema + RLS minimal (só super_admin lê — sync state é interno).

**Pedro roda manual no SQL Editor** (ou aplica migration via CLI se preferir).

---

## Etapa 3 — Edge `google-calendar-push`

`supabase/functions/google-calendar-push/index.ts`

Reusa helper `google-auth.ts` (PR1).

Lógica conforme spec acima (create/update/delete).

---

## Etapa 4 — Hooks + mutations

`src/features/appointments/hooks/`:
- `useAppointments(filters)` — lista appointments do tenant
- `useCreateAppointment()` — insert + invoca edge push
- `useUpdateAppointment()` — update + invoca edge push (action=update)
- `useCancelAppointment()` — update status=cancelled + invoca edge push (action=delete)

Sequência de criação:
```ts
async function createAppointment(input) {
  // 1. Insert no DB
  const { data: appt } = await supabase.from('appointments').insert(input).select().single();
  
  // 2. Chama edge pra sincar Google
  const { data: pushResult } = await supabase.functions.invoke('google-calendar-push', {
    body: { appointment_id: appt.id, action: 'create' }
  });
  
  // 3. Se push falhou, marca status=error no sync (já tratado pela edge)
  return { appointment: appt, push: pushResult };
}
```

---

## Etapa 5 — Cleanup + deploy

### Antes do deploy

**1) Migration tabela appointments:**
```sql
-- ... schema completo
```

**2) Migration tabela appointment_google_sync:**
```sql
-- ... schema completo
```

**3) Confirma:**
```sql
SELECT COUNT(*) FROM public.appointments;
```
Esperado: 0.

```sql
SELECT COUNT(*) FROM public.appointment_google_sync;
```
Esperado: 0.

### Deploy

```bash
gh pr merge <PR> --squash --delete-branch
git checkout main && git pull origin main
supabase functions deploy google-calendar-push
git push origin main
```

### Validação pós-deploy

Smoke teste manual via curl ou painel admin:

1. Pega `professional_calendar_id` de teste (PR1)
2. Cria appointment via SQL ou mutation:
   ```sql
   INSERT INTO appointments (tenant_id, professional_id, customer_name, customer_phone, start_at, end_at)
   VALUES (...);
   ```
3. Chama edge push manualmente:
   ```bash
   curl -X POST .../google-calendar-push \
     -H "Authorization: Bearer <jwt>" \
     -d '{"appointment_id": "<id>", "action": "create"}'
   ```
4. Verifica:
   - Response com `google_event_id`
   - Evento aparece no Google Calendar do profissional
   - Row em `appointment_google_sync` com `sync_status='synced'`

---

## Critérios de aceite

- [ ] Etapa 1 confirmação aprovada
- [ ] Migration `appointments` rodada
- [ ] Migration `appointment_google_sync` rodada
- [ ] Edge `google-calendar-push` deployada
- [ ] Hooks `useCreateAppointment`, `useUpdateAppointment`, `useCancelAppointment` criados
- [ ] `extendedProperties.private.risen_source = "crm_whats"` em todos eventos
- [ ] Build/tsc/vitest verde
- [ ] PR description anota: "Backend de appointments. UI fica pra futura sprint. PR5 (webhook) + PR6 (tools IA) completam Sprint Schedule."

---

## Restrições

- ❌ Sem trigger DB (decisão B1 — aplicação chama explícito)
- ❌ Sem UI ainda
- ❌ Sem lógica de resource_id auto-pick (PR6)
- ❌ Sem webhook receiver Google → CRM (PR5)
- ❌ Sem cron pull (PR5)
- ❌ Sem tools IA (PR6)
- ✅ Branch: `schedule-pr4-appointments`
- ✅ PR título: `feat(schedule): tabelas appointments + edge push CRM→Google (PR4)`

---

## Pós-merge — Próximo: PR5

PR5 entrega:
- Edge webhook receiver Google → CRM (recebe push do Google quando alguém edita no Calendar app)
- Cron pull conciliatório (proteção contra webhook perdido)
- Conflict resolution: last-write-wins via etag/updated_at
- Identifica eventos próprios via `risen_source = "crm_whats"` (ignora eventos do Risen OS)

Estimativa: ~1 dia.

---

## O que NÃO fazer neste PR

- ❌ UI visual de appointments
- ❌ Webhook Google → CRM (PR5)
- ❌ Tools IA (PR6)
- ❌ Auto-pick resource (PR6)
- ❌ Compiler emite caixa de calendário no contexto (PR6)
- ❌ Notification por email/SMS (Google Calendar cuida automaticamente)
