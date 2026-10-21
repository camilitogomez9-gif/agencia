#!/usr/bin/env python3
"""
POST-2 · Despachador proactivo vrShEXQGGAo4FqAt — política de recontacto + habilitar envío.

Dos pasos separados a propósito:

  1) --politica   Parchea el gate de `Seleccionar (tope-2 + prioridad)`. No envía nada (los 3 nodos de
                  escritura siguen deshabilitados). Se puede aplicar antes del cutover.
  2) --habilitar-envio   Habilita `Enviar template GHL` + `Siembra memoria (Supabase)` + `Update toques (+1)`.
                  Recién acá el despachador empieza a mandar WhatsApp. Hacerlo DESPUÉS de mirar 2-3 corridas
                  en dry-run (Executions → output de `Tiene templateId?`).

Sin --execute es dry-run (muestra el diff y no toca nada). Guarda snapshot pre en batch-C2/pre/.

Qué corrige la política (bugs verificados en el vivo el 22/9):
  - Sin espaciado entre toques: el gate no leía la fecha del último toque (que `Update toques` sí escribe en
    P3a7nGkO57LwCvHhYQyc). Con el cron horario, un lead elegible recibía sus 2 toques con 1 h de diferencia.
    → mínimo MIN_HORAS_ENTRE_TOQUES entre toques.
  - Históricos sin fecha: `última actividad` null pasaba el filtro de recencia (rescate + nurturing), y en
    outreach un `Touch 1 programado at` null contaba como vencido. Eran ~1.500 candidatos del import.
    → rescate/nurturing exigen última actividad dentro de RECENCIA_DIAS; outreach exige Touch 1 dentro de
      RECENCIA_DIAS (un lead de Form Meta nuevo todavía no escribió, por eso no se le pide última actividad).

Uso:
  python3 vtr_post2_despachador.py --politica                    # dry-run
  python3 vtr_post2_despachador.py --politica --execute
  python3 vtr_post2_despachador.py --habilitar-envio --execute
  python3 vtr_post2_despachador.py --deshabilitar-envio --execute  # freno de mano
"""
import json, sys, hashlib, urllib.request, urllib.error
from pathlib import Path

ROOT = Path("/Users/camilo/Downloads/camilo-workspace")
WID = "vrShEXQGGAo4FqAt"
PRE = ROOT / "clients/VTR_Venttur/03_workflows/ghl-live-2026-09-22-batch-C2/pre"
SEL = "Seleccionar (tope-2 + prioridad)"
ENVIO = ["Enviar template GHL", "Siembra memoria (Supabase)", "Update toques (+1)"]
MIN_HORAS = 24          # entre toque 1 y toque 2 (la cadencia vieja de outreach era T1 → T2 a las 24 h)


def env(k):
    for line in open(ROOT / ".env"):
        if line.startswith(k + "="):
            return line.split("=", 1)[1].strip()


BASE, KEY = env("N8N_BASE_URL").rstrip("/"), env("N8N_API_KEY")


