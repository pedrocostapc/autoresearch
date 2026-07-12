# PR6 — FAQ + Objections + Excel (Sprint Catalog Onda 2)

> **2 caixas multi-item juntas.** Estruturas idênticas (3 blocos / 10 campos / 2 obrigatórios cada). Reusa 100% da infra genérica do PR5.
>
> Estimativa: ~4-6h.
> Branch: `catalog-pr6-faq-objections`

---

## Contexto

PR5 fechou com o `<MultiItemListEditor>` + `<BoxFormMultiItem>` genéricos. PR6 só **adiciona 2 schemas + 2 tools + 2 wrappers**. Sem refator estrutural.

Decidimos juntar FAQ + Objections (memory item #21) porque:
- Mesma estrutura: 3 blocos × ~10 campos × 2 obrigatórios cada
- Mesmo padrão (Pergunta + Resposta + Direcionamento IA)
- Diferença é só semântica
- Code já generalizou tudo no PR5

---

## Schemas finais

### FAQ (10 campos / 3 blocos)

| Bloco | Campo | Tipo |
|---|---|---|
| **Pergunta** | question | text ✅ |
| | question_variants | csv |
| | category | text |
| | tags | csv |
| **Resposta** | answer | textarea ✅ |
| | short_answer | text |
| **Direcionamento IA** | confidence | single_choice (Alta/Média/Baixa) |
| | escalate_to | text (link futuro Team) |
| | ai_notes | textarea |
| | last_updated | date |

### Objections (10 campos / 3 blocos)

| Bloco | Campo | Tipo |
|---|---|---|
| **Objeção** | objection | text ✅ |
| | objection_variants | csv |
| | category | single_choice (Preço/Qualidade/Entrega/Concorrência/Confiança/Outro) |
| **Resposta** | rebuttal | textarea ✅ |
| | main_argument | text |
| | social_proof | textarea |
| **Direcionamento IA** | dont_insist_when | textarea |
| | escalate_if_persists | boolean |
| | responsible_professional | text |
| | ai_notes | textarea |

---

## Etapa 1 — Confirmações antes de codar

### A. Schemas atuais

```bash
grep -n "FAQSchema\|FaqSchema\|ObjectionsSchema\|formatFAQ\|formatObjections" \
  src/features/ai-settings/lib/personaBoxSchemas.ts \
  supabase/functions/_shared/persona-compiler.ts
```

Reportar:
- Schema Zod atual de FAQ (copia literal)
- Schema Zod atual de Objections (copia literal)
- Compiladores `formatFAQ` e `formatObjections` atuais
- Se hoje tem tools `query_faq` ou `query_objections` em `_shared/persona-tools.ts`

### B. Volume real em produção

```sql
SELECT box_type, COUNT(*), 
       AVG(jsonb_array_length(COALESCE(data->'items', '[]'::jsonb)))::int AS avg_items,
       MAX(jsonb_array_length(COALESCE(data->'items', '[]'::jsonb))) AS max_items
FROM persona_boxes 
WHERE box_type IN ('faq', 'objections') AND is_active = true
GROUP BY box_type;
```

Reportar números (Pedro confirma antes do DELETE).

### C. Decisões pendentes

#### C1. Tipo `date` no QuestionBlock

FAQ tem campo `last_updated` (date). Existe `time` mas não `date`. Adicionar?

**Recomendação:** Sim. `<Input type="date">`. Trivial. Reusável pra outras caixas no futuro (validade de cupom, etc).

#### C2. Tools de FAQ e Objections

Diferente de Products/Services, FAQ e Objections são **mais úteis sem tool fuzzy**:

- **FAQ:** IA recebe lista (10-30 itens é normal) e usa direto pra responder dúvidas comuns. Tool útil só se passar de 50 perguntas.
- **Objections:** IA precisa "estar preparada" — geralmente <20 objeções. Lista direto no compiler é melhor.

**Opção A — Sem tools, despeja no compiler** (recomendado):
- `formatFAQ` lista todas as perguntas + respostas resumidas
- `formatObjections` lista todas as objeções + argumentos principais
- Funciona até ~50 itens por caixa sem peso significativo

**Opção B — Tools `query_faq` e `query_objections`** (igual products/services):
- Compiler só mostra count + sample
- IA chama tool quando precisar
- Útil se cliente tiver 100+ FAQs

**Recomendação Opção A.** Simples, IA tem contexto sempre, sem round-trip de tool. Volume típico é baixo.

Code confirma ou propõe alternativa.

#### C3. Validação cross-field

FAQ tem `confidence: Alta/Média/Baixa`. Se confidence = "Baixa", faz sentido obrigar `escalate_to` preenchido?

**Recomendação:** **não validar cross-field**. Cliente pode ter FAQ com confidence Baixa e ainda querer responder direto (com aviso pra IA). Não força.

#### C4. DELETE manual

Pedro vai rodar (separado em 2 queries por caixa).

---

## Aguarda OK antes de prosseguir.

---

## Etapa 2 — Schemas declarativos

Adicionar em `_shared/box-schemas.ts`:

```ts
export const FAQ_SCHEMA: BoxSchemaDef = {
  boxType: "faq",
  label: "Perguntas frequentes",
  cardinality: "multi_item",
  hasExcel: true,
  blocks: [
    {
      title: "Pergunta",
      fields: [
        { field: "question", question: "Pergunta", type: "text", required: true },
        { field: "question_variants", question: "Variações da pergunta", type: "csv", helper: "Cliente pode perguntar de formas diferentes — separe por vírgula" },
        { field: "category", question: "Categoria", type: "text", helper: "Ex: Pagamento, Entrega, Produto" },
        { field: "tags", question: "Tags", type: "csv" },
      ],
    },
    {
      title: "Resposta",
      fields: [
        { field: "answer", question: "Resposta completa", type: "textarea", required: true },
        { field: "short_answer", question: "Resposta resumida (1 linha)", type: "text" },
      ],
    },
    {
      title: "Direcionamento IA",
      fields: [
        { field: "confidence", question: "Confiança nessa resposta", type: "single_choice", options: ["Alta", "Média", "Baixa"] },
        { field: "escalate_to", question: "Encaminhar pra alguém depois?", type: "text", helper: "Nome de quem está em Team" },
        { field: "ai_notes", question: "Observações pra IA", type: "textarea" },
        { field: "last_updated", question: "Atualizado em", type: "date" },
      ],
    },
  ],
};

export const OBJECTIONS_SCHEMA: BoxSchemaDef = {
  boxType: "objections",
  label: "Objeções comuns",
  cardinality: "multi_item",
  hasExcel: true,
  blocks: [
    {
      title: "Objeção",
      fields: [
        { field: "objection", question: "Objeção do cliente", type: "text", required: true },
        { field: "objection_variants", question: "Variações de como aparece", type: "csv" },
        { field: "category", question: "Categoria", type: "single_choice", options: ["Preço", "Qualidade", "Entrega", "Concorrência", "Confiança", "Outro"] },
      ],
    },
    {
      title: "Resposta",
      fields: [
        { field: "rebuttal", question: "Como rebater", type: "textarea", required: true },
        { field: "main_argument", question: "Argumento principal", type: "text" },
        { field: "social_proof", question: "Prova social / case", type: "textarea", helper: "Exemplo de cliente satisfeito que pode ser citado" },
      ],
    },
    {
      title: "Direcionamento IA",
      fields: [
        { field: "dont_insist_when", question: "Quando NÃO insistir", type: "textarea" },
        { field: "escalate_if_persists", question: "Encaminhar pra humano se persistir?", type: "boolean" },
        { field: "responsible_professional", question: "Profissional responsável", type: "text" },
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
  services: SERVICES_SCHEMA,
  faq: FAQ_SCHEMA,            // NOVO
  objections: OBJECTIONS_SCHEMA,  // NOVO
};
```

---

## Etapa 3 — QuestionBlock (tipo `date`)

Adicionar `date` no FieldType union. No render:

```tsx
case "date":
  return (
    <Input
      type="date"
      value={value ?? ""}
      onChange={(e) => onChange(e.target.value)}
    />
  );
```

`isFieldEmpty` reconhece string vazia como vazia (default já cobre).

---

## Etapa 4 — Forms (wrappers ~12 linhas cada)

```tsx
// FaqForm.tsx
export function FaqForm({ items, onChange, ...rest }: FaqFormProps) {
  return (
    <BoxFormMultiItem
      boxType="faq"
      items={items}
      onChange={onChange}
      modes={["manual", "excel"]}
    />
  );
}

// ObjectionsForm.tsx (idem)
```

Adicionar entries em `AbaBlocos.tsx` (seção ATENDIMENTO) e `EditBoxDialog.tsx`.

---

## Etapa 5 — Compilers

### `formatFAQ`

Despeja todas as perguntas no contexto (recomendação C2 Opção A):

```ts
function formatFAQ(box: PersonaBox | null): string {
  if (!box?.data?.items?.length) return "";
  
  const items = box.data.items;
  const lines = items.map((item: any) => {
    const q = item.question;
    const a = item.short_answer || item.answer;
    return `**Q: ${q}**\nA: ${a}`;
  });
  
  return `## Perguntas frequentes\n\n${lines.join("\n\n")}`;
}
```

### `formatObjections`

```ts
function formatObjections(box: PersonaBox | null): string {
  if (!box?.data?.items?.length) return "";
  
  const items = box.data.items;
  const lines = items.map((item: any) => {
    const obj = item.objection;
    const reb = item.main_argument || item.rebuttal;
    return `- Cliente diz "${obj}" → ${reb}`;
  });
  
  return `## Como lidar com objeções comuns\n\n${lines.join("\n")}`;
}
```

Ambos usam **resumo** (`short_answer`/`main_argument`) se disponível, fallback pro completo. Reduz tokens sem perder conteúdo crítico.

### Tool calls?

**Não cria tools.** FAQ e Objections vão direto no contexto.

Se no futuro algum tenant passar de 50 perguntas/objeções, aí avalia tool. Por enquanto não.

---

## Etapa 6 — Cleanup + deploy

### Antes do deploy

Pedro roda separado:

**1) Volume FAQ:**
```sql
SELECT 
  tenant_id,
  jsonb_array_length(COALESCE(data->'items', '[]'::jsonb)) AS items
