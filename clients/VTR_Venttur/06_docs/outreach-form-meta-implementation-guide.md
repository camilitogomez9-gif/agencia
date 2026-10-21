# Outreach Proactivo post-Form Meta — Guía de Implementación

> **Cliente:** VTR — Venttur · **Fecha inicio:** 2026-06-12 · **Go-live:** 2026-06-13 · **Status:** ✅ LIVE
> **Owner:** la agencia (la agencia) · **Contacto cliente:** Max
>
> **Resumen en una línea:** Cuando un lead completa el formulario de Meta de Boarding School y NO agenda cita dentro de un delay configurable, n8n crea el contacto en ManyChat via API y dispara el WhatsApp Template `boarding_form_follow` para iniciar la conversación.

---

## 0. Convenciones de este documento

- ✅ = ya existe / hecho
- 🔲 = pendiente
- 🟦 = lo configura **Max** (cliente)
- 🟩 = lo configura **la agencia** (la agencia)
- ⚠️ = decisión pendiente / bloqueante

---

## 1. Arquitectura end-to-end

```
                        ┌─────────────────────────┐
                        │ 1. Meta Ads (campaña)   │
                        │    Form Lead Ad         │
                        │    + checkbox WA opt-in │
                        └────────────┬────────────┘
                                     │ Lead completa form
                                     ▼
                        ┌─────────────────────────┐
                        │ 2. Webhook a n8n        │
                        │  (Meta → n8n o vía      │
                        │   Zapier/Make si Meta   │
                        │   no soporta webhook    │
                        │   directo)              │
                        └────────────┬────────────┘
                                     ▼
                        ┌─────────────────────────┐
                        │ 3. n8n: upsert Airtable │
                        │  (dedup por teléfono)   │
                        │  Estado = "Form Meta"   │
                        │  Outreach enviado=false │
                        └────────────┬────────────┘
                                     ▼
                        ┌─────────────────────────┐
                        │ 4. Wait N minutos       │
                        │   (o cron cada X min)   │
                        └────────────┬────────────┘
                                     ▼
                        ┌─────────────────────────┐
                        │ 5. Check Airtable:      │
                        │   ¿Agendó cita?         │
                        │   ¿Outreach ya enviado? │
                        └─────┬───────────────────┘
                       Sí ◀───┤                   ├───▶ No
                       END    │                   │
                              ▼                   ▼
                  ┌─────────────────────────┐
                  │ 6. ManyChat API:        │
                  │   createSubscriber      │
                  │   (whatsapp_phone +     │
                  │    consent_phrase)      │
                  └────────────┬────────────┘
                               ▼
                  ┌─────────────────────────┐
                  │ 7. ManyChat API:        │
                  │   sendFlow              │
                  │   (Flow que contiene    │
                  │    el Template          │
                  │    boarding_form_follow)│
                  └────────────┬────────────┘
                               ▼
                  ┌─────────────────────────┐
                  │ 8. n8n: marca           │
                  │   Outreach enviado=true │
                  │   Outreach enviado at=  │
                  │     timestamp           │
                  └─────────────────────────┘
```

---

## 2. Pre-requisitos del cliente (Max)

### 2.1. Form Meta — campos mínimos 🟦

El form Lead Ad de Meta tiene que pedir mínimo:

| Campo | Obligatorio | Para qué |
|-------|-------------|----------|
| **Teléfono** (con código de país) | ✅ Sí | Identificador para crear contacto en ManyChat. Formato E.164 ideal (ej. `+5491112345678`). Si Meta entrega sin código de país, normalizamos en n8n asumiendo Argentina como default (definir con Max). |
| **Nombre** | ✅ Sí | Variable `{{1}}` del template. **Sin nombre el template falla** (o queda raro). |
| **Email** | 🟡 Opcional | Dedup adicional + backup contacto. |
| **Programa de interés** | 🟡 Opcional | Hoy el template es solo para Boarding School, así que se puede asumir. Si en el futuro hay más programas, este campo decide qué template usar. |
| **Checkbox de consentimiento WA** | ✅ Sí | **Como el template es MARKETING, el opt-in debe ser explícito y específico.** Texto recomendado: _"Quiero recibir información y seguimiento sobre programas de Boarding School por WhatsApp"_. Un genérico "acepto política de privacidad" NO es suficiente para marketing templates. Requerido por ManyChat (`consent_phrase`) y por compliance de Meta. **Sin esto: riesgo alto de baneo de la cuenta WhatsApp Business.** |