def api(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
                                 headers={"X-N8N-API-KEY": KEY, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"❌ {method} {path} → {e.code} {e.read().decode()[:300]}")


# (ancla, reemplazo) — cada ancla tiene que aparecer exactamente una vez
EDITS = [
    ("const RECENCIA_DIAS = 30;              // ⚠ null en históricos → no filtra (política §8 recontacto pendiente)",
     "const RECENCIA_DIAS = 30;              // null ya NO pasa: política conservadora POST-2 (2026-09-22)\n"
     f"const ULT_TOQUE = 'P3a7nGkO57LwCvHhYQyc';   // lo escribe Update toques (+1)\n"
     f"const MIN_HORAS_ENTRE_TOQUES = {MIN_HORAS};"),
    ("  const ua = cfv(c, UAF); const t = ua ? Date.parse(ua) : null;\n"
     "  if (t && (now - t) > RECENCIA_DIAS*864e5) return false;\n"
     "  return true;\n};",
     "  const ut = cfv(c, ULT_TOQUE); const tu = ut ? Date.parse(ut) : null;\n"
     "  if (tu && (now - tu) < MIN_HORAS_ENTRE_TOQUES*36e5) return false;   // espaciado entre toques\n"
     "  return true;\n};\n"
     "// Recencia por carril: rescate/nurturing miden la última actividad del lead; outreach mide el Touch 1\n"
     "// (un lead de Form Meta todavía no escribió). Sin fecha → no se toca (históricos del import).\n"
     "const reciente = (iso) => { const t = iso ? Date.parse(iso) : NaN; return !isNaN(t) && (now - t) <= RECENCIA_DIAS*864e5; };"),
    ("for (const c of flat('Query rescate','contacts')) { if (gate(c)) sel.set(c.id, mk(c,'rescate')); }",
     "for (const c of flat('Query rescate','contacts')) { if (gate(c) && reciente(cfv(c,UAF))) sel.set(c.id, mk(c,'rescate')); }"),
    ("if (truthy(cfv(c,L))) continue; if (gate(c)) sel.set(c.id, mk(c,'nurturing')); }",
     "if (truthy(cfv(c,L))) continue; if (gate(c) && reciente(cfv(c,UAF))) sel.set(c.id, mk(c,'nurturing')); }"),
    ("  const t1 = cfv(c, TOUCH1); const due = t1 ? (Date.parse(t1) <= now) : true;\n"
     "  if (due && gate(c)) sel.set(c.id, mk(c,'outreach'));",
     "  const t1 = cfv(c, TOUCH1); const due = t1 ? (Date.parse(t1) <= now) : false;\n"
     "  if (due && reciente(t1) && gate(c)) sel.set(c.id, mk(c,'outreach'));"),
]

ALLOWED_SETTINGS = {"executionOrder", "saveManualExecutions", "callerPolicy", "errorWorkflow", "timezone",
                    "saveDataErrorExecution", "saveDataSuccessExecution", "saveExecutionProgress",
                    "executionTimeout"}


def main():
    execute = "--execute" in sys.argv
    w = api("GET", f"/api/v1/workflows/{WID}")
    if w["active"] and "--habilitar-envio" in sys.argv:
        print("ℹ️ el despachador está activo: el envío arranca en la próxima corrida del cron (horaria).")
    nodes = {n["name"]: n for n in w["nodes"]}
    cambios = []

    if "--politica" in sys.argv:
        code = nodes[SEL]["parameters"]["jsCode"]
        if "MIN_HORAS_ENTRE_TOQUES" in code:
            print("✓ política ya aplicada — nada que hacer")
        else:
            for a, b in EDITS:
                n = code.count(a)
                if n != 1:
                    raise SystemExit(f"❌ ancla encontrada {n} veces (esperado 1): {a[:70]!r}")
                code = code.replace(a, b)
            nodes[SEL]["parameters"]["jsCode"] = code
            cambios.append(f"gate de '{SEL}' parcheado ({len(EDITS)} ediciones)")

    for flag, disabled in (("--habilitar-envio", False), ("--deshabilitar-envio", True)):
        if flag in sys.argv:
            for nm in ENVIO:
                if bool(nodes[nm].get("disabled")) != disabled:
                    nodes[nm]["disabled"] = disabled
                    cambios.append(f"{'deshabilitado' if disabled else 'HABILITADO'}: {nm}")

    if not cambios:
        print("Nada que cambiar. Flags: --politica · --habilitar-envio · --deshabilitar-envio [--execute]")
        return
    print("\n".join("  · " + c for c in cambios))
    if not execute:
        print("\n[DRY-RUN] Nada cambió. Agregá --execute para aplicar.")
        return

    PRE.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(api("GET", f"/api/v1/workflows/{WID}"), ensure_ascii=False, indent=1)
    snap = PRE / f"despachador-pre-post2-{hashlib.sha256(raw.encode()).hexdigest()[:8]}.json"
    snap.write_text(raw, encoding="utf-8")

    body = {"name": w["name"], "nodes": w["nodes"], "connections": w["connections"],
            "settings": {k: v for k, v in (w.get("settings") or {}).items() if k in ALLOWED_SETTINGS}}
    api("PUT", f"/api/v1/workflows/{WID}", body)
    back = {n["name"]: n for n in api("GET", f"/api/v1/workflows/{WID}")["nodes"]}
    ok = ("--politica" not in sys.argv or "MIN_HORAS_ENTRE_TOQUES" in back[SEL]["parameters"]["jsCode"])
    for flag, disabled in (("--habilitar-envio", False), ("--deshabilitar-envio", True)):
        if flag in sys.argv:
            ok = ok and all(bool(back[nm].get("disabled")) == disabled for nm in ENVIO)
    print(f"\n{'✅ aplicado y verificado' if ok else '❌ la relectura no coincide — revisar'} · snapshot pre: {snap}")


if __name__ == "__main__":
    main()
