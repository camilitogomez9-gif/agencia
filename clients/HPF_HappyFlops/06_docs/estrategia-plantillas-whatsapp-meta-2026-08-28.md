# Estrategia de plantillas de WhatsApp (Meta HSM) — Migración Kommo → GHL

**Cliente:** Happy Flops · **Fecha:** 2026-08-28 · **Autor:** la agencia (la agencia)
**Alcance:** cómo se resuelven las plantillas Meta de WhatsApp (HSM) en la migración de Kommo/amoCRM a GoHighLevel.
**Estado del sistema al escribir esto:** M7 (WABA + plantillas) sin arrancar; número `+52 331 594 8670` todavía activo en Kommo; el stack nuevo (W0–W10 en `devn8n`) corre por Telegram y por el carril de GHL, pero **sin WABA conectada**.

> **Cómo leer este doc.** El §0 es el resumen de 1 minuto con las 5 respuestas. Todo lo demás es el detalle y la evidencia. Lo que está **verificado contra el vivo** (n8n `devn8n`, código real de W0/W10) va marcado ✅; lo que es **conocimiento de dominio / diseño** va sin marca; lo que **hay que confirmar a mano** (Meta Business Manager, API de GHL) va marcado 🔍 y está consolidado en el §9.

---

## §0. Resumen ejecutivo (las 5 preguntas, respondidas)

**El encuadre cambió apenas se miró la evidencia.** La pregunta "¿cómo migramos las ~66 plantillas?" está mal planteada, por tres motivos:

1. **El "66" es un número fantasma.** No aparece escrito en ningún archivo del repo. Lo que existe son **capas distintas** que se estaban mezclando: 146 *salesbots* de Kommo (bots de automatización, **no** plantillas), de los cuales 41 son de reenganche; **9 toques** reactivadores que n8n realmente dispara; y **0 plantillas Meta** guardadas en el repo. El conteo real de plantillas HSM **solo se ve en Meta Business Manager** (ver §1 y §9).
2. **El sistema nuevo no reusa esas plantillas: las reemplaza.** El diseño GHL ya contemplaba **~4 plantillas nuevas** hechas a medida, no recrear el catálogo viejo (verificado en dos docs de arquitectura). Migrar 66 plantillas es trabajo que nadie pidió.
3. **Hoy el sistema nuevo no necesita NI UNA plantilla para funcionar.** ✅ El reactivador vivo (W10) manda sus 3 toques a **1h / 4h / 5h** — todos **dentro** de la ventana de 24h — y el punto de "24h" solo **evalúa** (mueve etapa / clasifica desinterés), **no envía nada**. Y el cliente GHL (W0) solo sabe mandar **texto libre** (`send_text`), que la ventana de 24h permite.

Con eso, las respuestas:

| # | Pregunta | Respuesta corta |
|---|----------|-----------------|
| **1** | **Extracción** — ¿hay que sacar las 66 de Kommo a mano? | **No.** No se migran. Si se quiere el *inventario* (auditoría), sale automatizado del **Meta Graph API** (`GET /{WABA_ID}/message_templates`) o de la UI de WhatsApp Manager — nunca de `kommo_export.json`, que no las trae. Lo único que sí valía rescatar (los **textos de los 9 toques**) ya está recuperado (§6). |
| **2** | **Implementación en GHL** — ¿viajan las plantillas con el WABA o hay que recrearlas? | **Depende de quién es dueño del WABA**, y eso **hay que confirmarlo en Meta Business Manager** (2 min, §2). Pero es **casi irrelevante**: el sistema nuevo necesita solo ~4 plantillas nuevas, que **se crean igual**. La jugada que sí importa: si HPF es dueña del WABA, se pueden **crear y aprobar esas ~4 plantillas ANTES del cutover**, directo en Meta BM, y quedan listas. |
| **3** | **Envío** — ¿n8n o GHL dispara la plantilla? | **n8n decide cuándo/cuál/variables; GHL ejecuta el envío.** Texto libre (in-window) ya funciona: `POST /conversations/messages type:WhatsApp message:"..."`. Plantillas (out-of-window) **hoy no existen en el código**: W0 no tiene op `send_template`. Hay que agregarla (vía API de GHL 🔍) o disparar un Workflow de GHL que mande la plantilla. |
| **4** | **Timing** — pre vs post cutover | **PRE:** confirmar dueño del WABA, cerrar los textos de las ~4 plantillas, **mandarlas a aprobar** (24–72h c/u) y construir la capacidad de envío de plantilla en n8n/GHL. **POST:** verificar que quedaron aprobadas y probar un envío real. Si HPF es dueña del WABA, **todo el trabajo de plantillas se hace pre-cutover**. |
| **5** | **Mapeo** — qué plantilla en qué flujo | Tabla en §5. Resumen: **1** reactivador fuera-de-ventana (opcional, solo si Oscar quiere tocar al lead a las 24h+), **3** notificaciones post-venta (pago / diseño / envío). Los reactivadores de 1h/4h/5h **no** son plantillas (van in-window, texto libre). |

