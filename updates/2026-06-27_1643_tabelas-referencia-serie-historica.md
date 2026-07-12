# Handoff — Tabelas de referência + série histórica + limpeza de fantasmas (2026-06-27)

Continuação direta do handoff `2026-06-26_1909_reconstrucao-motor.md`. Escrito pra quem
não viu a conversa. Repos: `super-secretaria-functions` (backend) + `supersec` (front),
mesmo Supabase `abysijyuhvwrczxnwaqg`.

## Contexto de uma linha
O sistema está em reconstrução. Esta sessão fechou o **cérebro de tabelas de referência**
(a verdade que a conferência consulta) e começou a **série histórica versionada**. O próximo
grande passo é o **agente curador da pasta NF + script**, com a conferência ligada nessas tabelas.

## OS PASSOS INTEIROS que o sistema percorre ao chegar um arquivo
(Verificado na fonte nesta sessão: `services/ocr-fleet/worker.py` + `supabase/functions/worker-agent-1/index.ts`.)

0. **Ingestão.** O doc cai em `SuperSec/Novos Documentos` (Drive) — por scan do Drive (cron
   `drive-scan` varre a pasta), email, upload ou WhatsApp. Cria linha em `documents` e enfileira
   em `processing_queue` + um job em `extraction_jobs`.
1. **Frota lê DE GRAÇA (OCR/visão).** `worker.py` reivindica o job (`claim_extraction_job`), baixa
   os bytes (edge `doc-bytes`, pra não espalhar segredo), roda um **PAINEL de engines** (Apple Vision
   no Mac, easyocr, tesseract, pdf-engine, pdfplumber/pdftotext-layout, camelot, docling…), faz
   **CONSENSO** entre eles, extrai **barcode** e valores, e grava texto + linhas/bbox em
   `document_extractions`. Custo ~0 (OCR local na frota). Daí saem as **tags** do documento.
2. **Agente 1 classifica POR TAGS (roteador puro).** `worker-agent-1` consome `processing_queue`.
   `classifyByTags` carrega o **brain** (`document_tags` ativas, 1x por invocação) e compara as tags
   do doc com as do catálogo (com peso/folga). **scoreDoc foi REMOVIDO.** Casou com folga → vira o
   `type` da pasta mapeada (`PASTA_TO_TYPE`: "Notas Fiscais Entrada/Venda"→`nfe`, "Extrato"→`extrato`).
   Folga fraca / sem match → `desconhecido`.
3. **A PASTA extrai 100% (raw verbatim).** `run_phase2` lê `extraction_scripts.handler`, importa
   `importers/<handler>.py` do BUCKET e chama `run(ctx)`. Worker é BURRO — a receita mora no bucket
   (editável no /admin, sem deploy). Hoje **só `nfe` (NF entrada) tem extrator real** (determinístico
   por consenso, ~99,9%); o resto é slot vazio. LLM só **tapa-buraco** até os 98% (dormente).
4. **Enquadrador LLM (Etapa 3b) — só pro desconhecido.** Se `desconhecido`, `enquadrarLlm(text,
   CATALOG_DOCS)` → Haiku afirma tipo+tags do catálogo → grava em `document_tags` (ativo=true → o
   **próximo igual cai DE GRAÇA**, sem LLM) + custo em `agent_runs(agent=enquadrador)`. **DORMENTE**
   (gated pelo cofre).
5. **Materialização + filing.** `processOne` resolve a entidade (**CNPJ é a fonte da verdade**),
   grava `raw_data` (verbatim), materializa o canônico do tipo, garante **idempotência** (re-processar
   não duplica) e **arquiva no Drive** na planta `{Entidade}/{Página}/{Aba}`. Sem confiança →
   `needs_review` (= mapa de bugs: conserta a CAUSA e reprocessa, não materializa lixo).
6. **(Próximo — Task 4) Conferência contra as tabelas.** Validar chave-44 (DV módulo 11), CFOP/CST/NCM,
   e alíquotas **pela vigência da data do doc**. É o que o agente curador da pasta vai fazer.

## A PASTA DO DRIVE que eu (Claude) tenho acesso
Acesso o **`/Users/pedrocosta/My Drive`** direto pelo filesystem (Bash/Read) — e há também o MCP
Google Drive (`search_files`/`read_file_content`…). Três coisas dentro:
- **`SuperSec/`** = o **Drive VIVO do sistema = a planta**. Tem `Novos Documentos` (a caixa de entrada
  do passo 0), `Aguardando Revisão`, e as pastas por entidade no padrão `{Entidade}/{Página}/{Aba}`
  (ex.: `PC CONSTRUTORA - 0001-34`, `RISEN MIDIA - 0001-14`). É onde dá pra **testar o pipeline sem
  produção**: copiar um doc pra `Novos Documentos`, forçar o `drive-scan`, deixar o sistema rodar
  (cofre off = 0¢). NÃO interferir no run — corrigir função, não forçar resultado.
