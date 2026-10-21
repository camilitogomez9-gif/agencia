# Presupuesto para Latinbien
**Fecha:** 01/08/2025

---

## Introducción

Proponemos un Agente Conversacional de Inteligencia Artificial para la tienda Latinbien. Este Agente automatizará procesos de ventas (línea de crédito y contado), conectándose al ERP Odoo para acceder a la base de datos de productos y para gestionar leads, con un enfoque inicial en ventas. Construido con n8n, OpenAI y ManyChat, el Agente manejará consultas en WhatsApp, Instagram, Facebook y opcionalmente Telegram, ofreciendo respuestas conversacionales con tono profesional y cercano, adaptado a la audiencia local.

Además, la propuesta incluye un **Agente de Gestión de Datos Ingresados desde Formularios** para gestionar y limpiar la información de los leads.

El sistema incluirá una base de conocimiento actualizable (RAG), calculadora de planes de pago fraccionados, registro de datos de leads en el CRM, registro de interacciones y escalamiento a humanos para casos prioritarios (ej: intención de compra confirmada, emergencia, etc.).

La solución implementada optimiza significativamente el tiempo dedicado a la atención de consultas repetitivas, posicionando a la tienda para escalar de forma exponencial. Al mismo tiempo, permite a Latinbien reducir la necesidad de un equipo operativo amplio, mejorando su eficiencia y rentabilidad.

Además, esta infraestructura sentará las bases técnicas para una futura automatización del proceso de cobranza, asegurando una evolución orgánica del sistema hacia un modelo integral de atención y seguimiento postventa.

---

## Agente de Atención al Cliente

### Alcance General

El Agente de IA optimizará los procesos de ventas de la tienda, con los siguientes objetivos:

- **Automatizar Ventas:** Responder todas las consultas iniciales en WhatsApp, Instagram, Facebook y opcionalmente Telegram, sobre productos, planes de pago, procesos, preguntas frecuentes, etc.
- **Calculadora de Planes Fraccionados:** Generar dinámicamente planes de pago (ej: inicial del 30% o más, cuotas quincenales de 6, 10, 15 o 20) basados en el precio del producto y capacidad crediticia.
- **Integración con Odoo ERP/CRM:** Consultar productos en tiempo real (marca, categoría, atributos) y registrar leads/pedidos en Odoo.
- **Gestión de Conversaciones:** Log de interacciones en ManyChat, con etiquetas y escalamiento a asesores para intención de compra.
- **Soporte Multicanal:** Configuración modular para gestionar conversaciones de distintos canales (WhatsApp, Instagram y Facebook).
- **Escalabilidad:** Preparado para flujo de mensajes altos durante expansión nacional.

---

### Funcionalidades del Agente de Atención al Cliente

#### 1. Atención Conversacional

**Descripción:** Responde consultas en WhatsApp, Instagram, Facebook (y opcionalmente Telegram) con un tono humano, detectando intenciones (ej: consulta de producto, interés en crédito) y adaptando respuestas.

**Detalles:**
- Saludo: "¡Hola! Bienvenido a Latinbien. 😊 ¿Buscas un producto o quieres saber sobre nuestros planes de pago?"
- Responde preguntas frecuentes: catálogo, precios, planes, envíos (ej: "¿Cuánto cuesta un teléfono?" → "Puedo mostrarte modelos disponibles. ¿Tenés alguna marca o presupuesto en mente?").
- Tono: Profesional, amigable, adaptado a la audiencia venezolana. Completamente personalizable según lo que busca el equipo de Latinbien.

#### 2. Calculadora de Planes de Pago Fraccionados

**Descripción:** Calcula dinámicamente planes de pago basados en el monto inicial y las cuotas, ajustando el precio final de forma personalizada con cada usuario.

**Detalles:**
- Ajusta precios según duración: más cuotas, mayor precio final (lógica definida con el cliente).
- Solicita datos: "Para calcular tu plan, dime tu presupuesto y capacidad de pago inicial."

#### 3. Gestión de Productos

