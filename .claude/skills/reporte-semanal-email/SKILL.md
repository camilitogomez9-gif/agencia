---
name: reporte-semanal-email
description: >
  Usar este skill cuando el usuario quiera crear un workflow n8n de reporte periódico
  (semanal, mensual) que analice datos y los envíe por email. Se activa con frases como
  "crear reporte semanal", "armar un workflow que mande métricas por email", "quiero que
  el agente mande un resumen de sus conversaciones", "hacer un dashboard por correo",
  "análisis semanal automático", o cuando el cliente quiera un email periódico con KPIs.
  Produce el JSON del workflow n8n listo para importar, con el HTML del email incluido.
---

# Skill: Reporte Semanal por Email

## Descripción

Guía la construcción de un workflow n8n que extrae datos de una fuente (PostgreSQL,
Airtable, Google Sheets, etc.), los analiza con un LLM, y envía un reporte HTML estético
por email de forma periódica.

**Referencia de producción:** `clients/CLT008_Narvaja/03_workflows/narvaja-resumen-semanal-v3.json`

---

## Principios Fundamentales (Aprendidos en Producción)

Antes de cualquier implementación, internalizar estas reglas. Son el resultado de haber
corregido errores reales que produjeron resultados 3x diferentes en ejecuciones consecutivas.

### Regla #1 — Lo que se puede contar con código, NO se delega al LLM

El LLM es notoriamente malo contando items en textos largos. Cuando el input supera ~5K tokens,
los conteos empiezan a alucinar. En producción se observó:

- Ejecución 1: `conversaciones_total = 100`
- Ejecución 2: `conversaciones_total = 292`
- Ejecución 3: `conversaciones_total = 194`

Con los **mismos datos fuente** y `temperature = 1.0` (default de n8n).

**Regla:** Toda métrica cuantitativa que se pueda calcular con JavaScript (conteos,
sumas, porcentajes, rankings) **debe calcularse en un nodo Code** antes de pasársela al LLM.
El LLM recibe esos valores pre-calculados y los devuelve tal cual ("passthrough").

### Regla #2 — Temperature=0 + seed para el nodo LLM

El nodo OpenAI en n8n tiene `temperature=1.0` por defecto. Para reportes que deben ser
consistentes entre ejecuciones:

```json
"options": {
  "temperature": 0,
  "seed": 42
}
```

Esto no elimina la variabilidad completamente (el modelo puede cambiar), pero la minimiza
y hace el comportamiento debuggeable.

### Regla #3 — Listas cerradas para categorías y motivos

Si el LLM puede inventar categorías libremente, la misma conversación se clasifica de
forma diferente en cada ejecución. En el prompt, siempre proveer:

- Lista exacta de categorías permitidas (con los nombres exactos que deben aparecer en el JSON)
- Regla de clasificación unívoca (ej: "una conversación → un motivo dominante")
- Validación numérica (ej: "suma de motivo_X_count ≤ total")

### Regla #4 — Eventos binarios con marcadores duros, no criterios subjetivos

Para detectar si algo ocurrió (ej: "¿fue escalada esta conversación?"), usar regex sobre
campos concretos en lugar de pedirle al LLM que "evalúe si el cliente estaba molesto".

Ejemplo producción (detección de escalamiento en mensajes del agente):
```javascript
const escalamientoRegex = /elevar_conversacion|post_venta/i;
const fueEscalada = messages.some(m =>
  m.type === 'ai' && escalamientoRegex.test(m.content || '')
);
```

Si las tool calls no están en el `content` del mensaje, ampliar el regex con frases
literales que el agente usa al escalar (ej: `"quedamos a las órdenes"`).

### Regla #5 — Prompt con PASOS secuenciales, no lista de métricas

En lugar de darle al LLM una lista de campos a completar, darle un proceso ordenado:

```
## PASO 1 — Calcular X
[instrucciones específicas]

## PASO 2 — Clasificar Y
Lista cerrada: "Opción A", "Opción B", "Opción C"
[reglas de clasificación]

## PASO 3 — Inferir Z
[instrucciones + restricciones]
```

Esto produce outputs más consistentes que "completa estos 26 campos".

---

## Arquitectura Canónica del Workflow

```
Schedule Trigger
      ↓
Execute Query (SQL / Airtable / Sheets)
      ↓
Code in JavaScript          ← calcula métricas cuantitativas + prepara texto concatenado
      ↓
OpenAI (temperature=0, seed=42, JSON schema)    ← solo análisis cualitativo
      ↓
Send a message (Gmail)      ← HTML estético con variables interpoladas
      ↓
[Error handler opcional]
```

### Nodos alternativos

| Necesidad | Nodo recomendado |
|-----------|-----------------|
| Datos en PostgreSQL | `Execute a SQL query` |
| Datos en Airtable | `Airtable: Search Records` |
| Datos en Google Sheets | `Google Sheets: Get Rows` |
| Email por Gmail | `Gmail: Send a message` |
| Email por SMTP | `Send Email` |
| Notificación adicional | `Telegram: Send Message` (bcc operativo) |

---

## Paso a Paso de Implementación

