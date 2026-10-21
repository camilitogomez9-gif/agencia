# Guia de implementacion: Asignacion de fallas a Miguel

**Fecha:** 2026-05-26
**Objetivo:** Que Jose Miguel Chumacera Gonzalez (Tecnico) vea solo chats de fallas en ManyChat Live Chat, se le asignen automaticamente, y tanto el como Mauricio puedan responder.

---

## Mecanismo de asignacion

ManyChat ya tiene un **Flow de asignacion a Miguel** (`content20251129220130_658273`) que ejecuta 3 acciones:

1. **Asignar conversacion** a Jose Miguel Chumacera Gonzalez
2. **Notificar a los asignados** (2 personas via email)
3. **Pausar todas las automatizaciones** para siempre (el bot deja de responder, el humano toma el control)

El nodo "Elevar" en n8n ya llama a este flow. El problema es que HOY las 3 ramas (repo, b2b, fallback) terminan en ese mismo nodo → todas las escalaciones se asignan a Miguel, incluyendo B2B.

---

## Cambios implementados

### 1. ManyChat: flow de asignacion a Mauricio (creado)

Flow creado con las acciones:
1. **Asignar conversacion** a Mauricio Garcia de la Vega
2. **Notificar a los asignados** via email
3. **Pausar todas las automatizaciones** para siempre

flow_ns: `content20260526142445_613819`

### 2. Sub-workflow n8n: separar rama B2B/fallback

**Archivo:** `03_workflows/elevar-conversacion-tofo-v2.json`

**Antes (v1):**
```
Switch (tipo)
  |-- repo     → Telegram Miguel    → "Elevar" (flow Miguel)     ← todo a Miguel
  |-- b2b      → Telegram Mauricio  → "Elevar" (flow Miguel)     ← MAL: B2B a Miguel
  |-- fallback → Telegram Alejandra → "Elevar" (flow Miguel)     ← MAL: todo a Miguel
```

**Despues (v2):**
```
Switch (tipo)
  |-- repo     → Telegram Miguel    → "Elevar" (flow Miguel)         ← Miguel ✅
  |-- b2b      → Telegram Mauricio  → "Elevar a Mauricio" (flow nuevo) ← Mauricio ✅
  |-- fallback → Telegram Alejandra → "Elevar a Mauricio" (flow nuevo) ← Mauricio ✅
```

**Unico cambio:** se agrego nodo `Elevar a Mauricio` (HTTP Request, sendFlow) y se reconectaron las ramas B2B y fallback a este nodo. La rama repo queda intacta.

### 3. Prompts ajustados (2 archivos)

#### Agente de Servicio al Cliente v1.1 → v1.2

**Archivo:** `04_agents/agente-tofo-servicio-system-prompt.md`
**Seccion:** §10 ELEVAR CONVERSACION

**Antes:** llamaba `elevar_conversacion` sin especificar `tipo`. Sin tipo definido, el LLM podia pasar cualquier valor o vacio → la rama del Switch era impredecible.

**Despues:** siempre pasa `tipo='repo'`. Toda conversacion en este agente es sobre fallas → debe ir a Miguel.

#### Agente de Derivacion v1.1 → v1.2

**Archivo:** `04_agents/agente-tofo-derivacion-system-prompt.md`
**Seccion:** §7 ELEVAR CONVERSACION

**Antes:** siempre pasaba `tipo=''` (vacio). Si el user pedia humano durante una falla, iba al fallback en vez de a Miguel.

**Despues:** tipo contextual:
- Conversacion sobre falla/error/maquina → `tipo='repo'` → Miguel
- Conversacion sobre negocio/inversion → `tipo='b2b'` → Mauricio
- Otro caso → `tipo=''` → fallback

### 4. Prompts sin cambios (validados)

| Agente | `tipo` | Correcto |
|--------|--------|----------|
| **Reposicion** v1.1 | Siempre `'repo'` al final | ✅ |
| **B2B** v1.2 | Siempre `'b2b'` antes de cita | ✅ |
| **RRSS** v1.1 | No tiene `elevar_conversacion` | ✅ |

---

## Mapa completo de `elevar_conversacion` (post-cambios)

| Agente | Cuando llama | tipo | Destino |
|--------|-------------|------|---------|
| Derivacion | User pide humano + contexto falla | `'repo'` | Miguel |
| Derivacion | User pide humano + contexto B2B | `'b2b'` | Mauricio |
| Derivacion | User pide humano + otro | `''` | Fallback (Mauricio) |
| Servicio al Cliente | User pide humano (siempre es falla) | `'repo'` | Miguel |
| Reposicion | Siempre despues de entregar codigo | `'repo'` | Miguel |
| B2B | Antes de confirmar cita | `'b2b'` | Mauricio |

---

## Pasos para activar

1. **ManyChat:** crear flow de asignacion a Mauricio (copiar estructura del flow de Miguel, cambiar asignado)
2. **ManyChat:** anotar el `flow_ns` del nuevo flow
3. **JSON:** abrir `elevar-conversacion-tofo-v2.json`, buscar `FLOW_NS_ASIGNAR_MAURICIO`, reemplazar con el flow_ns real
4. **n8n:** importar el JSON modificado como nueva version del workflow `Elevar conversacion | Tofo`
5. **n8n:** copiar los prompts actualizados (Derivacion v1.2 y Servicio v1.2) a los Google Docs que alimentan a los agentes en el workflow principal
6. **Testear** segun tabla de verificacion

---

## Verificacion

| # | Test | Resultado esperado |
|---|------|--------------------|
| 1 | Falla completa: reportar → protocolo → codigo | Miguel recibe Telegram + chat asignado en ManyChat + bots pausados |
| 2 | Falla + user pide humano (evidencia insuficiente) | Servicio eleva con tipo='repo' → Miguel |
| 3 | "La maquina no funciona, quiero hablar con alguien" | Derivacion detecta falla → tipo='repo' → Miguel |
| 4 | Login como Miguel en ManyChat | Solo ve chats asignados (fallas) |
| 5 | Mauricio abre mismo chat de falla | Puede ver y responder |
| 6 | Flujo B2B → cita agendada | tipo='b2b' → Mauricio, NO Miguel |
| 7 | "Quiero hablar con una persona" (contexto general) | tipo='' → fallback → Mauricio |

---

## Datos del workflow

- Workflow ID: `yJA04Pfyk2Id1aMo`
- ManyChat page ID: `3882072`
- Flow NS asignacion Miguel: `content20251129220130_658273`
- Flow NS asignacion Mauricio: `content20260526142445_613819`
- Telegram Bot: `TOFO Bot` (credential ID: `armkWWROo7lljFIm`)
- Telegram chat IDs: Miguel `8067142805` | Mauricio `5839874323`
