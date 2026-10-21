#!/usr/bin/env python3
"""
update-sonrisas-nodes.py
Genera el código JS actualizado para los nodos Filtro, Categoria y Clase
de los flujos "Sonrisas | Reporte Facturación" y "Sonrisas | Correos Reportes
Facturación" a partir del Listado de Precios completo (xlsx).

CLASIFICACIÓN MES-AWARE (snapshot v2, junio 2026):
    Cada fila del Histórico se clasifica con los códigos vigentes EN SU MES
    de recepción del pago (campo `_fechaISO` derivado por 'Parsear y validar
    fecha'), no con los códigos del mes corriente. Resuelve el drift de
    códigos entre meses (caso PERIODONCIA Mayo = $0 en el reporte de junio).

Uso:
    python3 scripts/utilities/update-sonrisas-nodes.py <ruta_al_excel> [--mes YYYY-MM] [--no-snapshot] [--force-mes]

Ejemplos:
    # Mes implícito (mes calendario actual TZ Montevideo) — pide confirmación.
    python3 scripts/utilities/update-sonrisas-nodes.py ~/Downloads/listado-junio.xlsx

    # Mes explícito — recomendado, sin ambigüedad.
    python3 scripts/utilities/update-sonrisas-nodes.py ~/Downloads/listado-mayo.xlsx --mes 2026-05

Salida:
    3 bloques JS listos para pegar en n8n. Cada bloque embebe la TABLA_MES_AWARE
    de los últimos N meses (default 6) + lógica de lookup por mes con fallback
    hacia atrás → adelante → _error.

    - NODO: Filtro      → valida que el código exista en algún mes; emite _error
                          si no aparece en ninguno
    - NODO: Categoria   → lookup mes-aware con fallback
    - NODO: Clase       → idem; null = descarta fila (no-ortodoncia)

VALIDACIÓN PREVIA (obligatoria, antes de generar nada):
    1. Códigos ÚNICOS dentro del xlsx (mismo mes): ningún código puede aparecer
       en más de una fila con Rubros distintos. Aborta si hay conflicto interno.
    2. Rubro conocido: todo Rubro del xlsx debe estar en RUBRO_A_CATEGORIA.

CAMBIO ENTRE MESES (NO aborta):
    Si un código cambia de categoría/clase respecto al último mes registrado en
    el snapshot, se detecta y se reporta en el bloque "REVISIÓN REQUERIDA" al
    final del run, pero NO aborta — el cambio entre meses es legítimo (Cecilia
    reclasifica). El operador inspecciona y confirma antes de pegar los nodos.

SNAPSHOT MES-AWARE (clients/SNR_Sonrisas/_snapshots/codigos-historico.json):
    Estructura:
        codigos[X].meses[YYYY-MM] = {categoria, clase, computaImporte, computaCantidad}
    Mergea xlsx en meses[mes_arg]. NO sobrescribe meses anteriores. Pruning
    automático: entradas con YYYY-MM > VENTANA_MESES_DEFAULT meses atrás se
    eliminan; si todas las entradas de un código quedan prunneadas, se elimina
    el código entero. Cambios entre meses se registran en `changelog`.

    Si el snapshot está en v1 (flat), correr primero migrate-snapshot-mesaware.py.

    Flag --no-snapshot: bypass para regeneraciones puntuales sin tocar el snapshot
    (debug / experimentación). Genera el JS solo con datos del xlsx (sin ventana
    multi-mes, sin fallback útil — solo el mes que estás procesando).
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo
import pandas as pd


# ═══ CONSTANTES ══════════════════════════════════════════════════════════════

SNAPSHOT_VERSION = 2
VENTANA_MESES_DEFAULT = 6
TZ_OPERATIVA = "America/Montevideo"

RUBRO_A_CATEGORIA = {
    "ALINEADORES":                          "ALINEADORES",
    "CIRUGIA BUCAL Y MAXILOFACIAL":         "CIRUGIA",
    "ENDODONCIA O TRATAMIENTO DE CONDUCTO": "ENDODONCIA",
    "ODONTOLOGIA GENERAL":                  "GENERAL",
    "ORTODONCIA AJUSTES":                   "ORTODONCIA",
    "ORTODONCIA INSTALACION":               "ORTODONCIA",
    "ORTODONCIA RETIRO":                    "ORTODONCIA",
    "ORTOPEDIA":                            "ORTOPEDIA",
    "PERIODONCIA":                          "PERIODONCIA",
    "PRODUCTOS HIGIENE BUCAL":              "PRODUCTOS HIGIENE BUCAL",
    "RADIOLOGIA ORAL Y MAXILO FACIAL":      "RADIOLOGIA",
    "REHABILITACION CON PROTESIS":          "PROTESIS",
}

RUBRO_A_CLASE = {
    "ORTODONCIA AJUSTES":     "AJUSTE",
    "ORTODONCIA RETIRO":      "RETIRO",
    "ORTODONCIA INSTALACION": "COMBO",
}


# ═══ LECTURA DEL EXCEL ══════════════════════════════════════════════════════

def leer_excel(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    df["Código"] = df["Código"].astype(str).str.strip()
    df["Rubro"] = df["Rubro"].fillna("").astype(str).str.strip().str.upper()
    df["Computa para Planilla Importe"] = (
        df["Computa para Planilla Importe"].astype(str).str.strip().str.upper()
    )
    df["Computa para Planilla Cantidad"] = (
        df["Computa para Planilla Cantidad"].astype(str).str.strip().str.upper()
    )
    df = df[df["Código"].notna() & (df["Código"] != "") & (df["Código"] != "nan")]
    return df


# ═══ EXTRACCIÓN DE DATOS ════════════════════════════════════════════════════

def todos_los_codigos(df: pd.DataFrame) -> list[str]:
    return sorted(set(df["Código"].tolist()))


def codigos_no_computan_importe(df: pd.DataFrame) -> list[str]:
    mask = df["Computa para Planilla Importe"] != "SI"
    return sorted(set(df[mask]["Código"].tolist()))


def codigos_no_computan_cantidad(df: pd.DataFrame) -> list[str]:
    mask = df["Computa para Planilla Cantidad"] != "SI"
    return sorted(set(df[mask]["Código"].tolist()))


def validar_codigos_unicos(df: pd.DataFrame) -> list[tuple[str, list[str], int]]:
    filas: dict[str, list[str]] = {}
    for _, row in df.iterrows():
        filas.setdefault(row["Código"], []).append(row["Rubro"])
    dups = [
        (cod, sorted(set(rubros)), len(rubros))
        for cod, rubros in filas.items()
        if len(rubros) > 1
    ]
    return sorted(dups)


def validar_rubros_conocidos(df: pd.DataFrame) -> list[tuple[str, str]]:
    desconocidos, vistos = [], set()
    for _, row in df.iterrows():
        cod, rubro = row["Código"], row["Rubro"]
        if rubro not in RUBRO_A_CATEGORIA and cod not in vistos:
            desconocidos.append((cod, rubro))
            vistos.add(cod)
    return sorted(desconocidos)


def codigo_a_categoria(df: pd.DataFrame) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for _, row in df.iterrows():
        cod = row["Código"]
        if cod in mapping:
            continue
        mapping[cod] = RUBRO_A_CATEGORIA.get(row["Rubro"], "OTRO")
    return mapping


def codigos_clase(df: pd.DataFrame) -> dict[str, list[str]]:
    clases: dict[str, list[str]] = {"AJUSTE": [], "RETIRO": [], "COMBO": []}
    vistos: set[str] = set()
    sub = df[df["Rubro"].str.contains("ORTODONCIA", na=False)].copy()
    for _, row in sub.iterrows():
        clase = RUBRO_A_CLASE.get(row["Rubro"])
        cod = row["Código"]
        if clase and cod not in vistos:
            clases[clase].append(cod)
            vistos.add(cod)
    for k in clases:
        clases[k].sort()
    return clases


def _codigo_a_clase_lookup(clases_xlsx: dict[str, list[str]]) -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    for clase, codigos in clases_xlsx.items():
        for cod in codigos:
            out[cod] = clase
    return out


# ═══ ARG DE MES ══════════════════════════════════════════════════════════════

def _es_yyyymm_valido(s: str) -> bool:
    if not (len(s) == 7 and s[4] == "-"):
        return False
    try:
        y, m = int(s[:4]), int(s[5:7])
    except ValueError:
        return False
    return 1 <= m <= 12 and 2000 <= y <= 2100


def _yyyymm_actual() -> str:
    hoy = date.today() if ZoneInfo is None else _hoy_montevideo()
    return f"{hoy.year:04d}-{hoy.month:02d}"


def _hoy_montevideo() -> date:
    """Hoy en TZ America/Montevideo (negocio del cliente)."""
    import datetime as _dt
    now = _dt.datetime.now(ZoneInfo(TZ_OPERATIVA))
    return now.date()


def _ordinal_mes(yyyymm: str) -> int:
    """YYYY-MM → entero monotónico Y*12+M para comparar distancia entre meses."""
    y, m = int(yyyymm[:4]), int(yyyymm[5:7])
    return y * 12 + (m - 1)


def derivar_mes_arg(args: list[str]) -> tuple[str, bool, bool]:
    """Devuelve (mes_arg YYYY-MM, viene_de_default, force_mes_flag).

    Reglas:
      - Si --mes YYYY-MM presente → usar.
      - Si no → default = mes actual TZ Montevideo + bandera 'viene_de_default=True'.
      - Si el mes_arg está > 1 mes en el futuro o > VENTANA_MESES_DEFAULT
        en el pasado vs mes actual: aborta salvo --force-mes.
    """
    force = "--force-mes" in args
    if force:
        args.remove("--force-mes")

    mes_arg = None
    if "--mes" in args:
        idx = args.index("--mes")
        if idx + 1 >= len(args):
            print("❌ --mes requiere argumento YYYY-MM (ej. --mes 2026-06)", file=sys.stderr)
            sys.exit(2)
        mes_arg = args[idx + 1]
        del args[idx:idx + 2]
        if not _es_yyyymm_valido(mes_arg):
            print(f"❌ --mes inválido: {mes_arg!r}. Formato esperado: YYYY-MM", file=sys.stderr)
            sys.exit(2)

    viene_de_default = mes_arg is None
    if mes_arg is None:
        mes_arg = _yyyymm_actual()

    actual = _yyyymm_actual()
    delta = _ordinal_mes(mes_arg) - _ordinal_mes(actual)
    if not force:
        if delta > 1:
            print(
                f"❌ --mes {mes_arg} está {delta} meses en el futuro (actual: {actual}).\n"
                f"   Re-correr con --force-mes si es a propósito.",
                file=sys.stderr,
            )
            sys.exit(2)
        if delta < -VENTANA_MESES_DEFAULT:
            print(
                f"❌ --mes {mes_arg} está {-delta} meses en el pasado (>{VENTANA_MESES_DEFAULT}).\n"
                f"   Re-correr con --force-mes si es a propósito (probablemente backfill).",
                file=sys.stderr,
            )
            sys.exit(2)

    return mes_arg, viene_de_default, force


# ═══ SNAPSHOT MES-AWARE ═════════════════════════════════════════════════════

def snapshot_path_from_script() -> Path:
    script_path = Path(__file__).resolve()
    workspace_root = script_path.parent.parent.parent
    return workspace_root / "clients" / "SNR_Sonrisas" / "_snapshots" / "codigos-historico.json"


def cargar_snapshot(path: Path) -> dict:
    """Carga snapshot. Aborta si está en v1 (pide migrar)."""
    if not path.exists():
        print(
            f"⚠  Snapshot no encontrado en {path}. Arrancando vacío (primera corrida mes-aware).",
            file=sys.stderr,
        )
        return {
            "version": SNAPSHOT_VERSION,
            "last_updated": None,
            "ventana_meses": VENTANA_MESES_DEFAULT,
            "comment": (
                "Snapshot mes-aware de códigos. Cada código guarda sus clasificaciones "
                "por mes (YYYY-MM) para que el lookup de Filtro/Categoria/Clase use los "
                "códigos vigentes en el mes de recepción del pago. NO editar a mano."
            ),
            "codigos": {},
            "changelog": [],
        }
    with path.open("r", encoding="utf-8") as f:
        snap = json.load(f)
    version = snap.get("version", 1)
    if version < SNAPSHOT_VERSION:
        print(
            f"❌ Snapshot está en v{version}, se requiere v{SNAPSHOT_VERSION}.\n"
            f"   Corré primero: python3 scripts/utilities/migrate-snapshot-mesaware.py\n"
            f"   (one-shot que crea backup v1 y migra a v2 mes-aware).",
            file=sys.stderr,
        )
        sys.exit(2)
    if version > SNAPSHOT_VERSION:
        print(
            f"❌ Snapshot está en v{version}, este script entiende v{SNAPSHOT_VERSION}.\n"
            f"   Actualizá el script o el snapshot.",
            file=sys.stderr,
        )
        sys.exit(2)
    snap.setdefault("ventana_meses", VENTANA_MESES_DEFAULT)
    snap.setdefault("changelog", [])
    return snap


def detectar_cambios_clasificacion(
    mapping_xlsx: dict[str, str],
    clases_xlsx: dict[str, list[str]],
    no_importe_xlsx: list[str],
    no_cantidad_xlsx: list[str],
    snapshot: dict,
    mes_arg: str,
) -> list[dict]:
    """Compara la clasificación del xlsx (mes_arg) contra el último mes registrado
    estrictamente anterior a mes_arg para el mismo código.

    Devuelve lista de cambios:
        [{cod, campo, mes_referencia, antes, ahora}, ...]
    NO aborta. Cada cambio se imprime en 'REVISIÓN REQUERIDA' al final.
    """
    cod_clase_xlsx = _codigo_a_clase_lookup(clases_xlsx)
    no_imp_set = set(no_importe_xlsx)
    no_cant_set = set(no_cantidad_xlsx)
    cambios: list[dict] = []

    for cod, cat_xlsx in mapping_xlsx.items():
        info = snapshot.get("codigos", {}).get(cod)
        if not info:
            continue
        meses = info.get("meses", {})
        meses_previos = sorted([m for m in meses if m < mes_arg], reverse=True)
        if not meses_previos:
            continue
        mes_ref = meses_previos[0]
        entrada_ref = meses[mes_ref]

        clase_xlsx = cod_clase_xlsx.get(cod)
        comp_imp_xlsx = cod not in no_imp_set
        comp_cant_xlsx = cod not in no_cant_set

        comparaciones = [
            ("categoria", entrada_ref.get("categoria"), cat_xlsx),
            ("clase", entrada_ref.get("clase"), clase_xlsx),
            ("computaImporte", entrada_ref.get("computaImporte", True), comp_imp_xlsx),
            ("computaCantidad", entrada_ref.get("computaCantidad", True), comp_cant_xlsx),
        ]
        for campo, antes, ahora in comparaciones:
            if antes != ahora:
                cambios.append({
                    "cod": cod,
                    "campo": campo,
                    "mes_referencia": mes_ref,
                    "antes": antes,
                    "ahora": ahora,
                })
    return cambios


def materializar_tabla_mes_aware(
    mapping_xlsx: dict[str, str],
    clases_xlsx: dict[str, list[str]],
    no_importe_xlsx: list[str],
    no_cantidad_xlsx: list[str],
    snapshot: dict,
    mes_arg: str,
) -> dict:
    """Construye la tabla mes-aware combinando snapshot (todos los meses
    persistidos) + xlsx actual (mes_arg). El xlsx sobrescribe la entrada del
    mes_arg si ya existía.

    Output:
        {
          "tabla_por_mes": {"2026-05": {"OA001": {cat, clase, ci, cc}}, "2026-06": {...}},
          "todos_codigos_union": [...],
          "meses_ordenados": ["2026-05", "2026-06"],
        }
    """
    cod_clase_xlsx = _codigo_a_clase_lookup(clases_xlsx)
    no_imp_set = set(no_importe_xlsx)
    no_cant_set = set(no_cantidad_xlsx)

    tabla: dict[str, dict[str, dict]] = {}

    # 1) Cargar todo lo persistido en el snapshot
    for cod, info in snapshot.get("codigos", {}).items():
        for m, entrada in info.get("meses", {}).items():
            tabla.setdefault(m, {})[cod] = {
                "categoria": entrada.get("categoria"),
                "clase": entrada.get("clase"),
                "computaImporte": entrada.get("computaImporte", True),
                "computaCantidad": entrada.get("computaCantidad", True),
            }

    # 2) Sobrescribir mes_arg con los datos del xlsx (fuente de verdad para ese mes)
    if mes_arg not in tabla:
        tabla[mes_arg] = {}
    for cod, cat in mapping_xlsx.items():
        tabla[mes_arg][cod] = {
            "categoria": cat,
            "clase": cod_clase_xlsx.get(cod),
            "computaImporte": cod not in no_imp_set,
            "computaCantidad": cod not in no_cant_set,
        }

    todos = set()
    for m_dict in tabla.values():
        todos.update(m_dict.keys())

    return {
        "tabla_por_mes": tabla,
        "todos_codigos_union": sorted(todos),
        "meses_ordenados": sorted(tabla.keys()),
    }


def actualizar_snapshot(
    snapshot: dict,
    mapping_xlsx: dict[str, str],
    clases_xlsx: dict[str, list[str]],
    no_importe_xlsx: list[str],
    no_cantidad_xlsx: list[str],
    mes_arg: str,
    cambios: list[dict],
    fecha_corrida_iso: str,
) -> dict:
    """Mergea xlsx en `codigos[cod].meses[mes_arg]`. NO toca otros meses.
    Actualiza first_seen / last_seen_xlsx top-level. Append de cambios al changelog."""
    cod_clase_xlsx = _codigo_a_clase_lookup(clases_xlsx)
    no_imp_set = set(no_importe_xlsx)
    no_cant_set = set(no_cantidad_xlsx)

    nuevo = {
        "version": SNAPSHOT_VERSION,
        "last_updated": fecha_corrida_iso,
        "ventana_meses": snapshot.get("ventana_meses", VENTANA_MESES_DEFAULT),
        "comment": snapshot.get("comment", (
            "Snapshot mes-aware de códigos. Cada código guarda sus clasificaciones "
            "por mes (YYYY-MM) para que el lookup de Filtro/Categoria/Clase use los "
            "códigos vigentes en el mes de recepción del pago. NO editar a mano."
        )),
        "codigos": {cod: {
            "meses": dict(info.get("meses", {})),
            "first_seen": info.get("first_seen"),
            "last_seen_xlsx": info.get("last_seen_xlsx"),
        } for cod, info in snapshot.get("codigos", {}).items()},
        "changelog": list(snapshot.get("changelog", [])),
    }

    for cod, cat in mapping_xlsx.items():
        entrada_mes = {
            "categoria": cat,
            "clase": cod_clase_xlsx.get(cod),
            "computaImporte": cod not in no_imp_set,
            "computaCantidad": cod not in no_cant_set,
        }
        if cod in nuevo["codigos"]:
            nuevo["codigos"][cod]["meses"][mes_arg] = entrada_mes
            nuevo["codigos"][cod]["last_seen_xlsx"] = fecha_corrida_iso
            if not nuevo["codigos"][cod].get("first_seen"):
                nuevo["codigos"][cod]["first_seen"] = fecha_corrida_iso
        else:
            nuevo["codigos"][cod] = {
                "meses": {mes_arg: entrada_mes},
                "first_seen": fecha_corrida_iso,
                "last_seen_xlsx": fecha_corrida_iso,
            }

    for c in cambios:
        nuevo["changelog"].append({
            "fecha_corrida": fecha_corrida_iso,
            "mes_arg": mes_arg,
            **c,
        })

    return nuevo


def cutoff_pruning_yyyymm(fecha_hoy: date, meses: int) -> str:
    """YYYY-MM cabeza de ventana. fecha_hoy=2026-06-06, meses=6 → '2026-01'."""
    y, m = fecha_hoy.year, fecha_hoy.month - (meses - 1)
    while m <= 0:
        m += 12
        y -= 1
    return f"{y:04d}-{m:02d}"


def prunear_snapshot(
    snapshot: dict,
    fecha_hoy: date,
    meses: int = VENTANA_MESES_DEFAULT,
) -> tuple[dict, list[tuple[str, str]], list[str]]:
    """Borra entradas `meses[YYYY-MM]` con YYYY-MM < cutoff.
    Si todas las entradas de un código quedaron prunneadas, borra el código entero.

    Devuelve (snapshot, entradas_borradas[(cod, mes)], codigos_borrados[cod]).
    """
    cutoff = cutoff_pruning_yyyymm(fecha_hoy, meses)
    nuevo = {
        "version": snapshot.get("version", SNAPSHOT_VERSION),
        "last_updated": snapshot.get("last_updated"),
        "ventana_meses": snapshot.get("ventana_meses", meses),
        "comment": snapshot.get("comment", ""),
        "codigos": {},
        "changelog": snapshot.get("changelog", []),
    }
    entradas_borradas: list[tuple[str, str]] = []
    codigos_borrados: list[str] = []

    for cod, info in snapshot.get("codigos", {}).items():
        meses_vivos: dict[str, dict] = {}
        for m, entrada in info.get("meses", {}).items():
            if m < cutoff:
                entradas_borradas.append((cod, m))
            else:
                meses_vivos[m] = entrada
        if not meses_vivos:
            codigos_borrados.append(cod)
            continue
        nuevo["codigos"][cod] = {
            "meses": meses_vivos,
            "first_seen": info.get("first_seen"),
            "last_seen_xlsx": info.get("last_seen_xlsx"),
        }

    return nuevo, sorted(entradas_borradas), sorted(codigos_borrados)


def guardar_snapshot(snapshot: dict, path: Path) -> None:
    """Escribe ordenado por código + meses ordenados. Diffs git estables."""
    path.parent.mkdir(parents=True, exist_ok=True)
    codigos_ordenados: dict[str, dict] = {}
    for cod in sorted(snapshot.get("codigos", {}).keys()):
        info = snapshot["codigos"][cod]
        codigos_ordenados[cod] = {
            "meses": {m: info["meses"][m] for m in sorted(info.get("meses", {}).keys())},
            "first_seen": info.get("first_seen"),
            "last_seen_xlsx": info.get("last_seen_xlsx"),
        }
    snapshot_ordenado = {
        "version": snapshot["version"],
        "last_updated": snapshot["last_updated"],
        "ventana_meses": snapshot.get("ventana_meses", VENTANA_MESES_DEFAULT),
        "comment": snapshot["comment"],
        "codigos": codigos_ordenados,
        "changelog": snapshot.get("changelog", []),
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(snapshot_ordenado, f, indent=2, ensure_ascii=False)
        f.write("\n")


# ═══ FORMATEO JS ════════════════════════════════════════════════════════════

def _js_str(value: object) -> str:
    """Serializa un valor Python a literal JS."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def formato_tabla_mes_aware_js(tabla_por_mes: dict[str, dict[str, dict]]) -> str:
    """Formatea TABLA_MES_AWARE como objeto JS legible.

    Output (1 código por línea, agrupado por mes):
        "2026-05": {
          "OA001": {categoria:"ORTODONCIA",clase:"AJUSTE",computaImporte:true,computaCantidad:true},
          ...
        },
    """
    lineas = ["{"]
    for mes in sorted(tabla_por_mes.keys()):
        codigos = tabla_por_mes[mes]
        lineas.append(f'  "{mes}": {{')
        for cod in sorted(codigos.keys()):
            e = codigos[cod]
            cat = _js_str(e.get("categoria"))
            cls = _js_str(e.get("clase"))
            ci = _js_str(e.get("computaImporte", True))
            cc = _js_str(e.get("computaCantidad", True))
            lineas.append(
                f'    "{cod}": {{categoria:{cat},clase:{cls},computaImporte:{ci},computaCantidad:{cc}}},'
            )
        lineas.append("  },")
    lineas.append("}")
    return "\n".join(lineas)