**La decisión que destraba todo (owner: Oscar, con la agencia):** confirmar en Meta Business Manager si el WABA de `+52 331 594 8670` está en el **Business Portfolio de HPF** (→ se conserva número y se pre-aprueban las plantillas) o en el de un proveedor (→ número nuevo + WABA nueva, escenario Collazo). Pasos exactos en §2.4.

---

## §1. El hallazgo que reencuadra todo: salesbot ≠ plantilla ≠ mensaje

Se estaban colapsando tres cosas distintas. Separarlas es lo que vuelve el problema chico.

| Capa | Qué es | Dónde vive | Cuántas hay | ¿Se migra? |
|---|---|---|---|---|
| **Mensaje** | El texto que le llega al lead | En el prompt / en el código del bot | ~120 mensajes únicos (catálogo) | Se rediseña en GHL |
| **Salesbot (Kommo)** | Bot de automatización que Kommo dispara con `bot_id` vía `POST /salesbot/run` | Editor visual de Kommo | ✅ **146** (41 de reenganche) | **No** — se reemplaza por los workflows W0–W10 |
| **Plantilla Meta (HSM)** | Objeto aprobado por Meta, requerido para escribir **fuera de la ventana de 24h** | **Meta Business Manager** (a nivel WABA) | **Desconocido desde el repo** (el "66" no está escrito en ningún lado) | Se crean ~4 nuevas |

Consecuencias directas:

- **`kommo_export.json` NO trae las plantillas Meta ni los textos de los salesbots.** ✅ Es un array de 1 objeto con 146 salesbots en modo *cascarón*: `nodes`/`actions`/`triggers` vacíos en las 146. Buscar `template`/`hsm` = 0 resultados. El único `"waba"` del material es el `origin` de un mensaje **entrante** de ejemplo. → Para el inventario de plantillas, el export es inútil.
- **El único `bot_id` que n8n dispara son 9** (los "Seg eN – M"): rebeca `60864/60866/60868`, imagen `60870/60872/60874`, cotización `60878/60880/60882`. Los otros ~137 salesbots son legacy de Kommo que el sistema nuevo no toca.
- **El número "66" probablemente confunde salesbots con plantillas**, o cuenta fichas de catálogo (≈40 × 3 eventos). No es un dato a defender. El número que sí importa —**cuántas plantillas Meta hay aprobadas hoy**— solo se sabe mirando Meta BM o pegándole al Graph API (§9).

> **Corrección a docs previos.** `04_guia_migracion/07_whatsapp_meta.md` y `03_arquitectura_ghl/06_integraciones.md §2` ya proponían **4 plantillas nuevas**, no migrar las viejas. Esta estrategia lo confirma y lo formaliza: **no hay un "trabajo de migrar 66 plantillas"; hay un trabajo de crear ~4.**

---

## §2. Q2 — Implementación en GHL: ¿MIGRAR el WABA o RECREARLO?

Esta es la determinación central de timing, y **es la misma pregunta de portabilidad que ya vivimos en VTR y en el incidente Collazo.** Los docs de migración de HPF la dan por sentada ("seleccionar el Business Manager de HPF", "mover el número al BSP de GHL") **sin haberla verificado nunca.** Hay que verificarla antes de comprometer fechas.

### §2.1 Las plantillas viven a nivel WABA, no de BSP

