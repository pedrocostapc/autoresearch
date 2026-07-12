# CHECKPOINT GERAL — dia 12/07 (Core/esteira) — GRAVADO ANTES DO LIMITE SEMANAL

**Contexto:** limite semanal do Claude quase batido; Pedro mandou todas as sessões
gravarem estado. Este é o checkpoint do CORE (sessão risencore). O quadro operacional
vivo é `~/Dev/autoresearch/COORDENACAO-ESTEIRA.md` (LER ELE PRIMEIRO ao retomar).

## PAPÉIS (Pedro, 12/07) — vale até segunda ordem
- **CORE** = dono da ESTEIRA SuperSec (fila extraction_jobs, worker.py da frota,
  claim RPC, importers/curadores por delegação do Pedro) + broker + coordenação via quadro.
- **SUPERSEC-AGENTES** = enquadrador/agentes; MODO ENSAIO: Fable orquestra, cada operação
  LLM = 1 subagente SONNET com os prompts REAIS (achar bugs antes de ligar API paga).
- **FROTA-MONITOR** = máquinas (SSH, .env FROTA_THREADS, matar instâncias -2, swap/RAM).

## O QUE FICOU NO AR HOJE (tudo commitado; repo super-secretaria-functions main)
**Worker da frota (bucket fleet, auto-update 60s; último = 793f34e0):**
1. N slots paralelos/máquina (cores/2; env FROTA_THREADS) + supervisor drena antes do re-exec.
2. GATE digital (pymupdf×pdfplumber concordam ≥200 chars → pula docling/markitdown/camelot
   E raster/OCR). Split _DIGITAL_FAST×_DIGITAL_HEAVY. FROTA_GATE=off desliga.
3. PENEIRA text-first+pixels no claim (~100ms): digital processa JÁ; scan→priority 85;
   provável-foto (96×96, top3<0.55)→88; grandão >12pág→95 (só forte). FROTA_PENEIRA=off.
4. GOVERNADOR educado: humano <3min input+máquina>60% → pausa claims; presente+folga →
   ¼ núcleos; ausente → 100%. Knobs FROTA_MODO/FROTA_CAP_HUMANO/FROTA_HUMANO_IDLE_S.
   AnyDesk conta como humano. run-idle-gated.sh APOSENTADO (vira exec run.sh).
5. Thread-safety: raster tmpdir único (matou B18 texto-trocado), locks easyocr/vision/fase2.
6. claim_extraction_job v3: **phase desc** (fase 2 primeiro = completa ciclo) + forte/fraca.
**Importers (Core assumiu com autorização expressa do Pedro):**
- nfe.py: ramo não-fechou SETA needs_review (era o buraco dos 144 presos); XML dispensa DV.
- contas_a_pagar.py: B19 venc re-ancorado na data do doc (nome AA-MM-DD; senão boleto
  histórico ganha venc 2042+); B17 fallback de nome + SELF-CHECK do ledger (falhou →
  'cap_ledger_falhou'); B20 nome com R$ rejeitado; régua NÚCLEO (valor+venc+barcode/pix).
- comprovantes.py: B21 extrai favorecido+banco; SELF-CHECK do INSERT.
- Migrations: campos de ENRIQUECIMENTO viraram nullable (payment_receipts/ledger);
  alias 'Funcionários' (acento) em extraction_scripts; cron renamer-tick.
**worker-renamer-tick** (*/5min): todo processed sem renamed_filename ganha nome padrão
naming.ts ("AAAA-MM-DD - TIPO - CONTRAPARTE - NF n - R$…") e é RENOMEADO NO DRIVE.

## NÚMEROS (último tick ~19h55)
480/h manhã → **~3.500/h**; ETA fila (~18k restantes) ~5h; erros 0; ledger 2→193;
payment_receipts 0→59; renomeados 179; a_processar 240→~100 (maioria pasta Revisar =
correto). needs_review virou exceção genuína (118 'texto_nao_classificado_pdf' = fase
1/tags, assunto separado; resto motivos reais).

## PENDÊNCIAS ABERTAS (retomar por aqui)
1. **Fila zerar** (~5h) → relatório final do teste dos 20k (hipótese: todos catalogados/
   materializados/renomeados). Wakeup agendado nesta sessão p/ ~18h10 local.
2. **bank_statement_lines = 0**: 834 extratos ainda na fase 1 (peneira vai trazê-los);
   conferir curador extratos materializando quando chegarem.
3. Monitor: calibragem FROTA_THREADS por máquina (ordem 6) + matar processo m1-2 +
   teto .wslconfig na 3060 (memória chegou a 94%).
4. Agentes: ensaios Sonnet do enquadrador (rodada 67 liberada); catalogar B## novos.
5. 118 'texto_nao_classificado_pdf' precisam de dono (fase 1/tags — Core).
6. Hub/CRM do dia (contexto separado): canal cobrança = GMAIL (nunca Resend p/ cliente);
   Peça 3 WhatsApp no inbox FEITA (provider enum = 'qr'); boleto Fernando emitido+enviado
   (idemUuid no provider-cora: chave legível vira UUID v5); core_call_log com error_code/
   error_detail (recusa nunca mais fica muda); cofre limpo (key CRM saneada, dupes apagadas).
7. Corpus CRM baixado (~/Dev/risen/corpus-crm, 4.971 arquivos) + gate 3-vias validado
   (57% peça identificável na hora) — insumo do document.read futuro do Core.

## COMO RETOMAR (sessão nova do Core)
1. Ler `~/Dev/autoresearch/COORDENACAO-ESTEIRA.md` (quadro vivo) + este arquivo.
2. Medir: extraction_jobs (pending/done/h/erros), documents por status, ledger/receipts/
   renamed acumulados (queries prontas nos STATUS do quadro).
3. Publicação do worker: `services/ocr-fleet/publish.sh` com SUPABASE_URL+SRK do supersec
   (cofre; SRK do ref abysijyuhvwrczxnwaqg). Máquinas se atualizam sozinhas em 60s.
