# HPF · Corrección Vasos Mágicos $35 (bot Kommo) — 2026-09-09

## Pedido de Oscar (WhatsApp)

> los VASOS DE 24 OZ "MAGICOS" esos cuestan $35 · esos no entran en la promoción · para que lo puedan
> poner como observación · si ponen algo como: los vasos que cambian de color / los vasos magicos /
> vaso termocromatico → esos son los de $35 "magicos".

## Qué se aplicó (LIVE en devn8n, `pYtiBlhOTr7HVPmr`)

Edit de prompt en el nodo **`AI Agent Recolector`** (Rebeca), en 2 puntos:

1. **Bloque de precios** (después de `- Vasos popote: $25`): se agregó
   `- Vasos Mágicos 24 oz (termocromáticos / los que cambian de color): $35 — ⚠️ NO entran en la promoción`.
2. **Reglas de vasos** (después de la regla de 1 color del popote): bloque nuevo "Vasos Mágicos 24 oz
   — PRODUCTO DISTINTO al Vaso Popote" con: keywords de reconocimiento ("vasos mágicos", "vasos que
   cambian de color", "vaso termocromático"), precio **$35, fuera de promo**, desambiguación ("vasos" a
   secas = popote $25; solo $35 si menciona mágicos/cambian de color/termocromático), y que para
   **envío y mínimos se tratan igual que los vasos popote** (mínimo 50, mismo peso, 1 diseño).

## Decisiones

- **No se tocó la CALCULADORA** (`Code2`): los mágicos comparten categoría "vasos" para peso/mínimo
  (0.14 kg, mín 50). El precio ($25 vs $35) lo pone el agente en la cotización, no la calculadora.
- **No se tocó `AI Agent Recolector1`** (rama de imagen): tiene otra estructura y no matchean los
  anchors; además el mágico se reconoce por texto ("cambian de color"), no por foto. Si en la rama de
  imagen llegara a cotizar mal un vaso, se agrega ahí con un anchor propio.
- Recolector2 es huérfano: no se toca.

## Verificación / rollback

- Releído del vivo: líneas 172 (precio) + 206-210 (reglas) presentes y coherentes.
- Script: `/private/tmp/.../hpf_vasos_magicos.py` (anchored, dry-run por defecto; `--apply` escribe;
  sanea `settings`). Snapshot de rollback del main pre-edit:
  `clients/HPF_HappyFlops/03_workflows/kommo-live-2026-09-09-pre-vasos-magicos/` (sha256).

## Pendiente sugerido

- Confirmar con Oscar si los Vasos Mágicos tienen **imagen propia** (para mandarla cuando el cliente
  pregunte) y si el **mínimo** es 50 como el popote. Hoy quedaron asumidos = popote.
