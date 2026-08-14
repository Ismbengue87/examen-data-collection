"""Source 2 : Gaaraas — annonces auto du vendeur Dakar Auto.

https://www.gaaraas.com/fr/users/dakar-auto?page=1

Le vendeur publie 245 annonces reparties sur 13 pages (20 par page).
Les 7 variables demandees sont toutes presentes sur la carte de l'annonce :
aucune page de detail n'a besoin d'etre ouverte.
"""

import time

import pandas as pd
from selenium.webdriver.common.by import By

from .driver import get_driver

NB_PAGES = 13

# Marques ecrites en deux mots : sans cette liste, 'Land Rover Range Rover'
# donnerait marque = 'Land' et modele = 'Rover Range Rover'.
MARQUES_COMPOSEES = [
    'Land Rover', 'Alfa Romeo', 'Aston Martin', 'Great Wall',
    'Mercedes Benz', 'Range Rover', 'DS Automobiles',
]


def nettoyer_nombre(texte):
    """'CFA 2 700 000' ou '120 000 km' -> 2700000 / 120000. None si illisible."""
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
    return annee, marque, ' '.join(mots_reste[1:])


def texte_ou_vide(container, selecteur):
    """Texte d'un sous-element, ou chaine vide si l'element est absent."""
    elements = container.find_elements(By.CSS_SELECTOR, selecteur)
    return elements[0].text.strip() if elements else ''


def scraper(nb_pages=NB_PAGES, progression=None):
    """Collecte nb_pages du vendeur et renvoie un DataFrame nettoye."""
    # Lancer le navigateur
    driver = get_driver()
    df_final = pd.DataFrame()

    try:
        for i in range(1, nb_pages + 1):
            url = f'https://www.gaaraas.com/fr/users/dakar-auto?page={i}'
            # ouvrir la page
            driver.get(url)

            # containers : une carte par annonce
            containers = driver.find_elements(By.CSS_SELECTOR, 'a.common-ad-card')

            data = []
            for container in containers:
                try:
                    titre = container.find_element(By.CSS_SELECTOR, 'h4').get_attribute('title')
                    annee, marque, modele = decouper_titre(titre)

                    dic = {
                        'marque': marque,
                        'modele': modele,
                        'annee': annee,
                        'prix': nettoyer_nombre(texte_ou_vide(container, '.ad-vehicle-price .value')),
                        'kilometrage': nettoyer_nombre(texte_ou_vide(container, '.ad-vehicle-mileage .value')),
                        'boite_vitesses': texte_ou_vide(container, '.transmission') or 'Non precise',
                        'region': texte_ou_vide(container, '.location') or 'Non precise',
                    }
                    data.append(dic)
                except:
                    pass

            df = pd.DataFrame(data)
            df_final = pd.concat([df_final, df], axis=0).reset_index(drop=True)

            if progression:
                progression(i, nb_pages)

            # on evite de marteler le site
            time.sleep(1)
    finally:
        # fermer le navigateur
        driver.quit()

    return df_final


if __name__ == '__main__':
    import sys

    from db import sauvegarder

    pages = int(sys.argv[1]) if len(sys.argv) > 1 else NB_PAGES

    def afficher(n, total):
        print(f'\rpage {n}/{total}', end='', flush=True)

    df_final = scraper(pages, afficher)
    print()
    sauvegarder(df_final, 'cars_clean')
    print(df_final.shape, 'lignes enregistrees dans cars_clean')
