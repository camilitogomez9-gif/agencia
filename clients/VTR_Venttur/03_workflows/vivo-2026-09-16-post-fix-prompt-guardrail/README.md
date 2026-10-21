# Snapshot post-fix · 2026-09-16 (Fase 3 del plan Nahe)

Aplicado sobre el vivo por API n8n (`https://[TU-INSTANCIA-N8N]`) a las **14:49 UTC del 2026-09-16**. Cierra el incidente Nahe descripto en `06_docs/incidente-nahe-2026-09-15.md`.

## Cambios aplicados al `main-venttur` (`k3aivKSP67S97IHn`)

### Cambio A · Prompt v2.0 → v2.1 en el nodo `Agente IA WPP`

`options.systemMessage` del nodo: 46.868 → 49.560 chars (+2.692).

4 ediciones quirúrgicas:

1. **Bloque `[ESTADO DEL LEAD]`** — eliminada la instrucción "ofrecé coordinar el horario a mano" cuando el link ya fue enviado. Sustituida por: preguntar qué lo detuvo, y **si el lead vuelve pidiendo agendar, re-enviar el link inmediatamente**. Nunca coordinar por chat.
2. **REGLA ABSOLUTA #8 nueva · "No agendo yo"** — en la sección Principios rectores. Prohibición explícita de coordinar/agendar/programar/confirmar/reservar cita por chat, con lista de frases prohibidas ("voy a coordinar", "quedamos", "programamos la llamada", "te confirmo el horario", "coordinamos", "coordinemos"). Explica el motivo (no hay tool de calendar) y remite al caso Nahe como precedente.
3. **Sección `📲 Enlaces de asesoría`** — advertencia inicial: "El link es la ÚNICA vía real para reservar una asesoría. Cuando el lead pide agendar, tu trabajo es enviarle el link — no coordinar por chat".
4. **Sección `Ya le mandaste el link y no agendó`** — reescrita completa. Dos casos: (i) lead vuelve solo saludando → conversar normal sin re-enviar; (ii) lead vuelve **pidiendo agendar** → re-enviar el link inmediatamente con framing "te lo dejo otra vez para que elijas horario". Nunca coordinar aunque insista.

Backup de v2.0 vivo: `04_agents/agente-venttur-system-prompt-v2.0-live-backup-2026-09-16.md`.
v2.1 canónica en repo: `04_agents/agente-venttur-system-prompt-v2.1.md`.

### Cambio B · Nuevo nodo `Detectar promesa fantasma` (Code · `n8n-nodes-base.code` v2)

Insertado entre `Formatear mensaje WPP` y `Normalizar burbujas` como Capa 2 estructural (guardrail determinístico por si el prompt v2.1 falla bajo presión conversacional).

Topología nueva:
```
Agente IA WPP → Formatear mensaje WPP → Detectar promesa fantasma → Normalizar burbujas → Settear variables → Enviar WPP → Envió link? → Actualizar link
```

**Lógica**: analiza `{parte1, parte2, parte3}` del output del `Formatear mensaje WPP`. Pass-through si ya contiene una URL canónica de la whitelist. Interceptación en dos caminos:

- **Camino A · verbo intrínseco de cita** (`quedamos/nos vemos/te llamo/te llamamos/te contacto/te confirmo`) + **referencia temporal** (hora, día de semana, "mañana", "hoy", "esta semana"). Estos verbos siempre implican una cita.
- **Camino B · verbo neutro de coordinar** (`coordinar/programar/agendar/reservar/apartar/confirmar el/la/los`) + **contexto de cita/llamada/asesoría/videollamada/reunión** + **referencia temporal**. Necesita los 3 para evitar falso positivo tipo "coordinar el programa".

Si intercepta: reemplaza las 3 burbujas por link canónico del programa (mapping `Programa interés` → URL vía `Buscar si ya existe`) + framing "para reservar tu horario necesito que uses este link...". Emite flag `_phantom_promise_intercepted: true` para alerta P1 downstream (Fase 6 · pendiente).

Fallback ante duda: `promo.venttur.com/agendar-ema` (Rodrigo).

Fuente en repo: `_core/standards/detectar-promesa-fantasma.js` (pendiente de mover — vive ahora en `/tmp/vtr-diagnose/detectar-promesa-fantasma.js`). Tests golden en `/tmp/vtr-diagnose/test-detector.js`: **12/12 OK** validados en Node local antes del deploy.

