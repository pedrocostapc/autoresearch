# PR1 — Schema Declarativo + QuestionBlock + Refator Establishment (Sprint Catalog Onda 1)

> Primeiro PR da Sprint Catalog. Valida approach de schema declarativo + componente reusável de pergunta com a caixa mais simples (Establishment) antes de replicar pras outras 14.
>
> Estimativa: 1-2 dias.
> Branch: `catalog-pr1-schemas-establishment`

---

## Contexto

Pedro decidiu refatorar todo o sistema de caixas (de 12 → 17). Cada caixa terá:
1. **Schema declarativo** que serve UI + Excel + master prompt
2. **UI de perguntas humanas** ("Tem estacionamento?") em vez de labels técnicos
3. **Componente reusável** `<QuestionBlock>` pra renderizar pergunta + dropdown/Sim-Não/texto

PR1 implementa **a fundação**:
- Define `_shared/box-schemas.ts` (1 source of truth)
- Cria `<QuestionBlock>` reutilizável
- Refatora **Establishment** (caixa singleton, mais simples) usando o novo padrão

Outras 14 caixas migrarão em PRs sequenciais (PR2-PR12) reusando essa fundação.

**SUF15 já mergeou** (10/05/26) — master prompt declara tools dinamicamente. PR1 não toca nessa parte.

**Pedro autorizou apagar dados de blocks** — 14 tenants são cobaias suas, IA não responde neles. Cleanup via SQL Editor antes do deploy.

---

## Decisões de produto registradas

Ler antes de codar:
- `/mnt/user-data/outputs/00-CAIXAS-ESTRUTURA-FINAL.md` — estrutura definitiva 17 caixas
- Memory Pedro: items #13, #14, #15, #16, #17 (schemas, UX padrão, decisões SUF15, faseamento Sprint Catalog)

### Schema novo de Establishment (16 campos, só Nome obrigatório)

| Bloco | Campo | Tipo |
|---|---|---|
| **Básico** | Nome | texto ✅ |
| | CNPJ | texto |
| | Razão social | texto |
| **Endereço** | Logradouro | texto |
| | Número | texto |
| | Complemento | texto |
| | Bairro | texto |
| | Cidade | texto |
| | Estado | UF (2 letras) |
| | CEP | texto |
| **Sobre** | Descrição (1-2 linhas) | texto |
| | Ano de fundação | número |
| | Diferenciais | texto CSV |
| | Missão/valores | texto livre |
| **Operação** | Atendimento | dropdown Loja física/Online/Híbrido |
| | Política de troca/devolução | texto livre |

---

## Etapa 1 — Confirmação (sem codar)

Antes de qualquer linha de código, reportar:

1. Caminho atual de:
   - `personaBoxSchemas.ts` (raio-x mencionou em `src/features/ai-settings/lib/`)
   - `persona-compiler.ts` (em `_shared/`)
   - Componente atual de edição de Establishment
   - Hook `usePersonaBoxes` ou similar

2. Schema atual de Establishment (Zod):
   - Quantos campos tem hoje?
   - Quais são obrigatórios?

3. Como `establishment` é formatado pelo compiler hoje (copia o `case "establishment":` literal)

4. Quantas linhas tem `establishment` em produção (deve ser 14, mas confere):
   ```sql
   SELECT COUNT(*) FROM persona_boxes
   WHERE box_type = 'establishment' AND is_active = true;
   ```

Reporta os 4 itens e **espera o OK** antes de prosseguir pra Etapa 2.

---

## Etapa 2 — `_shared/box-schemas.ts` (schema declarativo)

Cria um arquivo TypeScript canônico que descreve cada campo de cada caixa de forma rica.

### Estrutura proposta

