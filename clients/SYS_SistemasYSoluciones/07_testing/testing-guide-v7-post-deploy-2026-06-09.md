# Testing completo SYS — Post-deploy v0.9 + v2.2 + bugfix Return Output

**Fecha:** 2026-06-09
**Estado del sistema:** Producción activa con v0.9 (main) + v2.2 (prompt) + 3 tools fixeados (`consultar_catalogo-v2`, `guardar_email-v3`, `notificar_lead-v3`).

---

## Estructura

| Fase | Quién corre | Qué prueba | Dónde |
|---|---|---|---|
| **1 — Smoke subflujos** | la agencia | 11 sub-workflows: validate + happy + edge + error | n8n manual con pin data |
| **2 — Smoke AI Agent** | Claude | Capas 1+2+3, ETAPAS, reglas, tool calling, anti-alucinación | curl al webhook con `channel: "test"` |
| **3 — E2E casos borde** | la agencia + cliente | Audio, imagen, mensajes raros, multi-canal | WhatsApp real |

---

# FASE 1 — Smoke tests de subflujos (la agencia en n8n)

Para cada sub-workflow:
1. Abrí el workflow en n8n.
2. Click derecho en `Execute Workflow Trigger` → **Edit Pin Data**.
3. Pegá el JSON de pin data.
4. Click **Execute Workflow**.
5. Inspeccioná el output del `Return Output` final.
6. Verificá assertion (qué debería devolver).

**Output esperado universal:**
```json
{
  "status": "RESOLVED" | "NOT_FOUND" | "ERROR" | "AMBIGUOUS",
  "data": { ... } | null,
  "message_to_agent": "...",
  "trace_id": "<execution id>"
}
```

⚠️ **Si ves `{success: true}` en el Return Output, es bug del Postgres Log no fixeado** — re-importá el v2/v3 correspondiente.

---

## ⚠️ Qué simula el pin data

El pin data simula lo que **llega al `Execute Workflow Trigger`** del sub-workflow — que es lo que el `$fromAI()` del nodo `toolWorkflow` del main **extrajo** del razonamiento del LLM. **NO es el mensaje del cliente**.

Por ejemplo, si el cliente escribe *"hola, ¿qué impresoras HUENU tienen para UV?"*, el LLM razona, llama la tool `consultar_catalogo`, y el `$fromAI('query', ...)` extrae algo como `"HUENU UV"` o `"impresoras HUENU UV"` — eso es lo que llega al Trigger.

Cada caso lo marco con:
- **(realista)** — lo que el LLM bien-prompteado pasaría en producción.
- **(defensivo)** — input que el LLM **no debería** pasar, pero el sub-workflow tiene que manejarlo sin romper (validación, NOT_FOUND, ERROR). Cubre regresiones por bugs del prompt o por mala interpretación del LLM.

---

## 1.1 — `consultar_catalogo-v2` (workflowId `oQtLMujJBHlxZTTJ`)

Descripción del `$fromAI('query', ...)`: *"Texto natural del cliente sobre catalogo equipos aplicaciones o inventario refurbished. Pasa el mensaje literal o un resumen breve."*

### Caso 1.1.A — Happy intent=equipo (realista)
```json
{
  "query": "HUENU UV",
  "session_id": "smoke_catalogo_001"
}
```
**Esperado:** `status: "RESOLVED"`, `data.intent: "equipo"`, `data.items[]` con al menos `HR 6004 DU` o `HR 1602 SU` o `HR 3208 UV`, cada uno con `modelo`, `marca: "HUENU"`, `tecnologia` que incluya "UV".

### Caso 1.1.B — Happy intent=aplicacion (realista)
```json
{
  "query": "gorras",
  "session_id": "smoke_catalogo_002"
}
```
**Esperado:** `status: "RESOLVED"`, `data.intent: "aplicacion"`, `data.items[]` con tecnologías sugeridas (DTF UV / Sublimación). Si devuelve NOT_FOUND, la tabla Aplicaciones de Airtable no tiene "gorras" cargado — anotar como pendiente.

### Caso 1.1.C — Happy intent=inventario (realista)
```json
{
  "query": "BIZHUB Konica refurbished",
  "session_id": "smoke_catalogo_003"
}
```
**Esperado:** `status: "RESOLVED"`, `data.intent: "inventario"`, `data.items[]` con modelos tipo `BIZHUB C450i / BIZHUB 558E / Acurio Press C3080 / BIZHUB C224`.

### Caso 1.1.D — Happy intent=equipo con frase más larga (realista)
```json
{
  "query": "impresoras DTF textil ancho 60cm",
  "session_id": "smoke_catalogo_004"
}
```
**Esperado:** `status: "RESOLVED"`, `data.intent: "equipo"`, items DTF Textil. Verifica que el Classify Intent del sub-workflow maneje frases con specs incluidas.

### Caso 1.1.E — NOT_FOUND (defensivo)
```json
{
  "query": "xyzabc123",
  "session_id": "smoke_catalogo_005"
}
```
**Esperado:** `status: "NOT_FOUND"`, `message_to_agent` indica que no hay match. El LLM bien-prompteado no pasaría algo así, pero el sub-workflow no debe crashear.

### Caso 1.1.F — Edge: query vacía (defensivo)
```json
{
  "query": "",
  "session_id": "smoke_catalogo_006"
}
```
**Esperado:** `status: "NOT_FOUND"` con `message_to_agent` legible (NO crash, NO `{success:true}`). El LLM no debería pasar query vacía, pero el sub-workflow debe degradar.

---

## 1.2 — `consultar_tecnologia-v1`

`tecnologia` es ENUM cerrado. El LLM debería pasar el valor **exacto** de: `DTF Textil | DTF UV | UV | Sublimación | Eco-Solvente | Solvente | RISO | IDL Láser | Gran Formato | Corte`.

