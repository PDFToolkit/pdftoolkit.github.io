# Core et modules optionnels

PDFToolkit sépare le modèle PDF des traitements de fichiers externes.
Les versions documentées sont le core **0.12**, Reader **0.7**, Images et Fonts **0.2**, OpenType **0.4**, Codecs **0.1** et PDF vers HTML **0.7**. Elles nécessitent **PHP 8.3 ou supérieur en 64 bits** ; leurs validations couvrent PHP 8.3, 8.4 et 8.5. Les versions et révisions exactes sont fixées dans le manifeste de sources. OpenType et Codecs ne dépendent pas du core PDF.
Le core conserve son nom Composer `roukmoute/pdf` ; les modules utilisent `pdftoolkit/`.

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
| [PDFToolkit/pdf](https://github.com/PDFToolkit/pdf) — [`roukmoute/pdf`](https://packagist.org/packages/roukmoute/pdf) | Objets PDF assemblés par l'application | Fichier PDF, références croisées et révisions |
| [PDFToolkit/pdf-images](https://github.com/PDFToolkit/pdf-images) — [`pdftoolkit/pdf-images`](https://packagist.org/packages/pdftoolkit/pdf-images) | Octets PNG ou JPEG et limites explicites | Échantillons couleur/alpha ou représentation DCT du core |
| [PDFToolkit/pdf-fonts](https://github.com/PDFToolkit/pdf-fonts) — [`pdftoolkit/pdf-fonts`](https://packagist.org/packages/pdftoolkit/pdf-fonts) | Octets TrueType/CFF statiques, texte et étapes de layout explicites | Programmes incorporables, correspondances Unicode/CID/GID et texte PDF positionné |
| [PDFToolkit/pdf-reader](https://github.com/PDFToolkit/pdf-reader) — [`pdftoolkit/pdf-reader`](https://packagist.org/packages/pdftoolkit/pdf-reader) | Octets PDF et budgets de lecture | Graphe lu, pages et attributs hérités, références à résoudre et flux encodés ou décodés |
| [PDFToolkit/opentype](https://github.com/PDFToolkit/opentype) — [`pdftoolkit/opentype`](https://packagist.org/packages/pdftoolkit/opentype) | Octets OpenType SFNT/TTC/OTC et limites explicites | Tables, contours, métriques, substitutions GSUB et positionnement GPOS |
| [PDFToolkit/pdf-codecs](https://github.com/PDFToolkit/pdf-codecs) — [`pdftoolkit/pdf-codecs`](https://packagist.org/packages/pdftoolkit/pdf-codecs) | Octets JPEG, JPEG 2000 ou JBIG2 | Plans de composantes et métadonnées couleur/alpha exactes dans les profils pris en charge |
| [PDFToolkit/pdf-to-html](https://github.com/PDFToolkit/pdf-to-html) — [`pdftoolkit/pdf-to-html`](https://packagist.org/packages/pdftoolkit/pdf-to-html) | Octets PDF balisés ou modèle logique source explicite | HTML sémantique, CSS, ressources et diagnostics |

Les modules lecteur, images et fontes dépendent du core sans dépendre entre eux. Fonts utilise aussi OpenType ; PDF vers HTML utilise Reader. OpenType et Codecs sont des bibliothèques indépendantes. Reader découvre les codecs PHP optionnels seulement quand un décodage d’image est demandé. Le core ne connaît aucun de leurs parseurs : l’application peut construire directement ses objets PDF. Le modèle est partagé, sans copie des primitives ni registre global.

Le [modèle OpenType](https://github.com/PDFToolkit/opentype) implémente GSUB 1–8, GPOS 1–9 et GDEF explicites, axes/métriques variables et géométrie TrueType/CFF/CFF2 non hintée. La version 0.4 lit les collections TTC/OTC, sérialise une face complète choisie, exécute tous les formats cmap Unicode définis et expose les paramètres optiques/de style. Les plages de fonctionnalités exprimées en scalaires source conservent tout le contexte de shaping. L’application choisit toujours scripts, langues, étapes, normalisation et bidi.

La [couverture OpenType](https://pdftoolkit.github.io/fr/modules/opentype/coverage.html) distingue 27 périmètres de tables implémentés, quatre partiels et 19 tables non interprétées. Des octets bruts ne réalisent ni VM TrueType, ni consommateurs couleur/bitmap/mathématiques, ni décodage WOFF. `pdf-fonts` 0.2 incorpore TrueType et CFF1 statiques et émet le texte explicitement substitué/positionné, avec conservation des alias Unicode et ligatures. Le [guide de layout](https://pdftoolkit.github.io/fr/modules/fonts/opentype-layout.html) précise CID/GID et l’interopérabilité des conteneurs CFF. L’incorporation PDF CFF2/variable, la génération d’instances statiques et les sous-ensembles restent absents.

Le core 0.8.0 conserve l'écriture PDF 2.0 avec cryptographie moderne/PDF MAC, métadonnées, parties documentaires, enveloppes chiffrées et structure qualifiée. Il ajoute des [règles de source exécutées et corrections vérifiées](source-audits.md), la [caviardisation](tutorials/36-applied-redaction.md) native conservatrice et une comparaison XML WTPDF optionnelle du texte enrichi. WTPDF reste un audit mécanique partiel sans certification. L'authentification du lecteur et le layout OpenType ont leurs propres frontières ; ces évolutions du core ne réalisent pas la conversion PNG/JPEG ou l'incorporation de fontes variables.

## Installer ce dont l'application a besoin

Les sept bibliothèques sont disponibles sur Packagist sous `roukmoute/pdf` ou les noms `pdftoolkit/` ci-dessus. Les contraintes documentées sont core `^0.12`, Reader/HTML `^0.7`, Images/Fonts `^0.2`, OpenType `^0.4` et Codecs `^0.1`. Les anciens tags du core `v0.1.0` et `v0.1.1` conservent leur contrainte PHP 8.5.

Pour générer seulement des PDF :

```sh
composer require "roukmoute/pdf:^0.12"
```

Pour ajouter la lecture de PDF existants :

```sh
composer require "roukmoute/pdf:^0.12" "pdftoolkit/pdf-reader:^0.7.0"
```

Pour convertir des images :

```sh
composer require "roukmoute/pdf:^0.12" "pdftoolkit/pdf-images:^0.2.1"
```

Pour incorporer des fontes TrueType/CFF et choisir le layout :

```sh
composer require "roukmoute/pdf:^0.12" "pdftoolkit/pdf-fonts:^0.2.0"
```

Pour analyser une fonte indépendamment du PDF :

```sh
composer require "pdftoolkit/opentype:^0.4.0"
```

Cette commande installe uniquement OpenType, sans le core ni les convertisseurs PDF.

Pour rendre disponible le repli image en PHP pur :

```sh
composer require "pdftoolkit/pdf-codecs:^0.1"
```

Ghostscript et `prlimit` sont des outils système optionnels fournis séparément. Reader n’utilise que les profils natifs qualifiés pour préserver les échantillons et métadonnées demandés. Une entrée malformée ou une limite dépassée ne déclenche pas un autre décodeur.

Composer résout ces packages depuis Packagist et télécharge leurs distributions
publiées. Les trois modules PDF demandent le core stable transitivement ; installer le core
seul n'installe aucun module. Conserver le `composer.lock` de l'application pour
fixer les versions et les révisions.

Les applications qui avaient ajouté les dépôts GitHub dans `repositories`
peuvent retirer ces entrées de leur `composer.json`. Les noms Composer des
packages restent identiques.

Avant 1.0, une nouvelle version mineure peut changer les noms et signatures.
Les contraintes `^0.12`, `^0.7` et `^0.2` autorisent les correctifs de leur série et
écartent la version mineure suivante. Consulter les changelogs avant de changer
de série. Pour travailler sur les développements à venir, demander explicitement
`dev-master` pour les packages concernés.

Images 0.2 exige le core `^0.12` ; Reader 0.7 exige `^0.11 || ^0.12`. Fonts 0.2 accepte ses séries documentées du core 0.4–0.12 et exige OpenType `^0.4`. Les commandes ci-dessus sélectionnent le core 0.12. Le [guide de migration](migration-0.11.md) reste pertinent pour les changements d’API 0.11. Le core demande `ctype`, `iconv` et `zlib` ; les fournisseurs AES, CMS et de signature choisis demandent aussi `openssl`. Chaque manifeste Composer publié précise la compatibilité exacte.

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
[guide de lecture des pages](https://github.com/PDFToolkit/pdf-reader/blob/v0.7.0/docs/pages.md)
explique chaque étape et fournit un exemple exécutable avec trois pages héritées.

Les valeurs PDF restent des objets : `get()` conserve une référence comme
référence et `resolve()` demande son chargement dans ce document. Les objets lus
sont conservés dans un cache propre au document ; il n'y a ni singleton ni
résolution cachée dans les valeurs.

Le lecteur gère tables/flux xref, références hybrides, historiques `/Prev` et flux d’objets. L’analyse conserve les données encodées sans lancer de décodeur d’image. `streamData()` explicite traite les filtres, prédicteurs et CCITT bornés ; `imageData()` conserve les plans de composantes et métadonnées couleur/alpha exactes DCT/JPX/JBIG2. Le décodage natif qualifié est prioritaire, puis les codecs PHP installés fournissent le repli. Le [guide des codecs image](https://pdftoolkit.github.io/fr/modules/reader/image-codecs.html) précise profils, données globales, budgets et limites d’intercalage sans perte. Reader ne rend pas les pages et n’interprète pas les opérateurs pour extraire du texte.

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
[guide d'authentification](https://github.com/PDFToolkit/pdf-reader/blob/v0.7.0/docs/fr/authentication.md)
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

Les références lues restent liées au document source. Reader 0.7 fournit [ImportSession](https://pdftoolkit.github.io/fr/modules/reader/import.html) pour copier un graphe explicitement choisi vers de nouveaux objets writer avec remappage des identités. L’application choisit conservation des flux encodés ou décodage borné. Identités partagées et cycles sont conservés ; conteneurs de transport, signatures et autorité de chiffrement source ne sont pas transférés. Ce n’est ni une fusion automatique de pages, ni une réparation sémantique, ni une révision incrémentale de l’original. Les [capacités de flux externes](https://pdftoolkit.github.io/fr/modules/reader/external-streams.html) fournissent les octets sans accès implicite aux fichiers/réseau. Les budgets Reader et import continuent de s’appliquer.

Reader 0.6 ajoute un [historique physique des révisions](https://pdftoolkit.github.io/fr/modules/reader/revision-history.html) : préfixes exacts, xrefs et portées d'objets avec budgets cumulés. Cette vue conserve les octets source sans les authentifier ni vérifier les signatures. Pour interpréter un préfixe chiffré, le relire avec `DocumentReader` et les credentials/politiques d'intégrité explicites. Cet historique ne devient pas une `FileRevision` native autorisant l'écriture incrémentale.

## Une documentation centrale, des installations indépendantes

Cette documentation présente l'API des sept bibliothèques. Les fiches des modules
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

Le [module PDF vers HTML](https://pdftoolkit.github.io/fr/modules/to-html/index.html), optionnel, suit la spécification d’usage PDF Association **Deriving HTML from PDF 1.2** conservée. La version 0.7 utilise Reader 0.7, avec PHP 8.3+ en 64 bits, DOM et mbstring ; le manifeste de sources fixe les révisions exactes du core et des modules. Elle dérive le HTML sémantique de la structure logique sans inférer de structure absente, faire d’OCR ni reproduire la mise en page PDF. Modèle, adaptation des fichiers et intégration navigateur restent distincts.

```sh
composer require "roukmoute/pdf:^0.12" "pdftoolkit/pdf-to-html:^0.7"
```

[Suivre le tutoriel exécutable](tutorials/35-derive-html.md) et examiner les diagnostics avant publication du HTML. Les associations ParentTree, identités des en-têtes de tableaux, destinations, correspondances Unicode, images inline et actions de formulaire disposent de tests et d'oracles indépendants. Le [registre des exigences](https://pdftoolkit.github.io/fr/modules/to-html/requirements.html) relie chaque règle aux décisions et preuves ; il ne certifie pas l'acceptation de tout PDF.

Le [profil par défaut](https://pdftoolkit.github.io/fr/modules/to-html/policies.html) n'exécute ni script PDF ni action ResetForm/SubmitForm et ne récupère pas de ressource externe. `FormActionPolicy` permet d'activer séparément le reset ciblé vers `/DV` ou les soumissions HTML acceptées, sans autoriser ECMAScript PDF. Conserver toutes les ressources retournées avec le HTML.

Les [graphiques](https://pdftoolkit.github.io/fr/modules/to-html/graphics.html) gardent leurs programmes et ressources : `GraphicPdfExporter` produit un PDF isolé, puis `RasterContentRenderer` appelle le `GraphicsRasterizer` fourni par l'application. Le moteur de rendu, l'authentification des entrées chiffrées, les codecs supplémentaires et le respect des permissions par le lecteur HTML restent des capacités explicites. Un profil visuel demandé sans moteur échoue explicitement.

HTML 0.7 consomme les plans décodés du Reader et interprète les priorités PDF de couleur/alpha avant de produire des PNG pour le navigateur. Promotion exacte de profondeur, octets ICC, `Decode` et `SMaskInData` restent distincts du rendu de page. Les cas signés/à grilles distinctes ou de couleur/précision non représentable demandent le moteur explicite ou produisent diagnostics/placeholders ; aucune réduction silencieuse à huit bits n’est annoncée. Le [guide des codecs image](https://pdftoolkit.github.io/fr/modules/to-html/image-codecs.html) consigne les comparaisons navigateur et limites des moteurs couleur.

L'authentification native par mot de passe ou certificat se sélectionne avec un
lecteur explicite passé à `PdfToHtml` ; le
[guide d'authentification](https://pdftoolkit.github.io/fr/modules/to-html/authentication.html)
montre l'opération et la propagation des permissions vérifiées. Le credential
reste explicite et le navigateur doit appliquer les droits exportés.

[Packagist: pdftoolkit/pdf-to-html](https://packagist.org/packages/pdftoolkit/pdf-to-html).

`ContentAppearanceRenderer` réutilise ce moteur de contenu explicite pour les
apparences normales, enfoncées et survolées complètes des boutons. Le [guide des signatures](https://pdftoolkit.github.io/fr/modules/to-html/signatures.html)
montre le certificat choisi par l’application et les résultats liés à la source ;
intégrité mathématique, confiance et permissions des modifications ultérieures
restent distinctes. HTML 0.6 corrige aussi les propriétés marquées combinées, le
repli Unicode partiel, les artifacts des Forms imbriqués et le comportement des
formulaires/listes/attributs. Sa CI exacte vérifie PHP 8.3/8.4/8.5 et les moteurs
Chromium et Firefox.
