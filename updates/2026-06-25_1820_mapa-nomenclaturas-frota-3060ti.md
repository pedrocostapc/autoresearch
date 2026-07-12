# Mapa de nomenclaturas da frota (3060ti) — fim da confusão de nomes

2026-06-25 — referência durável salva em `lab/knowledge/wiki/mapa-nomenclaturas-frota.md`.

ATENÇÃO qualquer sessão que for acessar/arrumar as workers: **uma caixa física tem 3 nomes;
a WSL dentro dela tem 4 — e um colide com o hostname do host.** Por isso agentes ficam
"perseguindo o próprio rabo".

Resumo do que trava:
- **windows-3060ti** (host, `100.119.113.48`, alias `desktop-win`) e **linux-win-3060ti**
  (a WSL Ubuntu-24.04 onde roda o worker, `100.83.140.76`, alias `desktop-wsl`, user `risen`)
  são a MESMA caixa. Ambos têm hostname `DESKTOP-8H46QNV` (a WSL herdou) → indistinguíveis por
  `hostname`/log.
- Os nomes `*-3060ti` só existem no painel Tailscale (MagicDNS), não dentro da máquina.
- Os aliases `desktop-win`/`desktop-wsl` só existem no `~/.ssh/config` do Mac.
- A WSL estava **Stopped** → `100.83.140.76` offline (timeout), parecia sumida.
- **`amd-ryzen5` (`100.72.133.74`) é a máquina do pdf-engine, SEPARADA** — não é o 3060ti.

Atalho infalível: `wsl.exe -l -v` no host; se listar `Ubuntu-24.04`, você JÁ está na
windows-3060ti → rode local `wsl.exe -d Ubuntu-24.04 -u risen -- ...` (sem SSH).

Reorg proposta (no doc): itens seguros 1/2/5 (hostname da WSL via /etc/wsl.conf, `tailscale
set --hostname`, marcadores WHEREAMI) sem reboot; itens 3/4 (hostname Windows, aliases do Mac)
= decisão do Pedro.
