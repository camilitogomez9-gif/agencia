# F4 — 9 Tools Sub-Workflows — Setup & Smoke Tests

> **9 workflows nuevos** en `03_workflows/`. Todos siguen el patrón estándar:
> `Execute Workflow Trigger → Validate → Airtable Search → Format Output → Log Postgres → Return`
> (excepto `notificar_lead` que es más compleja: 10 nodos).
>
> **Fecha:** 2026-05-29

---

## Resumen de los 9 tools

| # | Workflow | Operación principal | Credentials requeridos |
|---|---|---|---|
| 1 | `sys-tool-consultar-tecnologia-v1` | Airtable Search Tecnologías | Airtable SYS, Supabase SYS |
| 2 | `sys-tool-consultar-faq-v1` | Airtable List FAQs + scoring | Airtable SYS, Supabase SYS |
| 3 | `sys-tool-consultar-lineas-priorizadas-v1` | Airtable Search Config Mensual | Airtable SYS, Supabase SYS |
| 4 | `sys-tool-consultar-url-tienda-v1` | Airtable Search Insumos | Airtable SYS, Supabase SYS |
| 5 | `sys-tool-buscar-equipo-v1` | Airtable Search Equipos (vista "Para agente") con filtros progresivos | Airtable SYS, Supabase SYS |
| 6 | `sys-tool-consultar-aplicacion-v1` | Airtable List Aplicaciones + matching por keywords | Airtable SYS, Supabase SYS |
| 7 | `sys-tool-consultar-compatibilidad-v1` | Airtable Search Equipos + heurística por tipo | Airtable SYS, Supabase SYS |
| 8 | `sys-tool-consultar-inventario-usados-v1` | Airtable Search Inventario Konica Minolta | Airtable SYS, Supabase SYS |
| 9 | `sys-tool-notificar-lead-v1` | Validate → Gmail + Telegram + Postgres state update | Airtable SYS, **Gmail SYS**, **Telegram Bot Interno**, Supabase SYS |

**Total nodos generados:** 60 (8 tools × 6 nodos + 1 tool × 10 nodos + 2 extras del notificar).

---

## Paso 1 — Importar los 9 JSONs (~15 min)

Por cada archivo en `03_workflows/sys-tool-*-v1.json`:

1. n8n → **Workflows** → **"Import from File"** → seleccionar el JSON.
2. Renombrarlo si querés (los nombres ya están seteados desde el JSON).
3. **NO activar todavía** — primero cablear credentials.

**Tip:** podés importar los 9 de corrido sin abrirlos uno por uno. Después vas a Workflows list y los abrís para cablear.

---

## Paso 2 — Cablear credentials (~20 min)

### En 8 tools (todas menos `notificar-lead`)

Cada una tiene **2 nodos con credentials**:
- **Search/List node** (Airtable) → seleccionar `Airtable SYS` del dropdown.
- **Log to sys_tool_calls** (Postgres) → seleccionar `Supabase SYS` del dropdown.

Probablemente n8n los detecta automáticamente porque ya tenés esas credentials creadas. Solo hay que **confirmar el match** y guardar.

### En `notificar-lead` (más complejo)

Tiene **4 nodos con credentials**:
- **Gmail Send (info@)** → seleccionar `Gmail SYS` (si no existe, créala con OAuth2 + cuenta `info@sistemasysoluciones.com`).
- **Telegram Send (la agencia)** → seleccionar `Telegram Bot Interno` (la compartida de la agencia) + completar `chatId` con el chat ID del grupo SYS (placeholder `<<<COMPLETAR_TELEGRAM_CHAT_ID_SYS>>>`).
- **Update session_state** (Postgres) → `Supabase SYS`.
- **Log to sys_tool_calls** (Postgres) → `Supabase SYS`.

**Si no tenés credencial Gmail SYS:**
1. n8n → Credentials → New → **"Gmail OAuth2"**.
2. Configurar OAuth (necesitás acceso a la cuenta `info@sistemasysoluciones.com` para autorizar; o autorizar con la cuenta si el cliente prefiere que el "From" sea la agencia).
3. Save → seleccionar en el nodo Gmail Send.

**Si no querés agregar Telegram ahora:**
- Deshabilitar (desactivar) solo el nodo `Telegram Send (la agencia)` por ahora. El workflow sigue funcionando — `notificar_lead` manda mail OK aunque Telegram falle (cada nodo crítico tiene `continueOnFail: true`).

---

## Paso 3 — Activar los 9 workflows

Una vez cableadas las credenciales, abrí cada uno y **toggle Active = ON** arriba a la derecha.

