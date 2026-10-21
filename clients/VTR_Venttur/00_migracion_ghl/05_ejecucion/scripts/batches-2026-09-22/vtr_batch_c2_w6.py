#!/usr/bin/env python3
"""
Batch C.2 · W6 · Confirmación agenda GHL (OFF) — reemplaza 2PSekVBxarsrnVBu.

Cambios vs viejo:
 - Trigger = Webhook GHL "Customer Booked Appointment" (NO 3 GCal Triggers por asesor).
 - Se BORRA el path Diego (D9 · Diego García fuera del ruteo).
 - Fix bug "marca-antes-de-enviar": PRIMERO envía la confirmación, DESPUÉS marca agendan_cita.
 - Ruteo único: el asesor viene en el payload del appointment (no hay Switch por asesor).

⚠️ El lado GHL (un GHL Workflow con trigger "Customer Booked Appointment" + acción Webhook
que POSTea a este n8n) se arma en la UI de GHL. Contrato del payload documentado en el README.
Recordatorios pre-cita 24h + 1h = W6b separado (no incluido acá).
"""
import json
import subprocess
import uuid
import hashlib
from pathlib import Path

ROOT = Path("/Users/camilo/Downloads/camilo-workspace")
BATCH_DIR = ROOT / "clients/VTR_Venttur/03_workflows/ghl-live-2026-09-22-batch-C2"
BATCH_DIR.mkdir(parents=True, exist_ok=True)
GHL_CRED = {"id": "YkVmaA4jlRbO1TQD", "name": "GHL VTR (PIT)"}
LOC = "7aXb4JCKsWV5nUyBXeSF"
CF = {"agendan_cita": "LwXu8AxMLhVGCbNmgzm2", "estado_conversacion": "Omg1BvHmpXR0MMGsrpFh"}


def env_get(k):
    r = subprocess.run(["grep", f"^{k}=", str(ROOT / ".env")], capture_output=True, text=True, check=True)
    return r.stdout.strip().split("\n")[0].split("=", 1)[1].strip().strip('"').strip("'")


def curl_json(method, path, data=None, allow_fail=False):
    base = env_get("N8N_BASE_URL").rstrip("/")
    key = env_get("N8N_API_KEY")
    cmd = ["curl", "-sS", "-w", "\n%{http_code}", "-X", method,
           "-H", f"X-N8N-API-KEY: {key}", "-H", "Content-Type: application/json"]
    if data is not None:
        cmd.extend(["--data-binary", "@-"])
    cmd.append(f"{base}/api/v1{path}")
    r = subprocess.run(cmd, input=json.dumps(data) if data else None, capture_output=True, text=True)
    parts = r.stdout.rsplit("\n", 1)
    body = parts[0] if len(parts) == 2 else r.stdout
    code = parts[1].strip() if len(parts) == 2 else "?"
    if not (200 <= int(code) < 300) and not allow_fail:
        raise RuntimeError(f"{method} {path} → {code}: {body[:600]}")
    try:
        return json.loads(body), code
    except Exception:
        return body, code


def nid():
    return str(uuid.uuid4())


def find_existing(name):
    data, _ = curl_json("GET", "/workflows?limit=250")
    for wf in data.get("data", []):
        if wf.get("name") == name:
            return wf.get("id")
    return None


W6_NORMALIZE = r"""
// W6 · Normaliza payload de appointment GHL + arma mensaje + body de marcado
// Contrato esperado (POST desde GHL Workflow "Customer Booked Appointment"):
//   { contact_id, phone, first_name, programa, appointment_start, appointment_title,
//     calendar_name, assigned_user, meeting_link }
const p = $json.body || $json;

const contact_id = (p.contact_id || p.contactId || '').toString();
const first_name = (p.first_name || p.firstName || '').toString();
const programa   = (p.programa || p.programa_interes || p.calendar_name || '').toString();
const start      = (p.appointment_start || p.startTime || p.start_time || '').toString();
const meeting    = (p.meeting_link || p.meeting_location || p.address || '').toString();

// asesoría vs cita
const pp = programa.toLowerCase();
const palabra = (/pathway|superior/.test(pp)) ? 'asesoría' : 'cita';

// Fecha/hora en TZ CDMX
let fecha = '';
try {
  if (start) {
    const dt = DateTime.fromISO(start, { setZone: true }).setZone('America/Mexico_City');
    if (dt.isValid) fecha = dt.toFormat("dd/MM 'a las' HH:mm");
  }
} catch (e) { fecha = ''; }

let message = first_name
  ? `${first_name}, ¡confirmamos tu ${palabra}${fecha ? ' para el ' + fecha : ''}! 📅`
  : `¡Confirmamos tu ${palabra}${fecha ? ' para el ' + fecha : ''}! 📅`;
if (meeting) message += `\n\n📲 Te dejo el link de la reunión para que lo tengas a mano: ${meeting}`;

const CF = %CF%;
const mark_body = {
  customFields: [
    { id: CF.agendan_cita, value: 'true' },
    { id: CF.estado_conversacion, value: 'Cita confirmada' }
  ]
};
const send_body = { type: 'WhatsApp', contactId: contact_id, message };

return [{ json: { contact_id, first_name, programa, fecha, meeting, message, send_body, mark_body } }];
""".replace("%CF%", json.dumps(CF))

