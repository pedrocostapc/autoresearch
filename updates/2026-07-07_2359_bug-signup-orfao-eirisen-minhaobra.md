# Bilhete — bug de signup órfão (Ei Risen + MinhaObra) — pra outro agente pegar

Handoff rápido (o Pedro vai abrir outro agente pra planejar/consertar isso; NÃO é o
foco da sessão atual, que é unificar os sistemas). Descoberto em jul/2026 durante uma
faxina de contas.

## Sintoma
Acúmulo de **tenants/contas órfãs** (criados sem completar cadastro). Só nos apps com
**signup público**:
- **Ei Risen** (`qbclqjkvovfriuhshkpw`): tinha 61 tenants, **~30 órfãos** (0 user, 0
  onboarding, 0 email) — LIMPO nesta sessão (sobraram 24 reais).
- **MinhaObra** (`uytnnaazexttxzjquxxd`, repo `~/minhaobra/pedro-obras`): 8 empresas, 9
  profiles, mas **34 contas auth** → **~25 auth órfãs** (signup abandonado, sem profile).
  AINDA NÃO limpo.

## Pista da causa (não confirmada — investigar)
No Ei Risen o **tenant nasce ANTES de completar o onboarding**. Evidência: os órfãos
tinham o NOME da pessoa (ex.: "Pedro Henrique Ferreira da Costa CRM" ×8) mas 0 users e
0 `onboarding_sessions` → o tenant foi criado num passo inicial (nome) e a pessoa desistiu,
deixando a casca. Onde olhar (repo `~/Dev/risen/risencrm/risen-ai-connect`):
- `supabase/functions/complete-onboarding/index.ts` (faz insert em tenants — mas é o FIM).
- Procurar quem cria o tenant no INÍCIO do signup/onboarding (antes de complete).
- Checar TRIGGER no `auth.users` (handle_new_user) que cria tenant/profile no signup.
- `onboarding_sessions` guarda CNPJ/áudio/setor, SEM email — o onboarding é por voz/CNPJ.

## Conserto sugerido (a planejar)
1. **Criar o tenant só na conclusão** (ou marcar como `draft` e só "ativar" ao completar).
2. **Cron de purga**: apagar tenants/contas em onboarding abandonado há > X dias (0 user +
   0 mensagem + 0 instância).
3. Aplicar o MESMO nos dois apps (Ei Risen + MinhaObra têm o mesmo padrão).

## Como limpar o que já existe (mecânica provada nesta sessão)
Deletar tenant no Ei Risen **cascateia limpo** (54 FKs ON DELETE CASCADE — contatos,
mensagens, users, etc.). `auth.users` NÃO cascateia (limpar à parte, conferindo antes se a
conta não pertence a tenant que fica). Planilha de auditoria: gerar CSV com sinais
(TEM_CONTA, INST_CONECTADA, TEM_MENSAGEM, última_msg) + coluna DELETAR pro dono marcar.
Ver memória [[frota-refs-e-caminhos]].
</content>
