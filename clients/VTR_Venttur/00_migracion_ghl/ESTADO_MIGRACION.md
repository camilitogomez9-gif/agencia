# Estado de Migración — Venttur → GHL

> Este archivo se actualiza al final de cada sesión de trabajo. Si continuás desde una sesión nueva, leé esto primero.

**Plan maestro:** `planes/el-cliente-venttur-quiere-inherited-stardust.md` (guardado en `~/.claude/plans/`)
**Última actualización:** 2026-09-17 (noche) — cierre de sesión export Clientify. Ver §"🔴 RETOMAR MAÑANA (2026-09-18)" abajo.
**Fecha objetivo de cutover CONFIRMADA (reunión 15/9): 18 o 19 de septiembre de 2026**, con ventana de testing hasta el 25/9. Deadline económico: Clientify renueva 26-27/9 (no se toca sin coordinar con el cliente). **Anterior "15 de septiembre" quedó atrás por atraso mutuo.**

---

## 🔴 SESIÓN 2026-09-18 (noche) · Snapshot Clientify integrado + inventario para migración

**Camilo entregó su zip** (`/Users/camilo/Downloads/Clientify (1).zip`) con Andrés + Max completos. Merge aplicado con `scripts/utilities/merge-camilo-snapshot.py --apply`: 19 archivos nuevos + 2 landings.md sobrescritos (Andrés y Max, Camilo cargó las URLs con IDs). Bug de encoding NFD del zip resuelto vía remap `Andr├®s → Andrés`. **Diego descartado oficialmente** — sus 7 flujos legacy no se bajan a screenshots.

**Fix de naming aplicado** con `scripts/utilities/fix-naming-clientify-snapshot.py --apply`: 64 renames — corrigió (a) 6 `_notemplate_*.png` que tenían sidecar `.txt` → renombrados a `_freetext_`; (b) 1 `_continuacion_` → `_accion3_` (nueva subcategoría de la convención); (c) 57 slugs con espacios parasitarios → snake_case. Convención ampliada a **8 prefijos**: `_notemplate_`, `_freetext_`, `_lanzador_`, `_accion_`, `_accion2_`, `_accion3_`, `_unknown_`, y sin prefijo (= plantilla).

**Auditor (Pieza 3) ejecutado** con `scripts/utilities/audit-clientify-flows-vs-templates.py`. 3 owners · 9 sub-carpetas · 4 sub-sub-carpetas de Max (Rescate No show por programa) · 71 screenshots clasificados · 0 mismatches. Outputs canónicos:

| Doc | Uso |
|---|---|
| `06_docs/mapeo-flujos-plantillas-2026-09-18.md` | Matriz por sub-carpeta con las 6 categorías + lista de plantillas Meta no referenciadas (huérfanas) |
| `06_docs/inventario-flujos-clientify-2026-09-18.md` | Input directo para Etapa 4 GHL — cada flujo → cómo se reconstruye |
| `06_docs/plantillas-waba-rodrigo-a-reaprobar-2026-09-18.md` | 🔴 **Subset crítico:** 12 plantillas del WABA de Rodrigo (`141523652373940`) que hoy disparan flujos operativos y hay que **reaprobar en el WABA del bot** (`1931874540684022`) — 24-72h por plantilla, empezar YA |

**Las 12 plantillas a reaprobar** (fuente: `plantillas-waba-rodrigo-a-reaprobar-2026-09-18.md`):
- `confirmacion_0_cita_internados_2026`, `confirmacion_p1_boarding`, `formulario_aa`, `formulario_aafamilia`, `formulario_boarding`, `mensaje_1_seguimiento_ema`, `rescate2_noshow_aafamilia`, `rescate2_noshow_internado`, `rescate2_noshow_pathway`, `rescate2_noshow_summercamp`, `seguimiento_ema_dia_10_3`, `seguimiento_ema_dia_15`

Body real de cada una está en el `.md` — se puede submitear tal cual al WABA del bot vía Meta BM UI o `POST /{waba}/message_templates`.

**Bloqueante actualizado:** `B-07 templates Meta` pasa de "1 plantilla" a "12 plantillas del WABA Rodrigo + `formulario_boarding_followup` original". Con 24-72h por plantilla y cutover Clientify el 26-27/9 (8-9 días), **el submit tiene que arrancar ya**.

---

## 🔴 SESIÓN 2026-09-18 (mediodía) · Restructuración del snapshot Clientify + revisita WABA de Rodrigo

**Hallazgo #1 (mañana) — las carpetas de Clientify son compartidas entre cuentas.** Al abrir con Mauricio, Andrés o Rodrigo, se ven las MISMAS carpetas de Landings y Flujos. Lo que varía es el owner (Propietario / Creada por).

**Reestructura aplicada en `/Users/camilo/Downloads/Clientify/`:**
- Estructura pasa de `Mauricio/`, `Andres/`, `Rodrigo/` (por cuenta de login) a `<Owner>/` (por dueño de carpeta).
- 5 owners detectados: **Mauricio** (7 landings + 6 flujos), **Andrés** (2 landings + 0 flujos), **Rodrigo** (0 landings + 3 flujos), **Diego Matus** (0 landings + 7 flujos legacy), **Max Almonte** (6 landings + 3 flujos).
- Redivisión de trabajo: **la agencia = Mauricio + Rodrigo · Camilo = Andrés + Max + Diego**.
- Los 7 flujos de Diego se preservan como snapshot (marcados legacy en Pieza 3, decisión final en Etapa 4 GHL con Mauricio).

**Hallazgo #2 (tarde) — el WABA de Rodrigo `141523652373940` NO es legacy pasivo.** Los primeros screenshots bajados de flujos de Max (`Max/Confirmaciones de citas/`) revelan que dispara plantillas del WABA de Rodrigo (`confirmacion_p1_boarding`, `confirmacion_0_cita_internados_2026`), no del bot. O sea: cuando Clientify se apague, los flujos de confirmación de cita se rompen. La decisión del 17/9 ("WABA de Rodrigo muere con Clientify sin consecuencias") era incorrecta.

**Decisión 18/9 — Opción A: consolidar en el WABA del bot.** Recrear los flujos de Max (y cualquier otro que dispare plantillas del WABA de Rodrigo) en GHL apuntando al WABA `1931874540684022`. Implica **reaprobar en Meta** las plantillas del WABA de Rodrigo que se usen efectivamente en flujos operativos — mínimo `confirmacion_p1_boarding` y `confirmacion_0_cita_internados_2026`, probable más. Ventana Meta 24-72h por plantilla. Descartada Opción B (migrar ambos WABAs a GHL) por complejidad de canal dual. Descartada Opción C (send free-form dentro de sesión) por riesgo si la confirmación llega >24h después del último inbound.

**Impacto en cronograma:** hay que empezar YA a submitear las plantillas de confirmación al WABA del bot para tener margen. El auditor (Pieza 3) va a reportar la lista completa de plantillas del WABA de Rodrigo que se usen en flujos — esa es la lista a reaprobar.

**Convención de screenshots ampliada (18/9):** se sumaron 2 prefijos a los 5 existentes: `_lanzador_` (detalle del modal "Editar lanzador") y `_accion_` (detalle del modal "Editar paso") — solo se bajan cuando el modal expone parámetros no visibles en la vista principal (importe, pipeline, etapa destino, propietario, moneda). Ver README + PROMPT-PARA-CLAUDE-DE-CAMILO en `/Users/camilo/Downloads/Clientify/`.

Contenido del turno anterior (`🔴 RETOMAR`) sigue vigente sobre arquitectura GHL y piezas del plan — solo cambian: (a) organización física del snapshot, (b) tratamiento del WABA de Rodrigo, (c) convención ampliada.

---

## 🔴 RETOMAR (cierre 2026-09-17) — contexto vigente

### Qué se hizo hoy (sesión `harmonic-prancing-raven`)

1. **Verificación exhaustiva de la API pública de Clientify** — probados 40+ endpoints. Confirmado: no expone landings HTML, calendarios (`meetings`), ni pasos internos de flujos. Sí expone contactos/deals/tareas (ya bajado en snapshot 24/7) y **29 superforms embebibles** (endpoint `/v1/webforms/` — dumpearlo cuando arranque Etapa 4 GHL).
2. **Los 3 WABAs de Venttur resueltos con Graph API** (evidencia técnica):
   - `1931874540684022` = Venttur | Agente de IA · `+52 1 33 2627 4502` · 50 plantillas · **WABA operativo del bot, el que migra a GHL** (era el correcto documentado desde agosto).
   - `1066425326128804` = alias solution ID auto-generado hoy al conectar la app "Venttur Marketing API"; artefacto, descartable.
   - `141523652373940` = Venttur Education & travel · `+52 1 33 1944 2476` (número de Rodrigo) · 42 plantillas · uso legacy Clientify · muere con Clientify.
3. **92 plantillas Meta dumpeadas** (50 + 42) en `06_docs/plantillas-meta-live-{WABA_ID}-2026-09-17.{json,md}`. Cero drift vs borradores locales.
4. **Arquitectura landings + calendarios definida**: todo-en-GHL nativo (Funnels + Round Robin Calendars), CNAME atómico con staging previo, paths de `promo.venttur.com/*` preservados exactos (bloqueante crítico: los tienen hardcodeados las 50 plantillas Meta aprobadas — cambio = reaprobación 24-72h).
5. **Naming convention snapshot export**: Opción 1 (nombre de archivo `.png` = nombre exacto de plantilla Meta que dispara el flujo, con prefijos `_notemplate_` y `_unknown_` para casos especiales).
6. **Working set del snapshot en `/Users/camilo/Downloads/Clientify/`** (fuera del repo, no versionado):
   - `README.md` — instrucciones generales.
   - `PROMPT-PARA-CLAUDE-DE-CAMILO.md` — prompt autocontenido para la sesión de Claude de Camilo.
   - `Mauricio/{landings y calendarios, flujos de trabajo}/` — sub-carpetas de flujos creadas (15 vacías) + `landings.md` con títulos + 13 URLs cargadas (Estudia y trabaja Australia + Registros La Garenne) con IDs auto-extraídos.
   - `Andres/`, `Rodrigo/` — vacíos.

### Qué falta para arrancar mañana

