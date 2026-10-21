#!/usr/bin/env python3
"""
test-sys-webhook-quick.py — Diagnóstico rápido del agente SYS productivo.

Ejecuta 10 casos focalizados contra el webhook n8n + evalúa con OpenAI LLM-as-judge.
Cada caso valida un aspecto crítico del comportamiento (apertura, cotización directa,
tool calls, FAQs nuevas, memoria persistente, out of scope).

Usage:
  source .env && python3 scripts/testing/test-sys-webhook-quick.py
  python3 scripts/testing/test-sys-webhook-quick.py --webhook-url=https://...
"""
import os, sys, json, time, uuid, argparse, requests, re
from datetime import datetime

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: pip install openai requests", file=sys.stderr); sys.exit(2)

# ─── Config ───────────────────────────────────────────────────────────────────
DEFAULT_WEBHOOK = "https://[TU-INSTANCIA-N8N]/webhook/sys-agent"
JUDGE_MODEL = "gpt-4o-mini"
DELAY_BETWEEN_CALLS = 1.5  # segundos

JUDGE_PROMPT = """Evaluá si la respuesta real del agente cumple el comportamiento esperado.

## Comportamiento esperado:
{expected}

## Respuesta real del agente:
{actual}

Considerá: ¿cubre lo esencial? ¿evita lo prohibido (frases con "NO", "sin", "NUNCA")?
NO penalices: diferencias menores de redacción, contenido adicional útil que no contradice.

Respondé EXACTAMENTE con un JSON: {{"verdict": "true"|"false"|"parcial", "reason": "una oración breve"}}"""

# ─── Casos de diagnóstico (10) ────────────────────────────────────────────────
# Cada caso: (id, descripción, lista de turnos, criterio_evaluación_final)
# Cada turno es (subscriber_id, mensaje). Misma sub_id en turnos consecutivos = memoria compartida.

CASES = [
    {
        "id": "01-apertura",
        "desc": "Apertura simple — saludo + pregunta abierta sin pedir datos",
        "turnos": [("diag-001", "Hola")],
        "expected": "Saluda como asistente de Sistemas y Soluciones. Hace UNA pregunta abierta. NO pide nombre/tel/datos. Sin frases de chatbot ('¡Perfecto!', '¡Genial!'). Tono rioplatense breve.",
    },
    {
        "id": "02-cotizacion-directa",
        "desc": "Regla 21 — cotización directa pide datos sin diagnóstico",
        "turnos": [("diag-002", "Hola, quiero un presupuesto de una impresora DTF")],
        "expected": "NO hace diagnóstico técnico previo (no pregunta sobre volumen, sustratos, espacio físico). Pide directamente nombre + teléfono + ubicación, en una sola pregunta breve.",
    },
    {
        "id": "03-consultar-tecnologia",
        "desc": "Tool consultar_tecnologia — info real de Airtable",
        "turnos": [("diag-003", "Qué es DTF UV?")],
        "expected": "Explica DTF UV mencionando: objetos rígidos, film con tintas UV + barniz, sin calor, transferencia con presión. NO inventa información. Tono natural sin decir 'según mi base de datos'.",
    },
    {
        "id": "04-tecnologia-nueva-solvente",
        "desc": "Tool consultar_tecnologia para tecnología NUEVA (Solvente)",
        "turnos": [("diag-004", "Y Solvente regular qué es? En qué se diferencia del Eco-Solvente?")],
        "expected": "Explica Solvente como tecnología distinta del Eco-Solvente. Menciona ventilación necesaria o VOC más alto. NO confunde con Eco-Solvente. Puede hacer comparativa breve.",
    },
    {
        "id": "05-faq-iva-nueva",
        "desc": "Tool consultar_faq — FAQ NUEVA sobre IVA",
        "turnos": [("diag-005", "Los precios incluyen IVA?")],
        "expected": "Responde que los precios están en dólares (USD) y NO incluyen IVA. Menciona que la cotización final con impuestos la pasa el equipo comercial.",
    },
    {
        "id": "06-aplicacion-encadenada",
        "desc": "Encadenamiento consultar_aplicacion → buscar_equipo",
        "turnos": [("diag-006", "Necesito estampar gorras, qué me conviene?")],
        "expected": "Recomienda DTF Textil como tecnología. Puede mencionar características (durable, funciona en cualquier color). Pregunta volumen estimado o pasa a más info. NO inventa modelos de equipos.",
    },
    {
        "id": "07-buscar-equipo-marca-real",
        "desc": "Tool buscar_equipo con marca REAL del catálogo (HUENU)",
        "turnos": [("diag-007", "Tienen impresoras HUENU UV de gran formato?")],
        "expected": "Menciona equipos HUENU UV específicos (ej. HR 1602 UV, HR 3204 UV, HR 3208 UV). NO menciona Mimaki ni Roland. Puede ofrecer pasar a comercial para cotización.",
    },
    {
        "id": "08-inventario-konica-usados",
        "desc": "Tool NUEVA consultar_inventario_usados (Konica refurbished)",
        "turnos": [("diag-008", "Tengo presupuesto bajo para producción digital láser. Tienen Konica usados?")],
        "expected": "Confirma que tienen equipos Konica refurbished (usados) disponibles en showroom PEPIRI. Menciona algún modelo específico (BIZHUB, ACCURIO) o invita a coordinar visita. NO da precios.",
    },
    {
        "id": "09-out-of-scope",
        "desc": "Out of scope — clima, no responde",
        "turnos": [("diag-009", "Cómo está el clima en Buenos Aires hoy?")],
        "expected": "NO responde sobre clima. Redirige verbatim o similar: 'Eso está fuera de lo que puedo ayudarte hoy, pero si tenés consultas sobre equipos o insumos de impresión, estoy a disposición.'",
    },
    {
        "id": "10-memoria-2turnos",
        "desc": "Memoria persistente — turno 2 con mismo sub_id recuerda turno 1",
        "turnos": [
            ("diag-010", "Hola, soy Mariana y tengo una imprenta en Mar del Plata"),
            ("diag-010", "Qué tecnología me conviene para banderas?"),
        ],
        "expected": "En el SEGUNDO turno, el agente trata la pregunta de banderas SIN volver a saludar y SIN pedir el nombre/ubicación de nuevo (ya los recibió). Recomienda Sublimación (tecnología para banderas) usando info real.",
    },
]


