# PR11 — Custom + Cleanup final (Sprint Catalog Onda 2)

> **ÚLTIMO PR DA SPRINT CATALOG.** Caixa Custom (texto livre) + cleanup final + documento de status fechando 11 PRs.
>
> Estimativa: ~3-4h.
> Branch: `catalog-pr11-custom`

---

## Contexto

Sprint Catalog em fechamento. Após PR10 mergear, falta só **Custom** — caixa "lixo" pra coisas que não cabem nas outras 16.

Casos de uso:
- Cliente quer documentar política específica (ex: "Atendimento bilíngue após 18h")
- Notas internas sobre fornecedores que não cabem em Forwards
- Procedimento específico do negócio (ex: como lidar com cliente VIP)
- Qualquer informação livre que cliente queira que IA tenha acesso

Estrutura: **multi-row livre**. Cliente cria N entradas, cada uma com Título + Conteúdo.

---

## Schema final Custom (2 campos, multi-row)

| Campo | Tipo | Obrigatório |
|---|---|---|
| **title** | text | ✅ |
| **content** | textarea (markdown) | ✅ |

Total: 2 campos. Ambos obrigatórios.

**Cap de tokens:** 4000 tokens somados de todas as entries (limite atual mantido). Sem Excel (texto livre), sem tool (vai direto no contexto).

---

## Etapa 1 — Confirmações antes de codar

### A. Schema atual de Custom

```bash
grep -n "CustomSchema\|formatCustom\|CustomEntry" \
  src/features/ai-settings/lib/personaBoxSchemas.ts \
  supabase/functions/_shared/persona-compiler.ts
```

Reportar:
- Schema Zod atual (copia literal)
- Estrutura do data: `entries[]`, `items[]`, `rows[]`?
- Como `formatCustom` é implementado hoje
- Cap de tokens onde fica (4000 tokens somados)

### B. UI atual CustomForm

```bash
grep -n "CustomForm" src/features/ai-settings/components/blocos/forms/
```

Reportar:
- Componente atual
- Se já é multi-row simples ou precisa refator
- Editor existente (markdown? texto puro?)

### C. Volume real

```sql
SELECT 
  tenant_id,
  jsonb_array_length(COALESCE(data->'entries', data->'items', data->'rows', '[]'::jsonb)) AS items
FROM persona_boxes
WHERE box_type = 'custom' AND is_active = true;
```

### D. Cardinality `multi_row`

Já existe no enum? Foi reservada no PR1 ou precisa adicionar agora?

```bash
grep -n "multi_row" supabase/functions/_shared/box-schemas.ts
```

### E. Decisões pendentes

#### E1. Migração estrutura `entries[]` ou `items[]`?

Padrão Sprint Catalog é `items[]` (Products/Services/FAQ/Objections/Team/Forwards/Delivery Items/Delivery Areas usam).

**Recomendação:** **`items[]`** pra consistência. Mesmo `<MultiItemListEditor>` ou variação simples pode renderizar.

#### E2. Renderização — `<MultiItemListEditor>` ou componente simples?

Custom tem só 2 campos (title + content). Não precisa accordions de blocks.

**Opções:**

**Opção A — Reusa `<MultiItemListEditor>` com schema declarativo de 1 bloco**

```ts
export const CUSTOM_SCHEMA: BoxSchemaDef = {
  boxType: "custom",
  label: "Conteúdo personalizado",
  cardinality: "multi_row",
  hasExcel: false,
  blocks: [
    {
      title: "Entrada",
      fields: [
        { field: "title", question: "Título", type: "text", required: true },
        { field: "content", question: "Conteúdo", type: "textarea", required: true },
      ],
    },
  ],
};
```

Card colapsado mostra `title`. Expansão mostra os 2 campos.

**Opção B — Componente próprio `<CustomEntriesEditor>`**

Editor simples sem accordions. Lista flat de cards com 2 inputs cada.

**Recomendação: Opção A.** Razões:
- Reusa toda infra
- Consistência visual com outras caixas multi_item
- Sem código novo
- Cliente entende pattern (igual outras caixas)

Code aceita ou propõe alternativa.

#### E3. Cap de tokens — onde validar?

Hoje tem cap de 4000 tokens somados. Onde fica?

**Opções:**
- Front: bloqueia save se passar (UX preventiva)
- Backend: Zod refina + retorna erro
- Compiler: trunca silenciosamente
- Combinação

**Recomendação:** **Front + compiler como fallback.**
- Front: contador visível ("X / 4000 tokens"), warning amarelo aos 3500, bloqueio vermelho aos 4000
- Compiler: se passar mesmo assim, trunca com aviso "Conteúdo cortado por limite de tokens"

#### E4. Tool ou sem tool?

Custom é volume baixo (~2-5 entries normais). **Sem tool, despeja direto no contexto.**

Compiler `formatCustom` lista cada entry como header markdown:

```markdown
## Conteúdo personalizado

### Política de atendimento bilíngue
Após 18h o atendimento é apenas em português. Clientes em inglês são encaminhados para o suporte 24/7 via email.

### Tratamento de cliente VIP
Clientes marcados como VIP no CRM têm prioridade...
```

