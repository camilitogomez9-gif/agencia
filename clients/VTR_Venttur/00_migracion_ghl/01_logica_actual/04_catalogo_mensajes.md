# 04 — Catálogo de Mensajes

> **Reescrito 2026-07-24** con los inputs completos de Etapa 0 (14 workflows n8n + snapshot de datos de las 5 plataformas + 6 CSVs Airtable + system prompt del agente + schema Supabase). Supera la versión de mayo 2026, que se generó con inputs parciales y contenía errores materiales (ver más abajo / doc 06).
>
> **Fuentes primarias usadas:**
> - `06_docs/template-texts-canonical.md` (rescate 15 textos + outreach 3 + plantilla memoria sintética; verificados contra screenshots del Flow editor de ManyChat el 2026-07-20).
> - `00_migracion_ghl/00_inputs/manychat-flows-content-2026-07-20.md` (contenido interno de 12 flows ManyChat: nurturing 4-toques, Agenda, Seguimiento agenda, Elevar, Recibir/Enviar mensajes, debounce).
> - `04_agents/agente-venttur-system-prompt-EXTRAIDO-2026-07-24.md` (system prompt del agente "Mauricio", 39K chars, extraído literal del nodo `Agente IA WPP`).
> - Análisis nodo-por-nodo de los 14 workflows JSON (`wf-*.json`) — flow_ns, tag_ids, field_ids, credenciales, disparadores.
> - `00_inputs/airtable-csvs/leads.csv` (schema real de Leads, 30 columnas) + `manychat-snapshot-2026-05-13.md`.

### Correcciones vs. versión mayo 2026

Este doc de mayo estaba particularmente incompleto (marcaba la categoría C "ManyChat operativos" como *"⚠️ SIN EXPORT DISPONIBLE"*). Los cambios materiales:

1. **El sistema NO es "puramente reactivo".** El corazón es un **AI Agent conversacional ("Mauricio")** que genera mensajes con LLM (gpt-4o) — no plantillas fijas. Mayo ni lo mencionaba. Se agrega la categoría G.
2. **Rescate Post-Link SÍ está en producción** (workflow n8n `mkEP1qFN7MVb9qP0`), no "no activado". Además siembra **memoria sintética** en Postgres. Se corrigen las categorías A/B.
3. **Outreach proactivo tri-toque SÍ está en producción** (`CUuFxbst3iHpgeXS`), con textos verbatim capturados. Se agrega la categoría C.
4. **Existe un nurturing de 4 toques por programa** (6 flows ManyChat) que mayo desconocía por completo. Se agrega la categoría D.
5. **El mensaje de Agenda contiene el número directo de Rodrigo** (+52 1 33 1944 2476) — dato de negocio nuevo. Se agrega la categoría E.
6. **La notificación Telegram del Formulario Clientify (D.1 de mayo) NO existe** en el JSON de ese workflow — era una suposición. Las notificaciones Telegram reales viven en Rescate Post-Link y Confirmación de agenda. Se corrige la categoría H.
7. Los links de agendamiento y sus expertos ahora salen del system prompt real (matriz completa), con una ambigüedad detectada entre "Gap Year" y "Estudiar y trabajar".

---

## 🆕 Validación con el cliente — 2026-08-17 (Etapa 2)

> Respuestas de **Mauricio García** (revisadas sobre el borrador de Max) al cuestionario
> `02_validacion_cliente/cuestionario-venttur-2026-07-24.md`. Lo de acá abajo **supera** al cuerpo de
> este documento donde haya conflicto. Mapeo completo a las preguntas internas en
> `02_validacion_cliente/preguntas-cierre-2026-07-24.md` (A1..A11). Lo que quedó abierto está en
> `02_validacion_cliente/puntos-abiertos-ronda-2-2026-08-18.md`.
>
> **Fecha objetivo de cutover confirmada: 15 de septiembre de 2026.**

### Lo que cambia en el catálogo de mensajes

**1. La matriz de links y expertos se reemplaza entera.** La tabla de §"Links de agendamiento por
programa" queda **obsoleta**: los enlaces actuales viven en Clientify y mueren con la migración.

| # | Programa | Asesor nuevo | Qué pasa con el link viejo |
|---|---|---|---|
| 1 | Internados | Rodrigo | `agendar-ema` → calendario GHL |
| 2 | Intercambio académico con familias | Rodrigo | `AAFamilia-Agendar` → calendario GHL |
| 3 | Viajes educativos | Andrés | **no existía** |
| 4 | Educación superior | Andrés | **no existía** |
| 5 | Campamentos de verano | Rodrigo | `SummerCamp-Agendar` → calendario GHL |
| 6 | Cursos de idiomas | Andrés | `EstudiaryTrabajar_Agendar` → calendario GHL |
| 7 | Pathway Alemania | Andrés | `PW_Alemania_Agendar` → calendario GHL |
| 8 | Gap Year / Estudia y Trabaja | **Andrés** (era Diego) | `Estudiar-y-Trabajar-en-Australia` → calendario GHL |

