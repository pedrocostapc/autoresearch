# Handoff — Páginas, Abas e Apontamentos de documentos (2026-06-26)

> Sessão de contexto limpo com o Pedro. Tema: transformar a lista de **tipos de
> documento** na estrutura de **páginas + abas** do app, e **apontar** cada documento
> pra (página, aba) — pra o arquivo ter pra onde ir. Leia também
> `docs/conceito-supersec-referencia.md` (o conceito-mãe dos 5 passos).

## O conceito que guiou tudo (decisões travadas com o Pedro)

1. **Pasta = página do app.** "Comprovantes" é a página `/comprovantes`. O destino de um
   documento é uma PÁGINA (rota do front), não doc_type de tabela nem pasta de Drive.
2. **Aba = tipo de documento** dentro da página. Sub-aba = variação/código (a princípio
   ainda não construída na maioria).
3. **Documento × Conceito.** Só vira página/aba o que é **papel que chega**. Tributo puro
   (ICMS, PIS), conta de razão (Fornecedores), resultado de apuração (PIS a recolher),
   provisão e lançamento contábil **NÃO são documento** → sem página (são o que os agentes
   calculam / o Agente 2 lança no razão).
4. **Notas = 2 eixos:** direção (compra/venda, decidida por **CNPJ**) × objeto (produto/
   serviço, decidido pelo tipo da nota). Viraram 2 páginas: **Notas Fiscais Entrada** e
   **Notas Fiscais Venda**, cada uma com filtro Produto/Serviço.
5. **Guia de imposto é multi-tributo → nunca colapsa a família.** DARF 0561 ≠ DARF PIS
   (código de receita impresso = taggável). Motivo do Pedro: *"tenho que saber quanto
   paguei por tipo de imposto"*. Todas as guias (DARF/DAS/GPS/DAM/GNRE/GIA/DAR) vivem em
   **Impostos**, cada uma uma aba; o tributo/código é coluna dentro da aba.
6. **FGTS é imposto** (Impostos). **INSS = GPS** (Impostos). **Extrato é documento**
   (página `/extrato`); **Conciliação é função** (`/conciliacao`, não recebe documento).
7. **Dedup só literal.** Funde só o MESMO documento escrito diferente (ex.: "Boleto" =
   "Boleto a pagar"; "DARF" = "DARF (Documento de Arrecadação...)"). Código/tributo
   diferente = documento diferente (mantém). NÃO fundir sem o Pedro aprovar item a item.

## O que foi construído

### Front (repo `supersec`, branch `main`, deploy Vercel)
- **`src/lib/paginas-destino.ts`** — FONTE ÚNICA dos apontamentos: array `PAGINAS` com
  `{slug, label, route, abas[]}`, gerado a partir do mapa documento→página→aba. Helpers:
  `PAGINA_LABELS`, `abasDaPagina(label)`.
- **Páginas novas** (scaffold via `src/components/PaginaScaffold.tsx`, abas vazias):
  `/obrigacoes-acessorias`, `/societario`, `/fiscalizacao`, `/extrato`, `/emprestimos`,
  `/bancos`.
- **Notas:** `/notas-entrada` e `/notas-venda` (componente `src/components/notas/NotasMesa.tsx`,
  direção fixa + filtro Produto/Serviço). `/notas` antiga REMOVIDA.
- **Impostos** (`/fiscal`): vira casca de abas por guia (DAS/DARF/GPS/FGTS/DAM/GNRE/GIA/DAR).
  Aba DAS mantém a apuração rica (calc × guia do contador). Outras abas: lista + **raw
  verbatim** via `src/components/fiscal/GuiasRaw.tsx` ("mostra só o raw; UI depois").
- **Menu:** `src/components/AppSidebar.tsx` atualizado (Fiscal, Cadastros, Financeiro).
- **Admin → aba "Tags de Documentos"** (`src/components/admin/TagsDocumentos.tsx`): lista os
  documentos do catálogo (nome · **página** (dropdown do config) · **aba** (dropdown
  dependente) · agentes · tags). Grava `pasta_destino` + `aba_destino`. Tags mostradas =
  **só do tageador**. Aba "Pastas" do admin renomeada → "Páginas".

