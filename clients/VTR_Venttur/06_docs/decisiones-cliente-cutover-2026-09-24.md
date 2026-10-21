# Decisiones cliente — Cutover WABA → GHL (miércoles 24/9/2026)

Estado al **2026-09-22**: **8 de 9 decisiones cerradas**. Única abierta: **D7** (precios/textos programas huérfanos) — nice-to-have, tiene default aplicado ("consultá con un asesor"), no bloquea el cutover.

- ✅ **Bloqueantes (3/3 cerradas)**: D1 (número WABA), D2 (tope-2 toques + prioridad rescate), D3 (destinatario notificaciones).
- ✅ **Nice-to-have cerradas (5/6)**: D4 (24h), D5 (`+` con canonPhone), D6 (métrica + destinatarios W14), D8 (slugs aventureras), D9 (Diego Matus no existe).
- 🟡 **Abierta (1/6)**: D7 — Mauricio pasa textos + precios cuando pueda; el bot deriva a asesor mientras tanto.

Cada decisión: pregunta al cliente + default que asumimos hoy + impacto si el cliente decide distinto + **decisión final**.

---

## BLOQUEANTES (3)

### D1 · Número WABA  ✅ CERRADA

**Pregunta:** ¿El número operativo del WhatsApp del bot es `+52 33 2627 4502`?
**Default asumido:** Sí. Confirmado por la agencia el 21/9. En Meta Business Manager / WABA API / BSP migration aparece con el "1" de prefijo móvil que Meta antepone (`+52 1 33 2627 4502`); en el WhatsApp del lead y en display se ve sin el "1" (`+52 33 2627 4502`). Es el mismo número físico.
**Impacto si distinto:** BSP migration falla, PIN OTP no llega al SMS, cutover se posterga. Cualquier discrepancia con lo que aparece en Meta Business Manager bloquea el paso `CUTOVER-1`.
**Decisión:** Sí, es `+52 33 2627 4502`.

### D2 · Tope-2 toques + prioridad rescate > nurturing  ✅ CERRADA

**Pregunta:** ¿OK explícito de Mauricio para tope global de 2 toques por contacto y prioridad rescate sobre nurturing?
**Default asumido:** Sí. Cadencia rescate `[45min, 24h]` gana sobre despachador nurturing.
**Impacto si distinto:** Desactivar despachador `vrShEXQGGAo4FqAt` post-cutover hasta rediseñar prioridades. Los leads que caen en rescate quedan sin nurturing hasta la resolución.
**Decisión:** Sí, default correcto.

### D3 · Mails destinatarios de notificaciones  ✅ CERRADA

**Pregunta:** ¿A qué emails mandamos las notificaciones del W14 (correo semanal) y las alertas críticas del main?
**Default asumido:** Solo Telegram grupo `-4925599962` cred `botla agencia V5k84z3AjQc9Y5yg`. Sin mail. El W14 (`OaOyHA2tfjMtuWTk`) usa Gmail node con destinatario placeholder `[EMAIL-AGENCIA]`.
**Impacto si distinto:** Configurar Gmail node destinatarios en W14 + tool `elevar` de main-venttur-ghl. Cambio en 2 nodos.
**Decisión:** administracion@venttur.com

---

## NICE-TO-HAVE (6)

### D4 · Umbral barrido interrumpida  ✅ CERRADA

**Pregunta:** ¿A qué edad marcamos una conversación como "interrumpida" para dispararle el barrido? 24h vs 5 días.
**Default asumido:** 24h.
**Impacto si distinto:** Cambiar interval en `LrJuzU7qDeELWiAl` (1 nodo Schedule).
**Decisión:** 24h.

### D5 · sessionKey formato  ✅ CERRADA · aplicado en Batch F.2

**Pregunta:** ¿`+52...` o `52...` como key de `n8n_chat_histories`? El staging usa `canonPhone()` con `+`; el rescate y el despachador usan `nsk()` sin `+`.
**Default asumido:** con `+` (staging usa `canonPhone()`). Alinear rescate + despachador al mismo formato al POST-2.
**Impacto si distinto:** Rebuildear el nodo de sessionKey en rescate `YB0UxwEVwzISdd54` + despachador `vrShEXQGGAo4FqAt` con `nsk()`.
**Decisión:** default correcto.

### D6 · Correo W14 (métrica + destinatario)  ✅ CERRADA

**Pregunta:** ¿Qué se cuenta en el correo semanal? Solo citas agendadas o etapas contadas por `createdAt`? Contadas por `createdAt` vs cambio de etapa. ¿A quién se manda?
**Default asumido:** Citas agendadas · contadas por `createdAt` · destinatario `[EMAIL-AGENCIA]` (placeholder).
**Impacto si distinto:** Reescribir query GHL Opps + destinatario Gmail en `OaOyHA2tfjMtuWTk`.
**Decisión:** Citas agendadas · contadas por `createdAt` · destinatario `administracion@venttur.com` · CCO `camilitogomez9@gmail.com`

### D7 · Precios/textos Viajes / Ed.Superior / Cursos idiomas  🟡 ABIERTA

**Pregunta:** ¿Textos y rangos de precio para los 3 programas huérfanos (Viajes educativos, Educación superior, Cursos de idiomas)?
**Default asumido:** Bot responde "consultá con un asesor" hasta que lleguen los textos. Los links de agendamiento caen al fallback `promo.venttur.com/agendar-ema`.
**Impacto si distinto:** Actualizar prompt v2.3 + tabla precios + landings dedicadas por programa.
**Decisión:** _pendiente · Mauricio pasa textos + rangos cuando pueda. Default aplicado. No bloquea cutover._

### D8 · Slugs aventureras  ✅ CERRADA

**Pregunta:** ¿Confirmá los slugs de las 10 aventureras para las landings?
**Default asumido:** Los slugs que están hoy en `04-landings/html/` (editables después vía renombre en GHL Funnels + regeneración CSV).
**Impacto si distinto:** Regenerar landings + URLs GHL Funnels + CSV de aventureras.
**Decisión:** Sí, slugs confirmados.

### D9 · Diego Matus vs Diego García  ✅ CERRADA

**Pregunta:** ¿"Diego Matus" (mencionado en `runbook flujos Rodrigo 14a_runbook_flujos_rodrigo.md`) existe como persona externa? En GHL solo existe Diego García (`Y1cWtQ0KoVhP9U1iD7MV`), y está fuera del ruteo automático (decisión previa del cliente).
**Default asumido:** Diego Matus no existe. Los 131 deals reasignados a Juan José Alfaro (`6CjRtzsyf22fVa5MPDMa`). El camino "Diego" del `wf-confirmacion-agenda` se borra en el rebuild W6, no se repara.
**Impacto si es real:** Reasignar deals + crear usuario en GHL + agregar al ruteo del W6.
**Decisión:** Default correcto. Diego Matus dejó de trabajar en Venttur y sus deals se asignaron a Juan José Alfaro.

---

## Cierre

**Estado al 2026-09-22:** 8 de 9 cerradas. Cutover del 24/9 desbloqueado por decisiones cliente. Única abierta (D7) tiene default operativo aplicado; el bot deriva los 3 programas huérfanos a asesor hasta que Mauricio pase precios/textos.

**Post-cutover (jueves-viernes):** cuando Mauricio pase D7, actualizar prompt v2.3 + tabla precios + landings dedicadas por los 3 programas (o mantenerlos derivando a asesor si el negocio prefiere).
