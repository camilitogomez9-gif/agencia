# Deploy R2 — la referencia del Recolector · 2026-08-20

**Parche:** `03_workflows/parches-2026-08-20/w6-recolector-referencia-absoluta.json`
**Workflow:** W6 (`cNmJCP2qVhdtfCH0`) · nodo `Recolector` · campo `parameters.text`

---

## El cambio

```
-  =Respuesta del usuario: {{ $json.texto }}
-  Fecha de hoy: {{ $json.fecha }}
+  =Respuesta del usuario: {{ $('Normalizar entrada').first().json.texto }}
+  Fecha de hoy: {{ $('Normalizar entrada').first().json.fecha }}
```

Tres nodos alimentan al `Recolector` y sólo dos traían `texto`/`fecha`. El tercero —
`¿Requiere cotizar? [0]`, que es el camino de las cotizaciones dentro de step_3 — es un IF cuyo
input es la salida del nodo openAi `¿Consulta especial?`, o sea `{message:{content:{response}}}`.
Ahí las dos expresiones resolvían vacío y el agente contestaba desde la memoria sola.

Es una regresión de la migración: el viejo lo leía con referencia **absoluta**
(`$node["Message & Date"]`, `main-happy-flops.json:1296`).

---

## Verificación

**Sonda directa del camino roto** (secuencia B5: `hola` → `es para una boda` →
`quiero 60 sandalias gruesas al CP 44100`, que nombra producto **y** cantidad en el mismo mensaje,
o sea step_3 + consulta especial):

| | cotizó | pidió datos ya dados |
|---|---:|---:|
| **antes** | **1/3** | 2/3 |
| **después** | **5/5** | **0/5** |

Las 2 fallas del "antes" reprodujeron **verbatim** el caso B5 del test de paridad:
*"Para poder cotizarle las sandalias gruesas necesitaría que me diga la cantidad y el código
postal."*, emitido justo después del CTA.

La cotización posterior al fix coincide peso por peso con la del viejo:

```
60 Sandalias Gruesas x $30 = $1,800 · Envío: $300 · Total: $2,100 · Anticipo (50%): $1,050
```

**Integridad del workflow:** `systemMessage` intacto (62.785 chars), W6 sigue en 41 nodos,
read-back por GET confirmado dos veces (el del propio script y uno independiente).

---

## ⚠️ Efecto secundario — es una regresión real, no ruido

Baseline de regresión (6 escenarios × 2 corridas, antes vs después): **6 diferencias, todas en un
solo turno** — `oferta_precio` T4 «cuanto cuestan?», hecho justo después de una cotización.

| | antes (2/2) | después (2/2) |
|---|---|---|
| step | step_4 | **step_3** |
| respuesta | *"Las Sandalias Gruesas tienen un precio de $30 cada una"* | reenvía las fichas + PDF y **vuelve a pedir cantidad y código postal** |

**Tasa medida:** 2/2 step_4 antes · **6/6 step_3 después** (2 del baseline + 4 de una sonda
dedicada). Determinístico, no variancia del LLM.

**El mecanismo, y por qué no es azar.** Los 5 agentes de W6 comparten `n8n_chat_histories`. Al
hacer que el Recolector **cotice** en el turno 3 en vez de pedir datos, cambia lo que el `Router`
lee en el turno 4, y con eso su decisión de ruteo. Es consecuencia causal del cambio.

**Por qué el remedio obvio no sirve.** En T4 el clasificador `¿Consulta especial?` responde `no`
(su propia regla: *"preguntas como 'cuánto cuesta'… referidas a un solo producto siempre son no"*),
así que el Recolector **no corre** y el flujo va por `Recuperar cards`, que **saltea
`Partir en burbujas` por completo**. Entonces:

- mover el CTA de `Cards a partes` a `Recuperar cards` (lo que proponía el análisis) **no cambia
  nada acá**: el CTA sigue saliendo por esa misma rama;
- el filtro `yaCotizo` de `Partir en burbujas` tampoco, porque mira el texto **del turno actual** y
  en esta rama ese nodo ni siquiera se ejecuta.

**Lo que sí lo arreglaría:** suprimir el CTA cuando **la sesión ya cotizó**, que es estado, no
turno. W6 ya tiene dónde ponerlo (`hpf_estado_sesion`, con `Leer evento` / `Guardar evento`).
Es alcance nuevo respecto del plan.

---

## Valoración

**No corresponde revertir.** R2 recupera **dos cotizaciones perdidas** — plata que hoy no se
cobra. El efecto secundario degrada una respuesta que **tampoco era paridad antes**: el viejo en
B4 repite la cotización entera, y ni el "antes" ni el "después" hacen eso. B4 estaba clasificado
como EQUIVALENTE y pasaría a DISTINTO.

