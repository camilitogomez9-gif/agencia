# Decisiones abiertas — bot nuevo de Happy Flops

**Para:** Juanpi · **Fecha:** 2026-08-05 · **v2**

> **Por qué hay una v2.** La v1 estaba escrita en jerga y Juanpi dijo, textual, que no entendió cuatro
> de las seis. Eso es culpa del doc, no de él: si el que tiene que decidir no entiende la pregunta, la
> pregunta está mal escrita. Esta versión no tiene términos técnicos.

Todas están **funcionando ya con una decisión tomada por defecto**. Nada está frenado esperando. Lo
que sigue es para que confirmes o cambies. Al final de cada una dice cuánto cuesta cambiarla.

---

## ✅ D-01 — RESUELTA · Cuando el lead pide "todos los productos"

**Qué pasaba.** El bot viejo, si el lead decía *"precio de todos"* en unos XV, le mandaba **también
mandiles**, que son solo para bodas.

**Tu respuesta (audio del 5/8):** *"Si dice que quiere todos y todavía no sabe el evento, se le
pregunta el evento. Si la conversación ya trae el evento y dice 'todos', es solo lo del evento — no se
puede escapar del evento."*

**Queda así.** En unos XV, "todos" = solo los productos de XV, sin mandiles. Y si todavía no sabe de
qué es el evento, primero pregunta. Agregué un caso de prueba para esa segunda parte.

---

## ✅ D-02 — RESUELTA · Los textos de los productos

**Decisión de la agencia (5/8):** *"corregí las erratas… los mandamos como los manda el bot hoy"*.

**Queda así:** la referencia para comparar es **el texto que manda el bot hoy**. Las dos erratas de
Oscar —la comilla suelta en sandalias, el primer renglón pegado en mandiles— quedan corregidas, y el
separador de línea vacía se mantiene como está.

> ⚠️ **Con una excepción que la decisión no cubría, y que NO es una errata.**
> La ficha de la pantufla de peluche tiene una diferencia de **contenido**, no de tipeo:
>
> | | Colores |
> |---|---|
> | Oscar, 1/8 15:07 | `blanca, negra, morada y rosa` |
> | **Oscar, 3/8 17:30 y 17:38** (lo corrigió dos veces, XV y Boda) | `blanca, negra, morada, rosa` |
> | El bot hoy | `blanca, negra, morada y rosa` ← quedó con la versión vieja |
>
> Aplicar acá la regla "como lo manda el bot hoy" sería **descartar en silencio una corrección que el
> cliente pidió expresamente**. Queda registrado como hallazgo pendiente (`HPF-FIC-035`), no como
> decisión de verbatim. **Costo de aplicarlo: 2 minutos.**

---

## ✅ D-03 — RESUELTA · La espera va en 50 segundos

**Decisión de la agencia (5/8):** 50 segundos.

**Queda así:** al terminar el testing, el nodo de espera se reactiva en **50 s**, no en 15. Eso además
lo deja coherente con la regla interna que ya usaba 50. Anotado en la deuda de test, y se verifica
exportando el flujo de nuevo, no de memoria.

> Nota: el nodo se llama `Wait 15s (Debounce)`. Conviene renombrarlo al cambiarlo, o el próximo que lo
> lea va a asumir 15.

---

## ✅ D-05 — RESUELTA · La octava regla se queda

**Decisión de la agencia (5/8):** *"La decisión es correcta. NO lo saques."*

El bot nuevo siempre tiene que contestar algo. Queda como `HPF-NRP-025`, severidad S1.

---

## 📎 Anexo — la versión original de D-02, por si hace falta el contexto

Esta es la que no se entendió. Va con el ejemplo concreto.

**El problema.** Cuando el bot manda la ficha de un producto —el bloque con el precio, el mínimo, los
colores— hay **tres versiones distintas de ese mismo texto** dando vueltas, y no coinciden:

1. La que manda el bot **hoy**.
2. La que mandaba el bot **viejo** de Kommo.
3. La que **Oscar escribió por WhatsApp** el sábado 1/8 y corrigió el domingo 3/8.

Las diferencias son chiquitas, pero son justo el tipo de cosa que Oscar mira. Ejemplos reales, sacados
de comparar los textos uno contra otro:

| | Oscar escribió | El bot manda hoy |
|---|---|---|
| Pantufla de peluche, colores | `blanca, negra, morada, rosa` | `blanca, negra, morada y rosa` |
| Sandalias, mínimo | `📦 Pedido mínimo de 50 pares."` ← con una comilla de más | `📦 Pedido mínimo de 50 pares.` |
| Mandiles, primera línea | `✨ Mandiles🍾 Ideales para el novio…` ← todo pegado | partido en dos renglones |

