# 07 — Pagamento

Sem cobrar, nao tem caixa rapido. Esse passo separa SaaS de experimento.

## Decisao previa: Stripe ou Mercado Pago

| Criterio | Stripe | Mercado Pago |
|---|---|---|
| Recorrencia BRL | desde 2024, excelente | OK, menos polido |
| PIX | si, usa Pix Brasil | nativo |
| Cartao internacional | top | dificil |
| Cartao recorrencia | top, com 3DS | OK |
| Documentacao | melhor do mercado | razoavel |
| Customer Portal | excelente (clientes gerenciam sozinhos) | inferior |
| Taxa transacao | ~3.99% + R$ 0,39 | ~3.79% + variavel |
| Webhook | confiavel | confiavel |

**Regra de bolso:**

- Ticket B2B (R$ 49-499/mes), 100% Brasil, quer PIX → **Mercado Pago** OU **Stripe** (Stripe ja tem Pix e Customer Portal melhor — ganha em ~70% dos casos)
- Cliente internacional ocasional → **Stripe**
- Voce ja conhece Stripe → **Stripe**

Esse pacote **vai com Stripe** como padrao. Se voce escolheu MP, os conceitos sao iguais — adapte.

## O que voce sai com esse prompt

- Checkout funcionando
- Webhook tratando todos eventos relevantes
- Pagina /billing com Customer Portal
- Sistema atualizando o `plan` do usuario corretamente
- Email de recibo via Resend

---

## Pre-requisitos no Stripe

Antes de codificar:

1. **Conta Stripe** ativada (https://dashboard.stripe.com/register)
   - Ativacao Brasil: precisa de CNPJ + dados bancarios
   - Pode levar 1-3 dias
2. **Modo Test** ja vem ativo. Use ate ter tudo funcionando
3. **Criar Produto + Preco**:
   - Dashboard → Products → Add product
   - Nome: `{Nome do seu plano}` (ex: "PontoFiscal Pro")
   - Preco: Recurring, R$ X/mes, BRL
   - Anota o `price_id` (parecido com `price_1Q...`) — vai em `STRIPE_PRICE_ID`
4. **Habilitar PIX** (opcional mas recomendado):
   - Dashboard → Settings → Payment methods → Pix → Activate
5. **Customer Portal**:
   - Dashboard → Settings → Billing → Customer portal → Activate
   - Configurar: o que cliente pode fazer (cancelar, atualizar cartao, atualizar email)
6. **Webhook endpoint**:
   - Dashboard → Developers → Webhooks → Add endpoint
   - URL: `https://{seu-dominio}/api/stripe/webhook`
   - Events: marca `checkout.session.completed`, `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_failed`, `invoice.payment_succeeded`
   - Anota `STRIPE_WEBHOOK_SECRET` (parecido com `whsec_...`)

---

--- COMECO DO PROMPT ---

Voce e um senior engineer especializado em integracao Stripe. Sua missao: implementar cobranca recorrente no projeto: checkout, webhook, atualizacao de plano, customer portal, e email transacional de recibo.

# Contexto

<arquitetura>
{COLE arquitetura.md}
</arquitetura>

<mvp>
{COLE a parte do mvp.md sobre cobranca}
</mvp>

# Decisoes ja tomadas

- Vou usar **Stripe**
- Plano: **{nome}** — R$ **{X}**/mes
- Trial: **{0 ou 7 dias}**
- Moeda: **BRL**
- Meios de pagamento: **cartao** + **PIX** (se ativado no painel)
- Ja criei `STRIPE_PRICE_ID` no painel: `{price_id}`

# Tarefa

## 1. Checkout

`app/api/stripe/checkout/route.ts`:

```typescript
import { NextResponse } from 'next/server'
import { stripe } from '@/lib/stripe/client'
import { createClient } from '@/lib/supabase/server'

export async function POST() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  
  if (!user) {
    return NextResponse.json({ error: 'unauthorized' }, { status: 401 })
  }

  // Busca ou cria customer no Stripe
  const { data: profile } = await supabase
    .from('profiles')
    .select('stripe_customer_id, email')
    .eq('id', user.id)
    .single()

  let customerId = profile?.stripe_customer_id

  if (!customerId) {
    const customer = await stripe.customers.create({
      email: profile?.email ?? user.email!,
      metadata: { supabase_user_id: user.id }
    })
    customerId = customer.id

    await supabase
      .from('profiles')
      .update({ stripe_customer_id: customerId })
      .eq('id', user.id)
  }

  // Cria sessao de checkout
  const session = await stripe.checkout.sessions.create({
    mode: 'subscription',
    customer: customerId,
    line_items: [{
      price: process.env.NEXT_PUBLIC_STRIPE_PRICE_ID!,
      quantity: 1,
    }],
    payment_method_types: ['card', 'pix'],
    success_url: `${process.env.NEXT_PUBLIC_APP_URL}/app?welcome=true`,
    cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/billing?canceled=true`,
    locale: 'pt-BR',
    // Trial opcional:
    // subscription_data: { trial_period_days: 7 },
    allow_promotion_codes: true,
  })

  return NextResponse.json({ url: session.url })
}
```

`components/CheckoutButton.tsx`:

```tsx
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { toast } from 'sonner'

