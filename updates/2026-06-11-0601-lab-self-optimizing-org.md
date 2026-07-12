# Lab: organização de pesquisa auto-otimizante

- **Criado em:** 2026-06-11 06:01 (BRT)
- **Sessão:** Claude Code, pasta `/Users/pedrocosta/Dev/autoresearch`

## Contexto

A conversa partiu de duas ideias do Karpathy:

1. **autoresearch** (este repo) — um agente de IA experimenta autonomamente
   em `train.py` durante a noite: modifica o código, treina por 5 minutos,
   mede `val_bpb`, mantém ou descarta, e repete. O humano edita apenas o
   `program.md` (as instruções do agente).
2. **Knowledge base auto-melhorável** (vídeo do YouTube "I Built Karpathy's
   AI Knowledge Base in Claude") — estrutura `raw/ → wiki/ → outputs/` +
   `CLAUDE.md`, onde o humano despeja informação sem organizar e a IA atua
   como bibliotecária: classifica, sintetiza, audita (health check mensal).

## O que foi discutido

- **Como juntar os dois projetos:** a fraqueza do autoresearch é que cada
  noite começa do zero — o conhecimento não compõe entre rodadas. A knowledge
  base resolve isso virando uma "memória de pesquisa": `raw/` recebe resumos
  das noites, `wiki/` destila achados (citando commit + val_bpb como fonte),
  `outputs/` gera briefings matinais. O health check vira gerador de
  hipóteses: contradições entre noites = experimentos de desempate; lacunas
  = candidatos para a próxima noite.
- **Pedido do usuário:** poder jogar agentes, skills e qualquer material em
  uma pasta e o sistema filtrar e otimizar sozinho — darwinismo do
  autoresearch aplicado às próprias skills/agentes da organização.

## O que foi construído

```
lab/
  CLAUDE.md        — schema do curador: triagem, scoring, promoção/demoção
  inbox/           — zona de despejo (qualquer coisa, sem organizar)
  agents/          — agentes curados (formato padronizado com frontmatter)
  skills/          — skills curadas (contém exemplo: ablate-before-adding)
  archive/         — itens descartados com motivo (nunca se deleta)
  knowledge/       — raw/ wiki/ outputs/
  scoreboard.tsv   — placar de desempenho por agente/skill
  changelog.md     — memória do curador
```

**Mecanismo:** itens entram como `candidate`, são usados nas rodadas
noturnas (experimentos inspirados levam tag `[skill:nome]` no results.tsv),
e após ~3 noites são promovidos a `active` ou movidos para `archive/` com
base no val_bpb real. Health check semanal funde skills sobrepostas e
atualiza a wiki.

**Integração:** o `program.md` ganhou a seção "The lab" com 3 obrigações
para o agente noturno: (1) triagem do inbox antes do loop + ler a wiki para
não repetir ideias falhas; (2) tagging de experimentos; (3) resumo da noite
em `knowledge/raw/` + atualização do scoreboard ao final.

## Estado atual do repo

- Nenhuma rodada do autoresearch foi executada ainda: sem branch
  `autoresearch/<tag>`, sem `results.tsv`, sem `run.log`, e
  `~/.cache/autoresearch` não existe (`uv run prepare.py` nunca rodou).
- Mudanças não commitadas: `program.md` modificado + pasta `lab/` nova.
  Atenção: `program.md` é do upstream do Karpathy — se for dar pull no
  futuro, vale manter essas mudanças numa branch própria.
- Esclarecido: sessões do Claude Code são isoladas — uma sessão não vê outra,
  apenas os arquivos no disco. O "link de skills" mencionado pelo usuário
  nunca chegou a esta sessão; deve ser colado aqui ou jogado em `lab/inbox/`.

## Próximos passos sugeridos

1. `uv run prepare.py` (requer GPU NVIDIA — o repo foi testado em H100).
2. Jogar o material de skills/agentes em `lab/inbox/` e pedir a triagem.
3. Iniciar a primeira rodada noturna apontando o agente para o `program.md`.
4. Decidir se commita o `lab/` (idealmente numa branch própria).