Queda **abierto y con dueño**: suprimir el CTA por estado de sesión.

---

## Corrección del efecto secundario — `ya_cotizo` por sesión

**Parche:** `03_workflows/parches-2026-08-20/w6-cta-solo-si-no-cotizo.json` · aplicado 2026-08-20.

Dos ediciones, sin nodos nuevos ni columnas nuevas:

1. **`Leer evento`** (que ya corre en la cadena principal de cada turno) suma un sub-select que
   responde si **la sesión** tiene alguna cotización previa en `n8n_chat_histories`, buscando
   `7 DIAS DE PROMO` — la misma marca que ya usan la regex `INDIVISIBLE` de `Partir en burbujas` y
   la condición `If4` del origen. Mismo `session_id` y misma tabla que ya consulta
   `¿Hay historial?` de W1, con el mismo guard `to_regclass`.
2. **`Cards a partes`** omite el CTA cuando esa bandera viene en `true`.

**Efecto lateral buscado:** vuelve **alcanzable** el fallback `partes.length === 0` de ese nodo,
que hoy es inalcanzable por construcción en step_3 (R4b del plan).

### ❌ REVERTIDO el mismo día — sobre-corregía

**El riesgo se confirmó y el parche se revirtió** (`w6-REVERSION-cta-solo-si-no-cotizo.json`,
aplicado y verificado; R2 quedó intacto).

**Lo que rompía.** Caso B5: el lead cotiza sandalias y después dice *"también quiero ver las
pantuflas"*.

```
[B5 1/3] step=step_3 burbujas=5 CTA=no menciona_cantidad=no
[B5 2/3] step=step_3 burbujas=5 CTA=no menciona_cantidad=no
[B5 3/3] step=step_3 burbujas=5 CTA=no menciona_cantidad=no
### pide cantidad 0/3   <- debería ser 3/3
```

El bot mostraba 5 burbujas de fichas de pantuflas y **nadie pedía cantidad ni código postal**.
El lead recibía material y silencio. **"La sesión ya cotizó" no implica "no necesito cantidad y
CP"**: el turno puede estar mostrando un producto NUEVO que todavía no se cotizó.

**Y el caso que venía a arreglar no era determinístico.** Se había medido 6/6 step_3 y después
**2/2 step_4** con un cambio que demostrablemente no toca el ruteo — el `Router` lee por
referencia absoluta (`$('Normalizar entrada')`) y su `systemMessage` no tiene ninguna
interpolación, así que agregar un campo a `Leer evento` no puede alterarlo. O sea que se estaba
pagando una regresión real y reproducible a cambio de un caso variable.

**Corrección al registro:** donde antes decía *"determinístico, no variancia del LLM"* sobre el
ruteo de ese turno, **estaba mal**. Las 6 muestras estaban correlacionadas; no probaban
determinismo.

### El camino correcto para ese caso

**R4b del plan**, no sacar el CTA: que en esa rama **corra el Recolector** (condición `OR` en
`¿Requiere cotizar?` con `sin_fichas` / con el caso de sesión ya cotizada), para que la pregunta
del lead reciba **respuesta** en vez de material mudo. Sacar el CTA ataca el síntoma y rompe el
flujo de captura; hacer que conteste ataca la causa.

### Estado final del vivo tras esta sesión

| | |
|---|---|
| `Recolector.parameters.text` | referencia absoluta ✅ (R2) |
| `Cards a partes` | 3.668 chars — original ✅ |
| `Leer evento` | 810 chars — original ✅ |
| nodos de W6 | 41 ✅ |

**Queda abierto:** el efecto secundario de R2 sobre el caso «¿cuánto cuestan?» post-cotización,
que es **variable** y cuya solución correcta es R4b.

---

## Qué dejó este episodio como método

1. **La memoria compartida acopla a los 5 agentes.** Cambiar lo que uno ESCRIBE altera lo que los
   otros LEEN en turnos posteriores, incluida la decisión de ruteo del `Router`. Cualquier cambio
   que altere el texto que produce un agente necesita el **baseline de regresión**, no sólo la
   sonda del caso que se está arreglando. El efecto secundario de R2 lo encontró el baseline; la
   sonda dirigida daba 5/5 y no lo habría visto nunca.
2. **N=2 y N=6 no son prueba de determinismo** cuando las muestras se toman en ventanas contiguas.
   Antes de declarar "determinístico", hay que separar las corridas o cambiar algo que
   demostrablemente no afecte al mecanismo y ver si el número se mueve.
3. **Antes de aplicar un fix, buscar el contraejemplo.** El de B5 no salió de una medición: salió
   de releer el caso y preguntarse si la condición nueva podía ser demasiado ancha. Costó una
   reversión en vez de una regresión en producción.
