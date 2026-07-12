# 57 Agents Contabilidade — Claude Code para contadores

**57 subagentes especializados** para escritórios contábeis brasileiros, prontos para uso no Claude Code. Cada agente é um especialista em uma rotina específica do escritório — apuração, obrigações acessórias, folha, conciliação, atendimento, operação interna — que atua proativamente quando o contexto da conversa bate com sua especialidade.

## Como instalar (usando os zips desta pasta)

Voce tem **57 zips individuais** + este README. Pode instalar **um a um** (so quem voce vai usar) ou **todos de uma vez**.

### Opcao A — Instalar 1 agente individual

1. Baixe o zip do agente que voce quer (ex: `01-apuracao-simples-nacional.zip`).
2. Descompacte. Dentro tem o `.md` do agente + um `COMO-INSTALAR.md` com o passo a passo.
3. Copie o `.md` para `.claude/agents/` (no seu projeto) ou `~/.claude/agents/` (global).
4. Reinicie o Claude Code (`/exit` e abra de novo). Pronto.

### Opcao B — Instalar todos os 57 de uma vez (terminal)

```bash
cd /caminho/onde/voce/baixou/57-Agents-Contabilidade
mkdir -p ~/.claude/agents
for z in *.zip; do
  unzip -o -j "$z" "*.md" -d ~/.claude/agents/ -x "COMO-INSTALAR.md"
done
```

Reinicie o Claude Code. Confirme com `/agents`.

## Como usar

- **Automatico**: "preciso apurar o DAS de abril/2026 desse cliente" → Claude delega para `apuracao-simples-nacional`.
- **Manual**: "use o agente `tese-repetitiva` para verificar se há tema afetado".
- **Em pipeline**: `cadastro-nf` → `conciliacao-bancaria` → `fechamento-mensal` → `relatorio-mensal` → `cobranca-honorarios`.

## Catalogo (57 agentes — alinhados a 6 categorias da rotina do escritório)

### 1 · Apuração & Tributário (5)
- 01 DAS Simples Nacional
- 02 ICMS / ISS
- 03 PIS / COFINS
- 04 IRPJ / CSLL
- 05 Conferência de guia

### 2 · Obrigações Acessórias (5)
- 06 SPED Fiscal (EFD-ICMS-IPI)
- 07 ECF / ECD
- 08 DCTFWeb
- 09 EFD-Reinf
- 10 eSocial

### 3 · Folha & Departamento Pessoal (5)
- 11 Holerite
- 12 Férias e 13º
- 13 Rescisão CLT
- 14 INSS / FGTS
- 15 Admissão

### 4 · Conciliação & Financeiro (4)
- 16 Conciliação bancária
- 17 Cobrança honorários
- 18 DRE mensal
- 19 Fluxo de caixa

### 5 · Atendimento ao Cliente (4)
- 20 Triagem WhatsApp
- 21 Documentos pendentes
- 22 Onboarding cliente
- 23 Follow-up cliente

### 6 · Operação Interna (4)
- 24 Cadastro de NF
- 25 Lembrete de prazo (calendário fiscal)
- 26 Relatório mensal
- 27 Backup do escritório

### 7 · Especializações por área (30)

**Tributário** — 28 MEI · 29 IPI · 30 IRRF folha · 31 Retenções tomador
**Obrigações** — 32 EFD-Contribuições · 33 DIMOB · 34 DMED
**Folha** — 35 Folha de pagamento mensal
**Contábil** — 36 Plano de contas CPC · 37 Lançamentos contábeis padrão
**Conciliação** — 38 Cartões/credenciadora · 39 Fornecedores · 40 Clientes
**Fechamento** — 41 Fechamento mensal · 42 Balancete · 43 Ativo imobilizado/depreciação
**Análise estratégica** — 44 Análise de regime tributário · 45 Recuperação créditos PIS/COFINS · 46 Revisão fiscal/cruzamento SPED
**Malha fina** — 47 PF · 48 PJ
**Consultoria** — 49 Due diligence contábil · 50 Valuation PME
**IR Pessoa Física** — 51 IRPF declaração completa
**Societário** — 52 Abertura empresa · 53 Alteração contratual · 54 Encerramento/baixa
**Contencioso fiscal** — 55 Parcelamento Receita Federal · 56 Resposta a fiscalização
**Reforma Tributária** — 57 CBS / IBS (EC 132/2023)

## Avisos legais

- Os agentes refletem CTN, RIR/2018, IN RFB, LC 87/96, LC 116/2003, LC 123/2006, LC 190/2022, EC 132/2023 (Reforma Tributária), Resolução CFC 1.546/2024 e legislação especial vigentes em 2026.
- Outputs gerados são **rascunhos**; o contador responsável deve revisar e assumir a responsabilidade técnica (CRC, Resolução CFC 1.546/2024).
- Templates e exemplos usam dados fictícios.

## Licenca

Uso permitido para clientes ASV Digital / Bravy. Nao redistribuir sem autorizacao.
