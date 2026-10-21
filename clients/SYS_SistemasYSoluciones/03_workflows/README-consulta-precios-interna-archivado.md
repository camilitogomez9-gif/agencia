# SYS — Consulta de precios interna (ARCHIVADO)

**Estado:** Archivado el 2026-06-23. Edgardo rechazó la propuesta económica del 2026-06-23.

## Qué es

Sub-workflow standalone de 8 nodos que implementa la lógica de consulta de precios desde un Google Sheet, sin LLM, devolviendo respuesta formateada por ManyChat.

Originalmente diseñado para inyectarse en el main `sys-agente-principal-v0.9` como una rama paralela que se activa cuando el `subscriber_id` matchea una whitelist interna (Rodrigo + la agencia). Ese diseño quedó en stand-by porque el cliente rechazó la propuesta económica.

## Archivos relacionados

- `sys-tool-consulta-precios-interna-archivado-v1.json` — el sub-workflow standalone (este).
- `../01_discovery/propuesta-consulta-precios-interna-2026-06-23.md` — la propuesta económica rechazada (USD 240 / 2hs).
- `../06_docs/guia-deploy-consulta-precios-interna-2026-06-23.md` — guía de deploy original (válida si en el futuro se retoma).

## Cómo retomar en el futuro

Si Edgardo aprueba en un proyecto más grande:

1. Importar este JSON a n8n como sub-workflow (sin activar).
2. Cablear desde el main `sys-agente-principal` con un nodo `Execute Workflow` que pase: `{ subId, mensajeActual, canalLabel, sessionKey }` (shape que entrega el `Normalize Payload` del main).
3. La decisión de cuándo invocarlo (whitelist Rodrigo, keyword especial, canal aparte, etc.) se hace en el main, no acá.
4. Pre-flight: spreadsheet ID + tab del Sheet de Rodri + credencial Google con acceso (placeholders `<<<SHEET_ID_PRECIOS_RODRI>>>` y `<<<TAB_NAME>>>` en el nodo `Read precios Rodri`).
5. Smoke tests: ver guía de deploy original.

## Notas técnicas

- Sin LLM. Code puro determinístico, ~100-300ms latencia, $0/consulta.
- El nodo Trigger es `Execute Workflow Trigger` (sub-workflow), no Webhook — para integrarse limpio en cualquier main.
- El nodo `Filter + Format` adapta automáticamente la salida a las columnas que tenga el sheet (muestra las primeras 2 columnas en el header de cada match, el resto en formato `key: value`).
- pinData incluye un test válido (subId de la agencia + query "cuanto sale el HUENU UV") para Execute Workflow en n8n.
