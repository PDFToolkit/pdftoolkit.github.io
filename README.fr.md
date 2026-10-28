# Documentation PDFToolkit

[English](README.md) · [Français](README.fr.md)

Le site s'ouvre en [anglais](https://pdftoolkit.github.io/) par défaut ; la
[documentation française complète](https://pdftoolkit.github.io/fr/) est
accessible depuis le sélecteur de langue de chaque page.

La documentation commune de PDFToolkit est publiée à **https://pdftoolkit.github.io/**.
Elle comprend le core, le lecteur PDF, les convertisseurs d'images et de polices,
avec leurs guides, la référence API complète, des tutoriels, les sources PHP
exécutables et des aperçus PDF. Commencer par
[le guide des packages](https://pdftoolkit.github.io/fr/guides/modules.html)
ou le module nécessaire :

- [Core](https://pdftoolkit.github.io/fr/modules/core/)
- [Lecteur PDF](https://pdftoolkit.github.io/fr/modules/reader/)
- [Images](https://pdftoolkit.github.io/fr/modules/images/)
- [Polices](https://pdftoolkit.github.io/fr/modules/fonts/)
- [OpenType](https://pdftoolkit.github.io/fr/modules/opentype/)
- [Codecs](https://pdftoolkit.github.io/fr/modules/codecs/)
- [PDF vers HTML](https://pdftoolkit.github.io/fr/modules/to-html/)

Ce dépôt contient les textes communs, les assets du site, le générateur et le
workflow de déploiement. Le code PHP, les exemples exécutables, les fixtures
et les documents de spécification originaux restent dans
[leurs dépôts de packages](https://github.com/orgs/PDFToolkit/repositories).
Les guides des modules sont publiés ici à partir de leurs sources versionnées.
Le core regroupe ses dix-huit PDF de référence originaux dans
`resources/reference-documents/`, avec leurs noms et octets d’origine.
Les téléchargements publics des références conservent leurs URL existantes.

Reader 0.7 ajoute l’import explicite de graphes, CCITT borné et le décodage d’images natif/PHP. Images 0.2 ajoute toutes les profondeurs PNG statiques légales, Adam7, les couleurs calibrées/ICC et JPEG YCCK. Fonts 0.2 relie les programmes TrueType/CFF statiques au layout OpenType explicite ; OpenType 0.4 ajoute collections, formats cmap Unicode et plages de fonctionnalités. Les [guides de couverture](https://pdftoolkit.github.io/fr/guides/coverage.html) distinguent ces mécanismes du rendu, du shaping Unicode automatique et de la confiance des signatures.

## Installer les bibliothèques

Les bibliothèques PHP sont disponibles sur Packagist. Installer le core avec
Composer :

```sh
composer require "roukmoute/pdf:^0.12"
```

Les versions documentées sont le core **0.12**, Reader **0.7**, Images et Fonts **0.2**, OpenType **0.4**, Codecs **0.1** et PDF vers HTML **0.7**. Elles nécessitent **PHP 8.3 ou supérieur en 64 bits** ; leurs validations couvrent PHP 8.3, 8.4 et 8.5. Les versions et révisions exactes sont fixées dans le manifeste de sources. OpenType et Codecs ne dépendent pas du core PDF.

Choisir les modules optionnels selon les fichiers traités par l'application :

- [Core : roukmoute/pdf](https://packagist.org/packages/roukmoute/pdf)
- [Lecteur PDF : pdftoolkit/pdf-reader](https://packagist.org/packages/pdftoolkit/pdf-reader)
- [Images : pdftoolkit/pdf-images](https://packagist.org/packages/pdftoolkit/pdf-images)
- [Polices : pdftoolkit/pdf-fonts](https://packagist.org/packages/pdftoolkit/pdf-fonts)
- [OpenType: pdftoolkit/opentype](https://packagist.org/packages/pdftoolkit/opentype)
- [Codecs: pdftoolkit/pdf-codecs](https://packagist.org/packages/pdftoolkit/pdf-codecs)
- [PDF vers HTML : pdftoolkit/pdf-to-html](https://packagist.org/packages/pdftoolkit/pdf-to-html)

Les modules images/fontes/lecteur installent le core. Fonts installe aussi le modèle OpenType indépendant ; PDF vers HTML installe Reader. Codecs est une bibliothèque de décodeurs en PHP pur distincte. Au décodage explicite d’une image, Reader choisit d’abord un profil natif Ghostscript/prlimit qualifié, puis la bibliothèque PHP installée si la capacité manque. Sans moteur disponible, il indique une commande Composer utilisable sans installer silencieusement de dépendance. Le [guide des codecs image](https://pdftoolkit.github.io/fr/modules/reader/image-codecs.html) précise profils, budgets et métadonnées.

PDF vers HTML 0.7 dérive le contenu sémantique des PDF balisés avec vérification
des associations structurelles, Unicode, images, tableaux, navigation et champs.
Son [registre des clauses](https://pdftoolkit.github.io/fr/modules/to-html/requirements.html)
relie la référence conservée aux décisions exécutables et aux tests indépendants.
Les [profils et politiques](https://pdftoolkit.github.io/fr/modules/to-html/policies.html)
distinguent sortie sémantique, actions ResetForm/SubmitForm optionnelles et scripts
PDF de confiance. Le [guide des graphiques](https://pdftoolkit.github.io/fr/modules/to-html/graphics.html)
explique l'export PDF isolé et le moteur de rendu fourni par l'application.
Rendu, authentification et codecs non pris en charge restent des capacités
explicites ; le profil par défaut n'exécute aucun script PDF ni action de formulaire.

PDF vers HTML 0.7 préserve la mise en forme MathML native lors du mapping de
Placement Layout, y compris pour les classes partagées. Le CSS explicite et le
display MathML de l’auteur gardent leur priorité. Le [guide de couverture MathML](https://pdftoolkit.github.io/fr/modules/to-html/coverage.html#placement-mathml-et-rendu-navigateur)
explique les règles et les contrôles indépendants Chromium/Firefox.

PDF vers HTML 0.6 ajoute le rendu réutilisable des apparences de boutons, la
[validation explicite des signatures](https://pdftoolkit.github.io/fr/modules/to-html/signatures.html)
liée à la source et des popovers natifs de statut. Le certificat choisi vérifie
l’intégrité mathématique d’une révision PDF complète ; confiance, révocation et
permissions des modifications ultérieures restent distinctes. Les corrections
de contenu, de listes/attributs et de formulaires sont reliées au registre des
clauses bilingue et contrôlées avec des outils indépendants.

Le lecteur 0.4 et PDF vers HTML 0.4 proposent une authentification native par mot
de passe sur activation explicite, avec permissions user/owner vérifiées. Les
[guides du lecteur](https://pdftoolkit.github.io/fr/modules/reader/authentication.html)
et [du HTML](https://pdftoolkit.github.io/fr/modules/to-html/authentication.html)
expliquent credentials, filtres, refus et responsabilités du viewer. Le lecteur
0.5 propose aussi une [authentification Adobe.PubSec](https://pdftoolkit.github.io/fr/modules/reader/public-key-authentication.html)
explicite, avec clés indépendantes par filtre, droits destinataire authentifiés
et vérification du MAC source. Déchiffrer par certificat ne prouve pas la
confiance des signatures. OpenType 0.2
fournit indépendamment GSUB/GPOS/GDEF et des coordonnées de variation explicites ;
son [guide de positionnement](https://pdftoolkit.github.io/fr/modules/opentype/positioning.html)
précise les ajustements natifs et les limites de composition et de contours.

## Guides et exemples PDF 2.0

Le [guide PDF 2.0](https://pdftoolkit.github.io/fr/guides/pdf-2-0.html) et
le [guide des spécifications complémentaires](https://pdftoolkit.github.io/fr/guides/pdf-2-0-bundle.html)
expliquent ISO 32000-2:2020 EC3, les chiffrements et signatures modernes, PDF MAC,
les métadonnées/déclarations, les fichiers associés, les parties de document et
les rôles de structure qualifiés, les horodatages documentaires, les preuves
DSS/VRI, les mesures géospatiales et les destinations de structure.
Les [37 tutoriels](https://pdftoolkit.github.io/fr/tutorials/)
comprennent des exemples exécutables et leurs véritables aperçus PDF. L'audit
WTPDF distingue les contrôles mécaniques et les preuves encore nécessaires ;
il ne certifie ni l'accessibilité ni PDF/UA.

Le core 0.8 ajoute [197 règles de dictionnaires exécutées et corrections vérifiées](https://pdftoolkit.github.io/fr/guides/source-audits.html),
une [caviardisation appliquée](https://pdftoolkit.github.io/fr/tutorials/36-caviardisation.html)
conservatrice avec nouveau fichier PDF et la comparaison XML WTPDF optionnelle
du texte enrichi. Les guides distinguent le classement de 65 errata Adobe d'une
implémentation complète et conservent les exigences EC3 non examinées, politiques
documentaires et preuves externes ou humaines.
Le core 0.8.1 ajoute des protections de provenance native et du delta complet
pour la signature/maintenance incrémentale bornée, ainsi que le contrôle du
domaine des fontes du caviardage. Le [guide de sécurité](https://pdftoolkit.github.io/fr/guides/securite.html)
précise les opérations permises, refus et migration de provenance dans l’exécution.
Le core 0.10.0 ajoute remplissage natif borné, annotations P3 et autorité UR3
par mise à jour ; son [guide](https://pdftoolkit.github.io/fr/guides/revisions-protegees.html) et le
[tutoriel 37](https://pdftoolkit.github.io/fr/tutorials/37-remplissage-protege.html) expliquent
les opérations couvertes, frontières figées des apparences et limites des oracles indépendants.

Les ajouts reliés aux sources couvrent aussi les messages ordonnés des
codes-barres et leurs apparences natives, les relations effectives entre
annotations/actions/mesures rectilignes, l'utilisation des glyphes Type 3
sélectionnés et les recommandations contextuelles de dépréciation WTPDF.
La vérification du MAC PDF source a son [guide lecteur](https://pdftoolkit.github.io/fr/modules/reader/source-mac.html) et sa politique explicite
d'entrée obligatoirement protégée. Les guides conservent les frontières de
symbologie, rendu, contenu opaque et confiance ; les contrôles fournissent des
preuves pour ces opérations sans établir une conformité PDF complète.

## Sources reproductibles

[resources/sources.json](resources/sources.json) consigne les versions stables
sélectionnées des packages et leurs commits Git exacts. La construction vérifie
que chaque tag désigne le commit enregistré et que les modules optionnels
installés lui correspondent. Les liens de source API utilisent ces commits.
Les liens de source documentaire utilisent le commit propre à ce dépôt.

## Construire et contribuer

Consulter [le guide de construction](docs/site/README.md) pour les commandes
locales et les prérequis. Le workflow produit les vrais PDF d'exemple, les
contrôle avec des lecteurs indépendants, rend toutes leurs pages, génère
chaque fiche API et valide l'ensemble du site.
Il vérifie aussi les fixtures de glyphes et d'images inline/fax du module HTML,
le HTML sémantique réel, les graphiques isolés, leurs contextes et les apparences
de widgets avec HTML5/pypdf/Poppler, les cibles de navigation, l’intégrité des
signatures source, le runtime Node et les exemples d’export de figure, de reset
sûr et de certificat explicite. Ces sorties de validation supplémentaires
restent dans l'espace de construction ; seuls les artefacts documentés des
tutoriels sont publiés.

Lorsqu'une version de package est publiée, mettre à jour son épinglage de source,
valider le site et publier une nouvelle version de documentation. Les
installations restent indépendantes : la génération du site n'ajoute aucun
module aux applications utilisant le core.

## Adresses existantes

Les URL existantes sous `https://pdftoolkit.github.io/pdf/` restent prises en
charge par le déploiement de compatibilité du core. La navigation HTML conserve
son chemin, sa requête et son fragment ; les URL PDF et autres fichiers binaires
continuent de servir leurs octets réels.

La documentation a commencé dans [PDFToolkit/pdf](https://github.com/PDFToolkit/pdf).
Les contenus communs ont été transférés depuis le core 0.5.2, commit
`ad1384a1400f9b13614e08aa352410b0af4b1e9c`, avec la [licence MIT](LICENSE)
conservée.
