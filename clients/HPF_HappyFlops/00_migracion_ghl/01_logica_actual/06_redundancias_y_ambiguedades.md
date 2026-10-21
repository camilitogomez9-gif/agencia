# Redundancias y Ambigüedades — Sistema actual Happy Flops

> **Etapa 1 → Etapa 2.** Lista priorizada de items a validar con el usuario antes de avanzar al diseño de arquitectura GHL. Cada ítem propone una **hipótesis** y pide una decisión: **KEEP / REMOVE / MODIFY** + razón.

> **Cómo trabajar este documento en Etapa 2:** leer cada ítem, marcar la decisión, agregar justificación. Cuando todo esté KEEP/REMOVE/MODIFY decidido, congelar como `02_logica_validada/01_decisiones.md` y avanzar a Etapa 3.

---

## A. REDUNDANCIAS ESTRUCTURALES

### A.1 Tres nodos para mover a "confirmar pago" (91450360)

**Hallazgo:** existen tres nodos PATCH que mueven al mismo status_id `91450360`:
- `Confirmar Pago`
- `Confirmar Pago1`
- `Confirmar pago`

Cada uno está en una rama distinta del flujo de detección de pago (PDF, imagen analizada, imagen analizada alternativa).

**Hipótesis:** son funcionalmente idénticos. La razón probable es que cada uno se agregó al detectar un nuevo path (PDF detectado, imagen analizada por main path, imagen analizada por path alternativo). En GHL se reduce a 1 acción.

**Decisión esperada:** REMOVE 2 de 3 (consolidar en una sola transición en GHL).

**🔵 Validar:**
- [X] ¿Confirmás que las tres rutas (PDF, imagen path A, imagen path B) deben terminar en la misma transición?
	- Sí, confirmo. Además, toda la rama desde `Usr. Envia Imágenes/Documentos4` es idéntica en funcionalidad a la que empieza en `Usr. Envia Imágenes/Documentos5` y a la que empieza en `Usr. Envia Imágenes/Documentos2`.
- [X] ¿Hay alguna diferencia funcional entre las tres que no estoy viendo (por ejemplo, registran el origen del pago)?
	- No.

**Decición final:** REMOVE 2 de 3 (consolidar en una sola transición en GHL). Las tres ramas ejecutan exactamente los mismo pasos.

---

### A.2 Múltiples nodos `actualizar`/`actualizar6..21` que hacen PATCH al lead

**Hallazgo:** hay ~14 nodos `actualizar*` (sin numerar consistentemente — `actualizar`, `actualizar6`, `actualizar7`, ..., `actualizar23`). Todos hacen PATCH a `https://happyflopss.amocrm.com/api/v4/leads/{entity_id}`.

**Hipótesis:** muchos son duplicados creados al copiar ramas. Cada uno se ejecuta antes de un `Envio Mensaje` específico para actualizar el status_id antes del envío. La proliferación parece un efecto secundario de copy-paste.

**Decisión esperada:** REMOVE/CONSOLIDATE — en GHL una sola acción "update opportunity stage" antes de cualquier envío de mensaje.

**🔵 Validar:**
- [X] ¿Cada `actualizar` está moviendo el lead a un status_id diferente, o son todos al mismo destino?
	- Los nodos "actualizar" no cambian el status del lead sino que lo que hacen es cambiar el valor de una varible. Esta variable contiene el mensaje que se le va a enviar. Por lo tanto, estos nodos actualizan el mensaje que se le envía al lead. En muchos de ellos, el mensaje a enviar (`value`) está determinado por una variable que entregan los agentes del flujo. En otros casos, el valor del mensaje está hardcodeado. Es importante que en la solución final post0migración se envíe el mismo mensaje hardcodeado o respuesta generada por IA que se envía ahora en cada etapa o situación.
	- Notar que todos los nodos "Enviar mensaje" que se encuentran inmediatamente después de cada nodo "actualizar" lo que hacen es activar un bot de Kommo que lo que hace es enviar el valor del custom field de ese lead al chat (la variable que fue actualizada en el nodo previo).
- [X] (Si son distintos) → ¿la proliferación viene de las distintas combinaciones evento × producto?
	- N/A

**Decisión final:** REMOVE/CONSOLIDATE — en GHL una sola acción "update opportunity stage" antes de cualquier envío de mensaje.

---

### A.3 `AI Agent Recolector` y `AI Agent Recolector1` con prompts ~95% idénticos

**Hallazgo:** los dos agentes Recolector tienen el mismo system prompt. La única diferencia funcional es el formato del input:
- Recolector: recibe texto del lead.
- Recolector1: recibe `"Te envio una imagen del producto que quiero: [producto]"`.

**Hipótesis:** se puede unificar en **un solo agente** con un preprocesamiento de input que normalice ambos casos.

**Decisión esperada:** MODIFY — unificar en GHL como un solo agente "Vendedor" con preprocesamiento.