### 2.2. WhatsApp Template — aprobación en Meta 🟦

El template ya está definido:

```
Nombre: boarding_form_follow
Categoría: MARKETING (confirmado 2026-06-12 — Meta lo pre-clasificó como
           marketing al detectar intento de utility; el copy busca iniciar
           nueva conversación con intención comercial = MARKETING en política
           actualizada de Meta 2024+)
Variable {{1}} = nombre del lead

Texto:
Hola {{1}}, gracias por tu interés en nuestros programas de
Boarding School. Vimos que recientemente solicitaste información
sobre opciones de estudio en el extranjero. Me gustaría conocer
un poco más sobre tu interés para poder orientarte mejor. ¿El
programa sería para tu hijo(a) o para algún familiar?
```

**Acciones de Max:**
- 🔲 Crear el template en Meta Business Manager → WhatsApp Manager → Message Templates
- 🔲 Esperar aprobación (24-48h típicamente)
- 🔲 Confirmar el `template_name` exacto y `language` (ej. `es_AR` o `es`)

### 2.3. ManyChat — permiso de import `wa_id` 🟦

**Crítico:** la API `createSubscriber` con `whatsapp_phone` viene DESACTIVADA por default. Si la llamamos sin habilitar, devuelve: `"Permission denied to import wa_id"`.

**Page ID de la cuenta Venttur en ManyChat:** `3256256` (de la URL `app.manychat.com/fb3256256/dashboard`).

**Acción de Max:**
- 🔲 Abrir ticket en soporte ManyChat (chat o email a support@manychat.com) con este texto:

  > Hi team — please enable WhatsApp phone import via API (`wa_id` permission)
  > for my Manychat account (Page ID: **3256256**). We use the
  > `createSubscriber` endpoint with `whatsapp_phone` to import leads
  > captured via Meta Lead Ads forms, with documented opt-in consent. Thanks!

- 🔲 Esperar confirmación de ManyChat (24-72h típicamente)

### 2.4. ManyChat — flow que entrega el template 🟦

Crear **un Flow nuevo en ManyChat**:

| Item | Valor |
|------|-------|
| Nombre interno | `[LA AGENCIA] Outreach Boarding Form Meta` |
| Trigger | External (disparado por `sendFlow` desde n8n) |
| Canal | WhatsApp |
| Contenido | Un único nodo `Enviar mensaje` tipo **WhatsApp Template** → seleccionar el template aprobado `boarding_form_follow` |
| Mapeo variable `{{1}}` | Custom field `first_name` (ManyChat lo trae por default) o `lead_first_name` si se quiere namespace-ear |

**⚠️ Detalle crítico del editor de ManyChat — modo "Fuera de la ventana de 24 horas":**

Al abrir el bloque `Enviar mensaje` por default está en modo **"Enviar dentro de la ventana de 24 horas"** (texto en azul arriba del bloque) y los únicos bloques disponibles son: Texto, Imagen, Retraso, Recopilación de datos, Archivo, Audio, Video, Mensaje de lista. **El bloque de Plantilla NO aparece** en ese modo.

Para que aparezca:
1. Click en el link azul **"dentro de la ventana de 24 horas"** (al lado del icono `?`)
2. En el dropdown, elegir **"Fuera de la ventana de 24 horas"**
3. El panel de bloques se actualiza y aparece el bloque **"Plantilla"** / **"Message Template"**
4. Elegir el template aprobado `boarding_form_follow` y mapear `{{1}}` al custom field

Esto es porque WhatsApp distingue:
- **Session message** (dentro de 24h post-respuesta del lead) → contenido libre
- **Template message** (fuera de 24h o conversación fría) → solo plantillas pre-aprobadas por Meta

Para outreach proactivo (lead nunca escribió) es siempre el segundo modo.

**Action de Max:**
- 🔲 Crear el flow una vez aprobado el template
- 🔲 Cambiar el modo del bloque a "Fuera de la ventana de 24 horas"
- 🔲 Seleccionar el template `boarding_form_follow` y mapear variable `{{1}}`
- 🔲 Copiar el `flow_ns` (formato `content::nombre_interno` o `content20260612...`) y pasárselo a la agencia

---

## 3. Setup Airtable 🟩

### 3.1. Campos nuevos en tabla `Leads` (`[AIRTABLE_TABLE_ID]`)

