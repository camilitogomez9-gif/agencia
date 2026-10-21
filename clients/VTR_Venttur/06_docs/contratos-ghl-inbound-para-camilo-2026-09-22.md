# Contratos GHL inbound → n8n (para Camilo · 2026-09-22)

Dos **GHL Workflows** que hay que armar en la UI de GHL (`app.gohighlevel.com` → Automation → Workflows),
cada uno con una acción **Webhook** que POSTea a n8n. Son la pieza que falta para que el bot y la
confirmación de citas funcionen post-cutover. Sin estos, los workflows n8n nuevos (ya construidos, OFF)
no reciben nada.

Location GHL: `7aXb4JCKsWV5nUyBXeSF`.

---

## 1. Inbound del bot → `main-venttur-ghl`

**Trigger GHL:** *Customer Replied* (o *Inbound Message* / *Conversation - Customer Reply*), filtrado a
canal **WhatsApp** (no email/SMS).

**Acción:** Webhook `POST` a:
```
https://[TU-INSTANCIA-N8N]/webhook/main-venttur-ghl-44ce5e8a
```

**Body (JSON) — contrato exacto que el main espera** (confirmado con la agencia 2026-09-22):
```json
{
  "contact_id": "{{contact.id}}",
  "phone": "{{contact.phone}}",
  "message": { "body": "{{message.body}}" },
  "contact": {
    "firstName": "{{contact.first_name}}",
    "lastAttributionSource": { "url": "{{contact.attributionSource.url}}" }
  }
}
```

**Lo que el main hace con esto** (`Normalize GHL Payload`):
- `contact_id` → todas las llamadas a la API GHL (W9/W11/clasificador, envío de mensajes). **Tiene que ser
  el contactId NATIVO de GHL**, no un id de otro sistema.
- `phone` → se canoniza a `+521<10>` (sessionKey de memoria, consistente con rescate/despachador).
- `message.body` → el texto que procesa el agente.
- `contact.attributionSource.url` → tracking de atribución.

**Notas:**
- El main ya está refactorizado y OFF (`1eS1Z5k898c3ATnf`). Al cutover se prende y este webhook lo alimenta.
- Si `contact.first_name` o la attribution no vienen, el main degrada sin romper (usa defaults).
- El main responde 200 rápido (RespondToWebhook temprano) — no esperes una respuesta con contenido.

---

## 2. Confirmación de cita → `W6`

**Trigger GHL:** *Customer Booked Appointment* (evento nativo cuando un lead agenda en cualquiera de los
8 calendarios por programa).

**Acción:** Webhook `POST` a:
```
https://[TU-INSTANCIA-N8N]/webhook/vtr-confirmacion-agenda-ghl-a191d178
```

**Body (JSON):**
```json
{
  "contact_id": "{{contact.id}}",
  "first_name": "{{contact.first_name}}",
  "programa": "{{contact.programa_interes}}",
  "appointment_start": "{{appointment.start_time}}",
  "meeting_link": "{{appointment.meeting_location}}"
}
```

**Lo que W6 hace:**
1. Envía la confirmación por WhatsApp al lead (fecha CDMX + link de reunión si viene).
2. **Después** marca `agendan_cita=true` + `estado_conversacion="Cita confirmada"` en el contacto GHL.
   (Fix del bug viejo que marcaba antes de enviar y la cadena moría.)

**Notas:**
- W6 está OFF (`AS9ZNhY3GJDfhY3P`). Prender al cutover.
- El asesor NO se rutea acá (viene del calendario/appointment). Diego García está fuera del ruteo (D9).
- Recordatorios pre-cita 24h + 1h = pieza aparte (W6b), no incluida.

---

## Checklist para Camilo

- [x] GHL Workflow 1 (*Customer Replied* WhatsApp) → webhook al main. **✅ creado por Camilo (2026-09-22).**
- [x] GHL Workflow 2 (*Customer Booked Appointment*) → webhook a W6. **✅ creado por Camilo (2026-09-22).**
- [ ] Verificar que `{{contact.id}}` resuelve al contactId nativo GHL (no a un id externo) — validar en el smoke CUTOVER-3.
- [ ] Probar cada uno con un lead de test post-cutover (parte del smoke CUTOVER-3).

> **✅ Ambos GHL Workflows inbound están creados (Camilo, 2026-09-22).** Con esto el lado GHL que alimenta
> al main y a W6 queda listo. Pendiente sólo la verificación E2E en CUTOVER-3 (que el body llegue con las
> keys correctas — `contact_id`/`phone`/`message.body` al main, `contact_id`/`appointment_start` a W6).

> ⚠️ Los merge fields (`{{contact.id}}`, `{{message.body}}`, etc.) pueden variar de nombre según la
> versión de GHL. Usá los que ofrezca el editor de Webhook de tu instancia; lo importante es que el
> JSON resultante tenga las **keys** `contact_id`, `phone`, `message.body` (main) / `contact_id`,
> `appointment_start` (W6).
