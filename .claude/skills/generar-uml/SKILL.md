---
name: generar-uml
description: >
  Generate UML documentation in Mermaid syntax for automation/AI projects, optimized
  for freelancer handoff. Use when: "generar UML", "documentar arquitectura",
  "crear diagramas del proyecto", "documentar para handoff", "UML de X cliente",
  "diagrama de componentes", "diagrama de secuencia", or when the user needs technical
  documentation for maintenance or transfer. Hybrid input: scans repo files
  (n8n workflows, system prompts, Airtable schemas, CLIENT_INFO) and interviews user
  for gaps. Outputs a single self-contained markdown with Mermaid diagrams.
---

# generar-uml

Genera documentación UML en Mermaid para proyectos de automatización/IA, optimizada para handoff a freelancers. Produce un documento único y autocontenido que permite a un tercero entender la arquitectura, los flujos y las dependencias del sistema sin necesidad del creador original.

**Siempre genera:** Componentes + Secuencia (los 2 diagramas críticos para handoff).
**Ofrece como opcionales:** Actividad, Estado, Despliegue.

---

## Fase 1 — Escaneo y Detección

### Paso 1.1 — Identificar el proyecto

Si el usuario no especifica un cliente o proyecto:
1. Listar directorios en `clients/` (excluyendo `_template`)
2. Preguntar cuál documentar

Si se especifica un cliente, buscar su directorio. Si no existe en `clients/`, preguntar si es un proyecto externo y pedir una descripción manual (saltar a Fase 2 modo manual).

### Paso 1.2 — Leer contexto base

Leer en este orden (detenerse si un archivo no existe):
1. `CLIENT_INFO.md` → stack, status, contactos, OKRs, notas críticas
2. La entrada del cliente en `CLAUDE.md` → archivos clave, pendientes, stack confirmado

### Paso 1.3 — Escanear archivos técnicos

Leer archivos en este orden de prioridad, extrayendo datos específicos:

| Fuente | Path pattern | Qué extraer |
|--------|-------------|-------------|
| Workflows n8n | `03_workflows/*.json` | Nodos, conexiones, webhooks, credenciales, notes, sticky notes |
| System prompts | `04_agents/*system-prompt*.md` (solo la versión más reciente, no backups) | Rol, tools, variables `{{VAR}}`, productos, etapas, reglas de escalamiento |
| Schemas CRM | `05_crm/*.md` | Tablas, campos, estados de pipeline, relaciones entre tablas |
| Arquitectura | `02_architecture/*.md` | Componentes, integraciones, decisiones de diseño |
| Docs existentes | `06_docs/*.md` | Notas de handoff, guías de implementación, contextos previos |
| Testing guides | `07_testing/*testing-guide*.md` (solo la más reciente) | Flujos de test = journeys reales del usuario |

**Extracción de workflow JSON (la más crítica):**

Para cada archivo `.json` en `03_workflows/`:
1. Parsear `nodes[]` — extraer: `name`, `type`, keys de `credentials`, `notes`, `parameters.path` (webhooks), `parameters.workflowId` (sub-workflows), `parameters.description` (tools)
2. Parsear `connections{}` — construir grafo dirigido de nodo a nodo
3. Clasificar nodos por tipo:
   - **Triggers**: `type` contiene `trigger` o `webhook`
   - **AI/Agent**: `type` contiene `langchain`
   - **Data stores**: `type` contiene `airtable`, `postgres`, `redis`, `googleSheets`, `notion`
   - **Messaging**: `type` contiene `telegram`, `slack`
   - **HTTP/Integraciones**: `type` es `httpRequest` (revisar URL destino)
   - **Lógica**: `type` contiene `if`, `switch`, `code`, `set`, `merge`
   - **Delays**: `type` contiene `wait` (extraer duración)
   - **Sub-workflows**: `type` es `executeWorkflow` o `toolWorkflow`
   - **Sticky notes**: `type` es `stickyNote` → leer `parameters.content` como documentación
4. Extraer tipos de credencial (keys del objeto `credentials` de cada nodo)

Si el JSON es inválido o malformado, logear y continuar con el siguiente archivo.

### Paso 1.4 — Presentar inventario al usuario

Antes de continuar, mostrar un inventario estructurado de lo detectado:

```
## Inventario Detectado

### Componentes Externos
- [lista de servicios encontrados vía credenciales: Airtable, Telegram, OpenAI, etc.]

### Workflows
- [nombre] (N nodos, trigger: webhook/cron/manual, AI: sí/no)
  - Sub-workflows: [lista si los hay]

### Agentes IA
- [nombre] (modelo: X, tools: [lista], memoria: tipo)

### Data Stores
- [tablas Airtable con cantidad de campos, estados de pipeline]
- [PostgreSQL/Redis si detectados]

### Canales de Comunicación
- [WhatsApp, Instagram DM, Facebook, Telegram, etc.]
```