| Campo | Tipo | Default | Para qué |
|-------|------|---------|----------|
| `Outreach Form Meta enviado` | Checkbox | `false` | Flag anti-duplicado |
| `Outreach Form Meta enviado at` | Date with time | — | Timestamp del envío exitoso (debug + métrica) |
| `Origen` (si no existe) | Single select | — | Valores: `Form Landing`, `Form Meta`, `CTWA`, `Otro`. Para segmentar en views. |
| `Meta lead_id` (opcional) | Single line text | — | Solo si Max quiere cerrar loop CAPI más adelante. No bloqueante. |
| `Meta form_id` (opcional) | Single line text | — | Idem. |

### 3.2. View útil

Crear view `Outreach Form Meta — Pendientes`:
- Filter:
  - `Origen` = `Form Meta`
  - `Outreach Form Meta enviado` = unchecked
  - `Agendan cita` = unchecked (NO mandar a quien ya agendó)
  - `Última actividad` está vacío (no respondió todavía)
  - Created time ≥ ahora − N minutos (delay configurable)

Esta view la consume directamente n8n vía Airtable Search con `view` parameter, o se replica el filtro en `filterByFormula`.

---

## 4. Setup n8n 🟩

### 4.1. Credencial ManyChat (si no existe limpia)

Según [estándar interno ManyChat](../../_core/standards/manychat-integration-pattern.md) §6:

- Tipo: `HTTP Header Auth`
- Nombre: `ManyChat - VTR`
- Header name: `Authorization`
- Header value: `Bearer {PAGE_ID}:{API_KEY}` (usar el token del cliente, una sola vez, reutilizable)

⚠️ Si los workflows existentes (Rescate Post-Link, venttur-main) usan Bearer hardcoded inline, NO los migramos en este sprint — solo el workflow nuevo usa la credencial. La migración legacy queda como deuda técnica.

### 4.2. Workflow nuevo: `outreach-form-meta-venttur-v1.json`

Compuesto por **2 sub-workflows**:

#### Sub-workflow A: Receptor del form Meta

| Nodo | Tipo | Configuración |
|------|------|----------------|
| 1. `Webhook` | webhook | Path: `vtr-form-meta-outreach`. Method: POST. Authentication: opcional (HTTP Header Auth) |
| 2. `Respond rápido` | Respond to Webhook | 200 OK, body vacío. Antes de cualquier lógica pesada — evita timeout de Meta/middleware |
| 3. `Normalize payload` | Code | Extrae `telefono`, `nombre`, `email`, `programa` del body. Normaliza teléfono a E.164 (si entra `91112345678` y default = AR → `+5491112345678`). Setea `origen = 'Form Meta'`. |
| 4. `Buscar lead existente` | Airtable | `Leads`, filterByFormula: `={Telefono} = '{{ $json.telefono }}'`, fields: `id_2`, `Agendan cita`, `Outreach Form Meta enviado` |
| 5. `IF lead existe?` | IF | Compara `$json.id_2` con vacío |
| 6a. Rama TRUE → `Actualizar lead` | Airtable | Update por `id_2`. Setea `Origen = 'Form Meta'`, conserva `Outreach Form Meta enviado` como está, conserva `Agendan cita` como está |
| 6b. Rama FALSE → `Crear lead nuevo` | Airtable | Create. Setea todos los campos del normalize + `Outreach Form Meta enviado = false`, `Origen = 'Form Meta'` |

**Trigger del intermediario:**
- Opción 1 (simple): cron del Sub-workflow B cada 5 min, consume view `Outreach Form Meta — Pendientes`
- Opción 2 (más reactivo): Execute Workflow no bloqueante al Sub-workflow B con un Wait + check upfront

Recomendación: **Opción 1** (cron). Más simple, más resiliente, anti-duplicado natural por la view.

#### Sub-workflow B: Cron de outreach

