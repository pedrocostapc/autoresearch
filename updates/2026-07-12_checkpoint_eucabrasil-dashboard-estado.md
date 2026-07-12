# CHECKPOINT Euca Brasil — estado completo pra retomar do zero

**Escrito em 12/07/2026 (checkpoint de limite semanal).** Última sessão de trabalho: 08/07/2026. Este doc assume que a próxima sessão nasce SEM memória nenhuma.

## O que está NO AR (tudo commitado, pushado e deployado — nada pela metade)

- **Site**: https://eucabrasilinvestigacao.vercel.app · repo privado `pedrocostapc/eucabrasilinvestiga` · pasta `~/Dev/eucabrasilinvestigacao` · branch `main` sincronizada com origin (HEAD `2169dc2`), **working tree limpo**.
- **Página Início = dashboard executivo "Situação da Empresa"** (10 seções: KPIs · caixa mês a mês · funil orçamento→NF com gap R$ 22,8 mi · vendedores · aging inadimplência · contas a pagar atrasadas com flags imposto/sócia/intercompany · sócios×empréstimo · dinheiro em espécie · 7 alertas "A investigar" · método+conferência de saldos). Verificado com screenshot em prod, desktop e mobile.
- Dados do dashboard num único **meta key `dashboard`** (13KB) no Supabase — página carrega leve. Já importado.

## Onde está cada coisa

- **Cálculo**: função `dashboard()` no fim de `scripts/build-data.mjs` (antes do bloco "executa"). Front: componente `Inicio` em `src/App.tsx` (+ helpers `Secao`, `HBar`, `ColunasMensais`, `Alerta`, `Clamp`, `mi`, paleta `GRAF`).
- **Import**: `scripts/supabase-import.mjs` (linha `{ chave: 'dashboard', valor: load('dashboard.json') }` no metaRows).
- **Gabarito dos números** (pra conferir depois de qualquer rebuild): plano em `~/.claude/plans/voc-vai-ver-a-parsed-ripple.md`, seção "Números validados".
- **Memória do projeto** (método, achados, pegadinhas de dados): `~/.claude/projects/-Users-pedrocosta-Dev-eucabrasilinvestigacao/memory/eucabrasil-apuracao.md` — ATUALIZADA em 08/07 (inclui a correção do A.L. Armarinhos e os achados novos).
- Update anterior com o resumo dos achados: `2026-07-08_0420_eucabrasil-dashboard-executivo.md` (nesta pasta).

## Como retomar (passo a passo)

1. Ler a memória do projeto (arquivo acima) + o update de 08/07.
2. Dados mudaram? → `npm run data` (confere saldos 27.414,62 / 9.155,79 no terminal) → `node scripts/supabase-import.mjs` (credenciais em `dados/.supabase.env`, fora do git).
3. Front → `npm run dev` local; deploy = `git push` (Vercel builda) ou, se a fila travar, `vercel build --prod && vercel deploy --prebuilt --prod` (o `--prod` no build é obrigatório, senão dá mismatch de target).
4. Pegadinhas que derrubam qualquer análise nova: venda real filtra por `top` `/^VENDA/` (NUNCA por `natureza`); `mov_socios.sentido` = 'saída'/'entrada' COM acento; `fluxo_caixa.natureza` = 'receber'/'pagar' minúsculo; `parceiros_nc.recebido` = a EMPRESA recebeu DA pessoa; max-width não funciona em `<td>` (usar o helper `Clamp`).

## Pendências (com dono)

- **Pedro**: pedir os documentos que destravam a conciliação — **arquivo de retorno CNAB** da cobrança (Cresol + Sicoob) e **extrato Stone** (a aba Conciliação do site lista tudo com prioridade). Sem eles, boleto (R$ 3,7 mi) e cartão não fecham.
- **Pedro**: mostrar o dashboard pros donos (era o objetivo — a URL é a entrega).
- **Aberto (próxima sessão, quando o Pedro pedir)**: cruzar as saídas pra Eliane com nota/título (o que saiu sem lastro é o indício); investigar quem são A.L. ARMARINHOS (pôs R$ 800 mil na empresa) e MAGDA (R$ 300 mil); aprofundar o gap orçamento×NF por vendedor/mês.
- **Nada ficou pela metade**: não há código não commitado nem tarefa interrompida.

## Fora da esteira

Este projeto NÃO faz parte da esteira/frota (sem seção no COORDENACAO-ESTEIRA.md) — checkpoint só aqui e na memória do projeto.
