# M2 — Pipeline, Custom Fields y Custom Values

> **Referencia:** `03_arquitectura_ghl/01_pipeline_ghl.md` y `03_arquitectura_ghl/02_data_model.md`  
> **Tiempo estimado:** 3-4 horas  
> **Prerequisito:** M1 completo

---

## ⚠️ Convención de idioma (2026-06-19)

Toda la cuenta de GHL se configura **en español** (decisión la agencia). Para que la UI quede en español **sin romper la integración con n8n**, aplicamos esta regla:

| Elemento | Idioma | Motivo |
|----------|--------|--------|
| **Stage names** (nombres de etapa) | 🇪🇸 Español | Visible en UI. n8n los referencia por **ID interno**, no por nombre → traducir es seguro. |
| **Field Label** (etiqueta del campo) | 🇪🇸 Español | Es lo que ve Oscar en la UI. |
| **Field Key** (clave del campo) | 🇬🇧 snake_case | **NO tocar.** Es el contrato técnico que n8n lee/escribe (`{ "key": "...", "value": ... }`). No es lo "visible". |
| **Tags** | 🇪🇸 Español | El tag ES su propio identificador (no hay label/key aparte). Al traducirlos se actualizan TODAS las referencias en M4 y M5 en cadena. |
| **Custom Value Name** | 🇪🇸 Español | Visible en UI. |
| **Custom Value Key** | 🇪🇸 autogenerada por GHL desde el Name | **NO editable.** GHL la genera a partir del Name (minúsculas, espacios→`_`, sin acentos). La fuente de verdad de cada key real está en §2.5. Se usa en `{{custom_values.key}}` y en n8n. |
| **Nombres de Workflow** (WF-0X) | 🇪🇸 Español | Visible en Automation. Se conserva el prefijo `WF-0X` como ID operativo. |

> 📌 **Regla mnemotécnica:** lo que **ve** el usuario → español. La **clave** que usa el código → snake_case en inglés intacta.

### Mapeo de stages EN → ES (referencia para todos los módulos)

| Inglés (docs viejos) | Español (UI real) |
|----------------------|-------------------|
| Incoming Lead | **Lead Nuevo** |
| Greeting Sent | **Saludo Enviado** |
| Event Identified | **Evento Identificado** |
| Products Shown | **Productos Mostrados** |
| Quoted | **Cotizado** |
| Awaiting Payment | **Esperando Pago** |
| Payment Confirmed | **Pago Confirmado** |
| Design In Progress | **Diseño en Proceso** |
| In Production | **En Producción** |
| Shipped | **Enviado** |
| En espera | **En Espera** |
| Won | **Ganado** |
| Ventas Perdidas Real | **Ventas Perdidas** |

### Mapeo de tags EN → ES

| Inglés | Español |
|--------|---------|
| human_takeover | **atencion_humana** |
| re_engagement_phase_1 | **reenganche_fase_1** |
| re_engagement_phase_2 | **reenganche_fase_2** |
| re_engagement_completed | **reenganche_completado** |
| paused | **pausado** |
| is_test_lead | **lead_prueba** |
| pago_detectado | pago_detectado *(ya en español)* |

---

## 2.1 Crear el Pipeline "Happy Flops IA"

**CRM → Pipelines → Add Pipeline**

- **Pipeline Name:** `Happy Flops IA`
- Desactivar cualquier pipeline de ejemplo que GHL cree por defecto.

### Stages a crear (en orden):

| # | Nombre del Stage | Color sugerido | Rotting (días) |
|---|-----------------|----------------|----------------|
| 1 | **Lead Nuevo** | Gris | — |
| 2 | **Saludo Enviado** | Azul claro | 1 |
| 3 | **Evento Identificado** | Azul | 2 |
| 4 | **Productos Mostrados** | Celeste | 3 |
| 5 | **Cotizado** | Amarillo | 4 |
| 6 | **Esperando Pago** | Naranja | 7 |
| 7 | **Pago Confirmado** | Verde claro | 3 |
| 8 | **Diseño en Proceso** | Verde | 5 |
| 9 | **En Producción** | Verde oscuro | 10 |
| 10 | **Enviado** | Teal | 3 |
| 11 | **En Espera** | Gris oscuro | — |
| — | **Ganado** | Verde brillante | (terminal) |
| — | **Ventas Perdidas** | Rojo | (terminal) |

