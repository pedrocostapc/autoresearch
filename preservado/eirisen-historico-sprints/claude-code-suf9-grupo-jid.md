# SUF9 — Envio pra grupos (fallback phone → JID)

> Sprint de fix curto. Hoje, mensagens enviadas pelo CRM (humano ou IA) pra
> conversations que são **grupos de WhatsApp** falham com
> `400 {"error":"Contact has no phone number"}`. Causa: grupos têm
> `whatsapp_jid` (`<id>@g.us`) mas `phone` é `null`, e o `provider-send-message`
> exige `phone` não-nulo.

---

## Contexto

### Sintoma observado em produção (09/05/2026)

Pedro tentou mandar mensagem em conversation de grupo. Front recebeu:

```
Edge function returned 400: Error
{"error":"Contact has no phone number"}

filename: supabase/functions/provider-send-message/index.ts
has_blank_screen: true
```

A mensagem é renderizada otimisticamente no inbox mas fica em
`status='failed'` com `provider_message_id=null` no banco. Em DM (contato
1:1 com phone) o envio funciona.

### Por que acontece

- **DMs (1:1):** contato tem `phone='553899526799'` e `whatsapp_jid='553899526799@s.whatsapp.net'`. `provider-send-message` valida `phone`, monta `{ number: phone, text }` e envia.
- **Grupos:** contato tem `phone=null` e `whatsapp_jid='123456789-1234567890@g.us'`. A validação de `phone` falha → 400 → mensagem nem é tentada.

A Evolution v2 aceita tanto número quanto JID no campo `number` da
`POST /message/sendText/{instance}`. Pra grupos, o que ela espera é o
JID inteiro (`...@g.us`).

### O que SUF9 entrega

`provider-send-message` (e o helper `sendTextViaEvolution` em
`_shared/evolution-client.ts` se aplicável) passa a derivar o destinatário
da seguinte ordem:

1. Se `contact.is_group=true` ou `whatsapp_jid` termina em `@g.us` → usa
   `whatsapp_jid` (JID inteiro) como `number`.
2. Senão, se `phone` existe → usa `phone`.
3. Senão, se `whatsapp_jid` existe → extrai a parte antes do `@` e usa
   como `number` (fallback pra DMs com phone null mas JID populado).
4. Se nada disso → 400 com mensagem clara: `Contact has neither phone nor whatsapp_jid`.

Sem mudança de schema. Sem migration.

---

## Escopo

### IN

- `supabase/functions/provider-send-message/index.ts` — lógica de validação
  e construção do destinatário.
- `supabase/functions/_shared/evolution-client.ts` — se a derivação de
  destinatário estiver lá, ajustar lá; senão deixar.
- Eventualmente as edges de broadcast (`send-broadcast-now`,
  `dispatch-scheduled-broadcasts`) — checar se têm a mesma validação rígida
  de phone e aplicar mesmo fallback.

### OUT (não tocar)

- Schema de `contacts` / `conversations`.
- UI do inbox.
- Lógica de recepção de mensagem (webhook).
- SUF8 paginação (já mergeado).
- SU8.3 captura de apikey (já mergeado).

---

## Pré-requisitos

