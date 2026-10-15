# Core et modules optionnels

PDFToolkit sépare le modèle PDF des traitements de fichiers externes. Le core
**0.10.0**, le lecteur PDF **0.5.1**, les modules images/fontes **0.1.11**, le modèle OpenType indépendant **0.2.0** et PDF vers HTML **0.4.2**
nécessitent PHP 8.3 ou supérieur et sont vérifiés sous PHP 8.3, 8.4 et 8.5.
Le core **0.10** et OpenType **0.2** exigent PHP en 64 bits ; OpenType reste indépendant du core PDF.
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
| [PDFToolkit/opentype](https://github.com/PDFToolkit/opentype) — `pdftoolkit/opentype` | Octets OpenType SFNT et limites explicites | Tables, métriques, correspondances Unicode, substitutions GSUB et positionnement GPOS |
| [PDFToolkit/pdf-to-html](https://github.com/PDFToolkit/pdf-to-html) — `pdftoolkit/pdf-to-html` | Octets PDF balisés ou modèle logique source explicite | HTML sémantique, CSS, ressources et diagnostics |

Les modules lecteur, images et fontes dépendent du core sans dépendre entre eux. PDF vers HTML dépend aussi du lecteur. Le core ne connaît aucun de leurs parseurs : une application peut
construire directement ses objets PDF ou les alimenter avec un autre convertisseur.
Le modèle objet PDF est commun, sans copie parallèle des primitives ni registre global.

Le [modèle OpenType](https://github.com/PDFToolkit/opentype) est indépendant : il ne dépend ni du core ni de `pdf-fonts`. Il produit ses propres objets sans construire de dictionnaires PDF. `pdf-fonts` reste le point d'entrée pour l'incorporation actuelle de TrueType. OpenType 0.2 implémente GSUB 1–8, GPOS 1–9, classes/filtres de marques/carets GDEF et coordonnées de variation normalisées explicites. Son [guide de positionnement](https://github.com/PDFToolkit/opentype/blob/v0.2.0/docs/fr/positioning.md) explique les séquences positionnées immuables, ajustements device et interpolation ItemVariationStore native. Sa [couverture](https://github.com/PDFToolkit/opentype/blob/v0.2.0/docs/fr/coverage.md) conserve les limites : composition Unicode/bidi/retour à la ligne, instanciation complète des contours variables, CFF/CFF2, autres tables, conteneurs, écriture et sous-ensembles restent distincts.

Le core 0.8.0 conserve l'écriture PDF 2.0 avec cryptographie moderne/PDF MAC, métadonnées, parties documentaires, enveloppes chiffrées et structure qualifiée. Il ajoute des [règles de source exécutées et corrections vérifiées](source-audits.md), la [caviardisation](tutorials/36-applied-redaction.md) native conservatrice et une comparaison XML WTPDF optionnelle du texte enrichi. WTPDF reste un audit mécanique partiel sans certification. L'authentification du lecteur et le layout OpenType ont leurs propres frontières ; ces évolutions du core ne réalisent pas la conversion PNG/JPEG ou l'incorporation de fontes variables.

## Installer ce dont l'application a besoin

Les six packages sont disponibles sur Packagist :
[core](https://packagist.org/packages/roukmoute/pdf),
[lecteur](https://packagist.org/packages/pdftoolkit/pdf-reader),
[images](https://packagist.org/packages/pdftoolkit/pdf-images),
[fontes PDF](https://packagist.org/packages/pdftoolkit/pdf-fonts) et
[OpenType](https://packagist.org/packages/pdftoolkit/opentype) et
[PDF vers HTML](https://packagist.org/packages/pdftoolkit/pdf-to-html).
Les contraintes stables sont `roukmoute/pdf:^0.10.0` pour le core et
`pdftoolkit/pdf-reader:^0.5.1`, `pdftoolkit/pdf-images:^0.1.11` ou
`pdftoolkit/pdf-fonts:^0.1.11` pour les modules PDF, et `pdftoolkit/opentype:^0.2.0` pour le modèle de fonte indépendant. Les anciens tags du core `v0.1.0`
et `v0.1.1` conservent leur contrainte PHP 8.5.

Pour générer seulement des PDF :

```sh
composer require "roukmoute/pdf:^0.10.0"
```

Pour ajouter la lecture de PDF existants :

```sh
composer require "roukmoute/pdf:^0.10.0" "pdftoolkit/pdf-reader:^0.5.1"
```

Pour convertir des images :

```sh
composer require "roukmoute/pdf:^0.10.0" "pdftoolkit/pdf-images:^0.1.11"
```

Pour analyser des fontes TrueType :

```sh
composer require "roukmoute/pdf:^0.10.0" "pdftoolkit/pdf-fonts:^0.1.11"
```

Pour analyser une fonte indépendamment du PDF :

```sh
composer require "pdftoolkit/opentype:^0.2.0"
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
Les contraintes `^0.10.0`, `^0.5.1` et `^0.1.11` autorisent les correctifs de leur série et
écartent la version mineure suivante. Consulter les changelogs avant de changer
de série. Pour travailler sur les développements à venir, demander explicitement
`dev-master` pour les packages concernés.

Le lecteur 0.5.1 exige le core `^0.9 || ^0.10` ; les modules images/fontes
0.1.11 conservent leurs anciennes séries acceptées jusqu'à `^0.10`. Les
commandes ci-dessus sélectionnent explicitement le core 0.10.0 ou un correctif compatible. Le core
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
[guide de lecture des pages](https://github.com/PDFToolkit/pdf-reader/blob/v0.5.1/docs/pages.md)
explique chaque étape et fournit un exemple exécutable avec trois pages héritées.

Les valeurs PDF restent des objets : `get()` conserve une référence comme
référence et `resolve()` demande son chargement dans ce document. Les objets lus
sont conservés dans un cache propre au document ; il n'y a ni singleton ni
résolution cachée dans les valeurs.

Le lecteur gère les tables et flux xref, références hybrides, révisions `/Prev`,
flux d'objets et décodages de filtres explicitement bornés.
Le chargement d'un flux garde ses octets encodés ; `streamData()` demande son
décodage. Il ne rend pas une page et n'interprète pas ses opérateurs pour extraire
du texte. La syntaxe PDF 1.0–2.0 et les chaînes UTF-8 PDF 2.0 restent acceptées.
Le lecteur 0.3 ajoute LZW et d'autres décodages de prédicteurs TIFF/PNG aux filtres
sans perte existants. DCT, JPX, CCITT et JBIG2 restent explicitement non pris en
charge par ce lecteur ; les décodeurs sélectionnés séparément dans l'adaptateur
HTML ont leur propre périmètre.

### Choisir l'authentification par mot de passe

```php
use PDF\Reading\Security\StandardPasswordAuthentication;
use PDF\Security\Saslprep;

$reader = new DocumentReader(authentication: new StandardPasswordAuthentication(
    (new Saslprep())->prepare($rawUtf8Password),
));
$document = $reader->read(new FileBytes($pdfBytes));
$permissions = $document->permissions();
```

R=5–7 reçoit un credential Unicode préparé explicitement ; R=2–4 utilise plutôt
`PdfDocEncodedPassword` avec des octets PDFDocEncoding. Le
[guide d'authentification](https://github.com/PDFToolkit/pdf-reader/blob/v0.5.1/docs/fr/authentication.md)
précise R=2–7, les filtres nommés `StrF`/`StmF`/`EFF` et la vérification des tags
AES-GCM. Par défaut le lecteur n'ouvre aucune entrée chiffrée sans cette sélection.
Le lecteur 0.4 vérifie tout MAC PDF source signalé avant de retourner le contenu
protégé. Choisir `SourceIntegrityPolicy::RequirePdfMac` lorsque l'application
doit aussi refuser les PDF ordinaires non protégés ou privés de leurs marqueurs ;
la valeur compatible par défaut les accepte. `requiringSourceIntegrity()`
conserve ou renforce la politique existante du lecteur sans remplacer ses
identifiants ni ses limites. Le
[guide du MAC source](https://pdftoolkit.github.io/fr/modules/reader/source-mac.html)
décrit la couverture exacte des octets et le cadrage pris en charge.
Le lecteur 0.5 accepte aussi `PublicKeyAuthentication` explicite avec capacité
de déchiffrement CMS et ordre des octets de permissions choisis par l'application.
Son [guide de clé publique](https://pdftoolkit.github.io/fr/modules/reader/public-key-authentication.html)
décrit Adobe.PubSec s3/s4/s5, les clés indépendantes des filtres et l'accès différé
aux pièces jointes. `DocumentPermissions::effectiveMask()` couvre les droits
Standard user/owner et destinataire authentifiés ; l'application les applique.
L'authentification ne vérifie ni mathématiquement les signatures ni la confiance des certificats.

Les valeurs lues ne sont pas directement réinjectables dans le writer : leurs
références appartiennent au fichier d'origine. L'import et le remappage du graphe,
la réécriture, la fusion et la réparation restent à construire. Consulter
[la documentation du lecteur](https://github.com/PDFToolkit/pdf-reader#readme)
et [ses contrôles de sécurité](https://github.com/PDFToolkit/pdf-reader/blob/v0.5.1/docs/security.md)
pour choisir ses budgets. Par défaut, les octets binaires conservés et le total
des flux décodés sont chacun bornés à 128 MiB, en plus des autres limites.

## Une documentation centrale, des installations indépendantes

Cette documentation présente l'API des six packages. Les fiches des modules
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

## Dériver du HTML depuis un PDF balisé

Le [module PDF vers HTML](https://pdftoolkit.github.io/fr/modules/to-html/index.html), optionnel, suit la spécification d’usage PDF Association **Deriving HTML from PDF 1.2** conservée. La version 0.4.2 exige le core `^0.9 || ^0.10` et le lecteur `^0.4.1 || ^0.5`, sous PHP 8.3+ en 64 bits avec DOM et mbstring. Le site documente le core 0.10.0 et Reader 0.5.1, tandis que le lock original de la version HTML conserve core 0.9.1 et Reader 0.5.0 pour sa propre validation. La commande ci-dessous demande explicitement le core 0.10.0 ou un correctif compatible. Elle dérive le HTML sémantique de la structure logique, sans inférer de structure absente, faire d’OCR ni reproduire la mise en page. Couverture du modèle, de l’adaptateur de fichiers et intégration navigateur/runtime restent distinctes.

```sh
composer require "roukmoute/pdf:^0.10.0" "pdftoolkit/pdf-to-html:^0.4.2"
```

[Suivre le tutoriel exécutable](tutorials/35-derive-html.md) et examiner les diagnostics avant publication du HTML. Les associations ParentTree, identités des en-têtes de tableaux, destinations, correspondances Unicode, images inline et actions de formulaire disposent de tests et d'oracles indépendants. Le [registre des exigences](https://pdftoolkit.github.io/fr/modules/to-html/requirements.html) relie chaque règle aux décisions et preuves ; il ne certifie pas l'acceptation de tout PDF.

Le [profil par défaut](https://pdftoolkit.github.io/fr/modules/to-html/policies.html) n'exécute ni script PDF ni action ResetForm/SubmitForm et ne récupère pas de ressource externe. `FormActionPolicy` permet d'activer séparément le reset ciblé vers `/DV` ou les soumissions HTML acceptées, sans autoriser ECMAScript PDF. Conserver toutes les ressources retournées avec le HTML.

Les [graphiques](https://pdftoolkit.github.io/fr/modules/to-html/graphics.html) gardent leurs programmes et ressources : `GraphicPdfExporter` produit un PDF isolé, puis `RasterContentRenderer` appelle le `GraphicsRasterizer` fourni par l'application. Le moteur de rendu, l'authentification des entrées chiffrées, les codecs supplémentaires et le respect des permissions par le lecteur HTML restent des capacités explicites. Un profil visuel demandé sans moteur échoue explicitement.

L'authentification native par mot de passe est désormais sélectionnable avec un
lecteur explicite passé à `PdfToHtml` ; le
[guide d'authentification](https://pdftoolkit.github.io/fr/modules/to-html/authentication.html)
montre l'opération et la propagation des permissions vérifiées. Le credential
reste explicite et le navigateur doit appliquer les droits exportés.

[Packagist: pdftoolkit/pdf-to-html](https://packagist.org/packages/pdftoolkit/pdf-to-html).
