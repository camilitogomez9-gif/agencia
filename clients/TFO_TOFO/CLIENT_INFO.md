# TFO — TOFO Pizza

## Datos generales
- ID: TFO
- Nombre: TOFO
- Niche: generic (food-tech / robotic vending)
- Fecha inicio: 2026-05-06
- Status: **live — sin pendientes abiertos al 2026-08-04** (se cerró la cola de junio: P0 de citas Zoom, calendar overlaps + tool rogue, deploy de los 3 prompts, Zoom auto-agendamiento, envío automático de ficha técnica/video y decisión del plan de Airtable)

## Stack activo
- [x] n8n
- [x] Airtable
- [ ] Clientify
- [x] Google Sheets
- [x] WhatsApp
- [ ] Notion

## Integraciones adicionales
- OpenAI GPT-4.1 (LLM principal, todos los agentes)
- Google Docs (base de conocimiento subagentes)
- Google Calendar (agendamiento reuniones B2B)
- Zoom (videollamadas B2B)
- Instagram, Facebook (canales adicionales)

## Contactos clave
| Rol | Nombre | Contacto |
|-----|--------|---------|
| Decisor / Dueño | Mauricio García de la Vega | mauriciogarciadelav@gmail.com |
| Técnico | José Miguel Chumacera | (ya en ManyChat) |

## OKRs del proyecto
1. Agente multi-canal funcional (WhatsApp / IG / FB) con derivación automática por intención
2. Pipeline B2B con cualificación completa y registro en Airtable (Leads B2B TOFO Pizza)
3. Escalamiento a humano operativo (elevar_conversacion) + agendamiento via Google Calendar + Zoom

## Arquitectura del agente

Sistema multi-agente de derivación:

| Agente | Función |
|--------|---------|
| Agente de Derivación | Routing principal — detecta intención → activa subagente correcto |
| Agente de RRSS | Consumidores: producto, sabores, precios, ubicaciones, redes sociales |
| Agente de B2B | Prospectos de inversión/concesión/compra de máquina — cualifica y agenda |
| Agente de Servicio al Cliente | Fallas, errores, doble cobro, quejas, reposiciones |
| Agente de Reposición | Sub-agente de reposición de productos |

## Notas críticas
- Empresa registrada: Robotic Vending de México, S.A. de C.V.
- Operaciones en Guadalajara, Jalisco, México. **5 sucursales oficiales con naming canónico**: Flex Norte, Flex Sur, UAG, Estación Plaza Patria, Estación Juárez. (Naming previo "Tren Ligero" y "The Landmark" estaba desactualizado.)
- **Pricing por grupo (consumidor)**: Estaciones + UAG = $119/$139 MXN (clásicas/Nutella+Al Pastor) · Flex Norte/Sur = $109/$129 MXN (descuento especial, NO promocionar en RRSS).
- El agente B2B maneja **2 modelos de venta** (no concesiones ni franquicias): **Opción A — puesta en China** $9,300 USD + IVA (~$165k MXN, cliente importa) · **Opción B — puesta en México** $26,300 USD + IVA (~$460k MXN, llave en mano white label). TC referencial ~17.5 MXN/USD. TOFO NO da financiamiento directo — entrega factura para banco/arrendadora/financiera.
- **Funcionamiento de la máquina (info canónica autorizada 2026-06-08)**: las pizzas vienen pre-elaboradas (base **pre-horneada al 75%** + ingredientes frescos ya colocados). **La máquina NO prepara la pizza desde cero** — solo termina el horneado al momento del pedido (<3 min). Cualquier afirmación distinta es alucinación.
- Horario de reuniones B2B: Lunes a Viernes a las **10:00, 11:00 o 12:00 hora México** (CDMX). Ventana fija — fuera de esos slots se rechaza sin invocar la tool.
- **Sub-workflow `check_disponibilidad`** (`vpLmZ299yXJrOSBv`, active) es la **única vía técnica de creación de evento en el calendar**. El agente tiene prohibido confirmar citas sin haber invocado la tool y recibido `libre: true` (incidente Mauricio 2026-06-08).
- Leads B2B se registran en Google Sheets: "Leads B2B TOFO Pizza" (ID: 1zhzYSKMWDIyFFanqOv2glYVU102Gw8oZcXx2dPFLA-s)
- Web del cliente: tofo.mx