Una plantilla Meta aprobada **pertenece al WABA** (WhatsApp Business Account) dentro de un Business Portfolio de Meta. Kommo y GHL son solo *BSP / tech providers* que tienen acceso a ese WABA. Por lo tanto, la pregunta "¿viajan las plantillas?" es en realidad "¿cambia el WABA?".

### §2.2 Tres escenarios reales (no dos)

| Escenario | Qué pasa con el número | Qué pasa con las plantillas | Cuándo aplica |
|---|---|---|---|
| **A — Cambio de BSP sobre el MISMO WABA** | **Se conserva** | **Se conservan** (no cambia el WABA) | HPF es dueña del WABA en su propio Business Portfolio; se agrega GHL/LeadConnector como acceso y se saca Kommo |
| **B — Migración del número a un WABA NUEVO** | **Se conserva** | **NO viajan** — el WABA destino arranca vacío → recrear + reaprobar | El número es portable pero termina en un WABA nuevo (p. ej. WABA nueva bajo HPF conectada a GHL) |
| **C — Número nuevo + WABA nueva** | **Nuevo** | Nada se conserva → crear todo de cero | El WABA actual es de un proveedor (no de HPF) y el número no es portable (escenario Collazo/ManyChat) |

> **Trampa conceptual importante:** "conservar el número" **no** garantiza "conservar las plantillas". Solo el escenario **A** (mismo WABA) las conserva. El **B** conserva el número pero las plantillas hay que rehacerlas. No confundir los dos.

### §2.3 Por qué, para HPF, esto importa menos de lo que parece

Como el sistema nuevo **necesita solo ~4 plantillas nuevas** (§5), el beneficio de "conservar las 66 viejas" (escenario A) es marginal: las creamos igual. Lo que sí vale de conservar el WABA/número es:

1. **Continuidad del número** (marca, historial, *quality rating*, opt-ins acumulados).
2. **Poder pre-aprobar las plantillas nuevas sobre el WABA existente, antes del cutover** (§4). Esto elimina la espera de 24–72h el día del corte.

O sea: **perseguí conservar el número por su valor de negocio, pero no dependas de que las 66 viejas viajen — son irrelevantes.**

### §2.4 🔍 Verificación (owner: Oscar + la agencia — 2 minutos, bloqueante)

En `business.facebook.com` → **Configuración del negocio** → **Cuentas** → **Cuentas de WhatsApp**:

- [ ] ¿Aparece un WABA que contiene el número `+52 331 594 8670`?
- [ ] ¿Ese WABA está **dentro del Business Portfolio de Happy Flops** (Oscar es admin) o figura como compartido/propiedad de un tercero (Kommo u otro proveedor)?
- [ ] En ese WABA → **Socios / Apps conectadas**: ¿qué BSP tiene acceso hoy? (esperado: Kommo / amoCRM vía amojo).
- [ ] En **WhatsApp Manager → Plantillas de mensajes**: anotar **cuántas plantillas hay y su estado** (este es el conteo real que reemplaza al mítico "66").

**Interpretación:**
- WABA en el portfolio de HPF → **Escenario A** (ideal). Se puede pre-aprobar todo y hacer un *BSP switch* con downtime de minutos.
- WABA propiedad del proveedor → **Escenario C** (Collazo). Número nuevo + WABA nueva bajo HPF. Definir con Oscar si acepta número nuevo o si vale la pena pelear la portabilidad.

> Señales indirectas que ya tenemos (no concluyentes): el WhatsApp entra por el transporte **amojo** de Kommo (`amojo.kommo.com`) y los salesbots se disparan contra `happyflopss.amocrm.com`. Que usen HSM (plantillas) confirma que es **WhatsApp Business API real (no "WhatsApp Lite" QR)**. La integración oficial de Kommo normalmente deja el WABA **bajo el BM del cliente** con Kommo como BSP → sesga hacia el escenario A, **pero no lo prueba.** Solo Meta BM lo confirma.

---

## §3. Q3 — Envío: ¿n8n o GHL dispara la plantilla?

### §3.1 Cómo se manda hoy (verificado en el vivo) ✅

Todo el stack nuevo envía por un único cliente, **W0** (`VK4M7VQm8CMefbty`), que expone la op `send_text`:

