# PR2 Sprint Schedule — Caixa Configuração de Calendário (singleton)

> **Caixa singleton de configurações globais de agendamento.** Reusa toda infra Sprint Catalog (`<BoxFormGeneric>`).
>
> Estimativa: ~0.5 dia.
> Branch: `schedule-pr2-calendar-config`

---

## Contexto

PR1 entregou:
- Tabela `professional_calendars`
- Edge `google-calendar-provision`
- Helper `google-auth.ts`
- 2 ALTER TYPE no enum (`calendar_config`, `calendar_links`)

**PR2 entrega:** caixa `calendar_config` (singleton) com schema declarativo + form wrapper.

**Não entrega:**
- UI de provisionamento (vai no PR3 junto com `calendar_links`)
- Tool IA pra calendário (vai no PR6)
- Compiler ainda não emite essa caixa pro contexto da IA (PR6 também)

---

## Schema final (10 campos / 3 blocos)

| Bloco | Campo | Tipo |
|---|---|---|
| **1. Estabelecimento** | establishment_calendar_email | email |
| | timezone | single_choice (default America/Sao_Paulo) |
| **2. Política de agendamento** | min_advance_time | text |
| | max_advance_time | text |
| | default_duration_minutes | number |
| | buffer_minutes | number |
| | reschedule_until_hours | number |
| **3. Direcionamento IA** | ai_can_confirm | single_choice (Sim/Confirmar/Não) |
| | no_slot_fallback | textarea |
| | ai_notes | textarea |

**Total: 10 campos. Cardinality singleton. Sem obrigatórios estritos** (cliente preenche o que aplica).

---

## Etapa 1 — Confirmações antes de codar

### A. Tipo `email` no QuestionBlock

Já existe? PR2 do Catalog adicionou pra Links/Pagamento. Confirmar.

### B. Lista de timezones

Single_choice com quantos valores?

**Recomendação:** 4 timezones brasileiros principais:
- `America/Sao_Paulo` (default — BRT/BRST, maioria do país)
- `America/Manaus` (AMT, AM/RR/RO/parte do MT)
- `America/Belem` (BRT sem horário de verão)
- `America/Noronha` (FNT, Fernando de Noronha)

Cobre 95% dos casos. Cliente em outro fuso pode falar com suporte.

Confirmar lista.

### C. Decisões pendentes

#### C1. `default_duration_minutes` — qual default sugerido?

Não é obrigatório, mas helper sugere algo razoável.

**Recomendação:** sem default. Helper: "Quanto tempo cada serviço dura em média? (ex: 30 minutos pra corte de cabelo, 60 pra consulta)".

#### C2. `min_advance_time` e `max_advance_time` — formato livre ou estruturado?

Cliente pode digitar:
- "1 dia"
- "24 horas"
- "2 semanas"

Texto livre vs structured (number + unit dropdown).

**Recomendação: texto livre.** Razões:
- Casos atípicos cobertos ("apenas no mesmo dia", "3 horas antes")
- IA interpreta naturalmente
- Estruturar adicionaria complexidade sem ganho

#### C3. `ai_can_confirm = "Não"` — significado

Se cliente marcar "Não", IA **não pode** confirmar agendamento direto. Sempre passa pra humano.

**Implicação no PR6:** tool `create_appointment` precisa respeitar essa flag. Se "Não", retorna mensagem sugerindo passar pra atendente humano.

PR2 só armazena. PR6 implementa.

#### C4. `no_slot_fallback` — exemplos

Helper sugere casos típicos:
- "Sugerir próximo profissional disponível"
- "Oferecer lista de espera"
- "Sempre transferir pra recepção humana"
- "Marcar primeiro horário disponível no próximo dia útil"

#### C5. Compilers — emite no contexto ou só consome via tool?

Caixa Calendar Config é **singleton** com 10 campos. Não tem tool dedicada.

**Decisão:** emite no contexto (formatCalendarConfig) similar a `formatDeliveryConfig`. IA precisa saber sempre:
- Timezone (pra interpretar "amanhã 14h")
- Política de agendamento (pra avisar cliente sobre antecedência mínima)
- Fallback quando não tem slot

**Não emite ainda em PR2.** Compiler novo entra no PR6 junto com as tools. PR2 só armazena.

Confirmar.

#### C6. AbaBlocos — onde aparece o card?

Sprint Catalog tinha 4 seções: SOBRE, O QUE OFERECE, ATENDIMENTO, PERSONALIZE.

**Opções pra Calendar Config:**