### Caso 1.2.A — Happy DTF Textil sin aspecto (realista)
```json
{
  "tecnologia": "DTF Textil",
  "aspecto": "",
  "session_id": "smoke_tecno_001"
}
```
**Esperado:** `status: "RESOLVED"`, `data` con descripción + materiales + aplicaciones + restricciones (ficha completa).

### Caso 1.2.B — Happy UV aspecto=materiales (realista)
```json
{
  "tecnologia": "UV",
  "aspecto": "materiales",
  "session_id": "smoke_tecno_002"
}
```
**Esperado:** `status: "RESOLVED"`, `data` enfocado en sustratos compatibles UV.

### Caso 1.2.C — Happy Sublimación aspecto=aplicaciones (realista)
```json
{
  "tecnologia": "Sublimación",
  "aspecto": "aplicaciones",
  "session_id": "smoke_tecno_003"
}
```
**Esperado:** `status: "RESOLVED"`, `data` con aplicaciones (textil, mug, taza, etc.).

### Caso 1.2.D — NOT_FOUND (defensivo: valor fuera del ENUM)
```json
{
  "tecnologia": "Holografía 3D",
  "aspecto": "",
  "session_id": "smoke_tecno_004"
}
```
**Esperado:** `status: "NOT_FOUND"`. El LLM bien-prompteado no debería pasar valores fuera del ENUM, pero el sub-workflow debe responder limpio.

### Caso 1.2.E — Naming sin tilde (defensivo: regresión de variantes)
```json
{
  "tecnologia": "Sublimacion",
  "aspecto": "",
  "session_id": "smoke_tecno_005"
}
```
**Esperado:** Si la tabla solo tiene `"Sublimación"`, devuelve `NOT_FOUND`. Si tiene normalización por slug, devuelve `RESOLVED`. Anotar comportamiento — útil para entender si el LLM puede romper con tildes.

---

## 1.3 — `consultar_aplicacion-v1`

`descripcion` es texto libre (el LLM extrae lo que el cliente quiere hacer); `sustrato_mencionado` es opcional.

### Caso 1.3.A — Happy wrap vehicular (realista)
```json
{
  "descripcion": "wrap vehicular",
  "sustrato_mencionado": "",
  "session_id": "smoke_aplic_001"
}
```
**Esperado:** `status: "RESOLVED"`, tecnologías recomendadas (UV o Eco-Solvente).

### Caso 1.3.B — Happy banderas con sustrato (realista)
```json
{
  "descripcion": "banderas",
  "sustrato_mencionado": "tela",
  "session_id": "smoke_aplic_002"
}
```
**Esperado:** `status: "RESOLVED"`, tecnología sugerida = Sublimación.

### Caso 1.3.C — Happy cartelería exterior (realista)
```json
{
  "descripcion": "cartelería exterior gran formato",
  "sustrato_mencionado": "",
  "session_id": "smoke_aplic_003"
}
```
**Esperado:** `status: "RESOLVED"`, tecnología sugerida = Gran Formato / Eco-Solvente.

### Caso 1.3.D — NOT_FOUND (defensivo)
```json
{
  "descripcion": "billetes falsos",
  "sustrato_mencionado": "",
  "session_id": "smoke_aplic_004"
}
```
**Esperado:** `status: "NOT_FOUND"`. El sub-workflow no entra en juicios de valor — solo busca match.

---

## 1.4 — `consultar_compatibilidad-v1`

`tipo_consulta` es ENUM (`equipo_sustrato | equipo_tinta | equipo_cabezal`); `equipo` es modelo concreto del catálogo; `elemento` es el sustrato/tinta/cabezal a verificar.

### Caso 1.4.A — Happy equipo_sustrato (realista)
```json
{
  "tipo_consulta": "equipo_sustrato",
  "equipo": "HR 6004 DU",
  "elemento": "vidrio",
  "session_id": "smoke_compat_001"
}
```
**Esperado:** `status: "RESOLVED"`, `data.compatible` boolean o `"depende"`, `data.equipo_referencia: "HR 6004 DU"`.

### Caso 1.4.B — Happy equipo_tinta (realista)
```json
{
  "tipo_consulta": "equipo_tinta",
  "equipo": "HR 1602 SU",
  "elemento": "tinta sublimación",
  "session_id": "smoke_compat_002"
}
```
**Esperado:** `status: "RESOLVED"`, `data.compatible: "depende"`, `message_to_agent` derivá a comercial.

### Caso 1.4.C — Happy equipo_cabezal (realista)
```json
{
  "tipo_consulta": "equipo_cabezal",
  "equipo": "HR 6004 DU",
  "elemento": "Ricoh Gen5",
  "session_id": "smoke_compat_003"
}
```
**Esperado:** `status: "RESOLVED"`, `data` con info del cabezal del equipo.

### Caso 1.4.D — NOT_FOUND equipo inexistente (defensivo)
```json
{
  "tipo_consulta": "equipo_sustrato",
  "equipo": "Mimaki UJF",
  "elemento": "vidrio",
  "session_id": "smoke_compat_004"
}
```
**Esperado:** `status: "NOT_FOUND"`, `message_to_agent`: "No encontré el equipo 'Mimaki UJF' en el catálogo...". SyS no comercializa Mimaki, el sub-workflow debe degradar limpio.

### Caso 1.4.E — Regresión bug DTF (defensivo)
```json
{
  "tipo_consulta": "equipo_sustrato",
  "equipo": "DTF",
  "elemento": "vidrio",
  "session_id": "smoke_compat_005"
}
```
**Esperado:** `status: "NOT_FOUND"` (porque "DTF" no matchea ningún `Modelo` en la tabla Equipos — es una tecnología, no un modelo). El LLM bien-prompteado debería usar `consultar_tecnologia`, no `consultar_compatibilidad`. Regresión del bug reportado el 2026-06-09.

---

## 1.5 — `consultar_faq-v1`

Descripción de `pregunta_usuario`: *"OBLIGATORIO: texto literal de la pregunta del cliente"*. Acá el LLM SÍ transcribe lo que el cliente preguntó, ese es el contrato. `categoria_hint` es ENUM opcional.

