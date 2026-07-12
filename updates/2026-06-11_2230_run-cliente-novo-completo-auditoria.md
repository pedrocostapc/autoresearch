# Run cliente-novo COMPLETO (4.649/4.649) + auditoria + 2 fixes de pipeline

Sessão: backend super-secretaria-functions (continuação da maratona do reprocesso).

## O que aconteceu

**O reprocesso clean-room zerou: 4.649/4.649 docs, DLQ 0.** O rabo de ~39 docs
que ficou horas travado tinha causa dupla, agora consertada:

1. **`WORKER_RESOURCE_LIMIT` (silencioso)**: edge function morre por
   memória/CPU do isolate (~256MB) com vários PDFs multi-MB + base64
   concorrentes. Logs só mostram "shutdown"; jobs viram órfãos e ciclam
   claim→órfão→reclaim pra sempre. Mitigação: `agent1.batch=4`,
   `agent1.concurrency=2` no agent_settings (NÃO voltar pra 25/6 às cegas).
2. **Peso por tamanho**: 37 boletos/guias escaneados de 9-11MB estavam com
   `needs_ocr` NULL → priority 50 → pista leve sem OCR. Migration
   `20260611100000`: desconhecido >4MB nasce pesado (90); worker manda
   desconhecido-grande DIRETO pro OCR (pula pilha layout/extract/barcode
   de ~240s). Commit `d4e549c` (main local).

## Auditoria do cliente-novo (pós-run)

- **Cadastros limpos**: 10 fornecedores + 80 clientes, 100% com CNPJ/CPF,
  ~95% com telefone/email (BrasilAPI). Própria empresa NÃO virou
  fornecedor/cliente. Zero duplicatas no ledger (doc+método).
- **Ledger**: payable 1.202 pagas + 91 abertas; receivable 615 pagas +
  1.117 abertas (receivable aberto alto = cobranças emitidas sem
  comprovante de recebimento no acervo — esperado).
- **Calibração ±20d**: histograma paid−due = 99,7% entre 0..+8 dias.
  Janela atual é folgada e segura; manter.
- **OCR**: maioria conf ≥80; 78 docs <50 (lixo de scan mesmo). Gate 55 ok.
- **needs_review 2.487 (53%)**: gate §9 rígido por campo. Boleto vai muito
  bem (82% direto, resgate por barcode). Pior: comprovante (24% direto).
  Próxima alavanca de qualidade = revisar gate/prompts de comprovante.
- **Falso pago descoberto** (taxa de 2015 "paga" hoje): era ação MANUAL da
  UI (markLedgerPaid, "Marcar pago" do card — paid_date=hoje). Não é bug de
  pipeline. MAS expôs buraco real: `matchObligation` do Agente 2 casava
  comprovante↔obrigação só por CNPJ+valor, sem data. Fix: vencimento a
  ±90d do pagamento. Commit `7d8dad1` — **ATENÇÃO: caiu no branch
  `feat/custo-llm-usage` (outra sessão trocou o branch do worktree no meio);
  ambos os fixes JÁ ESTÃO DEPLOYADOS em prod.**

## Pendências

- Pedro: OK pro push da main local (`d4e549c`) — gate de aprovação.
- Integrar `7d8dad1` quando o branch feat/custo-llm-usage for mergeado
  (ou cherry-pick pra main junto).
- Fila humana: 2.487 precisa-de-revisão pra UI /revisar drenar.
- Air/funnel, SwiftBar, Ryzen 9: inalterados (ver update anterior).