**🔵 Validar:**
- [X] ¿Hay alguna diferencia de comportamiento esperado entre Recolector y Recolector1 que justifique mantenerlos separados?
	- No, no hay ninguna diferencia significativa de comportamiento.

**Decisión final:** MODIFY — unificar en GHL como un solo agente "Vendedor" con preprocesamiento.

---

### A.4 Doble debouncing (50s y 15s) con dos keys Redis distintos

**Hallazgo:** el sistema tiene dos rutas de Redis paralelas:
- Key `contact_id` con `Wait_35` (50s).
- Key `numero_telefono` con `Wait_15s` (15s).

**Hipótesis:** la ruta de 50s es para mensajes de texto/audio (necesita más tiempo por si hay ráfaga); la de 15s es post-análisis-de-imagen (ya pasó tiempo en `Analyze image`, no se necesita esperar tanto). Funcionan en paralelo según la rama del flujo.

**Decisión esperada:** MODIFY — en GHL, una sola lógica de debouncing con valor único (probablemente 30-45s).

**🔵 Validar:**
- [X] ¿Confirmás que estas dos rutas son por tipo de input (texto/audio vs imagen) y no por otra razón?
	- Sí, confirmo.
- [X] ¿Querés mantener un debounce dual o un único timeout (más simple)?
	- Único timeout.

---

### A.5 19 nodos `noOp` (placeholders sin lógica)

**Hallazgo:** 19 nodos `n8n-nodes-base.noOp` (`No Operation, do nothing`, `..1`, `..2`, ...) están dispersos en el flujo. Cada uno cierra una rama IF que conduce a "no hacer nada".

**Hipótesis:** son cierres explícitos de ramas (estilo defensivo). En GHL, simplemente no se conecta la rama.

**Decisión esperada:** REMOVE en migración (no aportan a la lógica).

**🔵 Validar:**
- [X] ¿Algún noOp tenía función futura (placeholder a implementar) o todos son cierres definitivos?
	- Todos son cierres definitivos.

**Decisión final:** REMOVE en migración (no aportan a la lógica).

---

### A.6 5 nodos `stickyNote` (documentación)

**Hallazgo:** son notas explicativas dentro del workflow.

**Hipótesis:** documentación informal del flujo.

**Decisión esperada:** REMOVE estructuralmente, **TRANSFERIR contenido** a la nueva documentación GHL.

**🔵 Validar:**
- [X] ¿Querés que extraiga el texto de las stickyNotes y lo agregue al mapa funcional?
	- No. Elimínalas.

**Decisión final:** REMOVE estructuralmente.

---

## B. REDUNDANCIAS FUNCIONALES (DUPLICACIÓN DE LÓGICA)

### B.1 Tres modelos LLM "helper" que hacen formato de salida

**Hallazgo:** hay tres LLMs no-conversacionales involucrados en el postprocesamiento del output del agente:
- `Necesita Respuesta Especial` (gpt-5-mini): decide si el output requiere envío de adjunto.
- `Message a model` (gpt-4.1-mini): formatea texto largo en parte1/2/3.
- `Message a model1` (gpt-4.1-mini): variante del anterior para rama de imagen.
- `Formatear mensaje1`: variante adicional.

**Hipótesis:** estos helpers existen porque WhatsApp tiene límites de longitud y se quiere efecto humano (split + waits). En GHL, la división puede hacerse con regex + workflow steps, sin LLM intermedio.

**Decisión esperada:** REMOVE — eliminar LLMs intermedios, usar lógica determinística de división.

**🔵 Validar:**
- [X] ¿La división en parte1/2/3 es solo por longitud o por contenido semántico?
	- Por contenido semántico. También para evitar mensajes muy largos en un solo bloque.
- [X] ¿`Necesita Respuesta Especial` tiene una lógica concreta o es un meta-evaluador difuso?
	- Tiene lógica concreta.

**Notas importantes:**
- `Message a model` y `Necesita Respuesta Especial` NO formatean texto largo en partes. Cumplen otras funciones diferentes que no necesariamente pueden sustituirse por regex + workflow steps. Quizás sí, pero cumplen una función diferente.
- `Message a model1` y `Formatear mensaje1` cumplen otras funciones además de simplemente dividir el mensaje en partes. Es importante que tanto las reglas y criterios de división del mensaje en partes como las otras funcionalidades que cumplen estos nodos permanezcan en la lógica final post migración. Por ejemplo: una parte del prompt de estos nodos explicita un filtro para preguntas que puedan sonar agresivas o que empujen la venta demasiado; esa misma regla podría moverse al system prompt del agente previo para que, directamente, no genere ese tipo de preguntas.

**Decisión final:** REMOVE — eliminar LLMs intermedios, usar lógica determinística de división **ÚNICAMENTE** para `Message a model1` y `Formatear mensaje1`. MODIFY `Message a model` y `Necesita Respuesta Especial` - siguen una serie de reglas determinísticas que pueden sustituirse por código (analizar cada caso por separado).

