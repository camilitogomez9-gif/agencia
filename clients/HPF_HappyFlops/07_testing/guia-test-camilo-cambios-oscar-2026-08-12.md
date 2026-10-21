# Test — cambios del 12/08 (para Camilo)

Solo lo que se tocó en esta sesión. Nada más.

**Antes de empezar:** cada bloque arranca **conversación nueva** (contacto nuevo o resetear el
chat). Si reusás la misma, el bot ya sabe el evento y varios casos no prueban nada.

---

## 1 · Saludo

**Escribí:** `hola`

Tiene que llegar así, con las negritas y **los tres emojis**:

```
Hola! gracias por escribir a *Happy Flops*, me llamo *Rebeca* soy un asistente virtual, yo le estaré atendiendo con gusto ☺️🙋‍♀

Me podría decir de que es su evento?

🤵👰 - *Boda*
🎂🥳 - *XV Años*
👼🏢 - *Otros*
```

❌ Falla si: falta algún emoji · aparece `•` en vez de `-` · aparece una `"` suelta · no hay negritas.

---

## 2 · Evento (era el bug más grave)

**Escribí:** `hola` → `es para los 15 años de mi hija` → `me interesan los cilindros`

✅ Las imágenes de cilindros tienen que ser **de XV**.
❌ Falla si llega arte de **boda** (novios, anillos).

Repetilo con `es para una boda` → tienen que llegar las de boda.

---

## 3 · Pantufla de peluche

**Conversación A:** `hola` → `es para una boda` → `quiero las pantuflas de moño de peluche`
✅ Llega **solo la foto de la pantufla de peluche**.
❌ Falla si además llega el **catálogo de diseños** (es el de satín, no corresponde).

**Conversación B:** `hola` → `es para una boda` → `me interesan las pantuflas`
✅ Acá **sí** tiene que llegar el catálogo, con todas las opciones.

Las dos tienen que dar distinto. Si dan igual, está mal.

---

## 4 · Ubicación vs. confianza (son dos respuestas distintas)

**Escribí:** `de dónde son? tienen tienda física?`
✅ Dirección completa (JUAN R. ZAVALA #538…) + link de Google Maps.
❌ Falla si el link llega como `[Ubicación](https://...)` en vez de pelado.

**Conversación nueva → escribí:** `cómo sé que es seguro? no será estafa?`
✅ Respuesta de confianza con el link de Facebook.
❌ Falla si te da la dirección (son dos respuestas distintas, no se mezclan).

---

## 5 · Datos de pago

**Escribí:** `hola` → `es para una boda` → `quiero 60 sandalias gruesas al CP 44100` → `sí, quiero avanzar`

✅ Tiene que llegar el **PDF de números de cuenta**.
✅ El pedido de comprobante viene **junto o después** del PDF.

❌ Falla si:
- aparece el texto `url1234.com123` en el chat (ese marcador nunca lo tiene que ver el cliente)
- te pide el comprobante **sin** haberte mandado el PDF
- el mensaje arranca con una coma o un signo suelto

---

## 6 · Cotización: negritas y emojis

En la cotización del punto 5, mirá que estén en negrita:

```
50 *Sandalias Gruesas* x $30 = *$1,500*
Envío: $350
*Total: $2,350*
*Anticipo: $1,175*
```

Nombre del producto, subtotal, Total y Anticipo. La cantidad y el envío van sin negrita.

⚠️ **Lo más importante de este punto:** los **únicos** emojis permitidos son
`😊 ✨ 👟 📦 ⏳ 👍 🚀 🎨 ✏️ 🛠️ 📸 🚚 🎉`

❌ Si ves cualquier otro (💰 💳 🥤 🥿 👡 🧋 🎁 🍳 👛 o el que sea) **avisá** — son los que se ven
mal en el canal.

---

## 7 · "¿Cuánto cuestan?" ⚠️ este falla a veces

Después de la cotización el bot ofrece algo ("ya que pides sandalias, ¿le gustaría agregar
cilindros?").

**Escribí:** `cuánto cuestan?`

✅ Tiene que contestar por **lo que acaba de ofrecer** (cilindros).
❌ Si repite el precio de lo ya cotizado (sandalias), es el fallo conocido.

**Este da bien 4 de cada 7 veces.** Es límite del modelo, no del prompt — ya está medido. Si te
da mal, anotá cuántas veces de cuántas y seguí; no es un cambio que haya que rehacer.

---

## Lo que todavía NO está (no lo pruebes)

- **Video de reseñas de confianza** antes de los 7 pasos → falta subir el video.
- **Catálogo nuevo de mandiles** → sigue la imagen vieja (mandiles rojos). Oscar tiene que
  mandar la nueva.
- **Evento "Otros"** → le faltan imágenes de cilindros y kit anticruda; va a mostrar material
  de otro evento. Ya detectado, no es nuevo.

---

## Atajo: correrlo todo automático

```bash
python3 scripts/testing/hpf-smoke-reunion-oscar-2026-08-11.py
python3 scripts/testing/hpf-smoke-emojis-y-saludo.py
```

El primero cubre los puntos 1 a 7, el segundo el control de emojis. Comparan contra el catálogo
real, no contra lo que el bot dice.

**Si algo falla:** el detalle técnico de cada cambio está en
`06_docs/guia-cambios-reunion-oscar-2026-08-11.md`, y el rollback es una línea:

```bash
python3 scripts/utilities/hpf-deploy-workflow.py --restore clients/HPF_HappyFlops/03_workflows/ghl-live-2026-08-12/W6.json
```