**Bloqueo actual:** esperar que Mauricio pase los credenciales de las 3 cuentas de Clientify (Mauricio + Andrés + Rodrigo). Con eso, la agencia y Camilo pueden entrar a bajar screenshots.

**División de trabajo mañana:**
- **la agencia** bajá el resto de `Mauricio/` (13 sub-carpetas de landings sin URLs todavía, screenshots de flujos con naming Opción 1).
- **Camilo** trabaja sobre `Andres/` y `Rodrigo/` con su propia sesión de Claude. Recibe el zip actualizado con el prompt del turno 20, se autoservucia.
- **Al final** Camilo comprime `Andres/` + `Rodrigo/` y se lo pasa a la agencia. la agencia integra a su copia local y corre auditor Pieza 3.

### Comandos útiles para retomar

```bash
# Cargar token Meta (renovar si expiró — dura 2h por Graph API Explorer)
source /Users/camilo/Downloads/camilo-workspace/.env

# Bajar plantillas (idempotente, sobrescribe con la fecha del día)
python3 scripts/utilities/fetch-vtr-whatsapp-templates.py 1931874540684022  # bot
python3 scripts/utilities/fetch-vtr-whatsapp-templates.py 141523652373940   # Rodrigo (legacy)

# Auto-extraer IDs de landings después de agregar URLs
python3 scripts/utilities/extract-clientify-landing-ids.py "/Users/camilo/Downloads/Clientify/Mauricio/landings y calendarios/landings.md"
```

### Piezas pendientes del plan `~/.claude/plans/harmonic-prancing-raven.md`

- **Pieza 1** (`extract-clientify-landing-ids.py`): ✅ escrita y probada con 13 URLs. Correr cada vez que se agreguen URLs.
- **Pieza 2** (`fetch-vtr-whatsapp-templates.py`): ✅ escrita y ejecutada. 92 plantillas dumpeadas.
- **Pieza 3** (`audit-clientify-flows-vs-templates.py`): 🟡 **por escribir cuando esté completo el snapshot** (los 3 owners con screenshots + `landings.md` completos). Cruza filenames de screenshots vs las 92 plantillas canónicas, genera `mapeo-flujos-plantillas-YYYY-MM-DD.md` + `inventario-flujos-clientify-YYYY-MM-DD.md`.
- **Pieza 4** (rebuild landings/calendarios en GHL): documentada en el plan, ejecución en Etapa 4 GHL post-cutover WhatsApp. ~40-55h esfuerzo estimado.
- **Pieza 1.5** (fetcher de superforms): 🟡 diferida hasta arranque Etapa 4.

### Cutover WhatsApp (paralelo, independiente de este export)

Independiente de este snapshot: el cutover del canal WA (BSP migration Meta → GHL del `1931874540684022`) sigue su calendario propio 18-19/9 según `06_docs/guia-recta-final-cutover-2026-09-16.md`. Este export de Clientify solo tiene que estar listo antes del corte de Clientify (26-27/9).

---

> 📄 **Fuente de verdad operativa única hasta 27/9 EOD:** `06_docs/guia-recta-final-cutover-2026-09-16.md` — camino crítico próximas 48h, runbook D-day 18/9 + D+1, rollback playbook, testing continuo 20-25/9, corte Clientify 26-27/9. El `SINCRONIZACION-2026-09-16.md` queda como snapshot histórico del merge inicial (Bloques 0-5), reemplazado por la guía recta final.

---

## Estado actual

| Etapa | Estado | Modelo usado | Notas |
|-------|--------|--------------|-------|
| **Etapa 0** — Recolección de inputs | ✅ COMPLETA (2026-07-24) | (acción usuario) | n8n **14/14 workflows** + datos de las 5 plataformas exportados: Clientify (6.968 contactos/2.338 deals/266 companies/22 cfields) · ManyChat (16 flows/5 tags/13 cfields + contenido interno vía screenshots) · Supabase (schema + 10 muestras convo) · Airtable (6 CSVs). Snapshot en `00_inputs/vtr-data-snapshot-2026-07-24.json`. Restante no bloqueante: keyword triggers CTWA + config canal WA (ManyChat), landings (parcial). Meta/GHL no bloqueantes por decisión del usuario. **✅ 2026-08-18 PM: 3 de los 4 datos del canal WA recibidos.** Número del bot `+52 1 33 2627 4502` (Guadalajara, chip de Venttur — coherente con el quirk MX 52→521 documentado); WABA ID `1931874540684022` (verificado 2026-09-17 vía Graph API; ver §"Actualización 2026-09-17 (tarde)" para el detalle sobre los 3 WABAs distintos y por qué este es el operativo del bot). **Único pendiente:** desambiguar si el WABA está bajo el Business Manager de **Venttur** (portable, escenario A) o de **ManyChat** (NO portable, escenario Collazo). Resolución en 2 min desde `business.facebook.com` de Venttur → Configuración → Cuentas → Cuentas de WhatsApp. Verificación de negocio también pendiente |
| **Etapa 1** — Deducción de lógica actual | ✅ COMPLETA (2026-07-24) | Opus 4.8 (orquestación multi-agente) | Los 6 documentos de `01_logica_actual/` **reescritos por completo** con los inputs completos de Etapa 0 (14 workflows analizados nodo-por-nodo + system prompt del agente + snapshot de datos + 6 CSVs + schema Supabase). Corrigen los errores materiales de la versión de mayo (sobre todo "no hay agente IA" → sí hay agente conversacional "Mauricio"). Ver "Hallazgos de Etapa 1" abajo |
| **Etapa 2** — Validación con cliente | 🟡 **CASI CERRADA (2026-08-18)** — 9 de 11 respondidas + 2 parciales (A8 cadencia, A10 métrica) | — | **Respuestas del cliente integradas.** `cuestionario-venttur-2026-07-24.md` es ahora el **registro firmado por Mauricio (2026-08-17)**; el máster interno `preguntas-cierre-2026-07-24.md` tiene A1..A11 volcadas; los 6 docs de `01_logica_actual/` llevan bloque "🆕 Validación con el cliente". **Las 2 bisagras 🔴 quedaron resueltas:** el pipeline de Clientify **se migra completo** (A1) y el canal/agendamiento se define sobre **8 calendarios GHL** (A7). **Rangos de precio: CERRADOS por la agencia el 18/8** (Internados 50-130k). **Cerrado el 18/8 PM: los 5 puntos de Sección A + los 3 de Sección B**. La única desambiguación pendiente es la del WABA (ver Etapa 0). Los rangos de precio de los 3 huérfanos quedaron como "-" y se interpretan como: el bot no da precio ahí y pasa a asesoría → `puntos-abiertos-ronda-2-2026-08-18.md`. **Ninguno bloquea el diseño de arquitectura** (son prompt del agente y reglas de negocio, no topología) |
| **Etapa 3** — Diseño arquitectura GHL | ✅ **COMPLETA (2026-09-01)** | Opus 4.8 (multi-agente + verificación adversarial) | **12 docs en `03_arquitectura_ghl/`** (00-11), método quirúrgico 1:1, verificados en 3 rondas contra el sistema real. Ver §"Etapa 3 — Diseño de arquitectura GHL" abajo |
| **Etapa 4** — Guía paso a paso | 🟢 **EN CURSO (2026-09-03)** — 13 módulos + sandbox corrido | Opus 4.8 | Los 13 docs de `04_guia_migracion/` (00-12). **Sandbox de API corrido (`01 §Resultados`):** 6 PASS + A2 FAIL-esperado + A5 parcial + B2/B3/B1/B4/C1 manuales. B3 = Opción A. Falta: checks manuales (B1/B4/C1 UI + B2/B3 con nº de test) + decisiones de cliente (owners, tope-2). Ver §"Etapa 4" abajo |
| **Etapa 5** — Ejecución y monitoreo | 🟢 **EN CURSO (2026-09-03)** | Opus 4.8 | Plan `planes/vtr-ghl-ejecucion-etapa5-2026-09-03.md`. **Fase 0 ✅** (PIT/n8n verificados; estado GHL/n8n fotografiado; 14 workflows VTR re-exportados — main vivo `k3aivKSP67S97IHn` 39 nodos). **Fase 1 🟢 parcial** (por API en la sub-cuenta `7aXb4JCKsWV5nUyBXeSF`: **56 custom fields + 4 tags + 20 pipelines** creados, read-back verificado, idempotente; calendarios/custom-values diferidos, usuarios gated). **Fase 2 ✅** (ETL: unión deduplicada ~8.525 + reconciliación que corrobora el diseño + auditoría de migrabilidad Clientify). **Fase 3 🟡 preparado** (scripts + dry-run validados: 2.338 opps resuelven pipeline+stage al 100%; masivo 🛑 gated). **Fases 4/5 registradas** (build n8n enfocado gated en B1/B2; canal/WABA/templates/huérfanos/decisiones de cliente). Log vivo + bloqueantes: `05_ejecucion/REGISTRO-EJECUCION.md`. **Nada outward-facing ni de canal tocado; todo lo escrito es estructura reversible.** |

---

## Actualización 2026-09-17 (tarde) · Los 3 WABAs de Venttur — verdad canónica vía Graph API

Al conectar Meta Graph API se descubrió que Venttur tiene **tres IDs de WABA** vinculados en su Business Portfolio, pero solo dos son WABAs distintos y solo uno es el operativo del bot. Verificación técnica directa contra `graph.facebook.com/v20.0/` con token de MAXIMUS-IA (2026-09-17 tarde).

| WABA ID | Nombre | Número | Template namespace | Plantillas | Rol |
|---|---|---|---|---:|---|
| **`1931874540684022`** | Venttur \| Agente de IA | **+52 1 33 2627 4502** (`phone_id 733178679874597`) | `4d84d458_f03e...` | **50** | ✅ **WABA operativo del bot** — el que usa ManyChat, el que migra a GHL |
| `1066425326128804` | Venttur \| Agente de IA (mismo) | +52 1 33 2627 4502 (mismo `phone_id`) | `71f739b4_8e13...` | 50 idénticas | Solution WABA / alias auto-generado por Meta al conectar la app "Venttur Marketing API" el 17/9. Artefacto de la app; desaparece al desconectarla. **No requiere acción.** |
| `141523652373940` | Venttur Education & travel | **+52 1 33 1944 2476** (`phone_id 136823656179946`) | `ff807a31_329b...` | 42 (0 overlap con el bot) | **Número personal de Rodrigo** (ya documentado en `03_arquitectura_ghl/06_canal_whatsapp_y_agente.md §F.3` como KEEP dato de negocio). Probable canal de recordatorios/formularios de Clientify. Muere con Clientify. |

