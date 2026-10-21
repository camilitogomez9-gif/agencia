# Nodo Telegram para handoff notification (§7.3 de la guía ejecutable)

Rama paralela post-`elevar` en `main-venttur` (n8n). Este nodo se agrega como fallback / redundancia al workflow de trabajo GHL "Notificación interna" del §7.2.

**Credential a usar:** `botla agencia` (id `V5k84z3AjQc9Y5yg`, tipo `telegramApi`) — ya existe en n8n, usada por otros workflows VTR.

**Placeholder crítico:** `<<chat_id_del_grupo_operativo>>` — reemplazar con el chat ID que envíe Mauricio (accionable cliente #5). Si no llega a T-4, usar chat ID del grupo alternativo `botla agencia` que la agencia ya tenga.

## Cómo agregarlo al main-venttur

1. Abrir el workflow `[Venttur]` (main-venttur, id `k3aivKSP67S97IHn`) en n8n UI.
2. Después del nodo que ejecuta la tool `elevar` (buscar el que despacha la elevación al humano), agregar una rama paralela (no bloquear la ejecución principal).
3. Pegar el JSON de abajo como nodo nuevo.
4. Ajustar la posición para que quede visualmente ordenado.
5. Reemplazar `<<chat_id_del_grupo_operativo>>` con el chat ID real cuando llegue.
6. Test con un `elevar` de prueba.

## JSON del nodo (copiar-pegar en n8n con "Import from clipboard")

```json
{
  "id": "handoff-telegram-notif",
  "name": "Telegram · Notif handoff",
  "type": "n8n-nodes-base.telegram",
  "typeVersion": 1.2,
  "position": [1200, 400],
  "parameters": {
    "resource": "message",
    "operation": "sendMessage",
    "chatId": "=<<chat_id_del_grupo_operativo>>",
    "text": "=🚨 *Handoff — lead elevado a humano*\n\n*Lead:* {{ $json.contact.first_name }} {{ $json.contact.last_name }} ({{ $json.contact.phone }})\n*Motivo:* {{ $json.motivo || $json.reason || 'elevar' }}\n*Timestamp:* {{ $now.setZone('America/Mexico_City').toFormat('yyyy-MM-dd HH:mm') }} CDMX\n*Últimos 3 mensajes:*\n{{ ($json.context || $json.recent_messages || 'sin contexto') }}\n\n🔗 [Ver conversación en GHL](https://app.gohighlevel.com/v2/location/{{ $json.location_id || '7aXb4JCKsWV5nUyBXeSF' }}/contacts/detail/{{ $json.contact.id }}/conversation)",
    "additionalFields": {
      "parse_mode": "Markdown",
      "disable_web_page_preview": true
    }
  },
  "credentials": {
    "telegramApi": {
      "id": "V5k84z3AjQc9Y5yg",
      "name": "botla agencia"
    }
  },
  "onError": "continueRegularOutput",
  "notes": "Rama paralela post-elevar (handoff notification §7.3). Fallback si el cliente no entrega mails a tiempo para el workflow de trabajo GHL. Chat ID a completar cuando llegue (§6 accionable #5)."
}
```

## Ajustes según referencias reales del contexto n8n

Cuando el nodo `elevar` (tool call) ejecuta, el context puede tener las variables con nombres distintos:
- `$json.contact.*` — asumido, viene del `AI Agent` node.
- `$json.motivo` / `$json.reason` / `$json.tag` — depende de qué campo la tool `elevar` guarde.

**Verificar antes de activar** que las expresiones resuelven a valores reales — abrir un `elevar` real de la historia y ver el input al nodo. Si no matchea, ajustar las expresiones.

## Smoke test (§7.4)

Tres eventos que deben mandar mensaje:
1. **Elevación explícita:** disparar `elevar` desde n8n → verifica que llega Telegram.
2. **Guardrail promesa fantasma:** forzar match con input trap → verifica que llega Telegram.
3. **Ads sin match:** lead con `utm_source=facebook` sin programa canónico → verifica que llega Telegram.
