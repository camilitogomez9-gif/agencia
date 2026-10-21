# NVJ — Narvaja Hogar

## Datos generales
- ID: NVJ
- Nombre: Narvaja Hogar
- Niche: generic
- Fecha inicio: 2026-04-23
- Status: live

## Stack activo
- [x] n8n
- [x] Airtable
- [ ] Clientify
- [ ] Google Sheets
- [x] WhatsApp
- [ ] Notion
- [x] ManyChat
- [x] OpenAI (GPT-4.1-mini + GPT-4o-mini)
- [x] PostgreSQL (memoria conversacional)

## Contactos clave
| Rol | Nombre | Contacto |
|-----|--------|---------|
| Decisor | (pendiente) | |
| Técnico | | |

## OKRs del proyecto
1. Agente conversacional en producción que atiende consultas de ventas via WhatsApp, Instagram y Facebook
2. Clasificación y transcripción automática de audios e imágenes
3. Escalamiento fluido al equipo humano con resumen de conversación

## Notas críticas
- Tienda uruguaya de artículos para el hogar: colchones, sommiers, roperos, sofás, electrodomésticos
- Dirección local: Río Negro 1617, Montevideo
- Mecanismo anti-loop: Airtable guarda el último mensaje recibido; si se repite, el flujo se detiene (nodo "Repetido?")
- Memoria conversacional en PostgreSQL (tabla `n8n_chat_histories_with_date`, ventana de 40 mensajes)
- Resumen semanal automático: analiza conversaciones de los últimos 7 días y envía métricas por Gmail (v3: conteos deterministas en JS, prompt con pasos secuenciales, temperature=0+seed=42, listas cerradas para categorías/motivos)
- Sub-workflow "Elevar Conversación" recibe `resumen` + `id_manychat` desde el agente principal
- Canales: WhatsApp, Instagram, Facebook (Switch por campo `whatsapp_phone` / `ig_id`)
