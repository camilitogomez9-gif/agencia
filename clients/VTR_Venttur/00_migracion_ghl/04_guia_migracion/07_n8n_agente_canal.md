# 07 · n8n — main, agente "Mauricio" y canal

> ### 🔄 Estado a 2026-09-07 — 🟡 PARCIAL (piezas en staging; falta el canal real)
> **✅ Construido en staging `3sLd7KY3o8I7NvXi` (INACTIVO, entrada por Telegram para testear sin WABA):** context builder que lee el Contact de GHL e inyecta `[ESTADO DEL LEAD]` (fix gap #1) · **sessionKey MX 52→521** (fix doble sesión) · tool **`crear_contacto`** (upsert Contact GHL, validado) · tool **`elevar`** (assign + DND → **Mauricio**, validado). Agente Mauricio (gpt-4o + memoria Postgres) reusado del vivo.
> **🔴 [LA AGENCIA-n8n] pendiente (gated en sandbox B1/B2 + nº de test):** **main real del canal** — entrada por **Contact Reply trigger** + salida **free-form multi-burbuja** por Conversations API + switch por canal. Se itera contra ejecuciones reales, no se construye a ciegas.
> **🔴 [LA AGENCIA-n8n] audio** (camino nuevo, gated B4) · **🔴 handoff-notify** (fix "Notify:0") = **Workflow GHL-UI** (no creable por API; no hay cred de email en n8n VTR).
> **🟡 Decisión pendiente:** fuente del system prompt del cutover (vivo ~39K con `contestan_2do` fantasma vs `v2.0` limpio). **Re-exportar el main vivo antes de tocar.**

> **🔴 Riesgo #3.** El núcleo conversacional: reconstruye el `wf-venttur-main` para entrar por **Contact Reply de GHL** en vez de ManyChat, mantiene al agente **en n8n** (decisión N.2), y corrige el **gap #1** (el agente no recibe estado del lead) + la mayor densidad de bugs de origen (`Repetido?`, `Hay audios?`, sessionKey MX).
>
> **Para quién:** la agencia. **Prerequisito:** módulo `02` (Contact fields) + `04` (calendarios, para la matriz de links) + **sandbox B1-B5**. **Referencia:** `06_canal_whatsapp_y_agente.md`.
>
> **Estimado:** 8-10 hs. Corroborado contra `wf-venttur-main.json` (37 nodos, extracción real de nombres).

> ⚠️ **El export del repo puede ir detrás del vivo.** `wf-venttur-main.json` es del 13/5; el main vivo (verificado 17/8) ya tiene `Estampar estado (Contestó)` cableado (`08` wf11). **Recablear contra el estado vivo**, no solo contra este JSON. Re-exportar el main antes de tocar.

---

## 7.1 El loop — hoy vs destino

```
HOY:      lead → ManyChat (Recibir mensajes, debounce 20s → External Request) → n8n Webhook
          → Agente IA WPP (sin estado) → Formatear mensaje WPP → Separamos en partes → Enviar WPP (ManyChat)
DESTINO:  lead → GHL Conversations → Contact Reply trigger → n8n webhook
          → debounce (n8n) → context builder (+ ESTADO 🔧) → Agente IA WPP → split → GHL Conversations API (free-form)
```

Cambios (todos 1:1 salvo 🔧):
- **Entrada:** `Webhook` (ManyChat External Request) → **Contact Reply trigger de GHL → HTTP al webhook n8n** (sandbox **B1**). Menos hops.
- **Debounce 20s:** de ManyChat → **n8n** (Wait / colapso "gana el último" por sessionKey).
- 🔧 **Context builder + estado del lead** (gap #1): antes del agente, leer el Contact de GHL e inyectar `estado_conversacion`, `link_enviado`, `programa`, `toques`, `cita`, nombre al `[CONTEXTO TURNO]`.
- **Salida:** `Enviar WPP` (ManyChat) → **n8n envía N mensajes por GHL Conversations API, free-form de sesión** (sandbox **B2**).

---

## 7.2 Recableado del main nodo por nodo

Nodos reales del `[Venttur]` (37) y qué pasa con cada uno:

| Nodo actual | Tipo | Destino |
|---|---|---|
| `Webhook` | webhook | ⚠️ **entrada nueva:** Contact Reply de GHL → HTTP; el body trae contactId + mensaje + canal (B1) |
| `Responder rápido ManyChat` | respondToWebhook | mantener el 200-OK temprano (anti-timeout); adaptar a la respuesta del trigger GHL |
| `Settear variables` | httpRequest (ManyChat setCustomFields) | 🔧 **→ escribir estado a n8n/Contact GHL** (no a ManyChat custom fields) |
| `Repetido?` | if | 🔧 **rama TRUE es muerta + comparador desalineado (latin1 vs UTF-8)** → **descartar** (`00 §6`); el dedup se rehace limpio |
| `Hay audios?` | if | 🔧 **condición imposible** (`and`+`audio[0] equals "webp"` sobre URL S3) → **reconstruir** (§7.4) |
| `Get_Audio/s` / `Transcribir audio/s` | httpRequest | 🔧 bajar media de GHL (B4) → whisper-1 |
| `Aggregate` / `Juntar mensajes` / `Obtener solo texto` | aggregate/set | **context builder** (+ estado, gap #1) |
| `Agente IA WPP` | agent | **se queda** (gpt-4o); User Message enriquecido con estado (§7.3) |
| `OpenAI Chat Model` | lmChatOpenAi | **igual** (gpt-4o temp 0) |
| `Postgres Chat Memory` | memoryPostgresChat | **igual** — Supabase, `contextWindowLength 35`; sessionKey con **fix MX** (§7.3) |
| `crear_contacto` | toolWorkflow | **→ upsert Contact GHL** (una sola alta, `02 §7`); ver `09`-sub |
| `elevar` | toolHttpRequest | **→ Assign+notify GHL** (§7.5) |
| `Formatear mensaje WPP` | openAi (gpt-4o-mini splitter) | **se queda** (produce N partes) |
| `Separamos en partes` / `Split Out` | code/splitOut | **se queda** |
| `Enviar WPP` | httpRequest (ManyChat) | 🔧 **→ GHL Conversations API, N mensajes free-form** con delay (B2) |
| `Crear primer contacto` | airtable | 🔧 **colapsa** con `crear_contacto` → **una sola alta en GHL** (`02 §7`); el agente solo enriquece |
| `primer_registro` | toolWorkflow | **DISABLED hoy → no migra** (`00 §6`) |
| `Buscar registro`/`Buscar si ya existe`/`Actualizar ultimo mensaje`/`Crear registro` | airtable | 🔧 **→ read/upsert Contact GHL** (por teléfono canónico, A1/A5) |
| `Envió link?` / `Actualizar link` | if/executeWorkflow | **→ sub `wf-actualizar-link`** (marca `link_enviado`, `08`/`09`) |
| `Tomar todos los mensajes`/`Tomar fuente correcta` | airtable | **Mensajes anuncios → atribución** (se queda en CAPI, `09`) |
| `Meta CAPI` | executeWorkflow | **SE QUEDA** (`09`) |
| `Execute Workflow` (genérico) | executeWorkflow | probable `estado-lead`/`crear-contacto` sub — **verificar contra el vivo** |

---

## 7.3 El agente "Mauricio" — se queda en n8n

| Aspecto | Hoy | Destino |
|---|---|---|
| Modelo | gpt-4o, temp 0 | **igual** |
| System prompt | ⚠️ inline vivo **~39K chars, todavía con `contestan_2do`** ≠ archivo `v2.0.md` (~47K, sin el fantasma) | **definir la fuente del cutover** (¿lo vivo a limpiar, o el v2.0 ya limpio?); en ambos **se elimina `contestan_2do`** (`00 §6`) |
| Memoria | Postgres Chat Memory (Supabase) | **igual** — no migra a GHL |
| sessionKey | `whatsapp_phone.replace('+','')` — **NO normaliza 52→521** → doble sesión | 🔧 **fix: normalizar 52→521** (junto con la canonicalización de `06` para no partir sesiones) |
| User Message | `Mensaje del usuario: {texto}` + fecha — **sin estado** | 🔧 **gap #1:** el context builder inyecta `estado_conversacion`/`link_enviado`/`programa`/`toques`/`cita`/nombre |
| Tools | `crear_contacto`, `elevar` | `crear_contacto`→upsert GHL; `elevar`→Assign+notify (§7.5) |
| `contestan_2do` | instruida en el prompt, **sin nodo** (fantasma) | **se elimina del prompt** |

El diagnóstico de 7 pasos, EMA, Voss/Hormozi, las 10 reglas y la matriz de links (`04 §5`) **se replican tal cual** — solo se le da estado (gap #1), se limpia el fantasma y se repunta la matriz de links a los 8 calendarios GHL. El precio con rango por programa es un cambio de prompt que ya venía aparte.

---

## 7.4 Audio (camino nuevo — B4)

🔧 La rama `Hay audios?` **nunca corrió** (condición imposible) → una nota de voz llega al agente como **string vacío**. Destino: inbound WA audio → GHL guarda el media → n8n baja la URL (B4) → whisper-1 → texto al agente. **Se construye y TESTEA como camino nuevo** (casos de audio en `11`), no se asume "funciona tras migrar" (`00 §6`). Si B4 falla → degradar a "reenvía por texto" (mejor que el string vacío de hoy).

---

## 7.5 Handoff (`elevar`) → Assign + notify

Hoy: `elevar` → `sendFlow` al flow ManyChat "Elevar" (`content20250716130059_365663`) → pausa el bot + asigna + **Notify Assignees: 0** → 🐛 el equipo no se entera. Disparo: pide humano/emergencia, o repite el MISMO mensaje 2+ veces consecutivas.

Destino (1:1 + 🔧):
- **Assign to User** (el asesor del programa, o Mauricio/Max) en GHL Conversations.
- **Pausar la automation** del bot para ese Contact (sandbox **B5** — DND / remove-from-workflow / tag que el despachador respeta).
- 🔧 **Notificar a Mauricio Y Max** por email + notificación de app + inbox GHL (P8) — corrige el "Notify: 0".
- El disparo (pedido humano / repetición consecutiva) + la excepción anti-elevación (misma frase NO consecutiva) se mantienen en la lógica del agente.

---

## 7.6 IG/FB + debounce

- **IG/FB:** GHL Conversations **unifica los 3** → el mismo Contact Reply rutea IG/FB al mismo webhook. Sin canal nuevo (B1 confirma si es 1 trigger o 3).
- **Debounce 20s:** de ManyChat → **n8n** (Wait / colapso por sessionKey).

---

## 7.7 Banderas y checkpoints

| Bandera | Estado |
|---|---|
| Contact Reply trigger WA/IG/FB | **sandbox B1** — bloqueante del canal |
| Free-form <24h por API | **sandbox B2** |
| URL de media del audio | **sandbox B4** |
| Pausar bot por-contacto | **sandbox B5** |
| Fuente del system prompt (vivo ~49.5K post-16/9 vs v2.0 ~47K vs vivo pre-Nahe ~39K) | **definir cuál manda para el cutover** — obligatorio incluir REGLA ABSOLUTA #8 "No agendo yo" (contrato Nahe, `03_arquitectura_ghl/06 §9`) |
| sessionKey MX 52→521 | 🔧 aplicar con la canonicalización de `06` |
| Export del main desactualizado | **re-exportar el main vivo antes de tocar** |
| ⚠️ **`User-Agent` en los HTTP a GHL** | la API de GHL da **Cloudflare 1010** al UA por defecto → todo nodo HTTP Request a GHL (send free-form, upsert Contact, read estado) debe mandar un UA normal (verificado en el sandbox 2026-09-03) |
| Guardrail `Detectar promesa fantasma` + INSERT `vtr_phantom_interceptions` | 🔧 heredar tal cual del post-16/9 — vive entre Formatear y Normalizar burbujas |
| Workflow separado `VTR · digest diario guardrail` (cron 08:00 CDMX) | 🔧 heredar tal cual — trigger n8n, sin dependencia GHL |
| Secretos (Bearer ManyChat, OpenAI key whisper) | rotar |

✅ **Checkpoints de cierre:**
- [ ] Entrada por Contact Reply de GHL → n8n (WA/IG/FB) verificada.
- [ ] Context builder inyecta estado del lead (gap #1) — el agente "sabe" si mandó link/agendó/programa.
- [ ] Reply free-form multi-burbuja por GHL Conversations API.
- [ ] `Repetido?` y `Hay audios?` reconstruidos (dedup limpio + audio nuevo).
- [ ] sessionKey normaliza 52→521.
- [ ] `crear_contacto`/`elevar` apuntan a GHL (una alta / Assign+notify).
- [ ] `contestan_2do` eliminada del prompt; matriz de links → 8 calendarios GHL.
- [ ] **Prompt del cutover incluye REGLA ABSOLUTA #8 "No agendo yo"** (contrato Nahe · `06 §9`).
- [ ] **Guardrail `Detectar promesa fantasma` desplegado** en el main y cableado entre Formatear→Normalizar burbujas.
- [ ] **Digest diario 08:00 CDMX importado** y activo · lee de `vtr_phantom_interceptions`.

---

*Corroborado contra `wf-venttur-main.json` (37 nodos: `Webhook`, `Agente IA WPP`, `Repetido?`, `Hay audios?`, `Enviar WPP`, `crear_contacto`, `elevar`, `Crear primer contacto`, `Meta CAPI`…). El export puede ir detrás del vivo — re-exportar antes de tocar. 2026-09-03.*
