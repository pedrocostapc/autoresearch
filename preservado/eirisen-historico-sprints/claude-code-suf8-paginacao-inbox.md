# SUF8 — Paginação reversa do inbox

> Sprint de fix infra. Substitui o load fixo de 500 mensagens (asc + truncate) por
> paginação reversa estilo chat. Resolve o bug onde conversas longas
> (>500 mensagens) nunca mostravam mensagens novas no inbox.

---

## Contexto / raio-x do bug

### Sintoma observado

- Pedro está logado em `pedro@pcconstrutora.com.br`, tenant `bcdd0e10-b88c-49e6-9f58-81836831f68a`, super_admin.
- Abre a conversa **CONSTRUAI** (`cd9132ea-817e-40d8-8a10-471b3c6bd575`, contato `553899526799`).
- Manda uma mensagem nova pelo CRM. A mensagem chega no celular do destinatário ✅.
- A mensagem **não aparece no inbox**. F5 não resolve.
- O mesmo comportamento **não ocorre** em outras conversas do mesmo tenant.

### Diagnóstico

Mensagem de teste `Kx7mP2qZ9w` enviada pelo CRM. SQL na `messages`:

```
sender=agent, conversation_id=cd9132ea-..., tenant_id=bcdd0e10-...,
contact=CONSTRUAI, phone=553899526799, jid=553899526799@s.whatsapp.net
created_at=2026-05-09 15:24:26.478065+00
```

INSERT está **correto**. A mensagem foi gravada na conversation certa, no tenant
certo, com sender=agent. Bug não é gravação.

### Causa raiz

Network tab do DevTools no front:

```
GET /rest/v1/messages
    ?conversation_id=eq.cd9132ea-817e-40d8-8a10-471b3c6bd575
    &order=created_at.asc
    &limit=500
```

Retorna 200 OK com **500 mensagens, todas até 08/05 22:34 BRT** — porém a tabela
tem **655 mensagens** nessa conversation.

Com `order=asc&limit=500`, o Postgrest devolve as **500 mais antigas** e trunca
as 155 mais recentes (incluindo todas as de hoje). O front nunca enxerga
mensagens novas em conversations que cruzaram a barreira de 500.

Outras conversations do mesmo tenant funcionam porque têm <500 mensagens
históricas — o limit nunca trunca.

### Por que o limite atual é incompatível com o produto

Risen vende planos com retenção de 30 / 180 / 365 dias e pacotes de GB de
storage. Um limite hardcoded de 500 mensagens na carga inicial:
- contradiz a promessa de histórico longo;
- piora UX em conversas ativas (clinicas, lojas com volume diário);
- carrega 500 msgs upfront mesmo quando o usuário só quer ver as últimas 20.

Solução: paginação reversa estilo WhatsApp/Telegram — carrega N mais recentes
primeiro, scroll up busca mais antigas sob demanda.

---

## Objetivo

Refatorar o hook de leitura de mensagens do inbox para:

1. **Carga inicial:** as N mais recentes via `order=desc&limit=N`, revertidas no
   client para render cronológico ascendente.
2. **Scroll reverso:** ao chegar no topo da viewport, buscar próxima página
   usando cursor `created_at < primeira_carregada`.
3. **Realtime:** mantém append automático de mensagens novas (não regressão).

Sem mexer em retenção/storage — isso continua sendo política do banco / de plano
e está fora do escopo desta sprint.

---

## Escopo

### IN

- Hook que lista mensagens do inbox (`useMessages(conversationId)` ou nome
  equivalente — descobrir no repo).
- Componente do inbox / janela de conversa que consome esse hook.
- Lógica de scroll reverso + indicador "carregando mais".
- Constantes de tamanho de página.

### OUT (não tocar nesta sprint)

- Lógica de envio de mensagens.
- Webhook handler.
- RLS de `messages`.
- Retenção / archive / política de plano.
- Search de mensagens dentro da conversa (sprint futura).

---

## Pré-requisitos

- Branch nova a partir de `main`: `suf8-paginacao-inbox`.
- Build + tsc + vitest verdes antes de começar.

---

## Plano de execução

### Etapa 1 — Mapear código atual (raio-x)

Antes de qualquer mudança, descobrir e listar:

1. **Hook que carrega mensagens.** Busca por `messages` + `from(` ou `.select(`
   + `.eq('conversation_id'`. Provavelmente em `src/features/inbox/hooks/` ou
   `src/hooks/`. Reportar caminho exato.
2. **Componente que renderiza a lista de mensagens.** Procurar pelo consumidor
   do hook acima.
3. **Realtime subscription** existente em `messages`. Ela precisa continuar
   funcionando após o refactor — confirmar que existe e onde.
4. **Constante atual `limit=500`** (ou similar). Reportar valor + caminho.

Não codar nada nesta etapa. Só raio-x. Reportar findings em comentário no diff
ou no PR.

### Etapa 2 — Refatorar hook para paginação reversa

Assinatura sugerida (ajustar ao padrão do repo):

