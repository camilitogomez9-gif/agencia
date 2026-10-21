# Presupuesto para Dental Design Smile
**Fecha:** 08/07/2025

---

## Introducción

Proponemos un Agente de Inteligencia Artificial de Voz para Dental Design. Este Agente, diseñado para automatizar la recepción de llamadas telefónicas, optimizará la atención inicial de pacientes, reduciendo la carga de tres operadores humanos dedicados a tareas repetitivas como saludos, consultas triviales (ej: horarios, servicios) y transferencias a especialistas.

Este presupuesto detalla el desarrollo inicial, mantenimiento, implementaciones futuras y beneficios, asegurando una solución que optimizará la eficiencia de Dental Design.

---

## Alcance General

El Agente de Voz será un asistente de IA que operará 24/7 en la línea telefónica de Dental Design, con las siguientes metas:

- **Automatizar la atención inicial:** Gestionar saludos, consultas frecuentes (ej: horarios, servicios, precios) y transferencias a Agentes humanos en tiempo real.
- **Reducir carga operativa:** Minimizar el tiempo de los operadores en consultas repetitivas, permitiendo enfocarse en casos complejos que traigan mayor retorno.
- **Soporte bilingüe:** Responder en español e inglés, detectando el idioma del paciente para una experiencia fluida.
- **Escalabilidad:** Preparar el Agente para múltiples clínicas y procesos adicionales (ej: guardar datos de pacientes en un CRM).
- **Captura de datos:** Registrar consultas y transferencias para obtener métricas útiles (ej: volumen de llamadas, tipos de consultas, tiempo medio por llamada).

---

## 1. Desarrollo Inicial

### Funcionalidades del Agente de Voz

#### 1. Recepción de Llamadas y Saludo Inicial

**Descripción:** Responde llamadas con un saludo profesional y personalizado, identificando el propósito de la llamada.

**Detalles:**
- Saludo: *"Buenos días, gracias por llamar a Dental Design. ¿En qué puedo ayudarlo hoy?"* (español/inglés, según idioma detectado).
- Detecta intenciones: nuevo paciente, consulta de precios, horarios, o emergencias (ej: "Se me perdió una carilla").
- Ejemplo: Paciente: "¿Hasta qué hora están abiertos?" → Agente: "Estamos abiertos hasta las 6:00 p.m. ¿Desea información sobre algún servicio?"
- Tono profesional y cercano, totalmente personalizable según la identidad de Dental Design.

#### 2. Gestión de Consultas Triviales

**Descripción:** Responde preguntas frecuentes sobre horarios, servicios, precios y ubicaciones.

**Detalles:**
- Cubre: Horarios (ej: "Lunes a viernes, 8:00 a.m. – 6:00 p.m."), servicios (ej: limpiezas, ortodoncia), precios estimados (ej: "Una limpieza cuesta ~$80 USD").
- Responde con información de una base de conocimiento completa con todos los detalles y procesos de la clínica.

#### 3. Transferencia a Humanos

**Descripción:** Transfiere llamadas complejas o nuevos agendamientos a operadores humanos o especialistas.

**Detalles:**
- Detecta casos y emergencias específicas, simpatizando con el paciente.
- Es capaz de capturar datos (nombre, número, entre otros) antes de transferir.

#### 4. Soporte Bilingüe

**Descripción:** Detecta y responde en español o inglés según el idioma del paciente.

#### 5. Captura de Datos de Llamadas

**Descripción:** Registra datos de cada llamada (tipo de consulta, idioma, resultado, entre otros) para análisis futuro.

**Detalles:**
- Almacena: Nombre, número, tipo de consulta (ej: horario, emergencia), si fue transferida (sí/no).
- Mantiene un Dashboard de Métricas actualizado.

---

### Dashboard Personalizado

Junto al Agente, se entregará un Dashboard personalizado (en Airtable) donde se registrarán todas las llamadas, junto a sus grabaciones, métricas y más. Este dashboard presentará la información de forma clara para que Dental Design pueda entender exactamente el retorno que les brinda la solución.

**Métricas disponibles:**

- Volumen de llamadas (ej: "900 llamadas el último mes").
- Porcentaje de consultas triviales vs. transferidas (ej: "60% triviales, 30% transferidas a ventas").
- Tipos de consultas (ej: "20% emergencias, 50% nuevos pacientes").
- Tasa de conversión (ej: "40% de nuevos pacientes agendan citas").

---

## Cronograma de Implementación

