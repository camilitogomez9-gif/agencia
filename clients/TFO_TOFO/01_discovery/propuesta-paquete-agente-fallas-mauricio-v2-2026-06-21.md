# Propuesta — Agente de fallas técnicas, kit inicial para reventa

**Fecha:** 21 de junio de 2026
**Para:** Mauricio García de la Vega — TOFO Pizza / Robotic Vending de México
**De:** la agencia — la agencia

---

## Introducción

Mauricio, ajusté la propuesta según lo que charlamos el miércoles 18.

Vos pediste achicar el stack del paquete: sacar ManyChat, sacar la memoria persistente con base de datos, dejar el agente operando con WhatsApp Cloud API directa y memoria liviana nativa de n8n. Tiene sentido: las conversaciones de fallas son one-shot, no necesitan histórico cross-turn, y el cliente final no tiene que pagar Supabase + ManyChat Pro encima.

Esto cambia la propuesta de junio (USD 1.798, paquete pulido con dos guías separadas, sesión Zoom y testing guide formal) por algo mucho más liviano.

## Lo que te entrego

Cuatro piezas mínimas. Todo lo necesario para que vos o tu cliente importen el agente en la infraestructura de un cliente final y lo dejen operando.

**1. El system prompt fallas-only, listo para personalizar**

Depurado del prompt actual de Servicio + Reposición que corre en TOFO. Saco todo lo que no aplica (B2B, RRSS, agenda de citas con director, branding TOFO, sucursales, sabores). Quedan: empatía + recolección de evidencia (foto + ticket) + validación contra fraude + bloque anti-alucinación + bloque "lo que NO hago" explícito.

Las variables específicas de cada cliente final quedan como placeholders marcados con llaves dobles: `{{NOMBRE_NEGOCIO}}`, `{{CATALOGO_MAQUINAS}}`, `{{POLITICA_REPOSICION}}`, etc. Tu cliente o vos los llenan en 10 minutos cuando lo implementan.

**2. El workflow n8n completo, listo para importar**

Un solo archivo .json importable directo a un n8n del cliente final. Adaptado del workflow main que corre en producción en TOFO (51 nodos) y depurado a ~20-25 nodos:

- **Entrada:** webhook WhatsApp Cloud API (sin ManyChat).
- **Procesamiento:** normalización, transcripción de audio si viene, análisis de imagen si viene, junta los mensajes.
- **Cerebro:** AI Agent gpt-4.1 con Simple Memory nativa de n8n (in-memory, sin Supabase/Airtable).
- **Salida:** WhatsApp Cloud API directa a Meta.

Credenciales generalizadas — todo lo que hoy es "TOFO" queda como placeholder de credencial. Tu cliente importa, conecta sus propias credenciales (cuenta WhatsApp Cloud API, OpenAI), llena variables, lo activa.

**3. Un README único corto (3-5 páginas)**

Cubre lo necesario y nada más:

- Qué hace el agente y qué NO hace
- Pre-requisitos del cliente final (cuenta Meta con WhatsApp Cloud API verificada, número dedicado, OpenAI con saldo, instancia n8n)
- Pasos de import del JSON + reconexión de credenciales
- Cómo llenar los placeholders del prompt con los datos del cliente final
- 3 casos mínimos de smoke test para correr antes de pasar a producción

Sin screenshots, sin curso de plataformas. Lenguaje semi-técnico — un cliente lo lee y avanza solo.

**4. Loom async de walkthrough (10-15 min)**

Te grabo un Loom caminando los 3 archivos + demostrando un caso E2E contra el sandbox. El cliente lo mira cuando pueda, sin agenda Zoom.

## Qué no incluye

Para que no haya zonas grises:

- No hay dos guías separadas (una para vos y otra para tu dev). Hay un solo README corto.
- No hay testing guide formal con 15-20 casos. El README incluye 3 casos mínimos de smoke. Si después de implementar 1-2 querés una batería más completa, lo cotizamos aparte.
- No hay diagrama draw.io. Si en algún momento lo necesitás (por ejemplo para mostrarle a un cliente final cómo funciona), lo cotizamos aparte.
- No hay sesión Zoom 60 min de handoff. Hay Loom async + dudas por WhatsApp informal durante 14 días post-entrega.
- No hay implementación llave en mano por cliente final. Vos o tu dev implementan. Si en algún momento querés que la agencia haga el setup completo para un cliente puntual (mirás cómo se hace y replicás después), lo cotizamos aparte caso por caso.
- No hay mantenimiento mensual ni garantía formal de 30 días. Hay 14 días de fix informal post-entrega para bugs reproducibles. Después, cualquier cambio se cotiza puntual.
- No hay multi-idioma. Spanish MX heredado de TOFO.

Si más adelante necesitás cualquiera de estas cosas, las armamos en el momento.

## Inversión

| Concepto | Monto |
|---|---|
| Kit inicial — agente de fallas paquetizado, stack reducido | **USD 360** |

Se paga al contado una vez aceptado el presupuesto y previo a la implementación.

## Pre-requisitos del cliente final (para que tengas la cifra)

Lo que cada cliente final paga por mes para tener el agente operando con este stack:

| Componente | Costo aprox mensual |
|---|---|
| WhatsApp Cloud API + número Meta dedicado | Gratis hasta 1.000 conversaciones usuario-iniciadas/mes |
| n8n Cloud Starter (o self-hosted si instala VPS) | USD 20/mes (USD ~12/mes si instala VPS) |
| OpenAI (gpt-4.1, volumen típico de fallas) | USD <10/mes |
| **Total mensual cliente final** | **USD ~15-30/mes** |

Versus USD 60-100/mes del paquete v1 con ManyChat + Supabase.

## Próximos pasos

1. Confirmación de presupuesto y pago.
2. Te mando un formulario corto con decisiones de arranque: tono del prompt (español MX o LatAm neutro), y si tenés un cliente final puntual ya en pipeline para sumarlo al Loom.
3. Una vez cerradas las decisiones, comenzamos con la implementación.

Cualquier duda antes de decidir, me decís.

Un abrazo,

**Equipo la agencia**
