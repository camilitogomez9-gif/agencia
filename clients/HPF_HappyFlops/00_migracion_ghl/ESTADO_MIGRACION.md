# Estado de Migración — Happy Flops → GHL

> Este archivo se actualiza al final de cada sesión de trabajo. Si continuás desde una sesión nueva, leé esto primero.

**Plan maestro:** `planes/rol-act-a-como-scalable-hippo.md` (guardado en `~/.claude/plans/rol-act-a-como-scalable-hippo.md`)
**Última actualización:** 2026-07-24 — ver el bloque de estado de abajo

---

## ⚡ Estado al 2026-07-24

| Módulo | Estado |
|--------|--------|
| M0 · M1 · M2 (sub-account, pipeline, custom fields, tags, custom values) | ✅ hechos |
| M3 (Custom Object Producto) | ⏸️ descartado como fuente de envío — el catálogo queda en Airtable |
| **M4 (los 6 workflows de GHL: WF-01 a WF-06)** | ❌ **sin construir.** Todo lo que harían (saludo fijo, transiciones de etapa, reenganche, pago, guardia de horario) hoy no existe en ningún lado |
| **M5 (n8n: HPF Inbound Handler)** | 🔵 **construido y corriendo, pero en demo por Telegram.** Workflow vivo id `IPO1c36NLzkXrBh9`, 64 nodos, snapshot en `../03_workflows/hpf-inbound-handler-live-2026-07-24.json` |
| M6 (Supabase) | ✅ en uso (memoria del agente + buffer de debounce) |
| **M7 (WABA + plantillas Meta)** | ❌ **no arrancado.** Es el bloqueante principal: el número está activo en Kommo y las plantillas tardan 24-72 hs en aprobarse |
| M8 (testing pre-cutover) | 🔵 Fase 1 (13/15) y Fase 2 (20 casos) corridas sobre el agente, no sobre el sistema completo |
| M9 (cutover) | ❌ |

**Lo que hay que saber para retomar:** el agente conversacional está bien (envío determinístico verificado,
12 reglas inviolables sostenidas, memoria persistente), pero **el CRM no está escribiendo nada**: las tools
pegan a GHL con un `opportunity_id` inventado por el adaptador de Telegram (`tg_opp_<chatid>`) y devuelven
404. Hay un build alternativo (`v16`, en repo, no deployado) que resuelve contacto y oportunidad reales
contra la API de GHL y hace andar el CRM ya mismo por Telegram. Detalle completo, causas raíz y decisiones
abiertas: `../06_docs/guia-v16-telegram-crm-real-2026-07-24.md` §0 y la sección "Pendientes HPF" del
`CLAUDE.md` raíz.

> **NUEVO (2026-05-26):** reunión 2026-05-21 con Rebeca aportó 9 casos de mejora. Análisis y decisión en `02_logica_validada/02_mejoras_post_reunion_2026-05-21.md`. **Decisión: NO tocar Kommo; integrar las mejoras (versión MVP) en el build de GHL durante la creación de flujos (etapa actual), validadas en M8 antes del cutover.** Los 3 problemas más graves (loop repetición ~30%, reactivadores, memoria) ya quedan resueltos por el diseño de Etapa 3; el resto son adiciones chicas ya plegadas a los docs (Grupo B). La **opción avanzada** de reconocimiento de imágenes (matching real contra catálogo) + métricas + A/B se hacen **después del cutover, con migración estable**. Pendiente con Oscar (no bloquea): precio pantuflas moño + mínimos cilindros.

---

## Estado actual

| Etapa | Estado | Modelo usado | Notas |
|-------|--------|--------------|-------|
| **Etapa 0** — Recolección de inputs | ✅ COMPLETA | (acción usuario) | Todos los inputs en `00_inputs/` |
| **Etapa 1** — Deducción de lógica actual | ✅ COMPLETA | Opus 4.7 Max | 6 documentos en `01_logica_actual/` |
| **Etapa 2** — Validación con usuario | ✅ **COMPLETA** | Opus 4.7 + reunión Oscar + audios + research web | Todas las decisiones cerradas. Ver `02_logica_validada/01_decisiones.md`. Pendiente menor: confirmar con Oscar si ya tiene Postgres/Supabase pago en el stack actual |
| **Etapa 3** — Diseño arquitectura GHL | ✅ **COMPLETA** | Opus 4.7 | 8 documentos en `03_arquitectura_ghl/` (general, pipeline, data model, workflows, LLMs, re-engagement, integraciones, post-venta) |
| **Etapa 4** — Guía paso a paso | ✅ **COMPLETA** | Haiku 4.5 | 9 módulos en `04_guia_migracion/` (M1–M9). ~35-43 hs de implementación. |
| **Etapa 5** — Ejecución y monitoreo | 🔵 **EN CURSO** | Sonnet 4.6 / Haiku 4.5 / Opus 4.7 | **M0 ✅ · M1 ✅ (2 pendientes menores) · M2 ✅ (4 placeholders con Oscar)** → Siguiente: M3 (Custom Object Producto) o saltar a **M7** (templates Meta — aprobación 24-72h) según orden recomendado |

