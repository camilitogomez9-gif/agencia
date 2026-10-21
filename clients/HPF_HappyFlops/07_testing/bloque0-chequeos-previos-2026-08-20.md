# HPF · Bloque 0 — chequeos previos a los fixes de paridad

**Fecha:** 2026-08-20 · **Plan:** `planes/continuamos-la-migraci-n-de-nifty-penguin.md`

Los cuatro chequeos que definen la prioridad y el alcance del resto del plan. Todos son de
sólo lectura; ninguno tocó el sistema vivo.

---

## 0.3 · ¿El precio está quemado en la imagen? — **RESUELTO**

Se descargaron los 5 assets de las fichas con precio mal y se abrieron uno por uno.

| ficha | la IMAGEN dice | el TEXTO dice | qué hay que arreglar |
|---|---|---|---|
| **Boda \| Pantuflas boda** | **$29 PAR** ❌ | $29 ❌ | **texto + IMAGEN NUEVA** |
| XV \| Pantuflas XV | $30 ✅ | $29 ❌ | sólo texto |
| Otros \| Pantuflas XV | $30 ✅ | $29 ❌ | sólo texto |
| XV \| Comparativa sandalias | $25 / $30 ✅ | $24/$29 ❌ | sólo texto |
| Otros \| Comparativa sandalias | $25 / $30 ✅ | $24/$29 ❌ | sólo texto |

**Conclusión: 5 campos de texto + 1 imagen nueva.** Sólo la de Boda tiene el precio viejo
rasterizado, en el starburst amarillo `¡PROMO! $29 PAR`. Las otras cuatro ya muestran el precio
canónico: el desfasaje es exclusivamente del campo `descripcion`.

⚠️ **La imagen corregida de Boda no está en el repo.** El asset de Airtable es el que tiene el
$29. Hay que pedírsela a Oscar o bajarla del salesbot de Kommo — **se suma a la lista de
assets del Bloque 1**, con el mismo vencimiento.

### Efecto colateral: el "cruce de assets" es cosmético, no un problema de contenido

`XV|Pantuflas XV` y `Otros|Pantuflas XV` tienen los `adjunto_size` invertidos respecto de lo que
sirve el CDN (1.000.555 ↔ 306.564), y lo mismo pasa con las dos `Comparativa`. **Pero las
imágenes son visualmente idénticas entre sí y las cuatro muestran el precio correcto.** Son dos
compresiones distintas del mismo arte. **No hay nada que arreglar acá** — sólo drift de metadata
en el registro.

---

## 0.2 · El PDF de datos bancarios — **RESUELTO, y hay un riesgo de negocio**

**El 404 está confirmado.** La URL que sirve el bot devuelve
`<Error><Code>NoSuchKey</Code></Error>`:

```
https://assets.cdn.filesafe.space/onRwi0ZF4uYi0Lp6GAbE/media/6a7279870629193ed5bc458a.pdf
→ HTTP/2 404
```

**El archivo original se recuperó de Airtable** (la base sigue viva; el PAT de `.env` funciona).
`NUMEROS DE CUENTA.pdf`, 2.539.068 bytes, 1 página. **Se abrió: es legible y está completo** —
Banamex (cuenta + CLABE + tarjeta), OXXO/HSBC y BBVA (cuenta + CLABE + tarjeta), todas a nombre
del titular de Happy Flops. Nadie lo había abierto nunca.

> 🔴 **Riesgo de negocio, no técnico.** El viejo manda un archivo llamado
> **`NUMEROS DE CUENTA NUEVA`** de ~2,0 MB; el migrado se llama `NUMEROS DE CUENTA` y pesa
> 2,42 MB. **Son archivos distintos, y el del viejo dice "NUEVA".** Republicar el de Airtable
> sin confirmar sería servirle al lead una versión potencialmente vieja de los números de cuenta
> con los que transfiere el anticipo.
>
> **Confirmar con Oscar cuál es la vigente antes de subir nada.** Y bajar la del salesbot de
> Kommo mientras se pueda.

---

## 0.1 · ¿El asset de 6,12 MB rompe también en producción? — **NO SE PUEDE CERRAR SIN ENVIAR**

