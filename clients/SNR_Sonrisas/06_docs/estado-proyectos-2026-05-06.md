# Sonrisas — Estado de Proyectos
*Actualizado: 6 de mayo 2026 · Reunión de alineamiento*

---

## Semáforo

| Símbolo | Significado |
|---------|-------------|
| 🟢 | En producción / Completado |
| 🟡 | En pausa / Bloqueado externamente |
| 🔴 | Pendiente de implementación |
| 🔵 | Backlog / Proyecto futuro |

---

## 1. Reportes de facturación

### 1.1 Reporte general
🟢 **En producción**

El workflow principal de facturación está activo en n8n. Procesa los datos de Dentalink y genera el reporte general acumulado semana a semana.

**Cadencia:** Sábado noche → trigger manual (Cecilia) → reporte actualizado

---

### 1.2 Reporte por sucursal
🔴 **Pendiente**

Se necesita un reporte individual por sucursal que mida el desempeño contra las metas, con métricas de no confirmados y atendidos por semana. El objetivo es que Cecilia pueda generar los PDFs el domingo y enviarlos a las sucursales el lunes a las 9 AM.

**Métricas nuevas a incluir:**
- No confirmados por semana
- Atendidos por semana
- Cantidad de pacientes
- Promedio atendido por paciente

**Responsable:** la agencia

---

## 2. Correos para socios

### 2.1 Correo diario con métodos de pago
🟢 **En producción**

El correo diario con el detalle de métodos de pago está activo y enviándose automáticamente.

---

### 2.2 Correo semanal — Categoría + Ortodoncia
🔴 **Pendiente**

Correo automático semanal para los socios con resumen de rendimiento por categoría y ortodoncia.

**Formato:** Tabla simple con Ajustes, Cantidad, Importe, Combo, Retiro por clínica + suma total. Sin métodos de pago.
**Filas del Excel:** Fila 23 (General) · Fila 25 (Ortodoncia)

**Responsable:** la agencia

---

### 2.3 Correo mensual — Categoría + Ortodoncia
🔴 **Pendiente**

Correo automático mensual para los socios con resumen de rendimiento por categoría y ortodoncia.

**Formato:** Igual al semanal.
**Filas del Excel:** Fila 5 (General) · Fila 6 (Ortodoncia)

**Responsable:** la agencia

---

### 2.4 Envío retroactivo — Mes de abril
🔴 **Pendiente urgente**

Enviar manualmente el informe mensual de abril a los socios mientras se implementa el correo automático.

**Responsable:** la agencia
**Próximo paso:** Enviar en los próximos días.

---

## 3. Informe no confirmados / atendidos
🔴 **Pendiente**

Nuevo informe con métricas de no confirmados vs. atendidos para el seguimiento de la gestión de turnos. Incluye porcentajes de inasistencia sobre confirmadas y sobre notificados por WhatsApp.

**Responsable:** la agencia

---

## 4. Informe de eficiencia de doctores
🟡 **En pausa — Datos defectuosos en Dentalink**

El informe está pausado porque los datos de Dentalink no son confiables para este cálculo.

**Problemas identificados:**
- Agendas retroactivas: inflando las horas disponibles
- Tiempo bloqueado (ausencias) se cuenta como disponible

**Nuevo proceso acordado:**
- Frecuencia: **mensual** (no semanal)
- Cecilia proveerá las horas de los doctores manualmente desde registros de facturación
- la agencia creará un botón para que Cecilia ejecute esta automatización

**Pendiente de Cecilia:** Corregir manualmente los datos históricos de feb, mar y abr en el informe de cupos de ocupación.

---

## 5. Plataforma centralizada (portal web)
🔵 **Backlog — Proyecto futuro**

Una plataforma web unificada para centralizar todas las tareas de reporting.

**Alcance planificado:**
- **Admin (Cecilia):** subir archivos de Dentalink, ejecutar automatizaciones, generar PDFs
- **Usuarios de sucursal:** ver sus propios PDFs
- **Socios:** ver los informes de resumen

**Próximo paso:** la agencia enviará hoja de ruta y presupuesto a Cecilia.

---

### 5.1 Botón con webhook para activar el workflow (Cecilia)
🔴 **Pendiente — Prioridad inmediata**

Como paso previo a la plataforma completa, se necesita una página web simple ("rústica") con un botón que dispara el workflow de n8n vía webhook. Permite que Cecilia ejecute la automatización semanal por su cuenta sin acceder a n8n.

**Objetivo:** Destrabar el flujo de trabajo de Cecilia para que pueda lanzar el proceso ella sola el sábado a la noche.

**Responsable:** la agencia

---

## Resumen ejecutivo

| Frente | Estado | Urgencia |
|--------|--------|----------|
| 1.1 Reporte general | 🟢 En producción | — |
| 1.2 Reporte por sucursal | 🔴 Pendiente | Alta |
| 2.1 Correo diario (métodos de pago) | 🟢 En producción | — |
| 2.2 Correo semanal socios | 🔴 Pendiente | Alta |
| 2.3 Correo mensual socios | 🔴 Pendiente | Alta |
| 2.4 Envío retroactivo abril | 🔴 Pendiente | 🔥 Urgente |
| 3. Informe no confirmados / atendidos | 🔴 Pendiente | Alta |
| 4. Informe eficiencia doctores | 🟡 En pausa | Baja |
| 5.1 Botón webhook para Cecilia | 🔴 Pendiente | 🔥 Inmediata |
| 5. Plataforma centralizada (completa) | 🔵 Backlog | Futura |
