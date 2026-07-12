# escalate virou piso global "nunca inventa" (ai-reply DEPLOYADO)

2026-06-15 — risen-ai-connect, main c8921d3 + ai-reply deployado em prod.

ATENÇÃO sessão do feat-task-manager-v3: a semântica do escalate MUDOU.

- `escalate` + bloco "nunca inventa" agora SEMPRE injetados no ai-reply (todo tenant),
  não mais gated por allow_escalate.
- `allow_escalate` (mesma coluna) agora = "avisar o cliente":
  - true  = manda stall "vou chamar um atendente" + cria tarefa;
  - false = silêncio (vácuo) + cria a MESMA tarefa (retorna suppressed reason=escalated_silent).
- stall reescrito p/ "vou chamar um atendente" (nunca "eu confirmo").
- UI: novo EscalateNotifyToggleCard; Butler + Aprendizado de IA movidos do Avançado
  pro Motor > Comportamento (SettingRow compacto). Avançado ficou só edição manual de persona.
- Pedro manteve os 54 tenants em vácuo (notify off), sem mudar dados.

Se o v3 mexe em ai-reply/index.ts ou _shared/escalation-tool.ts, rebasear na main atual.
