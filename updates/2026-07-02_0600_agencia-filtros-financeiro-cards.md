# agencia: filtros em cards no Financeiro (Extrato/Boletos/Notas) + ordenação

**Sessão:** 2026-07-02 (madrugada) · Repo pixel-perfect-replica, main (deploy Vercel ok).

## Processo (importante pra próxima sessão)
Pedro exigiu e aprovou o fluxo: **mockup HTML primeiro (3 iterações), implementação
só depois do OK**. Design aprovado (v3): filtros em CARDS numa **linha só** —
Buscar compacto (cliente se busca ali, NÃO vira card) · Período em presets ·
grupos por tela · Valor mín–máx · limpar. Menu do app é lateral vertical; usar a
largura toda (limite 1440px já removido em sessão anterior).

## O que entrou (`src/components/finance/filter-bar.tsx` + 3 páginas)
- FBar/FBusca/FPeriodo/FCards/FValor + useSort/ThSort/ordena (camada de UI pura;
  filtros/ordenação em memória sobre o espelho local — zero rede).
- Extrato: Movimento + Tipo (cards dinâmicos por frequência) · default 30d.
- Boletos: Status + Forma · período conta por venc.⇄emissão⇄pagamento (rótulo
  alterna) · default Tudo · query agora lê o espelho inteiro (2022→hoje).
- Notas: Direção + Financeiro (quitada/parcial/vencida/aberta/**sem fatura**, via
  fatura do razão) · valor.
- Ordenação clicável em todas as colunas (asc/desc) · KPIs refletem o filtro.
- Preservados: TODAS as colunas, ColumnPicker, Atualizar, Modelos (exigência dele).

## Regras vivas do repo (outra sessão criou — LER)
`CLAUDE.md` + `docs/CORE-CONTRATO.md` no repo: não reescrever espelho.ts /
sync-espelho / risen-core-proxy / core-events-receiver; tela lê banco local e
sincroniza POR TRÁS; uma sessão por vez no repo. Pedro vai arrumar o sistema de
boletos junto com o Core depois — NÃO mexer em emissão de boleto até lá.

## Estado do espelho (prod)
extrato 1.406 · boletos 904 (172 c/ descrição — completar descrições é pendência)
· nfse 0 (throttle de releitura do ADN gov.br; re-consulta 1x/h, volta sozinho).
