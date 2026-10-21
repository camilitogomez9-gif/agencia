# Estándar interno — Referencias de datos entre nodos en n8n

**Aplica a:** todos los workflows n8n de cualquier cliente.
**Origen:** bug recurrente identificado 2026-06-05 en SYS (`sys-seguimientos-leads-v1`) — referencias `$json.X` en nodos Postgres que tomaban datos del nodo inmediato (que no era el correcto), produciendo `undefined` / NULL en las queries.

---

## Regla de oro

> `$json` y `$input.first().json` se refieren **EXCLUSIVAMENTE** al output del nodo **inmediatamente anterior** en la cadena de ejecución. Para acceder a datos de cualquier otro nodo upstream, usar `$('Nombre del Nodo').item.json.campo` (o `$('Nombre').first().json.campo`).

---

## Cuándo cada uno

### `$json` / `$input.first().json` — usar SOLO si

El dato viene del nodo INMEDIATAMENTE anterior según las conexiones del workflow. Ejemplo: si tu nodo Postgres está conectado directamente después de un nodo Code que devuelve `{session_id, nombre}`, entonces `$json.session_id` funciona.

### `$('Nombre del Nodo').item.json.X` — usar SIEMPRE que

- El dato viene de un nodo upstream que NO es el inmediato (típicamente porque hay 1+ nodos en el medio que producen otro output).
- Estás dentro de un `splitInBatches` y necesitás el contexto del lead que armaste pre-loop.
- Estás en cualquier nodo cuyo input es el output de un HTTP, un IF, un Switch, un Merge, etc., y el dato real lo armaste varios nodos atrás.

`.item.json` accede al item correspondiente del nodo referenciado en el contexto del item actual; `.first().json` accede al primer item. En workflows lineales son equivalentes; dentro de loops con `splitInBatches` o `Loop Over Items`, `.item.json` mantiene la correspondencia 1:1 con el item del batch actual — preferirlo.

---

## Casos típicos donde se cae el error

### 1. Nodo Postgres después de HTTP

```
... → Prepare Context (Code) → HTTP API → Postgres
                                              ↑
                              $json.X aquí NO trae lo de Prepare Context;
                              trae el response del HTTP API (que no tiene
                              tus campos de negocio).
```

**Correcto:**
```js
"queryReplacement": "={{ [$('Prepare Context').item.json.session_id, $('Prepare Context').item.json.nombre] }}"
```

**Incorrecto:**
```js
"queryReplacement": "={{ [$json.session_id, $json.nombre] }}"  // undefined → NULL en query
```

### 2. Nodo HTTP después de otro HTTP

```
... → Build Payload (Code) → setCustomFields (HTTP) → sendFlow (HTTP)
                                                            ↑
                                       $json aquí trae el response de
                                       setCustomFields, no el payload original.
```

**Correcto:**
```js
"jsonBody": "={{ JSON.stringify({ subscriber_id: $('Build Payload').item.json.subscriber_id, flow_ns: '...' }) }}"
```

### 3. Dentro de un `splitInBatches`

```
IF → Loop Over Items → Prepare item → LLM → Build → setCustomFields → sendFlow → Update → Log → (loopback)
                          ↑                                                              ↑
              Aquí $json es el item actual del loop                    Aquí $json es el response del nodo anterior,
              (lo arma splitInBatches automáticamente).               NO el item del loop. Usar $('Prepare item').item.json.
```

### 4. Después de un nodo que no produce data útil

Nodos como `If`, `Merge`, `Wait`, `Postgres` cuando se usan en medio de una cadena pueden no preservar el contexto original; el `$json` posterior trae lo del último nodo, no lo original. Cuando hay duda, **siempre referenciar el nodo origen por nombre.**

---

## Patrón defensivo recomendado

Para workflows con cadenas largas o loops, **referenciar SIEMPRE por nombre** los datos de negocio (session_id, subscriber_id, datos del lead, etc.). Solo usar `$json` cuando el dato es claramente el output del nodo previo y se evalúa de un vistazo.

Convención sugerida en n8n: tener un nodo Code llamado `Prepare X context` al inicio de la rama que arma todas las variables de negocio, y a partir de ahí TODOS los nodos downstream referencian con `$('Prepare X context').item.json.X`. Centraliza la fuente de verdad y elimina ambigüedad.

---

## Cómo detectarlo en testing