def formato_meses_ordenados_js(meses_ordenados: list[str]) -> str:
    return "[" + ", ".join(f'"{m}"' for m in meses_ordenados) + "]"


# ═══ HELPER COMÚN (embebido en cada nodo) ═══════════════════════════════════

LOOKUP_HELPER_JS = """\
// Códigos AMBIGUOS — el mismo código sirve para 2 prestaciones de Rubros distintos
// (Cecilia los usa para Periodoncia y Protesis indistintamente). Se resuelven
// SIEMPRE por el "Nombre categoría" original de la fila, NO por lookup mes-aware.
const CODIGOS_AMBIGUOS = new Set([
  "P0000","P1000","P1001","P1002","P1003","P1004","P2000","P2001","P2002"
]);

function resolverAmbiguo(nombreCat) {
  const n = String(nombreCat || "").normalize("NFD").replace(/[\\u0300-\\u036f]/g, "").toUpperCase().trim();
  if (n.includes("PERIODONCIA")) return "PERIODONCIA";
  if (n.includes("REHABILITACION CON PROTESIS")) return "PROTESIS";
  return "OTRO";
}

// Helper común: lookup por mes_key del código, con fallback hacia atrás → adelante.
// Devuelve { entrada, fallback } — fallback null si match directo,
// "atras:YYYY-MM" si vino de mes anterior, "adelante:YYYY-MM" si vino de mes posterior.
function lookupMesAware(codigo, mes_key) {
  let entrada = (TABLA_MES_AWARE[mes_key] || {})[codigo];
  if (entrada) return { entrada, fallback: null };
  // Hacia atrás: mes más reciente <= mes_key
  for (let i = MESES_ORDENADOS.length - 1; i >= 0; i--) {
    const m = MESES_ORDENADOS[i];
    if (m > mes_key) continue;
    if ((TABLA_MES_AWARE[m] || {})[codigo]) {
      return { entrada: TABLA_MES_AWARE[m][codigo], fallback: "atras:" + m };
    }
  }
  // Hacia adelante: mes más antiguo > mes_key (último recurso)
  for (let i = 0; i < MESES_ORDENADOS.length; i++) {
    const m = MESES_ORDENADOS[i];
    if (m <= mes_key) continue;
    if ((TABLA_MES_AWARE[m] || {})[codigo]) {
      return { entrada: TABLA_MES_AWARE[m][codigo], fallback: "adelante:" + m };
    }
  }
  return { entrada: null, fallback: null };
}

// Deriva YYYY-MM del row. Prioriza _fechaISO (poblado por 'Parsear y validar fecha');
// si no, intenta Fecha_de_recepcion_del_pago (puede venir como ISO o como objeto Luxon).
function derivarMesKey(row) {
  const candidatos = [
    row._fechaISO,
    row.Fecha_de_recepcion_del_pago,
    row["Fecha de recepción del pago"],
  ];
  for (const c of candidatos) {
    if (!c) continue;
    if (typeof c === "string" && c.length >= 7 && c[4] === "-") return c.substring(0, 7);
    if (c && typeof c === "object" && typeof c.toISO === "function") {
      const iso = c.toISO();
      if (iso && iso.length >= 7) return iso.substring(0, 7);
    }
  }
  return null;
}"""


