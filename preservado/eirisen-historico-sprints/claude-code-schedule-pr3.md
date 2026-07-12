# PR3 Sprint Schedule — Calendar Links + UI provisionamento

> **Maior PR da Sprint Schedule.** Caixa `calendar_links` (multi-item) + UI de provisionamento que chama edge PR1.
>
> Estimativa: ~1.5 dia.
> Branch: `schedule-pr3-calendar-links`

---

## Contexto

**PR1 entregou:** edge `google-calendar-provision`, tabela `professional_calendars`, helper `google-auth.ts`.
**PR2 entregou:** caixa singleton `calendar_config` com 10 campos.

**PR3 entrega a interface visual** que liga as 2 peças anteriores:
- Caixa `calendar_links` (multi-item) lista calendários linkados
- Dropdown puxa profissionais de Team (filtra quem tem email)
- Aviso visual: "profissional sem email não aparece"
- Botão "Provisionar" → chama edge `google-calendar-provision` (mode=create)
- Botão "Usar calendário existente" → chama edge (mode=use_existing)
- Status visível na UI (pending / provisioned / shared / error)
- Retry quando falha

**Não entrega:**
- Sync de appointments (PR4)
- Webhook receiver (PR5)
- Tools IA (PR6)
- Compiler ainda não emite essa caixa pro contexto da IA (PR6)

---

## Schema final calendar_links (8 campos / 2 blocos)

| Bloco | Campo | Tipo | Obrigatório |
|---|---|---|---|
| **1. Identificação do link** | link_type | single_choice (Estabelecimento/Profissional/Externo) | ✅ |
| | label | text | ✅ |
| | linked_professional_id | special (dropdown Team, só pra link_type=Profissional) | condicional |
| | google_email | email | ✅ |
| **2. Estado de provisionamento** | calendar_type | single_choice (system_created/tenant_owned) — readonly após provisionar | - |
| | google_calendar_id | text — readonly, preenchido pelo sistema | - |
| | provisioning_status | single_choice (pending/provisioned/shared/error) — readonly | - |
| | error_message | textarea — readonly | - |

**Total: 8 campos. 3 obrigatórios mínimos** (link_type, label, google_email). `linked_professional_id` obrigatório se link_type=Profissional.

---

## Modelo de dados

Cada linha da caixa `calendar_links` espelha uma row em `professional_calendars`:

```ts
data: {
  items: [
    {
      id: "uuid-do-item",                       // UUID estável no client
      link_type: "professional",
      label: "Calendário Maria",
      linked_professional_id: "team-item-id",   // ref a Team
      google_email: "maria@gmail.com",
      
      // Read-only — sistema preenche
      calendar_type: "system_created",
      google_calendar_id: "abc123@group.calendar.google.com",
      provisioning_status: "provisioned",
      error_message: null,
      professional_calendar_id: "uuid-da-tabela",  // FK pra professional_calendars
    },
    // ...
  ]
}
```

**Sync com `professional_calendars`:**
- Cliente preenche linha → edge chamada → row criada em `professional_calendars`
- `professional_calendar_id` armazenado no item pra rastreamento
- Status atualizado vem da tabela quando user recarrega

---

## Etapa 1 — Confirmações antes de codar

### A. Decisões pendentes

#### A1. Schema declarativo vs componente especializado

Caixa `calendar_links` tem peculiaridades:
- Campo `linked_professional_id` é **dropdown dinâmico** (lê Team em runtime)
- Vários campos são **readonly** após save (`google_calendar_id`, `provisioning_status`, etc)
- Tem **ações** (botões Provisionar / Retry / Usar existente)
- Cliente vê **status colorido** (badge "✅ Provisionado", "⏳ Pendente", "❌ Erro")

**Opções:**

**Opção A — Reusa `<MultiItemListEditor>` com campos especiais novos**
- Adicionar 2 tipos novos no QuestionBlock: `dynamic_dropdown` (lê de outra caixa) + `readonly_badge`
- Adicionar slot pra ações no card colapsado
- Vantagem: pattern consistente
- Desvantagem: estende infra Sprint Catalog (impacta outros componentes?)

**Opção B — Componente próprio `<CalendarLinksManager>`**
- Não usa `<MultiItemListEditor>`
- Lista flat de cards customizados
- Cada card mostra: badge status, campos editáveis, botões de ação
- Vantagem: zero impacto em infra existente, total controle UX
- Desvantagem: componente novo, código não compartilhado

