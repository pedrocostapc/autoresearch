# PR7 — Team + Excel (Sprint Catalog Onda 2)

> **Caixa Team — equipe interna do estabelecimento.** Schema de 21 campos / 4 blocos. Modelo Excel já existe (Pedro forneceu).
> Flag `tem_agenda_propria` reservada pra integração futura com Sprint Schedule.
>
> Estimativa: ~5-7h.
> Branch: `catalog-pr7-team-excel`

---

## Contexto

PR5 fechou infra genérica (`<MultiItemListEditor>`, `<BoxFormMultiItem>`). PR6 estendeu (`titleField`, validação required). PR7 reusa tudo + adiciona:

- 21 campos em 4 blocos (Identificação + Contato + Disponibilidade + Direcionamento IA)
- Flag **`tem_agenda_propria`** = chave pra Sprint Schedule futura (memory item #20)
- Possível tipo novo `phone` no QuestionBlock (E.164)

Pedro tem **modelo Excel pronto** desse schema. Mantém colunas conforme acordado.

---

## Schema final Team (21 campos / 4 blocos)

| Bloco | Campo | Tipo |
|---|---|---|
| **1. Identificação** | full_name | text ✅ |
| | aliases | csv |
| | sector | text |
| | role | text |
| | specialty | text |
| | branch | text |
| **2. Contato** | mobile | text E.164 |
| | has_whatsapp | boolean |
| | landline | text |
| | email | email |
| | number_type | single_choice (Empresa/Privado) |
| | preferred_channel | single_choice (WhatsApp/Email/Telefone) |
| **3. Disponibilidade** | status | single_choice (Ativo/Férias/Afastado/Inativo) |
| | service_hours | textarea |
| | languages | csv |
| | priority | single_choice (Alta/Média/Baixa) |
| | has_own_calendar | boolean ⭐ |
| **4. Direcionamento IA** | trigger_keywords | csv |
| | dont_route_when | csv |
| | ai_can_forward | single_choice (Sim/Confirmar/Não) |
| | ai_notes | textarea |

**Total: 21 campos. Apenas Nome obrigatório.**

⭐ `has_own_calendar` é a flag crítica pra Sprint Schedule. Quando = true, sistema vai criar calendar Google via Service Account pra esse profissional.

---

## Etapa 1 — Confirmações antes de codar

### A. Schema atual de Team

```bash
grep -n "TeamSchema\|formatTeam" \
  src/features/ai-settings/lib/personaBoxSchemas.ts \
  supabase/functions/_shared/persona-compiler.ts
```

Reportar:
- Schema Zod atual (copia literal)
- Como `formatTeam` é implementado hoje
- Estrutura do data atual: tem `members[]`, `pairs[]`, ou `items[]`?
- Se há tool `query_team` em `_shared/persona-tools.ts`

### B. UI atual TeamForm

```bash
grep -n "TeamForm" src/features/ai-settings/components/blocos/forms/
```

Reportar:
- Form atual
- Se usa `<CatalogEditor>` ou tem editor próprio
- Tem modo "Colar Lista"?

### C. Volume real

```sql
SELECT 
  COUNT(*) AS total_rows,
  COUNT(DISTINCT tenant_id) AS tenants,
  AVG(jsonb_array_length(COALESCE(data->'members', data->'items', '[]'::jsonb)))::int AS avg_items,
  MAX(jsonb_array_length(COALESCE(data->'members', data->'items', '[]'::jsonb))) AS max_items
FROM persona_boxes 
WHERE box_type = 'team' AND is_active = true;
```

Reportar números (Pedro confirma antes do DELETE).

### D. Tipos no QuestionBlock — checar suficiência

| Campo | Tipo necessário | Status |
|---|---|---|
| email | `email` | ? (PR2 Links tem `email` — provavelmente já existe) |
| mobile (E.164) | text com placeholder | OK reusa `text` |
| has_whatsapp | `boolean` | ✅ existe |
| status | `single_choice` | ✅ existe |
| service_hours | `textarea` | ✅ existe |
| languages | `csv` | ✅ existe |

Confirmar `email` existe ou criar.

### E. Decisões pendentes

#### E1. Tool `query_team` — criar ou não?

Volume típico:
- Salão pequeno: 3-8 profissionais
- Clínica média: 10-30 profissionais
- Hospital/rede: 50-200+ profissionais

**3 opções:**

**Opção A — Sem tool (igual FAQ/Objections):** Compiler despeja todos os profissionais no contexto. Funciona bem até ~30 profissionais. Acima disso, peso de tokens fica relevante.

**Opção B — Tool `query_team` (igual Products/Services):** Compiler mostra count + sample. IA chama tool com filtros (especialidade, status, dia da semana). Funciona em qualquer volume.

**Opção C — Híbrido:** Compiler mostra **só profissionais com `status = "Ativo"`** (até limite). Inativos/Férias/Afastados ficam só no banco. Tool `query_team` opcional pra busca complexa.

**Recomendação: Opção B.** Razões:
- Volume pode chegar fácil em 50+ (clínica/hospital/rede)
- Buscas complexas naturais ("cardiologista no sábado", "quem fala inglês")
- Custo baixo: já temos infra de tools (PR4/PR5)
- Sample no compiler já cobre caso simples

Code aceita ou propõe alternativa.

#### E2. Schema de retorno da tool `query_team`

Se Opção B aprovada, tool retorna ~10 campos úteis:

```ts
{
  full_name: string,
  role: string,
  specialty: string,
  sector: string,
  status: string,
  preferred_channel: string,
  mobile: string,        // só se ai_can_forward !== "Não"
  has_whatsapp: boolean,
  trigger_keywords: string[],
  ai_can_forward: string,
}
```

**Atenção privacidade:** `mobile` é dado sensível. Tool **omite mobile se `ai_can_forward = "Não"`**. IA usa pra decidir mostrar ou não pro cliente.

Code confirma approach.

#### E3. Haystack do fuzzy

```
full_name + aliases + role + specialty + sector + trigger_keywords + languages
```

Boa cobertura. Fuzzy match em "Maria" → acha Maria Silva, Maria José. Match em "dermato" → acha dermatologistas.

#### E4. Validação cross-field

Cliente pode marcar `has_whatsapp = true` mas `mobile` vazio. Não tem como mandar WhatsApp sem número.

**Recomendação: não validar cross-field.** Aviso silencioso (campo `mobile` vazio + `has_whatsapp=true` = inconsistência mas não crítica). IA tem informação suficiente pra agir certo.

Mantém comportamento PR3/PR4 (sem cross-field).

#### E5. Tipo `phone` novo?

Campo `mobile` é E.164 (`+5538998940667`). Hoje usa `text` com placeholder.

**Opção A:** Mantém `text`. Validação só no Excel import via Zod regex.
**Opção B:** Cria tipo `phone` novo no QuestionBlock que valida formato E.164 inline.

**Recomendação: A.** Razões:
- Validação inline pra E.164 é incômoda (cliente pode digitar sem +55)
- Excel import já valida via Zod
- Outras caixas (Forwards) também usam E.164 — tipo novo serviria, mas não bloqueia agora
- Adiciona complexidade sem ganho proporcional pra v1

Pode virar dívida técnica futura.

#### E6. DELETE manual

Pedro vai rodar.

---

## Aguarda OK antes de prosseguir.

---

## Etapa 2 — Schema declarativo

```ts
export const TEAM_SCHEMA: BoxSchemaDef = {
  boxType: "team",
  label: "Equipe",
  cardinality: "multi_item",
  hasExcel: true,
  blocks: [
    {
      title: "Identificação",
      fields: [
        { field: "full_name", question: "Nome completo", type: "text", required: true },
        { field: "aliases", question: "Apelidos", type: "csv", helper: "Como esse profissional pode ser chamado pelo cliente" },
        { field: "sector", question: "Setor", type: "text", helper: "Vendas, Logística, Atendimento, etc" },
        { field: "role", question: "Cargo", type: "text" },
        { field: "specialty", question: "Especialidade", type: "text", helper: "Importante pra clínica/salão (cardiologista, colorista, etc)" },
        { field: "branch", question: "Filial/Unidade", type: "text" },
      ],
    },
    {
      title: "Contato",
      fields: [
        { field: "mobile", question: "Celular", type: "text", placeholder: "+5538999999999" },
        { field: "has_whatsapp", question: "Tem WhatsApp?", type: "boolean" },
        { field: "landline", question: "Telefone fixo/Ramal", type: "text" },
        { field: "email", question: "Email", type: "email" },
        { field: "number_type", question: "Tipo do número", type: "single_choice", options: ["Empresa", "Privado"] },
        { field: "preferred_channel", question: "Canal preferido", type: "single_choice", options: ["WhatsApp", "Email", "Telefone"] },
      ],
    },
    {
      title: "Disponibilidade",
      fields: [
        { field: "status", question: "Status", type: "single_choice", options: ["Ativo", "Férias", "Afastado", "Inativo"] },
        { field: "service_hours", question: "Horário de atendimento", type: "textarea", helper: "Pode ser texto livre — ex: 'Seg-Sex 8-12h e 14-18h, Sáb 8-13h'" },
        { field: "languages", question: "Idiomas", type: "csv", helper: "Português, Inglês, Espanhol, etc" },
        { field: "priority", question: "Prioridade", type: "single_choice", options: ["Alta", "Média", "Baixa"], helper: "IA pode usar pra ordenar quem oferece primeiro" },
        { field: "has_own_calendar", question: "Tem agenda própria?", type: "boolean", helper: "Se Sim, sistema vai criar calendar Google dedicado quando Sprint Schedule for ativada" },
      ],
    },
    {
      title: "Direcionamento IA",
      fields: [
        { field: "trigger_keywords", question: "Quando direcionar (palavras-chave)", type: "csv" },
        { field: "dont_route_when", question: "NÃO direcionar quando", type: "csv" },
        { field: "ai_can_forward", question: "IA pode encaminhar direto?", type: "single_choice", options: ["Sim", "Confirmar", "Não"], helper: "Sim: IA passa contato direto. Confirmar: IA pergunta antes. Não: só atendente humano" },
        { field: "ai_notes", question: "Observações pra IA", type: "textarea" },
      ],
    },
  ],
};

// Adicionar ao registry
export const BOX_SCHEMAS: Record<string, BoxSchemaDef> = {
  // ... anteriores
  team: TEAM_SCHEMA,  // NOVO
};
```

---

## Etapa 3 — TeamForm (wrapper ~12 linhas)

```tsx
export function TeamForm({ items, onChange, ...rest }: TeamFormProps) {
  return (
    <BoxFormMultiItem
      boxType="team"
      titleField="full_name"  // card mostra nome no cabeçalho
      items={items}
      onChange={onChange}
      modes={["manual", "excel"]}
    />
  );
}
```

Adicionar entries em `AbaBlocos.tsx` (seção ATENDIMENTO) e `EditBoxDialog.tsx` se ainda não tiver.

---

## Etapa 4 — Tool `query_team` (Opção B aprovada na Etapa 1)

```ts
export async function queryTeam(supabase, tenantId, query: string, limit = 10) {
  const { data: box } = await supabase
    .from("persona_boxes")
    .select("data")
    .eq("tenant_id", tenantId)
    .eq("box_type", "team")
    .eq("is_active", true)
    .single();
  
  if (!box?.data?.items) return [];
  
  const items = box.data.items as any[];
  const filtered = filterTeam(items, query);
  
  return filtered.slice(0, limit).map(item => {
    const result: any = {
      full_name: item.full_name,
      role: item.role,
      specialty: item.specialty,
      sector: item.sector,
      status: item.status,
      preferred_channel: item.preferred_channel,
      has_whatsapp: item.has_whatsapp,
      trigger_keywords: item.trigger_keywords,
      ai_can_forward: item.ai_can_forward,
    };
    
    // Privacidade: omite mobile se ai_can_forward = "Não"
    if (item.ai_can_forward !== "Não") {
      result.mobile = item.mobile;
    }
    
    return result;
  });
}

function filterTeam(items: any[], query: string): any[] {
  if (!query) return items;
  const q = query.toLowerCase();
  return items.filter(item => {
    const haystack = [
      item.full_name,
      ...(item.aliases || []),
      item.role,
      item.specialty,
      item.sector,
      ...(item.trigger_keywords || []),
      ...(item.languages || []),
    ].filter(Boolean).join(" ").toLowerCase();
    return haystack.includes(q);
  });
}
```

Registrar tool no master prompt (SUF15 já fez declaração dinâmica).

---

## Etapa 5 — Compiler `summarizeTeam`

```ts
function summarizeTeam(box: PersonaBox | null): string {
  if (!box?.data?.items?.length) return "";
  
  const items = box.data.items;
  const active = items.filter((i: any) => i.status === "Ativo");
  const sample = active.slice(0, 5).map((i: any) => 
    i.specialty ? `${i.full_name} (${i.specialty})` : i.full_name
  ).join(", ");
  
  return `## Equipe

Você tem acesso a ${items.length} profissionais cadastrados (${active.length} ativos). Use a tool \`query_team(query)\` pra buscar por especialidade, idioma, ou nome.

${sample ? `Exemplos ativos: ${sample}` : ""}`;
}
```

---

## Etapa 6 — Excel template + import

Edges genéricas. Adicionar exemplos em `generateExamples()`:

```ts
function generateExamples(boxType: string): any[][] {
  // ... outros
  if (boxType === "team") {
    return [
      ["Maria Silva", "Maria, Mari", "Atendimento", "Atendente", "Atendimento WhatsApp", "Matriz", "+5538999999999", true, "(38) 3749-6900 r.123", "maria@empresa.com", "Empresa", "WhatsApp", "Ativo", "Seg-Sex 8h-18h", "Português, Inglês", "Alta", false, "atendimento, dúvida, geral", "vendas técnicas", "Sim", ""],
      ["Dr. João Santos", "João, Doutor João", "Médico", "Cardiologista", "Cardiologia + Hipertensão", "Filial Centro", "+5538988888888", true, "", "joao@clinica.com", "Privado", "WhatsApp", "Ativo", "Ter, Qui 14h-18h", "Português", "Média", true, "consulta, cardiologia, coração, hipertensão", "rotina, check-up", "Confirmar", "Atende plano de saúde Unimed"],
    ];
  }
  return [];
}
```

E `buildInstructions()` ganha dicas Team:

```
- Status: Ativo / Férias / Afastado / Inativo
- Tem agenda própria: marque Sim apenas pra profissionais que vão receber agendamentos via Sprint Schedule (futuro)
- IA pode encaminhar direto: Sim (passa número direto), Confirmar (pergunta antes), Não (só humano)
- Especialidade é importante pra clínica e salão — IA usa pra direcionar
```

---

## Etapa 7 — Cleanup + deploy

### Antes do deploy

Pedro roda separado:

**1) Volume:**
```sql
SELECT 
  tenant_id,
  jsonb_array_length(COALESCE(data->'members', data->'items', '[]'::jsonb)) AS items
