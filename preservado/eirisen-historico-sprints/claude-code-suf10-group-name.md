# SUF10 — Reconciliação de nome de grupo (subject como fonte da verdade)

> Sprint de fix médio. Hoje, nome de grupo é "congelado" na primeira leitura
> (mesmo que essa leitura seja errada — ex: pegou pushName de participante,
> ou nome temporário). Renames no WhatsApp não propagam.
> O guard `name LIKE 'Grupo ____'` aparece em 3 caminhos e impede qualquer
> sobrescrita de nome não-placeholder.

---

## Contexto

### Sintoma observado em produção

Pedro confirmou via SQL que tem grupos com nome desatualizado, casos:

- JID `120363428105763587@g.us` aparece em **3 tenants** com nomes diferentes:
  - "RSN Fernandinha" (tenant bcdd0e10) — `updated_at` recente, mas nome velho
  - "2RSN Fernandinha" (tenant 5c6dc551) — idem
  - "2RSN Fernandinha" (tenant ed02eb45) — idem
- Pedro renomeou o grupo no WhatsApp pra "Risen Fernandinha". Nenhum dos 3
  tenants pegou o rename.

### Causa raiz

Em `supabase/functions/provider-webhook/index.ts`, 3 lugares fazem update de
`contacts.name` pra grupo, **todos** com guard `LIKE "Grupo ____"`:

1. **Handler `groups.upsert` (linhas 101-134):** lê `g.subject` do payload mas
   `UPDATE ... LIKE "Grupo ____"` impede sobrescrever nome existente.
2. **Fallback `fetchAndUpdateGroupName` (linhas 1216-1286):** mesmo guard.
3. **Gate de invocação (linha 434):** `isGenericGroupName(name)` só dispara
   o fallback se nome casar com `/^Grupo \d{4}$/`.

Resultado: a **primeira** leitura do nome ganha permanentemente. Renames
posteriores nunca propagam.

### Por que não pode ser fix trivial "remove o guard"

Nem todo update vem da Evolution com `subject` confiável. Mensagens
`messages.upsert` em grupo chegam com `pushName` (nome do participante que
mandou a mensagem), não do grupo. Se removermos o guard sem cuidado, o nome
do grupo passa a oscilar conforme o último participante que falou.

A solução não é remover guard — é **distinguir fontes autoritativas
(`subject` no payload de grupo) de fontes não-autoritativas (`pushName` de
mensagem)**, e deixar a fonte autoritativa sobrescrever sem guard.

---

## O que SUF10 entrega

1. `groups.upsert` handler: update de `contacts.name = subject` **sem guard**
   (subject é fonte autoritativa). Se subject vazio/null, não atualiza
   (não sobrescreve com nada).
2. `fetchAndUpdateGroupName` (fallback): mesma mudança — se a Evolution
   retornou subject válido, sobrescreve sem guard.
3. Gate de invocação: amplia critério pra também disparar quando o nome
   atual for **suspeito** (não só `Grupo XXXX` placeholder). Critérios:
   - nome casa com `/^Grupo \d{4}$/` (placeholder antigo) → dispara
   - nome igual ao JID local-part (`120363428105763587`) → dispara
   - **OU** o último fetch do subject foi há >7 dias → dispara em
     background pra revalidar (ttl)
4. `messages.upsert` em grupo continua **não tocando** em
   `contacts.name` — só atualiza outros campos. Mantém comportamento atual.
5. **Backfill one-shot opcional (escopo separado, não nesta sprint):** edge
   tipo SU8.0 que itera grupos e força fetchAllGroups pra reconciliar nomes
   históricos. Anotar como SUF10b se Pedro quiser executar depois do deploy.

---

## Escopo

### IN

- `supabase/functions/provider-webhook/index.ts` — handler `groups.upsert`,
  `fetchAndUpdateGroupName`, e gate `isGenericGroupName`.
- Eventualmente um helper `isSuspectGroupName(name, jid)` em `_shared/`.

### OUT

- Backfill retroativo — fica como SUF10b se Pedro quiser depois.
- Lógica de DM (não-grupo) — intocada.
- Schema — sem mudança.

