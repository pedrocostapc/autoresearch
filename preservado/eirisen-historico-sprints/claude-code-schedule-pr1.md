# PR1 Sprint Schedule — Fundação Google + tabela `professional_calendars`

> **Primeiro PR da Sprint Schedule.** Fundação técnica pra integração Google Calendar. Sem UI ainda — só infra.
>
> Estimativa: ~1 dia.
> Branch: `schedule-pr1-google-foundation`

---

## Contexto

Sprint Schedule integra CRM Whats ao Google Calendar via Service Account. Arquitetura:

```
CRM Whats ←→ Google Calendar ←→ Risen OS
```

Google é o hub. CRM faz seu sync independente (sem comunicação direta com Risen OS).

**Infra já pronta** (confirmado em diagnóstico anterior):
- Service Account: `risen-calendar-bot@risen-services.iam.gserviceaccount.com`
- Secret `CRMWHATS_GOOGLE_SA_JSON` no Supabase
- GCP Project `risen-services` com Calendar API ativa

**Este PR entrega:**
- Tabela `professional_calendars` no Supabase
- Helper JWT → access token Google (reusável)
- Edge `google-calendar-provision` (cria calendar + compartilha)
- 2 ALTER TYPE no enum `persona_box_type` (`calendar_config` + `calendar_links`)

**Não entrega:**
- UI (PR2 e PR3)
- Sync de appointments (PR4 e PR5)
- Tools IA (PR6)

---

## Schema da tabela `professional_calendars`

```sql
CREATE TABLE professional_calendars (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  
  -- Identificação do "dono" do calendar
  link_type text NOT NULL CHECK (link_type IN ('establishment', 'professional', 'external')),
  label text NOT NULL,                         -- display name (ex: "Calendário Maria", "Atendimentos")
  linked_professional_id text,                 -- referência ao item.id dentro de persona_boxes.data.items (Team), nullable
  
  -- Google Calendar
  google_calendar_id text,                     -- ID do calendar no Google (preenchido após provisionamento)
  google_email text NOT NULL,                  -- email pra compartilhamento (pode = email do profissional)
  calendar_type text NOT NULL CHECK (calendar_type IN ('system_created', 'tenant_owned')),
  
  -- Estado de provisionamento
  provisioning_status text NOT NULL DEFAULT 'pending' 
    CHECK (provisioning_status IN ('pending', 'provisioned', 'shared', 'error')),
  error_message text,
  
  -- Audit
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  provisioned_at timestamptz,
  
  -- Constraints
  UNIQUE(tenant_id, google_calendar_id),
  UNIQUE(tenant_id, linked_professional_id)
);

CREATE INDEX idx_prof_cal_tenant ON professional_calendars(tenant_id);
CREATE INDEX idx_prof_cal_google ON professional_calendars(google_calendar_id);
CREATE INDEX idx_prof_cal_status ON professional_calendars(tenant_id, provisioning_status);

-- Trigger updated_at
CREATE TRIGGER update_professional_calendars_updated_at
BEFORE UPDATE ON professional_calendars
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

**Notas:**
- `linked_professional_id` é nullable porque links externos não têm profissional cadastrado
- `google_calendar_id` é nullable até o provisionamento dar certo
- `calendar_type='system_created'`: sistema criou via SA. `tenant_owned`: tenant compartilhou calendar existente com a SA.
- `provisioning_status='shared'`: específico pra `tenant_owned` quando confirmamos que SA tem acesso

---

## Etapa 1 — Confirmações antes de codar

### A. Tabela `tenants` existe?

```bash
grep -rn "CREATE TABLE tenants\|REFERENCES tenants" supabase/migrations/ | head -5
```

Reportar:
- Nome exato da tabela (tenants? accounts? organizations?)
- Schema relevante (id type)

### B. Função `update_updated_at_column()` existe?

```bash
grep -rn "update_updated_at_column\|updated_at_column" supabase/migrations/
```

Reportar:
- Existe? Em qual migration?
- Se não, criar nesta PR

### C. Helpers existentes pra Google APIs

```bash
grep -rn "google\|gapi\|googleapis" supabase/functions/_shared/ --include="*.ts" | head -10
```

Reportar:
- Algum helper Google já existe?
- Pattern de auth usado em outras edges (JWT? OAuth? SA?)

### D. Secrets confirmados

```bash
supabase secrets list 2>&1 | grep -i "google\|gcal\|crmwhats"
```

Reportar:
- `CRMWHATS_GOOGLE_SA_JSON` presente?
- Outros secrets relacionados

### E. Enum `persona_box_type` atual

```sql
SELECT unnest(enum_range(NULL::persona_box_type)) AS box_type;
```

Esperado: 16 valores. PR1 adiciona 2 (`calendar_config`, `calendar_links`) → 18.

### F. Decisões pendentes

#### F1. Schema `appointments` adiantar nesta PR ou esperar PR4?

PR4 da sequência cuida de appointments. Mas pode fazer sentido criar a tabela já agora pra evitar 2 migrations.

**Recomendação:** **Não adiantar.** PR1 fica focado em professional_calendars. Appointments tem complexidade própria (FKs, índices de busca por data, RLS) — merece PR dedicado.

#### F2. RLS na tabela?

Multi-tenant. Tenant só vê seus próprios calendários.

**Recomendação:** Adicionar RLS desde já:

```sql
ALTER TABLE professional_calendars ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Tenants can manage own calendars"
ON professional_calendars
FOR ALL
USING (tenant_id IN (
  SELECT tenant_id FROM tenant_users WHERE user_id = auth.uid()
));
```

Confirmar: a tabela `tenant_users` ou equivalente existe? Como é o pattern de RLS no projeto?

#### F3. Estrutura do helper JWT → access token

Pattern Google SA padrão:
1. Lê secret JSON da SA
2. Constroi JWT assinado com private_key (RS256)
3. Troca JWT por access token via OAuth token endpoint
4. Cache token em memória (válido 1h)

**Arquivo:** `supabase/functions/_shared/google-auth.ts`

```ts
export async function getGoogleAccessToken(): Promise<string> {
  // Implementação JWT signing + token exchange
}
```

Reusável por todas as edges Google (provision, push, webhook).

Confirmar approach.

#### F4. Edge `google-calendar-provision` — assinatura

```ts
POST /functions/v1/google-calendar-provision

