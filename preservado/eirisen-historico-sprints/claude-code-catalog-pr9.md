# PR9 — Delivery (3 caixas) + Excel (Sprint Catalog Onda 2)

> **Maior PR da Onda 2.** 3 caixas em 1 PR: Delivery Items, Delivery Areas, Delivery Config. Substitui caixa "delivery" legada que tinha tudo junto.
>
> Estimativa: ~6-8h.
> Branch: `catalog-pr9-delivery`

---

## Contexto

Memory item #14: caixa `delivery` legada será dividida em 3:

1. **Delivery Items** — multi-item, Excel. Schema idêntico a Products. Cardápio específico de delivery.
2. **Delivery Areas** — multi-item, Excel. Bairros/CEPs/taxas/tempos atendidos.
3. **Delivery Config** — singleton, perguntas. Pedido mínimo, horário delivery, políticas.

**Fallback inteligente Delivery Items** (memory item #16, SUF15 já preparou):
- **Vazia** → IA usa Products filtrado por `available_for_delivery=true`
- **Preenchida** → IA usa Delivery Items
- **Ambas** → prioridade Delivery Items (mais específico)

**Casos de uso real:**
- Restaurante com cardápio principal igual ao delivery → não preenche Delivery Items, usa Products
- Restaurante com cardápio reduzido pra delivery → preenche Delivery Items
- Loja vende A no balcão e B pra delivery → preenche Delivery Items separado

---

## Schemas finais

### 7. Delivery Items (multi-item, Excel)

**Schema idêntico a Products** (17 campos / 5 blocos). Reusa `PRODUCTS_SCHEMA` mas com `boxType: "delivery_items"`.

Por que reusar:
- 99% dos casos compartilha estrutura (nome, preço, categoria, descrição, etc)
- Cliente que tem produtos pode copiar/colar
- Excel template idêntico (cliente já conhece)
- Tool retorna mesmos campos

### 8. Delivery Areas (multi-item, Excel) — 10 campos / 3 blocos

| Bloco | Campo | Tipo |
|---|---|---|
| **Localidade** | neighborhood | text ✅ |
| | city | text |
| | zip_start | text |
| | zip_end | text |
| **Logística** | delivery_fee | number |
| | estimated_time_minutes | number |
| | minimum_order | number |
| | max_distance_km | text |
| **Direcionamento IA** | restrictions | single_choice (Atende/Não atende/Sob consulta) |
| | ai_notes | textarea |

### 9. Delivery Config (singleton, perguntas) — 11 campos / 3 blocos

| Bloco | Campo | Tipo |
|---|---|---|
| **Operação** | global_minimum_order | number |
| | service_fee_percent | number |
| | delivery_hours | textarea |
| | average_time_fallback | text |
| | accepted_payment_methods | csv |
| **Política** | cancellation_policy | textarea |
| | damaged_product_policy | textarea |
| | delay_policy | textarea |
| **Direcionamento IA** | order_status_protocol | textarea |
| | escalation_rule | textarea (ex: "atraso > 30min") |
| | ai_notes | textarea |

---

## Etapa 1 — Confirmações antes de codar

### A. Schema atual da caixa `delivery` legada

```bash
grep -n "DeliverySchema\|formatDelivery" \
  src/features/ai-settings/lib/personaBoxSchemas.ts \
  supabase/functions/_shared/persona-compiler.ts
```

Reportar:
- Schema Zod atual (copia literal)
- Estrutura do data: `areas[]`, `items[]`, ou tudo aninhado?
- Como `formatDelivery` é implementado hoje
- Se `query_delivery_items` (SUF15) já tem fallback Products implementado

### B. Volume real da `delivery` legada

```sql
SELECT 
  tenant_id,
  data
FROM persona_boxes
WHERE box_type = 'delivery' AND is_active = true
LIMIT 5;
```

Reportar amostras pra entender estrutura legada.

### C. Enum persona_box_type atual

```sql
SELECT unnest(enum_range(NULL::persona_box_type)) AS box_type;
```

Esperado hoje: 13 valores (12 antigos + pagamento). Vai precisar adicionar 3 novos valores.

### D. Decisões pendentes

#### D1. Approach de schemas — reuso ou cópia?

**Delivery Items** tem schema idêntico a Products. 2 opções:

**Opção A — Aliasing:** `DELIVERY_ITEMS_SCHEMA = { ...PRODUCTS_SCHEMA, boxType: "delivery_items" }`. Schema de fato compartilhado, mudança em Products propaga pra Delivery Items.

**Opção B — Cópia:** Define schema separado idêntico, mas independente. Mudanças em um não afetam outro. Permite divergência futura.

**Recomendação:** **Opção A (aliasing).** Razões:
- Fonte da verdade única
- Mudança em Products (ex: campo novo) propaga automaticamente
- Cliente vê interface idêntica (consistência)
- Se futuramente precisar divergir, vira sprint própria

Mas **excelLimitColumn** é diferente: Products usa `excel_max_mb_products`, Delivery Items usa `excel_max_mb_delivery_items` (ambos seedados no SUF16).

#### D2. Tool `query_delivery_items` — atualizar SUF15

SUF15 já criou tool com fallback Products. Atualizar pra:
- Lê Delivery Items primeiro (se preenchido)
- Senão, lê Products filtrado por `available_for_delivery=true`
- Retorna mesmos 12 campos (igual `query_products`)

Confirmar que SUF15 já implementou ou se precisa ajustar.

#### D3. Tool `query_delivery_areas` — criar

Busca por:
- Bairro, cidade, CEP
- Retorna área com taxa, tempo, mínimo, restrição

Cliente: "entregam em Pirapora?" → tool → retorna áreas que match
Cliente: "qual a taxa pro Centro?" → tool → retorna taxa

Haystack: `neighborhood + city`. CEP busca **exata** (não fuzzy — string formato `38600-000` precisa match preciso).

#### D4. Delivery Config — sem tool, vai no contexto

Singleton com configurações operacionais. **IA precisa SEMPRE saber pedido mínimo, horário, políticas.** Tool seria contraproducente — cliente pergunta "qual horário do delivery?" e IA tem que pedir tool? Não.

Compiler `formatDeliveryConfig` despeja TUDO no contexto. Tem 11 campos, peso de tokens irrelevante.

#### D5. ALTER TYPE — 3 valores novos no enum

Migration:
```sql
ALTER TYPE persona_box_type ADD VALUE IF NOT EXISTS 'delivery_items';
ALTER TYPE persona_box_type ADD VALUE IF NOT EXISTS 'delivery_areas';
ALTER TYPE persona_box_type ADD VALUE IF NOT EXISTS 'delivery_config';
```

Pedro roda manualmente no SQL Editor (igual fez no PR3). Padrão estabelecido.

#### D6. Caixa `delivery` legada — desativa ou mantém?

Não dá pra remover do enum (Postgres não suporta `DROP VALUE`). Mas pode:
- Deixar enum legacy
- Remover do registry/UI/tools
- DELETE manual de dados existentes

Approach: **legacy fica no enum mas removido completamente do código**. Dados apagados.

Code remove referências: `BOX_SCHEMAS`, `BOX_TO_TOOL_MAP`, `AbaBlocos`, `EditBoxDialog`, `usePersonaBoxes`, compiler, tool.

#### D7. UI — onde aparecem as 3 caixas?

Memory item #14: seção **"O QUE VOCÊ OFERECE"** já tem Products + Services. As 3 caixas Delivery entram lá:

```
SEÇÃO O QUE VOCÊ OFERECE
├── Products
├── Services
├── Delivery Items     [NOVA, 7ª posição]
├── Delivery Areas     [NOVA, 8ª posição]
├── Delivery Config    [NOVA, 9ª posição]
└── Events             [10ª posição, fica pra PR10]
```

#### D8. Compilers — 3 separados ou 1 unificado?

**3 separados.** Razões:
- Cada caixa tem cardinality diferente (multi_item / multi_item / singleton)
- Comportamento diferente (Items pode ser fallback, Config sempre vai)
- Mais simples de manter

```ts
function summarizeDeliveryItems(box, productsBox) {
  if (box?.data?.items?.length) {
    return /* count + sample + tool ref */;
  }
  // Fallback: Products filtrado
  if (productsBox?.data?.items?.some(i => i.available_for_delivery)) {
    return /* aviso de fallback ativo */;
  }
  return "";
}

function summarizeDeliveryAreas(box) { /* count + sample + tool ref */ }

function formatDeliveryConfig(box) { /* despeja TUDO no contexto */ }
```

Confirmar.

#### D9. Validação Areas — neighborhood obrigatório

Single required (`neighborhood`). City/CEP/etc opcionais.

#### D10. Campo `available_for_delivery` em Products

PR4 já adicionou. Validar que está populado pros tenants atuais. Cliente que não preencheu = `available_for_delivery=null` (não vai pro fallback).

Reportar:
```sql
SELECT 
  COUNT(*) FILTER (WHERE (item->>'available_for_delivery')::boolean = true) AS yes,
  COUNT(*) FILTER (WHERE (item->>'available_for_delivery')::boolean = false) AS no,
  COUNT(*) FILTER (WHERE item->>'available_for_delivery' IS NULL) AS null_value
FROM persona_boxes,
     jsonb_array_elements(data->'items') AS item
WHERE box_type = 'products' AND is_active = true;
```

---

## Aguarda OK antes de prosseguir.

---

## Etapa 2 — Migration enum

```sql
-- supabase/migrations/<timestamp>_pr9_delivery_enums.sql

ALTER TYPE persona_box_type ADD VALUE IF NOT EXISTS 'delivery_items';
ALTER TYPE persona_box_type ADD VALUE IF NOT EXISTS 'delivery_areas';
ALTER TYPE persona_box_type ADD VALUE IF NOT EXISTS 'delivery_config';
```

Pedro roda manualmente no SQL Editor antes do deploy do ai-reply.

---

## Etapa 3 — Schemas declarativos

```ts
// box-schemas.ts

// Delivery Items: aliasing de Products
export const DELIVERY_ITEMS_SCHEMA: BoxSchemaDef = {
  ...PRODUCTS_SCHEMA,
  boxType: "delivery_items",
  label: "Cardápio de delivery",
};

// Delivery Areas: caixa nova
export const DELIVERY_AREAS_SCHEMA: BoxSchemaDef = {
  boxType: "delivery_areas",
  label: "Áreas de entrega",
  cardinality: "multi_item",
  hasExcel: true,
  blocks: [
    {
      title: "Localidade",
      fields: [
        { field: "neighborhood", question: "Bairro / Região", type: "text", required: true },
        { field: "city", question: "Cidade", type: "text" },
        { field: "zip_start", question: "CEP inicial", type: "text", placeholder: "38600-000" },
        { field: "zip_end", question: "CEP final", type: "text", placeholder: "38699-999" },
      ],
    },
    {
      title: "Logística",
      fields: [
        { field: "delivery_fee", question: "Taxa de entrega", type: "number", helper: "R$ por pedido" },
        { field: "estimated_time_minutes", question: "Tempo estimado (min)", type: "number" },
        { field: "minimum_order", question: "Pedido mínimo nesta área", type: "number" },
        { field: "max_distance_km", question: "Distância máxima (km)", type: "text" },
      ],
    },
    {
      title: "Direcionamento IA",
      fields: [
        { field: "restrictions", question: "Atende com restrição?", type: "single_choice", options: ["Atende", "Não atende", "Sob consulta"] },
        { field: "ai_notes", question: "Observações pra IA", type: "textarea" },
      ],
    },
  ],
};

// Delivery Config: singleton com perguntas
export const DELIVERY_CONFIG_SCHEMA: BoxSchemaDef = {
  boxType: "delivery_config",
  label: "Configurações do delivery",
  cardinality: "singleton",
  hasExcel: false,
  blocks: [
    {
      title: "Operação",
      fields: [
        { field: "global_minimum_order", question: "Pedido mínimo geral", type: "number", helper: "Fallback se área não tiver mínimo próprio" },
        { field: "service_fee_percent", question: "Taxa de serviço (%)", type: "number" },
        { field: "delivery_hours", question: "Horário de delivery", type: "textarea", helper: "Pode diferir do horário da loja. Ex: 'Seg-Sex 18-23h, Sáb-Dom 12-23h'" },
        { field: "average_time_fallback", question: "Tempo médio geral (fallback)", type: "text", placeholder: "Ex: 45-60 minutos" },
        { field: "accepted_payment_methods", question: "Formas de pagamento aceitas", type: "csv" },
      ],
    },
    {
      title: "Política",
      fields: [
        { field: "cancellation_policy", question: "Política de cancelamento", type: "textarea" },
        { field: "damaged_product_policy", question: "Política de produto avariado", type: "textarea" },
        { field: "delay_policy", question: "Política de atraso", type: "textarea" },
      ],
    },
    {
      title: "Direcionamento IA",
      fields: [
        { field: "order_status_protocol", question: "Como informar status do pedido", type: "textarea" },
        { field: "escalation_rule", question: "Quando escalar pra humano", type: "textarea", placeholder: "Ex: atraso > 30min, cancelamento, reclamação grave" },
        { field: "ai_notes", question: "Observações pra IA", type: "textarea" },
      ],
    },
  ],
};

// Adicionar ao registry
export const BOX_SCHEMAS: Record<string, BoxSchemaDef> = {
  // ... anteriores
  delivery_items: DELIVERY_ITEMS_SCHEMA,
  delivery_areas: DELIVERY_AREAS_SCHEMA,
  delivery_config: DELIVERY_CONFIG_SCHEMA,
};
```

---

## Etapa 4 — Forms

### DeliveryItemsForm (wrapper ~12 linhas)

```tsx
export function DeliveryItemsForm({ items, onChange, ...rest }: Props) {
  return (
    <BoxFormMultiItem
      boxType="delivery_items"
      titleField="name"
      items={items}
      onChange={onChange}
      modes={["manual", "excel"]}
    />
  );
}
```

### DeliveryAreasForm (wrapper ~12 linhas)

```tsx
export function DeliveryAreasForm({ items, onChange, ...rest }: Props) {
  return (
    <BoxFormMultiItem
      boxType="delivery_areas"
      titleField="neighborhood"
      items={items}
      onChange={onChange}
      modes={["manual", "excel"]}
    />
  );
}
```

### DeliveryConfigForm (wrapper ~12 linhas)

```tsx
export function DeliveryConfigForm(props: Props) {
  return <BoxFormGeneric boxType="delivery_config" {...props} />;
}
```

(Singleton usa `BoxFormGeneric` igual Establishment/Hours/Pagamento.)

### AbaBlocos.tsx

3 cards novos na seção O QUE OFERECE:
- "Cardápio de delivery"
- "Áreas de entrega"
- "Configurações do delivery"

Remover card legado "Delivery" se ainda existe.

### EditBoxDialog.tsx

3 entries novas + remove legacy.

---

## Etapa 5 — Tools e compiler

### Tool query_delivery_items (atualiza SUF15)

```ts
export async function queryDeliveryItems(supabase, tenantId, query: string, limit = 10) {
  // Tenta Delivery Items primeiro
  const { data: deliveryBox } = await supabase
    .from("persona_boxes")
    .select("data")
    .eq("tenant_id", tenantId)
    .eq("box_type", "delivery_items")
    .eq("is_active", true)
    .single();
  
  if (deliveryBox?.data?.items?.length) {
    const filtered = filterProducts(deliveryBox.data.items, query); // mesma fn de Products
    return filtered.slice(0, limit).map(productToReturnShape);
  }
  
  // Fallback: Products filtrado por available_for_delivery
  const { data: productsBox } = await supabase
    .from("persona_boxes")
    .select("data")
    .eq("tenant_id", tenantId)
    .eq("box_type", "products")
    .eq("is_active", true)
    .single();
  
  if (!productsBox?.data?.items) return [];
  
  const deliveryProducts = productsBox.data.items.filter(
    (i: any) => i.available_for_delivery === true
  );
  const filtered = filterProducts(deliveryProducts, query);
  return filtered.slice(0, limit).map(productToReturnShape);
}
```

### Tool query_delivery_areas (nova)

```ts
export async function queryDeliveryAreas(supabase, tenantId, query: string, limit = 10) {
  const { data: box } = await supabase
    .from("persona_boxes")
    .select("data")
    .eq("tenant_id", tenantId)
    .eq("box_type", "delivery_areas")
    .eq("is_active", true)
    .single();
  
  if (!box?.data?.items) return [];
  
  const items = box.data.items as any[];
  const filtered = filterAreas(items, query);
  
  return filtered.slice(0, limit).map(item => ({
    neighborhood: item.neighborhood,
    city: item.city,
    zip_start: item.zip_start,
    zip_end: item.zip_end,
    delivery_fee: item.delivery_fee,
    estimated_time_minutes: item.estimated_time_minutes,
    minimum_order: item.minimum_order,
    max_distance_km: item.max_distance_km,
    restrictions: item.restrictions,
    ai_notes: item.ai_notes,
  }));
}

function filterAreas(items: any[], query: string): any[] {
  if (!query) return items;
  const q = query.toLowerCase();
  
  // Match exato em CEP (formato 12345-678 ou 12345678)
  const cepMatch = q.replace(/\D/g, "");
  if (cepMatch.length === 8) {
    return items.filter(item => {
      const start = item.zip_start?.replace(/\D/g, "") || "";
      const end = item.zip_end?.replace(/\D/g, "") || "";
      return cepMatch >= start && cepMatch <= end;
    });
  }
  
  // Fuzzy em bairro/cidade
  return items.filter(item => {
    const haystack = [item.neighborhood, item.city].filter(Boolean).join(" ").toLowerCase();
    return haystack.includes(q);
  });
}
```

### Compiler

```ts
function summarizeDeliveryItems(deliveryBox, productsBox): string {
  if (deliveryBox?.data?.items?.length) {
    const items = deliveryBox.data.items;
    const sample = items.slice(0, 5).map((i: any) => i.name).join(", ");
    return `## Cardápio de delivery\n\nVocê tem ${items.length} itens específicos pro delivery. Use \`query_delivery_items(query)\` pra buscar.\n\n${sample ? `Exemplos: ${sample}` : ""}`;
  }
  
  const deliveryProducts = productsBox?.data?.items?.filter((i: any) => i.available_for_delivery === true);
  if (deliveryProducts?.length) {
    return `## Cardápio de delivery\n\nNão há cardápio específico de delivery. Sistema usa Products filtrado por "Disponível pra delivery" (${deliveryProducts.length} itens). Use \`query_delivery_items(query)\` pra buscar.`;
  }
  
  return "";
}

