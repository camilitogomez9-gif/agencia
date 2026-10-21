---
name: setup-supabase-memoria-agente
description: >
  Usar este skill cuando hay que setup Supabase como memoria + observabilidad de
  un agente conversacional (F2 del Plan Maestro Etapa 2). Se activa con frases
  como "setup Supabase para X", "configurar memoria del agente X", "armar la
  base de Postgres para X", "F2 cliente X". Genera el SQL schema completo
  (4 tablas + 3 vistas + función upsert), guía de creación de proyecto en sa-east-1
  free tier, doc credentials gitignored con decisiones técnicas pre-cocinadas
  (Session Pooler + Ignore SSL).
---

# Skill: Setup Supabase Memoria Agente

## Descripción

Configura Supabase como backend de **memoria persistente + observabilidad** del agente conversacional. Incluye:

- **4 tablas:** `n8n_chat_histories` (memoria LangChain), `sys_tool_calls` (observabilidad), `sys_session_state` (cache cross-turn), `sys_conversations_summary` (reservado v2.1)
- **3 vistas:** `sys_leads_abandonados`, `sys_tool_metrics_24h`, `sys_sesiones_activas_hoy`
- **1 función:** `upsert_session_state` (helper)

Pre-cocina las 2 decisiones técnicas críticas descubiertas en SYS:
1. **Session Pooler** (`aws-0-sa-east-1.pooler.supabase.com:5432`) — NO Direct Connection (IPv6 incompatible con droplets) NI Transaction Pooler 6543 (rompe prepared statements).
2. **Ignore SSL Issues = true** en credencial n8n Postgres (Node.js sin cert root de Supabase).

---

## Cuándo invocarlo

- F2 del Plan Maestro
- Cliente Etapa 2 con stack Airtable + Supabase + n8n

## Cuándo NO invocarlo

- Stack distinto (PlanetScale, Neon directo, etc.) — usar setup específico
- Solo migración SQL sin Supabase nuevo (usar `supabase` skill genérico)

---

## Inputs requeridos

1. **Cliente ID + nombre** (ej. SYS, Sistemas y Soluciones)
2. **Cuenta Supabase a usar** (ej. `[EMAIL-AGENCIA]` — la cuenta compartida o la del cliente)
3. **Región preferida** (default: `sa-east-1` São Paulo)

---

## Proceso

### Paso 1 — Generar SQL schema

Crear `clients/{XXX}_{Nombre}/06_docs/supabase-schema.sql` con el schema completo. Base: `clients/SYS_SistemasYSoluciones/06_docs/supabase-schema.sql` (validado).

Adaptaciones por cliente:
- Si no usa la tool de notificación → omitir `sys_session_state.lead_airtable_id`
- Si no quiere observabilidad → reducir a solo `n8n_chat_histories`

### Paso 2 — Guía de setup proyecto Supabase

En el doc setup, incluir:
1. Login en https://supabase.com (cuenta {input})
2. New project → name `la agencia-{cliente_id_lower}`, password generada (guardar en password manager), region {input}, Free tier
3. Esperar 2-3 min provisioning
4. SQL Editor → pegar el schema → Run → verificar 4 tablas + 3 vistas + 1 función en Table Editor

### Paso 3 — Doc credentials gitignored

Crear `clients/{XXX}_{Nombre}/06_docs/supabase-credentials.md` (cubierto por `**/*-credentials.md` en `.gitignore`) con:

```markdown
## Proyecto Supabase
- Nombre: la agencia-{cliente_id_lower}
- Cuenta: {input}
- Region: {input}
- Plan: Free tier
- Project Reference ID: <<<COMPLETAR>>>
- URL: https://<<<REF>>>.supabase.co

## Password DB
- Generado: <<<FECHA>>>
- Password: <<<COMPLETAR — guardar también en 1Password/Bitwarden>>>

## Connection — IMPORTANTE: usar Session Pooler

> ⚠️ Decisión técnica: la Direct Connection falla desde el droplet n8n por IPv6 no soportado outbound.
> Usar Session Pooler (Supavisor) que soporta IPv4. NO usar Transaction Pooler 6543 — rompe prepared statements.

### Parámetros para n8n credential
| Campo | Valor |
|---|---|
| Host | aws-0-{region}.pooler.supabase.com |
| Database | postgres |
| User | postgres.<<<REF>>> |
| Password | (de arriba) |
| Port | 5432 |
| SSL | require |
| Ignore SSL Issues | true |

> ⚠️ Ignore SSL Issues = true es necesario porque Node.js (n8n) no tiene el cert root de Supabase pre-instalado. La conexión sigue siendo TLS encriptada.

## Credencial n8n
- Nombre: Supabase {CLIENTE_ID}
- ID interno: <<<COMPLETAR>>>
- Creada: <<<FECHA>>>
- Smoke test: <<<SELECT 'hello' OK >>>
```

### Paso 4 — Guía de smoke test

En el doc, smoke test final:
```sql
-- En SQL Editor de Supabase
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_name LIKE 'sys_%' OR table_name = 'n8n_chat_histories'
ORDER BY table_name;
```

Esperado: 4 filas (las 4 tablas).

```sql
SELECT * FROM sys_tool_metrics_24h;
SELECT * FROM sys_leads_abandonados;
SELECT * FROM sys_sesiones_activas_hoy;
```

Esperado: 3 queries OK sin error (resultados vacíos al inicio).

Test desde n8n (post-setup credencial):
- Crear workflow temporal con Postgres > Execute Query
- Query: `SELECT 'hello' AS test;`
- Credential: `Supabase {CLIENTE_ID}` (Session Pooler)
- Execute → debe retornar 1 fila con `test = hello`

### Paso 5 — Reportar al usuario

Output:
- Path del SQL schema
- Path del doc credentials (gitignored)
- Pasos: crear proyecto Supabase → ejecutar SQL → crear credencial n8n → smoke test
- Recordatorio: completar `<<<COMPLETAR>>>` en credentials.md con valores reales

---

## Composición

**Invoca:** ninguno.
**Es invocado por:** `bootstrap-agente-etapa-2` (S1) como F2.
**Precede a:** `generar-workflow-agente-n8n` (S2).

---

## Notas operativas

- **Tiempo estimado:** 15-30 min (~5 min del skill + 10-25 min del usuario en Supabase UI + n8n).
- **Free tier limits:** 500 MB DB, 2 GB egress/mes. Cubre 6+ meses de un agente conversacional típico.
- **Region sa-east-1 (São Paulo)** es la más cercana a Argentina. Si el cliente está en otra región, ajustar.
- **El SQL es idempotente** (`CREATE TABLE IF NOT EXISTS`) — se puede re-ejecutar sin riesgo.
