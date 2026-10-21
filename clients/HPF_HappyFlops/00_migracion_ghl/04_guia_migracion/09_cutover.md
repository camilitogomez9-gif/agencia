# M9 — Cutover y Go-Live

> **Referencia:** `03_arquitectura_ghl/00_arquitectura_general.md §6`  
> **Tiempo estimado:** 2-3 horas (día del cutover)  
> **Prerequisito:** M8 completo con todos los criterios en verde

---

## 9.1 Fecha de cutover

Según el timeline definido en Etapa 2:

- **Si Etapa 3 cerró antes del 1 junio 2026:** cutover ~15 julio 2026
- **Si Etapa 3 cerró después del 1 junio 2026:** cutover ~25 julio 2026

Etapa 3 se cerró el 12 mayo 2026, por lo que aplica la fecha de **~15 julio 2026**.

El plazo de solapamiento con Kommo es viable hasta el **26 agosto 2026** (antes del siguiente ciclo de pago de Kommo).

```
Fecha de cutover target: ________________________ (confirmar con Oscar)
```

---

## 9.2 Preparación (2-3 días antes)

### D-3: Comunicar a Oscar

- [ ] Confirmar fecha y hora del cutover con Oscar
- [ ] Oscar avisa a Rebeca (si hay equipo humano involucrado)
- [ ] Verificar que plantillas Meta están aprobadas (estado: APPROVED)
- [ ] Hacer backup manual de Kommo (exportar conversaciones activas del pipeline IA)
- [ ] Documentar los leads activos en Kommo que necesitan migración manual

### D-2: Migración de leads activos

Los leads en el pipeline IA de Kommo que están en seguimiento activo necesitan importarse a GHL para no perder contexto.

**Pasos:**

1. Exportar leads activos de Kommo (pipeline IA, stages activas) como CSV
2. Para cada lead: crear Contact en GHL + Opportunity con:
   - Stage equivalente en el nuevo pipeline
   - Custom Fields relevantes (evento detectado si se sabe, teléfono, nombre)
3. Importar el historial conversacional a Supabase:
   - Los mensajes de Kommo/n8n están en Postgres (session_id `<entity_id>_2131`)
   - En GHL el session_id cambia a `<phone>_2131`
   - Hacer el mapping: copiar las filas de `messages` con el nuevo session_id

```sql
-- Migrar historial de un lead (reemplazar valores)
INSERT INTO messages (session_id, message)
SELECT 
  '+52331XXXXXXXX_2131' as session_id,  -- nuevo session_id GHL
  message
FROM messages
WHERE session_id = '[entity_id_kommo]_2131'  -- session_id actual
ORDER BY id ASC;
```

### D-1: Dry run final

- [ ] Enviar 3 mensajes de prueba al número de testing y confirmar que todo funciona
- [ ] Verificar que n8n está corriendo (no hay errores en logs)
- [ ] Verificar Supabase (espacio disponible, conexiones activas)

---

## 9.3 Día del cutover (H-hora)

### Paso 1: Congelar Kommo (5 min)

- En Kommo: desactivar el webhook de WhatsApp → los mensajes entrantes dejan de llegar a n8n (Kommo)
- Si Kommo tiene su propio bot activo (no solo n8n): pausar el bot también
- **Ventana de downtime:** desde este momento hasta que GHL esté activo = ~10-15 minutos

### Paso 2: Migrar el número de WhatsApp a GHL (10-15 min)

- En GHL → Settings → WhatsApp → "Migrate existing number"
- Seguir el proceso de Meta: verificación OTP al número `3315948670`
- Oscar debe estar disponible para recibir el OTP
- Una vez confirmado: el número está activo en GHL

### Paso 3: Verificar incoming en GHL (2 min)

- Enviar WhatsApp desde un número externo al `3315948670`
- Debe aparecer en GHL → Conversations
- WF-01 debe dispararse

### Paso 4: Activar workflows GHL (1 min)

- Verificar que WF-01 está ACTIVO (toggle en ON)
- Verificar WF-02, WF-03, WF-04, WF-05, WF-06 activos

### Paso 5: Smoke test de producción (5 min)

- Enviar mensaje de prueba → verificar respuesta completa del Vendedor
- Verificar en GHL que el Opportunity se creó en el pipeline correcto
- Verificar en Supabase que el mensaje se guardó

### Paso 6: Comunicar go-live

- Oscar confirma que ve las conversaciones en GHL inbox
- la agencia confirma que n8n procesa sin errores
- **GO-LIVE confirmado**

