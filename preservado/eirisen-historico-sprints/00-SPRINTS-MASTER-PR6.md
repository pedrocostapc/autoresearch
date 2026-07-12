# Risen OS — Documento Mestre Atualizado

> Lê isso primeiro se chat compactar. Última atualização: 11/05/2026 — fim do dia.

---

## Identidade Pedro (CRÍTICO)

- Founder Risen OS (SaaS WhatsApp CRM multi-tenant)
- **DONO da plataforma**, não usuário. Vanderlei/etc são clientes dele
- Stack: React + TS + Tailwind + Supabase + Stripe + shadcn
- Dev via Lovable (build automático em push main)
- Project Supabase: `qbclqjkvovfriuhshkpw` (label "CRM Whats")
- Repo: `pedrocostapc/risen-ai-connect`
- Path local: `/Users/pedrocosta/Dev/risen/risencrm/risen-ai-connect`

Risen OS é nome do produto. **NÃO é dependência** do CRM — outro produto paralelo do Pedro. Cada um faz seu sync com Google Calendar de forma independente.

---

## Estado atual

| Sprint | PRs | Status |
|---|---|---|
| Sprint Catalog | 11 | ✅ COMPLETA |
| Sprint Schedule | 6 + 2 hotfixes | 🟡 PR6 RODANDO (último) |
| Sprint Forms | ~2-3 | 📋 Próxima |
| Sprint Arquétipos MVP Manual | 1 | 📋 (Pedro pediu) |
| Sprint Arquétipos Completa | TBD | 📋 Futura |

---

## SPRINT CATALOG (✅ COMPLETA)

**Refatorou 15 caixas de configuração da persona** em schema declarativo único.

### Arquitetura criada
- `box-schemas.ts` em `_shared/` — schema declarativo único consumido por UI + edges + compiler
- Cardinalities: `singleton | multi_item | multi_row | matrix`
- Componentes UI: `<QuestionBlock>`, `<BoxFormGeneric>`, `<BoxFormMultiItem>`, `<BoxFormMatrix>`, `<MultiItemListEditor>`, `<MatrixEditor>`, `<ExcelMode>`, `<TokenCounter>`
- 2 edges genéricas: `download-box-template` + `import-box-excel`
- 7 tools registradas
- Sistema de validação `required` automática
- TokenCounter pra cap de tokens

### 11 PRs (em ordem)

| PR | Caixa(s) | Commit |
|---|---|---|
| PR1 | Establishment + fundação | 98102d9 |
| PR2 | Hours + Links | 1d241a9 |
| PR3 | Pagamento | 95eabae |
| SUF16 | /admin/configuracoes + system_config | mergeado |
| PR4 | Products + Excel | 282cd10 |
| PR5 | Services | #210 |
| PR6 | FAQ + Objections + validação required | #211 |
| PR7 | Team (privacidade mobile) | #212 |
| PR8 | Forwards (parceiros externos) | #213 |
| PR9 | Delivery 3 caixas + bug fix SUF15 | #214 |
| PR10 | Events matriz 2D | #215 |
| PR11 | Custom + doc fechamento | #216 |

### Tools registradas (Catalog)

| Tool | Caixa |
|---|---|
| query_products | Products |
| query_services | Services |
| query_team | Team (privacidade mobile condicional) |
| query_forwards | Forwards (público) |
| query_delivery_items | Delivery Items (fallback Products) |
| query_delivery_areas | Delivery Areas |
| query_events | Events |

**Sem tool:** FAQ, Objections, Establishment, Hours, Links, Pagamento, Delivery Config, Custom (singletons ou volume baixo).

### Stats Catalog
- 224 testes verdes
- 18 valores enum `persona_box_type` antes de Schedule (depois 20)
- Cleanup completo do legacy
- Bug retroativo SUF15 corrigido

---

## SPRINT SCHEDULE (🟡 EM ANDAMENTO — PR6 rodando)

**Integração Google Calendar bidirecional** pra IA agendar via WhatsApp.

### Arquitetura
```
CRM Whats ←→ Google Calendar ←→ Risen OS
```
Google é hub. CRM e Risen OS independentes. Tenant pode editar em qualquer lugar (WhatsApp, Google Calendar app, Painel CRM, Painel Risen OS). Sync via webhook + cron pull.

