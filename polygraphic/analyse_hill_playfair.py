#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
PROGRAMA: analyse_hill_playfair.py
AUTOR: David Arboledas Brihuega
HERRAMIENTA: Clasificación estadística Hill 2×2 vs Playfair

DESCRIPCIÓN GENERAL:
    Este programa analiza un criptograma y estima si proviene de un cifrado
    Hill 2×2, de un Playfair ortodoxo o de un método distinto.

    El análisis es completamente estadístico y se basa en:
        1) Presencia de dígrafos idénticos (AA, BB…)  → incompatibles con Playfair.
        2) Índice de coincidencia monográfico (IC).
        3) χ² de uniformidad monográfica.
        4) χ² de independencia entre columnas de dígrafos (tabla 26×26).
        5) IC2 de dígrafos (Hill tiende a valores muy bajos).
        6) Simetría de columnas (delta-IC), muy característico del Hill.

CONVENCIÓN DEL LIBRO:
    Normalización a A–Z y sistema numérico A=1, …, Y=25, Z=0.
    Este sistema NO afecta al análisis (basado en frecuencias), pero se mantiene
    por coherencia editorial.

USO:
    python3 analyse_hill_playfair.py criptograma.txt
    python3 analyse_hill_playfair.py criptograma.txt --encoding ISO-8859-1
    python3 analyse_hill_playfair.py --help-ext

===============================================================================
"""

from __future__ import annotations
import argparse
import json
import sys
from collections import Counter
import unicodedata

import numpy as np
from scipy.stats import chisquare, chi2_contingency

ALFABETO = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# =========================================================================== #
# NORMALIZACIÓN                                                               #
# =========================================================================== #
def normalizar_AZ(texto: str) -> str:
    """Convierte a mayúsculas, elimina tildes y filtra solo A–Z."""
    t = texto.upper().replace("Ñ", "N")
    t = unicodedata.normalize("NFD", t)
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    return "".join(ch for ch in t if ch in ALFABETO)

# =========================================================================== #
# UTILIDADES                                                                  #
# =========================================================================== #
def separar_digrafos(texto: str) -> list[str]:
    """Divide el texto en dígrafos consecutivos; descarta la última letra si falta pareja."""
    if len(texto) % 2 == 1:
        texto = texto[:-1]
    return [texto[i:i+2] for i in range(0, len(texto), 2)]

def letra_a_num(c):
    """Convención del libro: A=1…Y=25, Z=0."""
    n = ord(c) - 64
    return 0 if n == 26 else n

# =========================================================================== #
# ESTADÍSTICOS                                                                 #
# =========================================================================== #
def indice_coincidencia(counter: Counter[str], N: int) -> float:
    return sum(n*(n-1) for n in counter.values())/(N*(N-1)) if N > 1 else 0.0

def indice_coincidencia_digrafos(counter: Counter[str], D: int) -> float:
    return sum(n*(n-1) for n in counter.values())/(D*(D-1)) if D > 1 else 0.0

def chi_uniforme(counter: Counter[str], N: int):
    esperado = N/26
    observados = [counter.get(c, 0) for c in ALFABETO]
    return chisquare(observados, f_exp=[esperado]*26)

def chi_independencia(digrafos: list[str]):
    """
    Prueba χ² de independencia entre la primera y la segunda letra del dígrafo,
    con Laplace smoothing para evitar celdas esperadas igual a cero.
    """
    tabla = np.zeros((26, 26), dtype=int)

    for dg in digrafos:
        i = ord(dg[0]) - 65
        j = ord(dg[1]) - 65
        tabla[i, j] += 1

    # Smoothing: evita ceros → evita el error de SciPy
    tabla_suavizada = tabla + 1

    chi2, p, *_ = chi2_contingency(tabla_suavizada, correction=False)
    return chi2, p

def digrafos_identicos(digrafos: list[str]) -> int:
    return sum(1 for dg in digrafos if dg[0] == dg[1])

def delta_ic_columnas(digrafos: list[str]) -> float:
    """Diferencia entre IC de primeras letras y IC de segundas."""
    col1 = [dg[0] for dg in digrafos]
    col2 = [dg[1] for dg in digrafos]
    c1 = Counter(col1)
    c2 = Counter(col2)
    ic1 = indice_coincidencia(c1, len(col1))
    ic2 = indice_coincidencia(c2, len(col2))
    return abs(ic1 - ic2)

# =========================================================================== #
# HEURÍSTICA                                                                   #
# =========================================================================== #
UMBRAL_IC = 0.045
UMBRAL_IC2 = 0.004
P_MIN_UNIFORME = 0.05
P_MIN_INDEP = 0.05
UMB_DELTA_IC = 0.007  # Más bajo → más compatible con Hill

def clasificar(res: dict) -> str:
    """
    Clasifica en cuatro categorías:

        • HILL_BIEN        → Cifrado Hill 2×2 con buena difusión.
        • HILL_DEBIL       → Cifrado Hill 2×2 válido pero con matriz pobre.
        • PLAYFAIR         → Compatible con Playfair.
        • NO_PLAYFAIR      → Playfair descartado (dígrafos idénticos).

    Criterios:
        - Hill bien distribuido:
            IC <= 0.045
            p_uniforme >= 0.05
            p_independencia >= 0.05
            IC2 <= 0.004

        - Hill débil:
            p_independencia >= 0.20   ← mantiene independencia de columnas
            dígrafos_idénticos >= 1   ← imposible en Playfair
            IC <= 0.060               ← IC elevado pero aún tipo Hill
            IC2 <= 0.015              ← IC2 alto pero compatible
    """

    uniforme = res["IC"] <= 0.045 and res["p_uniforme"] >= 0.05
    independiente = res["p_independencia"] >= 0.05
    ic2_bajo = res["IC2_digrafos"] <= 0.004

    # 1) Playfair imposible: dígrafos idénticos
    if res["digrafos_identicos"] > 0:

        # Caso Hill bien distribuido
        if uniforme and independiente and ic2_bajo:
            return "HILL_BIEN"

        # Caso Hill débil
        # (matriz pobre o irregular pero con independencia estructural)
        if (
            res["p_independencia"] >= 0.20 and
            res["IC"] <= 0.060 and
            res["IC2_digrafos"] <= 0.015
        ):
            return "HILL_DEBIL"

        # No Playfair, pero tampoco Hill reconocido
        return "NO_PLAYFAIR"

    # 2) Sin dígrafos idénticos → solo Playfair o Hill muy bueno
    if uniforme and independiente and ic2_bajo:
        return "HILL_BIEN"

    return "PLAYFAIR"




# =========================================================================== #
# AYUDA EXTENDIDA                                                              #
# =========================================================================== #
def ayuda_extendida():
    print("""
