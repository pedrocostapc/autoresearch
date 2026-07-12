# Euca Brasil: dashboard executivo no ar + achados novos da análise CFO

**Sessão de 08/07/2026 (~04h).** Repo `~/Dev/eucabrasilinvestigacao`, deploy prod OK em https://eucabrasilinvestigacao.vercel.app.

## O que mudou
- A página **Início virou um dashboard executivo** ("Situação da Empresa"): KPIs, caixa mês a mês, funil orçamento→NF, ranking de vendedores (inadimplência/margem/% dinheiro), aging receber/pagar, sócios×empréstimo, dinheiro em espécie e cards "Pontos a investigar".
- Dados num único meta key **`dashboard`** (13KB) gerado por `dashboard()` no `scripts/build-data.mjs` e importado pelo `supabase-import.mjs`. Página carrega leve (só meta).
- Cores de gráfico validadas com a skill dataviz; helper `Clamp` pra nomes longos em td.

## Achados novos (registrados na memória do projeto)
- **Gap orçamento×NF R$ 22,8 mi**: 1.523 orçamentos "faturados" (R$ 29,7 mi) × R$ 6,9 mi de vendas com NF-e. J J RURALISTA: R$ 5,9 mi orçados × R$ 252k com nota. Indício de venda sem nota (com caveat de re-emissão). Venda real filtra por `top` `/^VENDA/`, nunca por `natureza`.
- **Dinheiro em espécie R$ 1,09 mi** crescendo desde março; CAMILA registra mais que a Danielle.
- **Empréstimo Sicoob (R$ 1,92 mi) entra nos mesmos meses das maiores saídas pra Eliane** (abr e jun/26).
- **CORREÇÃO de direção**: A.L. ARMARINHOS e MAGDA **puseram** dinheiro NA empresa (R$ 800k + R$ 300k), não o contrário (semântica `recebido` = empresa recebeu). Memória corrigida.
- **R$ 386k de impostos vencidos** (SEFAZ MG/GO + RF); caixa total ~R$ 46k.
- O alerta antigo de "R$ 600k parados em investimento" era falso: aplicou 300k e resgatou tudo (líquido zero).
