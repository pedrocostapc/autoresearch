# CHECKPOINT nafazenda — Despesa por foto (Haiku) + Fornecedores + VersionChecker

**Data:** 2026-07-12 · app: **nafazenda/agrogestao** · Supabase **xggnllvhaehrtqditzft** · Vercel (deploy = push main)
**Pra quem nasce sem memória:** este é o app do Pedro (Fazenda Cachoeira — granja de ovos + eucalipto + milho, Pirapora/Sul de Minas). Stack: Vite+React+TS, shadcn/ui, Tailwind, Supabase (Postgres/Auth/Edge Functions Deno/RLS), React Router. Repo local: `/Users/pedrocosta/nafazenda/agrogestao` (cwd da sessão é o pai `/users/pedrocosta/nafazenda`).

## ✅ NO AR (tudo commitado e pushado; HEAD = 8edc91e)
1. **Despesa por foto** — funcionária/dono tira foto da nota → **Claude Haiku 4.5 (visão)** lê e preenche o lançamento (fornecedor, itens 1-por-linha, valor, data, forma de pgto). IA **ATIVA** (secret `ANTHROPIC_API_KEY` setada no Supabase, chave dedicada teto US$10/mês).
   - Edge fn: `supabase/functions/operational-scan-expense/index.ts` (verify_jwt=false; aceita **os 2 logins**: JWT operacional HMAC OU usuário Supabase autenticado via getUser).
   - Frontend celular (Cida, operacional): `src/pages/OperationalExpense.tsx` — tela de escolha (2 botões grandes **Tirar foto** / **Escolher imagem** + **Digitar manualmente**), lista de itens editável, forma de pgto (À vista/Notinha-fiado/Boleto), calendário shadcn compacto.
   - Frontend desktop/iPad (Militão, login completo): `src/pages/dashboard/NewExpense.tsx` — ordem **Setor → Responsável → depois** o bloco foto/manual (2 botões grandes). Foto NÃO sobrescreve setor/responsável (a pessoa marca). Downscale da imagem no browser antes de enviar.
2. **Nota de compra com Fornecedor** — despesa = cabeçalho `general_transactions` + itens `revenue_items` + **`supplier_id`** (migration aplicada em prod). Fornecedor = `contacts` type `supplier` (CHECK já aceitava). Campo fornecedor no NewExpense, EditExpense e OperationalExpense. Aba **"Por Fornecedor"** em `GeneralExpenses`.
3. **Página Fornecedores** — `src/pages/Suppliers.tsx` (rota `/fornecedores`, menu Cadastros). Lista com total gasto/nº notas/última compra; **editar, desativar, MESCLAR duplicados** (reaponta general_transactions.supplier_id → desativa o dup).
4. **Casamento fuzzy de fornecedor** (anti-duplicata) — `src/lib/supplierMatch.ts` (`normalizeSupplier` + `bestSupplierMatch`, Levenshtein, limiar 0.86, ignora acento/caixa/pontuação/sufixo jurídico). Usado em NewExpense, EditExpense e **inline** na edge fn `operational-create-transaction` (Deno não importa de src → lógica duplicada lá).
5. **VersionChecker** (`src/components/VersionChecker.tsx`) — CORRIGIDO: baseline agora é `__APP_COMMIT__` (commit fixado em BUILD via `vite.config.ts` define, vindo de `VERCEL_GIT_COMMIT_SHA`), comparado com `version.json.commit` publicado. Antes usava a 1ª leitura (já a mais nova) → popup nunca disparava quando o app rodava do cache (Chrome/iPad). `vercel.json` buildCommand agora grava `{id, commit}` no version.json.

## ⏳ PENDÊNCIAS (com dono)
- **[Pedro] Testar no iPad** após recarregar 1x (o VersionChecker novo só passa a valer depois de carregar essa versão uma vez — chicken-and-egg). Confirmar que: (a) foto lê e preenche; (b) fornecedor duplicado com escrita diferente cai no mesmo; (c) popup de versão aparece no próximo deploy.
- **[Claude] Calibrar prompt de leitura** se alguma nota real falhar (prompt está em `operational-scan-expense/index.ts`, const `EXTRACTION_PROMPT`).
- Pendências antigas: milho auto-diário (commodity, frágil); aliases PX Microm/Vitaminas (Pedro preenche com dado do fornecedor).

## 🔑 COMO RETOMAR (comandos)
- **Token Supabase (ao vivo do Bitwarden):**
  `export SUPABASE_ACCESS_TOKEN=$(BWS_ACCESS_TOKEN=$(security find-generic-password -s 'bws-access-token' -w) bws secret get 397251ce-20b0-423d-b31f-b4780170a76f | jq -r '.value')`
- **Chave Anthropic dedicada:** Bitwarden secret ID `4922929e-8a2e-41db-b41a-b47f016f6959` (nome cofre `ANTHROPIC_API_KEY_NAFAZENDA`, projeto `supabase-nafazenda`). Já setada como secret `ANTHROPIC_API_KEY` no Supabase.
- **Deploy edge fn:** `supabase --workdir /Users/pedrocosta/nafazenda/agrogestao functions deploy <fn> --no-verify-jwt`
- **DB query:** `supabase --workdir /Users/pedrocosta/nafazenda/agrogestao db query --linked "SELECT ..."` (cwd é o pai; sempre --workdir).
- **Push:** `git add <arquivos-especificos>` (NUNCA `git add -A` — o `.env` NÃO deve subir), `git commit`, `git stash push -- .env`, `git pull --rebase origin main`, `git push origin main`, `git stash pop`. Deploy Vercel é automático no push.

## ⚠️ ARMADILHAS
- **`.env` do repo aponta pro projeto ANTIGO `haxiohzchycovlfdjxah`** (herança Lovable). A PROD usa env vars do **dashboard da Vercel** (projeto novo), NÃO o `.env` do repo. Por isso o padrão é **sempre stashear o `.env`** e nunca commitar. Meu `.env` LOCAL aponta pro projeto novo `xggnllvhaehrtqditzft` (reconstruído com a anon key pública via `supabase projects api-keys --project-ref xggnllvhaehrtqditzft`). Se precisar rebuildar local, use o .env local (novo projeto).
- **Erro que cometi e corrigi:** commitei o `.env` com `git add -A` (commit 24fdf0b), restaurei o canônico em 8edc91e. Só tinha chaves públicas VITE_ — sem vazamento, nada a rotacionar.
- Edge fns operacionais DEVEM ir com `--no-verify-jwt` (o gateway rejeitaria o JWT custom operacional).

## Commits desta leva
8cb0bbe (tela escolha) → e88e340 (foto desktop) → 807bda0 (versionchecker) → 9e2eb65 (ordem+2botões) → 24fdf0b (fornecedores+fuzzy) → 8edc91e (restaura .env). Tudo pushado.
