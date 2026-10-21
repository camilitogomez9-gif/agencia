# Prompt para continuar — HPF migración GHL, tramo final de L7

Copiá todo lo que sigue como primer mensaje de la sesión nueva.

---

Continuamos la migración de Happy Flops de `[n8n + Airtable + Kommo]` a `[n8n + GHL]`.
Ya está construida y corroborada toda la infraestructura; faltan tres cosas puntuales.
Leé primero `clients/HPF_HappyFlops/03_workflows/ghl/README.md` y
`clients/HPF_HappyFlops/07_testing/evidencia-migracion/L2-informe-primitivas.md`, que
tienen los contratos y las trampas ya descubiertas.

## Regla 0 — producción es intocable

Los 8 workflows del bot vivo en `dev[TU-INSTANCIA-N8N]` son **sólo lectura**. Ni un nodo,
ni activar, ni desactivar. Están congelados con sha256 en
`clients/HPF_HappyFlops/03_workflows/base-prod-2026-08-06/`. Antes y después de cada
tanda de trabajo:

```bash
python3 scripts/utilities/hpf-congelar-base.py --verificar
```

Kommo y Airtable también son sólo lectura. En GHL sólo se agrega; cualquier cambio
destructivo se propone y se espera OK.

## Lo que ya está hecho y corroborado

Siete workflows nuevos, activos en `dev[TU-INSTANCIA-N8N]`, cada uno con su generador
reproducible en `scripts/generators/` y su gate en `scripts/testing/`:

| workflow | id | gate |
|---|---|---|
| W0 · GHL Client | `VK4M7VQm8CMefbty` | `hpf-l3-w0.py` → 14/14 |
| W1 · Inbound | `nA14dNwJ7VS3YMYr` | `hpf-l6-w1.py` → 8/8 · 7/7 aristas |
| W2 · Salida | `MdbOREN56lfQTYlM` | `hpf-l5-w2.py` → 6/6 |
| W3 · Catálogo | `vSLHOawn2bFVXyOK` | `hpf-l5-w3.py` → 8/8 |
| W4 · CALCULADORA | `psGRDByGNjHQ2DVT` | `hpf-l7-tools.py` → 8/8 |
| W5 · ATENCION | `mmo29FTvIquxksWV` | (mismo gate) |
| W6 · Conversación | `cNmJCP2qVhdtfCH0` | sin gate todavía ← tarea 1 |

Flujo: `W1 (entrada, idempotencia, identidad, gates, debounce) → W6 (Router + agentes)
→ W2 (burbujas a GHL)`. W0 es el único que habla con GHL; W3/W4/W5 son tools.

**Ya funciona end-to-end**: un POST al webhook de W1 termina en 3 burbujas dentro de GHL.

Catálogo: 65/65 fichas con asset en el custom object `custom_objects.fichas`
(`6a7506747dddfe7e35848ee8`), cacheadas en la tabla Postgres `hpf_fichas`.

Prompts extraídos del grafo congelado con sha256 en
`clients/HPF_HappyFlops/04_agents/base-prod-2026-08-06/` + `MANIFIESTO.json`.
Verificar con `python3 scripts/utilities/hpf-extraer-agentes.py --verificar`.

Registro de puntos: `00_migracion_ghl/06_registro/puntos.jsonl`, 54 puntos, gate
aritmético 395/395 (`python3 scripts/testing/hpf-registro.py --cobertura`).

## Las tres tareas

### 1. Runner de paridad conversacional (lo más importante)

Existe un oráculo congelado: `clients/HPF_HappyFlops/07_testing/oraculo/` — 10
transcripts reales de Kommo, 269 turnos, con `INDICE.json`.

Hay que construir un runner que reproduzca esos turnos contra el webhook de W1 y compare
contra el oráculo. Cosas a tener en cuenta:

- **W1 responde temprano** (un ack apenas pasa idempotencia). La evidencia NO está en la
  respuesta HTTP: está en el `runData` de la ejecución, nodo `Evidencia del turno`, que
  trae `{step, tools_usadas, partes_enviadas, enviados[]}`. Leerla con
  `GET /api/v1/executions?workflowId=nA14dNwJ7VS3YMYr&limit=N&includeData=true`.
