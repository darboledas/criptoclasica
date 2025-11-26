#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
PROGRAMA: IC.py
AUTOR: David Arboledas Brihuega
HERRAMIENTA: Criptoanálisis clásico / Índice de Coincidencia (IC)

DESCRIPCIÓN GENERAL:
    Este programa calcula el ÍNDICE DE COINCIDENCIA (IC) de un texto, tras
    normalizarlo al alfabeto inglés A–Z. El IC permite evaluar si un texto
    presenta la distribución típica de un idioma natural o la de un texto
    cercano al azar, siendo una herramienta fundamental para analizar cifrados
    por sustitución monoalfabética y polialfabética.

FUNCIONAMIENTO:
    1) Entrada mediante archivo, cadena directa o stdin interactivo.
    2) Normalización:
         - Elimina todo carácter no alfabético.
         - Convierte a mayúsculas.
         - Filtra solo A–Z.
    3) Cálculo:
         IC = sum(fi * (fi - 1)) / (n * (n - 1))
    4) Opcionalmente muestra las frecuencias individuales A–Z.

USO:
    python IC.py -t "Attack at dawn!"
    python IC.py -f texto.txt
    python IC.py -t "mensaje" --show-freq
    python IC.py -                      (stdin interactivo)

ARGUMENTOS:
    -t, --text "..."   Texto directo.
    -f, --file archivo Texto desde archivo.
    --show-freq        Muestra frecuencias detalladas.
    -h, --help         Ayuda estándar.
    --h, help, -?      Alias adicionales de ayuda extendida.

REFERENCIAS:
    • IC (español) ≈ 0.075
    • IC (texto completamente aleatorio) ≈ 0.0385
===============================================================================
"""

import sys
import argparse
import re
from collections import Counter

AZ_REGEX = re.compile(r"[^A-Za-z]")  # todo lo que NO es A–Z/a–z

# ---------------------------------------------------------------------------
# Normalización A–Z
# ---------------------------------------------------------------------------
def normalizar_AZ(texto: str) -> str:
    """Elimina todo lo que no sea alfabético y convierte a MAYÚSCULAS (A–Z)."""
    return AZ_REGEX.sub("", texto).upper()

# ---------------------------------------------------------------------------
# Índice de Coincidencia
# ---------------------------------------------------------------------------
def indice_coincidencia(texto: str):
    """
    Devuelve:
        ic (float)
        n (longitud del texto)
        freqs (diccionario A–Z)
    """
    n = len(texto)
    freqs = Counter(texto)

    if n < 2:
        return float("nan"), n, dict(freqs)

    num = sum(fi * (fi - 1) for fi in freqs.values())
    den = n * (n - 1)
    ic = num / den
    return ic, n, dict(freqs)

# ---------------------------------------------------------------------------
# Ayuda extendida
# ---------------------------------------------------------------------------
def ayuda_extendida():
    print("""
IC.py — Cálculo del Índice de Coincidencia (AYUDA EXTENDIDA)

USO:
    python3 IC.py -t "Attack at dawn!"
    python3 IC.py -f texto.txt
    python3 IC.py - --show-freq

FUNCIONAMIENTO:
    1) Limpia texto: solo A–Z (mayúsculas).
    2) Calcula:
         IC = sum(fi*(fi-1)) / (n*(n-1))
    3) Permite mostrar frecuencias A–Z.

ARGUMENTOS:
    -t, --text        Texto directo.
    -f, --file        Archivo de entrada.
    --show-freq       Muestra frecuencias del texto limpio.
    -h, --help        Ayuda estándar.
    --h, help, -?     Alias adicionales de ayuda.
""")
    sys.exit(0)

# ---------------------------------------------------------------------------
def main():

    # Aliases manuales de ayuda extendida
    if len(sys.argv) >= 2 and sys.argv[1].lower() in ("--h", "help", "-?"):
        ayuda_extendida()

    parser = argparse.ArgumentParser(
        description="Calcula el Índice de Coincidencia (IC) para texto A–Z limpio."
    )

    g = parser.add_mutually_exclusive_group()
    g.add_argument("-t", "--text", type=str, help="Texto directo de entrada.")
    g.add_argument("-f", "--file", type=str, help="Archivo de texto.")

    parser.add_argument(
        "--show-freq",
        action="store_true",
        help="Muestra frecuencias A–Z del texto ya normalizado."
    )

    args = parser.parse_args()

    # Lectura de entrada
    if args.text is not None:
        bruto = args.text
    elif args.file is not None:
        try:
            with open(args.file, "r", encoding="utf-8") as fh:
                bruto = fh.read()
        except FileNotFoundError:
            print(f"Error: archivo '{args.file}' no encontrado.", file=sys.stderr)
            sys.exit(1)
    else:
        bruto = input("Introduce el mensaje: ")

    # Normalización
    limpio = normalizar_AZ(bruto)
    ic, n, freqs = indice_coincidencia(limpio)

    print("\n=== RESULTADOS IC ===")
    print(f"Longitud original: {len(bruto)} caracteres")
    print(f"Longitud limpia  : {n} (solo A–Z)")

    if n > 0:
        preview = limpio[:80] + ("..." if n > 80 else "")
        print(f"Texto limpio (preview): {preview}")
    else:
        print("Texto limpio vacío tras el filtrado.")

    if n < 2:
        print("\nIC: no definido (n < 2).")
        return

    print(f"\nÍndice de Coincidencia (IC): {ic:.6f}")
    print("Referencia: español ≈ 0.075 | aleatorio ≈ 0.0385")

    if args.show_freq:
        print("\nFrecuencias del texto limpio (orden descendente):")
        for letra, freq in sorted(freqs.items(), key=lambda x: x[1], reverse=True):
            print(f"{letra}: {freq}")

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
