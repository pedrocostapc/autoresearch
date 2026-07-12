# eirisen: FUNDAÇÃO das "5 moradas" da IA SHIPPED (+ contrato pra caixas novas)

Sessão de design 11-12/07 com Pedro fechou a arquitetura definitiva da IA de
atendimento e a fundação já está EM PROD (commit "fundação das 5 moradas" em
main + deploy ai-reply/ai-suggest + 6 functions):

**As 5 moradas**: 1 arquétipo (ramo+personalidade, enxuto) · 2a LEIS DA CASA
(universais da plataforma — único prompt manual) · 2b mapa das caixas (gerado
do schema) · 3 caixas (dado + instrução COLADAS) · 4 ficha do cliente (nova).

**Shipped hoje**: LEIS_DA_CASA em todo tenant (protocolo de lacuna — mata o
"cancelado!" que nunca cancelou; dosagem de pagamento; anti-injeção; identidade
IA; temas proibidos) · trava de DADO do Pix (botão "Não" → chave NEM ENTRA no
prompt) · botões de Eventos passam a valer · botão novo "quando não achar no
catálogo" na caixa Produtos (anota-a-confirmar × diz-que-não-tem, escolha do
dono) · guard mapCoverage (caixa/tool fora do mapa 2b = build quebra).

**⚠️ PRA QUALQUER SESSÃO CRIANDO CAIXA NOVA (ex.: imóveis)**: seguir o contrato
`prompts/arquetipos-2-0/01-contrato-caixa-nova.md` (repo eirisen + cópia em
~/Dev/risen/risencrm/prompts/arquetipos-2-0/). Regras de ouro: instrução de uso
mora NA caixa; dado sensível = trava de dado; registrar no BOX_SCHEMAS +
compiler + BOX_TO_TOOL_MAP (senão o guard novo QUEBRA O BUILD).

**Backlog restante do sprint**: ficha do cliente (aba "Quem é seu cliente"
read-only + tool anotar_cliente + compilador por contato) · arquétipos 2.0
(Josemac rascunho pronto aguardando OK; Construbase tem tool fantasma
transfer_to_agent; Betel; CRD; Genérico — 10 tenants novos hoje atendem SEM
arquétipo) · caixa "o que coletar do cliente".

## UPDATE 12/07 noite — TODAS as caixas de informação viraram sob demanda (read_box)

Decisão Pedro ("tudo lido dentro das caixas, não interessa token; precisão
primeiro"): establishment, hours, links, PAGAMENTO, delivery_config,
calendar_config e calendar_links NÃO são mais despejadas inline — a IA abre
cada uma via tool nova `read_box` e recebe dado + regra de uso JUNTOS no
momento do uso. Prompt permanente ficou: Leis da Casa (2a) + mapa 2b (linha
por caixa ativa, gerada do aiUsage) + regras_gerais/jeito_de_falar (território
do arquétipo) + resumos-mapa dos catálogos + avisos de segurança. Caixa vazia
→ retorno instrui rotear pro escalate (toggle allow_escalate decide se o
cliente é avisado). Commit "read_box" em main + deploy ai-reply/ai-suggest+6.
⚠️ Sessões criando caixas novas: read_box é o padrão pra caixa de INFORMAÇÃO
(singleton); catálogo grande continua query_* próprio. Ver contrato 01.

## UPDATE 12/07 madrugada — camada 4 (FICHA DO CLIENTE) + caixa coleta SHIPPED

Ficha do cliente no ar: contacts.ai_facts (migration) + tool anotar_cliente +
compileContactCard injetada em toda resposta (cadastro + fatos + pedidos
abertos) + aba "Quem é seu cliente" em /contacts/:id (read-only, apagar por
linha) + pedidos clicáveis. Caixa "O que coletar do cliente" (enum 'coleta')
também no ar. Restam SÓ os Arquétipos 2.0: 5 drafts prontos em
prompts/arquetipos-2-0/02-drafts-arquetipos.md aguardando OK de texto do Pedro.

## UPDATE — Arquétipos 2.0 de Josemac (v4) e Construbase (v3) PUBLICADOS

Personalidades calibradas pelo Instagram REAL (Apify, token no Bitwarden):
Josemac "Sempre perto de você" (dragagem própria, vizinho de confiança) ·
Construbase "Energia de feirão" (Mega Feirão 73k seguidores; promoções →
vendedor garante; matou a tool fantasma transfer_to_agent). auto_update=true
→ já valendo. Faltam: Genérico (10 tenants sem arquétipo), Betel v2, CRD.
