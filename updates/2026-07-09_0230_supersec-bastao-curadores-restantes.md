# SuperSec — BASTÃO: o que falta construir (curadores/agentes restantes) — 2026-07-09

Sessão de 07-09/07 encerrando em 84% de contexto. Estado: esteira revisada e blindada,
curador NFe v4 + CaP v2 em produção, **teste dos XMLs concluído com sucesso** (124 PDFs
completados pela chave-44, 102 produtos com EAN, +20 itens recuperados pelo gabarito,
estoque R$383k sem dobrar), Estoque v2.1 na tela (canônico GTIN, Últ×Médio, fornecedor,
compras inline, EAN), 162 grupos de consulta (as 4 lacunas fechadas: ICMS 27 UFs,
LC116 104, feriados, ITCMD 27). Fluxograma-mestre: artifact 🧩 (estilo painel, com os
nºs dos 57 dentro de cada card) + doc `docs/esteira/revisao-esteira-2026-07-08.md`.

## Regras aprendidas HOJE (não re-aprender)
1. **Movedor cataloga, nunca DEScataloga** (deploy d036c67): retry não rebaixa
   processed→a_processar. 2. **Superseded sai das tabelas operacionais** (migration
   20260708200000) senão estoque dobra. 3. Chave-44: troca de bastão + herança fina
   (o índice único é parcial; upsert PostgREST não serve em suppliers). 4. NCM na
   consulta é PONTUADO. 5. CFOP impresso é do EMITENTE (destino real = resíduo v4).

## PROGRESSO 09/07 madrugada² (sessão continuou após o update)
- ✅ Interface da esteira COMPLETA no painel Ao Vivo (10 curadores + 11 agentes com
  fontes dos 57; front e819b43). ✅ Item 1: Extrato+Comprovante ATIVADOS (assinatura
  'Extrato (OFX)' no cérebro, extraction_scripts active, +doc_type 'extrato').
- ✅ Item 2: AGENTE FINANCEIRO v1 vivo (migration 20260709010000, b52c4b8): RPC SQL
  conciliar_automatico() + cron 10min — valor exato+tipo+20d+candidato ÚNICO = auto
  (conf .95); ambíguo → Sugestões humanas. Acorda com o 1º OFX.
- Teste XMLs concluído: 124 completadas, 102 EANs, +20 itens recuperados, regra
  'movedor não DEScataloga' (d036c67). Painel: 4 curadores ativos.
- ➡️ PRÓXIMO = item 3 (Curador NFS-e) — retomar daqui.

## FILA DE CONSTRUÇÃO (ordem do fluxograma; Pedro validou)
1. **ATIVAR Extrato + Comprovante** — esboços COMMITADOS (`importers/extratos.py`,
   `comprovantes.py`, commit 9787269) e já publicados no bucket fleet. Falta:
   (a) semear assinatura OFX no cérebro (grupo 'Extrato (OFX)', tags OFXHEADER/
   STMTTRN/TRNAMT/DTPOSTED/BANKMSGSRSV, tipo_arquivo='qualquer');
   (b) `update extraction_scripts set active=true where handler in ('extratos','comprovantes')`;
   (c) teste real com OFX do banco do Pedro; PDF de extrato/comprovante → assinaturas
   nascem via Enquadrador (Claude no papel, 0¢). Cards do PipelineVivo.tsx: flip pra ativo.
2. **Agente FINANCEIRO (matching 3 pontas)** — 16·38·39·40. Motor: valor+data+contraparte
   com janela; grava `reconciliations`; página Conciliação acende (3 baldes já prontos no
   front). Ambíguo (2 candidatos) = resíduo.
3. **Curador NFS-e** (31·24·02·39) — retenções: função retencoes() [IRRF 1/1,5% por
   atividade · PCC 4,65% dispensa <R$215,05 (grupo limite-csrf-dispensa) · INSS 11% cessão
   MO · ISS] → bruto no razão + passivo + líquido→CaP. Tabelas TODAS existem
   (retencoes-federais/nf/pj-quadro, prazos-retencao-tomador, iss-lista 104).