```ts
type UseMessagesResult = {
  messages: Message[];          // já em ordem cronológica ascendente para render
  isLoading: boolean;           // carga inicial
  isLoadingMore: boolean;       // paginando para trás
  hasMore: boolean;             // false quando não há mais histórico
  loadMore: () => Promise<void>;
};

const PAGE_SIZE = 50; // carga inicial e cada página subsequente
```

Implementação:

- **Query inicial:**
  ```ts
  supabase
    .from('messages')
    .select('*')
    .eq('conversation_id', conversationId)
    .order('created_at', { ascending: false })
    .limit(PAGE_SIZE);
  ```
  Reverter o array antes de devolver para o consumidor (chat espera ordem asc
  para renderizar de cima pra baixo, com a mais recente embaixo).

- **`loadMore`:**
  ```ts
  supabase
    .from('messages')
    .select('*')
    .eq('conversation_id', conversationId)
    .lt('created_at', firstLoadedCreatedAt) // cursor da mais antiga atual
    .order('created_at', { ascending: false })
    .limit(PAGE_SIZE);
  ```
  Reverter, **prepend** ao state, atualizar cursor.

- **`hasMore`:** `false` quando a query retornar < `PAGE_SIZE` linhas.

- **Realtime:** ao receber `INSERT` em `messages` para esse `conversation_id`,
  fazer **append** ao final do array (não prepend). Já é o comportamento
  esperado — só validar que continua funcionando.

- **Reset:** quando `conversationId` muda, zerar tudo e recarregar.

### Etapa 3 — Ajustar componente do inbox

- Substituir consumo do hook antigo pelo novo.
- Adicionar handler de scroll: quando `scrollTop` chega perto de 0 (topo) e
  `hasMore && !isLoadingMore`, chamar `loadMore()`.
- Preservar posição visual ao prepend de mensagens antigas: salvar
  `scrollHeight` antes do prepend e ajustar `scrollTop` após render para
  manter a mensagem que estava no topo no mesmo lugar visual (padrão chat).
- Indicador "carregando mais" no topo durante `isLoadingMore`.
- Indicador "início da conversa" quando `!hasMore`.

### Etapa 4 — Testes

- **Unit (vitest):** mockar resposta do supabase, testar:
  - carga inicial com PAGE_SIZE+10 mensagens devolve PAGE_SIZE últimas em ordem
    asc;
  - `loadMore` faz query com `.lt('created_at', cursor)` correto;
  - `hasMore=false` quando retorno < PAGE_SIZE;
  - reset ao trocar `conversationId`.
- **Build:** `pnpm build` (ou equivalente do repo) verde.
- **TSC:** sem erros.

### Etapa 5 — Smoke test em produção

Após deploy:

1. **CONSTRUAI (conversa de 655+ msgs):**
   - Abrir conversa. Deve carregar rápido (50 msgs).
   - Mensagens mais recentes devem estar visíveis no fundo.
   - Mandar uma mensagem nova → aparece no fundo via realtime ✅.
   - Scroll up até o topo → carrega próxima página (50 mais antigas), preserva
     posição visual.
   - Continuar scroll → eventualmente `hasMore=false`, mostra indicador de
     início.

2. **Conversa curta (<50 msgs):**
   - Abre normal, `hasMore=false` desde o início, sem regressão.

3. **Múltiplas conversations:**
   - Trocar entre conversas — cada uma reseta seu estado de paginação
     corretamente.

4. **Realtime:**
   - Abrir conversa em duas abas. Mandar mensagem em uma. Aparece na outra via
     realtime, no fundo, sem duplicar.

---

## Critérios de aceite

- [ ] Conversa CONSTRUAI (`cd9132ea-817e-40d8-8a10-471b3c6bd575`) abre e mostra
      mensagens de hoje sem F5.
- [ ] Mensagens novas enviadas pelo CRM aparecem no inbox imediatamente
      (realtime).
- [ ] Scroll up em conversa longa carrega mais histórico, sem pular posição.
- [ ] Conversas curtas continuam funcionando, sem regressão.
- [ ] `pnpm build`, `pnpm tsc` e `pnpm vitest` verdes.
- [ ] PR com descrição linkando este prompt e o diagnóstico do bug.

---

## Notas

- **Não mexer** em retenção, RLS, ou política de plano. Esta sprint é só
  paginação no front.
- A linha de mensagem `sender=contact` em outro tenant (`5c6dc551`) que apareceu
  no SQL de diagnóstico **não é parte deste bug** — é outra instância Evolution
  capturando webhook em conta separada. Fora de escopo.
- Se durante o raio-x da Etapa 1 aparecer algum motivo técnico que impeça a
  paginação reversa (ex: realtime acoplado ao array completo de forma rígida,
  RLS que exige comportamento específico), **parar e reportar** antes de
  improvisar workaround.

---

## Branch e PR

- Branch: `suf8-paginacao-inbox`
- PR título: `feat(inbox): paginação reversa de mensagens (SUF8)`
- PR descrição:
  - link pra este prompt;
  - resumo do diagnóstico (limit=500 + asc trunca conversas longas);
  - lista de arquivos tocados;
  - checklist de smoke test executado.
