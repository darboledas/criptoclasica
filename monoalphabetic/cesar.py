#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
PROGRAMA: caesar.py
AUTOR: David Arboledas Brihuega
HERRAMIENTA: Cifrado, descifrado y análisis del cifrado César (A–Z)

EXTENSIONES AÑADIDAS:
    - Entrada directa por texto:        -t "TEXTO"
    - Entrada desde archivo:            -i archivo.txt
    - Entrada desde stdin:              -
    - Salida opcional a archivo:        -o salida.txt
    - Salida por pantalla siempre (además del archivo)

DESCRIPCIÓN:
    Implementación completa del cifrado de César con:
      - cifrado y descifrado mediante desplazamiento k (1–25),
      - fuerza bruta sobre los 25 desplazamientos posibles,
      - análisis rápido de frecuencias,
      - normalización A–Z del texto,
      - entrada desde texto, archivo o stdin,
      - salida opcional en grupos de 5 letras.

USO:
    python3 caesar.py --cifrar   -k 3 -t "HOLA MUNDO"
    python3 caesar.py --descifrar -k 7 -i cifrado.txt
    python3 caesar.py --fuerza-bruta -i criptograma.txt
    python3 caesar.py --analisis -t "ESTE ES EL MENSAJE"
    cat texto.txt | python3 caesar.py --cifrar -k 5 -
===============================================================================
"""

import sys
import argparse
import unicodedata
from collections import Counter

ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MOD = 26

# ---------------------------------------------------------------------------
# Normalización universal A–Z
# ---------------------------------------------------------------------------
def normalizar(texto: str) -> str:
    t = unicodedata.normalize("NFD", texto.upper())
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    return "".join(ch for ch in t if "A" <= ch <= "Z")

# ---------------------------------------------------------------------------
# Agrupar en bloques de 5
# ---------------------------------------------------------------------------
def grupo5(s: str) -> str:
    return " ".join(s[i:i+5] for i in range(0, len(s), 5))

# ---------------------------------------------------------------------------
# Cifrado / descifrado de César
# ---------------------------------------------------------------------------
def cifrar(plaintext: str, k: int) -> str:
    return "".join(chr(((ord(ch)-65 + k) % MOD) + 65) for ch in plaintext)

def descifrar(cipher: str, k: int) -> str:
    return "".join(chr(((ord(ch)-65 - k) % MOD) + 65) for ch in cipher)

# ---------------------------------------------------------------------------
# Fuerza bruta
# ---------------------------------------------------------------------------
def fuerza_bruta(cipher: str):
    for k in range(1, MOD):
        print(f"[k={k:2d}] {descifrar(cipher, k)}")

# ---------------------------------------------------------------------------
# Análisis de frecuencias
# ---------------------------------------------------------------------------
def analisis_frecuencias(texto: str):
    total = len(texto)
    freqs = Counter(texto)
    print("FRECUENCIAS:")
    for letra, f in sorted(freqs.items(), key=lambda x: (-x[1], x[0])):
        print(f"{letra}: {f:5d} ({100*f/total:5.2f}%)")

# ---------------------------------------------------------------------------
# Ayuda extendida
# ---------------------------------------------------------------------------
def ayuda_extendida():
    print("""
CAESAR.PY — AYUDA EXTENDIDA
Ejemplos:
  python3 caesar.py --cifrar   -k 3 -t "HOLA MUNDO"
  python3 caesar.py --descifrar -k 7 -i cifrado.txt
  python3 caesar.py --fuerza-bruta -i criptograma.txt
  echo HOLA | python3 caesar.py --cifrar -k 4 -
""")
    sys.exit(0)

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():

    # Atajos de ayuda
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("--h", "help", "-?"):
        ayuda_extendida()

    parser = argparse.ArgumentParser(description="Cifrado y análisis César (A–Z).")

    modo = parser.add_mutually_exclusive_group(required=True)
    modo.add_argument("--cifrar", action="store_true")
    modo.add_argument("--descifrar", action="store_true")
    modo.add_argument("--fuerza-bruta", action="store_true")
    modo.add_argument("--analisis", action="store_true")

    parser.add_argument("-k", "--clave", type=int, help="Desplazamiento (1–25)")
    parser.add_argument("-t", "--texto", help="Entrada directa por texto entre comillas")
    parser.add_argument("-i", "--input", help="Archivo de entrada")
    parser.add_argument("-o", "--output", help="Archivo de salida")
    parser.add_argument("--grupo5", action="store_true")

    parser.add_argument("stdin", nargs="?", help="'-' para leer de stdin")

    args = parser.parse_args()

    # --------------------
    # FUENTES DE ENTRADA
    # --------------------
    entradas = 0

    if args.texto:
        bruto = args.texto
        entradas += 1

    if args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                bruto = f.read()
        except:
            sys.exit(f"Error: no se pudo abrir '{args.input}'")
        entradas += 1

    if args.stdin == "-":
        bruto = sys.stdin.read()
        entradas += 1

    if entradas == 0:
        sys.exit("Error: debe usar -t, -i o '-' para stdin.")

    if entradas > 1:
        sys.exit("Error: use solo una fuente de entrada (-t, -i o stdin).")

    texto = normalizar(bruto)

    # --------------------
    # MODOS
    # --------------------
    if args.cifrar:
        if args.clave is None or not (1 <= args.clave <= 25):
            sys.exit("Error: se requiere -k N (1–25).")
        resultado = cifrar(texto, args.clave)

    elif args.descifrar:
        if args.clave is None or not (1 <= args.clave <= 25):
            sys.exit("Error: se requiere -k N (1–25).")
        resultado = descifrar(texto, args.clave)

    elif args.fuerza_bruta:
        fuerza_bruta(texto)
        return

    elif args.analisis:
        analisis_frecuencias(texto)
        return

    # --------------------
    # FORMATEO Y SALIDA
    # --------------------
    if args.grupo5:
        resultado = grupo5(resultado)

    print(resultado)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(resultado)
        print(f"[+] Resultado guardado en {args.output}")

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
