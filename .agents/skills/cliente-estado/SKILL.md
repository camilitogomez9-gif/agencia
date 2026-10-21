---
name: cliente-estado
description: >
  Usar este skill cuando el usuario quiera obtener un resumen actualizado del estado de
  un cliente. Se activa con frases como "dame el estado de X", "revisar cliente X",
  "qué tenemos con X", "status de X", "briefing de X", "cómo está X". Lee todos los
  archivos relevantes del cliente y genera un briefing completo y accionable.
---

# Skill: Cliente Estado

## Descripción

Genera un briefing completo y actualizado del estado de un cliente específico.
Lee los archivos existentes del cliente y produce un resumen estructurado con
contexto, progreso, archivos clave, pendientes y próximos pasos sugeridos.

---

## Proceso

### Paso 1 — Identificar el cliente

Si no se especificó, listar `clients/` y preguntar cuál.

### Paso 2 — Leer todos los archivos del cliente

Leer en este orden:

1. `clients/[CLTXXX_Nombre]/CLIENT_INFO.md` — datos base, status, stack
2. Listar todas las subcarpetas y sus archivos (`01_discovery/` → `08_delivery/`)
3. Leer los archivos más relevantes o recientes de cada carpeta que tenga contenido
4. Revisar si hay entradas en `ops/04_upsells/` para este cliente
5. Revisar si hay entradas en `ops/02_desarrollos/` o `ops/03_mantenimientos/`

### Paso 3 — Revisar en AGENTS.md

Leer la sección del cliente en AGENTS.md para capturar cualquier info registrada ahí
(stack, variables de entorno, archivos clave documentados).

### Paso 4 — Generar el briefing

Producir un briefing en este formato:

---

## Estado del Cliente: [Nombre] (CLT[NNN])

### Resumen ejecutivo
[2-3 oraciones: qué solución tienen, en qué fase están, qué está pasando actualmente]

### Datos generales
| Campo | Valor |
|-------|-------|
| Status | [status] |
| Niche | [niche] |
| Fecha inicio | [fecha] |
| Stack activo | [lista de herramientas] |

### Progreso por fase

| Fase | Estado | Qué hay |
|------|--------|---------|
| 01 Discovery | ✅ / 🔄 / ⬜ | [resumen o "vacío"] |
| 02 Architecture | ✅ / 🔄 / ⬜ | [resumen o "vacío"] |
| 03 Workflows | ✅ / 🔄 / ⬜ | [resumen o "vacío"] |
| 04 Agents | ✅ / 🔄 / ⬜ | [resumen o "vacío"] |
| 05 CRM | ✅ / 🔄 / ⬜ | [resumen o "vacío"] |
| 06 Docs | ✅ / 🔄 / ⬜ | [resumen o "vacío"] |
| 07 Testing | ✅ / 🔄 / ⬜ | [resumen o "vacío"] |
| 08 Delivery | ✅ / 🔄 / ⬜ | [resumen o "vacío"] |

Leyenda: ✅ Completo | 🔄 En progreso | ⬜ Sin iniciar

### Archivos clave
[Listar los archivos más importantes encontrados, con rutas relativas]

### Upsells activos
[Si hay documentos en ops/04_upsells/ para este cliente, listarlos con su estado]
[Si no hay ninguno: "Sin upsells registrados"]

### OKRs
[Copiar los OKRs de CLIENT_INFO.md con indicación de si se avanzó o no]

### Pendientes y próximos pasos sugeridos
[Inferir de los archivos qué falta completar, qué está bloqueado, qué debería ser lo próximo]

### Notas críticas
[Copiar notas críticas de CLIENT_INFO.md y cualquier info relevante encontrada]

---

### Paso 5 — Ofrecer acciones

Al final del briefing, preguntar al usuario si quiere:
- Registrar un avance (`/cliente-avance`)
- Documentar un upsell (`/cliente-upsell`)
- Crear un plan de trabajo (`/crear-plan`)

---

## Reglas

- No inventar información que no esté en los archivos — si algo no está documentado, decir "no documentado"
- Si el cliente tiene muy poco contenido, indicarlo claramente y sugerir completar la documentación
- El briefing debe ser útil para retomar el trabajo en cualquier momento, sin necesidad de abrir archivos
- Responder en español
