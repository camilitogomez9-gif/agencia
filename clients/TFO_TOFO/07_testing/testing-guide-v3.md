# Testing Guide v3 — TOFO Pizza (pre GO-LIVE)

**Fecha:** 2026-06-05
**Versiones cubiertas:** Derivación v1.4 · B2B **v1.5** (post-incidente Oscar Amaya) · Servicio v1.4 · Reposición v1.4 · RRSS v1.4 · Sub-workflow `Chequear disponibilidad | Tofo v2` (`vpLmZ299yXJrOSBv`, active)
**Objetivo:** validar que los cambios de v1.4 + v1.5 funcionan en producción antes de promover **TESTING → LIVE**.

---

## Estructura

- **§A — Tests pin data del sub-workflow** (8 casos en n8n, validación directa)
- **§B — Tests de conversación E2E con AI Agent** (16 casos, smoke test ManyChat / chat n8n)
- **§C — Regression tests v1.5 (caso Oscar Amaya)** (3 casos críticos de moneda)
- **§D — Checklist de promoción a LIVE**

Marcado de resultado: ⬜ pendiente · ✅ pasa · ❌ falla · 🟡 parcial

---

## §A — Tests pin data del sub-workflow v2

Ejecutar editando el `pinData` del trigger `When Executed by Another Workflow` y haciendo "Execute Workflow". Fechas calculadas asumiendo hoy = 2026-06-05 (viernes). Próximo lunes hábil = 2026-06-08.

| # | Pin data | Esperado | Verifica bug fix |
|---|---|---|---|
| A1 | `{"fecha_hora":"2026-06-03T11:00:00-06:00","nombre":"X","subscriber_id":"1","canal":"wpp","telefono":"+521..."}` | `Respond NO VÁLIDO`: `{libre:false, motivo:"fecha_pasada", mensaje:"Esa fecha ya pasó. Proponé un horario futuro: lunes a viernes, 10:00, 11:00 o 12:00 (hora México)."}` | B1.5 sin validación fecha pasada |
| A2 | `{"fecha_hora":"2026-06-06T11:00:00-06:00","nombre":"X"}` (sábado) | `Respond NO VÁLIDO`: `{motivo:"no_laboral"}` | B1.4 sin validación Lun-Vie |
| A3 | `{"fecha_hora":"2026-06-08T09:00:00-06:00","nombre":"X"}` | `Respond NO VÁLIDO`: `{motivo:"fuera_ventana"}` | B1.3 ventana laboral |
| A4 | `{"fecha_hora":"2026-06-08T13:00:00-06:00","nombre":"X"}` | `Respond NO VÁLIDO`: `{motivo:"fuera_ventana"}` | B1.3 ventana laboral (13:00 fuera) |
| A5 | `{"fecha_hora":"2026-06-08T11:30:00-06:00","nombre":"X"}` | `Respond NO VÁLIDO`: `{motivo:"minutos_no_redondos"}` | B1.6 validación minutos |
| A6 | `{"fecha_hora":"2026-06-08T11:00:00-06:00","nombre":"Test","subscriber_id":"123","canal":"wpp","telefono":"+5215555555555"}` + Google Calendar de Mauricio VACÍO ese día | `Respond LIBRE`: `{libre:true, evento_id:"...", fecha:"2026-06-08T11:00:00-06:00", fecha_humana:"lunes 8 de junio a las 11:00", mensaje:"La cita quedó agendada..."}`. Evento creado en CDMX 11:00 con summary `Reunión TOFO con Test (wpp)` y description con teléfono+subscriber_id | B1.1 timezone + B1.7 timeZone explícito + B1.8 shape estable + B1.9 metadata en evento |
| A7 | Antes: crear manualmente evento en Calendar de Mauricio `2026-06-08 11:00-12:00`. Pin: `{"fecha_hora":"2026-06-08T11:00:00-06:00","nombre":"Test"}` | `Respond OCUPADO`: `{libre:false, motivo:"ocupado", mensaje:"Ese horario está ocupado. Para ese mismo día tengo libre: 10:00, 12:00 (hora México).", alternativas:["10:00","12:00"]}`. **Después del test: borrar el evento manual.** | B1.2 solapamiento determinista + alternativas |
| A8 | Pin actual del workflow: `{"fecha_hora":"2026-06-08T11:00:00-06:00","nombre":"Test"}` | `Respond LIBRE` (si calendar vacío) o `Respond OCUPADO` (si hay otra cita ese día) | regression del pin |

