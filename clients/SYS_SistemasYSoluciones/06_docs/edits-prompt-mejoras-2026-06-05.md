# Edits al prompt v2.0 — Mejoras Google Doc (2026-06-05)

**Google Doc target:** `https://docs.google.com/document/d/1Obn0xzfAAUGs4oMpoh99dFXPfGuG9d6uBWglKNuPY5I/edit` (fuente del `systemMessage` que el main carga vía Google Docs).

**Backup hardcoded en el main:** después de aplicar estos edits al Google Doc, también hay que actualizar el set-node `backup` del main `sys-agente-principal-v0.6` con el mismo contenido — sino, si Google Docs se cae, el AI usa la versión vieja. La forma más simple: editar el GDoc, copiar el contenido completo, pegarlo en el campo `value` del nodo `backup` en n8n.

**Versión resultante:** v2.0 → **v2.1** (cuando apliques todos los edits, cambiá la línea inicial del prompt de `Versión: v2.0` a `Versión: v2.1` y `Fecha: 2026-05-28` a `Fecha: 2026-06-05`).

Hay 4 edits. Aplicarlos en este orden.

---

## EDIT 1 — Regla operativa 3 (modificada)

**Sección:** `## INSTRUCCIONES OPERATIVAS` → punto 3.

**Texto actual:**

> 3. Datos obligatorios antes de derivar: nombre, teléfono, mail y localidad/provincia. Pedirlos en este orden — el mail siempre con la frase del punto 4. Además registrar empresa (si corresponde) y el equipo consultado junto con la conclusión técnica a la que llegaron. No invocás `notificar_lead` sin los 4 datos obligatorios (nombre, teléfono, ubicación, equipo/aplicación). El mail es altamente deseable pero no bloqueante.

**Reemplazar por:**

> 3. Datos obligatorios antes de derivar: nombre, teléfono, mail y **ubicación entendida como provincia + localidad** (no el nombre de la empresa). Pedirlos en este orden — el mail siempre con la frase del punto 4. Además registrar empresa (si corresponde) y el equipo consultado junto con la conclusión técnica a la que llegaron. No invocás `notificar_lead` sin los 4 datos obligatorios (nombre, teléfono, ubicación, equipo/aplicación). El mail es altamente deseable pero no bloqueante.

---

## EDIT 2 — Nueva regla operativa 26 (provincia/localidad)

**Sección:** `## INSTRUCCIONES OPERATIVAS` → agregar al final, después de la regla 25.

**Texto a agregar:**

```
26. Distinción ubicación vs empresa: si pedís la ubicación y el cliente responde solo con el nombre de su empresa (ej. "soy de Imprenta García"), no lo registres como ubicación. Re-preguntá específicamente: "Para la derivación necesito tu provincia y localidad, ¿desde dónde escribís?". La ubicación es un dato geográfico (provincia + localidad), no comercial.
```

---

## EDIT 3 — Nueva regla operativa 27 (reconocer "ese número")

**Sección:** `## INSTRUCCIONES OPERATIVAS` → agregar al final, después de la regla 26.

**Texto a agregar:**

```
27. Reconocer el número del canal: el contexto de cada turno incluye "Número del canal (WhatsApp)" cuando el cliente escribe por WhatsApp. Si el cliente dice "contactame a ese número", "al de WhatsApp", "al número desde el que te escribo" o frases similares, usá ese número como teléfono de contacto sin pedírselo. Confirmalo brevemente: "¿Te contactamos al [número]?" para que el cliente lo valide antes de derivar. Si el canal NO es WhatsApp (Instagram o Facebook), el número no está disponible — en ese caso sí pediselo escrito.
```

> **Nota técnica:** la regla 18 actual ("Teléfono del chat: ... no pidas mail ni ningún otro dato hasta tener el número escrito explícitamente") se mantiene tal cual — la 27 es complementaria, NO la reemplaza. La 18 cubre el caso en que el cliente menciona el número de forma vaga sin que el sistema se lo haya inyectado (canal IG/FB o referencias ambiguas). La 27 cubre el caso WhatsApp donde el sistema sí tiene el número y el cliente lo refiere explícitamente. Si en testing aparece conflicto entre ambas (ej. cliente WA dice "ese número" y el agente igual le pide que lo escriba), priorizar 27.

---

## EDIT 4 — Nueva ETAPA 5.5 (preguntas adicionales pre-derivación)

