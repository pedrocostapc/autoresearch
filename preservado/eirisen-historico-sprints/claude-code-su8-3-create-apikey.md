# SU8.3 — Captura de apikey ao criar instância

> Sprint de fix infra. Fecha o gap deixado pelo SU8.0 (backfill one-shot):
> instâncias **novas** criadas após o backfill ficam sem `apikey` em
> `whatsapp_providers.config.apikey`, e isso quebra `provider-send-message`
> (SU8.1) e broadcasts (SU8.2) que agora dependem desse campo.

---

## Contexto

### Estado atual

- **SU8.0** populou `whatsapp_providers.config.apikey` de forma one-shot em 18
  instâncias existentes via edge `backfill-evolution-apikeys`.
- **SU8.1** migrou `provider-send-message` pra usar `wa.crm` direto com
  header `apikey: <per-instance>` lido de `provider.config.apikey`.
- **SU8.2** migrou broadcasts (send-now + dispatch-scheduled) pra mesmo padrão
  via `_shared/evolution-client.ts`.

### O problema

Quando uma instância **nova** é criada (Pedro conecta um WhatsApp novo no CRM),
o fluxo atual chama a Evolution e cria a row em `whatsapp_providers`, mas
**não persiste o apikey** retornado pela Evolution. Resultado: a instância
nova tem `config.apikey` vazio/null, e qualquer envio (texto ou broadcast)
vai falhar com erro de auth porque o helper `sendTextViaEvolution` exige
`apikey` per-instância.

Hoje a única saída é rodar o backfill manualmente após criar instância — não
escala, é frágil.

### O que SU8.3 entrega

O fluxo de criação grava `config.apikey` automaticamente no INSERT (ou no
UPDATE imediatamente posterior, dependendo de como o código atual está
estruturado), de forma que toda instância criada já nasce pronta pra envio.

---

## Achado crítico (vindo do SU8.0)

A resposta da Evolution v2 **não bate com a doc**. O campo do apikey vem em
`token`, não `apikey`, e o nome vem em `name` raiz, não `instanceName`:

```json
{
  "id": "uuid",
  "name": "instance-name",
  "token": "C5B8...",
  ...
}
```

O endpoint de **criação** (`POST /instance/create`) pode ter shape **diferente**
do `/instance/fetchInstances` usado no backfill. Parte do raio-x da Etapa 1
é confirmar o shape exato da response de `create` antes de codar.

Fallback chain do helper de extração (já existe no código do SU8.0): tentar
`token`, depois `apikey`, depois `hash`, depois `key`. Reusar.

---

## Escopo

### IN

- Edge / função / handler que cria instâncias Evolution (provavelmente
  `evolution-proxy` ou nome similar — descobrir no raio-x).
- Lógica de INSERT em `whatsapp_providers` no fluxo de criação.
- Helper compartilhado de extração de apikey, se já existir; senão,
  centralizar em `_shared/evolution-client.ts`.

### OUT (não tocar)

- Backfill edge (`backfill-evolution-apikeys`) — fica como está, idempotente,
  pra cobrir lacunas se algo escapar.
- `provider-send-message`, `send-broadcast-now`, `dispatch-scheduled-broadcasts`
  — já migrados, intocados.
- RLS / policies de `whatsapp_providers`.
- UI do CRM para criar instância (cliente).

---

## Pré-requisitos

- Branch nova a partir de `main`: `su8-3-create-apikey-capture`.
- Build + tsc + vitest verdes antes de começar.

---

## Plano de execução

### Etapa 1 — Raio-x (sem codar)

Reportar antes de qualquer mudança:

1. **Edge / função que cria instância Evolution.** Procurar por
   `instance/create` ou `POST.*evolution.*instance` em `supabase/functions/`.
   Provavelmente é `evolution-proxy/index.ts` ou um handler dedicado tipo
   `create-instance`. Reportar caminho exato.

2. **Onde a row de `whatsapp_providers` é INSERTada após a criação.** Pode ser:
   - na própria edge de criação (depois de chamar Evolution);
   - em um trigger / RPC do banco;
   - no client (Lovable) após receber response da edge.
   Reportar ponto exato.

3. **Shape real da response de `POST /instance/create` da Evolution v2** que
   esse fluxo está chamando. Idealmente um log real ou tcpdump do response.
   Se não tiver log, fazer uma chamada de teste (criar instância descartável
   e olhar logs) — ou pedir pro Pedro fazer e mandar o JSON.

4. **Helper de extração de apikey existente.** Ver se
   `_shared/evolution-client.ts` (criado em SU8.1) já tem função de extrair
   apikey da response. Se sim, reusar. Se não, adicionar.

Não codar nada nesta etapa. Reportar findings antes de seguir.

### Etapa 2 — Implementação

Dependendo do que sair da Etapa 1, mas o padrão esperado:

1. **Centralizar extrator de apikey** em `_shared/evolution-client.ts`:

   ```ts
   export function extractApikeyFromEvolutionResponse(payload: unknown): string | null {
     if (!payload || typeof payload !== 'object') return null;
     const p = payload as Record<string, unknown>;
     // tentar nas variações conhecidas, em ordem
     for (const key of ['token', 'apikey', 'hash', 'key']) {
       const v = p[key];
       if (typeof v === 'string' && v.length > 0) return v;
     }
     // alguns shapes embutem em `instance` ou `Instance`
     for (const wrap of ['instance', 'Instance']) {
       const inner = p[wrap];
       if (inner && typeof inner === 'object') {
         const got = extractApikeyFromEvolutionResponse(inner);
         if (got) return got;
       }
     }
     return null;
   }
   ```

   Esse extrator deve ser o **mesmo** usado no backfill — DRY. Se o backfill
   tem cópia inline, mover pra cá e refatorar.

