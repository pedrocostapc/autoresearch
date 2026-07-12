# Playbook — worker noturno no DESKTOP-8H46QNV (escritório)

> Gerado a pedido do Pedro em 2026-06-11. Objetivo: a máquina do escritório
> (Ryzen 9 5900XT 16c, 24 GB RAM, RTX 3060 Ti 8 GB, Windows 11) trabalha fora
> do expediente — padrão "worker oportunista" (ver conversa SuperSec
> 2026-06-11 sobre M1 vs Ryzen). De dia ninguém percebe que ela tem segundo
> emprego.
>
> **Como executar:** abrir um Claude Code na própria máquina (passo 4) e colar
> este arquivo, ou seguir os passos manualmente. Cada passo é verificável.

## Convite do tailnet

```
https://login.tailscale.com/admin/invite/zPLHopUFH7XEG8L1Pczr11
```

(Convite gerado em 2026-06-11; se expirar, gerar outro em
https://login.tailscale.com/admin/users → Invite.)

## Passo 1 — Tailscale no Windows

1. Baixar e instalar: https://tailscale.com/download/windows
2. Abrir o link do convite acima no navegador da máquina e entrar com a conta
   do tailnet; depois logar no app do Tailscale com a mesma conta.
3. No ícone do Tailscale → Settings → **marcar "Run unattended"** — sem isso o
   Tailscale morre no logout/reboot e a máquina some da rede à noite.
4. Verificar: `tailscale status` no PowerShell deve listar a máquina e o Mac
   do Pedro. Anotar o nome MagicDNS (algo como `desktop-8h46qnv.<tailnet>.ts.net`).

## Passo 2 — Acesso remoto (SSH)

Tailscale SSH nativo não existe no Windows; usar o OpenSSH da Microsoft:

```powershell
# PowerShell como admin
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Set-Service sshd -StartupType Automatic
Start-Service sshd
```

Do Mac: `ssh <usuario-windows>@desktop-8h46qnv.<tailnet>.ts.net` — cai no
PowerShell; `wsl` entra no Ubuntu. Sem porta aberta no roteador: o tráfego só
existe dentro do tailnet.

## Passo 3 — Energia (a máquina não pode dormir à noite)

```powershell
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /h off
```

Monitor pode desligar à vontade (`monitor-timeout-ac` qualquer valor).
Custo de luz estimado rodando só as noites: ~R$ 50–80/mês.

## Passo 4 — WSL2 + Ubuntu + CUDA

1. Driver NVIDIA no **Windows** atualizado (Game Ready ou Studio recente).
   **Não** instalar driver NVIDIA dentro do WSL — o do Windows é compartilhado.
2. `wsl --install -d Ubuntu-24.04` (PowerShell admin; reiniciar se pedir).
3. Dentro do Ubuntu, verificar GPU: `nvidia-smi` deve mostrar a 3060 Ti.
4. Python + PyTorch (CUDA já vem na wheel):
   ```bash
   sudo apt update && sudo apt install -y python3-pip python3-venv git
   python3 -m venv ~/venv && source ~/venv/bin/activate
   pip install torch --index-url https://download.pytorch.org/whl/cu124
   python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
   # esperado: True NVIDIA GeForce RTX 3060 Ti
   ```
5. Claude Code no WSL (roda na assinatura Max — decisão de custos nº 2):
   `curl -fsSL https://claude.ai/install.sh | bash` e logar com a conta do Pedro.
6. WSL precisa sobreviver sem janela aberta: criar `/etc/wsl.conf` com
   `[boot]\nsystemd=true` e subir os jobs via Task Scheduler (passo 5), que
   inicia o WSL sozinho.

## Passo 5 — Janela noturna (Task Scheduler)

Dois agendamentos, rodando "whether user is logged on or not":

- **19:00 — start**: `wsl.exe -d Ubuntu-24.04 -- /home/<user>/night/start.sh`
- **06:30 — stop**: `wsl.exe -d Ubuntu-24.04 -- /home/<user>/night/stop.sh`

Contratos dos scripts (escrever junto com a primeira carga):

- `start.sh`: remove `~/night/STOP`, sobe o worker em `tmux`/`nohup`, loga em
  `~/night/logs/<data>.log`.
- `stop.sh`: cria `~/night/STOP`. O worker **checa o arquivo entre jobs** e
  encerra graciosamente — o experimento/documento em andamento termina antes
  de parar (ninguém pega a máquina "quente" às 7h).
- Sensor extra (opcional, fase 2): pausar se houver input de teclado/mouse —
  para desktop com horário fixo de escritório, a janela 19h–6h30 já basta.

## Passo 6 — A carga noturna (decisão pendente do Pedro)

As duas candidatas brigam pela mesma GPU; começar com UMA para validar:

| Carga | O que roda | Observações |
|---|---|---|
| **OCR SuperSec** | Paddle com CUDA processando a fila pesada do dia | Retorno direto no negócio; 10–20× mais rápido que o Paddle-CPU atual; recompilar/instalar `paddlepaddle-gpu` no WSL |
| **autoresearch** | loop overnight na 3060 Ti (custo zero vs US$ 20/noite H100) | 8 GB de VRAM: reduzir `DEPTH` 8→4, `MAX_SEQ_LEN` menor, dataset TinyStories (guia no README do upstream); resultados só comparáveis dentro da mesma máquina |

Dá para empilhar depois: OCR até esvaziar a fila → autoresearch no resto da
noite.

## Estado verificado em 2026-06-11 ~14h (do Mac mini)

Tailnet de pé (conta `risenmidia@`) com QUATRO máquinas: `pedros-mac-mini`
(100.80.109.34), `desktop-8h46qnv` (**100.119.113.48**),
`macbook-air-de-risen` (100.65.112.66) e `pdf-engine` (100.72.133.74, linux —
o motor OCR do SuperSec já está na malha).

- OpenSSH instalado no desktop e **porta 22 aberta** (o capability travou em
  `InstallPending`; destravou com reboot de verdade + DISM).
- **Armadilha de DNS do tailnet**: há um nameserver global cadastrado que não
  responde — com o Tailscale ligado, Claude/internet "travam". Contorno
  aplicado no Mac: `tailscale up --reset --accept-dns=false`. Corrigir na
  fonte em https://login.tailscale.com/admin/dns (Override local DNS).
  No Windows o contorno é `tailscale set --accept-dns=false`.
- Passos 1–5 + chave SSH do Mac: delegados a uma sessão de Claude Code rodando
  no próprio desktop (prompt autocontido entregue ao Pedro em 2026-06-11 ~14h;
  relatório esperado em `C:\night\SETUP-REPORT.md` na máquina).

## ACESSO FECHADO — estado final 2026-06-11 ~19h

**Acesso autônomo funcionando**: `ssh desktop-wsl` do Mac (alias em
`~/.ssh/config` → `risen@100.83.140.76`, Tailscale SSH, sem chave gerenciada).
Verificado por dentro: RTX 3060 Ti 8 GB (driver 591.86), torch 2.6.0+cu124
com `cuda: True`, estrutura `~/night/` (start.sh, stop.sh, job.sh, logs/)
pronta. Tarefas NightWorker-Start 19:00 / NightWorker-Stop 06:30 validadas
ponta a ponta pela sessão do desktop (relatório em `C:\night\STATUS-REPORT.md`).

Como foi fechado (para replicar): ACL do tailnet `ssh.action: check→accept` e
auth key pré-autorizada geradas **via API** (`api.tailscale.com/api/v2`, com
aprovação explícita do Pedro); no desktop,
`wsl -u root -- tailscale up --authkey=... --ssh --hostname=desktop-wsl
--accept-dns=false` + `systemctl enable --now tailscaled`.

Armadilhas registradas (Windows PT-BR):
- `icacls` com `Administrators`/`SYSTEM` falha — usar SIDs `*S-1-5-32-544` /
  `*S-1-5-18` (funciona em qualquer idioma).
- O OpenSSH nativo do Windows recusou a chave mesmo com
  `administrators_authorized_keys` correto (suspeita: `Match Group
  administrators` não casa com o grupo localizado "Administradores").
  Abandonado em favor do Tailscale SSH no WSL.
- `nvidia-smi` no WSL fica em `/usr/lib/wsl/lib/` (fora do PATH não-interativo).
- O WSL se auto-desliga ocioso; o KeepAlive revive a cada 5 min → SSH diurno
  pode falhar na 1ª tentativa (retentar). Polimento opcional: `.wslconfig`
  com `[wsl2] vmIdleTimeout` alto. À noite o job mantém o WSL vivo.

## Pendências

- [x] ~~Decidir a primeira carga~~ — DECIDIDO (Pedro, 2026-06-11 ~19h30):
      **política de frota por demanda** — `usuário > fila SuperSec > treino >
      ocioso`. O job.sh vira DESPACHANTE: com fila pesada no SuperSec → modo
      OCR; sem fila → modo treino (autoresearch). Histerese na troca; decisão
      sempre entre unidades de trabalho. Ordem de implantação:
      (a) autoresearch 8 GB como modo-treino (sessão autoresearch);
      (b) Paddle-GPU no WSL + endpoint queue-status (sessão SuperSec);
      (c) plugar a checagem de fila no despachante.
- [ ] **Modo diurno capado** (refinamento Pedro 2026-06-11 ~20h — a máquina
      fica ociosa de dia; browser não usa GPU): `.wslconfig` com memory=14GB
      processors=20 (aplicar exige `wsl --shutdown`); Task Scheduler:
      `nvidia-smi -pl 130` às 07h / `-pl 200` às 18h (admin, no Windows);
      treino com `nice 19`; back-off se usuário usar GPU de verdade (pausar
      treino ~10s a cada 10 min e medir util; >20% = recuar 30 min).
      Com isso a janela vira ~22h/dia (dia capado + noite cheia).
- [ ] **Pedro: revogar a API key do tailnet** usada no setup
      (https://login.tailscale.com/admin/settings/keys) — ela dá controle total
- [ ] Se a carga for autoresearch: branch no fork com hiperparâmetros p/ 8 GB
- [ ] Opcional: sshd do Windows está com LogLevel VERBOSE (reverter p/ INFO);
      OpenSSH→Windows como acesso redundante segue quebrado (dispensável)
- [ ] Opcional: `.wslconfig` com vmIdleTimeout para acesso diurno estável
