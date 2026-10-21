# Delta v1.2 → v1.3 — Fix schema CALCULADORA

**Fecha:** 2026-05-30
**Base:** v1.2 ya aplicada en producción
**Disparador:** Caso C del testing v1.1 falló con `Received tool input did not match expected schema` al llamar a CALCULADORA. Diagnóstico: el sub-workflow CALCULADORA (`OPiuPFwRmq6QgACL` — `HPF - Calculadora`) fue actualizado en algún momento para preferir un input estructurado `items` (con nombre de producto + cantidad), y el trigger expone schema `{cuentas: string, items: string}` exigiendo AMBOS campos. El prompt nunca documentó `items`, así que el LLM solo manda `cuentas` → falla schema en la capa langchain ANTES de ejecutar el JS.

## Contexto técnico

- **Trigger del sub-workflow**: `inputSource: "jsonExample"` con `{"cuentas": "", "items": ""}` → schema con AMBOS campos como string requeridos.
- **JS del sub-workflow** (`Code1`):
  - `if (input.items !== undefined) { orderLines = orderFromItems(input.items); }` — prefiere items, espera array o JSON string parseable.
  - `else if (typeof input.cuentas === "string") { orderLines = orderFromCuentasStr(input.cuentas); }` — fallback legacy (sin nombres → no aplica límites por categoría).
- **PRODUCT_ALIASES** dentro del JS reconoce variaciones ("pantufla mono satin", "pantufla moño satin", etc.) y las mapea al canónico ("Pantufla Moño Satin").

## Cambio en el prompt

Reemplazar la sección `# Tools → **CALCULADORA**` del system message del nodo `AI Agent Recolector` (workflow `[Happy Flops]` / `happyflops-main-v3`) por el nuevo contrato documentado.

### Buscar (texto literal):

```
- **CALCULADORA**: Llama a esta tool para calcular el costo de envio en la cotización (cumpliendo efectivamente con los minimos de cada producto). El proceso para activar la herramienta es simple:
1) Antes de activar verificar que cuentes con la cantidad de productos necesarios y si son sandalias preguntar si son delgadas o gruesas para saber cual es el precio
2) Debes enviar la variable "cuentas" que representan todas las cuentas necesarias para cumplir con el coste del envio. Es decir tienes que enviar separados por una coma todas las cuentas necesarias que representan el peso total para cada producto. Por ejemplo si el usuario pidio 75 pantuflas y 50 sandalias gruesas, la variable "cuentas" : "75 x 0.15, 50 x 0.15" y asi con todos los productos que sean, por lo que la variable "cuentas" es un arreglo de multiplicaciones que reflejan las unidades que se piden de ese producto multiplicado por el peso unitario de cada producto, este peso lo verificas en el apartado "Peso de los Productos (kg)".
3) Una vez recibas el coste total del envio mencionado por esta herramienta, puedes completar la cotizacion y enviarsela al usuario. 

Ejemplo: Si la tool CALCULADORA devuelve 300 entonces significa que el coste del envio es 300 y no se puede modificar el valor.

Importante: Este tool se activa SIEMPRE que haya que realizar una cotización
```

### Reemplazar por:

```
- **CALCULADORA**: Llama a esta tool para calcular el costo de envio en la cotización (cumpliendo efectivamente con los minimos de cada producto). El proceso para activar la herramienta es:

1) Antes de activar verificar que cuentas con TODAS las dimensiones del producto: para sandalias delgadas o gruesas; para pantuflas modelo (normal vs mono) y material (satín vs peluche).

2) ⚠️ La tool recibe DOS variables OBLIGATORIAS — debes mandar SIEMPRE las dos, aunque una vaya vacía. Si omitís alguna, la tool rechaza la llamada con error de schema.

  **2a) `items`** (formato preferido, usalo siempre que puedas) — JSON string con un arreglo de objetos `{producto, cantidad}` usando los **nombres canónicos** de la tabla de abajo. La tool conoce las categorías y aplica límites de empaque correctamente. Ejemplo:
  ```
  items: "[{\"producto\":\"Pantufla Moño Satin\",\"cantidad\":50},{\"producto\":\"Cilindros\",\"cantidad\":80}]"
  cuentas: ""
  ```

  **2b) `cuentas`** (formato legacy, solo si por algún motivo no podés armar `items`) — string con multiplicaciones cantidad × peso unitario separadas por coma, ejemplo: `"75 x 0.15, 50 x 0.14"`. En este caso `items` igual debe ir, vacío: `items: "[]"`.

3) Una vez recibas el `costo_total_envio` que devuelve la tool, usá ese valor exacto en la cotización. Si necesitás recalcular (porque cambiaron productos o cantidades), volvé a llamar la tool con el `items` actualizado.

### Nombres canónicos que la tool reconoce (`producto` en `items`)

Usá EXACTAMENTE estos strings (la tool tiene aliases internos para variaciones, pero conviene mandar el canónico):

- `Mandiles`
- `Kits Anticrudas` (sinónimos del cliente: "costalitos", "costales" → mismo producto)
- `Costales`
- `Cilindros`
- `Vaso Popote 24 oz`
- `Sandalias Delgadas`
- `Sandalias Gruesas`
- `Pantuflas` (normales, sin moño)
- `Pantuflas Mono` (con moño pero sin material confirmado — evitá usarlo: pediste material antes de cotizar)
- `Pantufla Moño Satin`
- `Pantufla Moño Peluche`

### Ejemplo completo de llamada

Cliente pide: 50 pantuflas mono satín + 80 cilindros, evento Boda, CP 44100.

Llamada a CALCULADORA:
```
items: "[{\"producto\":\"Pantufla Moño Satin\",\"cantidad\":50},{\"producto\":\"Cilindros\",\"cantidad\":80}]"
cuentas: ""
```

Respuesta esperada de la tool: objeto con `costo_total_envio`, `costo_total_envio_str`, `cantidad_cajas`, `resumen_cajas`.

Importante: Esta tool se activa SIEMPRE que haya que realizar una cotización.
```

