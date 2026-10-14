# Guide des composants

Ce guide explique les familles d'objets, leurs responsabilités et leur composition. La [référence API exhaustive](https://pdftoolkit.github.io/reference/index.html) donne ensuite les signatures de chaque classe, interface, enum, méthode et propriété. Les [tutoriels](tutorials/README.md) montrent des documents complets, leurs instructions PDF et leur résultat visuel ; les [recettes](recipes/README.md) combinent plusieurs familles pour un usage concret.

Cette documentation décrit les versions publiées du core et des modules sélectionnées dans le [manifeste de sources](../resources/sources.json). La référence API indique le package de chaque composant et relie sa déclaration au commit exact de la version documentée. Le core 0.7.1, le lecteur PDF 0.2.3, les modules images/fontes 0.1.8 et OpenType indépendant 0.1.0 nécessitent PHP 8.3 ou supérieur et sont vérifiés sous PHP 8.3, 8.4 et 8.5. Le core 0.7 exige aussi PHP en 64 bits ; OpenType reste indépendant du core PDF. Les modules PDF acceptent les séries 0.2 à 0.7 du core ; le lecteur 0.2 accepte la syntaxe PDF 1.0–2.0 et les chaînes UTF-8 PDF 2.0. Avant 1.0, les nouvelles versions mineures peuvent modifier les noms et signatures pour améliorer le modèle ; les versions correctives préservent l'API de leur série.

Le modèle couvre **PDF 1.7 / ISO 32000-1:2008**, le [supplément Adobe niveau 3](adobe-supplement.md), [PDF 2.0 / ISO 32000-2:2020 EC3](pdf-2-0.md) et ses [spécifications complémentaires](pdf-2-0-bundle.md). Les PDF de référence originaux gardent leurs noms fournis et leurs octets dans `resources/reference-documents/` du core. Les grands originaux du bundle sont liés depuis ce site et exclus des archives Composer. La version du runtime PHP est indépendante de celle du format PDF. La [couverture](coverage.md) distingue définitions, constructions natives, règles sémantiques vérifiées et traitements externes.

## Comment lire le modèle

Un fichier se construit en reliant des objets : une page possède un contenu et des ressources, un arbre possède des pages, un catalogue désigne cet arbre, puis un writer sérialise le graphe. Les numéros d'objets et les positions dans le fichier sont déterminés pendant l'écriture.

| Famille | Question à laquelle elle répond | Point d'entrée |
| --- | --- | --- |
| Valeurs PDF | Quelle valeur est écrite : nombre, nom, chaîne, tableau… ? | `BasicType`, `PDF\Syntax\Object` |
| Dictionnaires et définitions | Quelles entrées décrivent cet objet et quels types sont autorisés ? | `Entry`, `SchemaDictionary`, `PDF\Specification` |
| Identité et fichier | Où vivent les objets indirects et comment le lecteur les retrouve-t-il ? | `IndirectReference`, `FileStructure`, `FileWriter` |
| Flux et filtres | Quels octets sont stockés et comment sont-ils encodés ? | `StreamObject`, `Filter` |
| Instructions de contenu | Que doit dessiner ou afficher le lecteur PDF ? | `ContentStreams`, `Operator` |
| Documents et pages | Comment les pages, ressources et informations sont-elles reliées ? | `DocumentCatalog`, `PageTreeNode`, `PageObject` |
| Navigation | Où mènent les signets, liens et destinations nommées ? | `Destination`, `OutlineItem`, `NameTree` |
| Fonctions | Quelle transformation numérique le lecteur doit-il appliquer ? | `FunctionObject`, `PDF\Functions` |
| Formulaires et structure | À quels champs, pages et éléments logiques appartiennent les objets ? | `AcroForm`, `FieldTree`, `StructureTreeRoot` |
| Graphiques natifs | Quels espaces, échantillons, motifs, masques et calques sont déclarés ? | `ColourSpace`, `ImageXObject`, `FormXObject`, `OptionalContentProperties` |
| Écritures spécialisées | Comment organiser, chiffrer ou signer les octets du fichier ? | `LinearizedWriter`, `FileEncryption`, `SignatureWriter` |

Les valeurs composent d'autres objets PDF. Un scalaire PHP intervient principalement à une feuille : nombre, booléen, nom ou octets d'une chaîne. L'[architecture](architecture.md) décrit plus précisément les règles de construction.

## 1. Valeurs primitives et conventions lexicales

### Le contrat `BasicType`

[`BasicType`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/FileStructure/BasicType.php) est le contrat des valeurs PDF. Il expose `toPdf(SerializationContext $context): string` et le contrat PHP `Stringable`. Le contexte permet de sérialiser une valeur qui contient des références et d'empêcher les cycles directs.

L'emplacement du contrat dans `Syntax\FileStructure` ne transforme pas toutes les valeurs en fichiers. Un `NameType` reste un nom, et un `ArrayType` reste un tableau de valeurs. Un document complet s'écrit à travers `FileStructure`.

### Les huit familles d'objets PDF

| Terme PDF | Classes | Rôle et contraintes principales |
| --- | --- | --- |
| Boolean | [`BooleanType`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Object/BooleanType.php) | Valeur `true` ou `false`. |
| Numeric | [`NumericType`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Object/NumericType.php), [`IntegerType`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Object/IntegerType.php), [`RealType`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Object/RealType.php) | Valeur numérique finie ; écriture sans notation exponentielle. Les sous-types expriment un integer ou un real lorsque cette distinction est utile. |
| String | [`StringType`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Object/StringType.php), [`LiteralString`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Object/StringObject/LiteralString.php), [`HexadecimalString`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Object/StringObject/HexadecimalString.php) | Suite d'octets représentée par une chaîne littérale ou hexadécimale. |
| Name | [`NameType`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Object/NameType.php) | Identifiant PDF sensible à la casse ; le `/` et l'échappement des octets sont produits à l'écriture. |
| Array | [`ArrayType`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Object/ArrayType.php) | Suite ordonnée de `BasicType`. |
| Dictionary | [`DictionaryType`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Object/DictionaryType.php) | Collection d'entrées nommées ; une clé ne peut pas être déclarée deux fois au constructeur. |
| Stream | [`StreamObject`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Object/StreamObject.php) | Dictionnaire accompagné d'octets ; le flux est écrit comme objet indirect. |
| Null | [`NullType`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Object/NullType.php) | Valeur PDF `null`, notamment utilisée pour certains paramètres de destination. |

Par exemple, un rectangle PDF contient quatre nombres ; son type dédié exprime cette structure :

```php
use PDF\Syntax\DataStructure\Rectangle;
use PDF\Syntax\Object\NumericType;

$mediaBox = new Rectangle(
    new NumericType(0),
    new NumericType(0),
    new NumericType(612),
    new NumericType(792),
);
```

[`Rectangle`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/DataStructure/Rectangle.php) décrit `[x_min y_min x_max y_max]`, et non `[x y largeur hauteur]`. Les coordonnées du contenu dépendent ensuite de l'espace courant et de ses transformations. Le [tutoriel dessin](tutorials/03-graphics.md) explique cette distinction avec un rendu.

### Octets d'une chaîne et texte Unicode

Une `LiteralString` reçoit des **octets**. Elle échappe les parenthèses, les barres obliques inverses et les caractères nécessaires à la syntaxe. Une `HexadecimalString` reçoit également des octets et produit leur représentation hexadécimale. Ces deux classes ne choisissent pas l'encodage d'une police.

[`TextString`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/DataStructure/TextString.php) représente le *text string* de la norme : elle accepte de l'UTF-8 valide et le convertit en ASCII ou UTF-16BE avec BOM. Elle convient, par exemple, aux titres documentaires et aux titres de signets.

La chaîne affichée par l'opérateur `Tj` doit correspondre à l'encodage de la police sélectionnée. Passer un `TextString` Unicode à `ShowText` ne fournit donc pas automatiquement une police Unicode ni le codage de ses glyphes. Le [tutoriel pages et texte](tutorials/02-pages-and-text.md) explicite les choix d'encodage des exemples.

