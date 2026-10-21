---
name: versionar
description: >
  Usar este skill cuando el alumno quiera guardar una nueva versión de un workflow de n8n
  (.json) o de un system prompt de un agente (.md), preservando la versión anterior como
  backup. Se activa con frases como "versioná este flujo", "guardá esta versión",
  "actualizá la última versión del prompt", "actualizá el flujo con esto", "guardá el
  workflow", "creá un backup antes de cambiar esto", o cuando el alumno pega/adjunta un JSON
  de workflow o un system prompt actualizado y pide guardarlo en la carpeta del cliente.
  Mantiene el archivo principal (sin sufijo) como la última versión y congela la anterior
  como -vN. Simple, no depende de git.
---

# Skill: Versionar

## Qué hace

Guarda una nueva versión de un **workflow de n8n** (`.json`) o de un **system prompt** (`.md`)
sin perder la versión anterior. La convención es la misma que usamos en toda la agencia:

- **El archivo principal NO tiene sufijo de versión** → siempre contiene la **última** versión.
  - Ej: `agente-collazo-system-prompt.md`, `agente-collazo-main.json`
- **Los backups llevan sufijo `-vN`** → son versiones **congeladas** que no se vuelven a tocar.
  - Ej: `agente-collazo-system-prompt-v1.md`, `-v2.md`, `-v3.md`

Así, si algo sale mal, se vuelve atrás copiando un backup sobre el principal. Es la red de
seguridad: **nunca sobreescribas sin guardar antes la versión que funcionaba.**

---

## Dónde viven los archivos

Dentro de la carpeta del cliente:

- Workflows de n8n → `clients/[XXX]_Nombre/03_workflows/`
- System prompts de agentes → `clients/[XXX]_Nombre/04_agents/`

---

## Procedimiento

Cuando el alumno pide guardar una versión nueva (trae el JSON/prompt actualizado, o pidió
un cambio sobre un archivo existente):

### Paso 1 — Identificar el archivo principal
Ubicar el archivo **sin sufijo `-vN`** que corresponde al flujo o prompt en cuestión.
- Si el alumno lo nombra ("el flujo principal de Collazo", "el prompt del agente B2B"), usar ese.
- El archivo principal es SIEMPRE el que **no** tiene sufijo de versión. Los `-v1`, `-v2`, etc.
  son backups: **no los leas ni los edites** salvo para hacer un rollback.

### Paso 2 — Calcular el número de la nueva versión
Contar los backups `-vN` que ya existen para ese archivo y tomar el siguiente entero:

```bash
# Contar backups existentes (ajustar carpeta y nombre base)
ls clients/[XXX]_Nombre/04_agents/ | grep -cE "^agente-nombre-system-prompt-v[0-9]"
# Si hay 3 backups (-v1, -v2, -v3), el nuevo backup será -v4
```

Esquema **entero simple**: `v1 → v2 → v3 …`. No usar decimales (v1.1, v1.2) — mantenerlo simple.

### Paso 3 — Congelar la versión anterior
Copiar el **contenido actual** del archivo principal (lo que había ANTES de este cambio) a un
nuevo backup `-vN`:

```
clients/[XXX]_Nombre/04_agents/agente-nombre-system-prompt-v[N].md   ← contenido viejo (backup)
clients/[XXX]_Nombre/04_agents/agente-nombre-system-prompt.md        ← contenido nuevo
```

### Paso 4 — Escribir la versión nueva en el principal
Guardar el contenido actualizado en el archivo principal (sin sufijo).

### Paso 5 — Reportar
Avisar en una línea:
> "Guardé la versión anterior como `-v[N]` (backup). El archivo principal `[nombre]` ahora tiene
> la versión nueva. Si algo falla, se vuelve atrás copiando el `-v[N]` sobre el principal."

---

## Regla anti-duplicado (importante)

Cuando el alumno itera **varias veces sobre el mismo archivo en una misma sesión** (probar,
ajustar, volver a probar), **NO** crear un backup nuevo por cada cambio pequeño — se llena la
carpeta de versiones basura (v20, v21, v22, v23…).

Criterio por defecto:
- **Editar la última versión** (sobreescribir el principal sin nuevo backup) mientras son ajustes
  de la misma iteración.
- **Crear un backup `-vN` nuevo solo cuando** el alumno dice explícitamente "esta pasa a
  producción", "bumpeá la versión", "guardá esta como versión nueva", o cuando ya pegó el cambio
  en n8n y lo confirmó como estable.

Si hay ambigüedad, preguntar: **"¿Bumpeo a una versión nueva (backup) o edito la última?"**

---

## Rollback (volver atrás)

Si el alumno pide "volvé a la versión anterior" / "restaurá la v2":
1. Copiar el contenido del backup `-vN` pedido sobre el archivo principal (sin sufijo).
2. Avisar qué versión quedó activa.
3. (Opcional) el archivo principal previo puede guardarse como el próximo `-v(N+1)` si se quiere
   conservar el intento fallido para diagnóstico.

---

## Notas

- **No depende de git.** Funciona solo con lectura/escritura de archivos, así que sirve aunque el
  alumno no tenga git configurado.
- Sirve igual para `.json` (workflows) y `.md` (system prompts) — el procedimiento es el mismo.
- Después de versionar un workflow, recordá que el archivo y lo que corre en n8n **viven en
  paralelo**: guardar la versión en la carpeta NO lo aplica en n8n (y viceversa). La
  sincronización es manual (copiar/pegar el nodo o el flujo). Ver la guía del alumno.
