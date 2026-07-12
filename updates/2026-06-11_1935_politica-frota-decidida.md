# Política da frota decidida — fila SuperSec > treino

**Sessão:** autoresearch (Mac mini), 2026-06-11 ~19h35.
**Para a sessão do SuperSec ler.**

## A decisão (Pedro, nas palavras dele)

"Se tivermos filas grandes de arquivos na supersec, as máquinas trabalham pra
ela, essa com gpu inclusive. Se não tiver fila, as ociosas podem rodar modelos
de treinamento."

Formalizado (decisão nº 10 em `lab/knowledge/wiki/decisoes-ativas.md`):

```
usuário no teclado > fila SuperSec > treino de IA > ocioso
```

Vale para a frota toda. **Supersede** o "PROPÓSITO PRIMÁRIO: treinos de IA"
registrado na memória `maquina_pdf_engine.md` da sessão SuperSec (11/06) —
o treino agora é o uso do excedente, a fila é prioridade.

## Desenho acordado

- O job noturno do desktop vira **despachante**: checa a fila pesada do
  SuperSec a cada ciclo → fila grande = modo OCR; sem fila = modo treino
  (autoresearch). Decisão sempre ENTRE unidades de trabalho (experimento de
  ~5 min / documento), nunca matando no meio — contrato `~/night/STOP` já
  existente.
- **Histerese** para não bater modo: ex. entra em OCR com fila > 100 docs,
  volta ao treino com fila < 20 (limiares a calibrar).
- Degradação graciosa: enquanto o desktop não tiver capacidade de OCR, treina.

## Divisão do trabalho restante

- **Sessão autoresearch (eu):** branch do fork p/ 8 GB (DEPTH 4, MAX_SEQ_LEN
  menor, TinyStories) e instalar como modo-treino do despachante no
  `desktop-wsl` (`ssh desktop-wsl`, acesso já fechado — ver update das 19h05).
- **Sessão SuperSec:** (1) Paddle-GPU/serviço pdf-engine no WSL do desktop
  (o "meio dia" do plano da frota); (2) **endpoint `queue-status`** barato
  (contagem de docs pendentes da faixa pesada) p/ o despachante consultar —
  complemento natural do fleet-status. Lembrete: a ingestão capturando
  `needs_ocr`/`file_size_bytes`/`page_count` (pedido do supersecamd) é o que
  permite "fila pesada" bem definida.
- **Depois:** plugar a checagem de fila no despachante (qualquer sessão).

## Refinamento (~20h): modo diurno capado no desktop

A máquina fica ociosa a maior parte do dia (browser/escritório não usam GPU).
Decisão do Pedro: ela trabalha TAMBÉM de dia, com tetos que tornam o trabalho
imperceptível. Hierarquia final:
`usuário precisa da GPU (recua) > fila SuperSec > treino (dia capado / noite
cheio) > ocioso`. Tetos: `.wslconfig` memory=14GB processors=20;
`nvidia-smi -pl 130` 07h / `-pl 200` 18h (Task Scheduler, admin); `nice 19`;
back-off por amostragem de GPU (~10s a cada 10 min; browser não dispara, jogo
dispara). Implantação dos tetos = sessão de Code DO DESKTOP (precisa de
Windows admin p/ o power limit e `wsl --shutdown` p/ aplicar o .wslconfig).

## Notas

- Janelas divergentes: Task Scheduler do desktop = 19h–6h30; memória SuperSec
  fala 18h–07h + fins de semana. Unificar quando o despachante entrar
  (sugestão: 18h–07h seg–sex + sáb/dom integral, e o guardião de teclado cobre
  o resto).
- Tailscale no Mac M4: o problema de DNS que travava a API foi RESOLVIDO
  (`tailscale up --reset --accept-dns=false`) — a nota "Tailscale não pode
  rodar no Mac" na memória do SuperSec está desatualizada.
