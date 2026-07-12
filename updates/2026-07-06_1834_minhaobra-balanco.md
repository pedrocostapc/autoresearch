# minhaobra — BALANÇO (passado, presente, futuro)

App: **minhaobra** (gestão de obra do Pedro / PC Construtora). Supabase ref `uytnnaazexttxzjquxxd`.
Repo clonado nesta máquina: `~/minhaobra/pedro-obras`. Front publica via **Lovable** a partir de
`origin/main` (push em main = vai pro ar). DB/edge: aplico direto via Management API (token
`SUPABASE_ACCESS_TOKEN` ao vivo do Bitwarden). E-mail via Resend, **remetente `@risenos.com.br`**.
Continuação do update `2026-07-01_2044_minhaobra-vistoria-recibos-email.md`.

## PASSADO (últimos dias, no ar e provado)
- **Termo de Vistoria** (link de uso único por token, sem login; observações+fotos na hora; assina
  por OTP; PDF gerado e enviado ao cliente). Simulado 14/14. (detalhe no update de 07-01)
- **Fix e-mail Resend** — nada de transacional saía. Causa dupla: `RESEND_API_KEY` ausente (Pedro
  re-subiu) + remetente errado. Domínio verificado no Resend é **`risenos.com.br`**; corrigido o
  `from:` em vistoria + **enviar-otp-manual + request-password-reset** (OTP do Manual e reset de
  senha estavam quebrados havia tempo).
- **Recibos**: (a) excluir recibo ESTORNADO não funcionava (FK `recibo_estornos`→`recibo_etapas`
  NO ACTION) → corrigido na RPC `deletar_recibo_completo` (apaga estornos antes das etapas);
  (b) alinhamento dos ícones de ação (placeholder invisível no estornado); (c) **Editar Recibo
  virou página cheia** `/recibos/:id/editar` (mesmo layout do Novo), com "Estornar linha" por linha.
- **Obras / CUSTO — Fase 1 no ar** (o grande deste bloco): criada a **`vw_custo_obra`** (+
  `vw_custo_obra_consolidado`), fonte ÚNICA de custo realizado por obra, e reconectei os hooks que
  liam a `custos_obras` quebrada (`useExecutiveData`, `ComparativoObras`, `useObraCustos`). O custo
  real voltou a aparecer no Portfolio/Comparativo/drill-down (antes tudo R$0).

## O QUE APRENDEU
- **"Não aparece custo" NÃO era falta de dado — era fonte errada/quebrada.** Os dados existem;
  as telas liam a tabela legada `custos_obras`, cujo **trigger de materiais/despesas morreu em
  out/2025** (dropado por CASCADE numa migration, nunca recriado). Prova: `custos_obras` PRODUTO/
  SERVICO congelados em 10/10/2025; só RECIBO (mão de obra) segue entrando.
- **Havia 3 fontes de custo divergentes** (custos_obras quebrada; `vw_exec_obra` v1 quase vazia,
  só PRINCIPAL; `vw_exec_obra_v3` inflada ~2x por dupla contagem e sem filtro PAGO/estorno).
- **Regras de custo do Pedro (decisões, ver wiki):** mão de obra = só recibos **PAGO**
  (`recibo_etapas.valor_linha`, estornado=false); material = `itens_venda` **ENTREGUE** com
  `custo_origem` **OBRA+CLIENTE** (CLIENTE entra no custo E vira "a receber do cliente"; porcelanato
  que entrou na casa do cliente encarece a obra e ele te deve); **EMPREITEIRO sai do custo** →
  relatório à parte "a receber do empreiteiro"; despesas = `itens_lancamento_custo` PAGA;
  terreno = `vw_custo_terreno`. Hierarquia **PRINCIPAL→BLOCO→UNIDADE** (rollup por `obra_pai_id`).
- **"Bombeiro" = hidráulica** (achado de uma conferência anterior: mão de obra hidráulica nos
  recibos aparece como "BOMBEIRO EMPREITA", não "hidráulica").
