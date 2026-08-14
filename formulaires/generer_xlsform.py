"""Genere le XLSForm du formulaire d'evaluation, a televerser sur Kobo Toolbox.

    python formulaires/generer_xlsform.py

Produit formulaire_kobo.xlsx : trois feuilles (survey, choices, settings),
avec les quatre logiques conditionnelles et le champ calcule demandes.
"""

from pathlib import Path

import pandas as pd

SORTIE = Path(__file__).parent / 'formulaire_kobo.xlsx'

ACCORD = 'select_one accord'

# --------------------------------------------------------------------------- #
# Feuille survey
# --------------------------------------------------------------------------- #

survey = [
    # type, name, label, required, relevant, calculation, appearance, constraint
    ('begin_group', 'section1', 'SECTION 1 : Informations sur l\'évaluateur', '', '', '', '', ''),
    ('date', 'date_evaluation', 'Date de l\'évaluation', 'yes', '', '', '', ''),
    ('text', 'nom', 'Votre nom (facultatif)', '', '', '', '', ''),
    ('select_one role', 'role', 'Votre rôle / profession', 'yes', '', '', '', ''),
    ('text', 'autre_profession', 'Autre profession', 'yes', "${role} = 'autre'", '', '', ''),
    ('select_one appareil', 'appareil', 'Comment avez-vous accédé à l\'application ?', 'yes', '', '', '', ''),
    ('select_one oui_non', 'premiere_utilisation', 'Est-ce votre première utilisation de l\'application ?', 'yes', '', '', '', ''),
    ('select_one frequence', 'nb_utilisations', 'Combien de fois l\'avez-vous utilisée auparavant ?', '', "${premiere_utilisation} = 'non'", '', '', ''),
    ('end_group', '', '', '', '', '', '', ''),

    ('begin_group', 'section2', 'SECTION 2 : Première impression et interface', '', '', '', '', ''),
    (ACCORD, 'interface_attrayante', 'L\'interface est attrayante et bien conçue', 'yes', '', '', '', ''),
    (ACCORD, 'facile_naviguer', 'L\'application est facile à naviguer', 'yes', '', '', '', ''),
    (ACCORD, 'menus_clairs', 'Les menus et les boutons sont clairement libellés', 'yes', '', '', '', ''),
    (ACCORD, 'chargement_rapide', 'L\'application se charge rapidement', 'yes', '', '', '', ''),
    (ACCORD, 'fonctionne_appareil', 'L\'application fonctionne bien sur mon appareil', 'yes', '', '', '', ''),
    ('end_group', '', '', '', '', '', '', ''),

    ('begin_group', 'section3', 'SECTION 3 : Fonctionnalités et performances', '', '', '', '', ''),
    ('select_multiple fonctionnalites', 'fonctionnalites_testees', 'Quelles fonctionnalités avez-vous testées ?', 'yes', '', '', '', ''),
    (ACCORD, 'repond_besoins', 'Les fonctionnalités répondent à mes besoins', 'yes', '', '', '', ''),
    (ACCORD, 'faciles_utiliser', 'Les fonctionnalités sont faciles à utiliser', 'yes', '', '', '', ''),
    (ACCORD, 'resultats_precis', 'Les résultats fournis sont précis', 'yes', '', '', '', ''),
    (ACCORD, 'taches_efficaces', 'L\'application m\'aide à accomplir mes tâches efficacement', 'yes', '', '', '', ''),
    (ACCORD, 'instructions_claires', 'Les instructions et l\'aide sont claires et utiles', 'yes', '', '', '', ''),
    ('end_group', '', '', '', '', '', '', ''),

    ('begin_group', 'section4', 'SECTION 4 : Problèmes rencontrés', '', '', '', '', ''),
    ('select_one oui_non', 'problemes', 'Avez-vous rencontré des problèmes ou des erreurs ?', 'yes', '', '', '', ''),
    ('select_multiple types_problemes', 'types_problemes', 'Quel(s) type(s) de problème(s) ?', '', "${problemes} = 'oui'", '', '', ''),
    ('text', 'description_problemes', 'Veuillez décrire le(s) problème(s) en détail', '', "${problemes} = 'oui'", '', 'multiline', ''),
    ('end_group', '', '', '', '', '', '', ''),

    ('begin_group', 'section5', 'SECTION 5 : Satisfaction globale', '', '', '', '', ''),
    ('integer', 'rating', 'Note globale de l\'application', 'yes', '', '', '', '. >= 0 and . <= 10'),
    ('calculate', 'niveau_satisfaction', '', '', '', 'if(${rating} >= 9, "Excellent", if(${rating} >= 7, "Très bon", if(${rating} >= 5, "Bon", if(${rating} >= 3, "Passable", "Médiocre"))))', '', ''),
    ('note', 'affichage_satisfaction', 'Niveau de satisfaction : ${niveau_satisfaction}', '', '${rating} != \'\'', '', '', ''),
    ('select_one recommander', 'recommander', 'Recommanderiez-vous cette application ?', 'yes', '', '', '', ''),
    ('select_one utiliser_nouveau', 'utiliser_nouveau', 'Utiliseriez-vous cette application à nouveau ?', 'yes', '', '', '', ''),
    ('end_group', '', '', '', '', '', '', ''),

    ('begin_group', 'section6', 'SECTION 6 : Suggestions d\'amélioration', '', '', '', '', ''),
    ('text', 'points_forts', 'Quels sont les principaux points forts de cette application ?', 'yes', '', '', 'multiline', ''),
    ('text', 'ameliorations', 'Qu\'est-ce qui pourrait être amélioré ?', 'yes', '', '', 'multiline', ''),
    ('text', 'fonctionnalites_manquantes', 'Quelles fonctionnalités manquantes aimeriez-vous voir ajoutées ?', '', '', '', 'multiline', ''),
    ('text', 'commentaires', 'Commentaires ou suggestions supplémentaires', '', '', '', 'multiline', ''),
    ('end_group', '', '', '', '', '', '', ''),

    ('note', 'remerciement',
     'Merci pour votre précieux retour ! Vos commentaires nous aideront à améliorer l\'application.',
     '', '', '', '', ''),
]