### Paso 1 — Levantar Requerimientos

Antes de empezar a construir, clarificar con el usuario:

1. **Fuente de datos:** ¿PostgreSQL (tabla y query)? ¿Airtable (base + tabla)? ¿Google Sheets?
2. **Período:** ¿Últimos 7 días? ¿Mes en curso? ¿Semana anterior (lunes a domingo)?
3. **Métricas cuantitativas:** ¿Qué números hay que contar/sumar? (son para el nodo JS)
4. **Métricas cualitativas:** ¿Qué requiere interpretación semántica? (son para el LLM)
5. **Categorías/clasificaciones:** ¿Hay listas cerradas o se definen ahora?
6. **Eventos binarios:** ¿Hay algo que "ocurrió o no" y hay un marcador concreto?
7. **Destinatarios:** ¿A quién va el email? ¿Hay BCC?
8. **Horario:** ¿Qué día y hora se envía? ¿Qué timezone?
9. **Branding:** ¿Tiene logo? ¿Colores de la marca? ¿Tema (duolingo/corporate/minimal/warm)?

### Paso 2 — Diseñar el Nodo JavaScript

El nodo Code es el corazón del workflow. Su responsabilidad:

**A. Agrupar y preparar los datos**

```javascript
const items = $input.all();

// Agrupar por entidad (session_id, lead_id, usuario_id, etc.)
const groups = {};
for (const item of items) {
  const { group_key, ...rest } = item.json;
  if (!groups[group_key]) groups[group_key] = [];
  groups[group_key].push(rest);
}

// Ordenar cada grupo por timestamp ASC
for (const key in groups) {
  groups[key].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
}
```

**B. Calcular métricas cuantitativas (deterministas)**

```javascript
// Total de entidades
const total = Object.keys(groups).length;

// Conteo de eventos binarios (con regex o condición exacta)
const REGEX_EVENTO = /nombre_de_tool|frase_literal/i;
let eventoCount = 0;
for (const key in groups) {
  if (groups[key].some(item => REGEX_EVENTO.test(item.content || ''))) {
    eventoCount++;
  }
}

// Porcentaje
const pct = total > 0
  ? `${Math.round((eventoCount / total) * 100)}%`
  : '0%';
```

**C. Generar texto concatenado para el LLM**

```javascript
let texto = '';
for (const key of Object.keys(groups)) {
  texto += `===========================\nGRUPO: ${key}\n===========================\n\n`;
  texto += groups[key].map(item =>
    `[${item.type?.toUpperCase() || 'ITEM'}] ${item.content || ''}`
  ).join('\n');
  texto += '\n\n\n';
}

return [{
  json: {
    texto_analisis: texto.trim(),
    total,                    // ← passthrough al LLM
    evento_count: eventoCount, // ← passthrough al LLM
    evento_pct: pct           // ← passthrough al LLM
  }
}];
```

### Paso 3 — Diseñar el Prompt del LLM

Estructura recomendada:

```
# ROL
[Descripción del analista que Claude debe encarnar]

# TAREA
[Qué debe hacer + referencia al formato de entrada]

## FORMATO DE ENTRADA
[Descripción del texto concatenado que recibirá]

# DATOS PRE-CALCULADOS (NO RECALCULAR)

Los siguientes valores fueron calculados determinísticamente en JavaScript.
Devolvelos EXACTAMENTE tal como los recibes en el JSON de salida.

- total = {{ $json.total }}
- evento_count = {{ $json.evento_count }}
- evento_pct = "{{ $json.evento_pct }}"

REGLA CRÍTICA: No intentes recontar. Estas son la fuente de verdad.

# MÉTRICAS A INFERIR (ejecutar en orden)

## PASO 1 — [Primera métrica cualitativa]
[instrucciones específicas]

## PASO 2 — Clasificación [tipo]
Lista cerrada (USAR EXACTAMENTE ESTOS NOMBRES):
- "Categoría A"
- "Categoría B"
- "Categoría C"

[reglas de clasificación]

## PASO 3 — [Insights / Recomendaciones]
[instrucciones + restricciones]

# REGLAS GENERALES
- Español neutro y profesional.
- Si no hay datos suficientes: "Sin datos suficientes" (string) o 0 (integer).
- NUNCA inventar categorías fuera de las listas cerradas.
```

### Paso 4 — Diseñar el JSON Schema

Siempre usar `json_schema` en el nodo OpenAI para forzar el formato:

```json
{
  "type": "object",
  "properties": {
    "total": { "type": "integer" },
    "categoria_1": { "type": "string" },
    "categoria_2": { "type": "string" },
    "insight_1": { "type": "string" },
    "insight_2": { "type": "string" },
    "recomendacion_1": { "type": "string" }
  },
  "additionalProperties": false,
  "required": ["total", "categoria_1", "categoria_2", "insight_1", "insight_2", "recomendacion_1"]
}
```

**Reglas del schema:**
- Incluir los campos de passthrough (total, evento_count, etc.) con su tipo correcto
- `"additionalProperties": false` siempre — evita que el LLM invente campos
- Todos los campos en `required` — evita que el LLM omita campos opcionales
- Usar `"type": "integer"` para conteos, `"type": "string"` para texto y porcentajes

