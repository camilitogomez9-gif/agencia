# Sincronización de la migración VTR — 2026-09-16

> ⚠️ **REEMPLAZADO por `06_docs/guia-recta-final-cutover-2026-09-16.md`** (2026-09-16 tarde). Esa guía es la fuente de verdad operativa única hasta el 27/9 EOD. Este doc queda como snapshot histórico del estado del merge inicial (Bloques 0-5) — no actualizar acá, ir a la guía recta final.

> **Doc temporal · sunset date: 26/9/2026 post-cutover.** Después de esa fecha, este archivo se archiva o se borra y el estado permanente vuelve a `ESTADO_MIGRACION.md` + `05_ejecucion/REGISTRO-EJECUCION.md`. No documentar decisiones de largo plazo acá — este doc solo consolida el estado durante la ventana de sincronización pre-cutover.

## Contexto

Tres líneas de trabajo paralelas convergieron el 16/9:

1. **Camilo (la agencia, cuenta propia)** — 03-07/9 ejecutó la migración con scripts (todo committeado a main con prefijo `auto:`). 08-11/9 consolidó dos tracks y produjo 8 artefactos que **nunca se pushearon al repo**. El 16/9 nos pasó un `.zip` con el estado completo del 11/9 (`/Users/camilo/Downloads/_RECONCILIACION-2026-09-11.zip`, 242 archivos, 31 MB).
2. **la agencia + Claude (repo, este WS)** — 15-16/9 hicieron el incidente Nahe (Fase 3-6) y actualizaron los docs de arquitectura GHL (Fase 7). Todo committeado en main.
3. **Reunión con cliente (15/9)** — desbloqueó 12 puntos, resolvió la ambigüedad del WABA (Escenario A confirmado), y ajustó el cutover al 18-19/9 con testing hasta el 25/9. Transcript completo en la sesión de Fathom del 15/9.

Este doc consolida todo lo que hay que saber para llegar al cutover con el WS coherente.

## Bloque 0 · guardrail Nahe replicado en el staging n8n · ✅ HECHO 2026-09-16 17:02 UTC

El workflow staging que Camilo dejó operativo (`3sLd7KY3o8I7NvXi`, 12 nodos) fue construido antes del incidente Nahe (15/9). No tenía ni la Regla ABSOLUTA #8 "No agendo yo" ni el guardrail `Detectar promesa fantasma`. Si el cutover 18-19 saliera desde ese estado, Nahe se repite en GHL.

**Aplicado**: 4 edits quirúrgicos al `systemMessage` del `Agente IA WPP` (47.462 → 50.188 chars) + inserción del nodo Code `Detectar promesa fantasma` entre `Agente IA WPP` y `Enviar Telegram` (12 → 13 nodos). Detector adaptado al pipeline sin splitter — trabaja sobre `$json.output` (texto crudo) en vez de `{parte1, parte2, parte3}`. Lee `programa_interes` del custom field `xK2NFqtz1DYUw3gYdn8I` del Contact GHL. Fallback ante duda: `promo.venttur.com/agendar-ema` (Rodrigo).

**Verificaciones**:
- 8/8 tests golden del detector staging (`03_workflows/staging-2026-09-16-post-replica-guardrail/test-detector-staging.js`).
- 3/3 smoke test contra OpenAI con el prompt vivo del staging: mensajes verbatim de Nahe ("Si el lunes a las 11 podrás?", "Hola buenos días estoy lista", "no, mejor tú me dices qué día") ahora responden con `promo.venttur.com/AAFamilia-Agendar` en vez de prometer coordinar.

**Snapshots**:
- Pre: `03_workflows/staging-2026-09-16-pre-replica-guardrail/main-venttur-staging.json` · sha256 `4103e04a6a183561…`
- Post: `03_workflows/staging-2026-09-16-post-replica-guardrail/main-venttur-staging.json` · sha256 `44c99ff982952bd5…`
- Detector + tests versionados en el snapshot post.

**Pendiente iterativo (no bloquea el cutover)**: replicar en el staging la alerta P1 Telegram + el INSERT en `vtr_phantom_interceptions` que sí existen en el vivo. El flag `_phantom_promise_intercepted: true` queda en el runData de cada ejecución y es inspeccionable vía API n8n.

## Bloque 1 · integración del zip de Camilo · ✅ HECHO 2026-09-16

