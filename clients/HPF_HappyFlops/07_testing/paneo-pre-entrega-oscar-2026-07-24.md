# Paneo pre-entrega a Oscar — Agente HPF "Rebeca" (demo por **Telegram**)

> ⚠️ **Actualización 2026-07-24 21:30 — este doc quedó desfasado en dos puntos.** El build que corre hoy
> no es el `v13` sino `HPF Inbound Handler` (id `IPO1c36NLzkXrBh9`, active) = **v14 con las 3 tools de CRM
> restauradas a la versión del v12**, snapshot en `03_workflows/hpf-inbound-handler-live-2026-07-24.json`.
> Con esa combinación, el fix "Tools de CRM → no-op" de la tabla de abajo **ya no aplica**: las tools
> volvieron a pegar a GHL con el `opportunity_id` falso, así que volvió el 404. Y el "v15" cuyos altos
> figuran como cerrados **no existe en disco**. Estado real, causas raíz y decisiones abiertas:
> `06_docs/guia-v16-telegram-crm-real-2026-07-24.md` §0 y la sección "Pendientes HPF" de `CLAUDE.md`.

**Fecha:** 2026-07-24 · **Base auditada:** `HPF Inbound Handler (v12).json` · **Build de demo:** `v13 - demo telegram`
**Método:** 4 auditorías adversariales en paralelo + síntesis (36 hallazgos: 9 blockers, 15 altos, 8 medios, 4 bajos), **re-triageadas contra el path de Telegram**.

---

## Veredicto

**Entregable, con 3 gaps visibles a decidir.**

El paneo se corrió inicialmente asumiendo entrega por GHL/WhatsApp y dio 9 blockers. Al re-triagearlo contra **Telegram**, la mitad **no aplica**: son nodos que solo corren en la rama de producción (`Es Origen Telegram? (Post)` → FALSE). Lo que sí aplicaba ya está corregido en el v13.

| # | Blocker (contexto GHL) | ¿Aplica al demo por Telegram? |
|---|---|---|
| 1 | Credencial del webhook sin bindear | ❌ No — Telegram Trigger usa su propia credencial, que **sí** viaja en el JSON |
| 2 | `opportunity_id` vacío → 404 | ⚠️ Sí, pero **corregido**: era el 404 reportado |
| 3 | Debounce en 0s | ⚠️ Sí → **corregido** (15s) |
| 4 | Contexto `[7]` ciego | ❌ En Telegram lo cubre la **memoria Postgres** (verificado en Fase 1: no re-pregunta) |
| 5 | Imagen principal + promo en loop | ❌ No — esos nodos solo corren en la rama GHL |
| 6 | 3 nodos con `type: "SMS"` | ❌ No — son nodos GHL |
| 7 | `MOSTRAR_PRODUCTOS` no envía nada | ⚠️ **Sí — es el gap más visible** (ver decisiones) |
| 8 | Path de pago roto | ⚠️ Sí → **corregido** (era el que más dolía) |
| 9 | Sin datos de pago | ⚠️ **Sí** — necesita info de Oscar |

---

## Corregido en el v13 (lo que rompía el demo)

| Fix | Qué pasaba | Estado |
|-----|-----------|--------|
| **GHL no puede matar la ejecución** — `onError: continueRegularOutput` en los 11 nodos que pegan a leadconnectorhq | En Telegram el `opportunity_id` es `tg_opp_<chatid>` (falso) → **404 → `stopWorkflow`**. Oscar mandaba un comprobante y el bot **no respondía nada**; cualquier foto moría en `Set imagen_input` | ✅ 0 nodos GHL pueden tirar la ejecución |
| **Tools de CRM → no-op** (`IDENTIFICAR_EVENTO`, `MOSTRAR_PRODUCTOS`, `COTIZADOR`) | Devolvían el texto del 404 al LLM, que podía mencionarlo al lead | ✅ devuelven `ok, registrado` |
| **Debounce 0s → 15s** | Con 0s contestaba cada globito por separado, encimado | ✅ agrupa la ráfaga sin que la espera se note |
| **maxTokens 800 → 1500** | El turno de cotización (cotización + 7 pasos + upsell) se podía **truncar a la mitad** | ✅ |
| **Stickers / GIFs / documentos / video / ubicación** | `Auth + Normalize` tiraba error → **silencio total**. Oscar manda un sticker y el bot muere | ✅ el agente responde con naturalidad |

> El 404 reportado (`MOSTRAR_PRODUCTOS`) queda resuelto por partida doble: la tool ya no pega a GHL, y ningún nodo GHL puede matar la ejecución.

---

## Los 3 gaps que quedan (requieren decisión)

