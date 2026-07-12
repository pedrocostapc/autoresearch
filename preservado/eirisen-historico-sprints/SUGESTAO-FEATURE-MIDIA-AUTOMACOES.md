# Sugestão de Feature — Envio de Mídia em Automações

> Documento de proposta. Define o que é, casos de uso, escopo, riscos e plano de implementação.
> Pra discutir e depois virar prompt de implementação.

---

## 1. PROBLEMA / NECESSIDADE

Hoje o Risen tem **Automações** (aba `/automacoes`) mas só dispara texto. Tenants querem **enviar mídia** (foto, vídeo, áudio, PDF) pra:

- Uma lista pré-definida de números (broadcast)
- Um grupo específico
- Um segmento dinâmico (ex: "todos clientes do bairro X")

**Casos de uso reais:**

| Cenário | Tenant exemplo |
|---|---|
| Foto promocional do dia | Pizzaria → grupo de clientes VIP |
| Cardápio em PDF semanal | Restaurante → lista de clientes |
| Vídeo demonstrativo de produto | Construbase → carteira ativa |
| Card de aniversário com foto | Salão de beleza → contato aniversariante |
| Tabela de preços atualizada | Euca Brasil → lista de revendedores |

---

## 2. CONCEITO

**Biblioteca de mídia + Automação de envio + Lista de destino.**

### Componentes

**A) Biblioteca de Mídia (`/automacoes/biblioteca` ou similar)**
- Upload de foto/vídeo/PDF/áudio
- Storage no Supabase Storage
- Tagging (ex: "promoção", "cardápio", "institucional")
- Vencimento opcional (ex: arquivar depois de 30 dias)
- Preview inline

**B) Lista de Destino (`/automacoes/listas`)**
- Lista nomeada (ex: "Clientes VIP Pizzaria")
- Composição:
  - Manual (escolhe contatos)
  - Filtro dinâmico (ex: tag "vip", última compra > 30 dias)
  - Importar CSV
- Ou: link com 1 grupo específico (whatsapp_jid)

**C) Automação de Envio**
- Escolhe mídia da biblioteca
- Escolhe lista/grupo destino
- Texto de acompanhamento (caption)
- Agendamento (imediato ou agendado pra horário)
- Throttling (delay entre envios pra não spammar Evolution)

---

## 3. UX PROPOSTA

### Tela "Nova Automação de Mídia"

```
┌─────────────────────────────────────────────────┐
│ Nova automação de mídia                          │
│                                                  │
│ 1. Escolha a mídia                              │
│ ┌──────┬──────┬──────┐                          │
│ │ [+]  │ foto │ pdf  │ ← biblioteca             │
│ └──────┴──────┴──────┘                          │
│                                                  │
│ 2. Mensagem (opcional)                          │
│ ┌──────────────────────────────────────────┐   │
│ │ Olá! Confira nossa promoção da semana... │   │
│ └──────────────────────────────────────────┘   │
│                                                  │
│ 3. Destino                                       │
│ ○ Lista existente: [Clientes VIP ▼]            │
│ ○ Grupo: [Grupo Promoções WhatsApp ▼]          │
│ ○ Manual (cola números aqui)                    │
│                                                  │
│ 4. Quando enviar                                │
│ ● Agora                                          │
│ ○ Agendar: [data] [hora]                       │
│                                                  │
│ 5. Velocidade                                    │
│ Delay entre envios: [5] segundos                │
│                                                  │
│        [Cancelar]  [Disparar →]                 │
└─────────────────────────────────────────────────┘
```

### Tela "Disparo em andamento"

```
Enviando "Promoção da Semana" — 47/200
Próximo envio em 5s

┌──────────────────────────────┐
│ ✓ +5538... (entregue 14:32)  │
│ ✓ +5538... (entregue 14:33)  │
│ ⏳ +5538... (enviando)        │
│ ⏳ +5538... (aguardando)      │
│ ...                           │
└──────────────────────────────┘

[Pausar]  [Cancelar]
```

### Tela "Biblioteca"

Grid de cards com preview, peso do arquivo, tags, data upload, ações (editar/excluir/usar em automação).

---

## 4. RISCOS E LIMITES (IMPORTANTE)

### Risco 1 — Spam / ban do WhatsApp

WhatsApp baniu números que dispararam em massa. Mitigações:

- **Limite máximo por dia por tenant** (ex: 500 envios)
- **Delay obrigatório entre envios** (mínimo 3s, recomendado 5-10s)
- **Aviso na UI** sobre risco de ban
- **Termos de uso** explicitando responsabilidade do tenant
- **Detecção de patterns suspeitos** (ex: 100% taxa de envio rejeitado = bloqueia)

### Risco 2 — Legal (LGPD / CDC)

Disparar mídia pra contatos sem consentimento é violação.

- **Opt-in obrigatório** — só pode enviar pra quem aceitou comunicação
- **Opção de descadastro** em cada mensagem
- **Histórico de consentimento** auditável

