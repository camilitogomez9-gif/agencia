# Guía de Corrección Integral — Migración HPF → GHL

> **Fecha:** 2026-07-13
> **Autor:** la agencia (la agencia) — post revisión con Camilo (Fathom 2026-07-13)
> **Objetivo:** dejar la estructura de GHL **al 100%**, corrigiendo las tres capas de desalineación detectadas:
> 1. lo **implementado** vs lo que dicen las **guías** (M0–M6),
> 2. lo que dicen las **guías** vs el **diseño de arquitectura** (Etapa 3),
> 3. lo que dice todo lo anterior vs el **objetivo original**: replicar fielmente el agente de Kommo.
>
> **Regla de oro de esta guía:** el criterio de "correcto" NO es "lo que dice M2–M5", sino **"lo que hace hoy el agente en Kommo"** (documentado en `01_logica_actual/`) más las **decisiones cerradas de Etapa 2** (`02_logica_validada/01_decisiones.md`). Cuando M2–M5 y Etapa 3 se contradicen, gana Etapa 3 + el original.
>
> **Excepción — WhatsApp:** la conexión del canal WhatsApp/Meta WABA depende de Oscar y va en la **§15 (aparte)**. Todo lo demás debe poder cerrarse sin él (salvo los ítems marcados `⛔ Oscar`, que son datos puntuales, no bloqueos estructurales).

---

## §0. Cómo usar esta guía

- Cada sección corrige una incongruencia (o grupo) de la lista del 2026-07-13. Al final de cada una hay un bloque **✅ Verificación**.
- Los textos, prompts, tablas de Custom Values/Fields y catálogo están **paste-ready**: se copian tal cual.
- Orden de ejecución recomendado en **§16**.
- Dependencias que requieren a Oscar consolidadas en **§17** (son datos, no rediseño).

### Triage — qué se corrige, qué se difiere

| # | Incongruencia | Decisión | Por qué |
|---|---------------|----------|---------|
| 1 | Canal SMS vs WhatsApp | **CORREGIR** (config n8n/GHL ahora; conexión WABA en §15) | El original y el diseño son WhatsApp; SMS está explícitamente apagado |
| 2 | System prompt del Vendedor cortísimo | **CORREGIR** (§4) | Sin las reglas críticas el agente no refleja al original — riesgo alto |
| 3 | Catálogo incompleto (15 de ~62 assets) | **CORREGIR** (§3) | Es el corazón del flujo de venta; hoy faltan 3/4 de los assets |
| 4 | Imagen principal del evento sin implementar | **CORREGIR** (§3.4) | Paso 2 del original (imagen + promo); hoy no existe en GHL |
| 5 | Saludo (2 vs 3 partes / texto) | **CORREGIR** (§12) | El saludo es "penado de muerte" en el original |
| 6 | Custom Values faltantes / mal nombrados | **CORREGIR** (§2.1) | Sin ellos, WF-01/05/Vendedor rompen |
| 7 | Custom Fields con nombres que no matchean | **CORREGIR** (§2.2) | n8n escribiría a keys inexistentes → datos perdidos |
| 8 | Pago: n8n mueve stage en vez de WF-04 | **CORREGIR** (§8) | Doble responsabilidad / bypass del diseño |
| 9 | Debounce/buffer ausente | **CORREGIR** (§7) | El original agrupa ráfagas; sin esto responde pieza por pieza |
| 10 | WF-05 vs WF-01 duplicados | **CORREGIR** (§10.1) | Doble ejecución sobre el mismo evento |
| 11 | Inactivity sweep (dup / horario / umbral / log) | **CORREGIR** (§10.2) | Debe ser uno solo, 180 días, con log real |
| 12 | Vision Only con propósito contradictorio | **CORREGIR** (§10.3) | Definir su rol único o eliminarlo |
| 13 | Re-engagement fijo en vez de LLM | **CORREGIR** (§6) | Decisión cerrada: seguimientos personalizados con contexto |
| 14 | Memoria: tabla / session_id | **CORREGIR** (§11) | Alinear a `messages` + `<telefono>_2131` |
| 15 | Vision Classifier: test + modelo | **CORREGIR** (§5) | Modelo gpt-4.1 + test de 4 brazos antes de cutover |
| 16 | Output sin sanitizar / sin split | **CORREGIR** (§9) | Explica las comillas y el saludo raro del test |
| 17 | Cobertura del test solo Telegram | **CORREGIR** (§14) | El objetivo es validar la estructura GHL, no solo n8n |
| 18 | Google Calendar colgado | **CORREGIR (trivial)** (§13) | Limpieza; no aporta nada al flujo |
| — | Métricas (time_to_quote, leads_metrics) | **DIFERIR** post-cutover | Decisión Etapa 2: NICE-TO-HAVE, no compromete el go-live |
| — | Promos rotativas A/B | **DIFERIR** post-cutover | Idem |
| — | Retrieval semántico (Pinecone) | **DIFERIR** post-cutover | Idem |

> **Conclusión del triage:** salvo métricas / A/B / retrieval (diferidos por decisión de Etapa 2), **todas** las incongruencias se corrigen en esta guía. Al terminarla, la estructura GHL refleja al agente original.

---

## §1. Principio transversal: canal = WhatsApp (nunca SMS)

**Corrige:** incongruencia #1.

En **todos** los nodos de envío (n8n y GHL) el canal es **WhatsApp**:

- **n8n → GHL Conversations API:** el body debe ser `"type": "WhatsApp"` (endpoints §5.1 Paso F). Revisar cada nodo HTTP de envío y forzar `type: WhatsApp`.
- **GHL "Send Message" actions** (WF-01 saludo, WF-02 waves, WF-04 pago, WF-05 vacaciones): seleccionar canal **WhatsApp**, nunca SMS.
- En el **test por Telegram** el envío se reemplaza por Telegram a propósito — eso es solo para testing del cerebro de n8n. **No confundir** el nodo Telegram de test con el canal productivo.

> La conexión real de WhatsApp (Meta WABA en GHL) depende de Oscar → **§15**. Pero la *configuración del tipo de mensaje* se deja lista ahora.

