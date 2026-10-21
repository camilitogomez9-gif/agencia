# Paquete — Agente de fallas técnicas, modelo reventa (TFO)

**Fecha:** 2026-06-14 (post-llamada Mauricio 2026-06-12, [grabación Fathom 8 min](https://fathom.video/share/dApEwspSmtq_tXUXGLjyCfEyNByQzLHR))
**Cliente:** TFO — TOFO Pizza · **Decisor:** Mauricio García de la Vega
**Servicio:** Paquetización del agente de fallas técnicas para reventa por Mauricio a sus propios clientes (dueños de pizzerías con máquinas TOFO).
**Inversión:** USD 1.800 (50/50) · **Plazo:** 3 semanas calendario.
**Audiencia de este doc:** la agencia (interno). La versión externa para Mauricio vive en [`propuesta-paquete-agente-fallas-mauricio-2026-06-14.md`](propuesta-paquete-agente-fallas-mauricio-2026-06-14.md).

---

## 1. Resumen ejecutivo

Mauricio da soporte remoto a varios clientes que compraron máquinas TOFO pero no saben hacerles mantenimiento. Uno de esos clientes le pidió explícitamente *"préstame tu sistema de resolución de fallas"*. La pregunta de Mauricio es cómo paquetizar el agente que hoy corre en producción para TOFO de modo tal que él pueda revenderlo a sus clientes sin tener que armar uno nuevo cada vez.

El paquete entrega un **producto reusable cliente-a-cliente**: prompt depurado fallas-only + 2 JSONs n8n generalizados + 3 guías + testing guide + diagrama + sesión de handoff. Mauricio (o su dev) implementa por cada cliente final usando las guías; cada cliente final aloja el agente en SU propia infraestructura (su WhatsApp Business, su ManyChat, su n8n, su DB, su OpenAI). la agencia no implementa por cliente final — eso es add-on opcional cotizado aparte (USD 500/cliente, primer cliente USD 400 con descuento "vení mirá cómo se hace").

**Posicionamiento de venta:** continuación de la llamada del 12 de junio donde Mauricio pidió *"hacerle un módulo para él, igual que está el mío, le pedimos credenciales y todo, vamos a hacerle un agente solo para fallas de las máquinas, lo mismo que ya tenemos pero pasárselo a otro cliente"*. No es venta fría — es respuesta directa a su pedido.

## 2. Objetivo

Darle a Mauricio una **palanca económica clara**: invierte una vez (USD 1.800) y revende N veces (cobra cuotas a sus clientes finales dentro del paquete de servicios que ya les vende). El break-even de Mauricio está en 2 ventas (si cobra USD 800-1.200 a cada cliente final). De ahí en adelante, todo lo que cobre es ganancia neta.

El norte concreto:
1. **Independizar el agente** del andamiaje TOFO (precios, sucursales, sabores, branding, Miguel) — que sea instalable contra cualquier pizzería que tenga máquinas similares.
2. **Documentar para que Mauricio o su dev puedan implementar** sin tener que llamarme cada vez. Las guías son la única forma de que el paquete escale; sin ellas, cada implementación me come 5-8 hs y desaparece el modelo de reventa.
3. **Capacitar Mauricio en el handoff** para que pueda diagnosticar y resolver el 80% de los problemas operativos él mismo (las guías cubren los flujos típicos; la sesión cierra los puntos ciegos).

## 3. Restricciones operativas

- **Cap de 3 semanas calendario.** Si Mauricio no entrega decisiones u OKs en tiempo, el cronograma se corre. Después de 5 días de demora se pausa formalmente.
- **Alcance fallas-only.** Cero ventas, cero RRSS, cero agendado, cero reposición monetaria con códigos especiales de TOFO (los códigos quedan como variable que cada cliente final configura).
- **Sin retainer obligatorio.** Mauricio fue explícito en la llamada: *"el costo lo estoy absorbiendo yo porque al cliente le estoy cobrando unas cuotas"*. Mantenimiento mensual queda como add-on opcional USD 120/mes que él activa cuando quiera.
- **Sin multi-idioma.** Paquete viene en español MX (heredado de TOFO). Inglés/portugués cotizado aparte USD 400/idioma.
- **No implemento por cliente final.** El paquete entrega herramientas; la instalación la hace Mauricio o su dev. Si quiere que yo implemente directamente para un cliente final puntual, es add-on USD 500 (primer cliente USD 400).
- **Garantía 30 días sobre bugs del paquete original.** Después: cotizo aparte a USD 65/h o Mauricio activa el mantenimiento mensual.

## 4. Hipótesis del paquete resueltas por el discovery

| Incógnita previa | Resolución |
|---|---|
| ¿Mauricio quiere implementar la agencia o paquetizado? | **Paquetizado.** Verificado con la agencia. Modelo de reventa puro. |
| ¿Cuál es el alcance del agente especializado? | **Solo fallas técnicas.** Mauricio fue claro en la llamada: *"un agente solo para fallas de las máquinas"*. NO incluye Reposición con códigos de TOFO ni Servicio al Cliente genérico. |
| ¿Branding del Doc A (guía cliente final)? | **Co-branded:** TOFO arriba, "Powered by la agencia" en footer. Verificado con la agencia. Modelo de reventa con respaldo técnico visible. |
| ¿Cómo se maneja Telegram para escalamiento del técnico humano de cada cliente final? | **Descentralizado:** cada cliente final tiene su propio bot y su técnico. Modelo verificado con la agencia. Privacidad del cliente final + Mauricio no se satura con escalamientos cross-cliente. |
| ¿Mauricio implementa el primer cliente solo o lo acompañamos? | **Add-on con descuento (USD 400 primer cliente vs USD 500 siguientes).** Idea: si quiere, la agencia hace el primer setup llave en mano para que él mire cómo se hace y replique solo después. |
| ¿Quién es el cliente final que disparó la llamada? | **No declarado.** Mauricio mencionó "uno de mis clientes me lo pidió" sin nombrarlo. Si hay urgencia o pipeline concreto, sale en el kickoff. |

## 5. Entregables concretos

Cada entregable con definición de "hecho" (criterio binario: está o no está).

### 5.1 System prompt especializado en fallas

- **Qué entrego:** dos archivos:
  - `agente-fallas-system-prompt-vendor-v1.md` — la plantilla genérica. Heredada del prompt actual de **Servicio + Reposición** de TOFO (v1.5/v1.4), pero recortando todo lo no-fallas: B2B (venta de máquinas), RRSS (consumidor final + pricing), agendado de citas con director, identidad EMMA Vivanti específica de TOFO. Quedan: empatía + recolección de evidencia (foto + ticket) + validación contra fraude + escalamiento a técnico humano + anti-alucinación reforzado + bloque "qué NO hago".
  - `agente-fallas-guia-personalizacion.md` — guía corta (3-5 páginas) para que Mauricio o el dev del cliente final llene las variables: nombre del negocio, catálogo de máquinas/sucursales, catálogo de fallas conocidas, contacto del técnico humano, política de reposición del cliente final.
- **Variables exteriorizadas como placeholders** (ej. `{{NOMBRE_NEGOCIO}}`, `{{CATALOGO_MAQUINAS}}`, `{{TECNICO_NOMBRE}}`, `{{TECNICO_TELEGRAM_CHAT_ID}}`, `{{POLITICA_REPOSICION}}`).
- **Hecho cuando:** los dos .md están escritos, la plantilla pasa el smoke test interno con catálogo dummy, y la guía de personalización tiene un ejemplo trabajado de punta a punta.

### 5.2 Workflow n8n principal (`agente-fallas-main-vendor-v1.json`)

- **Qué entrego:** JSON importable directo a un n8n del cliente final. Tomado del [`agente-tofo-web-b2b-rrss-v2.json`](../03_workflows/agente-tofo-web-b2b-rrss-v2.json) (51 nodos), depurado a ~25-30 nodos:
  - **Mantiene:** Webhook ManyChat → Respond rápido → Code JS canal → Existe? Airtable/Supabase → IF crear contacto → Separar partes → Get/Transcribir audio/s → Analizar imagen → Juntar mensajes → **Nodo Fechas** (Patrón Napier, TZ del cliente como variable) → AI Agent gpt-4.1 con Postgres/Airtable Chat Memory → Humanizar → Settear variables → Elegir canal → Enviar [WhatsApp | IG | FB].
  - **Saca:** Tool Agente RRSS, Tool Agente B2B, Tool Agente Servicio (lo fusiono al main), Tool Agente Reposición (idem), Tool `check_disponibilidad` (no aplica a fallas), Tool `audio` (la dejo opcional, comentada), Tool `codigo_reposicion` (queda como tool genérica que retorna lo configurado en variable, no la generación dinámica de TOFO).
- **Credenciales generalizadas:** todo lo que hoy es `Airtable TOFO`, `Postgres TOFO`, `OpenAI la agencia`, `ManyChat TOFO`, etc., queda como credencial referenciada por nombre estándar (`Airtable Cliente`, `Postgres Cliente`, `OpenAI Cliente`, `ManyChat Cliente`) — el dev importa y conecta sus credenciales.
- **Hardcodes removidos:** Base IDs Airtable, IDs de docs Google, IDs de calendario, chat_id Telegram Miguel, ManyChat flow_ns — todos pasan a variables n8n configurables o nodos Set inicial.
- **Patrón Napier preservado:** nodo `Fechas` con TZ como variable (default `America/Mexico_City`, el dev cambia según el cliente final si está en otra zona).
- **Memoria persistente cross-turn** mantenida via Postgres Chat Memory (Supabase) o Airtable según opción de DB elegida por el cliente final.
- **Hecho cuando:** el JSON importa limpio en un n8n vacío, sin nodos rojos. Smoke test E2E pasa contra un setup mínimo (1 máquina, 1 técnico, 1 falla simulada) en sandbox de la agencia.

### 5.3 Sub-workflow escalamiento al técnico humano (`elevar-conversacion-fallas-vendor-v1.json`)

- **Qué entrego:** versión simplificada del [`elevar-conversacion-tofo-v2.json`](../03_workflows/elevar-conversacion-tofo-v2.json). El actual es Switch 3-way (repo→Miguel / b2b→Mauricio / fallback→Mauricio). El nuevo es **1 sola rama** (sin Switch — todo escalamiento va al técnico del cliente final):
  - Input: `id_manychat`, `resumen`, `nombre_cliente`, `telefono_cliente`.
  - Acción A: HTTP a Telegram bot (token + chat_id como variables) con el resumen estructurado.
  - Acción B: HTTP a ManyChat `sendFlow` con `flow_ns` configurable (el flow del cliente final pausa el bot + notifica al técnico que tome la conversación).
  - Acción C (opcional, comentada): HTTP a Gmail si el cliente final quiere también un mail copia.
- **Placeholders documentados en sticky notes** dentro del JSON para que el dev sepa exactamente qué reemplazar al importar.
- **Hecho cuando:** el JSON importa, pasa smoke test (escalamiento dispara mensaje Telegram + ejecuta sendFlow en sandbox ManyChat).

### 5.4 Guía A — Preparación de infraestructura (para el cliente final de Mauricio)

- **Qué entrego:** doc Markdown de ~15-20 páginas, **co-branded** (TOFO arriba, "Powered by la agencia" footer). Audiencia: dueño de pizzería, layperson. Cubre:
  - Qué hace el agente y qué NO hace
  - Checklist resumido de pre-requisitos
  - Detalle por plataforma (8 subsecciones: Meta Business Manager, WhatsApp Business dedicado, ManyChat Pro, n8n Cloud vs VPS, OpenAI con saldo, Airtable vs Supabase, Telegram bot opcional)
  - Datos a entregarle a Mauricio (formulario operativo)
  - Costos mensuales aproximados (Stack Mínimo vs Stack Robusto)
  - Cronograma típico 7-10 días hábiles
  - Soporte post-launch
- **Path:** `clients/TFO_TOFO/06_docs/guia-infra-cliente-final-paquete-fallas-2026-06-14.md`
- **Hecho cuando:** doc completo, escrito en tono layperson, todas las 8 subsecciones de plataforma con links a los wizards oficiales y costos en USD.

### 5.5 Guía B — Implementación técnica (para Mauricio o su dev)

- **Qué entrego:** doc Markdown de ~25-35 páginas con screenshots. Audiencia: Mauricio o el dev que implementa. Cubre paso a paso:
  - Pre-requisitos del entorno (cliente final ya tildó la Guía A)
  - Setup de cuentas (cómo crear PAT Airtable, cómo obtener connection string Supabase con Session Pooler, cómo configurar Meta Business + Cloud API + ManyChat connect)
  - Import del workflow main: cómo importar JSON en n8n, cómo reconectar las credenciales, cómo configurar variables n8n (TZ, catálogo de máquinas, etc.)
  - Import del sub-workflow escalamiento: placeholders a reemplazar
  - Personalización del system prompt: cómo llenar las variables, cómo cargarlo al nodo AI Agent (inline o Google Docs)
  - Conexión ManyChat ↔ n8n: configuración del webhook External Trigger en el flow Default Reply, configuración del sendFlow del escalamiento
  - Smoke test: cómo correr los 15-20 casos de la testing guide (entregable 5.6) contra el setup nuevo
  - Switch a producción + monitoreo primeras 48h
  - Troubleshooting: tabla de errores típicos + diagnóstico
- **Hecho cuando:** doc completo, todos los flujos paso a paso con screenshots, el smoke test al final reproduce el de la agencia.

### 5.6 Testing guide específica de fallas (`testing-guide-fallas-vendor-v1.md`)

- **Qué entrego:** doc con 15-20 casos de prueba específicos del agente especializado. Categorías:
  - **Casos felices** (4-5): "cliente reporta no salió pizza con foto + ticket" / "cliente describe doble cobro con captura" / "cliente reporta pantalla congelada con foto" / "cliente reporta pizza fría con foto + comprobante".
  - **Casos sin evidencia válida** (3-4): "cliente reporta falla sin foto" / "cliente reclama sin comprobante de pago" / "cliente manda foto borrosa" / "cliente reporta fuera de horario de la máquina".
  - **Casos de escalamiento** (3-4): "cliente exige hablar con humano" / "cliente está enojado y agresivo" / "cliente reporta falla técnica fuera del catálogo conocido" / "cliente pide reembolso" (escala porque NO está autorizado a procesar reembolsos).
  - **Casos out-of-scope** (3-4): "cliente pregunta precios de pizza" / "cliente pregunta horario de la sucursal" / "cliente pregunta inversión / franquicia" / "cliente quiere reservar evento" → el agente debe redirigir cortésmente sin inventar.
  - **Casos de memoria** (2): "cliente vuelve 1 día después y retoma" / "cliente cambia de canal en mitad de conversación".
- Cada caso con: prompt del cliente, respuesta esperada, criterio binario de pase/falla, query SQL/Airtable para auditar el log.
- **Hecho cuando:** los 15-20 casos están escritos con criterio binario, y el dev puede correrlos en una sesión de 60-90 min con un script o manualmente.

### 5.7 Diagrama de arquitectura

- **Qué entrego:** un draw.io + export PNG de la arquitectura del paquete. Componentes: Cliente final (WhatsApp) → ManyChat → Webhook n8n → AI Agent gpt-4.1 + Memory + Tools → Respuesta → ManyChat → Cliente final. Rama de escalamiento: AI Agent → Tool `elevar_conversacion` → Telegram técnico + ManyChat sendFlow. Etiquetas claras de qué componente corre dónde.
- **Hecho cuando:** .drawio + .png en el repo, ambos exportables/editables para que Mauricio lo use con sus clientes finales.

### 5.8 Sesión de handoff técnico (60 min Zoom + grabación)

- **Qué entrego:** una sesión Zoom 60 min con Mauricio (+ su dev si quiere) para:
  - Walkthrough del workflow main importado (15 min)
  - Walkthrough del sub-workflow escalamiento (10 min)
  - Walkthrough de las dos guías (10 min)
  - Demo de smoke test contra sandbox (10 min)
  - Q&A libre (15 min)
- Grabación queda disponible para que Mauricio la consulte después.
- **Hecho cuando:** sesión realizada, grabación entregada, dudas en vivo resueltas. Quedan 30 días de garantía para que Mauricio reporte bugs del paquete original por email o Loom (no WhatsApp informal).

## 6. Cronograma 3 semanas

| Semana | Trabajo | Hito |
|---|---|---|
| **S1** | Depuración prompt 5.1 + adaptación workflow main 5.2 + sub-workflow escalamiento 5.3 | Demo interna del agente funcionando en sandbox de la agencia con catálogo dummy |
| **S2** | Generalización credenciales/hardcodes (cierre 5.2) + Guía A 5.4 + Guía B 5.5 (primer draft) | Entrega draft de las 2 guías para review de Mauricio |
| **S3** | Testing guide 5.6 + diagrama 5.7 + revisión final de guías + sesión handoff 5.8 | Entrega final + handoff técnico realizado + arranca ventana de 30 días de garantía |

**Dependencias en el cronograma:**
- S1 puede arrancar sin OK de Mauricio sobre nada más allá del formulario inicial (ver §11 Apéndice B).
- S2 entrega DRAFT de guías; review de Mauricio no bloquea S3 si vuelve en ≤5 días.
- S3 sesión de handoff agendada al final de S3 (jueves o viernes idealmente).

## 7. Lo que NO entrega este paquete

Espejo de §5 del Doc B externo, con más detalle interno:

- **Implementación end-to-end por cada cliente final de Mauricio.** la agencia no instala el paquete contra la infra de cada pizzería. Si Mauricio quiere que lo haga para un cliente puntual, va como add-on USD 500/cliente (primer cliente USD 400 con descuento).
- **Soporte 24/7 ni mantenimiento mensual post-paquete.** 30 días de garantía sobre el paquete original (bugs reproducibles en sandbox). Después: USD 65/h con mínimo 2h, o Mauricio activa mantenimiento USD 120/mes.
- **Personalización por cada cliente final.** Las variables se llenan en la implementación de cada uno; la agencia entrega plantillas, no las llena cliente por cliente.
- **Hosting, suscripciones y cuentas de plataformas.** ManyChat, n8n, OpenAI, Airtable/Supabase son del cliente final. Si Mauricio paga la de algún cliente desde su cuenta, es decisión comercial de él — no afecta a la agencia.
- **Capacitación profunda de plataformas.** Las guías cubren lo necesario para el setup; no son curso ManyChat ni curso n8n.
- **Multi-idioma.** Paquete en español MX. Otros idiomas: USD 400/idioma (incluye prompt + testing guide + diagrama adaptado).
- **Soporte WhatsApp informal post-paquete a Mauricio.** Durante los 30 días de garantía, dudas vía email o Loom (para que quede registrado). Esto evita que se diluya el límite y previene "consulta de 5 min" que se vuelve hora gratis.
- **Trabajo sobre el agente actual de TOFO.** El paquete es derivado pero independiente. Si TOFO necesita cambios, va por la línea de trabajo TOFO existente.
- **Onboarding/training de los clientes finales de Mauricio.** Mauricio les enseña a usar el agente; la agencia solo enseña a Mauricio.

## 8. Dependencias del cliente

**Decisiones de arranque (formulario S0):**
1. Stack default para clientes finales: ¿Cloud (más simple, recomendado) o self-hosted (más barato a largo plazo)? Afecta el énfasis de la Guía A y Guía B.
2. Base de datos default: ¿Airtable (UI tipo planilla, visible para el dueño) o Supabase (gratis, más técnico)? Afecta el JSON del workflow main (Postgres Chat Memory vs Airtable como log).
3. Tono del prompt: ¿mantener español MX heredado de TOFO o neutralizar a español LatAm? (default: español MX).
4. ¿Hay clientes finales con urgencia en pipeline? Afecta prioridad y eventual add-on de implementación llave en mano.

**Tiempo de Mauricio durante las 3 semanas:**
- ~30 min S0 (formulario + kickoff Zoom)
- ~60 min S2 (review de los drafts de guías + decisiones de ajuste)
- ~90 min S3 (revisión final + sesión de handoff)
- **Total:** ~3 hs de Mauricio en 3 semanas.

**Buena fe de feedback:** si Mauricio no valida drafts/decisiones en 5 días, cronograma se corre. Después de 5 días extra de demora se pausa formalmente.

## 9. Criterios de cierre

El paquete se considera entregado cuando:

1. Los 8 entregables (5.1–5.8) están al 100% según definición de "hecho".
2. El smoke test E2E del paquete (15-20 casos de la testing guide 5.6) pasa en sandbox de la agencia con todos los placeholders llenos de datos dummy.
3. Sesión de handoff realizada, grabación entregada, dudas en vivo resueltas.
4. Mauricio confirma por email o Loom que recibió todos los entregables y entiende cómo replicar el setup.
5. Segundo pago (USD 900) acreditado.

Después del punto 5, arranca la ventana de 30 días de garantía sobre bugs del paquete original.

## 10. Riesgos y mitigaciones

| # | Riesgo | Mitigación / cláusula contractual |
|---|---|---|
| 1 | Mauricio implementa mal y echa la culpa al paquete | **Cláusula:** "El paquete se entrega tal como se prueba en sandbox de la agencia (testing guide 5.6 al 100%). Bugs reproducibles en sandbox → fix gratis durante 30 días. Problemas que solo aparecen en infraestructura del cliente final son responsabilidad de quien implementa." Si Mauricio reporta un bug y no se puede reproducir en sandbox, le pido logs/video del cliente final y diagnostico, pero arreglarlo en la infra del cliente final es trabajo cotizado aparte. |
| 2 | Cliente final de Mauricio le reclama directo a la agencia | **Cláusula:** "Soporte único al cliente final es responsabilidad de Mauricio. la agencia solo trata con Mauricio." Más email pre-armado que Mauricio puede mandar si el cliente final lo aborda: *"El paquete técnico lo desarrolló la agencia; la implementación y el soporte operativo soy yo. Escribime directo y lo resolvemos."* |
| 3 | Mauricio modifica el prompt o el workflow y lo rompe, después pide arreglo gratis | **Cláusula:** "Modificaciones al prompt o al workflow hechas por Mauricio o terceros invalidan la garantía sobre esa parte específica. Bugs del código original entregado se siguen cubriendo durante los 30 días." |
| 4 | Cliente final cambia plataforma (ej. de ManyChat a Chatwoot, de n8n a Make, de OpenAI a Claude/Gemini) | **Cláusula:** "El paquete está diseñado para WhatsApp Cloud API + ManyChat + n8n + OpenAI + Airtable/Supabase. Migraciones a otras plataformas requieren adaptación cotizada aparte a USD 65/h." |
| 5 | Bug crítico aparece después del día 31 | **Cláusula:** "Bugs reportados post-garantía se cotizan a USD 65/h con mínimo de 2h. Alternativamente, Mauricio puede activar mantenimiento USD 120/mes que cubre fixes ilimitados al paquete original + 2 horas/mes de mejoras menores." |
| 6 | Ambigüedad bug vs feature request | **Cláusula:** "Bug = el agente no hace lo que está documentado que debe hacer (testing guide o guía B). Feature request = querés que haga algo nuevo no documentado. Los primeros son gratis durante 30 días, los segundos se cotizan." |
| 7 | Mauricio sub-licencia el paquete a otros revendedores/desarrolladores/agencias | **Cláusula:** "Licencia de uso para Mauricio + sus clientes finales directos (pizzerías que compran sus servicios). No incluye sub-licenciar a otros revendedores, agencias o developers que quieran venderlo como producto. Si Mauricio quiere revender el paquete como producto a otros, hablamos otra estructura comercial." |
| 8 | Cambios de scope mid-flight ("hagamoslo bilingüe", "agreguemos esta tool nueva") | **Cláusula:** "Cambios de scope durante el desarrollo se cotizan aparte. El alcance final es el de esta propuesta. Si surge la necesidad de algo nuevo, lo cotizamos como agregado y decidimos si entra en este sprint o queda para después." |
| 9 | Mauricio quiere extender el paquete (idiomas, más tools, white-label para más industrias) | **Cláusula:** "Cada extensión va con cotización propia. Mantenimiento mensual USD 120 cubre fixes pero no extensiones." |
| 10 | El cliente final no entrega los datos a tiempo y la implementación se traba | **Esto es problema de Mauricio, no de la agencia.** El paquete está entregado al cumplirse los 9 criterios de cierre (§9). Si Mauricio no puede implementarlo porque su cliente final no entrega datos, eso no extiende la garantía ni la entrega. |

## 11. Próximos pasos internos (post-aprobación)

1. Mandar la propuesta externa ([`propuesta-paquete-agente-fallas-mauricio-2026-06-14.md`](propuesta-paquete-agente-fallas-mauricio-2026-06-14.md)) a Mauricio por WhatsApp con resumen Fathom de la llamada del 12 de junio.
2. Si Mauricio aprueba: emitir link de pago del 50% inicial (USD 900) por PayPal/Payoneer/Binance/transferencia.
3. Mandar formulario corto con las 4 decisiones de arranque (ver §8 dependencias del cliente).
4. Crear branch `feat/paquete-fallas-revendible` en el repo TFO + carpeta `clients/TFO_TOFO/paquete-fallas-vendor/` para alojar los artefactos del paquete (separado de los archivos de TOFO en producción).
5. Agendar kickoff técnico de 30 min Zoom (no es reunión obligatoria, es sync rápido).
6. Actualizar `CLIENT_INFO.md` de TFO + `contexto/datos-actuales.md` con la nueva línea de servicio activa (paquete reventa) — corre `/cliente-sync TFO`.
7. Crear upsell tracker en `ops/04_upsells/TFO-paquete-reventa-agente-fallas-2026-06-14.md` para que entre en el kanban.

---

## Apéndice A — Cálculo de costo interno (no compartir con cliente)

| Bloque | Horas estimadas | Notas |
|---|---|---|
| 5.1 Depuración prompt fallas (recortar B2B/RRSS/Servicio/Reposición → fallas-only + guía personalización) | 4-6 hs | El prompt fuente (`agente-tofo-servicio-system-prompt.md` v1.5 + `agente-tofo-reposicion-system-prompt.md` v1.4) son ~21 KB combinados. Depurar a fallas-only + agregar placeholders + escribir guía de personalización. |
| 5.2 Adaptación workflow n8n main (eliminar tools no relevantes, generalizar credenciales, parametrizar hardcodes) | 4-6 hs | 51 nodos del original → ~25-30 nodos del paquete. Lo más fino es revisar nodo por nodo qué hardcode pasar a variable. |
| 5.3 Sub-workflow escalamiento simplificado (1 rama, placeholders, sticky notes documentadas) | 2-3 hs | El v2 actual tiene 6 nodos; el del paquete queda en 4-5 nodos. Las sticky notes son lo que más toma porque deben ser leíbles por el dev de Mauricio. |
| 5.4 Guía A cliente final (8 secciones, 8 subsecciones de plataforma, costos, cronograma, layperson-friendly) | 4-6 hs | El detalle de plataforma con links a wizards + costos USD + cronograma toma más de lo que parece. Vale el esfuerzo: es el doc que Mauricio reenvía. |
| 5.5 Guía B técnica (screenshots de import n8n + setup ManyChat + setup Airtable/Supabase + smoke test + troubleshooting) | 6-8 hs | Los screenshots son el cuello de botella. Hay que reproducir cada paso en un entorno limpio y capturar pantallas. ~35 páginas final. |
| 5.6 Testing guide específica fallas (15-20 casos con prompt + respuesta esperada + criterio binario + queries de auditoría) | 3-4 hs | Heredo estructura del `testing-guide-v4.md` de TOFO. La curación de casos es lo más intelectual; el resto es plantilla. |
| 5.7 Diagrama arquitectura (draw.io + PNG, exportable y editable) | 1-2 hs | Componente standard. |
| 5.8 Sesión handoff (prep + 60 min Zoom + grabación + Loom complementario si hace falta) | 3 hs | Prep 60 min + sesión 60 min + post-procesado 30-60 min + 30 min de Loom si quedan dudas no resueltas en vivo. |
| Buffer + admin (kickoff sync 30 min + revisión final integral + sincronización CLAUDE.md + commit) | 2-3 hs | |
| **Total estimado** | **29-40 hs** | |

A USD 65/h → USD 1.885 - 2.600. Cobrado **USD 1.800** (cerca del piso, refleja descuento por reutilización del agente existente + relación repeat customer).

**Por qué USD 1.800 y no USD 1.500 (que era mi propuesta inicial):**
- A USD 1.500 → USD 37-52/h efectivo. Bajo para implementación técnica + redacción de documentación operativa (35 pp con screenshots).
- USD 1.800 mantiene margen sano sin asustar a Mauricio (palanca de reventa hace que recupere en 2 ventas).
- Anclaje psicológico: USD 1.800 → "casi USD 2.000, no es chiste". USD 1.500 → "redondo, regalado".

**Por qué USD 1.800 y no USD 2.500-3.000:**
- El argumento de Mauricio es válido en parte: el agente ya existe en producción, lo que cobramos es cirugía + documentación. No es construcción desde cero.
- Mauricio es repeat customer; vale la pena cuidar la relación.
- La línea de upsells (implementación por cliente final USD 500, mantenimiento USD 120/mes, idiomas USD 400, capacitación USD 250/sesión) abre revenue futuro sin presionar precio hoy.

## Apéndice B — Decisiones de arranque para mandar a Mauricio (formulario S0)

Estas 4 preguntas las mando a Mauricio inmediatamente después del primer pago, antes de arrancar S1. Respuestas no bloquean S1 pero sí afectan los outputs de S2-S3.

1. **Stack default para los clientes finales — ¿n8n Cloud o n8n self-hosted?**
   *Mi recomendación: Cloud (más simple, USD 20/mes, cero servidor que mantener; el ahorro de self-host se nota recién a partir de 3+ máquinas por cliente final). Si decís self-hosted, la Guía B suma 5-7 pp de instalación VPS + Docker + Caddy + Let's Encrypt.*

2. **Base de datos default — ¿Airtable o Supabase?**
   *Mi recomendación: Airtable para los primeros 1-2 clientes finales (el dueño de la pizzería puede entrar a ver los datos como planilla, baja la curva de adopción). Supabase a partir del 3° cliente final si querés ahorrar en planes Team.*

3. **Tono del prompt — ¿mantener español MX (heredado de TOFO) o neutralizar a español LatAm?**
   *Mi recomendación: español MX, porque el agente entiende contextos mexicanos (modismos, hora CDMX, monedas MXN/USD). Si el cliente final está fuera de México y querés tono neutro, sumamos ~3h de reescritura — cotizable como add-on si solo es para 1 cliente final, o lo cubrimos en la S1 si va a ser el default para todos los próximos.*

4. **¿Hay clientes finales con urgencia en pipeline ahora mismo?**
   *Afecta prioridad de S2-S3 y abre la conversación sobre el add-on "primer cliente USD 400 llave en mano" si querés que la agencia implemente directo al primero para mostrarte el flujo.*

## Apéndice C — Inventario de assets fuente para reusar

Inventario rápido para no perder tiempo en S1 buscando archivos.

| Asset fuente TOFO | Path | Cómo se usa en el paquete |
|---|---|---|
| Prompt Servicio v1.5 | [`clients/TFO_TOFO/04_agents/agente-tofo-servicio-system-prompt.md`](../04_agents/agente-tofo-servicio-system-prompt.md) | Base del prompt 5.1 (empatía + flujo de fallas). |
| Prompt Reposición v1.4 | [`clients/TFO_TOFO/04_agents/agente-tofo-reposicion-system-prompt.md`](../04_agents/agente-tofo-reposicion-system-prompt.md) | Suma flujo recolección evidencia + validación fraude + escalamiento. |
| Workflow main v2 | [`clients/TFO_TOFO/03_workflows/agente-tofo-web-b2b-rrss-v2.json`](../03_workflows/agente-tofo-web-b2b-rrss-v2.json) | Esqueleto del workflow main 5.2 (depurar tools no-fallas + generalizar credenciales). |
| Sub-workflow Elevar v2 | [`clients/TFO_TOFO/03_workflows/elevar-conversacion-tofo-v2.json`](../03_workflows/elevar-conversacion-tofo-v2.json) | Esqueleto del sub-workflow escalamiento 5.3 (simplificar a 1 rama, parametrizar credenciales). |
| Patrón Napier (nodo Fechas) | Embebido en main v2 | Código JS reusable para 5.2 — cambiar TZ a variable. |
| Bloque anti-alucinación común | Embebido en prompts v1.4+ | Conservar tal cual en el prompt 5.1. |
| Postmortem incidente Mauricio | [`clients/TFO_TOFO/06_docs/incidente-info-inventada-y-cita-2026-06-08.md`](../06_docs/incidente-info-inventada-y-cita-2026-06-08.md) | Insumo para la sección "qué NO hace" de la Guía A (5.4) — el agente no inventa códigos, no promete plata, pide evidencia. |
| Testing guide v4 (estructura) | [`clients/TFO_TOFO/07_testing/testing-guide-v4.md`](../07_testing/testing-guide-v4.md) | Plantilla para la testing guide 5.6 (queries SQL + criterio binario). |
| Guía migración SYS (estructura) | [`clients/SYS_SistemasYSoluciones/06_docs/guia-migracion-infra-cliente-2026-06-05.md`](../../SYS_SistemasYSoluciones/06_docs/guia-migracion-infra-cliente-2026-06-05.md) | Plantilla estructural para la Guía A (5.4) — adaptar de "migrar" a "crear de cero". |
