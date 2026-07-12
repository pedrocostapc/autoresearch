# Frota de Máquinas — Guia Completo (OCR/extração distribuída, custo zero)

> Escrito 2026-07-01. Fonte da verdade sobre a frota de workers do Pedro. Qualquer projeto do
> ecossistema Risen pode LER isto pra entender a frota e, se quiser, DESPACHAR trabalho nela.
> A frota nasceu no SuperSec, mas o mecanismo é genérico (ver §7 e §9).

## 1. O que é
Um **pool de computadores** (Macs + PCs) que lê documentos de graça — extrai texto de PDF nativo,
faz OCR de escaneado/imagem (inclusive **na GPU**), e devolve o RAW pro banco. Em vez de pagar OCR
na nuvem, usa **hardware ocioso** que o Pedro já tem. Cada máquina roda o mesmo programa burro
(`worker.py`) e puxa trabalho de uma **fila compartilhada**. Sem despachante central: é auto-organizado.

## 2. Como funciona (arquitetura)
- **Fila compartilhada** = tabela `extraction_jobs` no Postgres do projeto Supabase `abysijyuhvwrczxnwaqg`.
- **Worker burro** (`worker.py`, ~igual em toda máquina) roda em loop:
  1. **Reivindica 1 job atômico** — `POST rpc/claim_extraction_job {p_worker: <nome>}`. Usa `FOR UPDATE
     SKIP LOCKED` → dois workers nunca pegam o mesmo job. Re-reivindica jobs travados >10min.
  2. **Baixa os bytes** — `GET /functions/v1/doc-bytes?document_id=X` (a edge function baixa do Drive
     no servidor; **o worker não precisa de segredo do Google**). Auth: service-role + `x-worker-secret`.
  3. **Extrai** — roda um painel de engines: texto nativo (pymupdf, pdfplumber, pypdfium2, docling…) e,
     se o texto não vier (escaneado), **OCR** (Apple Vision no Mac / Paddle-CUDA na GPU / tesseract).
  4. **Devolve o RAW** — grava o texto (em `document_extractions` e/ou `documents.raw_data.raw`) e fecha
     o job (`extraction_jobs.status = done`, `engine_used`, `claimed_by`).
- **Distribuição = "claim-first"** (quem consulta a fila primeiro pega o job). Não há balanceamento: a
  máquina mais rápida/mais disponível abocanha mais. Máquina offline = 0.
- **A receita mora fora da máquina.** O worker é genérico; a receita de cada tipo de doc (extração
  estruturada) vem do bucket (`importers/<tipo>.py`), então dá pra mudar sem redeployar as máquinas.

## 2b. O painel de ferramentas (o que cada uma faz)
As 4 máquinas rodam o MESMO painel — **uniforme desde 2026-07-02** (antes o M1 rodava um venv pobre; ver §6).
Duas famílias. Custo zero, então roda várias e **une + consenso** (nenhuma engine sozinha manda).

**Texto — PDF nativo (rápido, sem imagem):**
| Ferramenta | O que faz | Onde |
|---|---|---|
| **pymupdf** (fitz) | leitor base rápido; também **rasteriza** a página pro OCR | todas |
| **pdfplumber** | texto + tabelas, bom em layout | todas |
| **pypdfium2** | engine do Chromium (PDFium), robusto | todas |
| **markitdown** | PDF → markdown (preserva estrutura) | todas |
| **pdftotext** | poppler `-layout`, preserva **COLUNAS** | todas *(Linux: apt · Macs: micromamba)* |
| **camelot** | extrai **TABELAS** (grades) | todas |
| **docling** | layout/estrutura rica (IBM) | todas |

**OCR — escaneado OU nativo-vetorial (sem camada de texto):**
| Ferramenta | Onde | Nota |
|---|---|---|
| **Apple Vision** (ocrmac) | **só Macs** (M1, M3) | melhor OCR grátis pra scan (~0,35s/pág) |
| **easyocr** | todas | |
| **tesseract** | todas | |
| **paddleocr** | GPU (3060ti/Linux) | 10-20× mais rápido na GPU |

**A regra de leitura (worker):** roda as engines de texto; se **nenhuma** deu texto → rasteriza
(`get_pixmap` 300dpi) e roda OCR. `pymupdf/pdfplumber` já dão consenso pro nativo; OCR é só pra imagem/vetorial.
> ⚠️ Melhoria pendente: a decisão de OCR hoje é "ALGUMA engine deu >40 chars?" — frágil (uma engine ruidosa
> como docling pode cuspir lixo e enganar → pular o OCR num PDF vetorial). O certo: decidir por **consenso** /
> texto real. (Caso que revelou: um boleto vetorial que o OCR lê perfeito, mas o docling enganou o check.)

**Instalar as ferramentas:** Linux (Ryzen5/3060ti) via apt + pip no venv. Macs sem Homebrew/sudo por SSH →
usar **micromamba** (binário único, sem sudo): `micromamba create -p ~/poppler-env -c conda-forge poppler` e
`export PATH="$HOME/poppler-env/bin:$PATH"` no run.sh. O resto (engines python) é `pip install` no `frota-venv`.

