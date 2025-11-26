#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
PROGRAMA: freq_analysis.py
AUTOR: David Arboledas Brihuega
HERRAMIENTA: Análisis estadístico monográfico, digráfico y trigramático (A–Z)

FUNCIONALIDADES:
    - Entrada por argumento (-t), por fichero (-i) o por stdin.
    - Frecuencias monográficas.
    - Frecuencias de dígrafos.
    - Frecuencias de trígrafos.
    - Índice de coincidencia (IC).
    - χ² de monogramas frente a distribución esperada del español.
    - Comparación con tabla real de dígrafos (expected_digrams.csv).
    - Comparación con tabla real de trigramas (char_trigrams_es.tsv).
    - Salida opcional a fichero (-o).
    - Normalización completa A–Z.

USO:
    python freq_analysis.py -t "TEXTO"
    python freq_analysis.py -i mensaje.txt --mono --digrama
    python freq_analysis.py -i file.txt --chi
    python freq_analysis.py -i file.txt --full
    cat file.txt | python freq_analysis.py --mono
    python freq_analysis.py -i file.txt --trigramas char_trigrams_es.tsv
===============================================================================
"""

import sys
import argparse
import unicodedata
from collections import Counter
import csv

ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# ---------------------------------------------------------------------------
# Normalización
# ---------------------------------------------------------------------------
def normalizar(texto: str) -> str:
    t = unicodedata.normalize("NFD", texto.upper())
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    return "".join(ch for ch in t if ch in ALFABETO)


# ---------------------------------------------------------------------------
# Carga de datos externos
# ---------------------------------------------------------------------------
def cargar_digramas(path: str):
    tabla = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for row in csv.reader(f):
                if len(row) >= 2:
                    dg, val = row[0].strip(), float(row[1])
                    if len(dg) == 2:
                        tabla[dg] = val
        return tabla
    except Exception as e:
        print(f"[AVISO] No se pudo cargar {path}: {e}")
        return {}


def cargar_trigramas_tsv(path: str):
    tabla = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.rstrip().split("\t")
                if len(parts) >= 3 and len(parts[0]) == 3:
                    tri = parts[0]
                    logp = float(parts[2])
                    tabla[tri] = logp
        return tabla
    except Exception as e:
        print(f"[AVISO] No se pudo cargar trigramas {path}: {e}")
        return {}


# ---------------------------------------------------------------------------
# Estadísticos
# ---------------------------------------------------------------------------
def indice_coincidencia(texto: str):
    N = len(texto)
    if N < 2:
        return 0.0
    f = Counter(texto)
    num = sum(v*(v-1) for v in f.values())
    den = N*(N-1)
    return num/den


def chi_cuadrado(texto: str):
    """
    χ² frente a distribución aproximada de español.
    Fuente: frecuencias típicas del castellano moderno.
    """
    frec_esp = {
        'A':0.1253,'B':0.0142,'C':0.0468,'D':0.0586,'E':0.1368,'F':0.0069,
        'G':0.0101,'H':0.0070,'I':0.0625,'J':0.0044,'K':0.0002,'L':0.0497,
        'M':0.0315,'N':0.0671,'O':0.0868,'P':0.0251,'Q':0.0088,'R':0.0654,
        'S':0.0798,'T':0.0463,'U':0.0393,'V':0.0090,'W':0.0001,'X':0.0022,
        'Y':0.0090,'Z':0.0052
    }
    N = len(texto)
    if N == 0:
        return 0.0
    conteo = Counter(texto)
    chi = 0.0
    for letra in ALFABETO:
        O = conteo.get(letra, 0)
        E = N * frec_esp[letra]
        chi += (O - E)**2 / E
    return chi


# ---------------------------------------------------------------------------
# Generadores de n-gramas
# ---------------------------------------------------------------------------
def digramas(texto: str):
    return [texto[i:i+2] for i in range(len(texto)-1)]


def trigramas(texto: str):
    return [texto[i:i+3] for i in range(len(texto)-2)]


# ---------------------------------------------------------------------------
# Impresión de frecuencias
# ---------------------------------------------------------------------------
def imprimir_frecuencias(contador: Counter, titulo: str, N: int):
    print(f"\n=== {titulo} ===")
    for elem, f in sorted(contador.items(), key=lambda x: (-x[1], x[0])):
        pct = 100*f/N
        print(f"{elem}: {f:>6} ({pct:5.2f}%)")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Análisis estadístico monográfico/digráfico/trigráfico A–Z")
    parser.add_argument("-t", "--texto", help="Texto literal a analizar.")
    parser.add_argument("-i", "--input", help="Archivo de entrada.")
    parser.add_argument("-o", "--output", help="Archivo de salida.")

    parser.add_argument("--mono", action="store_true", help="Frecuencias de letras.")
    parser.add_argument("--di", action="store_true", help="Frecuencias de dígrafos.")
    parser.add_argument("--tri", action="store_true", help="Frecuencias de trígrafos.")
    parser.add_argument("--chi", action="store_true", help="Chi-cuadrado monográfico.")
    parser.add_argument("--ic", action="store_true", help="Índice de coincidencia.")
    parser.add_argument("--full", action="store_true", help="Realizar TODOS los análisis.")

    parser.add_argument("--expected-di", help="CSV con frecuencias esperadas de dígrafos.")
    parser.add_argument("--trigramas", help="TSV con log-probabilidades de trigramas.")

    args = parser.parse_args()

    # ------------------- Obtener texto -------------------
    if args.texto:
        bruto = args.texto
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                bruto = f.read()
        except FileNotFoundError:
            sys.exit("ERROR: No se pudo abrir el archivo de entrada.")
    else:
        bruto = sys.stdin.read()

    texto = normalizar(bruto)
    N = len(texto)
    if N == 0:
        sys.exit("ERROR: No hay texto útil tras la normalización.")

    # ------------------- Capturar salida -------------------
    salida = []
    out = salida.append

    # ------------------- Monogramas -------------------
    if args.mono or args.full:
        freqs = Counter(texto)
        out("=== FRECUENCIAS MONOGRÁFICAS ===")
        for l, f in sorted(freqs.items(), key=lambda x: (-x[1], x[0])):
            out(f"{l}: {f}")

    # ------------------- Dígrafos -------------------
    if args.di or args.full:
        digs = digramas(texto)
        c = Counter(digs)
        out("\n=== FRECUENCIAS DE DÍGRAFOS ===")
        for dg, f in sorted(c.items(), key=lambda x: (-x[1], x[0])):
            out(f"{dg}: {f}")

        if args.expected_di:
            tabla = cargar_digramas(args.expected_di)
            out("\n--- Comparación con dígrafos esperados ---")
            for dg, f in sorted(c.items(), key=lambda x: (-x[1], x[0])):
                esp = tabla.get(dg, None)
                if esp is None:
                    out(f"{dg}: {f}  (sin referencia)")
                else:
                    out(f"{dg}: {f}  | esperado={esp}")

    # ------------------- Trigramas -------------------
    if args.tri or args.full:
        trs = trigramas(texto)
        c = Counter(trs)
        out("\n=== FRECUENCIAS DE TRÍGRAFOS ===")
        for tr, f in sorted(c.items(), key=lambda x: (-x[1], x[0])):
            out(f"{tr}: {f}")

        if args.trigramas:
            tabla = cargar_trigramas_tsv(args.trigramas)
            out("\n--- Log-probabilidades reales ---")
            for tr, f in sorted(c.items(), key=lambda x: (-x[1], x[0])):
                lp = tabla.get(tr, None)
                if lp is None:
                    out(f"{tr}: {f}  (sin referencia)")
                else:
                    out(f"{tr}: {f}  | logp={lp}")

    # ------------------- IC -------------------
    if args.ic or args.full:
        ic = indice_coincidencia(texto)
        out(f"\nIC = {ic:.5f}")

    # ------------------- χ² -------------------
    if args.chi or args.full:
        chi = chi_cuadrado(texto)
        out(f"\nChi-cuadrado (español) = {chi:.3f}")

    # ------------------- Imprimir o guardar -------------------
    resultado = "\n".join(salida)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(resultado)
        print(f"[OK] Resultados guardados en '{args.output}'")
    else:
        print(resultado)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
