# Caixa Products — Como Funciona

> Documento técnico sobre a caixa de produtos do Risen.
> Schema, busca, fuzzy match, tool, payload retornado.
> Atualizado: 11/05/2026 (pós PR #235)

---

## 1. ARMAZENAMENTO

### Tabela
`persona_boxes` (no Supabase Postgres)

### Identificação
```
box_type = 'products'
tenant_id = <uuid do tenant>
data = JSONB com array de items
is_active = true
```

### Estrutura no JSONB

```json
{
  "items": [
    {
      "name": "Varão",
      "sku": "VAR-5M-08",
      "brand": "EUCA",
      "category": "Madeira",
      "description": "Varão de eucalipto tratado",
      "price": 32.20,
      "discount_price": 28.00,
      "discount_condition": "Acima de 10 un",
      "unit": "un",
      "available": "Sim",
      "stock": 150,
      "available_for_delivery": "Sim",
      "prep_time": null,
      "restrictions": null,
      "ingredients": null,
      "var_1": "5m",
      "var_2": "Bitola 08 a 10 cm",
      "var_3": "MG"
    }
  ]
}
```

### 17 campos por item

| Bloco | Campo | Tipo |
|---|---|---|
| **1 - Identidade** | `name` | text (obrigatório) |
| | `sku` | text |
| | `brand` | text |
| | `category` | text |
| | `description` | text |
| **2 - Preço** | `price` | number |
| | `discount_price` | number |
| | `discount_condition` | text |
| | `unit` | text |
| **3 - Disponibilidade** | `available` | Sim / Não / Sob encomenda |
| | `stock` | number |
| | `available_for_delivery` | Sim / Não |
| **4 - Atributos** | `prep_time` | text |
| | `restrictions` | text |
| | `ingredients` | text |
| **5 - Variações** | `var_1` | text livre |
| | `var_2` | text livre |
| | `var_3` | text livre |

---

## 2. COMO É POPULADA

### 2 modos de input

**Manual (UI):**
- Painel CRM → IA → Persona → Bloco Products
- Adiciona/edita item por item
- Cards colapsáveis

**Excel (em massa):**
- Painel → caixa Products → modo Excel
- Download template → preenche → upload
- Edge `import-box-excel` valida
- UPDATE atômico (substitui tudo)

### Limite de tamanho

`system_config.excel_max_mb_products` controla tamanho máximo do upload (default 5MB).

### Casos extremos

- Vanderlei (Construbase): 2.401 itens com nomes únicos
- Euca Brasil: 1.458 itens com apenas 6 nomes únicos × 243 variações

---

## 3. ACESSO PELA IA

### Não vai inline no contexto

A caixa Products **NÃO é injetada no system_prompt**. Caixa de 200k chars consumiria ~50k tokens por chamada.

A IA acessa via **tool `query_products`** sob demanda.

### Tool: query_products

**Input schema:**
```typescript
{
  search?: string;          // texto buscado em haystack
  category?: string;        // filtra por categoria exata
  available_only?: boolean; // default true, esconde "Não" disponíveis
  limit?: number;           // default 50, max 200
}
```

**Como a IA chama:**
```typescript
query_products({ search: "varão" })
// ou
query_products({ search: "cimento 50kg", available_only: true })
// ou
query_products({ category: "Madeira", limit: 100 })
```

---

## 4. ALGORITMO DE BUSCA

### Função: `filterProducts` + `fuzzyProduct`

**Localização:** `supabase/functions/_shared/persona-tools.ts`

### Haystack

Quando IA passa `search: "varão 5m"`, a tool constrói haystack pra cada item:

```typescript
const haystack = [
  item.name,
  item.sku,
  item.brand,
  item.category,
  item.description,
  item.var_1,
  item.var_2,
  item.var_3
].filter(Boolean).join(' ').toLowerCase();
```

**Match:** substring case-insensitive de cada termo da query no haystack.

### Lógica do fuzzy

1. Quebra a query em termos (`"varão 5m"` → `["varão", "5m"]`)
2. Cada termo precisa aparecer no haystack do item
3. Se todos os termos batem → item passa
4. Se algum termo não bate → item é filtrado

**Exemplo:**
- Query: `"varão 5m"`
- Item: `{ name: "Varão", var_1: "5m", var_2: "Bitola 08 a 10 cm" }`
- Haystack: `"varão  5m bitola 08 a 10 cm"`
- Termos `varão` ✓ e `5m` ✓ → match

### Filtros adicionais

- `available_only=true` (default): exclui itens com `available != "Sim"`
- `category` (se informada): filtra `category` exato
- Resultado é ordenado pela ordem original do JSONB (não há ranking por score)

---

## 5. PAYLOAD RETORNADO

### Estrutura

```json
{
  "total_matches": 243,
  "returned": 50,
  "truncated": true,
  "hint": "243 itens encontrados. Variações disponíveis — pergunte ao cliente pra estreitar: var_1: 4m, 5m, 6m, 7m, 8m | var_2: Bitola 04-06, 06-08, 08-10 | var_3: SP, RJ, MG, MS",
  "items": [
    {
      "name": "Varão",
      "sku": "VAR-5M-08",
      "brand": "EUCA",
      "category": "Madeira",
      "description": "...",
      "price": 32.20,
      "discount_price": 28.00,
      "discount_condition": "Acima de 10 un",
      "unit": "un",
      "available": "Sim",
      "stock": 150,
      "available_for_delivery": "Sim",
      "var_1": "5m",
      "var_2": "Bitola 08 a 10 cm",
      "var_3": "MG"
    },
    ...
  ]
}
```

### Campos meta

| Campo | Significado |
|---|---|
| `total_matches` | Total de itens que dão match (antes do limite) |
| `returned` | Quantos itens vieram na resposta |
| `truncated` | true se total > returned |
| `hint` | String com variações disponíveis quando truncated |
| `items` | Array de produtos (até 50 default, 200 max) |

### Hint — quando aparece

Só quando `truncated = true`. Constrói uma string listando os valores únicos de `var_1`, `var_2` e `var_3` entre os itens filtrados.

```typescript
function buildProductsHint(items): string {
  const var1 = uniqueValues(items.map(i => i.var_1));
  const var2 = uniqueValues(items.map(i => i.var_2));
  const var3 = uniqueValues(items.map(i => i.var_3));
  
  // Só mostra variações que tem entre 2 e 30 valores únicos
  // (menos que 2 não ajuda, mais que 30 polui)
  ...
}
```

---

## 6. CICLO DE INTERAÇÃO ESPERADO

### Cenário 1 — Catálogo plano (Construbase)

```
Cliente: "tenho que comprar cimento"
IA chama: query_products({ search: "cimento" })
Tool retorna: { total_matches: 3, returned: 3, truncated: false, items: [...] }
IA responde: "Tenho Cimento CP-II 50kg R$25,90 disponível. Quantas unidades?"
```

Match direto, sem ambiguidade.

### Cenário 2 — Catálogo com variações (Euca)

```
Cliente: "tem varão?"
IA chama: query_products({ search: "varão" })
Tool retorna: { 
  total_matches: 243, 
  returned: 50, 
  truncated: true,
  hint: "var_1: 4m, 5m, 6m | var_2: 06mm, 08mm | var_3: SP, RJ, MG",
  items: [...]
}
IA NÃO lista os 50 itens
IA responde: "Tenho varão em 4 comprimentos (4m, 5m, 6m, 7m). Qual sua UF?"

Cliente: "MS, 5m bitola 08"
IA NÃO chama query_products de novo
IA procura nos items já retornados: name="Varão" + var_1="5m" + var_2="Bitola 08-10" + var_3="MS"
Encontra: { price: 48.30 }
IA responde: "Varão 5m bitola 08-10 em MS: R$48,30/un. Quantas unidades?"
```

### Anti-padrão (que existia antes do PR #235)

```
Cliente: "tem varão?"
IA chama: query_products({ search: "varão" })
Tool retorna: 10 items sem var_X, sem total_matches, sem hint
IA: vê 10 objetos idênticos "Varão" "Varão" "Varão"
IA: alucina presença/ausência baseada em conhecimento parcial
Resultado: "Tem varão" → "Não tem 5m bitola 08" → "Tem 5m bitola 08 R$32,20" → "Não tem"
```

---

## 7. CASOS QUE A TOOL NÃO RESOLVE BEM

### Variação muito específica não retorna match

Se IA chama `query_products({ search: "varão 6,0m bitola 08 a 10 cm MS" })`:
- Todos os 4 termos precisam aparecer no haystack
- Se algum estiver ligeiramente diferente (ex: "08-10" vs "08 a 10"), match falha
- Resultado: 0 itens

**Solução implementada (PR #235):** master prompt instrui IA a chamar query genérica e filtrar mentalmente os items retornados.

### Catálogo com nomes não-únicos sem variações estruturadas

Se Euca tivesse `name = "Varão 5,0m - Bitola 08 a 10 cm (MG)"` mas `var_1/var_2/var_3` vazios:
- Haystack tem tudo no nome
- Match funciona pra queries genéricas
- Mas IA não consegue filtrar mentalmente (não vê variações estruturadas)

**Recomendação:** preencher `var_1/var_2/var_3` quando há variações.

### Preço dinâmico por região

Se mesmo produto tem preços diferentes por UF (caso Euca: Varão 5m bitola 08 a 10 cm tem 27 preços diferentes):
- Cada combinação produto×UF é **linha separada** no catálogo
- `var_3` representa UF
- IA precisa perguntar UF antes de cotar preço

**Solução implementada (PR #235):** master prompt instrui IA a perguntar localização quando `var_3` é regional.

---

## 8. FALLBACK PARA DELIVERY ITEMS

Tool `query_delivery_items` (caixa Delivery Items) tem fallback automático pra Products:

```typescript
// Se delivery_items está vazia
if (!deliveryItemsBox || deliveryItemsBox.data.items.length === 0) {
  // Pega produtos com available_for_delivery="Sim" da caixa Products
  return filterProducts(productsBox.data.items, args)
    .filter(item => item.available_for_delivery === "Sim");
}
```

Tenant não precisa duplicar produtos em Delivery Items se já estão em Products marcados como `available_for_delivery="Sim"`.

---

## 9. PERFORMANCE E CUSTO

### Tokens por chamada

Tool `query_products` com 50 itens retorna ~2k-4k tokens. Sustentável pra mensagens conversacionais.

### Cache (Anthropic Claude)

System prompt grande (caixas pequenas inline + master prompt) fica em cache. Cache hit = 90% mais barato que cache miss.

Por isso compiler injeta caixas pequenas (Establishment, Hours, FAQ) — vão pro cache.

### Cobrança real (Sonnet 4.6, Euca Brasil)

22 mensagens IA, ~2.5k input por chamada, ~120 output, custo total R$15,24 = ~R$0,69/msg.

Com Haiku 4.5: ~R$0,11/msg (6x mais barato).

---

## 10. LIMITAÇÕES CONHECIDAS

### Sem ranking por score

Algoritmo retorna boolean (match/no match), não score. Se há 200 matches e limite 50, retorna os 50 primeiros na **ordem do Excel**, não por relevância.

**Implicação:** se as 50 primeiras linhas do Excel não cobrem a variação que cliente quer, IA vê dados parciais e pode dar resposta incompleta.

**Mitigação:** hint mostra variações disponíveis nos 50 retornados, IA pede refinamento.

### Sem cache de query

Cada chamada da tool processa o JSONB completo. Sem cache de results entre chamadas.

**Implicação:** chamar `query_products` 10 vezes seguidas com queries similares re-processa tudo.

**Mitigação:** master prompt instrui IA a reusar items do contexto entre turnos.

### Sem suporte a busca por preço

Tool não filtra por faixa de preço (ex: "produtos até R$50").

**Workaround:** IA pega items e filtra mentalmente.

---

## 11. SPRINT FUTURA (NÃO IMPLEMENTADA)

Ideias documentadas como possíveis melhorias:

- **Ranking por score** — Fuse.js ou similar, retornar items mais relevantes primeiro
- **Cache de result** — Redis ou similar pra queries similares no mesmo dia
- **Filtro por faixa de preço** — argumento `price_min`/`price_max`
- **Sinônimos** — "varão"/"vara"/"esteio" mapeados via thesaurus
- **Indexação Postgres** — `tsvector` + GIN index pra full-text search performático

---

**Fim do documento.**
