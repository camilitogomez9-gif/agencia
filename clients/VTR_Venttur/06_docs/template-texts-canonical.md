# VTR — Texto canónico de templates (source of truth para memoria sintética)

> **Propósito:** doc fuente de verdad del texto exacto de cada template/flow que el sistema envía al lead. Lo usan los nodos Postgres que insertan mensajes sintéticos `ai` en `n8n_chat_histories` para que el agente vea la conversación previa y NO re-salude ni repregunte datos.
>
> **Si Meta aprueba un cambio en cualquier template, actualizar este doc primero y luego propagar a los Code nodes de los workflows que lo usan (outreach v2, backfill v2, rescate post-link).**

---

## Reglas de renderizado

- Placeholder `{{first_name}}` → reemplazar con el `Nombre` del lead (no el "Nombre Completo"; solo el primer nombre).
- Si `{{first_name}}` está vacío → reemplazar con `"hola"` o quitar el saludo y arrancar con la segunda oración (depende del template).
- Resto del texto es literal — no interpolar otras variables.
- Mantener emojis literales (👋, 😊).
- Mantener URLs como aparecen (sin tracking params).

---

## 1. Outreach Form Meta — Touch 1

**Workflow:** `outreach-form-meta-venttur-v2` (workflowId `CUuFxbst3iHpgeXS`)
**Disparador:** rama 0 del Switch (`Toques enviados < 1`), 1h post `Touch 1 programado at`
**ManyChat flow_ns:** `content20260612151152_969589`
**Template Meta:** `boarding_form_followup` (categoría MARKETING, idioma es_MX, aprobado 2026-06-13)

### Texto — ✅ VERIFICADO contra el flow real de ManyChat (2026-07-20)

Confirmado por screenshot directo del flow editor (`flow_2026_07_20_070121.png`, ver `00_migracion_ghl/00_inputs/manychat-flows-content-2026-07-20.md`). El texto que ya estaba en este doc y en los Code nodes coincide palabra por palabra con lo que está realmente vivo en ManyChat — no hizo falta corregir nada.

```
Hola {{first_name}}, gracias por tu interés en nuestros programas de Boarding School.

Vimos que recientemente solicitaste información sobre opciones de estudio en el extranjero.

Me gustaría conocer un poco más sobre tu interés para poder orientarte mejor. ¿El programa sería para tu hijo(a) o para algún familiar?
```

---

## 2. Outreach Form Meta — Touch 2 (24h)

**Workflow:** `outreach-form-meta-venttur-v2`
**Disparador:** rama 1 del Switch (`Toques enviados = 1`), 24h post `Touch 1 programado at`
**ManyChat flow_ns:** `content20260616231914_193459`
**Template Meta:** aprobado 2026-06-16 (categoría MARKETING, es_MX)

### Texto — ✅ VERIFICADO contra el flow real de ManyChat (2026-07-20)

Confirmado por screenshot directo (`flow_2026_07_20_070110.png`). Coincide palabra por palabra con lo ya documentado.

```
Hola {{first_name}},

Muchos padres nos contactan porque quieren brindarles a sus hijos una experiencia internacional que los ayude a desarrollar independencia, confianza y una visión global para su futuro.

Cada estudiante tiene objetivos distintos, por eso nos gustaría entender mejor tu caso para orientarte adecuadamente.

¿Para qué edad o grado escolar estás buscando opciones?
```

---

## 3. Outreach Form Meta — Touch 3 (72h)

**Workflow:** `outreach-form-meta-venttur-v2`
**Disparador:** rama 2 del Switch (`Toques enviados = 2`), 72h post `Touch 1 programado at`
**ManyChat flow_ns:** `content20260616231947_185709`
**Template Meta:** aprobado 2026-06-16 (categoría MARKETING, es_MX)

### Texto — ✅ VERIFICADO contra el flow real de ManyChat (2026-07-20)

Confirmado por screenshot directo (`flow_2026_07_20_070058.png`). Coincide palabra por palabra con lo ya documentado.

```
Hola {{first_name}},

Sabemos que elegir una experiencia educativa internacional es una decisión importante y que normalmente surgen muchas preguntas sobre destinos, seguridad, costos, requisitos y beneficios para el futuro del estudiante.

Nuestro objetivo es ayudarte a encontrar la mejor opción según las metas y necesidades de tu familia.

Si aún estás explorando alternativas, responde este mensaje y con gusto te orientaremos sin compromiso.
```