> Las tools son **sub-workflows invocadas via Execute Workflow Trigger**, NO via webhook. No necesitan path público. Solo deben estar activos para ser invocables desde el main workflow.

---

## Paso 4 — Smoke tests por tool (~25 min)

Cada tool tiene un smoke test directo en n8n usando el botón **"Execute workflow"** del editor.

### Test 1 — consultar-tecnologia

1. Abrir el workflow `sys-tool-consultar-tecnologia-v1`.
2. Click en el nodo **Execute Workflow Trigger** → tab **"Settings"** o **"Workflow Input Source"** → pegar este JSON como input:
   ```json
   {"tecnologia": "DTF Textil", "aspecto": "", "session_id": "test-001"}
   ```
3. Click **"Execute workflow"** (botón arriba).
4. **Esperado:** Return Output con `status: "RESOLVED"`, `data.descripcion_larga: "Estampado textil..."`, etc.

Repetir con `tecnologia: "Corte"` (debería traer la tecnología recién agregada en re-alineación post-Excel).

### Test 2 — consultar-faq

```json
{"pregunta_usuario": "Hacen cuotas?", "categoria_hint": "Financiación", "session_id": "test-001"}
```
**Esperado:** RESOLVED con `respuesta_corta` empezando por "Sí, ofrecemos financiación...".

### Test 3 — consultar-lineas-priorizadas

```json
{"session_id": "test-001"}
```
**Esperado:** RESOLVED con `mes: "2026-05"`, `lineas_priorizadas: []` (vacío por ahora — Gerente todavía no priorizó nada).

### Test 4 — consultar-url-tienda

```json
{"producto": "tinta UV", "session_id": "test-001"}
```
**Esperado:** RESOLVED con `url_general: "https://www.sistemasysoluciones.com"` + posiblemente `url_producto_especifico` si encontró un insumo UV en Airtable.

### Test 5 — buscar-equipo

```json
{"tecnologia": "DTF Textil", "session_id": "test-001"}
```
**Esperado:** RESOLVED o AMBIGUOUS con `equipo_principal` siendo uno de los HUENU DTF (HR 6002 DT, HR 6004 DT, etc.) y `total_matches: 9` (los 9 equipos DTF Textil del catálogo).

Probar también:
```json
{"marca": "HUENU", "tecnologia": "Solvente", "session_id": "test-001"}
```
**Esperado:** los 5 equipos solvente HUENU.

### Test 6 — consultar-aplicacion

```json
{"descripcion": "imprimir gorras y mochilas", "session_id": "test-001"}
```
**Esperado:** RESOLVED con `aplicacion_match: "Estampado de gorras"` (o "mochilas" según scoring) + `tecnologias_recomendadas: ["DTF Textil"]`.

### Test 7 — consultar-compatibilidad

```json
{"tipo_consulta": "equipo_sustrato", "equipo": "DLI-1010", "elemento": "vidrio", "session_id": "test-001"}
```
**Esperado:** RESOLVED con `compatible: true` (DLI-1010 es UV cama plana que imprime sobre vidrio).

### Test 8 — consultar-inventario-usados

```json
{"tipo": "COLOR", "session_id": "test-001"}
```
**Esperado:** RESOLVED con `equipos_disponibles` listando los 12 modelos COLOR (BIZHUB C 654E, ACCURIO PRINT C3070L, etc.).

### Test 9 — notificar-lead

```json
{"nombre": "Test Smoke", "telefono": "11-9999-0000", "ubicacion": "CABA", "equipo_o_aplicacion": "DTF Textil", "mail": "tu-mail-personal@gmail.com", "perfil": "Pyme", "urgencia": false, "session_id": "test-smoke-001"}
```
**Esperado:**
- Mail recibido en `info@sistemasysoluciones.com` (chequear bandeja) con subject "🟢 Lead nuevo SyS — Test Smoke (CABA)".
- Mensaje Telegram en el chat configurado.
- Fila nueva en Supabase `sys_session_state` con `session_id = "test-smoke-001"` y `etapa = "derivado"`:
  ```sql
  SELECT * FROM sys_session_state WHERE session_id = 'test-smoke-001';
  ```
- Return Output con `status: "RESOLVED"`.

**Si Gmail falla pero todo lo demás OK:** el nodo está marcado `continueOnFail` — la tool retorna RESOLVED igual. Pero el cliente espera recibir el mail, así que es bloqueante para producción. Revisar credencial Gmail.

---

## Paso 5 — Verificar logs en Supabase

Después de los 9 smoke tests:

