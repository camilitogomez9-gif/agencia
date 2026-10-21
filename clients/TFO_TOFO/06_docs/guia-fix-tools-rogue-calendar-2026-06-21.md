# Guía manual — Fix tools rogue de calendar en Agente de B2B (n8n vivo)

**Fecha:** 2026-06-21
**Workflow afectado:** `Agente WEB B2B y RRSS` (n8n vivo de TOFO Pizza)
**Bloqueante:** sí — el agente está creando citas overlapeadas y sin Zoom asociado.
**Tiempo estimado:** 10-15 min de edits + 5 min de smoke + 5 min de cleanup retroactivo del calendar Mauricio.

---

## Por qué este fix

Mauricio mandó screenshot mostrando el calendar con **varias citas overlapeadas en los slots 10/11/12 hora CDMX** durante varios días seguidos. Auditoría del workflow vivo reveló que el **Agente de B2B** (subagente del Agente de Derivación) tiene cableada como `ai_tool` una tool **paralela** a `check_disponibilidad`:

| Nodo | Type | Descripción | Estado |
|------|------|-------------|--------|
| `Create an event in Google Calendar` | `n8n-nodes-base.googleCalendarTool` | **VACÍA** | ACTIVO, cableado al B2B vía `ai_tool` |

Cuando el lead pedía cita, el LLM podía elegir entre 2 caminos:
- `check_disponibilidad` → invoca sub-workflow `vpLmZ299yXJrOSBv` → chequea overlap → crea Calendar event + Zoom meeting atómicamente
- `Create an event in Google Calendar` (rogue) → escribe directo en el calendar de Mauricio, sin chequeo, sin Zoom

El modelo elegía la vía directa por ser más barata cognitivamente. Resultado: overlaps + ausencia de Zoom meetings en el dashboard de Mauricio (el síntoma que reportó el 19/6 y que asumimos era bug de credencial Zoom).

Aprovechamos la misma cirugía para limpiar 2 zombies más (`googleSheetsTool` disabled que siguen wired).

---

## Pre-requisitos

- Acceso al n8n productivo de TOFO (workflow `Agente WEB B2B y RRSS`).
- Cuenta con permisos de edición.
- Ventana de mantenimiento de ~15 min (durante la cirugía dejamos el workflow inactivo).

---

## Paso 0 — Backup del estado actual

1. Abrir el workflow `Agente WEB B2B y RRSS` en n8n.
2. Menú `…` (arriba a la derecha) → **Download** → guardar como `agente-tofo-web-b2b-rrss-prod-snapshot-2026-06-21-pre-fix.json` en `~/Downloads/`.
3. Mover el archivo a `clients/TFO_TOFO/03_workflows/agente-tofo-web-b2b-rrss-prod-snapshot-2026-06-21-pre-fix.json` (queda como backup rolleable si algo sale mal).

---

## Paso 1 — Bajar el workflow a INACTIVO

1. Toggle `Active` (arriba a la derecha del editor del workflow) → **off**.
2. Confirmar que ningún webhook entrante quede pendiente (esperar 30 segundos).

> **Por qué:** durante los próximos 5 minutos no queremos que un lead nuevo dispare una ejecución mientras estamos editando wiring del AI Agent.

---

## Paso 2 — Localizar el nodo `Agente de B2B`

1. En el editor visual, buscá el nodo **`Agente de B2B`** (type `@n8n/n8n-nodes-langchain.agentTool`).
2. Click sobre el nodo para abrirlo. Vas a ver, en el panel derecho, todas las herramientas conectadas como `ai_tool`.
3. Alternativamente, hacé scroll en el canvas hasta ver al `Agente de B2B` con todas sus tools alrededor (conexiones de color distinto a las `main`).

**Inventario actual esperado del Agente de B2B (9 tools):**

| # | Nombre del nodo | Type | Acción |
|---|-----------------|------|--------|
| 1 | `check_disponibilidad` | `toolWorkflow` (→ `vpLmZ299yXJrOSBv`) | ✅ **NO TOCAR** |
| 2 | `Create an event in Google Calendar` | `googleCalendarTool` | ❌ **DESCONECTAR** |
| 3 | `elevar_conversacion` | `toolWorkflow` (→ `yJA04Pfyk2Id1aMo`) | ✅ **NO TOCAR** |
| 4 | `registrar` | `airtableTool` | ✅ **NO TOCAR** |
| 5 | `enviar_ficha_tecnica` | `toolHttpRequest` | ✅ **NO TOCAR** |
| 6 | `enviar_video_funcionamiento` | `toolHttpRequest` | ✅ **NO TOCAR** |
| 7 | `Doc informacion al cliente` | `googleDocsTool` | ⚠️ **NO TOCAR** en esta pasada (queda para validación follow-up) |
| 8 | `Crear la base de datos` | `googleSheetsTool` (disabled) | ❌ **DESCONECTAR** |
| 9 | `registrarrrrrrr` | `googleSheetsTool` (disabled) | ❌ **DESCONECTAR** |

