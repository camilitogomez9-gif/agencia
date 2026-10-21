# Catálogo de Audios — Agente Diego Labores

> Lista completa de los audios pre-grabados que usa el agente. Sirve como guía operativa para Diego (qué falta grabar) y para el equipo de implementación n8n/ManyChat (qué `flow_id` mapear).

**Versión prompt asociada:** v1.12
**Fecha:** 2026-05-07
**Total:** 19 audios — 4 grabados ✅ · 15 pendientes 🎤

---

## Estado actual

| # | ID del audio | Estado | Momento de uso | Archivo |
|---|---|---|---|---|
| 1 | `APERTURA_FORM` | ✅ | Apertura cuando lead viene de typeform/formulario | `APERTURA_FORM.opus` |
| 2 | `RESPUESTA_INICIAL` | 🎤 | Apertura cuando lead entra directo por DM (sin formulario) | — |
| 3 | `LEAD_DESDE_CERO` | ✅ | Lead confirmó que arranca desde cero (`nunca_emprendo`) | `LEAD_DESDE_CERO.opus` |
| 4 | `LEAD_CON_NEGOCIO` | 🎤 | Lead confirmó que ya vende algo (`ya_vende`) | — |
| 5 | `METODO_INICIO_PROGRAMA` | ✅ | Lead manifestó idea/proyecto incipiente que necesita ordenar | `METODO_INICIO_PROGRAMA.opus` |
| 6 | `LEAD_TIBIO` | ✅ | Reactivación de lead inconcluso (follow-up) | `LEAD_TIBIO.opus` |
| 7 | `MICROVALOR_MIEDO_PLATA` | 🎤 | Lead dice que le da miedo perder plata (en diagnóstico, etapa 2) | — |
| 8 | `MICROVALOR_NO_EMPIEZA` | 🎤 | Lead dice que no sabe por dónde empezar (en diagnóstico, etapa 2) | — |
| 9 | `MICROVALOR_FALTA_INFO` | 🎤 | Lead dice que le falta info / hay demasiada suelta (en diagnóstico, etapa 2) | — |
| 10 | `MICROVALOR_PROVEEDORES` | 🎤 | Lead desconfía de proveedores (en diagnóstico, etapa 2) | — |
| 11 | `MICROVALOR_INTENTO_FRACASO` | 🎤 | Lead dice que ya lo intentó y no le fue (en diagnóstico, etapa 2) | — |
| 12 | `ROMPER_MIEDO` | 🎤 | Lead expresó miedo / "es complicado" / "necesito experiencia" (objeción) | — |
| 13 | `OBJECION_PRECIO` | 🎤 | Lead presentó objeción de precio explícita | — |
| 14 | `PRE_CIERRE` | 🎤 | Lead con interés claro, todavía no pidió el link | — |
| 15 | `CIERRE_SUAVE` | 🎤 | Cierre con confianza — lead listo para recibir link | — |
| 16 | `CIERRE_REENCUADRE` | 🎤 | Cierre cuando lead duda por precio/decisión post-objeción | — |
| 17 | `CIERRE_IDENTIDAD` | 🎤 | Cierre para leads tibios al límite de avanzar | — |
| 18 | `CIERRE_DIRECTO` | 🎤 | Cierre directo para lead caliente con decisión tomada | — |
| 19 | `CIERRE_CONTENCION` | 🎤 | Cierre con contención para indeciso con miedo final | — |

---

## Audios grabados (✅)

### 1. APERTURA_FORM
**Cuándo:** Primer mensaje al lead que vino de typeform/formulario (`{{ORIGEN}} = form`).

**Texto exacto:**
> "Mirá, mejor te mando un audio así queda mejor explicado. Ahí estuve viendo lo que completaste, y vi que te interesa el tema de importaciones. Buenísimo. Contame, ¿estás arrancando de cero o ya tocaste algo de esto? ¿Has hecho algo?"

---

### 3. LEAD_DESDE_CERO
**Cuándo:** El lead acaba de confirmar que arranca desde cero (perfil `nunca_emprendo`).

**Texto exacto:**
> "Bien, perfecto. Te digo algo porque es clave. Mirá que la mayoría arranca de cero, no necesitás experiencia previa, pero sí hacerlo con un paso a paso claro, porque ahí es donde la mayoría de la gente se traba o pierde plata. En tu caso, ¿qué es lo que más te frena hoy para empezar? Contame."

---

### 5. METODO_INICIO_PROGRAMA
**Cuándo:** El lead manifestó que tiene una idea o proyecto incipiente y necesita ordenarlo. Se le muestra que el programa empieza exactamente analizando esa idea.

**Texto exacto:**
> "Bueno, justamente por ahí es donde arrancamos en el programa: analizando la idea, analizando el modelo de negocios, viendo qué tan viable es, qué tan rentable es, generando una estrategia, analizando todos los canales de venta, el cliente, el producto, todo lo que va a estar enfocado en nuestro negocio para generar una estrategia, y a través de esa estrategia poder crecer y poder avanzar rápido."

---

### 6. LEAD_TIBIO
**Cuándo:** Reactivación de lead que quedó inconcluso (no respondió hace días, conversación abierta sin cierre). Para el follow-up.

