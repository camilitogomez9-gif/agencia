# Guía de reunión — Max & Mauricio (última antes del traspaso WABA)

**Objetivo:** evacuar TODOS los bloqueantes (de ellos y nuestros) para que, saliendo de la reunión, solo quede **ejecutar el traspaso del número + testear**. Nada quede en el aire.

> Cómo usar esta guía: los bloques **🎯 RESOLVER**, **❓ PREGUNTAR** y **📢 COMUNICAR** son para hacer EN la reunión. Al final están los **próximos pasos**, los **bloqueantes** y las **preguntas sin respuesta**.

---

## 🎯 PUNTO #1 — El número (WABA). Sin esto, no hay cutover.

Es el único bloqueante que depende 100% de ellos y traba TODO el canal. **No salir de la reunión sin esto resuelto o con fecha de resolución.**

**La pregunta que define todo:** *¿el número del bot lo compró Venttur, o se lo dio ManyChat?*
- Si es de **Venttur** → se porta (escenario A, se conserva casi todo).
- Si lo dio **ManyChat** → no es portable, chip nuevo (escenario B). No hay vuelta.

**Los 4 datos a pedirles (salen de Meta Business Manager → WhatsApp Manager):**
1. ¿Con qué número corre HOY el bot? *(candidato: `+52 1 33 2627 4502`. **OJO: NO es `+52 1 33 1944 2476`** — ese es el directo de Rodrigo que se comparte al agendar.)*
2. ¿Ese número lo compraron ustedes o lo dio ManyChat?
3. **Captura** de WhatsApp Manager mostrando la WABA `1931874540684022` y **de qué Business Manager cuelga** (ahí se ve si está bajo el portfolio de Venttur → portable).
4. ¿La verificación de negocio está aprobada? *(Configuración del negocio → Centro de seguridad)*

**⚠️ Gotchas para decirles:**
- Se mira en el **Business Manager de Venttur**, no en ManyChat. El problema (si lo hay) no se ve desde ManyChat, se ve de quién es la WABA en el BM.
- Hay que verificarlo **ANTES de dar de baja nada** — después no hay palanca (precedente Collazo: quedó bloqueado y no se pudo destrabar ni con soporte de Meta).

---

## ❓ PREGUNTAR / PEDIRLES (decisiones + datos que solo ellos tienen)

**Decisiones de negocio:**
- **¿A qué asesor se asigna cada programa?** (cuando el bot deriva a un humano). Hoy va TODO a Mauricio por default → necesitamos el mapa programa→asesor.
- **¿Cada cuánto salen los seguimientos?** (a qué días/horas caen los 2 toques).
- **Leads históricos:** ¿qué hacemos con los ~5.000 leads viejos para no spamearlos cuando arranque el re-enganche? *(Riesgo real de spam masivo — necesitamos una regla, ej. "solo re-contactar los de los últimos X días".)*
- **"Cualificado":** confirmar que va como **etiqueta del contacto** (no como etapa del pipeline) y que el criterio queda: 2 idiomas + escuela privada bilingüe + edad del programa.
- **Fallback de calendarios:** si la disponibilidad compartida no sale nativa en GHL, se cae a "1 calendario por asesor" — necesitamos OK porque contradice lo que habían pedido (no dobles reservas).

**Los 3 programas nuevos (Viajes educativos, Educación superior, Cursos de idiomas):**
- **Etapas comerciales de "Viajes educativos"** (es 100% nuevo, no existe en Clientify).
- **Textos** propios (seguimiento/nurturing) y **precios** (hoy el bot no cotiza y pasa a asesoría — ¿se mantiene?).

**Datos y textos:**
- **Textos de confirmación de cita y de recordatorios** (24h y 1h antes) — hoy salen de Clientify, los tienen que dar ellos.
- **Mails (y chat de Telegram si usan) de Mauricio y Max** — para el aviso cuando el bot derive a un humano.
- **Tokens nuevos de Meta** (para el tracking de conversiones/CAPI) — los generan en su Business Manager.
- **2 textos de nurturing** que faltaron (`AA t4` y `Summer Camp t4`) + las 3 plantillas `seg_dia_3/5/7` → hay que abrirlas/exportarlas de ManyChat.

