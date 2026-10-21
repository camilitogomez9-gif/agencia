# F7 — Diagnóstico Rápido (resultados)

**Fecha:** 2026-06-03 13:56
**Webhook:** `https://[TU-INSTANCIA-N8N]/webhook/sys-agent`
**Modelo juez:** `gpt-4o-mini`
**Casos:** 10

## Resumen

- ✅ Pass (true):    **6** (60.0%)
- ⚠️ Parcial:        **4**
- ❌ Fail (false):   **0**
- 🔴 Error transp.:  **0**

## Detalle por caso

| # | Caso | Veredicto | Razón | Respuesta agente |
|---|------|-----------|-------|------------------|
| 01-apertura | Apertura simple — saludo + pregunta abierta sin pe | true | Cumple con el saludo y hace una pregunta abierta sin solicitar datos personales. | Hola, bienvenido a Sistemas y Soluciones.  ---  ¿En qué te puedo ayudar hoy?... |
| 02-cotizacion-directa | Regla 21 — cotización directa pide datos sin diagn | true | La respuesta del agente solicita directamente el nombre, teléfono y ubicación en | Hola, bienvenido a Sistemas y Soluciones.  ---  Para conectarte con nuestro equipo comercial y que te envíen la cotizaci... |
| 03-consultar-tecnologia | Tool consultar_tecnologia — info real de Airtable | parcial | La respuesta cubre la mayoría de los aspectos esperados, pero incluye informació | La tecnología DTF UV permite personalizar objetos rígidos e irregulares sin necesidad de meterlos en una impresora. Se i... |
| 04-tecnologia-nueva-solvente | Tool consultar_tecnologia para tecnología NUEVA (S | true | La respuesta explica adecuadamente la tecnología Solvente, menciona la necesidad | La tecnología de impresión **Solvente** utiliza tintas con solventes fuertes que penetran profundamente el sustrato, ofr... |
| 05-faq-iva-nueva | Tool consultar_faq — FAQ NUEVA sobre IVA | true | La respuesta del agente cumple con el comportamiento esperado al mencionar que l | Los precios están expresados en dólares (USD) y no incluyen IVA. La cotización final con impuestos te la pasa el equipo ... |
| 06-aplicacion-encadenada | Encadenamiento consultar_aplicacion → buscar_equip | parcial | No recomienda DTF Textil ni menciona sus características, pero solicita informac | Para recomendarte la mejor opción para estampar gorras, necesito saber sobre qué material querés trabajar. ¿Podrías darm... |
| 07-buscar-equipo-marca-real | Tool buscar_equipo con marca REAL del catálogo (HU | parcial | Menciona impresoras HUENU UV, pero no especifica modelos concretos como se esper | Sí, tenemos impresoras HUENU UV de gran formato disponibles. ¿Podrías contarme un poco más sobre el tipo de trabajo que ... |
| 08-inventario-konica-usados | Tool NUEVA consultar_inventario_usados (Konica ref | parcial | Confirma la disponibilidad de equipos usados, pero no menciona modelos específic | Sí, tenemos equipos Konica Minolta usados disponibles para producción digital láser. ¿Me pasás tu nombre, teléfono y de ... |
| 09-out-of-scope | Out of scope — clima, no responde | true | La respuesta del agente cumple con el comportamiento esperado al redirigir adecu | Eso está fuera de lo que puedo ayudarte hoy, pero si tenés consultas sobre equipos o insumos de impresión, estoy a dispo... |
| 10-memoria-2turnos | Memoria persistente — turno 2 con mismo sub_id rec | true | Cumple con el comportamiento esperado al recomendar sublimación para banderas si | Para imprimir banderas, la tecnología de sublimación es ideal, especialmente si estás trabajando con poliéster. ¿Es ese ... |

## Casos completos (mensaje + esperado + obtenido)

### 01-apertura — Apertura simple — saludo + pregunta abierta sin pedir datos

**Mensajes:**
- `Hola`

**Esperado:** Saluda como asistente de Sistemas y Soluciones. Hace UNA pregunta abierta. NO pide nombre/tel/datos. Sin frases de chatbot ('¡Perfecto!', '¡Genial!'). Tono rioplatense breve.

**Obtenido:**
```
Hola, bienvenido a Sistemas y Soluciones.

---

¿En qué te puedo ayudar hoy?
```

**Veredicto:** ✅ `true` — Cumple con el saludo y hace una pregunta abierta sin solicitar datos personales.

---

### 02-cotizacion-directa — Regla 21 — cotización directa pide datos sin diagnóstico

**Mensajes:**
- `Hola, quiero un presupuesto de una impresora DTF`

**Esperado:** NO hace diagnóstico técnico previo (no pregunta sobre volumen, sustratos, espacio físico). Pide directamente nombre + teléfono + ubicación, en una sola pregunta breve.

**Obtenido:**
```
Hola, bienvenido a Sistemas y Soluciones.

---

Para conectarte con nuestro equipo comercial y que te envíen la cotización formal, ¿me pasás tu nombre, teléfono y de dónde escribís?
```

**Veredicto:** ✅ `true` — La respuesta del agente solicita directamente el nombre, teléfono y ubicación en una sola pregunta breve.

---

### 03-consultar-tecnologia — Tool consultar_tecnologia — info real de Airtable

**Mensajes:**
- `Qué es DTF UV?`

**Esperado:** Explica DTF UV mencionando: objetos rígidos, film con tintas UV + barniz, sin calor, transferencia con presión. NO inventa información. Tono natural sin decir 'según mi base de datos'.

**Obtenido:**
```
La tecnología DTF UV permite personalizar objetos rígidos e irregulares sin necesidad de meterlos en una impresora. Se imprime en un film especial con tintas UV, barniz y pegamento, y se transfiere al objeto manualmente con presión, sin necesidad de calor.

---

Es ideal para personalizar botellas, termos, tazas, cascos, carcasas de celular, trofeos, vidrio, metal, madera y acrílico. ¿Tenés algún proyecto en mente para esta tecnología?
```

**Veredicto:** ⚠️ `parcial` — La respuesta cubre la mayoría de los aspectos esperados, pero incluye información adicional sobre aplicaciones específicas que no se solicitó.

---

### 04-tecnologia-nueva-solvente — Tool consultar_tecnologia para tecnología NUEVA (Solvente)

**Mensajes:**
- `Y Solvente regular qué es? En qué se diferencia del Eco-Solvente?`

**Esperado:** Explica Solvente como tecnología distinta del Eco-Solvente. Menciona ventilación necesaria o VOC más alto. NO confunde con Eco-Solvente. Puede hacer comparativa breve.

**Obtenido:**
```
La tecnología de impresión **Solvente** utiliza tintas con solventes fuertes que penetran profundamente el sustrato, ofreciendo alta durabilidad y resistencia exterior. Es ideal para cartelería exterior de larga duración y banners vehiculares industriales, pero requiere buena ventilación debido a las emisiones de compuestos orgánicos volátiles (VOC).

---

Por otro lado, el **Eco-Solvente** usa pigmentos en solventes biodegradables que se fijan al evaporarse con calor. Es más amigable con el medio ambiente y no tiene restricciones especiales de ventilación. Es común para rotulación exterior, vehicular y señalética.

¿Te interesa saber más sobre alguna de estas tecnologías?
```

**Veredicto:** ✅ `true` — La respuesta explica adecuadamente la tecnología Solvente, menciona la necesidad de ventilación y compara correctamente con el Eco-Solvente sin confundirlos.

---

### 05-faq-iva-nueva — Tool consultar_faq — FAQ NUEVA sobre IVA

**Mensajes:**
- `Los precios incluyen IVA?`

**Esperado:** Responde que los precios están en dólares (USD) y NO incluyen IVA. Menciona que la cotización final con impuestos la pasa el equipo comercial.

**Obtenido:**
```
Los precios están expresados en dólares (USD) y no incluyen IVA. La cotización final con impuestos te la pasa el equipo comercial.
```

**Veredicto:** ✅ `true` — La respuesta del agente cumple con el comportamiento esperado al mencionar que los precios están en dólares, no incluyen IVA y que el equipo comercial proporciona la cotización final.

---

### 06-aplicacion-encadenada — Encadenamiento consultar_aplicacion → buscar_equipo

**Mensajes:**
- `Necesito estampar gorras, qué me conviene?`

**Esperado:** Recomienda DTF Textil como tecnología. Puede mencionar características (durable, funciona en cualquier color). Pregunta volumen estimado o pasa a más info. NO inventa modelos de equipos.

**Obtenido:**
```
Para recomendarte la mejor opción para estampar gorras, necesito saber sobre qué material querés trabajar. ¿Podrías darme más detalles sobre eso?
```

**Veredicto:** ⚠️ `parcial` — No recomienda DTF Textil ni menciona sus características, pero solicita información adicional.

---

### 07-buscar-equipo-marca-real — Tool buscar_equipo con marca REAL del catálogo (HUENU)

**Mensajes:**
- `Tienen impresoras HUENU UV de gran formato?`

**Esperado:** Menciona equipos HUENU UV específicos (ej. HR 1602 UV, HR 3204 UV, HR 3208 UV). NO menciona Mimaki ni Roland. Puede ofrecer pasar a comercial para cotización.

**Obtenido:**
```
Sí, tenemos impresoras HUENU UV de gran formato disponibles. ¿Podrías contarme un poco más sobre el tipo de trabajo que planeás realizar? Así puedo asesorarte mejor sobre cuál modelo se ajusta a tus necesidades.
```

**Veredicto:** ⚠️ `parcial` — Menciona impresoras HUENU UV, pero no especifica modelos concretos como se esperaba.

---

### 08-inventario-konica-usados — Tool NUEVA consultar_inventario_usados (Konica refurbished)

**Mensajes:**
- `Tengo presupuesto bajo para producción digital láser. Tienen Konica usados?`

**Esperado:** Confirma que tienen equipos Konica refurbished (usados) disponibles en showroom PEPIRI. Menciona algún modelo específico (BIZHUB, ACCURIO) o invita a coordinar visita. NO da precios.

**Obtenido:**
```
Sí, tenemos equipos Konica Minolta usados disponibles para producción digital láser. ¿Me pasás tu nombre, teléfono y de dónde escribís para que un representante comercial pueda contactarte con más detalles?
```

**Veredicto:** ⚠️ `parcial` — Confirma la disponibilidad de equipos usados, pero no menciona modelos específicos ni invita a coordinar visita.

---

### 09-out-of-scope — Out of scope — clima, no responde

**Mensajes:**
- `Cómo está el clima en Buenos Aires hoy?`

**Esperado:** NO responde sobre clima. Redirige verbatim o similar: 'Eso está fuera de lo que puedo ayudarte hoy, pero si tenés consultas sobre equipos o insumos de impresión, estoy a disposición.'

**Obtenido:**
```
Eso está fuera de lo que puedo ayudarte hoy, pero si tenés consultas sobre equipos o insumos de impresión, estoy a disposición. ¿En qué te puedo ayudar?
```

**Veredicto:** ✅ `true` — La respuesta del agente cumple con el comportamiento esperado al redirigir adecuadamente y no mencionar el clima.

---

### 10-memoria-2turnos — Memoria persistente — turno 2 con mismo sub_id recuerda turno 1

**Mensajes:**
- `Hola, soy Mariana y tengo una imprenta en Mar del Plata`
- `Qué tecnología me conviene para banderas?`

**Esperado:** En el SEGUNDO turno, el agente trata la pregunta de banderas SIN volver a saludar y SIN pedir el nombre/ubicación de nuevo (ya los recibió). Recomienda Sublimación (tecnología para banderas) usando info real.

**Obtenido:**
```
Para imprimir banderas, la tecnología de sublimación es ideal, especialmente si estás trabajando con poliéster. ¿Es ese el material que tenés pensado usar?
```

**Veredicto:** ✅ `true` — Cumple con el comportamiento esperado al recomendar sublimación para banderas sin saludar ni pedir información adicional.

---
