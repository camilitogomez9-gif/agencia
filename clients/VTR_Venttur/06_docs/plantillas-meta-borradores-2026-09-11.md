# Plantillas de Meta — borradores listos para subir (VTR)

**Fecha:** 2026-09-11 · Fuente de textos: `template-texts-canonical.md` (verificado contra ManyChat 2026-07-20).

> **Para qué:** dejar las plantillas de WhatsApp **redactadas en formato Meta** para subirlas apenas se resuelva el número (WABA). Meta tarda **24-72h** en aprobarlas, así que tenerlas listas ahorra ese tiempo del camino crítico.

## Cómo se suben (resumen)
- En GHL (o en Meta WhatsApp Manager): **Templates → New**.
- Por cada una: **Nombre** (tal cual, en minúscula con guiones bajos), **Categoría**, **Idioma** `es_MX`, y el **Cuerpo**.
- La variable **`{{1}}` = nombre del lead** (primer nombre). Meta pide un **valor de ejemplo** al subir → usar `María`.
- **Si el lead no tiene nombre:** el sistema de envío manda `hola` en `{{1}}` (o se arma una versión sin nombre). Es del lado del envío, no de la plantilla.
- Los **links** (`promo.venttur.com/...`) van **fijos dentro del cuerpo** (Meta lo permite). *Opción alternativa:* ponerlos como botón "Ver horarios" — si se prefiere, avisá y lo reformateo.
- **Todas MARKETING** salvo aviso: son de re-enganche (Meta rechaza "utility" para esto — lección Collazo).

---

## A) Outreach Form Meta (3 toques) — MARKETING

### 1. `outreach_form_t1`
**Categoría:** MARKETING · **Idioma:** es_MX · **Variables:** `{{1}}` = nombre (ej. María)
> ⚠️ Puede que ya exista como `boarding_form_followup` (aprobada 2026-06-13). Verificar antes de duplicar.
```
Hola {{1}}, gracias por tu interés en nuestros programas de Boarding School.

Vimos que recientemente solicitaste información sobre opciones de estudio en el extranjero.

Me gustaría conocer un poco más sobre tu interés para poder orientarte mejor. ¿El programa sería para tu hijo(a) o para algún familiar?
```

### 2. `outreach_form_t2`
**Categoría:** MARKETING · **Idioma:** es_MX · **Variables:** `{{1}}` = nombre
```
Hola {{1}},

Muchos padres nos contactan porque quieren brindarles a sus hijos una experiencia internacional que los ayude a desarrollar independencia, confianza y una visión global para su futuro.

Cada estudiante tiene objetivos distintos, por eso nos gustaría entender mejor tu caso para orientarte adecuadamente.

¿Para qué edad o grado escolar estás buscando opciones?
```

### 3. `outreach_form_t3`
**Categoría:** MARKETING · **Idioma:** es_MX · **Variables:** `{{1}}` = nombre
```
Hola {{1}},

Sabemos que elegir una experiencia educativa internacional es una decisión importante y que normalmente surgen muchas preguntas sobre destinos, seguridad, costos, requisitos y beneficios para el futuro del estudiante.

Nuestro objetivo es ayudarte a encontrar la mejor opción según las metas y necesidades de tu familia.

Si aún estás explorando alternativas, responde este mensaje y con gusto te orientaremos sin compromiso.
```

---

## B) Rescate Post-Link — Fase 1 (45 min) — MARKETING

*Una por programa. Variable `{{1}}` = nombre.*

### 4. `rescate_f1_boarding`
```
Hola {{1}}. Noté que solicitaste el enlace para platicar sobre Boarding School, pero el registro quedó pendiente. Si no encontraste un horario que se ajuste a tu agenda, avísame y reviso disponibilidad manual. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/agendar-ema
```

### 5. `rescate_f1_aa_familia`
```
Hola {{1}}. Vi que pediste el enlace para la asesoría de Año Académico, pero la cita quedó en pausa. Si tuviste problemas con la plataforma o los horarios no te cuadran, escríbeme y lo resolvemos. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/AAFamilia-Agendar
```

### 6. `rescate_f1_summer_camp`
```
Hola {{1}}. Solicitaste el acceso a la agenda para Summer Camp hace un momento. Si el calendario no te mostró horarios convenientes, dímelo y buscamos un espacio que te funcione. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/SummerCamp-Agendar
```

### 7. `rescate_f1_pathway`
```
Hola {{1}}. Noté que pediste el enlace para la sesión de Pathway en Alemania. Si la plataforma te dio error o no encontraste disponibilidad, avísame por aquí para coordinarlo directo. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/PW_Alemania_Agendar
```

