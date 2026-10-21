# 10 · Los 3 programas huérfanos — construir desde cero

> ### 🔄 Estado a 2026-09-07 — 🟡 PENDIENTE (bloqueado en assets del cliente)
> El enum `programa_interes` ya incluye los 3 (`02` ✅). Falta el resto de los deltas (calendarios, templates, ruteo, nurturing/rescate propios). **🔴 [CLIENTE]:** aportar los **textos/assets** de outreach/rescate/nurturing de los 3 (`Viajes educativos`, `Educación superior`, `Cursos de idiomas`) + definir la **forma del pipeline comercial de Viajes educativos** (100% nuevo, no existe en el snapshot). Regla: los 3 **no cotizan** → derivan a asesoría. Es el ítem que más presiona el 15/9 (Opción A no difiere nada).

> **🟢 Scope nuevo (no traducción).** Tres de los 8 canónicos **no existen en el bot**: `Viajes educativos`, `Educación superior`, `Cursos de idiomas en el extranjero`. No tienen enum, ni drip, ni rescate, ni pixel, ni landing. Hay que **construirlos**. Este módulo reúne los **deltas** que se aplican dentro de `02`/`03`/`04`/`05`/`07`/`08` — juntos acá para que la **dependencia de assets del cliente** y el **riesgo de timing B3** queden en un solo lugar visible.
>
> **Para quién:** la agencia + cliente (aporta textos/assets). **Referencia:** `10_programas_nuevos.md`.
>
> **Estimado:** 4-8 hs (según cuándo lleguen los assets). Corroborado contra `ESTADO` Hallazgo 20 + snapshot Clientify.

---

## 10.1 "Huérfano" es del lado bot, no del negocio

| Programa | ¿En el bot? | ¿Comercial (Clientify)? | Realmente nuevo |
|---|---|---|---|
| **Educación superior** | ❌ 0 hits | ✅ `Operativo Educación superior` (12 deals) | **solo el lado bot** |
| **Cursos de idiomas** | ⚠️ 1 link suelto | ✅ `Operativo Idiomas` (22 deals) | **solo el lado bot** |
| **Viajes educativos** | ❌ 0 hits | ❌ sin pipeline | **100% nuevo, ambos lados** |

→ Educación superior e Idiomas **ya se trabajan a mano** comercialmente (sus `Operativo *` migran en `03`); falta el **frente automatizado**. Viajes educativos hay que crearlo también en el pipeline comercial.

**Impacto medible hoy (bug de negocio):** un lead de Educación superior no matchea nada → cae al fallback `agendar-ema` = link de **Internados con Rodrigo** (programa Y asesor equivocados; el cliente lo asignó a **Andrés**) → no recibe rescate (`RESCATE_PROGRAMA_NO_MAPEADO`) → sin drip.

---

## 10.2 Checklist idéntico por programa (`ronda-2 §7`: "tratamiento completo")

Cada uno de los 3 necesita, y **dónde se aplica el delta**:

| Pieza | Delta | Módulo |
|---|---|---|
| **Valor de enum** `programa_interes` | agregar los 3 al dropdown | `02 §2.3.1` |
| **Calendario propio** | `cal-viajes-educativos`, `cal-educacion-superior`, `cal-cursos-idiomas` — **todos Andrés** | `04 §4.1` |
| **Ruteo del agente** | el prompt aprende a detectar/rutear los 3 (matriz de links) | `07 §7.3` (prompt) |
| **Nurturing propio** | secuencia de toques por programa (tope 2) | `08` despachador |
| **Rescate propio** | rama de rescate por programa (link sin cita) | `08` despachador |
| **Templates propios** | textos de outreach/rescate/nurturing | `05` Message Templates |
| **Atribución** | pixel/tracking por programa (aunque no haya campaña aún) | `09 §9.2` |
| **Cotización** | **el bot NO cotiza** → asesoría (§10.3) | `07` (prompt) |
| **Pipeline comercial** | Idiomas y Educación superior **ya lo tienen**; **Viajes educativos hay que crearlo** | `03` |

---

## 10.3 La regla de precio (los 3 no cotizan)

**`ronda-2 §8`:** rangos de los 3 = **"-"** → **el bot NO da precio en esos 3 y pasa directo a asesoría.**

En el prompt (`07`): para los otros 5 el agente da rango + cierre con fecha; para estos 3, el flujo de precio se reemplaza por **"te lo aterriza el asesor en la videollamada"** + agenda directa al calendario del programa (Andrés). Es una regla explícita de derivar sin cifra, no un "no sé". Cuando el cliente defina rangos, se agregan sin tocar la topología.

---

## 10.4 Viajes educativos — el único 100% nuevo

Necesita, además de todo lo anterior, un **pipeline comercial nuevo** (los otros 2 tienen `Operativo *`). Opciones: coordinar con el equipo comercial las etapas de delivery, o **clonar un `Operativo *` análogo** (`03`). No es problema de diseño — es de contenido y coordinación.

---

## 10.5 🟡 Gate — assets del cliente + timing B3

**El cliente aporta los textos propios** (`ronda-2 §7`). Advertencia del propio cliente: *"es scope grande. Puede empujar contra el B3 (cutover completo 15/9)… depende de si la agencia tiene los assets para construir los 3 en 4 semanas o si el cliente los aporta."*

→ **Dependencia de assets, no de diseño.** **B3 = Opción A (completo, cliente 2026-09-03):** los **3 huérfanos completos entran el 15/9** — con calendario + asesor + ruteo + nurturing/rescate/templates propios. **No hay "mínimo viable" que difiera a una 2ª ola** (esa era la Opción B, descartada). → **exige los textos/assets del cliente YA**; es el ítem de este módulo que más presiona el 15/9. Si los assets no llegan a tiempo, es lo primero que se pone sobre la mesa en la conversación de fecha (`12 §12.1`), no algo que se difiere en silencio.

> **`Francia` NO es uno de estos** — es un **destino** (`destino_interes`, nota), nunca programa (`01 §5`). No confundir con "Viajes educativos".

---

## 10.6 Banderas y checkpoints

| Bandera | Estado |
|---|---|
| Textos/assets de los 3 | 🟡 los aporta el cliente — **gate de timing B3** |
| Viajes educativos: pipeline comercial nuevo | coordinar con comercial o clonar `Operativo *` |
| Rangos de precio "-" | no bloquea (regla por defecto: no cotiza → asesoría) |
| Atribución sin campaña activa | pixel data-driven preparado (`09`), no forzado a Boarding |

✅ **Checkpoints de cierre:**
- [ ] Los 3 valores de enum agregados (`02`).
- [ ] 3 calendarios (Andrés) creados (`04`).
- [ ] Ruteo del prompt aprende los 3 + regla no-cotiza (`07`).
- [ ] (B3 = A) nurturing/rescate/templates propios de los 3 completos (`05`/`08`) — con los assets del cliente, para el 15/9.
- [ ] Viajes educativos: pipeline comercial creado (`03`).
- [ ] Pixel/atribución preparado para cuando haya campaña (`09`).
- [ ] El fallback `agendar-ema` deja de rutear los 3 a Internados/Rodrigo.

---

*Corroborado contra `ESTADO` Hallazgo 20 (0 hits) y el snapshot Clientify (Operativo Educación superior 12, Operativo Idiomas 22, sin Operativo Viajes educativos). 2026-09-03.*
