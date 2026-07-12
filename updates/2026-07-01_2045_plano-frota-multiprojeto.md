# Frota multi-projeto (via Core) — plano escrito

Atualizei o guia da frota (`lab/knowledge/wiki/frota-de-maquinas.md` §9) e escrevi o PLANO de execução:
`lab/knowledge/wiki/plano-frota-multiprojeto-via-core.md`.

Ideia: qualquer app Risen despacha OCR/extração na frota (custo zero) VIA CORE (broker v1-call), não
app-a-app direto. Chave: o app entrega um SIGNED URL do arquivo → a frota não guarda credencial de
projeto nenhum. Assíncrono (v1-ocr-dispatch → job_id → v1-ocr-result). Dual-source na transição (fila
do Core + a do SuperSec) pra não quebrar o SuperSec.

6 fases: fila fleet_jobs no Core → 2 edges no broker → worker dual-source → repontar as 4 máquinas →
contrato pros apps → (opcional) SuperSec migra. Esforço ~1-2 blocos. Dependência: confirmar como o
broker v1-call registra uma action nova (repo risencore).
