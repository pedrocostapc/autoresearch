# eirisen — Caixas verticais: taxonomia fechada com o Pedro (sessão remota, 12/07 ~18h)

**Sessão:** eirisen (risen-ai-connect), remote control, Pedro no celular.
**Checkpoint de limite semanal** — estado gravado pra sessão que nasce sem memória.

## O que aconteceu (só design, ZERO código/deploy)
Pedro pediu pra olhar o prompt avançado do tenant dele (pedro@pcconstrutora.com.br,
tenant "Pedro Costa" bcdd0e10-b88c-49e6-9f58-81836831f68a) e comparar com as
caixas do "Sua Empresa". Conclusão dele: a caixa de Produtos não serve pra
imóvel/outdoor/SaaS — e fechamos uma taxonomia de **3 caixas novas**:

1. **Imóveis** (primeira) — matriz tipo Eventos; ficha completa + financiamento
   (entrada/PRICE/SAC/renda mínima). O contrato de caixa nova da sessão da manhã
   (`prompts/arquetipos-2-0/01-contrato-caixa-nova.md`) já usa 'imoveis' de exemplo.
2. **Planos & Assinaturas** — CRM + Risen OS + Minha Obra + Indoor numa matriz só.
3. **Mídia OOH** — placa=inventário, venda real=placa×bi-semana, complementos=
   serviços; disponibilidade FICA COM O PEDRO (fase 1); fase 2 = ocupação viva
   do Hub Mídia OOH via Core (Pedro confirmou: **Hub↔CRM ainda NÃO conectado**,
   vai conectar em algum momento).
4. Gráfica/gestão digital → caixa Serviços existente, sem código.

## Onde está tudo
- **Spec completa:** `prompts/caixas-verticais/00-taxonomia-portfolio-pedro.md`
  (commitada em main) + cópia global `~/Dev/risen/risencrm/prompts/caixas-verticais/`.
- Checklist obrigatório de implementação: `prompts/arquetipos-2-0/01-contrato-caixa-nova.md`.
- Memória persistente do projeto: `project_caixas_verticais_taxonomia.md`.

## Como retomar
- Implementar caixa Imóveis seguindo o contrato (enum via Management API →
  box-schemas.ts → persona-compiler.ts → persona-tools.ts → Zod do front → testes).
- **GATED:** enum/compiler/tool = motor da persona → cada etapa só com OK do Pedro.
- Dados pra popular: prompt avançado do Pedro (tenant_ai_configs.system_prompt,
  seção 7) e caixa products dele (persona_boxes, 16 itens — V1-V5, L1-L2, planos).
- Query no banco: Management API /database/query, token SUPABASE_ACCESS_TOKEN
  ao vivo do Bitwarden (bws + Keychain), User-Agent custom (CF 1010).

## Pendências com dono
- Pedro: OK por etapa pra implementação (motor gated); decidir quando conecta
  Hub Mídia OOH ↔ CRM via Core (fase 2 do OOH).
- Sem nada quebrado, sem deploy pendente, working tree tinha só sujeira
  pré-existente de outras frentes (.env, package.json, android/, clientes/ etc.
  — NÃO são desta sessão, não commitei).
