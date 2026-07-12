# Frota de máquinas — guia completo publicado

Escrevi o guia canônico da FROTA DE MÁQUINAS (OCR/extração distribuída, custo zero) em:
`lab/knowledge/wiki/frota-de-maquinas.md`

**Pra qualquer projeto do ecossistema Risen que queira despachar OCR/extração de graça nessas máquinas.**

Cobre: o que é, arquitetura (fila `extraction_jobs` + workers burros claim-first), inventário das 5
máquinas + como alcançar cada uma (SSH/Tailscale), por que o 3060ti Linux roda dentro do Windows (WSL+CUDA),
o load-gate de 3 estados nos Macs (a frota cede ao usuário), onboarding de worker novo, o CONTRATO pra
despachar trabalho, operação/recuperação, e o que falta pra virar serviço multi-projeto (§9).

Estado (2026-07-01): 4 workers no ar (M1, M3 com load-gate; Ryzen5 e 3060ti dedicados). Frota é hoje
1-projeto (SuperSec); pra multi-projeto falta uma fila compartilhada + doc-bytes genérico (Drive/Storage/URL).
