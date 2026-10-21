# Barrido de cohorte · promesas fantasma de agenda

**Ventana**: aproximadamente los últimos 30–40 días (ids > 41500 en `n8n_chat_histories`, ejecutado 2026-09-16).
**Método**: query sobre `n8n_chat_histories` filtrando turnos AI que combinan verbo de coordinar + referencia temporal + ausencia de URL de whitelist. Los 71 candidatos iniciales pasaron por el mismo detector determinístico del guardrail deployado (Fase 3, 12/12 tests golden), quedando 60 turnos confirmados en 34 sesiones distintas.

## Números clave

- Leads afectados: **34** de 34 tienen registro en Airtable Leads (base `[AIRTABLE_BASE_ID]`).
- Turnos AI con promesa fantasma verificada: **60**.
- Leads con **2 o más** promesas fantasma en el período: **11** (patrón Nahe, la promesa se sostuvo turno a turno).
- Leads que ya habían recibido el link antes del turno con promesa fantasma: **7** (mismo patrón exacto de Nahe: link enviado + regreso pidiendo agendar + AI acepta coordinar en vez de re-enviar link).
- Leads con `Agendan cita = true` en Airtable: **3** (verificar si son citas reales o marcados por otro flujo).
- Leads con `Estado conversación = Contestó`: **3**.

## Distribución por programa

| Programa de interés | Leads afectados |
|---|---|
| No definido | 22 |
| AA Familiar IA | 8 |
| Boarding IA | 2 |
| Pathway IA | 1 |
| Gap Year IA | 1 |

El 65% (22/34) tiene programa sin definir. Es coherente con el hallazgo H5 del reporte de agosto (el clasificador de programa se apaga o queda vacío para muchos leads). El barrido no cambia por el fix de Fase 3 — es una deuda paralela.

## Top 10 casos por severidad

| # | Lead | Programa | Promesas | Link enviado antes | Estado | Extracto textual (1ra promesa) |
|---|---|---|---|---|---|---|
| 1 | Nahe (`5214731005555`) | AA Familiar IA | 8 | ✅ | Contestó | *"Claro, Nahe. Voy a coordinar para que tengas la asesoría el lunes a las 11. Te confirmo el horario lo antes posible. Si tienes ..."* |
| 2 | Silvia (`5216371053824`) | Boarding IA | 6 | ✅ | Conversación interrumpida | *"Entiendo, Silvia. Veo que aún no has agendado la cita. Permíteme coordinar el horario para ti. Voy a verificar la disponibilida..."* |
| 3 | José Manuel (`5217222977774`) | No definido | 4 | ✅ | Cita confirmada | *"Perfecto, Jose. Vamos a coordinar la videollamada con Diego para que puedan explorar todas las opciones disponibles para Valeri..."* |
| 4 | Melina (`5215525645023`) | No definido | 3 | ❌ | Conversación interrumpida | *"Entiendo perfectamente, Melina. Es importante considerar el presupuesto al planificar una experiencia tan significativa. Los in..."* |
| 5 | Juan (`5215517303468`) | AA Familiar IA | 3 | ❌ | Conversación interrumpida | *"Lamento que hayas tenido problemas con el enlace, Juan. No te preocupes, puedo coordinar la cita directamente contigo. ¿Te pare..."* |
| 6 | Ulises (`5214772418706`) | No definido | 3 | ❌ | Conversación interrumpida | *"¡Perfecto, Ulises! Entonces, para tu hijo, además de combinar estudios con trabajo, también es importante que pueda dominar el ..."* |
| 7 | Ale (`5212226621062`) | No definido | 2 | ❌ | Conversación interrumpida | *"Perfecto, Ale. Voy a coordinar la asesoría con Rodrigo para el martes 25. Te enviaré los detalles de la cita a tu correo para q..."* |
| 8 | Brenda (`5215515109333`) | No definido | 2 | ❌ | Conversación interrumpida | *"Entiendo, Brenda. No te preocupes, puedo ayudarte a coordinarlo manualmente. Voy a verificar la disponibilidad para una asesorí..."* |
| 9 | Juan (`5212291520998`) | No definido | 2 | ❌ | Conversación interrumpida | *"Entiendo que quieras tener una visión clara de las opciones disponibles. Los internados en el extranjero ofrecen una variedad d..."* |
| 10 | Graziela (`5215566286912`) | Boarding IA | 2 | ❌ | Conversación interrumpida | *"Eso suena a una oportunidad increíble para tu hija, Graziela. Vivir fuera y conocer otras culturas no solo le dará independenci..."* |

