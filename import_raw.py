"""Importe les CSV bruts de l'extension Web Scraper dans la base.

A lancer apres avoir exporte les donnees depuis Chrome :
    python import_raw.py

Les fichiers attendus sont data/raw/books_raw.csv et data/raw/cars_raw.csv.
Les colonnes sont importees telles quelles, sans nettoyage : c'est le but
de la partie no-code, qui sert de point de comparaison avec le scraping Selenium.
"""

from pathlib import Path

import pandas as pd

from db import sauvegarder

DOSSIER = Path(__file__).parent / 'data' / 'raw'

if __name__ == '__main__':
    for cle in ['books', 'cars']:
        fichier = DOSSIER / f'{cle}_raw.csv'
        if not fichier.exists():
            print(f'absent  : {fichier.name}')
            continue

        df = pd.read_csv(fichier, dtype=str)  # dtype=str : on ne type rien, donnees brutes
        sauvegarder(df, f'{cle}_raw')
        print(f'importe : {fichier.name} -> {cle}_raw ({df.shape[0]} lignes, {df.shape[1]} colonnes)')