function summarizeDeliveryAreas(box): string {
  if (!box?.data?.items?.length) return "";
  const items = box.data.items;
  const sample = items.slice(0, 5).map((i: any) => i.neighborhood).join(", ");
  return `## Áreas de entrega\n\nVocê atende ${items.length} áreas. Use \`query_delivery_areas(query)\` pra buscar por bairro, cidade ou CEP.\n\nExemplos: ${sample}`;
}

function formatDeliveryConfig(box): string {
  if (!box?.data) return "";
  const d = box.data;
  
  const lines = [];
  if (d.delivery_hours) lines.push(`- Horário: ${d.delivery_hours}`);
  if (d.global_minimum_order) lines.push(`- Pedido mínimo geral: R$ ${d.global_minimum_order}`);
  if (d.service_fee_percent) lines.push(`- Taxa de serviço: ${d.service_fee_percent}%`);
  if (d.average_time_fallback) lines.push(`- Tempo médio: ${d.average_time_fallback}`);
  if (d.accepted_payment_methods?.length) lines.push(`- Formas de pagamento: ${d.accepted_payment_methods.join(", ")}`);
  if (d.cancellation_policy) lines.push(`- Cancelamento: ${d.cancellation_policy}`);
  if (d.damaged_product_policy) lines.push(`- Avariado: ${d.damaged_product_policy}`);
  if (d.delay_policy) lines.push(`- Atraso: ${d.delay_policy}`);
  if (d.order_status_protocol) lines.push(`- Status do pedido: ${d.order_status_protocol}`);
  if (d.escalation_rule) lines.push(`- Quando escalar: ${d.escalation_rule}`);
  if (d.ai_notes) lines.push(`- Observações: ${d.ai_notes}`);
  
  if (!lines.length) return "";
  return `## Configurações do delivery\n\n${lines.join("\n")}`;
}
```

---

## Etapa 6 — Excel templates

### download-box-template

`generateExamples()` ganha entries:

```ts
if (boxType === "delivery_items") {
  // Reusa exemplos de Products (schema idêntico)
  return generateExamples("products");
}