- **`Arquivos de Referencia/`** = o **seed candidato** — **25.084 arquivos curados**, organizados por
  entidade (`PC Construtora - Financeiro`, `Risen Midia - Financeiro`…). É o corpus pra (a) **encher o
  cérebro** (`document_tags`) e (b) **VERIFICAR a extração contra docs REAIS** — o gabarito de cada
  tipo vale mais que o que o agente afirma.
- **`Icon`** = lixo do Drive, ignorar.

## O QUE MAIS uma sessão nova precisa saber (pra não herdar nada velho)
- **POSTURA (a regra que mais foi violada):** handoff, CLAUDE.md, regras e os 57 agentes são
  **REFERÊNCIA pra VERIFICAR**, não lei. A verdade mora no **sistema ao vivo** (banco, código
  deployado, /admin) e nos **documentos reais**. Se o agente diz X e a NF real diz Y, vale a NF.
- **As 3 fontes da verdade da conferência:** (1) **algoritmo** — código, nunca muda (DV da chave-44 por
  módulo 11, soma dos itens = total, DV do CNPJ); (2) **tabelas de referência** — lei muda, por isso
  versionadas por **vigência** (o que esta sessão construiu); (3) **API ao vivo** — SEFAZ via cert A1
  (`services/sefaz-dfe`, a frota faz o mTLS — Edge não), BrasilAPI pra CNPJ/NCM.
- **Onde mora cada coisa:** agentes em `autoresearch/lab/agents/contabilidade/` (57); importers no
  **bucket** (`importers/<handler>.py`, editável no /admin); o "professor" da extração é **offline/manual**
  em `scripts/nf-bench/` (loop gabarito-XML × extração, levou a NF a ~99,9%; NÃO é agente ainda);
  frota em `services/ocr-fleet/`.
- **Cofre LLM OFF** — por isso o pipeline LLM (enquadrador/tapa-buraco) está dormente: precisa da chave
  Anthropic no cofre + `LLM_TEXT_ENABLED`. É **decisão de custo do Pedro**, e o worker Edge **fatura API
  paga por token** (NÃO é cota Max). Não ligar por conta própria.
- **Convenções fixas (não re-perguntar):** CNPJ é a fonte da verdade (nome muda, CNPJ não); a Risen apura
  por **regime de CAIXA**; nome de arquivo `N - AAAA-MM-DD - ... - R$VALOR`, CAPS sem acento.
- **Regras de trabalho:** push `main` após modificar (sem perguntar); `git add` por caminho explícito
  (**nunca `-A`** — já vazou `.env.bak`); `git status` antes de mexer (Pedro roda várias sessões em
  paralelo); nada de `reset --hard`/`clean`. Banco ao vivo: DDL via management API
  (`POST /v1/projects/abysijyuhvwrczxnwaqg/database/query`), DML via REST (pooler aws-1-sa-east-1).
- **Comunicação:** PT-BR; ferramenta nomeada pela FUNÇÃO (não "Haiku/Sonnet"); não pedir pro Pedro
  compor comando de shell; não deixar escopo pela metade.

## O que ficou pronto nesta sessão (tudo commitado + push main)

### 1. Tabelas de referência — consolidação, re-checador, aba no /admin
- **Consolidação:** 152 → **138 tabelas** (14 duplicatas fundidas). Script `scripts/consolidar_tabelas.py`.
  INSS/IRRF mantiveram o seed oficial conferido (não absorveram as variantes web suspeitas).
- **Re-checador** (o "rodo a cotação todo dia"): RPC `admin_referencias_due(p_force)` lista o que
  está vencido por cadência (`diaria`=1d / `anual`=365d / `estavel`=3a); script `scripts/reconferir.py`
  re-dumpa as voláteis pro workflow de conferência e avisa pra re-rodar `popular_ncm.py` nas `api`.
  Migration `supabase/migrations/20260626195000_referencias_due.sql`.
- **Aba "Tabelas" no /admin:** `supersec/src/components/admin/Tabelas.tsx` — lista as 138 por domínio,
  expande pra ver itens + **veredito** (confirmado/corrigido/heurística/a-conferir) + **fonte_url**
  conferida. Ligada em `routes/_authenticated/admin.tsx`.
- Estado: ~16k itens (inclui 15042 NCM da BrasilAPI), 211 confirmados / 122 corrigidos na web.

### 2. Série histórica INSS/IRRF/salário mínimo 2020→2026 (com vigência)
- Resolveu o "conflito 1518 vs 1621": **NÃO era conflito, eram anos** (2025=1518, 2026=1621).
  Cada tabela entra com sua **vigência**; a conferência escolhe pela **DATA do documento**.
