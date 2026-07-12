# Negocio exemplo — Loja "Camisa BR"

> Ler isso uma vez antes de comecar economiza 10 dias de tropeco. Voce vai ver como uma operacao real flui no sistema.

## A loja

**Camisa BR** — loja online de camisetas tematicas (cidades brasileiras).

- Donos: Marcelo (operacao) e Ana (financeiro)
- Funcionarios: 2 vendedoras (Maria, Joana) + 1 designer (Pedro)
- Produtos: ~30 SKUs ativos
- Faturamento: ~R$ 35-50k/mes
- Vendas: ~70% online (site proprio), 30% atacado pra revendedores

Antes do sistema, o Marcelo gastava **6h aos sabados** atualizando 4 planilhas. Agora gasta **20 minutos** durante a semana toda + 30 minutos no fechamento mensal.

---

## Mes 1 — Os primeiros 30 dias

### Dia 1 — Setup

Marcelo seguiu o `PRIMEIRO-DIA.md`. Cadastrou:

- Saldo inicial em conta: R$ 18.500
- 28 produtos ativos (top 20 + 8 que ainda tinham estoque)
- 47 clientes que compraram nos ultimos 90 dias
- 3 fornecedores
- 3 funcionarios + ele e Ana
- 4 contas a pagar em aberto (R$ 4.200)
- 2 projetos: campanha "Junina" e troca da fotografia do site

Tempo total: 2h45.

### Dia 2 — Primeira venda registrada

Maria (vendedora) vendeu 3 camisetas pra um cliente novo. Marcelo conversou com Claude:

> Maria vendeu 3 camisetas Recife G pra um cliente novo: Carla Mendes, carla@email.com, 11 98888-1234. R$ 49,90 cada, recebeu no pix.

Claude:
1. Cadastrou Carla como cliente novo (C048)
2. Registrou venda V0001 — 3 unidades de SKU REC-G — R$ 149,70 — vendedor Maria — pago via pix
3. Baixou 3 unidades do estoque (de 22 para 19)
4. Adicionou entrada no caixa.csv: +R$ 149,70
5. Avisou: "Estoque de Recife G ficou em 19 unidades, ainda esta acima do minimo de 5."

Marcelo: ok. Proxima venda.

### Dia 7 — Conta vencendo

Marcelo abre Claude segunda de manha:

> dashboard

Claude responde com painel completo. Destaque vermelho:

```
🚨 ALERTAS
  - Conta a pagar vence amanha: Fornecedor TecidoCo — R$ 1.800
  - 2 produtos abaixo do minimo: Floripa M (3/10), Salvador G (4/10)
```

Marcelo paga a conta na hora. Volta no Claude:

> Paguei a conta da TecidoCo agora, R$ 1.800 do meu pix.

Claude marca como paga + registra saida no caixa.

### Dia 14 — Cliente sumindo

Marcelo, sexta de manha:

> Quem nao compra ha mais de 60 dias?

Claude lista 8 clientes. Marcelo escolhe 3 e manda WhatsApp manual oferecendo desconto no proximo pedido. 1 deles compra na quarta seguinte. **R$ 280 que ele nao teria sem o relatorio.**

### Dia 30 — Primeiro fechamento mensal

Marcelo, dia 1 do mes seguinte:

> Fecha o mes anterior

Claude gera `relatorios/relatorio-2026-01.md`:

```markdown
# Relatorio mensal — Janeiro/2026

## 1. Resumo financeiro
- Entradas no caixa: R$ 38.420,50
- Saidas no caixa: R$ 24.180,30
- Resultado: R$ 14.240,20
- Comparativo com dezembro: nao ha (primeiro mes no sistema)

## 2. Vendas
- Faturamento total (vendas pagas): R$ 38.420,50
- Numero de vendas: 142
- Ticket medio: R$ 270,57

## 3. Top 5 vendedores (por valor)
| # | Vendedor | Vendas | Valor    | % da meta |
| 1 | Maria    | 78     | R$ 21.3k | 178%      |
| 2 | Joana    | 51     | R$ 13.7k | 137%      |
| 3 | Marcelo  | 13     | R$ 3.4k  | -         |

## 4. Top 5 produtos
1. Recife G — 38 un — R$ 1.896
2. Floripa M — 28 un — R$ 1.397
3. Salvador G — 21 un — R$ 1.048
4. Sao Paulo P — 19 un — R$ 948
5. Rio de Janeiro M — 17 un — R$ 848

## 5. Top 5 clientes
1. Loja Estilo SP — R$ 4.200 (3 compras)
2. Carla Mendes — R$ 1.498 (5 compras)
3. ...

## 6. Contas em aberto
- A pagar: R$ 6.380 (3 contas)
- A receber: R$ 2.100 (2 contas)

## 7. Estoque
- Produtos abaixo do minimo: 4
- Valor total em estoque: R$ 18.700

## 8. Clientes
- Novos clientes no mes: 23
- Clientes ativos: 89
- Inativos (90+ dias): 12

## 9. Pontos de atencao
1. Maria bateu 178% da meta. Recalcular meta pra fevereiro
2. Recife G vendeu 38 un — comprar mais antes que falte
3. Sao Paulo P teve venda baixa (19 un) vs. expectativa — investigar (foto? preco?)
4. R$ 2.100 a receber atrasou — cobrar Loja Estilo SP
```

