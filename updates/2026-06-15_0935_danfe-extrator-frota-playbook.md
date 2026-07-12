# 2026-06-15 — Extrator DANFE em produção + frota ligada + playbook de extração

Para quem não viu a conversa (sessão remote-control com o Pedro, 14–15/06).

## O que foi PRA PRODUÇÃO (deployado + pushado)
- **Extrator DANFE (PDF→ParsedNfe), `worker-agent-1 v58`** no Supabase
  (`abysijyuhvwrczxnwaqg`). `_shared/danfe.ts` `parseDanfePdf(text)` — determinístico,
  ZERO LLM, **100% honesto em 121 pares reais** (NF-e digitais da PC Construtora,
  contra XML via `parseProcNFe`). Ligado no `classify` (DANFE digital sem XML →
  c.nfe → materializeNfe). Verificado de forma independente (não só pelo agente).
- **Frota automática ligada**: migration `20260614130000_frota_auto_enqueue`
  aplicada (trigger `documents→extraction_jobs` + backfill). `reader.ts` ganhou
  `fleetText` (consome o RAW da frota em vez de re-OCRar) e o `worker-agent-1`
  ganhou `loadFleetExtraction` + adia/usa frota/fallback inline. Os 3 worker.py
  (Air/3060/Escritório) agora recebem trabalho automático (pull, termina-1-puxa-outro).
- **functions/main pushado** (origin/main = `820d991`).
- **Front (supersec)**: botão **"Reprocessar todos os filtrados"** em /documentos
  (reenfileira todo o filtro, não só a página/seleção) — deployado no Vercel (READY).
  Foi junto o commit de Produtos/Serviços/Estoque (a48cba3) de sessão paralela.

## O MÉTODO (o ativo) — `docs/extracao-playbook.md`
A NF foi o PILOTO (tinha o gabarito perfeito, o XML). O método generaliza pra todos
os ~52 tipos. Loop de 6 passos: extração grátis → gabarito → compara → Sonnet itera
→ deploy → monitora+auto-cura. **2 trilhas de gabarito**: (A) gêmeo
XML/barcode/OFX = verdade grátis; (B) sem gêmeo → Sonnet LÊ O ARQUIVO e ensina o
grátis (holerite/recibo/comprovante). **Régua por tipo = `catalogo-extracao-schema`,
NÃO os agentes** (agente NF listava ~10 campos; catálogo tem 64; boleto tem 16 quase
todos do barcode = grátis). Detalhe na memória `extracao_playbook_metodo`.

## PLANO combinado (importante)
Os docs no banco hoje são **TESTE**. Depois de construir todos os extratores
(boleto→extrato→nfse→holerite, nessa ordem por volume×gap), o plano é **LIMPAR o
banco e REPROCESSAR TUDO do zero** com os extratores completos, e medir o resultado.
→ Não vale a pena corrigir doc individual agora.

## Aberto / próximos
- **Loop de produção `conferencia` + auto-cura Sonnet** (aprovação 1-clique) ainda
  NÃO construído — é o que monitora qualidade por tipo×layout e conserta sozativo.
- Extratores por tipo (boleto/guia/extrato/nfse/holerite) — a fábrica do playbook.
- Backlog: NFS-e da Risen 300+ em review (54%), guia_imposto 37% review.

## Gotchas registrados
- `agent1.batch=0` NÃO para o pipeline (`settings.ts:21` faz `v>0?v:fallback` → 0
  vira default 25). Pausa real = desabilitar o cron `agent1-drain`.
- Worktrees `../ss-danfe-extractor` e `../ss-frota-fila` já mergeadas em main
  (podem ser removidas com `git worktree remove`).
- Deploy de prod e self-permission são gated pelo harness — o Pedro rodou o
  `functions deploy` e o `db push`; depois criou regra `Bash(supabase:*)` em
  `.claude/settings.local.json` (ele, não a IA).
