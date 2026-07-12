# Risen — Continuidade de Trabalho (10/05/2026 noite)

> Documento de retomada caso o chat seja compactado ou perdido.
> Lê isso primeiro antes de reabrir conversa em nova sessão.
>
> Este documento substitui versões anteriores. Usar este como referência mais atual.

---

## Estado em 1 frase

Sprint Catalog Onda 1 quase fechada — 3 de 4 PRs + 2 SUFs mergeados. Só falta **PR4 (Products + Excel)** pra destravar os 30k itens da loja Vanderlei.

---

## Sprints fechadas em 09-10/05/26

### Sprints anteriores ao Sprint Catalog
- SUF8 (paginação inbox), SU8.3 (apikey)
- SUF9 (grupos JID)
- SUF10/10b/10c/10d (rename grupo)
- SU8.4a (delete helper)
- SU7b (UI imagem)
- SU7c-1 (áudio Deepgram + cobrança)
- SU7c-1 hotfix (duplicação)
- SU7c-1b (UI áudio)

### Sprint Catalog (em curso)
| Sprint | PR | Commit | Status |
|---|---|---|---|
| SUF15 (pré-Catalog: master prompt + tools) | #204 | 0267125 | ✅ Mergeado e deployado |
| PR1 (fundação + Establishment) | #205 | 98102d9 | ✅ Mergeado e deployado |
| PR2 (Hours + Links) | #206 | 1d241a9 | ✅ Mergeado e deployado |
| PR3 (Pagamento - caixa nova) | #207 | 95eabae | ✅ Mergeado e deployado |
| SUF16 (system_config + página /admin/configuracoes) | #208 | (mergeado) | ✅ Mergeado |
| **PR4 (Products + Excel) ⭐** | - | - | 🟡 **Prompt pronto, aguardando Code rodar** |

---

## Estado real do sistema

### Billing/Stripe — 🟢 MADURO (não tocar)
- Stripe LIVE em produção (2 cobranças pagas R$ 123 em 30d)
- 6 planos SA2 seedados, pacotes SI4
- Ledger + lots FIFO + auto-recharge + courtesy + trial funcionando
- Cron expire-lots-daily rodando 5h UTC
- Markup 3.3× aplicado correto
- Margem nos relatórios SI4: ~857%

### Persona Builder — 🟡 EM REFATORAÇÃO via Sprint Catalog
- Antes: 12 box types, schemas Zod espalhados no front
- Depois: 17 box types em 4 seções, schema declarativo canônico (`_shared/box-schemas.ts`)
- Atualmente refatoradas: establishment, hours, links, pagamento (4 de 17)
- Próxima: products (PR4 prestes a rodar)

### Distribuição (10/05/26)
- 23 tenants ativos (14 em blocks como cobaias, 9 em manual com clientes reais)
- 9 tenants em manual têm 200+ produtos no system_prompt direto (não usam blocks)

### SUF15 implementou
- Master prompt declara dinamicamente quais tools o tenant tem (com guard `persona_mode='blocks'`)
- Tool `query_delivery_items` registrada com fallback Products filtrado por `disponivel_pra_delivery=true`
- Tool query_products mantém String.includes() (refator tsvector vira sprint futura se virar gargalo)

### SUF16 implementou
- Página `/admin/configuracoes` (4º item na seção Admin, abaixo de Insights Backfill)
- 9 colunas adicionadas em `system_config` (singleton existente):
  - `support_whatsapp_number` (text, default `+5538998940667`)
  - `excel_max_mb_<box>` × 8 caixas (int, CHECK 1-100, defaults 5/5/5/2/3/2/2/2)
- Hooks `useSystemConfig` + `useUpdateSystemConfig`
- Helper `EXCEL_BOXES` em `src/features/admin/lib/excelBoxes.ts` (pra reuso no PR4)
- Read-only se não super admin

---

## Decisões de produto registradas (10/05/26)

### Estrutura final de caixas (17 caixas, 4 seções)

