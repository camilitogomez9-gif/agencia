# Deploy · R3 (asset de mandiles) + blindaje de W2 · 2026-08-20

Tres cambios encadenados. El primero era el objetivo; los otros dos salieron de verificarlo.

---

## 1. R3 — el asset de mandiles que mataba el turno · ✅

**Ficha:** `Boda::Boda::Mandiles` · record `6a750725364ab028d71b7ac8`
**Script:** `scripts/utilities/hpf-reemplazar-asset-ficha.py` (nuevo, generalizado)
**Rollback:** `03_workflows/parches-2026-08-20/asset-boda-boda-mandiles-rollback.json`

| | antes | después |
|---|---:|---:|
| archivo | PNG 4500×4500 | JPEG 2400×2400 |
| tamaño | **6.416.289 B (6,12 MB)** | **976.708 B (0,93 MB)** |
| vs. techo de Telegram (5 MB) | **119 %** ❌ | **19 %** ✅ |

**Verificado en las 3 superficies:** el CDN sirve 976.708 B con `HTTP 200 image/jpeg` · la caché
de W3 devuelve las 3 cards de mandiles con la URL nueva en `Mandiles` · el registro local
`catalogo-airtable.json` sincronizado (sin eso, un `--poblar` lo revertía en silencio).

**Sin efectos colaterales de formato:** `media_tipo` sigue siendo `imagen` (es propiedad del
record, no se deriva de la extensión) y el `tipoDe()` de `TG · aplanar` matchea `.jpe?g` → `foto`,
o sea el mismo camino de envío que el PNG.

**Legibilidad comprobada**, no asumida: se recortó a resolución real la zona del texto más chico
(*"Miembro oficial del Club de los mandilones"*) y se lee sin degradación.

### Barrido sistémico: ningún otro asset en riesgo

Se hizo HEAD sobre los **42 assets únicos** del catálogo:

- **0 sobre el techo de 5 MB** (era 1: éste).
- **1 roto (404)**: el PDF de `Métodos de Pago` — ya conocido, bloqueado en Oscar.

### ⚠️ Lo que este cambio NO arregla

La infografía sigue diciendo **"6 Frases diferentes para escoger"** y el catálogo vigente tiene
**5**. Se reemplazó el catálogo el 17/8 y esta ficha quedó desalineada. Entra con el arte de Oscar.

---

## 2. Blindaje de los nodos de envío de W2 · ✅

**Script:** `scripts/utilities/hpf-fix-w2-onerror.py`
**Snapshot de rollback:** `03_workflows/parches-2026-08-20/W2-snapshot-pre-onerror.json` (sha256 `5e57cac8f03d`)

Los nodos de envío tenían `onError: null` (= stopWorkflow): al fallar uno moría W2 entero y el
loop `Recorrer partes` no seguía, perdiendo **todas** las burbujas posteriores. Es el mecanismo
por el que la ficha de mandiles se comía el resto del turno en 6 de 6 corridas.

**Corrección al plan: son 5 nodos, no 4.** El plan listaba sólo los de Telegram; medido sobre el
vivo, **`W0 · enviar` —el carril de PRODUCCIÓN, el que manda a GHL— tenía la misma fragilidad**.
Los 5 convergen en `Arrastrar contexto`, que reconstruye desde `$('Preparar op')` y no depende del
output del nodo caído, así que el loop puede continuar.

`Armar resumen` pasa a contar los fallos (`partes_fallidas`, `fallos`) para que el fallo blindado
no sea **silencioso**: es la contrapartida aceptada de este cambio.

**`W2 · enviar` (dentro de W1) NO se tocó.** Ahí `onError` no es decisión técnica: haría que el
turno avance de etapa y marque actividad aunque el mensaje no haya salido, dejando al lead marcado
como atendido sin serlo y sacándolo del barrido de seguimientos.

### Nivel de verificación — honesto

| | |
|---|---|
| `onError` en los 5 nodos | ✅ read-back del vivo |
| campos nuevos de `Armar resumen` | ✅ aparecen en ejecuciones reales |
| happy path sin regresión | ✅ 3/3 burbujas entregadas con `ghl_message_id` |
| **la rama de fallo en runtime** | ⚠️ **NO ejercitada** |

No se pudo forzar un fallo por el carril de GHL: acepta con **201** tanto una URL 404 como una
malformada (`"no-es-una-url"`). El carril donde el fallo sí ocurre es Telegram, y mandar desde
Telegram requiere una persona. Queda como prueba manual pendiente.

---

## 3. 🆕 Un contacto sin fila en `hpf_identity` no recibía NADA, en silencio · ✅

**Encontrado** probando lo anterior. **Script:** `hpf-fix-w2-identidad-vacia.py`

`¿Es Telegram?` es un `SELECT … LIMIT 1` **sin `alwaysOutputData`**. Con 0 filas no emite items,
y en n8n un nodo sin entrada no se ejecuta: `Decidir transporte`, `Ruteo transporte` y los 5 nodos
de envío **quedaban sin correr**. W2 terminaba **en verde**, con 5 nodos y cero mensajes.

Y el fallback que debía cubrirlo era **inalcanzable**. `Decidir transporte` dice literalmente
*"Sin fila en hpf_identity o sin prefijo +999 → es un lead de verdad y sale por GHL"*, pero para
eso tiene que ejecutarse. Mismo patrón que el fallback muerto de `Cards a partes` en W6.

**Fix:** `alwaysOutputData: true`. Con 0 filas emite un item vacío, `Decidir transporte` corre,
`chat_id` queda null y la burbuja sale por GHL — lo que el comentario decía que pasaba.

**Verificado con el mismo contacto, antes y después:**

| | antes | después |
|---|---|---|
| ejecución | `1130111` · `success` · 5 nodos | 21 nodos |
| mensajes enviados | **0** (respuesta `null`) | **2/2 con `ghl_message_id`** |

**Alcance en producción:** W1 escribe la identidad antes de que corra W2, así que el camino normal
está cubierto. Pero cualquier ruta que no pase por ese write —o un fallo en él— dejaba al lead sin
respuesta y sin error. El `HPF_GHL_TEST_CONTACT_ID` del `.env` era justamente uno de esos casos.

---

## Higiene

Las pruebas dejaron 8 mensajes rotulados `[prueba onError]` / `[prueba fallback identidad]` en las
conversaciones de los contactos de test `3tzzBVjsKlOF2RJjKNOL` y `KSLMGxHkYbEUEwfkFjdk`. Son los
mismos contactos que ensucia el gate L6 en cada corrida.
