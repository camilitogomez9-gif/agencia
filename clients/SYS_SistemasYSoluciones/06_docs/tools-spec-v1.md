# Tools Spec v1 — Agente SYS Etapa 2

> **Cliente:** SYS — Sistemas y Soluciones
> **Versión:** v1.1 (actualizado 2026-05-29)
> **Fecha original:** 2026-05-28
> **Total tools:** **9** (8 lectura + 1 notificación)
> **Patrón base:** sub-workflow n8n con `toolWorkflow` node + Airtable + (opcional) sub-agent gpt-4.1-mini
> **Shape de output común:** `{ status, data, message_to_agent, trace_id }`
>
> **Cambios v1 → v1.1 (post-realineación Excel 2026-05-29):**
> - Tool `buscar_equipo`: marcas reales en single-select (HUENU/DLICAN/TENETH/HANRUN/XENONS/RISO/Sinajet/Konica Minolta, NO Mimaki/Roland); filtro nuevo `cabezales_tipo`; vista "Para agente" excluye `Precio USD`.
> - Nueva **Tool 9 `consultar_inventario_usados`**: consulta equipos Konica Minolta refurbished en showroom PEPIRI.
> - Tools `consultar_tecnologia`, `consultar_aplicacion`, `consultar_compatibilidad`: agregadas tecnologías `Solvente` y `Corte`.
>
> **Patrón de configuración (decisión 2026-05-29 — Opción C):** los 4 valores no-secretos (`AIRTABLE_BASE_ID_SYS`, `URL_TIENDA_SYS`, `GMAIL_TO_LEAD_SYS`, `GMAIL_FROM_SYS`) van **hardcoded** directamente en los nodos de cada sub-workflow. Catálogo único: `06_docs/airtable-credentials.md` sección "Valores hardcoded en workflows". Si un valor cambia: search & replace en `03_workflows/*.json`. Secrets (API tokens) sí van en n8n credentials.

---

## Cómo se conectan las tools al AI Agent

En el workflow principal `sys-agente-principal-v1.json`, cada tool aparece como un nodo `@n8n/n8n-nodes-langchain.toolWorkflow` conectado a la entrada `tool` del AI Agent. El nodo apunta a un sub-workflow independiente.

```json
{
  "type": "@n8n/n8n-nodes-langchain.toolWorkflow",
  "name": "buscar_equipo",
  "parameters": {
    "workflowId": "<<<sys-tool-buscar-equipo-v1 workflow ID>>>",
    "description": "Buscá equipos del catálogo de SyS por criterios. Usá cuando el cliente pregunta por modelos, especificaciones o qué equipo conviene para una aplicación.",
    "fields": [
      { "name": "query_libre", "type": "string", "required": false },
      { "name": "tecnologia", "type": "string", "required": false },
      { "name": "linea", "type": "string", "required": false },
      { "name": "aplicacion", "type": "string", "required": false },
      { "name": "ancho_min_mm", "type": "number", "required": false },
      { "name": "ancho_max_mm", "type": "number", "required": false },
      { "name": "zona_cliente", "type": "string", "required": false }
    ]
  }
}
```

---

## Shape común de output (contrato)

Toda tool de SYS devuelve este JSON al AI Agent:

```json
{
  "status": "RESOLVED" | "AMBIGUOUS" | "NOT_FOUND" | "ERROR",
  "data": { /* específico de la tool */ },
  "alternatives": [ /* solo en AMBIGUOUS */ ],
  "message_to_agent": "string corto que guía al LLM",
  "trace_id": "uuid"
}
```

El LLM lee `status` y decide:
- `RESOLVED` → integra `data` natural en respuesta
- `AMBIGUOUS` → presenta `data` principal + ofrece alternatives
- `NOT_FOUND` → comunica que no tiene esa info, deriva
- `ERROR` → "Dame un segundo, lo verifico" + reintenta o deriva

---

## Tool 1: `buscar_equipo`

### Propósito
Buscar equipos del catálogo según criterios técnicos.

### Cuándo el LLM la invoca
- "Qué impresoras DTF tienen?"
- "Modelos de gran formato 1.6m"
- "Qué equipo conviene para estampar gorras?"
- "Mostrame alternativas más económicas a X"