#### E5. Cleanup final

Esta PR é a **última** da Sprint Catalog. Aproveitar pra fazer cleanup global:

- Procurar **qualquer outro schema/tipo legacy** que tenha sobrado escondido
- Remover imports órfãos
- Confirmar que enum `persona_box_type` no DB tem só valores usados (ou documentar valores legacy mortos)
- Atualizar README/docs se houver

#### E6. Documento de status final da Sprint Catalog

Após PR11 mergear, Sprint Catalog está **100% completa**. Vale Code criar um arquivo `docs/SPRINT_CATALOG_COMPLETE.md` ou `CHANGELOG.md` com:

- Lista das 11 PRs com commit + descrição
- Estatísticas (testes acumulados, edges criadas, componentes novos)
- Mapeamento de quais caixas usam quais tools
- Como adicionar 18ª caixa no futuro (pattern documentado)

**Opcional mas valioso.** Code decide se entra nesta PR ou fica como follow-up.

#### E7. DELETE manual

Pedro vai rodar quando tudo pronto.

---

## Aguarda OK antes de prosseguir.

---

## Etapa 2 — Schema declarativo

```ts
// box-schemas.ts

export const CUSTOM_SCHEMA: BoxSchemaDef = {
  boxType: "custom",
  label: "Conteúdo personalizado",
  cardinality: "multi_row",  // confirma se já existe ou adiciona
  hasExcel: false,
  blocks: [
    {
      title: "Entrada",
      fields: [
        { field: "title", question: "Título", type: "text", required: true },
        { field: "content", question: "Conteúdo", type: "textarea", required: true, helper: "Aceita markdown. Limite total: 4000 tokens somados de todas as entradas." },
      ],
    },
  ],
};

// Adicionar ao registry
export const BOX_SCHEMAS: Record<string, BoxSchemaDef> = {
  // ... anteriores
  custom: CUSTOM_SCHEMA,
};
```

### Zod schema

```ts
export const CustomEntrySchema = z.object({
  title: z.string().min(1, "Título obrigatório"),
  content: z.string().min(1, "Conteúdo obrigatório"),
});

export const CustomSchema = z.object({
  items: z.array(CustomEntrySchema).default([]),
});
```

---

## Etapa 3 — Form

### CustomForm wrapper (~12 linhas)

```tsx
export function CustomForm({ items, onChange, ...rest }: CustomFormProps) {
  return (
    <BoxFormMultiItem
      boxType="custom"
      titleField="title"
      items={items}
      onChange={onChange}
      modes={["manual"]}  // sem Excel
    />
  );
}
```

Adicionar entries em `AbaBlocos.tsx` (seção PERSONALIZE) e `EditBoxDialog.tsx`.

### Contador de tokens

Componente `<TokenCounter>` na UI do `<MultiItemListEditor>` quando boxType === "custom":
- Calcula total de tokens dos campos `content` somados
- Mostra "X / 4000 tokens"
- Cor:
  - Verde: 0-3000
  - Amarelo: 3000-3500
  - Laranja: 3500-4000
  - Vermelho: >4000 (bloqueia save)

Função de estimativa simples (não precisa GPT tokenizer perfeito):

```ts
function estimateTokens(text: string): number {
  // ~4 chars por token, ajustável
  return Math.ceil(text.length / 4);
}

function totalCustomTokens(items: CustomEntry[]): number {
  return items.reduce((sum, item) => 
    sum + estimateTokens(item.title) + estimateTokens(item.content), 0
  );
}
```

---

## Etapa 4 — Compiler

```ts
function formatCustom(box: PersonaBox | null): string {
  if (!box?.data?.items?.length) return "";
  
  const items = box.data.items;
  
  // Truncamento defensivo se passar do cap
  let totalTokens = 0;
  const MAX_TOKENS = 4000;
  const lines: string[] = [];
  let truncated = false;
  
  for (const item of items) {
    const entryTokens = estimateTokens(item.title) + estimateTokens(item.content);
    if (totalTokens + entryTokens > MAX_TOKENS) {
      truncated = true;
      break;
    }
    totalTokens += entryTokens;
    lines.push(`### ${item.title}\n${item.content}`);
  }
  
  if (!lines.length) return "";
  
  const header = `## Conteúdo personalizado\n`;
  const footer = truncated 
    ? `\n\n_Algumas entradas foram cortadas por excederem o limite de 4000 tokens._` 
    : "";
  
  return header + "\n" + lines.join("\n\n") + footer;
}
```

---

## Etapa 5 — Cleanup final da Sprint Catalog

### Schemas legacy a investigar

```bash
grep -rn "Schema\|Item\b" src/features/ai-settings/lib/personaBoxSchemas.ts | grep -v "import\|export"
```

Listar schemas Zod ainda existentes. Confirmar que cada um é usado.

### Imports órfãos

```bash
# Procurar imports que não são usados em arquivos críticos
npx ts-prune src/ supabase/functions/_shared/ 2>/dev/null | head -30
```

(Se `ts-prune` não tiver instalado, ignora — não vale instalar pra 1 PR)

### Enum persona_box_type

Valores no DB:
- Usados pela Sprint Catalog: establishment, hours, links, pagamento, products, services, faq, objections, team, forwards, delivery_items, delivery_areas, delivery_config, events, custom (15)
- Legacy mortos: delivery (substituído pelas 3 novas no PR9)
- Reservados pra Sprint Forms/Schedule: nenhum (vão ser adicionados nas sprints específicas)

Total enum: 16 valores. Lista documentada no PR description.

### Documento `docs/SPRINT_CATALOG_COMPLETE.md` (opcional)

Code decide se cria. Conteúdo sugerido:

```markdown
# Sprint Catalog — Completa (11 PRs)

