# PR6 Sprint Schedule — Tools IA + compiler (ÚLTIMO)

> **ÚLTIMO PR DA SPRINT SCHEDULE.** Tools IA que orquestram agendamento via WhatsApp + compiler que emite caixas Calendar Config/Links no contexto.
>
> Estimativa: ~1 dia.
> Branch: `schedule-pr6-tools-ia`

---

## Contexto

PR1-PR5 entregaram toda infra:
- Tabelas (`professional_calendars`, `appointments`, `appointment_google_sync`, `webhook_channels`)
- Edges (provision, push, webhook, setup, pull-conciliation)
- Caixas Calendar Config + Calendar Links com UI
- Sync bidirecional CRM ↔ Google funcionando

**PR6 entrega o cérebro de agendamento da IA:**
- 4 tools (search_slots, create, reschedule, cancel)
- Compiler emite Calendar Config + Calendar Links no contexto
- Lógica de slots: horário estab + service_hours + buffers + freebusy Google
- Auto-pick `resource_id` quando `max_parallel_resources > 1`
- Helper `duration` puxa de Services/Events (não da Calendar Config)
- Smoke real com tenant cobaia

**Após este PR → Sprint Schedule COMPLETA.**

---

## Tools propostas (4)

### 1. `search_team_slots`

```ts
search_team_slots({
  professional_id?: string,
  service_id?: string,
  date_range: { from: string, to: string },
  duration_minutes?: number  // opcional, se omitir IA usa duration do service
})

Returns: {
  slots: [
    { professional_id, professional_name, start: ISO, end: ISO },
    // ...até 10
  ]
}
```

**Lógica:**

1. Determina lista de profissionais:
   - Se `professional_id` informado → 1 profissional
   - Se `service_id` informado → profissionais cuja `specialty` ou `trigger_keywords` casa
   - Senão → todos com `status='Ativo'` E `has_own_calendar=true`

2. Pra cada profissional:
   - Lê `service_hours` da caixa Team (textarea livre, parseia natural language)
   - Intersect com Establishment.hours
   - Apply buffers da Calendar Config (`buffer_before_minutes` + `buffer_after_minutes`)
   - Consulta Google Calendar freebusy API pro range
   - Retorna slots livres dentro do horário

3. Ordena por proximidade ao "agora" + `priority` do profissional (Alta antes de Baixa)

4. Limita a 10 slots no retorno

### 2. `create_appointment`

```ts
create_appointment({
  professional_id?: string,
  service_id?: string,
  resource_id?: string,    // opcional, se max_parallel_resources>1 sistema auto-picks
  customer_name: string,
  customer_phone: string,
  customer_email?: string,
  start_at: string,
  end_at: string,
  notes?: string
})

Returns: {
  appointment_id: string,
  google_event_id: string,
  professional_name?: string,
  resource_id?: string  // se auto-picked, retorna
}
```

**Lógica:**

1. Valida: ao menos `professional_id` OU `establishment` calendar configurado
2. Valida: `end_at > start_at`
3. Valida slot ainda livre (re-checa freebusy ou busy_status local)
4. **Auto-pick resource:** se `max_parallel_resources > 1` na Calendar Config e `resource_id` vazio:
   - Lista resources já ocupados nessa janela (query appointments)
   - Atribui próximo livre (ex: `machine_01`, `machine_02`, ...)
   - Numera 1 a `max_parallel_resources`
5. Insert appointment
6. Invoca edge `google-calendar-push` (action=create)
7. Retorna ID + nome do profissional (pra IA responder ao cliente)

### 3. `reschedule_appointment`

```ts
reschedule_appointment({
  appointment_id: string,
  new_start_at: string,
  new_end_at: string,
  reason?: string
})

Returns: {
  appointment_id: string,
  new_start_at: string
}
```

**Lógica:**

1. Lê appointment atual
2. Valida que tenant é dono
3. Valida `reschedule_until_hours` da Calendar Config (se `new_start_at < now() + reschedule_until_hours` → erro)
4. Valida slot novo está livre
5. Update appointment (start/end/notes)
6. Invoca edge `google-calendar-push` (action=update)

### 4. `cancel_appointment`

```ts
cancel_appointment({
  appointment_id: string,
  cancellation_reason?: string
})

Returns: {
  appointment_id: string,
  cancelled_at: string
}
```

**Lógica:**

1. Lê appointment
2. Update status='cancelled' + cancelled_at + cancellation_reason
3. Invoca edge `google-calendar-push` (action=delete)
4. Evento removido do Google Calendar mas appointment fica em histórico

---

## Compiler — caixas Calendar emitem no contexto

Hoje (PR2 mergeado), `calendar_config` está no ORDER mas sem case. PR6 adiciona.

### `formatCalendarConfig`

