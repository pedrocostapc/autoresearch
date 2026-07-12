# 06 — Build do MVP

Construir o produto com Claude Code, etapa por etapa, com codigo starter pronto.

## Antes de comecar

- Ja tem `arquitetura.md` (do prompt 04)?
- Ja tem `mvp.md` (do prompt 03)?
- Ja tem landing (do prompt 05)?
- Tem 14 dias mapeados pra construir?

Se sim, vai.

## Estrutura desta etapa

Esse passo e maior que os outros. Voce nao roda 1 prompt — voce roda **3 prompts em sequencia**, cada um pra uma fase. Mais o `07-PAGAMENTO.md` que continua o build.

```
PROMPT A — Setup (1-2h)
  ↓
PROMPT B — Auth + feature core (8-12h espalhadas)
  ↓
PROMPT C — Pagamento (em 07-PAGAMENTO.md)
  ↓
Smoke test fim a fim
```

---

## PROMPT A — Setup do projeto

Roda no Claude Code numa pasta vazia.

--- COMECO PROMPT A ---

Voce e um senior fullstack engineer trabalhando comigo no Claude Code. Vamos iniciar o projeto. Sua missao agora: **setup limpo, sem firula**.

# Contexto da arquitetura

Cole o conteudo de `arquitetura.md`:

<arquitetura>
{COLE AQUI}
</arquitetura>

# Tarefa

1. Crie a estrutura inicial do Next.js 15 com TypeScript, Tailwind, shadcn/ui
   - `npx create-next-app@latest`: TypeScript Yes, Tailwind Yes, App Router Yes
   - `npx shadcn@latest init`: tema = neutral, CSS variables = Yes
   - Instalar pacotes essenciais: `react-hook-form`, `zod`, `@hookform/resolvers/zod`, `@supabase/supabase-js`, `@supabase/ssr`, `stripe`, `resend`, `sonner`, `@vercel/analytics`

2. Configure ESLint + Prettier basico (defaults sensiveis)

3. Crie `.env.example` com TODAS as variaveis listadas em `arquitetura.md`

4. Crie a estrutura de `lib/`:
   - `lib/supabase/client.ts` (browser)
   - `lib/supabase/server.ts` (server components / server actions)
   - `lib/supabase/middleware.ts` (atualizar session)
   - `lib/stripe/client.ts` (server-side)
   - `lib/stripe/prices.ts`
   - `lib/auth/checkPlan.ts` (skeleton)
   - `lib/utils.ts` (cn function ja vem do shadcn)

5. Crie `middleware.ts` na raiz (atualiza session do Supabase em cada request)

6. Crie pastas vazias com placeholders:
   - `app/(marketing)/page.tsx` (placeholder simples)
   - `app/(auth)/login/page.tsx` (placeholder)
   - `app/(auth)/signup/page.tsx` (placeholder)
   - `app/(app)/layout.tsx` (placeholder)
   - `app/(app)/page.tsx` (placeholder)
   - `app/api/stripe/checkout/route.ts` (placeholder)
   - `app/api/stripe/webhook/route.ts` (placeholder)

7. Crie `README.md` com:
   - Pre-requisitos
   - Como rodar local
   - Como configurar Supabase (com SQL pronto pra executar)
   - Como configurar Stripe (com lista de passos)
   - Como configurar Resend
   - Como rodar testes locais com Stripe (`stripe listen`)

# Codigo de referencia que voce deve usar

## `lib/supabase/server.ts`
```ts
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function createClient() {
  const cookieStore = await cookies()
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() { return cookieStore.getAll() },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            )
          } catch {
            // Server Component — ignore
          }
        },
      },
    }
  )
}
```