---

## Paso 3 — Desconectar la conexión `ai_tool` de los 3 nodos rogue/zombie

> ⚠️ **Importante:** solo desconectamos la cara `ai_tool` del nodo (la línea que va al `Agente de B2B`). **NO eliminamos los nodos todavía** — los dejamos huérfanos en el canvas por seguridad/rollback. Una segunda pasada de cleanup puede eliminarlos completamente.

### 3.1. Desconectar `Create an event in Google Calendar` (CRÍTICO)

1. Localizar el nodo `Create an event in Google Calendar` (puede estar arriba/al costado del `Agente de B2B`).
2. Pasar el mouse por la **línea de conexión** que va del nodo al `Agente de B2B` (es una conexión `ai_tool`, color distinto a las `main`).
3. Click en la línea → aparece un botón ❌ (delete) → click para borrar **solo la conexión**.
4. El nodo `Create an event in Google Calendar` queda en el canvas pero **desconectado**.

### 3.2. Desconectar `Crear la base de datos`

Mismo proceso. Buscar la línea de conexión `ai_tool` del nodo `Crear la base de datos` (googleSheetsTool, disabled) al `Agente de B2B` y borrarla.

### 3.3. Desconectar `registrarrrrrrr`

Mismo proceso. Buscar la línea de conexión `ai_tool` del nodo `registrarrrrrrr` (googleSheetsTool, disabled) al `Agente de B2B` y borrarla.

---

## Paso 4 — Verificar inventario post-edit

Click sobre el `Agente de B2B`. En el panel derecho verifica que la lista de tools cableadas sea **exactamente 6**:

| # | Nombre del nodo | Type |
|---|-----------------|------|
| 1 | `check_disponibilidad` | toolWorkflow |
| 2 | `elevar_conversacion` | toolWorkflow |
| 3 | `registrar` | airtableTool |
| 4 | `enviar_ficha_tecnica` | toolHttpRequest |
| 5 | `enviar_video_funcionamiento` | toolHttpRequest |
| 6 | `Doc informacion al cliente` | googleDocsTool |

**Si la lista no coincide**, deshacé los cambios (`Ctrl+Z`) y revisá. Si coincide, seguir.

---

## Paso 5 — Smoke previo (lead simulado en el editor)

> Opcional pero recomendado. Si tenés prisa, saltá al Paso 6 y verificá con un smoke real post-deploy.

1. En el workflow, abrir el nodo `Webhook` (el primero) y agarrar un ejemplo de payload reciente (Pin data o execution history).
2. Click `Execute Workflow` con el payload de un lead simulado del tipo *"Hola, quiero agendar mañana 11 hs"*.
3. En la ejecución: verificar que el `Agente de B2B` invoque `check_disponibilidad` (no `Create an event...`). El último ya no existe como opción para el LLM.
4. Si todo OK → seguir. Si el LLM intenta invocar algo raro → revisar wiring.

---

## Paso 6 — Re-activar el workflow

1. Toggle `Active` → **on**.
2. Confirmar que el webhook está respondiendo (un lead real debería procesar normal en pocos segundos si entra alguno).

---

## Paso 7 — Export del JSON post-fix

1. Menú `…` → **Download** → guardar como `agente-tofo-web-b2b-rrss-v5.json` en `~/Downloads/`.
2. Mover el archivo a `clients/TFO_TOFO/03_workflows/agente-tofo-web-b2b-rrss-v5.json`.
3. Commitear al repo:

```bash
cd ~/Downloads/camilo-workspace
git add clients/TFO_TOFO/03_workflows/agente-tofo-web-b2b-rrss-v5.json
git add clients/TFO_TOFO/03_workflows/agente-tofo-web-b2b-rrss-prod-snapshot-2026-06-21-pre-fix.json
git commit -m "sync(TFO): export workflow vivo post-fix tools rogue calendar v5 + snapshot pre-fix"
```

---

## Paso 8 — Cleanup retroactivo del calendar de Mauricio

> Esto **no se puede hacer desde acá** — Mauricio tiene que entrar a su Google Calendar manualmente y borrar las citas duplicadas.

Mandarle el siguiente mensaje (WhatsApp grupo TOFO):

