# Risen — Continuidade de Trabalho (10/05/2026)

> Documento de retomada caso o chat seja compactado ou perdido.
> Lê isso primeiro antes de reabrir conversa em nova sessão.

---

## Onde estamos

**Sessão de 09-10/05/26**: fechamos 12 sprints (SUF8 → SU7c-1b), depois fizemos **2 raio-x consolidados** (billing/Stripe + boxes) pra mapear estado real do sistema.

Resultado: SA1 (Stripe/assinatura) **já está pronto em produção**, não precisa sprint nova. Próxima sprint real é **Sprint Catalog** (refatoração de boxes + import Excel + tools com tsvector).

---

## Sprints fechadas em 09-10/05

| Sprint | PR | Descrição |
|---|---|---|
| SUF8 | #185 | Paginação reversa do inbox |
| SU8.3 | #186 | Captura apikey em INSERT |
| SUF9 | #187+#188 | Envio pra grupos via JID |
| SUF10 | #189 | Subject autoritativo + gate |
| SUF10b | #190 | TTL 1h reativo |
| SUF10c | #191+#193 | Revalidação envio CRM + EarlyDrop |
| SUF10d | #194 | Gate em processManualSend |
| SU8.4a | #195 | Migra deleteMessageViaEvolution |
| SU7b | #196 | UI envio de imagem |
| SU7c-1 | #197 | Áudio → Deepgram → IA + cobrança |
| SU7c-1 hotfix | #198 | Fix duplicação áudio |
| SU7c-1b | #199 | UI configuração áudio |

---

## Estado real do sistema (do raio-x)

### Billing/Stripe — 🟢 MADURO (não precisa sprint)
- Stripe LIVE em produção (2 cobranças pagas em 30d, R$ 123)
- 6 planos SA2 seedados (Iniciante R$19,90, Crescimento R$49,90, Negócio R$99,90 × mensal/anual)
- Pacotes SI4 (1×R$99, 5×R$79, 10×R$59) funcionando
- Ledger + lots FIFO + auto-recharge + courtesy + trial
- Webhook robusto com idempotência
- Cron expire-lots-daily rodando 5h UTC
- Markup 3.3× aplicado correto
- Margem nos relatórios SI4: ~857% (custo wholesale R$ 10,35 vs cobrado R$ 99)

**Só sobrou cleanup pequeno (~3h):**
- Versionar `has_sufficient_credits` e `debit_credits` em migration retro
- Detalhe payment method (last4/brand)
- Remover `create-checkout-session` legacy + hook órfão
- Cron secret `x-cron-secret` exposto em pg_cron command (mover pra vault)

### Persona Builder — 🟢 BEM MODELADO mas precisa refatoração
- 12 box types com Zod schemas + RHF forms
- 8 inline (despejam markdown no prompt) + 4 tool-hint (services, products, delivery, events)
- 5 tools registradas: 4× query_* + schedule_followup, loop até 5 rounds
- **Busca em tools usa `String.includes()` em memória + slice(0, 10)** — não escala pra 30k

### Volume real em produção (10/05/26)
- **23 tenants ativos** (14 em `blocks` + 9 em `manual`)
- Caixa products: 2 tenants, max 71 itens hoje
- Caixa services: 3 tenants, max 47 itens hoje
- 30k itens da loja Vanderlei é o **primeiro caso extremo** que vai entrar

### Master prompt — 🟡 hardcoded
- `WHATSAPP_RULES` em `_shared/ai-config.ts`
- `buildSystemPrompt` concatena 9 camadas
- **Não editável via UI super admin** — Pedro quer mudar isso

### Tool calling / RAG — 🟡 tools sim, RAG não
- 5 tools registradas
- Sem pgvector, sem tsvector
- Busca em catálogo é `String.includes()` em memória
- Prompt máximo em prod: 86k tokens (relatório SI4 do Risen Midia, esperado)

### Distribuição modelos AI (7d)
- Haiku 4.5: 792 chamadas (66%) — R$ 0,051 médio
- Sonnet 4.6: 441 chamadas (36%) — R$ 0,19 médio
- Opus 4.6: 11 chamadas — R$ 7,16 médio (Pedro mudou de 4.7 pra 4.6 há 4 dias)
- Opus 4.7: 15 chamadas (resíduo de relatórios antigos pré-mudança)

---

## Decisões de produto tomadas

### Schema Excel da caixa Products (10/05/26)

**Apenas Nome obrigatório.** Resto opcional.

**Bloco 1 — Identificação:**
- Nome (obrigatório)
- SKU/código
- Marca
- Categoria (livre — cliente preenche o que faz sentido)
- Descrição curta

