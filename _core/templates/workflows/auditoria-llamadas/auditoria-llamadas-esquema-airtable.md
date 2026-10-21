# Airtable — Schema de la base de datos Call Audit

## Base: "Auditoría de Llamadas"

### Tabla: Llamadas

| Campo | Tipo Airtable | Fuente JSON |
|---|---|---|
| Closer | Single line text | `closer_name` |
| Fecha | Date | `call_date` |
| Resultado | Single select | `call_outcome` |
| Duración (min) | Number (integer) | `duration_minutes` |
| Score Total | Number (integer) | `score_total` |
| Resumen Ejecutivo | Long text | `resumen_ejecutivo` |
| Fortalezas | Long text | `fortalezas` (join con `\n`) |
| Oportunidades de Mejora | Long text | `oportunidades_mejora` (formatear como texto) |
| Objeciones Detectadas | Long text | `objeciones_detectadas` (formatear como texto) |
| Próximas Acciones | Long text | `proximas_acciones` (join con `\n`) |
| Score Rapport | Number (integer) | `metricas_universales.rapport_control_conversacion.score` |
| Score Discovery | Number (integer) | `metricas_universales.calidad_discovery.score` |
| Score Gap/Problema | Number (integer) | `metricas_universales.claridad_problema_y_gap.score` |
| Score Presentación | Number (integer) | `metricas_universales.presentacion_solucion.score` |
| Score Objeciones | Number (integer) | `metricas_universales.manejo_objeciones.score` |
| Score Estructura | Number (integer) | `metricas_universales.seguimiento_estructura.score` |
| Score Cierre | Number (integer) | `metricas_universales.cierre_y_cta.score` |
| Score Mecanismo | Number (integer) | `metricas_especificas.menciona_mecanismo.score` |
| Score Conexión Oferta | Number (integer) | `metricas_especificas.conecta_oferta_con_lead.score` |
| Score Casos Éxito | Number (integer) | `metricas_especificas.usa_casos_de_exito.score` |
| Score Precio | Number (integer) | `metricas_especificas.explica_precio_y_condiciones.score` |
| Score Calificación | Number (integer) | `metricas_especificas.calificacion_del_prospecto.score` |
| Modelo IA | Single line text | `modelo_usado` |
| Procesado En (seg) | Number (decimal) | `procesado_en_segundos` |

### Single select: campo "Resultado"

Opciones a crear en Airtable:
- `cerrado`
- `no_cerrado`
- `pendiente`
- `no_calificado`

---

## Mapeo en n8n (nodo Airtable)

En el nodo Airtable de n8n, usar expresiones para acceder a los campos anidados del JSON devuelto por el endpoint Modal. Ejemplo de mapeo:

```
Score Total         → {{ $json.score_total }}
Score Rapport       → {{ $json.metricas_universales.rapport_control_conversacion.score }}
Score Discovery     → {{ $json.metricas_universales.calidad_discovery.score }}
Fortalezas          → {{ $json.fortalezas.join('\n') }}
Resumen Ejecutivo   → {{ $json.resumen_ejecutivo }}
```

Para los campos de tipo array de objetos (oportunidades_mejora, objeciones_detectadas), formatearlos en n8n con un Code node antes de escribir en Airtable:

```javascript
// Formatear oportunidades de mejora
const oportunidades = $json.oportunidades_mejora.map((o, i) =>
  `${i+1}. ${o.punto}\nEjemplo: ${o.ejemplo_concreto}\nCómo mejorar: ${o.como_mejorarlo}`
).join('\n\n');

// Formatear objeciones
const objeciones = $json.objeciones_detectadas.map(o =>
  `• "${o.objecion}" → ${o.calidad_resolucion}: ${o.como_la_manejo}`
).join('\n');

return { ...($json), oportunidades_formateadas: oportunidades, objeciones_formateadas: objeciones };
```

---

## Vistas recomendadas

1. **Por Closer** — Agrupado por campo "Closer", ordenado por Fecha descendente
2. **Dashboard Semanal** — Filtrado por Fecha (última semana), mostrar Score Total + sub-scores
3. **Llamadas con bajo desempeño** — Filtrado por Score Total < 70, ordenado por score ascendente
4. **Ranking de closers** — Vista Gallery o Summary con promedio de Score Total por closer

---

## Fórmulas útiles en Airtable

**Score promedio del closer** (campo fórmula en una tabla separada "Closers"):
```
AVG({Score Total})
```

**Semáforo de performance** (campo fórmula):
```
IF({Score Total} >= 80, "🟢 Alto", IF({Score Total} >= 60, "🟡 Medio", "🔴 Bajo"))
```
