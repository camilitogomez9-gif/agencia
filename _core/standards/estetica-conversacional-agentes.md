# Estética Conversacional para Agentes de IA — Estándar interno

> **Estado:** vivo — se actualiza a medida que validamos patrones en clientes reales.
> **Origen:** validado en HPF (Happy Flops, WhatsApp/Telegram, gpt-4.1) el 2026-07-24.
> **Alcance:** cualquier agente conversacional de mensajería (WhatsApp, IG, Messenger, Telegram).
> **Portabilidad:** documento client-agnostic. Migrable tal cual a otro workspace.

---

## 1. El principio

Un agente suena a bot no por *lo que dice* sino por **cómo lo escribe**. El modelo, por defecto, escribe como redacción formal: mayúscula inicial, signos de apertura, párrafos completos, listas con guiones, fórmulas de cortesía. Nadie escribe así en WhatsApp.

**Objetivo:** que el lead sienta que del otro lado hay una persona tecleando, no un sistema respondiendo.

**Límite ético (no negociable):** humanizar el *estilo* no es fingir ser humano. Si el lead pregunta si habla con un bot, el agente **dice la verdad**. Cambiar eso es una decisión del cliente, no una decisión de estilo — y conviene dejarla asentada por escrito.

---

## 2. Las tres capas

La estética no se logra solo con prompt: los LLM son inconsistentes con reglas de formato. Se necesitan tres capas.

| Capa | Qué resuelve | Por qué |
|------|--------------|---------|
| **1. Prompt** | Tono, vocabulario, semántica del corte de mensajes | Es la única capa que entiende *qué* separar |
| **2. Post-proceso determinístico** | Signos, formato, división en burbujas | El modelo se olvida; el código no |
| **3. Bloques protegidos** | Textos fijos del negocio | Evita que las capas 1 y 2 rompan lo que no deben tocar |

**La capa 3 es la que más se olvida y la que más caro sale.** Un sanitizer que "humaniza todo" te destroza la cotización, el mensaje legal o la plantilla aprobada por Meta.

---

## 3. Capa 1 — Reglas de escritura (para pegar en el prompt)

Sección sugerida: `[1b] CÓMO ESCRIBÍS`. Adaptar vocabulario al país del cliente.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1b] CÓMO ESCRIBÍS (WhatsApp real, NO corporativo)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Escribís como una persona real tecleando rápido en WhatsApp, no como un chatbot formal.

1. Empezá los mensajes en MINÚSCULA ("hola! claro que sí..." — nunca "¡Hola! Claro que sí...").
   Los nombres propios conservan su mayúscula.
2. NO uses signos de apertura. Escribí "como te ayudo?" y "que padre!", jamás "¿cómo...?" ni "¡qué...!".
   Los signos de CIERRE (? y !) sí se usan.
3. IMPORTANTE — una idea por LÍNEA. Cada línea se envía como un mensaje SEPARADO,
   como cuando alguien manda varios mensajitos seguidos.
   Usá 2 a 4 líneas cortas por respuesta. Separá saludo, pregunta y dato en líneas distintas.
   Nunca metas todo en un párrafo corrido. Nada de listas con guiones.
4. Máximo 1 emoji por mensaje, y a veces ninguno. Nunca un emoji por línea.
5. No repitas el nombre de la empresa ni tu rol en cada mensaje: eso ya se dijo al inicio.
6. Nada de negritas ni markdown en la charla normal.
7. Muletillas naturales del país (MX: "va", "sale", "ahorita", "porfa", "dale", "mira").
8. NO abras con fórmulas de call center ("Gracias por tu mensaje!", "Gracias por tu interés!",
   "Te comento que..."). Entrá directo al punto.

⚠️ EXCEPCIÓN — estos bloques se escriben SIEMPRE tal cual, con su formato y signos originales
(son textos fijos del negocio, NO los humanices):
   · <listar acá los bloques canónicos del cliente>
