# Manejo de Datos y Seguridad — ALMIA

**Preparado para:** Dialectika · Pablo
**Plataforma:** ALMIA — Ecosistema de Dashboards
**Versión:** 2.0
**Fecha:** 14/05/2026

---

## 1. Introducción y Alcance

Este documento describe cómo la agencia recopila, procesa, almacena y protege los datos dentro del ecosistema ALMIA: la plataforma de salud mental con agente de IA conversacional y paneles de gestión para usuarios internos (Admin Dashboard) y clientes corporativos (Dashboard B2B).

**Qué cubre este documento:**

- El agente de IA conversacional operado en n8n (ya en funcionamiento), que procesa los mensajes de los usuarios vía OpenAI.
- El ecosistema de dashboards en construcción: Admin Dashboard (uso interno de Dialectika) y Dashboard Corporativo B2B (para equipos de RRHH).
- La base de datos Supabase que centraliza los datos de ambos dashboards.

**Qué no cubre este documento:**

La interfaz web donde los usuarios finales escriben sus mensajes es administrada por un desarrollador externo independiente. Su configuración, seguridad y responsabilidades de datos corresponden a ese desarrollador y están fuera del alcance de la agencia.

**Roles:**

- **la agencia** actúa como **encargado del tratamiento**: opera la infraestructura técnica (agente n8n, base de datos Supabase, dashboards) siguiendo las instrucciones de Dialectika.
- **Dialectika** es el **responsable del tratamiento** ante sus usuarios finales: define el propósito del procesamiento y asume las obligaciones regulatorias frente a la ley chilena.

ALMIA procesa datos de salud mental, que la **Ley N° 21.719 de Protección de Datos Personales** (Chile, vigente 2024) clasifica como **datos sensibles**. Esta clasificación exige consentimiento explícito e informado, finalidad específica del tratamiento, y medidas de seguridad proporcionales al nivel de riesgo.

---

## 2. Qué Datos Maneja ALMIA

### 2.1 Datos de identidad

Recopilados de usuarios B2C y administradores B2B durante el registro y uso de la plataforma:

- Dirección de correo electrónico
- Plan de suscripción activo (Free / Basic / Pro para B2C; plan corporativo para B2B)
- Fecha de registro
- Rol en la plataforma (usuario B2C, administrador de empresa B2B)
- Correos corporativos de empleados (cuando RRHH carga una lista de invitaciones)

### 2.2 Datos de sesiones de salud mental

Esta es la categoría más sensible que maneja ALMIA. Incluye el contenido generado durante las conversaciones del usuario con el agente de IA:

- Contenido textual de los mensajes intercambiados durante una sesión
- Clasificación temática generada por IA (ej: estrés laboral, ansiedad, burnout)
- Registro de derivaciones de crisis activadas (cuando el agente derivó al 131, 133 o \*4141)
- Muestras anonimizadas de conversaciones para control de calidad del agente (sin PII — Información Personal Identificable)

### 2.3 Datos agregados y anónimos (Dashboard B2B)

El Dashboard Corporativo muestra **exclusivamente** datos procesados, agregados y sin identificación individual:

- Distribución porcentual de temáticas del mes
- Mapa de calor horario de uso
- Indicador general de carga emocional del equipo
- Tasa de activación de licencias (usuarios activos vs. licencias contratadas)

**Regla técnica de privacidad:** si una empresa tiene menos de 10 empleados activos, o si un filtro por departamento resulta en menos de 10 personas, el Termómetro Emocional se oculta automáticamente. Esta restricción está implementada en código — ningún administrador de RRHH puede saltearla.

### 2.4 Datos operativos B2B

Información de las empresas cliente:

- Nombre de la empresa
- Plan contratado y fecha de renovación
- Límite de licencias (cupos) y estado de cada invitación
- Tickets de soporte generados

### 2.5 Qué ALMIA no recopila

- Contraseñas en texto plano (nunca se almacenan; solo hashes seguros vía Supabase Auth)
- Datos financieros completos (tarjetas de crédito, cuentas bancarias)
- Datos biométricos
- Documentos de identidad (RUT, pasaporte)
- Grabaciones de audio o video

---

## 3. Arquitectura de Datos

### 3.1 Flujo de datos en ALMIA

