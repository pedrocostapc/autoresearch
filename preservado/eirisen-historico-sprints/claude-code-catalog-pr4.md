# PR4 — Products + Excel + Tool Refatorada (Sprint Catalog Onda 1)

> **Quarto e último PR da Onda 1.** Maior PR da Sprint Catalog. Destrava 30k itens da loja Vanderlei.
>
> Estimativa: 1.5-2 dias.
> Branch: `catalog-pr4-products-excel`

---

## Contexto

Onda 1 já tem fundação sólida:
- ✅ PR1 — schema declarativo, QuestionBlock, BoxFormGeneric, Establishment
- ✅ PR2 — Hours + Links
- ✅ PR3 — Pagamento (caixa nova)
- ✅ SUF16 — system_config com `support_whatsapp_number` + `excel_max_mb_*`

PR4 fecha a Onda 1 com a caixa **mais importante**: Products. É a que destrava o caso real (loja com 30k itens).

PR4 traz **3 capacidades novas**:
1. **Refator de Products** pro schema declarativo (17 colunas, novo bloco Atributos)
2. **Excel template generator** — edge que gera XLSX vazio com headers + exemplos + aba Instruções
3. **Excel import** — edge que recebe XLSX, valida tamanho (via system_config), parseia, insere

E reusa:
- Fundação dos PRs 1-3
- `support_whatsapp_number` do SUF16 pro botão "Mande pra equipe"
- `excel_max_mb_products` do SUF16 pra validação de tamanho

---

## Schema final Products (17 colunas)

| Bloco | Campo | Tipo | Obrigatório |
|---|---|---|---|
| **1. Identificação** | name | text | ✅ |
| | sku | text | |
| | brand | text | |
| | category | text livre | |
| | description | textarea | |
| **2. Preço** | price | number | |
| | discount_price | number | |
| | discount_condition | text livre | |
| | unit | text | |
| **3. Disponibilidade** | available | single_choice (Sim/Não/Sob encomenda) | |
| | stock | number | |
| | available_for_delivery | boolean | |
| **4. Atributos** | preparation_time | text (ex: "20min") | |
| | dietary_restrictions | text CSV (vegano, sem glúten, etc) | |
| | ingredients | textarea | |
| **5. Variáveis extras** | var_1, var_2, var_3 | text (3 campos) | |

Total: **17 campos. Apenas Nome obrigatório.**

Variantes ("blusa preta" / "blusa laranja") = linhas separadas.

---

## Etapa 1 — Confirmações antes de codar

### A. Schema atual de Products

```bash
grep -n "ProductSchema\|CatalogItemSchema\|formatProducts" src/features/ai-settings/lib/personaBoxSchemas.ts supabase/functions/_shared/persona-compiler.ts
```

Reportar:
- Schema Zod atual de Products (copia literal)
- Se ainda compartilha `CatalogItemSchema` com Services/Delivery (raio-x mencionou price obrigatório)
- Como `formatProducts` é implementado hoje
- Sample real do tenant Construai/Vanderlei (71 itens, mais volumoso)

```sql
-- Sample
SELECT data->'items'->0 AS first_item, jsonb_array_length(data->'items') AS total
FROM persona_boxes
WHERE box_type = 'products' AND is_active = true
ORDER BY jsonb_array_length(data->'items') DESC
LIMIT 1;
```

### B. UI atual do modal Products

```bash
grep -n "ProductsForm\|ProductsModal" src/features/ai-settings/components/blocos/forms/
```

Reportar:
- Componente do modal atual
- Se tem 2 modos hoje (Manual + Colar Lista)
- Como o "Colar Lista" parseia (regex? linha-a-linha?)

### C. Capacidade Excel no projeto

```bash
grep -rn "xlsx\|sheetjs" package.json src/ supabase/functions/ --include="*.json" --include="*.ts" --include="*.tsx"
```

