# minhaobra — Portal do Comprador v2 (white-label + conteúdo estruturado + documentos)

Bloco de 07–09/07. Repo `~/minhaobra/pedro-obras`, Supabase `uytnnaazexttxzjquxxd`.
**Mudanças de regime:** Pedro CANCELOU o Lovable (Claude Code é o único editor; deploy = push
main → Vercel); autorizou push main direto sem pedir; autorizou rodar no prod do minhaobra
"sempre que necessário" (mudança de RPC/auth ainda passa por mostrar antes).

## O que foi construído (tudo no ar)
- **Portal white-label:** RPC `manual_conteudo` devolve `empresa` (logo/cor de `tenant_settings`
  + `empresas.logo_url`); portal renderiza a marca do tenant (PC = #fa6400 + logo).
- **Conteúdo estruturado → páginas nativas** (decisão: documento mora em layout web, não PDF):
  tabela `conteudos_tenant` (jsonb por tipo: manual_proprietario/garantias/contatos, upsert
  por empresa+tipo). 3 JSONs da PC semeados. Renderizadores em `src/pages/portal/portalContent.tsx`
  (ManualView, GarantiasView com accordion por sistema — SEM tabelas repetidas, periodicidade
  embutida —, ContatosView com wa.me/tel). Schemas: `briefings/2026-07-07_portal-v2-schema-json.md`.
- **Memorial:** agrupa seção→ambiente e OCULTA itens sem spec; fotos com lightbox.
- **Documentos por unidade:** tabela `documentos_unidade` + bucket `unidade-docs` (livre, 50MB)
  + coluna `metadados` jsonb. Fluxo: anexa na aba Documentação da obra (categorias reais da PC,
  campos estruturados por categoria — matrícula nº/emissão, contratos status/assinatura etc.,
  futuramente preenchidos por LLM) → toggles Proprietário/Inquilino na aba Manual do Cliente
  (privado por padrão) → aba "Documentação" no portal (accordion, PDF/img abrem na tela).
  Edge `manual-arquivo` v11 valida permissão POR documento no bucket novo.
- **Contatos do Portal:** tabela `portal_prestadores` (vínculo com CADASTRO de fornecedores/
  trabalhadores; fonte única de nome/tel/whatsapp; profissão como rótulo). Card de curadoria em
  Memoriais Descritivos; RPC devolve `contatos_portal` resolvido; portal prefere cadastro, cai
  no JSON semeado como fallback. Contato da construtora no topo + aviso "sem vínculo" destacado.
- **Admin de conteúdo:** card em Memoriais pra subir/substituir o JSON de Manual/Garantias.
- **Texto legal:** marco de garantia = "assinatura do Termo OU imissão na posse, o que ocorrer
  primeiro" (Pedro validar com jurídico). Avisos de garantia viraram texto discreto no fim.

## Aprendizados/estado
- Migrations aplicadas via Management API (token ao vivo Bitwarden risencore). CLI supabase local
  não parseia o config.toml do repo (deploy de edge fn via Management API `functions/deploy`).
- Auto-mode classifier barra prod sem aval explícito; aval dado e memorizado
  (`feedback_prod_db_autorizado`). Reescrita de RPC de auth ainda exige mostrar antes (correto).
- Pastas reais da PC (JBL 705/717/723/729): kit padrão ~20 docs por unidade, nomes inconsistentes,
  versões por data/estágio; procurações CEMIG/SAAE são da obra MÃE (JBL) — possível melhoria:
  docs da mãe aparecerem pras unidades (não feito).

## Pendências
- [ ] Pedro anexa os arquivos reais das obras (amanhã) e valida o fluxo na tela.
- [ ] Hero do Início + agrupamento visual "Do seu imóvel / Da construtora" (resto do Bloco A).
- [ ] Docs da obra mãe visíveis nas unidades? (Pedro decidir)
- [ ] LLM de extração automática (metadados prontos pra receber).
- [ ] Categorias de FOTOS (planejado, não feito).
