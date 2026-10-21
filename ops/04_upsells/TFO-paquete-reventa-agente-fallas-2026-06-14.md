# Upsell TFO — Paquete agente de fallas técnicas (modelo reventa)

**Cliente:** TFO — TOFO Pizza (Mauricio García de la Vega)
**Fecha registrada:** 2026-06-14
**Status:** Propuesta enviada (pendiente respuesta de Mauricio)
**Fecha estimada de cierre:** 2026-07-15 (1 semana revisión + 3 semanas ejecución)
**Disparador:** Mauricio en llamada Google Meet 2026-06-12 ([grabación Fathom 8 min](https://fathom.video/share/dApEwspSmtq_tXUXGLjyCfEyNByQzLHR)) pidió paquetizar el agente de fallas para revender a uno de sus clientes que se lo solicitó.

---

## Contexto

Mauricio da soporte remoto a varios clientes que compraron máquinas TOFO. Uno de esos clientes le pidió literalmente *"préstame tu sistema de resolución de fallas"*. La pregunta concreta de Mauricio fue: *"¿cuánto me cobrarías por hacérmelo?"*. Confirmó en la llamada el modelo:

- Cada cliente final aloja el agente en SU propia infraestructura (su WhatsApp Business, su ManyChat, su n8n, su DB).
- Mauricio absorbe el costo del paquete y cobra a sus clientes finales como parte de las cuotas de servicio que ya les vende.
- Mauricio quiere precio bajo argumentando que "el agente ya existe".

Se asume **modelo paquetizado** (no implementación por cliente final por parte de la agencia): JSONs n8n + guías + system prompt + diagramas. Mauricio (o su dev) implementa. la agencia solo implementa por cliente final si entra como add-on cotizado aparte.

---

## Propuesta

Crear un paquete reusable de "agente de fallas técnicas" derivado del agente actual de TOFO, listo para que Mauricio lo revenda a cualquier pizzería que tenga máquinas similares.

### Componentes (8 entregables)

1. System prompt especializado en fallas (plantilla + guía de personalización con placeholders para catálogo de máquinas, fallas, política de reposición, técnico humano)
2. Workflow n8n principal generalizado (~25-30 nodos, importable directo)
3. Sub-workflow de escalamiento al técnico humano (1 rama, placeholders dinámicos)
4. Guía A — Preparación de infraestructura para cliente final (co-branded TOFO + "Powered by la agencia")
5. Guía B — Implementación técnica para Mauricio o su dev (~35 pp con screenshots)
6. Testing guide específica de fallas (15-20 casos QA con criterio binario)
7. Diagrama de arquitectura (.drawio + .png)
8. Sesión 60 min de handoff técnico (Zoom + grabación)

### Decisiones cerradas con la agencia (AskUserQuestion 2026-06-14)

| Decisión | Valor |
|---|---|
| Precio | USD 1.800 (50/50: USD 900 firma + USD 900 entrega) |
| Branding Doc A | Co-branded: TOFO arriba, "Powered by la agencia" footer |
| Telegram escalamiento | Descentralizado: cada cliente final tiene su propio bot |
| Stack default | A decidir en formulario S0 (recomendación: n8n Cloud + Airtable) |
| Tono prompt | A decidir en formulario S0 (recomendación: español MX heredado de TOFO) |
| Retainer | NO obligatorio (add-on opcional USD 120/mes) |
| Garantía | 30 días post-entrega sobre bugs del paquete original |

---

## Esfuerzo estimado

| Componente | Horas | Tarifa | Notas |
|---|---|---|---|
| Depuración prompt fallas (recortar B2B/RRSS/Servicio/Reposición) + guía personalización | 4-6 h | USD 65/h | Heredado de prompts v1.5/v1.4 TOFO |
| Adaptación workflow n8n main (generalizar credenciales, eliminar tools no-fallas, parametrizar hardcodes) | 4-6 h | USD 65/h | De 51 a ~25-30 nodos |
| Sub-workflow escalamiento simplificado (1 rama + placeholders) | 2-3 h | USD 65/h | De 6 a 4-5 nodos |
| Guía A cliente final (8 secciones, layperson, co-branded) | 4-6 h | USD 65/h | Plantilla SYS migration adaptada a "crear de cero" |
| Guía B técnica con screenshots (import n8n + setup ManyChat + DB + smoke + troubleshooting) | 6-8 h | USD 65/h | Cuello de botella: capturar pantallas en entorno limpio |
| Testing guide específica fallas (15-20 casos) | 3-4 h | USD 65/h | Heredo estructura de testing-guide-v4 |
| Diagrama arquitectura (.drawio + .png) | 1-2 h | USD 65/h | Standard |
| Sesión handoff (prep + 60 min Zoom + grabación + Loom complementario) | 3 h | USD 65/h | Walkthrough + smoke demo + Q&A |
| Buffer + admin (kickoff sync 30 min + revisión final + sync CLAUDE.md + commit) | 2-3 h | USD 65/h | |
| **Total estimado** | **29-40 h** | | A USD 65/h = USD 1.885 a 2.600 |

---

## Precio sugerido

**Opción única — Paquete completo**
- One-time: **USD 1.800** (50/50)
- Sin retainer mensual obligatorio
- 30 días de garantía sobre el paquete original

**Por qué USD 1.800 (vs USD 1.500 propuesta inicial):**
- A USD 1.500 → USD 37-52/h efectivo. Bajo para implementación técnica + redacción documentación operativa.
- USD 1.800 mantiene margen sano sin asustar a Mauricio (recupera en 2 reventas).
- Anclaje psicológico: USD 1.800 → "casi USD 2.000". USD 1.500 → "redondo, regalado".

**Por qué USD 1.800 (vs USD 2.500-3.000):**
- El argumento de Mauricio es válido en parte: el agente ya existe en producción, no es construcción desde cero.
- Mauricio es repeat customer; vale cuidar la relación.
- Los add-ons listados abajo abren revenue futuro sin presionar precio hoy.

---

## Add-ons disponibles (cotizables aparte)

| Add-on | Precio | Notas |
|---|---|---|
| Implementación llave en mano por cliente final | USD 500/cliente | la agencia hace setup completo en infra del cliente. Primer cliente USD 400 con descuento "vení mirá cómo se hace". |
| Mantenimiento mensual del paquete | USD 120/mes | Updates de prompt, fixes transversales que aprovechan todos los clientes finales. Empieza después de los 30 días de garantía. |
| Adaptación multi-idioma (en/pt) | USD 400/idioma | Incluye prompt + testing guide + diagrama traducido |
| Capacitación a dev de Mauricio | USD 250/sesión 90 min | Útil si incorpora dev nuevo |
| Nuevas tools sobre el paquete (ej. tabla "Casos Técnicos" + reporte semanal — ver `TFO-upsell-tabla-casos-tecnicos-2026-06-04.md`) | USD 65/h | Tarifa standard |

---

## Cronograma

| Semana | Trabajo | Hito |
|---|---|---|
| S1 | Depuración prompt + adaptación workflow main + sub-workflow escalamiento | Demo interna en sandbox |
| S2 | Generalización credenciales + Guía A + Guía B (draft) | Entrega draft de guías para review |
| S3 | Testing guide + diagrama + revisión final + sesión handoff | Entrega final + arranque garantía 30 días |

---

## Riesgos / consideraciones

1. **Mauricio quiere implementar sin acompañamiento.** Cláusula contractual ya armada (Doc C §10 riesgo #1): el paquete se entrega tal como se prueba en sandbox de la agencia. Bugs reproducibles → fix gratis 30 días. Problemas que solo aparecen en infra del cliente final = responsabilidad del implementador.
2. **Cliente final reclama directo a la agencia.** Cláusula: "Soporte único cliente final es responsabilidad de Mauricio. la agencia solo trata con Mauricio." Email pre-armado para que Mauricio le pueda mandar al cliente final si lo abordan.
3. **Pipeline de clientes finales de Mauricio.** No declarado en llamada. Si hay 1 cliente esperando con urgencia, abre conversación sobre add-on "primer cliente USD 400 llave en mano".
4. **Versionado del paquete vs TOFO en producción.** El paquete es derivado pero independiente. Mejoras al paquete NO se propagan automáticamente al agente TOFO, y viceversa. A definir si se sincronizan algunos componentes (ej. anti-alucinación).
5. **Sub-licenciamiento por Mauricio a otros revendedores.** Cláusula explícita: licencia para Mauricio + sus clientes finales directos. Si quiere revender el paquete como producto a otros developers/agencias, es otra estructura comercial.

---

## Cómo presentarlo al cliente

Propuesta externa formal ya redactada en [`clients/TFO_TOFO/01_discovery/propuesta-paquete-agente-fallas-mauricio-2026-06-14.md`](../../clients/TFO_TOFO/01_discovery/propuesta-paquete-agente-fallas-mauricio-2026-06-14.md).

Formato Markdown listo para Notion o copy-paste a WhatsApp. Tono cercano-profesional, español rioplatense, una sola opción (sin menú A/B/C).

Mensaje sugerido al mandar la propuesta:

> Hola Mauri, te paso la propuesta para el paquete del agente de fallas que charlamos el jueves. Una sola opción, USD 1.800 50/50. Adentro tenés todo lo que incluye, lo que no incluye, cronograma de 3 semanas y los add-ons opcionales por si más adelante querés implementación por cliente o mantenimiento. Cualquier duda me decís.

Adjuntar también la **Guía A** ([`clients/TFO_TOFO/06_docs/guia-infra-cliente-final-paquete-fallas-2026-06-14.md`](../../clients/TFO_TOFO/06_docs/guia-infra-cliente-final-paquete-fallas-2026-06-14.md)) como **preview de lo que su cliente recibiría** — refuerza la sensación de "ya está armado, no es promesa".

---

## Estado del upsell

- [x] Cliente disparó la conversación — 2026-06-12 (llamada Google Meet)
- [x] Propuesta + Guía A redactadas — 2026-06-14
- [ ] Propuesta enviada a Mauricio (WhatsApp + adjuntos)
- [ ] Aprobación recibida
- [ ] Primera cuota (USD 900) cobrada
- [ ] Formulario de decisiones de arranque enviado y respondido
- [ ] Kickoff técnico (30 min Zoom) agendado
- [ ] S1 completada — demo interna
- [ ] S2 completada — drafts de guías
- [ ] S3 completada — entrega final + handoff
- [ ] Segunda cuota (USD 900) cobrada
- [ ] Garantía 30 días arrancada
- [ ] Garantía 30 días cumplida — paquete cerrado

---

## Archivos relacionados

- **Propuesta externa (la que Mauricio lee):** [`clients/TFO_TOFO/01_discovery/propuesta-paquete-agente-fallas-mauricio-2026-06-14.md`](../../clients/TFO_TOFO/01_discovery/propuesta-paquete-agente-fallas-mauricio-2026-06-14.md)
- **Paquete interno (control de scope, horas, riesgos):** [`clients/TFO_TOFO/01_discovery/paquete-agente-fallas-mauricio-2026-06-14.md`](../../clients/TFO_TOFO/01_discovery/paquete-agente-fallas-mauricio-2026-06-14.md)
- **Guía A cliente final (co-branded):** [`clients/TFO_TOFO/06_docs/guia-infra-cliente-final-paquete-fallas-2026-06-14.md`](../../clients/TFO_TOFO/06_docs/guia-infra-cliente-final-paquete-fallas-2026-06-14.md)
- **Upsell relacionado (tabla Casos Técnicos):** [`TFO-upsell-tabla-casos-tecnicos-2026-06-04.md`](TFO-upsell-tabla-casos-tecnicos-2026-06-04.md) — se puede ofrecer como add-on del paquete reventa para cualquier cliente final que quiera métricas operativas.
