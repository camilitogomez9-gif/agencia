# Contenido interno de flows ManyChat — screenshots 2026-07-20

> Cierra el gap "Contenido interno de flows" de `README.md` §2 — la API de ManyChat solo entrega `ns`/nombre/carpeta (ver `manychat-snapshot-2026-05-13.md`), no la lógica interna. Esto viene de 15 screenshots del Flow editor, provistos por el usuario en `/Users/camilo/Downloads/flujos_manychat_venttur/`.
>
> **Hallazgo:** de los 15 screenshots, 12 mapean a los 14 flows ya documentados (2 no fueron screenshotteados: "Asignar número" y el "Rescate Post-Link" viejo de ManyChat — este último es de bajo interés porque ya se reemplaza por el flujo n8n). Los otros **3 son flows nuevos que NO estaban en el snapshot de mayo** — son los templates de Outreach Form Meta Touch 1/2/3, lo que confirma que la lista de 14 flows de `manychat-snapshot-2026-05-13.md` está **desactualizada** (creados en junio, después del snapshot).

---

## Mapeo screenshot → flow

| Archivo | Flow (de los 14 documentados) | Carpeta |
|---|---|---|
| `flow_2026_07_20_065859.png` | **Agenda** | Seguimientos |
| `flow_2026_07_20_065940.png` | **Recibir mensajes** | Agente IA Principal |
| `flow_2026_07_20_065955.png` | **Elevar** | Agente IA Principal |
| `flow_2026_07_20_070010.png` | **Enviar mensajes** | Agente IA Principal |
| `flow_2026_07_20_070032.png` | **Borrar contactos** | Manejo de contactos |
| `flow_2026_07_20_070135.png` | **Seguimiento agenda** | Agendamiento |
| `flow_2026_07_20_070200.png` | **Boarding School** | Seguimientos |
| `flow_2026_07_20_070236.png` | **Año Académico** | Seguimientos |
| `flow_2026_07_20_070250.png` | **Gap year** | Seguimientos |
| `flow_2026_07_20_070305.png` | **Pathway** | Seguimientos |
| `flow_2026_07_20_070314.png` | **Summer Camp** | Seguimientos |
| `flow_2026_07_20_070325.png` | **Lead General** | Seguimientos |
| `flow_2026_07_20_070058.png` | 🆕 Outreach Touch 3 (no estaba en el snapshot) | — |
| `flow_2026_07_20_070110.png` | 🆕 Outreach Touch 2 (no estaba en el snapshot) | — |
| `flow_2026_07_20_070121.png` | 🆕 Outreach Touch 1 (no estaba en el snapshot) | — |

**No cubiertos por estos 15:** Rescate Post-Link (ManyChat-side, de baja prioridad — reemplazado por el workflow n8n que ya tengo en detalle completo) y Asignar número (utilitario, bajo impacto para la migración).

---

## Agente IA Principal (los 3 flows core del loop conversacional)

### Recibir mensajes
Trigger implícito (When...) → captura el último input de texto en `respuesta_definitiva` (User Field, vía "Set User Field... to {respuesta_definitiva}, {Last Text Input}" — hace merge/concat si ya había texto pendiente, para agrupar mensajes rápidos consecutivos del lead) → **Pausa inteligente: espera 20 segundos** (buffer anti-fragmentación, evita mandar cada mensaje corto del lead por separado al agente) → 2 condiciones en cadena (`Field is missing`) → **ChatGPT Actions Request** → **External Request** a `https://[TU-INSTANCIA-N8N]/webh...` (webhook del main de n8n) → limpia `respuesta_definitiva` al final.

**Relevancia para GHL:** este es el patrón de "debounce" de mensajes — GHL Workflows tiene su propio mecanismo de espera/trigger que hay que replicar para no perder esta lógica (sin esto, el agente respondería a cada mensaje fragmentado del lead como turnos separados).

### Enviar mensajes
Envía en cadena `parte1` → condición → `parte2` → condición → `parte3` (los 3 custom fields que arma el agente n8n) como 3 mensajes de WhatsApp separados con ritmo natural, y al final limpia los 3 campos (`Clear User Field`). Coincide con el nodo "Formatear mensaje"/Split Respuesta usado en otros clientes de la agencia.

### Elevar
Muy simple: `Pause all automations: Forever` + `Assign conversation: Unknown user` + `Notify Assignees: 0 people via Messenger & E-mail` (el campo de destinatarios aparece vacío/"Unknown user" en el screenshot — **revisar en ManyChat si esto está realmente configurado o es un artefacto de captura**, porque si "Notify Assignees" está en 0 personas, el equipo humano no se estaría enterando de la elevación por este canal).

---

## Agendamiento / Seguimientos operativos

