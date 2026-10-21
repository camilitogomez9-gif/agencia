# Plan de recuperación — Número WhatsApp viejo +598 91339312 (2026-07-01)

> Contexto previo: `06_docs/migracion-whatsapp-manychat-2026-06-30.md` (incidente + Plan B con número nuevo, ya en producción). Este doc es el plan específico para recuperar el número viejo, que sigue atrapado en la WABA de Chatrace.

**Encuadre:** esto es recuperación de un activo propio del cliente (su número histórico) atrapado en un proceso de negocio con un ex-proveedor — no un objetivo de intrusión. Todo lo que sigue usa mecanismos oficiales y documentados de Meta/WhatsApp Business Platform y canales de soporte legítimos.

**Confirmado con la agencia antes de investigar:** el chip +598 91339312 sigue físicamente activo y accesible (puede recibir SMS/llamada) → esto habilita el camino de auto-liberación de la Opción A. la agencia es admin del Business Manager de Collazo.

---

## 1. Diagnóstico técnico afinado

Dos hallazgos nuevos respecto al doc del 2026-06-30:

### 1.1 — Chatrace corre sobre **360dialog** como BSP subyacente

Chatrace no es un BSP (Business Solution Provider) en sí mismo — es una plataforma de automatización que se integra sobre la infraestructura API de **360dialog** (BSP oficial de Meta, Solution Partner). Esto explica por qué Chatrace support no podía darles una respuesta clara ("no tenemos el número de nuestro lado"): la WABA real donde vive el número probablemente está del lado de 360dialog, no en un sistema propio de Chatrace. **360dialog es un canal de soporte nuevo, no contactado todavía**, con capacidad técnica directa sobre la WABA.

### 1.2 — El bloqueo real probablemente es la verificación en dos pasos (2FA/PIN), no la WABA en sí

Fuentes oficiales (Meta for Developers, respond.io, Infobip, insiderOne — todos BSPs que documentan su propio flujo de migración) coinciden en un prerrequisito común para migrar un número entre BSPs: **la verificación en dos pasos (PIN de 6 dígitos) debe estar desactivada** en el número. Si el número se dio de alta por el flujo "clásico" (no self-service), hay que **pedirle al proveedor actual que la desactive** — y ese es exactamente el pedido que Chatrace nunca pudo/quiso resolver.

Esto reformula el problema de "¿cómo recuperamos la WABA?" a algo mucho más preciso y accionable: **"¿tiene este número un PIN de 2FA que no conocemos?"** — pregunta que se puede responder hoy mismo, sin depender de que nadie coopere (ver Opción A).

---

## 2. Opción A — Auto-liberación (probar HOY, antes que nada)

Basado en un mecanismo confirmado por un moderador oficial de la comunidad de ManyChat para exactamente este escenario (número atascado con un proveedor anterior no cooperativo): un número de WhatsApp solo puede estar registrado en **un** lugar a la vez (app personal, WhatsApp Business app, o Business API vía un BSP). Registrar el número en la app **personal** de WhatsApp (no Business) fuerza a Meta a soltar cualquier vínculo previo con la WABA/BSP anterior — sin necesitar que Chatrace haga nada.

**Esto NO toca el número nuevo ni la conexión ManyChat/n8n que ya está en producción** — son números distintos y WABAs distintas.

### Pasos

