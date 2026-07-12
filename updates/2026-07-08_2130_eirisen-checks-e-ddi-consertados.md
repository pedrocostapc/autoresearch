# eirisen: ✓✓/✓✓-lido FUNCIONANDO pela 1ª vez + DDI 55 obrigatório no cadastro

Dois fixes de frota inteira (sessão 08/07 noite, continuação do caso Josemac):

1. **Acks de entrega/leitura estavam TODOS sendo descartados desde sempre** —
   `messages.update` da Evolution v2 manda o id como `keyId`; o provider-webhook
   só lia `key.id`/`id` → nenhum tenant jamais viu ✓✓ (a UI MessageBubble sempre
   esteve pronta). Fix de 1 linha (main 4b2f03c, deployado); primeiro `delivered`
   da história registrado em prod (Construbase) minutos depois. Vale pra TODA a
   frota daqui pra frente; mensagens antigas ficam como estão.

2. **Cadastro de contato agora normaliza DDI 55 + DDD padrão no BANCO** (gatilho
   `contacts_normalize_phone`, migration 20260709000000, main 2c283fb): leigo
   digita "99865-4211" → sistema completa DDD do tenant (tenants.default_ddd) +
   55. Era a causa de "inicio conversa e dá X" (contato salvo sem 55 → jid
   inexistente). Validado ao vivo com contato novo na Josemac (X → sent ✓).
   **Fase 2 NÃO feita (decisão Pedro):** backfill dos 6.687 contatos antigos da
   frota sem normalização — avaliar depois.

Contexto Josemac: operando pelo FIXO (josemac-db0667) desde 08/07 manhã, 407
conversas migradas, envio validado; 1968 despareado em repouso (463), canário
vigiando; IA de resposta OFF até ~segunda (warm-up humano do fixo).
