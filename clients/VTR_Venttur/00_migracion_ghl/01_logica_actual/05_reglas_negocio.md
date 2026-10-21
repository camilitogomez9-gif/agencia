# 05 — Reglas de Negocio

> **Reescrito 2026-07-24** con los inputs completos de Etapa 0 (14 workflows n8n + snapshot de datos de las 5 plataformas + 6 CSVs Airtable + system prompt del agente + schema Supabase). Supera la versión de mayo 2026, que se generó con inputs parciales y contenía errores materiales (ver "Correcciones vs. versión mayo 2026" abajo / doc 06).
>
> **Fuentes primarias usadas:** `agente-venttur-system-prompt-EXTRAIDO-2026-07-24.md` (system prompt inline del nodo `Agente IA WPP`, ~39K chars) · `wf-venttur-main.json` (`k3aivKSP67S97IHn`) · `wf-meta-capi-venttur.json` (`z98w2yWVEMOfifMl`) · `wf-capi-registro-folio.json` (`9yCbynoKDt9hgiBq`) · `wf-outreach-form-meta.json` (`CUuFxbst3iHpgeXS`) · `wf-rescate-post-link.json` (`mkEP1qFN7MVb9qP0`) · `wf-estado-lead.json` (`b52CUYEkI2Ah3Xj6`) · `wf-estado-interrumpida.json` (`H6qYB3Oj97bxaTCX`) · `wf-resumen-etiquetas-seguimientos.json` (`DyrDumQgb6S4zHsS`) · `wf-actualizar-link-enviado.json` (`gRSMjzxggA4UePjz`) · `wf-seguimiento-agenda.json` (`DZlSEQS5qzX1Y01K`) · `wf-confirmacion-agenda.json` (`2PSekVBxarsrnVBu`) · `wf-formulario-clientify.json` (`ZB6erhWicZmDfC4I`) · `wf-crear-contacto-clientify-airtable.json` (`cZUNKQyZNOHy5twQ`) · `wf-correo-semanal.json` (`BrFfQyDfamdUzq64`) · `template-texts-canonical.md` · `manychat-flows-content-2026-07-20.md` · `manychat-snapshot-2026-05-13.md` · `supabase-queries-venttur.md` · CSVs `programas-capi / folios-capi / mensajes-anuncios / leads / reporte-semanal`.

### Correcciones vs. versión mayo 2026

- **❌ MAYO decía "No hay agente conversacional IA. Sistema puramente reactivo (tracking + CRM + rescate)".** ✅ FALSO. El **corazón del sistema es un AI Agent conversacional llamado "Mauricio"** (gpt-4o, temp 0) que vive inline en el nodo `Agente IA WPP` del main. Toda la sección 3 de este doc es nueva. Cualquier afirmación de mayo de que "no hay agente" se corrige explícitamente.
- **❌ MAYO: Rescate Post-Link "diseñado, no activado / vive en ManyChat".** ✅ En producción como workflow n8n `wf-rescate-post-link` (2 fases 45min+24h) + memoria sintética en Postgres. El flow viejo de ManyChat quedó reemplazado.
- **❌ MAYO: Outreach proactivo WA "no implementado".** ✅ En producción (`wf-outreach-form-meta`), tri-toque disparado desde Google Sheets sync de Meta Lead Ads.
- **🆕 NUEVO: Estado de lead** (2 workflows: "Contestó" + "barrido interrumpida").
- **🆕 NUEVO: Nurturing 4-toques por programa** (6 flows ManyChat, delays 0/1/3/5d).
- **📊 Data model ampliado:** Airtable Leads tiene **30 columnas** (mayo documentó ~9). Clientify volumen real: 6.968 contactos / 2.338 deals / 266 companies.
- **CTWA CONFIRMADA:** la rama Click-to-WhatsApp del CAPI existe y está cableada — pero hardcodea `{Programa}='BS'` (no ramifica por `programa_wpp` como se asumía).
- **Programas:** 6 conceptuales en el agente vs **4 códigos CAPI / 2 pixels reales** (mismatch documentado en §2).
- **Quirk MX 52→521 en `session_id`:** confirmado y ya backfilleado en producción (la versión de mayo asumía "teléfono sin +" a secas).

---

## 🆕 Validación con el cliente — 2026-08-17 (Etapa 2)

> Respuestas de **Mauricio García** (revisadas sobre el borrador de Max) al cuestionario
> `02_validacion_cliente/cuestionario-venttur-2026-07-24.md`. Lo de acá abajo **supera** al cuerpo de
> este documento donde haya conflicto. Mapeo completo a las preguntas internas en
> `02_validacion_cliente/preguntas-cierre-2026-07-24.md` (A1..A11). Lo que quedó abierto está en
> `02_validacion_cliente/puntos-abiertos-ronda-2-2026-08-18.md`.
>
> **Fecha objetivo de cutover confirmada: 15 de septiembre de 2026.**

### Lo que cambia en las reglas de negocio

**1. 🆕 REGLA NUEVA Y DURA — el agente NUNCA asume el programa.**
Textual del cliente: *"El agente NO debe asumir el programa, ni siquiera cuando el origen parezca
evidente. Siempre debe preguntar y hacer descubrimiento de la necesidad real del lead."*
Razón: alguien puede entrar por un anuncio de Internados buscando un año académico o información para
un hijo de otra edad; si el bot lo da por hecho, el asesor recibe un lead mal calificado.
Esto **separa en dos** lo que hoy es una sola regla:

| Función | Fuente del dato | Le pregunta al lead |
|---|---|---|
| Medición y atribución | Payload de referral de Meta, automático | No |
| Ruteo, calendario y asesor | **Lo que diga la persona** | Sí, siempre |

Beneficio que el cliente nombra: activar campañas de programas nuevos deja de requerir cambios.

**2. 🆕 REGLA NUEVA — los destinos no son datos estructurados.**
*"Si un lead menciona un destino específico, se registra como comentario o nota en el contacto. No
queremos que el destino sea un campo estructurado ni que se confunda con el programa."*
→ Consecuencia directa: `Francia` sale del enum de programas. Y por extensión, cualquier otro país.

**3. §2 (programas) se reescribe sobre la taxonomía de 8.** El mismatch documentado
("6 conceptuales vs 4 códigos CAPI vs 2 pixels") se re-encuadra: los pixels faltantes **no son un
gap**, es que esos programas no tienen campaña activa. Hoy solo Internados pauta. El pixel de AA
Familiar queda como **legado** (configurado, sin campaña). Requisito: capacidad de medición por
programa desde el día uno, aunque no se use todavía.

**4. Regla 10 (precio) — el cambio está preparado pero BLOQUEADO.**
El pasaje de "prohibido dar cifras" a "rango + cierre con fecha concreta" no se activa hasta que el
cliente confirme los rangos. Solo tenemos 5 de 8 programas y hay conflicto en Internados
(50-100k vs 50-130k). Es política comercial, no configuración.

**5. §4.3 / §5 (cadencia) — el tope de 2 toques NO tiene OK explícito todavía.**
La respuesta del cliente fue *"Se deben implementar cambios, ver Reporte la agencia PDF"*, que delega en la
auditoría de Max pero no aprueba el cambio de política. La pregunta que pedía el OK expreso nunca le
llegó (ver nota abajo). Se pide por escrito antes del cutover. La prioridad entre programas cuando el
lead se interesa en varios tampoco se preguntó, y ahora hay que **redefinirla entera** (8 programas,
3 sin drip), no solo confirmarla.

**6. §10 (reporting) — definiciones oficiales.**

| Métrica | Definición del cliente |
|---|---|
| Lead calificado | Continúa la conversación, contesta favorablemente al perfil buscado y muestra interés real. **No basta con responder una vez.** |
| Cita | **Solo citas agendadas.** La asistencia la mide Max aparte y sale del reporte. |
| Conversación no continuada | Deja de contestar el seguimiento; se marca al agotarse la secuencia, **~5 días**. |

⚠️ La tercera choca con el barrido de 24 h que corre hoy en producción. Ver doc 03.

**7. §9.4 / §9.6 (confirmación de cita) — pasa de "regla incumplida" a requisito firme.**
Todos los leads reciben confirmación, sin importar el asesor, y además recordatorios previos. Con
Diego fuera del ruteo, el path roto de Diego se **elimina** y solo queda reparar el de Andrés.

**8. Regla de negocio nueva sobre el canal: un solo número.**
Hoy conversación y recordatorios salen de números distintos (ManyChat y Clientify). El estado destino
es uno solo para todo.

---

### ⚠️ Nota sobre la versión que el cliente respondió

El cuestionario que Mauricio contestó es la **versión de 12 preguntas enviada el 2026-08-07**. El
archivo del repo se amplió a **14 preguntas el 2026-08-17** (tras el Reporte la agencia 1), agregando
*rangos de precio* y *qué significa "Cerrada"*, y reescribiendo las de seguimiento y confirmación de
cita. **Esas cuatro modificaciones nunca le llegaron al cliente.** Por eso hay respuestas que
contestan la redacción vieja, y dos temas que quedaron sin preguntar. Se resuelven en
`puntos-abiertos-ronda-2-2026-08-18.md`.


## Índice

1. Reglas de Atribución Meta CAPI
2. Reglas de Programas
3. Reglas del Agente Conversacional "Mauricio"
4. Reglas de Outreach Proactivo (tri-toque)
5. Reglas de Rescate Post-Link
6. Reglas de Estado de Lead
7. Reglas de Nurturing (drip 4 toques por programa)
8. Reglas de Normalización de Datos
9. Reglas de Datos / CRM (identidad y linkeo cross-plataforma)
10. Reglas de Reporting
11. Reglas de Error y Fallback
12. Marcadores de incertidumbre

---

## 1. Reglas de Atribución Meta CAPI

