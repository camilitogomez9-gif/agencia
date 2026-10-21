# Templates de Mensajes — Rescate de Agendamiento Incompleto

> **Cliente:** VTR Venttur
> **Fecha:** 2026-05-07
> **Fuente:** Documento de Implementación para la agencia (MODIFICADO) — Estrategia: Rescate de Agendamiento Incompleto

---

## Resumen

12 mensajes: 6 programas x 2 fases.

- **Fase 1 (45 min):** Tono concierge, reducción de fricción. Se envía 45 minutos después de entregar el link de agendamiento.
- **Fase 2 (24 hrs):** Tono storytelling, ataca dolor/objeción específica del programa. Se envía 24 horas después del primer mensaje de rescate.

**Variable ManyChat:** `{{first_name}}`

**Nota:** Los mensajes se envían como mensajes regulares del bot (el lead inició la conversación al solicitar el link). Para Fase 1 (45 min) no hay restricción — está dentro de la ventana de 24 hrs. Para Fase 2 (~25 hrs), si el lead no respondió a Fase 1, la ventana podría estar cerrada y ManyChat no entregaría el mensaje. Esto es aceptable para v1; si se quiere maximizar delivery de Fase 2, se pueden crear Templates como mejora futura.

---

## FASE 1 — Mensajes a los 45 minutos (Concierge y Reducción de Fricción)

### 1. Boarding School

**Condición Airtable:** `Programa interés` contains "Boarding"
**Link:** promo.venttur.com/agendar-ema

> Hola {{first_name}}. Noté que solicitaste el enlace para platicar sobre Boarding School, pero el registro quedó pendiente. Si no encontraste un horario que se ajuste a tu agenda, avísame y reviso disponibilidad manual. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/agendar-ema

---

### 2. AA Familia (Año Académico)

**Condición Airtable:** `Programa interés` contains "AA Familiar"
**Link:** promo.venttur.com/AAFamilia-Agendar

> Hola {{first_name}}. Vi que pediste el enlace para la asesoría de Año Académico, pero la cita quedó en pausa. Si tuviste problemas con la plataforma o los horarios no te cuadran, escríbeme y lo resolvemos. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/AAFamilia-Agendar

---

### 3. Summer Camp

**Condición Airtable:** `Programa interés` contains "Summer Camp"
**Link:** promo.venttur.com/SummerCamp-Agendar

> Hola {{first_name}}. Solicitaste el acceso a la agenda para Summer Camp hace un momento. Si el calendario no te mostró horarios convenientes, dímelo y buscamos un espacio que te funcione. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/SummerCamp-Agendar

---

### 4. Pathway (Alemania)

**Condición Airtable:** `Programa interés` contains "Pathway"
**Link:** promo.venttur.com/PW_Alemania_Agendar

> Hola {{first_name}}. Noté que pediste el enlace para la sesión de Pathway en Alemania. Si la plataforma te dio error o no encontraste disponibilidad, avísame por aquí para coordinarlo directo. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/PW_Alemania_Agendar

---

### 5. Estudio y Trabajo (Cursos de Idiomas)

**Condición Airtable:** `Programa interés` contains "Estudio y Trabajo"
**Link:** promo.venttur.com/EstudiaryTrabajar_Agendar

> Hola {{first_name}}. Vi que solicitaste el calendario para Estudio y Trabajo. Si tuviste algún inconveniente técnico al intentar agendar o no te acomodan las horas, dime y lo reviso. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/EstudiaryTrabajar_Agendar

---

### 6. Gap Year en Australia

**Condición Airtable:** `Programa interés` contains "Gap Year"
**Link:** promo.venttur.com/Estudiar-y-Trabajar-en-Australia

> Hola {{first_name}}. Solicitaste el enlace de asesoría para tu Gap Year en Australia. Si no encontraste un hueco en la agenda o se cerró el enlace, escríbeme y te ayudo a reservarlo. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/Estudiar-y-Trabajar-en-Australia

---

## FASE 2 — Mensajes a las 24 horas (Storytelling)

### 1. Boarding School

**Condición Airtable:** `Programa interés` contains "Boarding"
**Link:** promo.venttur.com/agendar-ema

> Hola {{first_name}} 👋. Noté que tu registro quedó en pausa ayer. Mandar a un hijo a un internado es un gran paso y es súper normal dudar si 'ya está listo'. En la sesión validamos su perfil y vemos los pocos cupos que quedan para la temporada. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/agendar-ema

---

### 2. AA Familia (Año Académico)

**Condición Airtable:** `Programa interés` contains "AA Familiar"
**Link:** promo.venttur.com/AAFamilia-Agendar

> Hola {{first_name}} 👋. Seguro entre tantas cosas ayer se te pasó agendar. La mayor preocupación de los papás siempre es: '¿Se adaptará bien si no domina el idioma?'. En la llamada armamos un plan de inmersión seguro para evitar frustraciones. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/AAFamilia-Agendar

---

### 3. Summer Camp

**Condición Airtable:** `Programa interés` contains "Summer Camp"
**Link:** promo.venttur.com/SummerCamp-Agendar

> Hola {{first_name}} 👋. Vi que tu registro quedó a medias ayer. Es súper común dudar si un Summer Camp será seguro y realmente formativo, o solo un paseo. En 45 min aterrizamos la opción ideal antes de que cierren los grupos de temporada. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/SummerCamp-Agendar

---

### 4. Pathway (Alemania)

**Condición Airtable:** `Programa interés` contains "Pathway"
**Link:** promo.venttur.com/PW_Alemania_Agendar

> Hola {{first_name}} 👋. Noté que pausaste el registro ayer. Muchos creen que necesitan alemán perfecto para empezar, pero el secreto es armar la ruta ya mismo para no perder la admisión en las universidades públicas. En 45 min les damos el mapa completo. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/PW_Alemania_Agendar

---

### 5. Estudio y Trabajo (Cursos de Idiomas)

**Condición Airtable:** `Programa interés` contains "Estudio y Trabajo"
**Link:** promo.venttur.com/EstudiaryTrabajar_Agendar

> Hola {{first_name}} 👋. Seguro el día a día te ganó y se te pasó agendar. ¿Dudas si vale la pena irse teniendo nivel básico? Justo la inmersión total hace que se pierda el miedo en semanas. En la sesión aterrizamos el destino ideal según fechas de inicio. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/EstudiaryTrabajar_Agendar

---

### 6. Gap Year en Australia

**Condición Airtable:** `Programa interés` contains "Gap Year"
**Link:** promo.venttur.com/Estudiar-y-Trabajar-en-Australia

> Hola {{first_name}} 👋. Vi que dejaste el registro a medias. Irse a Australia es un gran paso y la mayor duda siempre es: '¿Encontrará trabajo rápido?'. El secreto está en irse con una ruta clara y no improvisar. Nos quedan pocos espacios esta semana. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/Estudiar-y-Trabajar-en-Australia