Body:
{
  tenant_id: string,
  link_type: 'establishment' | 'professional' | 'external',
  label: string,
  google_email: string,                    // email pra compartilhar
  linked_professional_id?: string,          // se link_type=professional
  mode: 'create' | 'use_existing',         // Opção C
  existing_calendar_id?: string             // se mode=use_existing
}

Response:
{
  professional_calendar_id: string,
  google_calendar_id: string,
  provisioning_status: 'provisioned' | 'shared' | 'error',
  error_message?: string
}
```

**Mode `create`:**
1. Cria calendar via API: `POST /calendar/v3/calendars` com summary="Risen — {label}"
2. Compartilha com google_email: `POST /calendar/v3/calendars/{id}/acl` role=writer
3. Insere row em professional_calendars com status=provisioned

**Mode `use_existing`:**
1. Valida que SA tem acesso: `GET /calendar/v3/calendars/{existing_calendar_id}`
2. Se sim, insere row com calendar_type=tenant_owned, status=shared
3. Se não, retorna error com instruções: "Compartilhe o calendar com risen-calendar-bot@risen-services.iam.gserviceaccount.com (permissão Editor)"

#### F5. Timezone padrão

Calendars criados pela SA precisam de timezone explícito. Default `America/Sao_Paulo`.

Cliente em outro fuso ajusta na caixa Calendar Config (PR2).

#### F6. Tratamento de erro do Google API

- Rate limit (429): retry com backoff
- Quota exceeded: salva status=error + mensagem
- Email inválido: pre-validate no edge antes de chamar API
- Network: fail-fast, retry no client

---

## Aguarda OK + escolhas em F1-F6 antes de prosseguir.

---

## Etapa 2 — Migrations

**1) Tabela:**
```sql
-- supabase/migrations/<timestamp>_pr1_professional_calendars.sql
-- schema completo conforme acima + RLS
```

**2) ALTER TYPE (Pedro roda manual no SQL Editor — 2 queries separadas):**

Query 1:
```sql
ALTER TYPE persona_box_type ADD VALUE IF NOT EXISTS 'calendar_config';
```

Query 2:
```sql
ALTER TYPE persona_box_type ADD VALUE IF NOT EXISTS 'calendar_links';
```

Confirmar:
```sql
SELECT unnest(enum_range(NULL::persona_box_type)) AS box_type;
```

---

## Etapa 3 — Helper `google-auth.ts`

`supabase/functions/_shared/google-auth.ts`:

```ts
interface GoogleSAJson {
  client_email: string;
  private_key: string;
  token_uri: string;
}

