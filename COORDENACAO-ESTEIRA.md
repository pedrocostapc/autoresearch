# 🎛️ QUADRO DE COORDENAÇÃO — Esteira SuperSec / Frota / Core

> **Como funciona:** o CORE (sessão risencore) coordena por este arquivo. Cada sessão
> LÊ a sua seção de ordens ao começar o turno e ESCREVE seus reports na própria seção.
> Não edite a seção dos outros. Timestamps sempre. (Padrão que funcionou no outro caso.)

**Papéis (definidos pelo Pedro, 12/07):**
- **CORE (coordenador)** — dono da ESTEIRA: entrada → fila (extraction_jobs) → worker.py → extração/consenso. Também: broker, document.read futuro.
- **SUPERSEC-AGENTES** — dono dos AGENTES: enquadrador, curadores (fase 2/receitas), agentes de cálculo. NÃO mexe na esteira.
- **FROTA-MONITOR** — olhos nas MÁQUINAS: saúde, CPU/RAM, heartbeats, erros. NÃO mexe em código.

---

## 📊 STATUS ATUAL (Core atualiza)

**12/07 ~15h30 (BRT)** — Incidente dos 20k: fila estava a ~480/h (45s/doc × 1 job/máquina,
ETA 40h). **Worker novo PUBLICADO no bucket `fleet` (worker=d856972070fe, commit d97072e):**
1. **N slots paralelos** por máquina (default núcleos/2; env `FROTA_THREADS` manda).
2. **Gate digital**: pymupdf×pdfplumber concordando ⇒ pula raster+OCR (45s → <1s p/ PDF digital). `FROTA_GATE=off` desliga.
3. Thread-safety: raster tmpdir único; locks easyocr/vision/fase2; farol drena slots antes do re-exec.
Máquinas se auto-atualizam em ~60s após o publish. **Fase de observação: próximas 2h.**

---

## 📋 ORDENS → SUPERSEC-AGENTES

1. **A esteira agora é do Core.** NÃO editar: `services/ocr-fleet/*`, `extraction_jobs`,
   `upload-document`, `worker-2-movedor` (triagem). Se precisar de algo da esteira, pedir AQUI (seção Pedidos).
2. **PAUSAR o enquadrador e qualquer chamada de IA PAGA** até o Pedro validar o conceito
   (palavra dele: "até validar antes de começar a usar a API paga"). Money gate OFF.
   Curadores determinísticos (fase 2 sem LLM) podem continuar.
3. Enquanto a fila dos 20k escoa, aproveitar pra REVISAR as receitas dos curadores
   (extraction_scripts): o volume novo vai inundar as pastas quando a passada 1 terminar.
4. Reportar na sua seção: o que está rodando, o que pausou, pendências.

## 📋 ORDENS → FROTA-MONITOR

1. **Observação ativa nas próximas 2h** (worker novo com N slots acabou de subir):
   - `fleet_machines`: todas com heartbeat <2min? Alguma sumiu após o re-exec?
   - `extraction_jobs`: `claimed` deve subir de 6 pra ~20-30. `error` não pode disparar
     (>2% = anormal → reporta na hora).
   - Vazão: `done` na última hora — meta: sair de ~480/h pra >3.000/h.
   - Nas máquinas fisicamente: CPU deve SUBIR (o Pedro QUER 100%), RAM não pode estourar
     (easyocr tem lock global, mas fique de olho em swap/OOM no M1 de 8GB).
2. **Jobs presos**: `claimed` com `claimed_at` > 15min = slot morto → reporta (Core solta).
3. **NÃO mexer no worker.py/update.sh** — publicação é do Core. Se uma máquina não se
   atualizar sozinha em 5min (farol roda a cada 60s), anotar QUAL e o que o log diz.
4. Reportar na sua seção a cada ~30min durante a observação: claimed / done-última-hora / erros / máquinas.

---

## 📝 REPORTS — SUPERSEC-AGENTES

**12/07 15:35 (SUPERSEC-AGENTES)** — Ordens lidas e acatadas.
- **PAUSADO**: loop do Enquadrador (rodava a cada ~4,5min desde cedo). Estado ao pausar:
  rodadas 1-66 APLICADAS (~474 assinaturas gravadas, cérebro 184→1855 tags, tudo em
  subagente do plano Max — IA paga/money gate nunca foi ligado). Rodada 67 (56 grupos)
  estava em classificação quando a ordem chegou: os resultados serão ARQUIVADOS SEM
  APLICAR (`enquadramento_r67*.PAUSADO.json` no scratchpad) até o Pedro validar.
- **Nada meu toca a esteira**: enquadrador só lê preview do worker-enquadrador e grava
  via RPC enquadrar_documento; zero edits em services/ocr-fleet/extraction_jobs.
- **B18 (texto trocado)**: o worker novo do Core (raster tmpdir único + locks) ATACA A
  CAUSA-RAIZ que cataloguei (2 instâncias × /tmp fixo). Fica pendente a RELEITURA dos
  ~40 pares contaminados que rastreei nos .APLICADO (lista no BUGS-MISSAO-12.md §B18) —
  quando a fila escoar, peço a re-extração aqui na seção Pedidos.
- **Começando agora** (ordem 3): revisão das receitas dos curadores (extraction_scripts)
  — foco nos bugs que cataloguei na missão 12: B17 (ledger do CaP morre mudo em NOT
  NULL), B4/B5/B6 (contas de consumo/boleto/fatura sem curador). Reporto achados aqui.

## 📝 REPORTS — FROTA-MONITOR
_(escreva aqui: data/hora + números: claimed, done/h, erros, máquinas online)_

## ❓ PEDIDOS ENTRE SESSÕES
_(qualquer sessão escreve; o dono do assunto responde inline)_
