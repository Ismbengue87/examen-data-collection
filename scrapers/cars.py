"""Source 2 : Gaaraas — annonces auto du vendeur Dakar Auto.

https://www.gaaraas.com/fr/users/dakar-auto?page=1

Le vendeur publie 245 annonces reparties sur 13 pages (20 par page).
Les 7 variables demandees sont toutes presentes sur la carte de l'annonce :
aucune page de detail n'a besoin d'etre ouverte.
"""

import time

from selenium.webdriver.common.by import By

from .driver import get_driver

BASE = 'https://www.gaaraas.com/fr/users/dakar-auto?page='
NB_PAGES = 13

# Marques ecrites en deux mots : sans cette liste, 'Land Rover Range Rover'
# donnerait marque='Land' et modele='Rover Range Rover'.
MARQUES_COMPOSEES = [
    'Land Rover', 'Alfa Romeo', 'Aston Martin', 'Great Wall',
    'Mercedes Benz', 'Range Rover', 'DS Automobiles',
]


def nettoyer_nombre(texte):
    """'2 700 000' ou '120 000 km' -> 2700000 / 120000. Renvoie None si illisible."""
    chiffres = ''.join(c for c in texte if c.isdigit())
    return int(chiffres) if chiffres else None


def decouper_titre(titre):
    """'2010 Renault Clio' -> (2010, 'Renault', 'Clio')"""
    mots = titre.split()
    annee = int(mots[0]) if mots and mots[0].isdigit() else None
    reste = ' '.join(mots[1:]) if annee else titre

    for marque in MARQUES_COMPOSEES:
        if reste.lower().startswith(marque.lower()):
            return annee, marque, reste[len(marque):].strip()

    mots_reste = reste.split()
    marque = mots_reste[0] if mots_reste else ''
    modele = ' '.join(mots_reste[1:])
    return annee, marque, modele


def texte_ou_vide(conteneur, selecteur):
    """Renvoie le texte d'un sous-element, ou une chaine vide s'il est absent."""
    elements = conteneur.find_elements(By.CSS_SELECTOR, selecteur)
    return elements[0].text.strip() if elements else ''


def scraper_page(driver, numero):
    """Scrape les annonces d'une page et renvoie la liste des voitures nettoyees."""
    driver.get(f'{BASE}{numero}')
    cartes = driver.find_elements(By.CSS_SELECTOR, 'a.common-ad-card')

    data = []
    for carte in cartes:
        try:
            titre = carte.find_element(By.CSS_SELECTOR, 'h4').get_attribute('title')
            annee, marque, modele = decouper_titre(titre)

            data.append({
                'marque': marque,
                'modele': modele,
                'annee': annee,
                'prix': nettoyer_nombre(texte_ou_vide(carte, '.ad-vehicle-price .value')),
                'kilometrage': nettoyer_nombre(texte_ou_vide(carte, '.ad-vehicle-mileage .value')),
                'boite_vitesses': texte_ou_vide(carte, '.transmission') or 'Non precise',
                'region': texte_ou_vide(carte, '.location') or 'Non precise',
            })
        except Exception:
            pass  # une annonce mal formee ne doit pas arreter la collecte
    return data


def scraper(nb_pages=NB_PAGES, progression=None):
    """Scrape nb_pages du vendeur et renvoie la liste des annonces nettoyees."""
    driver = get_driver()
    data = []
    try:
        for numero in range(1, nb_pages + 1):
            data.extend(scraper_page(driver, numero))
            if progression:
                progression(numero, nb_pages)
            time.sleep(1)  # on evite de marteler le site
    finally:
        driver.quit()
    return data


if __name__ == '__main__':
    import sys

    import pandas as pd

    from db import sauvegarder

    pages = int(sys.argv[1]) if len(sys.argv) > 1 else NB_PAGES

    def afficher(n, total):
        print(f'\rpage {n}/{total}', end='', flush=True)

    df = pd.DataFrame(scraper(pages, afficher))
    print()
    sauvegarder(df, 'cars_clean')
    print(df.shape, 'lignes enregistrees dans cars_clean')
