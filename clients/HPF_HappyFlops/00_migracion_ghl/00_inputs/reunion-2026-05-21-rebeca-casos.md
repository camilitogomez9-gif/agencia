# Reunión Happy Flops — 2026-05-21 (Rebeca: revisión de casos)

> **Fuente:** grabación Fathom (54 min) — https://fathom.video/share/gDXbtkz6nxAsbc1Z9BJBM9ovWyPrELTN
> **Participantes:** Oscar (HappyFlops), Rebeca Cisneros (atención al cliente HPF), la agencia (la agencia), Juan Pablo Rosso (la agencia)
> **Objetivo de la reunión:** Rebeca presentó casos reales de leads donde el agente falla, para iterar el sistema.

---

## Documento de Rebeca — "Buzón de quejas y sugerencias"

Lista de problemas observados por Rebeca operando el agente día a día:

1. Clienta solicita información y el agente cotiza con éxito pero, después le volvió a pedir los datos para cotizar porque la clienta siguió comentando cosas referentes a los diseños para los productos.

2. He notado que, cuando los clientes mencionan los productos dentro de la conversación, el agente vuelve a repetir la info y vuelve a solicitar los datos para cotizar.

3. Cuando los clientes mandan diseños o imágenes que no son del catálogo, el agente no detecta como tal si pertenece a un diseño de nosotros. Sigue con el proceso normal y muchas veces son diseños que no es posible realizar.

4. He notado que hay leads que no responde cuando los pasa a los reactivadores de "R1 con información" o "R1 sin información", no importa realmente el reactivador que sea, 1, 2 o 3.

5. En ocasiones los clientes quieren cotización de pantuflas de moño y mandan la imagen pero, al momento de cotizar, la cotización la realiza con las de satín clásicas.

6. A una clienta que solicitó una cotización formal, el agente le pidió su correo electrónico para mandarle la cotización en PDF. Y tal cual, le dijo que se la iba a mandar y que quedaba atento a la respuesta para seguir con el depósito. En lugar de pasarlo a atención personalizada.

7. Los vasos con popote no siempre los identifica en imágenes y a veces no los cotiza, solo escala la conversación.

8. Cuando los clientes solicitan el catálogo de algún producto, no manda la info y escala el chat. Esto pasa con clientes nuevos y con clientes que ya tienen información en el chat. Entonces si algún cliente que ya había atendido anteriormente, quiere que se le reenvíe el catálogo de los productos, no realiza la acción y pasa el lead a atención personalizada.

9. A veces los clientes solicitan "fotos" cuando el agente pregunta en el caso de las pantuflas, si las requiere de moño o la normal. En esas situaciones también escala la conversación y podría reenviar la infografía de cada producto, tal vez ya no con la info completa pero, que se vea la imagen de cada producto.

---

## Puntos clave del transcript (más allá del documento)

### Sobre el loop de repetición de información (problema #1 y #2)
- Rebeca estima que **~30% de los leads** caen en el loop de repetición.
- Causa raíz discutida: la **rigidez de la estructura por etapas**. Cada etapa tiene un agente con instrucciones propias; cuando el lead "vuelve para atrás" (menciona productos de nuevo), el agente re-dispara el envío de info y re-pide datos (CP, cantidad) que ya tenía.
- El cliente se frustra, a veces llama a Rebeca diciendo "ya les pasé todo y me siguen preguntando lo mismo".

### Sobre los reactivadores que no responden (problema #4)
- Comportamiento esperado: el agente **responde en TODOS los reactivadores EXCEPTO los de atención personalizada** (R1 sin info, R1 con info, R2, R3 → responde; R1AP → humano).
- Síntoma: leads en R1 con/sin info que escriben y el agente NO responde → Rebeca tiene que cotizar manualmente.
- Hipótesis de Juan Pablo: en alguno de los cambios de embudos, una variable/identificador quedó mal y el agente no detecta esos estados. **ACTION ITEM:** probar con leads de prueba en R1 sin/con info y verificar si responde.

