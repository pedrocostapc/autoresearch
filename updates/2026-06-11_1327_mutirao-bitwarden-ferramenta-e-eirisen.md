# Mutirão Bitwarden: ferramenta de sync construída + EIRISEN parcial

> Criado: 2026-06-11 ~13:27 — sessão Claude Code em `/Users/pedrocosta/Dev` (mutirão Bitwarden)

Esta sessão **é** o mutirão Bitwarden que o `mapas/SECRETS-INVENTORY.md` (sessão Core)
pediu. Pedro quer um cofre central (Bitwarden Secrets Manager) com todas as keys e os
projetos lendo de lá. Abaixo o que já existe, pra ninguém refazer.

## Decisões do Pedro

- Produto: **Bitwarden Secrets Manager** (nuvem), organização **"Risen Midia"** (paga/trial).
- Estrutura: **1 projeto Bitwarden por app** (sem pool `shared`) — Pedro pediu separado.
- `.env` locais viram **gerados** a partir do Bitwarden (`pull`), não se edita à mão.

## Ferramenta construída — `~/Dev/risen/secrets-sync/`

- `risen-secrets.mjs` (Node puro, sem deps). Comandos:
  - `import` — sobe os `.env` locais mapeados pro Bitwarden (já rodado: 68 secrets, 8 projetos).
  - `push <projeto> [arquivo]` — **upsert genérico** de KEY=VALUE (arquivo, `./.env.push` ou
    stdin) num projeto Bitwarden; cria o projeto se não existir; trata rate-limit 429 sozinho.
    É o comando que cada sessão/projeto usa pra empurrar os próprios secrets.
  - `pull` — regenera os `.env` mapeados a partir do Bitwarden.
  - `status` — testa conexão e mostra o mapa.
- CLI `bws` 2.1.0 em `~/.local/bin/bws`. Token do machine account no **Keychain do macOS**
  (service `bws-access-token`) — nenhum projeto precisa de token próprio, o script lê de lá.
- `README.md`, `PROMPT-PARA-CADA-PROJETO.md` (prompt portátil pra colar no agente de cada repo)
  e `secrets-map.json` na mesma pasta.

## DESCOBERTA CRÍTICA (confirma e fecha a questão do inventário)

A Management API do Supabase (`GET /v1/projects/{ref}/secrets`) devolve o `value` de
cada Edge Function secret como **digest SHA256**, nunca o plaintext (write-only). Logo:
**não existe import automático dos secrets de backend** — confirmado em 23/23 do risenos.
Uma tentativa minha (`import-supabase`) chegou a subir 117 hashes inúteis; já foram
apagados 2 dos 6 projetos `supabase-*` lixo (eirisen/supersec/agencia/minhaobra ainda
existem com digests — **a apagar**, aguardando ok do Pedro por ser deleção).

→ Caminho correto: cada projeto **empurra** os próprios valores reais via `push`. O
agente do projeto também não lê o plaintext do painel; ele inventaria e o Pedro cola os
valores do dashboard. Por isso o `SECRETS-INVENTORY.md` (só nomes) é o mapa perfeito pra isso.

## Estado por projeto no cofre

- `.env` locais importados (reais): risen-root, supersec, super-secretaria-functions,
  risencore, risen-ai-connect, saas-erp-whats, newrisenos, pixel-perfect-replica.
- **EIRISEN** (criado nesta sessão): 11 chaves reais dentro — 9 da categoria A (do
  `.env`/`.env.local` do ai-connect: VITE_*, INTERNAL_FUNCTION_SECRET, SUPABASE_SERVICE_ROLE_KEY,
  CORDEIRO_JWT, SUPABASE_ACCESS_TOKEN) + APPLE_IAP_KEY_ID/APPLE_IAP_ISSUER_ID (do inventário).
  Inventário detalhado em `~/Dev/risen/secrets-sync/EIRISEN-INVENTORY.md`.

## Pendências

- [ ] **Pedro:** colar os ~24 valores da categoria B do EIRISEN (Stripe live, EVOLUTION_API_KEY,
      Anthropic, Deepgram, Resend, RISEN_CORE_*, crons…) do painel Supabase `qbclqjkvovfriuhshkpw`
      → Edge Functions → Secrets. Eles **não** existem em arquivo local; só no painel.
- [ ] Decidir APPLE_IAP_PRIVATE_KEY (.p8) e CRMWHATS_GOOGLE_SA_JSON (multi-linha, arquivos em
      `~/.config/risen` e `~/.appstoreconnect`): entram no cofre ou ficam só como arquivo?
- [ ] Apagar os 4 projetos `supabase-*` de digests restantes (aguarda ok — deleção).
- [ ] Replicar o fluxo pros outros 6 apps usando o `SECRETS-INVENTORY.md` como checklist.
- [ ] **Riscos do inventário a tratar na mesma leva** (flags do Core): rotacionar e remover o
      **PAT da conta no minhaobra** (`MANAGEMENT_ACCESS_TOKEN`/`Management API`, prioridade 1);
      guardar credenciais **Cora** (projeto órfão "Risen") e tokens **FocusNFe** órfãos no core.
- [ ] Confirmar se Stripe/Resend/Google/Anthropic duplicados entre apps são chaves DISTINTAS
      ou a MESMA copiada (flag 5 do inventário).
