# Diagnóstico de fricção (mineração de transcripts) + inventário do inbox

**Sessão:** autoresearch (Mac mini), 2026-06-12 ~17h45.

## O que foi pedido

Pedro: "voce consegue ver as minhas conversas, meus projetos, ver onde tenho
mais dificuldades, onde sempre tenho que ficar falando a mesma coisa?
[...] procurar dentro do banco de skills e agentes pra avaliar, otimizar e
deixar minha vida mais facil". E: "acabei de colocar novas skills no inbox".

## O que foi feito

1. **Mineração de TODOS os transcripts de Claude Code do Pedro**
   (~/.claude/projects/, 13 projetos, ~2.300 mensagens dele, 12/05→12/06).
   Script de extração → /tmp/pain-mining/*.txt → 4 agentes analistas em
   paralelo (ai-connect, SuperSec, risencrm/risenos/core, autoresearch/
   minhaobra). Consolidado priorizado:
   **`lab/knowledge/outputs/2026-06-12-diagnostico-friccao.md`** ← LEIAM.
2. **Inventário classificado do inbox** (~1.830 arquivos despejados):
   **`lab/knowledge/outputs/2026-06-12-inventario-inbox.md`**. Nada movido
   ainda.
3. Plano de ação virou bloco novo no topo de `wiki/pendencias-globais.md`.

## Achados-chave (para TODAS as sessões)

- A dor dominante do Pedro é de PROTOCOLO, não técnica: ele é carteiro entre
  sessões, operador de git por procuração e fiscal de status. As 3 coisas
  são automatizáveis.
- **Regras de comunicação com o Pedro** (valem já, em qualquer sessão):
  PT-BR; nomear ferramenta por função, não por engine ("sonnet" → "gerador
  de relatório"); opções em lista numerada curta; tabela quando ele pede
  tabela; NUNCA deixar escopo pela metade; nunca pedir pra ele compor
  comando de shell; segredo NUNCA no chat (apontar .env/cofre).
- **SEGURANÇA: segredos de produção estão em claro nos transcripts**
  (service_role, sk-ant, sbp_, DO, Cloudflare, tskey, chave SSH privada).
  Rotação + Bitwarden é pendência nº 1 de risco.
- O inbox novo contém a solução de várias dores: o FLUXO-IMPLEMENTACAO do
  Pedro (protocolo de gates já documentado), o runbook embrionário do
  incidente "IA parou" (11 ocorrências!), 6 agentes C-Level, packs de skills
  fullstack/instagram/PME.

## Pendências

- [ ] Ver bloco "Diagnóstico de fricção 12/06" em wiki/pendencias-globais.md
      (7 itens priorizados: CLAUDE.mds, rotação de segredos, /entregar,
      /ia-caiu, matriz de autonomia, status push, execução da triagem)
- [ ] Pedro: OK para as partes destrutivas da triagem (mover dados de
      cliente pro repo risen, descartar duplicatas/novo-projeto) e decidir
      as pastas vazias "Minha Obra"/"Risen OS"
