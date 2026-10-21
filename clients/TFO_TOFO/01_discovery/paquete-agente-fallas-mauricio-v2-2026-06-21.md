# Paquete — Agente de fallas técnicas v2 (TFO)

**Fecha:** 2026-06-21 (post-reunión Mauricio 2026-06-18, scope reducido)
**Cliente:** TFO — TOFO Pizza · **Decisor:** Mauricio García de la Vega
**Servicio:** Kit inicial del agente de fallas para que Mauricio lo reuse cliente a cliente.
**Inversión:** USD 360 · **Plazo:** 2 semanas calendario · **Esfuerzo la agencia:** ~3 horas.
**Audiencia de este doc:** la agencia (interno). Versión externa: [`propuesta-paquete-agente-fallas-mauricio-v2-2026-06-21.md`](propuesta-paquete-agente-fallas-mauricio-v2-2026-06-21.md).
**Reemplaza:** [`paquete-agente-fallas-mauricio-2026-06-14.md`](paquete-agente-fallas-mauricio-2026-06-14.md) (v1, USD 1.798 / 3 sem / 8 entregables — descartado por scope reducido). Add-ons de v1 archivados en [`../../../ops/04_upsells/TFO-addons-paquete-fallas-archivados-2026-06-21.md`](../../../ops/04_upsells/TFO-addons-paquete-fallas-archivados-2026-06-21.md) por si se reactivan.

---

## 1. Qué cambió vs v1

Mauricio (reunión 18/6/26) pidió achicar el stack del paquete para bajar el costo operativo recurrente de cada cliente final:

- **Sin ManyChat.** Cada cliente final usa WhatsApp Cloud API directa (Meta → webhook n8n).
- **Sin memoria persistente.** Simple Memory nativa de n8n (in-memory por sesión, sin DB externa Postgres/Supabase/Airtable).
- **Conversaciones de fallas son one-shot.** No hay valor en histórico cross-turn para este caso de uso.

Esto reduce el stack del cliente final de `ManyChat Pro + Supabase + n8n + OpenAI + Airtable` (~USD 60-100/mes) a `n8n + OpenAI + WhatsApp Cloud API` (~USD 25-40/mes). Menos infra a documentar → paquete más liviano → precio más bajo → recuperable en 1 venta de Mauricio.

## 2. Alcance reducido

Entrega un **kit inicial** (no un producto pulido). 4 piezas mínimas para que Mauricio o su dev importen el agente contra la infra de un cliente final y lo personalicen.

| # | Entregable | Formato | "Hecho cuando" |
|---|---|---|---|
| 1 | System prompt fallas-only con placeholders | 1 .md | Depurado del actual Servicio v1.5 + Reposición v1.4 de TOFO, recortando B2B/RRSS/agenda/branding TOFO. Variables marcadas (`{{NOMBRE_NEGOCIO}}`, `{{CATALOGO_MAQUINAS}}`, `{{POLITICA_REPOSICION}}`, etc.). Sin tool de escalamiento — si el agente detecta caso fuera de scope o el cliente exige humano, instruye al cliente final por texto a contactar al técnico (número/canal queda como variable del prompt). Comentado al inicio explicando cómo llenar cada placeholder. |
| 2 | Workflow n8n único | 1 .json | Importable directo. WhatsApp Cloud API entrada/salida + Simple Memory nativa + AI Agent gpt-4.1 + nodo Fechas Patrón Napier (TZ variable). Sin sub-workflow separado. Sin sendFlow ManyChat. Sin Postgres Chat Memory. Sin Tool de escalamiento Telegram. Smoke test interno OK contra setup dummy. |
| 3 | README único de implementación | 1 .md (3-5 pp) | Cubre: qué hace el agente, pre-requisitos (cuenta Meta + número WA verificado + n8n + OpenAI con saldo), pasos de import + reconectar credenciales + llenar placeholders del prompt + smoke test de 3 casos. Sin screenshots. Lenguaje semi-técnico — el implementador del lado del cliente final lo lee y avanza. |
| 4 | Walkthrough async Loom | 1 link (10-15 min) | Grabación caminando los 3 archivos + demo de 1 caso E2E contra setup dummy. Sin sesión Zoom sync. Mauricio o su cliente lo miran cuando pueden + preguntas async por WhatsApp si trabas. |

## 3. Lo que NO entrega este paquete