**Cómo se resolvió la ambigüedad:** 4 GETs contra Graph API — (1) `phone_numbers` de cada WABA confirmó qué número tiene cada uno; (2) `message_template_namespace` distinto entre `1931…` y `1066…` con set de nombres de plantillas idéntico confirmó que son alias del mismo WABA raíz; (3) `owner_business_info` confirmó los tres bajo el mismo BM `venttur_` (`231733062811233`); (4) 50 vs 42 vs 42 plantillas con cero overlap entre el bot y Rodrigo cerró la interpretación.

**Decisión de migración (2026-09-17):** migrar a GHL **solo el `1931874540684022`** con sus 50 plantillas. El `141523652373940` (Rodrigo) queda como legacy y muere con Clientify — Rodrigo puede conservar su número personal para atención ad-hoc fuera del sistema. El `1066425326128804` es descartable (solution ID auto-generado). Restablece la doc del repo desde agosto que ya tenía `1931874540684022` como fuente de verdad.

**Aclaración histórica:** al mediodía del 2026-09-17 se hizo un `sed` global reemplazando `1931874540684022` → `141523652373940` en 17 archivos asumiendo que el ID viejo era incorrecto (la agencia había compartido captura del WABA de Rodrigo pensando que era el mismo asset). A la tarde, con evidencia técnica de Graph API, se revirtió: el `1931874540684022` era correcto desde agosto. Las 9 notas de "corregido 2026-09-17" que quedaron autoreferenciales fueron limpiadas. Esta sección queda como registro canónico del ida y vuelta.

**Outputs vivos:**
- `clients/VTR_Venttur/06_docs/plantillas-meta-live-1931874540684022-2026-09-17.json` — dump crudo de las 50 plantillas del bot.
- `clients/VTR_Venttur/06_docs/plantillas-meta-live-1931874540684022-2026-09-17.md` — tabla legible.

**Script:** `scripts/utilities/fetch-vtr-whatsapp-templates.py` acepta el WABA como argumento CLI. Default = `1931874540684022` (bot). Para bajar el de Rodrigo si algún día se necesita: `python3 ... 141523652373940`.

---

## Actualización 2026-09-17 · decisión arquitectura landings + calendarios

Definido cómo se migran las **40 landings + 8 calendarios** de Clientify a GHL. Contexto: la API pública de Clientify **no expone** landings HTML, calendarios (`meetings`), ni pasos internos de flujos — verificado exhaustivamente con 40+ endpoints probados (turno 10, sesión `harmonic-prancing-raven`). Solo devuelve datos operativos (contactos/deals/tareas ya en snapshot 24/7) y **29 superforms con script embebible** (`/v1/webforms/`). Todo lo demás requiere export manual.

**Arquitectura de destino: todo-en-GHL nativo.**

- 40 landings → **GHL Funnels** con Nested URL Paths (Beta), preservando **paths exactos** de `promo.venttur.com/*` que hoy están hardcodeados en las **50 plantillas Meta del bot** (`06_docs/plantillas-meta-live-1931874540684022-2026-09-17.md`). Un cambio de path dispara reaprobación Meta (24-72h) y rompe el outreach en producción — **este es el bloqueante crítico a respetar**.
- 8 calendarios → **GHL Round Robin Calendars** (uno por programa, disponibilidad compartida entre asesores — coincide con decisión del cliente de Ronda 2). Slugs finales definidos ANTES de compartir a WhatsApp (GHL no da redirect automático al cambiar slug).
- Dominio `promo.venttur.com` → CNAME a `sites.ludicrous.cloud` (target de GHL). SSL auto. Cloudflare en modo DNS-only (proxy no soportado).

**Trampa central:** un subdominio solo puede servir UNA plataforma a la vez. **Cutover atómico obligado** — no hay coexistencia Clientify + GHL en `promo.venttur.com`.

**Estrategia zero-downtime:**
1. **Semanas -3 a -1:** buildear 40 funnels + 8 calendarios en subdominio staging (`staging-promo.venttur.com` CNAME → GHL desde ya). QA end-to-end.
2. **-48h:** bajar TTL del CNAME `promo.venttur.com` a 60 segundos.
3. **Día D:** agregar `promo.venttur.com` como dominio en GHL, relinkear cada funnel a los mismos paths que en staging, flip CNAME, verify (~5 min).
4. **Post-D:** setear 301 redirects granulares como red de seguridad para paths no capturados. Auditar logs 48h.
5. **D+2:** apagar Clientify (26-27/9).

**Estimación esfuerzo:** 40-55 horas (rebuild manual: sin importador Clientify→GHL; GHL solo importa desde ClickFunnels). Distribución: 1-2h setup dominio + 6-10h calendarios + 20-30h landings (3-4 templates maestros clonados) + 8-12h QA.

**Descartado:** ruta mixta Vercel/Netlify + GHL Calendars embebidos. Razón: el equipo del cliente (Mauricio, Max, Andrea, Rodrigo, Daniela) no es técnico y perdería el editor visual autoservicio. Analytics unificado en GHL vale más que la flexibilidad de código propio en Vercel para este caso.