```ts
function formatCalendarConfig(box: PersonaBox | null): string {
  if (!box?.data) return "";
  const d = box.data;
  
  const lines = [];
  if (d.timezone) lines.push(`Fuso horário: ${d.timezone}`);
  if (d.min_advance_time) lines.push(`Antecedência mínima: ${d.min_advance_time}`);
  if (d.max_advance_time) lines.push(`Antecedência máxima: ${d.max_advance_time}`);
  if (d.buffer_before_minutes) lines.push(`Buffer antes do agendamento: ${d.buffer_before_minutes} min`);
  if (d.buffer_after_minutes) lines.push(`Buffer depois do agendamento: ${d.buffer_after_minutes} min`);
  if (d.reschedule_until_hours) lines.push(`Reagendamento permitido até ${d.reschedule_until_hours}h antes`);
  if (d.max_parallel_resources) lines.push(`Capacidade paralela: ${d.max_parallel_resources} recursos`);
  if (d.ai_can_confirm) lines.push(`Autonomia IA pra confirmar: ${d.ai_can_confirm}`);
  if (d.no_slot_fallback) lines.push(`Quando não há horário: ${d.no_slot_fallback}`);
  if (d.ai_notes) lines.push(`Observações: ${d.ai_notes}`);
  
  if (!lines.length) return "";
  return `## Configurações da agenda\n\n${lines.map(l => `- ${l}`).join("\n")}`;
}
```

### `formatCalendarLinks`

```ts
function formatCalendarLinks(box: PersonaBox | null): string {
  if (!box?.data?.items?.length) return "";
  
  const provisioned = box.data.items.filter((i: any) => 
    i.provisioning_status === "provisioned" || i.provisioning_status === "shared"
  );
  
  if (!provisioned.length) return "";
  
  const lines = provisioned.map((item: any) => {
    const type = item.link_type;
    return `- ${item.label} (${type})`;
  });
  
  return `## Calendários disponíveis\n\nAgendamentos podem ser criados nos calendários:\n${lines.join("\n")}\n\nUse a tool \`search_team_slots\` pra ver disponibilidade.`;
}
```

Casos:
- Sem calendars provisionados → retorna "" (IA não tenta agendar)
- Calendars erro/pending → ignora

---

## Etapa 1 — Confirmações antes de codar

### A. Decisões pendentes

#### A1. Tool auth edge→edge

PR4 (push edge) tem `verify_jwt=true`. PR6 vai chamar push edge a partir de outra edge (ai-reply via tool).

**Opções:**

**A — Service role na invocação:**
- Tool faz `supabase.functions.invoke('google-calendar-push', { headers: { Authorization: `Bearer ${SERVICE_ROLE_KEY}` } })`
- Push edge identifica service role e bypassa verify_jwt
- Simples, sem mexer no push edge

**B — Edge interna sem auth:**
- Cria edge `google-calendar-push-internal` (mesma lógica, sem verify_jwt)
- Tools chamam essa
- Duplicação

**C — Push edge ganha bypass por header próprio:**
- Header `X-Internal-Call` valida via secret
- Push edge mantém verify_jwt=true mas pula se header bate

**Recomendação: A.** Service role pattern padrão. Outras edges no projeto provavelmente já fazem isso.

#### A2. Parser de `service_hours` (textarea livre)

`service_hours` em Team é texto livre tipo "Seg, Qua, Sex 9h-19h. Ter e Qui folga".

**Opções:**

**A — Parser regex/heuristica simples:**
- Extrai dias da semana + ranges horários
- Funciona em ~80% dos casos
- Falha em casos atípicos (parser retorna disponível 24/7, IA usa Establishment.hours como fallback)

**B — IA parseia natural language:**
- Tool retorna `service_hours` raw pra IA
- IA decide se profissional atende em X horário
- Mais robusto mas tool fica menos útil

**C — Parser híbrido:**
- Tenta regex primeiro
- Se falhar, retorna raw + flag `parse_uncertain`
- IA decide

**Recomendação: A (simples).** Razões:
- Falsos positivos cobertos por Google freebusy (evento conflitando bloqueia mesmo se parser errou)
- Service_hours raramente é exotic
- C adiciona complexidade sem ganho proporcional

Se virar gargalo, ajusta depois.

#### A3. Duration fallback

Decisão anterior: prioriza Services.duration → Events.duration → IA pergunta.

`Calendar Config.default_duration_minutes` **foi removido** (hotfix).

Sem fallback global. Tool valida:
- Se `service_id` informado → busca duration no Services item
- Se `service_id` null → IA precisa passar `duration_minutes` explicitamente
- Se ambos vazios → tool retorna erro pedindo duration

#### A4. Auto-pick resource_id

`max_parallel_resources` na Calendar Config define quantos recursos paralelos.

**Lógica:**
1. Lista appointments existentes nesse horário + status != cancelled
2. Pra cada appointment, extrai `resource_id` ocupado
3. Calcula próximo `resource_id` livre: numeração sequencial de 1 a `max_parallel_resources`
4. Atribui

Esquema simples: `resource_id` = string `"01"`, `"02"`, ... `"10"`.

Mostra na UI como "Máquina 01", "Máquina 02" (mas sistema não persiste nomes — só números).

**Confirmar.**

#### A5. Tool retorna nome do profissional

Pra IA responder cliente naturalmente:
- "Marquei com Dr. João às 14h"
- vs "Marquei (professional_id=abc123) às 14h"

Tools que retornam appointment incluem `professional_name`. IA usa pra resposta.

#### A6. Smoke real

Após PR mergear, validação com tenant cobaia:
1. Tenant tem calendar provisionado (PR3)
2. Tenant tem Team com Maria (`has_own_calendar=true`)
3. Cliente manda WhatsApp: "Quero marcar com Maria amanhã 14h"
4. IA chama `search_team_slots` → retorna slots de Maria
5. IA confirma com cliente
6. IA chama `create_appointment` → cria + push pro Google
7. Evento aparece no Google Calendar da Maria

#### A7. Tools no master prompt

Tools são declaradas dinamicamente (SUF15 pattern). Quando caixa Calendar Links tem provisioned calendars, tools de agenda são incluídas.

Se zero calendars provisionados → tools não declaradas (IA não tenta agendar).

#### A8. Helper de Services.duration_minutes (já mergeado)

Decisão anterior: helper diz "Tempo do serviço usado pra calcular slots no agendamento". Já mergeado (hotfix 2).

Tool `search_team_slots` usa esse campo se `service_id` informado.

---

## Aguarda OK + escolhas em A1-A8 antes de prosseguir.

---

## Etapa 2 — Tools implementation

`supabase/functions/_shared/tools/` (ou onde tools vivem hoje):

- `searchTeamSlots.ts` — lógica de slots
- `createAppointment.ts` — cria + push
- `rescheduleAppointment.ts` — update + push update
- `cancelAppointment.ts` — cancel + push delete

Helper:
- `parseServiceHours.ts` — parser regex de horários textarea livre
- `intersectHours.ts` — intersect horário estab + service_hours
- `pickResourceId.ts` — auto-pick lógica
- `getGoogleFreeBusy.ts` — consulta Google freebusy API

---

## Etapa 3 — Compiler emite Calendar Config + Calendar Links

Adicionar casos no compiler:
- `formatCalendarConfig` (case calendar_config)
- `formatCalendarLinks` (case calendar_links)

ORDER já tem ambos (PR2 + PR3). Só adicionar os cases.

---

## Etapa 4 — Master prompt declara tools dinamicamente

Pattern SUF15: tools são declaradas baseado em caixas preenchidas.

Adicionar:
```ts
if (hasProvisionedCalendars(boxes)) {
  tools.push(
    SEARCH_TEAM_SLOTS_TOOL,
    CREATE_APPOINTMENT_TOOL,
    RESCHEDULE_APPOINTMENT_TOOL,
    CANCEL_APPOINTMENT_TOOL
  );
}
```

---

## Etapa 5 — Smoke teste

Documentação no PR description:

```
## Smoke real após deploy