**Recomendação: Opção B (componente próprio).** Razões:
- Caixa tem comportamentos únicos (ações, dropdown dinâmico, readonly após save)
- Forçar genericidade adicionaria complexidade
- Sprint Catalog tinha 1 caixa com componente próprio (Events `<MatrixEditor>`) — precedente válido
- Cliente vê UX diferenciada apropriada pra ação crítica (provisionamento)

Code confirma ou propõe alternativa.

#### A2. `linked_professional_id` — dropdown dinâmico

Componente lê caixa Team em runtime:

```tsx
const teamBox = useBox("team");
const professionals = teamBox?.data?.items ?? [];
const withEmail = professionals.filter(p => p.email);
const withoutEmail = professionals.filter(p => !p.email);
```

Dropdown mostra:
```
┌────────────────────────────────┐
│ ▼ Selecione um profissional    │
├────────────────────────────────┤
│ Maria Silva                    │  ← clicável
│ Dr. João Santos                │  ← clicável
│ Pedro Costa                    │  ← clicável
│ ─────────────────              │
│ ⚠️ Sem email (não disponíveis) │  ← header de seção
│   Ana Oliveira                 │  ← desabilitado
│   Carlos Souza                 │  ← desabilitado
└────────────────────────────────┘
```

Profissionais sem email aparecem disabled com tooltip "Preencher email em Equipe pra liberar".

#### A3. Estabelecimento — auto-preenche email

Quando `link_type=Estabelecimento`:
- `google_email` puxa automaticamente de `calendar_config.establishment_calendar_email` (PR2)
- Tenant pode override editando

#### A4. Externo — totalmente manual

Quando `link_type=Externo`:
- Sem dropdown
- Campos `label` e `google_email` livres
- Sem link com Team

#### A5. Botões de ação no card

Cada linha tem botões diferentes baseado em `provisioning_status`:

| Status | Botões visíveis |
|---|---|
| `pending` (nunca provisionou) | "Provisionar" (mode=create) / "Usar calendário existente" (mode=use_existing) / "Remover" |
| `provisioned` (system_created OK) | "Ver no Google Calendar" (link) / "Remover" |
| `shared` (tenant_owned OK) | "Ver no Google Calendar" (link) / "Remover" |
| `error` | "Tentar novamente" / "Remover" / "Ver detalhes do erro" |

#### A6. Modal "Usar calendário existente"

Quando cliente clica "Usar calendário existente":
- Abre modal com instruções
- Mostra email da SA pra copiar (button "Copiar email")
- Input pra colar `existing_calendar_id`
- Botão "Validar e linkar"

```
┌────────────────────────────────────────────────────────┐
│ Usar calendário existente                       [X]   │
├────────────────────────────────────────────────────────┤
│ 1. Vá no Google Calendar (calendar.google.com)        │
│ 2. Abra o calendário que quer usar                    │
│ 3. Settings → Share with specific people               │
│ 4. Adicione este email com permissão Editor:           │
│                                                         │
│    risen-calendar-bot@risen-services.iam.gserv...     │
│    [Copiar email]                                      │
│                                                         │
│ 5. Volte aqui e cole o ID do calendário:               │
│                                                         │
│    [_____________________________________________]    │
│    Ex: abc123@group.calendar.google.com                │
│                                                         │
│                                  [Cancelar] [Linkar]   │
└────────────────────────────────────────────────────────┘
```

#### A7. Como atualizar status após chamar edge

Após edge retornar:
1. Insert/update item na caixa (data.items)
2. Cliente vê atualização imediata
3. **Refetch da caixa não é necessário** — edge já retorna info completa

Para retry após erro:
1. Cliente clica "Tentar novamente"
2. Mesma edge é chamada
3. Status atualiza no item

#### A8. Validação pré-save

Quando salva caixa:
- `link_type` obrigatório
- `label` obrigatório
- `google_email` obrigatório (exceto se vai puxar de Establishment)
- Se `link_type=Profissional`, `linked_professional_id` obrigatório

#### A9. Sincronização inicial — caixa nova vs tabela com rows

Cenário: tenant rodou edge `google-calendar-provision` via curl antes de abrir a UI. Tem rows em `professional_calendars` mas caixa `calendar_links` está vazia.

**Solução:** quando user abre caixa pela primeira vez, hook fetcha `professional_calendars` do tenant e popula `data.items` automaticamente.

Confirmar approach.

#### A10. RLS pra puxar professional_calendars

PR1 setou RLS com `get_user_tenant_id()`. UI usa client autenticado → consegue ler suas próprias rows. ✓

#### A11. DELETE manual

Pedro roda quando terminar.

---

