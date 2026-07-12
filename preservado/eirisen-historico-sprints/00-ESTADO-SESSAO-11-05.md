# Estado da Sessão — 11/05/2026

> Documento de continuidade. O que aconteceu, o que foi resolvido, qual o estado atual do sistema.

---

## Resumo executivo

Sessão extensa com múltiplos bugs descobertos em cascata + entregas de features. Saímos com sistema funcionando e várias melhorias arquiteturais.

**Total de PRs entregues hoje:** 6 (#229, #232, #233, #234, #235, #236, #237, #238, #239)
**Bugs críticos resolvidos:** 5
**Migrations rodadas manualmente:** 4

---

## 1. PRs MERGEADOS HOJE

### PR #229 — URLs legíveis pra relatórios
- Formato `/r/{slug}/insights/{periodo-iso}/{hex6}`
- Retrocompat preservada com UUIDs antigos
- Migration: `ALTER COLUMN public_share_token TYPE text`
- Edge `share-insight-toggle` deployada

### PR #232 — Botão "Assinar agora" PlanHero (trialing)
- Aparece só quando `status === "trialing"`
- Navega pra aba Faturamento com auto-open
- Posteriormente simplificado pelo PR #236

### PR #233 — Sidebar CRÉDITOS
- Seção nova no sidebar (saldo + recarregar one-click)
- Página `/creditos` deletada
- Clique no saldo → vai pra aba PLANO

### PR #234 — Caminho C refactor (single source of truth)
- 3 hooks (`useSubscription`, `useTrialStatus`, `usePlansAndLimits`) leem `subscriptions.status` em vez de `tenants.subscription_status` legacy
- TS types alinhados: `"trial"` → `"trialing"`, `"canceled"` → `"cancelled"`
- Edge `checkout-subscription-create` corrigida

### PR #235 — Fix query_products (catálogos com variações)
- Payload retorna `var_1/var_2/var_3`
- Limite default 50, max 200
- Hint quando truncated
- Master prompt instrui sobre `var_3` regional
- Aplicado também em `query_delivery_items` e `query_services`

### PR #236 — Refator Faturamento (planos sempre abertos)
- Cards de planos no topo da aba (sem accordion)
- Remove lógica `?open=plano` que ficou inerte
- gap-8 entre seções
- Botões "Assinar agora" simplificados

### PR #237 — Trigger DB novos tenants
- Default mudou de `iniciante_mensal` pra `negocio_mensal`
- 14 dias trial mantidos
- Branch invite preservado

### PR #238 — Botão "Resetar persona" Aba Avançado
- Visível quando `system_prompt` tem conteúdo
- Limpa via UPDATE `system_prompt = ''`
- Modal de confirmação
- Toast de sucesso

### PR #239 — Hotfix gate provider-webhook (URGENTE)
- Bug crítico: provider-webhook bloqueava tenants em `persona_mode='blocks'` com `system_prompt < 10 chars`
- Fix: pula gate quando `persona_mode === 'blocks'`
- IA voltou pra Euca Brasil imediatamente

---

## 2. BUGS DESCOBERTOS E RESOLVIDOS

### Bug 1: Subscription status duplicada (arquitetural)

**Sintoma:** Botão "Assinar agora" não aparecia no sidebar pra Vanderlei e outros tenants em trial.

**Diagnóstico:**
- `tenants.subscription_status` (enum `subscription_status_enum`) usado por 3 hooks
- `subscriptions.status` (enum `tenant_status`) usado pelo PlanHero
- 23 dos 24 tenants tinham `tenants.subscription_status = "none"` (webhook não populava)
- `subscriptions.status = "trialing"` mas hooks legacy liam o campo errado

**Solução:** PR #234 Caminho C — refactor 3 hooks pra usar subscriptions como source of truth.

### Bug 2: Stripe sync fantasma (Risen Midia)

**Sintoma:** Risen Midia tinha `subscriptions.status = active` mas `stripe_subscription_id = NULL`.

**Diagnóstico via Stripe API:**
- Customer `cus_URJUpNiRFBp71u` existia
- ZERO subscriptions reais no Stripe
- Pedro pagou pelo checkout mas pagamento não completou (provavelmente abandonou)
- Status "active" no DB veio de INSERT manual antigo (fantasma)

**Solução:**
```sql
UPDATE subscriptions 
SET status='trialing', stripe_subscription_id=NULL, plan_id='negocio_mensal',
    current_period_end = NOW() + INTERVAL '7 days'
WHERE tenant_id IN (...);
```

**Pendente:** Pedro precisa completar checkout real no Stripe quando quiser testar pagamento.

### Bug 3: IA Anthropic saldo zerado

**Sintoma:** Todas as 18 IAs pagantes pararam de responder simultaneamente.

**Diagnóstico:** Saldo da API Anthropic ficou em -US$ 0,01. Bloqueio do provider, não bug no Risen.

**Solução:** Pedro comprou créditos na console Anthropic. IA voltou em segundos.

**Lição:** Adicionar monitoramento de saldo Anthropic no admin (sprint futura).

### Bug 4: IA Euca Brasil inconsistente (alucinação sobre catálogo)

**Sintoma:** IA disse 4x "tem varão" e 4x "não tem" no mesmo chat de 10min.

**Diagnóstico:**
- Catálogo Euca tem 1458 itens em apenas 6 nomes únicos (Caibro, Esticador, Esteio, Mourão, Poste, Varão)
- Cada nome com ~243 variações em Var 1/2/3
- Tool `query_products` retornava 10 items truncados sem `var_1/var_2/var_3`
- IA via 10 objetos idênticos sem distinguir 4m de 5m

**Solução:** PR #235 — payload completo + hint + limite 50.

### Bug 5: IA Euca parou após reset de system_prompt (CRÍTICO)

**Sintoma:** Após resetar `system_prompt = ''` do Euca, IA parou.

**Diagnóstico em 3 iterações:**
1. **Primeira tentativa:** Suspeitamos webhook Evolution → falso
2. **Segunda tentativa:** Suspeitamos operator_takeover → falso (Pedro provou com timeline visual)
3. **Causa raiz:** Gate em `provider-webhook` (linha 766-774) bloqueava `system_prompt.length < 10` sem considerar `persona_mode='blocks'`

**Solução:** PR #239 — gate agora considera `persona_mode`:
```typescript
const isBlocksMode = cfg.persona_mode === "blocks";
if (!isBlocksMode && (!cfg.system_prompt || cfg.system_prompt.trim().length < 10)) return;
```

---

## 3. MIGRATIONS RODADAS MANUALMENTE (SQL Editor)

### Migration 1: Reset trials pra 7 dias + negocio_mensal
```sql
UPDATE public.subscriptions
SET status = 'trialing', stripe_subscription_id = NULL,
    plan_id = 'negocio_mensal',
    current_period_start = NOW(),
    current_period_end = NOW() + INTERVAL '7 days',
    updated_at = NOW()
WHERE status IN ('active', 'past_due', 'trialing') 
  AND stripe_subscription_id IS NULL;
```

### Migration 2: Sincronização tenants ↔ subscriptions
```sql
UPDATE public.tenants
SET plan = 'negocio_mensal', subscription_status = 'trial',
    subscription_current_period_end = NOW() + INTERVAL '7 days',
    updated_at = NOW()
WHERE id IN (
  SELECT t.id FROM tenants t 
  JOIN subscriptions s ON s.tenant_id = t.id 
  WHERE s.status = 'trialing'
);
```

### Migration 3: Trigger handle_new_user (PR #237)
Mudou default de `iniciante_mensal` pra `negocio_mensal` em:
- `tenants.plan` (DEFAULT + INSERT trigger)
- `subscriptions.plan_id` (INSERT trigger)

### Migration 4: Reset persona Euca
```sql
UPDATE tenant_ai_configs SET system_prompt = '' 
WHERE tenant_id = 'fe6d2bd3-8114-4661-a57f-ba5386c3c7de';

UPDATE tenant_ai_configs SET manual_archetype_prompt = NULL 
WHERE tenant_id = 'fe6d2bd3-8114-4661-a57f-ba5386c3c7de';
```

---

## 4. ESTADO FINAL DO SISTEMA

### Funcionando
- 18 tenants em trial com plan_id=negocio_mensal, 7 dias restantes
- IA respondendo em todos os tenants (saldo Anthropic OK)
- Sidebar com seção CRÉDITOS funcionando
- Botão "Assinar agora" aparece pra tenants em trialing
- URLs legíveis pra relatórios
- Tool `query_products` retorna estruturado pra catálogos com variações
- Aba Faturamento com cards sempre abertos
- Botão "Resetar persona" na aba Avançado

### Validado em produção
- Euca Brasil: IA responde coerentemente sobre catálogo (pergunta UF, lista variações)
- Vanderlei: sidebar mostra botão Assinar agora
- Hospital Teste: status sincronizado

### Configurações importantes
- Novos tenants entram com `negocio_mensal` + 14 dias trial
- Threshold de saldo baixo: R$ 20
- operator_takeover_timeout: 2 horas (default)

---

## 5. DECISÕES TÉCNICAS CONSOLIDADAS

| Decisão | Justificativa |
|---|---|
| `subscriptions.status` = source of truth | Refactor abandonou coluna duplicada em tenants |
| Trial sempre cria com Negócio (R$99) | UX premium: cliente experimenta o teto |
| Downgrade requer remoção de recursos | Sprint futura, conceito aprovado |
| Upgrade sempre livre | UX simples |
| `tenants.subscription_status` deprecated | Não fazer DROP COLUMN agora, deixa cemitério |
| Stripe key rotation adiada | Pedro decidiu manter por enquanto |
| Caixa Products NÃO inline | Apenas via tool query_products |
| Compiler injeta caixas pequenas inline | Establishment, Hours, Pagamento, etc |

---

**Fim do documento.**