> **Mauricio, ya destrabamos el bug que causaba las citas overlapeadas (era una herramienta que el agente podía usar para escribir directo al calendar sin chequear disponibilidad — la desconectamos hoy).**
>
> Hace falta que limpies a mano las citas duplicadas que se acumularon en los últimos días en tu Google Calendar. Regla rápida para decidir cuál borrar:
>
> 1. Si hay 2 eventos al mismo slot (ej. 10am martes) con **distintos leads**: dejá los 2, no son duplicados — el agente debería haber rechazado el segundo pero por el bug le dio cita igual. Vas a tener que decidir manualmente con quién te quedás y al otro le avisás que coordinamos otro horario.
> 2. Si hay 2 eventos al mismo slot con **mismo lead** (mismo nombre): dejá el más reciente, borrá el viejo.
> 3. Si dudás: no borres y avisanos, lo revisamos juntos.
>
> A partir de hoy las citas nuevas se crean siempre via la herramienta segura (`check_disponibilidad`) que primero chequea que el slot esté libre. **No debería volver a aparecer overlap**.

---

## Paso 9 — Verificación post-deploy (24 hs)

Durante los próximos 1-2 días:

1. Mauricio revisa diariamente su calendar — **0 nuevos overlaps**.
2. Mauricio revisa su dashboard de Zoom (`zoom.us/meeting`) — **las citas nuevas aparecen como meetings programadas con sus respectivos `join_url`s**.
   - **Si aparecen** → el ticket Zoom del 19/6/26 queda cerrado por carambola (la credencial era correcta, el bug era la tool rogue todo el tiempo). Actualizar `06_docs/zoom-credencial-fix-2026-06-19.md` con la corrección de diagnóstico.
   - **Si NO aparecen** → mantener el plan original del 19/6 (migración de credencial OAuth) como follow-up independiente.
3. Si aparece un nuevo overlap → abrir incidente nuevo, esta fix no cerró todo.

---

## Plan de rollback (si algo sale mal)

1. Toggle `Active` → off.
2. Menú `…` → **Import** → seleccionar `clients/TFO_TOFO/03_workflows/agente-tofo-web-b2b-rrss-prod-snapshot-2026-06-21-pre-fix.json` → **Overwrite existing**.
3. Toggle `Active` → on.
4. Mensaje al equipo: "Rollback aplicado, investigando."

> **Trade-off del rollback:** vuelve el bug de overlaps. Solo usar si la fix rompe algo más grave (ej. el agente no responde, todas las citas fallan, etc).

---

## Próximos pasos post-deploy (la agencia side, no requieren acción tuya)

- Subir prompt B2B v1.15 al Google Doc vivo (el AI Agent lo carga vía `Get a document`).
- Correr smoke tests §P de testing-guide v8 (`clients/TFO_TOFO/07_testing/testing-guide-v8.md`).
- Postmortem en `06_docs/incidente-calendar-overlaps-2026-06-21.md`.
- Estándar reusable en `_core/standards/n8n-ai-agent-tool-inventory-audit.md` para evitar repetir el bug en otros clientes.
- ✅ **Auditoría preventiva de RRSS / Servicio / Reposición** — completada (resultado: limpio, no hay rogues; ver apéndice abajo).
- Eliminación completa de los 3 nodos desconectados (segunda pasada de cleanup, opcional).

---

## Apéndice — Auditoría preventiva de los otros subagentes (2026-06-21)

Después de detectar el smoking gun en el Agente de B2B, hicimos el mismo grep sobre los 3 subagentes restantes para verificar que el bug no se repite en otros caminos. **Resultado: limpio**. No hay tools rogue tipo Calendar/Zoom standalone en ninguno. Lo único detectado son 6 tools legítimas a las que les falta `toolDescription` (zombies de bajo riesgo, no causan bugs como el del B2B):

| Subagente | Tools cableadas | Rogue crítica | Zombies sin descripción |
|-----------|-----------------|---------------|------------------------|
| **Agente de RRSS** | 4 (1 agentTool + 1 sheets + 1 docs + 1 airtable) | ❌ ninguna | `Append or update row in sheet`, `Get a document in Google Docs`, `registrar` |
| **Agente de Servicio al Cliente** | 4 (1 agentTool + 1 sheets + 1 docs + 1 toolWorkflow) | ❌ ninguna | `Append or update row in sheet`, `Get a document in Google Docs1` |
| **Agente de Reposición** | 4 (1 sheets + 1 code disabled + 2 toolWorkflow) | ❌ ninguna | `Append or update row in sheet` |

**Veredicto:** los 3 subagentes están operativamente OK. La regla #4 del prompt B2B v1.15 los cubre también de manera preventiva por si en el futuro alguien re-cablea por error una tool de Calendar/Zoom en ellos. Las descripciones faltantes son follow-up de prioridad baja (mejoran trazabilidad pero no evitan bugs activos).
