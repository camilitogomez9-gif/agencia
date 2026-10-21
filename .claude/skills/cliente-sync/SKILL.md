---
name: cliente-sync
description: >
  Skill de sincronización automática basada en git. Se ejecuta al final de cualquier
  trabajo significativo sobre un cliente. Detecta exactamente qué archivos fueron
  creados o modificados usando git status, actualiza CLIENT_INFO.md y CLAUDE.md,
  hace commit, y reporta únicamente qué cambió. No hace preguntas — actúa y avisa.
  También se puede invocar manualmente con "/cliente-sync [XXX]" o "sincronizar X".
---

# Skill: Cliente Sync

## Descripción

Usa `git status` para detectar con precisión qué archivos cambiaron durante la sesión
de trabajo. Registra los outputs significativos en `CLIENT_INFO.md` y `CLAUDE.md`,
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

Filtrar los resultados para quedarse solo con archivos dentro de `clients/[XXX_Nombre]/`.

Los prefijos de git status significan:
- `??` → archivo nuevo (untracked)
- `M ` → modificado (staged)
- ` M` → modificado (unstaged)
- `A ` → agregado al index

### Paso 2.5 — Versionar archivos clave modificados

Antes de cualquier otra acción, para cada archivo que git reporta como **modificado** (prefijo ` M` o `M `, NO `??` que son nuevos):

**Criterios para versionar** (debe cumplir todos):
- Está dentro de un directorio clave: `03_workflows/`, `04_agents/`, `05_crm/`, `06_docs/`, `08_delivery/`
- Su nombre **NO** contiene ya `-v[0-9]` (para no versionar backups de backups)
- No es `CLIENT_INFO.md`

**Cómo crear el backup:**

```bash
# 1. Extraer carpeta, nombre base y extensión del archivo
#    Ej: clients/IMP_ImportadoresConectados/04_agents/system-prompt.md
#    → carpeta = clients/IMP_ImportadoresConectados/04_agents/
#    → base    = system-prompt
#    → ext     = .md

# 2. Contar backups existentes de ese archivo
ls [carpeta] | grep -c "^[base]-v[0-9]"

# 3. El nuevo backup es vN+1
#    Si hay 2 backups (-v1, -v2), crear -v3

# 4. Guardar la versión anterior (la que estaba en git antes de este cambio)
git show HEAD:[ruta-completa-desde-raiz] > [carpeta]/[base]-v[N+1].[ext]
```

**Ejemplo:**
- Archivo modificado: `clients/IMP_ImportadoresConectados/04_agents/system-prompt.md`
- Backups existentes: `system-prompt-v1.md`, `system-prompt-v2.md` → hay 2
- Backup a crear: `system-prompt-v3.md` con el contenido previo (`git show HEAD:...`)
- El archivo `system-prompt.md` queda con los nuevos cambios

**Si el archivo es nuevo** (`??`): No crear backup — es su primera versión.

**Agregar los backups al staging antes del commit** (en Paso 5 se incluirán automáticamente con `git add clients/...`).

**Reportar en el resumen** qué backups se crearon (en Paso 6, sección "Versionados").

---

### Paso 3 — Clasificar los archivos detectados

Para cada archivo cambiado dentro de la carpeta del cliente:

**Son archivos clave** (registrar en CLAUDE.md si no están ya):
- `03_workflows/*.json` → workflows n8n (excluir archivos `-vN` generados automáticamente por este skill)
- `04_agents/*.md` → system prompts / configuraciones de agente (excluir backups `-vN`)
- `05_crm/*.md` → esquemas CRM (excluir backups `-vN`)
- `06_docs/*` que contenga `brand-bible`, `manual`, `guia`, `runbook` en el nombre
- `08_delivery/*` → entregables finales
- Archivos con `-v[0-9]` en el nombre que fueron creados **manualmente** (no por este skill en esta misma sesión) → registrar como "Backup vN"

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

#### A. Actualizar "Archivos clave" en CLAUDE.md

Bajo la sección del cliente en CLAUDE.md, agregar solo los archivos que no estén ya listados:
```
- `[ruta desde clients/]` — [descripción inferida del nombre del archivo]
```

#### B. Actualizar CLIENT_INFO.md

Solo modificar campos con evidencia clara:
- `Status` si hay un cambio de fase evidente
- Stack: marcar `[x]` las herramientas detectadas activas en los archivos modificados

