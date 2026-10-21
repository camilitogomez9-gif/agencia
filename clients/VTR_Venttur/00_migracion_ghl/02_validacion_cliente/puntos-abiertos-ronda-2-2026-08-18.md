# Puntos abiertos (ronda 2) — Venttur

Hola Mauricio y Max 👋

Gracias por las respuestas del 17 de agosto. Con eso quedó cerrada casi toda la validación y ya podemos empezar a diseñar el sistema nuevo.

Quedan **5 puntos** y todos son cortos. Los de precios, tope de seguimientos y nombres de programa ya quedaron resueltos de nuestro lado.

**Sección A** son cosas que pueden resolver ustedes por escrito, acá mismo, en el recuadro de cada punto. **Sección B** son tres temas que conviene ver juntos en una llamada de 30 minutos porque nosotros llevamos datos que hay que decidir en el momento.

---

## Lo que ya quedó cerrado el 17 de agosto (no hace falta volver sobre esto)

Para que nadie relea el documento anterior:

| Tema | Cerrado |
|---|---|
| Programas | 8 programas activos. Pathway es solo Alemania. Gap Year y Estudia y Trabaja son el mismo. Francia es destino, no programa. |
| Asesores | Rodrigo lleva 3 programas, Andrés lleva 5. Diego queda fuera del ruteo automático. |
| Calendarios | Uno por programa (8 en total) en el sistema nuevo, con disponibilidad compartida por asesor. |
| Número de WhatsApp | Uno solo compartido. El +52 1 33 1944 2476 sigue vigente. |
| Campañas | Hoy solo Internados. El sistema se construye para medir por programa desde el inicio. |
| Origen del lead | El agente pregunta el programa siempre. El anuncio se usa solo para medición interna. |
| Formularios | El formulario de Meta reemplazó a la landing. go.venttur.com/bs sigue viva y hay que apuntarla al sistema nuevo. |
| Avisos al equipo | Le llegan a Mauricio y a Max, por email, app e inbox. |
| Confirmación de cita | Todos la reciben, sin importar el asesor. Más recordatorios antes de la cita. |
| Proceso de venta | Se reconstruye igual en el sistema nuevo, con todo el histórico. Clientify deja de operar. |
| Reporte semanal | Se mantiene. Se reportan citas agendadas (la asistencia la sigue midiendo Max aparte). |
| Fecha objetivo | 15 de septiembre de 2026. |

---

# SECCIÓN A — Lo pueden resolver ustedes por escrito

## ✅ 1. Los precios que el bot puede decir (ya resuelto, no hace falta que respondan)

Quedó confirmado internamente el 18 de agosto. El bot pasa a dar rango y cerrar proponiendo una fecha concreta, con estos números: Internados USD 50,000 a 130,000 al año · Intercambio académico MXN 240,000 a 450,000 · Campamentos MXN 90,000 a 180,000 · Pathway Alemania MXN 400,000 a 450,000 · Gap Year / Estudia y Trabaja MXN 100,000 a 200,000.

Lo único que sigue faltando son los rangos de los tres programas del punto 7 (Viajes educativos, Educación superior y Cursos de idiomas). Si prefieren que en esos el bot no diga cifras y pase directo a la asesoría, díganlo ahí y lo dejamos así.

---

## ✅ 2. Política de "Cerrada" al reabrir — RESUELTO (2026-08-18)

El bot atiende normal. Diferencia clave con el comportamiento actual (que causó el incidente de agosto): **NO se sobreescribe el programa capturado y NO se dispara ninguna secuencia de nurturing por la reapertura**. El bot simplemente responde el mensaje entrante.

---

## ✅ 3. Recordatorio de cita — timing RESUELTO (2026-08-18)

**Dos recordatorios: 24 horas antes y 1 hora antes.**

---

## ✅ 4. Confirmación de cita — contenido RESUELTO (2026-08-18)