let cachedToken: { token: string; expiresAt: number } | null = null;

export async function getGoogleAccessToken(): Promise<string> {
  if (cachedToken && cachedToken.expiresAt > Date.now() + 60000) {
    return cachedToken.token;
  }
  
  const saJsonRaw = Deno.env.get("CRMWHATS_GOOGLE_SA_JSON");
  if (!saJsonRaw) throw new Error("CRMWHATS_GOOGLE_SA_JSON not configured");
  
  const sa: GoogleSAJson = JSON.parse(saJsonRaw);
  
  // Build JWT
  const header = { alg: "RS256", typ: "JWT" };
  const now = Math.floor(Date.now() / 1000);
  const payload = {
    iss: sa.client_email,
    scope: "https://www.googleapis.com/auth/calendar",
    aud: sa.token_uri,
    exp: now + 3600,
    iat: now,
  };
  
  const jwt = await signJWT(header, payload, sa.private_key);
  
  // Exchange JWT for access token
  const res = await fetch(sa.token_uri, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer",
      assertion: jwt,
    }),
  });
  
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Google token exchange failed: ${err}`);
  }
  
  const { access_token, expires_in } = await res.json();
  
  cachedToken = {
    token: access_token,
    expiresAt: Date.now() + expires_in * 1000,
  };
  
  return access_token;
}

async function signJWT(header: object, payload: object, privateKey: string): Promise<string> {
  // Implementação RS256 com WebCrypto API
  // ...
}
```

---

## Etapa 4 — Edge `google-calendar-provision`

`supabase/functions/google-calendar-provision/index.ts`:

```ts
import { getGoogleAccessToken } from "../_shared/google-auth.ts";

serve(async (req) => {
  const { tenant_id, link_type, label, google_email, linked_professional_id, mode, existing_calendar_id } = await req.json();
  
  try {
    let googleCalendarId: string;
    let provisioningStatus: 'provisioned' | 'shared';
    let calendarType: 'system_created' | 'tenant_owned';
    
    if (mode === 'create') {
      const created = await createCalendar(label);
      await shareCalendar(created.id, google_email);
      googleCalendarId = created.id;
      provisioningStatus = 'provisioned';
      calendarType = 'system_created';
    } else {
      // mode === 'use_existing'
      const hasAccess = await validateCalendarAccess(existing_calendar_id);
      if (!hasAccess) {
        return new Response(JSON.stringify({
          provisioning_status: 'error',
          error_message: 'SA não tem acesso. Compartilhe o calendar com risen-calendar-bot@risen-services.iam.gserviceaccount.com (Editor)'
        }), { status: 400 });
      }
      googleCalendarId = existing_calendar_id;
      provisioningStatus = 'shared';
      calendarType = 'tenant_owned';
    }
    
    // Insere no DB
    const { data, error } = await supabase
      .from('professional_calendars')
      .insert({
        tenant_id,
        link_type,
        label,
        linked_professional_id,
        google_email,
        google_calendar_id: googleCalendarId,
        calendar_type: calendarType,
        provisioning_status: provisioningStatus,
        provisioned_at: new Date().toISOString(),
      })
      .select()
      .single();
    
    if (error) throw error;
    
    return new Response(JSON.stringify({
      professional_calendar_id: data.id,
      google_calendar_id: googleCalendarId,
      provisioning_status: provisioningStatus,
    }));
  } catch (e) {
    return new Response(JSON.stringify({
      provisioning_status: 'error',
      error_message: e.message,
    }), { status: 500 });
  }
});

async function createCalendar(label: string) {
  const token = await getGoogleAccessToken();
  const res = await fetch('https://www.googleapis.com/calendar/v3/calendars', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      summary: `Risen — ${label}`,
      timeZone: 'America/Sao_Paulo',
    }),
  });
  if (!res.ok) throw new Error(`Create calendar failed: ${await res.text()}`);
  return res.json();
}

async function shareCalendar(calendarId: string, email: string) {
  const token = await getGoogleAccessToken();
  const res = await fetch(`https://www.googleapis.com/calendar/v3/calendars/${calendarId}/acl`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      role: 'writer',
      scope: { type: 'user', value: email },
    }),
  });
  if (!res.ok) throw new Error(`Share calendar failed: ${await res.text()}`);
}

