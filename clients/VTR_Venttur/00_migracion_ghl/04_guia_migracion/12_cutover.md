# 12 · Cutover y go-live (18-19/9/2026)

> ### 🔄 Estado a 2026-09-16 — 🟢 fecha ajustada a 18-19/9
> **Nueva fecha (reunión con cliente 15/9):** cutover el **viernes 18 o sábado 19 de septiembre**. Testing en producción hasta el viernes **25/9**. Clientify renueva 26-27/9 (deadline económico). La fecha previa "15/9" quedó atrás — el cutover se retrasó por (a) atraso de nuestro lado + (b) incidente Nahe descubierto la mañana del 15/9.
>
> **✅ WABA CONFIRMADO ESCENARIO A** (Venttur compró el número, no ManyChat): portable a GHL vía "Migrate from an existing BSP". Downtime esperado: minutos. Deadline vencido de 1/9 queda sin efecto. Detalle: `ESTADO_MIGRACION.md §Actualización 2026-09-16`.
>
> Fechas y secuencia originales en `00_indice.md §📅 Calendario` — actualizar re-anchoring D-3/D-2/D-1 sobre 18-19/9. Precondición de este módulo: `11` en verde y todos los 🚦 gates cerrados.

> **🔴 El día.** La coreografía del cutover con los **gates en secuencia**, la ejecución de **B3 = Opción A (completo)**, el go-live y el **runbook de rollback**. Nada de esto arranca sin `11` en verde.
>
> **Para quién:** la agencia (ejecuta) + Mauricio/Max (accesos, OTP, confirmación). **Prerequisito:** módulos `01`-`11` cerrados. **Referencia:** `00_indice.md §gates`, `11_flujo_end_to_end.md §5`.
>
> **Estimado:** 3-4 hs el día del cutover. **Fecha:** 18 o 19 de septiembre de 2026.

---

## 12.1 La decisión que ordena el día — ✅ B3 Opción A (completo)

**El cliente eligió Opción A (2026-09-03): cutover completo, todo el 15/9.** Sale de una: canal + agente + calendarios + **todo el pipeline comercial** (6.968 contactos + 2.338 deals + 266 companies) + **los 3 huérfanos completos**. No hay 2ª ola.

> la agencia había recomendado la Opción B (por olas) por el riesgo a T-12; el cliente optó por A. **Riesgo real, declarado:** 3 dependencias de terceros (WABA, templates, assets huérfanos) + la reconstrucción manual de 2.338 deals, todo convergiendo al 15/9. **Mitigación:** todos los gates (§12.2) en verde antes del D-day; si alguno no llega, **la conversación de correr la fecha se abre antes del D-3**, no el día del cutover.

---

## 12.2 Gates en secuencia (deben estar TODOS antes del D-day)

| Gate | Verde = | Doc |
|---|---|---|
| **Sandbox** | 13 checks en verde (o fallback + OK cliente donde 🔶) | `01` |
| **WABA resuelto** | escenario A (BSP listo) o B (chip nuevo activado + ramp-up) | `05` |
| **Templates Meta APPROVED** | todas (incl. las 3 `seg_dia_*_bs`) — arrancadas 24-72h antes | `05` |
| **Auditoría migrabilidad Clientify** | entregada; el cliente respaldó lo que no migra | `06 §6.3` |
| **Owners mapeados** | confirmado con el cliente (los 2 Diegos + históricos) | `02 §2.2` |
| **Textos/assets huérfanos** | **recibidos y los 3 construidos completos** (Opción A no admite mínimo diferido) | `10` |
| **OK cliente: tope-2 + prioridad** | firmado | `08` |
| **OK cliente: Cualificado / fallback calendario** | firmado si aplica | `03`/`04` |
| **Secretos rotados** | ManyChat/OpenAI/Clientify/Meta | `00` |
| **Testing en verde** | §11.4 completo | `11` |

> ⚠️ **A T-12 el gate más frágil es la WABA** (deadline 1/9 vencido). Si es escenario B, el chip nuevo + re-aprobación de templates (24-72h) + el broadcast a los leads del número viejo **tienen que estar hechos antes del 15/9** — no el día de.

---

## 12.3 Preparación (D-3 → D-1)

**D-3:**
- [ ] Confirmar fecha/hora del cutover + decisión B3 con Mauricio/Max.
- [ ] Templates Meta en estado **APPROVED** (verificar).
- [ ] (escenario A) 2FA off + verificación de negocio + display name aprobado (`05 §5.2`).
- [ ] Backup de ManyChat (flows/subs) + export final de Clientify (contactos/deals/conversaciones que el cliente respalda).
- [ ] Documentar los leads **activos** (conversación en caliente < 24h) que necesitan continuidad.

**D-2:**
- [ ] Import de datos **completo y reconciliado** (`06 §6.4`) — Companies + los ~8.575 Contacts + los 2.338 deals en los 20 pipelines (Opción A: todo antes del cutover).
- [ ] Continuidad de memoria: las sesiones de Supabase quedan con el `session_id` canónico (teléfono, fix MX) — el histórico no se parte.
- [ ] (escenario B) broadcast de aviso de número nuevo a los leads del número viejo — **partido en lotes de ≤250/24h** (precedente Collazo: 426 → 213+213). *(El número de Clientify NO se avisa — `05`/`portabilidad §8`.)*

