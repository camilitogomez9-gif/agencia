---
name: presupuestos-la agencia
description: >
  Usar este skill cada vez que el usuario solicite crear un presupuesto de desarrollo de
  soluciones de IA (agentes conversacionales, automatizaciones, CRMs, agentes de voz, etc.)
  para un cliente. Se activa cuando el usuario comparte una transcripción de llamada de
  descubrimiento, notas de reunión, o cualquier insumo de cliente y pide generar una propuesta
  económica formal. El output siempre es Markdown listo para copiar a Notion. No crear archivos
  externos. Responder en español con tono profesional.
---

# Skill: Generación de Presupuestos la agencia

## Descripción General

Este skill permite generar presupuestos profesionales en formato Markdown para proyectos de
automatización e Inteligencia Artificial, siguiendo el estilo, estructura y lineamientos de
la agencia. El output debe estar listo para copiar y pegar directamente en Notion.

---

## Proceso de Trabajo

### Paso 1 — Análisis del Insumo del Cliente

Antes de escribir el presupuesto, extraer de la transcripción o notas:

- **Nombre del cliente / empresa**
- **Problema principal** que quieren resolver
- **Canales** involucrados (WhatsApp, Instagram, Facebook, Web, Teléfono, etc.)
- **Integraciones requeridas** (CRM, ERP, ecommerce, plataformas específicas)
- **Funcionalidades mencionadas** (atención 24/7, escalamiento, CRM, dashboard, etc.)
- **Cantidad de usuarios / volumen** estimado
- **Restricciones** (presupuesto, plazos, tecnologías preferidas)
- **Información faltante** → preguntar al usuario antes de continuar si hay datos críticos ausentes

### Paso 2 — Determinar el Tipo de Solución

Identificar qué tipo de solución encaja según la llamada:

| Tipo | Cuándo usarlo |
|---|---|
| **Agente Conversacional** | Consultas en WhatsApp/RRSS, atención al cliente, ventas |
| **Agente de Voz** | Recepción de llamadas telefónicas, call centers |
| **Automatizaciones** | Social media, moderación, email marketing, procesos internos |
| **CRM Automatizado** | Gestión de leads, seguimiento, métricas |
| **Dashboard / Interfaz visual** | Visualización de datos y métricas |
| **Solución Combinada** | Múltiples agentes o módulos |

### Paso 3 — Determinar Costos Base

Usar los rangos de referencia extraídos de los presupuestos de ejemplo. Son estimativos y deben
ajustarse según la complejidad real del proyecto.

#### Desarrollo Inicial (pagos únicos)

| Módulo | Rango de Costo (USD) | Tiempo |
|---|---|---|
| Agente Conversacional básico (1 canal) | 897 – 1,200 | 1–2 semanas |
| Agente Conversacional multicanal estándar | 1,500 – 1,998 | 2–3 semanas |
| Agente Conversacional avanzado (ERP + multi-canal) | 2,000 – 2,597 | 2–3 semanas |
| Agente de Voz (IA telefónica) | 2,200 – 2,492 | 3–4 semanas |
| Automatización de moderación/RRSS | 220 – 489 | 1–2 semanas |
| CRM Automatizado | 220 – 350 | 1–2 semanas |
| Dashboard / Interfaz visual | 158 – 300 | 1 semana |
| Agente de limpieza/gestión de datos | 290 – 450 | 3–7 días |
| Solución completa (2 agentes + CRM) | 2,100 – 3,500 | 2–4 semanas |

#### Mantenimiento Mensual (recurrente)

| Tipo de Proyecto | Rango de Costo (USD/mes) |
|---|---|
| Solución básica (1 agente, pocos canales) | 237 – 268 |
| Solución estándar (multicanal + CRM) | 298 – 348 |
| Solución avanzada (ERP + múltiples agentes) | 332 – 400 |
| Agente de Voz | 338 + costos variables por minuto |

#### Costos Fijos para Agente de Voz (cubiertos por el cliente)

| Servicio | Costo |
|---|---|
| LLM (OpenAI) | USD 0.050 / min |
| Voice Engine (ElevenLabs) | USD 0.070 / min |
| Telefonía (Twilio) | USD 0.015 / min |
| **Total por minuto** | **USD 0.135 / min** |
| Voz personalizada (ElevenLabs, opcional) | USD 22 / mes |
| Dashboard Airtable | USD 24 / mes |
| Línea telefónica (Twilio) | ~USD 1.5 / mes |