| Nodo | Tipo | Configuración |
|------|------|----------------|
| 1. `Schedule` | scheduleTrigger | Cada 5 min (ajustable). |
| 2. `Get leads pendientes` | Airtable | List records de view `Outreach Form Meta — Pendientes`. Limit 50 por corrida (anti-abuso si pasa algo raro). |
| 3. `Split In Batches` | splitInBatches | Batch size 1 para procesar uno por uno y poder logear individualmente |
| 4. `createSubscriber ManyChat` | HTTP Request | POST `https://api.manychat.com/fb/subscriber/createSubscriber`. Body: `{ whatsapp_phone, first_name, consent_phrase }`. Continue on Fail. |
| 5. `IF subscriber OK?` | IF | Chequea `$json.status == 'success'` o existencia de `subscriber_id` |
| 6a. Rama TRUE → `sendFlow ManyChat` | HTTP Request | POST `https://api.manychat.com/fb/sending/sendFlow`. Body: `{ subscriber_id, flow_ns: 'content::outreach_boarding_form_meta' }`. Continue on Fail. |
| 7a. → `Marcar enviado` | Airtable | Update por `id_2`. `Outreach Form Meta enviado = true`, `Outreach Form Meta enviado at = $now.toISO()`. |
| 6b. Rama FALSE → `Log error` | Postgres / Airtable / Slack | Loguea fallo (subscriber_id null, permission denied, plan limit, etc.). Continue para no bloquear los demás leads del batch. |

**Body del `createSubscriber`:**

```json
{
  "whatsapp_phone": "{{ $json.telefono }}",
  "first_name": "{{ $json.nombre || 'Lead' }}",
  "consent_phrase": "Completó form Meta Boarding School el {{ $json.created_at_iso }} con checkbox de opt-in WhatsApp"
}
```

**Body del `sendFlow`:**

```json
{
  "subscriber_id": "{{ $('createSubscriber ManyChat').item.json.data.id }}",
  "flow_ns": "content::outreach_boarding_form_meta"
}
```

*(reemplazar `flow_ns` por el real que pase Max)*

---

### 4.3. Mapeo completo de campos Airtable por nodo

Tabla auditada contra el schema real de `Leads` (28 columnas). Definida después del análisis de qué workflow es dueño de qué campo.

| Campo | `Crear Lead Nuevo` (Flujo A) | `Actualizar Existente` (Flujo A) | `Marcar Enviado` (Flujo B) | Dueño semántico |
|-------|-------------------------------|-----------------------------------|-----------------------------|------------------|
| `id` | — | — | — | Auto Airtable |
| `id_2` | — | match key | match key | Auto Airtable |
| `Nombre` | ✅ del payload | — (no pisar) | — | Form Meta |
| `Apellido` | ✅ del payload | — (no pisar) | — | Form Meta |
| `Telefono` | ✅ del payload (sin `+`) | — | — | Form Meta |
| `Email` | ✅ del payload | — (no pisar) | — | Form Meta |
| `Programa interés` | ✅ del payload | — (no pisar — puede ser multi-interés) | — | Form Meta |
| `Origen` | ✅ `"Form Meta"` | ✅ `"Form Meta"` | — | Este flujo |
| `Contestan 1er mensaje` | ✅ `false` (explícito) | — | — | `venttur-main` cuando lead responda |
| `Outreach Form Meta enviado` | ✅ `false` | — (no pisar) | ✅ `true` | Este flujo |
| `Outreach Form Meta enviado at` | — | — | ✅ `{{ $now.toISO() }}` | Este flujo |
| `ID Manychat` | — | — | ✅ `{{ data.id }}` del createSubscriber | Este flujo |
| `Meta lead_id` | ✅ del payload (opcional) | ✅ del payload | — | Este flujo |
| `Meta form_id` | ✅ del payload (opcional) | ✅ del payload | — | Este flujo |
| `Link asesoría enviado` | — | — | — | `actualizar-link-enviado` |
| `Asistió` | — | — | — | Post-cita |
| `Agendan cita` | — | — | — | `confirmacion-agenda` |
| `Tipo` | — | — | — | ⚠️ Pedir definición a Max |
| `Creada` | — | — | — | Airtable Created time (auto) |
| `ID Clientify` | — | — | — | Fase 2 si se integra Clientify |
| `Nombre Completo` | — | — | — | Probablemente formula Airtable |
| `Cualificado` | — | — | — | Post-conversación (agente IA) |
| `Fuente lead` | ⚠️ ver §4.3.1 | — | — | A confirmar con Max |
| `Tabla métricas` | ⚠️ ver §4.3.1 | — | — | A confirmar con Max |
| `Reporte semanal` | ⚠️ ver §4.3.1 | — | — | A confirmar con Max |
| `Folio` | — | — | — | Solo Landings (CAPI) |
| `fbclid` | — | — | — | D7 — no CAPI extra en v1 |
| `Estado conversación` | — | — | — (ver §4.3.2) | `wf-estado-lead-venttur` |
| `Última actividad` | — (ver §4.3.3) | — (ver §4.3.3) | — (ver §4.3.3) | `wf-estado-lead-venttur` |