1. **Usuario final** escribe un mensaje en la interfaz web de ALMIA (desarrollada y administrada por tercero externo).
2. La web envía el mensaje vía **webhook** al agente en **n8n** (servidor de la agencia en DigitalOcean).
3. **n8n** envía el contenido del mensaje a la **API de OpenAI** (GPT-4o) para generar la respuesta del agente.
4. **OpenAI** procesa el mensaje y devuelve la respuesta a n8n. El contenido de la conversación pasa por los servidores de OpenAI en este paso.
5. **n8n** almacena los datos relevantes de la sesión en **Supabase** (metadatos, clasificación temática, logs de crisis) y devuelve la respuesta a la interfaz web.
6. **Los dashboards** leen desde Supabase para mostrar métricas, gestión de usuarios, logs y analítica B2B.

### 3.2 Dónde se almacena cada dato

| Sistema | Qué guarda | Controlado por |
|---|---|---|
| **Supabase Database** | Perfiles de usuario, metadatos de sesión, clasificaciones temáticas, logs de crisis, datos de empresas B2B, tickets de soporte | la agencia (configuración y acceso técnico) + Dialectika (gestión de datos) |
| **Supabase Auth** | Tokens de sesión JWT, emails de login, roles de usuario, refresh tokens | Supabase (SaaS) bajo configuración de la agencia |
| **n8n** (DigitalOcean) | Logs de ejecución de workflows, credenciales de integración cifradas | la agencia exclusivamente |
| **OpenAI API** | Procesa el texto de cada mensaje para generar la respuesta del agente. Por política de API, no almacena el contenido de forma permanente ni lo usa para entrenar modelos (ver sección 4.3) | OpenAI Inc. (tercero) |

### 3.3 Dato clave: el contenido de las sesiones pasa por OpenAI

El contenido textual de cada conversación que un usuario tiene con el agente de ALMIA es enviado a los servidores de OpenAI para su procesamiento. Esta es la operación de mayor sensibilidad del sistema. Ver sección 4.3 para el detalle de las garantías y límites de OpenAI.

---

## 4. Seguridad por Herramienta

### 4.1 Supabase

#### Row Level Security (RLS)

**Qué es:** RLS es el mecanismo de seguridad principal de la base de datos. Opera directamente en el motor de PostgreSQL: cada fila de cada tabla tiene reglas que determinan qué usuario puede leerla o escribirla. Ningún query desde la aplicación puede saltear estas reglas — son forzadas a nivel de base de datos, no a nivel de código.

**Cómo está planificado en ALMIA:**
- Un usuario B2C solo puede acceder a sus propias filas: `USING (auth.uid() = user_id)`
- Un administrador B2B solo puede ver datos de su empresa: `USING (org_id = get_user_org())`
- Los datos del Dashboard Corporativo exponen solo vistas agregadas, nunca filas individuales de sesiones
- Las tablas de sesiones y logs de crisis tienen RLS forzado; no pueden deshabilitarse sin aprobación explícita

**Límites del RLS:**
- RLS **no aplica** cuando se usa la `service_role key` de Supabase. Esta clave tiene acceso total sin restricciones. Debe existir únicamente en el servidor (n8n), nunca en el cliente (browser o app).
- Políticas mal escritas pueden filtrar datos entre usuarios o entre empresas sin generar errores visibles.
- Tablas accedidas vía `JOIN` desde una tabla sin RLS pueden exponer filas protegidas de forma indirecta.

**Riesgos:**
1. Exposición de la `service_role key` en el frontend o en un repositorio → acceso total a todos los datos de ALMIA sin restricciones.
2. Error en una política RLS → un administrador B2B puede leer datos de otra empresa.
3. RLS desactivado por error en una tabla durante una migración o deploy.
4. Queries con JOINs a tablas auxiliares sin RLS que filtran información de sesiones de forma indirecta.

**Mitigaciones aplicadas:**
- La `service_role key` solo existe en n8n (server-side). La app web usa únicamente la `anon key` + JWT del usuario autenticado.
- Revisión de políticas RLS en cada deploy y migración de esquema.
- Tablas de sesiones y crisis marcadas como críticas: cualquier cambio en sus políticas requiere validación explícita antes de aplicarse.

---

#### Supabase Auth

**Cómo funciona:** Gestiona el ciclo de autenticación. Al iniciar sesión, emite un **JWT de acceso** (corto plazo) y un **refresh token** (largo plazo) para renovar la sesión sin solicitar credenciales nuevamente.

