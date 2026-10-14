# Core et modules optionnels

PDFToolkit sépare le modèle PDF des traitements de fichiers externes. Le core
**0.7.0**, les trois modules PDF **0.1.8** et le modèle OpenType indépendant **0.1.0**
nécessitent PHP 8.3 ou supérieur et sont vérifiés sous PHP 8.3, 8.4 et 8.5.
Le core **0.7** exige aussi PHP en 64 bits ; OpenType reste indépendant du core PDF.
Le core conserve son nom Composer `roukmoute/pdf` après son transfert dans
l'organisation ; les nouveaux modules utilisent le préfixe `pdftoolkit/`.

## La frontière du core

Le [core](https://github.com/PDFToolkit/pdf) représente les objets et mécanismes
décrits par **PDF 1.7 / ISO 32000-1:2008** et le [supplément Adobe niveau 3](adobe-supplement.md), ainsi que [PDF 2.0 / ISO 32000-2:2020 EC3](pdf-2-0.md) et ses [spécifications complémentaires](pdf-2-0-bundle.md) : valeurs, références, dictionnaires,
flux, opérateurs, pages, polices, images, fonctions, écriture et révisions.
Les définitions gardent leurs noms PDF et leurs références au document Adobe.

PDF décrit, par exemple, les entrées `/Width`, `/ColorSpace`, `/SMask`,
`/FontFile2`, `/CIDToGIDMap` et `/ToUnicode`. Il permet d'incorporer des programmes
de fonte et des octets DCT ; il ne définit pas tout le format PNG ou OpenType.
Leurs lecteurs demandent d'autres spécifications et appartiennent aux modules.
L'écriture reste dans le core, car elle produit la syntaxe et la structure PDF.

La version 0.4 ajoute des constructions natives pour les champs AcroForm et FDF,
la structure logique, les espaces couleur, motifs et sept types de shading, les
images normalisées, les formes, la transparence, les calques, les fontes et CMaps.
Elle fournit aussi LZW et les prédicteurs, les mécanismes de chiffrement ISO et
Adobe, les signatures et la linéarisation. La [couverture détaillée](coverage.md)
sépare ces comportements vérifiés des règles encore à compléter.

La version 0.5 ajoute les générations et listes libres des révisions, les mises
à jour après linéarisation, la navigation native, les fichiers incorporés et les
collections. Les politiques de champs de signature sont appliquées aux snapshots
écrits et les résultats cryptographiques sont vérifiés avant finalisation.

| Dépôt et package | Entrée | Objets ou données produits |
| --- | --- | --- |
| [PDFToolkit/pdf](https://github.com/PDFToolkit/pdf) — `roukmoute/pdf` | Objets PDF assemblés par l'application | Fichier PDF, références croisées et révisions |
| [PDFToolkit/pdf-images](https://github.com/PDFToolkit/pdf-images) — `pdftoolkit/pdf-images` | Octets PNG ou JPEG et limites explicites | Échantillons couleur/alpha ou représentation DCT du core |
| [PDFToolkit/pdf-fonts](https://github.com/PDFToolkit/pdf-fonts) — `pdftoolkit/pdf-fonts` | Octets TrueType, texte et paramètres explicites | Programme incorporable, métriques et correspondances pour le core |
| [PDFToolkit/pdf-reader](https://github.com/PDFToolkit/pdf-reader) — `pdftoolkit/pdf-reader` | Octets PDF et budgets de lecture | Graphe lu, pages et attributs hérités, références à résoudre et flux encodés ou décodés |
| [PDFToolkit/opentype](https://github.com/PDFToolkit/opentype) — `pdftoolkit/opentype` | Octets OpenType SFNT et limites explicites | Tables, métriques, correspondances Unicode et substitutions de glyphes GSUB |

Les dépendances vont **des trois modules PDF vers le core**. Ces modules ne se dépendent
pas entre eux. Le core ne connaît aucun de leurs parseurs : une application peut
construire directement ses objets PDF ou les alimenter avec un autre convertisseur.
Le modèle objet PDF est commun, sans copie parallèle des primitives ni registre global.

Le [modèle OpenType](https://github.com/PDFToolkit/opentype) est indépendant : il ne dépend ni du core ni de `pdf-fonts`. Il analyse une fonte pour produire ses propres objets, sans construire de dictionnaires PDF. Le convertisseur `pdf-fonts` reste le point d’entrée pour l’incorporation actuelle de fontes TrueType dans un PDF. La première version OpenType ne fournit pas encore de composition complète des scripts, de GPOS, de GDEF, de fontes variables ou de CFF. Consulter sa [couverture](https://github.com/PDFToolkit/opentype/blob/v0.1.0/docs/coverage.md).

Le core 0.7.0 étend l’écriture PDF 2.0 avec la cryptographie moderne et PDF MAC, XMP/déclarations et les métadonnées d’objets, les parties de document, les enveloppes de contenus chiffrés et la structure qualifiée par namespace. L’audit WTPDF rapporte des contrôles mécaniques partiels et les preuves encore nécessaires, sans certification. Ces mécanismes du writer n’étendent ni le périmètre d’entrée PDF 1.0–1.7 du lecteur optionnel, ni la conversion PNG/JPEG ou TrueType statique.

## Installer ce dont l'application a besoin

Les cinq packages sont disponibles sur Packagist :
[core](https://packagist.org/packages/roukmoute/pdf),
[lecteur](https://packagist.org/packages/pdftoolkit/pdf-reader),
[images](https://packagist.org/packages/pdftoolkit/pdf-images),
[fontes PDF](https://packagist.org/packages/pdftoolkit/pdf-fonts) et
[OpenType](https://packagist.org/packages/pdftoolkit/opentype).
Les contraintes stables sont `roukmoute/pdf:^0.7.0` pour le core et
`pdftoolkit/pdf-reader:^0.1.8`, `pdftoolkit/pdf-images:^0.1.8` ou
`pdftoolkit/pdf-fonts:^0.1.8` pour les modules PDF, et `pdftoolkit/opentype:^0.1.0` pour le modèle de fonte indépendant. Les anciens tags du core `v0.1.0`
et `v0.1.1` conservent leur contrainte PHP 8.5.

Pour générer seulement des PDF :

```sh
composer require "roukmoute/pdf:^0.7.0"
```

Pour ajouter la lecture de PDF existants :

```sh
composer require "roukmoute/pdf:^0.7.0" "pdftoolkit/pdf-reader:^0.1.8"
```

Pour convertir des images :

```sh
composer require "roukmoute/pdf:^0.7.0" "pdftoolkit/pdf-images:^0.1.8"
```

Pour analyser des fontes TrueType :

```sh
composer require "roukmoute/pdf:^0.7.0" "pdftoolkit/pdf-fonts:^0.1.8"
```

Pour analyser une fonte indépendamment du PDF :

```sh
composer require "pdftoolkit/opentype:^0.1.0"
```

Cette commande installe uniquement OpenType, sans le core ni les convertisseurs PDF.

Composer résout ces packages depuis Packagist et télécharge leurs distributions
publiées. Les trois modules PDF demandent le core stable transitivement ; installer le core
seul n'installe aucun module. Conserver le `composer.lock` de l'application pour
fixer les versions et les révisions.

Les applications qui avaient ajouté les dépôts GitHub dans `repositories`
peuvent retirer ces entrées de leur `composer.json`. Les noms Composer des
packages restent identiques.

Avant 1.0, une nouvelle version mineure peut changer les noms et signatures.
Les contraintes `^0.7.0` et `^0.1.8` autorisent les correctifs de leur série et
écartent la version mineure suivante. Consulter les changelogs avant de changer
de série. Pour travailler sur les développements à venir, demander explicitement
`dev-master` pour les packages concernés.

Les modules 0.1.8 acceptent les séries `^0.2 || ^0.3 || ^0.4 || ^0.5 || ^0.6 || ^0.7` du core. Une
application qui reste sur une ancienne série acceptée du core peut donc les mettre à jour ; les commandes
ci-dessus sélectionnent explicitement les constructions du core 0.7. Le core
conserve ses extensions PHP obligatoires `ctype`, `iconv` et `zlib`. Les backends
AES, CMS et de signature utilisant OpenSSL demandent aussi `openssl`, lorsqu'ils
sont choisis par l'application.

## Lire un PDF externe

Le lecteur reçoit ses octets ; l'application choisit comment les obtenir.
`DocumentReader`, `FileBytes` et les lecteurs de pages appartiennent au namespace
`PDF\Reading` du module, tandis que les dictionnaires et nombres utilisent
les mêmes classes `PDF\Syntax\Object` que le writer.

```php
use PDF\Reading\DocumentReader;
use PDF\Reading\FileBytes;
use PDF\Reading\PageContentLimits;
use PDF\Reading\PageContentsReader;
use PDF\Reading\PageTreeLimits;
use PDF\Reading\PageTreeReader;
use PDF\Reading\ReaderLimits;

$reader = new DocumentReader(new ReaderLimits(maxFileBytes: 8_388_608));
$document = $reader->read(new FileBytes($pdfBytes));
$tree = (new PageTreeReader($document, new PageTreeLimits(
    maxDepth: 64,
    maxNodes: 10_000,
    maxPages: 5_000,
)))->read();
$contentsReader = new PageContentsReader($document, new PageContentLimits(
    maxStreams: 128,
));

printf("Validated page count: %d\n", count($tree));
foreach ($tree as $index => $page) {
    printf(
        "Page %d; rotation: %d; content streams: %d\n",
        $index + 1,
        $page->attributes->rotate->integer(),
        count($contentsReader->read($page)),
    );
}
```

`PageTreeReader::read()` vérifie l'arbre entier : comptes de feuilles, parents,
cycles et identités répétées. Il retourne un `ReadPageTree` comptable et itérable,
avec des `ReadPage` conservant leur document, leur référence et leur dictionnaire
source. Leurs `PageAttributes` donnent les ressources, MediaBox, CropBox et
rotation effectifs, après héritage depuis l'ancêtre le plus proche. Un dictionnaire
de ressources local remplace celui hérité sans fusion ; Contents reste local.

`PageContentsReader` donne des `EncodedStream` dans l'ordre du document, sans
concaténation ni décodage. Les limites de parcours et de nombre de flux sont des
objets explicites ; les budgets cumulatifs de `ReadDocument` continuent de
s'appliquer. Pour obtenir les octets décodés, demander séparément
`$document->streamData($stream)`. Le
[guide de lecture des pages](https://github.com/PDFToolkit/pdf-reader/blob/v0.1.8/docs/pages.md)
explique chaque étape et fournit un exemple exécutable avec trois pages héritées.

Les valeurs PDF restent des objets : `get()` conserve une référence comme
référence et `resolve()` demande son chargement dans ce document. Les objets lus
sont conservés dans un cache propre au document ; il n'y a ni singleton ni
résolution cachée dans les valeurs.

Le lecteur gère les tables et flux xref, les révisions `/Prev`, les flux d'objets,
Flate, ASCIIHex, ASCII85 et RunLength, ainsi que certains prédicteurs TIFF/PNG.
Le chargement d'un flux garde ses octets encodés ; `streamData()` demande son
décodage. Il ne rend pas une page et n'interprète pas ses opérateurs pour extraire
du texte. PDF 2.0, le chiffrement, les références hybrides et les codecs non
implémentés sont refusés explicitement.

Les valeurs lues ne sont pas directement réinjectables dans le writer : leurs
références appartiennent au fichier d'origine. L'import et le remappage du graphe,
la réécriture, la fusion et la réparation restent à construire. Consulter
[la documentation du lecteur](https://github.com/PDFToolkit/pdf-reader#readme)
et [ses contrôles de sécurité](https://github.com/PDFToolkit/pdf-reader/blob/v0.1.8/docs/security.md)
pour choisir ses budgets. Par défaut, les octets binaires conservés et le total
des flux décodés sont chacun bornés à 128 MiB, en plus des autres limites.

## Une documentation centrale, des installations indépendantes

Cette documentation présente l'API des cinq packages. Les fiches des modules
portent un badge **optionnel** et leurs liens de source utilisent le commit
du module fixé par le lock de construction, ou par le tag et le checkout séparé du package OpenType. Cela n'ajoute aucune dépendance aux
applications qui installent uniquement le core.

Le checkout de développement du core installe les modules en `require-dev`
pour générer les tutoriels [TrueType](tutorials/09-embedded-font.md) et
[PNG/JPEG](tutorials/10-image-files.md) et exporter toutes les signatures.
Les objets PDF correspondants restent dans le core ; seuls les lecteurs de
formats externes et leurs services de conversion sont dans les modules.

Le core reçoit les profils ICC, programmes de fonte, données d'image déjà
encodées, certificats et médias comme des données explicites. Il contrôle leurs
relations PDF dans les composants natifs concernés ; leur présence n'implémente
pas un moteur ICC, un codec, le rendu de pages, l'exécution de scripts ou la
politique de confiance d'une signature. Ces frontières sont détaillées dans le
[guide des composants](components.md) et la [couverture](coverage.md).
