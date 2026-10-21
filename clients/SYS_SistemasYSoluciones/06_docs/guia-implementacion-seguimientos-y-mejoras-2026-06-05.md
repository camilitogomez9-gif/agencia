# Guía de implementación — Seguimientos automáticos + 4 mejoras GDoc (SYS)

**Fecha:** 2026-06-05
**Cliente:** SYS — Sistemas y Soluciones
**Objetivo:** dejar implementado el cron de seguimientos a 24h/7d + los 4 ajustes del Google Doc del cliente, antes de la migración de infraestructura.

---

## Resumen de qué se entrega

| Archivo | Acción en n8n / Supabase |
|---------|--------------------------|
| [supabase-schema-v2-seguimientos.sql](supabase-schema-v2-seguimientos.sql) | Ejecutar en Supabase Studio SQL Editor |
| [sys-seguimientos-leads-v1.json](../03_workflows/sys-seguimientos-leads-v1.json) | Importar como workflow nuevo en n8n |
| [sys-agente-principal-v0.6.json](../03_workflows/sys-agente-principal-v0.6.json) | Importar reemplazando el v0.5 vivo |
| [edits-prompt-mejoras-2026-06-05.md](edits-prompt-mejoras-2026-06-05.md) | Aplicar 5 edits manualmente en el Google Doc del prompt |

**Cobertura de los pendientes:**
- ✅ Pendiente 2 (seguimientos): cubierto por SQL + workflow seguimientos + Update ultima_actividad en v0.6.
- ✅ Pendiente 3 punto 1 (provincia/localidad): cubierto por edits 1 + 2 en Google Doc.
- ✅ Pendiente 3 punto 2 (reconocer "ese número"): cubierto por edit 3 en GDoc + cambio JS en `Build User Message Context` en v0.6.
- ✅ Pendiente 3 punto 3 (preguntar equipo/experiencia): cubierto por edit 4 en GDoc (ETAPA 5.5 nueva).
- ✅ Pendiente 3 punto 4 (mensajes duplicados): cubierto por reorganización del `Respond to Webhook` en v0.6.

---

## Orden de aplicación recomendado

Aplicar en este orden para evitar inconsistencias:

### 1) Supabase — schema v2 (5 min)

1. Abrir Supabase Studio → proyecto `la agencia-sys` → SQL Editor.
2. Pegar el contenido completo de [supabase-schema-v2-seguimientos.sql](supabase-schema-v2-seguimientos.sql).
3. Ejecutar.
4. Verificar:
   ```sql
   SELECT column_name FROM information_schema.columns
     WHERE table_name='sys_session_state' AND column_name='seguimientos_enviados';
   -- debe devolver 1 fila

   SELECT * FROM sys_leads_para_seguimiento LIMIT 5;
   -- puede devolver vacío (es OK al principio); confirma que la vista existe
   ```

### 2) Main v0.6 — reemplazar el main vivo (10 min)

1. n8n → abrir el workflow `sys-agente-principal` (vivo, v0.5).
2. Hacer backup: menú `⋯` → `Download` → guardar local.
3. **Importar reemplazando:** menú `⋯` → `Import from File` → cargar [sys-agente-principal-v0.6.json](../03_workflows/sys-agente-principal-v0.6.json).
4. n8n te pide resolver credenciales — seleccionar las mismas que tenía v0.5:
   - `Supabase SYS`
   - `OpenAI` (para gpt-4o y formatter mini)
   - `ManyChat - SYS` (id `E41Ucr4mYfSjuoxJ`)
   - `Gmail | la agencia®` (heredado de tools)
5. **Verificación visual:**
   - El nodo `IF skip?` rama no-skip ahora dispara 3 conexiones paralelas: `Build User Message Context`, `Respond to Webhook`, `Update ultima_actividad`.
   - El nodo `sendFlow ManyChat` NO conecta más al `Respond to Webhook` (queda como nodo terminal).
   - Hay un nodo nuevo `Update ultima_actividad` (Postgres) al costado de los otros 2 iniciales.
   - Abrir `Build User Message Context` → en el JS debe aparecer la lógica de `numeroCanal = data.channel === 'wa' ? data.subId : null` y el `lineaNumero` que se inyecta condicional al contexto.
