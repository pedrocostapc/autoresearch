# Da H100 à Fábrica de Arquétipos — resumo da sessão

> Criado em: 2026-06-11 às 05:59
> Sessão: Claude Code em `/Users/pedrocosta/Dev/autoresearch`

## O ponto de partida

A sessão começou com o fork do [karpathy/autoresearch](https://github.com/karpathy/autoresearch)
(→ fork em `pedrocostapc/autoresearch`, clonado neste diretório, remote
`upstream` configurado). A ideia inicial era rodar pesquisa autônoma de LLM
numa H100 alugada.

## A virada de chave

Pergunta central do Pedro: *"ter isso rodando numa H100 vai melhorar meus
sistemas (Ei Risen CRM e SuperSec)?"*

**Resposta: não.** O autoresearch treina pesos de um GPT minúsculo do zero —
não melhora agentes que são prompts sobre o Claude. Mas o **loop** dele
(propor → medir → manter/descartar) é exatamente o que faltava nos sistemas:

- O Ei Risen **já tem** um "autoresearch de personas" em produção: o
  persona-evolution (Scanner → Historian → Drafter → Coach futuro, cron
  semanal dom 04:00) + persona-simulator. O que falta é a **medição objetiva
  antes de publicar** (as colunas metrics_before/after e effectiveness_score
  existem, mas vazias).
- SuperSec e demais: prompts são código com gabarito → evals no repo + iteração
  via Claude Code (Max paga), sem máquina de evolução em produção.
- Conclusão de custos: o investimento real seria GPU (~US$ 20/noite de H100);
  tudo que importa pros sistemas roda com as contas Max, custo extra zero.

## O problema real: escalar personas

Diagnóstico do catálogo (direto do banco eirisen):
- 11 categorias, 22 variações, só 10 com versão publicada — quase todas de
  clientes específicos (euca-brasil, loja-babi, betel, feijoada-oab).
- **Todas as variações `padrao` vazias** → tenant novo de setor não coberto
  cai no genérico.

## O que foi construído: Fábrica de Arquétipos

Em `risencrm/risen-ai-connect/prompts/archetype-factory/`:

| Arquivo | Conteúdo |
|---|---|
| `00-visao-fabrica.md` | Pipeline 5 estágios: taxonomia → template-ouro → geração → portão (simulator + juiz LLM) → seed não-publicado pra aprovação |
| `01-template-ouro.md` | Esqueleto extraído das 3 melhores personas de produção: seções invariantes (abertura, consulta caixas/tools, encerramento 3 msgs, anti-injection, anti-loop, escalonamento) vs. variáveis por setor (fluxo AGENDA/ORÇAMENTO/PEDIDO, FAQ, dial de tom) + 9 critérios do juiz |
| `02-taxonomia-proposta.md` | ~85 setores curados (20 business tier 1, ~45 tier 2, 20 personal) com slug/fluxo — rascunho pra curadoria |
| `03-inventario-caixas-tools.md` | Vocabulário VERIFICADO no código: 19 box_types (compiler) + 12 tools reais. Personas só podem citar o que está aqui |
| `output/salao-de-beleza-padrao.md` | Persona Bia (AGENDA) |
| `output/pizzaria-padrao.md` | Persona Léo (PEDIDO, usa query_delivery_items) |
| `output/assistencia-tecnica-padrao.md` | Persona Davi (ORÇAMENTO) |

## Testes nos perfis reais

Simulação fiel (emulada na sessão, sem custo de API) com prompts + caixas
reais de 3 tenants:

1. **Risen Midia** (pedro@pcconstrutora) — sem arquétipo, 11 caixas. Funciona
   pelas caixas mas sem persona/abertura/escalonamento. FAQ mistura
   PC Construtora (imóveis) com mídia/gráfica. Candidato nº 1 à fábrica.
2. **Construbase** (vanderleiconstruaiconstrubase@gmail.com) — prompt manual
   6,2k bom (fluxos A–G), MAS a variação `construbase` do catálogo está vazia:
   o trabalho não está versionado. Possível promover o manual a v1 do
   arquétipo. Estilo diverge da casa (usa menu numerado).
3. **Feijoada OAB** — o setup mais maduro (arquétipo v2 + 38 FAQs + 16
   objeções). Responde preço na hora, segura negociação. Evento 20/06: prompt
   tem pendências a atualizar na semana do evento.

## Decisões e correções importantes

1. **Anti-robotização**: as personas do piloto saíram "duras" (herdaram o DNA
   sóbrio do Betinho). Correção no template + 3 personas: a referência de TOM
   da fábrica é a **Feijoada** (reage, varia frases, emoji como dial por
   setor); o Betinho é referência só de ESTRUTURA. Critério 9 do juiz
   (naturalidade: "cliente desconfiaria que é bot?") é eliminatório.
2. **Semântica dos níveis (definida pelo Pedro)**:
   - N2 (variação) = ESTILO escolhido pelo tenant: `acolhedora` (default,
     ref. Feijoada) vs `direta` (ref. Betinho/EUCA) — não é tier de serviço.
   - N3 (versão) = evolução do estilo; tenant deixa `auto_update` ou trava.
   - Logo: ~85 setores × 2 variações = **~170 personas**, geradas como 1 base
     de regras por setor + 2 renderizações de tom.
3. **Custos**: tudo da sessão rodou na assinatura Max (zero API). A API do
   Pedro (PERSONA_SIMULATOR_ANTHROPIC_KEY etc.) só entra quando o portão de
   qualidade rodar de verdade na infra (persona-simulator/evolve-runner).

## Pendências (próxima sessão)

- [ ] Pedro: curar a taxonomia (riscar/adicionar setores em `02-taxonomia-proposta.md`)
- [ ] Pedro: decidir destino das variações `padrao` vazias no banco — renomear
      pra `acolhedora` ou aposentar inativas
- [ ] Gerar a renderização `direta` das 3 personas do piloto (hoje só existe a base)
- [ ] Seed SQL das personas-piloto (categoria + variações + v1 `is_published=false`),
      fluxo mostro→valida→aplica → testar no admin/persona-simulator
- [ ] Avaliar: promover prompt manual da Construbase a v1 do arquétipo
      `loja-material-de-construcao/construbase`
- [ ] Depois do piloto validado: rodar a fábrica nos ~85 setores (lote)
- [ ] Fechar o loop de medição do persona-evolution (preencher
      metrics_before/after via simulator) — o "val_bpb" das personas
- [ ] Feijoada OAB: atualizar lote/lineup/abadá na semana do evento (20/06)
