# Raio-X · Boxes (Persona Builder) — Estado Atual e Refatoração

> **Modo:** read-only puro. NÃO criar branch, NÃO escrever código, NÃO rodar migrations.
> **Output:** relatório em `/home/claude/risen-ai/raio-x-boxes-refatoracao.md` + sumário no chat.

---

## Por que esse raio-x

Pedro decidiu refatorar todo o sistema de boxes. Hoje 12 tipos com Zod schemas próprios, formulários específicos, modos Manual/Colar Lista. Pedro precisa importar 30k itens de Excel pra caixa Products. Decisões já tomadas:

1. **Cada caixa terá schema declarado** que serve 3 propósitos: validação import, geração de modelo Excel, master prompt mapeando.
2. **Categoria livre** (cliente preenche o que faz sentido).
3. **Apenas Nome obrigatório** em Products, resto opcional.
4. **Re-import substitui tudo** (sem upsert).
5. **Sem mapeamento inteligente** (cliente baixa modelo, preenche, sobe).
6. **Botão "mande pro time arrumar"** pra clientes com Excel bagunçado (lead pra serviço).

Antes de escopar a sprint, Pedro precisa do estado real **anatomia completa de cada caixa**: schema atual, formulário, formatador no compiler, dependências.

---

## Investigação

### 1. Schemas Zod de cada caixa (12 tipos)

```bash
# Localizar os schemas
grep -rn "z.object\|z\.array\|z\.discriminatedUnion\|boxSchema" src/features/ai-settings/ --include="*.ts" --include="*.tsx" -l
```

Para CADA tipo (establishment, hours, links, services, products, delivery, events, team, forwards, faq, objections, custom):

- Caminho do arquivo onde o schema vive
- **Copiar o schema Zod inteiro** (se < 50 linhas)
- Listar campos: nome, tipo, obrigatório/opcional
- Validações inline (min, max, regex, etc)

**Especialmente importante:** o schema atual da caixa Products. Comparar com o schema novo decidido (4 blocos: Identificação, Preço, Disponibilidade, Variáveis).

### 2. Formulários de cada caixa (UI)

```bash
find src/features/ai-settings -name "*.tsx" | xargs grep -l "BoxEdit\|BoxModal\|BoxForm\|EditBox\|PersonaBox" | head -20
```

Para cada caixa:
- Nome do componente
- Campos renderizados
- Padrão de save (onSubmit, onBlur, debounced)
- Validação client-side (zodResolver, manual)
- Modais Manual vs Colar Lista (especialmente Products, Services, Delivery)
- Toggles especiais (ex: "Controlar disponibilidade" em Products)

### 3. Formatadores no compilador (persona-compiler.ts)

```bash
grep -rn "function format\|formatBox\|case '" supabase/functions/_shared/persona-compiler.ts
```

Para cada tipo, copiar o formatador:
- Input: que JSON/objeto recebe
- Output: que markdown gera
- Se o tipo vira "tool-hint" (não despeja inline) ou "inline" (despeja conteúdo)
- Tamanho típico do output em caracteres

### 4. Schema do banco

```bash
grep -rn "persona_boxes\|persona_quiz" supabase/migrations/ --include="*.sql"
```

Reportar:
- CREATE TABLE final consolidado de `persona_boxes`
- Colunas: id, tenant_id, box_type, data (JSONB?), is_active, created_at, updated_at, etc
- Constraints, índices, RLS policies
- FKs (referencia tenant_ai_configs ou tenants direto?)
- Quaisquer triggers

### 5. Hooks e mutations

```bash
find src/features/ai-settings/hooks -name "*.ts"
```

Listar e descrever:
- `usePersonaBoxes` (busca caixas)
- `useUpsertPersonaBox` (cria/atualiza)
- `useDeletePersonaBox`
- Outros hooks relacionados

### 6. Quiz do negócio (5 capítulos)

```bash
grep -rn "quizStep\|wizardStep\|QuizWizard\|capítulo" src/features/ai-settings/ --include="*.tsx" --include="*.ts"
```

Reportar:
- Quais 5 capítulos existem
- Como cada capítulo gera blocos automaticamente
- Mapeamento capítulo → caixa(s)
- Persistência (auto-save? querystring?)
- Comportamento "Sua atendente já está configurada" (quando aparece, o que faz)

### 7. Persona modes

```sql
SELECT persona_mode, COUNT(*)
FROM tenant_ai_configs
GROUP BY persona_mode;
```

E:
- `persona_mode = 'manual'` lê de qual lugar (system_prompt direto)?
- `persona_mode = 'blocks'` lê de persona_boxes
- Como ai-reply alterna entre os dois?
- Existe path de migração manual → blocks?

### 8. Tool calling — tools de caixa

```bash
grep -rn "tools:" supabase/functions/ai-reply/ --include="*.ts" -A 30
```

Reportar:
- Lista das tools registradas hoje (raio-x anterior mencionou 5: 4 query_* + schedule_followup)
- Schema de cada tool (input + descrição)
- Que caixa cada tool consulta
- Como a busca acontece hoje (String.includes, slice, etc)