6. **Activar** el workflow (toggle Active).

### 3) Workflow seguimientos — importar nuevo (5 min)

1. n8n → `Workflows` → `Import from File` → cargar [sys-seguimientos-leads-v1.json](../03_workflows/sys-seguimientos-leads-v1.json).
2. Resolver credenciales:
   - `Supabase SYS` (Postgres)
   - `OpenAI la agencia` (reemplazar el placeholder `<<<COMPLETAR_OPENAI_CRED_ID>>>` del nodo `Generar mensaje seguimiento`)
   - `ManyChat - SYS` (los 2 nodos HTTP)
3. **Verificar timezone del workflow:** Settings → Timezone → `America/Argentina/Buenos_Aires` (sino el cron 9-17 corre en UTC y no calza con horario humano AR).
4. **NO activar todavía** — antes hacer smoke test manual (próximo paso).

### 4) Smoke test del workflow seguimientos (10 min)

1. En Supabase Studio, crear lead de prueba (24h vencido, 0 seguimientos):
   ```sql
   INSERT INTO sys_session_state (session_id, etapa, datos_capturados, ultima_actividad, seguimientos_enviados)
   VALUES (
     'wa_smoke_seguimiento_001',
     'diagnostico',
     '{"nombre":"Smoke Test","equipo":"DTF textil"}'::jsonb,
     NOW() - INTERVAL '25 hours',
     0
   )
   ON CONFLICT (session_id) DO UPDATE SET
     ultima_actividad = NOW() - INTERVAL '25 hours',
     seguimientos_enviados = 0,
     etapa = 'diagnostico';
   ```
2. Confirmar que aparece en la vista:
   ```sql
   SELECT * FROM sys_leads_para_seguimiento WHERE session_id = 'wa_smoke_seguimiento_001';
   -- debe devolver 1 fila con toque_a_enviar = 1
   ```
3. En n8n → abrir `sys-seguimientos-leads-v1` → click en `Schedule Trigger` → **Execute Workflow** (ejecuta una sola vez como si fuera el cron).
4. **Verificaciones:**
   - El nodo `Get leads para seguir` devuelve al menos 1 item.
   - El nodo `Generar mensaje seguimiento` produce texto razonable (un mensaje de WA natural).
   - Los nodos `setCustomFields` y `sendFlow` devuelven HTTP 200.
   - El subscriber `2004316097` (o el que estés usando) **recibe un mensaje real de WhatsApp** con el texto generado (si está dentro del 24h window de WA Business).
   - En Supabase:
     ```sql
     SELECT seguimientos_enviados, ultima_actividad FROM sys_session_state WHERE session_id = 'wa_smoke_seguimiento_001';
     -- seguimientos_enviados = 1, ultima_actividad ≈ NOW()

     SELECT * FROM sys_tool_calls WHERE session_id = 'wa_smoke_seguimiento_001' AND tool_name = 'seguimiento_auto';
     -- debe haber 1 fila con status='RESOLVED'
     ```
5. **Smoke test toque 2:** simular 7 días pasados:
   ```sql
   UPDATE sys_session_state
     SET ultima_actividad = NOW() - INTERVAL '8 days'
     WHERE session_id = 'wa_smoke_seguimiento_001';
   ```
   Ejecutar el workflow de nuevo. Verificar que:
   - El mensaje generado tiene tono de "último mensaje".
   - `seguimientos_enviados = 2` y `etapa = 'cerrado'`.
   - El lead ya NO aparece en `sys_leads_para_seguimiento` (porque etapa='cerrado').
6. **Limpiar** el lead de prueba:
   ```sql
   DELETE FROM sys_session_state WHERE session_id = 'wa_smoke_seguimiento_001';
   DELETE FROM sys_tool_calls WHERE session_id = 'wa_smoke_seguimiento_001';
   ```
7. **Activar** el workflow `sys-seguimientos-leads-v1` (toggle Active).

### 5) Google Doc del prompt — aplicar 5 edits (15 min)

