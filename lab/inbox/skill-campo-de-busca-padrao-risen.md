# SKILL — Campo de busca padrão Risen (todo app da frota)

**Origem:** Contatos do eirisen, 08/07/2026 — o campo roubava o foco a cada
letra, sumia quando a busca dava zero, e não achava "Pedro Costa" digitando
"Costa Pedro". Pedro decretou: todo campo de busca da frota nasce assim.

## As 5 regras (checklist pra QUALQUER campo de busca)

1. **O input NUNCA desmonta enquanto o usuário digita.**
   O campo vive FORA de qualquer ternário de loading/vazio. Skeleton no meio
   da digitação = input destruído = foco roubado. Com react-query:
   `placeholderData: keepPreviousData` (v5) — o resultado anterior fica na
   tela enquanto a busca nova carrega; `isLoading` só é true no primeiro load.

2. **Zero resultados NÃO engole o campo.**
   EmptyState de "tenant vazio" só quando NÃO há busca ativa. Busca sem
   resultado = mensagem "Nenhum X encontrado" ABAIXO do campo (que continua
   lá, com o texto, apagável).

3. **Ordem das palavras não importa.**
   Quebrar o termo em palavras; cada palavra vira um `ilike` próprio; TODAS
   precisam bater (AND), em qualquer posição, nos campos de nome. No
   PostgREST: `or(name.ilike.%costa pedro%, and(name.ilike.%costa%,name.ilike.%pedro%))`.
   Sanitizar `% , ( )` do input antes (quebram a sintaxe do .or).

4. **Debounce de ~300ms + busca NO SERVIDOR.**
   Busca no cliente só acha o que está carregado — com milhares de registros
   pós-import, mente. Debounce evita 1 request por tecla.

5. **Buscar pelo que o leigo tem na mão.**
   Nome, telefone (só dígitos, match parcial — com/sem 55/DDD/9), email,
   CPF/CNPJ, razão social, nº de pedido... O usuário cola o que tem; o campo
   descobre. Nunca exigir formato.

## Implementação de referência (copiar daqui)

`risen-ai-connect` (eirisen), commit `44b812a`:
- `src/features/contacts/hooks/useContacts.ts` — keepPreviousData + tokens AND
  + sanitização + busca server-side com múltiplos campos + resolver nº de
  pedido → dono.
- `src/features/contacts/pages/ContactsPage.tsx` — input fora do ternário,
  EmptyState só sem busca ativa.

## Anti-padrões (o que NÃO fazer)
- `{isLoading ? <Skeleton/> : <div><Input/>…</div>}` ← rouba foco.
- `ilike '%termo inteiro%'` como único match de nome ← ordem rígida.
- Filtrar client-side um array paginado ← não acha os antigos.
