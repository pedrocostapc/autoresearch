# SUF16 — Pré-PR4: Página de Configurações de Sistema

> Sub-sprint curta antes do PR4. Cria infra de configurações do superadmin que PR4 vai consumir.
>
> Estimativa: 3-4 horas.
> Branch: `suf16-system-config`

---

## Contexto

PR4 (Products + Excel) precisa ler 2 tipos de configuração:

1. **Número WhatsApp de suporte** — pro botão "Mande pra equipe arrumar" gerar link `wa.me/<numero>`
2. **Limite máximo de Excel por caixa** — pra validar tamanho do upload antes de processar

Em vez de hardcode esses valores, criar página `/admin/system-config` (ou similar) editável pelo superadmin. Tabela `system_config` key-value.

Decisões já tomadas com Pedro:
- Página completa de configurações no menu lateral, abaixo de "InsightBackfill"
- Nome no menu: **"Configurações"**
- Limites de Excel **por caixa** (não global)
- 8 caixas com Excel: products, services, delivery_items, delivery_areas, team, forwards, faq, objections (Events sai — só perguntas)
- Defaults: 5MB pra catálogos grandes (products, services, delivery_items), 3MB médios (team, events), 2MB pequenos (delivery_areas, forwards, faq, objections)

---

## Etapa 1 — Confirmações antes de codar

Reportar:

### A. Estrutura atual do menu lateral admin

```bash
grep -rn "InsightBackfill\|insight-backfill\|/admin" src/ --include="*.tsx" --include="*.ts" | head -20
```

- Caminho do componente do menu lateral admin
- Como rotas /admin são definidas
- Se existe layout dedicado pra páginas admin
- Reportar o array/lista de itens do menu lateral admin atual

### B. Tabela `system_config` ou similar existe?

```bash
grep -rn "system_config\|admin_config\|settings" supabase/migrations/ --include="*.sql"
```

- Se já existe alguma tabela de config, reportar schema
- Se não existe, confirma criação

### C. Confirmação dos defaults

Confirmar lista final de caixas + defaults. **Events removido** (só perguntas, sem Excel):

| Caixa | Default (MB) |
|---|---|
| products | 5 |
| services | 5 |
| delivery_items | 5 |
| delivery_areas | 2 |
| team | 3 |
| forwards | 2 |
| faq | 2 |
| objections | 2 |

### D. RLS e auth

- Como super admin é detectado hoje? (memory mencionou role super_admin)
- RLS na tabela `system_config` deve permitir SELECT pra autenticados (qualquer tenant pode ler — pra usar config no front)?
- Ou só super admin lê? (mais seguro mas exige edge function pra front consultar)

Recomendação: **SELECT pra autenticados**, **UPDATE só super admin**. Configs não são secrets sensíveis (são limites técnicos + número de suporte público). Front consulta direto.

Code reporta o approach atual (auth role super_admin) e confirma.

---

## Aguarda OK antes de prosseguir.

---

## Etapa 2 — Migration `system_config`

