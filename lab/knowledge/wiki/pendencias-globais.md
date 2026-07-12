# Pendências globais

> Página viva — consolidada dos resumos em `updates/`. Quem concluir um item,
> marca aqui com data. Atualizada: 2026-06-11 ~13h.

## Diagnóstico de fricção 12/06 — plano de ação (novo)

> Fonte: `knowledge/outputs/2026-06-12-diagnostico-friccao.md` (mineração de
> 2.300 msgs do Pedro). Ordem = impacto.

- [x] CLAUDE.md kernel nos 5 repos — FEITO 2026-06-12 ~18h20 (ai-connect e
      SuperSec estendidos; newrisenos e pedro-obras criados do zero;
      risencore ganhou comunicação+segredos). Sessões abertas nesses repos
      precisam reler o CLAUDE.md
- [ ] **Pedro+Claude: ROTACIONAR segredos vazados em transcripts** (service
      role, sk-ant, sbp_, DO, Cloudflare, tskey, chave SSH) + concluir Bitwarden
- [ ] Skill `/entregar` (commit→PR→merge→push→deploy c/ checklist) + hook
      anti `git add -A`/commit-na-main + worktree por sessão paralela
- [ ] Skill `/ia-caiu` no ai-connect (árvore de diagnóstico já mapeada;
      base: 00-FLUXO-RESPOSTA-IA.md do inbox)
- [ ] Matriz de autonomia em `.claude/settings.json` por repo
- [ ] Status push do worker noturno (update automático ao fim da janela)
- [x] Executar triagem do inbox — FEITO 2026-06-12 ~18h com OK do Pedro:
      ingeridos 6 agentes c-level + 4 packs/skills; dados de cliente movidos
      pros repos donos; duplicatas e novo-projeto apagados. Inbox vazio
      (sobram "Minha Obra"/"Risen OS" vazias — Pedro não sabe por quê;
      ficam até aparecer o conteúdo)

## Cérebro / lab (responsável: Claude)

- [x] Ingerir os 114 agentes (contabilidade + advocacia) — feito 2026-06-11,
      `lab/agents/` + `catalog.tsv`. Originais seguem em Downloads como backup.
- [ ] Curadoria da skills-library quando o download terminar (1825/2494 repos
      às 12:50, ~73%; retomável com `python3 download_skills.py`)
- [ ] Primeiro health check semanal (fundir skills sobrepostas, atualizar wiki)
- [ ] Avaliar os 5 agentes duplicados entre domínios (backup-escritorio,
      cobranca-honorarios, follow-up-cliente, lembrete-prazo,
      onboarding-cliente) — versões diferentes; possível fundir núcleo comum

## Pedro (operação)

- [x] **Worker noturno — acesso e infra PRONTOS** (2026-06-11 19h):
      `ssh desktop-wsl` funcionando do Mac, GPU+CUDA validados por dentro,
      janela 19h/6h30 agendada e testada. Playbook:
      `lab/knowledge/outputs/playbook-worker-noturno-desktop.md`
- [ ] **Pedro: decidir a carga noturna do desktop** — OCR SuperSec (Paddle
      CUDA) vs loop autoresearch p/ 8 GB (job.sh atual é placeholder)
- [ ] **SuperSec: afinidade de job por máquina?** — evidência de perf medida
      (2026-07-06, balanço supersec): 3060ti 21s/doc vs Ryzen5/M1mini ~34s. A
      GPU só ganha em OCR de IMAGEM (PDF-texto é CPU-bound). Ideia: escaneado/
      pesado → 3060ti; texto → resto. Registro da frota agora é `fleet_machines`
      (heartbeat auto-descreve cpu/ram/gpu/engines). Ver `2026-07-06_1840_supersec-balanco.md`.
