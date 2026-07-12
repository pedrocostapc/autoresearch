# Acesso autônomo ao desktop do escritório — FECHADO ✅

**Sessão:** autoresearch (Mac mini), 2026-06-11 ~19h. Continuação de
`2026-06-11_1310_worker-noturno-desktop.md`.

## Resultado

Qualquer sessão neste Mac agora alcança a GPU do escritório com:

```bash
ssh desktop-wsl '<comando>'     # alias em ~/.ssh/config → risen@100.83.140.76
```

Verificado por dentro: **RTX 3060 Ti 8 GB** (driver 591.86), **torch
2.6.0+cu124, cuda=True** (venv em `~/venv`), `~/night/` com
start.sh/stop.sh/job.sh/logs e Task Scheduler 19:00/06:30 validado.
`nvidia-smi` no WSL: usar `/usr/lib/wsl/lib/nvidia-smi`.

## Como foi (resumo da novela)

1. OpenSSH nativo do Windows recusou chave mesmo com
   `administrators_authorized_keys` correto — suspeita de `Match Group
   administrators` vs grupo localizado "Administradores" (Windows PT-BR).
   Lição paralela: `icacls` exige SIDs (`*S-1-5-32-544`, `*S-1-5-18`) em
   sistemas não-ingleses. Caminho abandonado (fica como redundância quebrada).
2. Pedro forneceu **API key do tailnet** → daqui via `api.tailscale.com`:
   ACL `ssh.action: check→accept` (com aprovação explícita dele) + auth key
   pré-autorizada de 1 uso.
3. No desktop: `wsl -u root -- tailscale up --authkey=... --ssh
   --hostname=desktop-wsl --accept-dns=false` e depois
   `systemctl enable --now tailscaled` (sem isso o nó caía quando o WSL dormia).
4. Nó `desktop-wsl` = **100.83.140.76** no tailnet.

## Avisos operacionais

- **WSL ocioso se auto-desliga**; KeepAlive revive a cada 5 min → SSH diurno
  pode falhar na 1ª tentativa; retentar em ~30s resolve. À noite o job mantém
  o WSL vivo. Polimento opcional: `.wslconfig` com `vmIdleTimeout` alto.
- DNS do tailnet: global vazio, inofensivo. Mac e WSL rodam com
  `--accept-dns=false` por precaução (houve travamento de Claude/DNS antes).

## Pendências

- [ ] **Pedro:** decidir a primeira carga noturna — OCR SuperSec (Paddle CUDA)
      vs autoresearch (job.sh atual é placeholder nvidia-smi com contrato STOP)
- [ ] **Pedro:** revogar a API key do tailnet usada no setup
      (https://login.tailscale.com/admin/settings/keys)
- [ ] Se autoresearch: branch no fork com hiperparâmetros p/ 8 GB
      (DEPTH 8→4, MAX_SEQ_LEN menor, TinyStories)
- [ ] Opcional: sshd Windows com LogLevel VERBOSE → reverter p/ INFO
