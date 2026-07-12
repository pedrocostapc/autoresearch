# SuperSec — esteira v2: revisão completa + TUDO implementado (2026-07-08, madrugada)

Sessão longa com o Pedro: revisão geral da esteira de documentos (3 exploradores de
código + leitura conjunta do fluxograma, nó a nó), e depois **modo automático**: todas
as decisões implementadas, deployadas e verificadas em produção na mesma noite.

**Relatório canônico:** `super-secretaria-functions/docs/esteira/revisao-esteira-2026-07-08.md`
(tabela achado→conserto completa). Fluxograma vivo v5 no artifact da sessão.

## O que mudou em produção (resumo pra quem não viu a conversa)

- **Triagem pós-leitura**: gatilho da triagem saiu do INSERT → dispara no done/error da
  fase 1 da frota. `deferFleet` MORREU. (Analogia do Pedro: a ficha só entra na mesa da
  secretária quando o leitor termina.)
- **XML sem caminho especial**: `classifyXml` aposentado; XML entra na frota
  (`text:xml`) e classifica por tags — assinatura `'NF-e (XML)'` (10 tags só-de-XML)
  semeada no cérebro. Movedor-v2 perdeu ~200 linhas de código morto do monólito.
- **Pré-voo de sanidade no worker.py**: senha/corrompido/em branco → Revisar com motivo
  acionável SEM gastar as 9 engines. Provado em produção.
- **Consenso por FAMÍLIA** (texto × OCR) em vez de por cabeça; confirmado ≥ 0,6.
- **Afinidade de máquina**: pesado prefere GPU/Apple Vision online (nunca exclusivo).
- **Órfão pelo coração**: heartbeat >2 min → job devolvido na hora, tentativa devolvida.
- **`retentar_leitura(2)` religada** (era função órfã — zero chamadas!): cron 15 min.
- **Placar de serviços + reloginho** (regra do Pedro: "consulta primeiro, chama
  depois"): `service_status` + `service-monitor` 1 min + gates no movedor (Drive) e
  enquadrador (IA) + chips no header do /admin (Drive · IA · Banco).
- **Cerca de dinheiro**: `llm.teto_diario_brl` (R$20 default) — estourou → IA pausa.
- **Drive por Changes API**: marcador por tenant, cron 1 min (intervalo editável em
  `drive.changes_interval_min`), completa diária 03:00. Latência de ingestão: até 30
  min → ~1 min.
- **worker-avisos** (15 min): DLQ>0 / erro de leitura esgotado / AP>24h → email pro
  Pedro com o erro exato (dedup por foto/24h). A gaveta não é mais muda.
- **fleet-status v2** (lia arquitetura morta; consertou "Ao Vivo: Frota 0 máquinas").
- **doc-bytes serve Storage**: doc de UPLOAD agora chega na frota (buraco achado no
  teste ponta-a-ponta).
- **Deriva git↔deploy sanada**: importers/enquadrador/10 migrations commitados; cron
  `movedor-drain` codificado em migration; config.toml sem worker-agent-1/2/3/4.

## Verificação (produção, ~02:48)

3 docs de teste (senha/em branco/XML sintético) injetados e removidos: pré-voo pegou os
2 PDFs com motivo certo e zero engine; o XML classificou por tags → curador fase 2 →
gate honesto. Pipeline inteiro < 1 min.

## Decisões de conceito registradas (valem pra frente)

- `a_processar`/aba AP é **MULETA**, não feature — morre quando os curadores nascerem.
  Ordem: **Extrato (OFX) → Comprovante (PIX/TED) → Holerite (soma de verbas)**.
- Movedor = conta de padaria (4 contas); espécie por tags, direção pela posição do
  nosso CNPJ (nota de fornecedor vem carimbada "1-SAÍDA" — tag não separa compra/venda).
- Incidente US$419 recontado certo: cron 120s × 20 docs×LLM morto à força sem rastro
  → re-fila infinita (não "doc quebrado").

## Pendências (próxima sessão com o Pedro)

- [ ] Curadores Extrato → Comprovante → Holerite (padrão nfe.py; gabaritos em
      `reference-ts-importers/`)
- [ ] Assunto **DANFE** que o Pedro guardou ("vou falar mais dela depois")
- [ ] `access_key_44` nunca é gravada (índice único inerte — dedup por chave-44 morto)
- [ ] Painel Ao Vivo semi-estático (estados hardcoded no TSX) + front polish
- [ ] Poda de engines por medição (dados já acumulando)
- [ ] Leitura do fluxograma parou na etapa 4 (agentes que calculam) — retomar de lá

Commits: backend `0daff62` + `1734157` · front `e73bf47` (Vercel). 8 crons ativos.
Sem valor de secret neste doc; tokens ao vivo via Bitwarden (padrão).
