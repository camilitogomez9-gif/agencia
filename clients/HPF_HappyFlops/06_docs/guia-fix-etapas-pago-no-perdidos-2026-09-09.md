# HPF · Leads en etapa de pago no deben ir a Ventas Perdidos — 2026-09-09

## Disparador

Oscar reportó que un lead que ya había pagado (movido a **PAGO SIN DISEÑO** el 2026-09-08 9:21)
fue movido solo a **Ventas Perdidos** el mismo día 18:35, por la automatización ("IA · la agencia |
Contabo"). Regla de Oscar: en etapas de pago el agente **no hace nada** salvo vigilar pagos entrantes
y moverlos a Confirmar Pago / Pago Liquidación.

## Investigación — hallazgos (importante, corrige supuestos del CLAUDE.md)

Rastreando las **ejecuciones reales** de n8n (no solo el código), en las dos instancias:

1. **El único nodo de n8n que setea Ventas Perdidos (`status_id 143`) es `PERDIDOS1`**, presente en las
   4 cadencias de seguimiento (Rebeca/Cotización/7 pasos/Imagen), en ambas instancias. Ningún main
   mueve a 143 (solo a Confirmar Pago `91450360`, AP `91266100`, Pago Liquidación `100395523`).
2. **`PERDIDOS1` no disparó en el incidente** — 0 ejecuciones en toda la ventana retenida (~24 h) que
   cubre las 18:35 del 2026-09-08 en cualquier huso, en **devn8n** y en **agencia**. Las cadencias de
   la instancia de agencia tienen **0 ejecuciones totales** (código muerto).
3. **Hay DOS `[Happy Flops]` vivos** apuntando al mismo Kommo `happyflopss`:
   `pYtiBlhOTr7HVPmr` (devn8n, producción) **y** `M0sEgp7mp27d8uIM` (agencia). El de agencia,
   que el CLAUDE.md daba por "copia vieja abandonada que descarta todo", **corrió 1.240 veces solo el
   2026-09-09**. No está abandonado. ⚠️ Revisar posible doble procesamiento.
4. **n8n purga ejecuciones muy rápido** (~24 h en las cadencias; se vieron 404 a los ~20 min). El
   incidente del 2026-09-08 ya no es trazable desde los logs.

**Conclusión:** ninguna ejecución de n8n marcó a este lead como Perdidos vía PATCH. El patrón que
encaja: **un Salesbot de Kommo (que n8n dispara vía `salesbot/run`) hace el move de etapa adentro de
Kommo**. Por eso "es n8n" (n8n lo gatilla) pero no aparece como PATCH en las ejecuciones. Ese Salesbot
no mira la etapa actual → pisa leads que ya pagaron. **Pendiente: la agencia revisa los Salesbots de Kommo.**

## Lo que se aplicó (devn8n, producción) — 2026-09-09

Guarda de etapa antes de cada `PERDIDOS1`, en las 4 cadencias de devn8n. Aunque la evidencia dice que
`PERDIDOS1` hoy no es el mover, es un hueco real y la guarda es correcta, reversible y no rompe nada.

**Por cadencia**, se insertó entre el feeder y `PERDIDOS1`:
`feeder → [Chequear etapa (guarda pago)] → [Filtrar etapa protegida] → PERDIDOS1`

- `Chequear etapa (guarda pago)`: HTTP GET `…/api/v4/leads/{{entity_id}}` (cred `H.F`, misma expresión
  de entity_id que `PERDIDOS1`).
- `Filtrar etapa protegida`: Code que lee el `status_id` actual y **corta** (no marca Perdidos) si el
  lead está en una etapa protegida. **Fail-closed**: si no puede leer la etapa, tampoco marca.

**Etapas protegidas (todo lo pagado / en curso):** `91450360` Confirmar Pago · `89263352` Pago sin
diseño · `91246120` Diseño · `100395519` En producción · `100395523` Pago Liquidación · `142` Ganado.

Feeders por cadencia: Rebeca `If3[0]` · Cotización `If4[1]` · 7 pasos `If2[1]` · Imagen `If10[0]`
(Imagen ya tenía whitelist ETAPA 1; se sumó igual por defensa en profundidad). El literal roto
`=100395519` del `If2` de 7 pasos queda inocuo: siempre rutea a la guarda nueva, que cubre En Producción.

**Verificación:** cableado releído del vivo (feeder→GET→Code→PERDIDOS1, PERDIDOS1 ya no colgado del
feeder) + 12 casos unitarios del filtro en Node (6 protegidas cortan, ETAPA 1/3 pasan, string/wrapped
`.data`/desconocida OK). Todo verde.

## Script y rollback

- Script reproducible: `scripts/utilities/hpf-guarda-etapa-perdidos.py` (`--apply` para escribir; sin
  flag es dry-run). Sanea `settings` (la API de devn8n rechaza `binaryMode`/`availableInMCP`).
- Snapshots de rollback (con sha256): `clients/HPF_HappyFlops/03_workflows/kommo-live-2026-09-09-pre-guarda-perdidos/`
  (los 4 workflows tal cual estaban antes). Restaurar = `PUT /api/v1/workflows/<id>` con
  `{name,nodes,connections,settings}` del snapshot (saneando settings).

## Pendiente / próximo

1. **la agencia revisa los Salesbots de Kommo** — buscar el que mueve a Ventas Perdidos por inactividad y
   agregarle condición de etapa (saltear las etapas de pago), o que n8n no lo dispare para esas etapas.
   **Ese es probablemente el fix que frena ESTE caso.**
2. Nivel 2/3 ("que no mande toques" / "silencio total" en etapas de pago) — pendiente de decisión de
   Oscar (la agencia consulta).
3. Aparte: resolver los **dos `[Happy Flops]` vivos** sobre el mismo Kommo.
