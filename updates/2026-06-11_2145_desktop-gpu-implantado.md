# Desktop GPU implantado: pdf-engine CUDA + dashboard + despachante

**Sessão:** autoresearch (Mac mini), 2026-06-11 ~21h45. Continuação dos
updates de 19h05 e 19h35. Contexto: Pedro vai criar um cliente novo no
SuperSec com ~20.000 arquivos — o desktop precisava virar capacidade de OCR.

## O que está NO AR agora (tudo verificado)

1. **pdf-engine com Paddle GPU no desktop-wsl** — `systemd pdf-engine.service`
   (enable, restart always, MemoryMax=8G), `/opt/pdf-engine`, venv com
   `paddlepaddle-gpu` cu126. `PADDLE_DEVICE=gpu`, `PADDLE_CHUNK=8`, WORKERS=6.
   Teste real de /ocr: conf 94,6, engine=paddle, deskew ok.
   Token PRÓPRIO da instância (não é o PDF_SERVICE_TOKEN da frota):
   `/opt/pdf-engine/.env` na máquina; cópia em `/tmp/pdf-engine-desktop-token.txt`
   no Mac do Pedro.
2. **URL pública (Funnel)**: `https://desktop-wsl.tail4f0062.ts.net` —
   /health público respondendo. ACL nodeAttrs funnel agora inclui
   100.83.140.76 (aprovação explícita do Pedro).
3. **Dashboard da frota**: `fleet-status` v3 deployada (aprovação explícita)
   com a entrada `pdf-engine-gpu` lendo secret `PDF_SERVICE_URL_GPU` (setado).
   Verificado online no painel. Commit na branch `feat/custo-llm-usage` do
   repo SuperSec (1 arquivo, aditivo).
4. **Despachante** em `~/night/job.sh` (placeholder backup em
   `job.placeholder.bak`): fila SuperSec > treino, histerese 100/20, recuo se
   usuário usar GPU, `nice 19`. Fila lida de `~/night/queue-status.url`
   (JSON {"pending": N}) ou `~/night/QUEUE_OVERRIDE` (número, manual) —
   **sem nenhum dos dois = treina**.
5. **Modo-treino**: branch `gpu-3060ti-8gb` no fork
   (pedrocostapc/autoresearch) — DEPTH 4, MAX_SEQ_LEN 512, VOCAB 4096,
   TOTAL_BATCH 2^15, WINDOW "L", TinyStories via `prepare_tinystories.py`.
   Clonado em `~/autoresearch` no desktop-wsl (uv sync ok). **Smoke test
   APROVADO (22h05): val_bpb 0.501262**, GPU 100%, 5,3 GB VRAM (sem OOM),
   ~220k tok/s, loss 8,3→2,1 nos 5 min. Obs.: stalls periódicos de ~9s a
   cada ~37 steps (interferência WSL/Windows?) — investigar depois, não
   bloqueia. Log completo: `~/night/logs/smoke.log` na máquina.

## IMPORTANTE p/ a sessão SuperSec — como usar a GPU nos 20k arquivos

A máquina NÃO está na rotação do pdf.ts (decisão pendente do Pedro). Para
colocar: ou setar o token da instância = PDF_SERVICE_TOKEN da frota (na
máquina: `/opt/pdf-engine/.env`, depois `systemctl restart pdf-engine`), ou
ensinar o pdf.ts a usar token por máquina. URL: a do Funnel acima.
Capacidade esperada: Paddle GPU 10–20× o supersecamd na faixa pesada.
**Falta também o endpoint `queue-status`** ({"pending": N} da faixa pesada)
p/ o despachante ceder a GPU automaticamente quando a fila crescer —
sem ele, usar `~/night/QUEUE_OVERRIDE` manualmente no dia do processão.

## Pendências

- [x] ~~Smoke test train.py~~ — APROVADO, val_bpb 0.501262 (22h05)

## AUDITORIA DA NOITE 11→12 (escrita 12/06 manhã): NÃO TREINOU

Causa raiz descoberta: **o WSL termina a distro quando o último cliente
wsl.exe/ssh desconecta — serviços systemd internos (tailscaled, pdf-engine,
tmux) NÃO contam como uso.** Timeline: 18:59 placeholder subiu (job.sh ainda
era o antigo na hora do Task Scheduler); 21:47 despachante lançado via ssh e
o WSL morreu segundos depois (nenhum "DESPACHANTE inicio" no log; zero
train_*.log). O stop.sh das 06:30 rodou no vazio. Implicação ADICIONAL: o
pdf-engine público fica intermitente de dia (nó some entre revives do
KeepAlive de 5 min) — precisa estar resolvido ANTES de entrar na rotação
dos 20k arquivos.