export function CheckoutButton({ children }: { children: React.ReactNode }) {
  const [loading, setLoading] = useState(false)

  async function handleCheckout() {
    setLoading(true)
    try {
      const response = await fetch('/api/stripe/checkout', { method: 'POST' })
      const data = await response.json()
      
      if (data.url) {
        window.location.href = data.url
      } else {
        toast.error('Erro ao iniciar checkout')
      }
    } catch (e) {
      toast.error('Erro de conexao')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Button onClick={handleCheckout} disabled={loading} size="lg">
      {loading ? 'Carregando...' : children}
    </Button>
  )
}
```

## 2. Webhook

`app/api/stripe/webhook/route.ts`:

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { stripe } from '@/lib/stripe/client'
import { createClient } from '@supabase/supabase-js'
import { Resend } from 'resend'
import type Stripe from 'stripe'

const supabaseAdmin = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
)
const resend = new Resend(process.env.RESEND_API_KEY!)

export async function POST(req: NextRequest) {
  const body = await req.text()
  const signature = req.headers.get('stripe-signature')!

  let event: Stripe.Event
  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    )
  } catch (err) {
    console.error('Webhook signature verification failed:', err)
    return NextResponse.json({ error: 'invalid signature' }, { status: 400 })
  }

  try {
    switch (event.type) {
      case 'checkout.session.completed': {
        const session = event.data.object as Stripe.Checkout.Session
        const customerId = session.customer as string
        const subscriptionId = session.subscription as string

        // Busca subscription pra ter detalhes
        const subscription = await stripe.subscriptions.retrieve(subscriptionId)
        
        // Atualiza profile
        await supabaseAdmin
          .from('profiles')
          .update({
            plan: 'paid',
            stripe_subscription_id: subscriptionId,
            current_period_end: new Date(subscription.current_period_end * 1000).toISOString(),
          })
          .eq('stripe_customer_id', customerId)

        // Email de boas-vindas/recibo
        const { data: profile } = await supabaseAdmin
          .from('profiles')
          .select('email, nome')
          .eq('stripe_customer_id', customerId)
          .single()

        if (profile?.email) {
          await resend.emails.send({
            from: process.env.RESEND_FROM_EMAIL!,
            to: profile.email,
            subject: 'Bem-vindo ao {NOME PRODUTO}!',
            html: `
              <h1>Oi ${profile.nome ?? ''}!</h1>
              <p>Seu pagamento foi confirmado. Tudo liberado pra voce usar.</p>
              <p><a href="${process.env.NEXT_PUBLIC_APP_URL}/app">Acessar o painel</a></p>
            `,
          })
        }
        break
      }

      case 'customer.subscription.updated': {
        const sub = event.data.object as Stripe.Subscription
        const customerId = sub.customer as string

        const planStatus = mapStripeStatusToPlan(sub.status)

        await supabaseAdmin
          .from('profiles')
          .update({
            plan: planStatus,
            current_period_end: new Date(sub.current_period_end * 1000).toISOString(),
          })
          .eq('stripe_customer_id', customerId)
        break
      }

      case 'customer.subscription.deleted': {
        const sub = event.data.object as Stripe.Subscription
        const customerId = sub.customer as string

        await supabaseAdmin
          .from('profiles')
          .update({
            plan: 'canceled',
            stripe_subscription_id: null,
          })
          .eq('stripe_customer_id', customerId)
        break
      }

      case 'invoice.payment_failed': {
        const invoice = event.data.object as Stripe.Invoice
        const customerId = invoice.customer as string

        await supabaseAdmin
          .from('profiles')
          .update({ plan: 'past_due' })
          .eq('stripe_customer_id', customerId)

        // Email avisando
        const { data: profile } = await supabaseAdmin
          .from('profiles')
          .select('email, nome')
          .eq('stripe_customer_id', customerId)
          .single()

        if (profile?.email) {
          await resend.emails.send({
            from: process.env.RESEND_FROM_EMAIL!,
            to: profile.email,
            subject: 'Falha no pagamento — atualiza seu cartao',
            html: `
              <h1>Oi ${profile.nome ?? ''}</h1>
              <p>Tivemos problema pra processar seu pagamento. Atualiza o cartao em:</p>
              <p><a href="${process.env.NEXT_PUBLIC_APP_URL}/billing">Atualizar cartao</a></p>
            `,
          })
        }
        break
      }

      default:
        // Ignora eventos que nao tratamos
        break
    }
  } catch (error) {
    console.error('Webhook handler error:', error)
    return NextResponse.json({ error: 'handler error' }, { status: 500 })
  }

  return NextResponse.json({ received: true })
}

function mapStripeStatusToPlan(status: Stripe.Subscription.Status) {
  switch (status) {
    case 'active':
    case 'trialing':
      return 'paid'
    case 'past_due':
    case 'unpaid':
      return 'past_due'
    case 'canceled':
    case 'incomplete_expired':
      return 'canceled'
    default:
      return 'free'
  }
}
```

## 3. Pagina /billing

`app/(app)/billing/page.tsx`:

```tsx
import { createClient } from '@/lib/supabase/server'
import { stripe } from '@/lib/stripe/client'
import { redirect } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { CheckoutButton } from '@/components/CheckoutButton'
import { Button } from '@/components/ui/button'

export default async function BillingPage() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/login')

  const { data: profile } = await supabase
    .from('profiles')
    .select('plan, stripe_customer_id, current_period_end')
    .eq('id', user.id)
    .single()

  const isPaid = profile?.plan === 'paid'

  // Cria URL do Customer Portal sob demanda
  async function gerarPortalUrl() {
    'use server'
    if (!profile?.stripe_customer_id) return null
    const portal = await stripe.billingPortal.sessions.create({
      customer: profile.stripe_customer_id,
      return_url: `${process.env.NEXT_PUBLIC_APP_URL}/billing`,
    })
    return portal.url
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Sua assinatura</CardTitle>
        <CardDescription>
          Plano atual: <strong>{profile?.plan ?? 'free'}</strong>
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isPaid ? (
          <form action={async () => {
            'use server'
            const url = await gerarPortalUrl()
            if (url) redirect(url)
          }}>
            <Button type="submit">Gerenciar assinatura</Button>
          </form>
        ) : (
          <CheckoutButton>Assinar por R$ {/* PRECO */}/mes</CheckoutButton>
        )}
      </CardContent>
    </Card>
  )
}
```

## 4. Como testar localmente

### Setup local com `stripe listen`

1. Instala Stripe CLI: https://stripe.com/docs/stripe-cli
2. Loga: `stripe login`
3. Roda local: `stripe listen --forward-to localhost:3000/api/stripe/webhook`
4. Ela mostra um `STRIPE_WEBHOOK_SECRET` temporario — **usa esse na .env.local** durante teste
5. Em outro terminal: `npm run dev`

### Cartoes de teste (Stripe)

- Pagamento que sucede: `4242 4242 4242 4242`, qualquer CVC, qualquer data futura
- Pagamento que recusa: `4000 0000 0000 0002`
- Pagamento que requer 3DS: `4000 0000 0000 3220`

### Roteiro de teste

1. Cadastra usuario novo no app
2. Vai em /billing
3. Clica "Assinar"
4. No checkout do Stripe, usa cartao `4242 4242 4242 4242`
5. Volta pro /app — deve estar logado e plan = 'paid'
6. Confere no banco: `select * from profiles where ...` — `plan = 'paid'`
7. Confere no painel Stripe: subscription ativa
8. No /billing, clica "Gerenciar" → abre Customer Portal
9. Cancela
10. Volta pro app, plan deve ter virado 'canceled' (depois do webhook)

# Antes de codificar

Mostre o plano de arquivos. Espera minha aprovacao. Codifica.

No final me liste exatamente:

1. O que tenho que fazer no painel do Stripe (passos numerados)
2. Como rodar `stripe listen` local
3. Roteiro de teste fim a fim com cartao 4242
4. Como configurar webhook em producao quando for deploy

--- FIM DO PROMPT ---

---

## Checklist antes de subir pra producao

- [ ] Cartao de teste passa, `plan = 'paid'`
- [ ] Cancelamento via Customer Portal: `plan = 'canceled'`
- [ ] Cartao recusado (`4000 0000 0000 0002`): `plan = 'past_due'`
- [ ] Webhook configurado em producao com `STRIPE_WEBHOOK_SECRET` da producao
- [ ] PIX testado em real com R$ 1 (vale a pena, da pra estornar depois)
- [ ] Email de boas-vindas chega
- [ ] Email de falha de pagamento chega

## Erro mais comum em pagamento

**99% dos bugs sao webhook nao chegando.** Se checkout funciona mas `plan` nao muda, e o webhook.

Verifique:

1. URL do webhook em producao no painel Stripe
2. `STRIPE_WEBHOOK_SECRET` em producao bate com o gerado no painel
3. Logs do Vercel: requests do `/api/stripe/webhook` estao chegando? Status 200?
4. O codigo nao esta lendo `request.body` antes da verificacao de assinatura (precisa ser `await req.text()`)

## Erros de seguranca a evitar

| Erro | Risco |
|---|---|
| Service role key no client | Vazamento total — nuke |
| Webhook sem verificar assinatura | Qualquer um manda evento fake e libera plano |
| Plan vindo do client (cliente diz "sou paid") | Trivial burlar |
| RLS desligada nas tabelas | Cliente A le dado do cliente B |

## Antes de seguir

```bash
git add .
git commit -m "pagamento Stripe + webhook funcionando"
```

**Para teste real:** Antes de lancar, peca pra um amigo cadastrar e pagar com PIX de R$ 1 ou cartao real.

Vai pro `08-LANCAMENTO.md`.