No tocar: OKRs, Notas críticas, Contactos clave.

#### C. Actualizar el tablero de estado (si el cliente lo tiene)

Si existe `clients/[XXX]/06_docs/estado/estado.json`, reflejar en ese JSON lo que avanzó en la sesión. Usar solo evidencia de los archivos modificados o de lo que se hizo; no inventar avance.
- `fases[].estado` (`cerrada` · `en_curso` · `bloqueada` · `lista` · `no_iniciada`), `progreso` (0-100) y `detalle`
- `bloqueos.nosotros` y `bloqueos.decisiones`: marcar `"hecho": true` lo resuelto y agregar lo nuevo
- `camino[]`: marcar `"hecho": true` los pasos cumplidos y ajustar las fechas si cambió el plan
- `cobros[]`: pasar a `"estado": "cobrado"` con `fecha` cuando haya evidencia de pago
- `pendiente_en`: `{"quien": "nosotros"|"cliente", "desde": "YYYY-MM-DD"}`, la fecha en que la pelota cambió de lado

**No cargar a mano** lo que el generador lee solo: los pendientes del cliente salen de los placeholders sin responder del documento de puntos de cierre, y los pacientes cargados salen de Airtable.

Después correr `python3 scripts/generators/estado-cliente.py --cliente [XXX]`. Los hooks de `.claude/settings.json` también lo regeneran solos al editar cualquier archivo del cliente y al final de cada turno.

### Paso 5 — Hacer commit

```bash
git add clients/[XXX_Nombre]/
git commit -m "sync([XXX]): [resumen de 1 línea de qué se trabajó]"
```

El mensaje de commit debe describir el trabajo realizado, no el proceso de sync.
Ejemplos:
- `sync(IMP): agrega workflow WhatsApp v2 y actualiza system prompt`
- `sync(SNR): registra esquema Airtable y brand bible`

Si hubo cambios en CLAUDE.md también, incluirlo en el commit:
```bash
git add clients/[XXX_Nombre]/ CLAUDE.md
git commit -m "sync([XXX]): [descripción]"
```

### Paso 6 — Reportar (única salida visible)

Emitir un bloque compacto:

```
✦ Sync [XXX] — [Nombre]  ([hash corto del commit])

Versionados:
  ↩ 04_agents/system-prompt.md → system-prompt-v3.md
  ↩ 03_workflows/flujo-main.json → flujo-main-v2.json

Registrado en CLAUDE.md:
  + 03_workflows/flujo-whatsapp-v2.json
  + 04_agents/system-prompt-v3.md

CLIENT_INFO.md actualizado:
  · Status: discovery → build
  · Stack: Airtable ✓

Commit: sync(IMP): agrega workflow WhatsApp v2 y actualiza system prompt
```

Si no hubo versionados (solo archivos nuevos), omitir la sección "Versionados".

Si no hubo archivos clave nuevos pero sí hubo cambios commiteados:
```
✦ Sync [XXX] — cambios commiteados, sin nuevos archivos clave para registrar.
Commit: sync(IMP): [descripción]
```

Si `git status` no muestra ningún cambio en la carpeta del cliente:
```
✦ Sync [XXX] — sin cambios detectados por git.
```

### Paso 7 — Ejecutar `/contexto-sync` automáticamente

**IMPORTANTE:** Después de completar los pasos 1–6, ejecutar automáticamente `/contexto-sync` para sincronizar el estado global del workspace con `contexto/`.

```
✦ Sync [XXX] — [Nombre] (completado)
...
[al terminar, ejecutar:]
/contexto-sync
```

`/contexto-sync` actualizará `contexto/datos-actuales.md` y `contexto/proyectos.md`, y hará commit. Esto asegura que el contexto global siempre refleje el estado actual, permitiendo que nuevas sesiones carguen contexto fresco sin necesidad de comandos iniciales.

---

## Reglas

- **La fuente de verdad es git** — solo se registra lo que git detecta como nuevo o modificado
- **No status a `live` automáticamente** — ese cambio requiere confirmación explícita del usuario
- **No sobreescribir** entradas existentes en CLAUDE.md — solo agregar las faltantes
- **Siempre hacer commit** si hay cambios — el historial git es el log de trabajo del cliente
- **Ejecutar `/contexto-sync` al final** — mantiene `contexto/` siempre fresco
- Responder en español