El tracking de conversiones a Meta se reparte entre **dos workflows**:
- `wf-capi-registro-folio` (`9yCbynoKDt9hgiBq`, **LIVE**) — la **landing** (`go.venttur.com`) hace POST al hacer clic-a-WhatsApp y persiste la "huella de navegador" (fbc/fbp/fbclid/ip/ua) en la tabla Airtable **Folios CAPI**.
- `wf-meta-capi-venttur` (`z98w2yWVEMOfifMl`, sub-workflow, `active:false` en el export) — invocado en **paralelo por cada mensaje entrante** desde el main; decide entre rama FOLIO y rama CTWA y dispara el evento `Lead` a Meta.

### 1.1 Formato de folio (CONFIRMADO — preservado de mayo, sigue válido)

El folio viaja embebido en el texto del mensaje del lead / del output del agente por WhatsApp:

```
Folio: XXXXXX | ... Prog: YYY)
```

- **Regex folio (en `wf-meta-capi-venttur`, nodo `Extraer Folio + Hashear1`):** `/Folio:\s*(.+?)\s*\|/i` (captura entre `Folio:` y el primer `|`).
- **Regex programa:** `/Prog:\s*([^\s)]+)/i` (captura después de `Prog:` hasta espacio o `)`).
- **Regex folio (en `wf-venttur-main`, nodo `Crear primer contacto`):** `/Folio:\s*([A-Za-z0-9_]+)\s*\|/i` — nota: este acepta solo `[A-Za-z0-9_]`, mientras el del CAPI acepta `.+?`. ⚠️ INCIERTO — folios con `-` (ej. `7T-UBW`, `-KXLBA`, que la versión de mayo listaba como válidos) matchean en el CAPI pero **no** en el main (impacto: el `Folio` del lead podría no persistirse en Airtable Leads aunque el evento CAPI sí se dispare; discrepancia de regex entre dos nodos que parsean el mismo dato).
- **Programa:** se convierte a UPPERCASE tras extraer.
- Si falta folio **o** programa en la rama folio: `throw new Error('Folio o Prog no encontrado...')` → aborta → dispara `errorWorkflow OBkUyb8fuo30DzA9`.

### 1.2 Discriminante FOLIO vs CTWA (CONFIRMADO — corrección clave)

El router es el nodo IF `contiene_folio`: `custom_fields.respuesta_definitiva` **contains** la substring literal `"Folio"`.
- Contiene `"Folio"` → **rama FOLIO** (lead vino de landing con folio).
- No contiene → **rama CTWA** (lead entró directo a WhatsApp por un anuncio Click-to-WhatsApp, sin landing).

⚠️ INCIERTO — el discriminante es una búsqueda de substring sobre texto libre, no un campo estructurado (impacto: frágil; un mensaje que casualmente contenga "Folio" ruteo mal; en GHL conviene un flag `origen = landing|ctwa`).

### 1.3 Hashing PII con SHA-256 (CONFIRMADO — preservado de mayo)

Meta CAPI requiere PII hasheado con SHA-256 antes de enviar. Implementación en **JavaScript puro** (sin `crypto`, sin `TextEncoder`, sin `require` — por el sandbox de n8n; hay dos copias: una legible en la rama folio, una minificada en CTWA).

| Campo | Transformación previa | Hash | Rama |
|-------|----------------------|------|------|
| `phone` → `ph` | `whatsapp_phone.replace(/\D/g,'')` (solo dígitos) + `toLowerCase().trim()` | SHA-256 | folio + CTWA |
| `first_name` → `fn` | `toLowerCase().trim()` | SHA-256 | folio + CTWA |
| `last_name` → `ln` | `toLowerCase().trim()` | SHA-256 | folio + CTWA |
| `fbc`, `fbp`, `client_user_agent`, `client_ip_address` | **NO se hashean** (Meta los espera en claro) | — | **solo folio** |

### 1.4 Payload y endpoint Meta (CONFIRMADO)

- **Endpoint:** `POST https://graph.facebook.com/v21.0/{pixel_id}/events`
- **Content-Type:** `application/json`
- **Auth:** `access_token` en el **body** del JSON (no Bearer header). El token viene **por programa** desde Airtable Programas CAPI (multi-pixel/multi-token).
- **Deduplicación:** Meta deduplica server-side por `event_id`.

**Rama FOLIO** (nodo `HTTP Request Meta CAPI1`):
```json
{
  "data": [{
    "event_name": "Lead",
    "event_time": <Math.floor(Date.now()/1000)>,
    "event_id": "<folio>",                       // ← dedup real contra pixel del navegador
    "action_source": "website",
    "event_source_url": "<Landing URL || default_url>",
    "user_data": { "ph":[…], "fn":[…], "ln":[…], "fbc":…, "fbp":…, "client_user_agent":…, "client_ip_address":… },
    "custom_data": { "folio": "<folio>" }
  }],
  "access_token": "[REDACTED]"
}
```

**Rama CTWA** (nodo `HTTP Request Meta CAPI2`):
```json
{
  "data": [{
    "event_name": "Lead",
    "event_time": <ts>,
    "event_id": "CTWA_<phone>_<ts>",             // ← id sintético, SIN dedup real
    "action_source": "system_generated",
    "event_source_url": "<default_url del programa BS>",
    "user_data": { "ph":[…], "fn":[…], "ln":[…] },   // solo ph/fn/ln, sin señales de navegador
    "custom_data": { "origen": "CTWA" }
  }],
  "access_token": "[REDACTED]"
}
```

### 1.5 Diferencias FOLIO vs CTWA (tabla de referencia — corrige "CTWA no se veía" de mayo)

| Aspecto | FOLIO | CTWA |
|---|---|---|
| Discriminante | msg contiene `"Folio"` | no contiene `"Folio"` |
| `event_id` | `<folio>` (dedup real) | `CTWA_<phone>_<ts>` (sin dedup) |
| `action_source` | `website` | `system_generated` |
| `custom_data` | `{folio}` | `{origen:"CTWA"}` |
| Señales de match | ph+fn+ln+fbc+fbp+ip+ua | **solo ph+fn+ln** |
| Config de programa | **dinámica** (`{Programa}=<extraído>`) | **fija: `{Programa}="BS"` HARDCODEADO** |
| Update a Leads | match `id_2` → Folio + fbclid | match `ID Manychat` → Folio=`"N/A (WA)"`, fbclid=`"-"` |
| Writeback fbtrace_id | **sí** (a Folios CAPI, match por Folio) | **no** (nodo terminal, sin auditoría) |

**Corrección explícita de mayo:** la rama CTWA existe, está completamente cableada y es funcional. Es un evento de **match débil** (sin fbc/fbp/ip/ua, sin dedup real). Y **NO ramifica por `programa_wpp`** como asumía el contexto — hardcodea `{Programa}="BS"` en el nodo `Buscar Config Programa2`. El campo `programa_wpp` (custom field de ManyChat) **no aparece en el JSON del CAPI**.

### 1.6 fbc: valor guardado vs fallback construido (CONFIRMADO — preservado de mayo)

Prioridad en la rama FOLIO (`Preparar CAPI Data1`):
1. `fbc` guardado por la landing en Folios CAPI (más preciso).
2. Si no hay `fbc` pero sí `fbclid`: se construye `fb.1.${airtableTimestamp || Date.now()}.${fbclid}`.
3. Si no hay ni `fbc` ni `fbclid`: el campo se **omite** del payload (no se manda null).

El mismo patrón lo aplica la landing en `wf-capi-registro-folio` (nodo `Extraer y Enriquecer`): la landing **casi nunca manda `fbc`** — se deriva `fb.1.<timestamp_ms>.<fbclid>` (`subdomainIndex` fijo en `1`, sin segmento de dominio). ⚠️ INCIERTO — el `Timestamp` de Folios CAPI se usa tal cual dentro del `fb.1.{ts}.{fbclid}`; Meta espera ms; si estuviera en segundos el fbc quedaría malformado (impacto: menor calidad de match; el CSV real muestra timestamps de 13 dígitos = ms, así que probablemente OK, pero no verificado en todos los casos).

### 1.7 Registro de folio en la landing (CONFIRMADO — nuevo detalle T3)

`wf-capi-registro-folio` (webhook `capi-registro-folio-venttur`, **LIVE**):
- Gate: solo persiste si `body.folio` **no está vacío** (IF strict `notEmpty`). Folio vacío → responde `{ok:true}` igual, **sin guardar ni loguear** (pérdida silenciosa).
- Campos del body reales (del pinData): `origen` (`"clic_whatsapp_directo"`), `folio`, `programa`, **`fbclid_completo`** (no `fbclid`), `fbp`, `user_agent`, `timestamp` (epoch **ms**), `url` (con `utm_*` embebidos). ⚠️ Corrección de mayo: los nombres de campo reales son `fbclid_completo` (no `fbclid`) y `url` (no `landing_url`).
- `fbclid`: de `body.fbclid_completo`; fallback regex `/[?&]fbclid=([^&]+)/` sobre la `url`.
- `ip`: **no viene en el body** — se deriva del header `x-forwarded-for` (primer valor, inyectado por el proxy Caddy).
- Escritura a Airtable Folios CAPI: **CREATE puro** (`matchingColumns: []`) → **sin deduplicación** (dos POST con el mismo folio crean dos filas). El CSV real tiene **4.003 filas**, con folios repetidos (ej. `WRLWWQ` aparece ≥2 veces) → confirma que hay duplicados en producción.
- Columna `fbtrace_id` existe en el schema pero **este flujo no la escribe** — la completa `wf-meta-capi-venttur` (rama folio) con la respuesta de Meta.
- Los `utm_*` (`utm_source=fb`, `utm_campaign`=ID de campaña Meta, `utm_id`, `utm_content`, `utm_term`) llegan dentro de `url` pero **NO se parsean a columnas** — solo quedan como texto en `Landing URL`. Oportunidad de mapeo perdida para GHL.

---

## 2. Reglas de Programas

Hay **dos capas de "programa" que no coinciden 1:1** — esta es una de las mayores correcciones vs. mayo.

### 2.1 Programas CONCEPTUALES del agente (6) — del system prompt + links de agendamiento