---

### B.2 Cuatro sub-workflows de seguimiento con estructura idéntica

**Hallazgo:** Seg. Rebeca, Seg. Imagen, Seg. Cotización, Seg. 7pasos comparten el patrón:
```
Wait → Query Postgres (¿AI dijo X?) → IF → si NO respondió, mover etapa + enviar mensaje + INSERT seguimiento → Wait → ...
```

Las únicas diferencias son:
- Patrón de texto a buscar.
- Etapa-destino de cada wave.
- Bot_id del salesbot.

**Hipótesis:** se pueden unificar en GHL como un **único sistema de timers de inactividad** con triggers basados en etapa actual.

**Decisión esperada:** MODIFY — en GHL: un solo workflow "Re-engagement" con condiciones por etapa.

**🔵 Validar:**
- [X] ¿Confirmás que las 4 sub-workflows funcionalmente representan "el mismo proceso pero por etapa"?
	 - No, tienen diferentes lógicas.
- [X] ¿Hay algua excepción en las cadencias (1h/3h/24h) entre ellas que importa preservar?
	- Sí.
- [X] ¿Los mensajes de re-engagement de cada wave están definidos en los salesbots Kommo? (Necesitamos sus textos para reproducirlos.)
	- Sí, son distintos.

---

### B.3 Dos lógicas paralelas de `If21 → If20 → checkType` y `If23 → Es PDF?`

**Hallazgo:** hay dos rutas casi paralelas que filtran el lead por status y tipo de mensaje. Aparentemente una para mensaje texto y otra para mensaje con archivo adjunto.

**Hipótesis:** la duplicación es para manejar la rama de imágenes (que requiere `Analyze image`) en paralelo a la rama de texto.

**Decisión esperada:** MODIFY — en GHL, un solo workflow con un Switch al inicio que bifurca por tipo y luego converge.

**🔵 Validar:**
- [Sí] ¿Es correcto que las dos rutas son por tipo de input (texto vs media)?

---

### B.4 Mensaje de "Foto Vacaciones" + lógica de horario laboral

**Hallazgo:** múltiples nodos `Code6/7/10/11/12` calculan `isWithinBusinessHoursMx`. Si fuera de horario y se recibe pago → respuesta auto.

**Hipótesis:** GHL tiene "Business Hours" nativo en sub-account. Una sola configuración + un workflow con condición "fuera de horario".

**Decisión esperada:** MODIFY — usar Business Hours nativo de GHL.

**🔵 Validar:**
- [X] ¿El mensaje "Foto Vacaciones" se envía solo en respuesta a pagos fuera de horario, o también en otros casos?
	- Siempre que se encuentren de vacaciones.

**Decisión final:** MODIFY — usar Business Hours nativo de GHL.

---

## C. REDUNDANCIAS DE INFRAESTRUCTURA

### C.1 Doble CRM activo (Kommo v4 + AmoCRM v2)

**Hallazgo:**
- ~7 nodos usan `https://happyflopss.kommo.com/api/v4/...` (moderna).
- ~44 nodos usan `https://happyflopss.amocrm.com/api/v4/...` o `/api/v2/...` (legacy).

**Hipótesis:** Kommo es el rebrand de AmoCRM — ambos URLs apuntan a la misma cuenta y backend. La duplicación es por inercia histórica (el sistema empezó con AmoCRM y se modernizó parcialmente).

**Decisión esperada:** REMOVE legacy en migración. **No tocar antes de cutover** (puede romper algo). Eliminar después del cutover.

**🔵 Validar:**
- [X] ¿Confirmás que ambos URLs son la misma cuenta Kommo y se pueden consolidar usando solo Kommo v4?
	- Sí, confirmo.
- [X] ¿Hay algún endpoint que SOLO funcione en `/api/v2/` (legacy) y no en `/api/v4/`? (Sospechoso: `/api/v2/salesbot/run` podría no tener equivalente moderno.)
	- No. Todos funcionan.

**Decisión esperada:** REMOVE legacy en migración. **No tocar antes de cutover** (puede romper algo). Eliminar después del cutover.

---

### C.2 Tres capas de estado (Redis + Postgres + Kommo) — ¿son realmente las tres necesarias?

**Hallazgo:**
- **Redis:** debouncing (acumular mensajes en ráfaga 15-50s).
- **Postgres LangChain Memory:** historial conversacional completo.
- **Kommo:** estado del lead (etapa).

**Hipótesis:**
- Redis se puede reemplazar con GHL Workflow Wait + workflow re-trigger.
- Postgres LangChain Memory se reemplaza con GHL Conversations.
- Kommo → GHL Pipeline (1:1).

**Decisión esperada:** REMOVE Redis y Postgres en GHL. Mantener todo nativo.

