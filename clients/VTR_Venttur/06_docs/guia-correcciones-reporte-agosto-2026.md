# Guía de correcciones — Reporte la agencia 1 (Agosto 2026)

> **Fuente de verdad:** "Reporte la agencia 1 — Agente WhatsApp Venttur — Agosto 2026" (Max). 245
> conversaciones, 1.320 mensajes, julio-agosto. Ante cualquier contradicción con el código o con la
> documentación previa, **gana el reporte**.
>
> **Snapshot de rollback:** `03_workflows/vivo-2026-08-17/` — los 14 workflows tal como corren hoy,
> con sha256 en su README. Tomado por API **antes** de tocar nada.
>
> **Regla de aplicación:** todo cambio va **por nodo, con anchor verificado**. Nunca re-importar un
> workflow completo (precedente HPF: el re-import borra nodos que el repo no conoce).

---

## Estado del repo antes de empezar (medido, no asumido)

El repo estaba desactualizado respecto de lo vivo. Verificado por API el 2026-08-17:

| Workflow | Repo | Vivo | Diferencia real |
|---|---|---|---|
| `[Venttur]` main (`k3aivKSP67S97IHn`) | 34 nodos | **35** | vivo tiene `Estampar estado (Contestó)` |
| Resumen/etiquetas/seguimientos (`DyrDumQgb6S4zHsS`) | 27 | 27 | mismos nodos |
| Rescate Post-Link (`mkEP1qFN7MVb9qP0`) | 25 (v3) | **23** | el repo tiene 2 nodos que **nunca se deployaron** (`Mensaje de ejecución`, `Mensaje de ejecución1`) |
| Outreach Form Meta (`CUuFxbst3iHpgeXS`) | 36 (v5) | **37** | vivo tiene `Wait 1.5s (rate limit)` |
| Actualizar 'Link enviado' (`gRSMjzxggA4UePjz`) | 6 en `03_workflows/`, 7 en `00_inputs/` | **7** | la copia buena era la de `00_migracion_ghl/00_inputs/` |

> ⚠️ **Corrección a `CLAUDE.md` y `CLIENT_INFO.md`:** ambos dicen que los EDITs del reporte de estado
> de leads fueron *"descartados el 2026-08-04, no se importa"*. **Es falso:** el nodo
> `Estampar estado (Contestó)` está vivo, habilitado y cableado como 3ª rama de
> `Responder rápido ManyChat`, y el sub-workflow `b52CUYEkI2Ah3Xj6` registró **18 ejecuciones, todas
> exitosas**, en la ventana de retención. La máquina de estados **sí se aplicó**.

---

## Ola 0 — Verificación previa · ✅ EJECUTADA (2026-08-17)

| # | Verificación | Resultado |
|---|---|---|
| 0.1 | Export vivo con sha256 | ✅ `03_workflows/vivo-2026-08-17/` (14 workflows) |
| 0.2 | ¿El trigger de Calendar de `confirmacion-agenda` dispara? | ✅ **Sí.** 2 ejecuciones (1 success, 1 error). **H1 se arregla con las refs rotas, NO con un cambio de trigger.** |
| 0.3 | ¿Están cruzados los `flow_ns` de `Agenda` / `Seguimiento agenda`? | ⏳ **Pendiente — requiere abrir ManyChat.** Sin esto **no se toca ningún `flow_ns`.** |
| 0.4 | Cohortes `Origen='Form Meta'` vs `Link asesoría enviado` | ✅ Disjuntas sobre el snapshot (1 lead de 3.819). Confirmar en la base viva. |
| 0.5 | **Nuevo** — ¿por qué el Rescate Post-Link tiene 0 ejecuciones? | ⏳ Ver §Ola 4.2. Es material: el mecanismo que el reporte quiere volver estándar **no está corriendo**. |

### 0.2 — La prueba de H1, con número de ejecución