[`Date`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/DataStructure/Date.php) construit une date PDF depuis un `DateTimeImmutable`, en conservant son décalage UTC. Les types de [`LexicalConvention`](https://github.com/PDFToolkit/pdf/tree/v0.7.1/src/Syntax/LexicalConvention) représentent les fins de ligne, espaces blancs et délimiteurs du langage PDF. Ce sont des éléments de syntaxe ; une application compose généralement les objets de niveau supérieur qui les utilisent.

## 2. Entrées, dictionnaires et schémas

### Une entrée est elle-même un objet

[`Entry`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Object/DictionaryObject/Entry.php) relie un `NameType` à un `BasicType`. La clé possède sa propre identité de valeur PDF ; la valeur peut être un dictionnaire, un tableau ou une référence.

```php
use PDF\Syntax\Object\DictionaryObject\Entry;
use PDF\Syntax\Object\DictionaryType;
use PDF\Syntax\Object\NameType;
use PDF\Syntax\Object\NumericType;

$original = new DictionaryType(
    new Entry(new NameType('ExampleNumber'), new NumericType(12)),
);
$modified = $original->with(
    new Entry(new NameType('ExampleNumber'), new NumericType(24)),
);
```

`with()` remplace ou ajoute l'entrée dans une **nouvelle instance**. `$original` conserve sa valeur 12. `without()` produit aussi une nouvelle instance. Il faut conserver la valeur retournée. `get()` retourne une valeur PDF ; `entries()` permet d'examiner les objets `Entry`.

Le dictionnaire générique accepte des noms arbitraires. Un dictionnaire spécialisé ajoute les contraintes de son rôle : types autorisés, champs structurels calculés ou entrées obligatoires.

### Définition de norme et instance PDF

[`SchemaDictionary`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Specification/SchemaDictionary.php) compose un [`TableDefinition`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Specification/TableDefinition.php). Il vérifie les types des entrées connues au constructeur, à l'ajout par `with()` et pendant `validate()`. La sérialisation appelle `validate()` et vérifie les exigences inconditionnelles.

[`SchemaEntry`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Specification/SchemaEntry.php) compose une [`EntryDefinition`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Specification/EntryDefinition.php). Il vérifie la valeur avant de l'associer à la clé normalisée. Les entrées à clé variable demandent un `NameType` explicite.

Une entrée générique permet une extension explicite. Lorsqu'elle utilise une clé déjà définie, elle reste soumise à la contrainte de cette clé. Les exigences conditionnelles et héritées ainsi que les relations entre objets doivent être traitées par les composants spécialisés et par l'application lorsque leur validation n'est pas encore implémentée.

### Lire et composer les classes générées

Les trois parties d'une table ont des rôles distincts :

| Exemple de classe | Responsabilité |
| --- | --- |
| [`AnnotationDictionaryTable164Definition`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Specification/Definition/AnnotationDictionaryTable164Definition.php) | Définition immuable de la table 164, avec ses sources et contraintes. |
| [`AnnotationDictionaryTable164`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Specification/Dictionary/AnnotationDictionaryTable164.php) | Instance PDF des entrées communes aux annotations. |
| [`SubtypeEntry`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Specification/Dictionary/AnnotationDictionaryTable164/SubtypeEntry.php), [`RectEntry`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Specification/Dictionary/AnnotationDictionaryTable164/RectEntry.php) | Entrées nommées `/Subtype` et `/Rect`, avec leurs types autorisés. |

Un dictionnaire commun d'annotation peut ainsi être construit avec des objets d'entrée :

```php
use PDF\Specification\Dictionary\AnnotationDictionaryTable164;
use PDF\Specification\Dictionary\AnnotationDictionaryTable164\ContentsEntry;
use PDF\Specification\Dictionary\AnnotationDictionaryTable164\RectEntry;
use PDF\Specification\Dictionary\AnnotationDictionaryTable164\SubtypeEntry;
use PDF\Syntax\DataStructure\Rectangle;
use PDF\Syntax\DataStructure\TextString;
use PDF\Syntax\Object\NameType;
use PDF\Syntax\Object\NumericType;

$annotation = new AnnotationDictionaryTable164(
    new SubtypeEntry(new NameType('Text')),
    new RectEntry(new Rectangle(
        new NumericType(72), new NumericType(600),
        new NumericType(96), new NumericType(624),
    )),
    new ContentsEntry(new TextString('Une note associée à cette page.')),
);
```

Cet extrait construit l'objet ; il faut encore l'insérer, par référence, dans le tableau `/Annots` d'une page pour le rendre accessible au lecteur. Le [tutoriel liens](tutorials/05-links.md) montre cet assemblage complet avec un autre sous-type d'annotation.

La table indiquée dans le nom rattache chaque classe à la norme et distingue des tableaux portant des titres proches. Les dictionnaires d'entrées supplémentaires composent leurs définitions communes : le [`Type2ShadingDictionaryTable80`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Specification/Dictionary/Type2ShadingDictionaryTable80.php) utilise, par exemple, les entrées communes de la table 78 et les entrées spécifiques de la table 80. Le [tutoriel dégradé](tutorials/07-gradient.md) les assemble.

Les 263 dictionnaires et leurs 1 405 classes d’entrée couvrent les tables d’entrées ISO 32000-1 recensées. ISO 32000-2 possède son propre catalogue : 306 dictionnaires et 1 709 entrées, dont 1 702 fixes et sept variables. Les noms PDF restent sensibles à la casse : `/OP` et `/op` sont deux clés différentes, même lorsque les classes PHP doivent employer un suffixe pour conserver cette distinction.

## 3. Références, identité et sérialisation

### Une référence vise une instance

[`IndirectReference`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Object/IndirectReference.php) désigne un objet. Deux références vers **la même instance** permettent de partager cet objet dans le fichier. Deux objets de même contenu restent deux instances distinctes ; le writer n'effectue pas de déduplication par comparaison de leurs valeurs.

```php
use PDF\Document\Fonts\StandardFont;
use PDF\Document\Fonts\Type1Font;
use PDF\Syntax\Object\IndirectReference;

$font = new Type1Font(StandardFont::Helvetica);
$firstUse = new IndirectReference($font);
$secondUse = new IndirectReference($font);
```

Lorsque ces références sont accessibles dans le même graphe de fichier, elles désignent le même numéro d'objet. Ce numéro est attribué pendant l'écriture. La référence peut également recevoir un [`ObjectIdentifier`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Object/IndirectObject/ObjectIdentifier.php) explicite, composé d'un [`ObjectNumber`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Object/IndirectObject/ObjectNumber.php) et d'un [`GenerationNumber`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Object/IndirectObject/GenerationNumber.php).

[`IndirectObject`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Object/IndirectObject.php) représente une valeur munie de son identifiant lorsqu'un contrôle explicite du corps du fichier est nécessaire.

### Le contexte appartient à une écriture

[`SerializationContext`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Serialization/SerializationContext.php) tient la correspondance entre instances et identifiants. Il réserve les identifiants explicites avant d'attribuer les identifiants automatiques et contrôle les conflits. Il existe pour une écriture donnée ; aucun registre global ne partage les numéros entre documents.

Les cycles passent par des références indirectes. Ainsi, une page référence son parent et le parent référence ses enfants. Un cycle de valeurs directement imbriquées est refusé. Le contexte vérifie aussi que deux instances ne réclament pas le même numéro et qu'une instance ne réclame pas deux identifiants.

Les objets de graphe doivent être configurés avant l'écriture. Modifier l'arbre pendant sa sérialisation empêcherait d'obtenir un fichier cohérent.

## 4. Fichier, références croisées et objets compressés

[`FileStructure`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/FileStructure.php) compose un [`FileHeader`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/FileStructure/FileHeader.php), un [`FileBody`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/FileStructure/FileBody.php), la référence de racine et d'éventuelles entrées de trailer. Le header exprime la version PDF ; [`PdfVersion`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/FileStructure/PdfVersion.php) expose les versions 1.0 à 1.7.

[`FileWriter`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Serialization/FileWriter.php) transforme ce graphe en octets. Il parcourt les références accessibles, écrit les objets et mesure les offsets. Il produit les références croisées et le trailer. `startxref` désigne la position réelle de la section correspondante.

`FileStructure::toPdf()` retourne les octets du fichier. `writeTo()` les écrit dans un chemin de fichier choisi par l'application. Ces opérations construisent le document en mémoire ; la limite de mémoire de l'application reste donc un élément du dimensionnement.

### Révisions et identités historiques

[`FileRevision`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/FileStructure/FileRevision.php) est l'instantané produit par `FileStructure::toRevision()`. Ses octets restent figés. Ses [`RevisionObject`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/FileStructure/RevisionObject.php) conservent la valeur effective, les alias d'identité et une copie des entrées du dictionnaire au moment de l'écriture. Un builder mutable n'est donc pas reparcouru lorsqu'une référence historique est réutilisée.

[`IncrementalUpdate`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/FileStructure/IncrementalUpdate.php) compose la révision précédente, un `FileBody` de modifications explicites et d'éventuelles entrées de trailer. [`IncrementalWriter`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Serialization/IncrementalWriter.php) ajoute les nouveaux objets, garde les numéros des remplacements, hérite le trailer et produit `/Prev`. [`CrossReferenceSection`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/FileStructure/CrossReferenceSection.php) représente les enregistrements de cette section ; [`CrossReferenceLimits`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/FileStructure/CrossReferenceLimits.php) borne la capacité cumulée. Voir le [tutoriel des révisions](tutorials/11-incremental-update.md).

| Composant | Représentation PDF |
| --- | --- |
| [`CrossReferenceFormat`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/FileStructure/CrossReferenceFormat.php) | Choix explicite entre table, stream et références hybrides. |
| [`CrossReferenceTable`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/FileStructure/CrossReferenceTable.php), [`CrossReferenceEntry`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/FileStructure/CrossReferenceEntry.php) | Section `xref` classique et ses entrées. |
| [`CrossReferenceStream`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/FileStructure/CrossReferenceStream.php) | Flux de références croisées. |
| [`CrossReferenceStreamFreeEntry`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/FileStructure/CrossReferenceStreamFreeEntry.php), [`CrossReferenceStreamInUseEntry`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/FileStructure/CrossReferenceStreamInUseEntry.php), [`CrossReferenceStreamCompressedEntry`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/FileStructure/CrossReferenceStreamCompressedEntry.php) | Entrées de type 0, 1 et 2 : libre, objet autonome ou membre d'un flux d'objets. |
| [`ByteOffset`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/FileStructure/ByteOffset.php) | Position mesurée en octets. |
| [`FileTrailer`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/FileStructure/FileTrailer.php) | Dictionnaire du trailer et fin de fichier. |
| [`ObjectStream`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/FileStructure/ObjectStream.php), [`ObjectStreamEntry`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/FileStructure/ObjectStreamEntry.php) | Groupe d'objets embarqués dans un flux `/ObjStm`. |

Un `ObjectStream` exige une version PDF 1.5 au minimum et des références croisées au format stream ou hybride. Ses membres reçoivent les entrées de type 2 correspondantes et ne sont pas écrits une seconde fois comme objets autonomes. Le [tutoriel objets compressés](tutorials/08-object-stream.md) montre le corps du fichier et ces relations.

### Écriture linéarisée

[`LinearizedWriter`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Serialization/LinearizedWriter.php) calcule l'ordre
physique du document et les tables d'indices binaires de l'annexe F. Les objets
de [`Syntax\Linearization`](https://github.com/PDFToolkit/pdf/tree/v0.7.1/src/Syntax/Linearization) représentent les
dépendances, offsets, références partagées et indications de pages. Cette
écriture produit elle-même les octets ; le [tutoriel 16](tutorials/16-linearization.md)
explique leur contrôle avec qpdf. Les variantes prises en charge et celles qui
restent à compléter sont enregistrées dans la [couverture](coverage.md).

Le premier [tutoriel](tutorials/01-first-document.md) expose l'assemblage classique jusqu'à l'appel de `writeTo()`.

## 5. Flux et filtres

Un [`StreamObject`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Object/StreamObject.php) reçoit des octets ou un `ContentStreams`, un dictionnaire et une suite d'objets [`Filter`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Filters/Filter.php). Il calcule `/Length`, `/Filter` et `/DecodeParms`. Ces entrées sont gérées par le flux ; les fournir manuellement est refusé.

`/Length` compte les octets **après encodage**, en excluant la fin de ligne de délimitation. [`StreamExtent`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Object/StreamObject/StreamExtent.php) porte ce nombre. Un flux est écrit indirectement ; on utilise une `IndirectReference` lorsqu'il est la valeur d'une entrée de dictionnaire. `PageObject` crée cette référence pour le flux de contenu reçu directement au constructeur.

Les filtres natifs sont [`ASCIIHexDecode`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Filters/ASCIIHexDecode.php), [`ASCII85Decode`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Filters/ASCII85Decode.php), [`FlateDecode`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Filters/FlateDecode.php), [`RunLengthDecode`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Filters/RunLengthDecode.php) et [`LZWDecode`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Filters/LZWDecode.php). Leurs noms expriment le **décodage effectué par le lecteur PDF** ; leurs objets appliquent l'encodage nécessaire à l'écriture.

[`TiffPredictor`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Filters/TiffPredictor.php) et
[`PngPredictor`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Filters/PngPredictor.php) transforment les lignes
d'échantillons avant Flate ou LZW, avec un [`PredictorLayout`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Filters/PredictorLayout.php)
explicite aux profondeurs 1/2/4/8/16 bits. Ces prédicteurs PDF ne décodent pas un
fichier PNG ; le [tutoriel 19](tutorials/19-filters-predictors.md) montre les octets
et les paramètres nécessaires.

La suite de filtres est donnée dans l'ordre du décodage. Les encodages s'appliquent en sens inverse. Par exemple, une suite ASCII85 puis Flate déclare que le lecteur retire d'abord ASCII85, puis décompresse Flate.

[`EncodedData`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Filters/EncodedData.php) déclare des données **déjà encodées**, avec un [`FilterName`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/Filters/FilterName.php). Il peut, par exemple, déclarer des octets JPEG associés à `DCTDecode`. Il ne lit pas d'image, n'applique pas de codec et ne convertit pas un bitmap en JPEG. Il doit être le dernier filtre de décodage et recevoir des données binaires ; le traitement `Crypt` exige une prise en charge de la sécurité du document.

Le [tutoriel images](tutorials/06-images.md) compare une image XObject réutilisable et une inline image. Une [`InlineImage`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/ContentStreamsResources/Operators/InlineImage.php) regroupe `BI`, `ID` et `EI` en un objet atomique ; les restrictions sur son dictionnaire et ses octets évitent une délimitation ambiguë.

### Fichiers JPEG et PNG

Les composants de [`Document\Images`](https://github.com/PDFToolkit/pdf/tree/v0.7.1/src/Document/Images) sont des objets PDF du core. [`ImageSamples`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Images/ImageSamples.php) associe dimensions, disposition des composantes et octets ; [`SampledImage`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Images/SampledImage.php) sépare couleur et alpha. [`DCTImage`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Images/DCTImage.php) conserve des octets encodés, leurs dimensions, leur disposition et la transformation de couleur explicite, sans inspecter un format de fichier externe.

Le module optionnel [`pdftoolkit/pdf-images`](https://github.com/PDFToolkit/pdf-images) reçoit un [`ImageFileBytes`](https://github.com/PDFToolkit/pdf-images/blob/v0.1.8/src/ImageFileBytes.php), sans lire de chemin ni d'URL. [`ImageImportLimits`](https://github.com/PDFToolkit/pdf-images/blob/v0.1.8/src/ImageImportLimits.php) borne les octets, pixels, dimensions et chunks. [`PngImageDecoder`](https://github.com/PDFToolkit/pdf-images/blob/v0.1.8/src/PngImageDecoder.php) reconstruit les échantillons couleur et alpha ; [`JpegImageReader`](https://github.com/PDFToolkit/pdf-images/blob/v0.1.8/src/JpegImageReader.php) inspecte les marqueurs et couleurs du fichier, puis produit un `DCTImage` du core.

[`ImageXObjectFactory`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Images/ImageXObjectFactory.php) compose le dictionnaire normalisé de la table 89 et ses flux. Il crée un `/SMask` indirect pour l'alpha et fournit les paramètres DCT ou Flate appropriés. Il ne choisit ni le nom de ressource ni la matrice de peinture. Le [tutoriel des fichiers image](tutorials/10-image-files.md) montre ces opérations et les modes supportés.

### Échantillons et XObjects natifs

[`SampleLayout`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Images/SampleLayout.php) accepte les profondeurs
1/2/4/8/16 bits et un espace couleur explicite. [`SamplePacker`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Graphics/XObjects/SamplePacker.php)
empaquette les valeurs en alignant chaque ligne à l'octet.
[`ImageXObject`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Graphics/XObjects/ImageXObject.php) compose ces données
avec Decode, un stencil, un masque par intervalle ou un masque souple. `MatteColour`
porte les calculs de précomposition ; les relations avec le parent et les
dimensions sont contrôlées.

[`EncodedImageXObject`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Graphics/XObjects/EncodedImageXObject.php) reçoit
des octets déjà encodés et leurs déclarations PDF. Il ne vérifie pas le contenu
des codecs DCT/JPX/JBIG2/CCITT. [`FormXObject`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Graphics/XObjects/FormXObject.php)
possède ses instructions, ressources, BBox et Matrix, avec d'éventuels Group,
Ref et OC. Les noms de ressources des instructions typées et les composantes
des espaces explicitement sélectionnés sont vérifiés ; l'état graphique hérité
de l'appelant reste un paramètre de cette composition. Le
[tutoriel 21](tutorials/21-native-graphics.md) montre ces objets ensemble.

## 6. Instructions de contenu, dessin et texte

### `ContentStreams` contient des instructions

[`ContentStreams`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/ContentStreamsResources/ContentStreams.php) compose une suite ordonnée d'objets [`Operator`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/ContentStreamsResources/Operator.php). Il ne représente pas un dictionnaire de flux. `StreamObject` prend en charge le stockage de ses instructions dans le fichier.

Chaque opérateur décrit un token PDF et ses opérandes typés. `with()` retourne un nouveau `ContentStreams` contenant les instructions supplémentaires. `validate()` contrôle les états et les imbrications avant l'émission des octets.

```php
use PDF\Syntax\ContentStreamsResources\ContentStreams;
use PDF\Syntax\ContentStreamsResources\Operators\BeginTextObject;
use PDF\Syntax\ContentStreamsResources\Operators\EndTextObject;
use PDF\Syntax\ContentStreamsResources\Operators\MoveTextPosition;
use PDF\Syntax\ContentStreamsResources\Operators\SetTextFontAndSize;
use PDF\Syntax\ContentStreamsResources\Operators\ShowText;
use PDF\Syntax\Object\NameType;
use PDF\Syntax\Object\NumericType;
use PDF\Syntax\Object\StreamObject;
use PDF\Syntax\Object\StringObject\LiteralString;

$instructions = new ContentStreams(
    new BeginTextObject(),
    new SetTextFontAndSize(new NameType('F1'), new NumericType(18)),
    new MoveTextPosition(new NumericType(72), new NumericType(720)),
    new ShowText(new LiteralString('Bonjour PDF')),
    new EndTextObject(),
);
$contents = new StreamObject($instructions);
```

Cet extrait produit `BT`, `/F1 18 Tf`, `72 720 Td`, `(Bonjour PDF) Tj`, puis `ET`. `/F1` doit être défini dans les ressources de la page. La validation du contenu ne résout pas tous les noms de ressources et ne vérifie pas toutes les relations avec un espace colorimétrique ; leur assemblage reste explicite.

### Familles d'opérateurs

| Famille | Exemples de classes et tokens | Effet |
| --- | --- | --- |
| Graphics state | `SaveGraphicsState` (`q`), `RestoreGraphicsState` (`Q`), `SetLineWidth` (`w`), `SetGraphicsStateParameters` (`gs`) | Sauvegarder, restaurer ou configurer l'état graphique. |
| Transformations | `ConcatenateMatrix` (`cm`) | Modifier la transformation courante. |
| Path construction | `MoveTo` (`m`), `LineTo` (`l`), `CurveTo` (`c`), `AppendRectangle` (`re`), `CloseSubpath` (`h`) | Construire un chemin sans encore le peindre. |
| Path painting et clipping | `StrokePath` (`S`), `FillPathNonzero` (`f`), `ClipPathNonzero` (`W`), `EndPath` (`n`) | Peindre le chemin ou terminer l'application d'un clipping. |
| Couleurs | `SetStrokingRGBColor` (`RG`), `SetNonstrokingRGBColor` (`rg`), variantes gray, CMYK, espaces et patterns | Définir les couleurs de contour et de remplissage. |
| Text state | `SetTextFontAndSize` (`Tf`), `SetCharacterSpacing` (`Tc`), `SetWordSpacing` (`Tw`), `SetTextLeading` (`TL`) | Configurer police, taille, espacements et interligne. |
| Text positioning et showing | `SetTextMatrix` (`Tm`), `MoveTextPosition` (`Td`), `ShowText` (`Tj`), `ShowTextWithIndividualGlyphPositioning` (`TJ`) | Positionner et afficher les octets de texte. |
| XObjects et shadings | `InvokeXObject` (`Do`), `PaintShading` (`sh`) | Invoquer une ressource nommée. |
| Marked content | `BeginMarkedContent` (`BMC`), `BeginMarkedContentWithProperties` (`BDC`), `EndMarkedContent` (`EMC`) | Associer une structure marquée à une séquence de contenu. |
| Compatibility | `BeginCompatibilitySection` (`BX`), `EndCompatibilitySection` (`EX`) | Représenter les sections de compatibilité prévues par PDF. |
| Type 3 glyph metrics | `SetGlyphWidth` (`d0`), `SetGlyphWidthAndBoundingBox` (`d1`) | Déclarer les métriques initiales d'un flux de glyphe Type 3. |

Les classes se trouvent dans [`Operators`](https://github.com/PDFToolkit/pdf/tree/v0.7.1/src/Syntax/ContentStreamsResources/Operators). La référence API détaille chacune de leurs signatures. L'inventaire représente les 73 tokens, dont le token historique `F` et les trois délimiteurs de l'inline image.

La validation empêche notamment les objets texte imbriqués, les chemins inachevés, les restaurations `Q` sans sauvegarde `q`, les scopes marqués qui se croisent et les instructions de dessin incompatibles avec un objet texte. Un clipping `W` ou `W*` doit être suivi d'un opérateur qui termine le chemin.

[`Type3GlyphContentStream`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/ContentStreamsResources/Type3GlyphContentStream.php) représente un flux `CharProcs`. Il exige `d0` ou `d1` au début et applique les contraintes d'un glyphe non coloré lorsque `d1` est utilisé. Ce composant ne construit pas à lui seul toute une police Type 3.

### Valeurs de graphics state et text state

[`Matrix`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Graphics/CoordinateSystems/Matrix.php) contient les six composantes d'une transformation. [`LineDashPattern`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Graphics/GraphicsState/LineDashPattern.php), [`LineCapStyle`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Graphics/GraphicsState/LineCapStyle.php), [`LineJoinStyle`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Graphics/GraphicsState/LineJoinStyle.php) et [`RenderingIntent`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Graphics/GraphicsState/RenderingIntent.php) donnent des objets ou enums aux paramètres correspondants. [`TextRenderingMode`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Text/TextRenderingMode.php) exprime les modes de peinture et de clipping du texte.

Ces objets décrivent les valeurs passées aux instructions. Ils ne calculent pas de mise en page et ne dessinent pas dans un canvas PHP. Le lecteur PDF exécute les instructions une fois le document ouvert. Les [tutoriels dessin](tutorials/03-graphics.md) et [texte](tutorials/02-pages-and-text.md) montrent leurs effets.

### Espaces couleur, motifs et shading

Les objets de [`Graphics\ColourSpaces`](https://github.com/PDFToolkit/pdf/tree/v0.7.1/src/Graphics/ColourSpaces) construisent
CalGray, CalRGB, Lab, ICCBased, Indexed, Separation, DeviceN et Pattern. Ils
contrôlent nombres de composantes, plages, palettes, fonctions de teinte et
relations NChannel. Les calculs propres à CalGray/CalRGB/Lab sont disponibles ;
un profil ICC reste fourni par l'application, sans moteur de gestion ICC implicite.

[`TilingPattern`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Graphics/Patterns/TilingPattern.php) représente une cellule
et ses pas de répétition. [`ShadingPattern`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Graphics/Patterns/ShadingPattern.php)
compose un shading. Les sept types de [`Shadings`](https://github.com/PDFToolkit/pdf/tree/v0.7.1/src/Graphics/Patterns/Shadings)
comprennent de vrais flux de triangles et patches, avec quantification Decode,
empaquetage des bits et réutilisation géométrique. Le
[tutoriel 17](tutorials/17-colours-patterns.md) présente leurs rendus.

La vérification d'un motif stencil suit le contenu typé, y compris formes,
images alternatives et programmes Type3. Elle examine conservativement tous
les CharProcs de la police sélectionnée ; elle n'interprète pas les caractères
effectivement affichés ni des instructions fournies comme octets opaques.

### Transparence, halftones et contenu optionnel

[`GraphicsStateParameters`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Graphics/GraphicsState/GraphicsStateParameters.php)
construit ExtGState avec ses valeurs, fonctions et priorités. `GraphicsStateScope`
conserve explicitement les états sauvegardés. `BlendFunction` fournit les calculs
locaux des modes de mélange et de composition ; `SoftMask` associe une forme de
transparence à un masque alpha ou de luminosité. Les objets de
[`Halftones`](https://github.com/PDFToolkit/pdf/tree/v0.7.1/src/Graphics/Halftones) construisent les types 1/5/6/10/16 et leurs
vraies données de seuil. Cela décrit les opérations PDF ; le rendu des groupes,
l'application des profils ICC et le screening d'un dispositif restent externes.

[`OptionalContentProperties`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Graphics/OptionalContent/OptionalContentProperties.php)
déclare les groupes du catalogue et leurs configurations. OCG, OCMD et expressions
de visibilité composent leurs identités ; `GroupStates` et `UsageEvaluator`
calculent leurs états à partir de paramètres explicitement fournis. Les références
au catalogue, intentions, groupes radio et conditions d'usage sont contrôlées.
Le [tutoriel 21](tutorials/21-native-graphics.md) montre un contenu visible et caché.

## 7. Catalogue, pages et héritage

[`DocumentCatalog`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/DocumentStructure/DocumentCatalog.php) est le dictionnaire racine `/Catalog`. Son constructeur reçoit la racine de l'arbre de pages et crée `/Type` et `/Pages`. Il compose la définition du tableau 28 pour vérifier ses autres entrées. Le graphe protège les champs structurels contre le remplacement et la suppression par des entrées génériques.

[`PageTree`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/DocumentStructure/PageTree.php) est le contrat des éléments de l'arbre : [`PageTreeNode`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/DocumentStructure/PageTree/PageTreeNode.php) représente `/Pages`, et [`PageObject`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/DocumentStructure/PageTree/PageObject.php) représente une feuille `/Page`.

`PageTreeNode::addKid()` rattache un enfant au builder existant. Chaque enfant appartient à un seul parent. L'arbre produit `/Kids`, `/Parent` et `/Count`, et empêche les cycles. Une page doit être configurée avant son rattachement : elle ne peut plus ensuite être clonée ou recevoir une modification de dictionnaire par `with()`.

`PageObject` reçoit sa `Rectangle` de `/MediaBox`, ses ressources et son contenu. `/MediaBox` et `/Resources` peuvent aussi être hérités d'un ancêtre. Leur résolution effective est vérifiée au moment où la page est parcourue pour l'écriture. Un tableau `/Contents` doit contenir des références vers des flux.

Les objets d'entrée de [`PageDictionary`](https://github.com/PDFToolkit/pdf/tree/v0.7.1/src/Syntax/DocumentStructure/PageDictionary) expriment notamment `MediaBox`, `CropBox`, `BleedBox`, `TrimBox`, `ArtBox`, `Rotate`, `UserUnit` et `Resources`. Les constructeurs spécialisés conservent la responsabilité des champs qu'ils gèrent eux-mêmes.

Les entrées de [`CatalogDictionary`](https://github.com/PDFToolkit/pdf/tree/v0.7.1/src/Syntax/DocumentStructure/CatalogDictionary) relient les structures documentaires : `Names`, `Outlines`, `Metadata`, `PageLabels`, `AcroForm`, `ViewerPreferences` et les autres clés normalisées. [`PageLayout`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/PageLayout.php) et [`PageMode`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/PageMode.php) représentent les valeurs d'affichage du catalogue. Une définition d'`AcroForm`, par exemple, permet de construire ses entrées ; elle n'implémente pas automatiquement toutes les règles de comportement des formulaires.

### Champs et structure logique

[`AcroForm`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Forms/AcroForm.php) compose un `FieldTree` avec les
valeurs héritées, noms qualifiés, flags et ordre de calcul. Les champs texte,+bouton, choix et signature possèdent leurs objets ; les widgets séparés ou
fusionnés relient ces champs à leurs pages et apparences. `WidgetAppearance`
compose N/R/D ; un état AS est exigé dès qu'une de ces branches contient un
dictionnaire d'états. Le [tutoriel 14](tutorials/14-acroform-fields.md) montre leur construction.
[`Forms\Fdf`](https://github.com/PDFToolkit/pdf/tree/v0.7.1/src/Document/Forms/Fdf) construit aussi le fichier FDF et l'export
des champs explicitement sélectionnés. Les traitements XFA et l'exécution des
actions JavaScript restent des responsabilités distinctes.

[`StructureTreeRoot`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Structure/StructureTreeRoot.php) relie les
éléments logiques, leurs parents, contenus MCID/MCR et références OBJR. Le graphe
dérive ParentTree et IDTree, compose RoleMap/ClassMap et résout les attributs
Layout/List/PrintField/Table selon les règles prises en charge. `PageContentSequence`
représente les fragments d'un même contenu logique de page. La validation vérifie
leurs identités, les propriétés MarkInfo et les relations balisées décrites dans
la [couverture](coverage.md). Le [tutoriel 15](tutorials/15-tagged-structure.md)
construit trois pages avec paragraphe, tableau et lien. Les instructions sont
typées ; l'ordre de lecture visuel, le reflow et une certification PDF/UA ne sont
pas déduits automatiquement.

Le [premier document](tutorials/01-first-document.md) présente une page ; le [tutoriel pages et texte](tutorials/02-pages-and-text.md) montre des pages partageant des ressources et des propriétés héritées.

Pour consulter des pages d'un PDF existant, le module optionnel
[`PageTreeReader`](https://github.com/PDFToolkit/pdf-reader/blob/v0.2.3/src/PageTreeReader.php)
parcourt et vérifie son arbre. Il produit un
[`ReadPageTree`](https://github.com/PDFToolkit/pdf-reader/blob/v0.2.3/src/ReadPageTree.php)
dont les [`ReadPage`](https://github.com/PDFToolkit/pdf-reader/blob/v0.2.3/src/ReadPage.php)
gardent leurs dictionnaires source et leurs
[`PageAttributes`](https://github.com/PDFToolkit/pdf-reader/blob/v0.2.3/src/PageAttributes.php)
effectifs. [`PageContentsReader`](https://github.com/PDFToolkit/pdf-reader/blob/v0.2.3/src/PageContentsReader.php)
résout séparément les flux locaux de chaque page, sans décodage implicite.
Le [guide des modules](packages.md#lire-un-pdf-externe) montre cette construction ;
ces vues de lecture ne remplacent pas les objets de génération du core.

## 8. Ressources, polices et informations documentaires

### Ressources nommées

[`ResourceDictionary`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/ResourceDictionary.php) compose le tableau 33. Les objets de [`Document\Resources`](https://github.com/PDFToolkit/pdf/tree/v0.7.1/src/Document/Resources) définissent les catégories `ExtGState`, `ColorSpace`, `Pattern`, `Shading`, `XObject`, `Font`, `Properties` et `ProcSet`.

Chaque catégorie associe des noms locaux à des objets PDF. Le nom `/F1` dans un opérateur `Tf` désigne donc une entrée du dictionnaire `/Font` des ressources accessibles à cette page. Il ne désigne pas directement le nom de base `/Helvetica` de la police.

Réutiliser la même instance de police, d'image ou de shading par référence permet de la partager entre pages. Les noms de ressource et les objets vers lesquels ils pointent restent explicites. `ProcSet` représente une entrée prévue par PDF 1.7 et dépréciée dans cette spécification ; les nouveaux exemples n'ont pas besoin de l'utiliser.

### Polices

[`StandardFont`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Fonts/StandardFont.php) enumère les quatorze polices Type 1 standard. [`Type1Font`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Fonts/Type1Font.php) construit leur dictionnaire `/Type /Font`, `/Subtype /Type1` et `/BaseFont`, tout en permettant des entrées supplémentaires explicites. Les trois champs gérés ne peuvent être remplacés ou supprimés.

Pour une fonte incorporée, le module optionnel [`pdftoolkit/pdf-fonts`](https://github.com/PDFToolkit/pdf-fonts) analyse le TrueType statique avec [`FontProgram`](https://github.com/PDFToolkit/pdf-fonts/blob/v0.1.8/src/TrueType/FontProgram.php). Son [`CharacterMapFactory`](https://github.com/PDFToolkit/pdf-fonts/blob/v0.1.8/src/TrueType/CharacterMapFactory.php) produit un [`CharacterMap`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Fonts/CharacterMap.php) du core, composé de [`CharacterMapping`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Fonts/CharacterMapping.php) explicites. Les Unicode distincts gardent des CID distincts même s'ils pointent le même glyphe, afin de préserver leur extraction. Le service [`TextEncoder`](https://github.com/PDFToolkit/pdf-fonts/blob/v0.1.8/src/TrueType/TextEncoder.php) produit les codes à deux octets attendus par Identity-H.

[`CIDFontProgram`](https://github.com/PDFToolkit/pdf-fonts/blob/v0.1.8/src/TrueType/CIDFontProgram.php) prépare les octets du programme complet pour [`FontFile2`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Fonts/FontFile2.php), avec les tables et checksums appropriés au CIDFont. [`FontDescriptor`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Fonts/FontDescriptor.php), [`CIDFontType2`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Fonts/CIDFontType2.php) et [`Type0Font`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Fonts/Type0Font.php) composent les dictionnaires normalisés du core. [`CIDToGIDMap`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Fonts/CIDToGIDMap.php), les largeurs et [`ToUnicodeCMap`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Fonts/ToUnicodeCMap.php) donnent leurs correspondances propres. Le module fournit un `FontDescriptorFactory` qui convertit les métriques TrueType en valeurs du descripteur ; le core accepte directement ces valeurs PDF. Le [tutoriel TrueType et Unicode](tutorials/09-embedded-font.md) montre le graphe complet.

[`Type3Font`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Fonts/Type3Font.php) compose les CharProcs dessinés,
Différences d'encodage, largeurs, Matrix et ressources. Les fontes simples Type1,
MMType1 et TrueType disposent de métriques et programmes explicitement associés ;
les fontes CID Type0/Type2 portent leurs cartes et largeurs horizontales ou
verticales `DW2`/`W2`. Le [tutoriel 22](tutorials/22-native-fonts.md) montre ces
constructions natives.

Les [`CMaps`](https://github.com/PDFToolkit/pdf/tree/v0.7.1/src/Document/Fonts/CMaps) composent codespaces, correspondances
CID, plages notdef, séquences Unicode, mode d'écriture et héritage UseCMap.
`ToUnicodeCMap` écrit les programmes correspondants ; le
[tutoriel 18](tutorials/18-cmaps.md) utilise un encodage différent d'Identity-H.
Les noms et contraintes PDF sont distincts d'un lecteur de programmes de fonte.
Le core vérifie aussi l'identité des tags de sous-ensemble dans le document ;
il ne crée pas les sous-ensembles de programmes ni la composition des scripts
complexes. L'application fournit ses polices et leurs droits d'utilisation.

### `/Info` et metadata streams

[`DocumentInformation`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/DocumentInformation.php) compose les objets de [`Document\Information`](https://github.com/PDFToolkit/pdf/tree/v0.7.1/src/Document/Information) : `Title`, `Author`, `Subject`, `Keywords`, `Creator`, `Producer`, `CreationDate`, `ModDate` et `Trapped`. Les champs textuels utilisent un `TextString`, les dates un `Date`, et `Trapped` un enum dédié. Une référence vers ce dictionnaire est ajoutée sous `/Info` dans le trailer.

`XmpPacket` compose des propriétés explicites, bags, séquences et alternatives localisées ; `XmpLanguageAlternative` représente `dc:title` avec `x-default` et les langues choisies. `MetadataStream` écrit du RDF/XML UTF-8 échappé et `MetadataEntry` relie indirectement le flux à son propriétaire. Les déclarations et `ClaimData` peuvent décrire le document, un objet d’information ou une séquence marquée selon ce propriétaire. `DeclarationsPdfaExtensionSchema` fournit un schéma d’extension choisi explicitement. Ces affirmations d’auteur ne sont ni des certificats de conformité ni un validateur général de vocabulaire XMP ; le XML opaque de l’appelant et la cohérence avec `/Info` demandent leurs propres contrôles.

### Propriété PDF 2.0 et structure qualifiée

Les propriétés nommées des métadonnées sont résolues dans les ressources réelles de la page, de la Form, du motif de pavage ou du CharProc Type 3. Le writer fige les faits du contenu typé émis, y compris pour les révisions incrémentales. Les références inline vers un flux de métadonnées, les noms de ressource introuvables et les mauvais types cibles sont refusés. Les contrôles de fichiers associés suivent la portée des objets d’information plutôt qu’une liste fermée de propriétaires.

`DocumentPart`, `DocumentPartRoot`, `DocumentPartEntry` et `DocumentPartMetadata` construisent `/DPartRoot`, la hiérarchie, les plages de pages et `/DPM`. La validation du graphe contrôle les liens parent/page réciproques, l’ordre des plages et les types de valeurs DPM permis. `EncryptedPayload` et une file specification construisent un PDF externe non chiffré autour d’un PDF interne chiffré fourni, avec AF, EmbeddedFiles et une Collection masquée ; l’enveloppe n’analyse ni ne déchiffre son contenu. `UseBlackPointCompensation` écrit exactement `ON`, `OFF` ou `Default` ; le lecteur PDF et le périphérique de sortie réalisent l’opération couleur.

`StructureNamespace`, `StructureRole` et `NamespaceRoleMap` qualifient les rôles de structure. `NamespaceRoleResolver` résout les mappings avec détection de cycles et `StructureInclusionRules` applique TS 32005 aux rôles parent/enfant réels. `WtPdfAudit` retourne des échecs et constats en attente pour un niveau réutilisation ou accessibilité choisi explicitement. Ses contrôles bornés couvrent le texte typé utilisé, les métadonnées, la structure et les annotations ; l’ordre de lecture, l’utilité du texte alternatif, la fidélité du sens Unicode et les preuves sur les programmes de fonte externes demandent encore une vérification. Aucune certification WTPDF ou PDF/UA automatique n’est annoncée.

Les tutoriels expliquent [les métadonnées/déclarations et parties](tutorials/28-pdf20-metadata-declarations.md), [les contenus chiffrés enveloppés](tutorials/29-pdf20-encrypted-payload.md) et [la structure qualifiée avec rapports d’audit](tutorials/30-pdf20-tagged-namespaces.md).

## 9. Destinations, plans et arbres de clés

### Destinations et actions

[`Destination`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Destinations/Destination.php) est la base des destinations explicites. [`XYZ`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Destinations/XYZ.php), [`Fit`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Destinations/Fit.php), [`FitH`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Destinations/FitH.php), [`FitV`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Destinations/FitV.php), [`FitR`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Destinations/FitR.php), [`FitB`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Destinations/FitB.php), [`FitBH`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Destinations/FitBH.php) et [`FitBV`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Destinations/FitBV.php) décrivent une page cible et un mode de cadrage.

La page cible est un objet, directement reçu par le constructeur ou désigné par une référence. Les paramètres absents de `XYZ` deviennent des valeurs PDF `null`, qui ont un sens défini par la norme.

Une destination décrit une vue ; une action décrit une opération à effectuer. Les tables générées modélisent les dictionnaires d'actions et les annotations de lien. Le [tutoriel liens](tutorials/05-links.md) relie une annotation à une destination interne et à une URI externe.

`StructureDestination` et `DestinationView` ajoutent les cibles sémantiques PDF 2.0.
La résolution suit le contenu réel dans l’ordre des enfants ; une cible sans
contenu se replie sur la première page. Actions et dictionnaires de destination
nommés conservent leur repli de page à côté de `SD`. `RemoteStructureDestination`
représente un ID externe en octets sans ouvrir un autre fichier.
Le [tutoriel des destinations de structure](tutorials/34-pdf20-structure-destinations.md)
montre les vrais liens et les contrôles du graphe figé.

### Document outline

[`OutlineDictionary`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/OutlineDictionary.php) représente la racine du plan. [`OutlineItem`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/OutlineItem.php) reçoit un titre `TextString`, une destination ou un dictionnaire d'action, son état ouvert ou fermé et ses entrées supplémentaires. [`OutlineParent`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/OutlineParent.php) porte le contrat d'un parent de plan.

`addItem()` rattache les éléments et les sous-éléments. Les builders calculent les liens `/Parent`, `/Prev`, `/Next`, `/First`, `/Last` et les comptes de descendants visibles ; ces champs ne doivent pas être fabriqués par des entrées génériques. Un élément ne peut être rattaché à plusieurs parents et les cycles sont refusés. Le [tutoriel navigation](tutorials/04-navigation.md) explique le résultat dans le panneau des signets.

### Name trees et number trees

[`NameTree`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/DataStructure/NameTree.php) et [`NameTreeEntry`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/DataStructure/NameTreeEntry.php) associent des clés `StringType` à des valeurs PDF. [`NumberTree`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/DataStructure/NumberTree.php) et [`NumberTreeEntry`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/DataStructure/NumberTreeEntry.php) emploient des clés `IntegerType`.

Le constructeur reçoit des entrées de feuille ou une collection
[`NameTreeChildren`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/DataStructure/NameTreeChildren.php) /
[`NumberTreeChildren`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/DataStructure/NumberTreeChildren.php) pour
une branche. Les clés et intervalles sont triés ; doublons, descendants vides
et recouvrements sont refusés. `/Kids` et `/Limits` sont dérivés de ces objets ;
`with()` et `without()` ne permettent pas d'altérer cette structure.

[`NameDictionary`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Syntax/DocumentStructure/NameDictionary.php) associe des catégories nommées à des name trees. Il peut, par exemple, relier des destinations nommées au catalogue. Les number trees servent entre autres aux labels de pages. Ce sont des structures de classement définies par PDF, distinctes des noms locaux du dictionnaire de ressources.

## 10. Les quatre types de fonctions PDF

[`FunctionObject`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Functions/FunctionObject.php) expose le domaine, la plage éventuelle et les nombres de composantes d'entrée et de sortie. [`Domain`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Functions/Domain.php) et [`Range`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Functions/Range.php) composent des [`NumberInterval`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Functions/NumberInterval.php). [`NumberArray`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Functions/NumberArray.php) exprime les tableaux numériques complémentaires.

Ces composants produisent une définition de fonction que le lecteur PDF interprète. La bibliothèque ne fournit pas un moteur d'évaluation numérique universel des fonctions.

| FunctionType | Classe | Composition et contrôles principaux |
| --- | --- | --- |
| 0 — Sampled | [`SampledFunction`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Functions/SampledFunction.php) | Grille multidimensionnelle, nombre de sorties et valeurs échantillonnées. [`SamplingSize`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Functions/SamplingSize.php), [`SampleBitDepth`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Functions/SampleBitDepth.php), [`SampleValues`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Functions/SampleValues.php) et [`InterpolationOrder`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Functions/InterpolationOrder.php) décrivent la grille et son empaquetage. Le nombre de composantes doit correspondre au produit des tailles et des sorties. |
| 2 — Exponential interpolation | [`ExponentialInterpolationFunction`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Functions/ExponentialInterpolationFunction.php) | Une entrée et des vecteurs `C0`, `C1` de même taille ; `N` définit l'exposant. Les restrictions du domaine tiennent compte des exposants fractionnaires et négatifs. |
| 3 — Stitching | [`StitchingFunction`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Functions/StitchingFunction.php) | Une entrée partagée entre des sous-fonctions compatibles ; `Bounds` et `Encode` décrivent les subdivisions et les mappings. Les fonctions doivent avoir le même nombre de sorties. |
| 4 — PostScript calculator | [`PostScriptCalculatorFunction`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Functions/PostScriptCalculatorFunction.php) | Un flux contenant une procédure typée du sous-ensemble calculator autorisé par PDF. |

Pour le type 2, une interpolation de 0 à 1 s'écrit :

```php
use PDF\Functions\Domain;
use PDF\Functions\ExponentialInterpolationFunction;
use PDF\Functions\NumberInterval;
use PDF\Syntax\Object\NumericType;

$function = new ExponentialInterpolationFunction(
    new Domain(new NumberInterval(new NumericType(0), new NumericType(1))),
    new NumericType(1),
);
```

Les valeurs par défaut sont `C0 = [0]` et `C1 = [1]`. Avec `N = 1`, la fonction est linéaire. Le [tutoriel dégradé](tutorials/07-gradient.md) utilise trois composantes de sortie pour produire une couleur RGB.

Pour le type 4, [`Calculator\Procedure`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Functions/Calculator/Procedure.php) compose des objets [`Instruction`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Functions/Calculator/Instruction.php), dont [`Number`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Functions/Calculator/Number.php), l'enum [`Operator`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Functions/Calculator/Operator.php) et des procédures imbriquées. Il n'existe pas d'exécution de code PHP ou de programme PostScript libre ; les objets produisent les instructions calculator autorisées. La validité complète d'un calcul, de ses effets de pile et de ses résultats demande toutefois une validation sémantique supplémentaire.

## 11. Sources et objets de définition

Les définitions conservent les informations nécessaires pour remonter à la norme :

| Composant | Informations portées |
| --- | --- |
| [`SourceReference`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Specification/SourceReference.php) | Standard, tableau, clause éventuelle, nom du document, page physique du PDF et empreinte du document source. |
| [`Requirement`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Specification/Requirement.php) | Exigence de présence, avec son caractère inconditionnel ou conditionnel. |
| [`ObjectTypeConstraint`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Specification/ObjectTypeConstraint.php) | Familles de valeurs, règles d'objet direct ou indirect et autres contraintes de type prises en charge. |
| [`EntryDefinition`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Specification/EntryDefinition.php) | Nom, type, présence, description et source d'une entrée. |
| [`TableDefinition`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Specification/TableDefinition.php) | Collection d'entrées et composition explicite de tables communes. |
| [`ImplementationCorrection`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Specification/ImplementationCorrection.php) | Décision d'implémentation documentée lorsque le texte source est incohérent. |
| [`Catalogue`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Specification/Catalogue.php) | Collection immuable de définitions choisies et construite par l'appelant. |

Ces objets ne chargent pas de JSON à l'exécution. Les inventaires sous [`resources/iso32000-1`](https://github.com/PDFToolkit/pdf/tree/v0.7.1/resources/iso32000-1) servent aux outils de génération et de vérification. Les classes générées se construisent avec leurs définitions immuables. La [documentation de spécification](specification.md) explique la génération reproductible et la correction documentée de `/Prev`.

Le namespace `PDF\Specification\Adobe` compose les définitions ISO et les ajouts du supplément. Chaque entrée conserve sa propre origine. Les objets `DeveloperPrefix`, `DeveloperExtension`, `DeveloperExtensionEntry` et `DeveloperExtensions` construisent la déclaration d'extension du catalogue ; toutes ses valeurs sont directes, conformément à ISO 7.12.1. `BatesArtifact` représente la pagination Bates et `WindowDimension` des dimensions résolues et cohérentes. Le [tutoriel 13](tutorials/13-adobe-extensions.md) montre la déclaration et la pagination dans un PDF complet.

### Sécurité et signatures

[`HistoricalStandardSecurityHandler`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Security/HistoricalStandardSecurityHandler.php)
construit les mécanismes ISO par mot de passe R=2/3/4, avec RC4 ou AESV2 selon
la révision. Le mécanisme Adobe R=5 ajoute préparation SASLprep Unicode 3.2 et
AES-256. [`PublicKeySecurityHandler`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Security/PublicKeySecurityHandler.php)
compose les destinataires CMS et clés des filtres. `FileWriter` et les écritures
incrémentales reçoivent le `FileEncryption` choisi par l'application ; les backends
AES et CMS utilisant OpenSSL sont optionnels. Le [guide de sécurité](security.md)
et le [guide Adobe](adobe-supplement.md#chiffrement-historique-aes-256) expliquent
les protocoles, validations et limites.

[`PendingSignature`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Document/Signatures/PendingSignature.php) réserve
Contents et ByteRange. [`SignatureWriter`](https://github.com/PDFToolkit/pdf/blob/v0.7.1/src/Serialization/SignatureWriter.php)
fixe les plages d'octets avant le calcul ; `PreparedSignature` remplit ensuite
la réservation sans déplacer les objets. Les trois formats de signature ISO et
les signatures successives sont vérifiés par des outils indépendants. Le
[tutoriel 20](tutorials/20-signed-document.md) montre CMS détaché. L'identité,
chaîne de certificats et politique de confiance sont explicitement choisies ;
le résultat cryptographique ne certifie pas à lui seul cette confiance.

`ModernStandardSecurityHandler`, `ModernFileEncryption` et `ModernEncryptionDictionary` fournissent AES-CBC R=6 de PDF 2.0 et AES-GCM R=7 de TS 32003. `SignatureDigestMethod` et `ModernCmsSignatureBackend` sélectionnent SHA-3/SHAKE et les opérations RSA, ECDSA à courbe nommée ou EdDSA prises en charge, avec contrôle des combinaisons exactes. `IsoExtensions` déclare séparément chaque spécification technique ISO choisie. `PdfMacTokenComposer` authentifie les octets réels des fichiers initiaux, incrémentaux ou linéarisés, de façon autonome ou attachée à la signature CMS. Chaque révision demande sa propre opération MAC.

`PendingDocumentTimestamp` et `Rfc3161TimestampBackend` ajoutent des horodatages documentaires RFC 3161 avec un fournisseur de jeton et un vérificateur d’autorité explicites. `DocumentSecurityStore`, `ValidationDataStream` et `ValidationRelatedInformation` stockent les preuves DSS/VRI sans les récupérer ni leur faire confiance automatiquement. La politique restreinte `DocumentTimestampRevisionPolicy` vérifie le delta de maintenance figé avant d’appliquer l’exception DocMDP pour horodatage/DSS ; les autres changements de révision et FieldMDP restent contraints. Ces mécanismes n’établissent pas une validation générale à long terme ni la confiance PKI. Le [tutoriel de signature moderne](tutorials/31-pdf20-modern-signature.md), le [tutoriel horodatage/DSS](tutorials/32-pdf20-timestamp-dss.md), le [guide du bundle](pdf-2-0-bundle.md) et la [revue de sécurité](security.md) expliquent les frontières des algorithmes, fournisseurs et preuves.

Une classe de dictionnaire d'encryption, de signature, de font descriptor, de multimédia ou de structure balisée décrit des entrées du format. Les traitements sont portés par leurs mécanismes dédiés lorsqu'ils existent, comme le programme TrueType et l'incorporation CID. La présence d'un dictionnaire ne réalise pas le chiffrement, la signature, la lecture multimédia ou la conformité d'une structure balisée. La référence API documente les objets disponibles ; la couverture annoncée reste celle de leurs comportements effectivement implémentés.

### Mesures géospatiales

`GeographicCoordinateSystem` et `ProjectedCoordinateSystem` déclarent le système
de référence. `GeospatialControlPoints` possède les coordonnées locales/réelles
appariées ; `GeospatialMeasure`, `Viewport` et `Viewports` associent ces valeurs
aux pages, Form et images. Unités d’affichage, matrice affine projetée à douze
valeurs et nuages de points typés ont leurs objets distincts. La validation du
graphe effectif contrôle aussi les dictionnaires bruts et les révisions conservées.
Le [tutoriel géospatial](tutorials/33-pdf20-geospatial.md) explique ces relations
sans laisser entendre qu’il s’agit d’un convertisseur de projections SIG.

## 12. Choisir un composant et poursuivre

Pour créer un document, commencer par les objets de domaine : pages, ressources, contenu et catalogue. Utiliser les entrées générées pour les concepts encore dépourvus d'objet spécialisé ou pour ajouter une entrée normalisée explicite. Employer un `Entry` générique pour une extension dont le nom et le sens sont maîtrisés par l'application.

Les constructeurs vérifient les valeurs locales, les builders vérifient la propriété des graphes, et l'écriture vérifie les états qui nécessitent un graphe complet. L'application choisit les données, les chemins, les ressources accessibles et les actions qu'elle accepte. La [documentation de sécurité](security.md) précise les limites et les protections disponibles.

Pour passer à des documents complets, suivre les [tutoriels](tutorials/README.md), comparer leur aperçu au PDF téléchargeable sur le site, puis étudier la [recette de tableau](recipes/table.md). Pour lire un PDF externe, utiliser le [module lecteur](packages.md#lire-un-pdf-externe), avec résolution et décodage explicites. Pour ajouter un comportement au modèle, consulter l'[architecture](architecture.md), la [couverture de spécification](specification.md) et la [référence API](https://pdftoolkit.github.io/reference/index.html).

Pour dériver le contenu logique en HTML, le module optionnel PDF vers HTML 0.2.0 construit des objets source immuables et des processeurs propres au document, en utilisant le lecteur 0.2.3+. `HtmlDeriver` produit HTML, CSS, ressources et diagnostics ; `GraphicPdfExporter` conserve les programmes et prépare un PDF isolé pour le moteur `GraphicsRasterizer` de l'application. `FormActionPolicy` distingue le reset/soumission de formulaire de l'autorisation d'ECMAScript PDF. Les [exigences](https://pdftoolkit.github.io/fr/modules/to-html/requirements.html), [politiques](https://pdftoolkit.github.io/fr/modules/to-html/policies.html) et [graphiques](https://pdftoolkit.github.io/fr/modules/to-html/graphics.html) documentent les règles natives et ces capacités explicites ; le [tutoriel 35](tutorials/35-derive-html.md) montre la vraie sortie.
