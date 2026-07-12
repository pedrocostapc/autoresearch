# PR8 — Forwards + Excel (Sprint Catalog Onda 2)

> **Caixa Forwards — contatos externos** (parceiros, fornecedores, técnicos terceirizados). Schema 14 campos / 4 blocos. Estrutura similar a Team mas semântica diferente.
>
> Estimativa: ~3-4h (reusa 100% infra).
> Branch: `catalog-pr8-forwards-excel`

---

## Contexto

Team (PR7) = colaboradores **internos**. Forwards = contatos **externos**.

Casos de uso:
- Cliente quer comprar peça que loja não tem → IA forwarda pra fornecedor parceiro
- Cliente precisa de serviço terceirizado (instalação, técnico) → IA forwarda
- Vendedor parceiro de outra empresa que tem comissão acordada

**Diferença crítica de Team:**
- 2 obrigatórios (Nome + WhatsApp), não 1
- Tipo é dropdown fixo (Vendedor parceiro / Fornecedor / Técnico externo / Outro)
- Tem campo `previous_message_template` — IA usa pra mandar primeira mensagem padrão pro contato externo

Reusa 100% da infra de PR5+PR6+PR7.

---

## Schema final Forwards (14 campos / 4 blocos)

| Bloco | Campo | Tipo |
|---|---|---|
| **1. Identificação** | name | text ✅ |
| | type | single_choice (Vendedor parceiro/Fornecedor/Técnico externo/Outro) |
| | company | text |
| **2. Contato** | whatsapp | text ✅ |
| | phone | text |
| | email | email |
| | website | url |
| **3. Especialidade** | description | text (o que faz) |
| | category | text |
| | geographic_coverage | text |
| **4. Direcionamento IA** | trigger_keywords | csv |
| | message_template | textarea (mensagem prévia) |
| | ai_can_forward | single_choice (Sim/Confirmar/Não) |
| | ai_notes | textarea |

**14 campos. 2 obrigatórios: Nome + WhatsApp.**

---

## Etapa 1 — Confirmações antes de codar

### A. Schema atual de Forwards

```bash
grep -n "ForwardsSchema\|formatForwards" \
  src/features/ai-settings/lib/personaBoxSchemas.ts \
  supabase/functions/_shared/persona-compiler.ts
```

Reportar:
- Schema Zod atual (copia literal)
- Estrutura do data: `entries[]`, `members[]`, `items[]`, ou outra?
- Como `formatForwards` é implementado hoje
- Se há tool `query_forwards` em produção

### B. Volume real

```sql
SELECT 
  tenant_id,
  jsonb_array_length(COALESCE(data->'entries', data->'members', data->'items', '[]'::jsonb)) AS items
FROM persona_boxes 
WHERE box_type = 'forwards' AND is_active = true;
```

### C. Decisões pendentes

#### C1. Tool `query_forwards` — criar?

Volume típico: 5-30 contatos externos.

**Opção A — Sem tool, despeja no compiler** (igual FAQ/Objections): volume baixo justifica. Compiler lista todos os forwards no contexto. IA usa direto.

**Opção B — Com tool** (igual Team/Products/Services): IA chama `query_forwards("instalação")` pra achar técnicos.

**Recomendação:** **Opção B (com tool).** Razões:
- Buscas naturais ("alguém que faz instalação?", "fornecedor de tinta?")
- Mesmo padrão de Team — facilita IA
- Volume pode crescer se cliente tiver muitos parceiros
- Custo mínimo (infra já existe)

#### C2. Schema retorno tool

10 campos:
```ts
{
  name, type, company,
  whatsapp,        // sempre, é dado público pra contato
  phone, email, website,
  description, category, geographic_coverage,
  message_template, // IA usa pra enviar primeira msg
  ai_can_forward, trigger_keywords
}
```

**Privacidade:** Diferente de Team (mobile pessoal), em Forwards o WhatsApp é dado **público de empresa**. Não precisa omissão condicional.