Ejecución **`1362988`** (2026-08-17 19:56:50, workflow `2PSekVBxarsrnVBu`), nodos ejecutados:

```
Andres → is_asesoria → nombre_lead → Obtener datos → exists → Obtener ID Manychat1 → If
  → Agendan cita = true → Switch → mensaje_andres → Settear variables → ❌ "Referenced node doesn't exist"
```

Dos conclusiones, ambas verificadas:

1. **La cadena llega hasta el envío y muere ahí.** El trigger funciona, el cruce de identidad
   funciona, el Switch rutea bien. Lo único roto son las referencias.
2. **`Agendan cita = true` se ejecuta ANTES de la falla.** El lead queda marcado como que agendó y
   **nunca recibe la confirmación** — y además queda excluido de todo seguimiento. Esto es H1 y H3 con
   la misma causa raíz, demostrado en producción.

**Las 4 referencias rotas** (verificadas contra los nombres de nodo reales del export vivo):

| Nodo | Referencia actual | Existe | Path |
|---|---|---|---|
| `Settear variables` | `$('Obtener ID Manychat')` | ❌ | Andrés |
| `Enviar` | `$('Obtener ID Manychat')` | ❌ | Andrés |
| `Settear variables2` | `$('Obtener ID Manychat2')` | ❌ | Diego |
| `Enviar2` | `$('Obtener ID Manychat2')` | ❌ | Diego |
| `Settear variables1` / `Enviar1` | `$('Obtener ID Manychat1')` | ✅ | Rodrigo |

El único nodo Airtable que existe es **`Obtener ID Manychat1`**. Los paths de **Andrés y Diego están
rotos desde siempre**; solo el de Rodrigo resuelve.

---

## ✅ APLICADO EN PRODUCCIÓN — 2026-08-18

Seis cambios aplicados por API y **verificados uno por uno contra el vivo**. Snapshot posterior en
`03_workflows/vivo-2026-08-18-post-patches/`; rollback en `03_workflows/vivo-2026-08-17/`.

| Cambio | Workflow | Cierra |
|---|---|---|
| 4 referencias rotas → `Obtener ID Manychat1` | `confirmacion-agenda` | **H1** |
| Tri-toque a 2 + Touch 3 desconectado | `outreach-form-meta` | **H3** (11 de 34 fallos) |
| Whitelist: **+`agendar-ema`**, −`SPEagendar`, −duplicados | `resumen-etiquetas-seguimientos` | **H2** (el 64%) |
| Los 2 `No envio link?` leen el campo real de Airtable | `resumen-etiquetas-seguimientos` | **H2** (estructural) |
| `Hay audios?`: `equals` → `notContains` | `main-venttur` | **H4 / P5** |
| Dedupe: comparador alineado + salida TRUE cableada | `main-venttur` | **H4** |
| Guard `¿Programa ya definido?` (nodo nuevo) — el LLM deja de pisar `Programa interés` | `resumen-etiquetas-seguimientos` | **H5** |
| **System prompt v2.0** (39.123 → 46.868 chars) | `main-venttur` / `Agente IA WPP` | **H6, H7, H8, P1, P2, P3, P4** |
| Bloque **`[ESTADO DEL LEAD]`** en el User Message | `main-venttur` / `Agente IA WPP` | **H2, H4, H5, P3** + rasgo 3 |
| Nodo `Normalizar burbujas` (fail-open) + `Settear variables` con `JSON.stringify` | `main-venttur` | **H6, P1** + bug de comillas |
| `Agendan cita = true` movido a **después** del envío de la confirmación | `confirmacion-agenda` | **H1 + H3** (desacopla el marcado del envío) |

**Integridad verificada nodo por nodo contra `vivo-2026-08-17/`:** en el main se agregaron 2 nodos
(`Normalizar burbujas`, y el guard va en el dispatcher), cambiaron los parámetros de 4 nodos y las
conexiones de 3; **cero nodos huérfanos**. En el dispatcher se agregó 1 nodo y en el prompt del
clasificador cambió **una sola línea** de 4.564 caracteres. Todos los workflows con trigger siguen
`active: true`.

