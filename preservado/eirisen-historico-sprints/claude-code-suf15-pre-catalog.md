# SUF15 — Pré-Catalog (Master Prompt + Fallback Tools)

> Sub-sprint curta antes da Sprint Catalog grande.
> 2 ajustes pequenos e independentes que destravam IA e preparam terreno.
> Estimativa: 3-4 horas.

---

## Contexto

Raio-x complementar (10/05/26) identificou 8 gaps das decisões novas. Dois são **quick wins** que cabem em sub-sprint isolada antes da Sprint Catalog:

1. **Gap 8** — Master prompt não declara textualmente quais tools a IA tem disponíveis
2. **Gap 2** — Tools sem padrão de fallback condicional

Ambos mergem separado, sem dependência entre si.

---

## Ajuste 1 — Master prompt declarando tools dinamicamente

### Problema atual

Tools (query_products, query_services, etc) são registradas no payload da API pro provider, mas o **system prompt em texto não menciona elas**. Resultado:
- IA às vezes inventa em vez de chamar tool
- IA não sabe priorizar tools quando o tenant tem múltiplas caixas preenchidas
- Performance subutilizada (Pedro notou que a IA do Vanderlei perguntou marca em vez de buscar no catálogo)

### Solução

Em `ai-reply/index.ts` (~linha 346, onde `buildSystemPrompt` é montado), adicionar um trecho dinâmico que lista quais caixas o tenant tem preenchidas e instrui IA a usar tools antes de inventar.

### Lógica

```ts
// Pseudocódigo do que adicionar
async function buildAvailableResourcesText(supabase, tenantId): Promise<string> {
  // 1. Busca persona_boxes ativas do tenant
  const { data: boxes } = await supabase
    .from("persona_boxes")
    .select("box_type")
    .eq("tenant_id", tenantId)
    .eq("is_active", true);

  if (!boxes || boxes.length === 0) return "";

  // 2. Mapeia box_type pra tool correspondente
  const toolMap: Record<string, { name: string; description: string }> = {
    products: {
      name: "query_products",
      description: "buscar produtos do catálogo",
    },
    services: {
      name: "query_services",
      description: "buscar serviços oferecidos",
    },
    delivery: {
      name: "query_delivery_items",  // ou query_products com fallback (Ajuste 2)
      description: "buscar itens disponíveis pra delivery",
    },
    events: {
      name: "query_events",
      description: "buscar pacotes de eventos",
    },
    faq: {
      name: "query_faq",
      description: "consultar perguntas frequentes",
    },
    objections: {
      name: "query_objections",
      description: "consultar como rebater objeções comuns",
    },
    team: {
      name: "search_team",
      description: "buscar colaboradores e profissionais",
    },
    forwards: {
      name: "search_forwards",
      description: "buscar contatos externos pra encaminhamento",
    },
  };

  // 3. Filtra só caixas que tem tool correspondente
  const availableTools = boxes
    .filter(b => toolMap[b.box_type])
    .map(b => toolMap[b.box_type]);

  if (availableTools.length === 0) return "";

  // 4. Monta texto declarativo
  const toolsList = availableTools
    .map(t => `- ${t.name}: ${t.description}`)
    .join("\n");

  return `

## RECURSOS DISPONÍVEIS

Este atendimento tem acesso aos seguintes recursos via tools:

${toolsList}

INSTRUÇÕES IMPORTANTES SOBRE USO DE TOOLS:
- SEMPRE use as tools antes de inventar informação sobre produtos, serviços, eventos, etc.
- Se não souber algo que pode estar no catálogo, chame a tool primeiro.
- Se a tool retornar vazio ou não encontrar, AÍ pode dizer ao cliente que não tem aquele item.
- Nunca afirme valores, disponibilidade, ou características de produtos/serviços sem antes consultar a tool correspondente.
- Quando cliente perguntar algo específico (preço, disponibilidade, características), chame a tool ANTES de responder.
`;
}

// Uso em buildSystemPrompt:
const availableResources = await buildAvailableResourcesText(supabase, tenant_id);
const systemPrompt = baseSystemPrompt + temporalParts.join(" ") + availableResources;
```

