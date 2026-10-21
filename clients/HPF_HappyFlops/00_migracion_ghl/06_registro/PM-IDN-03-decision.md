# PM-IDN-03 — Un contacto = una oportunidad · DELTA aceptado

**Estado:** cerrado como `DELTA` (no `PARIDAD`). Fecha 2026-08-06.

## El hecho, corroborado

`POST /opportunities/` devuelve `400 OPPORTUNITY_NO_DUPLICATE` con `meta.existingId`
cuando el contacto ya tiene una oportunidad — **incluso si está en `status: lost`**
(caso T-16, evidencia en `07_testing/evidencia-migracion/PM-IDN-03/T-16.json`).

En Kommo cada pedido era un `entity_id` nuevo: un cliente que volvía generaba otro lead.
En GHL se reusa la misma oportunidad.

## Por qué no se cambia el flag

`location.settings.allowDuplicateOpportunity` está en `false`. No es alcanzable:

1. **No está en la UI.** Settings → Opportunities & Pipelines sólo muestra el toggle de
   owners (`crmSettings.deSyncOwners`). Verificado con captura de la pantalla completa.
2. **No es alcanzable por API con este PIT.** `PUT /locations/{id}` →
   `401 The token is not authorized for this scope`. Falta `locations.write`, que es
   scope de agencia, no de sub-cuenta.

Queda como pendiente de la cuenta de agencia, no de este trabajo. El script está listo:
`scripts/utilities/hpf-toggle-duplicate-opportunity.py --activar` (read-modify-write de
un solo flag, con snapshot y `--revertir`).

## Cómo lo resuelve W1, sin depender del flag

`find_or_create_opportunity` de W0 ya distingue los dos casos: devuelve `via: "creada"`
o `via: "existente"`. W1 se apoya en eso:

```
find_or_create → via = "existente" y etapa ∈ {Ganado, Ventas Perdidas}
   ⇒ es un cliente que vuelve:
       · volcar los campos del pedido anterior a `notas_postventa`
       · resetear la oportunidad a `Lead Nuevo`
       · limpiar los CF de cotización del pedido viejo
```

No se pierde el historial del pedido anterior: queda en `notas_postventa`. Lo que se
pierde es tener **una oportunidad por pedido** en el pipeline, que era la granularidad
de Kommo.

**Se adapta solo si el flag cambia.** Si mañana alguien lo pone en `true`, GHL empieza a
crear oportunidades nuevas, `find_or_create` devuelve `via: "creada"`, y la rama de reset
deja de dispararse sin tocar una línea. No hay que acordarse de nada.

## Lo que sí hay que mirar

El caso T-16 hoy corrobora que los duplicados **están bloqueados**. Si alguna vez se
activa el flag, ese caso va a fallar — y eso es correcto: es la señal de que este punto
pasa de `DELTA` a `PARIDAD`. No "arreglar" el test; actualizar la decisión.