W6 = {
    "name": "W6 · Confirmación agenda (GHL) - Venttur (OFF)",
    "nodes": [
        {
            "parameters": {"httpMethod": "POST", "path": f"vtr-confirmacion-agenda-ghl-{nid()[:8]}",
                           "responseMode": "responseNode", "options": {}},
            "id": nid(), "name": "Webhook: appointment GHL", "type": "n8n-nodes-base.webhook",
            "typeVersion": 2, "position": [0, 0], "webhookId": nid(),
        },
        {
            "parameters": {"jsCode": W6_NORMALIZE},
            "id": nid(), "name": "Normalize + build msg", "type": "n8n-nodes-base.code",
            "typeVersion": 2, "position": [220, 0],
        },
        {
            "parameters": {
                "method": "POST", "url": "https://services.leadconnectorhq.com/conversations/messages",
                "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
                "sendHeaders": True,
                "headerParameters": {"parameters": [
                    {"name": "Version", "value": "2021-04-15"},
                    {"name": "LocationId", "value": LOC}]},
                "sendBody": True, "contentType": "json",
                "jsonBody": "={{ JSON.stringify($json.send_body) }}", "options": {},
            },
            "id": nid(), "name": "1. Enviar confirmación (WhatsApp)", "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2, "position": [440, 0], "credentials": {"httpHeaderAuth": GHL_CRED},
        },
        {
            "parameters": {
                "method": "PUT",
                "url": "=https://services.leadconnectorhq.com/contacts/{{ $('Normalize + build msg').first().json.contact_id }}",
                "authentication": "genericCredentialType", "genericAuthType": "httpHeaderAuth",
                "sendHeaders": True,
                "headerParameters": {"parameters": [
                    {"name": "Version", "value": "2021-07-28"},
                    {"name": "LocationId", "value": LOC}]},
                "sendBody": True, "contentType": "json",
                "jsonBody": "={{ JSON.stringify($('Normalize + build msg').first().json.mark_body) }}", "options": {},
            },
            "id": nid(), "name": "2. Marcar agendan_cita=true", "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.2, "position": [660, 0], "credentials": {"httpHeaderAuth": GHL_CRED},
        },
        {
            "parameters": {"respondWith": "json", "responseBody": '={"ok": true}', "options": {}},
            "id": nid(), "name": "Responder OK", "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1.1, "position": [880, 0],
        },
    ],
    "connections": {
        "Webhook: appointment GHL": {"main": [[{"node": "Normalize + build msg", "type": "main", "index": 0}]]},
        "Normalize + build msg": {"main": [[{"node": "1. Enviar confirmación (WhatsApp)", "type": "main", "index": 0}]]},
        "1. Enviar confirmación (WhatsApp)": {"main": [[{"node": "2. Marcar agendan_cita=true", "type": "main", "index": 0}]]},
        "2. Marcar agendan_cita=true": {"main": [[{"node": "Responder OK", "type": "main", "index": 0}]]},
    },
    "settings": {"executionOrder": "v1"},
}


if __name__ == "__main__":
    existing = find_existing(W6["name"])
    if existing:
        print(f"⚠️  ya existe → id={existing}")
        wid = existing
    else:
        created, _ = curl_json("POST", "/workflows", data=W6)
        wid = created["id"]
        print(f"✓ W6 creado id={wid} active={created.get('active')}")
    final, _ = curl_json("GET", f"/workflows/{wid}")
    path = BATCH_DIR / "W6-confirmacion-agenda-ghl.json"
    json.dump(final, open(path, "w"), indent=2, ensure_ascii=False)
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
    wh = [n["parameters"].get("path") for n in final["nodes"] if n["type"] == "n8n-nodes-base.webhook"]
    print(f"💾 W6-confirmacion-agenda-ghl.json · sha256={sha}")
    print(f"   webhook_path={wh}  active={final.get('active')}")
