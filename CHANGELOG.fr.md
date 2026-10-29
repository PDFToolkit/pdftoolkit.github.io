# Historique de la documentation

[English](CHANGELOG.md) · [Français](CHANGELOG.fr.md)

## Non publié

## [0.13.0] - 2026-10-29

- Sélectionner Images 0.2.1 depuis son checkout publié indépendant, avec son guide d’architecture français/anglais harmonisé. Conserver distinctes les dépendances verrouillées des exemples du core et des oracles de modules.

- Sélectionner core 0.12.1, Reader 0.7, Images 0.2, Fonts 0.2, OpenType 0.4,
  HTML 0.7 et Codecs indépendant 0.1 publiés, aux commits exacts de leurs tags
  annotés. Construire les sept inventaires API et guides depuis ces sources.
- Documenter le décodage natif prioritaire et l’utilisation automatique de la
  bibliothèque PHP optionnelle, avec commande d’installation, limites de
  ressources et profils pris en charge. Actualiser les guides FR/EN EC3,
  pages/actions, import natif, images, fontes/OpenType et migration du core
  avec les preuves correspondantes.
- Intégrer la démo 0.2.1 publiée et dix exemples reproductibles, dont JPEG,
  JPEG 2000 et JBIG2 dans des Workers PHP/WebAssembly locaux. Conserver les
  quatre identités des packages embarqués, PDF originaux, ressources et licences.
  Amener les cadres de résultat hors écran dans la zone visible avant les contrôles
  des widgets Chromium/Firefox, avec les mêmes limites de temps/mémoire et assertions
  sur les pixels.
- Compléter le build par les oracles indépendants Reader/Codecs/images/fontes,
  les outils JPEG 2000 et Poppler épinglés, les échantillons compactés/16 bits et
  les témoins couleur/alpha/ICC sous Chromium/Firefox. Distinguer preuves
  normatives, limites connues des oracles et comparaisons entre décodeurs.
- Valider navigation bilingue, provenance API/source, téléchargements, aperçus
  PDF, démo intégrée et anciennes adresses de compatibilité avant de publier
  la documentation avec sa version indépendante.

## [0.12.0] - 2026-10-28

- Intégrer la démo PDF vers HTML publiée indépendamment et sept exemples reproductibles, en conservant les versions des packages PHP. Sélectionner la démo par son propre tag annoté et son commit source exact.
- Ajouter les captures comparées du PDF source et du HTML dérivé directement aux guides anglais/français de présentation, graphiques et signatures, avec liens vers les exemples interactifs, PDF et code PHP. Consigner la provenance réelle des captures Chromium.
- Convertir les PDF locaux dans un Worker PHP/WASM borné, avec des ressources inventoriées et servies localement. Conserver les documents importés dans la mémoire du navigateur, isoler les aperçus et autoriser uniquement le script de bibliothèque adressé par contenu de l’exemple de réinitialisation vérifié, via son hash CSP exact.
- Vérifier les ressources et hashes du runtime, ses deux variantes navigateur, la navigation bilingue, les comparaisons des guides et les comportements Chromium/Firefox, en complément des contrôles complets API, PDF, liens et compatibilité des anciennes adresses.

## [0.11.0] - 2026-10-28

- Sélectionner PDF vers HTML 0.6.0 publié au commit exact de son tag annoté, en conservant les versions indépendantes du core, Reader, images/fontes et OpenType.
- Publier le guide complet des signatures anglais/français, le registre des clauses actualisé et l’exemple exécutable à certificat explicite. Expliquer le rendu des apparences, les corrections de contenu/formulaire/attributs et la distinction entre intégrité, confiance et permissions des changements ultérieurs.
- Exécuter les oracles indépendants d’apparences et de signatures dans la construction documentaire complète ; conserver les preuves PHP et navigateur dans la qualification du package HTML. Vérifier toutes les pages API, routes, liens source, aperçus PDF et adresses de compatibilité.

## [0.10.1] - 2026-10-28

- Sélectionner PDF vers HTML 0.5.1 publié au commit exact de son tag annoté et actualiser les installations, packages, tutoriels et liens source anglais/français.
- Publier le guide corrigé du placement MathML : les déclarations display dérivées de Layout préservent la mise en forme mathématique native ; Placement Block sur la racine utilise `math[display="block"]`, en conservant la priorité du CSS explicite et du display MathML de l’auteur.
- Relier les preuves par clause et la procédure Chromium/Firefox du module, sans assimiler les cas de placement vérifiés à une conformité générale du rendu ou de l’accessibilité. Conserver les autres versions sélectionnées et toutes les anciennes routes et téléchargements.

## [0.10.0] - 2026-10-15

