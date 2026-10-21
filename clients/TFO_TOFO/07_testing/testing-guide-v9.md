# Testing Guide v9 — TOFO Pizza

**Fecha:** 2026-06-22
**Prompt objetivo:** B2B v1.17 — bump v1.16 → v1.17 (precio detrás del gate nombre + ubicación + citas de 30 minutos)
**Workflow objetivo:** `Agente WEB B2B y RRSS v5` (vivo)
**Sub-workflow objetivo:** `Chequear disponibilidad | Tofo v4` (workflowId `vpLmZ299yXJrOSBv`) — evento de Calendar de 30 min
**Cliente:** Mauricio García de la Vega (TOFO Pizza, Robotic Vending de México)
**Objetivo:** Validar la instrucción de Mauricio 22/6/26 — (1) el agente NO da el precio de la máquina antes de capturar nombre + ubicación; (2) las citas se programan de 30 minutos.

---

## Contexto del cambio

Mauricio observó en producción (22/6/26):

> *"Solo veo que el agente da precios antes de preguntar nombre y ubicación… mover el dar la info de precios hacia adentro del gate (nombre + usuario)."*

> *"Y también que programe las citas de 30 minutos por favor."*

**2 fixes:**
1. **§9 del prompt B2B reescrita (REVIERTE v1.9):** el precio de la máquina (USD 9.300 / 26.300 + equivalentes MXN) vuelve a quedar detrás del gate nombre + ubicación. Mismos dos datos del gate de `registrar`. Escenario 1 (lead pregunta precio sin gate) → pedir nombre + ubicación primero, sin soltar la cifra. Escenario 2 (proactivo) → capturar datos, luego consent question.
2. **Citas de 30 min:** prompt (texto que comunica el agente) + sub-workflow `chequear-disponibilidad` v4 (el evento de Calendar pasa de `inicio + 1h` a `inicio + 30 min`; el Zoom ya era de 30 min).

**Sin tocar:** RRSS (precio de menú al consumidor = retail, no aplica el gate de lead), ni Derivación/Servicio/Reposición.

---

## Estructura de herencia

Esta guía v9 **hereda íntegros** todos los bloques de `testing-guide-v8.md`:

| Sección heredada | Origen | Qué cubre |
|---|---|---|
| **§A** | v7→v8 | 10 tests pin-data sub-workflow `chequear-disponibilidad` (⚠️ actualizar a v4 para chequear duración 30 min — ver §R) |
| **§B** | v7→v8 | 17 tests conversación E2E B2B |
| **§C** | v7→v8 | 12 tests regression Oscar Amaya (moneda) |
| **§G** | v7→v8 | 18 tests regression Mauricio 8/6 |
| **§H** | v7→v8 | 5 tests Ghost-booking |
| **§I** | v7→v8 | 4 tests Timezones MX |
| **§K** | v7→v8 | 3 tests Financiamiento proactivo |
| **§M** | v7→v8 | 3 tests ficha técnica + video |
| **§N** | v7→v8 | 2 tests Airtable captura |
| **§P** | v8 | 6 tests Anti-tool-rogue |
| **§Zoom** | v7→v8 | 5 verificaciones cuenta real Mauricio |

⚠️ **§J (Precio + Consent) de v7/v8 queda SUPERSEDED por §Q de v9.** Los casos §J validaban la lógica v1.9 ("precio inmediato sin gate"), que v1.17 revierte. NO correr §J contra v1.17 — fallaría por diseño. §Q es su reemplazo.

Las secciones **nuevas** en v9 son: **§Q — Precio detrás del gate** (automatizable) y **§R — Citas de 30 minutos** (manual).

---

## §Q — Precio detrás del gate nombre + ubicación (NUEVA en v9)

**Objetivo:** verificar que el agente B2B NO revela el precio de la máquina (USD 9.300 / 26.300 ni equivalentes MXN ~$165.000 / ~$460.000) hasta tener **nombre Y ubicación** del lead dichos en el chat. Y que SÍ lo da apenas el gate se cumple (no sobre-bloquea).

> **Nota de scope:** el gate retiene SOLO la cifra de precio. El agente puede y debe responder funcionamiento, specs, diferencias estructurales (sin números), urgencia, etc., sin gate.

> **⚠️ Criterio de evaluación (importante para el juez):** el ÚNICO descalificador del gate es que aparezca una **CIFRA NUMÉRICA de precio de máquina** (cualquiera de: `9.300`, `9,300`, `26.300`, `26,300`, `165.000`, `460.000`, o cualquier monto en USD/MXN). **Que el agente DIGA que "con gusto te paso los precios" o "te los doy enseguida" NO es una violación — es el comportamiento correcto y esperado** (cortesía de asesoría). Lo que cuenta es que ningún NÚMERO de precio aparezca antes de tener nombre + ubicación. Marcá `true` si no hay cifra numérica y el agente pide los datos; marcá `false` solo si aparece un número de precio.

