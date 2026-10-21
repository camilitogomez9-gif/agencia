---
name: iterar-prompt
description: >
  Usar este skill cuando el usuario quiera actualizar un system prompt existente con nueva
  información, o cuando comparta los resultados de un testing para corregir el prompt.
  Se activa con frases como "iterar prompt", "integrar esto al prompt", "actualizar el prompt con...",
  "nueva documentación para el agente", "resultados del testing", "corregir el prompt",
  "ajustes post-testing", "el cliente mandó correcciones", "incorporar feedback al prompt",
  o cuando el usuario pega o adjunta archivos junto a una mención del agente o el prompt.
  Siempre busca automáticamente el prompt actual del cliente, versiona antes de modificar,
  guarda la versión actualizada, y entrega el prompt final en bloque de código para n8n.
---

# Skill: Iterar Prompt

## Descripción

Gestiona el ciclo de vida iterativo de un system prompt ya existente. Cubre dos casos:

- **Modo A — Integrar nueva información:** el usuario trae documentos, correcciones del cliente, nueva info de producto, feedback de uso real, o cualquier material que debe incorporarse al prompt.
- **Modo B — Post-testing:** el usuario comparte los resultados de una guía de testing completa y quiere corregir el prompt en base a los fallos detectados.

En ambos casos: versiona el prompt anterior, aplica los cambios mínimos necesarios, y genera o actualiza la guía de testing.

---

## Recursos de Referencia

- **Template guía de testing:** `_core/templates/agents/testing-guide-template.md`
- **Guía de principios:** `_core/standards/system-prompt-engineering.md`
- **Prompt actual del cliente:** `clients/[CLT###_Nombre]/04_agents/agente-[nombre]-system-prompt.md`
- **Guía de testing actual:** `clients/[CLT###_Nombre]/07_testing/testing-guide-v[N].md`

---

## Detección de Modo

**Modo A — Integrar nueva información**
Señales: el usuario adjunta o pega documentos, menciona correcciones del cliente, trae nueva info de productos/precios/procesos, o indica que hay material nuevo para incorporar al prompt.

**Modo B — Post-testing**
Señales: el usuario adjunta o pega una guía de testing con la columna "Resultado obtenido" completada, o menciona explícitamente que terminó el testing y hay errores a corregir.

Si no está claro, preguntar: "¿Estás trayendo nueva información para integrar al prompt, o estás compartiendo los resultados del testing?"

---

## Flag de Testing

El testing automatizado (pasos A.8b y B.7b) es el comportamiento **por defecto**. Se omite únicamente si el usuario lo indica explícitamente en su mensaje.

**Señales de "omitir testing":** "sin testing", "solo iterar", "sin test", "no testees", "saltar testing", "skip testing", o cualquier frase equivalente.

Si el usuario no dice nada al respecto → ejecutar testing automáticamente (no preguntar).
Si el usuario lo indica → omitir los pasos A.8b / B.7b y entregar el prompt directamente después de guardarlo.

---

## MODO A — Integrar Nueva Información

### Paso A.1 — Leer el contexto

Identificar el cliente: por nombre explícito, por contexto de la conversación, o por el archivo adjunto.
Si no es posible determinarlo, preguntar antes de continuar.

Leer siempre:
- El prompt actual (archivo principal, sin sufijo de versión): `clients/[CLT###_Nombre]/04_agents/agente-[nombre]-system-prompt.md`
- Todos los archivos o texto que el usuario adjuntó o pegó en el chat

El archivo principal es siempre la versión más reciente — no leer los archivos con sufijo de versión (`-v1.1.md`, etc.), esos son backups.

### Paso A.1b — Verificación de scope (BLOQUEANTE)

Inmediatamente después de identificar el cliente, antes de analizar ningún material nuevo:

**1. Leer `clients/[CLT###_Nombre]/CLIENT_INFO.md` y extraer:**
- Nombre del negocio (campo "Nombre")
- Niche
- Servicios principales (sección OKRs o Stack)