**Resultado §A:** ⬜ / ⬜ / ⬜ / ⬜ / ⬜ / ⬜ / ⬜ / ⬜

**Notas:**
- Verificar que el evento creado en A6 aparezca en `Google Calendar account 2` (el credential nuevo que usa el nodo `Crear evento`), no en el calendar de `mauriciogarciadelav@gmail.com`. Si la idea era que los eventos vayan al calendar de Mauricio, revisar la credencial del nodo `Crear evento`.
- El `timeZone` explícito del nodo `Crear evento` está vacío. Funciona porque el `start`/`end` traen offset `-06:00`. Si se quiere que el UI de Google Calendar muestre la TZ correcta, agregar `additionalFields.timeZone: "America/Mexico_City"`. Opcional, no bloquea.

---

## §B — Tests de conversación E2E con AI Agent (smoke)

Probar contra el webhook real de ManyChat o directo desde n8n "Execute Workflow" del main `Agente WEB B2B y RRSS v2`.

### B.1 — Cambios v1.4 — RRSS (identidad EMMA Vivanti + pricing por sucursal + Maps)

| # | Mensaje del lead | Esperado |
|---|---|---|
| B1 | "Hola" (primer contacto desde Instagram) | El agente RRSS se presenta como **EMMA Vivanti** y dice que es agente de IA. Sin teléfono ni email en la respuesta. |
| B2 | "Cuánto sale la pizza?" | Responde con precios **$119 / $139** (Estaciones y UAG). NO menciona precios de Flex. |
| B3 | "Tengo una en Flex Norte, cuánto vale?" | Responde: "En Flex tenemos un descuento especial — los precios solo los doy en sucursal o por chat directo." NO da $109/$129 sin más. |
| B4 | "Dónde están?" → "En Zapopan norte" | Sugiere **Flex Norte** + manda link `https://maps.app.goo.gl/tT4S4iS17jxithpD7`. NO menciona precio de Flex. |
| B5 | "Dónde está Plaza Patria?" | Responde naming oficial "**Estación Plaza Patria**" + link `https://maps.app.goo.gl/7rg8ee2SvS4T4TGN6` + precio $119/$139. |
| B6 | "Tienen sucursal en Flex Oriente?" | "No tenemos punto en Flex Oriente. Nuestras 5 sucursales son: Flex Norte, Flex Sur, UAG, Estación Plaza Patria y Estación Juárez." |
| B7 | "Cuál es su email?" | "No compartimos email — todo se resuelve por aquí mismo." NO inventa email. |

**Resultado §B.1:** ⬜ / ⬜ / ⬜ / ⬜ / ⬜ / ⬜ / ⬜

### B.2 — Cambios v1.4 — B2B base (arancel transitorio + refacciones + receta)

| # | Mensaje del lead | Esperado |
|---|---|---|
| B8 | "Quiero poner una máquina TOFO en mi local" | Pide nombre + ciudad. Después cotiza Opción A y B con precios USD + equivalencias MXN + disclaimer TC. |
| B9 | "Y qué pasa si se rompe la máquina?" | Menciona **stock de refacciones en Guadalajara** (no esperar envío desde China) como diferencial. |
| B10 | "Me pasas la receta y los proveedores?" | "Te entregamos la receta completa y te ayudamos a encontrar un proveedor local cerca de tu punto. La lista exacta la aterriza el director en la llamada." NO da lista nominal de proveedores. |
| B11 | "¿Cuánto era el arancel antes y cuánto es ahora?" | "En 2025 era 15%, en enero 2026 subió a 40%. Quedan pocas máquinas con el arancel anterior." (urgencia) |
| B12 | "¿Cómo es la política de cancelación si pago el 50%?" | "Esos detalles los conversa el director contigo en la llamada." NO inventa política. |

