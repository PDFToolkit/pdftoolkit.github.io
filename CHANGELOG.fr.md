# Historique de la documentation

[English](CHANGELOG.md) · [Français](CHANGELOG.fr.md)

## [Non publié]

## [0.5.0] - 2026-10-14

- Documenter le core 0.7.0 et les modules PDF 0.1.8 à partir de leurs tags publiés ;
  conserver OpenType 0.1.0 indépendant et la provenance propre à la documentation.
- Publier les guides anglais/français du bundle PDF 2.0 à onze sources, de ses
  objets, algorithmes, preuves de validation et limites explicites de conformité.
- Étendre les fiches API et la recherche à l’inventaire des dictionnaires de base,
  avec clés variables et extraits normatifs originaux en anglais. Distinguer
  les résumés du projet traduits et les états d’approbation des corrections.
- Ajouter des tutoriels exécutables avec aperçus PDF réels pour XMP/déclarations,
  enveloppes chiffrées, espaces de noms, signatures modernes et horodatages/DSS.
- Étendre le parcours bilingue à 34 tutoriels avec mesures géospatiales et
  destinations de structure ; expliquer les métriques explicites des polices PDF2.
- Relier la revue WTPDF par clause et vérifier identité de source, frontières
  d’exécution déclarées et chemins de preuve à chaque construction documentaire.
- Exécuter les oracles indépendants de métadonnées, AES-GCM/CMS/MAC, horodatages
  historiques et structure ; vérifier l’identité des octets des originaux liés.
- Actualiser installation, prérequis, architecture, revue de sécurité, frontières
  des packages, README et navigation tout en préservant les URL existantes.

## [0.4.0] - 2026-10-14

- Ajouter OpenType 0.1.0 indépendant à côté du core et des convertisseurs PDF :
  source publiée exacte, composants d'API, navigation et guides anglais/français complets.
- Expliquer les correspondances Unicode, métriques, ligatures, petites capitales,
  variantes et construction directe, avec la couverture et les mécanismes restants.
- Documenter le core 0.6.2 et relier l'original ISO 32000-2:2020 EC3 inchangé dans
  son dépôt public. Indiquer l'accès sponsorisé de la PDF Association et vérifier les octets.
- Garder les modules PDF optionnels en 0.1.7 ; préserver routes, aperçus,
  téléchargements et alias. OpenType n'ajoute aucune dépendance de production au core.

## [0.3.0] - 2026-10-14

- Documenter le core 0.6.1 et les modules optionnels 0.1.7 depuis leurs versions
  publiées ; conserver séparément les commits de packages et la provenance du site.
- Ajouter le guide PDF 2.0 et le tutoriel 27 intégralement en anglais/français,
  avec PDF réel, rendu de police incorporée, noms F/UF Unicode et octets CSV.
- Expliquer les associations AF, le contenu MCAF nommé corrigé, les faits figés
  lors de l’émission native, les ressources des Form PDF 2.0 et la validation
  bornée des dates sources. Distinguer le texte UTF-8 et les codes de police/CID.
- Ajouter des fiches API et recherches propres au pilote ISO 32000-2 ; un numéro
  de tableau n’associe plus une source ISO1 aux définitions ISO2 ou au MCAF natif.
- Conserver la provenance de la source EC3 privée par ses métadonnées et pages
  physiques, sans publier son PDF personnalisé ni créer un téléchargement invalide.
- Distinguer Completed approuvé par ISO d’Accepted approuvé par le TWG,
  les fonctionnalités introduites/dépréciées/interdites, le refus R5 et les
  permissions CMS PDF 2.0 ; garder catalogue complet, R6 et autres mécanismes en attente.
- Préserver les 26 leçons existantes, PDF de référence, téléchargements, langues
  et adresses historiques. Vérifier structure bilingue, régressions de provenance
  et exemple réel avec l’oracle PDF 2.0 indépendant.

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
