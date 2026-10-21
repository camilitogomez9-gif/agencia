# Guía verificación n8n — Asignación automática de fallas a Miguel

**Fecha:** 2026-06-03 (actualizada con snapshot de producción capturado el mismo día)
**Workflow:** `Elevar conversación | Tofo` (ID `yJA04Pfyk2Id1aMo`)
**Estado:** ✅ **ya cableado en producción.** Esta guía es de **auditoría + pendientes operativos**, no de edits estructurales.

---

## Estado actual del workflow en producción (verificado 2026-06-03)

Snapshot oficial: [`03_workflows/elevar-conversacion-tofo-prod-snapshot-2026-06-03.json`](../03_workflows/elevar-conversacion-tofo-prod-snapshot-2026-06-03.json) — captura del workflow vivo, no un diseño.

**Topología verificada:**

```
When Executed by Another Workflow (id_manychat, resumen, tipo)
         │
         ▼
   Elegir persona (Switch v3.3, fallbackOutput=extra)
   ┌──────────────┬──────────────┬─────────────────────┐
   │ output 0     │ output 1     │ output 2 (fallback) │
   │ tipo='repo'  │ tipo='b2b'   │ resto               │
   ▼              ▼              ▼
Mensaje a       Mensaje a      Mensaje a
Miguel          Mauricio       Mauricio (mismo nodo
(Telegram                       que output 1)
8067142805)     (Telegram
                5839874323)
   │              │                │
   ▼              ▼                ▼
Elevar Miguel  Elevar a       Elevar a
(HTTP sendFlow Mauricio       Mauricio
flow_ns        (HTTP sendFlow (mismo nodo
content2025... flow_ns        que output 1)
658273)        content2026...
               613819)
```

**Estados confirmados:**
- ✅ Workflow `active: true`
- ✅ Nodo HTTP `Elevar Miguel` con flow_ns `content20251129220130_658273`
- ✅ Nodo HTTP `Elevar a Mauricio` con flow_ns `content20260526142445_613819`
- ✅ Switch con 3 outputs cableados (Reposición/B2B/extra-fallback)
- ✅ Telegram a Miguel (chatId `8067142805`) en rama `repo`
- ✅ Telegram a Mauricio (chatId `5839874323`) en ramas `b2b` y fallback
- ✅ Token Bearer ManyChat hardcodeado en ambos HTTP (page `3882072`)

**Conclusión:** ningún edit estructural pendiente. La asignación automática a Miguel funciona desde el momento en que un agente invoca `elevar_conversacion` con `tipo='repo'`.

---

## Lo que SÍ está pendiente para activar el flujo end-to-end

### 1. Sincronizar los 5 prompts a Google Docs (bloqueante)

Los agentes leen su system prompt desde Google Docs vivos. Hasta que se copie el contenido de los `.md` v1.3, los agentes siguen operando con voseo rioplatense y sin la documentación actualizada del flujo a Miguel/Mauricio.

| Agente | Archivo local fuente (v1.3) | Doc destino |
|--------|-----------------------------|-------------|
| Derivación | `04_agents/agente-tofo-derivacion-system-prompt.md` | Google Doc del Agente de Derivación |
| B2B | `04_agents/agente-tofo-b2b-system-prompt.md` | Google Doc del Agente B2B |
| Servicio al Cliente | `04_agents/agente-tofo-servicio-system-prompt.md` | Google Doc del Agente de Servicio |
| Reposición | `04_agents/agente-tofo-reposicion-system-prompt.md` | Google Doc del Agente de Reposición |
| RRSS | `04_agents/agente-tofo-rrss-system-prompt.md` | Google Doc del Agente RRSS |

**Tip:** copiar solo desde el bloque `## System Prompt` (o `🧠 PROMPT MAESTRO` en RRSS) hacia abajo. El bloque de versionado y metadata (al inicio de cada `.md`) NO va en el Doc.

### 2. Confirmaciones operativas en ManyChat

- [ ] **Nombres exactos** registrados en ManyChat coinciden con los flows de asignación:
  - Flow `content20251129220130_658273` asigna a `Jose Miguel Chumacera Gonzalez` (sin acentos, exacto).
  - Flow `content20260526142445_613819` asigna a `Mauricio Garcia de la Vega` (exacto).
  - Si difieren, asignación falla silenciosamente en runtime.
- [ ] **Permisos Live Chat:**
  - Miguel: rol Agent — ve solo chats asignados.
  - Mauricio: rol Admin — ve todos.
- [ ] **Email de notificación** configurado en el flow de Miguel (verificar que llegue al mail correcto cuando se asigna un chat).

### 3. Opcionales (no bloqueantes)

