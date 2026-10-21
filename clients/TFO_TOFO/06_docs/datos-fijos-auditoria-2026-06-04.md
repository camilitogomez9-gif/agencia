# Auditoría de datos fijos — TOFO Pizza (prompts v1.3)

**Fecha:** 2026-06-04
**Update 2026-06-05:** Mauricio respondió las preguntas. Detalle en [`respuestas-mauricio-datos-fijos-2026-06-05.md`](respuestas-mauricio-datos-fijos-2026-06-05.md). Las secciones §2 y §3 de este doc se mantienen como histórico; **los datos canónicos actualizados están en §3 del doc de respuestas**.
**Update 2026-06-05 (PM):** post-incidente Oscar Amaya — el agente B2B v1.4 prometió Opción B sin validar moneda. Solucionado en B2B v1.5 con protocolo de moneda + sección de financiamiento externo. Detalle: [`incidente-confusion-moneda-2026-06-05.md`](incidente-confusion-moneda-2026-06-05.md). Nuevos datos canónicos (TC ~17.5 MXN/USD + equivalencias MXN + 3 categorías financiamiento) sumados al doc de respuestas §3.9.
**Alcance:** los 5 system prompts vigentes en `clients/TFO_TOFO/04_agents/` (Derivación, B2B, Servicio, Reposición, RRSS).
**Objetivo:** consolidar la single source of truth de los datos que el agente puede usar, detectar inconsistencias internas, identificar vacíos que causen alucinación, y proponer un mecanismo anti-alucinación uniforme.

---

## §1 — Datos autorizados actuales (single source of truth)

Tabla consolidada de lo que YA está en los prompts. Cualquier dato no listado aquí **NO está autorizado** y el agente no debería mencionarlo.

### 1.1 Identidad del negocio

| Dato | Valor | Prompts donde aparece |
|---|---|---|
| Web oficial | `tofo.mx` | Servicio, RRSS |
| Zona de operación | Guadalajara / Zapopan, México | RRSS |
| Tono | Español de México (sin voseo) | Los 5 (vigente desde v1.3) |
| Nombre del agente | (sin nombre propio definido) | — |

### 1.2 Ubicaciones (5 puntos canónicos)

| Sucursal | Zona sugerida | Google Maps |
|---|---|---|
| Flex Norte | Zona norte / Zapopan norte | (link pendiente) |
| Flex Sur | Zona sur / López Mateos / Chapalita | (link pendiente) |
| UAG | Zona UAG / Av. Patria / Lomas del Valle | (link pendiente) |
| Plaza Patria | Zona Plaza Patria / Zapopan | (link pendiente) ⚠ |
| Estación Juárez | Zona Juárez / Centro / Estaciones tren | (link pendiente) ⚠ |

**Aparece en:** Servicio (L92-97), RRSS (L85-91, L144-145), Reposición (L48-49). El Agente B2B y Derivación **no las listan** intencionalmente (no es su rol).

### 1.3 Sabores y precios al consumidor

| Sabor | Precio |
|---|---|
| Pepperoni | $119 MXN |
| Hawaiana | $119 MXN |
| 4 Quesos | $119 MXN |
| Nutella 🍫 | $139 MXN |
| Al Pastor 🌮 | $139 MXN |

**Aparece en:** Servicio (L71-80), RRSS (L67-72). Pizza de 12" (30 cm), 8 rebanadas, lista en menos de 3 minutos.

### 1.4 Disponibilidad y horarios

| Concepto | Valor |
|---|---|
| Disponibilidad máquinas | 24/7 |
| Ventana B2B agendamiento (director) | **Lun–Vie, inicios 10:00 / 11:00 / 12:00 hora México (CDMX)**, último bloque 12:00–13:00 |

⚠ La ventana B2B está definida en el prompt B2B v1.3 línea 336. El sub-workflow Chequear disponibilidad v1 tiene una variante contradictoria que se corrige en v2 (ver `guia-fix-chequear-disponibilidad-2026-06-04.md`).

