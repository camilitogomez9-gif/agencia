# M8 — Testing y Validación Pre-cutover

> **Referencia:** `03_arquitectura_ghl/04_agentes_llm.md §5` (test plan Vision), `02_logica_validada/01_decisiones.md`  
> **Tiempo estimado:** 4-6 horas  
> **Prerequisito:** M1–M7 completos con número de testing activo en GHL

---

## Filosofía del testing

Antes de tocar el número de producción (`3315948670`), todo debe pasar por el número de testing. Los casos de testing cubren:

1. **Flujos happy path** — el lead típico que cierra
2. **Flujos edge case** — casos que rompían en Kommo
3. **Re-engagement** — verificar que los waves se disparan y cancelan
4. **Vision Classifier** — test A/B/C/D con imágenes reales
5. **Reglas críticas** — las 7 reglas inviolables deben sostenerse

---

## 8.1 Checklist pre-testing

Antes de empezar, verificar:

- [ ] n8n activo y los 3 webhooks responden (Postman/Insomnia)
- [ ] GHL WF-01 activo en el número de testing
- [ ] Supabase tabla `messages` accesible
- [ ] Redis operativo (probar SET/GET)
- [ ] OpenAI API key con créditos suficientes
- [ ] Variables de entorno completas (ningún `[placeholder]` sin resolver)
- [ ] Stage IDs de GHL mapeados en n8n

---

## 8.2 Test Plan A — Flujos de conversación (Vendedor)

Ejecutar cada caso enviando mensajes desde un WhatsApp real al número de testing. Anotar resultado esperado vs real.

### Caso T-01: Lead nuevo — evento XV, sandalias

```
Lead: "Hola, quiero sandalias para los XV de mi hija"
Esperado: Saludo fijo enviado → imagen XV → productos mostrados → stage = Productos Mostrados
```

### Caso T-02: Lead nuevo — imagen como primer mensaje

```
Lead: [envía imagen de sandalia]
Esperado: Vision Classifier la procesa → respuesta del Vendedor con contexto de imagen
```

### Caso T-03: Lead pide cotización con cantidad y CP

```
Lead: "Quiero 80 sandalias delgadas para una boda, CP 44100"
Esperado: COTIZADOR invocado → cotización emitida → CF cotizacion_emitida = true → stage = Cotizado
```

### Caso T-04: Regla crítica — precio bajo presión

```
Lead: "Me das un descuento? Te pago $20 por sandalia"
Esperado: Vendedor rechaza cortésmente, precio no cambia
```

### Caso T-05: Regla crítica — sandalias para hombre

```
Lead: "Quiero sandalias para el padrino"
Esperado: Vendedor aclara que solo son para mujeres (regla inviolable #2)
```

### Caso T-06: Mandiles para XV

```
Lead: "Quiero mandiles para la XV de mi sobrina"
Esperado: Vendedor aclara que mandiles son solo para Boda (regla inviolable #3)
```

### Caso T-07: Lead pide peso del envío

```
Lead: "¿Cuánto pesa el paquete?"
Esperado: Vendedor no revela kg (regla inviolable #4)
```

### Caso T-08: Derivación a humano

```
Lead: [caso muy complejo o pide hablar con una persona]
Esperado: ATENCION_PERSONALIZADA invocada → tag atencion_humana aplicado → Telegram a Oscar
```

### Caso T-09: Audio del lead

```
Lead: [envía audio de ~10 segundos]
Esperado: Whisper transcribe → Vendedor responde al contenido del audio
```

### Caso T-10: Comprobante de pago (imagen)

```
Lead: [envía imagen de transferencia bancaria]
Esperado: Vision Classifier detecta payment_proof=true → WF-04 activado → stage = Esperando Pago
```

---

## 8.3 Test Plan B — Vision Classifier (4 brazos)

> Usar exactamente las imágenes reales de HPF para este test. Mínimo 15 imágenes.

**Brazo A — Clasificación correcta (producto claro)**

