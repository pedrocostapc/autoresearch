# Raio-X — Estado atual do sistema de cobrança e Stripe

> Não é uma sprint. É um diagnóstico.
> Pedro precisa saber **exatamente** o que existe hoje no sistema de
> cobrança, planos, Stripe, FIFO, courtesy, trial, antes de escopar
> qualquer SA1. A premissa "Stripe não funciona" pode estar errada.

---

## O que precisa investigar

Reportar com caminhos de arquivo, linhas, schema de tabela, status (funciona/parcial/quebrado/inexistente). **Não codar nada.** Só ler, listar, e relatar.

### 1. Schema de banco — tabelas relacionadas a billing

Listar e descrever:
- `tenants.credits_cents` — existe? Como é atualizado?
- `tenant_ledger` — existe? Schema completo. Quem escreve nele? Cron diário ou em tempo real?
- `tenant_credit_lots` — existe? Schema. Como FIFO é consumido?
- `credit_purchases` — existe? Schema. Liga com Stripe?
- `tenant_subscriptions` (ou nome similar) — existe? Schema?
- `system_config` — quais campos? `markup_multiplier`, `usd_to_brl_ptax`, `usd_to_brl_surcharge_pct` confirmados, mais algum?
- Outras tabelas relacionadas a planos, courtesy, trial, recharges?

Para cada tabela, listar colunas relevantes e RLS.

### 2. RPCs de cobrança

Listar todas RPCs em `supabase/migrations/` que tocam billing:
- `debit_credits`
- `apply_credit_grant`
- `has_sufficient_credits`
- `try_acquire_auto_recharge_slot`
- `calculate_transcription_cost` (SU7c-1)
- `check_and_reserve_system_budget`
- Outras?

Para cada RPC: assinatura, o que faz, quem chama (qual edge ou trigger).

### 3. Stripe — o que está integrado

Procurar em `supabase/functions/`:
- Edge `stripe-webhook` — existe? O que processa? Quais eventos?
- Edge `stripe-checkout` ou similar — cria checkout session? Pra qual produto/plano?
- Edge `stripe-customer-portal` — permite cliente gerenciar assinatura?
- Outras edges com import de Stripe?

Procurar em `src/`:
- Tela de billing/subscription? Caminho?
- Botão "Upgrade plan" ou "Adicionar crédito"?
- Componente de checkout?

Verificar secrets do Supabase: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_ID_*` configurados?

### 4. Plans / pricing — definição em algum lugar?

Procurar:
- Tabela `plans` ou `subscription_plans`?
- Constantes hardcoded em `_shared/plans.ts` ou similar?
- Configurado em `system_config`?
- Os 3 planos do memory (Iniciante R$19,90 / Crescimento R$49,90 / Negócio R$99,90) existem em algum lugar como dados?
- Anuais (com 50% off) existem?
- Add-ons (extra seats, extra instances, storage tiers) existem?

### 5. Courtesy credit — como funciona hoje?

- Tabela ou campo que rastreia courtesy?
- Cron mensal que adiciona courtesy?
- Lógica de "não-acumulativa" (substitui em vez de somar)?
- Valores atuais (R$30/80/150 por plano)? Onde estão definidos?

### 6. Trial — como funciona hoje?

- Tabela ou flag `trial_started_at` em `tenants`?
- Cron que expira trial após 30 dias ou consome 1GB?
- R$3 AI credit é aplicado automaticamente em onboarding?
- Trial ativa cobrança mas com saldo cortesia, ou bloqueia totalmente?

### 7. Auto-recharge — opt-in?

- Coluna `auto_recharge_enabled` em `tenants`?
- Edge que dispara recharge quando saldo < threshold?
- Threshold configurável?
- Stripe charge automático funcionando?
- Consentimento explícito (CDC art. 39) registrado em algum lugar?

### 8. UI — telas existentes

Listar telas em `/src/features/`:
- `/billing` ou equivalente — existe? Mostra saldo, histórico, recharge?
- Onboarding com cadastro de cartão?
- Página de planos com upgrade?
- Página admin pra ver receita/MRR?

### 9. Cobrança real — está debitando hoje?

Verificar via SQL:
```sql
-- Volume de débitos últimos 30 dias
SELECT COUNT(*), SUM(amount_cents)
FROM tenant_ledger
WHERE entry_type = 'debit'
  AND created_at > NOW() - INTERVAL '30 days';

-- Tenants com saldo positivo
SELECT COUNT(*) FROM tenants WHERE credits_cents > 0;

-- Recharges (Stripe ou manual?) últimos 30 dias
SELECT COUNT(*), SUM(amount_cents)
FROM credit_purchases
WHERE created_at > NOW() - INTERVAL '30 days';
```

Se `credit_purchases` tem rows com Stripe IDs → Stripe já está cobrando alguém.
Se só tem rows com `entry_type='manual_grant'` ou similar → cobrança Stripe não rodou ainda em produção.

### 10. Gaps reais vs implementação

Após levantar tudo, fazer uma matriz:

| Componente | Status | Onde |
|---|---|---|
| FIFO de créditos | ? | tabela X, RPC Y |
| Stripe checkout | ? | edge Z ou inexistente |
| Webhook Stripe | ? | edge W ou inexistente |
| Cobrança recorrente (assinatura) | ? | ? |
| Auto-recharge | ? | ? |
| Courtesy credit | ? | ? |
| Trial | ? | ? |
| UI de billing | ? | ? |
| ... | | |

Marcar cada um como:
- ✅ funcional em produção
- 🟡 implementado mas não testado / não em uso
- 🔴 schema/edge existe mas falta integração
- ❌ inexistente

---

## Output esperado

Um relatório estruturado pra Pedro entender:

1. **O que já está funcionando** (não precisa SA1 pra isso)
2. **O que está implementado mas não está em uso** (precisa só ligar/configurar)
3. **O que falta de fato** (precisa codar)

Esse relatório vai virar o input pra escopar **SA1 corretamente** — só o que falta, sem reinventar o que existe.

---

## Não codar

Esta tarefa é **pura investigação**. Nenhum arquivo modificado. Nenhuma migration nova. Nenhum commit. Apenas:
- Leitura de arquivos
- Queries no banco (via SQL Editor)
- Listagem de schemas, RPCs, edges
- Relatório textual com caminhos de arquivo + linhas

Pedro vai ler o relatório e decidir o escopo real do SA1 baseado no estado real do sistema.
