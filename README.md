# Projet d'examen — Data Collection

Collecte de données par web scraping, nettoyage, stockage en base SQL et déploiement
d'une application Streamlit.

Master IA — Dakar Institut of Technology.

## Accès rapide

| | Lien |
|---|---|
| Application déployée | https://ismbengue.streamlit.app |
| Formulaire d'évaluation — Kobo | https://ee.kobotoolbox.org/single/bNwGbN3j |
| Formulaire d'évaluation — Google Forms | https://docs.google.com/forms/d/e/1FAIpQLSehbn0C7JisktD4q4bsO9ytF4ASWoS5_PH9grLf-VmiTmGfzw/viewform |

Les deux formulaires sont également accessibles depuis la page **Évaluation** de
l'application.

---

## Les deux sources

| | Source 1 | Source 2 |
|---|---|---|
| Site | [Books to Scrape](https://books.toscrape.com/catalogue/page-1.html) | [Gaaraas — Dakar Auto](https://www.gaaraas.com/fr/users/dakar-auto?page=1) |
| Pages | 50 | 13 |
| Lignes collectées | 1000 | 245 |
| Variables | 9 | 7 |

---

## Structure du projet

```
.
├── app.py              application Streamlit (5 pages)
├── config.py           liens des formulaires et description des sources
├── db.py               base SQLite : écriture, lecture, liste des tables
├── import_raw.py       import des CSV du scraping no-code dans la base
├── scrapers/
│   ├── driver.py       fabrique du navigateur Chrome (local et Streamlit Cloud)
│   ├── books.py        source 1 — Selenium, avec nettoyage
│   └── cars.py         source 2 — Selenium, avec nettoyage
├── data/
│   ├── collecte.db     base SQLite (4 tables)
│   └── raw/            CSV bruts exportés depuis l'extension Web Scraper
├── requirements.txt    dépendances Python
└── packages.txt        paquets système pour Streamlit Cloud (chromium)
```

---

## Les 4 tables de la base

| Table | Origine | Nettoyage |
|---|---|---|
| `books_clean` | Selenium | oui |
| `cars_clean` | Selenium | oui |
| `books_raw` | Web Scraper (no-code) | non |
| `cars_raw` | Web Scraper (no-code) | non |

Conserver le brut **et** le propre dans la même base permet de comparer directement
les deux méthodes de collecte.

---

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Chrome doit être installé sur la machine. Le pilote est téléchargé automatiquement
par Selenium Manager, il n'y a rien à installer de plus.

## Utilisation

```bash
python -m scrapers.books 50    # source 1 : 50 pages, ~1000 livres (environ 25 min)
python -m scrapers.cars 13     # source 2 : 13 pages, 245 annonces (environ 1 min)
python import_raw.py           # importe les CSV du scraping no-code
streamlit run app.py           # lance l'application
```

---

## Le scraping Selenium

Contrainte de l'énoncé : **Selenium uniquement**, BeautifulSoup interdit. Les deux
scrapers utilisent donc `find_elements(By.CSS_SELECTOR, ...)` et `.text` /
`.get_attribute()` pour tout extraire.

Le nettoyage est fait **pendant** la collecte, au moment où chaque champ est lu,
et non dans une passe pandas après coup.

### Source 1 — Books to Scrape

Trois des neuf variables (description, type de produit, tax) n'existent que sur la
page de détail d'un livre. La collecte se fait donc en deux temps : on parcourt
d'abord les 50 pages du catalogue pour récupérer les 1000 liens, puis on ouvre
chaque livre.

Nettoyages appliqués :

- `prix` et `tax` : suppression du symbole `£`, conversion en nombre décimal
- `disponibilite` et `nombre_produits` : découpage de `In stock (22 available)`
- `note` : la note est écrite dans la classe CSS (`star-rating Three`), convertie en entier
- `description` : **le site publie un extrait tronqué, puis répète le texte complet
  derrière, et termine par `...more`**. La fonction `nettoyer_description` supprime
  le suffixe et la partie dupliquée.

### Source 2 — Gaaraas

Les 7 variables sont toutes présentes sur la carte de l'annonce dans la liste :
aucune page de détail n'a besoin d'être ouverte.

Nettoyages appliqués :

- `prix` et `kilometrage` : `CFA 2 700 000` et `120 000 km` convertis en entiers
- `marque`, `modele`, `annee` : découpage du titre `2010 Renault Clio`. Une liste de
  marques écrites en deux mots (`Land Rover`, `Alfa Romeo`…) évite de couper
  `Land Rover Range Rover` en marque `Land` et modèle `Rover Range Rover`.
- une pause d'une seconde entre chaque page, pour ne pas marteler le site

---

## Remarques sur les données

Ces observations viennent de la collecte réelle et sont assumées telles quelles.

**Books to Scrape**

- `nombre_reviews` vaut `0` pour les 1000 livres, et `tax` vaut `£0.00` partout.
  C'est la donnée du site, pas une erreur de collecte : ce site est un bac à sable
  et ces deux champs n'ont jamais été remplis.
- La variable V8 « Type de produit (catégorie) » est ambiguë. Le tableau de la page
  contient un champ `Product Type` qui vaut toujours `Books`, sans intérêt pour une
  analyse. La catégorie réelle du livre (Poetry, Historical Fiction…) se trouve dans
  le fil d'Ariane. **Les deux sont collectées** : `type_produit` et `categorie`.
- La table contient deux colonnes en plus des 9 variables demandées : `upc`, qui est
  l'identifiant unique du livre sur le site, et `url`, qui permet de remonter à la
  page d'origine de chaque ligne.
- Lors d'une première collecte, un livre sur les 1000 avait échoué pour une raison
  passagère : il se scrapait sans erreur quand on le relançait seul. Le scraper
  effectue depuis une seconde tentative avant d'abandonner une page, et signale
  explicitement tout abandon au lieu de l'ignorer en silence.

**Gaaraas**

- L'énoncé indique 100 pages. Le vendeur `dakar-auto` n'en publie que **13**
  (245 annonces, la page 14 est vide et la pagination du site s'arrête à 13).
  L'intégralité des annonces disponibles a donc été collectée. Le total obtenu,
  245 lignes, correspond exactement au compteur affiché par le site.
- Valeurs manquantes réelles : 1 année, 1 prix, 2 kilométrages. Elles sont conservées
  en `NULL` plutôt que remplacées par une valeur inventée.
- Le champ `region` vaut `Dakar` pour 244 annonces sur 245, ce qui est attendu pour
  un concessionnaire dakarois.

---

## Déploiement

L'application est déployée sur Streamlit Community Cloud.

Selenium a besoin d'un navigateur sur le serveur : le fichier `packages.txt`
installe `chromium` et `chromium-driver`. Le module `scrapers/driver.py` détecte
l'environnement et pointe vers le bon binaire, avec les options `--headless=new`,
`--no-sandbox` et `--disable-dev-shm-usage` nécessaires dans un conteneur.

La base `data/collecte.db` est versionnée avec le projet : l'application affiche
immédiatement la collecte complète, et le bouton de scraping de la page
« Scraping live » sert à démontrer que la collecte fonctionne en direct, sur un
nombre de pages volontairement limité.

---

## Scraping no-code

Les données brutes des deux sources ont été collectées avec l'extension Chrome
**Web Scraper**, puis exportées en CSV et déposées dans `data/raw/` sous les noms
`books_raw.csv` et `cars_raw.csv`. La commande `python import_raw.py` les charge
dans la base.

Aucun nettoyage n'est appliqué, c'est le principe de cette partie : les prix
gardent leur symbole, les titres ne sont pas découpés, et les colonnes techniques
de l'outil sont conservées. La comparaison avec les tables `*_clean` montre
concrètement ce que le nettoyage Selenium apporte.

## Formulaires d'évaluation

Le questionnaire existe en deux versions, l'une sur Kobo Toolbox et l'autre sur
Google Forms. Toutes deux reprennent les mêmes 6 sections et les mêmes questions,
avec les 4 logiques conditionnelles demandées : précision du rôle, fréquence
d'utilisation, et le détail des problèmes rencontrés.

Une différence est à noter. La question « Niveau de satisfaction » est **calculée**
à partir de la note globale. Kobo le gère nativement avec un champ de type
`calculate`. Google Forms ne dispose pas de champ calculé : sur cette version, la
note globale est saisie seule, sans niveau dérivé. Les logiques conditionnelles y
sont reproduites par la navigation entre sections plutôt que par affichage
dynamique.

Les liens des deux formulaires sont renseignés dans `config.py` et exposés par la
page **Évaluation** de l'application.