**Duración Total:** 3 – 4 semanas

- **Días 1–5:** Comienzo del desarrollo y entrega de versión de prueba inicial (a los 4–6 días).
- **Semana 1–2:** Desarrollo de recepción, consultas, transferencias y soporte bilingüe. Entrega de segunda versión de prueba.
- **Semana 3–4:** Implementación del dashboard, análisis, retoques en la personalización de voz y pruebas con datos reales. Capacitación y lanzamiento.

> Incluye 2–3 versiones de prueba para ajustes según feedback.

---

## Costos

### Desarrollo Inicial (Pago Único)

**Total: USD 2.492**

| Condición | Monto |
|---|---|
| 50% al inicio (para confirmar el proyecto) | USD 1.246 |
| 50% tras aprobación final | USD 1.246 |

---

### Costos Fijos Operativos (cubiertos por Dental Design)

| Servicio | Costo |
|---|---|
| Costo por LLM | USD 0.050 / min |
| Costo por Voice Engine (ElevenLabs) | USD 0.070 / min |
| Costo por telefonía (Twilio) | USD 0.015 / min |
| **Total por minuto** | **USD 0.135 / min** |

> **Ejemplo:** 100 llamadas de 3 minutos = USD 40.5 / mes en costos de uso.

| Servicio adicional | Costo |
|---|---|
| Voz personalizada (ElevenLabs, opcional) | USD 22 / mes |
| Dashboard con métricas (Airtable) | USD 24 / mes |
| Línea telefónica (Twilio) | ~USD 1.5 / mes |

> Estos costos serán cubiertos por el equipo de Dental Design mes a mes según el uso. Este importe no irá al bolsillo de la agencia; simplemente será utilizado para cubrir los costos fijos por uso de servicios.

---

## 2. Mantenimiento Mensual (Opcional)

### Soporte Técnico

- Monitoreo diario de interacciones.
- Reportes de consultas.
- Resolución de fallos (ej: API de ElevenLabs).

### Actualización de Funcionalidades

- Nuevas voces, idiomas o integraciones (CRM).
- Ajustes según feedback (ej: tono más cálido, voz más femenina).

### Capacitación y Seguimiento

- Grupo de WhatsApp exclusivo con el el equipo.
- Capacitación inicial para el equipo de Dental Design.
- Reuniones opcionales siempre que sea necesario.

### Opciones de Mantenimiento

| Opción | Costo |
|---|---|
| Soporte por la agencia | USD 338 / mes + Costos Fijos por servicios |
| Soporte y mantenimiento por Dental Design | USD 0 / mes |

> En ambos casos, la propiedad de la solución pertenecerá a Dental Design.

---

## Beneficios Esperados

- **Ahorro de Tiempo:** Automatización de consultas triviales, liberando a 3 operadores para tareas de mayor valor.
- **Mejor Experiencia del Cliente:** Respuestas 24/7 en español/inglés, con transferencias rápidas a especialistas, resolviendo altas demandas de consultas.
- **Reducción de Costos:** Reasigna personal a ventas o emergencias, optimizando el equipo en tareas de mayor retorno.
- **Datos Valiosos:** Análisis de llamadas y otras métricas para estrategias de marketing.
- **Escalabilidad:** Base modular que soporta múltiples clínicas y procesos.
- **Flexibilidad:** Voz personalizable y ajustes rápidos según feedback.

---

## Notas Finales

- **Seguridad y Propiedad:** Cumplimos normativas (HTTPS, APIs oficiales). Los datos (llamadas, historial) son propiedad de Dental Design.
- **Flexibilidad:**
  - Ajustamos voz, tono o integraciones según feedback.
  - En caso de que Dental Design opte por mantener la solución de forma autónoma, la agencia se asegurará de que la transferencia sea exitosa.
  - Opciones de alojamiento según preferencia.
- **Soporte Continuo:**
  - Grupo de WhatsApp exclusivo con el el equipo.
  - Capacitación inicial para el equipo de Dental Design.
  - Propuestas proactivas basadas en análisis de llamadas.

---

## Opciones de Pago

- PayPal
- Payoneer
- Binance
- Podemos ajustarnos a otro método en caso de ser necesario.

---

## Próximos Pasos

En caso de querer avanzar con la propuesta, agradecemos su confirmación vía WhatsApp (+598 92 314 547). Lo primero que haremos será enviarles un formulario con preguntas clave de su empresa para empezar a desarrollar el Agente a su medida.

**la agencia**
