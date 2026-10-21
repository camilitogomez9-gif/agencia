---
name: cliente-sync
description: >
  Skill de sincronización automática basada en git. Se ejecuta al final de cualquier
  trabajo significativo sobre un cliente. Detecta exactamente qué archivos fueron
  creados o modificados usando git status, actualiza CLIENT_INFO.md y AGENTS.md,
  hace commit, y reporta únicamente qué cambió. No hace preguntas — actúa y avisa.
  También se puede invocar manualmente con "/cliente-sync [CLTXXX]" o "sincronizar X".
---

# Skill: Cliente Sync

## Descripción

Usa `git status` para detectar con precisión qué archivos cambiaron durante la sesión
de trabajo. Registra los outputs significativos en `CLIENT_INFO.md` y `AGENTS.md`,
hace un commit con los cambios, y reporta un resumen compacto. Sin ambigüedad, sin
dependencia de memoria de sesión.

---

## Proceso

### Paso 1 — Identificar el cliente

Usar el cliente que se estaba trabajando en el contexto actual.
Si se invoca manualmente sin contexto, listar `clients/` y preguntar.

### Paso 2 — Detectar cambios con git

Ejecutar:
```bash
git status --porcelain
```

Filtrar los resultados para quedarse solo con archivos dentro de `clients/[CLTXXX_Nombre]/`.

Los prefijos de git status significan:
- `??` → archivo nuevo (untracked)
- `M ` → modificado (staged)
- ` M` → modificado (unstaged)
- `A ` → agregado al index

### Paso 3 — Clasificar los archivos detectados

Para cada archivo cambiado dentro de la carpeta del cliente:

**Son archivos clave** (registrar en AGENTS.md si no están ya):
- `03_workflows/*.json` → workflows n8n
- `04_agents/*.md` → system prompts / configuraciones de agente
- `05_crm/*.md` → esquemas CRM
- `06_docs/*` que contenga `brand-bible`, `manual`, `guia`, `runbook` en el nombre
- `08_delivery/*` → entregables finales
- Cualquier archivo con `v[0-9]` en el nombre → versión explícita

**Son cambios de estado** (actualizar CLIENT_INFO.md):
- Nueva carpeta con contenido en `03_workflows/` o `04_agents/` + status era `discovery` → actualizar a `build`
- Archivos en `07_testing/` → considerar `testing`
- Archivos en `08_delivery/` → considerar `live` (solo si hay varios entregables)
- Referencias a herramientas no marcadas en el stack → marcar como activo

**Ignorar para el registro**:
- `CLIENT_INFO.md` en sí mismo
- `01_discovery/*` → notas internas, no outputs
- `07_testing/*` → QA interno
- Archivos `.gitkeep`

### Paso 4 — Ejecutar actualizaciones silenciosas

#### A. Actualizar "Archivos clave" en AGENTS.md

Bajo la sección del cliente en AGENTS.md, agregar solo los archivos que no estén ya listados:
```
- `[ruta desde clients/]` — [descripción inferida del nombre del archivo]
```

#### B. Actualizar CLIENT_INFO.md

Solo modificar campos con evidencia clara:
- `Status` si hay un cambio de fase evidente
- Stack: marcar `[x]` las herramientas detectadas activas en los archivos modificados

No tocar: OKRs, Notas críticas, Contactos clave.

### Paso 5 — Hacer commit

```bash
git add clients/[CLTXXX_Nombre]/
git commit -m "sync([CLTXXX]): [resumen de 1 línea de qué se trabajó]"
```

El mensaje de commit debe describir el trabajo realizado, no el proceso de sync.
Ejemplos:
- `sync(IMP): agrega workflow WhatsApp v2 y actualiza system prompt`
- `sync(SNR): registra esquema Airtable y brand bible`

Si hubo cambios en AGENTS.md también, incluirlo en el commit:
```bash
git add clients/[CLTXXX_Nombre]/ AGENTS.md
git commit -m "sync([CLTXXX]): [descripción]"
```

### Paso 6 — Reportar (única salida visible)

Emitir un bloque compacto:

```
✦ Sync [XXX] — [Nombre]  ([hash corto del commit])

Registrado en AGENTS.md:
  + 03_workflows/flujo-whatsapp-v2.json
  + 04_agents/system-prompt-v3.md

CLIENT_INFO.md actualizado:
  · Status: discovery → build
  · Stack: Airtable ✓

Commit: sync(IMP): agrega workflow WhatsApp v2 y actualiza system prompt
```

Si no hubo archivos clave nuevos pero sí hubo cambios commiteados:
```
✦ Sync [XXX] — cambios commiteados, sin nuevos archivos clave para registrar.
Commit: sync(IMP): [descripción]
```

Si `git status` no muestra ningún cambio en la carpeta del cliente:
```
✦ Sync [XXX] — sin cambios detectados por git.
```

---

## Reglas

- **La fuente de verdad es git** — solo se registra lo que git detecta como nuevo o modificado
- **No status a `live` automáticamente** — ese cambio requiere confirmación explícita del usuario
- **No sobreescribir** entradas existentes en AGENTS.md — solo agregar las faltantes
- **Siempre hacer commit** si hay cambios — el historial git es el log de trabajo del cliente
- Responder en español
