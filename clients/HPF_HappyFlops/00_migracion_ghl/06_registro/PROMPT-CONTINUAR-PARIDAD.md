# Prompt para continuar — HPF, cerrar la paridad con el agente original

Copiá todo lo que sigue como primer mensaje de la sesión nueva.

---

Continuamos la migración de Happy Flops de `[n8n + Kommo]` a `[n8n + GoHighLevel]`.

## El objetivo de esta sesión

Generar **un plan completo y ordenado** para corregir **todas** las diferencias entre el
agente nuevo y el original. El criterio de aceptación es **paridad exacta**: el agente nuevo
tiene que responder igual que el viejo. Si en algún caso responde distinto, se corrige —
**incluso cuando la respuesta del nuevo parezca mejor**.

No implementes todavía: primero el plan.

## De dónde salen las diferencias

Ya se corrió un test de paridad completo: 50 casos ejecutados dos veces (el nuevo por
Telegram, el viejo por WhatsApp), con las dos respuestas pegadas. Y ya se analizó.

| Archivo | Qué es |
|---|---|
| `clients/HPF_HappyFlops/07_testing/paridad-resultados-2026-08-19.md` | La corrida completa (6.701 líneas). **Es la evidencia** — ante cualquier duda, gana esto |
| `clients/HPF_HappyFlops/07_testing/analisis-paridad-2026-08-19.md` | El análisis: 6 regresiones S1, 4 S2, 4 S3, 7 heredados, con causa raíz verificada y fix propuesto |
| `clients/HPF_HappyFlops/07_testing/guia-paridad-nuevo-vs-viejo-2026-08-18.md` | La guía en blanco, para re-correr casos |

**Leé el análisis completo antes de planificar.** Tiene la causa raíz de cada cosa ya
verificada contra el sistema vivo, y varias no son la que parece.

## El hallazgo estructural que explica la mitad de todo

**La migración copió el campo equivocado de Airtable.** Cada ficha tiene dos copias del
texto: `descripcion` y el `CURL` (una captura del envío real de Kommo). Se migró
`descripcion`, que está desactualizada. Verificado:

```
Otros | Pantuflas XV            descripcion $29      →  CURL $30
Otros | Comparativa sandalias   descripcion $24/$29  →  CURL $25/$30
XV    | Pantuflas XV            descripcion $29      →  CURL $30
XV    | Comparativa sandalias   descripcion $24/$29  →  CURL $25/$30
```

El `CURL` coincide con el prompt canónico. Antes de dar por buena cualquier ficha,
compará los dos campos en `00_migracion_ghl/00_inputs/*-Grid view.csv`
(⚠️ los CSV tienen BOM: `encoding="utf-8-sig"`; el `text` del CURL se saca con
`re.search(r'"text":"(.*?)","crm_dialog_id"', curl, re.S)`).

Los 5 records de GHL con precio mal, por id:
```
6a7507435a8cdd94859ff094  Otros::Otros::Pantuflas XV                          $29 → $30
6a7507429c080e695f8e5153  Otros::Otros::Comparativa sandalias suelas d. y g.  $24/$29 → $25/$30
6a750736ba12e25112dcf25f  XV::XV::Comparativa sandalias suelas d. y g.        $24/$29 → $25/$30
6a7507325dc856b8c64ad40f  XV::XV::Pantuflas XV                                $29 → $30
6a750726e73a6ab91effc751  Boda::Boda::Pantuflas boda                          $29 → $30
```

## ⚠️ Lo primero que hay que resolver con la agencia, antes de planificar el resto

El objetivo dice "corregir incluso las mejoras". Hay **dos grupos muy distintos** ahí y
mezclarlos sería un error caro:

**Grupo 1 — diferencias que son juicio nuestro.** Revertirlas para igualar al viejo es
coherente con el objetivo. Ejemplos: URLs peladas (el viejo manda `[texto](url)` en markdown
crudo, que en WhatsApp le llega roto al cliente), no insertar el saludo espurio a mitad de
conversación (el viejo lo hizo 4 veces), avisar y derivar ante una fecha imposible (el viejo
queda mudo), el orden de la prueba social, el orden del dump de "todos los productos".

**Grupo 2 — cambios que pidió el CLIENTE explícitamente.** Revertirlos significa deshacer lo
que Oscar pidió, y en un caso contradecir algo que confirmó por escrito hace días:

| Delta | Qué hace el nuevo | Origen |
|---|---|---|
| 08 | Mandiles: el lead **elige** entre 5 modelos y se cotiza | Oscar por WhatsApp, **17/8/2026**: *"Los mandiles si los eligen de los 5 modelos que hay disponibles"* |
| 02 | Negritas y emojis en las cotizaciones | Reunión con Oscar, 11/8 |
| 06 | Ubicación separada de "¿es estafa?" | Reunión con Oscar, 11/8 |
| 07 | Pantufla de moño de peluche: una sola imagen | Reunión con Oscar, 11/8 |

**Preguntale a la agencia qué hacer con el Grupo 2 antes de meterlo en el plan.** El viejo, con
una foto de mandiles sin numerar, no puede tomar el pedido y nunca cotiza — replicar eso es
replicar una limitación que el cliente ya pidió sacar.