## Smoke test contra OpenAI · 5 escenarios reales

Corrido sobre gpt-4o con el prompt v2.1 vivo + historial simulado con el `[ESTADO DEL LEAD]` de Nahe y el mensaje verbatim que disparó el bug:

| Escenario | Mensaje del lead | URL enviada | Sin promesa fantasma |
|---|---|---|---|
| S1 · Nahe turno 18 (disparador original) | "Si el lunes a las 11 podrás ?" | ✅ `promo.venttur.com/AAFamilia-Agendar` | ✅ |
| S2 · Nahe turno 38 (esperando cita fantasma) | "Hola buenos días estoy lista" | ✅ `promo.venttur.com/AAFamilia-Agendar` | ✅ |
| S3 · lead insiste con "tú me dices" | "no, mejor tú me dices qué día" | ✅ `promo.venttur.com/AAFamilia-Agendar` | ✅ |
| S4 · consulta de precio pura | "¿cuánto costaría el programa?" | ⚠️ (correcto — no pidió agendar todavía; el prompt cotiza rango + propone asesoría con puente de fecha, comportamiento esperado) | ✅ |
| S5 · Nahe turno 34 (aceptando hora fantasma) | "Super a las 9 me parece bien" | ✅ `promo.venttur.com/AAFamilia-Agendar` | ✅ |

**El prompt v2.1 pasa los 5 escenarios sin ninguna promesa fantasma**. El caso disparador de Nahe queda cerrado a nivel prompt.

Ejemplo de respuesta v2.1 al mensaje literal que rompió a Nahe:

> "Para reservar tu horario, necesito que uses este enlace: promo.venttur.com/AAFamilia-Agendar. Ahí puedes elegir el día y la hora que te acomode mejor, y me llega la confirmación automáticamente."

Compara con la respuesta v2.0 verbatim del mismo turno:

> "Claro, Nahe. Voy a coordinar para que tengas la asesoría el lunes a las 11. Te confirmo el horario lo antes posible."

## SHA256 · versión canónica

```
e6411613d3375021019a7ea7b9e877dab583cd00978c874194ea01423b229cd8  main-venttur.json
```

## Metadata del vivo

- workflow id: `k3aivKSP67S97IHn`
- versionId: `9a86946c-a595-4678-b134-48a27c91822f`
- nodos: 40 (era 39 + 1 nuevo `Detectar promesa fantasma`)
- active: **true**
- updatedAt: `2026-09-16T14:49:10.484Z`

## Rollback

En caso de regresión, importar por API el JSON de `vivo-2026-09-16-pre-fix-prompt-guardrail/main-venttur.json` (snapshot inmediatamente anterior al deploy).

## Pendiente Fase 6 · alerta P1 desde el flag `_phantom_promise_intercepted`

Este snapshot deploya la **interceptación**, pero **no** la **alerta P1** que debería sonar cuando el guardrail se dispara. Diseño de la alerta (para segundo commit):

- IF `{{ $('Detectar promesa fantasma').first().json._phantom_promise_intercepted === true }}` en paralelo a la salida de `Detectar promesa fantasma`
- HTTP Telegram al bot Venttur con payload `{execution_url, id_2, nombre, programa, url_correcta, mensaje_original, mensaje_reemplazado}`
- No bloquea el envío al lead — corre en paralelo.

Se agrega en la iteración siguiente. Mientras tanto, el flag queda escrito en el JSON del turno y es detectable via query a `n8n_chat_histories` o `n8n_executions_entity`.

## Deuda que queda para después (no bloquea el fix)

- **Fase 5 · barrido de cohorte** — script que detecte otros "Nahes" en los últimos 30 días. El patrón se refinó en el incidente-report (`06_docs/incidente-nahe-2026-09-15.md` §"Alcance de la cohorte").
- **Fase 6 · alerta P1 estructurada** (arriba).
- **Fase 6 · reconciliador transversal** (Airtable ↔ Postgres ↔ ManyChat ↔ GHL).
- **Fase 7 · contrato de diseño GHL** — trasladar la regla "no prometer acciones que no se pueden ejecutar" como REGLA ABSOLUTA del prompt GHL cuando se cierre la migración.
- **Fire-and-forget en `Enviar WPP`** (deuda técnica identificada en Fase 0, no relacionada al caso Nahe pero vigente).
- **`resumen-etiquetas-seguimientos` inactive** — investigar por qué está apagado.
