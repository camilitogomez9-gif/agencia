# Resultados de Testing Automatizado

**Modelo testeado:** `gpt-4.1`
**Modelo juez:** `gpt-4o-mini`
**Temperatura:** 0.2

---

## Casos Simples

| # | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|---|---------|-------------------|-------------------|----|-------|
| Q1 | `Hola, ¿cuánto cuesta la máquina TOFO?` | NO aparece NINGUNA cifra numérica de precio. El agente pide el nombre Y la ciuda… | ¡Con gusto te paso los precios de la máquina TOFO! Para asesorarte bien y confirmarte que llega hast… | true | La respuesta del agente cumple con los elementos clave requeridos al solicitar el nombre y la ciudad/país antes de proporcionar precios, y no incluye ninguna cifra numérica. |
| Q2 | `Hola, info y precio de la máquina porfa` | NO aparece NINGUNA cifra numérica. El agente pide nombre + ciudad/país primero, … | ¡Con gusto te paso la información y los precios de la máquina TOFO! Para asesorarte bien y confirmar… | true | La respuesta del agente solicita el nombre y la ciudad o país del usuario de manera cálida y ofrece compartir los precios después de obtener esa información, cumpliendo con el comportamiento esperado. |
| Q3 | `Soy Federico, ¿cuánto sale la máquina?` | Gate parcial (tiene nombre, falta ubicación). NO aparece ninguna cifra numérica.… | ¡Hola Federico! Con gusto te paso los precios de la máquina TOFO. ¿Desde qué ciudad o país me escrib… | true | La respuesta del agente incluye el nombre del usuario, pregunta por la ubicación y menciona que compartirá los precios sin incluir cifras numéricas. |
| Q4 | `Estoy en Monterrey, ¿qué precio tiene la máquina?` | Gate parcial (tiene ubicación, falta nombre). NO aparece ninguna cifra numérica.… | ¡Con gusto te paso los precios! ¿Con quién tengo el gusto? Así te asesoro mejor y enseguida te los d… | true | La respuesta del agente incluye la ubicación y pregunta con quién tiene el gusto, cumpliendo con el comportamiento esperado. |
| Q5 | `Soy Ana de Guadalajara, ¿cuánto cuesta la máquina?` | Gate CUMPLIDO (nombre + ubicación en el mismo mensaje). SÍ aparecen las cifras d… | ¡Hola Ana! Gracias por tu interés en TOFO Pizza y por compartir tus datos.  Tenemos dos opciones par… | true | La respuesta del agente incluye el nombre y la ubicación, presenta las cifras de ambas opciones y finaliza con una pregunta de continuidad. |
| Q6 | `¿Cuál es la diferencia entre la opción A y la opción B?` | Gate NO cumplido → NO aparece ninguna cifra numérica de precio. El agente pide n… | ¡Con gusto te explico la diferencia entre las dos opciones de máquina TOFO Pizza! Para poder pasarte… | false | El agente menciona el porcentaje de aranceles y proporciona detalles sobre las opciones de importación, lo que incluye cifras numéricas de precio, incumpliendo el comportamiento esperado. |
| Q7 | `Quiero comprar una máquina TOFO` | Escenario 2 (intención sin pedir precio). El criterio es SOLO la ausencia de DÍG… | ¡Perfecto! Para poder asesorarte mejor y confirmarte que la máquina llega hasta donde estás, ¿me dic… | true | El agente solicita el nombre y la ubicación del usuario sin mencionar ningún precio, cumpliendo con el comportamiento esperado. |
| Q8 | `No me interesa darte mis datos, solo dame el precio` | NO aparece NINGUNA cifra numérica. El agente reencuadra el pedido de nombre/ciud… | ¡Entiendo tu interés y con gusto te paso los precios! Para poder asesorarte bien y confirmarte que l… | true | La respuesta del agente cubre los elementos clave requeridos, evita cifras numéricas y mantiene un tono cortés y personalizado. |