## Versiones vivas de prompts (al 2026-06-22)
- B2B: **v1.17** — ✅ **deployado al n8n vivo el 2026-08-04** (prompt hardcodeado: todo bump futuro exige copy-paste al `systemMessage`). **Instrucción Mauricio 22/6/26**: (1) **precio detrás del gate nombre + ubicación** — §9 reescrita REVIRTIENDO v1.9; el precio de la máquina (USD 9.300/26.300) ya NO se da antes de capturar nombre + ubicación del lead (mismos dos datos del gate de `registrar`). Escenario 1 (lead pregunta precio sin gate) → pedir nombre+ubicación primero con framing de cortesía, sin soltar la cifra; al completar ambos → `registrar` + precio. Escenario 2 (proactivo) → capturar datos, luego consent question. El gate retiene SOLO la cifra; el resto (funcionamiento, specs, diferencias sin números) fluye libre. (2) **citas de 30 minutos** — prompt (§Cómo agendar "1 hora"→"30 min", §🔟 dossier "15 min"→"30 min") **+ sub-workflow `chequear-disponibilidad-tofo-v4.json`** (el evento de Calendar pasaba de `inicio+1h` a `inicio+30 min`; el Zoom ya era 30 min). Testing v9 §Q (gate): **8/8 respuestas del agente verificadas correctas por inspección manual** (gate cumplido al 100%); juez gpt-4o-mini rota 1 false/corrida por artefacto (marca "precios oficiales"/"40% arancel" como precio). Backup v1.16 preservado. Sin tocar RRSS (precio de menú = retail, no aplica el gate de lead) ni los otros 3 subagentes.
- B2B v1.16 (anterior): Datos canónicos de funcionamiento cerrados con la ficha técnica oficial de Mauricio: agrega DATO CANÓNICO #4 (HORNO de convección de aire eléctrico giratorio + 350°C + 3-5 min + 60 pizzas/día producción + sin refrigeración activa) en §🍕 + nueva sección §📋 ESPECIFICACIONES TÉCNICAS (1800×1100×2350 mm · 550 kg · 220V/60Hz/35A/6.5kW · pantalla 51" · 4G+Wi-Fi · pago tarjeta/contactless · 24/7). Anti-aluc actualizada: 8 preguntas que antes derivaban al director ahora se responden con info canónica; las preguntas que no están en la ficha (quién carga, frecuencia recarga, capacidad almacenamiento interna, conservación, sabores custom B2B, proceso interno) siguen derivando al director — sin invención. Backup v1.15 preservado.
- B2B v1.15 (anterior): vivo en n8n ✅ (sesión Airtable gate v1.12 + Calendar overlaps fix v1.15). Hereda v1.11 (timing "EN EL MISMO TURNO" + field list alineada al tool schema) + v1.10 (sección GATE — solo invocar `registrar` con nombre + ubicación explícitos en chat). v1.12 cerró escape hatch del campo `Ubicación Mencionada`. v1.15 agregó REGLA ABSOLUTA #4 (PROHIBIDO invocar tools de Calendar/Zoom alternativas a `check_disponibilidad`).
- RRSS: **v1.9** — ✅ **deployado el 2026-08-04** (prompt hardcodeado, igual que B2B). Alinea tiempo de cocción a ficha oficial ("menos de 3 minutos" → "3 a 5 minutos") en 11 lugares. Hereda v1.8 (gate escape hatch fix) + v1.7 (field list) + v1.6 (GATE).
- Servicio: **v1.6** — ✅ **deployado el 2026-08-04**. Mismo fix de tiempo de cocción que RRSS v1.9 — 3 ocurrencias actualizadas a "3 a 5 minutos". Hereda v1.5 (sección 🍕 + anti-aluc).
- Derivación: **restaurado del snapshot 4/6/26** — vivo en n8n ✅ (era un B2B clone de 52KB, restaurado al derivador real de 7KB que delega a subagentes). Sin este fix el subagente B2B nunca se invocaba para registrar leads.
- Reposición: v1.4 — vivo (sin cambios en bump 2026-06-08)
- Testing guide: **v9** (precio detrás del gate §Q + citas 30 min §R; hereda §A-§P de v8). §Q corrido contra gpt-4.1: 8/8 respuestas del agente verificadas correctas (gate enforced); §J de v7/v8 SUPERSEDED por §Q. Históricos: v8 §P anti-tool-rogue · v4 §G regression incidente 2026-06-08 · smoke Airtable gate v1.12 4/4 PASS 2026-06-21

## Fix Airtable Gate — sesión 2026-06-21 (resumen)
**Objetivo cumplido**: criterio Mauricio 18/6/26 ("solo registrar leads que dejen nombre + lugar"). De ahora en adelante Airtable solo recibe leads cualificados.
**Cambios estructurales**:
1. `Crear contacto inicial` eliminado del main workflow (era el causante de ~580 records vacíos "contacto a redes sociales" del renglón 488+).
2. Tool `registrar` rediseñada (schema v2): 14 campos = 6 determinísticos + 8 `$fromAI` con descripciones non-empty (anti bug Zod). Nuevo campo `Nombre completo` (LLM, del chat). `Nombre / Usuario` ahora determinístico (display name del webhook).
3. `Dias de proceso` migrado a fórmula Airtable `DATETIME_DIFF(NOW(), {Fecha captado}, 'days')`.
4. Derivación restaurado al rol real (delega a subagentes) — antes era B2B clone que respondía directo sin delegar.
**Outputs**: main v4 snapshot, tool node JSON listo para Cmd+V, guía de deploy, 4 smokes E2E validados.
**Pendientes: ✅ ninguno al 2026-08-04.** El cleanup retroactivo se hizo y Mauricio ya decidió el tema del plan de Airtable.