# ═══ GENERADORES JS (mes-aware) ═════════════════════════════════════════════

def generar_filtro_mesaware(
    tabla_por_mes: dict[str, dict[str, dict]],
    meses_ordenados: list[str],
) -> str:
    tabla_js = formato_tabla_mes_aware_js(tabla_por_mes)
    meses_js = formato_meses_ordenados_js(meses_ordenados)

    return f"""\
// FILTRO MES-AWARE
// Valida que cada código exista en al menos un mes de TABLA_MES_AWARE
// (con fallback hacia atrás → adelante). Emite _error:true para el branch
// 'Códigos inválidos?' si hay códigos desconocidos o fechas inválidas.
// Anota _warning_fallback en la fila si tuvo que caer en fallback.

const TABLA_MES_AWARE = {tabla_js};

const MESES_ORDENADOS = {meses_js};

{LOOKUP_HELPER_JS}

// Detección de errores y warnings
const desconocidos = new Set();
const fechasInvalidas = [];

for (const item of items) {{
  const row = item.json || {{}};
  const cod = String(row["Código Prestación"] || "").trim().toUpperCase();
  const pg = Number(row["Pagado Prestación"]);
  const tieneContenido = cod !== "" || (Number.isFinite(pg) && pg !== 0);

  if (row._fechaValida === false && tieneContenido) {{
    const fechaCruda = row["Fecha_de_recepcion_del_pago"] ?? row["Fecha de recepción del pago"];
    const idFila = row.id ?? row.row_number;
    fechasInvalidas.push((idFila != null ? ("fila " + idFila + " ") : "") + "cod=" + cod + " fecha='" + String(fechaCruda ?? "") + "'");
    continue;
  }}

  if (cod === "") continue;

  // Ambiguos siempre son válidos; no requieren lookup mes-aware.
  if (CODIGOS_AMBIGUOS.has(cod)) continue;

  const mes_key = derivarMesKey(row);
  if (mes_key === null && tieneContenido) {{
    const idFila = row.id ?? row.row_number;
    fechasInvalidas.push((idFila != null ? ("fila " + idFila + " ") : "") + "cod=" + cod + " (sin fecha)");
    continue;
  }}

  const {{ entrada }} = lookupMesAware(cod, mes_key);
  if (!entrada) desconocidos.add(cod);
}}

if (desconocidos.size > 0 || fechasInvalidas.length > 0) {{
  const lista = [...desconocidos].sort().join(", ");
  return [{{ json: {{ _error: true, codigos: lista, fechas_invalidas: fechasInvalidas }} }}];
}}

// Todos válidos → agregar flags computaImporte / computaCantidad mes-aware
return items.map(item => {{
  const row = item.json || {{}};
  const cod = String(row["Código Prestación"] || "").trim().toUpperCase();
  const mes_key = derivarMesKey(row);
  // Ambiguos: flags conservadores (computan importe y cantidad)
  if (CODIGOS_AMBIGUOS.has(cod)) {{
    return {{ json: {{ ...row, _error: false, computaImporte: true, computaCantidad: true, _warning_fallback: null }} }};
  }}
  const {{ entrada, fallback }} = (cod && mes_key) ? lookupMesAware(cod, mes_key) : {{ entrada: null, fallback: null }};
  return {{
    json: {{
      ...row,
      _error: false,
      computaImporte: entrada ? !!entrada.computaImporte : true,
      computaCantidad: entrada ? !!entrada.computaCantidad : true,
      _warning_fallback: fallback,
    }},
  }};
}});\
"""