### Agenda
Envía "Rodrigo se comunicará contigo por WhatsApp directamente desde el número +52 1 33 1944 2476" + "Siéntete con la libertad de compartirlo con algún familiar que gustes que te acompañe a la reunión. Nos vemos pronto!" — condicionado a un chequeo de campo (probablemente valida que la cita se haya confirmado antes de mandar este mensaje). **Dato nuevo:** el número directo de Rodrigo (+52 1 33 1944 2476) no estaba documentado en ningún doc previo — es información de negocio a preservar en la migración.

### Seguimiento agenda
Doble condición (`Field is missing`) → mensaje: *"Hola [First Name] 👋 Hace unos días te compartí el enlace para agendar tu asesoría personalizada, pero vi que aún no la agendaste. ¿Tuviste algún problema con el link? Sé que una decisión así requiere claridad, y por eso diseñamos estas sesiones: para ayudarte a resolver dudas reales, evitar errores comunes y construir un plan viable antes de que se pierda tiempo valioso o se cierren opciones 📆. Me interesa que tomes la mejor decisión posible, con respaldo profesional y en el momento adecuado. ¿Te gustaría que te lo vuelva a compartir?"* → `Add Tag: seguimiento_agenda`. Coincide con el propósito documentado del workflow n8n homónimo.

### Borrar contactos
Trigger `Contact event occurs (Date/Time based trigger)` → acción única `Delete Contact`. Limpieza programada de contactos (probablemente ligada a alguna condición de inactividad o test data — **el screenshot no muestra el detalle del trigger de fecha**, conviene abrir el flow en ManyChat para ver la condición exacta antes de replicar esto en GHL, ya que borrar contactos es una acción destructiva).

---

## Seguimientos de nurturing por programa (drip campaigns largos)

Los 5 siguientes comparten estructura: `Condición (Field is missing)` → `Acciones (Add Tag seguimiento / seguimiento_agenda)` → mensaje inicial → `Pausa inteligente (Wait 1 Day)` → mensaje 2 → `Pausa (Wait 2 Days)` → mensaje 3 → `Pausa (Wait 2 Days)` → mensaje 4 final. Este patrón (4 toques a 0/1/3/5 días) es el nurturing de largo plazo para leads que no siguieron el flujo de agendamiento — **no estaba documentado en ningún doc previo del repo**, es contenido nuevo para el mapa funcional de Etapa 1.

### Boarding School
1. *"Te comparto algo que puede servirte. Hola [First Name], no estoy seguro si este sea un buen momento para ti, pero quería dejarte esto por si te ayuda. Muchos papás se detienen porque sienten que no tienen toda la información o no saben por dónde empezar. Te comparto tres errores más comunes al elegir escuela en el extranjero: 1. Elegir por el país, no por el perfil del estudiante. 2. Guiarse solo por presupuesto sin entender qué implica. 3. No considerar si la edad y madurez son compatibles con el programa. Espero que estos errores te brinden más claridad. Ojalá te sirva, saludos y un fuerte abrazo."*
2. *"La pregunta que cambia todo. ¿Cómo es tu hijo cuando lo ve? Esta pregunta cambia completamente el tipo de recomendación. Muchas veces se elige por destino o por precio, pero si no se parte del perfil del estudiante, es muy fácil equivocarse. Si te interesa, con gusto te ayudo a pensar desde ahí."*
3. *"Esto lo usamos mucho con las familias que al principio no sabían qué recomendar. Aunque no hayas decidido todavía: ¿Está tu hijo listo para estudiar fuera? ✅ Tiene cierta autonomía en casa ✅ Sabe manejar frustraciones sin papás cerca ✅ Tiene una razón clara (más allá de 'me gusta viajar') ✅ Ustedes como papás tienen expectativas claras. No es un test. Solo algo que puede ayudar a pensar si es el momento correcto. Si te sirve, me da gusto. Y si en algún momento quieres retomarlo, aquí estoy."*
4. *"No te quiero saturar, lo prometo. Solo quería dejarte este último. Si en algún punto quieres que hablemos de esto, aquí ando. Espero que encuentres pronto lo que están buscando. Aquí no vendemos algo, ayudamos a tomar buenas decisiones. Cuando sientas que es el momento, aquí estoy."*

