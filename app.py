"""Application Streamlit — Projet d'examen Data Collection.

Cinq pages :
  Accueil          : presentation du projet et des deux sources
  Scraping live    : lance Selenium en direct sur un nombre de pages choisi
  Donnees brutes   : apercu et telechargement du scraping no-code (Web Scraper)
  Dashboard        : visualisation des donnees nettoyees
  Evaluation       : acces aux deux formulaires (Kobo et Google Forms)
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

import db
from config import LIEN_GOOGLE_FORMS, LIEN_KOBO, SOURCES

st.set_page_config(page_title='Data Collection — Examen', page_icon='📊', layout='wide')

DOSSIER_BRUT = Path(__file__).parent / 'data' / 'raw'


@st.cache_data
def charger(table):
    return db.charger(table)


# --------------------------------------------------------------------------- #
# Pages
# --------------------------------------------------------------------------- #

def page_accueil():
    st.title('📊 Collecte de données par web scraping')
    st.caption('Projet d\'examen — Master IA, Dakar Institut of Technology')

    st.markdown(
        "Cette application collecte, nettoie, stocke et visualise des données issues "
        "de deux sites web. Le scraping est réalisé avec **Selenium**, les données sont "
        "stockées dans une base **SQLite**."
    )

    colonnes = st.columns(2)
    for colonne, (cle, source) in zip(colonnes, SOURCES.items()):
        df = charger(source['table'])
        with colonne:
            st.subheader(source['nom'])
            st.link_button('Voir le site', source['url'])
            sous_colonnes = st.columns(2)
            sous_colonnes[0].metric('Lignes collectées', len(df))
            sous_colonnes[1].metric('Variables', df.shape[1] if not df.empty else 0)
            if not df.empty:
                st.dataframe(df.head(5), use_container_width=True)

    st.divider()
    st.subheader('Contenu de la base de données')
    tables = db.tables()
    if tables:
        resume = pd.DataFrame(
            [{'table': t, 'lignes': len(charger(t)), 'colonnes': charger(t).shape[1]}
             for t in tables]
        )
        st.dataframe(resume, use_container_width=True, hide_index=True)
    else:
        st.info('La base est vide. Lancez un scraping depuis la page « Scraping live ».')


def page_scraping():
    st.title('🔎 Scraping live')
    st.markdown(
        'Lance une collecte **en direct** avec Selenium. Le nombre de pages est limité '
        'pour garder un temps de réponse raisonnable : la collecte complète a été faite '
        'en amont et se trouve dans la base.'
    )

    cle = st.selectbox(
        'Source à scraper',
        list(SOURCES),
        format_func=lambda c: SOURCES[c]['nom'],
    )
    source = SOURCES[cle]
    nb_pages = st.slider('Nombre de pages', 1, 5, 2)

    if cle == 'books':
        st.info(f'{nb_pages} page(s) = {nb_pages * 20} livres, une page de détail par livre.')

    if st.button('Lancer le scraping', type='primary'):
        barre = st.progress(0.0, text='Ouverture du navigateur…')

        def avancement(n, total):
            barre.progress(n / total, text=f'{n}/{total}')

        try:
            if cle == 'books':
                from scrapers.books import scraper
            else:
                from scrapers.cars import scraper

            with st.spinner('Collecte en cours…'):
                data = scraper(nb_pages, avancement)

            barre.empty()
            df = pd.DataFrame(data)
            st.success(f'{len(df)} lignes collectées et nettoyées.')
            st.dataframe(df, use_container_width=True)
            st.download_button(
                'Télécharger ce résultat (CSV)',
                df.to_csv(index=False).encode('utf-8'),
                file_name=f'{cle}_scraping_live.csv',
                mime='text/csv',
            )
        except Exception as erreur:
            barre.empty()
            st.error(f'Le scraping a échoué : {erreur}')


def page_donnees_brutes():
    st.title('📁 Données brutes — scraping no-code')
    st.markdown(
        'Ces fichiers proviennent de l\'extension Chrome **Web Scraper**. Ils sont '
        'volontairement **non nettoyés** : prix avec symboles, textes non découpés, '
        'colonnes techniques de l\'outil.'
    )

    for cle, source in SOURCES.items():
        st.subheader(source['nom'])
        fichier = DOSSIER_BRUT / f'{cle}_raw.csv'

        if fichier.exists():
            df = pd.read_csv(fichier)
            st.caption(f'{len(df)} lignes · {df.shape[1]} colonnes · `{fichier.name}`')
            st.dataframe(df.head(20), use_container_width=True)
            st.download_button(
                f'Télécharger {fichier.name}',
                fichier.read_bytes(),
                file_name=fichier.name,
                mime='text/csv',
                key=f'dl_{cle}',
            )
        else:
            st.warning(f'Fichier absent : `data/raw/{cle}_raw.csv`')
        st.divider()


def dashboard_books(df):
    colonnes = st.columns(4)
    colonnes[0].metric('Livres', len(df))
    colonnes[1].metric('Prix moyen', f"£{df['prix'].mean():.2f}")
    colonnes[2].metric('Note moyenne', f"{df['note'].mean():.2f} / 5")
    colonnes[3].metric('Catégories', df['categorie'].nunique())

    categories = st.multiselect('Filtrer par catégorie', sorted(df['categorie'].unique()))
    if categories:
        df = df[df['categorie'].isin(categories)]

    gauche, droite = st.columns(2)
    with gauche:
        st.plotly_chart(
            px.histogram(
                df, x='prix', nbins=30, title='Distribution des prix (£)',
                labels={'prix': 'Prix (£)'},
            ).update_yaxes(title='Nombre de livres'),
            use_container_width=True,
        )
    with droite:
        moyennes = (
            df.groupby('categorie')['note'].mean()
            .sort_values(ascending=False).head(15).reset_index()
        )
        st.plotly_chart(
            px.bar(
                moyennes, x='note', y='categorie', orientation='h',
                title='Note moyenne par catégorie (top 15)',
                labels={'note': 'Note moyenne', 'categorie': ''},
            ),
            use_container_width=True,
        )

    st.dataframe(df, use_container_width=True)


def dashboard_cars(df):
    colonnes = st.columns(4)
    colonnes[0].metric('Annonces', len(df))
    colonnes[1].metric('Prix médian', f"{df['prix'].median() / 1e6:.2f} M CFA")
    colonnes[2].metric('Marques', df['marque'].nunique())
    colonnes[3].metric('Km médian', f"{df['kilometrage'].median() / 1000:.0f} 000 km")

    marques = st.multiselect('Filtrer par marque', sorted(df['marque'].unique()))
    if marques:
        df = df[df['marque'].isin(marques)]

    gauche, droite = st.columns(2)
    with gauche:
        medianes = (
            df.groupby('marque')['prix'].median()
            .sort_values(ascending=False).head(15).reset_index()
        )
        st.plotly_chart(
            px.bar(
                medianes, x='marque', y='prix',
                title='Prix médian par marque (top 15)',
                labels={'prix': 'Prix médian (CFA)', 'marque': ''},
            ),
            use_container_width=True,
        )
    with droite:
        st.plotly_chart(
            px.scatter(
                df.dropna(subset=['prix', 'kilometrage']),
                x='kilometrage', y='prix', color='boite_vitesses',
                hover_data=['marque', 'modele', 'annee'],
                title='Prix en fonction du kilométrage',
                labels={
                    'kilometrage': 'Kilométrage (km)',
                    'prix': 'Prix (CFA)',
                    'boite_vitesses': 'Boîte',
                },
            ),
            use_container_width=True,
        )

    st.dataframe(df, use_container_width=True)


def page_dashboard():
    st.title('📈 Dashboard — données nettoyées')

    cle = st.radio(
        'Source', list(SOURCES), format_func=lambda c: SOURCES[c]['nom'], horizontal=True
    )
    df = charger(SOURCES[cle]['table'])

    if df.empty:
        st.warning('Aucune donnée en base pour cette source.')
        return

    if cle == 'books':
        dashboard_books(df)
    else:
        dashboard_cars(df)


def page_evaluation():
    st.title('📝 Évaluer l\'application')
    st.markdown(
        'Votre retour permet d\'améliorer l\'application. Le questionnaire est '
        'disponible sur deux plateformes, au choix — les questions sont identiques.'
    )

    gauche, droite = st.columns(2)
    with gauche:
        st.subheader('Kobo Toolbox')
        st.caption('Version complète, avec calcul automatique du niveau de satisfaction.')
        if LIEN_KOBO:
            st.link_button('Ouvrir le formulaire Kobo', LIEN_KOBO, type='primary')
        else:
            st.warning('Lien à renseigner dans `config.py` (LIEN_KOBO).')
    with droite:
        st.subheader('Google Forms')
        st.caption('Même questionnaire, hébergé sur Google Forms.')
        if LIEN_GOOGLE_FORMS:
            st.link_button('Ouvrir le formulaire Google', LIEN_GOOGLE_FORMS, type='primary')
        else:
            st.warning('Lien à renseigner dans `config.py` (LIEN_GOOGLE_FORMS).')


# --------------------------------------------------------------------------- #
# Navigation
# --------------------------------------------------------------------------- #

PAGES = {
    'Accueil': page_accueil,
    'Scraping live': page_scraping,
    'Données brutes': page_donnees_brutes,
    'Dashboard': page_dashboard,
    'Évaluation': page_evaluation,
}

st.sidebar.title('Navigation')
choix = st.sidebar.radio('Aller à', list(PAGES), label_visibility='collapsed')
st.sidebar.divider()
st.sidebar.caption('Scraping : Selenium · Base : SQLite · Interface : Streamlit')

PAGES[choix]()
