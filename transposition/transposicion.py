#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
PROGRAMA: transposicion.py
AUTOR: David Arboledas Brihuega
HERRAMIENTA: Cifrado y descifrado por transposición columnar simple

DESCRIPCIÓN GENERAL:
    Este programa cifra o descifra mensajes mediante la transposición columnar
    clásica utilizando una clave alfabética. Toda entrada se normaliza a A–Z.

FUNCIONAMIENTO:
    • La clave alfabética se convierte en una clave numérica (A=1).
    • En cifrado, el texto se normaliza, se coloca en una matriz por filas
      y se leen las columnas en orden ascendente según la clave numérica.
    • En descifrado, se reconstruye la matriz columna por columna.
    • Puede trabajar con archivo o con entrada estándar (stdin).
    • Puede agrupar la salida en bloques de cinco letras (--grupo5).

USO:
    python3 columnar.py --cifrar --clave CLAVE archivo.txt
    python3 columnar.py --descifrar --clave CLAVE archivo.txt
    cat archivo.txt | python3 columnar.py --cifrar --clave CLAVE -

OPCIONES:
    --cifrar / --descifrar     Modo de operación.
    -k, --clave CLAVE          Clave alfabética (se normaliza A–Z).
    --grupo5                   Muestra la salida en bloques de 5 letras.
    archivo                    Archivo de entrada o '-' para stdin.
    --h, help, -?              Muestra ayuda extendida.

===============================================================================
"""

import sys
import argparse
import unicodedata


# ---------------------------------------------------------------------------
# Normalización universal A–Z (A=1 en todas las operaciones internas)
# ---------------------------------------------------------------------------
def normalizar_AZ(texto: str) -> str:
    """Convierte a mayúsculas, elimina tildes, Ñ→N y filtra solo A–Z."""
    t = texto.upper().replace("Ñ", "N")
    t = unicodedata.normalize("NFD", t)
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    return "".join(ch for ch in t if "A" <= ch <= "Z")


# ---------------------------------------------------------------------------
# Clave alfabética → clave numérica
# ---------------------------------------------------------------------------
def derivar_clave_numerica(clave: str) -> list[int]:
    """
    Convierte una clave alfabética en clave numérica según orden alfabético.
    Si hay letras repetidas, el orden se mantiene de izquierda a derecha.
    """
    clave = normalizar_AZ(clave)
    ordenados = sorted([(letra, idx) for idx, letra in enumerate(clave)])
    asignacion = {}
    valor = 1
    for letra, idx in ordenados:
        asignacion[(letra, idx)] = valor
        valor += 1
    return [asignacion[(letra, idx)] for idx, letra in enumerate(clave)]


# ---------------------------------------------------------------------------
# Utilidad: agrupar en bloques de 5 letras
# ---------------------------------------------------------------------------
def agrupar_5(t: str) -> str:
    return " ".join(t[i:i+5] for i in range(0, len(t), 5))


# ---------------------------------------------------------------------------
# CIFRADO COLUMNAR
# ---------------------------------------------------------------------------
def cifrar_columnar(texto: str, clave_num: list[int]) -> str:
    columnas = len(clave_num)
    filas = -(-len(texto) // columnas)  # ceil

    # Relleno con X si es necesario
    texto += "X" * (filas * columnas - len(texto))

    # Construcción de la matriz
    matriz = [list(texto[i:i+columnas]) for i in range(0, len(texto), columnas)]

    # Orden ascendente según clave numérica
    orden = sorted(range(columnas), key=lambda k: clave_num[k])

    # Lectura columna-columna
    resultado = "".join(matriz[f][c] for c in orden for f in range(filas))
    return resultado


# ---------------------------------------------------------------------------
# DESCIFRADO COLUMNAR
# ---------------------------------------------------------------------------
def descifrar_columnar(texto_cifrado: str, clave_num: list[int]) -> str:
    texto_cifrado = normalizar_AZ(texto_cifrado)
    columnas = len(clave_num)
    filas = len(texto_cifrado) // columnas

    orden = sorted(range(columnas), key=lambda k: clave_num[k])

    # Extraer trozos por columna
    col_len = filas
    contenido = {}
    idx = 0
    for col in orden:
        contenido[col] = texto_cifrado[idx:idx+col_len]
        idx += col_len

    # Reconstrucción de la matriz
    matriz = [[""] * columnas for _ in range(filas)]
    for col in range(columnas):
        for f in range(filas):
            matriz[f][col] = contenido[col][f]

    # Lectura por filas
    return "".join("".join(fila) for fila in matriz)


# ---------------------------------------------------------------------------
# Ayuda extendida
# ---------------------------------------------------------------------------
def ayuda_extendida():
    print("""
columnar.py — AYUDA EXTENDIDA

USO:
    python3 columnar.py --cifrar   --clave CLAVE archivo.txt
    python3 columnar.py --descifrar --clave CLAVE archivo.txt
    cat archivo.txt | python3 columnar.py --cifrar --clave CLAVE --

DETALLES:
    • La clave alfabética se transforma en clave numérica (A=1...).
    • Toda entrada se normaliza a A–Z.
    • El cifrado rellena con X si la matriz no es exacta.
    • El descifrado reconstruye la matriz por columnas.
    • --grupo5 muestra la salida en grupos de cinco letras.

EJEMPLO:
    Clave: ROMA  → clave numérica = 3 2 4 1
""")
    sys.exit(0)


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------
def main():
    # Atajos manuales para ayuda extendida
    if len(sys.argv) >= 2 and sys.argv[1].lower() in ("--h", "help", "-?"):
        ayuda_extendida()

    parser = argparse.ArgumentParser(
        description="Cifra o descifra mediante transposición columnar (A–Z)."
    )

    modo = parser.add_mutually_exclusive_group(required=True)
    modo.add_argument("--cifrar", action="store_true")
    modo.add_argument("--descifrar", action="store_true")

    parser.add_argument("-k", "--clave", required=True,
                        help="Clave alfabética (se normaliza A–Z).")

    parser.add_argument("--grupo5", action="store_true",
                        help="Salida en bloques de 5 letras.")

    parser.add_argument("archivo", nargs="?", default="-",
                        help="Archivo de entrada o '-' para stdin.")

    args = parser.parse_args()

    # Leer entrada
    if args.archivo != "-":
        try:
            with open(args.archivo, "r", encoding="utf-8") as f:
                bruto = f.read()
        except FileNotFoundError:
            print(f"Error: archivo '{args.archivo}' no encontrado.", file=sys.stderr)
            sys.exit(1)
    else:
        bruto = sys.stdin.read()

    clave_num = derivar_clave_numerica(args.clave)

    texto = normalizar_AZ(bruto)

    if args.cifrar:
        resultado = cifrar_columnar(texto, clave_num)
    else:
        resultado = descifrar_columnar(texto, clave_num)

    if args.grupo5:
        resultado = agrupar_5(resultado)

    print(resultado)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
