# SuperSec — Missão 02 (Societário/Empréstimos): código pronto — PROD DA MISSÃO 02

Executora da esteira. Missão 01 concluída e testada (update 0115). Missão 02 codada,
testada com sb falso (4 cenários) e commitada (`9a8a027`, push ok). Regime B em vigor:
supervisora aplica o prod.

## PROD DA MISSÃO 02 (pra supervisora aplicar)
- [ ] `bash scripts/aplicar_migration.sh supabase/migrations/20260709130000_curador_societario.sql`
      (rotas 'Societário','societario','emprestimo','Empréstimos','contrato' → handler societario)
- [ ] `cd services/ocr-fleet && set -a; source ../../.env.local; set +a; bash publish.sh`
      (sobe importers/societario.py pro bucket fleet — máquinas hot-reload ~60s)
- Depois disso a executora roda o teste sintético (contrato de empréstimo 12×R$1.100,
  1º venc 10/08/2026 → 12 payables no ledger) e fecha a missão (card `soc` + bastão).

## O que o curador faz (commit 9a8a027)
- Ato societário: tipo (abertura/alteração/distrato) + NIRE/Junta + data; CESSÃO DE
  COTAS → bloco informativo {ganho_capital, darf_4600_estimado 15%, itcmd_uf+alíquota
  da tabela itcmd-aliquotas-uf (UF do address da unidade)} com pendência nomeada
  `darf_itcmd_conferir_contador` — não lança guia sozinho.
- Empréstimo: principal/n/parcela/1º venc/taxa; gabarito parcela×n ≥ principal;
  Price confere quando taxa impressa (divergência = resíduo `price_divergente`, não
  bloqueia); materializa 1 ledger payable por parcela (delete-by-source antes),
  description "Empréstimo <banco> parcela k/n", vencimentos mensais dia clampado.
- Fontes lidas: 52·53·54·19. Sem assinatura PDF semeada (Enquadrador no 1º real).
