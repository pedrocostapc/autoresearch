# Skill/receita — Popup "Nova versão disponível" (drop-in p/ toda a frota)

Origem: **Ei Risen** (risen-ai-connect). O Pedro gostou e quer em TODOS os apps.
Funciona em iPad / Chrome / Safari / web normal — é 100% web, sem backend, sem
build extra. App nativo (Capacitor) pula (atualiza pela loja).

## Como funciona (o truque)
O Vite gera o bundle de entrada com HASH no nome (`/assets/index-XXXX.js`) que muda
a cada build. O app compara o hash que ELE carregou (lendo o DOM) com o que o
servidor serve AGORA (`fetch('/')` com `no-store`). Diferente = saiu versão nova →
modal bloqueante. O botão "Atualizar agora" limpa Cache API + service workers e dá
reload (Ctrl+Shift+R por software) — mata o "bug fantasma" de versão velha em cache.

Requisito: app **Vite + SPA** hospedado na Vercel (o padrão da frota). Se for
Next.js/CRA, ver "Adaptações" no fim.

## Passo 1 — `src/hooks/useVersionCheck.ts` (drop-in, sem dependência nova)
```ts
import { useEffect, useRef, useState } from "react";

// Bundle de entrada com hash do Vite — muda a cada build.
const BUNDLE_RX = /\/assets\/index-[A-Za-z0-9_-]+\.js/;

// Guard nativo SEM importar @capacitor/core (funciona em app que não tem Capacitor).
function isNativeApp(): boolean {
  const cap = (window as unknown as { Capacitor?: { isNativePlatform?: () => boolean } }).Capacitor;
  return !!cap?.isNativePlatform?.();
}

function bundleFromHtml(html: string): string | null {
  const m = html.match(BUNDLE_RX);
  return m ? m[0] : null;
}
function currentBundle(): string | null {
  const nodes = Array.from(document.querySelectorAll("script[src], link[href]"));
  for (const n of nodes) {
    const url = (n as HTMLScriptElement).src || (n as HTMLLinkElement).href || "";
    const m = url.match(BUNDLE_RX);
    if (m) return m[0];
  }
  return null;
}
async function serverBundle(): Promise<string | null> {
  try {
    const res = await fetch(`/?_v=${Date.now()}`, { cache: "no-store" });
    if (!res.ok) return null;
    return bundleFromHtml(await res.text());
  } catch {
    return null;
  }
}
export async function hardReload() {
  try {
    if ("caches" in window) {
      const keys = await caches.keys();
      await Promise.all(keys.map((k) => caches.delete(k)));
    }
    if (navigator.serviceWorker) {
      const regs = await navigator.serviceWorker.getRegistrations();
      await Promise.all(regs.map((r) => r.unregister()));
    }
  } catch { /* segue pro reload */ }
  window.location.reload();
}
export function useVersionCheck(): { updateAvailable: boolean; reload: () => Promise<void> } {
  const [updateAvailable, setUpdateAvailable] = useState(false);
  const boot = useRef<string | null>(null);
  useEffect(() => {
    if (isNativeApp()) return;               // nativo atualiza pela loja
    boot.current = currentBundle();
    if (!boot.current) return;               // sem como comparar → não incomoda
    let stopped = false;
    const check = async () => {
      if (stopped || updateAvailable || document.visibilityState !== "visible") return;
      const srv = await serverBundle();
      if (srv && boot.current && srv !== boot.current) {
        setUpdateAvailable(true);
        stopped = true;
      }
    };
    const interval = setInterval(check, 3 * 60 * 1000);   // a cada 3 min
    const onVis = () => { if (document.visibilityState === "visible") void check(); };
    document.addEventListener("visibilitychange", onVis);
    const first = setTimeout(check, 30_000);              // 1ª checagem após 30s
    return () => {
      stopped = true;
      clearInterval(interval);
      clearTimeout(first);
      document.removeEventListener("visibilitychange", onVis);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return { updateAvailable, reload: hardReload };
}
```

## Passo 2 — `src/components/common/UpdateBanner.tsx` (modal bloqueante)
Ajuste os imports de `Button`/ícones pro que o app usa (aqui: shadcn + lucide).
Se o app não tiver `<Button>`, troque por um `<button>` estilizado.
```tsx
import { useState } from "react";
import { RefreshCw, Loader2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useVersionCheck } from "@/hooks/useVersionCheck";

export function UpdateBanner() {
  const { updateAvailable, reload } = useVersionCheck();
  const [reloading, setReloading] = useState(false);
  if (!updateAvailable) return null;
  return (
    <div className="fixed inset-0 z-[300] flex items-center justify-center bg-background/85 p-4 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-2xl border border-border bg-card p-8 text-center shadow-2xl">
        <span className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-accent/15 text-accent">
          <Sparkles className="h-8 w-8" />
        </span>
        <h2 className="font-display text-2xl font-medium tracking-tight">Nova versão disponível</h2>
        <p className="mx-auto mt-2 max-w-xs text-sm text-muted-foreground">
          Saiu uma atualização do sistema. Atualize agora pra continuar com a versão mais recente.
        </p>
        <Button size="lg" className="mt-7 h-12 w-full gap-2 text-base" disabled={reloading}
          onClick={() => { setReloading(true); void reload(); }}>
          {reloading ? <Loader2 className="h-5 w-5 animate-spin" /> : <RefreshCw className="h-5 w-5" />}
          {reloading ? "Atualizando…" : "Atualizar agora"}
        </Button>
      </div>
    </div>
  );
}
```

## Passo 3 — Montar UMA vez na raiz do app
No shell/layout raiz (ex.: `AppShell.tsx`, `App.tsx`), renderize `<UpdateBanner />`
uma vez, no topo da árvore (fica escondido até sair versão nova):
```tsx
import { UpdateBanner } from "@/components/common/UpdateBanner";
// ...dentro do return raiz:
<UpdateBanner />
```

## Verificar
1. `git push main` → Vercel builda (bundle ganha hash novo).
2. Deixe uma aba aberta na versão antiga; em ≤3 min (ou ao voltar pra aba) o modal
   aparece. Clicar recarrega na versão nova. Testar iPad Safari + Chrome desktop.

## Adaptações por app
- **Sem shadcn/lucide:** troque `<Button>` por `<button>` e os ícones por emoji/SVG.
- **Classe de tema:** `bg-background/85`, `bg-card`, `text-accent` são tokens do
  tema; se o app usa outras, ajuste.
- **Next.js:** não há `/assets/index-hash.js`; use `__NEXT_DATA__.buildId` vs o
  buildId servido em `/_next/...` (ou o header `x-nextjs-...`). Mecanismo idêntico,
  fonte do "hash" diferente.
- **CRA:** o entry é `/static/js/main.[hash].js`; ajuste o regex.

## Como o Pedro propaga
Em CADA app, abrir a sessão do Claude e colar:
> "Implanta o popup de 'Nova versão disponível' igual o Ei Risen — receita em
> `~/Dev/autoresearch/lab/inbox/skill-popup-nova-versao.md`. Adapta os imports de
> Button/ícone e monta na raiz."