**Fecha, hora, asesor y link de videollamada.** Sin campos adicionales.

---

## ✅ 6. Multi-programa — RESUELTO (2026-08-18)

**El bot pregunta / sugiere en base al contexto del lead.** No hay orden fijo de prioridad. Alinea con la política ya definida de que el agente nunca asume el programa.

⚠️ Deprecación asociada: se elimina el orden actual del Switch de nurturing (Pathway > Summer > AA Familiar > Boarding > Gap Year), que quedó sin criterio comercial.

---

## ✅ 7. Los 3 programas sin material — RESUELTO (2026-08-18)

**Tratamiento completo:** calendario propio, seguimientos propios, textos propios. Aplica a Viajes educativos, Educación superior y Cursos de idiomas en el extranjero.

⚠️ Impacto en la fecha del 15/9: es scope grande. Puede empujar contra el B3 (cutover completo vs dos olas) — depende de si la agencia tiene los assets para construir los 3 en 4 semanas o si el cliente los aporta.

---

## 🟡 8. Rangos de precio de los 3 huérfanos — SIN DEFINIR

La respuesta del cliente fue "-". Se toma como: **el bot NO da precio en esos 3 programas y pasa directo a la asesoría.** Cuando existan rangos definidos, se agregan.

---

# SECCIÓN B — respuestas integradas

## ✅ B1. Portabilidad del número — DATOS RECIBIDOS (2026-08-18)

- **Número del bot:** `+52 1 33 2627 4502` (Guadalajara). Chip **de Venttur**.
- **WABA:** ID `1931874540684022`, declarado como "ManyChat".

⚠️ **Hay que desambiguar la respuesta del WABA antes de dar veredicto de portabilidad.** "WABA: ManyChat" tiene dos lecturas posibles y solo una es portable:

| Interpretación | Consecuencia |
|---|---|
| **(a)** El WABA vive dentro del Business Manager de **Venttur**, con ManyChat conectado como BSP | ✅ Portable a GHL. Escenario A del doc de portabilidad |
| **(b)** El WABA vive dentro del Business Manager de **ManyChat** (mismo patrón que hundió a Collazo) | ❌ NO portable. Aunque el chip lo compró Venttur, si el WABA está bajo BM de ManyChat, el número queda atado. Hay que ir a número nuevo |

**Cómo se resuelve en 2 minutos** (solo Mauricio o Max pueden hacerlo, requiere acceso a Meta Business Suite de Venttur):
1. Entrar a **Meta Business Suite** con la cuenta de Venttur → `business.facebook.com`
2. Configuración del negocio → Cuentas → **Cuentas de WhatsApp**
3. Si el WABA `1931874540684022` **aparece en esa lista** → interpretación (a) → migrable
4. Si **NO aparece** → interpretación (b) → número nuevo

## ✅ B2. Migrabilidad de Clientify — POLÍTICA RECIBIDA (2026-08-18)

**Sobrevive todo lo que esté en Clientify.** Se migra en su totalidad: 6.968 contactos, 2.338 deals, 266 companies, 22 custom fields, historial de conversaciones, notas, adjuntos, automatizaciones.

⚠️ La auditoría de migrabilidad sigue siendo necesaria — no todo lo que está en Clientify tiene equivalente 1:1 en GHL. La auditoría inventaría qué se puede pasar automáticamente, qué requiere trabajo manual y qué directamente no viaja. Recién ahí se dimensiona el trabajo real y se decide si el 15/9 sigue siendo alcanzable.

## ✅ B3. Cutover 15/9 — DEFINIDO (2026-08-18)

**Cutover completo el 15/9.** Todo migra junto: canal + agente + calendarios + pipeline comercial.

⚠️ Este cutover tiene un pre-requisito duro: la auditoría de B2 tiene que devolver que la migración de Clientify es factible en 4 semanas. Si la auditoría muestra bloqueos, se re-abre B3 antes de que sea tarde.