---

## Pasos en n8n

1. Abrir el workflow `[Happy Flops]` en producción.
2. Click sobre el nodo **AI Agent Recolector** (el activo, posición `[4160, 1344]` — no confundir con Recolector1 ni Recolector2).
3. Sección **Options** → desplegar **System Message**.
4. Hacer el find/replace de arriba.
5. Save nodo → Save workflow.

---

## Re-verificación

### Re-correr Caso C
```
Usuario: Quiero 50 pantuflas mono satín para XV con envío a CP 44100
Esperado v1.3:
  - La tool CALCULADORA es invocada con: items: "[{\"producto\":\"Pantufla Moño Satin\",\"cantidad\":50}]"  + cuentas: ""
  - La tool devuelve costo_total_envio (probable $300 según rangos por peso: 50 × 0.15 = 7.5 kg)
  - Rebeca cotiza: 50 Pantuflas Mono Satín × $30 = $1,500 + Envío $300 + Total $1,800 + Anticipo $900
NO debe: "Received tool input did not match expected schema"
```

### Re-correr Caso D con v1.3
```
Usuario: 50 pantufla satin + 50 pantufla de moño de satin, CP 88993
Esperado:
- v1.2 ya resolvió la disambiguación → ambos quedan mapeados a "Pantufla Moño Satin"
- v1.3 fix de schema → la tool ahora se llama con items: "[{\"producto\":\"Pantufla Moño Satin\",\"cantidad\":100}]" (suma ambos lotes) o dos líneas separadas según interpretación
- Cotización correcta sin error de schema y con producto canónico
```

### Re-correr Caso A (regresión)
```
Usuario: 50 pantuflas para boda, CP 44100
Esperado: Rebeca sigue preguntando "¿pantuflas normales o pantuflas mono?" antes de cotizar (no llama CALCULADORA hasta saber).
```

---

## Pendientes derivados (fuera de este fix de prompt)

1. **Discrepancia en rangos de costo**: el sub-workflow tiene DOS code nodes (`Code1` activo + `(viejo)` desconectado) con distintos rangos:
   - `Code1` (activo): 0–4.99→$250, 5–7→$280, 7.1–12→$300, 12.1–19.99→$350, 20–35→$400
   - `(viejo)`: 0–4.99→$200, 5–7→$250, 7.1–15→$300, 15.1–27.99→$350, 28–35→$400
   - Verificar con Oscar que `Code1` tiene los rangos correctos. Si no, conviene volver al viejo o ajustar.
2. **`Pantuflas Mono` (sin material) en aliases**: la tool acepta este nombre y lo mapea a peso 0.15 kg, categoría SANDALIAS — pero el prompt v1.2 prohíbe cotizar Pantuflas Mono sin material. Coherente: el agente nunca debería mandar este string a CALCULADORA. Lo dejamos en la lista canónica solo por completitud.
3. **`AI Agent Recolector2` huérfano**: aparece en el workflow sin conexiones inbound ni outbound. Probablemente un nodo dejado de un intento previo. Conviene borrarlo para evitar confusión.
4. **`AI Agent Recolector1`**: usa CALCULADORA1 (toolCalculator, math básico) en vez de la nueva CALCULADORA workflow. Si Recolector1 está activo en alguna rama del flujo, hay que decidir si también migra al contrato nuevo o sigue con math básico. Inspeccionar inbound `Memory_ID1 → Recolector1`.