### 4.3.1. Campos que requieren confirmación de Max

Hay 3 campos cuyo valor por defecto no está claro. Recomendado preguntar antes de activar:

| Campo | Pregunta a Max | Si la respuesta es "sí" |
|-------|----------------|--------------------------|
| `Fuente lead` | ¿Qué valor del single-select debería setear para leads que vienen de Meta Lead Ads? Conflicto potencial con `Origen`. | Setear ese valor en `Crear Lead Nuevo` |
| `Tabla métricas` | ¿Estos leads tienen que aparecer en la tabla de métricas? (true/false) | Setear `true` en `Crear Lead Nuevo` |
| `Reporte semanal` | ¿Estos leads tienen que entrar en el reporte semanal de Telegram? | Setear `true` en `Crear Lead Nuevo` |

Si Max no contesta, **default seguro: no setear ninguno** (quedan BLANK). Bug-by-omission, no bug-by-action.

### 4.3.2. Por qué `Estado conversación` NO se setea desde Marcar Enviado

Tentación: en `Marcar Enviado` setear `Estado conversación = "Activa"` para reflejar que hay una conversación arrancada.

**No conviene.** La máquina de estados de `Estado conversación` está diseñada forward-only con esta progresión:

```
(BLANK) → Contestó → Cita confirmada → (terminal)
              ↘
                Conversación interrumpida
```

"Activa" no es un estado del modelo — `wf-estado-lead-venttur` saltea directamente a "Contestó" cuando recibe un mensaje entrante. Si nosotros pre-setamos otra cosa, rompemos las guardas.

**Trade-off conocido:** un lead que recibió outreach y NUNCA respondió queda con `Estado conversación = BLANK`. Para reportar "outreach sin respuesta", el filtro es:

```
AND(
  {Outreach Form Meta enviado} = TRUE(),
  {Estado conversación} = BLANK()
)
```

### 4.3.3. Por qué `Última actividad` NO se setea desde NINGUN nodo

Semántica del campo: "última vez que el LEAD hizo algo" (mandó mensaje, agendó). No "última vez que se tocó el registro".

| Si la seteamos en... | Qué se rompe |
|----------------------|---------------|
| `Crear Lead Nuevo` con `$now` | El filtro del cron `{Última actividad} = BLANK()` excluye el lead → **nunca se envía outreach**. Bug. |
| `Marcar Enviado` con `$now` | El cron de barrido `wf-estado-interrumpida` evalúa `IS_BEFORE({Última actividad}, NOW()-24h)`. Si la fingimos al hacer outreach, contamos las 24h desde nuestro envío, no desde el último input del lead. Rompe el reporting de "Conversación interrumpida". |
| `Actualizar Existente` con `$now` | Si el lead ya estaba conversando con el agente, sobrescribimos la `Última actividad` real → falsifica la métrica de silencio. Bug. |

**Si querés trackear "última vez que tocamos el registro"** → usar el campo nativo de Airtable **"Last modified time"** (lo crea Max en la UI, es auto). No replicar en `Última actividad`.

**Caveat reporting:** los leads del form Meta que reciben outreach y nunca responden NO van a entrar automáticamente al barrido de "Conversación interrumpida" (porque `{Última actividad} = BLANK()` falla la condición del cron). Si se quiere que entren, modificar el `filterByFormula` de `wf-estado-interrumpida-venttur-v1` para considerar también `{Outreach Form Meta enviado at}` como proxy:

```
OR(
  AND({Última actividad}, IS_BEFORE({Última actividad}, DATEADD(NOW(), -24, 'hours'))),
  AND({Outreach Form Meta enviado at}, {Última actividad} = BLANK(),
      IS_BEFORE({Outreach Form Meta enviado at}, DATEADD(NOW(), -48, 'hours')))
)
```

Pero ese cambio es scope del workflow `Estado de Leads`, no de este. Dejado como sugerencia.

---

## 5. Decisiones de diseño abiertas ⚠️

Bloqueantes para escribir el workflow final. Resolver con Max antes de `/implementar`.

