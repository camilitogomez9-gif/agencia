# 04 · Calendarios GHL + confirmación + recordatorios

> ### 🔄 Estado a 2026-09-07 — 🔴 PENDIENTE (no arrancado; gate de cutover)
> Owner split de lo que falta:
> - **[LA AGENCIA-GHL]** crear los **8 calendarios** (uno por programa) + cablear confirmación + recordatorios 24h/1h.
> - **[LA AGENCIA-sandbox]** validar **C1** (disponibilidad compartida por asesor) y **C2** (trigger de booking + query de appointments) — aún sin correr.
> - **[CLIENTE-asesores]** Rodrigo y Andrés **conectan su calendario personal** (OAuth) a GHL — sin esto no hay disponibilidad real.
> - **[CLIENTE]** aportar los **textos** de confirmación y recordatorios (hoy en Clientify) → hasta entonces, placeholders.
> - **[CLIENTE-decisión 🔶]** si C1 no se resuelve nativo → fallback **1 calendario por asesor** (contradice P2, requiere OK).

> **🟡 Riesgo medio.** Reemplaza los 3 Google Calendar Triggers + la matriz de links de Clientify por **8 calendarios nativos de GHL (uno por programa)** con **disponibilidad compartida por asesor**, reconstruye la **confirmación** (hoy rota: 0/11 enviadas) y **construye de cero** los **recordatorios pre-cita** que hoy salen de un segundo número en Clientify.
>
> **Para quién:** la agencia. **Prerequisito:** módulo `02` (usuarios Rodrigo/Andrés creados) + sandbox **C1** (disponibilidad compartida) y **C2** (trigger booking + query appointments). **Referencia:** `07_agendamiento_calendarios.md`, `cuestionario` P2/P9, `ronda-2` §3/§4.
>
> **Estimado:** 4-6 hs. Corroborado contra `wf-confirmacion-agenda.json` y las decisiones del cliente.

---

## 4.1 Los 8 calendarios (uno por programa)

**Decisión cliente (P2):** *"un calendario por programa (8), así el sistema sabe desde el agendamiento a qué programa pertenece cada cita, sin etiquetado manual."*

| # | Programa (`01`) | Calendario GHL | Asesor | Link viejo (muere) |
|---|---|---|---|---|
| 1 | Internados | `cal-internados` | **Rodrigo** | `agendar-ema` |
| 2 | Intercambio académico con familias | `cal-intercambio` | **Rodrigo** | `AAFamilia-Agendar` |
| 3 | Campamentos de verano | `cal-campamentos` | **Rodrigo** | `SummerCamp-Agendar` |
| 4 | Viajes educativos ⭐ | `cal-viajes-educativos` | **Andrés** | *no existía* (`10`) |
| 5 | Educación superior ⭐ | `cal-educacion-superior` | **Andrés** | *no existía* (`10`) |
| 6 | Cursos de idiomas ⭐ | `cal-cursos-idiomas` | **Andrés** | *(dudoso, `01` bandera 1)* |
| 7 | Pathway Alemania | `cal-pathway-alemania` | **Andrés** | `PW_Alemania_Agendar` |
| 8 | Gap Year / Estudia y Trabaja | `cal-gap-year` | **Andrés** | `Estudiar-y-Trabajar-en-Australia` |

**Reparto:** Rodrigo 3 · Andrés 5 · **Diego fuera del ruteo automático** (`02 §2.2`).

> **`agendar-ema` NO es un asesor.** Es el slug del calendario de Internados (Rodrigo) + el fallback genérico. Hoy es un **bug de negocio** (Educación superior cae al calendario de Rodrigo = programa Y asesor equivocados). Se elimina con los 8 calendarios reales (`10`). "EMA" por separado es la metodología del agente.

---

## 4.2 Disponibilidad compartida por asesor (el requisito duro) — depende de sandbox C1

**Decisión cliente (P2):** los calendarios de un mismo asesor **comparten disponibilidad**. Si alguien agenda "Internados" el martes 4pm, ese bloque **desaparece** de "Intercambio" y "Campamentos". **No dobles reservas.**
- **Rodrigo:** cal 1+2+3 = un solo pool.
- **Andrés:** cal 4+5+6+7+8 = un solo pool (5 calendarios).

⚠️ **GHL no lo hace out-of-the-box.** El mecanismo se decide **según el resultado del sandbox C1** (probar en orden, parar en el que pase):
- **(a)** cada asesor conecta su **calendario personal** (Google/Outlook) a GHL + cada calendario GHL con **"check for conflicts"** contra él → un booking bloquea los otros vía el calendario común.
- **(b)** GHL **Team / Service calendars** con el mismo usuario en varios event-types.
- **Fallback 🔶** (si (a)/(b) fallan): **1 calendario por asesor con event-types por programa** — la disponibilidad se comparte nativo (es un solo calendario); el programa lo distingue el event-type. Cumple el objetivo real, pero **contradice P2** → **requiere OK del cliente** (`01 C1`, `07 §2`).