def generar_categoria_mesaware(
    tabla_por_mes: dict[str, dict[str, dict]],
    meses_ordenados: list[str],
) -> str:
    tabla_js = formato_tabla_mes_aware_js(tabla_por_mes)
    meses_js = formato_meses_ordenados_js(meses_ordenados)

    return f"""\
// CATEGORIA MES-AWARE
// Asigna Categoria a cada item buscando la clasificación vigente en el mes
// de recepción del pago. Fallback hacia atrás → adelante si el código no
// existía exactamente en su mes. El nodo Filtro upstream ya descartó las
// filas con código desconocido o fecha inválida (emitió _error).

const TABLA_MES_AWARE = {tabla_js};

const MESES_ORDENADOS = {meses_js};

{LOOKUP_HELPER_JS}

return items.map(item => {{
  const row = item.json || {{}};
  const cod = String(row["Código Prestación"] || "").trim().toUpperCase();
  // Ambiguos: resolver SIEMPRE por el "Nombre categoría" original de la fila.
  // El field se llama "Categoria" porque el nodo upstream 'Filtro de campos'
  // mapea Nombre_categoria → Categoria. Ese es el valor original del row.
  if (CODIGOS_AMBIGUOS.has(cod)) {{
    return {{ json: {{ ...row, Categoria: resolverAmbiguo(row.Categoria || ""), _warning_fallback: null }} }};
  }}
  const mes_key = derivarMesKey(row);
  if (!cod || !mes_key) {{
    return {{ json: {{ ...row, Categoria: "OTRO" }} }};
  }}
  const {{ entrada, fallback }} = lookupMesAware(cod, mes_key);
  const categoria = entrada ? entrada.categoria : "OTRO";
  return {{
    json: {{
      ...row,
      Categoria: categoria || "OTRO",
      _warning_fallback: fallback,
    }},
  }};
}});\
"""