```sql
SELECT tool_name, status, created_at, input_payload, output_payload
FROM sys_tool_calls
ORDER BY created_at DESC
LIMIT 20;
```

**Esperado:** 9 filas (una por tool ejecutada), todas con `status = 'success'` (o lo que la tool haya devuelto en `status`).

Vista útil para métricas:
```sql
SELECT * FROM sys_tool_metrics_24h;
```

---

## Paso 6 — Conectar tools al Main Workflow (F4.5 — F5)

Una vez que los 9 sub-workflows estén activos y testeados, hay que **conectarlos al `sys-agente-principal-v0.1`** como `toolWorkflow` nodes para que el AI Agent pueda invocarlos.

Hay 2 opciones:

### Opción A — Editar v0.1 manualmente (rápido)

1. Abrir `sys-agente-principal-v0.1` en n8n.
2. Por cada tool, agregar un nodo **"Call n8n Workflow Tool"** (`@n8n/n8n-nodes-langchain.toolWorkflow`).
3. Cablearlo a la entrada `tool` del AI Agent (línea punteada hacia abajo).
4. Configurar cada uno:
   - **Workflow ID:** seleccionar del dropdown el sub-workflow correspondiente (ej. `sys-tool-buscar-equipo-v1`).
   - **Tool Description:** copiar de la spec en `06_docs/tools-spec-v1.md` (ej. para `buscar_equipo`: "Buscá equipos del catálogo de SyS por criterios. Usá esto cuando el cliente pregunta por modelos, especificaciones, qué equipo conviene para una aplicación...").
   - **Fields:** copiar los args declarados en el `inputSource: jsonExample` de cada sub-workflow (el JSON example del trigger).

### Opción B — Generar v0.2 con todos los toolWorkflow ya integrados (siguiente paso)

Yo te genero `sys-agente-principal-v0.2.json` con los 9 toolWorkflow nodes ya creados y posicionados; vos solo confirmás los workflow IDs (selector). Avisame y lo genero.

**Mi recomendación:** Opción B. Más limpio y rápido.

---

## Limitaciones conocidas v1 de las tools

1. **Sin sub-agente gpt-4.1-mini en `buscar_equipo`.** El plan maestro especificaba que si Airtable devolvía >5 matches, un sub-LLM elegía top 3. En v1 simplificamos: devolvemos hasta 3 (principal + 2 alternativas) por orden de match en Airtable. Si en F7 vemos que el agente recibe resultados poco relevantes, agregamos el sub-LLM en v1.1.

2. **Matching de `consultar_aplicacion` y `consultar_faq` es por keywords + boost.** No usa embeddings ni LLM. Funciona bien para queries típicas; si falla mucho, considerar LLM en v1.1.

3. **`consultar_compatibilidad` con `tipo_consulta = equipo_tinta` o `equipo_cabezal` devuelve `compatible: "depende"` y deriva al comercial.** La heurística automática es débil para tintas/cabezales (depende de muchos factores). El agente correctamente le dice al cliente "esto lo confirma el comercial".

4. **`consultar_url_tienda` busca insumos por texto pero NO devuelve URLs específicas** (la mayoría de los insumos del Excel tienen el campo `URL tienda` vacío). Devuelve la URL raíz del sitio. Si el cliente agrega URLs específicas en Airtable, automáticamente las usa.

5. **`notificar_lead` NO escribe en Airtable Leads** (CRM pausado por decisión cliente 2026-05-28). Solo manda mail + Telegram + actualiza `sys_session_state.etapa = 'derivado'`. Cuando el cliente apruebe el upsell CRM, se reactivan los pasos de Airtable Create/Update.

6. **`notificar_lead` necesita Gmail credential.** Pendiente crear/configurar en n8n. Hasta que esté, el workflow falla en el nodo Gmail (pero la tool retorna RESOLVED igual gracias a `continueOnFail: true`).

---

## Próximos pasos

- [ ] Paso 1-3: importar + cablear + activar 9 workflows
- [ ] Paso 4: 9 smoke tests directos
- [ ] Paso 5: verificar logs en Supabase
- [ ] Avisarme — genero `sys-agente-principal-v0.2.json` con tools integrados (Opción B)
- [ ] Paso 6.B: importar v0.2, confirmar workflow IDs en cada toolWorkflow node
- [ ] Smoke test E2E del main workflow con tools (probar `curl` con "Qué es DTF?" y verificar que el agente invoca `consultar_tecnologia` y devuelve la ficha).

Cuando eso pase, F4 + F5 (integración tools al main) están completas y arrancamos **F6 — Integración ManyChat** (la última pieza productiva).