FROM persona_boxes
WHERE box_type = 'faq' AND is_active = true;
```

**2) Volume Objections:**
```sql
SELECT 
  tenant_id,
  jsonb_array_length(COALESCE(data->'items', '[]'::jsonb)) AS items
FROM persona_boxes
WHERE box_type = 'objections' AND is_active = true;
```

**3) DELETE FAQ:**
```sql
DELETE FROM persona_boxes WHERE box_type = 'faq';
```

**4) DELETE Objections:**
```sql
DELETE FROM persona_boxes WHERE box_type = 'objections';
```

**5) Confirma vazio:**
```sql
SELECT box_type, COUNT(*) FROM persona_boxes 
WHERE box_type IN ('faq', 'objections')
GROUP BY box_type;
```

### Deploy

```bash
gh pr merge <PR> --squash --delete-branch
git checkout main && git pull origin main
supabase functions deploy ai-reply  # compiler novo
git push origin main                 # Lovable build
```

Edges genéricas (`download-box-template` + `import-box-excel`) leem registry — sem redeploy. Mas pode redeployar `download-box-template` opcionalmente pra Excel ter exemplos de FAQ/Objections.

### Validação pós-deploy

1. Cards "Perguntas frequentes" e "Objeções comuns" aparecem na seção ATENDIMENTO
2. Manual: adicionar 1 FAQ + 1 Objection
3. Excel: baixar modelo de cada, preencher 3 itens, importar
4. Não-regressão Products + Services + outros

---

## Critérios de aceite

- [ ] Etapa 1 confirmação aprovada
- [ ] FAQ_SCHEMA + OBJECTIONS_SCHEMA em box-schemas.ts
- [ ] Tipo `date` no QuestionBlock
- [ ] FaqForm + ObjectionsForm wrappers ~12 linhas cada
- [ ] formatFAQ + formatObjections (despejam direto no contexto, sem tool)
- [ ] generateExamples() ganha entries pra faq + objections
- [ ] Build/tsc/vitest verde
- [ ] Pedro confirma DELETE
- [ ] PR description anota: "FAQ + Objections juntos. Sem tools — despeja no contexto. Volume típico baixo."

---

## Restrições

- ❌ Sem mexer em outras caixas
- ❌ Sem criar tools `query_faq` / `query_objections` (volume não justifica)
- ❌ Smoke automático
- ✅ Mostra diff antes do commit
- ✅ Branch: `catalog-pr6-faq-objections`
- ✅ PR título: `feat(catalog): FAQ + Objections + Excel (PR6)`

---

## Pós-merge — Próximo: PR7 (Team + Excel)

Memory item #17 menciona modelo de **21 campos** pronto pra Team (modelo Pedro). Caixa Team é a mais complexa de Atendimento — alimenta muitas outras (link futuro com Services, Forwards, Agenda).

PR7 deve ter ~6-8h pelo schema maior + integração com `tem_agenda_propria` (memory item #20).

---

## O que NÃO fazer neste PR

- ❌ Tools de FAQ/Objections (volume não justifica)
- ❌ Team, Forwards, Delivery, Events, Custom (PRs sequenciais)
- ❌ Templates por nicho
- ❌ Validação cross-field (confidence/escalate_to)
