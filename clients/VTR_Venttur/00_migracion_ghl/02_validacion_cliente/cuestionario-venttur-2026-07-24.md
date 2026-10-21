# Puntos a confirmar — Venttur

**Respuestas revisadas y confirmadas por Mauricio García — 17 de agosto de 2026**

> **Contexto general:** esta implementación es una migración desde el stack actual (Clientify como CRM + ManyChat como canal de WhatsApp) hacia GoHighLevel. El objetivo es consolidar en una sola plataforma lo que hoy vive en herramientas separadas.
>
> **Fecha objetivo: 15 de septiembre de 2026.**

---

## Programas y asesores

**1. ¿Cuáles son todos los programas que ofrecen hoy?**

```
Son 8 programas, todos activos. Ninguno dado de baja.

1. Internados (Boarding School)
2. Intercambio académico con familias
3. Viajes educativos
4. Educación superior
5. Campamentos de verano
6. Cursos de idiomas en el extranjero
7. Pathway Alemania
8. Gap Year / Estudia y Trabaja

Aclaraciones sobre la lista original:

— "Pathway" lo usamos exclusivamente para Alemania. No es un programa
  genérico. El nombre correcto es Pathway Alemania.

— "Gap Year" y "Estudia y Trabaja" son EL MISMO PROGRAMA con dos nombres
  comerciales distintos. Se trata de cursos vocacionales tipo VET
  (marketing, emprendedurismo, diseño, fotografía, cocina, enfermería,
  childcare education, entre otros): diplomados cortos de 6 a 8 meses que
  incluyen permiso para trabajar legalmente en el destino. Usamos ambos
  nombres según lo que resulte más atractivo comercialmente, pero el
  producto es uno solo. En el sistema debe existir como un solo programa.

— "Francia" NO es un programa. Es un DESTINO que manejamos dentro de varios
  programas: intercambio académico con familia anfitriona, internados,
  cursos de idiomas y educación superior. No debe crearse como programa
  en el sistema.

— Sobre destinos en general: si un lead menciona un destino específico,
  se registra como comentario o nota en el contacto. No queremos que el
  destino sea un campo estructurado ni que se confunda con el programa.
```

---

**2. ¿Qué asesor y qué enlace de agenda corresponde a cada programa?**

```
RODRIGO atiende:
  1. Internados
  2. Intercambio académico con familias
  3. Campamentos de verano

ANDRÉS atiende:
  4. Viajes educativos
  5. Educación superior
  6. Pathway Alemania
  7. Cursos de idiomas en el extranjero
  8. Gap Year / Estudia y Trabaja

Sobre la pregunta puntual: "Gap Year en Australia" y "Estudiar y Trabajar"
son el mismo programa, dos nombres comerciales del mismo producto (ver
pregunta 1). Ambos los atiende Andrés.

Diego NO entra en el ruteo automático del sistema. Trabaja leads orgánicos
y tráfico frío que él mismo genera, fuera del flujo del agente. Andrés es
su supervisor directo.

ENLACES DE AGENDA — pendientes de crear:

No existen todavía. Los enlaces actuales viven en Clientify y quedan
obsoletos con la migración.

Se debe configurar UN CALENDARIO POR PROGRAMA (8 en total) en GoHighLevel,
cada uno dirigido al asesor correspondiente según el reparto de arriba:
3 calendarios apuntando a Rodrigo, 5 a Andrés.

Es importante que sea un calendario por programa y no uno por asesor,
porque así el sistema sabe desde el momento del agendamiento a qué programa
pertenece cada cita, sin depender de etiquetado manual posterior. Eso
alimenta directamente la medición por programa (ver pregunta 4).

Requisito técnico: todos los calendarios de un mismo asesor deben compartir
su disponibilidad real. Si alguien agenda "Internados" el martes a las 4pm,
ese bloque debe desaparecer también de "Intercambio académico" y
"Campamentos de verano". No queremos dobles reservas.
```

---

**3. ¿Qué número de WhatsApp usa cada asesor?**

