# Decisões ativas

> Decisões do Pedro que valem entre sessões. Cada uma cita a fonte.
> Se uma decisão for revertida, mover para o fim com data e motivo — não apagar.

1. **Divisão de trabalho (2026-06-11, nesta sessão):** o Claude constrói e
   mantém o cérebro (`lab/`, wiki, curadoria, memória entre sessões); o Pedro
   toca a operação dos produtos do jeito que já vinha fazendo. Não despejar
   sobre o Pedro tarefas de organização do cérebro.
2. **Custos (2026-06-11, sessão fábrica):** tudo que dá pra fazer via Claude
   Code roda na assinatura Max — custo extra zero. API key só em produção
   (persona-simulator/evolve-runner). GPU H100 (~US$20/noite) só para o loop
   do autoresearch.
3. **Semântica dos níveis de persona (2026-06-11, sessão fábrica):**
   N2/variação = ESTILO do tenant (`acolhedora` default | `direta`), não tier
   de serviço. N3/versão = evolução do estilo, com `auto_update` opcional.
4. **Tom das personas:** referência de TOM é a Feijoada; Betinho é referência
   só de ESTRUTURA. Critério 9 do juiz (naturalidade) é eliminatório.
5. **Arquivar, nunca deletar** (schema do lab): item demovido vai para
   `archive/` com motivo.
6. **`updates/` é o canal entre sessões:** formato `YYYY-MM-DD_HHMM_<slug>.md`;
   toda sessão lê os recentes ao abrir e escreve ao fechar bloco relevante.
7. **Git deste repo:** mudanças locais (program.md, lab/, updates/, CLAUDE.md)
   ficam fora do master até o Pedro decidir; idealmente branch própria antes
   de pull do upstream Karpathy.
8. **Ponte para o cérebro em todo projeto (2026-06-11, sessão pontes):** o
   CLAUDE.md de cada repo do Pedro deve ter a seção "Cérebro da organização"
   (ler `updates/` ao abrir, escrever ao fechar, `lab/` como fonte de
   agentes/skills). Modelo: a seção no CLAUDE.md do risen-ai-connect.
9. **Escrita no banco eirisen (2026-06-11, sessão fábrica):** sempre fluxo
   mostro→valida→aplica com aprovação explícita do Pedro; leitura livre via
   `risen-read.sh`.
10. **Política da frota (2026-06-11, sessão worker noturno):** prioridade por
    demanda, igual para todas as máquinas:
    `usuário no teclado > fila SuperSec > treino de IA > ocioso`.
    Se há fila grande no SuperSec, as máquinas (inclusive a GPU do desktop)
    trabalham para ela; sem fila, as ociosas rodam treino (autoresearch).
    Troca de modo com histerese (ex.: entra OCR fila>100, sai fila<20) e
    sempre ENTRE unidades de trabalho (contrato STOP). Supersede o "treino
    primário" anotado pela sessão SuperSec em 11/06. Pendências p/ vigorar
    plenamente: endpoint queue-status + Paddle-GPU no WSL do desktop.
    **Refinamento (Pedro, 2026-06-11 ~20h): o desktop trabalha TAMBÉM de dia,
    em modo capado** — browser/escritório não usam GPU. Tetos: `.wslconfig`
    memory=14GB/processors=20 (garantia de hardware p/ o Windows),
    `nvidia-smi -pl 130` de dia / `-pl 200` às 18h (ventoinha quieta),
    `nice 19` no treino, e back-off se detectar uso real de GPU pelo usuário
    (pausa e mede a cada ~10 min; jogo/vídeo dispara, browser não).
    Resultado: ~22h/dia de trabalho útil em vez de ~11h.
12. **Aluguel NÃO emite NFS-e — emite recibo, e só depois de pago (Pedro, 2026-07-03):**
    no Hub (risenagência, Contas a Receber), um recebível de **origem `aluguel`**
    NÃO emite nota fiscal. Emite **recibo de pagamento**, habilitado **só quando
    `status=pago`**. O botão "emitir" do aluguel NÃO pode abrir o modal de NFS-e
    (gov.br/Focus) — hoje abre "Emitir serviço — aluguel (só nota)", que está ERRADO.
    Serviço normal (outdoor/instagram) segue nota+boleto. **Supersede** o registro de
    30/06 que dizia "aluguel = só NFS-e + recibo". Fix é do CODE DO HUB.