# ─── Helpers ──────────────────────────────────────────────────────────────────
def call_webhook(url, canal, subscriber_id, mensaje, auth_token=None, auth_header="Authorization", timeout=60):
    # Contrato v0.3: channel + last_input_text (alineado con Flow A ManyChat)
    payload = {
        "channel": canal,
        "subscriber_id": subscriber_id,
        "last_input_text": mensaje,
        "first_name": "Test"
    }
    headers = {"Content-Type": "application/json"}
    if auth_token:
        headers[auth_header] = auth_token
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=timeout)
        if r.status_code != 200:
            return f"[HTTP {r.status_code}]: {r.text[:200]}"
        data = r.json() if r.text else {}
        # Soporta v0.3 (ai_msg_*) y legacy (parte1/2/3)
        raw = (data.get("raw")
               or " | ".join(p for p in (data.get(f"ai_msg_{i}", "") for i in (1,2,3)) if p)
               or " | ".join(p for p in (data.get(f"parte{i}", "") for i in (1,2,3)) if p))
        return raw or f"[Respuesta vacía: {json.dumps(data)[:200]}]"
    except requests.exceptions.Timeout:
        return "[TIMEOUT]"
    except Exception as e:
        return f"[ERROR: {e}]"


def judge(client, expected, actual):
    if actual.startswith("["):  # error de webhook
        return ("error", f"Error de transporte: {actual[:120]}")
    prompt = JUDGE_PROMPT.format(expected=expected, actual=actual)
    try:
        r = client.chat.completions.create(
            model=JUDGE_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        raw = r.choices[0].message.content or ""
        m = re.search(r'\{.*?\}', raw, re.DOTALL)
        if m:
            data = json.loads(m.group())
            return data.get("verdict", "parcial"), data.get("reason", "")
        return "parcial", f"No se pudo parsear: {raw[:80]}"
    except Exception as e:
        return "error", f"Error juez: {e}"


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--webhook-url", default=DEFAULT_WEBHOOK)
    ap.add_argument("--canal", default="test")
    ap.add_argument("--auth-token", default=None, help="Valor del header de autenticación del webhook")
    ap.add_argument("--auth-header", default="Authorization", help="Nombre del header de autenticación (default: Authorization)")
    ap.add_argument("--output", default="clients/SYS_SistemasYSoluciones/07_testing/f7-diagnostico-rapido-results.md")
    args = ap.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY no está en el ambiente. Ejecutar: source .env && python3 ...", file=sys.stderr)
        sys.exit(1)

    client = OpenAI()
    results = []

    print(f"\nDIAGNÓSTICO RÁPIDO F7 — Agente SYS")
    print(f"Webhook: {args.webhook_url}")
    print(f"Canal:   {args.canal}")
    print(f"Juez:    {JUDGE_MODEL}")
    print(f"Casos:   {len(CASES)}\n")
    print("─" * 70)

    for case in CASES:
        # Sub_id único por caso para aislar memoria (excepto cuando explícitamente compartimos)
        # Acá usamos el sub_id literal definido en cada turno → si dos turnos comparten, hay memoria
        print(f"\n[{case['id']}] {case['desc']}")
        actual_responses = []
        for i, (sub_id, mensaje) in enumerate(case["turnos"]):
            print(f"  → Turno {i+1}: '{mensaje[:70]}'", end="", flush=True)
            actual = call_webhook(args.webhook_url, args.canal, sub_id, mensaje, auth_token=args.auth_token, auth_header=args.auth_header)
            actual_responses.append(actual)
            time.sleep(DELAY_BETWEEN_CALLS)
            preview = actual.replace("\n", " ")[:60]
            print(f"\n     respuesta: {preview}...")

        # Evaluar SOLO la última respuesta contra el criterio
        last_response = actual_responses[-1]
        verdict, reason = judge(client, case["expected"], last_response)
        icon = "✅" if verdict == "true" else ("⚠️" if verdict == "parcial" else ("❌" if verdict == "false" else "🔴"))
        print(f"  → {icon} {verdict.upper()} — {reason[:100]}")
        results.append({
            "id": case["id"],
            "desc": case["desc"],
            "mensajes": [m for _, m in case["turnos"]],
            "actual": last_response,
            "verdict": verdict,
            "reason": reason,
            "expected": case["expected"],
        })

    # ─── Output md ─────────────────────────────────────────────────────────────
    counts = {v: sum(1 for r in results if r["verdict"] == v) for v in ("true", "false", "parcial", "error")}
    pct_pass = round(100 * counts["true"] / len(results), 1)

    lines = [
        "# F7 — Diagnóstico Rápido (resultados)",
        "",
        f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Webhook:** `{args.webhook_url}`",
        f"**Modelo juez:** `{JUDGE_MODEL}`",
        f"**Casos:** {len(CASES)}",
        "",
        f"## Resumen",
        "",
        f"- ✅ Pass (true):    **{counts['true']}** ({pct_pass}%)",
        f"- ⚠️ Parcial:        **{counts['parcial']}**",
        f"- ❌ Fail (false):   **{counts['false']}**",
        f"- 🔴 Error transp.:  **{counts['error']}**",
        "",
        "## Detalle por caso",
        "",
        "| # | Caso | Veredicto | Razón | Respuesta agente |",
        "|---|------|-----------|-------|------------------|",
    ]
    for r in results:
        msgs = " → ".join(f"`{m[:30]}`" for m in r["mensajes"])
        actual_short = r["actual"].replace("\n", " ").replace("|", "\\|")[:120]
        reason_short = r["reason"].replace("|", "\\|")[:80]
        lines.append(f"| {r['id']} | {r['desc'][:50]} | {r['verdict']} | {reason_short} | {actual_short}... |")

    lines.append("")
    lines.append("## Casos completos (mensaje + esperado + obtenido)")
    lines.append("")
    for r in results:
        lines.append(f"### {r['id']} — {r['desc']}")
        lines.append("")
        lines.append(f"**Mensajes:**")
        for m in r["mensajes"]:
            lines.append(f"- `{m}`")
        lines.append("")
        lines.append(f"**Esperado:** {r['expected']}")
        lines.append("")
        lines.append(f"**Obtenido:**")
        lines.append("```")
        lines.append(r["actual"])
        lines.append("```")
        lines.append("")
        icon = "✅" if r['verdict'] == "true" else ("⚠️" if r['verdict'] == "parcial" else "❌")
        lines.append(f"**Veredicto:** {icon} `{r['verdict']}` — {r['reason']}")
        lines.append("")
        lines.append("---")
        lines.append("")

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("\n" + "─" * 70)
    print(f"\n🎯 RESUMEN: {counts['true']}/{len(results)} OK ({pct_pass}%)  "
          f"| Parcial: {counts['parcial']}  | Fail: {counts['false']}  | Error: {counts['error']}")
    print(f"\n📄 Resultados completos: {args.output}\n")


if __name__ == "__main__":
    main()