FROM persona_boxes
WHERE box_type = 'team' AND is_active = true;
```

**2) DELETE:**
```sql
DELETE FROM persona_boxes WHERE box_type = 'team';
```

**3) Confirma:**
```sql
SELECT COUNT(*) FROM persona_boxes WHERE box_type = 'team';
```

### Deploy

```bash
gh pr merge <PR> --squash --delete-branch
git checkout main && git pull origin main
supabase functions deploy ai-reply  # tool + compiler novos
git push origin main
```

Edges template/import genéricas. Pode redeployar `download-box-template` opcionalmente pra exemplos.

### Validação pós-deploy

1. Card "Equipe" aparece na seção ATENDIMENTO
2. Modo Manual: adiciona 1 profissional completo
3. Card colapsado mostra `full_name` (titleField funcionando)
4. Modo Excel: baixa modelo, valida 21 colunas + 2 exemplos
5. Sobe Excel teste com 5 profissionais
6. Confirma persistência
7. **Não-regressão:** Products + Services + FAQ + Objections continuam OK

---

## Critérios de aceite

- [ ] Etapa 1 confirmação aprovada
- [ ] TEAM_SCHEMA em box-schemas.ts (21 campos, 4 blocos)
- [ ] TeamForm wrapper ~12 linhas com `titleField="full_name"`
- [ ] Tool `query_team` com filterTeam próprio + privacidade do mobile
- [ ] summarizeTeam mostra count + ativos + sample (não despeja items)
- [ ] generateExamples + buildInstructions ganham entries pra team
- [ ] Build/tsc/vitest verde
- [ ] Pedro confirma DELETE
- [ ] PR description anota: `has_own_calendar` reservada pra Sprint Schedule futura

---

## Restrições

- ❌ Sem implementar lógica de calendar (Sprint Schedule é futura)
- ❌ Sem mexer em outras caixas
- ❌ Sem cross-field validation
- ❌ Sem tipo `phone` novo (dívida técnica futura)
- ✅ Pode adicionar tipo `email` se ainda não existir
- ✅ Mostra diff antes do commit
- ✅ Branch: `catalog-pr7-team-excel`
- ✅ PR título: `feat(catalog): Team + Excel + tool query_team (PR7)`

---

## Pós-merge — Próximo: PR8 (Forwards + Excel)

Forwards é caixa **parecida com Team mas pra contatos externos** (parceiros, fornecedores, técnicos terceirizados).

Memory item #21 confirmou separação: Team = interno, Forwards = externo. Schemas similares mas semântica diferente.

PR8 deve ser **rápido** porque reusa toda infra (~3-4h estimado).

---

## O que NÃO fazer neste PR

- ❌ Sprint Schedule / Google Calendar (`has_own_calendar` é só flag)
- ❌ Forwards, Delivery, Events, Custom (sequencial)
- ❌ Templates por nicho
- ❌ Tipo phone com validação E.164 (futuro)
