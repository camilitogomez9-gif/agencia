# Inventario de flows ManyChat — Venttur (2026-08-17)

> **Qué es esto.** El contenido interno de los flows de ManyChat, transcrito nodo por nodo desde 15
> capturas del Flow editor (`00_inputs/manychat-flows-png/`, un PNG por flow, el nombre del archivo
> es el `flow_ns` real). Cierra el gap que arrastraba el proyecto desde mayo: la API de ManyChat
> devuelve `ns` / nombre / carpeta y **nada más** — la lógica interna no es accesible por API.
>
> **Para qué sirve.** (a) Es la fuente de verdad para re-crear los mensajes y la lógica en GoHighLevel.
> (b) Corrige el "Reporte la agencia 1" de agosto 2026 en la parte de fallos de entrega de plantillas.
> (c) Responde las cinco preguntas que estaban bloqueando la Etapa 1 de la migración.
>
> **Cobertura: 16 de 17 flows** (actualizado 2026-08-18 — ver más abajo "Borrar contactos").
>
> **`content20260210212250_552933` — "Borrar contactos"** (capturado por la agencia el 2026-08-18, no hay
> PNG en el repo: llegó por chat). Dos nodos. Trigger propio **`Contact Event` → "Disparador basado en
> fecha y hora"**, configurado sobre el campo **`Suscrito` a las 0:00**, que dispara **30 días
> después**; "se repite cada año" desactivado. Acción única: **`Eliminar contacto`**. Propósito
> confirmado por el cliente: no exceder el límite de contactos del plan de ManyChat. Probablemente se
> deprecie al migrar (en GHL el límite de contactos no funciona igual).
>
> ⚠️ **Consecuencia operativa que conviene tener presente:** a los 30 días el contacto de ManyChat
> deja de existir, así que el `ID Manychat` guardado en Airtable queda muerto y **cualquier `sendFlow`
> a un lead de más de 30 días falla**. Nurturing, rescate y el despachador nuevo dependen de ese ID.
> Puede explicar parte de los fallos de entrega del Reporte la agencia 1, sobre todo en los toques tardíos,
> y es el motivo por el que el despachador filtra a leads creados en los últimos 30 días.
>
> **Cobertura original:** La cuenta tiene 17 flows conocidos (los 14 del snapshot de mayo +
> los 3 de Outreach creados en junio). Queda **sin capturar** sólo `content20260513183625_644743` ("Rescate Post-Link" viejo de
> ManyChat, ya reemplazado por el workflow n8n homónimo — bajo interés).
>
> **Contraste contra el vivo.** Todo lo que dice "quién lo invoca desde n8n" está verificado contra
> `03_workflows/vivo-2026-08-17/` (export por API del 17/8, los 14 workflows con sha256), no contra
> el repo viejo.

---

## Resumen: los 15 flows

| `flow_ns` | Nombre | Qué hace | Cómo se dispara | Quién lo invoca desde n8n | Estado |
|---|---|---|---|---|---|
| `content20250617171957_654158` | **Recibir mensajes** | Debounce de 20 s: acumula el texto del lead en `respuesta_definitiva`, llama a ChatGPT Actions y después al webhook del main | `When…` **vacío** → sólo por invocación externa. **Ningún workflow n8n lo llama** ⇒ lo dispara una regla de ManyChat fuera del canvas (Default Reply) | — (es él el que **llama** a n8n, no al revés) | 🟢 Vivo · es la puerta de entrada del sistema |
| `content20250617172539_850988` | **Enviar mensajes** | Emite `parte1`/`parte2`/`parte3` como 3 burbujas y limpia los 3 campos | `When…` vacío → sólo API | `main-venttur` nodo `Enviar WPP` · `rescate-post-link` nodos `sendFlow: Fase 1` y `Fase 2` | 🟢 Vivo · sin él el agente es mudo |
| `content20250716130059_365663` | **Elevar** | Pausa el bot **para siempre**, asigna a "Unknown user", notifica a **0 personas** | `When…` vacío → sólo API | `main-venttur` tool `elevar` (`toolHttpRequest`, la decide el LLM) | 🔴 Vivo pero **roto** — ver Pregunta 3 |
| `content20250718115245_638127` | **Boarding School** (nurturing) | Drip de 4 toques a 0/1/3/5 días | `When…` vacío → sólo API | `resumen-etiquetas-seguimientos` (`DyrDumQgb6S4zHsS`) nodo `Boarding School` | 🟠 Vivo · **3 plantillas Meta = las 23 entregas fallidas** |
| `content20250718121921_967738` | **Pathway** (nurturing) | Idem, 4 toques 0/1/3/5 | `When…` vacío → sólo API | Idem, nodo `Pathway` | 🟠 Vivo · 4 plantillas Meta |
| `content20250718122822_491460` | **Gap year** (nurturing) | Idem | `When…` vacío → sólo API | Idem, nodo `Gap year` | 🟠 Vivo · 3 plantillas Meta |
| `content20250718123255_243860` | **Año Académico** (nurturing) | Idem | `When…` vacío → sólo API | Idem, nodo `Año Académico` | 🟠 Vivo · 3 plantillas Meta |
| `content20250718123847_652764` | **Summer Camp** (nurturing) | Idem | `When…` vacío → sólo API | Idem, nodo `Summer Camp` | 🟠 Vivo · 3 plantillas Meta · typo en producción |
| `content20250718124216_992343` | **Lead General** (nurturing) | Idem, fallback sin programa | `When…` vacío → sólo API | Idem, nodo `Seguimiento Lead General` | 🟠 Vivo · 3 plantillas Meta |
| `content20250718124614_140983` | **Agenda** (recordatorio "aún no agendaste") | Un toque único con candado por tag `seguimiento_agenda` | `When…` vacío → sólo API | `seguimiento-agenda` (`DZlSEQS5qzX1Y01K`) nodo `Seguimiento Agenda`, tras `Esperar 48 horas`; a su vez lo llama `actualizar-link-enviado` (`gRSMjzxggA4UePjz`), que llama el main | 🟢 Vivo |
| `content20250721163426_851504` | **Seguimiento agenda** (confirmación de cita) | Manda `mensaje_inicial_asesoria` + `mensaje_link_asesoria` + un cierre condicional por programa | `When…` vacío → sólo API | `confirmacion-agenda` (`2PSekVBxarsrnVBu`, **active**) nodos `Enviar` / `Enviar1` / `Enviar2`, disparados por 3 Google Calendar Triggers (Diego / Andrés / Rodrigo) | 🟢 Vivo |
| `content20260612151152_969589` | **Outreach Touch 1** | Una plantilla Meta y nada más | `When…` vacío → sólo API | `outreach-form-meta` (`CUuFxbst3iHpgeXS`, **active**) nodo `sendFlow Outreach Boarding Form` | 🟢 Vivo |
| `content20260616231914_193459` | **Outreach Touch 2** | Idem | `When…` vacío → sólo API | Idem, nodo `sendFlow Touch 2` | 🟢 Vivo |
| `content20260616231947_185709` | **Outreach Touch 3** | Idem | `When…` vacío → sólo API | Idem, nodo `sendFlow Touch 3` | 🔴 Vivo · **11 entregas fallidas** (`boarding_form_followup_touch3`) |
| `content20250918181220_518318` | **Asignar número** | Copia `{WhatsApp ID}` al custom field `wpp` | 🔵 **`Contact event occurs / Tag applied`** — **el único flow con trigger propio** | **Nadie** | ⚫ Huérfano · ver Pregunta 4 |

