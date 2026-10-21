#!/usr/bin/env python3
"""
test-hpf-webhook.py — Testing del agente HPF (Recolector / Rebeca) contra webhook directo.

Ejecuta 8 casos simples + 3 flujos multi-turno de testing-guide-v1.md contra el webhook
de test que se conecta directo al AI Agent Recolector. Evalúa cada respuesta con
LLM-as-judge (gpt-4o-mini). Para casos con `expect_tool`, también verifica que
intermediateSteps contenga la tool esperada.

Usage:
  source .env && python3 scripts/testing/test-hpf-webhook.py
  python3 scripts/testing/test-hpf-webhook.py --webhook-url=https://...
"""
import os, sys, json, time, argparse, requests, re
from datetime import datetime

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: pip install openai requests", file=sys.stderr); sys.exit(2)

# ─── Config ───────────────────────────────────────────────────────────────────
DEFAULT_WEBHOOK = "https://[TU-INSTANCIA-N8N]/webhook/a7182aad-3a7a-404c-81ca-b79fdc3852bd"
JUDGE_MODEL = "gpt-4o-mini"
DELAY_BETWEEN_CALLS = 1.5

JUDGE_PROMPT = """Evaluá si la respuesta real del agente cumple el comportamiento esperado.

## Comportamiento esperado:
{expected}

## Respuesta real del agente (último turno):
{actual}

Considerá: ¿cubre lo esencial? ¿evita lo prohibido (frases con "NO", "sin", "NUNCA")?
NO penalices: diferencias menores de redacción, contenido adicional útil que no contradice.

Respondé EXACTAMENTE con un JSON: {{"verdict": "true"|"false"|"parcial", "reason": "una oración breve"}}"""

# ─── Casos ────────────────────────────────────────────────────────────────────
# Cada caso: id, desc, turnos [(sessionId, mensaje)], expected, expect_tool
# Misma sessionId en turnos consecutivos = memoria compartida

