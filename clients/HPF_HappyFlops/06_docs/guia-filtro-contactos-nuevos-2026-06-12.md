# Fix temporal — Filtro "solo contactos nuevos" tras caída de ManyChat

**Fecha:** 2026-06-12
**Workflow afectado:** `HPF - Main` (snapshot local: `happyflops-main-v3.json`)
**Tipo:** EDIT en vivo, reversible. **No relacionado a la migración GHL.**

---

## Contexto

ManyChat estuvo caído un período. Oscar atendió manualmente todas las conversaciones que llegaron durante la caída y nosotros pausamos al agente. Ahora queremos reactivar el agente pero que **solo responda a contactos NUEVOS** (creados después del momento de reactivación). Cualquier mensaje proveniente de un contacto pre-existente — sin importar si Oscar habló con él o no — queda fuera del agente.

**Semántica elegida:** filtrar por `data.created_at` del contacto Kommo (NO por lead/entity, NO por tag). Es la opción más conservadora: cero riesgo de pisar conversaciones humanas.

---

## EDIT en n8n — `HPF - Main`

### Paso 1 — Obtener el timestamp Unix del momento de reactivación

En el momento exacto en que vayas a reactivar el agente, abrí una terminal y corré:

```bash
date +%s
```

Eso te devuelve algo como `1749744000`. **Anotalo** — lo vas a hardcodear en el IF.

> Alternativa desde el browser console: `Math.floor(Date.now() / 1000)`.

### Paso 2 — Crear el nodo IF nuevo

1. Abrí el workflow `HPF - Main` en n8n.
2. Ubicá el nodo **`Clear_Contact_Data`** (posición aprox `[-4048, 704]`, tipo Set).
3. Agregá un nodo **IF** justo a la derecha de `Clear_Contact_Data`. Nombrelo: **`Contacto nuevo?`**
4. Configurá la condición:
   - **Type validation:** strict
   - **Combinator:** AND
   - **Condition:**
     - Left value (Number): `{{ $json.data.created_at }}`
     - Operator: **greater than** (number)
     - Right value (Number): `1749744000` ← **reemplazar por el timestamp del Paso 1**

### Paso 3 — Re-cablear conexiones

1. **Desconectar** la conexión actual `Clear_Contact_Data → All_Data`.
2. **Conectar** `Clear_Contact_Data → Contacto nuevo?` (output principal).
3. **Conectar** la rama **TRUE** de `Contacto nuevo?` → `All_Data` (sigue el flujo normal).
4. **Dejar la rama FALSE sin conectar** (los contactos viejos terminan ahí, descartados silenciosamente).

> Si preferís tracking explícito, conectá la rama FALSE a un nodo `NoOp` con nombre `Contacto pre-existente (descartado)` — ayuda a auditar en n8n executions cuántos mensajes se filtran.

### Paso 4 — Guardar y reactivar el workflow

1. Save.
2. Activar el workflow (toggle Active).
3. Marcá el momento exacto (debería coincidir con el timestamp del Paso 1 ± segundos — si hay drift de minutos, mejor actualizar el timestamp al valor real del momento de activar).

---

## Verificación

### Smoke test 1 — Contacto pre-existente (debe filtrar)
1. Buscá en Kommo un contacto creado ANTES del cutoff que tenga una conversación abierta.
2. Pedile a Oscar (o desde Kommo) que simule un mensaje entrante de ese contacto.
3. En n8n executions: la ejecución debe llegar a `Contacto nuevo?` y salir por la rama FALSE. **No debe llegar a `All_Data` ni al `AI Agent`.**

### Smoke test 2 — Contacto nuevo (debe pasar)
1. Mandá un mensaje al WhatsApp de Happy Flops desde un número que NUNCA escribió antes.
2. Kommo crea el contacto con `created_at` = ahora (> cutoff).
3. En n8n executions: el flujo pasa el IF por rama TRUE y llega al agente. La IA responde normal.

### Query de auditoría (opcional)

Si querés ver cuántos contactos pre-existentes intentaron escribir durante el período del fix, mirá en n8n el panel de ejecuciones del workflow filtrando por path `Contacto nuevo?` con output `false`.

---

## Cómo REVERTIR (cuando ya no haga falta el fix)

1. Abrí `HPF - Main`.
2. Desconectá `Clear_Contact_Data → Contacto nuevo?`.
3. Desconectá `Contacto nuevo? (TRUE) → All_Data`.
4. Reconectá `Clear_Contact_Data → All_Data` (directo).
5. Eliminá el nodo `Contacto nuevo?` (y el `NoOp` de descarte si lo creaste).
6. Save.

Volvés al comportamiento normal: todo mensaje entrante pasa por el agente.

---

## Notas

- El cutoff es **estricto mayor** (`>`), no `>=`. Si querés incluir el segundo exacto del deploy, cambialo a `>=` (irrelevante en la práctica).
- Si Oscar atiende un contacto NUEVO (creado después del cutoff) durante el período del fix y lo deja en estado humano, el agente igual va a intentar responder al próximo mensaje de ese contacto. El filtro no detecta "Oscar tomó esta conversación" — solo "el contacto es viejo". Para ese caso borde, usar pausa manual en Kommo / Kommo bot.
- El `responsible_user_id` del lead **NO** se usa en este filtro. El filtro existente `No es IA` (que excluye al user `11622596` = el bot mismo) sigue funcionando aparte y es complementario.
