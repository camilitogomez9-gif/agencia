# 01 · Taxonomía de programas (la columna vertebral)

> **Por qué va primero.** El programa es el eje que consumen el schema del Contact (`02`), el diseño de pipelines (`03`), los custom fields/tags (`04`), la atribución CAPI (`05`), el ruteo del agente y los templates (`06`), los 8 calendarios (`07`) y todos los drips/rescates (`09`). Sin la taxonomía canónica cerrada, esos mappings quedan colgando. Casi todo está decidido por el cliente (2026-08-17); acá se fija y se remapea la data.

---

## 1. Los 8 programas canónicos

Nombres validados por Mauricio (2026-08-17, en español). Este es el **enum destino** de GHL para el campo de programa.

| # | Programa canónico (valor GHL) | Asesor | ¿Existe hoy? | Aclaración del cliente |
|---|---|---|---|---|
| 1 | **Internados** | Rodrigo | ✅ | "Boarding School" es el nombre comercial en inglés; el enum interno unifica a *Internados* |
| 2 | **Intercambio académico con familias** | Rodrigo | ✅ | Antes "AA Familiar" / "Año Académico" |
| 3 | **Viajes educativos** | Andrés | ❌ huérfano | 0 hits en el sistema — se construye de cero (`10`) |
| 4 | **Educación superior** | Andrés | ❌ huérfano | 0 hits — se construye de cero (`10`) |
| 5 | **Campamentos de verano** | Rodrigo | ✅ | Antes "Summer Camp" |
| 6 | **Cursos de idiomas en el extranjero** | Andrés | ❌ huérfano | Solo 1 link suelto en el prompt — se construye de cero (`10`) |
| 7 | **Pathway Alemania** | Andrés | ✅ | *"lo usamos exclusivamente para Alemania. No es genérico."* |
| 8 | **Gap Year / Estudia y Trabaja** | Andrés (era Diego) | ✅ | *"son EL MISMO PROGRAMA con dos nombres."* VET 6-8 meses + permiso de trabajo |

**Diego sale del ruteo automático** por completo (trabaja leads orgánicos/fríos propios). Su path roto en `wf-confirmacion-agenda` se **borra** (§descartes de `00`).

---

## 2. Reglas de normalización (qué se colapsa y qué se saca del enum)

