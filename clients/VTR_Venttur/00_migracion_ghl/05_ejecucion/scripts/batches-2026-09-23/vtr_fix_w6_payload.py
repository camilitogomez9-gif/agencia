#!/usr/bin/env python3
"""Fix 23/9 noche · W6: el flujo de GHL manda el payload ESTÁNDAR de la acción Webhook (no el body custom del
contrato): la cita viene en `calendar` ({startTime local sin zona, selectedTimezone, address, appoinmentStatus}) y el
programa en `programa_interes`. El código buscaba `appointment_start` → mensaje sin fecha (ejecución 1495803). Y una
hora sin zona se parseaba en la zona del servidor (UTC+2). Ahora: fecha desde `calendar.startTime` en su
`selectedTimezone` (o CDMX), link desde `calendar.address` si es URL, programa desde `programa_interes`.
Idempotente (W6-CAL-0923)."""
import sys, importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("p", Path(__file__).with_name("vtr_pre_bsp_fixes.py"))
p = importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
WID = "AS9ZNhY3GJDfhY3P"; OUT = p.OUT / "w6-payload"
c, wf = p.api("GET", f"/workflows/{WID}")
n = p.node(wf, "Normalize + build msg")
if "W6-CAL-0923" in n["parameters"]["jsCode"]: sys.exit("↷ ya aplicado")
p.replace_in(n, "const programa   = (p.programa || p.programa_interes || p.calendar_name || '').toString();\n"
                "const start      = (p.appointment_start || p.startTime || p.start_time || '').toString();\n"
                "let meeting    = (p.meeting_link || p.meeting_location || p.address || '').toString();",
             "const cal = (p.calendar && typeof p.calendar === 'object') ? p.calendar : {};  // W6-CAL-0923: payload estándar de GHL\n"
             "const programa   = (p.programa || p.programa_interes || p.calendar_name || '').toString();\n"
             "const start      = (p.appointment_start || p.startTime || p.start_time || cal.startTime || '').toString();\n"
             "const calZone    = cal.selectedTimezone || 'America/Mexico_City';\n"
             "let meeting    = (p.meeting_link || p.meeting_location || p.address || cal.address || '').toString();")
p.replace_in(n, "    const dt = DateTime.fromISO(start, { setZone: true }).setZone('America/Mexico_City');",
             "    const conZona = /[zZ]|[+-]\\d\\d:?\\d\\d$/.test(start);\n"
             "    const dt = (conZona ? DateTime.fromISO(start, { setZone: true }) : DateTime.fromISO(start.replace(' ', 'T'), { zone: calZone }))\n"
             "      .setZone('America/Mexico_City');")
if "--execute" not in sys.argv: sys.exit("[dry-run] ok")
c0, pre = p.api("GET", f"/workflows/{WID}"); p.save(pre, OUT / "pre" / "w6.json")
body = {"name": wf["name"], "nodes": wf["nodes"], "connections": wf["connections"],
        "settings": {k: v for k, v in (wf.get("settings") or {}).items() if k in p.SETTINGS_OK}}
c, r = p.api("PUT", f"/workflows/{WID}", body)
if c != 200: sys.exit(f"❌ PUT {c} {r}")
c, post = p.api("GET", f"/workflows/{WID}"); p.save(post, OUT / "post" / "w6.json"); print("✅ W6 lee calendar.startTime · activo", post["active"])