### Input schema
```json
{
  "query_libre": "string opcional — texto del cliente, ej: 'DTF para textil 60cm'",
  "tecnologia": "string opcional — DTF Textil | DTF UV | UV | Sublimación | Eco-Solvente | RISO | IDL Láser | Gran Formato",
  "linea": "string opcional — Sinajet | Konica Minolta IDL | RISO | Mimaki | etc.",
  "aplicacion": "string opcional — nombre de aplicación del catálogo",
  "ancho_min_mm": "number opcional",
  "ancho_max_mm": "number opcional",
  "zona_cliente": "string opcional — CABA | GBA | Interior"
}
```

Al menos uno debe estar. Si todos vacíos → `NOT_FOUND` + guía.

### Output schema (RESOLVED)
```json
{
  "status": "RESOLVED",
  "data": {
    "equipo_principal": {
      "modelo": "DTF-PRO-600",
      "marca": "Mimaki",
      "tecnologia": ["DTF Textil"],
      "linea": "Mimaki",
      "descripcion_corta": "Equipo DTF de producción media...",
      "ancho_max_mm": 600,
      "velocidad_m2h": 12.5,
      "disponibilidad_zona": ["CABA", "GBA"],
      "aplicaciones": ["Estampado de remeras", "Estampado de gorras"]
    },
    "alternatives": [ /* hasta 2 más con mismo shape */ ]
  },
  "message_to_agent": "Equipo principal: DTF-PRO-600. 2 alternativas disponibles.",
  "trace_id": "uuid"
}
```

### Output (NOT_FOUND)
```json
{
  "status": "NOT_FOUND",
  "data": null,
  "message_to_agent": "No hay equipos que matcheen. Sugerí pedir más criterios o derivar.",
  "trace_id": "uuid"
}
```

### Implementación (sub-workflow `sys-tool-buscar-equipo-v1`)

Nodos en orden:

1. **Execute Workflow Trigger** — recibe input args
2. **Code — Validate input**
   ```javascript
   const args = $input.first().json;
   const hasAny = args.query_libre || args.tecnologia || args.linea
                || args.aplicacion || args.ancho_min_mm || args.zona_cliente;
   if (!hasAny) {
     return [{ json: { status: 'NOT_FOUND', message_to_agent: 'No diste criterios. Pedile al cliente más info.', trace_id: $execution.id } }];
   }
   return [{ json: args }];
   ```

3. **Code — Build filterByFormula con relajación progresiva**
   ```javascript
   function buildFilter(args, level) {
     const filters = ['{Status} = "Activo"'];
     if (args.tecnologia)
       filters.push(`FIND("${args.tecnologia}", ARRAYJOIN({Tecnología}))>0`);
     if (args.linea && level <= 2)
       filters.push(`{Línea de Producto} = "${args.linea}"`);
     if (args.aplicacion && level <= 1)
       filters.push(`FIND("${args.aplicacion}", ARRAYJOIN({Aplicaciones compatibles}))>0`);
     if (args.ancho_max_mm && level === 0)
       filters.push(`{Ancho máx (mm)} <= ${args.ancho_max_mm}`);
     if (args.ancho_min_mm && level === 0)
       filters.push(`{Ancho máx (mm)} >= ${args.ancho_min_mm}`);
     if (args.zona_cliente && level <= 2)
       filters.push(`FIND("${args.zona_cliente}", ARRAYJOIN({Disponibilidad zona}))>0`);
     return `AND(${filters.join(', ')})`;
   }

   const formula = buildFilter($input.first().json, 0);
   return [{ json: { formula, level: 0, args: $input.first().json } }];
   ```

4. **Airtable Search** — base `SyS Catalogo`, tabla `Equipos`, view `Para agente`, filterByFormula desde paso 3, maxRecords 10
5. **IF — Count results**:
   - 0 → ir a paso 6 (retry con nivel más permisivo)
   - 1 → ir a paso 8 (formatear como RESOLVED)
   - 2-5 → ir a paso 8 (RESOLVED con alternatives)
   - >5 → ir a paso 7 (sub-agent decide top 3)
6. **Code + Loop** — incrementar level, rebuild formula, retry Airtable hasta level 3
7. **OpenAI Chat (gpt-4.1-mini)** — input: query_libre + lista de N equipos, output: ranking top 3
8. **Code — Format output** al shape del contrato
9. **Postgres Insert** — log a `sys_tool_calls`
10. **Return**

### Validaciones
- `ancho_min_mm > ancho_max_mm` → swap silencioso
- `zona_cliente` no en {CABA, GBA, Interior} → ignorar el filtro

### Manejo de errores
- Airtable timeout (>5s) → return `ERROR`
- Sub-agent gpt-4.1-mini falla → return primeros N sin filtro fino
- En todos los casos: log a `sys_tool_calls`

