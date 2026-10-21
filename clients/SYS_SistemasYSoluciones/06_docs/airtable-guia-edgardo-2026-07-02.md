# 📋 Guía rápida Airtable — SyS Catálogo

**Para:** Edgardo y el equipo que edita el catálogo.
**Para qué sirve:** referencia rápida para cambiar cosas del catálogo sin depender de la agencia. Leer una vez para entender la lógica; después usarla como consulta rápida al querer modificar algo. Si algo no queda claro o falta un caso, avisar para ajustarla.

---

## 🧠 Cómo pensar la base (leer una vez)

Airtable **no es Excel**. Las columnas con un cuadradito de color al lado del nombre son **links** a fichas de otra tabla — no texto suelto. Al ver en un equipo "Sustratos compatibles: Vinilo, Lona", esas son fichas reales de la tabla Sustratos, enganchadas ahí.

Consecuencia práctica: si algo se ve raro (ej. números en vez de nombres de material), el problema está en la **tabla de origen**, no en la que se está mirando.

Todo se **guarda solo**, al instante — no hay botón de guardar. ✅

---

## ✏️ Cómo agregar o editar (vale para todas las tablas)

- **Agregar una fila nueva:** botón `+` al final de la tabla. Para ver/cargar una ficha completa, pasar el mouse por la fila y clic en **Expand** (la flechita).
- **Un campo de texto** (ej. Descripción): clic y escribir.
- **Un campo con opciones o link** (el del cuadradito de color): clic y **elegir la opción que ya aparece en la lista**. Empezar a escribir y, si ya existe, Airtable la muestra — usar esa, **no crear una nueva** (así no quedan duplicados tipo "Vinilo" y "vinilo"). 🚫
- **Un link a otra tabla** (ej. Tecnología en un equipo): clic → buscar y seleccionar la ficha. Un mismo campo puede tener varias.

---

## 🖨️ Equipos

**Uso:** cargar un equipo nuevo o editar uno existente.
✅ **Modificar:** Modelo · Marca · Tecnología (link) · Línea de Producto (link) · Formato · Ancho · Descripción corta · Status · Sustratos compatibles (link) · Aplicaciones compatibles (link) · Cabezales incluidos/tipo · Precio USD.
💡 **Al cargar uno nuevo:** completar todos los campos posibles — si quedan vacíos, el agente responde incompleto. La **Descripción corta** es lo que el agente le cuenta al cliente: si está vacía, queda mudo.
🚫 **No tocar:** el Modelo de un equipo ya cargado · la vista "Para agente".

---

## 🎯 Aplicaciones

Esta tabla le dice al agente, para cada uso (remeras, cartelería, papel fotográfico…), qué tecnologías recomendar. Es la que se modifica cuando **el agente recomienda una tecnología equivocada para un uso**.

**Uso:** agregar un uso nuevo, o corregir las tecnologías que recomienda uno existente.
✅ **Modificar:** Aplicación · Categoría · Tecnologías recomendadas (link) · Sustratos típicos · Keywords cliente.
💡 **Para corregir una recomendación:** abrir (Expand) la ficha del uso y editar **Tecnologías recomendadas** — sacar la que no va, poner la correcta. Ejemplo real: para "papel fotográfico" el agente recomendaba una láser (que no sirve); se dejó **sin tecnología recomendada**. Si el problema es que **no hay ningún equipo** para ese uso, avisar — eso también se ajusta del lado del agente, no solo acá.
🚫 **No tocar:** el nombre (campo Aplicación) de una ficha ya cargada.

---

## 🧵 Sustratos

**Uso:** agregar un material nuevo sobre el que se puede imprimir.
✅ **Modificar:** Sustrato (nombre) · Tipo · Tecnologías compatibles (link).
🚫 **No tocar:** nunca poner un número o una medida como nombre del Sustrato.

---

## ⚙️ Tecnologías

**Uso:** casi nunca — son fijas y estables.
✅ **Modificar:** Descripción larga · Materiales recomendados · Notas para agente.
🚫 **No tocar:** el Nombre (si cambia, el agente deja de reconocerla).

---

## 🔩 Cabezales

**Uso:** raro — catálogo de referencia técnica de cabezales.
✅ **Modificar:** cualquier campo si cambia el dato técnico o el precio.
🚫 **No tocar:** el Modelo/código del cabezal.

