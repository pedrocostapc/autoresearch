# Ei Risen — balanço da sessão "Josemac não envia" (complementa o balanço 18:29 de iOS/IAP)

App: eirisen / repo `risen-ai-connect`. Sessão da tarde 06/07, foco único:
**por que a Josemac recebe mas nenhuma mensagem sai**. Diagnóstico FECHADO.

## PASSADO (o que esta sessão fez)
- **Diagnóstico fechado: erro 463 da Meta** (`NackCallerReachoutTimelocked`) — restrição
  anti-automação temporária aplicada pelo servidor do WhatsApp ao canal API do NÚMERO
  da Josemac. Não é CRM, não é Evolution, não é a instância. Prova em três pontas:
  self-send = SERVER_ACK ✅ · qualquer externo = ERROR ❌ (~200ms, via messages.update)
  · WhatsApp Web oficial envia normal. Não-entrega confirmada ponta-a-ponta (teste
  josemac→Risen Suporte nunca chegou no CRM do Suporte). Quadro idêntico a
  evolution-api#2588 (stub 463) e Baileys#2091. Doc completo:
  `prompts/josemac-envio-diagnostico/SESSAO-2-ACHADOS.md` (+ cópia global).
- **Derrubada a hipótese LID da sessão anterior**: TODOS os 14 tenants recebem
  `addressingMode: lid` (é o padrão novo do WhatsApp pra geral) e entregam — LID não
  discrimina nada. O "descartado: não é ban porque WA Web envia" do PANORAMA também
  caiu: o 463 é exatamente assim (oficial passa, Baileys não).
- **Acesso ao VPS da Evolution RECUPERADO**: porta 22 estava morta porque o IP do Pedro
  rotacionou (138.122.54.x) e o Cloud Firewall da DO (`fw-crm-evolution`) só tinha IPs
  velhos. Pedro adicionou regra SSH pro droplet api `64.23.220.240` = **jump fixo
  permanente** (chave `~/.ssh/id_ed25519_evolution`). Token DO novo no Bitwarden
  (`DIGITALOCEAN_API_KEY`, secret id d7f7a5b6-4950-49aa-8444-b47f0134e4a2); o antigo
  `DO_API_TOKEN` está morto (401).
- **Commits na main (7518255, 3329d3e, d5264e1)**: (a) `ackToStatus` mapeia ERROR→failed
  — CRM para de mentir "enviada" pra mensagem que o WhatsApp recusou; (b)
  `sync-contact-photos` com PAUSED_TENANTS (Josemac); (c) **freio de mão de envio**
  `_shared/send-pause.ts` + gates em provider-send-message / send-broadcast-now /
  dispatch-scheduled-broadcasts — TODO envio do tenant pausado morre no servidor com
  423 (cobre sessão logada que "escapou" da desativação de usuários); (d) canário
  `prompts/josemac-envio-diagnostico/canary-josemac.sh`.

## O QUE APRENDEU
- **463 existe e tem assinatura própria** (open+recebe+self-ack+externo-ERROR+oficial-ok).
  Gatilhos: lookups em massa (foto/onWhatsApp), broadcasts frios, re-pareamento
  frequente. Josemac: import de 5.000+ contatos + backfill de fotos em massa + conta
  já no device **:41**. Solta sozinho (relatos: horas a ~2 semanas); nada acelera.
- **O CRM não tinha como ver isso**: pipeline de ack está morto GLOBALMENTE —
  delivered/read nunca progridem pra nenhum tenant há 21+ dias (1 único read). O
  MESSAGES_UPDATE chega mas ERROR não era mapeado e delivered/read não aparecem.
  Backlog importante (é o "✓✓ mentiroso" do sistema inteiro).
- Evolution 2.3.7 + Baileys 7.0.0-rc.9 no VPS; apikey por instância também vive em
  `Instance.token` no Postgres local da Evolution; `Session.creds` é JSON duplo-encodado.
- Classificador do modo auto barra: instalar script persistente em prod, restart de
  instância, deploy de edge — mesmo com "pode" genérico do Pedro. Saída limpa: entregar
  comandos `!` prontos pro Pedro rodar.

## O QUE ERROU / BUGS
- **Meu**: mandei 2 comandos com typo/lentidão (`$APIKEEY`; `docker logs --since` em log
  de semanas = timeout) — refeito com captura `tail -0 -f` (rápida). Sem dano.
- **Da frota (não desta sessão, mas exposto aqui)**: (1) ack pipeline global morto
  (acima); (2) memória `reference_apply_migration_management_api` dizia token em
  `.env.local` — não está mais lá; o vivo é o Bitwarden (memória corrigir se recorrer);
  (3) EVOLUTION_API_KEY do Bitwarden dá 401 na Evolution (desatualizada — rotacionar).
- **RESOLVIDO nesta sessão**: SSH do VPS (firewall), CRM mentiroso (commitado),
  vazamento de tentativas de envio do tenant travado (freio).
- **AINDA ESPREITA**: o 463 em si (só a Meta solta); e o padrão que o causou pode se
  repetir em QUALQUER cliente novo com import grande → sprint "import seguro" desenhado.

## PRESENTE
- Josemac: instância `josemac-632281` CONECTADA e MUDA (decisão: não desconectar — perde
  registro e re-parear piora o score). IA/LGPD/leituras desligadas pelo Pedro; usuários
  serão DESATIVADOS pelo Pedro (quer que o sistema "não exista" até voltar). Time
  atende pelo WhatsApp oficial (que funciona).
- **PENDENTE DO PEDRO (2 comandos `!` já entregues no chat)**: (1) deploy das 5 edge
  functions (provider-webhook, sync-contact-photos, provider-send-message,
  send-broadcast-now, dispatch-scheduled-broadcasts); (2) instalar canário no VPS
  (cron 12:00 UTC) — testa 1x/dia e avisa o Pedro no WhatsApp via risen-suporte quando
  o número soltar, aí se desarma.
- Aparelho da loja: preso em "Sincronizando. Mantenha o app aberto" (Xiaomi matando o
  WhatsApp em background) — Pedro foi olhar; higiene recomendada.

## FUTURO
- **No destravamento (checklist)**: reativar usuários → tirar Josemac de
  SEND_PAUSED_TENANTS (`_shared/send-pause.ts`) e de PAUSED_TENANTS
  (sync-contact-photos) → redeploy 4 functions → religar IA → NÃO voltar a fazer
  varredura em massa nesse número.
- **Sprint "import seguro" (desenhado, aguardando ok do Pedro)**: foto lazy (só quem
  conversa + ao abrir ficha; importado fica de iniciais — Pedro aprovou a ideia),
  deployar o "adota jid" do sprint phone_match_key (escrito, nunca deployado),
  checagem 8/9 dígitos SOB DEMANDA no primeiro envio (1 lookup, com cache; mata a
  reclamação "fulano não está na lista" via phone_match_key sem tocar WhatsApp),
  carência pra número recém-pareado, broadcast só pra quem já conversou, telemetria
  de chamadas Evolution por número/dia.
- **Backlog herdado**: consertar delivered/read global; alarme automático de "tenant
  com envios ERROR em série" (o 463 teria sido pego dia 03, não dia 06).
- Médio prazo: Josemac é candidata a Cloud API oficial (sem 463) — lembrar do ponto
  cego (número Cloud API não espelha pra Evolution).
