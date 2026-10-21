# Manejo de Datos y Seguridad — ALMIA

**Preparado para:** Dialectika · Pablo
**Plataforma:** ALMIA
**Versión:** 1.0
**Fecha:** 13/05/2026

---

## 1. Introducción y Alcance

Este documento describe cómo la agencia recopila, procesa, almacena y protege los datos dentro de ALMIA: la plataforma web de psicología desarrollada para Dialectika, que opera en modalidad B2C (pacientes) y B2B (clínicas y terapeutas).

**Roles:**
- **la agencia** actúa como **encargado del tratamiento**: opera la infraestructura técnica (base de datos, automatizaciones, servidores) siguiendo las instrucciones de Dialectika.
- **Dialectika** es el **responsable del tratamiento** ante sus usuarios finales: define el propósito del procesamiento y asume las obligaciones regulatorias frente a la ley chilena.

ALMIA maneja datos de salud psicológica, que la **Ley N° 21.719 de Protección de Datos Personales** (Chile, vigente 2024) clasifica como **datos sensibles**. Esto implica obligaciones reforzadas: consentimiento explícito, finalidad específica, y medidas de seguridad adecuadas al nivel de riesgo.

Este documento no reemplaza el acuerdo contractual entre la agencia y Dialectika, que puede incluir cláusulas adicionales de confidencialidad o manejo de datos.

---

## 2. Qué Datos Maneja ALMIA

### 2.1 Datos de identidad

Recopilados de pacientes y profesionales durante el registro y uso de la plataforma:

- Nombre y apellido
- Dirección de correo electrónico
- Número de teléfono
- RUT (cuando se solicita para emisión de boletas u otros fines)
- Rol en la plataforma (paciente, terapeuta, administrador de clínica)

### 2.2 Datos de salud / sesiones psicológicas

Esta es la categoría más sensible. Incluye información generada durante la actividad clínica en la plataforma:

- Motivo de consulta
- Notas de sesión registradas por el terapeuta
- Historial terapéutico del paciente
- Diagnósticos o impresiones clínicas (según lo que el terapeuta registre)
- Archivos clínicos adjuntos (documentos, evaluaciones)

### 2.3 Datos operativos B2B

Información de clínicas, consultorios y equipos de terapeutas:

- Nombre y datos de contacto del consultorio
- Configuración del equipo (terapeutas vinculados, roles)
- Agenda de atención y disponibilidad horaria

### 2.4 Qué ALMIA no recopila

ALMIA no solicita ni procesa:

- Contraseñas en texto plano (nunca se almacenan; solo hashes seguros vía Supabase Auth)
- Datos financieros completos (números de tarjeta, cuentas bancarias)
- Datos biométricos
- Datos de menores sin representante legal autorizado

---

## 3. Arquitectura de Datos

### 3.1 Flujo de datos en ALMIA

1. **Usuario** (paciente o terapeuta) accede a la plataforma web ALMIA desde su navegador.
2. **Supabase Auth** autentica al usuario y emite un token JWT con su rol e identidad.
3. La aplicación consulta y escribe datos en **Supabase Database** (PostgreSQL) bajo las políticas de Row Level Security activas.
4. Archivos clínicos (si aplica) se almacenan en **Supabase Storage** en buckets privados.
5. **n8n** orquesta automatizaciones en segundo plano: notificaciones, sincronización de agenda, triggers internos entre módulos.
6. El usuario recibe respuestas, confirmaciones o notificaciones desde la plataforma o por email.

### 3.2 Dónde se almacena cada dato

| Sistema | Qué guarda | Controlado por |
|---|---|---|
| **Supabase Database** | Perfiles de usuario, notas de sesión, historial clínico, configuración B2B, agenda | la agencia (configuración) + Dialectika (gestión de datos) |
| **Supabase Auth** | Tokens de sesión JWT, emails de login, roles de usuario, refresh tokens | Supabase (SaaS) bajo configuración de la agencia |
| **Supabase Storage** | Archivos clínicos adjuntos, documentos de evaluación | la agencia (configuración) + Dialectika (contenido) |
| **n8n** (servidor DigitalOcean) | Logs de ejecución de workflows, credenciales de integración cifradas | la agencia exclusivamente |

### 3.3 Servidores

n8n corre en un servidor de DigitalOcean administrado directamente por la agencia. El entorno de ALMIA/Dialectika es independiente de otros proyectos; no comparte instancia ni credenciales con otros clientes de la agencia.

Supabase es un servicio SaaS (alojado en infraestructura de Supabase Inc. / AWS). Los datos residen en la región configurada al crear el proyecto.

---

## 4. Seguridad por Herramienta

