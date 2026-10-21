# Delta v1.1 → v1.2 — Mapeo material/modelo de Pantuflas

**Fecha:** 2026-05-30
**Base:** [guia-fix-pantuflas-mono-2026-05-30.md](./guia-fix-pantuflas-mono-2026-05-30.md) (v1.1 ya aplicada)
**Disparador:** Test D (multi-producto "pantufla satin + pantufla de moño de satin") cotizó un producto inexistente "Pantuflas Normales Satín × $30". Causa: el árbol v1.1 modelo→material trataba "satín" como material sin asumir que ya implica modelo Mono.

---

## Cambio

Un solo EDIT sobre el system prompt del nodo `AI Agent Recolector` (sigue siendo el mismo nodo). Reemplaza el bloque de Preguntas exactas de la REGLA CRÍTICA por un **Mapeo + Preguntas**, agregando atajos: "pantufla satín/peluche" sin "mono" se interpreta automáticamente como Mono — no se inventa "Pantufla Normal Satín".

### Buscar (texto literal):

```
Si el cliente menciona pantuflas y NO especifica modelo + material, debes preguntar SIEMPRE antes de cotizar y antes de activar CALCULADORA. La pregunta exacta a usar:

- Si dijo solo "pantuflas" / "pantufla": "¿Las prefiere pantuflas normales o pantuflas mono (con moñito)? 😊"
- Si dijo "pantufla mono", "pantufla con moño", "pantufla de moño", "moño" o "moñito": "¿Las prefiere con moño de peluche o con moño de satín? 😊"
```

### Reemplazar por:

```
## Mapeo de lo que dice el cliente → producto

El material (satín / peluche) es una característica EXCLUSIVA de Pantuflas Mono. **NO existen "Pantuflas Normales Satín" ni "Pantuflas Normales Peluche".** Si tu primera reacción es generar uno de esos productos en una cotización, estás equivocada — pará y revisá.

Usá esta tabla para decidir si preguntar o cotizar directo:

| Lo que dijo el cliente | Producto resuelto | Acción |
|---|---|---|
| "pantuflas" / "pantufla" (a secas) | AMBIGUO modelo | Preguntar modelo |
| "pantufla normal" / "pantufla básica" / "pantufla simple" | **Pantuflas** ($30) | Cotizar directo |
| "pantufla mono" / "pantufla con moño" / "pantufla de moño" / "moño" / "moñito" (sin material) | Mono pero AMBIGUO material | Preguntar material |
| "pantufla satín" / "pantuflas satin" (sin "mono" ni "normal") | **Pantuflas Mono Satín** ($30) — porque satín solo aplica a Mono | Cotizar directo |
| "pantufla peluche" (sin "mono" ni "normal") | **Pantuflas Mono Peluche** ($35) | Cotizar directo |
| "pantufla mono satín" / "pantufla con moño de satín" | **Pantuflas Mono Satín** ($30) | Cotizar directo |
| "pantufla mono peluche" / "pantufla con moño de peluche" | **Pantuflas Mono Peluche** ($35) | Cotizar directo |

## Preguntas exactas a usar

- Si dijo solo "pantuflas" / "pantufla": "¿Las prefiere pantuflas normales o pantuflas mono (con moñito)? 😊"
- Si dijo "pantufla mono", "pantufla con moño", "pantufla de moño", "moño" o "moñito" sin material: "¿Las prefiere con moño de peluche o con moño de satín? 😊"
```

---

## Pasos en n8n

1. Abrir `happyflops-main-v2` → nodo `AI Agent Recolector` → `Options > System Message`.
2. Hacer el find/replace de arriba.
3. Save nodo → Save workflow.

---

## Re-verificación

Re-correr el caso D (el que falló):

```
Usuario: 50 pantufla satin + 50 pantufla de moño de satin, CP 88993
Esperado v1.2:
  - 50 Pantuflas Mono Satín × $30 = $1,500
  - 50 Pantuflas Mono Satín × $30 = $1,500  (mismo producto, pero se cotizan en dos líneas porque el cliente lo pidió en dos lotes)
  - O bien, si interpretás que son el mismo producto pedido en una sola entrega: 100 Pantuflas Mono Satín × $30 = $3,000
NO debe: cotizar "Pantuflas Normales Satín" (producto inexistente)
```

> Nota: el "Caso D" original tenía ambigüedad intencional del cliente (dos descripciones distintas para lo que podría ser el mismo producto). Si Oscar quiere que el agente PREGUNTE en este caso ("¿son los mismos 100 pares o dos pedidos distintos?"), eso requeriría una regla extra. Hoy v1.2 los trata como dos líneas distintas siguiendo literal lo que pidió el cliente.

Casos A, B, E ya pasaron en v1.1 — no necesitan re-verificación. Sí conviene re-correr A y B con v1.2 para validar que el mapeo no quebró nada.

---

## Pendiente sin resolver

**Caso C** falló con `Received tool input did not match expected schema` en el nodo `AI Agent Recolector`. Esto NO es un problema del prompt — es un error de la tool CALCULADORA (o de la definición de su schema en el AI Agent).

Necesito el detalle del error (screenshot del execution log de n8n, sección "Error" del nodo) para diagnosticar. Posibles causas:
- El schema de la tool CALCULADORA cambió y ya no acepta el input que el agente arma.
- El agente arma un input con propiedades extra (ej: pasa "producto" como argumento cuando solo espera "cuentas").
- Conflicto con el OutputParser estructurado del nodo.

Cuando me pases el detalle del error C, lo investigo aparte del fix de prompt.
