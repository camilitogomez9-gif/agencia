# Guía de Testing — Agente Importadores Conectados v2

**Canal:** Instagram DM / WhatsApp / Facebook
**Prompt versión testeada:** v1.4
**Estado:** Pendiente

---

## Cambios respecto a v1

- Cambio de rol: el agente ahora **habla como Diego** en primera persona (no como "Setter del equipo de Diego").
- Se agregaron 2 audios nuevos: `APERTURA_FORM` (cuando lead viene de typeform) y `METODO_INICIO_PROGRAMA` (cuando lead manifiesta idea/proyecto).
- Variable nueva `{{ORIGEN}}` (`form` o `directo`) que decide qué audio de apertura usar.
- Catálogo total: 14 audios — 4 grabados (✅) + 10 pendientes (🎤). Ver [audios-catalogo.md](../06_docs/audios-catalogo.md).

**Casos NUEVOS en esta versión:** todos los del bloque "Casos de v1.4" más abajo. El resto se mantiene de v1 (con el ajuste de identidad: ahora se espera primera persona Diego en lugar de "del equipo").

---

## Instrucciones de uso

1. Ejecutar cada caso en el canal real o en el entorno de prueba (Telegram).
2. Para cada caso, **fijar la variable `{{ORIGEN}}`** según se indique (`form` o `directo`).
3. Pegar la respuesta exacta del agente en "Resultado obtenido".
4. Marcar OK como `true`, `false` o `parcial`.
5. Para los marcadores `[AUDIO:NOMBRE]`: validar que el agente los emite correctamente. Si el flow de ManyChat aún no está creado, el texto del audio debe llegar como mensaje normal (fallback funcional).
6. Agregar notas al pie si hay patrones sistémicos.

---

## Casos simples — heredados de v1 (con ajuste de identidad)

> **Importante:** en todos los casos donde antes se esperaba "habla como Setter del equipo", ahora se espera **primera persona Diego** ("yo te explico", "mi programa", "mi equipo atiende la llamada").

| # | Mensaje a enviar | Variable `{{ORIGEN}}` | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|---|-------------------|-------------------|----|
| 1 | `Hola` | `directo` | Apertura con `[AUDIO:RESPUESTA_INICIAL]` + texto del audio. UNA sola pregunta ("¿hoy ya estás vendiendo algo o estás arrancando desde cero?"). Habla en primera persona como Diego. | | |
| 2 | `Hola, quiero info del programa Importadores Conectados` | `directo` | Apertura con `[AUDIO:RESPUESTA_INICIAL]`. NO empieza explicando el programa — primero indaga situación. Habla como Diego. | | |
| 3 | `¿Cuánto cuesta el programa?` (lead solo_precio) | `directo` | NO da precio seco. Califica primero: una pregunta. Luego presenta IC con precio USD 497 + módulos completos (importación, finanzas, marketing, ecommerce, ventas). Refiere al programa como "mi programa". | | |
| 4 | `¿Cuánto cuesta la mentoría 1:1?` | `directo` | NO da precio fijo. Explica que la Mentoría 1:1 se cotiza según el caso y propone agendar llamada con su equipo. Mensaje directivo: "Te paso el link de agenda". Etiqueta `[NOTIFICAR_AGENDA]`. | | |
| 5 | `¿Cuánto tiempo tengo acceso a las clases?` | `directo` | Aclara: clases grabadas con acceso ILIMITADO. Acompañamiento, chat directo, clases en vivo y coaching: 3 meses. | | |
| 6 | `¿El programa es solo de importación?` | `directo` | NO. Aclara módulos completos: importación + finanzas + marketing + ecommerce + ventas. Menciona clases en vivo conmigo (Diego) y otros expertos. | | |
| 7 | `¿Qué incluye el programa?` (después de calificar) | `directo` | Lista IC: clases grabadas (acceso ilimitado), módulos completos, clases en vivo conmigo y expertos, 3 meses de acompañamiento, plantillas, planilla de compra, asesor IA. NO se queda solo en "clases grabadas". | | |
| 8 | `Garantizan que voy a ganar plata?` | `directo` | Cierra con honestidad: no hay garantía mágica, lo que ofrezco es proceso y método. NO usa "garantizado", "fácil", "rápido". | | |
| 9 | `Quiero algo que me dé ingresos pasivos sin trabajar` | `directo` | Descalifica limpiamente sin re-encauzar. Etiqueta `[NOTIFICAR_DESCALIFICADO]`. | | |
| 10 | `Es muy caro` | `directo` | Usa `[AUDIO:OBJECION_PRECIO]`. NO baja el precio. Reencuadra al valor. | | |
| 11 | `Importar de China me da miedo, parece complicado` | `directo` | Usa `[AUDIO:ROMPER_MIEDO]`. NO descarta el miedo, lo legitima y reencuadra. | | |
| 12 | `Tengo un negocio que ya funciona perfecto, quiero importar mis productos` | `directo` | Deriva a Tecnoimport. Mensaje del estilo "mi empresa Tecnoimport". Etiqueta `[NOTIFICAR_DERIVAR_TECNOIMPORT]`. NO ofrece IC ni Mentoría. | | |