Verificado que el archivo pesa **6.416.289 bytes** y que ese tamaño **ya venía de Airtable**
(`adjunto_size` idéntico) — no es un artefacto de re-subida sin comprimir, como se sospechaba.

Probarlo de verdad exige mandar un mensaje real de WhatsApp, que es una acción hacia afuera.
**Y no hace falta para avanzar:**

- Que el viejo entregue bien la ficha por WhatsApp **no prueba** que el archivo de 6,12 MB pase:
  el viejo sirve desde Kommo, que puede tener una copia más chica.
- **La recompresión (paso 2.1) es correcta en los dos escenarios**: arregla Telegram con certeza
  y de paso saca a producción de la zona de riesgo del límite de 5 MB.

**Conclusión: 0.1 no bloquea 2.1.** Queda como verificación posterior al deploy.

### Recompresión: medida, no estimada

| candidato | bytes | vs. original | ¿<5 MB? |
|---|---:|---:|---|
| 2000 px / high | 718.972 | 11,2 % | ✅ |
| **2400 px / high** | **976.708** | **15,2 %** | ✅ **recomendado** |
| 3000 px / high | 1.454.510 | 22,7 % | ✅ |

El original es un PNG de 4500×4500. 2400 px queda en el rango del resto del catálogo
(Cilindros 0,53 MB · Kit anticruda 2,46 MB) y sobra para un chat.

> 🚩 **Hallazgo colateral al abrir la ficha de mandiles:** dice **"6 Frases diferentes para
> escoger"**. El catálogo nuevo que pasó Oscar el 17/8 tiene **5**, y el prompt ya se corrigió
> para que el lead elija entre 5. **La ficha quedó desalineada** — se reemplazó el catálogo pero
> no esta infografía. Hay que pedirle a Oscar la versión de 5, o el bot va a decir 5 y mostrar
> una imagen que promete 6.

---

## 0.4 · ¿GHL acepta `.ogg` / `.mp3` / `.m4a`? — **PENDIENTE (requiere escritura)**

Sólo está observado el rechazo de `.oga` (`INVALID FILE TYPE`). Determinarlo exige subir un
archivo de prueba a la Media Library del cliente. **Pendiente de aprobación.**

---

## Qué cambia en el plan

1. **2.1 (recompresión de mandiles) puede arrancar ya.** No depende de 0.1.
2. **2.2 pasa de "5 campos" a "4 campos + 1 campo con imagen nueva".** La de Boda queda
   bloqueada por un asset que hay que conseguir.
3. **Se suman dos assets a la lista del Bloque 1:** la infografía de Boda pantuflas con $30 y la
   de mandiles con 5 frases.
4. **2.7 (PDF de pago) deja de ser "recuperar el archivo"** — el archivo ya está. Pasa a ser
   "confirmar con Oscar cuál de las dos versiones es la vigente".
5. **El cruce de assets sale del plan**: verificado que no afecta al contenido.

---

## Extra · Confirmación contra GHL vivo de la ficha que falta

Consultados los **65 records** del custom object en la location del cliente (2026-08-20):

- **Boda tiene 22 fichas.**
- Las únicas de sandalias son `Boda::Boda::Sandalias Video` y
  `Boda::Boda::Sandalias para boda personalizadas` — esta última tiene la `descripcion` en un
  solo espacio y viaja únicamente con el PDF del catálogo.
- **`Boda::Boda::Sandalias personalizadas` NO existe.**

Queda confirmado sobre el sistema vivo, no sólo sobre el registro local: **en el evento
principal no hay ninguna ficha que lleve el precio unitario de las sandalias.** La fila existe en
Airtable (`Boda-Grid view.csv`, bot `60766`, con el texto `$25 / $30` en su CURL) y se perdió en
la migración.

Es el bot `60766` que ya figura en la **Tanda 2** de la captura de Kommo (huérfanos de catálogo).

⚠️ **Crear** records en `custom_objects.fichas` por API está roto (400 sin `locationId`, 422 con
él). **Actualizar** sí funciona — verificado en este mismo ciclo. O sea que esta ficha hay que
crearla por la UI, no por script.