> El rotting es opcional pero ayuda a Oscar a ver leads estancados visualmente. Podés dejarlo en 0 si preferís no tener alertas visuales.

Para cada stage: **Add Stage → [nombre] → Save**

✅ Verificar que los 13 stages aparecen en el orden correcto.

---

## 2.2 Custom Fields — Contact

**Settings → Custom Fields → Contacts → Add Field**

Crear los siguientes campos:

| Field Label (UI, español) | Field Key (NO tocar) | Tipo | Opciones / Notas |
|---------------------------|----------------------|------|-----------------|
| Reenganche Pausado | `re_engagement_paused` | Checkbox | Default: false |
| Lead de Prueba | `is_test_lead` | Checkbox | Default: false |
| Idioma Preferido | `preferred_language` | Dropdown | `es-MX`, `es-419` |
| Total de Pedidos | `total_orders` | Number | Default: 0 |
| Valor de Vida (MXN) | `lifetime_value_mxn` | Number | Default: 0 |

> ⚠️ **Importante:** GHL genera el **Field Key** automáticamente desde el Label. Como acá el Label está en español, el Key autogenerado saldría distinto (`reenganche_pausado`, etc.). Después de crear cada campo, **editá el Field Key manualmente** para que quede EXACTAMENTE como la columna "Field Key" de arriba — n8n los referencia por esa clave. El Label sí puede quedar en español.

---

## 2.3 Custom Fields — Opportunity

**Settings → Custom Fields → Opportunities → Add Field**

Estos son los campos más importantes — son los que n8n lee y escribe en cada conversación.

> ⚠️ Igual que en §2.2: el **Label** va en español, pero después de crear cada campo **fijá el Field Key manualmente** para que coincida exacto con la columna Key (n8n lo necesita).

> ⏱️ **GHL NO soporta el tipo Date/Time en custom fields — solo Date (sin hora).** Para los timestamps que la lógica de reenganche necesita con precisión de hora/minuto, usamos **Single line text en formato ISO 8601** (ej. `2026-07-15T14:30:00Z`) y la comparación de fechas vive en **n8n** (que parsea el ISO con precisión total). Los timestamps cuya granularidad de día alcanza quedan como **Date** nativo. Detalle por campo en cada bloque.

### Bloque A: Datos del evento

| Label (UI, español) | Key (NO tocar) | Tipo | Opciones |
|---------------------|----------------|------|----------|
| Evento Detectado | `evento_detectado` | Dropdown | XV, Boda, Bautizo, Cumpleaños, Empresarial, Otro |
| Imagen Recibida | `imagen_input` | Checkbox | Default: false |
| Productos Mostrados | `productos_mostrados` | Text | (JSON array como string) |
| Última Imagen Clasificada | `ultima_imagen_clasificada` | Text | |
| Comprobante Detectado | `payment_proof_detectado` | Checkbox | Default: false |

### Bloque B: Cotización

| Label (UI, español) | Key (NO tocar) | Tipo | Opciones |
|---------------------|----------------|------|----------|
| Cantidad Sandalias | `cantidad_sandalias` | Number | |
| Talla Sandalias | `talla_sandalias` | Text | |
| Tipo Suela | `tipo_suela` | Dropdown | Delgada, Gruesa, Yute |
| Cantidad Cilindros | `cantidad_cilindros` | Number | |
| Cantidad Mandiles | `cantidad_mandiles` | Number | |
| Cantidad Otros | `cantidad_otros` | Number | |
| Código Postal de Entrega | `cp_entrega` | Text | |
| Cotización Emitida | `cotizacion_emitida` | Checkbox | Default: false |
| Monto Cotizado (MXN) | `monto_cotizado_mxn` | Number | |
| Cotización Generada El | `cotizacion_generada_at` | Date | |

### Bloque C: Seguimientos / Reenganche