```ts
// supabase/functions/_shared/box-schemas.ts

export type FieldType =
  | "text"           // input texto curto
  | "textarea"       // input texto longo
  | "number"         // input numérico
  | "boolean"        // toggle Sim/Não
  | "single_choice"  // dropdown ou botões mutually exclusive
  | "multi_choice"   // checkboxes
  | "csv"            // texto que vira array
  | "uf"             // dropdown UF
  | "url"
  | "email";

export interface BoxFieldDef {
  /** Nome técnico do campo no JSON do data */
  field: string;
  /** Pergunta humana mostrada ao tenant ("Tem estacionamento?") */
  question: string;
  /** Tipo de input */
  type: FieldType;
  /** Para single_choice/multi_choice: opções fechadas */
  options?: string[];
  /** Obrigatório? */
  required?: boolean;
  /** Hint/descrição opcional abaixo da pergunta */
  helper?: string;
  /** Placeholder dentro do input */
  placeholder?: string;
}

export interface BoxBlockDef {
  /** Título do accordion ("Básico", "Endereço", "Sobre") */
  title: string;
  /** Campos do bloco em ordem */
  fields: BoxFieldDef[];
}

export interface BoxSchemaDef {
  /** Box type que persiste em persona_boxes.box_type */
  boxType: string;
  /** Nome humano da caixa ("Estabelecimento") */
  label: string;
  /** Singleton (1 row por tenant) ou multi-item (vários itens dentro de items[]) */
  cardinality: "singleton" | "multi_item" | "multi_row";
  /** Pode ter Excel import? Só vai pra Sprint Catalog PRs futuros */
  hasExcel: boolean;
  /** Blocos visuais (accordions) */
  blocks: BoxBlockDef[];
}

// Schema da caixa Establishment
export const ESTABLISHMENT_SCHEMA: BoxSchemaDef = {
  boxType: "establishment",
  label: "Estabelecimento",
  cardinality: "singleton",
  hasExcel: false,
  blocks: [
    {
      title: "Básico",
      fields: [
        { field: "name", question: "Como o estabelecimento se chama?", type: "text", required: true, placeholder: "Nome fantasia" },
        { field: "cnpj", question: "Qual o CNPJ?", type: "text", placeholder: "00.000.000/0001-00" },
        { field: "legal_name", question: "Razão social (se diferente do nome)", type: "text" },
      ],
    },
    {
      title: "Endereço",
      fields: [
        { field: "address_street", question: "Logradouro", type: "text", placeholder: "Rua, avenida, etc" },
        { field: "address_number", question: "Número", type: "text" },
        { field: "address_complement", question: "Complemento", type: "text", placeholder: "Sala, bloco, andar" },
        { field: "address_neighborhood", question: "Bairro", type: "text" },
        { field: "address_city", question: "Cidade", type: "text" },
        { field: "address_state", question: "Estado", type: "uf" },
        { field: "address_zip", question: "CEP", type: "text", placeholder: "00000-000" },
      ],
    },
    {
      title: "Sobre",
      fields: [
        { field: "description", question: "Descreva o negócio em 1-2 linhas", type: "textarea", helper: "O que o cliente precisa saber em poucas palavras" },
        { field: "founded_year", question: "Ano de fundação", type: "number" },
        { field: "differentials", question: "Diferenciais do negócio", type: "csv", helper: "Lista separada por vírgulas" },
        { field: "mission_values", question: "Missão / valores", type: "textarea" },
      ],
    },
    {
      title: "Operação",
      fields: [
        { field: "channel_type", question: "Como atende o cliente?", type: "single_choice", options: ["Loja física", "Online", "Híbrido"] },
        { field: "return_policy", question: "Política de troca / devolução", type: "textarea" },
      ],
    },
  ],
};

// Registry: map box_type → schema
export const BOX_SCHEMAS: Record<string, BoxSchemaDef> = {
  establishment: ESTABLISHMENT_SCHEMA,
  // outras caixas vão aqui em PRs futuros
};

// Helpers
export function getBoxSchema(boxType: string): BoxSchemaDef | null {
  return BOX_SCHEMAS[boxType] ?? null;
}

export function getAllFieldsForBox(boxType: string): BoxFieldDef[] {
  const schema = getBoxSchema(boxType);
  if (!schema) return [];
  return schema.blocks.flatMap(b => b.fields);
}

export function getRequiredFieldsForBox(boxType: string): BoxFieldDef[] {
  return getAllFieldsForBox(boxType).filter(f => f.required);
}
```

### Considerações

- **Schema fica em `_shared/`** porque tanto edges quanto front podem precisar dele
- Front importa via build do Vite (já tem `_shared/` exportado pra src? confirma na Etapa 1)
- Se não tem, duplica em `src/features/ai-settings/lib/box-schemas.ts` (com warning de "manter sincronizado com edge")
- Evitar duplicação: se possível, use 1 só fonte (preferência: `_shared/` se Vite já bundla)

### Critérios

