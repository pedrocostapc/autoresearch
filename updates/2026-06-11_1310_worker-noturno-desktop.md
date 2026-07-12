# Worker noturno no desktop do escritório (Tailscale)

**Sessão:** autoresearch, 2026-06-11 ~13h10.

## O que foi pedido

Pedro recuperou a conversa "H100 vs 3060" (transcript da sessão autoresearch
48666f1b) e a "M1 vs Ryzen" (sessão SuperSec d74e1ca9) e decidiu avançar: o
desktop do escritório — **DESKTOP-8H46QNV, Ryzen 9 5900XT 16c, 24 GB RAM,
RTX 3060 Ti 8 GB, Windows** — fica parado fora do expediente e deve virar
worker noturno. Ele já criou o tailnet e mandou o convite (link dentro do
playbook).

## O que foi decidido

- Padrão "worker oportunista" (mesmo desenho feito para o MacBook Air na
  sessão SuperSec): Tailscale para alcance, janela de horário 19h–6h30 via
  Task Scheduler, parada graciosa por arquivo STOP entre jobs.
- Windows fica intacto para o expediente; jobs rodam em **WSL2 + CUDA**.
- Atenção: a conversa antiga assumia 3060 de 12 GB; a placa real é **3060 Ti
  de 8 GB** — para autoresearch, reduzir mais (DEPTH 8→4, MAX_SEQ_LEN menor,
  TinyStories).

## O que foi construído

- `lab/knowledge/outputs/playbook-worker-noturno-desktop.md` — passo a passo
  completo (Tailscale + Run unattended, OpenSSH Server, powercfg, WSL2 +
  PyTorch CUDA, Claude Code no WSL, Task Scheduler, contratos start/stop.sh)
  com o convite do tailnet embutido. Feito para colar numa sessão de Claude
  Code rodando na própria máquina.
- `lab/knowledge/wiki/pendencias-globais.md` e `lab/changelog.md` atualizados.

## Estado ao fechar (~14h)

- Tailnet (conta `risenmidia@`) com **4 máquinas**: pedros-mac-mini
  (100.80.109.34), **desktop-8h46qnv (100.119.113.48)**, macbook-air-de-risen
  (100.65.112.66) e **pdf-engine (100.72.133.74)** — o OCR do SuperSec já
  está na malha.
- OpenSSH no desktop instalado e **porta 22 aberta** (capability travou em
  `InstallPending`; saiu com reboot real + DISM).
- **Armadilha descoberta — DNS do tailnet**: nameserver global cadastrado que
  não responde; com Tailscale ligado, o Claude "trava". Contorno no Mac:
  `tailscale up --reset --accept-dns=false` (no Windows:
  `tailscale set --accept-dns=false`). Corrigir na fonte:
  https://login.tailscale.com/admin/dns. **Vale para o Air também.**
- Setup do desktop delegado a sessão de Claude Code rodando NELE (prompt
  autocontido entregue ao Pedro): chave SSH do Mac, energia, WSL2+CUDA,
  Task Scheduler 19h/6h30, job placeholder nvidia-smi com contrato STOP.
  Relatório esperado em `C:\night\SETUP-REPORT.md` (buscar por SSH).

## Pendências

- [ ] Sessão no desktop executar o prompt; Pedro repassar o `whoami`
- [ ] Mac: testar SSH por chave (`ssh <user>@100.119.113.48`) e ler o
      SETUP-REPORT.md
- [ ] **Pedro:** decidir a primeira carga noturna — OCR SuperSec (Paddle CUDA,
      retorno direto no negócio) **ou** loop autoresearch (custo zero vs
      US$ 20/noite de H100). Recomendação: validar com uma; depois empilhar
      (OCR até esvaziar fila → autoresearch no resto da noite).
- [ ] **Pedro:** corrigir o DNS do tailnet no admin console
- [ ] Se a carga for autoresearch: branch no fork com hiperparâmetros p/ 8 GB.
