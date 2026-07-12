# 57 Agents Advocacia — Claude Code para advogados

**57 subagentes especializados** para advogados brasileiros, prontos para uso no Claude Code. Cada agente é um especialista em uma rotina específica do escritório de advocacia — gestão de prazos, peças, pesquisa, atendimento, contratos, operação — que atua proativamente quando o contexto da conversa bate com sua especialidade.

## Como instalar (usando os zips desta pasta)

Voce tem **57 zips individuais** + este README. Pode instalar **um a um** (so quem voce vai usar) ou **todos de uma vez**.

### Opcao A — Instalar 1 agente individual

1. Baixe o zip do agente que voce quer (ex: `01-monitor-dje-djen.zip`).
2. Descompacte. Dentro tem o `.md` do agente + um `COMO-INSTALAR.md` com o passo a passo.
3. Copie o `.md` para `.claude/agents/` (no seu projeto) ou `~/.claude/agents/` (global).
4. Reinicie o Claude Code (`/exit` e abra de novo). Pronto.

### Opcao B — Instalar todos os 57 de uma vez (terminal)

```bash
cd /caminho/onde/voce/baixou/57-Agents-Advocacia
mkdir -p ~/.claude/agents
for z in *.zip; do
  unzip -o -j "$z" "*.md" -d ~/.claude/agents/ -x "COMO-INSTALAR.md"
done
```

Reinicie o Claude Code. Confirme com `/agents`.

## Como usar

- **Automatico**: "preciso monitorar o DJEN da minha OAB" → Claude delega para `monitor-dje-djen`.
- **Manual**: "use o agente `tese-repetitiva` para verificar se há tema afetado".
- **Em pipeline**: `triagem-novo-caso` → `onboarding-cliente` → `peticao-inicial-civel` → após sentença, `recurso` → após trânsito, `cumprimento-sentenca`.

## Catalogo (57 agentes — alinhados a 6 categorias da rotina do escritório)

### 1 · Prazos & Acompanhamento (5)
- 01 Monitor DJE / DJEN — busca DJEN/DJE por OAB/CPF/CNPJ, classificação por urgência
- 02 Lembrete de prazo — cálculo de data fatal + régua D-7/D-3/D-1/D-0 + ICS
- 03 Andamento processual — leitura DataJud/PJe/e-SAJ + status + gargalos
- 04 Intimação — leitura, classificação, prazo, minuta de resposta
- 05 Ciência — petição de ciência (simples, sem prejuízo, com renúncia, cumprimento)

### 2 · Petições & Documentos (5)
- 06 Petição inicial cível
- 07 Contestação cível
- 08 Recurso (genérico — escolha de cabimento + redação)
- 09 Parecer jurídico
- 10 Procuração ad judicia et extra

### 3 · Pesquisa Jurídica (5)
- 11 Jurisprudência STJ/STF
- 12 Doutrina
- 13 Lei e súmula
- 14 Tese repetitiva (RR/RG/IRDR/IAC)
- 15 Ementário (banco interno)

### 4 · Atendimento ao Cliente (4)
- 16 Triagem novo caso
- 17 Orientação inicial
- 18 Onboarding cliente
- 19 Follow-up cliente

### 5 · Contratos & Compliance (4)
- 20 Revisão de cláusula
- 21 Comparação de contratos (diff)
- 22 LGPD / Direito Digital
- 23 Due Diligence

### 6 · Operação do Escritório (4)
- 24 Cobrança de honorários
- 25 Agenda de audiência
- 26 Resumo de processo (case briefing)
- 27 Backup do escritório

### 7 · Peças por área do direito (30)

**Cível** — 28 Apelação · 29 Agravo de instrumento · 30 Cobrança
**Trabalhista** — 31 Reclamação trabalhista · 32 Defesa empregador · 33 Cálculo verbas rescisórias
**Família e Sucessões** — 34 Divórcio consensual · 35 Divórcio litigioso · 36 Alimentos · 37 Inventário extrajudicial · 38 Guarda compartilhada
**Criminal** — 39 Resposta a acusação · 40 Habeas corpus
**Tributário** — 41 Mandado de segurança · 42 Embargos à execução fiscal
**Empresarial** — 43 Recuperação judicial · 44 Contrato social · 45 Acordo de acionistas
**Consumidor** — 46 CDC prática abusiva
**Imobiliário** — 47 Despejo · 48 Renovatória · 49 Usucapião extrajudicial · 50 Usucapião judicial
**Previdenciário** — 51 Aposentadoria por tempo · 52 BPC/LOAS · 53 Auxílio-doença
**Operacional** — 54 Cumprimento de sentença · 55 Impugnação ao cumprimento · 56 Cálculo judicial · 57 Minuta de contrato de serviços

## Avisos legais

- Os agentes refletem CPC, CLT, CDC, CTN, CP, CPP, LGPD e legislação especial vigentes em 2026.
- Outputs gerados são **rascunhos**; o advogado responsável deve revisar e assumir a responsabilidade técnica (OAB, art. 32 do EAOAB).
- Templates e exemplos usam dados fictícios.

## Licenca

Uso permitido para clientes ASV Digital / Bravy. Nao redistribuir sem autorizacao.
