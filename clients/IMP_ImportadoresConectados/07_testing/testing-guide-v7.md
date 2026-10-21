# Guía de Testing — Agente Importadores Conectados v7

**Canal:** Instagram DM / WhatsApp / Facebook
**Prompt versión testeada:** v1.12
**Estado:** ✅ Completo — 46/46 true (0 false, 0 parcial)

**⚠️ FORMATO COMPATIBLE CON SCRIPT:** Esta guía usa exclusivamente tablas `| Turno | Rol | Mensaje | Resultado esperado |` para flujos multi-turno. No modificar la estructura de columnas. No agregar columnas extra (Área, Flujo, OK, Resultado obtenido). El script genera su propio output.

---

## Contexto

Re-test de los 4 fixes incorporados en v1.9 (sobre base v1.8):
1. METODO: variantes explícitas de NO-disparador + regla simplificada "sin producto/nicho/proyecto nombrado → no es METODO"
2. Distinción MICROVALOR_MIEDO_PLATA vs ROMPER_MIEDO: miedo al resultado económico vs. miedo al proceso de importar
3. REGLA ANTI-CADENA: excepción MICROVALOR — declaración de dolor específico permite el audio aunque haya 2 previos
4. LEAD CON INTERÉS DECLARADO: si historial ya muestra "quiero empezar" o precio, y lead dice "cuéntame", presentar IC directamente

**Variable n8n:** `{{ORIGEN}}` se reemplaza con `directo` en todos los casos (pre-procesado por el script antes de enviar el prompt).

---

## Bloque A — METODO sin idea concreta (fix #1)

### Caso 1 — "no tengo claro cómo funciona todo esto"

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `hola` | — |
| 2 | Agente | — | — |
| 3 | Usuario | `arranco de cero` | — |
| 4 | Agente | — | — |
| 5 | Usuario | `no tengo claro cómo funciona todo esto` | — |
| 6 | Agente | — | Usa [AUDIO:MICROVALOR_FALTA_INFO] o [AUDIO:MICROVALOR_NO_EMPIEZA]. NO usa [AUDIO:METODO_INICIO_PROGRAMA]. El lead no nombró ningún producto, nicho ni proyecto. El agente puede hacer preguntas de diagnóstico después del audio (incluso "¿tenés alguna idea?") — lo que NO debe hacer es enviar el marcador [AUDIO:METODO_INICIO_PROGRAMA]. |

---

### Caso 2 — "me falta información, no sé bien cómo funciona todo"

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `buenas` | — |
| 2 | Agente | — | — |
| 3 | Usuario | `arranco de cero` | — |
| 4 | Agente | — | — |
| 5 | Usuario | `el problema es que me falta información, no sé bien cómo funciona todo` | — |
| 6 | Agente | — | Usa [AUDIO:MICROVALOR_FALTA_INFO]. NO usa [AUDIO:METODO_INICIO_PROGRAMA]. El lead no nombró ninguna idea concreta. El agente puede hacer preguntas de diagnóstico después del audio. |

---

### Caso 3 — "no sé por dónde empezar, hay mucha info"

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `hola` | — |
| 2 | Agente | — | — |
| 3 | Usuario | `estoy arrancando desde cero` | — |
| 4 | Agente | — | — |
| 5 | Usuario | `no sé por dónde empezar, hay mucha info` | — |
| 6 | Agente | — | Usa [AUDIO:MICROVALOR_NO_EMPIEZA] o [AUDIO:MICROVALOR_FALTA_INFO]. NO usa [AUDIO:METODO_INICIO_PROGRAMA]. |

---

### Caso 4 — "no sé cómo funciona todo" (variante edge, sin idea)

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `hola` | — |
| 2 | Agente | — | — |
| 3 | Usuario | `de cero` | — |
| 4 | Agente | — | — |
| 5 | Usuario | `no sé cómo funciona todo esto del tema de importaciones` | — |
| 6 | Agente | — | Usa [AUDIO:MICROVALOR_FALTA_INFO] o [AUDIO:MICROVALOR_NO_EMPIEZA]. NO usa [AUDIO:METODO_INICIO_PROGRAMA]. Sin producto nombrado → no hay condición para METODO. El agente puede hacer preguntas de diagnóstico después del audio. |