**A)** Nova seção AGENDA (com Calendar Config + Calendar Links + futuro Forms?)
**B)** Dentro de SOBRE (configurações gerais)
**C)** Dentro de O QUE OFERECE (próximo a Services e Events)

**Recomendação: A (nova seção AGENDA).** Razões:
- Agrupa Calendar Config + Calendar Links (PR3)
- Cliente entende imediatamente o conceito
- Quando Forms chegar, pode ir em outra seção (FORMULÁRIOS) ou dentro de AGENDA dependendo de uso

Confirmar.

#### C7. DELETE manual

Pedro roda. Volume esperado: zero (caixa nova, ninguém preencheu ainda).

---

## Aguarda OK + escolhas em C1-C7 antes de prosseguir.

---

## Etapa 2 — Schema declarativo

```ts
// box-schemas.ts

export const CALENDAR_CONFIG_SCHEMA: BoxSchemaDef = {
  boxType: "calendar_config",
  label: "Configurações da agenda",
  cardinality: "singleton",
  hasExcel: false,
  blocks: [
    {
      title: "Estabelecimento",
      fields: [
        { 
          field: "establishment_calendar_email", 
          question: "Email principal pra compartilhar calendário do estabelecimento", 
          type: "email",
          helper: "Sistema vai enviar convite pra esse email quando você criar o calendário principal" 
        },
        { 
          field: "timezone", 
          question: "Fuso horário", 
          type: "single_choice", 
          options: ["America/Sao_Paulo", "America/Manaus", "America/Belem", "America/Noronha"],
          helper: "Maioria do Brasil usa America/Sao_Paulo (BRT/BRST)" 
        },
      ],
    },
    {
      title: "Política de agendamento",
      fields: [
        { 
          field: "min_advance_time", 
          question: "Antecedência mínima pra agendar", 
          type: "text",
          placeholder: "Ex: 2 horas, 1 dia",
          helper: "Quanto tempo o cliente precisa avisar antes do horário" 
        },
        { 
          field: "max_advance_time", 
          question: "Antecedência máxima", 
          type: "text",
          placeholder: "Ex: 30 dias, 3 meses",
          helper: "Até quando você aceita marcar agendamentos" 
        },
        { 
          field: "default_duration_minutes", 
          question: "Duração padrão de serviço (minutos)", 
          type: "number",
          helper: "Fallback quando o serviço específico não tem duração definida (ex: 30 pra corte, 60 pra consulta)" 
        },
        { 
          field: "buffer_minutes", 
          question: "Buffer entre agendamentos (minutos)", 
          type: "number",
          helper: "Tempo livre obrigatório entre 2 agendamentos consecutivos. Ex: 15 minutos pra preparação" 
        },
        { 
          field: "reschedule_until_hours", 
          question: "Reagendamento permitido até quantas horas antes", 
          type: "number",
          helper: "Ex: 24 horas. Depois disso, vira política de cancelamento" 
        },
      ],
    },
    {
      title: "Direcionamento IA",
      fields: [
        { 
          field: "ai_can_confirm", 
          question: "IA pode confirmar agendamento direto?", 
          type: "single_choice", 
          options: ["Sim", "Confirmar", "Não"],
          helper: "Sim: IA marca direto. Confirmar: IA pergunta antes. Não: só atendente humano marca." 
        },
        { 
          field: "no_slot_fallback", 
          question: "O que fazer se profissional não tem horário disponível", 
          type: "textarea",
          placeholder: "Ex: Sugerir próximo profissional disponível, ou oferecer lista de espera, ou transferir pra recepção humana",
          helper: "IA usa essa orientação quando bate em horário cheio" 
        },
        { 
          field: "ai_notes", 
          question: "Observações pra IA", 
          type: "textarea",
          helper: "Qualquer regra ou consideração específica sobre agendamento" 
        },
      ],
    },
  ],
};

// Adicionar ao registry
export const BOX_SCHEMAS: Record<string, BoxSchemaDef> = {
  // ... anteriores
  calendar_config: CALENDAR_CONFIG_SCHEMA,
};
```

### Zod schema