## Aguarda OK + escolhas em A1-A11 antes de prosseguir.

---

## Etapa 2 — Schema declarativo (mínimo)

Apesar de não usar `<MultiItemListEditor>`, schema declarativo serve pra:
- Documentar campos
- Edge import (caso queira Excel futuro — improvável)
- Validação Zod

```ts
// box-schemas.ts

export const CALENDAR_LINKS_SCHEMA: BoxSchemaDef = {
  boxType: "calendar_links",
  label: "Calendários linkados",
  cardinality: "multi_item",
  hasExcel: false,
  blocks: [
    {
      title: "Identificação do link",
      fields: [
        { 
          field: "link_type", 
          question: "Tipo de link", 
          type: "single_choice", 
          options: ["Estabelecimento", "Profissional", "Externo"],
          required: true 
        },
        { 
          field: "label", 
          question: "Nome do calendário", 
          type: "text",
          required: true,
          helper: "Como vai aparecer no Google Calendar (ex: 'Atendimentos Maria')" 
        },
        { 
          field: "linked_professional_id", 
          question: "Profissional vinculado", 
          type: "text",  // será renderizado como dropdown custom
          helper: "Selecione profissional da caixa Equipe (apenas quem tem email cadastrado)" 
        },
        { 
          field: "google_email", 
          question: "Email pra compartilhamento", 
          type: "email",
          required: true,
          helper: "Email do Google que vai receber o convite do calendário" 
        },
      ],
    },
    {
      title: "Estado de provisionamento (sistema)",
      fields: [
        { field: "calendar_type", question: "Tipo de calendário", type: "single_choice", options: ["system_created", "tenant_owned"], readonly: true },
        { field: "google_calendar_id", question: "ID do calendário no Google", type: "text", readonly: true },
        { field: "provisioning_status", question: "Status", type: "single_choice", options: ["pending", "provisioned", "shared", "error"], readonly: true },
        { field: "error_message", question: "Mensagem de erro", type: "textarea", readonly: true },
      ],
    },
  ],
};

// Adicionar ao registry
export const BOX_SCHEMAS: Record<string, BoxSchemaDef> = {
  // ... anteriores
  calendar_links: CALENDAR_LINKS_SCHEMA,
};
```

Nota: `readonly` é tipo novo? Provavelmente sim. Code confirma e adiciona ao FieldType union se necessário.

### Zod

```ts
export const CalendarLinkItemSchema = z.object({
  id: z.string(),
  link_type: z.enum(["Estabelecimento", "Profissional", "Externo"]),
  label: z.string().min(1),
  linked_professional_id: z.string().optional(),
  google_email: z.string().email(),
  
  // Read-only state
  calendar_type: z.enum(["system_created", "tenant_owned"]).optional(),
  google_calendar_id: z.string().optional(),
  provisioning_status: z.enum(["pending", "provisioned", "shared", "error"]).optional(),
  error_message: z.string().optional(),
  professional_calendar_id: z.string().optional(),
});

export const CalendarLinksSchema = z.object({
  items: z.array(CalendarLinkItemSchema).default([]),
});

export const BOX_DEFAULT_DATA: Record<PersonaBoxType, any> = {
  // ... anteriores
  calendar_links: { items: [] },
};
```

---

## Etapa 3 — `<CalendarLinksManager>` componente

Caminho: `src/features/ai-settings/components/blocos/CalendarLinksManager.tsx`

Estrutura:

```tsx
export function CalendarLinksManager() {
  const { data: linksBox } = useBox("calendar_links");
  const { data: teamBox } = useBox("team");
  const { data: configBox } = useBox("calendar_config");
  const { data: dbCalendars } = useProfessionalCalendars(); // fetch professional_calendars
  
  const items = linksBox?.data?.items ?? [];
  
  // Sincroniza estado do DB com items da caixa (Etapa A9)
  useEffect(() => {
    if (dbCalendars && items.length === 0 && dbCalendars.length > 0) {
      syncDbToBox(dbCalendars);
    }
  }, [dbCalendars]);
  
  return (
    <>
      <Button onClick={addLink}>+ Adicionar calendário</Button>
      
      {items.map((item) => (
        <CalendarLinkCard
          key={item.id}
          item={item}
          professionals={teamBox?.data?.items ?? []}
          establishmentEmail={configBox?.data?.establishment_calendar_email}
          onUpdate={(updated) => updateItem(item.id, updated)}
          onRemove={() => removeItem(item.id)}
          onProvision={(mode, existingId?) => provisionCalendar(item, mode, existingId)}
        />
      ))}
    </>
  );
}
```