---

## Casos de v1.4 — Identidad Diego (PRIMERA PERSONA)

| # | Mensaje a enviar | Variable `{{ORIGEN}}` | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|---|-------------------|-------------------|----|
| 13 | `¿Vos sos Diego?` | `directo` | Confirma que sí. NO dice "soy del equipo de Diego". Tono cálido en primera persona. | | |
| 14 | `¿Y vos me vas a acompañar en el programa?` | `directo` | Aclara con honestidad: las clases en vivo y los planes de Mentoría los acompaña él; las llamadas de evaluación / propuestas las atiende su equipo; la Asesoría 1:1 (USD 100) la da él personalmente. NO promete acompañar todas las llamadas. | | |
| 15 | `¿Quién atiende cuando agendo la llamada?` | `directo` | Responde claramente: "La atiende mi equipo". NO dice "yo te atiendo" para llamadas de evaluación. | | |
| 16 | `¿La asesoría 1:1 la das vos?` | `directo` | Confirma: "Sí, esa la doy yo, 1 hora 1:1 conmigo, USD 100". | | |
| 17 | `¿Tecnoimport qué es?` | `directo` | Explica: "Es mi empresa de servicios de importación". Primera persona posesiva. | | |

---

## Casos de v1.4 — Variable {{ORIGEN}} (apertura diferenciada)

| # | Mensaje a enviar | Variable `{{ORIGEN}}` | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|---|-------------------|-------------------|----|
| 18 | `Hola` (primer mensaje) | `form` | Apertura con `[AUDIO:APERTURA_FORM]` + texto exacto del audio: "Mirá, mejor te mando un audio así queda mejor explicado. Ahí estuve viendo lo que completaste...". NO usa `[AUDIO:RESPUESTA_INICIAL]`. | | |
| 19 | `Hola` (primer mensaje) | `directo` | Apertura con `[AUDIO:RESPUESTA_INICIAL]` + texto del audio. NO usa `[AUDIO:APERTURA_FORM]`. | | |
| 20 | `Buenas, completé el formulario y quería más info` | `form` | Reconoce el contexto del formulario. Usa `[AUDIO:APERTURA_FORM]`. | | |
| 21 | `Hola` | (vacío / no seteado) | Sin variable `{{ORIGEN}}` válida — tratar como `directo` y usar `[AUDIO:RESPUESTA_INICIAL]`. NO debe romper. | | |

---

## Casos de v1.4 — Audio METODO_INICIO_PROGRAMA

| # | Mensaje a enviar | Variable `{{ORIGEN}}` | Resultado esperado | Resultado obtenido | OK |
|---|-----------------|---|-------------------|-------------------|----|
| 22 | `Tengo una idea de un negocio de bijou para importar pero no sé por dónde empezar` (después de la apertura) | `directo` | Usa `[AUDIO:METODO_INICIO_PROGRAMA]` + texto exacto del audio. Muestra que el programa arranca analizando la idea, modelo, viabilidad, estrategia. | | |
| 23 | `Tengo un proyecto en mente pero está muy verde, no sé si es viable` | `directo` | Usa `[AUDIO:METODO_INICIO_PROGRAMA]`. NO va directo a precio. | | |
| 24 | `Quiero importar pero no tengo claro qué producto vender` | `directo` | Usa `[AUDIO:METODO_INICIO_PROGRAMA]` (encaja porque hay idea sin definir). | | |

---

## Flujos conversacionales — heredados y ajustados

> **Ajuste global:** todos los flujos de v1 siguen vigentes pero con el cambio de identidad (primera persona Diego). Las referencias a "el equipo de Diego" pasan a ser "mi equipo" cuando habla del equipo, o primera persona cuando habla de sí mismo.

Ver [testing-guide-v1.md](testing-guide-v1.md) para los flujos 1–10 originales. Re-ejecutar todos validando que las respuestas estén en primera persona.

---

## Flujo NUEVO 11: Lead viene de typeform

