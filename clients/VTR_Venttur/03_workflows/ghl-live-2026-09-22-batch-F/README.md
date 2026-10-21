# Batch F · Post-cutover activations · 2026-09-22

Aplicado por Codex el 2026-09-22 04:00 UTC.

## F.2 · Reconciliar sessionKey `+` / sin-`+` ✅

**Contexto:** El staging (`3sLd7KY3o8I7NvXi`) y `main-venttur-ghl` usan `canonPhone()` que devuelve teléfono con `+` (formato `+521<10>`). El rescate y despachador usaban `nsk()` que devuelve sin `+` (formato `521<10>`). Consecuencia: las sesiones que un flujo escribe con `+` no las lee el otro sin `+` → memoria del agente se rompe cross-workflow.

**Fix (default D5 con `+`):** patch quirúrgico donde se **asigna** `session_key` (no en la función `nsk()` que puede usarse en otros contextos).

### Rescate GHL `YB0UxwEVwzISdd54`

- Nodo `Code: Fase 1 (GHL)`: `const session_key = nsk(phone);` → `const session_key = '+' + nsk(phone);`
- Nodo `Code: Fase 2 (GHL)`: idem.

### Despachador `vrShEXQGGAo4FqAt`

- Nodo `Seleccionar (tope-2 + prioridad)`: `session_key: nsk(c.phone)` → `session_key: '+' + nsk(c.phone)`

Ambos workflows quedan OFF (mismo estado pre-batch). Se activan en CUTOVER-2 / POST-2/3.

**Snapshots post-fix:**

| Workflow | ID | sha256 |
|---|---|---|
| `rescate-ghl.json` | `YB0UxwEVwzISdd54` | `1c4a74c317a5258bd4e88fa6320d5db91444d65ec52ed6608534d7a8db18bb1e` |
| `despachador.json` | `vrShEXQGGAo4FqAt` | `42c45ad8b036e4db6f5886d10c023dd57ba71d79752347c16072e16731a7316f` |

Snapshots pre-fix en `pre/`.

## F.1 · Cablear templateId por programa en despachador ✅ APLICADO (2026-09-22)

Camilo pasó los 6 `templateId` el 2026-09-22 (§PAR-B cerrado). Cableado en el despachador `vrShEXQGGAo4FqAt`:

**Mapping programa → templateId** (custom field GHL `programa_interes` = `xK2NFqtz1DYUw3gYdn8I`):

| Programa (variantes) | templateId |
|---|---|
| Boarding School / Internados / Boarding IA | `6aa1b033c99a8adae9721464` |
| AA Familia / AA Familiar IA / Intercambio | `6aa1b0323e3fe07bce43d4ab` |
| Summer Camp / Campamentos / Summer Camp IA | `6aa1b03145d5045847ef9762` |
| Pathway / Pathway Alemania / Pathway IA | `6aa1b033a3ed42683a182e66` |
| Estudio y Trabajo / Estudia y Trabaja | `6aa1b032a3ed42683a182e5c` |
| Gap Year / Gap Year IA / "Hapy Year" (typo confirmado por la agencia 2026-09-22) | `6aa1b0309686d7ff49f76c20` |

**Cambios en el workflow:**

1. Nodo `Seleccionar (tope-2 + prioridad)`: agregada constante `PROGRAMA_FIELD = 'xK2NFqtz1DYUw3gYdn8I'` + mapping `TEMPLATE_BY_PROGRAMA` + función `resolveTemplate(programa)`. `mk()` ahora lee `programa` del contact y resuelve `templateId`. Si no matchea (programas huérfanos D7: Viajes/Ed.Superior/Idiomas), `templateId = null`.
2. Nuevo nodo IF `Tiene templateId?` insertado entre `Seleccionar` y `Enviar template`. Rama true (con template) → envía; rama false (huérfano) → skip silencioso.
3. Nodo `Enviar template GHL (PLACEHOLDER)` → renombrado a `Enviar template GHL` · `jsonBody` cambió de `templateId: "PENDIENTE_B-07"` (hardcoded) a `templateId: {{ $json.templateId }}` (expresión).

**Snapshot post-F.1:** `post/despachador.json` · sha256 `0ac0192a60899eec6aadc56c75b18dab5caeaddf4a8ae2fa2a75fdc05fa4a3fe` · workflow queda OFF hasta CUTOVER-2.

**"Hapy Year" = Gap Year** (typo confirmado por la agencia 2026-09-22). El mapping cubre las variantes `hapy year`, `happy year`, `gap year`, `gap year ia`, `gap year / estudia y trabaja` → mismo templateId `6aa1b0309686d7ff49f76c20`.

## F.3 · Rotar credencial ManyChat n8n `9OZtsIsmuVEG9l6R` · Post-cutover

Opcional, manual (la agencia en n8n UI). Una vez que ManyChat sea legacy (post watch-mode 4-5 días), rotar el token para dejar de exponer la credencial.

No aplicable durante esta sesión (requiere acción UI + espera watch-mode).

## Scripts fuente

`scratchpad/vtr_batch_f_investigate.py` — descarga workflows + diagnóstico.
`scratchpad/vtr_batch_f_sessionkey.py` — aplicación del fix D5.
