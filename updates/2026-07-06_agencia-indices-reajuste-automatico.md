# agencia: índices BCB + reajuste automático de aluguel + mensalidades rolantes

Pedro pediu (2026-07-06): tabelinha de IGP-M/IPCA no sistema e aluguel virando
sozinho no aniversário. Entregue (p45+p46):
- indices_economicos: IGP-M(SGS 189)/IPCA(SGS 433) via API pública BCB, robô
  indices-sync diário. Aba Aluguéis→Índices.
- rent-reajuste diário: aniversário (last_reajuste_at/start+12m) → acumulado 12m
  → contrato + mensalidades futuras sem cobrança + rental_reajustes + sino.
  Deflação mantém valor (cláusula 7.3).
- 1ª rodada REAL: CYMI +4,14% IPCA (2.200→2.291,14), Ronaldo +1,96% IGP-M
  (2.700→2.753,04), Fernando IGP-M negativo (-2,66%) → mantido 2.500 ✓.
  João Pedro vira sozinho em 08/07.
- p46 mensalidades rolantes (+3m, cron diário) — bug "para após 12 meses" estava
  mordendo (nada depois de jun/2026); contrato ativo vencido SEGUE gerando
  (prorrogação indeterminada). 25 mensalidades novas jul-out já com reajuste.
- Contratos: 7 PDFs lidos (IGP-M casas, IPCA CYMI), anexados em bucket PRIVADO
  tenant-docs, end_dates conferidos, CYMI→ipca.