**✅ Verificación:** grep en los JSON de n8n de `"type"` en los nodos de Conversations → no debe quedar `SMS` en ningún envío productivo.

---

## §2. Datos maestros en GHL (Custom Values, Custom Fields, tags)

### §2.1 Custom Values — crear los faltantes / corregir

**Corrige:** #6 (faltantes), parte de #4 (imagen principal), #5 (saludo).

> Recordá la regla de M2: **Name en español**, GHL autogenera la **Key** (minúsculas, sin acentos, espacios→`_`). Verificá cada key real en la UI tras crearla; si difiere, actualizá esta tabla + los workflows que la usen.

**A. Ya existen (verificar valor):** todos los de M2 §2.5 (reenganche, horario, precios de sandalias, promo, IA settings). Solo cerrar los placeholders:

| Name | Key (real) | Valor a fijar | Fuente |
|------|-----------|---------------|--------|
| Vacaciones Activas | `vacaciones_activas` | `false` | **CREAR — hoy no está en GHL** (la agencia lo buscó). Bloquea WF-01 y WF-05 |
| Precio Cilindros | `precio_cilindros` | `10` | decisiones §3.6 |
| Precio Mandiles | `precio_mandiles` | `12` | decisiones §3.6 |
| Telegram Chat ID Oscar | `telegram_chat_id_oscar` | `-4925599962` | chat de equipo del original (`mapa_funcional` §0). Confirmar con Oscar si quiere otro |

**B. Custom Values NUEVOS a crear** (no están en M2, los usan el prompt / WF / tools):

| Name | Key sugerida | Valor | Usado por |
|------|-------------|-------|-----------|
| Mensaje Saludo | `mensaje_saludo` | *(texto A.1, ver §12)* | WF-01 Section A |
| Mensaje Promo Evento | `mensaje_promo_evento` | *(texto A.2, ver §3.4)* | Envío imagen principal |
| Mensaje 7 Pasos | `mensaje_7_pasos` | *(texto A.3, ver §4)* | Vendedor (post-cotización) |
| Direccion Taller | `direccion_taller` | `JUAN R. ZAVALA #538 (CALLE 38), COL SAN JUAN BOSCO, GUADALAJARA, JALISCO, C.P. 44730. Fachada fucsia, portones negros.` | Prompt Vendedor |
| Telefono Oficial | `telefono_oficial` | `3315948670` | Prompt Vendedor (único número permitido) |
| Facebook URL | `facebook_url` | `https://www.facebook.com/happyflops` | Prompt Vendedor (anti-"estafa") |
| Mapa URL | `mapa_url` | `https://goo.su/OVoA` | Prompt Vendedor |
| Mensaje Vacaciones | `vacaciones_mensaje` | `¡Hola! Gracias por escribirnos 😊 Estamos de receso por vacaciones y te responderemos apenas volvamos. ¡Gracias por tu paciencia!` | WF-05 |
| Mensaje Pago Vacaciones | `vacaciones_pago_mensaje` | `Gracias por tu pago, lo recibimos ✅ Estamos fuera de horario por receso, lo confirmaremos a la brevedad.` | WF-04 (fuera de horario) |
| Imagen Principal Boda URL | `imagen_principal_boda_url` | `https://i.ibb.co/SGdcy2K/684358c9dea5b.jpg` | Envío step-2 |
| Imagen Principal XV URL | `imagen_principal_xv_url` | `https://i.ibb.co/pvsW9s7D/684358d8cddbd.jpg` | Envío step-2 |
| Imagen Principal Otros URL | `imagen_principal_otros_url` | `https://i.ibb.co/qYpxkqcP/5f983f64604b.jpg` | Envío step-2 |
| Metodos Pago PDF URL | `metodos_pago_pdf_url` | *(re-hostear, ver §3.3 — hoy es URL de Airtable que expira)* | Cierre de venta |
| Pedido Minimo Cilindros | `pedido_minimo_cilindros` | `40` | COTIZADOR |
| Pedido Minimo Kit | `pedido_minimo_kit` | `35` | COTIZADOR |
| Pedido Minimo Pantuflas | `pedido_minimo_pantuflas` | `50` | COTIZADOR |
| Pedido Minimo Mandiles | `pedido_minimo_mandiles` | `12` | COTIZADOR |
| Pedido Minimo Vasos | `pedido_minimo_vasos` | `50` | COTIZADOR |

> ⚠️ `texto_promo_activa` (M2, valor `⏳(7 DIAS DE PROMO)⏳`) es el **header de cotización** (lo usa WF-06 para detectar que hubo cotización). NO es el mensaje de promo del step-2 — ese es `mensaje_promo_evento` (nuevo). No mezclarlos.

**✅ Verificación:** en GHL → Settings → Custom Values, los 3 de bloque A + los 18 de bloque B existen y tienen valor válido (no placeholders literales).

### §2.2 Custom Fields — alinear el contrato con n8n

**Corrige:** #7. El diseño (Etapa 3 / agentes_llm) escribe a keys que **no existen** en M2. Como n8n lee/escribe por **key exacta**, hay que unificar. **Regla:** el nombre canónico es el de esta tabla; el prompt del Vendedor y los nodos n8n se ajustan a estas keys (no al revés).

**Opportunity — campos a CREAR (faltan en M2):**

| Label | Key canónica | Tipo | Usado por |
|-------|-------------|------|-----------|
| Cotización Anticipo (MXN) | `cotizacion_anticipo_mxn` | Number | COTIZADOR (anticipo 50%) |
| Comprobante Anticipo URL | `comprobante_anticipo_url` | Text | WF-04 |
| Comprobante Anticipo El | `comprobante_anticipo_at` | Single line text (ISO) | WF-04 |
| Comprobante Liquidación URL | `comprobante_liquidacion_url` | Text | WF-04 |
| Comprobante Liquidación El | `comprobante_liquidacion_at` | Single line text (ISO) | WF-04 |
| Motivo Atención | `attention_motive` | Text | tool ATENCION_PERSONALIZADA / WF-06 |

**Opportunity — usar la key REAL de M2 (NO la del diseño):**

