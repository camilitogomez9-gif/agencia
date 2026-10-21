# Respuestas de Mauricio a `preguntas-mauricio-datos-fijos`

**Fecha:** 2026-06-05
**Origen:** mensaje de Mauricio en respuesta al doc `preguntas-mauricio-datos-fijos-2026-06-04.md`
**Próximo paso:** integrar al bump v1.4 de los 5 prompts (este mismo turno).

---

## §1 — Respuestas verbatim

```
•  no quisiera que de mi numero el agente.
•  las sucursales son : Flex Norte, Flex Sur, UAG, Estación Plaza Patria, estación Juarez.
•  En RRSS no me gustaria promocionar los precios de Flex. hay que dejar los precios de las
   estaciones en RRSS. Tenemos descuento especial en Flex.
•  El arancel inicio en enero de 2026 y ya es vigente. en 2025 era del 15%
•  Nos quedan muy pocas maquinas con el arancel anterior, asi que tendremos que cambiar el precio pronto.
•  Plaza Patria. https://maps.app.goo.gl/7rg8ee2SvS4T4TGN6
•  Juarez. https://maps.app.goo.gl/rADUpM1z3HA3s9YK9
•  UAG. https://maps.app.goo.gl/NwpXm9KL3HBpspxT7
•  Flex Norte. https://maps.app.goo.gl/tT4S4iS17jxithpD7
•  Flex Sur. https://maps.app.goo.gl/LY9FEN3uQywD3U8G9
•  para los insumos, tofo pizza te pasa la receta y te ayuda a encontrar un proveedor local,
   ya que con eso evitas gastos de transporte de suministros.
•  Para refacciones, tofo pizza tiene un stok de refacciones en Gudalajara, con lo que no debes
   esperar a que llegue desde china una refaccion para reparar tu maquinao darle mantenimiento.
•  No quiero que me llamen si no tienen alguna compra o falla.
•  EMMA Vivanti en mi avatar de RRSS, ella puede ser el bot. y decir que es una agente de IA.
•  no quiero mandar documentación como contrato, etc. porque creo que hay competidores que
   solamente están buscando sacarnos información.
```

---

## §2 — Mapeo a las 13 preguntas

| # | Pregunta original | Estado | Respuesta interpretada |
|---|---|---|---|
| 1 | Email de contacto | ❌ Sin respuesta directa | Postura inferida: el agente NO da email. Canaliza todo por el chat. Combinado con (2) y (13). |
| 2 | Teléfono/WA general TOFO | ✅ Resuelto | "No quisiera que de mi número el agente." → el agente NO da número. |
| 3 | Política cancelación B2B | ❌ Sin respuesta | Anti-alucinación: si preguntan → "lo conversamos en la llamada con el director". |
| 4 | Garantía post-venta B2B | 🟡 Parcial | Stock de refacciones en Guadalajara (no se espera envío desde China). Plazo y cobertura formal NO definidos → tratar como B2B detalle a charlar en la llamada. |
| 5 | Política devolución | ❌ Sin respuesta | Anti-alucinación: "lo conversamos en la llamada con el director". |
| 6 | "Plantas Flex" | ✅ Resuelto | NO es producto separado. **"Flex" = sucursales Flex Norte / Flex Sur** (en gimnasios Flex), con **descuento especial** ($109 clásicas / $129 Nutella o Al Pastor). Las **Estaciones** (Plaza Patria, Juárez) y **UAG** mantienen **precio normal** ($119 clásicas / $139 Nutella o Al Pastor). En RRSS: **NO promocionar precios de Flex**. Sólo precios de Estaciones/UAG. |
| 7 | Arancel 40% — fecha y stock | ✅ Resuelto | Vigente desde 1-enero-2026 (no expira por ahora). En 2025 era 15%. **Quedan pocas máquinas con arancel 15% en stock** → urgencia comercial (precio actual va a subir cuando se agoten). |
| 8 | Direcciones físicas | 🟡 Parcial | Resuelto con links Google Maps (suficiente para Maps embed o "te paso ubicación"). Direcciones verbales NO entregadas. |
| 9 | Google Maps links | ✅ Resuelto | Los 5 links entregados (ver §3). |
| 10 | Proveedores de insumos B2B | ✅ Resuelto | TOFO **NO** entrega lista de proveedores. **TOFO pasa la receta y ayuda a encontrar proveedor local** (evita costos de transporte). |
| 11 | Horario humano de Servicio | ✅ Resuelto | Mauricio NO quiere recibir llamadas que no sean compra o falla. → El agente NO escala a humano para consultas genéricas, solo para B2B (compra) y Reposición/Servicio (falla). |
| 12 | Nombre propio del agente | ✅ Resuelto | **EMMA Vivanti** — adopción solo en el prompt RRSS. Debe identificarse como **agente de IA** (transparencia). |
| 13 | Contrato/garantía PDF | ✅ Resuelto | NO mandar documentación. Refuerzo de la regla actual en B2B v1.3 (ya prohibía dossiers/PDFs). Motivo: competidores buscando sacar info. |