**Rangos de precio confirmados por el cliente (2026-08-18):** internados **USD $50.000 – $130.000**
anuales. Los cinco rangos ya estaban en la base de conocimiento del prompt; el `$50-100k` del PDF de
Max era el ejemplo ilustrativo de la tabla de referencia, no un dato nuevo.

**Estados de conversación:** Max definió las reglas de cierre el 2026-08-18 y se resolvieron con el
tope en **2** — ver `06_docs/estados-de-conversacion-max-2026-08-18.md`. Implementado: el marcado de
cita movido a después del envío, y el despachador escribiendo `Perdida` al agotar el tope. Queda sin
implementar sólo la detección de "por ahora no puedo" (intención del lead, requiere desarrollo).

> ⚠️ **Errata del proceso.** La primera pasada del patch de la whitelist usó una regex `[^.]*\.`
> para capturar "hasta el primer punto" — pero los links contienen puntos (`promo.venttur.com`), así
> que cortó mal y dejó restos de la lista vieja pegados detrás de la nueva. Se detectó en la
> verificación post-cambio (`SPEagendar eliminado: False`) y se corrigió anclando en **los dos
> extremos**, sin regex. Lección: no usar `.` como delimitador en texto que contiene dominios.

---

## Ola 1 — Apagar el fuego (H3)

Va primero: todo lo demás sube volumen saliente y la cuenta de WhatsApp está degradada.

### 1.1 · Bajar el tri-toque a 2 — `VTR - Outreach Form Meta` (`CUuFxbst3iHpgeXS`)

**Nodo `Get Leads Pendientes`** → `filterByFormula`: cambiar `{Toques enviados} < 3` por
`{Toques enviados} < 2`, y borrar la cláusula de la cadencia de 72 h del `OR(...)`.

**Nodo `Switch`** → desconectar la salida de la rama 2 (Touch 3). No borrar los nodos: dejarlos
huérfanos permite volver atrás reconectando.

- **Cierra:** H3 (11 de los 34 fallos son `boarding_form_followup_touch3`).
- **Verificación:** ninguna ejecución nueva debe alcanzar `sendFlow Touch 3`. A las 72 h, ningún lead
  con `Toques enviados = 2` debe pasar el filtro.
- **Rollback:** restaurar `< 3` y reconectar la rama.

### 1.2 · Empezar a medir — mismo workflow

Habilitar `Registrar Error` y replicar la guarda `¿Subscriber OK?` también en la rama de Touch 2.
Sin esto no hay forma de saber si los fallos bajaron.

### 1.3 · Recortar los drips de ManyChat

Los 5 drips de nurturing (Boarding School, Año Académico, Gap year, Pathway, Summer Camp + Lead
General) tienen **4 toques a 0/1/3/5 días** y viven **enteros dentro de ManyChat**. Recortarlos a 2
toques desde la UI, o pausarlos mientras se construye 1.4.

> **Alcance honesto para Max:** `boarding_form_followup_touch3` = 11 de 34 fallos (**32%**). Los otros
> 23 son `seg_dia_3/5/7_bs`, que viven en ManyChat. **Sin tocar ManyChat, H3 se resuelve al 32%.**
> Decirlo con ese número, no como "resuelto".

### 1.4 · Despachador proactivo único — workflow nuevo · ⏸️ DIFERIDO (decisión la agencia, 2026-08-18)

> El JSON está terminado y validado (incluye las reglas de estado de Max: escribe `Perdida` al agotar
> el tope y excluye los estados terminales del pool), **pero no se importa por ahora**. Cambia quién
> recibe mensajes proactivos, así que el paso previo es correrlo en dry-run y revisar a mano la lista
> de leads que saldrían. Mientras no se importe, la cadencia del nurturing sigue viviendo en los flows
> de ManyChat — ya gateada por el campo real de Airtable (P3) y con la whitelist corregida (P2), que
> es lo que cortaba el 64% del Hallazgo 2.


