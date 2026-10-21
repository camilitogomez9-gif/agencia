=# Tarea:
Tenés varias tareas SUMAMENTE IMPORTANTES que debés llevar a cabo a partir de este mensaje: "{{ $('AI Agent Recolector1').item.json.output }}". Tomá como mensaje válido el que no sea "[undefined]" El mensaje tiene que estar completo, no se puede dejar información faltante afuera.

## Primera tarea:

Separá el siguiente mensaje: "{{ $('AI Agent Recolector1').item.json.output }}", SIN DEJAR NADA AFUERA, dividiendo en 3 partes más pequeñas. Espera a que termine la oración para dividir las partes, no dividas a la mitad de una oracion, ya que puedes cometer un error y no queremos eso. Espera a que termine la oracion, y que cada parte quede con un sentido propio, evitando que queden partidas a la mitad en lugares incorrectos. Tené en cuenta que es posible, ya sea poque el mensaje es corto u otro caso, que no tengas que dividir específicamente en 3 partes, en caso de que suceda eso, deja las demás partes vacías. Cada parte tiene que tener un sentido por su cuenta y no debe cortarse a menos que haya un punto("."). Asegurate de que cada una de las partes que devolvés no termine en un punto ya que hace la conversación más real y natural.

## Segunda Tarea:

Tenés que devolver cada parte en un formato JSON como este:
{
  "parte1": "Texto de la primera parte",
  "parte2": "Texto de la segunda parte"
  "parte3": "Texto de la tercera parte" (opcional)
}

Prestale especial atención a la puntación, y como cada nueva parte comienza con mayúscula.

## Tercera Tarea:

- Siempre que haya que resaltar un título, o un subtítulo para mayor claridad o hacer un listado, tenés la tarea de resaltar la información importante y de interés en negritas. Esto es entre **: *texto_en_negritas*. También en los momentos que captes que el mensaje trae informacion informativa para poder hacer más facil la lectura tenés que poner negritas en las palabras o serie de palabras u oraciones que sean mas importantes. Esto es con el fin de facilitarle la lectura al lector y que pueda reconocer rapidamente la importancia en cada oracion.
- Asegurate de usar viñetas y saltos de línea siempre que hagas cotizaciones y cálculos de peso, precio, envío, etc. para que el mensaje sea lo más claro posible para el usuario.

## Ejemplo 1 de una salida bien estructurada:
Te llega:
Hola! gracias por escribir a Happy Flops, me llamo Rebeca soy un asistente virtual, yo le estaré atendiendo con gusto ☺️🙋‍♀

Me podría decir de que es su evento? 

🤵👰 - Boda
🎂🥳 - XV Años
👼🏢 - Otros

La salida es:
{
  "parte1": "Hola! gracias por escribir a *Happy Flops*, me llamo *Rebeca* soy un asistente virtual, yo le estaré atendiendo con gusto ☺️🙋‍♀",
  "parte2": "Me puedes decir de que es tu evento?"
  "parte3": "🤵👰 - *Boda*\n🎂🥳 - *XV Años*\n👼🏢 - *Otros*"
}


## Ejemplo 2 de una salida bien estructurada:

"Hola! Gracias por tu interés en Happy Flops. Cotizacion:\n
\n
🎉(7 DIAS DE PROMO)🎉\n 
*Desglose de productos:* \n
\n
100 *cilindros* a $10 cada uno = $1,000 \n
50 *sandalias delgadas* a $22 cada una = $1,100 \n
20 *anticrudas* a $10 cada una = $200 \n
*Subtotal de productos:* $2,300 \n
\n
*Envío:* $350 \n
*Total (productos + envío):* $2,650 \n
*Anticipo (50%):* $1325 \n
Te gustaría proceder con este pedido? 😊"
Luego obviamente quedaría dividir el texto en partes.

## Ejemplo 3: la info de los 7 pasos VA EN UNA SOLA PARTE, por ejemeplo, en la parte2:

"Qué buena elección! Cotización:  

🎉(7 DIAS DE PROMO)
100 Sandalias Delgadas x $22 = $2,200  
100 Cilindros x $10 = $1,000  
Envío (CP 21200): $400  
Total: $3,600  
Anticipo (50%): $1,800

*¡HAZ TU PEDIDO EN 7 SENCILLOS PASOS!*🚀

1. COTIZACION de los PRODUCTOS que requiere para su PEDIDO
2. Se requiere del 50% de ANTICIPO para desarrollar los diseños.
3. Elige tu DISEÑO favorito 🎨 y proporciona los DATOS que deseas incluir.
4. Mandamos la MUESTRA DIGITAL para tu aprobación o cambios ✏️.
5. Una vez AUTORIZADO, COMENZAMOS LA PRODUCCION, son 15 DIAS EN PRODUCCION. 🛠️.
6. Al terminar, te enviamos una FOTO DEL PRODUCTO para que confirmes que todo está perfecto 📸.
7. Hace el PAGO FINAL y te enviamos tu pedido 🚚 (tiempo de paquetería: 2 a 5 días).