### Paso 5 — Generar el HTML del Email

Usar el comando `/email-html-generator` del workspace:

1. Definir la estructura del JSON (todos los campos del schema)
2. Invocar `/email-html-generator` con el JSON de ejemplo y el tema deseado
3. Pegar el HTML generado en el nodo Gmail
4. Ajustar las variables de interpolación n8n a la ruta correcta:
   - **OpenAI en n8n:** `{{ $json.output[0].content[0].text.CAMPO }}`
   - **Otros nodos:** `{{ $json.CAMPO }}`

**Reglas email-safe** (no relajar estas reglas):
- Todo CSS inline — sin `<style>` tags
- Layout con `<table>` — sin `<div>` estructurales
- `max-width: 600px` en el contenedor principal
- Colores en HEX
- Fallback fonts: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif`
- DOCTYPE + `<meta viewport>` presentes
- Sin JS, sin web fonts críticos, sin flexbox/grid

### Paso 6 — Configurar el Schedule Trigger

```json
{
  "rule": {
    "interval": [{ "field": "cronExpression" }]
  },
  "cronExpression": "0 9 * * 1"  // Lunes a las 9:00 AM
}
```

Timezones comunes:
- Uruguay / Argentina: `America/Montevideo` / `America/Argentina/Buenos_Aires`
- México: `America/Mexico_City`
- España: `Europe/Madrid`

### Paso 7 — Nodo de Error

Siempre agregar un Error Trigger conectado a una notificación (Telegram o email):

```
Error Trigger → Telegram: Send Message → "❌ Reporte fallido: {{ $json.error.message }}"
```

---

## Checklist de Validación Pre-Deploy

### Workflow

- [ ] Schedule Trigger configurado con timezone correcta
- [ ] Query SQL/Airtable filtra por el período correcto (últimos N días)
- [ ] Nodo JS calcula todas las métricas cuantitativas (ningún número delegado al LLM)
- [ ] `temperature: 0` y `seed: 42` en el nodo OpenAI
- [ ] JSON Schema con `additionalProperties: false` y todos los campos en `required`
- [ ] Prompt tiene sección "DATOS PRE-CALCULADOS" con regla de passthrough
- [ ] Prompt usa listas cerradas para todas las categorías/clasificaciones
- [ ] HTML tiene CSS inline en todos los elementos
- [ ] Variables n8n en el HTML apuntan a la ruta correcta del output del LLM
- [ ] Nodo de error configurado

### Email

- [ ] Probar en Gmail desktop: ¿renderiza correctamente?
- [ ] Probar en Gmail mobile: ¿el responsive funciona?
- [ ] Todos los campos del JSON aparecen en el email (ninguno vacío)
- [ ] Asunto del email claro y con emoji identificador

### Determinismo

- [ ] Ejecutar el workflow 3 veces consecutivas con los mismos datos
- [ ] Verificar que las métricas cuantitativas son **idénticas** en las 3 ejecuciones
- [ ] Verificar que las categorías/motivos tienen variación ≤ 1 posición entre ejecuciones

---

## Anti-patrones (Nunca Hacer)

| Anti-patrón | Por qué falla | Solución |
|-------------|---------------|----------|
| Pedirle al LLM que cuente items en texto largo | Alucina los conteos → resultados 3x diferentes | Contar en JavaScript |
| `temperature = 1.0` (default n8n) | Máxima aleatoriedad → inconsistencia | Siempre `temperature: 0` |
| Categorías abiertas en el prompt | Misma cosa clasificada distinto en cada run | Listas cerradas en el prompt |
| Detectar eventos con criterios subjetivos | "cliente molesto" varía según el run | Regex sobre texto literal o tool calls |
| LLM calcula porcentajes | Numerador + denominador pueden divergir del passthrough | Calcular en JS, LLM devuelve el string tal cual |
| Schema sin `additionalProperties: false` | LLM puede agregar campos extra o inventar nombres | Siempre cerrar el schema |
| Sin nodo de error | Un fallo silencioso = reporte no enviado y nadie se entera | Siempre Error Trigger + notificación |

---

## Output Esperado del Skill

Al finalizar, entregar:

1. **JSON del workflow n8n** listo para importar, guardado en:
   `clients/[CLTXXX]/03_workflows/[cliente]-reporte-[periodo]-v1.json`

2. **Resumen de las métricas implementadas:**
   - Métricas cuantitativas (calculadas en JS): [lista]
   - Métricas cualitativas (inferidas por LLM): [lista]
   - Listas cerradas usadas: [lista con sus valores]
   - Regex de eventos binarios: [lista]

3. **Instrucciones de testing:**
   - Cómo ejecutar el Test de Determinismo (3 ejecuciones consecutivas)
   - Qué verificar en el email resultante
   - Cómo interpretar los resultados del primer run real

4. **Próximos pasos para el cliente:**
   - Confirmar timezone y horario de envío
   - Validar destinatarios (to + bcc)
   - Aprobar el diseño del email antes de activar en producción
