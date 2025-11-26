#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
PROGRAMA: digraph_matrix.py
AUTOR: David Arboledas Brihuega
HERRAMIENTA: Criptoanálisis clásico / Estadística de dígrafos

DESCRIPCIÓN GENERAL:
    Este programa cuenta todos los DÍGRAFOS SOLAPADOS (pares de letras
    consecutivas) en un texto normalizado al alfabeto A–Z y genera:
        1) Lista de frecuencias
        2) Matriz de doble entrada alineada

FUNCIONAMIENTO:
    1) Entrada desde archivo o stdin.
    2) Normalización del texto:
         - Mayúsculas
         - Sustituye Ñ → N
         - Elimina acentos y diacríticos
         - Filtra únicamente letras A–Z
    3) Generación de dígrafos solapados.
    4) Conteo y presentación de resultados.

USO:
    python3 digraph_matrix_clean_aligned_AZ.py archivo.txt
    cat archivo.txt | python3 digraph_matrix_clean_aligned_AZ.py      (Linux/Mac)
    type archivo.txt | python3 digraph_matrix_clean_aligned_AZ.py     (Windows)
    python3 digraph_matrix_clean_aligned_AZ.py -                      (stdin)

ARGUMENTOS:
    archivo.txt     Archivo de entrada o '-' para stdin.
    -h, --help      Ayuda estándar.
    --h, help, -?   Alias adicionales de ayuda extendida.

===============================================================================
"""

import sys
import argparse
import unicodedata
from collections import Counter

CELL_WIDTH = 4
ROW_LABEL_MIN_WIDTH = 1

# ---------------------------------------------------------------------------
# Normalización A–Z
# ---------------------------------------------------------------------------
def normalizar_AZ(texto: str) -> str:
    t = texto.upper().replace("Ñ", "N")
    t = unicodedata.normalize("NFD", t)
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    return "".join(ch for ch in t if "A" <= ch <= "Z")

# ---------------------------------------------------------------------------
# Dígrafos solapados
# ---------------------------------------------------------------------------
def digrafos_solapados(texto: str):
    return [texto[i:i+2] for i in range(len(texto) - 1)]

# ---------------------------------------------------------------------------
# Ayuda extendida
# ---------------------------------------------------------------------------
def ayuda_extendida():
    print("""
digraph_matrix_clean_aligned_AZ.py — Análisis de dígrafos solapados A–Z
(AYUDA EXTENDIDA)

USO:
    python3 digraph_matrix_clean.py file.txt
    cat file.txt | python digraph_matrix.py
    type file.txt | python digraph_matrix.py
    python digraph_matrix.py 

SALIDA:
    • Total de dígrafos solapados.
    • Tabla con: DÍGRAFO, FRECUENCIA, PORCENTAJE.
    • Matriz alineada de frecuencia (filas=1ª letra, columnas=2ª letra).

AYUDA:
    -h, --help      Ayuda estándar.
    --h, help, -?   Alias adicionales.

NOTA:
    CELL_WIDTH controla el ancho de columna en la matriz.
""")
    sys.exit(0)

# ---------------------------------------------------------------------------
def main():

    # Aliases de ayuda extendida
    if len(sys.argv) >= 2 and sys.argv[1].lower() in ("--h", "help", "-?"):
        ayuda_extendida()

    # Argumentos
    parser = argparse.ArgumentParser(
        description="Cuenta dígrafos solapados y genera una matriz de frecuencias."
    )
    parser.add_argument(
        "archivo",
        nargs="?",
        default="-",
        help="Archivo de entrada o '-' para leer desde stdin"
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

    # Normalización
    texto = normalizar_AZ(bruto)

    if len(texto) < 2:
        print("Texto demasiado corto para formar dígrafos.", file=sys.stderr)
        sys.exit(0)

    # Cálculo
    dig = digrafos_solapados(texto)
    conteo = Counter(dig)
    total = sum(conteo.values())

    # Lista de frecuencias
    print(f"TOTAL DIGRAFOS (solapados): {total}\n")
    print(f"{'DIGRAFO':<8} {'FRECUENCIA':>10} {'%':>7}")

    for dg, f in sorted(conteo.items(), key=lambda x: (-x[1], x[0])):
        pct = 100.0 * f / total
        print(f"{dg:<8} {f:>10} {pct:>6.2f}")

    # Matriz
    letras = sorted(set(texto))
    ancho_label = max(ROW_LABEL_MIN_WIDTH, len(max(letras, key=len)))

    print("\n\nDIGRAPH FREQUENCY MATRIX (rows=first, cols=second, blanks=0)\n")

    cabecera = " " * (ancho_label + 2) + "".join(f"{c:>{CELL_WIDTH}}" for c in letras)
    print(cabecera)
    print(" " * (ancho_label + 1) + "-" * (len(cabecera) - (ancho_label + 1)))

    blank = " " * CELL_WIDTH

    for r in letras:
        fila = []
        for c in letras:
            v = conteo.get(r+c, 0)
            fila.append(f"{v:>{CELL_WIDTH}}" if v > 0 else blank)
        print(f"{r:>{ancho_label}} |{''.join(fila)} |")

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