- **Manual de garantia (PDFs do portal)** sobe em **Documentação → Memoriais Descritivos** (card
  `ManuaisTenantCard` → tabela `manuais_tenant` + bucket `manuais`), é da empresa (vale p/ todas as
  unidades); o toggle na aba Manual do Cliente da obra só liga/desliga o que o cliente vê.
- **Investigação barata que valeu:** 5 agentes Sonnet em paralelo (paga na Max) mapearam página/
  mão de obra/materiais/agregação/modelo — fechou o diagnóstico sem auditar o repo inteiro.

## O QUE ERROU / BUGS
- **Estimativa de custo real, sem testar em runtime:** a RPC de recibos e as telas de custo exigem
  usuário autenticado / são financeiras; não dá pra testar o fluxo pela API (só `bun run build` +
  agregados read-only). Editar-recibo e a UI de custo dependem do Pedro validar na tela.
- **Editar Recibo — limitações conhecidas:** `recibo_etapas` tem unique `(recibo_id, obra_etapa_id)`
  → não dá pra re-adicionar a MESMA etapa no mesmo recibo após estorno; e o casamento linha↔vínculo
  é **por valor** (itens_recibo não guarda obra_etapa_id) — frágil se 2 linhas do mesmo valor.
- **Secret rotacionado:** o `SUPABASE_ACCESS_TOKEN` mudou de ID no Bitwarden (o antigo deu 404).
  Reforça a regra: buscar SEMPRE ao vivo por nome, nunca cachear ID.
- **Código morto encontrado:** os 4 dialogs em `components/obras/custos/` (ConsumoProdutoDialog etc.)
  não são renderizados em lugar nenhum — restos de uma versão antiga do fluxo de custos. A aposentar.
- **RESOLVIDOS:** delete de estornado, e-mail transacional, custo zerado no portfolio. **AINDA
  ESPREITA:** `CustosObra.tsx` (a página "Ver Custos Detalhados") ainda lê a `custos_obras` legada
  (lista de linhas) — não migrada; e a `vw_exec_obra_v3`/patrimônio segue inflada (não é a fonte nova).

## PRESENTE (estado real)
- **Vistoria:** pronto, no ar, provado.
- **E-mail Resend:** pronto (remetente risenos.com.br em todas as fns).
- **Recibos (excluir/layout/editar página):** no ar; **falta o Pedro validar a edição na tela**.
- **Obras/Custo Fase 1:** no ar (view + 3 hooks). Portfolio/Comparativo/drill-down mostram custo real.
- **Obras/Custo Fase 2 (UI nova):** PELA METADE / a fazer — aba "Custo" no drill-down (breakdown,
  timeline mensal, lista de lançamentos, a-receber cliente/empreiteiro, previsto×realizado da mão de
  obra), cards do portfolio com categoria/custo-m²/margem-semáforo, e reescrever `CustosObra.tsx`.
- **Obras/Custo Fase 3 (orçamento por obra):** a fazer — tabela `obra_orcamento` + planejado×realizado.

## FUTURO (pra onde vamos)
- **Próximo passo concreto:** executar **Fase 2** (UI de custo) — autorização do Pedro já dada
  ("executa fase 1, 2 e 3, pode ir direto, não precisa mostrar SQL"). Depois **Fase 3** (orçamento).
- **Rumo:** transformar a página Obras de "não mostra nada" em "quanto cada obra custou de verdade,
  por categoria, com margem e a-receber", e depois planejado×realizado.
- **Decisão em aberto pro Pedro:** a **estimativa de obra** (planejado top-down) será feita à parte,
  no jeito tradicional **m² × SINAPI por região** — é feature futura, separada da execução. O
  orçamento da Fase 3 é o "orçamento que se cria numa obra", não a estimativa SINAPI.
- Menor: mover o upload de "Manuais e Garantias" pra um lugar mais óbvio (hoje em Memoriais
  Descritivos); aposentar os 4 dialogs de custo órfãos; endereçar limitações do Editar Recibo.
