#!/usr/bin/env python3
"""
run-agent-tests.py — Test runner automático para agentes conversacionales de IA.

Ejecuta los casos de una guía de testing contra la OpenAI API usando el modelo
configurado en n8n, evalúa respuestas con LLM-as-judge, y genera dos outputs:
  - {output}-auto-results.md : casos automatizables con resultados completos
  - {output}-manual.md       : casos que requieren tool calls (verificación humana)

Invocado por el skill /iterar-prompt en los pasos A.7b y B.7b.
"""

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from typing import Optional

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai no está instalado. Ejecutar: pip install openai", file=sys.stderr)
    sys.exit(2)

# ─── Constantes ──────────────────────────────────────────────────────────────

TOOL_CALL_PATTERN = re.compile(r"\[([A-Z][A-Z0-9_]+)\]")
TEMPERATURE = 0.2
RATE_LIMIT_DELAY = 0.5  # segundos entre llamadas

JUDGE_PROMPT = """\
Eres un evaluador de agentes conversacionales de IA. Tu tarea es determinar si \
la respuesta real de un agente satisface el comportamiento esperado.

## Comportamiento esperado:
{expected}

## Respuesta real del agente:
{actual}

Evalúa si la respuesta real cumple con lo esperado. Considera:
1. ¿Cubre los elementos clave requeridos?
2. ¿Evita los comportamientos prohibidos (ítems con "NO", "sin", "NUNCA", "jamás")?
3. ¿El tono e intención general están alineados?

NO penalices por:
- Diferencias menores de redacción o frases sinónimas
- Contenido adicional útil que no contradice lo esperado

Respondé con EXACTAMENTE un JSON (sin markdown, sin explicación extra):
{{"verdict": "true" | "false" | "parcial", "reason": "una oración en español explicando por qué"}}
"""


# ─── Estructuras de datos ─────────────────────────────────────────────────────

@dataclass
class SimpleCase:
    number: str
    message: str
    expected: str
    actual: str = ""
    verdict: str = ""
    reason: str = ""
    tool_calls: list = field(default_factory=list)

    @property
    def is_manual_only(self):
        return bool(self.tool_calls)


@dataclass
class FlowTurn:
    turn: str
    role: str          # "Usuario" o "Agente"
    message: str       # el mensaje a enviar (rol Usuario) o vacío (rol Agente)
    expected: str      # resultado esperado para el turno Agente
    actual: str = ""
    verdict: str = ""
    reason: str = ""
    tool_calls: list = field(default_factory=list)

    @property
    def is_manual_only(self):
        return bool(self.tool_calls)


@dataclass
class FlowCase:
    name: str
    turns: list  # lista de FlowTurn


# ─── Extracción del system prompt ─────────────────────────────────────────────

def extract_system_prompt(path: str) -> str:
    """Extrae el prompt puro desde un archivo markdown.

    Busca el primer bloque de código largo (>100 chars) después de un heading
    que contenga "System Prompt" o "system prompt". Si no encuentra, usa el
    archivo completo.
    """
    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Buscar bloque de código después de heading relevante
    sections = re.split(r'\n#{1,3} ', content)
    for i, section in enumerate(sections):
        if re.search(r'system.?prompt', section, re.IGNORECASE):
            # Buscar el primer bloque de código en esta sección
            code_blocks = re.findall(r'```+\n?(.*?)```+', section, re.DOTALL)
            for block in code_blocks:
                stripped = block.strip()
                if len(stripped) > 100:
                    return stripped

    # Fallback: buscar cualquier bloque de código largo en el archivo
    code_blocks = re.findall(r'```+\n?(.*?)```+', content, re.DOTALL)
    for block in code_blocks:
        stripped = block.strip()
        if len(stripped) > 100:
            return stripped

    # Último fallback: usar el archivo completo
    return content.strip()


# ─── Parser de guía de testing ────────────────────────────────────────────────

def _strip_backticks(text: str) -> str:
    return text.strip().strip("`").strip()


def _detect_tool_calls(text: str) -> list:
    return TOOL_CALL_PATTERN.findall(text)


