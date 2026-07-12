# PLANO — 1º fio interno (Hub→Ei Risen WhatsApp) + modelo de cobrança (07/jul/2026)

Ponto de retomada pra PRÓXIMA sessão (Pedro bateu o limite semanal). Design fechado
com o Pedro; falta construir. Contexto: 2ª camada do Core = integrações INTERNAS
(app↔app via broker). Este é o 1º fio: **emitir boleto/nota no Hub → disparar cobrança
pelo WhatsApp do cliente, que é o canal do Ei Risen**. Ver [[integracoes-internas-quem-alimenta-quem]].

## O caso de uso
Hub emite boleto → dispara automático pro cliente pelo WhatsApp (canal do Ei Risen) →
cobrança de atraso (régua) também pelo WhatsApp → tudo aparece no **inbox** do Ei Risen
(no thread do cliente). O Hub NÃO duplica tela de WhatsApp — CONSOME a capability do
Ei Risen pelo Core.

## Autorização (estilo "janela do Google" / OAuth interno)
NÃO digitar login/senha do dono no Hub. Fluxo = igual o "conecta num clique" do MP, só
que interno: Hub → Conectores → "WhatsApp (via Ei Risen)" → Conectar → redireciona pro
Ei Risen → dono loga NA TELA DELE → tela de consentimento ("O Hub (conta Josemac) quer
enviar cobranças/notas pelo seu WhatsApp. Autorizar?") → aprova → Core grava o VÍNCULO
(core_tenant_links + consentimento + escopo). Segurança:
- Opt-in por tenant no Ei Risen (padrão OFF): "permitir apps da frota enviarem pelo meu WhatsApp".
- Escopo: só cobrança/nota — NÃO libera chat livre.
- Revogável + log de auditoria (qual app disparou, pra qual cliente, quando).

## Reconhecimento técnico JÁ FEITO (Ei Risen, repo risencrm/risen-ai-connect, ref qbclqjkvovfriuhshkpw)
- **Envio existe:** `_shared/evolution-client.ts` → `sendTextViaEvolution(cfg,{number,text})` +
  `sendMediaViaEvolution`. Instância por tenant em `whatsapp_providers.config` (instance_name+apikey).
  Base Evolution: `https://wa.crm.risenmidia.com.br`.
- **Envio robusto (com inbox):** `provider-send-message` (cria a messages row, takeover, assinatura)
  — mas exige `conversation_id`.
- **Inbox = achar/criar contato+conversa:** lógica ENTRELAÇADA no `provider-webhook` (handler de
  inbound). NÃO há helper isolado → pra cair no inbox tem que reusar essa lógica (mexe no
  messaging AO VIVO — cuidado, testar no número do Pedro primeiro).
- **Falta segredo:** Ei Risen NÃO tem `BROKER_HMAC_SECRET`. Provisionar (o Core assina com o
  secret da capability; o alvo confere). Template do broker-in = `v1-risenos` do RisenOS
  (HMAC verify + dispatch). Ei Risen (risen-whatsai) tem 5 api_keys mas 0 capabilities
  registradas (só é CALLER hoje, não TARGET).

## Peças a construir (ordem)
1. **Opt-in de segurança** (Ei Risen) — flag por tenant + escopo. Zero risco.
2. **Capability `whatsapp.enviar`** — função `v1-eirisen` (broker-in, confere HMAC, checa opt-in,
   envia via evolution-client) + registrar no Core (system risen-whatsai, target_url, secret) +
   provisionar o BROKER_HMAC_SECRET no Ei Risen. Fica testável mas INERTE (só dispara se chamado).
3. **Inbox + trigger** (v2, sensível) — mensagem cai no thread do cliente (reusa provider-webhook)
   + o Hub dispara na emissão do boleto + a **régua** (cron no Core: D-3/D0/D+3/D+7) via evento
   `core.cobranca.vencida`. Testar no número do Pedro ANTES de qualquer cliente.

## MODELO DE COBRANÇA (fechado + CORRIGIDO com o Pedro)
⚠️ O cliente NUNCA vê o Core. Quem cobra NÃO é o Core — ele MEDE; quem FATURA é o app de ENTRADA.
- **Cliente assina pelo app de ENTRADA** (por onde entrou; ex.: começou pelo Ei Risen/"CRM").
  Esse app é a **casa da cobrança** (fatura/cartão/plano). Única cara que o cliente vê.
- **O Core MEDE** todo consumo por tenant (`core_usage_log`, custo+margem via `core_emissao_precos`)
  — invisível. Relógio de luz, não concessionária.
- **Integrar módulo novo (ex.: RisenOS) → custo PUXA JUNTO** na MESMA fatura do app de entrada.
  Cliente NÃO ganha 2ª cobrança; a conta que ele paga cresce.
- **App de entrada LÊ o consumo do Core** (capability `consumo.resumo`) e cobra pelo próprio meio.
  O Core só informa "tenant X usou Y"; quem emite a fatura é o app.
- **Cross-app do MESMO cliente = 1 conta só, sem cobrança dupla.** Não duplica tela — embute a
  FUNÇÃO (capability) via Core. Core = relógio (mede); app de entrada = concessionária (cobra).
- FALTA construir: a capability `consumo.resumo` no Core + o app de entrada ler e faturar.

## Estado atual da frota (pra contexto do restart)
Conectores externos JÁ propagados: Hub (referência) + RisenOS + Ei Risen (memória
[[conectores-propagado-risenos-eirisen]]). Financeiro do Ei Risen = tela de conciliação
enxuta (7 colunas), E2E entra quando plugar o Extrato do Core. Ver [[extrato-conciliacao-e2e]].
</content>