- Fetch via workflow `serie-historica-inss-irrf` (1 Sonnet/ano, fonte oficial). Populado por
  `scripts/popular_inss_irrf_historico.py` (lê `/tmp/serie_historica.json`).
- **Princípio aplicado:** a parcela a deduzir (INSS e IRRF) é **DETERMINÍSTICA** (continuidade
  tetos+alíquotas) → é **recomputada**, não confiada no fetch. Isso auto-corrigiu o erro do
  Sonnet no INSS 2025 faixa-3 (trouxe 106,02; o certo é **106,59**).
- Gravado: salário mínimo (7 anos), INSS (28 itens / 7 vigências), IRRF (27 itens / 4 tabelas
  distintas: vig 2015-04, 2023-05, 2024-02, 2025-05). Grupos `inss-faixas`/`irrf-faixas`/`salario-minimo`.
- **Por que histórico:** cobre a janela de decadência (5 anos). Doc de 2022 usa tabela de 2022.
  Estender pra trás (acervo vai a 2010) é sob-demanda.

### 3. Limpeza dos "agentes fantasma" no /admin
- A aba Agentes mostrava agentes 2/3/4 + Resolvedor como se ativos. **Verdade ao vivo:** só 4 crons
  (`agent1-drain` = único agente; `drive-scan`/`orphan-reset`/`usage-refresh` = encanamento).
  Os 2/3/4/resolvedor NÃO têm cron nem função.
- Removido: labels mortos em `AGENTE_INFO`/`RUN_KEY`/`SETTINGS_PREFIX`, a seção `<Resolvedor/>`
  (botão chamava `worker-resolvedor` deletada → 404), o componente `Resolvedor.tsx`, menção em
  `ProvedoresIA`. A tela passou a bater com o backend.

## Commits desta sessão
- front `supersec`: `5a4d867` (aba Tabelas) · `e23d962` (limpeza fantasmas)
- backend `super-secretaria-functions`: `5a59ffa` (consolidação) · `397d878` (re-checador) ·
  `c2f47d6` (série histórica INSS/IRRF/salário mínimo)

## PRÓXIMOS PASSOS (em ordem)

### ▶️ Task 4 — agente curador da pasta NF + script (estava adiado pra "casa em ordem"; AGORA é a vez)
- Curador da pasta Notas Fiscais = agente **`24-cadastro-nf`** (em `autoresearch/lab/agents/contabilidade/`).
- Script da pasta extrai 100% + **valida contra as tabelas de referência**: chave-44 DV (módulo 11,
  determinístico), CFOP/CST/NCM (tabela), alíquotas por **vigência** (a série que acabou de entrar).
- É o **piloto do "professor/treinador-aferidor"** — o agente in-system que leva cada pasta aos 98%
  com o gabarito de cada tipo (XML→NF). Hoje esse loop é OFFLINE/manual (`scripts/nf-bench/`).
- ⚠️ Antes de construir: consultar o agente 24 + catálogo + tabelas reais (REGRA Nº1), e **verificar
  contra NF real** (o gabarito vale mais que o agente).

### Lacunas de dados a fechar (alimentam o Task 4 / a conferência)
1. **CFOP completo** (~600, fonte CONFAZ) e **DARF completo** (RFB) — hoje só os comuns; faltam em lote.
2. Outras voláteis por ano (ICMS por UF, DAS anexos) — sob-demanda, mesmo método (Sonnet→fonte oficial).
3. Spot-check humano dos vereditos `corrigido-web` que ainda divergem (a aba Tabelas mostra fonte).

### Depois do Task 4
- Encher o cérebro (`document_tags`): tageador (volume) + enquadrador (exceção). Seed candidato
  `~/My Drive/Arquivos de Referencia` (~25k docs curados). Depende do **cofre LLM** (chave Anthropic
  + `LLM_TEXT_ENABLED`) — decisão de custo do Pedro, hoje OFF.
- Pasta por pasta aos 98%: boleto → extrato → nfse → holerite.
- Downstream (financeiro/conciliação) só DENTRO da página `/conciliacao`, quando a info estiver
  encaixada nas páginas.

## Gotchas úteis
- A parcela a deduzir é calculável — sempre recomputar, nunca confiar no valor buscado (achei 1 erro).
- "Tarefas em segundo plano" do painel acumula entradas-zumbi (esta sessão ficou 4 dias aberta);
  são display velho, nada roda de fato (ps confirma). Clear/restart limpa.
- DDL via management API `POST /v1/projects/abysijyuhvwrczxnwaqg/database/query`; DML via REST
  (PostgREST capa fetch ~1000 linhas — usar `limit` alto pra contagem).
