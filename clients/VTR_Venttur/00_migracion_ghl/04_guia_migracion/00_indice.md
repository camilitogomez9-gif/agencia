# Etapa 4 — Guía de implementación paso a paso (VTR → GHL)

> **Para quién:** la agencia (implementador técnico). Mauricio/Max supervisan y proveen accesos + decisiones de cliente.
> **Prerequisito:** Etapa 3 completa — los 12 docs de `03_arquitectura_ghl/` (00-11) son la **fuente de verdad del "qué"**. Esta guía es el **"cómo"** y asume su lectura previa.
> **Método:** traducción quirúrgica del diseño, no rediseño. Cada paso se corrobora contra el **sistema real** (`00_inputs/`: 14 JSON de workflows, CSVs, snapshot 13,7 MB), no contra la prosa. No simplificar salvo lo ya marcado muerto/duplicado en `00 §6`.
> **Cutover confirmado:** **15-sep-2026.**

---

## ⏱️ Realidad de calendario (leer primero)

Hoy es **2026-09-07** → **T-8 días** al cutover. **Lo que la agencia controla ya está en buena parte hecho** (ver §🔄 Estado abajo): datos + estructura importados y validados en GHL, y las piezas del agente construidas en staging. Lo que resta en el camino crítico son las **dependencias que no controlamos** (WABA + plantillas Meta) y las validaciones de canal que necesitan un **número de test**. Por eso el foco de esta semana es **destrabar el WABA** y arrancar las plantillas (aprobación Meta 24-72h).

**La decisión B3 está tomada: Opción A — cutover completo** (cliente 2026-09-03). Todo migra el 15/9, sin olas. Es la decisión de mayor impacto sobre la fecha (§Decisión B3 abajo) y sube la exigencia del camino crítico.

---

## 🔄 Estado global a 2026-09-07 (leer segundo)

**✅ Hecho (la agencia, por API):** import de datos (2.295 opps · 6.316 contacts · 4.736 assignedTo reasignados · companies 266 · 61 duplicados borrados → **2.299 opps** finales); estructura GHL (56 custom fields + 20 pipelines incl. `OP · Bot Venttur` + 5 tags incl. `cualificado`); piezas del agente en **staging** (`3sLd7KY3o8I7NvXi`): context builder, sessionKey MX, tools `crear_contacto`/`elevar`; despachador tope-2 (`vrShEXQGGAo4FqAt`); clasificador Cualificado (`Xmyoewwa1W5gm1fy`); barrido interrumpida (`LrJuzU7qDeELWiAl`). Sandbox headless: (a)(b)(h)(i) validados. Decisiones cerradas: tope-2, `elevar`→Mauricio, criterio `Cualificado`.

**🔴 Falta (camino crítico, gated en terceros/canal):** decisión + traspaso del **WABA**; **plantillas Meta**; validación de canal con **nº de test** (B1/B2/B3/B4/C1); main real del canal + audio; 8 calendarios + confirmación/recordatorios; notificación del handoff (GHL-UI); rotar secretos.

**Fuente de verdad del estado de ejecución:** `05_ejecucion/REGISTRO-EJECUCION.md`. **Tareas del cliente centralizadas:** `06_docs/guia-pendientes-pre-traspaso-waba-2026-09-07.md`.

---

## Estructura de módulos

