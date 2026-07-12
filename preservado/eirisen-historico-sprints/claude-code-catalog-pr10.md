# PR10 — Events + Matriz 2D (Sprint Catalog Onda 2)

> **Maior PR funcional da Onda 2.** Caixa Events com **matriz 2D** (perguntas em linhas, pacotes em colunas). Arquitetura nova — cardinality `matrix`, componente `<MatrixEditor>`, Excel pivotado.
>
> Estimativa: ~2 dias.
> Branch: `catalog-pr10-events-matrix`

---

## Contexto

Eventos da vida real têm **variação de preço por condição** — não cabe em multi-item plano:

| Aspecto | Festa Casamento | Festa Aniversário | Workshop |
|---|---|---|---|
| Capacidade max | 300 | 150 | 60 |
| Cozinha | Equipada | Sim | Não |
| Preço diurno | 5000 | 2500 | 500 |
| Preço noturno | 8000 | 3500 | 700 |
| Preço fim de semana | 10000 | 4500 | 900 |

Cliente compara pacotes lado a lado. Pra modelar isso:
- **Linhas fixas** = perguntas do schema (~57 campos em 10 accordions)
- **Colunas dinâmicas** = pacotes que tenant define
- **Células** = valores

Estrutura de matriz reflete tabela de preços que cliente já usa em PDF/Excel.

---

## Schema final Events (~57 campos / 10 accordions)

| # | Accordion | Campos |
|---|---|---|
| 1 | Identificação | type, description, aliases (3 campos — nome do pacote vai no header da coluna, não como campo) |
| 2 | Capacidade | min_capacity, max_capacity, layout, area_m2 (4) |
| 3 | Estrutura | parking, parking_spots, accessibility, bathrooms, wifi, kitchen (6) |
| 4 | Equipamentos | sound_included, projector, microphone, tables_included, chairs_included, dishware, other_equipment (7) |
| 5 | **Preço (expandido)** | price_base, price_diurno, price_noturno, price_madrugada, price_seg_qui, price_sex_dom, price_feriado, price_temporada_alta, price_temporada_baixa, hour_extra, included, extras (12) |
| 6 | Logística | usage_hours, sound_limit, prev_day_setup, prev_day_cost, prev_day_entry (5) |
| 7 | Regras | wall_decoration, third_party_suppliers, security_required, insurance_included (4) |
| 8 | Cancelamento | has_formal_policy, cancel_advance_days, cancel_penalty, rescheduling, rescheduling_terms (5) |
| 9 | Contrato | has_formal_contract, contract_delivery (2) |
| 10 | Direcionamento IA | trigger_keywords, ai_can_confirm, ai_can_pass_value, responsible, backup, ai_notes (6) |

**Total: ~57 campos.** Apenas `name` (header da coluna) é obrigatório.

---

## Modelo de dados — cardinality `matrix`

Storage estruturado:

```ts
data: {
  packages: [
    {
      name: "Festa Casamento",     // header da coluna (obrigatório)
      values: {
        type: "Festa",
        description: "Casamento completo com decoração e serviço",
        max_capacity: 300,
        price_base: 5000,
        price_sex_dom: 8000,
        price_feriado: 10000,
        kitchen: "Equipada",
        // ... outras keys das 57 perguntas
      }
    },
    {
      name: "Workshop",
      values: { /* ... */ }
    }
  ]
}
```

Diferente de multi_item (`{ items: [...] }`). Cada package é objeto com `name + values`.

---

## Etapa 1 — Confirmações antes de codar

### A. Schema atual de Events

```bash
grep -n "EventsSchema\|formatEvents" \
  src/features/ai-settings/lib/personaBoxSchemas.ts \
  supabase/functions/_shared/persona-compiler.ts
```

Reportar:
- Schema Zod atual (copia literal)
- Estrutura legada do data
- Compiler atual

### B. Volume real

