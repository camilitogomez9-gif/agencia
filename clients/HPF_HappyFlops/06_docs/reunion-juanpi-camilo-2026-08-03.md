# Reunión Juanpi + la agencia + Camilo — 2026-08-03

**Duración:** 43 min · [Grabación](https://fathom.video/share/mEeEi92TsZb8qozn4Vvff22vgi9AAaUs)
**Motivo:** Oscar viene reclamando que el agente migrado no funciona como el anterior. Juanpi lo frenó y armó esta llamada para cerrar el tema.

---

## 1. La decisión operativa (esto es lo que ordena todo lo demás)

Juanpi habló con Oscar por teléfono y le dijo, textual, que **no le vamos a mandar más feedback hasta que la solución pase por su aprobación**. Oscar quedó conforme.

Qué significa en la práctica:

- **El canal con Oscar lo maneja Juanpi**, por privado. Nadie más le escribe.
- Antes de mandarle nada a Oscar, **va a Juanpi por Telegram** y él lo prueba.
- **Compromiso de fecha: martes 4/8** le llega una versión que funciona bien.

> Contexto de por qué esto importa: Oscar es dramático y exagera, pero el volumen es real — el bot le vende USD 1.000–2.000 por día en automático. Ya le mandamos algo roto más de una vez. La regla que bajó la agencia: **cada cosa que sale al cliente se testea antes, aunque lleve dos horas**.

---

## 2. ⚠️ Lo primero que hay que saber: buena parte del plan ya está hecho

En la reunión la agencia dictó un plan de 3 fases (mapear el original → adaptar el nuevo → testear). **Ese trabajo se hizo el 31/7 y está en el repo.** Camilo no arranca de cero.

| Fase que se dictó | Estado real |
|---|---|
| **1.** Definir cómo se comporta el agente original en cada rama | ✅ **Hecho.** `06_docs/paridad-voz-rebeca-2026-07-31.md` — se rastrearon los 236 nodos de `happyflops-main-v3.json` y se documentaron los dos caminos de salida del original (texto libre filtrado vs. bloques pre-horneados), las 15 fichas de producto verbatim, el saludo en 3 partes, los 7 pasos, la cotización atómica |
| **2.** Cambios en el agente nuevo para igualar ese flujo | ✅ **Hecho.** `03_workflows/hpf-inbound-handler-v18-paridad-rebeca.json` + prompt `agente-hpf-inbound-rebeca-system-prompt-v3.md` |
| **3.** Testear al 100% | 🟡 **Parcial.** 35/35 unitarios sobre el código real + 13 conversaciones end-to-end con gpt-4.1. **Falta la validación en el bot vivo.** |

**Lo que falta de verdad, entonces, es:**

1. **Deployar el v18** (hoy no está en producción — el live es el v17).
2. **Probarlo en Telegram** y cerrar lo que aparezca.
3. **Resolver el bug de "todos"** (§4) — es genuinamente nuevo, no lo cubre el v18.

Antes de tocar nada: leer `paridad-voz-rebeca-2026-07-31.md`, sobre todo §6 (deploy) y §7 (lo que falta y los riesgos).

### Deploy del v18 — nota importante

El doc recomienda **pegar los 4 nodos modificados uno por uno** desde `06_docs/snippets/clipboard-v18-nodos-tocados-2026-07-31.json`, en vez de re-importar el JSON entero. Razón: en este cliente un re-import ya rompió configs de tools antes.

Y después del deploy, verificar que **Return Intermediate Steps siga en ON** en el nodo `Vendedor (LLM Agent)` → Options. Sin eso el envío de fotos pierde la capa determinística y vuelve a depender de que el modelo escriba el marcador.

---

## 3. ❌ La idea de "duplicar el flujo y dejarlo corriendo toda la noche" quedó descartada

Esto es importante porque **los action items automáticos de Fathom la listan como vigente** — quedaron congelados en el minuto 25 y no registraron que se dio marcha atrás en el 39.

La propuesta era: duplicar el flujo original, meterle `Respond to Webhook`, conectar Supabase por MCP y dejar a Claude iterando toda la noche comparando el bot viejo contra el nuevo.

Se descartó en la misma llamada, por tres razones:

- El flujo original tiene **~118 nodos**, no 50.
- Hay que meter `Respond to Webhook` **en cada rama**, y son muchas.
- Arrastra tools, seguimientos y creación de leads: duplicarlo dispara efectos reales y **rompe un montón de cosas** (no crea el lead, etc.).

Cierre de Juanpi, textual: *"olvídense de la idea esa de duplicar las dos cosas y dejarlo a la noche. Hay que ir haciéndolo a huevo."*

---

## 4. 🐛 Lo que se vio roto en vivo durante el demo

### 4.1 "todos" rompe el flujo — CONFIRMADO, y no lo cubre el v18

Camilo probó pedir **"todos"** los productos en vez de nombrarlos uno por uno. la agencia, textual: *"ahí se cagó todo"*.

Verificado contra el repo: **ni el prompt v3 ni el código del v18 manejan el pedido colectivo.** Toda la lógica de fichas asume que el lead nombra productos concretos. Es un gap real y es el único bug del demo que sigue abierto.

Al resolverlo, tener presente que el conjunto **cambia según el evento**: Boda lleva todos los productos (es el único con Mandiles), XV no. Ya está gateado así en el v18 para pedidos individuales — el fix tiene que respetar la misma regla.

### 4.2 Las dos fotos "repetidas" — falsa alarma

Camilo notó que le llegaban dos imágenes parecidas y lo levantó como bug. Se aclaró en la llamada: **una es la de boda y otra la de XV años**, son distintas.

Igual queda el punto de Camilo, que es razonable: si en algún caso llegan dos mensajes idénticos, no tiene sentido. **Anotarlo y consultárselo a Oscar** junto con el resto, en una lista de 3-5 puntos, en vez de ir preguntando de a uno.

### 4.3 Debounce — verificar que haya vuelto a 15s

Camilo lo bajó a **0.3s** para poder probar sin esperar. El valor correcto en el repo es **15s** (el live del 31/7 ya lo tiene bien).

**Antes de mandarle nada a Oscar: confirmar que quedó en 15.** Con 0.3 el agente contesta globito por globito en vez de agrupar la ráfaga, que es exactamente una de las cosas que Oscar reclamó.

---

## 5. 🚨 El riesgo que planteó la agencia y que nadie resolvió en la llamada

El flujo nuevo tiene **dos partes que no son simétricas**: la de Telegram y la de Go High Level. En los testeos de hoy **solo corre la de Telegram** — las herramientas del lado GHL no se están ejecutando.

Consecuencia directa: **que quede impecable en Telegram no garantiza nada en GHL.** Se puede dar vuelta la llave y encontrar todo roto de nuevo.

Se suma que la migración del número **demora entre 20 minutos y 3 horas** en establecerse, y esa ventana es lo único que hay para probar antes de que entren leads reales.

**Lo que hay que hacer antes de migrar el número: emparejar las dos ramas.** No dejarlo para el día del cutover.

---

## 6. Otros temas de la llamada

| Tema | Estado / acción |
|---|---|
| **TOFO — Camilo sin acceso a n8n** | No le llega el código de verificación al mail. Hipótesis de la agencia: **algo del servidor**, y el dueño del servidor es Mauricio (a él tampoco lo deja entrar). Camilo averigua; ante la mínima señal de que es eso, le pregunta directo a Mauricio |
| **TOFO — debe 2 meses** | Camilo quiere destrabar el acceso también para hacer los pendientes y meter presión de cobro |
| **SyS — debe 2 meses y no contesta** | Hace ~2 semanas sin respuesta. **Mandarles mensaje para agendar una reunión** |
| **API key de OpenAI** | Verificar que esté bien cargada en el flujo principal. La de Oscar tiene auto-charge configurado, no preocupa; la nuestra la manejamos nosotros |
| **Repartija de la migración** | Reunión interna la agencia + Camilo (quedó para el día siguiente). la agencia ya adelantó que **le va a tocar una parte grande a Camilo** |

---

## 7. Orden sugerido para arrancar

1. Leer `paridad-voz-rebeca-2026-07-31.md` — §6 deploy, §7 riesgos.
2. Deployar el v18 pegando los 4 nodos del snippet. Confirmar Return Intermediate Steps en ON.
3. Correr el smoke del §6: `hola` → `boda` → `quiero ver sandalias y cilindros` → `50 delgadas CP 44100`.
4. Resolver el bug de **"todos"** (§4.1), respetando el gate por evento.
5. Confirmar **debounce en 15s**.
6. Mandarle la versión **a Juanpi por Telegram**, no a Oscar.
7. Armar la lista de 3-5 puntos a consultarle a Oscar (arranca con el de las fotos repetidas, §4.2).

Pendiente aparte, sin fecha: **emparejar la rama GHL con la de Telegram** antes de migrar el número (§5).

---

## 8. Lo que sigue sin estar y hay que pedirle a Oscar

De `paridad-voz-rebeca-2026-07-31.md` §7 — nada de esto se recupera del repo, vive dentro de Kommo:

- **Datos bancarios.** El original nunca los tuvo en texto: emitía un centinela y n8n lo cambiaba por el PDF `NUMEROS DE CUENTA.pdf`. Es **lo único que impide cerrar el Paso 5 solo**.
- **Videos de producto** y **catálogos PDF** de mandiles, pantuflas y sandalias. El original mandaba ficha + catálogo + video; el v18 manda solo la ficha.

Con la cuenta de Kommo por darse de baja, esto tiene fecha de vencimiento real.
