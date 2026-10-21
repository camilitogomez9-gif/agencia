#!/usr/bin/env python3
"""
HPF · hacer que el marcador de pago mande de verdad el PDF de números de cuenta.

PROBLEMA (item 11 de la reunión del 2026-08-11, verificado en vivo el 2026-08-12)
Oscar: "le gustaría avanzar con el pedido, así le paso los números de cuenta […] pero me
contestó otra cosa: le pido el comprobante del 50%. Pues todavía ni me manda los números de
cuenta y ya me está pidiendo el pago."

El prompt del Recolector le dice al agente que emita el marcador `url1234.com123` para
mandar los datos bancarios. Se midió: ese marcador aparece 4 veces en el prompt del
Recolector y CERO veces en código de cualquiera de los 11 workflows vivos. Nadie lo procesa.
En Kommo lo interceptaba un salesbot; en GHL no hay salesbots, así que hoy el marcador le
llega al cliente como texto literal y el PDF nunca sale.

Arreglar el orden en el prompt es necesario pero no alcanza: sin este cambio el agente
seguiría sin poder mandar los datos, y encima ahora se le prohíbe pedir el comprobante — o
sea que el cierre de pago se quedaría sin salida.

FIX
1. `Leer evento` (ya en la cadena principal por el fix del evento) devuelve además la
   media_url del PDF, leída de `hpf_fichas` — no hardcodeada. Una query, dos datos.
2. `Partir en burbujas` detecta el marcador, LO SACA del texto y adjunta el PDF a la burbuja
   donde estaba. Si por lo que sea no hay PDF en la caché, saca el marcador igual: que le
   llegue un mensaje sin adjunto es malo, que le llegue "url1234.com123" es peor.
"""
import importlib.util
import pathlib
import sys

_spec = importlib.util.spec_from_file_location(
    "hpfdeploy", pathlib.Path(__file__).parent / "hpf-deploy-workflow.py")
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)

SQL_VIEJO = ("-- Sub-select en vez de WHERE: así devuelve SIEMPRE una fila (evento NULL si no hay\n"
             "-- estado todavía) y `$('Leer evento').first()` nunca explota en el primer turno.\n"
             "SELECT (SELECT evento FROM hpf_estado_sesion WHERE session_id = $1) AS evento;")

SQL_NUEVO = ("-- Sub-selects en vez de WHERE: así devuelve SIEMPRE una fila (los campos en NULL si\n"
             "-- no hay estado todavía) y `$('Leer evento').first()` nunca explota en el primer turno.\n"
             "--\n"
             "-- `pdf_pago` sale de la caché del catálogo, no hardcodeado: es la ficha \"Métodos de\n"
             "-- Pago\" (el PDF NUMEROS DE CUENTA). La usa `Partir en burbujas` para resolver el\n"
             "-- marcador url1234.com123 que emite el Recolector y que en GHL no procesaba nadie.\n"
             "SELECT (SELECT evento FROM hpf_estado_sesion WHERE session_id = $1) AS evento,\n"
             "       (SELECT media_url FROM hpf_fichas\n"
             "         WHERE nombre ILIKE '%todos de pago%' AND media_url IS NOT NULL\n"
             "         LIMIT 1) AS pdf_pago;")

ANCHOR_PB = """const pasos = (salida.intermediateSteps || []).map(s => s?.action?.tool).filter(Boolean);"""

REEMPLAZO_PB = """// ── MARCADOR DE PAGO ────────────────────────────────────────────────────────────
// El prompt del Recolector le pide emitir `url1234.com123` para mandar los datos
// bancarios. En Kommo ese marcador lo interceptaba un salesbot; en GHL no hay
// salesbots y se midió que NINGÚN nodo de los 11 workflows lo procesaba, así que le
// llegaba al cliente como texto literal y el PDF nunca salía. Acá se resuelve: se
// saca el marcador del texto y se adjunta el PDF *NUMEROS DE CUENTA*.
//
// El orden importa y es el reclamo textual de Oscar: primero los datos de pago,
// después el comprobante. Si el PDF no está en la caché, el marcador se saca igual —
// un mensaje sin adjunto es malo, pero "url1234.com123" en el chat es peor.
const MARCADOR = /\\s*(?:el\\s+siguiente\\s+URL\\s*:?\\s*)?url1234\\.com123\\s*/gi;
const _le2 = $('Leer evento');
const pdfPago = _le2.isExecuted
  ? ((_le2.first().json || {}).pdf_pago || null) : null;
const teniaMarcador = MARCADOR.test(txt);
MARCADOR.lastIndex = 0;
if (teniaMarcador) {
  txt = txt.replace(MARCADOR, ' ').replace(/[ \\t]{2,}/g, ' ')
           .replace(/\\n{3,}/g, '\\n\\n').trim();
}

const pasos = (salida.intermediateSteps || []).map(s => s?.action?.tool).filter(Boolean);"""

