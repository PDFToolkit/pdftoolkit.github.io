# Architecture

Cette architecture décrit le core et les modules optionnels aux versions publiées
sélectionnées dans le [manifeste de sources](../resources/sources.json).
Le [guide des composants](components.md) présente leurs objets concrets ; la
[couverture](coverage.md) distingue constructions natives, règles vérifiées et
travail restant dans les références Adobe/ISO conservées et leur bundle complémentaire.

## Domaine PDF

Le namespace `PDF\Syntax` suit les termes de la référence. `BasicType` est le contrat des valeurs PDF. Les sous-types représentent les huit familles d'objets ; les objets indirects et leurs références ont des classes distinctes. Les classes spécialisées, comme `Rectangle`, ajoutent des contraintes à ces valeurs sans convertir leur contenu en scalaires PHP.

Les arguments scalaires sont limités aux feuilles : une valeur numérique, une suite d'octets, un nom ou un booléen. Les compositions utilisent des objets. Une entrée de dictionnaire possède un `NameType` et un `BasicType` ; une instruction de contenu possède des opérandes typés.

Chaque classe porte une responsabilité propre au modèle PDF. Les noms et les abstractions suivent la norme ; l'API peut évoluer pour respecter ce modèle. Les raccourcis de composition et les fonctions de mise en page appartiennent aux futures bibliothèques de confort.

## Frontière des packages

Le core `roukmoute/pdf` contient les objets et les mécanismes PDF décrits par la référence Adobe/ISO. `pdftoolkit/pdf-reader`, `pdftoolkit/pdf-images` et `pdftoolkit/pdf-fonts` sont des modules optionnels séparés. Ils dépendent du core, qui ne dépend d'aucun d'eux. Leurs parseurs ne sont pas chargés par une application qui installe seulement le core.

Les noms, valeurs, références et structures sont partagés par composition. Le core définit notamment les échantillons et flux image, le programme incorporé `/FontFile2`, les métriques, les fontes CID et les CMaps PDF. L'inspection d'un JPEG, le décodage PNG et l'analyse des tables TrueType sont des traitements de formats externes dans leurs modules. Le [guide des packages](packages.md) détaille ces frontières et les installations.

## Définition et instance

`PDF\Specification` sépare une définition de norme et un objet PDF. `SourceReference`, `Requirement`, `ObjectTypeConstraint`, `EntryDefinition` et `TableDefinition` sont des valeurs immuables. Les définitions générées sont construites par des instances, sans lecture JSON à l'exécution ni registre global.

Les dictionnaires et entrées générés portent les termes du tableau d'origine. Le numéro de tableau stabilise les noms de classes lorsque plusieurs tableaux portent un titre similaire. Les noms de classes PHP sont uniques sans tenir compte de la casse ; les noms PDF restent sensibles à la casse. Cette différence est vérifiée dans les tests.

ISO 32000-1, les extensions Adobe et ISO 32000-2 possèdent des namespaces de
catalogue et des éditions de source distincts. `NameAlternatives` représente un
ensemble de noms permis explicitement vérifié ; une phrase citant plusieurs noms
ne se réduit pas au premier nom apparemment fixe. Les entrées à clé variable
conservent leur motif source et reçoivent une clé `NameType` explicite. Chaque
correction conserve son autorité et sa page.

Une table d'« additional entries » peut composer les définitions communes de son type. Les entrées inconnues restent accessibles par un objet `Entry` explicite afin de permettre les extensions du format. Ce mécanisme n'autorise pas à contourner les contraintes d'une entrée connue.

`DocumentCatalog` et `ResourceDictionary` composent les définitions des tableaux 28 et 33 pour valider leurs entrées. Le catalogue ajoute les règles de propriété du graphe de pages. Ces règles complètent les contraintes de la définition, qui s'appliquent aussi aux entrées génériques.

## Assemblage des graphes

Les valeurs et définitions ne gèrent pas l'identité d'un fichier. Les références visent leurs objets. Pendant une écriture, `SerializationContext` parcourt les objets accessibles et réserve les identifiants explicites avant d'attribuer les identifiants automatiques. Un même objet reçoit un seul identifiant dans ce fichier.

Les cycles indirects, comme les liens `Parent`/`Kids`, sont permis. Les cycles directs sont refusés. Deux instances distinctes ne peuvent pas réclamer le même numéro, et une instance ne peut pas réclamer deux identifiants.

Les arbres de pages et plans sont assemblés par des builders qui contrôlent le rattachement à un seul parent. Les champs structurels ne peuvent pas être remplacés ou supprimés par une entrée générique. Les arbres de noms et nombres trient leurs clés et vérifient les intervalles de leurs descendants.