```sql
SELECT 
  tenant_id,
  jsonb_typeof(data) AS data_type,
  data
FROM persona_boxes
WHERE box_type = 'events' AND is_active = true
LIMIT 5;
```

Reportar amostras.

### C. Decisões pendentes

#### C1. Cardinality `matrix` — adicionar ao enum

Hoje BoxSchemaDef.cardinality é `"singleton" | "multi_item" | "multi_row"` (PR1). Adicionar `"matrix"`.

Confirmar approach.

#### C2. Componente novo `<MatrixEditor>`

Componente dedicado a Events. Não usa `<MultiItemListEditor>` (esse é pra cardinality `multi_item`).

Estrutura proposta:

```tsx
<MatrixEditor
  schema={EVENTS_SCHEMA}
  packages={data.packages}
  onChange={(packages) => ...}
/>
```

UI:
```
┌───────────────────────┬─────────────────┬───────────────┬──────┐
│ Pergunta              │ Festa Casamento │ Workshop  [✏️ X] │ + Pacote │
├───────────────────────┼─────────────────┼───────────────┼──────┤
│ ▼ Identificação       │                 │                │      │
│   Tipo                │ [Festa ▼]       │ [Workshop ▼]   │      │
│   Descrição           │ [textarea]      │ [textarea]     │      │
│   Apelidos            │ [csv]           │ [csv]          │      │
├───────────────────────┼─────────────────┼───────────────┼──────┤
│ ▼ Capacidade          │                 │                │      │
│   Mínimo de pessoas   │ [50    ]        │ [10    ]       │      │
│   Máximo de pessoas   │ [300   ]        │ [60    ]       │      │
│ ...                   │                 │                │      │
└───────────────────────┴─────────────────┴───────────────┴──────┘
```

- Linhas agrupadas em **accordions** (10 grupos)
- Header das colunas: nome do pacote editável (✏️) + botão remover (X)
- Botão "+ Pacote" no fim das colunas → coluna nova com nome editável
- Cada célula renderiza input apropriado pelo tipo do field
- Validação: `name` da coluna obrigatório, demais opcionais

Componente reusável? **Não.** É específico de matrix. Se outras caixas matrix surgirem (não tem no roadmap), aí extrai genérico. Por enquanto fica `<MatrixEditor>` em `events/`.

#### C3. Excel pivotado — formato exato

```
A1: (vazio)        | B1: Festa Casamento | C1: Workshop  | D1: Auditório
A2: ▼ Identificação                                                       
A3: Tipo            | B3: Festa            | C3: Workshop  | D3: Locação
A4: Descrição       | B4: ...              | C4: ...       | D4: ...
A5: Apelidos        | B5: casamento, ...   | C5: ...       | D5: ...
A6: ▼ Capacidade
A7: Mínimo          | B7: 50               | C7: 10        | D7: 30
A8: Máximo          | B8: 300              | C8: 60        | D8: 200
...
```

- **Linha 1:** nomes dos pacotes (headers de coluna)
- **Linhas 2+:** perguntas + valores
- Linhas separadoras com nome do accordion (sem valor) — Excel ignora, mas ajuda visualmente
- Cliente pode adicionar coluna nova facilmente (escreve nome no header + valores nas células)

Aba 2: Instruções com explicação de como preencher.

#### C4. Tool `query_events`

Volume típico: 3-15 pacotes. Sempre cabe.

**Opções:**
- **A — Sem tool:** compiler despeja resumo + tool ref (igual FAQ/Objections)
- **B — Com tool:** IA chama `query_events(query)` que retorna pacote(s) match

**Recomendação: B.** Cliente faz perguntas naturais ("preço da festa de aniversário no sábado?"). Tool retorna o pacote cheio com todos os campos.

Haystack: `name + type + description + aliases + trigger_keywords`

Retorno: package completo (name + values). IA monta resposta pegando os campos relevantes.

#### C5. Compiler `summarizeEvents`