Ver `03_workflows/vtr-despachador-proactivo-v1.json`. Cron que lee el estado real de Airtable, aplica
el **tope global de 2 toques por contacto** y manda **un solo** mensaje por lead, con prioridad
`recordatorio de link pendiente > nurturing por programa`. Reemplaza la cadencia de los 5 drips;
ManyChat queda como capa de envío.

---

## Ola 2 — Los one-liners (máximo retorno, riesgo mínimo)

### 2.1 · ⭐ El cambio más rentable de toda la guía

**Workflow:** `Resumen, etiquetas, seguimientos - Venttur` (`DyrDumQgb6S4zHsS`) · **nodo `OpenAI`** ·
texto de la **Tarea 4**.

Hoy le da al LLM la lista cerrada de *"los únicos links para agendar asesorías"*:

```
SPEagendar · Estudiar-y-Trabajar-en-Australia · AAFamilia-Agendar · SummerCamp-Agendar
PW_Alemania_Agendar · EstudiaryTrabajar_Agendar · Estudiar-y-Trabajar-en-Australia (dup) · SPEagendar (dup)
```

**Falta `promo.venttur.com/agendar-ema`**, que es el link de **Internados / Boarding School** y el
**fallback ante duda** del system prompt. Y la instrucción siguiente es explícita: *"Cualquier otro
link que haya podido recibir el usuario NO es para agendar asesoría… debes devolver el valor 'cero'"*.

**Consecuencia:** todo lead que recibió `agendar-ema` queda clasificado como *"nunca recibió link"*
**por construcción** y entra al drip genérico. No es un LLM que a veces se equivoca: es determinístico.
Cierra el círculo con H3 — las plantillas que fallan son `seg_dia_*_`**`bs`** (**b**oarding **s**chool),
exactamente esa cohorte.

**Cambio:** reemplazar la enumeración por esta lista, sin duplicados y sin el `SPEagendar` inexistente:

```
'promo.venttur.com/agendar-ema', 'promo.venttur.com/AAFamilia-Agendar',
'promo.venttur.com/SummerCamp-Agendar', 'promo.venttur.com/PW_Alemania_Agendar',
'promo.venttur.com/EstudiaryTrabajar_Agendar', 'promo.venttur.com/Estudiar-y-Trabajar-en-Australia'
```

- **Cierra:** H2 (el 64% que recibió broadcast genérico).
- **Verificación:** tomar una conversación real donde se mandó `agendar-ema` y correr el nodo
  `OpenAI` con Pin Data → `asesoria` debe dar `'uno'`.
- **Rollback:** restaurar el texto anterior (está en el export vivo).

### 2.2 · Dejar de preguntarle al LLM lo que ya está en la base

**Mismo workflow · nodos `No envio link?` y `No envio link? x2`.**

| | Hoy | Va |
|---|---|---|
| leftValue | `={{ $json.message.content.asesoria }}` | `={{ $('Obtener ID Clientify').item.json['Link asesoría enviado'] }}` |
| operador | `equals` (string) | `boolean` → `isFalse` |
| rightValue | `'cero'` | — |

`Obtener ID Clientify` **ya trae ese registro de Airtable y lo descarta**. Es el fix estructural de
2.1: aunque el LLM se equivoque, el drip deja de dispararse contra el campo real.

> Airtable **no devuelve los checkbox sin marcar**, así que el campo llega `undefined` para quien no
> recibió link. Usar `isFalse` con coalescing (`?? false`), no `exists` — el patrón de bug que ya nos
> mordió en SYS con `typeValidation: strict`.

### 2.3 · Dejar de reescribir el programa de interés (H5)

**Mismo workflow.** Insertar un IF `¿Programa ya definido?` antes de `Interés` y de
`Set programa_interes`: si el lead ya tiene `Programa interés` distinto de `No definido`, **no se
sobrescribe**.

