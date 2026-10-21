# IMP — Importadores Conectados (Diego Labores)

- **ID**: IMP
- **Nombre**: Importadores Conectados
- **Instagram**: @diegolabores
- **Niche**: agency (coaching / formación — importaciones)
- **Fecha inicio**: 2026-03
- **Status**: **live — sin pendientes al 2026-08-04.** Toda la línea de audios (grabación, parser `[AUDIO:NOMBRE]`, flows de ManyChat, mapping, variable `{{ORIGEN}}`) y la actualización del brand bible quedaron descartadas. El agente sigue operando solo con texto
- **Stack activo**: n8n, Airtable, ManyChat, WhatsApp, Facebook
- **Modelo LLM (nodo AI Agent)**: gpt-4.1-mini (OpenAI Chat Model)

## Contactos clave
- **Dueño**: Diego Labores (@diegolabores)
- **Secretaria**: Georgina Paradiso (Geor)

## OKRs del proyecto
- Agente conversacional que responde DMs en IG, WhatsApp y Facebook
- Guarda historial y pipeline de leads en Airtable
- Notifica al equipo por Telegram ante eventos clave

## Notas críticas
- System prompt legacy en `04_agents/agente-diegolabores-system-prompt.md` — versión canónica está en `06_docs/brand-bible.md`
- Flujo de producción: `03_workflows/flujo-n8n-agente-diegolabores.json`
- Flujo de test Telegram: `03_workflows/flujo-n8n-telegram-test.json`