**Leyenda de "cómo se dispara":** 14 de 15 flows tienen el nodo inicial `When…` **vacío**, sin
keyword, sin tag, sin Default Reply, sin trigger de fecha. En ManyChat eso significa que el flow
**no puede arrancar por su cuenta**: sólo corre si alguien lo invoca por
`POST /fb/sending/sendFlow`. La única excepción es "Asignar número".

---

## Respuestas a las preguntas que estaban bloqueadas

### 1. ¿Dónde están las plantillas `seg_dia_3_bs`, `seg_dia_5_bs`, `seg_dia_7_bs`?

**Están en el flow `content20250718115245_638127` ("Boarding School"), en los mensajes #1, #2 y #3.**
Es la única conclusión compatible con toda la evidencia, pero **el nombre literal de la plantilla no
es legible en la captura** — y eso no es un problema de resolución: **el canvas de ManyChat no
muestra nunca el `template_name`**, sólo un ícono de documento verde en la esquina superior derecha
del nodo. El nombre vive dentro del nodo, hay que abrirlo.

Lo que sí está verificado visualmente (crop a resolución nativa de `content20250718115245_638127.png`):

- `Enviar mensaje` (día 0) — **NO tiene ícono de plantilla**. Es mensaje libre de sesión.
- `Enviar mensaje #1` (día 1) — **ícono de plantilla presente**.
- `Enviar mensaje #2` (día 3) — ícono de plantilla presente.
- `Enviar mensaje #3` (día 5) — ícono de plantilla presente.

