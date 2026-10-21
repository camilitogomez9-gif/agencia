# Presupuesto para Genera tu Energía
*(Solución Base)*

---

## Alcance de la Solución Base

### Objetivo Principal

Implementar un Agente de Inteligencia Artificial conversacional que actúe como un filtro inicial para las consultas de los clientes, gestione interacciones en múltiples plataformas (sitio web, WhatsApp, Instagram, Facebook) y facilite la generación de embudos de venta, integrándose con HubSpot y WooCommerce. El Agente proporcionará respuestas personalizadas basadas en la información de todas las páginas del sitio web, folletos técnicos y catálogo de productos, con un tono conversacional humanizado y adaptado al público objetivo (personas de 40 a 80 años, principalmente B2B).

---

## Funcionalidades Clave del Agente de IA

### 1. Atención Multicanal

- Respuesta simultánea a consultas en el sitio web (WordPress), WhatsApp, Instagram y Facebook.
- Uso de APIs oficiales para evitar bloqueos.

### 2. Acceso a Información del Sitio

- Extracción y procesamiento de datos de las páginas del sitio, folletos en PDF y catálogo de productos en WooCommerce, entre otros medios que se necesiten.
- Respuestas basadas en información detallada y preguntas frecuentes.
- Recomendaciones de productos personalizadas según las necesidades del usuario.

### 3. Memoria

- El Agente tendrá la capacidad de recordar la conversación con el usuario para brindar respuestas mucho más personalizadas y contextualizadas (ej: "Hola Jorge, ¿seguís interesado en los paneles solares por los que preguntaste ayer?").

### 4. Humanización de la Interacción

- Tono conversacional con jerga totalmente personalizable (ej: Rioplatense, argentina, etc.).
- Respuestas adaptadas al contexto.
- Capacidad de manejar mensajes fragmentados y múltiples consultas en una sola interacción.

### 5. Integración con HubSpot

- Registro automático de leads en HubSpot con categorización según el nivel de interés.
- Creación de embudos de venta iniciales para segmentar contactos.
- Notificaciones al equipo de ventas para leads calificados que requieran intervención humana.

### 6. Automatización de Seguimientos

- Envío de múltiples mensajes de seguimiento personalizados una vez el lead deja de contestar (ej: a las 8 horas se le envía: "Hola Juan, vimos que estabas interesado en paneles solares y justo tenemos un descuento especial que te podría interesar. ¿Querés escuchar de qué se trata?").

### 7. Gestión de Inbox

- Implementación de una plataforma de inbox para que el equipo de ventas visualice conversaciones, embudos y notificaciones desde dispositivos móviles o computadoras de forma sencilla.
- Asignación de conversaciones que requieran atención humana (las consultas triviales y repetitivas serán filtradas y respondidas por el Agente).

### 8. Escalabilidad

- Diseño modular que permite agregar funcionalidades futuras, como interacción por voz o integración con otras plataformas.

**Costo de desarrollo inicial: USD 1.827**
**Tiempo de entrega: 2 – 3 semanas**

---

## Especificaciones Técnicas

### Tecnologías Utilizadas

- **n8n:** Plataforma de automatización alojada en el servidor de la agencia. Gestiona flujos conversacionales, integraciones con APIs y almacenamiento de datos.
- **Vertex LLM:** Modelo de IA para procesar consultas y generar respuestas basadas en el contenido del sitio y FAQs.
- **HubSpot:** Gestión de leads y embudos de venta. Integración directa con n8n para registrar datos y notificar al equipo.
- **Chatrace:** Plataforma de inbox para visualizar conversaciones, gestionar leads y enviar seguimientos.
- **WordPress / WooCommerce:** Extracción de datos de productos y páginas mediante APIs nativas.
- **APIs Oficiales:** WhatsApp, Instagram, Facebook, WooCommerce y HubSpot.

### Seguridad

- Uso de APIs oficiales y protocolos HTTPS para garantizar la estabilidad y evitar inconvenientes.

---

## Mantenimiento Mensual

### Soporte Técnico

- Resolución de incidencias en n8n, Chatrace o integraciones con APIs.
- Monitoreo de las conversaciones para detectar errores, respuestas fuera de tono o problemas con la información.
- Ajustes en los flujos conversacionales según feedback del equipo (ej: "Agregar una respuesta para consultas sobre pagos.").

### Actualización de Funcionalidades

- Incorporación de nuevas instrucciones al prompt según necesidades emergentes (ej: explicar nuevas promociones, actualizar detalles, etc.).
- Optimización de respuestas para mejorar la tasa de conversión (ej: ajustar el tono para sonar más persuasivo en promociones).

### Capacitación y Seguimiento

- Capacitación inicial al equipo de Genera tu Energía sobre la gestión de derivaciones y aspectos relacionados a la solución para que la adaptación sea fluida y sencilla.
- Grupo de WhatsApp exclusivo con el el equipo para resolver dudas en tiempo real, proponer mejoras y coordinar ajustes.
- Reuniones semanales (opcionales) para evaluar el rendimiento del Agente y definir nuevas funcionalidades.

### Cobertura de Costos Fijos

- Licencias de n8n, tokens de LLM (como Vertex u OpenAI), y suscripciones de plataformas necesarias.
- Mantenimiento de servidores y conexiones API para garantizar operatividad continua.

**Costo del mantenimiento mensual: USD 252 / mes**

---

## Ideas de Fases Posteriores

- **Envío de mensajes en frío en masa:** Herramienta avanzada del Agente para campañas outbound.
- **Automatización de procesos internos:** Facturación, sustitución de tareas administrativas.
- **Interacción por Voz:** Audios personalizados en tiempo real para contestar las consultas de los clientes. Uso de ElevenLabs para clonación de voz.
- **Automatización de mails:** Respuestas personalizadas automáticas a través de mail (usando SMTP).
- **Creación de contenido automatizada:** Posts personalizados según cada red social.

> Los costos de fases futuras se ajustarán según facturación y necesidades del cliente, asegurando un enfoque escalable.

---

## Beneficios Esperados

- **Eficiencia:** Reducción de consultas triviales (ej: "¿Alquilan equipos?") que llegan al equipo de ventas.
- **Conversión:** Mejora en la tasa de conversión al filtrar leads calificados y gestionar embudos automatizados.
- **Autoridad SEO:** Respuestas rápidas y personalizadas en redes sociales y el sitio web, aumentando la autoridad en Google.
- **Escalabilidad:** Solución modular que crece con la empresa, desde 50 consultas diarias hasta miles en el futuro.
- **Humanización:** Interacciones cálidas y adaptadas al público objetivo, mejorando la experiencia del cliente.
- **Control de Costos:** Inversión inicial y costos fijos manejables, atados al crecimiento de la facturación.

---

## Notas Importantes

- **Pago:** la agencia solo solicita el pago del **50% del desarrollo inicial** para comenzar el proyecto. El 50% restante se abona al finalizar, tras la aprobación del cliente.
- **Flexibilidad:** Los flujos son iterativos; añadiremos funcionalidades según surjan necesidades. Si algo no es viable, propondremos alternativas de inmediato.
