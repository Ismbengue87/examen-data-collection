"""Source 1 : Books to Scrape — scraping + nettoyage avec Selenium uniquement.

https://books.toscrape.com/catalogue/page-1.html  (50 pages, 20 livres par page)

Les 9 variables demandees. Les 3 dernieres (description, type de produit, tax)
ne sont disponibles que sur la page de detail de chaque livre : on passe donc
d'abord sur les pages du catalogue pour recuperer les liens, puis sur chaque livre.
"""

from selenium.webdriver.common.by import By

from .driver import get_driver

BASE = 'https://books.toscrape.com/catalogue/'

# La note est ecrite dans le nom de la classe CSS : <p class="star-rating Three">
NOTES = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}


def nettoyer_prix(texte):
    """'£51.77' -> 51.77"""
    return float(texte.replace('£', '').strip())


def nettoyer_description(texte):
    """Corrige le defaut de la source : le site publie un extrait tronque, puis
    repete le texte complet derriere, et termine par '...more'.
    """
    texte = texte.replace('...more', '').strip()
    debut = texte[:40]
    if debut:
        seconde_occurrence = texte.find(debut, 1)
        if seconde_occurrence > 0:
            texte = texte[seconde_occurrence:]
    return texte.strip()


def collecter_liens(driver, nb_pages):
    """Parcourt les pages du catalogue et renvoie l'URL de chaque livre."""
    liens = []
    for i in range(1, nb_pages + 1):
        driver.get(f'{BASE}page-{i}.html')
        conteneurs = driver.find_elements(By.CSS_SELECTOR, 'article.product_pod h3 a')
        for conteneur in conteneurs:
            liens.append(conteneur.get_attribute('href'))
    return liens


def scraper_livre(driver, url):
    """Ouvre la page d'un livre et renvoie ses 9 variables, deja nettoyees."""
    driver.get(url)

    # 'In stock (22 available)' -> disponibilite + nombre de produits
    stock = driver.find_element(By.CSS_SELECTOR, 'p.instock.availability').text
    disponibilite = stock.split('(')[0].strip()
    nombre_produits = int(stock.split('(')[1].split(' ')[0]) if '(' in stock else 0

    # Le tableau de caracteristiques : on le transforme en dictionnaire
    table = {}
    for ligne in driver.find_elements(By.CSS_SELECTOR, 'table.table-striped tr'):
        cle = ligne.find_element(By.TAG_NAME, 'th').text
        table[cle] = ligne.find_element(By.TAG_NAME, 'td').text

    # La description est le paragraphe qui suit le titre '#product_description'
    descriptions = driver.find_elements(By.CSS_SELECTOR, '#product_description ~ p')
    description = nettoyer_description(descriptions[0].text) if descriptions else ''

    # La categorie est le 3e maillon du fil d'ariane : Accueil > Books > Poetry
    fil = driver.find_elements(By.CSS_SELECTOR, 'ul.breadcrumb li a')
    categorie = fil[2].text if len(fil) > 2 else ''

    note = driver.find_element(By.CSS_SELECTOR, 'p.star-rating').get_attribute('class')

    return {
        'titre': driver.find_element(By.TAG_NAME, 'h1').text,
        'prix': nettoyer_prix(driver.find_element(By.CSS_SELECTOR, 'p.price_color').text),
        'disponibilite': disponibilite,
        'nombre_produits': nombre_produits,
        'note': NOTES.get(note.replace('star-rating', '').strip(), 0),
        'nombre_reviews': int(table.get('Number of reviews', 0)),
        'description': description,
        'type_produit': table.get('Product Type', ''),
        'categorie': categorie,
        'tax': nettoyer_prix(table.get('Tax', '£0.00')),
        'upc': table.get('UPC', ''),
        'url': url,
    }


def scraper(nb_pages=50, progression=None):
    """Scrape nb_pages du catalogue et renvoie la liste des livres nettoyes.

    progression : fonction optionnelle appelee a chaque livre (utilisee par Streamlit).
    """
    driver = get_driver()
    data = []
    try:
        liens = collecter_liens(driver, nb_pages)
        for n, lien in enumerate(liens, start=1):
            # Une page peut echouer pour une raison passagere (reseau) : on retente
            # une fois avant d'abandonner ce livre, et on signale l'abandon.
            for tentative in range(2):
                try:
                    data.append(scraper_livre(driver, lien))
                    break
                except Exception as erreur:
                    if tentative == 1:
                        print(f'\nABANDON {lien} ({type(erreur).__name__})')
            if progression:
                progression(n, len(liens))
    finally:
        driver.quit()
    return data


if __name__ == '__main__':
    import sys

    import pandas as pd

    from db import sauvegarder

    pages = int(sys.argv[1]) if len(sys.argv) > 1 else 50

    def afficher(n, total):
        print(f'\r{n}/{total} livres', end='', flush=True)

    df = pd.DataFrame(scraper(pages, afficher))
    print()
    sauvegarder(df, 'books_clean')
    print(df.shape, 'lignes enregistrees dans books_clean')
