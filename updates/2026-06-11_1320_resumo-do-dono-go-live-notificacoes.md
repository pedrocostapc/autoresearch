# Resumo do dono v3.2 + go-live do sistema de notificações (ai-connect)

> Criado: 2026-06-11 13:20 — sessão Claude Code em `risen-ai-connect`

## O que foi pedido (Pedro, madrugada→manhã de 11/06)

Transformar o relatório diário dos tenants em "1 tela sem scroll" com valor
de dono (não métrica de produto), corrigir o canal de notificações (helpdesk
Risen Suporte) e colocar o sistema no ar.

## O que foi construído/decidido (tudo em main + prod)

- **Resumo do dono v3.2** (template `daily_report`): 7 métricas fixas
  definidas pelo Pedro — chamadas (clientes distintos, não msgs), orçamentos
  em aberto (antes de vendas), vendas fechadas, encaminhados pra vendas,
  tempo médio de resposta humana, clientes sem retorno, maior demanda do dia
  (line_items). Fonte = `conversation_extracts` (camada Map dos insights),
  agregação 100% código, zero LLM. Envio 8h BRT sobre ontem. Rótulos
  editáveis em /admin/notificações. Migrations ...140000/150000/160000.
- **Bugs corrigidos em prod:** (1) safeupdate quebrava UPDATEs sem WHERE em 4
  funções singleton (vincular canal etc.) — mig ...113000; (2) "401 fóssil"
  no reconcile-instance-status: instância re-pareada ficava presa em
  disconnected (casos Vanderlei/Fixoloja, Chocodoces, juniobetel, Feijoada —
  todos autocorrigidos pós-deploy); (3) templates de alarme com domínio velho
  risencrm.com e rota inexistente → eirisen.com.br + /inbox?conv= + spintax.
- **Go-live:** canal vinculado ao risen-suporte (+55 38 9832-8411), 7
  telefones de donos verificados (Pedro autorizou pular OTP), switch "Envio
  em massa" ligado, lote de 6 resumos entregue ~9h50 pelo caminho oficial
  (fila→drainer com gap anti-ban→dispatcher) — 6/6 sent.
- **Cortesia + backfill insights:** R$ 970 concedidos via apply_credit_grant
  (PavGas 660, CRD 140, juniobetel 120, Nudeck 50) e 2.229 conversas
  enfileiradas pro Extractor (Feijoada/Nudeck concluídos; PavGas ao longo da
  tarde). Nudeck sobrou R$ 1,36 — daily dele trava sem topo extra.

## ⚠️ Pendência CRÍTICA (bloqueia o automático de amanhã 8h)

Os crons `notification-scanner` e `notification-drainer` **nunca funcionaram**:
usam `current_setting('app.functions_url')`/`('app.internal_function_secret')`
que estão NULL → toda execução falha. Hoje o lote saiu manual. Fix = 2
`ALTER DATABASE postgres SET ...` (classificador exige autorização explícita
do Pedro — pendente de "pode alterar o banco", ou ele roda no SQL Editor com
o segredo do `.env.local` do ai-connect).

## Outras pendências do bloco

- [ ] Nudeck: topo de cortesia (~R$ 20–30) se quiser extração diária
- [ ] Costa/ErpObras (tenant do Pedro): apikey da Evolution inválida no banco
      (HTTP 401) — reconcile não enxerga; corrigir via backfill-evolution-apikeys
      ou autorização pra ler EVOLUTION_API_KEY do secret store
- [ ] Pav Gas backfill termina ~meio da tarde (fila 8/min)

## Caminhos

Doc do design: `risen-ai-connect/prompts/tenant-notifications/resumo-do-dono.md`
(+ cópia global em `~/Dev/risen/risencrm/prompts/tenant-notifications/`).
Scanner: `supabase/functions/notification-scanner/index.ts`. Commits de hoje
na main: ed907df → (vários) → v3.2.