---

## Tool 2: `consultar_tecnologia`

### Propósito
Ficha técnica de una tecnología del catálogo.

### Cuándo el LLM la invoca
- "Qué es DTF?"
- "Cómo funciona la sublimación?"
- "Diferencia entre DTF y UV"

### Input schema
```json
{
  "tecnologia": "string OBLIGATORIO — DTF Textil | DTF UV | UV | Sublimación | Eco-Solvente | RISO | IDL Láser | Gran Formato",
  "aspecto": "string opcional — descripcion | materiales | restricciones | aplicaciones"
}
```

### Output schema
```json
{
  "status": "RESOLVED",
  "data": {
    "nombre": "DTF Textil",
    "descripcion_larga": "Estampado textil y personalización...",
    "materiales_recomendados": "algodón, poliéster, nylon...",
    "restricciones": "ninguna especial",
    "aplicaciones_tipicas": "Estampado textil, personalización de prendas",
    "equipos_asociados_count": 5,
    "notas_para_agente": "..."
  },
  "trace_id": "uuid"
}
```

### Implementación

1. **Execute Workflow Trigger**
2. **Airtable Search** — tabla `Tecnologías`, filterByFormula `{Nombre} = "{tecnologia}"`, maxRecords 1
3. **IF**:
   - 1 match → `Code — Format` con shape RESOLVED
   - 0 → `Code` con `NOT_FOUND` + sugerencia ("Las disponibles son: DTF Textil, DTF UV, UV, Sublimación, Eco-Solvente, RISO, IDL Láser, Gran Formato")
4. **Postgres Insert** log
5. **Return**

---

## Tool 3: `consultar_aplicacion`

### Propósito
Dada una descripción libre del cliente, matchear a una aplicación del catálogo y devolver tecnologías recomendadas.

### Cuándo el LLM la invoca
- "Necesito imprimir gorras y mochilas"
- "Quiero hacer wrap vehicular"
- "Hago carteles para frentes de comercio"

### Input schema
```json
{
  "descripcion": "string OBLIGATORIO — texto libre del cliente",
  "sustrato_mencionado": "string opcional"
}
```

### Output schema (RESOLVED)
```json
{
  "status": "RESOLVED",
  "data": {
    "aplicacion_match": "Estampado de gorras",
    "categoria": "Textil",
    "tecnologias_recomendadas": ["DTF Textil"],
    "sustratos_tipicos": ["Algodón", "Poliéster"],
    "notas_para_agente": "DTF es ideal por durabilidad..."
  },
  "trace_id": "uuid"
}
```

### Implementación (más complejo, con sub-agent)

1. **Execute Workflow Trigger**
2. **Airtable List** — tabla `Aplicaciones`, todos los records
3. **Code — Build prompt para sub-agent**:
   ```
   "El cliente dijo: '{descripcion}'.
    Estas son las aplicaciones del catálogo:
    - Estampado de remeras (keywords: remeras, camisetas)
    - Estampado de gorras (keywords: gorras, viseras)
    - ...
    Cuál matchea mejor? Devolvé solo el nombre exacto, o 'NONE' si ninguna aplica."
   ```
4. **OpenAI Chat (gpt-4.1-mini)** — temperature 0
5. **IF**:
   - response = "NONE" → return `NOT_FOUND`
   - response es nombre válido → ir a 6
6. **Airtable Search** — tabla `Aplicaciones`, `{Aplicación} = "{nombre}"`, expand `Tecnologías recomendadas` y `Sustratos típicos`
7. **Code — Format**
8. **Postgres Insert** log
9. **Return**

### Validaciones
- `descripcion` vacía → `NOT_FOUND`
- `descripcion` muy larga (>500 chars) → truncar

---

## Tool 4: `consultar_compatibilidad`

### Propósito
Verificar compatibilidad entre un equipo y un sustrato/tinta/cabezal.

### Cuándo el LLM la invoca
- "Mi Mimaki imprime sobre vidrio?"
- "Esta tinta XYZ sirve para tal equipo?"
- "El cabezal Epson DX5 es compatible con el plotter X?"

### Input schema
```json
{
  "tipo_consulta": "string — equipo_sustrato | equipo_tinta | equipo_cabezal",
  "equipo": "string OBLIGATORIO — modelo o nombre del equipo",
  "elemento": "string OBLIGATORIO — sustrato, tinta o cabezal a verificar"
}
```

