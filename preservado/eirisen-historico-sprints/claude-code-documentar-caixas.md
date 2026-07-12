# Prompt Code — Documentar funcionamento de todas as caixas

> **Objetivo:** Code lê o repo e produz documentação técnica viva de todas as caixas do sistema. Documento fiel ao estado atual (não memória ou docs antigos).
>
> Sem branch, sem PR. É só leitura + escrita de doc.

---

## Tarefa

Ler arquivos canônicos do projeto e produzir documento em `docs/CAIXAS-FUNCIONAMENTO.md` cobrindo:

- Cada uma das ~18 caixas existentes
- Schema técnico (campos, tipos, required)
- Tool associada (se houver)
- Comportamento no compiler
- Tabelas auxiliares (se houver)
- UI (componente que renderiza)
- Edges relacionadas

---

## Onde ler

### Fonte 1 — Schema declarativo
`supabase/functions/_shared/box-schemas.ts`

Tem:
- Definições de cada `BoxSchemaDef`
- Cardinality (singleton / multi_item / multi_row / matrix)
- Flag `hasExcel`
- Blocos e campos
- Tipos de field
- Helpers e options

### Fonte 2 — Compiler
`supabase/functions/_shared/persona-compiler.ts` (ou `persona-tools.ts`)

Tem:
- ORDER de compilação
- Funções `formatX` que emitem texto pro prompt da IA
- Switch que liga box_type → formatter

### Fonte 3 — Hooks
`src/features/ai-settings/hooks/`

Tem:
- `usePersonaBoxes.ts` — union de `PersonaBoxType`
- `useBox/use<Caixa>.ts` — hooks específicos
- `personaBoxSchemas.ts` — Zod schemas

### Fonte 4 — Components
`src/features/ai-settings/components/blocos/`

Tem:
- Cards que renderizam cada caixa
- `EditBoxDialog.tsx` — mapping box_type → form

### Fonte 5 — Edges
`supabase/functions/`

Procura por:
- Tools que consultam caixas (`query_*`, `search_*`)
- Edges genéricas (`download-box-template`, `import-box-excel`)
- Edges específicas (Google Calendar, etc)

### Fonte 6 — Tabelas auxiliares
Migrations em `supabase/migrations/`

Caixas com tabelas próprias (não usam `persona_boxes`):
- Calendar → `professional_calendars`, `appointments`, `appointment_google_sync`, `webhook_channels`

---

## Formato do output

Cria `docs/CAIXAS-FUNCIONAMENTO.md` com esta estrutura:

```markdown
# Funcionamento das Caixas — Risen OS

> Documento gerado por análise estática do código em [DATA].
> Fonte da verdade: arquivos canônicos no repo.

## Sumário

| # | Caixa | Seção | Cardinality | Excel | Tools | Tabela auxiliar |
|---|---|---|---|---|---|---|
| 1 | Establishment | Identidade | singleton | ❌ | - | persona_boxes |
| ... | ... | ... | ... | ... | ... | ... |

## Arquitetura geral

[Como caixas vivem em persona_boxes (JSONB), schema declarativo, ORDER do compiler, etc.]

---

## Caixa 1 — Establishment

**Seção visual:** Identidade
**Cardinality:** singleton
**Flag hasExcel:** false
**Tabela:** persona_boxes (rows com box_type='establishment')

### Schema técnico

| Campo | Tipo | Required | Helper |
|---|---|---|---|
| nome_estabelecimento | text | ✅ | "Nome que aparece pros clientes" |
| cnpj | text | - | "Opcional" |
| ... | ... | ... | ... |

### Tool relacionada

Nenhuma. IA consome direto via compiler.

### Comportamento no compiler

Função `formatEstablishment` em `persona-compiler.ts:XXX`. 
Emite no master prompt:
\`\`\`
## Estabelecimento
[campos formatados]
\`\`\`

### UI

Componente `<EstablishmentForm>` em `src/features/ai-settings/components/blocos/EstablishmentForm.tsx`.
Usa `<BoxFormGeneric>` com schema declarativo.

### Edges relacionadas

Nenhuma específica. Edge genérica `download-box-template` e `import-box-excel` cobrem.

---

## Caixa 2 — Hours

[mesma estrutura]

---

[... continua pra todas as caixas ...]

---

## Tools por caixa

| Tool | Caixa consultada | Quando IA chama | Privacidade |
|---|---|---|---|
| query_products | Products | Cliente pergunta produto | - |
| query_team | Team | Cliente quer falar com alguém | Mobile oculto se ai_can_forward=Não |
| ... | ... | ... | ... |

## Edges por caixa

| Edge | Caixa(s) | Função |
|---|---|---|
| download-box-template | Todas com hasExcel | Gera XLSX |
| import-box-excel | Todas com hasExcel | Importa XLSX |
| google-calendar-provision | Calendar Links | Provisiona calendar Google |
| ... | ... | ... |

## Estado atual do sistema

- **Total caixas:** X
- **Caixas com Excel:** Y
- **Caixas com tool:** Z
- **Caixas com tabela auxiliar:** W
- **Última caixa adicionada:** Calendar Links (Sprint Schedule PR3)
```

