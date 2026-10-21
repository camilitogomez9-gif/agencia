# Fix `Etiquetar Contacto` — rama FALSE del IF `es vacío` (2026-06-06)

**Workflow:** `Formulario Clientify - Venttur` (id `ZB6erhWicZmDfC4I`)
**Nodo afectado:** `Etiquetar Contacto` (HTTP POST a `/v1/contacts/{id}/tags/`)
**Estado:** ✅ aplicado en prod

## Síntoma

El workflow tiraba el siguiente error cuando un lead repetido llegaba al webhook:

```
ExpressionError: Node 'Crear Contacto Clientify' hasn't been executed
parameter: "url"
cause: "=https://api.clientify.net/v1/contacts/{{ $('Crear Contacto Clientify').item.json.id }}/tags/"
```

## Causa raíz

El nodo `Etiquetar Contacto` referenciaba hardcodeado `$('Crear Contacto Clientify').item.json.id`, pero ese nodo **solo corre en la rama TRUE** del IF `es vacío` (contacto nuevo). Cuando el lead ya existía en Clientify, la rama FALSE ejecutaba el nodo gemelo `Crear Contacto Clientify1`. Al evaluar la URL, n8n no encontraba ejecución del nodo referenciado y abortaba.

### Topología

```
Buscar Contacto Clientify → es vacío (IF)
  ├─ TRUE  (no existe)  → Crear Contacto Clientify   ┐
  └─ FALSE (ya existe)  → Crear Contacto Clientify1  ┘→ Actualizar ID Clientify → Etiquetar Contacto
```

## Fix aplicado

Expresión condicional con `isExecuted` que toma el `id` de la rama que efectivamente corrió:

**URL antes:**
```
=https://api.clientify.net/v1/contacts/{{ $('Crear Contacto Clientify').item.json.id }}/tags/
```

**URL después:**
```
=https://api.clientify.net/v1/contacts/{{ $('Crear Contacto Clientify').isExecuted ? $('Crear Contacto Clientify').item.json.id : $('Crear Contacto Clientify1').item.json.id }}/tags/
```

Es la receta que el propio mensaje de error sugiere (`$if($("nodeName").isExecuted, <action_if_executed>, "")`), adaptada para fallback al nodo de la rama opuesta en vez de cadena vacía.

## Smoke test recomendado

1. **Lead nuevo (rama TRUE):** webhook con teléfono que no existe en Clientify → debe crear contacto + estampar tag del programa.
2. **Lead repetido (rama FALSE — el que reventaba):** webhook con teléfono ya existente → debe identificar el contacto vía `Buscar Contacto Clientify`, no recrearlo, y **estampar la tag igual**.

## Pendientes derivados

- Auditar el resto del workflow buscando otros nodos posteriores al IF `es vacío` que referencien por nombre a `Crear Contacto Clientify` (mismo patrón de bug latente).
- Considerar consolidar ambas ramas en un solo nodo Set que normalice `{id}` y simplificar el grafo (refactor de fondo, no urgente).
