# PR3 — Pagamento (Sprint Catalog Onda 1)

> Terceiro PR da Sprint Catalog. **Caixa nova** (não existe hoje). Singleton, perguntas, sem Excel.
> Fecha a seção IDENTIDADE da Onda 1 (Establishment + Hours + Links + Pagamento).
>
> Estimativa: ~3-4 horas (sem migration de dados, sem schema antigo, só adicionar caixa nova).
>
> Branch: `catalog-pr3-pagamento`

---

## Contexto

PR1 entregou fundação. PR2 entregou Hours + Links. Ambos em produção.

PR3 adiciona caixa **Pagamento** — caixa nova, não existe hoje.

**Por que centralizada:** Products, Services, Events, Formulários vão referenciar Pagamento (chave PIX, formas aceitas, política IA). Em vez de duplicar essas perguntas em cada caixa, fica em uma só.

**Decisões importantes:**
- Pedro decidiu seção: vai pra **IDENTIDADE** (junto com Establishment, Hours, Links)
- Singleton (1 row por tenant), sem Excel
- Bloco "Política IA" com nível de autonomia da IA em cada ação de pagamento (Sim/Confirmar/Não)

Ler antes de codar:
- Memory items #18, #19 (PR1 e PR2 mergeados)
- Documento `/mnt/user-data/outputs/00-CAIXAS-ESTRUTURA-FINAL.md` — seção "Pagamento (singleton, perguntas)"

---

## Schema final — Pagamento

20 perguntas em 5 blocos.

| Bloco | Campo | Tipo | Notas |
|---|---|---|---|
| **PIX** | tem_pix | boolean | "Tem chave PIX?" |
| | pix_chave | text | "Qual a chave PIX?" |
| | pix_titular | text | "Em nome de quem?" |
| **Banco** | banco_nome | text | "Banco" |
| | banco_agencia | text | "Agência" |
| | banco_conta | text | "Conta" |
| | banco_tipo | single_choice | options: Corrente / Poupança |
| | banco_titular | text | "Titular da conta" |
| **Cartão online** | tem_link_pagamento | boolean | "Tem link de pagamento online?" |
| | link_pagamento_url | url | "URL do link" |
| | plataforma_pagamento | single_choice | options: Stripe / Mercado Pago / Asaas / PagSeguro / Outros |
| **Outras formas** | aceita_boleto | boolean | "Aceita boleto?" |
| | aceita_debito_presencial | boolean | "Aceita débito presencial?" |
| | aceita_credito_presencial | boolean | "Aceita crédito presencial?" |
| | aceita_dinheiro | boolean | "Aceita dinheiro?" |
| | parcelamento | text | "Política de parcelamento (ex: até 12x sem juros)" |
| **Política IA** | ia_pode_informar_valor | single_choice | "IA pode informar valor pro cliente?" — options: Sim / Confirmar antes / Não |
| | ia_pode_passar_pix | single_choice | "IA pode passar chave PIX direto?" — options: Sim / Confirmar antes / Não |
| | ia_pode_enviar_link | single_choice | "IA pode enviar link de pagamento direto?" — options: Sim / Confirmar antes / Não |
| | escalation_pagamento | textarea | "Quando escalar pra humano em pagamento?" |
| | observacoes_pagamento | textarea | "Observações pra IA sobre pagamento" |

**Total: 21 campos. 0 obrigatórios** (cliente preenche o que faz sentido pro negócio).

---

## Etapa 1 — Confirmações antes de codar

### A. Confirmar que caixa não existe hoje

```bash
grep -rn "pagamento\|payment\|PaymentSchema" supabase/functions/_shared/ src/features/ai-settings/lib/ --include="*.ts"
```

```sql
-- Confirma que box_type 'pagamento' nunca existiu em produção
SELECT box_type, COUNT(*) FROM persona_boxes
WHERE box_type IN ('pagamento', 'payment')
GROUP BY box_type;
```

Esperado: zero ocorrências em código + zero rows. Se aparecer algo, paramos pra entender.