---

## Etapa 1 — Confirmações antes de gerar doc

Antes de começar, reporta:

### A. Inventário

1. Lista todas as caixas encontradas em `box-schemas.ts` (nome + cardinality + hasExcel)
2. Conta total
3. Compara com union `PersonaBoxType` em `usePersonaBoxes.ts`
4. Aponta divergências (caixa em um mas não em outro)

### B. Onde salvar

Confirmar:
- `docs/CAIXAS-FUNCIONAMENTO.md` é local OK?
- Ou prefere `/mnt/user-data/outputs/CAIXAS-FUNCIONAMENTO.md` (acessível pro Pedro)?

### C. Quanto detalhe

Por caixa, posso variar nível de detalhe:

**Nível 1 — Síntese (~1 página por caixa)**
- Schema resumido (lista de campos sem helpers)
- Tool name (sem schema da tool)
- Componente UI (path apenas)
- Mais legível pra humano

**Nível 2 — Completo (~2-3 páginas por caixa)**
- Schema completo com helpers e options
- Schema da tool com JSON Schema de parâmetros
- Caminhos de arquivo + linhas
- Migrações relacionadas
- Útil pra developer onboarding

**Recomendação:** Nível 2. Documento extenso mas é referência. Tamanho final estimado: ~80-120 páginas markdown.

### D. Decisões pendentes
- Incluir info histórica (em qual PR a caixa foi criada)?
- Incluir exemplo de dados preenchidos por caixa?
- Incluir snapshots de UI (ASCII art aproximado)?

---

## Critérios de aceite

- [ ] Etapa 1 reportada e confirmada por Pedro
- [ ] Documento gerado contendo TODAS as caixas em box-schemas.ts
- [ ] Sumário inicial com tabela de visão geral
- [ ] Cada caixa cobrindo schema + tool + compiler + UI + edges
- [ ] Sem inventar — só info extraída do código
- [ ] Aponta caixas em estado inconsistente (em schema mas sem case no compiler, etc) se houver
- [ ] Tamanho estimado: 80-120 páginas dependendo do nível

---

## O que NÃO fazer

- ❌ Inventar comportamento que não está no código
- ❌ Documentar caixas planejadas mas não implementadas
- ❌ Misturar info de memória/docs antigos com leitura real
- ❌ Pular alguma caixa "porque é óbvia"
- ❌ Reescrever lógica das funções — só documentar O QUE elas fazem

---

## Pós-conclusão

Quando documento estiver pronto:
1. Reporta path final + tamanho (kb / linhas)
2. Lista as ~18 caixas documentadas
3. Aponta inconsistências encontradas (caixa em X mas não em Y)

Documento vira referência viva. Pode ser regenerado quando schema mudar (Sprint Forms, etc).