**Preguntas puntuales a confirmar:**
- **¿Quién era "Diego Matus"?** (2º Diego, 131 deals, ya no está — sus deals se reasignaron a Juan José Alfaro).
- **¿Dónde/cómo se calcula el "Lead Score"** (hot/warm/cold)? No lo encontramos en ningún lado.
- **Las "landings de aventureras"** que mencionó Max: **¿cuáles son exactamente y a dónde mandan los leads hoy?** (No hay ninguna landing con ese nombre en la doc que tenemos — ver bloque de agendamiento.)

---

## 📢 COMUNICARLES — lo que DEBEN HACER ellos (con el gotcha de cada uno)

1. **Verificar el WABA (2 min)** → define todo. *(ver Punto #1)*
2. **Si el número es portable, preparar 3 cosas del número:**
   - Desactivar la **verificación en dos pasos (2FA)**. *Gotcha: es la causa #1 de migraciones que se traban.*
   - **Verificación de negocio** confirmada en Meta.
   - **Display name** aprobado.
   - **NO instalar la app de WhatsApp/WhatsApp Business en ese número.** *Gotcha (regla dura): es excluyente con el sistema al que va — si la instalan, el número queda bloqueado.*
3. **Cada asesor (Rodrigo, Andrés, Diego) conecta su calendario personal** (Google/Outlook) a GHL. *Gotcha: sin esto no hay disponibilidad real ni forma de evitar dobles reservas.*
4. **Generar los tokens nuevos de Meta** (uno por pixel/programa). *Gotcha: el tracking sobrevive al cutover; si no se rotan, quedan claves viejas expuestas.*
5. **Respaldar Clientify ANTES de apagarlo.** *Gotcha CRÍTICO: entendieron que "migra todo", pero el **historial de chat, los adjuntos y las automatizaciones NO migran** a GHL — lo tienen que respaldar ellos. Clientify no se apaga hasta que respalden Y confirmemos el traspaso de datos.*

---

## 📅 AGENDAMIENTO / CALENDARIOS / LANDINGS (lo que preguntó Max)

**Calendarios — qué está y qué falta:**
- ✅ Hecho: la spec de los **8 calendarios** (uno por programa, con disponibilidad compartida por asesor: Rodrigo 3 · Andrés 5 · Diego fuera del ruteo) + los usuarios ya en GHL.
- ⏳ Falta: **crearlos** en GHL + que **los asesores conecten su calendario personal** + validar el mecanismo de disponibilidad compartida.
- 🟢 **Se puede hacer ANTES del número** — solo el envío de la confirmación/recordatorio al lead espera el canal.

| Programa | Asesor | Link viejo (muere) |
|---|---|---|
| Internados | Rodrigo | agendar-ema |
| Intercambio c/ familias | Rodrigo | AAFamilia-Agendar |
| Campamentos de verano | Rodrigo | SummerCamp-Agendar |
| Pathway Alemania | Andrés | PW_Alemania_Agendar |
| Gap Year / Estudia y Trabaja | Andrés | Estudiar-y-Trabajar-en-Australia |
| Viajes educativos ⭐ | Andrés | *(no existía)* |
| Educación superior ⭐ | Andrés | *(no existía)* |
| Cursos de idiomas ⭐ | Andrés | *(a confirmar)* |

- ⚠️ **Bug actual a mencionar:** hoy la confirmación de cita está **rota** — **0 de 11 leads que agendaron recibieron confirmación** (los flujos de Andrés y Diego apuntan a nodos que no existen). Se reconstruye en la migración. Además el fallback manda a todos a `agendar-ema` (Rodrigo/Internados), aunque el programa sea otro — se arregla con los 8 calendarios reales.

**Landings ("aventureras"):**
- **No existe ninguna landing "aventureras" en la documentación que tenemos** → **preguntarle a Max exactamente cuáles son y a dónde mandan los leads hoy.**
- Lo que SÍ tenemos mapeado: el **formulario nativo de Meta** (Internados, es lo activo para tráfico pago) y la landing **`go.venttur.com/bs`** (viva, orgánicos) — esa hay que **repuntarla a GHL** para que no quede muerta. Los otros 7 programas no tienen landing.
- **Proceso de migración de landings:** el formulario hoy crea el lead en Airtable+Clientify; se reconstruye para que **cree el contacto en GHL** (conservando el programa de interés). El registro de la conversión (CAPI) se queda en n8n. **Esto también se puede adelantar sin el número.**

---

## 📢 ALINEAR / DEJAR CLARO (temas a poner sobre la mesa)

- **La fecha del 15/9 ya no es viable** (falta resolver el número + las plantillas tardan 24-72h en aprobarse). **Acordar una fecha nueva de cutover en esta reunión.**
- **Escenario chip nuevo (si no porta):** arranca limitado a **250 conversaciones nuevas/día** hasta que Meta lo escala, y las plantillas se re-aprueban de cero (24-72h). El chip tiene que estar **activo antes** del cutover. Por eso conviene resolver el número YA.
- **El 2º número (Clientify, recordatorios):** quedó decidido que **muere y no se avisa**. Confirmar que sigue firme.
- **Cutover "todo de una" (Opción A):** lo eligieron ellos contra nuestra recomendación de ir por olas. Recordar que junta 3 dependencias de terceros el mismo día = más riesgo. Reconfirmar o repensar.

---

## ➡️ PRÓXIMOS PASOS (después de la reunión)

**Ellos (cliente) destraban:** WABA + prereqs del número + conectar calendarios + tokens Meta + respaldar Clientify + decisiones y textos.

**Nosotros, EN PARALELO (no espera el número) — apenas tengamos su parte:**
- Crear los 8 calendarios + validar disponibilidad compartida.
- Reimportar y probar el estado "Cerrada".
- Terminar el despachador de re-enganche (con la política de históricos que definan).
- Construir el aviso de handoff (con los mails/chat ids).
- Dejar las ~38 plantillas listas + formatear las que faltan.
- Repuntar la landing `go.venttur.com/bs` a GHL.

**Nosotros, cuando el número esté conectado:**
- Subir las plantillas a Meta (24-72h de aprobación).
- Cablear el envío real por WhatsApp + audio.
- Validaciones de sandbox + **testing E2E completo** (prerequisito duro).
- Traspaso del WABA en franja de bajo tráfico → cutover → 48h de monitoreo.

**En una línea:** el 90% de lo que falta se puede adelantar YA; lo único que frena de verdad es el número.

---

## 🔴 BLOQUEANTES REGISTRADOS (abiertos, para no perderlos de vista)

| # | Bloqueante | Depende de | Traba |
|---|---|---|---|
| B-05/07 | **WABA / número** (portar vs chip nuevo) | Cliente (2 min) | TODO el canal — deadline propio 1/9 vencido |
| B-07 | **Plantillas Meta** (subir + aprobación 24-72h) | Agencia + Meta | Re-enganche, recordatorios en vivo |
| B-09 | **Etapas de "Viajes educativos"** | Cliente/comercial | Cierre de scope |
| B-10 | **8 calendarios** (crear + disponibilidad + OAuth asesores) | Agencia + Cliente | Agendamiento, confirmación, recordatorios |
| B-N1 | **Aviso de handoff** (Workflow GHL + mails/chat ids) | Agencia + Cliente | Que las elevaciones no queden en limbo |
| — | **Política de históricos del despachador** | Cliente decide | Evitar spam masivo en la 1ª corrida |
| — | **Confirmación de cita rota (0/11)** | Agencia | Se reconstruye |
| — | **Prompt del cutover sin decidir** (vivo 39K vs v2.0 47K) | Agencia | Qué se testea y despliega |
| — | **Secretos a rotar** (OpenAI, Meta CAPI, ManyChat, Clientify) | Agencia + Cliente | Seguridad pre-cutover |
| — | **Validaciones de sandbox** (envío free-form, trigger de entrada, audio, booking) | Agencia (con nº de test) | Gated en el canal vivo |

---

## ❔ Preguntas SIN respuesta en la doc (confirmar sí o sí en la reunión)

1. **Landings "de aventureras"** — no existen en nuestra doc. ¿Cuáles son y a dónde mandan los leads?
2. **¿Quién era Diego Matus?** (131 deals reasignados).
3. **¿Dónde se calcula el Lead Score** (hot/warm/cold)?
4. **La nueva fecha de cutover** (el 15/9 es inviable).
5. **Precios de los 3 programas huérfanos** (hoy figuran como "-").

---

*Nota: preparando esta guía no tuve bloqueantes de acceso — verifiqué todo contra los docs reales de la migración. Las 5 preguntas de arriba son los únicos puntos que la documentación no resuelve y que solo el cliente puede cerrar.*
