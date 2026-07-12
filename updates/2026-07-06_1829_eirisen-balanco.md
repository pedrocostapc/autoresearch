# Ei Risen (eirisen) — balanço: passado, presente, futuro

App: CRM/atendimento WhatsApp. Repo `risen-ai-connect`/`saas-erp-whats`. Front na Vercel
(push main → deploy), backend Supabase `qbclqjkvovfriuhshkpw`, iOS App Store 6772821195.
Foco desta janela (02–06/07): **publicação iOS + catálogo IAP**.

## PASSADO (últimos dias)
- **iOS 2.0.3 NO AR** (READY_FOR_SALE 03/07): features web "dono escolhe telas por
  funcionário (papéis) + área Financeiro". Aprovada sem rejeição em ~17h.
- **iOS 2.0.4 EM REVIEW** (submetida 06/07 01:24): fix do login Google que sumiu no app
  + fixes de avisos (página que quebrava por `cn` não importado + display por vendedor,
  esses vieram de sessões paralelas).
- **Publicação iOS 100% HEADLESS provada** — `xcodebuild archive` (cloud signing via
  `-allowProvisioningUpdates` + chave `.p8` QTG8RWCLX7) → `-exportArchive destination:upload`
  → criar versão + whatsNew + anexar build + reviewSubmissions + submit, tudo via ASC API.
  **Nunca mais precisa abrir o Xcode pra publicar.** Recipe no `frota/eirisen.md`.
- **Catálogo IAP construído na Apple via API**: 5 recargas consumíveis
  (`eirisen.credito.5000..50000`, R$50–500, valor cheio SEM bônus) + 12 add-ons de
  assinatura (grupos "Usuários adicionais" `eirisen.seat.1..6` R$9,90–59,90 e "Números
  adicionais" `eirisen.instance.1..6` R$49,90–299,90). Tudo com preço/localização/BRA.

## O QUE APRENDEU
- **Numeração de versão iOS:** "1.05"=[1,5]; a próxima sempre > a última (1.0.6 seria rejeitado).
- **Assinatura no ASC:** criar sub = `POST /v1/subscriptions` (não /v2); PREÇO exige
  `attributes:{startDate:null,preserveCurrentPrice:false}` E só pega ~1min DEPOIS de criar
  (409 se imediato → passe de preço separado). Consumível cria em `POST /v2/inAppPurchases`.
- **Apple NÃO faz quantidade** em assinatura no varejo → add-ons de seat/instância viram
  tiers fixos (+1..+6 como produtos separados), cada tipo em grupo próprio pra empilhar.
- **Bônus de recarga é WEB/Stripe só** — no iOS credita valor cheio (a Apple já leva 30%).
- **MISSING_METADATA das assinaturas = review screenshot** (suporte Apple, caso 102906529582):
  o print não pode ser igual ao ícone nem a screenshot da ficha; tem que ser o paywall real.
- **403 `REQUIRED_AGREEMENTS_MISSING_OR_EXPIRED`** no ASC API = contrato pendente na conta
  Apple (Agreements, Tax, and Banking), NÃO é a chave. Pedro aceita e volta. Aconteceu 06/07.

## O QUE ERROU / BUGS
- **REGRESSÃO que eu causei:** buildei a 2.0.3 com o `.env` LOCAL sem `VITE_GOOGLE_IOS_CLIENT_ID`
  (config PÚBLICA que sumiu do working tree — outra sessão apagou 2 linhas). Resultado: botão
  "Entrar com Google" sumiu no iOS 2.0.3. **Corrigido na 2.0.4** (restaurei o .env da origin/main,
  confirmei o client no bundle). **Aprendizado: conferir `.env` local vs origin/main ANTES de
  buildar** — o working tree diverge por sessões paralelas (bug recorrente potencial).
- **AINDA ESPREITA:** as 5 recargas consumíveis seguem MISSING_METADATA por motivo não-claro
  (consumível não exige print — os antigos estão APPROVED sem; availability foi criada mas o
  estado não recomputou). Precisa escavar.
- **Base subs travadas:** 6 planos base + testes em MISSING_METADATA por print inválido (Pedro
  trocou por imagem que a Apple rejeita). Fix = subir paywall único e válido nas 18 subs.

## PRESENTE
- **2.0.3:** no ar. **2.0.4:** em review (WAITING_FOR_REVIEW), monitorando com cadência
  escalonada (2h até 17h, 1h depois — janela provável ~17h de review).
- **Catálogo IAP:** todos os 17 produtos CRIADOS na Apple, mas MISSING_METADATA. Travado em:
  (a) prints de paywall das 18 assinaturas (Pedro, no device), (b) CÓDIGO não wirado
  (`appleIap.ts` + `apple-iap-validate` não conhecem os 17 novos; add-ons escondidos no iOS
  de propósito). Consumíveis novos não precisam de print mas seguem travados (item acima).
- **Web (Vercel):** intacta — nada disso a afetou (o Google no browser sempre aparece).

## FUTURO
- **Imediato:** aprovação da 2.0.4 (monitorando).
- **Próximo passo concreto:** wirar os 17 produtos IAP no código (`appleIap.ts` +
  `CREDIT_CENTS_BY_PRODUCT`/handler de add-on na `apple-iap-validate` + des-esconder add-ons
  no iOS) + Pedro capturar os prints → versão nova com catálogo completo.
- **Aberto pro Pedro:** os 18 prints de paywall (pergunta pendente à Apple se dá pra reusar
  1 print); investigar as 5 recargas travadas; responder o caso 102906529582 se a Apple pedir.
- **Rumo da frota:** eirisen é o ÚLTIMO conector do Core a fazer (ver core-balanco 06/07) —
  ainda não começou; hoje o foco foi App Store, não integração Core.

Chave `.p8` local (recipe/IDs no `frota/eirisen.md`); nenhum valor de secret aqui.

---
## ATUALIZAÇÃO 2026-07-09
- **2.0.4 APROVADA E NO AR** (READY_FOR_SALE) — fix do login Google + avisos live.
  Review levou ~2-3 dias (o bloqueio do contrato Apple de 06/07 e o fim de semana esticaram).
  Duas versões publicadas headless na semana (2.0.3 + 2.0.4).
- Segue igual: catálogo IAP (17 produtos) ainda MISSING_METADATA — falta prints das 18 subs
  (Pedro) + wirar no código. É a próxima frente do iOS quando o Pedro quiser.
