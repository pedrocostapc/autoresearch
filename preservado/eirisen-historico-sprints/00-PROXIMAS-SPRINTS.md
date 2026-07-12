# Risen — Próximas sprints (atualizado 09/05/2026 ~22h BRT)

> Backlog priorizado pós-SU7c-1b. Use junto com `00-CONTINUIDADE-suf8-su8.3-suf9-suf10.md`
> e a memória sumarizada no início desta conversa.

---

## Fechadas nesta sessão (09/05)

| Sprint | PR | Descrição |
|---|---|---|
| **SUF8** | #185 | Paginação reversa do inbox |
| **SU8.3** | #186 | Captura apikey em INSERT de instâncias novas |
| **SUF9** | #187+#188 | Envio pra grupos via JID resolution |
| **SUF10** | #189 | Subject autoritativo + gate amplo de revalidação |
| **SUF10b** | #190 | TTL 1h reativo via webhook receive |
| **SUF10c** | #191+#193 | Revalidação em envio CRM + fix EarlyDrop |
| **SUF10d** | #194 | Gate em processManualSend (Pedro envia pelo celular) |
| **SU8.4a** | #195 | Migra deleteMessageViaEvolution pro padrão SU8.1+ |
| **SU7b** | #196 | UI envio de imagem (paperclip + upload + signed URL) |
| **SU7c-1** | #197 | Áudio recebido → Deepgram → IA processa + cobrança FIFO |
| **SU7c-1 hotfix** | #198 | Fix duplicação de resposta IA em áudios |
| **SU7c-1b** | #199 | UI configuração áudio + toggle de habilitação |

---

## Fila imediata (infra/cleanup)

### 1. SU8.5 — Cleanup CRM_API_KEY env ⏳

**Objetivo:** depois de SU8.4a (migrou helper interno) ter movido o último uso interno do proxy `api.crm`, `CRM_API_KEY` (chave global) só é usado pelo path Cloud API agora.

**Escopo:**
- Confirmar quais edges ainda usam `Deno.env.get("CRM_API_KEY")` ou `CRM_API_BASE`.
- Remover de onde não precisa mais.
- Limpar typo `CRM_API_KE` no Supabase secrets.

**Dependências:** nenhuma — SU8.4a (✅) destravou.

**Tamanho:** curto (~1h).

---

### 2. SU8.4b/c/d — Delete de mensagem (UI + cenário A + cenário B) 📦

**Status:** arquivado. SU8.4 completo (UI delete, cenário A propagar pra Evolution, cenário B handler webhook + reconfig events) só será desarquivado se produto pedir. Hoje ninguém usa esse fluxo.

---

## Fila de produto (revenue/feature)

### 4. SA1 — Stripe + Assinatura + FIFO + Auto-recharge ⏳⏳⏳ (prioridade)

**Objetivo:** sistema completo de cobrança recorrente.

**Escopo (já scoped em prompts anteriores `claude-code-sa1-assinatura.md`):**
- Stripe integration (subscription).
- Courtesy credit R$10/mês (não-acumulativo, "taste").
- FIFO credit lots com expiração (60 dias).
- Auto-recharge opt-in com consentimento explícito (CDC art. 39).
- Trial 7d com R$3 AI credit, sem cartão.
- CRM continua quando AI pausa (sem AI ≠ sem CRM).
- 3.0× markup em créditos extras.

**Dependências:** Resend setup (envio email transacional, OTP). Pendente desde SU1 Phase 3.

**Ordem:** depois de SU8.4/8.5 fecharem infra. Receita é prioridade alta.

---

### 5. SG1 — Gemini Flash-Lite/Flash/Pro ⏳

**Objetivo:** terceiro provedor AI (atual: Anthropic + OpenAI).

**Escopo (já scoped `claude-code-sg1-gemini.md`):**
- Adicionar Gemini Flash-Lite, Flash, Pro como modelos.
- Cap 180k tokens em Pro (evitar tier-2 pricing).
- Tier mapping: Estagiária / Sec Júnior / Sec Sênior / Consultora.

**Dependências:** SUF10c-cleanup-debug-logs (não-bloqueante).

