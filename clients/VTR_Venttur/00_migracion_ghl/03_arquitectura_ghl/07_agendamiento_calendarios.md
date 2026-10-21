# 07 · Agendamiento — 8 calendarios GHL + confirmación + recordatorios

> **🟡 Riesgo medio.** Reemplaza los 3 Google Calendar Triggers + la matriz de links de Clientify por **8 calendarios nativos de GHL (uno por programa)**, reconstruye la confirmación (hoy rota: 0/11 enviadas) y **construye desde cero los recordatorios pre-cita** que hoy salen de un segundo número en Clientify.
>
> Corroborado contra `wf-confirmacion-agenda.json`, `cuestionario` P2/P9, `ronda-2` §3/§4 y el anexo de reparto de asesores.

---

## 1. Los 8 calendarios (uno por programa)

**Decisión cliente (`cuestionario` P2, anexo):** *"UN CALENDARIO POR PROGRAMA (8 en total)… así el sistema sabe desde el momento del agendamiento a qué programa pertenece cada cita, sin depender de etiquetado manual posterior."*

| # | Programa (`01`) | Calendario GHL | Asesor | Link viejo (Clientify, muere) |
|---|---|---|---|---|
| 1 | Internados | `cal-internados` | **Rodrigo** | `agendar-ema` |
| 2 | Intercambio académico con familias | `cal-intercambio` | **Rodrigo** | `AAFamilia-Agendar` |
| 3 | Campamentos de verano | `cal-campamentos` | **Rodrigo** | `SummerCamp-Agendar` |
| 4 | Viajes educativos | `cal-viajes-educativos` | **Andrés** | *no existía* (`10`) |
| 5 | Educación superior | `cal-educacion-superior` | **Andrés** | *no existía* (`10`) |
| 6 | Cursos de idiomas en el extranjero | `cal-cursos-idiomas` | **Andrés** | *(dudoso — `01` bandera 1: `EstudiaryTrabajar_Agendar` probablemente mapea a Gap Year; Idiomas es huérfano sin link previo, `10`)* |
| 7 | Pathway Alemania | `cal-pathway-alemania` | **Andrés** | `PW_Alemania_Agendar` |
| 8 | Gap Year / Estudia y Trabaja | `cal-gap-year` | **Andrés** | `Estudiar-y-Trabajar-en-Australia` |

**Reparto:** Rodrigo 3 · Andrés 5 · **Diego fuera del ruteo automático** (`cuestionario` P2: trabaja leads orgánicos que él genera, fuera del flujo del agente).

> **⚠️ Corrige un malentendido:** no hay un asesor "Ema". `agendar-ema` es el **slug del calendario de Internados (Rodrigo)** y el fallback genérico; "EMA" por separado es la metodología del agente. El fallback a `agendar-ema` es hoy un **bug de negocio** (un lead de Educación superior cae al calendario de Internados/Rodrigo = programa y asesor equivocados) — se elimina con los 8 calendarios reales (`10`).

---

## 2. Disponibilidad compartida por asesor (el requisito duro)

**Decisión cliente (`cuestionario` P2):** *"todos los calendarios de un mismo asesor deben compartir su disponibilidad real. Si alguien agenda 'Internados' el martes a las 4pm, ese bloque debe desaparecer también de 'Intercambio académico' y 'Campamentos'. No queremos dobles reservas."*

- **Rodrigo:** cal 1+2+3 comparten un solo pool de disponibilidad.
- **Andrés:** cal 4+5+6+7+8 comparten un solo pool (5 calendarios).

