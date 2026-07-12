# SuperSec: doc_type novo mapeado — "prestação de contas com cheque" (N despesas : 1 saída)

Durante o teste de estresse da frota (12/07), o Pedro analisou o doc
`18-09-28 Despezas Escritório Ch 426 R$520,81.pdf` (tenant EUCA/PC Construções,
Drive id `1v5hWWV5aVMCjhcG01hWo5FAaqsZLF3kq`, document_id
`50591fc1-c9fd-4e47-a478-6068f5fca8e0`) e identificou um padrão de documento
que a esteira ainda não modela:

**O documento**: 1 página escaneada com (a) tabela impressa de ~30 despesas
miúdas (data, fornecedor, tipo de comprovante CF/Recibo/NF, valor) somando
R$ 520,81 e (b) cópia do cheque SICOOB nº 426 manuscrito que paga o total.
Camada de texto embutida é OCR-lixo de scanner (leitores divergem 2,2k-12k chars).

**O problema apontado pelo Pedro** (nas palavras dele): as despesas já teriam
que estar lançadas no sistema pra ele só vincular o monte de notinhas a UMA
saída de pagamento consolidada. Hoje a esteira trata como "um doc, um valor" —
ou vira despesa genérica de 520,81 (perde o detalhe) ou notinhas soltas sem
forma de pagamento (não conciliam com extrato).

**Fluxo ideal do doc_type** (proposta discutida):
1. Extrair a tabela → N lançamentos de despesa individuais.
2. Extrair o cheque → 1 saída consolidada (banco, nº cheque, valor, data).
3. Vínculo N:1 despesas→cheque; conciliação casa o cheque com o débito do extrato.

É o mesmo padrão curador do "extrato→comprovante→holerite no padrão nfe.py"
(ver memória supersec-aprocessar-muleta). O arquivo de 2015-2018 da PC deve ter
MILHARES de irmãos desse (prestações de contas mensais com cheque).

**Bônus técnico pra esteira** (Zeladora): esses híbridos scan+OCR-embutido são
os que mais custam OCR (5-18min/doc). Discriminador pronto e barato: a
CONCORDÂNCIA entre os leitores de texto já gravada em document_extractions
(char_count por engine) — concordância alta = camada confiável, pular OCR
pesado; divergência = rodar tudo. Maior alavanca de vazão disponível.

— Zeladora da Frota, 12/07 15:10

## ADENDO 15:20 — Pedro corrigiu o modelo + pedido de CATALOGAÇÃO (pra Operadora)

**Correção do Pedro sobre o doc_type**: a folha de despesas NÃO é autossuficiente —
é só APONTAMENTO. Sem as notas fiscais de compra lançadas no sistema, não há o que
baixar contra o cheque. Autossuficiente = NF digitalizada + cheque no MESMO arquivo
(despesa + forma de pagamento juntos). Docs como esse são "mistos de apontamento".

**Pedido do Pedro (dito à Zeladora e também à Operadora)**: catalogar documentos
pra que pesados (contratos da Caixa registrados) e mistos (apontamento+cheque)
fiquem PRO FIM da esteira, deixando os leves/resolvíveis passarem primeiro.

**Diagnóstico da Zeladora (só leitura, 15:15)**:
1. O mecanismo já existe pela metade: claim_extraction_job tem priority + regra
   forte/fraca (fracas não pegam priority ≥90 com forte online; teto attempts 5).
2. PEGADINHA: o ORDER BY atual manda pesados pras FORTES PRIMEIRO
   (case when v_forte then -priority), o CONTRÁRIO de "fim da esteira".
   Pra "pesado por último pra todos" é ajuste pequeno no ORDER BY + catalogador.
3. page_count/file_size são NULOS/inúteis pré-processamento (99,9% dos 19,6k
   pendentes sem page_count; nenhum >5MB na fila atual). O sinal de entrada barato
   é o NOME DO ARQUIVO. Contagem na fila pendente de agora:
   - "Contrato .* Registrado" (gigantes 12-18min): 27
   - "Despe[sz]as .* Ch/prestação" (mistos): ~571
   - contratos em geral: 47
4. Catalogador definitivo (pós-1ª extração): CONCORDÂNCIA entre leitores de texto
   (char_count por engine em document_extractions) — já gravado, custo zero.

A Zeladora NÃO alterou priority de nenhum job (semântica do funil = Operadora).
SQL de exemplo pro catalogador de nome (a Operadora valida/aplica):
  update extraction_jobs ej set priority = 20  -- ou o valor "fim de fila" escolhido
  from documents d where d.id = ej.document_id and ej.status = 'pending'
    and d.original_filename ~* 'contrato.*registrado|despe[sz]as.*ch [0-9]|prestac';
(exige antes o ajuste do ORDER BY pra que priority baixo = fim pra TODOS.)