1. **Boarding School → Internados.** Doble grafía viva en los datos: `Boarding School` (482 leads, lo escribe el outreach hardcodeado) + `Boarding IA` (437, lo escribe el LLM del dispatcher). **No es legado — ambas se escriben hoy.** El Rescate se salvaba por `contains "Boarding"`; en GHL, exact-match las trataría como 2 programas → **unificar ambas a `Internados`**.
2. **Francia → NO es programa, es destino.** Sale del enum. *"Es un DESTINO que manejamos dentro de varios programas (intercambio, internados, idiomas, educación superior). No debe crearse como programa."* Los ~279+167 leads con fuente "Francia / P. México…" conservan Francia como **nota/comentario** en el contacto (ver `02`, campo `Destino de interés`), y su programa se determina por descubrimiento, no por el origen.
3. **Gap Year = Estudia y Trabaja = un solo programa (#8).** Cualquier etiqueta "estudiar y trabajar" / "estudio y trabajo" / "Gap Year" colapsa a #8. La 6ª rama de memoria del rescate ("Estudio y Trabajo") deja de ser código muerto separado: se fusiona.
4. **Pathway → Pathway Alemania.** El destino Alemania es intrínseco; no hay Pathway genérico.
5. **`Automatización - Comentarios` NO es un programa.** Es una fuente/lead-source (comment automation). 5 leads. → no va al enum de programa; se mapea como `Fuente lead` / tag (ver `04`).
6. **`No definido` / vacío → sin programa aún.** 1.315 leads. El agente lo descubre en conversación. En GHL el campo de programa queda vacío hasta que el descubrimiento lo setea. **Regla dura del cliente:** el agente **nunca asume el programa** por el origen, ni aunque sea evidente.

---

## 3. Crosswalk: valores actuales → canónico (para el remapeo de datos)

Toda representación del programa que aparece en algún sistema, mapeada al canónico. Los conteos salen de `leads.csv` (3.819 filas) salvo indicación.

| Valor actual | Dónde aparece | Conteo | → Canónico | Nota |
|---|---|---|---|---|
| `Boarding IA` | Airtable `Programa interés` (LLM) | 437 | **Internados** | unificar |
| `Boarding School` | Airtable `Programa interés` (outreach hardcode) | 482 | **Internados** | unificar |
| `BS` / `BSG` / `BSC` | CAPI (Programas), tag Clientify | — | **Internados** | 3 códigos, 1 pixel `228398216567258` |
| flow "Boarding School" | ManyChat | — | **Internados** | drip |
| `AA Familiar IA` | Airtable (LLM), nurturing tag | 632 | **Intercambio académico con familias** | |
| flow "Año Académico" | ManyChat | — | **Intercambio académico con familias** | |
| `HF` | CAPI (Programas) | — | **Intercambio académico con familias** | pixel `24520910174237152` |
| `Pathway IA` | Airtable, nurturing tag | 881 | **Pathway Alemania** | sin fila CAPI → tracking incierto (`05`) |
| flow "Pathway" | ManyChat | — | **Pathway Alemania** | |
| `Summer Camp IA` | Airtable, nurturing tag | 42 | **Campamentos de verano** | sin fila CAPI |
| flow "Summer Camp" | ManyChat | — | **Campamentos de verano** | |
| `Gap Year IA` | Airtable, nurturing tag | 25 | **Gap Year / Estudia y Trabaja** | sin fila CAPI |
| `Estudio y Trabajo` | memoria Rescate (6ª clave) | ~0 | **Gap Year / Estudia y Trabaja** | fusiona (era muerto separado) |
| flow "Gap year" | ManyChat | — | **Gap Year / Estudia y Trabaja** | |
| link `/Estudiar-y-Trabajar-en-Australia` (Diego) | prompt agente | — | **Gap Year / Estudia y Trabaja** | asesor pasa a Andrés |
| link `/EstudiaryTrabajar_Agendar` (Andrés) | prompt agente | — | **Gap Year / Estudia y Trabaja** ⚠️ | ver bandera #2 abajo |
| `Automatización - Comentarios` | Airtable `Programa interés` | 5 | **(no es programa)** | → Fuente lead / tag |
| `Francia IA` | enum Airtable (sin uso real) | 0 | **(no es programa)** | → destino/nota |
| `No definido` / vacío | Airtable | 1.315 | **(sin programa aún)** | el agente lo descubre |
| *(no existe)* | — | 0 | **Viajes educativos** ⭐ | huérfano, de cero (`10`) |
| *(no existe)* | — | 0 | **Educación superior** ⭐ | huérfano, de cero (`10`) |
| link suelto `cursos idiomas` | prompt agente | 0 | **Cursos de idiomas en el extranjero** ⭐ | huérfano, de cero (`10`) |

**Remapeo neto de la cohorte de 3.819 leads:** Internados 919 (437+482) · Pathway Alemania 881 · Intercambio académico 632 · Campamentos 42 · Gap Year 25 · sin programa 1.320 (1.315 "No definido" + 5 "Automatización") · huérfanos 0. → **La migración de datos reescribe `Programa interés` según esta tabla** antes de importar a GHL.

---

## 4. Tabla-madre programa → asesor → calendario → pixel (referencia para 05/06/07)

Backbone que los demás docs referencian. Los slugs de calendario se definen en `07`; los pixels en `05`.

| # | Programa | Asesor | Calendario GHL (`07`) | Link viejo (muere) | Pixel CAPI (`05`) |
|---|---|---|---|---|---|
| 1 | Internados | Rodrigo | `cal-internados` | `/agendar-ema` | `228398216567258` (BS/BSG/BSC) |
| 2 | Intercambio académico con familias | Rodrigo | `cal-intercambio` | `/AAFamilia-Agendar` | `24520910174237152` (HF) |
| 3 | Viajes educativos ⭐ | Andrés | `cal-viajes-educativos` | *no existía* | **falta** (crear) |
| 4 | Educación superior ⭐ | Andrés | `cal-educacion-superior` | *no existía* | **falta** (crear) |
| 5 | Campamentos de verano | Rodrigo | `cal-campamentos` | `/SummerCamp-Agendar` | **falta** (crear) |
| 6 | Cursos de idiomas ⭐ | Andrés | `cal-cursos-idiomas` | `/EstudiaryTrabajar_Agendar` (dudoso) | **falta** (crear) |
| 7 | Pathway Alemania | Andrés | `cal-pathway-alemania` | `/PW_Alemania_Agendar` | **falta** (crear) |
| 8 | Gap Year / Estudia y Trabaja | Andrés | `cal-gap-year` | `/Estudiar-y-Trabajar-en-Australia` | **falta** (crear) |

> **`agendar-ema` NO es un asesor.** Es el slug del calendario de Internados (Rodrigo) y además el **fallback** genérico del prompt. Hoy es un bug de negocio: los 3 huérfanos caen ahí → programa y asesor equivocados. En destino, el fallback deja de rutear a Internados (ver `06`/`10`).

---

## 5. Destinos (van como nota, nunca campo estructurado)

Regla del cliente: *"si un lead menciona un destino específico, se registra como comentario o nota en el contacto. No queremos que el destino sea un campo estructurado ni que se confunda con el programa."*

Destinos que aparecen hoy mezclados con programa/fuente (Francia, Australia, Alemania, P. México, etc.) → en GHL se guardan en un campo de texto libre `Destino de interés` en el Contact (`04`) o como nota, **no** en el enum de programa. Excepción intrínseca: Alemania (Pathway) y el permiso-de-trabajo del VET (Gap Year) son parte de la definición del programa, no destinos sueltos.

---

## 6. Banderas de esta taxonomía

1. **#6 Cursos de idiomas vs #8 Gap Year — tensión residual.** El cliente los declara **distintos** (ambos Andrés). Pero "estudiar y trabajar" aparece en dos links viejos: `/Estudiar-y-Trabajar-en-Australia` (era Diego, VET Australia) y `/EstudiaryTrabajar_Agendar` (Andrés, etiquetado "cursos idiomas" en el prompt). Por la regla del cliente ("estudia y trabaja = Gap Year"), **ambos links se interpretan como #8 Gap Year**, y **#6 Cursos de idiomas queda como huérfano genuino sin link previo** (inmersión lingüística ≠ VET). ✅ Confirmar con el cliente que `/EstudiaryTrabajar_Agendar` no era realmente inmersión de idiomas. Bajo impacto: 0 leads estructurados en ambos.
2. **Grafía canónica final.** El cliente nombró los 8 en español; acá se adopta el nombre español como valor de enum GHL. Si el equipo prefiere conservar los sufijos "IA" internos por continuidad de datos, es una decisión cosmética — el mapeo de cohorte no cambia.
3. **`Automatización - Comentarios`** (5 leads): no es programa; se preserva como `Fuente lead` = "Comment automation IG/FB" (capacidad nativa nueva de GHL, ver `06`).

---

*Corroborado contra `leads.csv`, `programas-capi.csv`, `manychat` snapshot y los 6 docs de `01_logica_actual/`. 2026-08-26.*
