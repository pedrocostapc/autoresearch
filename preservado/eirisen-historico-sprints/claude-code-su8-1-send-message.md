# SU8.1 — Migrar provider-send-message pra wa.crm

## Objetivo

Migrar envio outbound de texto do `provider-send-message` do proxy `api.crm` (com `x-api-key` global) pro Evolution direto `wa.crm` (com `apikey` por instância).

Pré-requisito: SU8.0 fechado (apikey populada em todas as 18 instâncias). ✅

## Fase 1 — Raio-x antes do código

**Sem escrever código novo.** Mostre raw:

### 1.1 Estado atual de provider-send-message

Mostre `supabase/functions/provider-send-message/index.ts` completo. Quero ver:
- Como resolve `provider.config` no lookup (linhas ~134-142)
- Como chama Evolution hoje (linhas ~255-281)
- Como faz o INSERT/UPDATE em `messages` antes/depois da chamada (linhas ~161-200)
- Como trata erro
- Branch Cloud API (linhas ~309-373) — confirmar que é totalmente isolado

### 1.2 Existe algum helper compartilhado em `_shared/`?

```
ls supabase/functions/_shared/
```

Se já houver `evolution-client.ts` ou similar, mostre. Se não, vamos criar.

### 1.3 Greps relacionados

```
"sendText"
"/message/send"
"evolution-client"
"EVOLUTION_BASE"
```

Quero saber se outras edges já têm padrão pronto.

## Fase 2 — Plano de implementação (após raio-x)

Espera meu OK depois do raio-x. Plano provável:

### Helper novo: `_shared/evolution-client.ts`

Contrato esperado:
```ts
export const EVOLUTION_BASE = "https://wa.crm.risenmidia.com.br";

export interface EvolutionConfig {
  instanceName: string;
  apikey: string;
}

export function evolutionConfigFromProvider(provider: { config: any }): EvolutionConfig | null {
  // Extrai instance_name + apikey do provider.config, retorna null se faltar
}

export async function sendTextViaEvolution(
  cfg: EvolutionConfig,
  args: { number: string; text: string; options?: Record<string, unknown> }
): Promise<{ ok: true; providerMessageId: string } | { ok: false; status: number; error: string }> {
  // POST /message/sendText/{instance} com header apikey
}
```

Razão de helper: SU8.2 (broadcasts) vai reutilizar a mesma chamada.

### Mudança em `provider-send-message`

1. Trocar bloco da chamada Evolution (linhas ~255-281) pra usar o helper
2. Resolver apikey de `provider.config.apikey` (já populado)
3. **Não** trocar lógica de fallback se apikey ausente — se faltar, retorna erro 4xx claro pra atendente saber
4. Manter Cloud API path 100% intocado (linhas ~309-373)
5. Manter INSERT em `messages` igual (mas já alertar que linha 169 `message_type: media_url ? "image" : "text"` tem bug — não corrigir nesta sprint, fica pra SU7b)

### Decisão pendente

- O envio de texto manda **algum body extra** hoje (delay, presence, linkPreview) que precisa preservar?
- Ver no proxy CRM (se conseguir) ou só replicar o comportamento atual: body simples `{ number, text }` sem options.

## Fase 3 — Smoke test

1. Enviar 1 mensagem de texto pelo inbox de produção
2. Conferir no banco:
   ```sql
   SELECT id, status, provider_message_id, sender, created_at
   FROM messages
   WHERE created_at > now() - interval '2 minutes'
     AND sender = 'agent'
   ORDER BY created_at DESC LIMIT 5;
   ```
   Esperado: `status='sent'`, `provider_message_id` populado (não null)
3. Conferir logs da edge (não pode ter erro 401, 502, etc)
4. Conferir no celular destino: mensagem chegou
5. Repetir com 2 instâncias diferentes (ex: `Pedro-1296` e `nudeck`) pra confirmar que apikey por instância funciona

## Branch e PR

Criar branch `feat/su8.1-send-message-wa-crm` e abrir PR depois do smoke. Não merge sem aprovação do Pedro.

## Não fazer nesta sprint

- ❌ Mídia outbound (SU7b)
- ❌ Migrar broadcasts (SU8.2)
- ❌ Migrar evolution-proxy (SU8.3)
- ❌ Migrar deleteMessageViaEvolution (SU8.4)
- ❌ Cleanup CRM_API_KEY env (SU8.5)
- ❌ Mexer em Cloud API path
- ❌ Arrumar bug do `message_type: media_url ? "image" : "text"` (fica pra SU7b)

## Output esperado

Comece com raio-x da fase 1. Espera meu OK antes da fase 2.
