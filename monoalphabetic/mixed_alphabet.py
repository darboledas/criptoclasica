#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
PROGRAMA: mixed_alphabet.py
AUTOR: David Arboledas Brihuega
HERRAMIENTA: Generación de alfabetos mixtos y variantes clásicas (A–Z)

DESCRIPCIÓN:
    Construye alfabetos mixtos utilizados en criptografía clásica:

      • Alfabeto mixto simple por palabra clave.
      • Alfabeto mixto invertido.
      • Alfabeto mixto con desplazamiento circular.
      • Alfabeto columnar (método Kasiski/Bellaso).
      • Alfabetos para Quagmire I, II, III y IV.

    Todas las claves y textos se normalizan a A–Z.
    Soporta entrada por archivo, texto literal o stdin.
    Puede guardar el alfabeto resultante en un archivo.

===============================================================================
"""

import sys
import argparse
import unicodedata
import string

ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# ---------------------------------------------------------------------------
# Normalización universal A–Z
# ---------------------------------------------------------------------------
def normalizar(s: str) -> str:
    s = unicodedata.normalize("NFD", s.upper())
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return "".join(ch for ch in s if ch in string.ascii_uppercase)


# ---------------------------------------------------------------------------
# Construcción de alfabetos básicos
# ---------------------------------------------------------------------------
def alfabeto_mixto_simple(clave: str) -> str:
    clave = normalizar(clave)
    resultado = []
    for ch in clave:
        if ch not in resultado:
            resultado.append(ch)
    for ch in ALFABETO:
        if ch not in resultado:
            resultado.append(ch)
    return "".join(resultado)


def alfabeto_invertido(clave: str) -> str:
    base = alfabeto_mixto_simple(clave)
    return base[::-1]


def alfabeto_desplazado(clave: str, k: int) -> str:
    base = alfabeto_mixto_simple(clave)
    k %= 26
    return base[k:] + base[:k]


# ---------------------------------------------------------------------------
# Columnar — estilo Kasiski/Bellaso
# ---------------------------------------------------------------------------
def alfabeto_columnar(clave: str) -> str:
    clave = normalizar(clave)
    n = len(clave)

    resto = "".join(ch for ch in ALFABETO if ch not in clave)
    texto = clave + resto

    filas = []
    while texto:
        filas.append(texto[:n])
        texto = texto[n:]

    order = sorted(range(n), key=lambda i: clave[i])

    salida = []
    for c in order:
        for fila in filas:
            if c < len(fila):
                salida.append(fila[c])

    return "".join(salida)


# ---------------------------------------------------------------------------
# Quagmire I–IV  (CLARO y CIFRADO)
# ---------------------------------------------------------------------------
def quagmire_I(clave_claro: str, clave_cifrado: str) -> tuple:
    claro = ALFABETO
    cif = alfabeto_mixto_simple(clave_cifrado)
    return claro, cif


def quagmire_II(clave_claro: str, clave_cifrado: str) -> tuple:
    claro = alfabeto_mixto_simple(clave_claro)
    cif = ALFABETO
    return claro, cif


def quagmire_III(clave_claro: str, clave_cifrado: str) -> tuple:
    claro = alfabeto_mixto_simple(clave_claro)
    cif = alfabeto_mixto_simple(clave_cifrado)
    return claro, cif


def quagmire_IV(clave_claro: str, clave_cifrado: str) -> tuple:
    claro = alfabeto_columnar(clave_claro)
    cif = alfabeto_columnar(clave_cifrado)
    return claro, cif


# ---------------------------------------------------------------------------
# Ayuda extendida
# ---------------------------------------------------------------------------
def ayuda_extendida():
    print("""
MIXED_ALPHABET.PY — AYUDA EXTENDIDA

VARIANTES DISPONIBLES:
  --clave PAL        → alfabeto mixto simple
  --invertido        → invierte el alfabeto mixto
  --desp K           → desplaza el alfabeto mixto en K posiciones
  --columnar         → alfabeto mixto por columnas (Kasiski/Bellaso)