### Infra Google
- GCP Project: `risen-services`
- Service Account: `risen-calendar-bot@risen-services.iam.gserviceaccount.com`
- Secret: `CRMWHATS_GOOGLE_SA_JSON`
- Token webhook: `GOOGLE_WEBHOOK_TOKEN` (setado por Pedro)
- Token cron: `RISEN_CRON_SECRET` (setado por Pedro)

### Decisões críticas

1. **2 caixas novas:** Calendar Config (singleton) + Calendar Links (multi-item)
2. **Provisionamento MANUAL** — sistema nunca cria calendar automático. Tenant clica.
3. **Opção C híbrida:** default sistema cria calendar próprio. Escape hatch: tenant compartilha calendar existente com SA.
4. **Email Team opcional** — dropdown filtra quem tem email, mostra disabled com aviso ⚠️ pra quem não tem.
5. **Tabela `professional_calendars`** separada do schema declarativo (estado dinâmico de sync).
6. **`extendedProperties.private.risen_source = "crm_whats"`** identifica eventos criados pelo CRM.
7. **A5 — NÃO espelha eventos manuais do Google.** Tenant cria evento direto no Google Calendar app (almoço, dentista pessoal) — CRM ignora. Só rastreia eventos criados pelo CRM.
8. **Conflict resolution:** last-write-wins via timestamps de origem + etag stamping no push (anti-reentrância).
9. **Auto-pick `resource_id` zero-padded** ("01", "02"... "NN") quando `max_parallel_resources > 1`.
10. **Hotfix 2:** removeu `default_duration_minutes` da Calendar Config. Sem fallback global. Duration vem de Services/Events ou IA pergunta.

### Estrutura buffer/resources

| Campo | Lugar | Significado |
|---|---|---|
| `buffer_before_minutes` | Calendar Config | Tempo de preparo antes do agendamento |
| `buffer_after_minutes` | Calendar Config | Tempo de recolhimento depois |
| `max_parallel_resources` | Calendar Config | Quantos agendamentos paralelos cabem no mesmo horário (chopp delivery 10 máquinas, salão+piscina, etc) |

### 6 PRs + 2 hotfixes

| Item | Entrega | Status |
|---|---|---|
| PR1 #217 | Fundação Google + tabela `professional_calendars` + edge provision + helper google-auth | ✅ Mergeado |
| Hotfix #218 | Fix djwt URL (deno.land vs esm.sh) | ✅ Mergeado |
| PR2 #219 | Caixa Calendar Config (singleton) + nova seção AGENDA | ✅ Mergeado |
| PR3 #220 | Caixa Calendar Links + UI provisionamento (componente próprio) | ✅ Mergeado |
| Hotfix #221 | Buffer separado (before/after) + max_parallel_resources | ✅ Mergeado |
| Hotfix #223 | Remove `default_duration_minutes` (sem fallback global) | ✅ Mergeado |
| PR4 #222 | Tabelas `appointments` + `appointment_google_sync` + edge push CRM→Google | ✅ Mergeado |
| PR5 #224 | 3 edges (webhook + setup + cron pull) + tabela `webhook_channels` + cron 10min | ✅ Mergeado |
| **PR6** | **Tools IA + compiler (search/create/reschedule/cancel + emite Config/Links no contexto)** | **🟡 Code rodando** |

### Tabelas criadas

| Tabela | Função |
|---|---|
| `professional_calendars` | Liga calendar Google a profissional/estabelecimento. RLS pattern padrão. |
| `appointments` | Agendamentos do CRM. RLS pattern padrão. |
| `appointment_google_sync` | Mapping CRM ↔ Google event. RLS DENY-by-default (só service_role). |
| `webhook_channels` | Registros de channel push Google. RLS DENY-by-default. |

### Edges criadas

| Edge | Função |
|---|---|
| `google-calendar-provision` | Cria calendar Google + compartilha (modo create OR use_existing). Hotfix A2 chama webhook-setup interno após sucesso. |
| `google-calendar-push` | Push CRM→Google (create/update/delete event). |
| `google-calendar-webhook` | Recebe push Google→CRM (verify_jwt=false, valida X-Goog-Channel-Token). |
| `google-calendar-webhook-setup` | Registra channel via events.watch. |
| `google-calendar-pull-conciliation` | Cron 10min — varre eventos modificados + renova channels < 24h. Auth via X-Cron-Secret. |

### Cron job