⚠️ **GHL no comparte disponibilidad entre calendarios independientes out-of-the-box** (`00` §7.10c). Mecanismos posibles a validar en sandbox:
- **(a)** cada asesor conecta su calendario personal (Google/Outlook) a GHL y cada uno de sus calendarios GHL tiene **"check for conflicts"** contra ese calendario personal → un booking en uno bloquea los otros vía el calendario personal común.
- **(b)** GHL **Team / Service calendars** con un mismo usuario en varios event-types.
- **Fallback si ninguno alcanza:** 1 calendario por **asesor** con **event-types por programa** (la disponibilidad se comparte nativamente porque es un solo calendario; el programa lo distingue el event-type). Rompe el "1 calendario por programa" literal pero cumple el objetivo real (sin dobles reservas + programa conocido al agendar). **Se decide tras probar (a)/(b) en sandbox; y como contradice la instrucción literal de P2** (*"un calendario por programa y no uno por asesor"*), **requiere OK del cliente, no solo el resultado técnico.**

---

## 3. Confirmación de cita (hoy rota → se reconstruye)

**Hoy:** 3 Google Calendar Triggers (`eventCreated`) sobre `dgarcia@`/`agarcia@`/`rgarcia@venttur.com` → `wf-confirmacion-agenda` → cruce frágil GCal→Clientify→Airtable → `Agendan cita=true` + confirmación por ManyChat. **Está roto:** los paths de Andrés y Diego referencian nodos inexistentes → **de 11 leads que agendaron, 0 recibieron confirmación** (solo Rodrigo funcionaba); y `Agendan cita=true` se escribe **antes** del envío, dejando al lead marcado como agendado, sin confirmación **y excluido de todo seguimiento**.

**Destino:**
- El booking en un **GHL Calendar** dispara un **GHL workflow → HTTP a n8n** (o n8n lee la cita) → confirmación.
- **Contenido (decisión cliente `ronda-2` §4):** **fecha, hora, asesor y link de videollamada.** Sin campos adicionales.
- **Un solo número** (el del agente) — la confirmación sale del mismo canal, no de un segundo número.
- 🔧 **Fix del orden:** la etapa "Cita agendada"/`Agendan cita` se marca **después** (o junto con) el envío exitoso, no antes → el lead no queda marcado como agendado si la confirmación falla.
- 🔧 **El path de Diego se borra** (no se repara — Diego sale del ruteo). Solo se cablean Rodrigo y Andrés.
- **El número directo de Rodrigo `+52 1 33 1944 2476`** que hoy el flow comparte al agendar (*"Rodrigo se comunicará contigo por WhatsApp directamente desde…"*) es un **dato de negocio a preservar** (KEEP, `06` §7), no un canal a reconciliar. Se mantiene en el texto de la confirmación de Internados/Rodrigo.

---

## 4. Recordatorios pre-cita (se construyen desde cero)

**Decisión cliente (`ronda-2` §3):** **dos recordatorios — 24 horas antes y 1 hora antes.**

⚠️ **Hoy los recordatorios NO existen en los 14 workflows** — salen de **Clientify, desde un segundo número de WhatsApp** (hallazgo ronda 2). Por eso el lead agenda con un número y recibe el recordatorio desde otro distinto (confunde). En GHL:
- Los recordatorios se **reconstruyen desde cero** (no hay workflow que migrar).
- Salen del **mismo número del agente** (consolidación a un número, `06` §7).
- **24h antes + 1h antes** de la cita agendada, disparados por el GHL Calendar (o un cron n8n que lee las citas próximas).
- El **segundo número de Clientify muere y NO se avisa** (decisión explícita `portabilidad` §8).
- Como son **fuera de la ventana de 24h**, van por **Message Template** (el de 1h antes puede caer dentro de ventana si el lead interactuó — usar free-form si aplica). El cliente aporta los textos actuales de Clientify para replicarlos.

---

## 5. La matriz de links del agente → calendarios GHL

El agente "Mauricio" hoy manda `promo.venttur.com/<slug>` según el programa detectado en el descubrimiento. En destino, esos slugs → **links de booking de los 8 calendarios GHL**. El agente sigue eligiendo el link por el programa que **surge de la conversación** (no del anuncio — atribución y conversación separadas, `01`/`06`). El fallback `agendar-ema` deja de ser un parche: cada programa tiene su calendario real (incluidos los 3 nuevos, `10`).

**⚠️ Nuevo hallazgo 2026-09-15 (reunión con cliente):** además del link del agente y de la landing orgánica, existe una tercera vía paralela — **las landings de aventureras**. Ver §6 nuevo.