### 1.5 Modelos B2B

| Modelo | Precio | Qué incluye |
|---|---|---|
| **Opción A — Puesta en China** | $9.300 USD + IVA | Cliente gestiona importación, aduana (arancel 40% vigente), flete, seguro, configuración. Sin soporte local. |
| **Opción B — Puesta en México** | $26.300 USD + IVA | TOFO resuelve: importación, aranceles, flete, seguro, software en español, soporte técnico local, refacciones en México, configuración completa. |

**Ambas opciones:**
- ✅ White label (la máquina puede llevar la marca del cliente)
- ✅ Sin venta de insumos por TOFO; asesoría sobre proveedores
- Pago: 50% al ordenar + 50% antes de envío

**Especificaciones técnicas:** 220V / 35A, 500 kg, con llantas (movible por una persona), control total desde celular.

**Modelo base de referencia (B2B L185-195):** insumo $70/pizza · venta $129 · margen $59 · renta $2.000 MXN/mes · tráfico 1.000 pers/día · conversión 5% = 50 pizzas/día. Es escenario asumido — disclaimer obligatorio cuando el lead pide proyecciones (L198-201).

### 1.6 Aranceles

| Dato | Valor |
|---|---|
| Arancel actual sobre máquinas importadas de China | 40% (desde 1 enero de 2026) |
| Arancel previo (anterior al 40%) | (no especificado en prompts) |
| Stock con arancel previo | "Aún hay máquinas disponibles" (B2B L120) — sin cantidad ni fecha límite |

⚠ Falta fecha de expiración del 40%. Ver §3.

### 1.7 ManyChat (routing automático)

| Tag / flow_ns | Acción | Destino |
|---|---|---|
| `tipo='b2b'` + `elevar_conversacion` | Flow `content20260526142445_613819` | Mauricio (director B2B): asignación + mail + pausa bot |
| `tipo='repo'` + `elevar_conversacion` | Flow `content20251129220130_658273` | Miguel (técnico): asignación + notificación + pausa bot |
| `tipo=''` + `elevar_conversacion` | Fallback | Mauricio |
| Tag `FALLA_TECNICA` | (cleanup manual por Miguel — auto-cleanup descartado) | — |

### 1.8 Personas internas (no se muestran al cliente)

| Rol | Nombre completo (ManyChat) |
|---|---|
| Director B2B | Mauricio García de la Vega |
| Técnico (Reposición/Servicio) | José Miguel Chumacera González |

---

## §2 — Inconsistencias internas detectadas

### 2.1 "Plantas Flex" — producto fantasma 🚨

- **Aparece en:** Servicio L83-85 — "Plantas Flex (clásicas) $109 MXN / Plantas Flex (Nutella / Al Pastor) $129 MXN".
- **NO aparece en:** RRSS, B2B, Reposición, Derivación.
- **Riesgo:** un lead que viene por RRSS pregunta por Plantas Flex y el agente RRSS no tiene info → improvisa o pide aclaración inconsistente.
- **Pregunta a Mauricio:** ¿qué es Plantas Flex? ¿producto vigente? ¿precio real? ¿en qué sucursales se vende? ¿es un nombre interno o de cara al cliente?
- **Fix candidato v1.4:** confirmar y agregar a RRSS, o eliminar de Servicio.

### 2.2 "Al Pastor" vs "Pastor"

- **Servicio L73-74:** "Al Pastor 🌮"
- **RRSS L67:** "Pastor y edición especial Nutella 🍫"
- **Fix:** unificar a "Al Pastor" en los 2 prompts (la versión más completa).

### 2.3 Modelo Base B2B asume venta uniforme $129

- **B2B L190:** asume precio de venta $129 MXN en el modelo de proyección.
- **Realidad:** los precios reales son $119 (3 sabores) y $139 (Nutella + Al Pastor).
- **Riesgo:** si el lead pregunta "y la proyección con mi mix real de sabores?", el agente no tiene fórmula.
- **Fix:** aclarar en el prompt v1.4 que $129 es promedio asumido. Mantener disclaimer L198-201.

