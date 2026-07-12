# SU7a — Raio-X (mapeamento antes de implementar)

## Objetivo

**Não escrever código nesta etapa.** Só mapear o estado atual do projeto pra gente decidir o pipeline de mídia (SU7a) com base no que existe, não no que eu chutei. Saída esperada: um relatório markdown único respondendo todas as seções abaixo.

## Contexto rápido

Estamos prestes a implementar recepção de mídia (descriptografia + storage + render) no inbox WhatsApp. WhatsApp manda mídia criptografada E2E e hoje o frontend tenta renderizar o `.enc` direto, quebrando imagem/vídeo/áudio/documento. O plano é: webhook detecta mídia → edge function chama `POST /chat/getBase64FromMediaMessage/{instance}` no Evolution → decode base64 → upload Supabase Storage → frontend renderiza signed URL.

Antes de escrever isso, preciso do raio-x abaixo.

---

## Seção 1 — Schema do banco

### 1.1 Tabela `messages`
- Liste **todas as colunas** com tipos
- Destacar colunas relacionadas a mídia (`media_url`, `message_type`, e qualquer outra)
- Tem alguma coluna `media_*` além das óbvias?
- Qual o tipo de `message_type`? Enum, text, varchar?
- Quais são os valores que `message_type` recebe hoje? (rodar `SELECT DISTINCT message_type FROM messages LIMIT 50`)

### 1.2 Tabela de instâncias do WhatsApp / Evolution
- Qual é o nome exato da tabela que guarda as instâncias do Evolution por tenant?
- Liste colunas e tipos
- Onde estão as credenciais (URL do Evolution, API key)? Em coluna texto, em `vault`, em `tenant_settings`, em outro lugar?
- Como o `provider-webhook` resolve qual instância é qual hoje?

### 1.3 Multi-tenancy
- Qual é o nome exato da tabela que mapeia user → tenant? (chutei `tenant_members`)
- Liste colunas
- Tem coluna de role (super_admin, admin, member)?
- Como as RLS atuais do projeto verificam acesso ao tenant? (mostrar 1-2 policies de exemplo de outras tabelas)

### 1.4 Tabela `conversations`
- Liste colunas relevantes (especialmente `tenant_id`, `whatsapp_jid`, `instance_id` ou similar)
- Como o webhook resolve `conversation_id` quando chega uma mensagem nova?

### 1.5 Storage existente
- Já existe algum bucket no Supabase Storage do projeto? Listar todos com `SELECT id, name, public FROM storage.buckets`
- Tem alguma policy `storage.objects` já configurada? Mostrar quais

---

## Seção 2 — Edge functions

### 2.1 `provider-webhook`
- Caminho do arquivo
- **Cole o código completo** (ou a função principal se for longo) — preciso ver:
  - Como detecta tipo de evento (MESSAGES_UPSERT etc)
  - Como extrai `message_type`, `key.id`, `remoteJid`
  - Como insere em `messages` (campos passados)
  - Como resolve `conversation_id` e `tenant_id`
  - Trata mídia hoje? Salva alguma coisa em `media_url`?

### 2.2 `evolution-proxy`
- Existe? Caminho do arquivo
- O que faz hoje? (cole o código ou resumo + assinatura das funções)
- Como autentica no Evolution (API key vem de onde)?

### 2.3 Outras edges relevantes
- Lista todas as edges em `supabase/functions/`
- Marca quais tocam em `messages` ou `conversations`

### 2.4 Padrão de invocação async
- Já tem algum lugar no código usando `EdgeRuntime.waitUntil` ou `supabase.functions.invoke` fire-and-forget?
- Se sim, qual é o padrão usado?

---

## Seção 3 — Frontend

### 3.1 Renderização atual de mensagem
- Qual componente renderiza cada mensagem no inbox? (procurar por `MessageBubble`, `MessageItem`, `ChatMessage`, etc — caminho do arquivo)
- **Cole o JSX que decide entre texto vs mídia hoje** (aquele que está mostrando "Imagem" como alt text quebrado nos prints)
- Como hoje ele tenta renderizar imagem/vídeo/áudio/documento?

### 3.2 Subscription Realtime do inbox
- Já existe Realtime subscription pra atualizar mensagens em tempo real?
- Caminho do hook ou contexto
- O `select` da subscription pega quais campos hoje?

### 3.3 React Query / TanStack
- Versão do `@tanstack/react-query`
- Onde está a config do `QueryClient`
- Qual o padrão de cache invalidation usado em outras queries (ex: quando insere uma mensagem nova)?

### 3.4 shadcn / UI
- Confirma que `lucide-react` está instalado e disponível
- Tem algum componente de "skeleton" ou "loader" já padronizado pra usar enquanto mídia processa?

---

## Seção 4 — Sample real do payload Evolution

Capture **um payload real** de cada tipo abaixo (do log do `provider-webhook` ou de uma mensagem recente no Evolution Manager). Cola JSON cru, ofuscando só dados sensíveis (telefone, tenant_id):

- `imageMessage`
- `videoMessage`
- `audioMessage` (PTT)
- `documentMessage`

Preciso ver:
- Onde está o `messageType` no payload (raiz? aninhado em `data.messageType`? `message.imageMessage`?)
- Onde está o `key.id` (que vai pro `getBase64FromMediaMessage`)
- Tem `mimetype` direto no payload do webhook ou só vem do Evolution na chamada de getBase64?
- Tem URL do `.enc` no payload (pra confirmar que é exatamente isso que o frontend está pegando hoje)?

---

## Seção 5 — Versão do Evolution e config atual

### 5.1 Evolution API
- Qual versão está rodando no droplet `crm-evolution-risen-dev-01`? (rodar `curl http://localhost:8080` ou checar docker-compose / package.json)
- Tem alguma config de S3/MinIO atual no `.env` do Evolution? (listar variáveis `S3_*` que existem hoje, mesmo se vazias)
- Qual o webhook URL configurado nas instâncias hoje? (aponta pro `provider-webhook` do Supabase, presumo, mas confirmar)

### 5.2 Endpoint `/chat/getBase64FromMediaMessage`
- Testar manualmente com `curl` em uma mensagem recente que tenha mídia. Cola request e response (ofuscando base64 longo) pra confirmar que funciona nessa versão do Evolution
- Confirma o formato exato do response (`mediaType`, `fileName`, `mimetype`, `base64`, `size.fileLength`)

---

## Seção 6 — Migrations e padrão do projeto

### 6.1 Como migrations são aplicadas
- Pedro tem 2 terminais: o "antigo" com auth Supabase CLI cacheada (db push funciona), o "novo" trava com erro de role. Qual está sendo usado pra esse sprint?
- Tem alguma migration recente como referência de estilo? (cola o nome do arquivo mais recente em `supabase/migrations/`)

### 6.2 Convenções
- Naming de tabelas: snake_case singular ou plural? (`message` vs `messages`)
- Naming de colunas timestamp: `created_at` / `updated_at` / `processed_at`?
- Padrão de RPC: `SECURITY DEFINER` ou `INVOKER`? Como verificam tenant na maioria das RPCs?

---

## Formato da saída

Um único relatório markdown com **todas as 6 seções respondidas em ordem**. Onde uma resposta for "não existe" ou "não encontrei", explicitar isso — não pular.

Não escrever código novo nesta etapa. Não criar migrations, não editar edges, não tocar em nada do frontend. Só leitura e relatório.

Quando terminar, salvar como `docs/sprints/su7a-raio-x.md` no repo (ou só colar no chat — o que for mais rápido).
