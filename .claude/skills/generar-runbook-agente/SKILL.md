---
name: generar-runbook-agente
description: >
  Usar este skill cuando hay que generar el runbook operativo de un agente
  conversacional en producción (estructura: SLAs P1-P3, diagnóstico rápido,
  incidentes comunes, queries SQL útiles, escalamiento, lecciones aprendidas,
  decisiones arquitectónicas críticas). Se activa con frases como "armar
  runbook del agente X", "runbook para X", "guía de troubleshooting del agente",
  "doc de soporte producción cliente X". Stack: Airtable + Supabase + ManyChat + n8n.
---

# Skill: Generar Runbook Agente Productivo

## Descripción

Genera el runbook operativo del agente conversacional. Es el doc al que recurre el el equipo cuando hay un incidente o cuando hay que diagnosticar.

**Estructura validada en SYS:**

1. Arquitectura en una pantalla (diagrama + componentes/dueños)
2. SLAs por severidad (P1 < 30 min, P2 < 2h, P3 < 24h)
3. Diagnóstico rápido en 5 min (los primeros pasos al recibir alerta)
4. Incidentes comunes (síntoma → causa raíz → fix)
5. Mantenimiento periódico (diario, semanal, mensual)
6. Contactos (cliente decisor, gerente, técnico, la agencia on-call)
7. Comandos útiles (Supabase SQL Editor queries)
8. Variables y credenciales clave (referencia, NO commitear valores)
9. Decisiones arquitectónicas críticas (Session Pooler, Ignore SSL, $fromAI pattern, queryReplacement array, etc.)
10. Incidentes resueltos (lecciones aprendidas — se va completando)
11. Escalamiento

---

## Cuándo invocarlo

- F8 del Plan Maestro (pre-producción)
- Cuando el cliente entra en producción y hay que tener el runbook listo
- Cuando hay rotación del equipo y un nuevo on-call necesita el doc

## Cuándo NO invocarlo

- Cliente no productivo aún
- Para incidentes específicos (esos van como entradas a "Incidentes resueltos", no como runbook nuevo)

---

## Inputs requeridos

1. **Cliente ID + nombre**
2. **Stack activo** (canales, tools, integraciones)
3. **Contactos** (cliente decisor + la agencia on-call)
4. **Lista de decisiones técnicas tomadas durante el proyecto** (las más críticas)
5. **Lista de incidentes resueltos** (si los hay) en formato síntoma → causa → fix

---

## Proceso

### Paso 1 — Generar el doc con secciones estándar

Path: `clients/{XXX}_{Nombre}/06_docs/runbook.md`

Base: `clients/SYS_SistemasYSoluciones/06_docs/runbook.md` (validado).

### Paso 2 — Adaptar por niche/stack

- **Si cliente NO usa ManyChat:** quitar sección de timeout ManyChat / patrón Respond-First.
- **Si cliente NO tiene CRM (caso típico — pausado por upsell):** marcar `notificar_lead` con scope reducido.
- **Si cliente NO usa Telegram:** quitar referencias a alerts la agencia por Telegram.

### Paso 3 — Pre-poblar "Decisiones arquitectónicas críticas"

Embebir las lecciones SYS por default:
- Supabase Session Pooler vs Direct (IPv6 issue)
- Ignore SSL Issues = true en n8n credential
- queryReplacement Postgres como array literal
- `$fromAI` con backticks + type string + comment auto-generated
- Tabla "ghosting" para upsell pendiente
- Patrón ManyChat Respond-First (para F6 si aplica)

### Paso 4 — Pre-poblar "Incidentes resueltos" con templates

Las lecciones SYS son base:
- Log queryReplacement bug (síntoma: `sys_tool_calls` vacía; causa: sintaxis CSV; fix: array literal)
- Schema validation strict (síntoma: respuestas vacías `{}`; causa: type≠string en $fromAI; fix: cambiar a string + ajustar schema)
- $fromAI con quotes mezcladas (síntoma: tool falla; causa: SyntaxError JS; fix: backticks consistentes)

### Paso 5 — Sección de queries SQL útiles

Embebir las queries Supabase típicas:
```sql
-- Última conversación de un lead
SELECT ... FROM n8n_chat_histories WHERE session_id = '...' ORDER BY id;

-- Tool calls con error 24h
SELECT tool_name, COUNT(*) FROM sys_tool_calls
WHERE status != 'success' AND created_at >= NOW() - INTERVAL '24 hours'
GROUP BY tool_name;

-- Performance tools 24h
SELECT * FROM sys_tool_metrics_24h;

-- Leads abandonados
SELECT * FROM sys_leads_abandonados;
```

### Paso 6 — Reportar al usuario

Output:
- Path del runbook
- Lista de secciones generadas
- Recordatorio: la sección "Incidentes resueltos" se va completando con cada incidente que pase. Cada uno va con síntoma + causa + fix.

---

## Composición

**Invoca:** ninguno.
**Es invocado por:** F8 del Plan Maestro o standalone cuando el cliente entra en producción.

---

## Notas operativas

- **Tiempo:** 30-45 min del skill.
- **Es un doc vivo:** se actualiza con cada incidente. La sección "Incidentes resueltos" es el conocimiento acumulado de la agencia.
- **El runbook NO contiene credentials.** Esos van en `*-credentials.md` (gitignored). Acá solo referencias y nombres.
- **El runbook puede compartirse con el cliente** si quieren visibilidad operativa. Las credentials nunca.