### Backend (repo/worktree `ss-cockpit-motor`, branch `feat/cockpit-no-motor`)
- **`document_catalog`** (tabela master): `documento` (pk) · `pasta_destino` (página) ·
  `aba_destino` (aba) · `agentes` (jsonb) · `classes` (jsonb). RLS: read+write `authenticated`.
  Migrations: `20260626140000_document_catalog.sql`, `20260628120000_document_catalog_aba.sql`.
- **`document_tags`** (já existia): tags por **documento** (coluna `documento`), com `pasta`
  (=destino), `tag`, `is_regex`, `tipo_arquivo`, `ativo`, `peso`. Populada SÓ pelo tageador.

## Números atuais (catálogo)
- **305** documentos no `document_catalog` (vieram dos ~340 da aba PEDRO TAG; ~34 eram texto
  idêntico repetido; 1 fusão literal aprovada: "Boleto a pagar"→"Boleto").
- **184 com página + aba** · **~111 conceitos** sem página (correto).
- **Tags do tageador:** NF-e 40 · Boleto 33 · Extrato Bancário 29 (todas `ativo=false`).
- **14 páginas** no config: Notas Entrada, Notas Venda, Impostos, Obrigações Acessórias,
  Contas a Pagar, Contas a Receber, Comprovantes, Extrato, Funcionários, Societário,
  Fiscalização, Relatórios/Contador, Empréstimos, Bancos (+ Revisar).

## O tageador (como funciona) — `_shared/tags.ts`
Aprende, de graça (substring, sem LLM), a impressão digital de cada tipo:
- **Camada 2** `buildMatrix`+`vocabulary(0.5)`: tag = palavra presente em ≥50% dos docs do tipo.
- **Camada 3** `crossWeights` (share ponderado): peso = freq_no_tipo ÷ soma das freqs em todos
  os tipos → palavra específica = peso alto; genérica (CNPJ/DATA) = peso baixo. Nunca remove.
- **Uso** (`router.ts`): `classifyByTags` + `decidePorFolga` (piso + folga sobre 2º) → roteia
  ou Revisar. `clusterByTags` = arranque frio (agrupa por Jaccard, LLM rotula 1 por cluster).

## Pendências (próximos passos)
1. **Rodar o tageador** nos tipos sem tags (guias DARF/DAS/GPS, holerite, folha, etc.) — agora
   que cada tipo tem página/aba. Minerar de `documents.raw_data.raw.text` por tipo.
2. **Roteador gravar `pasta_destino`+`aba_destino`** no documento ao classificar (hoje o
   `worker-agent-1` ainda decide por `scoreDoc`; cutover pendente — ver memória
   `plano_reconstrucao`).
3. **Páginas lerem os docs apontados** pra elas (sair do scaffold → mostrar raw, depois UI).
4. **Extrair código de receita** no curador do DARF → habilita sub-aba por tributo em Impostos
   (hoje `tax_guides.raw_canonical` não tem `codigo`).
5. **Tabela de referência "Tributos"** (os 31 nomes de imposto) fora do catálogo de documentos.
6. **Revisar os apontamentos no admin** (o bucketing automático precisa de olho humano; ex.:
   "Documentos pessoais" funcionário×sócio; 5 docs que vazaram pra conceito: Extrato FGTS,
   Espelho de Conciliação, Comprovante de Dívidas/Ônus, Documentos de Importação, Cadastro de
   Restrição).

## Canais / como aplicar (operacional)
- **REST** (service role, lê `.env.local` `SUPABASE_SERVICE_ROLE_KEY`): DML no catálogo/tags.
- **Management API** (`/v1/projects/abysijyuhvwrczxnwaqg/database/query`, token
  `.env.local` `SUPABASE_ACCESS_TOKEN`): DDL. **Dá 403 (Cloudflare 1010) intermitente →
  retentar 2-3× via curl resolve.**
- **Front:** `npm run build` no `supersec` (regenera `routeTree.gen.ts`); commit com paths
  explícitos; **push pra main = deploy de produção Vercel → precisa do gate do Pedro.**
- Guardrails do Pedro: cofre LLM nunca ligado; não rodar worker na mão; `git add` por caminho
  (nunca `-A`); segredo nunca no chat (Bitwarden); não tocar `arrecadacao.ts`/`folha.ts`
  (outra sessão); não fundir/decidir taxonomia sozinho — mostrar e ele aprova.