- **La ambigüedad marcada `⚠️ INCIERTO` en esta sección queda RESUELTA**, y no como se suponía. No
  era "Gap Year Australia con Diego vs. cursos de idiomas con Andrés": **Diego sale del ruteo
  automático por completo** y los dos programas son de **Andrés**. Siguen siendo dos programas
  distintos (#6 cursos de idiomas ≠ #8 cursos vocacionales VET), con dos calendarios.
- **El fallback `agendar-ema` es hoy un bug de negocio.** Con 3 programas sin link, un lead que
  pregunta por Educación superior cae al fallback, que es el link de **Internados con Rodrigo**:
  programa equivocado y asesor equivocado.

**2. A.5 / B.5 "Estudio y Trabajo" — el código muerto se resuelve FUSIONANDO, no agregando.**
Los textos A.5 y B.5 existen en el diccionario pero nunca se envían porque el `Code: Fase 1` mapea
solo 5 destinos. La corrección **no** es agregarle la sexta rama: "Estudio y Trabajo" y "Gap Year" son
**el mismo programa** (cursos vocacionales VET de 6 a 8 meses con permiso de trabajo). Las dos ramas
colapsan en una sola y **A.5 / B.5 se dan de baja**.

**3. Faltan mensajes para 3 programas.** Viajes educativos, Educación superior y Cursos de idiomas no
tienen drip de nurturing, ni texto de rescate, ni texto de outreach. Decisión de alcance pendiente
(ronda 2, punto 7): tratamiento completo o solo calendario y asesor correctos para el 15/9.

**4. 🆕 Categoría de mensajes que este catálogo no cubre: los recordatorios de cita.**
Existen y se envían hoy, **desde Clientify y desde un segundo número de WhatsApp**. Por eso no están
inventariados acá. El cliente va a compartir config y textos para replicarlos en GHL. Falta definir
cuántas horas antes salen.

**5. Confirmación de cita: contenido pendiente.** Confirmado que la reciben todos sin importar el
asesor; el texto lo aporta el cliente desde Clientify.

**6. 🔴 Precios: el guion nuevo está listo pero NO se activa.** El cambio de "el bot no dice cifras" a
"el bot da rango y cierra con fecha concreta" está preparado, pero es una decisión comercial y los
rangos **no están confirmados**. Además solo cubren 5 de los 8 programas, y hay un conflicto sin
resolver en Internados (USD 50-100k según el reporte vs. 50-130k según el prompt vivo). Ronda 2,
punto 1.

**7. El número +52 1 33 1944 2476 (Rodrigo) SIGUE VIGENTE** y es el que se comparte al agendar.
Confirmado. Ningún asesor tiene número propio: es uno solo compartido.

---

### ⚠️ Nota sobre la versión que el cliente respondió

El cuestionario que Mauricio contestó es la **versión de 12 preguntas enviada el 2026-08-07**. El
archivo del repo se amplió a **14 preguntas el 2026-08-17** (tras el Reporte la agencia 1), agregando
*rangos de precio* y *qué significa "Cerrada"*, y reescribiendo las de seguimiento y confirmación de
cita. **Esas cuatro modificaciones nunca le llegaron al cliente.** Por eso hay respuestas que
contestan la redacción vieja, y dos temas que quedaron sin preguntar. Se resuelven en
`puntos-abiertos-ronda-2-2026-08-18.md`.


## Resumen por categoría

| Cat. | Categoría | Cantidad | Estado | Canal | Variable / origen del texto |
|------|-----------|----------|--------|-------|------------------------------|
| A | Rescate Post-Link Fase 1 (por programa) | 6 + fallback | **LIVE** (n8n `mkEP1qFN7MVb9qP0`) | WhatsApp (ManyChat) | `{{first_name}}` · texto fijo en Code node |
| B | Rescate Post-Link Fase 2 (por programa) | 6 + fallback | **LIVE** | WhatsApp (ManyChat) | `{{first_name}}` · texto fijo en Code node |
| C | Outreach Form Meta Touch 1/2/3 | 3 | **LIVE** (n8n `CUuFxbst3iHpgeXS`) | WhatsApp (Template MARKETING) | `{{first_name}}` · template Meta `boarding_form_followup` |
| D | Nurturing 4-toques por programa | 6 flows × 4 = 24 | **LIVE** (dispatcher n8n `DyrDumQgb6S4zHsS` + flows ManyChat) | WhatsApp (ManyChat) | `[First Name]` · texto fijo en flow ManyChat |
| E | Agenda + Seguimiento agenda | 2 | **LIVE** | WhatsApp (ManyChat) | `[First Name]` + nº directo Rodrigo |
| F | Mensaje `system` de memoria sintética | 1 plantilla | **LIVE** (rescate + outreach) | Postgres `n8n_chat_histories` (no va al lead) | prosa dinámica desde campos Airtable |
| G | Mensajes del agente "Mauricio" | N (generados por LLM) | **LIVE** (core del sistema) | WhatsApp (ManyChat) | gpt-4o · guías de estilo, no literales |
| H | Notificaciones operativas (Telegram) | 3 tipos | **LIVE** (parcial) | Telegram | texto fijo |
| **Total plantillas fijas** | | **~44** (+ N agénticos) | | | |

> **Nota de conteo:** los textos de A, B, C, D, E, F son **plantillas fijas** (inventariables verbatim). Los de G los genera el LLM en runtime y no son inventariables — se documentan sus guías de estilo canónicas.

> 🔴 **FALTAN EN ESTE CATÁLOGO — plantillas Meta que no viven en ningún archivo del repo.**
> El Reporte la agencia 1 (agosto 2026) nombra cuatro plantillas por las que se fueron **los 34 fallos de
> entrega**, y tres de ellas **no aparecen en ningún lado de este repositorio**:
>
> | Plantilla | Fallos | Dónde vive |
> |---|---|---|
> | `seg_dia_5_bs` | 14 | ManyChat / Meta — **no está en el repo** |
> | `boarding_form_followup_touch3` | 11 | outreach n8n (Touch 3) — sí documentada (Cat. C) |
> | `seg_dia_3_bs` | 5 | ManyChat / Meta — **no está en el repo** |
> | `seg_dia_7_bs` | 4 | ManyChat / Meta — **no está en el repo** |
>
> `grep -r "seg_dia"` sobre todo el workspace devuelve **cero resultados**. Antes de migrar hay que
> exportarlas desde Meta Business Manager: son plantillas aprobadas cuyo texto no está versionado en
> ninguna parte. Las `_bs` corresponden a la cohorte **Boarding School**, que es justamente la que el
> dispatcher clasificaba mal (ver `01_mapa_funcional.md` §8.1).
>
> **También falta el mensaje de confirmación de cita**, que hoy no existe: el workflow que debería
> mandarlo muere antes del envío (Hallazgo 1). Se incorpora como categoría nueva al implementarlo.

---

## Categoría A — Rescate Post-Link, Fase 1 (45 min)

**Estado:** LIVE. Workflow n8n `wf-rescate-post-link` (`mkEP1qFN7MVb9qP0`), invocado por `Actualizar 'Link enviado'` (`gRSMjzxggA4UePjz`) cuando el agente envía un link `promo.venttur.com/`.
**Disparador:** `Wait: 45 min` post-envío del link → `Airtable: 1er check` → solo si `Agendan cita = false`.
**Tono:** concierge / reducción de fricción ("¿tuviste problemas con la plataforma o los horarios?").
**Variable:** `{{first_name}}` → reemplazado por el `Nombre` (primer nombre) del lead; si vacío → `"hola"`.
**Canal / ventana:** mensaje **regular** de ManyChat (no template Meta). El lead ya escribió al negocio → ventana de 24 h abierta. A 45 min casi siempre entra bien.
**Entrega técnica:** `Set Custom Fields: Fase 1` (field_id `13337279` = parte 1; `13337280`/`13337281` = null) → `sendFlow` flow_ns `content20250617172539_850988` (flow "Enviar mensajes" de ManyChat).

> ⚠️ INCIERTO — routing real de los Code nodes de envío (impacto: alto para el catálogo de leads efectivamente contactados). El `Code: Fase 1` del workflow mapea SOLO 5 destinos vía `programa.includes()`: `Boarding`, `AA Familiar`||`Francia`, `Summer Camp`, `Pathway`, `Gap Year`. **"Estudio y Trabajo" NO tiene rama en el Code de envío** → un lead con `Programa interés = "Estudio y Trabajo"` cae en `matched=false`, recibe el tag `RESCATE_PROGRAMA_NO_MAPEADO` (tag_id `87501935`) y **nunca recibe el mensaje A.5 ni B.5**, aunque el texto exista en el diccionario. El texto A.5 abajo está documentado como plantilla pero es **código muerto en el path de envío**.

### A.1 — Boarding School
- **Match Airtable:** `Programa interés` contains `"Boarding"`
- **Link:** `promo.venttur.com/agendar-ema` · **Experto:** Rodrigo

> Hola {{first_name}}. Noté que solicitaste el enlace para platicar sobre Boarding School, pero el registro quedó pendiente. Si no encontraste un horario que se ajuste a tu agenda, avísame y reviso disponibilidad manual. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/agendar-ema

### A.2 — Año Académico con Familia (AA Familiar)
- **Match:** `Programa interés` contains `"AA Familiar"` (también captura `"Francia"` por el `||` del Code)
- **Link:** `promo.venttur.com/AAFamilia-Agendar` · **Experto:** Rodrigo

> Hola {{first_name}}. Vi que pediste el enlace para la asesoría de Año Académico, pero la cita quedó en pausa. Si tuviste problemas con la plataforma o los horarios no te cuadran, escríbeme y lo resolvemos. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/AAFamilia-Agendar

### A.3 — Summer Camp
- **Match:** `Programa interés` contains `"Summer Camp"`
- **Link:** `promo.venttur.com/SummerCamp-Agendar` · **Experto:** Rodrigo

> Hola {{first_name}}. Solicitaste el acceso a la agenda para Summer Camp hace un momento. Si el calendario no te mostró horarios convenientes, dímelo y buscamos un espacio que te funcione. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/SummerCamp-Agendar

### A.4 — Pathway (Alemania)
- **Match:** `Programa interés` contains `"Pathway"`
- **Link:** `promo.venttur.com/PW_Alemania_Agendar` · **Experto:** Andrés

> Hola {{first_name}}. Noté que pediste el enlace para la sesión de Pathway en Alemania. Si la plataforma te dio error o no encontraste disponibilidad, avísame por aquí para coordinarlo directo. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/PW_Alemania_Agendar

### A.5 — Estudio y Trabajo (Cursos de Idiomas) — ⚠️ texto existe pero NO se envía (ver aviso arriba)
- **Match:** `Programa interés` contains `"Estudio y Trabajo"` → **sin rama en el Code de envío**
- **Link:** `promo.venttur.com/EstudiaryTrabajar_Agendar` · **Experto:** Andrés (según system prompt)

> Hola {{first_name}}. Vi que solicitaste el calendario para Estudio y Trabajo. Si tuviste algún inconveniente técnico al intentar agendar o no te acomodan las horas, dime y lo reviso. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/EstudiaryTrabajar_Agendar

### A.6 — Gap Year en Australia
- **Match:** `Programa interés` contains `"Gap Year"`
- **Link:** `promo.venttur.com/Estudiar-y-Trabajar-en-Australia` · **Experto:** Diego

> Hola {{first_name}}. Solicitaste el enlace de asesoría para tu Gap Year en Australia. Si no encontraste un hueco en la agenda o se cerró el enlace, escríbeme y te ayudo a reservarlo. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/Estudiar-y-Trabajar-en-Australia

### A.fallback — Genérico (programa no matcheado)
> Nota: este fallback está documentado en `template-texts-canonical.md`, pero en el path de ENVÍO real un programa no mapeado dispara el tag `RESCATE_PROGRAMA_NO_MAPEADO` y NO manda mensaje. El fallback aplica a la **memoria sintética** (Categoría F), no al mensaje al lead. Ver §F.

> Hola {{first_name}}. Vi que solicitaste el enlace de asesoría pero el registro quedó pendiente. Si tuviste algún inconveniente con la plataforma o los horarios, escríbeme y lo resolvemos. Reserva tu espacio aquí cuando puedas.

---

## Categoría B — Rescate Post-Link, Fase 2 (~24 h)

**Estado:** LIVE. Mismo workflow, tras `Wait: 24 hrs` → `Airtable: 2do check` → solo si `Agendan cita = false`.
**Tono:** storytelling / atacar la objeción específica del programa (miedo, cupos, requisitos).
**Variable:** `{{first_name}}`. **Entrega:** mismo `sendFlow content20250617172539_850988`. Tras Fase 2, si sigue sin agendar → tag `LINK_ABANDONADO_FRIO` (tag_id `87501917`).
**Ventana WhatsApp:** ~24 h 45 m post-link. Si el lead no respondió a Fase 1, la ventana de 24 h puede estar cerrada y el mensaje regular no se entrega. Aceptable para v1; monitorear delivery rate.

> ⚠️ El mismo gap de "Estudio y Trabajo" aplica: solo se llega a Fase 2 si Fase 1 matcheó (mismo routing de 5 destinos). B.5 abajo es plantilla, no envío real.

### B.1 — Boarding School (`promo.venttur.com/agendar-ema`)
> Hola {{first_name}} 👋. Noté que tu registro quedó en pausa ayer. Mandar a un hijo a un internado es un gran paso y es súper normal dudar si 'ya está listo'. En la sesión validamos su perfil y vemos los pocos cupos que quedan para la temporada. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/agendar-ema

### B.2 — AA Familia (`promo.venttur.com/AAFamilia-Agendar`)
> Hola {{first_name}} 👋. Seguro entre tantas cosas ayer se te pasó agendar. La mayor preocupación de los papás siempre es: '¿Se adaptará bien si no domina el idioma?'. En la llamada armamos un plan de inmersión seguro para evitar frustraciones. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/AAFamilia-Agendar

### B.3 — Summer Camp (`promo.venttur.com/SummerCamp-Agendar`)
> Hola {{first_name}} 👋. Vi que tu registro quedó a medias ayer. Es súper común dudar si un Summer Camp será seguro y realmente formativo, o solo un paseo. En 45 min aterrizamos la opción ideal antes de que cierren los grupos de temporada. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/SummerCamp-Agendar

### B.4 — Pathway (`promo.venttur.com/PW_Alemania_Agendar`)
> Hola {{first_name}} 👋. Noté que pausaste el registro ayer. Muchos creen que necesitan alemán perfecto para empezar, pero el secreto es armar la ruta ya mismo para no perder la admisión en las universidades públicas. En 45 min les damos el mapa completo. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/PW_Alemania_Agendar

### B.5 — Estudio y Trabajo (`promo.venttur.com/EstudiaryTrabajar_Agendar`) — ⚠️ no se envía
> Hola {{first_name}} 👋. Seguro el día a día te ganó y se te pasó agendar. ¿Dudas si vale la pena irse teniendo nivel básico? Justo la inmersión total hace que se pierda el miedo en semanas. En la sesión aterrizamos el destino ideal según fechas de inicio. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/EstudiaryTrabajar_Agendar

### B.6 — Gap Year en Australia (`promo.venttur.com/Estudiar-y-Trabajar-en-Australia`)
> Hola {{first_name}} 👋. Vi que dejaste el registro a medias. Irse a Australia es un gran paso y la mayor duda siempre es: '¿Encontrará trabajo rápido?'. El secreto está en irse con una ruta clara y no improvisar. Nos quedan pocos espacios esta semana. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/Estudiar-y-Trabajar-en-Australia

---

## Categoría C — Outreach Form Meta (Touch 1 / 2 / 3)

**Estado:** LIVE. Workflow n8n `outreach-form-meta-venttur` (`CUuFxbst3iHpgeXS`). Disparado por Google Sheets Trigger (sync de Meta Lead Ads) → Cron cada ~5 min lee leads pendientes → Switch por `Toques enviados`.
**Cadencia REAL (confirmada en `filterByFormula` + Normalize):** los 3 toques se anclan todos a `Touch 1 programado at` = **timestamp de creación del lead** (SIN +1h en la versión v4). → Touch 1 en el próximo ciclo del cron (≈0 h), Touch 2 a +24 h, Touch 3 a +72 h desde la creación.
**Canal / ventana:** son **Templates de WhatsApp categoría MARKETING** (fuera de ventana de 24 h — el lead nunca escribió primero, vino de un form). Requieren opt-in explícito; por eso `createSubscriber` envía `consent_phrase` citando el formulario.
**Template Meta:** `boarding_form_followup`, idioma `es_MX`, categoría MARKETING (aprobado 2026-06-13; Touch 2/3 aprobados 2026-06-16).
**Variable:** `{{first_name}}`.
**Textos:** ✅ VERIFICADOS palabra por palabra contra el Flow editor de ManyChat (screenshots 2026-07-20).

### C.1 — Touch 1 (≈0 h desde creación)
- **flow_ns ManyChat:** `content20260612151152_969589`
- **Disparador:** rama 0 del Switch (`Toques enviados < 1`)

```
Hola {{first_name}}, gracias por tu interés en nuestros programas de Boarding School.

Vimos que recientemente solicitaste información sobre opciones de estudio en el extranjero.

Me gustaría conocer un poco más sobre tu interés para poder orientarte mejor. ¿El programa sería para tu hijo(a) o para algún familiar?
```

### C.2 — Touch 2 (+24 h)
- **flow_ns ManyChat:** `content20260616231914_193459`
- **Disparador:** rama 1 del Switch (`Toques enviados = 1`)

```
Hola {{first_name}},

Muchos padres nos contactan porque quieren brindarles a sus hijos una experiencia internacional que los ayude a desarrollar independencia, confianza y una visión global para su futuro.

Cada estudiante tiene objetivos distintos, por eso nos gustaría entender mejor tu caso para orientarte adecuadamente.

¿Para qué edad o grado escolar estás buscando opciones?
```

### C.3 — Touch 3 (+72 h)
- **flow_ns ManyChat:** `content20260616231947_185709`
- **Disparador:** rama 2 del Switch (`Toques enviados = 2`)

```
Hola {{first_name}},

Sabemos que elegir una experiencia educativa internacional es una decisión importante y que normalmente surgen muchas preguntas sobre destinos, seguridad, costos, requisitos y beneficios para el futuro del estudiante.

Nuestro objetivo es ayudarte a encontrar la mejor opción según las metas y necesidades de tu familia.

Si aún estás explorando alternativas, responde este mensaje y con gusto te orientaremos sin compromiso.
```

> **Nota:** los 3 templates hablan de "Boarding School" en el saludo (el form Meta era el de Boarding Schools). No se ramifican por programa — es un outreach único para todos los leads de Form Meta, que hoy son 100% de la campaña Boarding. Si se abren otras campañas, el copy quedaría desalineado.

---

## Categoría D — Nurturing de 4 toques por programa (drip largo)

**Estado:** LIVE. Es la secuencia de seguimiento educativo de largo plazo para leads que conversaron pero NO recibieron link de asesoría.
**Dispatcher:** workflow n8n `Resumen, etiquetas, seguimientos` (`DyrDumQgb6S4zHsS`), invocado por el main 8 h después de la conversación. Un LLM (gpt-4o-mini) clasifica la conversación en `tags` (programas), y un Switch dispara **UN** `sendFlow` de ManyChat.
**Gate clave (anti-doble-contacto):** el drip SOLO se dispara si el LLM determina `asesoria == 'cero'` (el lead NO recibió link). Si ya recibió link, no entra a este nurturing (para eso está el Rescate, Categoría A/B).
**Estructura de cada flow ManyChat (idéntica en los 6):** `Add Tag` → mensaje 1 → `Wait 1 Day` → mensaje 2 → `Wait 2 Days` → mensaje 3 → `Wait 2 Days` → mensaje 4. → **Delays 0 / +1 d / +3 d / +5 d.**
**Variable:** `[First Name]` (convención ManyChat con corchetes).
**Canal:** mensajes regulares de ManyChat.

> ⚠️ INCIERTO — prioridad del Switch (impacto: medio). El `Switch` del dispatcher NO usa `allMatchingOutputs`, así que un lead con varios `tags` recibe SOLO el drip del **primer match** en este orden: Pathway > Summer Camp > AA Familiar > Boarding > Gap Year. El orden parece arbitrario/accidental, no una prioridad de negocio deliberada.

**flow_ns por programa (creados 2025-07-18):**

| Programa (tag LLM) | Flow ManyChat | flow_ns |
|---|---|---|
| Boarding IA | Boarding School | `content20250718115245_638127` |
| Pathway IA | Pathway | `content20250718121921_967738` |
| Gap Year IA | Gap year | `content20250718122822_491460` |
| AA Familiar IA | Año Académico | `content20250718123255_243860` |
| Summer Camp IA | Summer Camp | `content20250718123847_652764` |
| (sin tag) Lead General | Seguimiento Lead General | `content20250718124216_992343` |

### D.1 — Boarding School (4 toques)

**Toque 1 (día 0):**
> Te comparto algo que puede servirte. Hola [First Name], no estoy seguro si este sea un buen momento para ti, pero quería dejarte esto por si te ayuda. Muchos papás se detienen porque sienten que no tienen toda la información o no saben por dónde empezar. Te comparto tres errores más comunes al elegir escuela en el extranjero: 1. Elegir por el país, no por el perfil del estudiante. 2. Guiarse solo por presupuesto sin entender qué implica. 3. No considerar si la edad y madurez son compatibles con el programa. Espero que estos errores te brinden más claridad. Ojalá te sirva, saludos y un fuerte abrazo.

**Toque 2 (día 1):**
> La pregunta que cambia todo. ¿Cómo es tu hijo cuando lo ve? Esta pregunta cambia completamente el tipo de recomendación. Muchas veces se elige por destino o por precio, pero si no se parte del perfil del estudiante, es muy fácil equivocarse. Si te interesa, con gusto te ayudo a pensar desde ahí.

**Toque 3 (día 3):**
> Esto lo usamos mucho con las familias que al principio no sabían qué recomendar. Aunque no hayas decidido todavía: ¿Está tu hijo listo para estudiar fuera? ✅ Tiene cierta autonomía en casa ✅ Sabe manejar frustraciones sin papás cerca ✅ Tiene una razón clara (más allá de 'me gusta viajar') ✅ Ustedes como papás tienen expectativas claras. No es un test. Solo algo que puede ayudar a pensar si es el momento correcto. Si te sirve, me da gusto. Y si en algún momento quieres retomarlo, aquí estoy.

**Toque 4 (día 5):**
> No te quiero saturar, lo prometo. Solo quería dejarte este último. Si en algún punto quieres que hablemos de esto, aquí ando. Espero que encuentres pronto lo que están buscando. Aquí no vendemos algo, ayudamos a tomar buenas decisiones. Cuando sientas que es el momento, aquí estoy.

### D.2 — Año Académico (AA Familiar) (4 toques)

**Toque 1 (día 0):**
> No es solo el país, es tu casa. Hola [First Name], no estoy seguro si todavía estás considerando esta opción, pero te quiero dejar una reflexión importante. Muchos papás eligen el país o el colegio... pero se olvidan de algo esencial: 🏠 Tu hijo no va a vivir en una escuela, va a vivir en una familia anfitriona. El impacto que tiene la familia anfitriona en la experiencia es enorme. Si quieres, te puedo explicar cómo funciona este punto en cada país y por qué hace la diferencia.

**Toque 2 (día 1):**
> ¿Cómo saber si tu hijo está listo? Una de las dudas más grandes que tienen los papás es: ¿Mi hijo realmente está preparado para vivir un año fuera, sin ustedes ahí? Te comparto algunas indicaciones que usamos para acompañar a las familias en esta decisión: ✅ Tiene cierto nivel de autonomía y se adapta bien a nuevos entornos ✅ Muestra apertura a otras culturas y estilos de vida ✅ Tiene curiosidad por mejorar su idioma ✅ Papás e hijo comparten expectativas realistas del programa.

**Toque 3 (día 3):**
> ¿Dónde hay programas y cómo se elige uno bien? Te comparto los países donde actualmente manejamos programas: 🇺🇸 Estados Unidos 🇨🇦 Canadá 🇫🇷 Francia 🇮🇹 Italia 🇳🇱 Países Bajos. Todos tienen diferencias importantes en cuanto a costos, requisitos, estructura y selección de familias. Si tienes en mente alguno o cuál te acomoda mejor según lo que buscan, puedo ayudarte a saber si es el más adecuado.

**Toque 4 (día 5):** ⚠️ INCIERTO — texto exacto NO capturado en screenshot (impacto: bajo, es un cierre corto). Lo visible del cierre es aproximadamente:
> ¿Tu hijo ya te dijo a cuál país le gustaría irse?

### D.3 — Gap Year (4 toques)

**Toque 1 (día 0):**
> Gap Year no es escapista. Hola [First Name], no sé si todavía estás explorando esta opción, pero quería invitarte a considerar. Una de las diferencias más importantes que nadie explica bien es esta: 🎯 Un Gap Year no es una 'pausa' ni una 'escapadista'. Bien diseñado, es una herramienta para ganar claridad, madurez y dirección. Lo ideal es que no sea improvisado. Si te interesa, puedo ayudarte a definir cuál es el enfoque más adecuado para ti.

**Toque 2 (día 1):**
> Te comparto esta reflexión. Muchas veces se piensa que el Gap Year es solo para 'descansar' antes de la universidad. Pero si se planea bien, ayuda a construir un mejor perfil académico y laboral después.

**Toque 3 (día 3):**
> ¿Qué países permiten estudiar y trabajar legalmente? Una de las preguntas más comunes es: ¿Dónde se puede estudiar y trabajar legalmente al mismo tiempo? Te comparto un resumen rápido: 🇦🇺 Australia — con cursos de idiomas o vocacionales 🇮🇪 Irlanda — con cursos de más de 25 semanas 🇨🇦 Canadá — en programas académicos específicos 🇲🇹 Malta 🇦🇪 Dubái — con ciertas condiciones. Y muchos más... Cada país tiene sus reglas, y elegir mal significa no poder trabajar legalmente. Si quieres, te explico cuál se adapta según tu perfil.

**Toque 4 (día 5):**
> Lo importante no es irte, es saber por qué.

### D.4 — Pathway (Alemania) (4 toques)

**Toque 1 (día 0):**
> Una pregunta que muchos no se atreven a hacer. Hola [First Name], te dejo algo que tal vez ya te has preguntado o has estado pensando o comparando opciones. Una de las preguntas más comunes (pero que casi nadie hace) es: ¿Es verdad que puedo estudiar en Alemania pagando menos que en México? La respuesta es sí, pero depende mucho de cómo te prepares. El Pathway es el paso previo para acceder a universidades públicas alemanas sin costo de colegiatura. Muchas veces hace toda la diferencia. Si quieres, te puedo ayudar a entender cuál aplica para ti y cuál es el camino correcto.

**Toque 2 (día 1):**
> Lo que me hubiera gustado saber antes. Muchos estudiantes que nos escriben creen que van a llegar el día en el país listos, pero les faltan requisitos formales y académicos, y por eso nadie les dice que necesitan cumplirlos, y pierden tiempo valioso o incluso llegan tarde para inscribirse en algún lugar. Si me cuentas un poco más de tu perfil, puedo decirte si estás en el camino correcto... o si hay algo que debes ajustar antes de avanzar.

**Toque 3 (día 3):**
> Te comparto este checklist rápido de cómo funciona el Pathway (2 años): ✅ ¿Llevas o estás por terminar la prepa o una carrera universitaria? ✅ ¿Te gustaría estudiar una carrera desde principio o aprender alemán desde cero? ✅ ¿Estás dispuesto a aprender alemán desde cero o reforzarlo? ✅ ¿Tienes experiencia viviendo fuera a largo plazo? Si respondiste que sí a 2 o más, ya te puedo recomendar opciones más adecuadas.

**Toque 4 (día 5):**
> Lo importante no es tener prisa, es tomar la mejor decisión.

### D.5 — Summer Camp (4 toques)

**Toque 1 (día 0):**
> ¿Campamento o vacaciones? Hola [First Name], te escribo porque veo algo seguido: los papás están considerando un campamento de verano y dudan entre esto. ⚡ A veces se piensa que es unas 'vacaciones fuera', pero la realidad es que bien elegido, puede ser una experiencia que le dé a tu hijo mucha más seguridad, independencia y visión del mundo. Si quieres, te puedo explicar qué hace que un campamento sea de valor real, y qué países tienen las mejores opciones en este momento.

**Toque 2 (día 1):**
> 3 preguntas que pueden ayudarte a decidir. Te comparto 3 preguntas que suelen ayudar a los papás a decidir si un summer camp les hace sentido: 1. ¿Tu hijo se adapta fácilmente a entornos nuevos y sin ti cerca? 2. ¿Ha tenido experiencias antes similares (campamentos, viajes, convivencia)? 3. ¿Este viaje es un primer paso hacia algo más (como estudiar fuera) o solo para disfrutar el verano? No hay respuestas correctas. Pero saber esto te ayuda a elegir mejor.

**Toque 3 (día 3):**
> Qué países manejamos (y por qué). Te comparto los destinos donde actualmente manejamos campamentos, con los mejores mixtos de seguridad y contenido formativo: Estados Unidos, Reino Unido, Canadá, Francia, Alemania. Y muchos más... Todos tienen enfoques diferentes, algunos más académicos, otros más culturales o deportivos. Si tienes algún país en mente, puedo ayudarte a identificar si es una buena opción para el verano.

**Toque 4 (día 5):** ⚠️ INCIERTO — texto NO capturado en el screenshot (impacto: bajo). La cadena en el flow tiene 4 mensajes (misma estructura que los demás), pero el 4º no quedó registrado. **Recuperar del Flow editor de ManyChat antes de migrar.**

### D.6 — Lead General (fallback, sin programa identificado) (4 toques)

Se dispara cuando el LLM no detectó ningún programa (`tags` vacío) Y el lead no recibió link.

**Toque 1 (día 0):**
> ¿En qué etapa estás? Hola, espero que estés muy bien. Vi que nos escribiste hace poco, pero no sé si aún tienes claro cuál es tu siguiente paso o apenas estás explorando opciones. Solo por si te sirve: entiendo mejor a las familias y estudiantes para encontrar el mejor programa para estudiar fuera, dependiendo de su perfil, intereses y objetivos. Cuando quieras, podemos platicarlo sin compromiso. Aquí ando.

**Toque 2 (día 1):**
> ¿Prefieres que te oriente? A veces lo más difícil no es encontrar programas, sino saber por dónde empezar. Si quieres, puedo orientarte con algunas preguntas rápidas para saber qué tipo de opciones te harían más sentido, sin compromiso. Me puedes decir si prefieres que te guíe paso a paso.

**Toque 3 (día 3):**
> Las rutas más comunes. Te comparto algo que sirve a muchas familias que apenas están explorando: 🏫 Internado (educación de alto nivel en el extranjero) 🎓 Año académico en familia anfitriona 🏕 Campamentos de verano ⭐ Pathway universitario 📚 Programas de estudio y trabajo. Cada ruta tiene perfiles distintos. Si me dices cuál te llama más la atención, te puedo ayudar a afinar cuál será para ti (o para tu hijo).

**Toque 4 (día 5 — la última pausa de este flow es de 3 días, no 2):**
> Aquí cuando lo necesites. Te agradezco mucho que nos hayas escrito. Entiendo que a veces no se sabe si se necesita más. Solo quería dejarte claro que si en algún momento quieres avanzar de nuevo, aquí estoy. Que tengas la mejor decisión, sea cual sea.

---

## Categoría E — Agenda + Seguimiento agenda

### E.1 — Agenda (confirmación de cita con nº directo de Rodrigo)

**Estado:** LIVE. Es el flow ManyChat `content20250721163426_851504` que dispara el workflow `Confirmación de agenda` (`2PSekVBxarsrnVBu`) tras detectar una cita creada en el Google Calendar del asesor. El workflow n8n rellena los custom fields `mensaje_inicial_asesoria` (fecha/hora) y `mensaje_link_asesoria` (link Google Meet); el texto siguiente es la parte fija del flow ManyChat.
**Condición:** validación de que la cita fue confirmada.
**Dato de negocio a preservar (nuevo en esta reescritura):**

> Rodrigo se comunicará contigo por WhatsApp directamente desde el número +52 1 33 1944 2476
>
> Siéntete con la libertad de compartirlo con algún familiar que gustes que te acompañe a la reunión. Nos vemos pronto!

> ⚠️ INCIERTO — el texto exacto de `mensaje_inicial_asesoria` / `mensaje_link_asesoria` (fecha, hora, link Meet) se arma dinámicamente en el workflow n8n y no es una plantilla fija; el número directo y el mensaje de "siéntete con la libertad..." sí son fijos, dentro del flow ManyChat. El detalle interno del flow ManyChat no es inspeccionable vía API (impacto: bajo — el número es el dato clave).

### E.2 — Seguimiento agenda (recordatorio único a 48 h)

**Estado:** LIVE (aunque el JSON del sub-workflow `DZlSEQS5qzX1Y01K` está scaffoldeado con un nodo placeholder; ver doc 02). Se dispara si el lead recibió el link pero NO agendó tras 48 h.
**flow_ns ManyChat:** `content20250718124614_140983`. **Tag aplicado:** `seguimiento_agenda`.
**Variable:** `[First Name]`.

> Hola [First Name] 👋 Hace unos días te compartí el enlace para agendar tu asesoría personalizada, pero vi que aún no la agendaste. ¿Tuviste algún problema con el link? Sé que una decisión así requiere claridad, y por eso diseñamos estas sesiones: para ayudarte a resolver dudas reales, evitar errores comunes y construir un plan viable antes de que se pierda tiempo valioso o se cierren opciones 📆. Me interesa que tomes la mejor decisión posible, con respaldo profesional y en el momento adecuado. ¿Te gustaría que te lo vuelva a compartir?

> **Nota de solape:** E.2 (48 h, single-touch, disparado por `Seguimiento agenda`) y el Rescate Post-Link (A/B, 45 min + 24 h, disparado por `Actualizar 'Link enviado'`) son DOS mecanismos distintos y paralelos que apuntan al mismo objetivo (lead con link, sin cita). En GHL conviene consolidarlos en una sola secuencia de nurture multi-toque. Ver doc 06.

---

## Categoría F — Mensaje `system` de memoria sintética (no va al lead)

**Estado:** LIVE. NO es un mensaje que reciba el lead — es un turno `system` en prosa que los workflows de Rescate (A/B) y Outreach (C) **insertan en `n8n_chat_histories`** (Postgres/Supabase) junto con un turno `ai` (el texto del toque enviado). Objetivo: que el agente "Mauricio" cargue esos turnos como contexto previo y **no re-salude ni repregunte** datos que el lead ya dio en el form cuando responde al outreach/rescate.
**Idempotencia:** el `system` se inserta 1 sola vez por `session_id` (`WHERE NOT EXISTS ... type='system'`). Los `ai` se insertan por cada toque.
**SessionKey:** teléfono normalizado con quirk MX (`52XXXXXXXXXX` de 12 dígitos → `521XXXXXXXXXX`, para matchear el sessionKey que ManyChat envía al main).

**Plantilla con todos los campos:**
```
El lead {Nombre Completo} ({Email}, tel +{Telefono}) completó un formulario de {Origen} interesado/a en {Programa interés} para {Grado Escolar} con inicio deseado en {Inicio Deseado} y nivel de inglés {Nivel Inglés}. Vino por la campaña {Ad Name} en {Platform}.
```

**Reglas de omisión elegante:** sin `Apellido` → solo `Nombre` · sin `Email` → omitir el paréntesis de email · sin `Telefono` → omitir tel · `Origen=Form Meta` → "completó un formulario de Meta" · `Origen=Form Landing` → "completó el formulario de nuestra landing" · `Origen=CTWA` → "vino por un anuncio de WhatsApp" (sin "completó formulario") · Grado/Inicio/Nivel todos vacíos → omitir el bloque de cualificación · sin `Ad Name` → omitir última oración · sin `Programa interés` → "...interesado/a en uno de nuestros programas".

**Pseudocódigo del builder (referencia del Code node):**
```javascript
function buildSystemMessage(lead) {
  const nombre = lead['Nombre Completo'] || lead['Nombre'] || 'el lead';
  const email = lead.Email ? `${lead.Email}` : null;
  const tel = lead.Telefono ? `tel +${lead.Telefono}` : null;
  const contact = [email, tel].filter(Boolean).join(', ');
  const contactStr = contact ? ` (${contact})` : '';
  const origenMap = {
    'Form Meta': 'completó un formulario de Meta',
    'Form Landing': 'completó el formulario de nuestra landing',
    'CTWA': 'vino por un anuncio de WhatsApp',
  };
  const accion = origenMap[lead.Origen] || 'mostró interés';
  const programa = lead['Programa interés']
    ? ` interesado/a en ${lead['Programa interés']}`
    : ' interesado/a en uno de nuestros programas';
  const cualif = [
    lead['Grado Escolar'] && `para ${lead['Grado Escolar']}`,
    lead['Inicio Deseado'] && `con inicio deseado en ${lead['Inicio Deseado']}`,
    lead['Nivel Inglés'] && `y nivel de inglés ${lead['Nivel Inglés']}`,
  ].filter(Boolean).join(' ');
  const cualifStr = cualif ? ` ${cualif}` : '';
  const campania = lead['Ad Name']
    ? ` Vino por la campaña ${lead['Ad Name']}${lead.Platform ? ' en ' + lead.Platform : ''}.`
    : '';
  return `El lead ${nombre}${contactStr} ${accion}${programa}${cualifStr}.${campania}`;
}
```

**Ejemplos generados:**
- Lead completo Form Meta:
  > El lead María García López (maria.garcia@gmail.com, tel +5215512345678) completó un formulario de Meta interesado/a en Boarding School para preparatoria con inicio deseado en agosto_2026 y nivel de inglés intermedio. Vino por la campaña BS_MAMAS_TEST1 en ig.
- Lead Form Meta sin email:
  > El lead Juan Pérez (tel +5215587654321) completó un formulario de Meta interesado/a en Gap Year para secundaria con inicio deseado en enero_2027 y nivel de inglés básico. Vino por la campaña GAP_PAPAS_V1 en fb.
- Lead CTWA mínimo:
  > El lead Ana Torres (tel +5491134567890) vino por un anuncio de WhatsApp interesado/a en uno de nuestros programas.

> **Fallback de memoria del Rescate:** el `Build Rescate Memory` del workflow sí tiene diccionario de 6 claves (incluye "Estudio y Trabajo") + fallback genérico — a diferencia del path de envío que solo tiene 5. Por eso "Estudio y Trabajo" es código muerto en el ENVÍO pero vive en la MEMORIA. Ver §A.

---

## Categoría G — Mensajes del agente "Mauricio" (generados por LLM — guías de estilo, no literales)

**Estado:** LIVE. Es el CORAZÓN del sistema. El agente vive inline en el nodo `Agente IA WPP` del main (`k3aivKSP67S97IHn`), modelo **gpt-4o temperature 0**, systemMessage ~39K chars, memoria Postgres (contextWindowLength 35). Usa marcos Chris Voss (empatía táctica: labeling, mirroring, validación, preguntas calibradas) + Alex Hormozi (diagnóstico consultivo antes de vender), metodología propia EMA (Evaluation-Match-Achieve) y un diagnóstico de 7 pasos.

> **IMPORTANTE:** estos textos NO son plantillas fijas. El prompt dice explícitamente *"los ejemplos y frases que aparecen aquí no son para copiar y pegar literalmente. Son guías"*. La respuesta real la genera el LLM en cada turno, se parte en hasta 3 mensajes (nodo gpt-4o-mini) y se limpian los `¿`/`¡` de apertura. Se documentan como **guías de estilo canónicas** para que la migración preserve el comportamiento, no como mensajes inventariables.

**G.1 — Saludo / Paso 1 (obtener nombre de quien escribe):**
- Si el usuario solo dice "quiero info":
  > "¡Hola! Soy Mauricio de Venttur 😊 Me compartes tu nombre completo para brindarte una orientación más personalizada?"
- Si ya expresa interés:
  > "¡Qué gusto que estés considerando una experiencia internacional! ¿Me compartes tu nombre completo para darte una atención adecuada desde el inicio?"
- Regla dura: **siempre** pedir el nombre de la persona que escribe (nunca del hijo/a), aún si el interés es para el hijo/a.

**G.2 — Manejo de precio (nunca dar cifra suelta):**
- Regla: nunca citar la cifra de un programa directamente. Enfocar en beneficios. Validar la preocupación económica, enmarcar el valor total, usar comparaciones, ofrecer explorar formas de optimizar.
  > "Entiendo que el precio es importante. Justamente por eso preferimos explicarlo con claridad una vez que conocemos bien tu perfil. Sería irresponsable darte un número suelto sin saber lo que buscas. En la asesoría vemos eso a fondo y, si el programa lo permite, exploramos formas de optimizar la inversión. ¿Te gustaría revisar eso juntos?"
- Honorarios:
  > "Nuestros honorarios son un porcentaje mínimo del costo total y los explicamos con transparencia en la asesoría, ya que dependen del tipo de programa, destino y nivel de acompañamiento. ..."

**G.3 — Cierre consultivo (Paso 7):**
  > "Con lo que me compartes, el siguiente paso ideal sería agendar una videollamada con [Rodrigo/Andrés/Diego]. En esa llamada podremos entender a fondo su perfil, sus objetivos y cualquier duda que tengan. Les va a servir mucho porque no les daremos información genérica, sino opciones reales que se alineen con su presupuesto, valores y momento familiar. Es una asesoría personalizada, sin compromiso, pero con mucha claridad. ¿Te comparto el enlace para que elijan día y hora?"
- Regla: no repetir el enlace si ya se envió; no ofrecerlo si el lead no está listo.

**G.4 — Links de asesoría por programa (matriz del prompt):** ver tabla en "Links de agendamiento por programa" abajo.

**G.5 — Instrucciones técnicas internas del prompt (tools):**
- Al recibir nombre+apellido → guarda `nombre`/`apellido` y activa la tool `crear_contacto` (sin avisarle al usuario).
- Si el usuario responde al segundo mensaje → activa `contestan_2do`. ⚠️ INCIERTO — **esta tool NO existe como nodo cableado en el main** (impacto: medio; el prompt instruye llamar una tool inexistente, ver doc 02). No se puede confirmar dónde vive esa lógica.
- Si el usuario pide humano/emergencia, o repite exactamente el mismo mensaje dos+ veces consecutivas → activa `elevar` (flow_ns `content20250716130059_365663`).
- Si el usuario pregunta por la web → enviar `venttur.com` + `@venttur_` (Instagram), recalcando que la mejor info está en la asesoría.

---

## Categoría H — Notificaciones operativas (Telegram)

**Estado:** LIVE (parcial). Son mensajes al equipo/errores, no al lead.

| # | Mensaje | Workflow | chatId / bot | Trigger |
|---|---------|----------|--------------|---------|
| H.1 | `🚨 Ejecución en flujo: {workflow} NODO 45 min (1)` + timestamp | Rescate Post-Link | `6390727286` / `NA_errores_bot` | tras `Wait: 45 min` (traza, dispara en cada corrida) |
| H.2 | `🚨 Ejecución en flujo: {workflow} NODO 24 HS (2)` + timestamp | Rescate Post-Link | `6390727286` / `NA_errores_bot` | tras `Wait: 24 hrs` (traza) |
| H.3 | `✈️ VENTTUR — Fallo el nodo de Clientify para recordatorio. Verifica la ejecución: .../executions/{id}` | Confirmación de agenda | `6390727286` / `botla agencia` | fallback: Clientify sin resultado, error Airtable, o SIEMPRE al crear contacto nuevo |

**Errores de workflow (no Telegram):** la mayoría de los workflows usan `errorWorkflow OBkUyb8fuo30DzA9` (`webapp_errors`), que registra en un Supabase central de la agencia (NO en el Supabase de Venttur). Outreach y varios sub-workflows lo usan.

> **Corrección vs. mayo:** el doc de mayo listaba "D.1 — Notificación Telegram del Formulario Clientify". El JSON de `Formulario Clientify` (`ZB6erhWicZmDfC4I`) **NO tiene ningún nodo Telegram** — termina en `Etiquetar Contacto`. Esa notificación no existe en ese workflow. Las notificaciones Telegram reales son H.1–H.3.

---

## Mapping `Programa interés` → texto de Rescate

Usado por el Code node de `wf-rescate-post-link`. **Ojo:** el path de ENVÍO solo tiene 5 ramas (falta "Estudio y Trabajo"); la MEMORIA tiene 6.

| `Programa interés` (contains) | Rescate Fase 1 | Rescate Fase 2 | ¿Se envía? |
|---|---|---|---|
| "Boarding" | §A.1 | §B.1 | ✅ |
| "AA Familiar" (o "Francia") | §A.2 | §B.2 | ✅ |
| "Summer Camp" | §A.3 | §B.3 | ✅ |
| "Pathway" | §A.4 | §B.4 | ✅ |
| "Estudio y Trabajo" | §A.5 | §B.5 | ❌ tag `RESCATE_PROGRAMA_NO_MAPEADO`, sin mensaje |
| "Gap Year" | §A.6 | §B.6 | ✅ |
| (otro) | fallback genérico | fallback genérico | ❌ tag, sin mensaje (solo memoria) |

> **Valores de `Programa interés` en Airtable Leads:** enum de 8 en el schema (`No definido`, `Boarding IA`, `Gap Year IA`, `Pathway IA`, `Summer Camp IA`, `AA Familiar IA`, `Francia IA`, `Automatización - Comentarios`) **+ `Boarding School`**, un 9º valor que escribe activamente el Outreach Form Meta (⚠️ doble grafía Boarding School↔Boarding IA — 482 vs 437 leads; ver doc 03 §5.2 y doc 06). El Code de rescate matchea por substring (`.includes('Boarding')`), lo que hace robusto el match pese a la doble grafía y al sufijo `IA`. `Francia IA` cae en la rama de AA Familiar por el `||`. `Automatización - Comentarios` nunca recibe rescate ni nurturing.

---

## Links de agendamiento por programa (matriz del system prompt)

| Interés del lead | Link | Experto |
|---|---|---|
| Internados / Boarding School | `promo.venttur.com/agendar-ema` | Rodrigo |
| Año Académico con familia (AA Familiar) | `promo.venttur.com/AAFamilia-Agendar` | Rodrigo |
| Summer Camp | `promo.venttur.com/SummerCamp-Agendar` | Rodrigo |
| Pathway universitario Alemania | `promo.venttur.com/PW_Alemania_Agendar` | Andrés |
| Gap Year / Estudiar y trabajar (Australia) | `promo.venttur.com/Estudiar-y-Trabajar-en-Australia` | Diego |
| Estudiar y trabajar (cursos de idiomas) | `promo.venttur.com/EstudiaryTrabajar_Agendar` | Andrés |
| (duda / fallback) | `promo.venttur.com/agendar-ema` | — |

> ⚠️ INCIERTO — ambigüedad "Gap Year / Estudia y trabaja" vs "Estudiar y trabajar" (impacto: medio para el routing de links y expertos). El system prompt tiene DOS entradas que se pisan: (a) "Gap Year / Estudiar y trabajar" → link Australia → **Diego**; (b) "estudiar y trabajar" (cursos de idiomas) → link `EstudiaryTrabajar_Agendar` → **Andrés**. Y una tercera: "GAP Year Australia" → Australia → Diego. El LLM debe desambiguar solo con el contexto; en la práctica puede mandar el link/experto equivocado. **Confirmar con Venttur cuál es la separación real** (Gap Year Australia con Diego vs cursos de idiomas con Andrés).

---

## Notas sobre la ventana de WhatsApp (crítico para la migración)

| Categoría | Tipo de mensaje | Ventana | Requiere Template Meta |
|---|---|---|---|
| A/B Rescate | Mensaje regular | El lead ya escribió → ventana 24 h abierta (Fase 1 sí, Fase 2 puede estar cerrada) | No |
| C Outreach Touch 1/2/3 | **Template MARKETING** (`boarding_form_followup`, es_MX) | Lead nunca escribió (vino de form) → fuera de ventana | **Sí** (aprobado; requiere opt-in `consent_phrase`) |
| D Nurturing 4-toques | Mensaje regular | El lead conversó → dentro de ventana mientras responda | No |
| E Agenda / Seguimiento | Mensaje regular | Lead activo → dentro de ventana | No |
| G Agente Mauricio | Mensaje regular | Lead escribió → dentro de ventana | No |

**En GHL:** los mensajes regulares (A/B/D/E/G) se envían desde Conversations sin necesidad de Templates. **Solo el Outreach Form Meta (C)** requiere Templates de WhatsApp aprobados en el proveedor WA de GHL, porque dispara sobre leads que no escribieron primero (fuera de ventana). Re-registrar los 3 templates MARKETING al migrar.

**Debounce de mensajes:** el flow ManyChat "Recibir mensajes" tiene un **buffer de 20 segundos** (`Pausa inteligente: espera 20 segundos`) que agrupa mensajes cortos consecutivos del lead antes de llamar al webhook del main. GHL debe replicar este debounce, o el agente responderá fragmentado a cada mensaje suelto.

---

## Marcadores de incertidumbre

| Ítem | Qué falta confirmar | Impacto | Owner / cómo resolver |
|---|---|---|---|
| Rescate "Estudio y Trabajo" no se envía | El Code de envío del Rescate solo tiene 5 ramas (falta "Estudio y Trabajo"); leads de ese programa reciben tag `RESCATE_PROGRAMA_NO_MAPEADO` y ningún mensaje. ¿Es un bug o deliberado? | Alto — leads de ese programa quedan sin rescate | la agencia: revisar el Code node del workflow `mkEP1qFN7MVb9qP0`; confirmar con Venttur si "Estudio y Trabajo" es un programa vivo |
| Nurturing AA Familiar toque 4 | Texto exacto no capturado en screenshot (visible ≈ "¿Tu hijo ya te dijo a cuál país le gustaría irse?") | Bajo | la agencia: abrir flow `content20250718123255_243860` en ManyChat Flow editor |
| Nurturing Summer Camp toque 4 | Texto no capturado (la cadena tiene 4 mensajes, el 4º no quedó en el screenshot) | Bajo | la agencia: abrir flow `content20250718123847_652764` en ManyChat |
| Ambigüedad Gap Year vs Estudiar y trabajar | El prompt tiene 2-3 entradas solapadas con links/expertos distintos (Diego/Australia vs Andrés/EstudiaryTrabajar) | Medio — el LLM puede mandar link/experto equivocado | Venttur: definir la separación real de programas y expertos |
| Tool `contestan_2do` | Instruida en el prompt pero sin nodo cableado en el main; ¿dónde/si vive esa lógica? | Medio — métrica "contesta 2do mensaje" puede no registrarse | la agencia: buscar en sub-workflows; decidir si se implementa en GHL o se descarta |
| Texto exacto del flow Agenda (E.1) | El `mensaje_inicial_asesoria` (fecha/hora/link Meet) se arma en n8n; el resto del flow ManyChat no es inspeccionable vía API | Bajo — el nº directo de Rodrigo (dato clave) sí está confirmado | la agencia: abrir flow `content20250721163426_851504` en ManyChat |
| Flow "Elevar" con "Notify Assignees: 0 people" | El screenshot muestra 0 destinatarios; ¿el equipo humano se entera de las elevaciones? | Alto — posible bug: escalamientos sin aviso | Venttur/Max: revisar config real del flow "Elevar" en ManyChat |
| Prioridad del Switch de nurturing | Orden Pathway>Summer Camp>AA Familiar>Boarding>Gap Year para leads multi-programa; ¿es intencional? | Medio | Venttur: definir prioridad de programa para leads con interés múltiple |
| Fallback genérico de rescate vs tag | El fallback existe en `template-texts-canonical` pero el path de envío aplica tag `RESCATE_PROGRAMA_NO_MAPEADO` sin mandar mensaje. ¿El fallback textual llega a usarse en algún envío? | Bajo — parece aplicar solo a la memoria sintética | la agencia: confirmar en el Code node |
| Delivery rate real de C (Templates) y B (Fase 2) | No hay métricas de entrega en el JSON | Medio — clave para justificar la cadencia | Venttur: monitorear delivery/response rate primeras 2 semanas post-go-live |
