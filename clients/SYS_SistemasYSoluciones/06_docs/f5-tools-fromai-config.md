# F5 — Config manual de Tools "From AI" en v0.2

> **Para:** configurar manualmente cada uno de los 9 toolWorkflow nodes del main v0.2 en n8n UI.
> **Por qué este doc existe:** re-importar el v0.2 borra la config del `$fromAI()` cuando se re-cablea el workflowId. Esta guía permite configurar todo a mano sin re-import.
> **Fecha:** 2026-05-29

---

## Procedimiento por cada toolWorkflow node

En el `sys-agente-principal-v0.2` actualmente activo en n8n, por cada uno de los 9 toolWorkflow nodes:

### Paso 1 — Verificar / completar el campo **Description del tool**

Es el texto que el LLM lee para decidir CUÁNDO invocar la tool. Está arriba del todo en el panel del nodo. Si está vacío, copiar el texto correspondiente de la sección "Tool X" abajo.

### Paso 2 — Configurar Workflow Inputs

En la sección **"Workflow Inputs"** del toolWorkflow node:
- **Mapping Mode:** `Define Below`
- **Attempt to Convert Types:** **ON** ✅
- **Convert Fields to String:** OFF

### Paso 3 — Configurar cada parámetro

Hay 2 tipos de campos: los que vienen **del LLM** (`$fromAI`) y los que vienen del **contexto del workflow** (expresión n8n).

#### Campos "From AI" (mayoría — el LLM decide qué pasar)

1. Click en **"+ Add Field"** (o ya existe el field).
2. **Name:** copiar el `name` exacto del doc (case-sensitive).
3. **Type:** seleccionar **`string`** para TODOS los campos (incluso los que lógicamente serían array/boolean — el sub-workflow internamente los parsea).
4. **Value:** click en el icono ✨ "From AI" → se llena automático con `$fromAI('name', 'description', 'type')`.
5. **Editar la descripción del $fromAI** y pegar el texto correspondiente del doc (con el "OBLIGATORIO" o "Opcional" al inicio — es lo que el LLM lee para saber qué pasar).

#### Campos "Expresión n8n" (`session_id` y similares — vienen del contexto, NO del LLM)

1. Click en **"+ Add Field"**.
2. **Name:** `session_id` (o el name correspondiente).
3. **Type:** `string`.
4. **Value:** **NO usar From AI.** En su lugar, escribir directamente la expresión n8n:
   ```
   ={{ $('Normalize Payload').item.json.leadIdentifier }}
   ```
   Esto pasa el `leadIdentifier` (canal_subscriberId) calculado en el Normalize Payload node, que es estable e identifica unívocamente la conversación.

> **Por qué session_id NO es From AI:** el session_id identifica qué conversación es. Si lo manejara el LLM, podría alucinar uno distinto cada turno → romper el tracking de tool calls + memoria. Pasándolo como expresión n8n directa, garantizamos consistencia y seguridad.

> **IMPORTANTE:** el `required` en n8n debe quedar **OFF** para TODOS los campos (incluso los lógicamente obligatorios). La obligatoriedad la marca solo el texto "OBLIGATORIO" de la descripción, NO el toggle de required. Si marcás required en la UI, Zod (LangChain) lo valida strict y los inputs complejos del LLM van a fallar (como te pasó con HUENU UV y banderas).

---

## Tool 1: `consultar_tecnologia`

**Description del tool** (campo "Description" del toolWorkflow node):

```
Consulta ficha técnica de una tecnología del catálogo SyS. Devuelve descripción, materiales recomendados, restricciones y aplicaciones. Tecnologías disponibles: DTF Textil, DTF UV, UV, Sublimación, Eco-Solvente, Solvente, RISO, IDL Láser, Gran Formato, Corte. Usá cuando el cliente pregunta 'qué es X', 'cómo funciona X', 'diferencia entre X e Y' (en este caso invocá 2 veces, una por cada tecnología).
```

**Parámetros (todos type=string, required=OFF):**

| Name | Descripción para $fromAI |
|---|---|
| `tecnologia` | `OBLIGATORIO: nombre exacto. Valores: DTF Textil | DTF UV | UV | Sublimación | Eco-Solvente | Solvente | RISO | IDL Láser | Gran Formato | Corte` |
| `aspecto` | `Opcional: descripcion | materiales | restricciones | aplicaciones` |

**Campo adicional (NO es From AI — es contexto):**

| Name | Value (expresión n8n directa) |
|---|---|
| `session_id` | `={{ $('Normalize Payload').item.json.leadIdentifier }}` |


---

## Tool 2: `consultar_faq`

**Description del tool:**

```
Busca en la base de FAQs sobre showroom, financiación, garantía, plazos, servicio técnico, llamadas, tienda online, distribuidores, IVA, cabezales. Usá cuando el cliente pregunta cualquiera de estos temas operativos/comerciales.
```

**Parámetros (todos type=string, required=OFF):**