| # | Decisión | Opciones | Recomendación la agencia |
|---|----------|----------|---------------------|
| D1 | **Delay** entre form completado y outreach | 30 min / 1h / 2h / 24h | **1-2h**. Suficiente para que el lead "frío" recupere intención sin estar todavía en otra cosa. |
| D2 | **Cantidad de toques** | 1 solo / secuencia (ej. 1h + 24h + 3d) | **1 toque para v1**. Si la conversión es baja, agregar 2do toque post-validación métrica. Replicar patrón Rescate Post-Link si v1 funciona. |
| D3 | ~~**Categoría del template** en Meta~~ ✅ **RESUELTO 2026-06-12** | ~~Utility / Marketing~~ | **MARKETING**. Meta pre-clasificó el template como marketing (rechazó re-submit como utility). El copy busca iniciar conversación comercial → cae en política Marketing 2024+. Implica: opt-in EXPLÍCITO obligatorio en form Meta, frequency cap (~70-90% delivery típico), costo mayor (~$0.06-0.10 USD/conv vs $0.01-0.03 utility). Aceptable para escala VTR. |
| D4 | **País default** para normalizar teléfono | AR / MX / US / detectar por código de país | **AR** (Venttur es Argentina). Si Meta entrega siempre con código país, irrelevante. |
| D5 | **Webhook directo Meta → n8n o vía Zapier/Make?** | Meta soporta webhook nativo en Lead Ads pero requiere config compleja. Zapier/Make son más prácticos pero suman costo. | Verificar si el form actual ya tiene flujo a algún destino. Si ya hay Zapier, mantenerlo. Si no, intentar webhook directo. |
| D6 | **Form actual o nuevo?** | Reusar form actual de landing / crear form nuevo en Meta | Esperar respuesta de Max |
| D7 | **¿Disparamos también CAPI Lead event al hacer outreach?** | Sí (más datos a Meta) / No (suficiente con el ya existente al recibir el form) | **No** en v1. Ya hay CAPI tracking via `meta-capi-venttur-v3.json` para conversiones reales (agendado). El outreach es paso intermedio, no merece evento propio. |

---

## 6. Plan de testing

### 6.1. Smoke con teléfono propio

| Paso | Acción | Verificación |
|------|--------|--------------|
| 1 | Llenar form Meta (de prueba) con tu propio teléfono + nombre + email + check WA opt-in | Webhook recibe el payload, n8n loguea correctamente |
| 2 | Verificar Airtable | Aparece registro nuevo con `Origen = 'Form Meta'`, `Outreach Form Meta enviado = false`, datos consistentes |
| 3 | Esperar el delay configurado (o forzar manualmente el cron) | El cron levanta el lead pendiente |
| 4 | ManyChat → Contacts | Aparece el contacto nuevo creado, con el teléfono correcto |
| 5 | WhatsApp del tester | Llega el mensaje del template `boarding_form_follow` con tu nombre interpolado correctamente |
| 6 | Airtable | `Outreach Form Meta enviado = true`, timestamp poblado |

### 6.2. Caso lead que ya agendó

| Paso | Acción | Verificación |
|------|--------|--------------|
| 1 | En Airtable, marcar manualmente `Agendan cita = true` en un lead pendiente | El cron NO debe agarrarlo en la próxima corrida |
| 2 | Confirmar con log que el filtro de la view lo excluyó | Lead salió de la view "Pendientes" |
| 3 | El lead NO recibe outreach | WhatsApp del tester silencio total |

### 6.3. Caso lead duplicado (entra 2 veces al form)

| Paso | Acción | Verificación |
|------|--------|--------------|
| 1 | Llenar form Meta con el MISMO teléfono que ya está en Airtable | Sub-workflow A hace UPDATE (no crea duplicado) |
| 2 | Airtable | Sigue habiendo 1 sola row para ese teléfono |
| 3 | Si el primer outreach ya se envió → `Outreach Form Meta enviado = true` se conserva | El cron NO vuelve a mandar |

### 6.4. Caso permission denied de ManyChat

| Paso | Acción | Verificación |
|------|--------|--------------|
| 1 | Si Max aún no habilitó `wa_id` import → `createSubscriber` devuelve error | n8n loguea, NO marca `enviado = true`, NO rompe el flow del resto |
| 2 | Una vez habilitado, el lead queda igual en pendientes y se procesa en la siguiente corrida del cron | Self-healing |

---

## 7. Activación y monitoreo

### Pre-activación (checklist) — ✅ COMPLETADO 2026-06-13