```ts
function summarizeEvents(box): string {
  if (!box?.data?.packages?.length) return "";
  
  const packages = box.data.packages;
  const sample = packages.slice(0, 5).map((p: any) => {
    const type = p.values?.type;
    const max = p.values?.max_capacity;
    const desc = type && max ? `${type}, até ${max} pessoas` : (type || "");
    return desc ? `${p.name} (${desc})` : p.name;
  }).join(", ");
  
  return `## Pacotes de eventos

Você tem ${packages.length} pacotes cadastrados. Use \`query_events(query)\` pra buscar detalhes (preço, capacidade, equipamentos).

Pacotes: ${sample}`;
}
```

#### C6. UI — botões de coluna

- **+ Pacote** → coluna nova com prompt pra digitar nome
- **✏️ no header** → renomeia pacote (input inline)
- **X no header** → confirma remover + apaga coluna inteira do data

#### C7. Validação no save

`name` obrigatório em cada package. Toast bloqueia se algum sem nome.

#### C8. Volume de campos no Excel

57 perguntas × N pacotes. Pra 5 pacotes = 285 células. Cliente vê tabela grande mas plana — não é problema técnico.

#### C9. DELETE manual

```sql
DELETE FROM persona_boxes WHERE box_type = 'events';
```

#### C10. Migration enum

Não precisa. `events` já existe no enum legacy.

---

## Aguarda OK antes de prosseguir.

---

## Etapa 2 — Tipos novos

### Adicionar `matrix` em cardinality

```ts
// box-schemas.ts
export type BoxCardinality = "singleton" | "multi_item" | "multi_row" | "matrix";

