# nafazenda — funções operacionais quebravam por verify_jwt (gateway)

## Sintoma
Tela "Nova Venda de Ovos" (funcionária/operacional) dava "Erro ao carregar dados: Edge Function returned a non-2xx status code". Não carregava clientes, vendedor, nem produtos (dúzia/pente).

## Causa raiz
As funções operacionais usam um **token JWT customizado** (login da funcionária, assinado com JWT_SECRET próprio — não o JWT do Supabase). Se a função tiver `verify_jwt = true` (padrão), o **gateway do Supabase rejeita** o token customizado ANTES de rodar a função: retorna `{"code":"UNAUTHORIZED_INVALID_JWT_FORMAT"}` HTTP 401. Diagnóstico: curl com `Authorization: Bearer dummy` — se vier erro do gateway = verify_jwt ON; se vier o erro DA função ("Token inválido ou expirado") = verify_jwt OFF (correto).

`operational-get-data` e `operational-create-egg-sale` (e deletes/updates/mark-paid) estavam com verify_jwt ON porque **faltavam no `supabase/config.toml`**. `operational-get-permissions`/`-get-houses` estavam OK (no config).

## Fix
- Redeploy de TODAS as operacionais com `--no-verify-jwt`.
- Adicionadas ao `supabase/config.toml` (verify_jwt=false) pra não voltar a quebrar em deploy futuro.
- Regra: TODA função `operational-*` (token customizado) precisa de verify_jwt=false no config.

## Nota
`supabase/config.toml` tem `project_id = "haxiohzchycovlfdjxah"` (projeto ANTIGO/Lovable). Deploys usam `--linked` (projeto certo xggnllvhaehrtqditzft), então funciona, mas o project_id do arquivo está desatualizado.