Esperar confirmación del usuario antes de continuar.

---

## Fase 2 — Entrevista para Gaps

Preguntar en batches de 3-4 preguntas máximo por mensaje.

### Preguntas obligatorias (si no se encontró en archivos):

1. **"¿Cuál es el journey principal del usuario?"** (ej. "lead escribe por IG → agente responde → califica → cierra venta")
   — Necesario para diagrama de Secuencia.
   — Saltear si los testing guides documentan flujos claros.

2. **"¿Hay servicios externos no capturados en los workflows?"** (ej. pasarelas de pago, calendarios, CRMs externos)
   — Necesario para diagrama de Componentes.
   — Saltear si CLIENT_INFO.md tiene stack completo.

3. **"¿Quién monitorea/mantiene este sistema? ¿Cómo es su interacción diaria?"**
   — Necesario para contexto de handoff.
   — Saltear si hay docs de handoff en `06_docs/`.

### Preguntas para diagramas opcionales:

4. **"¿Cuáles son los estados posibles de un lead/entidad?"** → para Estado
   — Saltear si el schema Airtable tiene campo Single select con estados.

5. **"¿Dónde corre n8n? ¿Dónde están las bases de datos?"** → para Despliegue
   — Saltear si CLIENT_INFO.md especifica infraestructura.

6. **"¿Hay workflows con schedule/cron o intervenciones manuales periódicas?"** → para Actividad
   — Saltear si ya se detectaron cron triggers en los JSON.

### Confirmar alcance

Después de las preguntas, confirmar:
> "Voy a generar **Componentes + Secuencia**. Basándome en lo que encontré, también puedo generar [Actividad/Estado/Despliegue — los que apliquen]. ¿Querés alguno de estos adicionales?"

### Modo manual (sin archivos de proyecto)

Si no hay archivos o el proyecto es externo:
1. Preguntar: ¿Qué hace el sistema? ¿Para quién?
2. Preguntar: ¿Qué servicios/herramientas usa? (listar stack)
3. Preguntar: ¿Cuál es el flujo principal? (paso a paso)
4. Preguntar: ¿Qué datos maneja y dónde se guardan?
5. Proceder a Fase 3 con la información recopilada

---

## Fase 3 — Generación de Diagramas

**Antes de generar, leer `references/mermaid-uml-specs.md`** para sintaxis, patrones y buenas prácticas.

### Reglas generales

- Máximo 15-20 nodos por diagrama
- Labels en español, 3-5 palabras máximo
- Mermaid válido que renderice en GitHub, Notion y Claude
- Agrupar componentes relacionados con `subgraph`
- Comentarios `%% explicación` para ayudar al freelancer a leer el código Mermaid
- Nombrar por función, no por herramienta ("Buffer de mensajes" no "Redis Wait_35")
- Incluir tipo de credencial en tablas (nunca valores/tokens)
- Incluir timing si hay delays o seguimientos automáticos
- Si un workflow tiene >20 nodos, colapsar lógica interna en una arista etiquetada

### Diagrama 1: Componentes (obligatorio)

**Pregunta que responde:** "¿Qué piezas tiene este sistema y cómo se conectan?"

- Tipo Mermaid: `graph LR`
- Subgraphs por rol: Canales de Entrada, Motor de IA, Almacenamiento, Canales de Salida, Servicios Externos
- Un nodo por: servicio externo, workflow principal, AI agent, data store
- Sub-workflows como nodos dentro del subgraph del workflow padre
- Aristas etiquetadas con tipo de conexión ("webhook", "API REST", "tool call", "local")

### Diagrama 2: Secuencia (obligatorio)

**Pregunta que responde:** "¿Cómo fluye un request típico por el sistema?"

- Tipo Mermaid: `sequenceDiagram`
- Participants: Lead/Usuario, canal de entrada, n8n, AI Agent, cada data store relevante, equipo humano
- Mostrar el happy path del journey más común
- `alt`/`else` para bifurcaciones clave (lead nuevo vs. existente, evento crítico vs. normal)
- `loop` para patrones de reintento o seguimiento
- `Note over` para contexto (timing, condiciones, datos)
- Si hay múltiples journeys (ej. agente principal + seguimientos + reportes), generar UN diagrama de secuencia por cada uno

### Diagrama 3: Actividad (opcional)

**Pregunta que responde:** "¿Qué decisiones toma el sistema?"