**Descripción:** Consulta productos en tiempo real desde Odoo ERP (marca, categoría, atributos, precio, etc.) para ofrecerlos a los usuarios.

**Detalles:**
- Ofrece productos que coinciden con las preferencias del usuario: "Tenemos el Samsung Galaxy A54 que se ajusta a tu presupuesto de $1000. ¿Te interesa verlo por la web?"
- Responde detalles: "El Galaxy A54 tiene 128GB y cámara de 50MP, ideal para ti que buscas tomar muchas fotos."
- Filtra por presupuesto o preferencias si se proporcionan.

#### 4. Registro y Escalamiento de Conversaciones

**Descripción:** Registra interacciones en ManyChat y notifica y escala a asesores en situaciones clave, registrando cambios de etapa de leads en Odoo.

**Detalles:**
- Escalamiento: Notifica a asesores vía ManyChat (o Telegram) cuando hay intención de compra, emergencias, etc.
- Ejemplo: Cliente: "Quiero el plan de 10 cuotas." → Agente: "¡Perfecto! Te paso con un asesor para completar el proceso de compra." → Notifica y cambia de etapa en Odoo: "Lead Juan, iPhone, plan 10 cuotas."

#### 5. Generación de Pedidos

**Descripción:** Crea pedidos en Odoo ERP creando notas en leads tras confirmar intención de compra, incluyendo producto y plan de pago.

**Detalles:**
- Ejemplo: Cliente confirma iPhone, plan 10 cuotas → Agente: "Tu pedido está registrado: iPhone, inicial $90, 10 cuotas de $22.50. Recibirás confirmación."
- Notifica al equipo para validación manual si es necesario.

#### 6. Soporte Multicanal

**Descripción:** Responde en WhatsApp, Instagram, Facebook (y opcionalmente Telegram).

**Tiempo de implementación:** 3 – 4 semanas
**Costo:** USD 1.998 (pago único)

---

## Agente de Gestión de Datos Ingresados desde Formularios

Este Agente ya se encuentra parcialmente implementado por Latinbien y cumple una función crítica dentro del embudo de ventas: limpiar, estructurar y registrar correctamente la información de leads provenientes de formularios publicitarios (Meta Ads) y del e-commerce.

La solución será integrada al ecosistema general propuesto y mejorada con capacidades adicionales que aumentan su confiabilidad y escalabilidad.

#### 1. Limpieza Inteligente de Datos

**Descripción:** El Agente analiza los leads capturados desde formularios de Instagram/Facebook y corrige inconsistencias comunes en los datos ingresados por usuarios.

**Detalles:**
- Normaliza teléfonos, eliminando caracteres y estandarizando formato local (ej: +58 412-1234567 → 04121234567).
- Corrige errores comunes de tipeo en campos como nombre o email.
- Detecta duplicados en CRM antes de registrar nuevos leads.

#### 2. Enriquecimiento y Registro de Leads en Odoo

**Descripción:** Una vez corregidos los datos, el Agente estructura la ficha del lead para su registro en el CRM.

**Detalles:**
- Garantiza que los campos obligatorios estén presentes (nombre, teléfono).
- Establece una estructura uniforme para facilitar su uso por asesores.
- Listo para ampliarse con campos como producto de interés o presupuesto (si se definen con el cliente).

**Tiempo de implementación:** 3 – 7 días
**Costo:** USD 290 (pago único)

---

## Implementaciones Futuras Incluidas en el Mantenimiento

Estas funcionalidades se implementarán sin costos adicionales:

- **E-commerce Integrado:** Conectar el Agente a la futura plataforma de e-commerce para procesar compras directas.
- **Automatización de Cobranza:** Extender el Agente para gestionar recordatorios de cuotas y detectar intención de pago (tras definir procesos con el cliente).
- **Soporte para Campañas Masivas:** Manejar picos de ~3.000 mensajes diarios durante expansión nacional.

---

## Mantenimiento Mensual

En la agencia entendemos que cada empresa tiene diferentes necesidades y niveles de autonomía, por eso ofrecemos dos modalidades de mantenimiento.