**Texto exacto:**
> "Buenas, ¿cómo andás? Por acá te habla Diego. Quería saber en qué estabas. Contame sin problema ninguno y vamos hablando. Abrazo."

---

## Audios pendientes de grabación (🎤)

> Diego: estos son los 15 audios que faltan grabar. El texto es el guion sugerido — adaptalo a tu tono natural, lo importante es mantener el sentido y la longitud aproximada (15–30 segundos).
>
> **Orden de prioridad sugerido:** microvalores (7–11) primero, porque son los que más impactan la conversión — cada lead que dice su dolor va a recibir una respuesta específica tuya en lugar de un texto genérico.

---

### 🆕 MICROVALORES POR DOLOR — Agregar primero (mayor impacto)

Estos 5 audios se disparan en el momento de diagnóstico, cuando el lead declara su freno principal. Son los que convierten una respuesta genérica en una respuesta personalizada con tu voz.

---

### 7. MICROVALOR_MIEDO_PLATA
**Cuándo:** El lead dice que le da miedo perder plata ("me da miedo", "¿y si no funciona?", "¿y si invierto y no me va?"). Se dispara en la etapa de diagnóstico (no confundir con `OBJECION_PRECIO` que es cuando dice que es caro después de ver el precio).

**Guion:**
> "Te entiendo, es súper común eso. Sobre todo cuando no tenés claro cómo es el proceso. Porque desde afuera parece que podés perder plata fácil. Pero en realidad, la mayoría de los errores vienen por no saber bien qué mirar antes de comprar. Cuando eso lo entendés, el riesgo baja muchísimo."

---

### 8. MICROVALOR_NO_EMPIEZA
**Cuándo:** El lead dice que no sabe por dónde empezar ("no sé por dónde arrancar", "no tengo claro el primer paso", "me perdí con tanta info"). Se dispara en diagnóstico.

**Guion:**
> "Bien, ahí está el punto. No es que no puedas, es que no está claro el camino. Y cuando no tenés un paso a paso, todo parece más complicado. Pero cuando lo ordenás, se vuelve mucho más simple."

---

### 9. MICROVALOR_FALTA_INFO
**Cuándo:** El lead dice que le falta información o hay demasiada información suelta ("no sé bien cómo funciona", "hay mucha info pero no entiendo", "leo cosas distintas"). Diferente de `METODO_INICIO_PROGRAMA` (que es cuando tiene una idea concreta pero no sabe cómo encararla).

**Guion:**
> "Sí, totalmente. El problema no es que falte info, es que hay demasiada suelta. Y eso en vez de ayudar, termina confundiendo más. Cuando lo ves ordenado, es otra cosa."

---

### 10. MICROVALOR_PROVEEDORES
**Cuándo:** El lead menciona desconfianza en proveedores como freno ("no sé a quién comprarle", "me da miedo que me estafen", "no conozco proveedores confiables").

**Guion:**
> "Sí, eso también es bastante común. Porque desde afuera no sabés en quién confiar. Pero hay formas bastante claras de filtrar proveedores y evitar los típicos errores. Cuando eso lo entendés, cambia mucho la seguridad."

---

### 11. MICROVALOR_INTENTO_FRACASO
**Cuándo:** El lead dice que ya intentó importar o emprender y no le fue bien ("ya lo intenté y no funcionó", "probé y me fue mal", "lo intenté pero no pude").

**Guion:**
> "Ok, eso pasa bastante. Muchas veces no es el producto, sino cómo se encaró todo. Porque si no entendés bien el proceso, terminás probando sin mucho criterio. Y eso desgasta."

---

### APERTURA Y DIAGNÓSTICO — Segunda prioridad

### 2. RESPUESTA_INICIAL
**Cuándo:** Apertura cuando el lead entra directo por DM (sin haber pasado por formulario, `{{ORIGEN}} = directo`).

**Guion:**
> "Buenas, ¿cómo andás? Por acá te habla Diego. Antes de contarte bien, decime — ¿hoy ya estás vendiendo algo o estás arrancando desde cero? Así voy directo a lo que te sirve."

---

### 4. LEAD_CON_NEGOCIO
**Cuándo:** El lead acaba de confirmar que ya vende algo (perfil `ya_vende`).

**Guion:**
> "Bien, ahí en ese caso tiene mucho sentido lo que estás viendo. Lo que pasa muchas veces es que ya están vendiendo, pero compran caro… y no se dan cuenta cuánto margen están perdiendo ahí. La importación bien hecha te cambia eso. Decime, ¿qué tipo de productos estás trabajando ahora?"

---

### 7. ROMPER_MIEDO
**Cuándo:** El lead manifestó miedo o sensación de que importar es complicado / necesita experiencia / contactos / viajar.

**Guion:**
> "Es normal lo que decís. La mayoría arranca pensando que es complicado o que necesitás experiencia, contactos, viajar… y no es así. El tema no es la dificultad. Es no entender el proceso. Cuando lo ves claro, se vuelve mucho más simple de lo que parece. ¿Qué es lo que más te genera duda hoy?"