**Tech debt herdada:** `getTierForModel` em `src/features/ai-settings/lib/tierMapping.ts` é keyword-heuristic. Vai quebrar com nomes Gemini novos. Fix durável: adicionar `tier` column em `ai_models` table — entrar junto do SG1 ou logo depois.

---

### 6. SU7c — IA multimodal (parcialmente fechada) 🟡

**Status:**
- ✅ **SU7c-1** áudio recebido → transcrição Deepgram → IA processa
- ✅ **SU7c-1b** UI configuração + toggle de habilitação
- ⏳ **SU7c-2** imagem recebida → vision API → IA responde
- ⏳ **SU7c-3** AI envia imagem do catálogo (tool `send_image`) — depende catálogo de produtos

**Escopo SU7c-2 (próximo se priorizar):**
- Detector em `processIncomingMessage` quando `message_type='image'`
- Builder multimodal por provider (Anthropic, OpenAI, Gemini)
- Default Gemini Flash 2.5 (R$ 0,0001/imagem) — depende SG1 ou roda com Claude/GPT-4o
- Fallback gracioso se modelo configurado não suporta vision
- Custo: ~R$ 0,0001 a R$ 0,03 por imagem dependendo do modelo

**Escopo SU7c-3 (Opção A — MVP simples):**
- Tabela `products` com schema mínimo (name, image_url, sku, price, description)
- UI `/products` com lista + cadastro + edição
- Tool `send_image(query)` no AI runtime — busca tsvector
- Edge dedicada chamada pela tool

**Decisão de produto pendente:** SU7c-3 Opção A (MVP) vs Opção B (embeddings + categorias). Recomendação: A primeiro, evolui se cliente pedir.

---

## Fila de UI/UX (deferida)

### 7. UI/Editorial Noir ⏳

**Objetivo:** identidade visual completa (`prompt-lovable-v2.md`).

**Status:** deferido até sprints funcionais fecharem. Accent atual é teal em vez do burnt amber `#B8521B` planejado — desvio pequeno, não-bloqueante.

---

## Cleanups e tangentes (oportunístico)

### 8. Limpar logs de debug do SUF10c/SUF10d 🧹

Logs ainda no ar:
- `[suf10c-debug ...]` em `provider-send-message`
- `[webhook] {...}`, `[webhook-manual-send] {...}` verbose em `provider-webhook`

**Quando:** depois de 1-2 semanas confirmando que SUF10b/c/d estão estáveis. Não urgente.

---

### 9. SUF10c-broadcasts (residual) 🧹

**Objetivo:** revalidação de nome de grupo também em broadcasts (`send-broadcast-now`, `dispatch-scheduled-broadcasts`).

**Por que ficou de fora do SUF10c:** path `target_jids` usa `contactId: null` — exigiria SELECT extra por target.

**Quando:** baixa prioridade. Broadcasts em grupo é caso de uso menos frequente, e quando a mensagem chegar de volta via webhook (echo), o gate de SUF10b/d cobre.

---

### 10. SUF10e — Backfill retroativo de nomes de grupo 🧹

**Objetivo:** edge one-shot que itera todos os grupos e força `fetchAllGroups` pra reconciliar nomes históricos.

**Por que opcional:** com SUF10b/c/d, grupos reconciliam organicamente conforme recebem mensagens. Backfill só zeraria débito mais rápido.

**Quando:** se Pedro notar grupos antigos persistentemente errados que nunca recebem mensagem. Edge tipo `backfill-evolution-apikeys`.

---

### 11. Configurar SUPABASE_DB_PASSWORD env 🧹

**Objetivo:** evitar `supabase db push` falhar com auth error em migrations futuras.

**Como:**
```bash
echo 'export SUPABASE_DB_PASSWORD="<senha-do-projeto>"' >> ~/.zshrc
source ~/.zshrc
```

Senha em https://supabase.com/dashboard/project/qbclqjkvovfriuhshkpw/settings/database (Connection string → "DB Password").

**Quando:** próxima migration. Caso pontual resolve com SQL Editor manual + INSERT em `supabase_migrations.schema_migrations`.

---

### 12. Backfill nomes de grupo "Grupo XXXX" antigos 🧹

**Objetivo:** caso isolado encontrado: `Grupo 1525` (`120363427093191525@g.us`) restou no banco com placeholder porque nunca recebeu mensagem.