```js
// W0 · "Construir request"  (código real del vivo)
send_text: () => {
  exigir(['contactId', 'mensaje']);
  return { method: 'POST', path: '/conversations/messages', body: {
    type: 'WhatsApp', contactId: args.contactId, message: args.mensaje } };
},
```

- **`POST /conversations/messages` con `type:'WhatsApp'` + `message` = texto libre.** WhatsApp lo permite **solo dentro de la ventana de 24h** desde el último mensaje del lead.
- **No existe ninguna op `send_template` en W0.** Ni `templateId`, ni `templateName`, ni parámetros. → **Hoy el sistema no puede mandar una plantilla, punto.** Cualquier intento de escribir fuera de ventana con `send_text` va a ser rechazado por Meta.

Esto **no rompe nada hoy** porque —como se ve en §4— todos los envíos actuales son in-window. Pero es el hueco que hay que tapar antes de habilitar cualquier flujo fuera de ventana.

### §3.2 Diferencia texto libre vs plantilla

| | **Texto libre** (in-window) | **Plantilla HSM** (out-of-window) |
|---|---|---|
| Cuándo | ≤ 24h desde el último inbound del lead | > 24h, o primer contacto proactivo |
| Contenido | Cualquiera | **Fijo y pre-aprobado**; solo varían `{{1}}`, `{{2}}`… |
| Cómo se referencia | `message: "texto"` | por **nombre de plantilla + idioma + valores de variables** |
| En GHL | `POST /conversations/messages` (ya funciona) | Workflow "Send WhatsApp" con selector de plantilla, **o** API con `templateId` 🔍 |
| Costo | Gratis (dentro de la conversación) | Se paga por plantilla (Marketing > Utility) |

### §3.3 Recomendación de arquitectura de envío

**n8n manda la inteligencia (cuándo, cuál plantilla, qué variables); GHL ejecuta.** Dos formas de que GHL ejecute la plantilla, en orden de robustez:

1. **(Recomendada) GHL Workflow "Send WhatsApp Template".** n8n (W10 / un trigger post-venta) hace `POST` a un *Inbound Webhook* de GHL que dispara un Workflow; ese Workflow tiene la acción de WhatsApp con la **plantilla aprobada seleccionada** y mapea `{{1}}`, `{{2}}` a campos del contacto/oportunidad. Ventaja: GHL administra el catálogo de plantillas y la lógica de ventana; es la vía más estable y la que no depende de un detalle de API sin confirmar.
2. **(Alternativa) Op `send_template` en W0, vía API de GHL.** Agregar a W0 una op nueva que pegue al endpoint de GHL para envío de plantilla. **🔍 Requiere confirmar** el shape exacto que expone hoy la API de GHL para mandar una plantilla de WhatsApp desde código (campo `templateId`/`templateName` + parámetros). No lo pude verificar headless (no hay WABA conectada para probar un envío real). Ventaja: mantiene toda la lógica en n8n, consistente con W0–W10.

> **Decisión pragmática:** para el MVP, ir con la opción **1** (Workflow de GHL) para las notificaciones post-venta, y para el reactivador fuera-de-ventana (si Oscar lo quiere). Es menos código nuevo en n8n y no depende de un detalle de API sin confirmar. Migrar a la op `send_template` de W0 solo si más adelante conviene centralizar.

---

## §4. Q4 — Timing: qué se hace PRE-cutover y qué POST

### §4.1 El dato que simplifica el timing (verificado) ✅

El reactivador vivo (**W10**, `fpKvo0ECWIhFcckE`) **nunca manda un mensaje fuera de la ventana de 24h.** Su código `Decidir acción` define, para las 4 campañas:

```
olas: [60, 240, 300]  // minutos = 1h / 4h / 5h  → los 3 toques
eval_h: 24            // a las 24h: EVALÚA (silencio→Perdidos/R1, o clasifica desinterés). NO envía.
```

Es decir: los 3 toques caen **dentro** de la ventana, y el hito de 24h solo mueve etapa o corre el clasificador. **El sistema, tal cual está hoy, no depende de ninguna plantilla Meta.** (La campaña "cotización"/"7pasos" además mueve a las nuevas etapas `R1 SIN/CON INFORMACION`, que son buckets terminales, no un ciclo de envío.)