- **No hay 2 guías separadas** (cliente final + dev técnica con screenshots). Hay 1 README único corto.
- **No hay testing guide formal** con 15-20 casos QA. El README incluye 3 casos mínimos de smoke. Si Mauricio quiere batería de tests, se cotiza aparte.
- **No hay diagrama draw.io.** Si hace falta, se cotiza aparte.
- **No hay sesión Zoom 60 min sync.** Hay Loom async + dudas por WhatsApp informal durante 14 días post-entrega.
- **No hay garantía formal de 30 días.** Bugs reproducibles que detecte Mauricio en las 2 semanas post-entrega los arreglo sin discusión. Después: cotizable.
- **No hay implementación llave en mano por cliente final.** Mauricio o su dev implementan. Si quiere que la agencia implemente directo a un cliente puntual, cotizamos aparte caso por caso (ver [add-ons archivados](../../../ops/04_upsells/TFO-addons-paquete-fallas-archivados-2026-06-21.md)).
- **No hay mantenimiento mensual incluido.** Si más adelante quiere mantenimiento, lo armamos en el momento.
- **No hay multi-idioma.** Spanish MX heredado de TOFO.
- **No hay trabajo sobre el agente actual de TOFO.** El paquete es derivado pero independiente.

## 4. Cronograma 2 semanas

| Semana | Trabajo | Hito |
|---|---|---|
| **S1** | Depurar prompt (entregable 1) + adaptar workflow n8n con WhatsApp Cloud API + Simple Memory (entregable 2) | Smoke test interno OK contra setup dummy |
| **S2** | Escribir README (entregable 3) + grabar Loom walkthrough (entregable 4) + entrega final por email con los 4 artefactos | Mauricio recibe el kit completo + arranca ventana de 14 días de fix informal |

2 semanas calendario es holgado para 3 horas de trabajo efectivo — da margen para encajarlo entre otros proyectos sin presionar TOFO en producción.

## 5. Dependencias del cliente

**Decisiones de arranque (mando por WhatsApp después del pago, no bloquean S1):**

1. ¿Tono del prompt: mantener español MX o neutralizar a LatAm? Default: español MX.
2. ¿Hay cliente final puntual ya en pipeline para implementación inmediata? Si sí, en el Loom usamos un caso real (sucursales/máquinas del cliente final) en vez de uno dummy.
3. ¿A qué canal/contacto direcciona el prompt cuando el agente detecta caso fuera de scope o el cliente exige humano? (Default: el agente sugiere "contactá al equipo técnico" sin especificar — Mauricio o su cliente final llenan el placeholder con el contacto real.)

**Tiempo de Mauricio durante las 2 semanas:** ~15 min responder formulario S0 + ~20 min mirar Loom + ~15 min dudas async. Total ~50 min en 2 semanas.

## 6. Modelo de pago

Pago único de **USD 360 al contado**, una vez aceptado el presupuesto y previo al arranque de la implementación. No hay segundo pago contra entrega — el cobro adelantado refleja que el alcance es chico, el plazo es corto, y el riesgo de cancelación intermedia se elimina.

## 7. Criterios de cierre

El paquete se considera entregado cuando:

1. Los 4 entregables están al 100% según definición de "hecho".
2. Smoke test de 3 casos pasa en sandbox con datos dummy (no exigible contra infra de Mauricio o de su cliente final porque eso depende de quién implemente).
3. Loom entregado por link compartido (Drive o Loom directo).
4. Mauricio confirma recepción por WhatsApp.

Después: 14 días de fix informal para bugs reproducibles en sandbox.

## 8. Riesgos y mitigaciones

| # | Riesgo | Mitigación |
|---|---|---|
| 1 | Cliente del lado de Mauricio importa el JSON contra un n8n con versión rara y rompe | El README aclara: requiere n8n >= 1.50, nodos LangChain disponibles. Si la infra del cliente final difiere, el fix se cotiza aparte. |
| 2 | Mauricio espera más de lo entregado y reclama | El README más esta propuesta dejan claro qué hay y qué no. Si pide algo no incluido durante las 2 semanas, contesto "no entra en el alcance, lo cotizo aparte si lo querés agregar." |
| 3 | Cliente final no tiene número WhatsApp dedicado verificado en Meta | El README enumera pre-requisitos arriba de todo. Si el cliente final no los cumple, no es problema de la agencia — es Mauricio el que coordina con su cliente. |
| 4 | Mauricio o el implementador del cliente final modifica el prompt y lo rompe, pide arreglo gratis | Mismo principio que TOFO: si modificó algo y dejó de andar, decimos qué cambió. Si lo arreglamos, lo cotizamos aparte (USD 65/h, mínimo 1h). |
| 5 | Un add-on de los archivados (mantenimiento, idiomas, implementación llave en mano) lo termina pidiendo | Está documentado en `ops/04_upsells/TFO-addons-paquete-fallas-archivados-2026-06-21.md`. Si lo pide, cotizamos en el momento sobre la base de ahí. |
| 6 | Cliente final exige escalamiento a humano y el agente no tiene tool de Telegram | El prompt v2 NO incluye tool de escalamiento — el agente instruye al cliente final por texto a contactar al técnico. Si Mauricio o su cliente final piden tool de escalamiento real (Telegram / WhatsApp template al técnico), se cotiza como add-on aparte (~USD 80-120 según destino). |

## 9. Próximos pasos internos (post-aprobación)