### Risco 3 — Custo de storage

Mídia (especialmente vídeo) consome storage rápido.

- **Limite de storage por plano** (já existe `armazenamento` no plano)
- **Compressão automática** de fotos > 5MB
- **Limite de tamanho por arquivo** (ex: 16MB pra vídeo, padrão WhatsApp)

### Risco 4 — Custo de envio

Cada envio chama Evolution API. Sem cobrança direta hoje, mas há custos de infra.

- **Limite por plano** (ex: Negócio = 1000 envios/mês, Iniciante = 100)
- **Pacote adicional** vendável (ex: R$X por 1000 envios extras)
- **Métrica visível** no `/admin/dashboard`

### Risco 5 — Mensagens repetidas / duplicação

Disparo executado 2x por erro = cliente recebe 2x = bad UX.

- **Idempotência** — automação tem ID único, garante 1 envio por destinatário
- **Histórico visível** pra cada disparo
- **Confirmação dupla** antes de disparar massa

---

## 5. SCHEMA PROPOSTO

### Tabelas novas

**`media_library`:**
```sql
CREATE TABLE public.media_library (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid REFERENCES tenants(id) NOT NULL,
  name text NOT NULL,
  description text,
  media_type text NOT NULL CHECK (media_type IN ('image','video','audio','pdf')),
  storage_path text NOT NULL,
  size_bytes bigint NOT NULL,
  tags text[],
  expires_at timestamptz,
  created_by uuid REFERENCES users(id),
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);
```

**`broadcast_lists`:**
```sql
CREATE TABLE public.broadcast_lists (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid REFERENCES tenants(id) NOT NULL,
  name text NOT NULL,
  type text NOT NULL CHECK (type IN ('manual','filter','group')),
  filter_json jsonb,  -- se type=filter, regras
  group_jid text,     -- se type=group, JID do whatsapp
  member_count int DEFAULT 0,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);
```

**`broadcast_list_members`:**
```sql
CREATE TABLE public.broadcast_list_members (
  list_id uuid REFERENCES broadcast_lists(id) ON DELETE CASCADE,
  contact_id uuid REFERENCES contacts(id),
  opted_in_at timestamptz,
  opted_out_at timestamptz,
  PRIMARY KEY (list_id, contact_id)
);
```

**`media_broadcasts`** (disparo individual):
```sql
CREATE TABLE public.media_broadcasts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid REFERENCES tenants(id),
  media_id uuid REFERENCES media_library(id),
  list_id uuid REFERENCES broadcast_lists(id),
  caption text,
  scheduled_at timestamptz NOT NULL,
  delay_seconds int DEFAULT 5,
  status text DEFAULT 'pending' CHECK (status IN ('pending','running','completed','failed','cancelled')),
  total_recipients int,
  sent_count int DEFAULT 0,
  failed_count int DEFAULT 0,
  created_at timestamptz DEFAULT now(),
  started_at timestamptz,
  finished_at timestamptz
);
```

**`broadcast_recipients`** (cada envio individual):
```sql
CREATE TABLE public.broadcast_recipients (
  broadcast_id uuid REFERENCES media_broadcasts(id) ON DELETE CASCADE,
  contact_id uuid REFERENCES contacts(id),
  status text DEFAULT 'pending' CHECK (status IN ('pending','sent','failed','skipped')),
  provider_message_id text,
  error_message text,
  sent_at timestamptz,
  PRIMARY KEY (broadcast_id, contact_id)
);
```

---

## 6. ESCOPO POR FASES

### MVP (1 PR ~2 dias)

- Upload de mídia (foto + PDF apenas, sem vídeo/áudio inicialmente)
- Biblioteca simples (lista + preview + delete)
- Disparo manual (cola números no textarea)
- Delay fixo de 5s
- Sem agendamento, sem listas salvas

**Deliverable:** tenant consegue subir foto + colar 10 números + disparar.

### Fase 2 (1 PR ~2 dias)

- Listas salvas (manuais)
- Histórico de disparos (`media_broadcasts`)
- Métricas básicas (enviado/falhou)

### Fase 3 (1 PR ~3 dias)

- Listas com filtro dinâmico (segmentação)
- Disparo agendado
- Pausa/cancelar em andamento

### Fase 4 (1 PR ~2 dias)

- Vídeo + áudio
- Compressão automática
- Limite por plano + monitoramento

### Fase 5 (futura)

- Opt-in/opt-out automático
- Templates de campanhas
- A/B testing de mensagens
- Métricas de engajamento

---

## 7. EDGE FUNCTION

**`broadcast-dispatcher`** — processa broadcasts pendentes.

Fluxo:
1. Cron (a cada 1min) pega `media_broadcasts` com `status='pending'` e `scheduled_at <= NOW()`
2. Marca `status='running'`
3. Pega lista de destinatários
4. Pra cada destinatário:
   - Chama Evolution API com mídia + caption
   - Aguarda `delay_seconds`
   - Salva `broadcast_recipients.status` + `provider_message_id`