### Caso 1.5.A — Happy financiación (realista)
```json
{
  "pregunta_usuario": "¿manejan financiación?",
  "categoria_hint": "Financiación",
  "session_id": "smoke_faq_001"
}
```
**Esperado:** `status: "RESOLVED"`, `data` con respuesta sobre planes de financiación.

### Caso 1.5.B — Happy showroom (realista)
```json
{
  "pregunta_usuario": "¿puedo ir al showroom a ver los equipos?",
  "categoria_hint": "Showroom",
  "session_id": "smoke_faq_002"
}
```
**Esperado:** `status: "RESOLVED"`, ubicación + horarios del showroom.

### Caso 1.5.C — Happy servicio técnico sin hint (realista)
```json
{
  "pregunta_usuario": "se me rompió la impresora, ¿reparan?",
  "categoria_hint": "",
  "session_id": "smoke_faq_003"
}
```
**Esperado:** `status: "RESOLVED"`, debe mencionar 4342-5742. Verifica que el matching funcione sin `categoria_hint`.

### Caso 1.5.D — Happy distribuidores (realista)
```json
{
  "pregunta_usuario": "¿qué condiciones tienen para distribuidores?",
  "categoria_hint": "Distribuidores",
  "session_id": "smoke_faq_004"
}
```
**Esperado:** `status: "RESOLVED"`, info de condiciones distribuidor.

### Caso 1.5.E — NOT_FOUND (defensivo)
```json
{
  "pregunta_usuario": "¿venden autos?",
  "categoria_hint": "Otros",
  "session_id": "smoke_faq_005"
}
```
**Esperado:** `status: "NOT_FOUND"`. El sub-workflow no debe inventar.

---

## 1.6 — `consultar_lineas_priorizadas-v1`

### Caso 1.6.A — Happy
```json
{
  "session_id": "smoke_lineas_001"
}
```
**Esperado:** `status: "RESOLVED"`, lista de líneas priorizadas del mes. Si la tabla está vacía, devuelve `NOT_FOUND` o lista vacía con `message_to_agent` aclarándolo.

---

## 1.7 — `consultar_url_tienda-v1`

`producto` es texto libre opcional; `categoria` es ENUM opcional (`TINTAS | FILM | POLVO | Vinilo | Papel transfer | Otros`).

### Caso 1.7.A — Happy con producto + categoría (realista)
```json
{
  "producto": "tinta UV",
  "categoria": "TINTAS",
  "session_id": "smoke_tienda_001"
}
```
**Esperado:** `status: "RESOLVED"`, `data.url_tienda`, `data.url_categoria` apuntando a `sistemasysoluciones.com`.

### Caso 1.7.B — Happy solo categoría (realista)
```json
{
  "producto": "",
  "categoria": "FILM",
  "session_id": "smoke_tienda_002"
}
```
**Esperado:** `status: "RESOLVED"`, URL de la categoría FILM.

### Caso 1.7.C — Happy solo producto sin categoría (realista)
```json
{
  "producto": "polvo DTF",
  "categoria": "",
  "session_id": "smoke_tienda_003"
}
```
**Esperado:** `status: "RESOLVED"`, URL del producto o categoría POLVO.

### Caso 1.7.D — Fallback ambos vacíos (defensivo)
```json
{
  "producto": "",
  "categoria": "",
  "session_id": "smoke_tienda_004"
}
```
**Esperado:** `status: "RESOLVED"`, URL raíz de la tienda. El LLM bien-prompteado debería pasar al menos uno, pero el sub-workflow debe responder con la home.

---

## 1.8 — `consultar_inventario_usados-v1`

⚠️ **NO está cableado al main v0.9.** Después del refactor nuclear (2026-06-03) la funcionalidad de inventario se consolidó dentro de `consultar_catalogo` (intent=inventario). Estos casos son test aislado de la tool por si se reconecta.

### Caso 1.8.A — Happy modelo específico (realista si reconectada)
```json
{
  "modelo": "BIZHUB C450i",
  "session_id": "smoke_invent_001"
}
```
**Esperado:** `status: "RESOLVED"`, `data` con disponibilidad + contador copias si aplica.

### Caso 1.8.B — Happy búsqueda parcial (realista)
```json
{
  "modelo": "Acurio Press",
  "session_id": "smoke_invent_002"
}
```
**Esperado:** `status: "RESOLVED"`, lista de modelos Acurio.

### Caso 1.8.C — NOT_FOUND marca no comercializada (defensivo)
```json
{
  "modelo": "Canon ImageRunner",
  "session_id": "smoke_invent_003"
}
```
**Esperado:** `status: "NOT_FOUND"`.

---

## 1.9 — `buscar_equipo-v1`

⚠️ **NO está cableado al main v0.9.** Igual que `consultar_inventario_usados`, su funcionalidad se consolidó en `consultar_catalogo` (intent=equipo) después del refactor nuclear. Test aislado por si se reconecta.

### Caso 1.9.A — Happy búsqueda libre (realista si reconectada)
```json
{
  "query_libre": "DTF textil",
  "tecnologia": "DTF Textil",
  "linea": "",
  "aplicacion": "",
  "ancho_min_mm": null,
  "ancho_max_mm": null,
  "zona_cliente": "CABA",
  "session_id": "smoke_busc_001"
}
```
**Esperado:** `status: "RESOLVED"`, equipo principal + alternativas.

### Caso 1.9.B — Happy filtro por ancho (realista)
```json
{
  "query_libre": "",
  "tecnologia": "UV",
  "linea": "",
  "aplicacion": "",
  "ancho_min_mm": 1500,
  "ancho_max_mm": 2500,
  "zona_cliente": "CABA",
  "session_id": "smoke_busc_002"
}
```
**Esperado:** `status: "RESOLVED"`, equipos UV con ancho 1500-2500mm.

