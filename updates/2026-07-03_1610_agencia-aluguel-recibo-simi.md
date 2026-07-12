# agencia: aluguel sem NFS-e no Contas a Receber + recibo no layout SIMI

**Sessão 2026-07-03** (commits 7a5a439 + 5cdb0d8). Implementa a decisão #12.

1. **Contas a Receber**: origem `aluguel` NÃO mostra mais "emitir" (nem boleto nem
   NFS-e). Coluna "NF / Recibo" mostra: "✓ recibo <data>" (recibo_sent_at),
   "recibo pendente (sai em minutos)" (pago, cron 10min pega) ou "recibo
   automático após o pagamento". Serviço normal intacto.
2. **p40** (aplicada em prod): marcar o RECEBÍVEL de aluguel como pago agora baixa
   a rental_payment → trigger p32 dispara o recibo. Testado em prod com
   transação+rollback (mensalidade baixou, nada persistiu, nenhum e-mail).
   Pipeline conferido: cron send-rent-receipt ativo, triggers p32 ok, 78 enviados
   / 0 pendentes.
3. **Recibo restilizado** (send-rent-receipt redeployada): carta declaratória de
   quitação igual ao modelo SIMI que o Pedro mandou. **Emitente = DONO do imóvel**
   (owner_client_id): casa com o modelo de documento pelo CPF/CNPJ (PC Serviços ×
   Ivete), fallback default → dados do owner. Amostra PDF aprovada no chat.
