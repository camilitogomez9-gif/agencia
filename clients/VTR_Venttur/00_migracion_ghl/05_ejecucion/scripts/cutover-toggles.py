#!/usr/bin/env python3
"""
CUTOVER-2 · Flip de toggles n8n (Venttur WABA → GHL).

Deja de usarse ManyChat/Airtable y arranca el stack GHL. Desde el 23/9 el traspaso de WhatsApp (hora H, la
elegimos nosotros) y el DNS de promo.venttur.com (hora T, la de la agencia) van separados. Orden (guía raíz
`guia-recta-final-ejecutable-2026-09-20.md`):
  Fase B (H): B0 snapshot → B1 --solo-on → B2 dominio-links-agente.py --a vtr + --landings-on → B3 BSP
              → B4 smoke → B6 --solo-off → B7 anuncio
  B5 (T):     dominio en GHL + redirects → dominio-links-agente.py --a promo → (+4 h) --landings-off
Con los links del agente en vtr.[TU-DOMINIO] (landings de GHL), el rescate puede ir con B2 aunque promo
siga en Clientify; el motivo de abajo aplica sólo si el agente mandara links a promo con promo en Clientify.

Uso:
  python3 cutover-toggles.py                 # DRY-RUN del flip completo: muestra qué haría, no toca nada
  python3 cutover-toggles.py --execute       # flip completo (agente + landings): ON los 9 nuevos, OFF los 6 viejos.
                                             #   Sólo si promo.venttur.com ya sirve GHL (incluye el rescate).
  python3 cutover-toggles.py --rollback --execute   # revierte todo: ON los 6 viejos, OFF los 9 nuevos (rescate incluido)
  python3 cutover-toggles.py --verify        # solo muestra el estado actual de todos
  python3 cutover-toggles.py --solo-on --execute    # B1 (antes del CNAME y del BSP): prende los nuevos MENOS el rescate
  python3 cutover-toggles.py --solo-off --execute   # B6 (después del BSP): solo apaga los viejos del agente
  python3 cutover-toggles.py --landings-on --execute   # B5, cuando promo.venttur.com ya sirve GHL: W4 + CAPI folio
                                                       #   Supabase + rescate GHL
  python3 cutover-toggles.py --landings-off --execute  # B5.8, +4 h de B5: form Clientify + CAPI folio Airtable viejos
Sin --execute todo es dry-run.

Dos grupos que se mueven por separado:
  · AGENTE (main, confirmación, outreach, barrido): se mueve con el BSP.
  · LANDINGS (formulario Clientify + CAPI folio ↔ W4 + CAPI folio Supabase + rescate GHL): se mueve con el cambio
    del CNAME de promo.venttur.com. Mientras promo siga sirviendo Clientify, los webhooks viejos tienen que seguir
    prendidos; por eso --solo-off no los toca.

Por qué el rescate GHL (YB0UxwEVwzISdd54) va con las landings y NO con --solo-on:
  el agente nuevo manda links a promo.venttur.com. Si el BSP (B3) pasa antes de que promo sirva GHL (B5), el lead
  agenda en Clientify y GHL no ve la cita: el rescate (45 min / 24 h después del link) le escribiría "no agendaste"
  a alguien que sí agendó. Con el rescate apagado eso no puede pasar. Lo que sí pasa, y es esperado: el main llama
  a W9 con waitForSubWorkflow:false, así que W9 igual marca link_enviado=true y su POST al webhook
  vtr-rescate-link devuelve 404 → la ejecución de W9 queda en rojo sin afectar al agente (ruido esperado hasta B5).
  El carril "rescate" del despachador tiene el mismo problema (elige por link_enviado=true y sólo excluye citas que
  estén en GHL): lo protege el gate de C2 de la guía (habilitar el envío sólo después de B5), no este script.
  --rollback lo sigue apagando (está en NUEVOS).

Por qué partirlo en 2 (--solo-on / --solo-off): si el stack nuevo ya está prendido cuando el BSP conmuta, el
primer mensaje que entra por GHL tiene receptor. Prender lo nuevo antes es inocuo (sin WABA en GHL no llega
tráfico de WhatsApp; el despachador corre en dry-run; W4 sólo recibe de las landings nuevas).

n8n API: POST /workflows/{id}/activate  ·  POST /workflows/{id}/deactivate
"""
import json, sys, urllib.request, urllib.error

