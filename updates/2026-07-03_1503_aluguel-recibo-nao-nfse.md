# Correção fiscal: ALUGUEL = recibo (não NFS-e), só depois de pago

**Decisão do Pedro (2026-07-03) — pro CODE DO HUB (risenagência).**

No Hub, Financeiro → Contas a Receber: um recebível de **origem `aluguel`** NÃO
emite nota fiscal (NFS-e). Emite **RECIBO DE PAGAMENTO**, e **só DEPOIS que o
aluguel é pago** (`status=pago`).

- Hoje o botão "emitir" do aluguel abre o modal **"Emitir serviço — aluguel (só
  nota)"** com canal NFS-e (gov.br/Focus) → **ERRADO** para aluguel.
- Correto: recebível `origem=aluguel` → ação "gerar recibo", habilitada quando pago;
  NÃO abrir o modal de NFS-e.
- Serviço normal (outdoor/instagram) segue nota + boleto — sem mudança.

Supersede o registro de 30/06 ("aluguel = só NFS-e + recibo"). Detalhe em
`lab/knowledge/wiki/decisoes-ativas.md` #12. Fix é do Hub, não do Core.