- Mandar `debounce_seg: 0` en el payload de test, si no cada turno espera 50 s.
- Cada conversación necesita su `sessionId` propio y limpieza previa de
  `n8n_chat_histories` para ese `session_id`, o arrastra memoria entre corridas.
- Casos borde que hay que cubrir además del oráculo: evento "Otros", "todos los
  productos", producto no mostrado, mínimo no alcanzado (35 cilindros), audio, imagen de
  producto, comprobante de pago, PDF, fuera de horario, lead en producción, lead perdido,
  mensaje duplicado, ráfaga.

**Tripwire, no negociable:** si a los 20 casos el pase está por debajo del 60%, parar y
reportar el número crudo antes de escribir un solo fix.

**Orden de diagnóstico ante una falla de paridad:** primero la plomería (catálogo
incompleto, CF rechazado, tool devolviendo error como texto), recién después el prompt.
El historial de este cliente tiene un "paste parcial" de prompt que costó semanas por
invertir ese orden.

### 2. Rama de imagen (Recolector1)

Hoy W6 sólo tiene el camino de texto. Falta:

- `Analyze image1` (clasificador de producto, gpt-4o, 3.025 chars) →
  `llm-analyze-image1.md` en la carpeta de prompts congelados.
- `Analyze image2` / `Analyze image3` (detector de comprobante de pago, 1.383 chars cada
  uno, idénticos entre sí).
- `transcribe voice` (whisper, `language: es`, sin prompt).
- `Recolector1` con el prompt **parchado**:
  `clients/HPF_HappyFlops/04_agents/agente-recolector1-imagen-parchado.md`.
  Decisión ya firmada: lleva la **CALCULADORA real (W4)**, no el `toolCalculator`
  genérico que tenía en producción. El parche tiene 4 cambios documentados en su
  encabezado; regenerable con `scripts/utilities/hpf-parchar-recolector1.py`.
- El flujo de comprobante de pago del origen: si el lead **no** está en `En Producción`
  → mover a `Pago Confirmado` + alerta Telegram; si **sí** está → `pago liquidación` +
  alerta. Fuera de horario → mensaje de "Foto Vacaciones".

W1 ya clasifica el tipo (`texto` / `audio` / `imagen` / `pdf`) en `Normalizar entrada` y
lo pasa en el contexto; falta que W6 ramifique por ahí.

### 3. Helpers sin cablear

- **Canonicalizador de nombres de producto** (`llm-message-a-model.md`, gpt-4.1-mini,
  `jsonOutput`, 2.658 chars). En el origen va entre `AI Agent Products` y la consulta al
  catálogo: mapea lo que dice el cliente a los nombres cerrados del catálogo. Sin él,
  W3 recibe los nombres crudos del LLM y matchea peor.
- **Gate de intención de cotizar** (`llm-necesita-respuesta-especial.md`, **gpt-5-mini**,
  5.491 chars). Devuelve `{response: "sí"|"no"}`. En el origen filtra ANTES del
  Recolector: `sí` = pedido de cotización o pregunta de negocio → Recolector; `no` =
  pregunta de precio unitario o relleno ("dale", "ok") → respuesta canónica sin invocar
  al agente caro. **Hoy todo `step_4` va directo al Recolector**, que es un DELTA no
  declarado: hay que cablearlo o registrarlo como decisión.

## Cómo se trabaja acá

**Loop, no lista.** Cada punto: determinar → implementar → ejecutar contra el sistema
real → evaluar el assert → sólo entonces avanzar. Si falla: (a) endpoint/parámetro
alternativo, (b) mover la capacidad fuera de GHL y anotar `REEMPLAZAR`, (c) `BLOQUEADO`
con pregunta concreta. **Nunca** dar por bueno algo porque el nodo quedó verde.

**La evidencia es el read-back, no el 2xx.** Todo caso escribe request+response crudos en
`07_testing/evidencia-migracion/`.

