# 05 — Landing page

Criar a landing que converte **antes** do produto existir.

## Por que landing primeiro

Voce pode (e deve) publicar a landing **antes do produto pronto**. Razoes:

1. **Valida demanda real** com trafego — se ninguem se cadastra na lista de espera, voce sabe que tem problema
2. **Captura leads** que viram clientes assim que voce lanca
3. **Forca clareza** sobre o que e o produto (se voce nao consegue escrever a landing, voce nao sabe o que esta construindo)

## O que voce sai com esse prompt

- Landing page completa em Next.js + Tailwind + shadcn — codigo pronto
- Copy escrita pra cada secao
- Componentes separados em arquivos
- SEO basico (title, meta, og)
- Tracking de conversao configurado

---

--- COMECO DO PROMPT ---

Voce e um copywriter direto + dev senior em Next.js. Sua missao: gerar uma landing page completa, codada, pronta pra deploy no Vercel, que converta visitante interessado em "lead que paga" (ou pelo menos "lead quente na lista de espera").

# Contexto

Cole abaixo:

<nicho>
{COLE NICHO.MD}
</nicho>

<mvp>
{COLE MVP.MD}
</mvp>

# Decisoes minhas

- Dominio: {ex: pontofiscal.com.br ou ainda nao definido}
- Estagio: {pre-MVP / MVP em construcao / MVP pronto}
- CTA principal: {ex: "agendar conversa de 15min" / "pagar agora" / "entrar pra lista de espera"}
- Preco a exibir: {ex: R$ 49/mes ou "sob consulta" ou "em breve"}
- Tracking: {Plausible US$9 / Vercel Analytics gratis / Umami self-host}

# O que voce me entrega

## 1. Estrutura da landing

Estrutura B2B SaaS de nicho que converte (em ordem):

```
1. Hero — promessa nuclear + CTA primario
2. Dor — problema do cliente, na voz dele (sem mencionar voce)
3. Solucao — como o produto resolve em 3 passos
4. Demonstracao — print/video curto/print animado
5. Para quem e (e para quem nao e — esse filtro converte mais)
6. Preco — claro, sem trocadilho
7. Prova social — depoimento das pre-vendas (mesmo que "fundadores beta") OU "estamos comecando" honesto
8. FAQ — 6-10 perguntas reais que apareceram nas conversas de validacao
9. CTA final
10. Rodape minimo (CNPJ, contato, politica de privacidade)
```

## 2. Copy completa de cada secao

Use linguagem do `nicho.md` (a do publico, nao a sua).

### Hero
- **Titulo**: maximo 8 palavras. Beneficio especifico, sem clichê
  - ✅ "Lembrete de DAS-MEI no automatico, pra todos seus clientes."
  - ❌ "Revolucione sua gestao com IA"
- **Subtitulo**: 1-2 linhas. Pra QUEM + O QUE entrega + DIFERENCIAL
  - ✅ "Voce cadastra. A gente lembra. Cliente paga. Voce nao perde mais cliente por esquecer."
- **CTA**: verbo + beneficio
  - ✅ "Calcular meu primeiro DAS agora"
  - ❌ "Comecar"

### Dor
3-5 sintomas que o cliente reconhece. **Bullets curtos.**

### Solucao
3 passos numerados, beneficio em cada um.

### Para quem e / Para quem NAO e
2 colunas:
- **PARA**: 3-5 bullets de quem o produto serve
- **NAO PARA**: 2-3 bullets — filtra publico errado, **converte mais**

### FAQ
6-10 perguntas REAIS que apareceram em `validacao.md`. Resposta direta.

## 3. Implementacao tecnica (codigo pronto)

Crie os arquivos:

```
app/
└── (marketing)/
    ├── layout.tsx
    ├── page.tsx
    └── _components/
        ├── Hero.tsx
        ├── Dor.tsx
        ├── Solucao.tsx
        ├── Demo.tsx
        ├── ParaQuem.tsx
        ├── Preco.tsx
        ├── ProvaSocial.tsx
        ├── Faq.tsx
        ├── CtaFinal.tsx
        └── Footer.tsx
```

### Codigo de exemplo — `app/(marketing)/_components/Hero.tsx`

```tsx
import { Button } from '@/components/ui/button'
import Link from 'next/link'

export function Hero() {
  return (
    <section className="relative bg-background py-24 sm:py-32">
      <div className="mx-auto max-w-4xl px-6 text-center">
        <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
          {/* TITULO */}
        </h1>
        <p className="mt-6 text-lg leading-8 text-muted-foreground">
          {/* SUBTITULO */}
        </p>
        <div className="mt-10 flex items-center justify-center gap-x-6">
          <Button size="lg" asChild data-cta="hero">
            <Link href="/signup">{/* CTA */}</Link>
          </Button>
          <Link
            href="#preco"
            className="text-sm font-semibold leading-6"
          >
            Ver preco <span aria-hidden="true">→</span>
          </Link>
        </div>
      </div>
    </section>
  )
}
```

### Codigo de exemplo — `app/(marketing)/_components/Faq.tsx`