11. **Chaves de API de IA/voz = só o Pedro provisiona, via UI (Pedro, 2026-07-03):**
    as chaves de terceiros no Bitwarden — **Anthropic** (`ANTHROPIC_API_KEY`,
    `PERSONA_SIMULATOR_ANTHROPIC_KEY`), **Deepgram/voz** (`DEEPGRAM_API_KEY`), e
    afins (Lovable AI, etc.) — pertencem ao sistema pra que foram criadas (hoje:
    **Ei Risen / CRM**). **NENHUMA sessão/agente pode implementar, cablear, copiar
    ou reusar essas chaves em OUTRO sistema** sem autorização explícita do Pedro.
    Se um app precisar de IA/voz, é decisão do Pedro e entra **pela UI do super
    admin** — nunca "pega a chave que já existe e usa em outro lugar", nunca
    hardcode. Vale pra todas as sessões, inclusive as do cloud/Lovable.
14. **Euca Brasil apuração — Supabase Micro pago + método "prova antes de acusar" (Pedro, 2026-07-06):**
    o app `eucabrasilinvestigacao` (investigar desvio na Euca Brasil, standalone, fora do Core) ganhou
    **Supabase próprio, plano Micro PAGO** (org Risen Midia, ref `dwslonurzantbtqpwziw`) — Pedro autorizou
    (não tinha free sobrando). Método da apuração (regra de ouro do Pedro): importa cru → rotula ruído →
    sobra dinheiro real → casa por CHAVE (boleto via CNAB / CNPJ), **nunca por valor+data** → o que não
    casa é "falta informação", **não acusação**. Guardar TODAS as colunas (nada de descartar). Truque útil:
    o export certo da Movimentação Financeira (TGFFIN) é o que **tem a coluna "Data Baixa"** — o "Cabeçalho
    da Nota" (TGFCAB) parece igual mas é as vendas, não o financeiro.
13. **Acesso restrito ao banco p/ funcionário = só ENTRADAS, travado na RLS (Pedro, 2026-07-03):**
    no Hub (risenagência, Financeiro → Extrato) criar um papel "funcionário" que vê
    **só os créditos** (Pix/boletos que caíram) e **NÃO** vê débitos/saídas/pagamentos,
    saldo do dia, nem a vida financeira da empresa. **REGRA DE OURO: travar na RLS do
    `espelho_extrato`** (o papel restrito só lê `type='CREDIT'` — os débitos NEM SAEM
    do servidor), **não** só filtro de tela (senão o funcionário vê pela rede/API). A
    tela esconde cards de saldo/débito e o menu de contas a pagar/faturas pra esse
    papel. Enforcement = RLS; tela = só apresentação. Fix é do CODE DO HUB. Spec
    completo no update `2026-07-03_*_acesso-banco-funcionario-so-entradas.md`.
14. **Import de contatos NUNCA dispara varredura em massa no WhatsApp (Pedro, 2026-07-06):**
    lição do 463 da Josemac (número punido pela Meta após import de 5.000 contatos +
    backfill de fotos em massa). Regra pra toda a frota WhatsApp: importar = só banco
    nosso (normalização + phone_match_key, zero chamadas); foto de perfil = lazy (só
    contato com conversa ou ao abrir a ficha; importado fica de iniciais/cartoon — ok
    pelo Pedro); checagem "tem WhatsApp / 8 ou 9 dígitos" = SOB DEMANDA no primeiro
    envio real (1 lookup, cache no contato), nunca em lote; número recém-pareado tem
    carência sem operação em massa; broadcast só pra quem já conversou. Enquanto um
    número estiver punido: instância fica CONECTADA e MUDA (recebe/registra, não envia
    — freio server-side em _shared/send-pause.ts), nunca desconectar/re-parear à toa.