**Límites:**
- El JWT de acceso expira en 1 hora por defecto (configurable).
- Los refresh tokens no tienen expiración predeterminada — una sesión puede mantenerse activa indefinidamente si no se configura un límite.
- MFA (autenticación multifactor) no está disponible en todos los planes de Supabase.

**Riesgos:**
1. Robo de un refresh token → el atacante mantiene sesión activa hasta que sea revocado manualmente.
2. Emails de recuperación de contraseña como vector de phishing si no provienen de un dominio verificado.
3. Sesiones abiertas en dispositivos compartidos sin logout explícito.

**Mitigaciones aplicadas:**
- Expiración de refresh tokens configurada (máximo 30 días de inactividad).
- Emails de autenticación enviados desde dominio verificado de ALMIA.
- Logout activo ante detección de comportamiento anómalo.

---

#### Cifrado en Supabase

| Capa | Mecanismo |
|---|---|
| Datos en reposo (base de datos) | AES-256 gestionado por Supabase / AWS |
| Datos en tránsito | TLS 1.2+ forzado en todas las conexiones |
| Contraseñas de usuario | bcrypt — nunca almacenadas en texto plano |

---

### 4.2 n8n (DigitalOcean, self-hosted)

#### Almacenamiento de credenciales

**Cómo funciona:** Todas las API keys y tokens que n8n necesita (OpenAI, Supabase, webhooks) se almacenan como **credenciales cifradas** dentro de n8n. El cifrado usa AES-256 con una clave derivada del entorno del servidor. No aparecen en código fuente ni en repositorios.

**Límites:**
- La clave de cifrado de n8n vive en el servidor. Si el servidor es comprometido, las credenciales pueden extraerse.
- n8n necesita la `service_role key` de Supabase para escrituras administrativas. Esta clave bypasea el RLS — es el punto de mayor riesgo del sistema.

**Riesgos:**
1. La `service_role key` de Supabase en n8n = acceso total a todos los datos de ALMIA sin restricciones. Si n8n es comprometido, la base de datos lo es también.
2. La API key de OpenAI en n8n: si es extraída, puede usarse para enviar prompts arbitrarios a cargo de la cuenta de Dialectika.

**Mitigaciones:**
- La `service_role key` y la API key de OpenAI se almacenan solo como credenciales cifradas en n8n; nunca en código fuente ni en variables de entorno planas.
- Principio de mínimo privilegio: cada workflow accede solo a las credenciales que necesita.
- Rotación periódica de credenciales críticas (al menos anual o ante cualquier sospecha de exposición).

---

#### Acceso al servidor

**Cómo funciona:** El servidor de DigitalOcean donde corre n8n solo acepta acceso SSH mediante **llave privada**. El acceso por contraseña está deshabilitado a nivel de sistema operativo.

**Límites:**
- Si la llave SSH privada es comprometida, el atacante tiene acceso total al servidor y a todo lo que corre en él.

**Riesgos:**
1. Robo de la llave SSH → acceso al servidor, n8n, credenciales cifradas y la `service_role key` de Supabase.
2. Llave SSH en un equipo del equipo técnico de la agencia que sea comprometido.

**Mitigaciones:**
- La llave SSH está protegida con passphrase.
- Acceso restringido por IP cuando es posible.
- El servidor no expone servicios adicionales públicamente.

---

#### Logs de workflows y datos sensibles

**Cómo funciona:** n8n registra los datos de entrada y salida de cada nodo durante la ejecución. Estos logs sirven para auditoría y depuración, pero pueden contener el texto de conversaciones de salud mental.

**Riesgos:**
1. Los logs de ejecución de n8n pueden contener mensajes de sesiones de salud mental en texto legible.
2. Retención indefinida de logs = acumulación de datos sensibles sin necesidad operativa.
3. Acceso a la interfaz de n8n = acceso a logs de conversaciones.

**Mitigaciones:**
- Retención de logs configurada en **30 días**; se eliminan automáticamente.
- Los workflows que procesan el contenido de sesiones están configurados para no loguear los payloads completos de conversación — solo metadatos de operación (IDs, timestamps, estado de ejecución).
- Acceso a n8n restringido por autenticación + IP allowlist.

---

#### Aislamiento entre proyectos

El entorno n8n de ALMIA/Dialectika corre en una instancia dedicada, separada de los workflows de otros clientes de la agencia. No comparte base de datos ni credenciales con otros proyectos.

---

### 4.3 OpenAI API