**🔵 Validar:**
- [X] ¿Necesitás conservar el historial Postgres post-migración (analytics, auditoría)?
	- No.
- [X] ¿Es aceptable que el historial conversacional viva solo en GHL Conversations sin export adicional?
	- No. Necesitamos guardar el historial de mensajes.
- [X] Si necesitás analytics: ¿BigQuery/Postgres externo con export de GHL es suficiente?
	- Sí.

---

### C.3 Múltiples versiones de modelos LLM (gpt-4o, gpt-4o-mini, gpt-4.1-mini, gpt-5-mini)

**Hallazgo:** 6 modelos OpenAI distintos en uso simultáneo:
- `gpt-4o` × 3 (análisis de imágenes)
- `gpt-4o-mini` × 1
- `gpt-4.1-mini` × 4
- `gpt-5-mini` × 1 (Necesita Respuesta Especial)

**Hipótesis:** la heterogeneidad es por iteración no consolidada. Cada vez que se agregó un nodo, se eligió el modelo "del momento". Probablemente se puede consolidar en 2-3 modelos como máximo.

**Decisión esperada:** MODIFY — consolidar a:
- 1 modelo principal para agentes conversacionales (probablemente `gpt-4.1-mini` o equivalente).
- 1 modelo para análisis de imagen (`gpt-4o`).
- 1 modelo helper para clasificación rápida (mini).

**🔵 Validar:**
- [X] ¿Hay performance crítica que dependa del modelo específico de algún nodo?
	- No.
- [X] ¿Querés mantener `gpt-4o` para imágenes o probar Vision en GHL nativo?
	- Probemos Vision en GHL.

**Decisión final:** MODIFY — consolidar a:
- 1 modelo principal para agentes conversacionales (probablemente `gpt-4.1-mini` o equivalente).
- 1 modelo para análisis de imagen (`gpt-4o`).
- 1 modelo helper para clasificación rápida (mini).

---

### C.4 Pipeline IDs hardcodeados en URLs

**Hallazgo:** los IDs `11622596`, `91450360`, `91266100`, `100395523` están escritos directamente en URLs de PATCH y en condiciones IF.

**Hipótesis:** si se cambia algún ID en Kommo (rara pero posible), se rompe el sistema. En GHL, los IDs deben venir de variables/Custom Values, no hardcoded.

**Decisión esperada:** MODIFY — usar variables/configuración en GHL.

**🔵 Validar:**
- [X] ¿Estos IDs se cambiaron alguna vez históricamente o han sido estables?
	- Han sido estables.

**Decisión final:** MODIFY — usar variables/configuración en GHL.

---

## D. AMBIGÜEDADES DE DATOS

### D.1 ¿Para qué sirve exactamente el `bot_id` en cada producto Airtable?

**Hallazgo:** cada fila de `Imagen Principal`, `Boda`, `XV`, `Otros` tiene un campo `bot_id` (numérico, ej: `60810`, `60814`, `60816`). Hay también un `CURL` con un payload completo.

**Hipótesis:** El `bot_id` es el ID de un **salesbot Kommo** (script de automatización en Kommo). El sistema dispara `POST /api/v2/salesbot/run` con ese `bot_id` y el salesbot ejecuta el envío del producto (con la imagen ya subida a Kommo).

El `CURL` en cambio es un sendMessage directo (alternativa que NO usa salesbot, sino el endpoint amojo).

**Decisión esperada:** ENTENDER cuál es la fuente de verdad para luego reproducir en GHL.

**🔵 Validar:**
- [X] ¿Confirmás que el bot_id apunta a un salesbot en Kommo que tiene el producto pre-cargado?
	- Sí, confirmo.
- [X] ¿En la migración a GHL, vamos a tener que recrear estos salesbots (ahora como GHL Workflows) o vamos a reemplazarlos con HTTP requests + adjuntos?
	- Lo que sea más profesional, simple y robusto.
- [X] ¿Querés mantener Airtable como source of truth de productos durante un periodo, o migrar todo a GHL Custom Objects/Files?
	- Migrar todo a GHL Custom Objects/Files.

**Decisión final:** MODIFY. La fuente de verdad de productos pasa a alojarse en GHL, así como los salesbots.

---

### D.2 Los CURLs en Airtable contienen IDs de contactos de prueba

**Hallazgo:** los CURLs tienen valores como `recipient_id: "afebf778-..."`, `crm_dialog_id: 159636`, `crm_contact_id: 23241591`, `crm_account_id: 33068423`, `crm_entity:{id:21116147,type:2}`. Estos son IDs de contactos específicos.

**Hipótesis:** Los CURLs son **plantillas**. n8n los lee, **reemplaza dinámicamente** los IDs con los del lead actual (de `All_Data`), y luego ejecuta. El `Code3` y `Code5/9` parecen hacer esta sustitución.