---

## 🧴 Insumos

**Uso:** agregar o actualizar tintas, films, polvo.
✅ **Modificar:** Insumo · Categoría · Marca · Tecnología · Cantidad ML/G · Precio USD · Descripción.
🚫 **No tocar:** el campo Insumo de uno ya cargado.

---

## ♻️ Konica Minolta

**Uso:** entra o sale una unidad usada/refurbished.
✅ **Modificar:** Modelo · Tipo · Copias Total/Negro/Color · Estado (Disponible / No disponible) · Stock · Precio USD · Notas.
🚫 **No tocar:** no crear fichas "fantasma" para guardar texto que no es un equipo real (ya pasó una vez con un prompt guardado ahí).

---

## ❓ FAQs

**Uso:** agregar una pregunta frecuente nueva (cuando se nota que algo se pregunta seguido).
✅ **Modificar:** Pregunta · Respuesta corta · Categoría · Keywords · Status (`Activo` para que el agente la use).
💡 **Tip:** la Categoría se asigna sola; en Keywords poner las palabras con las que el cliente suele preguntar. Si ya existe una FAQ parecida, editar esa en vez de crear una nueva.
🚫 **No tocar:** nada delicado — es la tabla más simple.

---

## 🏷️ Líneas de Producto

**Uso:** casi nunca — agrupa equipos por marca/familia comercial.
✅ **Modificar:** Descripción.
💡 **Orden:** al sumar una marca o línea nueva, primero cargar el/los equipos en **Equipos** y después la línea acá.
🚫 **No tocar:** el nombre de la Línea.

---

## 🔍 Si el agente responde algo mal, ¿dónde lo arreglo?

| Síntoma | Ir a… | Modificar… |
|---|---|---|
| 🎯 Recomienda una tecnología equivocada para un uso (ej. papel fotográfico → láser) | **Aplicaciones** → Tecnologías recomendadas | Abrir la ficha del uso (Expand) → en "Tecnologías recomendadas" sacar la que está mal y linkear la correcta. Si ninguna tecnología sirve para ese uso, dejarlo vacío — así el agente no la recomienda. |
| 🖨️ No conoce un equipo que sí se vende, o da specs incompletas | **Equipos** | Si el equipo no existe: cargarlo (botón `+`) completando todos los campos. Si ya existe pero responde poco: abrirlo y completar la **Descripción corta** — es lo que el agente repite al cliente. |
| 🧵 Dice que un equipo imprime (o no) sobre un material, al revés | **Equipos** → Sustratos compatibles | Abrir la ficha del equipo → en "Sustratos compatibles" agregar el material que falta o sacar el que no corresponde (elegir de la lista, no escribir texto libre). |
| ❓ Responde mal una pregunta frecuente (envíos, garantía, showroom, financiación) | **FAQs** | Buscar la pregunta parecida y editar **Respuesta corta** con el texto correcto. Si no existe, crear una nueva (ver sección FAQs) y sumar keywords para que el agente la encuentre. |
| ⚠️ Afirma que hay algo que no hay, o al revés | Avisar | No es un cambio de tabla — puede necesitar un ajuste de comportamiento del agente. Contar el caso puntual (ideal: captura de la conversación) para resolverlo del otro lado. |

---

## 🚫 Nunca tocar (en toda la base)

- El campo primario de una ficha ya en uso (Modelo, Aplicación, Sustrato, Nombre…) — es su identidad; renombrarlo rompe las referencias.
- La vista **"Para agente"** en cualquier tabla — es la que lee el agente en producción.
- Escribir dos valores con coma en un campo de link ("Vinilo, Lona") — cada valor es una ficha aparte, linkeada por separado.
- Crear una ficha para guardar una nota o texto que no sea catálogo real.
- **Representantes** — no corresponde editarla, la maneja Gerencia/la agencia.
- **Config Mensual** — no corresponde editarla, la maneja Gerencia/la agencia (define qué líneas priorizar cada mes).

---

## 💬 Soporte

Cualquier duda antes de tocar algo grande: **Camilo Gómez** - vía WhatsApp. Regla de oro: **ante la duda, no borrar** — sacar una foto y escribir. Y si algo de esta guía no queda claro o falta un caso, avisar para ajustarla.

---

*Revisión 2026-07-10, en base a la reunión con Edgardo y Jimena del 2026-07-08.*