15. **Custo de obra = execução realizada, com regras por origem (minhaobra, Pedro, 2026-07-06):**
    o custo por obra vem de fontes reais, não da tabela legada `custos_obras`. Regras:
    **mão de obra** = recibos **PAGO** (`recibo_etapas.valor_linha`, estornado=false);
    **material** = `itens_venda` **ENTREGUE** com `custo_origem` **OBRA + CLIENTE** — CLIENTE entra
    no custo E gera "a receber do cliente"; **EMPREITEIRO** sai do custo e vira relatório "a receber
    do empreiteiro"; **despesas** = `itens_lancamento_custo` PAGA; **terreno** = `vw_custo_terreno`.
    Hierarquia PRINCIPAL→BLOCO→UNIDADE, rollup por `obra_pai_id`. Fonte única = view `vw_custo_obra`.
    **Estimativa (planejado top-down) é OUTRA coisa, futura: m² × SINAPI por região** — não confundir
    com o "orçamento por obra" (Fase 3) nem com a execução. Autorização do Pedro p/ executar as 3 fases
    direto (aplicar SQL/publicar sem mostrar antes) dada nesta sessão.

16. **Concierge Bridge — envio "1 clique" via Core + braço local, segredo nunca no Vercel
    (financaspedro, Pedro, 2026-07-06):** quando o Pedro autoriza uma ação num app (1º caso:
    responder e-mail no financaspedro), o app **enfileira no Core** (`v1-concierge-inbox`,
    tabela `concierge_actions`, Realtime); um **braço local 24/7 na máquina do Pedro** escuta e
    **executa** (envia SMTP com senha vinda do **Bitwarden ao vivo**), depois `-ack`. O **Core é
    stateless**: guarda só o registro da aprovação (app/kind/ref/choice/meta não-sensível),
    **nunca** credencial. **Regra dura: NENHUM segredo de envio (SMTP/creds) vai pro Vercel** —
    o front só enfileira. Segredo-em-Vercel e persistência (launchd) = **o Pedro roda** (o
    guardrail bloqueia o Claude, de propósito). É **capability genérica do Core** — qualquer app
    da frota pode enfileirar "Pedro aprovou X → executa". Ver update
    `2026-07-06_2140_financaspedro-balanco.md`.

11. **SuperSec — XML é GABARITO DE TREINO, não muleta (Pedro, 2026-07-06):** o XML
    da NF-e mostra o TETO do que dá pra extrair do PDF; NÃO é pré-requisito. Só tem PDF
    → extrai TUDO que o DANFE imprime (fornecedor, produtos, valores; `danfe_extractor.py`
    99,9% portado pra frota) e materializa marcando `completo=false`. Quando o XML chega,
    COMPLETA a mesma nota (dedup por chave-44, XML vence). Corolário: a chave-44 é
    mini-gabarito embutido (deriva emitente/série/número; DV mód-11 = leu certo).
    Ver `2026-07-06_1840_supersec-balanco.md`.
15. **Todo campo de busca da frota segue o padrão Risen (Pedro, 2026-07-08):**
    (1) input NUNCA desmonta durante a digitação (keepPreviousData; campo fora
    do ternário de loading — skeleton no meio da digitação rouba o foco);
    (2) zero resultados não engole o campo (EmptyState só sem busca ativa);
    (3) ordem das palavras não importa ("Costa Pedro" acha "Pedro Costa" —
    cada palavra um ilike, AND); (4) debounce ~300ms + busca no SERVIDOR;
    (5) busca pelo que o leigo tem na mão (nome/fone/email/doc/nº pedido, sem
    exigir formato). Skill completa com implementação de referência:
    lab/inbox/skill-campo-de-busca-padrao-risen.md (ref: eirisen 44b812a).
16. **Membro com login = atendimento SEMPRE interno, nunca wa.me (Pedro, 2026-07-09):**
    no eirisen, se a pessoa da EQUIPE tem usuário/assento no sistema, a IA NUNCA
    encaminha o cliente pra ela por wa.me — direciona INTERNO (transfer_to_team),
    a conversa fica no sistema. O valor de assinar assentos é centralização +
    VISIBILIDADE do dono; wa.me pro zap pessoal do vendedor cegaria o dono. wa.me
    só pra Parceiros externos (outra Caixa) e membro SEM login. Na tela unificada
    de Equipe, campos de WhatsApp/celular/canal SOMEM pra membro com login.
    Reforça o internalMode do ai-reply. Ref: prompts/equipe-unificada/REVISAO-EQUIPE.md.

- **#17 Concierge banco local (11/07/2026):** SQLite `~/Dev/concierge/concierge.db` no Mac 24h (não Supabase agora; app é estático, build lê do .db). Schema: categorias, despesas_pf, transacoes_cartao (natureza pessoal×negócio), contas_a_pagar, pensão. Token Management Supabase do Core está inválido (não sbp_).
