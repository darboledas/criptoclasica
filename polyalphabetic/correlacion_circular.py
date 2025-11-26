#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
PROGRAMA: correlacion_circular.py
AUTOR: David Arboledas Brihuega
HERRAMIENTA: Criptoanálisis clásico / Correlación circular de frecuencias

DESCRIPCIÓN GENERAL:
    Este programa calcula la CORRELACIÓN CIRCULAR entre las frecuencias A–Z
    obtenidas de las dos primeras líneas de un texto ya normalizado. Para cada
    desplazamiento k (0–25) se calcula:

        correl(k) = sum( f1[i] * f2[(i+k) mod 26] )

    El desplazamiento que maximiza esta correlación suele indicar la relación
    entre dos secuencias cifradas bajo un cifrado polialfabético (p. ej.,
    Vigenère, Beaufort) o la coincidencia estructural entre dos subtextos.

FUNCIONAMIENTO:
    1) Entrada por archivo o stdin.
    2) Normalización del texto:
         - Mayúsculas
         - Ñ → N
         - Eliminación de acentos y caracteres no A–Z
    3) Cálculo de las frecuencias de las dos líneas.
    4) Rotación circular de la segunda línea y productos escalares sucesivos.
    5) Identificación del desplazamiento con correlación máxima.

USO:
    python3 correlacion_circular.py archivo.txt
    cat archivo.txt | python3 correlacion_circular.py
    python3 correlacion_circular.py -

ARGUMENTOS:
    archivo.txt     Archivo de entrada o '-' para stdin.
    -h, --help      Ayuda estándar.
    --h, help, -?   Alias de ayuda extendida.

===============================================================================
"""

import sys
import argparse
import unicodedata

# ---------------------------------------------------------------------------
# Normalización A–Z
# ---------------------------------------------------------------------------
def normalizar_AZ(texto: str) -> str:
    t = texto.upper().replace("Ñ", "N")
    t = unicodedata.normalize("NFD", t)
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    return "".join(ch for ch in t if "A" <= ch <= "Z")

# ---------------------------------------------------------------------------
# Frecuencias A–Z
# ---------------------------------------------------------------------------
def contar_letras(texto: str):
    frecuencias = [0] * 26
    for ch in texto:
        if "A" <= ch <= "Z":
            frecuencias[ord(ch) - ord("A")] += 1
    return frecuencias

# ---------------------------------------------------------------------------
# Rotación circular
# ---------------------------------------------------------------------------
def desplazar(arr):
    return arr[1:] + [arr[0]]

# ---------------------------------------------------------------------------
# Ayuda extendida
# ---------------------------------------------------------------------------
def ayuda_extendida():
    print("""
correlacion_circular.py — Correlación circular entre dos líneas A–Z
(AYUDA EXTENDIDA)

USO:
    python correlacion_circular.py archivo.txt
    cat archivo.txt | python correlacion_circular.py
    python3 correlacion_circular.py -

DESCRIPCIÓN:
    • Normaliza el texto a A–Z.
    • Lee las dos primeras líneas del fichero.
    • Calcula 26 correlaciones por productos escalares circulares.
    • Determina el desplazamiento con coincidencia máxima.

ARGUMENTOS:
    archivo.txt    Archivo o '-' para stdin.
    -h, --help     Ayuda estándar.
    --h, help, -?  Alias adicionales.
""")
    sys.exit(0)

# ---------------------------------------------------------------------------
def main():

    # Aliases manuales para ayuda extendida
    if len(sys.argv) >= 2 and sys.argv[1].lower() in ("--h", "help", "-?"):
        ayuda_extendida()

    parser = argparse.ArgumentParser(
        description="Correlación circular de frecuencias A–Z entre dos líneas."
    )
    parser.add_argument(
        "archivo",
        nargs="?",
        default="-",
        help="Archivo de entrada o '-' para stdin"
    )
    args = parser.parse_args()

    # Lectura
    if args.archivo != "-":
        try:
            with open(args.archivo, "r", encoding="utf-8") as f:
                lineas = f.readlines()
        except FileNotFoundError:
            print(f"Error: archivo '{args.archivo}' no encontrado.", file=sys.stderr)
            sys.exit(1)
    else:
        lineas = sys.stdin.readlines()

    if len(lineas) < 2:
        print("Se necesitan al menos DOS líneas de texto.", file=sys.stderr)
        sys.exit(1)

    # Normalizar
    l1 = normalizar_AZ(lineas[0])
    l2 = normalizar_AZ(lineas[1])

    if len(l1) == 0 or len(l2) == 0:
        print("Una de las líneas está vacía tras normalizar.", file=sys.stderr)
        sys.exit(1)

    f1 = contar_letras(l1)
    f2 = contar_letras(l2)

    # Mostrar frecuencias
    print("\nFrecuencias A–Z")
    print("[A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z]")
    print(f"Línea 1: {f1}")
    print(f"Línea 2: {f2}")

    # Correlación circular
    correl = []
    v2 = f2.copy()

    for _ in range(26):
        correl.append(sum(a * b for a, b in zip(f1, v2)))
        v2 = desplazar(v2)

    print("\nCORRELACIÓN CIRCULAR 0–25:\n")
    for i, val in enumerate(correl):
        letra = chr(ord("A") + i)
        print(f"{letra}: {val}")

    # Desplazamiento máximo
    max_letra = chr(ord("A") + correl.index(max(correl)))
    print(f"\nDesplazamiento con correlación máxima: {max_letra}")

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
