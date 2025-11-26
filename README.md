# criptoclasica
Python tools for classical cryptanalysis with a mathematical focus: frequency analysis, IC, Hill cipher algebra, Vigenère attacks, transposition reconstruction, and statistical methods for ciphertext analysis.
## Overview
This repository provides a modular collection of scripts for analysing and breaking classical ciphers. Each tool is designed for teaching, research, and reproducible experiments in classical cryptanalysis, following mathematically rigorous methods.

## Features
- **Monoalphabetic ciphers**: Caesar, affine, mixed alphabets, decimation.
- **Frequency analysis**: monographic, digraphic, index of coincidence.
- **Polyalphabetic ciphers**: Vigenère, Kasiski test, subtext extraction, IC-based key length estimation.
- **Polygraphic ciphers**: Hill cipher (2×2), matrix algebra, modular inverses, involutive matrices.
- **Transposition systems**: columnar transposition, double transposition, column compatibility checks.
- **Statistical tools**: distribution comparison, circular correlation, coincidence counting.

## Folder Structure
criptoclasica/
│
├── analysis_tools/        # auxiliary modules 
│   ├── IC.py
│   ├── digraph_matrix.py
│   ├── trigraphs.py
│   ├── expected_digrams.csv
│   └── char_trigrams_es.tsv
│
├── monoalphabetic/        # direct CLI tools
│   ├── cesar.py
│   ├── affine.py
│   ├── mixed_alphabet.py
│   └── freq_analysis.py
│
├── polyalphabetic/
│   ├── vigenere.py
│   ├── repeticiones.py
│   ├── recomponer_subtextos.py
│   ├── subtextos_cifrados.py
│   └── correlacion_circular.py
│
├── polygraphic/
│   ├── hill.py
│   ├── analyse_hill_playfair.py
│   └── digraph_matrix.py
│
└── transposition/
    ├── transposicion.py
    ├── transposition_word.py
    └── auto_transpo.py


## Documentation

Each script includes:

command-line help (--help)

commented code


A **full guide** is available in the book “**Fundamentos Matemáticos del Criptoanálisis Clásico — Teoría y Práctica**”.

## Installation
No installation required.  
Clone the repository and run any script directly:

```bash
git clone https://github.com/darboledas/criptoclasica
cd criptoclasica
python3 folder/script.py --help

## License

MIT License.

## Author

David Arboledas Brihuega
