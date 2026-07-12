# SuperSec — esteira completa desenhada + Curador Notas v4 no ar (2026-07-08, madrugada²)

Continuação da sessão da revisão (ver update 0300). Pedro explicou a ORIGEM e a VISÃO:
SuperSec = o funcionário que ele não conseguiu contratar; os **57 agentes de contabilidade**
(lab/agents/contabilidade) são a descrição do trabalho, mas LLM-puros. A conversão é em
3 camadas: **Script** (lógica) + **Tabela de consulta** (a LEI, com vigência — muda a
tabela, não o código) + **resíduo LLM** (gated; na fase de teste o Claude faz o papel da
IA a custo zero; validado → chave no cofre → liga pra clientes).

## Esteira completa (fluxo com dependências) — artifact "esteira-completa-supersec"

Ordem 1→14 (construção = fluxo; cada peça nasce com insumos existindo):
Fase A (por documento): 1-Notas v4 (fabrica insumos de todos) → 2-CaP v2 (guias→tax_guides)
→ 3-NFS-e (retenções IN 1.234) → 4-Extrato / 5-Comprovante / 6-Holerite / 7-Empréstimos /
8-Fiscalização (paralelos). Fase B (por competência): 9-Financeiro (matching 3 pontas) →
10-Patrimônio (página NOVA Imobilizado) → 11-Fiscal (calculada×lida) → 12-Obrigações
(SPED) → 13-Auditor (0,1%) → 14-Relatórios/Pacote. Fontes dos 57 mapeadas por card.
3 tabelas a criar: ~~monofásicos~~ (FEITA), IN 1.234, vidas úteis IN 1.700.

## Feito nesta sessão (produção)

- **Estoque não aceita mais ativo/uso-consumo** (CFOP x.55x/406/407): `cfop_sem_estoque()`
  + limpeza (migration 20260708170000). Nota: CFOP impresso é do EMITENTE — destino real
  do comprador é resíduo do v4.
- **Curador NFe v4 — andar fiscal** (`importers/nfe.py::_andar_fiscal`, commit 2e52da9):
  destino_item por CFOP · valida NCM na consulta (chave PONTUADA 7216.10.00) · item_taxes
  por item regime-aware (Simples=0 c/ motivo; Real credita 1,65/7,6 se não-monofásico e
  destino revenda/insumo) · monofásicos = grupo novo `pis-cofins-monofasicos` (28 prefixos,
  4 leis) · fornecedor auto em suppliers (índice único é PARCIAL → get→patch/post, upsert
  PostgREST não serve) · C190 por CFOP×CST em raw_data.fiscal · pendências nomeadas.
- **Provado com NF real** (78dbb599): Simples→créditos 0, NCM válido, C190 5102=187600c.
  Teste do fornecedor auto rodando na frota ao fechar este update.
- Merge XML→PDF ganhou troca de bastão da chave-44 + herança fina (commits 334978e/8265527);
  montar_estoque agora é chamado pelo curador (9ae21fe).

## Estratégia comercial registrada

Pedro quer VENDER o SuperSec. Fase de teste: Claude no papel do Enquadrador/resíduo
(assinatura, 0¢ — o worker-enquadrador já devolve grupos+5 reps em modo preview pra isso).
Validou com os docs da empresa dele → API Anthropic no cofre → liga pra geral, já cercada
(teto 5 tentativas, teto diário R$, placar).

## Próximos (ordem do fluxo)

- [ ] Fechar teste do fornecedor auto (job phase-2 em rerun)
- [ ] nº 2: CaP v2 (guia lida → tax_guides) · nº 3: NFS-e (criar tabela IN 1.234)
- [ ] nº 4-6: Extrato (OFX) / Comprovante / Holerite — moldes do v4
- [ ] Painel Ao Vivo: cards dos curadores novos (hoje hardcoded no TSX)
