# Upsell: CRM de Leads (tabla Leads + vistas operativas + tool write completo)

## Cliente
- ID: SYS
- Nombre: Sistemas y Soluciones
- Fecha identificación: 2026-05-28

## Oportunidad

Durante la ejecución de F1 (migración Airtable) el cliente comunicó que **NO quiere avanzar con la implementación CRM en esta etapa**. El sistema queda en alcance reducido: el agente notifica leads por mail a `info@sistemasysoluciones.com` y por Telegram al el equipo, pero **no traquea el ciclo de vida del lead en Airtable** (status, derivación, cierre, ganado/perdido).

La oportunidad es activar el CRM completo cuando el cliente lo apruebe (con la cotización correspondiente). El sistema ya está pre-construido para eso — solo hay que descomentar los pasos relevantes en la tool `notificar_lead` y crear las vistas operativas.

## Origen
- [x] Decisión del cliente (alcance reducido durante F1)
- [ ] Pedido del cliente
- [ ] Propuesta nuestra
- [ ] Reunión de revisión

## Qué QUEDA dentro del alcance actual (sin CRM)

- Tabla `Leads` creada en Airtable, **vacía y sin uso productivo**
- Tool `notificar_lead` modificada: NO escribe en Airtable, solo envía mail a `info@` + Telegram a la agencia
- Tabla `Representantes` con 1 record "Equipo Comercial" (mantiene el destino del mail)

## Qué se ACTIVA con este upsell

### Componentes técnicos a habilitar

1. **Tool `notificar_lead`** — restaurar pasos completos del workflow:
   - Search idempotencia (lead existente en últimos 30 min)
   - Airtable Create record en tabla Leads
   - Airtable Update con Status, Notificación enviada, Fecha derivación, session_id
   - (Mantener) mail + Telegram

2. **Vistas críticas Airtable Leads** (no creadas en F1):
   - `Nuevos hoy` — `Fecha creación` is today, sort by created desc
   - `Pendientes derivación >24h` — `Status` = "En conversación" AND `Última actividad` is before 1 day ago
   - `Derivados` — `Status` = "Derivado"
   - `Por representante` — group by `Representante asignado`
   - `Cerrados ganados` — `Status` = "Cerrado-Ganado"

3. **Tool `notificar_lead` Opción B (especialización por rep)** — opcional, segundo nivel del upsell. Activar lookup en tabla `Representantes` por línea + zona si el cliente quiere segmentar comercial.

4. **Dashboard operativo Airtable Interfaces** — vista única con métricas: leads nuevos/derivados/cerrados, tiempo promedio de derivación, conversión por canal.

5. **Workflow seguimiento automático** (referenciado en CLIENT_INFO OKR 4 → "Seguimiento: día siguiente + semana siguiente, máximo 2 mensajes"):
   - Cron diario que detecta leads en `Pendientes derivación >24h` y envía mensaje automático via ManyChat (`sendFlow`)
   - Cron a 7 días para 2do toque
   - Marcar lead como "Descalificado" si no responde después del 2do toque

6. **Reporte semanal por mail** al Gerente con KPIs: # leads nuevos, # derivados, % conversión, fuente principal (WA/IG/FB), tecnología más consultada.

### Stack involucrado

- Airtable (ya existente, solo activar vistas + dashboard)
- n8n (modificar 1 sub-workflow + crear 2 nuevos: seguimiento + reporte semanal)
- Gmail (reporte semanal al Gerente)
- Opcional: integración Clientify/HubSpot si el cliente ya tiene CRM externo

## Estimación económica

- **Setup CRM básico (tool + vistas + dashboard):** USD 200-300 único
- **Seguimiento automático (2 workflows nuevos):** USD 150 único
- **Reporte semanal automático:** USD 100 único
- **Opción B (especialización por rep, lookup avanzado):** USD 100 único
- **Mantenimiento mensual añadido:** USD 30/mes (sobre el retainer base)

**Total setup completo upsell:** USD 450-650 único + USD 30/mes adicional al retainer base.

**Bundle sugerido (CRM + Seguimiento + Reporte):** USD 500 único + USD 30/mes.

## Próximos pasos

- [ ] Cuando el cliente reactive: revisar este doc y armar propuesta formal con la cotización elegida
- [ ] Validar con el cliente si quiere Opción A (rep único) u Opción B (especialización)
- [ ] Confirmar mail del Gerente (si querés que reciba reporte semanal — hoy va `info@`)
- [ ] Crear plan táctico `/crear-plan sys-upsell-crm-leads-YYYY-MM-DD`
- [ ] Implementar en orden: vistas Airtable → reactivar tool → workflow seguimiento → reporte semanal

## Componentes existentes que ya soportan este upsell (cero re-trabajo cuando se active)

- ✅ Tabla `Leads` Airtable creada con todos los campos (`05_crm/airtable-syscatalogo-schema.md` Tabla 10)
- ✅ Tabla `Representantes` con record fallback "Equipo Comercial"
- ✅ Tool 8 `notificar_lead` documentada en `06_docs/tools-spec-v1.md` con dos versiones (la actual reducida + la completa CRM)
- ✅ Postgres `sys_session_state` con campo `lead_airtable_id` listo para vincular cuando se reactive el write
- ✅ Runbook menciona las queries SQL para auditar leads cuando exista CRM

## Estado
- [x] Identificado
- [ ] Propuesto al cliente
- [ ] Aprobado
- [ ] En desarrollo
- [ ] Entregado

## Notas

- El cliente vio el sistema sin CRM funcionando bien (espera de uso en F8 GO LIVE). Es muy probable que después de 2-4 semanas de producción quiera el CRM porque van a notar la falta de tracking. **Re-proponer al mes 1 post-GO-LIVE**.
- Si el cliente sigue sin querer CRM después de 3 meses: evaluar si vale la pena dejar la tabla Leads creada o limpiarla.
