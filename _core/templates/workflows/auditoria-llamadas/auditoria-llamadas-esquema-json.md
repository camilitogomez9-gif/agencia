# Call Audit — JSON Schema de Output

Ejemplo de response completo del endpoint `/analyze_call`.

## Estructura completa

```json
{
  "closer_name": "Juan García",
  "call_date": "2026-02-18",
  "call_outcome": "pendiente",
  "duration_minutes": 45,
  "score_total": 74,
  "metricas_universales": {
    "rapport_control_conversacion": {
      "score": 8,
      "justificacion": "Buen inicio, tono cálido. El closer mantuvo el control de la agenda sin presionar."
    },
    "calidad_discovery": {
      "score": 7,
      "justificacion": "Exploró el dolor principal y la urgencia, pero no profundizó en intentos anteriores de solución."
    },
    "claridad_problema_y_gap": {
      "score": 8,
      "justificacion": "Articuló claramente que el prospecto pierde $20k/mes por baja conversión de su equipo de ventas."
    },
    "presentacion_solucion": {
      "score": 7,
      "justificacion": "Conectó la solución con el caso, aunque fue breve. Podría haber usado más detalle sobre el mecanismo."
    },
    "manejo_objeciones": {
      "score": 6,
      "justificacion": "La objeción 'necesito consultarlo' fue manejada pero sin explorar qué necesitaba el socio saber."
    },
    "seguimiento_estructura": {
      "score": 7,
      "justificacion": "Siguió el flujo general. Se saltó la etapa de visión antes de presentar la oferta."
    },
    "cierre_y_cta": {
      "score": 8,
      "justificacion": "CTA claro: llamada con el socio el viernes. Comprometió al prospecto con fecha concreta."
    }
  },
  "metricas_especificas": {
    "menciona_mecanismo": {
      "score": 5,
      "justificacion": "Mencionó la auditoría automática pero no explicó el mecanismo diferencial vs. otras soluciones."
    },
    "conecta_oferta_con_lead": {
      "score": 8,
      "justificacion": "Conectó directamente con el problema de los $20k mensuales perdidos."
    },
    "usa_casos_de_exito": {
      "score": 4,
      "justificacion": "No usó ningún caso de éxito o testimonio durante la llamada."
    },
    "explica_precio_y_condiciones": {
      "score": 7,
      "justificacion": "Presentó el precio después de establecer el ROI. Tono seguro, sin disculparse."
    },
    "calificacion_del_prospecto": {
      "score": 6,
      "justificacion": "Identificó el problema pero no preguntó explícitamente por presupuesto ni autoridad de decisión."
    }
  },
  "resumen_ejecutivo": "Llamada con buen nivel de rapport y discovery sólido que identificó un dolor claro ($20k/mes en oportunidades perdidas). El closer conectó bien la solución con el caso pero falló en demostrar el mecanismo diferencial y no usó casos de éxito. La objeción de consultar al socio fue manejada funcionalmente pero quedó oportunidad de explorar más. CTA concreto al final.",
  "fortalezas": [
    "Excelente articulación del ROI: conectó el precio directamente con el costo del problema actual",
    "Control de la conversación y agenda desde el inicio sin generar presión",
    "CTA concreto con fecha acordada para el siguiente paso"
  ],
  "oportunidades_mejora": [
    {
      "punto": "No explicó el mecanismo diferencial",
      "ejemplo_concreto": "Cuando presentó la solución solo dijo 'auditamos cada llamada automáticamente' sin explicar cómo funciona ni por qué es diferente a una capacitación tradicional.",
      "como_mejorarlo": "Agregar 2-3 oraciones sobre el mecanismo: 'Lo que hacemos diferente es X, que logra Y resultado en Z tiempo, a diferencia de [alternativa genérica].'"
    },
    {
      "punto": "Omitió casos de éxito",
      "ejemplo_concreto": "No mencionó ningún cliente con situación similar ni resultado concreto antes de presentar el precio.",
      "como_mejorarlo": "Antes de presentar el precio, incluir: 'Un cliente similar, en el mismo sector, pasó de X% a Y% de conversión en 60 días usando esto.'"
    },
    {
      "punto": "Manejo superficial de la objeción 'necesito consultarlo'",
      "ejemplo_concreto": "Aceptó la objeción rápidamente sin explorar qué necesitaba saber el socio o si había otra preocupación detrás.",
      "como_mejorarlo": "Responder con: '¿Qué información necesitaría tu socio para poder tomar la decisión? Así me aseguro de que tengas todo lo que necesita.'"
    }
  ],
  "objeciones_detectadas": [
    {
      "objecion": "Necesito consultarlo con mi socio",
      "como_la_manejo": "Aceptó y propuso llamada con el socio el viernes",
      "calidad_resolucion": "buena",
      "cita_textual": "Prospecto: Necesito consultarlo con mi socio. Closer: Totalmente entendible."
    }
  ],
  "proximas_acciones": [
    "Preparar 2-3 casos de éxito específicos para el sector del prospecto antes de la llamada del viernes",
    "Practicar la explicación del mecanismo diferencial en 30 segundos",
    "Preparar respuestas para las posibles objeciones del socio (precio, ROI, implementación)"
  ],
  "modelo_usado": "gpt-4o-mini",
  "procesado_en_segundos": 8.3
}
```

## Valores posibles para campos enum

### `call_outcome`
- `cerrado` — El prospecto compró
- `no_cerrado` — No avanzó
- `pendiente` — Siguiente paso agendado
- `no_calificado` — El lead no era fit

### `calidad_resolucion` (dentro de `objeciones_detectadas`)
- `excelente` — Convirtió la objeción en razón para avanzar
- `buena` — Respondió correctamente
- `regular` — Respondió pero de forma genérica
- `mala` — No manejó bien la objeción
- `no_manejada` — Ignoró la objeción

## Notas de implementación para n8n → Airtable

Al mapear desde n8n a Airtable, los campos anidados se acceden con notación de punto:
- `metricas_universales.rapport_control_conversacion.score` → Score Rapport
- `metricas_universales.calidad_discovery.score` → Score Discovery
- `fortalezas` es un array — joinear con `\n` para Airtable Long text
- `oportunidades_mejora` es un array de objetos — formatear como texto antes de guardar
