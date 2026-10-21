#!/usr/bin/env python3
"""
HPF · Guarda de etapa antes de PERDIDOS1 (Kommo, devn8n).

Inserta, en cada una de las 4 cadencias de seguimiento de Happy Flops en devn8n,
un par de nodos [GET lead -> Code filtro] entre el feeder y el nodo PERDIDOS1, de
modo que un lead que ya esta en una etapa de PAGO / EN CURSO nunca se marque como
Ventas Perdidos (status_id 143). Fail-closed: si no se puede leer la etapa, no marca.

Etapas protegidas (todo lo pagado / en curso):
  91450360 Confirmar Pago | 89263352 Pago sin diseno | 91246120 Diseno
  100395519 En produccion | 100395523 Pago Liquidacion | 142 Ganado

Uso:
  python3 scripts/utilities/hpf-guarda-etapa-perdidos.py            # dry-run (no escribe)
  python3 scripts/utilities/hpf-guarda-etapa-perdidos.py --apply    # aplica (PUT) + verifica

Auth: .env -> HPF_N8N_API + HPF_N8N_API_KEY (header X-N8N-API-KEY).
Rollback: snapshots en clients/HPF_HappyFlops/03_workflows/kommo-live-2026-09-09-pre-guarda-perdidos/
"""
import json, os, sys, hashlib, uuid, urllib.request, urllib.error

ROOT = "/Users/camilo/Downloads/camilo-workspace"
SNAP_DIR = os.path.join(ROOT, "clients/HPF_HappyFlops/03_workflows/kommo-live-2026-09-09-pre-guarda-perdidos")
APPLY = "--apply" in sys.argv

env = {}
with open(os.path.join(ROOT, ".env")) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
BASE = env.get("HPF_N8N_API", "").rstrip("/")
KEY = env.get("HPF_N8N_API_KEY") or env.get("N8N_API_KEY")