- Sélectionner core 0.11.0, Reader 0.6.0, images/fontes 0.1.12, HTML 0.5.0 et OpenType indépendant 0.3.0 publiés, aux commits exacts des tags annotés.
- Actualiser les guides anglais/français de révisions protégées, authentification, EC3, polices et migration. Ajouter les guides Reader historique physique/politique structurelle et huit guides OpenType axes/métadonnées/métriques/contours à la navigation et aux contrôles de routes.
- Exécuter les oracles indépendants Reader historique et UR3 chiffré dans le build complet, avec les validations mises à jour des signatures, certificats, HTML et rendus. Conserver les mécanismes hors périmètre et limites des outils indépendants.
- Distinguer provenance documentaire et packages ; conserver chaque ancienne route et téléchargement binaire avec le build de compatibilité.

## [0.9.2] - 2026-10-15

- Sélectionner les versions publiées core 0.10.0, Reader 0.5.1, modules
  images/fontes 0.1.11 et PDF vers HTML 0.4.2 ; conserver OpenType 0.2.0
  indépendant et les commits de source exacts.
- Ajouter le guide bilingue des révisions protégées et le tutoriel 37 depuis
  le véritable exemple `protected-form-fill.php` : remplissage Tx/Ch/Btn borné,
  verrous FieldMDP historiques, remplacement isolé de Tx, annotations P3 listées
  et contrôles explicites d’autorité/sauvegarde UR3 par opération. Préserver les
  limites modèles, texte enrichi, chaînes externes, nouvelles ressources et PKI.
- Exécuter l’oracle indépendant des permissions incrémentales dans chaque build
  complet ; conserver preuves CMS/pixels et divergences de politique pyHanko
  dans les rapports privés sans en déduire conformité générale ni confiance.
- Sélectionner un seul Reader installé par version et commits source/dist
  exacts du lock et de l’installation, avec préférence core et repli HTML pour
  les anciens pins. Réutiliser cette source pour API, guides, tutoriel et oracles.
  Vérifier HTML séparément contre son lock inchangé core 0.9.1/Reader 0.5.0 ;
  consigner les deux provenances réelles sans réécrire les locks publiés.

## [0.9.1] - 2026-10-15

- Documenter le lecteur 0.5.0 et PDF vers HTML 0.4.1 depuis leurs commits publiés,
  en conservant les sélections indépendantes du core, des images/fontes et d'OpenType.
- Publier le guide d'authentification par clé publique du lecteur en anglais et
  français, avec navigation, routes obligatoires et liens de langue réciproques.
- Expliquer Adobe.PubSec s3/s4/s5, les clés indépendantes des filtres, l'accès EFOpen
  différé, les permissions destinataire authentifiées et le MAC DefaultCryptFilter.
  Corriger les limites obsolètes MAC source/clé publique tout en conservant les
  frontières de confiance des signatures, réparation, rendu et application des droits.
- Exécuter l'oracle indépendant CMS/clés/MAC du lecteur, quatre cas d'alias
  physiques/métadonnées, deux cas EFF implicites et les six sources de l'oracle
  HTML de clé publique pendant le build complet. Garder credentials générés et
  PDF hostiles privés à la validation.
- Préserver les instructions de dépendances d'intégrité source verrouillées dans
  les deux guides de build et installer explicitement les dépendances hashées
  des oracles du lecteur sélectionné.

## [0.9.0] - 2026-10-15

- Documenter les versions publiées du core 0.9.1, du lecteur 0.4.1, des modules
  images/fontes 0.1.10, d’OpenType indépendant 0.2.0 et de PDF vers HTML 0.4.0
  depuis leurs commits exacts ; actualiser les installations dans les deux langues.

- Expliquer la préparation ordonnée des valeurs de codes-barres, la compression
  globale avant répartition, l'association exacte aux PMD et les apparences
  natives sur tout le widget. Conserver la capacité d'encodage explicite, les
  budgets, la frontière de l'oracle à image de test et l'ambiguïté Adobe du widget unique.
- Documenter appartenance/réponses/popups des annotations effectives, cibles
  d'actions distantes et contrôles des mesures rectilignes ; séparer les 84 tests
  et 132 assertions des 197 règles intrinsèques et de la couverture normative incomplète.
- Expliquer `AP` natif obligatoire en PDF 2.0, les exceptions de point et de
  sous-type, les apparences normales Form/états et le cas licite d'un `AS` sans état correspondant.
  Ajouter les revues EC3 exactes approuvées #22/#124 aux quatre précédentes et
  exécuter l'oracle indépendant huit PDF/onze refus/28 pixels pendant la construction.
  Conserver l'interdiction d'AP de Projection lorsqu'une dimension du rectangle est nulle.
- Expliquer l'inspection des véritables glyphes Type 3 natifs sélectionnés, les
  modes 3/7, les différences Poppler indépendantes et les constats contextuels
  de dépréciation WTPDF. Distinguer recommandations, erreurs et preuves opaques/de contexte en attente.