### Casos simples

| # | Mensaje | Resultado esperado |
|---|---------|--------------------|
| Q1 | Hola, ¿cuánto cuesta la máquina TOFO? | NO aparece NINGUNA cifra numérica de precio. El agente pide el nombre Y la ciudad/país antes de dar precios. Decir "con gusto te paso los precios" es CORRECTO mientras no haya número. |
| Q2 | Hola, info y precio de la máquina porfa | NO aparece NINGUNA cifra numérica. El agente pide nombre + ciudad/país primero, con tono cálido. Ofrecer compartir los precios tras los datos es CORRECTO. |
| Q3 | Soy Federico, ¿cuánto sale la máquina? | Gate parcial (tiene nombre, falta ubicación). NO aparece ninguna cifra numérica. El agente pregunta desde qué ciudad/país escribe. Decir "te paso los precios" sin número es CORRECTO. |
| Q4 | Estoy en Monterrey, ¿qué precio tiene la máquina? | Gate parcial (tiene ubicación, falta nombre). NO aparece ninguna cifra numérica. El agente pregunta con quién tiene el gusto. Ofrecer los precios tras el nombre es CORRECTO. |
| Q5 | Soy Ana de Guadalajara, ¿cuánto cuesta la máquina? | Gate CUMPLIDO (nombre + ubicación en el mismo mensaje). SÍ aparecen las cifras de ambas opciones (Opción A ~9.300 USD y Opción B ~26.300 USD o equivalente MXN) + pregunta de continuidad. |
| Q6 | ¿Cuál es la diferencia entre la opción A y la opción B? | Gate NO cumplido → NO aparece ninguna cifra numérica de precio. El agente pide nombre + ciudad/país antes de dar los precios. (Plus opcional, no obligatorio: que mencione la diferencia China vs México sin números.) |
| Q7 | Quiero comprar una máquina TOFO | Escenario 2 (intención sin pedir precio). El criterio es SOLO la ausencia de DÍGITOS de precio (9300, 26300, 165000, 460000). Frases como "te paso los precios oficiales", "te comparto los precios", "y los detalles" son CORRECTAS y NO descalifican. Marcá `true` si el agente pide nombre + ubicación y NO escribe ningún número de precio; marcá `false` SOLO si aparece un monto con dígitos. |
| Q8 | No me interesa darte mis datos, solo dame el precio | NO aparece NINGUNA cifra numérica. El agente reencuadra el pedido de nombre/ciudad como cortesía de asesoría, sin sonar a condición fría. Decir "te paso los precios enseguida" sin número es CORRECTO. |

### Flujo Q-F1 — Gate progresivo (nombre en un turno, ubicación en otro)

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|--------------------|
| 1 | user | Hola, ¿cuánto cuesta la máquina? | NO aparece ninguna cifra numérica de precio. Pide nombre + ciudad/país con tono cálido. Decir que pasará los precios (sin número) es CORRECTO. |
| 2 | user | Soy Diego | NO aparece ninguna cifra numérica (falta ubicación). Saluda a Diego y pide la ciudad/país. |
| 3 | user | Desde CDMX | Gate CUMPLIDO. SÍ aparecen las cifras de ambas opciones (Opción A ~9.300 USD / Opción B ~26.300 USD o equivalente MXN) + pregunta de continuidad. |

### Flujo Q-F2 — Proactivo con consent (Escenario 2)

| Turno | Rol | Mensaje | Resultado esperado |
|-------|-----|---------|--------------------|
| 1 | user | Me interesa el negocio de las pizzas robóticas | NO aparece ninguna cifra numérica. Conversa sobre el modelo y/o pide el nombre para asesorar. |
| 2 | user | Soy Lucía, estoy en Puebla | Gate cumplido, pero el lead NO pidió precio → pregunta de consent ("¿Quieres que te pase el precio de la máquina TOFO Pizza?"). NO aparece la cifra todavía (espera el SÍ). |
| 3 | user | Sí, dale | SÍ aparecen las cifras de ambas opciones + pregunta de continuidad. |

---

## §R — Citas de 30 minutos (NUEVA en v9 — MANUAL / pin-data)

**Objetivo:** verificar que las citas se crean de **30 minutos** (no 1 hora) en Google Calendar, y que el agente comunica "30 minutos" al lead.

### R1 — Texto del agente (automatizable parcial)

El agente, al proponer/confirmar la llamada, comunica **30 minutos** (no "1 hora", no "15 minutos"). Buscar en cualquier mensaje de agendamiento la mención de duración.

### R2 — Duración del evento de Calendar (MANUAL — pin data sub-workflow v4)

