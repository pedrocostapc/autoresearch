# agencia (Hub Mídia OOH) — Faturas (razão) + conciliação retroativa + emissão parcelada

**Sessão:** 2026-07-02 · **Repo:** `~/Dev/risen/risenagencia/pixel-perfect-replica` · main `8530351` (push = deploy Vercel).

## O que entrou
1. **Razão do Hub — FATURA** (novo conceito): 1 fatura = 1 NFS-e + N parcelas (boletos Cora),
   amarrados desde o nascimento. Numero interno `FAT-ANO-NNNN` (contador por tenant/ano, trigger).
   Status financeiro **derivado** das parcelas na view `v_faturas_status`:
   aberta / parcial (x/y) / quitada / vencida. Migration: `supabase/migrations/20260702000000_p31_faturas.sql`.
2. **Emissão parcelada**: EmitirServicoDialog ganhou seletor 1..12x; `emitirServico` divide
   centavos exatos (resto na 1ª), vencimentos mensais, idempotência por parcela
   (`rcv-<id>-p<n>`), 1 e-mail com todos os PDFs. Fatura criada junto (fail-safe).
3. **Página Financeiro → Faturas** (`/app/:slug/faturas`): lista com parcelas expandíveis,
   KPIs, sync de baixa **determinístico** (parcela aponta boleto Cora por `cora_invoice_id`;
   Cora diz PAID → baixa `matched_by='regra'`).
4. **Conciliação retroativa** (`/faturas/conciliacao`): casa notas gov.br × boletos Cora
   (regex `/NF\s*(\d+)/i` na descrição) e pagamento × extrato (instante ao segundo + valor +
   documento; fallback único-do-dia). **Regra propõe, humano confirma** — resíduo listado,
   nada de baixa por palpite. Lógica pura em `src/lib/api/conciliacao.ts` (19 testes vitest).
5. **Notas Fiscais**: coluna **Financeiro** ao lado do fiscal (dois status coexistem);
   nota sem fatura mostra "sem fatura" apontando pra conciliação.

## ✅ Migration p31 APLICADA em prod (Pedro validou e autorizou, 2026-07-02 ~01h)
Confirmado no catálogo: tabelas `faturas`/`fatura_parcelas`/`fatura_counters`, view
`v_faturas_status`, triggers (numeração + updated_at) e policies RLS — tudo no ar.
Insert exercitado em transação descartada (trigger/FKs OK); banco segue com 0 faturas.
**Próximo passo humano:** abrir **Faturas → Conciliar histórico** e confirmar as
propostas (popula o histórico das ~110 notas).

## Decisões de arquitetura (pra frota)
- Core segue stateless: razão/vínculo/status/conciliação = estado do Hub (Supabase próprio).
- "Detectar pagamento = Core; decidir que quita recebível = Hub" — baixa automática SÓ
  quando o elo é por ID (mesmo boleto); casamento por texto/heurística sempre passa por humano.
