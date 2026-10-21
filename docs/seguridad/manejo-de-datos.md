# Manejo de Datos y Seguridad — la agencia

**Preparado para:** [NOMBRE DEL CLIENTE]
**Versión:** 1.0
**Fecha:** [DD/MM/AAAA]

---

## 1. Introducción y Alcance

Este documento describe cómo la agencia recopila, procesa, almacena y protege los datos de usuarios finales en el contexto de los agentes conversacionales que opera en nombre de sus clientes. Aplica a todos los proyectos activos en producción.

**Roles:**
- **la agencia** actúa como **procesador de datos**: opera la infraestructura técnica y los flujos de automatización siguiendo las instrucciones del cliente.
- **El cliente** es el **responsable del tratamiento** ante sus usuarios finales: define el propósito del procesamiento y tiene la obligación frente a la regulación local aplicable.

Este documento no reemplaza el acuerdo contractual entre la agencia y el cliente, que puede incluir cláusulas adicionales de confidencialidad o manejo de datos.

---

## 2. Qué Datos Procesamos

### 2.1 Datos del usuario final (leads y clientes del cliente)

Los agentes conversacionales de la agencia procesan exclusivamente la información que los usuarios finales comparten de forma voluntaria durante una conversación. Esto incluye:

- Nombre y apellido
- Número de teléfono (WhatsApp) o nombre de usuario (Instagram, Facebook)
- Dirección de correo electrónico (cuando el usuario la proporciona)
- Historial de mensajes completo dentro del canal de mensajería
- Estado en el proceso de venta o servicio (ej: "consultó", "calificado", "reservó")
- Datos de reservas o turnos (fecha, hora, servicio solicitado), cuando aplica al proyecto

### 2.2 Datos que no recopilamos

la agencia no solicita ni procesa:

- Datos financieros (números de tarjeta, cuentas bancarias, CBU/CLABE)
- Documentos de identidad (DNI, pasaporte, CURP)
- Contraseñas o credenciales de los usuarios finales
- Datos biométricos

---

## 3. Arquitectura de Datos

### 3.1 Flujo general

Un mensaje de un usuario final recorre el siguiente camino:

1. **Usuario final** escribe en WhatsApp, Instagram o Facebook.
2. **ManyChat** (plataforma de mensajería) recibe el mensaje y lo reenvía vía webhook.
3. **n8n** (orquestador, alojado en servidor privado de la agencia) recibe el mensaje y consulta el historial del contacto en el CRM.
4. **Modelo de lenguaje** (OpenAI GPT-4 o Google Gemini, según el proyecto) procesa el texto del mensaje junto con el contexto del contacto y genera una respuesta.
5. **n8n** guarda la actualización del historial en el CRM y envía la respuesta de vuelta vía ManyChat.
6. **Usuario final** recibe la respuesta en el canal original.

### 3.2 Dónde se almacena la información

| Sistema | Qué guarda | Quién lo controla |
|---|---|---|
| **Airtable** | CRM: datos del contacto, historial de conversación, estado de conversión | la agencia + cliente (acceso compartido) |
| **PostgreSQL** (DigitalOcean) | Memoria conversacional del agente (contexto reciente) | la agencia (servidor privado) |
| **ManyChat** | Inbox de mensajería, datos básicos del contacto en el canal | ManyChat (plataforma SaaS) |
| **OpenAI / Google Gemini** | Procesamiento del mensaje para generar la respuesta | OpenAI / Google (sin retención permanente, ver sección 4) |

### 3.3 Servidores propios

Los servicios de n8n y PostgreSQL corren en servidores de DigitalOcean administrados directamente por la agencia. Los entornos de cada cliente están aislados: no se comparten bases de datos ni flujos entre distintos clientes.

---

## 4. Quién Accede a los Datos

| Actor | Nivel de acceso |
|---|---|
| **la agencia (equipo técnico)** | Acceso completo a n8n, PostgreSQL y Airtable para operación, mantenimiento y mejora de los agentes |
| **El cliente** | Acceso a su propia base en Airtable (leads y conversaciones). El nivel de permisos se define al inicio del proyecto |
| **OpenAI / Google Gemini** | Procesan el texto de los mensajes para generar respuestas. Por política de API, no almacenan datos de clientes de forma permanente ni los utilizan para entrenar modelos |
| **ManyChat** | Plataforma SaaS que gestiona el inbox de mensajería. Sus términos y política de privacidad aplican de forma independiente a los de la agencia |
| **Terceros adicionales** | Según el proyecto (ej: Google Calendar, Kommo, GoHighLevel), aplican las políticas de privacidad de cada plataforma |