1. Conseguir un teléfono cualquiera (no importa si es Android o iPhone, no hace falta que sea el celular "oficial" del negocio).
2. Instalar **WhatsApp normal** (no WhatsApp Business — la versión personal simplifica el flujo).
3. Registrar el número **+598 91339312** → Meta manda un SMS/llamada con código OTP.
4. **Acá hay dos resultados posibles:**

   **(a) Se registra sin pedir PIN** → el número NO tenía 2FA activo. Al confirmar el OTP, WhatsApp automáticamente invalida el registro anterior en la WABA de Chatrace/360dialog (por eso decían "the number is disconnected from our platform" — puede que ya esté parcialmente cierto y sea justo el 2FA lo único que falta destrabar).
   - Inmediatamente: `Ajustes → Cuenta → Eliminar mi cuenta` para volver a soltar el número (si no, queda "ocupado" en la app personal y no se puede migrar a Business API).
   - Esperar ~3 minutos (tiempo de propagación en los sistemas de Meta).
   - Seguir el flujo que ya usaron con el número nuevo: ManyChat → Settings → WhatsApp → Connect → **"Transfer your own WhatsApp number"** → Embedded Signup → seleccionar la WABA real de Collazo (`10111928183308888`) → verificar por OTP → conectado.
   - **Con esto, la Opción B (tickets) deja de ser necesaria** — se puede avisar a los 3 soportes que ya se resolvió y cerrar los casos.

   **(b) Pide un PIN de verificación en dos pasos que no conocen** → confirma que Chatrace/360dialog sí activó 2FA. En este caso:
   - Tocar **"¿Olvidaste tu PIN?" → "Restablecer"** de inmediato — esto arranca el conteo oficial de **7 días** que Meta exige antes de poder resetear el PIN sin conocerlo (política de seguridad de WhatsApp, no hay forma de acelerarlo). Conviene arrancar este reloj YA, en paralelo con la Opción B, para no perder tiempo.
   - Si el número tiene un email de recuperación configurado (poco probable que sea de Collazo y no de Chatrace, pero vale confirmar) hay una vía de reset más rápida por mail.

   **(c) Error "WhatsApp no está disponible en este momento, intentá de nuevo en 1 hora"** → NO es (a) ni (b). Es un **bloqueo temporal de seguridad por rate-limit**, no una respuesta sobre 2FA ni la WABA. Ver §2.1 abajo.

---

## 2.1 — Resultado del 1er intento de Opción A (2026-07-10) — RATE LIMIT

Matías ejecutó la Opción A y grabó el intento (video `WhatsApp Video 2026-07-10 at 22.11.42.mp4`). Secuencia observada:

1. WhatsApp (app normal) → "Ingresa tu número de teléfono" → Uruguay, **+598 91 339 312** → Siguiente.
2. "¿Este es el número correcto? +598 91 339 312" → Sí.
3. "Verificación de tu número — Esperando detectar automáticamente el código de 6 dígitos que enviamos por SMS al +598 91 339 312" → "Enviando código…".
4. **Error: "WhatsApp no está disponible en este momento. Por favor, intenta de nuevo en 1 hora."**

**Lectura correcta:** esto es un **throttle de seguridad de WhatsApp por demasiados intentos de verificación** en poco tiempo (sobre ese número o ese dispositivo). NO es la respuesta que buscábamos:
- NO llegó a pedir PIN → **seguimos sin saber si el número tiene 2FA activo** (el bloqueo saltó antes de esa pantalla).
- NO dio el error de "número ya registrado en una cuenta de negocio" → la app estaba dispuesta a mandar el OTP, o sea el camino de auto-liberación **no está descartado**, solo interrumpido por el rate-limit.

**Regla de oro ahora — NO reintentar.** Cada reintento **reinicia y alarga** el reloj (1 h → 6 h → hasta 24 h). El error más común es seguir tocando "reenviar código" y empeorar el bloqueo. La "1 hora" es un piso, no una garantía.

**Higiene para el próximo intento (uno solo, bien hecho):**
- Esperar bastante más que 1 hora — **ideal: de un día para el otro** (bloqueo limpio).
- Reiniciar el celular antes de reintentar.
- Un solo intento. Si el SMS no llega en ~1-2 min, usar la opción **"Llamarme" / "Llamada"** en vez de SMS (el OTP por voz a veces entra cuando el SMS no).
- Conexión estable (probar datos móviles si venían con Wi-Fi o viceversa).
- Confirmar que sea **WhatsApp normal**, no WhatsApp Business (la versión personal simplifica el forzado de liberación).

**Qué NO cambia:** la Opción B (los 4 mensajes de soporte de abajo) no depende para nada de este throttle → conviene mandarlos **ahora mismo, en paralelo**, mientras el número "descansa". Especialmente 360dialog (canal nuevo) y Chatrace con el ask preciso de desactivar 2FA.

