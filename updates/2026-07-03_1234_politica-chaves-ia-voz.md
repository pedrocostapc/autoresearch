# Política: chaves de API de IA/voz só o Pedro provisiona (via UI)

**Decisão do Pedro (2026-07-03).** As chaves de terceiros no Bitwarden —
**Anthropic** (`ANTHROPIC_API_KEY`, `PERSONA_SIMULATOR_ANTHROPIC_KEY`),
**Deepgram / leitura de voz** (`DEEPGRAM_API_KEY`) e afins (Lovable AI etc.) —
pertencem ao sistema pra que foram criadas (hoje: **Ei Risen / CRM**).

**NENHUMA sessão/agente pode implementar, cablear, copiar ou reusar essas chaves
em OUTRO sistema sem autorização explícita do Pedro.** Ele SEMPRE provisiona as
chaves nos sistemas **pela UI do super admin**, ele mesmo.

Motivo: sessões paralelas (inclusive cloud/Lovable) estavam pegando a chave que já
existe e ligando em outros apps sem autorização — Pedro perde controle de onde a
chave roda (custo, rotação, escopo).

Se um app "precisa de IA/voz": NÃO pegue a chave existente, NÃO hardcode. A provisão
é decisão do Pedro, pela UI. Registrado em `lab/knowledge/wiki/decisoes-ativas.md` (#11).