5. Ao terminar todos, marca `status='completed'`
6. Se interrompido, marca `status='failed'` e mantém destinatários pendentes pra retry manual

---

## 8. INTEGRAÇÃO COM EVOLUTION

Evolution já suporta mídia. Endpoint:

```
POST /message/sendMedia/:instance
{
  "number": "5538998765432",
  "mediatype": "image|video|audio|document",
  "mimetype": "image/jpeg",
  "media": "<base64 ou URL>",
  "fileName": "promo.jpg",
  "caption": "Confira nossa promoção!"
}
```

Risen precisa:
- Subir mídia pro Storage do Supabase
- Gerar URL pública assinada (com expiração)
- Passar URL pra Evolution
- Tratar erros (mídia muito grande, formato inválido, número sem WhatsApp)

---

## 9. UI VISUAL — PADRÃO RISEN

Manter Editorial Noir:

- Cards grandes com bordas finas
- Cores: accent verde-limão (`--accent`), texto preto
- Tipografia: títulos em serif, monoespaço em metadados
- Sem cores chamativas pra status (use opacidade e tom)
- Layout: 12 colunas, gap-8 entre seções

---

## 10. PROMPT PRO CLAUDE CODE (quando estiver pronto pra implementar)

```
Feature nova — Envio de Mídia em Automações.

MVP escopo:
- Aba nova /automacoes/midia
- Upload imagem (jpg/png) ou PDF
- Biblioteca lista + preview + delete
- Disparo manual: cola números no textarea, escolhe mídia da biblioteca, opcional caption
- Delay fixo 5s entre envios
- Sem agendamento, sem listas salvas, sem segmentação

Schema novo:
- media_library (id, tenant_id, name, media_type, storage_path, size_bytes, tags, created_at)
- media_broadcasts (id, tenant_id, media_id, recipients_jsonb, caption, status, sent_count, created_at)

Edge nova:
- broadcast-dispatcher (cron a cada 1min, processa pending)

Integração:
- Storage Supabase pra mídia
- Evolution API endpoint /message/sendMedia/:instance

UI:
- Aba /automacoes/midia 
- Card "Biblioteca" + Card "Novo disparo"
- Manter Editorial Noir

Restrições MVP:
- Sem listas salvas
- Sem agendamento
- Sem vídeo/áudio
- Sem segmentação dinâmica
- Sem limite de envios por plano (Sprint Plans futura)

Riscos a sinalizar pro usuário na UI:
- Banner "Envios em massa podem causar ban do WhatsApp"
- Confirmação dupla antes de disparar pra >10 números

Investiga ANTES de propor fix:
1. Storage Supabase já tem bucket configurado?
2. Como mídia é enviada hoje via Evolution (lookup em mensagens existentes)?
3. Padrão de cron existente no projeto pra reusar setup?
4. Como integrar com /automacoes existente ou criar aba nova?

Reporta achados antes de propor fix.

Branch: feat/media-broadcasts-mvp

PR title: feat(automacoes): MVP envio de mídia
```

---

## 11. DECISÕES PRA PEDRO CONFIRMAR ANTES DE COMEÇAR

| # | Questão | Sugestão |
|---|---|---|
| Q1 | Começa com MVP enxuto ou escopa fase 1+2 junto? | MVP primeiro, valida com tenant real |
| Q2 | MVP suporta grupos OU listas OU só números colados? | Só números colados (simples) |
| Q3 | Storage Supabase ou outro? | Supabase Storage (já temos) |
| Q4 | Limite de tamanho de arquivo no MVP? | 5MB foto / 10MB PDF |
| Q5 | Caption obrigatório ou opcional? | Opcional |
| Q6 | Cobrar como add-on no plano ou liberado? | Liberado no MVP, depois cobra via Sprint Plans |
| Q7 | Tipos de mídia no MVP? | Imagem + PDF (vídeo/áudio fica fase 4) |
| Q8 | Aba nova `/automacoes/midia` ou modal dentro de /automacoes? | Aba nova (mais espaço) |

---

## 12. DEPENDÊNCIAS COM OUTRAS SPRINTS

- **Sprint Plans** (downgrade controlado) — quando rodar, define limites de envios por plano
- **SU7** (image send/receive) — feature paralela de receber mídia, pode aproveitar setup
- **Monitor Anthropic** — se for fazer, monitora também volume de broadcasts

Sem bloqueios fortes. Pode começar isolada.

---

## 13. PRÓXIMO PASSO

Pedro confirma:

1. Quer começar o MVP? Quando?
2. Responde Q1-Q8
3. Anexa este doc + prompt na próxima conversa com Code
4. Code roda Etapa 1, propõe fix, Pedro autoriza

---

**Fim do documento.**