Pré-requisito: tenant cobaia com:
- Calendar Config preenchida (timezone)
- 1 calendar provisionado em Calendar Links (link_type=professional)
- Team com 1 profissional Maria (has_own_calendar=true, email=maria@gmail.com)

Steps:
1. Cliente envia mensagem ao tenant via WhatsApp: "Quero marcar com Maria amanhã às 14h"
2. IA chama search_team_slots
3. IA confirma horário com cliente
4. IA chama create_appointment
5. Verificar:
   - Row em appointments
   - Row em appointment_google_sync
   - Evento aparece no Google Calendar da Maria
```

---

## Etapa 6 — Deploy

```bash
gh pr merge <PR> --squash --delete-branch
git checkout main && git pull origin main
supabase functions deploy ai-reply
git push origin main
```

Sem migration nova. Sem ALTER TYPE.

---

## Critérios de aceite

- [ ] Etapa 1 confirmação aprovada
- [ ] 4 tools implementadas
- [ ] Compiler emite calendar_config + calendar_links
- [ ] Master prompt declara tools quando calendar provisioned
- [ ] Service role auth pra edge→edge
- [ ] Auto-pick resource_id quando max_parallel_resources>1
- [ ] Build/tsc/vitest verde
- [ ] PR description tem roteiro de smoke real
- [ ] Smoke real validado com tenant cobaia

---

## Restrições

- ❌ Sem UI nova (tools são consumidas pela IA)
- ❌ Sem migration de dados
- ❌ Sem parser AI de service_hours (regex simples basta)
- ❌ Sem espelhar eventos pessoais do Google (decisão A5 da PR5)
- ✅ Branch: `schedule-pr6-tools-ia`
- ✅ PR título: `feat(schedule): tools IA + compiler (PR6) — Fecha Sprint Schedule`

---

## Pós-merge — Sprint Schedule COMPLETA 🎉

Total: 6 PRs + 2 hotfixes em ~6 dias estimado.

**Próximas sprints:**
- Sprint Forms (~1.5 dia)
- Sprint Arquétipos MVP manual (~1 dia) — Pedro mencionou
- Sprint Arquétipos completa (~1-2 semanas) — destrava Vanderlei migrar pra blocks

---

## O que NÃO fazer neste PR

- ❌ UI visual de appointments (futura sprint)
- ❌ Painel admin de calendários
- ❌ Espelhar eventos pessoais do Google
- ❌ Sprint Forms / Sprint Arquétipos
