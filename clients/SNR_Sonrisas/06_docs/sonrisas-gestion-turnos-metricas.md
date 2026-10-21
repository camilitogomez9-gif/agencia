# Sonrisas — Informe semanal de gestión de turnos (por sucursal)

> Workflow: `03_workflows/sonrisas-gestion-turnos-semanal-v1.json`
> Creado: 2026-05-25 · Para: Cecilia (administración)

---

## Qué hace

Cada **sábado a las 18:00 (America/Montevideo)** —después del cierre de la clínica (17 h)— el flujo:
1. Calcula la semana recién cerrada (**Lunes → Sábado**).
2. Consulta la **API de Dentalink** (`/citas` con paginación + `/sucursales`).
3. Cuenta las citas de esa semana **por sucursal**, según el **estado actual** de cada cita.
4. Escribe/actualiza una fila por semana en una **pestaña por sucursal** del Google Sheets.

También se puede correr a mano con el **Trigger Manual** (reporta la última semana cerrada).

---

## Métricas (sobre el estado ACTUAL de la cita)

| Columna | Definición |
|---|---|
| `Agendadas` | nº de citas cuyo `id_estado ∈ {7, 28, 8, 19, 14, 2}` |
| `Atendidos` | nº de citas con `id_estado == 2` (Atendido) |
| `No asistió` | nº de citas con `id_estado == 8` |
| `% Atendidos` | `Atendidos / Agendadas × 100` (1 decimal; 0 si Agendadas = 0) |
| `% Inasistencia` | `No asistió / Agendadas × 100` (1 decimal; 0 si Agendadas = 0) |

Mapeo de estados Dentalink usados:
`7 No confirmado` · `28 Confirmado por pcte. vía WhatsApp` · `8 No asistió` · `19 Anulado por pcte. vía WhatsApp` · `14 Cambio de fecha` · `2 Atendido`.

> El **universo "Agendadas" incluye Atendido (2)**, por eso `Atendidos ⊆ Agendadas` y `% Atendidos ∈ [0,100]`.
> Se cuentan **citas** (no pacientes únicos). La fecha de referencia es la `fecha` de la cita dentro de [Lunes..Sábado].

---

## Límite importante (por qué NO hay "% sobre confirmadas / notificados WA")

La API de Dentalink expone **solo el estado ACTUAL** de cada cita: no hay endpoint de historial de estados. Una cita que se confirmó y luego no asistió hoy figura como "No asistió", no como "confirmada". Por eso **no es posible** reconstruir desde la API métricas de ciclo de vida como "% de las confirmadas que no asistieron" o "% de las notificadas por WhatsApp que no asistieron".

Esas métricas (las del documento `sonrisas-metricas-inasistencias.md`) solo se pueden calcular con el **CSV de cambios de estado** que se baja manualmente (1 fila por transición). Quedan fuera de este flujo por decisión acordada (vía API-pura).

---

## Arquitectura (node-by-node)

1. **Trigger Semanal (Sábado 18h)** / **Trigger Manual** → ambos entran a `Calcular semana`.
2. **Calcular semana** (Code): con Luxon en `America/Montevideo` calcula el sábado más reciente, el lunes de esa semana, el rango ISO y la etiqueta `semanaISO` (ej. `2026-W21`).
3. **Obtener citas + sucursales (paginado)** (Code): usa `this.helpers.httpRequest` y **sigue `links.next`** hasta agotar páginas (no trunca en 50). Trae todas las citas del rango y la lista de sucursales.
4. **Agregar por sucursal** (Code): agrupa por `id_sucursal`, cuenta por estado, calcula porcentajes. Emite **una fila por sucursal** (con ceros si no tuvo citas, para que la serie sea continua).
5. **Escribir métricas por sucursal** (Google Sheets `appendOrUpdate`): `sheetName` dinámico = nombre de la sucursal; **match por `Semana`** (upsert: re-correr la misma semana actualiza, no duplica).
6. **Error Trigger → Mensaje de error** (Telegram): avisa al equipo si el flujo falla.

---

## Setup (antes del primer uso)

1. **Crear el Google Sheet** y pegar su **ID** en el nodo `Escribir métricas por sucursal` → `documentId` (hoy: `PEGAR_ID_DEL_NUEVO_GOOGLE_SHEET`).
2. **Crear una pestaña por sucursal**, con el **nombre EXACTO** al de Dentalink, y esta fila de encabezados (fila 1):

   ```
   Semana | Desde | Hasta | Sucursal | Agendadas | Atendidos | No asistió | % Atendidos | % Inasistencia | Actualizado
   ```

   > Tip para conocer los nombres: corré una vez el **Trigger Manual** y mirá la salida del nodo `Agregar por sucursal` (campo `Sucursal`). Copiá esos nombres tal cual a las pestañas.
3. **Settings del workflow → Error Workflow** = este mismo workflow (o el global), para que dispare el aviso de Telegram ante fallos.
4. (Opcional recomendado) Migrar el **token de Dentalink** —hoy hardcodeado en el nodo de fetch, igual que en los otros flujos— a una credencial n8n Header Auth.
5. Activar el workflow (`active`) una vez configurado.

---

## Verificación

1. **Cuadre manual:** correr el Trigger Manual sobre una semana cerrada y comparar `Agendadas / Atendidos / No asistió` por sucursal contra un export manual de Dentalink del mismo rango.
2. **Paginación:** en una semana de alto volumen, confirmar que el total de citas procesadas coincide con Dentalink (que no se corte en 50).
3. **Sanidad:** `Atendidos ≤ Agendadas`, `No asistió ≤ Agendadas`, `% ∈ [0,100]`.
4. **Idempotencia:** re-ejecutar la misma semana → la fila se actualiza (sin duplicar).

---

## Notas / supuestos

- Citas que el sábado 18 h sigan en estados no-terminales (`5 En sala`, `6 Atendiéndose`) quedan fuera del universo `{7,28,8,19,14,2}`; por eso el flujo corre tras el cierre.
- Las sucursales se traen dinámicamente de `/sucursales` (no hardcodeadas).
- Credenciales reutilizadas: Google Sheets OAuth `Google Sheets | Heber Vera DEF.`, Telegram `botla agencia` (chat del equipo).
