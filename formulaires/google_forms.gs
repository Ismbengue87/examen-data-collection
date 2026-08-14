/**
 * Genere le formulaire d'evaluation sur Google Forms.
 *
 * Mode d'emploi :
 *   1. Ouvrir https://script.google.com et creer un nouveau projet
 *   2. Coller ce fichier a la place du contenu par defaut
 *   3. Lancer la fonction creerFormulaire et autoriser l'acces
 *   4. Les deux liens (edition et reponse) s'affichent dans le journal d'execution
 *
 * Les questions sont ajoutees dans l'ordre du document : chaque saut de section
 * ouvre une section, et tout ce qui suit lui appartient jusqu'au saut suivant.
 * Les branchements sont appliques a la fin, quand toutes les sections existent.
 *
 * Les quatre logiques conditionnelles de l'enonce sont reproduites avec la
 * navigation par section : chaque question conditionnelle est la derniere de sa
 * section, et chacun de ses choix renvoie vers la section voulue.
 *
 * Difference assumee avec la version Kobo : Google Forms n'a pas de champ
 * calcule. La question « Niveau de satisfaction », derivee de la note globale,
 * n'existe donc que sur la version Kobo.
 */

var ACCORD = [
  'Tout à fait en désaccord',
  'En désaccord',
  'Neutre',
  "D'accord",
  "Tout à fait d'accord",
];

/** Ajoute une question d'accord (echelle de Likert a 5 niveaux). */
function ajouterAccord(form, libelle) {
  form.addMultipleChoiceItem()
      .setTitle(libelle)
      .setChoiceValues(ACCORD)
      .setRequired(true);
}

