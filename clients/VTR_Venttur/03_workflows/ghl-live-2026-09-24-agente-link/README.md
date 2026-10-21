# Agente VTR: link de agenda + estado de citas + memoria + tuteo (24/9)

**Disparador:** Mauricio García (Venttur) probó el bot el 23/9 (18:28 CDMX) y tuvo que insistir 4 veces para que le
mandara el link de agenda. Diagnóstico completo con la conversación reconstruida desde GHL: el prompt era
casi igual al de ManyChat; lo que cambió fue el `[ESTADO DEL LEAD]`.

- Su contacto (`uFx22fuKbExjkkUssx37`) venía importado con `agendan_cita = true` y `estado = Cita confirmada`
  (pruebas viejas de Clientify), **sin ninguna cita en GHL**.
- El builder nuevo mandaba `Cita: AGENDADA (no le vuelvas a mandar el link)` en cada turno. El prompt también
  decía "nunca le ofrezcas el link de nuevo". Con eso el bot inventó un "correo de confirmación" y respondió
  que no tenía acceso a la fecha.
- La memoria de ManyChat no se veía (claves `521…` contra `+521…`). N1 lo corrió la agencia recién el 24/9 a las 16:04 UTC, después de la prueba.
- El baseline reproduce el caso de forma literal: gpt-4o con el prompt y el estado viejos da **5/9** y llega a
  contestar "tu cita está agendada para el [inserta aquí la fecha y hora de la cita]"
  (`test-baseline-prompt-y-estado-viejos.txt`).

## Los 4 pasos (main `1eS1Z5k898c3ATnf`, cada uno verificado antes del siguiente)

| Paso | Qué | Script | Verificación |
|---|---|---|---|
| 1 · CITAS-0924 | Nodo nuevo `GHL · Citas (estado)` (GET `/contacts/{id}/appointments`, con `continueRegularOutput`). `Construir estado lead` reescrito con 4 casos: cita futura con fecha · cita pasada · flag sin cita registrada · sin cita. Se sacó "(no le vuelvas a mandar el link)" y volvió "YA ENVIADO y NO agendó todavía" | `batches-2026-09-24/vtr_1_estado_citas.py` (JS en `estado_lead_citas.js`) | Local en Node (5 contactos reales + 7 bordes) · dentro de n8n con workflow temporal de solo lectura · diff pre/post: 1 nodo nuevo, 1 modificado · **4 ejecuciones reales de Daiana en prod** (16:20 UTC) sin error y con la fecha real |
| 2 · REAGENDAR-0924 | Prompt: los 3 casos de cita del bloque · regla absoluta "Reagendar = mandar el link, en el mismo mensaje" · regla absoluta "No inventes nada sobre la cita" · excepción al "no repitas el enlace" · situación "Su cita ya pasó" | `vtr_prompt_deploy.py --paso 2` (`prompt_paso2.py`) | gpt-4o t=0: 9/9 dos veces (baseline 5/9) |
| 3 · N1 + remanente | N1 ya lo había corrido la agencia (24/9 16:04 UTC, 42.521 filas). Se migraron además **57 filas / 12 sesiones** de leads de Form Meta con teléfono sin lada país (`6677474751` → `+5216677474751`), con respaldo en `vtr_sessionkey_backup_0924`. Quedan 86 filas a propósito: 2 sesiones de prueba por Telegram y 4 de jul-2025 con id de ManyChat sin teléfono | `vtr_3_memoria_sin_lada.py` · consultas de solo lectura con `vtr_sql_lectura.py` | Sesión de Mauricio: 228 filas (218 de ManyChat), mismo formato LangChain, ordenadas por id |
| 4 · TUTEO-0924 | Prompt: voseo → tuteo en todas las secciones de la agencia (unas 50 formas, ejemplos incluidos, p. ej. "Vos elegís día y hora" → "Tú eliges día y hora"). Re-escaneo que falla si queda voseo | `vtr_prompt_deploy.py --paso 4` (`prompt_paso4.py`) | 12/12 (link + precio + moneda + una pregunta) sin voseo en ninguna respuesta |

**Final:** `test-final-vivo.txt` corre la suite completa contra el systemMessage leído de n8n después del deploy: **12/12**.
Prompt versionado en `clients/VTR_Venttur/04_agents/agente-venttur-system-prompt-v2.3.md`.
Suite reusable: `python3 batches-2026-09-24/test_agente_link.py --prompt <archivo> [--estado viejo|nuevo]` (sólo llama a OpenAI).

## Rollback

- Workflow: PUT del JSON en `pre/main-pasoN.json` (paso 1 = antes de todo). La cadena de hashes es continua:
  el `pre` de cada paso es el `post` del anterior (ver `sha256.txt`), así que nadie tocó el main entre medio.
- Memoria (remanente del paso 3):
  `UPDATE n8n_chat_histories h SET session_id = b.session_id FROM vtr_sessionkey_backup_0924 b WHERE h.id = b.id;`
  N1: igual con `vtr_sessionkey_backup_0923`.

## Quedó fuera a propósito / cierre

- La descripción de las tools `crear_contacto` y `elevar` dice "Activala" (voseo). Sólo la lee el modelo y no
  llega al lead, así que no se tocó.
- El flag `agendan_cita` de los contactos importados queda como está. El builder ya no depende sólo de él, así
  que un contacto con el flag y sin cita en GHL recibe el link cuando lo pide.
- El workflow one-shot de N1 (`QFNNXILfUM3P9C3c`) quedó borrado el 24/9 (chequeo previo: 0 filas sin `+` en rango 11-15). Se recrea con `--crear` si hiciera falta.