---

## §3 — Datos autorizados — actualización completa

### 3.1 Sucursales canónicas (5) — naming oficial corregido

| Naming oficial | Grupo | Pricing | RRSS |
|---|---|---|---|
| **Flex Norte** | Flex (gimnasio) | Descuento especial: $109 / $129 | NO promocionar precios |
| **Flex Sur** | Flex (gimnasio) | Descuento especial: $109 / $129 | NO promocionar precios |
| **UAG** | Punto público (campus) | Precio normal: $119 / $139 | SÍ promocionar |
| **Estación Plaza Patria** | Estaciones (tren) | Precio normal: $119 / $139 | SÍ promocionar |
| **Estación Juárez** | Estaciones (tren) | Precio normal: $119 / $139 | SÍ promocionar |

⚠ Cambios de naming vs auditoría 2026-06-04:
- Antes: "Plaza Patria" → ahora **"Estación Plaza Patria"**.
- Antes: "Estación Juárez" → confirmado.
- Antes "Plantas Flex" como producto → **eliminar**, era nomenclatura interna para los precios de las sucursales Flex.

### 3.2 Google Maps (5 links)

- Flex Norte: https://maps.app.goo.gl/tT4S4iS17jxithpD7
- Flex Sur: https://maps.app.goo.gl/LY9FEN3uQywD3U8G9
- UAG: https://maps.app.goo.gl/NwpXm9KL3HBpspxT7
- Estación Plaza Patria: https://maps.app.goo.gl/7rg8ee2SvS4T4TGN6
- Estación Juárez: https://maps.app.goo.gl/rADUpM1z3HA3s9YK9

### 3.3 Precios consumidor por grupo

**Estaciones + UAG (precio normal):**
- Pepperoni / Hawaiana / 4 Quesos: $119 MXN
- Nutella / Al Pastor: $139 MXN

**Flex Norte y Flex Sur (descuento especial):**
- Pepperoni / Hawaiana / 4 Quesos: $109 MXN
- Nutella / Al Pastor: $129 MXN

### 3.4 Aranceles

| Año | Arancel | Estado |
|---|---|---|
| 2025 | 15% | Stock muy bajo de máquinas con este arancel |
| 2026 (desde enero) | 40% | Vigente |

**Implicación comercial:** los precios actuales ($9.300 Opción A / $26.300 Opción B) se basan parcialmente en stock con arancel 15%. Cuando se agote → suben. Comunicar urgencia. El agente puede mencionar "estamos por cambiar el precio pronto" en el flujo B2B sin dar fecha.

### 3.5 Insumos B2B

TOFO entrega:
- ✅ La **receta** completa.
- ✅ **Ayuda a encontrar proveedor local** (evita costos de transporte).

NO entrega:
- ❌ Lista nominal de proveedores.
- ❌ Contratos con proveedores específicos.

### 3.6 Refacciones (diferencial B2B)

**Stock de refacciones en Guadalajara** — el cliente NO espera envío desde China para reparar/mantener su máquina. Esto es una ventaja diferencial frente a comprar directo en Alibaba (Opción A).

### 3.7 Identidad del agente

**Solo en RRSS:** Emma Vivanti, agente de IA. Identificarse como tal con transparencia.
**Otros prompts:** sin nombre propio (subagentes no se presentan; Derivación es genérico).

### 3.8 Política de comunicación (decisión Mauricio)

- ❌ NO compartir teléfono, email, contrato, dossier, PDF, brochure.
- ✅ Canalizar TODO por el chat (`elevar_conversacion` cuando corresponda).
- ❌ NO escalar a humano para consultas que no sean compra o falla.
- ✅ Para compra B2B: agendar llamada con director (vía sub-workflow `check_disponibilidad`).
- ✅ Para falla técnica: derivar a Miguel vía ManyChat (`tipo='repo'`).

### 3.9 Moneda y financiamiento (agregado post-incidente Oscar Amaya, 2026-06-05)

**Datos canónicos:**
- TC de referencia: ~17-18 MXN/USD (2026). El director confirma TC final.
- Equivalencias canónicas con disclaimer:
  - Opción A: $9.300 USD + IVA ≈ ~$165.000 MXN + IVA
  - Opción B: $26.300 USD + IVA ≈ ~$460.000 MXN + IVA

