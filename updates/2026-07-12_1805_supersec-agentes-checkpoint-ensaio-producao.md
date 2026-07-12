# CHECKPOINT SUPERSEC-AGENTES — 12/07 ~18h05 (sessão Fable, missão 12 → modo ensaio)

> Pra uma sessão que nasce SEM memória: você é a sessão **SUPERSEC-AGENTES** do quadro
> `~/Dev/autoresearch/COORDENACAO-ESTEIRA.md` (papéis: CORE = esteira; VOCÊ = agentes/
> enquadrador/curadores; FROTA-MONITOR = máquinas). Leia o quadro primeiro. Regras vivas:
> **você ORQUESTRA, nunca executa** — cada operação que a API pagaria = 1 subagente
> Sonnet; prompts REAIS sem adaptar; API paga OFF até o Pedro ligar; bugs = catalogar
> B## no quadro → corrigir → re-ensaiar.

## O que está NO AR (feito e verificado)
- **Enquadrador manual (rodadas 1-67)**: ~503 assinaturas aplicadas via RPC
  `enquadrar_documento`; cérebro (document_tags) em **2.311 tags**. Rodada 67 foi o 1º
  ato do modo ensaio (aplicada dos arquivos `.APLICADO`).
- **Modo ensaio de produção — ciclo 1 COMPLETO**: ensaio 1 (prompt real verbatim, 14
  grupos × 14 Sonnets) expôs **B22** (CLASSIFY_SYS vocabulário genérico × lookup por
  nome exato no catálogo → 3/14 aplicáveis TODOS errados, SAAE→"Boleto"; 5 comprovantes
  certos perdidos), **B23** (confidence null passava no gate), **B24** (chamada paga
  antes da checagem de viabilidade). Fix commitado; ensaio 2 (mesmos 14 grupos, prompt
  novo) **LIMPO**: 6/6 corretos aplicados, 8 recusas justificadas.
- **Auditoria dos curadores** (ordem 3): B17 (ledger NOT NULL mudo), B19 (rollover
  fator FEBRABAN → vencimentos 2042/2047 em boleto histórico), B20 (counterpart_name
  lixo), B21 (comprovantes: INSERT impossível — 3 colunas NOT NULL nunca enviadas).
  Detalhe em `super-secretaria-functions/docs/esteira/plano-execucao/BUGS-MISSAO-12.md`
  (B1-B24 + ESTADO-SALVO no fim). **O Core aplicou patches e a materialização acordou**
  (ledger 193, payment_receipts 59 — ver STATUS do quadro ~19h55).

## Pela metade / PENDÊNCIAS (com dono)
1. **[PEDRO] Deploy do worker-enquadrador corrigido** — commit
   "enquadrador: B22 contrato de vocabulário..." no super-secretaria-functions
   (arquivos: `supabase/functions/_shared/llm_docs.ts` novo `ENQUADRA_SYS`+`enquadraLlm`;
   `supabase/functions/worker-enquadrador/index.ts`). A trava de permissão exigiu OK
   humano. Comando: `supabase functions deploy worker-enquadrador --project-ref
   abysijyuhvwrczxnwaqg` (SUPABASE_ACCESS_TOKEN = bws secret get
   397251ce-20b0-423d-b31f-b4780170a76f; BWS token no Keychain `bws-access-token`).
2. **[SUPERSEC-AGENTES] Mais 2-3 ensaios** com ondas maiores pra bater estatística
   antes de o Pedro ligar a chave de API no super admin (money gate OFF até lá).
3. **[SUPERSEC-AGENTES] Releitura dos ~40 pares B18** (texto trocado da era 2-workers)
   — lista nos `enquadramento_r*.APLICADO.json` e no caderno §B18; pedir re-extração
   na seção Pedidos do quadro quando a fila (~18k) escoar.
4. **[SUPERSEC-AGENTES] Revisão das receitas restantes**: fiz contas_a_pagar,
   comprovantes e olhada em extratos; faltam funcionarios, nfse, societario,
   fiscalizacao, admissao, nfe (baixados em
   `<scratchpad>/importers_review/` — scratchpad é efêmero; re-baixar do bucket
   `fleet/importers/*.py` se sumiu).
5. **[PEDRO/CORE] Regra de fila com peso** (ditado do Pedro 14:58): docs importantes
   na frente, contratos gigantes pro fim — registrada no caderno; implementação é da
   esteira (Core), pós-validação.

## COMO RETOMAR (passo a passo)
1. `git -C ~/Dev/autoresearch pull` → ler COORDENACAO-ESTEIRA.md (ordens + reports).
2. `git -C ~/Dev/risen/super-secretaria-functions pull` → ler
   `docs/esteira/plano-execucao/BUGS-MISSAO-12.md` (fim do arquivo = ESTADO-SALVO com
   o protocolo completo do ciclo do Enquadrador).
3. Ciclo de ensaio: POST no worker-enquadrador (header `x-worker-secret` do
   `.env.local`, corpo `{}`) → devolve preview de grupos → **1 Sonnet por grupo** com
   os prompts de `scratchpad/ensaio2/system.txt` (= ENQUADRA_SYS, também no
   llm_docs.ts) e user "TIPOS CONHECIDOS: <catálogo> + GRUPO/Arquivos/Assinatura" →
   validar (chave exata no document_catalog, conf ≥0.75, null recusa) → aplicar
   `select enquadrar_documento(rep_id::uuid, doc, pasta, aba, array[assinatura])` via
   management API (`POST https://api.supabase.com/v1/projects/abysijyuhvwrczxnwaqg/
   database/query`).
4. SQL/queries de conferência: fila `documents.status='pending'`; cérebro
   `document_tags where ativo`; materialização `ledger`/`payment_receipts`.

## Notas de working tree (por que não subiu)
- `super-secretaria-functions`: só `scripts/investigador/logs/nohup.out` modificado —
  log de outra sessão, não é meu, não commitei.
- `autoresearch`: `program.md`, `lab/`, `preservado/` são de outras sessões — não toquei.
  O `COORDENACAO-ESTEIRA.md` do disco tinha texto do Core ainda não commitado; meu
  commit de checkpoint inclui o arquivo inteiro do disco (nada se perde).