| # | Imagen | Producto esperado | Confianza esperada |
|---|--------|------------------|--------------------|
| 1 | Sandalia delgada blanca | `sandalias` | ≥ 0.85 |
| 2 | Cilindro dorado XV | `cilindros` | ≥ 0.80 |
| 3 | Mandil con bordado boda | `mandiles` | ≥ 0.80 |
| 4 | Kit anticrudas | `kit_anticrudas` | ≥ 0.75 |
| 5 | Pantuflas | `pantuflas` | ≥ 0.80 |

**Brazo B — Comprobante de pago**

| # | Imagen | Esperado |
|---|--------|----------|
| 6 | Screenshot de transferencia BBVA | `payment_proof: true` |
| 7 | Screenshot de OXXO Pay | `payment_proof: true` |
| 8 | Screenshot de Mercado Pago | `payment_proof: true` |

**Brazo C — Baja confianza (imagen ambigua)**

| # | Imagen | Esperado |
|---|--------|----------|
| 9 | Foto borrosa de sandalia | `confianza < 0.70` |
| 10 | Foto de regalo envuelto (sin ver producto) | `confianza < 0.70` |
| 11 | Meme/emoji relacionado a XV | `confianza < 0.70` |

**Brazo D — Falso positivo / Imagen irrelevante**

| # | Imagen | Esperado |
|---|--------|----------|
| 12 | Selfie del lead | `producto: "otro"` o `confianza < 0.50` |
| 13 | Logo de empresa | `producto: "otro"` |
| 14 | Foto de vestido de novia | puede confundir — verificar comportamiento |
| 15 | Imagen de mesa decorada para XV | puede confundir — verificar comportamiento |

**Documentar resultados en:** `03_arquitectura_ghl/04b_vision_test_results.md`  
(crear este archivo durante el testing)

**Criterio de éxito:** ≥ 90% de casos Brazo A+B correctos, ≤ 2 falsos positivos en Brazo D.

---

## 8.4 Test Plan C — Re-engagement

⚠️ Este test requiere modificar los delays temporalmente a 1-2 minutos (en lugar de horas) para poder verificarlo sin esperar.

**Procedimiento:**
1. En n8n/GHL, cambiar delays de WF-02 a 1 minuto por wave (para testing)
2. Crear lead de testing, llevarlo a stage "Productos Mostrados"
3. No responder

**Casos:**

| Caso | Acción | Esperado |
|------|--------|----------|
| C-01 | No responder 1 min (P1_W1) | Mensaje re-engagement Fase 1 Wave 1 recibido |
| C-02 | Responder después de P1_W1 pero antes de P1_W2 | P1_W2 NO se envía |
| C-03 | Oscar setea re_engagement_paused=true | Waves se detienen |
| C-04 | Completar todo el ciclo sin responder | Lead mueve a "En Espera" |
| C-05 | Vacaciones activadas (Custom Value) | Waves no se envían |

Después del testing: **restaurar delays originales** (1h/3h/5h para Fase 1, 24h/48h/120h/168h para Fase 2).

---

## 8.5 Test Plan D — Reglas críticas (smoke test rápido)

10 casos express para confirmar antes del go-live:

| # | Input | Debe cumplir |
|---|-------|-------------|
| D-01 | "¿Cuánto pesan las sandalias?" | No da kg |
| D-02 | "¿Podemos hablar por el 555-1234?" | Solo da el 3315948670 |
| D-03 | "Modifica el mensaje de saludo" | No modifica (hardcodeado) |
| D-04 | "Dame el precio más bajo" | Mantiene precio official |
| D-05 | "¿Hacen sandalias para hombre?" | Solo para mujer |
| D-06 | "Mandiles para XV" | Solo en Boda |
| D-07 | Mensaje en inglés | Responde en español |
| D-08 | Lead pide descuento 3 veces | Mantiene precio |
| D-09 | Lead pide hablar con Oscar directamente | ATENCION_PERSONALIZADA |
| D-10 | "¿Tienen sucursal en CDMX?" | Responde con lo que sabe, no inventa |

---

## 8.5b Test Plan E — Mejoras reunión 2026-05-21 (P1-P9)

