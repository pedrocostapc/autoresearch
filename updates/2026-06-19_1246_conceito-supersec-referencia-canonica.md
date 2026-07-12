# Conceito SuperSec travado numa referência canônica (anti-desvio)

2026-06-19 — super-secretaria-functions, branch main. Doc novo:
`docs/conceito-supersec-referencia.md` (cópia idêntica em `~/.claude/plans/eu-criei-um-sistema-refactored-pebble.md`).

ATENÇÃO qualquer sessão que for mexer em classificação/extração de documentos: leia a
referência ANTES. Uma sessão anterior foi PARADA pelo Pedro por ficar **misturando o
conceito novo (data-driven por tags) com o jeito antigo (scoreDoc hardcoded + LLM no
caminho principal)**. Não repita.

O conceito em 1 parágrafo: secretária que organiza contas/NF/conciliação; inteligência é
ECONÔMICA — extração grátis nas máquinas ociosas faz o máximo, LLM só tapa-buraco.
5 passos: (1) doc chega bagunçado → Novos Documentos; (2) frota lê em BANDO (vários
motores no mesmo doc, junta tudo) → vira TAGS, sem LLM; (3) Agente 1 = comparador PURO de
tags vs tabela `document_tags` → move pra pasta; fraco → Revisar; (4) leitor da pasta roda
multi-motor, cruza, mira 98% dos campos de graça, LLM completa SÓ os campos que faltam;
(5) os 57 agentes calculam.

**A verdade do conceito mora no `/admin`** (repo `supersec`, `admin.tsx` + `components/admin/Pastas.tsx`):
aba **Pastas** = "cada pasta é um agente" com 3 partes — Reconhecer (`document_tags`),
Extrair (`extraction_scripts` + engines + confiança 0.98, sem LLM), Agente IA (Haiku/Sonnet
+ prompt, só quando o determinístico não fecha). Handler `importers/<handler>.py` editável
na tela, frota recarrega sem deploy (edge `agent-code`).

**Gap real (o "caminho limpo" deixado de propósito):** `document_tags` e as colunas novas
de `extraction_scripts` (`llm_model`, `prompt`, `nome`, `descricao`, `passo_a_passo`) NÃO
estão em migration e nada no backend lê `document_tags` (classificação ainda é `scoreDoc`
hardcoded em `_shared/classify_doc.ts`). Pode haver drift no banco ao vivo (a UI escreve
nelas) — confirmar.

Decisões travadas: tags APRENDIDAS minerando docs já rotulados (tabela nasce vazia);
piloto = NF entrada/compras end-to-end; router de tags SUBSTITUI o scoreDoc (rede:
desconhecido → Revisar); CNPJ decide entrada vs saída.

Próximo: vasculhar o sistema com o /admin como gabarito → confirmar drift no banco →
plano de implementação do piloto NF-entrada.