```sql
-- supabase/migrations/<timestamp>_create_system_config.sql

CREATE TABLE IF NOT EXISTS system_config (
  key text PRIMARY KEY,
  value text NOT NULL,
  description text,
  updated_at timestamptz DEFAULT now(),
  updated_by uuid REFERENCES auth.users(id)
);

-- Trigger pra updated_at automático
CREATE TRIGGER set_system_config_updated_at
  BEFORE UPDATE ON system_config
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- (assumindo que set_updated_at já existe; se não, criar inline)

-- RLS
ALTER TABLE system_config ENABLE ROW LEVEL SECURITY;

-- SELECT: qualquer autenticado pode ler
CREATE POLICY system_config_read ON system_config
  FOR SELECT TO authenticated
  USING (true);

-- INSERT/UPDATE/DELETE: só super admin
CREATE POLICY system_config_write ON system_config
  FOR ALL TO authenticated
  USING (is_super_admin())  -- assumindo função is_super_admin existente
  WITH CHECK (is_super_admin());

-- Seed
INSERT INTO system_config (key, value, description) VALUES
  ('support_whatsapp_number', '+5538998940667', 'Número WhatsApp de suporte ao cliente'),
  ('excel_max_mb_products', '5', 'Limite Excel para Products (MB)'),
  ('excel_max_mb_services', '5', 'Limite Excel para Services (MB)'),
  ('excel_max_mb_delivery_items', '5', 'Limite Excel para Delivery Items (MB)'),
  ('excel_max_mb_delivery_areas', '2', 'Limite Excel para Delivery Areas (MB)'),
  ('excel_max_mb_team', '3', 'Limite Excel para Team (MB)'),
  ('excel_max_mb_forwards', '2', 'Limite Excel para Forwards (MB)'),
  ('excel_max_mb_faq', '2', 'Limite Excel para FAQ (MB)'),
  ('excel_max_mb_objections', '2', 'Limite Excel para Objections (MB)')
ON CONFLICT (key) DO NOTHING;
```

**Atenção:** Pedro vai rodar essa migration via SQL Editor manualmente (sem `supabase db push`). PR description anota.

Se `is_super_admin()` ou `set_updated_at()` não existem, Code adapta no momento (escreve inline).

---

## Etapa 3 — Hook + helpers

### Hook React

```ts
// src/hooks/useSystemConfig.ts

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

export function useSystemConfig(key?: string) {
  return useQuery({
    queryKey: ["system_config", key ?? "all"],
    queryFn: async () => {
      let query = supabase.from("system_config").select("*");
      if (key) query = query.eq("key", key);
      const { data, error } = await query;
      if (error) throw error;
      return key ? data[0]?.value : data;
    },
  });
}

export function useUpdateSystemConfig() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ key, value }: { key: string; value: string }) => {
      const { error } = await supabase
        .from("system_config")
        .update({ value })
        .eq("key", key);
      if (error) throw error;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["system_config"] });
    },
  });
}
```

### Helper pra pegar limite por caixa

```ts
// src/lib/systemConfig.ts

export function getExcelLimitKey(boxType: string): string {
  return `excel_max_mb_${boxType}`;
}

export function parseLimitMb(value: string | undefined, fallback = 5): number {
  if (!value) return fallback;
  const n = Number(value);
  return isNaN(n) ? fallback : n;
}
```

---

## Etapa 4 — Página /admin/system-config

### Roteamento

Adicionar rota `/admin/configuracoes` (ou `/admin/system-config`) — Code escolhe que faz mais sentido com o padrão atual.

### Item no menu lateral admin

Adicionar entry abaixo de "InsightBackfill":

```tsx
{
  label: "Configurações",
  href: "/admin/configuracoes",
  icon: Settings,  // lucide-react
}
```

### Página

```tsx
// src/pages/admin/SystemConfig.tsx

import { useSystemConfig, useUpdateSystemConfig } from "@/hooks/useSystemConfig";
// ...

export default function SystemConfigPage() {
  const { data: configs, isLoading } = useSystemConfig();
  const update = useUpdateSystemConfig();
  const [draft, setDraft] = useState<Record<string, string>>({});

  // ... carrega configs em draft, edita, salva

  return (
    <AdminLayout>
      <h1>Configurações</h1>
      
      <Section title="Suporte">
        <Field
          label="WhatsApp de suporte"
          helper="Cliente clica 'Mande pra equipe arrumar' → abre conversa com esse número"
          value={draft.support_whatsapp_number ?? ""}
          onChange={(v) => setDraft({ ...draft, support_whatsapp_number: v })}
          placeholder="+5538998940667"
        />
      </Section>

      <Section title="Limites de upload por caixa">
        <p>Acima do limite, cliente é orientado a usar "Mande pra equipe arrumar"</p>
        
        {EXCEL_BOXES.map(box => (
          <NumberField
            key={box.boxType}
            label={box.label}
            suffix="MB"
            value={draft[`excel_max_mb_${box.boxType}`] ?? ""}
            onChange={(v) => setDraft({ ...draft, [`excel_max_mb_${box.boxType}`]: v })}
          />
        ))}
      </Section>

      <Button onClick={handleSave}>Salvar configurações</Button>
    </AdminLayout>
  );
}

const EXCEL_BOXES = [
  { boxType: "products", label: "Products" },
  { boxType: "services", label: "Services" },
  { boxType: "delivery_items", label: "Delivery Items" },
  { boxType: "delivery_areas", label: "Delivery Areas" },
  { boxType: "team", label: "Team" },
  { boxType: "forwards", label: "Forwards" },
  { boxType: "faq", label: "FAQ" },
  { boxType: "objections", label: "Objections" },
];
```