- **Tag `FALLA_TECNICA`** en ManyChat: crear el tag y aplicarlo en el flow `content20251129220130_658273` para filtrar bandeja por tipo de chat.
- **Token ManyChat hardcodeado** en los nodos HTTP: pendiente mover a env var n8n. No es regresión (heredado de v1) pero recomendable antes de scale.

---

## Verificación end-to-end (7 tests)

Ejecutar **después** de sincronizar los Google Docs en el paso 1 (con prompts viejos los tests pueden fallar por razones de prompt, no de workflow).

| # | Escenario | Resultado esperado |
|---|-----------|--------------------|
| 1 | Falla completa: reportar → protocolo → código | Miguel recibe Telegram en `8067142805` + chat asignado en ManyChat + bot pausado |
| 2 | Falla + user pide humano (evidencia insuficiente) | Servicio eleva `tipo='repo'` → Miguel |
| 3 | "La máquina no funciona, quiero hablar con alguien" | Derivación detecta falla → `tipo='repo'` → Miguel |
| 4 | Login Miguel en ManyChat | Ve solo chats asignados (fallas) |
| 5 | Mauricio abre chat de falla | Puede ver y responder |
| 6 | Flujo B2B completo → cita | `tipo='b2b'` → Mauricio en `5839874323` (NO Miguel) |
| 7 | "Quiero hablar con una persona" (consulta general sin contexto) | `tipo=''` → fallback → Mauricio |

**Smoke test tono México** (paralelo, post-Google Docs):
- 1 conversación rápida por agente (Derivación, B2B, Servicio, Reposición). Confirmar 0 voseo en las respuestas que el bot manda al cliente.

---

## Riesgos / notas conocidas

1. **Doble escalamiento Reposición → Servicio.** Reposición y Servicio invocan `elevar_conversacion` con `tipo='repo'`. Si una conversación pasa primero por Servicio (que escala) y luego deriva a Reposición (que vuelve a escalar al final), Miguel recibe 2 notificaciones por la misma conversación. Comportamiento heredado, no corregido en este ciclo. Decisión pendiente: ¿colapsar la escalación en uno solo de los dos agentes?
2. **Token ManyChat hardcodeado** en el body del HTTP en ambos nodos. No regresión (ya estaba en v1) pero pendiente mover a env var antes de scale.
3. **Mensaje del Telegram a Mauricio** (`5839874323`) usa texto "🔔 Tienes un nuevo lead B2B" — sirve también para fallback (cliente quiere hablar con humano sin contexto B2B). Si en fallback querés un texto distinto, hay que separar el `Mensaje a Mauricio` en dos nodos. Hoy es el mismo nodo conectado a 2 outputs del Switch.

---

## Auto-cleanup de la etiqueta `FALLA_TECNICA` (ManyChat)

### Contexto

El flow `content20251129220130_658273` agrega la etiqueta `FALLA_TECNICA` al contacto al asignarlo a Miguel. Sin un mecanismo de limpieza, la etiqueta queda persistente — ensucia la bandeja del Live Chat (todo cliente que tuvo *alguna* falla histórica queda marcado FALLA_TECNICA permanentemente) y rompe las métricas.

### ⚠️ Nota: el trigger "Conversation Closed" no es nativo en ManyChat

Lo verificaste vos y se confirma: ManyChat hoy **no expone como Trigger de Automation** el cierre de una conversación del Live Chat. Tampoco hay un trigger "Resume Bot" ni "Hand back to bot". El enfoque event-driven que mencioné en mi respuesta anterior NO es viable.

### Solución: Delay + Remove Tag dentro del mismo flow (zero-touch, nativo)

La forma más simple y 100% nativa: agregar un `Delay` + `Remove Tag` al final del mismo flow que aplica la etiqueta. Ventana sugerida: **48 horas** (suficiente para que Miguel atienda la mayoría de los casos; si una falla queda abierta más tiempo, no pasa nada — el agente la re-agrega en la próxima invocación del flow).

### Setup paso a paso

#### Paso 1 — Abrir el flow

1. Login en ManyChat.
2. Sidebar izquierdo → **Automation** → **Flows**.
3. Buscar el flow con `flow_ns = content20251129220130_658273` (es el flow de "Asignar a Miguel" que disparamos desde n8n). Si tiene un nombre legible, debería ser algo como "Asignar conversación a Miguel" o similar.
4. Click para abrir el editor visual.

#### Paso 2 — Verificar / agregar la acción `Add Tag FALLA_TECNICA`

El flow debe tener (en este orden) las siguientes acciones. Las primeras 3 ya están:

1. ✅ **Assign Conversation** → `Jose Miguel Chumacera Gonzalez`
2. ✅ **Send Email Notification** (a los asignados)
3. ✅ **Stop Automations** (pausar bot)
4. ❓ **Add Tag** → `FALLA_TECNICA`

Si la **acción 4** ya está, saltá al Paso 3. Si no:

1. Hacer click en el `+` después de "Stop Automations".
2. En el menú lateral, buscar **Action** → **Add Tag**.
3. En el dropdown de tag, escribir `FALLA_TECNICA`. Si no existe, ManyChat ofrece "Create new tag" — confirmar.
4. Save.

#### Paso 3 — Agregar el Delay

1. Click en el `+` después de "Add Tag FALLA_TECNICA".
2. En el menú, buscar **Action** → **Smart Delay** (también puede aparecer como solo "Delay" según la versión).
3. Configurar:
   - **Duration:** `48`
   - **Unit:** `Hours`
   - (Si el campo pregunta por "Quiet hours" / "Time window", dejar en default — no aplica para esto.)
4. Save.

> **Tip de testing:** mientras hacés el primer caso de prueba, configurá el delay en `5` `Minutes` para no esperar 48 horas. Después de validar, volvelo a `48` `Hours`.

#### Paso 4 — Agregar el Remove Tag

1. Click en el `+` después del Delay.
2. En el menú, buscar **Action** → **Remove Tag**.
3. En el dropdown, seleccionar `FALLA_TECNICA`.
4. Save.

#### Paso 5 — Guardar el flow

1. Botón **Publish** (arriba a la derecha).
2. Confirmar el cambio. ManyChat aplica la nueva versión a las próximas invocaciones inmediatamente; las conversaciones ya escaladas (con el delay todavía corriendo de la versión vieja) no se afectan retroactivamente — usan la rama vieja hasta cumplir su delay.

### Paso 6 — Verificación del cleanup

Test ideal (con delay temporal en 5 min para no esperar):

1. Triggear el flow desde n8n para un subscriber de testing (ej. tu propio Instagram conectado al sandbox).
2. Ir al perfil del subscriber en ManyChat → confirmar:
   - Asignado a Miguel ✓
   - Tag `FALLA_TECNICA` presente ✓
   - Automations Status: Paused ✓
3. Esperar el delay (5 min para test).
4. Refrescar el perfil → confirmar:
   - Tag `FALLA_TECNICA` removida ✓
   - Asignación a Miguel: sigue (el flow no la limpia, solo la tag) — lo cual está bien
   - Automations Status: sigue Paused (no reactivamos bot acá — ver más abajo)
5. Revertir el delay a `48 Hours` y publish nuevamente.

### ⚠️ Importante: el cleanup NO incluye "Resume Bot"

Decisión deliberada. **No incluyas `Resume Automations` después del Remove Tag** porque:

- Si Miguel sigue atendiendo cuando se cumple el delay, el bot se mete en medio de la conversación humana = experiencia rota.
- Si Miguel ya terminó: el cliente está fuera de una falla activa. Si vuelve a escribir, normalmente vendrá con un mensaje que dispara el bot por su propio flujo (default reply / keywords / etc.). No se necesita un Resume forzado.

**Reactivar el bot queda como acción manual de Miguel cuando él decide que terminó:** abre el perfil del subscriber → sección "Automation status" → click `Resume`. Es 1 click, lo hace cuando él considera.

### Alternativa para Miguel: limpieza manual desde el perfil del subscriber

Si Miguel quiere limpiar inmediatamente (sin esperar 48h) además del auto-clean:

1. En el Live Chat, abrir el perfil del subscriber (panel derecho).
2. Sección **Tags** → click en la `X` al lado de `FALLA_TECNICA`.
3. Sección **Automation status** → click `Resume` (si quiere reactivar el bot también).

**Pro:** control total + reactivación inmediata del bot.
**Con:** 2 clicks por caso, depende de la disciplina.

### Combo recomendado

- **Auto-clean por delay 48h** (configurado una vez, siempre activo) → red de seguridad pasiva.
- **Quick visit al perfil del subscriber cuando Miguel termina** → limpieza inmediata + reactivación del bot si corresponde.

Con este combo: el 90% de los casos quedan limpios al cierre (Miguel hace la visita manual); el 10% que Miguel olvida se autolimpia a las 48h.

---

## Referencia técnica

- Workflow ID: `yJA04Pfyk2Id1aMo`
- ManyChat Page ID: `3882072`
- Flow NS Miguel: `content20251129220130_658273`
- Flow NS Mauricio: `content20260526142445_613819`
- Telegram credential: `armkWWROo7lljFIm` (TOFO Bot)
- Telegram chat IDs: Miguel `8067142805` · Mauricio `5839874323` · Alejandra `8219977470` (no usado en topología actual)
- Snapshot de prod en repo: `03_workflows/elevar-conversacion-tofo-prod-snapshot-2026-06-03.json`
- Blueprint anterior: `03_workflows/elevar-conversacion-tofo-v2.json` (diseño 2026-05-26, ya aplicado en prod)
- Guía contexto previa: `06_docs/guia-asignacion-fallas-miguel-2026-05-26.md`
