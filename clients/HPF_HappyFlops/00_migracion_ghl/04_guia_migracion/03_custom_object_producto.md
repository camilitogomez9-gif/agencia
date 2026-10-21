# M3 — Custom Object: Producto (Catálogo)

> **Referencia:** `03_arquitectura_ghl/02_data_model.md §4`  
> **Tiempo estimado:** 2-3 horas  
> **Prerequisito:** M2 completo

---

## 3.1 ¿Por qué Custom Object y no Airtable?

En la arquitectura GHL definimos que Airtable sigue siendo el **source of truth del catálogo** al inicio. El Custom Object de GHL es opcional para MVP — si preferís no crearlo ahora, n8n puede consultar directamente Airtable usando los mismos datos de los CSVs de `00_inputs/`.

**Decisión:**  
- **Opción A (recomendada MVP):** Mantener Airtable como source. n8n ya sabe leer Airtable. Sin Custom Object por ahora.  
- **Opción B (más integrado):** Crear Custom Object en GHL y poblar desde Airtable. Más limpio a largo plazo pero requiere más setup.

Este módulo documenta la Opción B. Si elegís Opción A, saltear a M4 y en M5 se explica cómo n8n consulta Airtable.

---

## 3.2 Crear el Custom Object "Producto"

> ⚠️ Los Custom Objects requieren plan GHL que lo soporte (Pro/Agency). Verificar antes de proceder.

**Settings → Custom Objects → New Object**

- **Object Name:** `Producto`
- **Object Label (plural):** `Productos`
- **Description:** `Catálogo de productos Happy Flops por evento`

---

## 3.3 Campos del objeto Producto

Dentro del objeto, **Add Field** para cada uno (Label en español; fijar el Key snake_case manualmente como en M2):

| Label (UI, español) | Key (NO tocar) | Tipo | Requerido |
|---------------------|----------------|------|-----------|
| ID de Producto | `producto_id` | Text | Sí |
| Evento | `evento` | Dropdown | Sí |
| Categoría | `categoria` | Dropdown | Sí |
| Nombre | `nombre` | Text | Sí |
| Precio Unitario (MXN) | `precio_unitario_mxn` | Number | Sí |
| Pedido Mínimo | `pedido_minimo` | Number | — |
| Peso (KG) | `peso_kg` | Number | — |
| Descripción | `descripcion` | Text Area | — |
| URL de Imagen | `imagen_url` | Text | — |
| CURL de Envío | `curl_envio` | Text Area | — |
| Activo | `activo` | Checkbox | Sí |
| Solo Mujeres | `solo_mujeres` | Checkbox | — |
| Solo Boda | `solo_boda` | Checkbox | — |

**Opciones para campo Evento:**  
`XV`, `Boda`, `Bautizo`, `Cumpleaños`, `Empresarial`, `Todos`

**Opciones para campo Categoría:**  
`Sandalias`, `Cilindros`, `Mandiles`, `Kit Anticrudas`, `Pantuflas`, `Otros`

---

## 3.4 Poblar el catálogo

Los productos vienen de los CSVs de `00_inputs/`:
- `XV-Grid view.csv`
- `Boda-Grid view.csv`
- `Otros-Grid view.csv`
- `Imagen Principal-Grid view.csv`

**Opción A — Manual (MVP rápido):**  
Cargar los 28 productos manualmente desde la UI. Tarda ~1 hora pero no requiere automatización.

**Opción B — Via n8n (recomendado si hay más de 30 productos):**  
Crear un workflow de "carga inicial" en n8n que lea los CSVs de Airtable y cree registros en el Custom Object via GHL API.

Endpoint para crear un registro:
```
POST https://services.leadconnectorhq.com/custom-objects/records
Authorization: Bearer [GHL_API_KEY]
Content-Type: application/json

{
  "objectId": "[ID_DEL_OBJETO_PRODUCTO]",
  "fields": {
    "producto_id": "SAN-XV-DEL-001",
    "evento": "XV",
    "categoria": "Sandalias",
    "nombre": "Sandalia delgada XV",
    "precio_unitario_mxn": 25,
    "pedido_minimo": 50,
    "activo": true,
    "solo_mujeres": true,
    "solo_boda": false
  }
}
```

El `objectId` del objeto "Producto" se obtiene en **Settings → Custom Objects → [click en Producto] → URL**.

---

## 3.5 Catálogo de productos a cargar

