# Agente de soporte técnico TOFO Pizza
## Guía de implementación — qué hay que tener listo antes de coordinar el alta

**Versión 1.0 — Junio 2026**

---

## 1. Para qué sirve este documento

Compraste una máquina TOFO y quieres sumar un agente automatizado que responda fallas técnicas a tus clientes por WhatsApp. Esta guía indica exactamente qué hay que tener listo antes de coordinar la implementación.

Si arrancas de cero (sin Meta Business Manager ni WhatsApp Business previos), la infraestructura se prepara en **1 semana**. La mayor parte del tiempo de espera depende de Meta — una vez activada la verificación, el resto avanza rápido.

---

## 2. Qué hace el agente y qué NO hace

### Qué hace

- Atiende fallas técnicas de tu máquina por WhatsApp 24 horas, todos los días. El cliente escribe, el agente responde.
- Reconoce los síntomas más comunes: la pizza no salió, pantalla congelada, doble cobro, pizza fría, sabor equivocado, problema con el pago.
- Le pide al cliente la **foto del problema + foto del ticket de compra**. Sin evidencia no entrega códigos de reposición — eso te protege contra fraude.
- Si la falla es resoluble dentro de lo que aprendió, te genera un código de reposición según las reglas que tú definas.
- Si la falla no puede resolverse (es algo nuevo, el cliente está enojado, o pide algo fuera de su alcance), avisa al instante a tu Telegram con un resumen completo de la conversación, para que tu técnico humano tome el caso.
- Mantiene memoria de la conversación — si el cliente vuelve un día después, el agente recuerda dónde quedó la charla.
- Detecta los canales: si el cliente escribe por Instagram o Facebook, también puede responder por ahí (depende de cuáles se activen).

### Qué NO hace

Importante saber esto para no esperar lo que no va a entregar:

- **No vende.** Si un cliente pregunta dónde comprar una máquina, el agente le dice "no tengo esa información" y lo redirige cortésmente.
- **No agenda visitas técnicas presenciales.** Si la falla requiere visita, el agente escala a tu técnico humano y el cierre se coordina por afuera.
- **No responde por inversión o franquicia.** Si alguien pregunta cuánto vale tener una máquina TOFO, lo desvía amablemente.
- **No acepta reembolsos.** Si el cliente pide devolución del dinero, escala a ti. La política de reembolso la manejas directo.
- **No factura.** Si el cliente pide factura por su consumo, escala a ti.
- **No maneja redes sociales** (comentarios públicos, historias, contenido).
- **No inventa información que no sabe.** Si le preguntan algo que no está cargado en su catálogo, lo dice y deriva. No "completa" con información incorrecta. Esa es una regla central, aprendida por las malas.

---

## 3. Checklist resumido

Esto es lo que conviene tener tildado antes de avisar que está todo listo para implementar.

| Ítem | Estado | Quién lo hace |
|---|---|---|
| Cuenta Meta Business Manager verificada | ☐ | Tú (con tu contador para RFC) |
| Número de WhatsApp Business dedicado al soporte | ☐ | Tú (chip nuevo o VoIP — no usar el personal) |
| Cuenta ManyChat Pro vinculada a tu WhatsApp | ☐ | Tú con acompañamiento del responsable |
| Cuenta n8n (Cloud o instalada en VPS) | ☐ | Se decide en conjunto según presupuesto |
| OpenAI API key con saldo cargado | ☐ | Tú |
| Base de datos elegida (Airtable o Supabase) | ☐ | Tú con la recomendación del responsable |
| Catálogo de tus máquinas completo (cuántas, dónde, sabores, precios) | ☐ | Tú |
| Contacto del técnico humano que recibe escalamientos | ☐ | Tú |
| Plantilla de respuestas (cómo se presenta el agente, qué cierre usa) | ☐ | Tú completas un formulario corto |
| Bot de Telegram para alertas (opcional pero muy recomendado) | ☐ | Tú con apoyo del responsable |

Cada uno de estos se detalla en la sección 4.

---