---

## 9.4 Post-cutover inmediato (primeras 48 horas)

### Monitoreo activo

Durante las primeras 48 horas, monitorear:

- [ ] **n8n errors:** revisar cada 2 horas los últimos runs
- [ ] **Latencia:** respuestas deben ser ≤ 8s
- [ ] **Leads en Kommo → GHL:** confirmar que leads nuevos van a GHL, no a Kommo
- [ ] **Memoria:** verificar que el historial de conversaciones se recupera correctamente para leads migrados
- [ ] **Re-engagement:** si pasan 1+ horas desde un outbound sin respuesta, confirmar que WF-02 disparó

### Alertas a Telegram (ya configuradas en M5)

n8n debe notificar a Oscar via Telegram cuando:
- Hay un error 5XX en la API de OpenAI
- Un lead activa ATENCION_PERSONALIZADA
- Un comprobante de pago es detectado

### Kommo: modo lectura solamente

- Dejar Kommo activo pero en modo observación por 2 semanas
- No hacer cambios en Kommo
- Si hay algún problema grave con GHL: Kommo es el fallback

---

## 9.5 Descomisionar Kommo (post-cutover + 4 semanas)

Solo cuando:
- GHL funcionando de forma estable por 4+ semanas
- No hay incidentes graves
- Oscar confirma que está cómodo con GHL

**Acciones:**

1. Exportar toda la data de Kommo (contactos, conversaciones, custom fields)
2. Archivar los 12 pipelines de LIMBO
3. Desactivar el pipeline IA de Kommo
4. Cancelar suscripción de Kommo antes del próximo ciclo de pago (26 agosto 2026)
5. Documentar fecha de baja en `ESTADO_MIGRACION.md`

---

## 9.6 Runbook de emergencia

Si algo falla durante o después del cutover:

### Escenario A: n8n no responde

```
1. Verificar que el servidor n8n está activo (SSH o panel de control)
2. Reiniciar n8n: pm2 restart n8n (o el método de tu deploy)
3. Verificar variables de entorno intactas
4. Test de webhook inmediato
5. Si n8n sigue fallando: activar respuesta manual en GHL (Oscar responde manualmente)
```

### Escenario B: OpenAI API caída

```
1. Verificar status.openai.com
2. Activar tag "atencion_humana" en todos los leads activos (vía GHL bulk action)
3. Notificar a Oscar para respuesta manual
4. Monitorear status.openai.com — típicamente se resuelve en < 1 hora
```

### Escenario C: Rollback a Kommo

Solo en caso de fallo catastrófico no recuperable en el día del cutover:
```
1. En GHL: desconectar el WABA (número vuelve a estar disponible)
2. En Kommo: reconectar el webhook de WhatsApp
3. Verificar que los mensajes vuelven a llegar a Kommo
4. Notificar a Oscar
5. Investigar causa del fallo antes del próximo intento de cutover
```

---

## ✅ Checklist M9 (día del cutover)

### D-3
- [ ] Fecha confirmada con Oscar
- [ ] Templates Meta aprobadas
- [ ] Backup de Kommo realizado

### D-2
- [ ] Leads activos migrados a GHL
- [ ] Historiales migrados en Supabase

### D-1
- [ ] Dry run final exitoso

### Día del cutover
- [ ] Kommo webhook desactivado
- [ ] Número migrado a GHL (OTP confirmado por Oscar)
- [ ] Incoming test exitoso en GHL
- [ ] Todos los workflows activos
- [ ] Smoke test de producción pasado
- [ ] GO-LIVE confirmado con Oscar

### 48 horas post
- [ ] Monitoreo activo completado sin incidentes graves
- [ ] Todos los leads atendidos correctamente
- [ ] `ESTADO_MIGRACION.md` actualizado con Etapa 5 en progreso

---

## 9.7 Actualizar ESTADO_MIGRACION.md después del cutover

Una vez completado el cutover, actualizar:

```
| Etapa 5 — Ejecución y monitoreo | 🟢 EN CURSO | Haiku 4.5 | Cutover [fecha] — monitoreo activo |
```

Y agregar una sección:

```
## Cutover completado

**Fecha:** [fecha]
**Hora:** [hora CST]
**Número migrado:** +523315948670
**Leads migrados de Kommo:** [cantidad]
**Incidentes durante cutover:** [ninguno / descripción]
**Kommo cancelar antes de:** 26 agosto 2026
```