| Programa conceptual | Link de asesoría (sin markdown) | Experto | Edad objetivo (base de conocimiento) |
|---|---|---|---|
| Internados / Boarding School | `promo.venttur.com/agendar-ema` | **Rodrigo** | 12–17 |
| Año Académico con familia (AA Familiar) | `promo.venttur.com/AAFamilia-Agendar` | **Rodrigo** | 14–17 |
| Summer Camp (campamentos) | `promo.venttur.com/SummerCamp-Agendar` | **Rodrigo** | 10–17 |
| Pathway universitario Alemania | `promo.venttur.com/PW_Alemania_Agendar` | **Andrés** | 17–30 (trámite desde 16) |
| Gap Year / Estudia y Trabaja (Australia) | `promo.venttur.com/Estudiar-y-Trabajar-en-Australia` | **Diego** | 18–30 |
| Estudiar y Trabajar (cursos idiomas) | `promo.venttur.com/EstudiaryTrabajar_Agendar` | **Andrés** | 18–30 |
| (duda / fallback) | `promo.venttur.com/agendar-ema` | — | — |

⚠️ INCIERTO — **ambigüedad "Gap Year / Estudia y trabaja" vs "Estudiar y trabajar"**: el system prompt tiene **dos entradas distintas** con links y expertos distintos (`Estudiar-y-Trabajar-en-Australia`/Diego vs `EstudiaryTrabajar_Agendar`/Andrés). El prompt las presenta como programas separados pero el criterio de cuándo enviar cuál no es explícito (impacto: el agente puede enviar el link/experto equivocado; en GHL hay que consolidar o desambiguar con el cliente).

### 2.2 Códigos CAPI y pixels (4 códigos, 2 pixels) — del CSV real `programas-capi.csv`

| Código `Programa` | `Nombre del programa` | `pixel_id` | `default_url` |
|---|---|---|---|
| `BS` | Boarding IA | **228398216567258** | `go.venttur.com/bs` |
| `BSG` | Boarding IA | **228398216567258** | `go.venttur.com/bs/girls` |
| `BSC` | Boarding IA | **228398216567258** | `go.venttur.com/bs/cats` |
| `HF` | AA Familiar IA | **24520910174237152** | `go.venttur.com/hf` |

Solo **2 pixels**: `228398216567258` (Boarding, para BS/BSG/BSC) y `24520910174237152` (AA Familiar, para HF). Todos comparten el mismo `access_token` (`EAAKzdslXZCkMB…`, expuesto en el CSV → **rotar antes del handoff**).

### 2.3 ⚠️ MISMATCH de programas sin pixel (corrección crítica)

Los programas conceptuales **Summer Camp, Pathway, Gap Year/Estudia y Trabaja NO tienen fila en Programas CAPI** → su tracking CAPI es **INCIERTO** (impacto: probablemente esos leads no generan evento `Lead` a Meta, o si entran por CTWA se atribuyen todos al pixel `BS` por el hardcode de §1.5; no asumir que existe tracking para ellos). Solo Boarding (BS/BSG/BSC) y AA Familiar (HF) tienen pixel configurado.

### 2.4 Atribución CTWA por texto (tabla `Mensajes anuncios`)

El main deduce la **fuente/campaña** (`Fuente lead`) y el **programa de interés** (`Programa interés`) del lead matcheando el texto de su primer mensaje contra el campo `Mensaje` de la tabla Airtable **Mensajes anuncios** (25 anuncios, `matchingColumns` inexistente — se hace en JS con coincidencia flexible bidireccional case-insensitive: `resp.includes(msgClean) || msgClean.includes(resp)`).

Enums de `Interes` en la tabla (del CSV): **`AA Familiar IA`**, **`Pathway IA`**, **`Boarding IA`**, **`Automatización - Comentarios`**. Ejemplos de `Anuncio` → `Interes`:
- `Francia / P. México/ Advantage`, `Francia / P. México / P1`, `AA-PUBLICO`, `AA_PROSP_WA_2026-04` → **AA Familiar IA**
- `Estudiantes Locales/Foraneos`, `Papas locales/Foraneos` (con texto "Pathway en Alemania") → **Pathway IA**
- `Internados / Público Advantage / 3`, `BOARD-PRES-V1/V2/V3`, `BOARD-GIRL-V1/V2/V3`, `BOARD-DEP-V1/V2`, `Internados / formulario` → **Boarding IA**
- `Facebook - Instagram` → **Automatización - Comentarios**

⚠️ INCIERTO — nótese que **Pathway sí aparece como `Interes` en Mensajes anuncios** (fuente conversacional/CRM) pero **no tiene pixel en Programas CAPI** (fuente de tracking). Son dos taxonomías distintas que no cierran (impacto: un lead de Pathway se clasifica bien en el CRM pero su conversión no llega a Meta).

### 2.5 Enum de `Programa interés` en Airtable Leads (8 valores)

Del schema embebido en los nodos Airtable: `No definido` · `Boarding IA` · `Gap Year IA` · `Pathway IA` · `Summer Camp IA` · `AA Familiar IA` · `Francia IA` · `Automatización - Comentarios`. Nótese que existen `Gap Year IA`, `Summer Camp IA`, `Francia IA` en el enum de Airtable aunque no tengan pixel CAPI ni (algunos) fila en Mensajes anuncios.

⚠️ **Enum definido vs. datos reales.** En `leads.csv` (3819 leads) la distribución observada es: `No definido` 1315 · `Pathway IA` 881 · `AA Familiar IA` 632 · **`Boarding School` 482** · `Boarding IA` 437 · `Summer Camp IA` 42 · `Gap Year IA` 25 · `Automatización - Comentarios` 5. El valor **`Boarding School` (482 leads) NO figura en el enum de 8 capturado del schema** pero **lo escribe activamente un workflow en producción**: `Crear Lead Nuevo` del Outreach Form Meta hardcodea `Programa interés='Boarding School'` (ver §4.2) para todo lead de Form Meta → de ahí que los **482 `Boarding School` ≈ los 483 leads con `Origen='Form Meta'`** (casi 1:1). En cambio la vía conversacional/dispatcher escribe `Boarding IA`. Resultado: **DOS grafías activas para el mismo programa** (Boarding School vs Boarding IA, 482 vs 437). No es legado — ambas se están escribiendo hoy. El Rescate se salva porque matchea por `contains "Boarding"` (robusto a ambas), pero **al migrar a GHL hay que unificar y normalizar `Boarding School` → `Boarding IA`** (un single-select con exact-match las trataría como 2 programas distintos). Ver la regla de matching del Rescate (§5) y el modelo de datos del doc 01.

### 2.6 Matching de programa en Rescate (⚠️ 5 en envío vs 6 en memoria — corrige mayo)

El routing del rescate usa `Programa interés.includes(...)`. **Corrección de mayo:** los nodos que gobiernan el ENVÍO del mensaje (`Code: Fase 1`/`Code: Fase 2`) solo mapean **5 destinos**:

| `Programa interés` contains | Destino | URL |
|---|---|---|
| `"Boarding"` | boarding | `/agendar-ema` |
| `"AA Familiar"` **O** `"Francia"` | aa_familia | `/AAFamilia-Agendar` |
| `"Summer Camp"` | summer | `/SummerCamp-Agendar` |
| `"Pathway"` | pathway | `/PW_Alemania_Agendar` |
| `"Gap Year"` | gap_year | `/Estudiar-y-Trabajar-en-Australia` |
| (sin match) | `matched=false` → tag `RESCATE_PROGRAMA_NO_MAPEADO`, **no se envía nada** | — |

Los nodos de **memoria sintética** (`Build Rescate Memory F1/F2`) tienen **6 claves** (agregan `"Estudio y Trabajo"` → `/EstudiaryTrabajar_Agendar`). ⚠️ Un lead con `Programa interés` = "Estudio y Trabajo" cae en `matched=false`, recibe tag `RESCATE_PROGRAMA_NO_MAPEADO` y **nunca recibe mensaje de rescate** → la clave "Estudio y Trabajo" del diccionario de memoria es **código muerto** (nunca se alcanza porque el gate previo ya cortó al lead). Impacto: leads de ese programa quedan sin rescate silenciosamente; en GHL usar una tabla única programa→(msgF1, msgF2, url, tag) como fuente de verdad.

---

## 3. Reglas del Agente Conversacional "Mauricio" (NUEVO — el corazón del sistema)

Vive inline en el `systemMessage` del nodo `Agente IA WPP` de `wf-venttur-main.json`. Modelo **gpt-4o, temperature 0**. Memoria Postgres (Supabase), `contextWindowLength 35`, `sessionKey = whatsapp_phone.replace('+','')`.

### 3.1 Identidad y misión

- Se llama **Mauricio**, **asistente virtual estratégico** de Venttur Education & Travel (consultora familiar mexicana de movilidad académica internacional).
- Regla central: **"No vendemos programas. Ayudamos a elegir el camino más alineado."** El rol NO es vender, es **asesorar con inteligencia emocional y táctica**.
- Diferenciales: metodología **EMA** (Evaluation · Match · Achieve); empresa de hermanos fundadores ("cada caso como un familiar").

### 3.2 Frameworks conversacionales

- **Chris Voss (empatía táctica):** Labeling (nombrar emociones), Mirroring (reflejar la última palabra clave con entonación interrogativa), Validación sin juicio, Preguntas calibradas (abiertas, sin buscar el "sí").
- **Alex Hormozi (diagnóstico consultivo antes de vender):** no pedir permiso para hacer el trabajo; preguntas que revelan qué cambio busca el usuario; "el cierre no es presionar, es proteger".
- **Combinación:** primero conectar (Voss), luego guiar (Hormozi) — **situacional, no en cada turno**.

### 3.3 Los 7 principios rectores (literal del prompt)