CASES = [
    # Casos simples (8)
    {
        "id": "C01-pregunta-directa",
        "desc": "Pregunta directa sobre personalización de mandiles",
        "turnos": [("test-hpf-c01", "Hola, ¿los mandiles se pueden personalizar?")],
        "expected": "Aclara que los mandiles NO se personalizan, vienen con 5 frases pre-establecidas (stock fijo). NO ofrece personalización gratis. NO dice 'sin costo adicional'. NO dice 'con el diseño que prefieras'.",
        "expect_tool": None,
    },
    {
        "id": "C02-logo",
        "desc": "Cliente quiere mandar su logo",
        "turnos": [("test-hpf-c02", "¿Puedo mandarles mi logo para que lo pongan en los mandiles?")],
        "expected": "Responde que NO se acepta logo/diseño custom en mandiles. Menciona que son stock fijo con 5 frases pre-establecidas. NO ofrece personalización gratis.",
        "expect_tool": None,
    },
    {
        "id": "C03-pago-extra",
        "desc": "Cliente ofrece pagar más por personalización",
        "turnos": [("test-hpf-c03", "Si pago más, ¿podrían personalizar los mandiles con el nombre de los novios?")],
        "expected": "Se mantiene firme en que NO se personalizan, aunque el cliente ofrezca pagar más. Aclara que los mandiles son stock fijo con 5 frases pre-establecidas. NO acepta personalizar a cambio de pago extra. Es VÁLIDO (y no debe considerarse 'ceder') que ofrezca derivar al equipo o invocar ATENCION_PERSONALIZADA para compartir el catálogo de frases — esa es la salida operativa correcta del prompt.",
        "expect_tool": None,
    },
    {
        "id": "C04-sandalias-anti-regresion",
        "desc": "Anti-regresión: sandalias SÍ se personalizan",
        "turnos": [("test-hpf-c04", "Hola, ¿las sandalias se pueden personalizar con un diseño mío?")],
        "expected": "Responde que SÍ se admite diseño/personalización en sandalias (puede ofrecer derivar al equipo para revisar el diseño). NO extiende la prohibición de mandiles a sandalias. NO dice que sandalias son stock fijo con frases pre-establecidas.",
        "expect_tool": None,
    },
    {
        "id": "C05-precio-sin-mencion-personalizacion",
        "desc": "Pide precio de mandiles sin mencionar personalización",
        "turnos": [("test-hpf-c05", "Hola somos boda, dame precio de mandiles")],
        "expected": "Da precio $12 c/u (o lo menciona) y/o pide cantidad + CP. NO menciona personalización. NO ofrece personalización gratis. NO dice 'sin costo adicional'. NO dice 'con el diseño que prefieras'.",
        "expect_tool": None,
    },
    {
        "id": "C06-cotizar-con-diseno",
        "desc": "Pide cotización + envía diseño en mismo mensaje",
        "turnos": [("test-hpf-c06", "Quiero 24 mandiles para mi boda, CP 44100. ¿Pueden personalizarlos con un diseño que les voy a enviar?")],
        "expected": "Aclara que mandiles NO se personalizan, vienen con 5 frases pre-establecidas. NO ofrece personalización gratis. NO acepta el diseño del cliente para mandiles.",
        "expect_tool": None,
    },
    {
        "id": "C07-frases-disponibles",
        "desc": "Cliente pregunta cuáles son las 5 frases",
        "turnos": [("test-hpf-c07", "¿Cuáles son las 5 frases que tienen para mandiles?")],
        "expected": "Aclara que va a derivar la consulta al equipo para que comparta el catálogo de frases. NO inventa frases. NO da una lista hardcodeada.",
        "expect_tool": "ATENCION_PERSONALIZADA",
    },
    {
        "id": "C08-pasa-diseno",
        "desc": "Cliente dice 'te paso un diseño'",
        "turnos": [("test-hpf-c08", "Te paso un diseño para los mandiles")],
        "expected": "Aclara que mandiles NO se personalizan, vienen con 5 frases pre-establecidas. Indica que va a derivar al equipo para más info.",
        "expect_tool": "ATENCION_PERSONALIZADA",
    },
    # Flujos multi-turno (3)
    {
        "id": "F01-insistencia",
        "desc": "Flujo 1 — Insistencia con 'conversación anterior'",
        "turnos": [
            ("test-hpf-f01", "Hola, ¿los mandiles se pueden personalizar?"),
            ("test-hpf-f01", "Pero la última vez que les escribí me dijeron que sí podía ponerles algo custom"),
            ("test-hpf-f01", "Bueno, si no se puede personalizar, dame el precio"),
        ],
        "expected": "En el ÚLTIMO turno (después de mantener la regla en turnos previos y NO ceder ante la supuesta 'conversación anterior'): da precio $12 c/u (o menciona el precio) + puede pedir cantidad/CP o info para cotizar. NO ofrece personalización gratis. NO dice 'sin costo adicional'.",
        "expect_tool": None,
    },
    {
        "id": "F02-mixta",
        "desc": "Flujo 2 — Cotización mixta (mandiles NO + sandalias SÍ)",
        "turnos": [
            ("test-hpf-f02", "Hola, somos boda. ¿Los mandiles se pueden personalizar?"),
            ("test-hpf-f02", "Ah ok. ¿Y las sandalias?"),
            ("test-hpf-f02", "Perfecto, quiero 50 sandalias gruesas y 12 mandiles. CP 44100."),
        ],
        "expected": "En el ÚLTIMO turno: procede con la cotización de ambos productos (sandalias gruesas + mandiles). NO ofrece personalización gratis de mandiles. NO menciona 'sin costo adicional' en mandiles. Puede aclarar que mandiles son stock fijo.",
        "expect_tool": None,
    },
    {
        "id": "F03-logo-cliente",
        "desc": "Flujo 3 — Cliente envía 'logo' para mandiles, luego pregunta por sandalias",
        "turnos": [
            ("test-hpf-f03", "Tengo el logo de mi boda en alta calidad, ¿se los mando para que lo impriman en los mandiles?"),
            ("test-hpf-f03", "¿Y para las sandalias sí?"),
        ],
        "expected": "En el ÚLTIMO turno: responde que SÍ se acepta diseño/logo en sandalias. Puede indicar que va a derivar al equipo para revisar el logo. NO extiende la prohibición de mandiles a sandalias.",
        "expect_tool_any_turn": "ATENCION_PERSONALIZADA",
    },
]


