# Presupuesto para Weak Meak
**Fecha:** 25/04/2025

---

## Introducción

Este presupuesto detalla una solución integral diseñada específicamente para abordar los desafíos actuales de Weak Meak, como la gestión de consultas a través de múltiples canales (Instagram, WhatsApp y correo electrónico), la necesidad de respuestas inmediatas, y la integración con su base de datos de la tienda online para proporcionar información precisa sobre productos, stock, precios, promociones y datos de envíos.

Además, proponemos un enfoque escalable que permitirá a Weak Meak adaptarse a futuros cambios, como la migración al nuevo ERP Odoo, garantizando una transición fluida y un soporte continuo. Nuestro objetivo es implementar un Agente de Inteligencia Artificial conversacional avanzado que actúe como un asistente virtual, ofreciendo respuestas humanizadas, personalizadas y eficientes, mientras se integra perfectamente con sus sistemas actuales.

A continuación, presentamos una propuesta detallada que no solo resolverá los puntos débiles mencionados, mejorando la experiencia del usuario y aumentando las conversiones.

---

## 1. Desarrollo Inicial

### 1.1 Implementación del Agente de IA

**Diseño y desarrollo del Agente:** Creación de un Agente de Inteligencia Artificial que cumplirá las siguientes funciones clave, alineadas con las necesidades de Weak Meak:

- **Gestión multicanal de consultas:** Atención al cliente automatizada en Instagram, Facebook, WhatsApp y correo electrónico, integrando las interacciones (excepto las de correo electrónico) en el inbox de ManyChat para optimizar tiempo, filtrar conversaciones y escalar al equipo humano solo las que requieran intervención.
- **Acceso a la base de datos de la tienda online:** Conexión directa a la base de datos a través de la API disponible, permitiendo al Agente consultar en tiempo real información sobre productos, stock, precios, y enlaces directos a la página web para compras. También proporcionará imágenes de productos y detalles de promociones específicas.
- **Recomendaciones personalizadas:** El Agente se adaptará a las preferencias del usuario, ofreciendo opciones personalizadas que se alineen con sus necesidades.
- **Seguimiento de envíos:** Consulta del estado de pedidos (ej: "Tu pedido #1234 está en camino") utilizando la API adecuada, derivando a un humano si la consulta requiere información no disponible en el sistema.
- **Humanización de la interacción:** Uso de un tono cercano, profesional y alineado con la marca Weak Meak, enviando mensajes en partes (como un humano), evitando signos de interrogación iniciales, y utilizando emojis moderados según prefiera la empresa.
- **Escalamiento a humanos:** Derivación automática de consultas complejas (ej: problemas con Mercado Pago, quejas específicas) al inbox de ManyChat, notificando únicamente a la persona asignada para evitar duplicidad de esfuerzos.
- **Gestión de promociones:** Explicación clara de promociones vigentes, con respuestas personalizadas que refuercen el valor de la oferta y dirijan al cliente a la compra.
- **Soporte 24/7:** Respuestas inmediatas en todo momento, para capturar oportunidades de venta y resolver consultas urgentes, mejorando la experiencia del cliente.

**Beneficios clave:**

- Reducción significativa de la carga de trabajo del equipo de Weak Meak, permitiéndoles enfocarse en tareas con mayor retorno.
- Mejora de la inmediatez en la atención, capturando clientes que consultan fuera de horario aprovechando su impulso de compra.
- Aumento de conversiones al ofrecer respuestas personalizadas.
- Mayor orden en la gestión de consultas, con derivaciones inteligentes y resúmenes claros (estos resúmenes automáticos podrán ser integrados en el ERP para un seguimiento detallado de interacciones con clientes).

**Tiempo de desarrollo:** 2 – 3 semanas
**Costo del desarrollo inicial:** USD 2.597

---

## 2. Mantenimiento Mensual

### 2.1 Soporte Técnico

