# Propuesta — Paquete agente de fallas técnicas, modelo reventa

**Fecha:** 14 de junio de 2026
**Para:** Mauricio García de la Vega — TOFO Pizza / Robotic Vending de México
**De:** la agencia — la agencia

---

## Introducción

Mauricio, esto es lo que charlamos el jueves. Vos venís dando soporte remoto a varios clientes que compraron máquinas TOFO. Uno de ellos te pidió literalmente *"préstame tu sistema de resolución de fallas"*. La pregunta concreta es cómo paquetizamos el agente que ya está en producción en tu operación de TOFO para que vos lo puedas revender a esos clientes sin tener que armar uno nuevo desde cero cada vez.

Te resumo el contexto, porque importa para entender cómo está armada la propuesta:

- El agente que hoy tenés respondiendo en TOFO tiene cinco cabezas: derivación, RRSS, B2B, servicio al cliente y reposición. Las dos últimas son las que sirven para fallas — el resto es para venta de máquinas y comunidad. Lo que vamos a vender es solo esa parte, sacada limpia del andamiaje TOFO y lista para enchufar contra la infraestructura de cualquier otra pizzería.
- El agente actual ya está depurado. Las reglas anti-alucinación, prohibición de prometer códigos sin evidencia, descripción autorizada del funcionamiento de la máquina, prioridad de pedido sobre cualificación — todo eso ya lo escribimos y probamos. No arrancamos de cero.
- Tu modelo te conviene económicamente: pagás una vez por el paquete y lo revendés N veces dentro del servicio de mantenimiento que ya cobrás a tus clientes.

Como me dijiste en la llamada: *"el costo lo estoy absorbiendo yo porque al cliente le estoy cobrando unas cuotas"*. Lo que cobramos es el trabajo de cirugía + documentación para que vos puedas implementarlo (o tu dev) sin depender de nosotros cada vez que aparezca un cliente nuevo.

## Lo que vamos a construir

El paquete entrega cinco bloques que se complementan entre sí.

**1. El system prompt especializado en fallas**

Incluye:

- Refactorización del prompt actual de Servicio + Reposición, autónomo y sin dependencia del agente de Derivación.
- Eliminación de los catálogos específicos de TOFO (precios, sucursales, sabores), reemplazados por variables que cada cliente final llena con sus propios datos: máquinas, sucursales, sabores, política de reposición.
- Bloque "lo que NO hago" explícito (no vende, no agenda, no responde por inversión, no da reembolsos) para cortar conversaciones fuera de scope sin improvisar.
- Plantilla genérica en .md + guía corta de cómo personalizarla cliente por cliente.

**2. El workflow n8n principal, listo para importar**

Incluye:

- Workflow main de TOFO limpiado: sin las branches de RRSS, B2B ni la tool de chequear disponibilidad para reuniones (no aplican a fallas).
- Flujo de Fallas operativo: memoria persistente, transcripción de audios, análisis de imágenes, recolección de evidencia y escalamiento al técnico humano.
- Credenciales generalizadas — todo lo que hoy es "TOFO Airtable Base XXX" queda como placeholder.
- JSON importable directo al n8n del cliente final. El dev solo conecta credenciales propias: ManyChat, OpenAI, base de datos.

**3. El sub-workflow de escalamiento al técnico humano**

Incluye:

- Versión genérica del flujo actual de TOFO (el que avisa a Miguel por Telegram), simplificado a una sola rama.
- Placeholders documentados para chat_id de Telegram y WhatsApp del técnico del cliente final.
- Cada cliente final pone a su técnico: Miguel sigue siendo Miguel para tu operación, "José" entra para el cliente que lo necesita.
- Importar + reemplazar placeholders + queda operativo.

**4. Las guías de implementación**

Incluye dos documentos distintos:

- **Guía A — Preparación de infraestructura del cliente final.** Para el dueño de la pizzería (no developer). Detalla qué cuentas crear: WhatsApp Business dedicado, Meta Business Manager verificada, ManyChat Pro, n8n, OpenAI con saldo, base de datos. Costos mensuales aproximados + cronograma esperado. Co-branded con tu marca arriba + "Powered by la agencia" en el footer.
- **Guía B — Implementación técnica.** Para vos o tu dev. Paso a paso: import del JSON a n8n, configuración de credenciales, conexión ManyChat ↔ n8n vía webhook, setup de base de datos, personalización del prompt con el catálogo de cada cliente, smoke test antes de pasar a producción. Troubleshooting de errores típicos. Con screenshots.

**5. La testing guide específica de fallas**

Incluye:

- 15-20 casos de prueba reales: "cliente reporta no salió pizza sin foto", "cliente está enojado", "cliente pide reembolso", "cliente quiere hablar con humano", "cliente pregunta precios" (fuera de scope, el agente debe redirigir sin inventar), entre otros.
- Por cada caso: prompt del cliente, respuesta esperada, criterio binario de pase/falla.
- Para correr en cada cliente final antes de pasar a producción — asegura que la implementación quedó bien antes de mandarla en vivo.

## Qué incluye el paquete