### Output schema
```json
{
  "status": "RESOLVED",
  "data": {
    "compatible": true,
    "notas": "Sí, este equipo trabaja sobre vidrio con tintas UV. Requiere imprimación previa.",
    "alternativas_si_no_compatible": []
  },
  "trace_id": "uuid"
}
```

### Implementación

1. **Execute Workflow Trigger**
2. **Switch** por `tipo_consulta`:
   - `equipo_sustrato` → buscar equipo en `Equipos`, verificar si `elemento` está en `Sustratos compatibles` (linked)
   - `equipo_tinta` → buscar en `Insumos` con `Categoría=Tinta`, verificar linked Equipos
   - `equipo_cabezal` → buscar en `Cabezales`, verificar linked Equipos
3. **Code — Format**:
   - Si match → `compatible: true`
   - Si no match pero equipo existe → `compatible: false` + buscar alternativas
   - Si equipo no existe → `NOT_FOUND`
4. **Postgres Insert** log
5. **Return**

---

## Tool 5: `consultar_faq`

### Propósito
Responder consultas frecuentes sobre showroom, financiación, plazos, etc.

### Cuándo el LLM la invoca
- "Hacen cuotas?"
- "Tienen showroom?"
- "Garantía?"
- "Servicio técnico?"

### Input schema
```json
{
  "pregunta_usuario": "string OBLIGATORIO — texto literal del cliente",
  "categoria_hint": "string opcional — Showroom | Financiación | Servicio Técnico | etc."
}
```

### Output schema
```json
{
  "status": "RESOLVED",
  "data": {
    "respuesta_corta": "Sí, ofrecemos financiación. Las condiciones se definen personalmente. Dejame tu nombre y teléfono y un representante te explica las opciones.",
    "categoria": "Financiación"
  },
  "trace_id": "uuid"
}
```

### Implementación

1. **Execute Workflow Trigger**
2. **Airtable List** — tabla `FAQs`, view `Activas` (status=Activo)
3. **Code — Match**:
   - Si `categoria_hint` provista, filtrar por categoría
   - Para cada FAQ restante, calcular score: cuántas keywords matchean tokens de `pregunta_usuario`
   - Devolver el de mayor score si score >= 1
4. **IF**:
   - Match → return RESOLVED con `respuesta_corta`
   - No match → return NOT_FOUND
5. **Postgres Insert** log
6. **Return**

### Mejora futura (v2.1)
- Usar gpt-4.1-mini para matching semántico en vez de keyword score.

---

## Tool 6: `consultar_lineas_priorizadas`

### Propósito
Devolver las líneas de producto destacadas este mes.

### Cuándo el LLM la invoca
- 1 vez al inicio de la conversación (opcional)
- Si el cliente pregunta "qué tienen este mes" / "alguna promo"

### Input schema
```json
{}
```
(sin args)

### Output schema
```json
{
  "status": "RESOLVED",
  "data": {
    "mes": "2026-05",
    "lineas_priorizadas": ["RISO", "DTF Textil"],
    "notas_para_agente": "Este mes hay promo en RISO. Mencionar si pregunta por digital alta producción."
  },
  "trace_id": "uuid"
}
```

### Implementación

1. **Execute Workflow Trigger**
2. **Airtable Search** — tabla `Config Mensual`, filterByFormula `{Activo} = TRUE()`, maxRecords 1
3. **IF**:
   - 1 match → format RESOLVED
   - 0 → return RESOLVED con `lineas_priorizadas: []` y warning a log
4. **Postgres Insert** log
5. **Return**

### Cacheable
La response puede cachearse 1 hora en n8n (Redis o file cache) para evitar Airtable calls repetidos.

---

## Tool 7: `consultar_url_tienda`

### Propósito
Devolver URL de la tienda online de insumos, idealmente con deep link.

### Cuándo el LLM la invoca
- "Dónde compro tintas?"
- "Tienen tienda online?"
- "Quiero comprar repuestos"

### Input schema
```json
{
  "producto": "string opcional — ej: 'tinta sublimación Epson'",
  "categoria": "string opcional — Tinta | Film DTF | Polvo DTF | Vinilo | Papel transfer"
}
```

### Output schema
```json
{
  "status": "RESOLVED",
  "data": {
    "url_general": "https://tienda.sistemasysoluciones.com.ar",
    "url_categoria": "https://tienda.sistemasysoluciones.com.ar/tintas",
    "url_producto_especifico": null,
    "stock_disponible": true,
    "mensaje_sugerido_agente": "Podés ver y comprar online en https://tienda.sistemasysoluciones.com.ar/tintas. Si querés que alguien te ayude a elegir, te paso con el equipo."
  },
  "trace_id": "uuid"
}
```