### B. Confirmar listagem de caixas no painel

Hoje as caixas aparecem em alguma página tipo `/settings/ai` aba "Blocos". Onde a lista de caixas é definida?

```bash
grep -rn "BOX_REGISTRY\|boxList\|allBoxes\|BoxCard\|box_type:" src/features/ai-settings/ --include="*.ts" --include="*.tsx" -l
```

Reportar:
- Caminho onde caixas são listadas pra renderização
- Se existe enum/tipo `BoxType` no front
- Se adicionar `'pagamento'` exige mudar o tipo

### C. Decisões pendentes

#### C1. Nome da caixa em código

Opções:
- `'pagamento'` (português, segue padrão "establishment", "hours", "links")
- `'payment'` (inglês)

Recomendação: **`'pagamento'`**. Pedro tem outras caixas pensadas em PT (`forwards` é exceção). Mantém consistência com domínio brasileiro.

#### C2. Posição visual na seção IDENTIDADE

Hoje a seção tem 3 caixas: Establishment, Hours, Links. Pagamento entra como **4ª**. Confirmar ordem visual:

```
SEÇÃO IDENTIDADE
1. Establishment
2. Hours
3. Links
4. Pagamento  ← novo
```

Code precisa adicionar Pagamento na ordem certa em qualquer registry/lista de caixas.

#### C3. Compiler — gera output mesmo se vazio?

Pagamento pode ficar muito vazio (cliente não preenche nada). Comportamento:

- **Opção A:** se nenhum campo preenchido, compiler retorna `""` (não inclui seção no prompt)
- **Opção B:** sempre inclui seção, mesmo vazia

Recomendação: **A**. Já é o padrão de PR1 (Establishment vazio não vira seção no prompt). Mantém consistência.

#### C4. Validação de "tem PIX = não" + "chave PIX preenchida"

Cliente pode marcar "Tem chave PIX = Não" mas deixar a chave preenchida (legado). Compiler ignora ou mostra aviso?

Recomendação: **schema declarativo não valida cross-field.** Compiler renderiza apenas se `tem_pix = true` (ignora chave/titular se boolean falso). Code adiciona lógica condicional no formatter.

Mesma lógica pra `tem_link_pagamento`.

#### C5. Tipos novos no QuestionBlock?

Olhando o schema, todos os tipos já existem (`text`, `boolean`, `url`, `single_choice`, `textarea`). **Não precisa tipo novo**.

Confirmar.

---

## Aguarda OK antes de prosseguir.

---

## Etapa 2 — `box-schemas.ts` (adicionar PAYMENT_SCHEMA)

Sem alterar tipos existentes. Apenas adicionar:

