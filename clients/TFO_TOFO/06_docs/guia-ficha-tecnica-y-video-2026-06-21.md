# Guía de implementación — Ficha técnica + Video funcionamiento (P2)

**Fecha:** 2026-06-21
**Origen:** Reunión Mauricio 18/6/26 + Plan v2 `1-qued-resuelto-2-enchanted-trinket.md`
**Bump prompt:** B2B v1.12 → v1.13 (ya aplicado en `agente-tofo-b2b-system-prompt.md`)

---

## 1. Decisión: 2 tools separadas

**Verbatim Mauricio (18/6/26):**
> "Pregunta costo, ficha técnica. ¿Cómo funciona la máquina? Le pasas el video."

→ 2 triggers distintos, 2 contenidos distintos. Se diseña con 2 flows separados en ManyChat + 2 tools separadas en n8n.

**Por qué NO unificar en uno solo:**
- Triggers ortogonales: el lead que pregunta precio NO necesariamente quiere video, y viceversa.
- Si después conviene mandar ambos (ej. cuando da SÍ a consent question de precio), es trivial invocar las dos tools en el mismo turno.
- Logs/diagnóstico por separado.

---

## 2. Decisión: HTTP node directo (no sub-workflow)

**Cambio respecto a la primera versión de esta guía:** originalmente se diseñaron 2 sub-workflows (`enviar-ficha-tecnica-tofo-v1.json` + `enviar-video-funcionamiento-tofo-v1.json`), cada uno con Trigger + HTTP node único. Borrados — la abstracción no aporta nada porque el "subflujo" tenía un solo nodo.

**Patrón vigente:** 2 nodos `@n8n/n8n-nodes-langchain.toolHttpRequest` directos en el main, cableados al `Agente de B2B` via `ai_tool`. Es el mismo patrón que `notificar` en `clients/CRZ_CerezaInvest/03_workflows/cereza-invest-agente-principal-v1.json`.

**Ventajas vs. sub-workflow:**
- 1 menos hop de invocación → menos latencia + menos puntos de falla.
- 1 menos workflow para mantener / activar / monitorear.
- Toda la lógica de la tool vive en el mismo workflow del agente — más fácil auditar.

---

## 3. JSON listo para pegar al main

**Archivo:** `clients/TFO_TOFO/03_workflows/tools-ficha-video-nodes-v1.json`

Contiene `{"nodes": [...], "connections": {}}` con los 2 nodos `toolHttpRequest`:

| Nodo (name = tool name que ve el LLM) | toolDescription resumido |
|---|---|
| `enviar_ficha_tecnica` | Mandar PDF oficial. Trigger: lead pidió precio o ficha. |
| `enviar_video_funcionamiento` | Mandar video oficial. Trigger: lead preguntó cómo funciona la máquina. |

**Configuración común (ambos nodos):**
- **method:** POST
- **url:** `https://api.manychat.com/fb/sending/sendFlow`
- **headers:** `Accept: application/json` + `Authorization: Bearer 3882072:b1c5f61336dcf3b9f2a0f0642648b7ab` (mismo bearer que `elevar_conversacion`)
- **body (JSON):**
  ```json
  {
    "subscriber_id": "{{ $('Webhook').first().json.body.id }}",
    "flow_ns": "REEMPLAZAR_CON_FLOW_NS_FICHA_TECNICA"
  }
  ```
  o `REEMPLAZAR_CON_FLOW_NS_VIDEO` según el nodo.

**Cómo importar:**
1. Abrí el main workflow `Agente WEB B2B y RRSS` en n8n.
2. Copiá el contenido entero de `tools-ficha-video-nodes-v1.json`.
3. En el canvas del main, paste (Cmd/Ctrl+V) — n8n agrega los 2 nodos.
4. Reemplazá los 2 placeholders `REEMPLAZAR_CON_FLOW_NS_*` en el JSON body de cada nodo por los `flow_ns` reales (después de crear los flows en ManyChat — ver §4).
5. Conectá cada nodo al `Agente de B2B` arrastrando un cable de tipo `ai_tool` (no `main`).
6. Save + Activate.