**2. Declarar el scope activo en la respuesta al usuario:**
```
Scope activo: [NOMBRE_NEGOCIO] ([NICHE]) — [CLT###]
```

**3. Para cada dato concreto presente en el nuevo material** (horarios, precios, nombres de personas, URLs, servicios, zonas de cobertura, condiciones comerciales):
- Verificar que ese dato aparece **explícitamente** en el material adjunto o pegado por el usuario en **este request específico**
- Si un dato no puede rastrearse al material de este request → NO incluirlo; señalarlo así:
  `⚠️ Dato sin fuente en este request: "[dato]" — no aparece en el material adjunto. ¿Confirmás que corresponde a [NOMBRE_NEGOCIO]?`

**Por qué esto importa:** la conversación puede contener contexto de otros clientes trabajados en la misma sesión. Un dato "obvio" o "recordado" del contexto podría pertenecer a otro cliente. Solo el material explícitamente provisto en este request es fuente válida.

Este paso es **BLOQUEANTE**. No avanzar a A.2 sin haber completado la verificación.

### Paso A.2 — Analizar qué cambia

Identificar:
- Qué secciones del prompt se ven afectadas por la nueva información
- Qué información ya estaba cubierta (no duplicar)
- Qué agrega, corrige o reemplaza cada fragmento nuevo

### Paso A.3 — Generar lista de cambios

Antes de aplicar, presentar una lista indexada y simple de los cambios a realizar. Ejemplo:

```
1. Agregar producto X con precio y descripción en PRODUCTOS DISPONIBLES
2. Actualizar tono: reemplazar "che" por lenguaje más formal según instrucción del cliente
3. Agregar FAQ sobre envíos internacionales en FLUJO DE CONVERSACIÓN
```

Si los cambios son menores y obvios, se puede omitir este paso e ir directo a A.4.

### Paso A.4 — Versionar el prompt actual

Guardar el prompt actual como archivo versionado ANTES de modificarlo:

```
clients/[CLT###_Nombre]/04_agents/agente-[nombre]-system-prompt-v[VERSION_ACTUAL].md
```

La versión se extrae del historial de versiones dentro del archivo. Si no tiene, usar `v1.0`.

### Paso A.5 — Aplicar cambios al prompt

Reglas:
- **Modificar solo las secciones afectadas.** Lo que no cambió quede exactamente igual.
- No reescribir el prompt completo — solo los deltas.
- Actualizar el número de versión y agregar entrada en el historial de versiones.

Formato de la entrada en historial:
```
| v[X.Y] | [FECHA] | [Descripción concisa del cambio] |
```

### Paso A.6 — Guardar el prompt actualizado

Sobreescribir el archivo principal:
```
clients/[CLT###_Nombre]/04_agents/agente-[nombre]-system-prompt.md
```

Verificar el guardado con `ls -la` sobre `04_agents/` y confirmar que el timestamp del archivo es reciente. Si el archivo no aparece o no se actualizó, reintentar antes de continuar. Este paso es un **bloqueante** — no avanzar sin confirmar que el archivo fue guardado.

### Paso A.6b — Entregar el prompt en bloque de código

Extraer el contenido puro del prompt (sin el wrapper markdown del documento) y presentarlo en un bloque de código para que el usuario pueda copiarlo y pegarlo directamente en el nodo de IA de n8n.