if (boxType === "delivery_areas") {
  return [
    ["Centro", "Pirapora", "38600-000", "38600-999", 5.00, 30, 30.00, "5km", "Atende", ""],
    ["Sagrada Família", "Pirapora", "38601-000", "38601-999", 7.50, 45, 30.00, "8km", "Atende", "Bairro mais distante, taxa maior"],
    ["Várzea da Palma", "Várzea da Palma", "38600-000", "38699-999", 15.00, 90, 50.00, "30km", "Sob consulta", "Pedido grande tem desconto na taxa"],
  ];
}

return [];
```

### Não tem Excel pra Delivery Config (singleton)

Edge `download-box-template` retorna 404 ou erro claro pra `boxType=delivery_config`. Confirmar comportamento.

---

## Etapa 7 — Cleanup + deploy

### Antes do deploy

**1) Volume Delivery legado:**
```sql
SELECT 
  tenant_id,
  jsonb_typeof(data) AS data_type,
  CASE 
    WHEN jsonb_typeof(data->'items') = 'array' THEN jsonb_array_length(data->'items')
    WHEN jsonb_typeof(data->'areas') = 'array' THEN jsonb_array_length(data->'areas')
    ELSE 0
  END AS items_count
FROM persona_boxes
WHERE box_type = 'delivery' AND is_active = true;
```

**2) ALTER TYPE (3 valores novos):**
```sql
ALTER TYPE persona_box_type ADD VALUE IF NOT EXISTS 'delivery_items';
```

```sql
ALTER TYPE persona_box_type ADD VALUE IF NOT EXISTS 'delivery_areas';
```

```sql
ALTER TYPE persona_box_type ADD VALUE IF NOT EXISTS 'delivery_config';
```

**3) Confirma:**
```sql
SELECT unnest(enum_range(NULL::persona_box_type)) AS box_type;
```

Esperado: 16 valores (13 anteriores + 3 novos).

**4) DELETE delivery legado:**
```sql
DELETE FROM persona_boxes WHERE box_type = 'delivery';
```

**5) Confirma:**
```sql
SELECT COUNT(*) FROM persona_boxes WHERE box_type IN ('delivery', 'delivery_items', 'delivery_areas', 'delivery_config');
```

Esperado: 0.

### Deploy

```bash
gh pr merge <PR> --squash --delete-branch
git checkout main && git pull origin main
supabase functions deploy ai-reply
git push origin main
```

### Validação pós-deploy

1. **3 cards na seção O QUE OFERECE:** "Cardápio de delivery", "Áreas de entrega", "Configurações do delivery"
2. **Card legado "Delivery"** sumiu
3. Modo Manual de cada uma funciona
4. Modo Excel de Items + Areas funciona (Config não tem)
5. **Não-regressão:** Products + Services + FAQ + Objections + Team + Forwards continuam OK

---

## Critérios de aceite

- [ ] Etapa 1 confirmação aprovada
- [ ] Migration enum rodada por Pedro antes do deploy
- [ ] DELIVERY_ITEMS_SCHEMA aliasing de Products
- [ ] DELIVERY_AREAS_SCHEMA novo (10 campos / 3 blocos)
- [ ] DELIVERY_CONFIG_SCHEMA novo (11 campos / 3 blocos / singleton)
- [ ] 3 forms wrappers (~12 linhas cada)
- [ ] query_delivery_items atualizada com fallback Products
- [ ] query_delivery_areas nova (com match de CEP exato + fuzzy bairro/cidade)
- [ ] formatDeliveryConfig despeja TUDO (sem tool)
- [ ] Caixa "delivery" legada removida do código
- [ ] generateExamples ganha delivery_items + delivery_areas
- [ ] Build/tsc/vitest verde
- [ ] Pedro confirma DELETE + ALTER TYPE
- [ ] PR description anota: "PR9 fecha 9 de 11 PRs da Sprint Catalog. 3 caixas Delivery substituem caixa legacy."

---

## Restrições

- ❌ Sem refator estrutural além do necessário
- ❌ Sem mexer em outras caixas
- ❌ Sem implementar tool `query_delivery_config` (vai no contexto)
- ❌ Sem Excel pra Delivery Config (singleton)
- ✅ Aliasing schema Products → Delivery Items
- ✅ Branch: `catalog-pr9-delivery`
- ✅ PR título: `feat(catalog): Delivery (3 caixas) + Excel (PR9)`

---

## Pós-merge — Próximo: PR10 (Events)

PR10 é a caixa Events com 51 campos em accordions visuais. Não tem Excel (são "pacotes" complexos, cada um com muitos detalhes). Memory item #15 cobre.

Estimativa ~5-6h.

---

## O que NÃO fazer neste PR

- ❌ Mexer em Hours/Pagamento (caixas singleton de outras seções)
- ❌ Implementar agendamento via tools (Sprint Schedule futura)
- ❌ Otimizar fallback Products → Delivery Items com tsvector (futuro)
- ❌ Custom (PR11)