| Label (UI, español) | Key (NO tocar) | Tipo |
|---------------------|----------------|------|
| Último Mensaje Saliente El | `last_outbound_at` | **Single line text (ISO 8601)** ⏱️ |
| Último Mensaje Entrante El | `last_inbound_at` | **Single line text (ISO 8601)** ⏱️ |
| Última Ola de Reenganche | `last_re_engagement_wave` | Text |
| Reenganche Completado El | `re_engagement_completed_at` | Date |
| Tuvo Información | `had_information` | Checkbox |
| Tuvo Imagen | `had_image` | Checkbox |
| Tuvo Cotización | `had_quote` | Checkbox |

> ⏱️ **`last_outbound_at` y `last_inbound_at` son críticos para el reenganche** (olas a 1h/3h/5h y el check "¿el lead respondió?" comparan dentro del mismo día). Por eso van como **Single line text ISO 8601**, NO Date. **n8n es el único escritor canónico** y los escribe con `$now.toISO()`. La comparación `last_inbound_at < workflow_started_at` se resuelve en n8n parseando el ISO. `re_engagement_completed_at` mide 180 días → **Date** alcanza.

### Bloque D: Post-venta

| Label (UI, español) | Key (NO tocar) | Tipo |
|---------------------|----------------|------|
| Diseño Aprobado El | `diseno_aprobado_at` | Date |
| Fecha Prometida de Envío | `fecha_prometida_envio` | Date |
| Número de Guía | `tracking_number` | Text |
| Paquetería | `paqueteria` | Text |
| Notas Post-venta | `notas_postventa` | Text Area |

### Bloque E: Métricas (post-MVP, crear igualmente)

| Label (UI, español) | Key (NO tocar) | Tipo |
|---------------------|----------------|------|
| Fecha Primer Contacto | `created_at_first_contact` | Date |
| Horas Hasta Cotizar | `time_to_quote_hours` | Number |
| Horas Hasta Cerrar | `time_to_close_hours` | Number |

> ⏱️ **Cuando se activen las métricas (post-MVP):** `Horas Hasta Cotizar` / `Horas Hasta Cerrar` necesitan precisión de hora. Dos opciones: (a) cambiar `created_at_first_contact` + `cotizacion_generada_at` a **Single line text ISO 8601** y que n8n calcule las horas; o (b) **mejor** — no crear `created_at_first_contact` como CF y usar el timestamp nativo de GHL **"Date Added"** del contacto (tiene hora completa), calculando las métricas en n8n al momento de cerrar. Para MVP queda como **Date** porque las métricas no están activas.

✅ Verificar en Opportunities que aparecen todos los custom fields al abrir un registro.

---

## 2.4 Tags predefinidos

**Settings → Tags → Add Tag** — crear los siguientes (en español; el tag ES su propio identificador, n8n los aplica por este string):

| Tag (español) | Reemplaza a (doc viejo) | Cuándo se aplica |
|---------------|-------------------------|-----------------|
| `atencion_humana` | `human_takeover` | Tool ATENCION_PERSONALIZADA invocada |
| `reenganche_fase_1` | `re_engagement_phase_1` | Inicio de olas Fase 1 |
| `reenganche_fase_2` | `re_engagement_phase_2` | Inicio de olas Fase 2 |
| `reenganche_completado` | `re_engagement_completed` | Fin del ciclo completo sin respuesta |
| `pausado` | `paused` | Oscar pausa manualmente (distinto al CF `re_engagement_paused`) |
| `vacaciones` | — | No se usa en tag — se usa Custom Value global |
| `lead_prueba` | `is_test_lead` | Lead de prueba, excluir de reportes |
| `pago_detectado` | — | Vision Classifier confirmó comprobante |

---

## 2.5 Custom Values (configuración global del sub-account)

**Settings → Custom Values → Add Custom Value**

Estos son los "toggles" que Oscar puede editar sin tocar workflows. Crear todos aunque algunos tengan valores post-MVP.