```
Ningún asesor tiene número propio. Todos usan UN SOLO NÚMERO COMPARTIDO.
El +52 1 33 1944 2476 sigue vigente y es el que se comparte al agendar.

SITUACIÓN ACTUAL — dos números en operación:

Hoy operamos con dos números distintos:
  — Uno en ManyChat: donde vive el agente que conversa y agenda.
  — Otro en Clientify: desde donde salen los recordatorios de cita.

Esto pasó porque el agente nunca se pudo conectar al chat de Clientify.
El resultado es que el lead agenda con un número y después recibe el
recordatorio desde otro distinto, lo cual confunde.

LO QUE QUEREMOS:

Un solo número para todo: conversación del agente, confirmaciones de cita
y recordatorios. Que desaparezca la separación de canales.

Idealmente conservamos el número actual, migrándolo de ManyChat a
GoHighLevel. Sabemos que mover un número entre proveedores de WhatsApp
Business API puede complicarse según cómo esté vinculado hoy.

Necesitamos que nos confirmen:
  — Si la migración del número actual es viable.
  — Qué requiere de nuestra parte y en cuánto tiempo.
  — Qué se perdería si tenemos que dar de alta uno nuevo (historial,
    contactos, etiquetas) y cómo se manejaría la transición.

Si la portabilidad no es viable o implica riesgo de downtime, preferimos
número nuevo. Vale más eso que perder conversaciones o atorar la migración
(ver pregunta 12).
```

---

## Anuncios y medición (Meta)

**4. ¿Qué programas tienen campañas activas en Meta/Facebook?**

```
Hoy Internados (Boarding School) es el único programa con campaña activa.

Sin embargo, es probable que activemos campañas de otros programas más
adelante. No hay fecha definida ni programas confirmados todavía.

Por eso pedimos que el sistema se construya desde el inicio con la
capacidad de medir conversiones por programa de forma independiente,
para no tener que rehacerlo cuando eso pase.
```

---

**5. Los que escriben directo por WhatsApp desde un anuncio, ¿de qué programas suelen ser?**

```
Hoy sí, todos vienen de Internados, porque es la única campaña activa.

PERO PEDIMOS UN CAMBIO DE ENFOQUE:

El agente NO debe asumir el programa, ni siquiera cuando el origen parezca
evidente. Siempre debe preguntar y hacer descubrimiento de la necesidad
real del lead.

Alguien puede llegar desde un anuncio de Internados y estar buscando otra
cosa —un año académico, información para un hijo de otra edad—. Si el bot
da por hecho el programa, se pierde esa información y el asesor recibe un
lead mal calificado.

La distinción que queremos:

  — PARA MEDICIÓN Y ATRIBUCIÓN: que el sistema registre automáticamente la
    campaña de origen desde el dato que envía Meta. Eso es interno y no
    requiere preguntarle nada al lead.

  — PARA LA CONVERSACIÓN: que el agente indague el programa de interés.
    El programa que determina el ruteo y el calendario debe salir de lo
    que la persona diga, no del anuncio del que vino.

Con este enfoque, cuando activemos campañas de otros programas no hay que
ajustar nada.
```

---

## Páginas web (formularios)

**6. ¿Cuáles son todas las páginas/landings activas y qué datos pide cada formulario?**

```
Aclaración importante: los dos formularios no están activos en paralelo.
El formulario nativo de Meta SUSTITUYÓ a la landing, no la complementa.

ESTADO ACTUAL — Formulario nativo de Meta (Internados):
La campaña activa lleva a un formulario nativo de Meta, no a una página web.
Campos: nombre completo, email, teléfono, grado escolar, cuándo quiere
iniciar y nivel de inglés.

LANDING ANTERIOR — go.venttur.com/bs (Internados):
Sigue viva y funcionando al 100%. Manda a WhatsApp y tiene su propio
formulario. Campos: nombre, apellidos, email, teléfono, país y ciudad.
Hoy no recibe tráfico de campaña, pero cualquier lead orgánico que llega
entra al sistema con normalidad.

IMPORTANTE: hay que modificar el flujo de esta landing para que apunte a
GoHighLevel en lugar de ManyChat y Clientify. No debe quedar como puerta
muerta después de la migración.

LO QUE NECESITAMOS DEL SISTEMA:

Que ambas rutas de entrada funcionen y sean intercambiables. Si mañana
decidimos volver al embudo con landing, o correr las dos en paralelo, el
sistema debe adaptarse sin rehacerse.

Los campos que pide cada formulario son distintos, así que el sistema debe
manejar que un lead llegue con información parcial según por dónde entró,
y completar lo que falte durante la conversación (esto conecta con el
enfoque de descubrimiento de la pregunta 5).

Los demás programas no tienen landing ni formulario activo hoy, porque no
tienen campañas corriendo. Cuando los activemos aplicará la misma lógica.
```

