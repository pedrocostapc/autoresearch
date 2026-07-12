# Processos/Dossiês — auto-agrupamento de documentos por job

**Repo:** super-secretaria-functions · **commit local:** `057c640` (não pushado)

## O que é
Pedido do Pedro: arquivos que sozinhos não têm sentido (PP + nota fiscal +
comprovante + fotos da "Festa do Sol") precisam virar um **processo** sozinhos.
A chave de vínculo já vive nos dados: o nº do job aparece no filename
("2862.6 - ... Festa do Sol", "PI 2418.77 - NF 775") e na discriminação da NF.

## Implementação (4 migrations)
- `20260612140000_processos.sql` — tabelas `processos` + `processo_documentos`
  (RLS por tenant), `extrair_referencia`, `montar_processos` (varredura
  idempotente, gated), `processo_detalhe` (RPC pra UI).
- `141000_service_role` — montar_processos roda via service role (cron/backend,
  `auth.uid() is null`).
- `142000_ref_ampla` — chave = nº solto no início do filename OU prefixo
  PI/PP/Pedido; `titulo_processo` extrai o nome do projeto ("Festa do Sol").
- `143000_anti_data` — exclui competência `AAAA[.-]MM` (ano 2005-2035 + mês
  1-12). Sem isso, boletos/folhas nomeados "2014-08 INSS", "2021.03 BOLETO"
  viravam processo fantasma (ex.: 29 boletos num "processo" #2021.01).

## Validação read-only (contra prod, sem tocar)
Simulei a regex nova via REST sobre os filenames reais:
- **15 jobs reais mantidos** (todos no range 2418-3039, ex.: Festa do Sol 2862.6
  = 15 docs; 2418.90 = 12; 2773.21 = 11 — PP + NFs + fotos juntos).
- **287 docs-data descartados** (51 competências distintas: INSS/FGTS/folha/boleto).

## Estado
- Migrations escritas, validadas e **commitadas local** — push **gated**
  (o `143000` dá truncate/delete nas tabelas-derivadas de dossiê; precisa do OK
  do Pedro antes do `supabase db push`).
- **Falta (próxima fase):** UI de dossiê consumindo `processo_detalhe`;
  refinamento de título/agrupamento via LLM (hoje é heurística determinística).

## Pendências herdadas (intocadas)
- Rotação das chaves vazadas (.env*.bak) — Pedro fecha quando tudo resolver.
- Chaves de provedor (OpenAI failover etc.) — Pedro cola depois.
