# Diagnóstico — Estado do Resend

> Investigação read-only. **NÃO modifica nada.** Só reporta o estado atual de configuração + integração do Resend no projeto.
>
> Estimativa: ~30min.
> Sem branch (não toca código).

---

## Contexto

Sprint Forms (futura, ~2 dias estimado) e Sprint SA3 (Onboarding) precisam Resend funcional pra:
- OTP por email (validação de subscrição/submissão de formulário)
- Email de confirmação ao cliente após submissão
- Invite por email pra equipe (SU1 Fase 3, pausada)

Pedro confirmou hoje que Resend está "praticamente todo configurado". Memory anterior datava de quando ainda estava em setup. Precisa atualizar.

Objetivo: mapear estado real **agora**, identificar gaps, ter clareza do que falta antes de Sprint Forms começar.

---

## Investigação — 10 pontos

### 1. Secrets configurados

```bash
supabase secrets list 2>&1 | grep -i "resend\|app_url"
```

Reportar:
- `RESEND_API_KEY` existe? (não precisa mostrar valor, só presença)
- `APP_URL` existe? Qual valor?
- Outros secrets relacionados (`RESEND_FROM_EMAIL`, `RESEND_DOMAIN`, etc)

### 2. Edges que importam Resend

```bash
grep -rn "resend\|RESEND" supabase/functions/ --include="*.ts" -l
grep -rn "resend\|RESEND" supabase/functions/ --include="*.ts" | head -30
```

Reportar:
- Quais arquivos importam/usam Resend
- Se tem util/helper compartilhado (`_shared/resend.ts`?)
- Edges que mandam email atualmente

### 3. SDK Resend instalado

```bash
grep -A 1 "resend" supabase/functions/**/import_map.json 2>/dev/null
grep -A 1 "resend" supabase/functions/**/deno.json 2>/dev/null
cat supabase/functions/_shared/deno.json 2>/dev/null | grep -A 1 resend
```

Reportar:
- Versão do SDK Resend importada (se houver)
- Qual lib (npm:resend, https://esm.sh/resend, etc)

### 4. Função sendEmail / sendInvite existente?

```bash
grep -rn "sendEmail\|sendInvite\|sendOtp\|sendNotification\|emails\.send" \
  supabase/functions/ --include="*.ts" | head -20
```

Reportar:
- Função wrapper já existe?
- Edge dedicada `send-email` ou similar?
- Padrão de uso (template, plain text, html)

### 5. Templates de email

```bash
ls supabase/functions/**/templates 2>/dev/null
ls supabase/functions/_shared/email-templates 2>/dev/null
grep -rn "email.*html\|template.*email\|<html>" supabase/functions/ --include="*.ts" | head -10
```

Reportar:
- Templates HTML existentes
- Onde estão armazenados (arquivo .html? template literal inline? variável?)
- Se usa engine de templates (handlebars, mustache, etc)

### 6. Domínio remetente configurado

Olhar nas edges encontradas no item 2:
```ts
from: "..." // qual valor?
```

Reportar:
- Sandbox `onboarding@resend.dev` ou domínio próprio?
- Se for domínio próprio: qual?
- DNS configurado (precisa olhar Resend dashboard, mas Pedro confirma)

### 7. Supabase Auth integração

```bash
# Verifica config Auth (read-only via API)
curl -s "https://qbclqjkvovfriuhshkpw.supabase.co/auth/v1/settings" \
  -H "apikey: $SUPABASE_ANON_KEY" 2>&1 | head -30
```

Ou checa via gestão local:
```bash
grep -rn "site_url\|email_confirmation\|smtp" supabase/config.toml 2>/dev/null
cat supabase/config.toml 2>/dev/null | grep -A 5 "\[auth\]"
```

Reportar:
- `site_url` configurado pra onde
- Auth está usando SMTP customizado (Resend) ou default Supabase
- Email confirmation enabled?

### 8. Logs de envios recentes

Não dá pra acessar dashboard Resend via Code, mas dá pra inferir uso recente:

```bash
grep -rn "console\.log.*sent\|console\.log.*email\|resend.*success" \
  supabase/functions/ --include="*.ts" | head -10
```

Reportar:
- Tem logs estruturados de envios?
- Algum monitoramento existente?

### 9. Histórico do SU1 Fase 3

```bash
git log --all --oneline | grep -i "resend\|email\|invite" | head -20
```

Reportar:
- Commits relacionados a Resend/invite/email
- Quando foi a última mudança nesse contexto

### 10. Tabela de tracking de emails

```bash
grep -rn "email_logs\|email_sent\|mail_queue\|emails_sent" \
  src/ supabase/migrations/ --include="*.sql" --include="*.ts" 2>/dev/null | head -10
```

Reportar:
- Existe tabela pra registrar emails enviados/recebidos?
- Schema da tabela se houver

---

## Critérios de aceite do diagnóstico

- [ ] Cada um dos 10 itens reportado (com "não encontrado" se for o caso)
- [ ] Diagnóstico breve no final: o que está pronto vs o que falta pra Sprint Forms começar
- [ ] Sem modificar nada (puro read)
- [ ] Reportar de volta em formato estruturado

---

## Formato esperado do relatório

```markdown
# Diagnóstico Resend — Estado atual

## ✅ Pronto
- [item X]: detalhe
- [item Y]: detalhe

## 🟡 Parcial
- [item Z]: detalhe + o que falta

## ❌ Faltando
- [item W]: o que não foi encontrado

## Recomendação pra Sprint Forms
- [Lista do que precisa fazer ANTES de Sprint Forms começar]
```

---

## Restrições

- ❌ Não criar arquivos
- ❌ Não modificar config
- ❌ Não rodar migrations
- ❌ Não fazer commits
- ✅ Apenas grep, ls, curl read-only, git log