---

## 6. Landings de aventureras — atribución de referencia (🔴 pendiente rediseño)

**Hallazgo destapado en la reunión 15/9.** Venttur trabaja con ~20-25 "aventureras" (comisionistas externas que refieren leads). Cada una tiene su propia **estructura de 6 landings en Clientify** hoy: una principal + 5 landings por programa, cada una con el calendario del asesor correspondiente **embebido** (no linkeado). Total: ~20-25 × 5 = **100-125 landings**. La atribución "de quién vino el lead" se captura al momento de agendar — cada calendario embebido escribe una etiqueta con el nombre de la aventurera en el registro del lead.

**Estructura hoy en Clientify:**

```
promo.venttur.com/agendar-<AventureraX>          ← landing principal (menú de 5 programas)
    ├── Internados          → landing con calendario embebido → cal de Rodrigo + tag Aventurera X
    ├── Año con Familia     → idem
    ├── Summer Camp         → idem
    ├── Pathway             → landing con calendario embebido → cal de Andrés + tag Aventurera X
    └── Gap Year            → idem
```

**Contradicción con §1 y §5**: el diseño actual habla de **8 calendarios GHL fijos** y de una **matriz única** de links del agente. Las aventureras hoy son ortogonales a esa matriz — cada aventurera tiene sus links propios, no las 8 URLs canónicas.

**Vías posibles a resolver antes del cutover 18-19/9:**

- **Vía a · wrapper con atribución por query string.** Los 8 calendarios GHL viven una sola vez; se embeben (o se linkean) en ~100 landings-wrapper (una por combinación aventurera × programa) con `?ref=<slug_aventurera>`. GHL captura el `ref` en un custom field nuevo `atribuida_a` del contact. Menos landings a construir si se usan links directos con query string en vez de embed.
- **Vía b · GHL Snippets o URL templating.** Si GHL soporta variantes de la misma landing con hidden fields distintos (a validar en sandbox), se puede reducir el número de landings a construir.

**Sea cual sea la vía, requiere:**
- Custom field nuevo `atribuida_a` (contact-level) para el nombre de la aventurera.
- Slug canónico por aventurera (validar naming con el cliente).
- Actualizar el reporte semanal para discriminar por aventurera (hoy Clientify lo hace nativo).
- Confirmar con el cliente que las aventureras pueden pasar por reconstrucción de sus links (URLs cambian de `promo.venttur.com/*` al subdominio nuevo).

**Alternativa sin rediseño previo al cutover:** aceptar que las aventureras pierden trazabilidad transitoria post-cutover (los links viejos de Clientify mueren con Clientify), reconstruir sus landings en una fase 2. **Requiere OK del cliente**. Impacto en el negocio: aventureras dejan de generar leads atribuibles hasta que se reconstruya el sistema.

**Doc operativo con el inventario detallado:** `06_docs/aventureras-mapeo-landings-2026-09-16.md` (pendiente crear).

---

## 7. El agente NO agenda por chat (contrato heredado del incidente Nahe · 16/9/2026)

**Regla dura:** el agente Mauricio **nunca** ofrece coordinar / agendar / programar / confirmar una cita por chat. La única vía real de reserva es el link del calendario del programa (§5). Cuando el lead pide agendar directamente ("¿el lunes a las 11?", "¿podemos mañana a las 9?"), el agente **re-envía el link** — no acepta el horario.

- **Por qué está acá:** el 15/9 el prompt del agente aceptaba coordinar por chat aunque no tuviera tool de calendar. Resultado: **34 leads afectados en 30 días**, uno público (Nahe). Reconstrucción, causa raíz y fix: `06_docs/incidente-nahe-2026-09-15.md`.
- **Dónde vive el contrato:** en el system prompt (Regla ABSOLUTA "No agendo yo") + en un guardrail Code node determinístico en n8n. Ver `06 §9` para el detalle de las dos capas.
- **En la migración a GHL:** ni el prompt ni el guardrail cambian de lugar. El reply del agente es n8n-first (`06 §4a`), así que ambas capas siguen viviendo en n8n. Cero cambios estructurales por el cutover. Pero **el contrato tiene que estar en el prompt del cutover** — chequeo pre-go incluido en `11 §11.3`.