```ts
export const PAYMENT_SCHEMA: BoxSchemaDef = {
  boxType: "pagamento",
  label: "Pagamento",
  cardinality: "singleton",
  hasExcel: false,
  blocks: [
    {
      title: "PIX",
      fields: [
        { field: "tem_pix", question: "Tem chave PIX?", type: "boolean" },
        { field: "pix_chave", question: "Qual a chave PIX?", type: "text", placeholder: "CPF, email, telefone ou chave aleatória" },
        { field: "pix_titular", question: "Em nome de quem?", type: "text" },
      ],
    },
    {
      title: "Banco",
      fields: [
        { field: "banco_nome", question: "Banco", type: "text" },
        { field: "banco_agencia", question: "Agência", type: "text" },
        { field: "banco_conta", question: "Conta", type: "text" },
        { field: "banco_tipo", question: "Tipo de conta", type: "single_choice", options: ["Corrente", "Poupança"] },
        { field: "banco_titular", question: "Titular da conta", type: "text" },
      ],
    },
    {
      title: "Cartão online",
      fields: [
        { field: "tem_link_pagamento", question: "Tem link de pagamento online?", type: "boolean" },
        { field: "link_pagamento_url", question: "URL do link de pagamento", type: "url" },
        { field: "plataforma_pagamento", question: "Plataforma utilizada", type: "single_choice", options: ["Stripe", "Mercado Pago", "Asaas", "PagSeguro", "Outros"] },
      ],
    },
    {
      title: "Outras formas",
      fields: [
        { field: "aceita_boleto", question: "Aceita boleto?", type: "boolean" },
        { field: "aceita_debito_presencial", question: "Aceita débito presencial?", type: "boolean" },
        { field: "aceita_credito_presencial", question: "Aceita crédito presencial?", type: "boolean" },
        { field: "aceita_dinheiro", question: "Aceita dinheiro?", type: "boolean" },
        { field: "parcelamento", question: "Política de parcelamento", type: "text", placeholder: "ex: até 12x sem juros" },
      ],
    },
    {
      title: "Política IA",
      fields: [
        { field: "ia_pode_informar_valor", question: "IA pode informar valor pro cliente?", type: "single_choice", options: ["Sim", "Confirmar antes", "Não"] },
        { field: "ia_pode_passar_pix", question: "IA pode passar chave PIX direto?", type: "single_choice", options: ["Sim", "Confirmar antes", "Não"] },
        { field: "ia_pode_enviar_link", question: "IA pode enviar link de pagamento direto?", type: "single_choice", options: ["Sim", "Confirmar antes", "Não"] },
        { field: "escalation_pagamento", question: "Quando escalar pra humano em pagamento?", type: "textarea", placeholder: "ex: cliente pede desconto não previsto, problema com pagamento confirmado" },
        { field: "observacoes_pagamento", question: "Observações pra IA sobre pagamento", type: "textarea" },
      ],
    },
  ],
};

// Adicionar ao registry
export const BOX_SCHEMAS: Record<string, BoxSchemaDef> = {
  establishment: ESTABLISHMENT_SCHEMA,
  hours: HOURS_SCHEMA,
  links: LINKS_SCHEMA,
  pagamento: PAYMENT_SCHEMA,  // NOVO
};
```

---

## Etapa 3 — Compiler

### Formatter

Pagamento pode usar `formatBoxFromSchema` genérico (já existe desde PR1). Saída esperada:

```
## Pagamento

### PIX
- Tem chave PIX: Sim
- Qual a chave PIX: pedro@email.com
- Em nome de quem: Pedro Costa

### Banco
- Banco: Itaú
- Agência: 1234
...

### Política IA
- IA pode informar valor pro cliente: Sim
- IA pode passar chave PIX direto: Confirmar antes
...
```

### Mas atenção — campos condicionais (boolean = false)

Cliente marca "Tem chave PIX = Não". Não faz sentido mostrar `pix_chave` e `pix_titular` no prompt (ficam vazios mesmo, mas se tiverem dados legado, mostraria).

Solução: **adicionar lógica condicional no formatBoxFromSchema** ou **formatter custom pra pagamento**.

Recomendação: **lógica condicional no formatter genérico** via convenção — campos com prefixo `pix_*` só aparecem se `tem_pix === true`. Mesmo pra `link_pagamento_*` e `tem_link_pagamento`.

Pseudocódigo:

```ts
// Dentro de formatBoxFromSchema, ao processar bloco "PIX":
if (data.tem_pix !== true) {
  // Pula campos pix_chave, pix_titular
  // Mas inclui ainda "tem_pix: Não" se preenchido como false explícito
}

// Ao processar bloco "Cartão online":
if (data.tem_link_pagamento !== true) {
  // Pula link_pagamento_url, plataforma_pagamento
}
```

**Decisão Etapa 1 (C4):** Code propõe abordagem. Pode ser via:
- Convenção de prefixo (mais simples mas frágil)
- Campo `dependsOn` no schema declarativo (mais robusto)
- Formatter custom só pra pagamento (escape hatch)

Code escolhe na implementação. Recomendação: **formatter custom inline** pra pagamento (igual Hours teve no PR2). Mantém genérico simples.

### Inclui no compilePersonaFromBoxes

Adicionar case `'pagamento'` no switch principal do compiler.