```
SEÇÃO IDENTIDADE
├── 1. Establishment      (texto curto)        ✅ refatorada PR1
├── 2. Hours              (perguntas, 2 turnos)✅ refatorada PR2
├── 3. Links              (texto curto)        ✅ refatorada PR2
└── 4. Pagamento [NOVA]   (perguntas)          ✅ adicionada PR3

SEÇÃO O QUE VOCÊ OFERECE
├── 5. Products           (Excel)              🟡 PR4 prestes a rodar
├── 6. Services           (Excel)              📋 PR5
├── 7. Delivery Items [NOVA] (Excel - fallback Products) 📋 PR9
├── 8. Delivery Areas [NOVA] (Excel)           📋 PR9
├── 9. Delivery Config [NOVA] (perguntas)      📋 PR9
└── 10. Events            (perguntas)          📋 PR10

SEÇÃO ATENDIMENTO
├── 11. Team              (Excel, 21 campos)   📋 PR7
├── 12. Forwards          (Excel)              📋 PR8
├── 13. FAQ               (Excel)              📋 PR6
├── 14. Objections        (Excel)              📋 PR6 (junto FAQ)
├── 15. Formulários [NOVA] (form especializado)📋 Sprint Forms (separada)
└── 16. Agenda [NOVA]     (Google Calendar via SA) 📋 Sprint Schedule (separada)

SEÇÃO PERSONALIZE
└── 17. Custom            (texto livre)        📋 PR11
```

### Schema Products final (17 colunas)

**Apenas Nome obrigatório.**

- **Bloco 1 Identificação:** Nome ✅, SKU, Marca, Categoria livre, Descrição
- **Bloco 2 Preço:** Preço normal, Preço com desconto, Condição do desconto, Unidade
- **Bloco 3 Disponibilidade:** Disponível? (Sim/Não/Sob encomenda), Estoque, Disponível pra delivery? (Sim/Não)
- **Bloco 4 Atributos:** Tempo de preparo, Restrições alimentares, Ingredientes
- **Bloco 5 Variáveis extras:** Var 1, Var 2, Var 3 (nomes livres do tenant)

Variantes ("blusa preta" / "blusa laranja") = linhas separadas.

### Decisões UX universais
- Cada campo vira **pergunta humana** ("Tem estacionamento?"), não label de form
- Dropdown/botão Sim/Não/etc como default
- Texto livre só quando não cabe estruturado
- Accordions com contador "X de Y respondidas"
- Componente `<QuestionBlock>` reusável + `<BoxFormGeneric>` schema-driven
- Master prompt usa pergunta humana no contexto

### Decisões técnicas
- **Sem mapeamento inteligente Excel** — cliente baixa modelo, preenche, sobe
- **Re-import substitui tudo** — sem upsert, transação atômica
- **Botão "Mande pra equipe arrumar"** abre wa.me com número do super admin
- **Caixa Pagamento centralizada** — outras caixas referenciam, não duplicam
- **Delivery virou 3 caixas** — Items (reusa Products), Areas (Excel), Config (singleton)
- **CatalogItemSchema afrouxa price em todas** (Services + Products + Delivery)
- **Hours suporta 2 turnos** (almoço fechado)
- **Cada caixa tem seu modelo Excel próprio** (não 1 Excel grande)
- **Bloco "Direcionamento IA"** em todas multi-item (palavras-chave + autonomia + restrições)
- **Cardinality enum:** `singleton | multi_item | multi_row` (Custom é multi_row)

### Sprint Templates por Nicho
NÃO escopada ainda. Vira sprint separada **depois** de Catalog + Forms + Schedule. Recomendação Nível 2: presets pré-preenchidos por nicho. Esforço M (~3-4 dias).

### Google Calendar (pra Sprint Schedule)
- API configurada via Service Account no projeto Supabase
- Secret: `CRMWHATS_GOOGLE_SA_JSON`
- **Tenants NÃO conectam calendar pessoal**
- Sistema usa SA pra criar calendars próprios pro estabelecimento (1 por profissional com `tem_agenda_propria=true`)
- Calendars owned pela SA, tenant vê só pela UI do CRM
- Cliente final nunca acessa
- OAuth pessoal vira fase 2 opcional
- Sprint Schedule MVP só com SA — economia 3-5 dias

---

## Sprint Catalog Onda 1 — Status

### Concluído
- ✅ PR1: fundação (`box-schemas.ts`, `<QuestionBlock>`, `<BoxFormGeneric>`) + Establishment (16 campos)
- ✅ PR2: Hours (2 turnos com `<WeeklyHoursInput>`) + Links (13 fixos + 1 link_list em 5 blocos)
- ✅ PR3: Pagamento (caixa nova, 21 campos em 5 blocos, formatter custom com supressão condicional)
- ✅ SUF16: página `/admin/configuracoes` + `system_config` estendida

### Faltando — PR4 (o destravante)
**Prompt pronto em `/mnt/user-data/outputs/claude-code-catalog-pr4.md`.**

