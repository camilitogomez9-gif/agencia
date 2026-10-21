# Métricas de Inasistencias — Sonrisas

> Definiciones acordadas con el cliente para los tres KPIs implementados en el flujo n8n "Sonrisas | Registro Inasistencias" (sección métricas, rama manual).

---

## Fuente de Datos

**Archivo CSV:** `agenda_citas_estados_mes_*.csv` (descargado de Dentalink por Cecilia cada sábado)

**Estructura clave:** Cada fila es **un cambio de estado** de una cita. La misma cita puede tener N filas (una por cada estado por el que pasó). Se agrupan por `# Cita` para rastrear el recorrido completo.

---

## Estados Relevantes del CSV

| Estado | Categoría |
|--------|-----------|
| `Notif. automática vía WhatsApp` | Notificado WA ✉️ |
| `Confirmado por pcte. vía WhatsApp` | Confirmado ✅ |
| `Confirmado por teléfono` | Confirmado ✅ |
| `Confirmado por Whatsapp` | Confirmado ✅ |
| `No asistió` | No-show ❌ |
| `Atendido` | Llegó al día ✅ |
| `Atendiéndose` | Llegó al día ✅ |
| `En sala de espera` | Llegó al día ✅ |

---

## Métrica 1 — Índice de Inasistencias

**Pregunta que responde:** De los pacientes que tenían turno el día previsto, ¿qué porcentaje no asistió?

**Denominador:** Citas que *llegaron al día* = tuvieron al menos un estado en `{Atendido, Atendiéndose, En sala de espera, No asistió}`
*(Excluye citas canceladas/anuladas antes del día del turno)*

**Numerador:** Citas con `llegoAlDia = true` Y `Estado = "No asistió"`

**Fórmula:**
```
Índice = (citas "No asistió" que llegaron al día) / (total citas que llegaron al día) × 100
```

**Benchmark Feb 2026:** 530 / 9.605 ≈ **5.5%**

---

## Métrica 2 — % No Asistió sobre Confirmadas

**Pregunta que responde:** De los pacientes que confirmaron su turno, ¿qué porcentaje igual no asistió?

**Denominador:** Citas con al menos una fila de estado `Confirmado por pcte. vía WhatsApp`, `Confirmado por teléfono` o `Confirmado por Whatsapp`

**Numerador:** Citas confirmadas que también tienen `Estado = "No asistió"`

**Fórmula:**
```
% = (citas confirmadas + "No asistió") / (total citas confirmadas) × 100
```

**Campo en la tabla de pacientes:** `Confirmo y No Asistio`

---

## Métrica 3 — % No Asistió sobre Notificados WA

**Pregunta que responde:** De los pacientes que recibieron la notificación automática por WhatsApp, ¿qué porcentaje no asistió?

**Denominador:** Citas con estado `Notif. automática vía WhatsApp`
*(Se excluye `Notif. WhatsApp fallida` porque la notificación no llegó al paciente)*

**Numerador:** Citas notificadas por WA que también tienen `Estado = "No asistió"`

**Fórmula:**
```
% = (citas notificadas WA + "No asistió") / (total citas notificadas WA) × 100
```

**Campo en la tabla de pacientes:** `Notif WA y No Asistio`

---

## Condicionante de Identidad del Paciente

El campo `# Paciente` del CSV es el identificador único y estable que permite:
- Agrupar todas las citas del mismo paciente
- Contar cuántas veces un paciente no asistió en el período
- Diferenciar por tipo (confirmó, fue notificado WA, ambas, ninguna)

---

## Output del Flujo n8n

### Hoja "Resumen" (nueva)

| Concepto | Valor |
|----------|-------|
| Período | Febrero 2026 |
| Última actualización | 08/03/2026 14:30 |
| ── ÍNDICE GENERAL ── | |
| Total citas (llegaron al día) | 9.605 |
| Total no asistieron | 530 |
| **Índice de inasistencias** | **5.5%** |
| ── SOBRE CONFIRMADAS ── | |
| Total citas confirmadas | X |
| Confirmadas que no asistieron | X |
| **% No asistió / Confirmadas** | **X.X%** |
| ── SOBRE NOTIFICADOS WA ── | |
| Total notificados por WA | 3.710 |
| Notificados WA que no asistieron | X |
| **% No asistió / Notificados WA** | **X.X%** |

### Hoja "Inasistencias" (ampliada)

| ID | Nombre | Inasistencias | Fecha Ultima Inasistencia | Confirmo y No Asistio | Notif WA y No Asistio |
|----|--------|--------------|--------------------------|----------------------|----------------------|
| ... | ... | 2 | 2026-02-15 | 1 | 2 |

---

## Mantenimiento

- **Frecuencia:** Semanal (sábado, después de que Cecilia importa el CSV)
- **Activación:** Trigger manual en n8n → "Trigger Manual (Métricas)"
- **Ajuste de nombres de columna:** Si el CSV importado usa nombres de columna distintos a los del CSV original (ej. `Numero Cita` en lugar de `# Cita`), editar las líneas `String(d['# Cita'] || d['Numero Cita'] || '')` en el Code node "Calcular Metricas"
