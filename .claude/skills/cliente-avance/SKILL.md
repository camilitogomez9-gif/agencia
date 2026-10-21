---
name: cliente-avance
description: >
  Usar este skill cuando el usuario quiera registrar progreso, actualizar archivos,
  o documentar cambios dentro de un cliente existente. Se activa con frases como
  "avancé en X", "actualizar cliente X", "registrar progreso", "terminé el workflow de X",
  "cambió el stack de X", "actualizar docs del cliente". Modifica archivos del cliente
  según la fase activa y mantiene CLIENT_INFO.md y CLAUDE.md al día.
---

# Skill: Cliente Avance

## Descripción

Registra cualquier avance, cambio o actualización dentro de un cliente existente.
Puede ser: completar una fase, agregar un workflow, actualizar el system prompt,
cambiar el stack, subir a producción, o cualquier modificación relevante.

---

## Proceso

### Paso 1 — Identificar el cliente

1. Si el usuario no especificó el cliente, listar `clients/` y preguntar
2. Leer `clients/[CLTXXX_Nombre]/CLIENT_INFO.md` para cargar contexto actual

### Paso 2 — Entender el avance

Preguntar o inferir del mensaje del usuario:

- **¿Qué se completó o cambió?** (workflow, agente, CRM, docs, testing, delivery)
- **¿En qué fase del ciclo cae?** (`01_discovery` → `08_delivery`)
- **¿Hay archivos que crear, editar o renombrar?**
- **¿Cambió el status del cliente?** (discovery → build → testing → live)
- **¿Hay variables de entorno, stack o contactos nuevos?**

### Paso 3 — Ejecutar los cambios

Según lo relevante, hacer una o más de las siguientes acciones:

#### A. Crear o editar archivo en la carpeta del cliente

Guardar en la subcarpeta correspondiente según la fase:

| Fase | Carpeta | Qué va ahí |
|------|---------|------------|
| Discovery | `01_discovery/` | Notas de reunión, transcripciones, brief |
| Arquitectura | `02_architecture/` | Diagramas, decisiones técnicas, ADRs |
| Workflows | `03_workflows/` | JSONs n8n, documentación de flujos |
| Agentes | `04_agents/` | System prompts, configuraciones de agente |
| CRM | `05_crm/` | Esquemas Airtable/Notion, scripts de CRM |
| Docs | `06_docs/` | Brand bible, manuales, guías de uso |
| Testing | `07_testing/` | Casos de prueba, bug reports, resultados QA |
| Delivery | `08_delivery/` | Entregables finales, handoff docs, credenciales |

Naming de archivos: usar kebab-case descriptivo con fecha si es un doc versionado.
Ej: `system-prompt-v2.md`, `flujo-whatsapp-leads-v1.json`, `brief-reunion-2026-04-11.md`

#### B. Actualizar CLIENT_INFO.md

Si cambió cualquiera de estos campos, actualizarlo:
- `Status` del proyecto
- Stack activo (marcar/desmarcar ítems)
- Contactos clave
- OKRs (si se refinaron o completaron)
- Notas críticas (agregar sin borrar las anteriores)

#### C. Actualizar CLAUDE.md

Si se creó un archivo clave (workflow de producción, system prompt definitivo, schema CRM):
- Agregarlo en la lista **"Archivos clave"** del cliente en CLAUDE.md
- Si cambió el stack, actualizarlo
- Si cambió la descripción del proyecto, actualizarla

#### D. Registrar en ops/ (opcional)

Si el avance corresponde a un hito operativo formal:
- Nuevo desarrollo iniciado → crear nota en `ops/02_desarrollos/`
- Mantenimiento aplicado → crear nota en `ops/03_mantenimientos/`

### Paso 4 — Sincronizar

Ejecutar el skill `cliente-sync` sobre el cliente trabajado. El sync reportará qué se registró.

---

## Reglas

- No borrar contenido previo de CLIENT_INFO.md al actualizar — solo modificar los campos que cambiaron
- Si el usuario pega contenido largo (un workflow, un prompt), guardarlo en el archivo correspondiente sin truncar
- Respetar el naming convention del workspace (kebab-case, sin espacios, con versión si aplica)
- Responder en español
