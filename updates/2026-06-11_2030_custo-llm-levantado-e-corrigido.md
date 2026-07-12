# Custo LLM do SuperSec: levantado (R$ 37,40 hoje) e instrumentado de verdade

> Criado: 2026-06-11 ~20:30 — sessão Claude Code em `super-secretaria-functions`

## O levantamento (Pedro: "não tenho ideia de quanto me custa rodar os arquivos")

Via REST (service role, read-only) sobre `agent_runs` de prod:
- **R$ 37,40 registrados em 11/06** (único dia com dados — reprocesso em massa),
  ≈ US$ 6,71. 4.764 runs, 4.645 docs únicos, 2,94M tok in + 756k out, 100% Haiku 4.5.
- 52% dos runs usam LLM; 48% são XML/determinístico (custo zero).
- **~R$ 0,008/doc geral · ~R$ 0,015/doc com LLM** · run mais caro: R$ 0,11.

## Bugs/gaps achados e corrigidos (branch `feat/custo-llm-usage`, commit 0cdca13)

1. **Subcontagem**: classify+extract = 2 chamadas, só a última era gravada
   (`c.llm?.usage ?? c.llmUsage`). Agora `c.llmUsages[]` acumula tudo.
2. **Preço hardcoded de Haiku**: virou `llmCostCentsBRL()` com tabela por modelo
   (haiku 1/5, sonnet 3/15 USD/Mtok, ×5,50); desconhecido cobra como Sonnet.
3. **Tabela `usage` VAZIA** → cobrança metered de tokens (multiplier 4.7 em
   `plans.metadata`) não tinha base faturável. Migration `custo_usage_margem`:
   `refresh_usage()` + cron horário populam tenant×mês de `agent_runs`.
4. RPCs novas (gate is_super_admin): `admin_custo_margem(p_days)` (custo
   wholesale / receita retail ×4.7 / margem / por dia/tenant/modelo) e
   `admin_parser_saude()` (extratos por banco: confiança, parsers, sem-parse).

## Front (supersec `feat/ui-handoff`, commit 729511c)

/admin ganhou **Custo & margem** (KPIs + período hoje/7d/30d/90d + barras por
dia + tabela por tenant) e **Parsers de extrato por banco** — estrutura copiada
do superadmin do risen-ai-connect (`~/Dev/risen/risencrm/risen-ai-connect/src/
features/admin/`), que o Pedro mandou usar de referência.

## Gates pendentes (Pedro)

- Aplicar a migration em prod (`supabase db push`) e deployar worker-agent-1.
- Push dos dois branches. deno test 59/59 ok; deno check sem erros novos.