**Decisión esperada:** ENTENDER el patrón exacto de sustitución para replicarlo en GHL.

**🔵 Validar:**
- [X] ¿Confirmás esa hipótesis (los CURLs son plantillas, no se ejecutan tal cual)?
	- Son plantillas
- [X] ¿Querés que extraiga el código de sustitución de `Code3`/`Code5`/`Code9` y lo documente?
	- Los CURLs están total y completamente obsoletos.

**Decisión final:** REMOVE completamente la lógica de los CURLs, no se utilizan actualmente.

---

### D.3 Mensajes de seguimiento (waves 1h/3h/24h) — ¿dónde viven?

**Hallazgo:** los sub-workflows detectan patrones en memoria (ej: `"sigues por aquí?"`, `"Cuéntame, es para boda..."`) pero NO están los textos completos. Solo los primeros caracteres como "trigger" para identificar dónde está la conversación.

**Hipótesis:** los mensajes completos de seguimiento están **dentro de los salesbots Kommo** (cada salesbot tiene un texto pre-cargado y se dispara por bot_id). n8n solo decide cuál disparar, no compone el texto.

**Decisión esperada:** EXTRAER los textos de los salesbots Kommo para reproducirlos en GHL.

**🔵 Validar:**
- [X] ¿Confirmás que los mensajes están en salesbots Kommo y no en n8n?
	- Sí, confirmo.
- [X] ¿Podés exportar/screenshotear los salesbots para que extraigamos los textos?
	- Sí, lo hago en un documento a parte.

**Decisión final:** los textos de los salesbots se encuentran en 'textos_salesbots.txt'

---

### D.4 Pipelines paralelos: ¿cuáles están realmente en uso?

**Hallazgo:** Kommo tiene 13 pipelines, pero solo `IA` (11622596) está conectado al agente. Los otros 12 (`SANDALIAS BODAS`, `SANDALIAS XV AÑOS`, `Cilindros`, `Mandiles`, `Kit anticrudas`, `Pantuflas`, `Sandalia lisa`, `Happyfloops`, `XV AÑOS`, `BODAS`, `Reactivadores Genericos`, `GENERAL`) son legacy.

**Hipótesis:** algunos están vivos (gestión manual del equipo), otros están abandonados.

**Decisión esperada:** clasificar cada uno como ACTIVO MANUAL / LEGACY ARCHIVO / LIMBO.

**🔵 Validar:**

| Pipeline ID | Nombre | ¿Estado? |
|------------|--------|---------|
| 9018931 | GENERAL | ACTIVO MANUAL  |
| 9111555 | SANDALIAS BODAS | LIMBO |
| 9111991 | SANDALIAS XV AÑOS | LIMBO |
| 9112155 | Cilindros | LIMBO |
| 9112275 | Mandiles | LIMBO |
| 9122183 | Kit anticrudas | LIMBO |
| 9122527 | Pantuflas | LIMBO |
| 9122659 | Sandalia lisa | LIMBO |
| 9146991 | Happyfloops | LIMBO |
| 9194491 | XV AÑOS | LIMBO |
| 9194495 | BODAS | LIMBO |
| 12081404 | Reactivadores Genericos | LIMBO |

---

### D.5 Etapas R1-R5 sin/con info / ap (45 etapas en sub-pipeline de seguimientos)

**Hallazgo:** el pipeline IA tiene 17 etapas dedicadas a seguimientos (`r1 sin/con info/ap`, `r2 sin/con info/ap`, ..., `r5 sin/con info/ap`, `sin info especial`, `con info especial`).

**Hipótesis:** el sistema mueve el lead progresivamente a través de Rn cuando no responde. La distinción "sin info" / "con info" / "ap" indica el contexto previo (sin info de pedido / con info / vino de atención personalizada).

**Decisión esperada:** SIMPLIFICAR — en GHL, no necesitamos 17 etapas para esto. Una sola "Re-engagement" con tags + custom values puede capturar lo mismo.

**🔵 Validar:**
- [X] ¿Las distintas Rn corresponden a momentos temporales distintos (T+24h, T+48h, T+7d, etc.)?
	- Sí. Es correcto.
- [X] ¿Querés mantener el granularismo de la distinción "sin info / con info / ap" o lo aceptamos consolidado?
	- Lo aceptamos consolidado.
- [X] ¿Existe algún reporte que use estas etapas para métricas (% de conversión por wave, etc.)?
	- Actualmente, no.

---

### D.6 ¿`If25` (entity_id == 8075544) qué hace?

**Hallazgo:** uno de los primeros IFs verifica `entity_id == 8075544`. **Ambas ramas conducen al mismo nodo** `Get_Contact`.

**Hipótesis:** este IF era un toggle de tracking/debugging para un lead específico (probablemente sandbox de Diego/equipo). No filtra, solo "marca".

**Decisión esperada:** REMOVE — no hay efecto funcional.