Consecuencia para el timing: **conectar el WABA no está bloqueado por las plantillas.** Se puede hacer el cutover del número y el sistema sigue funcionando (in-window) sin una sola plantilla. Las plantillas hacen falta **solo** para las capacidades nuevas que se decidan habilitar (§5).

### §4.2 PRE-cutover (se puede/debe hacer ya, no depende del switch del número)

1. 🔍 **Confirmar dueño del WABA** (§2.4). Bloqueante de todo lo demás.
2. **Cerrar los textos** de las ~4 plantillas con Oscar (fijos, aptos para aprobación Meta — §5, §7).
3. **Mandarlas a aprobar** (24–72h c/u):
   - **Escenario A (HPF dueña del WABA):** crearlas **directo en Meta Business Manager → WhatsApp Manager → Plantillas**, sobre el WABA existente. **Quedan aprobadas y esperando**, sin tocar Kommo ni el número. Esta es la jugada que borra la espera del día del corte.
   - **Escenario C (WABA nueva):** crear la WABA nueva bajo HPF, conectarla a GHL, y crear las plantillas ahí. Igual se hace pre-cutover (la WABA nueva es independiente del número viejo).
4. **Construir la capacidad de envío de plantilla** (§3.3 opción 1): el/los Workflow(s) de GHL "Send WhatsApp Template" + el trigger desde n8n. Se puede construir y testear con un número de prueba antes del cutover.
5. **Bajar de Kommo los assets** que los flujos referencian y que hoy viven solo ahí (PDF de datos de cuenta, fotos) — cruzado con `06_docs/estado-crm-ghl-2026-07-27.md §8.6`. Relevante porque una plantilla de post-venta puede llevar un header de documento.

### §4.3 POST-cutover (requiere el número/WABA ya en GHL)

6. Verificar que las plantillas figuran **APPROVED** y disponibles en GHL (Settings → WhatsApp → Templates).
7. **Prueba de envío real** de cada plantilla end-to-end (a un teléfono de prueba fuera de ventana).
8. Recién ahí habilitar los flujos que las usan (reactivador 24h+ y/o notificaciones post-venta).

### §4.4 Regla de oro del cutover

Un número solo puede estar en **un** proveedor a la vez. El switch Kommo → GHL es **atómico** (ventana corta, madrugada de sábado MX). No dejar el número conectado en Kommo y GHL simultáneamente. (Ya documentado en `06_integraciones.md §2.1` y `estado-crm-ghl §8.4`.)

---

## §5. Q5 — Mapeo: qué plantilla en qué flujo

**Piso:** el sistema nuevo necesita **entre 0 y 4 plantillas**, según qué capacidades fuera-de-ventana decida Oscar. Ninguna es obligatoria para el funcionamiento base (in-window).

| Plantilla (nombre sugerido) | Categoría Meta | Flujo / disparador | Ventana | Variables | ¿Necesaria? |
|---|---|---|---|---|---|
| — (los 3 toques 1h/4h/5h) | — | Reactivador W10 (rebeca/imagen/cotización) | **IN** | — | **No es plantilla.** Texto libre vía `send_text`. Ya funciona. |
| `hpf_reactivador_v1` | MARKETING | Toque proactivo a las **24h+** sin respuesta (si Oscar lo quiere; hoy W10 no lo manda) | **OUT** | `{{1}}`=nombre; opc. `{{2}}`=evento | Opcional |
| `hpf_pago_confirmado` | UTILITY | Al confirmar el pago (si se auto-notifica; hoy el equipo lo maneja en el inbox) | OUT (típico) | — | Opcional |
| `hpf_diseno_aprobado` | UTILITY | Al aprobar el diseño (días después → fuera de ventana) | **OUT** | `{{1}}`=días de producción | Recomendada |
| `hpf_envio` | UTILITY | Al despachar (tracking) | **OUT** | `{{1}}`=paquetería, `{{2}}`=guía, `{{3}}`=link | Recomendada |

Notas por flujo (verificadas contra el diseño):

