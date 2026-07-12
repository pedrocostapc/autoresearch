# RUNBOOK DO ENQUADRADOR — handoff pra sessão SONNET (12/07 18h15, encerramento Fable)

> O Pedro abriu uma sessão Sonnet dedicada que assume o enquadrador/curador sob demanda.
> Este é o runbook EXATO. Contexto geral: `COORDENACAO-ESTEIRA.md` (você é
> SUPERSEC-AGENTES) + `updates/2026-07-12_1805_supersec-agentes-checkpoint-ensaio-producao.md`.
> Artefatos duráveis copiados pra **`~/.risen-enquadrador/`** (catalogo.json,
> catnames_ensaio.txt, ensaio1/, ensaio2/, todos os enquadramento_r*.APLICADO.json e
> grupos*.json — o scratchpad da sessão antiga era efêmero).

## Segredos (nunca no chat; ler ao vivo)
```bash
export BWS_ACCESS_TOKEN=$(security find-generic-password -s bws-access-token -w)
export SUPABASE_ACCESS_TOKEN=$(bws secret get 397251ce-20b0-423d-b31f-b4780170a76f | jq -r .value)
# WORKER_SECRET: cd ~/Dev/risen/super-secretaria-functions && set -a; source .env.local; set +a
```

## O ciclo do enquadrador (1 rodada)
1. **Preview** (agrupador determinístico; a LLM real dorme — modo preview):
```bash
curl -s -X POST "https://abysijyuhvwrczxnwaqg.supabase.co/functions/v1/worker-enquadrador" \
  -H "x-worker-secret: $WORKER_SECRET" -H "Content-Type: application/json" -d '{}'
```
   → `{grupos: [{tamanho, assinatura[], reps[{id, arquivo}]}]}`.
2. **Classificar — 1 subagente SONNET por grupo** (regra do Pedro; prompts REAIS):
   - system = `~/.risen-enquadrador/ensaio2/system.txt` (é o ENQUADRA_SYS pós-fix B22,
     também em `supabase/functions/_shared/llm_docs.ts`);
   - user = `TIPOS CONHECIDOS: <conteúdo de ~/.risen-enquadrador/catnames_ensaio.txt>`
     + linha em branco + `GRUPO de N documentos parecidos.` + `Arquivos dos
     representantes: <arquivos dos reps separados por " | ">` + `Assinatura de tags
     (palavras comuns a ≥90% deles): <assinatura separada por espaço>`;
   - resposta esperada: `{"doc_type": "<chave EXATA do catálogo ou null>", "confidence": 0..1}`.
3. **Validar** (como a produção): doc_type tem que existir EXATO em
   `~/.risen-enquadrador/catalogo.json` (campo `documento`; pasta/aba vêm de lá);
   `confidence >= 0.75`; null/lixo recusa.
4. **Aplicar** (RPC, via management API):
```bash
echo "select enquadrar_documento('<rep_id>'::uuid, '<documento>', '<pasta_destino>', '<aba_destino|null>', array['tag1','tag2',...]);" \
 | jq -Rs '{query:.}' | curl -s -X POST \
 "https://api.supabase.com/v1/projects/abysijyuhvwrczxnwaqg/database/query" \
 -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" -H "Content-Type: application/json" -d @-
```
   `p_tags` = a assinatura COMPLETA do grupo (fidelidade à produção). Retorna
   `{resweep, requeued, brain_total, inserted_tags}` — `brain_total` é o tamanho do cérebro.
5. **Registrar** a rodada em
   `super-secretaria-functions/docs/esteira/plano-execucao/BUGS-MISSAO-12.md`
   (padrão das rodadas 1-67; commit + push). Bug novo → catalogar B## no quadro
   (último usado: **B24**).

## Regras de decisão que a régua das 67 rodadas consolidou
- Nome de arquivo MENTE; na dúvida entre nome × tags, recusar (<0.75). Texto de doc
  visivelmente de OUTRO documento = B18 (não classificar; anotar).
- DARF só com código lido (8109 PIS · 2172 COFINS · 2089 IRPJ · 2372 CSLL · 0561
  pró-labore/13º). B10 = tipos fora do catálogo (IPTU, cartório, mesma titularidade,
  dist. lucros, contratos CEF...) → recusar e seguir.
- Conferências úteis: fila `select count(*) from documents where status='pending'`;
  rev idem `needs_review`; cérebro `select count(distinct tag)...` em document_tags.

## Estado ao encerrar (12/07 18h15)
- Rodadas 1-67 aplicadas; cérebro **2.311 tags**; fila ~18k (Core acelerou pra ~3.500/h).
- Ensaio de produção ciclo 1 completo: B22/B23/B24 achados → corrigidos → re-ensaio
  limpo (6/6). **Deploy do worker-enquadrador corrigido AGUARDA OK DO PEDRO**:
  `supabase functions deploy worker-enquadrador --project-ref abysijyuhvwrczxnwaqg`.
- Próximos: 2-3 ensaios com ondas maiores → Pedro liga a API paga no super admin.
  Releitura dos ~40 pares B18 pós-fila. Receitas ainda não revisadas: funcionarios,
  nfse, societario, fiscalizacao, admissao, nfe (fonte: bucket `fleet/importers/`).