def generar_clase_mesaware(
    tabla_por_mes: dict[str, dict[str, dict]],
    meses_ordenados: list[str],
) -> str:
    tabla_js = formato_tabla_mes_aware_js(tabla_por_mes)
    meses_js = formato_meses_ordenados_js(meses_ordenados)

    return f"""\
// CLASE MES-AWARE
// Subclasifica SOLO ortodoncia (AJUSTE / RETIRO / COMBO) usando la entrada del
// mes de recepción del pago. Filas no-ortodoncia se DESCARTAN del bloque (se
// contabilizan en el bloque Categoría aguas paralelas).
// cantidadComputable deriva de computaCantidad mes-aware.

const TABLA_MES_AWARE = {tabla_js};

const MESES_ORDENADOS = {meses_js};

{LOOKUP_HELPER_JS}

const out = [];
for (const item of items) {{
  const row = item.json || {{}};
  const cod = String(row["Código Prestación"] || "").trim().toUpperCase();
  // Ambiguos NUNCA son ortodoncia (son PERIODONCIA o PROTESIS) → descartar.
  if (CODIGOS_AMBIGUOS.has(cod)) continue;
  const mes_key = derivarMesKey(row);
  if (!cod || !mes_key) continue;
  const {{ entrada, fallback }} = lookupMesAware(cod, mes_key);
  if (!entrada || !entrada.clase) continue;  // no-ortodoncia → fuera del bloque
  out.push({{
    json: {{
      ...row,
      Clase: entrada.clase,
      cantidadComputable: entrada.computaCantidad ? 1 : 0,
      _warning_fallback: fallback,
    }},
  }});
}}
return out;\
"""


