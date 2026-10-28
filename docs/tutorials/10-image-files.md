# 10. Importer les octets JPEG et PNG

Le [tutoriel sur les images](06-images.md) construit directement des pixels.
Celui-ci part de fichiers encodés : il sépare leur import de leur représentation
PDF, puis de leur placement. L'exemple utilise le core et le module d'images aux versions publiées sélectionnées par le [manifeste de sources](../../resources/sources.json).

La lecture de ces fichiers appartient au module optionnel
[`pdftoolkit/pdf-images`](https://github.com/PDFToolkit/pdf-images). Les
échantillons, les images DCT et les flux XObject appartiennent au core.
`composer install` dans le checkout du core installe le module pour les exemples ;
une application l'installe depuis Packagist avec
`composer require "pdftoolkit/pdf-images:^0.2.0"`. Le
[guide des packages](../packages.md) explique comment sélectionner aussi
la série du core.

- **Exemple complet :** [image-files.php](https://github.com/PDFToolkit/pdf/blob/v0.11.0/examples/image-files.php).
- **Résultat :** quatre images sur une page Letter, avec un damier révélant la transparence.
- **Données :** [motifs synthétiques MIT](https://github.com/PDFToolkit/pdf-images/blob/v0.2.0/examples/assets/images/README.md), distribués avec le module dans `vendor/pdftoolkit/pdf-images/examples/assets/images/`.
- **Prérequis :** [premier document](01-first-document.md), [dessin](03-graphics.md) et [images](06-images.md).

## 1. Donner des octets, sans déléguer l'accès au fichier

`ImageFileBytes` représente la suite d'octets du fichier. Les importeurs ne
reçoivent aucun chemin et ne chargent aucune URL. Dans l'exemple, l'application
lit quatre fichiers connus dans ses propres ressources, contrôle l'échec de
lecture, puis construit cet objet. Une application web décide elle-même comment
authentifier et limiter un téléversement avant d'en fournir les octets.

```php
use PDF\Images\ImageFileBytes;
use PDF\Images\ImageImportLimits;
use PDF\Images\JpegImageReader;
use PDF\Images\PngImageDecoder;

$limits = new ImageImportLimits(maxEncodedBytes: 1_048_576, maxPixels: 262_144);
$jpeg = (new JpegImageReader($limits))->read(new ImageFileBytes($jpegBytes));
$png = (new PngImageDecoder($limits))->decode(new ImageFileBytes($pngBytes));
```

Les limites sont des objets propres à chaque importeur. Par défaut : 16 MiB
encodés, 16 MiB de données décodées, 4 194 304 pixels, 32 768 pixels par dimension
et 65 536 chunks ou marqueurs. Le PNG compte aussi les octets de filtre et le
développement des indices de palette. Ces plafonds bornent les données du codec ;
le processus PHP doit également disposer de mémoire pour les chaînes temporaires
et le document final. Les produits de dimensions sont vérifiés avant allocation.

## 2. JPEG : préserver la représentation DCT

`JpegImageReader` vérifie le début et la fin du fichier, les longueurs de segments,
la trame, les composants, les tables et les en-têtes de scan. Il accepte le JPEG
DCT Huffman 8 bits de base et progressif. Il ne décode pas les coefficients DCT
et ne prétend pas vérifier chaque bit du codage entropique : cette étape appartient
au lecteur PDF. Le fichier encodé reste exactement le même.

Le `DCTImage` du core expose dimensions, disposition des composantes, transformation couleur, espace ICC éventuel et octets inchangés. Sans profil, gris/RGB utilisent DeviceGray/DeviceRGB. RGB reçoit un `/ColorTransform` explicite : JFIF indique YCbCr, Adobe fournit la valeur de son marqueur, sinon les identifiants reconnus distinguent `1,2,3` de `R,G,B`. Les fragments ICC APP2 gris/RGB/CMYK sont assemblés par numéro de séquence avec taille bornée et conservation exacte des octets du profil.

Adobe CMYK transformation 0 conserve CMYK ; Adobe YCCK transformation 2 choisit `/ColorTransform 1` PDF. Les deux gardent la convention d’inversion Adobe par `/Decode [1 0 1 0 1 0 1 0]`. Les processus JPEG autres que huit bits, arithmétiques ou sans perte restent refusés par cet importeur. Les déclarations de composantes/couleurs ambiguës échouent explicitement. L’orientation EXIF n’est pas appliquée.

## 3. PNG : reconstruire les échantillons

`PngImageDecoder` vérifie signature, cadrage, CRC, chunks critiques, ordre et absence de données après IEND. Les IDAT consécutifs forment un flux zlib borné par la longueur exacte des scanlines attendues. Une fin manquante, une sortie décompressée excessive ou un filtre inconnu sont refusés. Les octets encodés inutilisés après le dernier flux zlib IDAT sont ignorés comme le permet PNG ; des données comprimées supplémentaires dans iCCP restent invalides.

`PngScanlineDecoder` reconstruit les filtres None, Sub, Up, Average et Paeth.
Le résultat est un `SampledImage` : des `ImageSamples` couleur et, si nécessaire,
des `ImageSamples` d'opacité. Chaque objet décrit dimensions, espace de couleur,
profondeur et octets intercalés. Une ligne apparaît dans l'ordre du fichier, depuis
le haut de l'image. Les couleurs ne sont pas prémultipliées par l'alpha.

Le décodeur accepte chaque combinaison statique légale : gris 1/2/4/8/16, palette 1/2/4/8 et RGB/gris-alpha/RGBA 8/16 bits. Les parcours non entrelacé et Adam7 reconstruisent les filtres séparément pour chaque passe. Les indices de palette deviennent RGB huit bits ; couleur/alpha intrinsèque seize bits restent seize bits. `tRNS` compare les échantillons originaux à pleine précision après masquage des bits hauts inutilisés de la clé et produit une opacité huit bits. Alpha zéro est transparent ; la valeur maximale de l’échantillon est opaque.

ICC incorporé prévaut sur sRGB, puis gAMA/cHRM. Les octets ICC sont conservés dans ICCBased ; sRGB utilise le transfert exact par morceaux et conserve l’intention de rendu ; gAMA/cHRM produisent CalGray/CalRGB. La [politique couleur](https://pdftoolkit.github.io/fr/modules/images/png-colour.html) décrit les valeurs explicites pour les métadonnées manquantes. Des échantillons totalement non caractérisés restent dépendants du périphérique. APNG et métadonnées HDR sont refusés ; l’importeur ne tourne pas l’image selon EXIF et n’exécute pas de transformation couleur propre au périphérique.

## 4. Composer l'image XObject et son masque

```php
use PDF\Document\Images\ImageXObjectFactory;

$factory = new ImageXObjectFactory();
$jpegStream = $factory->create($jpeg);
$pngStream = $factory->create($png);
```

Le service compose un `StreamObject` avec les objets d'entrée de la table 89 :
`/Type /XObject`, `/Subtype /Image`, dimensions, espace de couleur et profondeur.
Le JPEG utilise `EncodedData(DCTDecode)` ; les échantillons PNG sont compressés
avec `FlateDecode`. On peut injecter un autre niveau de compression Flate par objet.

`ImageXObjectFactory` est un composant du core. Il reçoit des `DCTImage` ou
`SampledImage` explicites ; il ne parse aucun fichier PNG ou JPEG. Une autre
bibliothèque ou l'application peut construire ces objets sans installer le module.

L’alpha devient un autre flux image, huit ou seize bits selon sa source, en `/DeviceGray`. Une
`IndirectReference` sous `/SMask` le relie à l'image principale. Le writer le
découvre dans le graphe et attribue son numéro, sans registre global. Le masque
doit avoir les mêmes dimensions ; le constructeur le vérifie.

Les entrées qui décrivent les échantillons et les masques sont gérées par cette
composition : une entrée supplémentaire ne peut pas remplacer `/Width`,
`/ColorSpace`, `/Decode` ou `/SMask`. D'autres choix, par exemple `/Interpolate`,
restent des objets d'entrée explicites. Comme pour tout flux, `StreamObject`
gère `/Length`, `/Filter` et `/DecodeParms`.

## 5. Référencer et peindre les images

Le service n'ajoute ni page, ni ressource, ni opérateur. L'exemple construit
`/XObject << /JpegRGB … /PngRGBA … >>` dans le `ResourceDictionary`, puis quatre
groupes `q`, `cm`, `Do`, `Q`. Les matrices fixent 216 × 162 points et la position.
La résolution de 48 × 36 pixels ne détermine donc pas la taille physique du PDF.

Le damier est construit avec des rectangles et des remplissages avant l'image.
Il reste visible sous les PNG partiellement transparents. Les deux JPEG montrent
le même motif en RGB et CMYK : ils permettent de vérifier le sens de `/Decode`.

## Exécuter

```sh
php examples/image-files.php /tmp/image-files.pdf
qpdf --check /tmp/image-files.pdf
```

Les tests comparent les échantillons reconstruits aux motifs originaux et exercent
les cinq filtres, les masques, les CRC, les longueurs tronquées, les indices de
palette invalides et les données zlib excessives. Le résultat PDF se vérifie aussi
avec un lecteur indépendant ; une validation syntaxique ne suffit pas à confirmer
les couleurs et l'opacité.

Références : [PNG, W3C](https://www.w3.org/TR/png/),
[JPEG, ITU T.81](https://www.w3.org/Graphics/JPEG/itu-t81.pdf) et ISO 32000-1,
sections 7.4.8 et 8.9.
