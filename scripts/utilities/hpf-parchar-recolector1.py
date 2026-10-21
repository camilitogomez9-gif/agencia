#!/usr/bin/env python3
"""
HPF · L7 — Parcha el prompt de Recolector1 para que sepa usar la CALCULADORA real.

En producción, `AI Agent Recolector1` (la rama que atiende conversaciones que entran
por imagen) tiene conectado `CALCULADORA1`, que es el `toolCalculator` genérico de
LangChain: una calculadora aritmética. Su prompt fue escrito para eso — dice
"sumar los pesos resultantes y devolver ese resultado".

Decisión del cliente: conectarle la CALCULADORA real (W4). Pero una tool sin
instrucciones es una tool que el LLM usa mal, así que el prompt necesita el bloque
que sí describe el contrato `items` / `cuentas`.

Parche quirúrgico, dos reemplazos:
  1. El bloque `- **CALCULADORA**: …` (4 líneas del genérico) → el bloque completo
     del Recolector bueno, que documenta items/cuentas, los nombres canónicos, el
     ejemplo y la red de seguridad ante rechazo por mínimos.
  2. La línea que manda "contrastar el número de peso (kg) devuelto por la
     calculadora": la tool real devuelve costo, no peso. Quedaría instruyendo al LLM
     a leer un campo que no existe.

Todo lo demás del prompt queda intacto y se verifica por diff.
"""
import difflib
import hashlib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BASE = REPO / "clients/HPF_HappyFlops/04_agents/base-prod-2026-08-06"
FUENTE = BASE / "agente-recolector.md"
DESTINO = BASE / "agente-recolector1-imagen.md"
SALIDA = REPO / "clients/HPF_HappyFlops/04_agents/agente-recolector1-imagen-parchado.md"

INICIO = "- **CALCULADORA**:"
FIN = "- **ATENCION_PERSONALIZADA**:"


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


def bloque(txt):
    i = txt.index(INICIO)
    j = txt.index(FIN, i)
    return txt[i:j]


def main():
    fuente, destino = FUENTE.read_text(), DESTINO.read_text()
    bloque_bueno = bloque(fuente)
    bloque_viejo = bloque(destino)

    nuevo = destino.replace(bloque_viejo, bloque_bueno, 1)
    if nuevo == destino:
        print("❌ no se reemplazó el bloque de la tool")
        sys.exit(1)

    # 2) la instrucción de leer el peso: la tool real devuelve costo
    patron = re.compile(
        r"- En base al numero devuelto por la calculadora completar la cotización y "
        r"contrastar el numero de peso \(kg\) devuelto por la calculadora con el rango "
        r"de pesos informado sin confundir las cuentas ni mostrarle este resultado al usuario\.")
    reemplazo = ("- En base al `costo_total_envio` devuelto por la tool \"CALCULADORA\" "
                 "completar la cotización, usando ese valor exacto y sin modificarlo. "
                 "Nunca le muestres al cliente el peso ni la cantidad de cajas.")
    nuevo2, n = patron.subn(reemplazo, nuevo)
    if n != 1:
        print(f"⚠️  la línea del peso no se encontró tal cual (n={n}); "
              f"revisar a mano antes de deployar")
    nuevo = nuevo2

    # 3 y 4) Las dos menciones que seguían describiendo la calculadora aritmética.
    # Ambas le piden al LLM estimar el envío de memoria por rangos de peso — que es
    # justo lo que el mismo prompt prohíbe en "Los únicos precios válidos son…".
    EXTRA = [
        (
            "- Determina el costo del envío según el peso total de la compra y "
            "recalculalo cada vez que se modifique o se agreguen productos a la "
            "cotizacion, usa la tool 'CALCULADORA'. ",
            "- Determina el costo del envío activando la tool 'CALCULADORA' con el "
            "arreglo `items` de la cotización, y usá el `costo_total_envio` que devuelve "
            "tal cual, sin recalcularlo por tu cuenta. Si el cliente modifica productos "
            "o cantidades, volvé a llamar la tool con el `items` actualizado. ",
        ),
        (
            '- Llama a la TOOL "CALCULADORA" para calcular el costo de envio y recuerda '
            "el rango de kilos y cuanto sale el envio en consecuencia.",
            # redacción tomada del Recolector bueno en su lugar equivalente
            '- Llama a la TOOL "CALCULADORA" para calcular el costo de envio enviando la '
            "variable correspondiente en el formato especificado.",
        ),
    ]
    for viejo, nuevo_txt in EXTRA:
        if viejo not in nuevo:
            print(f"⚠️  no encontré para reemplazar: {viejo[:70]}…")
            continue
        nuevo = nuevo.replace(viejo, nuevo_txt, 1)

    encabezado = (
        "<!-- PARCHADO — no es byte-exacto del origen.\n"
        f"     base: agente-recolector1-imagen.md  sha256 {sha(destino)[:16]}…\n"
        f"     resultado:                          sha256 {sha(nuevo)[:16]}…\n"
        "     Dos cambios, ambos porque Recolector1 pasa de la calculadora aritmética\n"
        "     (toolCalculator de LangChain) a la CALCULADORA real de envío/empaque:\n"
        "       1. bloque de la tool → el del Recolector bueno (items/cuentas,\n"
        "          nombres canónicos, ejemplo, red de seguridad ante mínimos)\n"
        "       2. la instrucción de leer el peso (kg) → leer costo_total_envio\n"
        "       3-4. las dos menciones que pedían estimar el envío de memoria por\n"
        "          rangos de peso → llamar la tool y usar su valor exacto\n"
        "     Regenerar: scripts/utilities/hpf-parchar-recolector1.py -->\n\n")
    SALIDA.write_text(encabezado + nuevo, encoding="utf-8")

    print(f"origen  Recolector1 : {len(destino):6d} chars  sha {sha(destino)[:12]}")
    print(f"parchado            : {len(nuevo):6d} chars  sha {sha(nuevo)[:12]}")
    print(f"bloque insertado    : {len(bloque_bueno)} chars (venía de {len(bloque_viejo)})")

    diff = list(difflib.unified_diff(destino.splitlines(), nuevo.splitlines(),
                                     "origen", "parchado", lineterm="", n=1))
    quitadas = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
    agregadas = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
    print(f"diff                : -{quitadas} líneas / +{agregadas} líneas")

    # el resto del prompt tiene que estar intacto: mismo texto fuera de los 2 bloques
    resto_ori = patron.sub("", destino.replace(bloque_viejo, ""))
    resto_new = patron.sub("", nuevo.replace(bloque_bueno, "").replace(reemplazo, ""))
    for viejo, nuevo_txt in EXTRA:
        resto_ori = resto_ori.replace(viejo, "")
        resto_new = resto_new.replace(nuevo_txt, "")
    intacto = resto_ori.strip() == resto_new.strip()
    print(f"resto del prompt    : {'intacto ✅' if intacto else 'CAMBIÓ ❌ — revisar'}")

    # menciones residuales de la tool que quedaron sin tocar, para revisión humana
    print("\nmenciones residuales de CALCULADORA que quedaron como estaban:")
    for i, l in enumerate(nuevo.splitlines(), 1):
        if "CALCULADORA" in l.upper() and INICIO not in l and "costo_total_envio" not in l:
            print(f"  L{i}: {l.strip()[:110]}")
    print(f"\n→ {SALIDA.relative_to(REPO)}")


if __name__ == "__main__":
    main()
