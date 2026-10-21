# HPF — Happy Flops

## Datos generales
- ID: HPF
- Nombre: Happy Flops
- Niche: event (Sandalias e insumos para fiestas y eventos)
- Fecha inicio: 2026-04-22
- Status: **live** — pendientes al 2026-08-04: (1) 🔴 **conectar la WABA (M7)**, único bloqueante de producción real; (2) 🟡 **replicar la estética conversacional del agente original** (owner: Camilo). Cerrados: fix de `Send Photo`, deploy del v16 con CRM real contra GHL, assets de catálogo + datos bancarios de Oscar, workflows GHL M4

## Stack activo
- [x] n8n
- [x] Kommo / AmoCRM (bot en producción, el que se está reemplazando)
- [x] GoHighLevel (migración en curso — sub-account `onRwi0ZF4uYi0Lp6GAbE`, pipeline "Happy Flops IA")
- [x] OpenAI (gpt-4.1 vendedor + vision, Whisper para audios)
- [x] Postgres/Supabase (memoria del agente + buffer de debounce)
- [x] Telegram (canal de la demo del agente GHL, mientras no entra la WABA)
- [x] Airtable (catálogo de productos del bot Kommo — base `appMHtUN9zKYODufC`)
- [ ] WhatsApp Cloud API / WABA en GHL (M7, pendiente)
- [ ] Clientify
- [ ] Notion

## Dos líneas de trabajo en paralelo
1. **Bot Kommo (producción actual):** `happyflops-main-v3.json` + sub-workflows de seguimiento + `HPF - Calculadora`. Se mantiene hasta el cutover.
2. **Agente GHL (migración):** workflow `HPF Inbound Handler` (id `IPO1c36NLzkXrBh9`), hoy en demo por Telegram. Estado real, causas raíz y pendientes: `06_docs/guia-v16-telegram-crm-real-2026-07-24.md` §0 + sección "Pendientes HPF" de `CLAUDE.md`.

## Contactos clave
| Rol | Nombre | Contacto |
|-----|--------|---------|
| Dueño | Oscar | |
| Técnico | | |

## OKRs del proyecto
1. Mantener y escalar la solución existente en producción
2. Agregar nuevas integraciones según necesidad del cliente
3. Automatización completa de flujos operacionales

## Notas críticas
- Proyecto en fase de mantenimiento (live)
- Flujo principal importado: `happyflops-main-v1.json`
- Stack y componentes adicionales a definir conforme se agreguen nuevos flujos

## Fixes aplicados
- **2026-05-04** — Fix memoria primera interacción (atención personalizada): se agregó nodo Postgres `SAVE_FIRST_MESSAGE` entre `Exist_Interaction?1` (rama false) y `ATENCION_PERSONALIZADA2` en el flujo principal. Guarda `{"type": "human", "content": <mensaje>}` en `n8n_chat_histories` con el `session_id` del `Memory_ID2`. Sin este fix, los leads con prefijo +1 siempre volvían a atención personalizada porque la memoria quedaba vacía en la primera interacción.
- **2026-07-15** — Fix mínimo de compra no respetado (Oscar reportó cotización de 35 Cilindros, mínimo real 40): causa raíz = el mínimo de compra vivía SOLO como texto en el prompt, sin ninguna validación determinística en la tool `CALCULADORA` (que solo controla límites de empaque, no mínimos de pedido). Fix de doble capa: (1) prompt v1.6 con nueva "REGLA CRÍTICA — Mínimos de compra" (checklist obligatorio + tratamiento igual que Mandiles/Pantuflas); (2) `happyflops-calculadora-v2.json` (preserva workflowId `OPiuPFwRmq6QgACL`) rechaza determinísticamente cualquier cotización por debajo del mínimo cuando usa formato `items`, devolviendo error explícito en vez de un costo de envío válido. **Capa 2 (Code1) verificada directamente en producción (2026-07-15):** el código vivo era byte-por-byte idéntico al v1 del repo (confirma la causa raíz sin ambigüedad); tras pegar el nuevo `Code1`, 4/4 tests ejecutados directo en el sub-workflow `HPF - Calculadora` (sin pasar por el bot) dieron el resultado esperado: 35 cilindros → rechazo, 40 → $280, mixto sandalias+kits insuficientes → rechazo, pedido válido de ejemplo → $350 sin regresión. **Capa 1 (prompt) — paste parcial detectado (2026-07-15):** al pedir el prompt vivo para verificar, se confirmó que solo se había pegado el paso 4 de la sección CALCULADORA; faltaba la sección completa "REGLA CRÍTICA — Mínimos de compra" (25 líneas, ya referenciada 2 veces en el prompt sin existir) y 1 de las 2 aclaraciones sobre "solo recordás el mínimo cuando piden por debajo". Se entregó el prompt completo v1.6 para reemplazo total (no parches sueltos) y evitar que se repita el paste incompleto. Hallazgo colateral (repo, no bloqueante): el prompt embebido en `happyflops-main-v3.json` (repo) sigue desactualizado vs. el `.md` vigente — usa el formato legacy `cuentas` en la sección CALCULADORA en vez de `items` (export viejo, la producción real ya usa `items`). Guía completa: `06_docs/guia-fix-minimo-cilindros-2026-07-15.md`. **Pendiente: pegar el prompt v1.6 completo en el System Message del `AI Agent Recolector`** (Capa 2 ya está verificada y viva).