### Paso 4 — Redactar el Presupuesto

Seguir estrictamente la estructura de secciones definida más abajo.

---

## Estructura del Presupuesto

El presupuesto se compone de los bloques que apliquen según el proyecto. No todos los bloques
son obligatorios; incluir solo los relevantes para el caso.

```
[BLOQUE OBLIGATORIO] Encabezado
[BLOQUE OBLIGATORIO] Introducción
[BLOQUE OBLIGATORIO] Desarrollo Inicial
[BLOQUE CONDICIONAL] Alcance General (para agentes de voz o soluciones complejas)
[BLOQUE CONDICIONAL] Funcionalidades del Agente
[BLOQUE CONDICIONAL] Cronograma de Implementación
[BLOQUE OBLIGATORIO] Costos / Inversión
[BLOQUE OBLIGATORIO] Mantenimiento Mensual
[BLOQUE CONDICIONAL] Implementaciones Futuras
[BLOQUE OBLIGATORIO] Notas Adicionales / Condiciones de Pago
[BLOQUE CONDICIONAL] Próximos Pasos
```

---

## Template Completo con Instrucciones

A continuación, el template con instrucciones inline (en `[corchetes]`) para cada sección.

---

### BLOQUE: Encabezado

```markdown
# Presupuesto para [NOMBRE DEL CLIENTE]
**Fecha:** [DD/MM/AAAA]
```

> Regla: Siempre incluir nombre del cliente y fecha. Si el cliente no tiene nombre de empresa
> definido, usar el nombre de contacto.

---

### BLOQUE: Introducción

```markdown
## Introducción

[2–4 párrafos que cumplan estas funciones:]

Párrafo 1 — Contexto del problema:
Describir brevemente los desafíos actuales del cliente mencionados en la llamada. Ser específico
(ej: "la gestión de consultas a través de múltiples canales", "la falta de respuesta inmediata
fuera de horario", etc.). Usar los puntos de dolor reales mencionados.

Párrafo 2 — Propuesta de solución:
Presentar la solución propuesta a alto nivel. Mencionar el tipo de agente o sistema,
qué automatiza y qué beneficio trae. No entrar en detalles técnicos aquí.

Párrafo 3 (opcional) — Escalabilidad / visión a futuro:
Si el cliente mencionó planes de crecimiento, migración de sistemas, o expansión, incluirlo.

Párrafo 4 (opcional) — Cierre orientado al valor:
Una frase que conecte la solución con el objetivo de negocio del cliente.
```

> Regla: La introducción debe hablar DEL CLIENTE, no de la agencia. Evitar lenguaje genérico.
> Personalizar siempre usando información de la transcripción.

---

### BLOQUE: Desarrollo Inicial

```markdown
## 1. Desarrollo Inicial

### 1.1 Implementación del Agente de IA [Nombre descriptivo del agente]

**Diseño y desarrollo:** [Descripción de 1–2 oraciones sobre qué se va a construir.]

**Capacidades del Agente:**

- [Funcionalidad 1, con detalle específico al cliente]
- [Funcionalidad 2]
- [Funcionalidad N...]

**Integraciones:**

- **[Tecnología 1]:** [Para qué se usa en este contexto específico]
- **[Tecnología 2]:** [Para qué se usa]
- **[Tecnología N]:** [Para qué se usa]

**Tiempo de desarrollo:** [X – X semanas]
**Costo:** USD [MONTO]
```

> Reglas para las integraciones más comunes:
> - **n8n**: backend, flujos de automatización, lógica del agente
> - **OpenAI API**: modelo de lenguaje, procesamiento de consultas
> - **ManyChat / ChatRace**: frontend de inbox, gestión de conversaciones, notificaciones
> - **Supabase**: memoria, almacenamiento de usuarios e interacciones
> - **Airtable**: CRM, dashboard de métricas
> - **WhatsApp Business API**: canal de WhatsApp
> - **Meta API**: Instagram y Facebook
> - **HubSpot / Odoo**: CRM/ERP del cliente
> - **ElevenLabs**: síntesis de voz (para agentes de voz)
> - **Twilio / Vapi**: telefonía (para agentes de voz)