Sub-componente `<CalendarLinkCard>`:

```tsx
function CalendarLinkCard({ item, professionals, ... }) {
  return (
    <Card>
      <CardHeader>
        <Badge variant={statusVariant(item.provisioning_status)}>
          {statusLabel(item.provisioning_status)}
        </Badge>
        <span>{item.label || "Sem nome"}</span>
        <Button onClick={onRemove}>X</Button>
      </CardHeader>
      
      <CardContent>
        {/* Editar dados */}
        <Select value={item.link_type} onValueChange={...}>
          <SelectItem value="Estabelecimento">Estabelecimento</SelectItem>
          <SelectItem value="Profissional">Profissional</SelectItem>
          <SelectItem value="Externo">Externo</SelectItem>
        </Select>
        
        <Input value={item.label} onChange={...} placeholder="Nome do calendário" />
        
        {/* Dropdown dinâmico só pra Profissional */}
        {item.link_type === "Profissional" && (
          <ProfessionalDropdown
            professionals={professionals}
            value={item.linked_professional_id}
            onChange={(profId, email) => { 
              onUpdate({ linked_professional_id: profId, google_email: email }); 
            }}
          />
        )}
        
        {/* Email - puxa de Establishment ou edita */}
        <Input 
          value={item.google_email} 
          onChange={...}
          disabled={item.link_type === "Estabelecimento" && !manuallyOverridden}
          placeholder="email@dominio.com"
        />
        
        {/* Mensagem de erro se houver */}
        {item.provisioning_status === "error" && item.error_message && (
          <Alert variant="destructive">{item.error_message}</Alert>
        )}
        
        {/* Botões de ação baseados em status */}
        <ActionButtons item={item} onProvision={onProvision} />
      </CardContent>
    </Card>
  );
}
```

Sub-componente `<ProfessionalDropdown>`:

```tsx
function ProfessionalDropdown({ professionals, value, onChange }) {
  const withEmail = professionals.filter(p => p.email);
  const withoutEmail = professionals.filter(p => !p.email);
  
  return (
    <Select value={value} onValueChange={(profId) => {
      const prof = professionals.find(p => p.id === profId);
      onChange(profId, prof?.email);
    }}>
      {withEmail.map(p => (
        <SelectItem value={p.id} key={p.id}>{p.full_name}</SelectItem>
      ))}
      
      {withoutEmail.length > 0 && (
        <SelectGroup>
          <SelectLabel className="text-yellow-600">⚠️ Sem email (preencher em Equipe)</SelectLabel>
          {withoutEmail.map(p => (
            <SelectItem value={p.id} key={p.id} disabled>{p.full_name}</SelectItem>
          ))}
        </SelectGroup>
      )}
    </Select>
  );
}
```

Sub-componente `<ActionButtons>`:

