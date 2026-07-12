# Core — inventário completo + plano de propagação pros apps (06/jul/2026)

Estado do **Risen Core** (broker `hjclvuzugdbpvnomvtpn`, branch feat/core-broker-fundacao)
e do que já está **implantado no Hub**. Serve de mapa pra próxima fase: **replicar as
telas (Conectores, Extrato, Boletos) e as integrações nos outros apps**, todos consumindo
o MESMO Core. Nada de app-a-app: tudo via broker `v1-call`.

## 1. O que o Core FAZ hoje — capabilities por sistema (ao vivo)

**Pagamentos / Banco**
- **cora**: testar_conexao, config, webhooks (criar/listar/excluir), emitir/consultar/cancelar/listar boleto, `emitir_pix_qr`, `dados_conta`, `saldo_conta`, `extrato_conta`, `pagar_boleto_stage` (saída DESLIGADA por trava)
- **sicoob**: testar_conexao, config, `saldo_conta`, `extrato_conta` (Conta Corrente v4, mTLS A1)
- **mercadopago**: testar_conexao, config, `cobrar` (pix/boleto/cartão + split), `extrato_conta` (entradas+saídas), `consultar_pagamento` — + OAuth "conecta num clique" (`v1-mp-oauth`)
- **asaas**: config, cobrar, cliente.criar, cartao.tokenizar, assinatura.criar/status/cancelar
- **stripe**: config, checkout.criar, link.criar, conectar, status
- **assinatura**: criar, cancelar (régua de recorrência sobre asaas/stripe)

**Extrato multibanco** (o unificado)
- **extrato**: `extrato.list`, `saldo.get` — lê a view `v_extrato_entries` (Cora + Sicoob + MP num lugar só). Espelho alimentado por crons `bank-statement-sync-tick` (*/15) e `cora-statement-sync-tick`. Cada lançamento carrega **transaction_id (E2E do Pix)**.

**Fiscal**
- **govnfse** (gov.br, self-hosted no Core, assina DPS + mTLS): gerar_dps, emitir/consultar/listar nfse, baixar_danfse, testar_cert, diagnostico, diag_dfe — **emite ponta a ponta**
- **focus** (Focus NFe, 3º canal): emitir nfe/nfse/nfse_nacional, consultar/cancelar, reenviar_email, listar_nfes_recebidas, manifestar_nfe, webhook, testar — **empresa Risen cadastrada (id 229710), liga/desliga via `ativo`**
- **v1-fiscal-templates**: templates de boleto/NFS-e + contrato (Core dono do template)
- **v1-notify**: 1 e-mail ao cliente com nota+xml+boleto anexos (via Resend)

**Barramento de eventos** (pub/sub): `v1-events-publish` + `events-dispatch-tick` — ex.: `core.cobranca.paga` Cora→Hub dá baixa no boleto.

**Concierge Bridge** (fila de aprovações do Pedro): `v1-concierge-inbox/pending/ack` — app enfileira → Realtime → braço local executa.

**GTIN** (o que já era operante): v1-gtin, v1-gtin-by-date, v1-gtin-resolve, gtin-worker-tick, gtin-sources-status, image-backfill-tick.

**Broker / infra**: `v1-call` (roteador HMAC + tenant translation), `v1-capabilities-register`, `v1-manifest`, `v1-credentials-set`, webhooks (cora/focus/mercadopago/asaas).

**Sistemas consumidores já registrados** (targets/callers): risen-agency (Hub), risenos, risen-whatsai (Ei Risen), minha-obra, risen.
**risenos** já tem capabilities próprias no broker: echo, produtos.listar, produto.obter, estoque.consultar, **erp.pedido.criar/obter**.

## 2. O que está IMPLANTADO no Hub (risen-agency) — o modelo a replicar

Pro tenant **risen-midia** estão plugadas AO VIVO 5 credenciais: **cora, mercadopago, sicoob, focus, govnfse**.

Telas/UX construídas no Hub (é isso que vai "conviver" nos outros apps):
- **Conectores** (`IntegrationsSettingsPage`): liga/desliga por tenant, some do menu quando off; **Certificado A1 = credencial compartilhada** (anexa 1x, serve Sicoob/gov.br/Focus); **Mercado Pago = OAuth 1 clique**; **Focus com toggle real** (bate no `ativo` do Core); cards Cora/Sicoob/gov.br.
- **Extrato** (`ExtratoPage`): multibanco (Cora+MP+Sicoob), **coluna Banco**, **ID transação (E2E)**, tipos em PT, filtro por banco, Realtime.
- **Boletos** (`BoletosPage`): **coluna Banco emissor**, filtro de banco, Forma em PT.
- **Emissão fiscal** + **notify** (nota+boleto+e-mail), templates do Core.
- Proxy `risen-core-proxy` (mapa service→capability, HMAC, envelope).

## 3. Próxima fase — propagar pros outros apps

Todos consomem o MESMO Core (via cada `*-core-proxy` do app). O que cada app recebe:
- **RisenOS**: Conectores + Extrato + Boletos (mesmas telas) + já tem pedido (erp.pedido). **Aqui vai a tela "casar por comprovante" (E2E)** — é onde existe PEDIDO pra casar. Fiscal (emite consumindo o SuperSec).
- **Ei Risen**: Conectores + Extrato + (opcional boletos). Conciliação por comprovante também faz sentido (atendimento).
- **SuperSec**: já tem Conectores (módulo opt-in). É o CÉREBRO FISCAL (confere, não emite).
- **agencia/minhaobra/nafazenda**: Conectores + Extrato + Boletos conforme o app precisar.

**Padrão da propagação:** faz no Hub (feito) → replica a tela + o proxy em cada app →
liga as credenciais por tenant. Core não muda (é compartilhado); só o front de cada app
ganha as telas. Conciliação por comprovante (E2E) = RisenOS/Ei Risen, NÃO no Hub (no Hub
concilia pela baixa do boleto).

Ver memória risencore: [[extrato-conciliacao-e2e]], [[focus-empresa-cadastrada]],
[[conectores-modulo-opt-in]], [[mercadopago-conector]], [[papeis-da-frota-e-core-cerebro]].