### Tratamento de tenants em modo manual

`persona_mode = 'manual'` significa que o tenant tem markdown direto em `system_prompt` em vez de blocos. Para esses, o trecho acima **não deve ser injetado** porque:
1. Não tem caixas preenchidas
2. O conteúdo já está dentro do system_prompt deles
3. As tools tradicionais provavelmente não retornariam nada

Verificação:
```ts
if (tenantConfig.persona_mode === "blocks") {
  // injeta availableResources
} else {
  // pula
}
```

### Critérios de aceite

- [ ] Função `buildAvailableResourcesText` criada em `_shared/` ou inline em `ai-reply`
- [ ] Texto injetado no system prompt SOMENTE para tenants em `persona_mode='blocks'`
- [ ] Lista de tools dinâmica baseada em `persona_boxes.box_type` ativos do tenant
- [ ] Tenant sem caixas ativas: não adiciona nada (return "")
- [ ] Smoke real: tenant Vanderlei (Construai) responde melhor após mudança — IA consulta tool em vez de inventar marca

---

## Ajuste 2 — Tool com fallback Delivery → Products

### Problema atual

Decisão de produto: caixa **Delivery Items** com fallback inteligente para Products quando vazia.

Hoje, tool `query_products` busca só na caixa Products. Não existe tool `query_delivery_items` nem lógica condicional.

### Solução

Criar tool `query_delivery_items` que:
1. Busca em `persona_boxes` com `box_type='delivery_items'` (caixa nova que Sprint Catalog vai criar — por enquanto vai retornar vazio)
2. Se vazia ou inexistente, busca em `persona_boxes` com `box_type='products'`, filtrando itens com `disponivel_pra_delivery=true`
3. Se Products também não tem o flag setado em nenhum item, retorna vazio
4. Retorna o array de items do catálogo

### Implementação

Local provável: `supabase/functions/ai-reply/tools/` ou inline no switch case de tools em `ai-reply/index.ts`.

```ts
async function queryDeliveryItems(
  supabase: SupabaseClient,
  tenantId: string,
  query: string,
  limit = 10
): Promise<DeliveryItemResult[]> {
  console.log(`[query-delivery-items] tenant=${tenantId} query="${query}"`);

  // 1. Tenta buscar em delivery_items (caixa nova)
  const { data: deliveryBox } = await supabase
    .from("persona_boxes")
    .select("data")
    .eq("tenant_id", tenantId)
    .eq("box_type", "delivery_items")
    .eq("is_active", true)
    .maybeSingle();

  if (deliveryBox?.data?.items?.length > 0) {
    console.log(`[query-delivery-items] using delivery_items box (${deliveryBox.data.items.length} items)`);
    return searchInItems(deliveryBox.data.items, query, limit);
  }

  // 2. Fallback: busca em products filtrado por disponivel_pra_delivery
  const { data: productsBox } = await supabase
    .from("persona_boxes")
    .select("data")
    .eq("tenant_id", tenantId)
    .eq("box_type", "products")
    .eq("is_active", true)
    .maybeSingle();

  if (!productsBox?.data?.items?.length) {
    console.log(`[query-delivery-items] no products box found`);
    return [];
  }

  // Filtra apenas items com disponivel_pra_delivery=true
  // OBS: o campo ainda não existe no schema atual de Products.
  // Sprint Catalog vai adicionar. Por enquanto, retorna vazio se nenhum item tem flag.
  const deliveryAvailable = productsBox.data.items.filter(
    (item: any) => item.disponivel_pra_delivery === true
  );

  if (deliveryAvailable.length === 0) {
    console.log(`[query-delivery-items] no products marked as available for delivery`);
    return [];
  }

  console.log(`[query-delivery-items] using products fallback (${deliveryAvailable.length} items)`);
  return searchInItems(deliveryAvailable, query, limit);
}

// Helper de busca (reusa a lógica de query_products atual ou cria nova)
function searchInItems(items: any[], query: string, limit: number): any[] {
  const q = query.toLowerCase().trim();
  if (!q) return items.slice(0, limit);
  return items
    .filter(item => 
      item.name?.toLowerCase().includes(q) ||
      item.description?.toLowerCase().includes(q) ||
      item.category?.toLowerCase().includes(q)
    )
    .slice(0, limit);
}
```

