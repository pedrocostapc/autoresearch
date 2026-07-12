# Nova máquina na frota OCR: Mac mini M1 (dedicada 24/7)

**Quando:** 2026-07-02
**Nó:** `mac-mini-m1` / tailnet `100.65.209.42` / hostname `Pedros-Mac-mini`
**Estado:** ✅ worker ativo, Apple Vision, launchd dedicado, auto-update ligado.

## O que ficou pronto
- Login por chave M4→mini fechado. **Gotcha:** a `id_ed25519` da M4 tem
  passphrase → `BatchMode` não assinava. Resolvido com
  `ssh-add --apple-load-keychain` (a passphrase já estava no Keychain).
- Alias no `~/.ssh/config` da M4: `Host mac-mini-m1 → HostName 100.65.209.42`
  (**MagicDNS não resolve da M4** — nem o nome curto nem o FQDN; usar o IP tailnet).
- `~/ocr-fleet/.env` montado do **Bitwarden** (SUPABASE_URL, SERVICE_ROLE_KEY,
  WORKER_SECRET) + WORKER_NAME=mac-mini-m1, POLL_SECS=5, TENANT_ID default.
  Nunca passou valor pelo chat: `risen-secrets pull` → grep das 3 linhas → scp.
- Arquivos da frota via **rsync** da M4 (mini **não tem deploy key do GitHub** e
  não precisa — auto-update é via bucket Supabase). Bootstrap rodado com
  `REPO_DIR` pré-populado.
- `bootstrap.sh` OK (uv+Python 3.12, frota-venv, ocrmac/Apple Vision, paddle CPU),
  serviço launchd `com.risen.ocrworker` (**run.sh dedicado**, KeepAlive+RunAtLoad)
  + updater diário 04:00. `pmset -a sleep 0 disablesleep 1` (24/7).
- Worker conectou na fila do tenant c55fd91e e chegou em `fila vazia, aguardando…`.

## Bug de bootstrap encontrado (patchado à mão, falta corrigir no repo)
`bootstrap.sh` copia `run.sh`/`run-idle-gated.sh` pro `~/ocr-fleet` mas **NÃO copia
`update.sh`**. O `worker.py` (farol, ~a cada 60s) roda `~/ocr-fleet/update.sh` →
`No such file or directory` em loop no `worker.err`. Copiei o `update.sh` à mão e
parou. **TODO no repo:** adicionar `cp "$FLEET/update.sh" "$RUNTIME/"` no passo 5
do `bootstrap.sh` (junto do worker.py/run.sh).

## Como alcanço
`ssh mac-mini-m1` (alias já aponta pro IP). Logs em `~/ocr-fleet/worker.out|err`,
`update.out`, `bootstrap.log`. Doc de setup em texto puro no Dropbox:
`mac-mini-m1-worker-setup.txt`.