**Mas:** se `ai_can_forward = "Não"`, faz sentido ainda retornar o WhatsApp? IA não pode encaminhar mas ainda informa o cliente?

**Recomendação:** **Retorna tudo sempre.** `ai_can_forward = "Não"` significa "IA não passa contato direto pro cliente automaticamente — atendente humano decide". Mas IA ainda precisa do WhatsApp internamente pra contextualizar (ex: "tem fornecedor X mas precisa confirmar com gerente"). Comportamento diferente de Team (mobile pessoal omitido).

Code confirma.

#### C3. Haystack do fuzzy

```
name + company + description + category + trigger_keywords + geographic_coverage
```

#### C4. Required validation no Excel

Schema declara 2 required (`name` + `whatsapp`). Validação `<BoxFormMultiItem>` (PR6) já bloqueia save Manual se vazio. Edge import-box-excel valida via Zod. **Sem mudança necessária.**

Confirmar.

#### C5. message_template — texto livre ou estruturado?

Pedro tem padrão de "MSG3 copiável" no caso Vanderlei (memory item da análise do prompt). É um texto pronto pra IA mandar pro contato externo.

Exemplo:
```
Olá [parceiro]! Sou da Construbase. Cliente [nome_cliente] está interessado em [categoria]. Pode atendê-lo? Aguardo retorno.
```

**Aceita variáveis** `[nome_cliente]`, `[categoria]`? Ou só texto literal?

**Recomendação:** **Texto livre** (textarea) com helper sugerindo variáveis. IA interpreta naturalmente. Não cria sistema de templating com placeholders rigorosos.

Helper:
```
Ex: "Olá [parceiro]! Sou da Construbase, tenho cliente interessado em [categoria]. Pode atender?". Pode usar variáveis livres — IA vai substituir contextualmente.
```

#### C6. DELETE manual

Pedro vai rodar.

---

## Aguarda OK antes de prosseguir.

---

## Etapa 2 — Schema declarativo

```ts
export const FORWARDS_SCHEMA: BoxSchemaDef = {
  boxType: "forwards",
  label: "Encaminhamentos externos",
  cardinality: "multi_item",
  hasExcel: true,
  blocks: [
    {
      title: "Identificação",
      fields: [
        { field: "name", question: "Nome / Razão social", type: "text", required: true },
        { field: "type", question: "Tipo", type: "single_choice", options: ["Vendedor parceiro", "Fornecedor", "Técnico externo", "Outro"] },
        { field: "company", question: "Empresa", type: "text", helper: "Se for diferente do nome (ex: pessoa física trabalhando como autônomo)" },
      ],
    },
    {
      title: "Contato",
      fields: [
        { field: "whatsapp", question: "WhatsApp", type: "text", required: true, placeholder: "+5538999999999" },
        { field: "phone", question: "Telefone fixo", type: "text" },
        { field: "email", question: "Email", type: "email" },
        { field: "website", question: "Site", type: "url" },
      ],
    },
    {
      title: "Especialidade",
      fields: [
        { field: "description", question: "O que faz", type: "text", helper: "Em uma linha — IA usa pra direcionar quando cliente precisa do serviço" },
        { field: "category", question: "Categoria", type: "text" },
        { field: "geographic_coverage", question: "Cobertura geográfica", type: "text", helper: "Cidades, raio km, ou estado" },
      ],
    },
    {
      title: "Direcionamento IA",
      fields: [
        { field: "trigger_keywords", question: "Quando direcionar (palavras-chave)", type: "csv", helper: "IA procura essas palavras na mensagem do cliente" },
        { field: "message_template", question: "Mensagem prévia (template)", type: "textarea", helper: "Mensagem pronta que IA pode mandar pro contato. Ex: 'Olá! Sou da [empresa], tenho cliente interessado em [serviço]. Pode atender?'" },
        { field: "ai_can_forward", question: "IA pode encaminhar direto?", type: "single_choice", options: ["Sim", "Confirmar", "Não"], helper: "Sim: IA passa contato direto pro cliente. Confirmar: IA pergunta antes. Não: só atendente humano decide." },
        { field: "ai_notes", question: "Observações pra IA", type: "textarea" },
      ],
    },
  ],
};

// Adicionar ao registry
export const BOX_SCHEMAS: Record<string, BoxSchemaDef> = {
  // ... anteriores
  forwards: FORWARDS_SCHEMA,  // NOVO
};
```

