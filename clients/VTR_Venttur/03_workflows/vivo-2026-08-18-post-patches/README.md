# Export post-patches — Venttur — 2026-08-18

Estado de los 4 workflows tocados **después** de aplicar las correcciones del Reporte la agencia 1.
Punto de referencia actual. El estado **previo** (rollback) está en `../vivo-2026-08-17/`.

| workflow | id | active | nodos | sha256[:16] |
|---|---|---|---|---|
| `main-venttur.json` | `k3aivKSP67S97IHn` | True | 35 | `1da9fe227f8dc642` |
| `outreach-form-meta.json` | `CUuFxbst3iHpgeXS` | True | 37 | `989d386eedeca249` |
| `resumen-etiquetas-seguimientos.json` | `DyrDumQgb6S4zHsS` | False | 27 | `2374e89b06751f33` |
| `confirmacion-agenda.json` | `2PSekVBxarsrnVBu` | True | 22 | `601be065f4afd461` |

## Cambios aplicados (todos verificados contra el vivo)

| # | Workflow | Cambio | Cierra |
|---|---|---|---|
| — | `confirmacion-agenda` | 4 referencias rotas a nodos inexistentes → `Obtener ID Manychat1` | **H1** (0 de 11 leads recibían confirmación) |
| P1 | `outreach-form-meta` | `Toques enviados < 3` → `< 2`; cadencia de 72 h eliminada; `Switch` salida[2] (Touch 3) desconectada | **H3** (11 de 34 fallos) |
| P2 | `resumen-etiquetas-seguimientos` | whitelist de la Tarea 4: **+`agendar-ema`**, −`SPEagendar` (no existe), −2 duplicados | **H2** (el 64%) |
| P3 | `resumen-etiquetas-seguimientos` | los 2 `No envio link?` leen `Link asesoría enviado` de Airtable en vez de la inferencia del LLM | **H2** (fix estructural) |
| P4 | `main-venttur` | `Hay audios?`: `equals 'webp'` → `notContains 'webp'` (condición imposible con `AND`) | **H4 / P5** — la rama de transcripción nunca había corrido |
| P5 | `main-venttur` | `Actualizar ultimo mensaje` escribe `respuesta_definitiva` (UTF-8) en vez de `headers.mensaje` (mojibake); salida TRUE de `Repetido?` cableada | **H4** (caso Omar Montes) |

## Verificación de integridad

En los 3 workflows: mismo set de nodos, y **sólo** cambiaron los parámetros de los nodos listados
y las conexiones de `Repetido?` y `Switch`. En el prompt del dispatcher cambió **una sola línea**
de 4.564 caracteres (−85). Los 3 siguen `active: true`.

## Rollback

`python3 scripts/utilities/vtr-aplicar-correcciones-agosto.py --list` para ver los patches.
Para revertir, importar el JSON correspondiente de `../vivo-2026-08-17/` por nodo (nunca re-import
completo del workflow).
