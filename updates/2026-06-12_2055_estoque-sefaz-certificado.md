# Estoque por NF-e + puller SEFAZ (liga o certificado A1)

**Repo:** super-secretaria-functions · **commit:** `1641741` (não pushado)

## O que o Pedro pediu
Ligar o certificado digital A1 e, com ele, "extrair XML do passado". Módulo de
produtos/estoque no Risen OS: toda NF de compra gera estoque de entrada
(comprou caixa d'água → vira a página "caixa d'água"); venda dá baixa. Com
autonomia total ("não fica me perguntando se pode executar").

## Consulta aos agentes (REGRA Nº 1)
Não há agente dedicado a produto/estoque. A régua veio de **24-cadastro-nf**
(CFOP/CST/CSOSN/NCM), **06-sped-fiscal** (registro 0200 = produto, Bloco H =
inventário) e **29-calculo-ipi / 02-icms-iss**.

## Construído e aplicado (migration em prod)
- `products` (já existia, órfã) ganhou `natural_key` (EAN válido ou
  `dn:normaliza(desc)|ncm`) + `photo_url`.
- `stock_movements` (novo) = razão de giro, 1 mov/item, sinal pelo CFOP.
- `montar_estoque(tenant)` idempotente/gated, `produto_detalhe`, `v_estoque_saldo`.
- `inventory_records` (já existia) = snapshot anual Bloco H, não o giro.

## Puller SEFAZ (`services/sefaz-dfe/`, Node, RODA NA FROTA)
O Edge não faz TLS mútuo com client cert; o Node sim. Decifra cert+senha do
Supabase (AES-GCM, esquema do `cert_encryption.ts`), loop `distNSU`, gunzip,
parseia `procNFe` → grava documents + document_items (XML = fonte 100%, sem OCR)
→ chama `montar_estoque`. Parser **validado por teste** (2 itens, inbound,
ICMS/CSOSN/EAN). Cert do Pedro já carregado: Risen Mídia 14822130000114, val.
2026-12-10, tenant c55fd91e.

## A descoberta que conecta tudo
`document_items` está **VAZIO** — os docs do acervo são NFS-e (serviço) e PDF
escaneado, não NF-e XML. O estoque não tem combustível até o XML chegar. Por
isso o certificado é o pré-requisito, não paralelo. O puller é a linha de
combustível.

## Para rodar de verdade (na frota)
1. `npm install` em `services/sefaz-dfe/`.
2. Env na máquina: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `TENANT_ID`,
   e **`CERT_ENCRYPTION_KEY`** (a mesma do Edge — subir via secrets-sync).
3. `node run.mjs --dry` (autentica + lista) → depois `node run.mjs`.
4. cron horário; cStat 656 = consumo indevido (esperar 1h quando em dia).

## Gotcha legal
Destinatário (compras) recebe só RESUMO até MANIFESTAR ciência (210210); o XML
completo com itens só vem depois. Manifestação automática NÃO ligada (peso
legal) — passo explícito a habilitar quando o Pedro autorizar.

## Pendências intocadas
Rotação das chaves vazadas; UI de dossiê + estoque; refino de título via LLM.
