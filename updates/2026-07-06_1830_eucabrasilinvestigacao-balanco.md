# Balanço — eucabrasilinvestigacao (portal de apuração de desvio na Euca Brasil)

> App NOVO e standalone (não ligado ao Core da frota). Pasta `~/Dev/eucabrasilinvestigacao`,
> repo privado `pedrocostapc/eucabrasilinvestiga`, deploy Vercel.
> Objetivo: investigar desvio de dinheiro na **Euca Brasil Madeiras** cruzando o que o
> sistema (Sankhya) diz com o que o banco mostrou. 3ª tentativa do Pedro (as 2 anteriores
> morreram por over-engineering do Code/Cloud) — desta vez o rumo é: simples, honesto, prova antes de acusar.

## PASSADO (o que subiu e foi provado)

- **No ar:** https://eucabrasilinvestigacao.vercel.app (Vite+React+TS, deploy via `vercel build && vercel deploy --prebuilt --prod` — o build normal da Vercel travava na fila UNKNOWN, prebuilt contorna).
- **Supabase criado e povoado:** projeto `eucabrasilinvestigacao`, ref **`dwslonurzantbtqpwziw`**, org **Risen Midia**, São Paulo, plano **Micro** (pago, autorizado pelo Pedro — ele não tinha free sobrando). 9 tabelas (titulos, notas, parceiros, 3 extratos, 2 dicionários, meta) com campos-chave + `extra jsonb` (guarda TODAS as colunas) e RLS de leitura pública. Import: `npm run data` → `node scripts/supabase-import.mjs`.
- **Credenciais:** em `dados/.supabase.env` (fora do git) **e** no Bitwarden — projeto criado id `c2567787-c921-4c77-8583-b47f012c68bf`, 6 secrets (`SUPABASE_URL/ANON_KEY/SERVICE_ROLE_KEY/DB_PASS/PROJECT_REF/ORG`). Valores nunca no chat.
- **Telas prováveis no ar:** Início (conferência de saldos), Conciliação (cobertura 68% + lista de docs a solicitar), Cadastros→Parceiros (1.285) e Notas Fiscais (3.467), Movimentação Financeira (3.013 títulos), 3 extratos. Todas com seletor de colunas (principais/extras-preenchidas/extras-vazias) e dicionário embutido.
- **Entregável extra:** PDF "Solicitação de Documentos" (gerador `scripts/gen-solicitacao.mjs` via Chrome headless) pro Pedro mandar pros donos.

## O QUE MELHOROU

- **Peso:** bundle passou de **24 MB → 450 KB** ao migrar os dados pro Supabase (antes tudo era JSON embutido no JS; agora cada tela busca sua tabela sob demanda via `src/lib/supabase.ts`, anon key pública + RLS).
- **Preservação de dado:** de "mapeei 23 colunas" pra "guardo TODAS num `extra` + seletor de grupos" (o Pedro cobrou: "não descarte coluna"). Vale pra parceiros/notas/títulos.
- **Banner "Atualizar agora"** automático a cada deploy (mesma ideia do popup-nova-versão da frota, variação por `version.json` carimbado no build).

## O QUE APRENDEU (mudou o rumo)

- **De-para das contas Cresol (provado nos extratos originais):** os rótulos do Sankhya são o **número interno de cooperado**, não a conta corrente. `CRESOL 30847-0` = conta **74.165-5** (Madeiras, matriz 0001-75); `CRESOL 346152` = conta **74.237-6** = **maquininha** (EUCABRASIL VAREJOS, filial 0002-56); `API SICOOB 1` = **920.864-0**. Prova: a linha "INTEGRALIZAÇÃO CAPITALIZAÇÃO" traz `2035-30847-100001` / `2035-346152-00001`. ⇒ NÃO falta extrato Cresol.
- **Movimentação Financeira (TGFFIN, 194 col) ≠ Cabeçalho da Nota (TGFCAB, 395 col).** O Pedro mandou 2x a "completa" achando ser a financeira, mas era a de NOTAS. Só 7 colunas em comum; a de notas NÃO tem Data Baixa/Conta Baixa. Regra p/ conferir o export certo: **tem a coluna "Data Baixa"? então é o Financeiro.** A LIMPA (100 col) veio do original `~/Downloads/Movimentacao_Financeira (1).xls` (194 col) — hoje o portal usa esse original.
- **Método firmado (regra de ouro do Pedro):** importa cru → rotula ruído → sobra dinheiro real → casa por CHAVE (boleto/CNPJ), nunca por valor+data → o que não casa é "falta informação", não acusação.
- **Supabase agora faz sentido** (antes eu tinha steerado contra): a conciliação vai precisar GRAVAR os casamentos que o Pedro confirmar — estático não persiste.