## `lib/supabase/client.ts`
```ts
import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

## `middleware.ts`
```ts
import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({ request })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() { return request.cookies.getAll() },
        setAll(cookies) {
          cookies.forEach(({ name, value, options }) => {
            request.cookies.set(name, value)
            response.cookies.set(name, value, options)
          })
        },
      },
    }
  )

  const { data: { user } } = await supabase.auth.getUser()

  // Protege /app/*
  if (!user && request.nextUrl.pathname.startsWith('/app')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // Logado nao volta pra login/signup
  if (user && (request.nextUrl.pathname === '/login' || request.nextUrl.pathname === '/signup')) {
    return NextResponse.redirect(new URL('/app', request.url))
  }

  return response
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.png$).*)'],
}
```

## `lib/stripe/client.ts`
```ts
import Stripe from 'stripe'

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2025-01-27.acacia',
})
```

# Antes de codificar

Mostre o plano de arquivos que vai criar/editar (lista resumida). Depois que eu aprovar, codifique.

No final, me diga em passos numerados:

1. O que eu preciso fazer manualmente (criar conta Supabase, Stripe, Resend, dominio)
2. Como rodar o `npm run dev` e ver o placeholder
3. Quais SQLs rodar no Supabase (cole inteiros)
4. Como criar produto/preco no Stripe (passo a passo)

--- FIM PROMPT A ---

---

## PROMPT B — Auth + feature core

Roda **depois** que setup ta funcionando local + Supabase configurado + tabelas criadas.

--- COMECO PROMPT B ---

Continuando o projeto. Vamos implementar agora:

1. Auth completo (signup, login, logout, recuperar senha)
2. Layout da area logada
3. A feature core do produto
4. Bloqueio de feature pra usuario sem assinatura paga (paywall)

# Contexto

<arquitetura>
{COLE arquitetura.md}
</arquitetura>

<mvp>
{COLE mvp.md}
</mvp>

# Tarefa detalhada

## 1. Auth (~3h)

### Decisao: email + senha (mais comum em B2B brasileiro)

- `app/(auth)/signup/page.tsx`:
  - Form com email + senha + confirmar senha + nome
  - Validacao: senha min 8 chars + uppercase + numero
  - Apos signup, dispara email de boas-vindas via Resend
  - Cria entrada em `profiles` (trigger SQL ja faz, mas confirma)
  - Redireciona pra /app

- `app/(auth)/login/page.tsx`:
  - Form com email + senha
  - Link "Esqueci a senha"
  - Redireciona pra /app

- `app/(auth)/recuperar/page.tsx`:
  - Form com email
  - Dispara email Supabase

- `app/(auth)/recuperar/confirmar/page.tsx`:
  - Form com nova senha (apos clicar link do email)

- `app/(app)/logout/route.ts` (POST):
  - Server action que faz signOut
  - Redireciona pra /

Use **Server Actions** sempre que possivel pra forms de auth.

## 2. Layout da area logada

`app/(app)/layout.tsx`:

- Header com logo + nome usuario + dropdown (Configuracoes / Billing / Logout)
- Sidebar minima (se MVP precisa) ou tabs
- Container principal

## 3. Feature core

Implemente o fluxo descrito em `mvp.md` passo a passo:

- Crie rotas necessarias em `app/(app)/{feature}/`
- Server Actions OU API routes pra cada operacao
- Componentes de UI usando shadcn (Form, Input, Button, Table, Dialog, Sheet)
- Validacao com Zod em **toda** entrada de dados
- Tratamento de erro com toast (sonner)
- Loading states (Suspense + skeleton)

## 4. Paywall

- `lib/auth/checkPlan.ts`:
  ```ts
  import { createClient } from '@/lib/supabase/server'
  
  export async function getUserPlan(): Promise<'free' | 'paid' | 'past_due' | 'canceled'> {
    const supabase = await createClient()
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) return 'free'
    
    const { data: profile } = await supabase
      .from('profiles')
      .select('plan')
      .eq('id', user.id)
      .single()
    
    return profile?.plan ?? 'free'
  }
  
  export async function requirePaid() {
    const plan = await getUserPlan()
    return plan === 'paid'
  }
  ```

- Componente `<Paywall />` que aparece quando `plan !== 'paid'`:
  ```tsx
  export function Paywall({ feature }: { feature: string }) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Esse recurso e exclusivo do plano pago</CardTitle>
          <CardDescription>
            Pra usar {feature}, voce precisa assinar. R$ {PRECO}/mes.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button asChild>
            <Link href="/billing">Assinar agora</Link>
          </Button>
        </CardContent>
      </Card>
    )
  }
  ```

- Use no inicio das paginas/server actions:
  ```tsx
  export default async function FeaturePage() {
    const isPaid = await requirePaid()
    if (!isPaid) return <Paywall feature="cadastro de clientes" />
    
    return <FeatureContent />
  }
  ```

# Antes de codificar

1. Mostre o plano de arquivos que vai criar/editar (lista)
2. Indique a ordem de implementacao
3. Codifique a primeira coisa, espera eu testar local, depois segue

# Sinal verde pra prompt C

- [ ] Cadastro funciona, recebe email de boas-vindas
- [ ] Login redireciona pra /app
- [ ] Logout funciona
- [ ] Recuperar senha funciona
- [ ] Layout area logada renderiza
- [ ] Feature core: crud basico funciona
- [ ] Paywall aparece pra usuario free e bloqueia feature

--- FIM PROMPT B ---

---

## Como nao se perder durante o build

### Regras de ouro

1. **`git commit` a cada coisa que funciona** — mesmo coisa pequena. Cria pontos de retorno.
2. **Roda local depois de cada feature** — nao codifica 3 features e testa tudo junto
3. **Quando o Claude propor mudanca grande, peca pra dividir** — "Faca em etapas, espera minha confirmacao entre elas"
4. **Use `git diff` antes de aceitar** — especialmente em `package.json`, `middleware.ts`, configs
5. **Se travou em algo, pergunta pro Claude antes de gastar 1h sozinho** — economiza 80% do tempo

### Ritmo recomendado (modo realista, 2h/dia)

```
Dia 1 (sabado): PROMPT A — setup, configurar Supabase
Dia 2 (domingo): SQL das tabelas, configurar Stripe, configurar Resend
Dia 3 (segunda): PROMPT B — comeca por Auth (signup + login)
Dia 4 (terca): Termina auth (logout + recuperar)
Dia 5 (quarta): Layout area logada + paywall basico
Dia 6 (quinta): Feature core parte 1 (CRUD basico)
Dia 7 (sexta): Pausa — usa
Dia 8 (sabado): Feature core parte 2 (segunda funcao)
Dia 9 (domingo): Feature core parte 3 (terceira funcao)
Dia 10 (segunda): Refinos UI + testes
Dia 11 (terca): PROMPT C — pagamento (em 07-PAGAMENTO.md)
Dia 12 (quarta): Webhook Stripe + Customer Portal
Dia 13 (quinta): Email transacional + smoke test
Dia 14 (sexta): Deploy producao + dominio + ultimo smoke test
```

### Sinal de que voce ta bem

- Apos PROMPT A: `npm run dev` roda sem erro, abre `localhost:3000`, mostra placeholder
- Apos PROMPT B: voce consegue se cadastrar, logar, ver area logada, mas feature core mostra paywall
- Apos PROMPT C: voce consegue pagar com cartao de teste, paywall some, feature funciona

### Sinal de que voce ta mal

| Sinal | O que fazer |
|---|---|
| Mais de 3h no mesmo erro | Para. Le erro com calma. Considera reverter o ultimo passo |
| "Funciona, mas nao sei por que" | Para. Pede o Claude pra explicar antes de seguir |
| Mudanca enorme em arquivo nao pedido | Rejeita. Pergunta por que. Pede menor |
| Voce ta querendo "mais 1 feature" | Para. Olha `mvp.md`. Se nao ta no TEM QUE TER, nao constroi |

## Quando algo quebra

Antes de gastar tempo:

```bash
# Veja o que mudou:
git diff

# Se a mudanca foi do Claude e quebrou:
git checkout {arquivo}  # reverte 1 arquivo
# OU
git reset --hard HEAD   # reverte tudo (cuidado, perde mudancas nao commitadas!)

# Se voce ainda nao commitou nada que esta funcionando, perde menos:
git stash  # guarda mudancas
# tenta de novo, se nao der:
git stash pop  # volta o que tinha
```

Por isso voce **commita toda hora**.

## Antes de seguir

```bash
git add .
git commit -m "MVP build feito ate paywall — ainda sem pagamento"
```

Vai pro `07-PAGAMENTO.md`.
