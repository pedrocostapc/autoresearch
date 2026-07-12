# agencia: recibo de aluguel por e-mail · PENDÊNCIA pro Core (v1-notify, 1 linha)

**Sessão:** 2026-07-02 · **Repo:** pixel-perfect-replica (main).

## O que entrou no Hub
Ao **marcar mensalidade paga** (Aluguéis → Mensalidades), o Hub gera o **RECIBO DE
ALUGUEL em PDF** (valor por extenso, locador/locatário/imóvel/competência, estilo da
casa) e envia ao inquilino por e-mail **via Core → Resend** (`core.notify.send`, PDF
anexo, assunto customizado). Nas pagas há botão **Recibo** pra (re)enviar. Arquivos:
`src/pdf/RentReceiptPDF.tsx`, `src/lib/api/rental-receipt.ts`, `src/lib/valor-extenso.ts`.
Sem e-mail cadastrado no cliente → avisa e não envia (cadastrar e-mail dos inquilinos!).

## 🔧 PENDÊNCIA pra sessão do CORE (mexer no Core está fora do meu escopo aqui)
O `v1-notify` tem o cabeçalho do e-mail FIXO: `emailLayout('Sua Nota Fiscal e Boleto', corpo)`.
Pra recibo (e futuros usos genéricos) ele precisa aceitar título customizado.
**Patch de 1 linha** em `functions/v1-notify/index.ts` (projeto `hjclvuzugdbpvnomvtpn`):

```ts
// antes
html: emailLayout('Sua Nota Fiscal e Boleto', corpo),
// depois (retrocompatível)
html: emailLayout(body.titulo ? String(body.titulo) : 'Sua Nota Fiscal e Boleto', corpo),
```

O Hub **já envia** `titulo: "Recibo de pagamento de aluguel"` no payload — hoje é
ignorado; com o patch, passa a valer. Enquanto isso o recibo sai com corpo correto,
anexo correto e assunto correto; só o h2 interno do e-mail fica genérico.

## Contexto extra da mesma sessão
- Conciliação retroativa validada pelo Pedro em produção: regra pegou NF 67/68 com
  "soma difere" = pagamentos parte em dinheiro (real). Futuro: forma de pagamento
  composta (dinheiro+boletos) nasce no ORÇAMENTO; o razão já suporta parcela sem
  cora_invoice_id com baixa manual.
- Varredura da conciliação agora começa no ano da nota mais antiga do gov.br (2026).
- Pedro vai mandar PDFs das notas de 2025 (sistema antigo) pra importar no razão.