| Name | Descripción para $fromAI |
|---|---|
| `pregunta_usuario` | `OBLIGATORIO: texto literal de la pregunta del cliente` |
| `categoria_hint` | `Opcional: Showroom | Financiación | Servicio Técnico | Plazos | Garantía | Llamadas | Devoluciones | Distribuidores | Otros` |

**Campo adicional (NO es From AI — es contexto):**

| Name | Value (expresión n8n directa) |
|---|---|
| `session_id` | `={{ $('Normalize Payload').item.json.leadIdentifier }}` |


---

## Tool 3: `consultar_lineas_priorizadas`

**Description del tool:**

```
Devuelve las líneas de producto destacadas este mes según el equipo comercial. Útil al inicio de una conversación para mencionar sutilmente promos si las hay. NO obligatoria invocar siempre.
```

**Parámetros para el LLM:** ninguno.

**Campo adicional (NO es From AI — es contexto):**

| Name | Value (expresión n8n directa) |
|---|---|
| `session_id` | `={{ $('Normalize Payload').item.json.leadIdentifier }}` |

---

## Tool 4: `consultar_url_tienda`

**Description del tool:**

```
Devuelve URL de la tienda online de insumos/repuestos (tintas, films, polvos, vinilos). Usá cuando el cliente pregunta dónde comprar consumibles o repuestos.
```

**Parámetros (todos type=string, required=OFF):**

| Name | Descripción para $fromAI |
|---|---|
| `producto` | `Opcional: nombre o tipo del producto buscado (ej: tinta UV, film DTF)` |
| `categoria` | `Opcional: TINTAS | FILM | POLVO | Vinilo | Papel transfer | Otros` |

**Campo adicional (NO es From AI — es contexto):**

| Name | Value (expresión n8n directa) |
|---|---|
| `session_id` | `={{ $('Normalize Payload').item.json.leadIdentifier }}` |


---

## Tool 5: `buscar_equipo`

**Description del tool:**

```
Busca equipos del catálogo SyS por criterios. Marcas reales: HUENU, DLICAN, TENETH, HANRUN, XENONS, RISO, Sinajet, Konica Minolta (NO Mimaki/Roland). Usá cuando el cliente pregunta por modelos, especificaciones, qué equipo conviene para una aplicación, o cuando ya sabe la tecnología y quiere ver opciones.
```

**Parámetros (todos type=string, required=OFF):**

| Name | Descripción para $fromAI |
|---|---|
| `query_libre` | `Opcional: texto libre del cliente con detalle de lo que busca` |
| `tecnologia` | `Opcional: DTF Textil | DTF UV | UV | Sublimación | Eco-Solvente | Solvente | RISO | IDL Láser | Corte` |
| `linea` | `Opcional: Sinajet | RISO | Konica Minolta IDL | DTF Textil | DTF UV | UV | etc` |
| `marca` | `Opcional: HUENU | DLICAN | TENETH | HANRUN | XENONS | RISO | Sinajet | Konica Minolta` |
| `aplicacion` | `Opcional: nombre de la aplicación del catálogo (ej: Estampado de gorras, Wrap vehicular)` |
| `zona_cliente` | `Opcional: CABA | GBA | Interior` |
| `exclude_models` | `Opcional: lista comma-separated de modelos a excluir para no repetir (ej: 'HR 1602 ES, DLI-1010')` |

**Campo adicional (NO es From AI — es contexto):**

| Name | Value (expresión n8n directa) |
|---|---|
| `session_id` | `={{ $('Normalize Payload').item.json.leadIdentifier }}` |


> ⚠️ Nota: `exclude_models` era originalmente `type: array` y eso rompía Zod. Configurar como `string` y el sub-workflow lo splittea internamente.

---

## Tool 6: `consultar_aplicacion`

**Description del tool:**

```
Dada una descripción libre del cliente ('imprimir gorras', 'wrap vehicular', 'cartelería luminosa'), matchea a una aplicación del catálogo y devuelve tecnologías recomendadas + sustratos típicos. Usá cuando el cliente describe lo que quiere imprimir sin nombrar tecnología.
```

**Parámetros (todos type=string, required=OFF):**

| Name | Descripción para $fromAI |
|---|---|
| `descripcion` | `OBLIGATORIO: texto libre del uso o aplicación que describe el cliente (ej: imprimir gorras, wrap vehicular, banderas)` |
| `sustrato_mencionado` | `Opcional: sustrato/material si el cliente lo mencionó` |

**Campo adicional (NO es From AI — es contexto):**

| Name | Value (expresión n8n directa) |
|---|---|
| `session_id` | `={{ $('Normalize Payload').item.json.leadIdentifier }}` |


---

## Tool 7: `consultar_compatibilidad`

**Description del tool:**

```
Verifica compatibilidad entre un equipo y un sustrato/tinta/cabezal. Usá cuando el cliente pregunta 'este equipo imprime sobre vidrio?', 'esta tinta sirve para mi Mimaki?', etc.
```

**Parámetros (todos type=string, required=OFF):**