> Si hay múltiples módulos (automatizaciones, CRM, dashboard), crear subsecciones 1.2, 1.3, etc.

---

### BLOQUE: Alcance General (para agentes de voz o soluciones complejas)

```markdown
## Alcance General

El Agente [de Voz / Conversacional] operará [canal/contexto], con las siguientes metas:

- **[Meta 1]:** [Descripción]
- **[Meta 2]:** [Descripción]
- **[Meta N]:** [Descripción]
```

> Usar este bloque cuando el proyecto es suficientemente complejo como para necesitar un
> resumen ejecutivo de objetivos antes de entrar en funcionalidades.

---

### BLOQUE: Funcionalidades del Agente (detalle expandido)

Usar cuando el proyecto amerita desplegar cada funcionalidad con su nombre, descripción y
ejemplo. Estructura por ítem:

```markdown
## Funcionalidades del Agente de IA

### 1. [Nombre de la Funcionalidad]

**Descripción:** [Qué hace esta funcionalidad en una oración.]

**Detalles:**
- [Detalle técnico o de comportamiento]
- [Ejemplo concreto: "Cliente: '...' → Agente: '...'"]
- [Otro detalle relevante]

### 2. [Nombre de la Funcionalidad]
[...]
```

> Funcionalidades comunes a incluir según el tipo:
> - Agente conversacional: Atención multicanal, Reconocimiento de intenciones, Acceso a base
>   de datos, Memoria conversacional, Recomendaciones personalizadas, Seguimiento automático,
>   Escalamiento a humanos, Gestión de inbox, Soporte multimedia
> - Agente de voz: Recepción de llamadas, Gestión de consultas triviales, Transferencia a humanos,
>   Soporte bilingüe, Captura de datos, Dashboard de métricas

---

### BLOQUE: Cronograma de Implementación

```markdown
## Cronograma de Implementación

**Duración Total:** [X–X semanas]

- **Días 1–5:** [Qué se hace en la primera etapa. Ej: configuración, versión de prueba inicial]
- **Semana 1–2:** [Desarrollo principal de funcionalidades]
- **Semana 3–4:** [Ajustes, integración final, capacitación y lanzamiento]

> Incluye [X] versiones de prueba para ajustes según feedback.
```

> Incluir este bloque siempre que el proyecto dure más de 2 semanas o sea técnicamente complejo.

---

### BLOQUE: Costos / Inversión

Para proyectos estándar:

```markdown
## Costos

| Componente | Costo (USD) | Tiempo |
|---|---|---|
| [Módulo 1] | [MONTO] | [X semanas] |
| [Módulo 2] | [MONTO] | [X semanas] |
| **Total Desarrollo Inicial** | **[TOTAL]** | **[X–X semanas]** |
```

Para agentes de voz, agregar costos variables:

```markdown
### Costos Fijos Operativos (cubiertos por [CLIENTE])

| Servicio | Costo |
|---|---|
| Costo por LLM | USD 0.050 / min |
| Costo por Voice Engine (ElevenLabs) | USD 0.070 / min |
| Costo por telefonía | USD 0.015 / min |
| **Total por minuto** | **USD 0.135 / min** |
| Dashboard Airtable | USD 24 / mes |
| Línea telefónica (Twilio) | ~USD 1.5 / mes |

> **Ejemplo:** 100 llamadas de 3 minutos = USD 40.5 / mes en costos de uso.
```

---

### BLOQUE: Mantenimiento Mensual

