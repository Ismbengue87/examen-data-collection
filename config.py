"""Parametres de l'application.

Les deux liens de formulaires sont a remplir une fois les formulaires publies.
"""

# Formulaire d'evaluation heberge sur Kobo Toolbox
LIEN_KOBO = ''

# Formulaire d'evaluation heberge sur Google Forms
LIEN_GOOGLE_FORMS = ''

SOURCES = {
    'books': {
        'nom': 'Books to Scrape',
        'url': 'https://books.toscrape.com/catalogue/page-1.html',
        'table': 'books_clean',
        'table_brute': 'books_raw',
        'nb_pages': 50,
    },
    'cars': {
        'nom': 'Gaaraas — Dakar Auto',
        'url': 'https://www.gaaraas.com/fr/users/dakar-auto?page=1',
        'table': 'cars_clean',
        'table_brute': 'cars_raw',
        'nb_pages': 13,
    },
}
