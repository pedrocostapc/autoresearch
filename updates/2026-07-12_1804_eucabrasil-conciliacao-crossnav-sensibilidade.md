# Euca Brasil — conciliação, navegação cruzada e a decisão pendente do match (complemento do checkpoint)

**Escrito 12/07/2026 18:04 (checkpoint de limite semanal).** Complementa o
`2026-07-12_checkpoint_eucabrasil-dashboard-estado.md` (leia AQUELE primeiro pro estado geral,
retomada, pegadinhas de dados). Este foca no que a última leva de trabalho (commit `d2fb660`,
08/07) entregou **além do dashboard**, e na **única coisa em aberto na conversa**: até onde afrouxar
o casamento título↔extrato.

## O que está NO AR (tudo em `d2fb660`/`2169dc2`, working tree limpo, pushado, deployado)

Além do dashboard (Início), estas telas estão no ar e funcionando:

1. **Contas a Receber** e **Contas a Pagar** (menu Lado do Sistema) — componente único `ContasFluxo({natureza})`
   em `src/App.tsx`. Uma linha por nota, **meses dinâmicos** (YYYY-MM, lidos de `meta.fluxo_receber.meses`
   / `fluxo_pagar.meses`; pagar vai dez/25→dez/26, receber dez/25→out/26). Critério **BINÁRIO** (regra do
   Pedro): "o dinheiro está no banco ou não?" — ✓ verde na cor da conta (Sicoob verde escuro / Cresol c/c
   laranja / maq roxo) se achei no extrato; vermelho se não. **Embaixo de cada parcela: quem deu a baixa**
   (`usuario_baixa`). Build: `fluxoCaixa(titulos, ccL, maqL, sicL)` em `build-data.mjs` (processa Receita E
   Despesa; célula guarda `{v, ok, acct, u, ids}`).
2. **Conciliação nas linhas do extrato** — `conciliarExtratos()` marca cada linha REAL do extrato como
   `conciliado` (casou com um título baixado por valor+data) + `titulo_parceiro`/`titulo_nota`. Coluna
   "Conciliação" (só mostra ✓ conciliado; o que não tem é o "a conciliar"). Filtro "🔎 Só a conciliar" na
   toolbar dos extratos. cc: 788 conciliadas / 627 a conciliar.
3. **Navegação cruzada** (helper no App): hash `#view|q=termo` (parser `rawHash`/`hashView`/`hashQ`;
   `setView(v,q)`). Clicar na **parcela ✓** (Contas) → pula pro **extrato na LINHA EXATA que casou** (por
   `id`, guardado na conciliação — NÃO por nome, porque a linha do banco não tem o nome escrito). Clicar no
   **✓ conciliado** (extrato) → Contas a Pagar/Receber no fornecedor/cliente. **Nome de parceiro e CPF/CNPJ**
   em qualquer tabela (helper `LinkParc`, sublinhado pontilhado) → cadastro **Parceiros** filtrado.
4. **Contas a Pagar existe** (Despesa): maior é a **sócia ELIANE R$ 282k**; pagamentos grandes (R$235k,
   R$200k) **baixados pela DANIELLE**. Placar pagar: no banco R$3,9mi · fora R$8,58mi.

## A DECISÃO EM ABERTO (onde a conversa parou — última pergunta do Pedro)

Pedro perguntou: *"Só dá pra casar com Pix, já casou tudo que dava pra casar?"*. Rodei a sensibilidade do
match (receita baixada até jul, 1597 títulos, contra os créditos dos 3 extratos):

| Regra do casamento | Casou |
|---|---|
| **ATUAL** (valor exato ±0,02 · ±7 dias) | 369 (23%) |
| janela ±15 dias | 404 (25%) |
| **tolerância 1% no valor (taxa de boleto)** | **592 (37%)** |
| 2% + ±15 dias (bem frouxo) | 1019 (64%) |

Dos 1228 não-casados: **boleto 711 · cartão 229 · dinheiro 169 · PIX 100**.

**O que isso diz (e a resposta pro Pedro):**
- NÃO é "só PIX por regra" — o match aceita qualquer título por valor+data. É que **só o PIX sobrevive**:
  boleto vem líquido de taxa/agrupado, cartão vai pra Stone (sem extrato), dinheiro vai pro caixa.
- **Dá pra espremer MAIS sem documento novo**: afrouxar o valor pra 1% (taxa de boleto) quase DOBRA
  (23%→37%). Mas **aumenta risco de falso-casado** — vai contra a regra de ouro "nunca por coincidência de
  valor+data". **DECISÃO do Pedro pendente**: afrouxar (mais cobertura, menos rigor) ou manter exato e
  esperar o CNAB. Recomendação: manter exato como padrão + talvez um modo "aproximado (1%)" marcado como
  candidato, não como prova.
- **Os 100 PIX que NÃO casaram são o achado mais interessante** — PIX deveria casar exato. Prováveis
  motivos: Sicoob só tem extrato de abr/26 pra frente (perde PIX antes); ou valor/data fora da janela. **Vale
  investigar esses 100 um a um** — PIX baixado no sistema sem crédito no banco é o cheiro de desvio de verdade.

Onde reproduzir: o teste foi um `node -e` inline lendo `src/data/titulos.json` + os 3 extratos; a função de
casamento canônica é `achaBanco()` dentro de `fluxoCaixa()` em `scripts/build-data.mjs` (hoje `±0,02` e `±7`).

## Estado técnico

- Git: `main` = origin (`git rev-list --left-right --count origin/main...main` = `0 0`), working tree limpo.
  Deploy no ar `index-Bg09DGtm.js`. **Nada preso no disco.**
- **NÃO commitar**: `dados/.supabase.env` (segredo, gitignorado). Tudo mais do `dados/` É versionado (repo privado).
- Reimport pós-rebuild: `npm run data` → `node scripts/supabase-import.mjs`. DDL sem PAT: postgres.js no pooler
  `aws-1-sa-east-1.pooler.supabase.com:5432` com `SUPABASE_DB_PASS`.

## Pendências (com dono) — além das já listadas no checkpoint principal
- **Pedro decidir**: afrouxar o match (1% taxa) ou manter exato + esperar CNAB.
- **Próxima sessão**: investigar os **100 PIX baixados sem crédito no banco** (o filtro/dado já existe: título
  Receita PIX baixado que `achaBanco` retorna null). É o alvo mais quente da apuração.
