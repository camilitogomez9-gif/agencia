# Plantillas del WABA de Rodrigo a reaprobar en el WABA del bot — 2026-09-18

**Contexto:** el WABA `141523652373940` (número personal de Rodrigo) muere con Clientify. Los flujos operativos que hoy disparan estas plantillas hay que reconstruirlos en GHL apuntando al WABA del bot (`1931874540684022`), lo que requiere **reaprobar cada plantilla** en el nuevo WABA (24-72h por plantilla). Este documento es el input directo del proceso.

**Total a reaprobar:** 11 plantillas únicas (12 nombres — `confirmacion_0_cita_internados_2026` y `confirmacion_p1_boarding` son **idénticas** en body/asset/category, solo cambia el nombre; se consolida en `confirmacion_0_cita_internados_2026` en el WABA del bot, ver §consolidación abajo).

## Consolidación 2026-09-18 (noche)

**`confirmacion_p1_boarding` → `confirmacion_0_cita_internados_2026`.** (la agencia subió esta última manualmente al WABA del bot el 18/9 — cualquiera de las dos servía, quedó la primera.) Verificado byte-a-byte que ambas plantillas del WABA de Rodrigo son idénticas (mismo body, mismo asset video de 16.6 MB con hash coincidente, misma categoría UTILITY, mismo idioma `es_MX`). En Clientify existen como 2 flujos distintos en `Max/Confirmaciones de citas/` pero disparan el mismo mensaje. En el WABA del bot se sube **solo `confirmacion_p1_boarding`**, y ambos flujos de la migración a GHL apuntan a esa única plantilla.

## Lista

### `confirmacion_0_cita_internados_2026`

- **Idioma:** `es_MX` · **Categoría:** `UTILITY` · **Estado hoy en WABA Rodrigo:** `APPROVED`
- **Usada en:** `Max/Confirmaciones de citas`

**Body actual (submitear tal cual al WABA del bot):**

```
Hola {{1}},  Soy Rodrigo, el asesor con quien tendrás tu sesión sobre internados en el extranjero para estudiantes de secundaria y preparatoria.

En este video te explico cómo ingresar al enlace de tu reunión.

Vi que acabas de reservar y quiero confirmar personalmente que el horario sí te funciona.

Responde, por favor:
1. Sí, confirmo mi asistencia.
2. Necesito cambiar el horario.

Rodrigo Garcia de la Vega
Venttur Education & Travel
```

