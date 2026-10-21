# IDs de recursos GHL VTR (creados por API)

**Generado:** 2026-09-21 por sesión automatizada.
**Location:** `7aXb4JCKsWV5nUyBXeSF`

## Users

| Nombre | Email | userId |
|---|---|---|
| Rodrigo Garcia | `rgarcia@venttur.com` | `IaSkyQuhbjGdwNyXg1VD` |
| Andres Garcia | `agarcia@venttur.com` | `4VtbDVSjnoHm5125qa8I` |
| Diego García de la Vega Delfín | `dgarcia@venttur.com` | `Y1cWtQ0KoVhP9U1iD7MV` |
| Mauricio Garcia De La Vega Delfin | `administracion@venttur.com` | (listar con `GET /users`) |
| Max Almonte | `malmonte@venttur.com` | (listar con `GET /users`) |

## Custom Fields de Contact (relevantes)

| Nombre | Unique Key | id | Uso |
|---|---|---|---|
| `test_aventurera` | `contact.test_aventurera` | `V2buxmVoMqCQOKJncUcI` | Test §0.2 (queda de referencia). |
| `atribuida_a` | `contact.atribuida_a` | `yEgBeLQNnCPkTTv8OvfX` | **Producción — aventureras §2.2.** |

## Pipelines relevantes

| Nombre | id | Etapas |
|---|---|---|
| `VENTAS EMA METODOLOGÍA` | `9MHAJV5x5QEQ1CMEEbiK` | 12 (incluye `AGENDÓ REUNIÓN`) |
| `Operativo Idiomas` | `ByuL5ELI3LHHhtxZj4ge` | **4** (faltan 5 según runbook `14a`) |
| `Operativo Internados` | `iB14RGap1HImv5smV210` | 13 (falta `PERFILAMIENTO`) |
| `Campaña Internados Erika` | `0Lp7xCY9NTnDOQ6YRFf5` | 12 (incluye `Cita de Ventas concretada`, trigger EMA) |

**Gap detectado:** `Operativo Idiomas` tiene solo 4 etapas y el runbook Rodrigo requiere 9 (`Recabar Datos` / `Realizar Aplicación` ✅ / `Recibir Documentos` / `Enviar Presupuesto` / `Cobrar Programa` ✅ / `Enviar Comprobante` / `Coordinar llegada` / `Tramitar Visa` ✅ / `Estudiante...` ✅). Faltan: **Recabar Datos, Recibir Documentos, Enviar Presupuesto, Enviar Comprobante, Coordinar llegada**.

**Gap detectado:** `Operativo Internados` no tiene etapa `PERFILAMIENTO` (individual/familiar) explícita. Verificar si es prerequisito real o si se resolvió con otras etapas.

## Tags creados en esta sesión (18 tags del §Anexo A del runbook Rodrigo)

Todos creados por API el 21/9. Ver detalles: `06_docs/mensaje-cliente-accionables-2026-09-21.md` no aplica — esto es interno.

**Idiomas (8):** `aplicación realizada en espera de documentos` · `documentos recibidos enviar presupuesto (idiomas)` · `presupuesto final aceptado (idiomas)` · `programa pagado (idiomas)` · `no necesita visa` · `trámite finalizado` · `necesita visa` · `llegada coordinada (idiomas)`.

**Internados (10):** `cita perfilamientos agendada (internados)` · `perfilamientos realizados en espera resultados` · `resultados de perfilamientos y presentación` · `escuela elegida agendar cita familia + escuela` · `reunión familia + escuela efectuada (internados)` · `aplicación autorizada por familia (internados)` · `aplicación realizada revisión con familia` · `aplicación enviada a escuela en espera` · `estudiante aceptado inicio cobranza programa` · `perfilamiento ema pagado`.

**Tags pre-existentes (no tocados):** `atencion_humana` · `cualificado` · `follow-up` · `high priority` · `lead_prueba` · `link_abandonado_frio` · `rescate_programa_no_mapeado` · `seguimiento` · `seguimiento_agenda` · `warm lead`.

## Calendarios creados en esta sesión

Todos tipo **Reserva personal**, Lun-Vie 9-18h, duración 30 min, meetingLocation="Videollamada".

| Slug | Nombre | Asesor | cal_id |
|---|---|---|---|
| `cal-internados` | Internados (Rodrigo) | Rodrigo | `CIxOV100yyRFqPoa6LdK` |
| `cal-intercambio` | Intercambio académico con familias (Rodrigo) | Rodrigo | `SiAPsk27X5yilff5bSS5` |
| `cal-campamentos` | Campamentos de verano (Rodrigo) | Rodrigo | `981EzNS7jf9HhJNkL41W` |
| `cal-viajes-educativos` | Viajes educativos (Andrés) | Andrés | `j0jcAdaieJXaoPZBempp` |
| `cal-educacion-superior` | Educación superior (Andrés) | Andrés | `RUjWx74NPK77FPUcs5ME` |
| `cal-cursos-idiomas` | Cursos de idiomas (Andrés) | Andrés | `5PxslDhdQxZeDcKmLYNq` |
| `cal-pathway-alemania` | Pathway Alemania (Andrés) | Andrés | `oNN7oLWsNhQlWi7q7pDX` |
| `cal-gap-year` | Gap Year - Estudia y Trabaja (Andrés) | Andrés | `Omgde6Ko8TGKYMtiUb1x` |

