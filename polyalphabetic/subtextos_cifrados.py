#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
PROGRAMA: subtextos_cifrados.py
AUTOR: David Arboledas Brihuega
HERRAMIENTA: Criptoanálisis clásico / Subtextos (Vigenère, polialfabéticos)

DESCRIPCIÓN GENERAL:
    Este programa divide un criptograma normalizado al alfabeto A–Z en N
    SUBTEXTOS, tomando caracteres en posiciones congruentes módulo N. Cada
    subtexto corresponde al resultado de cifrar con uno de los alfabetos de la
    clave (periodo N) en un cifrado polialfabético tipo Vigenère.

FUNCIONAMIENTO:
    1) Entrada por archivo o stdin.
    2) Normalización:
         - Mayúsculas
         - Ñ → N
         - Elimina acentos y caracteres no A–Z
    3) Se generan N subcriptogramas:
         subtexto 1: posiciones 1, 1+N, 1+2N...
         subtexto 2: posiciones 2, 2+N, 2+2N...
         ...
    4) Se guardan todos en un archivo (uno por línea) y se muestran por pantalla.

USO:
    python subtextos_cifrados.py -n 5 archivo.txt salida.txt
    cat archivo.txt | python subtextos_cifrados.py -n 4 - salida.txt
    python  subtextos_cifrados.py -n 7

ARGUMENTOS:
    -n N, --period N     Periodo de la clave (número de subtextos).
    archivo_entrada      Archivo o '-' para stdin.
    archivo_salida       Archivo donde guardar los subtextos.
    -h, --help           Ayuda estándar.
    --h, help, -?        Alias de ayuda extendida.

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
# División del criptograma en subtextos
# ---------------------------------------------------------------------------
def generar_subtextos(texto: str, n: int):
    """
    Devuelve una lista con los N subtextos correspondientes a un periodo N.
    """
    subtextos = []
    for i in range(n):
        sub = texto[i::n]
        subtextos.append(sub)
    return subtextos

# ---------------------------------------------------------------------------
# Ayuda extendida
# ---------------------------------------------------------------------------
def ayuda_extendida():
    print("""
subtextos_cifrados.py — Generación de subtextos para análisis de periodo
(AYUDA EXTENDIDA)

USO:
    python3 subtextos_cifrados.py -n 4 archivo.txt salida.txt
    cat archivo.txt | python3 subtextos_cifrados.py -n 5 - salida.txt

DESCRIPCIÓN:
    • Normaliza el texto a A–Z.
    • Divide el criptograma en N subtextos (posición i mod N).
    • Cada subtexto corresponde a un alfabeto de clave distinto (cifrado Vigenère).

ARGUMENTOS:
    -n, --period N    Número de subtextos (periodo de clave).
    archivo_entrada   Archivo o '-' para stdin.
    archivo_salida    Archivo donde se escriben los subtextos.
    -h, --help        Ayuda estándar.
    --h, help, -?     Alias adicionales.

NOTA:
    El archivo de salida incluye N líneas, cada una un subtexto.
""")
    sys.exit(0)

# ---------------------------------------------------------------------------
def main():

    # Aliases de ayuda
    if len(sys.argv) >= 2 and sys.argv[1].lower() in ("--h", "help", "-?"):
        ayuda_extendida()

    parser = argparse.ArgumentParser(
        description="Divide un criptograma A–Z en N subtextos para análisis polialfabético."
    )

    parser.add_argument(
        "-n", "--period",
        type=int,
        required=True,
        help="Periodo del cifrado (número de subtextos a generar)."
    )

    parser.add_argument(
        "archivo_entrada",
        help="Archivo de entrada o '-' para leer desde stdin."
    )

    parser.add_argument(
        "archivo_salida",
        help="Archivo donde se guardarán los subtextos."
    )

    args = parser.parse_args()

    # Leer texto
    if args.archivo_entrada != "-":
        try:
            with open(args.archivo_entrada, "r", encoding="utf-8") as f:
                bruto = f.read()
        except FileNotFoundError:
            print(f"Error: archivo '{args.archivo_entrada}' no encontrado.", file=sys.stderr)
            sys.exit(1)
    else:
        if sys.stdin.isatty():
            print("Introduce el criptograma. Finaliza con Ctrl+D o Ctrl+Z:", file=sys.stderr)
        bruto = sys.stdin.read()

    # Normalización
    texto = normalizar_AZ(bruto)

    if len(texto) == 0:
        print("Texto vacío tras normalización.", file=sys.stderr)
        sys.exit(0)

    N = args.period
    if N < 1:
        print("El periodo N debe ser ≥ 1.", file=sys.stderr)
        sys.exit(1)

    subtextos = generar_subtextos(texto, N)

    # Guardar en archivo
    try:
        with open(args.archivo_salida, "w", encoding="utf-8") as f:
            f.write("\n".join(subtextos))
    except Exception as e:
        print(f"No se pudo escribir en '{args.archivo_salida}': {e}", file=sys.stderr)
        sys.exit(1)

    # Mostrar por pantalla
    print(f"\nGENERADOS {N} SUBTEXTOS (periodo = {N}):\n")
    for i, st in enumerate(subtextos, 1):
        print(f"{i}: {st}")

    print(f"\nSubtextos guardados en: {args.archivo_salida}")

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