def parse_simple_table(rows: list) -> list:
    """Parsea una tabla de casos simples."""
    cases = []
    for row in rows:
        cells = [c.strip() for c in row.strip("|").split("|")]
        if len(cells) < 3:
            continue
        num = cells[0].strip()
        if not num or num == "#" or num.startswith("---") or num.startswith(":"):
            continue
        message = _strip_backticks(cells[1])
        expected = cells[2].strip()
        if not message and not expected:
            continue
        tool_calls = _detect_tool_calls(expected)
        cases.append(SimpleCase(
            number=num,
            message=message,
            expected=expected,
            tool_calls=tool_calls,
        ))
    return cases


def parse_flow_table(rows: list, flow_name: str) -> FlowCase:
    """Parsea una tabla de flujo conversacional."""
    turns = []
    for row in rows:
        cells = [c.strip() for c in row.strip("|").split("|")]
        if len(cells) < 4:
            continue
        turn_num = cells[0].strip()
        if not turn_num or turn_num.lower() == "turno" or turn_num.startswith("---") or turn_num.startswith(":"):
            continue
        role = cells[1].strip()
        message = _strip_backticks(cells[2])
        expected = cells[3].strip() if len(cells) > 3 else ""
        tool_calls = _detect_tool_calls(expected)
        turns.append(FlowTurn(
            turn=turn_num,
            role=role,
            message=message,
            expected=expected,
            tool_calls=tool_calls,
        ))
    return FlowCase(name=flow_name, turns=turns)


def parse_testing_guide(path: str) -> tuple:
    """Parsea la guía de testing y retorna (simple_cases, flow_cases)."""
    with open(path, encoding="utf-8") as f:
        content = f.read()

    simple_cases = []
    flow_cases = []

    lines = content.split("\n")
    i = 0
    current_section = ""
    current_flow_name = ""

    while i < len(lines):
        line = lines[i]

        # Detectar headings para nombre de sección/flujo
        if re.match(r'^#{1,4} ', line):
            current_section = line.lstrip("#").strip()
        if re.match(r'^\*\*(?:Rama|Flujo)\s+', line, re.IGNORECASE):
            current_flow_name = line.strip("*").strip()

        # Detectar inicio de tabla
        if line.strip().startswith("|"):
            # Recopilar todas las filas de la tabla
            table_rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_rows.append(lines[i])
                i += 1

            if not table_rows:
                continue

            # Detectar tipo por el header
            header = table_rows[0].lower()
            if "turno" in header and "rol" in header:
                name = current_flow_name or current_section or f"Flujo {len(flow_cases)+1}"
                flow = parse_flow_table(table_rows[2:], name)  # skip header + separator
                if flow.turns:
                    flow_cases.append(flow)
            elif "mensaje" in header or "# |" in header or re.search(r'\|\s*#\s*\|', header):
                cases = parse_simple_table(table_rows[2:])  # skip header + separator
                simple_cases.extend(cases)
            continue

        i += 1

    return simple_cases, flow_cases


# ─── Llamadas a OpenAI ────────────────────────────────────────────────────────

