# Snapshot vivo — 2026-09-15 (Fase 0 del plan Nahe)

Traído por API n8n (`https://[TU-INSTANCIA-N8N]`) el **2026-09-15** para verificar el estado real de los workflows VTR antes de tocar nada. Sirve como referencia + rollback.

Guía-fuente: `06_docs/guia-correcciones-reporte-agosto-2026.md`.
Plan: `~/.claude/plans/max-de-vtr-envi-serialized-grove.md`.

## SHA256 · versión canónica de este snapshot

```
ee51eda587535bc593e8371ef5e6b6745604d2bd92195cce55227daaf40532f4  actualizar-link-enviado.json
d33be9b39673e9dbe682fa7f3494ae21339963c1f134106efefd22318da21d98  confirmacion-agenda.json
d5c56bfa0eb955d1a3812e1aa793af8f317e8486046a54a83cfb5ca08886a3e9  main-venttur.json
8c9f4f77085833cad5a57a9c96893539143e7f3d616be69abab5227f2586e4d1  resumen-etiquetas-seguimientos.json
```

## Metadatos por workflow

| Workflow | ID n8n | Nodos | Active | updatedAt (n8n) |
|---|---|---|---|---|
| `main-venttur` | `k3aivKSP67S97IHn` | 39 | **true** | 2026-09-15 10:16:44 UTC · **tocado hoy** |
| `confirmacion-agenda` | `2PSekVBxarsrnVBu` | 22 | **true** | 2026-08-18 16:31:45 UTC |
| `resumen-etiquetas-seguimientos` | `DyrDumQgb6S4zHsS` | 31 | **false** | 2026-08-18 16:10:58 UTC |
| `actualizar-link-enviado` | `gRSMjzxggA4UePjz` | 7 | false (sub-workflow, se llama por Execute Workflow) | 2026-05-26 16:17:25 UTC |

## Diff estructural vs `vivo-2026-08-18-post-patches/`

**Los 3 workflows presentes en el snapshot de agosto tienen los mismos nombres de nodo y misma cardinalidad** (39 / 22 / 31). Los SHA256 difieren por serialización (orden de keys, `versionId`, metadatos del export por API), no por cambios de shape.

**Diferencia relevante**: las **conexiones internas de `confirmacion-agenda` sí cambiaron** entre AGO y hoy. En AGO el flujo era `If → Agendan cita = true → Switch → mensaje_X → Settear variables → Enviar` (marcar antes de enviar). En el vivo actual es `If → Switch → mensaje_X → Settear variables → Enviar → Agendan cita = true` (marcar después de enviar). Es decir, **B4-b se aplicó al vivo entre el snapshot de agosto y hoy, sin quedar registrado en el repo**.

## Los 3 hechos verificables del plan

### 1) ¿`confirmacion-agenda` ya movió `Agendan cita = true` a después del envío? · ✅ SÍ

Conexiones (jq sobre el JSON vivo):

```
Settear variables  → Enviar
Settear variables1 → Enviar1
Settear variables2 → Enviar2
Enviar   → Agendan cita = true
Enviar1  → Agendan cita = true
Enviar2  → Agendan cita = true
```

`Agendan cita = true` es el nodo Airtable terminal. El write se ejecuta **después** de los tres `Enviar*`. **B4-b está aplicado** en las 3 ramas (Andrés, Diego, Rodrigo).

Sin embargo, los nodos `Enviar*` son `httpRequest` con `options: {}`, `onError: null`, `retryOnFail: null`. El fix protege contra fallos HTTP 4xx/5xx (n8n detiene la cadena) pero **NO contra `200 OK + body.status === "error"`**, que es el comportamiento típico de ManyChat cuando el `sendFlow` no puede entregar (subscriber inválido, flow inválido, rate limit).

### 2) ¿`resumen-etiquetas-seguimientos` sigue `active: false`? · ✅ CONFIRMADO