### 4.1 Supabase

#### Row Level Security (RLS)

**Qué es:** RLS es el mecanismo de seguridad principal de la base de datos. Es un sistema de políticas que opera directamente en PostgreSQL: cada fila de cada tabla tiene reglas que determinan qué usuario puede leerla o escribirla. Ningún query desde la aplicación puede saltear estas reglas — operan a nivel de motor de base de datos.

**Cómo está configurado en ALMIA:**
- Un paciente solo puede acceder a sus propias filas: `USING (auth.uid() = user_id)`
- Un terapeuta solo accede a los pacientes de su consultorio: `USING (org_id = get_user_org())`
- Los administradores B2B tienen scope delimitado por su `org_id`
- Las tablas de notas clínicas y archivos de salud tienen RLS forzado (no puede desactivarse sin aprobación explícita)

**Límites del RLS:**
- RLS **no aplica** cuando se usa la `service_role key` de Supabase. Esta clave tiene acceso total a la base de datos, bypasseando todas las políticas. Solo debe usarse en el servidor (n8n), nunca en el cliente (browser).
- Políticas mal escritas pueden filtrar datos entre usuarios o entre organizaciones sin generar errores visibles.
- Tablas accedidas vía `JOIN` desde una tabla sin RLS pueden exponer filas que de otro modo estarían protegidas.

**Riesgos:**
1. Exposición de la `service_role key` en el frontend o en repositorios → acceso total a todos los datos sin restricciones.
2. Error en una política RLS → un terapeuta puede leer notas de otro consultorio.
3. RLS desactivado por accidente en una tabla durante un deploy o migración.
4. Queries con JOINs a tablas auxiliares sin RLS que filtran información sensible de forma indirecta.

**Mitigaciones aplicadas:**
- La `service_role key` solo vive en n8n (server-side); la aplicación web usa únicamente la `anon key` + JWT del usuario.
- Revisión de políticas RLS en cada deploy y migración de esquema.
- Tablas de salud marcadas como críticas: cualquier cambio en sus políticas requiere validación explícita.
- Tests de aislamiento entre organizaciones antes de cada release.

---

#### Supabase Auth

**Cómo funciona:** Gestiona el ciclo completo de autenticación. Al iniciar sesión, emite un **JWT de acceso** (corto plazo) y un **refresh token** (largo plazo) que permite renovar la sesión sin pedir credenciales nuevamente.

**Límites:**
- El JWT de acceso expira en 1 hora por defecto (configurable). Después, se necesita el refresh token.
- Los refresh tokens no tienen expiración por defecto en Supabase — una sesión puede persistir indefinidamente si no se configura un límite.
- El plan gratuito no incluye MFA (autenticación de múltiples factores) nativo.

**Riesgos:**
1. Robo de un refresh token → el atacante mantiene sesión activa indefinidamente hasta que el token sea revocado manualmente.
2. Emails de recuperación de contraseña como vector de phishing si el dominio de envío no está verificado.
3. Sesiones abiertas en dispositivos compartidos sin logout explícito.

**Mitigaciones aplicadas:**
- Expiración de refresh tokens configurada (máximo 30 días de inactividad).
- Emails de autenticación enviados desde dominio verificado de Dialectika/ALMIA.
- Logout activo en detección de comportamiento anómalo.

---

#### Supabase Storage

**Uso en ALMIA:** Almacena archivos clínicos adjuntos (documentos de evaluación, informes). Los buckets son privados — ningún archivo es accesible sin un token de descarga válido.

**Cómo funciona el acceso:** Los archivos se sirven mediante **signed URLs** — URLs temporales generadas con una expiración definida. Después de ese tiempo, la URL deja de funcionar.

**Límites:**
- El Storage usa cifrado en reposo de AWS S3 (AES-256), pero no ofrece cifrado end-to-end propio: Supabase puede técnicamente acceder a los archivos almacenados.
- Las signed URLs, una vez generadas, son válidas para cualquier persona que las tenga — no están ligadas al usuario que las solicitó.

**Riesgos:**
1. Signed URLs con TTL muy largo → un link de descarga compartido por error sigue siendo válido días después.
2. Bucket configurado como público por error en un deploy → todos los archivos quedan accesibles sin autenticación.
3. Nombres de archivos predecibles que permitan enumeración si un bucket quedara expuesto.

**Mitigaciones aplicadas:**
- Todos los buckets de ALMIA configurados como **privados** por defecto; ningún bucket público salvo assets de la interfaz (imágenes de UI, logos).
- Signed URLs generadas con TTL de 15 minutos para archivos clínicos.
- Nombres de archivo con UUIDs para evitar enumeración.