- **Reactivadores 1h/4h/5h → NO plantilla.** Van in-window; texto fijo con `{evento}`, ya compatible. El sistema los manda hoy sin problema.
- **Reactivador 24h+ → plantilla**, pero **hoy no se manda** (W10 solo evalúa a las 24h). Recrearlo es una **decisión de Oscar**, no un pendiente. Además choca con Meta (§7.1): tendría que ser **texto fijo**, no el LLM-personalizado que soñaba el diseño de reenganche.
- **Post-venta (pago/diseño/envío):** en el diseño actual las etapas 8–10 las mueve **el equipo a mano** dentro de GHL. Si el equipo escribe al lead > 24h después, GHL **ya obliga** a elegir una plantilla aprobada. Tener `hpf_diseno_aprobado` y `hpf_envio` aprobadas es lo que hace que ese mensaje manual (o automatizado) sea posible.
- **"Datos de pago" (PDF + texto de Oscar):** se manda **in-window** (responde a que el lead pregunta), así que **no es plantilla**. Verificado en la sesión del 2026-08-28 (P8, `Partir en burbujas` W6).
- **Fuera de horario (W7):** responde a un inbound activo → **in-window** → no plantilla.

---

## §6. Q1 — Extracción: de dónde salen, qué sacar, qué automatizar

### §6.1 ¿Hay que extraer las 66 a mano? No.

- **No se migran** (el sistema nuevo las reemplaza).
- Si se quiere el **inventario** (auditoría / referencia / por si Oscar reconoce alguna que sí quiera conservar), es **100% automatizable** por el **Meta Graph API**:

  ```
  GET https://graph.facebook.com/v21.0/{WABA_ID}/message_templates?limit=200
  Authorization: Bearer {SYSTEM_USER_TOKEN con whatsapp_business_management}
  ```

  Devuelve cada plantilla con nombre, idioma, categoría, estado (APPROVED/PENDING/REJECTED), componentes y variables — todo en JSON. Requiere el **WABA_ID** y un **token de system user** con `whatsapp_business_management`, que se obtiene del BM de HPF (o queda disponible al hacer el embedded signup con GHL). **Hoy no tenemos ese token** (ver §9).
- **Nunca sale de `kommo_export.json`** (no las trae) ni de los workflows de n8n (solo llevan `bot_id`, no textos).

### §6.2 Lo que sí valía rescatar, ya está rescatado ✅

Los **textos de los 9 toques** reactivadores (lo único con valor de contenido) son recuperables de los fragmentos que los sub-workflows de Kommo usan para detectar envíos, y ya están en W10 (texto fijo hardcodeado). Reproducidos en el §10 (apéndice). No hace falta abrir el editor de salesbots de Kommo para esto.

### §6.3 Qué se puede automatizar en la extracción

| Objetivo | Vía | Automatizable | Nota |
|---|---|---|---|
| Listar todas las plantillas Meta y su estado | **Meta Graph API** `GET /{WABA_ID}/message_templates` | ✅ Sí | Requiere WABA_ID + token system user |
| Idem, desde Kommo | API de Kommo (template manager) | ⚠️ Posible | Gateado por permisos + cuenta en baja; **no** recomendado |
| Textos de los salesbots reactivadores | Ya extraídos (fragmentos en n8n) | ✅ Hecho | §10 |
| Assets (PDF cuentas, fotos) | Descarga manual del editor de Kommo | ❌ Manual | Urgente antes de dar de baja Kommo (§4.2 punto 5) |

---

## §7. Colisiones y riesgos que la estrategia tiene que resolver

### §7.1 🔴 El reactivador LLM-personalizado NO es compatible con plantillas Meta

El diseño de reenganche (`03_arquitectura_ghl/05_reengagement.md`) quería que **cada** toque fuera **texto generado por LLM, distinto cada vez** ("NUNCA repetir un mensaje previo"). **Meta no aprueba plantillas de texto libre**: el cuerpo es fijo y solo varían `{{n}}`, y encima el contenido de las variables tiene que ser "predecible" (Meta rechaza plantillas cuyo `{{1}}` es "poné cualquier cosa acá").

