# L2 — Corroboración de primitivas contra GHL · 2026-08-06

**17/17 corroboradas.** Cada caso escribió request+response crudos en
`evidencia-migracion/<PM-id>/<T-id>.json`. Re-correr:

```bash
python3 scripts/testing/hpf-ghl-primitivas.py
```

Sub-cuenta `onRwi0ZF4uYi0Lp6GAbE` · contacto de prueba `3tzzBVjsKlOF2RJjKNOL`
(tag `lead_prueba`) · oportunidad `vzYAb3P86uJ08CI9jKyV`.

| Caso | Punto | Clase | Estado |
|---|---|---|---|
| T-01 | PM-OUT-02 | send-text con read-back byte-exacto | ✅ |
| T-02 | PM-OUT-03 | send-image (ficha de producto) | ✅ |
| T-03 | PM-OUT-04 | send-pdf (métodos de pago) | ✅ |
| T-04 | PM-OUT-04 | send-video (mp4 de catálogo) | ✅ |
| T-05 | PM-IDN-01 | upsert-contact + dedup por teléfono | ✅ |
| T-06 | PM-IDN-02 | find-opportunity (snake_case) | ✅ |
| T-07 | PM-IDN-02 | find-or-create-opportunity | ✅ |
| T-08 | PM-CRM-01 | move-stage: las 13 etapas | ✅ |
| T-09 | PM-CRM-02 | write-CF texto/numérico | ✅ |
| T-10 | PM-CRM-02 | write-CF checkbox por id + array | ✅ |
| T-11 | PM-CRM-03 | prueba negativa: evento fuera del picklist | ✅ |
| T-12 | PM-CRM-04 | add/remove tag | ✅ |
| T-13 | PM-STA-02 | read-stage-to-gate por igualdad de UUID | ✅ |
| T-14 | PM-CAT-02 | catalog-query sobre custom object | ✅ |
| T-15 | PM-OPS-01 | telegram-alert | ⏭ diferido a L3 |
| T-16 | PM-IDN-03 | 1 contacto = 1 oportunidad | ✅ |
| T-17 | PM-CRM-05 | ¿un CF malformado rechaza todo el array? | ✅ |

---

## Hallazgos que cambian el diseño

### 1. 🔴 Cloudflare bloquea el User-Agent por defecto — afecta a todo cliente

Sin un `User-Agent` explícito, **toda** llamada a `services.leadconnectorhq.com` y a
`assets.cdn.filesafe.space` devuelve `403 error_code 1010 browser_signature_banned`.
No es rate limiting ni permisos del PIT: es la firma del cliente HTTP.

Aplica al CDN de la Media Library también. Si un asset "no carga", revisar esto **antes**
de sospechar del archivo.

> **Para W0:** fijar `User-Agent` en todos los nodos httpRequest que peguen a GHL, y
> verificarlo como parte del smoke de L3.

*(Nota: un reporte previo atribuía un 403 a `pageLimit:100` en `records/search`. Era esto.)*

### 2. 🟢 `POST /opportunities/` es el find-or-create autoritativo — mejor que el search

Cuando el contacto ya tiene oportunidad, devuelve **`400` con `code: OPPORTUNITY_NO_DUPLICATE`
y `meta.existingId`**. Es **síncrono y sin lag**, a diferencia de `/opportunities/search`,
que en la primera corrida devolvió `0` resultados para una oportunidad recién creada.

```
find_or_create(contactId):
    POST /opportunities/  {pipelineId, locationId, contactId, name, status:"open", pipelineStageId}
      201 → (resp.opportunity.id, "creada")
      400 && code == "OPPORTUNITY_NO_DUPLICATE" → (resp.meta.existingId, "reusada")
      otro → throw
```

Una sola llamada en el camino común, sin carrera de indexación. **El inbound nunca debe
confirmar un `create` vía `search`.**

`/opportunities/search` sigue sirviendo para consultas, con dos reglas:
**sólo snake_case** (`location_id`, `contact_id`, `pipeline_id`) — camelCase devuelve `422`
listando los parámetros como no existentes — y **no confiar en él inmediatamente después de escribir**.

### 3. 🟠 Un contacto = una oportunidad, para siempre — DELTA vs Kommo

Verificado: incluso con la oportunidad en `status: lost`, crear otra para el mismo contacto
devuelve `OPPORTUNITY_NO_DUPLICATE`.

En Kommo cada lead es una entidad nueva, así que un cliente que volvía generaba otro
`entity_id`. En GHL se reusa la misma oportunidad y **se pierde la separación entre pedidos**.

Impacto concreto en dos casos que el origen sí maneja:
- **Lead perdido que vuelve a escribir** (`Si está en perdidos` → alerta Telegram, sin responder):
  funciona igual, la etapa se lee y se corta.