Correções (FEITAS 12/06 ~13h30):
- [x] **Causa raiz real**: a tarefa WSL-KeepAlive tinha só gatilho AtStartup
      (LastRun=1999) → nunca rodou sem reboot. Sessão do desktop consertou:
      gatilho de tempo a cada 5 min + `.wslconfig vmIdleTimeout=-1` (WSL nunca
      desliga por ociosidade). HOLDER no start.sh também entrou (defesa extra).
- [x] **SSH do Windows DESTRAVADO** — chave `desktop-recovery` (gerada pela
      sessão do desktop, fingerprint SHA256:2YvJIm6k8cNV6nDQ6PaGuZbwB+7/
      ozzVtvsWDbmiiCc, confirmada pelo Pedro). Alias `desktop-win` no
      ~/.ssh/config do Mac → acesso admin ao Windows independente do WSL.
      Shell é cmd.exe: um comando por conexão, sem `;`.
- [x] **Tetos diurnos**: `nvidia-smi -pl 130` aplicado agora; tarefas
      GPU-PowerCap-Day (07:00, 130W) e -Night (19:00, 200W) registradas.
- [x] Despachante relançado capado (treino real, modo treino — sem sinal de
      fila ainda). Janela 19h agora roda num WSL resiliente.
- [x] **Tmux → systemd (12/06 ~15h45)**: o tmux 'night' ainda ficava órfão
      quando o WSL oscilava (3 experimentos e parava). Trocado por
      `night-train.service` (Restart=always, User=risen, enable --now) —
      treino contínuo 24/7, reinicia sozinho em 10s se cair. STOP virou PAUSA
      (não encerra o serviço). Tarefas NightWorker-Start/Stop do Windows
      DESABILITADAS (lançavam tmux → dupla carga na GPU). Intensidade dia/noite
      segue nas GPU-PowerCap-Day/Night. job.sh antigo em job.dispatcher-tmux.bak.
      Instalação feita pelo caminho desktop-win (WSL direto estava intermitente):
      `wsl -u root -- bash /mnt/c/night/install-night-service.sh`.
- [x] **WSL-Holder (12/06 ~16h) — o conserto FINAL**: mesmo com systemd, o
      treino morria a cada ~5 min porque o WSL inteiro desligava (vmIdleTimeout
      NÃO é honrado fora de networkingMode=mirrored; KeepAlive só rodava
      /bin/true). Solução: tarefa `WSL-Holder` (ONSTART, sempre rodando) com
      `C:\night\wsl-holder.cmd` = loop que mantém `wsl -- sleep infinity`
      atachado e reconecta em 5s se a VM cair. Resultado VERIFICADO: serviço
      sem ciclar desde 16:07, GPU sustentada 99% por >7min, experimento
      completo às 16:12:44 (4º val_bpb). PROBLEMA RESOLVIDO — treino contínuo.
- [x] **GPU-PowerCap-Auto (a cada 15min)**: reaplica 130W(dia)/200W(noite) —
      o reset de driver no ciclo do WSL revertia p/ 220W. Agora persistente.
- [x] **Compartilhamento adaptativo (12/06 ~16h30)** — pedido do Pedro: "quanto
      mais o usuário usa, menos o agente usa". `C:\night\adaptive-share.ps1`
      (tarefa GPU-AdaptiveShare, ONSTART/sempre, lê a cada 15s):
      sinal do usuário = NVENC/NVDEC (encoder/decoder — o treino CUDA nunca usa,
      separação limpa e à prova de idioma). 3 faixas: OCIOSO=treina no teto do
      horário (130/200W); LEVE (enc/dec≥12%)=treina capado 110W; PESADO (≥40%)=
      PAUSA (touch STOP + pkill train.py → libera VRAM/GPU em segundos), retoma
      quando cai. Substituiu os 3 tetos fixos (Day/Night/Auto DESABILITADOS).
      Thresholds 12/40% ajustáveis no .ps1. Limitação honesta: VRAM/treino é
      tudo-ou-nada (não dá "30% de um treino") → daí pausar em vez de fatiar.
      Pura rasterização (jogo sem encode) não dispara o sinal de vídeo —
      cobertura futura se necessário. Log: C:\night\adaptive.log.
- [ ] **Pedro: revogar a API key do tailnet** (já cumpriu o papel; dá controle
      total — https://login.tailscale.com/admin/settings/keys)
- [ ] Pedro: `claude login` dentro do WSL p/ o loop COMPLETO do autoresearch
      (agente editando train.py à noite; sem isso o modo-treino repete o
      train.py base — útil como burn-in, não como pesquisa)
- [ ] Sessão SuperSec: queue-status + decidir entrada na rotação pdf.ts
- [ ] Sessão desktop (Windows admin): tetos diurnos (.wslconfig 14GB/20thr,
      nvidia-smi -pl 130/200 às 07h/18h via Task Scheduler)