Hoy, 8 h después de cada alta, un LLM reclasifica la conversación y **pisa** `Programa interés` en
Airtable y `programa_interes` en ManyChat. Es el mecanismo exacto de H5: Benjamin Dozal (conversación
cerrada + mensaje de comida) fue reclasificado a `Boarding IA` y disparó el drip **de 0/1/3/5 días =
"los siguientes 5 días"** que describe el reporte.

Esto además detiene la sangría de la doble grafía: `Boarding School` (482 leads) vs `Boarding IA` (437).

### 2.4 · Dejar de crear leads duplicados — main (`k3aivKSP67S97IHn`)

**Orden obligatorio.** Primero el IF, después el upsert:

1. **`No existe`**: `={{ $json.Nombre }}` / `notExists` → `={{ $json.id_2 }}` / `notExists`.
2. Recién entonces **`Crear primer contacto`**: `create` → `upsert` con `matchingColumns: ["id_2"]`.

> **Si se hace al revés se rompe la atribución.** `Crear primer contacto` mapea
> `Fuente lead` = `$('Tomar fuente correcta').first().json.Anuncio` y `Programa interés` = `.Interes`.
> Ese nodo tiene `alwaysOutputData: true` y devuelve item vacío para mensajes orgánicos → con el
> upsert activo y `No existe` sin corregir, **cada mensaje pisaría esos campos con vacío**. Hay 1.915
> leads con `Fuente lead` poblado y es la base del reporting y de Meta CAPI.

### 2.5 · Dejar de descartar mensajes en silencio (H4) — main

**Nodo `Repetido?`** — hoy:

```
left  = {{ $('Buscar registro').item.json['Ultimo mensaje'] }}
right = {{ $('Webhook').item.json.body.custom_fields.respuesta_definitiva }}
```

Pero **`Actualizar ultimo mensaje` escribe** `Ultimo mensaje` desde
`$('Webhook').item.json.headers.mensaje` — y ManyChat manda ese header en **latin1 mojibake**
(`"Me llamo la atenciÃ³n…"`) mientras `respuesta_definitiva` viene en UTF-8 limpio. Campo escrito ≠
campo comparado: **el dedupe solo dispara con texto ASCII puro**, que es exactamente *"Muchas gracias"*
— el primer mensaje de Omar Montes.

Dos cambios:

1. **Alinear el comparador:** `Actualizar ultimo mensaje` pasa a escribir
   `={{ $('Webhook').item.json.body.custom_fields.respuesta_definitiva }}`.
2. **Cablear la salida TRUE dejando pasar** (hoy es una rama muerta: el mensaje desaparece sin
   respuesta). El dedupe real ya lo hace el debounce de 20 s de ManyChat; esta segunda capa solo
   agrega pérdida silenciosa.

> ⚠️ Hacer (1) **sin** (2) es peor que no hacer nada: convierte un bug aleatorio en uno consistente y
> empezaría a descartar **más** mensajes.
>
> **No afecta a Meta CAPI:** `Meta CAPI` es rama hermana de `Responder rápido ManyChat`, no cuelga de
> `Repetido?`. (Corolario incómodo: hoy ya se disparan eventos CAPI por turnos que el agente nunca
> contestó — ruido de atribución preexistente.)

### 2.6 · La rama de audio nunca se ejecutó — main

**Nodo `Hay audios?`**, combinador `and`, 3ª condición:

```
{{ $json.audio[0] }}   equals   "webp"
```

`audio[0]` es una **URL completa de S3**. Nunca puede ser igual al string `"webp"` → la condición es
**imposible** → toda la rama de transcripción (`Split Out → Get_Audio/s → Transcribir audio/s →
Aggregate → Juntar mensajes`) **jamás corrió**.

Para una nota de voz pura, `Separamos en partes` quita la URL y `Mensaje completo` queda **vacío**: el
agente responde a un string vacío.

