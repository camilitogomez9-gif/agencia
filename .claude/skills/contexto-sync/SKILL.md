# Skill: contexto-sync

**Propósito:** Sincronizar el estado global del workspace con `contexto/` automáticamente después de commits de clientes.

**Trigger:** Se ejecuta automáticamente después de `/cliente-sync` (al finalizar trabajo en un cliente).

---

## Qué Hace

1. **Lee git log** (`git log --oneline -15`) para detectar commits recientes
2. **Parsea CLAUDE.md** para extraer:
   - Clientes activos y su status actual (LIVE/TESTING/DISCOVERY)
   - Fase de cada cliente (system prompt versión, testing versión, etc.)
   - Pendientes técnicos de cada cliente
3. **Analiza `contexto/proyectos.md`** para detectar cambios
4. **Genera/actualiza `contexto/datos-actuales.md`:**
   - Tabla de clientes activos con estado, fase, última actividad, próximo paso
   - Lista de proyectos en desarrollo con prioridad
   - Pendientes críticos por cliente
   - Cambios recientes (últimos 3 commits)
   - Métricas del workspace
5. **Actualiza `contexto/proyectos.md`:**
   - Mueve proyectos completados a "Completados" si hay evidencia en git
   - Agrega progreso % si hay cambios detectados
   - Remueve de "En desarrollo" si ya está en backlog
6. **Hace commit:**
   ```bash
   git add contexto/
   git commit -m "sync-contexto: actualiza datos-actuales, proyectos, estado de clientes"
   ```
7. **Reporta resumen:** Cambios detectados, archivos actualizados

---

## Cómo Se Ejecuta

**Opción A (Recomendada):** Integrado en `/cliente-sync`

Después de que `/cliente-sync` termina, ejecuta automáticamente `/contexto-sync`. El flujo es:

```
/cliente-sync (detecta cambios CLT)
    ↓
git commit "sync(CLT[NNN]): ..."
    ↓
/contexto-sync (detecta cambios globales) [AUTOMÁTICO]
    ↓
git commit "sync-contexto: ..."
    ↓
Reporta resumen (2 commits)
```

**Opción B (Manual):** Si quieres actualizar contexto sin haber hecho cambios a clientes

```
/contexto-sync (sin trigger de cliente-sync)
```

---

## Implementación Técnica

### Paso 1: Parse git log

```bash
git log --oneline -15 | grep -E "sync|feature|fix"
```

Extrae últimos 15 commits relevantes. Busca patrones de cambio.

### Paso 2: Parse CLAUDE.md

Lee la sección "Clientes Activos" (línea ~197 adelante) y extrae:
- Nombre CLT y descripción
- Status implícito (leyendo la sección de "Pendientes técnicos")
- Versión de system prompt actual
- Testing guide más reciente

Ejemplo de parseo:
```
### CLT001 — Importadores Conectados
Status = LIVE (porque hay "en producción")
Fase = System prompt v1.6 (línea que dice "System prompt v1.6")
```

### Paso 3: Parse `contexto/proyectos.md`

Lee secciones "En desarrollo", "Completados", "Backlog" y detecta:
- Qué proyectos se movieron entre secciones
- Qué nuevos proyectos aparecieron
- Qué proyectos tienen fecha de cambio

### Paso 4: Generar datos-actuales.md

Estructura dinámica (usar plantilla en `contexto/datos-actuales.md` como base):

```markdown
# Estado Actual del Workspace

> **Actualizado:** [timestamp actual]

---

## Resumen Rápido

- **Clientes activos:** [COUNT de CLTs en LIVE + TESTING]
- **Proyectos en desarrollo:** [COUNT]
- **Últimos cambios:** [commit más reciente del log]

---

## Clientes Activos

[generar tabla dinámica]

| CLT | Nombre | Status | Fase Actual | Última Actividad | Próximo Paso |
...

## Pendientes Críticos

[parsear "Pendientes técnicos" de CLAUDE.md para cada CLT]

## Cambios Recientes

[mostrar últimos 3 commits del log]

## Métricas

[contar clientes LIVE, TESTING, scripts, herramientas]
```