---

## Conversación y seguimiento

**7. Los mensajes de seguimiento automáticos, ¿siguen vigentes?**

```
Se deben implementar cambios — ver Reporte la agencia - Agente WhatsApp Venttur
- Agosto 2026.pdf.
```

---

**8. Cuando el bot pasa una conversación a una persona del equipo, ¿quién debe recibir el aviso?**

```
El aviso debe llegarle a DOS personas, no a una:
  — Mauricio García
  — Max

Si el sistema permite notificar a más de un destinatario, queremos que
ambos lo reciban.

Canales de notificación: email, notificación de la app e inbox de
GoHighLevel.
```

---

**9. ¿Todos reciben confirmación de cita por WhatsApp, sin importar el asesor?**

```
Sí, todos deben recibir confirmación al agendar, sin importar el asesor.

ADEMÁS: necesitamos recordatorios automáticos antes de la cita.

Contexto de cómo está hoy y qué queremos cambiar:

Los recordatorios ya existen, pero están programados en Clientify, que
opera con un número distinto al de ManyChat. Como el agente nunca se pudo
conectar al chat de Clientify, hoy el lead agenda con un número y recibe
el recordatorio desde otro. Eso confunde.

EL OBJETIVO ES CONSOLIDAR TODO EN UN SOLO NÚMERO. Confirmación de cita y
recordatorios deben salir desde el mismo número que usa el agente, y todo
debe poder programarse dentro de GoHighLevel. Que ya no haya dos canales
separados.

No es una función nueva: es replicar en GHL algo que ya tenemos operando.
Aplica igual para todos los asesores y todos los programas.

Les compartiremos la configuración y los textos actuales de Clientify para
replicarlos.
```

---

## Ventas (CRM)

**10. El proceso de venta en Clientify, ¿lo reconstruimos en el sistema nuevo o lo dejan como está?**

```
Sí, queremos que el proceso de venta viva en el sistema nuevo. El objetivo
de la migración es tener todo en un solo lugar, así que Clientify deja de
operar.

CÓMO: reconstrúyanlo tal como está hoy, lo más parecido posible. Mismas
etapas, mismos nombres, mismo orden. No queremos rediseñarlo en este
momento; preferimos migrarlo igual y después nosotros depuramos lo que
sobre desde adentro.

HISTÓRICO: pasamos todo. Contactos, negocios abiertos, ganados y perdidos.
Preferimos tener la data completa y limpiarla nosotros después, a perder
información en la migración.

Entendemos que no existe una migración automática entre Clientify y
GoHighLevel y que buena parte del trabajo será reconstrucción manual.

Como ya tienen acceso a la API de Clientify, les pedimos que revisen qué
es replicable y qué no. Si algo no se puede migrar —historial de
conversaciones, archivos adjuntos, automatizaciones— NECESITAMOS SABERLO
ANTES DE APAGAR CLIENTIFY, para respaldarlo por nuestra cuenta.
```

---

## Reporte y fechas

**11. El reporte semanal de métricas, ¿lo mantenemos?**