---

## Etapa 4 — Form

### PaymentForm.tsx (12 linhas)

```tsx
// src/features/ai-settings/components/blocos/forms/PaymentForm.tsx

import { BoxFormGeneric } from "../BoxFormGeneric";

interface PaymentFormProps {
  value: Record<string, any>;
  onChange: (value: Record<string, any>) => void;
  onSave: () => void;
}

export function PaymentForm(props: PaymentFormProps) {
  return <BoxFormGeneric boxType="pagamento" {...props} />;
}
```

### Card no painel de blocos

Adicionar Pagamento na **seção IDENTIDADE**, após Links. Code descobre na Etapa 1 onde fica essa lista e adiciona.

Sugestão de copy do card:
- Título: **Pagamento**
- Subtítulo: PIX, banco, link online, política da IA.

---

## Etapa 5 — Deploy

Sem DELETE. Caixa não existe em produção, não tem dados pra apagar.

```bash
gh pr merge <PR> --squash --delete-branch
git checkout main && git pull origin main
supabase functions deploy ai-reply  # compiler ganhou case pagamento
git push origin main                 # Lovable build
```

### Validação pós-deploy

Pedro abre `/settings/ai`, testa:
1. Card Pagamento aparece na seção IDENTIDADE (após Links)
2. Status inicial: vazio
3. Clica → modal abre com 5 accordions
4. Marca "Tem chave PIX = Sim", preenche chave + titular
5. Marca "Tem link de pagamento = Não" (não preenche URL)
6. Em Política IA: escolhe Sim/Confirmar/Não nos 3 dropdowns
7. Salva
8. Recarrega → persistência
9. Reabre, confirma que campos preenchidos têm ✅

---

## Critérios de aceite

- [ ] Etapa 1 confirmação aprovada antes de codar
- [ ] `box-schemas.ts` ganha PAYMENT_SCHEMA + registry atualizado
- [ ] Card Pagamento aparece na seção IDENTIDADE (4ª caixa)
- [ ] PaymentForm wrapper de ~12 linhas
- [ ] Compiler trata pagamento (genérico ou formatter custom)
- [ ] Lógica condicional implementada (`tem_pix=false` → não mostra chave/titular)
- [ ] Build/tsc/vitest verde
- [ ] PR description anota: "PR3 = caixa NOVA Pagamento, fecha seção IDENTIDADE da Onda 1"

---

## Restrições

- ❌ Sem migration (caixa nova, não existe schema antigo)
- ❌ Sem DELETE manual (não tem dados em produção)
- ❌ Smoke automático (Pedro testa)
- ❌ Mexer em outras caixas
- ✅ Pode adicionar formatter custom pra pagamento se preferir (igual Hours)
- ✅ Mostrar diff antes do commit
- ✅ Branch: `catalog-pr3-pagamento`
- ✅ PR título: `feat(catalog): caixa Pagamento (PR3)`

---

## Pós-merge — Próximo: PR4 (Products + Excel)

PR4 é o **destravante real**:
- Refatora Products pro schema declarativo (17 colunas)
- Adiciona campo `disponivel_pra_delivery` no schema
- Edge `download-box-template/products` gera XLSX vazio
- Edge `import-box-excel` parseia + valida + insere
- UI: 3º modo "Excel" no modal Products
- Tool `query_products` continua usando o mesmo (SUF15 já preparou estrutura)
- Smoke real com Excel de 30k itens da loja Vanderlei

Estimativa: 1.5-2 dias. Maior PR da Onda 1.

Após PR4, Onda 1 está completa. Onda 2 (Services, Delivery 3 caixas, Events, Team, FAQ, Objections, Forwards, Custom) vira backlog rolando.

---

## O que NÃO fazer neste PR

- ❌ Products — fica pra PR4
- ❌ Excel — fica pra PR4
- ❌ Mexer em Establishment/Hours/Links (já mergeados)
- ❌ Implementar Formulários ou Agenda (Sprint Forms / Sprint Schedule)
