# Pontes criadas: SuperSec e ai-connect agora sabem do cérebro

> Criado: 2026-06-11 12:55 — sessão Claude Code em `/Users/pedrocosta/Dev/autoresearch`

## O problema (apontado pelo Pedro)

Os 114 agentes foram ingeridos em `lab/agents/` mas **as outras sessões não
ficaram sabendo** — o projeto que planejava usar esses arquivos como
referência (SuperSec) não tinha nenhum ponteiro para a nova localização
canônica. O canal `updates/` só funciona se a sessão souber que ele existe.

## Verificação primeiro: nada se perdeu

- `~/Downloads/57 Agents Contabildiade/` — 70 arquivos intactos
- `~/Downloads/57 Agents advocacia/` — 58 arquivos intactos
- Docs de apoio (`mapeamento-57-agentes*.md`, `00-super-secretaria-projeto-base-v4.md`) — intactos
- A ingestão para `lab/agents/` foi **cópia**, não movimentação. O SuperSec
  nunca teve os arquivos dentro do repo dele (sempre estiveram só em Downloads).

## O que foi feito

1. **`super-secretaria-functions/CLAUDE.md` criado** (não existia): contexto
   do projeto + ponte para o cérebro (updates/ + lab/) + localização canônica
   dos 114 agentes + protocolo de scoring + plano `super-secretaria-knowledge`.
2. **`risen-ai-connect/CLAUDE.md` atualizado** (existia, 88 linhas, zero
   menção ao cérebro): adicionada seção "Cérebro da organização (cross-sessão)"
   ao final, sem tocar no resto.
3. **`autoresearch/CLAUDE.md` corrigido**: o mapa dizia que os agentes estavam
   "ainda em Downloads" — agora aponta `lab/agents/` como canônico e Downloads
   como cópia congelada.

## Convenção que isso estabelece

Toda sessão/projeto do Pedro deve ter no seu CLAUDE.md a ponte para o cérebro
(ler `updates/` ao abrir, escrever ao fechar, lab/ como fonte de agentes/skills).
Projetos novos: copiar a seção "Cérebro da organização" do CLAUDE.md do
ai-connect.

## Pendências

- [ ] Sessões SuperSec e ai-connect ainda não *leram* as pontes — elas só
      passam a valer na próxima sessão aberta nesses repos (CLAUDE.md é lido
      na abertura). Se houver sessão antiga ainda aberta, avisar manualmente.
- [ ] `pendencias-globais.md` da wiki pode absorver este checklist no próximo
      health check.
