# Extensión Agente SyS — Captación de Leads desde Meta Ads

**Propuesta de alcance e inversión**

**Fecha:** 3 de junio de 2026
**Para:** Edgardo · Sistemas y Soluciones
**De:** la agencia
**Referencia:** extensión del proyecto base *Agente Conversacional Etapa 2* (en producción)

---

## Contexto

Esta propuesta responde al pedido concreto que nos planteaste:

> *"En los anuncios de Meta hay una mini conversación que se autocontesta. Hoy uno arma respuestas hardcodeadas para cuando el cliente pregunta 'hola, ¿qué precio tiene?'. Lo que quiero es aprovechar eso pero que la respuesta la dé la IA de forma más humana, y que pueda seguir el hilo de la conversación desde ahí. Porque probablemente todos los contactos que vienen ahora van a venir de Meta."*

Tiene mucho sentido hacerlo ahora: el agente conversacional ya está construido, validado y operando en producción. Lo que falta es **conectar la puerta de entrada de los anuncios al agente** para que cada lead que llega de Meta sea recibido por la IA en lugar de quedar en un árbol rígido de respuestas pre-armadas. Así capitalizamos la inversión publicitaria que ya están haciendo y el agente que ya está pago: cada click en un anuncio cae directo en una conversación natural, con seguimiento del hilo y derivación al comercial cuando corresponde.

---

## 1. Qué construimos

### 1.1 Flow de entrada Meta Ads en ManyChat

Resuelve: que cualquier persona que haga click en un anuncio de Meta caiga en un flujo dedicado en ManyChat, y NO en el árbol genérico de respuestas hardcodeadas.

- Welcome message corto y alineado al tono del agente
- 3 a 5 *quick-replies* a definir junto con vos (ejemplos: "Catálogo / Asesoramiento técnico / Servicio técnico"), siempre evitando que alguno mencione precios
- *Custom field* nuevo en ManyChat (`origen = meta_ads`) que viaja con la conversación durante todo el ciclo de vida del lead
- (Si Meta lo expone vía Referral) captura del `meta_ad_id` específico para trazabilidad por anuncio

### 1.2 Enriquecimiento del payload al webhook n8n

Resuelve: que el agente reciba contexto del origen del lead apenas arranca la conversación, sin pedirle al cliente que aclare de dónde viene.

- Modificación del payload que ManyChat envía al webhook n8n para incluir el `origen`, la *quick-reply* seleccionada por el cliente, y el `meta_ad_id` si está disponible
- Ajuste del nodo `Normalize Payload` para propagar esos campos al resto del flujo
- Inyección de la variable `ORIGEN_LEAD` en el User Message del AI Agent

### 1.3 Contextualización del agente al recibir tráfico de anuncios

Resuelve: que la conversación se sienta natural desde el primer mensaje, sin que el cliente tenga que repetir lo que ya dijo en el anuncio.

- Actualización del System Prompt del agente (versión 2.3) con una regla operativa nueva:
  - Cuando llega un lead con `ORIGEN_LEAD = meta_ads:<asunto>`, el agente arranca directamente sobre ese asunto (catálogo, asesoramiento, servicio técnico) sin pedir clarificación inicial
  - Se mantiene firme la política actual: no se entregan precios en chat — se confirma interés, se relevan datos, se deriva al comercial
- Re-testing de 4-5 casos de conversación que arrancan desde cada *quick-reply* para verificar tono y derivación

### 1.4 Tracking básico de origen Meta Ads

Resuelve: poder saber cuántos leads están entrando desde la pauta publicitaria y diferenciarlos del resto, para que puedas evaluar el rendimiento de las campañas.

- Campo `entry_source` agregado a los logs internos del agente en Supabase (queryable)
- Tag explícito *"Origen: Meta Ads"* en el mail de notificación de lead que ya recibís hoy en `info@sistemasysoluciones.com`
- Pestaña nueva en la planilla "SyS – Leads" que ya usamos, con filtro pre-armado de los leads Meta Ads del periodo

### 1.5 Consultoría operativa (1-2 horas incluidas)

Resuelve: que vos, que estás gestionando las campañas Meta Ads vos mismo, tengas claridad sobre cómo conectar el CTA de cada anuncio al flow que armamos.

- Sesión grabada (o presencial via WhatsApp/Meet) explicándote paso a paso cómo configurar el botón "Enviar mensaje" del anuncio para que apunte al flow nuevo de ManyChat
- Sugerencias sobre los 3-5 *quick-replies* más probables para tu rubro
- Quedan disponibles para futuras campañas: una vez configurado, podés crear cuantos anuncios quieras apuntando al mismo flow sin volver a tocar nada técnico

---

## 2. Qué queda fuera de alcance

Para que quede claro qué incluye y qué no esta propuesta:

- ❌ Creación, optimización o gestión de las campañas Meta Ads en sí mismas (eso lo seguís manejando vos)
- ❌ Diseño creativo de los anuncios (imágenes, copy publicitario)
- ❌ Conversions API de Meta para tracking server-side de conversiones → ver "Implementaciones futuras"
- ❌ Reporte automatizado semanal de ROI por anuncio o campaña → ver "Implementaciones futuras"
- ❌ Retargeting via WhatsApp masivo a leads no respondidos → ver "Implementaciones futuras"

---

## 3. Dependencias del cliente

