"""Source 1 : Books to Scrape — scraping et nettoyage avec Selenium.

https://books.toscrape.com/catalogue/page-1.html  (50 pages, 20 livres par page)

Trois des neuf variables (description, type de produit, tax) n'existent que sur
la page de detail d'un livre. Pour chaque page du catalogue on recupere donc les
liens des livres, puis on ouvre chaque livre pour en extraire les variables.
"""

import pandas as pd
from selenium.webdriver.common.by import By

from .driver import get_driver

# La note est ecrite dans le nom de la classe CSS : <p class="star-rating Three">
NOTES = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}


def nettoyer_description(texte):
    """Le site publie un extrait tronque, puis repete le texte complet derriere,
    et termine par '...more'. On enleve le suffixe et la partie dupliquee.
    """
    texte = texte.replace('...more', '').strip()
    debut = texte[:40]
    if debut:
        seconde_occurrence = texte.find(debut, 1)
        if seconde_occurrence > 0:
            texte = texte[seconde_occurrence:]
    return texte.strip()


def scraper(nb_pages=50, progression=None):
    """Collecte nb_pages du catalogue et renvoie un DataFrame nettoye."""
    # Lancer le navigateur
    driver = get_driver()
    df_final = pd.DataFrame()

    try:
        for i in range(1, nb_pages + 1):
            url = f'https://books.toscrape.com/catalogue/page-{i}.html'
            # ouvrir la page
            driver.get(url)

            # recuperer le lien de chaque livre de la page
            # (on stocke les liens avant d'ouvrir les pages de detail :
            #  ouvrir une nouvelle page rend les elements precedents inutilisables)
            liens = []
            for container in driver.find_elements(By.CSS_SELECTOR, 'article.product_pod h3 a'):
                liens.append(container.get_attribute('href'))

            data = []
            for lien in liens:
                # une page peut echouer pour une raison passagere : on retente une fois
                for tentative in range(2):
                    try:
                        driver.get(lien)

                        # 'In stock (22 available)' -> disponibilite + nombre de produits
                        values = driver.find_element(
                            By.CSS_SELECTOR, 'p.instock.availability').text.split(' (')

                        # le tableau des caracteristiques, transforme en dictionnaire
                        table = {}
                        for ligne in driver.find_elements(By.CSS_SELECTOR, 'table.table-striped tr'):
                            cle = ligne.find_element(By.TAG_NAME, 'th').text
                            table[cle] = ligne.find_element(By.TAG_NAME, 'td').text

                        # la description est le paragraphe qui suit le titre de section
                        descriptions = driver.find_elements(By.CSS_SELECTOR, '#product_description ~ p')
                        # la categorie est le 3e maillon du fil d'ariane : Home > Books > Poetry
                        fil = driver.find_elements(By.CSS_SELECTOR, 'ul.breadcrumb li a')
                        note = driver.find_element(By.CSS_SELECTOR, 'p.star-rating').get_attribute('class')

                        dic = {
                            'titre': driver.find_element(By.TAG_NAME, 'h1').text,
                            'prix': float(driver.find_element(
                                By.CSS_SELECTOR, 'p.price_color').text.replace('£', '')),
                            'disponibilite': values[0].strip(),
                            'nombre_produits': int(values[1].split(' ')[0]),
                            'note': NOTES[note.replace('star-rating', '').strip()],
                            'nombre_reviews': int(table['Number of reviews']),
                            'description': nettoyer_description(descriptions[0].text) if descriptions else '',
                            'type_produit': table['Product Type'],
                            'categorie': fil[2].text,
                            'tax': float(table['Tax'].replace('£', '')),
                            'upc': table['UPC'],
                            'url': lien,
                        }
                        data.append(dic)
                        break
                    except:
                        if tentative == 1:
                            print(f'\nABANDON {lien}')

            df = pd.DataFrame(data)
            df_final = pd.concat([df_final, df], axis=0).reset_index(drop=True)

            if progression:
                progression(i, nb_pages)
    finally:
        # fermer le navigateur
        driver.quit()

    return df_final


if __name__ == '__main__':
    import sys

    from db import sauvegarder

    pages = int(sys.argv[1]) if len(sys.argv) > 1 else 50

    def afficher(n, total):
        print(f'\rpage {n}/{total}', end='', flush=True)

    df_final = scraper(pages, afficher)
    print()
    sauvegarder(df_final, 'books_clean')
    print(df_final.shape, 'lignes enregistrees dans books_clean')