- [x] Template `boarding_form_followup` aprobado por Meta (categoría MARKETING, idioma es_MX)
- [x] Permiso `wa_id` import habilitado en ManyChat (ya estaba activo, no requirió ticket)
- [x] Flow `[LA AGENCIA] Outreach Boarding Form Meta` creado en ManyChat con el template + `flow_ns` real cableado en el nodo `sendFlow Template`
- [x] Form Meta tiene el checkbox de opt-in WA visible y obligatorio
- [x] Campos Airtable creados (`Outreach Form Meta enviado`, `Outreach Form Meta enviado at`, `Origen`, `ID Manychat`, `Meta lead_id`, `Meta form_id`)
- [x] Workflow `outreach-form-meta-venttur-v1.json` importado en n8n
- [x] Sub-flujo de registro de errores cableado con trigger Execute + Set reconstrucción nested
- [x] Smoke `createSubscriber ManyChat` manual ejecutado con éxito (devolvió `data.id` válido)
- [x] Smoke E2E completo ejecutado y validado

### Activación

1. Activar Sub-workflow A (webhook receptor)
2. Activar Sub-workflow B (cron outreach)
3. Notificar a Max que la campaña Meta puede arrancar
4. Monitorear primeras 24h cada 4-6h

### Métricas a trackear (primeras 2 semanas)

| Métrica | Cómo | Target inicial |
|---------|------|----------------|
| Leads entrantes del form | Count rows `Origen = Form Meta` en Airtable | — (depende de inversión Meta) |
| Tasa de outreach exitoso | `Outreach enviado = true` / total leads form Meta | > 90% (si baja, hay bug en createSubscriber) |
| Tasa de respuesta al template | Count `Estado conversación = Contestó` post-outreach / total outreach | 15-30% típico WA |
| Tasa de conversión a cita | Count `Agendan cita = true` post-outreach / total outreach | 5-15% típico |
| Errores `wa_id` permission | Logs de n8n | 0 post-habilitación |

---

## 8. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| ~~Meta rechaza el template como utility~~ ✅ **YA OCURRIÓ — categoría definida: MARKETING** | Mayor costo por mensaje (~$0.06-0.10 USD/conv), frequency cap activo (delivery ~70-90%), requiere opt-in explícito | Opt-in fuerte en form Meta (§2.1). Monitorear delivery rate primeras 2 semanas — si < 70% revisar quality rating de la cuenta. |
| Frequency cap de Meta impacta delivery | Marketing templates tienen tope mensual por usuario (de TODOS los negocios combinados). Si lead saturado → mensaje no entregado, sin notificación. | No controlable desde nuestro lado. Aceptado como costo del modelo. Si delivery rate baja consistentemente < 60%, evaluar cambio de estrategia (CTWA en vez de Lead Ads form). |
| Marketing template = costo mayor | $0.06-0.10 USD/conversación vs $0.01-0.03 utility. Con 1000 leads/mes = $60-100 USD vs $10-30 USD. | Comunicado a Max. Si volumen crece, evaluar transición post-primer-toque a conversación libre (gratis dentro de 24h post-respuesta del lead). |
| ManyChat no habilita `wa_id` import a tiempo | Bloquea todo el envío | Pedirlo con anticipación (24-72h antes del go-live). Tener fallback de Twilio API directo si urge. |
| Lead pone teléfono inválido o sin código país | `createSubscriber` falla | Validación regex en n8n + fallback con país default. Logear pero no bloquear el batch. |
| Form Meta sin opt-in → riesgo de baneo cuenta WA | Loss total del canal WA | Bloquear el go-live hasta que Max confirme el checkbox. Validar visualmente el form en preview. |
| Cron corre 2 veces simultáneamente y manda 2 templates al mismo lead | Lead recibe spam, mala UX | El check `Outreach Form Meta enviado = true` en la view + ese mismo flag actualizado en el primer envío exitoso lo previene. Validar con caso §6.3. |
| Templates de WA tienen costo por envío (~$0.05-0.10 USD c/u) | Si entran 1000 leads/mes → ~$50-100 USD/mes en templates | Comunicar a Max el costo proyectado. Discutir si después del primer toque se hace `customerService` (gratis dentro de 24h post-respuesta) en lugar de templates. |

---

## 9. Distinción crítica con otros flujos VTR (NO confundir)

