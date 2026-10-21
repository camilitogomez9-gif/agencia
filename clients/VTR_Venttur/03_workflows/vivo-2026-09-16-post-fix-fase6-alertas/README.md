# Snapshot post-fix · Fase 6 alertas · 2026-09-16

Aplicado sobre el vivo por API n8n (`https://[TU-INSTANCIA-N8N]`) el 2026-09-16 después del deploy de Fase 3. Cierra la sección 6A del plan (alertas P1 + P2 desde el guardrail). Las secciones 6B y 6C quedan documentadas al final como diseño pendiente.

## SHA256

```
e73409a0f161fc76355fa152092ca78f84802b3b004153e7de5a0078d53e8a82  main-venttur.json
2f4f63e45f6a17bcd42c868c2f9551c10f599fa8cf50040336980a28c3b1b636  vtr-digest-diario-guardrail.json
```

## Cambios aplicados

### 1) Persistencia · nueva tabla Postgres `vtr_phantom_interceptions`

Creada en el mismo Postgres que hostea `n8n_chat_histories` (credencial `Venttur` · id `ihpvM7nYMdLCwWDP`).

```sql
CREATE TABLE IF NOT EXISTS vtr_phantom_interceptions (
    id BIGSERIAL PRIMARY KEY,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    session_key TEXT NOT NULL,
    execution_id TEXT NOT NULL,
    lead_nombre TEXT,
    lead_programa TEXT,
    url_enviada TEXT,
    mensaje_original_parte1 TEXT,
    mensaje_original_parte2 TEXT,
    mensaje_original_parte3 TEXT
);
CREATE INDEX IF NOT EXISTS idx_vtr_phantom_occurred ON vtr_phantom_interceptions(occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_vtr_phantom_session ON vtr_phantom_interceptions(session_key);
```

Cada activación del guardrail escribe una fila. Sirve como fuente para el digest diario y como registro histórico para análisis.

### 2) 3 nodos nuevos en `main-venttur` (`k3aivKSP67S97IHn`) — 40 → 43 nodos

Topología del branch de monitoreo (todo en paralelo al flujo principal del mensaje):

```
Detectar promesa fantasma
   ├─→ Normalizar burbujas                          (rama principal · el mensaje reemplazado sigue al lead)
   └─→ ¿Promesa fantasma interceptada? (IF)
         ├─ TRUE → Alerta promesa fantasma (Telegram)   (P1 · alerta inmediata)
         │      → Log guardrail hit (Postgres INSERT)   (P1 · persistencia)
         └─ FALSE → (nada · el guardrail no se activó, no hay que alertar)
```

- **`¿Promesa fantasma interceptada?`** — IF sobre `_phantom_promise_intercepted === true` (flag emitido por el Code node de Fase 3).
- **`Alerta promesa fantasma`** — Telegram · chatId `6390727286` · credencial `botla agencia` (`V5k84z3AjQc9Y5yg`) · `onError: continueRegularOutput` para no bloquear la persistencia.
- **`Log guardrail hit`** — Postgres INSERT idempotente por `execution_id` (queryReplacement con 8 parámetros) · `onError: continueRegularOutput` para no bloquear Telegram.

Formato del mensaje Telegram:

```
✈️ VENTTUR — Promesa fantasma interceptada por guardrail

Lead: {nombre} ({telefono | subscriber_id})
Programa: {programa | 'sin definir'}
URL enviada al lead: {url_canónica}

Mensaje que hubiera enviado el bot:
1) {parte1_original}
2) {parte2_original}
3) {parte3_original}

Ejecución: https://[TU-INSTANCIA-N8N]/workflow/k3aivKSP67S97IHn/executions/{execution_id}
```

### 3) Workflow nuevo · `VTR · digest diario guardrail` (`BzBCMGxEdJy6zmA9`)

5 nodos · activo · cron a las **14:00 UTC = 08:00 CDMX** cada día (México no observa DST desde 2022, la offset -6 es estable).

Topología:

```
Cron 08:00 CDMX
   → Traer hits 24h (SELECT vtr_phantom_interceptions WHERE occurred_at > NOW() - INTERVAL '24 hours' LIMIT 50)
   → Formatear digest (Code node · agrupa por session_key, top 5, arma texto)
   → ¿Enviar digest? (IF sobre send === true)
       └─ TRUE → Enviar Telegram
       └─ FALSE → (nada · si N=0 no manda mensaje)
```

Formato del digest:

