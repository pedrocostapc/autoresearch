# Hotfix Calendar Config — Buffer separado + max_parallel_resources

> **Hotfix pequeno** antes do PR4 da Sprint Schedule. Adiciona 3 ajustes na caixa Calendar Config (PR2 já mergeado).
>
> Estimativa: ~0.5 dia.
> Branch: `schedule-hotfix-calendar-config-buffers`

---

## Contexto

PR2 da Sprint Schedule entregou caixa Calendar Config com 1 campo `buffer_minutes` (genérico) e sem `max_parallel_resources`.

Decisão em conversa subsequente: dividir buffer em **antes/depois** (igual checkin/checkout de hotel) + adicionar capacidade paralela pra casos como chopp delivery com N máquinas.

## Mudanças (3 ajustes)

### 1. Renomear `buffer_minutes` → `buffer_after_minutes`
- Significado: tempo de "checkout" depois do agendamento
- Valor existente nas cobaias (zero ou null) preservado

### 2. Adicionar `buffer_before_minutes`
- Tempo de "checkin" antes do agendamento
- Number, opcional, default 0

### 3. Adicionar `max_parallel_resources`
- Quantos agendamentos paralelos cabem no mesmo horário
- Number, opcional (vazio = sem limite, useful pra prestador único)
- Exemplos: chopp delivery=10 máquinas, salão de eventos=2 espaços (salão + piscina)
- Apenas armazenado nesta PR. PR6 implementa a lógica de check_availability.

## Schema final atualizado

Bloco "Política de agendamento" passa de 5 pra **7 campos**:

| Campo | Tipo | Status |
|---|---|---|
| min_advance_time | text | existente |
| max_advance_time | text | existente |
| default_duration_minutes | number | existente |
| **buffer_before_minutes** | number | **NOVO** |
| **buffer_after_minutes** | number | **RENOMEADO de buffer_minutes** |
| reschedule_until_hours | number | existente |
| **max_parallel_resources** | number | **NOVO** |

Outros blocos (Estabelecimento, Direcionamento IA) intactos.

---

## Etapa 1 — Confirmações curtas

### A. Dados existentes em `buffer_minutes`

```sql
SELECT 
  tenant_id,
  data->>'buffer_minutes' AS buffer_minutes
FROM persona_boxes
WHERE box_type = 'calendar_config' 
  AND data ? 'buffer_minutes';
```

Reportar volume. Esperado: zero ou pouquíssimo (caixa nova).

Se houver, **migração de dados leve no front:** quando user abrir caixa, hook copia `buffer_minutes` → `buffer_after_minutes` e remove `buffer_minutes`. Single-shot.

### B. Decisões pendentes (curtas)

#### B1. Migração `buffer_minutes` → `buffer_after_minutes`
**Opções:**
- A) Migração no front (hook lê chave antiga, migra ao salvar)
- B) Migration SQL em rows existentes
- C) Reset (DELETE rows antigas, ninguém preencheu mesmo)

**Recomendação:** C (DELETE). Caixa nova, cobaias só. Limpo e simples.

#### B2. Helper text dos novos campos

`buffer_before_minutes`: "Tempo de preparo antes do agendamento (ex: 15min pra preparação)"

`buffer_after_minutes`: "Tempo de recolhimento depois do agendamento (ex: 15min pra limpeza)"

`max_parallel_resources`: "Quantos agendamentos cabem no mesmo horário (ex: 10 chopeiras = 10 paralelos). Vazio = sem limite."

#### B3. Validação Zod
- Os 2 buffers: `z.number().int().nonnegative().optional()`
- `max_parallel_resources`: `z.number().int().positive().optional()`

### Aguarda OK.

---

## Etapa 2 — Mudanças

### Box-schemas.ts

```ts
// CALENDAR_CONFIG_SCHEMA, bloco "Política de agendamento":
{
  field: "buffer_before_minutes",   // NOVO
  question: "Buffer ANTES do agendamento (minutos)",
  type: "number",
  helper: "Tempo de preparo antes (ex: 15min)",
},
{
  field: "buffer_after_minutes",     // RENOMEADO
  question: "Buffer DEPOIS do agendamento (minutos)",
  type: "number",
  helper: "Tempo de recolhimento depois (ex: 15min)",
},
{
  field: "max_parallel_resources",   // NOVO
  question: "Agendamentos paralelos máximos",
  type: "number",
  helper: "Quantos cabem no mesmo horário (ex: 10 chopeiras). Vazio = sem limite.",
},
```

Remove campo `buffer_minutes` (renomeado, não é mais existente).

### Zod (personaBoxSchemas.ts)

```ts
export const CalendarConfigSchema = z.object({
  // ... outros campos
  buffer_before_minutes: z.number().int().nonnegative().optional(),
  buffer_after_minutes: z.number().int().nonnegative().optional(),
  max_parallel_resources: z.number().int().positive().optional(),
});
```

Remove `buffer_minutes`.

---

## Etapa 3 — Cleanup + deploy

### Antes do deploy

**1) DELETE preventivo (Pedro roda):**
```sql
DELETE FROM persona_boxes WHERE box_type = 'calendar_config';
```

Caixa nova, ninguém preencheu de verdade ainda.

### Deploy

Sem deploy de edge. Lovable build automático no merge.

### Validação pós-deploy

1. Caixa "Configurações da agenda" abre normalmente
2. Bloco "Política de agendamento" agora tem 7 campos
3. 2 buffers separados (antes/depois) editáveis
4. `max_parallel_resources` editável (number)
5. **Não-regressão:** todos os outros campos preservam funcionamento

---

## Critérios de aceite

- [ ] Schema declarativo atualizado (7 campos no bloco Política)
- [ ] Zod atualizado
- [ ] Pedro roda DELETE preventivo
- [ ] Build/test verde
- [ ] PR description anota: "Hotfix prepara Calendar Config pra cases de resource paralelo (chopp delivery, salão+piscina). PR4-6 implementam lógica."

---

## Restrições

- ❌ Sem ALTER TYPE (caixa já existe no enum)
- ❌ Sem implementar lógica de buffer/parallel (PR6 cuida)
- ❌ Sem migração de dados (DELETE preventivo)
- ✅ Branch: `schedule-hotfix-calendar-config-buffers`
- ✅ PR título: `feat(schedule): buffer separado + max_parallel_resources em Calendar Config (hotfix)`

---

## Pós-merge

**Próximo: PR4** — tabela `appointments` + sync push CRM→Google + trigger.

Tabela `appointments` ganha coluna `resource_id` (text, nullable) pra cases de resource paralelo. PR4 não implementa lógica de availability — só armazena o campo.

PR6 implementa:
- Tools IA respeitam `buffer_before` + `buffer_after`
- Tools IA respeitam `max_parallel_resources` (chama check_resource_availability)
- Sistema escolhe resource_id livre automaticamente quando cria appointment
