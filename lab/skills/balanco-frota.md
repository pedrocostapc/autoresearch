# Skill: balanço-frota — registrar passado/presente/futuro no cérebro

**Quando usar:** ao encerrar um bloco relevante de trabalho num app da frota, ou quando
o Pedro pedir pra "atualizar a pasta geral". Cole o prompt abaixo em qualquer projeto —
cada sessão escreve o próprio balanço datado (nome com app+hora, sem colidir) e o
`autoresearch/` vira a memória viva da frota. Irmã do `sync-projeto-cerebro.md`, mas
com foco em RETROSPECTIVA + DIREÇÃO (não só changelog).

---

```text
TAREFA (rápida, sem gastar à toa): registrar no cérebro compartilhado da frota Risen
um BALANÇO desta sessão/projeto — passado, presente e futuro — pra qualquer sessão
(ou o Pedro daqui a semanas) pegar o bastão sabendo o rumo, não só o changelog.

DESCUBRA em qual app você está (pasta / git remote) via a tabela do ~/.claude/CLAUDE.md.
Depois, NESTA ORDEM:

0) DE ONDE VEM O BALANÇO:
   - Se você ACABOU de trabalhar neste app → use o que já sabe desta sessão.
   - Se é sessão NOVA (não trabalhou agora, ex.: minhaobra, nafazenda, eirisen) → RECONSTRUA
     o estado, econômico: leia a memória do projeto (memory/ + MEMORY.md), os updates recentes
     DESTE app em ~/Dev/autoresearch/updates/, e o `git log --oneline -20`. Não audite o repo inteiro.

1) LEIA antes (continuidade / não duplicar):
   - ~/Dev/autoresearch/updates/  → os 5–10 mais recentes
   - ~/Dev/autoresearch/lab/knowledge/wiki/pendencias-globais.md e decisoes-ativas.md

2) ESCREVA o balanço datado:
   ~/Dev/autoresearch/updates/AAAA-MM-DD_HHMM_<app>-balanco.md
   Curto e HONESTO, com estas seções:

   ## PASSADO (o que a gente fez nestes últimos dias)
   - O que subiu NO AR e foi provado (contratos/URLs/refs/secret-ids do Bitwarden — só ID, nunca valor).
   - O que MELHOROU (o que estava ruim e a gente arrumou / refatorou).

   ## O QUE APRENDEU
   - Descobertas que mudaram o rumo. Padrões que se firmaram.

   ## O QUE ERROU / BUGS
   - Erros cometidos e como corrigiu. BUGS RECORRENTES (os que voltam sempre).
   - Quais RESOLVIDOS (e como) vs quais ainda ESPREITAM.

   ## PRESENTE (onde a gente está)
   - Estado real de cada frente: pronto / pela metade / travado (e esperando o quê).

   ## FUTURO (pra onde vamos)
   - Próximo passo concreto + rumo geral + decisões em aberto pro Pedro.

3) ATUALIZE a wiki SE houver: pendencias-globais.md (cruza apps) · decisoes-ativas.md (rumo).

4) ATUALIZE o projeto: memória automática (memory/ + MEMORY.md) com o durável;
   se schema/edge/secrets mudou, ~/Dev/risen/mapas/build-maps.sh (ou anote no mapas/<app>.md).

REGRAS:
- Segredo NUNCA no chat/arquivo trackeado — só secret-id/nome do Bitwarden.
- E-mail/dado sensível NÃO vai pra autoresearch.
- Econômico: use o que você JÁ sabe; não audite o repo. É balanço, não auditoria.
- Honesto no "errou/bugs" — o valor está aí, não em parecer perfeito.

No fim diga: (a) caminho do update, (b) o que mexeu na wiki, (c) o que gravou na memória.
```