**Y hay un tercer caso:** el viejo tiene comportamientos que son **bugs suyos**, no
funcionalidad. Incumple su propia especificación en la línea *"(Pedidos solo para eventos
2026)"* —que está mandada verbatim en su prompt congelado y no manda en 50/50 corridas— y
**afirma que tiene mandiles en XV contra su propio catálogo**. Igualarlos al pie de la letra
significa introducir bugs a propósito. Planteáselo también.

## Las diferencias a corregir

Todas están en el análisis con evidencia y causa raíz. Resumen:

**6 regresiones S1** — R1 precios en 5 fichas · R2 no cotiza aunque tenga los datos
(intermitente; incluye el "no avisa el mínimo de cilindros" que reportó Oscar en julio, que
**es la misma frase enlatada, no un defecto aparte**) · R3 la ficha de mandiles nunca se
envía, así que desaparecen precio, mínimo y el disclaimer · R4 Vasos Popote fuera de la
lista de boda + fallback inalcanzable por construcción · R5 toda imagen que no sea foto
simple deriva y traba el lead · R6 la nota de voz le devuelve al cliente el JSON de error
de GHL.

**4 S2** — material de "Otros" apuntando a XV en cilindros · el cross-sell dirigido cayó de
7 a 2 · asume la variante de pantufla donde el viejo pregunta · reenvía el catálogo de
sandalias en un turno de pantuflas.

**4 S3** — PDFs con nombre de hash · la prueba social va antes de la cotización · el dump de
"todos" sale alfabético en vez de agrupado por producto · dice "enlace para realizar el pago"
cuando adjunta un PDF.

**7 heredados** (fallan los dos: sandalias de hombre, talla, mandiles en XV, logo propio,
desambiguación de variantes, pantufla de moño en "Otros", nota de voz). **No son regresiones
de la migración**, pero bajo el criterio de paridad exacta quedan igual — decidí con la agencia si
entran en este plan o van a uno propio de calidad de producto.

## 🔴 Lo urgente, con fecha de vencimiento

Los textos vigentes de las fichas y al menos 3 assets de cilindros de "Otros" **viven sólo
dentro de los salesbots de Kommo**. El `CURL` de Airtable cubre 40 de 65 fichas y en algunos
casos ni siquiera trae la versión vigente. Existe el workflow
`kommo-salesbot-text-capture-runner` (`bYMfYToYsZMFpVDw`) para eso.

**Correrlo completo antes de dar de baja Kommo.** Después del apagado, varios de estos fixes
dejan de ser posibles. Esto va primero en el plan.

## Reglas del proyecto que no se negocian

1. **Fuente de verdad del sistema vivo:** `03_workflows/ghl-live-2026-08-18-adjuntos-telegram/`
   (13 workflows con sha256). Los generadores `scripts/generators/hpf-gen-w*.py` están
   ATRASADOS: **regenerar y deployar borra nodos de producción.**
2. **Todo cambio de workflow va como parche dirigido de nodo:**
   `scripts/utilities/hpf-deploy-workflow.py --apply <parche.json>` (valida que el anchor
   aparezca exactamente una vez, valida todo antes de escribir, y relee del vivo). Para
   insertar nodos o tocar conexiones, el molde es
   `scripts/utilities/hpf-fix-mute-cliente-vuelve.py` o `hpf-fix-telegram-adjuntos.py`.
3. **Los prompts NO se editan en la base congelada** `04_agents/base-prod-2026-08-06/`.
   ⚠️ Y `hpf-aplicar-deltas-prompt.py --deploy` **es peligroso hoy**: compone desde la base y
   el vivo divergió (vivo 62.785 chars vs base 55.600). Mientras siga así, los cambios de
   prompt van por parche de nodo con anchor verificado **contra el vivo**.
4. **Principio medido en este proyecto:** los arreglos por **nodo** dieron 4/4 y 5/5; los
   arreglos por **prompt**, 4/7 y 3/5. Si se puede resolver en un nodo, se resuelve en un nodo.
   Ninguna de las 6 S1 necesita tocar un prompt.
5. **Read-back obligatorio:** `records/search` de GHL tiene lag de indexación y devuelve el
   valor viejo después de un PUT. Verificar siempre con **GET directo** del record.
6. **Gate de W1:** `python3 scripts/testing/hpf-l6-w1.py` → tiene que dar 8/8 y 7/7 aristas.
   `hpf-baseline-regresion.py` **no sirve para W1** (sólo pega al webhook de W6).

## Lo que hay que producir

Un plan que, para cada diferencia:
- diga **qué hace el viejo** y **qué hace el nuevo**, con la cita literal del test;
- nombre la **causa raíz verificada** (no la aparente);
- proponga el **fix concreto** (qué archivo, qué nodo, qué campo);
- indique **cómo se verifica** que quedó igual al viejo.

Ordenado por dependencias: primero lo que caduca (captura de Kommo), después los fixes de
datos (baratos y verificables), después los de nodo, y al final lo que necesita re-test.

Y con las decisiones del Grupo 2 y de los heredados **resueltas con la agencia antes de empezar**,
no asumidas.