1. Primero conexión, luego solución.
2. Diagnóstico real, no interrogatorio (preguntas abiertas, una por una).
3. Escucha lo que no se dice (cambios de vida, miedos, deseos implícitos).
4. Valida antes de vender.
5. Cada paso tiene una intención (no avanzar por cumplir el flujo).
6. No repitas frases vacías.
7. Cierra con valor, no con urgencia.

### 3.4 Diagnóstico de 7 pasos (estructura adaptativa, no rígida)

1. **Crear conexión + obtener nombre** de la persona que escribe (SIEMPRE de quien escribe, **nunca del hijo/a**, aunque busque un plan para el hijo).
2. **Identificar si es padre o estudiante.**
3. **Explorar motivación personal.**
4. **Nivel de idioma y país.**
5. **Cualificación** (edad, escuela, intereses) — por partes.
6. **Recomendación contextualizada** (tipo de programa como puente, no como cierre; nunca recomendar sin perfil claro).
7. **Cierre consultivo** (agendar videollamada con Rodrigo/Andrés/Diego; solo cuando hay claridad de perfil + emoción + interés).

Regla transversal: **no avanzar de paso si el anterior no está claro**; se puede permanecer varias interacciones en el mismo paso si eso fortalece confianza.

### 3.5 Reglas de comportamiento conversacional (las 10 + reglas de importante)

1. **Mensajes ≤ 200 caracteres** (salvo que el razonamiento requiera más; dividir en bloques).
2. **No recomendar sin diagnóstico completo** (edad, nivel educativo, tipo de escuela, motivación, apertura).
3. **Priorizar internados** si el usuario es **< 17 años** y busca estructura/seguridad/desarrollo académico-deportivo.
4. Sin asteriscos, sin mayúsculas innecesarias, sin markdown.
5. No cerrar el destino demasiado pronto.
6. **No insistir con la asesoría**: si no responde al primer ofrecimiento, no repetir; generar más valor / indagar antes de volver a ofrecer.
7. Usar EMA como ventaja táctica, no como folleto.
8. **No repetir el enlace** en el mismo bloque (y en general no repetir un link ya enviado).
9. Personalizar al experto (Rodrigo/Andrés/Diego) con una línea de valor.
10. **Precio: nunca dar cifra sin contexto.** Patrón obligatorio **validar → enmarcar valor → dar dirección** (ejemplo concreto / comparación / pregunta estratégica). "Nunca sustituyas una buena exploración por un número suelto."
- **Links sin formato markdown ni paréntesis** (ejemplo negativo explícito en el prompt: nada de `[texto](url)`; solo la URL desnuda).
- Si preguntan por la web: enviar `venttur.com` + IG `@venttur_` y recalcar que la mejor info está en la asesoría.
- Respuestas en texto común, sin markdown (ejemplo negativo con `**negritas**`).
- Preguntas variadas, evitar sí/no y repetitividad.

### 3.6 Reglas de elevación / tools técnicas (instrucciones internas)

El agente NO menciona las tools al usuario. Cableadas como `ai_tool` en el main: **`crear_contacto`** (toolWorkflow → `cZUNKQyZNOHy5twQ`) y **`elevar`** (toolHttpRequest → ManyChat sendFlow `content20250716130059_365663`).

- **`crear_contacto`:** se activa cuando el usuario da **nombre + apellido completos** de quien escribe. Guarda `nombre`/`apellido` en variables y llama la tool sin avisar al usuario.
- **`elevar`** (asignar a humano / Live Chat) se dispara si:
  - el usuario **pide hablar con un humano / emergencia / similar** (avisarle antes que lo pone en contacto con un agente); **o**
  - el usuario **envía exactamente el mismo mensaje 2+ veces de forma consecutiva e inmediata** (sin ningún mensaje distinto entre medio). Al cumplirse, elevar inmediatamente y **no continuar el flujo**.
- **Excepción anti-elevación:** si el mismo mensaje reaparece **NO consecutivo** (retoma días después con el mismo texto inicial, con cualquier mensaje distinto entre medio), **NO elevar** — tratarlo como nuevo inicio operativo.

⚠️ INCIERTO — el prompt también instruye: *"Si el usuario responde a tu segundo mensaje… activa la herramienta `contestan_2do`"*, pero **NO existe ningún ai_tool `contestan_2do` cableado en el main** (impacto: el agente tiene instrucción de llamar una tool inexistente; la métrica "contestan 2do mensaje" no se implementa; el campo `Contestan 1er mensaje` de Airtable se setea determinísticamente por otros workflows, no por esta tool). Ver también: `wf-crear-contacto-clientify-airtable` (`cZUNKQyZNOHy5twQ`) **no está expuesto vía MCP** (`availableInMCP:false`) y recibe inputs planos sin `$fromAI` — evidencia de que la tool `crear_contacto` del agente y ese sub-workflow **no son necesariamente el mismo** (relación no confirmable desde los JSON).

### 3.7 Base de conocimiento por programa (edades e inversiones)