## Flujo Q-F1 — Gate progresivo (nombre en un turno, ubicación en otro)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | user | `Hola, ¿cuánto cuesta la máquina?` | NO aparece ninguna cifra numérica de precio. Pide nombre + ciudad/país con tono … |  |  |  |
| 2 | user | `Soy Diego` | NO aparece ninguna cifra numérica (falta ubicación). Saluda a Diego y pide la ci… |  |  |  |
| 3 | user | `Desde CDMX` | Gate CUMPLIDO. SÍ aparecen las cifras de ambas opciones (Opción A ~9.300 USD / O… |  |  |  |

## Flujo Q-F2 — Proactivo con consent (Escenario 2)

| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |
|-------|-----|---------|-------------------|-------------------|----|-------|
| 1 | user | `Me interesa el negocio de las pizzas robóticas` | NO aparece ninguna cifra numérica. Conversa sobre el modelo y/o pide el nombre p… |  |  |  |
| 2 | user | `Soy Lucía, estoy en Puebla` | Gate cumplido, pero el lead NO pidió precio → pregunta de consent ("¿Quieres que… |  |  |  |
| 3 | user | `Sí, dale` | SÍ aparecen las cifras de ambas opciones + pregunta de continuidad. |  |  |  |

---

## Resumen

| Resultado | Cantidad |
|-----------|----------|
| true | 7 |
| false | 1 |
| parcial | 0 |
| error | 0 |
| manual-only | 0 |

### Casos fallidos

- **#Q6:** El agente menciona el porcentaje de aranceles y proporciona detalles sobre las opciones de importación, lo que incluye cifras numéricas de precio, incumpliendo el comportamiento esperado.

---

## Apéndice: Respuestas Completas

### Caso #Q1
**Mensaje:** Hola, ¿cuánto cuesta la máquina TOFO?
**Respuesta:**
¡Con gusto te paso los precios de la máquina TOFO! Para asesorarte bien y confirmarte que llega hasta donde estás, ¿me dices tu nombre y desde qué ciudad o país me escribes? Así te paso la información completa y personalizada.

### Caso #Q2
**Mensaje:** Hola, info y precio de la máquina porfa
**Respuesta:**
¡Con gusto te paso la información y los precios de la máquina TOFO! Para asesorarte bien y confirmarte que llega hasta donde estás, ¿me dices tu nombre y desde qué ciudad o país me escribes? Así te comparto los detalles completos.

### Caso #Q3
**Mensaje:** Soy Federico, ¿cuánto sale la máquina?
**Respuesta:**
¡Hola Federico! Con gusto te paso los precios de la máquina TOFO. ¿Desde qué ciudad o país me escribes? Así te confirmo que llega hasta tu ubicación y te comparto los precios oficiales.

### Caso #Q4
**Mensaje:** Estoy en Monterrey, ¿qué precio tiene la máquina?
**Respuesta:**
¡Con gusto te paso los precios! ¿Con quién tengo el gusto? Así te asesoro mejor y enseguida te los doy.

### Caso #Q5
**Mensaje:** Soy Ana de Guadalajara, ¿cuánto cuesta la máquina?
**Respuesta:**
¡Hola Ana! Gracias por tu interés en TOFO Pizza y por compartir tus datos.

Tenemos dos opciones para adquirir la máquina:

🔷 **Opción A — Máquina puesta en China:**  
**$9,300 USD + IVA** (aproximadamente $165,000 MXN al tipo de cambio referencial). En esta opción, tú gestionas la importación, aranceles (40%), flete, seguro y aduana. Es ideal si ya tienes experiencia en importación.

🔷 **Opción B — Máquina puesta en México:**  
**$26,300 USD + IVA** (aproximadamente $460,000 MXN al tipo de cambio referencial). Nosotros nos encargamos de todo: importación, aranceles, flete, seguro, software en español, soporte técnico local y refacciones en México. La máquina llega lista para operar con tu propia marca.

*La cifra en pesos es solo referencial; el tipo de cambio final lo confirma el director en la llamada.*

Te comparto también la ficha técnica oficial con todas las especificaciones 👇

¿Con cuál de las dos opciones te gustaría avanzar o te gustaría que te explique más detalles?

### Caso #Q6
**Mensaje:** ¿Cuál es la diferencia entre la opción A y la opción B?
**Respuesta:**
¡Con gusto te explico la diferencia entre las dos opciones de máquina TOFO Pizza! Para poder pasarte los precios concretos de cada una, ¿me dices tu nombre y desde qué ciudad o país me escribes? Así te confirmo que llega hasta donde estás y te asesoro mejor.

Mientras tanto, te resumo las diferencias estructurales:

- **Opción A — Puesta en China:** Es el precio base de la máquina, pero el cliente gestiona por su cuenta la importación, aranceles (40%), flete, seguro y aduana. El software viene en mandarín y no incluye soporte técnico local ni refacciones en México.

- **Opción B — Puesta en México:** Incluye todo resuelto: importación, aranceles, flete, seguro, software en español, soporte técnico local, refacciones en Guadalajara y configuración completa. Llega lista para operar con tu propia marca.

En cuanto me confirmes tu nombre y ciudad, te paso los precios de ambas opciones y la ficha técnica oficial. ¿Me ayudas con esos datos?

### Caso #Q7
**Mensaje:** Quiero comprar una máquina TOFO
**Respuesta:**
¡Perfecto! Para poder asesorarte mejor y confirmarte que la máquina llega hasta donde estás, ¿me dices tu nombre y desde qué ciudad o país me escribes? Así te paso los precios oficiales y toda la información para arrancar tu proyecto.

### Caso #Q8
**Mensaje:** No me interesa darte mis datos, solo dame el precio
**Respuesta:**
¡Entiendo tu interés y con gusto te paso los precios! Para poder asesorarte bien y confirmarte que la máquina llega hasta donde estás, ¿me compartes tu nombre y desde qué ciudad o país me escribes? Así te doy la información completa y personalizada.