**Objetivo:** validar el camino completo cuando el lead pasó por formulario antes del chat.
**Perfil del lead:** nunca_emprendo
**Variable:** `{{ORIGEN}} = form`

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Hola, completé el form` | — | | |
| 2 | Agente | — | `[AUDIO:APERTURA_FORM]` + texto exacto del audio. UNA pregunta. | | |
| 3 | Usuario | `Estoy desde cero` | — | | |
| 4 | Agente | — | `[AUDIO:LEAD_DESDE_CERO]` + texto del audio. UNA pregunta. | | |
| 5 | Usuario | `Tengo una idea pero no sé cómo encararla` | — | | |
| 6 | Agente | — | `[AUDIO:METODO_INICIO_PROGRAMA]` + texto del audio. NO suelta precio todavía. | | |
| 7 | Usuario | `Me suena, ¿qué incluye el programa?` | — | | |
| 8 | Agente | — | Presenta IC con USD 497 + módulos completos + clases en vivo conmigo. UNA pregunta de cierre. Primera persona. | | |

---

## Flujo NUEVO 12: Lead viene directo por DM

**Objetivo:** validar que la apertura usa `RESPUESTA_INICIAL` cuando no hay form previo.
**Perfil del lead:** sin_clasificar
**Variable:** `{{ORIGEN}} = directo`

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Hola` | — | | |
| 2 | Agente | — | `[AUDIO:RESPUESTA_INICIAL]` + texto. UNA pregunta. NO `[AUDIO:APERTURA_FORM]`. | | |
| 3 | Usuario | `Quiero saber qué hacés` | — | | |
| 4 | Agente | — | Explica brevemente desde primera persona: "Ayudo a emprendedores a armar negocios de importaciones". UNA pregunta para calificar. | | |

---

## Flujo NUEVO 13: Lead pregunta directo "¿sos Diego?" en mitad de la conversación

**Objetivo:** validar coherencia de identidad cuando el lead duda.
**Perfil del lead:** sin_clasificar
**Variable:** `{{ORIGEN}} = directo`

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Hola, info del programa` | — | | |
| 2 | Agente | — | `[AUDIO:RESPUESTA_INICIAL]`. | | |
| 3 | Usuario | `Pará, ¿estoy hablando con Diego o con un asistente?` | — | | |
| 4 | Agente | — | Confirma identidad como Diego sin trabarse. NO confiesa ser bot/asistente (a menos que pregunte explícitamente "¿sos un bot?"). Reencauza la conversación: vuelve a la pregunta inicial. | | |

---

## Flujo NUEVO 14: Lead con idea/proyecto que necesita ordenarse

**Objetivo:** validar uso de `METODO_INICIO_PROGRAMA` y conversión a IC.
**Perfil del lead:** intento_fracaso
**Variable:** `{{ORIGEN}} = directo`

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK |
|-------|-----|---------|-------------------|-------------------|----|
| 1 | Usuario | `Hola, ya intenté antes con un proyecto pero no salió` | — | | |
| 2 | Agente | — | `[AUDIO:RESPUESTA_INICIAL]`. UNA pregunta para entender qué intentó. | | |
| 3 | Usuario | `Quería poner una marca de ropa pero no supe cómo seguir` | — | | |
| 4 | Agente | — | `[AUDIO:METODO_INICIO_PROGRAMA]`. Muestra que el programa arranca analizando esa idea. UNA pregunta. | | |
| 5 | Usuario | `Sí, quiero retomar` | — | | |
| 6 | Agente | — | Pasa a propuesta IC con USD 497 + módulos. UNA pregunta de cierre. | | |

---

## Notas adicionales

_Completar al finalizar el testing con observaciones sistémicas: patrones de error,
comportamientos inesperados, sugerencias de mejora._

**Validaciones específicas a la versión 1.4:**

- ¿El agente habla SIEMPRE en primera persona como Diego? Buscar deslices del tipo "Diego te puede acompañar" cuando debería decir "yo te puedo acompañar".
- ¿La variable `{{ORIGEN}}` cambia correctamente el audio de apertura?
- ¿`[AUDIO:APERTURA_FORM]` se emite SOLO cuando `{{ORIGEN}} = form`?
- ¿`[AUDIO:METODO_INICIO_PROGRAMA]` se usa en el momento correcto (lead con idea/proyecto que necesita ordenarse)?
- ¿El agente respeta la distinción "yo doy Asesoría 1:1 / mi equipo atiende llamadas de evaluación"?
- ¿El texto exacto de los 4 audios grabados se mantiene fiel a la transcripción del catálogo (para fallback funcional)?

---

> Guía de testing v2 para Agente Importadores Conectados. Casos diseñados sobre el prompt v1.4 (cambio de rol Setter → Diego + 2 audios nuevos + variable {{ORIGEN}}).
