# eirisen: auditoria da pré-leitura da IA shipped + E2E ID do Pix (Fase 0 da conciliação)

Sessão eirisen 10/07 (noite). Dois commits em main, deployados:

**`9b39215` fix(ia)** — pré-leitura da IA atualizada pro sistema atual (auditoria
com 4 agentes, diagnóstico em `prompts/pre-leitura-audit/diagnostico-2026-07-10.md`):
- Matou contradição no prompt: seção Parceiros mandava montar wa.me na mão vs regra
  de sempre usar `create_whatsapp_link`.
- Campos-fantasma consertados (forwards.ai_notes agora chega na IA; campos de
  reagendamento da Agenda REMOVIDOS por decisão do Pedro).
- IA agora sabe da galeria de mídia automática e de agenda quebrada (aviso em vez
  de tools sumirem mudas).
- UI morta limpa (transcription_keywords, toggle "IA cria tarefas", rota /ia órfã,
  banner pro modo legado Sugestão). Os 9 tenants em persona_mode='manual' FICAM
  como estão (decisão Pedro).

**`c0f9634` feat(financeiro)** — E2E ID da transação Pix extraído do comprovante
(payment-proof) e exposto no /financeiro embaixo da contraparte. É a Fase 0 do
**sprint Conciliação Pix** (spec completo em `prompts/conciliacao-pix/01-spec-sprint.md`
+ cópia em ~/Dev/risen/risencrm/prompts/): comprovante × extrato bancário via Core
(Cora/Sicoob/MP), IA só confirma pagamento com match forte de E2E ID; extrato nunca
vai pra UI do atendente nem pro prompt.

**Fechado na mesma noite**: migration `conversation_payments.e2e_id` aplicada em
prod (Pedro aprovou) e provider-webhook deployado na sequência (boot 200). Total de
9 functions deployadas: ai-reply, ai-suggest, provider-webhook + 6 de box-schemas.
Comprovante novo já grava o E2E ID; antigos ficam sem (não reprocessa retroativo).

## UPDATE 11/07 noite — bug de expiração de créditos DESARMADO

Auditoria FEFO (prompts/fefo-lotes-audit/): expiração de lotes debitava valor
CHEIO do saldo vivo (gasto nunca consumia lote — FEFO nunca existiu). Vítimas:
Construai -1000 (restituído 10/07), Betel/Euca ZERADOS na madrugada de 11/07.

DECISÃO PEDRO: crédito NÃO expira mais, nenhum tipo ("nosso modelo é fazer querer
usar o robô, não confiscar"). Migration 20260711230000 aplicada em prod: trigger
com expires_at=NULL, 26 lotes ativos desarmados, cron expire-lots-daily OFF
(via cron.alter_job — role não tem UPDATE em cron.job). Verificado: 0 bombas.

PENDENTE passo 2: restituição dos saldos lesados (dívida dura externa ~R$100:
Fernandes 92,83 + Betel 6,80; tenant do próprio Pedro: ~1.054). Planilha
linha-do-tempo de cada tenant em prompts/fefo-lotes-audit/. Bônus: Stripe
confirmou que as 2 "recargas" R$99 da Betel eram manuais sem pagamento, e que a
assinatura live da Betel (13/05, R$299,90/ANO) não está na tabela subscriptions
(webhook live não registra — investigar depois).
