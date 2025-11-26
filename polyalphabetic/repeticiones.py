#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
PROGRAMA: repeticiones.py
AUTOR: David Arboledas Brihuega
HERRAMIENTA: Criptoanálisis clásico / Detección de repeticiones

DESCRIPCIÓN GENERAL:
    Este programa detecta SECUENCIAS REPETIDAS de longitud mínima N dentro de un
    texto normalizado al alfabeto A–Z. Para cada secuencia que aparezca dos o
    más veces, se muestran sus posiciones y los intervalos entre repeticiones,
    información útil para análisis tipo Kasiski en cifrados polialfabéticos.

FUNCIONAMIENTO:
    1) Entrada desde archivo o stdin.
    2) Normalización:
         - Mayúsculas
         - Filtrado solo A–Z
    3) Búsqueda de secuencias repetidas de longitud mínima N.
    4) Cálculo de intervalos entre posiciones de repetición.

USO:
    python3 repeticiones.py -n 3 archivo.txt
    cat archivo.txt | python3 repeticiones.py -n 4
    python3 repeticiones.py -n 3 -

ARGUMENTOS:
    -n N, --min-length N   Longitud mínima de las secuencias a buscar.
    archivo.txt            Archivo de entrada o '-' para stdin.
    -h, --help             Ayuda estándar.
    --h, help, -?          Alias de ayuda extendida.

SALIDA:
    • Secuencia repetida
    • Posiciones (1-indexed)
    • Intervalos entre repeticiones (para análisis Kasiski)

===============================================================================
"""

import sys
import argparse
import unicodedata
from collections import defaultdict

# ---------------------------------------------------------------------------
# Normalización A–Z
# ---------------------------------------------------------------------------
def normalizar_AZ(texto: str) -> str:
    """Convierte a MAYÚSCULAS y filtra únicamente letras A–Z."""
    t = texto.upper()
    t = unicodedata.normalize("NFD", t)
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    return "".join(ch for ch in t if "A" <= ch <= "Z")

# ---------------------------------------------------------------------------
# Detección de repeticiones (método Kasiski generalizado)
# ---------------------------------------------------------------------------
def encontrar_repeticiones(texto: str, longitud_minima: int):
    """
    Devuelve un diccionario:
        secuencia -> lista de posiciones en las que aparece
    """
    resultados = defaultdict(list)

    n = len(texto)
    for L in range(longitud_minima, n + 1):
        for i in range(n - L + 1):
            seq = texto[i:i + L]
            resultados[seq].append(i)

    return resultados

# ---------------------------------------------------------------------------
# Ayuda extendida
# ---------------------------------------------------------------------------
def ayuda_extendida():
    print("""
repeticiones.py — Detección de repeticiones para análisis Kasiski
(AYUDA EXTENDIDA)

USO:
    python3 repeticiones.py -n 3 archivo.txt
    cat archivo.txt | python3 repeticiones.py -n 4
    python3 repeticiones.py -n 4 -

DESCRIPCIÓN:
    • Normaliza el texto a A–Z.
    • Busca secuencias de longitud mínima N.
    • Muestra posiciones (1-indexed) e intervalos entre repeticiones.

ARGUMENTOS:
    -n, --min-length N   Longitud mínima de secuencias.
    archivo.txt          Archivo o '-' para stdin.
    -h, --help           Ayuda estándar.
    --h, help, -?        Alias adicionales.

NOTA:
    Para textos largos, aumentar N (p. ej., 3–5) evita explosión combinatoria.
""")
    sys.exit(0)

# ---------------------------------------------------------------------------
def main():

    # Aliases de ayuda
    if len(sys.argv) >= 2 and sys.argv[1].lower() in ("--h", "help", "-?"):
        ayuda_extendida()

    # Argumentos
    parser = argparse.ArgumentParser(
        description="Busca secuencias repetidas de longitud mínima N en texto A–Z."
    )

    parser.add_argument(
        "-n", "--min-length",
        type=int,
        required=True,
        help="Longitud mínima de las secuencias a buscar."
    )

    parser.add_argument(
        "archivo",
        nargs="?",
        default="-",
        help="Archivo de entrada o '-' para stdin"
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

    if len(texto) == 0:
        print("Texto vacío tras normalización.", file=sys.stderr)
        sys.exit(0)

    L = args.min_length
    if L < 1:
        print("La longitud mínima debe ser ≥ 1.", file=sys.stderr)
        sys.exit(1)

    rep = encontrar_repeticiones(texto, L)

    print("\nSECUENCIAS REPETIDAS (posiciones e intervalos):\n")

    encontrado = False
    for secuencia, posiciones in rep.items():
        if len(posiciones) >= 2:
            encontrado = True

            # Posiciones como 1-indexed
            pos_1 = [p + 1 for p in posiciones]
            intervalos = [posiciones[i+1] - posiciones[i] for i in range(len(posiciones) - 1)]

            print(f"{secuencia}: {pos_1}  |  Intervalos: {intervalos}")

    if not encontrado:
        print("No se han encontrado repeticiones con esa longitud mínima.")

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