```markdown
## [2 ó 3]. Mantenimiento Mensual

### [X.1] Soporte Técnico

- Resolución de incidencias en [tecnologías del proyecto].
- Monitoreo de conversaciones para detectar errores, respuestas fuera de tono o problemas con
  las integraciones.
- Ajustes en flujos conversacionales según feedback del equipo (ej: "[ejemplo específico al
  cliente]").

### [X.2] Actualización de Funcionalidades

- Incorporación de nuevas instrucciones o funcionalidades según necesidades emergentes.
- Optimización de respuestas para mejorar la tasa de conversión.
- [Si aplica: migración futura a otro sistema, ej: "Migración al ERP Odoo cuando [CLIENTE] lo necesite."]

### [X.3] Capacitación y Seguimiento

- Capacitación inicial al equipo de [CLIENTE] sobre la gestión de derivaciones y el uso de la
  solución.
- Grupo de WhatsApp exclusivo con el el equipo para resolver dudas en tiempo real,
  proponer mejoras y coordinar ajustes.
- Reuniones semanales (opcionales) para evaluar el rendimiento y definir nuevas funcionalidades.

### [X.4] Cobertura de Costos Fijos

- la agencia cubrirá al 100% los gastos de los sistemas utilizados (n8n, ManyChat/ChatRace,
  OpenAI, entre otros).

**Costo del mantenimiento mensual: USD [MONTO] / mes**

> El mantenimiento comenzará a cobrarse a partir del segundo mes de implantada la solución.
```

> Para proyectos grandes, ofrecer dos opciones de mantenimiento:
> - **Opción 1: Acompañamiento por la agencia** — con soporte completo, costo mensual
> - **Opción 2: Sin acompañamiento (autónomo)** — USD 0 / mes, la solución se transfiere al cliente

---

### BLOQUE: Implementaciones Futuras

```markdown
## Implementaciones Futuras

Sugerimos considerar las siguientes funcionalidades escalables para fases posteriores:

- **[Funcionalidad futura 1]:** [Descripción breve de qué agrega y por qué es relevante]
- **[Funcionalidad futura 2]:** [Descripción breve]
- **[Funcionalidad futura N]:** [Descripción breve]
```

> Incluir solo si en la llamada se mencionaron planes de crecimiento o si hay oportunidades
> claras de expansión. Ejemplos comunes:
> - Integración con ERP/CRM adicional
> - Gestión avanzada de comentarios en RRSS
> - Audios personalizados / clonación de voz
> - Dashboard de métricas avanzado
> - Envío de mensajes en frío masivos
> - Automatización de cobranza o facturación
> - Soporte para nuevos canales (web, Telegram)

---

### BLOQUE: Resumen / Total del Proyecto

```markdown
## Resumen del Proyecto

| Concepto | Monto |
|---|---|
| Desarrollo Inicial | USD [MONTO] |
| Mantenimiento Mensual | USD [MONTO] / mes |
| Tiempo de Entrega | [X–X semanas] |
```

> Incluir este bloque cuando el presupuesto tiene múltiples módulos o es extenso. En proyectos
> simples se puede omitir (el costo ya queda claro en cada sección).

---

### BLOQUE: Notas Adicionales (SIEMPRE incluir)

```markdown
## Notas Adicionales

- **Condiciones de pago:** Para comenzar el proyecto, solo debe abonarse el **50% del total del
  desarrollo inicial**. El 50% restante se abona al momento de implantar la solución.
- **Medios de pago:** PayPal, Payoneer, Binance, MercadoPago [incluir los relevantes según el
  cliente].
- **Versión de prueba:** Durante el desarrollo se entregará una versión de prueba del Agente
  para que el equipo pueda interactuar, simular consultas y proporcionar feedback antes de la
  entrega final.
- **Reuniones de avance:** Se recomienda una reunión semanal para revisión de avances y
  asegurar la transferencia de conocimientos.
- **Propiedad de la solución:** Todos los datos, flujos e integraciones son propiedad de
  [CLIENTE].
- **Flexibilidad:** La solución es adaptable a cambios futuros. Cualquier funcionalidad
  adicional de tamaño considerable que esté fuera del alcance del mantenimiento mensual será
  cotizada por separado.
- [Agregar notas específicas surgidas de la llamada, ej: "El scraping de leads inicial está
  incluido de forma gratuita."]
```

---

### BLOQUE: Próximos Pasos (opcional)

```markdown
## Próximos Pasos

En caso de querer avanzar con la propuesta:

1. Confirmación del proyecto vía WhatsApp (+598 92 314 547).
2. Envío del formulario de la agencia con preguntas clave sobre la empresa y el funcionamiento
   esperado del Agente.
3. [Paso adicional si aplica, ej: "Reunión inicial para pulir la base de conocimiento."]
```

---

## Reglas de Estilo y Tono

### Tono General
- Profesional, pero cercano. Nunca frío ni excesivamente técnico.
- Orientado al valor de negocio, no solo a la tecnología.
- Primera persona del plural ("proponemos", "implementaremos", "nos encargamos").

