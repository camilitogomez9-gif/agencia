#!/usr/bin/env python3
"""
meeting-summary: Genera un resumen inteligente de la última reunión grabada en Fathom.
Detecta el cliente desde el transcript y guarda el resumen en clients/[CLIENTE]/06_docs/.

Uso:
    python meeting_summary.py [--webhook-url URL] [--save] [--workspace PATH]

Env vars:
    ANTHROPIC_API_KEY   Requerida. API key de Anthropic.
    N8N_WEBHOOK_URL     Opcional. Override de la URL del webhook.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import anthropic
import requests

WEBHOOK_URL_DEFAULT = "https://[TU-INSTANCIA-N8N]/webhook/my-meeting-transcripts"
FALLBACK_CLIENT = "INT_Interno"

SYSTEM_PROMPT_BASE = """Sos un asistente especializado en resumir reuniones de trabajo de la agencia, \
una agencia de consultoría e implementación de IA en LATAM.

Tu tarea es analizar el transcript de una reunión, identificar el cliente involucrado, \
y generar un resumen estructurado y útil.

## Paso 1: Identificar el cliente

Leé el transcript e identificá con qué cliente de la agencia se relaciona la reunión. \
Usá la lista de clientes disponibles más abajo. Buscá menciones de nombres de empresas, \
personas, proyectos o contexto que permita asociar la reunión a un cliente específico.

Si no podés determinarlo con certeza, usá INT_Interno.

En la primera línea de tu respuesta escribí exactamente:
`CLIENTE: [carpeta_del_cliente]`

Por ejemplo: `CLIENTE: XXX_Cliente`

## Paso 2: Identificar el tipo de reunión

Leé el transcript y determiná a cuál de estas categorías corresponde:

1. **Reunión técnica interna (con colega técnico, ej. Juanpi)**: discuten flujos de n8n, \
integraciones, arquitectura de agentes, código, herramientas técnicas.

2. **Kick-off con cliente**: primera reunión formal con un cliente nuevo. Se presenta el negocio \
del cliente, el problema a resolver, se acuerdan pasos iniciales.

3. **Reunión de alineación con cliente**: reunión de seguimiento de un proyecto en curso. \
Se revisa el estado, se alinean expectativas, se definen próximos pasos.

4. **Otra reunión**: no matchea claramente con ninguna de las anteriores.

## Paso 3: Declarar el tipo detectado

En la segunda línea escribí exactamente:
`**Tipo de reunión detectado:** [tipo] — [una oración breve explicando por qué]`

## Paso 4: Generar el resumen según el tipo

### Para reunión técnica interna:
- **Descripción del flujo/solución**: qué se está construyendo o explicando
- **Nodos y herramientas involucradas**: tecnologías, integraciones, APIs mencionadas
- **Lógica del proceso**: cómo funciona paso a paso
- **Puntos clave a recordar**: decisiones, patrones, advertencias importantes
- **Preguntas abiertas**: dudas o pendientes que quedaron sin resolver (si las hay)

### Para kick-off con cliente:
- **Contexto del cliente**: quién es, a qué se dedica, escala relevante
- **Problema u objetivo**: qué quieren resolver o lograr con la IA
- **Acuerdos tomados**: qué se definió en la reunión
- **Próximos pasos**: con responsables si se mencionaron
- **Fechas y deadlines**: si se mencionaron

### Para reunión de alineación con cliente:
- **Estado actual del proyecto**: cómo estamos parados
- **Qué se acordó**: decisiones tomadas en la reunión
- **Qué cambió**: ajustes respecto a lo planeado
- **Obstáculos identificados**: problemas o bloqueos (si los hay)
- **Próximos pasos**: con responsables si se mencionaron

### Para otra reunión:
Generá un resumen con las secciones que realmente aporten valor dado el contenido. \
No uses secciones genéricas vacías.

## Reglas generales

- Usá español rioplatense, tono profesional pero directo
- Si hay nombres de personas mencionados, incluílos en el contexto correcto
- Omitir secciones que no apliquen — no rellenar con placeholders vacíos
- Ser concreto y accionable, no vago
- El resumen debe ser útil para alguien que no estuvo en la reunión

## Lista de clientes disponibles

