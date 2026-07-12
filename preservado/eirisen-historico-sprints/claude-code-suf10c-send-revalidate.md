# SUF10c — Revalidação de nome de grupo também no envio (provider-send-message)

> Sprint complementar ao SUF10b. SUF10b cobriu revalidação reativa via webhook
> (`messages.upsert`), mas mensagens **enviadas pelo CRM** (sender=agent)
> não passam pelo webhook — elas são gravadas direto no banco pelo
> `provider-send-message`. Resultado: tenant que só envia, nunca recebe,
> nunca revalida nome.

---

## Contexto

### Cenário descoberto no smoke do SUF10b

Pedro mandou mensagem "Oi" no grupo `RSN Fernandinha` (JID
`120363428105763587@g.us`) pelo CRM, do tenant `bcdd0e10`. Resultado no banco:

| Tenant | sender | last_name_check_at | name |
|---|---|---|---|
| `bcdd0e10` (Pedro envia) | `agent` | **null** | "RSN Fernandinha" (velho) |
| `e0c95dbd` (outro recebe) | `contact` | preenchido | "Risen Fernanda" (novo) ✅ |

O tenant que **recebe** a mensagem revalida via webhook. O tenant que
**envia** não — porque envio não passa pelo webhook, vai direto ao
`provider-send-message`.

### Fluxo atual de envio

1. Front chama `provider-send-message` com `conversation_id` + `text`.
2. Edge faz SELECT da conversation+contact+provider.
3. Edge insere `message` com `sender='agent'`, `status='pending'`.
4. Edge chama Evolution `/message/sendText/{instance}` com JID/phone do
   destinatário.
5. Edge atualiza `message.status='sent'` + `provider_message_id`.

Em nenhum passo a edge consulta `fetchAllGroups` ou olha `last_name_check_at`.

### O que SUF10c entrega

Quando `provider-send-message` envia mensagem pra conversation cujo
contato é `is_group=true`, antes (ou logo após) do envio bem-sucedido,
checa `shouldRevalidateGroupName(contact.last_name_check_at)`. Se TRUE,
dispara `fetchAndUpdateGroupName` em background (fire-and-forget,
não-bloqueante).

Mesma lógica do SUF10b, só que no caminho de envio. Helper já existe em
`_shared/group-naming.ts`. A função `fetchAndUpdateGroupName` está em
`provider-webhook/index.ts` — precisa ser **extraída pra `_shared/`**
pra ser reusada por `provider-send-message`.

---

## Escopo

### IN

- Refatorar `fetchAndUpdateGroupName` pra `_shared/group-name-fetcher.ts`
  (ou nome equivalente).
- `provider-webhook/index.ts` passa a importar do shared (sem mudança
  comportamental).
- `provider-send-message/index.ts`:
  - SELECT inclui `whatsapp_jid`, `is_group`, `last_name_check_at`.
  - Após envio bem-sucedido a grupo, dispara fallback em background se
    TTL vencido.
  - Não bloqueia resposta da edge — fire-and-forget como no webhook.

### OUT

- Backfill retroativo (continua opcional, sprint separada).
- Broadcasts (`send-broadcast-now`, `dispatch-scheduled-broadcasts`) —
  podem ser tocados na mesma sprint **se for trivial** após a refatoração
  do shared. Decidir na Etapa 1.
- DM — não tocada (revalidação só pra `is_group=true`).

---

## Pré-requisitos