4. **Curador HOLERITE** (11·30·14·12·13) — motor_inss_irrf ÚNICO (criar em
   `importers/_motores.py`; tabelas inss-faixas 28/irrf-faixas 27 existem); gabarito =
   soma verbas = líquido ±5c → employees(get→post por CPF, índice parcial!) +
   employee_payslips + payslip_items; kind por palavra.
5. **Motor CALENDÁRIO/PENDÊNCIAS** (25·21) → Hoje (prazos-fiscais* + feriados*; FGTS=dia 20).
6. **Agente FISCAL** (01-05·28·29) — DAS primeiro (tenant Simples; grupos das-anexo-i..v,
   limites, fator R = folha12m/RBT12) → tax_guides origem='calculada' → confronto na
   página Impostos (front já confronta lida×calculada).
7. Contabilização/Razão (37·36) + Patrimônio/Imobilizado (43) + Folha própria (35...)
   + Obrigações (06·32·08·09·07) + Fechamento/Auditor (41·42·46) + Gerencial (18·19·26).
8. Curadores menores conforme papel chegar: Admissão (15), Fiscalização (48⇄56),
   Societário (52-54), Cartões (38).

## Pendências de DOCUMENTO (sem código)
- Pedro vai soltar a LEVA DE BOLETOS na pasta (CaP v2 pronto: cobrança→ledger;
  arrecadação→tax_guides). Só assistir, mesmo ritual dos XMLs.
- Notas de VENDA quando chegarem → saída de estoque (engine pronta, outbound).
- Sincronização Estoque×Core (imagens/canônico): gtin-resolve pronto; depende de
  CORE_ANON_KEY setada no supersec (senão 'no_api') — conferir/plugar quando Pedro pedir.
- Pirapora-MG: feriados municipais pendentes de confirmação (grupo feriados-municipais).

## Como retomar
Sessão nova em ~/Dev/risen/supersec ou super-secretaria-functions: ler este update +
`docs/esteira/revisao-esteira-2026-07-08.md` + fluxograma 🧩. Molde do curador =
`importers/nfe.py` (v4). Aplicar migrations = `scripts/aplicar_migration.sh` ou management
API com token Bitwarden 397251ce-…. Publicar frota = `services/ocr-fleet/publish.sh`.
Commits de hoje: backend até 9787269 · front até 696a52e.

## PROGRESSO 09/07 madrugada³ — "um por um" (Pedro mandou seguir)
- ✅ nº 3 CURADOR NFS-e v1 (d0a7191): XML gabarito, retenções DESTACADAS lidas, tomado→payable líquido, chave natural dedup; assinatura "NFS-e (XML)" (10 tags) + rota NFS-e→nfse no Movedor. Pendência futura: conferir retenções contra IN 1.234 (tabelas prontas).
- ✅ nº 4 CURADOR HOLERITE v1 (010f2e9): gabarito = soma ±5c; INSS/IRRF/FGTS por rótulo; funcionário auto por CPF; payslips+items; 5 doc_types ativos. Recálculo nas faixas = pendência futura. Assinaturas PDF via Enquadrador no 1º doc real.
- ✅ nº 5 CURADOR ADMISSÃO v1 (c1f8ea5): tipo de doc (ASO/contrato/CTPS/RG/ficha), CPF+nome, ASO apto?, funcionário nasce inativo, checklist. Gate S-2200 = Agente eSocial.
- ✅ Painel: 7 curadores ATIVOS de 10 (front 0732348). Faltam curadores: Fiscalização, Societário/Empréstimos, Cartões. Agentes: seguir fila (Calendário → Fiscal/DAS → ...).
- Todos v1 CONSERVADORES: só materializam com gabarito fechado; resíduo → Revisar nomeado. Testar com docs reais do Pedro (holerite/NFS-e/OFX) e iterar rótulos.

