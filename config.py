"""Parametres de l'application.

Les deux liens de formulaires sont a remplir une fois les formulaires publies.
"""

# Formulaire d'evaluation heberge sur Kobo Toolbox
LIEN_KOBO = 'https://ee.kobotoolbox.org/single/bNwGbN3j'

# Formulaire d'evaluation heberge sur Google Forms
LIEN_GOOGLE_FORMS = (
    'https://docs.google.com/forms/d/e/'
    '1FAIpQLSehbn0C7JisktD4q4bsO9ytF4ASWoS5_PH9grLf-VmiTmGfzw/viewform'
)

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
