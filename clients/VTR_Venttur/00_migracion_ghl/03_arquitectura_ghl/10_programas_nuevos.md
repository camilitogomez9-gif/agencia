# 10 · Los 3 programas huérfanos — construir desde cero

> **🟢 Scope nuevo (no traducción).** Tres de los 8 programas canónicos **no existen en el sistema del bot**: `Viajes educativos`, `Educación superior`, `Cursos de idiomas en el extranjero`. No tienen enum, ni drip de nurturing, ni rama de rescate, ni pixel, ni landing. Hay que **construirlos**, no migrarlos. El cliente pidió tratamiento completo.
>
> Corroborado contra `ESTADO` Hallazgo 20 (grep exhaustivo: 0 hits) y el snapshot Clientify.

---

## 1. Qué significa "huérfano" acá (y el matiz que cambia el trabajo)

"Huérfano" es del lado **automatización** (el bot), no necesariamente del lado **negocio**. El snapshot Clientify lo desambigua:

| Programa | ¿Existe en el bot? | ¿Existe comercialmente (Clientify)? | Realmente nuevo |
|---|---|---|---|
| **Educación superior** | ❌ (0 hits: sin enum/drip/rescate/pixel) | ✅ **`Operativo Educación superior`** (12 deals) | solo el lado bot |
| **Cursos de idiomas** | ⚠️ (1 link suelto en el prompt) | ✅ **`Operativo Idiomas`** (22 deals) | solo el lado bot |
| **Viajes educativos** | ❌ (0 hits) | ❌ (sin pipeline en Clientify) | **100% nuevo, ambos lados** |

→ Educación superior e Idiomas ya se trabajan a mano comercialmente; lo que falta es el **frente automatizado** (que el bot los conozca, rutee, cotice/derive, nurturee). Viajes educativos hay que crearlo también en el pipeline comercial.

**Impacto medible hoy (bug de negocio):** un lead que pregunta por Educación superior no matchea nada → cae al fallback `agendar-ema` = link de **Internados con Rodrigo** (programa Y asesor equivocados; el cliente asignó Educación superior a **Andrés**) → no recibe rescate (cae en `RESCATE_PROGRAMA_NO_MAPEADO`) → sin drip propio.

---

## 2. Qué hay que construir para cada uno (checklist idéntico)

**Decisión cliente (`ronda-2` §7):** *"Tratamiento completo: calendario propio, seguimientos propios, textos propios."* Cada uno de los 3 necesita:

| Pieza | Detalle | Vive en |
|---|---|---|
| **Valor de enum** `programa_interes` | agregar los 3 al dropdown del Contact | GHL Contact (`02`, `04`) |
| **Calendario propio** | `cal-viajes-educativos`, `cal-educacion-superior`, `cal-cursos-idiomas` — **todos Andrés** | GHL Calendars (`07`) |
| **Ruteo del agente** | el prompt aprende a detectar y rutear los 3 (matriz de links `07` §5) | prompt n8n (`06`) |
| **Nurturing propio** | secuencia de toques por programa (sujeta al tope global de 2) | despachador n8n (`09`) |
| **Rescate propio** | rama de rescate por programa (link sin cita) | despachador n8n (`09`) |
| **Templates propios** | textos de outreach/rescate/nurturing por programa | Message Templates GHL (`09`) |
| **Atribución** | pixel/tracking por programa (aunque no haya campaña activa aún) | CAPI, n8n (`05`) |
| **Cotización** | **el bot NO cotiza** → pasa a asesoría (§3) | prompt n8n (`06`) |
| **Pipeline comercial** | Idiomas y Educación superior ya lo tienen (`Operativo *`); **Viajes educativos hay que crearlo** | GHL Opportunities (`03`) |

**Textos:** el cliente aporta los textos propios (`ronda-2` §7). Advertencia del propio cliente: *"es scope grande. Puede empujar contra el B3 (cutover completo 15/9)… depende de si la agencia tiene los assets para construir los 3 en 4 semanas o si el cliente los aporta."* → **dependencia de assets, no de diseño.**

---

## 3. La regla de precio (los 3 no cotizan)

**Decisión cliente (`ronda-2` §8):** los rangos de precio de los 3 = **"-"** → interpretación operativa: **el bot NO da precio en esos 3 programas y pasa directo a la asesoría.** Cuando existan rangos definidos, se agregan.

En el prompt (`06` §3): para los otros 5 programas el agente da rango + cierre con fecha; para estos 3, el flujo de precio se reemplaza por **"te lo aterriza el asesor en la videollamada"** + agenda directa al calendario del programa (Andrés). No es un caso de "no sé" — es una regla explícita de derivar sin cifra.

---

## 4. Banderas de este mapping

1. **Scope vs cutover (B3):** construir los 3 completos en 4 semanas es el ítem que puede empujar contra el 15/9. Depende de **quién aporta los textos/assets** (la agencia vs cliente). No es un problema de diseño — el diseño está; es un problema de contenido y tiempo.
2. **Rangos de precio "-":** no bloquea (la regla por defecto es no cotizar → asesoría). Cuando el cliente defina rangos, se agregan al prompt sin tocar la topología.
3. **Viajes educativos necesita pipeline comercial nuevo** (los otros 2 ya tienen `Operativo *`). Coordinar con el equipo comercial la forma de ese pipeline (etapas de delivery), o clonarlo de un `Operativo *` análogo.
4. **Atribución sin campaña activa:** los 3 no tienen pixel hoy. Se prepara el tracking data-driven (`05`) para cuando se activen campañas, sin forzarlo al pixel de Boarding.
5. **`Francia` NO es uno de estos** — es un **destino**, va como nota en el contacto, nunca como programa (`01`). No confundir con "Viajes educativos".

---

*Corroborado contra `ESTADO` Hallazgo 20 y el snapshot Clientify (Operativo Educación superior 12, Operativo Idiomas 22, sin Operativo Viajes educativos). 2026-08-26.*