### 2.4 Arancel 40% sin fecha de expiración

- **B2B L119:** "Los aranceles subieron al 40% desde el 1 de enero" (contexto = 2026 implícito).
- **No dice hasta cuándo dura, ni qué pasa si baja.**
- **Riesgo:** un lead que vuelva en 6 meses recibe la misma respuesta aunque el arancel haya cambiado.
- **Fix candidato v1.4:** agregar "válido al [fecha de versión del prompt]" o disclaimer "consultá fecha vigente con el equipo".

### 2.5 Ventana laboral B2B inconsistente entre prompt y sub-workflow

- **Prompt B2B v1.3 L336:** "Lunes a Viernes 10:00am–13:00pm (siendo las 12:00 el último cupo)".
- **Sub-workflow `Chequear disponibilidad` v1:** prompt LLM con 3 reglas contradictorias (10–13, 10–12, último bloque 12–13).
- **Decisión 2026-06-04:** fuente de verdad es el prompt B2B — inicios `{10, 11, 12}`, último bloque 12:00–13:00. Sub-workflow v2 implementa esto. Ver `guia-fix-chequear-disponibilidad-2026-06-04.md`.

---

## §3 — Vacíos críticos (preguntas para Mauricio)

Versión WhatsApp-friendly de esta sección en [`preguntas-mauricio-datos-fijos-2026-06-04.md`](preguntas-mauricio-datos-fijos-2026-06-04.md).

### 3.1 Bloqueantes para promote a LIVE

1. **Email de contacto general** — ¿`info@tofo.mx`? ¿otro? Hoy ningún prompt tiene email. Si un lead pregunta "mándame info al mail", el agente puede inventarse uno.
2. **Teléfono/WhatsApp general TOFO** — Servicio menciona "WhatsApp de la máquina" pero sin número. ¿Cuál es el número público?
3. **Política de cancelación B2B** — Si paga 50% y cancela, ¿pierde todo? ¿retiene parte? ¿tiene plazo?
4. **Garantía post-venta B2B** — Plazo (¿6 meses? ¿1 año?), qué cubre, cómo reportar, tiempo de respuesta. Solo aplica a Opción B (México) o también A (China)?
5. **Política de devolución máquina** — ¿hay periodo de prueba? ¿se puede devolver?
6. **"Plantas Flex"** — ¿producto vigente? ¿precio real? ¿en qué sucursales? (ver §2.1)
7. **Arancel 40%** — ¿fecha de expiración? ¿cuántas máquinas con arancel previo quedan en stock?

### 3.2 Importantes (alta probabilidad de pregunta)

8. **Google Maps links** de las 5 sucursales (especialmente Plaza Patria y Estación Juárez — RRSS los marca como "pendientes" L93-94).
9. **Direcciones físicas exactas** de cada sucursal (calle, número, referencia).
10. **Lista de proveedores recomendados de insumos** para B2B. El prompt B2B dice "te asesoramos sobre proveedores" pero no los nombra.
11. **Horario humano de Servicio al Cliente** — si un lead pide hablar con humano por fuera del flujo B2B, ¿cuándo hay alguien para atender?

### 3.3 Nice to have

12. **Nombre propio del agente** — hoy no tiene. ¿"Tofito"? ¿"Sofía"? ¿genérico? Ayuda a humanizar.
13. **Última versión del contrato/garantía B2B** — para poder referenciarlo cuando el lead pregunta "mándame el contrato".

---

## §4 — Mecanismo anti-alucinación recomendado

### 4.1 Bloque común para los 5 prompts en v1.4

