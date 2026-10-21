# PARKING — lo que quedó fuera de alcance, con su razón

El protocolo lo pide explícito: *"cualquier mejora que no sea el fix mínimo de una familia enumerada
va a `PARKING.md`"*. Esto no es un backlog aspiracional: es la lista de lo que **conscientemente no se
está midiendo**, para que nadie lea el resultado como si cubriera más de lo que cubre.

---

## Aristas de la Matriz B sin caso (8 de 34)

| # | Arista | Por qué no |
|---|---|---|
| PARKING-01 | `Es Stage Pausado?[true]` | Requiere poner una opportunity de GHL en un stage pausado. Se puede, pero contamina el contacto de prueba y no toca ninguna familia S1 |
| PARKING-02 | `Es Origen Telegram? (Pago)[false]` | Rama de pago por GHL. Depende de `HPF-CAN-025` (rama GHL) primero |
| PARKING-03 | `If[true]` y `If[false]` (comando `/b`) | Solo alcanzable desde `Telegram Trigger`. El webhook no pasa por ese `If` — verificado en las conexiones del build |
| PARKING-04 | `¿Media de Telegram?[true]` | Requiere `telegram_file_id`, que solo produce el trigger nativo de Telegram, no el webhook |
| PARKING-05 | `¿Audio de Telegram?[true]` | Idem PARKING-04 |
| PARKING-06 | `¿Es test?[true]` | Es el **nivel C** del protocolo: output crudo del LLM salteando el Sanitize y los 7 emisores. Prohibido como gate. Se deja sin cubrir a propósito |

## Celdas de la Matriz A sin caso P0

| # | Qué | Por qué |
|---|---|---|
| PARKING-07 | ~4 celdas imposibles del embudo (ej. `comprobante` en el paso `saludo`) | El embudo no las produce. Grado `JUICIO`, fuera del set contable |
| PARKING-08 | El grueso de `Otros` y `Boda` más allá de los 6 casos asignados | La Fase 4 las cubre al 100 %. En P0 entran solo las que ejercen el gate de evento |

## Verbatim que no se mide en P0

| # | Qué | Por qué |
|---|---|---|
| PARKING-09 | Fichas de accesorios: `tapas`, `bolsa_shein`, `correa15`, `correa9`, `tintas`, `cuentas` | Todas S3. **Regla de secuencia del protocolo:** no se toca ninguna fila S3 mientras quede un S1 o S2 abierto |
| PARKING-10 | Las 5 frases de mandiles | Idem, y su fuente es el v18, no el CSV |

## Defectos del build detectados y no arreglados en esta fase

| # | Qué | Por qué |
|---|---|---|
| PARKING-11 | `Send a text message` lee su `chatId` de `$('Telegram Trigger')`, que no existe cuando se entra por el webhook | **Arista muerta por construcción.** Ningún test la puede alcanzar. Va a la entrega como *"NO VERIFICADO — arista defectuosa"*, no como cobertura faltante |
| PARKING-12 | Los 7 emisores tienen `onError: continueRegularOutput` **y** `retryOnFail: true` | Es la causa estructural del verde falso. El runner lo compensa leyendo el acuse; cambiarlo es una decisión de diseño del workflow, no del testing |
| PARKING-13 | 127 memos de campañas de test viejas dentro del `staticData` del workflow vivo | Limpiarlo requiere escritura sobre el workflow de producción. Se declara y se mide su efecto (`depende_de_memo` → 3 corridas) |

## Fuera del protocolo entero

| # | Qué | Por qué |
|---|---|---|
| PARKING-14 | **Los reactivadores.** 41 de los 146 salesbots del original + 4 sub-workflows n8n (131 nodos), cadencia 1h→3h→8h→24h. El nuevo tiene **cero** | Es el **28 % de la superficie de conducta** del original. No es un problema de prompt y no se arregla con este protocolo. **Va explícito en la entrega**: si Oscar dice que el bot nuevo vende menos, esta puede ser la razón principal |