> 🔒 **GHL autogenera la Key del Custom Value desde el Name y NO permite editarla después.** El algoritmo de GHL: pasa el Name a minúsculas, reemplaza espacios por `_`, **elimina acentos y caracteres no-ASCII** (por eso `Días` → `das`, `Número` → `nmero`, `Mínimo` → `mnimo`). La columna **"Key (real, autogenerada)"** de abajo es la **fuente de verdad** — esa es la key con la que se referencia el CV en GHL merge fields y en n8n. Cualquier doc previo que muestre otra key (ej. la vieja convención `re_engagement_fase1_active`) queda obsoleto; reemplazar por la real de esta tabla.
>
> 💡 **Si querés keys más limpias en futuros CVs** (sin perder los actuales): creá el Name **sin acentos y sin paréntesis** desde el principio (ej. "Horario Inicio" en vez de "Horario Inicio (hora local)") → GHL genera `horario_inicio` directo. Para los que ya están creados, **no los toques** — renombrar el Name no cambia la Key (queda colgada).

### Categoría: Reenganche

| Name (UI, español) | Key (real, autogenerada) | Valor default |
|--------------------|--------------------------|---------------|
| Reenganche Fase 1 Activa | `reenganche_fase_1_activa` | `true` |
| Reenganche Fase 1 Olas | `reenganche_fase_1_olas` | `1h,3h,5h` |
| Reenganche Fase 2 Activa | `reenganche_fase_2_activa` | `true` |
| Reenganche Fase 2 Días Activos | `reenganche_fase_2_das_activos` | `R1,R2,R3,R4` |

### Categoría: Horario y Vacaciones

| Name (UI, español) | Key (real, autogenerada) | Valor default |
|--------------------|--------------------------|---------------|
| Vacaciones Activas | `vacaciones_activas` | `false` |
| Horario Inicio (hora local) | `horario_inicio_hora_local` | `9` |
| Horario Fin (hora local) | `horario_fin_hora_local` | `18` |
| Días Laborales | `das_laborales` | `1,2,3,4,5` (Lun=1, Dom=7) |
| Mensaje Fuera de Horario | `mensaje_fuera_de_horario` | `¡Hola! Gracias por escribirnos. Nuestro horario es de lunes a viernes de 9 a 18 hrs (CST). Te responderemos en cuanto abramos 😊` |

### Categoría: Catálogo y Precios

| Name (UI, español) | Key (real, autogenerada) | Valor default |
|--------------------|--------------------------|---------------|
| Precio Sandalias Delgadas | `precio_sandalias_delgadas` | `25` |
| Precio Sandalias Gruesas | `precio_sandalias_gruesas` | `30` |
| Precio Sandalias Yute | `precio_sandalias_yute` ⚠️ verificar en GHL | `35` |
| Precio Cilindros | `precio_cilindros` | `[confirmar con Oscar]` |
| Precio Mandiles | `precio_mandiles` | `[confirmar con Oscar]` |
| Pedido Mínimo Sandalias | `pedido_mnimo_sandalias` | `50` |
| Texto Promo Activa | `texto_promo_activa` | `⏳(7 DIAS DE PROMO)⏳` |
| Promo Activa | `promo_activa` | `true` |

### Categoría: IA Settings

| Name (UI, español) | Key (real, autogenerada) | Valor default |
|--------------------|--------------------------|---------------|
| IA Activa Global | `ia_activa_global` | `true` |
| Modelo Vendedor | `modelo_vendedor` | `gpt-4.1` |
| Modelo Vision | `modelo_vision` | `gpt-4.1` |
| Temperatura Vendedor | `temperatura_vendedor` | `0.3` |
| Max Tokens Vendedor | `max_tokens_vendedor` | `800` |
| Número WA Negocio | `nmero_wa_negocio` | `+523327682994` |
| Telegram Chat ID Oscar | `telegram_chat_id_oscar` | `[chat_id de Oscar]` |

> Los valores de precios de cilindros y mandiles: Oscar los confirma antes del go-live. Por ahora dejá `0` como placeholder para no bloquear la configuración de workflows.
>
> ⚠️ **`precio_sandalias_yute`** quedó sin verificar en la tabla de la agencia (celda vacía). Confirmar en la UI de GHL después de crearlo: si por la regla de autogenerate dio `precio_sandalias_yute` exacto, no hace falta cambiar nada en los docs; si dio algo distinto, actualizar acá Y en M4/M5.