| # | Archivo | Cubre | Estimado |
|---|---------|-------|----------|
| 00 | `00_indice.md` | Este doc: camino crítico, gates, accesos, convenciones, decisión B3 | — |
| 01 | `01_sandbox_validacion.md` ⭐ | **Gate maestro.** 13 checks bloqueantes (+1 opcional) de plataforma GHL a validar antes del import | 3-5 hs |
| 02 | `02_setup_ghl_base.md` | Sub-cuenta, owners→usuarios, Contact + Opportunity custom fields, tags | 3-4 hs |
| 03 | `03_pipelines_ghl.md` | ~19 pipelines comerciales (etapas verbatim del snapshot) + 1 pipeline operativo del bot | 4-6 hs |
| 04 | `04_calendarios_y_agendamiento.md` | 8 calendarios (o fallback) + disponibilidad compartida + confirmación + recordatorios 24h/1h | 4-6 hs |
| 05 | `05_templates_meta_waba.md` | **Portabilidad WABA** + Message Templates + aprobación Meta + 3 faltantes | 3-5 hs + espera Meta 24-72h |
| 06 | `06_datos_preproceso_import.md` | Canonicalización + merge → ~8.575 Contacts + auditoría Clientify + carga Companies→Contacts→Opportunities | 8-12 hs |
| 07 | `07_n8n_agente_canal.md` | Main reconstruido + agente Mauricio + tools + audio + handoff | 8-10 hs |
| 08 | `08_n8n_despachador.md` | Despachador único (tope 2) + gate del rescate + Cerrada + interrumpida | 5-7 hs |
| 09 | `09_n8n_capi_formulario.md` | CAPI (se queda) + fix data-driven + repunte de formulario/landing a GHL | 3-5 hs |
| 10 | `10_programas_nuevos.md` | Deltas de los 3 huérfanos en todos los módulos + gate de assets del cliente | 4-8 hs (según assets) |
| 11 | `11_testing_precutover.md` | Plan E2E (sobre `testing-guide-v1`) — criterios en verde = prerequisito de cutover | 6-8 hs |
| 12 | `12_cutover.md` | Coreografía 15/9 con gates en secuencia + decisión B3 + rollback | 3-4 hs (día del cutover) |

**Total estimado:** ~55-80 hs de trabajo técnico (sin contar esperas de terceros: aprobación Meta, respuesta de portabilidad, entrega de textos/assets del cliente).

---

## Orden de ejecución / camino crítico

```
                    ┌─────────────────────────────────────────────┐
        01 SANDBOX  │  gate maestro — primero de todo (3-5 hs)     │
                    └───────────────┬─────────────────────────────┘
                                    │
   ┌────────────────────────────────┼──────────────────────────────────┐
   │  EN PARALELO desde el día 1 (dependen de terceros, lead time largo)│
   │                                                                    │
   │  05 WABA + templates ......... portabilidad (deadline VENCIDO, ver │
   │                                gates) + aprobación Meta 24-72h     │
   │  06 §auditoría Clientify ..... gate del import (qué NO se puede    │
   │                                migrar automático)                  │
   │  10 §textos/assets huérfanos . los aporta el cliente (riesgo B3)   │
   └────────────────────────────────┬──────────────────────────────────┘
                                     │
   SETUP GHL (orden fijo):  02 custom fields ─► 03 pipelines ─► 04 calendarios
                                     │
                            06 pre-proceso + import de datos (~8.575 Contacts)
                                     │
                            07 / 08 / 09  recableado n8n (14 workflows)
                                     │
                            11 testing E2E (verde = prerequisito de cutover)
                                     │
                            12 CUTOVER 15/9
```

- **`02` y las estructuras vacías de `03`/`05`** (crear pipelines/templates sin datos) se pueden empezar **en paralelo** al sandbox — no dependen de los comportamientos que valida `01`. Lo que espera al verde es la **carga de datos** (`06`) y el **cableado de lógica** (`07`-`09`).
- **`07` y `08`/`09` son paralelizables** si hay dos personas; si no, `07` (el canal) primero.
- **`10` no es un build aislado:** son los *deltas* de los 3 huérfanos que se aplican dentro de `02`/`03`/`04`/`05`/`07`/`08`. Se documentan juntos en `10` para que la dependencia de assets del cliente quede en un solo lugar visible.

---

## 🚦 Gates (dependencias que bloquean el cutover)