export interface BoxSchemaDef {
  // ...
  cardinality: BoxCardinality;
}
```

### Schema declarativo

```ts
export const EVENTS_SCHEMA: BoxSchemaDef = {
  boxType: "events",
  label: "Pacotes de eventos",
  cardinality: "matrix",  // NOVA
  hasExcel: true,
  blocks: [
    {
      title: "Identificação",
      fields: [
        { field: "type", question: "Tipo", type: "single_choice", options: ["Festa", "Locação espaço", "Workshop", "Reunião", "Outro"] },
        { field: "description", question: "Descrição", type: "textarea" },
        { field: "aliases", question: "Apelidos / como cliente chama", type: "csv" },
      ],
    },
    {
      title: "Capacidade",
      fields: [
        { field: "min_capacity", question: "Mínimo de pessoas", type: "number" },
        { field: "max_capacity", question: "Máximo de pessoas", type: "number" },
        { field: "layout", question: "Layout do espaço", type: "text", helper: "Ex: Auditório, U, Mesas redondas" },
        { field: "area_m2", question: "Espaço (m²)", type: "number" },
      ],
    },
    {
      title: "Estrutura",
      fields: [
        { field: "parking", question: "Estacionamento?", type: "single_choice", options: ["Sim", "Não", "Pago", "Gratuito"] },
        { field: "parking_spots", question: "Vagas de estacionamento", type: "number" },
        { field: "accessibility", question: "Acessibilidade PCD", type: "single_choice", options: ["Sim", "Não", "Parcial"] },
        { field: "bathrooms", question: "Banheiros (qtd)", type: "number" },
        { field: "wifi", question: "WiFi", type: "boolean" },
        { field: "kitchen", question: "Cozinha disponível", type: "single_choice", options: ["Sim", "Não", "Equipada"] },
      ],
    },
    {
      title: "Equipamentos",
      fields: [
        { field: "sound_included", question: "Som incluso", type: "single_choice", options: ["Sim", "Não", "Sob aluguel"] },
        { field: "projector", question: "Projetor/TV", type: "single_choice", options: ["Sim", "Não", "Sob aluguel"] },
        { field: "microphone", question: "Microfone", type: "single_choice", options: ["Sim", "Não", "Sob aluguel"] },
        { field: "tables_included", question: "Mesas inclusas (qtd)", type: "number" },
        { field: "chairs_included", question: "Cadeiras inclusas (qtd)", type: "number" },
        { field: "dishware", question: "Louça/talher/copos", type: "single_choice", options: ["Sim", "Não", "Sob aluguel"] },
        { field: "other_equipment", question: "Outros equipamentos extras", type: "textarea" },
      ],
    },
    {
      title: "Preço",
      fields: [
        { field: "price_base", question: "Preço base/padrão", type: "number" },
        { field: "price_diurno", question: "Preço diurno (8h-18h)", type: "number" },
        { field: "price_noturno", question: "Preço noturno (18h-2h)", type: "number" },
        { field: "price_madrugada", question: "Preço madrugada (após 2h)", type: "number" },
        { field: "price_seg_qui", question: "Preço seg-qui", type: "number" },
        { field: "price_sex_dom", question: "Preço sex-dom", type: "number" },
        { field: "price_feriado", question: "Preço feriado", type: "number" },
        { field: "price_temporada_alta", question: "Preço temporada alta", type: "number" },
        { field: "price_temporada_baixa", question: "Preço temporada baixa", type: "number" },
        { field: "hour_extra", question: "Preço por hora extra", type: "number" },
        { field: "included", question: "O que está incluso no preço", type: "textarea" },
        { field: "extras", question: "O que é extra (com valores)", type: "textarea" },
      ],
    },
    {
      title: "Logística",
      fields: [
        { field: "usage_hours", question: "Horário de uso (das X às Y)", type: "text" },
        { field: "sound_limit", question: "Limite de som (horário/decibéis)", type: "text" },
        { field: "prev_day_setup", question: "Montagem dia anterior permitida?", type: "single_choice", options: ["Sim", "Não", "Depende"] },
        { field: "prev_day_cost", question: "Custo da montagem dia anterior", type: "number" },
        { field: "prev_day_entry", question: "Horário pra entrar dia anterior", type: "text" },
      ],
    },
    {
      title: "Regras de uso",
      fields: [
        { field: "wall_decoration", question: "Decoração na parede", type: "single_choice", options: ["Sim", "Não", "Com adesivo específico"] },
        { field: "third_party_suppliers", question: "Fornecedores terceiros liberados?", type: "single_choice", options: ["Sim", "Não", "Com aviso"] },
        { field: "security_required", question: "Segurança obrigatória?", type: "single_choice", options: ["Sim", "Não", "Por conta do cliente"] },
        { field: "insurance_included", question: "Seguro do espaço incluso?", type: "boolean" },
      ],
    },
    {
      title: "Cancelamento",
      fields: [
        { field: "has_formal_policy", question: "Tem política formal", type: "boolean" },
        { field: "cancel_advance_days", question: "Antecedência sem multa (dias)", type: "number" },
        { field: "cancel_penalty", question: "Multa em cima da hora", type: "text" },
        { field: "rescheduling", question: "Reagendamento permitido", type: "single_choice", options: ["Sim", "Não", "Com taxa"] },
        { field: "rescheduling_terms", question: "Condições do reagendamento", type: "textarea" },
      ],
    },
    {
      title: "Contrato",
      fields: [
        { field: "has_formal_contract", question: "Tem contrato formal", type: "boolean" },
        { field: "contract_delivery", question: "Como envia", type: "single_choice", options: ["WhatsApp", "Email", "Presencial"] },
      ],
    },
    {
      title: "Direcionamento IA",
      fields: [
        { field: "trigger_keywords", question: "Quando oferecer (palavras-chave)", type: "csv" },
        { field: "ai_can_confirm", question: "IA pode confirmar disponibilidade?", type: "single_choice", options: ["Sim", "Confirmar", "Não"] },
        { field: "ai_can_pass_value", question: "IA pode passar valor sem confirmar?", type: "single_choice", options: ["Sim", "Confirmar", "Não"] },
        { field: "responsible", question: "Profissional responsável", type: "text" },
        { field: "backup", question: "Backup se responsável tá fora", type: "text" },
        { field: "ai_notes", question: "Observações pra IA", type: "textarea" },
      ],
    },
  ],
};