### Mapeo de Custom Value keys (vieja → real)

Para que M3-M9 y los docs de arquitectura no se queden con keys obsoletas:

| Convención vieja (snake_case inglés) | Key real GHL (autogenerada) |
|---------------------------------------|------------------------------|
| `re_engagement_fase1_active` | `reenganche_fase_1_activa` |
| `re_engagement_fase1_waves` | `reenganche_fase_1_olas` |
| `re_engagement_fase2_active` | `reenganche_fase_2_activa` |
| `re_engagement_fase2_active_days` | `reenganche_fase_2_das_activos` |
| `vacaciones_active` | `vacaciones_activas` |
| `business_hours_start` | `horario_inicio_hora_local` |
| `business_hours_end` | `horario_fin_hora_local` |
| `business_days` | `das_laborales` |
| `off_hours_message` | `mensaje_fuera_de_horario` |
| `pedido_minimo_sandalias` | `pedido_mnimo_sandalias` |
| `promo_texto_activo` | `texto_promo_activa` |
| `ia_modelo_vendedor` | `modelo_vendedor` |
| `ia_modelo_vision` | `modelo_vision` |
| `ia_temp_vendedor` | `temperatura_vendedor` |
| `ia_max_tokens_vendedor` | `max_tokens_vendedor` |
| `wa_numero_negocio` | `nmero_wa_negocio` |

(Sin cambios: `precio_sandalias_delgadas`, `precio_sandalias_gruesas`, `precio_sandalias_yute`, `precio_cilindros`, `precio_mandiles`, `promo_activa`, `ia_activa_global`, `telegram_chat_id_oscar`.)

✅ Verificar que todos los Custom Values aparecen en el listado y son editables.

---

## ✅ Checklist M2

- [x] Pipeline "Happy Flops IA" creado con 13 stages **en español** en orden correcto
- [x] 5 Custom Fields de Contact creados (Label español + Key snake_case verificado)
- [x] Todos los Custom Fields de Opportunity creados (Bloques A-E, Label español + Key snake_case verificado)
- [x] 8 tags **en español** predefinidos creados
- [x] Todos los Custom Values creados (Name español + Key real-autogenerada GHL) con valores default

---

## 📋 Placeholders pendientes de M2 (cierre antes del cutover / M5)

Valores que quedaron stub durante el setup y deben confirmarse con Oscar antes de que los workflows o el agente los consuman.

| # | Custom Value | Valor actual (stub) | Acción | Bloquea |
|---|--------------|---------------------|--------|---------|
| 1 | `precio_cilindros` | `[confirmar con Oscar]` | Pedir a Oscar el precio unitario MXN vigente. Mientras tanto: dejar `0` (no `[confirmar...]` literal — rompe cálculos JS si el Cotizador lo lee). | M5 (Cotizador) y M8 (testing T-03) |
| 2 | `precio_mandiles` | `[confirmar con Oscar]` | Idem #1. | M5 (Cotizador) y M8 |
| 3 | `telegram_chat_id_oscar` | `[chat_id de Oscar]` | Pedirle a Oscar que le escriba al bot Telegram de la agencia una vez; obtener el `chat_id` desde `getUpdates`. Pegarlo como número (sin comillas). | M5 (tool `ATENCION_PERSONALIZADA` → notify_telegram) y M8 (test T-08) |
| 4 | Key real `precio_sandalias_yute` | sin verificar (celda vacía en la tabla original) | Abrir GHL → Custom Values → Precio Sandalias Yute → copiar la key autogenerada. Si NO es `precio_sandalias_yute` exacto, actualizar §2.5 + M4 + M5 (el script de bootstrap usa este string). | Solo cosmético si la key sale como se asume; bloqueante si difiere |

> ⚠️ **Tip operativo para los 3 primeros:** dejar el Custom Value creado con un valor **válido por tipo** (Number→`0`, Text→string vacío o `pending`), NO con el placeholder literal `[confirmar con Oscar]`. Así los workflows no rompen al leerlo; el Cotizador devolverá `0` y eso es visible en testing → fuerza el cierre del placeholder antes del go-live.

**Siguiente:** M3 → Custom Object: Producto
