# Primeiro dia

Roteiro objetivo pro seu primeiro dia rodando o sistema. Demora **2-3 horas** se voce tem os dados na mao. Pode parecer chato, mas e o ultimo dia em que voce vai gastar tempo "alimentando sistema" — depois disso, sao 5 minutos por dia.

## Princípio

Voce nao precisa cadastrar **tudo** o que existe na sua empresa. Cadastre **o que esta vivo agora**:

- Produtos com estoque > 0
- Clientes que compraram nos ultimos 90 dias
- Fornecedores que voce usou no ultimo trimestre
- Funcionarios ativos
- Projetos em andamento
- Tarefas dos proximos 30 dias
- Contas a pagar/receber em aberto

O resto fica pra cadastrar **se** virar relevante. Nao tente importar 10 anos de planilha.

## Bloco 1 — Saldo financeiro inicial (15 min)

Sem isso, todo o resto fica capenga.

> Quero registrar o saldo inicial do meu caixa. Hoje (data de hoje) eu tenho R$ X em conta corrente. Quero que isso entre como saldo de abertura.

> Tenho contas a pagar em aberto: lista as contas com data de vencimento, fornecedor, descricao, valor.

> Tenho contas a receber em aberto: lista clientes, descricao, valor, vencimento.

**Saida esperada:** caixa.csv com 1 linha (saldo abertura), contas-a-pagar e contas-a-receber populadas.

## Bloco 2 — Estoque atual (30-60 min)

Pega seu inventario atual fisico OU sua planilha mais recente. Se nao tem inventario, faz uma contagem rapida agora — produtos vendaveis, em ordem do que vende mais.

> Vou cadastrar produtos. Pra cada um, vou te passar SKU, nome, custo unitario, preco de venda, estoque atual e estoque minimo.

Cadastre **20-50 produtos** que representam ~80% do faturamento (curva ABC). O resto pode entrar na semana 2.

## Bloco 3 — Clientes ativos (30 min)

Pegue clientes que compraram nos **ultimos 90 dias**. Se voce nao tem registro, cadastre os 20-30 que voce mais lembra.

> Vou cadastrar meus clientes ativos. Pra cada um: nome, email, telefone, origem (instagram, indicacao, etc.) e status (ativo/lead/etc.).

## Bloco 4 — Funcionarios (15 min, se aplicavel)

> Cadastra funcionarios ativos: nome, cargo, salario base, data de admissao, carga horaria diaria.

## Bloco 5 — Tarefas + projetos do dia (15 min)

Pega o que voce tem em mente pra essa semana e proximas 2.

> Vou listar tarefas pra cadastrar. Pra cada uma: titulo, responsavel, prazo, prioridade.

Se voce tem projetos com cliente em andamento:

> Cadastra projeto: nome, cliente, responsavel, data de inicio, prazo final, valor.

## Bloco 6 — Confirmacao e backup (5 min)

> dashboard

Olha os numeros. Bate com o que voce tem na cabeca? Se nao bate, ajusta agora.

```bash
git add .
git commit -m "primeiro dia — dados iniciais"
git push  # se voce ja tem remoto
```

## Como continuar (rotina)

A partir de amanha, sua rotina vai ser:

### Diario (5 min)
- Registrar entradas e saidas do dia: `vendi 3 X`, `paguei R$ Y de Z`, `recebi R$ W do cliente J`
- Olhar `dashboard` antes de fechar o expediente
- `git commit` no fim do dia

### Semanal (20 min — escolha um dia fixo, ex: sexta de manha)
- Conferir saldo bancario fisico vs. caixa.csv (ajusta se precisar)
- Olhar contas que vencem na proxima semana
- Olhar follow-ups pendentes de cliente
- Olhar tarefas atrasadas
- Olhar produtos abaixo do minimo

### Mensal (45 min — primeiro dia util do mes)
- `gera relatorio do mes anterior`
- Le o relatorio gerado, anota 3 conclusoes
- Compara com mes anterior — o que mudou e por que?
- Define 3 acoes pro mes que comeca

## Erros comuns no primeiro dia

| Erro | O que acontece | Como evitar |
|---|---|---|
| Cadastrar produto demais | Cansa, voce desiste | Comeca com top 20 que vendem mais |
| Importar planilha antiga inteira | Dado podre vira erro depois | So o que esta vivo nos ultimos 90 dias |
| Esquecer saldo de abertura do caixa | Saldo do mes vira fantasia | Sempre comeca com saldo inicial |
| Nao versionar com Git | Erro humano apaga dado | `git init` no passo 1, sempre |
| Cadastrar e nunca usar | Sistema vira museu | Forca-se a rodar `dashboard` 1x por dia na semana 1 |

## Proximo passo

[`NEGOCIO-EXEMPLO.md`](NEGOCIO-EXEMPLO.md) — leia uma vez. Voce vai ver uma loja ficticia rodando 3 meses inteiros com isso, das primeiras vendas ao primeiro fechamento mensal. Vale o tempo de leitura.
