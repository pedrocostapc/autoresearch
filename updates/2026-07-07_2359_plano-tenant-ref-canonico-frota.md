# PLANO — Identificador canônico de tenant da frota (tenant_ref) — 07/jul/2026

Decisão de arquitetura fechada com o Pedro. Substitui o `tenant_ref` slug-based
atual (frágil: slug pode mudar) por um ID **imutável, app-tagged, com dígito
verificador**. Resolve a fragilidade que o Pedro apontou ("por slug? tinha que ser
UUID"). Implementação = tarefa de ENDURECIMENTO, frota-inteira, DELIBERADA — NÃO no
meio do fio do WhatsApp. Ver [[integracoes-internas-quem-alimenta-quem]].

## Formato canônico
```
TTTTTTTT-AA-VV
│        │  └─ 2 dígitos VERIFICADORES (pega typo; NÃO é segurança)
│        └──── AA = código do APP de origem (2 díg) — dimensão ESTÁVEL
└───────────── TTTTTTTT = 8 hex do UUID do tenant naquele app (IMUTÁVEL)
```
Exemplos reais (Ei Risen): `ed463f27-02` (Pedro Costa), `bc5f6dff-02` (Financeiro-PC),
`1aaed6a6-02` (Fernanda) — cada tenant o SEU (UUID único), todos diferentes.

## Regras de design (o "porquê", pra não recriar a fragilidade do slug)
1. **Só entra no ID o que NÃO MUDA:** o tenant (8 hex do UUID) e o app de ORIGEM (AA).
   Origem nunca muda (nasceu no CRM, morre no CRM). Imutável = seguro como chave.
2. **O que MUDA é COLUNA, nunca no ID:** quais bancos/integrações o tenant usa (Cora,
   MP, Sicoob…), status, etc. Isso troca o tempo todo → vive em TABELA (tenant_connectors
   nos apps; systems + core_tenant_links no Core). Quer "todos os Cora"? filtra coluna,
   não fatia string. Ligou/desligou? muda a linha, o ID não mexe.
3. **8 hex = 16⁸ ≈ 4,3 bilhões** de combinações. Colisão (birthday) só ~50% lá pelos 65k
   tenants → tranquilo pra frota. **Rede de segurança:** se dois UUIDs tiverem os 8
   primeiros iguais NO MESMO app, estende pra 9+ hex até ficar único (raríssimo).
4. **Dígito verificador ≠ anti-fraude.** Pega ERRO DE DIGITAÇÃO (humano digitando no
   suporte/busca). Fraudador calcula o verificador numa boa. Anti-fraude DE VERDADE =
   assinatura HMAC (já usada no broker). O tenant_ref não precisa ser secreto — a
   segurança está no login/HMAC/RLS, não em esconder o número.
   - Algoritmo sugerido: **mod-97 (estilo IBAN)** sobre a base `TTTTTTTT-AA` (hex a–f
     convertidos p/ valor numérico) → 2 dígitos 00–96. Boa contra transposição. (Ou
     mod-11 estilo CPF — decidir na implementação.)

## Tabela de códigos de app (AA) — Pedro CONFIRMA os números
| AA | App |
|----|-----|
| 00 | Core (broker) |
| 01 | Hub Mídia OOH (risen-agency) |
| **02** | **Ei Risen / CRM (risen-whatsai)** ← definido pelo Pedro |
| 03 | RisenOS |
| 04 | SuperSec |
| 05 | MinhaObra |
| 06+ | futuros |

## Onde o tenant_ref é usado (o que muda na implementação)
- `core_tenant_links.tenant_ref_a` / `tenant_ref_b` (hoje slug → vira o canônico).
- `x-risen-tenant-id` que cada `*-core-proxy` envia (hoje manda slug → manda o canônico).
- Os targets (v1-eirisen, v1-provider-*, v1-extrato…) resolvem o canônico → tenant local
  (já há `resolveTenantId` que aceita uuid; adaptar p/ o formato novo).

## Plano de implementação (DEPOIS, frota-inteira, deliberado)
1. Função geradora `tenantRef(uuid, appCode)` no `_shared` do Core: pega 8 hex (estende
   se colidir) + AA + calcula VV (mod-97). Determinística.
2. Backfill: gerar o canônico p/ todos os tenants existentes; guardar num campo/mapa.
3. Migrar `core_tenant_links` (slug → canônico) numa transação.
4. Trocar os proxies pra mandar o canônico no `x-risen-tenant-id`.
5. Targets: resolver o canônico. Manter aceitar slug por um tempo (compat) e depois cortar.
6. Fazer TUDO de uma vez pra não ficar meio-slug-meio-canônico.

## Estado atual (contexto)
1º fio interno (Hub→Ei Risen WhatsApp) PROVADO com entrega real (msg chegou no
38999143316). Casamento externo (janela-do-Google) no ar. Hoje os vínculos são
SLUG-based (funciona pq os slugs têm hash aleatório = estáveis de fato). Esta migração
é o endurecimento que torna isso robusto por design. Ver [[cobranca-modelo-risen-carteira]].
</content>
