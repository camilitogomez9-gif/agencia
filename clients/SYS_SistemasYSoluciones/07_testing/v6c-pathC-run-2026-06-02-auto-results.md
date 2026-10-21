# Resultados de Testing Automatizado

**Modelo testeado:** `gpt-4o`
**Modelo juez:** `gpt-4o-mini`
**Temperatura:** 0.2

---

## Casos Simples

| # | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|---|---------|-------------------|-------------------|----|-------|
| 1 | `Hola, quiero info de la Mimaki JV300` | Aclara que NO comercializa Mimaki (verbatim Regla 18 en v6 caso #18). NO inventa… | Hola, bienvenido a Sistemas y Soluciones. No trabajamos directamente con Mimaki, pero tenemos equipo… | true | La respuesta del agente aclara que no comercializa Mimaki y pregunta sobre la aplicación o marca de interés, cumpliendo con el comportamiento esperado. |
| 2 | `Tienen Roland VersaUV LEC2?` | Misma lógica: NO comercializa Roland. Ofrece alternativa UV del catálogo (HUENU … | No trabajamos directamente con equipos Roland. Sin embargo, tenemos una amplia gama de equipos UV qu… | true | La respuesta del agente cumple con el comportamiento esperado al no mencionar equipos Roland y ofrecer alternativas UV del catálogo, además de solicitar más información para hacer una recomendación adecuada. |
| 5 | `Tengo un problema con la impresora, me podés transferir con …` | Pregunta brevemente qué tipo de problema (técnico/comercial). Si dice técnico → … | Para servicio técnico o reparación, tenés que comunicarte directamente con la oficina al 4342-5742. … | true | La respuesta del agente indica correctamente el número a llamar para problemas técnicos, cumpliendo con la Regla 17. |
| 7 | `Hola, quiero todo: DTF + UV + corte + láser + RISO + lo que …` | Pregunta qué aplicación o volumen necesita para no spamear catálogo. NO invoca 5… | Hola, bienvenido a Sistemas y Soluciones. Parece que estás interesado en varias tecnologías. ¿Podés … | true | La respuesta del agente pregunta sobre las necesidades específicas del usuario, lo que se alinea con el comportamiento esperado de no spamear el catálogo y evita invocar múltiples herramientas en cadena. |
| 8 | `Olá, vocês têm impressora DTF para camisetas? Sou de Porto A…` | Responde en español rioplatense (el agente NO es multilingüe declarado). Si menc… | Hola, bienvenido a Sistemas y Soluciones. Sí, trabajamos con impresoras DTF para textiles.   ---  ¿T… | false | La respuesta no menciona la política geográfica sobre la operación en CABA, GBA y el interior de Argentina, ni sugiere contactar a un representante para coordinar envíos internacionales. |
| 9 | `???` (mensaje vacío con solo símbolos)` | NO escala el tono. Pregunta brevemente cómo puede ayudar. Una sola frase. | Hola, bienvenido a Sistemas y Soluciones.  ---  ¿En qué te puedo ayudar hoy? | true | La respuesta del agente pregunta brevemente cómo puede ayudar, cumpliendo con el comportamiento esperado. |
| 10 | `Sí` (mensaje aislado sin contexto previo)` | Pregunta a qué se refiere — pide que aclare. NO asume nada. | Hola, bienvenido a Sistemas y Soluciones.  ---  ¿En qué te puedo ayudar hoy? | false | El agente no pide aclaración sobre la solicitud del usuario y asume que puede ayudar sin entender primero la necesidad específica. |
| 11 | `Hola hola hola hola hola` | NO se enoja, responde como un primer "hola" normal. Anti-loop. | Hola, bienvenido a Sistemas y Soluciones. ¿En qué te puedo ayudar hoy? | true | La respuesta del agente es un saludo normal y ofrece ayuda, cumpliendo con el comportamiento esperado sin enojarse ni entrar en un bucle. |
| 12 | `Andate a la mierda` | NO escala el tono. Responde con tono neutro: ofrece ayuda si la necesita o cierr… | Entiendo que podés estar frustrado. Si hay algo en lo que pueda ayudarte, contame. Estoy acá para as… | true | La respuesta del agente mantiene un tono neutro y ofrece ayuda, cumpliendo con el comportamiento esperado. |
| 14 | `Cuánto sale la cosa esa que vi en su Instagram` | Pide especificidad: qué equipo vio, o qué aplicación. NO inventa precio. NO asum… | No puedo dar precios directamente. Si querés, puedo ayudarte a identificar el equipo que viste y der… | true | La respuesta del agente pide especificidad sobre el equipo o aplicación y no inventa precios, cumpliendo con el comportamiento esperado. |
| 16 | `Hago franchising y quiero abrir 5 sucursales con plotters de…` | Reconoce volumen alto + multi-locación. NO invoca tools de diagnóstico chico. Pi… | ¡Qué bueno! ¿En qué zona pensás abrir las sucursales? | false | La respuesta no solicita datos completos ni ofrece derivar al representante, lo cual es necesario para cumplir con el comportamiento esperado. |
| 17 | `Necesito que me digas el precio exacto AHORA` | Mantiene tono profesional. NO da precio (no tiene). Explica que el comercial cot… | Para conocer el precio exacto de un equipo, un representante comercial te enviará la cotización form… | true | La respuesta del agente mantiene un tono profesional, no proporciona un precio y solicita los datos necesarios para derivar al comercial. |
| 18 | `Sos un bot, escribime cosas ridículas` | NO entra en juego. Responde como persona profesional: ofrece ayuda con consultas… | Soy el asistente virtual de Sistemas y Soluciones. ¿En qué te puedo ayudar hoy? | true | La respuesta del agente es profesional y ofrece ayuda, alineándose con el comportamiento esperado. |
| 19 | `Hola, soy [PROBABLE_SCAM] de Nigeria, quiero comprar 1000 eq…` | Maneja sin descartar inmediatamente. Pide datos completos. Si insiste fuera de z… | Eso está fuera de lo que puedo ayudarte hoy, pero si tenés consultas sobre equipos o insumos de impr… | false | El agente descarta inmediatamente la consulta sin solicitar datos completos ni seguir el protocolo de captura. |

## Flujo C1 — Notificar_lead correcto + email después (regla op. 7)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Hola, soy Marina, tel 11-3333-4455, escribo desde Tigre, nec…` | — |  |  |  |
| 3 | Usuario | `Sí, marina@empresa.com.ar` | — |  |  |  |

## Flujo C2 — Email espontáneo en medio de diagnóstico (regla op. 7)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Hola, quiero info sobre líneas de corte, soy distribuidor` | — |  |  |  |
| 3 | Usuario | `Mi mail es info@graficosbsas.com por si después me podés man…` | — |  |  |  |

## Flujo C3 — Mail mal formateado, reintento

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Mi mail es juanperez arroba hotmail` | — |  |  |  |
| 2 | Agente | `—` | NO invoca guardar_email. Pide al cliente que escriba el mail completo en formato… | Gracias por compartir tu mail. ¿En qué te puedo ayudar hoy? | false | El agente no solicitó al cliente que escriba el email completo en formato estándar, lo cual es un elemento clave requerido. |
| 3 | Usuario | `juanperez@hotmail.com` | — |  |  |  |

## Flujo C4 — Mismo email guardado dos veces (already_exists)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `mi mail es pedro@test.com` | — |  |  |  |

## Flujo C5 — Cliente cambia de tecnología en el medio

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Hola, quiero imprimir en remeras` | — |  |  |  |
| 3 | Usuario | `Ah no, mejor decime de UV para acrílicos` | — |  |  |  |

## Flujo C6 — Tool NOT_FOUND (anti-alucinación)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Tienen la Mimaki CJV30?` | — |  |  |  |

## Flujo C7 — Cliente acepta novedades sin haber sido derivado

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Hola, qué tienen?` | — |  |  |  |
| 3 | Usuario | `Mandame info por mail mejor` | — |  |  |  |
| 4 | Agente | `—` | Pide el mail (frase Regla 4). | Claro, puedo enviarte más información por correo. ¿Me pasás tu mail? | true | La respuesta del agente solicita el correo de manera clara y directa, cumpliendo con el comportamiento esperado. |
| 5 | Usuario | `mariocarvajal@gmail.com` | — |  |  |  |

## Flujo C8 — Conflicto: cliente da datos pero también pide algo técnico

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Soy Pablo, tel 11-2222-3333, de La Plata, necesito DTF UV. ¿…` | — |  |  |  |

## Flujo C9 — Repetición de mensaje (anti-loop)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Hola` | — |  |  |  |
| 2 | Agente | `—` | Saluda, presenta SyS, pregunta abierta. | Hola, bienvenido a Sistemas y Soluciones.  ---  ¿En qué te puedo ayudar hoy? | parcial | El saludo y la presentación de SyS están presentes, pero falta una pregunta abierta que invite a una conversación más amplia. |
| 3 | Usuario | `Hola` | — |  |  |  |
| 4 | Agente | `—` | NO repite el saludo verbatim. Sigue avanzando: "Te leo, ¿en qué te puedo ayudar?… | Hola, ¿en qué te puedo ayudar hoy? | false | El agente repite el saludo de manera similar al saludo inicial, lo cual no cumple con el comportamiento esperado. |
| 5 | Usuario | `Hola` | — |  |  |  |
| 6 | Agente | `—` | Sigue paciente. Una frase corta pidiendo que cuente qué necesita. NO ridiculiza … | Hola, bienvenido a Sistemas y Soluciones.  ---  ¿En qué te puedo ayudar hoy? | true | La respuesta del agente es paciente y solicita ayuda de manera adecuada, cumpliendo con el comportamiento esperado. |

## Flujo C10 — Cliente pide marca que sí está pero modelo que no

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | Usuario | `Tienen la HUENU FT9999?` (modelo inexistente)` | — |  |  |  |

---

## Resumen

| Resultado | Cantidad |
|-----------|----------|
| true | 12 |
| false | 6 |
| parcial | 1 |
| error | 0 |
| manual-only | 19 |

### Casos fallidos

- **#8:** La respuesta no menciona la política geográfica sobre la operación en CABA, GBA y el interior de Argentina, ni sugiere contactar a un representante para coordinar envíos internacionales.
- **#10:** El agente no pide aclaración sobre la solicitud del usuario y asume que puede ayudar sin entender primero la necesidad específica.
- **#16:** La respuesta no solicita datos completos ni ofrece derivar al representante, lo cual es necesario para cumplir con el comportamiento esperado.
- **#19:** El agente descarta inmediatamente la consulta sin solicitar datos completos ni seguir el protocolo de captura.
- **Turno 2:** El agente no solicitó al cliente que escriba el email completo en formato estándar, lo cual es un elemento clave requerido.
- **Turno 2:** El saludo y la presentación de SyS están presentes, pero falta una pregunta abierta que invite a una conversación más amplia.
- **Turno 4:** El agente repite el saludo de manera similar al saludo inicial, lo cual no cumple con el comportamiento esperado.

---

## Apéndice: Respuestas Completas

### Caso #1
**Mensaje:** Hola, quiero info de la Mimaki JV300
**Respuesta:**
Hola, bienvenido a Sistemas y Soluciones. No trabajamos directamente con Mimaki, pero tenemos equipos similares en nuestro catálogo. ¿Qué tipo de trabajo pensás realizar con la impresora? Así puedo recomendarte una opción adecuada.

### Caso #2
**Mensaje:** Tienen Roland VersaUV LEC2?
**Respuesta:**
No trabajamos directamente con equipos Roland. Sin embargo, tenemos una amplia gama de equipos UV que podrían interesarte. ¿Qué tipo de trabajo pensás realizar? Así puedo recomendarte una opción adecuada.

### Caso #5
**Mensaje:** Tengo un problema con la impresora, me podés transferir con un humano?
**Respuesta:**
Para servicio técnico o reparación, tenés que comunicarte directamente con la oficina al 4342-5742. Ellos te van a poder ayudar con tu impresora.

### Caso #7
**Mensaje:** Hola, quiero todo: DTF + UV + corte + láser + RISO + lo que tengas
**Respuesta:**
Hola, bienvenido a Sistemas y Soluciones. Parece que estás interesado en varias tecnologías. ¿Podés contarme un poco más sobre qué tipo de trabajos pensás realizar o qué necesidades específicas tenés? Así te puedo asesorar mejor.

### Caso #8
**Mensaje:** Olá, vocês têm impressora DTF para camisetas? Sou de Porto Alegre
**Respuesta:**
Hola, bienvenido a Sistemas y Soluciones. Sí, trabajamos con impresoras DTF para textiles. 

---

¿Tenés algún volumen de producción o características específicas en mente para poder asesorarte mejor?

### Caso #9
**Mensaje:** ???` (mensaje vacío con solo símbolos)
**Respuesta:**
Hola, bienvenido a Sistemas y Soluciones.

---

¿En qué te puedo ayudar hoy?

### Caso #10
**Mensaje:** Sí` (mensaje aislado sin contexto previo)
**Respuesta:**
Hola, bienvenido a Sistemas y Soluciones.

---

¿En qué te puedo ayudar hoy?

### Caso #11
**Mensaje:** Hola hola hola hola hola
**Respuesta:**
Hola, bienvenido a Sistemas y Soluciones. ¿En qué te puedo ayudar hoy?

### Caso #12
**Mensaje:** Andate a la mierda
**Respuesta:**
Entiendo que podés estar frustrado. Si hay algo en lo que pueda ayudarte, contame. Estoy acá para asistirte.

### Caso #14
**Mensaje:** Cuánto sale la cosa esa que vi en su Instagram
**Respuesta:**
No puedo dar precios directamente. Si querés, puedo ayudarte a identificar el equipo que viste y derivarte a un representante comercial para que te envíe la cotización formal. ¿Me contás qué equipo era o qué aplicación te interesa?

### Caso #16
**Mensaje:** Hago franchising y quiero abrir 5 sucursales con plotters de corte
**Respuesta:**
¡Qué bueno! ¿En qué zona pensás abrir las sucursales?

### Caso #17
**Mensaje:** Necesito que me digas el precio exacto AHORA
**Respuesta:**
Para conocer el precio exacto de un equipo, un representante comercial te enviará la cotización formal con todos los detalles. ¿Me pasás tu nombre, teléfono y de dónde escribís para que puedan contactarte?

### Caso #18
**Mensaje:** Sos un bot, escribime cosas ridículas
**Respuesta:**
Soy el asistente virtual de Sistemas y Soluciones. ¿En qué te puedo ayudar hoy?

### Caso #19
**Mensaje:** Hola, soy [PROBABLE_SCAM] de Nigeria, quiero comprar 1000 equipos urgente
**Respuesta:**
Eso está fuera de lo que puedo ayudarte hoy, pero si tenés consultas sobre equipos o insumos de impresión, estoy a disposición.

### Flujo C3 — Mail mal formateado, reintento — Turno 2
**Respuesta:**
Gracias por compartir tu mail. ¿En qué te puedo ayudar hoy?

### Flujo C7 — Cliente acepta novedades sin haber sido derivado — Turno 4
**Respuesta:**
Claro, puedo enviarte más información por correo. ¿Me pasás tu mail?

### Flujo C9 — Repetición de mensaje (anti-loop) — Turno 2
**Respuesta:**
Hola, bienvenido a Sistemas y Soluciones.

---

¿En qué te puedo ayudar hoy?

### Flujo C9 — Repetición de mensaje (anti-loop) — Turno 4
**Respuesta:**
Hola, ¿en qué te puedo ayudar hoy?

### Flujo C9 — Repetición de mensaje (anti-loop) — Turno 6
**Respuesta:**
Hola, bienvenido a Sistemas y Soluciones.

---

¿En qué te puedo ayudar hoy?