**De prueba (para test C1 de §5.1):**
| Slug | Nombre | Asesor | cal_id |
|---|---|---|---|
| `cal-test-a-api` | cal-test-A | Rodrigo | `aQB4P4wMYp2yL9kk0ubz` |
| `cal-test-b-api` | cal-test-B | Rodrigo (mismo que A) | `Vp1mKGaKD3WpytJDBxRo` |
| `prueba-aventurera` | prueba-aventurera (§0.2 confirmado) | Mauricio | `r8eOGhHud3mgjGRS9nDT` |

**Pendiente (requiere OAuth cliente):** activar "Verificar conflictos con Google Calendar personal" en cada uno — Rodrigo/Andrés deben conectar OAuth Google primero (accionable cliente #6).

## URLs de webhooks n8n (para §10.5 cutover + §11.1 rollback)

- **`main-venttur` (Webhook node):** `https://[TU-INSTANCIA-N8N]/webhook/43fa146c-53a0-4915-89ef-311b7e72a6a3` (método POST).
  - Este es el URL al que GHL debe apuntar el `Contact Reply` en el §10.5 D-day 10:00.
  - Para rollback (§11.1): re-apuntar el webhook al de ManyChat viejo (recuperar el URL del snapshot pre-BSP).

## Workflows existentes (VTR pre-esta sesión)

- `WF-01 Enrutador de Entrada` (published) · `eb835383-f5d0-41b1-b2d0-b4752b5a0559`
- `WF-02 Rescate (disparador)` (published) · `1ed7af47-4727-4c18-a1f3-d2281c1e8609`

Los 23 flujos de Rodrigo (§3) + Handoff (§7) NO existen todavía.

## Email Templates

**0 templates en VTR.** La plantilla `Solicitud de datos...` que el runbook Rodrigo cita (Clientify id `732481`) hay que crearla en GHL antes del rebuild de idiomas 2.1. Ver `06_docs/plantilla-email-solicitud-datos-idiomas.md` (a crear cuando esté el contenido).

## Diego Matus vs Diego García

El runbook Rodrigo cita usuario `Diego Matus` como creador original de los flujos Clientify. **NO existe** en GHL VTR. El único Diego es `Diego García de la Vega Delfín` (`dgarcia@venttur.com`). Confirmar con la agencia si "Diego Matus" es alguien externo (staff de Clientify que administraba) o si el runbook confundió el nombre.

## Credentials n8n VTR (para §9.2 rotación de secretos)

10 credentials distintas usadas por los 13 workflows VTR (extraídas del snapshot `vivo-2026-09-21-preventivo`).

**Críticas (rotar en §9.2 D-1 25/9):**
| Type | Nombre | id | Usado por |
|---|---|---|---|
| `openAiApi` | **`OpenAI \| Venttur`** | `ibkhdCMyhr3yqDQk` | `main-venttur` · `staging-agent-telegram` |
| `openAiApi` | **`OpenAI la agencia®`** | `Fa3aaCsYTBS79y3Y` | `clasificador-cualificado` · `resumen-etiquetas-seguimientos` |

**Adicional a rotar (§9.2):** el HARDCODE de OpenAI en el nodo `Transcribir audio/s` del `main-venttur.json` (header `Authorization: Bearer sk-proj-...`). Reemplazar por credential HTTP header ANTES de rotar la key nueva, o el Whisper deja de transcribir.

**Diferibles (§16.2 nice to have, no bloquean cutover):**
| Type | Nombre | id | Usado por |
|---|---|---|---|
| `airtableTokenApi` | `Venttur Dashboard` | `[N8N_CREDENTIAL_ID]` | 8 workflows |
| `postgres` | `Postgres Venttur` | `ihpvM7nYMdLCwWDP` | 7 workflows |
| `telegramApi` | `botla agencia` | `V5k84z3AjQc9Y5yg` | 3 workflows |
| `telegramApi` | `Venttur` | `EpeHMkSGuruXQu9U` | staging |
| `httpHeaderAuth` | `GHL VTR (PIT)` | `YkVmaA4jlRbO1TQD` | 4 workflows |
| `httpHeaderAuth` | `Venttur Header Auth account` | `9OZtsIsmuVEG9l6R` | outreach + rescate |
| `googleCalendarOAuth2Api` | `Google Calendar \| Rodrigo` | `6idhqxfKUyIkPGON` | confirmacion-agenda (probable desactivación post-cutover) |
| `googleSheetsTriggerOAuth2Api` | `la agencia (@gmail)` | `xjVkf0DxxXJ7sMSa` | outreach-form-meta |