### Año Académico (AA Familiar)
1. *"No es solo el país, es tu casa. Hola [First Name], no estoy seguro si todavía estás considerando esta opción, pero te quiero dejar una reflexión importante. Muchos papás eligen el país o el colegio... pero se olvidan de algo esencial: 🏠 Tu hijo no va a vivir en una escuela, va a vivir en una familia anfitriona. El impacto que tiene la familia anfitriona en la experiencia es enorme. Si quieres, te puedo explicar cómo funciona este punto en cada país y por qué hace la diferencia."*
2. *"¿Cómo saber si tu hijo está listo? Una de las dudas más grandes que tienen los papás es: ¿Mi hijo realmente está preparado para vivir un año fuera, sin ustedes ahí? Te comparto algunas indicaciones que usamos para acompañar a las familias en esta decisión: ✅ Tiene cierto nivel de autonomía y se adapta bien a nuevos entornos ✅ Muestra apertura a otras culturas y estilos de vida ✅ Tiene curiosidad por mejorar su idioma ✅ Papás e hijo comparten expectativas realistas del programa."*
3. *"¿Dónde hay programas y cómo se elige uno bien? Te comparto los países donde actualmente manejamos programas: 🇺🇸 Estados Unidos 🇨🇦 Canadá 🇫🇷 Francia 🇮🇹 Italia 🇳🇱 Países Bajos. Todos tienen diferencias importantes en cuanto a costos, requisitos, estructura y selección de familias. Si tienes en mente alguno o cuál te acomoda mejor según lo que buscan, puedo ayudarte a saber si es el más adecuado."*
4. *"¿Tu hijo ya te dijo a cuál país le gustaría irse?"* (cierre corto — implícito por la posición final en la cadena, texto exacto no capturado en el screenshot).

### Gap Year
1. *"Gap Year no es escapista. Hola [First Name], no sé si todavía estás explorando esta opción, pero quería invitarte a considerar. Una de las diferencias más importantes que nadie explica bien es esta: 🎯 Un Gap Year no es una 'pausa' ni una 'escapadista'. Bien diseñado, es una herramienta para ganar claridad, madurez y dirección. Lo ideal es que no sea improvisado. Si te interesa, puedo ayudarte a definir cuál es el enfoque más adecuado para ti."*
2. *"Te comparto esta reflexión. Muchas veces se piensa que el Gap Year es solo para 'descansar' antes de la universidad. Pero si se planea bien, ayuda a construir un mejor perfil académico y laboral después."*
3. *"¿Qué países permiten estudiar y trabajar legalmente? Una de las preguntas más comunes es: ¿Dónde se puede estudiar y trabajar legalmente al mismo tiempo? Te comparto un resumen rápido: 🇦🇺 Australia — con cursos de idiomas o vocacionales 🇮🇪 Irlanda — con cursos de más de 25 semanas 🇨🇦 Canadá — en programas académicos específicos 🇲🇹 Malta 🇦🇪 Dubái — con ciertas condiciones. Y muchos más... Cada país tiene sus reglas, y elegir mal significa no poder trabajar legalmente. Si quieres, te explico cuál se adapta según tu perfil."*
4. *"Lo importante no es irte, es saber por qué."* (cierre corto).

### Pathway (Alemania)
1. *"Una pregunta que muchos no se atreven a hacer. Hola [First Name], te dejo algo que tal vez ya te has preguntado o has estado pensando o comparando opciones. Una de las preguntas más comunes (pero que casi nadie hace) es: ¿Es verdad que puedo estudiar en Alemania pagando menos que en México? La respuesta es sí, pero depende mucho de cómo te prepares. El Pathway es el paso previo para acceder a universidades públicas alemanas sin costo de colegiatura. Muchas veces hace toda la diferencia. Si quieres, te puedo ayudar a entender cuál aplica para ti y cuál es el camino correcto."*
2. *"Lo que me hubiera gustado saber antes. Muchos estudiantes que nos escriben creen que van a llegar el día en el país listos, pero les faltan requisitos formales y académicos, y por eso nadie les dice que necesitan cumplirlos, y pierden tiempo valioso o incluso llegan tarde para inscribirse en algún lugar. Si me cuentas un poco más de tu perfil, puedo decirte si estás en el camino correcto... o si hay algo que debes ajustar antes de avanzar."*
3. *"Te comparto este checklist rápido de cómo funciona el Pathway (2 años): ✅ ¿Llevas o estás por terminar la prepa o una carrera universitaria? ✅ ¿Te gustaría estudiar una carrera desde principio o aprender alemán desde cero? ✅ ¿Estás dispuesto a aprender alemán desde cero o reforzarlo? ✅ ¿Tienes experiencia viviendo fuera a largo plazo? Si respondiste que sí a 2 o más, ya te puedo recomendar opciones más adecuadas."*
4. *"Lo importante no es tener prisa, es tomar la mejor decisión."* (cierre corto).