---

## Bloque B — MICROVALOR_MIEDO_PLATA vs ROMPER_MIEDO (fix #2)

### Caso 5 — "me da miedo perder plata"

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `buenas` | — |
| 2 | Agente | — | — |
| 3 | Usuario | `arranco de cero` | — |
| 4 | Agente | — | — |
| 5 | Usuario | `me da miedo perder plata, si invierto y no me va` | — |
| 6 | Agente | — | Usa [AUDIO:MICROVALOR_MIEDO_PLATA]. El texto incluye algo como "Te entiendo, es súper común eso…". NO usa ROMPER_MIEDO (que es para miedo al proceso de importar, no al resultado económico). |

---

### Caso 6 — "me da miedo no poder vender"

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `buenas` | — |
| 2 | Agente | — | — |
| 3 | Usuario | `arranco de cero` | — |
| 4 | Agente | — | — |
| 5 | Usuario | `me da miedo no poder vender` | — |
| 6 | Agente | — | Usa [AUDIO:MICROVALOR_MIEDO_PLATA]. NO usa ROMPER_MIEDO. "No poder vender" es miedo al resultado económico, no al proceso de importar. |

---

### Caso 7 — miedo al PROCESO de importar (debe usar ROMPER_MIEDO)

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `hola` | — |
| 2 | Agente | — | — |
| 3 | Usuario | `arranco de cero` | — |
| 4 | Agente | — | — |
| 5 | Usuario | `me parece muy complicado eso de importar, no tengo experiencia ni contactos` | — |
| 6 | Agente | — | Usa [AUDIO:ROMPER_MIEDO]. NO usa MICROVALOR_MIEDO_PLATA. "Muy complicado" + "no tengo experiencia" = creencia sobre el proceso de importar, no sobre el resultado económico. |

---

### Caso 8 — "¿y si no vendo?"

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `buenas` | — |
| 2 | Agente | — | — |
| 3 | Usuario | `quiero empezar algo propio` | — |
| 4 | Agente | — | — |
| 5 | Usuario | `¿y si no vendo nada?` | — |
| 6 | Agente | — | Usa [AUDIO:MICROVALOR_MIEDO_PLATA]. Es miedo al resultado de negocio. NO usa ROMPER_MIEDO. |

---

## Bloque C — REGLA ANTI-CADENA: excepción microvalor (fix #3)

### Caso 9 — microvalor en turno 3 (miedo a perder plata, excepción anti-cadena)

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `buenas` | — |
| 2 | Agente | — | — |
| 3 | Usuario | `arranco de cero` | — |
| 4 | Agente | — | — |
| 5 | Usuario | `me da miedo perder plata, si invierto y no me va` | — |
| 6 | Agente | — | Usa [AUDIO:MICROVALOR_MIEDO_PLATA] aunque sea el 3er audio en la secuencia. La excepción MICROVALOR permite enviarlo: el lead declaró su dolor específico. NO bloquea el audio por anti-cadena. |

---

### Caso 10 — microvalor proveedores en turno 3 (excepción anti-cadena)

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `buenas` | — |
| 2 | Agente | — | — |
| 3 | Usuario | `ya vendo algo, quiero importar` | — |
| 4 | Agente | — | — |
| 5 | Usuario | `el tema es que no sé a quién comprarle, me da miedo que me estafen` | — |
| 6 | Agente | — | Usa [AUDIO:MICROVALOR_PROVEEDORES] aunque haya 2 audios previos (RESPUESTA_INICIAL + LEAD_CON_NEGOCIO). La excepción MICROVALOR aplica: desconfianza en proveedores es dolor específico declarado. |

---

