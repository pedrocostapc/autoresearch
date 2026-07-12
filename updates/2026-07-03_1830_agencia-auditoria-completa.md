# agencia: AUDITORIA COMPLETA (7 agentes Sonnet) — relatório em briefings/AUDITORIA-2026-07-03.md

Pedro pediu mapeamento+teste de todas as páginas, campos faltantes e automações.
7 agentes auditaram: Operação, Outdoor, IG+Gráfica, Aluguéis+Portal, Financeiro,
Cadastros/Config/Shell, Backend. Relatório consolidado no repo (briefings/, untracked).

## Achados CRÍTICOS (não corrigidos ainda — aguardando OK do Pedro):
1. SEGURANÇA: RPCs financeiras SECURITY DEFINER sem tenant check (settle_rental_payment
   e mais 5) — cross-tenant write em dinheiro. Fix = migration com current_tenant_id().
2. Repasse ao dono = R$0 na baixa automática (triggers p32/p40 não calculam admin_fee/
   owner_transfer — só o botão manual calcula). Portal do dono e Repasses subestimados.
3. Filtro "Vencidos" sempre vazio (nada seta overdue) + ZERO cobrança automática de inadimplência.
4. Mensalidades de aluguel param após 12 meses (generate 1x na ativação, sem rolling).
5. Fila Semanal IG sempre vazia (due_at nunca gravado); grafica_orders sem página de gestão;
   tráfego pago fora do financeiro.
6. Orçamento: trocar cliente na edição não salva; desconto editável em aprovado.
7. Robôs críticos sem monitoração (withCronRun) e fora da AutomationPage; pi-emit erro não
   retenta; check-cert-expiry NÃO agendada; sync-boletos/sync-nfse crons mortos 3/3min.
8. Cliente sem IBGE emite NF com município vazio (sem aviso).

Features fantasma detectadas: SLA "Escalar", switch WhatsApp, protesto de boleto,
custom_sla_* por cliente, can_view_rentals, PDFs da placa (P21), Importar PDF placas.

## UPDATE: PACOTE CRÍTICO APLICADO (p43, commit abc4ad7)
1. Trigger trg_rental_payments_calc_repasse (BEFORE): QUALQUER baixa calcula taxa/repasse
   (fórmula do settle). Testado em prod com rollback: aluguel 2.200 → taxa 220 (10%) →
   repasse 1.980 ✓. Bomba do dia 25 desarmada.
2. Tenant checks: settle_rental_payment (+ valor>0), generate_rental_payments,
   generate_pieces_for_contract, _create_receivables_outdoor/instagram/aluguel
   (_assert_tenant; service_role segue livre). process_approval_slas e
   compute_weekly_queue sem grant authenticated. _create_receivables_from_quote é
   INVOKER (RLS cobre) — não precisou.
3. receivables-overdue (cron diário 09:00 UTC): emitted→overdue + notificação no sino +
   e-mail de cobrança 1x (overdue_notified_at). Smoke: {marcadas:0, notificadas:0} ✓.
   AutomationPage agora lista os 7 robôs financeiros novos.
Pendências do relatório seguem: mensalidades rolantes, campos de imóvel/contrato,
fila semanal IG, gestão de pedidos gráfica, etc. (briefings/AUDITORIA-2026-07-03.md)
