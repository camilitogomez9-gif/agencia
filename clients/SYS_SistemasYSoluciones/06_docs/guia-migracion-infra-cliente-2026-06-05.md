# Guía de migración de infraestructura a cuentas del cliente (SYS) — 2026-06-05

**Cliente:** Sistemas y Soluciones · **Contacto:** Edgardo · **Ejecuta:** la agencia (+ quien instale n8n en el server del cliente).

**Objetivo:** pasar todo lo que hoy corre en cuentas de la agencia a infraestructura propia del cliente, dejando el agente funcionando igual que hoy. Es el ítem más pesado del cierre. Esta guía es de **alto nivel** (plataformas + pasos generales + chequeos), no un paso-a-paso de cada click.

**Regla de oro:** migrá todo con el sistema viejo **todavía activo**. Lo único que se cambia al final, recién cuando el entorno nuevo pasa el smoke test, es el **webhook de ManyChat**. Así el rollback es instantáneo (volvés a apuntar el webhook al n8n de la agencia).

---

## 1. Qué se migra y qué no

| Plataforma | Hoy | Acción |
|---|---|---|
| **Airtable** `SyS Catalogo` (catálogo/RAG) | Cuenta la agencia | ✅ Migrar a cuenta del cliente |
| **Supabase** (memoria + logs) | Cuenta la agencia | ✅ Migrar a cuenta del cliente |
| **n8n** (main + tools + seguimientos) | Droplet la agencia (`[TU-INSTANCIA-N8N]`) | ✅ Instalar en el server del cliente |
| **Gmail** (notificación de leads) | Credencial la agencia | ✅ Recrear con cuenta del cliente |
| **Google Sheets** (captura de emails) | OAuth la agencia | ✅ Recrear/compartir con cuenta del cliente |
| **OpenAI** (gpt-4o / gpt-4o-mini) | API key la agencia | ⚠️ **Decisión:** el cliente aporta su propia API key, o la agencia mantiene la suya con facturación. Definir con Edgardo. |
| **ManyChat** (WA/IG/FB) | Cuenta del cliente | ⛔ No se toca (ya es del cliente). Solo se repunta el webhook al final. |
| **Telegram** (alertas internas) | Bot la agencia | ⛔ No se migra (es monitoreo interno de la agencia). |

---

## 2. Orden recomendado

1. **Preparar cuentas nuevas** (Airtable, Supabase, server con n8n, Gmail, Google Sheets, OpenAI según decisión).
2. **Recrear datos** en las cuentas nuevas (base Airtable + schema Supabase).
3. **Importar workflows** en el n8n nuevo y **reconectar credenciales**.
4. **Smoke test E2E** en el entorno nuevo (todavía sin tocar el webhook de producción).
5. **Switch:** repuntar el webhook de ManyChat al n8n nuevo.
6. **Monitoreo 48 h.**

---

## 3. Pasos generales por plataforma

### 3.1 Airtable
1. Crear cuenta/workspace del cliente.
2. Replicar la base `SyS Catalogo` (estructura en [`05_crm/airtable-syscatalogo-schema.md`](../05_crm/airtable-syscatalogo-schema.md); ~230 records, 12 tablas). Vía "Duplicate base" o re-import de CSVs.
3. Recrear las **vistas "Para agente"** (las tools filtran por esas vistas).
4. Generar un **PAT nuevo** con scopes `data.records:read` + `data.records:write` + `schema.bases:read`, acceso solo a esa base.
5. Actualizar la credencial n8n `Airtable SYS` con el PAT nuevo.
6. **Repuntar el `Base ID` hardcoded** en los nodos (hoy está hardcodeado, no en variable) — el `Base ID` nuevo es distinto. Ver catálogo de valores hardcoded en [`airtable-credentials.md`](airtable-credentials.md) (gitignored).

### 3.2 Supabase
1. Crear proyecto del cliente (recomendado **región sa-east-1**, free tier alcanza).
2. Ejecutar en el SQL Editor: [`supabase-schema.sql`](supabase-schema.sql) (4 tablas + 3 vistas + función `upsert_session_state`) y luego [`supabase-schema-v2-seguimientos.sql`](supabase-schema-v2-seguimientos.sql) (columna `seguimientos_enviados` + vista `sys_leads_para_seguimiento`).
3. Obtener la connection string usando **Session Pooler** (NO Direct Connection — el server puede no tener IPv6 outbound): `...pooler.supabase.com:5432`.
4. Actualizar la credencial n8n `Supabase SYS` con los datos nuevos y **Ignore SSL Issues = true** (n8n no trae el cert root de Supabase).
5. (Opcional) No hace falta migrar el historial de conversaciones viejo; la memoria se reconstruye sola por sesión.