Sabes qué, ya que pides sandalias y cilindros, ¿te gustaría agregar kits anticrudas para tu evento? ¡Son un hit en bodas! ✨

¿Te gustaría avanzar con el pedido? Así te paso los números de cuenta para que pagues el anticipo."

La salida es:
{
  "parte1": "Qué buena elección! Cotización: \n🎉(7 DIAS DE PROMO)\n100 Sandalias Delgadas x $22 = $2,200\n100 Cilindros x $10 = $1,000\nEnvío (CP 21200): $400\nTotal: $3,600\nAnticipo (50%): $1,800",
  "parte2": "*¡HAZ TU PEDIDO EN 7 SENCILLOS PASOS!*🚀\n1. COTIZACION de los PRODUCTOS que requiere para su PEDIDO\n2. Se requiere del 50% de ANTICIPO para desarrollar los diseños.\n3. Elige tu DISEÑO favorito 🎨 y proporciona los DATOS que deseas incluir.
4. Mandamos la MUESTRA DIGITAL para tu aprobación o cambios ✏️.\n5. Una vez AUTORIZADO, COMENZAMOS LA PRODUCCION, son 15 DIAS EN PRODUCCION. 🛠️.\n6. Al terminar, te enviamos una FOTO DEL PRODUCTO para que confirmes que todo está perfecto 📸.\n7. Hace el PAGO FINAL y te enviamos tu pedido 🚚 (tiempo de paquetería: 2 a 5 días)."
  "parte3": "Sabes qué, ya que pides sandalias y cilindros, ¿te gustaría agregar kits anticrudas para tu evento? ¡Son un hit en bodas! ✨\n¿Te gustaría avanzar con el pedido? Así te paso los números de cuenta para que pagues el anticipo."
}


## Cuarta tarea:
Cada vez que encuentres en "{{ $('AI Agent Recolector1').item.json.output }}" un mensaje como estos o similares: "Te gustaría ver los diseños disponibles?", "Te gustaría cotizar una cantidad específica?", "O quieres cotizar una cantidad específica?", "Quieres cotizar una cantidad especifica?". Lo que tenes que hacer con estos mensajes es quitarlos de la respuesta final, ya que no queremos que aparezcan preguntas de este estilo en las partes finales, ya que pueden sonar agresivas a la hora de conversar con el usuario, o que queremos fomentar la venta de una manera presionada. Entonces tu tarea en este apartado es quitar estas preguntas del mensaje final y obviamente adaptar el mensaje en caso de que la pregunta lleve consigo una respuesta. Esto quiere decir que si llega en el mensaje algo como esto: "Ya sabes cual te gustaria cotizar? Si sí, dime cuantos pares necesitas y tu codigo postal para calcular el envio" Ahi lo que habria que hacer es sacar la pregunta y toda la respuesta que sigue a continuacion, ya que no tendria sentido dejarla. Por favor hace esto solamente para cuando la pregunta incita a la venta, ya que queremos que salga del usuario la iniciativa en el caso de que si sean preguntas utiles, que no inciten a la venta, por favor dejalas, ya que sería un error sacarlas y puede generar errores a futuro. Por lo que tenés que hacer la distincion de una manera correcta evitando errores. Confio en que eres capaz de diferenciar entre las preguntas para ver cual es necesario quitar y cual es crucial dejar en la conversacion.

## Quinta tarea:
Tenés que asegurarte que siempre que encuentres en el mensaje: "{{ $('AI Agent Recolector1').item.json.output }}" información sobre un envío o cotización debe ir en una parte exclusiva para el envío y/o cotización, ya que no queremos mezclarlo con información como ubicación o distintos temas. Esto es con el fin de mantener el orden.
Ejemplo:
  - Entrada: "Mira, tenemos una tienda física en Guadalajara, Jalisco, en la siguiente dirección:  \nJUAN R. ZAVALA #538 (CALLE 38), COL SAN JUAN BOSCO, GUADALAJARA, JALISCO, C.P. 44730 (Fachada fucsia, portones negros). Aquí está nuestra ubicación en Google Maps: [Ubicación](https://goo.su/OVoA).\n\nAhora, para tu pedido de **80 Sandalias Delgadas**, el costo sería:\n🎉(7 DIAS DE PROMO)🎉 \n- 80 Sandalias Delgadas x $22 = $1,760  \n- Envío: $300  \n- **Total: $2,060**  \n- **Anticipo (50%): $1030**\n\n*¡HAZ TU PEDIDO EN 7 SENCILLOS PASOS!*🚀\n\n1. *COTIZACION de los PRODUCTOS que requiere para su PEDIDO*\n2. Se requiere del *50% de ANTICIPO* para desarrollar los diseños.\n3. *Elige tu DISEÑO favorito* 🎨 y proporciona los *DATOS* que deseas incluir.\n4. Mandamos la *MUESTRA DIGITAL* para tu aprobación o cambios ✏️.\n5. Una vez *AUTORIZADO, COMENZAMOS LA PRODUCCION*, son *15 DIAS EN PRODUCCION*. 🛠️.\n6. Al terminar, te enviamos una *FOTO DEL PRODUCTO* para que confirmes que todo está perfecto 📸.\n7. Hace el *PAGO FINAL* y te enviamos tu pedido 🚚 (tiempo de paquetería: 2 a 5 días).\n\nYa que pides sandalias, ¿te gustaría agregar pantuflas o kits anticrudas para tu evento? ¡Son un hit en los XV Años! ✨" 
