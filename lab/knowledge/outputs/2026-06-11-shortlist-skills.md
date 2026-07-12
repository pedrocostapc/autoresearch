# Shortlist de skills — primeiro garimpo do catálogo (2026-06-11)

Fonte: `~/Dev/skills-library/catalog.tsv` (20.000 skills ranqueadas; o catálogo
está completo mesmo com o download dos arquivos ainda em andamento).
Critério: relevância para SuperSec, Ei Risen e o próprio cérebro, priorizada
pelo ranking global (menor = mais usada/instalada).

## Achado principal

**Zero skills Brasil-específicas** no diretório inteiro (busca por fiscal,
NF-e, boleto, contábil, advocacia, PIX: nada além de falsos positivos).
Os 114 agentes próprios em `lab/agents/` são material sem concorrente no
ecossistema — reforça o plano do "skills.sh privado" (`super-secretaria-knowledge`).

## Candidatas por área (rank — owner/repo/skill)

### SuperSec (documentos, fiscal, financeiro)
- 133 — anthropics/skills/**pdf** (oficial Anthropic)
- 1384 — claude-office-skills/**pdf-extraction**; 2107 **pdf-ocr-extraction**
- 2282/2429 — invoice-organizer; 2301 invoice-generator; 2403 invoice-automation
- 888 — github/awesome-copilot/**pdftk-server**

### Ei Risen (WhatsApp, CRM)
- 1973 — claude-office-skills/**whatsapp-automation**
- 2660/3055/3508 — gokapso/agent-skills/**integrate/automate/observe-whatsapp**
- 2058 — claude-office-skills/**crm-automation**

### Infra comum (Supabase)
- 38 — supabase/agent-skills/**supabase-postgres-best-practices**
- 151 — supabase/agent-skills/**supabase**
- 1412 — nextjs-supabase-auth

### O próprio cérebro (memória, knowledge base)
- 728 — github/awesome-copilot/**memory-merger**
- 887 — langchain-ai/**deep-agents-memory**
- 1339 — obra/episodic-memory/**remembering-conversations**
- 1579 — anthropics/knowledge-work-plugins/**memory-management**
- 808 — firecrawl/**firecrawl-knowledge-base**
- 2336 — anthropics/knowledge-work-plugins/**legal-risk-assessment** (ponte p/ advocacia)

## Próximo passo de curadoria

Quando o download terminar: ler o SKILL.md das candidatas acima em
`raw/<owner>/<repo>/<skill>/`, ingerir as aprovadas em `lab/skills/` como
`candidate`, instalar as de uso imediato via `npx skills add <owner>/<repo> --skill <nome>`
no projeto certo (SuperSec ou risen-ai-connect), e registrar no scoreboard
quando forem usadas de verdade.
