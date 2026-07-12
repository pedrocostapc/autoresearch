# O padrão central: gerar → medir → selecionar

> Wiki do cérebro. Atualizada: 2026-06-11. Fontes: `updates/2026-06-11_*`.

Todos os sistemas do Pedro convergem para o mesmo loop darwinista do
autoresearch (propor → medir → manter/descartar), aplicado em três escalas:

| Escala | Gerador | Métrica | Seletor | Estado |
|---|---|---|---|---|
| Código de treino (autoresearch) | agente noturno em `train.py` | `val_bpb` | keep/discard em `results.tsv` | nunca rodou (precisa GPU) |
| Skills & agentes (`lab/`) | inbox + skills-library + packs próprios | `scoreboard.tsv` (uso real nos projetos) | candidate → active → archived | cérebro montado 2026-06-11 |
| Personas (Ei Risen) | Fábrica de Arquétipos | simulator + juiz LLM (9 critérios) e metrics_before/after | portão antes de publicar; `auto_update` por tenant | fábrica desenhada, medição em aberto |

## Implicações

1. **Sem métrica não há seleção.** O elo fraco em todas as escalas é a
   medição: o persona-evolution tem colunas de métricas vazias; o scoreboard
   do lab nasce vazio; o autoresearch nunca rodou. Prioridade do cérebro é
   fechar loops de medição, não gerar mais material.
2. **Conhecimento deve compor entre rodadas.** A fraqueza do autoresearch puro
   é cada noite começar do zero. O antídoto é esta wiki: achados viram
   artigos citando fonte (commit, val_bpb, conversa); contradições viram
   experimentos de desempate; lacunas viram candidatos.
3. **Naturalidade é critério eliminatório** (decisão do Pedro na fábrica de
   personas): "o cliente desconfiaria que é bot?" reprova. O DNA sóbrio do
   Betinho é referência de estrutura, não de tom.