**Status:** com SUF10b/d ativos, vai reconciliar quando receber qualquer mensagem. Se não receber nunca, backfill SUF10e cobre.

**Quando:** SUF10e ou nunca, se ninguém usar o grupo.

---

### 13. Verificação de preços OpenAI quebrada 🧹

**Objetivo:** painel `/admin/ai-infra` → "Verificação de preços" mostra os 4 modelos GPT com ❌ "Modelo não encontrado na página". Apenas Anthropic está sendo scrapeado com sucesso.

**Status atual:**
- Claude Haiku 4.5 ✅ preço OK
- Claude Sonnet 4.6 ✅ preço OK
- Claude Opus 4.7 ✅ preço OK
- GPT-5.4 nano ❌ não encontrado
- GPT-5.4 mini ❌ não encontrado
- GPT-5.4 ❌ não encontrado
- GPT-5.5 Pro ❌ não encontrado

**Por que importa:** se algum tenant usa OpenAI e o preço do banco está desatualizado, você cobra errado (margem real diferente do que dashboard mostra). Hoje é mitigado porque os modelos OpenAI estão pouco usados (visível no dashboard `/admin/dashboard` — todas as chamadas recentes são Anthropic).

**Causas prováveis:**
- Layout da página de pricing OpenAI mudou desde quando o scraper foi escrito
- Selectors HTML quebrados
- Nomes dos modelos mudaram (GPT-5.4 nano vs gpt-4o-nano vs outro nome real)

**Escopo do fix:**
- Raio-x do scraper atual (provavelmente edge `scrape-openai-prices` ou similar)
- Atualizar selectors / regex / nome dos modelos
- Considerar: se OpenAI não tem página HTML estruturada e dificulta scraping, alternativa é hardcode na seed e atualização manual quando OpenAI mexer (modelos OpenAI mudam preço raramente, ~1-2x ao ano)

**Tamanho:** ~2-4h dependendo se scraping ainda funciona com selectors novos ou se vai ter que migrar pra estratégia diferente.

**Quando:** baixa urgência. Se SG1 entrar antes (Gemini), aproveita pra revisar todo o pipeline de scraping de preços.

---

### 14. Painel admin: Deepgram + futuras transcrições 🧹

**Objetivo:** após SU7c-1 entrar, dashboard `/admin/dashboard` (Tenant × modelo) e `/admin/ai-infra` (Verificação de preços) não cobrem Deepgram. Fica visível só na `tenant_ledger`, sem segregação.

**Decisão pendente:**
- Adicionar coluna/seção "Transcrição" separada nos painéis
- Ou unificar com modelos AI (mistura unidades, fica confuso)

**Recomendação:** seção separada, como SU7c-1 escopa modelo distinto em tabela `transcription_models`.

**Quando:** após SU7c-1 estabilizar e ter dados reais pra mostrar.

---

## Ordem recomendada de execução

1. **SU8.4** (delete em Evolution) — fecha bloco SU8 de migração de envio
2. **SU8.5** (cleanup env) — depois do SU8.4
3. **SU7b** (UI mídia) — destrava produto
4. **SA1** (Stripe) — receita, prioridade alta
5. **SG1** (Gemini) — terceiro provider
6. **SU7c** (multimodal) — depende SU7b
7. UI/Editorial Noir + cleanups oportunísticos

---

## Sinais que devem fazer parar e re-priorizar

- Cliente real reclamando de bug → vira prioridade
- Custo de Evolution/Supabase escalando inesperado → SU8.5/cleanup logs sobem
- Pedro decidir trial/launch antecipado → SA1 + SU7b sobem juntos
- AI errar muito ou ficar caro → SG1 sobe (Gemini tem custo menor)

---

## Pendências cross-sprint

- **Resend setup pendente** (Pedro precisa criar conta + gerar API key + decidir se renomeia projeto Lovable). Bloqueia SA3 (onboarding flow) e parte do SA1.
- **Configurar `SUPABASE_DB_PASSWORD`** (cleanup #11) — antes da próxima migration.
- **Hook de notificação sonora no Claude Code** — Pedro pediu setup, está em `~/.claude/settings.json` com `Stop` hook + `notify.sh` + `notify-cancel.sh`.
