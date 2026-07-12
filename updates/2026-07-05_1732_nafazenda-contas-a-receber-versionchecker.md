# nafazenda — Contas a Receber (por cliente) + VersionChecker + fixes granja/plantel

App nafazenda (`~/nafazenda/agrogestao`, Supabase `xggnllvhaehrtqditzft`, deploy git push main → Vercel).

## Contas a Receber — reescrita cliente-cêntrica (`src/pages/AccountsReceivable.tsx`)
- Modelo: `general_transactions` (type=revenue) + `revenue_installments` (id, transaction_id, installment_number, due_date, amount, paid, paid_date). O parcelamento na VENDA já existia (componente `PaymentMethodSection` em NewRevenue; à vista/a prazo 2-6x → grava revenue_installments).
- Construo "recebíveis" = 1 linha por parcela (parceladas) + 1 linha por venda (fiado sem parcela). Carrego pagas e não pagas.
- **Aba Clientes (principal)**: tabela Cliente · Comprou (Σ tudo) · Em aberto (Σ não pago) · Atrasado (vencido não pago), ordenado por em aberto desc. Clica → **statement** (Dialog): resumo + compras com status + **"Adicionar pagamento"** (valor+data, baixa as mais antigas primeiro via `settleItems`; parcelas de uma venda todas pagas → `general_transactions.payment_status='paid'`).
- **Aba Lançamentos (secundária)**: lista linha-a-linha com filtro de status (a receber/atrasadas/recebidas/todas).
- Status: recebido (verde) / atrasado Nd (vermelho) / vence Nd (amarelo) / em dia. Abrange todas as fontes (ovo/eucalipto/geral).
- ⚠️ Dado real: ~169 recebíveis em aberto e TODOS "atrasados" porque venda fiado usa due_date=data da venda (passada). R$403k em aberto — provável backlog/legado; conferir com o Pedro.

## VersionChecker (`src/components/VersionChecker.tsx`, montado no App.tsx)
- Popup "Nova versão disponível → Atualizar" quando o bundle muda no ar. Faz fetch de `/index.html?ts=` (no-store) a cada 2min + no visibilitychange, compara `assets/index-*.js` com o baseline carregado. Botão = `location.reload()`.
- **Ovo-galinha**: só funciona a partir do deploy SEGUINTE ao que o introduziu (o app aberto ainda não tem o checker). Usuário precisa recarregar 1x pra pegá-lo.

## Fixes de granja (mesma sessão)
- **getHousePlantelBreakdown** (poultryEconomics): fonte única do plantel (contagem + entradas − saídas por categoria). InventoryTab e card do Galpão agora batem. Galpão Principal e Frangas tinham sido **excluídos** (soft delete, is_active=false) pelo user "Militão" — reativei. Entrada suspeita de 391 no Galpão Principal (05/07) fica pro Pedro apagar manual.
- Cotações: aba comparativa (Descrição · Último preço sistema · Commodity · Individual) + botão único "Cotar tudo". Commodities (milho/soja/café/boi) via edge fn `cotacoes-commodity` (melhorcambio, cron diária 21h UTC). Supermercado via Inflio. Fubá/metionina/semente etc. NÃO estão no Inflio → EU pesquiso no Google e preencho manual (registrei fubá/metionina/semente).

## Nota operacional
Deploy de edge functions exige `SUPABASE_ACCESS_TOKEN` ao vivo do Bitwarden (secret `397251ce-20b0-423d-b31f-b4780170a76f`, via `bws`; token no Keychain). O CLI linkado às vezes dá 401 → puxar do cofre.