PR4 entrega:
1. Refator Products pro schema declarativo (17 campos em 5 blocos, `cardinality: multi_item` primeira caixa)
2. Edge `download-box-template` — gera XLSX com aba Dados + aba Instruções, exemplos pré-preenchidos
3. Edge `import-box-excel` — valida tamanho via `system_config.excel_max_mb_products`, parseia, substitui tudo
4. UI: 3º modo "Excel" no modal Products (junto com Manual + Colar Lista)
5. Botão "Mande pra equipe arrumar" abrindo `wa.me/<system_config.support_whatsapp_number>`
6. Smoke real: Pedro tem Excel da loja Vanderlei (~30k itens) pra testar

Pedro tem o Excel pronto, vai testar com volume real após PR4 mergear.

---

## Sprint Catalog Onda 2 — Backlog

7 PRs spread em ~4 dias úteis. Todos reusam fundação + Excel template/import do PR4:

- **PR5** — Services + Excel (~4-6h, mesmo padrão Products)
- **PR6** — FAQ + Objections + Excel (juntos, estrutura quase idêntica)
- **PR7** — Team + Excel (modelo de 21 campos do Pedro pronto, com flag `tem_agenda_propria`)
- **PR8** — Forwards + Excel (contatos externos)
- **PR9** — Delivery (3 caixas: Items + Areas + Config)
- **PR10** — Events (51 campos em accordions, sem Excel — só perguntas)
- **PR11** — Custom (migra pro padrão schema declarativo)

---

## Backlog adicional (não-Catalog)

### Sprint Forms (~2 dias)
- Caixa Formulários (perguntas configuráveis pelo tenant)
- OTP via Resend (Resend já 80% pronto, send-auth-email com 6 templates)
- Email final ao cliente com confirmação (sem PDF — texto puro Resend)
- Sem fluxo externo, tudo via WhatsApp + email

### Sprint Schedule (~3-4 dias)
- Caixa Agenda (multi-row se tenants com agenda própria, singleton senão)
- Integração Google Calendar via Service Account (já configurada)
- Tools encadeadas: search_services → search_team → get_calendar_slots → create_appointment
- Sync bidirecional via webhook (Pedro tá vendo padrão em outro sistema dele)

### Sprint Templates por Nicho (~3-4 dias)
- Presets pré-preenchidos por nicho (Clínica/Loja/Restaurante/Vendedor)
- Onboarding aplica preset
- Editor super admin cria/edita presets
- Reusa fundação Catalog (sem mudar schema declarativo)

