# Snapshot staging pre-replica del guardrail Nahe · 2026-09-16 (Bloque 0 del plan de sincronización)

Estado del workflow **`3sLd7KY3o8I7NvXi` [Venttur] GHL staging (Telegram test)** inmediatamente **antes** de replicarle el fix Nahe. Este es el estado que dejó Camilo el 2026-09-12 (última modificación registrada).

## Estado

- workflow id: `3sLd7KY3o8I7NvXi`
- nombre: `[Venttur] GHL staging (Telegram test)`
- nodos: 12
- active: **true**
- updatedAt: `2026-09-12T00:06:21.000Z`
- versionId pre: `aa2f427f-9c83-4efd-8e7f-65d8a42b9a91`

## Topología

```
Telegram Trigger → Normalizar payload → Buscar Contact GHL → Construir estado lead → Agente IA WPP → Enviar Telegram
                                                                                       ↑
                                                                    OpenAI Chat Model
                                                                    Postgres Chat Memory
                                                                    crear_contacto, elevar, cerrar_conversacion (tools)
```

## Bug reproducible en este snapshot

El systemMessage del `Agente IA WPP` tiene **47.462 chars** y contiene las dos instrucciones catastróficas del prompt v2.0 pre-Nahe:

1. Bloque `[ESTADO DEL LEAD]` (~línea 754): *"reconocé que ya se lo mandaste, preguntá qué lo detuvo y **ofrecé coordinar el horario a mano**"*.
2. Sección `Ya le mandaste el link y no agendó`: *"dime qué día te viene bien y **lo coordino contigo directo**"*.

Camilo construyó el staging antes del 15/9 (incidente Nahe). El prompt del staging es el mismo del vivo pre-fix + adaptaciones GHL (tools `crear_contacto` con `POST /contacts/upsert`, `elevar` con `PUT /contacts/{id}`, `cerrar_conversacion` nueva, context builder que lee del Contact de GHL). No incluye la Regla ABSOLUTA #8 "No agendo yo" ni el guardrail estructural del vivo del 16/9.

Si el cutover 18-19/9 se hace desde este estado, Nahe se repite en GHL — el agente aceptará coordinar citas por chat sin tener tool de calendar.

## SHA256

```
4103e04a6a183561e7c00e3b8d1f3677f5c36ed23fb7903ee9a892df800fe8f5  main-venttur-staging.json
```

## Rollback

`PUT /api/v1/workflows/3sLd7KY3o8I7NvXi` con este JSON (payload minimal `{name, nodes, connections, settings}`) restaura el staging al estado pre-fix.

## Post-fix

Ver `staging-2026-09-16-post-replica-guardrail/` (13 nodos, con el nodo Code `Detectar promesa fantasma` insertado entre `Agente IA WPP` y `Enviar Telegram` + Regla #8 en el prompt).