---

## Decisiones confirmadas (Etapa 0)

1. **Cutover:** paralelo ✅
2. **Agente IA:** n8n + OpenAI como puente inicialmente ✅
3. **Catálogo:** Airtable como source of truth al inicio ✅
4. **Memoria:** GHL Conversations + persistencia externa mínima ✅
5. **AmoCRM legacy:** mantener hasta cutover final ✅
6. **Cuenta GHL:** no existe aún — se crea cuando arranque la implementación ✅
7. **Canal de entrada actual:** WA → Kommo → n8n → Kommo → WA ✅

---

## Inputs disponibles en `00_inputs/`

- [x] `kommo_export.json` — Export completo de Kommo (13 pipelines, custom fields)
- [x] `conversation_samples.json` — Transcripts golden de conversaciones reales
- [x] `XV-Grid view.csv` — Catálogo Airtable evento XV Años
- [x] `Boda-Grid view.csv` — Catálogo Airtable evento Boda
- [x] `Otros-Grid view.csv` — Catálogo Airtable evento Otros
- [x] `Imagen Principal-Grid view.csv` — Imágenes de portada por evento
- [x] `Métodos de Pago-Grid view.csv` — PDF cuentas bancarias
- [x] `Foto Vacaciones-Grid view.csv` — Respuesta auto-fuera de horario
- [x] Workflows n8n — en `../03_workflows/` (7 archivos)

---

## Outputs de Etapa 1 en `01_logica_actual/` (versión Opus 4.7 Max)

- [x] `01_mapa_funcional.md` — Arquitectura y flujo completo (14 secciones, ~700 líneas)
- [x] `02_intents.md` — Catálogo de intents primarios + secundarios + mapping a componentes n8n
- [x] `03_maquina_estados.md` — Pipeline IA (31+ etapas) + transiciones automatizadas + sub-pipeline R1-R5
- [x] `04_catalogo_mensajes.md` — Inventario completo (~120 mensajes únicos en 6 categorías)
- [x] `05_reglas_negocio.md` — 12 secciones: identidad, productos, cotización, upsell, tono, derivación
- [x] `06_redundancias_y_ambiguedades.md` — 7 secciones (A-G) con preguntas KEEP/REMOVE/MODIFY

---

## Próximos pasos (cerrar Etapa 2 → Etapa 3)

**Documento de referencia:** `02_logica_validada/01_decisiones.md` (consolidado de doc 06 + reunión Oscar + cross-reference).

### Decisiones pendientes que bloquean Etapa 3

