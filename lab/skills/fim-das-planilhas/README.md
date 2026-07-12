# Fim das Planilhas

Pare de perder 10h/semana em planilha. Controle tudo com IA: organizacao, ZERO ERRO, velocidade real.

> Esse pacote nao e teoria. Sao **10 skills do Claude Code prontas pra rodar**, **9 templates CSV** com dados de exemplo, **1 guia de instalacao** que voce roda em 15 minutos, **1 dia 1 estruturado** pra voce comecar usando ja, e **1 exemplo completo** mostrando uma loja ficticia rodando 3 meses inteiros com essas skills.

## A dor que voce conhece

- Planilha que ninguem mais acha
- Formula que quebrou e ninguem sabe quando
- Versao "FINAL_V3_REVISADO_OK.xlsx" coexistindo com 4 outras
- Vendedor que esqueceu de baixar estoque
- Conta que voce so descobriu que estava vencendo no dia que voce entrou em juros
- Cliente que ja era seu e voce ofereceu como se fosse novo
- Demora pra responder "quanto vendi mes passado" (resposta: 40 minutos abrindo abas)

A planilha foi util quando voce comecou. Hoje, ela e o teto do seu negocio.

## A proposta

Em vez de planilha, voce conversa com o Claude. Ele:

- **Le** os arquivos CSV do seu negocio (tudo em uma pasta organizada)
- **Atualiza** quando voce avisa: "vendi 3 camisetas pretas P pro Joao por R$ 150, recebi no pix"
- **Calcula** sob demanda: saldo, comissao, fluxo de caixa, ranking de cliente
- **Alerta** sem voce pedir: estoque acabando, conta vencendo, cliente sumido ha 90 dias
- **Gera relatorio** quando voce manda: fechamento mensal completo em 1 mensagem

E os arquivos sao seus. CSV em pasta. Voce abre no Excel se quiser, versiona com Git, faz backup com 1 comando. **Nada esta refem de planilha.**

## O que esta dentro

```
skills-fim-das-planilhas/
├── README.md                       (esse arquivo)
├── INSTALACAO.md                   (15min do zero ao primeiro uso)
├── PRIMEIRO-DIA.md                 (roteiro do dia 1)
├── NEGOCIO-EXEMPLO.md              (loja ficticia rodando 3 meses)
├── skills/
│   ├── 01-controle-financeiro/SKILL.md
│   ├── 02-controle-estoque/SKILL.md
│   ├── 03-controle-vendas/SKILL.md
│   ├── 04-controle-clientes/SKILL.md
│   ├── 05-controle-fornecedores/SKILL.md
│   ├── 06-controle-tarefas/SKILL.md
│   ├── 07-controle-funcionarios/SKILL.md
│   ├── 08-controle-projetos/SKILL.md
│   ├── 09-relatorio-mensal/SKILL.md
│   └── 10-dashboard-rapido/SKILL.md
└── templates/                      (CSVs prontos com cabecalho + 2-3 linhas exemplo)
    ├── financeiro/
    ├── estoque/
    ├── vendas/
    ├── clientes/
    ├── fornecedores/
    ├── tarefas/
    ├── funcionarios/
    ├── projetos/
    └── dashboard.md
```

## Resumo das 10 skills

| # | Skill | O que entrega |
|---|---|---|
| 01 | controle-financeiro | Caixa, contas a pagar/receber, fluxo de caixa, vencimentos |
| 02 | controle-estoque | Saldo, alerta de minimo, valor em estoque, curva ABC |
| 03 | controle-vendas | Registro, comissoes, metas, top vendedor/produto/cliente |
| 04 | controle-clientes | CRM: cadastro, interacoes, follow-up, recencia, segmentacao |
| 05 | controle-fornecedores | Cadastro, historico, comparativo de preco, confiabilidade |
| 06 | controle-tarefas | Todo com prazo, prioridade, responsavel, lista do dia |
| 07 | controle-funcionarios | Ponto, banco de horas, ferias, calculo gerencial de salario |
| 08 | controle-projetos | Etapas, marcos, atraso, % conclusao, saude do portfolio |
| 09 | relatorio-mensal | Fechamento mensal automatico cruzando todas as outras skills |
| 10 | dashboard-rapido | Snapshot textual em 1 mensagem: saude do negocio em 5 segundos |

## Por onde comecar

1. **`INSTALACAO.md`** — 15 minutos, do clone ao primeiro `dashboard`
2. **`PRIMEIRO-DIA.md`** — roteiro do que registrar no dia 1 pra sair do zero
3. **`NEGOCIO-EXEMPLO.md`** — leia uma vez antes pra entender o ritmo

Depois e so usar. Skills sao acionaveis por linguagem natural. Voce nao precisa decorar nome de skill — fala o que quer e o Claude usa a skill certa.

## O que esse pacote NAO faz

- **Nao tem interface visual.** E texto + arquivos CSV. Se voce quer dashboard piscando, isso aqui nao e pra voce
- **Nao tem multi-usuario com permissao.** Mais de 1 pessoa pode usar com Git, mas conflito se 2 editarem ao mesmo tempo
- **Nao tem mobile app.** Roda onde Claude Code roda (Mac, Linux, Windows com WSL)
- **Nao emite NF-e nem cumpre obrigacao fiscal.** Isso ainda precisa de ERP/contador
- **Nao substitui banco.** E controle gerencial, nao conta corrente

Pra **gestao operacional do dia a dia** de uma empresa de 1 a ~30 pessoas, com volume baixo a medio, isso aqui acaba com 80-90% das suas planilhas.

---

**ASV Digital** — produtos@asv.digital