ANCHOR_ADJ = """const partesFinales = fichas.concat(partes.map(p => (typeof p === 'string'
  ? { texto: p, adjuntos: [] } : p)));"""

REEMPLAZO_ADJ = """const partesFinales = fichas.concat(partes.map(p => (typeof p === 'string'
  ? { texto: p, adjuntos: [] } : p)));

// El PDF de los datos bancarios se cuelga de la última burbuja del agente (no de las
// fichas del catálogo, que van primero y son de producto). Así el cliente recibe el
// texto del cierre y los números de cuenta juntos, en un mismo mensaje.
if (teniaMarcador && pdfPago && partesFinales.length) {
  const ult = partesFinales[partesFinales.length - 1];
  ult.adjuntos = (ult.adjuntos || []).concat([pdfPago]);
}"""

ANCHOR_RET = """  texto_completo: txt,
  etapa_destino,"""

REEMPLAZO_RET = """  texto_completo: txt,
  etapa_destino,
  // Trazas del cierre de pago, para poder auditar en las ejecuciones si el PDF salió.
  pago_marcador: teniaMarcador,
  pago_pdf: teniaMarcador ? (pdfPago || null) : null,"""


def main():
    dry = "--dry-run" in sys.argv
    w = D.bajar("W6")
    idx = {n["name"]: n for n in w["nodes"]}
    print(f"W6 vivo: {len(w['nodes'])} nodos")

    # 1) SQL de Leer evento
    q = idx["Leer evento"]["parameters"]["query"]
    if "pdf_pago" in q:
        print("   • Leer evento: ya devuelve pdf_pago")
    elif q.count(SQL_VIEJO) == 1:
        idx["Leer evento"]["parameters"]["query"] = q.replace(SQL_VIEJO, SQL_NUEVO)
        print("   ~ Leer evento: SQL ampliado con pdf_pago")
    else:
        sys.exit("❌ no reconozco el SQL de Leer evento; ¿cambió?")

    # 2) Partir en burbujas
    js = idx["Partir en burbujas"]["parameters"]["jsCode"]
    if "MARCADOR" in js:
        print("   • Partir en burbujas: ya parcheado")
    else:
        for anchor, rep, nombre in ((ANCHOR_PB, REEMPLAZO_PB, "detección del marcador"),
                                    (ANCHOR_ADJ, REEMPLAZO_ADJ, "adjuntar el PDF"),
                                    (ANCHOR_RET, REEMPLAZO_RET, "trazas")):
            n = js.count(anchor)
            if n != 1:
                sys.exit(f"❌ anchor de «{nombre}» aparece {n} veces (tiene que ser 1)")
            js = js.replace(anchor, rep)
        # `txt` es const en el original y ahora se reasigna
        if "let txt = " not in js:
            if js.count("const txt = ") == 1:
                js = js.replace("const txt = ", "let txt = ")
                print("   ~ txt: const → let (ahora se reasigna al sacar el marcador)")
            elif "let txt" not in js:
                sys.exit("❌ no encuentro la declaración de txt")
        idx["Partir en burbujas"]["parameters"]["jsCode"] = js
        print(f"   ~ Partir en burbujas parcheado ({len(js)} chars)")

    if dry:
        print("(dry-run: no escribo)")
        return

    D.subir("W6", w)
    v = D.bajar("W6")
    vidx = {n["name"]: n for n in v["nodes"]}
    ok = True
    if "pdf_pago" in vidx["Leer evento"]["parameters"]["query"]:
        print("   ✅ Leer evento devuelve pdf_pago")
    else:
        ok = False
        print("   ❌ Leer evento sin pdf_pago")
    jsv = vidx["Partir en burbujas"]["parameters"]["jsCode"]
    for marca, desc in (("MARCADOR", "detección"), ("pdfPago", "adjunto"),
                        ("pago_marcador", "trazas"), ("let txt", "txt reasignable")):
        if marca in jsv:
            print(f"   ✅ Partir en burbujas: {desc}")
        else:
            ok = False
            print(f"   ❌ Partir en burbujas: falta {desc}")
    if len(v["nodes"]) != len(w["nodes"]):
        ok = False
        print("   ❌ cambió la cantidad de nodos")
    print("✅ aplicado y verificado" if ok else "❌ NO verificado")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