| Gate | Estado a 2026-09-07 | Bloquea | Dueño | Doc |
|---|---|---|---|---|
| **Sandbox validado** (01) | 🟡 **parcial** — headless OK ((a) match teléfono, (b) fecha→CF, (h) DND, (i) query por CF). Faltan **B1/B2/B3/B4/C1** (necesitan nº de test / calendario personal) | main real + audio + calendarios | la agencia | `01` |
| **Portabilidad WABA** | 🔴 **deadline propio 1/9 VENCIDO** — desambiguar YA el WABA `1931874540684022` (BM Venttur = portable / BM ManyChat = chip nuevo). Decisión pre-tomada del cliente: *si hay riesgo de downtime, chip nuevo* | número migrado vs chip nuevo → templates | **Cliente** (verificación 2 min en `business.facebook.com`) + la agencia | `05`, `portabilidad-numero-whatsapp-2026-08-18.md` |
| **Aprobación de templates Meta** | 🔴 arrancar YA — tarda **24-72h**; las 3 faltantes (`seg_dia_3/5/7_bs`) y toda template ausente de la WABA migrada se re-crean/re-aprueban | re-enganche (`09`) + recordatorios (`07`) | la agencia + Meta | `05`, `09 §7` |
| **Auditoría migrabilidad Clientify** | 🟢 **entregable existe** (`05_ejecucion/auditoria-migrabilidad-clientify.md`) — falta OK/decisión del cliente antes de apagar Clientify | descomisión Clientify (`12`) | Cliente (decide) | `06` |
| **Textos/assets de los 3 huérfanos** | 🟡 los aporta el cliente (`ronda-2 §7`) | scope completo de los 3 (`10`) → decisión B3 | **Cliente** | `10` |
| **OK cliente: tope de 2 toques + prioridad** | ✅ **OK dado** — despachador construido con tope-2 | despachador (`08`) | — | `08 §8`, `09` |
| **Criterio de `Cualificado`** | ✅ **determinado de los flujos vivos** (clasificador batch ~8h; 3 condiciones) + reconstruido (`Xmyoewwa1W5gm1fy`, tag) — NO era real-time del agente | pipeline operativo (`03 §5`) | — | `03 §5`, `08` |
| **OK cliente: fallback 1-cal-por-asesor** 🔶 | 🟡 solo si el sandbox C1 falla — contradice P2 | modelo de calendarios (`04`) | **Cliente** | `01 C1`, `04` |
| **Notificación del handoff (Notify:0)** | 🔴 build **GHL-UI** (Workflow nativo, no creable por API) — email+app a Mauricio/Max; no hay cred de email en n8n VTR | handoff (`07`) | la agencia (GHL-UI) | `07`, REGISTRO B-N1 |
| **Secretos rotados** | 🔴 antes de cualquier handoff | higiene | la agencia | ver abajo |

> **Nota sobre el 1/9:** el deadline de portabilidad ya pasó. Esto **no** frena nada de lo ya hecho, pero sí presiona: o se confirma esta semana que el WABA es portable, o se activa la decisión pre-tomada (chip nuevo → todas las templates se re-aprueban, +24-72h, el número arranca a 250 conv/24h). Escalarlo con el cliente es lo primero (ver §📅 Calendario).

---

## 📅 Calendario — fechas importantes

Hoy **2026-09-07** · cutover **15/9/2026** (T-8).