**🔵 Validar:**
- [X] ¿Confirmás que este IF no tiene efecto observable?
	- Sí, confirmo.
- [X] ¿`8075544` es algún lead/contacto especial (de testing) que querés conservar?
	- Sí, es el lead de Oscar. Podemos conservar la referencia del lead id en algún lado. Puede ser en alguna documentación, no tiene por qué ser dentro del flujo.

---

### D.7 Workflows ID referenciados pero no exportados

**Hallazgo:** los `Execute Workflow` en main-v2 hacen referencia a workflows con IDs:
- `D04kO8VPKoAKL004` → "Happy Flops - Seg. Imagen" ✅ tenemos
- `dNzLtCZFJnIqjlZx` → "Happy Flops - Seg. Cotización" ✅ tenemos
- `xo1sLt9cAhFAC6k3` → "Happy Flops - Seg. 7 pasos" ✅ tenemos
- `YR8yBPNdgVl0TxT1` → "HappyFlops - Seg. Rebeca" ✅ tenemos
- **`nkRBXbc4G0Cn67gY` → ¿qué es?** (referenciado en `Execute Workflow4`)

**Hipótesis:** podría ser el workflow "Foto Vacaciones" / fuera de horario, o algo más. No tenemos su JSON exportado.

**Decisión esperada:** CONSEGUIR este workflow.

**🔵 Validar:**
- [X] ¿Podés exportar el workflow con ID `nkRBXbc4G0Cn67gY` y agregarlo a `00_inputs/`?
	- No. No existe. El workflow que ese nodo debería llamar es `xo1sLt9cAhFAC6k3` → "Happy Flops - Seg. 7 pasos".

**Decisión esperada:** MODIFY. Cambiar el id de workflow al indicado.

---

## E. AMBIGÜEDADES DE COMPORTAMIENTO

### E.1 step_2 vs step_3 cuando lead identifica evento + producto en mismo turno

**Hallazgo:** el system prompt del Router tiene instrucciones contradictorias:
- En la sección general: "una vez que la persona haya elegido el evento debemos si o si guiarlo a este step_2"
- En los ejemplos: "Para una boda, quiero 50 sandalias y 40 cilindros" → `step_3` (NO step_2)

**Hipótesis:** la regla efectiva es: si el lead identifica evento + producto en el mismo turno, salta step_2 y va directo a step_3 (mostrar productos). El step_2 es para casos donde el lead solo dice el evento, sin producto.

**Decisión esperada:** ACLARAR en la versión nueva del prompt para Etapa 3.

**🔵 Validar:**
- [X] ¿Confirmás que si lead identifica evento+producto, salta step_2 y va a step_3?
	- Sí, confirmo.
- [X] (Si sí) → la imagen principal del catálogo nunca se envía si lead pidió producto desde el primer turno con evento — ¿es correcto?
	- Sí, es correcto.

---

### E.2 ¿Cuándo se mueve el lead a `93616840` (ETAPA 4)?

**Hallazgo:** no hay un nodo `ETAPA 4` explícito (a diferencia de ETAPA 2 y 3). La etapa 4 aparece en condiciones IF (`If10`, `If11` checkean si data == 93616840) pero **no se ejecuta un PATCH a 93616840**.

**Hipótesis:** la etapa 93616840 puede que la mueva un salesbot Kommo (configurado por fuera de n8n) cuando se envía la cotización. O puede ser una etapa intermedia que el equipo mueve manualmente.

**Decisión esperada:** ACLARAR antes de Etapa 3.

**🔵 Validar:**
- [X] ¿La etapa ETAPA 4 (93616840) la mueve algún salesbot? ¿Cuál?
	- La ETAPA 4 se mueve con el nodo `ETAPA 3` del flujo `Happpy Flops - Seg. 7 pasos`.

---

### E.3 Patrón de wait `Wait2` con valor vacío

**Hallazgo:** los sub-workflows tienen `Wait2` con `amount=""` y `unit=""`. Sospechoso.

**Hipótesis:** podría ser un wait con valor configurable por variable de entorno, o un bug.

**Decisión esperada:** REVISAR antes de migrar.

**🔵 Validar:**
- [X] ¿Podés abrir el nodo `Wait2` en n8n y ver si tiene un valor real (sea por variable o expresión)?
	- El nodo `Wait2` se encuentra en el flujo principal, no en un sub-workflow. Además, está setteado a 1.00 segundo. De todos modos, se puede eliminar.


**Decisión esperada:** REMOVE. No altera la lógica ni el funcionamiento del sistema.

---

### E.4 ¿`Necesita Respuesta Especial` qué evalúa exactamente?

**Hallazgo:** el nodo es un LLM (`gpt-5-mini`) que aparentemente toma el output del Recolector y devuelve `{"response":"sí|no"}`. Su system prompt no se muestra en el extracto que leímos.