def call_agent(client: OpenAI, model: str, system_prompt: str, messages: list) -> str:
    """Llama al modelo del agente y retorna la respuesta."""
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    try:
        response = client.chat.completions.create(
            model=model,
            messages=full_messages,
            temperature=TEMPERATURE,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        return f"[ERROR API: {e}]"


def call_judge(client: OpenAI, judge_model: str, expected: str, actual: str) -> tuple:
    """Evalúa la respuesta del agente y retorna (verdict, reason)."""
    prompt = JUDGE_PROMPT.format(expected=expected, actual=actual)
    try:
        response = client.chat.completions.create(
            model=judge_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        raw = response.choices[0].message.content or ""
        # Extraer JSON de la respuesta
        json_match = re.search(r'\{.*?\}', raw, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data.get("verdict", "parcial"), data.get("reason", "")
        return "parcial", f"No se pudo parsear la respuesta del juez: {raw[:100]}"
    except json.JSONDecodeError as e:
        return "parcial", f"JSON inválido del juez: {e}"
    except Exception as e:
        return "error", f"Error del juez: {e}"


# ─── Ejecución de tests ───────────────────────────────────────────────────────

def run_simple_cases(client: OpenAI, model: str, judge_model: str,
                     system_prompt: str, cases: list, dry_run: bool) -> list:
    results = []
    for case in cases:
        if dry_run:
            print(f"  [DRY-RUN] Caso #{case.number}: {case.message[:60]}")
            if case.is_manual_only:
                print(f"    → manual-only: {case.tool_calls}")
            results.append(case)
            continue

        print(f"  → Caso #{case.number}...", end=" ", flush=True)
        actual = call_agent(client, model, system_prompt, [{"role": "user", "content": case.message}])
        time.sleep(RATE_LIMIT_DELAY)

        if case.is_manual_only:
            # Evaluar solo la parte textual, marcar como manual-only
            verdict, reason = call_judge(client, judge_model, case.expected, actual)
            time.sleep(RATE_LIMIT_DELAY)
            case.actual = actual
            case.verdict = "manual-only"
            case.reason = f"Tool calls: {case.tool_calls}. Respuesta textual: {verdict} — {reason}"
            print("manual-only")
        else:
            verdict, reason = call_judge(client, judge_model, case.expected, actual)
            time.sleep(RATE_LIMIT_DELAY)
            case.actual = actual
            case.verdict = verdict
            case.reason = reason
            print(verdict)

        results.append(case)
    return results


def run_flow_cases(client: OpenAI, model: str, judge_model: str,
                   system_prompt: str, flows: list, dry_run: bool) -> list:
    results = []
    for flow in flows:
        print(f"  → Flujo: {flow.name}")
        messages = []
        pending_expected = None
        pending_turn = None

        for turn in flow.turns:
            if dry_run:
                print(f"    Turno {turn.turn} [{turn.role}]: {turn.message[:50] if turn.message else '—'}")
                if turn.is_manual_only:
                    print(f"      → manual-only: {turn.tool_calls}")
                continue

            if turn.role.lower() in ("usuario", "user"):
                messages.append({"role": "user", "content": turn.message})
                pending_expected = turn.expected if turn.expected and turn.expected != "—" else None
                pending_turn = turn
            elif turn.role.lower() in ("agente", "agent", "assistant"):
                # Llamar al agente con el historial acumulado
                actual = call_agent(client, model, system_prompt, messages)
                time.sleep(RATE_LIMIT_DELAY)

                expected = turn.expected
                is_manual = turn.is_manual_only

                # Turno sin criterio de evaluación (—): aceptar cualquier respuesta
                if not expected or expected.strip() == "—":
                    turn.actual = actual
                    turn.verdict = "true"
                    turn.reason = "Sin criterio de evaluación especificado."
                    print(f"    Turno {turn.turn} [Agente]: skip (sin criterio)")
                elif is_manual:
                    turn.actual = actual
                    turn.verdict = "manual-only"
                    verdict, reason = call_judge(client, judge_model, expected, actual)
                    time.sleep(RATE_LIMIT_DELAY)
                    turn.reason = f"Tool calls: {turn.tool_calls}. Textual: {verdict} — {reason}"
                    print(f"    Turno {turn.turn} [Agente]: manual-only")
                else:
                    verdict, reason = call_judge(client, judge_model, expected, actual)
                    time.sleep(RATE_LIMIT_DELAY)
                    turn.actual = actual
                    turn.verdict = verdict
                    turn.reason = reason
                    print(f"    Turno {turn.turn} [Agente]: {verdict}")

                # Agregar la respuesta del agente al historial
                messages.append({"role": "assistant", "content": actual})

        results.append(flow)
    return results


# ─── Generación de outputs ────────────────────────────────────────────────────

def _truncate(text: str, max_len: int = 150) -> str:
    text = text.replace("\n", " ").strip()
    if len(text) > max_len:
        return text[:max_len] + "…"
    return text


def generate_auto_results(simple_cases: list, flow_cases: list,
                           model: str, judge_model: str, output_path: str):
    """Genera el archivo de resultados automáticos."""
    lines = [
        f"# Resultados de Testing Automatizado\n",
        f"**Modelo testeado:** `{model}`",
        f"**Modelo juez:** `{judge_model}`",
        f"**Temperatura:** {TEMPERATURE}\n",
        "---\n",
    ]

    # Casos simples automatizables
    auto_simple = [c for c in simple_cases if not c.is_manual_only]
    if auto_simple:
        lines.append("## Casos Simples\n")
        lines.append("| # | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |")
        lines.append("|---|---------|-------------------|-------------------|----|-------|")
        for c in auto_simple:
            lines.append(
                f"| {c.number} | `{_truncate(c.message, 60)}` | {_truncate(c.expected, 80)} "
                f"| {_truncate(c.actual, 100)} | {c.verdict} | {c.reason} |"
            )
        lines.append("")

    # Flujos automatizables
    for flow in flow_cases:
        auto_turns = [t for t in flow.turns if not t.is_manual_only]
        if not auto_turns:
            continue
        lines.append(f"## {flow.name}\n")
        lines.append("| Turno | Rol | Mensaje | Resultado esperado | Resultado obtenido | OK | Notas |")
        lines.append("|-------|-----|---------|-------------------|-------------------|----|-------|")
        for t in flow.turns:
            if t.is_manual_only:
                continue
            msg = _truncate(t.message, 60) if t.message else "—"
            lines.append(
                f"| {t.turn} | {t.role} | `{msg}` | {_truncate(t.expected, 80)} "
                f"| {_truncate(t.actual, 100)} | {t.verdict} | {t.reason} |"
            )
        lines.append("")

    # Resumen
    all_simple_auto = [c for c in simple_cases if not c.is_manual_only]
    all_flow_turns_auto = [t for f in flow_cases for t in f.turns if not t.is_manual_only and t.role.lower() in ("agente", "agent", "assistant")]

    verdicts = [c.verdict for c in all_simple_auto] + [t.verdict for t in all_flow_turns_auto]
    count = {v: verdicts.count(v) for v in ("true", "false", "parcial", "error")}
    manual_count = sum(1 for c in simple_cases if c.is_manual_only) + sum(1 for f in flow_cases for t in f.turns if t.is_manual_only)

    lines.append("---\n")
    lines.append("## Resumen\n")
    lines.append("| Resultado | Cantidad |")
    lines.append("|-----------|----------|")
    for v in ("true", "false", "parcial", "error"):
        lines.append(f"| {v} | {count[v]} |")
    lines.append(f"| manual-only | {manual_count} |")
    lines.append("")

    failed = [c for c in all_simple_auto if c.verdict in ("false", "parcial")]
    failed_turns = [t for f in flow_cases for t in f.turns if t.verdict in ("false", "parcial") and not t.is_manual_only]
    if failed or failed_turns:
        lines.append("### Casos fallidos\n")
        for c in failed:
            lines.append(f"- **#{c.number}:** {c.reason}")
        for t in failed_turns:
            lines.append(f"- **Turno {t.turn}:** {t.reason}")
        lines.append("")

    # Respuestas completas en apéndice
    lines.append("---\n")
    lines.append("## Apéndice: Respuestas Completas\n")
    for c in all_simple_auto:
        if c.actual:
            lines.append(f"### Caso #{c.number}")
            lines.append(f"**Mensaje:** {c.message}")
            lines.append(f"**Respuesta:**\n{c.actual}\n")
    for flow in flow_cases:
        for t in flow.turns:
            if t.actual and not t.is_manual_only:
                lines.append(f"### {flow.name} — Turno {t.turn}")
                lines.append(f"**Respuesta:**\n{t.actual}\n")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def generate_manual_guide(simple_cases: list, flow_cases: list,
                           original_guide_path: str, output_path: str):
    """Genera la guía de testing manual con casos que requieren tool calls."""
    manual_simple = [c for c in simple_cases if c.is_manual_only]
    manual_flows = [f for f in flow_cases if any(t.is_manual_only for t in f.turns)]

    if not manual_simple and not manual_flows:
        return None  # No hay casos manuales

    lines = [
        "# Testing Manual — Casos con Tool Calls\n",
        "> ⚠️ Estos casos requieren verificación humana porque dependen de herramientas",
        "> reales de n8n que no se pueden simular via API.\n",
        "---\n",
        "## Instrucciones",
        "1. Ejecutar cada caso en n8n o en el canal real",
        "2. Completar **Resultado obtenido** con la respuesta del agente",
        "3. Marcar **OK** como `true`, `false` o `parcial`",
        "4. Verificar que la tool call se activó correctamente (ver logs de n8n)\n",
        "---\n",
    ]

    if manual_simple:
        lines.append("## Casos Simples\n")
        lines.append("| # | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |")
        lines.append("|---|---------|-------------------|----------------|-------------------|----|-------|")
        for c in manual_simple:
            tools = ", ".join(f"`{t}`" for t in c.tool_calls)
            lines.append(
                f"| {c.number} | `{c.message}` | {c.expected} | {tools} | | | |"
            )
        lines.append("")

    for flow in manual_flows:
        manual_turns = [t for t in flow.turns if t.is_manual_only]
        if not manual_turns:
            continue
        lines.append(f"## {flow.name}\n")
        lines.append("| Turno | Rol | Mensaje | Resultado esperado | Tool requerida | Resultado obtenido | OK | Notas |")
        lines.append("|-------|-----|---------|-------------------|----------------|-------------------|----|-------|")
        for t in flow.turns:
            if not t.is_manual_only:
                continue
            msg = t.message if t.message else "—"
            tools = ", ".join(f"`{tc}`" for tc in t.tool_calls)
            lines.append(
                f"| {t.turn} | {t.role} | `{msg}` | {t.expected} | {tools} | | | |"
            )
        lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return output_path


# ─── Main ─────────────────────────────────────────────────────────────────────

def build_summary(simple_cases: list, flow_cases: list) -> dict:
    """Construye el resumen de resultados para stdout."""
    auto_simple = [c for c in simple_cases if not c.is_manual_only]
    auto_turns = [t for f in flow_cases for t in f.turns
                  if not t.is_manual_only and t.role.lower() in ("agente", "agent", "assistant")]
    manual_count = sum(1 for c in simple_cases if c.is_manual_only)
    manual_count += sum(1 for f in flow_cases for t in f.turns if t.is_manual_only)

    verdicts = [c.verdict for c in auto_simple] + [t.verdict for t in auto_turns]
    count = {v: verdicts.count(v) for v in ("true", "false", "parcial", "error")}
    count["manual-only"] = manual_count
    count["total_auto"] = len(verdicts)

    failed = []
    for c in auto_simple:
        if c.verdict in ("false", "parcial"):
            failed.append({"id": f"#{c.number}", "reason": c.reason, "expected": c.expected})
    for f in flow_cases:
        for t in f.turns:
            if t.verdict in ("false", "parcial") and not t.is_manual_only:
                failed.append({"id": f"{f.name} T{t.turn}", "reason": t.reason, "expected": t.expected})

    return {"counts": count, "failed": failed}


def print_summary(summary: dict, model: str, judge_model: str):
    c = summary["counts"]
    total = c["total_auto"]
    passed = c["true"]
    print("\n" + "="*60)
    print(f"RESUMEN DE TESTING AUTOMATIZADO")
    print(f"Modelo: {model} | Juez: {judge_model}")
    print("="*60)
    print(f"  true       : {c['true']}/{total}")
    print(f"  false      : {c['false']}/{total}")
    print(f"  parcial    : {c['parcial']}/{total}")
    print(f"  manual-only: {c['manual-only']} (verificar en n8n)")
    if c.get("error"):
        print(f"  error      : {c['error']}")
    print("-"*60)
    if summary["failed"]:
        print("CASOS FALLIDOS:")
        for f in summary["failed"]:
            print(f"  {f['id']}: {f['reason']}")
    else:
        print("✅ Todos los casos automatizables pasaron.")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(description="Test runner para agentes conversacionales")
    parser.add_argument("--system-prompt", required=True, help="Ruta al archivo del system prompt")
    parser.add_argument("--testing-guide", required=True, help="Ruta a la guía de testing")
    parser.add_argument("--model", required=True, help="Model ID de OpenAI (ej: gpt-4.1-mini)")
    parser.add_argument("--output", help="Ruta base del output (sin extensión)")
    parser.add_argument("--judge-model", default="gpt-4o-mini", help="Modelo para el LLM judge")
    parser.add_argument("--dry-run", action="store_true", help="Parsear sin llamar a la API")
    args = parser.parse_args()

    # Verificar API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key and not args.dry_run:
        print("ERROR: OPENAI_API_KEY no está configurada.", file=sys.stderr)
        print("Agregar al .env: OPENAI_API_KEY=sk-... y ejecutar: source .env", file=sys.stderr)
        sys.exit(2)

    # Verificar que el modelo sea OpenAI
    non_openai = ["gemini", "claude", "llama", "mistral", "groq"]
    if any(n in args.model.lower() for n in non_openai):
        print(f"INFO: El modelo '{args.model}' no es compatible con OpenAI API.", file=sys.stderr)
        print("Auto-testing solo disponible para modelos OpenAI. Usar testing manual.", file=sys.stderr)
        sys.exit(2)

    # Determinar paths de output
    guide_base = args.output or args.testing_guide.replace(".md", "")
    auto_output = guide_base + "-auto-results.md"
    manual_output = guide_base + "-manual.md"

    print(f"\nExtrayendo system prompt desde: {args.system_prompt}")
    system_prompt = extract_system_prompt(args.system_prompt)
    print(f"  Prompt extraído: {len(system_prompt)} caracteres")

    print(f"\nParsando guía de testing: {args.testing_guide}")
    simple_cases, flow_cases = parse_testing_guide(args.testing_guide)
    total_simple = len(simple_cases)
    total_flows = len(flow_cases)
    manual_simple = sum(1 for c in simple_cases if c.is_manual_only)
    manual_flows = sum(1 for f in flow_cases if any(t.is_manual_only for t in f.turns))
    print(f"  Casos simples: {total_simple} ({manual_simple} manual-only)")
    print(f"  Flujos: {total_flows} ({manual_flows} con turns manual-only)")

    if total_simple == 0 and total_flows == 0:
        print("\nERROR: No se detectaron casos en la guía de testing.", file=sys.stderr)
        print("Verificar que las tablas usan exactamente las columnas:", file=sys.stderr)
        print("  Casos simples: | # | Mensaje | Resultado esperado |", file=sys.stderr)
        print("  Flujos: | Turno | Rol | Mensaje | Resultado esperado |", file=sys.stderr)
        print("No agregar columnas extra (Área, Flujo, OK, Resultado obtenido, {{ORIGEN}}).", file=sys.stderr)
        sys.exit(2)

    if args.dry_run:
        print("\n[DRY-RUN] Casos encontrados:\n")
        print("── Casos Simples ──")
        for c in simple_cases:
            tag = " [MANUAL-ONLY]" if c.is_manual_only else ""
            print(f"  #{c.number}: {c.message[:70]}{tag}")
        print("\n── Flujos ──")
        for flow in flow_cases:
            print(f"  {flow.name}:")
            for t in flow.turns:
                tag = " [MANUAL-ONLY]" if t.is_manual_only else ""
                print(f"    T{t.turn} [{t.role}]: {t.message[:50] if t.message else '—'}{tag}")
        sys.exit(0)

    client = OpenAI(api_key=api_key)

    print(f"\nEjecutando casos simples contra {args.model}...")
    simple_results = run_simple_cases(client, args.model, args.judge_model,
                                       system_prompt, simple_cases, args.dry_run)

    print(f"\nEjecutando flujos conversacionales...")
    flow_results = run_flow_cases(client, args.model, args.judge_model,
                                   system_prompt, flow_cases, args.dry_run)

    # Generar outputs
    print(f"\nGenerando resultados automáticos: {auto_output}")
    generate_auto_results(simple_results, flow_results, args.model, args.judge_model, auto_output)

    manual_path = generate_manual_guide(simple_results, flow_results, args.testing_guide, manual_output)
    if manual_path:
        print(f"Generando guía manual: {manual_output}")

    # Resumen en stdout
    summary = build_summary(simple_results, flow_results)
    print_summary(summary, args.model, args.judge_model)

    if summary["counts"]["manual-only"] > 0:
        print(f"\n📋 Guía de testing manual guardada en: {manual_output}")

    # Exit code según resultados
    if summary["failed"]:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