| Cuándo | Qué | Owner |
|---|---|---|
| **Hoy (7/9)** | Cerrar el runbook (esta sesión); dejar listo el mensaje + la lista de tareas del cliente | la agencia |
| **Mañana (8/9)** | Enviar el mensaje a Mauricio por el grupo + compartir el agente por Telegram; pedir los 4 datos del WABA + prereqs | la agencia → Cliente |
| **Esta semana (~9/9)** | Cerrar la decisión del WABA (portable vs chip). Si no se confirma la portabilidad → **chip nuevo YA** | Cliente + la agencia |
| **En cuanto se decida el WABA** | Arrancar las plantillas Meta — **aprobación 24-72h, no se puede comprimir** | la agencia + Meta |
| **Apenas haya nº de test** | Validar canal (B1/B2/B3/B4/C1) → reconstruir main real + despachador a producción + audio | la agencia |
| **Continuo hasta el cutover** | 8 calendarios + confirmación/recordatorios (necesita textos del cliente), notificación de handoff (GHL-UI), rotar secretos, testing E2E en verde | la agencia + Cliente |
| **Ventana de bajo tráfico pre-15/9** | Traspaso del WABA a GHL (downtime de minutos en escenario A) | la agencia + Cliente |
| **15/9** | **Cutover** — Opción A, todo de una | Todos |
| **15/9 +48h** | Monitoreo post-cutover → cierre de la migración | la agencia |

> ⚠️ **Regla de la fecha:** si algún gate (🚦 arriba) no va a llegar, la charla de "correr la fecha" se abre con el cliente **antes del D-3 (12/9)**, no el día del cutover.

---

## 🔐 Secretos a rotar (antes del handoff)

Detectados hardcodeados en los JSON de `00_inputs/` (`ESTADO` hallazgo 11, `00 §7.8`). Rotar **antes** de entregar accesos:

- Bearer de **ManyChat** (en varios workflows) — muere con ManyChat, pero rotar igual hasta el cutover.
- API key de **OpenAI** (agente + whisper) — mover a credencial de n8n.
- Token de **Clientify** — muere con Clientify; rotar hasta la descomisión.
- **`access_token` de Meta por-programa** expuesto en el CSV `Programas CAPI` — rotar (el CAPI se queda, `05`).
- Tokens de **pixel Meta** en los JSON del CAPI.

---

## Convenciones usadas en esta guía

- `[VALOR]` → placeholder que completás con el valor real
- ⚠️ → paso crítico, no saltear
- ✅ → checkpoint de verificación (confirmar antes de continuar)
- 📋 → copiar/pegar literal
- 🔧 → fix de un bug de origen (no es rediseño: es reparar lo que ya debía funcionar)
- 🔶 → decisión que **requiere OK del cliente** (no solo resultado técnico)
- 🔍 → endpoint/comportamiento de GHL a confirmar en el sandbox antes de asumirlo
- Nombres de stages/campos GHL en **negrita** · IDs de n8n/GHL en `monoespaciado`
- **Formato de entrega n8n** (estándar interno): workflow nuevo → JSON importable; EDIT en producción → guía paso a paso de nodos (no pre-editar producción). Nodo suelto → siempre envuelto en `{"nodes":[...],"connections":{}}`.

> ⚠️ **Gotcha de plataforma confirmado (sandbox 2026-09-03):** la API v2 de GHL rechaza el `User-Agent` por defecto de las librerías con **Cloudflare 1010** — **todo HTTP a GHL** (scripts de import + nodos HTTP Request de n8n) debe mandar un UA browser-like. Otros hallazgos de la corrida en `01 §Resultados`: Companies = `/businesses/`, búsqueda por `POST /contacts/search` con filtro anidado, y `OPPORTUNITY_NO_DUPLICATE` a resolver antes del import.

---

## Accesos necesarios

| Recurso | Quién lo provee | Dónde se usa |
|---|---|---|
| Sub-cuenta GHL (✅ creada) + `locationId` | Cliente/la agencia | 01-12 |
| Private Integration token GHL (scopes en `01 §0`) | la agencia (crear) | 01, 02, 03, 04, 06 |
| WABA de Venttur + desambiguación del BM (`1931874540684022`) | Cliente | 05 |
| Número del bot (`+52 1 33 2627 4502`, a confirmar contra el `1944 2476`) | Cliente | 05 |
| Export de Clientify (contacts + deals + companies + CF) | ya en `vtr-data-snapshot-2026-07-24.json` | 06 |
| CSVs de Airtable (leads, folios, programas, mensajes) | ya en `00_inputs/airtable-csvs/` | 06, 09 |
| Credenciales Supabase (memoria, sin cambios) | ya en n8n | 07, 08 |
| OpenAI API key (agente gpt-4o + whisper) | la agencia | 07 |
| Owners reales de Clientify → usuarios GHL (Rodrigo, Andrés, Mauricio, Max, Niza…) | Cliente confirma el mapeo | 02, 03 |
| Textos de confirmación/recordatorio (hoy en Clientify) | Cliente | 04 |
| Textos/assets de los 3 huérfanos | Cliente | 10 |
| Meta Business Manager (para templates + portabilidad) | Cliente | 05 |