2. **No fluxo de criação:**
   - Após `POST /instance/create`, extrair apikey via helper.
   - Se apikey extraído, incluir no `config` que vai pro INSERT:
     ```ts
     const config = {
       ...existingConfig,
       apikey: extractedApikey,
     };
     ```
   - Se apikey **não foi extraído** (response em shape inesperado), logar
     `console.warn` com payload truncado e seguir com INSERT mesmo assim
     (não falhar a criação por causa disso — backfill cobre depois). Mas o
     warn precisa estar lá pra a gente saber que aconteceu.

3. **Atomicidade:** o ideal é gravar `config.apikey` no mesmo INSERT da row.
   Se a estrutura atual faz INSERT primeiro e UPDATE depois (ex: row criada
   e depois config preenchido), usar o UPDATE pra incluir apikey também,
   de forma que a row nunca persista com `config.apikey` faltando após o
   fluxo de criação completar com sucesso.

### Etapa 3 — Testes

- **Unit (vitest)** em `_shared/evolution-client.ts`:
  - `extractApikeyFromEvolutionResponse` cobre os shapes:
    - `{ token: "abc" }` → `"abc"`
    - `{ apikey: "abc" }` → `"abc"`
    - `{ hash: "abc" }` → `"abc"`
    - `{ instance: { token: "abc" } }` → `"abc"`
    - `{ Instance: { hash: "abc" } }` → `"abc"`
    - `{}` → `null`
    - `null` → `null`
    - `"string"` → `null`
    - precedência: se tiver `token` e `apikey`, ganha `token`.

- **Smoke deferido** (Etapa 5) cobre o fluxo end-to-end real, já que mockar
  o INSERT no Postgres em teste de edge é overkill.

- **Build:** `bun run build` (ou equivalente do repo) verde.
- **TSC:** `bunx tsc --noEmit` sem erros.
- **Vitest:** todos verdes, incluindo os novos.

### Etapa 4 — Não-regressão

- O backfill (`backfill-evolution-apikeys`) deve continuar funcional. Se o
  extrator foi movido pra `_shared`, o backfill agora importa de lá em vez
  de ter a cópia inline. Smoke do backfill: rodar dry-run e confirmar que
  identifica 0 instâncias sem apikey (se já tá tudo populado) ou as que
  estão faltando.

### Etapa 5 — Smoke em produção

Após deploy:

1. **Criar instância nova de teste** pelo CRM (qualquer tenant de
   desenvolvimento).
2. SQL imediatamente depois:

   ```sql
   SELECT id, tenant_id, instance_name, type, status,
          config ? 'apikey' AS has_apikey,
          length(config->>'apikey') AS apikey_len,
          created_at
   FROM whatsapp_providers
   WHERE created_at > NOW() - INTERVAL '5 minutes'
   ORDER BY created_at DESC;
   ```

   Esperado: `has_apikey=true`, `apikey_len > 0`.

3. **Enviar uma mensagem teste** via inbox dessa nova instância. Esperado:
   `status='sent'`, `provider_message_id` populado, mensagem chega no celular.

4. **Não-regressão broadcasts:** disparar 1 broadcast manual com 2
   destinatários, confirmar `status='sent'` em ambos.

---

## Critérios de aceite

- [ ] Toda instância criada após o deploy nasce com `config.apikey` populado.
- [ ] Extrator de apikey centralizado em `_shared/evolution-client.ts`,
      sem duplicação de código entre backfill e create.
- [ ] Unit tests do extrator cobrem shapes documentados (token, apikey, hash,
      wraps `instance` / `Instance`).
- [ ] `bun run build`, `bunx tsc --noEmit`, vitest verdes.
- [ ] Smoke com instância nova: SQL confirma `has_apikey=true`, mensagem de
      teste vai com sucesso.
- [ ] Broadcasts continuam funcionando (não-regressão).
- [ ] PR com descrição linkando este prompt + findings da Etapa 1.

---

## Notas

- **Não remover** o backfill — ele continua útil como rede de segurança
  pra recuperar instâncias que escapem do fluxo (ex: criação manual via
  Postman, instâncias importadas de outro Evolution, etc).
- Se na Etapa 1 descobrir que a criação **já** captura apikey e o problema
  é em outro lugar (ex: row sendo criada antes do fetch da apikey), parar
  e reportar — não improvisar.
- **Logging:** quando apikey não puder ser extraído, log deve incluir
  `instance_name`, status HTTP da response, e os primeiros ~200 chars do
  body (truncar pra não vazar token em logs externos). Não logar payload
  inteiro em prod.

---

## Branch e PR

- Branch: `su8-3-create-apikey-capture`
- PR título: `feat(provider): captura apikey ao criar instância (SU8.3)`
- PR descrição:
  - link pra este prompt;
  - findings da Etapa 1 (caminho exato do edge + shape do response);
  - lista de arquivos tocados;
  - checklist de smoke executado (com SQL real);
  - confirmação de não-regressão broadcasts.
