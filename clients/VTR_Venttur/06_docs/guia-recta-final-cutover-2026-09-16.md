# Guía recta final · cutover VTR → GHL

**Ventana operativa:** 2026-09-16 → 2026-09-27 EOD (fin de vida Clientify). **Hoy: 2026-09-20 (D-6, sábado).**
**D-day:** **viernes 26/9** (confirmado por la agencia 19/9). **Clientify muere:** sábado **27/9 EOD**. La ventana 26 → 27 preserva 24h de rollback antes de perder Clientify.
**Fuente de verdad operativa única** hasta esa fecha. Reemplaza a `SINCRONIZACION-2026-09-16.md` (queda archivado como snapshot). Post-cutover el estado permanente vuelve a `ESTADO_MIGRACION.md` y `05_ejecucion/REGISTRO-EJECUCION.md`. Post-mortem separado en `06_docs/postmortem-cutover-2026-09.md` (a crear post-cutover).

> **⚡ Bloqueantes de cutover al 20/9 (D-6):** 2 de 3 grandes bloqueantes **CAÍDOS** — **B-07 plantillas Meta ✅ CERRADO 19/9** (11/11 APPROVED, incluyendo `seguimiento_ema_dia_10_3`), y **contactos GHL ✅ CERRADO 17/9**. Quedan **3 bloqueantes vivos**: WABA BSP migration (cliente, 20-22/9) · landings 6 paths + 23 flujos Rodrigo (Camilo, 21-24/9) · test §07 hidden fields (la agencia, 22/9). Ver §00 semáforo.

Se abre a las 08:00 pensando **"¿qué falta para hoy?"** — no "¿qué está hecho?".

> **Cambio de fecha 17/9 → 26/9:** el D-day original era 18-19/9. Se corrió a 26/9 por dependencias de terceros (WABA BSP migration + 8 plantillas Meta en cola de aprobación) que no cerraron a tiempo, y para preservar la ventana de rollback antes de que Clientify caduque el 27/9. Todas las secciones "próximas 36 horas / D-day 18/9" se recalibraron a **próximos 7 días / D-day 26/9**.

---

## 🎯 MVP absoluto (leer primero)

Post-conversación con el usuario el 16/9 PM se recorta el scope. **Solo estos 8 items bloquean el cutover.** El resto (§16 al final) es Nice to have — se puede diferir sin bloquear el go-live.

**Los 5 que definió el cliente:**

| # | Item | Estado | Owner | Bloqueante para |
|---|---|---|---|---|
| 1 | Migrar landings de Clientify (~100-125 aventureras) + calendarios | 🔴 no iniciada | la agencia (Camilo) | Cutover — sin landings los ads mueren |
| 2 | Verificar que el agente Telegram staging responda igual que el vivo | 🔴 diferencia reportada | la agencia (la agencia) | Cutover — sin paridad no hay confianza |
| 3 | Traspaso WABA (número `+52 1 33 2627 4502` de ManyChat → GHL) | 🔴 no iniciado | cliente + la agencia | Cutover — sin WABA no hay canal |
| 4 | Exports y backups Clientify + ManyChat + n8n vivo | 🟡 parcial | la agencia | Cutover — sin backup no hay rollback |
| 5 | Verificar contactos GHL tengan info completa | ✅ auditado 16/9 + fixes al 100% aplicados 17/9 | la agencia (la agencia) | ✅ CERRADO |

**Los 3 críticos adicionales (que la agencia detectó y confirmó):**

| # | Item | Estado | Owner | Justificación |
|---|---|---|---|---|
| 6 | Decidir + aplicar el prompt del cutover (v2.1 → v2.2 sin Diego) | 🟡 v2.2 lista 16/9 PM | la agencia (la agencia) | Sin esto, el ítem 2 no tiene benchmark |
| 7 | Preservar `session_id = teléfono` normalizado en el cutover | 🟡 documentado | la agencia (Camilo) | Sin esto todos los leads activos re-saludan de cero |
| 8 | Handoff notification funcionando (bot eleva → equipo se entera) | 🔴 pendiente | la agencia + cliente | Mismo patrón que rompió a Nahe |

### Detalle por item

**Item 1 · Landings + calendarios** — sección §07 (test hidden fields) + §04 §B9 landings aventureras. Owner: Camilo con acceso Clientify de Rodrigo/Andrés/Mauricio (confirmado por usuario).

