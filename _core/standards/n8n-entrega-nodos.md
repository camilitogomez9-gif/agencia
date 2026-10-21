# Estándar interno — Entrega de nodos y workflows n8n

**Estado:** vigente · **Aplica a:** todo trabajo de n8n en este workspace (cualquier cliente).

Este doc fija **cómo se entrega** cualquier pieza de n8n al usuario. Es regla, no preferencia. Lectura obligatoria antes de devolver nodos o workflows.

---

## Regla 1 — Nodo suelto para copiar/pegar → SIEMPRE en formato clipboard

Cuando el entregable es **un nodo (o un puñado de nodos) para que el usuario los pegue en n8n con Ctrl/Cmd+V**, hay que envolverlo en la estructura que n8n espera del portapapeles:

```json
{
  "nodes": [
    { "...nodo completo..." }
  ],
  "connections": {}
}
```

- `nodes` → array, aunque sea un solo nodo.
- `connections` → objeto (vacío `{}` si es un nodo aislado; con las conexiones si entregás varios nodos cableados entre sí).
- Cada nodo conserva sus campos completos: `parameters`, `type`, `typeVersion`, `position`, `id`, `name` (y `credentials` si aplica).

**PROHIBIDO** entregar el objeto del nodo pelado (sin el envoltorio `nodes`/`connections`). n8n **no lo pega** — el usuario tiene que volver a pedirlo. Esto se pidió varias veces; tratarlo como default, no como caso especial.

### Incluye el código de un Code node

La regla **también aplica cuando lo único que cambia es el `jsCode` de un Code node**. No entregar el JavaScript suelto en un bloque ` ```javascript ` esperando que el usuario lo pegue a mano en el campo Code: entregar **el nodo completo en formato clipboard**, con el `jsCode` ya adentro.

Aplica igual si el nodo ya existe en el canvas y solo se le cambia el código. Motivos:

- El usuario pega el nodo, lo compara contra el que tiene y reemplaza — sin transcribir a mano ni arriesgar un paste parcial (**ya pasó**: en HPF 2026-07-15 se pegó solo un fragmento del prompt y faltó una sección entera de 25 líneas que el resto del texto ya referenciaba).
- Viajan también `typeVersion`, `parameters` y el nombre exacto del nodo, que es lo que hace que las expresiones `$('Nombre')` de otros nodos sigan resolviendo.

⚠️ **Decir explícitamente que pegar crea un nodo NUEVO, no reemplaza el existente.** El usuario tiene que elegir: (a) copiar el contenido del campo desde el nodo pegado al original y después borrar el pegado, o (b) borrar el original, renombrar el pegado igual y recablearlo. Entregar el nodo en clipboard **sin** aclarar esto genera nodos duplicados sueltos en el canvas.

### Cuando son varios edits sobre un flujo en vivo

Combinar: bloque clipboard con los nodos afectados **+** una tabla corta de "qué cambió en cada uno" (campo → antes → después), para que el usuario pueda auditar el diff sin leer JSON crudo. Ver también Regla 3.

### Ejemplo correcto (un nodo Set)

```json
{
  "nodes": [
    {
      "parameters": { "assignments": { "assignments": [] }, "options": {} },
      "type": "n8n-nodes-base.set",
      "typeVersion": 3.4,
      "position": [0, 0],
      "id": "11111111-1111-4111-8111-111111111111",
      "name": "Mi nodo"
    }
  ],
  "connections": {}
}
```

### Varios nodos cableados

Si entregás 2+ nodos que van conectados, incluí las conexiones por **nombre de nodo**:

```json
{
  "nodes": [ { "...nodo A..." }, { "...nodo B..." } ],
  "connections": {
    "Nodo A": { "main": [[{ "node": "Nodo B", "type": "main", "index": 0 }]] }
  }
}
```

---

## Regla 2 — Workflow nuevo completo → JSON importable

Un workflow entero se entrega como archivo `.json` completo (con `name`, `nodes`, `connections`, `settings`, `active: false`, etc.) listo para **importar** en n8n. Va en `clients/[XXX]/03_workflows/`. Indicar "importar este archivo".

---

## Regla 3 — EDIT sobre workflow en vivo/producción → guía paso a paso

NO pre-editar el JSON de un flujo que ya corre en producción (tiene credenciales y estado: memoria, IDs, webhooks registrados). Entregar una **guía de implementación** en `clients/[XXX]/06_docs/` que liste exactamente: qué nodos crear, qué nodos modificar (nombre de nodo + campos + expresiones), qué conexiones agregar. El usuario aplica a mano.

---

## Checklist antes de devolver n8n

- [ ] ¿Es un nodo/fragmento para pegar? → envuelto en `{ "nodes": [...], "connections": {...} }`.
- [ ] ¿Es solo el código de un Code node? → **igual va el nodo completo en formato clipboard**, no el JS suelto. Y aclarar que pegar crea un nodo nuevo.
- [ ] ¿Es un workflow nuevo? → JSON completo importable en `03_workflows/`.
- [ ] ¿Es un cambio sobre algo en producción? → guía paso a paso en `06_docs/`, sin pre-editar el flujo vivo.
- [ ] ¿El JSON valida? (`python3 -c "import json; json.load(open('archivo.json'))"`).
- [ ] ¿Hay Code nodes? → chequear que usen `$getWorkflowStaticData` y no `this.getWorkflowStaticData` (ver `n8n-data-references.md`; es un error que solo revienta en runtime).