Les arbres de champs et de structure logique suivent la même règle de propriété.
Un widget appartient à son champ et à une page ; un contenu marqué appartient à
ses éléments et à son contexte de page ou de forme. Les identités permettent de
dériver les liens ParentTree/IDTree et de contrôler les références. Les groupes
de contenu optionnel ont leurs propres objets, configurations et états de
document ; deux groupes de même nom restent deux identités différentes.

Les constructeurs de valeurs restent immuables. Les builders qui assemblent un
graphe possèdent explicitement leur état local ; ils ne servent pas de registres
globaux et ne sélectionnent pas des pages ou ressources à la place de l'appelant.

## Mécanismes natifs

Les composants spécialisés composent les définitions PDF avec leurs contraintes
couplées : dimensions et composantes d'images, espaces et fonctions de teinte,
coordonnées et bits des maillages, programmes Type3, codespaces et CMaps, états
de champs, classes et attributs de structure. Les flux produits contiennent les
octets du mécanisme, par exemple un mesh, LZW ou des indices de linéarisation.
Une simple déclaration de dictionnaire conserve un rôle distinct.

Les fonctions arithmétiques PDF disponibles reçoivent des objets explicites :
transformation de couleurs calibrées, quantification Decode, précomposition
Matte, mélange local ou évaluation des conditions de visibilité. Elles ne
constituent pas un moteur de rendu, une mise en page ou une analyse de format
externe. Un profil ICC, programme de police ou média demeure une donnée fournie.

## Écriture

`FileWriter` et les objets `CrossReferenceTable`, `CrossReferenceStream` et `ObjectStream` portent la représentation du fichier. Le format de références croisées est choisi par un objet enum `CrossReferenceFormat` : table, stream ou hybride. Les flux d'objets demandent des références stream ou hybrides et PDF 1.5 au minimum.

Le sérialiseur compte des octets, pas des caractères Unicode. Le header utilise le tiret ASCII prescrit, les chaînes échappent leur syntaxe, les noms échappent leurs octets, et les nombres n'utilisent jamais de notation exponentielle. La longueur d'un flux est calculée après l'application des filtres.

Les membres d'un flux d'objets reçoivent des entrées de type 2 dans le flux de références et ne sont pas écrits une seconde fois comme objets autonomes. `startxref` vise le début réel de la section de références.

`LinearizedWriter` planifie les dépendances, l'ordre physique et les tables
d'indices de l'annexe F. `SignatureWriter` prépare une révision dont les
ByteRange sont fixes avant le calcul cryptographique, puis la signature remplit
sa réservation. Le chiffrement des chaînes et flux passe par un `FileEncryption`
et ses backends explicitement choisis. Les offsets sont ceux des octets écrits,
avec les filtres, réservations et paramètres de sécurité applicables.

`PendingSignature` et `PendingDocumentTimestamp` partagent le mécanisme de
réservation via `PendingSignatureDictionary`, avec des types de dictionnaires
et contrats de fournisseurs distincts. `PdfMacTokenComposer` se lie à la clé
de chiffrement réelle et à la révision sérialisée. Il ne remplace ni le fournisseur
de signature ni sa politique de confiance. Les snapshots immuables conservent
les octets et les identités des révisions historiques.

## Validation

Les constructeurs refusent les états localement invalides. Les validations de graphe interviennent au moment de la sérialisation, lorsque les parents et ressources peuvent être établis. Les contraintes conditionnelles de la norme ne sont pas présentées comme automatiquement couvertes tant qu'une validation et un test dédiés ne les prennent pas en charge.

`DocumentGraphValidation` traverse le graphe réel du writer, y compris les
dictionnaires de flux et opérandes typés. Le contrat `CatalogComponent` permet
à un composant de vérifier ses relations avec le catalogue ; `VersionedComponent`
contrôle les fonctions sélectionnées contre la version PDF effective du header
et du catalogue. Les déclarations Adobe et identités de sous-ensemble de fontes
font aussi l'objet de contrôles au niveau du document. La validation s'appuie
sur les valeurs effectives figées lorsqu'une révision est réutilisée.

Ces contrats couvrent les familles et conditions annoncées, sans prétendre
vérifier chaque phrase de la norme. Les tests de graphe ne sont pas une
certification PDF/UA ; une signature valide ne remplace pas la politique de
confiance du certificat. Les [inventaires](coverage.md) conservent ces frontières
et les contraintes ouvertes.

Les tests PHPUnit vérifient des comportements et des contre-exemples ; des lecteurs indépendants contrôlent aussi les fichiers produits. L'analyse PHPStan au niveau 8 et le format PSR-12 font partie de `composer check`.

