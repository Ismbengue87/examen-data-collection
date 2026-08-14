"""Base de donnees SQLite du projet.

Une table par jeu de donnees :
  books_clean / cars_clean : donnees scrapees et nettoyees avec Selenium
  books_raw   / cars_raw   : donnees brutes issues de l'extension Web Scraper (no-code)
"""

import sqlite3
from pathlib import Path

import pandas as pd

CHEMIN = Path(__file__).parent / 'data' / 'collecte.db'


def connexion():
    CHEMIN.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(CHEMIN)


def sauvegarder(df, table):
    """Ecrit un DataFrame dans une table (remplace la table si elle existe)."""
    with connexion() as conn:
        df.to_sql(table, conn, if_exists='replace', index=False)


def charger(table):
    """Lit une table et renvoie un DataFrame. DataFrame vide si la table n'existe pas."""
    try:
        with connexion() as conn:
            return pd.read_sql_query(f'SELECT * FROM {table}', conn)
    except Exception:
        return pd.DataFrame()


def tables():
    """Liste les tables presentes dans la base."""
    with connexion() as conn:
        lignes = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
    return [ligne[0] for ligne in lignes]
