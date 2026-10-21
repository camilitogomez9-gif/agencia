# Testing del agente por Telegram — Venttur (staging)

**Fecha:** 2026-09-07 · **Workflow:** `[Venttur] GHL staging (Telegram test)` (`3sLd7KY3o8I7NvXi`, activo) · **Bot:** `Venttur` (Telegram).

> **Qué es esto:** un preview del **agente conversacional "Mauricio"** ya reconstruido sobre GHL, accesible por **Telegram** para probarlo sin tocar el WhatsApp de producción. Sirve para evaluar **cómo conversa** (tono, respuestas, memoria, uso del estado del lead). El canal real de WhatsApp, el audio y los calendarios se conectan más adelante (ver `04_guia_migracion/`).

---

## Qué está conectado (y qué no) en este preview

**✅ Conectado:** agente Mauricio (gpt-4o) · memoria por conversación · **context builder** (lee el estado del lead en GHL e inyecta `[ESTADO DEL LEAD]`) · tools `crear_contacto` (alta en GHL) y `elevar` (derivar a humano).
**❌ Todavía NO (se arma con el canal real):** entrada/salida por WhatsApp real, transcripción de audios, agendamiento en calendarios GHL, notificación del handoff por email/app, despachador de re-enganche.

---

## Pre-flight (la agencia, antes de compartirlo con Mauricio)

1. Abrir el chat del bot `Venttur` en Telegram y mandar **"hola"**.
2. Esperar la respuesta (debe saludar como Mauricio de Venttur y preguntar el nombre). Confirma que la cadena completa corre en vivo (normalize → búsqueda en GHL → estado → agente → respuesta).
3. Si responde bien → listo para compartir con Mauricio. Si no responde o da error → avisar antes de compartir.

> **Validado headless (2026-09-07):** el system prompt real corrido por gpt-4o da respuestas on-brand; saluda, pide el nombre, da el rango de precio de Internados (USD 50-130k) + ofrece asesoría, y **NO re-pregunta el nombre** cuando el estado ya lo trae. El único paso que faltaba confirmar en vivo es el runtime de n8n (el "hola" del pre-flight lo cierra).

---

## Casos para que pruebe Mauricio

Mandar los mensajes de a uno y ver cómo responde. No hay respuestas "correctas" únicas — se evalúa el **criterio**.

| # | Mandale al bot | Qué debería pasar |
|---|---|---|
| 1 | `hola` | Se presenta como Mauricio de Venttur, cálido, pregunta con quién habla (el nombre). |
| 2 | `busco un internado para mi hijo de 15 años` | Muestra interés genuino, hace preguntas de descubrimiento (no vomita info); puede pedir el nombre si aún no lo tiene. |
| 3 | `¿cuánto sale?` | Da un **rango** (no un precio cerrado) y ofrece **asesoría con Rodrigo** para el número exacto; invita a agendar. |
| 4 | Decile tu nombre (ej. `soy Mauricio`) y seguí la charla | Usa tu nombre de ahí en más y **no te lo vuelve a preguntar**. |
| 5 | Preguntá por otro programa (ej. `y campamentos de verano?`) | Reconoce el programa, adapta la conversación; no se confunde de programa. |
| 6 | Mandá 2-3 mensajes seguidos sobre el mismo tema | **Recuerda el contexto** de los mensajes anteriores (memoria), no arranca de cero. |
| 7 | Preguntá algo que no debería saber (ej. `¿me hacés un descuento del 50%?`) | No inventa; responde con criterio (deriva a asesoría / no promete lo que no puede). |
| 8 | `quiero hablar con una persona` | Ofrece derivarte a un asesor (handoff). *(En el preview la notificación al equipo aún no está conectada — es esperado.)* |

---

## Qué mirar (criterios de "bien")

- **Tono:** humano, cálido, rioplatense/neutro; no robótico ni con listas largas.
- **Ritmo:** hace preguntas, no larga toda la info de golpe.
- **Memoria:** no repite preguntas ya respondidas; recuerda nombre, programa, lo dicho antes.
- **Precisión:** no inventa precios cerrados, fechas ni datos; ante lo que no sabe, deriva a asesoría.
- **Cierre:** empuja suave hacia agendar una videollamada con el asesor.

## Qué reportar

Lo que se sienta raro, forzado o incorrecto: una respuesta fría, que repregunte algo ya dicho, que invente un dato, que no entienda el programa, o cualquier frase que no dirías vos. Con captura del chat alcanza.

---

## Nota operativa (la agencia)

- **Contactos de test en GHL:** cuando el agente da de alta un lead de prueba, crea un contacto con email `tg-<chatid>@venttur.test`. Son inofensivos e identificables. Para limpiarlos después de las pruebas: buscar en GHL los contactos con email que termina en `@venttur.test` y borrarlos (o pedírmelo y los limpio por API).
- **Alcance del preview:** es conversacional. No confirmar contra Mauricio funciones de canal real (WhatsApp/audio/calendarios) — esas se prueban post-traspaso del WABA (`04_guia_migracion/11` y `12`).