analyse_hill_playfair.py — AYUDA EXTENDIDA
==========================================

El programa determina si un criptograma es compatible con:

    • Hill 2×2
    • Playfair
    • Ninguno (INDETERMINADO)

CONVENCIÓN DEL LIBRO:
    Normalización A–Z y sistema A=1…Y=25, Z=0.

CRITERIOS:
    1. Dígrafos idénticos → descarta Playfair.
    2. IC monográfico bajo → compatible con Hill.
    3. χ² uniforme aceptable → compatible con Hill.
    4. Independencia 26×26 → característica de Hill.
    5. IC2 muy bajo → típico de Hill.
    6. Delta-IC entre columnas → Hill tiende a simetría.

USO:
    python3 analyse_hill_playfair.py criptograma.txt
    python3 analyse_hill_playfair.py criptograma.txt --encoding ISO-8859-1
    python3 analyse_hill_playfair.py --help-ext
""")
    sys.exit(0)

# =========================================================================== #
# MAIN                                                                         #
# =========================================================================== #
def main():

    # Atajos para ayuda extendida
    if len(sys.argv) >= 2 and sys.argv[1].lower() in ("--h", "help", "-?"):
        ayuda_extendida()

    parser = argparse.ArgumentParser(
        description="Clasifica un criptograma como Hill, Playfair o indeterminado."
    )
    parser.add_argument("archivo")
    parser.add_argument("--encoding", default="utf-8")
    parser.add_argument("--help-ext", "-H", action="store_true",
                        help="Mostrar ayuda extendida.")

    args = parser.parse_args()

    if args.help_ext:
        ayuda_extendida()

    try:
        with open(args.archivo, "r", encoding=args.encoding, errors="ignore") as f:
            raw = f.read()
    except FileNotFoundError:
        sys.exit("Error: no se pudo abrir el archivo.")

    texto = normalizar_AZ(raw)
    dig = separar_digrafos(texto)

    N = len(texto)
    D = len(dig)

    mon = Counter(texto)
    dmon = Counter(dig)

    IC = indice_coincidencia(mon, N)
    chi2, p_uni = chi_uniforme(mon, N)
    chi_i, p_i = chi_independencia(dig)
    ic2 = indice_coincidencia_digrafos(dmon, D)
    dobles = digrafos_identicos(dig)
    delta = delta_ic_columnas(dig)

    res = {
        "letras": N,
        "digrafos": D,
        "IC": IC,
        "chi2_uniforme": chi2,
        "p_uniforme": p_uni,
        "chi2_independencia": chi_i,
        "p_independencia": p_i,
        "IC2_digrafos": ic2,
        "digrafos_identicos": dobles,
        "delta_ic_columnas": delta
    }

    decision = clasificar(res)
    print(json.dumps(res, indent=2, ensure_ascii=False))

    print()
    if D < 200:
        print("⚠️  Advertencia: menos de 200 dígrafos → fiabilidad reducida.\n")

    if decision == "HILL_BIEN":
       print("Conclusión: ALTA probabilidad de Hill 2×2 bien construido (difusión correcta).")
    
    elif decision == "HILL_DEBIL":
       print("Conclusión: Probablemente cifrado Hill 2×2, pero con matriz débil o mal distribuida (IC y χ² no uniformes).")

    elif decision == "PLAYFAIR":
       print("Conclusión: Compatible con Playfair (sin dígrafos idénticos y patrones coherentes).")

    else:  # NO_PLAYFAIR
       print("Conclusión: NO es Playfair (dígrafos idénticos detectados), y tampoco coincide con un Hill 2×2 claro.")

# =========================================================================== #
if __name__ == "__main__":
    main()