**Resolución:**
- **In-window (1h/4h/5h):** la personalización LLM **sí** es posible (es texto libre). Ahí puede vivir toda la magia.
- **Out-of-window (24h+):** **texto fijo** obligatorio. La plantilla `hpf_reactivador_v1` lleva a lo sumo `{{1}}`=nombre y `{{2}}`=evento (de una lista cerrada). Se **sacrifica** la personalización LLM para los toques fuera de ventana. Esto ya estaba anticipado a medias en `07_whatsapp_meta.md` ("si Meta rechaza, usar texto fijo") — acá se vuelve regla.
- **Patrón estándar de re-engagement:** una plantilla fija "seguimos por acá, ¿retomamos?" **reabre** la ventana; cuando el lead responde, el resto de la conversación vuelve a ser texto libre LLM. Ese es el uso correcto de la plantilla.

### §7.2 Costo: Marketing vs Utility (aprendizaje Collazo)

Meta **recategoriza automáticamente** por contenido desde 2026-04-09, y su veredicto manda (lo vivimos en Collazo: una Utility se aprobaba como Marketing por el tono). Para México/LatAm, **Marketing cuesta bastante más que Utility**.

- **Reactivador** → va a caer como **MARKETING** sí o sí (es un empujón promocional). Asumir el costo. Además, Meta aplica **topes de frecuencia por usuario** a las plantillas de marketing.
- **Post-venta (pago/diseño/envío)** → redactar como **actualización transaccional atada al pedido específico del cliente** (tono neutro, sin signos de admiración, sin CTA promocional) para que Meta las deje en **UTILITY**. Mismo patrón que funcionó en la plantilla Utility de Collazo (`actualizacion_contacto_servicio`).

### §7.3 Coexistencia de dos BSP sobre un WABA (escenario A)

Para pre-aprobar plantillas sobre el WABA existente **sin cortar Kommo**, la gestión de plantillas es a nivel WABA y **no** requiere exclusividad de mensajería — así que crear/aprobar plantillas en Meta BM mientras Kommo sigue mensajeando **debería** funcionar. Lo que sí es exclusivo es el **registro del número para mensajería** (un solo proveedor). 🔍 Confirmar que crear plantillas en el WABA no interfiere con la sesión de Kommo (bajo riesgo, pero verificar en Meta BM).

### §7.4 El detalle de API de envío de plantilla desde n8n sigue sin confirmar

Ver §3.3 opción 2 y §9. Mitigado eligiendo la opción 1 (Workflow de GHL) para el MVP.

### §7.5 Higiene: rotar el token de Kommo

El JWT de Kommo/amoCRM (válido hasta 2030) y los `X-Auth-Token` de amojo están **hardcodeados en texto plano** en los workflows del repo (`06_docs/PENDIENTE-rotar-token-kommo.md`). Rotarlos/revocarlos en el cutover, antes de que la cuenta quede sin dueño operativo.

---

## §8. Plan accionable

**Fase 0 — Desbloquear (owner: Oscar + la agencia)**
- [ ] 🔍 Confirmar dueño del WABA en Meta BM (§2.4). **Gate de todo.**
- [ ] Anotar el conteo real de plantillas Meta existentes (reemplaza al "66").
- [ ] Decidir con Oscar qué capacidades fuera-de-ventana se quieren: ¿reactivador 24h+? ¿auto-notificar pago/diseño/envío? Esto fija cuántas plantillas se crean (0–4).

**Fase 1 — Preparar plantillas (owner: la agencia/Camilo + Oscar)**
- [ ] Redactar los textos fijos de las plantillas elegidas (Utility-friendly para post-venta, §7.2).
- [ ] Crear + mandar a aprobar en Meta BM (escenario A) o en la WABA nueva (escenario C). **24–72h de espera.**
- [ ] Construir el/los Workflow(s) de GHL "Send WhatsApp Template" + trigger desde n8n (§3.3 op. 1), testeados con número de prueba.

**Fase 2 — Cutover (owner: la agencia)**
- [ ] Switch atómico del número Kommo → GHL (madrugada sábado MX).
- [ ] Rotar/revocar tokens de Kommo (§7.5).
- [ ] Bajar assets de Kommo antes de la baja (§4.2 p.5).

**Fase 3 — Verificar (owner: la agencia)**
- [ ] Plantillas APPROVED y visibles en GHL.
- [ ] Prueba de envío real fuera de ventana de cada plantilla.
- [ ] Habilitar los flujos que las consumen.