### Sobre reconocimiento de imágenes (problema #3, #5, #7)
- Historia: originalmente se implementó reconocimiento de imágenes, pero generaba problemas → se reemplazó por "qué linda imagen" + seguir el proceso.
- **Decisión heredada de la reunión anterior con Oscar:** implementar identificación real de imágenes que contraste con los diseños de la empresa. Cuando esté: si el diseño NO es de HappyFlops → "ese diseño no es nuestro, pero tenemos estos…".
- Oscar sugiere evaluar **Claude (Anthropic)** en lugar de OpenAI solo para la parte de reconocimiento de imágenes.
- Oscar: **"eso háganlo para la nueva implementación del otro"** (= GHL). No implementar en el sistema actual.
- Oscar descartó la opción de "toda imagen → atención personalizada" porque saturaría a Rebeca (de 100 a 200 mensajes/día).

### Sobre solicitud de catálogo (problema #8)
- Cuando piden "el catálogo de sandalias" reenvía TODO (infografía + video + todo), no solo el catálogo.
- **Tensión señalada por Juan Pablo:** resolver esto mal puede costar ventas. Mucha gente pide "el catálogo" al inicio sin saber que hay infografía + video detrás. Si solo mandás el PDF, perdés ese material de venta.
- Caso real frecuente (Oscar): en México la gente borra los WhatsApp (les llega mucha publicidad de bodas, borran chats, vuelven a picar el anuncio meses después). El lead VOLVIÓ a pedir info que el sistema "sabe" que ya mandó, pero el cliente ya no la tiene.
- **Solución discutida:** cuando el cliente pida catálogo/imagen, el agente PREGUNTA "¿tenés la información que te pasé antes o te la mando de nuevo?" y reenvía según la respuesta.

### Sobre cotización formal / PDF / correo (problema #6 del doc)
- **Regla acordada:** si el cliente solicita cotización formal o por PDF/correo → **elevar directamente a atención personalizada** (el agente no manda correos; por seguridad la info se mantiene en WhatsApp).

### Discusión arquitectónica: centralizar vs mantener etapas
- la agencia planteó la posibilidad de **descentralizar los 4 agentes en 1 solo prompt** con herramientas (tools) para casos específicos → más flexible, menos rígido.
- Juan Pablo defendió **mantener la estructura por etapas**: ventaja de métricas (ver dónde se quedan los leads), facilidad de mejorar puntos específicos, proceso de HPF naturalmente estructurado (evento → productos → cotización → venta).
- **Síntesis acordada:** mantener la estructura/guía por etapas PERO darle flexibilidad al agente para manejar casos borde (volver a pedir info, retroceder) sin re-disparar etapa 1 ni re-cotizar todo.
- **Probar en sandbox** antes de tocar producción ("lo mejor es enemigo de lo bueno"; "no demos 10 pasos para atrás por querer dar 1 para adelante").

### Sobre ventas perdidas / memoria
- Hoy los leads se mandan a "ventas perdidas" **para liberar memoria**; ahí el agente no responde → Rebeca contesta los que vuelven.
- Oscar recuerda que en GHL **esto ya no pasaría** (memoria persistente). Confirmado por la agencia: se reestructura.

### Modelo / inversión
- Oscar abierto a **invertir más** (Claude, Gemini, modelo más capaz) si se refleja en ventas. "No estoy peleado con invertir más si se refleja en las ventas."

### Decisión de timing (lo central)
- la agencia pregunta a Oscar: ¿implementar esto antes de migrar o después en GHL?
- Oscar devuelve la pregunta: ¿implementarlo en el actual sirve como prueba-error para mejorar en GHL, o no vale la pena tocar el actual? Su miedo: **echar a perder el de GHL** por meter mejoras. Su contexto: el actual tiene volumen real (100-150 msgs/día, "200"), GHL no tendrá volumen hasta migrar.
- **la agencia pensó en voz alta:** "me doy cuenta que lo mejor es capaz que es mejor terminar la migración y después implementar estas cosas ahí en Go High Level."
- Timeline GHL: mapeo ya hecho, implementación rápida, **1-2 semanas** para tener todo funcionando + testing.
- **ACTION ITEM (la agencia):** analizar sandbox vs GoHighLevel y confirmar enfoque a Oscar. Rebeca enviará el documento con capturas + notas.

### Meta-objetivo de Oscar
- Que Rebeca pase de contestar 100-150 mensajes/día a **20-30**, para liberarla a otras tareas del negocio.
- Cerrar **más ventas** (objetivo primario).
