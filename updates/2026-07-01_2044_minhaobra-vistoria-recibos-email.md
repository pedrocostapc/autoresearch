# minhaobra — Termo de Vistoria + fix e-mail Resend + recibos (excluir/editar)

App: **minhaobra** (Supabase ref `uytnnaazexttxzjquxxd`). Repo local desta máquina:
`~/minhaobra/pedro-obras` (está clonado aqui, apesar do briefing dizer "só nuvem").
Front publica via **Lovable** a partir de `origin/main`. Tudo abaixo já está em main + aplicado.

## 1. Termo de Vistoria e Entrega do Imóvel (novo, ponta a ponta)
Documento jurídico assinado por OTP, criado pelo gestor. Fluxo final (após iterações com o Pedro):
- Gestor cria a vistoria na aba **Vistoria** da unidade (obra não-PRINCIPAL) e gera um
  **link de uso único por TOKEN** (sem login CPF/senha). Abre no celular → termo direto.
- Preenche observações + fotos na hora; no fim o cliente põe e-mail → OTP → assina →
  **PDF gerado (pdf-lib) e enviado ao e-mail do cliente + salvo** (bucket `vistoria-pdfs`).
- Duas variantes: **VENDA** (Pedro Costa Construções) e **LOCACAO** (PC Serviços, CNPJ 14.822.130/0001-14).
- Qualificação (nacionalidade/RG/estado civil/profissão/endereço) enriquecida no **contato** e congelada em snapshot.
- Tabelas `vistoria_acessos/otp/confirmacoes/fotos` (+ coluna `token` unique), RPCs `vistoria_conteudo/salvar_observacoes/confirmar` (por token), edge fns `enviar-otp-vistoria`, `vistoria-arquivo`, `vistoria-foto-upload`, `gerar-pdf-vistoria`. Simulado ponta a ponta (14/14) com sandbox `delivered@resend.dev`.

## 2. FIX de e-mail (Resend) — afetava vários fluxos
Descoberto na simulação: **nenhum e-mail transacional saía**. Duas causas:
- `RESEND_API_KEY` estava ausente no projeto Supabase (Pedro re-adicionou).
- **Remetente errado:** o domínio verificado no Resend é **`risenos.com.br`**; `notify.pcgestor.com.br` NÃO é verificado → 403.
Corrigido o `from:` para `noreply@risenos.com.br` em: `enviar-otp-vistoria`, `gerar-pdf-vistoria`,
**e também `enviar-otp-manual` e `request-password-reset`** (o OTP do Manual do Cliente e o reset de senha
estavam quebrados havia tempo). Regra pra minhaobra: **enviar sempre de `@risenos.com.br`**.

## 3. Recibos (Emissão de Recibos)
- **Excluir recibo estornado não funcionava** (FK `recibo_estornos.recibo_etapa_id` NO ACTION). Corrigido na
  RPC `deletar_recibo_completo`: apaga `recibo_estornos` das etapas antes das `recibo_etapas`. Recibos ESTORNADO agora excluem.
- **Layout:** ícone de estornar vira placeholder invisível nos estornados (mantém alinhamento das colunas).
- **Editar recibo virou página cheia** `/recibos/:id/editar` (mesmo layout do Novo Recibo) no lugar do modal.
  Linhas vinculadas travadas + botão "Estornar linha" (RPC `estornar_pagamento_etapa`); adicionar itens = fluxo do Novo.
  ⚠️ `recibo_etapas` tem unique `(recibo_id, obra_etapa_id)` → não dá pra re-adicionar a MESMA etapa no mesmo recibo após estorno.
  ⚠️ heurística casa item↔vínculo por valor (itens_recibo não guarda obra_etapa_id) — frágil se 2 linhas do mesmo valor. Falta o Pedro testar na tela (RPCs exigem auth; não dá pra testar via API).

## 4. Secret rotacionado
`SUPABASE_ACCESS_TOKEN` foi **rotacionado** (o ID antigo no cofre deu 404). Reforço da regra nova:
buscar **ao vivo do Bitwarden por nome** (não cachear ID). Aplicação de migração direta via Management API
é barrada pelo classificador sem OK explícito do Pedro (prod gated) — ele autoriza caso a caso.
