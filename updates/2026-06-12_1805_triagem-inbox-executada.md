# Triagem do inbox executada + pipeline Bitwarden pronto

**Sessão:** autoresearch (Mac mini), 2026-06-12 ~18h05. Continuação do
diagnóstico de fricção (update 17h45).

## O que foi decidido (Pedro, via setas)

1. "Pode apagar tudo" — duplicatas dos 114 agentes + novo-projeto/ (26 MB).
2. "Pode mover" — dados de cliente e specs saem do cérebro pros repos donos.
3. Chaves vazadas: Pedro já está subindo pro Bitwarden; pediu pra "deixar
   pronto pra subir mais chaves".

## O que mudou (resumo; detalhe no lab/changelog.md)

- **lab/ ganhou**: `agents/c-level/` (6 agentes, catalog.tsv atualizado —
  total agora 120); skills `fluxo-implementacao-3-agentes`,
  `meta-prompt-gerar-personas`, `subir-chaves-bitwarden` (nova); packs
  `fullstack-monorepo/` (15), `instagram/` (6), `fim-das-planilhas/` (10);
  4 referências em `knowledge/raw/`.
- **risen-ai-connect ganhou** (sessões do ai-connect, atenção):
  `clientes/euca/` e `clientes/construbase/` (planilhas/cartões dos tenants),
  `docs/historico-sprints/` (65 md), `docs/runbooks/21-05-26 - 00-FLUXO-
  RESPOSTA-IA.md` (base da futura skill /ia-caiu). NADA commitado.
- **super-secretaria-functions ganhou**: `docs/00-super-secretaria-projeto-
  base-v3.md`. NADA commitado.
- **~/Dev/projeto-instagram/**: MCPs + transcrições (projeto próprio agora).
- **Inbox: VAZIO** (ficam README + pastas vazias "Minha Obra"/"Risen OS" —
  Pedro não sabe por que estão vazias; provável dump falho).

## Bitwarden — pronto pra mais chaves

Pipeline `~/Dev/risen/secrets-sync/` conferido: `risen-secrets.mjs push
<PROJETO> ./.env.push` com token no Keychain (`bws-access-token`); 9 projetos
no cofre; prompt pronto em `PROMPT-PARA-CADA-PROJETO.md`. Receita de uma tela:
`lab/skills/subir-chaves-bitwarden.md`. Regra pra todas as sessões:
**valor de secret nunca no chat — sempre via arquivo .env.push/.env.local.**

## Pendências

- [ ] Próximo do plano de fricção: CLAUDE.md kernel nos 5 repos
      (ai-connect, super-secretaria-functions, newrisenos, risencore,
      pedro-obras) — ver bloco novo em wiki/pendencias-globais.md
- [ ] Sessões ai-connect/SuperSec: avisar nos seus updates se os arquivos
      movidos devem ser commitados ou ficar fora do git
- [ ] Scoreboard: primeiro uso real de qualquer item novo (c-level, packs)
      deve ser relatado em updates/ pra virar promoção