`active = false`. El clasificador post-hoc de drip **no está corriendo**. `Ola 2.3` (guard `¿Programa ya definido?`) sí está aplicada como nodo (existe en el JSON), pero **el workflow no dispara**. Investigar por qué se desactivó antes de decidir si reactivar.

Este workflow no es crítico para el envío inicial del link — es el que decide qué drip aplicar a leads que ya recibieron o no recibieron link. Con él apagado, la cadencia de nurturing viene por otro lado (probablemente los flows de ManyChat directamente, o el despachador diferido `vtr-despachador-proactivo-v1`). Es un tema secundario al caso Nahe.

### 3) ¿`main-venttur` tiene `Normalizar burbujas` + bloque `[ESTADO DEL LEAD]`? · ✅ AMBOS PRESENTES

- Nodo `Normalizar burbujas` (`n8n-nodes-base.code`) presente entre `Formatear mensaje WPP` y `Settear variables`.
- El `text` del `Agente IA WPP` arranca con el bloque `[ESTADO DEL LEAD]` implementado como IIFE que lee de `$('Buscar si ya existe').first().json`, con fallback nombre-con-tilde / nombre-sin-tilde, y campos: `Nombre`, `Programa interés`, `Origen/Fuente lead`, `Link asesoría enviado`, `Agendan cita`, `Estado conversación`, `Grado Escolar`, `Inicio Deseado`, `Nivel Inglés`.
- Nodo `Estampar estado (Contestó)` (Execute Workflow → `b52CUYEkI2Ah3Xj6`) también presente.

## Mapa bug → estado en el vivo (fuente de verdad al 2026-09-15)

| Bug de la auditoría agosto | Estado real hoy | Evidencia |
|---|---|---|
| B1 · Whitelist post-hoc sin `agendar-ema` | ✅ APLICADO | Los 6 URLs canónicos aparecen en el prompt de Tarea 4 del nodo `OpenAI` de `resumen-etiquetas-seguimientos` |
| B2 · `Hay audios?` con "webp" imposible | ✅ APLICADO (asumido — el node existe y el snapshot de agosto ya lo tenía con `notContains`; sin cambios de shape desde entonces) | Diff estructural sin cambios vs `vivo-2026-08-18-post-patches` |
| B3 · `Repetido?` mojibake dedupe | ✅ APLICADO (idem B2) | Diff sin cambios |
| B4-a · Refs rotas en `confirmacion-agenda` | ✅ APLICADO | 22 nodos, `active: true`, sin nodos huérfanos en el diff |
| **B4-b · `Agendan cita = true` antes del envío** | ✅ **APLICADO EN EL VIVO** entre AGO y hoy | Ver §1 arriba — `Enviar* → Agendan cita = true` en las 3 ramas |
| B5 · Andrés/Diego rotos | ✅ APLICADO (mismos 4 refs de B4-a) | — |
| B6 · Agente sin estado del lead | ✅ APLICADO | Ver §3 arriba — bloque `[ESTADO DEL LEAD]` presente en el text del `Agente IA WPP` |
| Guard `¿Programa ya definido?` (Ola 2.3) | ✅ APLICADO | Nodo existe en `resumen-etiquetas-seguimientos` |
| `Normalizar burbujas` (Ola 5.2) | ✅ APLICADO | Nodo existe en el main entre `Formatear mensaje WPP` y `Settear variables` |
| `Estampar estado (Contestó)` | ✅ APLICADO | Nodo Execute Workflow existe en el main |
| **`resumen-etiquetas-seguimientos` activo** | ❌ **INACTIVE** | `active: false` — investigar por qué antes de reactivar |
| **Fire-and-forget en `Enviar WPP` del main** | ❌ **VIGENTE — nueva raíz vs plan** | `httpRequest` a `api.manychat.com/fb/sending/sendFlow` sin `options.response`, sin `retryOnFail`, sin verify del `body.status` |
| **Fire-and-forget en `Settear variables` del main** | ❌ **VIGENTE** | Mismo patrón — `httpRequest` a `setCustomFields` sin verify |
| **Fire-and-forget en `Enviar/Enviar1/Enviar2` de `confirmacion-agenda`** | ❌ **VIGENTE** | Idem — reorden aplicado, verify no |
| **`Envió link?` matchea texto crudo del AI, no confirma entrega** | ❌ **VIGENTE** | IF con condición `$('Agente IA WPP').item.json.output contains "promo.venttur.com/"` — si el AI mencionó el dominio pero la entrega falló, igual dispara `Actualizar link` |

