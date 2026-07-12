# Acesso restrito ao banco p/ funcionário — só ENTRADAS, travado na RLS

**Decisão do Pedro (2026-07-03) — pro CODE DO HUB (risenagência).**

Objetivo: no Financeiro → Extrato, um papel "funcionário" vê **só o que ENTROU**
(Pix e boletos que caíram = créditos) e **NÃO** vê débitos/saídas, pagamentos, saldo
do dia, nem a vida financeira/saída fixa da empresa. Ele "acessa o banco" mas não
enxerga os gastos.

## REGRA DE OURO: travar no BANCO (RLS), não só na tela
Se filtrar só no React, o funcionário curioso vê os débitos pela rede/API — o dado
chega no navegador dele. O corte tem que ser enforcement na camada de dados.

## Spec
1. **Papel/permissão** `extrato_somente_entradas` (nome à escolha), atribuível na
   Equipe, reusando o sistema de papéis do Hub (RequireRole/permissions).
2. **RLS no `espelho_extrato`** — hoje: `using (tenant_id = current_tenant_id())`.
   Trocar por: `using (tenant_id = current_tenant_id() AND (NOT <papel_restrito()> OR
   type = 'CREDIT'))`, usando o helper de papel que o Hub já usa nas policies.
   Débitos NEM SAEM do servidor pro usuário restrito. (Opcional: refinar créditos por
   Pix/boleto via transaction_type; `type='CREDIT'` já cobre "só entradas".)
3. **UI (ExtratoPage)** pro papel restrito: esconder cards de saldo/A receber/total/
   débito; esconder filtro Movimento (Entradas/Saídas); tabela já vem só crédito.
4. **Fechar vazamentos:** Dashboard (KPIs de saldo/saídas), menu (Contas a Pagar/
   Boletos a pagar/Faturas de despesa/Extrato completo) — mesmo gate de papel.

Enforcement = RLS (passo 2). Tela = só apresentação (3-4). Se a RLS estiver certa, mesmo
com a tela falhando, o funcionário não acessa os débitos. Migration em prod = gated.
Registrado em `lab/knowledge/wiki/decisoes-ativas.md` #13.