```tsx
function ActionButtons({ item, onProvision }) {
  if (item.provisioning_status === "pending" || !item.provisioning_status) {
    return (
      <>
        <Button onClick={() => onProvision("create")}>Provisionar</Button>
        <Button variant="outline" onClick={() => openUseExistingModal(item, onProvision)}>
          Usar calendário existente
        </Button>
      </>
    );
  }
  
  if (item.provisioning_status === "error") {
    return (
      <>
        <Button onClick={() => onProvision("create")}>Tentar novamente</Button>
        <Button variant="outline" onClick={() => openErrorDetails(item)}>Ver detalhes</Button>
      </>
    );
  }
  
  if (item.provisioning_status === "provisioned" || item.provisioning_status === "shared") {
    const calUrl = `https://calendar.google.com/calendar/u/0/r?cid=${item.google_calendar_id}`;
    return (
      <Button asChild>
        <a href={calUrl} target="_blank" rel="noopener">Ver no Google Calendar</a>
      </Button>
    );
  }
  
  return null;
}
```

Modal `<UseExistingCalendarModal>`:

```tsx
function UseExistingCalendarModal({ open, onClose, onSubmit }) {
  const [calendarId, setCalendarId] = useState("");
  const saEmail = "risen-calendar-bot@risen-services.iam.gserviceaccount.com";
  
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogTitle>Usar calendário existente</DialogTitle>
        
        <p>1. Vá no Google Calendar (calendar.google.com)</p>
        <p>2. Abra o calendário que quer usar</p>
        <p>3. Settings → Share with specific people</p>
        <p>4. Adicione este email com permissão Editor:</p>
        
        <div className="flex">
          <code>{saEmail}</code>
          <Button onClick={() => copyToClipboard(saEmail)}>Copiar</Button>
        </div>
        
        <p>5. Cole abaixo o ID do calendário:</p>
        <Input 
          value={calendarId}
          onChange={(e) => setCalendarId(e.target.value)}
          placeholder="abc123@group.calendar.google.com"
        />
        
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Cancelar</Button>
          <Button onClick={() => onSubmit(calendarId)}>Linkar</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
```

---

## Etapa 4 — Hook `useProfessionalCalendars` + `provisionCalendar`

```ts
// useProfessionalCalendars.ts
export function useProfessionalCalendars() {
  return useQuery({
    queryKey: ['professional_calendars'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('professional_calendars')
        .select('*');
      if (error) throw error;
      return data;
    }
  });
}

// useProvisionCalendar.ts
export function useProvisionCalendar() {
  return useMutation({
    mutationFn: async (params: {
      link_type: string;
      label: string;
      linked_professional_id?: string;
      google_email: string;
      mode: 'create' | 'use_existing';
      existing_calendar_id?: string;
    }) => {
      const { data, error } = await supabase.functions.invoke('google-calendar-provision', {
        body: params,
      });
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['professional_calendars'] });
    },
  });
}
```

---

## Etapa 5 — Forms + AbaBlocos

### CalendarLinksForm wrapper

```tsx
export function CalendarLinksForm() {
  return <CalendarLinksManager />;
}
```

### AbaBlocos.tsx — Adicionar ao section AGENDA

```tsx
{ id: "calendar_links", title: "Calendários linkados", section: "agenda" }
```

### EditBoxDialog.tsx

TITLES: `calendar_links: "Calendários linkados"`. Render `<CalendarLinksForm>`.

---

## Etapa 6 — Cleanup + deploy

### Antes do deploy

```sql
SELECT COUNT(*) FROM persona_boxes WHERE box_type = 'calendar_links';
SELECT COUNT(*) FROM professional_calendars;
```

### Deploy

Sem deploy de edge. Lovable build automático no merge.

### Validação pós-deploy

1. Card "Calendários linkados" aparece na seção AGENDA
2. Cliente clica → modal aberto
3. Botão "+ Adicionar calendário"
4. Card colapsado mostra:
   - Status badge
   - Tipo de link dropdown
   - Nome do calendário
   - (Se Profissional) dropdown de profissionais
   - Email
5. Profissional sem email aparece desabilitado no dropdown
6. Botão "Provisionar" chama edge → status muda pra "provisioned"
7. Botão "Usar calendário existente" abre modal com email da SA copiável
8. Status "error" mostra botão "Tentar novamente"

---

## Critérios de aceite

- [ ] Etapa 1 confirmação aprovada
- [ ] CALENDAR_LINKS_SCHEMA documental em box-schemas.ts
- [ ] CalendarLinksSchema Zod
- [ ] `<CalendarLinksManager>` componente novo (com sub-componentes)
- [ ] Hook `useProfessionalCalendars` (lê tabela)
- [ ] Hook `useProvisionCalendar` (chama edge)
- [ ] Dropdown filtrado de profissionais (com email vs sem email)
- [ ] Auto-preenche email do estabelecimento quando link_type=Estabelecimento
- [ ] Modal "Usar calendário existente" com email da SA copiável
- [ ] Status badge colorido (4 estados)
- [ ] Botões de ação contextuais (Provisionar / Tentar novamente / Ver no Google)
- [ ] Sync inicial: caixa carrega rows existentes de professional_calendars
- [ ] Build/tsc/vitest verde
- [ ] PR description anota: "PR3 fecha UI de Calendar Links. PR4-6 entregam sync de appointments."

---

## Restrições

- ❌ Sem implementar appointments (PR4)
- ❌ Sem webhook receiver (PR5)
- ❌ Sem compiler ainda (PR6)
- ❌ Sem editar `linked_professional_id` após save (vincula uma vez só)
- ✅ Branch: `schedule-pr3-calendar-links`
- ✅ PR título: `feat(schedule): Calendar Links + UI provisionamento (PR3)`

---

## Pós-merge — Próximo: PR4 (Schema appointments)

PR4 entrega tabelas `appointments` + `appointment_google_sync` + edge push CRM → Google + trigger.

Estimativa: ~1 dia.

---

## O que NÃO fazer neste PR

- ❌ Sync de appointments (PR4)
- ❌ Webhook Google → CRM (PR5)
- ❌ Tools IA (PR6)
- ❌ Cron pull conciliatório (PR5)
- ❌ Migration de dados legacy (não existe)