SISTEMAS QUAGMIRE:
  --quagmire1  --clave-cifrado C
  --quagmire2  --clave-claro L
  --quagmire3  --clave-claro L --clave-cifrado C
  --quagmire4  --clave-claro L --clave-cifrado C

ENTRADAS:
  --clave, --clave-claro, --clave-cifrado se normalizan a A–Z.
  Archivoo '-' para stdin.

SALIDA:
  En pantalla o con -o archivo.txt

EJEMPLOS:
  python3 mixed_alphabet.py --clave MAGIA
  python3 mixed_alphabet.py --columnar --clave FORTUNA
  python3 mixed_alphabet.py --invertido --clave ORION
  python3 mixed_alphabet.py --quagmire3 --clave-claro SOL --clave-cifrado LUNA
""")
    sys.exit(0)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():

    if len(sys.argv) >= 2 and sys.argv[1].lower() in ("--h", "help", "-?"):
        ayuda_extendida()

    parser = argparse.ArgumentParser(
        description="Generación de alfabetos mixtos clásicos (A–Z)."
    )

    parser.add_argument("--clave", help="Palabra clave para alfabeto mixto simple.")
    parser.add_argument("--invertido", action="store_true")
    parser.add_argument("--desp", type=int, help="Desplazamiento circular del alfabeto.")
    parser.add_argument("--columnar", action="store_true")

    # Quagmire
    parser.add_argument("--quagmire1", action="store_true")
    parser.add_argument("--quagmire2", action="store_true")
    parser.add_argument("--quagmire3", action="store_true")
    parser.add_argument("--quagmire4", action="store_true")
    parser.add_argument("--clave-claro", help="Clave para construir el alfabeto CLARO.")
    parser.add_argument("--clave-cifrado", help="Clave para construir el alfabeto CIFRADO.")

    parser.add_argument("-o", "--output", help="Archivo de salida.")
    args = parser.parse_args()

    # ------------------------------
    # Quagmire I–IV
    # ------------------------------
    if args.quagmire1:
        if not args.clave_cifrado:
            sys.exit("Error: --quagmire1 requiere --clave-cifrado.")
        claro, cif = quagmire_I("", args.clave_cifrado)
        texto = f"CLARO : {claro}\nCIFRADO: {cif}"

    elif args.quagmire2:
        if not args.clave_claro:
            sys.exit("Error: --quagmire2 requiere --clave-claro.")
        claro, cif = quagmire_II(args.clave_claro, "")
        texto = f"CLARO : {claro}\nCIFRADO: {cif}"

    elif args.quagmire3:
        if not (args.clave_claro and args.clave_cifrado):
            sys.exit("Error: --quagmire3 requiere --clave-claro y --clave-cifrado.")
        claro, cif = quagmire_III(args.clave_claro, args.clave_cifrado)
        texto = f"CLARO : {claro}\nCIFRADO: {cif}"

    elif args.quagmire4:
        if not (args.clave_claro and args.clave_cifrado):
            sys.exit("Error: --quagmire4 requiere --clave-claro y --clave-cifrado.")
        claro, cif = quagmire_IV(args.clave_claro, args.clave_cifrado)
        texto = f"CLARO : {claro}\nCIFRADO: {cif}"

    # ------------------------------
    # Alfabetos simples / mixtos
    # ------------------------------
    else:
        if not args.clave:
            sys.exit("Error: se requiere --clave para generar un alfabeto mixto.")

        texto = alfabeto_mixto_simple(args.clave)

        if args.columnar:
            texto = alfabeto_columnar(args.clave)

        if args.invertido:
            texto = texto[::-1]

        if args.desp is not None:
            k = args.desp % 26
            texto = texto[k:] + texto[:k]

    # ------------------------------
    # Salida
    # ------------------------------
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(texto)
    else:
        print(texto)


if __name__ == "__main__":
    main()
