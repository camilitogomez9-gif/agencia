# Guía — Fix mínimo de compra no respetado (caso Cilindros 35/40)

**Fecha:** 2026-07-15
**Disparador:** Oscar reportó en el grupo que el agente le cotizó 35 Cilindros a un lead, cuando el mínimo de compra real es 40 piezas.
**Alcance:** premigración (Kommo + n8n). No toca nada de `00_migracion_ghl/` — esos documentos son para la migración futura a GHL, todavía no aplican en producción.

---

## 1. Diagnóstico

### Causa raíz confirmada (alta confianza)

El mínimo de compra de Cilindros (40 piezas) **está correctamente documentado** en el system prompt vigente (dos veces: sección "Restricciones de cotización" y sección "Notas Adicionales"), así que no es un error de dato. El problema es de **arquitectura de control**:

- La única capa que verifica los mínimos de compra es el LLM leyendo instrucciones de un prompt de **~840 líneas** con decenas de reglas compitiendo (tono, formato de cotización, upsell, mandiles, pantuflas, precios, género de sandalias, etc.).
- La tool `CALCULADORA` (sub-workflow `HPF - Calculadora`, nodo `Code1`) **nunca validó mínimos de compra** — su única función es calcular peso/cajas/costo de envío respetando los límites de *empaque* (250 cilindros máx. por caja, 200 sandalias máx., 35 kg máx.). Si se le pide calcular el envío de 35 Cilindros, la tool devuelve un `costo_total_envio` perfectamente válido, sin ninguna señal de que la cantidad no alcanza el mínimo real.
- Es decir: **no había ninguna red de seguridad determinística**. Si el LLM se distraía o priorizaba mal (por ejemplo la instrucción de "ahorrar preguntas" y "ser breve"), nada en el sistema lo frenaba — el cálculo de envío "se veía bien" y reforzaba la ilusión de que todo estaba correcto.
- A diferencia de otras reglas críticas del negocio (Mandiles, Pantuflas, Precios, Género de sandalias), la regla de mínimos **nunca recibió el tratamiento de "REGLA CRÍTICA"** (bloque dedicado, con checklist explícito) — vivía como una línea más dentro de una lista larga de "Restricciones de cotización". Esto la hacía más fácil de saltear en una conversación larga.

### Hallazgo adicional (drift repo vs. producción — requiere verificación manual)

Al comparar el prompt embebido en `03_workflows/happyflops-main-v3.json` (nodo `AI Agent Recolector`) contra el archivo vigente `04_agents/agente-happyflops-recolector-system-prompt.md`, encontramos que **el JSON en el repo tiene una versión vieja de la sección CALCULADORA** — la de antes del rediseño a formato `items` con nombres de producto (el que documenta `06_docs/delta-fix-calculadora-v1.3-2026-05-30.md`). El propio CLAUDE.md ya tenía este pendiente anotado ("Aplicar EDIT v1.3 en AI Agent Recolector... re-correr Caso C+D+A") sin marcar como confirmado.

**Esto importa porque:** si el prompt realmente vigente en n8n todavía instruye usar el formato legacy `cuentas` (multiplicaciones sin nombre de producto, ej. `"35 x 0.14"`), la tool **nunca tuvo forma de saber que ese pedido era de Cilindros** — ni para límites de empaque ni (ahora) para el chequeo de mínimos, que solo puede aplicarse cuando se manda el nombre del producto. No podemos confirmar con certeza cuál versión está pegada ahora mismo en el nodo AI Agent (no tenemos acceso directo al n8n vivo en esta sesión) — **ver Paso 0 más abajo antes de desplegar nada**.

---

## 2. Fix aplicado (en repo, pendiente deploy)

Se aplicó un fix de **doble capa** (defensa en profundidad — no confiar en una sola barrera):

### Capa 1 — Prompt endurecido
`04_agents/agente-happyflops-recolector-system-prompt.md` (backup de la versión anterior guardado como `-v1.5.md`):

1. Nueva sección **"REGLA CRÍTICA — Mínimos de compra"** (mismo tratamiento que ya tienen Mandiles/Pantuflas/Precios/Género): tabla resumen de mínimos + checklist obligatorio antes de invocar CALCULADORA + aclaración de que la eficiencia/brevedad NUNCA está por encima de este chequeo.
2. Paso 4 nuevo en la descripción de la tool CALCULADORA: verificar mínimos antes de llamar a la tool, y qué hacer si la tool rechaza el cálculo.
3. Aclaración en las dos menciones de "Sólo le recuerdas el mínimo cuando piden por debajo" — para que quede explícito que esa instrucción es sobre el tono de la conversación, NO una excusa para saltear la verificación interna.

### Capa 2 — Validación determinística en la tool (red de seguridad real)
`03_workflows/happyflops-calculadora-v2.json` (nueva versión del sub-workflow `HPF - Calculadora`, **preserva el workflowId `OPiuPFwRmq6QgACL`** — importar sobreescribe in-place, no rompe las referencias del main):

- Nodo `Code1` ahora valida cada producto del formato `items` contra una tabla de mínimos (`Sandalias Delgadas/Gruesas`: 50, `Pantuflas` y variantes: 50, `Cilindros`: 40, `Vaso Popote`: 50, `Kits Anticrudas`/`Costales`: 35, `Mandiles`: 12).
- Si algún producto no alcanza su mínimo, la tool **rechaza el cálculo completo** y devuelve `{ error: "MINIMO_NO_ALCANZADO", detalle_violaciones: [...], message_to_agent: "..." }` en vez de un `costo_total_envio` — el LLM ya no puede completar la cotización aunque se salte el chequeo del prompt.
- El formato legacy `cuentas` (sin nombre de producto) **sigue funcionando sin romperse** — no podía validarse por falta de identidad de producto, así que en vez de bloquearlo se le agregó un campo `advertencia_minimos` explícito en la respuesta, avisando que ese cálculo no verificó mínimos. Esto evita que un despliegue con el prompt viejo (formato `cuentas`) deje de funcionar de golpe, pero deja visible el hueco para que se cierre migrando a `items`.

