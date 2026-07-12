# agencia: 30 placas de outdoor com geo + foto oficial (extraídas dos QRs)

**Sessão:** 2026-07-02 · Sem mudança de código — só DADOS em prod (autorizado pelo Pedro).

## O que foi feito
- Fonte: `Dropbox/.../Outdoor/Fotos Prontas/*.png` (33 artes oficiais RSN, nomeadas
  pelo código da placa). Cada arte tem QR "LOCALIZAÇÃO" com link do Google Maps.
- QRs decodificados com Vision nativo do macOS (swift; script em scratchpad/qr/) —
  2 precisaram de crop+upscale; 2 eram shortlink goo.gl (resolvido via redirect).
- `placas.latitude/longitude`: **30/33 preenchidas** (faltam EUC-001, EUC-002,
  PIR-025 — não têm arte na pasta). Liga mapa/rota/copiar-coordenada do detalhe.
- Fotos: 30 PNGs no bucket `tenant-assets` + `placa_photos` (is_primary, com a
  coluna legada `url` preenchida — ela é NOT NULL e a galeria lê `p.url` direto).
- **Bucket `tenant-assets` virou PÚBLICO** (decisão do Pedro): todo o código de
  fotos usa getPublicUrl e o bucket só contém as artes de divulgação. Se um dia
  entrar material sensível, criar bucket privado separado.
- Órfãos de upload limpos via Storage API (deleção direta em storage.objects é bloqueada).

## Pendência
- EUC-001/002 e PIR-025 sem geo/foto (produzir as artes ou me passar link do Maps).