---

## 4. Estructura sugerida flujos ManyChat

### Flujo 1: `B2B Ficha técnica`

| Paso | Tipo bloque ManyChat | Contenido sugerido |
|---|---|---|
| 1 | Text | *"Te paso la ficha técnica completa con specs y modelos 👇"* |
| 2 | File / PDF | (subir el PDF que mandó Mauricio) |
| 3 | Text (opcional) | *"Cuando la revises, contame qué dudas te queda y vemos."* |

**Nombre interno:** `B2B Ficha técnica`
**Trigger:** External Request (desde n8n via `sendFlow`)
**Channel:** todos los activos (WhatsApp, Instagram, Facebook)

### Flujo 2: `B2B Video funcionamiento`

| Paso | Tipo bloque ManyChat | Contenido sugerido |
|---|---|---|
| 1 | Text | *"Mirá cómo funciona la máquina 🎥"* |
| 2 | Video / File | (subir el MP4 que mandó Mauricio) |
| 3 | Text (opcional) | *"En menos de 3 minutos el cliente tiene su pizza. ¿Tenés dudas puntuales sobre algún paso?"* |

**Nombre interno:** `B2B Video funcionamiento`
**Trigger:** External Request (desde n8n via `sendFlow`)
**Channel:** todos los activos

### Por qué este formato (3 pasos cada uno)
- **Mensaje de intro corto:** prepara el contexto antes de que llegue el adjunto pesado (mejor UX que mandar archivo solo).
- **Adjunto:** el contenido que pidió Mauricio.
- **Cierre con gancho:** mantiene la conversación viva y le pasa el turno al lead. Sin este paso el lead suele leer el archivo y desaparecer sin responder.

### Recolectar los `flow_ns` después de crear
ManyChat los muestra en la URL del flujo o en el botón "Get Flow ID". Formato esperado: `content<timestamp>_<hash>` (ej. `content20260526142445_613819`).

Una vez creados, copialos y reemplazalos en los 2 nodos `toolHttpRequest` del main (1 línea en el body JSON de cada uno).

---

## 5. Cambios al system prompt B2B (v1.12 → v1.13) — ya aplicados

El archivo `04_agents/agente-tofo-b2b-system-prompt.md` ya está actualizado a v1.13. El backup v1.12 queda en `04_agents/agente-tofo-b2b-system-prompt-v1.12.md`.

**Resumen de los 7 cambios aplicados:**

1. **§ 4 Tono y estilo:** quitar `Ofrecer dossier, brochure, PDF` de "Evita 100%". Agregar bloque de excepciones autorizadas (ficha técnica + video).
2. **§ 6 OBJETIVO:** revisar "Nunca ofrezcas: Dossiers/PDFs/brochures/Archivos de cualquier tipo" → reformular a "Contratos, brochures genéricos, dossiers comerciales / Documentación legal o financiera por chat" + agregar excepciones autorizadas.
3. **§ 9 PRECIO (Acción dar precio):** ahora son **3 cosas en el mismo turno** (texto del precio + invocar `enviar_ficha_tecnica` + cierre). Prohibición simétrica: no dar precio sin ficha; no mandar ficha sin precio.
4. **§ 🍕 FUNCIONAMIENTO:** nueva subsección "🎥 TOOL OBLIGATORIA `enviar_video_funcionamiento`" con disparadores y prohibiciones (frases tipo *"tenemos prohibido mandar videos"* ahora explícitamente vetadas).
5. **§ 🔟 Respuestas modelo "Si pide dossier":** se desdobla en 3 respuestas separadas: ficha técnica, video, y dossier comercial (este último sigue rechazado).
6. **§ Anti-alucinación:** "Contratos/dossiers/brochures/PDFs/archivos de cualquier tipo" reformulado a "Contratos, dossiers comerciales, brochures genéricos, archivos no autorizados" + nota explícita de excepciones autorizadas. Cierre con frase nueva ("el contrato se aterriza en la llamada" sin la frase contradictoria "mandamos cero documentación").
7. **Header + Historial:** v1.12 → v1.13 + fila nueva en la tabla.

