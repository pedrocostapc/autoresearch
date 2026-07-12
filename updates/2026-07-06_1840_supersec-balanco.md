# SuperSec — Balanço (2026-07-06)

App: **Super Sec** (gestão documental/fiscal PMEs BR). Dois repos, mesmo Supabase
`abysijyuhvwrczxnwaqg`. Front no Vercel (`supersec-murex.vercel.app`, repo
`pedrocostapc/supersec`). Backend = `super-secretaria-functions` (edge + frota OCR).

Contexto: o sistema foi **reconstruído do zero** seguindo o fluxograma (frota-worker-burra).
Este balanço cobre a semana que levou a esteira de "conceito" a **rodando ponta-a-ponta com
corpus real** (126 NFs materializadas só do PDF).

---

## PASSADO (o que fizemos)

**No AR e provado:**
- **Esteira P1→P2 rodando ponta-a-ponta.** Doc chega → frota lê grátis (multi-engine) →
  cospe `documents.frota_tags` (conta palavras que repetem) → Movedor (`worker-2-movedor`,
  Edge, **deployado**) roteia por tags → curador da pasta extrai → materializa.
- **Curador NFe (`importers/nfe.py`, bucket `fleet`, v3):** XML = gabarito completo; **sem XML,
  extrai TUDO do DANFE** (fornecedor, produtos, valores) via `danfe_extractor.py` (99,9%, portado
  de `scripts/nf-bench` pro bundle da frota). A chave-44 valida/deriva os estruturados. Marca
  `completo=false` no PDF-só → XML depois COMPLETA (dedup por chave, XML vence). **126/126 NFs
  materializadas só com PDF**, com nome do fornecedor + itens no estoque.
- **Curador Contas a Pagar (`importers/contas_a_pagar.py`, v2):** barcode-first (boleto/DARF/DAS/
  GPS + PIX/FGTS). Decodifica FEBRABAN, e ao materializar **PUBLICA no `ledger`** (module_key=
  `accounting`, type=`payable`, status=`open`) → página Contas a Pagar acende.
- **Painéis /admin novos (front):** aba **Ao Vivo** (esteira animada, nós clicáveis com "o que faz/
  onde mexer"), aba **Workers** (frota via registro `fleet_machines` + heartbeat: online/offline,
  CPU/RAM/GPU, engines, docs/hora por app). Aba padrão = Ao Vivo.
- **Heartbeat da frota:** `worker.py` auto-descreve a máquina (platform/cpu/ram/gpu/engines) e bate
  em `fleet_machines` a cada ~30s → as 5 máquinas aparecem SEMPRE (4/5 se uma desligada), não só
  quando processam.
- **Popup "Nova versão disponível"** (receita da frota, Ei Risen) — atualiza sem Cmd+Shift+R.
- **Mesa de cópia de Notas** com **preview do documento embutido** (DocViewer via `get-document-file`).

**O que MELHOROU (estava ruim → arrumado):**
- Assinatura de tags do Boleto estava **diluída** (enquadrei doc-a-doc, 14 tags lixo) → podei pras
  6 discriminantes → boletos voltaram a rotear.
- Movedor carimbava type=`enquadrado` genérico → curador não disparava. Agora **type = nome da
  pasta** → trigger `enqueue_phase2_on_classify` casa o script ativo.
- Mesa de Notas comprimida em 880px → **largura total**, campos dimensionados ao conteúdo, item
  numa linha só, preview grande à direita.

---

## O QUE APRENDEU

- **XML é GABARITO de treino, não muleta** (regra do Pedro, virou princípio). O XML mostra o TETO
  do que dá pra tirar do PDF; se só tem PDF, trabalha com o PDF e deixa o só-XML em aberto até o
  XML chegar (preenchimento progressivo).
- **A chave-44 é um mini-gabarito embutido:** codifica CNPJ emitente, série, número, modelo, UF,
  AAMM. DV mód-11 válido = leu a chave certa → deriva o resto sem depender de OCR por campo.
- **GPU (3060 Ti) só ganha em OCR de imagem**; em PDF com texto, tudo é CPU-bound → a vantagem
  some. Ryzen 5 5560U (móvel) ≈ M1 mini. Números reais: 3060ti 21s/doc, Ryzen5/M1mini ~34s.
- **Extração cara ≠ materialização barata:** re-shape de campo já extraído = backfill no banco,
  não reprocessar na frota (race-prone).

---

## O QUE ERROU / BUGS

