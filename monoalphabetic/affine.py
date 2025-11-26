#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
PROGRAMA: affine.py
AUTOR: David Arboledas Brihuega
HERRAMIENTA: Cifrado y descifrado Afín (A–Z, convención A=1…Y=25, Z=0)

DESCRIPCIÓN:
    Implementación completa del cifrado afín:
        C = (a·P + b) mod 26
    donde:
        - a debe cumplir gcd(a, 26) = 1 para ser invertible,
        - b es un desplazamiento aditivo.

    Funcionalidades:
        - cifrado y descifrado,
        - cálculo automático del inverso modular de a,
        - normalización completa del texto (A–Z),
        - entrada desde texto (-t), archivo (-i) o stdin (-),
        - salida opcional a archivo (-o),
        - formateo opcional en grupos de 5.

USO RÁPIDO:
    python3 affine.py --cifrar -a 5 -b 8 -t "TEXTO DE PRUEBA"
    python3 affine.py --descifrar -a 5 -b 8 -i cifrado.txt
    echo ABC | python3 affine.py --cifrar -a 7 -b 2 -
    python3 affine.py --h    (ayuda extendida)
===============================================================================
"""

import sys
import argparse
import unicodedata
from math import gcd

ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MOD = 26

# ---------------------------------------------------------------------------
# Normalización universal A–Z
# ---------------------------------------------------------------------------
def normalizar(texto: str) -> str:
    """Convierte a mayúsculas, elimina tildes y deja solo A–Z."""
    t = unicodedata.normalize("NFD", texto.upper())
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    return "".join(ch for ch in t if "A" <= ch <= "Z")

# ---------------------------------------------------------------------------
# Conversión A=1…Z=0
# ---------------------------------------------------------------------------
def letra_a_num(ch: str) -> int:
    n = ord(ch) - 64  # A=1
    return 0 if n == 26 else n

def num_a_letra(n: int) -> str:
    return "Z" if n == 0 else chr(n + 64)

# ---------------------------------------------------------------------------
# Inverso modular
# ---------------------------------------------------------------------------
def inverso_mod(a: int, m: int = 26) -> int:
    """Devuelve el inverso modular de a mod m si existe."""
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError(f"No existe inverso modular para a={a} mod {m}")

# ---------------------------------------------------------------------------
# Cifrado Afín
# ---------------------------------------------------------------------------
def cifrar(plaintext: str, a: int, b: int) -> str:
    out = []
    for ch in plaintext:
        p = letra_a_num(ch)
        c = (a * p + b) % MOD
        out.append(num_a_letra(c))
    return "".join(out)

def descifrar(cipher: str, a: int, b: int) -> str:
    a_inv = inverso_mod(a, MOD)
    out = []
    for ch in cipher:
        c = letra_a_num(ch)
        p = (a_inv * (c - b)) % MOD
        out.append(num_a_letra(p))
    return "".join(out)

# ---------------------------------------------------------------------------
# Bloques de cinco
# ---------------------------------------------------------------------------
def grupo5(s: str) -> str:
    return " ".join(s[i:i+5] for i in range(0, len(s), 5))

# ---------------------------------------------------------------------------
# Ayuda extendida
# ---------------------------------------------------------------------------
def ayuda_extendida():
    print("""
AFFINE.PY — AYUDA EXTENDIDA

MODOS:
  --cifrar                  Cifrado afín
  --descifrar               Descifrado afín

PARÁMETROS:
  -a A                      Parámetro multiplicativo (requiere gcd(a,26)=1)
  -b B                      Parámetro aditivo (0–25)
  -t "TEXTO"                Entrada por argumento
  -i archivo.txt            Entrada desde archivo
  -o salida.txt             Guardar salida en archivo
  --grupo5                  Formatear resultado en grupos de 5

EJEMPLOS:
  python3 affine.py --cifrar   -a 5 -b 8 -t "ATAQUE AL AMANECER"
  python3 affine.py --descifrar -a 7 -b 3 -i criptograma.txt
  cat mensaje.txt | python3 affine.py --cifrar -a 11 -b 2 -
""")
    sys.exit(0)

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():

    if len(sys.argv) >= 2 and sys.argv[1].lower() in ("--h", "-?", "help"):
        ayuda_extendida()

    parser = argparse.ArgumentParser(
        description="Cifrado y descifrado Afín (A–Z, convención A=1…Z=0)."
    )

    modo = parser.add_mutually_exclusive_group(required=True)
    modo.add_argument("--cifrar", action="store_true")
    modo.add_argument("--descifrar", action="store_true")

    parser.add_argument("-a", type=int, required=True,
                        help="Parámetro multiplicativo a (gcd(a,26)=1).")
    parser.add_argument("-b", type=int, required=True,
                        help="Parámetro aditivo b (0–25).")

    parser.add_argument("-t", "--texto", help="Texto directo entre comillas.")
    parser.add_argument("-i", "--input", help="Archivo de entrada.")
    parser.add_argument("-o", "--output", help="Archivo de salida.")
    parser.add_argument("--grupo5", action="store_true", help="Salida en bloques de 5 letras.")

    parser.add_argument("stdin_rest", nargs="?", default=None,
                        help="'-' para leer desde stdin.")

    args = parser.parse_args()

    # Validación de parámetros
    if gcd(args.a, 26) != 1:
        sys.exit("Error: gcd(a,26) debe ser 1 para que exista inverso.")

    b = args.b % 26

    # Obtener texto
    if args.texto:
        bruto = args.texto
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                bruto = f.read()
        except FileNotFoundError:
            sys.exit(f"Error: archivo '{args.input}' no encontrado.")
    elif args.stdin_rest == "-":
        bruto = sys.stdin.read()
    else:
        sys.exit("Error: no se indicó ni texto (-t), ni archivo (-i), ni stdin ('-').")

    texto = normalizar(bruto)

    # Ejecutar cifrado/descifrado
    if args.cifrar:
        salida = cifrar(texto, args.a, b)
    else:
        salida = descifrar(texto, args.a, b)

    if args.grupo5:
        salida = grupo5(salida)

    # Salida a archivo o pantalla
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(salida)
    print(salida)

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
