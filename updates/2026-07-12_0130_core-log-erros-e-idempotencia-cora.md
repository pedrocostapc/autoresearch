# Core: log de saída com MOTIVO + veredito da idempotência Cora (12/07 ~01h30)

**Contexto:** boleto do aluguel (Hub) recusado 2 dias seguidos com "Cora recusou a
emissão do boleto" sem motivo. Sessão do Hub diagnosticou; sessão do Core aplicou.

## O que o Core aplicou (prod, migration+deploy+commit a2d80e3 em feat/core-broker-fundacao)
1. **`core_call_log` ganhou `error_code` (text) + `error_detail` (jsonb).** O v1-call
   agora detecta erro DE NEGÓCIO do provider (HTTP 200 + `{error}` no envelope — o
   padrão "não mede/não cobra") e loga `status='provider_error'` + motivo completo
   (inclui `cora_status` e `cora_body`). Antes recusa aparecia como `ok`.
2. **v1-email e v1-notify** (saídas que NÃO passam pelo v1-call) agora gravam no
   MESMO livro via `_shared/call-log.ts` (`email.enviar` / `notify.send`; systems
   `google` e `resend` registrados, billing_exempt). WhatsApp já passava pelo
   v1-call (`whatsapp.enviar` → risen-whatsai) = coberto. NFS-e (focus/govnfse) idem.
   → **TODA saída da frota (boleto, nota, e-mail, whatsapp) rastreável com êxito/motivo.**
3. **risen-core-proxy do Hub:** Core ASSUMIU o patch da sessão do Hub (repassa
   `error.details` com cora_status+cora_body pro app) — deployado no projeto do Hub
   e commitado (ba417e8 na main do pixel-perfect-replica). A sessão do Hub NÃO
   precisa reverter nada desse arquivo.
4. ⚠️ Gotcha corrigido: deploy de v1-email/v1-notify sem entrada no config.toml
   resetou `verify_jwt` pro default true (~10min de canal quebrado). Agora
   persistido `verify_jwt=false` no config.toml dos dois. **Regra: função nova do
   broker chamada por API key SEMPRE ganha entrada no config.toml.**

## Veredito da idempotência (pergunta da sessão do Hub)
- **O Core NÃO cacheia nada** (verificado no código do v1-call: zero cache).
- O cache de 24h é **DA CORA** (`Idempotency-Key` obrigatório em POST; ela replaya
  a resposta gravada — ERRO INCLUSO). Recusa de ontem re-servida hoje = comportamento
  da Cora, não do Core.
- **Fix certo é o do Hub:** chave de idempotência inclui o vencimento
  (`alug-{id}-{due_date}`) → payload novo = chave nova = chamada viva na Cora.
  Re-clique com a MESMA data continua idempotente. **Com esse fix o boleto do
  Fernando destrava HOJE** (não precisa esperar o cache expirar).
- Sessão do Hub: luz verde pra aplicar rental-boleto.ts + commitar; o proxy já é
  do Core (não reverter).

## Regressão feita
`emitir_boleto` sem args → `provider_error`+motivo no log; envelope pro app
inalterado; `listar_boletos` ok; `email.status` ok (financeiro@ conectado) e não
suja o log (só SAÍDAS logam).

## ADENDO (~01h45) — o motivo REAL, revelado pelo log novo na 1ª recusa
`cora_body`: **"The Idempotency-Key|x-idempotency-id header must be a valid UUID."**
NÃO era data no passado, NÃO era cache/replay (os dois diagnósticos anteriores caíram):
a chave legível do Hub (`alug-{id}`) era rejeitada NO HEADER, antes da Cora olhar o
payload. **Fix aplicado no Core** (commit 8a7a766, v1-provider-cora deployado):
`idemUuid()` — chave não-UUID vira **UUID v5 determinístico** (mesma string → mesmo
UUID → re-clique idempotente); UUID real passa reto. Vale pros 4 pontos (boleto, pix,
stage, webhook). **Nenhum app precisa mudar**; a chave com data do Hub segue
recomendada (determinismo por vencimento). Boleto do Fernando: é só reemitir.