```tsx
'use client'

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'

const FAQS = [
  { q: '...', a: '...' },
  { q: '...', a: '...' },
]

export function Faq() {
  return (
    <section className="py-20 sm:py-32">
      <div className="mx-auto max-w-3xl px-6">
        <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
          Perguntas frequentes
        </h2>
        <Accordion type="single" collapsible className="mt-10">
          {FAQS.map(({ q, a }, i) => (
            <AccordionItem key={i} value={`item-${i}`}>
              <AccordionTrigger>{q}</AccordionTrigger>
              <AccordionContent>{a}</AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </section>
  )
}
```

(use o mesmo padrao pros outros componentes)

### `app/(marketing)/page.tsx`

```tsx
import { Hero } from './_components/Hero'
import { Dor } from './_components/Dor'
import { Solucao } from './_components/Solucao'
import { Demo } from './_components/Demo'
import { ParaQuem } from './_components/ParaQuem'
import { Preco } from './_components/Preco'
import { ProvaSocial } from './_components/ProvaSocial'
import { Faq } from './_components/Faq'
import { CtaFinal } from './_components/CtaFinal'

export default function HomePage() {
  return (
    <>
      <Hero />
      <Dor />
      <Solucao />
      <Demo />
      <ParaQuem />
      <Preco />
      <ProvaSocial />
      <Faq />
      <CtaFinal />
    </>
  )
}
```

### Mobile-first

Todos os componentes responsivos:
- Tipografia escala (`text-4xl sm:text-6xl`)
- Espacamento aumenta em telas grandes (`py-24 sm:py-32`)
- Grids viram coluna unica em mobile

## 4. SEO

Em `app/(marketing)/layout.tsx`:

```tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '{TITULO SEO — 50-60 chars} | {NOME PRODUTO}',
  description: '{DESCRICAO SEO — 150-160 chars}',
  openGraph: {
    title: '{TITULO}',
    description: '{DESCRICAO}',
    images: ['/og-image.png'],  // 1200x630
    url: 'https://{dominio}',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: '{TITULO}',
    description: '{DESCRICAO}',
    images: ['/og-image.png'],
  },
}
```

Sugira o que colocar no `og-image.png` (gere com Figma/Canva: titulo grande + logo + cor marca).

## 5. Tracking de conversao

Recomendo Vercel Analytics (gratis ate 2.5k events/mes):

```bash
npm install @vercel/analytics
```

Em `app/layout.tsx`:

```tsx
import { Analytics } from '@vercel/analytics/react'

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
```

Eventos minimos a rastrear:
- `pageview` (automatico)
- `cta_hero_click` — botao do hero
- `cta_final_click` — botao do final
- `signup_started` — quando entra em /signup
- `signup_completed` — quando faz cadastro

```tsx
import { track } from '@vercel/analytics'

<Button onClick={() => track('cta_hero_click')}>...</Button>
```

## 6. Lista de espera (se MVP ainda nao pronto)

Se voce ainda nao tem produto ligado, o CTA leva pra formulario de lista de espera:

```tsx
// app/(marketing)/_components/ListaEsperaForm.tsx
'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

const schema = z.object({
  email: z.string().email(),
  contexto: z.string().min(10).max(280).optional(),
})

type FormData = z.infer<typeof schema>

export function ListaEsperaForm() {
  const { register, handleSubmit, formState } = useForm<FormData>({
    resolver: zodResolver(schema)
  })

  async function onSubmit(data: FormData) {
    await fetch('/api/lista-espera', {
      method: 'POST',
      body: JSON.stringify(data)
    })
    // toast sucesso
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input type="email" {...register('email')} placeholder="Seu email" />
      <textarea {...register('contexto')} placeholder="Conta um pouco do seu negocio (opcional)" />
      <button type="submit" disabled={formState.isSubmitting}>
        Entrar na fila
      </button>
    </form>
  )
}
```

E `app/api/lista-espera/route.ts` que salva no Supabase (tabela simples) + dispara email.

Faca o trabalho completo. Crie os arquivos. Mostre primeiro a copy de cada secao, depois o codigo.

--- FIM DO PROMPT ---

---

## Sinal verde pra ir pro `06-BUILD.md`

- [ ] Landing publicada no Vercel
- [ ] Dominio configurado
- [ ] Lista de espera capturando emails
- [ ] Pelo menos 1 visitante real ja viu (mesmo que voce mesmo)
- [ ] Tracking ligado

## Atalho

Voce pode (e deve) divulgar a landing antes do produto pronto:

- Posta no LinkedIn pessoal
- Manda nos grupos de WhatsApp
- Cola em assinatura de email
- Coloca no Instagram bio

Em 7 dias, **se nao chegou em 20-50 cadastros na lista de espera com algum trafego**, voce tem informacao valiosa: a copy/oferta nao bate com o publico. Volta pro `01-NICHO.md` ou `02-VALIDACAO.md`.

## Erros comuns

1. **Copy cheia de marketinges** — usa linguagem do nicho, nao da agencia
2. **Hero sem promessa nuclear clara** — visitante sai em 5s
3. **Sem secao "para quem NAO e"** — atrai publico errado, queima leads
4. **Preco escondido** — "fale com vendas" mata conversao em ticket baixo
5. **FAQ generica** — usa as PERGUNTAS REAIS das suas conversas, nao "o que e seu produto?"

## Antes de seguir

```bash
git add app/
git commit -m "landing publicada"
git push
# deploy automatico na Vercel
```

Vai pro `06-BUILD.md`.