- Branch nova a partir de `main`: `suf9-grupo-jid-fallback`.
- Build + tsc + vitest verdes antes de começar.
- Confirmar que `main` está pós-merge do SU8.3 (PR #186).

---

## Plano de execução

### Etapa 1 — Raio-x (sem codar)

Reportar antes de qualquer mudança:

1. **Onde mora a validação `Contact has no phone number`** em
   `provider-send-message/index.ts`. Reportar caminho + número da linha.

2. **Como o destinatário é montado hoje.** Provavelmente algo tipo
   `body: { number: contact.phone, text }`. Reportar a estrutura exata.

3. **Se `_shared/evolution-client.ts` (do SU8.1) tem a montagem do `number`**
   centralizada ou se cada edge monta por conta. Quero saber se o fix vai
   em 1 lugar ou em 3.

4. **Edges de broadcast**: `send-broadcast-now/index.ts` e
   `dispatch-scheduled-broadcasts/index.ts` — elas validam `phone` da
   mesma forma? Reportar trecho.

5. **Confirmar shape do contato grupo no banco.** Roda mentalmente:
   ```sql
   SELECT id, name, phone, whatsapp_jid, is_group
   FROM contacts
   WHERE is_group = true
   LIMIT 3;
   ```
   Esperar `phone=null`, `whatsapp_jid LIKE '%@g.us'`. Se algum grupo tiver
   phone populado por engano, anotar pra revisar dados depois (mas não bloqueia
   o fix).

Não codar nesta etapa. Reportar findings.

### Etapa 2 — Implementação

Sugestão de helper centralizado em `_shared/evolution-client.ts` (ou no
local apropriado conforme findings da Etapa 1):

```ts
type RecipientInput = {
  phone: string | null;
  whatsapp_jid: string | null;
  is_group: boolean | null;
};

export function resolveEvolutionRecipient(input: RecipientInput): string {
  const { phone, whatsapp_jid, is_group } = input;

  // 1) Grupo → JID inteiro
  const isGroupByFlag = is_group === true;
  const isGroupByJid = !!whatsapp_jid && whatsapp_jid.endsWith('@g.us');
  if (isGroupByFlag || isGroupByJid) {
    if (!whatsapp_jid) {
      throw new Error('Group contact missing whatsapp_jid');
    }
    return whatsapp_jid;
  }

  // 2) DM com phone
  if (phone && phone.length > 0) {
    return phone;
  }

  // 3) Fallback: extrair phone do JID
  if (whatsapp_jid && whatsapp_jid.includes('@')) {
    const localPart = whatsapp_jid.split('@')[0];
    if (localPart.length > 0) return localPart;
  }

  throw new Error('Contact has neither phone nor whatsapp_jid');
}
```

Aplicação:

- `provider-send-message`: substituir a validação atual de `phone` pela
  chamada de `resolveEvolutionRecipient`. O `body` da chamada Evolution
  passa a ter `number: resolveEvolutionRecipient(contact)`.
- Edges de broadcast: aplicar o mesmo helper se elas montam o destinatário
  por conta.
- Mensagem de erro 400 quando não houver nem phone nem JID deve ser clara
  (`Contact has neither phone nor whatsapp_jid`), não `Contact has no phone number`.

### Etapa 3 — Testes

**Unit (vitest)** em `_shared/evolution-client.ts`:

- `resolveEvolutionRecipient`:
  - `{ phone: '5538...', whatsapp_jid: '5538...@s.whatsapp.net', is_group: false }` → phone
  - `{ phone: null, whatsapp_jid: '123-456@g.us', is_group: true }` → JID inteiro
  - `{ phone: null, whatsapp_jid: '123-456@g.us', is_group: false }` → JID inteiro (detecta `@g.us`)
  - `{ phone: '5538...', whatsapp_jid: '...@g.us', is_group: true }` → JID inteiro (grupo ganha)
  - `{ phone: null, whatsapp_jid: '5538...@s.whatsapp.net', is_group: false }` → `5538...` (extrai do JID)
  - `{ phone: null, whatsapp_jid: null, is_group: false }` → throw `Contact has neither phone nor whatsapp_jid`
  - `{ phone: null, whatsapp_jid: null, is_group: true }` → throw `Group contact missing whatsapp_jid`

- **Build:** `bun run build` verde.
- **TSC:** `bunx tsc --noEmit` sem erros.
- **Vitest:** todos verdes.

### Etapa 4 — Smoke em produção

Após deploy:

1. **Mensagem em grupo (caso que falhava):** abrir conversation de grupo no
   inbox, mandar texto teste. Esperado: aparece com `status='sent'` e
   `provider_message_id` populado, mensagem chega no grupo no WhatsApp.

   ```sql
   SELECT id, sender, text, status, provider_message_id, created_at
   FROM messages
   WHERE created_at > NOW() - INTERVAL '5 minutes'
     AND sender = 'agent'
   ORDER BY created_at DESC
   LIMIT 3;
   ```

2. **DM (não-regressão):** mandar mensagem pra contato 1:1, conferir mesmo
   resultado. Esperado: mesmo SQL acima mostra `status='sent'`.

3. **Broadcast (se aplicável):** se as edges de broadcast também foram
   tocadas, disparar 1 broadcast com 2 destinatários (1 DM + se possível
   1 grupo). Conferir ambos `status='sent'`.

---

## Critérios de aceite

- [ ] Envio de texto pra conversation de grupo funciona via inbox (status=sent,
      mensagem chega no WhatsApp).
- [ ] Envio pra DM continua funcionando (não-regressão).
- [ ] Erro de 400 quando contato não tem nem phone nem JID tem mensagem clara
      (`Contact has neither phone nor whatsapp_jid`).
- [ ] Helper `resolveEvolutionRecipient` em `_shared/evolution-client.ts`
      com 7 unit tests cobrindo todos os branches.
- [ ] `bun run build`, `bunx tsc --noEmit`, vitest verdes.
- [ ] PR com descrição linkando este prompt + findings da Etapa 1.

---

## Notas

- **Sem migration.** Schema permanece igual. Grupos continuam com
  `phone=null`, e isso passa a ser válido.
- **Não dependa do `is_group` ser sempre populado** — o fallback `endsWith('@g.us')` cobre casos onde o flag esteja errado/não setado.
- Se durante a Etapa 1 descobrir que a montagem do `number` está espalhada
  em mais de 2 lugares, **parar e reportar** antes de codar — pode merecer
  refator maior do que a sprint prevê.

---

## Pós-merge

Depois do PR mergeado em `main`:

```bash
gh pr merge <PR_NUM> --squash --delete-branch
git checkout main
git pull origin main
supabase functions deploy provider-send-message
# se broadcasts foram tocados:
supabase functions deploy send-broadcast-now dispatch-scheduled-broadcasts
git push origin main   # garante que main no GitHub está sincronizado pra Lovable buildar o front (se houver mudança)
```

Lovable buida o front automaticamente quando `main` recebe push. Edges
não são deployadas pelo Lovable — precisam de `supabase functions deploy`
manual via CLI.

---

## Branch e PR

- Branch: `suf9-grupo-jid-fallback`
- PR título: `fix(send): fallback phone → JID pra grupos (SUF9)`
- PR descrição:
  - link pra este prompt;
  - findings da Etapa 1 (caminhos exatos das validações de phone);
  - lista de arquivos tocados;
  - checklist de smoke executado (com SQL real);
  - confirmação de não-regressão DM + broadcast.
