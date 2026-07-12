# Sprint Arquétipos MVP Manual — Prompt customizado por tenant

> **Sprint pequena (1 PR único, ~1 dia).** MVP que destrava migração de tenants em manual → blocks mantendo comportamento customizado.
>
> Estimativa: ~1 dia.
> Branch: `archetypes-mvp-manual`

---

## Contexto

Vanderlei (e outros 8-9 tenants em `persona_mode='manual'`) tem prompt monolítico customizado (~29k chars no caso do Vanderlei). Sprint Arquétipos Completa (presets por nicho) é grande (~1-2 semanas) e fica pra depois.

**MVP Manual destrava agora:**
- Pedro/cliente cola prompt customizado num campo
- Sistema prepend ao master prompt do CRM
- Tenant pode migrar pra `persona_mode='blocks'` usando blocks + arquétipo manual

**Após Sprint Arquétipos Completa:**
- Migra `manual_archetype_prompt` → `attendant_archetype_id` (FK)
- Tenants viram entries em `attendant_archetypes` privadas

---

## Schema

### Migration

```sql
ALTER TABLE public.tenants 
ADD COLUMN IF NOT EXISTS manual_archetype_prompt text;

COMMENT ON COLUMN public.tenants.manual_archetype_prompt IS
  'MVP Arquétipos: prompt customizado prepended ao master prompt. Sprint Arquétipos Completa migra pra attendant_archetype_id (FK).';
```

**Sem CHECK constraint de tamanho.** Cliente pode colar prompt grande (Vanderlei tem 29k). Limite via UI (cap 100k chars) + compiler trunca se passar.

---

## Compiler

`ai-reply` adiciona prepend:

```ts
// No início da construção do master prompt
const customArchetype = tenant.manual_archetype_prompt?.trim();

if (customArchetype) {
  masterPrompt = customArchetype + "\n\n---\n\n" + masterPrompt;
}
```

**Ordem final do master prompt:**
```
[manual_archetype_prompt] (se preenchido)
---
[Você é a {ai_name}, atendente de {establishment}...]
[Tone: {tone}]
[Caixas preenchidas...]
[Tools disponíveis: query_team, search_team_slots, etc.]
```

---

## UI

### Localização
Aba **PERSONA** em `/settings/ai`, após Passo 03 (Blocos de conhecimento).

### Layout

```
PASSO 04 · ARQUÉTIPO MANUAL [BETA]

Modo de comportamento da IA.
Cole abaixo o prompt que define como ela age no atendimento.
Esse texto é prepended ao master prompt do sistema.

⚠️ [BETA] Sprint Arquétipos completa virá com presets por nicho.

┌─────────────────────────────────────────────────────┐
│ [textarea — 20-25 linhas visíveis, expansível]      │
│                                                      │
│ Você é a Pedro, atendente do consultório Maranello..│
│ Sua função é triagem entre contatos do Dr. João.    │
│ ...                                                  │
└─────────────────────────────────────────────────────┘

Caracteres: 0 / 100.000

[Salvar arquétipo]
```

### Componente novo

`src/features/ai-settings/components/ManualArchetypeCard.tsx`

- Textarea grande (`<Textarea>` shadcn)
- Contador de chars no canto inferior direito
- Botão "Salvar arquétipo" com mutation
- Toast de sucesso
- Cor amarela do badge `[BETA]`

### Hook

`useManualArchetype.ts`:
- `useQuery` lê `tenants.manual_archetype_prompt` do tenant atual
- `useMutation` faz update no campo

---

## Etapa 1 — Confirmações antes de codar

### A. Verificações

#### A1. Tabela `tenants` schema
```bash
\d public.tenants
```
Confirma:
- Tabela existe
- Tem campo `id uuid PRIMARY KEY`
- Schema padrão `public`

#### A2. Tenants em manual hoje
```sql
SELECT COUNT(*) FROM tenants WHERE persona_mode = 'manual';
```

Esperado: ~9 (memory anterior). Confirmar.

#### A3. Hook de update pra `tenants`
Existe hook que atualiza tenants? Pattern usado em outros lugares?

#### A4. Aba PERSONA — estrutura atual
Como Passo 03 (Blocos de conhecimento) está estruturado? Card next vai como Passo 04 inserido nessa mesma estrutura.

### B. Decisões pendentes

#### B1. Cap de caracteres no front

100k é safe (Vanderlei tem 29k, margem 3x).

**Visual:**
- 0-80k → verde
- 80-95k → amarelo
- 95-100k → vermelho
- > 100k → bloqueia save

**Compiler defensivo:** se passar do limit por alguma razão, trunca ao começar do master prompt + adiciona aviso "[...truncado por exceder limite]".