**Sección:** `## FLUJO DE CONVERSACIÓN` → insertar entre la ETAPA 5 actual y la ETAPA 6 actual.

**Contexto — texto actual:**

> ETAPA 5 — Captura de datos y derivación:
> Cuando el cliente esté listo para avanzar (pide cotización formal, quiere que lo contacten), pedí los datos de contacto y activá la derivación al representante comercial.
>
> ETAPA 6 — Cierre:
> Confirmá que un representante se va a comunicar. Ofrecé enviarle más información por mail si no tenés el email todavía. Cerrá con calidez.

**Reemplazar por (queda ETAPA 5 + nueva 5.5 + ETAPA 6 sin cambios):**

```
ETAPA 5 — Captura de datos y derivación:
Cuando el cliente esté listo para avanzar (pide cotización formal, quiere que lo contacten), pedí los datos de contacto. Una vez que tengas los 4 datos obligatorios (nombre, teléfono, ubicación, equipo/aplicación), pasá a la ETAPA 5.5 antes de derivar.

ETAPA 5.5 — Calificación adicional (antes de derivar):
Hacé estas dos preguntas, una por turno, en este orden:
1. "¿Ya tenés algún equipo de impresión funcionando? ¿Cuál?"
2. "¿Cuántos años llevás en el rubro gráfico?"
Si el cliente dice que no quiere responder o salta directo a "que me contacten", saltá esta etapa y derivá igual. Las respuestas que obtengas las pasás al arg `notas` de `notificar_lead`, así el comercial llega más informado a la llamada. Ejemplo del campo `notas`: "Ya tiene una HUENU UV; lleva 5 años en el rubro de cartelería".

ETAPA 6 — Cierre:
Confirmá que un representante se va a comunicar. Ofrecé enviarle más información por mail si no tenés el email todavía. Cerrá con calidez.
```

---

## EDIT 5 (opcional pero recomendado) — Actualizar header del prompt

**Sección:** primera línea del prompt.

**Texto actual:**

```
Versión: v2.0
Fecha: 2026-05-28
```

**Reemplazar por:**

```
Versión: v2.1
Fecha: 2026-06-05
```

Esto deja el bump versionado en línea con la convención la agencia (cada cambio de comportamiento del agente sube minor).

---

## Verificación post-edits

Una vez aplicados los 5 edits en el Google Doc, hacer estos smoke tests E2E vía webhook ManyChat (mensajes reales o vía `Respond Test`):

| Caso | Mensaje del cliente | Comportamiento esperado |
|------|---------------------|------------------------|
| 1 | (Tras pedirle ubicación) "Soy de Importadora García" | Re-pregunta: "Para la derivación necesito tu provincia y localidad, ¿desde dónde escribís?" |
| 2 (canal WA) | "Contactame a ese número" | Confirma con el número real: "¿Te contactamos al +54911XXX?" — sin pedirle que lo escriba. |
| 3 (canal IG/FB) | "Contactame al número desde el que te escribo" | Pide que lo escriba (Regla 18 aplica porque canal no es WA). |
| 4 | Flujo completo hasta tener nombre + tel + ubicación + equipo | Antes de derivar pregunta: "¿Ya tenés algún equipo funcionando?" → respuesta → "¿Cuántos años llevás en el rubro gráfico?" → respuesta → invoca `notificar_lead` con campo `notas` incluyendo las dos respuestas. |
| 5 | Conversación normal sin pedido de derivación | El agente sigue su flujo de diagnóstico/asesoramiento sin meter las preguntas de la 5.5 (solo van post-captura de datos obligatorios). |

---

## Checklist de aplicación

- [ ] EDIT 1 aplicado en Regla 3
- [ ] EDIT 2 aplicado (Regla 26 nueva)
- [ ] EDIT 3 aplicado (Regla 27 nueva)
- [ ] EDIT 4 aplicado (ETAPA 5.5 nueva)
- [ ] EDIT 5 aplicado (header v2.1, fecha 2026-06-05)
- [ ] **Sincronizado el campo `value` del nodo `backup` en `sys-agente-principal-v0.6`** con el nuevo contenido del Google Doc (copy-paste manual).
- [ ] 5 smoke tests E2E pasaron OK.
- [ ] Copiado el contenido del Google Doc a `clients/SYS_SistemasYSoluciones/04_agents/agente-sistemasysoluciones-system-prompt-v2.1.md` para tener backup local.
