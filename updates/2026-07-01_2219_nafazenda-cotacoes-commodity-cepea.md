# nafazenda — Cotações: commodity (saca/arroba) separado de supermercado + Cotar agora

Continuação do bloco de Cotações (app nafazenda, Supabase xggnllvhaehrtqditzft).

## O que entrou
- **`products.commodity_key`** (text): Milho='milho', Farelo de Soja='soja', Carvão='carvao'. (Não há produto "Café".)
- Commodity é cotado por **saca/arroba via índice**, NÃO supermercado. `price_quotes.item_type` agora aceita **'produto'** (era o bug do "Cotar agora": CHECK só tinha commodity/insumo).
- **Edge fn `cotacoes-commodity`** (deployada, --no-verify-jwt): raspa **melhorcambio.com/<slug>-hoje** (`<input id="comercial" value="X">`) pra **milho/soja/café/boi** → grava em price_quotes (unit saca60/arroba, source 'melhorcambio', region nacional). Aceita `{farm_id}` (app) ou sem (todas as fazendas com commodity). Carvão NÃO tem índice público → fica manual.
- **Cron diária** `commodities-diaria` (pg_cron+pg_net habilitados) `0 21 * * *` (18h BRT) → net.http_post na função.
- **`pesquisar-precos`** ganhou **modo lote** `{queries:[{key,term}]}` (sitemap 1x, teto 60 páginas, match por palavra inteira — "sal" não pega "salsicha").
- **QuotesTab**: botão **"Cotar agora"** (supermercado, lote, ignora commodity) + botão **"Commodities"** (chama cotacoes-commodity). Produto commodity mostra a cotação de índice.

## Valores de hoje (01/07): milho R$64,02 · soja R$131,07/sc · café R$1.665,59/sc · boi R$335,30/@.

## Notas
- Deploy de functions exigiu `SUPABASE_ACCESS_TOKEN` **ao vivo do Bitwarden** (o do CLI dava 401). Fluxo novo OK.
- Cotação de commodity = **referência de mercado**; NÃO é o custo usado na ração/estoque (milho na ração usa price_per_unit R$0,95/kg configurado). São coisas separadas de propósito.
