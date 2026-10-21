```markdown
# Decisión cliente — Plan Airtable (límite 1000 records)

**Fecha:** 2026-06-19
**Cliente:** TFO (TOFO Pizza)
**Prioridad:** P2
**Status:** ESPERANDO_DECISIÓN_MAURICIO
**Fuente:** Reunión Mauricio 18/6/26 (28 min)
**Plan padre:** `/Users/camilo/.claude/plans/1-qued-resuelto-2-enchanted-trinket.md`

---

## 1. Síntoma reportado (verbatim Mauricio)

> "Ya pasé los mil records y ya me borró todo. Y ahora qué? Request of Raid. Estos cabrones ya me van a cobrar."
> "¿Tú qué piensas que me conviene?"

**Traducción operativa:**
- La base Airtable Leads de TOFO superó el límite del plan free (1.000 records).
- Airtable borró/bloqueó registros viejos automáticamente para mantener el cap.
- Mauricio sigue recibiendo leads nuevos diariamente — el problema empeora cada día.
- Está bloqueante operativamente: sin Airtable funcional no hay CRM para seguir leads B2B.

**Contexto adicional importante:**
- ManyChat tiene 1.494 contactos (más del cap de Airtable).
- Solución del bug de captura (doc P1 `airtable-diagnostico-captura-datos-2026-06-19.md`) **va a aumentar el flujo de leads que llegan a Airtable**, no reducirlo. La decisión del plan es urgente o el bug nuevo termina rompiéndose contra el mismo techo.

---

## 2. Análisis A/B/C

### Opción A — Upgrade Airtable Team plan

**Descripción:** subir al plan Team (paid). Sube cap a 50.000 records por base, agrega features (vistas extras, automations, sync, permisos granulares).

**Costo:** ~$24 USD/usuario/mes (verificar tarifa 2026 directamente en airtable.com — Airtable cambia precios con cierta frecuencia y la fuente de verdad es su pricing page del momento de la decisión).
- Si Mauricio es el único user → ~$24/mes = ~$288/año.
- Si suma a Miguel + la agencia + otros: $24 × N usuarios/mes. Verificar en checkout.

**Pro:**
- Simple, definitivo, sin esfuerzo de implementación.
- 50.000 records dan ~5 años de margen al ritmo actual (1063 leads en 2 semanas ≈ 27.638/año — incluso así tarda 1.8 años en llenar).
- Mauricio no pierde data histórica.
- Features extras útiles a futuro (automations nativas, sync, permisos para Miguel).

**Contra:**
- Costo recurrente en USD.
- Hay que validar que Mauricio quiera el desembolso mensual fijo.

### Opción B — Auto-cleanup workflow en n8n

**Descripción:** workflow n8n programado (semanal o mensual) que borra de Airtable leads con `Estado embudo = Descartado` o más viejos que X meses sin actividad.

**Costo:** $0 recurrente + esfuerzo de implementación (~2-4 hs la agencia).

**Pro:**
- Cero costo recurrente.
- Mantiene la base "limpia" — solo leads activos/relevantes.

**Contra:**
- **Mauricio pierde data histórica permanentemente** — no recuperable después.
- Define el criterio de "descartado" requiere reglas claras que Mauricio tendría que pensar y mantener.
- **Sigue contra el techo si los leads ACTIVOS pasan 1000.** Al ritmo actual (~1000 cada 2 semanas), Mauricio llega a 1000 leads activos en ~3-4 meses. Después, el cleanup empieza a borrar leads activos. No es solución estructural.
- Mauricio ya está limpiando registros viejos a mano con Claude (los 580 con "contacto a redes sociales") — automatizar más cleanup encima de lo que ya hace a mano agrega cognición operativa.

### Opción C — Híbrido: upgrade Team + archive a Google Sheets

**Descripción:** upgrade a Team plan + workflow n8n que cada 3 meses mueve leads inactivos (sin actividad > 90 días, no agendaron cita, no en seguimiento) de Airtable a un Google Sheets de "cold storage".

**Costo:** ~$24 USD/mes Airtable + esfuerzo de implementación archive (~3-5 hs la agencia).

**Pro:**
- Balance entre capacidad y costo.
- Mauricio mantiene acceso a histórico (en cold storage) sin saturar la base operativa.

**Contra:**
- Más complejidad para un problema que la Opción A ya resuelve por 5 años.
- Google Sheets como cold storage es subóptimo (sin búsqueda potente, sin vistas, sin filtros como Airtable).
- Implementación + mantenimiento del archive workflow → más superficie de bugs futura.

---

## 3. Recomendación: Opción A (upgrade Team)

**Justificación:**
1. **Tiempo de Mauricio limpiando + riesgo de perder leads activos > $24/mes.** Ya está perdiendo tiempo manualmente con los 580 registros corruptos. Agregar más limpieza no ayuda.
2. **Resuelve el problema estructuralmente.** No tenemos que volver a tocar esto por años.
3. **Features bonus.** Vistas extras + permisos para Miguel + automations nativas Airtable pueden ahorrar tiempo a futuro (potencial reemplazo parcial de workflows n8n simples).
4. **El bug de captura de datos del doc P1 va a aumentar leads a Airtable, no reducirlos.** Si arreglamos captura y seguimos en plan free, llegamos al cap mucho más rápido que con el bug.
5. **Costo modesto vs ARR de Mauricio.** TOFO es un negocio con ARR alto (máquinas a $9.300-$26.300 USD c/u). $24/mes es <0.1% del ticket de 1 venta cerrada. Si Airtable ayuda a cerrar 1 venta extra al año, paga 30+ años de plan.

**Cuándo NO Opción A:**
- Si Mauricio dice "no quiero gastos recurrentes fijos en USD" → ir a Opción B con criterio estricto (borrar solo `Descartado` y > 12 meses inactivo) + advertir que en 4-6 meses vamos a tener que volver a la conversación cuando los leads activos pasen 1000.

---

## 4. Mensaje WhatsApp listo para Mauricio

```
Hola Mauri, te paso el análisis del tema Airtable.