Reportar:
- SheetJS (xlsx) instalado?
- Se sim, em qual versão e onde já é usado
- Se não, instalar (`npm i xlsx`)
- Confirma que funciona em Deno (edge functions)

Atenção: edges Supabase rodam Deno, não Node. SheetJS funciona em Deno via `import * as XLSX from 'https://esm.sh/xlsx'` ou similar.

### D. Decisões pendentes

#### D1. Comportamento de re-import

Pedro decidiu antes: **re-import substitui tudo**. Sem upsert.

Confirmação: ao importar Excel de Products, edge faz:
```ts
// transação atômica:
1. SELECT data->'items' antigos (pra log/rollback se falhar)
2. UPDATE persona_boxes SET data = { items: [...novos] } WHERE box_type = 'products' AND tenant_id = ?
3. Confirma sucesso
```

Falha em qualquer ponto → reverte. Substitui completo.

Confirmar.

#### D2. Validação de Excel

Edge valida antes de processar:
- Tamanho ≤ `excel_max_mb_products` do system_config
- Aba "Produtos" existe (ou o que for definido como aba canônica)
- Headers batem com schema declarativo
- Pelo menos 1 linha além do header

Erros voltam pro front com mensagem clara:
- "Arquivo grande demais. Limite atual: X MB. Use 'Mande pra equipe arrumar'."
- "Aba 'Produtos' não encontrada. Use o modelo padrão."
- "Coluna 'Nome' não encontrada. Use o modelo padrão."

Confirmar approach.

#### D3. Aba "Instruções" no template gerado

Modelo XLSX vazio gerado pelo `download-box-template/products` deve ter:
- **Aba 1: "Produtos"** — colunas + 2-3 linhas de exemplo + linha vazia
- **Aba 2: "Instruções"** — texto explicativo seguindo o padrão Team que Pedro forneceu antes (preenchimento, formato, exemplo bom vs ruim)

Confirma.

#### D4. Tool `query_products` — atualizar?

SUF15 já registrou tool no payload da API e melhorou master prompt. Hoje a busca dentro da tool é `String.includes()` em memória + slice(0, 10).

Pra 30k itens da Vanderlei, **`includes()` em memória vai escalar mal mas ainda funciona** (consulta acontece no edge ai-reply, não no banco).

**Opção A (PR4):** mantém `String.includes()`. Funciona até ~50k itens. Refator pra tsvector vira sprint futura.

**Opção B (PR4):** já refatora pra tsvector com tabela própria `box_products` indexada.

Recomendação: **A**. Razões:
- Pedro tem 1 caso de 30k itens, não 200k
- `String.includes()` resolve até onde precisa
- Refator pra tsvector exige migration grande, mexe em ai-reply, smoke complexo
- Vira **sprint própria** depois se virar gargalo real (`SUF Catalog Search` ou `Sprint Search`)

Code aceita ou propõe alternativa.

#### D5. Volume real em produção

```sql
SELECT box_type, COUNT(*), 
       AVG(LENGTH(data::text))::int AS avg_chars,
       MAX(LENGTH(data::text)) AS max_chars
FROM persona_boxes
WHERE box_type = 'products'
GROUP BY box_type;
```

Esperado: 2 tenants, max 71 itens. Confirmar antes do DELETE manual.

---

## Aguarda OK antes de prosseguir.

---

## Etapa 2 — Schema declarativo

Adicionar `PRODUCTS_SCHEMA` em `_shared/box-schemas.ts`:

