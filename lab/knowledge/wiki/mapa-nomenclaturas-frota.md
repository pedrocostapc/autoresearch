# Mapa de nomenclaturas — frota OCR (por que os agentes se perdem)

> Confirmado 2026-06-25. **Uma caixa física tem 3 nomes; a WSL dentro dela tem 4 — e um
> colide com o hostname do host Windows.** Por isso agente que procura por um nome não acha
> pelos outros. Leia isto ANTES de tentar acessar/arrumar a máquina do 3060ti.
> Tailnet inteiro = `tail4f0062.ts.net`.

## 1. As duas "máquinas" são UMA caixa física + a WSL dentro dela

### A) O PC Windows (host)
| Camada | Nome | Onde existe |
|---|---|---|
| Hostname do Windows | `DESKTOP-8H46QNV` | dentro do Windows (`hostname`) |
| Tailscale HostName (auto) | `DESKTOP-8H46QNV` | reportado pelo SO ao Tailscale |
| Tailscale MagicDNS / admin | `windows-3060ti` | só no painel Tailscale → `windows-3060ti.tail4f0062.ts.net` |
| IP Tailscale | `100.119.113.48` | tailnet |
| Alias SSH | `desktop-win` | só no `~/.ssh/config` do **Mac** |

### B) A WSL (Ubuntu, onde roda o worker de OCR)
| Camada | Nome | Onde existe |
|---|---|---|
| Distro WSL | `Ubuntu-24.04` | `wsl -l -v` no Windows |
| Hostname do Linux | `DESKTOP-8H46QNV` ⚠️ | `/etc/hostname` na WSL — **herdado do Windows, idêntico ao host** |
| Tailscale HostName (pref local) | `desktop-wsl` | `tailscale debug prefs` na WSL |
| Tailscale MagicDNS / admin | `linux-win-3060ti` | painel Tailscale → `linux-win-3060ti.tail4f0062.ts.net` |
| IP Tailscale | `100.83.140.76` | tailnet |
| Usuário Linux | `risen` | dentro da WSL |
| Alias SSH | `desktop-wsl` | só no `~/.ssh/config` do **Mac** (via Tailscale SSH) |
| Como o worker se identifica no log | `linux-win-3060ti` | `journalctl -u ocr-worker` |

**Nó relacionado, SEPARADO:** `amd-ryzen5` (Tailscale HostName `pdf-engine`, `100.72.133.74`)
= é a máquina **pdf-engine**, NÃO o 3060ti. (Foi onde o SSH "amd-ryzen5" falhava: máquina
diferente, com seu próprio usuário.)

## 2. As 5 (+1) armadilhas
1. **WSL tem o MESMO hostname do host** (`DESKTOP-8H46QNV`). `hostname` ou o log não dizem se
   você está no Windows ou na WSL.
2. **O nome do tailnet não existe dentro da máquina.** `windows-3060ti`/`linux-win-3060ti` só
   no painel Tailscale. `grep 3060ti` na máquina não acha nada → conclui errado "não é aqui".
3. **`desktop-win`/`desktop-wsl` só existem no `~/.ssh/config` do Mac.** Agente rodando fora
   do Mac faz `ssh desktop-win` → "Could not resolve hostname".
4. **O agente não percebe que JÁ ESTÁ na máquina alvo** e tenta sair via SSH pra ele mesmo.
5. **WSL estava Stopped** → nó `linux-win-3060ti` offline → todo ping/SSH pra 100.83.140.76 dá
   timeout. Parece que "sumiu"; só não tinha bootado.
6. Até dentro da WSL diverge: pref local `desktop-wsl` vs tailnet `linux-win-3060ti`.

## 3. Atalho que SEMPRE funciona (dar pro agente)
- Identidade real do nó: `tailscale ip -4` + `tailscale status --json | grep DNSName`.
- Pra saber se o host tem a WSL: `wsl.exe -l -v`. Se listar `Ubuntu-24.04`, **você já está na
  windows-3060ti** — não precisa de SSH, é tudo local: `wsl.exe -d Ubuntu-24.04 -u risen -- ...`.

## 4. Reorg proposta (nome canônico por máquina = nomes do tailnet)
| # | Ação | Risco | Efeito |
|---|---|---|---|
| 1 | WSL parar de herdar hostname: `/etc/wsl.conf` → `[network]\nhostname=linux-win-3060ti` + `wsl --shutdown` | Baixo | mata a colisão #1 |
| 2 | `sudo tailscale set --hostname=linux-win-3060ti` na WSL | Baixo | alinha pref vs tailnet |
| 3 | Renomear Tailscale HostName / hostname do Windows p/ `windows-3060ti` | Médio (reboot) | HostName = MagicDNS no host |
| 4 | Renomear aliases SSH do Mac p/ bater com o tailnet (manter desktop-win/wsl como extra) | Baixo | um nome ponta a ponta |
| 5 | Marcador "você está aqui": `~/WHEREAMI.txt` na WSL + `C:\WHEREAMI.txt` no host | Nenhum | agente descobre onde está em 1 comando |

Itens 1, 2, 5 = seguros (sem reboot, sem mexer na rede do host). Itens 3, 4 = decisão do Pedro
(reboot / config do Mac).

## 5. ESTADO — aplicado 2026-06-25 (do M4, via `ssh desktop-win` → `wsl.exe`)
- ✅ **Item 1** — WSL `/etc/wsl.conf` ganhou `[network] hostname=linux-win-3060ti` + `wsl --shutdown`/reboot. `hostname` agora = **linux-win-3060ti** (colisão morta). Worker `ocr-worker` + `tailscaled` voltaram `active`. Backup em `/etc/wsl.conf.bak.*`.
- ✅ **Item 2** — `tailscale set --hostname=linux-win-3060ti` na WSL.
- ✅ **Item 4** — `~/.ssh/config` do Mac: nomes canônicos `linux-win-3060ti`, `windows-3060ti`, `amd-ryzen5` (com aliases antigos `desktop-wsl`/`desktop-win`/`pdf-engine` mantidos).
- ✅ **Item 5** — `WHEREAMI.txt` na WSL (`/home/risen/` + `/etc/motd`) e `C:\WHEREAMI.txt` no host.
- ✅ **Bônus** — `ssh amd-ryzen5` funciona como **`supersec`** (hostname real da caixa = `supersecamd`); é a pdf-engine/Escritório, máquina separada.
- ✅ **SSH direto na WSL** — `tailscale set --ssh` ligado; `ssh linux-win-3060ti` entra direto como `risen` (sem hop pelo host).
- ✅ **Autostart da WSL (GPU não cai mais)** — Tarefa Agendada do Windows **`KeepWSL-3060ti`** (gatilho: logon + repete a cada 10 min) roda `wsl -d Ubuntu-24.04 -u root /bin/true`, que boota a WSL; o systemd dela sobe `ocr-worker` + `tailscaled`. Desfazer: `Unregister-ScheduledTask -TaskName KeepWSL-3060ti -Confirm:$false`.
- ⏳ **Item 3** — hostname interno do Windows ainda `DESKTOP-8H46QNV` (renomear pede reboot = decisão do Pedro). O nome no tailnet (MagicDNS) já é `windows-3060ti`.