Para arrancar necesitamos:

- ✅ Acceso al Business Manager de Meta de Sistemas y Soluciones (admin o editor según permiso disponible)
- ✅ Al menos 1 campaña Meta Ads activa o lista para activarse, para hacer la prueba E2E real
- ✅ Aprobación conjunta de los 3 a 5 *quick-replies* que vamos a usar como puerta de entrada
- ✅ Confirmación del mail (y opcionalmente Telegram) donde van a llegar las notificaciones de leads Meta Ads

(El plan de ManyChat Pro ya está activo desde la implementación del agente actual — no hace falta nada nuevo ahí.)

---

## 4. Cronograma de implementación

Estimamos **una semana calendario** de trabajo neto, distribuido así:

| Día | Tarea |
|---|---|
| 1 | Reunión de kick-off · acceso al Business Manager · definición conjunta de *quick-replies* |
| 2 | Setup del Flow Meta Ads en ManyChat (welcome message + *quick-replies* + *custom fields*) |
| 3 | Ajuste del payload n8n + Normalize Payload + propagación al AI Agent |
| 4 | System Prompt v2.3 + tracking en Supabase + tag en mail + pestaña nueva en planilla |
| 5 | Smoke tests E2E con una campaña piloto + ajustes según resultado real |
| 6 | Handoff: mini-guía operativa de 1-2 páginas para que sepas cómo replicar a futuro |

Asume que conseguimos accesos y *quick-replies* aprobados dentro de los primeros 48hs.

---

## 5. Inversión

Te presentamos dos escenarios según el estado de tu cuenta con la agencia:

### Escenario A — Sin plan de mantenimiento activo

Esta extensión se cotiza como un proyecto único y cerrado.

| Concepto | Monto |
|---|---|
| Desarrollo de la extensión completa (puntos 1.1 a 1.5) | **USD 380** |
| Condiciones de pago | 50% al iniciar · 50% al entregar |
| Tiempo de entrega | 1 semana |

### Escenario B — Con plan de mantenimiento activo

> Esta extensión está **incluida dentro del plan de mantenimiento mensual** de la agencia. **No representa inversión adicional.**

El plan mensual cubre extensiones de complejidad equivalente a esta, ajustes al agente según data real, monitoreo del flow productivo y soporte ante incidentes (más detalle en la sección siguiente).

---

## 6. Plan de mantenimiento mensual (informativo)

Para los clientes que tienen el plan mensual activo, lo que cubre la agencia es:

- **Soporte técnico** ante incidentes del agente, ManyChat, n8n o integraciones (Airtable, Supabase, OpenAI)
- **Actualizaciones del agente** según evolución del negocio: cambios de catálogo, nuevas tecnologías, nuevos canales, ajustes de tono
- **Inclusión de extensiones** como esta dentro del retainer (no se cobran como proyectos separados)
- **Capacitación y seguimiento operativo** con tu equipo (canal directo de WhatsApp con la agencia para dudas en tiempo real)
- **Cobertura de los costos fijos** de infraestructura: licencias n8n, tokens de OpenAI, Supabase, ManyChat (lo que aplique)

Si querés que te pase el detalle del plan mensual, decime y lo coordinamos aparte de esta propuesta.

---

## 7. Implementaciones futuras

Esta extensión deja la base lista para varios upgrades que tiene mucho sentido sumar a medida que el volumen de leads desde Meta Ads crezca:

1. **Conversions API de Meta (tracking server-side)** — *USD 350 a 500 únicos + componente mensual.* Le devuelve a Meta la información de cuándo un lead pasa a "calificado" o "derivado", de modo que el algoritmo de Meta optimiza tus campañas hacia conversiones reales (no solo clicks). Mejora la eficiencia de la pauta entre un 15% y un 30% según el caso.

2. **Reporte semanal automatizado de ROI Meta Ads** — *USD 200 a 300 únicos + componente mensual.* Cron semanal que cruza los leads Meta Ads con el periodo, te llega por mail con: cantidad de leads, cantidad de derivaciones, costo por lead estimado y ranking por *quick-reply*.

3. **Segmentación de respuesta por anuncio específico** — *USD 250 a 400 únicos.* Si tenés un anuncio sobre Plotters de Corte y otro sobre DTF, el agente arranca cada conversación dirigida al producto correcto. Requiere mapeo de `meta_ad_id` → contexto del anuncio.

4. **Retargeting via WhatsApp** — *USD 400 a 600 únicos + componente mensual.* Broadcasts segmentados a leads Meta Ads que no respondieron en 7/14/30 días, dentro del marco de la política de WhatsApp Business. Útil cuando hay volumen suficiente para que valga el esfuerzo.

Si alguna de estas implementaciones te interesa más adelante, te armamos cotización detallada caso por caso.

---

## 8. Próximos pasos

1. Confirmás la propuesta y elegimos escenario (A o B según corresponda)
2. Coordinamos el acceso al Business Manager de Meta
3. Definimos juntos los 3-5 *quick-replies* iniciales
4. Arrancamos dentro de los 7 días posteriores a la confirmación
5. Entrega en 1 semana de trabajo

Cualquier duda sobre alcance, cronograma o inversión, escribime y la resolvemos antes de avanzar.

---

*Propuesta preparada por la agencia para Sistemas y Soluciones · Junio 2026*