### Caso 1.9.C — NOT_FOUND tecnología fuera del catálogo (defensivo)
```json
{
  "query_libre": "",
  "tecnologia": "Holografía 3D",
  "linea": "",
  "aplicacion": "",
  "ancho_min_mm": null,
  "ancho_max_mm": null,
  "zona_cliente": "",
  "session_id": "smoke_busc_003"
}
```
**Esperado:** `status: "NOT_FOUND"`.

---

## 1.10 — `guardar_email-v3` (workflowId `v9HD7P2uroG4Ni3A`)

Todos los args (email, nombre, telefono, aplicacion_interes, origen) los **extrae el LLM** del contexto de la conversación. `canal`, `subscriber_id`, `session_id` los inyecta el main desde `Normalize Payload` — son contexto técnico, no contexto del LLM.

### Caso 1.10.A — Happy nuevo email (realista)
```json
{
  "email": "smoketest1@[TU-DOMINIO]",
  "nombre": "Smoke Test 1",
  "telefono": "1131345321",
  "aplicacion_interes": "DTF textil",
  "origen": "newsletter",
  "canal": "WhatsApp",
  "subscriber_id": "smoke_001",
  "session_id": "smoke_email_001"
}
```
**Esperado:** `status: "RESOLVED"`, `data.already_exists: false`, `data.email: "smoketest1@[TU-DOMINIO]"`, `message_to_agent` confirma el guardado. **Verificá en Google Sheets:** fila nueva en pestaña Emails. **Verificá en Supabase:** `SELECT datos_capturados FROM sys_session_state WHERE session_id = 'smoke_email_001'` → debe contener `{"mail": "smoketest1@[TU-DOMINIO]"}`.

### Caso 1.10.B — Happy solo email (realista, args opcionales en blanco)
```json
{
  "email": "smoketest2@[TU-DOMINIO]",
  "nombre": "",
  "telefono": "",
  "aplicacion_interes": "",
  "origen": "",
  "canal": "Instagram",
  "subscriber_id": "smoke_002",
  "session_id": "smoke_email_002"
}
```
**Esperado:** `status: "RESOLVED"`, `data.already_exists: false`. Guarda el email aunque los opcionales vengan vacíos. El cliente puede dar solo el email sin más contexto.

### Caso 1.10.C — Happy email duplicado (realista)
```json
{
  "email": "smoketest1@[TU-DOMINIO]",
  "nombre": "Smoke Test 1",
  "telefono": "1131345321",
  "aplicacion_interes": "",
  "origen": "newsletter",
  "canal": "WhatsApp",
  "subscriber_id": "smoke_001",
  "session_id": "smoke_email_001"
}
```
**Esperado:** `status: "RESOLVED"`, `data.already_exists: true`, NO duplica en Sheets pero SÍ updatea `datos_capturados` en Supabase. Correr DESPUÉS de 1.10.A para que ya esté en Sheets.

### Caso 1.10.D — Error email malformado (defensivo)
```json
{
  "email": "no-es-un-email",
  "nombre": "",
  "telefono": "",
  "aplicacion_interes": "",
  "origen": "",
  "canal": "WhatsApp",
  "subscriber_id": "smoke_003",
  "session_id": "smoke_email_003"
}
```
**Esperado:** `status: "ERROR"`, `data: null`, `message_to_agent` indica formato inválido, `trace_id` presente. ✅ Si ves `{success:true}` o crudo del Validate, no se importó v3. El LLM bien-prompteado no llamaría con email malformado (Regla 26), test defensivo.

### Caso 1.10.E — Error email vacío (defensivo)
```json
{
  "email": "",
  "nombre": "Sin Email",
  "telefono": "1131345321",
  "aplicacion_interes": "",
  "origen": "",
  "canal": "WhatsApp",
  "subscriber_id": "smoke_004",
  "session_id": "smoke_email_004"
}
```
**Esperado:** `status: "ERROR"`, message_to_agent: "Faltó el email...". El LLM no debería llamar sin email (Regla 26), test defensivo. ✅ Si pasa los 4 fixes, devuelve shape estándar.

---

## 1.11 — `notificar_lead-v3` (workflowId `QI1gO4dZ5vXXo7V3`)

Los 4 args obligatorios (`nombre`, `telefono`, `ubicacion`, `equipo_o_aplicacion`) más los opcionales (`mail`, `empresa`, `perfil`, `urgencia`, `notas`, `tecnologia_interes`) los **extrae el LLM** del contexto. `canal`, `subscriber_id`, `session_id` los inyecta el main desde `Normalize Payload`. Las Reglas operativas 2 y 22 del prompt obligan al LLM a tener los 4 obligatorios antes de llamar.

### Caso 1.11.A — Happy completo con mail (realista)
```json
{
  "nombre": "Federico Vizcarra",
  "telefono": "1131345321",
  "ubicacion": "San Miguel",
  "equipo_o_aplicacion": "DTF Textil",
  "mail": "fede.smoketest@[TU-DOMINIO]",
  "empresa": "",
  "perfil": "Pyme",
  "urgencia": "false",
  "notas": "",
  "tecnologia_interes": "DTF Textil",
  "subscriber_id": "smoke_lead_001",
  "canal": "WhatsApp",
  "session_id": "smoke_lead_001"
}
```
**Esperado:**
- `status: "RESOLVED"`, `data.mail_enviado: true`, `data.live_chat_url` o `null`, `message_to_agent` confirma derivación.
- **Mail a `marketing@sistemasysoluciones.com`** con cc a `info@`. Avisale a Edgardo que es smoke test.
- **Supabase:** `SELECT etapa, datos_capturados FROM sys_session_state WHERE session_id = 'smoke_lead_001'` → `etapa: 'derivado'`, `datos_capturados` con los 4 obligatorios + mail.
- **ManyChat:** llama a `sendFlow` asignando a Jimena — si el `subscriber_id` no existe en ManyChat, falla silenciosamente (continueOnFail), no debería romper el flujo.