### Opción 1: Acompañamiento por la agencia

**Soporte Técnico:**
- Resolución de incidencias en n8n, ManyChat o integraciones con la API de Odoo.
- Monitoreo de las conversaciones para detectar errores, respuestas fuera de tono o problemas con la base de datos.
- Ajustes en los flujos conversacionales según feedback del equipo (ej: "Agregar una respuesta para consultas sobre envíos nacionales").

**Actualización de Funcionalidades:**
- Incorporación de nuevas funcionalidades sencillas.
- Optimización de respuestas para mejorar la tasa de conversión.

**Capacitación y Seguimiento:**
- Capacitación inicial al equipo de Latinbien sobre la gestión de derivaciones y aspectos relacionados a la solución.
- Grupo de WhatsApp exclusivo con el el equipo para resolver dudas en tiempo real, proponer mejoras y coordinar ajustes.
- Reuniones (opcionales) para evaluar el rendimiento del Agente y definir nuevas funcionalidades.

**Costo de Mantenimiento Mensual: USD 298 / mes**

**Desglose:**
- Costos Fijos: OpenAI Tokens + Honorarios la agencia
- Monitoreo diario de interacciones y logs.
- Resolución de incidencias en menos de 24 horas.
- Ajustes de flujos (ej: nuevos productos, promociones).
- Implementación de futuras funcionalidades.
- Reportes semanales de métricas.

> Los costos fijos de ManyChat y Odoo serán cubiertos por el equipo de Latinbien.

---

### Opción 2: Sin Acompañamiento por la agencia

**Total: USD 0 / mes**

La solución será transferida por completo al equipo de Latinbien, asegurando su correcto funcionamiento.

---

## Cronograma de Implementación

**Duración Total:** 3 – 4 semanas

- **Días 1–5:** Configuración de n8n, ManyChat, WhatsApp Business API, Meta API, Odoo API, OpenAI. Entrega de versión de prueba inicial (5–7 días).
- **Semana 1–2:** Desarrollo de atención conversacional, calculadora, captura de leads, gestión de productos y escalamiento. Pruebas con datos reales de Odoo.
- **Semana 3–4:** Ajustes según feedback, integración completa con Odoo, capacitación y lanzamiento.

> Incluye 2–3 versiones de prueba para garantizar satisfacción.

---

## Inversión

### Desarrollo Inicial (Pago Único)

| Componente | Costo (USD) |
|---|---|
| Agente de Atención al Cliente | 1.998 |
| Agente de gestión de datos desde formularios | 290 |
| **Total** | **2.288** |

**Condiciones de Pago:**
- 50% al inicio para confirmar.
- 50% tras finalización y aprobación final.

### Mantenimiento

| Opción | Costo |
|---|---|
| Acompañamiento por la agencia | USD 298 / mes |
| Sin acompañamiento por la agencia | USD 0 / mes |

**Opciones de Pago:** PayPal, Payoneer, Western Union, Binance.

---

## Beneficios Esperados

- **Ahorro de Tiempo:** Automatiza el 80% de las consultas, liberando a múltiples asesores para cierres y tareas estratégicas.
- **Mejor Conversión:** Filtra leads no cualificados, enfocando esfuerzos en clientes con intención de compra.
- **Escalabilidad:** Soporta picos altos de mensajes diarios.
- **Experiencia del Cliente:** Respuestas rápidas y humanas mejoran la percepción de la marca.

---

## Notas Adicionales

- **Seguridad:** APIs oficiales (WhatsApp, Meta, Odoo) con HTTPS.
- **Propiedad:** La propiedad de la solución pertenecerá 100% al equipo de Latinbien.

---

## Próximos Pasos

1. Confirmación del presupuesto para comenzar el proyecto.
2. Envío de formulario por parte de la agencia para que el equipo de Latinbien complete con información clave del funcionamiento del Agente.

**WhatsApp:** +598 92 314 547
**Mail:** [EMAIL-AGENCIA]
