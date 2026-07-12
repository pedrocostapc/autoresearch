# nafazenda — Suprimentos, estoque em 2, cotações Inflio, fix dos galpões

App **nafazenda** (agrogestão da suíte). Supabase ref `xggnllvhaehrtqditzft`, domínio nafazenda.app.

## ⚠️ Correção ao frota/nafazenda.md e ao mapa
- O repo **ESTÁ clonado nesta máquina**: `~/nafazenda/agrogestao` (git remote `github.com/pedrocostapc/agrogestao`, branch `main`). Não é "não clonado".
- **`supabase db query --linked` FUNCIONA** desta pasta (o CLI abre o projeto xggnllvhaehrtqditzft; não deu 403). O "PAT 403" do doc é de outra conta/PAT — mas o CLI linkado local resolve. Deploy = **git push main → Vercel** (auto). Edge functions = `supabase functions deploy <fn> --no-verify-jwt`.
- Obs: rodar supabase daqui exige cwd = `~/nafazenda/agrogestao` (ou `--workdir`), senão dá "Cannot find project ref".

## O que entrou nesta janela (tudo no ar)
- **Seção Suprimentos** (`/suprimentos`): abas Produtos · Estoque · Ração · Cotações. Menu lateral reordenado (Suprimentos subiu pro grupo Gestão; Produtos saiu de Cadastros). Aba ativa em verde sólido (padrão dos filtros de Despesas).
- **Estoque separado em 2:**
  - *Ração → Estoque*: só ingredientes da ração (`ingredient_stock_movements`).
  - *Suprimentos → Estoque* (`FarmStockTab`): estoque **geral da fazenda** = produtos com flag `products.track_stock` + ingredientes de ração; valor unit/total + total geral. Nova tabela **`product_stock_movements`** (+RLS `has_farm_access(auth.uid(),farm_id)`), helper `src/utils/productStock.ts`. Compra (despesa) de produto track_stock dá **entrada automática**. Botão verde "Ajuste de estoque" (popup).
- **Cotações por classificação** (Insumos/Consumo/…): botão "Cotar" por produto → função **`pesquisar-precos` reescrita pra raspar o Inflio** (sitemap `/preco/*` + meta `de R$ X a R$ Y`, supermercado BH, **grátis, sem chave**); agro (fosfato etc.) via **deep-link** Mercado Livre/MF Rural (ML bloqueia scraping 403) + manual. Alias `products.search_alias` ("fosfato"→"fosfato bicálcico").
- **Fix dos galpões (Granja):** o tipo agora vem da **ração** (`feed_formulas.lifecycle_stage`: laying=Postura, rearing=Recria) em vez de `chicken_type` (que era sempre 'laying' → tudo "Postura"). Card mostra **plantel contado** (`getHouseBirdCount` = contagem+entradas−saídas) + capacidade; "Registrar Produção" só em postura. Rótulos: "Capacidade do galpão" (tamanho) × "Aves no galpão hoje (plantel)" (contado, read-only). Frangas estava sem ração → atribuí a de Franga.
- **Milho** lançado no estoque como ajuste manual (600 kg = 10 sacas × R$57 = R$0,95/kg), sem virar despesa.

## Colunas/tabelas novas no schema (xggnllvhaehrtqditzft)
`products.track_stock` (bool), `products.search_alias` (text); tabelas `product_stock_movements`, `price_quotes`, `ingredient_stock_movements`; `feed_ingredients.price_per_unit` numeric(14,6).

## Pendências
- Frangas com `capacity=1` (dado de tamanho errado — o Pedro corrige).
- **PX Microm / PX Vitaminas**: núcleos/premix não têm preço público → cotação de fornecedor (Produmix/Cogran-MG). Sem alias ainda.
- Preço da Metionina/PX aparece ~R$0 na fórmula Postura (parece subvalorizado — conferir unidade/preço).
- Milho: cotação commodity "auto por dia" não construída (frágil). Valoração de produtos gerais usa `default_price`.
- Secrets: uso o CLI linkado; se cair o token, puxar `SUPABASE_ACCESS_TOKEN` ao vivo do Bitwarden (secret `397251ce-20b0-423d-b31f-b4780170a76f`).
