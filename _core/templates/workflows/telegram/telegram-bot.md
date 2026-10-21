# Telegram Bot — la agencia

> Bot de Telegram centralizado para notificaciones, comandos y automatizaciones de la agencia.
> El token vive en `.env` como `TELEGRAM_BOT_TOKEN` (nunca commitearlo).

---

## Configuración

| Variable | Descripción |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Token del bot (en `.env`) |
| `TELEGRAM_CHAT_ID` | ID del chat/grupo receptor (en `.env`) |

**Obtener el `TELEGRAM_CHAT_ID`:**
1. Enviar cualquier mensaje al bot
2. Consultar: `https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates`
3. Copiar el valor de `message.chat.id` y guardarlo en `.env`

**API base:** `https://api.telegram.org/bot{TOKEN}/`

---

## Funcionalidades Activas

### Captura de ideas de video (`salidas/telegram-bot/`)
Bot Python con polling. El usuario manda cualquier mensaje de texto → Gemini lo parsea en `nombre`, `idea` y `script` → se crea una página en la base "Reels IG" de Notion → responde "Idea guardada ✅".

**Para correr:**
```bash
cd salidas/telegram-bot
pip install -r requirements.txt
python bot.py
```

**Variables de entorno usadas:**
- `TELEGRAM_BOT_TOKEN` — token del bot
- `NOTION_TOKEN` — token de integración de Notion
- `GEMINI_API_KEY` — para parsear el mensaje
- `NOTION_IDEAS_DB_ID` — ID de la base Reels IG (`2ca27c52c2868015864cecfae6967a5a`)

**Base de Notion:** `Reels IG` (dentro de la página Instagram)
- `Nombre` (title): título corto del video
- `Idea` (text): descripción expandida
- `Script` (text): guión si lo hay, vacío si no
- `Finalizado` (checkbox): siempre `false` al crear

---

## Casos de Uso Planificados

### Notificaciones automáticas desde n8n
- Alerta cuando un lead nuevo pasa el filtro MQL en Prospección IG
- Notificación cuando se completa una auditoría de llamada (score + resumen)
- Alerta de renovación del `INSTAGRAM_ACCESS_TOKEN` (cada 60 días)
- Resumen diario/semanal de KPIs (leads prospectados, llamadas auditadas, etc.)

### Comandos operativos
- Trigger manual de workflows de n8n desde Telegram
- Consulta rápida de métricas (ej. "¿cuántos leads hoy?")
- Comandos de control del panel la agencia Tools

### Integración con el stack existente
- **n8n**: nodo Telegram disponible nativamente — webhook entrante + envío de mensajes
- **la agencia Tools**: API route para enviar notificaciones push al bot
- **Auditoría de llamadas**: enviar scorecard al finalizar cada auditoría
- **Outreach IG**: notificar cuando un prospecto responde y el agente actúa

---

## Envío de Mensajes — Referencia Rápida

### Desde n8n
Nodo **Telegram** → credencial con el token → acción `Send Message`.

### Desde Python (Modal / scripts)
```python
import httpx
import os

def send_telegram(text: str):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    httpx.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    )
```

### Desde Next.js (la agencia Tools)
```typescript
async function sendTelegram(text: string) {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;
  await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chat_id: chatId, text, parse_mode: "Markdown" }),
  });
}
```

### Desde bash / curl
```bash
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d chat_id="${TELEGRAM_CHAT_ID}" \
  -d text="Mensaje de prueba" \
  -d parse_mode="Markdown"
```

---

## Comandos del Bot (a implementar)

| Comando | Descripción |
|---------|-------------|
| `/start` | Presentación e instrucciones |
| `/status` | Estado del sistema (servicios activos) |
| `/leads` | Resumen de leads del día |
| `/ping` | Health check rápido |

---

## Notas de Seguridad

- El token **nunca** va en código commiteado ni en archivos tracked por git
- Siempre leerlo desde variables de entorno
- Si el token se compromete: regenerarlo en @BotFather con `/revoke`
- Validar el `chat_id` para no procesar mensajes de chats no autorizados en webhooks

---

## Historial

| Fecha | Evento |
|-------|--------|
| 2026-03-13 | Token creado e integrado al workspace |