```

**Los ejemplos son lo que más mueve la aguja.** Incluir siempre un "Así SÍ" en formato multi-línea y un "Así NO" con las respuestas robóticas reales que salieron en testing:

```
Así SÍ (cada línea es un mensajito aparte):

hola! soy <Nombre> 😊
para qué evento buscas los recuerditos?

qué padre, unos XV!
qué productos te interesan?
tenemos sandalias, cilindros, pantuflas y kit anticruda

Así NO (robótico / corporativo):

"¡Hola! Soy <Nombre>, asistente virtual de <Empresa> en <Ciudad>. 😊"
"¡Gracias por tu interés! Te comento que..."
"Para cotizarte, solo necesito:
 - ¿Cuántos pares?
 - ¿Prefieres...?"
```

---

## 4. Capa 2 — El insight clave: **una línea = una burbuja**

El error típico es partir los mensajes por línea en blanco (`\n\n`). El modelo escribe un párrafo corrido y sale **una sola burbuja larga** — que es exactamente lo que delata al bot.

**La regla correcta:** el modelo decide la semántica del corte (capa 1: "una idea por línea") y el código la ejecuta (capa 2: cada línea → un mensaje). Así:

| El modelo escribe | El lead recibe |
|---|---|
| `hola! soy Rebeca 😊`<br>`para qué evento buscas los recuerditos?` | 💬 hola! soy Rebeca 😊<br>💬 para qué evento buscas los recuerditos? |

Por qué no hacerlo puramente determinístico (partir por oraciones): el agrupamiento correcto es **semántico**. "hola! soy Rebeca 😊" son dos oraciones pero **una** burbuja; la pregunta que sigue es otra. Ningún regex acierta eso — el modelo sí.

**Cadencia:** un `Wait` de 1–1.5s entre burbujas. Menos se siente robótico (llegan juntas); más se siente lento.

---

## 5. Capa 2 — Código (n8n Code node, paste-ready)

Genérico. Solo hay que ajustar `isCanon` y la constante del teléfono oficial.

```javascript
let text = $json.output || '';

text = text.trim();
if ((text.startsWith('"') && text.endsWith('"')) || (text.startsWith("'") && text.endsWith("'"))) {
  text = text.slice(1, -1);          // el modelo a veces envuelve todo en comillas
}

