# W6 después del ciclo de cierre — 2026-08-14

Rollback: `../ghl-live-2026-08-14/W6.json`

## Qué cambió, y nada más que esto

| nodo | cambio |
|---|---|
| `Products` (systemMessage) | + delta 07: conserva el material de la pantufla (peluche vs satín) |
| `Recolector` (systemMessage) | + delta 02: negritas en producto/subtotal/total/anticipo + lista cerrada de emojis |
| `Partir en burbujas` | + conversión de `[texto](url)` a URL pelada |

## Lo que NO se cambió, y por qué

- **Delta 04 (orden del pago)** — se midió 5/5 funcionando sin él.
- **Delta 06 (separar ubicación de seguridad)** — se midió 5/5 funcionando sin él; lo que
  fallaba era el formato del link, que se arregló por código.
- **Delta 01 y 03 (saludo)** — ya resuelto por el nodo `Partir en burbujas`.
- **`LM Products`** — se probó temp 0 (3/6) y gpt-5-mini (2/6) contra el original (3/5).
  Ninguna mejora, así que se restauró byte-idéntico al snapshot.

## Efecto colateral del deploy, benigno

El PUT completo de la API de n8n descarta las claves con valor por defecto: `Router`,
`Starter` y `Main Image` perdieron `hasOutputParser: false`. Es el default, así que es
semánticamente idéntico — y se verificó en la captura posterior que los tres agentes se
comportan igual. Se anota porque aparece en cualquier diff estructural contra el snapshot.