## Hipótesis primaria actualizada para el caso Nahe

**El fix B4-b (reorden en `confirmacion-agenda`) ya está aplicado — no es lo que rompió a Nahe.**

La causa raíz probable es **fire-and-forget en el envío del link inicial**, en el main:

```
Agente IA WPP
  → Formatear mensaje WPP (2do LLM que parte en burbujas)
  → Normalizar burbujas (Code, deja una sola pregunta y limpia comillas)
  → Settear variables (POST setCustomFields — sin verify)
  → Enviar WPP (POST sendFlow — sin verify)
  → Envió link? (IF: output del AI contains "promo.venttur.com/")
  → Actualizar link (Execute Workflow →
       marca Airtable "Link asesoría enviado = TRUE" +
       dispara Rescate Post-Link + Seguimiento Agendamiento)
```

**Modo de falla**: `Enviar WPP` retorna `200 OK` con `body: {status:"error"}` (patrón habitual de ManyChat cuando no puede entregar). n8n avanza sin marcar la ejecución como error. `Envió link?` valida sobre el **texto del AI**, no sobre el resultado del `sendFlow`. Entonces:

1. Airtable escribe `Link asesoría enviado = TRUE` — aunque el lead nunca vio el link.
2. `Rescate Post-Link` corre en cascada — manda mensajes de rescate ("¿viste el link que te mandé?", "¿tenés dudas?") a un lead que no sabe de qué le están hablando.
3. El lead se irrita / se siente ignorado → queja pública (patrón que Max describe como "se sigue repitiendo").

**Encaja con la firma de Nahe en el snapshot Airtable del 13/8**: `Link asesoría enviado = checked`, `Agendan cita = false`, `Toques enviados = 0, cold`.

Este anti-patrón **no estaba cubierto por la auditoría original de Max** — se descubrió en Fase 0 al inspeccionar la topología del main y los parámetros de los HTTP nodes.

## Deuda estructural detectada (excede caso Nahe)

Tres nodos con el mismo anti-patrón fire-and-forget en workflows VTR:

- `main-venttur.Enviar WPP` (POST `sendFlow` de ManyChat)
- `main-venttur.Settear variables` (POST `setCustomFields`)
- `confirmacion-agenda.Enviar` / `Enviar1` / `Enviar2` (POST `sendFlow` — reorden hecho, verify no)

Falta auditar el resto de sub-workflows VTR (`meta-capi`, `wf-rescate-post-link`, `outreach-form-meta`, etc.) por el mismo patrón — pauta para Fase 3.

## Rollback

Si algo se rompe durante el fix, importar los 4 JSON de esta carpeta por API (`PUT /api/v1/workflows/{id}`), tirando encima del vivo. Verificar sha256 post-import contra los valores canónicos del top de este README.

## Salida de Fase 0

- **Fase 1 (reconstrucción del caso Nahe) queda desbloqueada.**
- **La hipótesis primaria cambia**: no es el reorden pendiente en `confirmacion-agenda` (ya aplicado), es el fire-and-forget en `Enviar WPP` del main.
- **El fix de Fase 3 cambia de scope**: pasa de "reordenar `confirmacion-agenda`" a "agregar verify-send determinístico en los 3 (o 5) nodos `Enviar*` del stack VTR".
- El `resumen-etiquetas-seguimientos` inactive queda como investigación paralela — no es el bug de Nahe pero es un pendiente sin explicar.
