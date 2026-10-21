---
name: sync-status-cliente-3-docs
description: >
  Usar este skill cuando hay que actualizar el status de un cliente en los 3 docs
  canónicos a la vez (CLIENT_INFO.md del cliente + CLAUDE.md raíz + contexto/datos-actuales.md).
  Se activa con frases como "actualizar status de X", "sincronizar 3 docs de X",
  "marcar avance en F5 de X en todos lados", "marcar X como GO-LIVE". Diferente
  a `cliente-sync` (git-based): este es para cambios de status puntuales sin
  esperar commit, garantizando consistencia entre los 3 lugares.
---

# Skill: Sync Status Cliente en 3 Docs Canónicos

## Descripción

Actualiza el status/avance de un cliente en los 3 docs canónicos de manera coherente:

1. **`clients/{XXX}_{Nombre}/CLIENT_INFO.md`** — ficha del cliente
2. **`CLAUDE.md`** raíz — sección "Clientes Activos" del cliente
3. **`contexto/datos-actuales.md`** — dashboard en vivo

Garantiza que los 3 cuenten la **misma historia** en el mismo momento, sin esperar a `/cliente-sync` (que dispara solo post-commit).

Diferente a `/cliente-sync` (S = `cliente-sync`):
- `cliente-sync`: git-based, detecta cambios reales en archivos, scope amplio.
- `sync-status-cliente-3-docs`: cambio puntual de status, scope estrecho, no requiere commit.

---

## Cuándo invocarlo

- Avance de fase (F3 → F4, F7 → F8)
- Resolución de un bloqueo
- Cambio de stack
- Pase a producción / GO-LIVE
- Pausa de un upsell o un alcance

## Cuándo NO invocarlo

- Cambios pequeños que ya capturará el próximo `/cliente-sync`
- Cliente recién creado — usar `cliente-nuevo` que ya cubre los 3 docs

---

## Inputs requeridos

1. **Cliente ID** (ej. SYS, IMP, NPR)
2. **Cambio concreto** a aplicar (ej. "F5 completada", "GO-LIVE el {fecha}", "ManyChat pausado, F7 en curso")
3. **Fecha del cambio** (default: hoy)

---

## Proceso

### Paso 1 — Leer los 3 docs y entender estado actual

- Leer `clients/{XXX}_*/CLIENT_INFO.md`
- Leer sección del cliente en `CLAUDE.md` raíz (buscar `### {XXX} —`)
- Leer `contexto/datos-actuales.md`

Identificar la línea / bloque actual del cliente en cada uno.

### Paso 2 — Drafting del nuevo texto

Componer el nuevo bloque/línea respetando el estilo de cada doc:

- **CLIENT_INFO.md:** entrada técnica detallada (qué se hizo, qué quedó pendiente)
- **CLAUDE.md raíz:** una o dos líneas resumen para la sección del cliente — agregar al inicio o reemplazar el "Estado:"
- **datos-actuales.md:** una línea bullet con `[Cliente X] {fecha}: {qué cambió}`

Validar que las 3 versiones sean **coherentes y no se contradigan**. Si hay datos numéricos (records importados, % completado), debe coincidir.

### Paso 3 — Aplicar Edits en paralelo

3 Edits independientes, idealmente con `Edit` tool en 1 mensaje paralelo:

- Edit en `CLIENT_INFO.md`
- Edit en `CLAUDE.md` raíz
- Edit en `contexto/datos-actuales.md`

Si alguno tiene ambigüedad de `old_string`, agregar contexto suficiente.

### Paso 4 — Verificación cruzada

Re-leer los 3 docs y verificar:
- ✓ Mismas fechas
- ✓ Mismos números
- ✓ Mismo estado nominal (Etapa N, Fase N, % progreso)
- ✓ No quedan referencias contradictorias (ej. `CLAUDE.md` dice "F5 completada" y `CLIENT_INFO.md` dice "F4 en curso")

### Paso 5 — Reportar al usuario

Output corto:
```
✓ CLIENT_INFO.md (clients/{XXX}_{Nombre}/)
✓ CLAUDE.md raíz (sección {XXX})
✓ contexto/datos-actuales.md

Status sincronizado: {cambio aplicado, ej. "F5 completada — workflow v0.2 activo en n8n con 9 tools cableadas, smoke tests OK"}.

Próximo paso: {sugerencia operativa, ej. "correr smoke-test-agente-webhook contra v0.2 / arrancar F6 ManyChat"}.

Nota: si querés que el commit suceda ahora, correr /cliente-sync. Si no, se commiteará con el próximo trabajo significativo.
```

---

## Composición

**Invoca:** ninguno.
**Es invocado por:** otros skills (bootstrap-, integrar-, smoke-test-) post-fase, o manualmente.
**No reemplaza a `/cliente-sync`** — es complementario.

---

## Notas operativas

- **Tiempo:** 3-5 min del skill.
- **No commitea.** Solo edita los 3 archivos. El commit es responsabilidad de `cliente-sync` o de un commit manual posterior.
- **Si el cliente no existe en CLAUDE.md raíz** (raro post-`cliente-nuevo`), warning explícito.
- **Errar a más data en `CLIENT_INFO.md`, menos en `CLAUDE.md`, mínima en `datos-actuales.md`.** Los 3 escalan en abstracción.
