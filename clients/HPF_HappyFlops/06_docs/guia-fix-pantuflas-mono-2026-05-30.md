# Guía de implementación — Refuerzo disambiguación Pantufla Mono Satín/Peluche

**Fecha:** 2026-05-30
**Cliente:** Happy Flops (HPF)
**Disparador:** Oscar reporta (audio 2026-05-30 14:11) que cuando el cliente menciona "pantufla de moño" sin material, el agente está cotizando como peluche por defecto en vez de preguntar.
**Diagnóstico:** la regla ya existía en producción (línea de Pantuflas en Instrucciones Finales) pero el agente no la cumplía. Causa raíz probable: el catálogo "Productos y Precios" tenía un único valor "Pantuflas Mono: $35" (sin distinguir material), lo que hacía que el LLM asumiera material implícito. Además, la regla competía con la instrucción de Tono "Prioriza la eficiencia ahorrando la máxima cantidad de preguntas".
**Tipo de cambio:** EDIT en vivo sobre nodo de producción.
**Versión prompt resultante:** v1.1

---

## 1. Resumen

Tres ediciones sobre el `AI Agent Recolector`:

| # | Dónde | Qué |
|---|-------|-----|
| 1 | `Productos y Precios` | Desglosar "Pantuflas Mono: $35" en dos líneas: Mono Satín $30 y Mono Peluche $35. Elimina la ambigüedad estructural que llevaba al default a peluche. |
| 2 | `Instrucciones Finales` (línea de Pantuflas) | Reforzar la regla existente con ⚠️ + anti-patrones explícitos + override sobre la instrucción de eficiencia. |
| 3 | Final del prompt (después de "Género de las sandalias") | Nueva REGLA CRÍTICA con árbol de decisión, prohibiciones, caso especial multi-producto, y check operativo de 3 pasos. |

---

## 2. Dónde aplicar el cambio

- **Workflow n8n:** `happyflops-main-v2` (producción)
- **Nodo:** `AI Agent Recolector` (`@n8n/n8n-nodes-langchain.agent`)
- **Campo:** `Options` → `System Message`

---

## 3. EDIT 1 — Fix de precios en `Productos y Precios`

### Buscar (texto literal):

```
- Pantuflas: $30
- Pantuflas Mono: $35
- Vasos popote: $35
```

### Reemplazar por:

```
- Pantuflas: $30
- Pantuflas Mono Satín: $30
- Pantuflas Mono Peluche: $35
- Vasos popote: $35
```

> ⚠️ Confirmar con Oscar antes de aplicar: los Ejemplos 8, 9, 11 del prompt ya usaban estos precios ($30 satín, $35 peluche). Si Oscar dice que en realidad ambas variantes valen $35, revertir esta línea a "Pantuflas Mono: $35" y corregir el Ejemplo 8.

---

## 4. EDIT 2 — Reforzar la regla de Pantuflas en `Instrucciones Finales`

### Buscar (texto literal):

```
- Pantuflas: Si el cliente menciona “pantuflas”, “pantuflas de moño” o “pantuflas mono”, debes aclarar exactamente a cuál producto se refiere antes de cotizar. Primero confirma si quiere pantuflas normales o pantuflas mono. Si quiere pantuflas mono, debes preguntar si las quiere de satín o de peluche. No cotices ni asumas el producto hasta que esa distinción quede clara.
```

### Reemplazar por:

```
- ⚠️ Pantuflas (REGLA OBLIGATORIA, no aplica la "eficiencia ahorrando preguntas"): Si el cliente menciona "pantuflas", "pantufla", "pantufla de moño", "pantufla con moño", "pantuflas mono", "moñito" o cualquier sinónimo SIN especificar el modelo Y el material, DEBES aclarar ANTES de cotizar y ANTES de activar CALCULADORA. Hay un árbol de 2 niveles: (1) modelo: ¿pantuflas normales o pantuflas mono? — (2) si dijo mono: ¿satín o peluche? JAMÁS asumas un modelo ni un material por defecto, JAMÁS defaultees a peluche, JAMÁS unifiques pantuflas normales y pantuflas mono en una misma línea de cotización. Si el cliente especifica ambas dimensiones en un solo mensaje (ej: "pantufla mono satín"), cotizá directamente sin re-preguntar. Esta regla aplica incluso si el cliente ya envió cantidad + código postal junto con el pedido.
```