---

## 4-9. Rescate Post-Link — Fase 1 (45 min) — por programa

**Workflow:** `wf-rescate-post-link` (workflowId `mkEP1qFN7MVb9qP0`)
**Disparador:** 45 min post `Link asesoría enviado at`, solo si `Agendan cita = false`.
**Variable ManyChat:** `{{first_name}}`

> Textos verificados en `rescue-flow-message-templates.md` el 2026-05-07. **Reproducidos íntegros abajo** para que los Code nodes del workflow no dependan de leer otro archivo. Si se modifican, actualizar AMBOS docs (este + el de rescate).

### 4. Boarding School

**Match Airtable:** `Programa interés` contains `"Boarding"`

```
Hola {{first_name}}. Noté que solicitaste el enlace para platicar sobre Boarding School, pero el registro quedó pendiente. Si no encontraste un horario que se ajuste a tu agenda, avísame y reviso disponibilidad manual. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/agendar-ema
```

### 5. AA Familia (Año Académico)

**Match:** `Programa interés` contains `"AA Familiar"`

```
Hola {{first_name}}. Vi que pediste el enlace para la asesoría de Año Académico, pero la cita quedó en pausa. Si tuviste problemas con la plataforma o los horarios no te cuadran, escríbeme y lo resolvemos. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/AAFamilia-Agendar
```

### 6. Summer Camp

**Match:** `Programa interés` contains `"Summer Camp"`

```
Hola {{first_name}}. Solicitaste el acceso a la agenda para Summer Camp hace un momento. Si el calendario no te mostró horarios convenientes, dímelo y buscamos un espacio que te funcione. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/SummerCamp-Agendar
```

### 7. Pathway (Alemania)

**Match:** `Programa interés` contains `"Pathway"`

```
Hola {{first_name}}. Noté que pediste el enlace para la sesión de Pathway en Alemania. Si la plataforma te dio error o no encontraste disponibilidad, avísame por aquí para coordinarlo directo. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/PW_Alemania_Agendar
```

### 8. Estudio y Trabajo (Cursos de Idiomas)

**Match:** `Programa interés` contains `"Estudio y Trabajo"`

```
Hola {{first_name}}. Vi que solicitaste el calendario para Estudio y Trabajo. Si tuviste algún inconveniente técnico al intentar agendar o no te acomodan las horas, dime y lo reviso. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/EstudiaryTrabajar_Agendar
```

### 9. Gap Year en Australia

**Match:** `Programa interés` contains `"Gap Year"`

```
Hola {{first_name}}. Solicitaste el enlace de asesoría para tu Gap Year en Australia. Si no encontraste un hueco en la agenda o se cerró el enlace, escríbeme y te ayudo a reservarlo. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/Estudiar-y-Trabajar-en-Australia
```

---

## 10-15. Rescate Post-Link — Fase 2 (24h post-Fase 1)

**Disparador:** 24h post-envío de Fase 1, solo si `Agendan cita = false`.

### 10. Boarding School

```
Hola {{first_name}} 👋. Noté que tu registro quedó en pausa ayer. Mandar a un hijo a un internado es un gran paso y es súper normal dudar si 'ya está listo'. En la sesión validamos su perfil y vemos los pocos cupos que quedan para la temporada. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/agendar-ema
```

### 11. AA Familia

```
Hola {{first_name}} 👋. Seguro entre tantas cosas ayer se te pasó agendar. La mayor preocupación de los papás siempre es: '¿Se adaptará bien si no domina el idioma?'. En la llamada armamos un plan de inmersión seguro para evitar frustraciones. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/AAFamilia-Agendar
```

### 12. Summer Camp

```
Hola {{first_name}} 👋. Vi que tu registro quedó a medias ayer. Es súper común dudar si un Summer Camp será seguro y realmente formativo, o solo un paseo. En 45 min aterrizamos la opción ideal antes de que cierren los grupos de temporada. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/SummerCamp-Agendar
```

### 13. Pathway

```
Hola {{first_name}} 👋. Noté que pausaste el registro ayer. Muchos creen que necesitan alemán perfecto para empezar, pero el secreto es armar la ruta ya mismo para no perder la admisión en las universidades públicas. En 45 min les damos el mapa completo. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/PW_Alemania_Agendar
```

### 14. Estudio y Trabajo