## 4. Detalle por plataforma

Una subsección por componente. Se explica qué es, para qué se usa, cómo crear la cuenta, cuánto cuesta, y qué se necesita de tu parte una vez que esté lista.

### 4.1 Meta Business Manager — el primer paso

**Qué es:** la cuenta corporativa de Meta (Facebook + Instagram + WhatsApp). Es la que valida tu negocio como real ante Meta. Sin esto, no se puede vincular WhatsApp Business a la API que usa el agente.

**Cómo se crea:** entra a [business.facebook.com](https://business.facebook.com/) → "Crear cuenta" → cargas los datos de tu negocio + un comprobante de domicilio + tu identificación fiscal (RFC). Meta revisa la documentación.

**Tiempo:** 2 a 7 días de revisión por parte de Meta. Es el cuello de botella real de toda la implementación. Empieza por acá.

**Costo:** gratis.

**Qué se necesita de tu parte:** el ID de tu Business Manager (se ve en la URL una vez verificado: `business.facebook.com/?business_id=XXXXX`).

---

### 4.2 Número de WhatsApp Business dedicado

**Por qué tiene que ser dedicado:** una vez vinculado a la API de Meta y a ManyChat, ese número **no se puede usar desde la app de WhatsApp normal**. Si usas tu personal, lo pierdes para chatear con tus contactos. Tiene que ser un número nuevo, exclusivo del soporte de la pizzería.

**Opciones:**
- **Chip físico nuevo:** compras una SIM con un número fresco. Funciona pero obliga a tener el chip en algún equipo. Costo: el del chip + cargas mensuales si es móvil.
- **Número VoIP (recomendado):** un número fijo virtual de proveedores como Aircall, Voys o MicroSIP. No depende de chip físico, no se pierde si se rompe un teléfono. Costo: USD 5 a 15 por mes según el proveedor.

**Tiempo:** activación inmediata una vez que tienes el número. La verificación en Meta Business Suite tarda 1 a 2 días.

**Qué se necesita de tu parte:** el número confirmado y, en el momento de activarlo en ManyChat, el código de verificación de 6 dígitos que Meta manda por SMS o llamada.

---

### 4.3 ManyChat Pro

**Qué es:** la plataforma que conecta tu WhatsApp con el resto del sistema. Es donde se reciben los mensajes del cliente final, donde se pausa el bot cuando escala a tu técnico, y donde el agente le manda las respuestas.

**Por qué Pro y no Free:** el plan Free no permite las integraciones outbound vía API que el agente necesita para responder. El Pro habilita los componentes "External Request" y "External Trigger", que son los que hacen funcionar todo. No hay forma de hacerlo con el Free.

**Cómo se crea:** entras a [manychat.com](https://manychat.com/) → Sign up → conectas tu WhatsApp Business via API (no la Business app — la API, que es lo que Meta verificó en el paso 4.1).

**Costo:** USD 15 por mes hasta 500 contactos (suficiente para una pizzería que arranca). Escala automáticamente a USD 25 a 50 por mes si superas los 2.500 contactos. Para 1 a 3 máquinas, el plan inicial alcanza tranquilo.

**Qué se necesita de tu parte:** acceso a tu cuenta como Editor (no como Admin, no hace falta ese nivel). Desde ahí se configuran los flows necesarios y los webhooks.

---

### 4.4 n8n — el motor del agente

Es donde corre la lógica del agente. Hay dos caminos según la situación.

#### Opción A — n8n Cloud (recomendado para empezar)

**Qué es:** un n8n hospedado por la gente que hace el producto. Te suscribes, te dan una URL, y listo. Cero servidor que mantener.

**Cómo se crea:** [n8n.io](https://n8n.io/) → plan Starter (USD 20 por mes, 2.500 ejecuciones mensuales) o Pro (USD 50 por mes, 10.000 ejecuciones).

**¿Cuánto consume el agente?:** cada mensaje del cliente final consume entre 3 y 6 ejecuciones (un mensaje entrante puede disparar varios pasos internos). En una pizzería chica de 1 máquina, con 50 a 150 conversaciones por mes, el plan Starter alcanza.

**Costo:** USD 20 a 50 por mes.

**Ventaja:** sin mantenimiento, updates automáticos, SSL incluido. La opción más simple para arrancar.

**Desventaja:** tope mensual de ejecuciones. Si tu pizzería crece fuerte, eventualmente conviene mover a self-hosted.

#### Opción B — n8n self-hosted en VPS

**Qué es:** pagas un servidor virtual chico (VPS) y ahí corre tu propio n8n. Sale más barato a largo plazo, pero requiere a alguien que sepa configurar Docker, dominios y SSL.

**VPS recomendados:** Hetzner CX22 (USD 5 por mes, 4 GB RAM) o DigitalOcean Basic Droplet (USD 6 por mes).

**Requisitos mínimos:** 2 GB RAM, 2 vCPU, 40 GB de disco, Ubuntu 22.04 o superior, Docker instalado.

**También se requiere:**
- **Un subdominio** apuntando al VPS (ejemplo: `agente.tupizzeria.com`). Si no tienes dominio, sale unos USD 12 al año.
- **SSL gratuito con Let's Encrypt** vía Caddy o Traefik. Queda configurado en una sesión.

**Costo total:** USD 5 a 10 por mes (VPS + dominio prorrateado).

**Qué se necesita de tu parte:** acceso SSH al VPS + control DNS del subdominio. La configuración inicial se hace en una sesión de 1 a 2 horas con tu dev.

#### Recomendación

Si tienes 1 máquina, arranca con **n8n Cloud Starter**. Te ahorras dolores de servidor y el costo extra de USD 15 al mes vale la simplicidad. Si tienes 3 o más máquinas, el VPS self-hosted se paga el cambio en 4 o 5 meses.

---

### 4.5 OpenAI API key con saldo

**Qué es:** el "cerebro" del agente. Cada respuesta que el agente genera consume tokens, cada token cuesta fracciones de centavo, pero suma si hay mucho tráfico.

**Cómo se crea:** [platform.openai.com](https://platform.openai.com/) → Sign up → Billing → cargar mínimo USD 20 inicial (recomendado USD 50 para no quedarse corto las primeras semanas). Después se crea una API key con permiso "All" desde la sección API Keys.

**Estimación de consumo según volumen:**

| Tamaño de operación | Conversaciones por mes | Costo OpenAI estimado |
|---|---|---|
| Pizzería chica (1 máquina, arranque) | 50 a 150 | USD 10 a 25 / mes |
| Pizzería media (1-2 máquinas activas) | 300 a 600 | USD 30 a 80 / mes |
| Pizzería grande (3+ máquinas) | 1.000+ | USD 100 a 200 / mes |

**Recomendación operativa:** activa "Auto-recharge" para que cuando el saldo baje de USD 5, OpenAI recargue automáticamente USD 20. Así se evita que el agente se quede colgado un fin de semana sin responder por falta de crédito.

**Qué se necesita de tu parte:** la API key (`sk-...`). Se indica cómo pasarla de forma segura (no por WhatsApp, no por email plano — se usa un canal cifrado).

---

### 4.6 Base de datos — elegir una opción

Acá se guarda el historial de cada conversación (para que el agente recuerde) y cada caso de falla registrado. Hay dos caminos.

#### Opción simple — Airtable

**Qué pasa ahí:** queda el historial de conversaciones como filas en una planilla. Si quieres ver qué pasó con un cliente, abres Airtable y lo ves como una tabla, igual que un Excel.

**Plan:** Free alcanza para arrancar (hasta 1.200 registros por base). El plan Team de USD 20 al mes te da más vistas y más registros si crece la operación.

**Ventaja:** puedes entrar y mirar los datos sin saber nada técnico. En el handoff queda explicado cómo usarlo.

**Qué se necesita de tu parte:** crear el workspace y dar acceso como Collaborator + un Personal Access Token (se genera en Account Settings) para que n8n pueda leer y escribir.

#### Opción robusta — Supabase Postgres

**Qué pasa ahí:** lo mismo que Airtable, pero en una base SQL profesional. La diferencia es que no tiene UI tipo planilla — para mirar datos hay que usar el SQL Editor de Supabase o un dashboard externo.

**Plan:** Free (500 MB de DB + 5 GB de transferencia mensual). Alcanza tranquilo para 1 a 3 máquinas durante mucho tiempo.

**Ventaja:** gratis prácticamente para siempre + más rápido + escala mucho mejor si la operación crece.

**Desventaja:** más técnico. Si quieres ver los datos directamente, no vas a abrir Supabase y entender en 1 minuto — vas a depender de reportes que te genere el responsable o tu técnico.

#### Recomendación

Si quieres meter mano directamente en los datos (revisar conversaciones, ver casos abiertos, cambiar registros), **Airtable**. Si confías en recibir reportes y prefieres ahorrar la cuota mensual, **Supabase**.

---

### 4.7 Bot de Telegram para escalamiento (opcional pero MUY recomendado)

**Qué pasa:** cuando el agente no puede resolver un caso, manda un mensaje a un grupo o chat de Telegram donde está tu técnico humano. El técnico ve el resumen completo de la conversación, los datos del cliente, las fotos de evidencia, y responde directo por WhatsApp al cliente final.

**Por qué importa:** sin Telegram, los escalamientos llegan solo por correo o por una notificación interna de ManyChat. Telegram es lo más rápido — el técnico recibe la alerta como un mensaje normal en su teléfono y puede actuar en minutos.

**Cómo se crea:**
1. Abre Telegram → busca [`@BotFather`](https://t.me/BotFather) → escríbele `/newbot` → pide un nombre + username → devuelve un token.
2. Crea un grupo nuevo en Telegram, agrega al bot recién creado.
3. Si prefieres que las alertas vayan a un chat contigo solo, no creas grupo — al bot le mandas `/start` desde tu cuenta.

**Costo:** gratis. Telegram no cobra por bots ni por mensajes.

**Qué se necesita de tu parte:**
- El **bot token** (lo entrega @BotFather, formato `1234567890:ABC-DEF...`).
- El **chat_id** del grupo o del chat donde van a llegar las alertas. Se explica cómo obtenerlo en 30 segundos (se manda un mensaje al bot y se consulta un endpoint).

---

## 5. Datos que se necesitan para configurar el agente

Apenas se tilde el checklist de la sección 3, se solicita llenar un formulario con esto. Conviene tenerlo a mano.

### Sobre tu negocio

- **Nombre comercial:** cómo se llama tu pizzería, así el agente lo dice en las conversaciones.
- **Una frase de cierre:** cómo quieres que el agente cierre las conversaciones. Ejemplo: *"Gracias por escribir, si necesitas algo más estoy acá."*
- **Logo en PNG** (opcional): si quieres que aparezca en emails transaccionales o en el branding del bot.
- **Email del negocio** (opcional): por si quieres sumar correo al loop de notificaciones de escalamiento.

### Catálogo de tus máquinas

Esto es lo más importante. El agente necesita saber qué tienes.

- Cuántas máquinas tienes en total.
- Por cada máquina:
  - Un nombre interno (ejemplo: "Sucursal Centro", "Plaza Norte", "Estación Sur").
  - La dirección.
  - El link a Google Maps.
  - Qué sabores vende esa máquina y a qué precio cada uno.
  - El modelo, si TOFO tiene más de un modelo de máquina (en general es uno solo, pero conviene confirmar).

### Catálogo de fallas conocidas

El paquete viene con un catálogo genérico de fallas (no salió la pizza, doble cobro, pantalla congelada, pizza fría, sabor equivocado, problema con el pago). Si tu operación tiene fallas específicas que no están en ese genérico, se anotan acá.

### Política de reposición

- ¿Cuándo el agente puede entregar un código de reposición directamente, sin validación humana?
- ¿Hay un monto máximo de reposición que el agente puede ofrecer solo?
- ¿Por encima de qué monto el agente debe pasar el caso a tu técnico?
- ¿Hay sabores o situaciones donde nunca debe ofrecer reposición y siempre escalar?

### Contacto del técnico humano

- Nombre del técnico.
- Su WhatsApp.
- El chat_id de Telegram donde van a llegar los escalamientos.
- El horario en que el técnico responde (ejemplo: "lunes a viernes 9 a 18").
- Qué hacer fuera de ese horario: ¿el agente manda un mensaje del estilo "te respondemos mañana"? ¿deja el caso registrado para el día siguiente?

### Mensajes y políticas

- Cómo quieres que se presente el agente al cliente (una sola línea, por ejemplo: *"Hola, soy el asistente de soporte automatizado de [nombre]. Estoy acá para ayudarte con cualquier inconveniente con tu pedido."*).
- ¿El agente se identifica como "asistente automático" o como persona del equipo? Es decisión tuya — la recomendación es identificarlo como asistente, por transparencia.
- ¿Hay información de tus clientes que NO se puede guardar por temas de privacidad o regulación local? Se configura para que no quede registrada.

---

## 6. Costos mensuales aproximados

Estos son los costos que pagas directamente a las plataformas. **No se le paga al responsable ni a TOFO por estas suscripciones** — son tus cuentas, tu plata, tú las controlas.

| Plataforma | Stack Mínimo (1 máquina) | Stack Robusto (3+ máquinas) |
|---|---|---|
| WhatsApp Business (Cloud API de Meta) | Gratis (1.000 conversaciones iniciadas por usuario al mes en tier gratuito) | USD 10 a 40 / mes (según volumen) |
| ManyChat Pro | USD 15 / mes | USD 25 a 50 / mes |
| n8n | Cloud Starter USD 20 / mes | VPS self-hosted USD 5 a 10 / mes (+ USD 1 / mes prorrateado por dominio) |
| OpenAI | USD 10 a 25 / mes | USD 80 a 200 / mes |
| Airtable | Gratis | USD 20 / mes (plan Team) |
| Supabase | Gratis | Gratis a USD 25 / mes |
| Bot Telegram | Gratis | Gratis |
| **Total estimado** | **USD 45 a 60 / mes** | **USD 140 a 340 / mes** |

Aparte de esto, hay que considerar la implementación + el mantenimiento del agente. Esos costos se conversan directamente con quien vende este servicio — el responsable de tu cuenta — y no son parte de las suscripciones de plataformas.

---

## 7. Cronograma típico de implementación

Asume velocidad razonable y que Meta no se demora más de lo habitual.

| Día | Tarea | Quién |
|---|---|---|
| Día 1 | Crear Meta Business Manager + iniciar verificación | Tú |
| Días 1 a 7 | Esperar verificación de Meta (tiempos de Meta, no controlables) | Esperar |
| Día 2 | Conseguir el número de WhatsApp dedicado, abrir cuenta OpenAI con saldo | Tú |
| Día 3 | Crear cuenta ManyChat Pro, base de datos (Airtable o Supabase), cuenta n8n | Tú |
| Día 4 | Llenar el formulario de datos de la sección 5 y enviarlo al responsable de cuenta | Tú |
| Días 5 a 7 | Sesión técnica: configuración de credenciales, importación de workflows, conexión WhatsApp ↔ ManyChat ↔ n8n | Tu responsable + tú |
| Día 8 | Pruebas controladas (se prueban mensajes simulando ser un cliente) | Tu responsable + tú |
| Día 9 | Switch a producción + monitoreo | Tu responsable |
| Día 10 | Revisión post-launch — ajustes finos | Tu responsable |

**Total:** 7 a 10 días hábiles si todo sale parejo y Meta no se demora más allá del rango típico. Si Meta tarda más en verificar (puede llegar a 2 semanas en casos excepcionales), todo el cronograma se corre.

---

**Powered by la agencia** — Agencia de automatización con IA · [[EMAIL-AGENCIA]]