**Cambio:** `equals` → `notContains` (era lo que se quiso escribir, igual que la condición de `jpeg`).

- **No está en el reporte**, pero es un generador silencioso de conversaciones rotas en un canal donde
  el audio es habitual, y encaja con H4/P5 mejor que varias hipótesis que sí se persiguieron.
- **Verificación:** mandar una nota de voz al número y confirmar que `Transcribir audio/s` ejecuta y
  que `Mensaje completo` trae el texto transcripto.

---

## Ola 3 — Darle memoria al agente

Es la causa raíz que el propio reporte nombra al cerrar. Hoy el User Message del nodo
**`Agente IA WPP`** es, completo:

```
Mensaje del usuario: {{ $json['Mensaje completo'] }}

Fecha de hoy: {{ $now.setZone('America/Mexico_City')... }}
```

Nada más. El agente no sabe si ya mandó el link, si el lead agendó, de qué programa es, de dónde vino,
ni qué contestó en el formulario.

### 3.1 · Traer el estado — nodo `Buscar si ya existe`

Hoy `options` está **vacío**, así que devuelve todos los campos pero nadie los usa. Fijar
`options.fields` con lo que el agente necesita: `Nombre`, `Programa interés`, `Origen`, `Fuente lead`,
`Link asesoría enviado`, `Agendan cita`, `Estado conversación`, `Última actividad`, `Nivel Inglés`,
`Grado Escolar`, `Inicio Deseado`.

### 3.2 · Inyectar el bloque `[ESTADO DEL LEAD]`

Nodo `Construir contexto` (Code) entre `Buscar si ya existe` y el agente, y el `text` del
`Agente IA WPP` pasa a incluirlo. Formato propuesto:

```
[ESTADO DEL LEAD]
Nombre: María (ya lo sabés — no se lo vuelvas a preguntar)
Programa de interés: Boarding School
Origen: Form Meta (campaña BS_MAMAS_TEST1)
Link de agenda: ENVIADO el 12/08 — NO agendó todavía
Cita: sin agendar
Del formulario: preparatoria · inicio agosto 2026 · inglés intermedio
```

**Fallback obligatorio del origen:** `Origen` → `Fuente lead` → `DESCONOCIDO`. `Origen` está vacío en
**3.336 de 3.819** leads; sin fallback el agente preguntaría el origen a casi todos, incluidos los que
vinieron de un anuncio identificado.

### 3.3 · El escritor de estado ya está vivo — no duplicarlo

`Estampar estado (Contestó)` ya corre (18 ejecuciones exitosas). **No agregar otro escritor.** Lo que
falta es que `Estado conversación` y `Última actividad` se usen como gate en las secuencias
proactivas — eso lo hace el despachador de 1.4.

> **Antes de subir volumen:** `Estado interrumpida (barrido)` (`H6qYB3Oj97bxaTCX`) está **activo** con
> barrido horario. A medida que `Última actividad` se pueble, va a marcar de golpe cientos de leads
> como `Conversación interrumpida`. **Desactivarlo 48 h** y revisar el criterio.

### 3.4 · Normalizar el teléfono

`sessionKey` del `Postgres Chat Memory` = `whatsapp_phone.replace('+','')`, sin normalizar. En la base
conviven **2.510 leads con `521…` y 1.229 con `52…`**. Un mismo lead puede tener **dos memorias
distintas**, y los lookups por `{Telefono}` / `{id}` fallan para una de las dos formas.

Normalizar a un único formato canónico en: `sessionKey`, `Buscar si ya existe`, `Buscar registro`, la
memoria sintética y el despachador.

> **Caso de test obligatorio:** lead con fila en formato `52…`. Verificar que `[ESTADO DEL LEAD]` y la
> memoria de chat **no queden desincronizados** — si el contexto dice "link ya enviado" y la memoria
> arranca vacía, el agente se contradice a sí mismo. Es un modo de falla **nuevo** que introduce la
> Ola 3 si no se hace 3.4 primero.