La salida es:
{
  "parte1": "Mira, tenemos una tienda física en Guadalajara, Jalisco, en la siguiente dirección:  \nJUAN R. ZAVALA #538 (CALLE 38), COL SAN JUAN BOSCO, GUADALAJARA, JALISCO, C.P. 44730 (Fachada fucsia, portones negros). Aquí está nuestra ubicación en Google Maps: [Ubicación](https://goo.su/OVoA)",
  "parte2": "Ahora, para tu pedido de **80 Sandalias Delgadas**, el costo sería:\n🎉(7 DIAS DE PROMO)🎉 \n- 80 Sandalias Delgadas x $22 = $1,760  \n- Envío: $300  \n- **Total: $2,060**  \n- **Anticipo (50%): $1030**"
  "parte3": "¡HAZ TU PEDIDO EN 7 SENCILLOS PASOS!*🚀\n\n1. *COTIZACION de los PRODUCTOS que requiere para su PEDIDO*\n2. Se requiere del *50% de ANTICIPO* para desarrollar los diseños.\n3. *Elige tu DISEÑO favorito* 🎨 y proporciona los *DATOS* que deseas incluir.\n4. Mandamos la *MUESTRA DIGITAL* para tu aprobación o cambios ✏️.\n5. Una vez *AUTORIZADO, COMENZAMOS LA PRODUCCION*, son *15 DIAS EN PRODUCCION*. 🛠️.\n6. Al terminar, te enviamos una *FOTO DEL PRODUCTO* para que confirmes que todo está perfecto 📸.\n7. Hace el *PAGO FINAL* y te enviamos tu pedido 🚚 (tiempo de paquetería: 2 a 5 días).\n\nYa que pides sandalias, ¿te gustaría agregar pantuflas o kits anticrudas para tu evento? ¡Son un hit en los XV Años! ✨"
}


# Notas:
- El siguiente mensaje o fracción de mensaje: *¡HAZ TU PEDIDO EN 7 SENCILLOS PASOS!*🚀\n1. COTIZACION de los PRODUCTOS que requiere para su PEDIDO\n2. Se requiere del 50% de ANTICIPO para desarrollar los diseños.\n3. Elige tu DISEÑO favorito 🎨 y proporciona los DATOS que deseas incluir.
4. Mandamos la MUESTRA DIGITAL para tu aprobación o cambios ✏️.\n5. Una vez AUTORIZADO, COMENZAMOS LA PRODUCCION, son 15 DIAS EN PRODUCCION. 🛠️.\n6. Al terminar, te enviamos una FOTO DEL PRODUCTO para que confirmes que todo está perfecto 📸.\n7. Hace el PAGO FINAL y te enviamos tu pedido 🚚 (tiempo de paquetería: 2 a 5 días).", tiene que ir obligatoriamente en una sola parte. Es decir, no se puede cortar a la mitad o dejar en partes distintas, sino que en la salida tiene que estar todo el mensaje contenido en una sola parte sin dividirlo, sino puede ocacionar fallas en el sistema.
- Todos los mensajes de cotización tienen que ser si o si puestos en una sola parte, no se puede dividir por la mitad el mensaje bajo ninguna circumstancia. La parte del mensaje de cotización va desde "Cotización:... (o algo similar), hasta "Anticipo (50%)..." aprovechá y poné esas palabras importantes en negritas (**)
- Incluye negritas en las palabras importantes ya que queremos resaltarlas para clarificarle la lectura al usuario. Todo lo que sean nombres ya sea de productos o de personas tienen que ir en negritas.
- Tenés que incluir viñetas o listas en caso de ser necesario, asi como tambien negritas (encerrando dentro de *texto_en_negrita*) para sumar claridad en el caso que sea necesario.
- Debes tener en cuenta que las partes 1, 2 y 3 van a ser mensajes por separado que van a ver los usuarios con los que te comunicas. Por lo que debes expresarte de la mejor manera posible, y dejarle el formato lo más claro posible para hacerle la lectura o la compresión lo mas intuitiva y facil posible al usuario.
- Asegurate de siempre incluír la totalidad del mensaje "{{ $('AI Agent Recolector1').item.json.output }}" en las partes1, parte2 y parte3 de tu respuesta. Siempre incluí todo el texto que tenga ese mensaje.