Si necesitás ver el diff exacto: `git diff HEAD~1 -- clients/TFO_TOFO/04_agents/agente-tofo-b2b-system-prompt.md` (después del commit).

---

## 6. Smoke tests (post-deploy)

Casos mínimos a verificar:

| # | Trigger del lead | Comportamiento esperado |
|---|---|---|
| F1 | "Hola, ¿cuánto cuesta la máquina?" | Agente da precio en texto + invoca `enviar_ficha_tecnica` en el mismo turno. Lead recibe mensaje + PDF + cierre. |
| F2 | "¿Cómo funciona la máquina?" | Agente responde con descripción canónica (pre-horneada al 75% + ingredientes frescos) + invoca `enviar_video_funcionamiento`. Lead recibe mensaje + video + cierre. |
| F3 | "¿Tienes ficha técnica?" | Agente invoca `enviar_ficha_tecnica` directo + acompaña con frase corta. NO se la niega. |
| F4 | "¿Me puedes mandar un video?" | Agente invoca `enviar_video_funcionamiento`. NO debe decir "tenemos prohibido mandar videos" (regression del incidente Mauricio 18/6/26). |
| F5 | "Mándame el contrato" | Agente NO invoca ninguna tool de archivo, sigue con respuesta canónica "el contrato lo aterrizamos en la llamada con el director". (la regla anti-contratos sigue viva — el cambio solo autoriza ficha técnica + video). |
| F6 | Lead pregunta precio + "cómo funciona" en el mismo mensaje | Agente da precio + invoca AMBAS tools (ficha + video) en el mismo turno. |
| F7 | Lead dice consent SÍ a "¿quieres saber el precio?" | Agente da precio + invoca `enviar_ficha_tecnica` (post-consent positivo cuenta como pregunta de precio). |

**Cómo verificar en producción:**
- Logs n8n del main (ejecución del nodo `enviar_ficha_tecnica` / `enviar_video_funcionamiento` con response 200).
- Consola ManyChat → ver que el `sendFlow` se ejecutó.
- Conversación con el lead en el inbox ManyChat — confirmar que llegó el adjunto.

---

## 7. Rollback

Si algo rompe:

1. En el main n8n, **deshabilitar** los 2 nodos `toolHttpRequest` (`enviar_ficha_tecnica`, `enviar_video_funcionamiento`) → quita la conexión `ai_tool` al `Agente de B2B`.
2. Revertir el prompt vivo a v1.12 desde el backup `agente-tofo-b2b-system-prompt-v1.12.md` (sobrescribir y subir al Google Doc del prompt si está cargado desde ahí).
3. Save + Activate.

Tiempo estimado rollback: < 3 min.

---

## 8. Pendientes operativos

- [ ] Mauricio: localizar los 2 archivos (PDF ficha + MP4 video) y subirlos a ManyChat (en los 2 flows nuevos).
- [ ] la agencia: crear los 2 flows en ManyChat (`B2B Ficha técnica` + `B2B Video funcionamiento`) — copiar los 2 `flow_ns`.
- [ ] la agencia: pegar los 2 nodos en el main (Cmd/Ctrl+V con el JSON de `tools-ficha-video-nodes-v1.json`).
- [ ] la agencia: reemplazar los 2 placeholders `REEMPLAZAR_CON_FLOW_NS_*` por los `flow_ns` reales.
- [ ] la agencia: cablear los 2 nodos via `ai_tool` al `Agente de B2B`.
- [ ] la agencia: smoke F1-F7 en testing.
- [ ] la agencia: promover a LIVE post-pass + commit.