**Bloco 2 — Preço:**
- Preço normal
- Preço com desconto (opcional)
- Condição do desconto (livre — campo texto)
- Unidade

**Bloco 3 — Disponibilidade:**
- Disponível? (Sim/Não/Sob encomenda)
- Estoque (numérico)

**Bloco 4 — Variáveis extras:**
- Var 1, Var 2, Var 3 (nomes livres definidos pelo tenant)

**Removidos por decisão:**
- Parcelamento (vai em caixa "Formas de Pagamento" separada futura)
- Prazo de entrega (vira política geral, não por produto)

**Princípio:** variantes viram linhas separadas. "Blusa preta" e "blusa laranja" = 2 linhas, sem variantes complexas no schema.

### Outras decisões
- **Sem mapeamento inteligente Excel** — cliente baixa modelo, preenche, sobe. Se Excel bagunçado → erro claro.
- **Re-import substitui tudo** — sem upsert, mais simples.
- **Botão "mande pro time arrumar"** — lead pra serviço de implementação (cliente com Excel bagunçado paga você pra arrumar).
- **Categoria é livre** — cliente escreve "Bebidas alcoólicas", "Cimento", "Roupa feminina", o que fizer sentido pro nicho dele.

### Conflito de schema descoberto
**Services + Products compartilham `CatalogItemSchema` com `price` obrigatório.**

Decisão pendente:
- **Opção A:** split do schema — Services mantém price obrigatório, Products afrouxa
- **Opção B:** afrouxa price em ambos (Service "consulta sob orçamento" passa a ser válido)

Recomendação: **Opção B**. Mais flexível pra negócios reais (clínica, construtora).

---

## Sprint Catalog — desenho proposto

Sprint grande de refatoração. Quebrada em 5 PRs sequenciais, cada um mergeia separado.

### PR1 — Schema declarativo + refator Products
**Tamanho:** M-L (~1-2 dias)

- Cria `_shared/box-schemas.ts` como source of truth pra TODAS as caixas
- Refatora `CatalogItemSchema` de Products pra aceitar 14 campos do schema novo
- Migra `persona_boxes` rows existentes (2 tenants com Products) pra novo formato
- Atualiza form do front pra usar schema novo
- Atualiza compiler pra format dos novos campos
- **Não inclui Excel ainda**
- Build/tsc/test verde

### PR2 — Import Excel pra Products
**Tamanho:** L (~1-2 dias)

- Edge `download-box-template/{box_type}` gera XLSX vazio com headers + 3 linhas exemplo
- Edge `import-box-excel` recebe XLSX, parseia via SheetJS, valida headers, insere em batch
- UI: terceiro botão no modal Products → "Importar Excel" + "Baixar modelo"
- Re-import: DELETE WHERE tenant_id=X + INSERT em transação atômica
- Botão "mande pro nosso time arrumar" como alternativa (mailto ou WhatsApp pra você)
- Smoke real com Excel de 30k linhas (Vanderlei)
- Limite tamanho: 10MB (cobre ~50k itens)

### PR3 — RAG via tsvector
**Tamanho:** M (~1 dia)

- Migra Products + Services + Delivery pra tabela própria com tsvector index
- RPC `search_products(tenant_id, query, limit, cursor)` com ranking PT-BR
- Refatora tool `query_products` pra usar RPC em vez de `String.includes()`
- Paginação real com cursor
- Substitui slice(0, 10) por busca rankeada de top N

### PR4 — Master prompt editável super admin
**Tamanho:** M (~1 dia)

- Tabela `system_prompts` com versionamento
- UI no `/admin` pra editar master prompt + WhatsApp rules
- Edge `ai-reply` lê de tabela em vez de hardcoded
- Backward-compatible (fallback pra hardcoded se tabela vazia)

### PR5 — Replicar pros 3 catálogos restantes
**Tamanho:** M (~1 dia)

- Replicar approach do PR1 pra services, delivery, events
- Mesmas funções genéricas de Excel template + import
- Migrar dados existentes
- Tools refatoradas pra usar tsvector

**Total estimado: 5-7 dias de trabalho focado.**

---

## Backlog priorizado

### Próxima sprint
**Sprint Catalog** (5 PRs acima) — destrava 30k itens, prepara base pra escalar

### Cleanups oportunísticos (não-bloqueantes)
- Versionar `has_sufficient_credits` + `debit_credits` em migration retro
- Cron secret `x-cron-secret` pra vault
- Detalhe payment method (last4/brand)
- Remover `create-checkout-session` legacy + hook órfão
- Atualizar `seed-stripe-live.ts` outdated
- Limpar logs de debug `[suf10c-debug]` antigos
- Verificação de preços OpenAI quebrada (modelos GPT-5.4 ❌ no painel `/admin/ai-infra`)

