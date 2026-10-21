# Migración de canal WhatsApp: Chatrace → ManyChat (2026-06-30)

## Resumen

El número histórico de WhatsApp de Collazo (**+598 91339312**) quedó bloqueado tras dar de baja la cuenta de Chatrace, imposibilitando conectarlo a ManyChat. Después de varios días de gestiones sin resolución (Chatrace, Meta, ManyChat), se optó por un **Plan B**: activar un número nuevo y conectarlo directamente a ManyChat vía Embedded Signup, dejando el número viejo como gestión pendiente en paralelo.

**Estado al cierre de esta sesión:** número nuevo conectado a ManyChat + n8n recableado y funcionando. Número viejo (+598 91339312) sigue sin liberar — casos abiertos en paralelo con Meta y ManyChat.

---

## 1. Incidente — número viejo bloqueado

Al intentar conectar +598 91339312 a la WABA propia de Collazo (`Collazo Servicio Técnico`, WABA ID `10111928183308888`) vía Embedded Signup de ManyChat, Meta devolvía:

> "El número de teléfono ya está en uso. Este número de teléfono ya está registrado con una cuenta de WhatsApp. Para continuar, migra este número de teléfono o desconéctalo de esa cuenta."

**Diagnóstico:** Chatrace no registró el número dentro de la WABA propia del cliente (que está vacía, sin partners), sino en una **WABA propia de Chatrace**. Por eso no existía ningún "partner" que remover desde el Business Manager de Collazo — el número quedó fuera del alcance de autogestión del cliente.

### Gestiones realizadas (sin éxito directo)

- **Chatrace support** — respuestas contradictorias en varios tickets:
  - "There is nothing we can do on our side. The number is disconnected from our platform."
  - "The embedded sign up flow has an option to transfer number from one BSP to another."
  - "Please check with Manychat support."
  - "You can delete chatrace as partner from the waba."
  - "We do not hold any numbers on our side."
  
  A pesar de decir que no retienen el número, el bloqueo persistió tras reintentar el Embedded Signup (con esperas de 5+ minutos entre intentos).

- **Meta Business Support** — caso abierto ("Something else", recibido 2026-06-30) desde el Business Manager de la agencia Automation. Sin respuesta de operador humano tras más de 90 minutos; se envió mensaje de seguimiento con urgencia.

- **ManyChat support** — ticket abierto vía "Recibe ayuda" (Configuración → Ayuda) con contexto completo del incidente, pidiendo escalamiento a Meta Partner Operations para iniciar un Phone Number Recovery. Pendiente respuesta por correo.

- **Verificación de otro Business Manager** — pendiente que Matías confirme si existe un segundo BM donde Chatrace figure como partner (pista que surgió de la respuesta "you can delete chatrace as partner from the waba", que implica que existe *algún* WABA con Chatrace listado — no es la de Collazo).

---

## 2. Plan B — número nuevo

Ante la falta de resolución, Matías activó un **chip nuevo** (número distinto al histórico +598 91339312) para destrabar la recepción de mensajes.

### Regla crítica descubierta/reforzada

**El número NUNCA debe registrarse en la app de WhatsApp o WhatsApp Business (ni celular ni compu).** La Cloud API (que usa ManyChat) y la app son mutuamente excluyentes — un número solo puede vivir en un lado. Si se registra primero en la app, se repite exactamente el mismo error "número ya está en uso" al intentar conectarlo a ManyChat después. Esto es lo que probablemente le pasó al número viejo en su momento.

Esta regla aplica también a futuro: **cualquier edición de perfil (foto, "acerca de", horarios, dirección) se hace desde WhatsApp Manager (Meta Business Manager → WhatsApp Manager → Números de teléfono → Perfil) o desde ManyChat — nunca desde la app.**

### Pasos de conexión ejecutados

1. Chip nuevo activado (solo señal para recibir SMS/llamada — sin instalar WhatsApp).
2. ManyChat → Settings → WhatsApp → Connect → **"Transfer your own WhatsApp number"**.
3. Embedded Signup → seleccionar el Business Manager y la **WABA existente** "Collazo Servicio Técnico" (ID `10111928183308888`) — no crear una nueva.
4. Ingresar el número nuevo → verificación por SMS/llamada → conectado sin error (a diferencia del número viejo, este está limpio).
5. n8n recableado a ManyChat (confirmado por la agencia — "la parte de n8n ya está configurada. Manychat quedó también").

### Pendiente de comunicación (no ejecutado en esta sesión)

Si el número público cambió de cara al cliente final, falta actualizar: redes sociales (IG/FB, botón de contacto WhatsApp), landing/web, Google Business Profile, firma de email del equipo. Evaluar aviso directo a clientes frecuentes si la base es chica.

