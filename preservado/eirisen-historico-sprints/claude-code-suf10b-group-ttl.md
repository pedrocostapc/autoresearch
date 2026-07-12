# SUF10b — Revalidação reativa de nome de grupo (TTL 1h)

> Sprint complementar ao SUF10. SUF10 corrigiu os UPDATEs (subject vence sem
> guard) e ampliou o gate (`isSuspectGroupName`). Mas Pedro descobriu que
> rename de grupo no WhatsApp **não dispara `groups.upsert`** na Evolution —
> só `messages.upsert`. E `isSuspectGroupName` não reconhece nomes
> "aparentemente válidos mas desatualizados". Resultado: rename nunca propaga.

---

## Contexto

### Estado pós-SUF10 (PR #189)

- Handler `groups.upsert` tira o nome do `subject` do payload e atualiza
  `contacts.name` sem guard. ✅ Mas o evento **não chega** em rename.
- `fetchAndUpdateGroupName` faz fallback via `fetchAllGroups`, mas só
  dispara quando o gate `isSuspectGroupName(name, jid)` retorna `true`
  (placeholder `Grupo XXXX`, JID local-part puro, ou null/vazio).
- Nomes "RSN Fernandinha", "2RSN Fernandinha" — não-suspeitos pelo gate
  atual — ficam congelados mesmo após rename no WhatsApp.

### Smoke real (09/05/2026)

Pedro renomeou grupo `120363428105763587@g.us` no WhatsApp pra "Risen
Fernandinha". Mensagem nova entrou no grupo, webhook chegou
(`event=messages.upsert`), `updated_at` do contato foi tocado, mas `name`
permaneceu velho nas 3 rows (3 tenants). Logs do `provider-webhook` na
janela do smoke mostram zero ocorrências de `groups.upsert` — confirmado
que esse evento não vem em rename.

### Decisão de produto

Pedro quer comportamento "igual WhatsApp Web" — nome sempre fresco. Custo
de chamadas extras a `fetchAllGroups` é desprezível (Evolution self-hosted
em droplet do Pedro, capacidade ociosa). Caminho escolhido: **revalidação
reativa por TTL curto (1h)**.

---

## O que SUF10b entrega

1. Coluna nova `contacts.last_name_check_at` (timestamptz, nullable).
2. Toda vez que `messages.upsert` bater num contato `is_group=true`, se
   `last_name_check_at` for null ou mais antigo que **1 hora**, dispara
   `fetchAndUpdateGroupName` em background.
3. `fetchAndUpdateGroupName` passa a atualizar `last_name_check_at` no
   final, **mesmo se o nome não mudou** (importante pro TTL não martelar
   a Evolution toda mensagem).
4. Mantém o caminho atual (`isSuspectGroupName` continua disparando
   imediatamente sem TTL — placeholder/JID puro são casos urgentes,
   não esperam 1h).

---

## Escopo

### IN

- Migration nova adicionando `last_name_check_at` em `contacts`.
- `provider-webhook/index.ts`:
  - Helper novo `shouldRevalidateGroupName(contact, ttlMs)`.
  - Gate ampliado no ponto de invocação: dispara fallback se
    `isSuspectGroupName` OU `shouldRevalidateGroupName` for `true`.
  - `fetchAndUpdateGroupName` atualiza `last_name_check_at` ao final.

### OUT

- Backfill retroativo dos contatos existentes — fica como SUF10c separado
  se Pedro quiser zerar débito de uma vez. Sem isso, contatos antigos vão
  reconciliando organicamente conforme recebem mensagem.
- pg_cron periódico — descartado em favor do reativo.
- DM (não-grupo) — não tocada.

---

## Pré-requisitos