### UX

- Form simples com 2 seções
- Cada campo tem label + helper text + input
- Botão "Salvar configurações" ao final
- Toast de sucesso/erro após salvar
- Loading state enquanto carrega

### Validações

- WhatsApp: aceita formato livre, mas placeholder mostra `+5538998940667`
- Limite MB: numérico positivo, min 1, max 100
- Salvar valida tudo antes de mandar

---

## Etapa 5 — Deploy

### Antes do deploy

Pedro roda a migration manualmente:

```sql
-- Cole conteúdo de supabase/migrations/<timestamp>_create_system_config.sql no SQL Editor
-- Confirma com:
SELECT * FROM system_config;
-- Esperado: 9 rows (1 whatsapp + 8 limites)
```

### Deploy

```bash
gh pr merge <PR> --squash --delete-branch
git push origin main  # Lovable build
```

Sem deploy de edge function (mudança só em front + DB).

### Validação pós-deploy

Pedro abre `/admin/configuracoes`:
1. Confirma menu lateral mostra "Configurações" abaixo de InsightBackfill
2. Página abre com valores seedados
3. Edita WhatsApp pra outro número de teste
4. Salva → toast de sucesso
5. Recarrega → valor persistido
6. Edita 1 limite (ex: products de 5 pra 10)
7. Salva
8. Recarrega → persistido

---

## Critérios de aceite

- [ ] Etapa 1 confirmação aprovada antes de codar
- [ ] Migration `system_config` com tabela + RLS + seed
- [ ] Hook `useSystemConfig` e `useUpdateSystemConfig`
- [ ] Helper `getExcelLimitKey` e `parseLimitMb`
- [ ] Rota `/admin/configuracoes` (ou similar)
- [ ] Item no menu lateral abaixo de InsightBackfill
- [ ] Página completa com 2 seções (Suporte + Limites)
- [ ] 9 campos editáveis (1 WhatsApp + 8 limites)
- [ ] Salvar funciona, toast de feedback
- [ ] Build/tsc/vitest verde
- [ ] PR description anota que Pedro roda migration via SQL Editor

---

## Pós-merge — Próximo: PR4

PR4 vai consumir essa config:
- Edge `import-box-excel` lê `excel_max_mb_<boxType>` antes de processar
- UI do modal Products lê `support_whatsapp_number` pro botão "Mande pra equipe"
- Hook `useSystemConfig("excel_max_mb_products")` pro front mostrar limite na UI

---

## Restrições

- ❌ Sem mexer em outras páginas admin (dashboard, etc)
- ❌ Sem implementar Excel import ainda (PR4)
- ❌ Smoke automático (Pedro testa)
- ✅ Migration vai no commit, Pedro roda manual
- ✅ Mostrar diff antes do commit
- ✅ Branch: `suf16-system-config`
- ✅ PR título: `feat(admin): página de configurações + tabela system_config (SUF16)`

---

## O que NÃO fazer neste PR

- ❌ PR4 (Products + Excel) — sub-sprint específica depois
- ❌ Outras configs (locale, system_name, support_email) — só os 9 valores combinados
- ❌ Histórico de mudanças (audit log) — fica pra futuro se precisar
