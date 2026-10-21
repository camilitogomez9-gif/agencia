# Edits al Google Doc del prompt SYS — bump v2.1 → v2.2

**Fecha:** 2026-06-09
**Doc vivo:** https://docs.google.com/document/d/1Obn0xzfAAUGs4oMpoh99dFXPfGuG9d6uBWglKNuPY5I/edit
**Versión actual del doc:** v2.1
**Versión objetivo:** v2.2
**Cambio:** agregar la sección "USO DEL CONTEXTO DEL TURNO" inmediatamente antes de `## FLUJO DE CONVERSACIÓN`. Cero cambios a las demás secciones.

Capa 3 del plan `/Users/camilo/.claude/plans/act-a-como-un-senior-imperative-quasar.md`. Complementa Capas 1+2 (workflow `sys-agente-principal-v0.9.json` + `sys-tool-guardar-email-v2.json`).

---

## Edit 1 — Header del Google Doc (opcional pero recomendado)

Si el Google Doc tiene un header con la versión, actualizalo:

- Buscar: `Versión: v2.1`
- Reemplazar por: `Versión: v2.2`
- Buscar: `Fecha: 2026-06-05`
- Reemplazar por: `Fecha: 2026-06-09`

Si no tiene esa línea (solo el cuerpo), ignorar este edit.

---

## Edit 2 — Insertar la nueva sección "USO DEL CONTEXTO DEL TURNO"

**Ubicación exacta:** insertar el bloque de abajo entre `## OBJETIVO PRINCIPAL` y `## FLUJO DE CONVERSACIÓN`. Es decir, justo arriba del título `## FLUJO DE CONVERSACIÓN`.

**Copy-paste literal (incluyendo los `---` separadores):**

```
---

## USO DEL CONTEXTO DEL TURNO

Cada turno recibís un `[CONTEXTO TURNO]` con el estado real del lead (canal, fecha y hora, perfil, etapa actual, datos ya capturados y productos ya mostrados). Usalo SIEMPRE como guardia antes de elegir qué decir. Las ETAPAS abajo son una guía progresiva — NO las ejecutes desde el principio si el contexto indica que ya pasaste por alguna.

Reglas duras de uso del contexto:

- Si `Etapa actual` es distinta de `bienvenida`, NO saludes ni te presentes de nuevo. Continuá donde quedó la conversación.
- Si `Etapa actual` es `derivado`, NO inicies nuevo diagnóstico. Reconocé que ya derivaste y respondé acotado a la consulta puntual. Excepción: si el lead pide un equipo distinto al ya derivado, podés reabrir diagnóstico.
- Si `Datos ya capturados` contiene `nombre`, NO preguntes el nombre.
- Si `Datos ya capturados` contiene `telefono`, NO pidas el teléfono. Excepción Regla 18: si el lead se refiere al número del canal, sí pedile que lo escriba en el chat.
- Si `Datos ya capturados` contiene `mail`, NO vuelvas a pedir el mail.
- Si `Datos ya capturados` contiene `ubicacion`, NO preguntes de dónde escribe.
- Si `Datos ya capturados` contiene `equipo_interes`, NO preguntes qué equipo le interesa; usalo para asesorar.
- `Productos ya mostrados` se aplica como dice la Regla 25 (no repetir equipos ya presentados).

Este bloque es transversal: aplica antes y durante las ETAPAS 1-6 del FLUJO DE CONVERSACIÓN, antes y durante las INSTRUCCIONES OPERATIVAS, y antes de cualquier tool call. Si una ETAPA o regla pide un dato que el contexto ya tiene, salteala — el dato ya está.
```

---

## Verificación post-edit

1. Abrí el Google Doc y confirmá que ahora aparecen en este orden:
   ```
   ## OBJETIVO PRINCIPAL
   ...
   ## USO DEL CONTEXTO DEL TURNO   ← NUEVA
   ...
   ## FLUJO DE CONVERSACIÓN
   ```

2. Confirmá que **NO** hay ninguna mención de "descuento" en la nueva sección ni en la Regla 4 ni en la ETAPA 6 (Edgardo descartó el incentivo del descuento el 2026-06-09).

3. Confirmá que las ETAPAS 1-6 quedaron intactas — la nueva sección NO las reemplaza; las complementa.

4. Confirmá que las INSTRUCCIONES OPERATIVAS y REGLAS CRÍTICAS no se tocaron.

---

## Si NO podés editar el Google Doc

El AI Agent del workflow `sys-agente-principal-v0.9` tiene un fallback inline en el nodo `backup` que ya contiene el prompt v2.2 completo (sincronizado 2026-06-09). Si el `Get a document` falla, el fallback se dispara automáticamente y el agente sigue usando v2.2. Esto te da un margen para coordinar el edit del Google Doc sin urgencia operativa.

---

## Cambios que NO se hacen

- **Regla 4 (solicitud de mail)**: queda intacta. NO menciona descuento. La frase canónica sigue siendo: *"Si querés, te mando más información sobre los equipos que consultaste. ¿Me pasás tu mail?"*
- **ETAPA 6 (cierre)**: queda intacta. NO menciona descuento. *"Confirmá que un representante se va a comunicar. Ofrecé enviarle más información por mail si no tenés el email todavía. Cerrá con calidez."*
- **HERRAMIENTAS, BASE DE CONOCIMIENTO, INSTRUCCIONES OPERATIVAS 1-26, CALIFICACIÓN, FORMATO DE RESPUESTA, REGLAS CRÍTICAS, ESCALADA A HUMANO**: sin cambios.

---

## Snapshot local sincronizado

- Archivo principal: `clients/SYS_SistemasYSoluciones/04_agents/agente-sistemasysoluciones-system-prompt.md` (ya bumpeado a v2.2)
- Backup inmediato: `agente-sistemasysoluciones-system-prompt-v2.1.md` (intacto, queda como referencia)
- Nodo `backup` del workflow `sys-agente-principal-v0.9.json`: sincronizado con el v2.2 completo.
