# ManyChat Snapshot — Venttur
> Exportado vía API el 2026-05-13. Fuente: `clients/VTR_Venttur/03_workflows/manychat-venttur-export-snapshot-v1.json`

---

## Cuenta

| Campo | Valor |
|-------|-------|
| Nombre | Venttur \| Agente de IA |
| Timezone | America/Montevideo |
| Plan | Pro |

---

## Flows (14)

| ns | Nombre | Carpeta |
|----|--------|---------|
| `content20260513183625_644743` | Rescate Post-Link | Reactivación |
| `content20260210212250_552933` | Borrar contactos | Manejo de contactos |
| `content20250918181220_518318` | Asignar número | — |
| `content20250721163426_851504` | Seguimiento agenda | Agendamiento |
| `content20250718124614_140983` | Agenda | Seguimientos |
| `content20250718124216_992343` | Lead General | Seguimientos |
| `content20250718123847_652764` | Summer Camp | Seguimientos |
| `content20250718123255_243860` | Año Académico | Seguimientos |
| `content20250718122822_491460` | Gap year | Seguimientos |
| `content20250718121921_967738` | Pathway | Seguimientos |
| `content20250718115245_638127` | Boarding School | Seguimientos |
| `content20250716130059_365663` | Elevar | Agente IA Principal |
| `content20250617172539_850988` | Enviar mensajes | Agente IA Principal |
| `content20250617171957_654158` | Recibir mensajes | Agente IA Principal |

### Carpetas

| ID | Nombre |
|----|--------|
| 30830401 | Agendamiento |
| 30788316 | Agente IA Principal |
| 32679762 | Manejo de contactos |
| 33306477 | Reactivación |
| 30788323 | Seguimientos |

---

## Custom Fields (13)

| ID | Nombre | Tipo | Descripción |
|----|--------|------|-------------|
| 14465599 | `ad_source_id` | text | ID del anuncio de Meta |
| 14584070 | `agendan_cita` | boolean | Almacena si el lead ya agendó (viene de Airtable) |
| 14465598 | `ctwa_clid` | text | Click ID del anuncio CTWA |
| 13359001 | `mensaje_inicial_asesoria` | text | — |
| 13358999 | `mensaje_link_asesoria` | text | — |
| 13337279 | `parte1` | text | — |
| 13337280 | `parte2` | text | — |
| 13337281 | `parte3` | text | — |
| 14183362 | `programa_interes` | text | — |
| 14584073 | `programa_rescate` | text | Almacena el programa de interés del lead (viene de Airtable) |
| 14465600 | `programa_wpp` | text | Programa detectado para leads WA directo |
| 13337278 | `respuesta_definitiva` | text | — |
| 13644518 | `wpp` | text | — |

---

## Tags (5)

| ID | Nombre |
|----|--------|
| 87501935 | `RESCATE_PROGRAMA_NO_MAPEADO` |
| 87501917 | `LINK_ABANDONADO_FRIO` |
| 77385811 | `seguimiento_agenda` |
| 72033971 | `wpp` |
| 68459367 | `seguimiento` |

---

## Notas para la migración

- El flow "Rescate Post-Link" (`content20260513183625_644743`) es el rescate **actual** en ManyChat (la versión que se va a reemplazar por el flujo n8n). Vive en la carpeta "Reactivación".
- El flow "Enviar mensajes" (`content20250617172539_850988`) es el que usa el rescate n8n para enviar `parte1`/`parte2`/`parte3`. Está en "Agente IA Principal".
- Los flujos de "Seguimientos" (Boarding School, Pathway, etc.) son los que probablemente entregan el link de agendamiento. El External Request a n8n se conecta ahí.
- Los custom fields `parte1`, `parte2`, `parte3` ya existen — no crear.
- Los tags `RESCATE_PROGRAMA_NO_MAPEADO` y `LINK_ABANDONADO_FRIO` ya existen — no crear.
- `agendan_cita` (boolean) en ManyChat y `Agendan cita` en Airtable son sincrónicos — n8n lee desde Airtable directamente.
