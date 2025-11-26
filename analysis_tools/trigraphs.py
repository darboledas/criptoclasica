#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
PROGRAMA: trigrafos.py
AUTOR: David Arboledas Brihuega
HERRAMIENTA: Criptoanálisis clásico / Estadística de trígrafos

DESCRIPCIÓN GENERAL:
    Este programa cuenta todos los TRÍGRAFOS SOLAPADOS (tres letras consecutivas)
    en un texto normalizado A–Z y muestra una tabla ordenada por frecuencia.

FUNCIONAMIENTO:
    1) Entrada desde archivo o stdin.
    2) Normalización:
         - MAYÚSCULAS
         - Ñ → N
         - eliminación de tildes
         - filtrado A–Z
    3) Extracción de trígrafos solapados.
    4) Conteo y ordenación.
    5) Opción --top para mostrar solo los N más frecuentes.

USO:
    python trigrafos.py archivo.txt
    cat archivo.txt | python trigrafos.py      (Linux/Mac)
    type archivo.txt | python trigrafos.py     (Windows)
    python3 trigrafos.py - --top 20

ARGUMENTOS:
    archivo.txt     Archivo de entrada o '-' para stdin.
    --top N         Limita salida a los N trígrafos más frecuentes.
    -h, --help      Ayuda estándar.
    --h, help, -?   Alias de ayuda extendida.

===============================================================================
"""

import sys
import argparse
import unicodedata
from collections import Counter

# ---------------------------------------------------------------------------
# Normalización A–Z
# ---------------------------------------------------------------------------
def normalizar_AZ(texto: str) -> str:
    t = texto.upper().replace("Ñ", "N")
    t = unicodedata.normalize("NFD", t)
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    return "".join(ch for ch in t if "A" <= ch <= "Z")

# ---------------------------------------------------------------------------
# Trígrafos solapados
# ---------------------------------------------------------------------------
def trigrafos_solapados(texto: str):
    return [texto[i:i+3] for i in range(len(texto) - 2)]

# ---------------------------------------------------------------------------
# Ayuda extendida
# ---------------------------------------------------------------------------
def ayuda_extendida():
    print("""
trigrafos.py — Análisis de trígrafos solapados A–Z
(AYUDA EXTENDIDA)

USO:
    python3 trigrafos.py archivo.txt
    cat archivo.txt | python3 trigrafos.py
    type archivo.txt | python3 trigrafos.py
    python3 trigrafos.py - --top 20

ARGUMENTOS:
    --top N         Muestra solo los N trígrafos más frecuentes.
    -h, --help      Ayuda estándar.
    --h, help, -?   Alias adicionales.

SALIDA:
    • Total de trígrafos.
    • Tabla con TRÍGRAFO, FRECUENCIA y PORCENTAJE.
""")
    sys.exit(0)

# ---------------------------------------------------------------------------
def main():

    # Aliases de ayuda extendida
    if len(sys.argv) >= 2 and sys.argv[1].lower() in ("--h", "help", "-?"):
        ayuda_extendida()

    # Argumentos
    parser = argparse.ArgumentParser(
        description="Cuenta trígrafos solapados normalizados al alfabeto A–Z."
    )
    parser.add_argument(
        "archivo",
        nargs="?",
        default="-",
        help="Archivo de entrada o '-' para stdin"
    )
    parser.add_argument(
        "--top",
        type=int,
        default=0,
        help="Muestra solo los N trígrafos más frecuentes"
    )
    args = parser.parse_args()

    # Leer texto
    if args.archivo != "-":
        try:
            with open(args.archivo, "r", encoding="utf-8") as f:
                bruto = f.read()
        except FileNotFoundError:
            print(f"Error: archivo '{args.archivo}' no encontrado.", file=sys.stderr)
            sys.exit(1)
    else:
        if sys.stdin.isatty():
            print("Introduce texto. Finaliza con Ctrl+D o Ctrl+Z:", file=sys.stderr)
        bruto = sys.stdin.read()

    # Normalizar
    texto = normalizar_AZ(bruto)

    if len(texto) < 3:
        print("Texto demasiado corto para formar trígrafos.", file=sys.stderr)
        sys.exit(0)

    # Conteo
    tris = trigrafos_solapados(texto)
    conteo = Counter(tris)
    total = sum(conteo.values())

    # Salida
    print(f"TOTAL TRIGRAFOS (solapados): {total}\n")
    print(f"{'TRIGRAFO':<10} {'FRECUENCIA':>10} {'%':>7}")

    items = sorted(conteo.items(), key=lambda x: (-x[1], x[0]))

    if args.top > 0:
        items = items[:args.top]

    for tri, f in items:
        pct = 100.0 * f / total
        print(f"{tri:<10} {f:>10} {pct:>6.2f}")

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