**Sobre OpenAI y Google:** ambos proveedores tienen compromisos explícitos de que los datos enviados vía API no se usan para entrenar sus modelos ni se retienen de forma permanente. Esta información puede verificarse en sus respectivos términos de servicio para API.

---

## 5. Medidas de Seguridad Implementadas

### Lo que existe hoy

- **Credenciales almacenadas de forma segura:** las API keys, tokens y contraseñas se guardan como variables cifradas dentro de n8n. No aparecen en código fuente ni en repositorios públicos o privados.
- **Acceso a servidores por llave SSH:** los servidores de DigitalOcean no admiten acceso por contraseña; solo por llave privada controlada por el equipo técnico de la agencia.
- **Infraestructura propia (self-hosted):** n8n corre en servidores de la agencia. Los flujos de automatización y la lógica del agente no pasan por plataformas de terceros.
- **Repositorios privados:** el código fuente de los proyectos está en repositorios privados en GitHub, con acceso restringido al equipo técnico.
- **Aislamiento por cliente:** cada cliente tiene su propia base de datos en Airtable y su propio entorno en PostgreSQL. Los datos de un cliente no son accesibles desde el entorno de otro.
- **Permisos por rol en Airtable:** el acceso del cliente a su base de datos se configura con permisos granulares (lectura, edición) por invitación de email.

### En desarrollo

- Política formal de retención y eliminación de datos con tiempos explícitos documentados.
- Logs de auditoría de acceso que registren quién consultó o modificó datos y cuándo.
- Documentación de procedimientos de backup y recuperación ante desastres.

---

## 6. Responsabilidades Compartidas

la agencia y el cliente comparten responsabilidades sobre distintas capas del sistema. Esta tabla clarifica qué corresponde a cada parte:

| Área | Responsable |
|---|---|
| Seguridad del servidor n8n y PostgreSQL | la agencia |
| Seguridad del acceso a Airtable (permisos internos del cliente) | la agencia + cliente |
| Políticas de datos de WhatsApp / Meta / ManyChat | Plataforma (tercero) |
| Políticas de datos de OpenAI / Google Gemini | Proveedor de IA (tercero) |
| Informar a usuarios finales que interactúan con un agente automatizado | Cliente |
| Obtener el consentimiento de los usuarios finales para el procesamiento | Cliente |
| Cumplimiento regulatorio local (Ley de Protección de Datos Personales, GDPR, etc.) | Cliente (la agencia como procesador bajo su instrucción) |

**Nota sobre WhatsApp Business API:** Meta requiere explícitamente que las empresas que usan WhatsApp Business API informen a sus usuarios que pueden estar interactuando con un sistema automatizado. Esta responsabilidad recae sobre el cliente.

---

## 7. Retención y Eliminación de Datos

- Al concluir la relación contractual, la agencia entrega al cliente un export completo de sus datos (Airtable + PostgreSQL) en un formato accesible (CSV / JSON) y elimina el acceso de la agencia a esa información.
- Los tiempos específicos de retención durante el contrato y el proceso detallado de eliminación se documentan en el acuerdo contractual con cada cliente.
- Solicitudes de eliminación de datos de un usuario final específico (ej: derecho al olvido) deben canalizarse por el cliente a la agencia vía el canal de soporte asignado al proyecto.

---

## 8. Ante un Incidente de Seguridad

la agencia monitorea los agentes en producción de forma activa. Ante un incidente que afecte la integridad, confidencialidad o disponibilidad de los datos de un cliente:

1. la agencia notifica al cliente dentro de las **24 horas** de detectado el incidente.
2. Se comparte una descripción del incidente: qué datos se vieron afectados, cómo ocurrió y qué pasos se están tomando.
3. La respuesta se coordina de forma directa con el equipo del cliente.

Los logs de n8n permiten rastrear el flujo de cada conversación y detectar anomalías de acceso o comportamientos fuera de lo esperado.

---

## 9. Contacto

Para consultas sobre manejo de datos, privacidad o seguridad relacionadas con un proyecto de la agencia:

- **Email:** [email@la agencia.ai]
- **WhatsApp:** +598 92 314 547

Las consultas específicas sobre los datos de un proyecto particular se atienden con el responsable de cuenta asignado.

---

*la agencia — Documento de uso interno y compartible con clientes. Versión 1.0.*
*Para personalizar: reemplazar `[NOMBRE DEL CLIENTE]` y `[DD/MM/AAAA]` en el encabezado.*