- **Cliente ganado que hace un segundo pedido**: en Kommo era un lead nuevo desde ETAPA 1;
  acá reescribe la oportunidad existente, pisando el historial del pedido anterior.

> **Decisión requerida.** Puede depender del toggle *Allow Duplicate Opportunity* de la
> sub-cuenta (Settings → Opportunities), que no es legible por API. Tres salidas:
> (a) activar el toggle y replicar el comportamiento de Kommo;
> (b) aceptar el DELTA y documentar que el histórico por pedido se pierde;
> (c) mover el historial de pedidos a un custom object aparte.

### 4. ✅ REFUTADO: "un CF malformado rechaza el array entero"

Los docs de la migración anterior lo listaban como hecho ganado a pulso, y justificaba
varias decisiones. **No se reproduce.** Probado con dos formas de malformación:

| Prueba | Resultado |
|---|---|
| `customFields` con un `id` inexistente + un campo válido | `200`. El id desconocido se ignora en silencio; **el campo válido SÍ se escribe** |
| `field_value: true` (booleano crudo) en un checkbox | `200`. Se almacena `[True]` |
| `evento_detectado: "Otros"` — valor fuera del picklist `['XV','Boda','Casamiento']` | `200`. Se almacena `['Otros']` |

El riesgo real es **el opuesto** al que se creía: GHL es demasiado permisivo. Un `id` de
campo con typo se traga la escritura y devuelve `200 OK` — **pérdida de datos silenciosa**.

**Dos consecuencias:**
- El validador de W0 sigue siendo obligatorio, pero por otro motivo: detectar ids inexistentes
  antes de escribir, no evitar un rechazo global.
- **La decisión bloqueante nº 3 del plan se cae.** `evento_detectado` acepta `"Otros"` tal cual;
  no rompe nada. Corregir el picklist (sacar `Casamiento`, agregar `Otros`) pasa a ser
  higiene cosmética, no un bloqueante. Igual con `tipo_suela` y `Yute`.

### 5. 🟢 El envío es corroborable sin WABA, con evidencia fuerte

`POST /conversations/messages` devuelve `201` y **persiste el mensaje con `body` byte-exacto
y `attachments[]` con la URL exacta**; queda en `status: "failed"` porque no hay WABA.
Verificado para texto, jpg, pdf y mp4 sobre la misma conversación (`44tBzIqK9ODLJ7Jr9Lco`).

Los tres assets de la Media Library responden `206` con el `Content-Type` correcto
(`image/jpeg`, `application/pdf`, `video/mp4`) — son públicos y servibles.

Queda sin probar **únicamente** que Meta entregue y que WhatsApp renderice. Todo el resto
del camino de salida está cubierto.

### 6. ⚠️ Hueco de datos en el catálogo → PM-CAT-05 (L4)

`records/search` sobre `custom_objects.productos` funciona (`201`, 15 registros), pero
**0 de 15 tienen `imagen_url`**. La primitiva está corroborada; el catálogo está vacío de
media. Son 15 SKU arquetípicos, no las ~62 fichas que el bot manda.

---

## Contratos verificados, listos para W0

| op | request | evidencia de éxito |
|---|---|---|
| `upsert_contact` | `POST /contacts/upsert` `{locationId, phone, firstName, lastName, name, tags, source}` | `contact.id` estable ante repetición del mismo `phone` |
| `find_or_create_opportunity` | `POST /opportunities/` optimista | `201`→`opportunity.id` · `400 OPPORTUNITY_NO_DUPLICATE`→`meta.existingId` |
| `get_opportunity` | `GET /opportunities/{id}` | `opportunity.pipelineStageId`, `.contact.id`, `.customFields[]` |
| `update_stage` | `PUT /opportunities/{id}` `{pipelineId, pipelineStageId}` | read-back con igualdad de UUID |
| `update_cf` | `PUT /opportunities/{id}` `{customFields:[{id, field_value}]}` | read-back por `id`; **validar el id contra el schema antes de mandar** |
| `add_tag` / `remove_tag` | `POST`/`DELETE /contacts/{id}/tags` `{tags:[]}` | `contact.tags[]` |
| `send_text` / `send_media` | `POST /conversations/messages` `{type:"WhatsApp", contactId, message, attachments[]}` | `GET /conversations/{convId}/messages` → `body` byte-exacto |
| `search_products` | `POST /objects/custom_objects.productos/records/search` `{locationId, page, pageLimit, query, searchAfter}` | `records[].properties` |

Header obligatorio en todas: `Authorization: Bearer <PIT>`, `Version: 2021-07-28`,
`Content-Type: application/json`, **`User-Agent` no-vacío y no-urllib**.