### Caso 11 — microvalor intento fracaso en turno 3 (excepción anti-cadena)

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `hola` | — |
| 2 | Agente | — | — |
| 3 | Usuario | `arranco de cero` | — |
| 4 | Agente | — | — |
| 5 | Usuario | `en realidad ya lo intenté antes pero no me fue bien` | — |
| 6 | Agente | — | Usa [AUDIO:MICROVALOR_INTENTO_FRACASO] aunque haya 2 audios previos. La excepción MICROVALOR aplica: intento fallido es dolor específico declarado. |

---

## Bloque D — Lead con interés declarado (fix #4)

### Caso 12 — "quiero empezar + ¿cuánto cuesta?" → "cuéntame"

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `quiero empezar, ¿de cuánto es el programa?` | — |
| 2 | Agente | — | Abre con [AUDIO:RESPUESTA_INICIAL]. |
| 3 | Usuario | `bien, cuéntame` | — |
| 4 | Agente | — | Presenta IC con precio USD 697 + los 4 pilares (clases grabadas, módulos, EN VIVO, 3 meses acompañamiento). NO reinicia el diagnóstico de perfil desde cero. El lead ya mostró intención en su primer mensaje. |

---

### Caso 13 — "¿cuánto vale?" → "dale, contame"

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `hola, ¿cuánto vale el programa de importaciones?` | — |
| 2 | Agente | — | Abre con [AUDIO:RESPUESTA_INICIAL]. |
| 3 | Usuario | `dale, contame` | — |
| 4 | Agente | — | Presenta IC con precio USD 697 + los 4 pilares del programa (clases grabadas, módulos, EN VIVO, 3 meses acompañamiento). NO reinicia diagnóstico de perfil desde cero. |

---

## Edge cases — positivos que deben seguir funcionando

### Caso 14 — lead con idea concreta sigue usando METODO

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `hola` | — |
| 2 | Agente | — | — |
| 3 | Usuario | `arranco de cero` | — |
| 4 | Agente | — | — |
| 5 | Usuario | `tengo una idea pero no sé cómo encararla` | — |
| 6 | Agente | — | Usa [AUDIO:METODO_INICIO_PROGRAMA]. "Una idea" mencionada explícitamente → condición para METODO. NO debe ir a microvalor. |

---

### Caso 15 — lead con producto concreto sigue usando METODO

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `buenas` | — |
| 2 | Agente | — | — |
| 3 | Usuario | `quiero importar ropa para vender` | — |
| 4 | Agente | — | — |
| 5 | Usuario | `no tengo claro por dónde empezar con eso` | — |
| 6 | Agente | — | NO usa [AUDIO:MICROVALOR_NO_EMPIEZA] ni MICROVALOR_FALTA_INFO. El lead ya declaró "ropa" como producto en T3 → el agente reconoce que la confusión es sobre cómo importar ropa, no sobre si tiene idea. No puede repetir [AUDIO:METODO_INICIO_PROGRAMA] (ya enviado en T4). Avanza el diagnóstico METODO: puede preguntar sobre el modelo de negocio ("¿ya vendés ropa?" / "¿cuánto capital tenés?") o presentar IC directamente. |

---

### Caso 16 — info + idea concreta → METODO gana

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|-------------------|
| 1 | Usuario | `hola` | — |
| 2 | Agente | — | — |
| 3 | Usuario | `de cero` | — |
| 4 | Agente | — | — |
| 5 | Usuario | `quiero importar pero no sé cómo funciona todo, tengo pensado vender electrónica` | — |
| 6 | Agente | — | Usa [AUDIO:METODO_INICIO_PROGRAMA]. Lead dijo "no sé cómo funciona" pero TAMBIÉN nombró "electrónica" → idea concreta gana. |

---

**Correcciones aplicadas en v1.9:** METODO variantes NO-disparador, distinción MICROVALOR_MIEDO_PLATA/ROMPER_MIEDO, excepción MICROVALOR en anti-cadena, LEAD CON INTERÉS DECLARADO.
