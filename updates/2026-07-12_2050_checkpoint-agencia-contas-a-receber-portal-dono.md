# CHECKPOINT agencia/Hub — Contas a Receber (p71/p72) + Portal do Dono v3

> Pra uma sessão que nasce SEM memória: repo `~/Dev/risen/risenagencia/pixel-perfect-replica`
> (app "Hub Mídia OOH", briefing em `~/.claude/frota/agencia.md`, contrato crítico em
> `docs/CORE-CONTRATO.md` — LEIA antes de mexer em integração). Supabase ref
> `yfzljfvqlnxqaqtdrntc`. Deploy = push na main (Vercel). TUDO DESTA SESSÃO ESTÁ
> NO AR E PUSHADO (último commit `13b829c`); working tree limpo; nada pela metade.

## O que foi feito hoje à tarde (tudo em prod)
1. **p71** (`supabase/migrations/20260712250000_*.sql`, commit 5aada3a): Contas a
   Receber = cobrança que EXISTE. Receivable só nasce no dia de emissão do
   contrato (`boleto_emit_day`, padrão 25) — reverteu o "nasce com a mensalidade"
   da p70. Baixa do legado pré-sistema (3 mensalidades pagas no vencimento, recibo
   carimbado '(histórico — não enviado)' pra NÃO disparar e-mail, repasse marcado).
   5 receivables draft de 05/08 apagados.
2. **Robô `rent-boletos-monthly`** (deployado 2×): no dia de emissão, contrato
   depósito/externa agora CRIA o receivable draft ("Aguardando pagamento") em vez
   de ser pulado; janela de candidatos 20d→60d (cobre vencimento_no_mes p69);
   grava `receivables.boleto_id` ao emitir.
3. **p72** (commit cc313f0): fluxos de aluguel esqueciam `receivables.boleto_id`
   → linha "Emitido" reoferecia "emitir boleto" (risco de duplicar na Cora).
   Corrigido em `src/lib/api/rental-boleto.ts` + robô + backfill em prod + tela
   endurecida (botão some com status emitted).
4. **ReceivablesPage** (commit 2ac1291): cards mensais (mês anterior/atual/
   seguinte) com Total/Recebido/A receber; card de mês vizinho só aparece com
   movimento; filtro por origem (Aluguéis/Outdoor/Instagram/Gráfica/PI); chips
   de mês+origem+status numa linha; linha PAGA conta no mês do paid_at.
5. **Mensalidades (Aluguéis)** (commit ea311db): "Pendentes" exige receivable
   (cobrança gerada); futuras ficam no chip novo "Programadas".
6. **Portal do Dono v3** (commit 13b829c): mobile-first iPhone 15+.
   `src/pages/portal/PortalOwnerDashboard.tsx`: banner EM DIA/atrasado, card
   "Seu investimento" (investido → virou = imóveis hoje + aluguéis, +%), card
   por imóvel com a mesma história + atalho `?imovel=CODE`.
   `src/pages/portal/PortalOwnerHistory.tsx`: filtro por imóvel, mês por setas,
   resumo Recebido/Líquido/A receber, cards, histórico clicável, PDF mantido.
   Sem mudança de backend (RPCs portal_owner_* p66/p67 já davam tudo).

Detalhe fino no update irmão: `2026-07-12_1720_agencia-p71-contas-a-receber-cobranca-que-existe.md`.

## Como aplicar SQL/migrations neste projeto (IMPORTANTE)
- `supabase_migrations.schema_migrations` NÃO EXISTE → `supabase db push` não serve.
- Caminho que funciona: Management API com PAT `SUPABASE_ACCESS_TOKEN` (Bitwarden,
  projeto **risencore** `64c6f019-...`), token do bws no Keychain (`bws-access-token`):
  `jq -Rs '{query:.}' < arquivo.sql | curl -X POST
  https://api.supabase.com/v1/projects/yfzljfvqlnxqaqtdrntc/database/query
  -H "Authorization: Bearer $TOKEN"` (curl, NÃO urllib — Cloudflare 1010 bloqueia python).
- Edge deploy: `SUPABASE_ACCESS_TOKEN=... supabase functions deploy <fn>
  --no-verify-jwt --project-ref yfzljfvqlnxqaqtdrntc`.

## Pendências (com dono)
- **Pedro**: rotacionar/corrigir o secret `SUPABASE_DB_URL` do projeto Bitwarden
  `supabase-agencia` — o valor não é URL nem senha do banco (hex 64, não autentica)
  e VAZOU num erro de terminal na sessão de 12/07. Avisado no chat.
- **Pedro**: validar o Portal do Dono v3 no iPhone (Aluguéis → Portal → Ver portal
  em modo mobile, ou portal real). Ajustes finos de layout sob demanda.
- **Qualquer sessão**: 78 mensalidades históricas (backfill p32) pagas sem
  `owner_transferred_at` → podem poluir "Repasses pendentes" no dashboard de
  Aluguéis. Pedro sabe; baixa em massa só se ele pedir.
- **Observar dia 25/07**: primeira rodada do robô com a regra nova — deve abrir
  cobranças de agosto (boleto Cora p/ contratos de boleto; draft p/ depósito/
  externa) e elas aparecem no card/chip de agosto. Se não aparecer, olhar logs da
  edge rent-boletos-monthly.
- Recibos "pendentes (sai em minutos)" dos 4 pagamentos de 05/07 marcados pagos
  em 12/07: cron de 10min devia ter enviado — se continuarem pendentes, investigar
  edge send-rent-receipt.

## Como retomar
1. Ler `~/.claude/frota/agencia.md` + `docs/CORE-CONTRATO.md` + este update.
2. Conferir tela: hubmidiaooh.app → Financeiro → Contas a Receber (cards por mês,
   chips) e Aluguéis → Mensalidades (Pendentes/Programadas).
3. Mapa completo do sistema (todas as ~60 páginas) foi levantado em 12/07 — se
   precisar de novo, 5 agentes Explore por módulo resolvem em ~3 min.