### Caso 1.11.B — Happy solo obligatorios sin mail (realista)
```json
{
  "nombre": "María López",
  "telefono": "1199887766",
  "ubicacion": "CABA",
  "equipo_o_aplicacion": "Sublimación",
  "mail": "",
  "empresa": "",
  "perfil": "",
  "urgencia": "false",
  "notas": "",
  "tecnologia_interes": "",
  "subscriber_id": "smoke_lead_002",
  "canal": "Instagram",
  "session_id": "smoke_lead_002"
}
```
**Esperado:** `status: "RESOLVED"` (mail es opcional, no bloqueante por Regla 3 del prompt). Mail llega sin la línea de email del lead.

### Caso 1.11.C — Happy distribuidor urgente (realista)
```json
{
  "nombre": "Juan Distribuidor",
  "telefono": "1166778899",
  "ubicacion": "Córdoba",
  "equipo_o_aplicacion": "línea HUENU UV completa",
  "mail": "juan.dist.smoketest@[TU-DOMINIO]",
  "empresa": "Gráfica del Centro SA",
  "perfil": "Distribuidor",
  "urgencia": "true",
  "notas": "Quiere condiciones por volumen",
  "tecnologia_interes": "UV",
  "subscriber_id": "smoke_lead_003",
  "canal": "WhatsApp",
  "session_id": "smoke_lead_003"
}
```
**Esperado:** `status: "RESOLVED"`. El mail al CM debería destacar `perfil: Distribuidor` + `urgencia: true` + notas.

### Caso 1.11.D — Error falta nombre (defensivo)
```json
{
  "nombre": "",
  "telefono": "1131345321",
  "ubicacion": "CABA",
  "equipo_o_aplicacion": "DTF Textil",
  "mail": "",
  "empresa": "",
  "perfil": "",
  "urgencia": "false",
  "notas": "",
  "tecnologia_interes": "",
  "subscriber_id": "smoke_lead_004",
  "canal": "WhatsApp",
  "session_id": "smoke_lead_004"
}
```
**Esperado:** `status: "ERROR"`, `data: null`, `message_to_agent`: "Faltan datos obligatorios...". ✅ Si ves crudo del Validate, no se importó v3. El LLM no debería llamar sin nombre (Regla 2), test defensivo.

### Caso 1.11.E — Error falta teléfono (defensivo)
```json
{
  "nombre": "Sin Tel",
  "telefono": "",
  "ubicacion": "CABA",
  "equipo_o_aplicacion": "UV",
  "mail": "",
  "empresa": "",
  "perfil": "",
  "urgencia": "false",
  "notas": "",
  "tecnologia_interes": "",
  "subscriber_id": "smoke_lead_005",
  "canal": "Instagram",
  "session_id": "smoke_lead_005"
}
```
**Esperado:** `status: "ERROR"`.

### Caso 1.11.F — Error falta ubicación (defensivo)
```json
{
  "nombre": "Sin Zona",
  "telefono": "1131345321",
  "ubicacion": "",
  "equipo_o_aplicacion": "Sublimación",
  "mail": "",
  "empresa": "",
  "perfil": "",
  "urgencia": "false",
  "notas": "",
  "tecnologia_interes": "",
  "subscriber_id": "smoke_lead_006",
  "canal": "Facebook",
  "session_id": "smoke_lead_006"
}
```
**Esperado:** `status: "ERROR"`.

### Caso 1.11.G — Error falta equipo/aplicación (defensivo)
```json
{
  "nombre": "Sin Equipo",
  "telefono": "1131345321",
  "ubicacion": "Quilmes",
  "equipo_o_aplicacion": "",
  "mail": "",
  "empresa": "",
  "perfil": "",
  "urgencia": "true",
  "notas": "",
  "tecnologia_interes": "",
  "subscriber_id": "smoke_lead_007",
  "canal": "WhatsApp",
  "session_id": "smoke_lead_007"
}
```
**Esperado:** `status: "ERROR"`.

---

## 1.12 — Cleanup post-Fase 1

```sql
-- Borrar todas las filas smoke
DELETE FROM sys_session_state WHERE session_id LIKE 'smoke_%';
DELETE FROM sys_tool_calls    WHERE session_id LIKE 'smoke_%';
DELETE FROM n8n_chat_histories WHERE session_id LIKE 'smoke_%';
```

Y en Google Sheets pestaña Emails: borrar manualmente las filas con `smoketest*@[TU-DOMINIO]`.

---

# FASE 2 — Smoke tests del AI Agent (Claude vía curl)

## Setup

**Webhook URL:** `https://[TU-INSTANCIA-N8N]/webhook/sys-agent`
**Method:** POST
**Auth:** headerAuth con credential `Webhook SYS Inbound` (id `UnA18VVz7bSrSUNX`).
**Trigger del modo test:** `channel: "test"` en el body — el `IF channel test?` enruta a `Respond Test (con body)` que devuelve un JSON con `ai_msg_1`, `ai_msg_2`, `ai_msg_3` parseados.

⚠️ **Necesito de vos**:
1. El **header name** del webhook auth (probablemente `key` o `x-api-key` — del pinData de v0.9 aparece `"key": "3d20a948..."`).
2. El **valor del secret** (no está en el repo, vive en la credential de n8n).

Pasámelos en el próximo mensaje y disparo los 17 casos.

Body template:
```json
{
  "subscriber_id": "test_<id_único>",
  "channel": "test",
  "last_input_text": "<mensaje del lead>",
  "first_name": "Test"
}
```

Antes de cada caso, limpieza por sesión:
```sql
DELETE FROM n8n_chat_histories WHERE session_id = 'test_test_<id_único>';
DELETE FROM sys_session_state    WHERE session_id = 'test_test_<id_único>';
DELETE FROM sys_tool_calls       WHERE session_id = 'test_test_<id_único>';
```

(sessionKey = `channel_subscriberId` = `test_test_<id>`)

---

## 2.1 — Capa 1+2+3 del fix re-saludo/re-pregunta (casos A–I del plan)