El problema: pasaste los 1.000 records del plan free y Airtable bloqueó / borró registros viejos. Esto va a empeorar porque cuando arreglemos el bug de captura de datos (que ya tengo diagnosticado), van a entrar más leads completos por día.

Tenés 3 opciones:

A — Upgrade plan Team ($24 USD/mes aprox, verificar en airtable.com)
   Sube el cap a 50.000 records. Te da ~5 años de margen al ritmo actual. Es lo que te recomiendo: simple, definitivo, sin perder histórico y agrega features útiles para vos y Miguel.

B — Workflow que borra leads viejos automáticamente
   Cero costo mensual pero perdés histórico permanente y, al ritmo de leads que tenés, en 3-4 meses vamos a estar igual con los leads activos.

C — Upgrade + archive a Google Sheets cada 3 meses
   Balance pero más complejo de mantener. Honestamente, la A te resuelve por años, no le veo ventaja a C.

Mi recomendación: opción A. $24/mes es menos del 0.1% de una venta tuya, y en 2 semanas ya tenés 1.063 contactos — la base no va a parar de crecer.

¿Cómo lo querés manejar?
```

---

## 5. Decisión esperada de Mauricio (a registrar acá cuando responda)

- [ ] Opción A — proceder con upgrade.
- [ ] Opción B — implementar auto-cleanup (definir criterio).
- [ ] Opción C — implementar híbrido.
- [ ] Otra (descripción).

**Fecha decisión:** _pendiente_
**Notas adicionales Mauricio:** _pendiente_

---

## 6. Pasos post-decisión

### Si elige A:
1. Mauricio hace el upgrade desde su cuenta Airtable.
2. Verificar que el cap subió en el workspace de TOFO.
3. Backfill manual de los 381 leads de diferencia ManyChat vs Airtable queda fuera de scope técnico (Mauricio lo hace con Claude — alineado con doc P1).
4. Continuar con fix del bug de captura (doc P1).

### Si elige B:
1. Definir con Mauricio el criterio exacto de descarte (campos + thresholds).
2. Implementar workflow `clients/TFO_TOFO/03_workflows/airtable-cleanup-leads-v1.json`.
3. Smoke test sobre data de prueba antes de activar en prod.
4. Activar con frecuencia inicial conservadora (mensual) + monitorear 2 meses.
5. **Advertencia formal a Mauricio:** "En 4-6 meses vamos a tener esta misma conversación cuando los leads activos pasen 1000. Avisame con tiempo si querés cambiar a Opción A."

### Si elige C:
1. Upgrade A primero.
2. Implementar workflow `clients/TFO_TOFO/03_workflows/airtable-archive-coldstorage-v1.json` cuando esté disponible.
3. Configurar Google Sheets receptor + permisos.
4. Smoke + activación + monitoreo (idem B).

---

## 7. Riesgos

- **Mauricio puede pedir esperar a evaluar.** Bloqueante: cada día sin decidir es leads nuevos potencialmente perdidos. Mitigación: insistir en que el problema empeora cada día, no se detiene.
- **Si elige B y luego cambia a A:** sin pérdida — el upgrade es siempre upward compatible.
- **Si elige B sin definir criterio:** parálisis. Forzar definición concreta en la primera conversación (no aceptar "después vemos").

---

## 8. Vínculos

- Plan v2 fuente de verdad: `/Users/camilo/.claude/plans/1-qued-resuelto-2-enchanted-trinket.md`
- Doc hermano (bug captura): `clients/TFO_TOFO/06_docs/airtable-diagnostico-captura-datos-2026-06-19.md`
- Airtable pricing oficial: https://airtable.com/pricing
```