**Resolvidos (e como):**
- **Vencimento de boleto caía em 2000/2001** — base do fator FEBRABAN sem o rollover de 22/02/2025
  (fator 4-díg estourou em 9999 e voltou a 1000). Fix: +9000 dias quando a data ingênua cai muito
  no passado.
- **Beneficiário vinha o NOSSO CNPJ** (pagador) — pegava `cnpjs[0]` cego. Fix: pega o que NÃO é
  nosso (exclui `company_units`).
- **`extract_chave` devolvia None em chave VÁLIDA** — os regexes exigiam a chave com espaços ou
  run ≥46 chars; DANFE que imprime a chave **grudada** (44 díg limpos) escapava. Fix: caso "run cru
  de 44", validando pelo DV.
- **NF `direction` = `entrada`/`saida`** no código, mas front + `drive_organize` esperam
  **`inbound`/`outbound`** — inconsistência do próprio repo. Padronizado em inbound/outbound.
- **Ledger vazio → Contas a Pagar em branco:** curador extraía pra `raw_data` mas não publicava a
  linha no razão. Fix: curador popula o `ledger`.
- **Notas em branco:** front lê `raw_data.llm.{prestador/tomador/valor_total_centavos}` + colunas
  (`nfe_number`, `emission_date`, `access_key_44`...); curador só gravava `raw_data.curador`. Fix:
  curador escreve o bloco `llm` + as colunas.
- **Popup de versão falso-positivava toda hora** — code-splitting por rota faz a assinatura do DOM
  nunca bater com `fetch('/')`. Fix: compara servidor-vs-servidor (baseline do 1º fetch) + fechável.
- **Gate do curador marcava `processed` vazio** (Docol OCR-colado) → agora não-fechou vai pra
  `needs_review`.

**Padrão recorrente (o que volta sempre):** eu **estico campos com `1fr`/`flex-1` sem teto** → "campo
pra trilhões". Voltou 3x nesta sessão (numéricos, descrição, card do item). **Lei: largura fixa ao
conteúdo; `flex-1` só com `max-w`.** Outro recorrente: **nome de coluna chutado** (query quebra) —
conferir o schema real antes.

**Ainda espreita:**
- DANFE com layout de itens que o `extract_items` não casa → materializa cabeçalho, itens=0.
- Preview universal só está na página de Notas; falta replicar (Contas a Pagar, Comprovantes, etc.).

---

## PRESENTE (onde estamos)

- **Frota + tags + Movedor + curador NFe + curador Contas a Pagar:** PRONTOS e no ar.
- **Notas Fiscais Entrada:** materializa só do PDF (126/126), com preview + mesa de cópia. PRONTO.
- **Contas a Pagar (ledger):** curador publica; falta reimportar a leva de boletos pra encher.
- **Curadores Extrato / Comprovante / Holerite:** A CRIAR (slots inertes).
- **Agente 2 Financeiro (conciliação) / 3 Fiscal / 4 Relatórios:** A RECONSTRUIR.
- **Enquadrador LLM:** DORMENTE (cofre de API em branco de propósito; gate do Pedro).
- **Cérebro/infra preservados:** tags 144, planta 309, referências fiscais ~32k, 3 filiais.

---

## FUTURO (pra onde vamos)

**Próximo passo concreto:** replicar o preview (DocViewer) nas outras páginas de documento; reimportar
os boletos p/ encher Contas a Pagar; afinar `extract_items` pros layouts que faltam.

**Rumo:** cada TIPO = uma PASTA autossuficiente {tags + curador 98% + agente treinável}. Cresce
criando pastas. Depois que a info está encaixada nas páginas, reconstruir os agentes de cálculo
(financeiro/fiscal) SOBRE o dado.

**Decisões em aberto pro Pedro:**
- Afinidade de job por máquina (escaneado/pesado → 3060ti com GPU; texto → resto)?
- Ligar o cofre LLM (Enquadrador/tapa-buraco) quando e com qual teto de custo?

---

**Refs (sem valores — só ID Bitwarden):** `SUPABASE_ACCESS_TOKEN` = secret `397251ce-20b0-423d-b31f-
b4780170a76f`. Projeto do cofre p/ URL+SERVICE_ROLE do supersec = `1e435ab1-...` (busca por nome).
Frota publica no bucket `fleet` via `services/ocr-fleet/publish.sh` (URL+SRK do cofre, ao vivo).
Front no Vercel: push em `main` → deploy. Último commit front: `3251ad6`.