Le modèle requiert PHP 8.3 ou supérieur en 64 bits, avec des constantes typées, des classes `readonly` et des enums. La CI exécute les vérifications sous PHP 8.3, 8.4 et 8.5. Sous PHP 8.5, l'attribut natif `NoDiscard` signale les résultats ignorés des méthodes immuables qui le déclarent ; ces méthodes construisent les mêmes objets sous les trois versions.

## Extension

Une bibliothèque de confort peut transformer ses propres objets de mise en page en ce modèle. Une nouvelle entrée normalisée peut recevoir un type spécialisé et sa validation, en conservant la définition et sa source. Un nouveau filtre doit réaliser l'encodage qu'il déclare ; un nom de filtre ou une définition de dictionnaire ne suffit pas à revendiquer un codec.

Dans `pdftoolkit/pdf-fonts`, le parcours existant programme TrueType/CID reste explicite. L’adaptateur OpenType accepte aussi CFF1 statique et fournit `TextLayout`, `ShapedText`, `GlyphText` et `PositionedText` pour les étapes GSUB/GPOS choisies et le placement PDF. TrueType et CFF utilisent le même contrat de layout ; l’incorporation relie leurs GID aux CID et séquences d’extraction appropriés. Le choix d’une face de collection est explicite. Le module ne découvre pas de fontes système, ne réalise pas automatiquement itemisation/bidi et ne crée pas d’instance statique depuis une fonte variable.

Le modèle indépendant [OpenType](https://github.com/PDFToolkit/opentype) possède tables, contours, métriques et entrées d’exécution immuables. Il lit SFNT et TTC/OTC et sérialise une face complète choisie ; les plages de fonctionnalités conservent le contexte des clusters source. Axes, métriques et géométrie TrueType/Type 2 CFF/CFF2 sont évalués avec des bornes explicites. Les résultats géométriques ne créent ni instance statique d’une fonte variable ni dictionnaires PDF. Le [registre de couverture](https://pdftoolkit.github.io/fr/modules/opentype/coverage.html) distingue 27 périmètres de tables implémentés, quatre partiels et 19 tables non interprétées ; VM, rastérisation et shaping Unicode complet restent séparés.

Dans `pdftoolkit/pdf-images`, les lecteurs reçoivent `ImageFileBytes` et des budgets d’import par appel. Le PNG devient des échantillons couleur/alpha à leur profondeur exacte après reconstruction non entrelacée ou Adam7, avec déclarations ICC/couleur calibrée explicites. Le JPEG devient un `DCTImage` du core conservant octets encodés, ICC et politique de transformation/Decode. `ImageXObjectFactory` compose dictionnaires et flux sans parser le fichier d’origine. Noms de ressources et matrices de peinture restent explicites.

Dans `pdftoolkit/pdf-reader`, `DocumentReader` lit `FileBytes` avec `ReaderLimits`. Un `ReadDocument` possède références, xrefs, cache et budgets cumulés. L’application demande séparément `resolve()`, `streamData()` ou `imageData()`. Le décodage d’image natif qualifié s’exécute dans un processus borné ; les capacités indisponibles se replient vers la bibliothèque PHP optionnelle. Plans et métadonnées exacts traversent une interface du Reader sans imposer cette dépendance pour analyser les PDF. `ImportSession` copie séparément un graphe choisi vers de nouvelles identités writer avec une politique de flux explicite. Il ne transforme pas les révisions source en autorité native de modification des signatures.

`FileRevision` fige les octets et les liaisons d'identité d'un document. `RevisionObject` conserve ses alias historiques et une copie des entrées de son dictionnaire, pour ne pas reparcourir un builder mutable après écriture. `IncrementalUpdate` sélectionne les changements dans un `FileBody` ; `IncrementalWriter` ajoute les nouveaux octets, hérite le trailer et relie les sections xref. Une référence historique ne déclenche pas de nouvelle sérialisation. Les conteneurs structuraux anciens sont conservés et les membres compressés remplacés utilisent un nouveau conteneur ou un objet autonome.

Les handlers par mot de passe et certificat, identités, permissions et signatures
possèdent leurs objets dans `PDF\Security` et `PDF\Document\Signatures`. Les
backends OpenSSL sont choisis explicitement ; le core n'effectue pas de recherche
automatique de certificats ou de clés sur le disque ou le réseau. La lecture de
fichiers externes, la composition de texte, les moteurs ICC/XFA/3D/multimédia et
la confiance des certificats conservent leurs responsabilités propres.