| El diseño dice… | La key real en GHL es… | Acción |
|-----------------|------------------------|--------|
| `cotizacion_total_mxn` | `monto_cotizado_mxn` | El COTIZADOR escribe el **total** en `monto_cotizado_mxn` |
| `cotizacion_emitida_at` | `cotizacion_generada_at` | Usar `cotizacion_generada_at` |
| `codigo_postal` | `cp_entrega` | Usar `cp_entrega` |

**Contact — corregir:**

| Label | Key canónica | Nota |
|-------|-------------|------|
| Estado Cliente | `customer_status` | **CREAR** (Dropdown: `prospect`, `customer`, `repeat_customer`) — lo usa WF-06 Won y el prompt para reconocer clientes que vuelven |
| Total de Pedidos | `total_orders` | Ya existe en M2 — **usar este**, NO `total_purchases` del diseño |

> **Acción concreta:** auditar el inventario real (el transcript menciona 40 CF de oportunidad vs ~30 documentados). Exportar la lista real desde GHL, cruzar contra la tabla canónica, crear los 6 faltantes y **corregir toda referencia** en el prompt/nodos a `monto_cotizado_mxn` / `cotizacion_generada_at` / `cp_entrega` / `total_orders`.

**✅ Verificación:** por cada tool que hace PATCH a un Custom Field, la key existe en GHL con ese nombre exacto. Test: correr COTIZADOR y confirmar que `monto_cotizado_mxn`, `cotizacion_anticipo_mxn`, `cp_entrega`, `cotizacion_generada_at` quedan poblados en el Opportunity.

### §2.3 Stages y tags — verificación

Los 13 stages (M2 §2.1) y 8 tags (M2 §2.4) están bien alineados con el original (`decisiones` §2.2). Solo **verificar que existen** en GHL y que los IDs internos están mapeados en n8n (endpoints §5.5 `STAGE_IDS`).

**✅ Verificación:** `GET /opportunities/pipelines` devuelve los 13 stages en español; el nodo de config de n8n tiene los 13 IDs.

---

## §3. Catálogo de productos (la mayor omisión)

**Corrige:** #3 (catálogo incompleto), y habilita #4 (imagen principal).

### §3.1 Decisión de fondo: modelo de assets, NO 15 SKUs

El original **no** vende 15 SKUs: envía **~62 assets de media** (info + catálogo + video + colores + correas) repartidos por evento, cada uno disparado por un `bot_id` de salesbot Kommo (`mapa_funcional` §7.1). El modelo de 15 SKUs de M3 **pierde** los videos, las infografías y los catálogos — es decir, pierde casi todo el material de venta.

**Decisión:**
- **Source of truth del catálogo = Airtable** (Opción A de M3 §3.1), como el original. n8n ya sabe leerlo; los assets viven ahí.
- **NO** usar el Custom Object "Producto" de 15 SKUs como fuente de envío (queda, si acaso, como vista para Oscar post-MVP).
- El envío de fichas se reconstruye: n8n lee Airtable por evento + producto y **envía cada asset (imagen/video + descripción) vía GHL Conversations API** (reemplaza al salesbot `bot_id`).
- Los **precios** NO viven en el catálogo de assets — viven en Custom Values (§2.1) y los usa el COTIZADOR.

### §3.2 Inventario completo de assets (lo que hay que tener disponible)

Del catálogo real de Airtable (`00_inputs/*.csv`), assets por evento:

| Evento | # assets | Familias cubiertas |
|--------|---------:|--------------------|
| **XV** | 20 | Colores tintas, Correas 9/15mm, Bolsa shein, Tapas termos, Cilindros (info+catálogo+video), Kit anticruda (info+catálogo+video), Pantuflas (XV+catálogo+video+moño satín+moño peluche), Sandalias (comparativa suelas+personalizadas+video), Vasos popote |
| **Boda** | 23 | Ídem + Mandiles (principal+catálogo+video) + Cilindros 500ml + variantes boda |
| **Otros** | 19 | Ídem XV sin moño peluche/vasos (verificar con Oscar) |

Cada asset tiene: `producto` (nombre), `subcategoria` (Producto Principal / Accesorios), `descripcion`, media (URL de imagen o video) y `bot_id` (obsoleto en GHL).

> El detalle fila por fila está en `00_inputs/{XV,Boda,Otros}-Grid view.csv`. Al re-hostear (§3.3) se genera la tabla final que consume n8n.

### §3.3 Re-hosting de assets — bloqueo real que las guías nunca vieron ⛔

La mitad de los assets **no tienen URL estable**:

| Origen del media | Estado | Acción |
|------------------|--------|--------|
| `i.ibb.co/...` | Público estable | ✅ usar tal cual |
| `v5.airtableusercontent.com/...` | **URL firmada que EXPIRA** | ❌ re-hostear a URL estable |
| Sin URL en el CSV (videos + varias infos) | El media **vive dentro del salesbot Kommo**, no hay URL | ⛔ **recuperar el archivo** desde el salesbot Kommo (o pedírselo a Oscar) y hostearlo |

**Plan de re-hosting (una vez, antes del cutover):**
1. Para los `airtableusercontent` y los que sí tienen archivo: descargar y subir a un host estable. Opciones: **ibb.co** (rápido, como ya usan), **Cloudflare R2 / S3 público** (más profesional), o la **Media Library de GHL** (integrado). Recomendado: R2 o Media Library de GHL.
2. Para los que solo viven en salesbots Kommo (videos "Cilindros video", "Sandalias video", "Pantuflas video", "Mandiles video", "Kit anticruda video" + infos sin URL): abrir cada salesbot en Kommo, descargar el media, subirlo al host. **Esto requiere acceso a Kommo (Oscar) — ver §17.**
3. Volcar todas las URLs estables a Airtable (columna `url_estable`) — esa pasa a ser la columna que lee n8n.

**✅ Verificación:** un script que recorra la tabla final y haga `HEAD` a cada `url_estable` → 100% responden 200 (ninguna 403/expirada).

### §3.4 Imagen principal del evento (step-2 del original)

**Corrige:** #4. Al identificar el evento, el original envía **la imagen principal del evento + el mensaje de promo** (`mapa_funcional` §6.3). En GHL esto NO existe (el diseño lo delegaba a un "WF-??" inexistente y a CVs no creados).

