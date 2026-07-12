# SU8.4 — Sincronização de delete de mensagem com Evolution

> Sprint que completa o ciclo de migração SU8.x. Hoje, quando uma mensagem é
> deletada (no CRM ou no WhatsApp), o estado das duas pontas pode divergir.
> Esta sprint garante que delete em qualquer ponta propaga pra outra de forma
> consistente.

---

## Contexto

### Estado pós-SU8.3/SUF10d

- `provider-send-message` envia direto pra `wa.crm` com apikey per-instance ✅
- Broadcasts migrados ✅
- Captura de apikey em criação de instância ✅
- Reconciliação de nome de grupo cobrindo todos os caminhos (receive, send CRM, manual send celular) ✅

### Gap atual

**Cenário A — Delete iniciado no CRM:**
Operador clica "deletar" numa mensagem no inbox. Front deleta no banco local. Mas na Evolution / WhatsApp do destinatário, a mensagem continua lá.

**Cenário B — Delete iniciado no WhatsApp:**
Operador deleta uma mensagem pelo celular ou WA Web ("apagar para todos"). Evolution dispara webhook (provavelmente `messages.update` com `messageStubType: REVOKE` ou `messages.delete`). Hoje, dependendo do que o `provider-webhook` faz com esse evento, a mensagem pode ficar no banco local mesmo deletada lá fora.

### O que SU8.4 entrega

1. **Helper `deleteMessageViaEvolution`** em `_shared/evolution-client.ts` — chama o endpoint correto da Evolution v2 com `apikey` per-instance.
2. **Cenário A:** edge nova ou ajuste em edge existente pra que delete iniciado no CRM dispare o helper. Front passa a chamar essa edge ao deletar.
3. **Cenário B:** `provider-webhook` reconhece evento de delete da Evolution e sincroniza localmente (delete físico ou soft delete em `messages` — decidir na Etapa 1 conforme schema atual).

---

## Escopo

### IN

- Helper `deleteMessageViaEvolution` em `_shared/evolution-client.ts`.
- Edge / endpoint pra delete iniciado no CRM (Cenário A).
- Handler em `provider-webhook` pra delete vindo da Evolution (Cenário B).
- Ajuste no front (componente do inbox) pra chamar a edge nova ao deletar.

### OUT

- Soft delete UI / "deletado, mostra placeholder em vez de sumir" — fora de escopo,
  decisão de produto pra outra sprint.
- Histórico/audit trail de deletes — fora de escopo.
- Delete em massa, delete agendado — fora de escopo.

---

## Pré-requisitos

