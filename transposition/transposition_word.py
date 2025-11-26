#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
PROGRAMA: transposition_word.py
AUTOR: David Arboledas Brihuega (versión unificada para el libro)

HERRAMIENTA:
    Búsqueda de crib (palabra/frase conocida) en el texto llano producido por
    una TRANSPOSICIÓN COLUMNAR (inscripción por FILAS), probando múltiples
    variantes estructurales del método clásico:

        - Columnas irregulares: "natural" o "read"
        - Dirección de lectura de columna: arriba→abajo (“down”) o abajo→arriba (“up”)
        - Clave numérica 1-based o derivada de una palabra clave
        - Exploración de k columnas (kmin..kmax), exploración completa o muestreada
        - Validación por recifrado exacto

FUNCIONALIDADES AÑADIDAS (versión libro):
    ✔ Normalización estándar A–Z (tildes fuera, ñ→N)
    ✔ Entrada uniforme: archivo, --texto, o stdin (-)
    ✔ Salida técnica completa (Formato B)
    ✔ Opción --out archivo.txt
    ✔ Ayuda extendida (--h, help, -?)

USO BÁSICO:
    python3 transposition_word.py --texto "CT..." --crib PALABRA --kmin 5 --kmax 10
    python3 transposition_word.py --file criptograma.txt -w ATAQUE
    cat cripto.txt | python3 transposition_word.py -w ATAQUE -

Para conocer todas las opciones:
    python3 transposition_word.py --h
===============================================================================
"""

# --------------------------------------------------------------------------- #
# Importaciones                                                               #
# --------------------------------------------------------------------------- #
import argparse, sys, unicodedata, string, itertools, random
from typing import List, Tuple

# --------------------------------------------------------------------------- #
# Normalización estándar A–Z                                                  #
# --------------------------------------------------------------------------- #
def normalizar_AZ(s: str) -> str:
    """Convierte la cadena a A–Z mayúsculas, sin tildes, sin ñ y sin símbolos."""
    if not s:
        return ""
    s = unicodedata.normalize('NFD', s.upper())
    s = s.replace("Ñ", "N")
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return "".join(ch for ch in s if "A" <= ch <= "Z")

# --------------------------------------------------------------------------- #
# Ayuda extendida                                                             #
# --------------------------------------------------------------------------- #
def ayuda_extendida():
    print("""
AYUDA EXTENDIDA – transposition_word.py
---------------------------------------

Este programa intenta recuperar texto llano generado mediante TRANSPOSICIÓN
COLUMNAR (inscripción por FILAS). Para comprobar si un crib aparece en el claro,
explora distintas variantes de la técnica clásica:

VARIANTES ESTRUCTURALES:
  --long-rule natural    Columnas largas = C1..Cr
  --long-rule read       Columnas largas = primeras r del orden de lectura
  --col-dir down         Columnas leídas arriba→abajo
  --col-dir up           Columnas leídas abajo→arriba
  --keyword PALABRA      Convierte PARABRA→orden de lectura (1-based)
  --order 3,5,1,8,...    Orden de lectura explícito (1-based)

ENTRADA:
  --file archivo.txt     Lee el criptograma de un archivo UTF-8
  --texto "ABCDEF..."    Introducción directa por argumento
  -                      Lee desde STDIN

SALIDA:
  --out archivo.txt      Guarda todas las soluciones en Formato Técnico Completo

EJEMPLOS:
  python3 transposition_word.py --file cripto.txt -w ATAQUE --kmin 5 --kmax 10
  python3 transposition_word.py --texto "CT..." -w OPERACION --keyword DIAMANTE
  cat cripto.txt | python3 transposition_word.py -w ESTADOSUNIDOS -
