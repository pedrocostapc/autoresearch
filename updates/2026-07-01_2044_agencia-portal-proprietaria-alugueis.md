# Agência (Hub) — carteira de aluguéis da Ivete/CRD + Portal do Proprietário

App: **agencia** (pixel-perfect-replica, ref `yfzljfvqlnxqaqtdrntc`, tenant `risen-midia`).
Tudo aplicado em PROD (gated) e no ar (push main → Vercel).

## 1) Import da carteira de aluguéis (dados reais)
Módulo Aluguéis estava vazio. Populei a partir dos contratos PDF (Dropbox
`Imobiliaria/`) + planilha `alugueis recebidos.xlsx`:
- **2 donos**: CRD (Cordeiro Bicicletas e Motos, CNPJ 04.890.362/0001-56) e Ivete Alves
  Cordeiro (CPF 042.275.086-73). CRD ligada à Ivete via novo `clients.represented_by_client_id`.
- **7 imóveis** (`rental_properties`, casas Cícero Passos/Pirapora): MLZ-1077/1087 (CRD),
  MJO-500 (CRD, inquilina CYMI), MJO-510/520/530/540 (Ivete). 7 contratos ativos, 7 inquilinos
  (5 reaproveitados de `clients`, 2 criados).
- **Histórico de mensalidades** inserido direto (as RPCs padrão não reproduzem proporcionais/
  reajustes/paid_at histórico): recebido **R$ 179.037,25** (bate com a planilha), taxa adm 10%.
- **MLZ-1087 encerrado** (contrato ended, imóvel available; removi meses pós-termo + recebível).

## 2) Portal do Proprietário (reaproveita client_portal_accounts)
Migrations novas: **`p29_owner_portal`** e **`p30_property_acquisition`**.
- **Login por CPF/CNPJ** (e-mail sintético `04227508673@portal.hubmidiaooh.app` + senha=CPF)
  na `PortalLoginPage`. Conta da Ivete em `client_portal_accounts` (can_view_rentals).
  ⚠️ CPF como senha é fraco — MVP; trocar por senha própria depois (fluxo nova-senha já existe).
- **RPCs security-definer** (filtram por `current_client_id()` + representados):
  `portal_owner_client_ids`, `portal_owner_properties`, `portal_owner_payments`.
  Testado isolamento: a conta só enxerga os próprios dados.
- **RLS self-read** (account/clients/tenants) — sem isso o PortalGate lê zero pra portal user
  (gap que afeta TODO o portal atual: as tabelas só tinham policy `current_tenant_id()` = staff).
- **Realtime** em `rental_payments`/`rental_contracts`/`rental_properties` + `receivables`
  (atualização ao vivo quando marca pago/repassado/boleto).
- **Dashboard de investidora** (`PortalOwnerDashboard` + `PortalOwnerHistory`): imóveis, valor
  mensal, entrada, já rendeu, fechamento por ano (2025/2026), **rentabilidade a.a. (yield)**,
  mensalidades mês a mês, **status do boleto** (não emitido/emitido/pago + link, via join
  receivables+boletos) e **prestação de contas PDF** (reusa `OwnerStatementPDF`).
- Novo campo `rental_properties.acquisition_cost_cents` (R$ 250k placeholder em cada) → yield.

## Acesso
`hubmidiaooh.app/portal/risen-midia/login` — CPF nos dois campos.

## Pendências (quando o Pedro quiser)
- Valores REAIS de aquisição por imóvel (hoje R$ 250k média) → yield exato.
- Yield líquido (descontando taxa adm) e rentabilidade realizada (já rendeu / aquisição).
- Boletos de aluguel ainda `draft` (dia 5): quando emitir via Cora, a coluna Boleto acende sozinha.