---

## 5. EDIT 3 — Nueva REGLA CRÍTICA al final del prompt

### Buscar (las últimas líneas del system message):

```
# REGLA CRÍTICA — Género de las sandalias
Las sandalias son exclusivamente para MUJERES. No se producen sandalias para varones bajo ninguna circunstancia. Jamás menciones ni insinúes que hay sandalias para hombres. Si un cliente pregunta por sandalias para hombre, aclara amablemente que solo se fabrican para mujeres.
```

### Reemplazar por:

```
# REGLA CRÍTICA — Género de las sandalias
Las sandalias son exclusivamente para MUJERES. No se producen sandalias para varones bajo ninguna circunstancia. Jamás menciones ni insinúes que hay sandalias para hombres. Si un cliente pregunta por sandalias para hombre, aclara amablemente que solo se fabrican para mujeres.


# REGLA CRÍTICA — Material y modelo de las pantuflas

Existen TRES productos distintos de pantuflas, con precios distintos:
- **Pantuflas** (normales) — $30
- **Pantuflas Mono Satín** — $30
- **Pantuflas Mono Peluche** — $35

Si el cliente menciona pantuflas y NO especifica modelo + material, debes preguntar SIEMPRE antes de cotizar y antes de activar CALCULADORA. La pregunta exacta a usar:

- Si dijo solo "pantuflas" / "pantufla": "¿Las prefiere pantuflas normales o pantuflas mono (con moñito)? 😊"
- Si dijo "pantufla mono", "pantufla con moño", "pantufla de moño", "moño" o "moñito": "¿Las prefiere con moño de peluche o con moño de satín? 😊"

Esta regla está por encima de la instrucción de Tono ("Prioriza la eficiencia ahorrando la máxima cantidad de preguntas") porque cotizar el modelo o material incorrecto genera pérdidas y disputas con clientes.

Está PROHIBIDO:
- Asumir un modelo o material por defecto.
- Defaultear a peluche cuando el cliente solo dijo "moño" (este era el comportamiento erróneo previo reportado por Oscar).
- Unificar pantuflas normales y pantuflas mono en una misma línea de cotización.
- Cotizar pantuflas si todavía no tenés modelo + material confirmados, AUNQUE el cliente ya haya enviado la cantidad y el código postal en el mismo mensaje.
- Activar la tool CALCULADORA antes de tener modelo + material confirmados.

Caso especial — cliente pide múltiples variantes en un mismo mensaje (ej: "50 pantufla satin + 50 pantufla de moño de satin"):
Tratá cada variante como un producto distinto, con su propia línea, su precio y su cantidad. NO los unifiques aunque suenen parecido. Si una de las variantes tiene ambigüedad de modelo/material, preguntá solo por esa antes de cotizar.

Excepción (cotizá directamente sin re-preguntar): si el cliente ya especificó modelo + material en un solo mensaje, ejemplos:
- "pantufla mono satín" → ya dijo modelo (mono) + material (satín)
- "pantufla con moño de peluche" → ya dijo modelo (mono) + material (peluche)
- "pantufla normal" → ya dijo modelo (normal), no aplica material
- "pantuflas" + (en mensaje aparte) "satín" → ya tenés ambas dimensiones aclaradas

Recordatorio Operativo: antes de cualquier cotización de pantuflas, hacer este check mental:
1. ¿Tengo confirmado el modelo (normal vs mono)? Si NO → preguntar y NO cotizar.
2. Si es mono, ¿tengo confirmado el material (satín vs peluche)? Si NO → preguntar y NO cotizar.
3. Solo si ambas dimensiones están confirmadas → activar CALCULADORA y cotizar.
```

---

## 6. Pasos en n8n (UI)

1. Abrir el workflow `happyflops-main-v2` en producción.
2. Click sobre el nodo **AI Agent Recolector**.
3. Sección **Options** → desplegar **System Message**.
4. Hacer **EDIT 1** (precios) → **EDIT 2** (regla reforzada) → **EDIT 3** (REGLA CRÍTICA al final).
5. **Save** del nodo.
6. **Save** del workflow.

