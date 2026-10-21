#!/usr/bin/env python3
"""
HPF · L1 — Registro de puntos de migración.

Enumera TODOS los nodos significativos de los 8 workflows congelados y los asigna a
grupos. El gate de completitud es aritmético, no de criterio:

    Σ nodos_asignados  ==  nodos_significativos_totales

Si no cierra, hay nodos sin dueño y el registro no está terminado. Ese es el
"stop condition" del plan hecho verificable.

Uso:
    python3 scripts/testing/hpf-registro.py --cobertura   # gate + huérfanos
    python3 scripts/testing/hpf-registro.py --generar     # escribe puntos.jsonl + PUNTOS.md
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BASE = REPO / "clients/HPF_HappyFlops/03_workflows/base-prod-2026-08-06"
OUT = REPO / "clients/HPF_HappyFlops/00_migracion_ghl/06_registro"

WF = {
    "main-happy-flops": "main",
    "seg-rebeca": "rebeca",
    "seg-imagen": "imagen",
    "seg-cotizacion": "cotizacion",
    "seg-7pasos": "7pasos",
    "atencion-personalizada": "atencion",
    "tool-calculadora": "calculadora",
    "kommo-salesbot-text-capture-runner": "salesbot-runner",
}

# ── Reglas de asignación. Se evalúan EN ORDEN; gana la primera que matchea.
# (grupo, título, ámbito, patrón sobre el nombre del nodo)
#   ámbito: "main" | "sub" | "*"
REGLAS = [
    # ── ING · ingreso
    ("PM-ING-01", "Webhook, triggers y gate de entrada", "main",
     r"^(New_Message|If25|la agencia|When Executed by Another Workflow)$"),
    ("PM-ING-02", "Lectura de contacto y teléfono", "main",
     r"^(Get_Contact|Clear_Contact_Data)$"),
    ("PM-ING-03", "Normalización del payload", "main", r"^All_Data$"),
    ("PM-ING-04", "Ruteo texto / voz / imagen", "main", r"^checkType1?$"),
    ("PM-ING-05", "Debounce de texto (50 s)", "main",
     r"^(Get_Text|Guardar|Wait_35|Get_Messages|Ultimo\?|Borrar almacenamiento|"
     r"Date & Time|Message & Date)$"),
    ("PM-ING-06", "Debounce de imagen (15 s)", "main",
     r"^(Guardar1|Wait_15s|Get_Messages1|Ultimo\?1|Borrar almacenamiento1|"
     r"Date & Time1|Message & Date1)$"),
    ("PM-ING-07", "Audio: descarga + transcripción", "main",
     r"^(Get_Audio|transcribe voice)$"),
    ("PM-ING-08", "Imagen: clasificador de producto", "main",
     r"^(Analyze image1|Es producto\?)$"),
    ("PM-ING-09", "Imagen/PDF: detector de comprobante", "main",
     r"^(Analyze image[23]|Es PDF\?1?|Es Pago\?1?)$"),

    # ── STA · gates de estado
    ("PM-STA-01", "Filtro de pipeline IA / país", "main", r"^(No es IA|No es EEUU)$"),
    ("PM-STA-02", "Lectura de entidad para gatear", "main", r"^Get_Entity\d*$"),
    ("PM-STA-03", "Gate En Producción / Perdidos", "main",
     r"^(En prod\?1?|Si está en perdidos|Code in JavaScript)$"),
    ("PM-STA-04", "Gates de etapa (whitelists y bloqueos)", "main",
     r"^If(5|7|8|9|10|11|12|18|19|20|21|22|23)$"),

    # ── OUT · salida  (arquitectura de salesbots: PATCH cf 1099420 + salesbot/run)
    ("PM-OUT-01", "Escritura del texto en el campo 1099420", "main", r"^actualizar\d*$"),
    ("PM-OUT-02", "Disparo de salesbot de texto", "main", r"^Envio Mensaje\d*$"),
    ("PM-OUT-03", "Disparo de salesbot de imagen", "main", r"^Envío Imagen\d*$"),
    ("PM-OUT-04", "Secuencia de saludo en 3 partes", "main", r"^(Saludo PTE \d|Wait[67])$"),
    ("PM-OUT-05", "Split en 3 partes + limpieza + cadencia", "main",
     r"^(Message a model1|Formatear mensaje1?|Character_Cleaner1?|File_Not_Required1?|"
     r"Wait[145]?|If|If2|If13|If14)$"),
    ("PM-OUT-06", "Parsers de CURL vestigiales", "main", r"^Code[59]$"),

    # ── CAT · catálogo (Airtable → custom object GHL)
    ("PM-CAT-01", "Imagen principal por evento", "main", r"^(Formula|Search_Main_Image)$"),
    ("PM-CAT-02", "Fichas de producto por evento", "main",
     r"^(Search_Products|Return_Formula|Loop Over Items|Wait3|Data|Aggregate)$"),
    ("PM-CAT-03", "Foto vacaciones (fuera de horario)", "main", r"^Search_Main_Image1$"),
    ("PM-CAT-04", "Canonicalización de nombres de producto", "main",
     r"^(Message a model|Is_Products_Empty|backup)$"),

    # ── AGT · agentes
    ("PM-AGT-01", "Router de steps", "main", r"^(AI Agent|Switch1)$"),
    ("PM-AGT-02", "Agente Starter (saludo)", "main", r"^AI Agent Starter1?$"),
    ("PM-AGT-03", "Agente Main Image (clasifica evento)", "main", r"^AI Agent Main Image$"),
    ("PM-AGT-04", "Agente Products (elige fichas)", "main", r"^AI Agent Products$"),
    ("PM-AGT-05", "Agente Recolector (vendedora, texto)", "main", r"^AI Agent Recolector$"),
    ("PM-AGT-06", "Agente Recolector1 (vendedora, imagen)", "main", r"^AI Agent Recolector1$"),
    ("PM-AGT-07", "Agentes huérfanos, sin conexiones (NO migrar)", "main",
     r"^(AI Agent Recolector[23]|backup1)$"),
    ("PM-AGT-08", "Gate de intención de cotizar", "main",
     r"^(Necesita Respuesta Especial|If1)$"),
    ("PM-AGT-09", "Modelos y parsers de los agentes", "main",
     r"^(OpenAI Chat Model\d*|Structured Output Parser\d*|Auto-fixing Output Parser\d*)$"),

    # ── MEM · memoria
    ("PM-MEM-01", "Clave de sesión <teléfono>2131", "main", r"^Memory_ID\d*$"),
    ("PM-MEM-02", "Memoria Postgres de los agentes", "main", r"^Postgres Chat Memory\d*$"),
    ("PM-MEM-03", "Consultas SQL crudas de historial", "main",
     r"^(GET_LAST_INTERACTION|GET_PREVIOUS_INTERACTION1?|SAVE_FIRST_MESSAGE|"
     r"Exist_Interaction\?1?)$"),

    # ── TOOL
    ("PM-TOOL-01", "Tool CALCULADORA (envío, empaque, mínimos)", "main",
     r"^CALCULADORA1?$"),
    ("PM-TOOL-02", "Tool ATENCION_PERSONALIZADA", "main",
     r"^ATENCION_PERSONALIZADA6?$"),
    ("PM-TOOL-03", "Tool Think", "main", r"^Think1?$"),

    # ── CRM · escrituras de etapa
    ("PM-CRM-01", "Mover a atención personalizada", "main",
     r"^ATENCION_PERSONALIZADA[1245]$"),
    ("PM-CRM-02", "Confirmar pago / pago liquidación", "main",
     r"^(Confirmar [Pp]ago1?|PAGO_LIQUIDACION)$"),
    ("PM-CRM-03", "Metadatos de ejecución", "main",
     r"^(Detect_Evento|Execution Data\d*)$"),

    # ── OPS
    ("PM-OPS-01", "Alertas operativas a Telegram", "main",
     r"^Usr\. Envia Imágenes/Documentos\d*$"),

    # ── REE · invocación del reenganche desde el main
    ("PM-REE-00", "Invocación de los seguimientos", "main",
     r"^(Execute Workflow\d*|Call '.*'|Wait2)$"),
    ("PM-REE-00b", "Gates que deciden el seguimiento", "main",
     r"^If(3|4|6|15|16|17|24|26|27)$"),

    # ── Sub-workflows completos
    ("PM-REE-01", "Seguimiento Rebeca (post-saludo)", "rebeca", r".*"),
    ("PM-REE-02", "Seguimiento Imagen (post-evento)", "imagen", r".*"),
    ("PM-REE-03", "Seguimiento Cotización (post-fichas)", "cotizacion", r".*"),
    ("PM-REE-04", "Seguimiento 7 pasos", "7pasos", r".*"),
    ("PM-TOOL-04", "Sub-workflow ATENCION_PERSONALIZADA", "atencion", r".*"),
    ("PM-TOOL-05", "Sub-workflow CALCULADORA", "calculadora", r".*"),
    ("PM-OUT-07", "Runner de captura de texto de salesbots", "salesbot-runner", r".*"),

    # ── Guardia de horario (lógica de negocio real, TZ America/Mexico_City)
    ("PM-OUT-08", "Guardia de horario laboral", "main", r"^Code(6|7|10|11|12)$"),

    # ── Cadena amojo vestigial: envío directo por la API interna de Kommo.
    # Es la arquitectura ANTERIOR a los salesbots; quedó huérfana. NO se migra.
    ("PM-MISC-02", "Cadena amojo vestigial, huérfana (NO migrar)", "main",
     r"^(Send_Attachment\d*|Get token\d*|Code3|Edit Fields\d*|Send_Message_\d*|"
     r"Recieve message)$"),

    # ── Sumideros del debounce (last-writer-wins): ramas que mueren a propósito
    ("PM-MISC-01", "Sumideros noOp del debounce", "main",
     r"^No Operation, do nothing\d*$"),
]

TITULOS = {g: t for g, t, _, _ in REGLAS}


def cargar():
    nodos = []
    for slug, ambito in WF.items():
        d = json.loads((BASE / f"{slug}.json").read_text())
        for n in d["nodes"]:
            if n["type"].endswith("stickyNote"):
                continue
            nodos.append({
                "wf": slug, "ambito": ambito, "nombre": n["name"],
                "tipo": n["type"].split(".")[-1],
                "disabled": bool(n.get("disabled")),
            })
    return nodos


def clasificar(nodos):
    asign, huerfanos = defaultdict(list), []
    for n in nodos:
        for grupo, _t, ambito, patron in REGLAS:
            if ambito not in ("*", n["ambito"]):
                continue
            if re.match(patron, n["nombre"]):
                asign[grupo].append(n)
                n["grupo"] = grupo
                break
        else:
            huerfanos.append(n)
    return asign, huerfanos


def main():
    nodos = cargar()
    asign, huerfanos = clasificar(nodos)
    total = len(nodos)
    cubiertos = sum(len(v) for v in asign.values())

    print(f"Nodos significativos: {total}")
    print(f"Asignados a grupos:   {cubiertos}")
    print(f"Huérfanos:            {len(huerfanos)}\n")

    dom = defaultdict(int)
    for g, v in asign.items():
        dom[g.split("-")[1]] += len(v)
    print("Por dominio:", " · ".join(f"{k}={v}" for k, v in sorted(dom.items())))
    print()
    for g, _t, _a, _p in REGLAS:
        if g in asign:
            print(f"  {g:12s} {len(asign[g]):4d}  {TITULOS[g]}")

    if huerfanos:
        print(f"\n🔴 {len(huerfanos)} nodos SIN DUEÑO — el registro no está terminado:")
        for n in huerfanos:
            print(f"   {n['wf']:22s} {n['nombre'][:44]:44s} <{n['tipo']}>")
        sys.exit(1)

    print(f"\n✅ GATE DE COBERTURA: {cubiertos}/{total} — cierra.")

    if "--generar" in sys.argv:
        OUT.mkdir(parents=True, exist_ok=True)
        with (OUT / "puntos.jsonl").open("w", encoding="utf-8") as fh:
            for g, _t, _a, _p in REGLAS:
                if g not in asign:
                    continue
                ns = asign[g]
                fh.write(json.dumps({
                    "id": g, "dominio": g.split("-")[1], "titulo": TITULOS[g],
                    "n_nodos": len(ns),
                    "nodos_origen": [f"{n['wf']}/{n['nombre']}" for n in ns],
                    "tipos": sorted({n["tipo"] for n in ns}),
                    "deshabilitados": [n["nombre"] for n in ns if n["disabled"]],
                    "contrato_origen": None, "evidencia_origen": None,
                    "intencion": None, "cambio": None, "clase_corrob": None,
                    "prueba_id": None, "assert": None, "estado": "PENDIENTE",
                    "artefacto": None,
                }, ensure_ascii=False) + "\n")
        print(f"→ {(OUT / 'puntos.jsonl').relative_to(REPO)}  ({len(asign)} puntos)")


if __name__ == "__main__":
    main()
