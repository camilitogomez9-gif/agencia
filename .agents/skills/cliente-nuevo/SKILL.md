---
name: cliente-nuevo
description: >
  Usar este skill cuando el usuario quiera crear un nuevo cliente en el workspace.
  Se activa con frases como "crear cliente", "nuevo cliente", "onboarding cliente X",
  o cuando se provee info de un cliente nuevo para registrar. Crea la estructura de
  carpetas desde _template, completa CLIENT_INFO.md, y actualiza AGENTS.md.
---

# Skill: Cliente Nuevo

## Descripción

Crea la estructura completa de un nuevo cliente en `clients/`, basándose en `clients/_template/`.
Completa `CLIENT_INFO.md` con los datos provistos y registra el cliente en la sección
"Clientes Activos" de AGENTS.md.

---

## Proceso

### Paso 1 — Recopilar datos

Si el usuario no los proveyó, preguntar:

- **Nombre del cliente / empresa**
- **Niche**: dental | real-estate | agency | automotive | generic
- **Status inicial**: discovery | build | testing | live
- **Descripción en una línea** de qué solución se está construyendo
- **Stack** que se usará (n8n, Airtable, WhatsApp, etc.)
- **Contacto decisor** (nombre + contacto si está disponible)

### Paso 2 — Determinar el ID del cliente

1. Listar `clients/` para ver los IDs existentes (`IMP`, `SNR`, etc.)
2. El ID debe ser provisto por el usuario — no se auto-genera. Verificar que no esté en uso en `clients/REGISTRY.md`
3. El nombre de carpeta sigue el formato: `[XXX]_[NombreSinEspacios]`

### Paso 3 — Crear la estructura

1. Copiar recursivamente `clients/_template/` a `clients/[XXX]_[Nombre]/`
2. Los subdirectorios a crear son:
   - `01_discovery/`
   - `02_architecture/`
   - `03_workflows/`
   - `04_agents/`
   - `05_crm/`
   - `06_docs/`
   - `07_testing/`
   - `08_delivery/`

### Paso 4 — Completar CLIENT_INFO.md

Escribir el archivo `clients/[XXX]_[Nombre]/CLIENT_INFO.md` con todos los datos recopilados.
Usar este template:

```markdown
# [XXX] — [Nombre Cliente]

## Datos generales
- ID: [XXX]
- Nombre: [Nombre]
- Niche: [niche]
- Fecha inicio: [YYYY-MM-DD]
- Status: [status]

## Stack activo
- [x] n8n          ← marcar solo los confirmados
- [ ] Airtable
- [ ] Clientify
- [ ] Google Sheets
- [ ] WhatsApp
- [ ] Notion

## Contactos clave
| Rol | Nombre | Contacto |
|-----|--------|---------|
| Decisor | [nombre] | [contacto] |
| Técnico | | |

## OKRs del proyecto
1. [OKR principal]
2.
3.

## Notas críticas
[cualquier restricción, contexto especial, o acuerdo relevante]
```

### Paso 5 — Actualizar AGENTS.md

Agregar una entrada en la sección **"Clientes Activos"** de `AGENTS.md` siguiendo el formato
de los clientes existentes:

```markdown
### [XXX] — [Nombre] (`clients/[XXX]_[Nombre]/`)

[Descripción de una línea de la solución.]

**Stack:** [stack activo]

**Archivos clave:**
- (completar a medida que se crean)
```

### Paso 6 — Sincronizar

Ejecutar el skill `cliente-sync` sobre el cliente recién creado para registrar el estado inicial.

---

## Reglas

- Nunca reutilizar un ID ya existente
- Si faltan datos críticos (nombre, niche), preguntar antes de crear
- No crear archivos dentro de las subcarpetas — solo la estructura vacía
- Responder en español
