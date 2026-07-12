# Cérebro comum + secrets no cofre + frota agregada

Pra TODAS as sessões: mudou a base de como a gente trabalha. **Releia o
`~/.claude/CLAUDE.md`** (novo — carrega em todo projeto) e o `~/.claude/frota/<seu-app>.md`.

## Secrets = Bitwarden AO VIVO (zero cópia em disco)
- **NUNCA** leia secret do `.env.local` nem hardcode. Busque **ao vivo** do Bitwarden
  (`bws`, token no Keychain `bws-access-token`). Se o `.env.local` estiver comentado/vazio,
  é ESPERADO — vá no cofre. É pra isso que o Pedro paga o Bitwarden.
- `SUPABASE_ACCESS_TOKEN` está no cofre (secret ID `397251ce-20b0-423d-b31f-b4780170a76f`).
- `~/Dev/risen/risen-read.sh` foi corrigido pra puxar o PAT do Bitwarden ao vivo — voltou a
  funcionar mesmo com o `.env.local` comentado.
- Mapa de secrets (nomes): `~/Dev/risen/mapas/SECRETS-INVENTORY.md`. Receita: `lab/skills/subir-chaves-bitwarden.md`.

## Pasta mãe agregada = ~/.claude/
- `~/.claude/CLAUDE.md` = o COMUM (todo projeto). `~/.claude/frota/<app>.md` = briefing
  específico de cada app: core, agencia (Hub Mídia OOH), eirisen, risenos, supersec,
  minhaobra, nafazenda. Descubra seu app pela pasta e leia o `frota/<app>.md`. Some com
  CLAUDE.md espalhado pelos repos.

## Core fiscal (safra desta janela)
- **Core stateless**: dado sensível (cert/cred/notas/boletos/extrato) vive no APP, viaja no
  payload. **TEMPLATES fiscais** (NFS-e/boleto) vivem no CORE (`core_nfse_templates`,
  `core_boleto_templates`); o Core APLICA na emissão e DECLARA o contrato (`v1-fiscal-templates`).
- NFS-e gov.br provada (A1+mTLS via relay BR); e-mail único nota+xml+boleto (`v1-notify`).
- Telas de "Modelos" no Hub (Financeiro → Boletos/Notas Fiscais) leem do Core via broker.

## E-mail do Pedro
- Ferramenta local `~/.risen-mail/mail.py` lê os 4 Gmails (readonly). **Confidencial** —
  regras de privacidade no CLAUDE.md comum.
