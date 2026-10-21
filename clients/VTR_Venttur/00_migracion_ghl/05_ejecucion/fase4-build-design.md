# FASE 4 · Build design — staging main por Telegram (VTR → GHL)

> Reconstrucción del `[Venttur]` vivo (`k3aivKSP67S97IHn`, 39 nodos) como staging **sin tocar producción**, con entrada por **Telegram** para testear sin WABA (patrón HPF). Se construye por incrementos; la parte que toca GHL espera el reset del cap diario (B-12).

## Staging creado
- **`3sLd7KY3o8I7NvXi` · `[Venttur] GHL staging (Telegram test)`** — INACTIVO, 6 nodos.
- Reusa del vivo: **gpt-4o** (`ibkhdCMyhr3yqDQk`) + **system prompt 46.868 chars** + **Postgres memory** (`ihpvM7nYMdLCwWDP`).

## Incrementos

### ✅ Increment 1 — loop testeable SIN GHL (hecho)
`Telegram Trigger → Normalizar payload → Agente IA WPP (gpt-4o + prompt + Postgres) → Enviar Telegram`
- `Normalizar payload` mapea el update de Telegram → `{message, chatId, sessionKey, canal:'telegram', name, email sintético}`.
- sessionKey = chatId de Telegram (memoria por tester).
- **Prueba:** el agente Mauricio responde por Telegram, con memoria persistente. **Sin GHL.**
- **Gotchas HPF ya aplicados:** Telegram Trigger **con `webhookId`** (sin él activa y no recibe nada); identidad por **email sintético** (`tg-<chatid>@venttur.test`).

### ✅ Increment 2 — context builder gap #1 (hecho 2026-09-06)
`Normalizar payload → Buscar Contact GHL → Construir estado lead → Agente IA WPP`.
- **Buscar Contact GHL** (`n8n-nodes-base.httpRequest`): `POST /contacts/search` por teléfono (fallback email), `locationId` literal, cred `httpHeaderAuth` **`GHL VTR (PIT)` (`YkVmaA4jlRbO1TQD`, creada por API)** + headers Version/UA/Content-Type/Accept explícitos, `onError: continueRegularOutput`.
- **Construir estado lead** (Code): arma `[ESTADO DEL LEAD]` desde los `customFields` del contacto (reverse-map por id: `programa_interes`, `origen`/`fuente_lead`, `link_enviado`, `estado_conversacion`, `toques_enviados`, `grado_escolar`/`inicio_deseado`/`nivel_ingles`) — réplica del `text` del main vivo. Si no hay hit → "Lead nuevo".
- **Agente IA WPP**: `text` reescrito al formato `[ESTADO DEL LEAD]` real (reemplaza el text simple del inc.1).
- **Validado**: la lógica READ probada en Python contra GHL real — `search by phone` devuelve el contacto con customFields; SINGLE_OPTIONS vuelven como etiqueta (`Pathway Alemania`, `Internados`, `Form Meta`), CHECKBOX como `['true']`. Generador idempotente: `scripts/gen-staging-inc2.py`.
- **Estado del staging**: **ACTIVO**, bot Telegram `Venttur` (`telegramApi`) ya bindeado en Trigger+Enviar por el usuario (B-13 parcial). **Pendiente E2E**: la agencia manda un mensaje al bot → confirmar que el flujo corre y el agente ve el `[ESTADO DEL LEAD]`. Caveat: un lead de test por Telegram usa email sintético / sin teléfono → cae en la rama "Lead nuevo" (correcto); la rama "lead conocido" está validada en Python contra un contacto real.

### ✅ Increment 3 — sessionKey MX (hecho 2026-09-07)
`gen-staging-inc3.py`. `Normalizar payload` con `canonPhone()` (réplica del ETL: `52`/`521`+10 → `+521<10>`); `sessionKey = canonPhone(phone) || chatId`. Arregla el doble-sesión del vivo. Telegram sin teléfono → sigue por chatId.

### ✅ Increment 4 — tools → GHL (hecho 2026-09-07)
- **4a `crear_contacto`** (`gen-staging-inc4a.py`): toolHttpRequest `POST /contacts/upsert`, nombre/apellido por `$fromAI`. Validado por API (upsert 201 + dedup). `ai_tool` conectado.
- **4b `elevar`** (`gen-staging-inc4b.py`): toolHttpRequest `PUT /contacts/{id}` `{assignedTo: Mauricio, dnd:true}`. Primitivos validados (200 + read-back). `ai_tool` conectado. **Notificación email+app pendiente → Workflow GHL (B-N1).** Assign target default Mauricio (gap: asignar al asesor del programa).

### ⏳ Increment 5 — send GHL + salida por canal (GATED)
En cutover: `Enviar Telegram` → **GHL Conversations API free-form**, multi-burbuja (reusar `Formatear mensaje WPP` + `Normalizar burbujas` del vivo). Depende de asunción (d) free-form send + WABA. **No se construye a ciegas.** En staging el send sigue por Telegram.

### ⏳ Increment 6 — audio (B4), dedup, despachador, Cerrada, CAPI, formulario, confirmación/recordatorios (GATED)
El **despachador** ya está desbloqueado por la asunción (i) (query por CF ✓) pero espera decisiones de cliente (tope-2/prioridad). Audio depende de (g); confirmación/recordatorios de (c)+(j)+calendarios. Ver `REGISTRO-EJECUCION.md` §BLOQUEANTES.

## ✅ Dependencia para testear (B-13): RESUELTA
Bot de Telegram VTR dedicado (`Venttur`, cred `telegramApi`) creado por el usuario y bindeado en Trigger+Enviar; staging **ACTIVO**. E2E del agente confirmado por la agencia (2026-09-06): responde por Telegram con memoria. **Falta ejercitar por Telegram las tools nuevas** (crear_contacto/elevar) y la rama "lead conocido" del context builder (los primitivos ya están validados por API).

## Regla de oro
Todo esto vive en el workflow staging `3sLd7KY3o8I7NvXi`. **Los 14 workflows vivos NO se tocan** hasta el cutover. Generador reproducible: `scripts/gen-staging-main.py` (idempotente por nombre).
