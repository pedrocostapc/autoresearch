# Revisão 100% do histórico de conversas — Betel Barber Shop (juniobetel)

**Sessão:** risen-ai-connect, 2026-06-12 ~14:50 BRT
**O quê:** leitura completa das 401 conversas / 6.623 msgs do tenant Betel
(01/05→12/06), mesmo método da leitura Risen Mídia de 08/06. 11 revisores
paralelos, síntese em `risen-ai-connect/prompts/betel-review/2026-06-12-revisao-historico-conversas.md`
(+ cópia em `risencrm/prompts/betel-review/`).

## Pra quem mexe no produto (bugs achados em prod)
1. **Respostas duplicadas/triplicadas da IA**: ~25 ocorrências em ~20 conversas,
   em TODOS os lotes. Race condition quando o cliente manda msgs fragmentadas.
   Bug nº 1 de produto — precisa debounce/dedup no ai-reply.
2. **Template "vou te conectar + wa.me" alucina números**: 7+ números fake e um
   `wa.me/[número do Melqui]` literal enviado ao cliente. Matar/sanitizar o template.
3. IA **se passou pela atendente humana em chat interno** respondendo ao sócio;
   atravessa atendimento humano; responde contexto de dias atrás como atual.
   → supressão por lista interna + humano-ativo + anti-stale.
4. **Persona dupla** "Risen"→"Betinho" no mesmo número (trocou ~25/05).
5. Broadcasts CashBarber entram como sender=agent (HUMANO): 31% das conversas
   são só lembrete, poluem métricas e o contexto da IA.
6. Possível bug de fuso em respostas com horário (IA falou "fechamos às 20h"
   em msg 22:27).

## Pro comercial/CS
- Saldo do Betel em 12/06: **R$ 1,17** — 3º apagão de IA iminente (2 semanas
  inteiras sem IA por crédito zero em maio/junho).
- ~12 itens de Caixa prontos extraídos do histórico (preços, horários reais,
  escala por barbeiro, PIX, endereço, regra no-show, roteiro da migração
  CashBarber→AppBarber) — seção 5 do relatório.
- Vendas perdidas documentadas por latência humana (1h–38h) + IA muda.

## Conexões
- Alimenta direto o redesign do Revisor por lacuna + Butler (gatilho
  lacuna→tarefa→Caixa) e o Task Manager v2 (handoff "equipe te retorna"
  sem tarefa rastreável = ≥8 promessas no vácuo).
- 2º tenant da amostra de betas com leitura 100% (1º: Risen Mídia 08/06).