# ═══ RESUMEN DE CAMBIOS ═════════════════════════════════════════════════════

def imprimir_resumen_cambios(cambios: list[dict], mes_arg: str) -> None:
    if not cambios:
        return
    sep = "═" * 70
    print(f"\n{sep}", file=sys.stderr)
    print(f"⚠  REVISIÓN REQUERIDA — {len(cambios)} cambio(s) de clasificación detectado(s)", file=sys.stderr)
    print(f"   ({mes_arg} vs último mes registrado anterior)", file=sys.stderr)
    print(sep, file=sys.stderr)
    print("   Verificar con Cecilia si los cambios son intencionales antes de pegar", file=sys.stderr)
    print("   los nodos en n8n. Cada cambio queda registrado en snapshot.changelog.", file=sys.stderr)
    print("", file=sys.stderr)
    por_codigo: dict[str, list[dict]] = {}
    for c in cambios:
        por_codigo.setdefault(c["cod"], []).append(c)
    for cod in sorted(por_codigo.keys()):
        cs = por_codigo[cod]
        for c in cs:
            mes_ref = c["mes_referencia"]
            campo = c["campo"]
            antes = c["antes"]
            ahora = c["ahora"]
            print(f"   {cod:9s} | {campo:16s} | {mes_ref} → {mes_arg} : {antes!r} → {ahora!r}", file=sys.stderr)
    print(sep, file=sys.stderr)