// Adicionar ao registry
export const BOX_SCHEMAS: Record<string, BoxSchemaDef> = {
  // ... anteriores
  events: EVENTS_SCHEMA,  // NOVO ou substituindo legacy
};
```

### Zod schema

```ts
export const EventPackageSchema = z.object({
  name: z.string().min(1, "Nome do pacote obrigatório"),
  values: z.record(z.any()).default({}),
});

export const EventsSchema = z.object({
  packages: z.array(EventPackageSchema).default([]),
});
```

---

## Etapa 3 — Componente `<MatrixEditor>`

Caminho: `src/features/ai-settings/components/blocos/MatrixEditor.tsx`

Props:
```ts
interface MatrixEditorProps {
  schema: BoxSchemaDef;
  packages: { name: string; values: Record<string, any> }[];
  onChange: (packages: any[]) => void;
}
```

Estrutura interna:
```tsx
<div>
  {/* Header */}
  <div className="grid">
    <div className="col-pergunta">Pergunta</div>
    {packages.map((pkg, i) => (
      <PackageHeader 
        key={i}
        name={pkg.name}
        onRename={(newName) => updatePackageName(i, newName)}
        onRemove={() => removePackage(i)}
      />
    ))}
    <Button onClick={addPackage}>+ Pacote</Button>
  </div>
  
  {/* Linhas agrupadas por accordion */}
  {schema.blocks.map((block) => (
    <Accordion key={block.title} title={block.title}>
      {block.fields.map((field) => (
        <MatrixRow
          key={field.field}
          field={field}
          packages={packages}
          onChange={(pkgIndex, value) => updateValue(pkgIndex, field.field, value)}
        />
      ))}
    </Accordion>
  ))}
</div>
```

`<MatrixRow>` renderiza:
- 1ª coluna: pergunta + helper
- N colunas: 1 célula por package, input apropriado pelo `field.type`

`<PackageHeader>` renderiza:
- Nome editável inline (clique pra editar)
- Botão "X" pra remover (com confirmação)

---

## Etapa 4 — `<BoxFormMatrix>` orquestrador

Caminho: `src/features/ai-settings/components/blocos/BoxFormMatrix.tsx`

Similar ao `<BoxFormMultiItem>` mas usa `<MatrixEditor>` no modo Manual.

```tsx
export function BoxFormMatrix({ boxType, modes }: Props) {
  const [activeMode, setActiveMode] = useState<"manual" | "excel">("manual");
  const { data: box, mutate } = useBox(boxType);
  
  return (
    <>
      <Tabs>
        {modes.includes("manual") && <Tab>Manual</Tab>}
        {modes.includes("excel") && <Tab>Excel</Tab>}
      </Tabs>
      
      {activeMode === "manual" && (
        <MatrixEditor
          schema={BOX_SCHEMAS[boxType]}
          packages={box?.data?.packages ?? []}
          onChange={(packages) => mutate({ packages })}
        />
      )}
      
      {activeMode === "excel" && (
        <ExcelMode boxType={boxType} />
      )}
    </>
  );
}
```

### EventsForm wrapper

```tsx
export function EventsForm() {
  return <BoxFormMatrix boxType="events" modes={["manual", "excel"]} />;
}
```

Adicionar entries em `AbaBlocos.tsx` e `EditBoxDialog.tsx`.

---

## Etapa 5 — Tool e compiler

### Tool `query_events`

```ts
export async function queryEvents(supabase, tenantId, query: string, limit = 5) {
  const { data: box } = await supabase
    .from("persona_boxes")
    .select("data")
    .eq("tenant_id", tenantId)
    .eq("box_type", "events")
    .eq("is_active", true)
    .single();
  
  if (!box?.data?.packages) return [];
  
  const packages = box.data.packages as any[];
  const filtered = filterEvents(packages, query);
  
  return filtered.slice(0, limit).map(pkg => ({
    name: pkg.name,
    ...pkg.values,  // despeja todos os values
  }));
}

