# CRZ — Cereza Invest

## Datos generales
- ID: CRZ
- Nombre: Cereza Invest
- Niche: generic
- Fecha inicio: 2026-05-12
- Status: build

## Stack activo
- [x] n8n
- [ ] Airtable
- [ ] Clientify
- [ ] Google Sheets
- [x] WhatsApp
- [ ] Notion

## Contactos clave
| Rol | Nombre | Contacto |
|-----|--------|---------|
| Decisor | Maxi Robles | — |
| Técnico | | |

## OKRs del proyecto
1. Agente conversacional "Alexis" que califica leads de inversión y agenda llamadas
2. Cobertura multi-canal: WhatsApp + Instagram vía ManyChat
3.

## Notas críticas
- País: Argentina
- Rubro: inversiones / educación financiera
- Agente se presenta como "Alexis de Cereza Invest"
- Arquitectura: ManyChat webhook → n8n AI Agent (gpt-4.1) + PostgreSQL memoria → ManyChat sendFlow
- Transcripción de audios vía Whisper; detección de canal IG vs WPP
- Tool "notificar": activa flow ManyChat cuando usuario pregunta precios o genera fricción
- Tool "escalar": activa flow cuando usuario se enoja o no agendó tras múltiples intentos
- Credenciales OpenAI en nombre del cliente ("Cereza Invest (suya)")
- Credenciales PostgreSQL: "Cereza Invest"