---

## Etapa 3 — ForwardsForm (wrapper)

```tsx
export function ForwardsForm({ items, onChange, ...rest }: ForwardsFormProps) {
  return (
    <BoxFormMultiItem
      boxType="forwards"
      titleField="name"  // card mostra Nome no cabeçalho
      items={items}
      onChange={onChange}
      modes={["manual", "excel"]}
    />
  );
}
```

Adicionar entries em `AbaBlocos.tsx` (seção ATENDIMENTO) e `EditBoxDialog.tsx`.

---

## Etapa 4 — Tool `query_forwards`

```ts
export async function queryForwards(supabase, tenantId, query: string, limit = 10) {
  const { data: box } = await supabase
    .from("persona_boxes")
    .select("data")
    .eq("tenant_id", tenantId)
    .eq("box_type", "forwards")
    .eq("is_active", true)
    .single();
  
  if (!box?.data?.items) return [];
  
  const items = box.data.items as any[];
  const filtered = filterForwards(items, query);
  
  return filtered.slice(0, limit).map(item => ({
    name: item.name,
    type: item.type,
    company: item.company,
    whatsapp: item.whatsapp,  // sempre — dado público
    phone: item.phone,
    email: item.email,
    website: item.website,
    description: item.description,
    category: item.category,
    geographic_coverage: item.geographic_coverage,
    message_template: item.message_template,
    ai_can_forward: item.ai_can_forward,
    trigger_keywords: item.trigger_keywords,
  }));
}

function filterForwards(items: any[], query: string): any[] {
  if (!query) return items;
  const q = query.toLowerCase();
  return items.filter(item => {
    const haystack = [
      item.name,
      item.company,
      item.description,
      item.category,
      item.geographic_coverage,
      ...(item.trigger_keywords || []),
    ].filter(Boolean).join(" ").toLowerCase();
    return haystack.includes(q);
  });
}
```

Registrar em `BOX_TO_TOOL_MAP`.

---

## Etapa 5 — Compiler `summarizeForwards`

```ts
function summarizeForwards(box: PersonaBox | null): string {
  if (!box?.data?.items?.length) return "";
  
  const items = box.data.items;
  const sample = items.slice(0, 5).map((i: any) => 
    i.category ? `${i.name} (${i.category})` : i.name
  ).join(", ");
  
  return `## Contatos externos pra encaminhamento

Você tem acesso a ${items.length} contatos externos (parceiros, fornecedores, técnicos). Use a tool \`query_forwards(query)\` pra buscar quando o cliente precisar de algo que não fazemos internamente.

${sample ? `Exemplos: ${sample}` : ""}`;
}
```

---

## Etapa 6 — Excel template + import

Adicionar em `generateExamples()`:

```ts
if (boxType === "forwards") {
  return [
    ["MotoRápido Entregas", "Vendedor parceiro", "MotoRápido LTDA", "+5538999111222", "(38) 3749-5555", "contato@motorapido.com", "https://motorapido.com", "Entrega expressa de pequenos volumes", "Logística", "Pirapora e raio 30km", "entrega rápida, motoboy, urgente", "Olá! Sou da [empresa], cliente precisa de entrega expressa de [item]. Pode atender hoje?", "Sim", "Comissão 10% no primeiro pedido"],
    ["João Silva (técnico)", "Técnico externo", "MR Reformas", "+5538998222333", "", "joaomr@gmail.com", "", "Instalação de pisos e azulejos", "Construção", "Pirapora", "instalação, mão de obra, pedreiro, azulejista", "Olá João! Cliente da Construbase quer instalar [tipo de revestimento] em [endereço]. Disponível?", "Confirmar", "Profissional próprio, não exclusivo"],
  ];
}
```

`buildInstructions()` ganha dicas Forwards:

```
- Tipo: Vendedor parceiro / Fornecedor / Técnico externo / Outro
- WhatsApp obrigatório (E.164 preferido: +5538999999999)
- Mensagem prévia: template livre, IA substitui variáveis contextualmente
- IA pode encaminhar: Sim (passa contato direto), Confirmar (pergunta antes), Não (só atendente humano)
```

---

## Etapa 7 — Cleanup + deploy

### Antes do deploy

**1) Volume:**
```sql
SELECT 
  tenant_id,
  jsonb_array_length(COALESCE(data->'entries', data->'members', data->'items', '[]'::jsonb)) AS items
