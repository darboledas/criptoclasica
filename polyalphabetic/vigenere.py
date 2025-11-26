#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ============================================================================
# PROGRAMA: Vigenere.py  (versión ampliada con CLI)
# AUTOR: David Arboledas Brihuega
# DESCRIPCIÓN:
#     Mantiene el funcionamiento original (menú interactivo) pero añade:
#         - cifrado/descifrado por línea de comandos
#         - lectura desde archivo o stdin
#         - salida opcional a archivo
#         - generación de tabla por consola
#         - agrupación opcional en bloques de 5 letras
#         - ayuda extendida (--h, help, -?)
#
#     La lógica histórica y la tabla recíproca quedan intactas.
# ============================================================================

import sys
import argparse

# ---------------------------------------------------------------------------

ALFABETO = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
NUMERO = len(ALFABETO)
COL_CLAVE = list(ALFABETO)

global alfabeto
alfabeto = [''] * NUMERO

# ---------------------------------------------------------------------------
# UTILIDADES ORIGINALES (sin tocar)
# ---------------------------------------------------------------------------

def quitar_duplicados(clave):
    nueva = ""
    for c in clave:
        if c not in nueva:
            nueva += c
    return nueva

def alfabeto_inicial(clave):
    nueva = ""
    clave = clave.upper()
    resto = list(ALFABETO)
    for c in clave:
        if c not in nueva:
            nueva += c
            resto.remove(c)
    return nueva + "".join(resto)

def verificar_clave(clave):
    if clave.strip() == "":
        return ALFABETO
    return alfabeto_inicial(quitar_duplicados(clave))

def generar_tabla(inicio, mostrar=False):
    global alfabeto
    alfabeto[0] = inicio
    for i in range(1, NUMERO):
        fila = ""
        for j in range(NUMERO):
            fila += alfabeto[i-1][(j+1) % NUMERO]
        alfabeto[i] = fila
    if mostrar:
        mostrar_tabla(alfabeto)
    return alfabeto

def mostrar_tabla(alf):
    print('  ' + " ".join(list(ALFABETO)).lower())
    for i in range(NUMERO):
        print(COL_CLAVE[i], end=" ")
        print(" ".join(alf[i]))

def cifrar_descifrar(clave, mensaje, modo):
    clave = ''.join(clave.split()).upper()
    salida = ""
    idx = 0
    for s in mensaje:
        pos = ALFABETO.find(s)
        if pos != -1:
            n = ALFABETO.find(clave[idx])
            if modo == "cifrar":
                salida += alfabeto[n][pos]
            else:
                p = alfabeto[n].find(s)
                salida += ALFABETO[p]
            idx = (idx + 1) % len(clave)
        else:
            salida += s
    return salida

def cifrarMensaje(clave, mensaje):
    return cifrar_descifrar(clave, mensaje.upper(), "cifrar").upper()

def descifrarMensaje(clave, mensaje):
    return cifrar_descifrar(clave, mensaje.upper(), "descifrar").lower()

# ---------------------------------------------------------------------------
# FUNCIONALIDADES NUEVAS (CLI)
# ---------------------------------------------------------------------------

def agrupar_5(txt):
    return " ".join(txt[i:i+5] for i in range(0, len(txt), 5))

def ayuda_extendida():
    print("""
Uso avanzado:
    vigenere.py --cifrar   -k CLAVE --tabla-clave PASS   [-i archivo] [-o archivo] [--grupo5]
    vigenere.py --descifrar -k CLAVE --tabla-clave PASS  [-i archivo] [-o archivo]
    vigenere.py --tabla --tabla-clave PASS

Ejemplos:
    python vigenere.py --tabla --tabla-clave BOLA
    python vigenere.py --cifrar   -k CASO --tabla-clave BOLA -i mensaje.txt -o salida.txt
    python vigenere.py --descifrar -k CASO --tabla-clave BOLA < criptograma.txt
""")
    sys.exit(0)

def cli_mode():
    parser = argparse.ArgumentParser(add_help=False)

    modo = parser.add_mutually_exclusive_group()
    modo.add_argument("--cifrar", action="store_true")
    modo.add_argument("--descifrar", action="store_true")
    modo.add_argument("--tabla", action="store_true")

    parser.add_argument("-k", "--clave", help="Clave para cifrado/descifrado")
    parser.add_argument("--tabla-clave", help="Clave para generar la tabla")
    parser.add_argument("-i", "--infile", help="Archivo de entrada (opcional)")
    parser.add_argument("-o", "--outfile", help="Archivo de salida (opcional)")
    parser.add_argument("--grupo5", action="store_true")

    # *** FIX: todas las opciones empiezan por '-' ***
    parser.add_argument("--h", "-?", "--help", action="store_true", dest="helpflag")

    args, unknown = parser.parse_known_args()

    # ayuda extendida si se pide --h, -?, --help o si hay argumentos inválidos
    if args.helpflag or unknown:
        ayuda_extendida()

    # Si no se especifica ningún modo → volver al menú original
    if not args.cifrar and not args.descifrar and not args.tabla:
        return False

    # Generar tabla
    inicio = verificar_clave(args.tabla_clave or "")
    generar_tabla(inicio, mostrar=args.tabla)

    if args.tabla:
        return True

    # Entrada
    if args.infile:
        with open(args.infile, "r", encoding="utf-8") as f:
            texto = f.read()
    else:
        texto = sys.stdin.read()

    # Cifrado / Descifrado
    if args.cifrar:
        res = cifrarMensaje(args.clave, texto)
    else:
        res = descifrarMensaje(args.clave, texto)

    if args.grupo5:
        res = agrupar_5(res)

    # Salida
    if args.outfile:
        with open(args.outfile, "w", encoding="utf-8") as f:
            f.write(res)
    else:
        print(res)

    return True


# ---------------------------------------------------------------------------
# MENÚ ORIGINAL (se mantiene intacto)
# ---------------------------------------------------------------------------

def main():
    # si hay parámetros CLI → saltar menú
    if cli_mode():
        return

    print("""Elige una de estas opciones:
    1) Generar una tabla con o sin clave.
    2) Cifrar un mensaje.
    3) Descifrar un criptograma.""")
    
    opc = int(input("Opción > "))

    if opc == 1:
        clave = input("Clave para la tabla (Enter para omitir) > ").upper()
        inicio = verificar_clave(clave)
        generar_tabla(inicio, True)

    elif opc == 2:
        clave_tabla = input("Clave para la tabla (Enter para omitir) > ").upper()
        inicio = verificar_clave(clave_tabla)
        generar_tabla(inicio)
        mensaje = input("Mensaje > ").upper()
        clave = input("Clave > ").upper()
        criptograma = cifrarMensaje(clave, mensaje)
        print("\n", criptograma)

    elif opc == 3:
        clave_tabla = input("Clave para la tabla (Enter para omitir) > ").upper()
        inicio = verificar_clave(clave_tabla)
        generar_tabla(inicio)
        criptograma = input("Criptograma > ").upper()
        clave = input("Clave > ").upper()
        texto = descifrarMensaje(clave, criptograma)
        print("\n", texto)
        


if __name__ == "__main__":
    main()
