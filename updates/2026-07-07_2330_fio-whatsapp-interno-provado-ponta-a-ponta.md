# Fio WhatsApp interno (Hub→Ei Risen via Core) PROVADO ponta a ponta — 07/jul/2026

Marco: o **1º fio interno da frota** está vivo de verdade. Hub Mídia OOH emite/cobra e a
mensagem sai pelo WhatsApp do cliente **pelo canal do Ei Risen**, roteado pelo **Core** (broker
`v1-call`) — sem app-a-app direto. É a prova de que o modelo "inter-sistema sempre via Core"
funciona com dado sensível viajando + gating por tenant.

## O que ficou provado hoje (na ordem)
1. **Consentimento estilo "Entrar com Google"** (a pedido do Pedro): o Hub abre uma **janelinha
   popup** (não página cheia) → dono loga no Ei Risen (tenant Financeiro `costa-bc5f6dff`) e
   Autoriza → popup fecha sozinho e devolve status via `postMessage`. Rota `/autorizar-frota`
   saiu de dentro do AppShell (página limpa, sem sidebar). AuthGate preserva `?params` no
   pós-login. Commits: Ei Risen `12836de`, Hub `3d9ba9e`.
   - Bug que travou antes: build da main do Ei Risen estava em **ERROR** (sintaxe `?? com ||` sem
     parênteses em AutorizarFrotaPage) → `eirisen.com.br` servia build velho → 404 na rota. NÃO
     era Lovable segurando: **o Ei Risen deploya por VERCEL** (projeto `eirisen`). Lição: quando o
     live diverge da main, cheque o ESTADO do build na Vercel, não presuma o editor.
2. **Grant + opt-in**: autorizar criou `core_tenant_link` risen-midia(Hub) ↔ costa-bc5f6dff
   (Ei Risen) `active:true` + ligou `tenant_settings.fleet_whatsapp_enabled` (scope [cobranca,nota]).
3. **Estado na UI do Hub** persiste (grava `tenant_integration_credentials` igual ao OAuth do MP);
   card mostra "✓ Conectado" no reload. Commit Hub `2ae4ba1`.
4. **7b — broker completo (`v1-call`)**: chamada como Hub (`risen-agency`/`risen-midia`) →
   traduziu tenant → checou grant → opt-in + escopo `cobranca` (régua real, sem atalho 'teste') →
   HMAC → `v1-eirisen` ENTREGOU. `enviado:true`, provider_message_id 3EB0247195BB482B66704E,
   5538999143316. Auditoria `fleet_whatsapp_audit`: status sent. Pedro confirmou a chegada no Zap.

## Segurança/gates observados
- Mint de API key temp no Core (pra rodar o 7b) é **prod write GATED** — o classifier bloqueia
  sozinho; precisa do "pode/try again" do Pedro. Revoguei a key no fim (nunca tocou disco/chat).
- Envio WhatsApp só no número do Pedro (regra dele).

## Falta (decomposto, gated por ação) — continuar daqui
- **Peça 2 (template de produção)** em `v1-eirisen`: hoje aceita `texto` cru (fronteira de teste).
  Produção = payload `{tipo:'cobranca', dados:{valor,vencimento,linha_digitavel,pix}}` renderizado
  por template AQUI DENTRO; corta texto livre (fecha "nunca conversa livre"). Junto: `v1-call`
  passar `consumer` (slug do chamador) pro target — hoje a auditoria grava `caller_app:'desconhecido'`.
- **Peça 3 (gatilho no Hub)**: ao emitir boleto, disparar `whatsapp.enviar` sozinho (+ PDF/PIX).
- **Régua** D-3/D0/D+3/D+7 via evento `core.cobranca.vencida` + idempotência.
- **Inbox**: msg cair no thread do cliente (reusa `provider-webhook` — mensageria viva, cuidado).

Memória viva com todo o estado: risencore `fio-whatsapp-estado-atual`. Refs/caminhos dos apps:
`frota-refs-e-caminhos`. Modelo de cobrança: `cobranca-modelo-risen-carteira`.
</content>
</invoke>