**Qué procesa:** El texto completo de cada mensaje que un usuario envía al agente de ALMIA — incluyendo el contenido de salud mental — es enviado a los servidores de OpenAI para generar la respuesta. Esta es la operación de mayor sensibilidad del sistema.

**Garantías de OpenAI para clientes de API:**
- Los datos enviados vía API **no se usan para entrenar los modelos** de OpenAI. Esta es una garantía explícita en sus términos de servicio para uso de API (distinto del uso gratuito de ChatGPT).
- Los datos enviados vía API **no se retienen de forma permanente**. OpenAI puede conservar los datos por hasta 30 días por razones de seguridad y abuso, después de lo cual son eliminados.
- OpenAI ofrece acuerdos de procesamiento de datos (DPA) para clientes que lo requieran.

**Límites:**
- Dialectika no controla la infraestructura de OpenAI ni puede auditar directamente cómo procesan los datos internamente.
- Los servidores de OpenAI están en Estados Unidos. Esto implica una transferencia internacional de datos sensibles de salud mental desde Chile.
- Las garantías de OpenAI son contractuales — dependen del cumplimiento de sus propios términos de servicio.

**Riesgos:**
1. Transferencia internacional de datos de salud mental (Chile → EE.UU.) sin un mecanismo formal de adecuación entre países.
2. Vulnerabilidad en la infraestructura de OpenAI que exponga datos de sesiones aún dentro de la ventana de retención de 30 días.
3. Cambios unilaterales en los términos de servicio de OpenAI que afecten las garantías actuales.

**Mitigaciones y recomendaciones:**
- Los prompts enviados a OpenAI están diseñados para no incluir más contexto del necesario para generar la respuesta (principio de minimización de datos).
- Se recomienda que Dialectika formalice un **DPA (Data Processing Agreement)** con OpenAI para uso empresarial, especialmente dado el carácter sensible de los datos.
- Se recomienda evaluar con asesoría legal si la transferencia internacional requiere cláusulas contractuales específicas bajo la Ley 21.719.

---

## 5. Quién Accede a los Datos

| Actor | Nivel de acceso |
|---|---|
| **la agencia (equipo técnico)** | Administrador del proyecto Supabase + acceso SSH al servidor n8n. Para operación, desarrollo y mantenimiento del agente y los dashboards. |
| **Dialectika — Pablo / Carlos** | Acceso al Admin Dashboard y al proyecto Supabase según el rol asignado al inicio del proyecto. |
| **Usuarios B2C (empleados)** | Solo sus propios datos: perfil y métricas de sus sesiones. RLS enforced. No pueden ver el contenido de sesiones de otros usuarios. |
| **Administradores B2B (RRHH)** | Solo datos agregados y anónimos de su empresa (Termómetro Emocional, tasa de activación, uso). Nunca datos individuales de sesiones. RLS enforced por `org_id`. |
| **OpenAI Inc.** | Procesa el contenido de los mensajes de sesión para generar respuestas. No retiene datos de forma permanente ni los usa para entrenar modelos (ver sección 4.3). |
| **Supabase Inc.** | Proveedor de infraestructura SaaS de la base de datos. Sus términos de servicio y política de privacidad aplican de forma independiente. |
| **Desarrollador externo** | Gestiona la interfaz web donde el usuario escribe. No tiene acceso a Supabase ni a n8n en el ámbito de la agencia. |

---

## 6. Regulación Aplicable

### Ley N° 21.719 — Protección de Datos Personales (Chile, vigente desde 2024)

Esta ley reemplaza a la antigua Ley 19.628 y establece un marco moderno de protección de datos personales en Chile.

**Puntos clave para ALMIA:**

- **Datos de salud mental = datos sensibles.** Requieren consentimiento explícito, finalidad específica, y medidas de seguridad reforzadas.
- **Responsable del tratamiento:** Dialectika. Es quien define para qué se procesan los datos y debe responder ante los usuarios y ante la ley.
- **Encargado del tratamiento:** la agencia. Opera la infraestructura técnica bajo instrucción de Dialectika.
- **Derechos de los titulares:** los usuarios tienen derecho a acceder a sus datos, rectificarlos, suprimirlos, oponerse al tratamiento y portarlos a otro sistema. Dialectika es quien debe dar cauce a estos derechos.
- **Transferencia internacional de datos:** el envío de datos a OpenAI (servidores en EE.UU.) constituye una transferencia internacional de datos sensibles. La Ley 21.719 exige que existan garantías adecuadas para estas transferencias.
- **Notificación de brechas:** ante un incidente que afecte datos personales, Dialectika tiene la obligación de notificar a la **Agencia de Protección de Datos Personales** en los plazos establecidos por la ley.