```ts
export const PRODUCTS_SCHEMA: BoxSchemaDef = {
  boxType: "products",
  label: "Produtos",
  cardinality: "multi_item",  // novo cardinality, primeira caixa que usa
  hasExcel: true,              // primeira caixa com Excel!
  blocks: [
    {
      title: "Identificação",
      fields: [
        { field: "name", question: "Nome do produto", type: "text", required: true },
        { field: "sku", question: "SKU/código", type: "text" },
        { field: "brand", question: "Marca", type: "text" },
        { field: "category", question: "Categoria", type: "text", helper: "Ex: Bebidas, Roupas femininas, Cimento" },
        { field: "description", question: "Descrição", type: "textarea" },
      ],
    },
    {
      title: "Preço",
      fields: [
        { field: "price", question: "Preço normal", type: "number" },
        { field: "discount_price", question: "Preço com desconto", type: "number" },
        { field: "discount_condition", question: "Condição do desconto", type: "text", helper: "Ex: 'À vista', 'Acima de 5un'" },
        { field: "unit", question: "Unidade", type: "text", placeholder: "un, kg, m², etc" },
      ],
    },
    {
      title: "Disponibilidade",
      fields: [
        { field: "available", question: "Disponível?", type: "single_choice", options: ["Sim", "Não", "Sob encomenda"] },
        { field: "stock", question: "Estoque", type: "number" },
        { field: "available_for_delivery", question: "Disponível pra delivery?", type: "boolean" },
      ],
    },
    {
      title: "Atributos",
      fields: [
        { field: "preparation_time", question: "Tempo de preparo", type: "text", placeholder: "Ex: 20min, Imediato" },
        { field: "dietary_restrictions", question: "Restrições alimentares", type: "csv", helper: "Vegano, sem glúten, etc — separe por vírgula" },
        { field: "ingredients", question: "Ingredientes / composição", type: "textarea" },
      ],
    },
    {
      title: "Variáveis extras",
      fields: [
        { field: "var_1", question: "Variável extra 1", type: "text", helper: "Ex: Cor, Tamanho, Voltagem — você define" },
        { field: "var_2", question: "Variável extra 2", type: "text" },
        { field: "var_3", question: "Variável extra 3", type: "text" },
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
  products: PRODUCTS_SCHEMA,  // NOVO
};
```

**Atenção tipos:** `cardinality: "multi_item"` é primeira caixa que usa. Implica que `data` é `{ items: [...] }` em vez de `{ ...campos }`. Helper precisa ser atualizado pra lidar com items[].

---

## Etapa 3 — Edge `download-box-template`

Edge nova que gera XLSX vazio com headers + 2 linhas de exemplo + aba "Instruções".

```ts
// supabase/functions/download-box-template/index.ts

import * as XLSX from "https://esm.sh/xlsx@0.18.5";
import { getBoxSchema, getAllFieldsForBox } from "../_shared/box-schemas.ts";

serve(async (req) => {
  const url = new URL(req.url);
  const boxType = url.searchParams.get("boxType");
  
  if (!boxType) {
    return new Response("boxType required", { status: 400 });
  }
  
  const schema = getBoxSchema(boxType);
  if (!schema || !schema.hasExcel) {
    return new Response("Schema not found or has no Excel template", { status: 404 });
  }
  
  // Aba 1: Dados
  const fields = getAllFieldsForBox(boxType);
  const headers = fields.map(f => f.question.replace(/\?$/, ""));  // Pergunta humana como header
  const exampleRows = generateExamples(boxType);  // 2-3 linhas de exemplo
  
  const ws1 = XLSX.utils.aoa_to_sheet([headers, ...exampleRows]);
  
  // Aba 2: Instruções
  const ws2 = XLSX.utils.aoa_to_sheet(buildInstructions(schema));
  
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws1, schema.label);
  XLSX.utils.book_append_sheet(wb, ws2, "Instruções");
  
  const buffer = XLSX.write(wb, { type: "array", bookType: "xlsx" });
  
  return new Response(buffer, {
    headers: {
      "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "Content-Disposition": `attachment; filename="modelo-${boxType}.xlsx"`,
    },
  });
});

function generateExamples(boxType: string): any[][] {
  if (boxType === "products") {
    return [
      ["Camiseta Básica", "CAM-001", "Marca X", "Roupas", "100% algodão", 49.90, 39.90, "À vista", "un", "Sim", 100, true, "", "", "100% algodão", "Preto", "M", ""],
      ["Pizza Margherita", "", "", "Cardápio", "Tomate, mussarela, manjericão", 45.00, 0, "", "un", "Sim", 0, true, "20min", "vegetariano", "tomate, mussarela, manjericão", "", "", ""],
    ];
  }
  return [];
}

function buildInstructions(schema: BoxSchemaDef): any[][] {
  return [
    [`COMO PREENCHER: ${schema.label.toUpperCase()}`],
    [""],
    ["1. Use a aba acima pra cadastrar seus produtos."],
    ["2. Cada linha = 1 produto."],
    ["3. Apenas a coluna 'Nome do produto' é obrigatória."],
    ["4. Variantes (cor, tamanho) viram linhas separadas. Ex: 'Camisa Preta' e 'Camisa Branca' = 2 linhas."],
    [""],
    ["DICA — Coluna 'Disponível pra delivery?'"],
    ["Marque TRUE/SIM pra produtos que aparecem no delivery. Se não tiver delivery, deixe vazio."],
    [""],
    ["DICA — Variáveis extras (Var 1, 2, 3)"],
    ["Use as 3 colunas de variáveis livres pra dados que seu negócio tem mas o sistema não cobre."],
    ["Renomeie a coluna Var 1 pra 'Cor' se for o caso. O sistema usa o nome que você colocar."],
  ];
}
```

