# STK — Stark Supplements

## Datos generales
- ID: STK
- Nombre: Stark Supplements
- Niche: generic (suplementos deportivos / e-commerce)
- Fecha inicio: 2026-05-10
- Status: **congelado en pre-producción (2026-08-04)** — pendientes descartados, incluido el cobro de USD 1.500 + mantenimiento. No se reconstruyen los bots de Kommo ni se completa el routing

## Stack activo
- [x] n8n
- [x] Airtable (catálogo de productos)
- [x] Kommo (CRM + chat + pipelines)
- [x] OpenAI (GPT-4o agente principal, GPT-4.1-mini post-procesador + clasificadores, Whisper transcripción)
- [x] PostgreSQL (memoria de chat)
- [x] Redis (batching de mensajes)
- [x] WhatsApp (vía Kommo)
- [x] Telegram (notificaciones internas)

## Contactos clave
| Rol | Nombre | Contacto |
|-----|--------|---------|
| Decisor / Dueño | Cristian | — |
| la agencia (build original) | Juan Pablo Rosso (Juampi) | — |

## OKRs del proyecto
1. Poner el agente conversacional en producción (reemplazar 5 vendedores a comisión)
2. Lograr que el agente maneje el ciclo completo: consulta → recomendación con imagen → cotización → pago → elevación
3. Activar seguimientos automatizados post-conversación (30m, 2h, 8h, 24h)

## Notas críticas
- **Cobro: ❌ descartado el 2026-08-04.** Ya no se persiguen los USD 1.500 del build ni la transferencia de mantenimiento mensual; el proyecto queda congelado en pre-producción. Contexto original: no poner en producción hasta que paguen ambos. Si no, empiezan cambios sin pagar.
- **Bolivianos:** Opera en Bolivia, precios en Bs. Producción de suplementos en EEUU. Marca propia ISOX.
- **Múltiples e-commerce:** Cristian tiene ~5 e-commerce (gafas, productos gym, etc.) que compiten entre sí para cubrir mercado. Solo nos concentramos en Stark Supplements.
- **Problemas con Kommo:** El cliente borra bots repetidamente (~6 veces). Hay que reclamarles cada vez y reconstruir. Necesitan separar los e-commerce en cuentas Kommo distintas (los webhooks se cruzan, como pasaba con Happy Flops).
- **Comunicación:** Son lentos para responder (semanas de silencio). Hay que ser insistente diariamente. "Todos los días hay que estar insistentes."
- **Hackeo reciente:** Les hackearon la cuenta de Kommo recientemente, cambiaron contraseñas.
- **Agente "Kathe":** La identidad del agente es una vendedora llamada Kathe del equipo Stark Supplements.
- **4 sucursales:** Santa Cruz Equipetrol, La Paz Torres Mall, La Paz Calacoto, Cochabamba Zafiro.
- **Manual de ventas:** Cristian pasó un manual de ventas que el agente intenta replicar. Pedir a Juampi que lo comparta.
