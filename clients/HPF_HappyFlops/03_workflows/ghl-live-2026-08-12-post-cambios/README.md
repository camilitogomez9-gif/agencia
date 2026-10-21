# devn8n vivo — DESPUÉS de los cambios de la reunión del 2026-08-11

Solo los 3 workflows que se tocaron. El resto está sin cambios en `../ghl-live-2026-08-12/`,
que es además el punto de rollback.

| wf | nodos antes | nodos después | qué se tocó |
|---|---|---|---|
| W3 | 13 | 13 | nada (se verificó que filtra bien; el bug no estaba acá) |
| W6 | 39 | 41 | +2 nodos (Leer evento, Guardar evento) · Leer Products, Partir en burbujas, Cards a partes, Canonicalizar productos, Router.text · systemMessage de Starter, Products y Recolector |
| W9 | 4 | 4 | +1 consulta en la lista blanca (estado_sesion) |