---

#### Cifrado en Supabase

| Capa | Mecanismo |
|---|---|
| Datos en reposo (base de datos) | AES-256 gestionado por Supabase / AWS |
| Datos en reposo (storage) | AES-256 gestionado por AWS S3 |
| Datos en tránsito | TLS 1.2+ forzado en todas las conexiones |
| Contraseñas de usuario | bcrypt (nunca almacenadas en texto plano) |

---

### 4.2 n8n (DigitalOcean, self-hosted)

#### Almacenamiento de credenciales

**Cómo funciona:** Todas las API keys, tokens de integración y contraseñas que n8n necesita para operar (ej: credenciales de Supabase, claves de email, webhooks) se almacenan como **credenciales cifradas** dentro de n8n. El cifrado usa AES-256 con una clave derivada de una variable de entorno en el servidor. No aparecen en código fuente ni en repositorios.

**Límites:**
- La clave de cifrado de n8n vive en el servidor. Si el servidor es comprometido físicamente o por acceso remoto, las credenciales podrían extraerse.
- n8n necesita la `service_role key` de Supabase para operaciones que requieren acceso admin (ej: triggers que escriben en tablas protegidas). Esta clave bypassea el RLS — es el punto de mayor riesgo.

**Riesgos:**
1. La `service_role key` de Supabase en n8n = acceso total a todos los datos de ALMIA sin restricciones de RLS. Si n8n es comprometido, la base de datos lo es también.
2. Credenciales de email o notificaciones en n8n podrían usarse para spam o phishing si son extraídas.

**Mitigaciones:**
- La `service_role key` se almacena solo en n8n como variable de entorno cifrada; nunca en código fuente ni en Supabase Dashboard compartido.
- Principio de menor privilegio: cada workflow tiene acceso solo a las credenciales que necesita.
- Rotación periódica de la service_role key (al menos anual o ante cualquier sospecha de exposición).

---

#### Acceso al servidor

**Cómo funciona:** El servidor de DigitalOcean donde corre n8n solo acepta acceso SSH mediante **llave privada**. El acceso por contraseña está deshabilitado a nivel de sistema operativo.

**Límites:**
- Si la llave privada SSH es comprometida, el atacante tiene acceso total al servidor (y por extensión a n8n y las credenciales cifradas en él).
- No existe un segundo factor de autenticación para SSH por defecto.

**Riesgos:**
1. Robo de la llave SSH privada → acceso completo al servidor.
2. Llave SSH en un equipo comprometido del equipo técnico de la agencia.

**Mitigaciones:**
- La llave SSH está protegida con passphrase.
- Acceso SSH restringido por IP (solo desde rangos conocidos del equipo de la agencia, cuando es posible).
- El servidor no corre servicios adicionales expuestos públicamente (solo n8n en puerto interno con proxy reverso).

---

#### Logs y datos en workflows

**Cómo funciona:** n8n registra los datos de entrada y salida de cada nodo de un workflow durante su ejecución. Estos logs sirven para depuración y auditoría, pero pueden contener datos personales de los usuarios.

**Riesgos:**
1. Logs de ejecución exponen nombres, emails o contenido de notas clínicas si los workflows procesan esos datos y los loguean completos.
2. Acceso a los logs de n8n = acceso a datos de usuarios en texto legible.
3. Retención indefinida de logs = acumulación de datos sensibles sin necesidad.

**Mitigaciones:**
- Retención de logs configurada en **30 días**; después se eliminan automáticamente.
- Workflows que manejan datos clínicos están configurados para no loguear payloads completos (solo IDs y metadatos de operación).
- Acceso a la interfaz de n8n restringido por autenticación básica + IP allowlist.

---

#### Aislamiento entre proyectos

El entorno n8n de ALMIA/Dialectika corre en una instancia dedicada, separada de los workflows de otros clientes de la agencia. No existe base de datos compartida ni credenciales cruzadas entre proyectos.

---

## 5. Quién Accede a los Datos

| Actor | Nivel de acceso |
|---|---|
| **la agencia (equipo técnico)** | Administrador de proyecto Supabase + acceso SSH a servidor n8n. Para operación, mantenimiento y desarrollo de ALMIA. |
| **Dialectika — Pablo / Carlos** | Acceso admin al proyecto Supabase (según lo definido al inicio del proyecto). Pueden consultar y exportar datos. |
| **Dialectika — Esteban (desarrollador web)** | Acceso al proyecto Supabase según el rol asignado. No tiene acceso al servidor n8n. |
| **Usuarios B2C (pacientes)** | Solo sus propios datos: perfil, historial de sesiones propias, archivos propios. RLS enforced. |
| **Usuarios B2B (terapeutas / admins de clínica)** | Datos de los pacientes y sesiones de su organización. Scope delimitado por `org_id`. RLS enforced. |
| **Supabase Inc.** | Proveedor de infraestructura SaaS. Sus términos de servicio y política de privacidad aplican de forma independiente. |

