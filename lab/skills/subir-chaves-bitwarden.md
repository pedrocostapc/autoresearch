---
name: subir-chaves-bitwarden
type: skill
status: candidate
created: 2026-06-12
nights_used: 0
source: ~/Dev/risen/secrets-sync/ (setup do Pedro, 2026-06-10/11)
---

Como subir chaves/secrets novos pro cofre Bitwarden Secrets Manager (org
"Risen Midia"). Use sempre que um secret novo aparecer num projeto, ou ao
rotacionar um vazado. REGRA: valor de secret NUNCA no chat — só em arquivo
local fora do git.

## Procedimento

1. A ferramenta é `node ~/Dev/risen/secrets-sync/risen-secrets.mjs`
   (token já está no Keychain como `bws-access-token`; ninguém precisa vê-lo).
2. Descubra o nome do projeto no cofre (um por app): `risen-root`, `supersec`,
   `super-secretaria-functions`, `risencore`, `risen-ai-connect`,
   `saas-erp-whats`, `newrisenos`, `pixel-perfect-replica` (+ `EIRISEN`,
   inventário em `~/Dev/risen/secrets-sync/EIRISEN-INVENTORY.md`).
3. Crie `./.env.push` na raiz do repo com `KEY=VALUE` (um por linha).
   - Valor que você (agente) tem acesso local (.env/.env.local): copie.
   - Valor que só existe em painel (Supabase/Lovable não devolvem plaintext):
     deixe `KEY=` e peça pro Pedro colar NO ARQUIVO, não no chat.
4. `node ~/Dev/risen/secrets-sync/risen-secrets.mjs push <PROJETO> ./.env.push`
5. Apague o `./.env.push` depois do push confirmado.
6. Para gerar os .env locais a partir do cofre: `... risen-secrets.mjs pull`
   (escreve só no arquivo primário `.env.local`, nunca em .env trackeado).
7. Chave compartilhada entre projetos (ex.: SUPABASE_ACCESS_TOKEN,
   STRIPE_SECRET_KEY): ao rotacionar, atualizar em TODOS os projetos que a
   contêm (busca por nome no Secrets Manager acha todas).

Prompt pronto pra colar em qualquer sessão:
`~/Dev/risen/secrets-sync/PROMPT-PARA-CADA-PROJETO.md`.