| # | Caso | Setup | Mensaje | Esperado | Assert SQL |
|---|---|---|---|---|---|
| **A** | Turno 1 limpio | (state vacío) | `"Hola"` | Saluda y se presenta como asistente. Etapa queda `bienvenida`. | `SELECT etapa FROM sys_session_state WHERE session_id='test_test_A'` → `bienvenida` |
| **B** | Turno 2 sin re-saludo | Después de A | `"Necesito un equipo DTF"` | NO contiene "Hola", "bienvenido", "soy el asistente". | `respuesta.ai_msg_1` no matchea esos términos |
| **C** | State pre-populado | `INSERT INTO sys_session_state (session_id, etapa, datos_capturados) VALUES ('test_test_C', 'captura', '{"nombre":"Federico","telefono":"1131345321"}')` | `"Soy de San Miguel"` | Reconoce a Federico, NO re-pregunta nombre/teléfono, pide equipo o cierra. | respuesta no contiene "nombre", "teléfono" como pregunta |
| **D** | Dump multi-dato | (vacío) | `"Soy Federico Vizcarra 1131345321 san Miguel, me interesa una DTF"` | El Parse detecta nombre+tel+zona. Datos quedan en state. Agente reconoce. | `datos_capturados` contiene `{"nombre":"Federico Vizcarra","telefono":"1131345321","ubicacion":"San Miguel"}` |
| **E** | Email aislado | (vacío) | `"mi mail es fede@gmail.com"` | Parse detecta email + agente invoca `guardar_email`. Próxima respuesta no re-pide mail. | `datos_capturados.mail = 'fede@gmail.com'`, `sys_tool_calls` tiene row `guardar-email` con `status='success'` |
| **F** | Tel oficina ignorado | (vacío) | `"Llamo al 4342-5742?"` | Parse NO captura ese teléfono. Agente responde con la info de oficina. | `datos_capturados` sin `telefono` |
| **G** | Memoria contaminada | Forzar 5 turnos viejos con `[CONTEXTO TURNO] Etapa: bienvenida / Datos: {}` en `n8n_chat_histories` + ahora pre-popular state con `{"nombre":"Ana"}`. | `"Necesito info de tintas"` | Agente prioriza el state fresco, NO re-saluda. | respuesta sin "Hola, bienvenido" |
| **H** | Conversación larga >20 turnos | Simular 22 turnos previos. | `"Te paso mi mail: ana@example.com"` | Aunque la ventana de 20 ya rotó, datos persistidos en `sys_session_state` sostienen el comportamiento. | `datos_capturados.mail` presente |
| **I** | Reset memoria, state intacto | `DELETE FROM n8n_chat_histories WHERE session_id='test_test_I'` pero state con `{"nombre":"Pedro","telefono":"1199887766","ubicacion":"CABA","equipo_interes":"DTF"}`. | `"hola necesito cotizar"` | Reconoce a Pedro, no re-pregunta los 4 datos, invoca `notificar_lead`. | `sys_tool_calls` con `notificar-lead` |

---

## 2.2 — ETAPAS 1-6 del prompt

| # | ETAPA | Mensaje | Esperado |
|---|---|---|---|
| 10 | ETAPA 1 bienvenida | `"Hola"` | Saludo + presentación + pregunta abierta. |
| 11 | ETAPA 2 distribuidor | `"Soy distribuidor, quiero condiciones comerciales"` | Reconoce perfil distribuidor, hace UNA pregunta de contexto (líneas o zona) — no pide diagnóstico técnico. |
| 12 | ETAPA 2 emprendedor | `"Estoy empezando un emprendimiento de remeras"` | Reconoce emprendedor, asesora desde cero con paciencia. |
| 13 | ETAPA 3 diagnóstico | `"Quiero imprimir camisetas, unas 200 por día, en CABA"` | Hace UNA pregunta a la vez (tipo de trabajo / sustrato / tamaño / volumen — el siguiente que falte). |
| 14 | ETAPA 4 asesoramiento | `"Quiero saber la diferencia entre DTF y UV"` | Explica con analogía/ejemplo. Invoca `consultar_tecnologia` (verificable en `sys_tool_calls`). |
| 15 | ETAPA 5 captura | Después de varios turnos previos llegando a derivación: `"Sí, mandame con un comercial"` | Pide nombre + teléfono + ubicación + equipo en orden. |
| 16 | ETAPA 6 cierre con mail | Después de captura completa + mail: `"<mail>@gmail.com"` | Invoca `notificar_lead`. Cierra con calidez. NO menciona descuento. |
| 17 | ETAPA 6 cierre sin mail | Captura completa sin mail | Ofrece pedir mail con la frase de Regla 4: `"Si querés, te mando más información sobre los equipos que consultaste. ¿Me pasás tu mail?"`. NO menciona descuento. |

---

## 2.3 — Reglas operativas críticas

| # | Regla | Mensaje | Esperado |
|---|---|---|---|
| 18 | 1 — NUNCA precios | `"¿cuánto sale la HR 6004 DU?"` | NO da precio. Deriva a comercial. |
| 19 | 4 — pedido de mail (sin descuento) | (en contexto de derivación, sin mail capturado) `"sí, mandame info"` | Usa la frase exacta SIN mención de descuento. |
| 20 | 10 — UNA pregunta por turno | `"Quiero un equipo DTF"` | NO hace dos preguntas (ej: "¿qué sustrato? ¿cuántas prendas?"). Solo una. |
| 21 | 13 — dump derivado inmediato | `"Soy Marta López, 1199887766, CABA, necesito DTF cotización"` | NO continúa diagnóstico. Invoca `notificar_lead` o pide el dato faltante (mail). |
| 22 | 16 — equipos vs servicio impresión | `"¿cuánto me sale imprimir 100 stickers?"` | Aclara que SyS vende equipos, no servicio. Sugiere ver equipos. |
| 23 | 17 — servicio técnico | `"mi impresora se rompió"` | Redirige a 4342-5742. |
| 24 | 18 — teléfono del chat | `"podés usar el teléfono por el que te estoy hablando?"` | Pide que lo escriba en el chat (NO usa el subId implícito). |
| 25 | 20 — no repetir tecnología | (turno 2 después de "Quiero DTF") `"qué velocidad maneja?"` | NO re-explica qué es DTF. Va directo a velocidad. |
| 26 | 21 — cotización directa | `"Quiero presupuesto de una DTF"` (primer mensaje) | Pide nombre+tel+ubicación SIN diagnóstico. |
| 27 | 26 — `guardar_email` solo con email explícito | `"Hola, soy Maria 1111111111 zona oeste"` (sin email) | NO invoca `guardar_email`. Verificable en `sys_tool_calls`. |
| 28 | Anti-precio interno | `"esto cuesta menos que el competidor?"` | NO compara precios. Deriva. |

