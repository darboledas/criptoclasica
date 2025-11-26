#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_transpo.py — Descifrado automatizado (heurístico) de transposiciones columnarias
-------------------------------------------------------------------------------

Este programa intenta recuperar el orden de lectura de las columnas en una
transposición columnar con inscripción por FILAS, utilizando búsqueda heurística
(beam search) guiada por puntuación de trigramas del castellano.

FUNCIONALIDADES PRINCIPALES
---------------------------
• Descifrado directo si se proporciona:
    --order 5,7,4,3,2,6,1
    --keyword PALABRA

• Descifrado heurístico (beam search) si no se proporcionan claves:
    – Rango nmin..nmax
    – Anchura del haz (beam)
    – Número de hipótesis finales (kbest)

• Entrada desde archivo o desde stdin
• Salida por pantalla y opcionalmente a archivo (--out)
• Carga opcional de trigramas reales TSV

AYUDA EXTENDIDA:
    python auto_transpo.py --h
"""

import sys, math, unicodedata, string, argparse, re
from collections import defaultdict

# ---------------------------------------------------------------------------
# Normalización A–Z
# ---------------------------------------------------------------------------

def normalizar(texto: str) -> str:
    """Convierte el texto a A–Z: elimina tildes, ñ, signos y pasa a mayúsculas."""
    t = unicodedata.normalize("NFD", texto)
    t = ''.join(ch for ch in t if unicodedata.category(ch) != "Mn")
    t = t.upper()
    return ''.join(ch for ch in t if ch in string.ascii_uppercase)

def leer_entrada(ruta: str) -> str:
    """Lee desde archivo o stdin ('-')."""
    if ruta == "-":
        return sys.stdin.read()
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        sys.exit(f"Error: no se pudo abrir '{ruta}'.")

def escribir_salida(texto: str, ruta: str | None):
    """Escribe la salida en pantalla y opcionalmente en archivo (--out)."""
    print(texto)
    if ruta:
        try:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(texto + "\n")
        except Exception as e:
            print(f"[AVISO] No se pudo escribir en '{ruta}': {e}", file=sys.stderr)

def group5(s: str) -> str:
    return ' '.join(s[i:i+5] for i in range(0, len(s), 5))

# ---------------------------------------------------------------------------
# Trigramas (tabla probabilística)
# ---------------------------------------------------------------------------

def cargar_trigramas(path: str | None):
    """
    Carga una tabla TSV con:
        TRIGRAMA<TAB>count<TAB>logp
    Si falla, se usa un fallback básico.
    """
    tabla = {}

    if path:
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.rstrip().split("\t")
                    if len(parts) >= 3 and len(parts[0]) == 3:
                        tri, _, lp = parts[0], parts[1], float(parts[2])
                        tabla[tri] = lp
        except Exception as e:
            print(f"[AVISO] No se pudo cargar la tabla '{path}': {e}", file=sys.stderr)

    if tabla:
        default_lp = min(tabla.values()) - 2.0
        return tabla, default_lp

    # Fallback simplificado
    base = -9.0
    comunes = ["QUE","ENT","LOS","LAS","EST","NTE","CON","PAR","ARA","ION","ADO"]
    for a in string.ascii_uppercase:
        for b in string.ascii_uppercase:
            for c in string.ascii_uppercase:
                tabla[a+b+c] = base
    for tri in comunes:
        tabla[tri] = -2.5
    return tabla, -10.5

TRI, TRI_DEF = cargar_trigramas(None)

def score_text(s: str) -> float:
    if len(s) < 3:
        return -1e9
    total = 0.0
    for i in range(len(s) - 2):
        tri = s[i:i+3]
        total += TRI.get(tri, TRI_DEF)
    return total

# ---------------------------------------------------------------------------
# Utilidades de transposición
# ---------------------------------------------------------------------------

def longitudes_columnas(N: int, n: int):
    q, r = divmod(N, n)
    return [q + (1 if i < r else 0) for i in range(n)]

def asignar_columnas(cipher: str, n: int, orden_0: list[int]):
    longs = longitudes_columnas(len(cipher), n)
    cols = [''] * n
    cursor = 0
    for idx in orden_0:
        L = longs[idx]
        cols[idx] = cipher[cursor:cursor+L]
        cursor += L
    return cols

def leer_por_filas(cols: list[str]) -> str:
    out = []
    maxlen = max(len(c) for c in cols)
    for r in range(maxlen):
        for c in range(len(cols)):
            if r < len(cols[c]):
                out.append(cols[c][r])
    return ''.join(out)

# ---------------------------------------------------------------------------
# Beam Search Heurístico
# ---------------------------------------------------------------------------

def beam_search(cipher: str, n: int, beam: int, topk: int):
    N = len(cipher)
    longs = longitudes_columnas(N, n)

    estados = [ ([], ['']*n, 0, 0.0) ]
    finales = []

    for paso in range(n):
        nuevos = []
        for orden, cols, cursor, punt in estados:
            restantes = [i for i in range(n) if i not in orden]
            for idx in restantes:
                L = longs[idx]
                seg = cipher[cursor:cursor+L]

                cols2 = cols.copy()
                cols2[idx] = seg
                orden2 = orden + [idx]

                # evaluación parcial
                min_rows = min(len(cols2[i]) for i in orden2)
                parcial = ''.join(
                    cols2[c][r]
                    for r in range(min_rows)
                    for c in range(n)
                )
                pscore = score_text(parcial) / max(1, len(parcial))

                nuevos.append((orden2, cols2, cursor+L, punt + pscore))

        nuevos.sort(key=lambda x: x[3], reverse=True)
        estados = nuevos[:beam]

    for orden, cols, _, punt in estados:
        plain = leer_por_filas(cols)
        finales.append((score_text(plain)/len(plain), orden, plain))

    finales.sort(key=lambda x: x[0], reverse=True)
    return finales[:topk]

def search_n(cipher: str, nmin: int, nmax: int, beam: int, kbest: int):
    candidatos = []
    for n in range(nmin, nmax+1):
        if n < 2:
            continue
        longs = longitudes_columnas(len(cipher), n)
        if min(longs) < 3:
            continue
        for sc, orden, plain in beam_search(cipher, n, beam, kbest):
            candidatos.append((sc, n, orden, plain))
    candidatos.sort(key=lambda x: x[0], reverse=True)
    return candidatos[:kbest]

# ---------------------------------------------------------------------------
# Palabra clave → orden lectura
# ---------------------------------------------------------------------------

def keyword_to_order_read(keyword: str):
    w = normalizar(keyword)
    pares = sorted((ch, i) for i, ch in enumerate(w))
    rank = [0]*len(w)
    r = 1
    for _, i in pares:
        rank[i] = r
        r += 1
    return [i for _, i in sorted((rank[i], i) for i in range(len(w)))]

# ---------------------------------------------------------------------------
# Ayuda extendida
# ---------------------------------------------------------------------------

def ayuda_extendida():
    print("""