**Interacción con §3 (confirmación de cita):** son dos fixes diferentes de un mismo síntoma superficial. §3 arregla el orden de escritura (`Agendan cita=true` va **después** del envío) — es fire-and-forget del canal. Esta §6 arregla que el agente ni siquiera prometa la cita en primer lugar — es prompt engineering. **Ambos son necesarios**, uno no reemplaza al otro.

---

## 8. Banderas de este mapping

1. **Disponibilidad compartida (§2):** el mecanismo concreto (calendario personal + check-conflicts / team calendars / 1-cal-por-asesor con event-types) **se valida en sandbox antes de comprometer los 8 calendarios**. Es el punto técnico más incierto del doc. Si se cae al fallback 1-cal-por-asesor, requiere OK del cliente (contradice P2). **Árbol de decisión: §9.**
6. **Trigger de booking + query de appointments** (§3/§4): validar en sandbox que el booking de un GHL Calendar dispara un webhook/HTTP a n8n, y que se pueden leer las citas próximas por API (para confirmación y recordatorios). El cron n8n que lee citas próximas es el fallback, y también depende de esa query (`00` §7.10j).
2. **Recordatorio de 1h antes:** confirmar si cae dentro o fuera de la ventana de 24h (define template vs free-form).
3. **Reconciliación de los 2 números** (`06` §7): el del agente sobrevive, el de Clientify muere; desambiguar cuál WABA es cuál antes del cutover.
4. **Owners de calendarios → usuarios GHL:** Rodrigo y Andrés deben existir como usuarios GHL con sus calendarios personales conectados (dependencia de §2).
5. **Textos de confirmación/recordatorio:** el cliente los aporta desde Clientify; hasta entonces, placeholders.

---

## 9. Árbol de decisión — disponibilidad compartida C1 vs fallback (19/9)

**Contexto:** el requisito duro del cliente (P2 del cuestionario) es que los N calendarios de un mismo asesor compartan disponibilidad — un booking en uno bloquea los otros. GHL no lo soporta out-of-the-box para calendarios independientes. Sin resolver esto en sandbox, no se pueden crear los 8 calendarios definitivos.

**Ventana de decisión:** T-4 (22/9). Sin resolución al T-3 (23/9), se cae al fallback y se comunica al cliente.

### 9.1 · Test en sandbox (~2-4h la agencia)

**Sandbox:** sub-cuenta de test GHL (o la propia sub-cuenta VTR `7aXb4JCKsWV5nUyBXeSF` con 2 calendarios throwaway).

**Preparación (una vez):**
1. Crear en GHL: 2 calendarios de test (`cal-test-A` + `cal-test-B`).
2. Asignar el mismo usuario (ej. Rodrigo o un test user) a ambos.
3. Ese usuario conecta su calendario personal Google (OAuth) a GHL.
4. En ambos calendarios test → Settings → **"Check for conflicts with"** → marcar el calendario personal Google del usuario.

**Test C1 (Mecanismo A — check-conflicts vía calendario personal):**
1. Reservar una cita en `cal-test-A` a las 15:00.
2. Intentar reservar `cal-test-B` a las 15:00 (mismo día).
3. ¿Aparece el slot 15:00 como no disponible en `cal-test-B`?

| Resultado | Interpretación | Acción |
|---|---|---|
| ✅ SÍ (slot bloqueado) | Mecanismo A funciona. **Adelante con 8 calendarios** siguiendo §1. | Setup Rodrigo (3 cals con check-conflicts a su Google) + Andrés (5 cals con check-conflicts a su Google). |
| ❌ NO (slot disponible) | Mecanismo A falla. Probar Mecanismo B → si también falla, fallback C. | Ir a Test C2. |