---

## Etapa 4 — Edge `import-box-excel`

Edge nova que recebe XLSX, valida, parseia, insere.

```ts
// supabase/functions/import-box-excel/index.ts

import * as XLSX from "https://esm.sh/xlsx@0.18.5";
import { getBoxSchema, getAllFieldsForBox } from "../_shared/box-schemas.ts";

serve(async (req) => {
  // Auth
  const supabase = createClient(/* ... */);
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return new Response("Unauthorized", { status: 401 });
  
  // Parse multipart
  const formData = await req.formData();
  const file = formData.get("file") as File;
  const boxType = formData.get("boxType") as string;
  const tenantId = formData.get("tenantId") as string;
  
  if (!file || !boxType || !tenantId) {
    return jsonError("Missing parameters");
  }
  
  // 1. Valida tamanho
  const { data: config } = await supabase
    .from("system_config")
    .select(`excel_max_mb_${boxType}`)
    .single();
  
  const maxMb = config?.[`excel_max_mb_${boxType}`] ?? 5;
  if (file.size > maxMb * 1024 * 1024) {
    return jsonError(`Arquivo grande demais. Limite atual: ${maxMb} MB.`);
  }
  
  // 2. Parse XLSX
  const buffer = await file.arrayBuffer();
  const workbook = XLSX.read(buffer, { type: "array" });
  const schema = getBoxSchema(boxType);
  
  // 3. Acha aba canônica
  const sheetName = schema.label;  // "Produtos"
  const sheet = workbook.Sheets[sheetName];
  if (!sheet) {
    return jsonError(`Aba "${sheetName}" não encontrada. Use o modelo padrão.`);
  }
  
  // 4. Parse linhas
  const rows = XLSX.utils.sheet_to_json(sheet, { header: 1 }) as any[][];
  if (rows.length < 2) {
    return jsonError("Planilha vazia ou só com cabeçalho.");
  }
  
  // 5. Mapeia headers
  const headers = rows[0].map((h: string) => h?.toString().trim());
  const fields = getAllFieldsForBox(boxType);
  const headerToField = mapHeadersToFields(headers, fields);
  
  // Verifica obrigatórios
  const requiredFields = fields.filter(f => f.required);
  for (const reqField of requiredFields) {
    if (!Object.values(headerToField).includes(reqField.field)) {
      return jsonError(`Coluna "${reqField.question}" não encontrada. Use o modelo padrão.`);
    }
  }
  
  // 6. Parse cada linha
  const items = rows.slice(1)
    .filter(row => row.some(cell => cell !== null && cell !== undefined && cell !== ""))
    .map(row => parseRow(row, headers, headerToField, fields));
  
  // 7. UPDATE em transação atômica (substitui tudo)
  const { error } = await supabase
    .from("persona_boxes")
    .update({ data: { items } })
    .eq("tenant_id", tenantId)
    .eq("box_type", boxType);
  
  if (error) return jsonError(`Erro ao salvar: ${error.message}`);
  
  return new Response(JSON.stringify({ success: true, imported: items.length }), {
    headers: { "Content-Type": "application/json" },
  });
});

function mapHeadersToFields(headers: string[], fields: BoxFieldDef[]): Record<number, string> {
  const map: Record<number, string> = {};
  headers.forEach((header, idx) => {
    // Match exato pela pergunta humana (sem ? final)
    const field = fields.find(f => f.question.replace(/\?$/, "").toLowerCase() === header.toLowerCase());
    if (field) map[idx] = field.field;
  });
  return map;
}

function parseRow(row: any[], headers: string[], map: Record<number, string>, fields: BoxFieldDef[]): any {
  const item: Record<string, any> = {};
  for (const [idx, fieldName] of Object.entries(map)) {
    const field = fields.find(f => f.field === fieldName)!;
    const rawValue = row[Number(idx)];
    item[fieldName] = parseValue(rawValue, field.type);
  }
  return item;
}

function parseValue(value: any, type: string): any {
  if (value === null || value === undefined || value === "") return undefined;
  switch (type) {
    case "number": return Number(value);
    case "boolean": 
      if (typeof value === "boolean") return value;
      const s = String(value).toLowerCase().trim();
      return ["sim", "true", "1", "yes"].includes(s);
    case "csv": 
      return String(value).split(",").map(s => s.trim()).filter(Boolean);
    default: 
      return String(value).trim();
  }
}
```

