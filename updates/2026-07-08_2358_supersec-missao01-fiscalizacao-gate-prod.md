# SuperSec — Missão 01 (Curador Fiscalização): código pronto, TRAVADO no gate de prod

Sessão executora da esteira (plano `docs/esteira/plano-execucao/`, LEIAME seguido).
Missão 01 codada, commitada e pushed (backend `28b5f27`), mas o modo de permissão
da sessão barrou TODA ação em prod (3 negativas do classificador): aplicar migration,
`publish.sh` da frota e deploy de edge function. Parei e perguntei ao Pedro, como
manda o LEIAME.

## O que está pronto (commit 28b5f27)
- `importers/fiscalizacao.py` (curador v1, molde nfse): tipo por palavra (TIF/Auto/
  Despacho/Comunicado/Aviso/Notificação, ordem específico→guarda-chuva), órgão
  (RFB/SEFAZ/Prefeitura), nº processo (padrão federal + rotulado), data de CIÊNCIA
  rotulada; prazo = ciência + dias LIDOS da tabela `tipos-notificacao-fiscal`
  (parse do 1º número de `valor.valor` — busca o grupo inteiro e casa chave em
  Python porque acento na URL quebra o `sb()`); gate = tipo+ciência; exigência do
  fisco = resíduo LLM sempre nomeado. Regexes testados com sintéticos (Auto de
  Infração ciência 01/07 → prazo 31/07 ✓).
- Migration `20260709120000_curador_fiscalizacao.sql`: 5 doc_types → handler
  'fiscalizacao' em extraction_scripts + item 'Notificação/Intimação' (30d,
  Decreto 70.235/72) completando o grupo (tinha 5 chaves, faltava o guarda-chuva
  que a missão pede). Assinaturas PDF NÃO semeadas (nascem via Enquadrador).
- `worker-avisos`: 4ª checagem — docs de fiscalização processed com
  `raw_data.curador.prazo_defesa` ≤7d → email com countdown (dias no fingerprint
  = lembrete diário até resolver). Subject ganhou `· prazos N`.
- Conferido ao vivo antes de codar: grupos `tipos-notificacao-fiscal` e
  `prazos-fiscais-malha-pj` existem (prazos batem com agentes 48/56); trigger
  `enqueue_phase2_on_classify` dispara no UPDATE de documents.type (teste será
  INSERT + UPDATE, não INSERT direto).

## PENDENTE (aguardando OK/execução do Pedro — gate de prod)
- [ ] `bash scripts/aplicar_migration.sh supabase/migrations/20260709120000_curador_fiscalizacao.sql`
- [ ] `cd services/ocr-fleet && set -a; source ../../.env.local; set +a; bash publish.sh`
- [ ] `supabase functions deploy worker-avisos --project-ref abysijyuhvwrczxnwaqg --no-verify-jwt`
- [ ] Teste sintético (PDF fitz "AUTO DE INFRAÇÃO … ciência 01/07/2026 … processo
      10855.722334/2026-11" via uploads-temp + INSERT documents + UPDATE type='fiscalizacao'
      → esperar prazo_defesa=2026-07-31, processed) + limpeza em cadeia.
- [ ] Front: card `fisz` já editado pra "ativo" no working tree do `~/Dev/risen/supersec`
      (PipelineVivo.tsx) — commit/push SÓ depois do curador vivo em prod (painel não mente).
- Deno check do worker-avisos: erro pré-existente em `_shared/supabase.ts:83`
  (tenantId string|undefined) — não é desta mudança; fica anotado.

## Nota pra supervisora
O `deno check` da pasta functions não passa limpo por causa do `_shared/supabase.ts`
(pré-existente). Se quiser, missão futura corrige o tipo.

Missões 02→12: não iniciadas (ordem obrigatória; 01 precisa fechar primeiro).
