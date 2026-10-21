# Runbook: Desarrollo de Agente Conversacional v1 — Canal Telegram

**Tipo:** Proceso estándar de desarrollo  
**Aplica a:** Clientes nuevos con agente v1, canal Telegram  
**Prerequisito:** Cliente realizó el pago del 50%

---

## Visión general del flujo

```
Pago 50%
  → Enviar formulario Typeform al cliente
  → Cliente completa el formulario
  → Descargar CSV y compartir con Claude
  → [FASE 1] Generar System Prompt v1 + mensaje con datos faltantes
  → Enviar mensaje al cliente
  → Cliente responde con datos faltantes
  → [FASE 2] Completar prompt a v1.1 + generar guía de testing
  → Configurar workflow en n8n
  → Testing en Telegram
  → Ajustes iterativos hasta aprobación
  → Activar con clientes reales
```

---

## FASE 1 — Recepción del formulario

### Trigger
El cliente completó el formulario de Typeform. Se descargó el CSV.

### Acción
Compartir el CSV con Claude y ejecutar `/generar-system-prompt`.

### Output esperado

1. **System Prompt v1** — completo en comportamiento, tono y flujo. Puede tener gaps en la base de conocimiento (productos, precios, FAQs específicas) que se completan en Fase 2.

2. **Mensaje para el cliente** — lista de datos faltantes para enviar por WhatsApp. Solo lo que realmente enriquece o bloquea el agente.

### Acciones post-Fase 1

- [ ] Copiar el System Prompt v1 al nodo `AI Agent` del workflow en n8n  
  → Usar `_core/templates/workflows/agente-telegram/WF_AGENTE_TELEGRAM_v1.json` como base
- [ ] Enviar el mensaje de datos faltantes al cliente por WhatsApp
- [ ] Guardar el prompt en `clients/[CLT###]/04_agents/[nombre]-system-prompt.md`

---

## FASE 2 — Recepción de datos faltantes

### Trigger
El cliente respondió con los datos solicitados (equipos, precios, FAQs, etc.).

### Acción
Compartir la respuesta del cliente con Claude e indicar que hay que completar el prompt.  
Claude actualizará solo las secciones con gaps — no reescribe el prompt completo.

### Output esperado

1. **System Prompt v1.1** — prompt completo con base de conocimiento rellena.

2. **Guía de Testing** — tabla de casos con mensajes exactos a enviar, resultados esperados y columnas para registrar resultados. Lista para pegar en Notion.  
   Incluye: casos simples (saludo, precio, scope, FAQs) + flujos conversacionales (diagnóstico completo, derivación, usuario hostil, cierre sin decisión, ramas del flujo).

### Acciones post-Fase 2

- [ ] Actualizar el System Prompt en n8n con la versión v1.1
- [ ] Guardar la guía de testing en `clients/[CLT###]/07_testing/testing-guide-v1.md`
- [ ] Pegar la guía de testing en Notion (o el canal de seguimiento acordado)

---

## FASE 3 — Testing en Telegram

### Cómo testear
Abrir el chat con el bot de Telegram configurado para este cliente y ejecutar cada caso de la guía en el orden listado. Registrar el resultado en la columna "Resultado obtenido" y marcar OK o no.

### Criterios para aprobar un caso
- El agente responde dentro del scope correcto
- El tono coincide con el definido en el prompt
- Los datos que da son correctos (productos, precios, horarios)
- Las derivaciones al equipo humano se activan en los momentos indicados

### Si un caso falla
1. Identificar en qué sección del prompt está el problema (tono, flujo, base de conocimiento, reglas)
2. Ajustar solo esa sección
3. Re-testear el caso fallido + los casos relacionados
4. Registrar el cambio en el historial de versiones del archivo del prompt

### Cuándo dar por aprobado el testing
- Todos los casos simples marcados OK
- Los flujos conversacionales principales marcados OK (se admite ajuste menor en flujos de borde)
- El cliente (o referente interno) validó al menos 1-2 conversaciones reales de prueba

---

## FASE 4 — Activación

### Prerequisito
Testing aprobado internamente.

### Acciones
- [ ] Reconectar el workflow de n8n al bot de Telegram de producción del cliente (no el de prueba)
- [ ] Confirmar con el cliente que el bot está activo
- [ ] Registrar la fecha de activación en `CLIENT_INFO.md` → Status: `live`
- [ ] Ejecutar `cliente-sync`

---

## Recursos

| Recurso | Ubicación |
|---------|-----------|
| Skill para generar el prompt | `/generar-system-prompt` |
| Template workflow n8n | `_core/templates/workflows/agente-telegram/WF_AGENTE_TELEGRAM_v1.json` |
| Template system prompt | `_core/templates/agents/SYSTEM_PROMPT_TEMPLATE.md` |
| Guía de principios prompt engineering | `_core/standards/system-prompt-engineering.md` |
| Carpeta del cliente | `clients/[CLT###_Nombre]/` |

---

## Historial

| Versión | Fecha | Cambio |
|---------|-------|--------|
| v1.0 | 2026-04-11 | Versión inicial basada en el proceso de Sistemas & Soluciones (CLT003) |