- [ ] Tipos `BoxFieldDef`, `BoxBlockDef`, `BoxSchemaDef` exportados
- [ ] `ESTABLISHMENT_SCHEMA` com 16 campos em 4 blocos
- [ ] Registry `BOX_SCHEMAS` com pelo menos `establishment`
- [ ] Helpers `getBoxSchema`, `getAllFieldsForBox`, `getRequiredFieldsForBox`
- [ ] Imports funcionam tanto em edges quanto em src

---

## Etapa 3 — Componente `<QuestionBlock>`

Componente reutilizável que renderiza 1 pergunta seguindo o `BoxFieldDef`.

### Comportamento

```tsx
<QuestionBlock
  field={fieldDef}                      // BoxFieldDef
  value={currentValue}                  // valor atual do JSON
  onChange={(newValue) => ...}          // atualiza o JSON
  answered={!!currentValue}             // pra contador de progresso
/>
```

### Renderização por tipo

| `type` | UI |
|---|---|
| `text` | `<Input>` |
| `textarea` | `<Textarea>` |
| `number` | `<Input type="number">` |
| `boolean` | 2 botões "Sim" / "Não" mutually exclusive |
| `single_choice` | Botões mutually exclusive com as `options` |
| `multi_choice` | Checkboxes com as `options` |
| `csv` | `<Input>` que parseia vírgulas em array no save |
| `uf` | Dropdown com 27 UFs |
| `url` | `<Input type="url">` com validação |
| `email` | `<Input type="email">` com validação |

### Layout

```
┌─────────────────────────────────────────────┐
│ ⭕ Como o estabelecimento se chama?  *      │  ← pergunta + ícone status (⭕ vazio, ✅ preenchido)
│ Nome fantasia                               │  ← helper opcional ou placeholder
│ ┌───────────────────────────────────────┐  │
│ │ Padaria do Pedro                      │  │  ← input
│ └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

### Acessibilidade

- `aria-required` quando obrigatório
- `aria-describedby` ligando helper ao input
- Tab order respeitada
- Focus visível (anel teal — design system Editorial Noir)

### Critérios

- [ ] Componente em `src/components/common/QuestionBlock.tsx`
- [ ] Suporta os 10 tipos listados
- [ ] Mostra ícone ⭕ (vazio) ou ✅ (preenchido)
- [ ] Mostra `*` em obrigatórios
- [ ] Storybook ou exemplo simples em alguma rota dev (opcional)

---

## Etapa 4 — Refator Establishment usando schema declarativo

### Migration (mínima)

`establishment` hoje provavelmente armazena `{ name, ... }` em `persona_boxes.data` (JSONB). Schema novo tem 16 campos. JSONB já aguenta sem ALTER.

**Mas** a UI atual provavelmente espera nomes diferentes. Decisão Pedro: **DELETE manual via SQL Editor** antes do deploy:

```sql
DELETE FROM persona_boxes
WHERE box_type = 'establishment';
-- Esperado: 14 rows deleted (todos cobaias)
```

Pedro roda manual antes de deployar. Code **não cria migration destrutiva**.

### Form refatorado

Substitui o componente antigo por um genérico que lê o schema:

```tsx
// src/features/ai-settings/components/BoxFormGeneric.tsx
function BoxFormGeneric({ boxType, value, onChange, onSave }) {
  const schema = getBoxSchema(boxType);
  if (!schema) return null;

  const totalFields = schema.blocks.flatMap(b => b.fields).length;
  const answeredCount = Object.keys(value).filter(k => !isEmpty(value[k])).length;

  return (
    <Modal title={schema.label}>
      {schema.blocks.map(block => (
        <Accordion title={block.title} subtitle={`${countAnswered(block, value)} de ${block.fields.length} respondidas`}>
          {block.fields.map(field => (
            <QuestionBlock
              key={field.field}
              field={field}
              value={value[field.field]}
              onChange={(v) => onChange({ ...value, [field.field]: v })}
              answered={!isEmpty(value[field.field])}
            />
          ))}
        </Accordion>
      ))}
      
      <Footer>
        <span>{answeredCount} de {totalFields} respondidas</span>
        <Button onClick={onSave} disabled={!isValid(schema, value)}>Salvar</Button>
      </Footer>
    </Modal>
  );
}
```

### Compiler refatorado

`persona-compiler.ts` hoje tem case-by-case por box_type. Refator pra ler schema declarativo:

```ts
// supabase/functions/_shared/persona-compiler.ts (parcial)
import { getBoxSchema } from "./box-schemas.ts";

