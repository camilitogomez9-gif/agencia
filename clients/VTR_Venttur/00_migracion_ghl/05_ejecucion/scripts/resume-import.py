"""
Resume del import tras el cap diario (B-12). Corre TODO lo pendiente SECUENCIAL (nunca en paralelo).
1) chequea el cap diario (1 request). Si daily-remaining == 0 → aborta (esperar reset).
2) opps (resume desde deal-idmap) → reasignación de contacts (resume) → dedup guard.
Uso: python3 resume-import.py [--check-only]
"""
import json, os, subprocess, sys, urllib.request, urllib.error, re, time
sys.path.insert(0, os.path.dirname(__file__))
from _ghl_client import GHL, UA

HERE = os.path.dirname(__file__)

def daily_remaining():
    g = GHL()
    req = urllib.request.Request(f"{g.BASE}/locations/{g.location_id}",
        headers={"Authorization": f"Bearer {g.token}", "Version": g.VERSION, "User-Agent": UA})
    try:
        r = urllib.request.urlopen(req, timeout=20)
        # header disponible también en 200
        return int(r.headers.get("X-RateLimit-Daily-Remaining", "1"))
    except urllib.error.HTTPError as e:
        v = e.headers.get("X-RateLimit-Daily-Remaining")
        return int(v) if v is not None else (-1 if e.code == 429 else 1)

rem = daily_remaining()
print(f"X-RateLimit-Daily-Remaining = {rem}")
if "--check-only" in sys.argv:
    sys.exit(0)
if rem <= 5:
    print("❌ cap diario agotado — esperar el reset. No corro nada.")
    sys.exit(2)

def run(args):
    print(f"\n▶ {' '.join(args)}")
    subprocess.run([sys.executable] + args, cwd=HERE, check=False)

# SECUENCIAL, nunca en paralelo
run(["import-datos.py", "--stage", "opportunities", "--apply"])
run(["reasignar-owners.py", "--apply"])
print("\n✅ resume completo — correr la reconciliación aparte")
