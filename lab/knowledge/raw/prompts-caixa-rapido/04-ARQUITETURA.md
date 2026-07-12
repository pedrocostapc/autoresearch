# 04 — Arquitetura

Stack, modelo de dados, ordem de construcao. Tudo decidido antes de escrever 1 linha de codigo.

## Por que decidir antes

Voce vai usar Claude Code pra construir. Claude e bom mas sem direcao escolhe stack diferente em cada arquivo. Resultado: caos.

Esse prompt **resolve isso uma vez** e dali em diante voce so executa.

## Stack default — use, salvo razao tecnica forte

| Camada | Default | Por que |
|---|---|---|
| Frontend + Backend | Next.js 15 (App Router) + TypeScript | unifica fullstack; deploy facil; Claude conhece muito bem |
| Hospedagem | Vercel | gratis ate dar trafego; 0 setup |
| Banco | Supabase (Postgres) | gratis ate 500MB; ja vem com auth, storage, RLS |
| Auth | Supabase Auth | gratis ilimitado; email/senha + magic link + OAuth |
| Pagamento | Stripe | melhor doc do mundo; recorrencia BRL com PIX desde 2024 |
| Email | Resend | gratis 3k/mes; integracao trivial |
| IA (se precisar) | Claude API | melhor opcao, pago por uso |
| CSS | Tailwind v4 + shadcn/ui | velocidade absurda |
| Validacao | Zod | obrigatorio pra inputs |
| Forms | React Hook Form + Zod | padrao de mercado |
| Notificacao UI | sonner (toast) | shadcn padrao |
| Queue / cron | Vercel Cron Jobs | gratis; ate 100 invocacoes/dia free |

> Se voce ta tentado a trocar por algo "moderno" sem razao tecnica concreta, **NAO TROCA**. Esse stack e o que voce ve em 80% dos SaaS B2B caixa-rapido em 2026.

---

--- COMECO DO PROMPT ---

Voce e um arquiteto de software senior. Sua missao: definir a arquitetura mais simples possivel pra construir o MVP em ate 14 dias, sem reinventar nada.

# Contexto

Cole o conteudo de `mvp.md`:

<mvp>
{COLE AQUI}
</mvp>

# Stack default que eu prefiro

- Next.js 15 + TypeScript + Tailwind + shadcn/ui
- Vercel
- Supabase (Postgres + Auth + Storage)
- Stripe (recorrencia BRL com PIX)
- Resend (email)
- Vercel Cron Jobs (se precisar)
- Claude API (se IA fizer parte do produto)

# O que voce me entrega

## 1. Validacao da stack

Olhando o `mvp.md`, essa stack atende? **Justifique em 3-5 linhas.**

Se nao atende, **qual a alteracao MINIMA**? Nao troca por gosto. Troca so se houver razao concreta (ex: "preciso de WebSocket alta concorrencia, vale Pusher" ou "tenho dado geoespacial pesado, vale PostGIS no plano pago do Supabase").

## 2. Modelo de dados

Liste as tabelas necessarias com colunas. Inclua:

```
### users (auth via Supabase — voce so estende com profile)

```sql
-- Supabase ja tem auth.users; voce cria um profile linkado:
create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text unique not null,
  nome text,
  plan text not null default 'free' check (plan in ('free', 'paid', 'past_due', 'canceled')),
  stripe_customer_id text unique,
  stripe_subscription_id text,
  current_period_end timestamptz,
  created_at timestamptz default now()
);

-- RLS pra cada usuario so ver o proprio profile:
alter table public.profiles enable row level security;
create policy "users own profile" on public.profiles
  for all using (auth.uid() = id);