**Resultado §B.2:** ⬜ / ⬜ / ⬜ / ⬜ / ⬜

### B.3 — Sub-workflow E2E (`check_disponibilidad`)

| # | Conversación | Esperado |
|---|---|---|
| B13 | Lead en WhatsApp pide agendar "el próximo lunes a las 11" | El agente B2B usa `fecha_contexto` del User Message → resuelve `2026-06-08T11:00:00-06:00` → invoca `check_disponibilidad` → recibe `libre:true` → activa `elevar_conversacion` con `tipo='b2b'` (interno) → confirma cita al lead con la `fecha_humana`. Evento aparece en Calendar de Mauricio. ManyChat flow `content20260526142445_613819` se dispara. |
| B14 | Lead pide "este sábado" | El agente NO debería avanzar (sábado fuera ventana). Responde: "Solo tomamos lunes a viernes…" SIN invocar `check_disponibilidad`. (o lo invoca y reacciona a `motivo:"no_laboral"`). |
| B15 | Lead pide horario con calendar ocupado en 11:00 | `check_disponibilidad` devuelve `alternativas: ["10:00","12:00"]` → agente ofrece esos slots al lead. |

**Resultado §B.3:** ⬜ / ⬜ / ⬜

---

## §C — Regression tests v1.5 (caso Oscar Amaya)

Críticos. Si alguno falla, NO promover a LIVE.

### C.1 — Protocolo de moneda (no asumir USD)

| # | Mensaje del lead | Esperado (B2B v1.5) | Anti-regresión vs v1.4 |
|---|---|---|---|
| C1 | "Tengo $250,000 de presupuesto, ¿qué máquina me alcanza?" | El agente NO afirma "te alcanza para B". Pregunta primero: "¿Es en pesos mexicanos o en dólares?" | v1.4 prometía B sin preguntar — incidente Oscar |
| C2 | "Tengo $14,000 de presupuesto" | Pregunta moneda. Si MXN → no cubre ni A. Si USD → cubre A sticker pero no end-to-end. | v1.4 podía interpretar USD por default |
| C3 | "Mi presupuesto es 250 mil pesos mexicanos" (explícito) | Convierte: $250k / 17.5 ≈ $14.3k USD. **NO cubre Opción B**. Cubre Opción A sticker pero advertir aranceles 40% + flete + seguro. Ofrecer **financiamiento externo** (banco / arrendadora / financiera). | reproduce el caso Oscar pero con prompt fixed |

**Resultado §C.1:** ⬜ / ⬜ / ⬜

### C.2 — Financiamiento externo

| # | Mensaje del lead | Esperado |
|---|---|---|
| C4 | "¿TOFO da financiamiento?" | "Nosotros no damos financiamiento directo, pero las máquinas se entregan con factura. Con esa factura puedes buscar financiamiento con un banco, una arrendadora o una financiera." NO inventa tasas, plazos, ni recomienda banco específico. |
| C5 | "Bueno, no tengo presupuesto. ¿Algún plan de pagos directo con ustedes?" | NO promete plan de pagos. Reitera: financiamiento externo (banco/arrendadora/financiera) con factura. Empuja a agendar llamada con director. |
| C6 | "¿Qué banco me recomiendan?" | NO recomienda banco específico. "El director te orienta en la llamada sobre cuál encaja con tu perfil." |

**Resultado §C.2:** ⬜ / ⬜ / ⬜

### C.3 — Equivalencias MXN + disclaimer TC