function filterEvents(packages: any[], query: string): any[] {
  if (!query) return packages;
  const q = query.toLowerCase();
  return packages.filter(pkg => {
    const haystack = [
      pkg.name,
      pkg.values?.type,
      pkg.values?.description,
      ...(pkg.values?.aliases || []),
      ...(pkg.values?.trigger_keywords || []),
    ].filter(Boolean).join(" ").toLowerCase();
    return haystack.includes(q);
  });
}
```

Registrar em `BOX_TO_TOOL_MAP`.

### Compiler

```ts
function summarizeEvents(box): string {
  if (!box?.data?.packages?.length) return "";
  
  const packages = box.data.packages;
  const sample = packages.slice(0, 5).map((p: any) => {
    const type = p.values?.type;
    const max = p.values?.max_capacity;
    const desc = type && max ? `${type}, até ${max} pessoas` : (type || "");
    return desc ? `${p.name} (${desc})` : p.name;
  }).join(", ");
  
  return `## Pacotes de eventos

Você tem ${packages.length} pacotes cadastrados. Use \`query_events(query)\` pra buscar detalhes (preço, capacidade, equipamentos).

Pacotes: ${sample}`;
}
```

---

## Etapa 6 — Excel template + import

### download-box-template — formato pivotado pra matrix

Edge precisa lógica especial pra cardinality matrix:

```ts
if (schema.cardinality === "matrix") {
  return generateMatrixTemplate(schema);
}
```

`generateMatrixTemplate`:
- Aba "Eventos":
  - **Linha 1:** vazia (col A) + nomes de pacotes exemplo (col B+: "Festa Casamento", "Workshop")
  - **Linhas 2+:** perguntas em col A + valores exemplo em col B+
  - Agrupamento visual: linha "▼ Identificação" antes das perguntas do bloco (sem valor)

```ts
function generateMatrixTemplate(schema: BoxSchemaDef): string[][] {
  const exampleNames = ["Festa Casamento", "Workshop"];
  
  // Linha 1: headers de pacote
  const rows: string[][] = [["", ...exampleNames]];
  
  // Linhas 2+: perguntas + valores exemplo
  for (const block of schema.blocks) {
    rows.push([`▼ ${block.title}`, "", ""]);
    for (const field of block.fields) {
      const exampleValues = generateExampleValuesForField(field);
      rows.push([field.question, ...exampleValues]);
    }
  }
  
  return rows;
}

function generateExampleValuesForField(field: BoxField): string[] {
  // Retorna 2 valores exemplo (1 por pacote exemplo)
  // Festa Casamento + Workshop com valores plausíveis pra cada field
}
```

### import-box-excel — parser pivotado

Detectar cardinality matrix → parsing diferente:

```ts
if (schema.cardinality === "matrix") {
  // Linha 1: nomes dos pacotes (col B+)
  // Linhas 2+: perguntas (col A) + valores (col B+)
  
  const headerRow = rows[0];
  const packageNames = headerRow.slice(1).filter(name => name?.trim());
  
  const packages = packageNames.map((name, colIdx) => ({
    name,
    values: {} as Record<string, any>,
  }));
  
  // Pular linhas de "▼ Accordion" (separadores)
  for (const row of rows.slice(1)) {
    if (row[0]?.startsWith("▼")) continue;
    
    const question = row[0]?.trim();
    if (!question) continue;
    
    // Achar field pelo question literal
    const field = findFieldByQuestion(schema, question);
    if (!field) continue;
    
    // Atribuir valor pra cada package
    for (let pkgIdx = 0; pkgIdx < packageNames.length; pkgIdx++) {
      const value = row[pkgIdx + 1];
      if (value !== undefined && value !== null && value !== "") {
        packages[pkgIdx].values[field.field] = parseValue(value, field.type);
      }
    }
  }
  
  return { packages };
}
```

### Validação na importação

- `name` (header) obrigatório em cada coluna
- Linhas com pergunta desconhecida = ignoradas (com warning no log)

---

## Etapa 7 — Cleanup + deploy

### Antes do deploy

**1) Volume:**
```sql
SELECT 
  tenant_id,
  data
