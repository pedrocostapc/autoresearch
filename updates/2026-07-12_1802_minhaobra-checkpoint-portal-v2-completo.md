# minhaobra — CHECKPOINT retomável (Portal do Comprador v2 COMPLETO)

**Sessão:** minhaobra (Claude Code local). **Escrito para uma sessão que nasce SEM memória.**
Complementa `2026-07-09_1530_minhaobra-portal-comprador-v2.md` (leia os dois).
Não participo da esteira/SuperSec — nada meu no COORDENACAO-ESTEIRA.md.

## ONDE ESTÁ CADA COISA
- **Repo:** `/Users/pedrocosta/minhaobra/pedro-obras` (github `pedrocostapc/pedro-obras`, branch main).
  Deploy = `git push origin main` → Vercel (domínio minhaobra.app). **Lovable CANCELADO** — Claude Code é o único editor. Push direto autorizado, sem pedir.
- **Supabase prod:** ref `uytnnaazexttxzjquxxd`. Pedro autorizou rodar no prod "sempre que necessário"
  via Management API: token `SUPABASE_ACCESS_TOKEN` no Bitwarden vault **risencore**
  (`bws secret list 64c6f019-35c9-45ac-b189-b4660040eff3`, token bws no Keychain `bws-access-token`).
  Service role do minhaobra: vault `supabase-minhaobra` (403c8ddf-...). Endpoint:
  `POST https://api.supabase.com/v1/projects/<ref>/database/query`. Edge deploy: `.../functions/deploy?slug=<fn>` (CLI local não parseia o config.toml — usar API).
  REGra: RPC sempre partir do corpo vivo (`pg_get_functiondef`); mudança de RPC/auth mostrar antes.
- **Briefings no repo:** `briefings/2026-07-07_1415_portal-comprador-v2-raio-x.md` (arquitetura) e
  `briefings/2026-07-07_portal-v2-schema-json.md` (schemas dos JSON).
- **PC Construtora:** empresa_id `007e8157-3eea-457b-af13-7b5cbbe36e84`, tenant_code `pc-construtora`.

## O QUE ESTÁ NO AR (tudo aplicado em prod, último commit `b5166ab` + working tree limpo neste checkpoint)
1. **Portal white-label**: RPC `manual_conteudo` devolve `empresa` (logo/cor de tenant_settings) — portal usa a marca do tenant.
2. **Conteúdo estruturado como páginas**: `conteudos_tenant` (manual_proprietario/garantias/contatos em jsonb; 3 JSONs da PC semeados). Renderizadores: `src/pages/portal/portalContent.tsx`. Upload/substituição pelo admin: card em **Memoriais Descritivos**.
3. **Memorial** agrupado seção→ambiente, oculta itens sem spec; fotos com lightbox.
4. **Documentos por unidade**: anexa na obra→aba Documentação (`documentos_unidade` + bucket `unidade-docs`, qualquer formato 50MB, campos estruturados por categoria em `metadados` jsonb — futuro: LLM preenche); compartilha por toggles Prop/Inq na aba Manual do Cliente (privado por padrão); aparece na aba "Documentação" do portal (accordion, PDF/img na tela). Edge `manual-arquivo` v11 valida por documento.
5. **Contatos do Portal**: `portal_prestadores` vincula ao CADASTRO (fornecedores/trabalhadores/profissões — fonte única); curadoria em Memoriais Descritivos; portal cai no JSON semeado se lista vazia.
6. **Portão de recebimento no manual**: após CPF+senha, sumário numerado + termo + OTP e-mail; sem assinar NÃO acessa (fecha o "nunca assinei"). Registro em `manual_confirmacoes`.
7. **Vistoria**: (a) fotos comprimidas no aparelho (1600px) antes do upload; (b) botão "Gerar PDF" no admin quando geração automática falha; (c) e-mail pós-assinatura com botão "Ver minha vistoria" (link) e anexo só <20MB; (d) vistoria assinada é aba "Vistoria" DENTRO do manual do portal; (e) 1º acesso pelo link = tela verde "Abrir minha vistoria" → clique registra consentimento ÚNICO (`vistoria_visualizacoes` + `aberta_em` na RPC `vistoria_conteudo`); admin mostra "aberta pelo cliente em X"; (f) observações: caixa dinâmica + Enter=bullet (na página, na visualização e no PDF).
8. **Caso real VCG 318 C2 (Valério de Araujo)**: vistoria assinada 09/07; PDF re-gerado formato bullets; e-mail com link enviado. Links: manual `minhaobra.app/pc-construtora/manualdoproprietario/vcg-318-c2` · vistoria `minhaobra.app/pc-construtora/vistoria/e4827500-71fa-4e5c-a0dd-cc291b013e06`. VCG 322 C1 = TESTE (confirmação de leitura já usada; zerar se virar entrega real).

## PELA METADE / NÃO FEITO
- **Hero do Início + agrupamento visual das abas** ("Do seu imóvel"/"Da construtora") — último acabamento do Bloco A. Nada começado; só design combinado.
- **Docs da obra mãe visíveis nas unidades** (procurações "JBL" sem nº de unidade) — aguarda decisão do Pedro.
- **Categorias de FOTOS da unidade** — planejado, não feito.
- **LLM de extração** (preencher `metadados` + campos da aba Documentação lendo o arquivo) — futuro; schema pronto.
- **Fonte por tenant** (ID Grotesk da PC) — decidido opção (a): fica tipografia neutra por ora.

## PENDÊNCIAS COM DONO
- Pedro: anexar arquivos reais das obras (combinado; kit-padrão mapeado nas pastas JBL 705/717/723/729 do Dropbox — cuidado: "ERRO.pdf" é lixo; matrícula 40.109 NÃO é da JBL 729).
- Pedro: validar redação do marco de garantia com jurídico (texto atual: "assinatura do Termo OU imissão na posse, o que ocorrer primeiro" — atualizado direto no jsonb de garantias).
- Pedro: decisão docs da obra mãe → unidades.
- Sessão futura: hero+agrupamento; fotos por categoria.

## COMO RETOMAR (passo a passo)
1. Ler `~/.claude/frota/minhaobra.md` + os 2 briefings do repo + este update.
2. `cd /Users/pedrocosta/minhaobra/pedro-obras && git pull` — código é a verdade; migrations em `supabase/migrations/2026070*` e `2026070914/16/18*` JÁ APLICADAS em prod.
3. Antes de commit: `bun run build`. Push main direto = deploy.
4. Prod: pegar token ao vivo (comando acima), nunca cachear; RPC via `pg_get_functiondef` antes de alterar.
5. Testar portal: links da VCG 318 acima (login CPF do acesso + 6 últimos dígitos).
