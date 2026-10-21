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

## MODO A — Integrar Nueva Información

### Paso A.1 — Leer el contexto

Identificar el cliente: por nombre explícito, por contexto de la conversación, o por el archivo adjunto.
Si no es posible determinarlo, preguntar antes de continuar.

Leer siempre:
- El prompt actual (archivo principal, sin sufijo de versión): `clients/[CLT###_Nombre]/04_agents/agente-[nombre]-system-prompt.md`
- Todos los archivos o texto que el usuario adjuntó o pegó en el chat

El archivo principal es siempre la versión más reciente — no leer los archivos con sufijo de versión (`-v1.1.md`, etc.), esos son backups.

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

### Paso A.6b — Entregar el prompt en bloque de código

Extraer el contenido del bloque ` ``` ` dentro del archivo `.md` (el texto puro del prompt, sin el wrapper markdown del documento) y presentarlo en un bloque de código para que el usuario pueda copiarlo y pegarlo directamente en el nodo de IA de n8n:

````
```
[CONTENIDO DEL PROMPT AQUÍ]
```
````

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

### Paso B.2 — Analizar los resultados

Clasificar cada caso:
- **true** → sin acción requerida
- **false** → fallo a corregir (prioritario)
- **parcial** → comportamiento aproximado que puede mejorarse
- **Notas adicionales** → observaciones sistémicas que aplican a múltiples casos

Para cada fallo o parcial, identificar la causa raíz en el prompt: ¿instrucción ausente? ¿instrucción ambigua? ¿conflicto entre reglas?

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

### Paso B.6 — Guardar el prompt actualizado

Sobreescribir el archivo principal:
```
clients/[CLT###_Nombre]/04_agents/agente-[nombre]-system-prompt.md
```

### Paso B.6b — Entregar el prompt en bloque de código

Extraer el contenido del bloque ` ``` ` dentro del archivo `.md` (el texto puro del prompt, sin el wrapper markdown del documento) y presentarlo en un bloque de código para que el usuario pueda copiarlo y pegarlo directamente en el nodo de IA de n8n:

````
```
[CONTENIDO DEL PROMPT AQUÍ]
```
````

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
- **Siempre entregar el prompt en bloque de código al finalizar** — el usuario lo copia y pega directamente en n8n. Extraer solo el contenido puro del prompt, sin el wrapper markdown del documento.
- **Guía de testing siempre actualizada** — si existe, ampliarla; si no, crearla.
- **Bloques ```markdown```** para las guías de testing (para pegar en Notion).
- **No preguntar lo que ya está claro** en los archivos o en el mensaje del usuario.
- Si el cliente no está especificado y no puede inferirse, preguntar antes de continuar.
- Responder en español.
- **Sin información no provista — regla crítica.** Solo incorporar al prompt datos, precios, servicios, comportamientos o instrucciones que estén explícitamente presentes en el material aportado por el cliente (formulario, audios, documentos, mensajes). Nunca inferir ni completar con información propia aunque parezca razonable. Si algo no está en el material provisto, no va al prompt. Ante la duda, omitir y señalarlo al usuario.