**D-1:**
- [ ] Dry run: 3 mensajes de prueba al número de testing → round-trip completo (Contact Reply→n8n→GHL→respuesta).
- [ ] n8n corriendo sin errores; Supabase con espacio/conexiones.
- [ ] Workflows GHL (Contact Reply, booking, template send) listos pero en pausa.

---

## 12.4 Día del cutover (H-hora)

### Paso 1 — Congelar el canal viejo (5 min)
- ManyChat: desactivar el flow `Recibir mensajes` / el External Request a n8n → los inbound dejan de entrar por ManyChat.
- **Ventana de downtime:** desde acá hasta que GHL esté activo.

### Paso 2 — Activar el número en GHL (según escenario)
- **Escenario A (portable):** `Settings → WhatsApp → Migrate from existing BSP` → seguir el flujo de Meta → OTP al número (Mauricio disponible). ⚠️ **downtime = solo el paso final de registro**, hasta que termina la duplicación de plantillas. Verificar plantillas APPROVED post-migración.
- **Escenario B (chip nuevo):** el número nuevo **ya está activo desde antes** (no se hace el día de) — acá solo se confirma que GHL Conversations recibe en el número nuevo, y que el broadcast de aviso ya salió (D-2).

### Paso 3 — Verificar inbound en GHL (2 min)
- [ ] WhatsApp desde un número externo → aparece en GHL Conversations → **Contact Reply dispara n8n**.

### Paso 4 — Activar los workflows (2 min)
- [ ] Activar en n8n: main reconstruido, despachador, CAPI, confirmación/recordatorios.
- [ ] Activar en GHL: Contact Reply trigger, booking trigger, template send.

### Paso 5 — Smoke test de producción (5 min)
- [ ] Mensaje real → el agente responde free-form completo.
- [ ] Verificar Contact en GHL (una sola alta) + memoria en Supabase.
- [ ] Un audio → transcribe.
- [ ] Agendar una cita → confirmación + etapa marcada después.

### Paso 6 — Go-live
- [ ] Mauricio/Max ven las conversaciones en el inbox de GHL.
- [ ] n8n procesa sin errores. **GO-LIVE confirmado.**

---

## 12.5 Post-cutover inmediato (48h)

Monitoreo activo (cada 2h):
- [ ] Errores de n8n (últimos runs).
- [ ] Latencia de respuesta.
- [ ] Leads nuevos → van a GHL, no a ManyChat.
- [ ] Memoria: los leads migrados recuperan su historial.
- [ ] Despachador: los toques respetan el tope 2 (no spam).
- [ ] (escenario B) el ramp-up de 250/24h no estrangula el outreach.
- [ ] Elevaciones: notifican a Mauricio Y Max.

Fallback: ManyChat queda **en observación 2 semanas** (no se toca) como red.

---

## 12.6 Descomisionar ManyChat + Clientify (post-cutover + semanas)

Solo con GHL estable + sin incidentes graves + OK del cliente:
- **ManyChat:** exportar todo → dar de baja. El número del agente ya vive en GHL.
- **Clientify:** ⚠️ **antes de apagar**, confirmar que el cliente respaldó lo que la auditoría (`06 §6.3`) marcó como no-migrable (historial, adjuntos, automatizaciones). El **segundo número de Clientify muere y NO se avisa** (`portabilidad §8`).
- (Opción A) el pipeline comercial **ya migró antes del cutover** — no hay 2ª ola pendiente; Clientify se apaga una vez confirmado el respaldo (arriba).
- Airtable Leads: congelado read-only (ya desde `06`); el CAPI se resuelve por GHL API (`09`).

---

## 12.7 Runbook de rollback

| Escenario | Acción |
|---|---|
| **n8n no responde** | reiniciar n8n; verificar env vars; test de webhook; si persiste → respuesta manual en el inbox de GHL |
| **OpenAI caída** | Assign a humano en GHL (bulk) + notificar a Mauricio/Max; monitorear status.openai.com |
| **GHL Conversations falla** | (escenario A) el número ya está en GHL — no hay vuelta a ManyChat sin re-migrar; escalar a soporte GHL. (escenario B) el número viejo de ManyChat pudo quedar disponible → reconectar el External Request de ManyChat como red |
| **Import con duplicados** | pausar el despachador (no spamear); corregir el merge; re-upsert idempotente (`06`) |
| **Confirmación/recordatorios no salen** | fallback cron n8n que lee citas próximas (C2); no bloquea el canal |
| **Rollback catastrófico (escenario A)** | ⚠️ migrar la WABA de vuelta NO es instantáneo — por eso la ventana de indisponibilidad se planifica en bajo tráfico y se prueba en D-1 |

> **Regla dura:** nunca instalar la app de WhatsApp/WhatsApp Business en el número que va a Cloud API (repite el bloqueo tipo Collazo).

---

## 12.8 Cierre — actualizar ESTADO_MIGRACION.md

```
| Etapa 5 — Ejecución y monitoreo | 🟢 EN CURSO | Cutover [fecha] — monitoreo activo |

## Cutover completado
**Fecha/hora:** [ ]  **Escenario WABA:** [A migrado / B chip nuevo]  **B3:** Opción A (completo)
**Número:** [ ]   **Contacts migrados:** [ ]   **Incidentes:** [ninguno / …]
**ManyChat baja:** [fecha]   **Clientify baja:** [fecha, tras respaldo del cliente]
```

---

*Coreografía del cutover 15/9/2026. Corrobora los gates contra `00_indice.md §gates` y las variantes de WABA contra `05`/`portabilidad`. 2026-09-03.*