### Sprints futuras (não escopadas)
- **SG1 Gemini** — adicionar Flash-Lite/Flash/Pro como provider
- **SU7c-2 vision** — IA processa imagens recebidas
- **SU7c-3 send_image** — IA envia imagem do catálogo (depende Sprint Catalog)
- **personality_style** — Pessoal/Clínica/Loja/Restaurante/Vendedor (decisão produto)
- **pgvector** — busca semântica (depois tsvector mostrar limite)
- **Painel admin Deepgram** — segregação SU7c-1 nos painéis
- **Quiz cobrindo mais caixas** — hoje 4 das 12

### Arquivado
- **SU8.4b/c/d** — UI delete + cenário A + cenário B (sem demanda real)

---

## Contexto crítico do projeto

### Identidade Pedro
- Founder Risen OS (SaaS WhatsApp CRM multi-tenant) + PC Construtora
- **DONO da plataforma**, não usuário. Vanderlei/CONSTRUAI/etc são clientes dele.
- Decisões de qualidade vs custo são suas, não dos clientes finais
- Pedro envia mensagens pelo celular dele, não pelo CRM (importante pra logic de takeover)

### Stack
- React + TS + Tailwind + Supabase + Stripe + shadcn
- Frontend dev via Lovable (build automático em push em main)
- Self-hosted Evolution API direto: `wa.crm.risenmidia.com.br`
- Deepgram Nova-3 transcrição (com Whisper fallback)
- Anthropic Claude (Haiku 4.5, Sonnet 4.6, Opus 4.6) + OpenAI (legado)

### Infraestrutura
- Project Supabase: `qbclqjkvovfriuhshkpw` (label "CRM Whats" no dashboard)
- Repo: `pedrocostapc/risen-ai-connect`
- Path local: `/Users/pedrocosta/Dev/risen/risencrm/risen-ai-connect`

### Aprendizados meta-sessão
- Pedro envia pelo celular, não pelo CRM
- `replace_all` com indentação diferente perde ocorrências — sempre `grep -n` antes/depois
- `EdgeRuntime.waitUntil(promise)` em fire-and-forget (lição SUF10c)
- Migration **antes** do deploy se schema mudou (lição SUF10b)
- `supabase db push` falha sem `SUPABASE_DB_PASSWORD` — usar SQL Editor manual
- Quando Pedro corrige ("não é nada disso"), parar e reler do último ponto confirmado
- Logs distintos por caller economizam tempo
- Lovable buida automático em push de main mas edges Supabase precisam `supabase functions deploy` separado
- `git add <path>` específico em vez de `-A` quando há untracked não relacionado
- "Field `wholesale_cost_cents_usd_micros` é micros de USD direto, não micros de cents" — atenção a unidades em cálculos
- **NÃO propor SA1 como sprint** — está pronto em produção
- Pedro é DONO, falar como SaaS owner, não como tenant final

---

## Documentos de referência

Salvos em `/mnt/user-data/outputs/`:
- `00-PROXIMAS-SPRINTS.md` — backlog completo (precisa atualizar com este doc)
- `00-CONTINUIDADE-suf8-su8.3-suf9-suf10.md` — narrativa pré-SU7c-1
- `raio-x-consolidado.md` — relatório de billing + persona + master prompt + tools (Code gerou)
- `raio-x-boxes-refatoracao.md` — relatório focado em boxes (Code gerou)
- `claude-code-su7c-1-audio.md` — prompt SU7c-1 áudio
- `claude-code-su7c-1b-audio-ui.md` — prompt SU7c-1b UI

---

## Próximo passo concreto

Pedro precisa **decidir conflito price obrigatório**:
- Opção A: split de schema (Services mantém, Products afrouxa)
- Opção B: afrouxa price em ambos

Após decisão, escrevo prompt do **PR1 da Sprint Catalog** (schema declarativo + refator Products) pra Code executar.

PR2-PR5 ficam em sequência conforme PR1 mergear e validar approach.

---

## Como retomar conversa após compactação

1. Lê este documento (`00-CONTINUIDADE-10maio.md`)
2. Lê `raio-x-consolidado.md` e `raio-x-boxes-refatoracao.md` se precisar de detalhe técnico
3. Confirma com Pedro: "Pedro, pegando do ponto onde paramos. Decidiu o conflito de schema price (Opção A split vs Opção B afrouxa ambos)? Pra eu escrever o prompt do PR1 da Sprint Catalog."
4. Após decisão, escreve prompt PR1 e procede

Não propor SA1 (está pronto). Não re-escopar coisas que já estão no backlog. Foco é Sprint Catalog.
