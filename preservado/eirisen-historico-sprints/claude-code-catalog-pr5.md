# PR5 — Services + Excel (Sprint Catalog Onda 2)

> **Primeiro PR da Onda 2.** Reusa toda a infra de Excel do PR4. 2ª caixa multi_item — força a extração natural do `<MultiItemListEditor>` genérico.
>
> Estimativa: ~1 dia.
> Branch: `catalog-pr5-services-excel`

---

## Contexto

Onda 1 fechada (5 entregas). Infra de Excel pronta:
- ✅ `download-box-template` genérica por boxType
- ✅ `import-box-excel` valida tamanho via `system_config`
- ✅ Modal Products tem 2 modos (Manual + Excel)
- ✅ `<ProductsItemEditor>` cards colapsáveis com accordions
- ✅ `system_config.excel_max_mb_services = 5MB` já seedado no SUF16

PR5 é o **primeiro PR da Onda 2** e o primeiro a reusar essa infra. Ele força refator natural:

> **`<ProductsItemEditor>` vira `<MultiItemListEditor>` genérico** que serve Products + Services + (futuro) Delivery Items + Events.

Code já mencionou que vai fazer essa extração no PR5. **Importante**: não força arquitetura nova de zero — extrai do que já tá funcionando em Products.

---

## Schema final Services (20 campos)

Confirmado em `/mnt/user-data/outputs/00-CAIXAS-ESTRUTURA-FINAL.md`. Apenas Nome obrigatório.

| Bloco | Campo | Tipo |
|---|---|---|
| **1. Identificação** | name | text ✅ |
| | category | text |
| | description | textarea |
| | aliases | csv (apelidos pro fuzzy match) |
| **2. Preço** | price | number |
| | discount_price | number |
| | discount_condition | text |
| | unit | text (sessão/hora/m²/etc) |
| | accepts_quote | single_choice (Sim/Não/Sob consulta) |
| **3. Tempo** | duration_minutes | number |
| | requires_appointment | boolean |
| | min_advance_notice | text (ex: "24h", "3 dias") |
| **4. Profissional** | responsible_professional | text (link futuro com Team) |
| | required_specialty | text |
| **5. Disponibilidade** | available | single_choice (Sim/Não/Sazonal) |
| | weekdays | csv (segunda, terça, etc) |
| **6. Direcionamento IA** | trigger_keywords | csv |
| | requirements | textarea |
| | dont_offer_when | textarea |
| | ai_notes | textarea |

**6 blocos, 20 campos.** Estrutura cobre: clínica, salão, oficina, estúdio, jurídico, etc.

---

## Etapa 1 — Confirmações antes de codar

### A. Schema atual de Services

```bash
grep -n "ServicesSchema\|formatServices\|CatalogItemSchema" \
  src/features/ai-settings/lib/personaBoxSchemas.ts \
  supabase/functions/_shared/persona-compiler.ts
```

Reportar:
- Schema Zod atual de Services (copia literal)
- Confirma que **ainda usa `CatalogItemSchema` legacy** (compartilhado com Delivery)
- Como `formatServices` é implementado hoje
- Sample real (se algum tenant tem services preenchido)

```sql
SELECT 
  COUNT(*) as total_rows,
  COUNT(DISTINCT tenant_id) as tenants,
  AVG(jsonb_array_length(COALESCE(data->'items', '[]'::jsonb)))::int AS avg_items,
  MAX(jsonb_array_length(COALESCE(data->'items', '[]'::jsonb))) AS max_items
FROM persona_boxes
WHERE box_type = 'services' AND is_active = true;
```

### B. UI atual do modal Services

```bash
grep -n "ServicesForm" src/features/ai-settings/components/blocos/forms/
```

Reportar:
- Form atual usa `<CatalogEditor>` compartilhado (igual era Products antes)
- Tem modo "Colar Lista" (parser regex)?

### C. Decisões pendentes

#### C1. Refator do `<MultiItemListEditor>`

PR4 criou `<ProductsItemEditor>` específico. PR5 introduz 2ª caixa multi_item — momento natural pra extrair genérico.

**Recomendação:**
1. Renomear `<ProductsItemEditor>` → `<MultiItemListEditor>` (genérico)
2. Aceita prop `boxType: string` que determina schema (`PRODUCTS_SCHEMA` ou `SERVICES_SCHEMA`)
3. Renderização genérica: card colapsável + accordions de blocks (já tá assim)
4. ProductsForm e ServicesForm viram wrappers de ~12 linhas cada, passando `boxType` correto
5. Lê schema declarativo de `BOX_SCHEMAS` registry

**Code confirma approach ou propõe alternativa?**