### Implementación

1. **Execute Workflow Trigger**
2. **Switch**:
   - `producto` específico → Airtable Search en `Insumos` con `FIND("{producto}", {Insumo})>0`
   - Solo `categoria` → Airtable Search por categoría, URL del primero
   - Nada → URL raíz `{{URL_TIENDA}}`
3. **Code — Format**
4. **Postgres Insert** log
5. **Return**

---

## Tool 8: `notificar_lead`

### Propósito
**Notifica al equipo comercial** (mail + Telegram) cuando llega un lead calificado.

> ⚠️ **Alcance reducido — decisión cliente 2026-05-28:** sin CRM. La tool **NO escribe en Airtable Leads**. Solo envía mail a `info@sistemasysoluciones.com` + Telegram a la agencia. La versión completa con Airtable Create/Update + lookup de representante queda documentada en la sección "Versión completa con CRM (activación futura)" más abajo, lista para activar cuando el cliente apruebe el upsell (ver `ops/04_upsells/SYS-upsell-crm-leads-2026-05-28.md`).

### Configuración de routing (v1 — Opción A, sin especialización)

Todos los leads se mandan a `info@sistemasysoluciones.com`. NO hay lookup de representante por línea/zona. La tabla Airtable `Representantes` queda como referencia/futuro, pero la tool NO la consulta.

Si en el futuro el cliente pide Opción B (especialización), reactivar los pasos de lookup por zona+línea. La estructura de la tabla Representantes ya está lista para ese caso.

### Cuándo el LLM la invoca
Cuando tiene los 4 datos obligatorios: nombre + telefono + ubicacion + equipo_o_aplicacion.

### Input schema
```json
{
  "nombre": "string OBLIGATORIO",
  "telefono": "string OBLIGATORIO",
  "ubicacion": "string OBLIGATORIO",
  "equipo_o_aplicacion": "string OBLIGATORIO",
  "mail": "string opcional",
  "empresa": "string opcional",
  "perfil": "Distribuidor | Pyme | Emprendedor | Sin clasificar",
  "tecnologia_interes": "string opcional",
  "linea_interes": "string opcional",
  "urgencia": "boolean default false",
  "notas": "string opcional"
}
```

### Output schema (RESOLVED)
```json
{
  "status": "RESOLVED",
  "data": {
    "lead_id": "LEAD-rec123ABC",
    "representante_asignado": "Marcos R.",
    "mail_enviado": true,
    "telegram_enviado": true,
    "fallback_aplicado": false
  },
  "message_to_agent": "Lead registrado y asignado a Marcos R. Confirmá al cliente y cerrá.",
  "trace_id": "uuid"
}
```

### Output (ERROR — validación)
```json
{
  "status": "ERROR",
  "data": null,
  "message_to_agent": "Faltó capturar 'ubicacion'. Pedile al cliente la ubicación antes de invocar de nuevo.",
  "trace_id": "uuid"
}
```

### Implementación VERSIÓN F1 (sin CRM — decisión cliente 2026-05-28)

Sub-workflow `sys-tool-notificar-lead-v1` reducido. Sin Airtable Create/Update, sin lookup de representante.

Nodos en orden:

1. **Execute Workflow Trigger**
2. **Code — Validate** (campos obligatorios)
3. **Code — Derive zona** desde `ubicacion` (informativa, para mail subject)
4. **Code — Derive linea** desde `equipo_o_aplicacion` (informativa, para mail subject)
5. ~~Airtable Search lead existente~~ **OMITIDO**
6. ~~Airtable Create/Update Leads~~ **OMITIDO**
7. ~~Airtable Search Representantes (lookup)~~ **OMITIDO**
8. **Gmail Send Email** a `info@sistemasysoluciones.com` (subject sin link a lead Airtable):
   ```
   From: info@sistemasysoluciones.com
   To:   info@sistemasysoluciones.com  (var GMAIL_TO_LEAD_SYS)
   Subject: 🟢 Lead nuevo SyS — {nombre} ({zona_derivada}) — {linea_derivada || "consulta general"}
   Body:
     Llegó un lead nuevo desde {canal_label}:
     - Nombre:       {nombre}
     - Empresa:      {empresa || "—"}
     - Teléfono:     {telefono}
     - Mail:         {mail || "no provisto"}
     - Ubicación:    {ubicacion}  (zona: {zona_derivada})
     - Consulta:     {equipo_o_aplicacion}
     - Línea inferida: {linea_derivada || "—"}
     - Perfil:       {perfil}
     - Notas:        {notas || "—"}
     - Urgencia:     {urgencia ? "🔴 SÍ" : "no"}

     Conversación session_id: {session_id}

     ---
     Mensaje generado automáticamente por el agente de SyS.
     (CRM tracking deshabilitado en esta etapa — el lead no está registrado en Airtable.)
   ```
