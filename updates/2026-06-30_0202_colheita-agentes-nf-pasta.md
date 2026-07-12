# Colheita dos agentes fiscais → pasta NF determinística (SuperSec)

**Quem:** sessão Claude Code no repo `super-secretaria-functions`.
**O quê:** usei 8 agentes de `contabilidade/` para "colher" suas regras determinísticas e
transformá-las na receita da **pasta NF** do SuperSec (extração + validação fiscal sem LLM no
caminho feliz). Contexto da arquitetura: estamos extraindo das LLMs-agentes a parte que era
"tabela decorada" → vira tabela de referência no banco (`referencia_grupo/item`), e a regra do
agente vira **consulta determinística**. A LLM fica só no resíduo.

## Como usei cada agente
Subagente por agente, lendo o `.md` inteiro e devolvendo o mapa `regra → campo do XML NF-e →
tabela → determinístico/julgamento`. Blueprint consolidado em
`super-secretaria-functions/docs/blueprint-pasta-nf.md` (+ `docs/colheita-cadastro-nf.md`).

## Scoring (protocolo) — todos entregaram, recomendação:
| Agente | Resultado | Recomendação |
|---|---|---|
| `24-cadastro-nf` | excelente — núcleo da classificação NF (CFOP/CST/NCM/retenções), ~tudo determinístico | **PROMOVER** |
| `06-sped-fiscal` | mapa forte de escrituração (C100/C170/C190/E1xx) determinística | **PROMOVER** |
| `32-efd-contribuicoes` | PIS/COFINS por item, base Tema 69, monofásico — determinístico | **PROMOVER** |
| `29-calculo-ipi` | IPI por NCM, recálculo, CST×CFOP — determinístico | **PROMOVER** |
| `02-icms-iss` | ICMS/ST/DIFAL/ISS, recálculo+coerência — determinístico | **PROMOVER** |
| `09-efd-reinf` | gerador de eventos de retenção sobre NF de serviço — determinístico dado destaque | **PROMOVER** |
| `46-revisao-cruzamento-sped` | é conciliação SPED×declaração (agregado), **não** pasta NF | manter `candidate` / re-escopar p/ A2/A3 |
| `05-conferencia-guia` | é pasta **Guias/pagamento**, não NF | manter `candidate` / mover p/ pasta Guias |

## Achados que valem pra curadoria
1. **Tese confirmada:** o caminho feliz da escrituração/validação fiscal é ~100% determinístico
   (recálculo `v=base×alíquota` + coerência CST/CFOP/regime-via-CRT + totais). O resíduo de LLM é
   **um tipo só** em TODOS os agentes: classificar **natureza/finalidade** quando o XML não basta
   (insumo? devolução? cessão de MO? cClassTrib ambíguo?). Quando a NF já destaca, é determinístico.
2. **~15 tabelas de referência novas** que os agentes "sabiam de cor" e ainda não estão no banco —
   2 críticas: `tipi-aliquotas-ipi` (IPI por NCM), `aliquotas-ibs-uf-municipio` (IBS ente-dual).
   Lista completa no blueprint. Estou semeando das fontes oficiais (não inventando).
3. **Gap NFS-e:** ISS e retenções de serviço operam sobre NFS-e (ABRASF/padrão nacional), que ainda
   NÃO tem leiaute semeado — é a próxima "pasta gabarito" (irmã do leiaute NF-e que já semeei).
4. **Fronteira:** os agentes de cruzamento/guia (46, 05) não pertencem à pasta NF; são da camada de
   conciliação (Agente fiscal A2/A3). Bom registrar pra não misturar camadas.

## Estado do SuperSec (pra quem cura)
Já semeei como tabelas de referência, da fonte oficial: leiaute NF-e 4.00 (831) + reforma RTC (1020),
boleto FEBRABAN (772, com CNAB+bancos), extrato Open Finance (31, obrigatório/opcional). Commits na
`main` do `super-secretaria-functions`. Próximo: semear as ~15 tabelas que faltam + régua NFS-e.