```markdown
## ⚠️ Anti-alucinación

Si te preguntan un dato puntual (email, teléfono específico, precio fuera de tu lista,
dirección exacta de sucursal, política de cancelación o garantía, horario humano de soporte,
nombre de proveedor) y NO está literalmente en estas instrucciones:

❌ NO inventes
❌ NO improvises
❌ NO uses tu conocimiento general — solo lo que está acá

✅ Decí: "Dejame consultarlo con el equipo y te confirmo en unos minutos."
✅ Activá `elevar_conversacion` con `tipo='b2b'` si es contexto B2B,
   o `tipo=''` si es consulta general.

Datos que SÍ tenés autorizados (consultá esta lista antes de responder):
- Sabores y precios consumidor: ver tabla en este prompt.
- Sucursales canónicas: Flex Norte, Flex Sur, UAG, Plaza Patria, Estación Juárez.
  Si te mencionan otra ("Flex Oriente", "Flex Centro"), decí: "No tenemos esa
  sucursal. Nuestras 5 ubicaciones son..." (y listá las canónicas).
- Web: tofo.mx
- Disponibilidad máquinas: 24/7
- Ventana B2B agendamiento: Lun–Vie 10:00, 11:00 o 12:00 hora México (CDMX).
- Modelos B2B: Opción A $9.300 USD + IVA / Opción B $26.300 USD + IVA.
- Arancel sobre máquinas de China: 40% (vigente al [FECHA DE VERSIÓN DEL PROMPT]).
```

### 4.2 Adaptaciones por prompt

- **Derivación** — agregar regla: "Si el lead pregunta un dato puntual antes de derivar, **derivá al subagente correspondiente y dejá que él decida si activar elevar_conversacion**. No respondas datos vos."
- **RRSS** — agregar validación: "**Antes de mencionar una sucursal, verificá que esté en la lista canónica de 5.** Si te piden una zona que no está mapeada, ofrecé las 2 más cercanas y aclará que no tenemos punto exacto allí."
- **B2B** — agregar al final de "Aranceles": "Si el lead pregunta hasta cuándo dura el 40%, decí: 'No tengo esa fecha confirmada al día. Lo mejor es que te lo confirme directamente el director en la llamada.'"
- **Servicio** — resolver "Plantas Flex": **eliminar del prompt si Mauricio confirma que es interno**, o **agregar a RRSS** si es producto de cara al cliente.
- **Reposición** — ya tiene anti-alucinación fuerte por imágenes. Solo agregar el bloque común.

---

## §5 — Datos repetidos en múltiples prompts (oportunidades de centralización)

| Dato | Aparece en | Riesgo de drift |
|---|---|---|
| 5 sucursales | Servicio, RRSS, Reposición | Medio — ya hay variaciones de naming |
| 5 sabores | Servicio, RRSS, Reposición | Bajo — solo "Al Pastor"/"Pastor" |
| `tofo.mx` | Servicio, RRSS (×6) | Bajo — único |
| 24/7 | Servicio, RRSS (×5) | Bajo |
| Especificaciones técnicas (12"/8 rebanadas/3min) | Servicio, RRSS | Bajo |
| ManyChat flow_ns | Documentación interna (changelog v1.3) en B2B y Reposición | Bajo — solo internas |

**Recomendación a futuro:** considerar mover los datos compartidos a un archivo `_core/clients/TFO_TOFO/datos-canonicos.md` referenciado desde todos los prompts. Hoy no es bloqueante.

---

## Referencias

- [Prompt Derivación v1.3](../04_agents/agente-tofo-derivacion-system-prompt.md)
- [Prompt B2B v1.3](../04_agents/agente-tofo-b2b-system-prompt.md)
- [Prompt Servicio v1.3](../04_agents/agente-tofo-servicio-system-prompt.md)
- [Prompt Reposición v1.3](../04_agents/agente-tofo-reposicion-system-prompt.md)
- [Prompt RRSS v1.3](../04_agents/agente-tofo-rrss-system-prompt.md)
- [Preguntas para Mauricio](preguntas-mauricio-datos-fijos-2026-06-04.md)
- [Plan completo](/Users/camilo/.claude/plans/users-la agencia-downloads-chequear-disponibi-frolicking-crescent.md)