COLONNES_SURVEY = [
    'type', 'name', 'label', 'required', 'relevant', 'calculation', 'appearance', 'constraint',
]

# --------------------------------------------------------------------------- #
# Feuille choices
# --------------------------------------------------------------------------- #

choices = []


def ajouter(liste, valeurs):
    for nom, libelle in valeurs:
        choices.append((liste, nom, libelle))


ajouter('role', [
    ('etudiant', 'Étudiant'), ('enseignant', 'Enseignant'), ('chercheur', 'Chercheur'),
    ('analyste', 'Analyste de données'), ('developpeur', 'Développeur'),
    ('chef_projet', 'Chef de projet'), ('autre', 'Autre'),
])
ajouter('appareil', [
    ('ordinateur', 'Ordinateur'), ('tablette', 'Tablette'), ('smartphone', 'Smartphone'),
])
ajouter('oui_non', [('oui', 'Oui'), ('non', 'Non')])
ajouter('frequence', [
    ('2_3', '2 à 3 fois'), ('4_5', '4 à 5 fois'), ('plus_5', 'Plus de 5 fois'),
])
ajouter('accord', [
    ('1', 'Tout à fait en désaccord'), ('2', 'En désaccord'), ('3', 'Neutre'),
    ('4', 'D\'accord'), ('5', 'Tout à fait d\'accord'),
])
ajouter('fonctionnalites', [
    ('collecte', 'Collecte (scraping) de données'), ('telechargement', 'Téléchargement'),
    ('formulaire', 'Remplissage du formulaire'), ('dashboard', 'Tableau de bord des données'),
])
ajouter('types_problemes', [
    ('erreur_chargement', 'Erreur de chargement'), ('affichage', 'Problème d\'affichage'),
    ('non_fonctionnelle', 'Fonctionnalité non fonctionnelle'), ('perte_donnees', 'Perte de données'),
    ('performance', 'Performance lente'), ('interface_confuse', 'Interface confuse'),
    ('autre', 'Autre'),
])
ajouter('recommander', [
    ('oui_sans_hesiter', 'Oui, sans hésiter'), ('oui_probablement', 'Oui, probablement'),
    ('peut_etre', 'Peut-être'), ('probablement_pas', 'Probablement pas'), ('non', 'Non'),
])
ajouter('utiliser_nouveau', [
    ('oui_regulierement', 'Oui, régulièrement'), ('oui_occasionnellement', 'Oui, occasionnellement'),
    ('peut_etre', 'Peut-être'), ('probablement_pas', 'Probablement pas'), ('non', 'Non'),
])

# --------------------------------------------------------------------------- #

if __name__ == '__main__':
    settings = pd.DataFrame([{
        'form_title': 'Évaluation de l\'application web',
        'form_id': 'evaluation_application_web',
        'default_language': 'French (fr)',
    }])

    with pd.ExcelWriter(SORTIE, engine='openpyxl') as writer:
        pd.DataFrame(survey, columns=COLONNES_SURVEY).to_excel(
            writer, sheet_name='survey', index=False
        )
        pd.DataFrame(choices, columns=['list_name', 'name', 'label']).to_excel(
            writer, sheet_name='choices', index=False
        )
        settings.to_excel(writer, sheet_name='settings', index=False)

    print(f'{SORTIE.name} genere : {len(survey)} lignes survey, {len(choices)} choix')