### Cleanups oportunísticos (não-bloqueantes)
- Versionar `has_sufficient_credits` + `debit_credits` em migration retro
- Cron secret `x-cron-secret` pra vault
- Detalhe payment method (last4/brand)
- Remover `create-checkout-session` legacy + hook órfão
- Verificação de preços OpenAI quebrada no painel `/admin/ai-infra`
- Logs debug SUF10c/d antigos
- Dívida técnica: `getTierForModel` heurística (memory item #4)

### Sprints futuras não escopadas
- SG1 Gemini (Flash-Lite/Flash/Pro)
- SU7c-2 vision (IA processa imagens recebidas)
- SU7c-3 send_image (depende Sprint Catalog mergear)
- pgvector (depois tsvector mostrar limite)

---

## Contexto crítico do projeto

### Identidade Pedro
- Founder Risen OS (SaaS WhatsApp CRM multi-tenant) + PC Construtora
- **DONO da plataforma**, não usuário. Vanderlei/Construai/etc são clientes dele
- Pedro envia mensagens pelo celular, não pelo CRM (importante pra logic de takeover)

### Stack
- React + TS + Tailwind + Supabase + Stripe + shadcn
- Frontend dev via Lovable (build automático em push em main)
- Self-hosted Evolution API: `wa.crm.risenmidia.com.br`
- Deepgram Nova-3 transcrição (com Whisper fallback)
- Anthropic Claude (Haiku 4.5, Sonnet 4.6, Opus 4.6) + OpenAI

### Infraestrutura
- Project Supabase: `qbclqjkvovfriuhshkpw` (label "CRM Whats")
- Repo: `pedrocostapc/risen-ai-connect`
- Path local: `/Users/pedrocosta/Dev/risen/risencrm/risen-ai-connect`

### Aprendizados meta-sessão
- `wholesale_cost_cents_usd_micros` é micros de USD direto (1 USD = 100M micros), NÃO micros de cents — atenção a unidade em cálculos
- `replace_all` com indentação diferente perde ocorrências — sempre `grep -n` antes/depois
- `EdgeRuntime.waitUntil(promise)` em fire-and-forget
- Migration **antes** do deploy se schema mudou
- `supabase db push` falha sem `SUPABASE_DB_PASSWORD` — usar SQL Editor manual
- Quando Pedro corrige ("não é nada disso"), parar e reler do último ponto confirmado
- **NÃO propor SA1 como sprint** — está pronto em produção
- Pedro é DONO, falar como SaaS owner não como tenant final
- DELETEs de migration ficam manuais via SQL Editor (Pedro assume — memory item #10)
- Etapa 1 com confirmações grep/SQL antes de codar **sempre** evita conflitos (SUF16 achou colisão de nome `system_config`)

---

## Documentos de referência (em `/mnt/user-data/outputs/`)

- `00-CAIXAS-ESTRUTURA-FINAL.md` — estrutura definitiva 17 caixas
- `00-CONTINUIDADE-10maio.md` — continuidade anterior (deste mesmo dia, mais cedo)
- `raio-x-consolidado.md` — relatório Code: billing + persona + master prompt + tools
- `raio-x-boxes-refatoracao.md` — relatório Code: anatomia 12 caixas atual
- `raio-x-boxes-anatomia-completa.md` — Code: schemas Zod literais + samples
- `raio-x-gaps-decisoes-novas.md` — Code: 8 gaps das decisões novas
- `claude-code-suf15-pre-catalog.md` — prompt SUF15 (executado)
- `claude-code-catalog-pr1.md` — prompt PR1 (executado)
- `claude-code-catalog-pr2.md` — prompt PR2 (executado)
- `claude-code-catalog-pr3.md` — prompt PR3 (executado)
- `claude-code-suf16-system-config.md` — prompt SUF16 (executado)
- `claude-code-catalog-pr4.md` — **prompt PR4 (PRONTO, aguardando Code rodar)**

---

## Próximo passo concreto

**PR4 prestes a rodar.** Pedro precisa colar pro Code o prompt em `claude-code-catalog-pr4.md`.

Mensagem pra Code:

```
Roda PR4 da Sprint Catalog Onda 1 conforme prompt em prompts/claude-code-catalog-pr4.md (cola conteúdo se não acessar arquivo).

Branch: catalog-pr4-products-excel

PR4 fecha Onda 1. Maior PR da Sprint Catalog. Cobre:
- Refator Products pro schema declarativo (17 campos em 5 blocos, cardinality multi_item primeira caixa)
- 2 edges novas: download-box-template + import-box-excel (consomem system_config do SUF16)
- UI: 3º modo "Excel" no modal + botão "Mande pra equipe arrumar"
- Tool query_products mantém String.includes() (refator tsvector vira sprint futura)

Plano:
- Etapa 1 (confirmação): schema atual Products, UI modal, SheetJS instalado, decisões pendentes
- Etapa 2: PRODUCTS_SCHEMA em box-schemas.ts
- Etapa 3: edge download-box-template
- Etapa 4: edge import-box-excel
- Etapa 5: UI 3 modos + Mande pra equipe
- Etapa 6: cleanup (DELETE manual rodado por Pedro) + deploy

Smoke real: Pedro tem Excel da loja Vanderlei (~30k itens).

Critérios:
- Build/tsc/vitest verde
- Diff antes do commit
- 3 edges deployadas (2 novas + ai-reply se compiler mudou)
- PR anota: Fecha Onda 1

Quando voltar com Etapa 1, eu valido. Esse PR é o maior — vai com calma.
```

---

## Como retomar conversa após compactação

1. Lê este documento (`00-CONTINUIDADE-10maio-pos-suf16.md`)
2. Memory items #18, #19, #22, #23, #24 cobrem detalhes técnicos dos PRs mergeados
3. Confirma com Pedro:
   - "Pedro, voltando do ponto onde paramos. Status: SUF16 mergeado, PR4 prestes a rodar. Quer que eu cole o prompt do PR4 pro Code agora ou tem outra prioridade primeiro?"
4. Após confirmação, cola prompt PR4 ou ajusta conforme novidade

**Não propor SA1 (está pronto). Não re-escopar coisas que já estão no backlog. Foco é PR4 fechar Onda 1.**

---

## Sequência canônica pra qualquer PR

1. Code reporta Etapa 1 (findings + decisões pendentes)
2. Pedro/Claude validam decisões
3. Code implementa Etapas 2+
4. Code mostra diff completo
5. Code confirma build/tsc/test verde
6. Pedro roda DELETE manual ou ALTER TYPE no SQL Editor (se aplicável)
7. Pedro confirma com SELECT
8. Code mergeia + deploya
9. Pedro testa no painel
10. Memory atualizado com PR # + commit + estado

Nunca pular etapa 1 (descobre conflitos antes de quebrar). Nunca pular validação SQL pre-deploy (descobre drift antes de deploy quebrar prod).