**Por qué importa para el testing.** Yo tengo que comparar lo que manda el bot contra *algo*. Si
comparo contra el texto equivocado, voy a reportar como error algo que está bien, o peor, voy a dar
por bueno algo que Oscar va a rechazar. Necesito saber cuál de las tres versiones es "la correcta".

**Lo que ya sabemos:** Oscar dijo el 3/8, textual: *"pongan las descripciones que les pasé el sábado"*.
Así que la referencia son sus textos. **Eso ya está decidido por él.**

**Lo que queda por decidir, y es lo único que te pregunto:** en los textos que mandó Oscar hay dos
cosas que parecen errores de tipeo suyos —la comilla de más en sandalias y el renglón pegado en
mandiles. ¿Los copiamos igual, tal cual los escribió, o los corregimos?

- **Copiarlos tal cual** → el bot queda idéntico a lo que él pidió, erratas incluidas.
- **Corregirlos** → queda más prolijo, pero si él compara carácter por carácter va a ver una diferencia.

**Mi recomendación:** corregir esas dos y avisarle en una línea. **Costo de cambiar de opinión:** 5 minutos.

---

## ⚠️ D-03 — El bot está esperando 15 segundos, pero vos dijiste 50

**Qué es.** El bot espera un rato antes de contestar, para juntar los mensajes del lead. Si alguien
escribe *"hola"*, *"quiero sandalias"*, *"para una boda"* en tres mensajes seguidos, la espera hace que
conteste **una vez a las tres cosas** en vez de tres veces por separado.

**El problema.** Hay tres números distintos y ninguno coincide:

- El bot tiene configurado **15 segundos**.
- Vos dijiste en el audio: *"el wait que usábamos nosotros era de 50 segundos"*.
- Y adentro hay una regla escondida que también dice **50 segundos**.

**Por qué importa.** Si testeo con 15 y en producción son 50 (o al revés), estoy midiendo un bot
distinto al que usa el cliente. Y Oscar ya se quejó de que el bot *"contesta de a poquito"*, que es
exactamente lo que pasa cuando la espera es corta.

**Lo que necesito:** que me confirmes cuál es el número que va a producción. **Costo:** un minuto.

---

## ✅ D-04 — RESUELTA · Hay un caso donde el lead no recibe absolutamente nada

**Qué pasa.** Si el lead manda algo que no es texto, ni foto, ni audio —un sticker, por ejemplo— el bot
**no contesta nada**. Ni un error, ni un "no entendí". Silencio. Y del lado nuestro figura como que
todo salió bien, así que nadie se entera.

**Decisión de la agencia:** entra al alcance, se arregla. Va a ser un mensaje genérico del estilo *"no pude
leer eso, ¿me lo escribís?"*. **Costo:** ~15 minutos.

---

## 📋 D-05 — Por qué agregué una regla que no estaba en la lista

Dijiste: *"no entiendo por qué carajo está eso"*. Es justo.

**De dónde salió.** Para saber cómo se comportaba el bot viejo, saqué 10 conversaciones reales de
producción. En esas 10 conversaciones el bot viejo, **13 veces**, no contestó nada. El lead escribía,
no recibía respuesta, volvía a escribir lo mismo, y así cinco o seis veces seguidas contra el silencio.

**Por qué lo agregué a la lista.** La lista original tenía 7 cosas que el bot viejo hacía mal y que **a
propósito no queremos copiar**. "Quedarse mudo" no estaba en esa lista, y para un negocio que vende por
WhatsApp es probablemente la peor de todas: el lead se va y nadie se entera de que se fue.

Así que agregué una octava: **el bot nuevo siempre tiene que contestar algo.**

**No te estoy pidiendo nada acá** — es un aviso. Si te parece que no corresponde, la saco.

---

## 📋 D-06 — Dos errores del protocolo que ya corregí

Esto es interno, no necesitás hacer nada. Lo dejo escrito para que quede el registro.

1. El documento del protocolo decía que faltaba escribir qué tiene que hacer el bot nuevo en lugar de
   cada cosa que el viejo hacía mal. **Ya estaba escrito**, en tres documentos del repo que el
   protocolo no listaba. Ahorró rehacer el trabajo.
2. El protocolo atribuía esas 7 reglas a una reunión del 12 de mayo. **Salen de otra, del 26 de mayo.**

---

## Y una cosa que no es decisión, es un número

El bot nuevo **no tiene reactivadores**: eso de volver a escribirle al lead que dejó de contestar a la
hora, a las 3 horas, a las 8 y a las 24.

El bot viejo tenía **41 de sus 146 flujos** dedicados solo a eso, más 4 procesos aparte.
El nuevo tiene **cero**.

Es cerca de un **tercio de todo lo que hacía el bot viejo**, no se arregla con este testing, y ninguna
prueba de conversación lo va a mostrar. **Si Oscar dice que el bot nuevo vende menos, esta es
probablemente la razón principal**, y conviene que lo sepamos antes de que lo diga él.