---

## Ola 4 — Los dos arreglos que devuelven plata

### 4.1 · Confirmación de cita (H1, P6) — `2PSekVBxarsrnVBu`

1. **Las 4 refs rotas** (§Ola 0.2): en `Settear variables`, `Enviar`, `Settear variables2` y `Enviar2`
   reemplazar `$('Obtener ID Manychat')` y `$('Obtener ID Manychat2')` por **`$('Obtener ID Manychat1')`**.
2. **Mover `Agendan cita = true` a después del envío.** Hoy se marca antes: si el envío falla, el lead
   queda "con cita", sin confirmación **y excluido de todo seguimiento**. Es el peor de los dos mundos.
3. `is_asesoria` → `caseSensitive: false`; guarda en `nombre_lead` si el título del evento no trae `<>`.
4. Conectar la rama muerta `Crear contacto → Switch` (hoy un lead nuevo que agenda no recibe nada).
5. Insertar el mensaje de confirmación en `n8n_chat_histories` para que el agente sepa que ya confirmó.
6. **Cron `Confirmación pendiente`** (`Agendan cita AND NOT Confirmación enviada AND fecha futura`):
   red de seguridad que funciona aunque el trigger falle.

- **Verificación:** agendar una cita de prueba **en el calendario de Andrés** (el path que falló en la
  ejecución `1362988`) y confirmar que llega el WhatsApp.
- **Rollback:** el export vivo tiene las refs originales.

### 4.2 · El recordatorio de link pendiente — antes de invertir, verificar

**El Rescate Post-Link (`mkEP1qFN7MVb9qP0`) tiene 0 ejecuciones** en todos los estados (`success`,
`error`, `waiting`, `canceled`), pese a que:

- está cableado y **habilitado** en `Actualizar 'Link enviado'` (nodo `Call 'Rescate Post-Link - Venttur'`),
- no está archivado,
- y su hermano `Ejecutar seguimiento agendamiento` **sí** generó una ejecución (`waiting`).

**Antes de mejorarlo hay que saber si corre.** Disparar `Actualizar 'Link enviado'` a mano con un
teléfono de prueba y mirar si aparece una ejecución del rescate. Si no aparece, mejorar sus textos no
sirve de nada y **el reemplazo es el despachador de 1.4**.

Si sí corre, aplicar:
- Fallback genérico cuando `Programa interés` no mapea: hoy **1.315 leads (34%) tienen `No definido`**
  y reciben silencio, más la doble grafía `Boarding School` / `Boarding IA`.
- Cablear el error output de `Etiquetar Contacto`.
- Documentar que los `Wait` de 24 h **no sobreviven un reinicio de n8n** (la retención de ejecuciones
  de esta instancia es de ~2 días — se ve en la API). El despachador de 1.4 elimina la dependencia.

---

## Ola 5 — Comportamiento conversacional

### 5.1 · System prompt v2.0
Ver `04_agents/agente-venttur-system-prompt-v2.0.md`. Backup del vivo en `-v1.9-2026-08-17.md`.

### 5.2 · Guardrails determinísticos

En este workspace está medido que el arreglo **por nodo** gana al arreglo **por prompt** (HPF: 4/4 y
5/5 por nodo vs 4/7 y 3/5 por prompt). Los hallazgos 6 y P1 se resuelven en nodos:

1. **Nodo `Normalizar burbujas`** entre `Formatear mensaje WPP` y `Settear variables`.
   **Listo para pegar:** `06_docs/snippets/clipboard-normalizar-burbujas-2026-08-17.json`
   (formato clipboard — pegarlo crea un nodo nuevo, no reemplaza al existente).

   Qué hace, todo determinístico:
   - **H6** — deja **una sola pregunta** en todo el mensaje: parte el texto en oraciones, conserva la
     primera interrogativa y descarta las siguientes.
   - **P1** — deja **una sola aparición del nombre** del lead, y limpia la puntuación que queda
     colgando al quitar las repeticiones (`"Te sirve, Carlos?"` → `"Te sirve?"`, con la mayúscula
     restituida si la frase quedaba empezando en minúscula).
   - **Arma el body como objeto real.** Hoy `Settear variables` lo construye **concatenando strings**
     y aplica `.replaceAll('"','')` — es decir, **le borra todas las comillas al mensaje del agente**,
     y si el texto trae algún carácter que rompa el JSON, el POST falla y **el lead no recibe nada**.

   Después de insertarlo, `Settear variables` pasa a tener un `jsonBody` de una sola línea:
   `={{ JSON.stringify($('Normalizar burbujas').item.json.mcBody) }}` — el mismo patrón que ya usa el
   rescate post-link.

   Verificado con 6 casos en Node contra las salidas reales que fallaron en el testing del 2026-08-17.
2. **Reescribir los ejemplos de `Formatear mensaje WPP`.** Este segundo LLM (gpt-4o-mini) reescribe
   **todos** los mensajes salientes, así que sus ejemplos son instrucciones de facto — y por eso P1
   sobrevivió a las correcciones anteriores de prompt.

   El **Ejemplo 1 actual es doblemente malo**:
   > *"Gracias Jorge. Me podrías proporcionar tu número de teléfono?"*

   Enseña (a) abrir con el nombre del lead — **P1** — y (b) **pedir el teléfono**, que es
   exactamente lo que el reporte prohíbe en su tabla de "enfoque prohibido" (*"cero fricción inicial:
   no pedir apellidos, correos o teléfonos en el primer contacto"*).

   **Reemplazo sugerido (mismo formato, sin enseñar los dos vicios):**
   ```
   ### Ejemplo 1:
   - Si el mensaje es "Perfecto. Los internados rondan entre USD 50,000 y 130,000 al año según el
     país. Te queda mejor hoy o mañana para verlo con Rodrigo?"
   - Debes separarlo de esta forma:
   'parte1' = "Perfecto"
   'parte2' = "Los internados rondan entre USD 50,000 y 130,000 al año según el país"
   'parte3' = "Te queda mejor hoy o mañana para verlo con Rodrigo?"
   ```

   Con el nodo `Normalizar burbujas` puesto, la repetición del nombre se corrige igual aunque el
   ejemplo quede — pero conviene sacarlo para no seguir empujando al modelo en la dirección incorrecta.

### 5.3 · Tools

- **`crear_contacto`**: hoy exige `nombre` **y** `apellido`. Por eso el prompt pide *"nombre completo"*
  en 4 lugares: **la fricción de H7 es estructural**, no de redacción. Hacer `apellido` opcional.
- **`contestan_2do`**: el prompt le ordena al agente activarla y **no existe como nodo**. Sacarla.
- **`primer_registro`**: nodo huérfano (`disabled: true`) que apunta a un workflow llamado
  `OUTDATED (Primer cto)`. Eliminar.

---

## Lo que esta guía NO resuelve

| Punto | Estado |
|---|---|
| **H3 al 100%** | 23 de 34 fallos viven en ManyChat. Con 1.4 se cierra; sin tocar ManyChat, 32%. |
| **H5 literal** | El estado *"Cerrado"* **no existe** en Airtable, Clientify ni tags de ManyChat. Se resuelve lateralmente. **Preguntarle a Max qué significa y quién lo setea.** |
| **P4 (longitud según ritmo)** | Sin mecanismo confiable. El tope de 200 caracteres ya existe en el prompt y no se cumple; truncar corta ideas al medio. Queda como **experimento a medir**, no como fix. |
| **Rangos de precio** | Criterio decidido (rango por programa); **las cifras las confirma Mauricio.** |
| **Secretos hardcodeados** | Bearer de ManyChat, API key de OpenAI y token de Clientify en claro en varios nodos. Fuera del reporte — rotar antes del handoff. |