### Archivos NUEVOS copiados al WS (14)

- `_RECONCILIACION-2026-09-11.md` (raíz del cliente) — explica la consolidación de dos tracks
- `00_migracion_ghl/PENDIENTES-MIGRACION-2026-09-11.md` — lista viva de pendientes (20 items, ver §Pendientes consolidados abajo)
- `06_docs/clientify-que-respaldar-antes-de-apagar.md`
- `06_docs/hallazgo-cruce-agenda-seguimiento-2026-09-11.md`
- `06_docs/plan-rotacion-secretos-2026-09-11.md`
- `06_docs/plantillas-meta-borradores-2026-09-11.md` — 16 plantillas Meta redactadas
- `06_docs/plantillas-meta-nurturing-2026-09-11.md` — plantillas de nurturing (bonus no declarado)
- `06_docs/guia-reunion-max-mauricio-pre-cutover.md`
- `06_docs/pedido-al-cliente-2026-09-11.md`
- `06_docs/pendientes-y-dependencia-waba-2026-09-11.md`
- `06_docs/incidente-mx-sessionkey-2026-06-30.md`
- `03_workflows/venttur-staging-agent-cerrada-v1.json` — workflow con la tool `cerrar_conversacion`
- `CLIENT_INFO-migracion-real.md` — versión actualizada del CLIENT_INFO (adoptar como base en Bloque 5)

### Archivos SUPERSEDED (NO copiados)

Según `_RECONCILIACION-2026-09-11.md §Archivos del track divergente`, estos son del track descartado (bot duplicado de ManyChat) y **no se usan como base**. Se mencionan acá solo para trazabilidad. Se pueden re-consultar en el zip original si se necesita algo puntual.

- `00_migracion_ghl/04_guia_implementacion/` (13 archivos, guía M1-M9)
- `00_migracion_ghl/especificaciones-waba-traspaso.md`
- `03_workflows/venttur-main-GHL-v1.json` (tiene OpenAI key hardcodeada — gitignored en la carpeta original)
- `03_workflows/wf-meta-capi-GHL-v1.json` + `wf-meta-capi-GHL-checklist.md`
- `03_workflows/wf-rescate-post-link-GHL-v1.json` + `wf-rescate-post-link-GHL-checklist.md`

### Archivos con conflicto que quedan sin merge (mi versión gana)

Los 4 docs de arquitectura/guía que edité el 16/9 (Fase 7) contienen mis secciones nuevas que Camilo no vio (§9 en `03_arquitectura_ghl/06`, §6 en `03_arquitectura_ghl/07`, checkpoints en `04_guia_migracion/07 §7.7`, §11.3.bis en `04_guia_migracion/11`). La versión de Camilo del 11/9 no tiene esas secciones. Mantengo mis versiones.

`ESTADO_MIGRACION.md` idem: la versión del WS (16/9) es más completa que la del zip (11/9) — incluye la sección "Incidente Nahe (15-16/9/2026) — contrato de diseño heredado" de Fase 7.

### Nota sobre "la agencia" vs "la agencia"

El zip de Camilo tiene aplicado el scrub-identidad (`la agencia` → `la agencia`, `la agencia` → `Camilo`) porque se lo generamos así para pasárselo (política estándar de handoff en la agencia, ver `scripts/utilities/scrub-identidad.py`). El WS interno mantiene "la agencia" y "la agencia" originales. Los 14 archivos NUEVOS que copié quedan con "la agencia" / "Camilo" — no invierto el scrub para no romper referencias legítimas a Camilo (él escribió esos docs). El WS queda con nomenclatura mixta hasta el próximo pase de higiene general (fuera de scope de esta sincronización).

## Bloque 5 · pendientes de merge (CLIENT_INFO y REGISTRO-EJECUCION)

Estos dos quedaron identificados para hacer en un pase separado (menos crítico que Bloque 0-4):

- **`CLIENT_INFO.md`** — versión WS del 26/8 (30 KB, con contexto del reporte de agosto y cutover 15/9), versión zip `CLIENT_INFO-migracion-real.md` del 11/9 (30 KB, con estado post-consolidación). Merge sugerido: adoptar la del zip como base + APPEND incidente Nahe + Fase 6 (alertas P1/P2 + tabla `vtr_phantom_interceptions`) + Bloque 0 (staging con guardrail replicado). Actualizar fecha de cutover a 18-19/9.
- **`REGISTRO-EJECUCION.md`** — versión WS del 07/9 (42 KB), versión zip del 11/9 (42 KB, tiene 4 días más de log de Camilo). Adoptar la del zip como base + APPEND entradas de 15-16/9 (incidente Nahe, Fase 3-7, Bloque 0). Timeline cronológico, atribución por sección.