Basado en el análisis de los CSVs de Etapa 0:

### Sandalias XV Años

| Producto ID | Nombre | Precio | Mínimo | Solo Mujeres |
|-------------|--------|--------|--------|-------------|
| `SAN-XV-DEL` | Sandalia Delgada XV | $25 MXN | 50 | Sí |
| `SAN-XV-GRU` | Sandalia Gruesa XV | $30 MXN | 50 | Sí |
| `SAN-XV-YUT` | Sandalia Yute XV | $35 MXN | 50 | Sí |

### Sandalias Boda

| Producto ID | Nombre | Precio | Mínimo | Solo Mujeres |
|-------------|--------|--------|--------|-------------|
| `SAN-BOD-DEL` | Sandalia Delgada Boda | $25 MXN | 50 | Sí |
| `SAN-BOD-GRU` | Sandalia Gruesa Boda | $30 MXN | 50 | Sí |
| `SAN-BOD-YUT` | Sandalia Yute Boda | $35 MXN | 50 | Sí |

### Cilindros

| Producto ID | Nombre | Precio | Mínimo |
|-------------|--------|--------|--------|
| `CIL-XV` | Cilindro XV | $10 MXN | [Oscar confirma] |
| `CIL-BOD` | Cilindro Boda | $10 MXN | [Oscar confirma] |

### Mandiles

| Producto ID | Nombre | Precio | Notas |
|-------------|--------|--------|-------|
| `MAN-BOD` | Mandil Boda | $12 MXN | Solo Boda = true |

### Kit Anticrudas

| Producto ID | Nombre | Precio |
|-------------|--------|--------|
| `KIT-GEN` | Kit Anticrudas | $10 MXN |

### Pantuflas (variantes — Mejora 2026-05-21, P4)

> Distinguir las variantes es **crítico**: Rebeca reportó que el agente cotiza moño con precio de satín clásica. El Custom Object debe tener una entrada por variante y el Cotizador debe tomar la que el lead confirme.

| Producto ID | Nombre | Precio | Categoría (campo) |
|-------------|--------|--------|-------------------|
| `PAN-SAT` | Pantufla satín clásica | $30 MXN | `pantufla_satin` |
| `PAN-MON-SAT` | Pantufla moño satín | [Oscar confirma, ≥$30] | `pantufla_mono_satin` |
| `PAN-MON-PEL` | Pantufla moño peluche | [Oscar confirma, ≥$30] | `pantufla_mono_peluche` |

> Peluche solo en blanca/negra/morada/rosa (regla del catálogo, ver Vendedor §3).

### Vasos con popote (Mejora 2026-05-21, P6)

| Producto ID | Nombre | Precio | Notas |
|-------------|--------|--------|-------|
| `VAS-POP` | Vaso con popote | $35 MXN | Categoría Vision: `VASO_POPOTE`. Distinto de Cilindro (popote visible) |

### Bolsa personalizada (Mejora 2026-05-21, P6)

| Producto ID | Nombre | Precio | Notas |
|-------------|--------|--------|-------|
| `BOL-GEN` | Bolsa personalizada | $7 MXN | Categoría Vision: `BOLSA`. Distinta del Kit Anticruda (bolsa vacía, sin relleno) |

> Precios confirmados según `02_logica_validada/01_decisiones.md §3.6`. Pendiente con Oscar: mínimos de cilindros y precio exacto de pantuflas moño (satín/peluche). Completar antes de M8 (testing) — necesarios para el Cotizador.

---

## 3.6 Asociar el objeto Producto a Opportunity

En GHL, los Custom Objects pueden asociarse a registros del CRM.

**Settings → Custom Objects → Producto → Associations → Add Association**  
- **Associate with:** Opportunity  
- **Relationship name:** `productos_cotizados`

Esto permite que en cada Opportunity, desde la UI, Oscar vea qué productos se cotizaron.

---

## ✅ Checklist M3

- [ ] Verificar que plan GHL soporta Custom Objects
- [ ] Objeto "Producto" creado con todos los campos
- [ ] Opciones de Evento y Categoría configuradas
- [ ] Catálogo cargado (mínimo: sandalias con precios confirmados)
- [ ] Precios pendientes de Oscar anotados para completar antes de M8
- [ ] Asociación Producto ↔ Opportunity creada

**Siguiente:** M4 → Workflows GHL (WF-01 a WF-06)