## Estatísticas
- 11 PRs mergeados
- ~14 dias de trabalho (5/05/26 a 10/05/26 com pausas)
- 224+ testes verdes acumulados
- 15 caixas refatoradas
- 2 caixas pendentes (Formulários, Agenda) — sprints separadas

## PRs

| PR | Caixa(s) | Commit |
|---|---|---|
| PR1 | Establishment + fundação | 98102d9 |
| PR2 | Hours + Links | 1d241a9 |
| ...

## Arquitetura final

- Schema declarativo único: `_shared/box-schemas.ts`
- Componentes UI: BoxFormGeneric (singleton), BoxFormMultiItem (multi-item), BoxFormMatrix (matrix)
- Edges genéricas: download-box-template, import-box-excel
- 7 tools registradas

## Como adicionar uma 18ª caixa

[Pattern documentado em N passos]
```

Code decide se cria nesta PR ou deixa pra documentação separada.

---

## Etapa 6 — Cleanup + deploy

### Antes do deploy

**1) Volume:**
```sql
SELECT 
  tenant_id,
  jsonb_array_length(COALESCE(data->'entries', data->'items', data->'rows', '[]'::jsonb)) AS items
FROM persona_boxes
WHERE box_type = 'custom' AND is_active = true;
```

**2) DELETE:**
```sql
DELETE FROM persona_boxes WHERE box_type = 'custom';
```

**3) Confirma:**
```sql
SELECT COUNT(*) FROM persona_boxes WHERE box_type = 'custom';
```

### Deploy

```bash
gh pr merge <PR> --squash --delete-branch
git checkout main && git pull origin main
supabase functions deploy ai-reply
git push origin main
```

Sem deploy de edges template/import (Custom não tem Excel).

### Validação pós-deploy

1. Card "Conteúdo personalizado" aparece na seção PERSONALIZE
2. Modo Manual: adicionar 2-3 entradas
3. Confirma contador de tokens funcionando
4. Salva, recarrega, persiste
5. Teste de cap: cola conteúdo gigante, vê bloqueio aos 4000 tokens
6. **Não-regressão:** todas as 15 caixas anteriores continuam funcionando

---

## Critérios de aceite

- [ ] Etapa 1 confirmação aprovada
- [ ] CUSTOM_SCHEMA em box-schemas.ts (multi_row, sem Excel)
- [ ] CustomEntrySchema Zod novo
- [ ] CustomForm wrapper ~12 linhas
- [ ] `<TokenCounter>` no MultiItemListEditor quando boxType === "custom"
- [ ] Compiler formatCustom com truncamento defensivo
- [ ] Cleanup final: imports órfãos removidos, enum documentado
- [ ] Build/tsc/vitest verde
- [ ] Pedro confirma DELETE
- [ ] PR description anota: "PR11 ÚLTIMO DA SPRINT CATALOG. 11 PRs, 15 caixas refatoradas."

---

## Restrições

- ❌ Sem mexer em outras caixas
- ❌ Sem Excel (Custom é texto livre)
- ❌ Sem tool (vai no contexto)
- ❌ Sem ALTER TYPE (custom já existe no enum)
- ✅ Mostra diff antes do commit
- ✅ Branch: `catalog-pr11-custom`
- ✅ PR título: `feat(catalog): Custom + cleanup final (PR11) — Fecha Sprint Catalog`

---

## Pós-merge — Sprint Catalog COMPLETA

Após PR11 mergear, **Sprint Catalog está 100% completa.** Próximas sprints:

| Sprint | Estimativa | Pré-requisito |
|---|---|---|
| Sprint Forms | ~2 dias | Resend configurado |
| Sprint Schedule | ~3-4 dias | SA Google já pronta |
| Sprint Arquétipos | ~1-2 semanas | Catalog + Forms + Schedule completas |

Vanderlei só migra pra blocks após **todas** essas sprints rolarem.

---

## O que NÃO fazer neste PR

- ❌ Outras sprints (Forms/Schedule/Arquétipos)
- ❌ Tool para Custom
- ❌ Excel para Custom
- ❌ Reagrupar caixas (estrutura está consolidada)
- ❌ Migração Vanderlei (pendente Arquétipos)