- Branch nova a partir de `main`: `suf10b-group-name-ttl`.
- Build + tsc + vitest verdes.
- `main` pós-merge SUF10 (PR #189).

---

## Plano de execução

### Etapa 1 — Migration

Arquivo: `supabase/migrations/<timestamp>_suf10b_group_name_ttl.sql`

```sql
-- SUF10b: TTL pra revalidação reativa de nome de grupo.
-- Tocado pela função fetchAndUpdateGroupName ao final.
-- Gate em provider-webhook dispara fallback quando este campo for null
-- ou mais antigo que 1h.
ALTER TABLE contacts
  ADD COLUMN IF NOT EXISTS last_name_check_at timestamptz;

COMMENT ON COLUMN contacts.last_name_check_at IS
  'Última vez que o nome do contato foi revalidado contra a fonte autoritativa (Evolution fetchAllGroups). NULL = nunca verificou. Usado por SUF10b pra TTL de 1h em grupos.';

-- Index parcial pra queries de "grupos com TTL vencido"
CREATE INDEX IF NOT EXISTS idx_contacts_group_ttl
  ON contacts (last_name_check_at)
  WHERE is_group = true;
```

Aplicar via Supabase CLI (`supabase db push`) **ou** SQL Editor manual + INSERT
em `supabase_migrations.schema_migrations` (Pedro tem o padrão).

### Etapa 2 — Helper `shouldRevalidateGroupName`

Em `supabase/functions/_shared/group-naming.ts` (mesmo arquivo do SUF10):

```ts
const TTL_MS = 60 * 60 * 1000; // 1 hora

export function shouldRevalidateGroupName(
  lastCheckAt: string | null | undefined,
  now: Date = new Date(),
  ttlMs: number = TTL_MS,
): boolean {
  if (!lastCheckAt) return true;
  const last = new Date(lastCheckAt).getTime();
  if (Number.isNaN(last)) return true;
  return now.getTime() - last >= ttlMs;
}
```

`now` parametrizável pra testes determinísticos.

### Etapa 3 — Adaptar webhook

Em `provider-webhook/index.ts`:

#### 3.1 — Carregar `last_name_check_at` no SELECT do contato

Onde o contato é lido após upsert (proximidade da linha 418-443 segundo
raio-x anterior), adicionar `last_name_check_at` no `.select()`.

#### 3.2 — Ampliar gate de invocação

```ts
// antes (SUF10)
if (
  contactRow.is_group &&
  instanceName &&
  isSuspectGroupName(contactRow.name, contactRow.whatsapp_jid)
) {
  fetchAndUpdateGroupName(...).catch(...)
}

// depois (SUF10b)
if (
  contactRow.is_group &&
  instanceName &&
  (
    isSuspectGroupName(contactRow.name, contactRow.whatsapp_jid) ||
    shouldRevalidateGroupName(contactRow.last_name_check_at)
  )
) {
  fetchAndUpdateGroupName(...).catch(...)
}
```

#### 3.3 — `fetchAndUpdateGroupName` carimba `last_name_check_at`

No final da função, **independentemente de ter atualizado o nome ou não**,
gravar `last_name_check_at = now()`. Isso garante que o TTL é respeitado
mesmo quando o nome não mudou.

```ts
// dentro de fetchAndUpdateGroupName, após o UPDATE de name (que pode ou
// não ter rodado):
await supabase
  .from('contacts')
  .update({ last_name_check_at: new Date().toISOString() })
  .eq('id', contactId);
```

Atenção: dois UPDATEs separados (um pra `name` quando subject vier, outro
pra `last_name_check_at` sempre). Se preferir, pode mesclar em um único
update quando ambos forem aplicáveis. Não otimizar prematuramente — clareza
vence.

### Etapa 4 — Testes

**Unit (vitest)** em `_shared/group-naming.ts`:

- `shouldRevalidateGroupName`:
  - `(null)` → true
  - `(undefined)` → true
  - `('')` → true (string vazia inválida)
  - `('not-a-date')` → true (`Number.isNaN`)
  - now=2026-05-09T12:00, lastCheck=2026-05-09T10:30 → true (1h30 atrás)
  - now=2026-05-09T12:00, lastCheck=2026-05-09T11:30 → false (30min atrás)
  - now=2026-05-09T12:00, lastCheck=2026-05-09T11:00 → true (exatamente 1h, `>=`)
  - TTL custom (ex: 5min) — confirma que ttlMs parametriza

Build + tsc + vitest verdes.

### Etapa 5 — Smoke em produção

1. **Aplica a migration** (CLI ou SQL Editor manual).
2. **Deploy** `provider-webhook`.
3. **Caso real:** mandar mensagem em qualquer grupo (ex: `RSN Fernandinha`,
   já renomeado no WhatsApp pra "Risen Fernandinha").
4. SQL imediatamente depois:
   ```sql
   SELECT id, tenant_id, name, whatsapp_jid, last_name_check_at, updated_at
   FROM contacts
   WHERE whatsapp_jid = '120363428105763587@g.us'
   ORDER BY updated_at DESC;
   ```
   Esperado: `last_name_check_at` populado (now), `name` atualizado pra
   "Risen Fernandinha" no tenant da instância que recebeu o webhook.
5. **Não-revalidação dentro de 1h:** mandar outra mensagem no mesmo grupo
   imediatamente. Logs do `provider-webhook` **não** devem mostrar
   `fetchAllGroups` nessa segunda invocação. SQL: `last_name_check_at` não
   muda (continua o do passo 4).
6. **Revalidação após TTL:** depois de 1h, mandar mensagem no grupo,
   conferir que `fetchAllGroups` rodou e `last_name_check_at` foi atualizado.

---

## Critérios de aceite

- [ ] Coluna `contacts.last_name_check_at` criada via migration aplicada.
- [ ] Rename de grupo no WhatsApp propaga pro CRM na próxima mensagem
      (após máx 1h se a última verificação foi recente, imediato se nunca
      verificou ou está com nome suspeito).
- [ ] Mensagens consecutivas dentro do TTL **não** disparam `fetchAllGroups`
      adicional — confirmado nos logs.
- [ ] Helper `shouldRevalidateGroupName` com 8 unit tests.
- [ ] DMs intocadas — `last_name_check_at` permanece null pra contatos
      `is_group=false`.
- [ ] Build / tsc / vitest verdes.
- [ ] Caso de teste real: `120363428105763587@g.us` reconciliado em todos
      os tenants que receberem webhook nessa janela.

---

## Notas

- **TTL de 1h é o equilíbrio inicial.** Se a Evolution mostrar carga
  preocupante (cenário improvável dado o droplet self-hosted), aumentar
  pra 6h. Constante no helper, fácil mexer.
- **Backfill retroativo é opcional.** Sem ele, contatos só reconciliam
  ao receber mensagem nova. Pedro decide depois se quer rodar uma edge
  one-shot pra zerar débito histórico (SUF10c).
- **Fila de invocações concorrentes:** se 2 mensagens chegam quase
  simultaneamente do mesmo grupo, podem disparar 2 `fetchAllGroups` antes
  do `last_name_check_at` ser gravado. Aceitável — race condition raro,
  custo é só 1 chamada extra eventual. Não vale lockar.
- **Migration zero-downtime:** `ADD COLUMN nullable` + `CREATE INDEX
  IF NOT EXISTS` são seguros sem manutenção. Pode aplicar com tráfego.

---

## Pós-merge

```bash
gh pr merge <PR_NUM> --squash --delete-branch
git checkout main
git pull origin main

# Aplicar migration:
supabase db push
# OU manualmente no SQL Editor + INSERT em supabase_migrations.schema_migrations

supabase functions deploy provider-webhook
git push origin main
```

Se Pedro estiver no terminal "novo" do Claude Code que tem problema de
auth Supabase CLI, aplicar migration via SQL Editor manual + INSERT em
`supabase_migrations.schema_migrations`. Ele tem o padrão dos sprints
anteriores.

---

## Branch e PR

- Branch: `suf10b-group-name-ttl`
- PR título: `feat(webhook): TTL 1h pra revalidação de nome de grupo (SUF10b)`
- PR descrição:
  - link pra este prompt;
  - findings de smoke real (logs mostrando `fetchAllGroups` disparando 1x
    e não-disparando dentro do TTL);
  - lista de arquivos tocados;
  - confirmação de smoke completo (passos 1-6 da Etapa 5).

---

## Lembretes operacionais

- Antes de `replace_all` em padrão repetido, `grep -n` antes/depois pra
  contar matches. Diferenças de indentação podem fazer replace perder
  ocorrências (lição do SUF9).
- Ler `_shared/group-naming.ts` antes de adicionar o helper novo — ele já
  existe (criado no SUF10). Adicionar `shouldRevalidateGroupName` no
  mesmo arquivo, não criar arquivo paralelo.