function creerFormulaire() {
  var form = FormApp.create("Évaluation de l'application web");
  form.setDescription(
    "Votre retour permet d'améliorer l'application de collecte de données. " +
    'Le questionnaire prend environ 5 minutes.'
  );
  form.setProgressBar(true);

  // --- SECTION 1 : Informations sur l'évaluateur -------------------------- //
  form.addDateItem().setTitle("Date de l'évaluation").setRequired(true);
  form.addTextItem().setTitle('Votre nom (facultatif)').setRequired(false);
  var role = form.addMultipleChoiceItem()
      .setTitle('Votre rôle / profession')
      .setRequired(true);

  // --- Section conditionnelle : precision du role ------------------------- //
  var pageAutreProfession = form.addPageBreak().setTitle('Précision du rôle');
  form.addTextItem().setTitle('Autre profession').setRequired(true);

  // --- Suite de la section 1 : acces et historique ------------------------ //
  var pageAcces = form.addPageBreak().setTitle("Accès à l'application");
  form.addMultipleChoiceItem()
      .setTitle("Comment avez-vous accédé à l'application ?")
      .setChoiceValues(['Ordinateur', 'Tablette', 'Smartphone'])
      .setRequired(true);
  var premiere = form.addMultipleChoiceItem()
      .setTitle("Est-ce votre première utilisation de l'application ?")
      .setRequired(true);

  // --- Section conditionnelle : frequence d'utilisation ------------------- //
  var pageFrequence = form.addPageBreak().setTitle("Fréquence d'utilisation");
  form.addMultipleChoiceItem()
      .setTitle("Combien de fois l'avez-vous utilisée auparavant ?")
      .setChoiceValues(['2 à 3 fois', '4 à 5 fois', 'Plus de 5 fois'])
      .setRequired(false);

  // --- SECTION 2 : Première impression et interface ----------------------- //
  var pageInterface = form.addPageBreak()
      .setTitle('SECTION 2 : Première impression et interface');
  ajouterAccord(form, "L'interface est attrayante et bien conçue");
  ajouterAccord(form, "L'application est facile à naviguer");
  ajouterAccord(form, 'Les menus et les boutons sont clairement libellés');
  ajouterAccord(form, "L'application se charge rapidement");
  ajouterAccord(form, "L'application fonctionne bien sur mon appareil");

  // --- SECTION 3 : Fonctionnalités et performances ------------------------ //
  form.addPageBreak().setTitle('SECTION 3 : Fonctionnalités et performances');
  form.addCheckboxItem()
      .setTitle('Quelles fonctionnalités avez-vous testées ?')
      .setChoiceValues([
        'Collecte (scraping) de données',
        'Téléchargement',
        'Remplissage du formulaire',
        'Tableau de bord des données',
      ])
      .setRequired(true);
  ajouterAccord(form, 'Les fonctionnalités répondent à mes besoins');
  ajouterAccord(form, 'Les fonctionnalités sont faciles à utiliser');
  ajouterAccord(form, 'Les résultats fournis sont précis');
  ajouterAccord(form, "L'application m'aide à accomplir mes tâches efficacement");
  ajouterAccord(form, "Les instructions et l'aide sont claires et utiles");

  // --- SECTION 4 : Problèmes rencontrés ----------------------------------- //
  form.addPageBreak().setTitle('SECTION 4 : Problèmes rencontrés');
  var problemes = form.addMultipleChoiceItem()
      .setTitle('Avez-vous rencontré des problèmes ou des erreurs ?')
      .setRequired(true);

  // --- Section conditionnelle : detail des problemes ---------------------- //
  var pageDetailProblemes = form.addPageBreak().setTitle('Détail des problèmes');
  form.addCheckboxItem()
      .setTitle('Quel(s) type(s) de problème(s) ?')
      .setChoiceValues([
        'Erreur de chargement',
        "Problème d'affichage",
        'Fonctionnalité non fonctionnelle',
        'Perte de données',
        'Performance lente',
        'Interface confuse',
        'Autre',
      ])
      .setRequired(false);
  form.addParagraphTextItem()
      .setTitle('Veuillez décrire le(s) problème(s) en détail')
      .setRequired(false);

  // --- SECTION 5 : Satisfaction globale ----------------------------------- //
  var pageSatisfaction = form.addPageBreak()
      .setTitle('SECTION 5 : Satisfaction globale');
  form.addScaleItem()
      .setTitle("Note globale de l'application")
      .setBounds(0, 10)
      .setLabels('Médiocre', 'Excellent')
      .setRequired(true);
  form.addMultipleChoiceItem()
      .setTitle('Recommanderiez-vous cette application ?')
      .setChoiceValues([
        'Oui, sans hésiter', 'Oui, probablement', 'Peut-être',
        'Probablement pas', 'Non',
      ])
      .setRequired(true);
  form.addMultipleChoiceItem()
      .setTitle('Utiliseriez-vous cette application à nouveau ?')
      .setChoiceValues([
        'Oui, régulièrement', 'Oui, occasionnellement', 'Peut-être',
        'Probablement pas', 'Non',
      ])
      .setRequired(true);

  // --- SECTION 6 : Suggestions d'amélioration ----------------------------- //
  form.addPageBreak().setTitle("SECTION 6 : Suggestions d'amélioration");
  form.addParagraphTextItem()
      .setTitle('Quels sont les principaux points forts de cette application ?')
      .setRequired(true);
  form.addParagraphTextItem()
      .setTitle("Qu'est-ce qui pourrait être amélioré ?")
      .setRequired(true);
  form.addParagraphTextItem()
      .setTitle('Quelles fonctionnalités manquantes aimeriez-vous voir ajoutées ?')
      .setRequired(false);
  form.addParagraphTextItem()
      .setTitle('Commentaires ou suggestions supplémentaires')
      .setRequired(false);

  // --- Branchements ------------------------------------------------------- //
  // Appliques maintenant : toutes les sections existent, on peut y renvoyer.

  // Logique 1 : si le rôle est « Autre », passer par la section de précision.
  role.setChoices([
    role.createChoice('Étudiant', pageAcces),
    role.createChoice('Enseignant', pageAcces),
    role.createChoice('Chercheur', pageAcces),
    role.createChoice('Analyste de données', pageAcces),
    role.createChoice('Développeur', pageAcces),
    role.createChoice('Chef de projet', pageAcces),
    role.createChoice('Autre', pageAutreProfession),
  ]);

  // Logique 2 : si ce n'est pas la première utilisation, demander la fréquence.
  premiere.setChoices([
    premiere.createChoice('Oui', pageInterface),
    premiere.createChoice('Non', pageFrequence),
  ]);

  // Logiques 3 et 4 : le détail des problèmes n'est demandé qu'en cas de « Oui ».
  problemes.setChoices([
    problemes.createChoice('Oui', pageDetailProblemes),
    problemes.createChoice('Non', pageSatisfaction),
  ]);

  form.setConfirmationMessage(
    'Merci pour votre précieux retour ! Vos commentaires nous aideront à améliorer ' +
    "l'application."
  );

  Logger.log('Lien de réponse  : ' + form.getPublishedUrl());
  Logger.log("Lien d'édition   : " + form.getEditUrl());
}
