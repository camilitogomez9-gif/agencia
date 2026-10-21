# Deploy · 4 textos de precio + extensión del audio · 2026-08-20

---

## 1. R1 (parcial) — los 4 textos de precio · ✅ APLICADO

**Script:** `scripts/utilities/hpf-remigrar-texto-fichas.py`
**Rollback:** `03_workflows/parches-2026-08-20/fichas-texto-rollback.json` (escrito ANTES de los PUT)

| record | ficha | de → a |
|---|---|---|
| `6a7507325dc856b8c64ad40f` | `XV::XV::Pantuflas XV` | $29 → **$30** |
| `6a750736ba12e25112dcf25f` | `XV::XV::Comparativa sandalias` | $24/$29 → **$25/$30** |
| `6a7507435a8cdd94859ff094` | `Otros::Otros::Pantuflas XV` | $29 → **$30** |
| `6a7507429c080e695f8e5153` | `Otros::Otros::Comparativa sandalias` | $24/$29 → **$25/$30** |

Los 4 PUT devolvieron 200 **con read-back por GET directo confirmado** (no por `records/search`,
que tiene lag de indexación). Registro local `catalogo-airtable.json` sincronizado en las 4
entradas — sin eso, un `hpf-crear-objeto-fichas.py --poblar` posterior revertía el fix en silencio.

**Verificación en la superficie que importa.** El bot NO lee de GHL: lee de la caché Postgres
`hpf_fichas`. Se consultó el webhook de W3 con `ttl_seg: 0` y se revisó ficha por ficha:

```
XV    · Comparativa sandalias   ['$25','$30'] ✅   Pantuflas XV ['$30','$7'] ✅
        Pantuflas mono peluche  ['$35','$7']  ✅   Pantuflas mono satin ['$30','$7'] ✅
Otros · Comparativa sandalias   ['$25','$30'] ✅   Pantuflas XV ['$30','$7'] ✅
```

**No queda ningún $24 ni $29 en la caché.**

### Lo que NO entra acá y por qué

**`Boda | Pantuflas boda` sigue en $29 a propósito.** Su imagen tiene el precio **quemado**
(starburst `¡PROMO! $29 PAR`, verificado abriendo el asset). Corregir sólo el texto dejaría el
mensaje contradiciéndose: texto $30, imagen $29. Entra cuando llegue el arte nuevo de Oscar.

Las otras 4 sí se corrigen solas porque sus imágenes **ya muestran el precio bueno** — el
desfasaje era exclusivamente del campo `descripcion`.

### Bug cosmético corregido de paso

El script imprimía `refresh caché XV: None cards` aunque el refresco funcionara: W3 responde
**envuelto en lista** cuando entra por webhook y el log leía `cantidad` sobre la lista. Arreglado
con el desempaque; el refresco siempre había andado bien.

---

## 2. R3.6 — la nota de voz nunca llegaba a Whisper

**Parche:** `03_workflows/parches-2026-08-20/w1-voice-ext-ogg.json`
**Nodo:** W1 · `TG → payload GHL` · rama `msg.voice` · `ext: 'oga'` → `ext: 'ogg'`

**Medición controlada (2026-08-20)** contra `medias/upload-file` de la location del cliente,
subiendo el **mismo archivo Ogg/Opus dos veces, byte por byte idéntico**, cambiando sólo el nombre:

| extensión | resultado |
|---|---|
| `.oga` | **400 `INVALID_FILE_TYPE`** |
| `.ogg` | **201** |
| `.mp3` | 201 |
| `.m4a` | 400 |
| `.wav` | 201 |

**GHL valida por EXTENSIÓN, no por contenido.** Los 3 archivos de prueba se borraron de la Media
Library después de medir (verificado: no queda ninguno).

**Efecto del bug:** el audio moría en el upload, **antes** de `¿Es audio?`, así que la cadena
`Descargar audio → Transcribir audio` no corría nunca en el carril de Telegram.

El regex de audio de `Normalizar entrada` (`/\.(ogg|oga|mp3|m4a|wav|amr)(\?|$)/`) ya matchea
`.ogg`, así que no cambia nada aguas abajo.

**Anotado, no tocado:** `DOC_OK` sigue aceptando `oga` y `m4a` para `document`, y GHL rechaza las
dos. Es un borde menor (un documento adjunto con esa extensión) que queda como deuda.

**Gate:** `scripts/testing/hpf-l6-w1.py` → 8/8 casos y 7/7 aristas.

---

## 3. Las 14 divergencias de contenido (2.3) · ✅ APLICADO 2026-08-21

**Rollback:** `03_workflows/parches-2026-08-20/fichas-contenido-rollback.json`

De las **23 divergencias** `descripcion` vs `CURL`, 6 eran de precio (ya hechas) y **17 de
contenido**. La revisión una por una las parte en dos:

### Aplicadas (14) — el CURL tiene información real que la migración perdió

| ficha | migrado | vigente |
|---|---|---|
| `Bolsa tipo shein de regalo` ×3 | sin advertencia | **`NO SE PERSONALIZA`** + *"la frase viene tal cual como en la imagen y no se modifica"* |
| `Correas 15MM` ×3 | `CORREAS 15MM` (etiqueta interna) | `CORREAS DE SUELA GRUESA` |
| `Correas 9MM` ×3 | `CORREAS 9MM` | `CORREAS DE SUELA DELGADA` |
| `Tapas termos` ×3 | *"aquí te muestro las tapas"* | *"puede ir surtido en los colores que gustes"* |
| `Catálogo de frases anticruda` (Boda) | sin negritas | con negritas |
| `Catalogo de anticrudas` (Otros) | *"catálogo de diseños"* | *"catalogo de frases"* — es lo que realmente es |

La de la bolsa SHEIN es la más cara: sin esa advertencia, un lead puede pedir la bolsa
personalizada creyendo que se puede.

**Verificado en la caché de W3** (la superficie que lee el bot), los 3 eventos, ficha por ficha.

### NO aplicadas (3) — el `CURL` es MÁS VIEJO que lo migrado

`Todos los productos` en los 3 eventos. Lo migrado cierra con `Cuáles te interesan?`, que es
**exactamente lo que manda el viejo** (verificado en el transcript, B5 y E4). El `CURL` cierra con
*"Dime cuales te interesan, así te mostramos toda su información 😊"*, que el viejo **no** usa.

Es la trampa que el plan anticipó —"el CURL no es siempre la versión vigente"— ahora confirmada
con evidencia. Copiar el CURL a ciegas acá habría sido una regresión.

### Un typo del origen que NO se replicó

El `CURL` de `Correas 15MM` de Otros dice **`CORREAS dDE SUELA GRUESA`**. Bajo la decisión de no
replicar bugs del viejo, se escribió `DE`. Queda declarado.