9. **Telegram Send** al chat interno la agencia
10. **Postgres Update** `sys_session_state.etapa = 'derivado'`
11. **Postgres Insert** log a `sys_tool_calls`
12. **Code — Return RESOLVED**:
    ```json
    {
      "status": "RESOLVED",
      "data": {
        "destino_notificacion": "info@sistemasysoluciones.com",
        "mail_enviado": true,
        "telegram_enviado": true,
        "lead_id": null,
        "lead_airtable_url": null
      },
      "message_to_agent": "Lead notificado al equipo comercial. Confirmá al cliente y cerrá."
    }
    ```

### Implementación VERSIÓN COMPLETA (activación con upsell CRM — futura)

> Esta es la versión "ideal" del sub-workflow, que se activa cuando el cliente apruebe el upsell CRM (`ops/04_upsells/SYS-upsell-crm-leads-2026-05-28.md`). Documentada para evitar re-trabajo cuando se reactive.

Nodos en orden:

1. **Execute Workflow Trigger**
2. **Code — Validate**:
   ```javascript
   const args = $input.first().json;
   const required = ['nombre', 'telefono', 'ubicacion', 'equipo_o_aplicacion'];
   const missing = required.filter(f => !args[f] || args[f].trim() === '');
   if (missing.length > 0) {
     return [{ json: { status: 'ERROR', message_to_agent: `Faltó capturar: ${missing.join(', ')}. Pedile al cliente.`, trace_id: $execution.id } }];
   }
   return [{ json: args }];
   ```

3. **Code — Derive zona** desde `ubicacion`:
   ```javascript
   const u = args.ubicacion.toLowerCase();
   let zona = 'Interior';
   if (u.includes('caba') || u.includes('capital') ||
       u.includes('buenos aires capital') || u.includes('ciudad de buenos aires'))
     zona = 'CABA';
   else if (u.includes('gba') || u.includes('gran buenos aires') ||
            u.includes('conurbano') || u.match(/(zona norte|zona sur|zona oeste)/))
     zona = 'GBA';
   args.zona_derivada = zona;
   return [{ json: args }];
   ```

4. **Code — Derive linea** desde `equipo_o_aplicacion` o `tecnologia_interes`:
   ```javascript
   const mapping = {
     'dtf textil': 'DTF Textil',
     'dtf uv': 'DTF UV',
     'sublimacion': 'Sublimación',
     'sublimación': 'Sublimación',
     'eco-solvente': 'Eco-Solvente',
     'riso': 'RISO',
     'konica': 'Konica Minolta IDL',
     'sinajet': 'Sinajet',
     // ...
   };
   const texto = (args.tecnologia_interes || args.equipo_o_aplicacion || '').toLowerCase();
   args.linea_derivada = Object.entries(mapping).find(([k,v]) => texto.includes(k))?.[1] || null;
   return [{ json: args }];
   ```

5. **Airtable — Buscar lead existente** (idempotencia):
   - Filter: `AND({Subscriber ID} = "{subId}", {Canal} = "{canal}", {Status} = "En conversación", IS_AFTER({Última actividad}, DATEADD(NOW(), -30, 'minutes')))`
   - Si existe → ir a paso 7 (UPDATE)
   - Si no → ir a paso 6 (CREATE)

6. **Airtable Create** — tabla `Leads` con todos los campos
7. **Airtable Update Lead** con `Notificación enviada = true`, `Fecha derivación = NOW()`, `Status = "Derivado"`
   - NOTA (Opción A): NO se asigna representante específico — todos los leads van a `info@sistemasysoluciones.com`. El campo `Representante asignado` queda vacío o con un rep "Equipo Comercial" como referencia.
   - Si en el futuro se activa Opción B, agregar acá los pasos de lookup en tabla Representantes.