| # | Decisión | Quién | Acción |
|---|----------|-------|--------|
| 3.1 | Memoria: 6 meses (A) o indefinida ~USD 25/mes (B) | Oscar | la agencia pasa costos detallados |
| 3.2 | Imágenes: Vision GHL / Claude / ajuste de prompt | la agencia → Oscar | Testear 10 imágenes reales (tarea #8) |
| 3.3 | 12 pipelines LIMBO en Kommo: archivar / mantener / migrar selectivo | Oscar | la agencia pasa propuesta default |
| 3.4 | Reglas "En espera" vs "Ventas perdidas real" | Oscar | Documentar criterios operativos |
| 3.5 | Delays reales R1/R2/R3 en los 4 sub-workflows | la agencia | Verificar en n8n |
| 3.6 | Sandalias delgadas: $24 (textos) vs $25 (doc 06) | Oscar | Confirmar precio actual |

**Técnico paralelo (no bloquea concepto pero sí implementación):**
- 3.7 Extraer todos los system/user prompts del JSON del workflow main-v2 (cliente lo pidió en E.4)
- 3.8 Documentar función exacta del bot `R2 GENERICO` (id 20998)

### Contradicciones resueltas en cross-reference (2026-05-12)

- **Pipeline post-pago:** 3 etapas separadas (sin diseño / diseño / producción), no consolidadas (reunión > doc 06 original)
- **Cadencias seguimientos:** 24h/48h/72h hasta 7 días de cara al cliente (reunión > doc 06)
- **Personalización seguimientos:** LLM-generated con contexto, no salesbots hardcoded (reunión > doc 06 D.3) — cambio arquitectónico importante
- **Modelo imágenes:** híbrido OpenAI + Claude (reunión > doc 06 C.3), sujeto a investigación 3.2

### Scope agregado por la reunión (no estaba en doc 06)

1. Seguimientos personalizados con contexto (MUST-HAVE julio)
2. Tracking de tiempo de cierre (NICE-TO-HAVE post-cutover)
3. Promociones rotativas A/B (NICE-TO-HAVE post-cutover)
4. Claude para imágenes (MUST-HAVE julio, sujeto a 3.2)

**Recomendación de scope MVP:** replicar funcionalidad actual en GHL + features #1 y #4. Métricas y A/B (#2, #3) post-cutover para no comprometer agosto.

### Timeline ajustado

- **Si §3 cierra antes del 1 junio** → inicio implementación ~15 julio (plan original mantenido)
- **Si §3 cierra después del 1 junio** → mover inicio a 25 julio (overlap Kommo aún viable hasta 26 agosto)

**Para retomar:** decile a Claude *"continuamos migración HPF, Etapa 2 cerrando"* y apuntá a `02_logica_validada/01_decisiones.md`.

---

## Hallazgos técnicos clave del análisis Opus

### Pipelines Kommo (13 totales)
- **Activo del agente:** `IA` (ID `11622596`) — único pipeline procesado por n8n
- **Legacy/manuales:** 12 pipelines paralelos (GENERAL, SANDALIAS BODAS, SANDALIAS XV AÑOS, Cilindros, Mandiles, Kit anticrudas, Pantuflas, Sandalia lisa, Happyfloops, XV AÑOS, BODAS, Reactivadores Genericos)
- Filtro explícito: nodo `No es IA` rechaza leads fuera del pipeline IA

### Etapas hardcodeadas en n8n (todas del pipeline IA)
- `89263340` Incoming leads
- `89263344` ETAPA 1 (saludo enviado)
- `93616832` ETAPA 2 (imagen del evento enviada)
- `93616836` ETAPA 3 (productos mostrados)
- `93616840` ETAPA 4 (cotización emitida) — **¿quién la mueve? AMBIGÜEDAD E.2**
- `91266100` atencion personalizada
- `91450360` confirmar pago
- `100395519` en producción
- `100395523` pago liquidación
- `142` / `143` Logrado con éxito / Ventas Perdidos
- 17 etapas R1-R5 sin/con info/ap (sub-pipeline de seguimientos)

### Arquitectura de agentes (7 LLMs identificados)
1. **AI Agent** (Router maestro) — devuelve `{step:N}` (357 líneas de prompt, 4 steps + ejemplos)
2. **AI Agent Starter** — saludo hardcodeado (split en 3 partes con waits 2s)
3. **AI Agent Main Image** — identifica evento, envía imagen + promo
4. **AI Agent Products** — devuelve JSON con productos + envía catálogo desde Airtable
5. **AI Agent Recolector** — vendedor (cotiza con tool CALCULADORA, deriva a humano con ATENCION_PERSONALIZADA)
6. **AI Agent Recolector1** — vendedor para input imagen (95% prompt idéntico — **REDUNDANCIA A.3**)
7. **Analyze image** — clasificador gpt-4o (5 productos válidos o `falso`)
+ helpers `Necesita Respuesta Especial`, `Message a model`, `Formatear mensaje1`

### Mecánica de envío
- Canal A (predominante): `POST /api/v2/salesbot/run` (legacy AmoCRM) — dispara salesbot Kommo con `bot_id`
- Canal B (alternativo): `POST amojo.kommo.com/v2/{chat_id}/sendMessage` — directo
- Los CURLs en Airtable son **plantillas**, n8n reemplaza IDs en runtime con datos del lead actual

### Persistencia (3 capas)
- **Redis:** debouncing (50s text / 15s imagen), keys = `contact_id` y `numero_telefono`
- **Postgres LangChain Memory:** historial conversacional, session_id = entity_id del lead
- **Kommo:** estado del lead (etapa actual)

### Estructura común sub-workflows seguimiento
Los 4 sub-workflows (Rebeca / Imagen / Cotización / 7pasos) comparten patrón:
```
Wait → Query Postgres (¿AI dijo X?) → IF → si no respondió, mover etapa + enviar mensaje + INSERT seguimiento → Wait → ...
```
Cadencias: 1h → 3h → ~8h → 24h. **REDUNDANCIA B.2** (consolidable a 1 workflow GHL con conditions por etapa).

### Reglas críticas inviolables (penadas de muerte)
1. Output Router debe ser JSON exacto
2. Sandalias solo mujeres
3. Mandiles solo Boda
4. No revelar peso del envío en kg
5. No modificar precios bajo presión del cliente
6. Solo número telefónico permitido: `3315948670`
7. Mensaje de saludo + mensaje de promo = NO MODIFICABLES

---

## Lista corta para Etapa 2 (10 preguntas críticas)

1. **D.1** — ¿Cómo funciona exactamente el `bot_id` de Airtable + el endpoint `salesbot/run`?
2. **D.3** — ¿Los textos completos de los re-engagement están en salesbots Kommo? Hay que exportarlos.
3. **D.4** — Estado de los 12 pipelines paralelos (¿qué se mantiene, qué se archiva?).
4. **D.7** — Exportar el workflow n8n `nkRBXbc4G0Cn67gY` (referenciado pero no en `03_workflows/`).
5. **E.1** — Comportamiento real del Router cuando lead da evento+producto en mismo turno (¿salta step_2?).
6. **E.2** — ¿Quién mueve el lead a `93616840` (ETAPA 4)?
7. **E.5** — ¿`Saludo PTE 1/2/3` son del Starter o re-engagement?
8. **E.7** — Tabla de precios consolidada (CSVs muestran $29, CURLs $30).
9. **F.1** — Aprobar consolidación pipeline IA: 31 → ~10 etapas en GHL.
10. **F.3** — Aprobar consolidación LLMs: 7 → 2 (Vendedor + Vision Classifier).
