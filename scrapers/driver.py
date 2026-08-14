"""Fabrique un navigateur Chrome pilote par Selenium.

Le meme code doit tourner sur deux environnements :
  - en local (Mac/Windows) : Selenium Manager telecharge le driver tout seul
  - sur Streamlit Cloud (Linux) : chromium est installe via packages.txt
"""

import shutil

from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')          # pas de fenetre visible
    options.add_argument('--no-sandbox')            # obligatoire sur Streamlit Cloud
    options.add_argument('--disable-dev-shm-usage') # evite les crash memoire du conteneur
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--blink-settings=imagesEnabled=false')  # on ne scrape pas les images

    chromium = shutil.which('chromium') or shutil.which('chromium-browser')
    if chromium:
        # Environnement Streamlit Cloud
        options.binary_location = chromium
        return webdriver.Chrome(service=Service(shutil.which('chromedriver')), options=options)

    # Environnement local
    return webdriver.Chrome(options=options)
