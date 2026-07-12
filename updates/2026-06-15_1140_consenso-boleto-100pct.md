# 2026-06-15 — Orquestrador de Consenso: fundação de extração + bench 93/93 (100%)

## O que foi feito

Branch `feat/consensus-orchestrator` no worktree `ss-consensus`.
Commit: `66029d2`

### Arquivos entregues

1. **`supabase/functions/_shared/consensus.ts`** — núcleo genérico reutilizável
   - `runConsensus<T>(reads, specs, opts)`: N leituras × M campos → voto por campo
   - `FieldSpec<T>`: parser plugável + validador DV + tiebreakOrder + serializer
   - Auto-validação DV VENCE o voto (1 engine DV-OK > 3 sem DV — verdade matemática)
   - `sonnetTiebreak`: último recurso via anthropic.ts (cota Max, grátis)
   - Utilitários: `onlyDigits`, `parseBRCents`, `parseBRDate`, `validCNPJ`, `validCPF`

2. **`supabase/functions/_shared/consensus_boleto.ts`** — plug boleto bancário
   - 4 engines: `pymupdf` (texto) + `extract` (/extract pdfplumber) + `ocr` (Tesseract+Paddle) + `barcode` (pyzbar 44-díg)
   - Validadores determinísticos: dvMod10 (campos 1-3) + dvMod11 (barcode geral)
   - `runBoletoCensus(reads)` → `BoletoConsensusResult` (confiança por campo)
   - `toBoletoRawData(result, n)` → shape compatível com `raw_data` existente
   - `boletoCensusToRaw(reads)` → all-in-one

3. **`scripts/consensus-bench/bench_boleto.py`** — prova nos boletos reais
   - Tenant Risen Mídia (c55fd91e), 100 boletos do banco

### Placar final (100 boletos)

| Categoria | Quantidade |
|-----------|-----------|
| GPS/DARF (fora escopo, linha 8x díg) | 3 |
| Misclassificados (Pix, cheque, GRF) | 4 |
| Boletos bancários REAIS | **93** |

| Métrica | Single-engine (pymupdf) | Consenso |
|---------|------------------------|---------|
| DL DV-válida | 83/93 = **89.2%** | 93/93 = **100%** ✅ |
| Lift | — | +10 boletos scanned |

**Onde cada engine ajudou:**
- `extract` (pdfplumber): fechou 5 boletos que pymupdf perdia
- `ocr` (Tesseract+Paddle): fechou 3 boletos scan ruim
- `barcode` (pyzbar): DV-validou 7 boletos pelo código de barras físico

**deno check**: limpo nos dois módulos (`consensus.ts` + `consensus_boleto.ts`).

### O que falta para plugar outros tipos

1. **Holerite/folha**: parsers de CPF/matrícula/valor/competência → `FieldSpec[]` + validador CPF
2. **NF-e/DANFE**: chave-44 (mod11 própria), CNPJ (validCNPJ já existe no consensus.ts), valor
3. **NFS-e municipal**: muito variado — provavelmente Sonnet tiebreak como fallback primário
4. **Arrecadação (GPS/DARF/DAS)**: layout de 48 díg diferente → spec própria (mod10 por segmento)
5. **Banco**: `document_consensus` table para gravar votos por campo (hoje só `document_extractions`)
6. **Worker**: integrar `boletoCensusToRaw` no pipeline do worker.py após run_panel()