Síntomas típicos del bug:
- **Postgres:** filas con NULL en columnas que esperabas pobladas. Queries que afectan 0 rows cuando deberían afectar 1+.
- **HTTP a APIs externas (ManyChat, Airtable, etc.):** request con campos vacíos / mal armados → 4xx error opaco.
- **JSON.stringify(undefined):** produce el string literal `"undefined"` en el log/DB (señal inequívoca).

Smoke test rápido: ejecutar el workflow con pin data, abrir cada nodo Postgres/HTTP downstream, revisar el `queryReplacement` o `jsonBody` evaluado — si ves valores vacíos o "undefined", chequear que la referencia apunte al nodo correcto.

---

## Aplicación retroactiva

Cuando heredás o revisás un workflow ajeno, hacer una pasada rápida:

```bash
# Lista todos los $json.X usados en nodos Postgres y HTTP (suelen ser los problemáticos)
jq -r '.nodes[] | select(.type | test("postgres|httpRequest")) | "\(.name): \(.parameters | tostring)"' workflow.json \
  | grep -oE '\$json\.[a-zA-Z_]+' | sort -u
```

Si aparece `$json.X` y el nodo no está conectado directamente a quien produce ese `X`, es bug latente.

---

## Built-ins del Code node: `$getWorkflowStaticData`, NO `this.getWorkflowStaticData`

**Origen:** bug 2026-08-01 en CLZ (`clz-notificacion-cambio-numero-v2-utility`) — 5 Code nodes escritos con `this.getWorkflowStaticData('global')` reventaban con `TypeError: this.getWorkflowStaticData is not a function` apenas se ejecutaba el workflow.

Dentro de un **Code node** (`n8n-nodes-base.code`) el sandbox expone los helpers como **variables globales con prefijo `$`**, no como métodos de `this`:

```js
// ✅ CORRECTO en un Code node
const staticData = $getWorkflowStaticData('global');

// ❌ INCORRECTO — TypeError en runtime
const staticData = this.getWorkflowStaticData('global');
```

La forma `this.getWorkflowStaticData()` es la de los **Function nodes legacy** y la de los **nodos custom** (donde `this` es el contexto de ejecución del nodo). En el Code node moderno `this` no expone esa API.

### Por qué se cuela tan fácil

El error **no aparece al guardar ni al validar el JSON** — el código dentro de `jsCode` es un string opaco para n8n hasta que el nodo se ejecuta. Un `node --check` del código tampoco lo detecta: es JS sintácticamente válido. Solo revienta en runtime, y solo en el nodo que lo usa. En el bug de CLZ los 5 nodos afectados tenían el mismo error, pero se descubrió de a uno porque cada ejecución moría en el primero.

### Cuidado con `this.helpers`

`this.helpers.httpRequest(...)` **sí** funciona en Code nodes (se usa en `clz-recuperar-contactos-calcom-v1`), lo que hace más fácil asumir por analogía que todo `this.*` está disponible. No es así: `helpers` está expuesto, `getWorkflowStaticData` no.

### Tabla de referencia

| Necesidad | En Code node | En Function node legacy / nodo custom |
|---|---|---|
| Estado persistente entre ejecuciones | `$getWorkflowStaticData('global')` | `this.getWorkflowStaticData('global')` |
| Datos de otro nodo | `$('Nombre').item.json.X` | `this.getNodeParameter(...)` |
| HTTP request | `this.helpers.httpRequest({...})` | idem |
| Items de entrada | `$input.all()` / `$json` | `items` |
| Metadata | `$workflow`, `$execution`, `$now` | `this.getWorkflow()`, etc. |

### Cómo detectarlo antes de ejecutar

```bash
# Cualquier hit acá es un bug latente que solo va a aparecer en runtime
jq -r '.nodes[] | select(.type == "n8n-nodes-base.code") | .parameters.jsCode' workflow.json \
  | grep -n 'this\.getWorkflowStaticData'
```

Correrlo sobre todo workflow con Code nodes **antes** de entregarlo. Si el workflow acumula estado (contadores, resúmenes de batch, dedup), casi seguro usa static data y vale la pena el chequeo.

---

## Resumen de 1 línea

`$json` = nodo previo. Para cualquier otro, `$('Nombre').item.json.X`. En Code nodes, helpers con `$` (`$getWorkflowStaticData`), no con `this`. Cuando dudes, referenciá por nombre.
