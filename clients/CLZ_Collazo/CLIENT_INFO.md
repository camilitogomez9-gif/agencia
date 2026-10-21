# CLZ — Collazo Servicio Técnico

## Datos generales
- ID: CLZ
- Nombre: Collazo Servicio Técnico
- Niche: generic
- Fecha inicio: 2026-04-17
- Status: **live** — pendientes al 2026-08-05: (1) **terminar de setear el Round Robin**; (2) **agregar `"phone": "{{phone}}"` al External Request del flow Default Reply en ManyChat** — único paso que falta para activar el prefill de teléfono en los links de cal.com, ya deployado en n8n (ver `06_docs/guia-prefill-telefono-calcom-2026-08-05.md`). Resueltos: pago anual arreglado, plantilla Utility aprobada, **broadcast de cambio de número ejecutado (409/426 entregados, $5,32)**, formularios de los 9 event types del team cal.com replicados con teléfono obligatorio. Descartados: recuperar el número viejo `+598 91339312` de la WABA de Chatrace y el re-test dedicado de precios/links

## Stack activo
- [x] n8n
- [ ] Airtable
- [ ] Clientify
- [ ] Google Sheets
- [x] WhatsApp (Cloud API vía ManyChat — número nuevo, ver Notas críticas)
- [ ] Notion
- [x] OpenAI (GPT-4o agente, GPT-4o-mini formateador)
- [x] PostgreSQL (memoria de chat + round-robin state)
- [x] ManyChat (canal de mensajería, reemplaza a Chatrace desde 2026-06-30)
- [~] Chatrace (deprecado — número viejo +598 91339312 sigue atrapado en su WABA, gestión de liberación en curso)
- [x] cal.com (reservas online + webhooks BOOKING_CREATED/CANCELLED/RESCHEDULED)
- [x] Google Calendar (Matías + Fabián — 2 credenciales OAuth)

## Contactos clave
| Rol | Nombre | Contacto |
|-----|--------|---------|
| Decisor | Collazo | — |
| Técnico | | |

## OKRs del proyecto
1. Agente conversacional que responde consultas sobre servicios técnicos (aires, calefones, electricidad)
2. Guiar usuarios a reservar visita técnica via cal.com según el servicio detectado
3. Seguimiento automático: 8 hs después de iniciar conversación, envía mensaje via Chatrace

## Notas críticas
- Zona de cobertura: todo Montevideo + Ciudad de la Costa, zonas de Canelones e interior
- Horarios: Lunes a Viernes 9–19 hs, Sábados 9–13 hs, Domingos sin servicio
- **Canal (desde 2026-06-30): ManyChat + WhatsApp Cloud API**, con número nuevo (el histórico +598 91339312 quedó bloqueado en la WABA de Chatrace tras dar de baja la cuenta — gestión de liberación en curso con Meta y ManyChat, sin resolver). Detalle completo del incidente y la migración: `06_docs/migracion-whatsapp-manychat-2026-06-30.md`.
- **Regla crítica — nunca instalar WhatsApp/WhatsApp Business app en el número conectado a ManyChat.** La Cloud API y la app son excluyentes; si se registra en la app, el número se desconecta de ManyChat y hay que repetir todo el proceso de conexión. Cualquier edición de perfil (foto, horarios, "acerca de") se hace desde WhatsApp Manager (Meta Business Manager) o desde ManyChat, nunca desde la app.
- Canal legacy: Chatrace (API token: `1739376.ScNUePkJWrVgIMwoDwZLstrRBzrmY7sIeea726GZz`) — en desuso, solo relevante para el trámite de liberación del número viejo.
- Política de visita sin reserva aceptada: $750 UYU
- El agente envía links de cal.com directamente en el chat, nunca pide día/hora manualmente
- Tools de reserva (aire instalación/mantenimiento/reparación; calefón instalación/reparación; eléctrico cortocircuito/asesoramiento) están deshabilitadas en el workflow — el agente usa links cal.com en su lugar
- Seguimiento: sub-workflow espera 8 hs luego de activarse y envía mensaje via Chatrace template `1755533389285`
- n8n credentials: `OpenAI | Collazo` (id: acG9u3QTjVmvzcGO), Postgres `Collazo` (id: HRV9xsfYlr934XEB). Pendiente crear `Google Calendar | Collazo Matías` y `Google Calendar | Collazo Fabián`.
- **Diagnóstico del round-robin nativo (2026-08-05)** — `06_docs/diagnostico-round-robin-calcom-2026-08-05.md`. Se verificó con datos la premisa de junio: **confirmada, el RR nativo no reparte** (desde el 1°/5: 126 reservas reales, 0 a Fabián; las únicas 8 que tuvo fueron pruebas de setup del 29-30/4, todas canceladas). Los 9 event types del team están bien configurados —`roundRobin`, hosts correctos, `priority: medium` en ambos— y Fabián sí tiene disponibilidad (aporta ~6% de slots). **Causa raíz abierta:** verificar si Fabián tiene destination calendar en cal.com; si no lo tiene, conectarlo podría arreglar el RR nativo y volver innecesario el workflow de n8n. **Bug corregido de paso:** el seed de `clz_event_type_routing` tenía los slugs de los event types personales (`reparacion-calefon`) y no los del team (`reparacion-de-calefon`) — sin corregir, las reparaciones de calefón habrían ido a Fabián la mitad de las veces siendo exclusivas de Matías.
- **Round-Robin manual cal.com → Google Calendar** (workflow `collazo-round-robin-v1`, en repo al 2026-06-10, pendiente deploy — **leer antes el diagnóstico de arriba**): el round-robin nativo de cal.com no funciona; este workflow lo reemplaza. Trigger: webhook genérico de cal.com (`BOOKING_CREATED/CANCELLED/RESCHEDULED`). Estado en 3 tablas Postgres (`clz_round_robin_state` singleton + `clz_event_type_routing` por servicio + `clz_event_assignment` mapping). Cuando le toca a Fabián: borra el evento del calendar de Matías y crea uno idéntico en el de Fabián con `sendUpdates=none` (movimiento silencioso, el lead no se entera). Schema: `05_crm/clz-round-robin-schema.sql`. Diseño: `06_docs/round-robin-design.md`. Setup webhook: `06_docs/calcom-webhook-setup.md`. Testing: `07_testing/testing-guide-round-robin-v1.md` con 11 casos C1-C11.