```
✈️ VENTTUR — Digest 24h del guardrail

Guardrail activado: {N} vez(ces) en {leads_unicos} lead(s) distinto(s) durante las últimas 24 horas.

Top por severidad:
1. {nombre} ({session_key}) · {programa} · {hits} hit(s)
2. ...
5. ...

Detalle completo:
https://[TU-INSTANCIA-N8N]/workflow/k3aivKSP67S97IHn/executions
```

**Regla de silencio**: si N=0, no se envía nada (`send: false` desde el Code node). Cero ruido en días limpios.

## Comportamiento esperado en producción

Ahora que Fase 3 corrigió la fuente del bug (prompt v2.1 + guardrail) y Fase 6 puso monitoreo:

- **Caso normal (95%+)**: el modelo con prompt v2.1 responde correctamente enviando el link cuando el lead pide agendar. El guardrail no se dispara. Postgres queda vacío. Ningún Telegram sale.
- **Caso raro**: el modelo, bajo presión conversacional, promete coordinar cita sin enviar link. El guardrail intercepta, reemplaza el mensaje por el link canónico + framing de disculpa, y se dispara:
    - **Alerta P1 en Telegram** al equipo (segundos).
    - **INSERT en Postgres** para historial.
- **Digest matinal**: si en las 24h previas hubo activaciones, un solo mensaje resumen. Si no, silencio.

## Rollback

Para revertir Fase 6 (mantener Fase 3 pero sin monitoreo):

1. Restaurar `main-venttur.json` desde `vivo-2026-09-16-post-fix-prompt-guardrail/` (40 nodos, sin los 3 nodos nuevos).
2. Desactivar y borrar el workflow `BzBCMGxEdJy6zmA9`.
3. Opcional: `DROP TABLE vtr_phantom_interceptions;` (o dejarla — no molesta a nada).

Para revertir todo (Fase 3 + Fase 6), usar el snapshot de `vivo-2026-09-15-pre-fix-nahe/`.

## Diseño pendiente (fuera del scope de esta iteración)

### 6B · Reconciliador transversal (batch diario)

Cruza cada 24h las 4 fuentes que hoy divergen en silencio:

- **Airtable Leads** ↔ **Postgres `n8n_chat_histories`** (por sessionKey normalizado).
- **Airtable Leads** ↔ **ManyChat subscriber log** (por `ID Manychat`).
- **Airtable Leads** ↔ **Meta CAPI events** (por `Folio` / `fbclid`).
- Cuando GHL entre en producción, agregar la cuarta pata.

Reporta divergencias específicas: `Link asesoría enviado = true` en Airtable pero ninguna URL en el chat histórico; `Agendan cita = true` sin evento en el calendar; leads en Postgres sin registro en Airtable. Persiste el delta en tabla `vtr_reconciliation_deltas`.

Requiere primero cerrar 6C (normalización de teléfono como sessionKey único) para que los cruces no sean ruidosos.

### 6C · Normalización de teléfono canónico

`sessionKey` = `whatsapp_phone.replace('+','')` sin normalizar → conviven `521…` (~2.510 leads) y `52…` (~1.229). Un mismo lead puede tener **dos memorias** distintas, y los cruces por teléfono fallan.

Fix: implementar helper `canonPhone(raw)` que resuelva el quirk MX (`52` → `521` cuando falta) y aplicarlo consistentemente en:

- `sessionKey` del Postgres Chat Memory
- `Buscar si ya existe` (Airtable filterByFormula)
- `Buscar registro` (Airtable filterByFormula)
- `outreach-form-meta` (Normalize Payload)
- Eventual reconciliador

**Cuidado**: cambiar el sessionKey del Chat Memory rompe la continuidad de la memoria para leads existentes. Hay que hacer una migración one-shot que consolide filas duplicadas antes del cambio en runtime. Ola 3.4 de la guía de agosto ya tenía este tema flageado como pendiente.

## Estado del sistema al final de Fase 6

- Prompt v2.1 vivo desde 2026-09-16 14:49 UTC (Fase 3 · Capa 1).
- Guardrail `Detectar promesa fantasma` vivo desde el mismo momento (Fase 3 · Capa 2).
- Alerta P1 Telegram + persistencia Postgres activas desde 2026-09-16 ~16:00 UTC (Fase 6A).
- Digest diario 08:00 CDMX activo desde el mismo momento (Fase 6A).
- 34 leads afectados históricamente identificados (Fase 5 · barrido).
- Deuda: 6B reconciliador + 6C normalización teléfono + Fase 7 traspaso a GHL.