FROM persona_boxes
WHERE box_type = 'forwards' AND is_active = true;
```

**2) DELETE:**
```sql
DELETE FROM persona_boxes WHERE box_type = 'forwards';
```

**3) Confirma:**
```sql
SELECT COUNT(*) FROM persona_boxes WHERE box_type = 'forwards';
```

### Deploy

```bash
gh pr merge <PR> --squash --delete-branch
git checkout main && git pull origin main
supabase functions deploy ai-reply
git push origin main
```

Edge `download-box-template` redeploy opcional pra exemplos.

### Validação pós-deploy

1. Card "Encaminhamentos externos" aparece na seção ATENDIMENTO
2. Modo Manual: adicionar 1 forward completo (Nome + WhatsApp obrigatórios)
3. Validação required: deixa Nome ou WhatsApp vazio → toast bloqueia (PR6 herdado)
4. Card colapsado mostra `name`
5. Modo Excel: baixa modelo, valida 14 colunas + 2 exemplos (MotoRápido + João Silva)
6. Sobe Excel teste com 3 forwards
7. **Não-regressão:** Products + Services + FAQ + Objections + Team OK

---

## Critérios de aceite

- [ ] Etapa 1 confirmação aprovada
- [ ] FORWARDS_SCHEMA em box-schemas.ts (14 campos, 4 blocos, 2 required)
- [ ] ForwardsForm wrapper ~12 linhas com `titleField="name"`
- [ ] Tool `query_forwards` com fuzzy haystack 6 fontes
- [ ] Tool retorna whatsapp sempre (sem privacidade condicional, diferente de Team)
- [ ] summarizeForwards (count + sample, não despeja items)
- [ ] generateExamples + buildInstructions ganham entries pra forwards
- [ ] Build/tsc/vitest verde
- [ ] Pedro confirma DELETE
- [ ] PR description anota: "Forwards = externos (público). Diferente de Team (interno, privacidade mobile)."

---

## Restrições

- ❌ Sem refator estrutural (toda infra de PR5-7)
- ❌ Sem cross-field validation
- ❌ Sem sistema de templating rigoroso pra `message_template` (texto livre)
- ❌ Sem mexer em Team (não confundir interno vs externo)
- ✅ Mostra diff antes do commit
- ✅ Branch: `catalog-pr8-forwards-excel`
- ✅ PR título: `feat(catalog): Forwards + Excel + tool query_forwards (PR8)`

---

## Pós-merge — Próximo: PR9 (Delivery 3 caixas)

PR9 é mais pesado. **3 caixas em 1 PR**:
- Delivery Items (multi-item Excel, schema idêntico a Products + flag delivery)
- Delivery Areas (multi-item Excel, bairros/CEPs/taxas)
- Delivery Config (singleton, perguntas: pedido mínimo, horário delivery, políticas)

Memory item #14 cobre essa decisão. Estimativa ~6-8h.

---

## O que NÃO fazer neste PR

- ❌ Delivery, Events, Custom (sequencial)
- ❌ Sistema de comissão/repasse pra parceiros (futuro talvez)
- ❌ Templating rigoroso de message_template
- ❌ Privacidade condicional do WhatsApp (Forwards = público)