**Barrido de regresión** después de cada bloque: re-correr *todos* los gates, no sólo el
que tocaste. Ya cazó un test frágil que pasaba por casualidad.

## Trampas ya descubiertas — no re-descubrirlas

**GHL**
- Sin `User-Agent` explícito, Cloudflare devuelve `403 error_code 1010`. Aplica también
  al CDN de la Media Library.
- `POST /opportunities/` es el find-or-create autoritativo: si el contacto ya tiene
  oportunidad devuelve `400 OPPORTUNITY_NO_DUPLICATE` con `meta.existingId`, **sin lag**.
  `/opportunities/search` sí tiene lag de indexación — no confiar después de escribir.
- `/opportunities/search` acepta **sólo snake_case** (`location_id`, `contact_id`);
  camelCase da 422.
- `PUT /objects/{key}/records/{id}` necesita `locationId` **en la query**: en el body da
  422, sin él 404. Y devuelve 2xx igual — hay que releer para saber si escribió.
- Los CF aceptan valores fuera del picklist y **ignoran en silencio** ids desconocidos
  devolviendo 200. Por eso W0 valida las claves antes del PUT.
- Un contacto = **una** oportunidad, aunque esté `lost`. `allowDuplicateOpportunity` está
  en `false` y no es alcanzable: no está en la UI y el PIT no tiene `locations.write`
  (401). Decisión cerrada en `PM-IDN-03-decision.md` — W1 lo resuelve reciclando la
  oportunidad, y se adapta solo si algún día se activa el flag.

**n8n**
- Un workflow devuelve la salida del **último nodo ejecutado**. Si la rama termina en una
  salida de `IF` sin nada conectado, devuelve `[]` y el llamador se corta en silencio con
  la ejecución en verde. Todos los sub-workflows llevan un `Devolver al llamador` (noOp).
- Un nodo con **0 filas no emite** y corta la cadena → `alwaysOutputData` en los `SELECT`
  que pueden dar vacío.
- n8n **trunca los mensajes de error quedándose con el final** (~130 chars): lo accionable
  va primero y corto.
- El detalle del error **no llega al cuerpo del webhook** (responde un genérico
  `Workflow execution failed`): está en el `runData` de la ejecución.
- `splitInBatches` v3: salida 0 = *done*, salida 1 = *loop*.

## Entorno

- Repo: `/Users/camilo/Downloads/camilo-workspace`
- Credenciales en `.env` (gitignored): `GHL_API_KEY`, `GHL_LOCATION_ID`,
  `HPF_N8N_API_KEY`, `HPF_WEBHOOK_AUTH_HEADER_NAME/VALUE`, `AIRTABLE_PAT_HPF`.
- ⚠️ **`HPF_N8N_API_KEY` vence el 2026-08-13 y no se renueva.**
- n8n: `https://dev[TU-INSTANCIA-N8N]` (API) · `https://[TU-INSTANCIA-N8N]`
  (webhooks). Los webhooks de prueba llevan header auth; el valor tiene un espacio, así
  que `source .env` lo parte — leer el `.env` con Python, no con `source`.
- GHL location `onRwi0ZF4uYi0Lp6GAbE`, pipeline `RMnhLPqtXoWUBGZ0gvbh` (13 etapas).
- Contacto de prueba `3tzzBVjsKlOF2RJjKNOL` (tag `lead_prueba`), oportunidad
  `vzYAb3P86uJ08CI9jKyV`.
- La WABA no está conectada: los mensajes quedan en `status: "failed"` pero se persisten
  con `body` y `attachments` exactos, que es la evidencia que usamos.

## Fuera de alcance

Todo lo que esté bajo `00_migracion_ghl/03_arquitectura_ghl/` y `04_guia_migracion/`, y
cualquier `hpf-inbound-handler-*.json`: es del intento anterior, descartado. No usarlo
como referencia. `happyflops-main-v3.json` tampoco — el grafo bueno está en
`base-prod-2026-08-06/`.

Arrancá por la tarea 1.
