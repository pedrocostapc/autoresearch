# SuperSec — Missões 08 e 09 CONCLUÍDAS · 10-11 codadas aguardando prod (toque do Pedro)

Executora, via canal COMUNICACAO-INTERNA.md (novo protocolo).

## 08 (Folha/Encargos/eSocial) — testada em prod ✓
Empregado sintético R$ 3.000: INSS 248,59 (tabela 2026 VIVA: SM 1.621 — os agentes
14/35 traziam números de 2025, TABELA DECIDE), IRRF 0 (simplificado), FGTS 240,00,
líquido 2.751,41; encargos: FGTS guia calculada + "CPP dentro do DAS" (Simples III);
fila eSocial: S-1200/1210/1299 prazo 15/07. Motor único validado 5/5.
⚠️ Bug histórico morto: curador holerite v1 NUNCA materializou payslip (payment_date
NOT NULL, falha muda). REGRA NOVA (da supervisora): teste de curador confere o
EFEITO na tabela de destino (count>0), nunca só status do doc.

## 09 (Obrigações) — testada em prod ✓
obrigacoes_do_mes regime-aware: junho = eSocial/FGTS/DCTFWeb (folha) + EFD-Contrib/
ECD (Presumido) + PGDAS-D (Simples); julho = ECF aparece sozinha. Status via
tax_filings. Gerador SPED = v2 (registrado).

## 10-11 codadas, prod RETIDO (itens 5-7 aguardam toque do Pedro)
- 10: fix posted_at commitado (83ae851) — re-apply pendente.
- 11: migration baf7bde + deploy generate-export-zip pendentes.
- Cards folha/enc/esoc/obrig ACESOS (front c184bd1); fech/ent aguardam teste.
- Empregado de teste (TESTE FOLHA MISSAO08, cpf 00000000191) + payslips calc +
  eventos + guia fgts calculada de teste ficam no banco ATÉ o teste da 10-11;
  limpeza total na sequência.

## Missão 12 = ITERATIVA com o Pedro (docs reais no Drive) — não fecha sozinha;
roteiro no arquivo 12 (OFX → boletos → PIX → holerite → NFS-e → auto).