#### B2. Persona mode interage com archetype?

Quando `manual_archetype_prompt` está preenchido E `persona_mode='blocks'`:
- Compiler prepend funciona normal
- IA usa arquétipo + caixas

Quando `manual_archetype_prompt` preenchido E `persona_mode='manual'`:
- Tenant está em modo manual (sem caixas)
- Master prompt todo é o manual prompt já
- `manual_archetype_prompt` **fica ignorado** (não duplica)

**Lógica no compiler:**
```ts
if (persona_mode === 'blocks' && customArchetype) {
  masterPrompt = customArchetype + "\n---\n" + masterPrompt;
}
// modo manual ignora manual_archetype_prompt
```

**Confirmar.**

#### B3. RLS

`tenants.manual_archetype_prompt` editável por:
- Admin/owner do tenant
- Super admin

Pattern: já existe RLS de UPDATE em `tenants` no projeto?

#### B4. Validação Zod

```ts
manual_archetype_prompt: z.string().max(100_000).optional()
```

#### B5. Card oculto se persona_mode='manual'?

Tenant em `manual` não usa essa feature. **Opções:**

**A) Card sempre visível, com aviso "Em modo manual, esse campo é ignorado"**
**B) Card só aparece em `blocks`**

Recomendo **A**. Razões:
- Tenant pode preencher antes de migrar pra blocks (workflow natural)
- Pedro pode preencher pelo super admin enquanto tenant ainda está em manual
- Sem condicional na UI

---

## Aguarda OK + escolhas em B1-B5 antes de prosseguir.

---

## Etapa 2 — Migration

```sql
ALTER TABLE public.tenants 
ADD COLUMN IF NOT EXISTS manual_archetype_prompt text;

COMMENT ON COLUMN public.tenants.manual_archetype_prompt IS
  'MVP Arquétipos: prompt customizado prepended ao master prompt. Sprint Arquétipos Completa migra pra attendant_archetype_id (FK).';
```

Pedro roda no SQL Editor.

Confirma:
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'tenants' AND column_name = 'manual_archetype_prompt';
```

---

## Etapa 3 — Compiler

`supabase/functions/ai-reply/index.ts` (ou onde master prompt é construído):

Adicionar lógica de prepend conforme B2.

---

## Etapa 4 — UI

### Hook
`src/features/ai-settings/hooks/useManualArchetype.ts`

### Componente
`src/features/ai-settings/components/ManualArchetypeCard.tsx`

### Integração
Adicionar ao layout da aba PERSONA, após Passo 03.

---

## Etapa 5 — Deploy

```bash
gh pr merge <PR> --squash --delete-branch
git checkout main && git pull origin main
supabase functions deploy ai-reply
git push origin main
```

### Validação pós-deploy

1. Aba PERSONA tem novo Passo 04 com card BETA
2. Textarea funciona
3. Contador de chars atualiza
4. Botão Salvar persiste
5. Recarrega → valor persiste
6. (Smoke real) cliente envia mensagem → IA responde com tom/comportamento do arquétipo

---

## Critérios de aceite

- [ ] Etapa 1 confirmação aprovada
- [ ] Migration aplicada (coluna `manual_archetype_prompt` em tenants)
- [ ] Compiler prepend funcional (só em blocks mode)
- [ ] UI: Passo 04 BETA com textarea + contador + save
- [ ] RLS respeitado (admin/owner do tenant + super admin)
- [ ] Build/tsc/vitest verde
- [ ] PR description anota: "MVP Arquétipos. Sprint Arquétipos Completa (presets por nicho) é futura sprint."

---

## Restrições

- ❌ Sem schema declarativo (campo livre)
- ❌ Sem presets por nicho (Sprint Arquétipos Completa)
- ❌ Sem migration de dados (Pedro/clientes preenchem manualmente)
- ❌ Sem mexer em persona_mode logic além do prepend
- ✅ Branch: `archetypes-mvp-manual`
- ✅ PR título: `feat(archetypes): MVP arquétipo manual prepended ao master prompt`

---

## Pós-merge

**Vanderlei pode migrar pra blocks:**
1. Pedro abre painel do Vanderlei como super admin
2. Cola prompt monolítico (29k chars) em manual_archetype_prompt
3. Muda `persona_mode` pra `blocks`
4. Preenche caixas com info estruturada (Products, Services, Team, etc)
5. IA usa: arquétipo (comportamento) + caixas (dados) + tools

**Próximas sprints possíveis:**
- Sprint Forms (~2 dias)
- Sprint Arquétipos Completa (~1-2 semanas) — migra manual_archetype_prompt pra attendant_archetypes
