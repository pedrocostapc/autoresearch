# Popup "Nova versão disponível" — receita drop-in pra TODA a frota

**Pra quem:** qualquer sessão de app da frota (agencia, risenos, supersec, minhaobra,
nafazenda, core-front, etc.). O Pedro quer o mesmo popup do **Ei Risen** em todos.

## O que é
Modal bloqueante "Nova versão disponível → Atualizar agora" que aparece sozinho
quando saiu deploy novo. 100% web (funciona iPad / Chrome / Safari / web normal),
**sem backend, sem build extra**. App nativo (Capacitor) pula (atualiza pela loja).

## Como funciona (o truque)
O Vite dá HASH no bundle de entrada (`/assets/index-XXXX.js`), que muda a cada build.
O app compara o hash que ELE carregou (lendo o DOM) com o que o servidor serve agora
(`fetch('/')` no-store). Diferente = versão nova → modal. Botão limpa Cache API +
service workers e recarrega (mata o "bug fantasma" de versão velha em cache).
Requisito: Vite + SPA na Vercel (o padrão da frota).

## Receita completa (copiar/colar)
`~/Dev/autoresearch/lab/inbox/skill-popup-nova-versao.md` — tem os 2 arquivos
(`useVersionCheck.ts` + `UpdateBanner.tsx`, sem dependência nova; guard nativo sem
importar Capacitor), onde montar (`<UpdateBanner/>` na raiz), como testar, e as
adaptações pra Next.js/CRA e pra apps sem shadcn/lucide.

## Como plantar num app
Abrir a sessão do Claude no app e colar:
> "Implanta o popup de 'Nova versão disponível' igual o Ei Risen — receita em
> `~/Dev/autoresearch/lab/inbox/skill-popup-nova-versao.md`. Adapta os imports de
> Button/ícone e monta na raiz."

## Armadilha conhecida (aprendida no susto de hoje)
Ao copiar o `UpdateBanner`/qualquer componente que use `cn(...)`, **conferir o import
`import { cn } from "@/lib/utils"`**. O `tsc` do eirisen NÃO pega `cn` faltando
(parece ter um ambient global) — passa no type-check e só quebra em runtime com
`ReferenceError: cn is not defined`. Rodar a página de verdade, não confiar só no tsc.