---

## 6. Regulación Aplicable

### Ley N° 21.719 — Protección de Datos Personales (Chile)

La ley chilena vigente desde 2024 establece:

- **Datos de salud = datos sensibles.** Requieren tratamiento con mayor nivel de protección, consentimiento explícito e informado, y finalidad específica.
- **Responsable del tratamiento:** Dialectika, como titular de ALMIA y quien define el propósito del procesamiento.
- **Encargado del tratamiento:** la agencia, como operador técnico que procesa datos bajo instrucción de Dialectika.
- **Derechos de los titulares:** los usuarios tienen derecho de acceso, rectificación, supresión, oposición y portabilidad de sus datos. Dialectika debe dar cauce a estos derechos.
- **Obligación de notificación de brechas:** ante un incidente significativo, Dialectika debe notificar a la **Agencia de Protección de Datos Personales** (organismo creado por la ley) en los plazos definidos por la normativa.

**la agencia provee el soporte técnico para cumplir con los requisitos de seguridad; el cumplimiento regulatorio formal es responsabilidad de Dialectika.**

---

## 7. Responsabilidades Compartidas

| Área | Responsable |
|---|---|
| Configuración de RLS y políticas de acceso en Supabase | la agencia |
| Validación de accesos internos del equipo de Dialectika | Dialectika + la agencia |
| Custodia de credenciales (service_role key, SSH) | la agencia |
| Rotación periódica de credenciales críticas | la agencia |
| Consentimiento informado de usuarios finales | Dialectika |
| Política de privacidad pública de ALMIA | Dialectika |
| Cumplimiento Ley 21.719 (responsable del tratamiento) | Dialectika |
| Notificación de brechas a la Agencia de Datos | Dialectika (con soporte técnico de la agencia para diagnóstico) |
| Respuesta a solicitudes de derechos de usuarios (acceso, supresión) | Dialectika canaliza a la agencia para ejecución técnica |
| Términos y política de datos de Supabase SaaS | Supabase Inc. (tercero) |

---

## 8. Retención y Eliminación de Datos

- Los tiempos de retención de datos clínicos deben ser definidos por Dialectika en función de la normativa sanitaria chilena aplicable a registros psicológicos.
- Los logs de n8n se retienen **30 días** y luego se eliminan automáticamente.
- Al concluir la relación contractual entre la agencia y Dialectika:
  1. la agencia entrega un export completo de los datos (SQL dump de Supabase + archivos de Storage) en formato accesible.
  2. la agencia elimina su acceso al proyecto Supabase y al servidor n8n de ALMIA.
  3. El proceso se documenta y se confirma por escrito.
- **Derecho de supresión de un usuario específico:** Dialectika recibe la solicitud del usuario → la canaliza a la agencia → la agencia ejecuta la eliminación en Supabase Database + Storage + logs de n8n relevantes → se confirma la eliminación por escrito a Dialectika.

---

## 9. Ante un Incidente de Seguridad

la agencia monitorea los servicios de ALMIA en producción. Ante un incidente que afecte la integridad, confidencialidad o disponibilidad de los datos:

1. **la agencia notifica a Dialectika dentro de las 24 horas** de detectado el incidente.
2. Se comparte: qué datos se vieron afectados, cómo ocurrió, qué datos de usuarios están en riesgo, y qué acciones se están tomando.
3. Supabase provee logs de acceso a la base de datos; n8n provee logs de ejecución de workflows. Ambos se usan para trazar el alcance del incidente.
4. **Dialectika es responsable** de evaluar si el incidente requiere notificación a la Agencia de Protección de Datos Personales según los umbrales definidos por la Ley 21.719.
5. La coordinación de respuesta se hace de forma directa entre ambos equipos por el canal de soporte asignado al proyecto.

---

## 10. Contacto

Para consultas sobre manejo de datos, privacidad o seguridad de ALMIA:

- **Email:** [EMAIL-AGENCIA]
- **WhatsApp:** +598 92 314 547

Las consultas sobre datos de un usuario específico deben canalizarse primero a través de Dialectika, que actúa como responsable del tratamiento ante sus usuarios finales.

---

*la agencia para Dialectika — ALMIA. Versión 1.0 — 13/05/2026.*
*Documento compartible con el equipo de Dialectika y sus asesores legales.*
