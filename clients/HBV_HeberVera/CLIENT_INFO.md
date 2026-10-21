# HBV — Heber Vera

## Datos generales
- **ID**: HBV
- Nombre: Heber Vera
- Niche: generic (peluquería / estética capilar)
- Fecha inicio: 2026-05-10
- Status: **live** — sin pendientes al 2026-08-04. La propuesta de Marca Personal para Eloísa no se envía (descartada) y el incidente P2 de Chatrace se cerró sin resolución (n8n y WhatsApp nunca se vieron afectados)

## Stack activo
- [x] n8n
- [ ] Airtable
- [ ] Clientify
- [x] Google Sheets
- [x] WhatsApp
- [ ] Notion
- [x] OpenAI (GPT-4o)
- [x] Telegram
- [x] Fresha (reservas online)

## Contactos clave
| Rol | Nombre | Contacto |
|-----|--------|---------|
| Dueña | Eloísa Vera | — |
| Escalamiento humano | — | https://wa.link/fxmq1o |

## Datos del negocio
- **Dirección:** Millán 3811, Montevideo, Uruguay
- **Horarios:** Martes a Sábados, 9:30 a 18:30
- **Teléfono:** 2336 2184
- **Reservas:** https://www.fresha.com/es/a/heber-vera-montevideo-avenida-millan-3811-lvrhi15g/booking?allOffer=true&pId=1420700
- **Antigüedad:** 50 años (peluquería) / 40 años en prótesis oncológicas
- **Organismos:** BPS, Caja Bancaria, Caja de Profesionales, ASSE

## OKRs del proyecto
1. Automatizar atención en WhatsApp: consultas, precios y guía de reservas sin intervención humana
2. Reporte semanal automático con métricas de conversación → Telegram
3. Mantener tasa de conversación → reserva medible semana a semana

## Incidentes abiertos
- **2026-06-22 — Reconnect Messenger Chatrace bot 1444981 (P2):** dashboard Chatrace muestra "You don't manage any chatbot" + mail "Reconnect Messenger" del propio bot. n8n sigue ejecutando (WhatsApp probablemente no afectado). Soporte de primera línea **escaló a agente humano** y advirtió que "Create New Account" crea bot nuevo (riesgo permanente). Detalle: `06_docs/incidente-reconnect-messenger-2026-06-22.md`. Bloqueante: respuesta del agente humano de Chatrace.

## Notas críticas
- El agente NO presiona para reservar — solo envía link si la persona lo pide o acepta explícitamente
- Prótesis oncológicas: flujo especial → activa herramienta 'enviar PDF' + link escalamiento humano
- Diagnóstico sin costo: mencionar con moderación, solo cuando amerita
- Respuestas divididas en 3 partes (más natural para WhatsApp); limpia signos ¡¿
- Si cliente manda imágenes (URLs https): ignorar mención de imagen, responder por contexto de texto
- Acepta Mercado Pago
- Google Sheets historial: `1oi-X2mk71z48pkkENRoT9YoQvAS_PQVEi-ANkTVAzdY` (Heber Historial)
- Credenciales n8n: OpenAI | Heber Vera (`eIbZmB3efILuCCuf`) + OpenAI la agencia® (`Fa3aaCsYTBS79y3Y`)

## Nueva línea de servicio — Marca Personal Eloísa (propuesta 2026-06-13) — ❌ DESCARTADA el 2026-08-04, no se envía
- **Tipo:** Consultoría estratégica (NO automatización; ortogonal al agente WPP existente)
- **Alcance:** 8 semanas — 5 docs estratégicos del curso de marca personal de la agencia adaptados a Eloísa (ICP & Ideal Follower, Análisis Competencia, Tu Personaje, One-Sheeter Offer, Dashboard Notion) + Plan de contenido 60 días + Sistema KPIs/tracking semanal + Manual operativo para Micaela
- **Modelo:** Asincrónico con 5 reuniones (kickoff 90 min + 3 quincenales 60 min + cierre 60 min). Review semanal de lote Micaela (8 reviews).
- **Precio:** USD 1.000 (50/50 — USD 500 firma + USD 500 cierre). Sin mantenimiento mensual.
- **Materiales fuente:** curso premium en Skool (USD ~3k, propiedad de la agencia). 5 docs Notion fundacionales recibidos en sesión 2026-06-13. SOPs/scripts/funnels adicionales del Skool se incorporan durante ejecución de entregables 4.6 (plan contenido), 4.7 (KPIs), 4.8 (manual Mica).
- **Documentación:**
  - `01_discovery/paquete-marca-personal-elo-2026-06-13.md` — paquete interno con 10 entregables + cronograma + riesgos + cálculo de costo
  - `01_discovery/propuesta-marca-personal-elo-2026-06-13.md` — propuesta externa lista para enviar a Eloísa
- ❌ **Descartado (2026-08-04):** no se manda la propuesta a Elo, ni se cobra el 50%, ni se agenda el kickoff. Quedó también sin resolver la incógnita "quién es Heber" para Eloísa (¿padre, esposo, fundador?) durante discovery del kickoff
- **Dependencia clave:** Micaela (CM de Elo) debe estar en kickoff + reunión #3 (handoff) para que el paquete cierre con ejecución autónoma
