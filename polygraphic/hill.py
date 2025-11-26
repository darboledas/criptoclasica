#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
PROGRAMA: hill.py
AUTOR: David Arboledas Brihuega
HERRAMIENTA: Cifrado y descifrado Hill (matriz 2×2) con alfabeto A=1…Y=25, Z=0

DESCRIPCIÓN:
    Implementación del cifrado Hill 2×2 usando la convención histórica:
        A=1, B=2, ..., Y=25, Z=0 (módulo 26)

    El texto se normaliza a A–Z. Se comprueba que la matriz sea invertible
    módulo 26 y se genera automáticamente la matriz inversa para descifrado.

    Entrada desde archivo o stdin. Salida opcional en bloques de 5.

USO:
    python3 hill.py --cifrar   --matriz "a b c d" archivo.txt
    python3 hill.py --descifrar --matriz "a b c d" archivo.txt
    cat mensaje.txt | python3 hill.py --cifrar --matriz "6 24 1 13" -

ARGUMENTOS:
    --cifrar / --descifrar   Selección del modo (uno obligatorio)
    --matriz "a b c d"       Matriz 2×2
    --grupo5                  Salida en grupos de 5 letras
    archivo                   Archivo de entrada o '-' para stdin
===============================================================================
"""

import sys
import argparse
import unicodedata
import numpy as np

# ---------------------------------------------------------------------------
# Normalización universal A–Z
# ---------------------------------------------------------------------------
def normalizar_AZ(texto: str) -> str:
    t = texto.upper().replace("Ñ", "N")
    t = unicodedata.normalize("NFD", t)
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    return "".join(ch for ch in t if "A" <= ch <= "Z")

# ---------------------------------------------------------------------------
# CONVERSIÓN A=1…Y=25, Z=0
# ---------------------------------------------------------------------------
def letra_a_num(c):
    n = ord(c) - 64  # A=1
    return 0 if n == 26 else n  # Z → 0

def num_a_letra(n):
    return chr(90) if n % 26 == 0 else chr((n % 26) + 64)

# ---------------------------------------------------------------------------
# Agrupar en bloques de 5
# ---------------------------------------------------------------------------
def agrupar_5(texto):
    return " ".join(texto[i:i+5] for i in range(0, len(texto), 5))

# ---------------------------------------------------------------------------
# Inverso modular (Euclides extendido)
# ---------------------------------------------------------------------------
def mod_inverse(a, m):
    a %= m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError(f"No existe inverso modular para {a} mod {m}")

# ---------------------------------------------------------------------------
# Matriz inversa modulo 26 con la convención A=1…Z=0
# ---------------------------------------------------------------------------
def matriz_inversa_mod26(M):
    det = int(round(np.linalg.det(M))) % 26
    inv_det = mod_inverse(det, 26)

    adj = np.array([[M[1,1], -M[0,1]],
                    [-M[1,0], M[0,0]]])

    return (inv_det * adj) % 26

# ---------------------------------------------------------------------------
# Cifrado Hill (A=1…Z=0)
# ---------------------------------------------------------------------------
def hill_cifrar(pt, M):
    if len(pt) % 2 != 0:
        pt += "X"

    out = []
    for i in range(0, len(pt), 2):
        v = np.array([[letra_a_num(pt[i])],
                      [letra_a_num(pt[i+1])]])

        c = np.dot(M, v) % 26
        out.append(num_a_letra(int(c[0,0])))
        out.append(num_a_letra(int(c[1,0])))

    return "".join(out)

# ---------------------------------------------------------------------------
# Descifrado Hill (A=1…Z=0)
# ---------------------------------------------------------------------------
def hill_descifrar(ct, M_inv):
    if len(ct) % 2 != 0:
        raise ValueError("Longitud del criptograma impar. No válido.")

    out = []
    for i in range(0, len(ct), 2):
        v = np.array([[letra_a_num(ct[i])],
                      [letra_a_num(ct[i+1])]])

        p = np.dot(M_inv, v) % 26
        out.append(num_a_letra(int(p[0,0])))
        out.append(num_a_letra(int(p[1,0])))

    return "".join(out)

# ---------------------------------------------------------------------------
# Ayuda extendida
# ---------------------------------------------------------------------------
def ayuda_extendida():
    print("""
hill.py — AYUDA EXTENDIDA
=========================

Convención usada por el libro:
    A=1, B=2, ..., Y=25, Z=0    (aritmética modular mod 26)

El texto se normaliza eliminando tildes, espacios y todo lo que no sea A–Z.

REQUISITOS DE LA MATRIZ
-----------------------
Debe ser 2×2 y su determinante debe tener inverso módulo 26.

USOS
----
Cifrar:
    python3 hill.py --cifrar --matriz "a b c d" archivo.txt

Descifrar:
    python3 hill.py --descifrar --matriz "a b c d" archivo.txt

Entrada por tubería:
    cat mensaje.txt | python3 hill.py --cifrar --matriz "3 3 2 5" -

Salida en bloques de 5:
    --grupo5

""")
    sys.exit(0)

# ---------------------------------------------------------------------------
def main():

    # Activar ayuda extendida
    if len(sys.argv) >= 2 and sys.argv[1].lower() in ("--h", "help", "-?"):
        ayuda_extendida()

    parser = argparse.ArgumentParser(
        description="Cifrado y descifrado Hill 2×2 con la convención A=1…Z=0."
    )

    modo = parser.add_mutually_exclusive_group(required=True)
    modo.add_argument("--cifrar", action="store_true")
    modo.add_argument("--descifrar", action="store_true")

    parser.add_argument("--matriz", required=True,
                        help='Matriz 2×2: "a b c d"')

    parser.add_argument("--grupo5", action="store_true",
                        help="Salida formateada en bloques de 5.")

    parser.add_argument("archivo", nargs="?", default="-",
                        help="Archivo de entrada o '-' para stdin.")

    args = parser.parse_args()

    # Leer matriz
    try:
        valores = list(map(int, args.matriz.split()))
        if len(valores) != 4:
            raise ValueError
        M = np.array(valores).reshape(2,2)
    except:
        print("Error: la matriz debe ser cuatro enteros separados por espacios.",
              file=sys.stderr)
        sys.exit(1)

    # Comprobar invertibilidad
    det = int(round(np.linalg.det(M))) % 26
    try:
        inv_det = mod_inverse(det, 26)
    except ValueError:
        print(f"La matriz no es invertible módulo 26 (det={det}).", file=sys.stderr)
        sys.exit(1)

    if args.descifrar:
        M_inv = matriz_inversa_mod26(M)

    # Leer entrada
    if args.archivo != "-":
        with open(args.archivo, "r", encoding="utf-8") as f:
            texto = f.read()
    else:
        texto = sys.stdin.read()

    texto = normalizar_AZ(texto)

    if args.cifrar:
        salida = hill_cifrar(texto, M)
    else:
        salida = hill_descifrar(texto, M_inv)

    if args.grupo5:
        salida = agrupar_5(salida)

    print(salida)

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