## 3. As máquinas (inventário + como alcanço cada uma)
Todas na mesma **Tailscale** (tailnet `risenmidia@`). Aliases SSH em `~/.ssh/config` do Mac mini (M4).

| Papel | Alias SSH | Endereço | SO / Hardware | Modo |
|---|---|---|---|---|
| **Orquestrador** | — | pedro-macmini-m4 | Mac mini M4 | onde o Claude roda; **NÃO é worker** |
| Worker Mac | `air-risen` | risenmidia@100.65.112.66 | MacBook Air **M1** | load-gate (§5) |
| Worker Mac | `macbookair-m3` | pedrocosta@192.168.1.132 | MacBook Air **M3** | load-gate (§5) |
| Worker Mac | `mac-mini-m1` | pedrocosta@100.65.209.42 | Mac mini **M1** 16GB | **100% dedicado** (pmset no-sleep) |
| Worker Linux | `amd-ryzen5` (=`pdf-engine`) | supersec@100.72.133.74 | Linux, Escritório (Ryzen 5) | **100% dedicado** |
| Worker GPU | `desktop-wsl` (=`linux-win-3060ti`) | risen@100.83.140.76 | **Ubuntu dentro do Windows** (WSL) | 100% dedicado |
| Casca do GPU | `desktop-win` (=`windows-3060ti`) | "Risen Midia"@100.119.113.48 | Windows 11 (Ryzen 9 + RTX 3060 Ti) | recuperação (§8) |

- Worker mora em `~/ocr-fleet/` (Mac) — `worker.py`, `run.sh`, `.env`, o supervisor do gate.
- Cada worker se identifica por `WORKER_NAME` (vira `extraction_jobs.claimed_by`).

## 4. Por que o Linux 3060ti está DENTRO do Windows (WSL)
A GPU (**CUDA**) acelera o OCR 10–20× — mas o stack de OCR na GPU (PaddleOCR-GPU, torch+cu124) é
**Linux**. A máquina física é **Windows 11** (é o desktop de trabalho). Solução: **WSL2** roda um
**Ubuntu dentro do Windows**, compartilhando o **driver NVIDIA do Windows** (não se instala driver no
WSL). Então:
- O **worker roda no Ubuntu (WSL)** — é o nó `linux-win-3060ti` na Tailscale.
- O **Windows é só a "casca"** — é o nó `windows-3060ti`, usado pra **recuperar** o WSL quando ele cai.
- Quando o WSL sobe, o `systemd` (`ocr-worker.service`) religa o worker sozinho.
- **Só a GPU faz diferença em ESCANEADO** (OCR). PDF nativo é CPU/texto — aí os Macs (Apple Silicon)
  ganham no claim-first.

## 5. O load-gate — a frota CEDE o computador ao usuário (só nos Macs)
Os Macs (M1, M3) são de uso pessoal, então o worker **educa-se** quando alguém está mexendo. Supervisor
`~/ocr-fleet/run-load-gated.sh` (lançado pelo launchd, sobrevive reboot). **3 estados:**

| Situação | Worker |
|---|---|
| Ninguém mexendo (ocioso ≥ `PRESENCE_SECS`) | **100%** (prioridade normal) |
| Usuário presente, uso do usuário < `USER_STOP_PCT` | **Educado** (background QoS via `taskpolicy -b`; usa só a folga) |
| Usuário presente, uso do usuário ≥ `USER_STOP_PCT` | **OFF** (worker sai fora, libera a máquina) |

- "**Uso do usuário**" = uso TOTAL da CPU **menos** o que a frota gasta (senão o worker dispararia o
  gate sozinho). Histerese: para em `USER_STOP_PCT`, volta em `USER_RESUME_PCT`.
- Presença = teclado/mouse nos últimos `PRESENCE_SECS` (via `ioreg` HIDIdleTime).
- Config no `~/ocr-fleet/.env`: `PRESENCE_SECS=60`, `USER_STOP_PCT=70`, `USER_RESUME_PCT=50`,
  `LOAD_POLL_SECS=10` (tunável, sem redeploy). Log das trocas de estado em `~/ocr-fleet/worker.out`.
- **Ryzen5 e 3060ti não têm gate** (ninguém mexe neles) → 100% sempre.

## 6. Como uma máquina ENTRA na frota (onboarding de um worker novo)
1. **Tailscale** instalado e logado na tailnet `risenmidia@` (pra ser alcançável).
2. **Código**: copiar a pasta `ocr-fleet/` (worker.py, run.sh) pra `~/ocr-fleet/`.
3. **Ambiente**: criar venv + `pip install -r requirements-frota.txt` (engines de texto/OCR).
   - Mac: Apple Vision já vem no SO. Linux GPU: PaddleOCR-GPU + torch cu124 no WSL (ver playbook).
4. **`.env`** em `~/ocr-fleet/.env` (contrato — ver §7). Mínimo: `SUPABASE_URL`,
   `SUPABASE_SERVICE_ROLE_KEY`, `WORKER_SECRET`, `WORKER_NAME` (único por máquina).