**Hipótesis:** decide si la respuesta del Recolector requiere envío adicional (ej: PDF de Métodos de Pago).

**Decisión esperada:** EXTRAER el system prompt de este nodo y documentarlo.

**🔵 Validar:**
- [X] ¿Querés que lo extraiga directamente del JSON?
	- Sí, extráelo del JSON. Deberías hacer eso con todos los system prompt, user prompt, system message, user message, y similares.

---

### E.5 ¿`Saludo PTE 1`, `2`, `3` son del Starter o son re-engagement?

**Hallazgo:** después del `Call 'HappyFlops - Seg. Rebeca'` y `If24` (¿output contiene `👼🏢`?), va a `Saludo PTE 1` → `Wait6` (2s) → `Saludo PTE 2` → `Wait7` (2s) → `Saludo PTE 3`.

**Hipótesis A:** es el saludo Starter dividido en 3 partes para efecto humano (lo más probable, dado el contenido `👼🏢` que es del menú del saludo).

**Hipótesis B:** es un mensaje de re-engagement de Seg. Rebeca que se dispara inmediatamente después.

**Decisión esperada:** ACLARAR. Cambia mucho el modelo del saludo.

**🔵 Validar:**
- [X] ¿`Saludo PTE 1/2/3` son las 3 partes del saludo inicial o son del flujo de re-engagement?
	- Son del saludo inicial. Eso lo vas a entender mejor cuando veas el documento con los textos de los salesbot

---

### E.6 Productos por evento — confirmar el set "Otros"

**Hallazgo:** el CSV `Otros-Grid view.csv` no incluye Mandiles (correcto), pero tampoco vi explícitamente Pantuflas mono satín ni Vasos popote. La estructura del CSV "Otros" tiene C1-C4 (Cilindros con 4 variantes en lugar de 3), lo que sugiere catálogo diferente.

**Hipótesis:** "Otros" tiene un subconjunto de productos respecto a Boda/XV.

**Decisión esperada:** VALIDAR el catálogo exacto por evento.

**🔵 Validar:**

| Producto | Boda | XV | Otros |
|----------|------|----|-------|
| Sandalias | ✅ | ✅ | ✅ |
| Pantuflas satín pers. | ✅ | ✅ | ✅ |
| Pantuflas mono satín | ✅ | ✅ | ❌ |
| Pantuflas mono peluche | ✅ | ✅ | ❌ |
| Cilindros | ✅ | ✅ | ✅ |
| Kit anticruda | ✅ | ✅ | ✅ |
| Mandiles | ✅ | ❌ | ❌ |
| Vasos popote | ✅ | ✅ | ❌ |


**Decisión final:** Validado.


---

### E.7 Precio Pantuflas: $29 vs $30

**Hallazgo:** los CSVs muestran descripciones con precio `$29` pero los CURLs (que parecen actualizados) usan `$30`.

**Hipótesis:** el precio cambió de $29 a $30 y los CSVs no se actualizaron uniformemente. Los CURLs son la fuente de verdad reciente.

**Decisión esperada:** CONFIRMAR precios actuales y consolidar.

**🔵 Validar:**
- [X] Precios actuales 2026 confirmados:
  - Sandalias delgadas: $25
  - Sandalias gruesas: $30
  - Pantuflas: $30
  - Cilindros: $10
  - Kit anticruda: $10
  - Mandiles: $12
  - Vasos popote: $35
  - Bolsa personalizada: $7

 **Decisión final:** Precios confirmados.

---

## F. CANDIDATOS A SIMPLIFICACIÓN AGRESIVA

### F.1 Reducir 31+ etapas del pipeline IA a 8-10 etapas en GHL

**Propuesta:**

| Etapa actual | Propuesta GHL |
|--------------|---------------|
| Incoming leads | New Lead |
| ETAPA 1 / Saludo | Greeted |
| ETAPA 2 / Imagen | Engaged (with event) |
| ETAPA 3 / Productos | Showed Products |
| ETAPA 4 / Cotización | Quoted |
| confirmar pago | Awaiting Payment |
| PAGO SIN DISEÑO + DISEÑO + en producción | In Production |
| pago liquidacion | Awaiting Final Payment |
| Logrado con éxito | Won |
| Ventas Perdidos | Lost |
| atencion personalizada | (Tag `human_takeover`) |
| R1-R5 sin/con info/ap | (Tags `re_engagement_wave_N`) |

**🔵 Validar:**
- [X] ¿Aceptás esta consolidación o querés mantener mayor granularismo en algún punto?
	- **Contexto:** Oscar aclaró el flujo completo post-Etapa 4:

| Etapa | Responsable | Descripción |
|-------|-------------|-------------|
| Confirmar pago | IA → Humano | IA detecta pago, manda mensaje de "gracias, te confirmamos en la brevedad". **IA se detiene aquí.** Equipo humano confirma manualmente. |
| Pago sin diseño | Diseñadora | Lead pagó pero no tiene diseño. **Prioridad alta** — el cliente siente incertidumbre post-pago. |
| Diseño | Diseñadora | Diseño enviado, pendiente aprobación del cliente. Prioridad menor. |
| Producción | Equipo | Diseño aprobado, en producción física. |
| Pago de liquidación | IA + Humano | Al terminar producción, se envía saldo. **IA detecta segundo pago** y mueve a esta etapa. Luego se genera guía de envío. |
| Logrado con éxito | — | Venta completada, sale del pipeline visible. |
| Ventas Perdidos | - | Venta perdida, el lead dejó de contestar. Sale del pipeline visible

**Decisión:** Mantener las tres etapas post-pago (sin diseño / diseño / producción) como separadas. Oscar, la diseñadora y Rebeca ven diferentes vistas del mismo pipeline — cada una necesita su visibilidad.

**Problema resuelto:** Se confirmó que la IA debe reactivarse en "Producción" para detectar el pago de liquidación (segundo pago).

---

### F.2 Eliminar AmoCRM legacy

**Propuesta:** después del cutover GHL, deprecar todos los endpoints `/api/v2/`. El equipo Kommo puede confirmar si hay funcionalidades únicas allí.

**🔵 Validar:**
- [X] ¿Querés desactivar AmoCRM legacy ya en Etapa 2 (limpieza pre-migración) o esperar al cutover final?
	- Esperamos al cutover final.

---

### F.3 Unificar 6 LLMs en 2-3

**Propuesta:**

| Actual | Propuesta GHL |
|--------|---------------|
| AI Agent (Router) | Eliminado: lógica de step → workflow conditions |
| AI Agent Starter | Eliminado: mensaje fijo (workflow GHL envía) |
| AI Agent Main Image | Eliminado: identificación de evento + envío fijo (workflow GHL) |
| AI Agent Products | Mantenido o reemplazado por workflow lookup en Airtable |
| AI Agent Recolector | Mantenido como **único agente conversacional** ("Vendedor") |
| AI Agent Recolector1 | Unificado en Recolector |
| Analyze image | Mantenido (Vision Classifier) |
| Necesita Respuesta Especial | Eliminado: lógica determinística |
| Message a model / Formatear | Eliminado: split determinístico |

**Resultado:** 2 LLMs activos (Vendedor + Vision Classifier) + workflow GHL maneja routing.

**🔵 Validar:**
- [X] ¿Estás de acuerdo con eliminar el Router y manejarlo con conditions en GHL Workflow?
	- Sí.
- [X] ¿Querés mantener un agente solo para "Productos" o consolidar todo en el Vendedor?
	- Consolidemos todo en el Vendedor.

---

## G. RESUMEN DE PREGUNTAS CRÍTICAS PARA ETAPA 2

Las **10 preguntas más urgentes** para destrabar Etapa 3:

1. **D.1** — ¿Cómo funciona exactamente el `bot_id` de Airtable + el endpoint `salesbot/run`?
	R: El `bot_id` es el ID de un **salesbot Kommo** (script de automatización en Kommo). El sistema dispara `POST /api/v2/salesbot/run` con ese `bot_id` y el salesbot ejecuta el envío del producto (con la imagen ya subida a Kommo).
2. **D.3** — ¿Los textos completos de los re-engagement están en salesbots Kommo? Necesitamos exportarlos.
	R: Sí. Están en "textos_salesbots.txt"
3. **D.4** — Estado de los 12 pipelines paralelos (¿qué se mantiene, qué se archiva?).
	R: 
4. **D.7** — Exportar el workflow `nkRBXbc4G0Cn67gY` (no lo tenemos).
	R: Ese workflow no existe. Fue reemplazado por `xo1sLt9cAhFAC6k3`.
5. **E.1** — Comportamiento real del Router cuando lead da evento+producto en mismo turno.
	R: la regla efectiva es: si el lead identifica evento + producto en el mismo turno, salta step_2 y va directo a step_3 (mostrar productos). El step_2 es para casos donde el lead solo dice el evento, sin producto.
6. **E.2** — ¿Quién mueve el lead a `93616840` (ETAPA 4)?
	R: El nodo `ETAPA 3` del flujo `Happpy Flops - Seg. 7 pasos`
7. **E.5** — ¿`Saludo PTE 1/2/3` son del Starter o re-engagement?
	R: Starter.
8. **E.7** — Tabla de precios actualizada (consolidar $29 vs $30 etc.).
	R: Consolidado.
9. **F.1** — Aprobar la consolidación de etapas Kommo a un set reducido.
	R: Revisar en la respuesta.
10. **F.3** — Aprobar la consolidación de LLMs a 2-3.
	R: Aprobado.

Una vez resueltas estas 10, las decisiones secundarias (A, B, C) se siguen lógicamente.
