---
name: sync-projeto-cerebro
type: skill
status: active
created: 2026-06-13
nights_used: 0
source: pedido do Pedro 2026-06-13 — manter o contexto de cada projeto atualizado, da fonte certa, e espelhado no cérebro
---

Mantém o `CLAUDE.md` de cada projeto atualizado **a partir do código real** (escrito
pela sessão que vive naquele projeto, não por inferência de fora) e manda uma cópia
para o espelho do cérebro em `lab/knowledge/projects/<slug>.md`, onde a sessão
autoresearch (curador) lê a visão geral sempre atual.

Princípio (lição de 2026-06-13): **só a sessão dona do projeto alimenta o cérebro
sobre aquele projeto, e só com o que dá pra verificar no código.** O curador não
inventa fato de sistema que não enxerga.

## Como o Pedro usa

Em cada aba de terminal (uma por projeto), cole o PROMPT abaixo trocando o `SLUG`.
A sessão daquele projeto atualiza o `CLAUDE.md` e roda o `lab-sync.sh`, que copia o
doc pro cérebro. Slugs sugeridos: `ai-connect`, `supersec`, `newrisenos`,
`risencore`, `pedro-obras`, `skills-library`.

## PROMPT (copiar e colar na aba do projeto; trocar o SLUG)

```
Você está na sessão do Claude Code DENTRO deste projeto. Tarefa: manter o
CLAUDE.md deste repositório atualizado A PARTIR DO CÓDIGO REAL e mandar uma
cópia para o cérebro da organização.

SLUG deste projeto: COLOQUE_O_SLUG_AQUI

REGRA DE OURO: descreva apenas o que você CONSEGUE VERIFICAR lendo o repo
(arquivos, estrutura de pastas, package.json/pyproject, configs, migrations,
supabase/config.toml, scripts de deploy, .env.example — nunca valores de
segredo). O que não der para confirmar no código, marque com
"⚠️ A CONFIRMAR com o Pedro" — NÃO invente, NÃO chute.

Faça, nesta ordem:
1) Leia o CLAUDE.md atual (se existir). Não apague o que já está bom — atualize.
2) Explore o repo o suficiente para descrever de verdade:
   - O que o sistema É (uma frase) e para quem.
   - Arquitetura / pastas principais / entrypoints.
   - Comandos REAIS de build, test e deploy (com as flags certas).
   - Refs, IDs e variáveis-chave (nomes, não valores).
   - Integrações externas e como autenticam (sem segredo no doc).
   - Seção "Fronteiras": o que o sistema NÃO faz e o que NÃO se deve fazer aqui.
3) Atualize/escreva o CLAUDE.md na raiz com isso. Preserve a seção
   "Cérebro da organização" se já existir (ponte para ~/Dev/autoresearch/updates
   e lab/); se não existir, adicione-a.
4) Garanta que o final do CLAUDE.md tenha esta regra de manutenção:
   "Mudou como o sistema funciona? Atualize este arquivo e rode:
    bash ~/Dev/autoresearch/lab/bin/lab-sync.sh SLUG"
   (troque SLUG pelo slug deste projeto).
5) Rode: bash ~/Dev/autoresearch/lab/bin/lab-sync.sh SLUG
   (copia este CLAUDE.md para lab/knowledge/projects/SLUG.md).
6) Me devolva: um resumo curto do que mudou desde a última versão + a lista do
   que ficou marcado "⚠️ A CONFIRMAR com o Pedro".
```

## O que o curador (autoresearch) faz com isso

Lê `lab/knowledge/projects/*.md` ao iniciar — é a visão geral verificada de todos
os projetos, sem o curador precisar entrar em cada um nem inventar nada. Mantém o
mapa entre projetos (`wiki/mapa-projetos.md`) a partir desses espelhos, e junta as
listas "⚠️ A CONFIRMAR" para o Pedro decidir.

## Mecânica (resumo)

- `lab/bin/lab-sync.sh <slug>` — copia o CLAUDE.md/AGENTS.md do repo atual para
  `lab/knowledge/projects/<slug>.md` com cabeçalho de data + commit. Zero IA.
- `lab/knowledge/projects/` — espelho vivo, sobrescrito a cada sync. NÃO é o inbox
  (que é triagem de coisa nova); é a fonte de overview do curador.
- Futuro opcional (Camada 3): agente agendado por projeto que regenera o CLAUDE.md
  do código semanalmente e roda o sync — só ligar quando valer o custo.