| Entregable | Formato | Notas |
|---|---|---|
| 1. System prompt especializado en fallas (plantilla + guía de personalización) | 2 .md | Reusable cliente a cliente |
| 2. Workflow n8n main (adaptado + generalizado) | 1 .json | Importable directo |
| 3. Sub-workflow escalamiento al técnico humano | 1 .json | Con placeholders documentados |
| 4. Guía A — preparación de infraestructura (para el cliente final) | 1 .md | Co-branded TOFO + la agencia footer |
| 5. Guía B — implementación técnica (para vos o tu dev) | 1 .md con screenshots | ~35 páginas paso a paso |
| 6. Testing guide específica de fallas | 1 .md | 15-20 casos QA con criterio binario |
| 7. Diagrama de arquitectura | 1 .drawio + .png | Editable, para mostrar a tus clientes finales |
| 8. Sesión de handoff técnico 60 min | Zoom + grabación | Walkthrough + dudas + smoke test demo |

## Cómo trabajamos juntos

Dos semanas de trabajo concentrado. La idea es que para fin de junio tengas el paquete completo en la mano y puedas arrancar a venderlo.

| Semana | Trabajo | Hito |
|---|---|---|
| Semana 1 | Depuración del prompt + adaptación del workflow main + sub-workflow escalamiento + generalización de credenciales | Demo interna del agente funcionando en sandbox con catálogo dummy |
| Semana 2 | Guía A + Guía B + testing guide + diagrama + revisión final + sesión de handoff | Entrega final + arranque ventana de garantía 30 días |

Tu tiempo durante las 2 semanas: unos 30 minutos al arranque (formulario corto con 4 decisiones de base), una hora a mitad para revisar drafts, y la sesión final de 60 minutos para el handoff. Unas 2 a 3 horas totales tuyas.

Si entregás OKs en tiempo, son 2 semanas calendario. Si algún OK se demora más de 3 días, el cronograma se corre.

## Qué no incluye este paquete

Para que no haya zonas grises:

- Implementación end-to-end por cada cliente final tuyo. Vos o tu dev implementan. Si querés que la agencia te haga la primera implementación llave en mano para uno de tus clientes, va como add-on aparte (ver más abajo).
- Soporte 24/7 ni mantenimiento mensual. Te doy 30 días post-entrega para reportar bugs del paquete original — los arreglo gratis. Después, cualquier cambio (mejoras, nuevas features, adaptaciones puntuales a un cliente) se cotiza aparte, o activás el mantenimiento mensual.
- Personalización por cada cliente final. El paquete viene con plantillas; los datos puntuales de cada pizzería (catálogo de máquinas, fallas específicas, precios, contacto del técnico) los carga el cliente final junto con vos. No los cargamos nosotros cliente por cliente.
- Hosting, suscripciones y cuentas de plataformas. ManyChat, n8n, OpenAI, Airtable o Supabase son del cliente final. Ni vos ni el cliente final le pagan a la agencia por esas plataformas.
- Capacitación profunda en plataformas (ManyChat, n8n). La Guía B cubre lo necesario para el setup técnico; no es un curso de ManyChat.
- Multi-idioma. El paquete viene en español (mexicano).
- Soporte por WhatsApp informal post-paquete.

## Inversión

| Concepto | Monto |
|---|---|
| Paquete completo — agente de fallas paquetizado para reventa | **USD 1.798** |

Pago en dos cuotas iguales:

- USD 899 al iniciar (firma)
- USD 899 al entregar (handoff técnico completado)

Sobre el precio, dos cosas que vale aclarar:

**Por qué USD 1.798 y no más.** El agente base ya existe y está en producción en TOFO — esto es trabajo de cirugía, no de construcción desde cero. El 60% de las horas se va en limpiar, generalizar y documentar para reventa. Si fuera un agente nuevo desde cero, esto saldría entre USD 4.000 y USD 6.000.

**Por qué USD 1.798 y no menos.** El valor del paquete no está solo en el código — está en que después de esta inversión vos podés implementar tu segundo, tercer, cuarto cliente final sin volver a contratarme. La documentación es lo que te permite escalar el modelo.

## Add-ons opcionales

Estos no entran en el paquete; los listo por si en algún momento los necesitás.

- **Implementación llave en mano para un cliente final tuyo** (la agencia hace el setup completo en la infraestructura del cliente, vos miras y replicás después).
- **Mantenimiento mensual del paquete** (updates de prompt, fixes generales, mejoras transversales que aprovechan todos tus clientes finales a la vez): Vos decidís cuándo activarlo — probablemente cuando tengas 3 o más clientes en producción y quieras tener una sola línea de soporte transversal.
- **Adaptación multi-idioma** (inglés o portugués): Incluye prompt + testing guide + diagrama traducido.
- **Nuevas tools sobre el paquete** (por ejemplo, registro de cada caso de falla en Airtable + reporte semanal automático).

## Próximos pasos

1. Confirmás que querés avanzar.
2. Te paso link de pago de la primera cuota (USD 899).
3. Te mando un formulario corto con 4 decisiones de arranque: stack default para los clientes finales (Cloud o self-hosted), base de datos default (Airtable o Supabase), tono del prompt (español MX o LatAm neutro), y si hay clientes finales con urgencia que afecten prioridad o disparen el add-on de implementación.
4. Kickoff técnico de 30 minutos por Zoom para alinear decisiones, y arrancamos la semana siguiente.

Cualquier duda antes de decidir, me decís.

Un abrazo,

**la agencia**
la agencia