**Reglas operativas:**
- Si el lead menciona un monto sin especificar moneda → **siempre preguntar MXN o USD antes de cotizar / afirmar elegibilidad**.
- Comunicar siempre ambas monedas cuando se cite una opción + disclaimer "el TC final lo confirma el director".

**Financiamiento (TOFO no da financiamiento directo):**
- Las máquinas se entregan con **factura**.
- Con la factura el cliente puede buscar financiamiento en:
  - **Bancos** (líneas de crédito empresarial, tarjetas, créditos)
  - **Arrendadoras** (leasing financiero/operativo)
  - **Financieras** (créditos específicos para equipo)
- NO recomendar un banco/arrendadora/financiera específico.
- NO prometer tasas, plazos ni porcentajes.

Detalle del incidente en [`incidente-confusion-moneda-2026-06-05.md`](incidente-confusion-moneda-2026-06-05.md). Aplicado en **B2B v1.5**.

---

## §4 — Delta por prompt para v1.4

### 4.1 Derivación
- Agregar bloque **anti-alucinación común** (no inventar email/tel/contrato; canalizar por chat).
- Reforzar regla: solo `elevar_conversacion` para B2B o Reposición/Servicio. Para todo lo demás, responder con datos canónicos o decir "no tengo ese dato puntual".

### 4.2 B2B
- Aclarar **arancel transitorio**: "Hasta 2025 el arancel era 15%; desde enero 2026 subió a 40%. Quedan pocas máquinas con el precio anterior — comunicar urgencia."
- Aclarar **stock refacciones GDL** como diferencial frente a Alibaba.
- Aclarar **política insumos**: receta + ayuda a buscar proveedor local (no lista nominal).
- Reforzar **prohibición de mandar contratos/PDFs** (ya existe; razón: competidores).
- Agregar bloque anti-alucinación (cancelación, devolución, garantía formal → "lo charlamos en la llamada con el director").
- Mantener objetivo: llamada con director vía `check_disponibilidad`.

### 4.3 Servicio
- Eliminar mención "Plantas Flex" como producto.
- Reemplazar por **tabla 2-grupos de pricing**: Estaciones+UAG ($119/$139) vs Flex ($109/$129 descuento especial).
- Actualizar naming: "Estación Plaza Patria" y "Estación Juárez".
- Agregar bloque anti-alucinación (no dar tel/email).

### 4.4 Reposición
- Actualizar naming sucursales (las 5 con naming oficial).
- Agregar bloque anti-alucinación.
- Resto del flujo (validación de imágenes, generación de código) se mantiene.

### 4.5 RRSS
- **Identidad EMMA Vivanti** desde el primer mensaje + "agente de IA" en presentación.
- Mostrar **solo precios de Estaciones+UAG** ($119/$139). NO mencionar precios de Flex Norte/Sur.
- Mencionar Flex Norte/Sur como sucursales (sin precio) — solo si el lead pregunta zona específica.
- Reemplazar links Google Maps "pendientes" por los 5 reales.
- Actualizar naming oficial.
- Agregar bloque anti-alucinación.
- Mantener regla: si zona no mapeada, ofrecer las 2 más cercanas y aclarar.

---

## §5 — Vacíos que quedan abiertos (NO bloquean v1.4)

| # | Tema | Cómo se maneja en v1.4 | Acción futura |
|---|---|---|---|
| 1 | Email general TOFO | El agente NO da email (canaliza por chat) | (no requerido — Mauricio prefiere no exponer otro canal) |
| 3 | Política cancelación B2B | "Lo conversamos en la llamada con el director" | Mauricio definirá cuando haya un caso real |
| 5 | Política devolución B2B | "Lo conversamos en la llamada con el director" | Idem |
| 4 | Garantía formal B2B (plazo, cobertura) | "El director te lo explica en la llamada — tenemos stock de refacciones en Guadalajara y soporte local" | Documentar formal cuando Mauricio defina términos legales |
| 8 | Direcciones físicas verbales | Solo links Google Maps (suficiente para "te paso ubicación") | Si algún canal no embebe links, pedirle direcciones verbales |

---

## §6 — Referencias

- [Auditoría datos fijos v1 (preguntas)](datos-fijos-auditoria-2026-06-04.md)
- [Nota WhatsApp enviada a Mauricio](preguntas-mauricio-datos-fijos-2026-06-04.md)
- [Incidente Oscar Amaya — confusión moneda](incidente-confusion-moneda-2026-06-05.md) — origen del bump B2B v1.5.
- Aplicado: 5 prompts v1.4 + B2B v1.5 (post incidente Oscar).