- Tipo Mermaid: `flowchart TD`
- Nodos de decisión `{}` para cada bifurcación de negocio
- Nodos de acción `[]` para cada paso
- Inicio/fin con `([])`
- Máximo 2 niveles de profundidad en bifurcaciones

Generar cuando: hay lógica compleja de routing, múltiples ramas condicionales, o el usuario lo pide.

### Diagrama 4: Estado (opcional)

**Pregunta que responde:** "¿Qué estados puede tener un lead/entidad?"

- Tipo Mermaid: `stateDiagram-v2`
- Estados extraídos de: campos Single select en Airtable, etapas en system prompts, flujos de testing
- Transiciones etiquetadas con el evento que las causa
- `note right of X` para indicar qué actor opera en ese estado (agente vs. humano vs. automático)

Generar cuando: hay un pipeline claro (ventas, tickets, pedidos) con estados definidos.

### Diagrama 5: Despliegue (opcional)

**Pregunta que responde:** "¿Dónde corre cada pieza del sistema?"

- Tipo Mermaid: `graph TB`
- Subgraphs por capa: infraestructura propia (VPS/cloud), SaaS, plataformas (Meta, Google), notificaciones
- Aristas etiquetadas con protocolo ("API REST", "webhook", "SMTP", "local")

Generar cuando: el proyecto tiene infra propia (VPS, DB self-hosted) o el freelancer necesita configurar el entorno.

---

## Fase 4 — Output

### Paso 4.1 — Ensamblar documento

Crear un único archivo markdown con esta estructura:

```markdown
# Documentación UML — [Nombre del Cliente]

> Generado: [YYYY-MM-DD] | Proyecto: [descripción breve del OKR/propósito]
> Stack: [lista separada por comas]

---

## Referencia Rápida para el Freelancer

### Qué es este sistema
[2-3 oraciones: qué hace la automatización, para quién, qué problema resuelve]

### Stack tecnológico
| Servicio | Función | Credencial requerida |
|----------|---------|---------------------|
| [nombre] | [qué hace en el sistema] | [tipo de credencial] |

### Workflows activos
| Workflow | Trigger | Función principal |
|----------|---------|-------------------|
| [nombre] | [webhook/cron/manual] | [qué hace] |

### Contactos
| Nombre | Rol | Contacto |
|--------|-----|----------|
| [nombre] | [rol] | [email/tel] |

---

## Diagrama de Componentes

[1-2 oraciones explicando qué muestra este diagrama]

```mermaid
[diagrama]
```

### Notas del diagrama
- [puntos no obvios sobre conexiones, servicios, dependencias]

---

## Diagrama de Secuencia — [Nombre del Journey]

[1-2 oraciones: "Muestra el flujo cuando un lead envía un mensaje por [canal]"]

```mermaid
[diagrama]
```

### Notas del diagrama
- [timing, manejo de errores, edge cases]

---

[Diagramas opcionales siguen el mismo patrón: título, explicación, mermaid, notas]

---

## Glosario Técnico

| Término | Significado |
|---------|-------------|
| [término específico del proyecto] | [definición para el freelancer] |

## Archivos Clave del Proyecto

| Archivo | Qué contiene | Ruta |
|---------|-------------|------|
| [nombre] | [descripción] | [ruta relativa] |
```

### Paso 4.2 — Guardar

Guardar en: `clients/[XXX_Name]/06_docs/uml-handoff-YYYY-MM-DD.md`

Si ya existe un `uml-handoff-*.md` previo, mencionar la versión anterior en el header del nuevo archivo.

Si el proyecto es externo (sin directorio en `clients/`), guardar en `salidas/uml/` o donde indique el usuario.

### Paso 4.3 — Confirmar y ofrecer siguiente paso

Mostrar resumen de lo generado (qué diagramas, cuántos nodos cada uno, path del archivo).

Ofrecer:
- "¿Querés que ejecute `/cliente-sync` para hacer commit?"
- "¿Querés generar algún diagrama adicional (Actividad/Estado/Despliegue)?"

---

## Reglas

- Responder siempre en español
- Nunca inventar información no encontrada en archivos o confirmada por el usuario
- Si el cliente tiene muy pocos archivos técnicos, decirlo explícitamente y sugerir documentar antes de generar UML
- Siempre mostrar el inventario (Paso 1.4) y esperar confirmación antes de generar
- Valores de credenciales nunca incluidos — solo tipos/nombres
- El documento de output debe ser autocontenido: un freelancer debe poder entender el proyecto leyendo solo este archivo
- No leer backups de system prompts (archivos con `-v1.X.md` en el nombre) — solo la versión vigente
- Si el workflow JSON es demasiado grande para parsear completo, enfocarse en: triggers, nodos AI, data stores y sub-workflows
