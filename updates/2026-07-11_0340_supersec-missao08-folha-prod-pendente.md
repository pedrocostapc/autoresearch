# SuperSec — Missão 08 (Folha/Encargos/eSocial) codada — PROD DA 08

Executora. O maior bloco restante, nos 3 sub-blocos da missão (backend `e36fb35`,
front `c6256d0` pushado — página /folha com lido×calculado + fila eSocial).

## PROD DA 08 (pra supervisora, em ordem)
- [ ] `bash scripts/aplicar_migration.sh supabase/migrations/20260711030000_agente_folha_encargos_esocial.sql`
- [ ] `cd services/ocr-fleet && set -a; source ../../.env.local; set +a; bash publish.sh`
      (_motores.py novo + funcionarios.py v2 pro bucket)
- Depois: executora roda o teste (empregado sintético R$ 3.000 → folha calculada →
  encargos regime-aware → fila eSocial → limpa) e acende folha/enc/esoc.

## O que nasceu
- **08a motor único** (_motores.py): INSS por ANO + IRRF por VIGÊNCIA com
  simplificado×legais (menor vence, Lei 14.663). VALIDADO 5/5 contra as tabelas
  vivas. ⚠️ ACHADO: as faixas INSS 2026 REAIS (SM 1.621, deduções 24,32/111,41/
  198,50) diferem dos números dos agentes 14/35 (que são 2025) — TABELA DECIDE;
  gabarito de teste = tabela, não o prompt. funcionarios.py v2 recalcula e nomeia
  divergência >R$1 (nunca bloqueia o papel).
- **08b**: calcular_folha (payslip_kind='holerite_calc' — o unique da fundação
  tenant×employee×kind×período separa calculada da lida = confronto) +
  calcular_encargos regime-aware (Simples I-III: CPP NO DAS; Presumido: 20%+5,8%
  +RAT médio 2% com pendência rat_fap_conferir_ecac) → tax_guides fgts/gps.
- **08c**: esocial_fila → esocial_events da fundação (S-1200/1210/2200/1299,
  due_date aditivo, requires_human_approval, SEM transmitir).
- Cron dia 1º 06:40. Fila eSocial mora na aba da página /folha (a página
  Obrigações é scaffold; missão 09 decide a casa definitiva — anotado).