### Summer Camp
1. *"¿Campamento o vacaciones? Hola [First Name], te escribo porque veo algo seguido: los papás están considerando un campamento de verano y dudan entre esto. ⚡ A veces se piensa que es unas 'vacaciones fuera', pero la realidad es que bien elegido, puede ser una experiencia que le dé a tu hijo mucha más seguridad, independencia y visión del mundo. Si quieres, te puedo explicar qué hace que un campamento sea de valor real, y qué países tienen las mejores opciones en este momento."*
2. *"3 preguntas que pueden ayudarte a decidir. Te comparto 3 preguntas que suelen ayudar a los papás a decidir si un summer camp les hace sentido: 1. ¿Tu hijo se adapta fácilmente a entornos nuevos y sin ti cerca? 2. ¿Ha tenido experiencias antes similares (campamentos, viajes, convivencia)? 3. ¿Este viaje es un primer paso hacia algo más (como estudiar fuera) o solo para disfrutar el verano? No hay respuestas correctas. Pero saber esto te ayuda a elegir mejor."*
3. *"Qué países manejamos (y por qué). Te comparto los destinos donde actualmente manejamos campamentos, con los mejores mixtos de seguridad y contenido formativo: Estados Unidos, Reino Unido, Canadá, Francia, Alemania. Y muchos más... Todos tienen enfoques diferentes, algunos más académicos, otros más culturales o deportivos. Si tienes algún país en mente, puedo ayudarte a identificar si es una buena opción para el verano."*
4. (cuarto mensaje no capturado en el screenshot — cadena se corta en el tercer "Enviar mensaje #2").

### Lead General (fallback genérico, sin programa identificado)
1. *"¿En qué etapa estás? Hola, espero que estés muy bien. Vi que nos escribiste hace poco, pero no sé si aún tienes claro cuál es tu siguiente paso o apenas estás explorando opciones. Solo por si te sirve: entiendo mejor a las familias y estudiantes para encontrar el mejor programa para estudiar fuera, dependiendo de su perfil, intereses y objetivos. Cuando quieras, podemos platicarlo sin compromiso. Aquí ando."*
2. *"¿Prefieres que te oriente? A veces lo más difícil no es encontrar programas, sino saber por dónde empezar. Si quieres, puedo orientarte con algunas preguntas rápidas para saber qué tipo de opciones te harían más sentido, sin compromiso. Me puedes decir si prefieres que te guíe paso a paso."*
3. *"Las rutas más comunes. Te comparto algo que sirve a muchas familias que apenas están explorando: 🏫 Internado (educación de alto nivel en el extranjero) 🎓 Año académico en familia anfitriona 🏕 Campamentos de verano ⭐ Pathway universitario 📚 Programas de estudio y trabajo. Cada ruta tiene perfiles distintos. Si me dices cuál te llama más la atención, te puedo ayudar a afinar cuál será para ti (o para tu hijo)."*
4. *"Aquí cuando lo necesites. Te agradezco mucho que nos hayas escrito. Entiendo que a veces no se sabe si se necesita más. Solo quería dejarte claro que si en algún momento quieres avanzar de nuevo, aquí estoy. Que tengas la mejor decisión, sea cual sea."* (última pausa de este flow es de 3 días, no 2 como los demás).

---

## 🆕 Outreach Form Meta — Touch 1/2/3 (verificados, ver `06_docs/template-texts-canonical.md`)

Estos 3 screenshots confirmaron palabra por palabra el texto que ya estaba documentado (y hardcodeado en los Code nodes de `outreach-form-meta-venttur-v5`) como "PENDIENTE DE COMPLETAR" — ya se actualizó ese doc quitando la marca de pendiente. No requirió cambios de contenido.

---

## Impacto en Etapa 1 / migración a GHL

1. **Nurturing de 4 toques por programa** (Boarding/AA Familiar/Gap Year/Pathway/Summer Camp/Lead General) es lógica de negocio sustancial que no estaba en ningún doc previo — hay que incorporarla al mapa funcional y recrearla como GHL Workflows con delays de 0/1/3/5 días.
2. **Número directo de Rodrigo** (+52 1 33 1944 2476) en el flow "Agenda" — dato de negocio a preservar.
3. **Debounce de 20 segundos** en "Recibir mensajes" — replicar en GHL o el lead va a recibir respuestas fragmentadas a mensajes seguidos.
4. **Flow "Elevar" con "Notify Assignees: 0 people"** — posible bug o config incompleta en producción, revisar con Max/Mauricio antes de migrar (si nadie se notifica hoy, el equipo humano podría no estar enterándose de escalamientos).
5. **Lista de 14 flows de `manychat-snapshot-2026-05-13.md` está desactualizada** — al menos 3 flows nuevos (Outreach Touch 1/2/3) se crearon después. Recomendado volver a correr el fetch de ManyChat (vía `VTR Data Export Runner v1`) antes de cerrar Etapa 1 para tener la lista de flows 100% actual.