""")
    sys.exit(0)

# --------------------------------------------------------------------------- #
# Palabra clave → orden de lectura                                            #
# --------------------------------------------------------------------------- #
def keyword_to_order_read(keyword: str) -> List[int]:
    w = normalizar_AZ(keyword)
    pares = sorted([(ch, i) for i, ch in enumerate(w)], key=lambda x: (x[0], x[1]))
    rank = [0]*len(w)
    r = 1
    for _, i in pares:
        rank[i] = r
        r += 1
    # orden 0-based
    return [i for _, i in sorted((rank[i], i) for i in range(len(w)))]

# --------------------------------------------------------------------------- #
# Geometría de columnas                                                       #
# --------------------------------------------------------------------------- #
def longitudes_columnas(N: int, ncols: int, order_read0: List[int], long_rule: str):
    q, r = divmod(N, ncols)
    longs = [q] * ncols
    if r > 0:
        if long_rule == "read":
            for j in range(r):
                longs[order_read0[j]] += 1
        else:
            for j in range(r):
                longs[j] += 1
    return longs

# --------------------------------------------------------------------------- #
# Descifrado y recifrado                                                      #
# --------------------------------------------------------------------------- #
def descifrar_por_orden(ciphertext: str,
                        read_order_1based: List[int],
                        long_rule: str = "natural",
                        col_direction: str = "down") -> str:

    C = normalizar_AZ(ciphertext)
    n = len(read_order_1based)
    order0 = [i-1 for i in read_order_1based]
    longs = longitudes_columnas(len(C), n, order0, long_rule)

    cols = [''] * n
    cursor = 0
    for idx in order0:
        L = longs[idx]
        cols[idx] = C[cursor:cursor+L]
        cursor += L

    if col_direction == "up":
        cols = [c[::-1] for c in cols]

    out = []
    max_rows = max(len(c) for c in cols)
    for r in range(max_rows):
        for c in range(n):
            if r < len(cols[c]):
                out.append(cols[c][r])
    return "".join(out)

def cifrar_por_orden_var(plaintext: str,
                         read_order_1based: List[int],
                         col_direction: str = "down") -> str:
    P = normalizar_AZ(plaintext)
    n = len(read_order_1based)
    order0 = [i-1 for i in read_order_1based]

    cols = [[] for _ in range(n)]
    idx = 0
    for ch in P:
        cols[idx].append(ch)
        idx = (idx + 1) % n

    if col_direction == "up":
        cols = [list(reversed(col)) for col in cols]

    out = []
    for j in order0:
        out.extend(cols[j])
    return "".join(out)

# --------------------------------------------------------------------------- #
# Búsqueda y verificación                                                     #
# --------------------------------------------------------------------------- #
def probar_perm(cipher: str,
                order1: List[int],
                crib: str,
                long_rule_opts: List[str],
                col_dir_opts: List[str],
                stopfirst: bool):

    soluciones = []
    for long_rule in long_rule_opts:
        for col_dir in col_dir_opts:
            plain = descifrar_por_orden(cipher, order1, long_rule, col_dir)
            if crib in plain:
                rec = cifrar_por_orden_var(plain, order1, col_dir)
                if rec == normalizar_AZ(cipher):
                    soluciones.append((order1[:], long_rule, col_dir, plain))
                    if stopfirst:
                        return soluciones
    return soluciones

def explorar_permutaciones(cipher: str,
                           k: int,
                           crib: str,
                           long_rules: List[str],
                           col_dirs: List[str],
                           stopfirst: bool,
                           maxperms: int):

    soluciones = []
    elems = list(range(1, k+1))

    total = 1
    for i in range(2, k+1):
        total *= i

    if total <= maxperms:
        perms = itertools.permutations(elems)
    else:
        random.seed(42)
        perms = (random.sample(elems, k) for _ in range(maxperms))

    for order1 in perms:
        sols = probar_perm(cipher, list(order1), crib, long_rules, col_dirs, stopfirst)
        if sols:
            soluciones.extend(sols)
            if stopfirst:
                break
    return soluciones

# --------------------------------------------------------------------------- #
# Guardado en formato técnico completo (Formato B)                            #
# --------------------------------------------------------------------------- #
def guardar_salida(outpath: str, cipher: str, soluciones):
    with open(outpath, "w", encoding="utf-8") as f:
        f.write("RESULTADOS – transposition_word.py\n")
        f.write("=================================\n\n")
        for i, (order1, long_rule, col_dir, plain) in enumerate(soluciones, 1):
            f.write(f"=== SOLUCIÓN {i} ===\n")
            f.write(f"CRIPTOGRAMA NORMALIZADO:\n{normalizar_AZ(cipher)}\n\n")
            f.write("CLARO RECONSTRUIDO:\n")
            f.write(f"{plain}\n\n")
            f.write("PARÁMETROS:\n")
            f.write(f"  k = {len(order1)}\n")
            f.write(f"  orden_lectura (1-based) = {order1}\n")
            f.write(f"  long_rule = {long_rule}\n")
            f.write(f"  col_dir   = {col_dir}\n\n")
            f.write("VERIFICACIÓN:\n")
            rec = cifrar_por_orden_var(plain, order1, col_dir)
            ok = "SÍ" if rec == normalizar_AZ(cipher) else "NO"
            f.write(f"  Recifrado correcto: {ok}\n")
            f.write("-"*70 + "\n\n")

# --------------------------------------------------------------------------- #
# CLI                                                                          #
# --------------------------------------------------------------------------- #
def main():

    # Ayuda extendida manual
    if len(sys.argv) >= 2 and sys.argv[1].lower() in ("--h", "-?", "help"):
        ayuda_extendida()

    ap = argparse.ArgumentParser(
        description="Crib-drag para transposición columnar (inscripción por FILAS)."
    )

    # Entrada del criptograma
    entrada = ap.add_mutually_exclusive_group(required=True)
    entrada.add_argument("--texto", help="Criptograma directo (se normaliza A–Z).")
    entrada.add_argument("--file", help="Archivo con el criptograma (UTF-8).")
    entrada.add_argument("stdin", nargs="?", default=None,
                         help="Use '-' para leer de STDIN.")

    # Crib obligatorio
    ap.add_argument("-w", "--crib", required=True, help="Palabra/frase conocida.")

    # Parámetros de búsqueda
    ap.add_argument("--kmin", type=int, default=2)
    ap.add_argument("--kmax", type=int, default=10)
    ap.add_argument("--stopfirst", action="store_true")
    ap.add_argument("--maxhits", type=int, default=50)
    ap.add_argument("--maxperms", type=int, default=200000)

    # Orden de lectura
    ap.add_argument("--order", help="Orden 1-based p.ej. '3,5,1,8,2,4,6,7'.")
    ap.add_argument("--keyword", help="Palabra clave → orden de lectura 1-based.")

    # Variantes estructurales
    ap.add_argument("--long-rule", choices=["natural", "read", "both"],
                    default="both")
    ap.add_argument("--col-dir", choices=["down", "up", "both"],
                    default="both")

    # Output a archivo
    ap.add_argument("--out", help="Guarda soluciones en archivo.")

    args = ap.parse_args()

    # --- Obtener criptograma ---
    if args.texto:
        C = normalizar_AZ(args.texto)
    elif args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                C = normalizar_AZ(f.read())
        except FileNotFoundError:
            sys.exit("Error: no se pudo abrir el archivo indicado.")
    else:
        if args.stdin == "-":
            C = normalizar_AZ(sys.stdin.read())
        else:
            sys.exit("Error: especifique --texto, --file o '-'.")
    
    W = normalizar_AZ(args.crib)

    if not C or not W:
        sys.exit("Error: criptograma o crib vacío tras normalización.")

    long_rules = ["natural", "read"] if args.long_rule == "both" else [args.long_rule]
    col_dirs   = ["down", "up"]      if args.col_dir   == "both"  else [args.col_dir]

    soluciones = []

    # Caso 1: orden explícito
    if args.order:
        order1 = [int(x.strip()) for x in args.order.split(",")]
        soluciones = probar_perm(C, order1, W, long_rules, col_dirs, args.stopfirst)

    # Caso 2: keyword → orden de lectura
    elif args.keyword:
        order0 = keyword_to_order_read(args.keyword)
        order1 = [i+1 for i in order0]
        soluciones = probar_perm(C, order1, W, long_rules, col_dirs, args.stopfirst)

    # Caso 3: búsqueda kmin..kmax
    else:
        for k in range(args.kmin, args.kmax + 1):
            sols = explorar_permutaciones(C, k, W, long_rules, col_dirs,
                                          args.stopfirst, args.maxperms)
            if sols:
                soluciones.extend(sols)
                if args.stopfirst:
                    break

    if not soluciones:
        print("SIN ÉXITO: ninguna variante produjo el crib y recifrado correcto.")
        sys.exit(2)

    # Mostrar en pantalla (primeros N resultados)
    print("=== SOLUCIONES ENCONTRADAS ===\n")
    for i, (order1, long_rule, col_dir, plain) in enumerate(soluciones[:args.maxhits], 1):
        print(f"[{i}] k={len(order1)}  orden={order1}  long_rule={long_rule}  col_dir={col_dir}")
        print(f"CT: {C}")
        print(f"PT: {plain}")
        print("-"*75)

    # Guardar si aplica
    if args.out:
        guardar_salida(args.out, C, soluciones)
        print(f"\n[INFO] Resultados guardados en '{args.out}'.")

# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    main()