```ts
export const CalendarConfigSchema = z.object({
  establishment_calendar_email: z.string().email().optional(),
  timezone: z.enum(["America/Sao_Paulo", "America/Manaus", "America/Belem", "America/Noronha"]).optional(),
  min_advance_time: z.string().optional(),
  max_advance_time: z.string().optional(),
  default_duration_minutes: z.number().int().positive().optional(),
  buffer_minutes: z.number().int().nonnegative().optional(),
  reschedule_until_hours: z.number().int().nonnegative().optional(),
  ai_can_confirm: z.enum(["Sim", "Confirmar", "Não"]).optional(),
  no_slot_fallback: z.string().optional(),
  ai_notes: z.string().optional(),
});

export const BOX_DEFAULT_DATA: Record<PersonaBoxType, any> = {
  // ... anteriores
  calendar_config: {},
};
```

---

## Etapa 3 — Form wrapper

```tsx
// CalendarConfigForm.tsx
export function CalendarConfigForm(props: CalendarConfigFormProps) {
  return <BoxFormGeneric boxType="calendar_config" {...props} />;
}
```

### AbaBlocos.tsx — Nova seção AGENDA

Adicionar seção entre ATENDIMENTO e PERSONALIZE:

```tsx
// Seção AGENDA
{
  id: "agenda",
  title: "Agenda",
  boxes: [
    "calendar_config",   // PR2
    // "calendar_links",  // PR3 adiciona
  ],
}
```

Card: "Configurações da agenda" → abre `<EditBoxDialog>` com `<CalendarConfigForm>`.

### EditBoxDialog.tsx

Adicionar entry pra `calendar_config` → render `<CalendarConfigForm>`. TITLES `calendar_config: "Configurações da agenda"`.

---

## Etapa 4 — Cleanup + deploy

### Antes do deploy

**1) Volume (esperado zero):**
```sql
SELECT COUNT(*) FROM persona_boxes WHERE box_type = 'calendar_config';
```

**2) DELETE preventivo (se aparecer algo de testes anteriores):**
```sql
DELETE FROM persona_boxes WHERE box_type = 'calendar_config';
```

**3) Confirma:**
```sql
SELECT COUNT(*) FROM persona_boxes WHERE box_type = 'calendar_config';
```

### Deploy

Sem deploy de edges (sem mudança em compilers/tools nesta PR). Só:

```bash
gh pr merge <PR> --squash --delete-branch
git checkout main && git pull origin main
git push origin main  # Lovable build
```

### Validação pós-deploy

1. Nova seção "AGENDA" aparece no painel
2. Card "Configurações da agenda" visível
3. Modo Manual: 3 accordions (Estabelecimento, Política, Direcionamento IA) com 10 campos
4. Preenche, salva, recarrega, persiste
5. **Não-regressão:** todas as 15 caixas anteriores continuam funcionando

---

## Critérios de aceite

- [ ] Etapa 1 confirmação aprovada
- [ ] CALENDAR_CONFIG_SCHEMA em box-schemas.ts (10 campos, 3 blocos, singleton)
- [ ] CalendarConfigSchema Zod novo
- [ ] Nova seção AGENDA em AbaBlocos
- [ ] CalendarConfigForm wrapper ~12 linhas
- [ ] EditBoxDialog ganha entry pra calendar_config
- [ ] Build/tsc/vitest verde
- [ ] PR description anota: "PR2 só armazena. Compiler/tool entra no PR6 junto com as tools de agendamento."

---

## Restrições

- ❌ Sem mexer em outras caixas
- ❌ Sem implementar tool (PR6)
- ❌ Sem emitir compiler ainda (PR6)
- ❌ Sem UI de provisionamento (PR3)
- ❌ Sem cross-field validation
- ✅ Mostra diff antes do commit
- ✅ Branch: `schedule-pr2-calendar-config`
- ✅ PR título: `feat(schedule): caixa Configurações da agenda (PR2)`

---

## Pós-merge — Próximo: PR3 (Calendar Links + UI provisionamento)

PR3 é o **maior da Sprint Schedule** (~1.5 dia):
- Caixa `calendar_links` (multi-item)
- Schema com 3 tipos (estabelecimento/profissional/externo)
- Dropdown puxa Team filtrando quem tem email
- Aviso visual: "Profissional sem email não aparece — preencher em Equipe"
- Botão "Provisionar" chama edge PR1
- Botão "Usar calendário existente" (Opção C)
- Status visível (pending/provisioned/shared/error)
- UI de retry quando falha
- Botão "Copiar email da SA" pra modo use_existing

---

## O que NÃO fazer neste PR

- ❌ Compiler/tool de calendário (PR6)
- ❌ UI de provisionamento (PR3)
- ❌ Caixa Calendar Links (PR3)
- ❌ Sync de appointments (PR4-PR5)
- ❌ Cross-field validation
