# Reconstrução do motor — scoreDoc fora, workers burros, Drive=planta, enquadrador (2026-06-26)

> Pras sessões paralelas. Sessão longa de reconstrução com o Pedro. Postura travada:
> **handoff/regras/57-agentes = referência pra VERIFICAR, não lei.** A verdade é o sistema
> ao vivo (banco, código deployado) + os documentos reais (gabarito). Muita regra velha caiu.

## O que foi PRA PRODUÇÃO nesta sessão
1. **scoreDoc DELETADO** → o classificador é o **roteador de tags** (`worker-agent-1` lê
   `document_tags`; sem match → enquadrador/Revisar). `_shared/classify_doc.ts` removido.
2. **Workers BURROS** — `services/ocr-fleet/worker.py` é loader genérico: importa
   `importers/<handler>.py` do bucket e chama `run(ctx)`. Receita mora no bucket, não na máquina.
   (A receita da NF saiu de dentro do worker → `importers/nfe.py::run`.)
3. **Agentes 2/3/4 + resolvedor DELETADOS** (cron desagendado + undeploy + código). Vivos:
   agent-1, enquadrador, tageador, tags-peso. A camada de cálculo será reconstruída na ordem
   certa (conciliação dentro da página `/conciliacao`) só depois da info encaixada nas páginas.
4. **Banco ZERADO de documentos** — apagados os tenants/docs do esquema antigo (PC CONSTRUTORA
   4900 + 107, diag, joao@batatas, RISEN MIDIA, risenmidia+t3). Sobrou `grupopcpirapora`. O
   **corpus de 4900 NÃO existe mais** (era referenciado como seed em memórias antigas).
5. **Drive = PLANTA.** Estrutura de pastas deriva de `document_catalog` + tabela nova `paginas`
   → `{Entidade}/{Página}/{Aba}`; básicas de cara, abas/não-básicas sob-demanda. `create-drive-folders`
   e `drive_organize` leem a planta (acabaram as 3 listas hardcoded divergentes). Testado num
   tenant real (criou só as 6 básicas).
6. **Enquadrador LLM (Etapa 3b)** construído, **DORMENTE** (gated pelo cofre): sem match a LLM
   (Haiku) afirma tipo+tags do catálogo → grava em `document_tags` ativo=true (próximo de graça)
   + custo próprio em `agent_runs`. `_shared/llm_docs.ts::enquadrarLlm`.
7. **Medidor de custo POR AGENTE** — RPC `admin_custo_por_agente` + seção no /admin Custo & margem.
8. **Link Admin na sidebar** (front) só pra super admin. pedro@pcconstrutora.com.br = super admin.

## O ponto cego (o próximo grande passo)
O **"professor" da extração** — o loop que levou a NF a ~99,9% (parear DANFE-PDF + XML → XML é
gabarito → extrair → comparar campo a campo → corrigir o parser → repetir) — é **OFFLINE/manual**
(`scripts/nf-bench/`, nem versionado, rodado pelo Claude). **Não é um agente do sistema.** Só a NF
foi treinada; as outras pastas (boleto/extrato/holerite/…) são slot vazio. Produtizar esse professor
num **agente treinador/aferidor in-system** (que usa o gabarito de cada tipo) é o que ensina TODOS
os documentos aos 98%.

## Como seguir
- Construir o treinador/aferidor (o professor) dentro do sistema.
- Encher o cérebro (`document_tags`): tageador (volume) + enquadrador (exceção); seed limpo
  candidato = `~/My Drive/Arquivos de Referencia` (25k docs curados por tipo). Depende do **cofre LLM**
  (chave Anthropic — hoje OFF por custo; API paga por token).
- Pasta por pasta aos 98% (ordem do playbook: boleto→extrato→nfse→holerite).
- Reconstruir downstream (financeiro/conciliação) depois.

## Docs atualizadas
`super-secretaria-functions/CLAUDE.md` (estado da arquitetura + caveat na REGRA Nº1) e
`docs/conceito-supersec-referencia.md` (seção "Estado honesto" reescrita). Commits do dia:
remoção scoreDoc/workers `2ab1a4d`, Drive `c92a319`/merge `21e68b3`, deleções agentes
`76194c5`/`64d0f5b`, enquadrador `44791cb` (back) / `6d4bae6` (front).
