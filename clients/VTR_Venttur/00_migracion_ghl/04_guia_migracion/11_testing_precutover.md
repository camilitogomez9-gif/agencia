# 11 · Testing pre-cutover

> ### 🔄 Estado a 2026-09-07 — 🟡 PASO INMEDIATO: testear el agente por Telegram
> **Ya ejecutable ahora** (sin canal): el **agente por Telegram** en staging `3sLd7KY3o8I7NvXi` (bot `Venttur`, activo) — verifica agente Mauricio + memoria + tools (`crear_contacto`/`elevar`) + context builder `[ESTADO DEL LEAD]`. Es el testeo que se comparte con Mauricio (paso del §Calendario "mañana 8/9"). **Guía lista para Mauricio + pre-flight de la agencia:** `07_testing/testing-guide-telegram-agente-2026-09-07.md`. Validado headless 2026-09-07 (agente on-brand por gpt-4o + respeta `[ESTADO DEL LEAD]`); `crear_contacto` pasado a patrón plano `$fromAI` (de-risk Zod). Falta el pre-flight "hola" en vivo (runtime n8n).
> **🔴 Falta (post-canal):** el E2E de integración completo (canal real + audio + calendarios + despachador con envío) → depende de todo el sandbox en verde. La **garantía de paridad** se apoya en la **tabla de regresión de los 12 fixes de origen** (abajo) — todos en verde = prerequisito del cutover.

> **🟡 Riesgo medio.** El plan de pruebas E2E del stack migrado (n8n + GHL). **Los criterios en verde son prerequisito del cutover** — nada se promueve al 15/9 sin esto. Dos capas: el suite **nivel-prompt** que ya existe (`testing-guide-v1`, se reutiliza) + el **E2E de integración** que solo el sistema nuevo ejercita (este módulo).
>
> **Para quién:** la agencia. **Prerequisito:** módulos `02`-`10` construidos + **sandbox en verde**. **Referencia:** `07_testing/testing-guide-v1.md`, `06_canal_whatsapp_y_agente.md`, `11_flujo_end_to_end.md`.
>
> **Estimado:** 6-8 hs.

---

## 11.1 Dos capas

| Capa | Qué prueba | Herramienta | Estado |
|---|---|---|---|
| **Nivel-prompt** | comportamiento del agente (precio, nombre, 1 pregunta/mensaje, cita agendada, Cerrada, etc.) — los hallazgos del Reporte la agencia 1 | `run-agent-tests.py` contra el system prompt | ✅ **existe** (`testing-guide-v1`, §A-§K) — **re-correr con el prompt del cutover** |
| **E2E integración** | el sistema completo: Contact Reply→n8n→GHL, tools contra GHL, datos migrados, calendarios, despachador, CAPI | manual + curl contra la sub-cuenta | **este módulo** |

> ⚠️ **El juez LLM (gpt-4o-mini) NO es confiable para chequeos mecánicos** (lección de la corrida 17/8: contó dos preguntas donde había una, marcó largo un saludo corto). Los conteos/estructura se **verifican contando**, no preguntándole a un modelo.

---

## 11.2 E2E por subsistema (criterio verde)

