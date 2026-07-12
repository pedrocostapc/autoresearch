# Checklist de Migracao — 12 passos

Independente da categoria, segue esses 12 passos pra trocar SaaS por Claude **sem perder dado, sem perder cliente, sem operacao quebrada**.

---

## Antes de comecar (dia 0)

### 1. Decisao formalizada

Voce ja:
- [ ] Calculou ROI (`CALCULADORA-ROI.md`)
- [ ] Confirmou que vale migrar
- [ ] Escolheu UMA categoria (nao varias ao mesmo tempo)
- [ ] Marcou prazo de 14 dias pro processo

### 2. Backup de dados da ferramenta atual

Toda ferramenta SaaS tem export. Vai exportar **antes de qualquer coisa**:

| Categoria | O que exportar |
|---|---|
| Copywriting | Pastas/projetos, brand voice configurado, templates favoritos |
| Automacao | Diagramas dos zaps/scenarios, lista de webhook URLs, credenciais |
| Dados | Dashboards exportados em PDF + queries, fonte de dados (CSV/SQL) |
| Atendimento | Historico de conversas (90+ dias), fluxos/decisões, FAQ atual |
| Documentos | Templates, contratos modelo, branding/logo |

Salva tudo numa pasta `backup-{ferramenta}-{data}/` versionada.

---

## Setup paralelo (dia 1-3)

### 3. Cria pasta do novo fluxo

```bash
mkdir -p ~/migracao-{categoria}
cd ~/migracao-{categoria}
git init
```

Estrutura sugerida:

```
migracao-{categoria}/
├── prompts/        # prompts versionados
├── outputs/        # resultados gerados
├── scripts/        # codigo de automacao se precisar
├── docs/           # base de conhecimento
└── backup/         # export da ferramenta antiga
```

### 4. Roda o prompt do produto

Abre o arquivo correspondente (01 a 05) e segue. **Customiza pro seu negocio** — nao usa generico.

### 5. Configura credenciais (se precisar)

Se for automacao ou atendimento, voce vai precisar de tokens de API:

- [ ] Cria `.env` (NUNCA commit)
- [ ] Anota onde cada credencial veio (qual painel)
- [ ] Documenta em `docs/credenciais.md` (sem o valor — so onde buscar)

### 6. Smoke test

Roda o fluxo end-to-end pelo menos 3 vezes com casos diferentes. Anota:

- [ ] Output bate com o que a ferramenta antiga gerava? Em qualidade?
- [ ] Tempo gasto pra rodar e razoavel?
- [ ] O processo cabe no fluxo do dia a dia ou da pra automatizar?

---

## Periodo paralelo (dia 4-10)

### 7. Roda os DOIS sistemas em paralelo

Por 7 dias:

- A ferramenta antiga **continua ligada**
- Toda demanda nova roda nos DOIS
- Voce compara saidas

**Nao cancela nada ainda.**

### 8. Compara qualidade e tempo

Tabela simples em planilha (sim, ironicamente):

| Caso | Saida ferramenta antiga | Saida Claude | Tempo antiga | Tempo Claude | Vencedor |

Apos 7 dias, voce tem 5-15 casos comparaveis. Se o Claude vence em **80%+** com qualidade aceitavel, segue.

### 9. Treina quem mais usa

Se outra pessoa do time usa a ferramenta antiga, mostra como usar o Claude pra mesma demanda. **Ate aqui, ainda em paralelo.**

- [ ] 1 sessao de 30min explicando
- [ ] Documenta em `docs/como-usar.md` os passos do dia a dia
- [ ] Pessoa roda 2-3 casos sozinha sob supervisao

---

## Cancelamento (dia 11-14)

### 10. Verifica reincidencia

Antes de cancelar:

- [ ] Tem alguma operacao do mes/trimestre que so a ferramenta antiga faz e ainda nao testamos? (relatorio anual, integracao especifica, etc.)
- [ ] Se cancelar, tem dado preso na ferramenta? (export feito no passo 2 cobre tudo?)
- [ ] Tem usuario que ainda nao migrou?

Se algum item ficou em aberto, mais 1 semana paralelo. Sem pressa.

### 11. Cancela com cuidado

Toda SaaS tem **ciclo de cobranca**. Cancele:

- Na **data correta** pro proximo ciclo (alguns cobram antecipado, outros no fim)
- Pelo **canal oficial** (alguns dao desconto absurdo se voce ligar — vale considerar pra fluxo de caixa)
- Com **export feito** dentro dos termos (algumas SaaS bloqueiam acesso ao historico apos o cancelamento)
- **Avisando time** que vai cancelar

### 12. Documenta a migracao

`docs/migracao-{categoria}.md`:

```
# Migracao {Ferramenta} → Claude

Data inicio:        2026-XX-XX
Data cancelamento:  2026-XX-XX
Custo ferramenta:   R$ X/mes
Economia mensal:    R$ Y
Quem manteim:       {nome}

## O que ficou diferente
{...}

## O que continuamos pagando
{ferramentas que NAO migraram nessa categoria, se houver}

## Risco identificado
{ex: se o Claude API der down, plano B e ...}

## Como reverter (caso precise)
1. Reativar conta {Ferramenta} (link)
2. Importar backup de dados
3. ...
```

Esse arquivo e ouro se daqui a 6 meses voce precisar reverter ou justificar.

---

## Sinais de que algo deu errado

| Sintoma | Acao |
|---|---|
| Time reclama que e "mais demorado" | Re-treina + automatiza partes repetitivas |
| Output do Claude parece pior que da ferramenta | Reaprimora prompt; talvez seja caso de manter SaaS |
| Cliente reclama de qualidade ou demora | Reverte ja, depois investiga |
| Voce gasta mais tempo mantendo prompt do que ganha | Talvez nao valia migrar mesmo |

Migrar nao e "ter coragem de cortar". E **fazer a troca quando o ROI justifica**. Se nao justifica, fica com SaaS.

---

## Cronograma resumido

```
Dia 0      Decisao + backup
Dia 1-3    Setup novo fluxo
Dia 4-10   Operacao paralela + comparativo
Dia 11     Avaliacao de criterios pra cancelamento
Dia 12-14  Cancelamento + documentacao
```

14 dias pra trocar com seguranca.

Pode rodar **uma categoria de cada vez**. Em 70 dias, voce migrou as 5 categorias e cortou R$ 1k-4k/mes.

Boa migracao.
