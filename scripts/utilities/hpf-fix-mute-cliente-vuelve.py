#!/usr/bin/env python3
"""
HPF · el cliente que vuelve deja de recibir respuesta del bot (paridad con Kommo).

EL PROBLEMA
Hoy, un lead cuya oportunidad está en `Ganado` o `Ventas Perdidas` y vuelve a escribir
**recibe respuesta del agente**. En el bot original de Kommo no la recibía.

Ruta exacta del original (`base-prod-2026-08-06/main-happy-flops.json`):

    Get_Entity → … → If20 (OR sobre 91266100, 92033296…92033312, "143")
       → checkType1 → Code (parsea status_id) → Si está en perdidos
       → Usr. Envia Imágenes/Documentos7   [Telegram, chat -4925599962]

`Si está en perdidos` tiene UNA sola salida y es el nodo de Telegram: "👤 El Lead:
{entity_id} esta en *Ventas Perdidos* y envió un mensaje". No hay PATCH de etapa después,
ni limpieza, ni nada — el lead se revivía A MANO. Oscar lo describió como parte de su
operación diaria en la reunión del 9/5: "Rebeca contesta ~50 mensajes diarios de leads en
'ventas perdidas' que escriben de vuelta".

Para `142` (Ganado) el original no tenía gate: la rama `If5` out1 quedó sin conectar, así
que era silencio total sin alerta. Eso es un agujero, no un diseño, y acá se corrige:
ambas etapas alertan.

POR QUÉ NO PASA HOY
`Evaluar estado` tiene el comportamiento bien traducido — `'Ganado'` y `'Ventas Perdidas'`
están en el mapa `BLOQUEO`, con los comentarios `// Kommo 142` y `// Kommo 143` — pero el
orden de precedencia lo anula:

    const vuelve = via === 'existente' && ['Ganado','Ventas Perdidas'].includes(etapaNombre);
    let ruta = 'seguir';
    if (vuelve) ruta = 'cliente_vuelve';   // ← gana
    else if (motivo) ruta = 'bloqueado';   // ← nunca se alcanza para esas dos etapas

y la salida `cliente_vuelve` del Switch va a un NoOp que es pass-through hacia el debounce.

EL FIX, Y POR QUÉ ES DE CABLEADO
**No se toca el jsCode de `Evaluar estado`.** Ocho nodos lo referencian por nombre
(`Debounce · esperar`, `Debounce · leer`, `¿Soy el último?`, `Descargar audio`,
`W2 · enviar`, `Decidir etapa`, `Evidencia del turno`, `Decidir seguimiento`), así que
cualquier cambio en lo que emite se propaga a todos. Y no hace falta: la ruta
`cliente_vuelve` ya aísla exactamente el caso que necesita alerta. Alcanza con recablearla.

    bloqueado      (En Espera, Pago Confirmado, En Producción) → Fin · agente en silencio
    cliente_vuelve (Ganado, Ventas Perdidas)                   → Telegram, y termina
    seguir         (resto)                                     → Debounce · push

POR QUÉ NO SE INSERTA NADA ANTES DE `Debounce · push`
Ese nodo Redis usa `$json` crudo (`'hpf:' + $json.contactId` y `$json.messageId`). Hoy le
llega el item de `Evaluar estado` intacto porque el NoOp es pass-through. Un nodo
intermedio que no propague esos dos campos rompería el debounce SOLO para esta rama — por
ejemplo un executeWorkflow hacia W0, que devuelve {ok, op, http_status, via, data, error}.
Acá la rama termina antes del debounce, así que el problema no existe.

EFECTO COLATERAL, A FAVOR
Estos leads dejan de llegar a `Marcar actividad`, que corría en todos los turnos sin IF y
hacía upsert sobre `hpf_seguimientos` con `cerrado_at = NULL` — reabriendo la fila cerrada
del pedido anterior para que W10 la levantara y la volviera a cerrar en cada ciclo.

RÁFAGA
Tres mensajes seguidos producen tres alertas, porque el Switch está antes del debounce. En
Kommo pasaba exactamente lo mismo: su debounce (`Guardar`/`Wait_35`/`Ultimo?`) vivía en la
rama de `checkType`, no en la de `checkType1`. Es paridad; se deja así.

Idempotente: si ya está aplicado, no duplica nada.

Uso:  hpf-fix-mute-cliente-vuelve.py [--dry-run]
"""
import importlib.util
import pathlib
import sys

