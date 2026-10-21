# Test — cierre de los puntos de Oscar (14/08)

Solo lo de este ciclo. **Cada bloque arranca conversación nueva.**

---

## 1 · Saludo

**Escribí:** `hola`

```
Hola! gracias por escribir a *Happy Flops*, me llamo *Rebeca* soy un asistente virtual, yo le estaré atendiendo con gusto ☺️🙋‍♀

Me podría decir de que es su evento?

🤵👰 - *Boda*
🎂🥳 - *XV Años*
👼🏢 - *Otros*
```

❌ Falla si falta un emoji, aparece `•`, o falta alguna negrita.

---

## 2 · Cotización con negritas ← **cambió hoy**

**Escribí:** `hola` → `es para una boda` → `quiero 60 sandalias gruesas al CP 44100, cuanto sale?`

Tienen que estar en negrita el **nombre del producto**, el **subtotal**, el **Total** y el **Anticipo**:

```
60 *Sandalias Gruesas* x $30 = *$1,800*
Envío: $300
*Total: $2,100*
*Anticipo (50%): $1,050*
```

La cantidad y el envío van **sin** negrita, a propósito: si todo está en negrita no resalta nada.

⚠️ Los únicos emojis permitidos son `😊 ✨ 👟 📦 ⏳ 👍 🚀 🎨 ✏️ 🛠️ 📸 🚚 🎉`.
❌ Si ves 💰 💳 🥤 🥿 👡 u otro, avisá.

---

## 3 · Pantufla de peluche ← **cambió hoy**

**A:** `hola` → `es para una boda` → `quiero las pantuflas de moño de peluche`
✅ Llega **una sola imagen**: la de la pantufla de peluche. Sin catálogo.

**B:** `hola` → `es para una boda` → `me interesan las pantuflas`
✅ Acá **sí** llegan todas con el catálogo.

Las dos tienen que dar distinto. Si dan igual, está mal.

---

## 4 · Ubicación ← **cambió hoy**

**Escribí:** `de dónde son? tienen tienda física?`

✅ Dirección completa + el link de Maps **pelado**:

```
https://goo.su/OVoA
```

❌ Falla si llega como `[link](https://goo.su/OVoA)` — así WhatsApp no lo renderiza y le llega roto al cliente. **Ese era el bug.**

**Conversación nueva:** `cómo sé que es seguro?`
✅ Respuesta de confianza con el link de Facebook, **sin** la dirección.

---

## 5 · Datos de pago

**Escribí:** `hola` → `es para una boda` → `quiero 60 sandalias gruesas al CP 44100` → `sí, quiero avanzar`

✅ Llega el **PDF de números de cuenta**, y el pedido de comprobante viene junto o después.
❌ Falla si aparece el texto `url1234.com123`, o si te pide el comprobante sin mandarte el PDF.

*(Esto ya funcionaba antes de hoy — está acá como control de que no lo rompimos.)*

---

## 6 · Evento correcto

**Escribí:** `hola` → `es para los 15 años de mi hija` → `me interesan los cilindros`

✅ Las imágenes tienen que ser **de XV**, no de boda.

*(También es control: ya funcionaba.)*

---

## 7 · "¿Cuánto cuestan?" ⚠️ **sigue fallando ~la mitad de las veces**

Después de la cotización el bot ofrece algo. **Escribí:** `cuánto cuestan?`

✅ Debería contestar por lo **ofrecido**.
❌ A veces te muestra fichas de sandalias, o sea repite lo ya cotizado.

**No lo reportes como bug nuevo.** Está medido: da bien **3 de 5**. Probé subir el modelo y
**empeora** (`gpt-5-mini` → 2/6; bajar la temperatura → 3/6), así que se dejó la configuración
original. El arreglo de verdad es otro y está propuesto aparte — ver la nota al final.

---

## Lo que NO está (no lo pruebes)

- **Video de reseñas** antes de los 7 pasos → falta subir el video a GHL.
- **Catálogo nuevo de mandiles** → sigue el viejo; falta el archivo.
- **Evento "Otros"** → le faltan imágenes en el catálogo de GHL, muestra material de otro evento.

---

## Automático

```bash
python3 scripts/testing/hpf-smoke-emojis-y-saludo.py          # saludo + control de emojis
python3 scripts/testing/hpf-baseline-regresion.py --diff \
  clients/HPF_HappyFlops/07_testing/baseline-2026-08-14/antes.json \
  clients/HPF_HappyFlops/07_testing/baseline-2026-08-14/despues.json
```

El segundo compara el comportamiento **antes y después** de los cambios sobre 12 escenarios, y
es lo que respalda que no se rompió nada fuera de lo pedido.

---

## Sobre el punto 7, para cuando lo quieras encarar

El prompt del Router **instruye** ir a mostrar fichas ante un "¿cuánto cuestan?" post-oferta
(líneas 36 y 80 de `agente-router.md`) — o sea que ese comportamiento es el deseado. Lo que
falla es **qué producto** se elige después: el agente tiene que inferir de la memoria cuál fue
la última sugerencia, y acierta ~60%.

El arreglo determinístico sería **persistir el último producto ofrecido** cuando se emite el
upsell e inyectarlo en el turno siguiente, igual que se hizo con el evento. Es el mismo patrón
que llevó ese bug de 0% a 100%. No se aplicó porque es un cambio de plomería nuevo y quedaba
fuera de lo aprobado para este ciclo.

**Rollback de todo lo de hoy:**

```bash
python3 scripts/utilities/hpf-deploy-workflow.py --restore clients/HPF_HappyFlops/03_workflows/ghl-live-2026-08-14/W6.json
```
