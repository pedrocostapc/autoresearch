# Aba "AP" (A Processar) em todos os destinos — front supersec

**Quando:** 2026-06-29
**Repo:** ~/Dev/risen/supersec (branch `feat/aba-ap-aprocessar`, NÃO mergeada — gate do Pedro)
**Deploy:** preview Vercel da branch; produção só quando o Pedro publicar.

## O quê
O Pedro pediu uma aba **AP** ("A Processar") em cada página de destino pra ele
VER os arquivos que a esteira reconheceu mas ainda não têm extrator (ficam em
`status='a_processar'`). São as NFs que a frota LEU e o roteador classificou,
mas a pasta-extratora (Agente 5) ainda não existe → empilham em a_processar.

Fonte da lista: `documents` onde `status='a_processar'` E
`raw_data->tags->>pasta` = label da página (+ filtro `company_unit_id` da unidade ativa).

## Como (peças novas)
- **`src/components/AProcessarTab.tsx`** — componente reutilizável. Lista
  filename/tipo/data + link `/doc/$id` e "abrir ↗" no Drive. Aceita
  `pastaLabel: string | string[]` (`.eq` p/ uma pasta, `.in` p/ várias).
- **`src/components/NotasComAP.tsx`** — envelopa NotasMesa numa Tabs
  [Processadas | AP]. Usado em notas-entrada e notas-venda.
- **`src/components/ComAbaAP.tsx`** — wrapper genérico [conteúdo | AP] pros
  destinos custom, sem tocar no miolo de cada página.
- **`PaginaScaffold.tsx`** — AP vira 1ª aba nas 6 páginas de destino padrão
  (extrato, emprestimos, societario, fiscalizacao, bancos, obrigacoes-acessorias).

## Cobertura (todos os destinos)
- notas-entrada → "Notas Fiscais Entrada"
- notas-venda → "Notas Fiscais Venda"
- fiscal → "Impostos"
- financeiro → ["Contas a Pagar","Contas a Receber"]
- comprovantes → "Comprovantes"
- funcionarios → "Funcionários"
- relatorios → "Relatórios / Contador"
- + as 6 páginas do PaginaScaffold.

## Estado
- Typecheck limpo (`tsc --noEmit` sem erro nos arquivos tocados).
- Commits na branch: núcleo (AProcessarTab/NotasComAP/scaffold/notas) + `aa3922a`
  (os 5 destinos custom).
- **Pendência de conferência:** o layout `h-full` de algumas páginas custom sob o
  Tabs precisa de olhada visual no preview (risco de scroll duplo / corte). Baixo
  risco, ajuste de CSS se aparecer.

## Contexto do porquê tem NF empilhada
Teste ao vivo no corpus PC: 1 leitura Sonnet ensina o tipo → cérebro aprende →
próximos reconhecidos de graça (0¢). Mas ~126 NFs ficam em `a_processar` porque
`document_items=0` — a pasta-extratora da NF (Agente 5 / nf_engine.py) ainda não
está ligada no worker. A aba AP torna esse acúmulo VISÍVEL. Próximo passo real:
ligar o extrator da pasta NF pra desempilhar.