### Paso 5: Actualizar proyectos.md

Lógica:
- Si un proyecto tiene commit reciente (en git log): actualizar "Última actualización"
- Si un proyecto aparece en CLAUDE.md como completado pero está en "En desarrollo": mover a "Completados"
- Si un proyecto no tiene actividad en 2+ meses: marcar como "Dormido" o considerar mover a backlog

---

## Reglas de Decisión

| Condición | Acción |
|-----------|--------|
| Hay commits nuevos en últimas 24 hrs | Actualizar secciones afectadas en datos-actuales.md |
| Proyecto en CLAUDE.md como "Completado" pero en "En desarrollo" | Mover a "Completados" en proyectos.md |
| Proyecto sin actividad 30+ días | Marcar como "En pausa" o sugerir mover a backlog |
| New CLT detectado en CLAUDE.md | Agregar a tabla de clientes en datos-actuales.md |
| Status de CLT cambió (discovery → testing → live) | Actualizar columna Status en tabla |

---

## Integración con `/cliente-sync`

En `.claude/skills/cliente-sync/SKILL.md`, al final del flujo:

```
[... flujo actual de cliente-sync ...]

# AL FINAL, ANTES DE REPORTAR:
IF hay cambios en clientes detectados:
    PRINT "Sincronizando contexto global..."
    EXEC skill "contexto-sync"
ENDIF

PRINT "✅ Sincronización completada"
```

---

## Output Esperado

```
✅ contexto-sync ejecutado

📊 Estado del workspace actualizado:
- Clientes: 8 (7 LIVE, 1 TESTING)
- Proyectos: 2 en desarrollo, 6 completados

📝 Archivos actualizados:
  - contexto/datos-actuales.md (estado clientes, pendientes, cambios recientes)
  - contexto/proyectos.md (progreso proyectos)

📌 Cambios detectados en últimas sesiones:
  - CLT001: Testing v4 completado, próximo: grabar audios
  - CLT003: System prompt v1.7 en testing, casi listo para LIVE
  - Proyecto Diagramador: 60% completado

🔄 Commits realizados:
  [git commit "sync-contexto: actualiza datos-actuales y proyectos"]
```

---

## Notas

- **Frecuencia:** Se ejecuta automáticamente después de cada `/cliente-sync` (al finalizar trabajo)
- **Manual:** También puede ejecutarse manualmente si quieres actualizar contexto sin haber trabajado en cliente
- **Parseadores:** Usar regex o parseo básico de líneas (no necesita ser perfecto — mejor "casi correcto" que no funcionar)
- **Fallback:** Si no puede parsear algo, marcar como "REVIEW MANUALMENTE" en el output
- **Git como fuente de verdad:** El log de git es la fuente de verdad para detectar cambios. Si no está en git, no se actualiza

---

## Checklist de Implementación

- [ ] Crear lógica de parse de `git log --oneline`
- [ ] Crear parsedor de CLAUDE.md (extraer clientes, status, fases)
- [ ] Crear parsedor de `contexto/proyectos.md`
- [ ] Crear generador dinámico de `contexto/datos-actuales.md`
- [ ] Crear actualizador de `contexto/proyectos.md`
- [ ] Integrar con `/cliente-sync` para ejecución automática
- [ ] Testear con 2–3 clientes reales (hacer cambios, ejecutar sync)
- [ ] Validar output y commits

---

## Trigger y Activación

**Primera activación:** Manual (`/contexto-sync`) para validar flujo
**Automatización:** Después de validar, integrar en `/cliente-sync` para ejecutarse automáticamente

---

_Este skill mantiene `contexto/` siempre fresco, habilitando sesiones de trabajo sin necesidad de `/iniciar`._
