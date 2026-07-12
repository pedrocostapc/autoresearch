# UI do cérebro agora é site: https://pedros-mac-mini.tail4f0062.ts.net

**Sessão:** autoresearch (Mac mini), 2026-06-12 ~18h40.

Pedro pediu "virar um site pra eu acompanhar". Decisão: NÃO Vercel (dados
vivem no Mac, fora do git, com info interna de clientes) — publicado na
tailnet via `tailscale serve` (HTTPS, só dispositivos da rede risenmidia).

- Servidor agora é launchd `com.pedro.cerebro-ui` (RunAtLoad + KeepAlive):
  sobe com o Mac, reinicia se cair. Log: /tmp/cerebro-ui.log.
  Gerenciar: `launchctl kickstart -k gui/501/com.pedro.cerebro-ui` (restart)
  / `launchctl bootout gui/501/com.pedro.cerebro-ui` (parar).
- Desligar a publicação: `tailscale serve --https=443 off`.
- Pendente Pedro: instalar app Tailscale no celular (login risenmidia) pra
  acessar de fora.
- Nota: o Mac mini está com "Use Tailscale DNS" desligado localmente — o
  nome .ts.net não resolve DESTE Mac (use localhost:8765 aqui). Outros
  dispositivos da tailnet resolvem normal (verificado via 100.100.100.100).
