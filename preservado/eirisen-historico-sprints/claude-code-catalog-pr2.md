# PR2 — Hours + Links (Sprint Catalog Onda 1)

> Segundo PR da Sprint Catalog. Reusa a fundação criada no PR1 (`box-schemas.ts`, `<QuestionBlock>`, `<BoxFormGeneric>`).
>
> Estimativa: 4-6 horas (validação real da fundação — se sair fácil, fundação tá boa; se exigir mudança em `<QuestionBlock>` ou `<BoxFormGeneric>`, é aprendizado pra próximos PRs).
>
> Branch: `catalog-pr2-hours-links`

---

## Contexto

PR1 entregou fundação + caixa Establishment piloto (PR #205, 98102d9). Funcionando em produção.

PR2 migra mais 2 caixas singleton — **Hours** e **Links** — usando a mesma fundação. Sem novos componentes, só novos schemas + 2 wrappers de form (12 linhas cada).

Decisões importantes herdadas:
- Hours suporta **2 turnos por dia** (almoço fechado) — decisão Pedro
- Links ganha **mais redes sociais** (TikTok, LinkedIn, YouTube, X)
- Pedro autorizou apagar dados das 14 cobaias em blocks
- DELETE manual via SQL Editor antes do deploy (Pedro assume)

Ler antes de codar:
- Memory items #15 (UX padrão), #17 (Sprint Catalog faseada), #18 (PR1 mergeado)
- Documento `/mnt/user-data/outputs/00-CAIXAS-ESTRUTURA-FINAL.md` — seções Hours e Links

---

## Schemas finais

### Hours (Horário de funcionamento)

**Suporta 2 turnos por dia.** Cada dia tem 5 campos:
1. Fechado o dia? (Sim/Não)
2. Abre às (1º turno)
3. Fecha às (1º turno)
4. Abre às (2º turno, opcional)
5. Fecha às (2º turno, opcional)

Total por dia: 5 campos × 7 dias = 35 campos + 3 especiais (feriados, datas comemorativas, observações) = **38 campos**.

```
Bloco 1: Segunda-feira (5 campos)
Bloco 2: Terça-feira (5 campos)
Bloco 3: Quarta-feira (5 campos)
Bloco 4: Quinta-feira (5 campos)
Bloco 5: Sexta-feira (5 campos)
Bloco 6: Sábado (5 campos)
Bloco 7: Domingo (5 campos)
Bloco 8: Especiais (3 campos: feriados, datas comemorativas, observações)
```

### Links e canais

```
Bloco 1: Localização
  - Google Maps URL

Bloco 2: Redes sociais
  - Instagram (@handle)
  - Facebook (URL)
  - TikTok (@handle)
  - LinkedIn (URL)
  - YouTube (URL)
  - X/Twitter (@handle)

Bloco 3: Contato
  - Site (URL)
  - E-mail
  - Telefone fixo
  - WhatsApp Business

Bloco 4: Catálogos
  - Catálogo (URL)
  - Cardápio (URL)

Bloco 5: Outros links
  - Lista livre {label, url}
```

---

## Etapa 1 — Confirmações antes de codar

Reportar:

### A. Schema atual de Hours

```bash
grep -n "HoursSchema\|formatHours" src/features/ai-settings/lib/personaBoxSchemas.ts supabase/functions/_shared/persona-compiler.ts
```

- Schema Zod atual de Hours (copia literal)
- Como `formatHours` é implementado hoje
- Se hoje suporta 1 ou 2 turnos
- Estrutura JSON de uma row real (sample)

### B. Schema atual de Links

- Schema Zod atual de Links (copia literal)
- Como `formatLinks` é implementado hoje
- Se já tem campo `others` como array livre
- Sample real da row mais preenchida (do SQL B.3 anterior, link teve 9 tenants com avg 137 chars)

### C. Tipos de input que faltam no `<QuestionBlock>`

PR1 criou 10 tipos. Confirmar quais já existem e quais precisam ser adicionados:

| Tipo | Usa em PR2? | Status |
|---|---|---|
| `text` | Hours observações, Links handles | ? |
| `textarea` | Hours feriados, observações | ? |
| `boolean` | Hours "Fechado o dia?" | ? |
| `time` | Hours horários (08:00, 12:00) | ❓ NOVO se não tem |
| `url` | Links várias | ? |
| `email` | Links e-mail | ? |
| `link_list` | Links "Outros links" array | ❓ NOVO complexo |

Reportar quais tipos já existem em `QuestionBlock.tsx` e quais precisam ser adicionados.

### D. Decisões pendentes

#### D1. UI de Hours — qual abordagem?

7 dias da semana = bastante volume visual. 3 opções:

**Opção A: 8 accordions (1 por dia + Especiais)**
```
▼ Segunda-feira (3 de 5 respondidas)
  ⭕ Fechado às segundas? [Sim] [Não]
  ⭕ Abre às (1º turno) [08:00]
  ⭕ Fecha às (1º turno) [12:00]
  ...
▼ Terça-feira (0 de 5)
...
```
Default fechado. Cliente expande dia por dia. **Reusa BoxFormGeneric sem modificação.**

**Opção B: 2 accordions (Dias da semana / Especiais)**
- "Dias da semana" expande mostra **7 sub-cards horizontais ou verticais** com 5 campos cada
- "Especiais" segue padrão
- **Exige UI customizada** dentro do BoxFormGeneric

**Opção C: Tipo novo "weekday_hours"**
- Adiciona tipo no QuestionBlock que renderiza tabela 7×5
- Schema declarativo fica mais simples (1 campo só pra Hours)
- **Mais código novo no QuestionBlock**

Recomendação: **A**. Razões:
- Reusa BoxFormGeneric 100%
- Cliente foca 1 dia por vez (preenche, fecha, vai pro próximo)
- Padrão consistente com outras caixas
- Custo: 38 campos no schema declarativo (verboso mas explícito)

Code confirma se concorda ou prefere B/C.

#### D2. Tipo `time` no QuestionBlock

Adicionar `type: "time"` que renderiza `<Input type="time" />`. Trivial.

#### D3. Campo `others` em Links — como suportar lista livre?

Hoje Links tem `others: { label: string, url: string }[]` (array livre).

Opções:
- **Manter como está** mas não cabe no schema declarativo padrão. Vira sub-form com lógica especial.
- **Tipo novo `link_list`** no QuestionBlock que renderiza:
  ```
  ⭕ Outros links importantes
     [+ Adicionar link]
     ┌─────────────────────────────────┐
     │ Label: [Site do parceiro     ]  │
     │ URL:   [https://parceiro.com ]  │ [×]
     ├─────────────────────────────────┤
     │ Label: [Catálogo PDF         ]  │
     │ URL:   [https://...          ]  │ [×]
     └─────────────────────────────────┘
  ```

Recomendação: **tipo novo `link_list`**. Razões:
- Reusa pra outras caixas no futuro (Custom poderia usar)
- Componente isolado, fácil de testar
- BoxFormGeneric continua agnóstico

Code confirma ou propõe alternativa.

#### D4. Volumes em produção

```sql
SELECT box_type, COUNT(*) FROM persona_boxes 
WHERE box_type IN ('hours', 'links') AND is_active = true 
GROUP BY box_type;
```

Esperado: 14 hours, 9 links (do raio-x anterior). Confirmar números pra o DELETE manual.

---

## Aguarda OK antes de prosseguir.

---

## Etapa 2 — `box-schemas.ts` (adicionar 2 schemas)

Sem alterar tipos existentes. Apenas adicionar:

```ts
export const HOURS_SCHEMA: BoxSchemaDef = {
  boxType: "hours",
  label: "Horário de funcionamento",
  cardinality: "singleton",
  hasExcel: false,
  blocks: [
    {
      title: "Segunda-feira",
      fields: [
        { field: "monday_closed", question: "Fechado às segundas?", type: "boolean" },
        { field: "monday_open_1", question: "Abre às (1º turno)", type: "time" },
        { field: "monday_close_1", question: "Fecha às (1º turno)", type: "time" },
        { field: "monday_open_2", question: "Abre às (2º turno, opcional)", type: "time", helper: "Se tem pausa de almoço" },
        { field: "monday_close_2", question: "Fecha às (2º turno, opcional)", type: "time" },
      ],
    },
    // ... idem pra tuesday, wednesday, thursday, friday, saturday, sunday
    {
      title: "Especiais",
      fields: [
        { field: "holidays", question: "Como funciona em feriados?", type: "textarea" },
        { field: "special_dates", question: "Datas comemorativas com horário diferente", type: "textarea" },
        { field: "notes", question: "Observações sobre horários", type: "textarea" },
      ],
    },
  ],
};

export const LINKS_SCHEMA: BoxSchemaDef = {
  boxType: "links",
  label: "Links e canais",
  cardinality: "singleton",
  hasExcel: false,
  blocks: [
    {
      title: "Localização",
      fields: [
        { field: "google_maps_url", question: "Link do Google Maps", type: "url" },
      ],
    },
    {
      title: "Redes sociais",
      fields: [
        { field: "instagram", question: "Instagram", type: "text", placeholder: "@perfil" },
        { field: "facebook_url", question: "Facebook", type: "url" },
        { field: "tiktok", question: "TikTok", type: "text", placeholder: "@perfil" },
        { field: "linkedin_url", question: "LinkedIn", type: "url" },
        { field: "youtube_url", question: "YouTube", type: "url" },
        { field: "twitter", question: "X/Twitter", type: "text", placeholder: "@perfil" },
      ],
    },
    {
      title: "Contato",
      fields: [
        { field: "website_url", question: "Site", type: "url" },
        { field: "email", question: "E-mail", type: "email" },
        { field: "phone_landline", question: "Telefone fixo", type: "text" },
        { field: "whatsapp_business", question: "WhatsApp Business", type: "text" },
      ],
    },
    {
      title: "Catálogos",
      fields: [
        { field: "catalog_url", question: "Catálogo (link)", type: "url" },
        { field: "menu_url", question: "Cardápio (link)", type: "url" },
      ],
    },
    {
      title: "Outros links",
      fields: [
        { field: "others", question: "Outros links importantes", type: "link_list" },
      ],
    },
  ],
};

// Adicionar ao registry
export const BOX_SCHEMAS: Record<string, BoxSchemaDef> = {
  establishment: ESTABLISHMENT_SCHEMA,
  hours: HOURS_SCHEMA,        // novo
  links: LINKS_SCHEMA,         // novo
};
```

---

## Etapa 3 — Implementação Hours

### 3a. Tipo `time` no QuestionBlock (se não existe)

```tsx
// Adicionar case "time" no switch do QuestionBlock
case "time":
  return (
    <Input
      type="time"
      value={value ?? ""}
      onChange={(e) => onChange(e.target.value)}
      aria-required={field.required}
    />
  );
```

Adicionar `"time"` no type union `FieldType`.

### 3b. Form wrapper

`HoursForm.tsx` (ou similar) vira wrapper de ~12 linhas:

```tsx
import { BoxFormGeneric } from "@/features/ai-settings/components/blocos/BoxFormGeneric";

export function HoursForm(props: HoursFormProps) {
  return <BoxFormGeneric boxType="hours" {...props} />;
}
```

### 3c. Compiler refatorado

`formatHours` antigo deletado. Compiler agora usa `formatBoxFromSchema("hours", data)` (já criado no PR1).

Mas **atenção**: a saída do compiler pra Hours fica feia se cada campo virar pergunta. Tipo:

```
- Fechado às segundas: Não
- Abre às (1º turno): 08:00
- Fecha às (1º turno): 12:00
- Abre às (2º turno, opcional): 14:00
- Fecha às (2º turno, opcional): 18:00
```

Pesado. Hours pode precisar de tratamento especial no compiler — formatar dia inteiro em uma linha:

```
- Segunda: 08:00-12:00 e 14:00-18:00
- Terça: Fechado
- ...
```

**Decisão pendente:** o compiler genérico (formatBoxFromSchema) usa pergunta humana literal, ou Hours tem formatador especial que consolida?

Recomendação: **Hours tem formatador especial** (`formatHoursConsolidated`). Mais legível pra IA. Outras caixas usam genérico.

Code implementa fallback: se existe formatter específico no compiler, usa. Senão, usa genérico.

### 3d. Skeleton de migração

Schema atual tem campos diferentes. Pedro autorizou apagar. DELETE manual:
```sql
DELETE FROM persona_boxes WHERE box_type = 'hours';
-- Esperado: 14 rows
```

---

## Etapa 4 — Implementação Links

### 4a. Tipo `link_list` no QuestionBlock

Componente novo. Renderiza array de `{ label, url }` com botões "+ Adicionar" e "× Remover".

```tsx
case "link_list":
  return <LinkListInput value={value ?? []} onChange={onChange} />;

// Componente novo:
function LinkListInput({ value, onChange }: { value: { label: string; url: string }[]; onChange: (v: any[]) => void }) {
  return (
    <div className="space-y-2">
      {value.map((item, i) => (
        <div key={i} className="flex gap-2">
          <Input placeholder="Label" value={item.label} onChange={(e) => updateItem(i, "label", e.target.value)} />
          <Input placeholder="https://..." type="url" value={item.url} onChange={(e) => updateItem(i, "url", e.target.value)} />
          <Button variant="ghost" onClick={() => removeItem(i)}>×</Button>
        </div>
      ))}
      <Button variant="outline" onClick={addItem}>+ Adicionar link</Button>
    </div>
  );
}
```

### 4b. Form wrapper

`LinksForm.tsx`:

```tsx
export function LinksForm(props: LinksFormProps) {
  return <BoxFormGeneric boxType="links" {...props} />;
}
```

### 4c. Compiler

Links pode usar `formatBoxFromSchema` direto (genérico). Saída fica:

```
## Links e canais

### Localização
- Link do Google Maps: https://maps.app.goo.gl/...

### Redes sociais
- Instagram: @padariadopedro
- TikTok: @padariadopedro
...
```

Caso `others` não imprima bem com formatBoxFromSchema (porque é array de objetos), Code adiciona tratamento no formatter genérico pra type `link_list`:

```ts
if (field.type === "link_list" && Array.isArray(value)) {
  for (const item of value) {
    if (item.label && item.url) lines.push(`  - ${item.label}: ${item.url}`);
  }
  continue;
}
```

### 4d. DELETE manual:

```sql
DELETE FROM persona_boxes WHERE box_type = 'links';
-- Esperado: 9 rows
```

---

## Etapa 5 — Cleanup + deploy

### Antes do deploy

Pedro roda no SQL Editor:

```sql
DELETE FROM persona_boxes WHERE box_type = 'hours';
DELETE FROM persona_boxes WHERE box_type = 'links';

-- Confirma
SELECT box_type, COUNT(*) FROM persona_boxes 
WHERE box_type IN ('hours', 'links')
GROUP BY box_type;
-- Esperado: 0 rows
```

### Deploy

```bash
gh pr merge <PR> --squash --delete-branch
git checkout main && git pull origin main
supabase functions deploy ai-reply  # compiler mudou
git push origin main                 # Lovable build
```

### Validação pós-deploy

Pedro abre `/settings/ai`, testa:
- **Hours:** modal abre com 8 accordions (Seg-Dom + Especiais), cada um com contador. Preenche um dia, salva, recarrega.
- **Links:** modal abre com 5 accordions. Adiciona 2 links em "Outros links". Salva, recarrega, confirma persistência.

---

## Critérios de aceite

- [ ] Etapa 1 confirmação aprovada antes de codar
- [ ] `box-schemas.ts` ganha HOURS_SCHEMA + LINKS_SCHEMA + registry atualizado
- [ ] `<QuestionBlock>` ganha tipos `time` e `link_list`
- [ ] `<LinkListInput>` componente novo
- [ ] `HoursForm` e `LinksForm` viram wrappers de ~12 linhas
- [ ] Compiler: `formatHours` antigo removido, novo formatter consolidado pra Hours (decisão na Etapa 1)
- [ ] Compiler: `formatLinks` antigo removido, usa `formatBoxFromSchema` com tratamento pra `link_list`
- [ ] Build/tsc/vitest verde (testes existentes)
- [ ] Pedro confirma DELETE manual rodado antes do deploy
- [ ] PR description anota: "PR2 reusa fundação do PR1, adiciona 2 tipos novos no QuestionBlock"

---

## Restrições

- ❌ Migrations destrutivas no código (DELETE manual via SQL Editor)
- ❌ Smoke automático (Pedro testa)
- ❌ Mexer em master prompt
- ❌ Mexer em outras caixas (Establishment, Pagamento, etc)
- ✅ Pode adicionar tipos novos no QuestionBlock (`time`, `link_list`)
- ✅ Pode adicionar formatador específico no compiler (Hours consolidado)
- ✅ Mostrar diff antes do commit
- ✅ Branch: `catalog-pr2-hours-links`
- ✅ PR título: `feat(catalog): Hours + Links com schema declarativo (PR2)`

---

## Pós-merge (PR3)

PR3 vai introduzir caixa **Pagamento** (nova, não existe hoje):
- Singleton, perguntas
- ~20 campos em 5 blocos (PIX, Banco, Cartão online, Outras formas, Política IA)
- Cria caixa do zero (sem schema antigo pra migrar)
- Sem DELETE manual necessário

PR4: Products + Excel + tool refatorada (o grande, destrava 30k itens).

---

## O que NÃO fazer neste PR

- ❌ Pagamento — fica pra PR3
- ❌ Products — fica pra PR4
- ❌ Excel — fica pra PR4+
- ❌ Mexer no Establishment (já mergeado)
- ❌ Mexer em quiz dos 5 capítulos