**Test C2 (Mecanismo B — Team / Service calendars):**
1. Buscar en GHL: `Settings → Calendars → New → Service Calendar` o `Team Calendar` (nomenclatura varía por versión).
2. Crear 1 Service Calendar con 3 event-types (uno por programa Rodrigo).
3. Reservar Programa 1 a las 15:00.
4. ¿Aparece 15:00 bloqueado para Programa 2 y 3?

| Resultado | Interpretación | Acción |
|---|---|---|
| ✅ SÍ | Mecanismo B funciona. **Setup con 2 Service Calendars** (1 para Rodrigo con 3 event-types, 1 para Andrés con 5 event-types). Contradice literalmente P2 pero preserva el objetivo. Comunicar al cliente y pedir OK (§9.3). | Documentar como C1-alt y avanzar. |
| ❌ NO | Fallback C. | Ir a §9.2 |

### 9.2 · Fallback — 1 calendario por asesor con event-types por programa

**Setup:**
- 1 calendario "Rodrigo" con 3 event-types (Internados, Intercambio, Campamentos).
- 1 calendario "Andrés" con 5 event-types (Viajes educ., Ed. superior, Idiomas, Pathway Alemania, Gap Year).

**Ventaja:** disponibilidad compartida garantizada por diseño (es un solo calendario).
**Desventaja:** contradice literalmente el requerimiento P2 del cliente ("un calendario por programa, no uno por asesor"). Requiere OK explícito.

**Impacto downstream:**
- Los slugs de landings apuntan a event-types específicos, no a calendarios: `promo.venttur.com/agendar-rodrigo?event_type=internados` en vez de `/agendar-ema`. **Rediseño de las 6 landings priorizadas (§13.6 del landings doc).**
- Custom fields para atribución quedan igual (el event-type sabe el programa).
- El agente conversacional cambia los enlaces que sirve al lead — ajuste en el prompt (variable `LINK_AGENDAMIENTO`).

### 9.3 · Mensaje pre-hecho al cliente (si aplica fallback o C1-alt)

Si tras el test §9.1 se cae a fallback o a C1-alt (Mecanismo B), se le pide OK al cliente antes de seguir. Copiar-pegar en WhatsApp (adaptar el resultado exacto):

```
Hola Mauricio, quería contarte cómo cerró la prueba técnica de los calendarios.

El escenario ideal que pediste (1 calendario por programa con disponibilidad compartida entre los calendarios del mismo asesor) tiene una limitación técnica en GHL: [{explicar en 1 línea el mecanismo que falló}].

La alternativa que preserva el objetivo (sin dobles reservas + programa conocido al agendar) es armarlo así:
- 1 calendario por ASESOR (Rodrigo, Andrés), cada uno con event-types por programa dentro.
- Rodrigo tendría 3 event-types (Internados, Intercambio, Campamentos).
- Andrés tendría 5 event-types (Viajes educativos, Educación superior, Cursos idiomas, Pathway Alemania, Gap Year).

Consecuencia visible: el link que el lead recibe cambia de "agendar-ema" a algo como "agendar-rodrigo/internados". El agente ya lo maneja.

¿Te parece bien avanzar así? Si preferís esperar a que salga la funcionalidad completa en GHL, se puede — pero eso mueve el cutover 2-4 semanas.
```

**Regla:** sin respuesta del cliente antes del T-3 (23/9), se avanza con el fallback y se lo comunica al cierre del día. Sin margen para esperar más.

### 9.4 · Path del spec

**El spec de los 8 calendarios vive en `05_ejecucion/spec/calendarios.json`** (NO en `03_arquitectura_ghl/spec/`). Corregir el path en cualquier doc que lo mencione. El JSON tiene: nombre, slug, duración, asesor, availability window.

---

*Corroborado contra `wf-confirmacion-agenda.json`, `cuestionario` P2/P9, `ronda-2` §3/§4. 2026-08-26. Revisión 2026-09-19 (§9 nueva: árbol de decisión C1 vs fallback + mensaje pre-hecho al cliente + corrección path spec).*
