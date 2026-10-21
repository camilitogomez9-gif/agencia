# Presupuesto para Pablo Noriega — Seguridad Electrónica
**Fecha:** 15/08/2025

---

## Introducción

Proponemos un Agente de Inteligencia Artificial conversacional para la distribuidora de seguridad electrónica de Pablo Noriega. Este Agente automatizará las consultas de consumidores finales, liberando al equipo de 5/6 vendedores para enfocarse en tareas de mayor retorno.

El Agente se integrará con la plataforma de Inbox ManyChat, ofreciendo respuestas personalizadas en español con tono personalizable según las preferencias de Pablo y su equipo. El Agente filtrará leads, gestionará ventas de productos y escalará casos complejos a humanos, reduciendo el tiempo de respuesta.

Este presupuesto detalla el desarrollo inicial, mantenimiento, implementaciones futuras y beneficios, con añadidos estratégicos como análisis de consultas y automatización de postventa para maximizar rentabilidad.

---

## Alcance General

El Agente de IA optimizará la atención al público vía WhatsApp, con los siguientes objetivos:

- **Automatizar Consultas:** Responder 24/7 a todos los mensajes entrantes con respuestas personalizadas.
- **Cualificación y Embudo:** Filtrar leads, notificando al equipo solo para casos cualificados.
- **Canales:** WhatsApp primario, con posibilidad de integrar Instagram o Facebook de ser necesario.
- **Integraciones:** ManyChat, Base de Datos de Productos, n8n.
- **Escalabilidad:** Preparado para campañas publicitarias y picos altos de demanda, así como para posibles implementaciones futuras.

---

## 1. Desarrollo Inicial

### Funcionalidades del Agente de IA

#### 1. Atención Conversacional

**Descripción:** Responde consultas en WhatsApp (y futuros canales) al instante, 24/7, con tono técnico accesible, detectando intenciones (consulta general, compra B2C, soporte B2B, etc.). Recibe y entiende audios, respondiendo con coherencia y naturalidad.

**Detalles:**
- Saludo: "¡Hola! Bienvenido. ¿Buscas cámaras, alarmas o algo específico?"
- Responde preguntas frecuentes: Precios, modelos, características, stock, entre otros.
- Tono: Profesional, empático, adaptado según preferencias de la empresa.
- Ejemplo: Cliente: "Necesito una cerradura de reconocimiento facial barata" → Agente: "¡Genial! Una opción económica sería [Modelo X], especial para hogares modernos."

#### 2. Cualificación de Leads

**Descripción:** Filtra y clasifica leads en base a datos clave (B2B, B2C, producto, presupuesto, etc.), registrándolos de forma personalizada en ManyChat o en CRM diseñado a medida.

**Detalles:**
- Cualifica y etiqueta según el lead (ej: "B2B – Potencial", "B2C – Consulta", entre otros).
- Registra información clave en CRM (Nombre, Teléfono, Producto de interés, entre otros).
- Ejemplo:
  - Cliente: "Soy un instalador, necesito 10 cámaras abajo de los USD 100."
  - Agente: "¡Perfecto! 😊 Te voy a derivar a nuestra área especializada para continuar con la compra. ¿Cuál es tu nombre?"

#### 3. Información de Productos y Base de Datos

**Descripción:** Proporciona datos detallados de productos de manera personalizada, alineada con las preferencias del usuario.

**Detalles:**
- Responde detalles técnicos: "Cámara X soporta 50 rostros, tiene un alcance de 100m, cuesta USD $300."
- Envía PDFs (opcional): "Te envío la ficha técnica de la cámara X: [PDF]. Avísame si te gustaría avanzar con la compra."
- Filtra opciones según el tipo de cliente: B2B vs. B2C.
- Ejemplo: Cliente: "¿Qué cámaras tienen para negocios?" → Agente: "Te recomendamos el Modelo Z, con IA facial, especial para grandes espacios. Si querés te envío la información técnica."

#### 4. Escalamiento a Humanos

**Descripción:** Transfiere consultas complejas o emergencias al equipo de forma inmediata, notificándolos.

**Detalles:**
- Detecta emergencias: "Falla en cámara X" → "Bien, no te preocupes, enseguida te pasamos con un experto técnico para que pueda asistirte."
- Notifica al equipo: "Consulta escalada: Instalador pregunta por reconocimiento facial, DNI X."