Marcelo le o relatorio em 5 minutos. Decisoes do mes:
- Recalcula meta da Maria pra R$ 18k (era R$ 12k)
- Liga pra Loja Estilo SP cobrando os R$ 2.100
- Pede mais Recife G pro fornecedor
- Investiga Sao Paulo P (descobre que foto estava ruim — pede pra Pedro refazer)

**Tempo gasto no fechamento: 30 minutos.** Antes era 4 horas no Excel.

---

## Mes 2 — Sistema rodando

### Padrao do dia a dia

**Marcelo, segunda 9h:**
> dashboard

**Maria, durante o dia, no celular dela com Claude.ai:**
> Vendi 2 camisetas Recife G pra cliente Carla Mendes (ja existe), R$ 99,80 no pix.

**Marcelo, sexta 17h:**
> Quem precisa de follow-up essa semana?
> Tem alguma conta vencendo na proxima?
> Quem ta abaixo da meta esse mes?

**Ana (financeiro), domingo 20h:**
> Conferi extrato do Itau, bate com caixa.csv? (Claude le ambos e responde)

### Coisa nova: producao de campanha

Marcelo cria projeto:

> Cria projeto "Campanha Dia das Maes": cliente interno, responsavel Pedro, inicio hoje, prazo 25/04, valor estimado R$ 8.000 (custo de producao).
> Etapas: pesquisa de tema (Pedro, 5 dias), arte (Pedro, 7 dias), producao (Marcelo, 10 dias), lancamento (Maria, 3 dias).

Toda semana, Marcelo pergunta:

> Como ta a Campanha Dia das Maes?

Claude responde com % de conclusao + atrasos + proxima etapa.

---

## Mes 3 — Decisoes baseadas em dado

Marcelo, no dia 1 de marco:

> Compara fevereiro com janeiro. Faturamento, ticket medio, top produtos. O que mudou?

Claude:

```
Comparativo Fev x Jan/2026:

Faturamento: R$ 38.420 → R$ 42.180 (+9.8%)
Numero de vendas: 142 → 158 (+11.3%)
Ticket medio: R$ 270 → R$ 267 (-1.1%)

Top 5 produtos:
- Recife G: 1o → 1o (38 → 45 un)
- Floripa M: 2o → 3o (28 → 22 un, queda de 21%)
- Salvador G: 3o → 2o (21 → 31 un, alta de 47%)
- NEW: BH M entrou em 4o (lancamento de 12/02)
- Sao Paulo P: caiu de 4o pra 7o (19 → 11 un)

Pontos relevantes:
1. Salvador G crescimento forte: provavel impacto de campanha de afiliado
2. Floripa M caiu — checa se faltou estoque (sim, ficou abaixo do min de 17 a 25 de fev)
3. Sao Paulo P continua caindo apesar de foto nova — repensar produto
4. Ticket medio caiu 1% — sem alarme, dentro de margem
```

Marcelo decide:
- Aumenta estoque minimo de Floripa M (10 → 25)
- Tira Sao Paulo P do site, vira saldao
- Pede pra Pedro fazer mais 3 designs como o de Salvador (que cresceu)

Decisao baseada em **5 minutos de leitura**, nao em achismo.

---

## O ganho real (medido)

| Metrica | Antes (planilha) | Depois (Claude) |
|---|---|---|
| Tempo cadastrando dado/dia | 1h | 5 min |
| Tempo no fechamento mensal | 4h | 30 min |
| Erros de calculo/mes | 5-8 (autocorrecoes em planilha) | 0 |
| Esquecimentos de conta | 1-2/mes (R$ ~150 em juros) | 0 |
| Cliente perdido por falta de follow-up | "uns tantos" | -90% |
| Tempo pra responder "quanto vendi de X esse mes?" | 30-40 min | 10s |
| Decisao baseada em dado real | mensal, parcial | semanal, completa |

**Tempo recuperado: ~10h/semana.** Marcelo usa essas 10h pra prospec novo revendedor + criar 2 produtos novos por mes.

---

## Coisas que nao saem como o planejado (e como tratar)

### "O Claude gravou venda errada"
Voce digitou errado e Claude registrou. Solucao: `git diff` mostra o que mudou. Voce pede:

> Cancela a venda V0042, foi registrada errada — era 2 unidades, nao 3.

Ou voce mesmo edita o CSV e confere com `git diff`.

### "Joana usou o nome errado do cliente"
Claude criou cliente novo "Carla M." quando ja existia "Carla Mendes". Solucao:

> Tem dois cadastros pra Carla? Funde eles, mantem o C048.

Claude faz a fusao de cadastro + atualiza historico.

### "Esqueci de registrar 1 semana"
Aconteceu. Voce volta:

> Tenho que registrar vendas dos dias 12 a 19 de marco que esqueci. Vou te passar uma de cada vez.

### "Acumulei 100 vendas pra registrar"
Use modo lote:

> Vou colar uma lista de vendas. Cada linha tem data, cliente, produto, qtd, valor, forma. Cadastra todas e me avisa de duplicatas.

---

## Voce nao precisa fazer tudo

Comece com **financeiro + vendas + estoque**. Adiciona clientes e tarefas na semana 2. Funcionarios e projetos so se for relevante pro seu caso.

A meta do mes 1 nao e usar 100% das skills. E **nunca mais abrir uma planilha pra coisa que essas 3 skills fazem**.

---

Pronto. Agora vai pra `INSTALACAO.md` e roda.