def api(path, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
                                 headers={"X-N8N-API-KEY": KEY, "accept": "application/json",
                                          "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())

# cadencia -> (workflow_id, feeder_node, feeder_output_index)
TARGETS = {
    "Rebeca":     ("YR8yBPNdgVl0TxT1", "If3",  0),
    "Cotizacion": ("dNzLtCZFJnIqjlZx", "If4",  1),
    "7pasos":     ("xo1sLt9cAhFAC6k3", "If2",  1),
    "Imagen":     ("D04kO8VPKoAKL004", "If10", 0),
}

GET_URL = "=https://happyflopss.kommo.com/api/v4/leads/{{ $('HappyFlops - Seg. Rebeca').item.json.entity_id }}"
CRED = {"oAuth2Api": {"id": "5LAQ0vGZpLnE497Q", "name": "H.F"}}

GUARD_CODE = r"""// Guarda de etapa: no marcar Ventas Perdidos si el lead ya esta en una etapa de pago / en curso.
const PROTEGIDAS = [91450360, 89263352, 91246120, 100395519, 100395523, 142];
const out = [];
const items = $input.all();
for (let i = 0; i < items.length; i++) {
  const it = items[i];
  const j = (it && it.json) ? it.json : {};
  let status = (typeof j.status_id === 'number') ? j.status_id
             : (typeof j.status_id === 'string' && j.status_id.trim() !== '') ? Number(j.status_id)
             : null;
  if (status === null || Number.isNaN(status)) {
    // fallback robusto: respuesta wrapped {data:"<json string>"} o cualquier shape con status_id
    const raw = (typeof j.data === 'string') ? j.data : JSON.stringify(j);
    const m = raw.match(/"status_id"\s*:\s*"?(\d+)"?/);
    status = m ? Number(m[1]) : null;
  }
  const protegida = status !== null && PROTEGIDAS.includes(status);
  // fail-closed: protege etapas de pago Y desconocidas (no marca perdido si no pudo leer la etapa)
  if (protegida || status === null) continue;
  out.push({ json: { _guard_status_id: status }, pairedItem: it.pairedItem != null ? it.pairedItem : { item: i } });
}
return out;
"""

def http_get_node(name, pos):
    return {
        "parameters": {
            "url": GET_URL,
            "authentication": "genericCredentialType",
            "genericAuthType": "oAuth2Api",
            "sendHeaders": True,
            "headerParameters": {"parameters": [{"name": "accept", "value": "application/json"}]},
            "options": {},
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": pos,
        "id": str(uuid.uuid4()),
        "name": name,
        "credentials": CRED,
    }

def code_node(name, pos):
    return {
        "parameters": {"jsCode": GUARD_CODE},
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": pos,
        "id": str(uuid.uuid4()),
        "name": name,
    }

def find(nodes, name):
    for n in nodes:
        if n["name"] == name:
            return n
    return None

os.makedirs(SNAP_DIR, exist_ok=True)
manifest = []

for label, (wid, feeder, out_idx) in TARGETS.items():
    wf = api(f"/api/v1/workflows/{wid}")
    name = wf.get("name", label)
    raw = json.dumps(wf, ensure_ascii=False, indent=2)
    snap_path = os.path.join(SNAP_DIR, f"{label}-{wid}.json")
    with open(snap_path, "w") as f:
        f.write(raw)
    sha = hashlib.sha256(raw.encode()).hexdigest()
    manifest.append(f"{sha}  {label}-{wid}.json  (rollback snapshot, {len(wf['nodes'])} nodes)")

    nodes = wf["nodes"]
    conns = wf.get("connections", {})
    perd = find(nodes, "PERDIDOS1")
    feeder_node = find(nodes, feeder)
    assert perd and feeder_node, f"{label}: missing PERDIDOS1 or feeder {feeder}"

    getn = f"Chequear etapa (guarda pago)"
    coden = f"Filtrar etapa protegida"
    assert find(nodes, getn) is None and find(nodes, coden) is None, f"{label}: guard nodes already exist"

    px, py = perd["position"]
    gnode = http_get_node(getn, [px - 320, py + 150])
    cnode = code_node(coden, [px - 150, py + 150])

    # --- verify feeder currently -> PERDIDOS1 on the expected output index
    fmain = conns.get(feeder, {}).get("main", [])
    cur = fmain[out_idx] if out_idx < len(fmain) else []
    tgt = [c for c in (cur or []) if c.get("node") == "PERDIDOS1"]
    assert tgt, f"{label}: feeder {feeder}[out {out_idx}] does not point to PERDIDOS1 (got {cur})"

    print(f"\n=== {label} ({wid}) [{name}] ===")
    print(f"  nodes: {len(nodes)} -> {len(nodes)+2}")
    print(f"  rewire: {feeder}[main:{out_idx}] -> '{getn}' -> '{coden}' -> PERDIDOS1")
    print(f"  (antes: {feeder}[main:{out_idx}] -> PERDIDOS1)")
    print(f"  snapshot: {snap_path}  sha256={sha[:12]}...")

    if not APPLY:
        continue

    # --- mutate: add nodes
    nodes.append(gnode)
    nodes.append(cnode)
    # rewire feeder output -> GET (preserve other targets on that output, if any, minus PERDIDOS1)
    new_out = [c for c in (cur or []) if c.get("node") != "PERDIDOS1"]
    new_out.append({"node": getn, "type": "main", "index": 0})
    # ensure list long enough
    while len(fmain) <= out_idx:
        fmain.append([])
    fmain[out_idx] = new_out
    conns.setdefault(feeder, {}).setdefault("main", fmain)
    # GET -> Code
    conns[getn] = {"main": [[{"node": coden, "type": "main", "index": 0}]]}
    # Code -> PERDIDOS1
    conns[coden] = {"main": [[{"node": "PERDIDOS1", "type": "main", "index": 0}]]}

    # n8n public API rejects settings keys outside its schema (e.g. binaryMode, availableInMCP);
    # n8n preserves those internally anyway. Whitelist the allowed ones.
    ALLOWED_SETTINGS = {"saveExecutionProgress", "saveManualExecutions", "saveDataErrorExecution",
                        "saveDataSuccessExecution", "executionTimeout", "errorWorkflow", "timezone",
                        "executionOrder"}
    settings = {k: v for k, v in (wf.get("settings") or {}).items() if k in ALLOWED_SETTINGS}
    payload = {"name": wf["name"], "nodes": nodes, "connections": conns, "settings": settings}
    if isinstance(wf.get("staticData"), dict):
        payload["staticData"] = wf["staticData"]
    api(f"/api/v1/workflows/{wid}", method="PUT", body=payload)

    # --- verify
    back = api(f"/api/v1/workflows/{wid}")
    bnodes = {n["name"]: n for n in back["nodes"]}
    bconn = back.get("connections", {})
    ok = (getn in bnodes and coden in bnodes
          and len(back["nodes"]) == len(nodes)
          and any(c.get("node") == getn for c in (bconn.get(feeder, {}).get("main", [[]]*(out_idx+1))[out_idx] or []))
          and any(c.get("node") == coden for c in (bconn.get(getn, {}).get("main", [[]])[0] or []))
          and any(c.get("node") == "PERDIDOS1" for c in (bconn.get(coden, {}).get("main", [[]])[0] or []))
          and not any(c.get("node") == "PERDIDOS1" for c in (bconn.get(feeder, {}).get("main", [[]]*(out_idx+1))[out_idx] or [])))
    print(f"  APPLIED. verify nodes={len(back['nodes'])} guard_wired={ok}")
    if not ok:
        print("  !!! VERIFY FAILED — revisar manualmente / restaurar snapshot")

# write manifest
with open(os.path.join(SNAP_DIR, "README.md"), "w") as f:
    f.write("# Rollback snapshots — pre guarda etapa PERDIDOS1 (2026-09-09)\n\n")
    f.write("Snapshots del vivo (devn8n) ANTES de insertar la guarda de etapa antes de PERDIDOS1.\n")
    f.write("Restaurar: PUT /api/v1/workflows/<id> con {name,nodes,connections,settings,staticData} del archivo.\n\n")
    f.write("## sha256\n\n")
    for m in manifest:
        f.write(f"- {m}\n")

print("\n" + ("APPLIED to devn8n." if APPLY else "DRY-RUN only — nada se escribio. Corré con --apply para aplicar."))
print("Snapshots + README en:", SNAP_DIR)
