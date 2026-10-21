# Base congelada — instancia de agencia (2026-08-06)

> ## ⚠️ ESTO NO ES LA FUENTE DE VERDAD — corregido el 2026-08-06
>
> Este export es de la instancia **`[TU-INSTANCIA-N8N]`** (agencia). **No es el bot de producción.**
>
> El bot productivo de Happy Flops corre en **otra instancia** y su grafo corresponde a la
> arquitectura de **`happyflops-main-v3.json`** (salesbots: `POST /api/v2/salesbot/run` + campo
> `1099420` + columna `bot_id` de Airtable), con `la agencia`, `Call 'Kommo Salesbot Text Capture Runner v1'`
> e `If25` **con sus dos salidas cableadas a `Get_Contact`** — confirmado contra la UI por el usuario.
>
> Lo que hay acá (`M0sEgp7mp27d8uIM`, 250 nodos, arquitectura de envío directo por amojo) es una
> **copia vieja abandonada** que sigue suscrita al webhook de Kommo y descarta todo lo que le llega
> — por eso sus ~40 ejecuciones por minuto duran 30 ms y mueren en `If25`. Ese sí está muerto,
> pero es un duplicado, no el bot.
>
> **Pendiente:** re-congelar contra la instancia correcta (hace falta su API key) y reemplazar
> este directorio. Hasta entonces, **no derivar contratos de acá.**
>
> Hallazgo colateral que sí importa: **Kommo tiene una suscripción de webhook de más**, apuntando
> a esta copia. Es inofensiva hoy, pero conviene darla de baja para no volver a confundir cuál es
> cuál.

**Exportado read-only vía `GET`**; ningún workflow fue modificado (Regla 0 del plan).

Regenerar / verificar drift:

```bash
python3 scripts/utilities/hpf-congelar-base.py --verificar
```

## Contenido — 7 workflows, 395 nodos

| Archivo | n8n id | nodos | active | rol |
|---|---|---|---|---|
| `main-happy-flops.json` | `M0sEgp7mp27d8uIM` | 250 | ✅ | main, webhook `7b45828c-d3e0-4d84-bedb-1dec9eab02aa` |
| `seg-rebeca.json` | `ZDJGftMdj63i0MZT` | 34 | — | reenganche post-saludo |
| `seg-imagen.json` | `QHmfLP4JmZOFT3KZ` | 38 | — | reenganche post-evento + CF 1099424 |
| `seg-cotizacion.json` | `JcjKsXNnnjaC3IoV` | 45 | — | reenganche post-fichas + clasificador de desinterés |
| `seg-7pasos.json` | `nkRBXbc4G0Cn67gY` | 20 | — | ola única 24 h, sólo mueve etapa |
| `atencion-personalizada.json` | `Fhp5ErGAegOAYrJX` | 3 | — | Telegram + PATCH etapa |
| `tool-calculadora.json` | `kJVHc3WjpIPwRED7` | 5 | — | CALCULADORA (envío + empaque) |

`BASELINE.json` guarda `versionId`, `updatedAt` y `sha256` de cada uno. El `sha256` se calcula
sobre `{name, nodes, connections, settings}` — ignora metadatos volátiles.

---

## La copia de agencia sí está muerta (pero es una copia)

Este duplicado está `active: true` y recibe webhooks de Kommo, pero ninguna ejecución llega a
contestar: son **dos compuertas mutuamente excluyentes** que ningún mensaje puede atravesar.
Es la huella de que quedó abandonado, no un problema del bot real.

```
New_Message ──▶ If25  ($json.body["message[add][0][entity_id]"] == "8075544")
                 ├─ out0 TRUE  ──▶ Get_Contact ──▶ … ──▶ Get_Entity ──▶ If24
                 └─ out1 FALSE ──▶ (sin conectar)          │
                                                            │
                        If24  (mismo entity_id == "8075544")│
                         ├─ out0 TRUE  ──▶ (sin conectar) ◀─┘
                         └─ out1 FALSE ──▶ No es IA ──▶ … (los otros 190 nodos)
```

- **Lead ≠ 8075544** (todo el tráfico real) → muere en `If25`.
- **Lead = 8075544** (el de prueba) → pasa `If25`, y muere en `If24`.

**Ningún valor de `entity_id` satisface las dos condiciones.** El grafo tiene 192 nodos cableados
aguas abajo que hoy son inalcanzables.

**Evidencia:** 40 ejecuciones consecutivas del 2026-08-06 (17:41–17:46 UTC), todas entre 0.025 s y
0.082 s, ninguna por encima de 2 s.

### Contraste con el flujo productivo

En los tres snapshots del repo (`happyflops-main-v1/v2/v3.json`) `If25` tiene **las dos salidas
cableadas a `Get_Contact`** — es un passthrough vestigial — e `If24` es un nodo distinto
(`$json.output contains "👼🏢"`, el ruteo del saludo). Es decir, las dos compuertas de arriba son un
**kill switch agregado después**, no lógica de negocio.

En el flujo productivo `If25` es passthrough y `If24` es el ruteo del saludo. Confirmado por el
usuario: **`No es IA` es el primer gate real, y los 4 nodos previos son funcionales.** La migración
replica esa semántica:

| Nodo | En vivo hoy | Semántica objetivo |
|---|---|---|
| `If25` | gate `entity_id == 8075544`, rama FALSE muerta | **passthrough** — todo pasa a `Get_Contact` |
| `If24` | gate `entity_id == 8075544`, rama TRUE muerta | **passthrough** — todo pasa a `No es IA` |

El primer filtro real de negocio es `No es IA` (descarta leads fuera del pipeline `11622596`).

> **Regla 0:** el kill switch **no se toca**. Esto se documenta y se reporta; restaurarlo o no es
> decisión del cliente.

---

## Otras divergencias entre este export y el repo

1. **`happyflops-main-v3.json` SÍ corresponde al flujo productivo** (arquitectura de salesbots).
   Su id `pYtiBlhOTr7HVPmr` da 404 en la instancia de agencia porque vive en otra. Esta copia usa
   la API interna de amojo (`ajax/v1/chats/session` → `amojo.kommo.com/v2/{chat}/sendMessage`) con
   la columna `CURL` — es la arquitectura **anterior**, previa al pasaje a salesbots.
2. **La CALCULADORA de esta copia es la vieja, sin mínimos** (`Code1`, 10.816 chars). No confundir
   con la de producción: ahí el trigger va a `Code2` (14.318 chars) y **sí tiene** `MIN_BY_PRODUCT`
   y `MINIMO_NO_ALCANZADO`. El fix del 2026-07-15 sí está deployado — ver
   [`../base-prod-2026-08-06/README.md`](../base-prod-2026-08-06/README.md) §2.
3. **Hay al menos tres juegos de ids para los mismos sub-workflows** (p. ej. `ATENCION_PERSONALIZADA`:
   repo `SUgT7UPYyQ3NDgRp`, esta copia `Fhp5ErGAegOAYrJX`, y el de la instancia productiva sin
   determinar). **Ninguno de los de este directorio sirve para la migración** — hay que releerlos
   de la instancia correcta. Los sub-workflows congelados acá son los que llama la copia vieja,
   no necesariamente los que llama el bot real.