---

## 2.4 — Tool calling correcto

| # | Caso | Mensaje | Tool esperada | Assert |
|---|---|---|---|---|
| 29 | Pregunta técnica → `consultar_tecnologia` | `"¿qué es DTF UV?"` | `consultar_tecnologia` con `tecnologia: "DTF UV"` | `sys_tool_calls.tool_name = 'consultar-tecnologia'` |
| 30 | Aplicación concreta → `consultar_catalogo` o `consultar_aplicacion` | `"¿qué necesito para imprimir gorras?"` | `consultar_catalogo` (intent=aplicacion) | `sys_tool_calls` con esa row |
| 31 | Compatibilidad modelo+sustrato → `consultar_compatibilidad` | `"este HR 6004 DU imprime sobre vidrio?"` | `consultar_compatibilidad` | row presente |
| 32 | FAQ financiación → `consultar_faq` | `"manejan financiación en cuotas?"` | `consultar_faq` | row presente |
| 33 | Insumos → `consultar_url_tienda` | `"dónde compro tinta?"` | `consultar_url_tienda` | row presente + URL en respuesta |
| 34 | Catálogo equipos → `consultar_catalogo` | `"qué impresoras HUENU UV tienen?"` | `consultar_catalogo` (intent=equipo) | row presente con `data.items[]` |
| 35 | NO tool si no aplica | `"hola buenas tardes"` | Ningún tool call | `sys_tool_calls` sin entrada en ese turno |

---

## 2.5 — Anti-alucinación

| # | Caso | Mensaje | Esperado |
|---|---|---|---|
| 36 | Precio inventado | `"¿la HR 6004 DU sale 5000 dólares?"` | NO confirma. NO da otro precio. Deriva a comercial. |
| 37 | Modelo inexistente | `"tienen la HUENU MEGA UV 9999?"` | Invoca `consultar_catalogo`, recibe NOT_FOUND, dice "Dejame verificar" o deriva. |
| 38 | Plazo de entrega | `"¿en cuánto me llega?"` | NO promete plazo. Deriva. |
| 39 | Stock | `"¿hay stock de la HR 1602 SU?"` | NO confirma stock. Deriva. |
| 40 | Comparación con competencia | `"es mejor que Roland?"` | Responde sin denigrar la competencia, usa autoridad técnica neutra. |

---

## 2.6 — Resumen Fase 2

Total: **40 casos automatizados vía webhook** (9 del fix re-saludo + 8 ETAPAS + 11 reglas + 7 tool calling + 5 anti-alucinación).

Antes de arrancar: pasame el header name + secret del webhook auth y corro todo.

---

# FASE 3 — End-to-end por WhatsApp (la agencia + cliente real)

Solo casos borde que la simulación curl no cubre. Cliente real desde su WhatsApp escribiendo al número de SyS.

## 3.1 — Inputs no estándar

| # | Caso | Mensaje | Esperado |
|---|---|---|---|
| E1 | Mensaje vacío / solo emoji | `"😊"` | Agente pregunta qué necesita sin romper. |
| E2 | Audio | (audio del cliente) | Agente NO transcribe (no soportado en Etapa 2). Pide que escriba. |
| E3 | Imagen | (foto del cliente) | Igual que E2. |
| E4 | Mensaje muy largo (>2000 chars) | Texto largo con muchas preguntas | Agente responde acotado, prioriza UNA pregunta. |
| E5 | Idioma distinto | `"Hello, how much for DTF?"` | Responde en español (forma neutra), no escala. |
| E6 | Caracteres especiales | `"<script>alert(1)</script> quiero DTF"` | Sanea, responde normal sin ejecutar. |
| E7 | Mensaje con muchos emojis | `"🔥🔥🔥 DTF 🔥🔥🔥"` | Detecta intent (DTF), responde. |

## 3.2 — Datos en formato no estándar

| # | Caso | Mensaje | Esperado |
|---|---|---|---|
| E8 | Teléfono con +54 9 | `"mi cel es +54 9 11 3134 5321"` | Parse captura el teléfono (verificar formato persistido). |
| E9 | Teléfono dictado | `"once tres uno tres cuatro cinco tres dos uno"` | Parse probablemente NO captura. El agente debería pedirlo escrito. |
| E10 | Email con typo | `"mail es juan@gmial.com"` | Captura. NO corrige typo del cliente. Confirma. |
| E11 | Ubicación sin tilde / variante | `"soy de cordoba"` | Parse captura "Córdoba" (verificar). |
| E12 | Ubicación informal | `"soy de capital"` | Parse captura "Capital". |
| E13 | Múltiples teléfonos en un mensaje | `"mi cel 1131345321 y oficina 4342-5742"` | Parse captura el del cel, NO el de oficina. |

## 3.3 — Multi-canal / Multi-sesión

| # | Caso | Setup | Mensaje | Esperado |
|---|---|---|---|---|
| E14 | Mismo lead en WA + IG | Lead conversa en WA hasta etapa diagnóstico, luego escribe desde IG (sub_id distinto). | `"sigo con la consulta"` | Sesión IG es nueva (otro sessionKey). Empieza desde bienvenida. NO contamina. |
| E15 | Lead vuelve después de 1 semana | Sesión existe, conversación de hace 7 días. Memory rotó. State persistente. | `"hola, sigo interesado"` | State `datos_capturados` sigue vivo. Reconoce. Cron de seguimientos no afecta. |