5. **Rodar como serviço** (pra subir no boot e reiniciar sozinho):
   - **Mac**: launchd `~/Library/LaunchAgents/com.risen.ocrworker.plist` (RunAtLoad + KeepAlive),
     `ProgramArguments` → `run.sh` (dedicada) **ou** `run-load-gated.sh` (com o gate do §5).
   - **Linux**: systemd `ocr-worker.service` (`systemctl --user enable --now` ou service de sistema).
6. Pronto: a máquina começa a puxar jobs da fila. Confere em `extraction_jobs.claimed_by`.

Playbook detalhado do desktop GPU (WSL+CUDA, SSH, agendamento):
`autoresearch/lab/knowledge/outputs/playbook-worker-noturno-desktop.md`.

## 7. Como DESPACHAR trabalho pra frota (pros OUTROS projetos)
A frota consome a fila `extraction_jobs` do projeto Supabase `abysijyuhvwrczxnwaqg`. Pra mandar um
documento pra frota ler, há **dois caminhos**:

**(a) Automático (o normal no SuperSec):** inserir o doc em `documents` → o trigger
`enqueue_extraction_on_document` cria o job em `extraction_jobs` sozinho (só p/ PDF/imagem).

**(b) Manual (despacho direto):** inserir uma linha em `extraction_jobs`:
```sql
insert into extraction_jobs (tenant_id, document_id, drive_file_id, status, priority, phase)
values (<tenant>, <document_id>, <id_do_arquivo_no_drive>, 'pending', 70, 1);
```

**O que o worker precisa pra ler o arquivo:** ele baixa os bytes via `GET /functions/v1/doc-bytes?
document_id=X`. Hoje o `doc-bytes` baixa **do Google Drive** (precisa de `drive_file_id`). Então o
documento tem que estar acessível por essa via. O RAW volta em `documents.raw_data.raw` /
`document_extractions`.

**Contrato de config do worker (`.env`):**
| Var | Pra quê |
|---|---|
| `SUPABASE_URL` | projeto Supabase (a fila) |
| `SUPABASE_SERVICE_ROLE_KEY` | escreve no banco + autentica no doc-bytes |
| `WORKER_SECRET` | autentica no doc-bytes |
| `WORKER_NAME` | identidade da máquina (claimed_by) |
| `POLL_SECS` | intervalo de polling (default 10s) |
| `TENANT_ID` | referência de tenant (hoje só num log; o claim NÃO filtra por tenant) |

## 8. Operação / recuperação
- **3060ti caiu?** `ssh desktop-win "wsl -d Ubuntu-24.04 whoami"` → boota o WSL → systemd religa o
  worker. Causa raiz "toda vez cai" = máquina dormia → resolvido com `powercfg /change
  standby-timeout-ac 0` (sleep na tomada = nunca). Comandos WSL sobre SSH: **quoting simples** (o shell
  do Windows quebra com aspas aninhadas).
- **Ver quem está na frota:** `select claimed_by, count(*), max(finished_at) from extraction_jobs group
  by claimed_by`.
- **Ver o worker vivo:** Mac `pgrep -f worker.py | wc -l` (o `-c` do pgrep NÃO existe no macOS);
  Linux `pgrep -c -f worker.py`.
- **Logs:** Mac `~/ocr-fleet/worker.out` (inclui as trocas do load-gate).

## 9. Limitações e como estender pra multi-projeto (via CORE)
- **Hoje a frota é 1-projeto**: a fila (`extraction_jobs`), o `claim_extraction_job` e o `doc-bytes`
  vivem no Supabase do **SuperSec**. Só o SuperSec despacha.
- **Regra da arquitetura Risen** (`~/.claude/CLAUDE.md`): inter-sistema é **SEMPRE via Core** (broker
  `v1-call`) — nada de app-a-app direto. Então a frota-multi-projeto **NÃO** é uma fila neutra que cada
  app cutuca direto; é uma **capability do Core**:
  1. o app chama o Core (`v1-call` → `v1-ocr-dispatch`) passando um **signed URL** do arquivo. O poster
     entrega o link fetchable → **a frota NÃO guarda credencial de projeto nenhum** (isso mata 80% da
     complexidade; some a necessidade de generalizar o `doc-bytes` pra cada Drive/OAuth).
  2. o Core insere o job numa **fila da frota no Core** (`fleet_jobs`, no Supabase do Core).
  3. os **workers apontam pra a fila do Core** (além da do SuperSec, durante a transição — dual-source
     pra não quebrar o SuperSec), baixam via `source_url` (HTTP GET), extraem, e escrevem o RAW em
     `fleet_jobs.result`.
  4. o app pega o resultado pelo Core (`v1-ocr-result` por poll, ou callback — OCR é pesado, assíncrono).
- **Ainda não construído.** Plano de execução detalhado:
  `lab/knowledge/wiki/plano-frota-multiprojeto-via-core.md`.