**Item 2 · Paridad agente Telegram** — usuario reportó "no responde igual que el actual". La causa probable: el staging tiene el prompt **base pre-Nahe (v2.0 backup, ~48K chars)** mientras que el vivo tiene **v2.1 post-Fase 3 (~50K chars con Regla ABSOLUTA #8)**. **Fix: aplicar v2.2 (v2.1 sin Diego) al staging.** Backup del vivo actual en `04_agents/agente-venttur-system-prompt-v2.0-live-backup-2026-09-16.md`. Comparativa completa en §17.

**Item 3 · Traspaso WABA** — **Runbook operativo listo:** `06_docs/runbook-bsp-migration-waba-2026-09-19.md` (8 clicks GHL + 4 precondiciones verificables + 5 errores comunes con fix + rollback rápido §7.1). Diagnóstico previo: `06_docs/portabilidad-numero-whatsapp-2026-08-18.md`. Si Escenario A falla → chip nuevo (Escenario B), retrasa cutover ~72h.

**Item 4 · Exports y backups** — **Runbook operativo listo para Clientify:** `04_guia_migracion/12a_backup_clientify_runbook.md` (7 elementos con paso-a-paso técnico + checklist verificación pre-GO). Snapshot n8n vivo del 16/9 ✅ + snapshot D-1 (`vivo-2026-09-25-pre-cutover`) pendiente. Ver §09 (checklist rápido) y §13 (snapshots).

**Item 5 · Contactos GHL — ✅ CERRADO** (auditado 16/9 + fixes al 100% aplicados 17/9). Reporte completo: `06_docs/auditoria-contactos-ghl-2026-09-16.md`. Estado post-fix (6.328 contactos):
- ✅ **95.7% con teléfono** (filtro API global).
- ✅ **`lastName` cobertura: 19% → 63.6%** post-split (1.117 nombres splitteados, 97 instituciones skippeadas — ej. `LILIANA ROJI` → `LILIANA` + `ROJI`; `HAVERGAL COLLEGE` preservado como institución).
- ✅ **`folio` cobertura: 0% → 522 contactos** (450 por email + 72 retry por teléfono).
- ✅ **`agendan cita` cobertura: 0% → 406 contactos** (match por teléfono canonicalizado, no era necesario Airtable API — el CSV Leads ya tenía el phone en la columna `id`).
- ✅ **`fbclid` cobertura: 0% → 50 contactos** (Facebook click IDs de leads CAPI Meta).
- ✅ **Verificación con GET directo** (contact `uFx22fuKbExjkkUssx37`, Mauricio García): `Agendan cita=['true']`, `programa_interes='Internados'`, `link_enviado=['true']`, `firstName='Mauricio'`, `lastName='García'`. Todos los CFs operativos.
- 🟡 **Casos residuales fuera de alcance por API (~23):** teléfonos que difieren entre Airtable y GHL (ej. Milka con `+5218998994485` en Airtable vs `+5218995037621` en GHL — el ETL usó Clientify). No arreglable sin decisión manual.
- 🟡 **Programa_interes 31%, estado_conversacion 0.2%** — coincide con el origen Airtable/Clientify (esos campos ya estaban vacíos en el origen, NO es bug del import). **Recomendación operativa:** filtrar en workflows de outreach/nurturing/rescate post-cutover para excluir contactos migrados sin actividad reciente hasta que interactúen 1 vez con el bot nuevo.

**Item 6 · Prompt cutover** — ✅ v2.2 lista. Cambios v2.1 → v2.2: Diego eliminado del contexto del equipo + los 6 lugares operativos donde aparecía; los 2 links `Estudiar-y-Trabajar-en-Australia` ahora asignan a **Andrés**. Backup v2.1 conservado. Aplicar al staging + al vivo antes del cutover.

**Item 7 · Session preserve** — la normalización 52↔521 ya está aplicada en el vivo n8n (nodo `canonPhone`). Verificar que la lógica de sessionKey del bot GHL sea equivalente. Documentado en `03_arquitectura_ghl/06 §canonPhone` y `04_guia_migracion/07 §7.7`.

**Item 8 · Handoff notification** — sin esto, un lead que el bot eleva puede quedar como Nahe (esperando sin respuesta). **Mini-runbook en §20.** Definir: (a) qué eventos elevan (Meta ads sin match, promesa fantasma interceptada por el guardrail, lead pide humano); (b) canal (mail a Mauricio+Max, Telegram al grupo, ambos); (c) template del mensaje con contexto. Ya existe el patrón Fase 6 alertas P1 vía Telegram — replicable como fallback si el cliente no entrega mails/chat ids a tiempo.

---

### Hecho el 16/9 PM (por API/MCP)

- ✅ **Snapshot n8n vivo pre-cutover**: 13 workflows con sha256 en `03_workflows/vivo-2026-09-16-pre-cutover/`.
- ✅ **Auditoría contactos GHL** (6.328 contactos, muestra 1.000): `06_docs/auditoria-contactos-ghl-2026-09-16.md`. Hallazgo revisado: los 2 rojos originales estaban exagerados (sesgo de muestreo). Los CFs "vacíos" en la muestra inicial estaban poblados correctamente en GHL (verificado con GET directo sobre contactos concretos).
- ✅ **Fix prompt Diego**: v2.2 creada en `04_agents/agente-venttur-system-prompt-v2.2.md`. 6 cambios quirúrgicos, 0 menciones residuales a Diego. Backup v2.1 conservado.
- ✅ **Fix nombres GHL — split firstName/lastName (1.ª ronda)**: 1.117 contactos con nombre split correctamente (`LILIANA ROJI` → `LILIANA` + `ROJI`). 97 instituciones saltadas. Cobertura `lastName`: 19% → **63.6%**. Script en repo: `00_migracion_ghl/05_ejecucion/scripts/fix-nombres-ghl-2026-09-16.py`.
- ✅ **Fix CF `folio` desde Airtable (1.ª ronda)**: 450/481 contactos (match por email). Script: `05_ejecucion/scripts/fix-folio-y-agendan-2026-09-16.py`.
- ✅ **Custom fields de GHL mapeados**: `/tmp/ghl-cf-map.json` (59 CFs).

### Hecho el 17/9 (por API/MCP) — 2.ª ronda contactos + housekeeping

- ✅ **Fix CF `agendan cita` — 406/410 contactos**. Hallazgo clave para resolver esto: el CSV Leads YA tenía el teléfono en la columna `id` (el ETL lo documenta: `# Airtable: 1 phone por lead (columna id)`). Match por teléfono canonicalizado (mismo `canonPhone` MX 52↔521 del ETL) en vez de por email — que fallaba para leads Meta sin email. Script: `05_ejecucion/scripts/fix-agendan-cita-phone-2026-09-17.py`. 4 not-found por diff de teléfonos Airtable/GHL.
- ✅ **Fix CF `folio` — retry por teléfono (2.ª ronda)**: +72 contactos sobre los 450 anteriores = **522 total**.
- ✅ **Fix CF `fbclid`**: 50 contactos con Facebook click ID. Script consolidado: `05_ejecucion/scripts/fix-consolidado-2026-09-17.py` (folio retry + fbclid).
- ✅ **Verificación con GET directo**: Mauricio García (ID `uFx22fuKbExjkkUssx37`) → `Agendan cita=['true']`, `programa_interes='Internados'`, `link_enviado=['true']`, `firstName='Mauricio'`, `lastName='García'`, `phone='+5213331275715'`. Todos los CFs operativos.
- ✅ **Housekeeping**: paradas 2 tareas colgadas del harness (`bp8zhphzm`, `bn6480d1m` — shells con loops `until pgrep` que quedaron durmiendo aunque sus procesos Python ya habían terminado). No había Python vivo detrás.

**Total en 2 rondas**: 2.095 PATCHes a GHL, 0 errores API. Ítem 5 del MVP cerrado al 100%.

---

## 00 · Semáforo del día (single-glance)

Actualizar la matriz al inicio de cada jornada. **Al 2026-09-20 (D-6, sábado) el estado es:**

| Bloqueante | Estado | Notas |
|---|---|---|
| A1 · migración BSP WABA iniciada | 🔴 no iniciada | Cliente ejecuta 20 (hoy sábado) o 22 (lunes). **Runbook operativo:** `runbook-bsp-migration-waba-2026-09-19.md` |
| A2 · prereqs WABA (2FA, display name, verif negocio, admin Portfolio, NO app WA en el número) | 🟡 parcial | 2FA-only OK; verificar los otros 3 con Mauricio (§1 del runbook BSP) |
| A3 · dominio destino GHL decidido | 🔴 pendiente | Cliente. **YA NO bloquea plantillas Meta** (todas APPROVED con `promo.venttur.com`, se pueden redirigir en GHL). Sí bloquea landings nuevas — necesario antes del 22/9. |
| A4 · plantillas Meta revisadas con dominio nuevo | ✅ **cerrado 19/9** | 11/11 relevantes APPROVED. Poll confirmado. `seguimiento_ema_dia_10_3` (HEADER IMAGE) se resolvió sin correr la guía Resumable Upload — alguien la submitió manualmente entre 18 y 19/9. |
| A5 · plantillas subidas a Meta (reloj 24-72h) | ✅ **cerrado 19/9** | 11/11 APPROVED en el WABA bot (`submit-templates-log.json §notes.2026-09-19-poll-recap`). **Bloqueante B-07 CERRADO.** |
| A6 · testing E2E (`11 §11.3.bis`) | 🟡 guía lista | Correr entre D-2 (24/9) y D-1 (25/9). |
| A7 · cutover 26/9 (D-day) · Clientify muere 27/9 | 🟡 fecha objetivo confirmada 19/9 | Franja baja tráfico Mx (madrugada preferentemente). |
| **Test §07 hidden fields (15 min)** | 🔴 pendiente | **la agencia el 22/9.** Bloquea B9 aventureras y §9 calendarios (define si cae a Mecanismo #1 hidden field o #3 workflow post-booking). Ver §07 de esta guía + `03_arquitectura_ghl/07_agendamiento_calendarios.md §9`. |
| **Lote priorizado landings — 6 paths hardcodeados en plantillas APPROVED** | 🔴 sin arrancar | **Camilo el 21-22/9.** 5-8h manual GHL Funnels UI. Ver `04_guia_migracion/13_landings_clientify_a_ghl_funnels.md §13.6`. |
| B9 · landings aventureras (~100-125) | 🔴 sin diseñar | **Camilo 22-24/9.** Depende del test §07. Si Mecanismo #1: 2-4h (colapso a 1-5 templates + hidden field). Si Mecanismo #3: +8-12h. Ver `13_landings §13.7`. |
| **Rebuild 23 flujos Rodrigo (GHL Workflows)** | 🔴 sin arrancar | **Camilo 22-24/9.** 4-6h paralelo con landings. EMA 1 · IDIOMAS 10 · INTERNADOS 12. Runbook: `04_guia_migracion/14a_runbook_flujos_rodrigo.md`. 7 ambigüedades a resolver on-the-fly abriendo Clientify UI (Anexo C). |
| **8 calendarios GHL** (mecanismo C1 vs fallback) | 🔴 pendiente decisión técnica | **la agencia 22-23/9.** Test en sandbox 2-4h (§9 del doc calendarios) para decidir C1 vs C1-alt vs fallback. Si cae a fallback → mensaje pre-hecho al cliente para OK. Ver `03_arquitectura_ghl/07_agendamiento_calendarios.md §9`. |
| Plantillas AA t4 + Summer Camp t4 + seg_dia_3/5/7 exportar de ManyChat | 🔴 pendiente | Nice to have — no bloquea si el bot funciona in-session |
| Decisión prompt cutover (v2.0 vivo vs v2.2 sin Diego) | ✅ **cerrado 16/9** | v2.2 lista en repo. Falta aplicar al vivo (D-day 08:00) — pisa `options.systemMessage` inline del nodo Agente IA WPP. |
| Contactos GHL con info completa (Item 5 MVP) | ✅ **cerrado 17/9** | 2.095 PATCHes, 0 errores. Ver §Item 5 detalle. |
| Rotación OpenAI key (single, el crítico) | 🟡 diferible | Antes de A6. Otros secretos (Meta CAPI, ManyChat, Clientify) → §16.2 nice to have. |
| **Respaldo Clientify** | 🔴 no iniciado | **la agencia/Camilo 22-25/9.** Runbook operativo: `04_guia_migracion/12a_backup_clientify_runbook.md`. 7 elementos + checklist verificación pre-GO. Punto de no retorno: 27/9 EOD. |
| **Handoff notification** (mails/chat de Mauricio+Max) | 🔴 pendiente | **la agencia + Cliente 23-24/9.** Ver §20 (mini-runbook). Sin datos del cliente al T-4 → fallback Telegram al grupo. |
| **Guía técnica `seguimiento_ema_dia_10_3` Resumable Upload** | ✅ **innecesaria 19/9** | La plantilla se aprobó por otra vía. Doc queda como referencia para futuros templates con HEADER IMAGE: `06_docs/guia-destrabar-seguimiento-ema-dia-10-3.md`. |

**GO/NO-GO del 26/9 depende de:** A2 completo + BSP migration ejecutada (típicamente 20 o 22/9) + A6 verde + B9 landings con atribución funcionando + backup Clientify completo + 23 flujos Rodrigo + handoff notification.

**Regla de aborto:** si al **T-3 (23/9)** BSP WABA no confirmada → chip nuevo (Escenario B, +72h warm-up de plantillas). Última fecha para no llegar al 26/9 con canal roto.

**Índice de runbooks operativos disponibles** (los 5 escritos 19/9 + preexistentes): ver §18.

---

## 01 · Reglas duras (leer antes de tocar nada)

1. **No revocar la OpenAI key vieja** hasta ver el bot vivo respondiendo con la nueva. Regla de rotación.
2. **No apagar ManyChat ni Clientify** hasta el 27/9 EOD. Es la ventana de rollback. Aunque el cutover se ejecute el 18-19, el fallback tiene que seguir vivo.
3. **No re-importar workflows a n8n vivo.** Parches dirigidos con anchor verificado por API (patrón Fase 3/Fase 6). Un re-import borra nodos que el repo no conoce (precedente HPF).
4. **`session_id = teléfono` se preserva en el cutover.** El bot lee `n8n_chat_histories` por sessionKey normalizado (con el fix MX 52↔521). Si se pierde, todo lead activo re-saluda.
5. **NO tocar los flows ManyChat `Agenda` (140983) ni `Seguimiento agenda` (851504)** — están **cruzados por nombre** (hallazgo Camilo 11/9): "Seguimiento agenda" es en realidad la confirmación de cita, "Agenda" es el rescate post-link. Mapear por CONTENIDO, no por nombre.
6. **Snapshot antes de todo cambio** en n8n vivo, con sha256, siguiendo la convención `03_workflows/vivo-YYYY-MM-DD-*/`.
7. **Ante duda en fin de semana → pausar, no improvisar.** Cobertura la agencia+Camilo hasta 25/9.
8. **Nunca dar detalles técnicos en público** al cliente ni al lead. Solo "ya te contactamos por privado". Aprendizaje incidente Nahe.

---

## 02 · Camino crítico próximos 7 días (19-26/9)

Timings en CDMX (UTC-6). Cada ítem tiene precondición y verificación. **D-day = viernes 26/9. Clientify muere sábado 27/9 EOD.**

### Estado al arrancar 19/9 (D-7)

**Cerrado 16-17/9** (no re-hacer):
- ✅ Snapshot pre-cutover n8n vivo del 16/9 (13 workflows con sha256).
- ✅ Auditoría contactos GHL + fixes al 100% (1.ª y 2.ª ronda).
- ✅ Prompt v2.2 sin Diego. Backup v2.1 conservado.
- ✅ Decisión prompt cutover: v2.2. **Pisa `options.systemMessage` inline del nodo Agente IA WPP** (NO hay Google Doc — dato corregido 19/9).

**Cerrado 18/9** (workflow de auditoría VTR):
- ✅ 10 plantillas Meta submiteadas al WABA bot `1931874540684022`. Estados: 2 APPROVED, 8 PENDING (reloj 24-72h), 1 CONSOLIDATED. Log: `submit-templates-log.json`.

**Cerrado 19/9** (esta sesión):
- ✅ Runbook operativo BSP migration escrito (`runbook-bsp-migration-waba-2026-09-19.md`).
- ✅ Research GHL API para Funnels/Pages: veredicto **NO viable end-to-end**. Solo CRUD de Redirects. Ver §16.7 nuevo.
- ✅ D-day fijado en 26/9. Runbook recalibrado.
- ✅ Landings §13.6 los 6 paths bloqueantes + §13.7 mecanismo hidden fields para colapsar 120 aventureras.
- ✅ Backup Clientify runbook operativo (`04_guia_migracion/12a_backup_clientify_runbook.md`).
- ✅ Runbook 3 grupos flujos Rodrigo (`04_guia_migracion/14a_runbook_flujos_rodrigo.md`). **Hallazgo: no son 3 flujos sino 23** (EMA 1 · IDIOMAS 10 · INTERNADOS 12). Effort Camilo: 4-6h (no 1h).
- ✅ Doc decisión 8 calendarios GHL — árbol C1 vs fallback + mensaje pre-hecho al cliente (`03_arquitectura_ghl/07_agendamiento_calendarios.md §9`).
- ✅ Guía técnica para destrabar `seguimiento_ema_dia_10_3` con Resumable Upload API (`06_docs/guia-destrabar-seguimiento-ema-dia-10-3.md`).
- 🟡 Rotación OpenAI (nice-to-have pre-cutover) — pendiente para D-1 25/9.

### 🕘 20/9 (D-6, sábado — HOY)

- ⏳ **Esperando ventana del cliente para BSP migration.** Runbook `runbook-bsp-migration-waba-2026-09-19.md` entregado; Mauricio ejecuta hoy o lunes.
- ✅ **B-07 plantillas Meta cerrado ayer 19/9.** 11/11 APPROVED en el WABA bot. Ver §00 A4/A5.
- 🟢 **Camilo puede arrancar hoy sin bloqueo:** lote priorizado 6 landings (§13.6 del landings doc) + 23 flujos Rodrigo (`14a_runbook_flujos_rodrigo.md`). Ambos en paralelo, cero dependencia del WABA.
- 🟢 **la agencia puede arrancar sin bloqueo:** test §07 hidden fields (15 min, define camino de aventureras + calendarios).
- 📋 **Chat operativo:** confirmar con Mauricio si arranca la BSP hoy o el lunes.

### 🕘 20/9 (sábado) - 22/9 (lunes) — WABA en cliente + trabajo paralelo la agencia

- **20 o 22/9 · Cliente ejecuta BSP migration** siguiendo `runbook-bsp-migration-waba-2026-09-19.md`. Ventana sugerida: madrugada CDMX (bajo tráfico). Duración: 15-30 min de clicks + segundos a minutos de switchover. Sin downtime perceptible para el usuario final.
- **20-22/9 · Verificación post-BSP** — templates preserved OK (mirar en GHL Templates), test send + test receive (§4 del runbook BSP).
- **20-22/9 · Poll de plantillas PENDING** — chequear estado en Meta con Graph API (`GET /message_templates?fields=name,status`). Cuando pasen a APPROVED, actualizar `submit-templates-log.json`.
- **20-22/9 · Cerrar A3 (dominio destino GHL)** — pedir a Mauricio decisión final: `study.venttur.com` vs `go.venttur.com` vs otro. Si la BSP migration ya ocurrió, esto ya no re-abre reloj de plantillas (las que están APPROVED se preservaron), pero define dónde apuntan las landings nuevas.
- **21-22/9 · Camilo — lote priorizado landings 6 paths** (5-8h manual). Ver `13_landings_clientify_a_ghl_funnels.md §13.6`.
- **22/9 · Test GHL hidden fields (15 min)** — §07. Confirma mecanismo de atribución para las ~100-125 aventureras. Bloquea B9.
- **22/9 · Iniciar respaldo Clientify** — runbook `04_guia_migracion/12a_backup_clientify_runbook.md`. Puede correr en background.
- **22/9 · Destrabar `seguimiento_ema_dia_10_3`** — Resumable Upload API + submit. Guía: `06_docs/guia-destrabar-seguimiento-ema-dia-10-3.md` (a crear hoy).

### 🕘 23/9 (T-3) — momento crítico: GO/NO-GO intermedio

- **09:00 · Check BSP status** — WABA en GHL? Templates preserved OK? Si NO → **decidir chip nuevo (Escenario B) hoy**, no mañana. Cutover se corre a la siguiente semana O se acepta pérdida de límites de mensajería + 72h warm-up.
- **10:00 · Verificar plantillas Meta** — 8 PENDING + `seguimiento_ema_dia_10_3` deberían estar APPROVED al T-3. Si alguna sigue PENDING, escalar a Meta support o quitarla del scope MVP (nurturing puede empezar sin ella).
- **12:00 · Landings aventureras batch 2** — Camilo con mecanismo hidden fields confirmado.
- **14:00 · B6 · crear los 8 calendarios (shells) GHL + instrucciones OAuth para Rodrigo/Andrés** (los conectan ellos T-2/T-1).
- **17:00 · Handoff notification workflow GHL-UI** (si tenemos mails/chat ids del equipo). Sin datos → fallback Telegram al grupo.

### 🕘 24/9 (T-2) — Testing E2E

- **09:00-13:00 · Correr `11_testing_precutover.md §11.3.bis` (regresión Nahe N1-N7)** contra el staging con v2.2. **Falla dura = aborto cutover.**
- **14:00-18:00 · Sandbox B1-B4 + C1 con número de test** (canal WABA vivo post-BSP).
- **18:00 · Auditar plantillas restantes** — verificar dominio final en las 8 templates APPROVED. Si hay `promo.venttur.com` hardcodeado, decidir: (a) mantener y setear redirect en GHL post-cutover, o (b) re-subir plantillas con dominio nuevo (reloj 24-72h — perdemos el 26/9).

### 🕘 25/9 (D-1) — Preparación final

- **09:00 · Snapshot obligatorio pre-cutover** — n8n vivo (14 workflows con sha256) en `03_workflows/vivo-2026-09-25-pre-cutover/`. Este es el rollback de referencia.
- **10:00 · Rotar OpenAI key** — credencial `ibkhdCMyhr3yqDQk` en n8n. Verificar nodo Whisper por hardcode. No revocar la vieja hasta ver el bot respondiendo con la nueva.
- **12:00 · Aplicar prompt v2.2 al staging** — pisar `options.systemMessage` inline del nodo Agente IA WPP en staging workflow `3sLd7KY3o8I7NvXi` (no Google Doc). Correr smoke sobre staging Telegram para confirmar paridad.
- **14:00 · Verificar respaldo Clientify completo** — checklist §12a. Sin backup completo NO se ejecuta el cutover.
- **17:00 · Comunicar al chat operativo el GO tentativo del 26/9** — plantillas aprobadas? sandbox verde? WABA lista? backup Clientify OK? Si algo falla → correr al 27/9 (último día antes de que Clientify muera).
- **19:00 · Descanso.** Cobertura la agencia+Camilo al día siguiente.

### 🕘 26/9 (D-day) — ver §08 Runbook D-day

### 🕘 27/9 (D+1) — Clientify caduca EOD

- Watch mode primer día post-cutover. Digest cada 2h.
- Si aparecen P1: rollback disponible hasta las 21:00 CDMX (Clientify todavía vivo hasta EOD).
- 21:00 · último momento para decidir apagar Clientify. **A las 00:00 del 28/9 Clientify caduca y no vuelve.**

---

## 03 · Bloqueantes duros del cutover (Tabla A ampliada)

| # | Ítem | Owner | Precondición | Verificación |
|---|---|---|---|---|
| A1 | Migración BSP WABA `1931874540684022` → GHL | Cliente + la agencia | Escenario A confirmado ✅ | Meta BM muestra WABA bajo Location GHL |
| A2 | Prereqs WABA (2FA-only, display name, verif negocio, no WA app) | Cliente | Chip 2FA-only OK ✅ | Display name aprobado + verif negocio ✅ + celular sin WA app |
| A3 | Dominio destino GHL decidido | Cliente | — | Slug canónico anunciado en el chat |
| A4 | 16 plantillas Meta con dominio nuevo | la agencia | A3 | Diff aplicado, dominio validado byte-a-byte |
| A5 | Plantillas subidas a Meta (aprobación 24-72h) | la agencia + Meta | A4 | Status APPROVED en Meta BM |
| A6 | Testing E2E `11 §11.3.bis` Nahe + sandbox B1-B4/C1 | la agencia | Staging con guardrail (Bloque 0 ✅), nº de test | N1-N7 verdes + sandbox verde |
| A7 | Cutover 26/9 (viernes) · Clientify muere 27/9 EOD | la agencia + Cliente | A1-A6 verdes + BSP ya ejecutada + backup Clientify | Bot responde por GHL, contact GHL creado, memoria preservada |
| A8 | Backup Clientify pre-corte 26-27/9 | la agencia | Credenciales Rodrigo/Andrés/Mauricio ✅ | Export completo verificado |

---

## 04 · Trabajo paralelizable (Tabla B priorizada)

| # | Ítem | Owner | Estimado | Dependencia |
|---|---|---|---|---|
| B1 | Re-verificar `cerrar_conversacion` en staging | la agencia | 30 min | Ninguna |
| B2 | Terminar despachador (nurturing + históricos + paginación) | la agencia | 2-3 h | Plantillas Meta A5 |
| B3 | Rotar OpenAI key | la agencia | 20 min | Verificar Whisper hardcode |
| B4 | Rotar Meta CAPI tokens (Airtable "Programas CAPI") | Cliente + la agencia | 45 min | Cliente genera tokens |
| B5 | Handoff notification workflow GHL-UI | la agencia + Cliente | 1 h | Mails/chat ids de Mauricio+Max |
| B6 | 8 calendarios GHL + conexión OAuth de asesores | la agencia crea + asesores conectan | 1-2 h | Credenciales Google de Rodrigo/Andrés |
| B7 | Respaldo Clientify — ver §09 | la agencia | 2-3 h | Credenciales (ya tenemos) |
| B8 | Handoff MCP/PIT para Camilo | la agencia | 30 min | Doc ya escrito (`handoff-camilo-mcp-ghl.md`) |
| B9 | Landings aventureras (~100-125) | la agencia cablea + Cliente slugs | 1-2 días | Test hidden fields §07 |
| B10 | Auditar prompts + links por referencias a "Diego" | la agencia | 30 min | Ninguna |
| B11 | Replicar alerta P1 Telegram + INSERT `vtr_phantom_interceptions` en staging | la agencia | 45 min | No bloqueante |
| B12 | Extraer 2 nurturing faltantes (`AA t4`, `Summer Camp t4`) + `seg_dia_3/5/7` de ManyChat | la agencia | 30 min | Acceso ManyChat |
| B13 | Extraer textos confirmación cita + recordatorios de Clientify | la agencia | 30 min | Credenciales ✅ |
| B14 | Landing `go.venttur.com/bs` repuntar a GHL (orgánicos BS) | la agencia | 45 min | Dominio A3 |
| B15 | Lead Score — decisión binaria preservar/descartar | la agencia + Cliente | 15 min consulta | Buscar en n8n/ManyChat cómo se computa |
| B16 | Precios de los 3 huérfanos (Viajes educ., Ed. Superior, Cursos idiomas) | Cliente | Chat | Sin esto el bot no cotiza esos |
| B17 | Etapas comerciales "Viajes educativos" | Cliente comercial | Chat | Programa queda huérfano si falta |
| B18 | Textos propios nurturing de los 3 programas nuevos | Cliente | Chat | Nurturing sin arrancar en esos programas si falta |

---

## 05 · Verificaciones secuenciales pre-D-day (Tabla C)

Orden importa.

1. **A3 (dominio) cerrado** → habilita A4.
2. **A4 (plantillas revisadas)** → habilita A5.
3. **A5 (plantillas subidas)** → reloj 24-72h.
4. **Test hidden fields §07** → habilita B9 (landings aventureras).
5. **B10 (auditoría Diego)** antes de tocar cualquier link de calendario.
6. **Rotación OpenAI key (B3)** antes de A6 para no mezclar variables.
7. **§11.3.bis Nahe (N1-N7)** contra staging + prompt v2.1. Falla dura = aborto.
8. **Sandbox B1-B4 + C1** con número de test.
9. **GO/NO-GO** del D-day (26/9) por la mañana: A5 aprobada + A6 verde + A2 completo + BSP ya ejecutada + B9 con atribución + backup Clientify OK.
10. **Cutover** en franja baja tráfico.
11. **Digest guardrail 08:00 CDMX** activo cada día D+1 a D+7.

---

## 06 · Riesgos y contingencias

| Riesgo | Probabilidad | Mitigación / rollback |
|---|---|---|
| Meta no aprueba plantillas en 24-72h | 🔴 alta | Correr cutover al 27/9 (último día pre-caducidad Clientify) o al lunes siguiente aceptando que Clientify caducó. ManyChat sigue vivo (no revocar token todavía). |
| WABA migration BSP falla | 🟡 media | Escenario B: chip nuevo. Cliente ya tiene 2FA-only. Retrasa cutover pero no lo aborta. |
| Plantillas subidas con dominio viejo (`promo.venttur.com`) | 🔴 alta si no se cierra A3 hoy | Re-subir plantillas al dominio nuevo (nueva ventana 24-72h). Ver A3. |
| Regresión Nahe post-cutover | 🟡 baja | Guardrail intercepta + digest 08:00 CDMX + Regla #8 en prompt. Rollback prompt: `03_workflows/vivo-2026-09-15-pre-fix-nahe/`. |
| **GHL Contact dedup agresivo con phone `+52 1` vs `+521`** | 🟡 media | Normalización pre-import ya aplicada (Fase 2 · Camilo). Verificar smoke sobre 3 contactos con formatos distintos: si crean duplicados, aplicar `canonPhone()` en el import script. |
| **`records/search` lag post-write en GHL** | 🟡 media | Regla: siempre GET directo del record por ID después de un PUT, nunca search. Documentado en HPF. |
| **ManyChat webhook queda activo aunque el flow esté STOPPED** | 🟡 media | Revocar el token de ManyChat en Meta BM → desconectar la app, no basta con desactivar el flow. Cutover Collazo lo aprendió. |
| **Bearer/workflowId drift** post re-import a n8n del cliente | 🟡 media | Auditar IDs reales en n8n vivo antes de asumir que los del zip de Camilo son correctos. Reserva `03_workflows/vivo-2026-09-16-pre-cutover/`. |
| **Deals Clientify → Opportunities GHL** (~2.338 deals, 19 pipelines) | 🟡 media | Verificar mapping antes de import masivo. Política Expired: skip (default) o migrar como "Perdida". Documentar en `SINCRONIZACION` §Bloque 5 pre-cutover. |
| Regresión de sessionKey MX en la memoria de conversación | 🟡 baja | Fix ya aplicado (Fase 3 de Camilo). Test post-cutover: contact con formato `521…` y otro con `52…` responden en la misma sesión. |
| Prompt vivo 39K divergente del testeado 50K | 🟡 media | Decisión hoy (§02 tarde) — recomendado v2.1. Testing del 20-25/9 se hace sobre esa versión. |
| Notify:0 handoff sin email/chat (B5 sin datos) | 🟡 media | Fallback Telegram desde n8n a chat ids del equipo (falta pedirlos hoy). Sin esto, elevaciones a humano quedan en limbo. |
| Landings aventureras con dedup por email en GHL crean contact único con última atribución | 🟢 baja | Custom field `atribuida_a_slug` acepta lista (comma-separated). Documentar en el rediseño §07. |
| Cutover viernes 26/9 + Clientify muere sábado 27/9 EOD (ventana rollback 24h) | 🟡 media | Cobertura activa la agencia+Camilo del 26/9 al 3/10. Umbral de aborto sábado 27/9: 3+ incidentes P1 en 6h → rollback a ManyChat/Clientify antes de las 21:00 CDMX (después Clientify caduca a las 00:00 del 28/9). |

---

## 07 · Rediseño aventureras · test GHL hidden fields (15 min)

**Contexto:** ~20-25 aventureras × 5 programas = ~100-125 landings de Clientify que hoy embeben calendarios con etiqueta de atribución. En GHL hay que replicar el mecanismo.

**Test contra la sub-cuenta `7aXb4JCKsWV5nUyBXeSF` (PIT ya disponible):**

1. **Crear custom field `test_aventurera`** en Contact (texto). En la config del campo, setear **Query Key = `test_aventurera`**. Vía UI GHL: Settings → Custom Fields → New → Contact → Text → Query Key.
2. **Editar un calendar de test** → Forms & Payment → agregar `test_aventurera` como field del formulario, marcar **Hidden**.
3. **Abrir en incógnito:**
    ```
    https://api.leadconnectorhq.com/widget/booking/CAL_ID?test_aventurera=SLUG_TEST_MP
    ```
4. **Reservar con email throwaway.**
5. **Buscar el contact vía API (PIT):**
    ```bash
    curl -s "https://services.leadconnectorhq.com/contacts/search" \
      -H "Authorization: Bearer $GHL_PIT_VTR" \
      -H "Version: 2021-07-28" \
      -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
      -d '{"locationId":"'$GHL_LOCATION_ID'","filters":[{"group":"OR","filters":[{"field":"email","operator":"eq","value":"THROWAWAY_EMAIL"}]}]}'
    ```
6. **Verificar** si `customFields` contiene `test_aventurera` = `SLUG_TEST_MP`.

**Interpretación:**
- **Si sí** → Mecanismo #1 confirmado. Adelante con B9 (125 landings, cada una con iframe hardcodeado con su slug).
- **Si no** → pasar directo al Mecanismo #3 (workflow post-booking):
    - Trigger: `Customer Booked Appointment`
    - Filter: por Calendar ID
    - Action: `Update Contact Field` → `atribuida_a` = `{{contact.attributionSource.url}}` o `{{appointment.source}}` parseado por regex en un Custom Code node
    - O bien: Inbound Webhook a n8n que parsea el URL del referrer del landing (`https://study.venttur.com/maria-perez/boarding` → slug = `maria-perez`) y escribe el CF vía API.

**Doc completo del mecanismo:** ver `04_guia_migracion/13_landings_clientify_a_ghl_funnels.md §13.7` (por qué existen las 120 aventureras y cómo colapsan a 1-5 templates + hidden field vs Mecanismo #3 fallback +8-12h).

**Fallback duro de la disponibilidad compartida (calendarios):** si el mecanismo hidden field falla, se cae a **"1 calendario por asesor con event-types por programa"**. **Árbol de decisión completo (test C1 en sandbox + Mecanismo A/B + fallback + mensaje pre-hecho al cliente para OK):** `03_arquitectura_ghl/07_agendamiento_calendarios.md §9`. Requiere OK del cliente si aplica (contradice P2 del cuestionario). Registrar el resultado del test §07 acá.

---

## 08 · Runbook D-day 26/9 (viernes)

**Prerequisito:** BSP migration WABA ya ejecutada entre 20-22/9 (§02). En el D-day el canal ya vive en GHL. Lo que se hace hoy es apuntar el webhook, revocar ManyChat como fallback, aplicar el prompt v2.2 al vivo, y watch mode.

| Hora CDMX | Paso | Owner | Checkpoint |
|---|---|---|---|
| 08:00 | **GO/NO-GO check** en el chat operativo | la agencia | Plantillas APPROVED + sandbox verde + A2 completo + BSP ya ejecutada + landings con atribución + backup Clientify OK. Si ❌ → correr al 27/9 (último día pre-caducidad Clientify). |
| 08:30 | Verificar `vtr_phantom_interceptions` últimas 24h · digest 08:00 verde (o silencio si N=0) | la agencia | Sin activaciones anómalas |
| 09:00 | Aplicar prompt v2.2 al vivo — pisar `options.systemMessage` inline del nodo Agente IA WPP (n8n main-venttur) | la agencia | Prompt vivo = 50.652 chars sin Diego, verificar via API |
| 09:30 | Downtime ventana — freezar webhook en n8n de ManyChat (nodo Set con abort temporal) | la agencia | ManyChat no recibe nuevos leads durante la ventana |
| 10:00 | Cutover del webhook: apuntar `Contact Reply` de GHL al n8n vivo | la agencia | Test: mensaje al número → llega a n8n con `contactId` |
| 10:15 | **Revocar token ManyChat en Meta BM** (no basta con STOP flow) | la agencia | ManyChat ya no recibe |
| 10:30 | Smoke test: reservar en un calendar de test como aventurera → verificar `atribuida_a` en contact | la agencia | Atribución funcionando |
| 11:00 | Verificar memoria: contact conocido escribe "hola" → bot NO re-saluda (sessionKey preservado) | la agencia | Memoria intacta |
| 11:30 | Habilitar el despachador con carril nurturing + históricos + política limitada (solo `Link asesoría enviado = true` + `Agendan cita = false`, no spam 5000) | la agencia | Corrida 1 procesa <100 leads (no 5000) |
| 12:00 | Comunicar en el chat operativo: **cutover exitoso**. Empieza monitoreo 48h. | la agencia | Ok |
| 12:00-20:00 | Watch mode. Digest cada 2h. | la agencia+Camilo | 0 P1 activos |

**Ventana de aborto:** entre 10:00 y 11:00, si aparece P1 (mensajes no salen, memoria perdida, dedup roto en Contact GHL) → rollback secuencial (§10). Rollback disponible hasta el sábado 27/9 21:00 CDMX (después Clientify caduca).

---

## 09 · Respaldo de Clientify pre-corte (la agencia ejecuta, tenemos credenciales)

> **⚡ Runbook operativo canónico:** `04_guia_migracion/12a_backup_clientify_runbook.md` (paso-a-paso técnico de los 7 elementos + checklist de verificación pre-GO + estructura final del backup + punto de no retorno). **Esa es la fuente operativa** — este §09 es solo el resumen visible desde la guía recta final.
>
> Aviso al cliente (transparencia): `06_docs/clientify-que-respaldar-antes-de-apagar.md`.

**Checklist rápido (los 7 elementos, detalle técnico en el runbook operativo):**

1. **Contactos** — CSV completo (~7k filas).
2. **Chats** — últimos 60 días abiertos + adjuntos.
3. **Automatizaciones activas** — screenshots + JSON export si aplica.
4. **Landing pages de aventureras** — HTML + assets vía `wget --mirror`.
5. **Calendarios embebidos** — URLs + configs para replicar en GHL.
6. **Plantillas WhatsApp** — screenshot + copia literal.
7. **Reportes** — CSV de conversiones, atribuciones.

Todo en `05_ejecucion/backup-clientify-2026-09/` (gitignored por PII).

**Punto de no retorno:** 27/9 EOD. **Regla dura:** si el 26/9 09:00 el checklist §3 del runbook operativo no está 100% verde, se retrasa cutover al 27/9. Si sigue rojo el 27/9 09:00 → se corre a la siguiente semana + otro mes de Clientify.

---

## 10 · Rollback playbook (por escenario)

**Escenario 1 · Meta no aprueba plantillas a tiempo (24-72h vence al T-3, 23/9)**
- Correr cutover al 27/9 (último día pre-caducidad Clientify) o al lunes siguiente.
- ManyChat sigue vivo, token NO revocar.
- Comunicar al cliente que el cutover se corre. Sin drama, gates de Meta son gates de Meta.
- **Regla dura:** si la ventana es de 24h (26 → 27), no arriesgar el cutover con plantillas todavía pendientes — la operación nurturing puede arrancar sin ellas si el bot funciona in-session (§16.1).

**Escenario 2 · WABA BSP migration falla o se cuelga**
- Escenario B (chip nuevo). Cliente ya tiene 2FA-only.
- Retrasa cutover ~72h (nueva WABA + re-aprobar plantillas + warm-up de 250 conv/24h).
- No aborta la migración, solo corre la fecha.

**Escenario 3 · Cutover parcial (mensajes salen pero memoria se perdió, o dedup roto en Contact GHL)**
- Rollback secuencial:
    1. Re-apuntar el webhook al ManyChat viejo (path pre-cutover).
    2. Restaurar token ManyChat en Meta BM.
    3. Restaurar OpenAI key vieja si se rotó.
    4. Snapshot revert `03_workflows/vivo-2026-09-25-pre-cutover/`.
- **Ventana de rollback = 24h.** ManyChat + Clientify siguen vivos hasta 27/9 EOD. **A las 00:00 del 28/9 rollback ya no es posible.**

**Escenario 4 · Bug crítico post-cutover D+1 (27/9) — con ventana de rollback muriendo EOD**
- 3+ incidentes P1 en 6h → rollback a ManyChat (Escenario 3). **Última oportunidad — decidir antes de las 18:00 CDMX del 27/9.**
- 1-2 incidentes → fix quirúrgico + digest a 30 min. Puede seguir sin rollback.

**Escenario 5 · Bug crítico post D+2 (a partir del 28/9)**
- Rollback a ManyChat/Clientify YA NO ES POSIBLE. Clientify caducó.
- Único camino: fix quirúrgico en GHL/n8n. Escalado inmediato con la agencia+Camilo cobertura 09:00-21:00 CDMX.
- Post-mortem al final en `06_docs/postmortem-cutover-2026-09.md`.

**Regla dura:** cualquier rollback antes de las 21:00 CDMX. No se hacen rollbacks de madrugada.

---

## 11 · Testing continuo 20-25/9

Ventana de estabilización. Cobertura la agencia+Camilo. Queries diarias a las 09:00 CDMX:

1. **Digest guardrail Nahe** (`BzBCMGxEdJy6zmA9`) — activaciones últimas 24h.
2. **`sys_tool_calls` equivalente en GHL** — tool calls exitosas vs fallidas.
3. **Dedup GHL** — contactos con `+52 1` y `+521` que deberían ser el mismo. Query por email si aplica.
4. **`records/search` lag** — verificar que los reads post-write funcionan.
5. **Attribution aventureras** — % de contacts nuevos con `atribuida_a` no vacío.
6. **Deals Expired/Perdidos** — cuántos aparecen mal mapeados.
7. **Plantillas Meta** — delivery rate por template.
8. **Bot response time** — p50/p95 vs baseline pre-cutover.

**Umbral de escalamiento:**
- P1 (bot no responde, mensajes no salen, memoria perdida): despertar a la agencia en cualquier momento.
- P2 (bug funcional específico, no bloquea al usuario): fix en <4h.
- P3 (cosmético, deuda documentada): fix en <48h o backlog post-cutover.

---

## 12 · Corte Clientify 26-27/9

- **26/9 mañana:** verificación final del respaldo (§09). Que todo esté en `05_ejecucion/backup-clientify-2026-09/`.
- **26/9 tarde:** confirmar con el cliente que da luz verde al apagado.
- **27/9 mañana:** apagar Clientify (no renovar suscripción).
- **27/9 EOD:** punto de no retorno. Clientify caduca. Post-mortem del cutover en `06_docs/postmortem-cutover-2026-09.md`.

**Deuda:** después del 27/9 esta guía se archiva a `06_docs/_historico/`. El estado permanente vuelve a `ESTADO_MIGRACION.md` + `REGISTRO-EJECUCION.md`.

---

## 13 · Snapshots y respaldos

| Path | Contenido | sha256 |
|---|---|---|
| `03_workflows/vivo-2026-09-15-pre-fix-nahe/` | Pre-Nahe (4 workflows) | ✅ existe |
| `03_workflows/vivo-2026-09-16-post-fix-prompt-guardrail/` | Post-Fase 3 (main-venttur 43 nodos) | ✅ existe |
| `03_workflows/vivo-2026-09-16-post-fix-fase6-alertas/` | Post-Fase 6 (main + digest workflow) | ✅ existe |
| `03_workflows/staging-2026-09-16-pre-replica-guardrail/` | Pre-Bloque 0 staging | ✅ existe |
| `03_workflows/staging-2026-09-16-post-replica-guardrail/` | Post-Bloque 0 (staging 13 nodos + detector + tests) | ✅ existe |
| `03_workflows/vivo-2026-09-16-pre-cutover/` | Pre-cutover del 18-19/9 (fecha original) — 13 workflows + sha256 | ✅ existe (histórico) |
| `03_workflows/vivo-2026-09-25-pre-cutover/` | **A crear el D-1 (25/9):** los 14 workflows productivos + credenciales exportadas — este es el rollback de referencia del cutover 26/9 | 🔴 pendiente (D-1) |
| `03_workflows/vivo-2026-09-17-pre-plantillas/` | Post-testing pre-upload plantillas Meta (histórico) | 🟡 obsoleto |
| `05_ejecucion/backup-clientify-2026-09/` | Export completo Clientify (PII, gitignored) — ver runbook `04_guia_migracion/12a_backup_clientify_runbook.md` | 🔴 pendiente (T-2 a T-1) |

---

## 14 · Contactos y chat operativo

- **Cliente**: Mauricio García de la Vega (dueño Venttur, no confundir con el padre homónimo de TOFO Pizza), Max Almonte (técnico).
- **la agencia**: la agencia (lead), Camilo (staging + scripts).
- **Chat operativo del cutover** — grupo de WhatsApp con Mauricio + Max + la agencia + Camilo. Confirmar el chat existente o crear uno específico para la ventana 16-25/9.
- **Ventana de cobertura**: la agencia + Camilo activos 09:00 a 21:00 CDMX del 26/9 al 3/10. Fuera de esa ventana → chat asíncrono, con SLA de 4h para P1. Cobertura extendida los 2 primeros días (26-27/9) por criticidad de la ventana de rollback.

---

## 15 · Referencias

- Plan operativo previo: `~/.claude/plans/perfecto-antes-de-cerrar-zazzy-twilight.md`
- Estado post-consolidación: `00_migracion_ghl/ESTADO_MIGRACION.md §Actualización 2026-09-16`
- Fuente de verdad temporal (archivada por esta guía): `00_migracion_ghl/SINCRONIZACION-2026-09-16.md`
- Pendientes de Camilo: `00_migracion_ghl/PENDIENTES-MIGRACION-2026-09-11.md`
- Incidente Nahe: `06_docs/incidente-nahe-2026-09-15.md`
- Barrido Nahe: `06_docs/barrido-leads-promesa-fantasma-2026-09-16.csv`
- Handoff MCP/PIT para Camilo: `06_docs/handoff-camilo-mcp-ghl.md`
- Portabilidad WABA: `06_docs/portabilidad-numero-whatsapp-2026-08-18.md`
- Plantillas Meta borradores: `06_docs/plantillas-meta-borradores-2026-09-11.md` + `plantillas-meta-nurturing-2026-09-11.md`
- Cruce Agenda/Seguimiento agenda: `06_docs/hallazgo-cruce-agenda-seguimiento-2026-09-11.md`
- Rotación de secretos: `06_docs/plan-rotacion-secretos-2026-09-11.md`
- Respaldo Clientify (aviso al cliente): `06_docs/clientify-que-respaldar-antes-de-apagar.md`
- Contratos de diseño heredables a GHL: `03_arquitectura_ghl/06 §9`, `07 §7`, `04_guia_migracion/07 §7.7`, `11 §11.3.bis`

---

**Última actualización:** 2026-09-20 CDMX (poll plantillas ✅ + auditoría gaps + secciones §18-§20 nuevas: índice runbooks + accionables cliente + mini-runbook handoff)
**Sunset:** 2026-09-27 EOD (corte Clientify) → post-mortem del cutover en `06_docs/postmortem-cutover-2026-09.md`

---

## 16 · Nice to have's (diferibles post-cutover)

Todo lo siguiente **NO bloquea** el go-live del 26/9. Se persigue solo si sobra tiempo, si aparece una necesidad en operación, o post-cutover. Se listan aquí para no perderlos, no para presionar.

### 16.1 Plantillas Meta

- **Subir las 16 plantillas Meta** (12 rescate + 3 outreach + 1 informativa). **No es bloqueante** si el bot funciona in-session — el 100% de conversaciones nuevas arrancan dentro de la ventana de 24h. Las plantillas solo se necesitan para nurturing automático fuera de ventana (rescate post-link a las 45m/24h, outreach form Meta t1/t2/t3, digest promocional). En los primeros días la operación puede correr sin nurturing y agregarlo cuando las plantillas estén aprobadas.
- **Auditoría del dominio destino GHL** en las 16 plantillas (`promo.venttur.com` hardcodeado). Cuando llegue la decisión del cliente, correr `grep -r 'promo.venttur.com' 06_docs/plantillas-meta-*.md` y reemplazar en todas.
- **Exportar de ManyChat las 5 plantillas nurturing faltantes** (AA t4, Summer Camp t4, seg_dia_3/5/7). Solo si querés replicar el nurturing completo. Sin esto, el nurturing funciona con los toques ya cubiertos.

### 16.2 Rotación de secretos (`plan-rotacion-secretos-2026-09-11.md`)

- OpenAI API key nueva
- Meta CAPI PIT nuevo
- ManyChat token nuevo
- Clientify token nuevo (aunque va a apagarse — puede quedar sin rotar)

Se puede posponer 1-2 semanas post-cutover sin exposición. **Nice to have** por higiene, no crítico. La key vieja de OpenAI queda expuesta hasta rotarla — riesgo bajo si el WS no está público.

### 16.3 Reparación de datos GHL

- ~~**Split firstName/lastName**~~ — ✅ **hecho 16/9** (1.117 contactos, cobertura `lastName` 19% → 63.6%).
- **Marcar contactos "instituciones"** (firstName contiene "School", "Academy", "College") con un flag para no mandarles WhatsApp personal. ~30 min manual. Bajo impacto — el split no los tocó, siguen intactos.
- **Backfill de email** para 55% sin email — solo si están en Clientify histórico o hay otra fuente.
- **Reconciliación de teléfonos Airtable vs GHL** — ~23 casos donde el ETL usó el phone de Clientify pero Airtable tenía otro (ej. Milka con `+5218998994485` en Airtable vs `+5218995037621` en GHL). Requiere decisión manual sobre cuál es correcto para cada caso.
- **Etapas comerciales del pipeline "Viajes educativos"** — 3 de los 8 programas no tienen deals hoy (0 hits). Se puede cablear cuando el programa arranque a facturar.
- **Poblar Airtable Programas CAPI** con los 3 huérfanos (Viajes educativos, Educación superior, Cursos de idiomas). Solo si hay volumen relevante — hoy es 0.

### 16.4 Textos y contenidos

- **Textos de confirmación de cita + recordatorios pre-cita 24h/1h** — extraer de Clientify (2 secuencias). Pueden replicarse en GHL post-cutover cuando la operación esté estable. Los recordatorios manualmente por Rodrigo/Andrés cubren el gap.
- **Repuntar `go.venttur.com/bs`** (link orgánico Boarding School) a GHL. Mientras tanto: redirect al link canónico `agendar-ema Rodrigo`.
- **Precios de los 3 huérfanos** (Viajes educativos, Educación superior, Cursos de idiomas) — el bot puede responder "consulta con asesor" durante las primeras semanas.
- **Textos de nurturing de los 3 programas huérfanos** — solo cuando facturen.

### 16.5 Diseño arquitectónico avanzado

- **Lead Score decisión binaria** — el CF existe pero no está poblado. Decidir su semántica antes de cablearlo al nurturing avanzado.
- **Handoff notification avanzado** (más que MVP): dashboard de leads elevados con SLA, escalamiento automático si no hay respuesta en X minutos, resumen semanal al equipo. MVP es solo el mail/Telegram inicial.
- **cerrar_conversacion tool** — que el agente pueda cerrar el estado del lead cuando se detecta churn/desinterés. Feature del roadmap post-Etapa 2.
- **Terminar el despachador proactivo** (`vrShEXQGGAo4FqAt`) — segunda ola de outreach basada en signals. Post-cutover.

### 16.6 Alertas y observabilidad

- **Alertas P1 del guardrail Telegram al staging** — replicar el patrón del vivo (Fase 6) sobre el n8n staging. Si el staging pasa a producción sin el clon de las alertas, un intercept ahí queda sordo. **Nice to have** — se puede agregar el 1-2 día post-cutover.

---

## 17 · Comparativa de prompts (para item 2: paridad Telegram)

**Contexto del reporte del usuario "el agente Telegram no responde igual que el actual":**

Hay 4 prompts vivos en el repo con diferencias sustantivas. La causa probable de la diferencia reportada es que el staging tiene el prompt viejo (pre-Nahe) y el vivo tiene el nuevo (post-Nahe).

| Prompt | Tamaño | Contexto | Diferencia clave |
|---|---|---|---|
| `agente-venttur-system-prompt-v1.9-backup-2026-08-17.md` | ? | Vivo pre-incidente Nahe 15/9 | Sin Regla ABSOLUTA #8 "No agendo yo" · sin guardrail |
| `agente-venttur-system-prompt-v2.0-live-backup-2026-09-16.md` | 48.402 chars | Snapshot del vivo justo pre-Fase 3 (16/9 AM) | Sin Regla ABSOLUTA #8 · sin bloque ESTADO DEL LEAD reforzado |
| `agente-venttur-system-prompt-v2.1.md` | 50.838 chars | Post-Fase 3 (16/9 PM, aplicado al vivo) | Con Regla ABSOLUTA #8 · con guardrail · **con 7 menciones a Diego** |
| `agente-venttur-system-prompt-v2.2.md` | 50.652 chars | **Recomendado para el cutover** | v2.1 sin Diego · 0 menciones residuales |

**Recomendación**:
- **Aplicar v2.2 al staging** (n8n `3sLd7KY3o8I7NvXi`).
- Correr el smoke test de los 5 casos Nahe post-Fase 3 en ese staging → si pasa 5/5, el ítem 2 del usuario queda cerrado.
- Aplicar v2.2 al vivo el D-day (26/9) — pisar `options.systemMessage` inline del nodo Agente IA WPP.

**Comando útil para diff:**

```bash
diff clients/VTR_Venttur/04_agents/agente-venttur-system-prompt-v2.0-live-backup-2026-09-16.md \
     clients/VTR_Venttur/04_agents/agente-venttur-system-prompt-v2.2.md | head -100
```

---

**Cierre del recorte al 19/9 (D-7):** de los 8 items MVP, **1 está cerrado al 100% (contactos GHL)**, **1 tiene runbook operativo listo (WABA BSP)**, y **6 tienen ventana definida entre el 22 y el 25/9**. §16 y §17 sirven para no perder el resto de vista, pero se persigue solo si el MVP está verde y sobra tiempo antes del 25/9.

**Snapshot de estado 8 items MVP al 19/9:**
| # | Item | Estado | Ventana |
|---|---|---|---|
| 1 | Landings + calendarios Clientify | 🟡 lote priorizado = 6 paths (identificado 19/9) + ~120 aventureras vía hidden fields §07 | Landings 6 = 21-22/9 · aventureras 22-24/9 |
| 2 | Paridad agente Telegram | 🟡 prompt v2.2 listo, falta aplicar y correr smoke (Item 6) | 25/9 12:00 (staging) |
| 3 | Traspaso WABA | 🟡 runbook operativo listo (`runbook-bsp-migration-waba-2026-09-19.md`) | Cliente ejecuta 20 o 22/9 |
| 4 | Exports y backups | 🟡 n8n snapshot 16/9 ✅ · Clientify 🔴 → runbook `12a_backup_clientify_runbook.md` (a crear hoy) · snapshot D-1 25/9 pendiente | 22-25/9 |
| **5** | **Contactos GHL info completa** | ✅ **CERRADO 17/9** | — |
| 6 | Prompt cutover | 🟡 v2.2 lista (50.652 chars). Pisar `options.systemMessage` inline del nodo Agente IA WPP en staging (D-1, 25/9 12:00) + al vivo el D-day (26/9 09:00) | 25-26/9 |
| 7 | Session preserve | 🟡 documentado, falta verificar en el bot GHL post-cutover | 26/9 11:00 (§08) |
| 8 | Handoff notification | 🔴 arranca 23/9 tarde (pedir a cliente mails/chat ids + fallback Telegram al grupo) | 23-24/9 |

**Adicionales cerrados el 19/9 (esta sesión):**
- ✅ Runbook operativo BSP migration escrito.
- ✅ Investigación GHL API para Funnels/Pages: NO viable end-to-end (solo CRUD Redirects). Plan híbrido posible (15-25% ahorro), con lote priorizado real = 6 paths.
- ✅ D-day recalibrado a 26/9 (ventana 24h de rollback antes de Clientify EOD 27/9).

**Adicionales cerrados el 20/9 (esta sesión):**
- ✅ Poll de plantillas Meta ejecutado — 11/11 APPROVED confirmadas. Bloqueante B-07 cerrado.
- ✅ Guía recta final auditada contra pendientes reales: 7 gaps identificados + cerrados (fecha desactualizada, refs a runbooks nuevos, líneas de semáforo faltantes, mini-runbook handoff, sección "accionables del cliente", índice de runbooks).

---

## 18 · Índice de runbooks operativos (por área)

Los 5 runbooks operativos escritos el 19/9 + los preexistentes, consolidados para acceso rápido. Cada uno es autocontenido (puede seguirse sin releer esta guía).

| Área | Runbook operativo | Owner de ejecución | Cuándo |
|---|---|---|---|
| **BSP migration WABA** | `06_docs/runbook-bsp-migration-waba-2026-09-19.md` | Mauricio (cliente) | 20 o 22/9 |
| **Backup Clientify pre-corte** | `04_guia_migracion/12a_backup_clientify_runbook.md` | la agencia o Camilo | 22-25/9 |
| **Rebuild 23 flujos Rodrigo (GHL Workflows)** | `04_guia_migracion/14a_runbook_flujos_rodrigo.md` | Camilo | 22-24/9 |
| **Landings — lote priorizado 6 paths + mecanismo aventureras** | `04_guia_migracion/13_landings_clientify_a_ghl_funnels.md §13.6-§13.7` | Camilo | 21-24/9 |
| **Decisión 8 calendarios GHL (C1 vs fallback + mensaje al cliente)** | `03_arquitectura_ghl/07_agendamiento_calendarios.md §9` | la agencia (test), Mauricio (OK) | 22-23/9 |
| **Destrabar template con HEADER IMAGE (referencia futura)** | `06_docs/guia-destrabar-seguimiento-ema-dia-10-3.md` | la agencia si aparece caso similar | N/A hoy |
| **Prompt agente cutover (v2.2 sin Diego)** | `04_agents/agente-venttur-system-prompt-v2.2.md` (aplicar inline en systemMessage) | la agencia | D-1 (25/9) staging, D-day (26/9) vivo |
| **Test §07 hidden fields (15 min)** | §07 de esta guía | la agencia | 22/9 |
| **Handoff notification** | §20 de esta guía (mini-runbook) | la agencia + Mauricio para datos | 23-24/9 |
| **D-day runbook** | §08 de esta guía | la agencia lidera + Camilo backup | 26/9 |
| **Rollback playbook** | §10 de esta guía | la agencia | Durante D-day + D+1 |
| **Aviso al cliente sobre Clientify** | `06_docs/clientify-que-respaldar-antes-de-apagar.md` | la agencia al cliente | Ya entregado |
| **Portabilidad WABA — diagnóstico previo** | `06_docs/portabilidad-numero-whatsapp-2026-08-18.md` | Referencia | — |

---

## 19 · Accionables del cliente (consolidado + deadline)

Todo lo que dependemos de Mauricio/Max/Rodrigo/Andrés en un solo lugar. **Sin estos datos/acciones a tiempo, el cutover se retrasa** (aborto T-3 → siguiente semana + otro mes de Clientify).

| # | Accionable | Owner del lado cliente | Deadline | Bloquea | Notas |
|---|---|---|---|---|---|
| 1 | **Ejecutar BSP migration WABA** siguiendo runbook | Mauricio | 20-22/9 | A1, todo el canal WhatsApp | Runbook: `runbook-bsp-migration-waba-2026-09-19.md`. Duración: 15-30 min de clicks. |
| 2 | **Prereqs Meta (2FA off, display name approved, business verified, rol admin del Portfolio)** | Mauricio | Antes del punto 1 | A1 | §1 del runbook BSP. |
| 3 | **Decisión dominio destino GHL** (`study.venttur.com` / `go.venttur.com` / otro) | Mauricio | 22/9 (T-4) | A3, landings nuevas | Ya NO bloquea plantillas Meta (todas APPROVED con `promo.venttur.com`, se pueden redirigir). |
| 4 | **OK fallback calendarios** si el test C1 falla | Mauricio | T-3 (23/9) | B6, prompt del bot | Contradice P2 del cuestionario. Mensaje pre-hecho: `07_agendamiento_calendarios.md §9.3`. |
| 5 | **Confirmar slugs canónicos aventureras** (30 madres con inconsistencias hoy) | Mauricio | T-3 (23/9) | B9 aventureras | Camilo no puede batchear sin la nomenclatura definitiva. |
| 6 | **Mails + Telegram chat IDs del equipo** para handoff notification | Mauricio + Max | T-4 (22/9) | Item 8 MVP | Sin datos al T-4 → fallback Telegram al grupo del proyecto. |
| 7 | **OAuth Google Calendar de Rodrigo + Andrés** (conectarlos a GHL) | Rodrigo + Andrés | T-2 (24/9) | B6 | Solo aplica si Mecanismo A o B del §9 calendarios se elige. |
| 8 | **Textos de confirmación de cita + recordatorios pre-cita** (extraer de Clientify) | Rodrigo + Andrés (o la agencia con sus credenciales) | T-2 (24/9) | Nice to have | Los recordatorios manuales cubren el gap si no llega. |
| 9 | **Precios + etapas + textos de los 3 programas huérfanos** (Viajes educ., Ed. superior, Cursos idiomas) | Mauricio | Post-cutover si no llega antes | Nice to have | Bot puede responder "consulta con asesor" hasta que llegue. |
| 10 | **Luz verde para apagar Clientify** | Mauricio | 26/9 tarde | Apagado 27/9 | Post-verificación de backup completo. |

**Regla:** si al **T-3 (23/9)** los ítems **1, 2, 3, 4, 5, 6** no están todos ✅ → GO/NO-GO intermedio con conversación de "corremos al 27/9 o a la siguiente semana".

---

## 20 · Mini-runbook — Handoff notification (Item 8 MVP)

**Contexto:** cuando el bot eleva un lead a humano (Meta ads sin match, promesa fantasma interceptada por el guardrail, lead pide humano, error tool call), el equipo tiene que enterarse **en tiempo real**. Sin esto, el lead queda como Nahe (esperando sin respuesta) — es el patrón que motivó el bloqueante.

**Prerequisito informativo del cliente (accionable #6 del §19):**
- Mails a los que llegan las notificaciones: `[email Mauricio]` + `[email Max]` (pendiente confirmar).
- Chat ID Telegram del grupo operativo `[chat_id]` (pendiente confirmar — fallback si mails no llegan).

**Diseño operativo (a implementar cuando lleguen los datos del cliente):**

**Eventos que disparan notificación** (3):
1. **Elevación explícita** — bot invoca `elevar` (tool call).
2. **Guardrail intercepta promesa fantasma** — patrón Nahe (Regla ABSOLUTA #8).
3. **Meta ads sin match** — lead entra con `utm_source=facebook` pero no matchea ningún programa canónico.

**Canal** (dos vías en paralelo, para redundancia):
- **Mail** vía GHL Workflow → `Send Email` a Mauricio + Max. Template con contexto (nombre lead, teléfono, último mensaje, motivo de elevación).
- **Telegram** vía n8n → HTTP a Bot API → grupo operativo. Mismo contexto, formato corto (una línea + link a la conversación GHL).

**Template del mensaje (Mail + Telegram)** — usar los mismos 5 campos:
- Lead: `[Nombre + Apellido]` (`[teléfono]`)
- Motivo: `[elevacion_explicita | guardrail_fantasma | ads_sin_match]`
- Últimos 3 mensajes del hilo (contexto)
- Link a conversación en GHL: `https://app.gohighlevel.com/v2/location/{locationId}/contacts/detail/{contactId}/conversation`
- Timestamp CDMX

**Implementación (la agencia en n8n + GHL UI):**
1. **En GHL:** crear Workflow "Handoff — Send Email" con trigger `Contact Tag Added = elevado_humano` → acción `Send Email` con los 5 campos. **Tiempo: 30-45 min.**
2. **En n8n (fallback + robustez):** en el flujo principal del agente, después del nodo `elevar` (tool call exitoso), agregar rama paralela → HTTP POST a Telegram Bot API con el mismo template. **Tiempo: 30 min.**
3. **Smoke test:** disparar los 3 eventos manualmente (elevar desde n8n, forzar match del guardrail con un input trap, mandar un lead con `utm_source=facebook` sin programa) → verificar que llegan las notificaciones a los 2 canales.

**Fallback si el cliente no entrega mails a tiempo (T-4, 22/9):**
- Solo Telegram al grupo operativo (ya tenemos el chat ID). Mail queda como upgrade post-cutover.
- Documentar la deuda en el semáforo §00 para revisar el 28/9.

**Verificación post-cutover (D-day 26/9 + D+1 27/9):**
- Query diaria: contar activaciones del guardrail en las últimas 24h. 0 activaciones = OK.
- Chat operativo: cada notificación recibida → replicar en el chat con timestamp.

---

## 21 · Estado n8n — qué falta (post-WABA)

> **Registro canónico y fuente única: `06_docs/pendientes-n8n-post-waba.md`** — tabla flujo-por-flujo con IDs + checklist de 12 pasos. Es la respuesta exacta a *"¿falta algo en n8n?"* después del BSP. Detalle node-level de cada rebuild en `revision-n8n-al-100-2026-09-20.md`; log de ejecución en `ejecucion-n8n-2026-09-21.md`.

**Ya hecho en n8n (21/9, todo OFF salvo el prompt del staging):**
- Borrados los 2 artefactos muertos (`venttur-main-GHL`, `Meta CAPI GHL`).
- Despachador (`vrShEXQGGAo4FqAt`): carril outreach consolidado (Decisión B) + 3 fixes (ultimo_toque_at, TERMINAL Cerrada, sessionKey).
- CAPI ledger → **Supabase** (Decisión A): tablas `capi_folios`/`capi_programas` (Programas migrado) + rebuilds `mf7VQJelfieCDJ5r` (Meta CAPI) y `4HgMkK34xqITULM3` (Registro Folio), sin Airtable.
- Clasificador (`Xmyoewwa1W5gm1fy`): escribe tipo_contacto + programa_interes (con guarda) + nota resumen.
- **Prompt v2.2 (Diego) aplicado al staging** (`3sLd7KY3o8I7NvXi`), preservando cerrar_conversacion + Nahe. (El vivo `[Venttur]` se aplica el D-day, §10.3.)
- W11 estado 'Contestó' GHL (`qYgeTc9PCq3TiGDn`) + Correo semanal GHL (`OaOyHA2tfjMtuWTk`) construidos.

**Falta (resumen — detalle en el doc canónico §2):**
1. **Construir:** W4 Formulario→GHL · W9 Actualizar link→GHL · W6 Confirmación agenda (⛔ calendarios+OAuth) · W10 ingest.
2. **Wiring del agente:** invocar W9/W2/W11/clasificador/dispatcher + increments de canal (Contact Reply, free-form multi-burbuja, audio).
3. **Cutover de datos CAPI:** migrar folios históricos · rotar token · swap de webhooks · activar `mf7VQJelfieCDJ5r`+`4HgMkK34xqITULM3`.
4. **Activar nurturing/rescate:** templateId por programa · política recontacto §8 · activar despachador+rescate+barrido.
5. **Correo W14:** definir métrica + destinatario · activar.
6. **sessionKey `+`/sin-`+`** reconciliado · **swap + limpieza** de los 14 originales y descartados · baja de credenciales Airtable+Clientify.

**Cuando los 12 pasos del §3 del doc canónico estén ✅ → no falta nada en n8n.**
