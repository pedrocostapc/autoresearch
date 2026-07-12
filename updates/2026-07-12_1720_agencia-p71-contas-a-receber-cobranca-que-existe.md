# agencia/Hub: p71 — Contas a Receber = cobrança que EXISTE (reverte pedaço da p70)

Pedro redefiniu o conceito hoje à tarde: **Contas a Receber não é projeção** de
fluxo de caixa — é cobrança viva. "Antes do boleto ser criado não é uma conta a
receber; nem dá pra garantir que o inquilino vai estar lá no mês que vem."
Projeção de mensalidades futuras mora em Aluguéis → Mensalidades.

## O que mudou (commit 5aada3a, migration aplicada em prod + edge deployada)
1. **p71** (`20260712250000_p71_receivable_nasce_na_emissao.sql`):
   - `ensure_rental_payments_cycle` volta a NÃO criar receivable junto com a
     mensalidade (reverte esse pedaço da p70 de hoje cedo; mantém p68/p69).
   - Baixa do legado pré-sistema: mensalidades não pagas com venc < mês corrente
     → pagas NO VENCIMENTO (`paid_at = due_date`), recibo carimbado
     "(histórico — não enviado)" (padrão p32, sem e-mail retroativo) e
     `owner_transferred_at` preenchido. Em prod eram 3 (dez/2025 Mariana + CYMI
     mai e jun/2026, ~R$ 6.7k).
   - Apagados 5 receivables draft de venc 05/08 (cobrança ainda não aberta).
2. **rent-boletos-monthly**: no dia de emissão do contrato (`boleto_emit_day`),
   contrato **depósito/externa** agora ABRE a cobrança (cria receivable draft →
   tela mostra "Aguardando pagamento") em vez de ser pulado. Janela de busca
   20d → 60d (cobre `vencimento_no_mes` p69, ex.: emite 25/07 vence 15/08).
3. **ReceivablesPage**: cards viram "A receber — junho/julho/agosto" (mês
   anterior = atrasados / atual / seguinte) + "Recebido no mês"; chips de mês
   com padrão no MÊS ATUAL; chips de status mantidos.

## Regra pra frota (Pedro)
Contas a Receber por **vencimento** (quando o dinheiro entra); competência é só
rótulo na descrição. Linha nasce no dia de emissão da cobrança, nunca antes.

## p72 (mesma tarde, commit cc313f0)
Bug: fluxos de ALUGUEL criavam boleto sem gravar `receivables.boleto_id` (só o
`boletos.receivable_id`) → linha "Emitido" reoferecia o botão "emitir boleto"
(risco de duplicar na Cora). Corrigido em `rental-boleto.ts` + robô (gravam o
vínculo inverso), tela endurecida (botão só quando emissível) e backfill p72
aplicado em prod. Os fluxos genéricos (EmitirServicoDialog etc.) já gravavam.

## Cards mensais + filtro de origem (commit 2ac1291)
Cards do Contas a Receber viraram 1 por mês (anterior/atual/seguinte) com
**Total / Recebido / A receber**; mês vizinho sem movimento não ganha card
(agosto só aparece pós-dia de emissão). Linha PAGA conta no mês do `paid_at`
(inclusive no filtro da tabela); aberta, no vencimento. Novo filtro por origem
(Aluguéis/Outdoor/Instagram/Gráfica/PI) e os 3 grupos de chips numa linha só.

## Mensalidades: "Pendente" = cobrança gerada (commit ea311db)
Na tela Aluguéis→Mensalidades, Pendentes agora exige `receivable_id` (a conta
foi gerada no dia de emissão); mensalidade futura do ciclo fica no chip novo
**Programadas** até o robô abrir a cobrança. Mesma filosofia da p71.

## Portal do dono v3 — mobile-first (commit 13b829c)
Reconstrução das duas telas do Portal do Investidor (pedido do Pedro, fim da
tarde): layout pensado pra iPhone 15+ (cards, max-w 720 centrado, sem tabela
larga). "Meus imóveis": banner EM DIA/atrasado, card "Seu investimento"
(investido → virou = imóveis hoje + aluguéis recebidos, % de ganho) e um card
por imóvel com a mesma história + atalho pro fluxo. "Mensalidades": filtro por
imóvel (?imovel=CODE), navegação de mês por setas, resumo Recebido/Líquido/
A receber, cards por mensalidade, histórico clicável, PDF mantido. Sem mudança
de backend (RPCs portal_owner_* p66/p67). Preview admin (ver) esconde o atalho.

## Avisos
- `supabase_migrations.schema_migrations` NÃO existe nesse projeto — migrations
  se aplicam via Management API (`database/query`), não `db push`.
- O secret `SUPABASE_DB_URL` do projeto Bitwarden `supabase-agencia` NÃO é uma
  URL nem a senha do banco (hex de 64 chars, não autentica no pooler) — valor
  suspeito/errado, e vazou num erro de terminal hoje; sugerido rotacionar/corrigir.
- 78 mensalidades históricas (backfill p32) estão pagas sem `owner_transferred_at`
  → podem poluir "Repasses pendentes" no dashboard de Aluguéis. Não mexi (fora
  do escopo de hoje).