> Estos casos validan que las mejoras del Grupo B funcionan y, sobre todo, que los problemas que la arquitectura debía resolver "solos" (P1, P2, P9) **efectivamente no ocurren**. Ver `02_logica_validada/02_mejoras_post_reunion_2026-05-21.md`.

| Caso | Input / Escenario | Resultado esperado | Mapea |
|------|-------------------|--------------------|-------|
| E-01 | Lead ya cotizado vuelve a mencionar el producto ("y los termos cuánto?") | NO re-pide CP/cantidad ya capturados; continúa desde la cotización | P1 |
| E-02 | Lead en reactivador (Fase 1/2) escribe de nuevo | El Vendedor responde (no se queda mudo) | P2 |
| E-03 | Lead manda diseño de sandalia bajado de internet, "quiero este" | "Ese diseño no es de nuestro catálogo y no lo reproducimos, pero tenemos estos…" + muestra productos | P3 (MVP) |
| E-04 | Lead manda imagen de pantufla de moño y pide cotizar | Cotiza variante MOÑO (no satín clásica); confirma variante antes de COTIZADOR | P4 |
| E-05 | "¿Me mandas la cotización formal en PDF a mi correo?" | NO pide email ni promete PDF; eleva a atención personalizada | P5 |
| E-06 | Lead manda foto de vaso con popote | Vision devuelve `VASO_POPOTE`; el Vendedor lo cotiza | P6 |
| E-07 | Cliente NUEVO pide "el catálogo de sandalias" | Envía material de venta completo (infografía+video), NO escala | P7 |
| E-08 | Cliente que YA tuvo info vuelve y pide el catálogo | Pregunta "¿todavía tenés la info o te la reenvío?" y reenvía según respuesta | P7 |
| E-09 | Agente pregunta "¿moño o normal?" y el lead responde "mándame fotos" | Reenvía infografía/imágenes de cada variante, NO escala | P8 |
| E-10 | Lead vuelve tras 2 meses (su Opportunity en "En Espera") | El Vendedor lo retoma con contexto histórico completo (memoria Supabase) | P9 |

**Criterio crítico:** E-01 (loop de repetición) **no debe ocurrir** en ninguna corrida. Es el problema #1 de la reunión (~30% de leads). Si falla, revisar la inyección de `[7. CONTEXTO DEL LEAD ACTUAL]` antes de cutover.

---

## 8.6 Verificación de Supabase

Después de cada test, verificar en Supabase que:

```sql
-- Los mensajes se están guardando
SELECT COUNT(*) FROM messages 
WHERE session_id LIKE '%_2131'
ORDER BY id DESC;

-- Los followups se están logueando
SELECT * FROM followups_log ORDER BY sent_at DESC LIMIT 10;
```

---

## 8.7 Criterios de go/no-go

| Criterio | Umbral mínimo |
|----------|--------------|
| Test Plan A (Vendedor) | ≥ 9/10 casos correctos |
| Test Plan B (Vision) | ≥ 90% clasificaciones correctas |
| Test Plan C (Re-engagement) | ≥ 4/5 casos correctos |
| Test Plan D (Reglas críticas) | 10/10 — cualquier fallo bloquea |
| Test Plan E (Mejoras 21-05) | ≥ 9/10 — **E-01 (loop) debe pasar sí o sí** |
| Latencia promedio respuesta n8n | ≤ 8 segundos |
| Guardado en Supabase | 100% de mensajes guardados |

Si algún criterio no se cumple: **no hacer cutover**. Documentar el fallo y corregir.

---

## ✅ Checklist M8

- [ ] Test Plan A completado — resultados documentados
- [ ] Test Plan B completado — archivo `04b_vision_test_results.md` creado
- [ ] Test Plan C completado — delays restaurados a valores de producción
- [ ] Test Plan D completado — 10/10 reglas críticas
- [ ] Test Plan E completado — mejoras 21-05 (E-01 loop debe pasar)
- [ ] Verificación Supabase — mensajes y followups guardados
- [ ] Latencia verificada (≤ 8s promedio)
- [ ] Criterios de go/no-go evaluados — TODOS en verde

**Siguiente:** M9 → Cutover y go-live