ROOT = "/Users/camilo/Downloads/camilo-workspace"


def env(key):
    for line in open(f"{ROOT}/.env"):
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip()


BASE = env("N8N_BASE_URL").rstrip("/")
KEY = env("N8N_API_KEY")

# Los 6 PRODUCTIVOS viejos (ManyChat/Airtable/Meta directo) → apagar en cutover
VIEJOS = {
    "k3aivKSP67S97IHn": "[Venttur] main WPP (ManyChat)",
    "2PSekVBxarsrnVBu": "Confirmación agenda (viejo)",
    "ZB6erhWicZmDfC4I": "Formulario Clientify (viejo)",
    "CUuFxbst3iHpgeXS": "Outreach Form Meta (viejo)",
    "9yCbynoKDt9hgiBq": "CAPI Registro Folio (Airtable)",
    "H6qYB3Oj97bxaTCX": "Estado interrumpida (Airtable)",
}
VIEJOS_LANDING = {k: VIEJOS[k] for k in ("ZB6erhWicZmDfC4I", "9yCbynoKDt9hgiBq")}

# El stack GHL nuevo → prender en cutover (los sub-workflows invocados NO necesitan toggle)
NUEVOS = {
    "1eS1Z5k898c3ATnf": "main-venttur-ghl (refactor)",
    "4HgMkK34xqITULM3": "CAPI Registro Folio Supabase",
    "OaOyHA2tfjMtuWTk": "W14 Correo semanal",
    "vrShEXQGGAo4FqAt": "Despachador proactivo",
    "YB0UxwEVwzISdd54": "Rescate GHL Post-Link (se prende en B5 con --landings-on)",
    "LrJuzU7qDeELWiAl": "Barrido interrumpida",
    "LhPSfMYtQbNcEK32": "W4 Formulario landing → GHL",
    "AS9ZNhY3GJDfhY3P": "W6 Confirmación agenda GHL",
    "MbPTKvy0bq8b4YAw": "W10 Outreach Sheet → GHL",
}
# Rescate GHL: se prende con las landings (B5), no con --solo-on (B1). Motivo en el docstring.
RESCATE = "YB0UxwEVwzISdd54"
NUEVOS_LANDING = {k: NUEVOS[k] for k in ("LhPSfMYtQbNcEK32", "4HgMkK34xqITULM3", RESCATE)}
# Nota despachador: se prende con sus 3 nodos de escritura DESHABILITADOS (Enviar template / Siembra memoria /
# Update toques) → corre como dry-run hasta POST-2. Prenderlo no manda nada.

# Sub-workflows con trigger "When Executed by Another Workflow": NO se activan. n8n los ejecuta aunque estén
# inactivos (verificado 22/9: gRSMjzxggA4UePjz inactivo corre OK desde el main viejo), y /activate sobre un
# workflow sin trigger activable devuelve error — que en la ventana del cutover se leería como una falla.
# mf7VQJelfieCDJ5r además tiene el Trigger deshabilitado (Meta CAPI, frente aparte).
SUBWORKFLOWS_INVOCADOS = {
    "v9XkOfL9dQtY2wyv": "vtr-tool-elevar-ghl (invocado por main)",
    "Xmyoewwa1W5gm1fy": "Clasificador postconv (invocado por main)",
    "qYgeTc9PCq3TiGDn": "W11 Estado Contestó (invocado por main)",
    "TROsQ5h78baAuVOY": "W9 Actualizar link_enviado (invocado por main → dispara rescate)",
    "mf7VQJelfieCDJ5r": "Meta CAPI Supabase (Trigger deshabilitado · pase aparte)",
}