---

## 3. Opción B — Escalación en paralelo (4 canales)

Independientemente del resultado de la Opción A, conviene mandar estos 4 mensajes hoy mismo — si la Opción A destraba todo, simplemente se cierran los casos como resueltos.

### 3.1 — Chatrace support (mensaje de seguimiento, más preciso que los anteriores)

> Asunto: Seguimiento — liberación de +598 91339312 (WABA Collazo Servicio Técnico)
>
> Hola,
>
> Seguimos sin poder migrar nuestro número +598 91339312 fuera de su plataforma. Entendemos que Chatrace opera su integración de WhatsApp sobre **360dialog** como Business Solution Provider. Les pedimos específicamente uno de estos dos pasos (cualquiera de los dos nos destraba):
>
> 1. **Desactivar la verificación en dos pasos (PIN de 2FA)** del número +598 91339312 en la WABA donde está registrado, o
> 2. **Liberar/desregistrar formalmente el número** de esa WABA (a través de su panel de 360dialog o pidiéndoselo directamente a 360dialog).
>
> Si no tienen acceso directo a esto, ¿pueden confirmarnos el WABA ID o darnos el contacto de su representante en 360dialog para que lo resolvamos directamente con ellos?
>
> Gracias.

### 3.2 — 360dialog support (canal nuevo, no contactado todavía)

Canales oficiales: chat vía **360dialog Hub** (si tienen o consiguen acceso), email **support@360dialog.com**, WhatsApp **+49 30 577140819**. Tiempos de respuesta: <24hs (plan básico) a <30min (premium) — el email/WhatsApp dan respuesta inicial en <24hs sin importar el plan.

> Asunto: Liberación de número de cliente final de Chatrace — +598 91339312
>
> Hola,
>
> Somos la agencia, agencia que representa a Collazo Servicio Técnico (Uruguay), cliente final de **Chatrace**, que entendemos corre su integración de WhatsApp sobre la infraestructura de 360dialog.
>
> El número **+598 91339312** quedó registrado en una WABA que no es la propia de nuestro cliente (WABA de Collazo: `10111928183308888`), y no tenemos visibilidad ni acceso a esa WABA intermedia. Chatrace nos dio respuestas contradictorias y no pudo liberar el número.
>
> Necesitamos que se **desactive la verificación en dos pasos (2FA/PIN)** de ese número, o que se **libere/desregistre** de la WABA donde está, para poder migrarlo a la WABA propia del cliente vía Embedded Signup.
>
> ¿Pueden ayudarnos u orientarnos sobre el proceso correcto dado que no somos cliente directo de 360dialog sino de un partner/reseller (Chatrace)?
>
> Gracias.

### 3.3 — Meta Business Support (mensaje de seguimiento más técnico, sobre el caso ya abierto)

> Seguimiento del caso abierto el 2026-06-30 (Business Manager de la agencia Automation). Al intentar migrar el número **+598 91339312** a nuestra WABA (`10111928183308888`, Business Manager de Collazo Servicio Técnico) vía Embedded Signup, recibimos el error: *"El número de teléfono ya está en uso. Este número de teléfono ya está registrado con una cuenta de WhatsApp. Para continuar, migra este número de teléfono o desconéctalo de esa cuenta."*
>
> El número está actualmente en una WABA controlada por nuestro ex-proveedor (Chatrace, sobre infraestructura de 360dialog), a la que no tenemos acceso. Chatrace no ha podido/querido liberar el número pese a múltiples pedidos.
>
> Solicitamos el proceso de **recuperación/disputa de número de teléfono** (Phone Number Recovery / número que un partner mantiene inactivo) para poder recuperar el control de nuestro propio número de negocio. Podemos verificar la titularidad del número vía OTP en cualquier momento — seguimos teniendo control físico de la línea.

### 3.4 — ManyChat support (actualización del ticket ya abierto)