```
Sí, lo mantenemos. Las definiciones que usamos:

LEAD CALIFICADO
El que continúa la conversación, contesta las preguntas del agente de
manera favorable al perfil que buscamos y muestra interés real en el
programa. No basta con que responda una vez: tiene que avanzar en el
descubrimiento y encajar con el perfil.

CITA
La métrica que queremos en el reporte es CITAS AGENDADAS. Las citas
presentadas (asistencia real) las mide Max por su cuenta, así que no hace
falta que el reporte las incluya.

CONVERSACIÓN NO CONTINUADA
Cuando el lead deja de contestar los mensajes de seguimiento. Se marca al
agotarse la secuencia completa sin respuesta, aproximadamente a los 5 días.
```

---

**12. Número de WhatsApp y fecha objetivo**

```
NÚMERO
Idealmente conservamos el mismo, pero no es condición. Hay que revisar si
ManyChat lo libera para poder registrarlo con otro proveedor.

Si la portabilidad no es viable o implica riesgo de downtime, preferimos
dar de alta un número nuevo. Vale más eso que arriesgarnos a perder
conversaciones o a que la migración se atore.

Les pedimos que la revisión de portabilidad sea LO PRIMERO que se atienda.
Es el único punto que depende de un tercero (ManyChat) y puede convertirse
en el cuello de botella de toda la migración. Necesitamos una respuesta
rápida —viable o no— para tomar la decisión sin comprometer la fecha.

Ver el detalle completo en la pregunta 3.

FECHA OBJETIVO
15 de septiembre de 2026, a más tardar.
```

---

## Anexo — Tabla de referencia: programa / asesor / calendario

| # | Programa | Asesor | Calendario GHL |
|---|---|---|---|
| 1 | Internados (Boarding School) | Rodrigo | Por crear |
| 2 | Intercambio académico con familias | Rodrigo | Por crear |
| 3 | Campamentos de verano | Rodrigo | Por crear |
| 4 | Viajes educativos | Andrés | Por crear |
| 5 | Educación superior | Andrés | Por crear |
| 6 | Pathway Alemania | Andrés | Por crear |
| 7 | Cursos de idiomas en el extranjero | Andrés | Por crear |
| 8 | Gap Year / Estudia y Trabaja | Andrés | Por crear |

Los 8 calendarios de un mismo asesor deben compartir su disponibilidad real
para evitar dobles reservas.

Diego no aparece en esta tabla porque queda fuera del ruteo automático:
trabaja leads orgánicos y tráfico frío propio.

---

## Anexo — Resumen de correcciones a la versión anterior

Las respuestas originales fueron redactadas por Max. Estos son los puntos
que se corrigieron o completaron en esta revisión:

| # | Cambio |
|---|---|
| 1 | Eran 9 programas listados, son 8. Gap Year y Estudia y Trabaja son el mismo. Pathway es exclusivamente Alemania. Francia es destino, no programa. |
| 2 | Se corrigió: Gap Year y Estudia y Trabaja NO son distintos, son el mismo programa. Se agregaron Cursos de idiomas (Andrés). Se aclaró que Diego queda fuera del ruteo. Se definió un calendario por programa, no por asesor. |
| 3 | La respuesta original ("Sí, es el mismo") era ambigua. Se aclaró que hay un solo número compartido entre asesores, pero DOS números a nivel sistema (ManyChat + Clientify), y que el objetivo es consolidar en uno. |
| 4 | Se agregó que es probable activar campañas de otros programas, y el requisito de medición independiente desde el inicio. |
| 5 | Se cambió el enfoque: el agente no debe asumir el programa por el anuncio de origen. Debe hacer descubrimiento. La atribución técnica va por separado. |
| 6 | Se corrigió: los dos formularios NO operan en paralelo. Meta sustituyó a la landing. La landing sigue viva para orgánicos y hay que redirigirla a GHL. |
| 8 | Se agregó a Max como segundo destinatario del aviso, y se definieron los canales. |
| 9 | Se agregaron los recordatorios automáticos y el requisito de que salgan del mismo número que el agente. |
| 10 | Estaba en blanco. Se respondió completa. |
| 11 | Estaba en blanco. Se respondió completa. |
| 12 | Faltaba la fecha objetivo. Se agregó, junto con la priorización de la revisión de portabilidad. |