### 1. El bot no manda fotos de producto — y el prompt promete que sí
El prompt dice en `[4]`: *"llamá MOSTRAR_PRODUCTOS con la lista. **El sistema envía las fichas**"*. No hay ningún nodo que envíe assets. Oscar pide *"mandame el catálogo de sandalias"* (los casos 8 y 9 del buzón de Rebeca, los que más le duelen) y **no llega ninguna imagen** — cuando el bot de Kommo que estamos reemplazando **sí las mandaba**.

Estado del catálogo (bloqueante real): la mayoría de los *Producto Principal* **no tiene URL estable** — son links de Airtable que expiran, o directamente no existen (los videos viven dentro de los salesbots de Kommo). Solo ~6 assets por evento tienen `i.ibb.co` estable, y casi todos son Accesorios.

**Opciones:**
- **(a) Honestidad — 10 min.** Ajustar el prompt para que **no prometa** enviar fichas y describa los productos en texto. Elimina la promesa incumplida.
- **(b) Imagen principal del evento — ~45 min.** Las 3 imágenes de lineup (Boda/XV/Otros) **sí tienen URL estable**. Es el paso 2 del flujo original ("TENEMOS ESTOS PRODUCTOS PARA TU EVENTO"). Se implementa con el patrón de marcadores que ya usamos en IMP (`[IMAGEN:XV]` en el output → el sanitizer lo detecta → nodo Telegram `sendPhoto`). Alto impacto visual.
- **(c) Fichas completas** — bloqueado hasta re-hostear los assets (necesita acceso a Kommo / Oscar).

**Recomendación:** (a) + (b). Con eso Oscar ve una imagen real al decir su evento, y el bot no promete nada que no cumpla.

### 2. Sin datos de pago
Cero ocurrencias de "cuenta"/"clabe"/"banco" en los 62 nodos. Oscar llega a *"quiero pagar el anticipo, pasame los datos"* y el bot no puede responder. **Necesito de vos:** los datos bancarios reales (o confirmar que el bot debe decir "te los paso por aquí" y sigue un humano).

### 3. Sin fecha actual en el contexto
El sistema Kommo original inyectaba la fecha; el v13 no. Si Oscar dice *"mi evento es el 15 de agosto"*, el bot no puede calcular si entra en los 15 días de producción. Fix de 10 min (nodo `Fechas`, patrón ya usado en NPR/TFO).

---

## Altos — ✅ cerrados en el v15

| Fix | Antes | Ahora |
|-----|-------|-------|
| **Cotización 100% determinística** | El LLM calculaba subtotales, total y el 50%; solo el envío era determinístico | `CALCULAR_ENVIO` devuelve la cotización completa (líneas, envío, total, anticipo) para copiar tal cual |
| **Mínimos mezclados** | 100 sandalias + 20 kits → rechazaba **todo** | Cotiza lo válido y avisa qué producto falta y cuál es su mínimo |
| **Imagen con caption** | `Parse Vision` pisaba el texto del lead | Conserva el caption + la nota de visión |
| **Fecha actual** | No existía → no podía evaluar los 15 días de producción | Inyectada en el prompt (TZ México) |
| **FAQ del catálogo** | Faltaban tallas, paqueterías, "¿es estafa?", kit anticruda, retiro en taller | Sección `[3b]` con las respuestas canónicas |
| **Errores transitorios** | Un 429 de OpenAI mataba el turno en silencio | `retryOnFail` (3 intentos) en LLM, Vision, Whisper y descargas |
| **Tipos no contemplados** | 4ª salida del Switch sin conectar | Cae a `Text Passthrough` |

Pendiente menor: **`ATENCION_PERSONALIZADA` no notifica a nadie** (aplica el tag y nada más). En el demo Oscar *es* el equipo, así que impacta poco.

---

## Lo que SÍ está sólido (para mostrarle a Oscar)

- **Motor de envío determinístico** con pesos, límites de empaque y brackets portados de la calculadora original. Verificado con números exactos.
- **Doble capa de mínimos**, nacida del incidente real de los 35 cilindros.
- **Las 12 reglas inviolables se sostienen bajo presión** (verificadas en Fase 1 y Fase 2).
- **Cotización canónica**: header exacto, envío calculado, total, anticipo 50%, separador de miles, 7 pasos idénticos.
- **Los 9 problemas del buzón de Rebeca**, direccionados uno por uno con trazabilidad.
- **Un solo Vendedor con memoria persistente** en lugar de 4 agentes por etapa — el argumento de fondo frente a Oscar.
- **Estética conversacional humanizada**: minúsculas, sin signos de apertura, una idea por burbuja (ver `_core/standards/estetica-conversacional-agentes.md`).

---

## Antes de darle el bot

1. Importar `v13 - demo telegram` (la credencial de Telegram viaja en el JSON; verificar igual).
2. Decidir los 3 gaps de arriba.
3. **Correr una conversación completa por Telegram de punta a punta**: hola → evento → productos → cotización → pago → mandar una foto → mandar un audio → mandar un sticker. Es la primera vez que el path de imagen y audio de Telegram va a correr de verdad.