- Branch nova a partir de `main`: `suf10c-send-revalidate-group`.
- Build + tsc + vitest verdes.
- `main` pós-merge SUF10b (PR #190) com migration aplicada.

---

## Plano de execução

### Etapa 1 — Raio-x

Reportar antes de codar:

1. **Escopo da função `fetchAndUpdateGroupName`.** Ela hoje recebe
   `{ supabase, instanceName, apiKey, remoteJid, contactId }`. Confirmar
   essas dependências e que não tem nada acoplado ao `provider-webhook`.

2. **Como `provider-send-message` acessa apikey + instance_name do
   provider.** Já tem essas infos no SELECT. Reportar.

3. **Broadcasts:** `send-broadcast-now` e `dispatch-scheduled-broadcasts`
   também enviam pra grupos? Se sim, eles têm o mesmo problema — mensagens
   enviadas via broadcast não revalidam. Decidir se entra nesta sprint ou
   fica pra SUF10d.

Não codar. Reportar findings.

### Etapa 2 — Refatorar `fetchAndUpdateGroupName` pra shared

Mover pra `supabase/functions/_shared/group-name-fetcher.ts` (ou nome
adequado). Assinatura sugerida:

```ts
import type { SupabaseClient } from 'https://esm.sh/@supabase/supabase-js@2';

export async function fetchAndUpdateGroupName(
  supabase: SupabaseClient,
  params: {
    instanceName: string;
    apiKey: string | null;
    remoteJid: string;
    contactId: string;
  },
): Promise<void> {
  // mesma implementação atual, sem mudança comportamental
  // - GET fetchAllGroups
  // - se subject vier, UPDATE name
  // - sempre carimba last_name_check_at no final
}
```

Atualizar `provider-webhook/index.ts` pra importar do shared. Smoke do
webhook continua funcionando.

### Etapa 3 — Adaptar `provider-send-message`

#### 3.1 — SELECT inclui campos necessários

Onde a conversation+contact é lida (raio-x do SUF9 mostra dois pontos —
retry e new message), garantir que ambos pegam:

```ts
contact:contacts(id, name, phone, whatsapp_jid, is_group, last_name_check_at),
provider:whatsapp_providers(id, type, config, status)
```

#### 3.2 — Disparar revalidação após envio bem-sucedido

Após o `sendResult.success` ser `true`, antes do `return`:

```ts
import { isSuspectGroupName, shouldRevalidateGroupName } from '../_shared/group-naming.ts';
import { fetchAndUpdateGroupName } from '../_shared/group-name-fetcher.ts';

const contact = conversation.contact;
const isGroup = contact?.is_group === true;
const isQR = provider?.type === 'qr';
const cfg = isQR ? evolutionConfigFromProvider(provider) : null;

if (
  isGroup &&
  isQR &&
  cfg &&
  contact?.whatsapp_jid &&
  (
    isSuspectGroupName(contact.name, contact.whatsapp_jid) ||
    shouldRevalidateGroupName(contact.last_name_check_at)
  )
) {
  fetchAndUpdateGroupName(supabase, {
    instanceName: cfg.instanceName,
    apiKey: cfg.apikey,
    remoteJid: contact.whatsapp_jid,
    contactId: contact.id,
  }).catch((e) => {
    console.warn('[send-message] fetchAndUpdateGroupName falhou:', e);
  });
}
```

**Importante:** fire-and-forget. Não `await`. Não bloqueia a resposta da
edge.

#### 3.3 — Não tocar Cloud API

Cloud API (Meta) não suporta grupos — `sendViaCloudAPI` já normaliza pra
DM. Revalidação só pra `provider.type === 'qr'`.

### Etapa 4 — Broadcasts (condicional, depende da Etapa 1)

Se `send-broadcast-now` e `dispatch-scheduled-broadcasts` enviam pra
grupos, aplicar o mesmo padrão. Senão, deixar pra SUF10d.

### Etapa 5 — Testes

Helper já tem cobertura via SUF10/SUF10b. Adicionar:

- Test (vitest ou mock) confirmando que `provider-send-message` chama
  `fetchAndUpdateGroupName` quando contato é grupo + TTL vencido. Pode
  ser só verificação de chamada via spy/mock — não precisa hit real na
  Evolution.

Build + tsc + vitest verdes.

### Etapa 6 — Smoke

1. Deploy `provider-webhook` e `provider-send-message` (ambas mudam:
   webhook por causa do import do shared, send-message pela lógica nova).

2. **Caso real Pedro:** mandar mensagem pelo CRM no grupo
   `RSN Fernandinha` (tenant `bcdd0e10`).

3. SQL imediatamente:
   ```sql
   SELECT id, tenant_id, name, whatsapp_jid, last_name_check_at, updated_at
   FROM contacts
   WHERE whatsapp_jid = '120363428105763587@g.us'
   ORDER BY updated_at DESC;
   ```
   Esperado: tenant `bcdd0e10` agora tem `last_name_check_at` populado e
   `name='Risen Fernanda'` (ou nome atual do grupo no WhatsApp).

4. **Não-revalidação dentro do TTL:** mandar outra mensagem pelo CRM
   imediatamente. `last_name_check_at` não muda (ainda dentro de 1h).

5. **DM não-regressão:** mandar mensagem pelo CRM em DM, conferir que
   `last_name_check_at` da DM permanece null (DM não dispara revalidação).

---

## Critérios de aceite

- [ ] `fetchAndUpdateGroupName` em `_shared/`, importada por
      `provider-webhook` e `provider-send-message`.
- [ ] Mensagem enviada pelo CRM em grupo dispara revalidação de nome
      em background (TTL respeitado).
- [ ] Tenant `bcdd0e10` reconcilia `RSN Fernandinha` → nome novo após
      próximo envio.
- [ ] DMs não disparam revalidação.
- [ ] Não-bloqueante: resposta da edge `provider-send-message` não atrasa
      por causa do fallback (fire-and-forget confirmado em smoke).
- [ ] Build / tsc / vitest verdes.
- [ ] Não-regressão: webhook continua revalidando recebimentos como
      antes do refactor.

---

## Notas

- **Race condition aceitável.** Se 2 mensagens consecutivas (recebida +
  enviada) disparam fallback antes de `last_name_check_at` ser carimbado,
  são 2 chamadas a `fetchAllGroups`. Custo desprezível.
- **Erro silencioso por design.** `.catch(console.warn)` no fallback
  garante que falha de revalidação não derruba envio nem retorna 500
  pro front. Funciona como "best effort".
- **Refatoração mínima.** Mover `fetchAndUpdateGroupName` pra shared sem
  mudar comportamento. Se aparecer tentação de "limpar" outras coisas
  no provider-webhook durante o move, **não fazer**. Cada PR um propósito.

---

## Pós-merge

```bash
gh pr merge <PR_NUM> --squash --delete-branch
git checkout main && git pull origin main
supabase functions deploy provider-webhook provider-send-message
git push origin main
```

(Sem migration nessa sprint. Migration do SUF10b já cobre.)

---

## Branch e PR

- Branch: `suf10c-send-revalidate-group`
- PR título: `feat(send): revalidação de nome de grupo no envio (SUF10c)`
- PR descrição:
  - link pra este prompt;
  - findings da Etapa 1 (escopo do helper, decisão sobre broadcasts);
  - lista de arquivos tocados;
  - smoke executado (passos 1-5 da Etapa 6).

---

## Lembretes operacionais

- `grep -n` antes/depois de `replace_all` em padrões repetidos.
- Helper `fetchAndUpdateGroupName` deve ser **movido**, não copiado.
  `provider-webhook` passa a importar de `_shared/`. Senão criamos drift
  de comportamento.