- Ajouter le guide bilingue du MAC PDF source à la navigation du lecteur et aux
  routes obligatoires. Décrire couverture exacte du fichier courant, politique
  d'intégrité requise, composition immuable, limites de cadrage et frontière signature/PKI.
- Expliquer valeurs nulles optionnelles et chaînes physiques bornées de
  références indirectes, avec restrictions des flux d'objets et maintien du
  caractère direct des valeurs de sécurité non nulles.
- Documenter la conservation des identités terminales Encrypt/Root/Metadata et
  des credentials inchangés dans le lecteur 0.4.1 ; exécuter ses onze cas de
  métadonnées, dont quatre alias chiffrés indépendants et les limites des lecteurs de haut niveau.
- Mettre à jour le tutoriel 35 pour l'intégrité MAC source exigée et la migration
  `AuthenticationProvider` 0.4 : politique effective en argument et retour d'un
  `ReadDocument` authentifié, avec contrôle commun source/permissions avant adaptation.
  Exécuter l'oracle MAC/HTML5 indépendant et l'exemple authentifié complet.
- Exécuter les oracles indépendants des codes-barres, usages Type 3 et MAC source
  pendant la construction complète de la documentation, avec résultats privés au build.

## [0.8.0] - 2026-10-15

- Documenter le core 0.8.1, le lecteur 0.3.1, les modules images/fontes 0.1.9,
  OpenType indépendant 0.2.0 et PDF vers HTML 0.3.2 dans les deux langues.
- Ajouter un guide des audits de source avec les 197 règles de dictionnaires
  exécutables, quatre revues EC3 exactes, le placement corrigé des apparences et
  le classement de 65 errata Adobe. Préserver différences d'édition et mécanismes incomplets.
- Ajouter le tutoriel 36 avec le véritable exemple de caviardisation conservatrice,
  ses deux pages PDF, la destruction dans un nouveau fichier, les ressources
  partagées et les frontières des entrées refusées.
  Expliquer bornes transformées, dépendances transitives des masques, métadonnées
  de fontes, types/contextes et budgets des arêtes vérifiés par des lecteurs indépendants.
- Expliquer la provenance native du core 0.8.1, les signatures historiques
  vérifiées, la garde du delta complet et les opérations bornées de signature,
  DSS et horodatage. Garder UR, changements généraux de formulaire/annotation et
  confiance PKI hors de ces opérations prouvées. Documenter le domaine des fontes
  du caviardage et le refus des données CID inutilisées sur les polices simples,
  en préservant les identifiants CID légitimes.
- Exposer l'authentification lecteur/HTML et le positionnement/variations OpenType
  dans les menus ; expliquer permissions vérifiées et domaines de fontes/composition incomplets.
- Expliquer les métadonnées claires limitées au catalogue, EFF indirect,
  les clés V4 fixes et Identity réservé du lecteur 0.3.1 avec sept cas d'oracle supplémentaires.
- Documenter la comparaison XML native optionnelle WTPDF et son parseur borné.
- Exécuter les oracles des liens EC3, de caviardisation destructive et
  d'authentification HTML native pendant la construction complète, en séparant
  les sorties de validation privées des ressources de tutoriels publiées.

## [0.7.0] - 2026-10-15

- Documenter PDF-to-HTML 0.2.1 et le lecteur PDF 0.2.3 depuis leurs tags publiés
  et commits exacts ; conserver les versions du core, des images, des fontes
  et d'OpenType qui n'ont pas changé.
- Publier sept guides de dérivation HTML en anglais et en français, dont un
  registre clause par clause de Deriving HTML 1.2, la construction des politiques
  et l'export graphique avec un moteur de rendu fourni par l'application.
- Enrichir le tutoriel 35 avec des exemples exécutables d'export de figure et
  de remise à zéro des champs, les frontières source/runtime explicites et
  le véritable résultat HTML sémantique.
- Exécuter les contrôles indépendants du module sur les glyphes, images inline,
  CCITT, graphiques, HTML5 et le runtime Node pendant la construction du site.
  Préserver les octets originaux, la provenance des packages, chaque téléchargement
  public et les anciennes adresses.
- Aligner commandes d'installation, liens API et instructions de contribution
  dans les deux langues sur les versions sélectionnées.
- Expliquer le clipping, la transparence et les viewports en coordonnées page
  des Form/OBJR racines, vérifiés par des programmes PDF et pixels Poppler indépendants.

## [0.5.1] - 2026-10-14

- Documenter le core 0.7.1 et le lecteur PDF 0.1.9 depuis leurs sources publiées ;
  conserver les modules images/fontes 0.1.8 et OpenType indépendant 0.1.0.
- Lire les dix-huit PDF de référence originaux depuis le dossier
  `resources/reference-documents/` du core, avec leurs noms et octets vérifiés.
- Actualiser guides anglais/français, tutoriels, provenance API et liens vers
  le dépôt en préservant chaque URL publique de téléchargement et ancre de page.

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