### Registrar a tool

No switch case de tools em `ai-reply/index.ts`:

```ts
case "query_delivery_items":
  result = await queryDeliveryItems(
    supabase,
    tenant_id,
    toolUse.input.query,
    toolUse.input.limit ?? 10
  );
  break;
```

E na declaração de tools (que vai pra API):

```ts
{
  name: "query_delivery_items",
  description: "Busca itens disponíveis pra delivery. Usa caixa Delivery Items se preenchida, senão busca em Products filtrando os marcados como disponíveis para delivery.",
  input_schema: {
    type: "object",
    properties: {
      query: { type: "string", description: "termo de busca" },
      limit: { type: "number", default: 10 }
    },
    required: ["query"]
  }
}
```

### Critérios de aceite

- [ ] Tool `query_delivery_items` registrada no payload da API
- [ ] Lógica de fallback testada: delivery_items vazia → busca em products filtered
- [ ] Logs distintos `[query-delivery-items]` mostrando qual fonte foi usada
- [ ] Não altera comportamento de `query_products` (continua funcionando como antes)
- [ ] Build/tsc/test verde

---

## Plano de execução

### Etapa 1 — Confirmação (sem codar)

Antes de codar, confirmar:
1. Caminho exato de `buildSystemPrompt` em `_shared/` (raio-x mencionou linha 346)
2. Como `tenantConfig.persona_mode` é lido hoje
3. Onde tools são registradas no payload da API (raio-x mencionou switch case)
4. Como `query_products` busca hoje (String.includes? slice?)

Reportar findings antes de prosseguir.

### Etapa 2 — Implementação Ajuste 1

Helper `buildAvailableResourcesText`. Injeção condicional. Build/tsc/test verde.

### Etapa 3 — Implementação Ajuste 2

Tool `query_delivery_items`. Registro na lista de tools. Switch case. Logs.

### Etapa 4 — Smoke

**Smoke do Ajuste 1:**
1. Tenant em modo blocks com Products preenchido
2. Cliente pergunta sobre produto
3. IA chama tool antes de inventar (verificar nos logs)
4. SQL: contar tool_uses em conversas recentes

**Smoke do Ajuste 2:**
1. Tenant sem caixa delivery_items mas com Products
2. Adicionar flag `disponivel_pra_delivery=true` manualmente em alguns produtos via SQL
3. Cliente pergunta sobre delivery
4. IA chama `query_delivery_items` e retorna os marcados
5. Logs `[query-delivery-items] using products fallback`

### Etapa 5 — Não-regressão

- Tenants em modo manual: prompt não muda (sem availableResources injetado)
- Tenants sem caixas: prompt não muda
- `query_products` continua funcionando idêntico
- Outras tools intocadas

---

## Critérios de aceite SUF15

- [ ] Build/tsc/vitest verde
- [ ] Smoke real do Ajuste 1 confirmado em tenant Vanderlei (Construai)
- [ ] Smoke real do Ajuste 2 confirmado com tenant teste
- [ ] PR linkando este prompt + diff + smoke real
- [ ] Logs distintos `[query-delivery-items]` aparecendo no provider-webhook

---

## Pós-merge

```bash
gh pr merge <PR> --squash --delete-branch
git checkout main && git pull origin main
supabase functions deploy ai-reply
git push origin main
```

Sem migration. Mudanças só em código de edges.

---

## Branch e PR

- Branch: `suf15-pre-catalog`
- PR título: `feat(ai): master prompt declarando tools + tool query_delivery_items com fallback (SUF15)`
- PR descrição:
  - Link pra este prompt
  - Findings da Etapa 1
  - Diff dos 2 ajustes
  - Smoke real

---

## Lembretes operacionais

- `grep -n` antes/depois de `replace_all`
- `EdgeRuntime.waitUntil` se algo for em background (não deve ter neste sprint)
- Logs distintos: `[available-resources]` e `[query-delivery-items]`
- Sem migration nesta sprint
- Não tocar lógica de outras tools — isolar mudanças
