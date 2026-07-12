# SuperSec — Missão 04 (Motor Calendário/Pendências): código pronto — PROD DA MISSÃO 04

Executora. Missões 01-02 concluídas, 03 dormente (decisão), movedor early-exit
commitado (`d51e382`, deploy ainda pendente — ver update 0230). Missão 04 codada.

## PROD DA MISSÃO 04 + pendência anterior (pra supervisora aplicar, em ordem)
- [ ] `bash scripts/aplicar_migration.sh supabase/migrations/20260709150000_motor_calendario_pendencias.sql`
- [ ] `supabase functions deploy worker-avisos --project-ref abysijyuhvwrczxnwaqg --no-verify-jwt`
- [ ] (da arbitragem, se ainda não foi) `supabase functions deploy worker-2-movedor --project-ref abysijyuhvwrczxnwaqg --no-verify-jwt`
- Depois: executora testa `select calendario_fiscal(...,7,2026)` (DAS 20/07 seg ok,
  FGTS/GPS 20/07, eSocial 15/07, antecipação em vencimento de domingo) + pendencias +
  hoje_resumo, e SÓ ENTÃO faz push do front (commit local `5930772` — card cal +
  2 blocos na página Hoje; sem migration os blocos não renderizam, mas o card mentiria).

## O que foi construído (backend `5b43dc1`)
- RPCs `calendario_fiscal` (regime-aware por unidade: o tenant tem Simples E Presumido!)
  e `pendencias_documentais` (recorrentes × recebidos, régua D-10/7/5/3/1) + helpers
  de dia útil + antecipação por feriado (nacionais-2026 + estaduais da UF do address).
- eSocial dia 15 SEM ajuste (MOS S-1.3); IRPJ/CSLL Presumido trimestral com conferir=true;
  GIA/EFD-ICMS puladas (extinta/varia UF — vereditos 'divergente' da própria tabela).
- hoje_resumo ganhou 'calendario' + 'pendencias_docs' (menor mudança no front).
- worker-avisos: 5ª checagem (D-3 sem guia em tax_guides nem ledger).
