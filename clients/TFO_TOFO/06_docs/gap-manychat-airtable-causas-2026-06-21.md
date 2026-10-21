# Gap ManyChat (1494) vs Airtable Leads (1113) — Posibles causas

**Fecha del análisis:** 2026-06-21
**Contexto:** Mauricio reportó el gap en la reunión 18/6/26. No es un bug crítico — es la diferencia natural entre "subscribers que ManyChat conoce" y "leads que el agente n8n efectivamente procesó y guardó en Airtable". Registramos las causas probables acá por si vuelve a consultar.

---

## Marco

- **ManyChat cuenta subscribers**: cualquiera que entró al sistema (mensaje, click en CTA, CTWA ad, quick reply, broadcast).
- **Airtable contaba leads**: hasta el fix del 21/6/26, solo los que pasaron por el nodo `Crear contacto inicial` (eliminado en main v4).

Cualquier subscriber que no haya disparado el External Request a n8n no tiene row en Airtable.

---

## Causas probables (ordenadas por impacto esperado)

### 🔴 Alta probabilidad — explican la mayoría del gap

1. **Subscribers anteriores al deploy del agente n8n**. ManyChat acumula subscribers desde que se conectó la cuenta. El agente con `Crear contacto inicial` arrancó ~mayo/2026. Todo el histórico previo no tiene fila en Airtable.

2. **Subscribers que nunca dispararon el External Request**. ManyChat solo llama al webhook dentro de flows específicos (Default Reply + algunos keyword flows). Subscribers que solo respondieron quick replies, vieron broadcasts, o se quedaron en welcome flow nunca llegaron al n8n.

3. **CTWA ads (Click To WhatsApp)**. Los anuncios CTWA de Meta crean subscribers en ManyChat apenas el lead clickea el ad, sin necesidad de mandar mensaje. ManyChat los cuenta; el agente nunca los procesa.

4. **TikTok desconectado**. ManyChat sacó TikTok del plan Pro vigente. Los subscribers TikTok históricos siguen contados en los 1494 pero ya no envían al webhook.

### 🟡 Media probabilidad — decenas cada una

5. **Ventanas de workflow inactivo / debugging**. Incidentes documentados con downtime: bug Zod LangChain (3/6, ~12h debugging), incidente Mauricio cita fantasma (8/6), bump moneda (5/6), sesión Airtable fix (21/6). Mensajes recibidos durante esas ventanas posiblemente respondieron 200 OK rápido (por `Responder rápido ManyChat`) pero el resto del pipeline falló o no completó.

6. **Bug Zod LangChain — período histórico** (3/6/26). Hubo días donde tools fallaban con errores Zod. Si el error ocurría antes del `Crear contacto inicial`, esos turnos no crearon row.

7. **Manual deletions del equipo TOFO**. Mauricio o equipo posiblemente borraron rows basura periódicamente sin tocar ManyChat. Cada borrado manual aumenta el gap aparente.

8. **n8n cloud cold starts / timeouts**. TFO usa `tofo.app.n8n.cloud`. En periodos de baja actividad, primer mensaje puede timeout antes de Airtable.

### 🟢 Baja probabilidad — efecto chico

9. **Tests internos sin cleanup** (smoke tests, dev, conversaciones de prueba).

10. **Mensajes con `respuesta_definitiva` vacío** (webhook disparado sin custom field — el resto del chain no crea lead).

11. **Quota Airtable API** (raro en TFO por volumen no masivo).

---

## Validación si Mauricio quiere certeza (en orden de costo)

1. **Preguntas a Mauricio** (5 min): ¿desde cuándo está la cuenta ManyChat? ¿borran rows manualmente? ¿usan CTWA ads?
2. **Filtros en ManyChat Audience** (15 min): segmentar por source = `ctwa_ad`, channel = TikTok, last_interaction_date BEFORE 2026-05-06, "never triggered Default Reply flow". Sumar buckets.
3. **Si aún hay 100+ sin explicar** → muestreo de 50 subscribers SIN row Airtable + clasificar manual (curiosa / error captura / spam).
4. **Si muestreo revela errores** → auditar n8n executions del período.

---

## Hipótesis principal

El gap NO es un bug. Estimación grosera:

| Causa | Estimación |
|---|---|
| Pre-agente (causa #1) | ~150-200 |
| CTWA + TikTok (causas #3 + #4) | ~100-150 |
| Sin External Request (causa #2) | ~50-80 |
| Ventanas inactivas + bugs (causas #5 + #6) | ~20-50 |
| Tests + manual deletes + ruido (causas #7 + #9) | resto |

≈ 400 explicados sin bug subyacente.

---

## Estado al cierre

Con el fix del 21/6/26 (gate nombre+ubicación), Airtable a partir de ahora solo registra leads cualificados — el gap se va a ensanchar a propósito (intencional, criterio Mauricio 18/6/26: solo registrar lead real con nombre+lugar). La métrica "gap ManyChat vs Airtable" deja de ser indicador útil; reemplaza por "leads cualificados por semana" leyendo Airtable directo.