| # | Mensaje del lead | Esperado |
|---|---|---|
| C7 | "¿Cuánto cuesta la máquina lista en México en pesos?" | "$26,300 USD (~$460,000 MXN). La cifra en pesos es referencial — el tipo de cambio final lo confirma el director." (con disclaimer) |
| C8 | "Y la opción de China?" | "$9,300 USD (~$165,000 MXN) base. **Pero ojo**: sin aranceles 40%, flete, seguro y aduana. El total termina arriba. + IVA." |
| C9 | "Convierte 50 mil dólares a pesos para mi proyección" | NO da una cifra exacta como compromiso. "Como referencia ronda $875,000-$900,000 al TC actual, pero el director te confirma TC final en la llamada." |

**Resultado §C.3:** ⬜ / ⬜ / ⬜

### C.4 — Tabla decisión presupuesto vs opción

| # | Lead dice | Esperado |
|---|---|---|
| C10 | "Tengo $500,000 MXN" | Cubre B → cotiza Opción B + agendar llamada. |
| C11 | "Tengo $300,000 MXN" | Cubre A sticker pero no B + no llega end-to-end de A → ofrecer financiamiento para B + agendar. |
| C12 | "Tengo $100,000 MXN" | No cubre A → ofrecer financiamiento externo + agendar llamada con director. NO cerrar negativamente. |

**Resultado §C.4:** ⬜ / ⬜ / ⬜

---

## §D — Checklist de promoción a LIVE

Solo marcar después de §A + §B + §C pasados.

- [ ] §A — 8 tests pin data del sub-workflow OK
- [ ] §B.1 — 7 tests RRSS OK
- [ ] §B.2 — 5 tests B2B base OK
- [ ] §B.3 — 3 tests E2E check_disponibilidad OK (evento creado + ManyChat flow disparado)
- [ ] §C.1 — 3 regression moneda OK
- [ ] §C.2 — 3 financiamiento OK
- [ ] §C.3 — 3 equivalencias OK
- [ ] §C.4 — 3 tabla decisión OK
- [ ] 4 prompts v1.4 + B2B v1.5 copiados a Google Docs vivos
- [ ] Caso Oscar Amaya redirigido manualmente por Mauricio
- [ ] Status TFO en CLAUDE.md cambiado de TESTING → LIVE
- [ ] Status TFO en CLIENT_INFO.md cambiado de build → live
- [ ] Anuncio interno: agente vivo

**Tras 1 semana sin issues en LIVE:**
- [ ] Confirmar que el v1 del sub-workflow (workflowId previo) ya no se usa. (En este caso el v2 reemplazó al v1 con el mismo ID, no hay v1 separado para desactivar.)

---

## §E — Datos para test

**Hoy (referencia):** 2026-06-05 (viernes)
**Próximo lunes hábil:** 2026-06-08
**Próximo martes:** 2026-06-09
**Sábado próximo:** 2026-06-06
**TC referencial:** ~17.5 MXN/USD
**ID del sub-workflow vivo:** `vpLmZ299yXJrOSBv` (v2, active)
**Calendar de availability:** `mauriciogarciadelav@gmail.com` (credential `z0IngCgigP1wgAux`)
**Calendar de evento creado:** **`Google Calendar account 2`** (credential `CVeDywE8Gb5JgEjC`) — verificar con Mauricio que sea el correcto.

---

## §F — Referencias

- [Sub-workflow v2 (n8n vivo)](../03_workflows/chequear-disponibilidad-tofo-v2.json)
- [B2B v1.5](../04_agents/agente-tofo-b2b-system-prompt.md)
- [Doc incidente Oscar Amaya](../06_docs/incidente-confusion-moneda-2026-06-05.md)
- [Respuestas Mauricio](../06_docs/respuestas-mauricio-datos-fijos-2026-06-05.md)
- [Auditoría datos fijos](../06_docs/datos-fijos-auditoria-2026-06-04.md)
- [Testing guide v2 (38 casos, histórico)](testing-guide-v2.md)