| Flujo | Identificador | Trigger | Documento |
|-------|--------------|---------|------------|
| **Outreach post-Form Meta (ESTE)** | Teléfono | Lead completa form Meta y NO agenda en X tiempo | Este doc |
| Rescate Post-Link | `subscriber_id` ManyChat existente | Lead recibió link de agenda y no agenda en 45min / 24h | `rescue-flow-implementation-guide.md` |
| CAPI Tracking | Folio + `ctwa_clid` | Lead vía CTWA dice algo al agente IA → reporta evento Lead | `CLIENT_INFO.md` §workflows |
| Formulario Clientify (landing) | Teléfono + email | Lead llena form en landing propia (NO Meta) | `formulario-clientify-venttur-v1.json` |
| Estado leads (Contestó/Cita/Interrumpida) | n/a (todos los leads) | Mensaje entrante / evento calendar / cron silencio 24h | `estado-leads-implementation-guide.md` |

---

## 10. Pendientes — ✅ TODOS RESUELTOS al 2026-06-13

### Resueltos por Max
- ✅ Confirmadas las 7 decisiones abiertas (§5: D1-D7)
- ✅ Template `boarding_form_followup` creado y aprobado en Meta (categoría MARKETING, idioma es_MX)
- ✅ Permiso `wa_id` import: no requirió ticket — ya estaba activo en la cuenta
- ✅ Flow `[LA AGENCIA] Outreach Boarding Form Meta` creado en ManyChat con el template
- ✅ Checkbox opt-in WA agregado al form Meta
- ✅ `flow_ns` pasado a la agencia y cableado en el workflow

### Resueltos por la agencia (la agencia)
- ✅ Campos Airtable creados (§3.1)
- ✅ Workflow `outreach-form-meta-venttur-v1.json` buildeado, importado y probado
- ✅ Sub-flujo de registro de errores integrado (Execute Trigger + Set + Supabase)
- ✅ Plan de testing §6 ejecutado con éxito
- ✅ Activación 2026-06-13 — sistema en producción

### Post-go-live (monitoreo)
- 🔲 Validar delivery rate primeras 2 semanas (target: > 70%)
- 🔲 Validar tasa de respuesta al template (target: 15-30%)
- 🔲 Si delivery rate < 70% sostenido → revisar quality rating cuenta WA

---

## 11. Referencias

- ManyChat Help — Create WhatsApp contacts via API: https://help.manychat.com/hc/en-us/articles/14281353475228
- ManyChat Help — WhatsApp Message Templates: https://help.manychat.com/hc/en-us/articles/14281326740124
- ManyChat Community — `wa_id` permission denied workaround: https://community.manychat.com/general-q-a-43/createsubscriber-api-permission-denied-to-import-wa-id-how-to-enable-this-feature-9349
- Meta WhatsApp Business — Template categories: https://developers.facebook.com/docs/whatsapp/business-management-api/message-templates/
- Estándar interno ManyChat ↔ n8n: `_core/standards/manychat-integration-pattern.md`
- Patrón Rescate Post-Link (referencia interna VTR): `clients/VTR_Venttur/06_docs/rescue-flow-implementation-guide.md`
- Plan Estado de Leads (referencia interna VTR): `planes/max-de-venttur-plante-joyful-shore.md`

---

## Historial de cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-06-12 | Doc inicial creado con plantilla `boarding_form_follow` confirmada por Max | la agencia + Claude |
| 2026-06-13 | Template renombrado a `boarding_form_followup` (categoría MARKETING, es_MX) por conflicto Meta. Permiso `wa_id` confirmado activo sin ticket. Workflow construido, sub-flujo errores integrado, smoke E2E OK. **Sistema LIVE.** | la agencia + Claude |
| 2026-06-16 | **Cadencia ampliada a 3 toques** (Max). Touch 2 (24h) y Touch 3 (72h) ambos con templates MARKETING aprobados + 2 flows ManyChat nuevos. Workflow refactor: Switch por `Toques enviados` con 3 ramas (Touch 1 con createSubscriber, Touch 2/3 reusan `ID Manychat`). `filterByFormula` con cadencia desde `CREATED_TIME()` del form (5min/24h/72h, no entre toques). 2 campos Airtable nuevos: `Toques enviados` (Number) y `Ultimo toque at` (Date with time). `Crear Lead Nuevo` agrega defaults `Fuente lead=Facebook - Instagram`, `Folio=N/A (Form)`, `fbclid=-`. Bearer ManyChat migrado a Credential `Venttur Header Auth account`. Bugs corregidos: cron sin `minutesInterval`, Split sin `batchSize`, Switch rama 0 con `notExists`, filterByFormula con `==`. | la agencia + Claude |
