# Fix cobertura de assets de pantuflas — 2026-08-26

**Disparador**: feedback de Oscar (26/8, WhatsApp) tras probar el bot nuevo por Telegram:

> - El único que mandó bien fue los cilindros
> - La pantufla cerrada mandó la infografía, no mandó el catálogo y el video la mandó hasta el último
> - No mandó el video de las de peluche
> - No mandó el catálogo de moño satín

## Diagnóstico

Los 3 síntomas (peluche sin video, cerrada/satín sin catálogo) comparten causa: el nodo
`Leer canónicos` de **W6** decidía qué assets mandar **filtrando según lo que emitía el
LLM** (`Products`), que es inconsistente turno a turno. Cuando el LLM emitía el término
específico (`pantuflas mono satin`), el filtro descartaba el término genérico `pantuflas`
→ el `LIKE` de W3 sólo matcheaba la ficha específica → se perdían el catálogo y/o el video.
Por eso a Oscar a veces le llegaba completo y a veces no (variance del LLM).

- **Cilindros** funcionaba bien porque no tiene lógica de material/filtrado.
- **Peluche**: el filtro dejaba sólo la ficha específica, sin el video general.
- **Satín / cerrada**: cuando el LLM emitía el específico, se perdía el catálogo (PDF).

Verificado con smoke real: pre-fix, `pantufla mono peluche` → 1 solo adjunto (ficha, sin video).

## Fix (W6 · nodo `Leer canónicos`)

Se reescribió el sub-bloque de branching de pantuflas para que decida por el **TEXTO del
lead** (determinístico), no por lo que emite el LLM:

- **Peluche** (`/peluche/` en el texto) → ficha de peluche + `pantuflas video`, **sin
  catálogo** (el catálogo es de diseños de satín, no aplica a peluche).
- **Satín / normal / cerrada** (cualquier otra mención de pantufla o material) → se garantiza
  el término genérico `pantuflas` → surtido completo con catálogo. El `EXISTS` de W3 deduplica.

Condición de activación: `_mencionaPantufla || _pidioMaterial` (cubre tanto "pantuflas
normales" como el short-form "la de peluche"/"de satín"). NO toca R10 (arrastre), ni la
lectura de productos, ni ningún otro producto (cilindros/sandalias/etc sin cambio).

Parche: `03_workflows/parches-2026-08-26/w6-cobertura-pantuflas-peluche-satin.json`.

## Verificación (3 capas)

1. **Unit test del branching** (`scratchpad/unit-test-branching.mjs`): **10/10**, probando
   los 3 caminos posibles de emisión del LLM (genérico / específico / ambos) × 3 intenciones
   (peluche / satín / normal-cerrada), **incluido el camino malo de Oscar** (LLM emite sólo el
   específico) → ahora siempre resuelve el catálogo.
2. **Smoke E2E contra W6 vivo** (8 casos): peluche → ficha + video (2 adjuntos); satín/normal
   → infografía + catálogo PDF + ficha + video (5 adjuntos), video al final; cilindros sin
   cambio (3 adjuntos).
3. **Entrega por Telegram (W2)**: verificado que el ruteo por extensión manda `.pdf` →
   `TG · documento` y `.mp4` → `TG · video`, ambos con param `file` correcto. Ejecuciones
   reales (`1184440`, `1177562`) muestran `TG · documento` entregando PDFs y `TG · video`
   entregando mp4s con `tg.ok=True` — la entrega funciona de punta a punta.

## Alcance

Snapshot post-fix: `03_workflows/ghl-live-2026-08-26-cobertura-pantuflas/`. Diff funcional
vs `ghl-live-2026-08-25-post-fix-c4`: **sólo W6** cambió por este fix. (W1 aparece también
como cambiado, pero por una edición externa no relacionada del 25/8 14:54 — ver nota abajo.)

## Nota sobre extra-fichas (no bloqueante)

Para un pedido de "cerrada/normal", el bot muestra las 2 fichas de moño (peluche + satín)
además de infografía + catálogo + video, porque el término genérico `pantuflas` matchea
todas. Oscar no se quejó de fichas de más (sólo de assets faltantes), y es el mismo
comportamiento del pedido genérico. Si más adelante quiere afinar a "sólo lo de cerrada",
es un ajuste menor aparte (requiere enumerar términos por evento, mayor superficie).

## ⚠ Hallazgo colateral — edición externa de W1 (25/8 14:54, NO de esta sesión)

Al tomar el snapshot detecté que W1 fue editado el **2026-08-25T14:54:29** por alguien que
no soy yo (yo hoy sólo toqué W6). n8n despojó params de 2 nodos:

- `Debounce · esperar`: se quitó `"unit": "seconds"` → queda sin unit (default del nodo).
- `TG · bajar archivo`: se quitó `"operation": "get"` y `"download": true`, se agregó `"additionalFields": {}`.

**Evaluación**: casi seguro es normalización automática de n8n al abrir+guardar el workflow
en la UI (los 3 valores despojados son los defaults de n8n, y n8n omite params que igualan el
default). Comportamiento **probablemente idéntico**. PERO: `TG · bajar archivo` (descarga de
notas de voz) **no corrió en ninguna ejecución posterior al cambio**, así que el descargador
quedó sin ejercitar desde entonces. El audio de la agencia funcionó ANTES de este cambio.

**Recomendación**: antes de mandar a Oscar, (a) mandar 1 nota de voz de prueba por Telegram
para confirmar el descargador, o (b) restaurar la config explícita conocida-buena con
`scratchpad/hpf-restore-w1-nodes.py --apply` (revierte a `unit:seconds` + `download:true` +
`operation:get`, la config verificada funcionando). Restore listo, no aplicado — decisión de la agencia.

**✅ RESUELTO (26/8)**: la agencia mandó una nota de voz de prueba. La ejecución `1185020` de W1
confirma el pipeline de audio completo con la config normalizada: `TG · bajar archivo` bajó
el binario (audio/ogg, 14.2 kB), subió a GHL, `Transcribir audio` devolvió «prueba 1,2,3»,
`Evaluar estado` dio `ruta=seguir` (no bloqueado), y llegó a `W6 · conversación` + `W2 · enviar`.
Confirmado empíricamente que la normalización de n8n fue **cosmética** (los valores despojados
eran los defaults del nodo). **No se restauró nada — no hace falta.**