```
Hola {{first_name}} 👋. Seguro el día a día te ganó y se te pasó agendar. ¿Dudas si vale la pena irse teniendo nivel básico? Justo la inmersión total hace que se pierda el miedo en semanas. En la sesión aterrizamos el destino ideal según fechas de inicio. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/EstudiaryTrabajar_Agendar
```

### 15. Gap Year en Australia

```
Hola {{first_name}} 👋. Vi que dejaste el registro a medias. Irse a Australia es un gran paso y la mayor duda siempre es: '¿Encontrará trabajo rápido?'. El secreto está en irse con una ruta clara y no improvisar. Nos quedan pocos espacios esta semana. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/Estudiar-y-Trabajar-en-Australia
```

---

## Mapping `Programa interés` → texto Rescate

Usado por el Code node del `wf-rescate-post-link` para elegir el template correcto:

| `Programa interés` (contains) | Fase 1 | Fase 2 |
|---|---|---|
| "Boarding" | §4 | §10 |
| "AA Familiar" | §5 | §11 |
| "Summer Camp" | §6 | §12 |
| "Pathway" | §7 | §13 |
| "Estudio y Trabajo" | §8 | §14 |
| "Gap Year" | §9 | §15 |
| (otro) | fallback genérico | fallback genérico |

**Fallback genérico** (si `Programa interés` no matchea ninguno):

```
Hola {{first_name}}. Vi que solicitaste el enlace de asesoría pero el registro quedó pendiente. Si tuviste algún inconveniente con la plataforma o los horarios, escríbeme y lo resolvemos. Reserva tu espacio aquí cuando puedas.
```

---

## Plantilla del mensaje `system` con datos del form (prosa natural)

Renderizado dinámicamente desde campos Airtable Leads, en español rioplatense neutro. Generado en Code node de cada workflow que pre-carga memoria.

**Plantilla con todos los campos:**

```
El lead {Nombre Completo} ({Email}, tel +{Telefono}) completó un formulario de {Origen} interesado/a en {Programa interés} para {Grado Escolar} con inicio deseado en {Inicio Deseado} y nivel de inglés {Nivel Inglés}. Vino por la campaña {Ad Name} en {Platform}.
```

**Reglas de omisión elegante:**

- Si `Apellido` vacío → solo `Nombre`.
- Si `Email` vacío → omitir el paréntesis con email.
- Si `Telefono` vacío → omitir tel del paréntesis.
- Si `Origen` = "Form Meta" → "completó un formulario de Meta".
- Si `Origen` = "Form Landing" → "completó el formulario de nuestra landing".
- Si `Origen` = "CTWA" → "vino por un anuncio de WhatsApp" (sin "completó formulario").
- Si campos de cualificación (Grado/Inicio/Nivel) están todos vacíos → omitir el bloque "para X con inicio Y y nivel Z".
- Si `Ad Name` vacío → omitir última oración "Vino por la campaña...".
- Si `Programa interés` vacío → "...interesado/a en uno de nuestros programas".

**Pseudocódigo del builder (referencia para Code node):**

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

Lead completo Form Meta:
> El lead María García López (maria.garcia@gmail.com, tel +5215512345678) completó un formulario de Meta interesado/a en Boarding School para preparatoria con inicio deseado en agosto_2026 y nivel de inglés intermedio. Vino por la campaña BS_MAMAS_TEST1 en ig.

Lead Form Meta sin email:
> El lead Juan Pérez (tel +5215587654321) completó un formulario de Meta interesado/a en Gap Year para secundaria con inicio deseado en enero_2027 y nivel de inglés básico. Vino por la campaña GAP_PAPAS_V1 en fb.

Lead CTWA mínimo:
> El lead Ana Torres (tel +5491134567890) vino por un anuncio de WhatsApp interesado/a en uno de nuestros programas.

---

## Historial de cambios

| Fecha | Cambio |
|-------|--------|
| 2026-06-23 | Doc creado. Templates 4-15 reproducidos de `rescue-flow-message-templates.md`. Templates 1-3 PENDIENTES de completar manualmente desde ManyChat Flow editor. |
| 2026-07-20 | Templates 1-3 verificados contra 15 screenshots reales del ManyChat Flow editor (`00_migracion_ghl/00_inputs/manychat-flows-content-2026-07-20.md`). El texto ya documentado coincidía exacto — sin cambios de contenido, solo se remueve la marca PENDIENTE. |