---

### 8. OBJECION_PRECIO
**Cuándo:** El lead presentó objeción de precio explícita ("es caro", "no tengo plata", "está fuera de mi presupuesto").

**Guion:**
> "Sí, te entiendo. Igual te digo algo… más allá del precio, lo importante es si esto realmente te sirve para lo que querés hacer. Porque muchas veces se pierde más plata por hacer mal una importación o por no animarse a hacerlo. Decime, ¿vos estás buscando arrancar algo o mejorar lo que ya tenés?"

---

### 9. PRE_CIERRE
**Cuándo:** El lead mostró interés claro pero todavía no pidió el link.

**Guion:**
> "Perfecto. Por lo que me contás, tiene bastante sentido para vos. Si querés, te explico bien cómo funciona el programa por dentro y cómo sería para que arranques."

---

### 10. CIERRE_SUAVE
**Cuándo:** Cierre con confianza. El lead ya mostró interés y está listo para recibir el link de IC. Acompaña el envío del link.

**Guion:**
> "Bien, perfecto. Por lo que me contás, tiene bastante sentido para vos. La idea del programa es justamente que no tengas que ir probando solo, sino que entiendas bien el proceso y arranques con claridad. Te paso el link para que puedas acceder y empezar. Y cualquier duda que tengas en el camino, lo vamos viendo."

---

### 11. CIERRE_REENCUADRE
**Cuándo:** Cierre cuando el lead duda por precio o decisión, ya pasó la objeción inicial pero sigue indeciso. Acompaña el envío del link.

**Guion:**
> "Mirá, te digo algo para que lo veas claro. Más allá del programa en sí… lo importante es que si vas a meterte en esto, lo hagas bien desde el principio. Porque una mala decisión o una importación mal hecha te puede salir más cara que esto. Si sentís que es por acá, te paso el link y arrancás tranquilo, sabiendo lo que estás haciendo."

---

### 12. CIERRE_IDENTIDAD
**Cuándo:** Cierre para leads tibios que están en el límite de avanzar. Apela a identidad y decisión.

**Guion:**
> "Esto no es para todos. Es para el que realmente quiere dejar de mirar y empezar a hacer algo propio. Por lo que me fuiste contando, estás bastante cerca de eso. Si querés dar ese paso, te paso el link y empezás."

---

### 13. CIERRE_DIRECTO
**Cuándo:** Cierre directo para lead caliente. El lead ya tiene la decisión tomada. Acompaña el envío del link.

**Guion:**
> "Perfecto. Si ya lo tenés claro, hacemos así: te paso el link de acceso, completás y ya podés entrar al programa. Cuando tengas el acceso me avisan y tenemos una llamada así arrancás de una."

---

### 14. CIERRE_CONTENCION
**Cuándo:** Cierre con contención para indecisos con miedo final. Última instancia antes de cerrar la conversación.

**Guion:**
> "Es normal tener esa duda antes de avanzar. Le pasa a todos. Pero la diferencia está en no quedarse ahí. Si ya sabés que querés hacer algo distinto, este es el paso que ordena todo. Si querés, te paso el link y empezás con una base clara."

---

## Implementación n8n + ManyChat

Para cada audio del catálogo:

1. **ManyChat:** crear un Flow que reproduzca el archivo de audio (cuando esté grabado).
2. **Mapping:** registrar el `flow_id` en n8n con clave igual al ID del audio (ej. `APERTURA_FORM → flow_id_xyz`).
3. **Parser n8n:** detectar `[AUDIO:X]` al inicio de un bloque del mensaje del agente.
   - Si `X` está mapeado y el flow existe → disparar HTTP a ManyChat (`flow_id`) y descartar el texto del audio del mensaje al lead.
   - Si `X` no está mapeado o el audio aún no está grabado → enviar el texto del audio como mensaje normal (fallback funcional).

**Ventaja del fallback:** mientras Diego va grabando los audios pendientes, el agente sigue funcionando 100% — los leads reciben el texto del audio en lugar del audio en sí. No bloquea producción.

---

## Próximos pasos

1. **Diego — grabar los 15 audios pendientes en este orden de prioridad:**
   - **Microvalores (mayor impacto):** `MICROVALOR_MIEDO_PLATA` → `MICROVALOR_NO_EMPIEZA` → `MICROVALOR_FALTA_INFO` → `MICROVALOR_PROVEEDORES` → `MICROVALOR_INTENTO_FRACASO`
   - **Apertura y diagnóstico:** `RESPUESTA_INICIAL` → `LEAD_CON_NEGOCIO`
   - **Objeciones:** `OBJECION_PRECIO` → `ROMPER_MIEDO`
   - **Cierres:** `PRE_CIERRE` → `CIERRE_SUAVE` → `CIERRE_DIRECTO` → `CIERRE_REENCUADRE` → `CIERRE_IDENTIDAD` → `CIERRE_CONTENCION`
2. **Equipo n8n:** crear los Flows en ManyChat y mapear `flow_id` por audio.
3. **Validación:** correr la guía de testing v5 (10 casos) para verificar precio 697, tono simple y microvalores.