⚠️ **CRÍTICO — wrapper de backticks:** Los system prompts frecuentemente contienen bloques ` ``` ` internos (plantillas de delegación, ejemplos de formato, etc.). Usar 3 backticks como wrapper externo los rompe. **Usar SIEMPRE 5 backticks (``````) como wrapper externo**, sin excepción:

`````````
`````
[CONTENIDO DEL PROMPT AQUÍ]
`````
`````````

### Paso A.7 — Generar o actualizar la guía de testing

Determinar si ya existe una guía de testing:
- `clients/[CLT###_Nombre]/07_testing/testing-guide-v[N].md`

**Si existe:** agregar nuevos casos al final que cubran específicamente los cambios recién integrados. No borrar casos anteriores. Actualizar el número de versión en el encabezado.

**Si no existe:** generar la guía completa usando el template en `_core/templates/agents/testing-guide-template.md`.

En ambos casos: los casos deben ser concretos y específicos al negocio — nunca genéricos.

Presentar la guía en bloque ```markdown``` para pegar directamente en Notion.

### Paso A.8 — Guardar la guía de testing

```
clients/[CLT###_Nombre]/07_testing/testing-guide-v[N].md
```

Si ya existía, incrementar el número (`v1` → `v2`, etc.).

### Paso A.8b — Testing automatizado iterativo

**Detección del modelo — fuente de verdad y confirmación obligatoria:**

1. Leer `clients/[CLT###_Nombre]/CLIENT_INFO.md` y buscar el campo "Modelo LLM". **Esta es la fuente primaria.**
2. Si no está en CLIENT_INFO.md, leer el workflow JSON del cliente (`03_workflows/`) y buscar el nodo de tipo `lmChat*` o `OpenAI Chat Model` para extraer el modelo.
3. **Nunca usar CLAUDE.md como fuente del modelo** — puede estar desactualizado si el workflow fue cambiado en n8n sin sincronizar el JSON.

**Antes de ejecutar el script, confirmar siempre con el usuario:**
```
Detecté el modelo: [MODELO]. ¿Es correcto? (Si el workflow fue actualizado en n8n sin exportar el JSON, indicame el modelo real.)
```
Esperar confirmación. Si el usuario corrige el modelo, usar el que indicó y actualizar el campo "Modelo LLM" en CLIENT_INFO.md.

Si el modelo confirmado **NO es OpenAI** (Gemini, Claude, Llama, etc.) → informar que auto-testing no está disponible para ese provider y saltar al siguiente paso.

**Verificar que OPENAI_API_KEY está disponible:**
```bash
source .env && python3 -c "import os; assert os.environ.get('OPENAI_API_KEY'), 'KEY no configurada'"
```
Si falla, indicar al usuario que agregue `OPENAI_API_KEY=sk-...` al `.env`.

---

#### Detección de fase del prompt (BLOQUEANTE antes del testing)

Los system prompts pasan por dos fases de desarrollo. Detectar cuál aplica leyendo el contenido del prompt:

**Fase 1 — Placeholders como output:**
El prompt instruye al agente a escribir el nombre de la herramienta como texto en su respuesta. Señales:
- Frases como "escribe `[NOMBRE_HERRAMIENTA]`", "envía el texto `[TOOL]`", "responde con `[ACCION]`"
- El prompt tiene un glosario o lista de "marcadores" / "etiquetas" que el agente debe outputear
- Las tools están documentadas como strings que el agente debe incluir en su mensaje

→ En Fase 1: testear directamente con el prompt tal como está. El agente producirá los placeholders como texto y el juez los evaluará normalmente.

**Fase 2 — Activación real de tools:**
El prompt instruye al agente a activar herramientas de n8n directamente (no como texto). Señales:
- Frases como "usa la herramienta X", "activa la tool Y", "ejecuta Z", "llama a la función"
- Las tools están listadas como capacidades del agente, no como strings a escribir
- No hay instrucciones de "escribir" o "enviar" el nombre de la herramienta como texto

→ En Fase 2: generar un **proxy de testing** antes de ejecutar el script (ver abajo).

---

#### Proxy de testing (solo Fase 2)

El objetivo es crear una versión temporal del prompt donde cada instrucción de activación real de tool se reemplaza por una instrucción equivalente de placeholder como texto. Esto permite testear el timing y condiciones de activación sin necesitar n8n.

**Paso proxy-1:** Leer el prompt e identificar todas las herramientas mencionadas y sus condiciones de activación. Ejemplo:
```
Original (Fase 2): "Cuando el usuario haya confirmado los datos, activa la herramienta `codigo_reposicion`"
Proxy:             "Cuando el usuario haya confirmado los datos, escribe exactamente el texto [CODIGO_REPOSICION]"
```

**Paso proxy-2:** Generar el prompt proxy aplicando la siguiente regla a cada instrucción de activación:
- Reemplazar "activa / usa / ejecuta / llama a [tool]" por "escribe exactamente el texto `[TOOL_EN_MAYUSCULAS]` en tu respuesta"
- Mantener idénticas todas las demás instrucciones (tono, flujo, reglas de negocio, condiciones)
- Agregar al inicio del prompt proxy: `[MODO TESTING — NO USAR EN PRODUCCIÓN]`

**Paso proxy-3:** Guardar el proxy en:
```
clients/[CLT###_Nombre]/04_agents/agente-[nombre]-system-prompt-test-proxy.md
```

**Paso proxy-4:** Actualizar los casos de la guía de testing que involucran tool calls. En los casos donde el "Resultado esperado" actualmente dice "activa la herramienta X" o describe el efecto de la tool, reemplazar por "el agente escribe `[TOOL_EN_MAYUSCULAS]` en su respuesta". Esto asegura que el juez evalúe correctamente el placeholder.

El archivo de la guía de testing NO se modifica permanentemente — los cambios de expected results para proxy solo se aplican internamente al ejecutar el test. La guía original se preserva.

---

#### Pre-procesamiento de variables n8n (ANTES de cada ejecución del script)

El script lee el system prompt raw. Las variables n8n como `{{ORIGEN}}` no son resueltas automáticamente. Si el prompt contiene variables n8n, crear un archivo temporal con los valores reemplazados antes de cada ejecución:

```bash
# Reemplazar {{ORIGEN}} con "directo" (valor estándar para testing)
sed 's/{{ORIGEN}}/directo/g' \
  "clients/[CLT###_Nombre]/04_agents/agente-[nombre]-system-prompt[-test-proxy].md" \
  > /tmp/prompt-testing-resolved.md
```

Usar `/tmp/prompt-testing-resolved.md` como argumento `--system-prompt` en todas las ejecuciones. No guardar este archivo en el repositorio — es temporal.

Si el prompt usa otras variables n8n (`{{NOMBRE_LEAD}}`, `{{FECHA}}`, etc.), agregar un reemplazo por cada una con un valor representativo de testing.

---

#### Validación dry-run (BLOQUEANTE antes del test real)

Antes de ejecutar el test real, correr siempre con `--dry-run` para verificar que el parser detectó los casos correctamente:

```bash
source .env && python3 scripts/testing/run-agent-tests.py \
  --system-prompt /tmp/prompt-testing-resolved.md \
  --testing-guide "clients/[CLT###_Nombre]/07_testing/testing-guide-v[N].md" \
  --model [model-id-exacto] \
  --dry-run
```

Leer el stdout. Debe reportar algo como:
```
  Casos simples: X (Y manual-only)
  Flujos: Z (W con turns manual-only)
```

**Si `Casos simples: 0` y `Flujos: 0` → STOP.** El formato de la guía es incompatible con el script. No ejecutar el test real. Reportar:
```
❌ Error de formato en la guía de testing: el parser no detectó ningún caso.
   Verificar que las tablas usan exactamente:
   - Casos simples: | # | Mensaje | Resultado esperado |
   - Flujos: | Turno | Rol | Mensaje | Resultado esperado |
   No agregar columnas extra (Área, Flujo, OK, {{ORIGEN}}).
```
Corregir la guía antes de continuar.

**Si detectó casos → reportar al usuario y proceder:**
```
✓ Guía parseada: [X] casos simples, [Y] flujos. Ejecutando testing...
```

---

#### Loop iterativo (máx. 3 iteraciones)

**Iteración 1:**
```bash
source .env && python3 scripts/testing/run-agent-tests.py \
  --system-prompt /tmp/prompt-testing-resolved.md \
  --testing-guide "clients/[CLT###_Nombre]/07_testing/testing-guide-v[N].md" \
  --model [model-id-exacto] \
  --output "clients/[CLT###_Nombre]/07_testing/testing-guide-v[N]"
```

El model-id debe ser el ID exacto de OpenAI tal como aparece en n8n (ej: `gpt-4.1-mini`, `gpt-4o`, `gpt-4.1`). Nunca usar el nombre de marketing.

Leer el resumen de stdout. Si todos los casos automatizables pasan (cero `false`, cero `parcial`) → ir a "Entrega final". Si hay fallos:

**Corrección automática (sin pedir confirmación al usuario):**
1. Analizar cada caso fallido usando la lógica del Paso B.2 (causa raíz: instrucción ausente / ambigua / condición de escape)
2. Generar lista de fixes
3. En Fase 1: aplicar los fixes directamente al prompt principal
4. En Fase 2: aplicar los fixes al prompt principal (Fase 2) Y regenerar el proxy para que refleje los mismos cambios
5. Guardar el prompt corregido (sobreescribir — no versionar las correcciones intermedias del loop)
6. Re-ejecutar el pre-procesamiento de variables → re-ejecutar dry-run → re-ejecutar test real → **Iteración 2**

**Iteración 2 y 3:** mismo ciclo.

---

#### Entrega final

**REGLA CRÍTICA — NO entregar si hay `false`:**
Si después de la iteración 3 siguen habiendo casos con `false`, **NO entregar el prompt**. Reportar:
```
⚠️ Testing incompleto: [N] casos con false/parcial después de 3 iteraciones.
   El prompt NO se entrega. Casos no resueltos:
   - [ID]: [reason]
   - [ID]: [reason]

   Opciones:
   1. Revisá el prompt manualmente y confirmá que querés entregarlo igual.
   2. Pedime que aplique más fixes y continúe el loop.
```
Esperar confirmación explícita del usuario antes de entregar.

**Si todos los casos automatizables pasan (cero `false`):**

→ Fase 1: entregar el prompt principal directamente en bloque de código.

→ Fase 2:
1. Eliminar el archivo proxy: `clients/[CLT###_Nombre]/04_agents/agente-[nombre]-system-prompt-test-proxy.md`
2. Entregar el **prompt principal de Fase 2** (con instrucciones de activación real), no el proxy
3. Hacer explícito: "Este es el prompt con activación real de tools. El proxy de testing fue eliminado."

En ambas fases: eliminar `/tmp/prompt-testing-resolved.md` si existe.

---

**Guía de testing manual (si hay casos manual-only):**
Si el script generó `testing-guide-v[N]-manual.md`, informar al usuario:
```
📋 Testing manual pendiente: [N] casos requieren verificación en n8n
   → Guía: clients/[CLT###_Nombre]/07_testing/testing-guide-v[N]-manual.md
   → Casos: #X ([TOOL_A]), #Y ([TOOL_B])
```

Los casos manual-only se detectan cuando el "Resultado esperado" contiene herramientas en formato `[NOMBRE_HERRAMIENTA]` (mayúsculas, guiones bajos). Para herramientas en otros formatos (ej: `'codigo_reposicion'` en comillas), agregarlas manualmente a la guía manual o convertir al formato `[CODIGO_REPOSICION]` en la guía de testing.

### Paso A.9 — Ejecutar cliente-sync

Ejecutar el skill `cliente-sync` para registrar los cambios.

---

## MODO B — Post-Testing

### Paso B.1 — Leer el contexto

Identificar el cliente: por nombre explícito, por contexto de la conversación, o por el archivo adjunto.
Si no es posible determinarlo, preguntar antes de continuar.

Leer siempre:
- La guía de testing con resultados: el archivo adjunto o pegado por el usuario
- El prompt actual (archivo principal, sin sufijo de versión): `clients/[CLT###_Nombre]/04_agents/agente-[nombre]-system-prompt.md`

El archivo principal es siempre la versión más reciente — no leer los archivos con sufijo de versión.

### Paso B.1c — Verificación de scope (BLOQUEANTE)

Inmediatamente después de identificar el cliente, antes de analizar los resultados:

**1. Leer `clients/[CLT###_Nombre]/CLIENT_INFO.md` y extraer:**
- Nombre del negocio, niche, servicios principales

**2. Declarar el scope activo en la respuesta al usuario:**
```
Scope activo: [NOMBRE_NEGOCIO] ([NICHE]) — [CLT###]
```

**3. Para cada corrección o dato nuevo derivado de los resultados de testing** (precios, horarios, nombres, URLs, servicios, flujos):
- Verificar que ese dato surge del comportamiento observado en el testing de **este cliente específico**
- Si una corrección introduce un dato que no estaba en el prompt original ni en el material de testing de este cliente → NO incluirlo; señalarlo:
  `⚠️ Dato sin origen verificado en este cliente: "[dato]". ¿Confirmás que corresponde a [NOMBRE_NEGOCIO]?`

Este paso es **BLOQUEANTE**. No avanzar a B.2 sin haber completado la verificación.

### Paso B.1b — Persistir resultados en la guía de testing

El archivo de resultados que el usuario provee (ej: `testing-guide-v4-results.md`) ES la guía de testing correspondiente con las columnas "Resultado obtenido" y "OK" completadas. Guardarlo sobre la guía existente:

```
clients/[CLT###_Nombre]/07_testing/testing-guide-v[N].md
```

Cómo identificar N: tomar el número de versión del nombre del archivo (ej: `testing-guide-v4-results.md` → N=4) o del encabezado "Versión: v[N]" si el nombre del archivo no lo indica.

**No crear un archivo paralelo con sufijo `-results`.** El archivo con resultados reemplaza la guía vacía. El historial git preserva la versión sin resultados si hace falta consultarla.

Verificar el guardado con `ls -la` sobre `07_testing/` antes de continuar.

### Paso B.2 — Analizar los resultados

Clasificar cada caso:
- **true** → sin acción requerida
- **false** → fallo a corregir (prioritario)
- **parcial** → comportamiento aproximado que puede mejorarse
- **Notas adicionales** → observaciones sistémicas que aplican a múltiples casos

Para cada fallo o parcial, identificar la causa raíz usando estas categorías:
- **Instrucción ausente** → la regla simplemente no existía
- **Instrucción ambigua** → la regla existía pero era insuficientemente específica
- **Condición de escape implícita** → la regla existía y era clara, pero el modelo encontró un escenario que interpretó como excepción válida porque no estaba explícitamente excluido (ej: "SIEMPRE audio al abrir" — el modelo consideró que una pregunta directa de precio era excepción válida)
- **Escenario no cubierto por testing** → la regla funcionaba en el caso canónico pero nunca fue testeada con el trigger real que causó el fallo

La categoría determina el tipo de fix correcto. Ausente → agregar. Ambigua → especificar, no solo enfatizar. Condición de escape → nombrar explícitamente los escenarios que parecen excepciones y no lo son. Escenario no cubierto → el fix va al prompt Y a la guía de testing.

### Paso B.3 — Determinar cambios necesarios

Generar lista indexada de cambios a aplicar. Ser preciso: indicar qué sección del prompt cambia y cómo.

Ejemplo:
```
1. [CRÍTICO] Etiquetas no se generan → reforzar instrucción como obligatoria con consecuencia explícita
2. [FALLO] Precio omitido en propuesta directa → agregar regla en Etapa 3: siempre incluir precio
3. [FALLO] Cierre sin decisión usa urgencia → nuevo caso en MANEJO DE OBJECIONES con instrucción explícita
4. [PARCIAL] Lead verde → Entrenamiento Gratuito demasiado rápido → agregar paso previo de exploración
5. [FORMATO] Mensajes no inician con mayúscula → agregar a FORMATO DE RESPUESTA
```

Presentar esta lista antes de aplicar los cambios.

Para cada fix de la lista, verificar internamente antes de presentarlo:
**"¿Esta instrucción cierra la condición de escape que causó el fallo?"**
- Si la causa fue ambigüedad: el fix debe ser más específico, no solo más enfático. Agregar "SIEMPRE" sin cerrar el escape no es suficiente.
- Si la causa fue condición de escape implícita: la instrucción debe nombrar explícitamente el escenario que el modelo interpretó como excepción. Ejemplo: "esto aplica incluso si el lead pregunta precio, información o cualquier otra cosa — el contenido del mensaje nunca es excepción".
- Si queda un escenario plausible donde el modelo podría ignorar la instrucción → reformular antes de incluirla en la lista.

### Paso B.4 — Versionar el prompt actual

Guardar el prompt actual como archivo versionado ANTES de modificarlo:

```
clients/[CLT###_Nombre]/04_agents/agente-[nombre]-system-prompt-v[VERSION_ACTUAL].md
```

### Paso B.5 — Aplicar cambios al prompt

Reglas:
- **Modificar solo las secciones afectadas.** Lo que no falló quede exactamente igual.
- Preferir instrucciones explícitas sobre instrucciones implícitas: si algo falló, ser más directo.
- Agregar ejemplos concretos cuando la ambigüedad fue la causa del fallo.
- Actualizar número de versión y agregar entrada en historial.

### Paso B.5b — Verificación pre-guardado

Antes de guardar, leer cada instrucción nueva o modificada y aplicar este filtro:
**"¿Hay un escenario plausible en el que un LLM ignore esta instrucción?"**

Señales de alerta:
- Dice "SIEMPRE X" pero no lista los casos que parecen excepciones y no lo son
- Es más enfática (más mayúsculas, más signos de exclamación) pero no más específica que antes del fallo
- La instrucción cubre el caso canónico que falló pero no las variantes del mismo trigger

Si alguna instrucción no pasa el filtro → cerrar el gap antes de continuar.

### Paso B.6 — Guardar el prompt actualizado

Sobreescribir el archivo principal:
```
clients/[CLT###_Nombre]/04_agents/agente-[nombre]-system-prompt.md
```

Verificar el guardado con `ls -la` sobre `04_agents/` y confirmar que el timestamp del archivo es reciente. Si el archivo no aparece o no se actualizó, reintentar antes de continuar. Este paso es un **bloqueante** — no avanzar sin confirmar que el archivo fue guardado.

### Paso B.6b — Entregar el prompt en bloque de código

Extraer el contenido puro del prompt (sin el wrapper markdown del documento) y presentarlo en un bloque de código para que el usuario pueda copiarlo y pegarlo directamente en el nodo de IA de n8n.

⚠️ **CRÍTICO — wrapper de backticks:** Los system prompts frecuentemente contienen bloques ` ``` ` internos (plantillas de delegación, ejemplos de formato, etc.). Usar 3 backticks como wrapper externo los rompe. **Usar SIEMPRE 5 backticks (``````) como wrapper externo**, sin excepción:

`````````
`````
[CONTENIDO DEL PROMPT AQUÍ]
`````
`````````

### Paso B.7 — Actualizar la guía de testing

Marcar en el archivo existente los casos corregidos. Agregar columna o nota al final:
```
**Correcciones aplicadas en v[X.Y]:** casos #N, #N, #N
```

Guardar como nueva versión:
```
clients/[CLT###_Nombre]/07_testing/testing-guide-v[N+1].md
```

Si hay casos que requieren re-testear, generar la tabla de re-test con solo esos casos.

Para cada regla nueva o modificada, incluir en la tabla de re-test no solo el caso que falló, sino 1-2 edge cases que prueben los límites de la regla — especialmente los escenarios identificados como "condición de escape" en B.2.

El "Resultado esperado" de reglas críticas debe incluir al menos un ítem negativo explícito:
- Correcto: "Envía `[AUDIO:X]`. NO responde al contenido del mensaje directamente. La frase Y NO aparece."
- Incorrecto: "Responde con el audio correcto."

Los ítems negativos explícitos le dicen al tester exactamente qué buscar para marcar `false` en lugar de `parcial`.

### Paso B.7b — Re-testing automatizado iterativo

Mismo loop que el Paso A.8b (incluyendo detección de fase + generación/eliminación de proxy), aplicado sobre la guía de re-test (`testing-guide-v[N+1].md`) generada en B.7.

El objetivo es validar que los fixes del prompt efectivamente corrigieron los fallos. Si siguen fallando, continuar iterando (máx. 3 iteraciones totales incluyendo las anteriores).

**Si el prompt es Fase 2:** si ya existe un proxy de una iteración anterior, actualizarlo para reflejar los cambios del prompt principal antes de re-testear. No reutilizar el proxy viejo.

El system prompt en bloque de código SOLO se entrega cuando todos los tests automatizables pasan (o se agotan las iteraciones). En Fase 2: siempre entregar el prompt principal (no el proxy) y eliminar el proxy al finalizar.

### Paso B.8 — Ejecutar cliente-sync

Ejecutar el skill `cliente-sync` para registrar los cambios.

---

## Convención de Versionado

| Tipo de cambio | Incremento |
|---|---|
| Correcciones post-testing, ajustes menores | Minor: v1.1 → v1.2 |
| Integración de nueva información significativa | Minor: v1.2 → v1.3 |
| Reestructuración mayor del prompt | Major: v1.x → v2.0 |

El archivo principal siempre se llama `agente-[nombre]-system-prompt.md` (sin sufijo de versión).
Los archivos versionados usan sufijo: `agente-[nombre]-system-prompt-v1.1.md`.

---

## Reglas del Skill

- **Auto-detectar el prompt actual.** El archivo principal es siempre `agente-[nombre]-system-prompt.md` (sin sufijo). Es la versión más reciente — nunca leer los archivos versionados con sufijo.
- **Siempre versionar antes de modificar.** Nunca sobreescribir sin guardar la versión anterior con sufijo (`-v1.2.md`).
- **Mínima intervención.** Solo tocar lo que cambia — el resto queda idéntico.
- **Lista de cambios antes de aplicar** (Modo B siempre; Modo A cuando los cambios son significativos).
- **Siempre guardar el prompt — es bloqueante.** El archivo principal debe quedar guardado en disco antes de entregar el bloque de código. Verificar con `ls -la` que el timestamp es reciente. Si el archivo no se guardó, reintentar antes de continuar.
- **Siempre entregar el prompt en bloque de código al finalizar** — el usuario lo copia y pega directamente en n8n. Extraer solo el contenido puro del prompt, sin el wrapper markdown del documento. En Fase 2: siempre entregar el prompt principal (nunca el proxy de testing).
- **Proxy de testing — regla crítica:** el archivo `*-test-proxy.md` es temporal. Siempre eliminarlo antes de entregar el prompt final. Nunca commitear ni entregar el proxy al usuario como prompt definitivo. El proxy solo existe para que el test runner pueda verificar el timing de activación de tools.
- **Guía de testing siempre actualizada** — si existe, ampliarla; si no, crearla.
- **Archivo de resultados reemplaza la guía** — cuando el usuario provee un archivo `testing-guide-vN-results.md`, ese archivo ES la guía `testing-guide-vN.md` con los datos completados. Guardarlo sobre la guía existente (ver paso B.1b). No crear archivos `-results` paralelos.
- **Bloques ```markdown```** para las guías de testing (para pegar en Notion).
- **No preguntar lo que ya está claro** en los archivos o en el mensaje del usuario.
- Si el cliente no está especificado y no puede inferirse, preguntar antes de continuar.
- Responder en español.
- **Sin información no provista — regla crítica.** Solo incorporar al prompt datos, precios, servicios, comportamientos o instrucciones que estén explícitamente presentes en el material aportado por el cliente (formulario, audios, documentos, mensajes). Nunca inferir ni completar con información propia aunque parezca razonable. Si algo no está en el material provisto, no va al prompt. Ante la duda, omitir y señalarlo al usuario.
- **Aislamiento de scope — regla crítica.** Cada invocación del skill opera sobre UN solo cliente. La conversación puede contener contexto de otros clientes trabajados previamente en la misma sesión; ese contexto es contaminación potencial. Regla operativa: un dato solo puede aplicarse al prompt del cliente activo si aparece explícitamente en el material de ESTE request. Horarios, precios, nombres, URLs, servicios — todo debe rastrearse al material adjunto/pegado ahora, no a memoria de la conversación. Ante cualquier dato no rastreable: omitir y preguntar (ver Paso A.1b / B.1c).