---

## §9. 🔍 Verificaciones pendientes (lo que no pude confirmar headless)

Honestidad sobre los límites de esta investigación:

1. **Dueño del WABA (MIGRAR vs RECREAR).** No hay token de Meta Graph API ni acceso a Meta BM en este entorno. **Solo se confirma mirando `business.facebook.com`** (§2.4). Todo el timing depende de esto.
2. **Conteo real de plantillas Meta.** Idem — solo Meta BM o Graph API con WABA_ID + token. El "66" no está en el repo y no lo pude verificar.
3. **Envío de plantilla desde la API de GHL (op `send_template`).** No verificable sin WABA conectada (no se puede mandar una plantilla de prueba). Mitigado con la opción 1 (Workflow de GHL).
4. **Estado de la conexión WhatsApp en GHL.** La evidencia del repo (M7 "no arrancado", CRM doc "en traspaso", CLAUDE.md) dice **no conectada**; confirmar en GHL → Settings → Conversations.
5. **Inventario en vivo de Kommo.** La sonda de sólo-lectura a la API de Kommo quedó **bloqueada por el clasificador** (es una credencial de producción). Si se quiere el inventario desde Kommo, requiere aprobación explícita — pero es innecesario dado que el Graph API de Meta lo da mejor.

---

## §10. Apéndice — Evidencia verificada del vivo

**Identificadores GHL reales** (del código de W0, `VK4M7VQm8CMefbty`): API `https://services.leadconnectorhq.com`, LOC `onRwi0ZF4uYi0Lp6GAbE`, pipeline `RMnhLPqtXoWUBGZ0gvbh`. Etapas nuevas de reactivación: `R1 SIN INFORMACION` `56423525-…`, `R1 CON INFORMACION` `2ef6a2ab-…`, `R1 AP` `7450c408-…`.

**Cadencia W10 (`fpKvo0ECWIhFcckE`), verbatim del código `Decidir acción`:** las 4 campañas usan `olas: [60,240,300]` min y `eval_h: 24`. El hito 24h no envía; evalúa.

**Los 9 toques reactivadores (texto fijo en W10, in-window):**
- rebeca (etapa *Saludo Enviado*): A `60864` "Hola 👋, sigues por aquí? Solo necesito que me cuentes qué tipo de evento tienes…" · B `60866` "…es para boda, XV años u otro evento?…" · C `60868` "…no quiero que se te pase la oportunidad…"
- imagen (etapa *Evento Identificado*): D `60870` "…vi que me comentaste {evento}… Qué productos quieres que te recomiende…" · E `60872` "…sigues ahí?… hay algún producto que te haya llamado la atención…" · F `60874` "…para {evento} puedo ayudarte a elegir lo más bonito y útil…"
- cotización (etapa *Productos Mostrados*): G `60878` "…necesito que me compartas la cantidad y el código postal 📦" · H `60880` "…solo me falta saber cuántas piezas necesitas y tu código postal…" · I `60882` "…para apartar y cotizar tus productos necesito esos dos datos…"
- 7pasos (etapa *Cotizado*): **0 toques** — solo evalúa a 24h → `R1 CON INFORMACION` / `Ventas Perdidas`.

**Cliente de envío (W0):** op `send_text` → `POST /conversations/messages {type:'WhatsApp', message}`. **Sin op de plantilla.**

**Kommo:** subdominio `happyflopss.kommo.com` (API v4) / `happyflopss.amocrm.com` (salesbot/run legacy) / transporte `amojo.kommo.com`. `kommo_export.json` = 146 salesbots en cascarón (sin textos), 0 plantillas HSM.

**Fuentes del repo:** `04_guia_migracion/07_whatsapp_meta.md` · `03_arquitectura_ghl/06_integraciones.md §2` · `03_arquitectura_ghl/05_reengagement.md` · `06_docs/estado-crm-ghl-2026-07-27.md §8.4/§8.6` · `06_docs/diseno-reactivadores-r1-r2-2026-08-27.md` · `ESTADO_MIGRACION.md` (M7) · `06_docs/PENDIENTE-rotar-token-kommo.md`.