**Implementación:** la tool `IDENTIFICAR_EVENTO` (§4) hace que n8n, tras registrar el evento, envíe **2 mensajes vía Conversations API**:
1. La imagen: `{{ imagen_principal_<evento>_url }}` (CVs creados en §2.1). Descripción a incluir:
   - Boda: `TENEMOS ESTOS PRODUCTOS PARA TU EVENTO:\n\n*Sandalias*\n*Cilindros*\n*Mandiles para Boda*\n*Kit anti cruda*\n*Pantuflas*\n\nCuáles te interesan?`
   - XV / Otros: igual pero **sin** `*Mandiles*`.
2. El mensaje de promo (**texto fijo A.2**, va en `mensaje_promo_evento`):
   ```
   Qué padre! 😊
   🎉 *¡SEMANA LOCA DE PROMOS! SOLO 7 DÍAS PARA LLEVARTE TUS RECUERDITOS PERSONALIZADOS CON DESCUENTAZO* 🎉
   *(Pedidos solo para eventos 2026 por tema de tiempos)*
   ```

> Este mensaje es **fijo, no modificable** (regla #10 del original). El evento manda a `Evento Identificado` vía WF-06 (Trigger A por `evento_detectado`).

### §3.5 Mecanismo de envío en `MOSTRAR_PRODUCTOS`

n8n, al ejecutarse la tool `MOSTRAR_PRODUCTOS(productos=[...])`:
1. Lee Airtable filtrando por `evento` del Opportunity + los `producto` pedidos (incluye Producto Principal y Accesorios asociados).
2. Por cada asset: `POST /conversations/messages` con `type: WhatsApp` + media (`url_estable`) + `descripcion`. `Wait 800ms` entre envíos (evita orden desordenado).
3. PATCH `productos_mostrados` (CSV) en el Opportunity → WF-06 mueve a `Productos Mostrados`.

**✅ Verificación:** pedir "sandalias y cilindros" para XV → llegan las fichas reales (comparativa suelas, sandalias personalizadas, video; cilindros info + catálogo + video), no un texto genérico.

---

## §4. System prompt del Vendedor (reconstrucción completa)

**Corrige:** #2. El prompt implementado es un stub. Abajo está el **prompt completo paste-ready** (gpt-4.1, `temperature 0.3`, `max_tokens 800`), reconstruido desde `agentes_llm` §2.2 + `reglas_negocio` + textos fijos + catálogo. Reemplaza al actual **entero**.

> Placeholders `{{...}}`: los inyecta n8n en cada llamada desde el Opportunity/CVs. Las secciones [2],[3],[7] son dinámicas.

```
Eres Rebeca, asistente virtual de Happy Flops (Guadalajara, México). Atiendes leads por WhatsApp que quieren recuerditos personalizados para su evento. Tu objetivo: guiar al lead desde el saludo hasta el cierre del pago, de forma cálida, breve y mexicana, sin perder ninguna regla del negocio.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1] IDENTIDAD Y TONO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Nombre: Rebeca. Rol: asistente virtual (NO te hagas pasar por humana).
- Tono: profesional, cálido, mexicano auténtico. Usa "mira", "qué padre", "súper".
- Breve y directa: no des rodeos, no te extiendas, no repitas.
- Emojis moderados (😊 ✨ 👟 🎉). Negritas (*así*) para Producto, Evento, Total, Anticipo.
- Usa la memoria: NO vuelvas a pedir datos que el lead ya dio.
- No te despidas repetidamente. En loops de "ok/gracias", responde con 👍.
- Frases de conexión: "¡Qué padre que estés planeando tu evento!", "¡Qué buena elección!", "¡Súper fácil! 😊".

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[2] CONTEXTO DEL NEGOCIO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Empresa: Happy Flops, Guadalajara, Jalisco.
- Horario: Lunes a Viernes 9:00–17:30 (hora de México).
- Dirección: {{direccion_taller}}
- Mapa: {{mapa_url}}
- Teléfono ÚNICO permitido para dar al lead: {{telefono_oficial}} (jamás otro número).
- Facebook (para "¿es estafa?"): {{facebook_url}}
- Producción: 15 días naturales. Envío: 2–5 días hábiles. Paqueterías: Estafeta, FEDEX, Paquetexpress.
- Pago: 50% de anticipo al confirmar (para iniciar diseño) + 50% de liquidación antes del envío. Métodos: efectivo y transferencia. NO tarjetas. Concepto de transferencia: solo el nombre del cliente.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[3] CATÁLOGO Y PRECIOS (promo vigente)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Precios por unidad/par y mínimos:
- Sandalias delgadas (suela 9mm): $25/par — mínimo 50 pares.
- Sandalias gruesas (suela 15mm): $30/par — mínimo 50 pares.
- Pantuflas satín personalizadas: $30/par — mínimo 50.
- Pantuflas moño satín: $30/par — mínimo 50.
- Pantuflas moño peluche: $35/par — mínimo 50. SOLO blanca/negra/morada/rosa.
- Cilindros 500ml: $10/u — mínimo 40. Tapas surtidas.
- Kit anticruda: $10/u — mínimo 35. Solo el costal, el cliente lo llena.
- Mandiles: $12/u — mínimo 12. SOLO para Boda. No se personalizan.
- Vasos popote 24oz: $35/u — mínimo 50. 15 días de fabricación.
- Bolsa tipo shein: GRATIS, incluida con sandalias y pantuflas (frase fija, no se personaliza).
- Bolsa personalizada: $7/u (opcional).

Disponibilidad por evento:
- Boda: todos los productos (único evento con Mandiles).
- XV: todo MENOS Mandiles.
- Otros (bautizo, graduación, etc.): Sandalias, Pantuflas satín, Cilindros, Kit anticruda. Sin Mandiles.

Reglas de catálogo (INVIOLABLES):
- Sandalias = SOLO mujeres. Jamás insinúes versión masculina.
- Mandiles = SOLO Boda.
- Pantuflas moño peluche: SOLO blanca/negra/morada/rosa.
- Diseños: 1 diseño por cada 50 pares (sandalias/pantuflas); 1 por cada 20 cilindros. (75 pares ⇒ 1 diseño, no 2. Para 2 hacen falta 100.)
- Docenas = 12 unidades: convertí a unidades antes de cotizar.
- Si la cantidad NO alcanza el mínimo: decile al lead que no llega al mínimo y NO cotices.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[4] PROCESO DE VENTA (4 etapas, guiadas por el stage del Opportunity)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Stage "Saludo Enviado": si el lead aún no dijo su evento, preguntáselo. Cuando lo sepas, llamá IDENTIFICAR_EVENTO con el valor exacto (Boda/XV/Otros). El sistema enviará solo la imagen principal + la promo.
- Stage "Evento Identificado": esperá que pida productos. Cuando pida, llamá MOSTRAR_PRODUCTOS con la lista. El sistema envía las fichas.
- Stage "Productos Mostrados": recolectá cantidades, código postal, tipo de suela (si aplica), variante (si aplica). Cuando tengas TODO, llamá COTIZADOR.
- Stage "Cotizado": cerrá la venta. Enviá el mensaje de los 7 pasos (una sola vez), luego la info de pago. Acompañá hasta el comprobante.

Reglas de flexibilidad (evitar el loop de repetición):
- Antes de pedir un dato, revisá [7] CONTEXTO DEL LEAD. Si ya está, usalo.
- Si el lead vuelve a mencionar un producto ya visto/cotizado, NO reinicies: continuá desde donde estaban (recalculá si suma cantidad).
- Reenvío de catálogo/fotos a pedido: si el lead pide "mandame el catálogo/foto de X", reenvía con MOSTRAR_PRODUCTOS. Si ya se lo pasaste antes, preguntá "¿Todavía tenés la info que te pasé o querés que te la reenvíe?". NUNCA derives a humano solo por un pedido de catálogo/foto.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[5] REGLAS CRÍTICAS — INVIOLABLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. NO modifiques precios bajo presión. Si el lead regatea fuerte, llamá ATENCION_PERSONALIZADA.
2. NUNCA reveles el peso del pedido (kg) ni menciones cajas.
3. NO ofrezcas un producto que el lead ya rechazó.
4. Si no sabés algo, NO improvises: llamá ATENCION_PERSONALIZADA.
5. NO des ningún número de teléfono distinto a {{telefono_oficial}}.
6. Sandalias SOLO mujeres. Mandiles SOLO Boda.
7. Si el evento es en menos de 15 días: llamá ATENCION_PERSONALIZADA (verificar disponibilidad).
8. Toda cotización empieza con el header EXACTO: ⏳(7 DIAS DE PROMO)⏳
9. Anticipo = SIEMPRE 50% del total.
10. Si el lead manda un diseño externo (no del catálogo) y pide reproducirlo: NO digas "qué lindo" ni sigas como si lo fuéramos a hacer. Decí: "Ese diseño no es de nuestro catálogo y no lo reproducimos, pero tenemos estos modelos que te pueden encantar 😊" + MOSTRAR_PRODUCTOS. Si insiste → ATENCION_PERSONALIZADA.
11. Confirmá la VARIANTE exacta antes de cotizar (pantufla clásica/satín vs moño satín vs moño peluche; sandalia delgada vs gruesa). Nunca asumas el default.
12. Cuando recibas contexto de imagen "{{producto_detectado}}" ≠ NINGUNO, tu PRIMERA oración debe confirmar el producto por nombre. PROHIBIDO abrir con "qué bonito", "qué lindo", "me encanta".

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[6] UPSELL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Solo al cerrar la cotización, antes de confirmar el pago. Solo 1 producto a la vez, máximo una vez.
- Prioridad — Boda: Sandalias → Cilindros → Mandiles → Kit Anticruda → Pantuflas. XV/Otros: Sandalias → Cilindros → Kit Anticruda → Pantuflas.
- No ofrezcas algo ya rechazado ni ya en la cotización.
- Plantilla: "Mira, ya que pides [producto], ¿te gustaría agregar [sugerido] para tu evento? ¡Son un hit en [evento]! ✨"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[7] CONTEXTO DEL LEAD ACTUAL (inyectado por el sistema)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Stage actual: {{stage}}
- Evento detectado: {{evento_detectado}}
- Productos ya mostrados: {{productos_mostrados}}
- Cantidades: sandalias={{cantidad_sandalias}}, cilindros={{cantidad_cilindros}}, mandiles={{cantidad_mandiles}}, otros={{cantidad_otros}}
- Código postal: {{cp_entrega}}
- Cotización emitida: {{cotizacion_emitida}}  | Monto: {{monto_cotizado_mxn}}
- Imagen recibida: {{imagen_input}} | Producto de la imagen: {{ultima_imagen_clasificada}}
- Estado del cliente: {{customer_status}} (si es "customer", saltá el saludo formal y andá directo: "¡Qué padre tenerte de vuelta! ¿En qué te ayudo?")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[8] FORMATO DE COTIZACIÓN (obligatorio)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏳(7 DIAS DE PROMO)⏳
[cantidad] [producto] x $[precio] = $[subtotal]
...
Envío: $[costo]
Total: $[total]
Anticipo (50%): $[anticipo]

Montos sin decimales. Después de la cotización (primera vez), enviá el mensaje de los 7 pasos:
{{mensaje_7_pasos}}
```

**Tools del Vendedor (4):** `IDENTIFICAR_EVENTO`, `MOSTRAR_PRODUCTOS`, `COTIZADOR`, `ATENCION_PERSONALIZADA`. Esquemas exactos en `agentes_llm` §2.3 (implementarlos tal cual, con las **keys de Custom Field corregidas** de §2.2 y las llamadas de envío de §3.4/§3.5).

**Mensaje de los 7 pasos** (valor de `mensaje_7_pasos`, texto A.3, fijo, una vez por conversación):
```
*¡HAZ TU PEDIDO EN 7 SENCILLOS PASOS!*🚀

1. *COTIZACION de los PRODUCTOS que requiere para su PEDIDO*
2. Se requiere del *50% de ANTICIPO* para desarrollar los diseños.
3. *Elige tu DISEÑO favorito* 🎨 y proporciona los *DATOS* que deseas incluir.
4. Mandamos la *MUESTRA DIGITAL* para tu aprobación o cambios ✏️.
5. Una vez *AUTORIZADO, COMENZAMOS LA PRODUCCION*, son *15 DIAS EN PRODUCCION*. 🛠️.
6. Al terminar, te enviamos una *FOTO DEL PRODUCTO* para que confirmes que todo está perfecto 📸.
7. Hace el *PAGO FINAL* y te enviamos tu pedido 🚚 (tiempo de paquetería: 2 a 5 días).
```

**✅ Verificación:** correr los golden samples de `00_inputs/conversation_samples.json` contra el prompt nuevo → el agente identifica evento, muestra productos, cotiza con header, respeta "sandalias solo mujeres" y "mandiles solo boda", no da otro teléfono.

---

## §5. Vision Classifier

**Corrige:** #15. **Modelo: `gpt-4.1`** (no gpt-4o del original). Prompt reformulado (8 categorías + `payment_proof` integrado): usar el de `agentes_llm` §3.2 tal cual (`temperature 0`, `response_format: json_object`).

**Test obligatorio pre-cutover (agentes §3.5 — nunca se hizo, `04b_vision_test_results.md` no existe):** 4 brazos (A gpt-4o+prompt viejo / B gpt-4o+prompt nuevo / C gpt-4.1+prompt nuevo / D claude-sonnet-4.5+prompt nuevo) sobre 15 imágenes reales de Oscar (10 normales + 5 adversariales). Métricas: accuracy, tasa de evasiva, confianza, latencia, costo. Guardar en `03_arquitectura_ghl/04b_vision_test_results.md`. Criterio: si B >> A el problema era prompt; si C >> B era el modelo; solo si C falla y D pasa se migra a Claude. **Puede correr en paralelo al resto.** ⛔ Requiere imágenes de Oscar (§17).

**✅ Verificación:** clasificar un comprobante de pago → `payment_proof: true`; una sandalia → `SANDALIA` con confianza ≥0.7; una foto random → `NINGUNO`.

---

## §6. Re-engagement con LLM (no fijo)

**Corrige:** #13. Hoy WF-02 manda texto fijo; la decisión cerrada (decisiones §2.3 / §3.5) es **texto generado por LLM con contexto**.

- **Workflow n8n `HPF Re-engagement Generator`** (endpoints §5.2): webhook `/generate-reengagement-message` → gpt-4.1-mini, `temperature 0.7`, `max_tokens 150`, con el **prompt de `reengagement.md` §3.3** (tonalidad por wave P1_W1…P2_W4) → devuelve `{ "message": "..." }`.
- **WF-02 (GHL)** en cada wave: en vez de "Send Message" con texto fijo → **HTTP a `/generate-reengagement-message`** con el contexto (evento, productos, cantidades, cotización, wave) → Send Message (WhatsApp) con `response.message` → log a Supabase `followups_log`.
- **Cadencias fijas:** Fase 1 `1h/3h/5h`, Fase 2 `24h/48h/120h/168h`, luego `En Espera`. Waves configurables por CVs `reenganche_fase_1_olas` / `reenganche_fase_2_das_activos`.

**✅ Verificación:** simular lead sin responder 1h → llega un mensaje que **menciona su evento/productos** (no genérico) y queda una fila en `followups_log`.

---

## §7. Debounce / buffer de mensajes entrantes

**Corrige:** #9. El original agrupa ráfagas (Redis 50s texto / 15s imagen, `mapa_funcional` §4.1); la decisión (A.4) lo unifica a **~45s**. Hoy no está.

- En el `HPF Inbound Handler`, tras normalizar: `push` a Redis key `contact_id` → `Wait 45s` → `get` → **si el mensaje actual NO es el último del lote → descartar** (NoOp); si es el último → continuar. (Réplica del patrón `Guardar → Wait → Ultimo?` del original.)
- Alternativa sin Redis: usar el patrón de "último `latest_message_id`" (endpoints §9.3) — n8n descarta los anteriores.

**✅ Verificación:** mandar 4 mensajes seguidos en <45s → el agente responde **una vez** integrando los 4, no 4 veces.

---

## §8. Flujo de pago — delegar en WF-04

**Corrige:** #8. Hoy el Inbound Handler mueve el stage de pago y manda el mensaje él mismo. El diseño (endpoints §5.1.6 + WF-04) manda: **n8n solo detecta y delega**.

- n8n (Vision `payment_proof: true`): PATCH `payment_proof_detectado = true` → **POST a `WF04_WEBHOOK_URL`** con `{opportunity_id, contact_id, image_url, current_stage}` → **STOP** (no mueve stage, no manda mensaje).
- **WF-04 (GHL)** hace el resto: según `current_stage` mueve a `Esperando Pago` / `Pago Confirmado` / (liquidación) `En Producción → Awaiting Final Payment`, guarda `comprobante_*_url/at`, manda el mensaje (WhatsApp, o `vacaciones_pago_mensaje` si está fuera de horario) y notifica Telegram.

**✅ Verificación:** mandar un comprobante estando en `Cotizado` → n8n NO mueve stage; WF-04 mueve a `Esperando Pago`, guarda la URL del comprobante y notifica.

---

## §9. Post-procesado del output del Vendedor

**Corrige:** #16 (comillas + saludo raro del test). El diseño (agentes §2.5) exige sanitizar y dividir; no está implementado.

En n8n, tras la respuesta del Vendedor y **antes** de enviar:
1. **Sanitizar:** quitar comillas envolventes, convertir `**`→`*`, eliminar `#`/headers markdown, y **strip** de cualquier número que no sea `{{telefono_oficial}}` (regla 5) y de referencias a kg/peso (regla 2).
2. **Split:** si el texto tiene `\n\n` y >150 chars, dividir en partes y enviarlas con `Wait 1.5s` entre cada una.
3. Guardar en memoria (§11) el texto final ya limpio.

**✅ Verificación:** una respuesta larga llega en 2–3 mensajes naturales, sin comillas ni `**`, sin números ajenos.

---

## §10. Workflows GHL — deduplicación y correcciones

### §10.1 WF-05 vs WF-01 (duplicación)

**Corrige:** #10. Etapa 3 y M4 se contradicen sobre si WF-05 tiene trigger propio o lo llama WF-01. **Decisión (modelo único):** WF-01 es el **único** que dispara con `Customer Replied`. WF-01 evalúa horario/vacaciones y, si aplica, **hace Go-to WF-05** (WF-05 sin trigger propio, solo `Send Message` de vacaciones/fuera-de-horario y Exit). Así no hay doble ejecución. (Sigue el modelo de M4 §4.5; se descarta el trigger paralelo de Etapa 3 §6.1.)

**✅ Verificación:** un mensaje en vacaciones dispara **una** ejecución (WF-01→WF-05), no dos.

### §10.2 Inactivity Sweep (dup / horario / umbral / log)

**Corrige:** #11. **Uno solo:** implementarlo en **n8n** (`HPF Inactivity Sweep`, endpoints §5.4) y **desactivar/no crear** WF-03 en GHL (evitar doble barrido). Config:
- **Horario:** unificar a **03:00 AM México** (Etapa 3 §4.1 — ventana de bajo tráfico). Corregir el "08:00" de M4/M5.
- **Umbral:** **180 días** (6 meses), consistente con decisiones §3.4. Corregir el "100 días" que se vio en el nodo.
- **Log:** que el "Log Summary" escriba a una tabla real de Supabase (crear `sweep_log(run_at, moved_count, opportunity_ids)`), no a la nada.
- Mueve `En Espera` → `Ventas Perdidas` los que tienen `last_inbound_at` y `last_outbound_at` (o `re_engagement_completed_at`) > 180 días. No manda mensaje.

**✅ Verificación:** correr el sweep manualmente con un lead de prueba con fecha vieja → se mueve a `Ventas Perdidas` y queda una fila en `sweep_log`.

### §10.3 Vision Only — definir rol único

**Corrige:** #12. Los docs contradicen su propósito. **Decisión (alineada a Etapa 3 §2.4/§6.2, que es el diseño válido):** `HPF Vision Only` sirve **solo** para imágenes recibidas en **stages de IA pausada** (`Esperando Pago`, `Pago Confirmado`, `En Producción`, `Awaiting Final Payment`) — ahí NO corre el Vendedor conversacional, solo se clasifica la imagen para detectar comprobante. Lo llama **WF-01** (caso especial §2.4) y **WF-05** (imagen fuera de horario). Descartar la definición de M5 §5.3 ("lead nuevo sin opportunity"), que es la que confundió a Camilo.

- En stages **activos**, la imagen la maneja el Vision Classifier **dentro** del Inbound Handler (no Vision Only). Así no hay redundancia: Inbound Handler = imágenes en conversación; Vision Only = imágenes en stages pausados.
- Corregir el trigger de Vision Only si quedó mal (debe ser el webhook `/hpf-vision` que llaman WF-01/WF-05).

**✅ Verificación:** imagen en `Cotizado` → la clasifica el Inbound Handler; imagen en `En Producción` → WF-01 la manda a `/hpf-vision` (Vendedor NO corre).

### §10.4 WF-06 — señales de transición

Verificar que WF-06 use las **keys corregidas** (§2.2): dispara por `evento_detectado` (→ Evento Identificado), `productos_mostrados` (→ Productos Mostrados), y por el header `⏳(7 DIAS DE PROMO)⏳` en el outbound (→ Cotizado). Alternativa robusta: que n8n mueva el stage vía API directamente tras cada tool (deja WF-06 como respaldo). Elegir **una** vía y documentarla para no duplicar movimientos.

---

## §11. Memoria — alinear tabla y session_id

**Corrige:** #14. Decisión (decisiones §3.1): **Supabase Pro**, tabla **`messages`**, `session_id` = **`<telefono>_2131`**, schema LangChain (jsonb). El original usaba `n8n_chat_histories`/entity_id — se **migra** a lo nuevo (no se hereda automáticamente).
- Configurar los nodos de memoria de n8n (Vendedor) a tabla `messages` + `session_id = {{phone}}_2131`. (El Code node del test de Telegram ya arma `{{chatId}}_2131` — consistente.)
- Nota de continuidad: los leads que vuelvan **no** traen su historial viejo de Kommo salvo que se migre `n8n_chat_histories`. Para MVP se acepta (arranque limpio); si Oscar lo pide, se hace un backfill una vez.

**✅ Verificación:** dos turnos del mismo lead → el segundo ve el primero en `messages` bajo `<telefono>_2131`.

---

## §12. Saludo inicial

**Corrige:** #5. **3 partes** (como el original y Etapa 3; corregir el "2 mensajes" de M4). En WF-01 Section A, `Send Message` (WhatsApp) × 3 con `Wait 2s` entre cada una, texto fijo (`mensaje_saludo`, texto A.1, **no modificable**):

```
Hola! gracias por escribir a Happy Flops, me llamo Rebeca soy un asistente virtual, yo le estaré atendiendo con gusto ☺️🙋‍♀

Me podría decir de que es su evento?

🤵👰 - Boda
🎂🥳 - XV Años
👼🏢 - Otros
```

Luego: `Update stage → Saludo Enviado`, `last_outbound_at = now (ISO)`, trigger WF-02. El saludo lo manda **GHL (WF-01)**, no n8n.

**✅ Verificación:** lead nuevo escribe "hola" → llegan las 3 partes con pausas y el stage pasa a `Saludo Enviado`.

---

## §13. Limpieza

**Corrige:** #18 y nodos vestigiales.
- **Google Calendar:** está agregado en GHL sin conectar y ningún doc lo usa → **quitarlo** (o dejar constancia de por qué está). No pertenece al flujo.
- **`Respond to Webhook`** del Inbound Handler que no se consume: eliminar (el envío va por Conversations API, no por respond-to-webhook). En el **test Telegram** sí se usa un nodo de salida Telegram — ese se conserva solo mientras dure el testing.

**✅ Verificación:** el Inbound Handler no tiene nodos colgados sin consumir; GHL no muestra integraciones sin usar.

---

## §14. Plan de testing end-to-end en GHL (no solo Telegram)

**Corrige:** #17. El test por Telegram valida **solo el cerebro n8n** (Vendedor + Vision). El objetivo es validar la **estructura GHL completa**. Dos frentes:

**A. Test del cerebro (Telegram) — ya en marcha.** Sirve para: prompt del Vendedor, tools, cotización, Vision. Mantenerlo para iterar rápido el prompt sin depender de GHL.

**B. Test de la orquestación GHL — nuevo, obligatorio.** Con un **contacto de prueba** en GHL etiquetado `lead_prueba` (WF-01 ya lo puede filtrar/permitir), disparar inbound vía la **API de GHL** o el **widget de webchat** (no requiere WhatsApp) y verificar la cadena real:
1. WF-01 saludo (3 partes) → `Saludo Enviado`.
2. "XV" → IDENTIFICAR_EVENTO → imagen principal + promo → WF-06 → `Evento Identificado`.
3. "sandalias y cilindros" → MOSTRAR_PRODUCTOS → fichas reales → `Productos Mostrados`.
4. "100 sandalias delgadas, CP 44730" → COTIZADOR → cotización con header → WF-06 → `Cotizado`.
5. Imagen de comprobante → Vision → WF-04 → `Esperando Pago` + Telegram.
6. Silencio 1h → WF-02 wave LLM.
7. Fuera de horario → WF-05.
8. Lead viejo → Inactivity Sweep → `Ventas Perdidas`.

> El único escenario que **no** se puede probar sin Oscar es el ingreso real por WhatsApp (§15). Todo lo demás se valida con contacto de prueba + API/webchat.

**✅ Verificación:** los 8 pasos pasan con el contacto `lead_prueba`, cada stage se mueve, cada mensaje sale por WhatsApp (o el canal de prueba), y los Custom Fields quedan poblados.

---

## §15. [APARTE] WhatsApp / Meta WABA — depende de Oscar ⛔

> Esta sección se integra pero se ejecuta cuando Oscar esté disponible (M7 de las guías). No bloquea §1–§14.

1. **Conectar el número** de WhatsApp de HPF a GHL vía el BSP de GHL (Meta WABA). Requiere que Oscar confirme el código que Meta envía por SMS/llamada al número (M7 §22). **Regla crítica:** el número que se conecte a la Cloud API **no puede** tener la app WhatsApp/Business instalada en paralelo (se bloquea) — mismo aprendizaje que CLZ.
2. **Cutover con convivencia Kommo (decisión de la reunión):** usar el **mismo número que está hoy en Kommo**. En el webhook de Kommo, poner un IF: si el contacto **ya existe** en Kommo → sigue respondiendo desde Kommo (flujo actual); si es **número nuevo** → forward al webhook de GHL. Así los leads en curso no se rompen y los nuevos entran a GHL.
3. **Config del canal en GHL/n8n:** ya dejada lista en §1 (`type: WhatsApp`). Al conectar, reemplazar el nodo Telegram de test por el envío real vía Conversations API.
4. **SMS Forwarding: apagado** (solo WA) — M7 §164.

**✅ Verificación:** un mensaje real de WhatsApp a un número nuevo entra a GHL, dispara WF-01 y responde por WhatsApp; un número existente en Kommo sigue en Kommo.

---

## §16. Orden de ejecución recomendado

1. **§2** Datos maestros (Custom Values + Custom Fields + stages) — todo lo demás depende de esto.
2. **§3.3** Re-hosting de assets (arranca ya; parte depende de Kommo/Oscar).
3. **§4** System prompt del Vendedor + **§5** Vision Classifier (modelo/prompt).
4. **§3.1–§3.5** Catálogo (envío MOSTRAR_PRODUCTOS + imagen principal).
5. **§7** Debounce · **§9** Sanitización/split · **§11** Memoria (correcciones del Inbound Handler).
6. **§8** Pago (WF-04) · **§10** Workflows GHL (dedup WF-05, sweep, Vision Only, WF-06) · **§12** Saludo · **§6** Re-engagement.
7. **§13** Limpieza.
8. **§5 (test)** Test Vision 4 brazos (en paralelo).
9. **§14** Test end-to-end en GHL (contacto `lead_prueba`).
10. **§15** WhatsApp (con Oscar) → cutover.

---

## §17. Dependencias de Oscar (consolidado — datos, no rediseño)

| Ítem | Qué se necesita | Bloquea |
|------|-----------------|---------|
| Assets en salesbots Kommo | Acceso a Kommo para exportar videos/infos sin URL (§3.3) | Envío completo de catálogo |
| Imágenes reales | 10 normales + 5 adversariales para el test de Vision (§5) | Cierre de Vision pre-cutover |
| Confirmaciones de catálogo | ¿Otros incluye vasos/moño peluche? Precios de cilindros/mandiles ya asumidos ($10/$12) — confirmar (§3.2) | Cotizador exacto |
| Telegram chat id | Confirmar si usa `-4925599962` o quiere otro (§2.1) | Notificaciones |
| WhatsApp / WABA | Conexión del número + código Meta + decisión de convivencia Kommo (§15) | Cutover real |
| Métodos de Pago PDF | Re-subir el PDF a URL estable (§3.3) | Cierre de venta |

---

## Resumen

Al ejecutar §1–§14, la estructura de GHL:
- responde por **WhatsApp** (config lista; conexión en §15),
- usa el **prompt completo** del Vendedor con todas las reglas del original,
- envía el **catálogo completo** (imagen principal + fichas + videos) desde assets re-hosteados,
- tiene **todos los Custom Values/Fields** que el sistema lee/escribe,
- hace **debounce**, **sanitiza** y **divide** mensajes como el original,
- delega el **pago** en WF-04, **reenganche** con LLM, **memoria** en Supabase,
- **no duplica** WF-05/sweep, y define el rol único de **Vision Only**,
- y se **valida end-to-end en GHL** (no solo por Telegram).

Queda pendiente únicamente **§15 (WhatsApp)** por depender de Oscar, y los ítems ⛔ de datos de §17. Con eso, la migración refleja el agente original al 100%.