## Pendientes consolidados hacia el cutover (18-19/9)

Consolida `PENDIENTES-MIGRACION-2026-09-11.md` (Camilo) + desbloqueos de la reunión 15/9 + trabajo Nahe/Fase 6.

### 🔴 Bloqueantes reales del cutover

| # | Tarea | Owner | Estado tras 15-16/9 |
|---|---|---|---|
| N1 | **WABA `1931874540684022` — desambiguar y portar** | [CL] | ✅ RESUELTO 15/9: Escenario A confirmado (Venttur compró el número, no ManyChat). Portable. Trigger: iniciar migración BSP a GHL. |
| N2 | **Landings de aventureras** (~100-125 landings × 5 calendarios) | [J] + [CL] | 🔴 NUEVO desbloqueo 15/9. Aún no diseñado. Ver Bloque 2 del plan `~/.claude/plans/perfecto-antes-de-cerrar-zazzy-twilight.md`. Puede requerir 1-2 días de reconstrucción; si no, el cutover 18-19 se hace sin trazabilidad de aventureras. |
| N3 | **Subir 16 plantillas Meta + aprobación 24-72h** | [J] + [M] | 🟡 Plantillas redactadas por Camilo (`06_docs/plantillas-meta-borradores-2026-09-11.md`). Falta subir a Meta apenas WABA quede migrada. Deadline duro: aprobación antes del cutover. |
| N4 | **Prereqs del número tras portar**: desactivar 2FA (durante migración), display name aprobado, verificación de negocio, NO instalar app WhatsApp en celular 2FA | [CL] | 🟡 2FA ya configurado, chip 2FA-only sin WhatsApp instalado (confirmado en reu 15/9). Falta reconciliar régimen "desactivar/reactivar 2FA" con el que ya tiene. Verificación de negocio pendiente. |
| N5 | **Testing E2E completo** (todos los subsistemas en verde) | [J] | 🟡 Guía en `04_guia_migracion/11_testing_precutover.md`, incluyendo §11.3.bis Regresión del incidente Nahe (7 casos N1-N7). Correr pre-cutover. |
| N6 | **Traspaso del número + cutover** | [J] + [CL] | 🟡 Fecha 18-19/9. Downtime de minutos si porta la WABA. |

### 🟡 Se puede avanzar sin el número

| # | Tarea | Owner | Estado |
|---|---|---|---|
| S1 | **Aplicar + probar `cerrar_conversacion`** | [J] | Snapshot en `03_workflows/venttur-staging-agent-cerrada-v1.json`. El staging vivo ya lo tiene como tool. Falta re-verificar con el bot. |
| S2 | **Terminar el despachador** (carril nurturing + política de históricos + paginación) | [J] | Gated en las plantillas de N3. |
| S3 | **Rotar secretos** (OpenAI key n8n · Meta CAPI Airtable) | [C] OpenAI · [CL] Meta | Guía: `06_docs/plan-rotacion-secretos-2026-09-11.md`. |
| S4 | **Notificación del handoff** (workflow GHL-UI) | [J] + [CL] | Falta mails/chat ids del equipo. |
| S5 | **Verificar cruce `Agenda` / `Seguimiento agenda`** en ManyChat | [C] o [J] | Del hallazgo del 09-11 (`06_docs/hallazgo-cruce-agenda-seguimiento-2026-09-11.md`): los flows están cruzados por nombre. Antes de tocar esos 2 flows. |
| S6 | **Crear los 8 calendarios (shells) + conectar los personales de asesores** | [J] crea · [CL] conecta | Depende de C1 (disponibilidad compartida) y de acceso a Google Calendar de Rodrigo y Andrés (Mauricio va a compartir credenciales, decisión 15/9). |
| S7 | **Respaldar Clientify** (chat, adjuntos, automatizaciones) | [CL] | Aviso: `06_docs/clientify-que-respaldar-antes-de-apagar.md`. |
| S8 | **Decisión de dominio destino GHL** | [CL] | Cliente aporta subdominio (study.venttur.com o go.venttur.com o similar). `promo.venttur.com` muere con Clientify. |
| S9 | **Handoff MCP/API PIT para Camilo** | [J] | Camilo pidió instrucciones para conectar Cloud Code a GHL. PIT es la vía rápida. Falta doc `06_docs/handoff-camilo-mcp-ghl.md`. |
| S10 | **Recontact policy post-cutover** | [J] | Del 15/9: solo re-engagement de leads con `Link asesoría enviado = true` + `Agendan cita = false`. NO spam a los 5.000+. Falta documentar en `03_arquitectura_ghl/09_nurturing_rescate_reengagement.md`. |