---

## Pré-requisitos

- Branch nova a partir de `main`: `suf10-group-name-reconcile`.
- Build + tsc + vitest verdes antes de começar.
- `main` pós-merge SUF9 (PRs #187 e #188).

---

## Plano de execução

### Etapa 1 — Raio-x (sem codar)

Reportar antes de qualquer mudança:

1. **Estrutura do payload `groups.upsert`** que a Evolution envia. Procurar
   nos logs do `provider-webhook` (Dashboard → Logs) por uma invocação
   recente com event=`groups.upsert` e colar o JSON. Quero ver:
   - Como cada item do array vem (`{ id, subject, ... }`?)
   - Se vem `creation`, `participants`, etc.
   - Se vem em rename ou só em create.

2. **Confirmar com fontes** (Evolution v2 docs ou teste real) se `groups.upsert`
   é disparado em **rename** de grupo, ou só em create/membership change. Se
   não for disparado em rename, fix tem que cobrir via outro caminho
   (`groups.update` se existir, ou fetchAllGroups periódico).

3. **Mapear todos os UPDATE em `contacts.name`** no webhook. Já vimos 3
   caminhos com guard `LIKE "Grupo ____"`. Confirmar que não tem outros.

4. **Conferir se a Evolution está subscrevendo `groups.upsert`** nos webhooks
   da instância. Pode estar configurado pra `messages.upsert` apenas.

Não codar. Reportar findings.

### Etapa 2 — Implementação

#### 2.1 — Helper `isSuspectGroupName`

Em `_shared/group-naming.ts` (arquivo novo) ou inline se preferir:

```ts
const PLACEHOLDER_RE = /^Grupo \d{4}$/;

export function isSuspectGroupName(
  name: string | null | undefined,
  whatsappJid: string | null | undefined,
): boolean {
  if (!name || typeof name !== 'string') return true;
  if (PLACEHOLDER_RE.test(name)) return true;

  // Nome igual ao JID local-part (ex: "120363428105763587")
  if (whatsappJid) {
    const localPart = whatsappJid.split('@')[0];
    if (name === localPart) return true;
  }

  return false;
}
```

#### 2.2 — Handler `groups.upsert`

Remover o `.like("name", "Grupo ____")` do UPDATE. Subject vindo de
`groups.upsert` é fonte autoritativa.

```ts
// antes
await supabase
  .from('contacts')
  .update({ name: subject })
  .eq('tenant_id', tenantId)
  .eq('whatsapp_jid', g.id)
  .like('name', 'Grupo ____');

// depois
if (subject && typeof subject === 'string' && subject.trim().length > 0) {
  await supabase
    .from('contacts')
    .update({ name: subject.trim() })
    .eq('tenant_id', tenantId)
    .eq('whatsapp_jid', g.id);
}
```

Sem guard. Sem subject válido = sem update.

#### 2.3 — `fetchAndUpdateGroupName`

Mesma mudança. Tirar `.like("name", "Grupo ____")` no UPDATE final. Manter
o resto (inclusive a tolerância a falha — função em fire-and-forget).

#### 2.4 — Gate de invocação

Trocar `isGenericGroupName(contactRow.name)` por
`isSuspectGroupName(contactRow.name, contactRow.whatsapp_jid)`.

```ts
if (
  contactRow.is_group &&
  instanceName &&
  isSuspectGroupName(contactRow.name, contactRow.whatsapp_jid)
) {
  fetchAndUpdateGroupName(supabase, { ... }).catch(...)
}
```

Isso amplia o disparo do fallback pra cobrir nomes-JID e placeholders.

#### 2.5 — TTL revalidação (opcional, deixar pra SUF10c se complicar)

Se for fácil, adicionar revalidação periódica: se `is_group=true` e
`updated_at < now() - interval '7 days'`, disparar `fetchAndUpdateGroupName`
em background mesmo que o nome pareça válido. Isso cobre rename silencioso
quando `groups.upsert` não vem.

Se for trabalho > 30min, **deixar pra outra sprint**. Não bloquear SUF10
por isso.

### Etapa 3 — Testes

**Unit (vitest)** em `_shared/group-naming.ts`:

- `isSuspectGroupName`:
  - `(null, '...@g.us')` → true
  - `('', '...@g.us')` → true
  - `('Grupo 1525', '...')` → true
  - `('120363428105763587', '120363428105763587@g.us')` → true (nome=local-part)
  - `('RSN Fernandinha', '120363428105763587@g.us')` → false (nome real)
  - `('Grupo 12345', '...')` → false (5 dígitos não casa /^Grupo \d{4}$/)
  - `('Grupo X', '...')` → false (não é \d)

- **Build:** `bun run build` verde.
- **TSC:** `bunx tsc --noEmit` sem erros.
- **Vitest:** todos verdes.

### Etapa 4 — Smoke em produção

Após deploy:

1. **Renomear grupo no WhatsApp.** Escolher um grupo de teste, mudar nome
   pra algo diferente.
2. **Mandar 1 mensagem nesse grupo** (pra forçar webhook).
3. SQL:
   ```sql
   SELECT id, name, whatsapp_jid, updated_at
   FROM contacts
   WHERE whatsapp_jid = '<JID-DO-GRUPO-RENOMEADO>'
   ORDER BY updated_at DESC;
   ```
   Esperado: nome novo refletido em todos os tenants.

4. **Caso real Pedro:** rename do grupo `120363428105763587@g.us` que hoje
   está como "RSN Fernandinha" / "2RSN Fernandinha". Após mensagem nova,
   conferir SQL acima — esperado: 3 rows com nome novo.

5. **Não-regressão:** mandar mensagem em DM, conferir que `contacts.name`
   da DM não foi tocado.

---

## Critérios de aceite

- [ ] Rename de grupo no WhatsApp propaga pro CRM (após próxima mensagem
      no grupo, ou após próximo `groups.upsert`).
- [ ] Nomes JID-puro (`120363...`) param de existir após reconciliação
      automática.
- [ ] Helper `isSuspectGroupName` com 7 unit tests.
- [ ] DMs não regridem.
- [ ] `bun run build`, `bunx tsc --noEmit`, vitest verdes.
- [ ] PR linkando este prompt + findings da Etapa 1 (especialmente: payload
      real do `groups.upsert` e se ele é disparado em rename).

---

## Notas

- **Não confiar em `pushName`** pra atualizar nome de grupo. `pushName` é o
  nome do participante que mandou a mensagem, não do grupo. Mensagens em
  grupo (`messages.upsert`) continuam não tocando em `contacts.name`.
- **Subject vazio = no-op.** Sem subject válido, não sobrescreve. Evita
  caso degenerado de pegar string vazia da Evolution e zerar o nome.
- **Mais de um tenant ouvindo o mesmo grupo é normal.** Cada tenant tem
  sua própria row em `contacts` com o mesmo JID. SUF10 atualiza todas as
  rows do tenant correspondente (filtra por `tenant_id`), então cada tenant
  reconcilia independentemente quando recebe webhook.
- Se a Etapa 1 mostrar que `groups.upsert` **não** é disparado em rename
  pela Evolution, o caminho principal vira o fallback `fetchAndUpdateGroupName`
  via TTL ou disparo em toda mensagem suspeita. Reportar antes de seguir.

---

## Pós-merge

```bash
gh pr merge <PR_NUM> --squash --delete-branch
git checkout main
git pull origin main
supabase functions deploy provider-webhook
git push origin main
```

---

## Branch e PR

- Branch: `suf10-group-name-reconcile`
- PR título: `fix(webhook): rename de grupo propaga pro CRM (SUF10)`
- PR descrição:
  - link pra este prompt;
  - findings da Etapa 1 (payload real, se groups.upsert dispara em rename);
  - lista de arquivos tocados;
  - smoke executado com SQL real (caso Pedro: 3 tenants reconciliados).

---

## Lembretes operacionais (do feedback do Code anterior)

- Antes de `replace_all` em padrão que aparece mais de uma vez, rodar
  `grep -n` pra confirmar match count. Não confiar só no "All occurrences
  successfully replaced" — diferenças de indentação podem fazer o replace
  perder ocorrências.
