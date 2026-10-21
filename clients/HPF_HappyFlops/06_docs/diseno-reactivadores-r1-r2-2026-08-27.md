# Diseño de reactivadores R1/R2 con etapas SIN/CON/AP (2026-08-27)

Disparador: pedido de Oscar en la reunión — crear las 6 etapas nuevas del pipeline
(`R1/R2 × {SIN INFORMACION, CON INFORMACION, AP}`) y "revisar que todo el flujo de
reactivación original esté en la solución nueva".

## Hallazgo (qué existe y qué no)

Se revisaron los 8 workflows de Kommo (`03_workflows/base-prod-2026-08-06/`) y el W10 vivo
del stack GHL. Resultado:

| Etapa pedida | ¿Existe en Kommo? | ¿Existe en GHL hoy? |
|---|---|---|
| R1 SIN INFORMACION | ✅ status `89263760` | como **tag** `r1_sin_informacion` (W10) |
| R1 CON INFORMACION | ✅ status `91408768` | como **tag** `r1_con_informacion` (W10) |
| R1 AP | ❌ no existe | ❌ |
| R2 SIN / CON / AP | ❌ no existe | ❌ |

**Conclusiones:**
1. **R1 SIN/CON son portables.** El criterio es **estructural** (la etapa del embudo en que
   corre el follow-up), no un campo del lead:
   - **SIN INFORMACION** = campaña `cotizacion` (el lead llegó a ver productos pero no dio
     cantidad + código postal para cotizar). Texto del toque: *"necesito que me compartas la
     cantidad y el código postal"*.
   - **CON INFORMACION** = campaña `7pasos` (el lead ya pasó por la cotización / "7 DIAS DE
     PROMO"). El disparo es `AI Agent Recolector.output` conteniendo `"7 DIAS DE PROMO"`.
   - El clasificador OpenAI de Kommo solo decide **R1 vs Ventas Perdidas** (desinterés), NO
     decide SIN vs CON.
2. **AP = elevación a atención humana.** En Kommo es `atencion-personalizada.json`
   (3 nodos: Telegram *"necesita atención personalizada"* + PATCH `status_id = 91266100`).
   En el stack nuevo ya existe como **W5 · ATENCION_PERSONALIZADA** (Telegram *"Avisar al
   equipo"* + `W0 · mover a En Espera` + `W0 · tag atencion_humana`), invocado por la tool
   `ATENCION_PERSONALIZADA` del agente (W6/W7). **Nunca fue un destino de reactivación** — es
   un handoff que puede ocurrir en cualquier momento.
3. **El segundo ciclo R2 no existe en ningún lado.** Ni en Kommo ni en GHL hay una segunda
   tanda de toques tras R1. Los seguimientos terminan en R1 o Ventas Perdidas. **R2 es diseño
   nuevo** y su cadencia/textos/transiciones **requieren definición de Oscar** (no se pueden
   "portar").

## Estado actual del W10 (seguimientos)

- Schedule cada 5 min, tabla `hpf_seguimientos`, sub-invoca `W2 · enviar toque`.
- `Decidir acción` / `Armar cierre` tienen el map `CAMPANIAS` (rebeca / imagen / cotizacion /
  7pasos). Olas `[60, 240, 300]` min para las 3 primeras, `[]` para 7pasos, `eval_h: 24`.
- **`Armar cierre` YA soporta mover a etapa**: el `efecto` puede ser `{tag: "..."}` o
  `{etapa: "..."}`, y el nodo emite `mover_etapa`, `etapa_destino`, `tag` según cuál venga.
  Hoy `cotizacion`/`7pasos` usan `{tag: "r1_sin_informacion"}` / `{tag: "r1_con_informacion"}`.
- Los custom fields `had_information` / `had_image` / `had_quote` SÍ se escriben (por las tools
  del agente) pero **W10 no los lee** — la segmentación es 100% por nombre de campaña.

## ✅ Aplicado el 2026-08-28 (decisión del cliente)

Tras confirmar que **R2-R5 son etapas muertas** (creadas en Kommo pero sin ninguna
automatización — el cliente lo confirmó), se aplicó el sistema R1 real:

1. **W10 tag→etapa** ✅ — `Decidir acción` + `Armar cierre`: `{tag: "r1_sin_informacion"}` →
   `{etapa: "R1 SIN INFORMACION"}` y `{tag: "r1_con_informacion"}` → `{etapa: "R1 CON INFORMACION"}`.
   El dict `STAGES` de **W0** ahora incluye las 3 etapas R1 con sus stage IDs. El flujo de move
   (`¿Mover a Ventas Perdidas?` → `W0 · etapa perdida`) ya era genérico.
2. **W5 R1 AP** ✅ — se agregó el nodo `W0 · leer oportunidad`; el move es condicional: si el lead
   está en `R1 SIN/CON INFORMACION` → **R1 AP**, en cualquier otro caso → **En Espera** (original).
   Verificado E2E: R1→R1 AP y Cotizado→En Espera.
3. **Borrar R2 en GHL** — pendiente del cliente: la API de GHL **no permite borrar stages**
   (`DELETE .../stages/{id}` → 404). Las 3 etapas R2 están vacías (0 leads). Hay que borrarlas
   desde la UI de GHL: `R2 SIN INFORMACION`, `R2 CON INFORMACION`, `R2 AP`.

**Nota:** R2-R5 completos (segundo+ ciclo) NO se implementan — no existen funcionalmente en Kommo.
Si en el futuro se quiere un R2, la cadencia de R1 sirve de molde y Oscar define textos/transiciones.

## Diseño propuesto (original — referencia)

### Segmentación de las 6 etapas

| Etapa | Criterio (cuándo cae ahí) |
|---|---|
| R1 SIN INFORMACION | Campaña `cotizacion` cierra por silencio/interés sin desinterés (lead vio productos, no cotizó, no respondió al toque) |
| R1 CON INFORMACION | Campaña `7pasos` cierra igual (lead ya cotizó, no avanzó) |
| R1 AP | Un lead **dentro del ciclo R1** eleva a atención personalizada (W5) |
| R2 SIN INFORMACION | Un lead en `R1 SIN INFORMACION` que tampoco responde al segundo ciclo |
| R2 CON INFORMACION | Un lead en `R1 CON INFORMACION` que tampoco responde al segundo ciclo |
| R2 AP | Un lead **dentro del ciclo R2** eleva a atención personalizada |

### Cambios de código

1. **W10 `Decidir acción` / `Armar cierre`** — cambiar en el map `CAMPANIAS`:
   - `cotizacion`: `{tag: "r1_sin_informacion"}` → `{etapa: "R1 SIN INFORMACION"}`
   - `7pasos`: `{tag: "r1_con_informacion"}` → `{etapa: "R1 CON INFORMACION"}`
   - El resto del nodo ya soporta `efecto.etapa` (no hay que tocar la lógica).
2. **W5 · ATENCION_PERSONALIZADA** — hoy mueve el lead a "En Espera" siempre. Agregar una
   condición: si el lead está en `R1 SIN/CON INFORMACION` → moverlo a `R1 AP`; si está en
   `R2 SIN/CON INFORMACION` → `R2 AP`; en cualquier otro caso → "En Espera" (comportamiento
   actual). Requiere leer la etapa actual del lead antes de mover.
3. **W10 segundo ciclo R2 (NUEVO)** — agregar campañas `r2_sin` / `r2_con` al map `CAMPANIAS`
   que:
   - Disparen sobre leads en etapa `R1 SIN/CON INFORMACION` (o marcados con tag equivalente).
   - Manden una segunda tanda de toques con **cadencia + textos que Oscar debe definir**.
   - Al cerrar, muevan a `R2 SIN/CON INFORMACION` (silencio) o Ventas Perdidas (desinterés).

## Stage IDs (etapas creadas en GHL el 2026-08-27)

Pipeline **Happy Flops IA** — `RMnhLPqtXoWUBGZ0gvbh`:

```
"R1 SIN INFORMACION": "56423525-d55c-4bf6-8903-9aa0e7a2158c",
"R1 CON INFORMACION": "2ef6a2ab-598c-418c-bcad-8f457c87130c",
"R1 AP":              "7450c408-b419-43ef-89cc-be74ed856696",
"R2 SIN INFORMACION": "cac2f6a8-de95-44d6-9060-ad935e54c008",
"R2 CON INFORMACION": "529868d4-cb62-471b-96c3-d03f782c6485",
"R2 AP":              "9cc408ff-3b92-446d-b914-c2939caf9291",
```

## Lo que falta para implementar (bloqueos)

1. ~~**Crear las 6 etapas en la UI de GHL**~~ ✅ **HECHO** (2026-08-27, stage IDs arriba).
   Falta agregarlas al dict `ETAPAS` de W10 y cablear los efectos.
2. **Definición de Oscar para el segundo ciclo R2** (no está en ningún flujo):
   - Cadencia: ¿mismo patrón que R1 (60/240/300 min) o en días? ¿cuántos toques?
   - Texto de cada toque de R2 (distinto de los de R1).
   - ¿Cuánto tiempo espera un lead en `R1 SIN/CON` antes de entrar a R2?
   - Destino final tras R2 (¿Ventas Perdidas? ¿queda en R2 SIN/CON?).

## Preparado vs cutover WABA

- Los cambios de W10 (tag→etapa) y W5 (AP condicional) se pueden aplicar apenas existan las
  etapas — **no dependen del WABA**.
- La **activación en producción** (que R2 dispare toques reales por WhatsApp) sí depende del
  cutover del WABA + de que las plantillas Meta estén aprobadas (las plantillas HSM de Kommo
  son accesibles desde Kommo para inventariarlas antes del cutover — punto aparte).