### ✅ Resueltos en la reunión 15/9 (no requieren acción adicional)

- **Diego sale** del ruteo automático. Solo Rodrigo y Andrés como asesores activos.
- **Rodrigo** = Internados / Año Académico con Familia / Summer Camp.
- **Andrés** = Pathway / Gap Year (idiomas).
- **Cualificado** = TAG del contacto (no etapa del pipeline). Confirmado por el cliente.
- **Modelo del agente** = gpt-4o (no se cambia por ahora).
- **Access a Clientify** = 3 accesos separados (Mauricio + Rodrigo + Andrés). Mauricio comparte credenciales.
- **Cutover** = 18-19/9, testing hasta 25/9, Clientify renueva 26-27/9.

## Documentos vivos que quedan sin actualizar en esta sincronización

Los siguientes docs quedan como deuda documental para un pase de higiene post-cutover (o antes si hay tiempo):

- Fechas de cutover en `04_guia_migracion/12_cutover.md`, `04_guia_migracion/05_templates_meta_waba.md §5.5` — todos siguen diciendo 15/9.
- WABA marcado como cerrado en `03_arquitectura_ghl/06 §7`, `04_guia_migracion/05 §5.0/§5.1`, `12 §12.2`, `06_docs/portabilidad-numero-whatsapp-2026-08-18.md`.
- Cualificado como TAG en `03_arquitectura_ghl/03_datos_pipeline_deals_estado.md` (todavía figura como etapa).
- Recontact policy en `03_arquitectura_ghl/09_nurturing_rescate_reengagement.md`.
- Landings de aventureras en `03_arquitectura_ghl/07_agendamiento_calendarios.md` (contradicción con §1/§5 · 8 calendarios fijos).
- Dominio destino GHL placeholder en `07 §5` y `08 §banderas`.
- `CLIENT_INFO.md` — merge del `-migracion-real` con notas Nahe/Fase 6 (Bloque 5).
- `REGISTRO-EJECUCION.md` — adoptar body del zip + APPEND Nahe/Fase 6/Bloque 0 (Bloque 5).

## Referencias cruzadas

- Plan de sincronización: `~/.claude/plans/perfecto-antes-de-cerrar-zazzy-twilight.md`
- Reconciliación tracks (Camilo): `_RECONCILIACION-2026-09-11.md`
- Pendientes vivos (Camilo): `00_migracion_ghl/PENDIENTES-MIGRACION-2026-09-11.md`
- Incidente Nahe: `06_docs/incidente-nahe-2026-09-15.md`
- Barrido de cohorte Nahe: `06_docs/barrido-leads-promesa-fantasma-2026-09-16.md/csv`
- Contrato Fase 7 GHL: `03_arquitectura_ghl/06 §9`, `07 §6`, `04_guia_migracion/07 §7.7`, `11 §11.3.bis`
- Staging con guardrail (Bloque 0): `03_workflows/staging-2026-09-16-post-replica-guardrail/`
- WABA portabilidad: `06_docs/portabilidad-numero-whatsapp-2026-08-18.md`
- Handoff MCP/API PIT (Camilo): `06_docs/handoff-camilo-mcp-ghl.md` (pendiente crear)

## Sunset

Este doc se archiva o se borra el **26/9/2026** (día después del cutover completo + ventana de testing). El estado permanente vuelve a:
- `00_migracion_ghl/ESTADO_MIGRACION.md` (estado general)
- `00_migracion_ghl/05_ejecucion/REGISTRO-EJECUCION.md` (log ejecutivo)
- `CLIENT_INFO.md` (contexto operativo del cliente)