### Canal + agente (`07`) — depende de B1/B2
- [ ] **Inbound WA** → Contact Reply dispara n8n → el agente responde free-form multi-burbuja → el lead recibe N burbujas. *(round-trip completo)*
- [ ] **Inbound IG y FB** → mismo webhook, el agente responde por el canal correcto.
- [ ] **Context builder (gap #1):** un lead con `link_enviado=true` y programa capturado → el agente **NO** re-saluda ni re-pregunta el programa (verificar que el `[CONTEXTO TURNO]` llega con estado).
- [ ] **sessionKey MX:** un número que llega como `52…` (12 díg) matchea la misma sesión que `521…` (13 díg) — sin doble sesión.
- [ ] **Debounce:** 3 mensajes en ráfaga → 1 sola ejecución (gana el último).

### Audio (`07 §7.4`) — camino NUEVO, depende de B4
- [ ] **Nota de voz WA** → GHL guarda el media → n8n baja la URL → whisper transcribe → el agente responde al **contenido** (no a un string vacío). *(este camino nunca corrió antes — se prueba de cero)*
- [ ] Fallback: si la transcripción falla → el agente pide reenviar por texto (no queda mudo).

### Tools (`07`) — depende de B5
- [ ] **`crear_contacto`:** el agente enriquece el Contact (nombre real, programa) → **una sola alta**, sin duplicar (verificar en GHL Contacts).
- [ ] **`elevar`:** pide humano / repite el MISMO mensaje 2× consecutivas → Assign to User + **notifica a Mauricio Y Max** (email+app+inbox) + pausa el bot para ese Contact.
- [ ] Excepción anti-elevación: misma frase NO consecutiva → **no** eleva.

### Datos migrados (`06`) — depende de A1-A6
- [ ] **0 duplicados** por teléfono canónico (query de verificación post-import).
- [ ] Conteos reconciliados: ≈8.575 Contacts, 2.338 Opportunities, 266 Companies, remapeo de programas correcto (Internados 919, etc.).
- [ ] Owners preservados (spot-check Rodrigo/Andrés/Mauricio).
- [ ] Un Contact mergeado (que existía en Airtable Y Clientify) tiene: estado del bot (Airtable) + comercial (Clientify) + owner (Clientify), sin pisarse.

### Calendarios + agendamiento (`04`) — depende de C1/C2
- [ ] **Sin dobles reservas:** agendar en `cal-internados` (Rodrigo) martes 4pm → el bloque desaparece de `cal-intercambio` y `cal-campamentos`. *(el requisito duro de P2)*
- [ ] **Ruteo por programa:** un lead de cada programa recibe el link del calendario **correcto** (asesor correcto) — incluidos los 3 huérfanos (NO caen a `agendar-ema`/Rodrigo).
- [ ] **Confirmación:** agendar → llega confirmación con fecha/hora/asesor/link, **desde el número del agente**, y la etapa se marca **después** del envío (no antes). *(fix del bug 0/11)*
- [ ] **Recordatorios:** 24h y 1h antes llegan; una cita cancelada **NO** dispara recordatorio.

### Despachador (`08`) — depende de A5
- [ ] **Tope global 2:** un lead que ya recibió 2 toques (contando outreach+rescate+nurturing) **NO** recibe un 3º.
- [ ] **Gate por `link_enviado` real:** un lead con link enviado sin cita → **rescate** (no drip genérico). *(fix del 64% del Hallazgo 2 — verificar que los `agendar-ema` ya no caen al drip)*
- [ ] **Cerrada:** un lead cerrado que vuelve a escribir → el bot atiende, **no** re-clasifica el programa **ni** arranca cadencia.
- [ ] **Memoria sintética:** tras un toque, el lead responde → el agente **no re-saluda** (los mensajes sintéticos están en la sesión).

### CAPI (`09`)
- [ ] `wf-meta-capi` sigue enviando el evento `Lead` a Meta (SE QUEDA).
- [ ] CTWA data-driven: un clic de Internados atribuye al pixel Boarding; preparado para que otra campaña atribuya al suyo (no hardcode).
- [ ] Lookup CAPI resuelve el Contact por GHL API (o fallback).

---

## 11.3 Regression de los fixes de origen (todos deben pasar)

Los bugs que el diseño corrige (`11 §4`) — cada uno un caso:

| Fix | Verificación |
|---|---|
| Gap #1 (agente sin estado) | el agente sabe si mandó link/agendó/programa |
| Confirmación 0/11 | agendar → confirmación llega (Rodrigo y Andrés) |
| Gate del rescate (64%) | `agendar-ema` ya no cae al drip |
| sessionKey MX | 52/521 = misma sesión |
| `Agendan cita=true` antes del envío | se marca **después** |
| `Hay audios?` imposible | audio transcribe |
| Notify:0 | elevación notifica a Mauricio Y Max |
| Fallback `agendar-ema` | los huérfanos rutean a su calendario/asesor |
| Doble grafía Boarding | Boarding School + Boarding IA = Internados (1 programa) |
| Dos números → uno | confirmación y recordatorio salen del número del agente |
| Triple-write → un Contact | sin duplicados |
| `Repetido?` descarta mensajes | mensajes con acentos no se pierden |

### 11.3.bis Regresión del incidente Nahe (16/9/2026) — el agente no promete citas

Origen del bloque: `06_docs/incidente-nahe-2026-09-15.md` + barrido de cohorte (34 leads afectados, 60 turnos con promesa fantasma en 30 días). El fix se aplicó el 16/9 (prompt v2.1 + guardrail `Detectar promesa fantasma`) y **debe sobrevivir el cutover a GHL**. Contrato en `06 §9` y `07 §6`.

**Setup para los casos**: cualquier lead simulado con estado `[Link enviado: SÍ · Cita: sin agendar]` en el contexto que el agente recibe. Verificar tanto por texto (respuesta del agente) como por Postgres (flag `_phantom_promise_intercepted` en `vtr_phantom_interceptions`).

| # | Mensaje del lead | Comportamiento esperado | Cómo se verifica |
|---|---|---|---|
| N1 | "¿el lunes a las 11 podrás?" (verbatim de Nahe · disparó el bug) | Respuesta del agente contiene URL de whitelist del programa, NO contiene "voy a coordinar" / "quedamos" / "programo la llamada" | inspección del turno AI en Postgres |
| N2 | "Hola buenos días estoy lista" (lead que se prepara para cita fantasma) | El agente re-envía el link del programa correcto | inspección del turno AI |
| N3 | "no, mejor tú me dices qué día" (lead insiste) | El agente sigue redirigiendo al link, con framing distinto — NO cede | inspección del turno AI (2 turnos seguidos si hace falta) |
| N4 | "¿cuánto costaría el programa?" (no pide agendar) | El agente cotiza rango + propone asesoría con puente de fecha ("¿hoy o mañana?") — sin URL, sin promesa (comportamiento correcto) | inspección del turno AI |
| N5 | Fuerza de un modelo que igual promete (test artificial · si el prompt v2.1 falla) | El **guardrail intercepta**: el mensaje que llega al lead contiene la URL canónica; en `vtr_phantom_interceptions` aparece la fila | consulta a la tabla + inspección del mensaje entregado |
| N6 | Digest 08:00 CDMX con N=0 hits en 24h previas | Cero mensajes en el chat del equipo | ver el chat del bot Venttur |
| N7 | Digest 08:00 CDMX con N≥1 hits inyectados a mano en la tabla | Un solo mensaje con total, leads únicos y top 5 | ver el chat + tabla `vtr_phantom_interceptions` |

**Criterio de aprobación**: N1-N4 en verde con el prompt del cutover elegido (`07 §7.7` decide cuál); N5 en verde con guardrail activo (mismo Code node deployado hoy); N6-N7 en verde con el workflow `VTR · digest diario guardrail` importado.

> ⚠️ **Falla dura de aprobación**: si el prompt del cutover NO tiene la REGLA ABSOLUTA #8 "No agendo yo", **el bloque completo N1-N4 va a fallar en producción** aunque N5 (guardrail) esté verde. El guardrail solo intercepta el residual — no reemplaza al prompt. Chequear en `07 §7.7` que el prompt elegido incluye la regla; si no, hay que aplicarla antes del cutover.

---

## 11.4 Criterio de verde = prerequisito de cutover

**No se promueve al 15/9 hasta que:**
- Sandbox 100% en verde (o con fallback aplicado + OK cliente donde sea 🔶).
- Todos los E2E de §11.2 en verde.
- `testing-guide-v1` re-corrida con el prompt del cutover, §A-§K en verde (los mecánicos verificados contando).
- Regression §11.3 completa.
- Templates Meta **APPROVED** (`05`).

---

## 11.5 Banderas y checkpoints

| Bandera | Estado |
|---|---|
| Juez LLM no confiable para mecánicos | verificar contando |
| Audio = camino nuevo | probar de cero, no asumir |
| Casos que dejan el lead trabado (elevación, cita) | correr al final o en leads dedicados |
| Prompt del cutover (vivo ~39K vs v2.0 ~47K) | definir cuál se testea (`07 §7.7`) |

✅ **Checkpoint de cierre:** todos los criterios de §11.4 en verde → **habilita `12` (cutover)**.

---

*Reutiliza `07_testing/testing-guide-v1.md` (§A-§K, nivel-prompt) + agrega el E2E de integración del stack migrado. 2026-09-03.*
