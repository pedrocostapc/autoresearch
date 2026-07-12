# FROTA-MONITOR — checkpoint de encerramento (12/07 ~19:00)

Turno encerrado por ordem do Pedro: calibragem validada, esteira autônoma.
Snapshot final: fila 15.382 · claimed 186 · done_1h 1.985 (picos ~2.800-3.450/h)
· error acumulado 2 (antigos; Event-bug zerado e residuais repostos pelo Core).

## Estado das máquinas (worker f8fec884, multi-slot, 1 processo por máquina)

| Máquina | FROTA_THREADS | Como está | Notas |
|---|---|---|---|
| linux-win-3060ti (WSL 18 GB) | **12** (.env, aplicado 18:24) | 1.301 done/30min (5,5× a base), RAM 5/18 folgada | Sobra recurso — dá pra testar 16-20 thr se o Core quiser |
| macbookair-m3 (16 GB) | **6** (.env, aplicado 18:20) | Medição do efeito ficou SUJA (restart + lote pesado) | Reavaliar 6 vs 4 numa janela limpa |
| mac-mini-m1 (16 GB) | default 4 (sem linha no .env) | swap oscilando 15-18,4 GB | Se swap >20 GB: THREADS=3 (Pedro autorizou no pacote) |
| air-risen (8 GB) | default (SEM SSH — chave negada) | Autônomo, produzindo | Calibragem impossível até Pedro instalar chave |
| amd-ryzen5 | — | DESLIGADA desde 08/07 ~01:00 (física) | Aguarda Pedro ligar |

## Como ajustar/reverter FROTA_THREADS
1. `ssh <máquina>` → editar/remover a linha `FROTA_THREADS=N` no `~/ocr-fleet/.env`
   (sem a linha, volta ao default núcleos/2).
2. Reiniciar o worker: Mac = `kill <pid do python -u worker.py>` (launchd renasce);
   Win = `kill <pid>` (systemd renasce; `systemctl restart` exige auth interativa).
3. Custo do restart: os claims em curso viram órfãos (voltam à fila em ~10min pela
   claim function). Janela ideal: quando `claimed` da máquina = 0.
4. Registrar em `fleet_events` (config_change) e anotar vazão antes/depois no quadro.

## Pendências abertas
- **"Processos" m1-2/m3-2/win-2**: NÃO são processos — são SLOTS do worker
  multi-slot reportando sob os nomes antigos (confirmado por censo de ps + done
  por nome). Nenhum clone vivo. Painel/views devem tratá-los como slots.
- **Teto .wslconfig da 3060**: WSL está com memory=18GB (subido de 12 hoje de
  madrugada; backup em `.wslconfig.bak-frota`; máquina tem 24 GB físicos). Com
  12 threads sobrou RAM — só reavaliar se o Core subir muito os threads.
- **Repo autoresearch é PÚBLICO** — reports do quadro estão em commits LOCAIS
  (sem push). Recomendação dada ao Pedro: `gh repo edit --visibility private`.
- **26→24 errors residuais do Event-bug**: Core repôs com attempts=0 ✅ (fechado).
- **Observabilidade da Zeladora** (mantida, útil pra todos): tabelas
  `fleet_events`/`fleet_vitals` + views `v_frota_vazao`/`v_frota_presenca`/
  `v_frota_quedas`; coletor `scripts/frota/zeladora-vitais.sh` (repo
  super-secretaria-functions) — sem cron, era rodado pelo monitor por ciclo.
- **Diário completo do dia**: `docs/esteira/plano-execucao/FROTA-DIARIO.md`
  (super-secretaria-functions) — histórico integral 03:52→19:00.

— FROTA-MONITOR (ex-Zeladora), encerrando 12/07 19:00
