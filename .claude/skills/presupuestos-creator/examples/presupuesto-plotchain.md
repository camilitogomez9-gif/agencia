# Presupuesto para PlotChain
**Fecha:** 07/03/2025

---

## 1. Desarrollo Inicial

### 1.1 Implementación del Agente de IA 'Community Manager' Multi-Tarea

**Diseño y desarrollo:** Creación de un Agente de IA avanzado personalizado que podrá:

- Responder consultas generales y específicas 24/7 por todos los canales necesarios (WhatsApp, Instagram, Web, Facebook, etc.)
- Aprender y nutrirse de conversaciones previas para mejorar la precisión en respuestas futuras.
- Generar respuestas según la intención del usuario y el contexto de la conversación.
- Transferir información clave a una base de datos para su análisis.
- Obtener métricas clave: cantidad de interacciones, temas más frecuentes, engagement, entre otros.
- Escalar conversaciones al equipo de la agencia en caso de requerir asistencia humana.
- Enviar notificaciones automáticas con alertas, recordatorios o eventos de interés.
- Mantener un tono ajustado a la forma de comunicarse de PlotChain y los valores de la empresa.

**Integraciones:**

- **API de OpenAI:** Para potenciar el asistente con el mejor modelo de datos y capacidades avanzadas de Inteligencia Artificial.
- **WhatsApp API:** Para el correcto manejo de las interacciones a través de WhatsApp Business.
- **n8n:** Para implementar el 'Backend' donde se gestiona el flujo de información, la generación de respuestas dinámicas basadas en los datos obtenidos y donde el Agente lleva a cabo las tareas.
- **ChatRace:** Para implementar el 'Frontend', visualizar y entrar a las conversaciones, enviar mensajes estructurados y alertar con notificaciones al equipo cuando sea necesario.
- **Supabase:** Para la memoria y el almacenamiento total de todos los usuarios y sus interacciones con el Agente.
- **Airtable:** Para la creación de un CRM Automatizado con la información clave de cada usuario, así como también un Dashboard con análisis de tendencias, preguntas frecuentes y datos de interés.

**Tiempo de desarrollo:** 2 – 3 semanas
**Costo Agente de IA:** USD 897

---

### 1.2 Implementación de Automatizaciones Clave

#### Moderación Automática de Comentarios y Análisis de Tendencias

El sistema automatizado (gestionado a través de ChatRace) moderará los comentarios en redes sociales para proteger la reputación de la marca y fomentar las interacciones positivas.

**Funciones Principales:**

- Eliminación automática de spam y comentarios negativos o inadecuados.
- Filtro de comentarios: se evadirán comentarios que inciten al odio y contengan palabras que la empresa quiera evitar.
- Respuesta automática a interacciones en redes como comentarios en publicaciones, menciones o respuestas a la historia (Instagram). También aplica a Facebook.
- Análisis de tendencias en conversaciones relacionadas con PlotChain: los comentarios serán guardados en una base de datos específica que se conectará con un Agente capaz de resumir los temas mencionados, permitiendo entender las tendencias de la audiencia. Este análisis será enviado por email mensualmente a la empresa.

**Tiempo de desarrollo:** 1 semana
**Costo:** USD 220

---

#### Social Media Manager Automatizado

Un Sistema Automatizado robusto planificará y ejecutará estrategias de contenido en redes sociales basado en todas las interacciones previas, garantizando una segmentación y un alcance superiores.

**Funciones Principales:**

- Creación automática de un calendario de publicaciones mes a mes, optimizado según engagement. Este calendario será gestionado en el CRM, con fácil acceso para editarlo de ser necesario.
- Redacción automática de Posteos, Blogs y Newsletters alineados con la identidad de marca.
- Adaptación del tono y estilo de comunicación según la plataforma (Instagram, LinkedIn, Twitter, etc.).
- El sistema se alimenta de publicaciones pasadas para crear contenido auténtico, entendiendo el tono y la forma de comunicarse específica de la empresa. También será 'alimentado' con todos los parámetros que la empresa considere necesarios para cada red social (tono, palabras a utilizar, cantidad de caracteres, estilo del post, etc.)
- El sistema estará optimizado para proporcionar posts relevantes y optimizados para SEO.

**Tiempo de desarrollo:** 1 – 2 semanas
**Costo:** USD 489

---

### 1.3 Implementación de CRM Automatizado