function formatEstablishmentFromSchema(data: Record<string, any>): string {
  const schema = getBoxSchema("establishment");
  if (!schema) return "";

  const lines: string[] = [`## ${schema.label}`];
  
  for (const block of schema.blocks) {
    const blockLines: string[] = [];
    for (const field of block.fields) {
      const value = data[field.field];
      if (isEmpty(value)) continue;
      // Formata "Pergunta humana: valor"
      blockLines.push(`- ${field.question.replace(/\?$/, "")}: ${formatValue(value, field.type)}`);
    }
    if (blockLines.length > 0) {
      lines.push(`\n### ${block.title}`);
      lines.push(...blockLines);
    }
  }
  
  return lines.join("\n");
}
```

**Por que isso importa:** quando master prompt for declarar caixas (SUF15 já implementou texto declarativo), ele vai usar a pergunta humana como contexto. IA recebe: "Como o estabelecimento se chama?: Padaria do Pedro" em vez de "name: Padaria do Pedro".

### Critérios

- [ ] Form genérico `<BoxFormGeneric>` criado
- [ ] Modal de Establishment usa `<BoxFormGeneric boxType="establishment">`
- [ ] Compiler refatorado pra ler schema declarativo (em vez de case hardcoded)
- [ ] Saída do compiler usa pergunta humana, não nome técnico do campo
- [ ] Card de Establishment no painel de blocos mostra status (vazio/parcial/completo)

---

## Etapa 5 — Cleanup + deploy

### Antes do deploy

Pedro roda manualmente no SQL Editor:

```sql
DELETE FROM persona_boxes WHERE box_type = 'establishment';
-- Esperado: 14 rows deleted
```

Confirma com:
```sql
SELECT COUNT(*) FROM persona_boxes WHERE box_type = 'establishment';
-- Esperado: 0
```

### Deploy

```bash
gh pr merge <PR> --squash --delete-branch
git checkout main && git pull origin main
supabase functions deploy ai-reply  # se persona-compiler mudou
git push origin main                 # Lovable build automático
```

### Validação pós-deploy

Pedro abre o painel `/settings/ai`, clica em Establishment, preenche os 16 campos novos, salva. Verifica:
- Form mostra 4 accordions
- Cada accordion mostra contador de progresso
- Salvar persiste no banco
- Compiler gera markdown legível com perguntas humanas

---

## Critérios de aceite

- [ ] Etapa 1 confirmação aprovada antes de codar
- [ ] `_shared/box-schemas.ts` exportado com Establishment
- [ ] `<QuestionBlock>` reusável criado
- [ ] `<BoxFormGeneric>` lê schema e renderiza accordions
- [ ] Modal de Establishment migrado pra novo form
- [ ] Compiler usa schema declarativo
- [ ] Build/tsc/vitest verde
- [ ] Pedro confirmou DELETE manual rodado antes do deploy
- [ ] PR description anota que PR1 é fundação pra PR2-PR12

---

## Pós-merge (próximo PR)

PR2 reusa toda a fundação:
- Adiciona schemas de **Hours** + **Links** em `box-schemas.ts`
- Refatora forms dessas 2 caixas pra `<BoxFormGeneric>`
- ~4-6 horas de trabalho (mais leve que PR1)

PR3: Pagamento (caixa nova).
PR4: Products + Excel + tool refatorada (o grande, destrava 30k itens).
PRs 5-12: outras caixas.

---

## Restrições e lembretes operacionais

- ❌ Nenhuma migration destrutiva (DELETE rodado por Pedro via SQL Editor)
- ❌ Nenhum smoke automático — Pedro testa manualmente
- ✅ `grep -n` antes/depois de `replace_all`
- ✅ Logs distintos: `[box-schemas]`, `[question-block]` se útil
- ✅ Sem teste E2E novo, mas verificar que vitest existente continua verde
- ✅ Mostrar diff antes do commit
- ✅ Branch: `catalog-pr1-schemas-establishment`
- ✅ PR título: `feat(catalog): schema declarativo + QuestionBlock + refator Establishment (PR1)`

---

## O que NÃO fazer neste PR

- ❌ Outras caixas (Hours, Links, etc) — ficam pra PR2+
- ❌ Excel import — fica pra PR4
- ❌ Mexer em master prompt (SUF15 já cobriu)
- ❌ Mexer em tools de IA
- ❌ Pagamento — fica pra PR3
- ❌ Quiz dos 5 capítulos (validação posterior)

PR1 é **fundação + 1 caixa piloto**. Se a fundação for boa, replicar pras outras é trivial.
