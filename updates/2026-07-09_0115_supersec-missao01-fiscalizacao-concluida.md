# SuperSec — Missão 01 CONCLUÍDA: Curador Fiscalização vivo e testado

Sequência do update 2026-07-08_2358 (gate de prod): supervisora aplicou migration +
publish + deploy; executora rodou o teste ponta-a-ponta em prod e fechou a missão.

## Prova (doc sintético, depois removido — zero sobras)
Auto de infração PDF (fitz) via uploads-temp → frota leu (fase 1) → triagem assentou
(`desconhecido`, sem assinatura PDF — esperado, nasce via Enquadrador no 1º real) →
classificado `fiscalizacao` → fase 2 → **processed** com raw_data.curador:
tipo "Auto de Infração" · órgão RFB · processo 10855.722334/2026-11 · ciência
2026-07-01 · prazo_dias 30 (LIDO da tabela) · **prazo_defesa 2026-07-31** ·
dias_restantes 22 · tributo IRPJ · valor 1.532.045¢ · resíduo ["exigencia"].
emission_date = ciência. Exatamente o esperado da missão.

## Commits
- backend `28b5f27` (curador + migration + worker-avisos 4ª checagem) — push ok.
- front `1513c9b` (card fisz "ativo" no PipelineVivo) — push main → Vercel.

## ⚠️ Achado pra supervisora (não corrigi — fora do escopo da missão)
Na 1ª tentativa de teste (fora de ordem), a TRIAGEM do movedor rodou DEPOIS do
curador e **reescreveu type ('fiscalizacao'→'desconhecido') e raw_data (perdeu o
bloco curador) de um doc já `processed`**. O "não descataloga" protege `status`,
mas não `type`/`raw_data`. No fluxo natural a triagem vem antes da fase 2, mas a
janela existe (ex.: humano classifica no Revisar enquanto uma triagem retry está
pendente). Sugestão: triagem pular doc com status='processed' (ou type já setado).

## Aprendizados de teste (pro ritual das próximas missões)
1. Tenant vivo é `9bcf5863-…` (PC CONSTRUTORA) — o default do worker.py (`c55fd91e`)
   está morto (banco zerado). 2. Teste sintético: INSERT → esperar fase 1 → esperar
   TRIAGEM assentar → só então UPDATE type (o trigger de fase 2 tem
   `on conflict do nothing` — reclassificar não re-roda fase 2 do mesmo doc).
3. `documents` não tem `mime_type`; obrigatórios: tenant_id, source, original_filename.

➡️ PRÓXIMO: missão 02 (Curador Societário/Empréstimos). Regime de prod pendente de
escolha do Pedro (A = executora autônoma com aprovações; B = supervisora aplica em
lote por missão).
