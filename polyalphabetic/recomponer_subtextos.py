#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
PROGRAMA: recomponer_subtextos.py
AUTOR: David Arboledas Brihuega
HERRAMIENTA: Criptoanálisis clásico / Reconstrucción de criptogramas

DESCRIPCIÓN GENERAL:
    Reconstruye el criptograma original a partir de los subtextos generados por
    subtextos_cifrados.py (periodo N). El resultado final se muestra en pantalla
    y se guarda en un archivo de salida, formateado en grupos de 5 letras.

FUNCIONAMIENTO:
    1) Entrada: archivo con N subcriptogramas (uno por línea).
    2) Se intercalan sus letras para reconstruir el mensaje original.
    3) El mensaje reconstruido se formatea en grupos de 5.
    4) Se guarda en el archivo de salida y se muestra por pantalla.

USO:
    python3 recomponer_subtextos.py subtextos.txt salida.txt
    cat subtextos.txt | python3 recomponer_subtextos.py - salida.txt

ARGUMENTOS:
    archivo_subtextos    Archivo con los subcriptogramas o '-' para stdin.
    archivo_salida       Fichero donde se guardará el resultado final.
    -h, --help           Ayuda estándar.
    --h, help, -?        Alias adicionales de ayuda.

===============================================================================
"""

import sys
import argparse

# ---------------------------------------------------------------------------
# Ayuda extendida
# ---------------------------------------------------------------------------
def ayuda_extendida():
    print("""
recomponer_subtextos.py — Reconstrucción del criptograma original
(AYUDA EXTENDIDA)

USO:
    python3 recomponer_subtextos.py subtextos.txt salida.txt
    cat subtextos.txt | python3 recomponer_subtextos.py - salida.txt

DESCRIPCIÓN:
    • Lee subtextos (uno por línea).
    • Reconstruye el criptograma por intercalación columna a columna.
    • Formatea en grupos de 5 letras.
    • Guarda el resultado en archivo y lo muestra en pantalla.

ARGUMENTOS:
    archivo_subtextos    Archivo o '-' para stdin.
    archivo_salida       Archivo donde guardar el texto reconstruido.

""")
    sys.exit(0)

# ---------------------------------------------------------------------------
def recomponer(lines):
    """Intercala los subtextos para reconstruir el criptograma."""
    lines = [line.strip() for line in lines]
    if not lines:
        return ""

    max_len = max(len(line) for line in lines)
    n = len(lines)

    resultado = []
    for i in range(max_len):
        for j in range(n):
            if i < len(lines[j]):
                resultado.append(lines[j][i])

    return "".join(resultado)

# ---------------------------------------------------------------------------
def agrupar_5(texto: str):
    """Devuelve el texto en grupos de 5 letras."""
    return " ".join(texto[i:i+5] for i in range(0, len(texto), 5))

# ---------------------------------------------------------------------------
def main():

    # Aliases de ayuda extendida
    if len(sys.argv) >= 2 and sys.argv[1].lower() in ("--h", "help", "-?"):
        ayuda_extendida()

    parser = argparse.ArgumentParser(
        description="Reconstruye e imprime en grupos de 5 el criptograma original."
    )

    parser.add_argument(
        "archivo_subtextos",
        help="Archivo con los subtextos o '-' para stdin."
    )

    parser.add_argument(
        "archivo_salida",
        help="Archivo donde se guardará el resultado final."
    )

    args = parser.parse_args()

    # Leer líneas
    if args.archivo_subtextos != "-":
        try:
            with open(args.archivo_subtextos, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: archivo '{args.archivo_subtextos}' no encontrado.", file=sys.stderr)
            sys.exit(1)
    else:
        lines = sys.stdin.readlines()

    if len(lines) == 0:
        print("Entrada vacía.", file=sys.stderr)
        sys.exit(1)

    # Reconstrucción
    reconstruido = recomponer(lines)

    # Agrupar en bloques de 5
    reconstruido_5 = agrupar_5(reconstruido)

    # Guardar en archivo
    try:
        with open(args.archivo_salida, "w", encoding="utf-8") as f:
            f.write(reconstruido_5 + "\n")
    except Exception as e:
        print(f"No se pudo escribir en '{args.archivo_salida}': {e}", file=sys.stderr)
        sys.exit(1)

    # Mostrar por pantalla
    print("\nCRIPTOGRAMA RECONSTRUIDO (grupos de 5):\n")
    print(reconstruido_5)

    print(f"\nTexto guardado en: {args.archivo_salida}")

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
