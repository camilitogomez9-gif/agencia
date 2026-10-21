Tengo todo el contexto necesario. Procedo a generar los 2 docs.


```markdown
# Diagnóstico técnico — Airtable no captura datos del lead

**Fecha:** 2026-06-19
**Cliente:** TFO (TOFO Pizza)
**Prioridad:** P1
**Status:** DIAGNÓSTICO_PENDIENTE (requiere inspección de workflow vivo)
**Fuente:** Reunión Mauricio 18/6/26 (28 min)
**Plan padre:** `/Users/camilo/.claude/plans/1-qued-resuelto-2-enchanted-trinket.md`

---

## 1. Síntoma reportado (verbatim Mauricio)

> "Inertable [Airtable] no está llenando los campos como los llenaba antes. Yo lo estoy teniendo que hacer con Cloud."

> "Del renglón 488 para arriba, todos dicen 'contacto a redes sociales' porque no cogieron nada más de información, solo cogieron la información inicial, no cogieron ni el nombre ni nada."

> "Antes sí me daba toda la información que tú ya ves después, antes sí la metía directamente el N8N y ahora ya no lo hace."

**Traducción operativa:**
- Registros 1-487 en Airtable: tienen nombre, ubicación, WhatsApp, edad/edición, datos cualificados.
- Registros 488+ (aprox. 580 registros): todos dicen "contacto a redes sociales" como nombre. Solo tienen la info inicial del primer mensaje (subscriber_id + canal). El agente conversó, capturó datos, pero esa data nunca llegó a Airtable.
- Diferencia ManyChat (1494) vs Airtable (1113) = 381 leads no migrados → mismo bug, mismo origen.

---

## 2. Hipótesis principal

**El write a Airtable ocurre al INICIO del flow con información parcial, pero NO existe un nodo UPDATE que persista los datos que el agente captura después.**

Detalle:
- Cuando entra el webhook ManyChat → main hace un write inicial a Airtable con: `subscriber_id`, `canal` ("Instagram", "WhatsApp", "Facebook"), `primer mensaje` (a veces algo genérico tipo "Hola"), `created_at`.
- El campo "Nombre completo" se llena por default con algo como `contacto a redes sociales` (placeholder) o queda en blanco.
- El agente conversa, captura nombre + ubicación + WhatsApp en los turnos siguientes, pero **ningún nodo del flow vuelve a tocar Airtable** para actualizar ese registro inicial.
- Los registros 1-487 funcionaban porque alguna versión anterior del flow (probablemente pre-v3, o pre-migración de algún sub-workflow) sí tenía esa actualización. El cambio que la removió no fue documentado y se rompió silenciosamente.

**Por qué creo que es esto y no otra cosa:**
- Si fuera bug del agente (no capturando nombre): los datos no estarían tampoco en el contexto de conversación de ManyChat. Pero Mauricio los ve en ManyChat — solo faltan en Airtable.
- Si fuera bug del write (no se crea registro): no habría 580 registros nuevos diciendo "contacto a redes sociales" — no habría ningún registro nuevo.
- El patrón "info inicial sí, info posterior no" apunta inequívocamente a falta de UPDATE.

---

## 3. Plan de diagnóstico paso a paso

### Step 1 — Leer ambos workflows
```
Read /Users/camilo/Downloads/camilo-workspace/clients/TFO_TOFO/03_workflows/agente-tofo-web-b2b-rrss-prod-snapshot-2026-06-04.json
Read /Users/camilo/Downloads/camilo-workspace/clients/TFO_TOFO/03_workflows/agente-tofo-web-b2b-rrss-v3.json
```

El snapshot es el vivo (la causa del bug está acá). El v3 es la versión que está pendiente deploy y podría reintroducir o corregir el patrón.

### Step 2 — Trazar nodos Airtable
Buscar todos los nodos con `"type": "n8n-nodes-base.airtable"` (también `airtableTrigger` y cualquier toolWorkflow que invoque sub-workflow con Airtable).

Por cada nodo:
- Nombre del nodo.
- Operación (`append`, `update`, `upsert`).
- Tabla destino (validar que sea "Leads" y no otra).
- Posición topológica (¿al inicio del flow? ¿después del AI Agent? ¿en una rama del switch?).

**Esperado encontrar:** 1 nodo de write inicial al inicio + (ausente) 0 nodos de update después.

### Step 3 — Verificar campos mapeados
Por cada nodo Airtable encontrado, listar los campos que mapea. Comparar contra schema canónico esperado:
- `Nombre completo`
- `Ubicación` (o `Zona` / `Ciudad`)
- `WhatsApp`
- `Estado embudo` / `Estado cualificación`
- `Canal`
- `Subscriber ID ManyChat`
- `Edición de la máquina` (si aplica B2B)
- `Última actividad`

**Esperado encontrar:** el write inicial solo mapea `Subscriber ID`, `Canal`, `created_at`. Los campos cualificados no se mapean en ningún lado.

### Step 4 — Verificar trigger temporal de cada write
Trazar las conexiones de cada nodo Airtable. ¿Se dispara antes del AI Agent? ¿Después? ¿En rama paralela?

Si el único write está antes del AI Agent → confirmación de la hipótesis.

### Step 5 — Comparar con versiones anteriores via git
```
cd /Users/camilo/Downloads/camilo-workspace
git log --all --oneline -- clients/TFO_TOFO/03_workflows/
git log --all --oneline -- "clients/TFO_TOFO/03_workflows/agente-tofo-web-b2b-rrss*.json"
```

Identificar la versión justa anterior a la rotura. Hacer `git show <hash>:clients/TFO_TOFO/03_workflows/<archivo>.json | grep -A 30 '"airtable"'` para ver si esa versión tenía el nodo UPDATE.

**Si encontramos la versión con el UPDATE:** restaurar el patrón. Mucho más rápido que diseñar de cero.

### Step 6 — Validar contra ManyChat custom fields
Mauricio tiene los datos en ManyChat → significa que ManyChat sí los captura (vía `setCustomFields` desde n8n o desde el bot directamente). Cruzar:
- ¿Qué custom fields de ManyChat se setean en el flow vivo?
- ¿Cuáles son los nombres exactos? (probablemente `lead_nombre`, `lead_ubicacion`, `lead_whatsapp` según estándar interno 2026)
- Esos mismos campos deberían ser los inputs del UPDATE a Airtable.

---

## 4. Plan de fix — 2 opciones

> **🆕 Principio rector (criterio explícito Mauricio 18/6/26):** *"Yo creo que se tienen que registrar todos los que dejen nombre y lugar de donde están ubicados — esa ya es una señal de interés para mí."*
>
> → Cualquier opción de fix DEBE respetar este gate: **el registro Airtable NO existe hasta que el agente capture nombre + ubicación**. Si el lead solo dice "hola" y se va, NO debe haber registro. Esto cambia el approach: NO es "crear siempre + actualizar después". Es "no crear hasta tener los 2 campos canónicos; después actualizar con info adicional".

### Opción A — Tool nueva `crear_lead_airtable` que invoca el agente

**Descripción:** crear sub-workflow `crear-lead-airtable-v1.json` que recibe `subscriber_id` + `nombre` + `ubicacion` (los 2 obligatorios — gate) + N campos opcionales (`whatsapp`, `edicion_interes`, `presupuesto`, etc.) y hace upsert en Airtable Leads por `Subscriber ID ManyChat`. El agente la invoca con `$fromAI()` cuando captura nombre + ubicación. Invocations subsecuentes en la misma conversación actualizan el registro existente (idempotente).

Regla en el prompt v1.9 (sección Tools):
> "DEBES invocar `crear_lead_airtable` apenas tengas **nombre + ubicación** del lead capturados. Si solo tenés uno de los 2, NO la invoques todavía — esperá a tener ambos. Una vez creado el registro, invocá la tool de nuevo cada vez que el lead te dé info adicional (WhatsApp, edición de interés, presupuesto) — la tool es idempotente (upsert por `subscriber_id`)."

**Importante (anti-regression):** la tool NO debe permitir invocación con solo uno de los 2 campos canónicos. Validación server-side en el sub-workflow: si `nombre` o `ubicacion` viene vacío → retornar error sin tocar Airtable. Esto blindiya contra el LLM olvidándose del criterio.

**Pro:**
- Explícito y trazable — el `sys_tool_calls` (Postgres) registra cada update con el snapshot de datos.
- Fácil de testear con casos unitarios en testing-guide v7 (§N).
- Si el agente olvida invocarla, el bug es obvio en logs.
- Permite updates incrementales (lead da nombre turno 1, ubicación turno 3 → 2 updates).

**Contra:**
- Es 1 tool más en la superficie del modelo (TOFO ya tiene ~5 tools + esta sería la 6ta). Riesgo Zod si la descripción `$fromAI()` no es minimalista (lección aprendida de SYS Episodio 2 del 2026-06-05).
- Modelo puede olvidar invocarla, especialmente en turnos largos.

### Opción B — Nodo "Update Airtable Lead" al final del flujo de cualificación, sin que el agente lo invoque

**Descripción:** agregar nodo `Update Airtable Lead` en el main, después del nodo `Formatear mensaje` (o equivalente). Lee custom fields de ManyChat actualizados que el agente seteó vía `setCustomFields` y los persiste a Airtable.

**Pro:**
- Automático, no depende del modelo.
- Cero riesgo Zod (no es una tool LLM-exposed).
- Idempotente — si el agente reenvía el mismo dato, el upsert no rompe nada.

**Contra:**
- ¿Cuándo dispararlo? La cualificación no tiene un "final" claro — es conversacional. Si lo disparamos cada turno, hacemos 1 write por turno (muchos sin cambios).
- Requiere que el agente sí haya seteado custom fields antes (vía `setCustomFields`). Si no, no hay nada que persistir.
- Acopla Airtable a ManyChat — si ManyChat falla en setear custom fields, Airtable tampoco se entera.

### Recomendación: Opción A con regla obligatoria en prompt

Razones:
1. Patrón ya validado en SYS con `guardar_email` (similar — el agente invoca cuando captura email).
2. Más control sobre qué se persiste y cuándo.
3. Logs en `sys_tool_calls` ayudan a debuggear regresiones futuras.
4. Riesgo Zod se mitiga con descripciones `$fromAI` minimalistas (lección SYS Episodio 2 ya internalizada).

**Implementación concreta:**
1. Crear `clients/TFO_TOFO/03_workflows/crear-lead-airtable-v1.json` con patrón Trigger → **Validate Input (nombre + ubicación obligatorios, error si falta uno)** → Airtable Upsert (matchear por `Subscriber ID ManyChat`) → Log Postgres → Return.
2. Wirearlo al main como toolWorkflow con descripciones minimalistas en cada `$fromAI()`.
3. **Eliminar del main el nodo de write inicial** (el que crea el registro "contacto a redes sociales" al entrar el webhook). Sin ese nodo, los leads que solo saludan no quedan en Airtable — exactamente el criterio Mauricio.
4. Agregar en prompt B2B v1.9 (y eventualmente Servicio + Reposición + Derivación + RRSS):
   > "Apenas tengas **nombre + ubicación** del lead, invocá `crear_lead_airtable` (NO antes, NO con solo uno de los 2). Una vez creado, invocá la tool de nuevo cada vez que el lead te dé info adicional (WhatsApp, edición de interés, presupuesto) — la tool es idempotente por `subscriber_id`."

---

## 5. Criterio cuándo crear registro inicial (alineado con definición Mauricio)

> "Yo creo que se tienen que registrar todos los que dejen nombre y lugar de donde están ubicados — esa ya es una señal de interés para mí."

**Decisión:**
- **NO** crear registro Airtable al primer mensaje del lead. Esperar a que el agente capture nombre + ubicación como mínimo.
- En `crear_lead_airtable` (Opción A): el primer invoke crea el registro (upsert por `Subscriber ID` — la tool exige los 2 campos en input, validación server-side), invokes subsecuentes lo actualizan.
- Esto resuelve simultáneamente el bug de los 580 registros "contacto a redes sociales" (no se crearán nuevos así) y el criterio de Mauricio (solo leads de interés en Airtable).
- **Acción complementaria (opcional, requiere aprobación Mauricio):** bulk-delete de los ~580 registros viejos "contacto a redes sociales" sin nombre/ubicación. Esto limpiaría la base históricamente. Alternativa conservadora: dejarlos y que Mauricio los procese a mano con Claude (su preferencia actual).

**Implicación de diferencia ManyChat vs Airtable:**
- Diferencia esperada legítima: ManyChat tiene TODOS los suscriptores (incluyendo los que solo mandaron "hola" y se fueron). Airtable solo los que dieron nombre + ubicación.
- Los 381 leads de diferencia actuales (1494 - 1113) que cumplen el criterio (tienen nombre + ubicación capturados en ManyChat pero no llegaron a Airtable) sí son leads que deberían migrarse, pero Mauricio dijo que lo hará a mano con Claude. Backfill fuera de scope técnico.

---

## 6. Backfill — fuera de scope

~580 registros viejos quedan como "contacto a redes sociales". Decisión de Mauricio: él los limpia a mano con Claude. **NO automatizar.** No vale el esfuerzo de implementación + riesgo de pisar datos que él ya curó manualmente.

---

## 7. Próximos pasos

1. Ejecutar Steps 1-6 del Plan de diagnóstico (requiere acceso al repo, sin credenciales externas).
2. Confirmar/descartar la hipótesis principal con evidencia.
3. Si confirmada: implementar Opción A + actualizar prompt v1.9 con regla nueva + agregar §N en testing-guide v7 (ya previsto en plan v2).
4. Smoke test E2E (caso N1 de testing-guide v7): conversación donde lead da nombre + ubicación → verificar en Airtable que el registro existe con esos campos.
5. Monitorear 1 semana post-deploy: nuevos registros deberían tener nombre + ubicación correctos.

---

## 8. Riesgos

- **Doble write:** si la versión anterior tenía un nodo UPDATE y al restaurarlo coexiste con el write inicial al webhook, podemos tener registros duplicados. Mitigación: upsert por `Subscriber ID ManyChat`, no append.
- **Modelo olvida invocar tool (Opción A):** mitigación con regla explícita en prompt + testing-guide §N obligatorio antes de promover a LIVE + monitoring de % de leads cualificados sin invoke de `update_lead_airtable` en logs Postgres.
- **Cambio de schema Airtable:** si Mauricio renombró campos en Airtable mientras tanto, los nombres en el nodo se romperán. Validar antes de implementar.

---

## 9. Vínculos

- Plan v2 fuente de verdad: `/Users/camilo/.claude/plans/1-qued-resuelto-2-enchanted-trinket.md`
- Snapshot prod main: `clients/TFO_TOFO/03_workflows/agente-tofo-web-b2b-rrss-prod-snapshot-2026-06-04.json`
- Main v3 pendiente deploy: `clients/TFO_TOFO/03_workflows/agente-tofo-web-b2b-rrss-v3.json`
- Estándar interno ManyChat custom fields: `_core/standards/manychat-integration-pattern.md`
- Lección aprendida bug Zod minimalista: `clients/SYS_SistemasYSoluciones/06_docs/incidente-bug-zod-langchain-2026-06-03.md`
```