# se carga a mano porque el nombre del archivo tiene guiones
_spec = importlib.util.spec_from_file_location(
    "hpfdeploy", pathlib.Path(__file__).parent / "hpf-deploy-workflow.py")
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)

CRED_TG = {"telegramApi": {"id": "vgyWhM8OBUJtYOGC", "name": "H.F"}}
CHAT = "-4925599962"          # el MISMO grupo que usaba Kommo

VIEJO = "Reciclar oportunidad (stub)"
NUEVO = "Cliente vuelve · sin respuesta"
TG = "Aviso · cliente vuelve"
DEBOUNCE = "Debounce · push"
SWITCH = "Ruteo por estado"

# El texto se arma con $('Evaluar estado') y no con $json por la regla de
# _core/standards/n8n-data-references.md, aunque el predecesor sea un NoOp que preserva.
# NO se incluye el texto del lead a propósito: el nodo Telegram va sin `parse_mode`
# explícito (default Markdown), así que un '*' o un '_' sueltos en el mensaje del cliente
# harían fallar el envío con un 400 de la API.
TEXTO = ("=👤 El lead {{ $('Evaluar estado').first().json.contactId }} está en "
         "*{{ $('Evaluar estado').first().json.etapa }}* y envió un mensaje. "
         "El bot no le respondió — hay que atenderlo a mano.")

NODO_TG = {
    "id": "c2f8b5e1-3333-4bbb-9003-1f2b3c4d5e03",
    "name": TG,
    "type": "n8n-nodes-base.telegram",
    "typeVersion": 1.2,
    "position": [1504, -320],
    "webhookId": "8d3c1a56-7e42-4b90-a1f5-62d7b8e93c14",
    "credentials": CRED_TG,
    # Un fallo de Telegram no puede tumbar el turno: el objetivo primario de esta rama es
    # que el bot NO conteste, y eso ya se cumplió al llegar acá.
    "onError": "continueRegularOutput",
    "parameters": {
        "chatId": CHAT,
        "text": TEXTO,
        "additionalFields": {"appendAttribution": False},
    },
}


def renombrar(w, viejo, nuevo):
    """Renombra un nodo y todas las referencias que le apuntan en connections."""
    for n in w["nodes"]:
        if n["name"] == viejo:
            n["name"] = nuevo
    conn = w["connections"]
    if viejo in conn:
        conn[nuevo] = conn.pop(viejo)
    for salidas in conn.values():
        for rama in salidas.get("main", []):
            for t in rama:
                if t.get("node") == viejo:
                    t["node"] = nuevo