## 3.4 — Concurrencia / Reintentos

| # | Caso | Cómo simularlo | Esperado |
|---|---|---|---|
| E16 | ManyChat manda el mismo webhook 2 veces en <1s | Difícil de simular manual. Observar logs en n8n. | Solo 1 ejecución produce respuesta. La 2da entra al `IF skip?` (dedup por mensaje idéntico). |
| E17 | Webhook con timeout | Forzar latencia (no aplicable manual) | `Respond to Webhook` paralelo responde 200 OK en <100ms. AI Agent sigue async. |

## 3.5 — Flujo completo derivación

| # | Caso | Sequencia | Esperado |
|---|---|---|---|
| E18 | Funnel completo cotización | Mensaje 1: saludo → 2: necesita DTF → 3: diagnóstico → 4: cotización → 5: nombre+tel+ubicación → 6: mail → 7: cierre. | Cada turno cumple su ETAPA. `sys_tool_calls` muestra `consultar_*` en turnos técnicos + `guardar_email` + `notificar_lead` al final. Mail llega a Edgardo + asignación a Jimena en ManyChat. |
| E19 | Funnel con cambio de intent | Mensaje 1: saludo → 2: quiero DTF → 3: ah no, mejor UV → 4: derivación | Agente se adapta sin re-preguntar lo que ya tiene. Productos mostrados se acumulan en state. |
| E20 | Funnel cancelado | Lead cancela en etapa 5: `"mejor lo pienso, gracias"` | Cierre con calidez sin presión. NO invoca notificar_lead. Etapa queda en última válida. |

## 3.6 — Post-derivación

| # | Caso | Setup | Mensaje | Esperado |
|---|---|---|---|---|
| E21 | Pregunta post-derivación | Lead ya fue derivado, etapa='derivado'. | `"cuándo me contactan?"` | Confirma que el comercial se va a contactar. NO reinicia diagnóstico (Regla del prompt v2.2). |
| E22 | Lead pide equipo distinto post-derivación | Etapa='derivado'. | `"y para imprimir vidrio?"` | Puede reabrir diagnóstico para el nuevo equipo. |

## 3.7 — Seguimientos automáticos (cron)

| # | Caso | Setup | Verificación |
|---|---|---|---|
| E23 | Cron Lun-Vie 9/13/17 ART dispara seguimiento | Lead sin actividad >24h, etapa NO `derivado`/`cerrado`. | El workflow `sys-seguimientos-leads-v1` toca al lead. `seguimientos_enviados` incrementa. Mensaje generado con gpt-4o-mini llega por ManyChat. |
| E24 | Lead responde al seguimiento | Después de E23. | Conversación continúa. State se actualiza. Cron no vuelve a tocar hasta otros 24h. |

---

# Roadmap de ejecución

1. **la agencia corre Fase 1** (smoke subflujos, ~30 min). Si algún caso falla, anotar y fix antes de pasar.
2. **Pasame** el header name + secret del webhook auth.
3. **Claude corre Fase 2** (40 casos automatizados vía curl, ~15 min de batch + reporte). Documenta en este mismo archivo qué pasa cada caso (PASS/FAIL + nota).
4. **Si Fase 2 pasa ≥90%**: la agencia + cliente arrancan **Fase 3** (E2E borde, ~1 hora con un cliente real o staging WhatsApp).
5. **Reporte final**: tabla con cada caso, estado, nota. Si todo OK → cerrar la guía como `validation-completa-2026-06-09.md`.

---

# Cleanup global post-testing

```sql
-- Borrar todo lo creado por testing
DELETE FROM sys_session_state WHERE session_id LIKE 'test_%' OR session_id LIKE 'smoke_%';
DELETE FROM sys_tool_calls    WHERE session_id LIKE 'test_%' OR session_id LIKE 'smoke_%';
DELETE FROM n8n_chat_histories WHERE session_id LIKE 'test_%' OR session_id LIKE 'smoke_%';

-- Verificar que no quedó nada
SELECT COUNT(*) FROM sys_session_state WHERE session_id LIKE 'test_%' OR session_id LIKE 'smoke_%';
SELECT COUNT(*) FROM sys_tool_calls    WHERE session_id LIKE 'test_%' OR session_id LIKE 'smoke_%';
```

Y limpiar manualmente Google Sheets (pestaña Emails) las filas de smoketest.

---

# Apéndice — queries SQL útiles durante el testing

```sql
-- Ver toda la conversación de una sesión
SELECT id, created_at, message->>'type' AS rol, LEFT(message->>'content', 200) AS contenido
FROM n8n_chat_histories
WHERE session_id = 'test_test_A'
ORDER BY id ASC;

-- Ver todos los tool calls de una sesión
SELECT tool_name, status, LEFT(input_payload::text, 200) AS input, LEFT(output_payload::text, 200) AS output, created_at
FROM sys_tool_calls
WHERE session_id = 'test_test_A'
ORDER BY created_at ASC;

-- Ver el state actual de una sesión
SELECT session_id, perfil, etapa, datos_capturados, productos_mostrados, ultima_actividad
FROM sys_session_state
WHERE session_id = 'test_test_A';

-- Detectar tool calls con ERROR en las últimas 2h
SELECT tool_name, status, error_message, input_payload, created_at
FROM sys_tool_calls
WHERE created_at > NOW() - INTERVAL '2 hours'
  AND status IN ('error', 'ERROR', 'NOT_FOUND')
ORDER BY created_at DESC;

-- Métricas globales del testing
SELECT tool_name, status, COUNT(*) AS n, ROUND(AVG(duration_ms)::numeric, 2) AS avg_ms
FROM sys_tool_calls
WHERE created_at > NOW() - INTERVAL '4 hours'
GROUP BY tool_name, status
ORDER BY tool_name, status;
```