## Archivos del proyecto
- `03_workflows/agente-collazo-main.json` — Workflow principal (⚠️ desactualizado desde la migración a ManyChat del 2026-06-30 — pendiente re-exportar desde n8n, ver `06_docs/migracion-whatsapp-manychat-2026-06-30.md`)
- `03_workflows/clz-notificacion-cambio-numero-v2-utility.json` — **v2 con plantilla Utility · ✅ BROADCAST EJECUTADO Y CERRADO (2026-08-04)**: mismo envío que el v1 pero con plantilla categorizada **Utility** en vez de Marketing. Motivo: el rate card de ManyChat para "Rest of Latin America" (donde cae Uruguay) cobra **$0.0851/msg Marketing vs $0.0130 Utility** → sobre 426 envíos, **$36.25 vs $5.54** (~USD 31 de diferencia). Confirmado empíricamente por la agencia (cargó $10, mandó 1 plantilla Marketing, monedero quedó en $9.91). Meta recategoriza automáticamente a Marketing desde el 2026-04-09 cualquier plantilla que no actualice sobre una **acción previa específica del cliente**; por eso la plantilla nueva (`actualizacion_contacto_servicio`) es una notificación post-venta atada al servicio concreto de cada contacto, con 3 variables: `{{1}}` nombre (system field First Name), `{{2}}` servicio y `{{3}}` fecha (custom fields `clz_servicio` + `clz_fecha_servicio`, **ambos tipo Text** — un tipo Date rompe con 400, mismo patrón del bug `ai_msg_count` del 30/06). El loop pasa a 3 llamadas API por contacto (`createSubscriber` → `setCustomFields` → `sendFlow`) con guardas en cada paso: si `setCustomFields` falla NO se dispara el `sendFlow` (evita que llegue un mensaje con variables vacías). Mantiene el split 213/213 en 2 días. **✅ EJECUTADO Y CERRADO (2026-08-04).** Día 1: 206 enviados / 7 fallidos. Día 2: 203 enviados / 10 fallidos. **Total 409/426 entregados (96%)**, costo real **$5,32** contra los ~$34,81 que hubieran salido en Marketing (ahorro $29,49). Los 17 fallidos: 15 eran subscribers preexistentes sin `clz_wa_id` (el hueco conocido — 14 de ellos con servicios de jun-jul 2026, o sea gente que ya había escrito al número nuevo) y 2 con teléfono incompleto en el registro de cal.com (`Javier +5989680308`, `Laura +5989856022`, ambos marcados `revisar` desde la generación de la lista). Contactos ManyChat: 66 → ~475 de 2500. **Dato empírico que quedó de esto:** la intersección real entre los 426 de cal.com y los subscribers preexistentes de ManyChat era de ~15 contactos, todos clientes recientes.

