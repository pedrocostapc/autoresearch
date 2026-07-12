# Calculadora de ROI — vale migrar?

Tempo: 5 minutos. Faca **antes** de migrar. Se nao passar nos criterios, **nao migra essa categoria** e foca em outra.

## Passo 1 — Custo atual da ferramenta

Anota tudo que voce paga **hoje** para essa categoria especifica:

```
Ferramenta atual: ____________________
Plano: ______________________
Numero de seats/usuarios: _______
Custo mensal (R$): _______
Custo anual (R$): _______ (geralmente plano anual da 15-20% desconto)
Outras ferramentas relacionadas (add-on, integracao paga): _______
TOTAL MENSAL: R$ _______
```

## Passo 2 — Volume atual

Quantas operacoes voce faz por mes na ferramenta?

```
Categoria: __________
Operacoes/mes: _______ (vendas geradas, automacoes rodadas, dashboards consultados, mensagens respondidas, documentos emitidos)
Tempo medio por operacao: _______ min
Tempo total/mes: _______ horas
```

## Passo 3 — Custo do Claude (estimado pro seu volume)

### Categoria 01 — Copywriting
- ate 100 textos/mes: Claude Pro (R$ 110/mes)
- 100-500: Claude Pro + uso eventual API (R$ 150/mes)
- 500-2000: Claude Pro + API moderada (R$ 250/mes)
- 2000+: API direta (R$ 400+/mes)

### Categoria 02 — Automacao
- ate 1000 execucoes/mes simples: Claude Pro + cron local (R$ 110/mes)
- 1000-10000: Claude Code + scripts otimizados (R$ 150/mes)
- 10000+: API com batching (R$ 300+/mes)

### Categoria 03 — Analise de dados
- consultas eventuais: Claude Pro (R$ 110/mes)
- dashboards diarios automatizados: Pro + scripts (R$ 150/mes)

### Categoria 04 — Atendimento
- ate 500 atendimentos/mes: Pro + integracao manual (R$ 110/mes)
- 500-3000: API integrada com webhook (R$ 200-400/mes)
- 3000+: depende — pode nao ser viavel migrar 100%

### Categoria 05 — Documentos
- ate 50 documentos/mes: Claude Pro (R$ 110/mes)
- 50-200: Pro + scripts (R$ 130/mes)
- 200+: API + template (R$ 200/mes)

## Passo 4 — Calcule

```
Economia mensal = custo atual ferramenta - custo Claude estimado

Se voce nao usa Claude pra mais nada hoje, considere o custo total dele.
Se voce ja paga Claude Pro pra outras coisas, o custo marginal e o adicional de uso (uso da API).
```

**Exemplo real (loja Camisa BR):**

```
Antes:
- Jasper (copy): R$ 280/mes
- Zapier Pro (automacao): R$ 150/mes
- Power BI Pro (dados): R$ 70/mes (1 seat)
- Manychat (atendimento): R$ 95/mes
- TOTAL: R$ 595/mes = R$ 7.140/ano

Depois (Claude Pro + uso ocasional API):
- R$ 180/mes total = R$ 2.160/ano

Economia liquida: R$ 415/mes = R$ 4.980/ano
```

## Passo 5 — Os 4 criterios pra migrar

Pra cada categoria, **so migre se passar nos 4**:

### Criterio 1 — Economia minima
Economia liquida mensal **>= R$ 200**.

Se for menos, o tempo que voce gasta migrando + manutencao nao paga. Mantenha a ferramenta.

### Criterio 2 — Volume cabe no Claude
Cheque a tabela do Passo 3 — voce esta dentro do volume que o Claude resolve sem dor?

Sim → segue.
Nao (volume gigante) → fica com SaaS especializado.

### Criterio 3 — Voce ou alguem do time consegue manter
Realista: voce ou alguem do time vai precisar:
- Manter prompt atualizado
- Mexer em script quando algo quebrar
- Ajustar base de conhecimento quando o produto/servico mudar

Sem isso, a migracao desmancha em 3 meses.

### Criterio 4 — Operacao tolera o periodo de transicao
Voce vai rodar em paralelo por 7-14 dias. **Voce tem tempo pra isso?**

Se voce esta em pico de operacao (campanha, lancamento, fim de ano), espera. Migra na temporada baixa.

## Resultado

Marca os criterios:

- [ ] Economia >= R$ 200/mes
- [ ] Volume cabe no Claude
- [ ] Eu ou alguem mantem
- [ ] Operacao tolera transicao

**4 marcados:** migra essa categoria, comeca pelo prompt correspondente.

**3 marcados:** revisa qual falhou. Se for o (4), apenas espera. Se for (1) ou (2), nao migra.

**2 ou menos:** nao migra essa categoria. Foca em outra que da retorno.

## Decisao tomada — proximo passo

Se decidiu migrar:

1. Vai pro `CHECKLIST-MIGRACAO.md` antes de comecar
2. Abra o prompt da categoria escolhida
3. Marca um prazo de 14 dias pra finalizar a transicao com seguranca

Se decidiu NAO migrar essa categoria:

- Otimo. Voce economizou tempo de tentativa.
- Talvez compense reduzir o plano da ferramenta atual (downgrade)
- Avalia outra categoria