- Resolución de incidencias en n8n, ManyChat, o integraciones con la API de la tienda online.
- Monitoreo de las conversaciones para detectar errores, respuestas fuera de tono, o problemas con la base de datos.
- Ajustes en los flujos conversacionales según feedback del equipo (ej: "Agregar una respuesta para consultas sobre envíos internacionales").

### 2.2 Actualización de Funcionalidades

- Incorporación de nuevas instrucciones al prompt según necesidades emergentes (ej: explicar nuevas promociones, actualizar tabla de talles, etc.).
- Optimización de respuestas para mejorar la tasa de conversión (ej: ajustar el tono para sonar más persuasivo en promociones).
- Migración al ERP Odoo cuando Weak Meak lo necesite, asegurando compatibilidad con su API y ajustando las conexiones necesarias.

### 2.3 Capacitación y Seguimiento

- Capacitación inicial al equipo de Weak Meak sobre la gestión de derivaciones y aspectos relacionados a la solución para que la adaptación sea fluida y sencilla.
- Grupo de WhatsApp exclusivo con el el equipo para resolver dudas en tiempo real, proponer mejoras y coordinar ajustes.
- Reuniones semanales (opcionales) para evaluar el rendimiento del Agente y definir nuevas funcionalidades.

### 2.4 Cobertura de Costos Fijos

- Licencias de n8n, tokens de OpenAI, y suscripciones de plataformas necesarias.
- Mantenimiento de servidores y conexiones API para garantizar operatividad continua.

**Costo del mantenimiento mensual: USD 332 / mes**

---

## 3. Futuras Implementaciones

Sugerimos considerar las siguientes funcionalidades escalables para fases posteriores:

- **Gestión avanzada de comentarios:** Automatización completa de respuestas a comentarios en Instagram y Facebook, con moderación inteligente para detectar tonos negativos y notificar al equipo con opciones de respuesta personalizadas.
- **Envío de audios personalizados:** Clonación de voz para enviar mensajes de audio pregrabados (ej: "Hola, soy parte del equipo de Weak Meak, ¡aprovechá el 14x1 hoy!"), aumentando la conexión emocional con los clientes.
- **Integración con Odoo ERP:** Conexión completa con el nuevo ERP Odoo, permitiendo al Agente consultar datos de sucursales físicas, gestionar inventario unificado y responder consultas sobre puntos de venta.
- **Dashboard de métricas avanzado:** Ampliación del panel visual con métricas adicionales, como análisis de comportamiento por canal y segmentación por tipo de cliente.

---

## Resumen del Proyecto

| Concepto | Monto |
|---|---|
| Desarrollo Inicial | USD 2.597 |
| Mantenimiento Mensual | USD 332 / mes |
| Tiempo de Entrega | 2 – 3 semanas |

---

## Notas Adicionales

- **Reunión inicial:** Sugerimos realizar una reunión inicial tras la aprobación del presupuesto para pulir la base de conocimiento (ej: preguntas frecuentes, detalles de promociones) y crear una base sólida para el Agente.
- **Versión de prueba:** Durante el desarrollo se entregará una versión de prueba del Agente de Weak Meak para que el equipo pueda interactuar, simular consultas de clientes y proporcionar feedback. Esta etapa permitirá validar el tono, la precisión de las respuestas y la integración con la base de datos, ajustando la solución para garantizar que sea 100% a medida antes de la entrega final.
- **Flexibilidad:** La solución es adaptable a cambios, como la migración a Odoo o la incorporación de comentarios en publicaciones. Los costos de mantenimiento incluyen estas actualizaciones, y ofrecemos flexibilidad para reducir funcionalidades (ej: eliminar correo) si no generan el valor esperado.
- **Condiciones de pago:** Para comenzar el proyecto, solo se necesita abonar el **50% del desarrollo inicial**. El 50% restante se abona al hacer la entrega de la solución.