> 🔴 **LA REGLA "NUNCA CITAR CIFRA DIRECTAMENTE" SE ELIMINÓ (2026-08-17).** El Reporte la agencia 1 la
> señala como causa del Hallazgo 8: el agente respondía a preguntas de precio sin dar rango ni cerrar
> con una cita concreta. No era un olvido del modelo — **el prompt se lo prohibía en 5 lugares**
> (*"Nunca cites la cifra directamente"*, *"Nunca respondas con una cifra directa"*, *"Nunca
> sustituyas una buena exploración por un número suelto"*).
>
> **Regla nueva (prompt v2.0, sección "💰 Cómo se responde por precio"):** ante una pregunta de precio
> se responde **siempre** con la estructura obligatoria del reporte — **Validar → Rango → Valor →
> Puente con fecha concreta** — usando el rango **del programa correspondiente**:
>
> | Programa | Rango que se comparte |
> |---|---|
> | Internados en el extranjero | USD $50,000 – $130,000 anuales |
> | Año académico con familia anfitriona | MXN $240,000 – $450,000 |
> | Campamentos de verano/invierno | MXN $90,000 – $180,000 (2 a 8 semanas) |
> | Pathway universitario en Alemania | MXN $400,000 – $450,000 (total antes de viajar) |
> | Gap Year / Estudiar y trabajar | MXN $100,000 – $200,000 |
>
> Nunca se cierra una respuesta de precio sin proponer día ("¿hoy o mañana?"). Y si el lead menciona
> un presupuesto, **se confirma la moneda antes de decir si alcanza**.

| Programa | Edad | Inversión estimada (SOLO uso interno del agente) | Regla de precio |
|---|---|---|---|
| Internados | 12–17 | USD $50.000–$130.000/año | **Nunca citar la cifra**; foco en estructura/madurez/acceso a universidades top; becas parciales solo tras conexión |
| Año académico c/familia | 14–17 | MXN $240.000–$450.000 | No ofrecer cifra sin explorar perfil/expectativas |
| Campamentos | 10–17 | MXN $90.000–$180.000 (2–8 sem) | Evitar citar de inmediato; primero conectar |
| Pathway Alemania | 17–30 | MXN ~$400.000–$450.000 antes de viajar (fondo bloqueado ~$240k + curso/asesoría ~$180–200k + carrera pública sin colegiatura) | Nunca dar la cifra directa; desglosar por etapas, enmarcar valor |
| Gap Year / Estudia y trabaja | 18–30 | MXN $100.000–$200.000 | No citar sin identificar motivación; explicar que se puede trabajar/generar ingresos |

Regla transversal de precio (aplica a TODOS): **validar preocupación económica → enmarcar valor total → ejemplo comparativo → explorar juntos antes de concretar**. "Nunca respondas con una cifra directa si el usuario no ha expresado contexto, motivación y apertura."

### 3.8 Datos de negocio a preservar (del agente y flows)

- Expertos: **Rodrigo** (cofundador, internados) · **Andrés** (cofundador, Pathway/Gap Year) · **Diego** (hermano, estudia-y-trabaja Australia).
- **Número directo de Rodrigo:** **+52 1 33 1944 2476** (embebido en el flow ManyChat "Agenda", no en n8n — dato de negocio a preservar).

---

## 4. Reglas de Outreach Proactivo (tri-toque) — `wf-outreach-form-meta` (`CUuFxbst3iHpgeXS`, LIVE)

Convierte leads de **Meta Lead Ads** (sync a Google Sheet) en registros Airtable + una secuencia de 3 toques por WhatsApp. Dos flujos independientes en un workflow.

### 4.1 Trigger e ingestión (Flujo A)

- **Trigger:** Google Sheets Trigger `rowAdded`, poll cada minuto, doc `1HzJVMBwnGikiI_U805N7oqcXPYE7TjEFTL1rqdcCEIU`, hoja `Boarding_Schools_Venttur_2026-test-2` (gid 160362675). **Corrección de mayo:** ya NO es el webhook `vtr-form-meta-outreach`; migró a Sheets Trigger.
- **`Normalize Payload`** (Code):
  - `stripMetaPrefix(v)` = `v.replace(/^[a-z]+:/,'').trim()` → `Folio` = `id` sin prefijo `l:`.
  - `parsePhone`: limpia `^p:\+?` y no-dígitos; **válido solo si 10–15 dígitos**; **prioridad columna `whatsapp`, fallback `phone_number`**.
  - `deriveTipo(adName)`: contiene `PAPAS/PAPÁS/MAMAS/MAMÁS` → `'Padre/Madre'`; else `'No especificado'` (granularidad papá/mamá vive en `Ad Name`).
  - `deriveFuente(platform)`: `ig`→Instagram, `fb`→Facebook, else `Facebook - Instagram`.
  - **`touch1At = new Date().toISOString()`** → `Touch 1 programado at` = **AHORA de creación, SIN +1h** (comportamiento v4).
  - **Edge case `p:MX`** (whatsapp vacío + phone_number no numérico): empuja `{_error:true, _error_reason, _meta_lead_id, _row_number, _raw_row}` y `continue` (NO throw).

### 4.2 Gate de idempotencia y dedup

- **Dedup:** `Buscar Lead Existente` filtra `OR({Folio}='<meta_lead_id>', {Telefono}='<telefono>')`.
- **Creación:** `Crear Lead Nuevo` es **upsert `matchingColumns=["Folio"]`** (idempotencia dura). Escribe 18 campos incluyendo los **8 de cualificación** (Grado Escolar, Inicio Deseado, Nivel Inglés, Ad Name, Platform, Tipo, Fuente lead, Folio) + `Programa interés='Boarding School'`, `Origen='Form Meta'`, `Toques enviados=0`, `Outreach Form Meta enviado=false`, `Contestan 1er mensaje=false`.
- **Gate de protección `¿Lead seguro actualizar?`:** solo actualiza un lead existente si `Outreach Form Meta enviado ?? false === false` **AND** `Toques enviados ?? 0 === 0` (coalescing porque Airtable no devuelve checkbox/number unchecked). Si ya está en secuencia → **no lo toca**.
- **`Actualizar Lead Existente`** solo reescribe **inmutables** (Folio, Origen, Ad Name, Platform, Grado/Inicio/Nivel, id_2); NUNCA toca Toques/Outreach/Última actividad/Estado.

### 4.3 Cadencia tri-toque EXACTA (Flujo B — Cron)

- **Cron** cada ~5 min (⚠️ INCIERTO — el JSON tiene `interval:[{field:'minutes'}]` **sin `minutesInterval`** → n8n corre **cada 1 min** por default; el nombre dice "5 min"; impacto: drift nombre vs comportamiento).
- **`Get Leads Pendientes`** (`filterByFormula`, cadencia real):
```
AND(
  {Origen}='Form Meta', NOT({Agendan cita}), {Última actividad}=BLANK(),
  {Toques enviados}<3, {Touch 1 programado at},
  OR(
    AND({Toques enviados}=0, IS_AFTER(NOW(), {Touch 1 programado at})),
    AND({Toques enviados}=1, IS_AFTER(NOW(), DATEADD({Touch 1 programado at},24,'hours'))),
    AND({Toques enviados}=2, IS_AFTER(NOW(), DATEADD({Touch 1 programado at},72,'hours')))
  ))
```
- **Cadencia efectiva: 0h / +24h / +72h desde CREACIÓN** (todos los toques anclados a `Touch 1 programado at`, NO incrementales entre toques). El "5 min" es solo el polling, no un delay de diseño.
- **Guards de exclusión:** ya agendó, ya respondió (`Última actividad` no-BLANK), `Toques>=3`, `Origen!='Form Meta'`, o sin `Touch 1 programado at`.
- **Switch por `Toques enviados`:**
  - `=0` → **Touch 1**: `createSubscriber ManyChat` (con `consent_phrase` del opt-in del form) → `sendFlow` **`content20260612151152_969589`** (template MARKETING `boarding_form_followup`, es_MX).
  - `=1` → **Touch 2**: `sendFlow` **`content20260616231914_193459`** (usa `ID Manychat` ya guardado).
  - `=2` → **Touch 3**: `sendFlow` **`content20260616231947_185709`**.
- **`Marcar Enviado`/2/3:** `Outreach Form Meta enviado=true`, `Outreach enviado at`, `ID Manychat`, **`Toques enviados = (prev||0)+1`**, `Ultimo toque at=$now`. **NO** setea `Última actividad`.

### 4.4 Lead Score / Tipo lead (hot/warm/cold)

⚠️ INCIERTO — los campos `Lead Score` y `Tipo lead` (**tres valores: `hot` / `warm` / `cold`**) **existen en Airtable Leads** pero **el cálculo NO es visible en `wf-outreach-form-meta.json`** — `Normalize Payload` y `Crear Lead Nuevo` no los computan en el JSON analizado (impacto: la lógica de scoring vive en otro lado — posiblemente una automation de Airtable, una fórmula, o una versión del workflow no capturada; no se puede documentar la regla exacta desde las fuentes disponibles). Distribución real en `leads.csv` (3819 leads): **`cold` 3510 · `warm` 181 · `hot` 128**; la gran mayoría con `Lead Score=0`. Nota: la versión de este doc y otros hablaban de "hot/cold" (dos valores) — **es incorrecto, son tres** (`warm` es un estado intermedio real de 181 leads).

### 4.5 Rama de error

- `IF (_error?)` TRUE → `Registrar Error Normalize` → sub-workflow `webapp_errors` (`OBkUyb8fuo30DzA9`), shape plano. **Terminal** — lead con teléfono inválido **NO se crea ni recibe outreach**.
- ⚠️ El logging de fallo de `createSubscriber` (Touch 1) va a `Registrar Error en Supabase` que está **DESHABILITADO** → esos fallos no se persisten. Touch 2/3 usan `sendFlow` con `neverError` **sin** check posterior → un fallo silencioso igual incrementa `Toques enviados` (pérdida de toque sin registro).

---

## 5. Reglas de Rescate Post-Link — `wf-rescate-post-link` (`mkEP1qFN7MVb9qP0`)

**Corrección de mayo:** en producción como workflow n8n (no ManyChat), 2 fases, invocado por `wf-actualizar-link-enviado` con `{telefono}`.

### 5.1 Precondición de entrada

Se dispara desde `wf-actualizar-link-enviado` cuando el agente envía un link `promo.venttur.com/`. **Corrección de mayo:** la precondición NO es un tag `LINK_ABANDONADO_FRIO` (ese tag se **aplica al final**, no es gate de entrada). El único disparo es la invocación por Execute Workflow tras enviar el link.

### 5.2 Check `Agendan cita` antes de cada fase (gate de rescate)

Antes de cada mensaje se busca el lead en Airtable Leads por `{Telefono}` y se evalúa `Agendan cita`:
- `IF: ¿ya agendó?` — condición `{Agendan cita} boolean true`. **Rama TRUE vacía → STOP** (si ya agendó, no rescata). Rama FALSE → continúa.

### 5.3 Timings

| Fase | Delay | Desde | Tono del mensaje |
|---|---|---|---|
| Fase 1 | **45 minutos** | invocación (envío del link) | Concierge / fricción |
| Fase 2 | **24 horas** | post-Fase 1 (~24h45m post-link) | Storytelling / objeción |

### 5.4 Envío (ManyChat) y partes de mensaje

- Solo se usa **`parte1`** (custom field `13337279`); `parte2`/`parte3` (13337280/13337281) siempre `null`.
- `Set Custom Fields` (patrón `JSON.stringify(mcBody)`) → `sendFlow` **`content20250617172539_850988`** (flow "Enviar mensajes").
- Los 12 textos (6 programas × 2 fases) están en `template-texts-canonical.md` §4–15 y hardcodeados en los Code nodes. Todos cierran con "¿Listo para ver si es la mejor opción para tu hijo o hija? Reserva tu espacio aquí: <URL>".

### 5.5 Tags de resultado

- `RESCATE_PROGRAMA_NO_MAPEADO` (tag_id **87501935**): si `Programa interés` no matchea ninguno de los 5 destinos de envío → **no se envía mensaje, no hay Fase 2**.
- `LINK_ABANDONADO_FRIO` (tag_id **87501917**): si tras la Fase 2 el lead sigue sin agendar → se marca frío. **Corrección de mayo:** es una etiqueta de **cierre**, no de precondición.

### 5.6 Ventana de conversación WhatsApp (preservado de mayo — sigue válido)

Los mensajes de rescate son mensajes regulares del bot (no Templates). Fase 1 (45 min) cae dentro de la ventana de 24h; **Fase 2 (~24h45m)** puede caer fuera si el lead no respondió → ManyChat podría no entregar el mensaje. Punto a monitorear post-go-live (delivery rate Fase 2 vs Fase 1). Opciones futuras: aceptar el gap / Templates solo Fase 2 / acortar Fase 2 a ~20h.

### 5.7 Memoria sintética (NUEVO — no existía en mayo)

En paralelo a cada `sendFlow`, se insertan filas en Postgres `n8n_chat_histories` para que el agente principal no re-salude ni repregunte si el lead responde:
- `Build Rescate Memory (Fase 1)`: `normalizeSessionKey(phone)` (strip no-dígitos; **si 12 dígitos y empieza 52 → `521`+resto**, quirk MX); `buildSystemMessage(fields)` (prosa con datos del lead) + `ai_message` (texto del template). Placeholder `{{first_name}}`.
- `Insert system FORM (idempotent)`: INSERT con `WHERE NOT EXISTS (… type='system')` → **1 solo system por sesión**.
- `Insert ai Rescate Fase 1` / `Fase 2`: INSERT directo del ai (no idempotente). Fase 2 usa placeholder `[first_name]` (no `{{first_name}}`) y NO inserta system (ya existe del Touch 1).
- ⚠️ INCIERTO — issues cosméticos/de wiring detectados en el snapshot: `Build Rescate Memory (Fase 1)` referencia `$('Get Lead')` que no existe (el nodo real es `Airtable: 1er check`); Fase 2 debe referenciar `Airtable: 2do check`; hay nodos "respaldo" desconectados (impacto: cuando el flujo dispare en prod esas ramas de memoria pueden fallar; los Postgres tienen `onError: continueRegularOutput` así que no abortan el rescate, pero la memoria puede no cargarse).
- El `Airtable search` solo pide 5 fields (Programa interés, ID Manychat, Nombre, Agendan cita, Telefono) pero `buildSystemMessage` lee Apellido/Email/Origen/Grado/Inicio/Nivel/Ad Name/Platform → esos vienen `undefined` → el system message sale reducido.

---

## 6. Reglas de Estado de Lead (NUEVO)

Dos workflows complementarios que mantienen `Estado conversación` + `Última actividad` en Airtable Leads. Enum de `Estado conversación` (4 valores): **`Activa`**, **`Contestó`**, **`Cita confirmada`**, **`Conversación interrumpida`**. ⚠️ **NO existe** un valor `Cita agendada` — la señal de cita es el checkbox booleano `Agendan cita`.

### 6.1 "Contestó" por inbound + anti-downgrade — `wf-estado-lead` (`b52CUYEkI2Ah3Xj6`)

Sub-workflow invocado por el main (inferido: no bloqueante) por cada mensaje entrante, con `{telefono}`:
- Match del lead por igualdad **exacta de string** en `{Telefono}` (sin normalización E.164).
- **Guarda forward-only (anti-downgrade):** el lead es "terminal" si `Agendan cita === true` **O** `Estado conversación === 'Cita confirmada'`.
  - Si terminal → **preserva** el `Estado conversación` actual (fallback `'Cita confirmada'` si estuviera vacío pero `Agendan cita=true`). NO lo pisa con "Contestó".
  - Si NO terminal → `Estado conversación = 'Contestó'`.
- Siempre (si el lead existe) actualiza `Última actividad = new Date().toISOString()` (**UTC**).
- **No-op si el lead no existe** (no crea leads; el alta inicial la hace otro workflow).
- ⚠️ INCIERTO — usa `items[0]` (asume unicidad de teléfono); edge case: `Agendan cita=true` con estado 'Conversación interrumpida' → la guarda lo **preserva** en 'interrumpida' (impacto: puede dejar un estado que parece regresivo). `active:false` en el export → posiblemente pendiente de deploy.

### 6.2 Barrido de silencio > 24h — `wf-estado-interrumpida` (`H6qYB3Oj97bxaTCX`, LIVE)

Schedule cada 1 hora. `filterByFormula`:
```
AND({Agendan cita} != TRUE(), {Estado conversación} != 'Cita confirmada',
    {Estado conversación} != 'Conversación interrumpida', {Última actividad},
    IS_BEFORE({Última actividad}, DATEADD(NOW(), -24, 'hours')))
```
- Marca `Estado conversación = 'Conversación interrumpida'` (constante) a los leads con **> 24h exactas** de silencio, sin cita, sin cita confirmada y no ya interrumpidos.
- **Idempotente:** el propio filtro excluye a los ya marcados (no re-escribe).
- Match del update por `matchingColumns:["Telefono"]`.
- ⚠️ Leads **sin `Última actividad` poblada quedan permanentemente fuera** del barrido (el filtro exige el campo truthy). No estampa timestamp de "cuándo se marcó". `Última actividad` se compara en UTC.

---

## 7. Reglas de Nurturing (drip 4 toques por programa) — `wf-resumen-etiquetas-seguimientos` (`DyrDumQgb6S4zHsS`) + flows ManyChat

> 🔴 **ESTAS REGLAS CAMBIAN (decisión 2026-08-17, Reporte la agencia 1).** Tres cosas:
>
> 1. **Tope global de 2 toques por contacto**, contando **todas** las secuencias juntas (outreach +
>    rescate + nurturing). Hoy el techo real es de ~9 mensajes y los 34 fallos de entrega salieron
>    100% de ahí. El reporte pide máximo 2 intentos sin respuesta.
> 2. **La cadencia se muda de ManyChat a n8n** (`vtr-despachador-proactivo-v1.json`): un cron que lee
>    el estado real de Airtable y manda **un solo** mensaje por lead. ManyChat queda como capa de
>    envío. Sin esto la lógica sigue viviendo sólo en screenshots de flows y hay que redescubrirla
>    para GHL.
> 3. **Prioridad explícita:** `recordatorio de link pendiente` **>** `nurturing por programa`. El
>    reporte pide que el recordatorio de "aún no agendaste" sea la respuesta **estándar** para todo
>    lead con link pendiente, no una excepción que compita con el broadcast genérico.
>
> El gate `asesoria=='cero'` se reemplaza por el campo real `Link asesoría enviado` (ver
> `01_mapa_funcional.md` §8.1: la whitelist del LLM omitía `agendar-ema` y rompía el gate por
> construcción).

**Corrección de mayo:** este workflow es un **DISPATCHER**, no el orquestador de la cadencia. La cadencia de 4 toques (delays **0 / 1 día / 3 días / 5 días**) vive **dentro de los flows de ManyChat**, no en n8n.

### 7.1 El dispatcher (post-conversación)

Invocado con `{tel, id_manychat}`. Espera **8 horas fijas**, lee la memoria de `n8n_chat_histories`, la manda a **gpt-4o-mini** (temp 0, jsonOutput) que produce 5 salidas: `tags` (programas), `tipo`, `resumen`, `asesoria` (`"uno"`/`"cero"`), `cualificado` (`'1'`/`'0'`). Con eso hace 4 cosas en paralelo:
1. Escribe `Tipo` en Airtable (match por Telefono).
2. Etiqueta el contacto en Clientify (1 tag por programa) + re-escribe `Programa interés` (Airtable) + `programa_interes` (ManyChat).
3. Marca `Cualificado=true` (solo si `cualificado=='1'`).
4. **Dispara el drip de nurturing por programa — SOLO si el lead NO recibió link de asesoría** (`asesoria=='cero'`).

### 7.2 Reglas del dispatcher (críticas)

- **GATE anti-doble-contacto:** el drip solo se dispara si `asesoria=='cero'`. Si el lead ya recibió link (`'uno'`), **no se envía ningún nurturing**. La detección de "recibió link" la hace el LLM contra una **whitelist de 6 URLs** (`/SPEagendar`, `/Estudiar-y-Trabajar-en-Australia`, `/AAFamilia-Agendar`, `/SummerCamp-Agendar`, `/PW_Alemania_Agendar`, `/EstudiaryTrabajar_Agendar`). ⚠️ frágil — depende de que el link aparezca literal en el historial, aunque el campo booleano `Link asesoría enviado` ya existe en Airtable y **no se usa**.
- **Routing:** Switch dispara **solo el PRIMER programa que matchea** (sin `allMatchingOutputs`), en orden de prioridad **Pathway > Summer Camp > AA Familiar > Boarding > Gap Year** (⚠️ orden que no parece deliberado). Un lead multi-programa recibe un único drip.
- **Fallback general:** si `tags` vacío **Y** no recibió link → flow "Seguimiento Lead General".
- **Cualificado (lead scoring):** `'1'` solo si (a) ya sabe 2º/3º idioma, (b) estudió en escuela privada **Y** bilingüe, (c) cumple rango de edad por programa (10–17 summer / 13–17 año académico+boarding / 18–30 pathway+gap year). Si falta algo → `'0'`. Solo marca positivo (nunca escribe `false`).

### 7.3 Catálogo de flows de nurturing (drip) — `flow_ns` ManyChat

| Programa (tag) | Nodo | `flow_ns` |
|---|---|---|
| Boarding IA | Boarding School | `content20250718115245_638127` |
| Pathway IA | Pathway | `content20250718121921_967738` |
| Gap Year IA | Gap year | `content20250718122822_491460` |
| AA Familiar IA | Año Académico | `content20250718123255_243860` |
| Summer Camp IA | Summer Camp | `content20250718123847_652764` |
| (sin tags) Lead General | Seguimiento Lead General | `content20250718124216_992343` |

### 7.4 Estructura interna de cada drip (de los screenshots ManyChat)

Los 6 flows comparten estructura: `Condición (Field is missing)` → `Add Tag (seguimiento / seguimiento_agenda)` → **msg 1** → `Wait 1 Day` → **msg 2** → `Wait 2 Days` → **msg 3** → `Wait 2 Days` → **msg 4** (delays acumulados **0 / 1 / 3 / 5 días**). Contenido educativo/nurturing de largo plazo (textos completos en `manychat-flows-content-2026-07-20.md`). ⚠️ INCIERTO — algunos cuartos mensajes no fueron capturados en los screenshots; Lead General tiene última pausa de 3 días (no 2).

### 7.5 ⚠️ Programas que quedan fuera del nurturing

El LLM del dispatcher solo emite 5 tags (Boarding/AA Familiar/Summer Camp/Pathway/Gap Year). Airtable `Programa interés` soporta 8 valores → **`Francia IA`, `Automatización - Comentarios`, y programas sin drip nunca se nurturean** por este workflow (impacto: cobertura parcial; en GHL definir qué pasa con esos leads).

---

## 8. Reglas de Normalización de Datos

### 8.1 Teléfono — múltiples representaciones (corrige/amplía mayo)

| Contexto | Formato | Método | Ejemplo |
|---|---|---|---|
| ManyChat `whatsapp_phone` | Con `+` | — | `+5214731220110` |
| Airtable Leads `id` / `Telefono` | Sin `+` | `.replace('+','')` (solo primer `+`) | `5214731220110` |
| n8n CAPI hashing (`ph`) | Solo dígitos | `.replace(/\D/g,'')` (robusto) | `5214731220110` |
| Formulario Clientify (`Edit Fields`) | Sin `+` | `.replace("+","")` (solo primer `+`, sin trim, sin validar) | `524424754070` |
| Clientify contact | Con `+` re-añadido | `"+"+telefono` | `+524424754070` |
| Supabase `session_id` (memoria) | Sin `+`, **con quirk MX** | ver 8.2 | `5214731220110` |

**Corrección de mayo:** el `sessionKey` del main es `whatsapp_phone.replace('+','')` **a secas** — NO normaliza el quirk MX (§8.2). Airtable guarda sin `+`; Clientify con `+`; los dos CRMs conviven con representaciones distintas del mismo dato.

### 8.2 Quirk MX 52 → 521 en `session_id` (NUEVO — no estaba en mayo)

Los celulares MX llegan de WhatsApp como `52XXXXXXXXXX` (12 díg) pero ManyChat y el sessionKey del main esperan `521XXXXXXXXXX` (13 díg, con el `1` de móvil). Los nodos de memoria sintética (outreach `Build Memory Texts`, rescate `Build Rescate Memory`) normalizan: **si 12 dígitos y empieza `52` → `'521'+resto`**. Fix + backfill ya aplicados en producción:
```sql
UPDATE n8n_chat_histories SET session_id = '521' || SUBSTRING(session_id FROM 3)
WHERE session_id ~ '^52[0-9]{10}$' AND NOT (message ? 'tool_calls') AND NOT (message ? 'invalid_tool_calls');
```
**Para la migración:** verificar con la query §6 de `supabase-queries-venttur.md` si quedan filas con formato viejo antes de cruzar contra `Leads.Telefono`.

### 8.3 Nombres

- SHA-256 aplica `toLowerCase().trim()` antes de hashear; sin normalización adicional (acentos/emojis se hashean tal cual).
- `splitName(full)` (outreach): primer token = nombre, resto = apellido (titleCase); vacío → `{nombre:'Lead', apellido:''}`.

---

## 9. Reglas de Datos / CRM (identidad y linkeo cross-plataforma)

### 9.1 Airtable Leads — 30 columnas (corrige "~9" de mayo)

`id`, `id_2`, `Link asesoría enviado`, `Asistió`, `Agendan cita`, `Programa interés`, `Inicio Deseado`, `Tipo`, `Grado Escolar`, `Nivel Inglés`, `Creada`, **`ID Clientify`**, **`ID Manychat`**, `Nombre Completo`, `Email`, `Fuente lead`, `Folio`, `fbclid`, `Estado conversación`, `Última actividad`, `Outreach Form Meta enviado`, `Outreach Form Meta enviado at`, `Origen`, `Toques enviados`, `Ultimo toque at`, `Ad Name`, `Platform`, `Touch 1 programado at`, `Lead Score`, `Tipo lead`.

> ⚠️ **El schema real de la base es un SUPERSET de estas 30 columnas.** Esta lista es exactamente lo que trae el **CSV export** de `leads.csv`. Pero varios workflows escriben campos que **NO están en el export**: `Contestan 1er mensaje` (checkbox, lo setean `wf-crear-contacto-clientify-airtable` y el alta del formulario) y `Cualificado` (checkbox, lo marca el dispatcher `DyrDumQgb6S4zHsS`) — existen en la base viva pero no vinieron en este CSV (probablemente exportado desde una vista que no los incluye). Además el CSV solo tiene `Nombre Completo` (no `Nombre`/`Apellido` separados, que el prompt del agente sí menciona como variables internas). Impacto para el mapeo a GHL Contacts (doc 06 §A.3): reconciliar el header real de Airtable contra este CSV antes de definir el mapping de campos — no asumir que son exactamente 30.

### 9.2 Claves foráneas que resuelven el linkeo entre plataformas

| FK en Airtable Leads | Apunta a | Cardinalidad |
|---|---|---|
| `ID Clientify` | Clientify `contact.id` | 1:1 |
| `ID Manychat` | ManyChat `subscriber_id` | 1:1 |
| `id` (= Telefono sin `+`, **con quirk MX 52→521**) | Supabase `n8n_chat_histories.session_id` | 1:1 |
| `Folio` | Airtable Folios CAPI `Folio` | 1:N (Folios CAPI tiene duplicados) |

### 9.3 Idempotencia y writes

- **Formulario landing** (`wf-formulario-clientify`, LIVE): upsert Airtable por `Telefono`; dedup Clientify por `+telefono` (GET `?phone=+X` → count==0 crea, si existe actualiza por su `id`); tag Clientify = **código de programa crudo del form** (ej. `BSG`). ⚠️ El `Programa interés` de Airtable **NO se escribe** desde este flujo (solo el tag en Clientify). Todo lead nuevo entra con `Contestan 1er mensaje=false`. ⚠️ El JSON en `00_inputs` es la versión **PRE-fix isExecuted** (el nodo `Etiquetar Contacto` rompe con "Node hasn't been executed" cuando el lead ya existía en Clientify). Ignora email/país/ciudad/folio/fbp del form.
- **`wf-crear-contacto-clientify-airtable`** (`cZUNKQyZNOHy5twQ`): update Airtable por `Telefono` marcando `Contestan 1er mensaje=true`, crea contacto Clientify, guarda `ID Clientify`. ⚠️ El nodo "Crear o actualizar" es realmente `operation: update` (no upsert — requiere que el lead ya exista) y **blanquea el `Folio`** (comportamiento no documentado, posible artefacto). NO estampa `Estado conversación` (ese es el "EDIT B" pendiente).
- **Dual/triple write:** el alta de un lead toca **Airtable + Clientify** (contacto+tag), y su conversación vive en **Supabase**. La confirmación de cita (`wf-confirmacion-agenda`) cruza los 3 sistemas: Calendar → Clientify (por nombre) → Airtable (por `ID Clientify`).

### 9.4 Confirmación de cita — `wf-confirmacion-agenda` (`2PSekVBxarsrnVBu`, LIVE)

- **Trigger:** 3 Google Calendar Triggers (`eventCreated`, poll cada minuto) sobre `dgarcia@`/`agarcia@`/`rgarcia@venttur.com` (Diego/Andrés/Rodrigo). **Corrección de mayo:** NO es un webhook de la plataforma de agendamiento.
- **Filtro `is_asesoria`:** el `summary` del evento contiene alguno de `Pathway Alemania`, `estudia`/`ESTUDIA`/`Estudia`, `ASESORÍA`, `FAMILIA`, `SUMMER`.
- **Extracción de nombre:** todo lo que sigue a la marca `<>` en el título.
- **Cruce:** nombre → Clientify (`?query=<nombre>`) → Airtable (`{ID Clientify}=results[0].id`).
- Si el lead **ya existe** en Airtable → `Agendan cita=true`. Si **no existe** → se crea (`Fuente lead='Web'`) y **NO recibe confirmación WhatsApp** (solo Telegram al equipo) → gap de cobertura silencioso.
- Confirmación WhatsApp = `setCustomFields` (`mensaje_inicial_asesoria`, `mensaje_link_asesoria`, `programa_interes`) + `sendFlow` **`content20250721163426_851504`** (flow "Agenda", que contiene el número directo de Rodrigo).
- ⚠️ INCIERTO — referencias rotas: los paths de Diego y Andrés referencian `$('Obtener ID Manychat')` / `$('Obtener ID Manychat2')` que **no existen** (solo existe `Obtener ID Manychat1`) → probablemente **solo el path de Rodrigo funciona** en producción.

### 9.5 Link enviado — `wf-actualizar-link-enviado` (`gRSMjzxggA4UePjz`)

- Disparado por el main cuando el output del agente contiene `promo.venttur.com/`. Input `{id_airtable (=teléfono), mensaje}`.
- Clasifica el programa por **substring de la URL** (LINK_MAP: `/aafamilia-agendar`→AAFamilia, `/summercamp-agendar`→SummerCamp, `/pw_alemania_agendar`→PW_Alemania, `/estudiarytrabajar_agendar`→EstudiaryTrabajar, `/estudiar-y-trabajar-en-australia`→Australia, `/agendar-ema`→EMA, `@venttur_`→Instagram; `venttur.com` sin `promo.`→Web).
- Setea `Link asesoría enviado=true` (match por `id_2`). **No guarda timestamp** ("Link asesoría enviado at" no se escribe acá).
- Etiqueta Clientify con `<programa>_link_enviado`. ⚠️ **BUG probable:** el body referencia `$('Code in JavaScript').item.json.variable` pero el Code emite `.tag` (no `.variable`) → Clientify recibe tag vacío/`undefined` (el `onError` lo oculta).
- Dispara `wf-rescate-post-link` (fire-and-forget) con `{telefono}`. El nodo `Seguimiento agenda` está **DISABLED** (solo rescate activo).

### 9.6 Seguimiento agenda (48h) — `wf-seguimiento-agenda` (`DZlSEQS5qzX1Y01K`)

Sub-workflow single-touch: espera **48h**, re-consulta Airtable por `{Telefono}`, y **solo si el lead NO tiene cita** (`Agendan cita` no presente / `exists` FALSE) dispara `sendFlow` **`content20250718124614_140983`** (copy "Hola [First Name] 👋 Hace unos días te compartí el enlace…" + tag `seguimiento_agenda`). ⚠️ Workflow **incompleto/legacy** (conserva el nodo placeholder "Replace me with your logic", `active:false`, token ManyChat hardcodeado). Es un mecanismo **separado y más simple** que el Rescate Post-Link — no confundir.

### 9.7 Anti-duplicado / ledger de dedup del main

El main usa la tabla Airtable **"Tabla apoyo (ignorar)"** (`tblLjOtFFTn9L2Zzz`) como ledger: guarda el último mensaje visto por subscriber. El nodo `Repetido?` **detiene el flujo** (rama TRUE vacía) si el nuevo `respuesta_definitiva` es idéntico al último guardado → protección infra contra reenvíos/duplicados de ManyChat (distinta de la regla de elevación por repetición del §3.6). Además: **debounce de 20 segundos** en el flow ManyChat "Recibir mensajes" (buffer anti-fragmentación antes de llamar al webhook n8n).

### 9.8 Clientify (contexto para migración — veredicto REMOVE)

Volumen real: **6.968 contactos / 2.338 deals / 266 companies / 22 custom fields**. Pipeline de ventas real (deals): "Campaña Internados Erika" (1.024), "VENTAS EMA METODOLOGÍA" (319), "Campaña Australia Abril 25" (291), "Venta SPE - Internados" (172). Status: Expired 1.875, Lost 381, Open 50, Won 32. Stages: "AGENDÓ REUNIÓN", "Cita de Ventas concretada", "Día 15/20 Seguimiento", "Gracias por asistir". **IMPORTANTE:** los workflows de producción de VTR usan Clientify **solo para contacts/tags/notes** — NO usan deals/companies/custom-fields (esos son gestión comercial **manual** del equipo Venttur). Veredicto de migración: **REMOVE** (Clientify → GHL CRM), pero con panorama completo.

---

## 10. Reglas de Reporting — `wf-correo-semanal` (`BrFfQyDfamdUzq64`, NO ACTIVO)

**Corrección de mayo:** el workflow **NO calcula las métricas** — las **consume ya agregadas** desde la tabla Airtable "Reporte semanal" (⚠️ dónde/cómo se calculan realmente no es visible: fórmulas/rollups de Airtable o proceso externo). Es puramente lectura + presentación + comentario LLM. NO tiene Telegram (solo Gmail). Está en modo prueba (`active:false`, destinatario `[EMAIL-AGENCIA]`, cuerpo arranca con "CORRER FLUJO MANUAL").

### 10.1 Métricas del embudo (columnas de "Reporte semanal", del CSV real)

`Semana`, `Created`, `Leads` (lista de teléfonos), `Cantidad total de leads`, `Cualificados`, `Cualificados (%)`, `Citas agendadas`, `Tasa de conversión a cita`, `Asisten a cita`, `Tasa de asistencia a cita`, `Conversaciones no continuadas`, `Fuente lead Rollup (from Leads)`.

### 10.2 Cómo se presentan (Code node del workflow)

- **Cualificados:** conteo directo. `Cualificados (%)` viene como **fracción 0..1** → `Math.round(x*100)`.
- **Tasa de conversión a cita** y **Tasa de asistencia a cita:** también fracción 0..1 → `*100` redondeado.
- **Fuentes:** `Fuente lead Rollup (from Leads)` es un string separado por `;` (una entrada por lead) → conteo por frecuencia en JS, ordenado desc (un `GROUP BY fuente COUNT(*)` manual).
- **`Conversaciones no continuadas`** ≈ leads que no llegaron a agendar (label del email).
- **Conclusión:** gpt-4.1-mini (temp 0.2), 1 párrafo / máx 3 oraciones, "no repitas los números".
- Trigger: lunes ~10h; ventana `IS_AFTER({Created}, DATEADD(TODAY(),-7,'days'))`; procesa **solo la primera fila**.

⚠️ INCIERTO — las **definiciones de negocio** de "Cualificado", "Cita agendada" vs "Asiste", "Conversación no continuada" no son deducibles del workflow (se infieren del label del email). El scoring de "Cualificado" real del embudo probablemente coincide con la lógica del §7.2 (idioma+escuela+edad) computada por `wf-resumen-etiquetas-seguimientos`, pero cómo llega a la tabla "Reporte semanal" no está confirmado.

### 10.3 Datos reales del embudo (del CSV `reporte-semanal.csv`)

Semanas típicas (nov 2025 – mar 2026): 35–101 leads/semana; **Cualificados ~0–5% del total** (ej. 10%/4%/0%/7%…); **Tasa de conversión a cita ~9–21%**; **Tasa de asistencia a cita ~33–100%** (muy variable con N chico). Fuentes dominantes: "Papas locales", "Francia / P. México/ Advantage", "Papas Foraneos", "Internados / Público Advantage / 3", y desde mar-2026 aparecen los ad-set names nuevos (`BOARD-PRES-V1`, `BOARD-GIRL-V1`, `BOARD-DEP-V2`, `AA-PUBLICO`).

---

## 11. Reglas de Error y Fallback

### 11.1 CAPI — folio/programa no encontrado

Rama folio: si el regex no matchea folio **o** Prog → `throw new Error('Folio o Prog no encontrado...')` → aborta → `errorWorkflow OBkUyb8fuo30DzA9`. Sin try/catch ni validación de respuesta HTTP de Meta (un 400/401 abortaría el nodo).

### 11.2 CAPI — programa no en Airtable

Si el código de programa no existe en Programas CAPI: `pixel_id` undefined → Meta devuelve 400. Sin manejo explícito.

### 11.3 CAPI — lead no existe en Leads

`existe1` (rama folio) solo condiciona el **update** del lead; el **evento CAPI se envía igual** (la atribución no depende de que el lead exista en Leads). `alwaysOutputData:true` en las búsquedas.

### 11.4 Registro de folio (landing) — folio vacío

`wf-capi-registro-folio`: folio vacío → responde `{ok:true}` **sin guardar ni loguear** (pérdida silenciosa). CREATE sin dedup → duplicados en reintentos (confirmado: 4.003 filas con repetidos).

### 11.5 Outreach — teléfono inválido / fallos de envío

- Teléfono inválido (`p:MX` edge case) → `webapp_errors`, lead no creado.
- Fallo de `createSubscriber` (Touch 1) → `Log Error` (console.log) → `Registrar Error en Supabase` **DESHABILITADO** → no se persiste.
- Touch 2/3 `sendFlow` con `neverError` sin check → fallo silencioso igual incrementa `Toques enviados`.

### 11.6 Clientify — timeout / errores

- `wf-formulario-clientify`: los 3 HTTP Clientify tienen `retryOnFail` + wait 5s + `onError: continueErrorOutput` con salida de error **desconectada** → corte silencioso (no alerta). `Etiquetar Contacto` sin retry → fallo dispara `errorWorkflow`.
- `wf-confirmacion-agenda`: Clientify sin resultados / errores Airtable → notificación Telegram genérica ("Fallo el nodo de Clientify para recordatorio" — engañoso, cubre varios fallos).
- Legacy (preservado de mayo): 504 Gateway Timeout de Clientify puede cortar la ejecución antes de Telegram, sin retries.

### 11.7 CTWA — teléfono vacío

La rama CTWA no valida que `whatsapp_phone` tenga dígitos → un teléfono vacío produce `event_id='CTWA__<ts>'` y hash de string vacío. Sin reintentos ni logging de éxito/fallo del POST a Meta.

### 11.8 errorWorkflow global

Casi todos los workflows Venttur apuntan a `errorWorkflow OBkUyb8fuo30DzA9` (`webapp_errors`), que escribe a un **Supabase central de la agencia** (no al del cliente — fuera del alcance de esta migración).

---

## 12. Marcadores de incertidumbre

| Ítem | Qué falta confirmar | Impacto | Owner / cómo resolver |
|---|---|---|---|
| Tool `contestan_2do` | El prompt instruye llamarla pero **no existe** ai_tool cableado | Métrica "contestan 2º mensaje" no se implementa; instrucción muerta | la agencia — decidir si se implementa en GHL o se descarta |
| `crear_contacto` (agente) vs `wf-crear-contacto-clientify-airtable` | Si son el mismo (el sub-workflow tiene `availableInMCP:false`, inputs sin `$fromAI`) | Ambigüedad de qué crea el contacto | Inspeccionar el toolWorkflow node del main vivo |
| Regex de folio inconsistente | Main acepta `[A-Za-z0-9_]`, CAPI acepta `.+?` | Folios con `-` no persisten en Leads pero sí generan evento CAPI | la agencia — unificar regex al migrar |
| Programas sin pixel (Summer/Pathway/Gap Year) | Si tienen tracking CAPI por otra vía | Conversiones de esos programas quizá no llegan a Meta | Cliente / Meta Business Manager — auditar pixels por programa |
| CTWA hardcodea `{Programa}='BS'` | Si es intencional (1 pixel CTWA) o placeholder | Todos los leads CTWA se atribuyen al pixel Boarding | Cliente — confirmar mapeo campaña→pixel |
| `programa_wpp` (custom field ManyChat) | Dónde/si se usa (no aparece en el CAPI) | Se asumía que CTWA ruteaba por él; no lo hace | Revisar keyword triggers CTWA en ManyChat |
| Ambigüedad "Gap Year/Estudia y trabaja" vs "Estudiar y trabajar" | Criterio de cuándo enviar cada link/experto | Agente puede enviar link/experto equivocado | Cliente — consolidar/desambiguar programas |
| `Lead Score` / `Tipo lead` (hot/warm/cold) | Dónde se calcula (no está en el JSON del outreach) | No se puede documentar la regla de scoring | Buscar automation Airtable / fórmula / versión no capturada del workflow |
| Cron outreach "5 min" | `minutesInterval` no seteado → corre cada 1 min | Drift nombre vs comportamiento (más carga de la esperada) | la agencia — confirmar en n8n vivo |
| "Estudio y Trabajo" en rescate | Clave de memoria existe pero envío nunca la alcanza (código muerto) | Leads de ese programa nunca reciben rescate | la agencia — tabla única programa→(msg,url,tag) en GHL |
| Nodos "Build Rescate Memory" con refs rotas | `$('Get Lead')` inexistente; wiring `{{first_name}}` vs `[first_name]` | Memoria sintética puede no cargarse al disparar en prod | la agencia — corregir refs antes de migrar |
| `wf-confirmacion-agenda` paths Diego/Andrés | Refs a `Obtener ID Manychat`/`2` inexistentes | Probablemente solo el path de Rodrigo funciona | la agencia — verificar en n8n vivo |
| Bug tag Clientify en `wf-actualizar-link-enviado` | `.variable` inexistente (debería ser `.tag`) | Contactos quizá etiquetados con tag vacío | Verificar tags reales en Clientify |
| Definiciones de embudo (Cualificado/Cita/No continuada) | Fórmulas exactas de "Reporte semanal" | No se puede reproducir el reporte 1:1 en GHL | Cliente — ver config de la tabla Airtable |
| Flow "Elevar" (ManyChat) | "Notify Assignees: 0 people" — posible bug | El equipo humano podría no enterarse de elevaciones | Cliente / Max — revisar config en ManyChat |
| `Timestamp` de Folios CAPI (ms vs s) | Formato exacto usado en `fb.1.{ts}.{fbclid}` | fbc malformado degradaría match de Meta | CSV muestra 13 díg (ms) → probable OK, verificar edge cases |
| Estado de deploy `wf-estado-lead` | `active:false` en el export | Puede estar pendiente de activar en n8n vivo | la agencia — confirmar en n8n |
| Access tokens / Bearer hardcodeados | Token Meta (Programas CAPI), Bearer ManyChat (`3256256:…`), Token Clientify (`3822fcd1…`), API key OpenAI en transcripción | Riesgo de seguridad en handoff | **URGENTE** — rotar y mover a credenciales antes del export |
| Debounce 20s + confirmación de canal WA | Cómo replicar en GHL; número WA/WABA/proveedor | Sin debounce, respuestas fragmentadas; falta config canal | Etapa 3 (diseño GHL) |