#### C2. CatalogItemSchema legacy

Memory item #5 (decisão D6 do PR4): ServiceItemSchema novo, CatalogItemSchema fica legacy.

Após PR5 mergear, **CatalogItemSchema só serve Delivery** (PR9).

#### C3. Excel template — bloco "Direcionamento IA"

Aba do template gera headers a partir de `field.question`. Pra bloco "Direcionamento IA" os headers ficam:

| QUANDO oferecer (palavras-chave) | Pré-requisitos / preparo | NÃO oferecer quando | Observações pra IA |

Headers longos. Vai funcionar mas Excel fica visualmente pesado. **Aceita?** Alternativa: schema declarativo permite `excel_header_short` opcional pra encurtar só no template.

Recomendação: **aceita headers longos por enquanto**. Se ficar problema na prática, adiciona `excel_header_short` em PR futuro.

#### C4. Tool `query_services` — atualizar

Hoje a tool `query_services` (se existe) lê `CatalogItem`. Após PR5, lê `ServiceItem` com 20 campos.

Reportar:
- Tool `query_services` existe hoje? Em `_shared/persona-tools.ts`?
- Se sim, schema de retorno atual (campos)
- Adaptar pra retornar campos novos: `name, category, description, price, discount_price, unit, duration_minutes, requires_appointment, available, requirements`
- `aliases` (csv de apelidos) entra no haystack do fuzzy

Recomendação:
- Mantém `String.includes()` igual `query_products` (sem tsvector)
- Haystack inclui: `name + category + description + aliases + trigger_keywords`
- Retorno expandido pra ~10 campos úteis

#### C5. Compiler `summarizeServices`

Adapta pro novo schema (igual fizemos `summarizeProducts` no PR4). Output esperado:

```
## Serviços disponíveis

Você tem acesso a N serviços. Use a tool `query_services(query)` pra buscar.

Sample (top 5 por relevância): [Serviço 1], [Serviço 2], ...
```

Não despeja schema completo. Tool busca on-demand.

#### C6. DELETE manual

```sql
SELECT box_type, COUNT(*) FROM persona_boxes 
WHERE box_type = 'services' AND is_active = true
GROUP BY box_type;
```

Esperado: alguns tenants em produção. Pedro decide se apaga ou migra.

**Recomendação:** Pedro apaga (são cobaias em blocks). Cliente vai re-cadastrar via Manual ou Excel novo.

---

## Aguarda OK antes de prosseguir.

---

## Etapa 2 — Schema declarativo

Adicionar `SERVICES_SCHEMA` em `_shared/box-schemas.ts`:

```ts
export const SERVICES_SCHEMA: BoxSchemaDef = {
  boxType: "services",
  label: "Serviços",
  cardinality: "multi_item",
  hasExcel: true,
  blocks: [
    {
      title: "Identificação",
      fields: [
        { field: "name", question: "Nome do serviço", type: "text", required: true },
        { field: "category", question: "Categoria", type: "text", helper: "Ex: Estética, Corte, Consulta clínica" },
        { field: "description", question: "Descrição", type: "textarea" },
        { field: "aliases", question: "Apelidos / outras formas de chamar", type: "csv", helper: "Cliente pode pedir o mesmo serviço por nomes diferentes — separe por vírgula" },
      ],
    },
    {
      title: "Preço",
      fields: [
        { field: "price", question: "Preço", type: "number" },
        { field: "discount_price", question: "Preço com desconto", type: "number" },
        { field: "discount_condition", question: "Condição do desconto", type: "text" },
        { field: "unit", question: "Unidade", type: "text", placeholder: "sessão, hora, m², visita" },
        { field: "accepts_quote", question: "Aceita orçamento?", type: "single_choice", options: ["Sim", "Não", "Sob consulta"] },
      ],
    },
    {
      title: "Tempo",
      fields: [
        { field: "duration_minutes", question: "Duração estimada (minutos)", type: "number", helper: "Importante pra agendamento" },
        { field: "requires_appointment", question: "Requer agendamento?", type: "boolean" },
        { field: "min_advance_notice", question: "Antecedência mínima", type: "text", placeholder: "Ex: 24h, 3 dias" },
      ],
    },
    {
      title: "Profissional",
      fields: [
        { field: "responsible_professional", question: "Profissional responsável", type: "text", helper: "Nome de quem está em Team. Em PRs futuros vira link." },
        { field: "required_specialty", question: "Especialidade necessária", type: "text" },
      ],
    },
    {
      title: "Disponibilidade",
      fields: [
        { field: "available", question: "Disponível?", type: "single_choice", options: ["Sim", "Não", "Sazonal"] },
        { field: "weekdays", question: "Dias da semana", type: "csv", helper: "Segunda, terça, quarta — separe por vírgula" },
      ],
    },
    {
      title: "Direcionamento IA",
      fields: [
        { field: "trigger_keywords", question: "Quando oferecer (palavras-chave)", type: "csv", helper: "IA detecta essas palavras na mensagem do cliente" },
        { field: "requirements", question: "Pré-requisitos / preparo", type: "textarea" },
        { field: "dont_offer_when", question: "NÃO oferecer quando", type: "textarea" },
        { field: "ai_notes", question: "Observações pra IA", type: "textarea" },
      ],
    },
  ],
};

// Adicionar ao registry
export const BOX_SCHEMAS: Record<string, BoxSchemaDef> = {
  establishment: ESTABLISHMENT_SCHEMA,
  hours: HOURS_SCHEMA,
  links: LINKS_SCHEMA,
  pagamento: PAYMENT_SCHEMA,
  products: PRODUCTS_SCHEMA,
  services: SERVICES_SCHEMA,  // NOVO
};
```