- [ ] **Pedro: revogar a API key do tailnet** usada no setup
      (https://login.tailscale.com/admin/settings/keys)

- [ ] **Publicar o lote 1 no admin + testar no persona-simulator** (40 personas
      v1 `is_published=false` aplicadas no banco em 2026-06-11)
- [ ] Decidir destino das variações `padrao` vazias no banco eirisen
- [ ] Feijoada OAB: atualizar lote/lineup/abadá na semana do evento (20/06)
- [ ] Decidir se commita `lab/` + `updates/` (branch própria sugerida)
- [ ] Se houver sessão antiga ainda aberta no SuperSec/ai-connect, colar lá:
      "leia o CLAUDE.md novo na raiz e os updates recentes em
      ~/Dev/autoresearch/updates/" (sessões novas já nascem sabendo)

## financaspedro / Concierge Bridge (2026-07-06)

- [ ] **Pedro: rodar 1 bloco de terminal** (no Mac Mini, fora do Code) que (a) põe
      `CONCIERGE_TOKEN` no env do Vercel do financaspedro e (b) instala o motor 24/7
      (launchd `com.risen.concierge-arm` → listener Realtime). É o que **destrava o
      clique real**. Guardrail impede o Claude de fazer (segredo→Vercel + persistência).
      Secret-ids no Bitwarden (cofre financaspedro): `CONCIERGE_TOKEN`
      `4437a150-caf0-493c-b4f9-b47f01516e12` · `CORE_SERVICE_ROLE_KEY`
      `ae3db503-55dc-49f5-9807-b47f01598952`.
- [ ] Depois de destravado: migrar passo-4 do monitor 100% pro `concierge_arm`;
      aposentar `responder_bridge` (ponte por log do Vercel).
- [ ] **Cross-app**: Concierge Bridge é capability genérica do Core
      (`v1-concierge-inbox/-pending/-ack`, tabela `concierge_actions`, Realtime).
      Qualquer app da frota pode enfileirar "Pedro aprovou X → executa". Firmar como
      padrão quando o 2º consumidor aparecer.
- [ ] **Pedro (decisão de custo): linkrsn** (Supabase ~R$600/mês) — pausar/deletar/mover
      free. Tentativa de pausar falhou (exige free-tier); nada foi mudado.

## Conjuntas / outras sessões

- [x] ~~Seed SQL das personas-piloto~~ — superado: lote 1 (20 setores × 2
      estilos, inclui as renderizações `direta`) aplicado no banco 2026-06-11
- [x] Pontes CLAUDE.md (SuperSec criado, ai-connect atualizado) — 2026-06-11 12:55
- [ ] Lote 2 da fábrica (resto da taxonomia ~85 setores)
- [ ] Promover prompt manual da Construbase a v1 do arquétipo?
- [ ] Fechar loop de medição do persona-evolution (metrics_before/after)
- [ ] Criar repo `super-secretaria-knowledge` a partir de `lab/agents/`
      (lab/ tem o canônico, mas nada disso está em git ainda)

## Frota — Core/conectores/pedido (sessão 2026-07-06, ver updates/2026-07-06_1823_core-balanco.md)

- [ ] **Ei Risen (eirisen)** = ÚLTIMO conector a fazer (Conectores já em Hub/RisenOS/SuperSec).
      Lá o conector RisenOS liga o painel "Novo pedido" + cria `core_tenant_link`.
- [ ] **Sicoob boleto travado**: emissão precisa do `numeroCliente` de cobrança REAL
      (734534 é contrato, não cliente — 5002). Pedro pega no Sicoobnet→Cobrança. Extrato Sicoob já no ar.
- [ ] **Concierge Bridge** (Core, no ar): falta o consumidor — endpoint no `financaspedro`
      + braço local 24/7 (Realtime→SMTP→ack). Prompt de handoff já entregue ao Pedro.
- [ ] **Pedido CRM→RisenOS**: backend `erp.pedido.criar` provado; falta painel no CRM +
      pagamento (Pix/boleto/link Cora) + volta OS→CRM (`erp.pedido.criado`).
- [ ] Regenerar typegen do Supabase no **SuperSec** (tabela `tenant_connectors` nova; hoje com cast).

## Ei Risen — App Store / IAP (sessão 2026-07-06→09, ver updates/2026-07-06_1829_eirisen-balanco.md)

- [x] **iOS 2.0.3 e 2.0.4 NO AR** — 2.0.4 (fix do login Google que sumiu + avisos) aprovada
      READY_FOR_SALE 09/07. Publicação iOS é **100% headless** agora (recipe no `frota/eirisen.md`)
      — NÃO mandar o Pedro no Xcode. Regressão do Google era `.env` local sem
      `VITE_GOOGLE_IOS_CLIENT_ID` (config pública apagada por sessão paralela) — conferir .env
      local vs origin/main ANTES de buildar.
- [ ] **Catálogo IAP travado em MISSING_METADATA:** 5 recargas consumíveis + 12 add-ons de
      assinatura (seat/instance) CRIADOS na Apple, mas falta (a) prints de paywall das 18 subs
      (Pedro, no device — não pode ser ícone/print da ficha; caso Apple 102906529582), e
      (b) wirar os 17 produtos no CÓDIGO (`appleIap.ts` + `apple-iap-validate`) + des-esconder
      add-ons no iOS. Bônus de recarga = web/Stripe só; iOS credita valor cheio.
- [ ] **5 recargas consumíveis** seguem MISSING_METADATA por motivo não-claro (consumível não
      exige print) — investigar.
- [ ] **Aprendizado operacional:** ASC API 403 `REQUIRED_AGREEMENTS_MISSING_OR_EXPIRED` = contrato
      Apple pendente (Agreements, Tax, and Banking), não a chave — Pedro aceita e volta.

## Euca Brasil — apuração de desvio (app novo standalone, ver updates/2026-07-06_1830_eucabrasilinvestigacao-balanco.md)

- [ ] **Pedro: exportar o CNAB de retorno (.RET)** da cobrança Cresol (e Sicoob) — destrava casar os 1.418 boletos (42% do valor) com prova. Sem ele, boleto só casa no chute.
- [ ] **Pedro: exportar extratos Stone** (87 baixas, R$1,07mi) e **Sicredi 51646-7** (4 baixas) — únicas contas com baixa no sistema sem extrato.
- [ ] **Pedro: decidir** se tranca a URL com senha/RLS por usuário antes de mandar pros donos (hoje anon lê tudo) + se traz o relatório de Notas Canceladas.
- [ ] Custo novo na frota: **Supabase Micro pago** (org Risen Midia, projeto `eucabrasilinvestigacao`/ref `dwslonurzantbtqpwziw`) — 1º projeto pago da conta.
- [ ] Próximo do Claude: motor de conciliação gravando casamentos no Supabase (só quando o CNAB chegar pra fazer com prova).
- [ ] **Custos Supabase da frota (levantado 2026-07-06):** 2 orgs pagas + 8 projetos Micro ≈ US$110-130/mês.
  INVERTIDO: **eirisen (CRM, o mais pesado — 1,35GB db + 21GB storage) roda em Nano grátis** enquanto
  projetos vazios (gestaorisen 24MB, nafazenda 18MB, linkrsn 13MB) pagam Micro. REGRA confirmada pelo
  Pedro: em org paga, Nano é COBRADO como Micro — downgrade NÃO economiza; economia real = transferir
  pra org free ou deletar. Decidir: upgrade do eirisen? destino do linkrsn?

## eirisen — Josemac 463 (sessão 2026-07-06 tarde, ver updates/2026-07-06_1835_eirisen-balanco-josemac463.md)

- [x] ~~Pedro: rodar os 2 comandos `!`~~ — FEITO 06/07 ~21:45 UTC: 5 functions deployadas
      (freio validado: Josemac→423, saudáveis ok) + canário instalado (1ª medição: ainda travado)
- [ ] **Pedro: desativar os usuários da Josemac** (quer "sistema não existe" até voltar)
- [ ] **Quando o canário cantar (WhatsApp do Pedro)**: reativar usuários → tirar Josemac
      de SEND_PAUSED_TENANTS (_shared/send-pause.ts) e PAUSED_TENANTS
      (sync-contact-photos) → redeploy → religar IA
- [ ] **Rotacionar/atualizar `EVOLUTION_API_KEY` no Bitwarden** (dá 401 na Evolution hoje;
      a por-instância em whatsapp_providers.config funciona)
- [x] ~~Backlog eirisen: ack pipeline global morto~~ — RESOLVIDO 08/07 (main 4b2f03c):
      Evolution manda `keyId`, webhook lia key.id → todo ack descartado; 1 linha; primeiro
      ✓✓ da história confirmado em prod minutos após deploy
- [ ] **Sprint "import seguro" aguardando ok do Pedro** (foto lazy + adota-jid + checagem
      8/9 sob demanda + carência de número novo + broadcast só p/ quem conversou)

## Minha Obra (minhaobra) — custo por obra (sessão 2026-07-06, ver updates/2026-07-06_1834_minhaobra-balanco.md)

- [x] **Custo real por obra voltou a aparecer** (Fase 1): view `vw_custo_obra` (+ `_consolidado`)
      é a fonte única; `useExecutiveData`, `ComparativoObras`, `useObraCustos` migrados. A
      `custos_obras` legada estava quebrada (trigger de materiais/despesas morto desde out/2025).
- [ ] **Fase 2 (UI de custo):** aba "Custo" no drill-down (breakdown, timeline mensal, lista de
      lançamentos, a-receber cliente/empreiteiro, previsto×realizado da mão de obra); cards do
      portfolio com categoria/custo-m²/margem; reescrever `CustosObra.tsx` (ainda lê a tabela legada).
- [ ] **Fase 3:** tabela `obra_orcamento` (planejado por obra) → planejado×realizado×saldo.
- [ ] **Estimativa de obra (top-down) = feature futura, separada:** m² × SINAPI por região.
- [ ] Pedro validar na tela: Editar Recibo (`/recibos/:id/editar`) e os custos.
- [ ] Aposentar 4 dialogs órfãos em `components/obras/custos/`; mover upload "Manuais e Garantias"
      (hoje em Documentação → Memoriais Descritivos) pra lugar mais óbvio.