**Recomendación:** dado el carácter sensible de los datos que maneja ALMIA, se recomienda que Dialectika cuente con asesoría legal especializada para definir los textos de consentimiento, la política de privacidad pública y los mecanismos de respuesta a solicitudes de derechos de los usuarios.

---

## 7. Responsabilidades Compartidas

| Área | Responsable |
|---|---|
| Configuración de RLS y políticas de acceso en Supabase | la agencia |
| Validación de accesos del equipo de Dialectika | Dialectika + la agencia |
| Custodia de credenciales (service_role key, API key OpenAI, SSH) | la agencia |
| Rotación periódica de credenciales críticas | la agencia |
| Diseño de prompts con minimización de datos (no incluir más PII del necesario) | la agencia |
| Formalización del DPA con OpenAI | Dialectika (recomendado) |
| Consentimiento informado de los usuarios finales | Dialectika |
| Política de privacidad pública de ALMIA | Dialectika |
| Cumplimiento Ley 21.719 como responsable del tratamiento | Dialectika |
| Notificación de brechas a la Agencia de Protección de Datos | Dialectika (la agencia provee diagnóstico técnico) |
| Respuesta a solicitudes de derechos de usuarios (acceso, supresión, etc.) | Dialectika canaliza → la agencia ejecuta técnicamente |
| Términos y política de datos de OpenAI | OpenAI Inc. (tercero) |
| Términos y política de datos de Supabase | Supabase Inc. (tercero) |
| Seguridad de la interfaz web del usuario final | Desarrollador externo |

---

## 8. Retención y Eliminación de Datos

- Los logs de n8n se retienen **30 días** y se eliminan automáticamente.
- Los datos de sesiones en Supabase se retienen según lo que Dialectika defina en su política de privacidad, considerando la normativa sanitaria chilena aplicable a registros de salud mental.
- OpenAI puede retener los datos enviados vía API por hasta 30 días por razones de seguridad, después de los cuales los elimina.

**Al término del contrato entre la agencia y Dialectika:**
1. la agencia entrega un export completo de los datos (SQL dump de Supabase) en formato accesible.
2. la agencia elimina su acceso al proyecto Supabase y al servidor n8n de ALMIA.
3. El proceso se documenta y se confirma por escrito.

**Derecho de supresión de un usuario específico (derecho al olvido):**
El Admin Dashboard incluye un botón de "Eliminar datos" por usuario. Al activarse: Dialectika coordina con la agencia → se eliminan los datos del usuario en Supabase Database → se confirma la eliminación por escrito. Los logs de OpenAI correspondientes a ese usuario se eliminan automáticamente al vencer su ventana de retención de 30 días.

---

## 9. Ante un Incidente de Seguridad

la agencia monitorea los servicios de ALMIA en producción. Ante un incidente que afecte la integridad, confidencialidad o disponibilidad de los datos:

1. **la agencia notifica a Dialectika dentro de las 24 horas** de detectado el incidente.
2. Se comparte: qué datos se vieron afectados, cómo ocurrió, qué usuarios están en riesgo, y qué acciones se están tomando.
3. Supabase provee logs de acceso a la base de datos; n8n provee logs de ejecución de workflows. Ambos se usan para trazar el alcance del incidente.
4. **Dialectika evalúa** si el incidente requiere notificación a la Agencia de Protección de Datos Personales según los umbrales definidos por la Ley 21.719.
5. La coordinación de respuesta se realiza directamente entre ambos equipos por el canal de soporte asignado al proyecto.

---

## 10. Contacto

Para consultas sobre manejo de datos, privacidad o seguridad de ALMIA:

- **Email:** [EMAIL-AGENCIA]
- **WhatsApp:** +598 92 314 547

Las solicitudes de derechos de usuarios (acceso, rectificación, supresión) deben canalizarse primero a través de Dialectika, que actúa como responsable del tratamiento ante sus usuarios finales.

---

*la agencia para Dialectika — ALMIA. Versión 2.0 — 14/05/2026.*
*Documento compartible con el equipo de Dialectika y sus asesores legales.*