---

## Etapa 5 — UI: 3º modo "Excel" no modal Products

Modal Products hoje tem 2 modos: **Manual** e **Colar Lista**. Adicionar 3º: **Excel**.

```
┌─ Catálogo de Produtos ──────────────────────────┐
│                                                 │
│ [✏️ Manual] [📋 Colar Lista] [📊 Excel]         │  ← novo botão
│                                                 │
│ ─── modo Excel ───                              │
│                                                 │
│ 📥 Baixar modelo Excel                          │
│    (gera XLSX vazio com colunas + exemplos)     │
│                                                 │
│ 📤 Importar Excel preenchido                    │
│    [arrasta arquivo aqui ou clique pra subir]   │
│                                                 │
│ ⚠️  Sua planilha está bagunçada?                │
│ → Mande pra equipe arrumar                      │
│                                                 │
│   📱 Abrir WhatsApp do suporte                  │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Botão "Baixar modelo"

```tsx
function handleDownloadTemplate() {
  window.location.href = `${SUPABASE_URL}/functions/v1/download-box-template?boxType=products`;
}
```

### Botão "Importar Excel"

Componente upload (drag-drop):

```tsx
async function handleUpload(file: File) {
  // Validação client-side
  const { data: config } = await useSystemConfig("excel_max_mb_products");
  const maxMb = parseInt(config) || 5;
  
  if (file.size > maxMb * 1024 * 1024) {
    toast.error(`Arquivo maior que ${maxMb} MB`);
    return;
  }
  
  const formData = new FormData();
  formData.append("file", file);
  formData.append("boxType", "products");
  formData.append("tenantId", currentTenantId);
  
  const response = await fetch(`${SUPABASE_URL}/functions/v1/import-box-excel`, {
    method: "POST",
    headers: { Authorization: `Bearer ${session.access_token}` },
    body: formData,
  });
  
  const result = await response.json();
  if (result.success) {
    toast.success(`${result.imported} produtos importados!`);
    refetch();
  } else {
    toast.error(result.error);
  }
}
```

### Botão "Mande pra equipe arrumar"

```tsx
const { data: whatsapp } = useSystemConfig("support_whatsapp_number");