Para gestionar toda la información relevante de interacciones, estrategias de contenido y métricas clave, se desarrollará un CRM intuitivo y automatizado.

- **Gestión de interacciones y consultas:** Registro y clasificación de las consultas recibidas en redes sociales, WhatsApp y la web.
- **Seguimiento y análisis de métricas:**
  - Cantidad de interacciones diarias.
  - Temas más frecuentes en conversaciones.
  - Engagement por tipo de contenido.
  - Detección de tendencias en menciones y comentarios.
- **Gestión de contenido automatizado:** Creación de un calendario de publicaciones basado en métricas de interacción y engagement, optimizado para cada plataforma.
- **Segmentación y análisis de audiencia:**
  - Registro de usuarios con datos clave: nombre, intereses, número de celular, nivel de interacción.
  - Personalización de respuestas y campañas en función de la intención del usuario.
- **Automatización de campañas de Email Marketing:** Creación de secuencias de emails personalizadas para inversores y nuevos usuarios, basadas en su comportamiento e intereses.
- **Notificaciones al equipo:** Alertas en tiempo real sobre interacciones destacadas, menciones relevantes o necesidad de intervención manual en conversaciones críticas.

**Tiempo de desarrollo:** 1 – 2 semanas
**Costo CRM:** USD 220

---

### 1.4 Implementación de una Interfaz Visual

Desarrollo de una interfaz minimalista con toda la información almacenada en el CRM. El fin de esta interfaz es que la gestión de datos y la toma de decisiones sea lo más simple e intuitiva posible.

**Panel de control a medida con:**

- Calendario de publicaciones.
- Métricas clave de interacciones.
- Ideas para contenido basadas en engagement.
- Análisis de conversaciones con mayor impacto.
- Listado de respuestas más frecuentes.
- Datos de usuarios (nombre, número de celular, interés).

**Tiempo de desarrollo:** 1 semana
**Costo:** USD 158

---

### 1.5 Manual de Usuario

- **Tutoriales simples:** Entrega de videos cortos que explican el buen manejo del CRM y los sistemas integrados.
- **Capacitación y seguimiento:** Seguimiento constante para garantizar el correcto uso del CRM y todas sus funcionalidades.

**Costo: USD 0 (incluido junto al CRM)**

---

## 2. Mantenimiento

### 2.1 Soporte Técnico Mensual

- Resolución inmediata de problemas técnicos relacionados con el funcionamiento del Agente y las integraciones.
- Revisión constante de la solución para garantizar la optimización de los sistemas y que puedan mejorar con el tiempo.
- Monitoreo del sistema para asegurar un rendimiento óptimo y evitar interrupciones.

### 2.2 Actualización de Funcionalidades

- Incorporación de nuevas funcionalidades según las necesidades cambiantes de PlotChain.
- Optimización y ajustes del Agente basados en datos y mensajes con los clientes.

### 2.3 Gestión de CRM y Reportes

- Mantenimiento y ajustes de la integración con el CRM y sistemas de gestión de datos.
- Generación de reportes mensuales sobre el rendimiento del Agente.

### 2.4 Capacitación Continua

- Sesiones de actualización para el equipo, según nuevas funcionalidades implementadas.
- Soporte en la incorporación de herramientas adicionales si el negocio lo requiere.
- Grupo de WhatsApp junto al el equipo para comunicación constante.

### 2.5 Cubrimiento de Gastos Fijos

- la agencia cubrirá al 100% los gastos de los sistemas utilizados, como n8n, ChatRace, OpenAI, entre otros.

**Costo: USD 348 / mes**

> El mantenimiento comenzará a cobrarse a partir del segundo mes de implantada la solución.

---

## Notas Adicionales

- Para comenzar el proyecto solo debe abonarse el **50% del total del desarrollo inicial**. El 50% restante se abona al momento de implantar la solución.
- El pago puede ser realizado a través de **PayPal** o **MercadoPago**.
- Se recomienda una reunión semanal para revisión de avances y asegurar la transferencia de conocimientos.
- El scraping de leads (único) está incluido de forma gratuita en la propuesta. En caso de que este proceso requiera sistemas establecidos para funcionar posteriormente, será conversado entre ambas partes.
- Cualquier funcionalidad adicional de tamaño considerable que esté fuera del alcance del mantenimiento mensual será cotizada por separado.