```

### {tabela_principal_do_dominio}
```sql
-- Adapte pra o caso. Sempre com user_id pra multi-tenant + RLS:
create table public.{tabela} (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade not null,
  -- campos do dominio
  ...
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

alter table public.{tabela} enable row level security;
create policy "users own {tabela}" on public.{tabela}
  for all using (auth.uid() = user_id);
```
```

Inclua o **SQL completo das tabelas com RLS** — vai economizar 1h depois.

## 3. Estrutura de pastas

```
{nome-projeto}/
├── app/
│   ├── (marketing)/        # landing, pricing, etc.
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── (auth)/             # signup, login, recuperar
│   │   ├── login/page.tsx
│   │   └── signup/page.tsx
│   ├── (app)/              # area logada — protegida
│   │   ├── layout.tsx
│   │   ├── page.tsx        # dashboard
│   │   ├── billing/page.tsx
│   │   └── {feature}/page.tsx
│   └── api/
│       ├── stripe/
│       │   ├── checkout/route.ts
│       │   └── webhook/route.ts
│       ├── cron/
│       │   └── {job}/route.ts
│       └── ...
├── components/
│   ├── ui/                 # shadcn (criados via CLI)
│   ├── marketing/
│   ├── app/
│   └── auth/
├── lib/
│   ├── supabase/
│   │   ├── client.ts       # client component
│   │   ├── server.ts       # server component
│   │   └── middleware.ts
│   ├── stripe/
│   │   ├── client.ts       # server-side
│   │   └── prices.ts
│   ├── auth/
│   │   └── checkPlan.ts
│   └── utils.ts
├── middleware.ts           # protege /app/*
├── .env.example
├── .env.local              (gitignored)
└── next.config.ts
```

## 4. Variaveis de ambiente (todas)

```env
# Supabase
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=    # nunca expor pro client

# Stripe
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=        # ok no client
STRIPE_WEBHOOK_SECRET=
NEXT_PUBLIC_STRIPE_PRICE_ID=   # id do preco recorrente que voce criou no painel

# Resend
RESEND_API_KEY=
RESEND_FROM_EMAIL=             # ex: "noreply@seudominio.com.br"

# Cron (Vercel)
CRON_SECRET=                   # gere um aleatorio pra autenticar requests do cron

# Claude (se aplicavel)
ANTHROPIC_API_KEY=

# App
NEXT_PUBLIC_APP_URL=           # ex: https://seuapp.com.br
```

## 5. Riscos tecnicos

3-5 coisas que costumam dar problema com essa stack neste tipo de projeto. Pra cada um, qual a precaucao:

1. **{ex: Webhook do Stripe nao chegando em producao}** — Verificar que `STRIPE_WEBHOOK_SECRET` e o de **producao** (cada ambiente tem o seu). Confirmar URL no painel.

2. **{ex: RLS bloqueando query legitima}** — Sempre testar com 2 usuarios diferentes. Use `service_role` SO em rotas API server-side.

3. **{ex: Cron nao executando}** — Vercel Cron requer `vercel.json` configurado + auth via header.

4. ...

## 6. Ordem de construcao (12 etapas)

```
1. Criar projeto Next.js + Tailwind + shadcn (1h)
   - npx create-next-app@latest
   - npx shadcn@latest init
   - Variaveis de ambiente em .env.example

2. Configurar Supabase: criar projeto + rodar SQL das tabelas (1h)
   - Cria projeto em supabase.com
   - SQL Editor: cola o SQL do passo 2
   - Copia URL + anon key + service_role key

3. Configurar lib/supabase com client.ts e server.ts (30min)
   - Padrao oficial (link na doc Supabase)

4. Auth — signup + login + logout + recuperar senha (3h)
   - Pages em /(auth)
   - Formularios com React Hook Form + Zod
   - Toast com sonner em sucesso/erro

5. Layout da area logada + middleware de protecao (1h)
   - middleware.ts redireciona pra /login se nao autenticado
   - Layout mostra nome + botao de logout

6. Feature core — passo central da promessa nuclear (4-6h)
   - CRUD basico das entidades principais
   - Server Actions ou API routes
   - Validacao com Zod

7. Bloqueio de feature pra plano free + paywall (1h)
   - lib/auth/checkPlan.ts
   - Componente <Paywall /> que mostra CTA pra assinar

8. Stripe checkout (2h)
   - Cria conta Stripe + produto + preco mensal
   - app/api/stripe/checkout/route.ts
   - Botao "Assinar" que cria session

9. Webhook do Stripe (2h)
   - app/api/stripe/webhook/route.ts
   - Trata: checkout.session.completed, subscription.updated, invoice.payment_failed
   - Atualiza profiles.plan
   - Testa com `stripe listen` local

10. Pagina /billing (1h)
    - Mostra plano atual
    - Botao "Gerenciar" → Customer Portal do Stripe

11. Email transacional (Resend) — boas-vindas + recibo (2h)
    - lib/email/templates/{welcome,receipt}.tsx (email components React)
    - Disparo no signup + apos pagamento

12. Landing publica + deploy Vercel + dominio (2h)
    - (vem do prompt 05)
    - Deploy + configurar dominio
    - Smoke test fim a fim
```

Total estimado: ~22-25h reais de codificacao. Cabivel em 14 dias.

## 7. Definicao de pronto

Frase em 1-2 linhas, especifica e mensuravel:

```
"O MVP esta pronto quando um usuario consegue:
1. Cadastrar
2. Pagar com cartao
3. Usar a feature core sem bug critico
4. Receber email de boas-vindas
5. Cancelar via Customer Portal
em ambiente de producao com dominio proprio."
```

Comece a montar.

--- FIM DO PROMPT ---

---

## Sinal verde pra ir pro `05-LANDING.md`

- [ ] `arquitetura.md` salvo
- [ ] SQL das tabelas pronto
- [ ] Lista de variaveis de ambiente listadas
- [ ] Voce sabe a ordem das 12 etapas
- [ ] Definicao de pronto e mensuravel

## Erros comuns

1. **Trocar stack porque "ouvi que X e melhor"** — manda no padrao
2. **Esquecer RLS no Supabase** — vazamento de dado entre usuarios, problema serio
3. **Service role exposta no client** — nuke da seguranca
4. **Variaveis de teste em producao (Stripe test_xxx)** — pagamento nunca acontece
5. **Cron sem auth** — qualquer um chama a rota e dispara seu fluxo

## Antes de seguir

```bash
git add arquitetura.md
git commit -m "arquitetura definida"
```

Vai pro `05-LANDING.md`.