function handleContactSupport() {
  const message = encodeURIComponent(
    "Olá, preciso de ajuda pra preencher o Excel da minha caixa Products. Vou enviar o arquivo agora."
  );
  window.open(`https://wa.me/${whatsapp.replace(/\D/g, "")}?text=${message}`, "_blank");
}
```

---

## Etapa 6 — Cleanup + deploy

### Antes do deploy

Pedro roda no SQL Editor:

```sql
DELETE FROM persona_boxes WHERE box_type = 'products';
-- Esperado: 2 rows deletadas
```

### Deploy

```bash
gh pr merge <PR> --squash --delete-branch
git checkout main && git pull origin main
supabase functions deploy download-box-template
supabase functions deploy import-box-excel
supabase functions deploy ai-reply  # se compiler mudou
git push origin main
```

3 edges deployadas (2 novas + 1 atualizada se compiler mudou).

### Validação pós-deploy

Pedro abre `/settings/ai`:
1. Card Products com novo schema
2. Modo "Excel" visível
3. Clica "Baixar modelo" → baixa XLSX
4. Abre Excel → vê headers + 2 linhas exemplo + aba Instruções
5. Apaga exemplos, preenche 5 produtos teste
6. Salva
7. Volta no painel, clica "Importar Excel"
8. Sobe arquivo
9. Toast de sucesso "5 produtos importados"
10. Confirma no SQL Editor:

```sql
SELECT jsonb_array_length(data->'items') FROM persona_boxes 
WHERE box_type = 'products' AND tenant_id = '<TENANT>';
```

### Smoke real com Vanderlei

1. Pedro pega Excel real da loja Vanderlei
2. Adapta colunas pro modelo (renomeia headers)
3. Sobe via Importar Excel
4. Confirma quantos itens entraram (esperado próximo de 30k)
5. Manda mensagem teste no WhatsApp Vanderlei: "vcs tem cimento Votoran?"
6. IA chama `query_products` (SUF15) e responde com base no catálogo importado

---

## Critérios de aceite

- [ ] Etapa 1 confirmação aprovada antes de codar
- [ ] PRODUCTS_SCHEMA em box-schemas.ts (17 campos, 5 blocos)
- [ ] Edge `download-box-template` gera XLSX com 2 abas (dados + instruções)
- [ ] Edge `import-box-excel` valida tamanho via system_config
- [ ] UI: 3º modo "Excel" no modal Products
- [ ] Botão "Mande pra equipe arrumar" abre wa.me com numero do system_config
- [ ] Re-import substitui tudo (transação atômica)
- [ ] Mensagens de erro claras
- [ ] Build/tsc/vitest verde
- [ ] Pedro testa import com Excel real
- [ ] Smoke real Vanderlei com `query_products`
- [ ] PR description anota: "Fecha Onda 1 da Sprint Catalog"

---

## Restrições

- ❌ Sem refator de tsvector (fica pra futuro)
- ❌ Sem mexer em outras caixas
- ❌ Smoke automático (Pedro testa)
- ❌ Sem upsert (re-import substitui)
- ✅ Pode adicionar SheetJS no projeto se não tem
- ✅ Mostrar diff antes do commit
- ✅ Branch: `catalog-pr4-products-excel`
- ✅ PR título: `feat(catalog): Products + Excel + tool refatorada (PR4) — Fecha Onda 1`

---

## Pós-merge — Onda 2 começa

PR5 — Services + Excel (~4-6h, reusa toda infra de Excel do PR4)
PR6 — FAQ + Objections + Excel (juntos)
PR7 — Team + Excel
PR8 — Forwards + Excel
PR9 — Delivery (3 caixas: Items + Areas + Config)
PR10 — Events
PR11 — Custom

7 PRs na Onda 2, ~4 dias spread.

---

## O que NÃO fazer neste PR

- ❌ Outras caixas (Onda 2)
- ❌ Tsvector / pgvector
- ❌ pgvector embeddings
- ❌ Refator master prompt além do que SUF15 já fez
- ❌ Mexer em RAG conceitual
