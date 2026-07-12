# agencia: orçamento MULTIUSO (item Serviço) + PDF deck visual + link Stripe opt-in

**Sessão:** 2026-07-02 · Aprovado pelo Pedro ("pra v1 ficou ótimo"). Main + deploy.

## O que entrou
1. **Item 'servico' no orçamento** (p36a/b): enum + colunas em quote_items
   (service_id → cadastro Serviços, qty, unit_cents), trigger de subtotal,
   quote_pdf_data com servico_items + photo_url da placa. O cadastro Serviços
   (antes órfão) virou a fonte: site, vídeo, gestão, indoor mensal, adesivo,
   banner (5 seeds novos; preços default a definir pelo Pedro).
   **p36c**: compute_quote_totals somava só outdoor/gráfica/manual — corrigido
   pra incluir 'servico' (bug pego no teste e2e em prod).
2. **PDF do orçamento reescrito como deck** (benchmark Alternativa #A2197,
   avaliado): capa com cliente/condições/sumário por seção/total black-accent;
   card de outdoor com FOTO real da placa + QR de localização (lib `qrcode`,
   offline) + link Maps + dimensões + período com datas de bi-semana + breakdown
   locação/instalação; gráfica/serviços com miniatura (image_url + upload nos
   cadastros). Assets preparados antes do render (src/pdf/quote-pdf-assets.ts).
3. **Link de pagamento (Stripe) opt-in**: quotes.payment_link_url + _incluir;
   campo no bloco Condições; PDF ganha bloco "Pagar com cartão" com QR quando
   marcado. MANUAL por ora — o Core já tem capability stripe; integração em
   etapas (gancho: botão "gerar link" → risenCore.call).

## Teste e2e (feito e LIMPO de prod)
Quote 4 itens (PIR-001 2 bis + papel + Site R$4.500 + IG 3×R$2.000) → trigger ok,
total R$ 11.630,00 ✓ → approve financeiro → 3 receivables exatas ✓ → apagado.
PDF de amostra validado visualmente e mandado no chat.

## Pendências/ganchos
- Preços default dos serviços novos (Pedro define no cadastro).
- Stripe via Core (etapa futura) · recorrência/contrato · inventário indoor.
- _create_receivables_from_quote ainda marca source 'outdoor' pra tudo (débito).
- Fotos/geo faltam em EUC-001/002 e PIR-025 (cards degradam sem foto).