# ═══ MAIN ════════════════════════════════════════════════════════════════════

def main():
    args = sys.argv[1:]
    no_snapshot = "--no-snapshot" in args
    if no_snapshot:
        args.remove("--no-snapshot")

    mes_arg, viene_de_default, force_mes = derivar_mes_arg(args)

    if not args:
        print(__doc__)
        sys.exit(1)
    path = args[0]
    df = leer_excel(path)

    if viene_de_default:
        print(
            f"\n⚠  --mes NO especificado. Usando default = mes actual: {mes_arg}\n"
            f"   Si el xlsx corresponde a OTRO mes, abortá con Ctrl-C y re-correr con --mes YYYY-MM.\n",
            file=sys.stderr,
        )

    # ── VALIDACIÓN PREVIA (obligatoria) ─────────────────────────────────────────
    sep = "─" * 70
    duplicados = validar_codigos_unicos(df)
    rubros_desc = validar_rubros_conocidos(df)
    if duplicados or rubros_desc:
        print(f"\n{sep}", file=sys.stderr)
        print("ABORTADO — el Listado de Precios no pasa la validación. NO se generó ningún nodo.", file=sys.stderr)
        print(sep, file=sys.stderr)
        if duplicados:
            print(f"\n❌ {len(duplicados)} código(s) DUPLICADO(s). Los códigos deben ser ÚNICOS.", file=sys.stderr)
            print("   Pedir a Cecilia que deje una sola fila (y un solo Rubro) por código:\n", file=sys.stderr)
            print(f"   {'CÓDIGO':9s} {'#FILAS':>6s}  RUBROS", file=sys.stderr)
            for cod, rubros, n in duplicados:
                tag = "CONFLICTO" if len(rubros) > 1 else "fila redundante"
                print(f"   {cod:9s} {n:6d}  [{tag}] {' | '.join(rubros)}", file=sys.stderr)
        if rubros_desc:
            print(f"\n❌ {len(rubros_desc)} código(s) con Rubro DESCONOCIDO (no mapea a categoría):", file=sys.stderr)
            for cod, rubro in rubros_desc:
                print(f"   {cod:9s}  Rubro='{rubro}'", file=sys.stderr)
            print("   Agregar el Rubro a RUBRO_A_CATEGORIA o pedir a Cecilia que lo corrija.", file=sys.stderr)
        print(f"\n{sep}", file=sys.stderr)
        return 1

    # Extraer datos del xlsx
    todos_xlsx = todos_los_codigos(df)
    no_importe_xlsx = codigos_no_computan_importe(df)
    no_cantidad_xlsx = codigos_no_computan_cantidad(df)
    mapping_xlsx = codigo_a_categoria(df)
    clases_xlsx = codigos_clase(df)

    # ── SNAPSHOT MES-AWARE ──────────────────────────────────────────────────────
    snapshot_stats: dict | None = None

    if no_snapshot:
        print("⚠  Modo --no-snapshot: tabla mes-aware solo con datos del xlsx actual.", file=sys.stderr)
        tabla_por_mes = {mes_arg: {}}
        for cod, cat in mapping_xlsx.items():
            cls = None
            for c, codigos in clases_xlsx.items():
                if cod in codigos:
                    cls = c
                    break
            tabla_por_mes[mes_arg][cod] = {
                "categoria": cat,
                "clase": cls,
                "computaImporte": cod not in set(no_importe_xlsx),
                "computaCantidad": cod not in set(no_cantidad_xlsx),
            }
        materializado = {
            "tabla_por_mes": tabla_por_mes,
            "todos_codigos_union": todos_xlsx,
            "meses_ordenados": [mes_arg],
        }
        cambios: list[dict] = []
    else:
        snapshot_path = snapshot_path_from_script()
        snapshot = cargar_snapshot(snapshot_path)

        cambios = detectar_cambios_clasificacion(
            mapping_xlsx, clases_xlsx, no_importe_xlsx, no_cantidad_xlsx, snapshot, mes_arg,
        )

        materializado = materializar_tabla_mes_aware(
            mapping_xlsx, clases_xlsx, no_importe_xlsx, no_cantidad_xlsx, snapshot, mes_arg,
        )

        fecha_corrida_iso = _hoy_montevideo().isoformat()
        snapshot_actualizado = actualizar_snapshot(
            snapshot, mapping_xlsx, clases_xlsx, no_importe_xlsx, no_cantidad_xlsx,
            mes_arg, cambios, fecha_corrida_iso,
        )
        snapshot_prunneado, entradas_borradas, codigos_borrados = prunear_snapshot(
            snapshot_actualizado, _hoy_montevideo(), snapshot.get("ventana_meses", VENTANA_MESES_DEFAULT),
        )
        guardar_snapshot(snapshot_prunneado, snapshot_path)

        codigos_nuevos_globales = sorted(set(todos_xlsx) - set(snapshot.get("codigos", {}).keys()))
        codigos_nuevos_en_mes = sorted([
            cod for cod in todos_xlsx
            if mes_arg not in snapshot.get("codigos", {}).get(cod, {}).get("meses", {})
        ])

        snapshot_stats = {
            "path": snapshot_path,
            "mes_arg": mes_arg,
            "del_xlsx": len(todos_xlsx),
            "nuevos_globales": codigos_nuevos_globales,
            "nuevos_en_mes": codigos_nuevos_en_mes,
            "entradas_prunneadas": entradas_borradas,
            "codigos_borrados": codigos_borrados,
            "cutoff_yyyymm": cutoff_pruning_yyyymm(
                _hoy_montevideo(),
                snapshot.get("ventana_meses", VENTANA_MESES_DEFAULT),
            ),
            "meses_en_snapshot": sorted({
                m for info in snapshot_prunneado["codigos"].values()
                for m in info.get("meses", {})
            }),
        }

    # Generar JS
    tabla_por_mes = materializado["tabla_por_mes"]
    meses_ordenados = materializado["meses_ordenados"]

    js_filtro = generar_filtro_mesaware(tabla_por_mes, meses_ordenados)
    js_categoria = generar_categoria_mesaware(tabla_por_mes, meses_ordenados)
    js_clase = generar_clase_mesaware(tabla_por_mes, meses_ordenados)

    # Imprimir
    print(f"\n{sep}")
    print("NODO: Filtro  (pegar en Filtro1 del Reporte + Filtro y Filtro3 del Correo)")
    print(sep)
    print(js_filtro)

    print(f"\n{sep}")
    print("NODO: Categoria  (pegar en Categoria del Reporte + Categoria y Categoria1 del Correo)")
    print(sep)
    print(js_categoria)

    print(f"\n{sep}")
    print("NODO: Clase  (pegar en Clase1 del Reporte + Clase y Clase1 del Correo)")
    print(sep)
    print(js_clase)

    # Resumen
    print(f"\n{sep}")
    print(f"RESUMEN — mes_arg: {mes_arg}")
    print(sep)
    print(f"  Códigos del xlsx (mes_arg):   {len(todos_xlsx)} (todos únicos ✓)")
    print(f"  No computan importe (xlsx):   {len(no_importe_xlsx)}")
    print(f"  No computan cantidad (xlsx):  {len(no_cantidad_xlsx)}")
    print(f"  Categorías (xlsx):            {len(mapping_xlsx)} (100% por código)")
    print(f"  Clase AJUSTE (xlsx):          {len(clases_xlsx.get('AJUSTE', []))} códigos")
    print(f"  Clase RETIRO (xlsx):          {len(clases_xlsx.get('RETIRO', []))} códigos")
    print(f"  Clase COMBO (xlsx):           {len(clases_xlsx.get('COMBO', []))} códigos")
    cats = Counter(mapping_xlsx.values())
    print(f"  Categorías (xlsx):")
    for cat in sorted(cats.keys()):
        print(f"    {cat:30s} {cats[cat]:3d} códigos")

    if snapshot_stats is not None:
        print(sep)
        print(f"  SNAPSHOT MES-AWARE (cutoff: {snapshot_stats['cutoff_yyyymm']})")
        print(f"    Path:                       {snapshot_stats['path']}")
        print(f"    Meses persistidos:          {snapshot_stats['meses_en_snapshot']}")
        print(f"    Códigos del xlsx actual:    {snapshot_stats['del_xlsx']}")
        print(f"    Nuevos GLOBAL (vs snap):    {len(snapshot_stats['nuevos_globales'])}")
        if snapshot_stats["nuevos_globales"]:
            head = ", ".join(snapshot_stats["nuevos_globales"][:8])
            suffix = " …" if len(snapshot_stats["nuevos_globales"]) > 8 else ""
            print(f"      {head}{suffix}")
        print(f"    Nuevos en {mes_arg} (vs snap.meses): {len(snapshot_stats['nuevos_en_mes'])}")
        print(f"    Entradas prunneadas:        {len(snapshot_stats['entradas_prunneadas'])}")
        print(f"    Códigos borrados (sin meses vivos): {len(snapshot_stats['codigos_borrados'])}")
        if snapshot_stats["codigos_borrados"]:
            head = ", ".join(snapshot_stats["codigos_borrados"][:8])
            suffix = " …" if len(snapshot_stats["codigos_borrados"]) > 8 else ""
            print(f"      {head}{suffix}")
    else:
        print(sep)
        print("  SNAPSHOT: deshabilitado (--no-snapshot)")
    print(sep)

    # Cambios de clasificación detectados (no aborta — operator review)
    imprimir_resumen_cambios(cambios, mes_arg)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
