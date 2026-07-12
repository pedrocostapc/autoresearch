# Pendências Futuras — Pós 11/05/2026

> Fila de trabalho daqui pra frente, organizada por prioridade e dependências.

---

## 🔴 PRIORIDADE ALTA (próximos passos)

### 1. Validar Persona v3 no Euca Brasil
**O que:** Aplicar `persona-risen-v3.md` em algum slot do Euca pra ver se elimina problemas restantes.

**Onde aplicar:**
- Aba **Persona** → Passo 04 BETA → `manual_archetype_prompt`
- OU Aba **Avançado** → `system_prompt`

**Mudanças vs v1:**
- Apresentação obrigatória na 1ª mensagem (sem "atendente virtual")
- Seção 6.1 sobre catálogos com variações
- Lê `agent_name` e `communication_style` dos configs do tenant
- ~30% menor

**Como testar:**
1. WhatsApp Euca: "Oi" → IA deve dizer "Sou a Risen, da EUCA Brasil"
2. "Tem varão?" → IA usa hint, pergunta UF
3. "5m bitola 08 MS" → IA usa items do contexto (não chama tool de novo)

### 2. Bug Stripe — Risen Midia precisa de checkout real
**O que:** `stripe_subscription_id = NULL` em Risen Midia. Precisa de checkout REAL pra sincronizar.

**Como resolver:**
1. Pedro entra em Risen Midia
2. Aba Faturamento → escolhe plano Negócio
3. Completa checkout Stripe com cartão de verdade
4. Webhook captura `customer.subscription.created`
5. DB sincroniza com `stripe_subscription_id` real

### 3. Bug taxa delivery (centavos vs reais)
**Sintoma:** Pedro digitou `7080` na planilha (= R$70,80 humano) mas sistema armazenou como `7080` cru.

**Pendente investigar:**
- Schema delivery_areas armazena em centavos ou reais?
- import-box-excel converte?
- Pode estar mostrando 100x errado pra cliente final

**Próximo passo:**
- Edita manualmente uma área pelo form (não Excel)
- Roda SELECT pra ver como ficou
- Compara com como Excel armazena

---

## 🟡 PRIORIDADE MÉDIA

### 4. Sprint Plans — Downgrade controlado
**Conceito aprovado:**
- Trial sempre cria com plano Negócio (R$99 completo)
- Downgrade só com modal de fricção (remover usuário/instância antes)
- Upgrade sempre livre

**Estimativa:** 3 PRs, ~2 dias

**PRs propostos:**
- PR1: RPC/edge `validate_plan_change` + lógica de limites
- PR2: Modal de downgrade controlado + integração checkout
- PR3: Polishing UI + testes E2E

### 5. UX Mobile + PWA (PR estava em andamento)
**Status:** Code estava aplicando antes do bug crítico

**Mudanças propostas:**
- Landing: botão "Entrar" como primário (mobile)
- Composer com teclado: usar 100dvh + scrollIntoView
- PWA com `vite-plugin-pwa`: manifest + service worker
- Ícones já gerados em `/mnt/user-data/outputs/`

### 6. Doc técnica das caixas
**Prompt pronto:** `/mnt/user-data/outputs/claude-code-documentar-caixas.md`

**Não foi rodado ainda.** Geraria documentação completa de cada caixa (Establishment, Hours, Products, etc) com schema, campos, exemplos.

### 7. Sprint Forms
**Conceito:** formulário conversacional via WhatsApp, IA preenche pelos turnos, OTP por email pra assinatura digital.

**Estimativa:** 1.5 dia, 3 PRs

**Decisão pendente:** Tipos finais (sim_não/texto/número/data/email/hora/escolha).

---

## 🟢 PRIORIDADE BAIXA / SPRINTS FUTURAS

### 8. Sprint Templates por Nicho
**Não escopada ainda.** Vira sprint separada depois de Catalog + Forms + Schedule.

**Recomendação Nível 2:** presets pré-preenchidos por nicho (Clínica/Loja/Restaurante/Vendedor) sem mudar schema declarativo. Onboarding aplica preset.

**Estimativa:** M (~3-4 dias). NÃO fazer Nível 3 (schema dinâmico por nicho) pra não quebrar fundação.

### 9. SU7 — Image send/receive
**Status:** Schema `messages.media_url` e `message_type` existem.

**Requer:**
- Endpoint na edge pra enviar media via Evolution API
- UI pra human agent fazer upload
- AI tool `send_image()`
- Product catalog com `image_url`

### 10. UI refinement sprint (Editorial Noir)
**Status:** Deferido até funcionais fecharem.

**Conhecida deviação:** accent color teal em vez de burnt amber `#B8521B` (`prompt-lovable-v2.md` tem spec).

### 11. Monitoramento saldo Anthropic
**Causa do incidente do dia 11/05:** saldo zerou e todas IAs pararam.

**Solução proposta:**
- Card "Saldo Anthropic" no `/admin/dashboard`
- Alerta amarelo se < $20
- Alerta vermelho se < $5

**Estimativa:** 30 min.

---

## ⏸️ ADIADOS POR DECISÃO

### 12. Stripe key rotation
**Status:** Key `rk_live_51SMWd...` apareceu no chat. Pedro decidiu adiar rotação.

**Quando fizer:**
1. Stripe Dashboard → Developers → API keys
2. Roll na chave restricted
3. Atualiza secret no Supabase
4. Revoke a antiga

### 13. DROP COLUMN tenants.subscription_status
**Status:** Coluna abandonada (Caminho C). Ninguém mais lê. Fica cemitério até sprint futura.

**Quando fizer:** Após validar que nenhum código novo tocou. Recomendado 3-6 meses depois.

---

## 📋 DEPENDÊNCIAS ENTRE PENDÊNCIAS

```
1 (Persona v3 Euca)        → independente
2 (Stripe Risen Midia)     → independente
3 (Taxa delivery)          → independente
4 (Sprint Plans)           → depende de #2 estar OK
5 (UX Mobile + PWA)        → independente
6 (Doc caixas)             → independente
7 (Sprint Forms)           → após #4 (escopo similar)
8 (Templates nicho)        → após #7
9 (Image send/receive)     → independente
10 (UI refinement)         → após funcionais fecharem
11 (Monitor Anthropic)     → quick win, independente
```

---

## 🎯 SUGESTÃO DE PRÓXIMA SESSÃO

**Caminho A (consolidação):**
1. Aplica Persona v3 no Euca
2. Testa coerência IA com persona limpa
3. Resolve bug taxa delivery

**Caminho B (entrega de feature):**
1. UX Mobile + PWA (estava em andamento)
2. Adiciona monitoramento saldo Anthropic

**Caminho C (sprint nova):**
1. Sprint Plans downgrade controlado

Pedro escolhe quando voltar.

---

**Fim do documento.**
