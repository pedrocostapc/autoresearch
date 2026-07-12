# Concierge ganhou banco LOCAL (SQLite) — 11/07/2026

**Onde:** `~/Dev/concierge/concierge.db` no Mac Mini M4 (24h ligado, onde roda o
braço do concierge). SQLite = arquivo único, sem servidor, sem chave, custo $0.

## Contexto
O "concierge do Pedro" (leio e-mails das 7 caixas, monto A Pagar/Responder, envio via
Core+braço local, monitoro serviços críticos, cuido da Lara/pensão) evoluiu a ponto de
precisar de tabelas. Decisão do Pedro: **banco local neste Mac**, não Supabase — o app
`financaspedro` (Vercel) é **estático**, então `build_dashboard` lê do `.db` e gera o
HTML já calculado; banco não precisa estar online. Mesmo schema migra pro Supabase se um
dia virar produto multiusuário. (O token de Management do Supabase no cofre Core está
INVÁLIDO — 64-hex, não `sbp_`; se for pro Supabase, gerar PAT novo.)

## Schema (concierge.db)
- `categorias` (Pessoal/Lara/Saúde/Alimentação/Transporte/Casa)
- `despesas_pf` — despesas mensais do Pedro (PF) por categoria, origem dinheiro/pix/cartão
- `transacoes_cartao` — natureza pessoal×negócio + categoria (negócio = anthropic/openai/
  meta-google ads/tráfego/COGS = FORA do PF). A preencher do pipeline da fatura.
- `contas_a_pagar`, `pensao_meta/pagamentos/obrigacoes` (migrados dos JSONs do financaspedro)

## Visão em andamento
`financaspedro` deixa de ser "gastos dos cartões" e vira **"Despesas do Pedro (pessoa
física)" por categoria**, separando o que é gasto pessoal do que é negócio dentro da
fatura do cartão. Fonte da verdade = concierge.db; front continua estático na Vercel.
Backup: git em ~/Dev/concierge + espelho Dropbox.
