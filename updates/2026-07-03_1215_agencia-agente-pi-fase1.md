# agencia: AGENTE DE PI (fase 1) — Importar PI no ar

**Sessão 2026-07-03.** Plano aprovado pelo Pedro. Commit `abcfc21`, migration p39
aplicada em prod, edge `pi-extract` deployada (JWT exigido).

## O que existe agora
- **/admin (Super Admin)**: página "Agente & IA" — chave da Anthropic (Vault via
  `set_anthropic_key`, nunca exibida), modelo (Haiku default), toggle por tenant.
  Super admin = `profiles.is_super_admin` (Pedro marcado).
- **Pedidos (PI)** (`/app/risen-midia/pedidos-pi`, menu Operação): upload do PDF →
  edge `pi-extract` (Anthropic structured output, schema cobre os 5 formatos:
  MG/Hubix planilha e web, Brasil84/Operand, ABC prosa, Ponto Agile) → revisão
  humana com match de placas (placa_aliases → code → endereço), SEMÁFORO de
  disponibilidade por bi (conflito = vermelho c/ nome da campanha), alerta de
  preço abaixo da tabela, vencimentos editáveis → aprovar = RPC
  `approve_pi_document` (cliente agência + campanha 'approved' + campaign_items
  + receivables source='pi' + aliases aprendidos). Campanha cai na Agenda e na
  Comprovação (checking) sozinha.
- Estudo dos 14 PIs reais em `~/Dev/risen/risenagencia/Exemplos de PI`.

## ⚠️ Regra nova do Pedro (memória gravada)
API key da Anthropic é POR SISTEMA. A do Bitwarden é EXCLUSIVA do CRM (eirisen).
Pedro vai gerar uma chave própria pro Hub e colar em /admin. NÃO reusar.

## Pendências
- Golden set (14 PDFs) BLOQUEADO até a chave ser colada em /admin.
- Fase 2: emissão programada (`emitir_em` já é gravado; cron pi-emit a fazer).
- Fase 3: monitor do e-mail financeiro@ por tenant (campo já existe em /admin).
- Agente 2 ("o mês") — futuro.

## UPDATE mesma sessão: FASES 2 e 3 TAMBÉM NO AR (commit a7246c8)
- **Emitir/Agendar**: PI aprovado ganhou botão "Emitir" → dialog escolhe descrição,
  com/sem boletos (default segue forma_pagamento do PI), canal, modelos → "Emitir
  agora" (client-side, emitirPi: 1 NFS-e do total + N boletos com os VENCIMENTOS
  EXATOS do PI + 1 e-mail pro email_nf da agência + fatura no razão) OU "Agendar"
  (grava emissao_config + emitir_em; edge pi-emit roda no cron 07:30/12:30 UTC e
  faz o mesmo server-side via _shared/risen-core-server).
- **Monitor de e-mail**: edge pi-mail-watcher (cron 15min) — IMAP Gmail
  (npm:imapflow + mailparser, BOOT OK no edge runtime), tenant com agente ativo +
  monitored_email + senha de app no Vault (set_mail_password via /admin); e-mail
  não lido c/ PDF com cara de PI (regex assunto/arquivo) → storage → pi_document
  (source email) → pi-extract → fila de revisão. Marca \Seen.
- **Conferência PI × orçamento**: revisão mostra quotes não-cancelados com itens
  nas mesmas placas/bis e compara total (bate ✓ / difere ⚠).
- Smoke-test prod: pi-emit {processed:0} e pi-mail-watcher {results:{}} ok.
- SEGUE bloqueado no golden set: aguardando Pedro colar a chave exclusiva em /admin.