#### 5. Análisis de Consultas y Leads

**Descripción:** Genera un reporte semanal (PDF) en base al historial de conversación para optimizar ventas y obtener métricas de interés.

#### 6. Memoria Conversacional

**Descripción:** Recuerda el historial de conversaciones para respuestas contextuales.

**Detalles:**
- Almacena: Datos del cliente (edad, nivel, presupuesto), interacciones previas.
- Ejemplo: "¡Hola Luis! Para tu hija de 8 años te recomendaría empezar por el modelo básico si me comentas que ella aún no ha patinado."

---

## Implementaciones Futuras Incluidas en el Mantenimiento

Estas funcionalidades se implementarán sin costos adicionales:

- **Seguimientos Automatizados:** Envía recordatorios personalizados (8h, 24h, 72h) para acciones pendientes o conversaciones perdidas (confirmar cotización, pagar, entre otros).
- **Dashboard de Métricas:** Visualizaciones en Google Data Studio (ej: "80% consultas B2C, 40% conversiones").
- **Análisis de Multimedia:** Reconocimiento de imágenes para mantener la conversación fluida con el cliente.
- **Reconocimiento de Transferencias o Pagos:** Extraer datos de interés en base a capturas de transferencias o pagos recibidos y postarlos en el CRM.
- **Soporte para Facebook / Instagram / Web:** Responder consultas en nuevos canales.

---

## Cronograma de Implementación

**Duración Total:** 3 – 4 semanas

- **Semana 1:** Prompt/instrucciones del Agente, ajustes en el tono, flujo de conversación y configuración de memoria. Entrega de versión de prueba básica.
- **Semana 2–3:** Carga de catálogo. Desarrollo de consultas, pedidos, escalamiento. Pruebas con datos reales. Entrega de versión de prueba avanzada.
- **Semana 3–4:** Ajustes finales, capacitación y lanzamiento.

> Incluye 3–4 versiones de prueba para ajustes.

---

## Inversión

### Desarrollo Inicial (Pago Único)

**Total: USD 1.512**

| Condición | Monto |
|---|---|
| 50% al inicio (para confirmar) | USD 756 |
| 50% tras aprobación final | USD 756 |

**Opciones de Pago:** PayPal, Western Union, Payoneer, Binance.

---

### Mantenimiento Mensual

**Total: USD 268 / mes**

**Desglose de Costos Fijos:**
- OpenAI Tokens
- ManyChat
- WhatsApp Business API
- Servidor de n8n para alojar la solución

**Honorarios la agencia:**
- Monitoreo diario de interacciones y logs.
- Resolución de incidencias en menos de 24 horas.
- Grupo de WhatsApp con el el equipo.
- Ajustes de flujos (nuevos productos, promociones, entre otros).
- Implementación de futuras funcionalidades.
- Reportes semanales de métricas.

> En caso de que la empresa supere los 500 contactos registrados dentro de ManyChat y quiera mantener el historial de conversaciones, esta se hará responsable del costo fijo asociado.

---

## Beneficios Esperados

- **Ahorro de Tiempo:** Automatiza todas las consultas, liberando a los vendedores y brindándole a Pablo la oportunidad de optimizar recursos.
- **Mejor Conversión:** Cualificación personalizada aumenta ventas.
- **Experiencia del Cliente:** Respuestas expertas y rápidas mejoran satisfacción.
- **Datos Valiosos:** Análisis de consultas permite tomar mejores decisiones.
- **Escalabilidad:** Soporta múltiples mensajes al mismo tiempo.

---

## Notas Adicionales

- **Seguridad:** APIs oficiales (WhatsApp, Meta) con HTTPS. Todos los datos y flujos son propiedad del cliente.
- **Soporte Continuo:**
  - Grupo de WhatsApp (respuesta rápida).
  - Ajustes de tono o flujos en menos de 24 horas.
  - Capacitación inicial para Pablo y su equipo.
  - Reuniones opcionales a pedido.

---

## Próximos Pasos

1. Confirmación del proyecto.
2. Lectura de la hoja de ruta de la agencia.
3. Envío de formulario para que Pablo complete con información clave de su empresa.
