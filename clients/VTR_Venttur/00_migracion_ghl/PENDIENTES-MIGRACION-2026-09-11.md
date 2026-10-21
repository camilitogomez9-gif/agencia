# Guía de pendientes — Migración Venttur → GHL

**Actualizada:** 2026-09-11 · Reemplaza como referencia viva a la foto del 2026-09-07.
**Leyenda responsable:** [C] Camilo · [J] la agencia/agencia · [CL] Cliente (Venttur) · [M] Meta/terceros.

> **Foto:** la migración está casi entera. Datos y estructura ya en GHL, agente nuevo probado por Telegram. Lo que falta se divide en **lo que se puede hacer sin el número de WhatsApp** y **lo que depende de él**. El desbloqueante de todo el canal es la **verificación del WABA** (2 min del cliente en Meta).

---

## 1. Lo que YA está hecho ✅

**Datos y estructura (import ejecutado 2026-09-06):**
- Contactos **6.316** · Opportunities **2.299** · Companies **266** importados a GHL (sub-cuenta prod `7aXb4JCKsWV5nUyBXeSF`).
- **56 custom fields** + **20 pipelines** (`OP · Bot Venttur` + 19 comerciales) + tags.

**Agente nuevo (staging `3sLd7KY3o8I7NvXi`, probado por Telegram):**
- Context builder (lee estado del lead de GHL), sessionKey MX (52→521), tools `crear_contacto` + `elevar`.
- Despachador tope-2 (`vrShEXQGGAo4FqAt`), clasificador `Cualificado` (tag), barrido interrumpida.

**Hecho en la sesión 2026-09-11:**
- Migración real adoptada como base del workspace (PII/secretos gitignored) + CLAUDE.md al día.
- Plan de rotación de secretos → `06_docs/plan-rotacion-secretos-2026-09-11.md`.
- 16 plantillas de Meta redactadas → `06_docs/plantillas-meta-borradores-2026-09-11.md`.
- Tool **`cerrar_conversacion`** construida (última pieza del modelo de estados de Max) → `03_workflows/venttur-staging-agent-cerrada-v1.json`. **Valor "Cerrada" ya agregado al campo GHL ✅.**
- Aviso de respaldo de Clientify para el cliente → `06_docs/clientify-que-respaldar-antes-de-apagar.md`.

---

## 2. Lo que FALTA sin depender del número 🟢

| # | Tarea | Quién | Estado / nota |
|---|---|---|---|
| 1 | **Completar plantillas Meta**: exportar de ManyChat el nurturing drip por programa + los `seg_dia_3/5/7` → formatear | [C] exporta · [J] formatea | Las otras 16 ya están redactadas |
| 2 | **Aplicar + probar "Cerrada"**: reimportar `venttur-staging-agent-cerrada-v1.json` + probar con el bot | [J] | Campo GHL listo; falta reimport + test con su bot |
| 3 | **Terminar el despachador** (carril nurturing + política de históricos + paginación) | [J] | El nodo de envío queda gated en las plantillas |
| 4 | **Rotar secretos**: OpenAI key (credencial n8n) · Meta CAPI (Airtable) | [C] OpenAI · [CL] Meta | No urgente. Guía: `plan-rotacion-secretos` |
| 5 | **Notificación del handoff** (workflow GHL-UI: avisar a Mauricio y Max al elevar) | [J] + [CL] datos | Falta mails/chat ids del equipo |
| 6 | **Decisiones del cliente**: asesor por programa · cadencia de seguimientos · definir los 3 programas nuevos (Viajes educativos, etc.) | [CL] | Se pueden cerrar antes del número |
| 7 | **Textos del cliente**: confirmación y recordatorios de cita + textos y precios de los 3 programas nuevos | [CL] | |
| 8 | **Respaldar Clientify** (chat, adjuntos, automatizaciones) | [CL] | Aviso listo: `clientify-que-respaldar...` |
| 9 | **Verificar cruce `Agenda` / `Seguimiento agenda`** en ManyChat | [C] | Antes de tocar esos 2 flows |
| 10 | **Crear los 8 calendarios** (shells) + conectar los personales de los asesores | [J] crea · [CL] conecta | Depende de C1 (disponibilidad compartida) |

---

## 3. Lo que DEPENDE del número (WABA) 🔴

Todo esto cuelga de resolver el WABA. **El desbloqueante (#11) es una verificación de 2 minutos del cliente.**

| # | Tarea | Quién | Nota |
|---|---|---|---|
| 11 | **Desambiguar el WABA `1931874540684022`** (¿portable desde Venttur o chip nuevo?) | [CL] | En `business.facebook.com` de Venttur. Desbloquea TODO el canal |
| 12 | **Prereqs del número** (si porta): desactivar 2FA · display name aprobado · verificación de negocio · NO instalar la app de WhatsApp | [CL] | |
| 13 | **Subir las plantillas a Meta** + aprobación **24-72h** | [J] + [M] | Arrancar apenas se resuelva el WABA |
| 14 | **Envío real por GHL** (free-form + switch por canal WA/IG/FB) — increment 5 | [J] | |
| 15 | **Audio entrante** (transcripción) + dedup — increment 6 | [J] | |
| 16 | **Validaciones de sandbox** B1-B4 + C1 (con número de test) | [J] | |
| 17 | **CAPI en vivo** (probar evento real con leads entrando) | [J] | |
| 18 | **Testing E2E completo** (todos los subsistemas en verde) | [J] | Prerequisito duro del cutover |
| 19 | **Traspaso del número + cutover** (canal + agente + calendarios + deals + huérfanos) | [J] + [CL] | Downtime de minutos si porta |
| 20 | **Monitoreo +48h** post-cutover | [J] | |

---

## 4. Orden hacia el cutover

1. **[CL]** Verificar el WABA (2 min) → define portar vs chip nuevo. *(desbloquea todo)*
2. **[J+M]** Subir plantillas Meta → esperar aprobación 24-72h. *(cuello de botella)*
3. **[CL]** Prereqs del número + generar tokens Meta + respaldar Clientify + decisiones/textos.
4. **[J]** Con número de test: sandbox B1-B4/C1 → increments 5/6 (canal + audio) → despachador a producción.
5. **[J+CL]** Calendarios + confirmación/recordatorios.
6. **[J]** Notificación de handoff + aplicar "Cerrada" + rotar secretos.
7. **[J]** Testing E2E en verde (prerequisito duro).
8. **[J+CL]** Traspaso del WABA en franja de bajo tráfico → **cutover** → +48h monitoreo.

---

## 5. Documentos de referencia
- Registro completo de ejecución: `05_ejecucion/REGISTRO-EJECUCION.md`
- Detalle pre-traspaso (2026-09-07): `06_docs/guia-pendientes-pre-traspaso-waba-2026-09-07.md`
- Plantillas Meta: `06_docs/plantillas-meta-borradores-2026-09-11.md`
- Rotación de secretos: `06_docs/plan-rotacion-secretos-2026-09-11.md`
- Respaldo Clientify: `06_docs/clientify-que-respaldar-antes-de-apagar.md`
- WABA / número: `06_docs/portabilidad-numero-whatsapp-2026-08-18.md`
- Reconciliación de tracks: `_RECONCILIACION-2026-09-11.md`