8. **Gmail Send Email** (Opción A — destino único):
    ```
    From: info@sistemasysoluciones.com  (configurado en n8n Gmail credential)
    To:   info@sistemasysoluciones.com  (var GMAIL_TO_LEAD_SYS)
    Subject: 🟢 Lead nuevo SyS — {nombre} ({zona_derivada}) — {linea_derivada || "consulta general"}
    Body:
      Llegó un lead nuevo desde {canal_label}:

      - Nombre:       {nombre}
      - Empresa:      {empresa || "—"}
      - Teléfono:     {telefono}
      - Mail:         {mail || "no provisto"}
      - Ubicación:    {ubicacion}  (zona: {zona_derivada})
      - Consulta:     {equipo_o_aplicacion}
      - Línea inferida: {linea_derivada || "—"}
      - Perfil:       {perfil}
      - Notas:        {notas || "—"}
      - Urgencia:     {urgencia ? "🔴 SÍ" : "no"}

      Ver lead en Airtable: https://airtable.com/{base}/{tableLeads}/{record_id}
      Conversación session_id: {session_id}

      ---
      Mensaje generado automáticamente por el agente de SyS.
    ```

9. **Telegram Send** al chat interno la agencia:
    ```
    🟢 Lead SYS: {nombre} ({zona_derivada})
    Canal: {canal_label} | Consulta: {equipo_o_aplicacion}
    Urgencia: {urgencia ? "🔴 SÍ" : "no"}
    ```

10. **Postgres Update** `sys_session_state` SET `etapa = 'derivado'`, `ultima_actividad = NOW()`
11. **Postgres Insert** log a `sys_tool_calls`
12. **Code — Return RESOLVED** con shape del contrato:
    ```json
    {
      "status": "RESOLVED",
      "data": {
        "lead_id": "LEAD-{recordId}",
        "destino_notificacion": "info@sistemasysoluciones.com",
        "mail_enviado": true,
        "telegram_enviado": true
      },
      "message_to_agent": "Lead registrado y notificado al equipo comercial. Confirmá al cliente y cerrá."
    }
    ```

### Validaciones
- Campos obligatorios vacíos → ERROR + no escribe nada
- Mail con formato inválido (regex `/^[^@]+@[^@]+\.[^@]+$/`) → registrar igual, log warning
- Airtable Create falla → ERROR + Telegram alert (no mandar mail si no se creó record)

### Manejo de errores
- Gmail falla → log ERROR pero mantener Airtable record + Telegram alert al equipo
- Telegram falla → log warning (no es crítico)
- Postgres state update falla → log warning, conversación sigue

### Idempotencia (importante)
Si el LLM invoca `notificar_lead` dos veces seguidas (puede pasar):
- Paso 5 detecta lead existente activo en últimos 30 min
- UPDATE en vez de CREATE
- No reenviar mail (verificar `Notificación enviada = true`)

---

## Resumen ejecutivo de tools

| Tool | Tipo | Latencia esperada | Tablas que toca | Output críticos |
|---|---|---|---|---|
| 1. buscar_equipo | Lectura | <800ms | Equipos | RESOLVED / AMBIGUOUS / NOT_FOUND |
| 2. consultar_tecnologia | Lectura | <300ms | Tecnologías | RESOLVED / NOT_FOUND |
| 3. consultar_aplicacion | Lectura + LLM | <1500ms | Aplicaciones + (gpt-4.1-mini) | RESOLVED / NOT_FOUND |
| 4. consultar_compatibilidad | Lectura | <500ms | Equipos + Sustratos/Insumos/Cabezales | RESOLVED / NOT_FOUND |
| 5. consultar_faq | Lectura | <400ms | FAQs | RESOLVED / NOT_FOUND |
| 6. consultar_lineas_priorizadas | Lectura | <200ms (cache) | Config Mensual | RESOLVED |
| 7. consultar_url_tienda | Lectura | <300ms | Insumos | RESOLVED |
| 8. notificar_lead | Escritura | <2000ms | Leads + Representantes + (Gmail + Telegram) | RESOLVED / ERROR |

**Latencia total worst-case** de un turno con 2 tools: ~3.5s + LLM ~5s = ~8.5s. Bien por debajo del timeout 20s.

---

## Convenciones de logging (todas las tools)

Cada sub-workflow termina con un nodo `Postgres > Execute Query`:

```sql
INSERT INTO sys_tool_calls (
  session_id, lead_airtable_id, tool_name,
  input_payload, output_payload, status,
  error_message, duration_ms
) VALUES (
  $1, $2, $3, $4::jsonb, $5::jsonb, $6, $7, $8
);
```