FROM persona_boxes
WHERE box_type = 'events' AND is_active = true;
```

**2) DELETE legacy:**
```sql
DELETE FROM persona_boxes WHERE box_type = 'events';
```

**3) Confirma:**
```sql
SELECT COUNT(*) FROM persona_boxes WHERE box_type = 'events';
```

### Deploy

```bash
gh pr merge <PR> --squash --delete-branch
git checkout main && git pull origin main
supabase functions deploy ai-reply
supabase functions deploy download-box-template
supabase functions deploy import-box-excel
git push origin main
```

3 edges deployadas (template e import precisam mudança pra matrix).

### Validação pós-deploy

1. Card "Pacotes de eventos" na seção O QUE OFERECE
2. Modo Manual: tabela vazia com botão "+ Pacote"
3. Adiciona 2 pacotes ("Festa Casamento", "Workshop"), preenche algumas células
4. Salva, recarrega, persiste
5. Modo Excel: baixa modelo, abre XLSX, vê:
   - Aba 1 com formato pivotado, 2 colunas exemplo + 57 linhas de perguntas
   - Aba 2 Instruções
6. Edita XLSX, adiciona 1 pacote (3ª coluna), preenche valores
7. Sobe Excel → toast "3 pacotes importados"
8. **Não-regressão:** Products, Services, FAQ, Objections, Team, Forwards, Delivery continuam OK

---

## Critérios de aceite

- [ ] Etapa 1 confirmação aprovada
- [ ] Cardinality `matrix` adicionada
- [ ] EVENTS_SCHEMA com ~57 campos / 10 accordions
- [ ] EventsSchema Zod novo (packages array)
- [ ] `<MatrixEditor>` componente novo (linhas + colunas + add/remove pacote)
- [ ] `<BoxFormMatrix>` orquestrador
- [ ] EventsForm wrapper ~12 linhas
- [ ] Tool query_events com fuzzy haystack 5 fontes
- [ ] summarizeEvents (count + sample com type/max_capacity)
- [ ] Edge download-box-template suporta matrix (template pivotado)
- [ ] Edge import-box-excel suporta matrix (parser pivotado)
- [ ] Build/tsc/vitest verde
- [ ] Pedro confirma DELETE
- [ ] PR description anota: "PR10 introduz cardinality matrix. Componente novo dedicado a Events."

---

## Restrições

- ❌ Sem aplicar matrix em outras caixas (só Events)
- ❌ Sem mexer em outras caixas
- ❌ Sem cross-field validation
- ❌ Sem reservas/agendamentos (Sprint Schedule futura)
- ✅ Mostra diff antes do commit
- ✅ Branch: `catalog-pr10-events-matrix`
- ✅ PR título: `feat(catalog): Events + matriz 2D (PR10)`

---

## Pós-merge — Próximo: PR11 (Custom)

PR11 é o **último** da Onda 2. Custom é caixa "lixo" — texto livre que cliente usa pra coisas que não cabem em outras caixas.

Schema: simples (1 array de `{title, content}`). Cardinality: `multi_row` (já existe). Sem Excel (texto livre).

Estimativa: ~3-4h.

Após PR11, **Sprint Catalog COMPLETA**. 11 PRs totais (4 Onda 1 + 7 Onda 2).

---

## O que NÃO fazer neste PR

- ❌ Custom (PR11)
- ❌ Matrix em outras caixas
- ❌ Reservas/agendamentos
- ❌ Templates por nicho
- ❌ Sprint Arquétipos