- Branch nova a partir de `main`: `su8-4-delete-message-evolution`.
- Build + tsc + vitest verdes.
- `main` pós-merge SUF10d (PR #194).

---

## Plano de execução

### Etapa 1 — Raio-x (sem codar)

Reportar antes de qualquer mudança. Esta etapa é crítica porque o escopo final depende dos findings:

1. **Endpoint Evolution v2 pra delete.** Verificar doc oficial e/ou testar contra `wa.crm.risenmidia.com.br`. Endpoints candidatos:
   - `DELETE /chat/deleteMessageForEveryone/{instance}` com body `{ id, remoteJid, fromMe, participant? }`
   - `POST /message/delete/{instance}` (variação)
   - Outro?
   
   Reportar:
   - Endpoint exato que aceita request com sucesso
   - Shape exato do body
   - O que volta na response (id confirmação? status? nada?)
   - Restrições conhecidas: tempo limite (ex: WhatsApp permite delete só nas últimas 2h?), só fromMe, só own messages, etc.

2. **Como o front deleta hoje.** Localizar o componente do inbox que tem ação "deletar". Reportar:
   - Caminho do componente
   - Como executa o delete (chama edge? chama supabase direto via RPC? supabase client `.from('messages').delete()`?)
   - Confirmação UX (modal? toast?)

3. **Schema de `messages` — soft vs hard delete.** Confirmar:
   - Tem coluna `deleted_at` ou `is_deleted`?
   - Se sim, delete atual é soft (UPDATE) ou hard (DELETE)?
   - Como o realtime trata? Front esconde rows com `deleted_at IS NOT NULL`?

4. **Eventos de delete vindos da Evolution.** Procurar nos logs do `provider-webhook` (últimos 7 dias) por:
   - `messages.delete`
   - `messages.update` com `messageStubType: REVOKE` ou similar
   - `chats.delete`
   
   Cola exemplo de payload real se aparecer. Se não aparecer, é sinal de que o webhook da instância não está subscrito a esse evento — precisa ajustar config Evolution.

5. **Trigger no banco.** Tem trigger PostgreSQL em `messages` que faz algo no DELETE? (Cascata em outras tabelas, audit log, etc.)

Não codar nesta etapa. Reportar findings em comentário do PR ou inline pro Pedro decidir escopo final antes de prosseguir.

### Etapa 2 — Helper `deleteMessageViaEvolution`

Em `_shared/evolution-client.ts`:

```ts
export async function deleteMessageViaEvolution(
  cfg: EvolutionConfig,
  args: {
    remoteJid: string;
    messageId: string;          // o provider_message_id do banco
    fromMe: boolean;
    participant?: string;       // pra grupos: JID do participante autor
  },
): Promise<{ ok: true } | { ok: false; status: number; error: string }> {
  // implementação conforme endpoint confirmado na Etapa 1
}
```

Tratar:
- 404 (mensagem já deletada / não encontrada) → `ok: true` (idempotente)
- 4xx outros → erro com mensagem clara
- 5xx → propagar pra retry futuro

### Etapa 3 — Cenário A: Delete iniciado no CRM

Duas opções de design, decidir com Pedro na Etapa 1:

**Opção 3.1 — Edge dedicada `delete-message`:**
- Recebe `{ message_id }` ou `{ message_id, conversation_id }`
- SELECT da mensagem + conversation + provider
- Chama `deleteMessageViaEvolution`
- Faz delete (ou soft delete) local somente após sucesso na Evolution
- Front substitui chamada atual por essa edge

**Opção 3.2 — Trigger no DELETE de `messages`:**
- Quando row é deletada (hard ou soft), trigger dispara um pg_net request pro endpoint da edge
- Edge faz a chamada Evolution
- Mais "automático" mas mais frágil (trigger silencia erros)

Recomendação inicial: **Opção 3.1**. Mais explícito, errar mais alto, fácil de debugar. Mas confirma com raio-x da Etapa 1.

### Etapa 4 — Cenário B: Delete iniciado no WhatsApp

Em `provider-webhook/index.ts`:

- Adicionar handler pra evento de delete (nome confirmado na Etapa 1).
- No handler:
  - Localizar `message` no banco por `provider_message_id` + `tenant_id`.
  - Aplicar mesmo modelo de delete (hard ou soft) que o front usa.
  - Log claro: `[webhook] message deleted by Evolution: msg=<id> conv=<id>`.

Atenção:
- Idempotência: se webhook chega 2x (Evolution às vezes duplica), DELETE deve ser no-op na 2ª.
- Race com Cenário A: se CRM deletou primeiro e Evolution ecoa, deve ser detectado e ignorado.

### Etapa 5 — Ajuste no front

- Trocar a chamada atual de delete pela nova edge.
- Mostrar loading enquanto Evolution confirma.
- Toast de erro se Evolution falhar (sem deletar local — manter consistência).
- Toast de sucesso após confirmação.

Não mexer em nada além da ação de delete. Sem refator do componente.

### Etapa 6 — Testes

**Unit (vitest):**
- `deleteMessageViaEvolution`:
  - Sucesso → `{ ok: true }`
  - 404 → `{ ok: true }` (idempotente)
  - 4xx outros → `{ ok: false, status, error }`
  - 5xx → `{ ok: false, status, error }`

**Build / tsc / vitest:** verdes.

### Etapa 7 — Smoke em produção

Após deploy:

1. **Cenário A — delete iniciado no CRM:**
   - Mandar mensagem teste pelo CRM pra contato seu (não cliente real).
   - Aguardar `status='sent'` + `provider_message_id` populado.
   - Deletar a mensagem pelo inbox.
   - Conferir no celular destino: mensagem desaparece (com aviso "esta mensagem foi apagada" do WhatsApp).
   - SQL: row removida ou `deleted_at` preenchido.

2. **Cenário B — delete iniciado no WhatsApp:**
   - Mandar mensagem teste pelo CRM (ou pelo celular).
   - No celular: apagar pra todos.
   - Aguardar webhook processar (~2s).
   - SQL: row removida ou marcada como deleted.
   - Inbox: mensagem desaparece em tempo real (via realtime).

3. **Idempotência:**
   - Repetir cenário A em mensagem já deletada → não retorna erro.
   - Forçar 2 webhooks de delete pra mesma mensagem → 2º é no-op.

---

## Critérios de aceite

- [ ] Helper `deleteMessageViaEvolution` em `_shared/evolution-client.ts` com testes.
- [ ] Cenário A funciona: delete no CRM propaga pro WhatsApp.
- [ ] Cenário B funciona: delete no WhatsApp propaga pro CRM.
- [ ] Idempotência: 2x delete = 1x efeito.
- [ ] Build / tsc / vitest verdes.
- [ ] PR linkando este prompt + findings da Etapa 1.

---

## Notas

- **Limite de tempo do delete pra todos.** WhatsApp tem limite de tempo (atualmente ~2 dias) pra "apagar pra todos". Após esse prazo, o delete vira "apagar pra mim" — Evolution provavelmente retorna erro. Tratar como 4xx esperado, mostrar mensagem clara no front.
- **Mensagens muito antigas.** Tentar deletar mensagem que nem está mais no servidor da Evolution pode dar 404. Helper já trata como idempotente.
- **Grupos.** Em grupos, só admin pode deletar mensagem de outro participante. Mensagem do próprio agente sempre pode ser deletada. Validar com raio-x se Evolution lida com isso ou retorna erro claro.
- **Cloud API (Meta).** Suporta delete? Se não, edge deve detectar `provider.type === 'cloud_api'` e seguir caminho diferente (provavelmente impossível, retorna erro explicativo).

---

## Pós-merge

```bash
gh pr merge <PR_NUM> --squash --delete-branch
git checkout main && git pull origin main
supabase functions deploy provider-webhook provider-send-message
# se criou edge nova:
supabase functions deploy delete-message
git push origin main
```

Sem migration nesta sprint (a menos que raio-x da Etapa 1 detecte que precisa adicionar `deleted_at` em `messages` — caso em que vira pré-requisito).

---

## Branch e PR

- Branch: `su8-4-delete-message-evolution`
- PR título: `feat(messages): sincronização de delete CRM ↔ Evolution (SU8.4)`
- PR descrição:
  - link pra este prompt;
  - findings da Etapa 1 (endpoint exato, design A/B escolhido, schema atual);
  - lista de arquivos tocados;
  - smoke executado com SQL real.

---

## Lembretes operacionais

- `grep -n` antes/depois de `replace_all`.
- Se migration for necessária, aplicar antes do deploy da edge (lição do SUF10b).
- `EdgeRuntime.waitUntil(promise)` se algum trabalho ficar em background pós-response.
- Logs distintos por caller pra debug fácil.