### Cuando se libere el número viejo

Decidir si migrar el agente de vuelta al +598 91339312 (recomendado, es el que la gente conoce) o quedarse con el nuevo. Los casos con Meta/ManyChat para liberar el número viejo siguen abiertos en paralelo y no bloquean la operación actual.

---

## 3. Bugs resueltos durante la integración ManyChat ↔ n8n

Con el número nuevo ya conectado, se armó/ajustó el cableado del nodo `setCustomFields` (respuesta del agente hacia ManyChat) y aparecieron varios bugs, todos resueltos:

### 3.1 — 401 "Wrong format token" en `setCustomFields`

Causa: la credencial `CLZ API Header Auth` tenía el token de ManyChat sin el prefijo `Bearer `. ManyChat exige el header:
```
Authorization: Bearer <token>
```
Fix: se corrigió el valor del header en la credencial (agregando `Bearer ` + un espacio antes del token).

### 3.2 — 400 "Value for number custom field should be integer or float"

Causa: el Code node `Build ManyChat Payload` mandaba `ai_msg_count` (custom field tipo **Number** en ManyChat) como string: `field_value: String(msgs.length)`.
Fix: se quitó el `String(...)`, quedando `field_value: msgs.length` (número real).

### 3.3 — `has_audio` siempre `false`/erróneo en Normalize Payload

Causa: `last_input_text.contains('o')` — `.contains()` no existe en JavaScript (es de otros lenguajes), y además el string buscado era `'o'` en vez de `.ogg`.
Fix: `last_input_text.includes('.ogg')`.

### 3.4 — Links de reserva mandados en formato markdown sucio

El AI Agent devolvía links tipo `[cal.com/collazo-servicio/instalacion-aire](https://cal.com/collazo-servicio/instalacion-aire)` en vez del link plano que exige el prompt (`cal.com/collazo-servicio/instalacion-aire`). El prompt ya tenía una instrucción genérica ("sin paréntesis ni formato especial") pero no alcanzaba — es un sesgo fuerte de GPT-4o/4o-mini hacia el formato hyperlink markdown.

**Fix en dos capas** (mismo patrón que otros clientes — prompt + guardrail determinístico en código):
- **Prompt** (`AI Agent` → systemMessage): se agregó una regla crítica de formato con ejemplo negativo explícito (mostrar el error exacto que hizo) justo en "Proceso de Reserva por Servicio", más un recordatorio corto en "Enlaces para la reserva".
- **Código** (`Code in JavaScript`, entre el AI Agent y el split de mensajes): se agregaron dos regex de limpieza determinística que corren siempre, sin depender del LLM:
  ```js
  // Fix 2: si el LLM devuelve [texto](url), nos quedamos con la URL real
  output = output.replace(/\[[^\]]*\]\(([^)]+)\)/g, '$1');
  // Fix 3: los links de Collazo van sin protocolo — se quita https://, http://, www.
  output = output.replace(/https?:\/\/(www\.)?/gi, '');
  ```
  Con esto, aunque el LLM vuelva a fallar, el mensaje que llega a ManyChat siempre sale limpio.

### 3.5 — Reglas de corte de mensaje poco naturales (`Formatear mensaje`)

El nodo `Formatear mensaje` (gpt-4o-mini, divide la respuesta en hasta 3 partes para simular mensajes de WhatsApp) cortaba a veces en medio de una idea (ej. justo antes de una coma que continuaba la misma frase, dejando una parte que arrancaba con ", por favor..."). Se reescribió el prompt con reglas explícitas de corte estilo humano: cortar solo entre oraciones completas, nunca antes de una coma que continúa la misma cláusula, cada parte debe sonar completa por sí sola, dividir por función discursiva (apertura/contenido/cierre) y no por longitud, no dividir mensajes cortos, no partir listas a la mitad.

---

## 4. Pendiente técnico

- **Re-exportar `agente-collazo-main.json` completo desde n8n.** El archivo en el repo quedó desactualizado — no refleja la topología ManyChat (`Normalize Payload`, `setCustomFields`, `Build ManyChat Payload`, `Formatear mensaje`, IDs de nodo nuevos). Los fixes de esta sesión (§3) están aplicados en n8n vivo pero no en el JSON del repo.
- **Registrar el número nuevo** en este documento y en `CLIENT_INFO.md` una vez confirmado formalmente (no se compartieron los dígitos en esta sesión).
- **Seguimiento de los casos abiertos** con Meta Business Support y ManyChat support para la eventual liberación de +598 91339312.
- **Confirmar con Matías** si hay otro Business Manager donde Chatrace figure como partner (pista de su propia respuesta de soporte).
- **Actualización de canales públicos** con el número nuevo si aplica (redes, landing, Google Business Profile).
