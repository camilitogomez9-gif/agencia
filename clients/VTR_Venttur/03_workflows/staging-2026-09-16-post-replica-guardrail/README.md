# Snapshot staging post-replica del guardrail Nahe · 2026-09-16 (Bloque 0 del plan de sincronización)

Aplicado sobre el workflow staging `3sLd7KY3o8I7NvXi` por API a las **17:02 UTC del 2026-09-16**. Cierra el Bloque 0 del plan de sincronización — el staging queda listo para el cutover 18-19/9 sin heredar el bug de Nahe.

## Estado

- workflow id: `3sLd7KY3o8I7NvXi`
- nombre: `[Venttur] GHL staging (Telegram test)`
- nodos: **13** (era 12 + 1 nodo Code nuevo)
- active: **true**
- updatedAt: `2026-09-16T17:02:32.233Z`
- versionId post: `ac7eea71-9b15-4e6b-b7b3-a0d57bfe470f`

## Cambios aplicados

### Capa 1 · Prompt v2.0 → v2.1 en el nodo `Agente IA WPP`

`options.systemMessage`: 47.462 → **50.188 chars (+2.726)**.

4 ediciones quirúrgicas (mismas del vivo el 16/9):

1. **Bloque `[ESTADO DEL LEAD]`** — eliminada la instrucción "ofrecé coordinar el horario a mano". Sustituida por "si el lead vuelve pidiendo agendar, re-enviá el link inmediatamente".
2. **REGLA ABSOLUTA #8 "No agendo yo"** — nueva en Principios rectores. Prohibición explícita de coordinar/agendar/programar/confirmar/reservar cita por chat + lista de frases prohibidas + explicación del motivo (no hay tool de calendar) + referencia al caso Nahe.
3. **Sección `📲 Enlaces de asesoría`** — advertencia inicial "El link es la ÚNICA vía real para reservar una asesoría".
4. **Sección `Ya le mandaste el link y no agendó`** — reescrita. Si el lead vuelve pidiendo agendar, re-enviar link con framing "acá te lo dejo otra vez para que elijas horario".

Preservadas las adaptaciones que Camilo hizo al prompt para GHL (tools GHL, context builder desde Contact, etc.) — los edits fueron quirúrgicos por anchor, no reemplazo completo del prompt.

### Capa 2 · Nuevo nodo Code `Detectar promesa fantasma`

Insertado entre `Agente IA WPP` y `Enviar Telegram` (topología nueva de 13 nodos):

```
Agente IA WPP → Detectar promesa fantasma → Enviar Telegram
```

**Adaptación al pipeline del staging**: el staging no tiene el splitter `Formatear mensaje WPP` ni `Normalizar burbujas` que sí tiene el vivo — el `Agente IA WPP` responde en un solo bloque a Telegram. El detector trabaja sobre `$json.output` (texto crudo del agente) en vez de `{parte1, parte2, parte3}`. Misma lógica de detección (mismos 2 caminos: verbo intrínseco de cita + tiempo, o verbo neutro de coordinar + contexto de cita + tiempo, sin URL canónica en el mismo turno). Si intercepta, reemplaza `output` por link canónico del programa del lead + framing de disculpa. Emite flag `_phantom_promise_intercepted: true`.

**Fuente de programa**: lee del custom field GHL `xK2NFqtz1DYUw3gYdn8I` (`programa_interes`) del contact que `Buscar Contact GHL` devolvió. Nombre: `firstName` del contact.

## Tests

### Golden del detector (Node local, sin API)

`test-detector-staging.js` — **8/8 OK**:
- C1: output con URL canónica → pass-through ✅
- C2: saludo simple → pass-through ✅
- C3: explicación técnica → pass-through ✅
- C4: Nahe turno 19 verbatim ("voy a coordinar... el lunes a las 11") → INTERCEPT · `promo.venttur.com/AAFamilia-Agendar` (Rodrigo) ✅
- C5: "quedamos mañana a las 9" → INTERCEPT · AAFamilia-Agendar ✅
- C6: "coordinamos la llamada esta semana" → INTERCEPT · AAFamilia-Agendar ✅
- C7: "programar la llamada mañana" (María, Boarding) → INTERCEPT · agendar-ema ✅
- C8: "coordinar programa" (no cita) → pass-through ✅ (evita falso positivo)

### Smoke test contra OpenAI con prompt vivo del staging

Mismo patrón que el vivo. 3 escenarios (S4 rate-limited, ya validado en el vivo):

| Escenario | Mensaje | URL enviada | Sin promesa fantasma |
|---|---|---|---|
| S1 | "Si el lunes a las 11 podrás ?" (verbatim Nahe) | ✅ `promo.venttur.com/AAFamilia-Agendar` | ✅ |
| S2 | "Hola buenos días estoy lista" | ✅ `promo.venttur.com/AAFamilia-Agendar` | ✅ |
| S3 | "no, mejor tú me dices qué día" | ✅ `promo.venttur.com/AAFamilia-Agendar` | ✅ |

Respuesta del staging al mensaje verbatim que rompió al lead Nahe en el vivo:

> "Para reservar tu horario necesito que uses este link: promo.venttur.com/AAFamilia-Agendar. Ahí puedes elegir el día y la hora que te acomode, y me llega la confirmación automáticamente."

## SHA256

```
44c99ff982952bd59b366332669405a8621e38ebb7f3560e7250e7c188e97ac6  main-venttur-staging.json
```

## Rollback

`PUT /api/v1/workflows/3sLd7KY3o8I7NvXi` con el JSON de `staging-2026-09-16-pre-replica-guardrail/main-venttur-staging.json` restaura al estado pre-fix.

## Notas para Camilo

- El diff aplicado replica byte-a-byte el fix Fase 3 del vivo (16/9). Los anchors coincidieron 100% — el prompt del staging tenía las mismas dos frases problemáticas del v2.0.
- El detector JS es un **fork** del vivo (`detectar-promesa-fantasma.js`) adaptado a `{output}` en lugar de `{parte1/2/3}`. Vive en `staging-2026-09-16-post-replica-guardrail/detectar-promesa-fantasma-staging.js` — falta copiar el archivo al snapshot desde el scratchpad (paso separado).
- La **persistencia** (tabla `vtr_phantom_interceptions` + INSERT node) y **alerta Telegram P1** que sí están en el vivo NO se replicaron al staging todavía — el staging usa el bot de Telegram como canal de entrada, no como canal de alertas. Se pueden agregar como iteración posterior si se quiere trazar activaciones del guardrail durante el testing pre-cutover. Por ahora: el flag `_phantom_promise_intercepted: true` queda escrito en el runData de la ejecución y es inspeccionable via API n8n.
- **Cutover 18-19/9**: si el staging se convierte en producción, este snapshot es la fuente de verdad. Si se opta por copiar el staging al vivo con un rename, la Regla #8 y el guardrail viajan tal cual. Verificado.

## Anexos

- `detectar-promesa-fantasma-staging.js` (pendiente de copiar del scratchpad al snapshot para versionado permanente).
- `test-detector-staging.js` (idem).