```sql
-- agendado, ativo, rodando a cada 10min
SELECT cron.schedule(
  'schedule-pull-conciliation',
  '*/10 * * * *',
  $$ ... net.http_post com X-Cron-Secret ... $$
);
```

**Importante:** secret `RISEN_CRON_SECRET` hardcoded no SQL da definição do cron (visível em `SELECT * FROM cron.job` pra super_admin). Hardening futuro: mover pra Supabase Vault.

### Helpers criados

- `_shared/google-auth.ts` — JWT signing + access token cache 1h
- `_shared/calendar-reconcile.ts` — lógica de reconciliação compartilhada entre webhook + cron pull

### PR6 — 4 tools IA + compiler

**Tools:**
- `search_team_slots(professional_id?, service_id?, date_range, duration_minutes?)` — busca slots livres
- `create_appointment(professional_id?, service_id?, customer_name, customer_phone, start_at, end_at, ...)` — cria + push pro Google
- `reschedule_appointment(appointment_id, new_start_at, new_end_at, reason?)` — update + push
- `cancel_appointment(appointment_id, cancellation_reason?)` — cancel + delete event

**Lógica de slots:**
1. Lista profissionais (filtra por specialty se service_id, status=Ativo, has_own_calendar=true)
2. Pra cada um: parseia service_hours (regex simples) ∩ Establishment.hours
3. Apply buffer_before + buffer_after da Calendar Config
4. Consulta Google freebusy API
5. Retorna slots livres ordenados por proximidade + priority

**Auto-pick resource:**
- Se `max_parallel_resources > 1` e `resource_id` vazio
- Query appointments com sobreposição de janela + status != cancelled
- Itera 1 a N, retorna primeiro livre como "01", "02", etc

**Compiler:**
- `formatCalendarConfig` emite no contexto (timezone, buffers, política, autonomia IA)
- `formatCalendarLinks` emite calendars provisionados disponíveis
- Tools só declaradas se `calendar_links` tem rows com status `provisioned`/`shared`

**Decisões importantes:**
- A1: Service role auth na invocação edge→edge
- A2: Parser regex simples de service_hours (~80% casos, falsos positivos cobertos por Google freebusy)
- A3: Duration prioriza Services→Events→IA pergunta (sem fallback global)
- A4: resource_id zero-pad "01" a "NN"
- A5: Tools retornam professional_name (IA responde natural)
- G3: Dedup create_appointment (customer_phone + start_at ±5min + últimos 60s)
- G4: Slot recheck só local (não Google) — race rara

### Smoke real pendente

Pedro zerou cobaias. Smoke vira follow-up quando recriar tenant cobaia com:
- Calendar Config preenchida
- 1 calendar provisionado
- Team item com has_own_calendar=true
- WhatsApp ativo

---

## Estado atual do sistema

- **23 tenants ativos**
- **14 em blocks** como cobaias (Pedro zerou recentemente)
- **9 em manual** com clientes reais
- Vanderlei principal em manual (29k chars de prompt, 2401 produtos)
- Stripe LIVE
- 224 testes verdes
- 20 valores enum `persona_box_type` (depois do PR1+PR2 Schedule)

---

## Próximas sprints (após PR6 mergear)

### Sprint Arquétipos MVP Manual (~1 dia) — IDEIA do Pedro
- Campo `manual_archetype_prompt` em `tenants` (coluna nova)
- Card simples na aba PERSONA pra colar texto livre
- Compiler prepend ao master prompt
- Vanderlei pode migrar pra blocks mantendo prompt customizado
- Pedro escreve prompt pros tenants iniciais (super admin)

### Sprint Forms (~2 dias)
- Caixa Formulários (multi-item, perguntas configuráveis)
- OTP por email (Resend pronto, ~1h pra wrapper + 2 templates)
- Endpoint público pra submissões
- Email confirmação ao lead + notificação ao tenant

### Sprint Arquétipos Completa (~1-2 semanas)
- Tabela `attendant_archetypes`
- 7 arquétipos seed (Pessoal-Filtro, Pessoal-Direto, Loja-Triagem, Loja-Vendedora, Clínica, Restaurante, Profissional)
- Caixa Triagem nova (fluxos estruturados)
- Migração de tenants em manual_archetype_prompt → arquétipos estruturados

---

## Aprendizados meta-sessão