**Componentes adicionales:**
- `HEADER`: {"type": "HEADER", "format": "VIDEO", "example": {"header_handle": ["https://scontent.whatsapp.net/v/t61.29466-34/590540867_2122694995125764_6603501902221000897_n.mp4?ccb=1-7&_nc_sid=8b1bef&_nc_ohc=O2

### `confirmacion_p1_boarding`

- **Idioma:** `es_MX` · **Categoría:** `UTILITY` · **Estado hoy en WABA Rodrigo:** `APPROVED`
- **Usada en:** `Max/Confirmaciones de citas`

**Body actual (submitear tal cual al WABA del bot):**

```
Hola {{1}},  Soy Rodrigo, el asesor con quien tendrás tu sesión sobre internados en el extranjero para estudiantes de secundaria y preparatoria.

En este video te explico cómo ingresar al enlace de tu reunión.

Vi que acabas de reservar y quiero confirmar personalmente que el horario sí te funciona.

Responde, por favor:
1. Sí, confirmo mi asistencia.
2. Necesito cambiar el horario.

Rodrigo Garcia de la Vega
Venttur Education & Travel
```

**Componentes adicionales:**
- `HEADER`: {"type": "HEADER", "format": "VIDEO", "example": {"header_handle": ["https://scontent.whatsapp.net/v/t61.29466-34/760522225_1077181054929307_2528367487538919193_n.mp4?ccb=1-7&_nc_sid=8b1bef&_nc_ohc=T1

### `formulario_aa`

- **Idioma:** `es` · **Categoría:** `MARKETING` · **Estado hoy en WABA Rodrigo:** `APPROVED`
- **Usada en:** `Max/Seguimientos - formulario - landings`

**Body actual (submitear tal cual al WABA del bot):**

```
Hola {{1}}!

Mucho gusto, soy {{2}} de Venttur, recientemente nos dejaste tus datos para solicitar mas información respecto al programa de Año Académico en Francia para Adolescentes.

Con mucho gusto te apoyo a resolver tus dudas, serias tan amable de platicarme, en que grado escolar va tu hijo/a y como esta su nivel de Ingles y Frances?

Con esto podemos brindar información mas precisa.
```

### `formulario_aafamilia`

- **Idioma:** `es_MX` · **Categoría:** `MARKETING` · **Estado hoy en WABA Rodrigo:** `APPROVED`
- **Usada en:** `Max/Seguimientos - formulario - landings`

**Body actual (submitear tal cual al WABA del bot):**

```
Hola {{1}} !

Mucho gusto, soy {{2}} de Venttur, recientemente nos dejaste tus datos para solicitar mas información respecto al programa de Intercambio Año Académico para Adolescentes.

Con mucho gusto te apoyo a resolver tus dudas, serias tan amable de platicarme, en que grado escolar va tu hijo/a?
Con esto podemos brindar información mas precisa.
```

### `formulario_boarding`

- **Idioma:** `es_MX` · **Categoría:** `MARKETING` · **Estado hoy en WABA Rodrigo:** `APPROVED`
- **Usada en:** `Max/Seguimientos - formulario - landings`, `Max/Seguimientos - formulario - landings`

**Body actual (submitear tal cual al WABA del bot):**

```
Hola {{1}} !
Mucho gusto, soy {{2}} de Venttur, recientemente nos dejaste tus datos para solicitar mas información respecto al programa de Boarding school (Internados).
Con mucho gusto te apoyo a resolver tus dudas, serias tan amable de platicarme, cuántos años tiene tu hija/o y  qué tipo de internado estas buscando? Con esto podemos brindar información más precisa.
```

### `mensaje_1_seguimiento_ema`

- **Idioma:** `es_MX` · **Categoría:** `MARKETING` · **Estado hoy en WABA Rodrigo:** `APPROVED`
- **Usada en:** `Mauricio/Flujos Seguimiento Campaña EMA Erika`

**Body actual (submitear tal cual al WABA del bot):**

```
🌟¡Hola {{1}}!

Espero te encuentres muy bien. Soy {{2}} de Venttur Education & Travel. 🌍 ✈️ 

¡Gracias por interesarte en nuestra metodología EMA para encontrar el internado ideal para tu hij@! 💪

Para poder ayudarte de la mejor manera, ¿hay alguna duda o inquietud que tengas después de ver el video? 😊

También, me encantaría saber qué aspectos te interesan más sobre los internados para poder brindarte información más precisa y útil.

Quedo atenta a tu respuesta.

Saludos cordiales,
{{3}}
```

**Componentes adicionales:**
- `BUTTONS`: {"type": "BUTTONS", "buttons": [{"type": "URL", "text": "Volver a Ver el Video", "url": "https://promo.venttur.com/entrenamientospe"}, {"type": "URL", "text": "Agendar Asesoría Gratuita", "url": "http

### `rescate2_noshow_aafamilia`

- **Idioma:** `es_MX` · **Categoría:** `MARKETING` · **Estado hoy en WABA Rodrigo:** `APPROVED`
- **Usada en:** `Max/Rescate No show/AA Familia - Rescate No show`

**Body actual (submitear tal cual al WABA del bot):**

```
Hola {{1}}

Sé que a veces el día se complica y no siempre logramos coincidir.

Una duda muy común entre los padres es:
¿mi hijo podrá adaptarse si aún no domina el idioma del país al que quiere ir?

La mayoría de los estudiantes comienzan con un nivel básico. Lo que realmente marca la diferencia es la inmersión diaria viviendo con una familia anfitriona y el acompañamiento durante todo el proceso.

En la sesión revisamos su caso, exploramos las opciones que mejor se adapten a su perfil y resolvemos todas sus dudas para que puedan tomar una decisión con claridad.
```

**Componentes adicionales:**
- `HEADER`: {"type": "HEADER", "format": "TEXT", "text": "La duda más común antes de estudiar en el extranjero"}
- `BUTTONS`: {"type": "BUTTONS", "buttons": [{"type": "URL", "text": "Visit website", "url": "https://promo.venttur.com/AAFamilia-Agendar{{1}}", "example": ["https://promo.venttur.com/AAFamilia-Agendar"]}]}

### `rescate2_noshow_internado`

- **Idioma:** `es_MX` · **Categoría:** `MARKETING` · **Estado hoy en WABA Rodrigo:** `APPROVED`
- **Usada en:** `Max/Rescate No show/Boarding - Rescate No show`

**Body actual (submitear tal cual al WABA del bot):**

```
Hola {{1}}
Sé que a veces el día se complica y no siempre logramos coincidir.
Muchos padres que consideran un internado tienen dudas como:
“¿Y si todavía no está listo para estar lejos?” o
“Su nivel de idioma aún no es el ideal?”
Lo interesante es que, en un entorno de internado con acompañamiento académico y residencial, los estudiantes suelen desarrollar autonomía mucho más rápido.
La sesión dura 45 minutos y nos permite revisar su situación, ver opciones reales según su perfil y resolver todas sus dudas.
Aquí pueden reagendar cuando les sea conveniente
```

**Componentes adicionales:**
- `HEADER`: {"type": "HEADER", "format": "TEXT", "text": "Lo que muchos padres descubren sobre el internado"}
- `BUTTONS`: {"type": "BUTTONS", "buttons": [{"type": "URL", "text": "Visit website", "url": "https://promo.venttur.com/agendar-ema{{1}}", "example": ["https://promo.venttur.com/agendar-ema"]}]}

### `rescate2_noshow_pathway`

- **Idioma:** `es_MX` · **Categoría:** `MARKETING` · **Estado hoy en WABA Rodrigo:** `APPROVED`
- **Usada en:** `Max/Rescate No show/Pathway - Rescate No show`

**Body actual (submitear tal cual al WABA del bot):**

```
Hola {{1}}

Sé que a veces el día se complica y no siempre logramos coincidir.

Muchos padres que consideran Alemania tienen la misma duda:
¿qué tan viable es realmente ingresar a una universidad pública y cumplir con los requisitos?

El reto normalmente no es la capacidad del estudiante, sino iniciar el proceso sin una ruta clara de idioma, validación académica y tiempos.

Cuando todo se estructura correctamente desde el inicio —idioma, Studienkolleg y proceso universitario— las probabilidades de éxito cambian completamente.

En la sesión revisamos su caso y les explicamos los pasos reales del proceso para que puedan tomar una decisión con claridad.
```

**Componentes adicionales:**
- `HEADER`: {"type": "HEADER", "format": "TEXT", "text": "¿Es realmente posible estudiar en Alemania?"}
- `BUTTONS`: {"type": "BUTTONS", "buttons": [{"type": "URL", "text": "Visit website", "url": "https://promo.venttur.com/PW_Alemania_Agendar{{1}}", "example": ["https://promo.venttur.com/PW_Alemania_Agendar"]}]}

### `rescate2_noshow_summercamp`

- **Idioma:** `es_MX` · **Categoría:** `MARKETING` · **Estado hoy en WABA Rodrigo:** `APPROVED`
- **Usada en:** `Max/Rescate No show/Summer - Rescate No show`

**Body actual (submitear tal cual al WABA del bot):**

```
Hola {{1}}

Sé que a veces el día se complica y no siempre logramos coincidir.

Muchos padres que consideran un Summer Camp tienen dudas muy similares:
¿será una buena primera experiencia?, ¿será seguro?, ¿realmente aprenderá o solo será un viaje?

Justamente por eso muchos estudiantes comienzan con programas cortos: permiten vivir una primera experiencia internacional en un entorno supervisado, estructurado y con enfoque en idioma y convivencia multicultural.

En la sesión revisamos su edad, nivel de idioma y objetivos para ayudarles a elegir la opción más adecuada para una primera experiencia segura y formativa.
```

**Componentes adicionales:**
- `HEADER`: {"type": "HEADER", "format": "TEXT", "text": "¿Es buena idea empezar con un Summer Camp?"}
- `BUTTONS`: {"type": "BUTTONS", "buttons": [{"type": "URL", "text": "Visit website", "url": "https://promo.venttur.com/SummerCamp-Agendar{{1}}", "example": ["https://promo.venttur.com/SummerCamp-Agendar"]}]}

### `seguimiento_ema_dia_10_3`

- **Idioma:** `es_MX` · **Categoría:** `MARKETING` · **Estado hoy en WABA Rodrigo:** `APPROVED`
- **Usada en:** `Mauricio/Flujos Seguimiento Campaña EMA Erika`

**Body actual (submitear tal cual al WABA del bot):**

```
¡Hola {{1}}!

Soy {{2}} nuevamente. 😊

Quería compartir contigo un testimonio sobre cómo la metodología EMA para la busqueda y seleccion de escuelas en el extranjero, ayudó a estos estudiantes y sus familias a tener una experiencia que les cambió la vida. Creo que te será muy útil.

¿Tienes algún tiempo esta semana para una breve llamada o reunión virtual? Me encantaría responder a todas tus dudas e inquietudes personalmente.

Saludos,
{{3}}
```

**Componentes adicionales:**
- `HEADER`: {"type": "HEADER", "format": "IMAGE", "example": {"header_handle": ["https://scontent.whatsapp.net/v/t61.29466-34/455274687_560899806268814_3441258536977698721_n.jpg?ccb=1-7&_nc_sid=8b1bef&_nc_ohc=YfL
- `BUTTONS`: {"type": "BUTTONS", "buttons": [{"type": "URL", "text": "Volver a Ver el Video", "url": "https://promo.venttur.com/entrenamientospe"}, {"type": "URL", "text": "Agendar Asesoría Gratuita", "url": "http

### `seguimiento_ema_dia_15`

- **Idioma:** `es_MX` · **Categoría:** `MARKETING` · **Estado hoy en WABA Rodrigo:** `APPROVED`
- **Usada en:** `Mauricio/Flujos Seguimiento Campaña EMA Erika`

**Body actual (submitear tal cual al WABA del bot):**

```
👋 ¡Hola {{1}}!

Soy {{2}} de Venttur Education & Travel.

Espero que estés bien. Quería compartir contigo algo especial: en Venttur, estamos tan seguros de nuestra metodología EMA que ofrecemos una garantía única. Si las opciones que te presentamos como ideales para tu hij@ no son de tu agrado, *te regresamos íntegramente el costo de implementación,* *¡SIN PREGUNTAS!* 🎓✨

Es una excelente oportunidad para resolver cualquier duda que tengas y explorar cómo podemos ayudarte a encontrar el internado ideal para tu hij@.

¡Espero verte pronto!

Saludos,
{{3}}
```

**Componentes adicionales:**
- `BUTTONS`: {"type": "BUTTONS", "buttons": [{"type": "URL", "text": "Volver a Ver el Video", "url": "https://promo.venttur.com/entrenamientospe"}, {"type": "URL", "text": "Agendar Asesoría Gratuita", "url": "http


## Estrategia `_v2` (2026-09-18 noche)

Meta bloquea por horas la creación de una plantilla con el mismo `name+language` justo después de haberla borrado. Al haber borrado `formulario_aa/aafamilia/boarding` (para reintentar el submit con `example` field), quedaron en cooldown que puede durar hasta 24h.

**Estrategia dual aplicada:**
1. **Subir 3 con sufijo `_v2`** desde Meta BM UI: `formulario_aa_v2`, `formulario_aafamilia_v2`, `formulario_boarding_v2` — mismos bodies, nombres nuevos. Meta las acepta al instante.
2. **Retry en background** de los nombres originales (30 min / 1h / 2h). Si en algún momento Meta destraba, quedan las 2 versiones aprobadas y se puede borrar las `_v2`.

**Impacto en GHL:** los workflows apuntan a `_v2` (o al nombre original si el retry funciona). Sin dependencia de Clientify — la migración avanza igual.