> No hace falta deshabilitar/rehabilitar — el cambio toma efecto en la próxima ejecución.

---

## 7. Verificación post-deploy

Probar con un mensaje de prueba en Kommo (o canal de pruebas):

### Caso A — solo dice "pantuflas", agente debe pedir modelo
```
Usuario: Quiero 50 pantuflas para boda, CP 44100
Esperado: Rebeca pregunta "¿Las prefiere pantuflas normales o pantuflas mono (con moñito)? 😊"
NO debe: cotizar como Pantuflas, Pantuflas Mono ni asumir nada
```

### Caso B — dice "pantufla de moño" sin material → pedir material
```
Usuario: Quiero 50 pantuflas de moño, CP 44100
Esperado: Rebeca pregunta "¿Las prefiere con moño de peluche o con moño de satín? 😊"
NO debe: defaultear a peluche (este es exactamente el bug que reporta Oscar)
```

### Caso C — material ya especificado → cotiza directo (al precio correcto)
```
Usuario: Quiero 50 pantuflas mono satín para XV, CP 44100
Esperado: cotiza directamente como "50 Pantuflas Mono Satín × $30 = $1,500"
NO debe: re-preguntar el material, ni cotizar a $35
```

### Caso D — múltiples productos en un mensaje (regresión del caso del 2026-05-29)
```
Usuario: Quiero 50 pantufla satin personalizadas, con bolsa personalizada.
        También quiero 50 pantufla de moño de satin. CP 88993.

Esperado: Rebeca aclara primero el modelo de la primera ("pantufla satín" no especifica si es normal o mono — preguntar).
Tras aclaración, cotiza DOS líneas distintas:
  - 50 [Pantuflas (normales) o Pantuflas Mono Satín, según lo aclarado] × $30 = $1,500
  - 50 Pantuflas Mono Satín × $30 = $1,500
NO debe: unificarlas en una sola línea ni asumir el modelo de la primera.
```

### Caso E — caso "normal" + cotización directa
```
Usuario: Quiero 50 pantuflas normales para boda, CP 44100
Esperado: cotiza como "50 Pantuflas × $30" sin preguntar (ya especificó modelo, material no aplica)
```

---

## 8. Versionado

- `clients/HPF_HappyFlops/04_agents/agente-happyflops-recolector-system-prompt-v1.0.md` — baseline real de producción (al 2026-05-30, previo al fix).
- `clients/HPF_HappyFlops/04_agents/agente-happyflops-recolector-system-prompt.md` — v1.1 con los 3 refuerzos.

Si querés mostrarle a Oscar el prompt nuevo entero, mandá el archivo `agente-happyflops-recolector-system-prompt.md`.

---

## 9. Notas para la migración a GHL

El árbol de decisión (modelo → material) y la regla crítica deben trasladarse al system prompt del bot equivalente en GHL cuando se ejecute la migración (`clients/HPF_HappyFlops/00_migracion_ghl/`). El catálogo de Pantuflas Mono Satín ($30) vs Pantuflas Mono Peluche ($35) también debe quedar reflejado en el catálogo de productos de GHL.

---

## 10. Confirmaciones pendientes con Oscar (antes de aplicar)

1. **Precio de Pantufla Mono Satín**: el Ejemplo 8 del prompt actual cotiza a $30, pero el catálogo "Productos y Precios" dice "$35 Pantuflas Mono" (sin distinguir). Esta guía asume **$30 Mono Satín / $35 Mono Peluche** (alineado al Ejemplo 8). Si esto es incorrecto, revertir el EDIT 1 y corregir el Ejemplo 8.
2. **Pantufla satín (sin moño)**: ¿existe como producto separado, o "satín" solo aplica al modelo Mono? Si la respuesta es "satín solo aplica a Mono", aclarar al cliente en el Caso D que "pantufla satin" significa "Pantufla Mono Satín" implícitamente. Esta guía asume que es ambiguo y el agente debe preguntar.