- Pedro pede SQL em **caixas separadas** (uma query por bloco)
- Pedro é DONO da plataforma, não tenant final
- Etapa 1 com confirmações grep/SQL **sempre** antes de codar (descobriu conflito system_config no SUF16, bug retroativo SUF15 no PR9, erro de URL djwt no PR1 Schedule)
- DELETEs manuais via SQL Editor (Pedro assume — memory item)
- ALTER TYPE em queries separadas, fora de transação
- Pedro autoriza apagar dados de cobaias quando refatora caixa
- Não propor Risen OS como dependência (sistemas independentes)
- Pedro corrige direto quando Claude assume errado
- Quando schema tem variações por campo (ex: `tem_pix=false`), formatter custom no compiler

---

## Sequência canônica de PR (pattern testado 17 vezes)

1. Claude escreve prompt em `/mnt/user-data/outputs/claude-code-<sprint>-pr<n>.md`
2. Pedro cola pro Code
3. Code reporta **Etapa 1** (findings via grep/SQL + decisões pendentes)
4. Claude valida decisões com Pedro
5. Code implementa Etapas 2-N
6. Code mostra **diff completo**
7. Code confirma **build/tsc/test verde**
8. Pedro roda DELETE manual / ALTER TYPE / Migration no SQL Editor (queries separadas)
9. Pedro confirma com SELECT
10. Code mergeia + deploya
11. Pedro testa no painel (smoke)
12. Documento de continuidade atualizado quando marco importante

**Nunca pular Etapa 1.** Descobriu bugs em múltiplos PRs.

---

## Documentos de referência

Em `/mnt/user-data/outputs/`:

| Documento | Uso |
|---|---|
| **`00-SPRINTS-MASTER-PR6.md`** | **Este documento (mais atual)** |
| `00-CONTINUIDADE-10maio-pos-pr9.md` | Continuidade anterior (até Catalog PR9) |
| `00-CAIXAS-ESTRUTURA-FINAL.md` | Schemas completos das 17 caixas |
| `claude-code-catalog-pr1.md` a `pr11.md` | Prompts Catalog |
| `claude-code-schedule-pr1.md` a `pr6.md` | Prompts Schedule |
| `claude-code-schedule-hotfix-calendar-config.md` | Hotfix 1 (buffers) |
| `claude-code-diagnostico-resend.md` | Diagnóstico Resend |
| `contexto-gcal-para-crm.md` | Contexto Google Calendar (upload Pedro) |

---

## Como retomar após compactação

### Passo 1 — Lê memory + este documento
Memory items #1-30 cobrem PRs Catalog em detalhe.
Este documento cobre tudo até PR6 Schedule.

### Passo 2 — Confirma estado com Pedro

```
Pedro, voltando do ponto onde paramos:
- Sprint Catalog completa (11 PRs)
- Sprint Schedule: 5 PRs + 2 hotfixes mergeados (PR1-PR5)
- PR6 Schedule (último — tools IA + compiler) rodando agora no Code
- Smoke real pendente (Pedro zerou cobaias)

Status atual? PR6 já mergeou? Quer ir pra próxima sprint (Arquétipos MVP Manual ou Forms)?
```

### Passo 3 — Aja baseado na resposta

| Resposta | Ação |
|---|---|
| "PR6 ainda rodando" | Aguarda diff, valida |
| "PR6 mergeou" | Sprint Schedule COMPLETA. Pergunta qual próxima sprint |
| "Faz Arquétipos MVP Manual" | Escopo simples (~1 dia): coluna em tenants + card UI + compiler prepend |
| "Faz Forms" | Escopo conhecido (~2 dias): caixa Formulários + Resend wrapper + 2 templates |
| "Pausa" | Aguarda |

### Passo 4 — Nunca recomeçar do zero
Sprint Catalog (11 PRs) + Sprint Schedule (5 PRs + 2 hotfixes) em produção. Foco em **terminar** o que tá rodando.

---

## NÃO FAZER

- ❌ Recomeçar do zero qualquer caixa
- ❌ Propor refator estrutural sem necessidade
- ❌ Migrar Vanderlei pra blocks antes da Sprint Arquétipos Completa (ou MVP manual quando vier)
- ❌ Pular Etapa 1 de confirmação
- ❌ Juntar múltiplos SQLs no mesmo bloco
- ❌ Sugerir Risen OS como dependência (sistemas independentes)
- ❌ Provisionar calendar automático (decisão crítica: manual sempre)
- ❌ Espelhar eventos pessoais do Google no CRM (decisão A5 PR5)