Abrir [edits-prompt-mejoras-2026-06-05.md](edits-prompt-mejoras-2026-06-05.md) y seguir los 5 edits en orden:
- EDIT 1: modificar Regla 3.
- EDIT 2: agregar Regla 26 (provincia/localidad).
- EDIT 3: agregar Regla 27 (reconocer "ese número").
- EDIT 4: insertar ETAPA 5.5 (preguntas adicionales).
- EDIT 5: bump header v2.0 → v2.1.

### 6) Sincronizar el backup hardcoded del prompt (5 min)

El nodo `backup` del main contiene una copia hardcoded del prompt. Si se actualiza el Google Doc pero no el backup, cuando Docs falle el AI usa la versión vieja.

1. En el Google Doc actualizado, seleccionar todo el contenido del prompt (sin el header markdown si hay).
2. n8n → abrir `sys-agente-principal-v0.6` → nodo `backup` → campo `value` (assignment).
3. Reemplazar todo el contenido del campo con el del Google Doc.
4. Guardar el workflow.

### 7) Smoke test E2E mejoras prompt (15 min)

Mandar mensajes reales desde WhatsApp al webhook y verificar comportamiento. Ver los 5 casos en [edits-prompt-mejoras-2026-06-05.md → sección Verificación post-edits](edits-prompt-mejoras-2026-06-05.md).

**Caso prioritario para mensajes duplicados (punto 4):**
Hacer 5-10 consultas seguidas que disparen tool calls largos (ej. "necesito una DTF UV grande para imprimir gorras y placas") — esto fuerza al AI Agent a tardar varios segundos. Verificar en `sys_tool_calls`:
```sql
SELECT session_id, tool_name, created_at
  FROM sys_tool_calls
  WHERE session_id = '<tu_session_de_prueba>'
  ORDER BY created_at DESC LIMIT 20;
```
**No deben aparecer 2 invocaciones de la misma tool con timestamps a <2 segundos de diferencia.** Si aparecen, los duplicados persisten — escalar.

---

## Rollback rápido si algo rompe

| Componente | Rollback |
|------------|----------|
| Main v0.6 | Reimportar el JSON downloadeado en el paso 2.2 (v0.5). |
| Workflow seguimientos | Desactivar el toggle Active en n8n. Los leads no reciben follow-ups; el resto del agente sigue funcionando. |
| Schema Supabase | La columna `seguimientos_enviados` y la vista `sys_leads_para_seguimiento` son aditivas — no afectan al resto del sistema si quedan ahí. Si se quiere limpiar: `DROP VIEW sys_leads_para_seguimiento; ALTER TABLE sys_session_state DROP COLUMN seguimientos_enviados;`. |
| Edits prompt | Editar el Google Doc revirtiendo manualmente cada edit (o pegar la versión vieja desde el backup local del paso de aplicación). |

---

## Notas operativas

- **El cron solo corre Lun-Vie 9, 13, 17 ART.** Si un lead deja de responder un sábado, el primer follow-up le llega el lunes 9hs. Aceptable: matchea horario humano del prompt (Regla 8).
- **Costo del LLM por seguimiento:** ~USD 0.001 (gpt-4o-mini, ~500 tokens input + ~80 output). Con volumen bajo (~5-10 leads/día) es despreciable.
- **Mensajes fuera de ventana 24h WhatsApp Business:** si el lead lleva >24h sin interactuar, mandar mensaje out-of-session falla en WhatsApp Business salvo que se use plantilla aprobada. ManyChat puede manejar esto si el subscriber está marcado como suscrito a notificaciones, pero conviene monitorear los primeros días vía `sys_tool_calls`.
- **Pruebas en producción:** la primera semana post-deploy, revisar diariamente la vista `sys_leads_para_seguimiento` y la tabla `sys_tool_calls` filtrada por `tool_name='seguimiento_auto'` para detectar comportamientos no deseados.
- **Migración de infra del cliente (pendiente 1):** este workflow + el schema + el v0.6 se migran junto con el resto cuando creemos las cuentas Airtable/Supabase/n8n del cliente. La estructura es la misma; solo cambian credenciales.