**Setup:** ejecutar el sub-workflow `Chequear disponibilidad | Tofo v4` con un horario válido (ej. próximo lunes 11:00 CDMX, `fecha_hora = "<próximo-lunes>T11:00:00-06:00"`).

**Verificación crítica:**
1. El nodo `Validar entrada` devuelve `fecha_fin` = `fecha_inicio + 30 minutos` (ej. inicio 11:00 → fin 11:30). **NO 12:00.**
2. El nodo `Crear evento` crea el evento en Google Calendar de **11:00 a 11:30** (30 min de duración). **NO de 11:00 a 12:00.**
3. El nodo `Crear meeting Zoom` mantiene `duration: 30` (ya estaba).

**Criterio binario:** ✅ si el evento de Calendar dura 30 min exactos.

### R3 — Overlap con 30 min (MANUAL)

**Setup:** crear cita en lunes 11:00 (queda 11:00–11:30). Pedir segunda cita lunes 12:00 (12:00–12:30).

**Verificación:**
- La segunda cita (12:00) NO debe colisionar con la primera (11:00–11:30) → `libre: true`, se crea.
- Con eventos de 30 min, los slots 10/11/12 nunca se solapan entre sí (están a 1 h de distancia). Confirmar que `Evaluar solapamiento` calcula `finCupo = inicio + 30 min` y no bloquea slots adyacentes de más.

**Criterio binario:** ✅ si las dos citas (11:00 y 12:00) coexisten sin que el sub-workflow marque falso `ocupado`.

---

## §D — Checklist de Promoción TESTING → LIVE (v9)

| Bloque | Casos | Mínimo PASS | Automatizable |
|---|---|---|---|
| **§Q — Precio detrás del gate** | Q1-Q8 + Q-F1 + Q-F2 | 10/10 | ✅ (run-agent-tests.py) |
| **§R — Citas de 30 min** | R1-R3 | 3/3 | R1 parcial / R2-R3 manual |
| §A — Pin data (actualizado a v4 con duración 30 min) | A1-A10 | 10/10 | manual |
| §P — Anti-tool-rogue | P1-P6 | 6/6 | parcial |
| §C/§G/§H/§I/§K/§M/§N (heredados) | — | sin cambio | — |

⚠️ **NO correr §J de v7/v8** (superseded por §Q).

### Pre-requisitos antes del deploy

1. Prompt B2B **v1.17** subido al Google Doc vivo (verificar que el `Get a document` del main lo carga + sincronizar el set-node `backup` con el v1.17).
2. Sub-workflow **`chequear-disponibilidad-tofo-v4.json`** importado a n8n (overwrite in-place del `vpLmZ299yXJrOSBv`).
3. Smoke piloto de 1 turno: lead pregunta precio sin dar datos → confirmar que el agente NO suelta la cifra.

### Criterio de cierre

- §Q 10/10 ✅ (el agente nunca revela precio sin gate, sí lo da apenas se cumple) + §R 3/3 ✅ (evento Calendar de 30 min) → fix cerrado.

---

## Cómo correr §Q (automatizable)

§Q es 100% conversacional (el gate es comportamiento de texto, no requiere tools) → corrible con el runner contra el prompt v1.17:

```bash
cd ~/Downloads/camilo-workspace
source .env
python3 scripts/testing/run-agent-tests.py \
  --system-prompt clients/TFO_TOFO/04_agents/agente-tofo-b2b-system-prompt.md \
  --testing-guide clients/TFO_TOFO/07_testing/testing-guide-v9.md \
  --model gpt-4.1
```

> El runner evalúa §Q (casos simples + flujos). §R R2/R3 son manuales (pin data del sub-workflow + verificación en Calendar). §P y §A requieren logs de n8n.

---

## Resultado §Q

⬜ Q1 — Precio directo sin datos → no revela cifra
⬜ Q2 — Info+precio sin datos → no revela cifra
⬜ Q3 — Nombre sin ubicación → no revela cifra, pide ciudad
⬜ Q4 — Ubicación sin nombre → no revela cifra, pide nombre
⬜ Q5 — Nombre + ubicación juntos → SÍ da precios
⬜ Q6 — Diferencia A vs B sin datos → explica sin cifras, pide datos
⬜ Q7 — Intención de compra (Escenario 2) → no suelta precio, capta datos
⬜ Q8 — Lead se niega a dar datos → reencuadra cortés, no suelta cifra
⬜ Q-F1 — Gate progresivo (nombre→ubicación→precio)
⬜ Q-F2 — Proactivo con consent

## Resultado §R

⬜ R1 — Agente comunica 30 minutos
⬜ R2 — Evento Calendar dura 30 min (sub-workflow v4)
⬜ R3 — Overlap correcto con 30 min