## Interpretación

- **El caso Nahe no fue aislado**. En 30 días de operación bajo el prompt v2.0, aproximadamente 34 leads recibieron al menos una promesa de coordinación de cita que el sistema no podía cumplir.
- **Al menos 7 son casos idénticos al de Nahe**: el bot ya les había enviado el link, ellos volvieron pidiendo agendar por chat, y el bot aceptó coordinar en vez de re-enviarles el link.
- **11 leads recibieron múltiples promesas**, no una sola — es decir, el patrón se sostuvo durante toda su conversación con el bot, no fue un desliz aislado.
- La sesión de Nahe (id_2 `5214731005555`) es la más severa del período, con 8 promesas fantasma. Silvia (`5216371053824`) sigue con 6, y Jose con 4.
- **A partir del 2026-09-16 14:49 UTC** (deploy de Fase 3), este patrón dejó de generarse: prompt v2.1 + guardrail estructural cortan el flujo antes de que llegue al lead.

## Archivo asociado

El detalle registro-por-registro está en `06_docs/barrido-leads-promesa-fantasma-2026-09-16.csv` (34 filas, 19 columnas), con `id_2`, teléfono, nombre, programa, fuente, estado, contadores y extracto del primer turno con promesa.

## Limitaciones del barrido

- La ventana es aproximada: `id > 41500` en `n8n_chat_histories`, estimada por rate de crecimiento (~80 msgs/día) sobre el rango observado. La tabla no tiene columna `created_at`, así que un dato exacto requeriría cruzar con `n8n_executions_entity` — no necesario para el objetivo del barrido.
- El detector opera sobre el texto que el modelo generó. No captura promesas fantasma que se hayan formulado sin verbo explícito de coordinación (edge case improbable, no observado en la muestra manual).
- El barrido no cubre leads que hayan sido eliminados de Airtable después del turno con promesa. Los 34 encontrados tenían todos registro vivo al 2026-09-16 15:15 UTC.
- El barrido no distingue entre casos donde el lead **notó** la falta de la cita y casos donde nunca volvió después de la promesa. Un cruce con `Última actividad` puede sugerirlo pero no es concluyente.

## Anexo · queries reproducibles

Query Postgres (regex simplificado):

```sql
SELECT session_id, id, message::text AS message
FROM n8n_chat_histories
WHERE (message::jsonb->>'type') = 'ai'
  AND id > 41500
  AND (message::jsonb->>'content') !~* 'promo\.venttur\.com/'
  AND (message::jsonb->>'content') ~* '(coordin\w+|program\w+\s+la\s+llamada|quedamos|nos\s+vemos|te\s+llamo|te\s+llamamos|te\s+contact\w+|te\s+aviso|te\s+confirmo|te\s+ap[aá]rt\w+|reserv\w+|agend\w+)'
  AND (message::jsonb->>'content') ~* '(a\s+las\s+\d|ma[ñn]ana|hoy|(el\s+)?(lunes|martes|mi[eé]rcoles|jueves|viernes|s[aá]bado|domingo)|esta\s+semana|pr[oó]xima\s+semana)'
ORDER BY id;
```

Post-filtrado con el detector preciso: `03_workflows/vivo-2026-09-16-post-fix-prompt-guardrail/detectar-promesa-fantasma.js` (misma lógica que el nodo deployado). Devuelve `_phantom_promise_intercepted: true` si aplica.