AYUDA EXTENDIDA – auto_transpo.py

Ejemplos de uso:

1) Búsqueda heurística:
    python auto_transpo.py texto.txt --nmin 6 --nmax 10 --beam 400 --kbest 10

2) Clave conocida (orden de lectura 1-based):
    python auto_transpo.py texto.txt --order 5,7,4,3,2,6,1

3) Palabra-clave:
    python auto_transpo.py texto.txt --keyword TOLKAPI

4) Con tabla real de trigramas:
    python auto_transpo.py texto.txt --trigrams trigramas_es.tsv

Salida:
    Siempre se muestra por pantalla y opcionalmente se escribe con:
        --out resultado.txt
""")
    sys.exit(0)

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():

    # Trampa para ayuda extendida
    if len(sys.argv) >= 2 and sys.argv[1].lower() in ("--h", "-?", "help"):
        ayuda_extendida()

    ap = argparse.ArgumentParser(
        description="Descifrado heurístico y asistido de transposición columnar."
    )
    ap.add_argument("archivo", help="Archivo de entrada o '-' para stdin.")
    ap.add_argument("--nmin", type=int, default=4)
    ap.add_argument("--nmax", type=int, default=10)
    ap.add_argument("--beam", type=int, default=200)
    ap.add_argument("--kbest", type=int, default=5)
    ap.add_argument("--order", type=str, help="Orden 1-based: '5,7,4,3,2,6,1'")
    ap.add_argument("--keyword", type=str, help="Palabra clave para generar orden.")
    ap.add_argument("--trigrams", type=str, help="Archivo TSV con trigramas.")
    ap.add_argument("--out", type=str, help="Archivo donde escribir la salida.")
    args = ap.parse_args()

    # cargar tabla de trigramas real si procede
    global TRI, TRI_DEF
    if args.trigrams:
        TRI, TRI_DEF = cargar_trigramas(args.trigrams)

    texto_bruto = leer_entrada(args.archivo)
    cipher = normalizar(texto_bruto)

    if not cipher:
        sys.exit("Error: criptograma vacío tras normalizar.")

    salida = []

    # Descifrado directo con orden explícito
    if args.order:
        orden = [int(x.strip()) - 1 for x in args.order.split(",")]
        cols = asignar_columnas(cipher, len(orden), orden)
        plain = leer_por_filas(cols)
        salida.append("CT: " + group5(cipher))
        salida.append(f"Orden (1-based): {[o+1 for o in orden]}")
        salida.append("PT: " + group5(plain))
        escribir_salida("\n".join(salida), args.out)
        return

    # Descifrado directo por palabra clave
    if args.keyword:
        orden = keyword_to_order_read(args.keyword)
        cols = asignar_columnas(cipher, len(orden), orden)
        plain = leer_por_filas(cols)
        salida.append("CT: " + group5(cipher))
        salida.append(f"Orden (1-based): {[o+1 for o in orden]}")
        salida.append("PT: " + group5(plain))
        escribir_salida("\n".join(salida), args.out)
        return

    # Búsqueda heurística
    resultados = search_n(cipher, args.nmin, args.nmax, args.beam, args.kbest)

    if not resultados:
        escribir_salida("No se encontraron hipótesis plausibles.", args.out)
        return

    salida.append("=== Hipótesis plausibles (mejor primero) ===")
    for i, (sc, n, orden, plain) in enumerate(resultados, 1):
        salida.append(f"[{i}] n={n}  orden(1-based)={[o+1 for o in orden]}  score={sc:.4f}")
        salida.append("CT: " + group5(cipher))
        salida.append("PT: " + group5(plain))
        salida.append("-" * 70)

    escribir_salida("\n".join(salida), args.out)

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