### 8. `rescate_f1_estudio_trabajo`
```
Hola {{1}}. Vi que solicitaste el calendario para Estudio y Trabajo. Si tuviste algún inconveniente técnico al intentar agendar o no te acomodan las horas, dime y lo reviso. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/EstudiaryTrabajar_Agendar
```

### 9. `rescate_f1_gap_year`
```
Hola {{1}}. Solicitaste el enlace de asesoría para tu Gap Year en Australia. Si no encontraste un hueco en la agenda o se cerró el enlace, escríbeme y te ayudo a reservarlo. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/Estudiar-y-Trabajar-en-Australia
```

---

## C) Rescate Post-Link — Fase 2 (24h) — MARKETING

*Una por programa. Variable `{{1}}` = nombre. (Llevan el emoji 👋.)*

### 10. `rescate_f2_boarding`
```
Hola {{1}} 👋. Noté que tu registro quedó en pausa ayer. Mandar a un hijo a un internado es un gran paso y es súper normal dudar si 'ya está listo'. En la sesión validamos su perfil y vemos los pocos cupos que quedan para la temporada. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/agendar-ema
```

### 11. `rescate_f2_aa_familia`
```
Hola {{1}} 👋. Seguro entre tantas cosas ayer se te pasó agendar. La mayor preocupación de los papás siempre es: '¿Se adaptará bien si no domina el idioma?'. En la llamada armamos un plan de inmersión seguro para evitar frustraciones. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/AAFamilia-Agendar
```

### 12. `rescate_f2_summer_camp`
```
Hola {{1}} 👋. Vi que tu registro quedó a medias ayer. Es súper común dudar si un Summer Camp será seguro y realmente formativo, o solo un paseo. En 45 min aterrizamos la opción ideal antes de que cierren los grupos de temporada. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/SummerCamp-Agendar
```

### 13. `rescate_f2_pathway`
```
Hola {{1}} 👋. Noté que pausaste el registro ayer. Muchos creen que necesitan alemán perfecto para empezar, pero el secreto es armar la ruta ya mismo para no perder la admisión en las universidades públicas. En 45 min les damos el mapa completo. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/PW_Alemania_Agendar
```

### 14. `rescate_f2_estudio_trabajo`
```
Hola {{1}} 👋. Seguro el día a día te ganó y se te pasó agendar. ¿Dudas si vale la pena irse teniendo nivel básico? Justo la inmersión total hace que se pierda el miedo en semanas. En la sesión aterrizamos el destino ideal según fechas de inicio. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/EstudiaryTrabajar_Agendar
```

### 15. `rescate_f2_gap_year`
```
Hola {{1}} 👋. Vi que dejaste el registro a medias. Irse a Australia es un gran paso y la mayor duda siempre es: '¿Encontrará trabajo rápido?'. El secreto está en irse con una ruta clara y no improvisar. Nos quedan pocos espacios esta semana. ¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: promo.venttur.com/Estudiar-y-Trabajar-en-Australia
```

---

## D) Rescate genérico (fallback) — MARKETING

### 16. `rescate_generico`
*Cuando el programa del lead no matchea ninguno de los 6.*
```
Hola {{1}}. Vi que solicitaste el enlace de asesoría pero el registro quedó pendiente. Si tuviste algún inconveniente con la plataforma o los horarios, escríbeme y lo resolvemos. Reserva tu espacio aquí cuando puedas.
```

---

## Lo que FALTA de textos (no lo pude redactar — no está en el repo)

Estas plantillas existen pero sus textos **viven en ManyChat/Meta**, no en la documentación. Hay que **exportarlas de ManyChat** antes de poder pasarlas:

- **Nurturing drip por programa** (Boarding, Pathway, Gap Year, Año Académico, Summer Camp, Lead General — 4 toques c/u). *Fuente: flows ManyChat `content2025071812...`.*
- **Las 3 `seg_dia_3_bs` / `seg_dia_5_bs` / `seg_dia_7_bs`** (viven en Meta/ManyChat — exportar directamente).
- **Recordatorios de cita** (24h + 1h antes) — el texto lo entrega el cliente; categoría probablemente **UTILITY** (atados a una cita agendada → envío más barato).

## Notas / banderas
- **Cantidad:** 16 plantillas redactadas acá + las que faltan de arriba. (La guía estimaba "~10" asumiendo más parametrización, pero el texto del rescate cambia por programa, así que van separadas.)
- **Cruce `Agenda` / `Seguimiento agenda`:** ⚠️ antes de tocar esos dos flujos, verificar en ManyChat cuál es cuál (ver `05_templates_meta_waba.md §5.4`). No afecta las 16 de acá.
- **Categoría:** si al subir Meta recategoriza alguna a UTILITY (raro en re-enganche), mejor — abarata. No forzar.
