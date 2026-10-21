# Revisión de portabilidad del número de WhatsApp — Venttur → GHL

**Fecha:** 2026-08-18 · **Pedido por:** Mauricio (prioridad #1 declarada) · **Estado:** diagnóstico hecho, falta **un dato del cliente** para dar veredicto final.

> **Por qué es prioridad.** Es la única pieza de toda la migración que depende de un tercero
> (ManyChat + Meta). Todo lo demás lo controlamos nosotros. Si sale mal y nos enteramos tarde,
> arrastra la fecha del 15/9.

---

## 1. Veredicto en una línea

**La migración es técnicamente viable y GHL la soporta de forma nativa** — *siempre y cuando el
número lo haya traído Venttur*. Si el número se lo dio ManyChat, **no es portable y no hay
discusión**: hay que comprar chip nuevo.

Todo se reduce a una sola pregunta, y hoy no la podemos responder desde el repo.

---

## 2. La pregunta decisiva

> ### ¿El número de WhatsApp del bot lo compró Venttur, o se lo dio ManyChat?

La documentación de ManyChat es explícita en que sus propios números son de un solo uso:

> *"If ManyChat provided your phone number, you will not be able to reconnect WhatsApp using that
> number, as those purchased from ManyChat are for single use only and cannot be utilized on
> platforms other than ManyChat."*

No es una restricción negociable ni un problema de soporte: es cómo está registrado el número del
lado de Meta.

| Respuesta | Consecuencia |
|---|---|
| **Lo trajo Venttur** (número propio, conectado por Embedded Signup) | ✅ Escenario A. La WABA vive en el Business Manager de Venttur y se migra conservando casi todo |
| **Lo dio ManyChat** | ❌ Escenario B. Número nuevo, sin vuelta |

---

## 3. Lo que NO pudimos determinar desde el repo (y por qué importa)

Buscamos en los 14 workflows, el snapshot de datos, los CSVs y toda la documentación del cliente:

| Dato | Estado |
|---|---|
| Número de WhatsApp con el que corre el bot | ❌ **No está en ninguna parte del repo** |
| WABA ID | ❌ No está |
| Business Manager que la contiene | ❌ No está |
| Quién proveyó el número | ❌ No está |

El `page_info` del snapshot de ManyChat devolvió `id: null` y ningún campo de teléfono; lo único que
trae es el nombre de la cuenta (`Venttur | Agente de IA`) y que es plan Pro.

⚠️ **Ojo con un malentendido fácil:** el número **+52 1 33 1944 2476** aparece 21 veces en la
documentación y es tentador tomarlo como el número del bot. **No lo es.** Es el número directo de
Rodrigo que el flow de Agenda comparte con el lead al agendar (*"se comunicará contigo por WhatsApp
directamente desde el número..."*). Puede o no coincidir con el del canal; hay que confirmarlo, no
asumirlo.

---

## 4. Escenario A — el número es de Venttur (migración viable)

GHL tiene un camino **nativo** para esto: en el onboarding de WhatsApp existe la opción
**"Migrating from an existing BSP"**, pensada exactamente para este caso.

> *"BSP migration is designed to move the existing WhatsApp Business Account to LeadConnector
> without creating a new WABA."*

### Qué se conserva

Meta preserva, al migrar el número entre WABAs: **el número, el display name, la calificación de
calidad, los límites de mensajería, el estado de Official Business Account y las plantillas
aprobadas.**

Dos matices que conviene saber de antemano:

- De las plantillas, Meta duplica **solo las que están APPROVED y con calidad GREEN**, hasta un tope
  de 250 por WABA. Las que estén en amarillo o rechazadas no viajan.
- La **calidad de las plantillas no se duplica**: quedan en `UNKNOWN` las primeras 24 h y después
  Meta recalifica con los datos nuevos.

### Requisitos previos (los tres son del lado de Venttur)

1. **Desactivar la verificación en dos pasos (2FA)** del número. Es la causa #1 de migraciones
   trabadas: *"Two-step verification can block or delay migration."*
2. **Verificación de negocio confirmada** en Meta Business Manager.
3. **Display name aprobado.**

### Downtime

Prácticamente nulo. La migración en sí no corta el servicio; **la única ventana de indisponibilidad
es el paso final de registro, y dura hasta que termina la duplicación de plantillas.** Se planifica
en una franja de bajo tráfico y listo.

---

## 5. Escenario B — el número lo dio ManyChat (no portable)

No hay workaround. Hay que dar de alta un número nuevo, y **el costo real no es el chip: es todo lo
que arrastra.**

| Qué se pierde | Impacto concreto en Venttur |
|---|---|
| El hilo con los contactos existentes | Los leads de Airtable tienen el número viejo agendado. Hay que avisarles con un broadcast |
| Calificación de calidad y **límite de mensajería** | Un número nuevo arranca en el escalón más bajo (típicamente **250 conversaciones iniciadas / 24 h** hasta que escala) |
| Plantillas aprobadas | Se re-crean y se re-aprueban desde cero. **La aprobación de Meta tarda 24 a 72 h** |
| Historial | No viaja |

**El límite de 250/24 h es el que más duele acá**, y no es teórico: en Collazo, avisar del cambio de
número a 426 contactos obligó a **partir el envío en dos días** (213 + 213) para no pasarse. Venttur
tiene un outreach tri-toque corriendo contra los leads del formulario de Meta — con un número nuevo
en el escalón bajo, ese outreach se estrangula justo en las primeras semanas post-cutover.

---

## 6. Precedente propio: Collazo (CLZ), junio 2026

Ya vivimos exactamente este problema y **terminó en el peor escenario**, así que conviene no
repetirlo por omisión.

Chatrace había registrado el número de Collazo **en una WABA propia de Chatrace, no en la del
cliente**. Al dar de baja la cuenta, el número quedó bloqueado: no había ningún "partner" que remover
desde el Business Manager de Collazo porque el Business Manager de Collazo nunca lo tuvo. Gestiones
en paralelo con soporte de Chatrace, Meta Business Support y ManyChat **no lo destrabaron**. Se
terminó activando un número nuevo.

**La lección aplicable:** el problema no se detecta desde la plataforma que estás usando, se detecta
mirando **de quién es la WABA en Business Manager**. Y se detecta *antes* de dar de baja nada, porque
después ya no hay palanca.

> ⚠️ **Regla dura heredada de ese caso:** nunca instalar la app de WhatsApp / WhatsApp Business en un
> número que va a Cloud API. Son excluyentes y repite el bloqueo.

---

## 7. Qué necesitamos de Venttur para cerrar el veredicto

Son cuatro cosas y salen todas de un lugar: **Meta Business Manager → WhatsApp Manager**.

1. **¿Con qué número corre el bot?** (el del canal de ManyChat, no el de Rodrigo).
2. **¿Ese número lo compraron ustedes o se los dio ManyChat?** Es la pregunta que define todo.
3. **Captura de WhatsApp Manager** mostrando la cuenta de WhatsApp Business (WABA) y qué número
   cuelga de ella. Ahí se ve si la WABA está dentro del portfolio de Venttur o no.
4. **¿La verificación de negocio está aprobada?** (aparece en Configuración del negocio → Centro de seguridad).

Con eso damos veredicto y plan en el día.

---

## 8. El segundo número, que nadie está contando

Recordatorio de la validación del 17/8: **hoy hay DOS números en operación.** Uno en ManyChat (el
agente) y otro en **Clientify** (los recordatorios de cita). La conversación sobre "portar el número"
viene tratándolo como si fuera uno solo.

**✅ RESUELTO (2026-08-18, decisión de la agencia y Mauricio):**

- **Sobrevive el del agente** (el de ManyChat). Es el que conocen los leads entrantes.
- **El de Clientify muere y NO se avisa.** Decisión explícita: no hay broadcast ni redirección. Quien
  le escriba a ese número después del apagado no le llega a nadie, y se asume.

→ Consecuencia práctica: **este punto sale del alcance.** No hay que presupuestar plantilla de aviso,
ni broadcast, ni la ventana de 250/24 h que ese envío habría necesitado.

---

## 9. Recomendación

**Intentar la migración, pero con fecha de corte.** El escenario A conserva la calificación de
calidad y los límites de mensajería, que es justo lo que protege al outreach en las semanas
inmediatamente posteriores al cutover. Vale el intento.

Ahora, la decisión ya está tomada por adelantado por el propio cliente (*"si la portabilidad no es
viable o implica riesgo de downtime, preferimos número nuevo"*), así que **no hace falta volver a
consultarlo**: alcanza con avisar y seguir.

Lo que sí propongo agregar es un **deadline propio**: si al **1 de septiembre** no tenemos la
migración confirmada y avanzando, se compra el chip nuevo. Eso deja dos semanas para re-aprobar
plantillas (24-72 h) y preparar el broadcast de aviso antes del 15/9. Sin ese corte, el riesgo es
quedar esperando a ManyChat hasta una semana antes del cutover y no tener plan B ejecutable.

---

## 10. Nivel de confianza de las fuentes

Para que nadie tome como verificado algo que no lo está:

| Afirmación | Confianza | Origen |
|---|---|---|
| GHL tiene camino nativo "Migrate from an existing BSP" y no recrea la WABA | 🟢 Alta | Artículo de soporte de GHL, leído directo |
| Prerequisitos: 2FA off, verificación de negocio, display name aprobado | 🟢 Alta | Mismo artículo |
| Qué preserva Meta al migrar (número, display name, calidad, límites, OBA, plantillas) | 🟢 Alta | Coincide en GHL y en varios BSP independientes |
| Solo migran plantillas APPROVED + GREEN, tope 250; calidad en UNKNOWN 24 h | 🟡 Media-alta | Documentación de BSPs, no verificado contra Meta directo |
| Números provistos por ManyChat son de un solo uso y no portables | 🟡 Media | Centro de ayuda de ManyChat vía búsqueda — **su sitio bloquea el acceso automatizado (403), no se pudo leer el artículo original**. Reconfirmar en la app o con soporte antes de decidir |
| Un número nuevo arranca en ~250 conversaciones iniciadas / 24 h | 🟢 Alta | Medido en Collazo (obligó a partir el broadcast en 2 días) |

---

## Anexo — Para mandarle a Mauricio y Max

```
Sobre la portabilidad del número, avanzamos y ya tenemos casi todo. La buena
noticia es que GoHighLevel soporta este tipo de migración de forma nativa y, si
sale, se conserva el número, el nombre visible, la calificación de calidad, los
límites de envío y las plantillas ya aprobadas. El corte de servicio es de
minutos, en el paso final.

Todo depende de una sola cosa, y es lo que necesitamos que nos confirmen:

1. ¿Con qué número corre hoy el bot? (el del canal de ManyChat, no el directo de
   Rodrigo que se comparte al agendar)

2. ¿Ese número lo compraron ustedes o se los dio ManyChat? Esto es lo que define
   todo: los números que provee ManyChat son de un solo uso y no se pueden mover
   a otra plataforma. Si el número es de ustedes, se migra sin problema.

3. Una captura de WhatsApp Manager dentro de su Business Manager, donde se vea la
   cuenta de WhatsApp Business y el número que cuelga de ella.

4. ¿La verificación de negocio de Meta está aprobada?

Con eso les damos el veredicto y el plan el mismo día.

Dos cosas más para tener en cuenta:

Si hay que ir a número nuevo, no es solo comprar el chip. Un número nuevo arranca
limitado a 250 conversaciones nuevas por día hasta que Meta lo va escalando, y las
plantillas hay que volver a aprobarlas, lo que tarda entre 1 y 3 días. Por eso
conviene resolverlo cuanto antes y no sobre la fecha.

Sobre el segundo número (el de Clientify, desde donde salen hoy los recordatorios):
quedó definido que se apaga junto con Clientify y que no se avisa. Lo dejamos así.
```