---

## Etapa 3 — Refator `<MultiItemListEditor>` genérico

### 3a. Renomear

`<ProductsItemEditor>` → `<MultiItemListEditor>`. Move arquivo se preciso.

### 3b. Generalizar

Aceita props:
```ts
interface MultiItemListEditorProps {
  boxType: string;  // "products" ou "services"
  items: any[];
  onChange: (items: any[]) => void;
}
```

Internamente:
- Lê schema de `BOX_SCHEMAS[boxType]`
- Renderiza cards colapsáveis com accordions de blocks
- Cada card mostra `item.name` (campo obrigatório de todo schema multi_item)
- Adiciona/Remove items
- Cada bloco do accordion renderiza com `<QuestionBlock>` por field

### 3c. Wrappers

```tsx
// ProductsForm.tsx (~12 linhas)
export function ProductsForm({ items, onChange, ...rest }: ProductsFormProps) {
  return (
    <BoxFormMultiItem
      boxType="products"
      items={items}
      onChange={onChange}
      // modo Manual + Excel
      modes={["manual", "excel"]}
    />
  );
}

// ServicesForm.tsx (~12 linhas)
export function ServicesForm({ items, onChange, ...rest }: ServicesFormProps) {
  return (
    <BoxFormMultiItem
      boxType="services"
      items={items}
      onChange={onChange}
      modes={["manual", "excel"]}
    />
  );
}
```

`<BoxFormMultiItem>` é o wrapper que orquestra:
- Tabs Manual / Excel
- Modo Manual: usa `<MultiItemListEditor>`
- Modo Excel: botões Baixar / Importar / Mande pra equipe (igual PR4)

---

## Etapa 4 — Tool e compiler

### 4a. Tool `query_services` (`_shared/persona-tools.ts`)

```ts
export async function queryServices(supabase, tenantId, query: string, limit = 10) {
  const { data: box } = await supabase
    .from("persona_boxes")
    .select("data")
    .eq("tenant_id", tenantId)
    .eq("box_type", "services")
    .eq("is_active", true)
    .single();
  
  if (!box?.data?.items) return [];
  
  const items = box.data.items as any[];
  const filtered = filterServices(items, query);
  
  return filtered.slice(0, limit).map(item => ({
    name: item.name,
    category: item.category,
    description: item.description,
    price: item.price,
    discount_price: item.discount_price,
    unit: item.unit,
    duration_minutes: item.duration_minutes,
    requires_appointment: item.requires_appointment,
    available: item.available,
    requirements: item.requirements,
  }));
}

function filterServices(items: any[], query: string): any[] {
  if (!query) return items;
  const q = query.toLowerCase();
  return items.filter(item => {
    const haystack = [
      item.name,
      item.category,
      item.description,
      ...(item.aliases || []),
      ...(item.trigger_keywords || []),
    ].filter(Boolean).join(" ").toLowerCase();
    return haystack.includes(q);
  });
}
```

### 4b. Compiler `summarizeServices`

```ts
function summarizeServices(box: PersonaBox | null): string {
  if (!box || !box.data?.items?.length) return "";
  
  const items = box.data.items;
  const sample = items.slice(0, 5).map(i => i.name).join(", ");
  
  return `## Serviços disponíveis