**Validado con 6 casos de prueba en Node.js** (extraídos y ejecutados fuera de n8n, ver `/tmp/harness.js` de esta sesión — no versionado):
- 35 Cilindros solos → rechazado ✅
- 40 Cilindros (límite exacto) → aceptado, cotiza normal ✅
- 50 Sandalias Gruesas + 35 Cilindros → rechazado, señala solo Cilindros como violación ✅
- 20 Kits Anticrudas (mín. 35) → rechazado ✅
- 80 Cilindros + 50 Pantufla Moño Satín (ejemplo del propio prompt) → aceptado, cotiza igual que antes ✅
- Formato legacy `cuentas: "35 x 0.14"` → sigue calculando, pero ahora con `advertencia_minimos` ✅

---

## 3. Pasos para desplegar en producción (Kommo/n8n)

### Paso 0 — Verificar qué está vivo ahora mismo (obligatorio antes de tocar nada)

1. Abrí el workflow main de HPF en n8n (el que contiene el nodo `AI Agent Recolector` en la posición ~[4160,1344]).
2. Abrí ese nodo y mirá el campo **System Message**.
3. Buscá la sección `# Tools` → `CALCULADORA`. Si ves texto que menciona la variable `"cuentas"` como la ÚNICA forma de llamar a la tool (sin mención de `items` ni de nombres canónicos de producto), el prompt vivo está desactualizado respecto al repo — anotalo, porque cambia el orden de despliegue (ver nota abajo).
4. Si ya ves el formato `items` con nombres canónicos (`Cilindros`, `Sandalias Delgadas`, etc.), el prompt vivo ya está alineado — podés saltar directo al Paso 2.

### Paso 1 — Actualizar el System Message del nodo `AI Agent Recolector` (solo si el Paso 0 detectó el formato viejo)

Reemplazá manualmente en el System Message del nodo (no reimportar el JSON completo del main — es un workflow de 236 nodos y un reimport completo puede pisar otros ajustes manuales hechos directo en n8n):

1. Pegá el contenido completo y actualizado de `04_agents/agente-happyflops-recolector-system-prompt.md` (reemplaza todo el System Message actual).
2. Confirmá que la sección `# Tools` → `CALCULADORA` ahora describe el formato `items` como preferido.
3. Confirmá que aparece la nueva sección `# REGLA CRÍTICA — Mínimos de compra`.

Si el Paso 0 ya mostró que el prompt vivo coincide con el repo, este paso ya está hecho — solo falta pegar el delta de esta sesión (la sección de mínimos + el paso 4 de la tool + las 2 aclaraciones), que podés ubicar buscando "REGLA CRÍTICA — Mínimos de compra" en el .md actualizado.

### Paso 2 — Importar el sub-workflow `HPF - Calculadora` v2

1. En n8n, abrí el workflow `HPF - Calculadora` (id `OPiuPFwRmq6QgACL`).
2. Importá `03_workflows/happyflops-calculadora-v2.json` — como preserva el mismo workflowId, el import sobreescribe in-place y el main (`CALCULADORA` toolWorkflow node) sigue apuntando correctamente sin cambios adicionales.
3. Activá el workflow si no lo estaba ya (`active` en el JSON queda en `false` por default de n8n al exportar, pero el sub-workflow se ejecuta igual como tool aunque no esté "activo" — confirmalo en la UI si tenés dudas).

### Paso 3 — Smoke test en Kommo/Telegram de testing

Probar como mínimo estos 3 casos conversacionales:

1. **Caso rechazo simple:** pedir "35 cilindros para una boda, CP 44100" → el agente debe avisar que el mínimo de Cilindros es 40 y NO debe presentar una cotización con 35.
2. **Caso al límite:** pedir "40 cilindros para una boda, CP 44100" → el agente debe cotizar normalmente.
3. **Caso mixto:** pedir "50 sandalias gruesas y 20 kits anticrudas" → el agente debe cotizar sandalias OK pero avisar que kits anticrudas necesita mínimo 35 antes de incluirlo.

Si en cualquiera de estos casos el agente **no llama a la tool en absoluto** (la resuelve solo con el prompt) y da la respuesta correcta, está bien — la Capa 1 (prompt) ya lo resolvió sin necesidad de la Capa 2. Lo importante es que en ningún caso termine cotizando por debajo del mínimo.

---

## 4. Rollback

- Prompt: restaurar `agente-happyflops-recolector-system-prompt-v1.5.md` en el System Message del nodo.
- Calculadora: reimportar `happyflops-calculadora-v1.json` (mismo workflowId, sobreescribe in-place).

---

## 5. Pendiente / fuera de alcance de este fix

- **Confirmar con Oscar** si "Costales" es realmente el mismo producto que "Kits Anticrudas" (el prompt dice que sí son sinónimos, pero la tool los trata como nombres canónicos distintos desde el rediseño v1.3 — ambos quedaron con mínimo 35 en este fix, de forma conservadora, pero valdría la pena unificarlos para evitar futuras inconsistencias).
- **Confirmar qué versión del System Message está realmente vigente en n8n ahora mismo** (Paso 0) y, si corresponde, re-exportar el main workflow completo a `happyflops-main-v4.json` para que el repo deje de estar desincronizado de producción — no se hizo en esta sesión porque reimportar/reexportar el main completo (236 nodos) sin acceso directo al n8n vivo es riesgoso de hacer a ciegas.