### 3.3 n8n
1. Instalar n8n en el server que ya tiene el cliente (Docker es lo más simple; mismo esquema que el droplet actual).
2. Importar desde [`03_workflows/`](../03_workflows/): el **main** `sys-agente-principal-v0.6.json`, **todos los sub-workflows de tools** (`sys-tool-*.json`) y el de **seguimientos** `sys-seguimientos-leads-v1.json`.
3. Reconectar las credenciales nuevas en cada nodo (ver sección 4).
4. Verificar que los `workflowId` de los nodos `toolWorkflow` del main apunten a los sub-workflows **ya importados en el n8n nuevo** (los IDs cambian al importar — re-seleccionar cada tool en el main si hace falta).
5. Activar los workflows.

### 3.4 Gmail
1. Crear una credencial OAuth de Gmail con la cuenta Google del cliente.
2. Apuntarla en el nodo de notificación de leads (`notificar_lead`): destino `marketing@sistemasysoluciones.com` (TO) + cc `info@sistemasysoluciones.com`.

### 3.5 Google Sheets
1. Compartir (o transferir) el Sheet de captura de emails "SYS - Leads (Captura Emails)" a la cuenta del cliente — o crear uno nuevo con el mismo header.
2. Crear una credencial OAuth de Google Sheets del cliente y apuntarla en el nodo de la tool `guardar_email`.

### 3.6 OpenAI
- Según la decisión de la sección 1: si el cliente aporta su key, crear la credencial OpenAI con esa key y apuntarla en el nodo AI Agent (+ nodo Formatter gpt-4o-mini). Si la agencia mantiene la suya, no se toca (pero queda como dependencia de la agencia y debe reflejarse en la facturación/mantenimiento).

---

## 4. Reconexión de credenciales en n8n (checklist)

Repuntar en el n8n nuevo, nodo por nodo:

- [ ] `Airtable SYS` → PAT nuevo + Base ID nuevo (hardcoded en nodos).
- [ ] `Supabase SYS` → connection string nueva (Session Pooler, Ignore SSL).
- [ ] Gmail → credencial del cliente.
- [ ] Google Sheets → credencial del cliente + Sheet nuevo/compartido.
- [ ] OpenAI → según decisión.
- [ ] ManyChat (HTTP `setCustomFields`/`sendFlow`) → la credencial/token de ManyChat es del cliente; verificar que siga válida en el n8n nuevo.
- [ ] Revisar **valores hardcoded** (Base ID, URL tienda, mails) nodo por nodo — algunos no están en credenciales sino en el cuerpo de los nodos.

> Los valores reales (PATs, passwords, IDs) están en los docs gitignored [`airtable-credentials.md`](airtable-credentials.md) y [`supabase-credentials.md`](supabase-credentials.md). Generar credenciales **nuevas** para las cuentas del cliente — no reutilizar las de la agencia.

---

## 5. Chequeos finales (dejar todo al 100%)

Con el entorno nuevo armado y **antes** de tocar el webhook de producción:

- [ ] **Smoke test E2E** contra el webhook del n8n nuevo (curl o `scripts/testing/...`): el agente responde y mantiene el tono.
- [ ] **Memoria persistente cross-turn**: mandar 2 mensajes en la misma sesión y verificar que recuerda el contexto (Supabase nuevo).
- [ ] **Tools**: cada tool invoca y loggea en `sys_tool_calls` (Supabase nuevo). Probar al menos `consultar_catalogo`, `consultar_faq`, `guardar_email`, `notificar_lead`.
- [ ] **Mail de lead**: invocar `notificar_lead` y confirmar que llega el mail a `marketing@` (+ cc `info@`) desde la cuenta Gmail del cliente.
- [ ] **Captura de email**: dar un email y confirmar que aparece en el Google Sheet del cliente.

Recién cuando todo lo anterior pasa:

- [ ] **Switch del webhook de ManyChat** a la URL del n8n nuevo del cliente.
- [ ] **Seguimientos**: verificar que el cron de `sys-seguimientos-leads-v1` esté activo en el n8n nuevo.
- [ ] **Monitoreo 48 h** post-switch (revisar `sys_tool_calls` por errores y que lleguen las notificaciones).

---

## 6. Rollback

Si algo falla después del switch: volver a apuntar el **webhook de ManyChat** al n8n de la agencia (`[TU-INSTANCIA-N8N]`). Como la migración se hace con el sistema viejo activo, el rollback es inmediato y sin pérdida de datos.

---

## 7. Referencias

- Arquitectura: [`02_architecture/architecture-v2-2026-05.md`](../02_architecture/architecture-v2-2026-05.md)
- Schema Airtable: [`05_crm/airtable-syscatalogo-schema.md`](../05_crm/airtable-syscatalogo-schema.md)
- Schema Supabase: [`supabase-schema.sql`](supabase-schema.sql) + [`supabase-schema-v2-seguimientos.sql`](supabase-schema-v2-seguimientos.sql)
- Credenciales (gitignored): [`airtable-credentials.md`](airtable-credentials.md) · [`supabase-credentials.md`](supabase-credentials.md)
- Runbook operativo: [`runbook.md`](runbook.md)
- Workflows: [`03_workflows/`](../03_workflows/)