> Actualización de nuestro ticket sobre +598 91339312: confirmamos que nuestro proveedor anterior (Chatrace) corre sobre **360dialog** como BSP. ¿Pueden escalar a Meta Partner Operations con este dato específico, o coordinar directamente con 360dialog dado que son ambos Solution Partners de Meta? Seguimos teniendo control físico del número (podemos recibir OTP) y ya conectamos exitosamente un número nuevo a la misma WABA (`10111928183308888`) usando "Transfer your own WhatsApp number", así que el resto de la configuración ya está lista del lado de Collazo.

---

## 4. Orden recomendado de ejecución

1. **Hoy, ~10 min:** correr la Opción A (registrar +598 91339312 en WhatsApp personal en cualquier celular). Esto es gratis, reversible, y no toca nada de lo que ya está en producción.
2. **Según resultado:**
   - Sin PIN → completar el flujo de liberación + reconectar a ManyChat (mismo proceso que ya usaron con el número nuevo). Avisar a los 3 soportes que se resolvió, cerrar casos.
   - Con PIN → tocar "Olvidaste tu PIN → Restablecer" para arrancar el reloj de 7 días YA.
3. **Hoy mismo, en paralelo:** mandar los 4 mensajes de la Opción B (Chatrace, 360dialog, Meta, ManyChat) — best case, alguno de los 4 libera el 2FA antes de que se cumplan los 7 días y se salta la espera.
4. **Si en 7 días nadie respondió:** completar el reset de PIN por la vía oficial de WhatsApp y retomar el flujo de Embedded Signup normal.

## 5. Riesgos / cosas a confirmar antes de arrancar

- Confirmar que el número viejo no tiene **ninguna otra dependencia activa** hoy (según CLIENT_INFO.md, Chatrace ya está en desuso — parece seguro, pero vale el doble check con Matías antes de tocarlo).
- Si el número tenía plantillas de mensajes aprobadas o historial importante en la WABA vieja, eso se pierde al liberar — dado que ya migraron operación al número nuevo, es bajo impacto.
- 360dialog podría no atender pedidos de alguien que no es su cliente directo (Collazo es cliente de Chatrace, no de 360dialog) — por eso el mensaje 3.2 aclara la relación y pide orientación explícita.

## 6. Fuentes consultadas

- [Migrating a business phone number from one Solution Partner to another via Embedded Signup — Meta for Developers](https://developers.facebook.com/documentation/business-messaging/whatsapp/solution-providers/support/migrating-phone-numbers-among-solution-partners-via-embedded-signup/)
- [Migrate an existing WhatsApp Number to a Business Account — Meta for Developers](https://developers.facebook.com/documentation/business-messaging/whatsapp/solution-providers/migrate-existing-whatsapp-number-to-a-business-account/)
- [Phone Number Migration to respond.io WhatsApp Business Platform](https://respond.io/help/whatsapp/phone-number-migration-to-respond-whatsapp-business-api)
- [Migrate WhatsApp Phone Numbers — Insider One Academy](https://academy.insiderone.com/docs/migrate-whatsapp-phone-numbers)
- [How to reset your two-step verification PIN — WhatsApp Help Center](https://faq.whatsapp.com/2183055648554771)
- [About registration and two-step verification — WhatsApp Help Center](https://faq.whatsapp.com/506595211487528)
- [ManyChat Community — Issue connecting WhatsApp with Coexistence (workaround de app personal)](https://community.manychat.com/general-q-a-43/issue-conecting-whatsapp-with-coexistence-9069)
- [Why you should use 360dialog as BSP — Client Documentation](https://docs.360dialog.com/docs/welcome-to-360dialog/why-you-should-use-360dialog-as-business-solution-provider-bsp)
- [Get support — 360dialog Client Documentation](https://docs.360dialog.com/docs/support/get-support)
- [Error: "This number is registered to an existing WhatsApp account" — eGrow Help Center](https://help.egrow.com/en/article/this-number-is-registered-to-an-existing-whatsapp-business-account-on-another-business-solution-provider)
- [Error: "This phone number is already registered to a WhatsApp account" — GoHighLevel Support](https://help.gohighlevel.com/support/solutions/articles/155000007276-error-this-phone-number-is-already-registered-to-a-whatsapp-account-)