| Name | Descripción para $fromAI |
|---|---|
| `tipo_consulta` | `OBLIGATORIO: equipo_sustrato | equipo_tinta | equipo_cabezal` |
| `equipo` | `OBLIGATORIO: modelo o nombre del equipo (ej: DLI-1010, HR 1602 ES, Mimaki UJF)` |
| `elemento` | `OBLIGATORIO: sustrato/tinta/cabezal a verificar compatibilidad` |

**Campo adicional (NO es From AI — es contexto):**

| Name | Value (expresión n8n directa) |
|---|---|
| `session_id` | `={{ $('Normalize Payload').item.json.leadIdentifier }}` |


---

## Tool 8: `consultar_inventario_usados`

**Description del tool:**

```
Consulta equipos Konica Minolta refurbished (usados) disponibles en showroom PEPIRI. Modelos BIZHUB, ACCURIO PRINT, Acurio Press. Usá SOLO cuando el cliente pregunta explícitamente por usados/refurbished/segunda mano, o cuando menciona presupuesto ajustado para producción digital láser. NO ofrecer usados de oficio si el cliente está interesado en equipos nuevos premium.
```

**Parámetros (todos type=string, required=OFF):**

| Name | Descripción para $fromAI |
|---|---|
| `tipo` | `Opcional: BN (blanco y negro) | COLOR` |
| `modelo_query` | `Opcional: texto libre para filtrar por modelo (ej: BIZHUB C450, ACCURIO PRINT)` |

**Campo adicional (NO es From AI — es contexto):**

| Name | Value (expresión n8n directa) |
|---|---|
| `session_id` | `={{ $('Normalize Payload').item.json.leadIdentifier }}` |


---

## Tool 9: `notificar_lead`

**Description del tool:**

```
ÚNICA tool de escritura. Notifica al equipo comercial sobre un lead calificado (mail a info@sistemasysoluciones.com + Telegram interno la agencia). Invocá SOLO cuando tengas los 4 datos obligatorios: nombre + telefono + ubicacion + equipo_o_aplicacion. La tool valida y rechaza el call si falta alguno; en ese caso, pedile al cliente el dato faltante antes de reintentar.
```

**Parámetros (todos type=string, required=OFF):**

| Name | Descripción para $fromAI |
|---|---|
| `nombre` | `OBLIGATORIO: nombre del lead` |
| `telefono` | `OBLIGATORIO: teléfono del lead` |
| `ubicacion` | `OBLIGATORIO: ubicación/localidad del lead (ej: CABA, Mar del Plata, Salta)` |
| `equipo_o_aplicacion` | `OBLIGATORIO: qué equipo o aplicación consultó el cliente` |
| `mail` | `Opcional: mail del lead` |
| `empresa` | `Opcional: empresa si corresponde` |
| `perfil` | `Opcional: Distribuidor | Pyme | Emprendedor | Sin clasificar` |
| `tecnologia_interes` | `Opcional: tecnología de interés si fue identificada` |
| `urgencia` | `Opcional: pasá la string 'true' si el lead expresó urgencia o frustración, sino 'false' o dejá vacío` |
| `notas` | `Opcional: notas adicionales del agente sobre el lead` |

**Campo adicional (NO es From AI — es contexto):**

| Name | Value (expresión n8n directa) |
|---|---|
| `session_id` | `={{ $('Normalize Payload').item.json.leadIdentifier }}` |


> ⚠️ Nota: `urgencia` era originalmente `type: boolean`. Configurar como `string` y el sub-workflow internamente parsea `"true"` → `true`.

---

## Checklist final de configuración v0.2

Por cada tool node:

- [ ] Description del tool completa
- [ ] Workflow seleccionado (no placeholder)
- [ ] Mapping Mode: `Define Below`
- [ ] Attempt to Convert Types: **ON**
- [ ] Cada field: name correcto, type `string`, required **OFF**, value es `={{ $fromAI('name', '...descripción del doc...', 'string') }}`

Cuando termines la config manual, **NO necesitás re-importar**. Solo guardar el workflow (Cmd+S / Ctrl+S) y activarlo.

Después corré el diagnóstico:
```bash
set -a && source .env && set +a && python3 scripts/testing/test-sys-webhook-quick.py
```

---

## Para el futuro: evitar este problema

El patrón "re-import → reset config" es una limitación conocida de n8n cuando los IDs del JSON apuntan a workflows que el ambiente no reconoce hasta que se re-seleccionan. Posibles workarounds futuros:

1. **No regenerar el JSON cuando hay cambios menores** — editar directamente en la UI y exportar a posteriori solo como snapshot/backup.
2. **n8n REST API** (`PATCH /workflows/:id`) para actualizar partes específicas sin re-import. Requiere n8n API key habilitada.
3. **Source-control via git de un export n8n** — exportar después de cada cambio confirmado en UI, no antes.

Para SYS v0.2 vamos con la opción 1: cuando termines la config manual de este doc, ese es el "source of truth" hasta nuevo aviso. Solo regenero el JSON si hay cambios estructurales mayores (nuevo tool, nuevo nodo, etc.).