O sea: **exactamente 3 plantillas Meta en el flow de Boarding School**, y el reporte lista
**exactamente 3 plantillas `seg_dia_*_bs`** con fallos (5 + 14 + 4 = **23 fallos**). El sufijo `_bs`
= **b**oarding **s**chool. Coinciden la cantidad, el canal, el programa y la posición. El texto de
cada una está transcrito completo en el catálogo de abajo (§ Boarding School, mensajes #1/#2/#3) —
con eso se pueden re-crear en GHL aunque nunca se llegue a leer el `template_name`.

**El desfase de nombre vs cadencia (día 3/5/7 en el nombre, día 1/3/5 en el flow) tiene una
explicación probable: Meta no permite renombrar una plantilla ya aprobada.** Si la cadencia se
retocó de 3/5/7 a 1/3/5 después de aprobar las plantillas, los nombres quedaron congelados en la
numeración vieja. Mapeo asumido: `seg_dia_3_bs` → `Enviar mensaje #1`, `seg_dia_5_bs` →
`Enviar mensaje #2`, `seg_dia_7_bs` → `Enviar mensaje #3`. **Consistente con el volumen de fallos**:
la del medio (`seg_dia_5_bs`, 14 fallos) es la que más dispara porque es la que más lejos está de la
última interacción real sin ser la última del drip.

**Lo que no se puede afirmar desde las capturas:** cuál de los tres nodos corresponde a cuál nombre
exacto. Para cerrarlo hay dos caminos, cualquiera de los dos alcanza:

1. Abrir los 3 nodos en el editor de ManyChat y leer el `template_name`. 2 minutos.
2. Pedir el **WhatsApp Manager de Meta** (lista de plantillas aprobadas con nombre + cuerpo) y
   matchear por texto contra el catálogo de abajo. Es determinístico: los cuerpos son únicos.

**Descartado con evidencia:** no están en los 3 flows de infraestructura (`Recibir` / `Enviar` /
`Elevar` no tienen ni un mensaje con texto propio), no están en los 3 de Outreach (ésos son
`boarding_form_followup*`), y no están en `Asignar número` (no manda ningún mensaje). Los otros 5
drips de nurturing también tienen plantillas Meta —**9 más, mínimo**— pero con otro sufijo de
programa; ninguna aparece en el reporte de fallos.

---

### 2. ¿Los drips de nurturing arrancan solos, o sólo si n8n los llama?

**Sólo si n8n los llama. Confirmado en los 6 flows, uno por uno.**

Esta es la respuesta operativamente más importante del documento: **se pueden apagar desde n8n, sin
tocar ManyChat y sin depender del acceso del cliente.**

El nodo inicial de cada uno de los 6 flows de nurturing es una tarjeta blanca con el ícono de rayo y
el texto literal `When...`, con una sola salida `Then` — es el placeholder de trigger **sin
configurar**. No hay keyword, no hay `Tag applied`, no hay Default Reply, no hay trigger de fecha.
Verificado en:

| Flow | Nodo inicial | ¿Puede arrancar solo? |
|---|---|---|
| Boarding School `…115245_638127` | `When…` vacío | No |
| Pathway `…121921_967738` | `When…` vacío | No |
| Gap year `…122822_491460` | `When…` vacío | No |
| Año Académico `…123255_243860` | `When…` vacío | No |
| Summer Camp `…123847_652764` | `When…` vacío | No |
| Lead General `…124216_992343` | `When…` vacío | No |

**La cadena completa de invocación, verificada contra el export vivo:**

```
main-venttur (k3aivKSP67S97IHn, ACTIVE)
  └─ nodo "Execute Workflow"  (waitForSubWorkflow: false)
       └─ Resumen, etiquetas, seguimientos - Venttur  (DyrDumQgb6S4zHsS)
            └─ "Esperar 8 horas"  (Wait 8h)
                 └─ Postgres (historial) → Code → Airtable (ID Clientify) → OpenAI (clasificador)
                      ├─ If (tags notEmpty)
                      │    ├─ TRUE  → "No envio link?"  (asesoria == "cero")
                      │    │            └─ TRUE → Switch por tag → 5 nodos sendFlow
                      │    │                       "Pathway IA"     → content20250718121921_967738
                      │    │                       "Summer Camp IA" → content20250718123847_652764
                      │    │                       "AA Familiar IA" → content20250718123255_243860
                      │    │                       "Boarding IA"    → content20250718115245_638127
                      │    │                       "Gap Year IA"    → content20250718122822_491460
                      │    └─ FALSE → "No envio link? x2" → "Seguimiento Lead General"
                      │                                       → content20250718124216_992343
```

**Consecuencia práctica — hay un único punto de corte.** Deshabilitar el nodo `Execute Workflow` del
main (el que apunta a `DyrDumQgb6S4zHsS`) **apaga los 6 drips de un golpe**, incluidas las 3
plantillas `seg_dia_*_bs` de los 23 fallos. Un clic, reversible, sin acceso a ManyChat, sin tocar
Meta. Si se quiere quirúrgico y sólo matar Boarding School, alcanza con deshabilitar el nodo
`Boarding School` dentro del dispatcher.

**Detalle de n8n que conviene tener claro:** `Resumen, etiquetas, seguimientos` figura como
`active: false` en el export. **Eso no significa que no corra.** Su trigger es
`executeWorkflowTrigger`, y un sub-workflow invocado con `Execute Workflow` se ejecuta
independientemente de su flag `active` — el flag sólo gobierna sus propios triggers. Lo mismo aplica
a `seguimiento-agenda`, `rescate-post-link` y `actualizar-link-enviado`. **No leer ese `false` como
"está apagado".**

---

### 3. ¿El flow "Elevar" notifica a alguien?

**No. A nadie. Verificado directamente sobre la captura, a resolución nativa.**

El flow tiene 2 nodos: `When…` vacío → un único nodo `Acciones` con exactamente tres acciones y
ninguna condición:

| Acción | Valor |
|---|---|
| Pause all automations | **Forever** |
| Assign conversation | **Unknown user** |
| Notify Assignees | **0 people via Messenger & E-mail** |

**"0 people" está confirmado, no es un artefacto de captura** — la duda que quedó abierta en
`manychat-flows-content-2026-07-20.md` §Elevar queda cerrada. Y la causa es evidente y encadenada:
la conversación se asigna a **"Unknown user"** (una cuenta que ManyChat no puede resolver: borrada,
sin acceso, o ID inválido), y como la notificación va "a los assignees", **el conjunto de
destinatarios es vacío**.

**Lo que implica, sumado:**

1. **El lead no recibe ningún mensaje.** El flow no manda ni una burbuja — nadie le dice "te paso
   con un asesor". Desde su lado, la conversación simplemente se corta.
2. **El bot queda mudo para siempre.** `Pause all automations: Forever` no tiene expiración. Y como
   las automatizaciones están pausadas, **"Recibir mensajes" tampoco se dispara** ⇒ todo lo que el
   lead escriba después ni siquiera se guarda en `respuesta_definitiva` ni llega al webhook del main.
3. **Nadie del equipo se entera.** Ni notificación, ni assignee real, ni tag, ni custom field, ni
   registro en Airtable.

**Cada elevación es una pérdida total y silenciosa del lead.** Y no es un camino marginal: lo dispara
el LLM del main por decisión propia, vía la tool `elevar`. La única forma de detectar los leads ya
caídos ahí es cruzar, en ManyChat, los contactos con automatizaciones pausadas contra los que no
tienen conversación cerrada — no hay ningún rastro del lado de n8n. **Es el hallazgo más caro del
inventario y no figura en el Reporte la agencia 1.**

Para GHL: la elevación tiene que ser assign a un usuario real + notificación + mensaje al lead +
alguna marca de estado. Los cuatro faltan hoy.

---

### 4. ¿Qué es el flow huérfano `content20250918181220_518318`?

**Se llama "Asignar número" y copia el WhatsApp ID del contacto a un custom field de texto.** El
nombre no es inferido: figura en `manychat-snapshot-2026-05-13.md:22` y en
`vtr-data-snapshot-2026-07-24.json` (`{"ns":"content20250918181220_518318","name":"Asignar número",
"folder_id":0}`). `folder_id: 0` = está en la raíz, es el único flow sin carpeta.

Son 2 nodos, verificado directamente sobre la captura:

- **Trigger:** `Contact event occurs` / `Tag applied`. **Es el único flow de la cuenta con trigger
  nativo propio** — todos los demás son API-only.
- **Acción:** `Set User Field` → `Set wpp to {WhatsApp ID}`.
- Cero condiciones, cero mensajes, cero plantillas, cero esperas, cero tags.

**El nombre del tag que lo dispara no se ve** (la tarjeta colapsada sólo muestra el tipo de evento).
Hipótesis fuerte: el tag `wpp` (id `72033971`) — es el único de los 5 tags de la cuenta cuyo nombre
coincide con el campo que este flow escribe, y el único que **ningún workflow de n8n aplica** (los
otros cuatro sí: `RESCATE_PROGRAMA_NO_MAPEADO` y `LINK_ABANDONADO_FRIO` los pone `rescate-post-link`,
`seguimiento_agenda` lo pone el flow "Agenda", `seguimiento` es el de nurturing). Sin confirmar.

**Está muerto por los dos extremos:**

- **Nadie lo dispara.** Ningún workflow de n8n aplica el tag `wpp`, y la cuenta tiene `widgets: []`
  (sin Growth Tools). Sólo podría activarse con una acción manual o una regla de keyword fuera del
  set de flows.
- **Nadie consume lo que escribe.** El campo `wpp` aparece en el `pinData` del webhook del main —
  o sea que viaja dentro del payload `custom_fields` que ManyChat manda— pero **ninguna expresión ni
  nodo lo lee**. El main y el CAPI usan el system field nativo `body.whatsapp_phone`.

**Qué se hace en la migración: no se migra.** En GHL el teléfono es campo nativo del contacto;
replicar un custom field de texto que duplica el `wa_id` no aporta nada, y el destino ya está
huérfano. **Antes de borrarlo en ManyChat**, dos chequeos de 5 minutos: (a) abrir el flow y anotar el
tag exacto del trigger — si resulta ser `seguimiento` o `seguimiento_agenda` en vez de `wpp`, el
blast radius cambia y hay que re-analizar; (b) confirmar que ningún consumidor externo al repo
(Clientify, algún Zapier/Make sobre Airtable, algún reporte de Max) lee el campo `wpp`.

**Dos documentos a corregir:** `manychat-flows-content-2026-07-20.md` (líneas 5 y 29) y
`00_inputs/README.md:34` dicen que "Asignar número" no fue capturado. Ya lo está. La clasificación
de "utilitario, bajo impacto" que hacían **se confirma correcta**.

---

### 5. ¿"Enviar mensajes" manda burbujas vacías?

**Para `parte2` y `parte3`, no. Para `parte1`, sí — no tiene ningún gate.**

La topología real es:

```
When… (vacío)
  └─ WhatsApp: Enviar mensaje  →  [parte1]          ← ⚠️ SIN condición previa
       └─ Condición: parte2 has any value
            ├─ SÍ  → Enviar mensaje #1 → [parte2]
            │         └─ Condición: parte3 has any value
            │              ├─ SÍ  → Enviar mensaje #2 → [parte3] → Acciones: Clear parte1+2+3 → FIN
            │              └─ NO  → Acciones: Clear parte1 + Clear parte2 → FIN
            └─ NO  → Acciones: Clear parte1 → FIN
```

Los gates `parteN has any value` están **antes** de cada envío, así que si n8n manda sólo `parte1`
sale una burbuja, si manda 2 salen dos, y en cada caso el flow limpia exactamente los campos que
usó. Ahí no hay bug.

**El agujero es `parte1`:** es la única burbuja que se emite sin verificar que tenga contenido. Si
n8n manda `parte1` vacío o nulo, ManyChat intenta enviar un mensaje vacío y WhatsApp lo rechaza.
**Es un candidato plausible a fallos de entrega esporádicos del canal conversacional, pero NO explica
los 34 del reporte** — ésos son todos de plantillas (`seg_dia_*_bs` y
`boarding_form_followup_touch3`), y este flow no usa ni una plantilla.

**Dos cosas más de este flow, relevantes para GHL:**

- **No hay ninguna espera entre burbujas.** Las 3 salen seguidas, sin delay ni simulación de tipeo.
  La documentación previa decía "con ritmo natural" — **es falso**, no hay ningún nodo de pausa.
- **El flow no tiene texto propio.** Todo el copy lo inyecta n8n en los custom fields. En GHL esto
  no se migra como contenido: se migra como mecanismo de entrega multi-burbuja.

---

## Catálogo por flow

> Fuente de verdad para re-crear los mensajes en GHL. Los textos están literales, con los saltos de
> línea y emojis tal como se leen en el canvas. `[First Name]` es el placeholder de ManyChat.
> **PLANTILLA META** = el nodo tiene el ícono de documento verde (mensaje HSM, sale fuera de la
> ventana de 24 h). **Libre** = mensaje de sesión, sólo entrega si la ventana está abierta.

---

### `content20250617171957_654158` — Recibir mensajes

**Infraestructura. Cero mensajes al lead. Es la puerta de entrada de todo el sistema.**

- **Trigger:** `When…` vacío. Ningún workflow n8n lo invoca ⇒ lo dispara una regla de ManyChat
  configurada **fuera del canvas** (Default Reply, en Automation settings). Ese punto de entrada no
  es visible en la captura y **hay que documentarlo antes de migrar**.
- **Condiciones (4, en orden):**
  1. `Condición #3` — `ad_source_id is unknown`. **Las dos salidas (verde y roja) van al mismo nodo
     siguiente** ⇒ es un no-op, no discrimina nada. Condición zombi.
  2. `Condición` — `respuesta_definitiva has any value`. Verde → `Acciones #1`. Roja → `Acciones`.
  3. `Condición #1` — `respuesta_definitiva has any value` (post-pausa). Verde → `Acciones #2`.
     **Roja: sin conexión** (acá mueren las ejecuciones duplicadas).
  4. `Condición #2` — `respuesta_definitiva has any value`. Verde → `Acciones #3`. **Roja: sin conexión.**
- **Acciones:**
  - `Acciones` — `Set User Field: respuesta_definitiva = {Last Text Input}` (primer mensaje del burst).
  - `Acciones #1` — `Set User Field: respuesta_definitiva = {respuesta_definitiva}, {Last Text Input}`
    (concatena, separado por coma + espacio).
  - `Acciones #2` — **`ChatGPT Actions → Request`**. Llamada a OpenAI **nativa de ManyChat**,
    anterior al webhook de n8n. Config no visible en el canvas.
  - `Acciones #3` — `External Request → https://[TU-INSTANCIA-N8N]/webh…` (URL truncada en el nodo).
  - `Acciones #4` — `Clear User Field: respuesta_definitiva`. Fin.
- **Espera:** `Pausa inteligente` = **20 segundos**.
- **Mecánica real del debounce:** cada mensaje entrante dispara una ejecución propia. Cada una
  acumula el texto, espera 20 s **desde su propio mensaje**, y al despertar chequea el campo. La
  **primera** en despertar se lo lleva todo, llama a OpenAI, llama a n8n y recién ahí limpia el
  campo. Las siguientes despiertan, encuentran el campo vacío y mueren por la rama roja
  desconectada. Es una **ventana fija de 20 s desde el primer mensaje** (leading-edge), **no un
  debounce deslizante**: si el lead tarda más de 20 s en terminar de escribir, el disparo ya salió
  con contexto incompleto y el resto se descarta sin dejar rastro.

---

### `content20250617172539_850988` — Enviar mensajes

**Infraestructura. Cero texto propio.** Ver la respuesta a la Pregunta 5 para la topología completa.

- **Trigger:** `When…` vacío → sólo API.
- **Mensajes:** 3 nodos WhatsApp cuyo contenido es **únicamente la variable**, sin texto fijo
  alrededor: `Enviar mensaje` = `[parte1]` · `Enviar mensaje #1` = `[parte2]` ·
  `Enviar mensaje #2` = `[parte3]`. **Ninguno es plantilla.**
- **Condiciones:** `parte2 has any value` · `parte3 has any value`.
- **Esperas:** ninguna.
- **Acciones:** `Clear User Field` de los campos usados, en las 3 salidas posibles.

---

### `content20250716130059_365663` — Elevar

**2 nodos. Cero mensajes. Ver la respuesta a la Pregunta 3.**

- **Trigger:** `When…` vacío → sólo API (tool `elevar` del main).
- **Condiciones:** ninguna.
- **Acciones (todas en un solo nodo):** `Pause all automations: Forever` · `Assign conversation:
  Unknown user` · `Notify Assignees: 0 people via Messenger & E-mail`.

---

### `content20250718115245_638127` — Boarding School (nurturing)

- **Trigger:** `When…` vacío → sólo API.
- **Estructura:** `Condición #3` (`Tag is seguimiento`) → verde **sin conexión** (dedupe) / roja →
  `Acciones` (`Add Tag: seguimiento`) → cadena de 4 gates de inactividad, cada uno con su mensaje.
- **Gates:** `more than 8 hours` → msg 0 · `more than 32 hours` → msg 1 · `more than 80 hours` →
  msg 2 · `more than 128 hours` → msg 3. **Todas las salidas negativas están sin conectar.**
- **Esperas:** 1 Day · 2 Days · 2 Days.
- **Acciones:** `Add Tag: seguimiento` (única de todo el flow).

**Mensaje 1 — `Enviar mensaje` (día 0) · LIBRE, no es plantilla**

```
Te comparto algo que puede servirte

Hola [First Name], no estoy seguro si este sea un buen momento para ti, pero quería dejarte esto por si te ayuda:

Muchos papás se detienen porque sienten que no tienen toda la información o no saben por dónde empezar.

Te comparto los 3 errores más comunes al elegir escuela en el extranjero:

1. Elegir por el país, no por el perfil del estudiante

2. Guiarse solo por el presupuesto sin entender qué implica

3. No considerar si la edad y madurez son compatibles con el programa

Espero que estos errores te brinden más claridad. Ojalá te sirva, saludos y un fuerte abrazo.
```

**Mensaje 2 — `Enviar mensaje #1` (día 1) · PLANTILLA META** → probable `seg_dia_3_bs` (5 fallos)

```
La pregunta que cambia todo

¿Cómo es tu hijo cuando nadie lo ve?

Esta pregunta cambia completamente el tipo de recomendación.

Muchas veces se elige por destino o por precio, pero si no se parte del perfil del estudiante, es muy fácil equivocarse.

Si te interesa, con gusto te ayudo a pensar desde ahí.
```

**Mensaje 3 — `Enviar mensaje #2` (día 3) · PLANTILLA META** → probable `seg_dia_5_bs` (14 fallos)

```
Te comparto esto, por si lo quieres revisar

Esto lo usamos normalmente con las familias que sí avanzan con nosotros, pero quise compartírtelo aunque no hayas decidido todavía:

🧠 Mini checklist: ¿Está tu hijo listo para estudiar fuera?

✅ Tiene cierta autonomía en casa

✅ Sabe manejar frustraciones sin papás cerca

✅ Tiene una razón clara (más allá de "me gusta viajar")

✅ Ustedes como papás tienen expectativas claras

No es un test. Solo algo que te puede ayudar a pensar si es el momento correcto.

Si te sirve, me da gusto. Y si en algún momento quieres retomarlo, aquí seguimos.
```

**Mensaje 4 — `Enviar mensaje #3` (día 5) · PLANTILLA META** → probable `seg_dia_7_bs` (4 fallos)

```
No te quiero saturar, lo prometo. Solo quería dejarte esto último:

Si en algún punto decides que este tema sí es algo serio para tu hijo (o para ti), tener una charla con nosotros puede evitarte muchos errores.

Aquí no vendemos viajes, ayudamos a tomar buenas decisiones.

Cuando sientas que es el momento, aquí estoy.
```

---

### `content20250718121921_967738` — Pathway (nurturing)

Misma estructura que Boarding School: gate `Tag is seguimiento` (verde sin conexión) → `Add Tag:
seguimiento` → gates 8h/32h/80h/128h → esperas 1d/2d/2d. Todas las salidas negativas sin conectar.

**Particularidad: los 4 mensajes son PLANTILLA META** — a diferencia de los otros 5 drips, acá el
primer toque también es plantilla. Y el primer nodo se llama `Enviar mensaje #4` (los demás drips
arrancan en `Enviar mensaje` sin número), lo que indica que ese nodo fue recreado o reordenado a
mano. **Conviene verificar que apunte a la plantilla correcta.**

**Mensaje 1 — `Enviar mensaje #4` (día 0) · PLANTILLA META**

```
Una pregunta que muchos no se atreven a hacer.

Hola [First Name], te dejo algo que tal vez te sirva aunque todavía estés pensando o comparando opciones:

Una de las preguntas más comunes (pero que casi nadie hace) es:

"¿Es verdad que puedo estudiar una carrera en Alemania pagando menos que en México?"

La respuesta es sí, pero depende mucho de cómo te prepares.

El Pathway es el paso previo para acceder a universidades públicas con colegiaturas muy bajas. Pero hay muchas versiones de este programa, y no todas te llevan al mismo resultado.

Si quieres, te puedo ayudar a entender cuál sí aplica para ti y cuál no.
```

**Mensaje 2 — `Enviar mensaje #1` (día 1) · PLANTILLA META**

```
"Lo que me hubiera gustado saber antes"

Muchos estudiantes que nos escriben creen que si hablan algo de alemán, ya pueden aplicar directo a la uni.

Pero lo que nadie les dice es que necesitas cumplir varios requisitos formales y académicos y si no los tienes, puedes perder tiempo valioso o incluso que te nieguen la visa.

Si me cuentas un poco más de tu perfil, puedo decirte si estás en el camino correcto... o si hay algo que debas ajustar antes de avanzar.
```

**Mensaje 3 — `Enviar mensaje #2` (día 3) · PLANTILLA META**

```
"Te comparto esto que usamos para saber quien tiene buen perfil para el Pathway"

Este checklist lo usamos en nuestras asesorías iniciales. Te lo comparto por si quieres evaluar por tu cuenta si esto hace sentido para ti:

✅ ¿Tienes o estás por terminar la prepa o una carrera universitaria?
✅ ¿Te gustaría estudiar una carrera o maestría en una universidad pública?
✅ ¿Estás dispuesto a aprender alemán desde cero (o reforzarlo)?
✅ ¿Ves esta experiencia como una inversión a mediano/largo plazo?

Si respondiste que sí a 3 o más... vale la pena hablar. Y si no, igual te puedo orientar con opciones más adecuadas.
```

**Mensaje 4 — `Enviar mensaje #3` (día 5) · PLANTILLA META**

```
"Lo importante es que tomes una buena decisión"

No te quiero llenar de mensajes, solo cerrar con esto:

Si estás pensando en estudiar en Alemania, lo mejor que puedes hacer es tener claridad desde ahora.

Aunque no sea con nosotros, tomar una buena decisión desde el principio te puede ahorrar tiempo, dinero y frustraciones.

Si en algún punto quieres retomarlo, cuenta conmigo.
```

---

### `content20250718122822_491460` — Gap Year (nurturing)

Estructura idéntica. Primer mensaje **libre**, los otros 3 plantilla.

**Mensaje 1 — `Enviar mensaje` (día 0) · LIBRE**

```
"¿Gap Year o escapatoria?"

Hola [First Name], no sé si todavía estás explorando opciones, pero te comparto esto que puede ayudarte a tomar una mejor decisión:

Una de las diferencias más importantes que nadie explica es esta:

👉 Un Gap Year no es una "pausa" ni una "escapatoria". Bien diseñado, es una herramienta para ganar claridad, madurez y dirección.

Lo ideal es que no sea improvisado. Si te interesa, puedo ayudarte a definir cuál es el enfoque más adecuado para ti.
```

**Mensaje 2 — `Enviar mensaje #1` (día 1) · PLANTILLA META**

```
"Te comparto esta reflexión"

Muchas veces se piensa que el Gap Year es solo para "descansar" antes de la universidad. Pero si se planea bien, puede ayudarte a:

✅ Validar intereses antes de elegir carrera
✅ Mejorar nivel de idioma
✅ Desarrollar independencia y madurez
✅ Ingresar con ventaja a un programa académico o laboral después

Si me cuentas un poco de lo que están buscando, te puedo decir si este tipo de programa realmente hace sentido.
```

**Mensaje 3 — `Enviar mensaje #2` (día 3) · PLANTILLA META**

```
"¿Qué países permiten estudiar y trabajar legalmente?"

Una de las preguntas más comunes es:

"¿Dónde se puede estudiar y trabajar legalmente al mismo tiempo?"

Te comparto un resumen rápido:

🇦🇺 Australia – Con cursos de idiomas o vocacionales
🇮🇪 Irlanda – Con cursos de más de 25 semanas
🇨🇦 Canadá – En programas académicos específicos
🇲🇹 Malta / 🇦🇪 Dubái – Con ciertas condiciones

Y más...

Cada país tiene sus reglas, y elegir mal puede significar no poder trabajar. Si quieres, te explico cuál te convendría según tu perfil.
```

**Mensaje 4 — `Enviar mensaje #3` (día 5) · PLANTILLA META**

```
"Lo importante no es irte... es saber por qué"

Gracias por leer hasta aquí. Te dejo solo esta última reflexión:

No se trata de si vale la pena irte o no, sino de si sabes por qué lo harías y qué quieres obtener de esa experiencia.

Si no es el momento, está bien. Pero si crees que este proyecto puede cambiar tu camino, una conversación te puede dar mucha más claridad.

Aquí estoy cuando quieras retomarlo.
```

---

### `content20250718123255_243860` — Año Académico (nurturing)

Estructura idéntica. Primer mensaje **libre**, los otros 3 plantilla.

**Mensaje 1 — `Enviar mensaje` (día 0) · LIBRE**

```
"No es solo el país, es la casa"

Hola [First Name], no estoy seguro si todavía estás considerando esta opción, pero te quiero dejar una reflexión importante:

Muchos papás eligen el país o el colegio… pero se olvidan de algo esencial:

👉 Tu hijo no va a vivir en una escuela, va a vivir en una casa.

El impacto que tiene la familia anfitriona en la experiencia es enorme.

Si quieres, te puedo explicar cómo funciona este punto en cada país y por qué hace la diferencia.
```

**Mensaje 2 — `Enviar mensaje #1` (día 1) · PLANTILLA META**

```
¿Cómo saber si tu hijo está listo?

Una de las dudas más grandes que tienen los papás es:

"¿Mi hijo realmente está preparado para vivir un año fuera, en casa de otra familia?"

Te comparto algunos indicadores que usamos para acompañar a las familias en esta decisión:

✅ Tiene cierto nivel de autonomía y se adapta bien a nuevas reglas
✅ Muestra apertura a otras culturas y estilos de vida
✅ Tiene curiosidad por mejorar su idioma
✅ Papás e hijo comparten expectativas realistas del programa

Si quieres, podemos ver juntos si este es el momento ideal o si habría que trabajar ciertos puntos antes.
```

**Mensaje 3 — `Enviar mensaje #2` (día 3) · PLANTILLA META**

```
"Dónde sí hay programas (y cómo se elige bien)"

Te comparto los países donde actualmente manejamos este tipo de experiencia con familia anfitriona y colegio público:

🇺🇸 Estados Unidos
🇨🇦 Canadá
🇫🇷 Francia
🇮🇹 Italia
🇳🇱 Países Bajos

Todos tienen diferencias importantes en cuanto a visado, requisitos, estructura y selección de familias.

Si tienes uno en mente, puedo ayudarte a saber si es el más adecuado según el perfil de tu hijo y lo que están buscando como familia.
```

**Mensaje 4 — `Enviar mensaje #3` (día 5) · PLANTILLA META**

```
"Lo que yo le diría a cualquier papá"

Para cerrar, solo te quiero dejar esto:

Como papá, una de las mejores decisiones que puedes tomar es NO hacer esto solo.

No se trata de tener prisa por mandar a tu hijo fuera, sino de saber si es el momento correcto, el programa correcto y el entorno correcto.

Si en algún momento quieres hablarlo con alguien que ya acompañó a muchas familias en este proceso, aquí estoy.
```

---

### `content20250718123847_652764` — Summer Camp (nurturing)

Estructura idéntica. Primer mensaje **libre**, los otros 3 plantilla.

**Mensaje 1 — `Enviar mensaje` (día 0) · LIBRE** — ⚠️ **termina con un `.no` espurio, se está enviando así a los leads**

```
¿Campamento o vacaciones?

Hola [First Name], te escribo porque algo que veo seguido con papás que están considerando un campamento de verano es esto:

👉 A veces se piensa que es solo "unas vacaciones fuera", pero la realidad es que bien elegido, puede ser una experiencia que le dé a tu hijo más seguridad, independencia y visión del mundo.

Si quieres, te puedo explicar qué tipo de campamento sería ideal para su edad y personalidad, y qué países tienen las mejores opciones en este momento.no
```

**Mensaje 2 — `Enviar mensaje #1` (día 1) · PLANTILLA META**

```
"3 preguntas que pueden ayudarte a decidir"

Te comparto 3 preguntas que siempre usamos para ayudar a los papás a decidir si un campamento es lo que su hijo necesita ahora:

1. ¿Tu hijo se adapta fácilmente a nuevos entornos o le cuesta salir de su zona de confort?

2. ¿Ha tenido experiencias de autonomía antes (viajes, actividades extracurriculares, convivencias)?

3. ¿Este viaje es un primer paso para algo más (como estudiar fuera) o solo para disfrutar el verano?

No hay respuestas correctas. Pero saber esto te ayuda a elegir mejor.

Si me cuentas un poco de lo que estás buscando, con gusto te oriento.
```

**Mensaje 3 — `Enviar mensaje #2` (día 3) · PLANTILLA META**

```
Qué países manejamos (y por qué)

Te dejo los destinos donde actualmente manejamos campamentos con los mejores niveles de seguridad, estructura y contenido formativo:

🇺🇸 Estados Unidos
🇬🇧 Reino Unido
🇨🇦 Canadá
🇫🇷 Francia
🇩🇪 Alemania

Y muchos más...

Todos tienen enfoques diferentes: algunos son más académicos, otros más culturales o deportivos.

Si tienes algún país en mente, puedo ayudarte a identificar si es una buena opción para tu hijo este verano.
```

**Mensaje 4 — `Enviar mensaje #3` (día 5) · PLANTILLA META**

```
"¿Vale la pena?"

Una de las preguntas que más nos hacen es:

"¿Vale la pena enviar a mi hijo solo al extranjero por unas semanas?"

Y la respuesta siempre es: depende de qué estés buscando sembrar.

En muchos casos, es un primer paso ideal para un adolescente que más adelante puede estudiar fuera.

Si en algún momento quieres tener claridad sobre esto, estoy aquí para ayudarte a decidir con calma y con toda la información sobre la mesa.
```

---

### `content20250718124216_992343` — Lead General (nurturing, fallback)

Estructura idéntica. Primer mensaje **libre**, los otros 3 plantilla. **Único drip cuyo primer
mensaje NO usa `[First Name]`** — arranca con "Hola," a secas.

**Mensaje 1 — `Enviar mensaje` (día 0) · LIBRE**

```
"¿En qué etapa estás?"

Hola, espero que estés muy bien. Vi que nos escribiste hace poco, pero no sé si ya tienes claro lo que estás buscando o apenas estás explorando opciones.

Solo para que sepas: ayudamos a familias y estudiantes a encontrar el mejor programa para estudiar fuera, dependiendo de su perfil, intereses y objetivos.

Cuando quieras, podemos platicarlo sin compromiso. Aquí sigo.
```

**Mensaje 2 — `Enviar mensaje #1` (día 1) · PLANTILLA META**

```
"¿Prefieres que te oriente?"

A veces lo más difícil no es encontrar programas, sino saber por dónde empezar.

Si quieres, puedo orientarte con algunas preguntas rápidas para saber qué tipo de opciones te harían más sentido, sin compromiso.

Me puedes decir si prefieres que te guíe paso a paso.
```

**Mensaje 3 — `Enviar mensaje #2` (día 3) · PLANTILLA META**

```
"Las rutas más comunes"

Te comparto algo que le sirve a muchos que apenas están explorando:

🎓 Internados (educación de alto nivel en el extranjero)
🏡 Años académicos en familia anfitriona
☀️ Campamentos de verano
🎓 Pathway universitario
🌎 Programas de estudia y trabaja

Cada ruta tiene perfiles distintos. Si me dices qué te llama más la atención, te puedo ayudar a afinar cuál sería ideal para ti (o para tu hijo).
```

**Mensaje 4 — `Enviar mensaje #3` (día 5) · PLANTILLA META**

```
"Aquí cuando lo necesites"

Te agradezco mucho que nos hayas escrito. Entiendo que a veces los tiempos no coinciden o que uno necesita pensarlo más.

Solo quería dejarte claro que, si en algún momento quieres avanzar o resolver dudas, aquí estoy para ayudarte de forma honesta, sin presiones.

Que tomes la mejor decisión es lo más importante, sea ahora o después.
```

---

### `content20250718124614_140983` — Agenda (recordatorio "aún no agendaste")

- **Trigger:** `When…` vacío → sólo API.
- **Condiciones:**
  1. `Tag is seguimiento_agenda` → **si YA lo tiene, la salida no está conectada: el flow termina sin
     enviar nada.** Es el candado de una-sola-vez.
  2. Si NO lo tiene → `Last Interaction less than 1 day ago`:
     - **SÍ** (ventana de 24 h abierta) → `Enviar mensaje #1`, **mensaje libre**.
     - **NO** → `Enviar mensaje`, **PLANTILLA META**.
- **Ambas ramas mandan el mismo texto y ambas terminan en `Add Tag: seguimiento_agenda`.**

**Este es el único flow del set que resuelve bien el problema de la ventana de 24 h**: bifurca por
`Last Interaction` y elige libre vs plantilla según corresponda. **Es el patrón que a los 6 drips de
nurturing les falta.**

**Texto (idéntico en ambas ramas)**

```
Hola [First Name] 👋 Hace unos días te compartí el enlace para agendar tu asesoría personalizada, pero vi que aún no la agendaste. ¿Tuviste algún problema con el link? …¿Te gustaría que te lo vuelva a compartir?
```

---

### `content20250721163426_851504` — Seguimiento agenda (confirmación de cita)

- **Trigger:** `When…` vacío → sólo API. Lo dispara `confirmacion-agenda` (`2PSekVBxarsrnVBu`,
  **active**) desde 3 Google Calendar Triggers, uno por asesor: `dgarcia@venttur.com` (Diego),
  `agarcia@venttur.com` (Andrés), `rgarcia@venttur.com` (Rodrigo), todos con `triggerOn:
  eventCreated`, polling cada minuto.
- **Mensajes:** primero manda los custom fields `mensaje_inicial_asesoria` y `mensaje_link_asesoria`
  (los arma n8n). Después, una `Condition` por programa:

**Rama A — `programa_interes` es "Boarding IA" o "Francia IA"**

```
Rodrigo se comunicará contigo por WhatsApp directamente desde el número +52 1 33 1944 2476, para que tengas un contacto directo en caso de cualquier ajuste previo a la asesoría.
```

**Rama B — no matchea**

```
Siéntete con la libertad de compartirlo con algún familiar que gustes que te acompañe a la reunión. ✈️ Nos vemos pronto!
```

> El número directo de Rodrigo (**+52 1 33 1944 2476**) es dato de negocio a preservar en la
> migración. Y ojo con el literal **"Boarding IA"**: es la grafía que usa esta condición y también el
> Switch del dispatcher de nurturing, mientras que el resto de la documentación dice "Boarding
> School". Ver Hallazgos.

---

### `content20260612151152_969589` — Outreach Form Meta · Touch 1

- **Trigger:** `When…` vacío → sólo API (`outreach-form-meta`, nodo `sendFlow Outreach Boarding Form`).
- **Condiciones:** ninguna. **Esperas:** ninguna. **Acciones:** ninguna.
- **1 solo nodo de mensaje · PLANTILLA META** = `boarding_form_followup` (MARKETING, es_MX,
  aprobada 2026-06-13). Texto confirmado contra `06_docs/template-texts-canonical.md`, coincide
  palabra por palabra.

```
Hola [First Name], gracias por tu interés en nuestros programas de Boarding School.

Vimos que recientemente solicitaste información sobre opciones de estudio en el extranjero.

Me gustaría conocer un poco más sobre tu interés para poder orientarte mejor. ¿El programa sería para tu hijo(a) o para algún familiar?
```

---

### `content20260616231914_193459` — Outreach Form Meta · Touch 2

- Idéntico en estructura: `When…` vacío, cero condiciones, cero esperas, cero acciones, **1 nodo ·
  PLANTILLA META**. Nombre de plantilla no visible en el canvas; por convención del proyecto sería
  `boarding_form_followup_touch2` (**no confirmado**).

```
Hola [First Name],

Muchos padres nos contactan porque quieren brindarles a sus hijos una experiencia internacional que los ayude a desarrollar independencia, confianza y una visión global para su futuro.

Cada estudiante tiene objetivos distintos, por eso nos gustaría entender mejor tu caso para orientarte adecuadamente.

¿Para qué edad o grado escolar estás buscando opciones?
```

---

### `content20260616231947_185709` — Outreach Form Meta · Touch 3

- Idéntico en estructura. **1 nodo · PLANTILLA META** = **`boarding_form_followup_touch3`** — la de
  los **11 fallos** del reporte.

```
Hola [First Name],

Sabemos que elegir una experiencia educativa internacional es una decisión importante y que normalmente surgen muchas preguntas sobre destinos, seguridad, costos, requisitos y beneficios para el futuro del estudiante.

Nuestro objetivo es ayudarte a encontrar la mejor opción según las metas y necesidades de tu familia.

Si aún estás explorando alternativas, responde este mensaje y con gusto te orientaremos sin compromiso.
```

---

### `content20250918181220_518318` — Asignar número

- **Trigger:** `Contact event occurs / Tag applied` (nombre del tag **no visible**).
- **Condiciones:** ninguna. **Mensajes:** ninguno. **Esperas:** ninguna.
- **Acciones:** `Set User Field` → `Set wpp to {WhatsApp ID}`.

---

## Cadencias

**Los 6 drips de nurturing** (Boarding School · Pathway · Gap year · Año Académico · Summer Camp ·
Lead General) son clones estructurales exactos: sólo cambia el copy.

| Toque | Nodo | Espera acumulada desde la entrada al flow | Gate de inactividad requerido | Tipo de mensaje |
|---|---|---|---|---|
| 1 | `Enviar mensaje` (`#4` en Pathway) | **0 (inmediato)** | `Last Interaction > 8 h` | Libre — **plantilla sólo en Pathway** |
| 2 | `Enviar mensaje #1` | **+1 día** | `Last Interaction > 32 h` | **PLANTILLA META** |
| 3 | `Enviar mensaje #2` | **+3 días** | `Last Interaction > 80 h` | **PLANTILLA META** |
| 4 | `Enviar mensaje #3` | **+5 días** | `Last Interaction > 128 h` | **PLANTILLA META** |

Pausas literales entre nodos: `Pausa inteligente` = 1 Day · `Pausa inteligente #1` = 2 Days ·
`Pausa inteligente #1` (segundo, mismo nombre) = 2 Days.

> **Corrección a `manychat-flows-content-2026-07-20.md`:** ese doc dice que Lead General tiene una
> última pausa de 3 días. **Es 2 días**, igual que los otros cinco. Los 6 drips son 0/1/3/5.

**Offset real desde que el lead escribe:** el dispatcher de n8n (`DyrDumQgb6S4zHsS`) arranca con un
`Esperar 8 horas` antes de clasificar y disparar el `sendFlow`. O sea que la cadencia efectiva
medida desde la conversación es **+8 h / +1 d 8 h / +3 d 8 h / +5 d 8 h**.

**Otras secuencias:**

| Secuencia | Cadencia | Dónde vive el timing |
|---|---|---|
| Outreach Form Meta (Touch 1/2/3) | **día 0 / +24 h / +72 h** desde `Touch 1 programado at` | **100 % en n8n** (`outreach-form-meta`, Cron cada 5 min + Switch por `Toques enviados`). Los 3 flows de ManyChat son shells de un mensaje, sin lógica |
| Agenda (recordatorio) | **+48 h** post envío del link | n8n (`seguimiento-agenda`, nodo `Esperar 48 horas`) |
| Rescate Post-Link | **+45 min** (Fase 1) y **+24 h** (Fase 2) | n8n (`rescate-post-link`) |
| Recibir mensajes (debounce) | **20 s** fijos desde el primer mensaje del burst | ManyChat |
| Enviar mensajes (3 burbujas) | **0 — sin delay entre burbujas** | ManyChat |
| Confirmación de cita | inmediato al `eventCreated` del calendar | n8n (polling cada minuto) |

---

## Hallazgos y riesgos

### 🔴 P0 — Las elevaciones a humano son una pérdida total y silenciosa del lead

Ya desarrollado en la Pregunta 3. Resumido: `Assign conversation: Unknown user` ⇒
`Notify Assignees: 0 people` ⇒ nadie se entera; `Pause all automations: Forever` ⇒ el bot no vuelve
nunca; y como las automatizaciones quedan pausadas, **"Recibir mensajes" tampoco corre**, así que lo
que el lead escriba después ni se guarda ni llega a n8n. Sin mensaje al lead, sin tag, sin custom
field, sin rastro en Airtable. **No figura en el Reporte la agencia 1 y probablemente sea el agujero más
caro del sistema.** Cuantificarlo requiere cruzar en ManyChat los contactos con automatizaciones
pausadas.

### 🔴 P0 — Causa raíz probable de los 23 fallos `seg_dia_*_bs`: no hay cota superior en los gates

En **5 de los 6 drips** (todos menos Pathway) el primer mensaje es **libre**, y el único gate previo
es `Last Interaction more than 8 hours ago` — **sin límite superior**. Un contacto cuya última
interacción fue hace 300 h pasa el gate igual y recibe un mensaje de sesión **fuera de la ventana de
24 h de WhatsApp** ⇒ entrega imposible.

Y el problema se repite hacia arriba: los gates `> 32 h`, `> 80 h` y `> 128 h` garantizan
justamente que **la ventana esté cerrada** cuando se disparan los mensajes 2, 3 y 4. Por eso esos
tres **sí** son plantilla — la arquitectura es correcta ahí. Lo que falla es que **una plantilla
también puede rebotar**: si Meta la pausa por baja calidad, si el número es inválido, o si el
contacto la bloqueó. Con 23 fallos concentrados en las 3 plantillas de un solo programa, la
hipótesis principal es **degradación de calidad de la plantilla del lado de Meta**, no un bug de
lógica del flow.

**El flow "Agenda" (`140983`) demuestra que el patrón correcto existe en la cuenta**: bifurca por
`Last Interaction less than 1 day ago` y elige libre vs plantilla. Los 6 drips no lo hacen. **En GHL
hay que aplicar ese patrón a todos.**

### 🔴 P0 — Un solo nodo de n8n gobierna todo el nurturing

`main-venttur` → `Execute Workflow` → `DyrDumQgb6S4zHsS`. Es palanca y es riesgo a la vez: sirve para
apagar los 6 drips de un clic (ver Pregunta 2), pero también significa que **cualquier falla en ese
sub-workflow se lleva puesto el nurturing entero sin que nadie lo note** — se invoca con
`waitForSubWorkflow: false`, o sea que el main ni siquiera se entera si revienta.

### 🟠 P1 — 15 ramas muertas: si el lead responde, la secuencia muere en silencio

En cada uno de los 6 drips hay 5 salidas sin conectar (30 en total): las 4 salidas negativas de los
gates de `Last Interaction` + la salida positiva de `Tag is seguimiento`. Cuando un lead responde y
resetea su `Last Interaction`, la secuencia **se corta en seco**: no se quita el tag `seguimiento`,
no se setea ningún campo, no se notifica, no queda rastro. **Es imposible distinguir "salió porque
respondió" de "nunca corrió"** — lo que arruina cualquier métrica de efectividad del nurturing y va a
complicar la validación post-migración.

### 🟠 P1 — El tag `seguimiento` es global: un lead sólo puede entrar a UN drip en toda su vida

`Condición #3` (`Tag is seguimiento`) es el dedupe, pero **el tag es el mismo en los 6 flows** y
**nunca se quita**. Consecuencia: el primer drip que se dispare bloquea permanentemente a los otros
cinco. Un lead que arranca como "Lead General" y después define que quiere Boarding School **nunca va
a recibir el nurturing de Boarding School**. No parece intencional.

### 🟠 P1 — El Switch del dispatcher no tiene salida fallback

En `resumen-etiquetas-seguimientos`, el nodo `Switch` tiene 5 reglas (`"Pathway IA"`,
`"Summer Camp IA"`, `"AA Familiar IA"`, `"Boarding IA"`, `"Gap Year IA"`) y **ninguna salida por
defecto**. Un lead cuyo tag no matchee ninguna de las cinco **se cae del flujo sin log ni alerta**.
Sumado al gate `No envio link?` (`asesoria == "cero"`), cuya rama FALSE también termina sin conectar,
son dos sumideros silenciosos más antes de llegar a ManyChat.

### 🟠 P1 — Un segundo LLM fuera de nuestro control, dentro de ManyChat

`Recibir mensajes` tiene un nodo **`ChatGPT Actions → Request`** que corre **antes** del External
Request a n8n. **No figura en ninguna documentación del proyecto.** Consume créditos de ManyChat, es
un segundo "cerebro" que no responde al system prompt del agente en n8n, y su configuración no es
visible en el canvas. Candidato a comportamiento errático y a costo oculto. **Hay que abrirlo antes
de migrar** — si hace algo funcional, se pierde en el cutover sin que nadie lo note.

### 🟡 P2 — Contradicciones con lo ya documentado (corregir estos docs)

| Doc | Dice | Realidad |
|---|---|---|
| `manychat-flows-content-2026-07-20.md` §5 y §29 · `00_inputs/README.md:34` | "Asignar número" no fue capturado | Ya está capturado. La clasificación de "utilitario, bajo impacto" **se confirma correcta** |
| `manychat-flows-content-2026-07-20.md` §Enviar mensajes | Las 3 burbujas salen "con ritmo natural" | **No hay ningún nodo de espera.** Salen seguidas |
| `manychat-flows-content-2026-07-20.md` §Lead General | Última pausa de 3 días | Son **2 días**. Los 6 drips son 0/1/3/5 |
| `manychat-flows-content-2026-07-20.md` §drips | Los gates son `Field is missing` | Son `Tag is seguimiento` + `Last Interaction more than N hours ago`. **Ningún flow del set usa `Field is missing`** |
| `manychat-flows-content-2026-07-20.md` §Elevar | "revisar si el 0 people es un artefacto de captura" | **Confirmado: es real** |
| `manychat-snapshot-2026-05-13.md` (14 flows) | Lista completa | Desactualizada — faltan los 3 de Outreach. Son **17** |
| `04_catalogo_mensajes.md:48-53` | `seg_dia_*_bs` "no está en el repo" | Sigue siendo cierto para el **nombre**, pero **el texto de las 3 ya está** en este documento |

### 🟡 P2 — Higiene que va a doler en la migración

- **Nombres de nodo duplicados dentro del mismo flow**: los 6 drips tienen **dos** `Condición #2` y
  **dos** `Pausa inteligente #1`. Cualquier mapeo por nombre a GHL se rompe; hay que desambiguar por
  posición o por criterio.
- **Doble grafía del programa**: `"Boarding IA"` (Switch del dispatcher + Condition de confirmación
  de cita) vs "Boarding School" (nombre del flow, del programa y de casi toda la documentación).
  Mismo patrón con `"AA Familiar IA"` vs "Año Académico". **En GHL hay que fijar un solo literal.**
- **Typo en producción**: el primer mensaje de Summer Camp termina con `…en este momento.no`. Se
  está enviando así.
- **`Condición #3` (`ad_source_id is unknown`) en "Recibir mensajes"** tiene las dos salidas cableadas
  al mismo nodo. Es un no-op — alguien segmentó leads de ads y después juntó las ramas. **No migrar.**
- **`respuesta_definitiva` sólo se limpia en el camino feliz.** Si la ejecución se corta antes
  (típicamente porque una elevación pausó las automatizaciones), el campo queda sucio y el próximo
  mensaje del lead se concatena al anterior ⇒ prompt contaminado.
- **`parte1` sin gate** (Pregunta 5): única burbuja que se intenta enviar sin verificar contenido.
- **Token de ManyChat hardcodeado en texto plano** en los nodos `Enviar WPP` y `elevar` del main
  (`Bearer 3256256:…`). Ya estaba señalado en la doc del proyecto; lo confirma este export.

### 🟢 Lo que sí está bien y conviene no romper al migrar

- La **arquitectura libre-vs-plantilla** de los mensajes 2/3/4 de los drips es correcta: los gates de
  inactividad garantizan que la ventana esté cerrada y por eso son plantilla.
- El flow **"Agenda"** resuelve bien la bifurcación por ventana de 24 h. Es el patrón a generalizar.
- El **dedupe por tag** del flow "Agenda" (candado de una-sola-vez) está bien pensado — el problema
  es que el de los drips usa un tag compartido.
- Los **6 drips son clones estructurales exactos**: en GHL migran limpio como **una sola plantilla
  parametrizada** con el copy como variable. No hacen falta 6 workflows distintos.

---

## Qué queda abierto (y cuánto cuesta cerrarlo)

| # | Pendiente | Cómo se cierra | Esfuerzo |
|---|---|---|---|
| 1 | Nombre literal de las 3 plantillas de Boarding School | Abrir los 3 nodos en ManyChat, o matchear cuerpos contra el WhatsApp Manager de Meta | 5 min |
| 2 | Nombre de la plantilla de Outreach Touch 2 | Idem | 2 min |
| 3 | Tag exacto que dispara "Asignar número" | Abrir el flow | 2 min |
| 4 | Qué hace el nodo `ChatGPT Actions` de "Recibir mensajes" | Abrir el nodo | 5 min |
| 5 | Punto de entrada real del sistema (la regla de Default Reply que dispara "Recibir mensajes") | ManyChat → Automation settings | 5 min |
| 6 | Capturar los 2 flows faltantes: **"Borrar contactos"** (`…552933`, acción destructiva) y Rescate Post-Link viejo (`…644743`) | 2 screenshots | 5 min |
| 7 | Cuántos leads quedaron enterrados por elevaciones | Cruzar en ManyChat contactos con automatizaciones pausadas | 30 min |

Los 6 primeros son 25 minutos de acceso a ManyChat en total. **Ninguno bloquea re-crear los mensajes
en GHL** — para eso alcanza con este documento.