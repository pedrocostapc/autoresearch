# Core: landing consertada, mapas dos 7 projetos, barramento desenhado

> Criado: 2026-06-11 ~13:30 — sessão Claude Code em `/Users/pedrocosta/Dev/risen/risencore`

## Contexto que o cérebro ainda não tinha

Esta sessão é dedicada ao **Risen Core** (`risencore`, gateway da suíte). Em
10/jun o Core foi reduzido a só GTIN (6 edges operantes); manual da sessão em
`Dev/risen/BRIEFING-CORE.md`. O mapa-projetos da wiki não menciona o Core —
candidato a entrar no próximo health check.

## O que foi feito (10–11/jun)

1. **Landing do Lovable consertada**: o hardening de 10/jun removeu o `.env`
   (público — anon key) do git e o site abriu em branco; fix = devolver ao repo
   (commit `909309f`, push direto na main autorizado pelo Pedro).
2. **Mapas raw dos 7 projetos** em `Dev/risen/mapas/` (`build-maps.sh` regenera):
   edges, tabelas+linhas, RPCs, buckets, crons de cada Supabase. Achados:
   nafazenda está em OUTRA conta (PAT 403) e existem 2 projetos extras no PAT
   ("Risen" = credenciais Cora órfãs; "Risen MedOs" vazio).
3. **Inventário de secrets (só nomes)** em `Dev/risen/mapas/SECRETS-INVENTORY.md`
   pro mutirão Bitwarden. Flags: PAT da conta guardado como secret de edge no
   minhaobra (prioridade 1), Cora órfã no projeto "Risen", FocusNFe órfã no core.
4. **Decisões de arquitetura do Pedro** (registradas na memória da sessão Core):
   - Comunicação entre os 7 sistemas: SEMPRE via Core (barramento), nunca
     app-a-app. **A conversa é a nível de TENANT** (vínculo explícito
     `core_tenant_links`, Core traduz tenant_id origem→destino).
   - Medir uso desde o dia 1 (log por chamada), precificar só quando houver
     cliente externo; sistemas próprios = `billing_exempt`.
5. **Desenhos prontos pra implementar** (no repo do Core):
   - `docs/barramento-eventos-v1.md` — pub/sub com HMAC+retry, envelope com
     tenant_ref, 3 tabelas + 2 edges.
   - `docs/integracao-crm-risenos-v1.md` — missão 1: IA do CRM lê produtos/
     serviços/horários do risenos (caixas `persona_boxes` viram espelho
     automático), agenda ao vivo via proxy síncrono, e fase 3 = provisionar
     instância da IA de dentro do risenos. Aprovado em conceito pelo Pedro.
6. **CLAUDE.md criado na raiz do risencore** com a ponte pro cérebro (não
   existia; convenção da decisão nº 8).

## Relevância cruzada

- A fábrica de arquétipos (sessão eirisen) e esta integração se tocam: as
  personas consultam caixas; com a integração, as caixas de dados (products,
  services, hours, team) passam a ser alimentadas pelo risenos via Core.
- O inventário de secrets interessa à sessão SuperSec/ai-connect (chaves
  Stripe/Google/Anthropic duplicadas entre apps — conferir se são distintas).

## Pendências

- [ ] Implementar lado Core do barramento (migration + v1-events-publish +
      events-dispatch-tick) — aguardando "pode" final do Pedro
- [ ] Pedro: mutirão Bitwarden (usar SECRETS-INVENTORY.md; prioridade = PAT no
      minhaobra)
- [ ] Health check da wiki: adicionar Core/risenos/agencia/minhaobra/nafazenda
      ao mapa-projetos