def api(method, path):
    req = urllib.request.Request(BASE + path, headers={"X-N8N-API-KEY": KEY, "accept": "application/json"}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.getcode(), json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:200]


def get_active(wid):
    code, resp = api("GET", f"/api/v1/workflows/{wid}")
    if isinstance(resp, dict):
        return resp.get("active"), resp.get("name", "")
    return None, f"ERR {code}"


def activate(wid):
    return api("POST", f"/api/v1/workflows/{wid}/activate")


def deactivate(wid):
    return api("POST", f"/api/v1/workflows/{wid}/deactivate")


def verify():
    print("=== ESTADO ACTUAL ===")
    print("\n[VIEJOS · deberían quedar OFF post-cutover]")
    for wid, name in VIEJOS.items():
        a, _ = get_active(wid); print(f"  {'🟢 ON ' if a else '⚪ OFF'}  {wid}  {name}")
    print("\n[NUEVOS · deberían quedar ON post-cutover]")
    for wid, name in NUEVOS.items():
        a, _ = get_active(wid); print(f"  {'🟢 ON ' if a else '⚪ OFF'}  {wid}  {name}")
    print("\n[SUB-WORKFLOWS invocados · no requieren toggle]")
    for wid, name in SUBWORKFLOWS_INVOCADOS.items():
        a, _ = get_active(wid); print(f"  {'🟢 ON ' if a else '⚪ OFF'}  {wid}  {name}")


def flip(rollback, execute, solo=None):
    # normal: OFF viejos, ON nuevos.  rollback: ON viejos, OFF nuevos.
    off_set = NUEVOS if rollback else VIEJOS
    on_set = VIEJOS if rollback else NUEVOS
    if solo == "on":
        off_set = {}
        if not rollback:
            on_set = {k: v for k, v in on_set.items() if k != RESCATE}  # el rescate espera a --landings-on (B5)
    elif solo == "off":
        on_set = {}
        off_set = {k: v for k, v in off_set.items() if k not in VIEJOS_LANDING}  # siguen hasta el cambio de DNS
    elif solo == "landings-on":
        on_set, off_set = dict(NUEVOS_LANDING), {}
    elif solo == "landings-off":
        on_set, off_set = {}, dict(VIEJOS_LANDING)
    mode = "ROLLBACK" if rollback else "CUTOVER-2"
    print(f"=== {mode} {'(EJECUTANDO)' if execute else '(DRY-RUN — no toca nada)'} ===\n")
    # Primero se prende lo nuevo y después se apaga lo viejo: el hueco sin receptor queda en ~segundos.
    print(f"ACTIVAR ({len(on_set)}):")
    for wid, name in on_set.items():
        if execute:
            code, _ = activate(wid); print(f"  {'✓' if 200 <= code < 300 else '✗ '+str(code)}  ON   {name}")
        else:
            print(f"  → ON   {wid}  {name}")
    print(f"\nDESACTIVAR ({len(off_set)}):")
    for wid, name in off_set.items():
        if execute:
            code, _ = deactivate(wid); print(f"  {'✓' if 200 <= code < 300 else '✗ '+str(code)}  OFF  {name}")
        else:
            print(f"  → OFF  {wid}  {name}")
    if not execute:
        print("\n[DRY-RUN] Nada cambió. Corré con --execute para aplicar.")
    else:
        print("\n✅ Toggles aplicados. Corré --verify para confirmar, y hacé el smoke test (CUTOVER-3).")


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify()
    else:
        solo = ("on" if "--solo-on" in sys.argv else "off" if "--solo-off" in sys.argv else
                "landings-on" if "--landings-on" in sys.argv else "landings-off" if "--landings-off" in sys.argv else None)
        flip(rollback="--rollback" in sys.argv, execute="--execute" in sys.argv, solo=solo)