### 9. Caixas usadas em produção (volume real)

```sql
-- Quem usa qual caixa
SELECT box_type, COUNT(*) AS rows, COUNT(DISTINCT tenant_id) AS tenants_usando
FROM persona_boxes
WHERE is_active = true
GROUP BY box_type
ORDER BY rows DESC;

-- Tamanho das caixas
SELECT box_type,
       AVG(LENGTH(data::text))::int AS avg_chars,
       MAX(LENGTH(data::text)) AS max_chars,
       SUM(LENGTH(data::text)) AS total_chars
FROM persona_boxes
WHERE is_active = true
GROUP BY box_type
ORDER BY max_chars DESC;
```

### 10. Sample real de cada caixa

```sql
-- Pega 1 row preenchida de cada tipo, dos tenants mais ativos
SELECT box_type, data
FROM persona_boxes
WHERE is_active = true
ORDER BY box_type, LENGTH(data::text) DESC
LIMIT 50;
```

Cola exemplos reais. Crítico pra entender estrutura JSON real, não só Zod schema teórico.

### 11. Personality_style

```bash
grep -rn "personality_style\|personalityStyle\|Pessoal\|Clínica\|Restaurante\|Loja\|Vendedor" src/ supabase/ --include="*.ts" --include="*.tsx" --include="*.sql"
```

Reportar:
- Coluna existe? (em qual tabela)
- Valores possíveis
- Como influencia o prompt
- Quantos tenants em cada valor (SQL agregado)

### 12. Master prompt — onde o WHATSAPP_RULES vive

```bash
grep -rn "WHATSAPP_RULES\|MASTER_PROMPT\|systemPrompt\|buildSystemPrompt" supabase/functions/ --include="*.ts"
```

Reportar:
- Caminho exato do arquivo
- Conteúdo completo do master prompt + whatsapp_rules (se < 100 linhas)
- Quantas camadas o `buildSystemPrompt` concatena
- Ordem das camadas
- Se está hardcoded ou vem do banco

### 13. Capacidade de Excel/CSV no projeto

```bash
grep -rn "xlsx\|sheetjs\|papaparse" src/ supabase/functions/ package.json --include="*.ts" --include="*.tsx" --include="*.json"
```

- SheetJS (xlsx) está instalado?
- Existe import de Excel em qualquer lugar?
- Componentes de upload de arquivo?

### 14. Templates Excel — não existem ainda

Confirmar negativamente:
```bash
grep -rn "box-template\|box_template\|excel-template" src/ supabase/ --include="*.ts" --include="*.tsx" --include="*.sql"
```

Se voltar vazio → confirmado que não existe, sprint cria.

---

## Output esperado

```markdown
# Raio-X Boxes — Refatoração (10/05/2026)

## Sumário executivo
(2-3 linhas: o que está bom, o que mudará na refatoração)

## 1. Anatomia das 12 caixas

### establishment
- Schema Zod (caminho + copy)
- Formulário (caminho + campos)
- Formatador compiler (copy)
- Sample real (JSON)
- Status: pequeno/médio/grande, simples/complexa

### hours
(idem)

### links
(idem)

### services
(modos manual/colar lista, parser de texto)

### products
(modos manual/colar lista, toggle estoque, comparação com schema novo)

### delivery
(cardápio + áreas + pedido mínimo)

### events
### team
### forwards
### faq
### objections
### custom

## 2. Schema banco persona_boxes
(CREATE TABLE consolidado)

## 3. Hooks e mutations
(lista)

## 4. Quiz 5 capítulos
(detalhamento)

## 5. Persona modes (manual vs blocks)
(distribuição + caminhos)

## 6. Tool calling
(5 tools listadas + schema + qual caixa consultam)

## 7. Volume real em produção
(tabela de uso por caixa)

## 8. Personality_style
(estado atual)

## 9. Master prompt
(caminho + conteúdo + camadas)

## 10. Capacidade Excel
(SheetJS instalado? import existe?)

## 11. Gaps pra refatoração planejada
| Caixa | Schema atual | Schema novo (Pedro) | Esforço |
|---|---|---|---|
| products | 4 campos (Nome, Desc, Preço, Desconto) | 14 campos em 4 blocos | M |
| services | ? | ? | ? |
| ... | | | |

## 12. Recomendação de ordem
(qual caixa atacar primeiro na refatoração, quais migrar depois)
```

---

## Restrições

- ❌ Nenhuma branch
- ❌ Nenhuma migration
- ❌ Nenhum arquivo modificado
- ✅ Pode ler tudo
- ✅ Pode rodar SQL no projeto
- ✅ Copiar trechos é encorajado (especialmente schemas Zod + formatadores compiler + samples reais)
- ✅ Output em arquivo + sumário no chat com matriz de gaps

Pedro vai ler o relatório e decidir o desenho da Sprint Catalog (refatoração de boxes + import Excel + tools com tsvector + master prompt mapeando).