{client_list}
"""


def get_workspace(explicit: Optional[str]) -> Path:
    if explicit:
        return Path(explicit).resolve()
    return Path(__file__).resolve().parent.parent.parent


def list_clients(workspace: Path) -> list[dict]:
    clients_dir = workspace / "clients"
    clients = []
    for d in sorted(clients_dir.iterdir()):
        if d.is_dir() and not d.name.startswith("_"):
            parts = d.name.split("_", 1)
            if len(parts) == 2:
                clients.append({"code": parts[0], "name": parts[1], "folder": d.name})
    return clients


def fetch_transcript(webhook_url: str) -> str:
    try:
        response = requests.post(
            webhook_url,
            json={},
            timeout=30,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("Error: el webhook de n8n no respondió en 30 segundos.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"Error: no se pudo conectar al webhook: {webhook_url}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP del webhook: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        data = response.json()
        if isinstance(data, dict):
            transcript = data.get("transcript") or data.get("text") or data.get("content")
            if transcript:
                return transcript
            return json.dumps(data, ensure_ascii=False, indent=2)
        return str(data)
    except (ValueError, json.JSONDecodeError):
        text = response.text.strip()
        if not text:
            print("Error: el webhook respondió con contenido vacío.", file=sys.stderr)
            sys.exit(1)
        return text


def generate_summary(transcript: str, clients: list[dict]) -> tuple[str, str]:
    """Returns (client_folder, summary_text)."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: la variable de entorno ANTHROPIC_API_KEY no está definida.", file=sys.stderr)
        sys.exit(1)

    if not transcript.strip():
        print("Error: el transcript está vacío.", file=sys.stderr)
        sys.exit(1)

    client_list = "\n".join(f"- {c['folder']}" for c in clients)
    system_prompt = SYSTEM_PROMPT_BASE.format(client_list=client_list)

    anthropic_client = anthropic.Anthropic(api_key=api_key)

    try:
        message = anthropic_client.messages.create(
            model="claude-opus-4-7",
            max_tokens=4096,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"Aquí está el transcript de la reunión:\n\n{transcript}",
                }
            ],
        )
    except anthropic.AuthenticationError:
        print("Error: ANTHROPIC_API_KEY inválida.", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIError as e:
        print(f"Error de la API de Anthropic: {e}", file=sys.stderr)
        sys.exit(1)

    full_response = message.content[0].text
    lines = full_response.splitlines()

    # Parse CLIENTE: line and strip it from the summary
    client_folder = FALLBACK_CLIENT
    summary_lines = lines

    if lines and lines[0].startswith("CLIENTE:"):
        detected = lines[0].replace("CLIENTE:", "").strip()
        valid_folders = {c["folder"] for c in clients}
        if detected in valid_folders:
            client_folder = detected
        summary_lines = lines[1:]

    summary = "\n".join(summary_lines).lstrip("\n")
    return client_folder, summary


def save_summary(summary: str, workspace: Path, client_folder: str) -> Path:
    docs_dir = workspace / "clients" / client_folder / "06_docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    filename = docs_dir / f"resumen_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.md"
    filename.write_text(summary, encoding="utf-8")
    return filename


def main():
    parser = argparse.ArgumentParser(
        description="Genera un resumen inteligente de la última reunión grabada en Fathom."
    )
    parser.add_argument(
        "--webhook-url",
        default=os.environ.get("N8N_WEBHOOK_URL", WEBHOOK_URL_DEFAULT),
        help="URL del webhook de n8n",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Guardar el resumen en clients/[CLIENTE]/06_docs/resumen_YYYY-MM-DD_HH-MM.md",
    )
    parser.add_argument(
        "--workspace",
        default=None,
        help="Ruta al workspace de la agencia (default: dos niveles arriba del script)",
    )
    args = parser.parse_args()

    workspace = get_workspace(args.workspace)
    clients = list_clients(workspace)

    print("Fetcheando transcript desde n8n...", flush=True)
    transcript = fetch_transcript(args.webhook_url)

    print("Generando resumen con Claude...\n", flush=True)
    client_folder, summary = generate_summary(transcript, clients)

    print(f"Cliente detectado: {client_folder}\n")
    print(summary)

    if args.save:
        saved_path = save_summary(summary, workspace, client_folder)
        print(f"\n---\nResumen guardado en: {saved_path}")


if __name__ == "__main__":
    main()