## O QUE ERROU / BUGS

- **Classifiquei "intercooperativo" como transferência interna — ERRADO.** "Intercooperativo" é só o tipo do PIX, não é dinheiro entre contas próprias. Escondeu movimentação real (LENHA REAL, DM FERRAMENTAS, os Fonseca Braga). Corrigido: interno = contraparte é a própria empresa (EUCABRASIL / CNPJ 59.777.125 / "mesma tit."). **Pego pelo Pedro, não por mim.**
- **Etiquetei a conta como "346152" confiando no doc do Pedro** — o número real (74.165-5) só saiu ao ler o PDF original. Lição: o cabeçalho do extrato manda, não o doc.
- **Bug React (guard-placement):** ao migrar pro fetch async, os `if (loading||!r) return` ficaram DEPOIS do `chips` que já lia `r.total` → tela branca "Cannot read properties of null". Corrigido movendo o guard pra logo após os hooks. Recorrente ao converter componentes p/ dados async — o tsc NÃO pega, só quebra rodando. **Sempre rodar a página de verdade (screenshot headless), não confiar no build.**
- **Token do Supabase:** o secret "Management API"/`MANAGEMENT_ACCESS_TOKEN` do Bitwarden NÃO é válido (dá "Invalid access token format"). O que funciona é o secret **`SUPABASE_ACCESS_TOKEN`** (o Pedro insistiu que existia — e existia).
- **Auto-mode classifier** bloqueia varrer o cofre inteiro procurando token (com razão). Buscar UM secret por nome exato, sem loop e sem imprimir valor, passa.

## PRESENTE (estado de cada frente)

- **Infra (Supabase + site leve):** ✅ PRONTO e no ar.
- **As 6 fontes carregadas e organizadas** (títulos, notas, parceiros, 3 extratos) com todas as colunas + dicionários: ✅ PRONTO.
- **Conciliação (casar título×extrato):** ⏳ NÃO começou de verdade (só sonda). Cobertura possível medida: ~48–55% por conta via valor+data; PIX por nome ~306.
- **Bloqueadores da conciliação com PROVA:**
  - falta o **arquivo de retorno CNAB** (.RET) da cobrança Cresol/Sicoob → sem ele, boleto (1.418 títulos = 42% do valor) não casa com chave.
  - faltam extratos **Stone** (87 baixas, R$1,07mi) e **Sicredi** (4 baixas) — já na lista de docs do PDF.
  - 727 títulos baixados sem "conta de baixa" informada no sistema (esclarecer no Sankhya).

## FUTURO (pra onde vamos)

- **Próximo passo concreto:** motor de conciliação — casar título×extrato por CONTA (de-para pronto) + IDENTIDADE (CNPJ no Sicoob, nome no Cresol; boleto só com CNAB), 1-a-1, **gravando cada casamento no Supabase** (o Pedro confirma/corrige na tela). Boletos ficam "provisório até o CNAB".
- **Depende do Pedro:** conseguir o **CNAB de retorno** (destrava a maior fatia) + extratos Stone/Sicredi.
- **Decisões em aberto:** (a) trancar o acesso com senha/RLS por usuário antes de mandar pros donos (hoje a URL é aberta, anon lê tudo)? (b) trazer o relatório de **Notas Canceladas** (red flag: nota cancelada com título baixado)?
- **Rumo geral:** manter simples e provado. A base está redonda; agora é cruzar e achar o buraco (o dinheiro que o sistema diz que entrou mas no banco não caiu).