## PARA AMANHÃ (Pedro, 09/07 — escrito pela supervisora ao fechar a noite)
ESTADO: missões 01 (Fiscalização) e 02 (Societário/Empréstimos) CONCLUÍDAS e provadas em prod. Executora parada numa ÚNICA pergunta: "usa maquininha de cartão?" — recomendação da supervisora: NÃO uso → card cart dormente → missão 04 (Calendário/Pendências, acende a página Hoje).
PRA RETOMAR: abrir a sessão executora e responder a pergunta ("não uso — dormente, segue pra 04"). Se ela pedir prod e travar: aprovar com "always allow" OU pedir os vales via plano (1 aprovação). A supervisora (sessão-mãe) segue disponível pra dúvidas com ~2% de contexto.

---

## ENCERRAMENTO DO PLANO (2026-07-12 01:20 — supervisora)

**11/11 missões construtivas FECHADAS e testadas em prod** (executora + supervisora
via canal `docs/esteira/plano-execucao/COMUNICACAO-INTERNA.md` — leia lá o histórico).
Placar: fundação · placar+ledger · [cartões DORMENTE por decisão do Pedro] ·
fiscalização · societário · contábil v2 (modelo vivo, censo) · calendário/pendências ·
folha+encargos+eSocial (motor único INSS/IRRF em `_motores.py`) · obrigações por
regime · fechamento+auditor (127 NFs × razão = R$ 38.084.833 AO CENTAVO, diff 0,00%) ·
gerencial + pacote do contador (relatorio_mensal.md + quadro_auditor.csv). Painel
Ao Vivo com a esteira inteira: 7 curadores + 10 agentes vivos + 1 dormente.
Dados de teste 100% limpos (0 empregados-teste/payslips/eventos/closings).

**Lições novas pro bastão:**
1. Teste de curador confere o EFEITO na tabela destino (count>0) — nunca só o
   status do documento (o holerite v1 rodou dias sem materializar NADA: NOT NULL
   de payment_date/company_unit_id falhava MUDO no sb()).
2. Pagamento de holerite sem data no papel: PREVISTO = 5º dia útil do mês
   seguinte (CLT 459 §1º) — curador põe dia 5 fixo, agente refina dia útil.
3. Prod pedido entre sessões passa pelo toque do Pedro agora (classificador
   reteve o regime automático). Comando pronto + `!` funciona bem.
4. `aplicar_migration.sh` precisa de SUPABASE_ACCESS_TOKEN exportado do
   Bitwarden (não vive no .env.local).

**Falta:** missão 12 — calibração ITERATIVA com docs reais do Pedro (roteiro em
`docs/esteira/plano-execucao/12-testes-calibracao.md`: OFX → boletos → PIX →
holerite → NFS-e → auto/intimação) + pendências antigas do bastão (Presumido v2
no Agente Fiscal, CIAP, SPED gerador, 38 linhas conferir:true, feriados Pirapora).

## MISSÃO 12 — observação do teste no limite (2026-07-12 ~02:10, observador puro)
Pedro despejou ~3.564 arquivos (era 2015-2016, escaneados) em Novos Documentos.
Drive captou tudo em ~30min; 4/5 máquinas vivas lendo (~4 docs/min no início).
Primeiros 24 desfechos (lote set/2015): 2 boletos padrão → curador CaP processou ✓;
CEMIG/SAAE → CaP mas resíduo nomeado "cap_98_nao_fechou:vencimento,codigo_receita,
competencia" (conta de consumo ≠ boleto padrão — candidato nº1 do resíduo-LLM);
"Cartão Cx" → a_processar; maioria (salário avulso, cartório, GPS, NF escaneada,
IPTU, Vivo, transferência) → desconhecido/texto_nao_classificado_pdf → Revisar
(cérebro de tags não conhece formatos 2015 — trabalho pro Enquadrador, 1 assinatura
por família). 0 DLQ, 0 error. NADA foi tocado (ordem: aprender com os erros).
