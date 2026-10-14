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
- [PDF vers HTML](https://pdftoolkit.github.io/fr/modules/to-html/)

Ce dépôt contient les textes communs, les assets du site, le générateur et le
workflow de déploiement. Le code PHP, les exemples exécutables, les fixtures
et les documents de spécification originaux restent dans
[leurs dépôts de packages](https://github.com/orgs/PDFToolkit/repositories).
Les guides des modules sont publiés ici à partir de leurs sources versionnées.
Le core regroupe ses dix-huit PDF de référence originaux dans
`resources/reference-documents/`, avec leurs noms et octets d’origine.
Les téléchargements publics des références conservent leurs URL existantes.

## Installer les bibliothèques

Les bibliothèques PHP sont disponibles sur Packagist. Installer le core avec
Composer :

```sh
composer require "roukmoute/pdf:^0.7.1"
```

Les versions documentées sont le core **0.7.1**, le lecteur **0.2.3**, les modules
images/fontes **0.1.8**, OpenType indépendant **0.1.0** et PDF vers HTML **0.2.1**. Elles nécessitent **PHP 8.3 ou supérieur**
et sont vérifiées sous PHP 8.3, 8.4 et 8.5. Le core **0.7** exige aussi PHP en
64 bits ; OpenType reste indépendant du core PDF.

Choisir les modules optionnels selon les fichiers traités par l'application :

- [Core : roukmoute/pdf](https://packagist.org/packages/roukmoute/pdf)
- [Lecteur PDF : pdftoolkit/pdf-reader](https://packagist.org/packages/pdftoolkit/pdf-reader)
- [Images : pdftoolkit/pdf-images](https://packagist.org/packages/pdftoolkit/pdf-images)
- [Polices : pdftoolkit/pdf-fonts](https://packagist.org/packages/pdftoolkit/pdf-fonts)
- [OpenType: pdftoolkit/opentype](https://packagist.org/packages/pdftoolkit/opentype)
- [PDF vers HTML : pdftoolkit/pdf-to-html](https://packagist.org/packages/pdftoolkit/pdf-to-html)

Les modules images/fontes/lecteur installent le core comme dépendance. PDF vers HTML ajoute la dérivation sémantique et installe aussi le lecteur. OpenType possède son propre modèle objet et s’installe sans dépendance PDF. Le guide des packages explique
leurs commandes Composer et les versions prises en charge.

PDF vers HTML 0.2.1 dérive le contenu sémantique des PDF balisés avec vérification
des associations structurelles, Unicode, images, tableaux, navigation et champs.
Son [registre des clauses](https://pdftoolkit.github.io/fr/modules/to-html/requirements.html)
relie la référence conservée aux décisions exécutables et aux tests indépendants.
Les [profils et politiques](https://pdftoolkit.github.io/fr/modules/to-html/policies.html)
distinguent sortie sémantique, actions ResetForm/SubmitForm optionnelles et scripts
PDF de confiance. Le [guide des graphiques](https://pdftoolkit.github.io/fr/modules/to-html/graphics.html)
explique l'export PDF isolé et le moteur de rendu fourni par l'application.
Rendu, authentification et codecs non pris en charge restent des capacités
explicites ; le profil par défaut n'exécute aucun script PDF ni action de formulaire.

## Guides et exemples PDF 2.0

Le [guide PDF 2.0](https://pdftoolkit.github.io/fr/guides/pdf-2-0.html) et
le [guide des spécifications complémentaires](https://pdftoolkit.github.io/fr/guides/pdf-2-0-bundle.html)
expliquent ISO 32000-2:2020 EC3, les chiffrements et signatures modernes, PDF MAC,
les métadonnées/déclarations, les fichiers associés, les parties de document et
les rôles de structure qualifiés, les horodatages documentaires, les preuves
DSS/VRI, les mesures géospatiales et les destinations de structure.
Les [35 tutoriels](https://pdftoolkit.github.io/fr/tutorials/)
comprennent des exemples exécutables et leurs véritables aperçus PDF. L'audit
WTPDF distingue les contrôles mécaniques et les preuves encore nécessaires ;
il ne certifie ni l'accessibilité ni PDF/UA.

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
le HTML sémantique réel, les graphiques isolés et leurs contextes de rendu avec
HTML5/pypdf/Poppler, les cibles de navigation, le runtime Node et les exemples
d'export de figure et de reset sûr. Ces sorties de validation supplémentaires
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
