# PDF

Un modèle objet explicite de **PDF 1.7 et PDF 2.0**, dont ISO 32000-2:2020 EC3 et ses spécifications complémentaires, pour **PHP 8.3 ou supérieur en 64 bits**.

Cette bibliothèque représente la syntaxe et les structures du format, jusque dans ses noms, nombres, références, entrées de dictionnaire et opérateurs. Elle ne cherche pas à fournir une API de mise en page. Une bibliothèque de plus haut niveau peut construire ces objets et conserver le contrôle de leur composition.

Le projet fait partie de l'organisation [PDFToolkit](https://github.com/PDFToolkit). Le dépôt [PDFToolkit/pdf](https://github.com/PDFToolkit/pdf) est le **core** : il contient les objets et mécanismes décrits par la norme Adobe/ISO, dont l'écriture. La lecture de PDF externes, la conversion des fichiers PNG/JPEG et l'analyse des fontes TrueType appartiennent à trois packages optionnels. Chaque module dépend du core ; installer le core pour générer un PDF n'installe aucun de ces modules.

La [documentation en ligne](https://pdftoolkit.github.io/) réunit les guides, la référence de tous les composants et les tutoriels avec leur code et leurs PDF consultables. Le dépôt [PDFToolkit/pdftoolkit.github.io](https://github.com/PDFToolkit/pdftoolkit.github.io) en conserve les textes, les assets et les outils de construction. Cette documentation présente les versions publiées du core et des modules sélectionnées dans le manifeste de sources. Le commit de documentation est indiqué séparément des versions des packages.

La série `0.x` est destinée aux développeurs qui souhaitent construire et explorer ce modèle. Avant la version `1.0`, une nouvelle version mineure peut modifier les noms et signatures ; les versions correctives conservent l'API de leur série. Le périmètre implémenté et les limites figurent dans [la couverture de la spécification](specification.md).

Les définitions se fondent sur les documents Adobe/ISO `PDF32000_2008.pdf` et `adobe_supplement_iso32000.pdf`, conservés dans le dépôt du core. Le [guide du supplément](adobe-supplement.md) explique les extensions Adobe du PDF 1.7, niveau 3, leur provenance et leurs mécanismes. Le [guide des références Adobe](adobe-references.md) présente aussi la référence de 2006, ses errata, l'addendum de caviardisation et leur portfolio. Les références Adobe archivées dans le core sont conservées avec leur nom et leurs octets d'origine ; les quatre références archivées sont exclues des archives Composer.

Le core 0.8.0 étend l'[écriture PDF 2.0](pdf-2-0.md) avec les [spécifications complémentaires](pdf-2-0-bundle.md) : AES-CBC R=6, AES-GCM R=7, condensats/signatures modernes, PDF MAC, XMP/déclarations, propriété des métadonnées, fichiers associés, parties de document et rôles de structure qualifiés. Les onze originaux du bundle gardent leurs noms fournis, octets et empreintes de source dans le core ; ils sont exclus des archives Composer. La PDF Association fournit les [normes sponsorisées](https://www.pdfa.org/sponsored-standards/). WTPDF propose un audit partiel, sans certification ; un catalogue de définitions ne permet pas de déduire une conformité complète PDF 2.0 ou PDF/A, PDF/X et PDF/UA.

## Installation

Le core **0.11.0** nécessite PHP 8.3 ou supérieur en 64 bits et les extensions `ctype`, `iconv` et `zlib`. Les backends AES et CMS sont optionnels et nécessitent `openssl`. Le package [`roukmoute/pdf`](https://packagist.org/packages/roukmoute/pdf) est disponible sur Packagist. Depuis le projet consommateur :

```sh
composer require "roukmoute/pdf:^0.11.0"
```

Les modifications d'API figurent dans le [changelog](../CHANGELOG.md) et le
[guide de migration 0.11](migration-0.11.md). Conserver le `composer.lock` du
projet consommateur pour fixer les versions installées.

## Modules optionnels

| Package | Responsabilité |
| --- | --- |
| [`pdftoolkit/pdf-reader`](https://pdftoolkit.github.io/modules/reader/index.html) | Lire les objets et révisions d'un PDF externe, vérifier ses pages et leur héritage, inspecter leurs flux. |
| [`pdftoolkit/pdf-images`](https://pdftoolkit.github.io/modules/images/index.html) | Inspecter des fichiers JPEG et décoder des fichiers PNG en objets image du core. |
| [`pdftoolkit/pdf-fonts`](https://pdftoolkit.github.io/modules/fonts/index.html) | Analyser un TrueType statique et préparer ses métriques et correspondances pour les objets de police du core. |

Le lecteur PDF **0.6.0** exige le core `^0.9 || ^0.10 || ^0.11` ; les modules images/fontes **0.1.12** conservent leurs anciennes séries prises en charge jusqu’à 0.11 sous PHP 8.3 ou supérieur. Le lecteur 0.6.0 prend en charge la syntaxe PDF 1.0–2.0, les chaînes UTF-8 PDF 2.0, les références indirectes chaînées bornées, l’authentification native explicite par mot de passe ou clé publique et la vérification du MAC source ; la conversion d’images reste PNG/JPEG et celle des fontes reste TrueType statique. Les trois packages sont disponibles sur Packagist : [lecteur](https://packagist.org/packages/pdftoolkit/pdf-reader), [images](https://packagist.org/packages/pdftoolkit/pdf-images) et [fontes](https://packagist.org/packages/pdftoolkit/pdf-fonts). Par exemple, pour importer des fichiers image avec le core 0.11.0 :

```sh
composer require "roukmoute/pdf:^0.11.0" "pdftoolkit/pdf-images:^0.1.12"
```

Le module installe le core avec sa contrainte stable. Le [guide des packages](packages.md) explique leur frontière, les installations et le fonctionnement du lecteur. Conserver le `composer.lock` de l'application pour fixer les versions et les commits utilisés.


Le [modèle OpenType indépendant](https://pdftoolkit.github.io/fr/modules/opentype/index.html), [`pdftoolkit/opentype`](https://packagist.org/packages/pdftoolkit/opentype), représente les tables de fonte, les correspondances Unicode, le layout GSUB/GPOS, les métriques variables et les contours TrueType/CFF/CFF2 non hintés. Il ne dépend d’aucun package PDF. Sa [couverture](https://github.com/PDFToolkit/opentype/blob/v0.3.0/docs/fr/coverage.md) détaille les mécanismes présents et ceux restant à construire.

```sh
composer require "pdftoolkit/opentype:^0.3.0"
```

## Développement et vérifications

Depuis un clone du dépôt [PDFToolkit/pdf](https://github.com/PDFToolkit/pdf) :

```sh
export COMPOSER_ROOT_VERSION=0.11.x-dev
composer install
composer check
php examples/hello-world.php hello-world.pdf
php examples/object-stream.php object-stream.pdf
```

Le code de production dépend uniquement de PHP et de ces trois extensions. PHPUnit 12, PHPStan, PHP-CS-Fixer et les modules utilisés par les exemples et la documentation sont des dépendances de développement verrouillées dans `composer.lock`. Leur présence dans ce checkout n'ajoute aucune dépendance de production aux applications utilisant le core. La CI du core exécute les tests et valide les PDF d'exemple sous PHP 8.3, 8.4 et 8.5. Les tests échouent aussi sur les dépréciations et avertissements PHP. Le [changelog](../CHANGELOG.md) décrit chaque version publiée.

Pour valider ce checkout, y compris depuis son tag, définir
`COMPOSER_ROOT_VERSION=0.11.x-dev` avant `composer install`. Cette variable identifie
le core courant comme appartenant à la série 0.10 acceptée par les modules. Les
dépendances de développement utilisent les modules PDF publiés, dont les versions
et les sources exactes sont verrouillées dans `composer.lock`. Les CI définissent
également cette variable pour les branches, les tags et les pull requests.

## Construction objet par objet

```php
$helvetica = new Type1Font(StandardFont::Helvetica);
$resources = new ResourceDictionary(
    new Font(new DictionaryType(
        new Entry(new NameType('F1'), new IndirectReference($helvetica)),
    )),
);
$contents = new StreamObject(new ContentStreams(
    new BeginTextObject(),
    new SetTextFontAndSize(new NameType('F1'), new NumericType(18)),
    new MoveTextPosition(new NumericType(72), new NumericType(720)),
    new ShowText(new LiteralString('Super !')),
    new EndTextObject(),
));
$page = new PageObject(
    new Rectangle(new NumericType(0), new NumericType(0), new NumericType(612), new NumericType(792)),
    $resources,
    $contents,
);
$pages = (new PageTreeNode())->addKid($page);
$catalog = new DocumentCatalog($pages);
$file = new FileStructure(new FileHeader('1.7'), new FileBody($catalog));
$file->writeTo('hello-world.pdf');
```

L'exemple complet, avec les imports et les métadonnées, se trouve dans [`examples/hello-world.php`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/examples/hello-world.php).

## Tutoriels et recettes

Les [34 tutoriels](tutorials/README.md) accompagnent chaque script d’une explication, d'un aperçu et de variantes à essayer. Les commentaires du code relient les objets aux instructions et structures du PDF.

| Sujet | Ce que l'exemple explique |
| --- | --- |
| [Premier document](tutorials/01-first-document.md) | Police, ressources, contenu, page, catalogue et informations documentaires. |
| [Pages et texte](tutorials/02-pages-and-text.md) | Héritage des ressources, plusieurs pages, positions et interligne. |
| [Dessin](tutorials/03-graphics.md) | Couleurs, chemins, courbes et transformations de l'état graphique. |
| [Navigation](tutorials/04-navigation.md) | Signets hiérarchiques et destinations vers les pages. |
| [Liens](tutorials/05-links.md) | Annotations cliquables internes et actions URI. |
| [Images](tutorials/06-images.md) | Image XObject, image inline, octets RGB et filtres. |
| [Dégradé](tutorials/07-gradient.md) | Fonction PDF de type 2 et shading axial. |
| [Objets compressés](tutorials/08-object-stream.md) | Flux de contenu, conteneur d'objets et références croisées. |
| [Police TrueType et Unicode](tutorials/09-embedded-font.md) | Programme incorporé, CID, largeurs et correspondance ToUnicode. |
| [Images JPEG et PNG](tutorials/10-image-files.md) | Couleurs, décodage PNG, JPEG conservé et masque de transparence. |
| [Révisions incrémentales](tutorials/11-incremental-update.md) | Remplacements explicites, octets historiques conservés et chaînage des xref. |

La séquence PDF 2.0 ajoute [UTF-8 et les fichiers associés](tutorials/27-pdf20-associated-files.md), [les métadonnées, déclarations et parties de document](tutorials/28-pdf20-metadata-declarations.md), [les enveloppes de contenus chiffrés](tutorials/29-pdf20-encrypted-payload.md), [les rôles de structure qualifiés et rapports WTPDF](tutorials/30-pdf20-tagged-namespaces.md), [les signatures modernes et l’intégrité](tutorials/31-pdf20-modern-signature.md) et [les horodatages et preuves DSS/VRI](tutorials/32-pdf20-timestamp-dss.md). Les [mesures géospatiales](tutorials/33-pdf20-geospatial.md) et [destinations de structure](tutorials/34-pdf20-structure-destinations.md) complètent le parcours. Le [guide du bundle](pdf-2-0-bundle.md) les relie aux spécifications conservées et aux contrôles indépendants.

La [recette de tableau](recipes/table.md) assemble ces notions dans une présentation concrète. La [collection de recettes](recipes/README.md) explique aussi comment proposer de nouveaux exemples.

## Identité et responsabilités

- Les valeurs PDF sont des objets. Les chaînes représentent des octets ; `TextString` réalise explicitement l'encodage du texte Unicode.
- Une `IndirectReference` vise une instance. Un `SerializationContext` attribue les identifiants pendant l'écriture d'un seul fichier. Il n'existe aucun singleton ni compteur global.
- `FileStructure` décrit le fichier ; `FileWriter` l'écrit. Chaque écriture crée un contexte neuf et produit les offsets et longueurs à partir des octets réellement émis.
- Les dictionnaires utilisent des objets `Entry`. `with()` et `without()` construisent des copies et préservent les contraintes des modèles spécialisés.
- Les arbres de pages et les plans utilisent des constructeurs de graphe mutables, avec un seul parent et des références explicites. Leur structure calcule les liens et compteurs ; les objets de définition de la norme sont immuables.
- Les filtres s'appliquent dans l'ordre inverse de leur ordre de décodage. Les flux sont toujours référencés comme objets indirects.

Voir [l'architecture](architecture.md) pour les choix de construction et [la couverture de la spécification](specification.md) pour la traçabilité et les limites.

Le [guide des composants](components.md) explique chaque famille d'objets. La [référence API](https://pdftoolkit.github.io/reference/index.html) donne les signatures et les liens vers le code et la norme. Les [instructions de construction du site](site/README.md) décrivent la génération et les vérifications locales.

## Couverture et limites

Le catalogue ISO 32000-1 recense les **392 tableaux**, **823 sections indexées** et **73 tokens d'opérateur** de la référence. Les tableaux de dictionnaires donnent lieu à des classes nommées pour leurs dictionnaires, leurs entrées et leurs définitions immuables. Les noms PDF conservent exactement leur casse, qui est significative dans le format.

Les implémentations exécutables couvrent les objets fondamentaux, l'écriture des fichiers, les tables et flux de références croisées, les objets compressés, les opérateurs de contenu, les arbres de pages/noms/nombres, les destinations et plans, les polices standard et les quatre représentations de fonction PDF.

**La présence d'une définition n'est pas une déclaration de conformité complète.** Le catalogue valide les types, références exigées, exigences inconditionnelles et certaines formes de valeurs. Les conditions, relations entre dictionnaires et règles de version qui ne disposent pas encore d'une validation spécialisée restent dans leurs définitions et dans le document de couverture.

Le core compose les objets de polices, les CMaps, les images et leurs masques, les formulaires, la structure balisée et les révisions incrémentales. Il écrit aussi les filtres, le chiffrement explicitement choisi, les signatures par plages d'octets, les références hybrides et la linéarisation. Les modules optionnels fournissent l'analyse TrueType, la conversion JPEG/PNG et la lecture de PDF externes. Les mécanismes vérifiés et les règles restantes figurent dans [l'inventaire de couverture](coverage.md). La fabrication de sous-ensembles de programmes de police, les scripts complexes et l'import avec remappage d'un graphe externe demandent des composants dédiés. `EncodedData` permet de déclarer explicitement des octets déjà encodés. Les obligations de sécurité non prises en charge sont refusées.

Le writer assemble actuellement le fichier en mémoire. Le lecteur est fourni par `pdftoolkit/pdf-reader`. Un moteur de rendu et une API de mise en page ne font pas partie du core.

## Sécurité

La [politique de sécurité](https://github.com/PDFToolkit/pdf/blob/v0.11.0/SECURITY.md) décrit les signalements privés et les frontières de confiance. La [revue de sécurité](security.md) explique les protections de sérialisation et les responsabilités de l'application pour les chemins, les actions PDF et les limites de ressources.

## Génération des définitions

Les ressources structurées et les classes générées sont versionnées dans le dépôt du core. Depuis ce dépôt, la génération est reproductible à partir de ces ressources ; elle n'a pas besoin de relire le PDF à l'exécution de la bibliothèque.

```sh
python tools/generate_specification.py
```

L'extracteur `tools/extract_spec.py` conserve la source et les localisations dans le PDF. Son utilisation demande les dépendances Python indiquées dans la documentation de la spécification. Les descriptions normatives servent à tracer les contraintes encore à implémenter ; les algorithmes ne sont pas remplacés par une génération de classes.

## Dériver du HTML

Pour dériver du HTML sémantique depuis un PDF balisé, installer `pdftoolkit/pdf-to-html:^0.5.1` puis suivre le [tutoriel 35](tutorials/35-derive-html.md). Cette conversion optionnelle reste hors du core.

La version 0.5.1 exige Reader 0.6 et PHP 8.3+ en 64 bits avec DOM et mbstring. Son [registre des exigences](https://pdftoolkit.github.io/fr/modules/to-html/requirements.html) rattache les règles aux tests. Les [profils](https://pdftoolkit.github.io/fr/modules/to-html/policies.html) distinguent contenu sémantique, actions de formulaire optionnelles et scripts PDF ; aucune de ces actions actives n'est autorisée par défaut. Le [rendu graphique](https://pdftoolkit.github.io/fr/modules/to-html/graphics.html) et l'authentification restent des capacités fournies explicitement par l'application. Conserver les ressources retournées et lire les diagnostics avant publication.

[Packagist: pdftoolkit/pdf-to-html](https://packagist.org/packages/pdftoolkit/pdf-to-html).