**Fuentes canónicas:** `/Users/camilo/.claude/plans/harmonic-prancing-raven.md` §Pieza 4 · [GHL Domain Setup](https://help.gohighlevel.com/support/solutions/articles/48001153720) · [Nested URL Paths (Beta)](https://help.gohighlevel.com/support/solutions/articles/155000005779) · [Round Robin Calendars](https://help.gohighlevel.com/support/solutions/articles/155000001485).

**Snapshot manual en curso:** `/Users/camilo/Downloads/Clientify/{Mauricio,Andres,Rodrigo}/` — screenshots + sidecar `flow.yaml` por flujo (decisión de arquitectura del snapshot: Opción 2 sidecar, ver README ahí).

---

## Actualización 2026-09-16 · sincronización tri-fuente + Bloque 0 staging

Convergencia de 3 líneas de trabajo paralelas: (1) Camilo consolidó el 11/9 con 8 artefactos nuevos que ya vivían fuera del repo, se integraron al WS el 16/9 desde `/Users/camilo/Downloads/_RECONCILIACION-2026-09-11.zip`; (2) la agencia+Claude hicieron el incidente Nahe entre el 15 y 16/9 (Fase 3 fix estructural + Fase 6 alertas + Fase 7 docs GHL); (3) reunión con cliente el 15/9 desbloqueó 12 puntos que ajustan el diseño de la migración. Detalle completo del merge: `SINCRONIZACION-2026-09-16.md` (temporal, sunset 26/9).

**Desbloqueos de la reunión 15/9 aplicables al diseño de la migración:**

- **WABA `1931874540684022` — ✅ ESCENARIO A CONFIRMADO.** Venttur compró el número directamente (no fue provisto por ManyChat vía ChatRace y después migración por Agustín — el número sigue siendo de Venttur). **Portable a GHL vía "Migrate from an existing BSP"**. Downtime esperado: minutos. Deadline vencido de 1/9 queda sin efecto. Reemplaza al bloqueante #1 del `PENDIENTES-MIGRACION-2026-09-11.md`.
- **Cutover ajustado a 18-19/9**, testing hasta 25/9, Clientify renueva 26-27/9. El 15/9 original se atrasó por (a) incidente Nahe descubierto el 15/9 mañana, (b) sincronización de tracks pendiente. Todos los docs siguen citando "15/9" — deuda documentada en `SINCRONIZACION-2026-09-16.md §Documentos vivos sin actualizar`.
- **Diego sale del ruteo automático.** Solo Rodrigo y Andrés atienden citas. Los 47 contactos + 131 deals de Diego Matus quedaron reasignados a Juan José Alfaro (decisión ya aplicada durante Fase 3 de la migración según `REGISTRO-EJECUCION.md`).
- **Programas por asesor confirmados:** Rodrigo = Internados / Año Académico con Familia / Summer Camp. Andrés = Pathway / Gap Year (idiomas).
- **"Cualificado" = TAG del contacto**, NO etapa del pipeline operativo del bot. Cierra la "decisión abierta" de `03_arquitectura_ghl/03_datos_pipeline_deals_estado.md §Cualificado`. El clasificador batch gpt-4o-mini que ya vive en el staging (workflow `Xmyoewwa1W5gm1fy`) escribe el tag `SAf2PNSjPNNYJisUSAFq`.
- **Modelo del agente = gpt-4o**, no se cambia por ahora. Mauricio preguntó por actualizar; se dejó como auditoría post-migración.
- **Recontact policy post-cutover:** primer contacto solo a leads con `Link asesoría enviado = true` + `Agendan cita = false`. NO spam a los 5.000+ del embudo total. Falta documentar en `03_arquitectura_ghl/09_nurturing_rescate_reengagement.md`.
- **2FA + chip 2FA-only:** ya configurado en el celular del cliente sin WhatsApp instalado (régimen bueno, hereda la política Collazo). Reconciliar con la regla "desactivar 2FA para migrar" del `04_guia_migracion/05_templates_meta_waba.md §5.0` — el chip queda 2FA-only durante todo el proceso.
- **Access Clientify:** 3 accesos separados (Mauricio + Rodrigo + Andrés). Mauricio comparte credenciales de Rodrigo y Andrés para acceder a sus calendarios embebidos en Clientify.
- **Aventureras** — nuevo hallazgo: ~20-25 aventureras × 5 landings + 5 calendarios embebidos por aventurera = ~100-125 landings de Clientify. Cada aventurera tiene su calendario propio ligado al calendario del asesor para trackear la atribución. **Contradice el diseño actual de `03_arquitectura_ghl/07_agendamiento_calendarios.md §1/§5`** (8 calendarios GHL fijos). Requiere rediseño previo al cutover — mecanismo de atribución vía custom field `atribuida_a_<aventurera>` (query string o hidden field en el embed GHL). Ver Bloque 2 del plan `~/.claude/plans/perfecto-antes-de-cerrar-zazzy-twilight.md`.
- **Dominio destino GHL:** cliente elige subdominio (study.venttur.com o go.venttur.com o similar; `promo.venttur.com` muere con Clientify). Falta decisión antes del 18/9 — impacta plantillas Meta que hardcodean URL.
- **MCP/API GHL para Camilo:** doc de handoff creado en `06_docs/handoff-camilo-mcp-ghl.md` (PIT + patrón `.env` gitignoreado + endpoints útiles + IDs canónicos + regla User-Agent obligatorio).

**Estado del staging n8n al 2026-09-16 17:02 UTC (Bloque 0):**

Workflow `[Venttur] GHL staging (Telegram test)` (`3sLd7KY3o8I7NvXi`): 12 → 13 nodos. Prompt v2.0 → v2.1 con REGLA ABSOLUTA #8 "No agendo yo" + nodo Code `Detectar promesa fantasma` insertado entre `Agente IA WPP` y `Enviar Telegram`. Adaptado al pipeline sin splitter (trabaja sobre `$json.output` crudo). El staging ya no puede pasar el bug de Nahe al cutover 18-19. Snapshots + tests golden 8/8 + smoke 3/3 en `03_workflows/staging-2026-09-16-post-replica-guardrail/`. Contrato de diseño heredable a GHL post-cutover en `03_arquitectura_ghl/06 §9` (Fase 7). Detalle en `SINCRONIZACION-2026-09-16.md §Bloque 0`.

**Los 8 artefactos de Camilo del 11/9 (integrados al WS el 16/9):**

- `_RECONCILIACION-2026-09-11.md` (raíz) — explica la reconciliación de dos tracks.
- `00_migracion_ghl/PENDIENTES-MIGRACION-2026-09-11.md` — lista viva de 20 pendientes (varios resueltos por la reunión del 15/9; ver `SINCRONIZACION §Pendientes consolidados`).
- `06_docs/plantillas-meta-borradores-2026-09-11.md` — 16 plantillas Meta redactadas por Camilo. Falta subir a Meta post-portabilidad WABA (aprobación 24-72h).
- `06_docs/plantillas-meta-nurturing-2026-09-11.md` — plantillas de nurturing (bonus).
- `06_docs/hallazgo-cruce-agenda-seguimiento-2026-09-11.md` — hallazgo de Camilo: los flows ManyChat `Agenda` y `Seguimiento agenda` están **cruzados por nombre**. Antes de tocar esos 2 flows en el cutover, mapear por contenido, no por nombre.
- `06_docs/plan-rotacion-secretos-2026-09-11.md` — plan de rotación de OpenAI key n8n y Meta CAPI Airtable.
- `06_docs/clientify-que-respaldar-antes-de-apagar.md` — aviso para el cliente sobre qué respaldar antes del apagado de Clientify.
- `03_workflows/venttur-staging-agent-cerrada-v1.json` — workflow con la tool `cerrar_conversacion` (ya activa en el staging vivo, este archivo es backup).

**Archivos del track divergente de Camilo (SUPERSEDED, NO copiados al WS):** ver `_RECONCILIACION-2026-09-11.md §Archivos del track divergente` — track del bot duplicado de ManyChat que quedó obsoleto. No usar como base. Los archivos siguen disponibles en el zip original si se necesitan puntualmente.

---

## Etapa 3 — Diseño de arquitectura GHL (✅ 2026-09-01)

**12 docs en `03_arquitectura_ghl/`**, método quirúrgico de HPF (traducción 1:1, no rediseño; preferencia n8n; solo se descarta lo muerto/duplicado/innecesario con argumento). Cada doc tiene su tabla de traducción (una fila por elemento del sistema actual) + banderas + footer de corroboración contra `00_inputs/`.

| Doc | Cubre | Riesgo |
|---|---|---|
| `00_overview` | método, stack, formato, registro de descartes, banderas, caveats | — |
| `01_taxonomia_programas` | 8 canónicos + crosswalk + remapeo de cohortes | prereq |
| `02_datos_contactos_identidad` | Airtable+Clientify+ManyChat → GHL Contacts (merge, ≈8.575) | 🔴 #1 |
| `03_datos_pipeline_deals_estado` | ~19 pipelines Clientify + 4 capas de estado → Opportunities | 🔴 #2 |
| `04_datos_campos_tags` | CF (22+13) + tags → GHL, lista canónica | 🟡 |
| `05_datos_capi_atribucion` | Folios/Programas/Mensajes → **se quedan en n8n** | 🟡 |
| `06_canal_whatsapp_y_agente` | canal, agente Mauricio, templates, handoff, 1 número | 🔴 #3 |
| `07_agendamiento_calendarios` | 8 calendarios + confirmación + recordatorios 24h/1h | 🟡 |
| `08_workflows_n8n` | los 14 workflows → se-queda/reconstruye/descarta | 🟡 |
| `09_nurturing_rescate_reengagement` | 4 cadencias → 1 despachador n8n + tope-2 + Cerrada | 🟡 |
| `10_programas_nuevos` | 3 huérfanos de cero | 🟢 scope |
| `11_flujo_end_to_end` | diagrama Mermaid del lead post-migración | síntesis |

**Verificado adversarialmente en 3 rondas** (fidelidad de datos con jq/python contra el snapshot y los CSVs + método quirúrgico + consistencia con las decisiones del cliente). Corrección material atrapada: los deals de Clientify están en **~19 pipelines, no ~10** (80% Expired).

**Lo que la Etapa 4 hereda:**
- La **lista de asunciones de plataforma GHL a validar en sandbox** (`00` §7.10, 10 items): dedup por teléfono, fechas históricas seteables, disponibilidad compartida entre calendarios de un asesor, Contact Reply trigger, free-form send, template por API, media de audio, pausar bot por-contacto, query de Contacts por custom field, trigger de booking + query de appointments. **Resolver antes del import.**
- **Decisiones de la agencia pendientes de OK del cliente:** tope global de 2 toques + prioridad entre secuencias (`09` §8); y "lo escribe el agente al cerrar el descubrimiento" para `Cualificado` (`03` §5).
- **Caveats de cutover (no de diseño):** portabilidad WABA (deadline 1/9), auditoría de migrabilidad de Clientify, textos/assets de los 3 programas huérfanos.

---

## Etapa 4 — Guía paso a paso (🟢 EN CURSO 2026-09-03)

**13 módulos en `04_guia_migracion/`** (00-12), método quirúrgico, corroborados contra el sistema real (snapshot 13,7 MB + 14 JSON + CSVs), no contra la prosa. Estructura tipo HPF.

| # | Módulo | Riesgo/Gate |
|---|---|---|
| 00 | `00_indice` — torre de control: camino crítico, calendario de gates, accesos, secretos, decisión B3 | — |
| 01 | `01_sandbox_validacion` ⭐ — **gate maestro**, 13 checks bloqueantes (+1 opcional) | gate |
| 02 | `02_setup_ghl_base` — sub-cuenta, owners→usuarios, custom fields, tags | 🟡 |
| 03 | `03_pipelines_ghl` — 20 pipelines comerciales verbatim + operativo del bot | 🔴 |
| 04 | `04_calendarios_y_agendamiento` — 8 calendarios + confirmación + recordatorios | 🟡 |
| 05 | `05_templates_meta_waba` — portabilidad WABA + templates | 🔴 |
| 06 | `06_datos_preproceso_import` — canonicalización + merge → ~8.575 + auditoría Clientify | 🔴 |
| 07 | `07_n8n_agente_canal` — main + agente + tools + audio + handoff | 🔴 |
| 08 | `08_n8n_despachador` — despachador único (tope 2) + gate + Cerrada | 🟡 |
| 09 | `09_n8n_capi_formulario` — CAPI (se queda) + formulario/landing | 🟡 |
| 10 | `10_programas_nuevos` — 3 huérfanos (deltas transversales) | 🟢 |
| 11 | `11_testing_precutover` — E2E + reuso de `testing-guide-v1` | 🟡 |
| 12 | `12_cutover` — coreografía 15/9 + gates + rollback | 🔴 |

**Verificación adversarial atrapó (no estaba en el diseño):** (1) faltaba el check de **moneda mixta MXN+USD** en el sandbox → agregado como A6; (2) hay **DOS Diegos** en los owners reales (Diego García de la Vega Delfín 289 deals + **Diego Matus** 47 contactos/131 deals, nunca distinguido en Etapa 3) + Niza/Juan José con deals pero baja actividad → `02` lo marca para cerrar con el cliente; (3) el **deadline de portabilidad WABA (1/9) ya venció** al 3/9 → `05`/`00` en rojo.

**Sandbox de API corrido (2026-09-03, sub-cuenta `7aXb4JCKsWV5nUyBXeSF`):** 6 PASS (A1 no-normaliza teléfono ✅, A3 abandoned ✅, A4 con corrección, A6 moneda ✅, B5 DND ✅, C2 endpoint ✅) · A2 FAIL-esperado (`dateAdded` no seteable por API → custom field) · A5 PARCIAL (teléfono ✅, custom field ✗ 400) · B2/B3 no ejecutados (mandan WA real) · B1/B4/C1 manuales. **Hallazgos operativos load-bearing:** (a) **UA obligatorio** (Cloudflare 1010) en todo HTTP a GHL; (b) Companies = endpoint **`/businesses/`** (no `/companies/`, sin CF); (c) búsqueda por `POST /contacts/search` con filtro anidado (`GET ?query=` no fiable); (d) 🆕 **`OPPORTUNITY_NO_DUPLICATE`** — un contacto con varios deals en un pipeline colisiona → activar "Allow Duplicate Opportunity" antes del import de los 2.338 deals. Credenciales GHL en `06_docs/ghl-credentials.md` (gitignored). Artefactos de juguete `ZZSBX` sin borrar en la sandbox.

**Lo que falta para cerrar Etapa 4 / pasar a Etapa 5:**
- **Checks de sandbox restantes:** B1 (Contact Reply trigger, UI) · B4 (audio, inbound) · C1 (disponibilidad compartida, UI + calendario personal) · B2/B3 (envío free-form/template — necesitan un número de test + OK) · A5 por custom field (hallar la sintaxis o usar índice Postgres). Ningún módulo que dependa de estos se cierra hasta resolverlos.
- **B3 ✅ DECIDIDO (2026-09-03): Opción A — cutover completo.** Todo migra el 15/9 (canal + agente + calendarios + los 2.338 deals + 266 companies + los 3 huérfanos completos), sin olas. la agencia había recomendado B (por olas) por el riesgo a T-12; el cliente eligió A. Guía actualizada (`00`/`03`/`06`/`10`/`12`).
- **Mapeo de owners ✅ RESUELTO (Mauricio 2026-09-03):** Diego Matus ya no está → sus 47 contactos + 131 deals se **reasignan a Juan José Alfaro** (colaborador activo, no se crea usuario para Matus); Niza Valeriano y Juan José son colaboradores activos; Diego García (289 deals) queda como usuario fuera del ruteo. Activos a crear: Mauricio · Rodrigo · Andrés · Max · Juan José · Niza · Diego García. **Falta solo:** los **emails** de esos 7 (para `POST /users/`). Detalle en `02 §2.2`.
- **Decisiones de cliente aún pendientes:** emails de los 7 owners · OK al tope de 2 toques + prioridad · OK a "Cualificado lo escribe el agente" · fallback 1-cal-por-asesor si C1 falla · textos de los 3 huérfanos + de confirmación/recordatorio.
- **Gates de terceros en el camino crítico:** portabilidad WABA (deadline vencido → desambiguar YA o chip nuevo), aprobación de templates Meta (24-72h), auditoría de migrabilidad de Clientify, textos/assets de los 3 huérfanos.

---

## Decisiones confirmadas (Etapa 0)

1. **n8n como cerebro:** se mantiene para lógica CAPI (SHA-256, lookups, Graph API POST)
2. **GHL reemplaza ManyChat:** canal WhatsApp nativo de GHL
3. **GHL reemplaza Clientify:** GHL CRM (Contacts + Custom Fields)
4. **Airtable se mantiene para CAPI:** tablas Folios CAPI y Programas CAPI siguen en Airtable (config de pixels, no CRM)
5. **Airtable Leads → GHL Contacts:** migración de datos, Airtable Leads se congela (read-only)

---

## Inputs disponibles

### Ya en el workspace

- [x] `meta-capi-venttur-v2.json` — Workflow CAPI principal (10 nodos, rama folio + CTWA)
- [x] `rescue-flow-implementation-guide.md` — Arquitectura completa del flujo de rescate (2 fases, 6 programas)
- [x] `rescue-flow-message-templates.md` — 12 templates de mensajes (6 programas × 2 fases)
- [x] `clientify-timeout-audit-2026-04-21.md` — Auditoría de problemas Clientify (justificación para eliminar)
- [x] `CLIENT_INFO.md` — Config del sistema, IDs, OKRs
- [x] Export ManyChat: 14 flows, 13 custom fields, 5 tags — `00_inputs/manychat-snapshot-2026-05-13.md`
- [x] Workflow JSON: `[Venttur]` (principal) — `00_inputs/wf-venttur-main.json`
- [x] Workflow JSON: `CAPI Registro Folio - Venttur` (`9yCbynoKDt9hgiBq`) — `00_inputs/wf-capi-registro-folio.json`
- [x] Workflow JSON: `Formulario Clientify - Venttur` — `00_inputs/wf-formulario-clientify.json`
- [x] Workflow JSON: `Meta CAPI - Venttur` (export fresco) — `00_inputs/wf-meta-capi.json`
- [x] Workflow JSON: `Actualizar 'Link enviado'` — `00_inputs/wf-actualizar-link-enviado.json`
- [x] Workflow JSON: `Confirmación de agenda` — `00_inputs/wf-confirmacion-agenda.json`
- [x] Workflow JSON: `Crear contacto Clientify y Airtable` — `00_inputs/wf-crear-contacto-clientify-airtable.json`
- [x] Workflow JSON: `Resumen, etiquetas, seguimientos` — `00_inputs/wf-resumen-etiquetas-seguimientos.json`
- [x] Workflow JSON: `Seguimiento agenda` — `00_inputs/wf-seguimiento-agenda.json`
- [x] Workflow JSON: `Correo Semanal` — `00_inputs/wf-correo-semanal.json`
- [x] CSV Airtable: Folios CAPI (4.003 filas) — `00_inputs/airtable-csvs/folios-capi.csv`
- [x] CSV Airtable: Leads (3.820 filas, incluye `ID Clientify` + `ID Manychat` — FK directas entre las 3 plataformas) — `00_inputs/airtable-csvs/leads.csv`
- [x] CSV Airtable: Programas CAPI (4 programas) — `00_inputs/airtable-csvs/programas-capi.csv`
- [x] CSV Airtable: Mensajes anuncios (24 anuncios → mensaje apertura → programa) — `00_inputs/airtable-csvs/mensajes-anuncios.csv`
- [x] CSV Airtable: Reporte semanal (37 semanas históricas agregadas) — `00_inputs/airtable-csvs/reporte-semanal.csv`
- [x] CSV Airtable: Tabla apoyo (2.114 filas, descartable según el cliente) — `00_inputs/airtable-csvs/tabla-apoyo-ignorar.csv`
- [x] Clientify: endpoints reales confirmados por inspección de código (base URL, auth, contacts/tags/notes) — ver `00_inputs/README.md` §4
- [x] ManyChat: 4 endpoints ya probados (getFlows/getTags/getInfo/getWidgets) + 1 nuevo a verificar (getCustomFields)
- [x] Workflow JSON nuevo: `VTR Data Export Runner v1` — Clientify + ManyChat + Supabase combinados en un solo flujo (modelado en el patrón Kommo de HPF + reusa endpoints ManyChat ya probados de `manychat-venttur-export-snapshot-v1.json`) — `00_inputs/wf-vtr-data-export-runner.json` (también en `../03_workflows/`)
- [x] Supabase: schema confirmado + 6 queries de export listos + bug MX `session_id` documentado — `00_inputs/supabase-queries-venttur.md`
- [x] Workflow JSON: `Estado interrumpida (barrido)` — `00_inputs/wf-estado-interrumpida.json` (también `../03_workflows/wf-estado-interrumpida-venttur-v2.json` — supera al v1 que era un blueprint de diseño, esto es el export real con IDs de n8n genuinos)
- [x] Workflow JSON: `Estado lead (Contestó)` — `00_inputs/wf-estado-lead.json` (también `../03_workflows/wf-estado-lead-venttur-v2.json`, mismo caso que el anterior)
- [x] Workflow JSON: `Rescate Post-Link` — `00_inputs/wf-rescate-post-link.json` (también `../03_workflows/wf-rescate-post-link-v3.json` — supera al v2: credencial ManyChat ahora referenciada por nombre en vez de token hardcodeado)
- [x] Workflow JSON: `Outreach Form Meta` — `00_inputs/wf-outreach-form-meta.json` (también `../03_workflows/outreach-form-meta-venttur-v5.json` — supera al v4: fix `session_id` MX 52→521 + nodo de backfill SQL, ver hallazgo abajo)
- [x] ManyChat: contenido interno de 12/14 flows + 3 flows nuevos descubiertos (Outreach Touch 1/2/3) — `00_inputs/manychat-flows-content-2026-07-20.md`. Confirma que la lista de 14 flows de mayo está desactualizada.
- [x] **🎯 EXPORT DE DATOS CORRIDO Y GUARDADO (2026-07-24)** — `00_inputs/vtr-data-snapshot-2026-07-24.json` (13,7 MB). Corrida real del `VTR Data Export Runner v1`. Contenido: Clientify **6.968 contactos + 2.338 deals + 266 companies + 22 custom fields** · ManyChat **16 flows + 4 folders + 5 tags + 13 custom fields + page_info** · **10 muestras de conversación** de Supabase (anonimizadas). ⚠️ Nota de lectura: `manychat.flows` es un array de 1 wrapper `{flows:[16], folders:[4]}` — los 16 flows están adentro, no en el top level. `_metadata.confirmed_endpoints` tiene texto "VERIFICAR" hardcodeado que quedó obsoleto: los conteos reales prueban que deals/companies/custom-fields SÍ existen.
- [x] **Clientify — endpoints resueltos:** `/deals/` (2.338), `/companies/` (266), `/custom-fields/` (22) CONFIRMADOS con datos reales. Ya no son "VERIFICAR".
- [x] **ManyChat — lista de flows actualizada:** 16 flows reales (vs 14 de mayo). El snapshot de mayo queda superado por este export.

### Faltantes (no bloqueantes — NINGUNO bloquea Etapa 1)

- [x] ~~**Keyword triggers CTWA** (ManyChat)~~ — ✅ **CERRADO 2026-08-18 por obsolescencia de diseño, no porque los hayamos conseguido.** El cliente separó atribución (automática, desde el referral de Meta) de conversación (el agente pregunta siempre el programa) → el mapeo keyword→programa deja de hacer falta. Contexto original: la API pública no los expone. Es el mapeo keyword→programa para leads de click-to-WhatsApp. Parcialmente deducible de: custom field `programa_wpp`, rama CTWA del workflow Meta CAPI, y la tabla `Mensajes anuncios`. Confirmar strings exactos con el cliente si Etapa 1 lo requiere.
- [x] **Config canal WA** — ✅ **RESUELTO en lo que decide el diseño (2026-08-18).** Un solo número compartido entre asesores (`+52 1 33 1944 2476` vigente). 🚨 **Dato nuevo: hoy hay DOS números a nivel sistema** — ManyChat (agente) y **Clientify (recordatorios de cita)**. Estado destino: uno solo. Business Account ID / proveedor API se resuelven dentro de la **revisión de portabilidad**, que el cliente pidió como prioridad #1.
- [x] ~~Revisar con Max/Mauricio: flow "Elevar" con "Notify Assignees: 0 people"~~ — ✅ **RESUELTO 2026-08-18.** El aviso de elevación debe llegarle a **dos personas: Mauricio y Max**, por email + notificación de app + inbox de GHL. Confirma que el "0 people" era un bug real de config.
- [x] ~~Landings~~ — ✅ **CERRADO 2026-08-18.** Inventario completo: el **formulario nativo de Meta SUSTITUYÓ** a la landing (no corren en paralelo). `go.venttur.com/bs` sigue viva al 100% para orgánicos y **hay que repuntarla a GHL**. Los otros 7 programas no tienen landing ni formulario. Campos de cada ruta documentados en A6 del máster.

### ✅ Supabase — CERRADO (2026-07-20)

3 tablas confirmadas: `n8n_chat_histories` (34.725 filas — única relevante para migrar), `documents` (0 filas, vector store LangChain sin usar, vestigio), `n8n_chat_histories_plus_backup` (2 filas, irrelevante). `workflow_errors` NO existe en esta base — el sub-workflow `webapp_errors` escribe a un Supabase compartido de la agencia, fuera de alcance. Detalle: `supabase-queries-venttur.md`.

**No bloqueantes por decisión del usuario (2026-05-13):** Meta (pixels/campaigns — la solución post-migración tiene partes en Meta y n8n, se resuelve más adelante) y GHL (sub-account/API key/plan — se resuelve al iniciar Etapa 3).

---

## Reconciliación workflows n8n — ✅ CERRADA (14/14)

La hipótesis de los 4 workflows faltantes (basada en CLAUDE.md) se confirmó al 100%: Rescate Post-Link, Outreach Form Meta, Estado lead (Contestó) y Estado interrumpida (barrido) son exactamente los 4 que faltaban.

**Lista completa de los 14:** `[Venttur]` (main) · Meta CAPI · CAPI Registro Folio · Formulario Clientify · Actualizar Link enviado · Confirmación de agenda · Crear contacto Clientify y Airtable · Resumen/etiquetas/seguimientos · Seguimiento agenda · Correo Semanal · Rescate Post-Link · Outreach Form Meta · Estado lead (Contestó) · Estado interrumpida (barrido).

**Hallazgo importante al comparar contra lo que ya había en el repo (`03_workflows/`):** los 4 workflows recién recibidos son exports genuinos y más recientes que lo que había guardado:
- **Estado interrumpida / Estado lead:** las versiones `v1` existentes en el repo eran blueprints de diseño (IDs de nodo sintéticos tipo `b2c3d4e5-1111-...`, no aleatorios) documentados como "pendiente aplicar en n8n" — los nuevos `v2` son el export real de n8n (IDs aleatorios genuinos), confirmando que el diseño **sí se deployó** desde la última vez que se documentó.
- **Rescate Post-Link v3:** vs. el v2 del repo, ahora la llamada a ManyChat usa la credencial `Venttur Header Auth account` por nombre en vez del Bearer token hardcodeado en texto plano — mejora de higiene de credenciales aplicada en producción.
- **Outreach Form Meta v5:** vs. el v4 del repo, agrega un fix real de `session_id` para números mexicanos (ver sección siguiente) + un nodo `Execute a SQL query` con el backfill ya corrido.

## 🐛 Hallazgo: bug de `session_id` en números MX (52 vs 521)

Los celulares mexicanos llegan de WhatsApp como `52XXXXXXXXXX` (12 dígitos) pero el resto del sistema (main, ManyChat) espera `521XXXXXXXXXX` (13 dígitos, con el `1` de celular). Algunos nodos de memoria sintética de Outreach no normalizaban este caso → generaban `session_id` con formato incorrecto que nunca hacía match cuando el lead respondía. **Ya resuelto en producción** (fix en el código + backfill SQL ya corrido sobre filas históricas). Detalle completo + query de verificación: `supabase-queries-venttur.md` sección "Quirk confirmado".

---

## Outputs de Etapa 1 en `01_logica_actual/` — ✅ REESCRITOS (2026-07-24)

Los 6 docs se regeneraron desde cero con los inputs completos de Etapa 0 (analizando los 14 workflows nodo-por-nodo + el system prompt del agente + el snapshot de datos + los 6 CSVs). Crecieron ~4-8× respecto de la versión de mayo. Cada doc lleva encabezado con fecha, bloque "Correcciones vs. versión mayo 2026", y sección final "Marcadores de incertidumbre".

- [x] `01_mapa_funcional.md` (~54 KB) — Arquitectura end-to-end COMPLETA: agente conversacional "Mauricio" como componente central + inventario de los 14 workflows + 16 flows ManyChat + **modelo de datos cruzado Airtable↔Clientify↔ManyChat↔Supabase** (FK ID Clientify / ID Manychat / id=teléfono=session_id / Folio).
- [x] `02_triggers_y_eventos.md` (~74 KB) — Taxonomía completa reorganizada en 7 categorías (Atribución / Conversacional / CRM / Outreach / Rescate / Nurturing / Estado / Reporting), incluyendo todos los subsistemas que en mayo estaban "no activados".
- [x] `03_ciclo_de_vida_lead.md` (~41 KB) — Doble capa de estado (conversacional del agente + operativa por campos Airtable reales), enum `Estado conversación` confirmado, cruce con pipeline Clientify.
- [x] `04_catalogo_mensajes.md` (~47 KB) — Inventario verbatim: rescate 15 + outreach 3 + nurturing 24 (4-toques × 6 programas) + agenda (nº Rodrigo) + memoria sintética + guías del agente.
- [x] `05_reglas_negocio.md` (~59 KB) — Reglas CAPI + del agente Mauricio (EMA/Voss/Hormozi/7 pasos) + outreach tri-toque + rescate + estado + nurturing + normalización + data/CRM + reporting.
- [x] `06_redundancias_y_ambiguedades.md` (~48 KB) — Issues actualizados (muchos "pendientes" de mayo resueltos) + decisiones KEEP/REMOVE/MODIFY/CONFIRM/DECIDE + preguntas para Etapa 2.

**Método:** orquestación multi-agente (14 analizadores de workflow en paralelo → 6 redactores con la verdad de base compartida → revisión de consistencia). Los redactores priorizaron los JSON reales por sobre las asunciones del brief y **auto-corrigieron varias asunciones históricas** (ver hallazgos). Pasada final de corrección con datos reales de `leads.csv` (Tipo lead hot/**warm**/cold; grafía legada `Boarding School`; Origen solo `Form Meta` en datos).

---

## Hallazgos de Etapa 1 (confirmados desde los JSON — insumo para Etapa 2/3)

Lo que la lectura nodo-por-nodo confirmó y que **no** se sabía en mayo. Varios contradicen supuestos previos (incluidos algunos de `CLAUDE.md`):

1. **Sí hay agente conversacional IA "Mauricio"** (gpt-4o, temp 0, system prompt inline ~39K chars en el nodo `Agente IA WPP` del main). Era el error más grave de mayo ("sistema puramente reactivo").
2. **Rescate Post-Link y Outreach Form Meta están LIVE** como workflows n8n (no "diseñados/no implementados"). + memoria sintética en Postgres.
3. **Tool `contestan_2do`: fantasma.** El system prompt instruye invocarla, pero **no existe ningún nodo/tool cableado con ese nombre** en el main. Métrica "contestan 2do mensaje" no se captura.
4. **Rama CTWA del Meta CAPI hardcodea `{Programa}='BS'`** — `programa_wpp` NO aparece en el workflow CAPI (contradice el supuesto de mayo/CLAUDE.md de que CTWA rutea por `programa_wpp`). ⚠️ intencional vs. bug a confirmar.
5. ~~**`wf-estado-lead` (Contestó) figura `active:false` / no invocado desde el main**~~ → ❌ **CORREGIDO (2026-08-17, verificado en el n8n vivo).** El main **sí** tiene el nodo
   `Estampar estado (Contestó)`, habilitado, como 3ª rama de `Responder rápido ManyChat`, y el
   sub-workflow `b52CUYEkI2Ah3Xj6` registró **18 ejecuciones, todas exitosas**. El `active:false` es
   normal en un sub-workflow invocado por Execute Workflow. Los 10 leads con `Estado=Contestó` del
   CSV se explican porque ese export es del **2026-07-24**, anterior al cableado.
   **`CLAUDE.md` y `CLIENT_INFO.md` afirman que estos EDITs se descartaron el 2026-08-04: es falso.**
6. **El sessionKey del main NO normaliza el quirk MX 52→521** — el fix + backfill se aplicaron solo a los nodos de memoria sintética de outreach y a filas históricas, no al armado de sesión en vivo → riesgo de doble identidad de sesión.
7. **"Estudio y Trabajo" es código muerto en el Rescate** (5 ramas en el envío vs 6 en la memoria); coincide con que ese valor no aparece en ningún lead real.
8. **`wf-confirmacion-agenda`: los paths de Diego y Andrés referencian nodos inexistentes** — solo el
   path de Rodrigo está consistente. ✅ **CONFIRMADO Y AGRAVADO (2026-08-17).** Ejecución `1362988`:
   la cadena llega a `Settear variables` y muere con `Referenced node doesn't exist`. El reporte lo
   mide del lado del cliente: **0 confirmaciones sobre 11 leads que agendaron**. Y `Agendan cita =
   true` se escribe **antes** del envío → el lead queda marcado como agendado, sin confirmación y
   excluido de todo seguimiento.
9. **Cron del Outreach sin `minutesInterval`** → probablemente corre cada 1 min (no cada 5).
10. **Meta CAPI y Correo Semanal figuran `active:false`** en los exports (Correo en modo testing con destino de prueba) — verificar estado real en la instancia viva.
11. **Secretos hardcodeados** (tokens de Meta pixel, Bearer ManyChat, tokens Clientify) en varios JSON → rotar antes/durante la migración.
12. **Flow "Elevar" con "Notify Assignees: 0 people"** → posible escalamiento silencioso (el equipo humano podría no enterarse de las elevaciones).
13. **Programas sin pixel CAPI:** solo Boarding (BS/BSG/BSC, pixel 228398216567258) y AA Familiar (HF, 24520910174237152) tienen configuración; Summer/Pathway/Gap Year no → su tracking CAPI es incierto.
14. **Grafía legada `Boarding School`** (482 leads) fuera del enum definido `Boarding IA` → normalizar al migrar a GHL single-select.

> Todos con detalle, ubicación e impacto en los 6 docs (marcados `⚠️ INCIERTO` cuando el JSON no permite confirmar). El doc 06 los consolida como decisiones para el cliente.

---

## Reporte la agencia 1 (agosto 2026) — hallazgos nuevos y correcciones al estado pre-migración

Max entregó una auditoría sobre **245 conversaciones / 1.320 mensajes** de julio-agosto. Es la fuente
de verdad del comportamiento real. Resolvió varios `⚠️ INCIERTO` de la Etapa 1 y destapó tres cosas
que **ningún análisis previo había visto**:

15. **La whitelist de links del dispatcher no incluye `promo.venttur.com/agendar-ema`.** El prompt de
    la Tarea 4 del nodo `OpenAI` de `DyrDumQgb6S4zHsS` enumera "los únicos links para agendar" y omite
    justamente el de Internados/Boarding (y el fallback ante duda), mientras repite dos entradas y
    lista un `SPEagendar` que no existe. Como la instrucción fuerza `'cero'` para cualquier otro link,
    **todo lead que recibió `agendar-ema` entra al drip genérico por construcción**. Es el 64% del
    Hallazgo 2 del reporte, y explica por qué las plantillas que fallan son las `_bs`.
16. **`Hay audios?` del main es una condición imposible.** Combinador `and` + `audio[0] equals "webp"`
    sobre una URL completa de S3 → **la rama de transcripción nunca se ejecutó**. Una nota de voz pura
    llega al agente como **string vacío**.
17. **`Repetido?` descarta mensajes en silencio con un comparador desalineado.** Escribe
    `headers.mensaje` (latin1 mojibake) y compara contra `respuesta_definitiva` (UTF-8) → solo dispara
    con texto ASCII puro, y su salida TRUE es una **rama muerta**. Es el mecanismo del Hallazgo 4
    (Omar Montes: *"Muchas gracias"* → *"Si podemos tener una llamada la próxima semana"*, sin respuesta).
18. **El agente no recibe NINGÚN estado del lead.** El User Message del nodo `Agente IA WPP` es sólo
    `Mensaje del usuario: {...}` + la fecha. No sabe si mandó el link, si el lead agendó, su programa,
    su origen ni sus datos del formulario. Es la causa raíz que el propio reporte nombra al cerrar.

### Decisiones tomadas (2026-08-17) que cambian el estado pre-migración

| Tema | Decisión |
|---|---|
| **Precios** | El agente **da el rango** (antes el prompt lo prohibía en 5 lugares). Rango **por programa**, con cierre obligatorio proponiendo día concreto. |
| **Tope de toques** | **Global de 2** por contacto, contando **todas** las secuencias (antes el techo real era ~9). |
| **Cadencia de nurturing** | **Se muda de ManyChat a n8n** (`vtr-despachador-proactivo-v1.json`). ManyChat queda como capa de envío. |

**Entregables:** `06_docs/guia-correcciones-reporte-agosto-2026.md` (EDITs por nodo) ·
`03_workflows/vtr-despachador-proactivo-v1.json` · `04_agents/agente-venttur-system-prompt-v2.0.md` ·
`07_testing/testing-guide-v1.md` · `03_workflows/vivo-2026-08-17/` (export de rollback con sha256).

---

## Validación con el cliente — respuestas del 2026-08-17 (Etapa 2)

Mauricio García revisó y confirmó el cuestionario que había redactado Max. El archivo
`02_validacion_cliente/cuestionario-venttur-2026-07-24.md` **ya no es un cuestionario en blanco: es
el registro firmado**. El mapeo pregunta-por-pregunta a las internas está en
`preguntas-cierre-2026-07-24.md` (A1..A11), y cada uno de los 6 docs de `01_logica_actual/` lleva un
bloque "🆕 Validación con el cliente" con lo que le cambia.

### ⚠️ Advertencia de versiones — leer antes de usar las respuestas

El cliente respondió la **versión de 12 preguntas enviada el 2026-08-07**. El archivo del repo se
amplió a **14 preguntas el 2026-08-17** (commit `d7ac607c`, tras el Reporte la agencia 1) agregando
*rangos de precio* y *qué significa "Cerrada"*, y reescribiendo las de seguimiento y confirmación de
cita. **Esas cuatro modificaciones nunca salieron hacia el cliente.** Consecuencias:

- Hay respuestas que contestan la redacción vieja (P7 seguimientos, P9 confirmación).
- **Dos temas quedaron sin preguntar**, y uno de ellos (precios) ya tiene código preparado.
- Los docs que decían "12 preguntas" estaban bien; el archivo era el que se había adelantado.

### Decisiones del cliente que cambian el diseño

| # | Decisión | Impacto |
|---|---|---|
| 1 | **8 programas canónicos.** Pathway es solo Alemania · Gap Year = Estudia y Trabaja (mismo producto, cursos VET) · Francia es **destino, no programa** · los destinos van como nota, nunca como campo estructurado | Reescribe la taxonomía en los 6 docs |
| 2 | **Diego sale del ruteo automático.** Rodrigo 3 programas, Andrés 5 | El path roto de Diego en `wf-confirmacion-agenda` se **borra**, no se repara |
| 3 | **8 calendarios GHL, uno por programa**, con disponibilidad compartida por asesor | Resuelve C-20. Requisito duro: nada de dobles reservas |
| 4 | **El agente NUNCA asume el programa**, ni con origen evidente. Atribución (automática, desde Meta) y conversación (siempre pregunta) se separan | Regla nueva del prompt. Vuelve innecesarios los keyword triggers CTWA |
| 5 | **Clientify se apaga y migra completo**: 6.968 contactos + 2.338 deals (abiertos, ganados y perdidos) + 266 companies, 1:1, sin rediseño, etapas manuales | Scope grande de Etapa 3 |
| 6 | **Un solo número** para conversación, confirmación y recordatorios | Hoy son dos (ver hallazgo 19) |
| 7 | **Reporte semanal se mantiene**, pero solo **citas agendadas** (la asistencia la mide Max aparte) | Simplifica el cálculo |
| 8 | **Cutover: 15 de septiembre de 2026** | T-28 días al 2026-08-18 |

### Hallazgos nuevos que las respuestas destapan

19. **🚨 Hay DOS números de WhatsApp en operación, y ningún doc lo registraba.** Uno en ManyChat (el
    agente que conversa y agenda) y **otro en Clientify, desde donde salen los recordatorios de
    cita**. Causa: el agente nunca se pudo conectar al chat de Clientify. **Esto explica por qué los
    recordatorios "existen" para el cliente pero no aparecen en ninguno de los 14 workflows** que
    analizamos en Etapa 1: viven fuera de nuestro perímetro. El cliente va a compartir su config y
    sus textos para replicarlos en GHL.

20. **🚨 Tres de los ocho programas no existen en el sistema.** `Viajes educativos` y
    `Educación superior` tienen **0 hits** en todo el cliente (grep exhaustivo sobre workflows,
    prompt, CSVs, flows y docs); `Cursos de idiomas` solo tiene un link suelto en el prompt. No
    tienen enum, ni drip de nurturing, ni rama de rescate, ni pixel. **Impacto medible hoy en
    producción:** un lead que pregunta por Educación superior no matchea nada → cae al fallback
    `agendar-ema`, que es el link de **Internados con Rodrigo** (programa equivocado y asesor
    equivocado, porque el cliente asignó ese programa a Andrés), no recibe rescate (cae en
    `RESCATE_PROGRAMA_NO_MAPEADO`) y no tiene drip propio. Es **scope nuevo**, no una corrección.

21. **La grafía canónica no se cerró, y el problema creció.** La pregunta era "¿`Boarding School` o
    `Boarding IA`?". El cliente no eligió: nombró los 8 programas **en español y con otros nombres**
    ("Internados", "Intercambio académico con familias", "Campamentos de verano"). La normalización
    pasa de elegir entre dos grafías a **renombrar el enum entero** y remapear todas las cohortes.

22. **`Conversación interrumpida` tiene dos definiciones en conflicto.** El barrido vivo
    (`H6qYB3Oj97bxaTCX`) la estampa a las **>24 h**; la definición oficial del cliente para el
    reporte es **~5 días** ("al agotarse la secuencia completa"). La que corre en producción es la de
    24 h. Además, si la secuencia se recorta al tope de 2 toques, el "~5 días" deja de valer y hay
    que re-anclar la definición.

23. **El hardcode `{Programa}='BS'` de la rama CTWA (Hallazgo 4) es correcto hoy.** Internados es la
    única campaña activa. Baja de "¿bug o intencional?" a **"correcto hoy, insostenible mañana"**:
    rompe con la segunda campaña. El cliente pide explícitamente que la atribución sea data-driven
    desde el inicio.

24. **El "Notify Assignees: 0 people" del flow Elevar (Hallazgo 12) era un bug real.** El aviso debe
    llegarle a **Mauricio y a Max**, por email + notificación de app + inbox de GHL.

### Gates y prioridades que el cliente impone

- **🔴 Prioridad #1 — revisión de portabilidad del número.** Pedido expreso: *"que sea LO PRIMERO que
  se atienda. Es el único punto que depende de un tercero (ManyChat) y puede convertirse en el cuello
  de botella de toda la migración."* Hay que devolver tres cosas: si es viable, qué requiere de ellos
  y en cuánto tiempo, y qué se pierde con número nuevo. **Decisión ya tomada por adelantado:** si hay
  riesgo de downtime, va número nuevo. No hace falta volver a consultarlo.
- **🔴 Gate de cutover — auditoría de migrabilidad de Clientify.** El cliente exige saber **antes de
  apagar Clientify** qué no se puede pasar (historial de conversaciones, adjuntos, automatizaciones)
  para respaldarlo por su cuenta. Es entregable de la agencia, no opcional.
- **🟡 Repuntar `go.venttur.com/bs` a GHL.** *"No debe quedar como puerta muerta."* Las dos rutas de
  entrada (form Meta y landing) tienen que quedar funcionando e intercambiables.

### Lo que quedó abierto → `puntos-abiertos-ronda-2-2026-08-18.md`

| Prioridad | Punto | Por qué importa |
|---|---|---|
| ✅ | ~~**Rangos de precio por programa**~~ | **CONFIRMADO por la agencia el 2026-08-18:** valen los 5 rangos que ya teníamos. El conflicto de Internados se resuelve a favor de **USD 50.000–130.000** (el prompt vivo gana sobre los 100.000 del reporte). **El guion nuevo de precio queda desbloqueado.** ⚠️ Sigue faltando el rango de los 3 programas sin infraestructura (Viajes educativos, Educación superior, Cursos de idiomas) |
| 🔴 | **Qué es "Cerrada" y qué pasa en la reapertura** | Nunca se preguntó. Sin política, se repite el caso de agosto (mensaje off-topic reabrió la conversación, cambió el programa y disparó 5 días de automatización) |
| 🟡 | Textos de confirmación y recordatorio + horas de anticipación | El cliente se comprometió a mandarlos desde Clientify. Pendiente de entrega, no de decisión |
| 🟡 | OK explícito al tope de 2 toques + prioridad entre programas | La respuesta delegó en el Reporte la agencia, no aprobó el cambio de política |
| 🟡 | Nombres definitivos del enum (ver hallazgo 21) | Bloquea la normalización de datos previa a la migración |
| 🟡 | Alcance de los 3 programas sin material (ver hallazgo 20) | Define si entran completos al 15/9 o solo con calendario y asesor |
| 🟢 | `utm_*` como campos del contacto · dar de baja "contestan 2do mensaje" | Confirmaciones de bajo costo |

### ⚠️ Lectura de riesgo sobre la fecha (evaluación la agencia)

El 15 de septiembre es **T-28 días** y el alcance **creció** con estas respuestas. En el camino
crítico hay tres dependencias que no controlamos: la portabilidad del número (ManyChat + Meta), la
migración de Clientify (sin herramienta automática; el propio cliente asume que *"buena parte del
trabajo será reconstrucción manual"*) y los 3 programas sin infraestructura. Etapas 3, 4 y 5 están
todas por delante.

**Recomendación:** poner sobre la mesa las dos opciones y que el cliente elija (punto B3 de la ronda
2): cutover completo el 15/9, o el 15/9 sale canal + agente + calendarios (lo que atiende leads) y la
migración del pipeline comercial va en una segunda ola. Está planteado en el doc del cliente sin
recomendar una por defecto, porque depende de cuánto les pesa tener Clientify prendido unas semanas
más.

---

## Incidente Nahe (15-16/9/2026) — contrato de diseño heredado

El 15/9 Max reportó un caso público: la lead **Nahe** (`id_2 5214731005555`, programa `AA Familiar IA`) pidió agendar por chat, el bot le prometió coordinar una cita que nunca existió, ella se preparó dos veces sin que nadie la llamara, y cerró con *"me parece falta de seriedad… mejor no gracias"*.

**Causa raíz** (verificada con Postgres + n8n executions): **el prompt v2.0 vivo le enseñaba al agente a coordinar el horario a mano** cuando ya había mandado el link, aunque el agente no tiene tool de calendar. No era fire-and-forget del canal (los mensajes salían OK): era prompt engineering. Reconstrucción completa: `06_docs/incidente-nahe-2026-09-15.md`.

**Alcance real del bug** — barrido de la cohorte (`06_docs/barrido-leads-promesa-fantasma-2026-09-16.md`):
- **34 leads** afectados en los ~30 días previos.
- **60 turnos AI** con promesa fantasma confirmada (detector determinístico, 12/12 tests golden).
- **11 leads con 2+ promesas** en el período; **7 leads con el patrón exacto de Nahe** (link enviado antes + volvieron pidiendo agendar + bot aceptó coordinar en vez de re-enviar link).
- Distribución por programa: 22 "No definido", 8 AA Familiar IA, 2 Boarding IA, 1 Pathway IA, 1 Gap Year IA.

**Fix aplicado al vivo** (16/9 14:49-16:00 UTC):
- **Capa prompt** — v2.0 → v2.1 con Regla ABSOLUTA #8 "No agendo yo" (lista de frases prohibidas + explicación del motivo + regla de re-envío del link cuando el lead vuelve pidiendo agendar).
- **Capa estructural** — Code node `Detectar promesa fantasma` entre `Formatear mensaje WPP` y `Normalizar burbujas` (regex determinística, no LLM; intercepta y reemplaza por link canónico + framing de disculpa).
- **Instrumentación** — INSERT en tabla nueva `vtr_phantom_interceptions` + alerta P1 Telegram inmediata + digest diario 08:00 CDMX (`BzBCMGxEdJy6zmA9`, cero envío si N=0).

**Traspaso a los docs de la migración GHL** (heredar tal cual — este bug no es de topología ManyChat vs GHL, es del agente que ambos comparten):
- `03_arquitectura_ghl/06_canal_whatsapp_y_agente.md §9` — contrato de diseño nuevo con las 4 sub-secciones (capa prompt, capa estructural, tabla destino, anti-patrón generalizable para otros clientes).
- `03_arquitectura_ghl/07_agendamiento_calendarios.md §6` — regla dura "el agente NO agenda por chat" + relación con el reorden del write ya documentado en §3 (los dos fixes son necesarios, uno no reemplaza al otro).
- `04_guia_migracion/07_n8n_agente_canal.md §7.7` — banderas y checkpoints actualizados: prompt del cutover **obligatoriamente** incluye Regla #8, guardrail se hereda entre Formatear→Normalizar, workflow del digest se importa.
- `04_guia_migracion/11_testing_precutover.md §11.3.bis` — nuevo bloque de regresión N1-N7 con mensajes verbatim de Nahe + falla dura de aprobación si el prompt del cutover no tiene la Regla #8.

**Snapshots** en `03_workflows/`:
- `vivo-2026-09-15-pre-fix-nahe/` — estado pre-fix con el bug reproducible.
- `vivo-2026-09-16-post-fix-prompt-guardrail/` — post Fase 3 (prompt v2.1 + guardrail).
- `vivo-2026-09-16-post-fix-fase6-alertas/` — post Fase 6 (alertas P1/P2 + persistencia).

**Recuperación individual de Nahe:** queda en manos de Venttur (fuera de scope la agencia).

---

## Próximos pasos

> **Al 2026-08-18 quedan 28 días para el cutover del 15/9.** Los ítems 3 y 4 dependen de terceros o
> del cliente: arrancarlos hoy, no cuando Etapa 3 esté lista.

**Hecho**

1. ~~Reescribir Etapa 1~~ ✅ (2026-07-24). Los 6 docs de `01_logica_actual/` reescritos con los inputs completos.
2. ~~Integrar las respuestas del cliente~~ ✅ (2026-08-18). Registro firmado + A1..A11 del máster + bloque de validación en los 6 docs. Etapa 0 cerrada, Etapa 3 desbloqueada.

**Camino crítico — arrancar ya (dependen de terceros)**

3. **🟡 Portabilidad del número — 3/4 datos recibidos, falta desambiguar el WABA.** Doc: `06_docs/portabilidad-numero-whatsapp-2026-08-18.md`. **Datos recibidos 18/8 PM:** número `+52 1 33 2627 4502` (Guadalajara, chip de Venttur), WABA ID `1931874540684022`. **Único paso restante:** verificar en `business.facebook.com` de Venttur → Configuración → Cuentas → Cuentas de WhatsApp si el WABA `1931874540684022` aparece bajo el Business Manager de Venttur (portable → escenario A) o no (WABA bajo BM de ManyChat → escenario Collazo → no portable, número nuevo). **Tarda 2 minutos.** Sin esto no se puede iniciar la migración BSP a GHL ni dimensionar el downtime real.
4. ✅ ~~Ronda 2 al cliente~~ CERRADA (2026-08-18 PM). Sección A + Sección B respondidas. Único punto sin definir: rangos de precio de los 3 programas huérfanos (respuesta "-" → el bot no cotiza en esos 3, pasa directo a asesoría).
5. **⚪ Cuenta GHL — diferida a propósito (decisión de la agencia, 2026-08-18).** No es bloqueante de Etapa 3: la sub-account se crea **cuando el mapa esté definido y haya algo concreto que construir ahí**. Etapa 3 se diseña en papel primero. Pasa a ser prerequisito de **Etapa 4/5 (ejecución)**, no del diseño.

**Antes de diseñar la arquitectura**

6. **🔴 Aplicar las correcciones del Reporte la agencia 1 sobre el sistema pre-migración.** La Etapa 3 tiene que partir del estado corregido, no del de julio. Guía: `06_docs/guia-correcciones-reporte-agosto-2026.md`.
7. **🟡 Dos verificaciones que necesitan acceso manual** (la API no alcanza): (a) abrir en ManyChat los flows `content20250721163426_851504` y `content20250718124614_140983` para resolver si los nombres están cruzados — **sin esto no se toca ningún `flow_ns`**; (b) averiguar por qué el Rescate Post-Link tiene **0 ejecuciones** pese a estar cableado y habilitado.

**En paralelo**

8. **🟢 Etapa 3 — diseño de arquitectura GHL.** Ya puede arrancar: lo que quedó abierto en Etapa 2 afecta el prompt del agente, no la topología. Scope confirmado a diseñar: 8 calendarios con disponibilidad compartida por asesor · consolidación a un solo número · pipeline de Clientify completo (6.968 contactos + 2.338 deals) · atribución CAPI data-driven · **los 3 programas que hoy no existen en el sistema** · normalización del enum de programas.
9. **🔴 Auditoría de migrabilidad de Clientify.** Gate duro que el cliente pidió: saber **antes de apagar Clientify** qué no se puede pasar (historial de conversaciones, adjuntos, automatizaciones) para que ellos lo respalden. Además dimensiona cuánto trabajo real es la migración de datos.
10. **🟡 Higiene:** rotar los secretos hardcodeados detectados en los JSON. El estado `active` real ya se verificó (2026-08-17): ver `03_workflows/vivo-2026-08-17/README.md`.

**⚠️ Decisión de alcance pendiente (punto B3 de la ronda 2):** el 15/9 creció de alcance con las
respuestas del cliente. Hay que elegir entre cutover completo, o cutover del canal + agente +
calendarios el 15/9 con la migración del pipeline comercial en una segunda ola. Está planteado al
cliente sin recomendación por defecto: depende de cuánto les pesa tener Clientify prendido unas
semanas más.

**Para retomar:** decile a Claude *"continuamos migración VTR, Etapa 3"* y apuntá a este archivo.
