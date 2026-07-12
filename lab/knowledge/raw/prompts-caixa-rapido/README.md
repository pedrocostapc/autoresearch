# Caixa Rapido

Como empresarios estao criando SaaS com IA e monetizando MUITO. Passo a passo pra aplicar ja.

> Esse pacote tem **10 prompts numerados em sequencia**, **um exemplo completo** mostrando um SaaS ficticio sendo construido do zero ao primeiro pagamento, **codigo starter** pro build (Next.js + Supabase + Stripe), e **frameworks de decisao com numeros** (nao "achismo").

## A premissa honesta

A maior parte do conteudo de "como criar SaaS" e:

- **Romantica:** fala de visao, missao, "encontrar sua paixao"
- **Confusa:** mistura SaaS de R$ 50/mes com unicornio de R$ 100M
- **Generica:** "achar nicho" sem explicar como
- **Tecnica demais:** assume que voce ja conhece Next.js, Stripe, Supabase

Esse pacote e diferente:

- **Cirurgico:** passo a passo com saidas concretas
- **B2B de nicho ate R$ 100k MRR:** o segmento real onde voce consegue caixa rapido
- **Numeros reais:** custo, timeline, criterios de decisao com threshold
- **Tecnico no necessario:** codigo starter funcionando + Claude Code montando o resto

## Quem deve ler

- Empresario que ja tem um negocio e quer transformar conhecimento em SaaS recorrente
- Profissional que entende profundamente de uma area (contador, advogado, agencia, consultor) e quer empacotar
- Quem ja tentou criar SaaS e travou em "achar nicho" ou "fazer o MVP"

## Quem **nao** deve ler

- Quem quer fazer "o proximo Notion" — nao e pra isso
- Quem nao quer cobrar dinheiro de cliente nenhum — sem cobrar, nao tem caixa rapido
- Quem nao tem nenhum acesso a um nicho especifico — voce vai precisar de canal pra encontrar 100 leads

## Conteudo

| # | Arquivo | O que voce sai com isso |
|---|---|---|
| 00 | LEIA-PRIMEIRO | Mentalidade + ordem + criterio de continuar |
| 01 | NICHO | 3 nichos avaliados + 1 escolhido com persona |
| 02 | VALIDACAO | Plano de validacao 7 dias + criterios objetivos pra seguir |
| 03 | MVP-MINIMO | Escopo cortado ao osso |
| 04 | ARQUITETURA | Stack escolhida + modelo de dados + ordem de construcao |
| 05 | LANDING | Landing codada (Next.js + Tailwind + shadcn) |
| 06 | BUILD | MVP construido com codigo starter pronto |
| 07 | PAGAMENTO | Stripe/MP plugado com codigo starter pronto |
| 08 | LANCAMENTO | Plano 7 dias + mensagens prontas |
| 09 | FEEDBACK | Sistema de customer success em 30 dias |
| 10 | ESCALA | Decisao escalar/pivotar/matar com framework numerico |
| E | EXEMPLO-COMPLETO | Tudo isso aplicado num SaaS ficticio (PontoFiscal pra contadores) |

## Tempo realista

- **Modo agressivo (full-time):** 14-21 dias do nicho ao primeiro pagamento
- **Modo realista (com trabalho durante o dia):** 30-45 dias
- **Modo lento (sozinho aprendendo):** 60-90 dias

Os prompts cabem em todos. O que muda e a velocidade.

## Como usar

1. Le `00-LEIA-PRIMEIRO.md` (10 minutos)
2. Le `EXEMPLO-COMPLETO.md` (30 minutos) — voce ve um SaaS sendo construido inteiro. Vale ouro.
3. Faz os 10 prompts em ordem. **Nao pula etapa.**
4. Cada prompt gera artefato (texto, codigo, plano). Salva em pasta propria do seu projeto. Versiona com Git.

## Stack que vamos usar

Pra deixar simples e barato:

- **Frontend + Backend:** Next.js 15 + TypeScript + Tailwind + shadcn/ui
- **Hospedagem:** Vercel (gratis ate dar trafego)
- **Banco + Auth:** Supabase (gratis ate 50k linhas e 50k MAU)
- **Pagamento:** Stripe (recorrencia BRL, com PIX) ou Mercado Pago
- **Email transacional:** Resend (gratis ate 3k/mes)
- **IA:** Claude API (paga por uso)

**Custo total mensal antes do primeiro cliente:** R$ 0 a R$ 50.

## A regra das 3 perguntas

Antes de comecar, voce tem que conseguir responder:

1. **Quem paga?** — Nome, cargo, perfil de pessoa especifica. Nao "PMEs". Nao "gestores".
2. **Quanto paga?** — Quanto essa pessoa ja gasta hoje pra resolver essa dor (ferramenta, mao-de-obra, tempo)?
3. **Como achar mais delas?** — Existe canal pra encontrar 100 dessas pessoas em ate 30 dias?

Se voce nao consegue responder, **nao comece**. Volta pro 01 e refina.

---

**ASV Digital** — produtos@asv.digital