**Dependencia dura:** Rodrigo y Andrés deben existir como usuarios GHL con su **calendario personal conectado** (§4.4 de `02` + este §).

---

## 4.3 Confirmación de cita (hoy rota → se reconstruye) — depende de C2

**Hoy (roto):** 3 Google Calendar Triggers (`eventCreated`) sobre `dgarcia@`/`agarcia@`/`rgarcia@venttur.com` → `wf-confirmacion-agenda` → cruce frágil GCal→Clientify→Airtable. Los paths de **Andrés y Diego referencian nodos inexistentes** → **de 11 leads que agendaron, 0 recibieron confirmación** (solo Rodrigo andaba); y `Agendan cita=true` se escribe **antes** del envío → el lead queda marcado como agendado, sin confirmación **y excluido de todo seguimiento**.

**Destino:**
- El booking en un **GHL Calendar** dispara un **workflow GHL → HTTP a n8n** (sandbox C2) → confirmación. Fallback: cron n8n que lee citas próximas.
- **Contenido (`ronda-2 §4`):** **fecha, hora, asesor y link de videollamada.** Sin campos extra.
- **Un solo número** (el del agente) — la confirmación sale del mismo canal.
- 🔧 **Fix del orden:** la etapa "Cita agendada"/`Agendan cita` se marca **después** (o junto con) el envío exitoso → el lead no queda marcado si la confirmación falla.
- 🔧 **El path de Diego se BORRA** (no se repara — Diego sale del ruteo). Solo se cablean Rodrigo y Andrés.
- **El directo de Rodrigo `+52 1 33 1944 2476`** (que hoy el flow comparte al agendar) se **preserva** en el texto de la confirmación de Internados/Rodrigo (dato de negocio, `06 §7`).

---

## 4.4 Recordatorios pre-cita (de cero) — depende de C2

**Decisión cliente (`ronda-2 §3`):** **dos recordatorios — 24h antes y 1h antes.**

⚠️ **Hoy NO existen en los 14 workflows** — salen de **Clientify, desde un segundo número** (el lead agenda con un número y el recordatorio le llega de otro → confunde). En GHL:
- Se **reconstruyen de cero** (no hay workflow que migrar).
- Salen del **mismo número del agente** (consolidación, `06 §7`).
- **24h + 1h antes** de la cita, disparados por el GHL Calendar (o cron n8n que lee citas próximas — sandbox C2).
- El **segundo número de Clientify muere y NO se avisa** (`portabilidad §8`).
- Como son **fuera de la ventana de 24h** → **Message Template** (`05`). El de 1h puede caer dentro de ventana si el lead interactuó → free-form si aplica.
- ⚠️ **Chequear estado de la cita** antes de mandar (no recordar una cancelada/reagendada).
- **Textos:** los aporta el cliente (los actuales de Clientify); hasta entonces, placeholders.

---

## 4.5 La matriz de links del agente → calendarios GHL

El agente "Mauricio" hoy manda `promo.venttur.com/<slug>` según el programa detectado. En destino → **links de booking de los 8 calendarios GHL**. El agente sigue eligiendo el link por el programa que **surge de la conversación** (no del anuncio — atribución y conversación separadas, `01`/`06`). El fallback `agendar-ema` deja de ser un parche: cada programa tiene su calendario real (incluidos los 3 nuevos, `10`).

> El detalle del reemplazo de la matriz de links en el prompt del agente vive en `07` (es cambio de prompt); acá se fija que **cada slug viejo → link del calendario GHL correspondiente** (tabla §4.1).

---

## 4.6 Banderas y checkpoints

| Bandera | Estado |
|---|---|
| Disponibilidad compartida (mecanismo a/b/fallback) | **sandbox C1** — fallback 1-cal-por-asesor 🔶 requiere OK cliente |
| Trigger de booking + query de appointments | **sandbox C2** — fallback: cron n8n |
| Recordatorio de 1h: dentro o fuera de ventana 24h | confirmar (define template vs free-form) |
| Owners de calendarios (Rodrigo/Andrés) con calendario personal conectado | dependencia de `02` + §4.2 |
| Textos de confirmación/recordatorio | los aporta el cliente; placeholders hasta entonces |
| 2FA / reconciliación de números | el del agente sobrevive, el de Clientify muere (`05`/`06 §7`) |

✅ **Checkpoints de cierre:**
- [ ] 8 calendarios creados (o el fallback 1-cal-por-asesor con OK del cliente).
- [ ] Disponibilidad compartida funcionando por asesor (sin dobles reservas — verificado).
- [ ] Confirmación cableada (Rodrigo + Andrés; **path de Diego borrado**) con fecha/hora/asesor/link + **orden corregido** (marca después del envío).
- [ ] Recordatorios 24h + 1h construidos, desde el número del agente, con chequeo de estado de cita.
- [ ] Matriz de links del agente repuntada a los 8 calendarios GHL.

---

*Corroborado contra `wf-confirmacion-agenda.json` (bug 0/11 + orden invertido + paths Andrés/Diego rotos), `cuestionario` P2/P9, `ronda-2` §3/§4. 2026-09-03.*