// markdown -> WhatsApp
text = text.replace(/\*\*/g, '*');
text = text.replace(/^#{1,6}\s*/gm, '');

// ── CAPA 3: líneas que pertenecen a un bloque FIJO del negocio.
//    No se humanizan ni se parten: van enteras. AJUSTAR POR CLIENTE.
const isCanon = (l) =>
  /⏳|HAZ TU PEDIDO|SENCILLOS PASOS|SEMANA LOCA|DIAS DE PROMO/i.test(l) ||
  /^\s*\d+[.)]\s/.test(l) ||                                        // listas numeradas canónicas
  /x\s*\$|^\s*(Total|Env[íi]o|Anticipo|Subtotal)\s*[:(]/i.test(l);  // líneas de cotización

// reglas de negocio del cliente (ej.: nunca revelar peso)
text = text.split('\n').filter(l => !/\bkg\b|\bpeso\b/i.test(l)).join('\n');

// humanización: fuera los signos de apertura (salvo bloques fijos)
text = text.split('\n').map(l => isCanon(l) ? l : l.replace(/[¿¡]/g, '')).join('\n');

// ningún teléfono que no sea el oficial
const OFICIAL = '0000000000';
text = text.replace(/\b\d{7,10}\b/g, (m) => (m === OFICIAL ? m : ''));
text = text.replace(/[ \t]{2,}/g, ' ');

// ── agrupado en burbujas: cada línea conversacional = 1 mensaje;
//    los bloques fijos se mandan enteros.
const parts = [];
let buf = [], bufCanon = false;
const flush = () => { const s = buf.join('\n').trim(); if (s) parts.push(s); buf = []; };

for (const raw of text.split('\n')) {
  const line = raw.trim();
  if (!line) { flush(); bufCanon = false; continue; }
  if (isCanon(line)) {
    if (!bufCanon) flush();
    buf.push(line);
    bufCanon = true;
  } else {
    if (bufCanon) { flush(); bufCanon = false; }
    parts.push(line);
  }
}
flush();

// tope de burbujas: el excedente se junta en la última
const MAX = 6;
let out = parts.filter(Boolean);
if (out.length > MAX) out = out.slice(0, MAX - 1).concat([out.slice(MAX - 1).join('\n')]);
if (!out.length) out = [text.trim()];

return out.map((p) => ({ message_part: p }));
```

Downstream: `Loop Message Parts` (splitInBatches) → enviar `message_part` → `Wait 1.5s` → loop.

---

## 6. Capa 3 — Qué NUNCA se humaniza

Antes de escribir una sola regla de estilo, **listar los bloques canónicos del cliente**. Típicamente:

- Cotizaciones / presupuestos (headers, líneas de ítems, totales)
- Textos legales, de garantía o de política
- Plantillas aprobadas por Meta (WhatsApp Template Messages) — alterarlas **rompe la aprobación**
- Instructivos numerados que el cliente considera "su" texto
- Datos de pago, direcciones, links

**Trampa conocida:** un sanitizer que hace `join(' ')` para limpiar espacios **aplasta todos los saltos de línea** y convierte la cotización en un renglón corrido — y encima deja muerto el split. Colapsar solo espacios/tabs (`[ \t]{2,}`), nunca `\n`.

---

## 7. Verificación

Antes de dar por buena la estética:

1. **Unit test del sanitizer** fuera de n8n (Node) con: saludo multi-línea, respuesta con pregunta, cotización completa, bloque canónico con signos.
   - ✅ cada línea conversacional → burbuja propia
   - ✅ bloque canónico → **una** burbuja, con su formato y signos intactos
   - ✅ sin `¿`/`¡` fuera de los bloques
2. **Test en vivo** (curl al webhook o el canal real) de 3–4 turnos y lectura a ojo: ¿parece una persona?
3. **Regresión**: la cotización sigue con los montos y el formato correctos.

---

## 8. Anti-patrones (observados en producción)

| Anti-patrón | Cómo se ve | Fix |
|---|---|---|
| Párrafo único | Una burbuja de 4 renglones | Capa 1 regla 3 + split por línea |
| Fórmula de apertura | "Gracias por tu mensaje! Te comento que..." | Regla 8 explícita |
| Lista con guiones para pedir datos | `- ¿Cuántos?` `- ¿Cuál prefieres?` | Pedirlos en una frase natural |
| Emoji por línea | 😊 en cada renglón | Máx. 1 por mensaje |
| Repetir marca/rol | "de <Empresa>" en cada turno | Regla 5 |
| Sanitizer que aplasta `\n` | Cotización en un renglón | Colapsar solo `[ \t]` |
| Humanizar un template de Meta | Template rechazado | Bloques protegidos |

---

## 9. Pendientes / a explorar

- **Minúscula inicial determinística**: hoy es solo prompt. Forzarla por código rompe nombres propios; requeriría whitelist. Evaluar si vale.
- **Cadencia variable**: `Wait` proporcional al largo del mensaje (más realista que fijo).
- **Typos simulados**: descartado por ahora — riesgo de verse descuidado en contexto comercial.
- **Indicador de "escribiendo…"** donde el canal lo permita.
- Medir si la estética mueve métricas reales (tasa de respuesta / conversión), no solo percepción.

---

## Registro

| Fecha | Cambio | Validado en |
|-------|--------|-------------|
| 2026-07-24 | Versión inicial: 3 capas, una-línea-una-burbuja, bloques protegidos | HPF (gpt-4.1, WhatsApp/Telegram) |