Você tem acesso a ${items.length} serviços cadastrados. Use a tool \`query_services(query)\` pra buscar.

${items.length > 0 ? `Exemplos: ${sample}` : ""}`;
}
```

---

## Etapa 5 — Excel template + import

### Não precisa criar edges novas

Edge `download-box-template` (PR4) já é genérica. Aceita `?boxType=services`. Usa `BOX_SCHEMAS[boxType]` pra gerar headers e exemplos.

Edge `import-box-excel` (PR4) também é genérica. Recebe `boxType: "services"` no FormData.

**Mas:** verificar que os geradores de exemplos funcionam pra Services. Se PR4 deixou exemplos hardcoded só pra products no `generateExamples(boxType)`, adicionar 2 exemplos de services no switch:

```ts
function generateExamples(boxType: string): any[][] {
  if (boxType === "products") {
    return [/* PR4 já tem */];
  }
  if (boxType === "services") {
    return [
      ["Corte de cabelo masculino", "Corte", "Corte tradicional, máquina e tesoura", "tradicional, social", 30, 25, "Toda terça", "sessão", "Sim", 30, true, "24h", "João", "Barbeiro", "Sim", "segunda, terça, quarta, quinta, sexta, sábado", "corte, cabelo, masculino, social", "Vir com cabelo lavado", "", ""],
      ["Limpeza de pele", "Estética facial", "Limpeza profunda + extração", "facial, peeling", 120, 0, "", "sessão", "Não", 60, true, "48h", "Maria", "Esteticista", "Sim", "segunda, quarta, sexta", "limpeza, pele, peeling, extração", "Sem maquiagem nas 24h anteriores", "Acne ativa - encaminhar pro derma", "Sempre confirmar prazo de cicatrização"],
    ];
  }
  return [];
}
```

---

## Etapa 6 — Cleanup + deploy

### Antes do deploy

```sql
-- Confirma volume
SELECT box_type, COUNT(*), 
       AVG(jsonb_array_length(COALESCE(data->'items', '[]'::jsonb)))::int AS avg_items
FROM persona_boxes WHERE box_type = 'services' AND is_active = true
GROUP BY box_type;

-- DELETE
DELETE FROM persona_boxes WHERE box_type = 'services';
```

### Deploy

```bash
gh pr merge <PR> --squash --delete-branch
git checkout main && git pull origin main
supabase functions deploy ai-reply  # tool query_services + compiler novo
git push origin main                 # Lovable build
```

Não precisa redeployar `download-box-template` nem `import-box-excel` — são genéricas e leem o registry.

### Validação pós-deploy

1. Card Services aparece com label "Serviços"
2. Modo Manual: adicionar 1 serviço, verificar 6 blocos visíveis
3. Modo Excel: baixar modelo, abrir XLSX, conferir 20 colunas + 2 exemplos
4. Modo Excel: subir Excel com 5 serviços, confirmar toast e persistência
5. Confirmar Products continua funcionando (não regressão)

---

## Critérios de aceite

- [ ] Etapa 1 confirmação aprovada
- [ ] SERVICES_SCHEMA em box-schemas.ts (20 campos, 6 blocos)
- [ ] `<MultiItemListEditor>` genérico extraído de `<ProductsItemEditor>`
- [ ] ProductsForm e ServicesForm wrappers de ~12 linhas
- [ ] `query_services` tool com fuzzy haystack (name+category+description+aliases+trigger_keywords)
- [ ] `summarizeServices` no compiler (count + sample, não despeja items)
- [ ] Excel template gera headers Services
- [ ] Excel import aceita Services
- [ ] Build/tsc/vitest verde
- [ ] Pedro confirma DELETE rodado
- [ ] PR description anota: "Inicia Onda 2. Extrai MultiItemListEditor genérico."

---

## Restrições

- ❌ Sem refator de `<CatalogEditor>` legacy (continua servindo Delivery até PR9)
- ❌ Sem mexer em outras caixas
- ❌ Sem mexer em Products comportamentalmente (só refator de naming)
- ✅ Pode renomear arquivos/componentes pra ficar genérico
- ✅ Mostrar diff antes do commit
- ✅ Branch: `catalog-pr5-services-excel`
- ✅ PR título: `feat(catalog): Services + Excel + MultiItemListEditor genérico (PR5)`

---

## Pós-merge — Próximo: PR6 (FAQ + Objections)

PR6 mergeia FAQ + Objections juntos (estruturas idênticas, decisão Pedro 10/05/26 — memory item #21).

Reusa toda a infra:
- `<MultiItemListEditor>` (refatorada nesse PR)
- Edge generator + import
- Excel templates

---

## O que NÃO fazer neste PR

- ❌ FAQ, Objections, Team, Forwards, Delivery, Events, Custom (Onda 2 sequencial)
- ❌ Mexer em master prompt além do necessário pra `query_services`
- ❌ Sprint Templates por Nicho
- ❌ Sprint Arquétipos
