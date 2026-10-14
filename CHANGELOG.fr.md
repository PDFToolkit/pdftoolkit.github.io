# Historique de la documentation

[English](CHANGELOG.md) · [Français](CHANGELOG.fr.md)

## [Non publié]

## [0.2.0] - 2026-10-14

- Publier les guides, les 26 tutoriels, les recettes et les documentations des
  packages en anglais et en français, avec l’anglais par défaut sur le site.
- Ajouter un sélecteur vers la même page, les messages de recherche et de copie
  traduits, la provenance propre à chaque traduction et les variantes pour les
  moteurs de recherche.
- Conserver les filtres de recherche et faire correspondre les ancres des
  sections lors du changement de langue ; maintenir les adresses françaises
  existantes et partager les PDF, sources et références inchangés.
- Vérifier les deux inventaires API complets, les pages équivalentes, les liens
  de langue, les titres et les comportements de navigation, recherche et copie.
- Sélectionner le core 0.5.5 et les modules optionnels 0.1.6 publiés.

## [0.1.3] - 2026-10-14

- Ajouter un espacement intérieur adaptatif aux introductions des encadrés
  PDF, sortie de lecture et code source dans les tutoriels et exemples.
  Éloigner les titres et descriptions des bordures en préservant les
  dispositions des aperçus, barres d'outils et blocs de code.

## [0.1.2] - 2026-10-14

- Conserver la hauteur normale du champ de recherche des composants sur
  ordinateur et mobile. Supprimer une base Flexbox qui imposait par erreur
  une hauteur de 230 pixels dans un libellé en colonne ; conserver la largeur
  adaptative et la hauteur minimale de 44 pixels.
- Ajouter une empreinte de contenu aux URL des feuilles de style pour que
  les navigateurs chargent les styles actualisés après un déploiement au
  lieu de conserver une version précédente en cache.

## [0.1.1] - 2026-10-14

- Documenter l'installation Composer des quatre bibliothèques PHP depuis
  Packagist, y compris les modules optionnels et l'installation indépendante
  du core.
- Relier les packages Packagist publiés depuis les cartes de packages,
  les pages d'entrée des modules et les index API par package.
- Distinguer l'installation d'une application du checkout de développement
  verrouillé utilisé pour exécuter les tutoriels et produire leurs vrais PDF.
- Sélectionner les sources du core 0.5.4 et des modules 0.1.5 pour les
  versions documentées et les commandes d'installation.

## [0.1.0] - 2026-10-14

- Centraliser la documentation PDFToolkit à https://pdftoolkit.github.io/
  dans un dépôt dédié, avec guides communs, tutoriels, fiches API et vrais PDF.
- Ajouter des pages d'entrée dédiées et des guides publiés centralement
  pour le core, le lecteur et les convertisseurs d'images et de polices.
- Séparer la provenance de la documentation de la version publiée et du
  commit exact de chaque package. Valider les sources stables épinglées et
  les liens de source générés.
- Sélectionner les versions du core 0.5.3 et des modules optionnels 0.1.4
  pour cette première version de documentation, avec leurs tags publiés
  et leurs commits exacts.
- Conserver la navigation existante sous `/pdf/`, les requêtes, fragments
  et téléchargements binaires grâce à un déploiement de compatibilité.