1. Mandar propuesta externa ([`propuesta-paquete-agente-fallas-mauricio-v2-2026-06-21.md`](propuesta-paquete-agente-fallas-mauricio-v2-2026-06-21.md)) a Mauricio por WhatsApp.
2. Si aprueba: emitir link de pago único de USD 360.
3. Mandar formulario corto con las 3 decisiones de arranque (§5).
4. Crear carpeta `clients/TFO_TOFO/paquete-fallas-v2/` para alojar los 4 artefactos.
5. Actualizar `CLIENT_INFO.md` de TFO + correr `/cliente-sync TFO`.
6. Bloquear ~1.5h S1 + ~1.5h S2 en calendario.

---

## Apéndice A — Cálculo de costo interno (no compartir con cliente)

| Bloque | Tiempo estimado |
|---|---|
| 1. Depurar prompt fallas-only con placeholders | 45 min |
| 2. Adaptar workflow n8n (WhatsApp Cloud API + Simple Memory, sin escalamiento Telegram, sin sub-workflow separado) | 75 min |
| 3. Escribir README (3-5 pp, sin screenshots) | 30 min |
| 4. Grabar Loom walkthrough 10-15 min | 15 min |
| Buffer + admin (entrega por email + commit + sync) | ~15 min |
| **Total estimado** | **3 horas** |

A USD 360 / 3h → **USD 120/h efectivo**. Refleja:
- Tarifa de experto (no comparar con USD 65/h de implementación standard) por la curaduría del prompt y la decisión técnica del stack reducido.
- Repeat customer Mauricio + relación TOFO en producción.
- El valor del paquete está en lo que NO hay que hacer (decisiones ya tomadas, prompt ya depurado en TOFO, workflow ya validado).

**Por qué USD 360 y no USD 500-800:**
- Mauricio pidió achicar todo. Si subo el precio mucho contradigo la conversación.
- 3 horas reales × USD 120/h = USD 360 es coherente y honesto.
- Margen del modelo de Mauricio: recupera en 1 sola venta a cliente final (típicamente cobra USD 800-1.200 por implementación).

**Por qué USD 360 y no USD 200-250:**
- USD 250 / 3h = USD 83/h. Bajo para curaduría técnica + redacción de README operativo.
- USD 360 mantiene anclaje profesional sin asustar.

## Apéndice B — Stack del cliente final (referencia para Mauricio)

Mauricio puede usar esto cuando le ofrezca el agente a sus clientes finales.

| Componente | Costo aprox mensual | Notas |
|---|---|---|
| WhatsApp Cloud API + número Meta | **Gratis** hasta 1k conv usuario-iniciadas/mes | Requiere número dedicado verificado en Meta Business |
| n8n Cloud Starter | USD 20/mes (USD ~12/mes si instala VPS) | Self-hosted reduce costo si el cliente final ya tiene infra |
| OpenAI (gpt-4.1 inputs/outputs típicos de fallas) | USD <10/mes | Volumen bajo: 1-5 fallas/día |
| **Total mensual cliente final** | **USD ~15-30/mes** | Vs USD 60-100/mes del paquete v1 con ManyChat + Supabase |

Esto es palanca de venta de Mauricio a sus clientes finales: "te dejo el agente operando por USD 30/mes contra el de un humano de soporte que te sale USD 500-1.000/mes".

## Apéndice C — Inventario de assets fuente para reusar

| Asset fuente TOFO | Path | Cómo se usa en el paquete v2 |
|---|---|---|
| Prompt Servicio v1.5 | [`clients/TFO_TOFO/04_agents/agente-tofo-servicio-system-prompt.md`](../04_agents/agente-tofo-servicio-system-prompt.md) | Base del prompt 1 (empatía + flujo de fallas). |
| Prompt Reposición v1.4 | [`clients/TFO_TOFO/04_agents/agente-tofo-reposicion-system-prompt.md`](../04_agents/agente-tofo-reposicion-system-prompt.md) | Suma flujo recolección evidencia + validación fraude. **NO se trae** la lógica de tool de escalamiento (queda fuera del paquete v2; el agente instruye al cliente final por texto). |
| Workflow main v2 TOFO | [`clients/TFO_TOFO/03_workflows/agente-tofo-web-b2b-rrss-v2.json`](../03_workflows/agente-tofo-web-b2b-rrss-v2.json) | Esqueleto del workflow 2 (depurar TODOS los nodos no-fallas + reemplazar ManyChat por WhatsApp Cloud API + reemplazar Postgres Chat Memory por Simple Memory + NO traer el tool de escalamiento). |
| Patrón Napier (nodo Fechas) | Embebido en main v2 TOFO | Reutilizable tal cual en workflow 2 con TZ como variable. |
| Postmortem incidente Mauricio | [`clients/TFO_TOFO/06_docs/incidente-info-inventada-y-cita-2026-06-08.md`](../06_docs/incidente-info-inventada-y-cita-2026-06-08.md) | Insumo para sección "lo que NO hace" del prompt 1 — anti-alucinación reforzada. |