---

## ⚖️ Decisión B3 — ✅ CONFIRMADA: Opción A (cutover completo)

**El cliente eligió Opción A el 2026-09-03.** El 15/9 sale **todo de una**: canal + agente + calendarios + **todo el pipeline comercial migrado** (6.968 contactos + 2.338 deals + 266 companies) + **los 3 huérfanos completos**. No hay olas — la migración es única.

> **la agencia había recomendado Opción B** (por olas) porque a T-12, con las 3 dependencias de terceros, protege mejor la fecha. El cliente optó por A. **Se respeta y se ejecuta A**, con la nota de riesgo abajo.

**Qué implica A (y qué hay que asegurar sí o sí para el 15/9):**
- **Migración completa de datos** (`06`): Companies + los ~8.575 Contacts + los 2.338 deals en los 20 pipelines, todo cargado y reconciliado **antes** del cutover. La reconstrucción de deals es en buena parte manual (`06 §6.3`) → arrancar temprano.
- **Auditoría de migrabilidad de Clientify** (`06 §6.3`) cerrada antes de apagar Clientify.
- **Los 3 huérfanos completos** (`10`): con nurturing/rescate/templates propios → **dependen de los textos/assets del cliente**. Con A no hay "mínimo viable" que difiera — todo entra. **Conseguir los assets YA.**
- **Todos los gates** (§🚦) en verde antes del D-day.

⚠️ **Riesgo (declarado, no bloqueante):** a T-12 el camino crítico queda tenso — WABA (deadline vencido), templates Meta (24-72h), reconstrucción manual de 2.338 deals, y los assets de los 3 huérfanos, todos convergiendo al 15/9. Mitigación: arrancar hoy las dependencias de terceros (§🚦) + la migración de datos en paralelo al sandbox. Si un gate no llega, la conversación de "correr la fecha" se abre con el cliente **antes** del D-3, no el día de.

---

## Referencias cruzadas a la arquitectura (Etapa 3)

Cada módulo referencia su doc de diseño:

- Sandbox → `03_arquitectura_ghl/00_overview.md §7.10`
- Setup / custom fields / tags → `02_datos_contactos_identidad.md`, `04_datos_campos_tags.md`
- Pipelines / opportunities / estado → `03_datos_pipeline_deals_estado.md`
- Calendarios / confirmación / recordatorios → `07_agendamiento_calendarios.md`
- WABA / templates / canal / agente → `06_canal_whatsapp_y_agente.md`
- Pre-proceso / import de datos → `01_taxonomia_programas.md` (remapeo) + `02` + `03`
- Agente / main / tools → `06_canal_whatsapp_y_agente.md`
- Despachador / nurturing / rescate → `09_nurturing_rescate_reengagement.md`
- CAPI / atribución → `05_datos_capi_atribucion.md`
- Formulario / landing → `08_workflows_n8n.md` (wf4) + `10_programas_nuevos.md`
- 3 huérfanos → `10_programas_nuevos.md`
- Catálogo de los 14 workflows → `08_workflows_n8n.md`
- Flujo end-to-end → `11_flujo_end_to_end.md`

---

*Etapa 4, módulo índice. Corrobora fechas contra el calendario real (hoy 2026-09-03, T-12 al cutover). 2026-09-03.*