Donde:
- `$1` = session_id (del payload entrante)
- `$2` = lead_airtable_id (si la tool lo conoce, sino NULL)
- `$3` = nombre de la tool (hardcoded en cada sub-workflow)
- `$4` = JSON de los args con que se llamó
- `$5` = JSON del output devuelto al LLM
- `$6` = `success` | `error` | `not_found` | `timeout` | `ambiguous`
- `$7` = mensaje de error si status = error/timeout
- `$8` = duración de la ejecución del sub-workflow

---

## Tool 9: `consultar_inventario_usados` (NUEVA v1.1)

### Propósito
Consultar equipos Konica Minolta refurbished (usados) disponibles en showroom PEPIRI. Ofrecer opción de menor presupuesto para producción digital láser.

### Cuándo el LLM la invoca
- Cliente pregunta explícitamente por "equipos usados / refurbished / segunda mano".
- Cliente menciona presupuesto ajustado para producción digital láser (Konica Minolta).
- Cliente pregunta específicamente por modelos BIZHUB, ACCURIO PRINT, ACURIO PRESS.

**NO invocar** cuando el cliente está interesado en líneas nuevas premium o no es relevante a digital láser.

### Input schema
```json
{
  "tipo": "string opcional — BN | COLOR",
  "modelo_query": "string opcional — texto libre, ej: 'BIZHUB C450' o 'Acurio Press'"
}
```

### Output schema (RESOLVED)
```json
{
  "status": "RESOLVED",
  "data": {
    "equipos_disponibles": [
      {
        "modelo": "BIZHUB 450i",
        "tipo": "BN",
        "copias_total": 13746,
        "stock": 17,
        "ubicacion": "PEPIRI",
        "accesorios": "TOP(Dual Scan),Duplex,PFU(2 Tray),Bypass,Printer Controller(Internal),NIC,SCANNER"
      }
      // ... más equipos
    ],
    "total_modelos": 21,
    "total_unidades": 65
  },
  "message_to_agent": "Hay 21 modelos refurbished disponibles en PEPIRI. Ofrecele al cliente coordinar visita al showroom para verlos."
}
```

### Implementación sub-workflow `sys-tool-consultar-inventario-usados-v1`

1. **Execute Workflow Trigger**
2. **Code — Build filterByFormula** desde args:
   ```javascript
   const args = $input.first().json;
   const filters = ['{Estado} = "Disponible"', '{Stock} > 0'];
   if (args.tipo) filters.push(`{Tipo} = "${args.tipo}"`);
   if (args.modelo_query) filters.push(`FIND(LOWER("${args.modelo_query.toLowerCase()}"), LOWER({Modelo})) > 0`);
   return [{ json: { formula: `AND(${filters.join(', ')})` } }];
   ```
3. **Airtable Search** — tabla `Inventario Konica Minolta`, view `Para agente` (sin Precio USD), maxRecords 25
4. **Code — Format output** según contrato. Agregar `message_to_agent` sugiriendo "coordinar visita al showroom PEPIRI" o "el comercial cotiza caso por caso".
5. **Postgres Insert** log a `sys_tool_calls`
6. **Return**

### Output NOT_FOUND
Si el filtro no encuentra match (ej: cliente pidió tipo=COLOR pero solo hay BN disponibles), devolver:
```json
{
  "status": "NOT_FOUND",
  "message_to_agent": "No hay equipos refurbished disponibles con esos criterios. Sugerí derivar al comercial para que confirme próximas reposiciones."
}
```

### Validaciones
- Si todos los args son null → retornar TOP 5 equipos (no NOT_FOUND, devolver muestra).
- Si `tipo` no es BN ni COLOR → ignorar el filtro y devolver todo lo disponible.

### Restricciones
- Esta tool NUNCA devuelve `Precio USD` (no está en la vista "Para agente"). El comercial cotiza usados caso por caso.
- El agente NUNCA menciona el precio (regla general anti-precios) — solo dice "el comercial te cotiza según el modelo y stock disponible".

---

## Checklist de implementación (Fase 4 del roadmap)

Para cada tool (de las 9 totales), los pasos son:
- [ ] Crear sub-workflow en n8n con naming `sys-tool-{tool_name}-v1`
- [ ] Implementar nodos según spec
- [ ] Configurar credenciales Airtable + Supabase
- [ ] Test manual: input válido → output esperado
- [ ] Test manual: input inválido → output ERROR controlado
- [ ] Test manual: Airtable down (simular) → output ERROR
- [ ] Exportar JSON y guardar en `clients/SYS_SistemasYSoluciones/03_workflows/`
- [ ] Documentar el workflow ID en el doc principal `sys-agente-principal-v1.json`
- [ ] Conectar como `toolWorkflow` al AI Agent del main workflow