def main():
    dry = "--dry-run" in sys.argv
    w = D.bajar("W1")
    idx = {n["name"]: n for n in w["nodes"]}
    print(f"W1 vivo: {len(w['nodes'])} nodos")

    # ── 1. renombrar el NoOp (el nombre viejo describe algo que ya no se va a hacer)
    if NUEVO in idx:
        print(f"   • {NUEVO}: ya renombrado")
    elif VIEJO in idx:
        renombrar(w, VIEJO, NUEVO)
        print(f"   ~ {VIEJO!r} → {NUEVO!r}")
    else:
        sys.exit(f"❌ no encuentro ni {VIEJO!r} ni {NUEVO!r} en el vivo")

    # ── 2. nodo de alerta (idempotente)
    if TG in {n["name"] for n in w["nodes"]}:
        print(f"   • {TG}: ya existe, no lo duplico")
    else:
        w["nodes"].append(NODO_TG)
        print(f"   + nodo {TG}")

    conn = w["connections"]

    # ── 3. la rama deja de ir al debounce y termina en la alerta
    rama = conn.setdefault(NUEVO, {}).setdefault("main", [[]])
    if not rama:
        rama.append([])
    destinos = [t["node"] for t in rama[0]]
    if destinos == [TG]:
        print(f"   • {NUEVO} → {TG}: ya cableado")
    else:
        rama[0] = [{"node": TG, "type": "main", "index": 0}]
        print(f"   ~ {NUEVO}: {destinos} → ['{TG}']")

    # el nodo de alerta es terminal
    if conn.get(TG, {}).get("main", [[]])[0]:
        sys.exit(f"❌ {TG} tiene conexiones de salida y debería ser terminal")

    # ── 4. el Switch no se toca: sólo se comprueba que siga igual
    sw = [t["node"] for r in conn[SWITCH]["main"] for t in r]
    esperado = ["Fin · agente en silencio", NUEVO, DEBOUNCE]
    if sw != esperado:
        sys.exit(f"❌ {SWITCH} quedó {sw}, esperaba {esperado}")
    print(f"   • {SWITCH}: 3 salidas intactas → {sw}")

    if dry:
        print("(dry-run: no escribo)")
        return

    D.subir("W1", w)

    # ── 5. releer del vivo y verificar
    print("\n── verificación contra el vivo")
    v = D.bajar("W1")
    vidx = {n["name"]: n for n in v["nodes"]}
    vconn = v["connections"]
    ok = True

    def chk(cond, bien, mal):
        nonlocal ok
        print(f"   {'✅' if cond else '❌'} {bien if cond else mal}")
        if not cond:
            ok = False

    chk(len(v["nodes"]) == 52, f"52 nodos", f"quedaron {len(v['nodes'])} nodos, esperaba 52")
    chk(TG in vidx, f"{TG} existe", f"falta {TG}")
    if TG in vidx:
        cred = vidx[TG].get("credentials", {}).get("telegramApi", {}).get("id")
        chk(cred == CRED_TG["telegramApi"]["id"], f"credencial {cred}", f"credencial {cred} equivocada")
        chk(vidx[TG]["parameters"]["chatId"] == CHAT, f"chat {CHAT}",
            f"chat {vidx[TG]['parameters'].get('chatId')} equivocado")
        chk(vidx[TG].get("onError") == "continueRegularOutput",
            "onError continueRegularOutput", "onError no quedó en continueRegularOutput")
    chk(VIEJO not in vidx, f"{VIEJO!r} ya no existe", f"{VIEJO!r} sigue ahí")
    chk(NUEVO in vidx, f"{NUEVO!r} existe", f"falta {NUEVO!r}")

    d = [t["node"] for t in vconn.get(NUEVO, {}).get("main", [[]])[0]]
    chk(d == [TG], f"{NUEVO} → {d}", f"{NUEVO} → {d}, esperaba ['{TG}']")
    chk(not vconn.get(TG, {}).get("main", [[]])[0], f"{TG} es terminal",
        f"{TG} tiene salida y no debería")

    sw = [[t["node"] for t in r] for r in vconn[SWITCH]["main"]]
    chk(sw == [["Fin · agente en silencio"], [NUEVO], [DEBOUNCE]],
        f"{SWITCH} → {sw}", f"{SWITCH} quedó {sw}")

    # el debounce ahora sólo lo alimenta la salida 'seguir' del Switch
    entradas = [o for o, s in vconn.items()
                for r in s.get("main", []) for t in r if t["node"] == DEBOUNCE]
    chk(entradas == [SWITCH], f"{DEBOUNCE} lo alimenta sólo {entradas}",
        f"{DEBOUNCE} lo alimentan {entradas}, esperaba ['{SWITCH}']")

    # el Telegram Trigger sin webhookId activa sin error y nunca recibe nada
    trig = [n for n in v["nodes"] if n["type"].endswith("telegramTrigger")]
    chk(bool(trig) and all(n.get("webhookId") for n in trig),
        "el Telegram Trigger conserva su webhookId", "¡el Telegram Trigger perdió el webhookId!")

    s, meta = D.api(f"/api/v1/workflows/{D.IDS['W1']}")
    chk(meta.get("active") is True, "W1 sigue activo", "W1 quedó INACTIVO")

    print("\n✅ aplicado" if ok else "\n❌ revisar")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