### Personalización
- **Usar el nombre del cliente** en toda la propuesta, no solo en el encabezado.
- **Mencionar sus problemas concretos** en la introducción y en los beneficios.
- **Adaptar los ejemplos** de conversación al rubro del cliente (ej: para una clínica dental,
  usar ejemplos de citas y horarios; para una tienda, usar productos y stock).
- **Adaptar el tono del agente** según lo que mencionó el cliente (voseo, formal, emojis, etc.).

### Uso de Emojis
- No usar emojis en el presupuesto en sí (es un documento formal).
- Sí pueden aparecer en los ejemplos de conversación del agente dentro del presupuesto.

### Listas vs. Párrafos
- Las funcionalidades siempre van en listas con viñetas.
- La introducción y los beneficios van en párrafos o listas según la longitud.
- Los costos siempre van en tablas cuando hay más de un ítem.

---

## Información que Siempre Pedir si Falta

Si la transcripción no provee estos datos, preguntar al usuario antes de generar el presupuesto:

1. **¿Cuál es el nombre de la empresa cliente?**
2. **¿Qué canales de comunicación usa actualmente?** (WhatsApp, Instagram, teléfono, etc.)
3. **¿Tiene algún CRM, ERP o plataforma existente?** (HubSpot, Odoo, Shopify, etc.)
4. **¿Cuál es el volumen estimado de consultas/llamadas por mes?**
5. **¿Hay preferencia de método de pago?** (para incluirlo en notas)
6. **¿El cliente necesita agente de voz o conversacional (texto)?**

Si falta información no crítica, proponer un valor estimativo indicando claramente que es
una suposición. Nunca inventar funcionalidades que no surgieron de la llamada.

---

## Checklist Final Antes de Entregar

Antes de mostrar el presupuesto al usuario, verificar:

- [ ] El nombre del cliente aparece en el encabezado y al menos 2 veces más en el texto
- [ ] La introducción menciona problemas concretos de la llamada (no genéricos)
- [ ] Todos los costos están en USD y son coherentes con los rangos de referencia
- [ ] Las condiciones de pago (50/50) están incluidas en Notas Adicionales
- [ ] El tiempo de desarrollo es consistente con la complejidad del proyecto
- [ ] El mantenimiento mensual está desagregado (soporte, actualizaciones, costos fijos)
- [ ] Las funcionalidades mencionadas en la llamada están todas reflejadas
- [ ] El formato es Markdown limpio, listo para copiar a Notion
- [ ] No hay secciones vacías ni placeholders `[SIN COMPLETAR]` visibles
- [ ] El output NO es un archivo externo — está en el chat directamente

---

## Ejemplos de Patrones Recurrentes

### Frase de apertura para Introducción (agente conversacional)
> "Este presupuesto detalla una solución integral diseñada específicamente para abordar los
> desafíos actuales de [CLIENTE], como [PROBLEMA 1], [PROBLEMA 2] y [PROBLEMA 3]."

### Frase de apertura para Introducción (agente de voz)
> "Proponemos un Agente de Inteligencia Artificial de Voz para [CLIENTE]. Este Agente,
> diseñado para automatizar [PROCESO], optimizará [BENEFICIO PRINCIPAL], reduciendo la
> carga de [RECURSO HUMANO AFECTADO]."

### Beneficios tipo para incluir en desarrollo o introducción
- Reducción significativa de la carga de trabajo del equipo de [CLIENTE]
- Mejora en la inmediatez en la atención, capturando clientes fuera de horario
- Aumento de conversiones al ofrecer respuestas personalizadas
- Mayor orden en la gestión de consultas, con derivaciones inteligentes
- Respuestas 24/7 sin intervención humana para consultas repetitivas

### Nota de mantenimiento para agente de voz
> "En caso de que [CLIENTE] opte por mantener la solución de forma autónoma, la agencia se
> asegurará de que la transferencia sea exitosa. En ambos casos, la propiedad de la solución
> pertenecerá a [CLIENTE]."

---

## Ejemplos de Referencia
Ver carpeta `examples/` para presupuestos reales que ilustran la aplicación de este skill.

*Skill mantenido por la agencia — Versión 1.0*
