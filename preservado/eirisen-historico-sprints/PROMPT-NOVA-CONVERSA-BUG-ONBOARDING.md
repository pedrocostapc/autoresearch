# Prompt — Nova Conversa: Bug Onboarding reabrindo após login

> Cole este prompt no início de uma nova conversa Claude.

---

## CONTEXTO RÁPIDO

Sou Pedro, founder do Risen OS — SaaS multi-tenant de CRM WhatsApp com IA. Tenants se cadastram, fazem onboarding, e depois usam o CRM normalmente.

**Stack:** React + TypeScript + Tailwind + Supabase + Stripe + shadcn. Dev via Lovable + Claude Code (terminal local).

**Projeto Supabase:** `qbclqjkvovfriuhshkpw`
**Repo:** `pedrocostapc/risen-ai-connect`

---

## O BUG

**Alguns tenants que JÁ concluíram o onboarding voltam a ver a tela de onboarding ao logar novamente.**

Não acontece com todos. Não é consistente. Comportamento esperado: uma vez concluído, login direto leva pro dashboard (`/hoje` ou `/inbox`).

---

## SCHEMA RELEVANTE

### Tabela `tenants`

Existe coluna `onboarding_completed` (boolean). Define se o tenant terminou ou não.

```sql
-- Confirma coluna existe
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'tenants' 
  AND column_name = 'onboarding_completed';
```

### Fluxo esperado

```
1. User faz signup → trigger handle_new_user cria tenant
2. Tenant inicia com onboarding_completed = false
3. User faz onboarding (preenche caixas, conecta WhatsApp)
4. Ao concluir: UPDATE tenants SET onboarding_completed = true
5. Próximos logins: AppShell verifica → vai direto pro dashboard
```

---

## PISTAS POSSÍVEIS

### A) Onboarding marca como true mas algum trigger reseta
Algum migration ou trigger pode estar fazendo UPDATE pra false ou DEFAULT em casos específicos.

### B) Hook lê de fonte errada
`useTenantOnboardingStatus` ou similar pode estar lendo de campo errado (cache, prop stale).

### C) Race condition no login
Sessão Supabase é restaurada antes do tenant ser totalmente carregado. AppShell mostra onboarding por default e depois corrige.

### D) Onboarding nunca foi marcado como completo pra esses tenants
Bug do passado — alguns tenants finalizaram onboarding em versão antiga do código que não fazia o UPDATE.

### E) Frontend invalidation falha
React Query não invalida cache após onboarding completar. Próximo login mostra dado antigo (stale).

---

## SQL PRA RODAR DE CARA

```sql
-- 1. Estado atual de onboarding_completed dos tenants
SELECT 
  COUNT(*) FILTER (WHERE onboarding_completed = true) AS completos,
  COUNT(*) FILTER (WHERE onboarding_completed = false OR onboarding_completed IS NULL) AS pendentes,
  COUNT(*) AS total
FROM tenants;
```

```sql
-- 2. Tenants pendentes que JÁ TÊM caixas preenchidas (provavelmente concluíram mas flag não foi setada)
SELECT 
  t.name,
  t.slug,
  t.created_at,
  t.onboarding_completed,
  COUNT(pb.id) FILTER (WHERE pb.is_active = true) AS caixas_ativas
FROM tenants t
LEFT JOIN persona_boxes pb ON pb.tenant_id = t.id
WHERE t.onboarding_completed IS NOT true
GROUP BY t.id, t.name, t.slug, t.created_at, t.onboarding_completed
HAVING COUNT(pb.id) FILTER (WHERE pb.is_active = true) > 0
ORDER BY t.created_at DESC;
```

```sql
-- 3. Verifica se há trigger DB resetando o campo
SELECT trigger_name, event_manipulation, action_statement
FROM information_schema.triggers
WHERE event_object_table = 'tenants';
```

---

## INVESTIGAÇÃO PRA CLAUDE CODE

```
Bug: tenants que concluíram onboarding voltam a ver tela de onboarding ao logar novamente.

Não acontece com todos. Comportamento intermitente.

Investiga em ordem:

1. Schema tenants.onboarding_completed:
   - Tipo, default, constraints
   - Há trigger que pode resetar?

2. Onde é setado como TRUE:
   grep -rn "onboarding_completed" src/ supabase/
   - Edge ou hook que finaliza onboarding?
   - O UPDATE realmente roda?
   - Cobertura de testes?

3. Onde é LIDO no login:
   - AppShell.tsx ou similar
   - useTenantOnboardingStatus hook?
   - React Query cache invalidation funcionando?
   - Race condition (lê antes do tenant carregar)?

4. Logs de console em sessão real:
   - Pedro pode reproduzir bug em algum tenant teste
   - Anota tenant_id afetado
   - Roda SELECT no DB pra ver estado atual
   - Compara com sessão saudável

5. Tenants atuais "esquisitos":
   SELECT que retorna tenants com onboarding_completed=false mas que TÊM caixas preenchidas
   - Esses são candidatos óbvios pro bug
   - UPDATE manual pra resolver pontual?

Reporta achados antes de propor fix.

Branch sugerido: bugfix/onboarding-status-reabre
```

---

## INFORMAÇÕES ÚTEIS

### Outras tabelas relacionadas

- `tenant_ai_configs` (config IA, persona_mode etc)
- `users` (auth + tenant_id)
- `persona_boxes` (caixas de conhecimento)

### Componentes prováveis (precisa confirmar com Code)

- `src/app/layout/AppShell.tsx` — decide rota inicial pós-login
- `src/features/onboarding/*` — fluxo onboarding
- `src/features/auth/*` — login

### Tenants conhecidos pra testar

- Hospital Teste — onboarding_completed devia estar true
- Vanderlei — concluiu onboarding faz tempo
- Euca Brasil — concluiu onboarding faz tempo
- Costa, Risen Midia, juniobetel25 — outros candidatos

---

## SUA TAREFA AGORA (Claude da nova conversa)

1. Leia este prompt inteiro
2. Faça perguntas se algo não estiver claro
3. Receba os outputs SQL do Pedro
4. Oriente Pedro a colar o prompt pro Code (Etapa 1)
5. Valide achados, oriente fix
6. Acompanhe até deploy + smoke teste

**Estilo de comunicação:** Pedro prefere respostas curtas, objetivas. Sem ficar repetindo coisas que ele já sabe. Tom direto.

---

## ANEXOS RECOMENDADOS

Quando começar a nova conversa, anexe:

- `00-ESTADO-SESSAO-11-05.md` (estado consolidado do projeto)
- `00-CAIXAS-REFERENCIA.md` (referência das caixas)

Pra ter contexto completo do sistema.

---

**Fim do prompt.**