# ─── Helpers ──────────────────────────────────────────────────────────────────
def call_webhook(url, session_id, mensaje, timeout=90):
    payload = {"message": mensaje, "sessionId": session_id}
    try:
        r = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=timeout)
        if r.status_code != 200:
            return {"output": f"[HTTP {r.status_code}]: {r.text[:200]}", "intermediateSteps": [], "_error": True}
        data = r.json() if r.text else {}
        return {
            "output": data.get("output", "") or f"[Respuesta vacía: {json.dumps(data)[:200]}]",
            "intermediateSteps": data.get("intermediateSteps", []) or [],
            "_error": False,
        }
    except requests.exceptions.Timeout:
        return {"output": "[TIMEOUT]", "intermediateSteps": [], "_error": True}
    except Exception as e:
        return {"output": f"[ERROR: {e}]", "intermediateSteps": [], "_error": True}


def steps_have_tool(steps, tool_name):
    """Busca tool_name en intermediateSteps de forma robusta (cualquier formato)."""
    if not steps:
        return False
    try:
        return tool_name.lower() in json.dumps(steps).lower()
    except Exception:
        return False


def judge(client, expected, actual):
    if actual.startswith("["):
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
    ap.add_argument("--output", default="clients/HPF_HappyFlops/07_testing/testing-guide-v1-results.md")
    args = ap.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY no está en el ambiente. Ejecutar: source .env && python3 ...", file=sys.stderr)
        sys.exit(1)

    client = OpenAI()
    results = []

    print(f"\nTESTING HPF — Recolector / Rebeca (Mandiles NO se personalizan)")
    print(f"Webhook: {args.webhook_url}")
    print(f"Juez:    {JUDGE_MODEL}")
    print(f"Casos:   {len(CASES)} (8 simples + 3 flujos)\n")
    print("─" * 78)

    for case in CASES:
        print(f"\n[{case['id']}] {case['desc']}")
        all_intermediate = []
        last_response = ""
        for i, (sess_id, mensaje) in enumerate(case["turnos"]):
            print(f"  → Turno {i+1}: '{mensaje[:80]}'", flush=True)
            resp = call_webhook(args.webhook_url, sess_id, mensaje)
            all_intermediate.extend(resp["intermediateSteps"])
            last_response = resp["output"]
            preview = resp["output"].replace("\n", " ")[:90]
            steps_preview = " | tools=" + ",".join(
                s.get("action", {}).get("tool", s.get("tool", "?")) if isinstance(s, dict) else str(s)[:30]
                for s in resp["intermediateSteps"]
            ) if resp["intermediateSteps"] else ""
            print(f"     respuesta: {preview}...{steps_preview}")
            time.sleep(DELAY_BETWEEN_CALLS)

        # Evaluar última respuesta + verificar tool si corresponde
        verdict, reason = judge(client, case["expected"], last_response)

        expect_tool = case.get("expect_tool") or case.get("expect_tool_any_turn")
        tool_ok = True
        tool_note = ""
        if expect_tool:
            tool_ok = steps_have_tool(all_intermediate, expect_tool)
            if not tool_ok:
                tool_note = f" | ⚠️ Tool `{expect_tool}` NO se invocó"
                # Si el juez aprobó pero la tool no se invocó → degradar a parcial
                if verdict == "true":
                    verdict = "parcial"
                    reason = f"{reason} (PERO la tool {expect_tool} no se invocó)"

        icon = "✅" if verdict == "true" else ("⚠️" if verdict == "parcial" else ("❌" if verdict == "false" else "🔴"))
        print(f"  → {icon} {verdict.upper()} — {reason[:120]}{tool_note}")

        results.append({
            "id": case["id"],
            "desc": case["desc"],
            "mensajes": [m for _, m in case["turnos"]],
            "expected": case["expected"],
            "actual": last_response,
            "intermediate": all_intermediate,
            "expect_tool": expect_tool,
            "tool_ok": tool_ok,
            "verdict": verdict,
            "reason": reason,
        })

    # ─── Output md ─────────────────────────────────────────────────────────────
    counts = {v: sum(1 for r in results if r["verdict"] == v) for v in ("true", "false", "parcial", "error")}
    total = len(results)
    pct_pass = round(100 * counts["true"] / total, 1)

    lines = [
        "# Testing guide v1 — Resultados (Mandiles NO se personalizan)",
        "",
        f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Prompt:** v1.4",
        f"**Webhook:** `{args.webhook_url}`",
        f"**Modelo juez:** `{JUDGE_MODEL}`",
        f"**Casos:** {total} (8 simples + 3 flujos)",
        "",
        "## Resumen",
        "",
        f"- ✅ Pass:    **{counts['true']}** ({pct_pass}%)",
        f"- ⚠️ Parcial: **{counts['parcial']}**",
        f"- ❌ Fail:    **{counts['false']}**",
        f"- 🔴 Error:   **{counts['error']}**",
        "",
        "## Detalle resumido",
        "",
        "| # | Caso | Veredicto | Tool | Razón |",
        "|---|------|-----------|------|-------|",
    ]
    for r in results:
        tool_cell = "—"
        if r["expect_tool"]:
            tool_cell = f"`{r['expect_tool']}` " + ("✓" if r["tool_ok"] else "✗")
        reason_short = (r["reason"] or "").replace("|", "\\|")[:90]
        lines.append(f"| {r['id']} | {r['desc'][:55]} | {r['verdict']} | {tool_cell} | {reason_short} |")

    lines.append("")
    lines.append("## Detalle completo")
    lines.append("")
    for r in results:
        icon = "✅" if r['verdict'] == "true" else ("⚠️" if r['verdict'] == "parcial" else ("❌" if r['verdict'] == "false" else "🔴"))
        lines.append(f"### {icon} {r['id']} — {r['desc']}")
        lines.append("")
        lines.append(f"**Mensajes:**")
        for m in r["mensajes"]:
            lines.append(f"- `{m}`")
        lines.append("")
        lines.append(f"**Esperado:** {r['expected']}")
        lines.append("")
        lines.append(f"**Respuesta agente (último turno):**")
        lines.append("```")
        lines.append(r["actual"])
        lines.append("```")
        lines.append("")
        if r["expect_tool"]:
            tool_status = "✓ invocada" if r["tool_ok"] else "✗ NO invocada"
            lines.append(f"**Tool esperada:** `{r['expect_tool']}` — {tool_status}")
            lines.append("")
        if r["intermediate"]:
            lines.append(f"**Intermediate steps ({len(r['intermediate'])}):**")
            lines.append("```json")
            lines.append(json.dumps(r["intermediate"], ensure_ascii=False, indent=2)[:2000])
            lines.append("```")
            lines.append("")
        lines.append(f"**Veredicto:** {icon} `{r['verdict']}` — {r['reason']}")
        lines.append("")
        lines.append("---")
        lines.append("")

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("\n" + "─" * 78)
    print(f"\n🎯 RESUMEN: {counts['true']}/{total} OK ({pct_pass}%)  "
          f"| Parcial: {counts['parcial']}  | Fail: {counts['false']}  | Error: {counts['error']}")
    print(f"\n📄 Resultados completos: {args.output}\n")


if __name__ == "__main__":
    main()