async function validateCalendarAccess(calendarId: string): Promise<boolean> {
  try {
    const token = await getGoogleAccessToken();
    const res = await fetch(`https://www.googleapis.com/calendar/v3/calendars/${calendarId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return res.ok;
  } catch {
    return false;
  }
}
```

---

## Etapa 5 — Testes

- Unit test pra `getGoogleAccessToken` com mock do fetch
- Unit test pra `createCalendar`, `shareCalendar`, `validateCalendarAccess`
- Integration test do endpoint completo (mode=create e mode=use_existing)

---

## Etapa 6 — Deploy

```bash
gh pr merge <PR> --squash --delete-branch
git checkout main && git pull origin main
supabase functions deploy google-calendar-provision
git push origin main
```

**Pedro roda manualmente antes do deploy:**
1. Migration `professional_calendars` (rodada pelo sistema de migrations ou manual)
2. 2 ALTER TYPE no SQL Editor (queries separadas)
3. Confirma com SELECT enum_range

### Validação pós-deploy

Teste manual via curl ou Postman:

```bash
curl -X POST https://<project>.supabase.co/functions/v1/google-calendar-provision \
  -H "Authorization: Bearer <SUPABASE_ANON_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "<tenant uuid>",
    "link_type": "professional",
    "label": "Maria Silva",
    "google_email": "maria@gmail.com",
    "mode": "create"
  }'
```

Verifica:
- Response retorna `google_calendar_id`
- Row criada em `professional_calendars`
- Convite chega no Gmail de maria@gmail.com
- Calendar aparece no Google Calendar app

---

## Critérios de aceite

- [ ] Etapa 1 confirmação aprovada
- [ ] Migration `professional_calendars` rodada
- [ ] 2 ALTER TYPE rodados (enum agora com 18 valores)
- [ ] Helper `google-auth.ts` em `_shared/`
- [ ] Edge `google-calendar-provision` deployada
- [ ] Testes verde
- [ ] Provisionamento manual testado (Pedro confirma com gmail real)

---

## Restrições

- ❌ Sem UI nesta PR
- ❌ Sem caixas Calendar Config / Calendar Links (PR2 e PR3)
- ❌ Sem sync de appointments (PR4 e PR5)
- ❌ Sem tools IA (PR6)
- ✅ Branch: `schedule-pr1-google-foundation`
- ✅ PR título: `feat(schedule): fundação Google Calendar + tabela professional_calendars (PR1)`

---

## O que NÃO fazer neste PR

- ❌ Schema appointments (PR4)
- ❌ Webhook receiver (PR5)
- ❌ Cron jobs (PR5)
- ❌ Tools IA (PR6)
- ❌ Caixas (PR2 e PR3)