<details>
<summary>Detalle de la validación previa (2026-08-01)</summary>

**VALIDADO E2E — listo para correr.** Aprobada como Utility, costo confirmado en $0.01/msg. Los dos caminos del flujo probados con mensajes reales: contacto nuevo (`createSubscriber` OK) y contacto ya existente (`findByCustomField` lo resuelve) — ambos entregaron el mensaje con las 3 variables renderizadas. El fallback usa `findByCustomField` sobre el custom field `clz_wa_id` (id `14840611`) y **no** `findBySystemField`, que no encuentra contactos de WhatsApp (limitación documentada de ManyChat, ver CLAUDE.md). Único hueco conocido: los ~66 subscribers preexistentes no tienen `clz_wa_id` y quedarán en `detalle_fallidos` — son gente que ya escribió al número nuevo. **Para correr:** reconectar `Contactos cal.com (426, con variables)` → `Split In Batches (1)` (hoy está el nodo de smoke en su lugar), poner `dia_envio = 1`, ejecutar, y repetir con `dia_envio = 2` a las 24hs. Setup en el sticky "🔧 Setup ManyChat" dentro del workflow.

</details>
- `03_workflows/clz-notificacion-cambio-numero-v1.json` — **Workflow manual, en repo, listo para importar (2026-07-31). Es el fallback si Meta recategoriza la plantilla Utility del v2 a Marketing** (usa `cambio_numero`, ya aprobada): notificación masiva a los 426 contactos de cal.com (`06_docs/contactos-collazo-cambio-numero.md`) del nuevo número 092 665 505, vía secuencia ManyChat `content20260731170830_999980` (plantilla ya aprobada por Meta). **Split en 2 días** (nodo `Config Envío (día 1 o 2)` con campo `dia_envio`): sin verificar la cuenta de WhatsApp Business el límite es 250 conversaciones iniciadas por la empresa/24hs, así que `dia_envio=1` manda los primeros 213 y `dia_envio=2` los restantes 213 — correr el workflow 2 veces, una por día. Loop `createSubscriber` → `sendFlow` con 1.5s de rate limit, normaliza automáticamente 189/426 teléfonos que traían un "0" de más pegado al código de país (`+598091046641` → `+59891046641`), y termina con un nodo "Resumen Final" (total/enviados/fallidos + detalle). 2 contactos quedan marcados `revisar` por teléfono con dígitos faltantes. Pendiente: bindear la credencial `CLZ API Header Auth` en los 2 nodos HTTP y correr un smoke test con 1 contacto (falta confirmar código de país del número de prueba).
- `06_docs/migracion-whatsapp-manychat-2026-06-30.md` — Incidente número bloqueado en Chatrace + migración a ManyChat + bugs resueltos (auth, validación de campos, links markdown, corte de mensajes)
- `03_workflows/seguimiento-collazo.json` — Sub-workflow seguimiento 8 hs (inactivo)
- `03_workflows/collazo-round-robin-v1.json` — **Round-Robin cal.com → Google Calendar** (35 nodos, en repo, pendiente deploy)
- `04_agents/agente-collazo-system-prompt.md` — System prompt v1.5
- `05_crm/clz-round-robin-schema.sql` — DDL 3 tablas + seeds + queries operativas
- `06_docs/round-robin-design.md` — Diseño + setup paso a paso del round-robin (con banner que remite al diagnóstico del 05/08)
- `06_docs/diagnostico-round-robin-calcom-2026-08-05.md` — **Verificación con datos de si el RR nativo reparte.** 249 bookings analizados por API + config de los 9 event types + medición de slots. Incluye apéndice con los gotchas de la API de cal.com (Cloudflare bloquea el UA de Python con `403 error code: 1010`; `skip`/`page`/`cursor` no funcionan, hay que paginar por fecha; versión de `cal-api-version` distinta por endpoint)
- `06_docs/calcom-webhook-setup.md` — Guía de 1 página para registrar webhook en cal.com
- `06_docs/troubleshooting-webhook-chatrace.md` — Troubleshooting del webhook del agente principal
- `07_testing/testing-guide-v1.md` — Testing agente conversacional v1
- `07_testing/testing-guide-v2.md` — Testing agente v1.4 (variaciones de servicio)
- `07_testing/testing-guide-round-robin-v1.md` — Testing del round-robin (C1-C11)
- `07_testing/fixtures/created.json` · `rescheduled.json` · `cancelled.json` — Payloads cal.com de ejemplo
