#!/usr/bin/env python3
"""
backfill-vtr-chat-memory.py — REFERENCIA / DEPRECATED como entry point
=====================================================================

⚠️ ESTE SCRIPT NO SE USA PARA EL DEPLOY REAL.

El deploy del backfill se hace ahora vía el workflow n8n:
    `clients/VTR_Venttur/03_workflows/backfill-vtr-chat-memory-v1.json`

Razón: el Postgres de VTR vive en Supabase, sin acceso directo desde fuera.
La credencial `Venttur` ya está cableada en n8n (id `ihpvM7nYMdLCwWDP`),
así que el flujo lee Airtable + escribe Postgres todo desde n8n.

Este archivo se conserva como REFERENCIA porque:
- Los 3 textos canónicos de Touch 1/2/3 viven acá (espejo del workflow n8n).
- La función `build_system_message()` documenta la lógica de prosa natural
  que el Code node `Build Messages` del workflow replica en JS.
- Útil para debug local: validar la salida de prosa con un lead específico
  sin tocar n8n (corriendo solo `build_system_message()`).

Si en algún momento se obtiene acceso directo al Postgres de VTR, este
script seguiría funcional con las env vars indicadas abajo.

Uso (solo si Postgres VTR accesible localmente):
    python3 backfill-vtr-chat-memory.py --dry-run
    python3 backfill-vtr-chat-memory.py
    python3 backfill-vtr-chat-memory.py --limit 5

Env vars requeridas (NO disponibles en este workspace al 2026-06-23):
    AIRTABLE_API_KEY        Personal Access Token de Airtable
    VTR_POSTGRES_URL        Connection string del Postgres Venttur, ej:
                            postgres://USER:PASS@HOST:5432/DB
                            (o usar VTR_POSTGRES_HOST/PORT/DB/USER/PASSWORD)

Dependencias (si se ejecuta):
    pip install requests psycopg2-binary python-dotenv
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import psycopg2
import psycopg2.extras
import requests
from dotenv import load_dotenv


# === Constantes Airtable VTR ===
AIRTABLE_BASE_ID = "[AIRTABLE_BASE_ID]"
LEADS_TABLE_ID = "[AIRTABLE_TABLE_ID]"
AIRTABLE_API_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{LEADS_TABLE_ID}"

# Filtro: leads que recibieron al menos Touch 1
AIRTABLE_FILTER = "AND({Outreach Form Meta enviado}=TRUE(), {Telefono}!=BLANK())"

# Campos del lead que vamos a leer
LEAD_FIELDS = [
    "Nombre", "Apellido", "Nombre Completo", "Telefono", "Email",
    "Programa interés", "Grado Escolar", "Inicio Deseado", "Nivel Inglés",
    "Ad Name", "Platform", "Origen", "Fuente lead", "Tipo",
    "Toques enviados", "Outreach Form Meta enviado at", "Ultimo toque at",
    "ID Manychat", "Folio",
]


# === Texto canónico de templates ===
# IMPORTANTE: estos placeholders deben reemplazarse con los textos literales
# aprobados por Meta. Ver clients/VTR_Venttur/06_docs/template-texts-canonical.md

TOUCH_1_TEXT = (
"Hola {{first_name}}, gracias por tu interés en nuestros programas de Boarding School.

Vimos que recientemente solicitaste información sobre opciones de estudio en el extranjero.

Me gustaría conocer un poco más sobre tu interés para poder orientarte mejor. ¿El programa sería para tu hijo(a) o para algún familiar?"
)

TOUCH_2_TEXT = (
"Hola {{first_name}},

Muchos padres nos contactan porque quieren brindarles a sus hijos una experiencia internacional que los ayude a desarrollar independencia, confianza y una visión global para su futuro.

Cada estudiante tiene objetivos distintos, por eso nos gustaría entender mejor tu caso para orientarte adecuadamente.

¿Para qué edad o grado escolar estás buscando opciones?"
)

TOUCH_3_TEXT = (
"Hola {{first_name}},

Sabemos que elegir una experiencia educativa internacional es una decisión importante y que normalmente surgen muchas preguntas sobre destinos, seguridad, costos, requisitos y beneficios para el futuro del estudiante.

Nuestro objetivo es ayudarte a encontrar la mejor opción según las metas y necesidades de tu familia.

Si aún estás explorando alternativas, responde este mensaje y con gusto te orientaremos sin compromiso."
)


# === Helpers ===

def normalize_phone(raw: str | None) -> str | None:
    """Replica la normalización del nodo Normalize Payload del v2."""
    if not raw:
        return None
    cleaned = "".join(c for c in str(raw) if c.isdigit())
    if len(cleaned) < 10 or len(cleaned) > 15:
        return None
    return cleaned


def build_system_message(lead: dict) -> str:
    """Construye la prosa natural con los datos del form."""
    fields = lead.get("fields", {})
    nombre = (fields.get("Nombre") or "").strip()
    apellido = (fields.get("Apellido") or "").strip()
    nombre_completo = fields.get("Nombre Completo") or " ".join(
        x for x in [nombre, apellido] if x
    ) or "el lead"

    email = fields.get("Email") or ""
    telefono = fields.get("Telefono") or ""

    contact_parts = []
    if email:
        contact_parts.append(email)
    if telefono:
        contact_parts.append(f"tel +{telefono}")
    contact_str = f" ({', '.join(contact_parts)})" if contact_parts else ""

    origen_map = {
        "Form Meta": "completó un formulario de Meta",
        "Form Landing": "completó el formulario de nuestra landing",
        "CTWA": "vino por un anuncio de WhatsApp",
    }
    accion = origen_map.get(fields.get("Origen") or "", "mostró interés")

    programa_int = fields.get("Programa interés")
    programa = (
        f" interesado/a en {programa_int}"
        if programa_int
        else " interesado/a en uno de nuestros programas"
    )

    cualif_parts = []
    if fields.get("Grado Escolar"):
        cualif_parts.append(f"para {fields['Grado Escolar']}")
    if fields.get("Inicio Deseado"):
        cualif_parts.append(f"con inicio deseado en {fields['Inicio Deseado']}")
    if fields.get("Nivel Inglés"):
        cualif_parts.append(f"y nivel de inglés {fields['Nivel Inglés']}")
    cualif_str = f" {' '.join(cualif_parts)}" if cualif_parts else ""

    ad_name = fields.get("Ad Name")
    platform = fields.get("Platform")
    campania = ""
    if ad_name:
        campania = f" Vino por la campaña {ad_name}"
        if platform:
            campania += f" en {platform}"
        campania += "."

    return f"El lead {nombre_completo}{contact_str} {accion}{programa}{cualif_str}.{campania}"


def render_template(template: str, first_name: str | None) -> str:
    fn = (first_name or "").strip() or "hola"
    return template.replace("{{first_name}}", fn)


def parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        if s.endswith("Z"):
            s = s.replace("Z", "+00:00")
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


# === Airtable ===

def fetch_all_leads(api_key: str, max_records: int | None = None) -> list[dict]:
    """Page through Airtable, returns list of records."""
    headers = {"Authorization": f"Bearer {api_key}"}
    records: list[dict] = []
    offset: Optional[str] = None
    page = 0
    while True:
        page += 1
        params = {
            "filterByFormula": AIRTABLE_FILTER,
            "pageSize": 100,
            "fields[]": LEAD_FIELDS,
        }
        if offset:
            params["offset"] = offset
        resp = requests.get(AIRTABLE_API_URL, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        records.extend(data.get("records", []))
        print(f"  Airtable page {page}: +{len(data.get('records', []))} records (total: {len(records)})")
        if max_records and len(records) >= max_records:
            return records[:max_records]
        offset = data.get("offset")
        if not offset:
            break
        time.sleep(0.2)  # gentle rate limit
    return records


# === Postgres ===

def get_pg_connection() -> psycopg2.extensions.connection:
    url = os.environ.get("VTR_POSTGRES_URL")
    if url:
        return psycopg2.connect(url)
    return psycopg2.connect(
        host=os.environ["VTR_POSTGRES_HOST"],
        port=int(os.environ.get("VTR_POSTGRES_PORT", "5432")),
        dbname=os.environ["VTR_POSTGRES_DB"],
        user=os.environ["VTR_POSTGRES_USER"],
        password=os.environ["VTR_POSTGRES_PASSWORD"],
    )


def session_already_exists(cur: psycopg2.extensions.cursor, session_id: str) -> bool:
    cur.execute(
        "SELECT 1 FROM n8n_chat_histories WHERE session_id = %s LIMIT 1;",
        (session_id,),
    )
    return cur.fetchone() is not None


def insert_message(
    cur: psycopg2.extensions.cursor,
    session_id: str,
    msg_type: str,
    content: str,
    created_at: datetime | None = None,
) -> int:
    payload = {"type": msg_type, "content": content}
    if created_at is None:
        cur.execute(
            "INSERT INTO n8n_chat_histories (session_id, message) "
            "VALUES (%s, %s::jsonb) RETURNING id;",
            (session_id, json.dumps(payload, ensure_ascii=False)),
        )
    else:
        cur.execute(
            "INSERT INTO n8n_chat_histories (session_id, message, created_at) "
            "VALUES (%s, %s::jsonb, %s) RETURNING id;",
            (session_id, json.dumps(payload, ensure_ascii=False), created_at),
        )
    row = cur.fetchone()
    return row[0]


# === Main ===

def process_lead(
    cur: psycopg2.extensions.cursor,
    lead: dict,
    dry_run: bool,
) -> str:
    """
    Returns one of: 'processed', 'skipped_phone', 'skipped_exists', 'error'
    """
    fields = lead.get("fields", {})
    telefono_raw = fields.get("Telefono")
    session_id = normalize_phone(telefono_raw)
    if not session_id:
        return "skipped_phone"

    if not dry_run and session_already_exists(cur, session_id):
        return "skipped_exists"

    if dry_run:
        # En dry-run igual chequeamos para reportar correctamente
        if session_already_exists(cur, session_id):
            return "skipped_exists"

    # Construir mensajes
    system_text = build_system_message(lead)
    first_name = fields.get("Nombre") or ""

    # Timestamps inferidos para cada Touch
    base_at = parse_iso(fields.get("Outreach Form Meta enviado at"))
    if base_at is None:
        base_at = datetime.now(tz=timezone.utc) - timedelta(days=1)  # fallback

    toques = int(fields.get("Toques enviados") or 0)

    # System message timestamp = un segundo antes del Touch 1 (orden cronológico)
    system_at = base_at - timedelta(seconds=1)

    plan = [
        ("system", system_text, system_at),
        ("ai", render_template(TOUCH_1_TEXT, first_name), base_at),
    ]
    if toques >= 2:
        plan.append(("ai", render_template(TOUCH_2_TEXT, first_name), base_at + timedelta(hours=24)))
    if toques >= 3:
        plan.append(("ai", render_template(TOUCH_3_TEXT, first_name), base_at + timedelta(hours=72)))

    if dry_run:
        print(f"  [DRY] session={session_id} nombre={first_name!r} toques={toques}")
        for t, c, when in plan:
            preview = c[:60].replace("\n", " ")
            print(f"        - {t} @ {when.isoformat()}: {preview}...")
        return "processed"

    for t, c, when in plan:
        insert_message(cur, session_id, t, c, when)
    return "processed"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="Print intended inserts sin escribir")
    parser.add_argument("--limit", type=int, default=None, help="Max leads a procesar (debug)")
    parser.add_argument("--env", type=str, default=None, help="Ruta al .env (default: workspace root)")
    args = parser.parse_args()

    # Load .env
    workspace_root = Path(__file__).resolve().parents[2]
    env_path = Path(args.env) if args.env else workspace_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded .env: {env_path}")
    else:
        print(f"⚠ .env no encontrado en {env_path}. Esperando variables exportadas en shell.")

    airtable_key = os.environ.get("AIRTABLE_API_KEY")
    if not airtable_key:
        print("❌ Falta AIRTABLE_API_KEY en .env o env vars")
        sys.exit(2)

    if not os.environ.get("VTR_POSTGRES_URL") and not all(
        os.environ.get(k) for k in ["VTR_POSTGRES_HOST", "VTR_POSTGRES_DB", "VTR_POSTGRES_USER", "VTR_POSTGRES_PASSWORD"]
    ):
        print("❌ Falta VTR_POSTGRES_URL (o el conjunto VTR_POSTGRES_HOST/DB/USER/PASSWORD)")
        sys.exit(2)

    # Fetch leads
    print(f"Fetching Airtable leads (filter: {AIRTABLE_FILTER})...")
    leads = fetch_all_leads(airtable_key, max_records=args.limit)
    print(f"Total leads a evaluar: {len(leads)}")
    if not leads:
        print("Sin leads. Salida.")
        return

    # Connect Postgres
    print("Connecting Postgres...")
    conn = get_pg_connection()
    conn.autocommit = False
    cur = conn.cursor()

    counters = {"processed": 0, "skipped_phone": 0, "skipped_exists": 0, "error": 0}

    try:
        for i, lead in enumerate(leads, 1):
            try:
                result = process_lead(cur, lead, dry_run=args.dry_run)
                counters[result] += 1
            except Exception as e:
                counters["error"] += 1
                print(f"  ❌ Error procesando lead {i}: {e}")
            if i % 50 == 0:
                print(f"  Progreso: {i}/{len(leads)} ({counters})")

        if not args.dry_run:
            conn.commit()
            print("✓ Commit OK")
        else:
            conn.rollback()
            print("✓ Dry-run completo, rollback (sin cambios persistidos)")
    except Exception as e:
        conn.rollback()
        print(f"❌ Rollback por error global: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

    print()
    print("=" * 60)
    print(f"Resumen:")
    print(f"  Total leads evaluados:    {len(leads)}")
    print(f"  Procesados (inserts):     {counters['processed']}")
    print(f"  Skipped (sin teléfono):   {counters['skipped_phone']}")
    print(f"  Skipped (sesión existe):  {counters['skipped_exists']}")
    print(f"  Errores:                  {counters['error']}")
    print()
    if args.dry_run:
        print("Modo DRY-RUN — re-ejecutar sin --dry-run para persistir.")
    else:
        print("Verificación recomendada:")
        print("  SELECT session_id, COUNT(*), MIN(created_at), MAX(created_at)")
        print("  FROM n8n_chat_histories")
        print("  GROUP BY session_id ORDER BY MIN(created_at) DESC LIMIT 20;")


if __name__ == "__main__":
    main()
