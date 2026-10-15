# PDF 2.0 : objets, écriture et spécifications complémentaires

Le core **0.11.0** implémente des objets et mécanismes ISO 32000-2:2020, avec des
corrections vérifiées d’Errata Collection 3 (EC3, 2026-06-01). Il nécessite PHP 8.3
ou ultérieur en 64 bits et conserve une construction explicite, des objets propres
au document et aucun registre global. La couverture des tableaux n’établit pas
la conformité conditionnelle, algorithmique ou sémantique complète.

Le [guide des audits de source](source-audits.md) explique les relations de
dictionnaires exécutées et les corrections EC3 exactes des flux xref, de la
priorité de `Path` dans les annotations et des indices de choix. PDF 1.7 et
PDF 2.0 conservent des contrats distincts.

## Périmètre de cette version

| Domaine | Construction implémentée | Limite |
| --- | --- | --- |
| Version du fichier | `PdfVersion::PDF20`, en-tête et version effective du catalogue | Déclarer une version ne garantit pas la conformité. |
| Texte des dictionnaires | PDFDoc/UTF-16BE et UTF-8 avec BOM, décodage explicite et contrôles de version | Le texte des pages utilise les codes de la police choisie. |
| Fichiers associés | AF sur les objets d’information, relations et propriétés MCAF nommées | Aucun chargement automatique de fichier ou d’URL. |
| Modèle de spécification | Inventaire de dictionnaires propre à l’édition, objets d’entrées fixes et variables, tableaux communs et corrections EC3 vérifiées | Les règles contextuelles et algorithmiques restent distinctes des définitions de tableaux. |
| Sécurité | Sécurité par mot de passe R=6, AES-GCM R=7, signatures CMS modernes et PDF MAC | La confiance, la politique de révocation et les choix de déploiement restent explicites. |
| Métadonnées et structure | XMP, déclarations, métadonnées d’objets et de contenu marqué, parties documentaires, enveloppes chiffrées, espaces de noms et règles ISO/TS 32005 | Les déclarations ne prouvent pas la conformité ; les rapports WTPDF conservent des contrôles humains et externes. |
| Conservation des signatures | Horodatages de document, DSS et VRI avec ordre réel des révisions | Les certificats et réponses de révocation fournis sont des preuves à examiner, pas une validation automatiquement digne de confiance. |

L’[exemple des fichiers associés](tutorials/27-pdf20-associated-files.md) relie
ces objets à un vrai fichier. Le [guide du bundle complémentaire](pdf-2-0-bundle.md)
présente les onze sources et les autres tutoriels exécutables.

## Édition, corrections et version du fichier

`SourceEdition` identifie la norme indépendamment du SHA-256 de la copie source
et de la version du fichier produit. `ErrataCollection` sélectionne EC3 sans
renommer l'édition de base 2020. Un `SourceReference` conserve la page PDF
physique, le tableau, la clause, l'identité de copie et l'édition sélectionnée.

ISO 32000-1:2008, le supplément Adobe PDF 1.7 et ISO 32000-2:2020 restent des
corpus séparés. Des numéros de tableaux identiques ont des sens différents :
le tableau 29 définit un nœud de pages dans ISO 32000-1 et le catalogue dans
ISO 32000-2. `Catalogue` refuse le mélange ISO1/ISO2 et les profils ISO2 avec
corrections différentes ; la composition ISO1 + extensions Adobe reste disponible.

EC3 ajoute des corrections, pas seulement du texte sur les pages. Le PDF fourni
contient des annotations de révision, leurs réponses et des pages de remplacement
ajoutées. `Completed` signifie une approbation ISO TC 171 SC 2 WG 8 ; `Accepted`
signifie une approbation du PDF Technical Working Group de la PDF Association.
`ErrataResolution` conserve cette distinction. Ces états ne doivent pas devenir
une affirmation générique d'approbation ISO.

## Chaînes textuelles Unicode

`TextString` reçoit du texte applicatif Unicode valide et un objet d'encodage.
Son `PdfDocOrUtf16TextStringEncoding` par défaut conserve la stratégie
PDFDocEncoding avec repli UTF-16BE. `Utf16BETextStringEncoding` sélectionne
explicitement UTF-16BE ; `Utf8TextStringEncoding` sélectionne UTF-8 PDF 2.0
et son BOM de trois octets.

```php
$title = new TextString('Résumé – fichiers associés', new Utf8TextStringEncoding());
```

Le writer contrôle la version effective des véritables objets textuels du graphe.
Les chaînes UTF-8 nécessitent PDF 2.0. `TextStringDecoder` interprète explicitement
le texte encodé des dictionnaires ; `LiteralString` et `HexadecimalString`
restent des octets.

Une chaîne textuelle de dictionnaire et une chaîne de police `Tj`/`TJ` ont des
rôles différents. Écrire des octets UTF-8 après `Tj` ne fournit pas au lecteur
une correspondance Unicode de police. L'exemple incorpore séparément un programme
TrueType et utilise son encodage CID et sa CMap ToUnicode pour le texte visible.
Voir les [polices incorporées](tutorials/09-embedded-font.md).

## Fichiers associés et contenu marqué corrigé

Une spécification décrit le fichier fourni ; sa relation explique le lien avec
un objet PDF. `AssociatedFileRelationship` encapsule un nom PDF ;
`AFRelationship` expose les valeurs standard Source, Data, Alternative,
Supplement, EncryptedPayload, FormData, Schema et Unspecified. Les noms de
relations personnalisées restent des valeurs explicites.

`AssociatedFiles` contient des dictionnaires de spécification de fichier ;
`AssociatedFilesEntry` fournit `/AF`. Le validateur du graphe vérifie le véritable
propriétaire, le tableau non vide, ses membres et chaque `AFRelationship`.
Une pièce jointe et un fichier associé restent distincts : `Names.EmbeddedFiles`
permet de retrouver une pièce jointe ; `/AF` exprime sa relation avec un objet.
La même spécification de fichier peut participer aux deux constructions.

Pour le contenu marqué, l'erratum EC3 374 remplace la liste de propriétés en
tableau contradictoire par un **dictionnaire contenant `/MCAF`**. Placer ce
dictionnaire dans `Resources.Properties` avec un nom, puis le référencer avec
`/AF /nom BDC … EMC`. Les références indirectes ne peuvent pas apparaître
directement dans un flux de contenu. Les opérateurs ponctuels `DP` et `MP`
ne décrivent pas une séquence associée. La validation native applique aussi
ces règles aux révisions générées effectives.

`PDF\Document\Files\BeginAssociatedFilesMarkedContent` compose l’opérateur BDC
existant avec `/AF` et un nom de ressource ; il n’ajoute aucun jeton à l’annexe A.
Les faits natifs sont figés avec les octets écrits : une modification non préparée
du builder ou un callback de filtre ne réécrit pas le sens d’une ancienne révision.
Les remplacements effectifs de ressources et de Filespec restent vérifiés.
Les octets de flux déclarés opaques restent hors de cette interprétation native.

Les Form XObjects PDF 2.0 doivent avoir leur propre dictionnaire de ressources.
Le MCAF d’une forme utilise ces ressources effectives, y compris les dictionnaires
indirects. Lorsqu’un `Params` de fichier associé est fourni, il nécessite une
`ModDate` source valide ; `PdfDateValidation` vérifie syntaxe bornée, calendrier
et décalages en conservant la représentation d’origine. Aucune date n’est inventée.

## Sécurité et applicabilité des versions

`FeatureApplicability` distingue l'introduction, la dépréciation et l'interdiction
d'une fonctionnalité. Une fonctionnalité dépréciée n'est pas automatiquement
interdite. Une fonctionnalité explicitement interdite ne devient pas valide
parce qu'on écrit un en-tête plus récent. Le graphe et le writer utilisent la
version effective après la déclaration du catalogue.

ISO 32000-2 interdit explicitement la révision 5 historique du gestionnaire
standard de sécurité. Le backend Adobe R=5 reste disponible pour les fichiers
antérieurs ; PDF 2.0 refuse cette combinaison. `ModernStandardSecurityHandler` implémente les données d’authentification R=6 et AES-GCM R=7. Les permissions CMS à clé publique portant sur le document
exigent l’ordre de l’octet le plus significatif en premier, le bit d’accessibilité
10 et les bits réservés 13–32 à 1. Des octets opaques de destinataire seuls ne
prouvent pas ces faits de permissions. Le chiffrement natif AES-256 à clé publique
est disponible en PDF 2.0 sans déclaration d’extension Adobe historique ; il
reste distinct du gestionnaire par mot de passe R=6. AES-GCM authentifie les valeurs chiffrées ; PDF MAC authentifie une révision sérialisée. Aucun de ces mécanismes n’établit la confiance envers les certificats.

## Métriques explicites des polices standard

Le tableau 109 de PDF 2.0, pages physiques 328–329, exige `FirstChar`, `LastChar`,
`Widths` et `FontDescriptor` pour les fontes simples. L’omission historique pour
les quatorze polices standard ne concerne que PDF 1.0–1.7. Un en-tête PDF 2.0
ne rend pas complet un simple `Type1Font(StandardFont::Helvetica)`.

Construire `SimpleFontMetrics` avec des objets `SimpleWidths` et `FontDescriptor`
explicites, ou choisir un programme incorporé avec ses véritables métriques.
Le helper Courier des exemples fournit largeurs ASCII et valeurs du descripteur
déclarées, sans ajouter de parseur de fonte ni de registre au core. L’incorporation
reste un choix distinct. Les contrôles du graphe effectif couvrent aussi les
dictionnaires génériques et les remplacements figés de fontes et ressources.

## Implémentations restantes

Le catalogue des dictionnaires comprend l’inventaire des tableaux de base,
leurs pages de continuation, les clés fixes et variables, les relations entre
tableaux communs et des corrections EC3 explicitement vérifiées. Ses classes
utilisent `PDF\Specification\Iso32000_2`, séparément d’ISO1 et d’Adobe. Les types,
noms fixes, exigences inconditionnelles et contraintes de références vérifiées
sont exécutables ; les mécanismes natifs réalisent les relations contextuelles.

La conformité conditionnelle et sémantique complète, la revue exhaustive EC3,
le rendu et le traitement des couleurs externes ainsi que la certification
automatique d’accessibilité ne sont pas établis par cet inventaire. Le
[relevé de couverture](coverage.md) distingue mécanismes natifs, objets déclaratifs
et travaux restants. Le lecteur optionnel 0.6.0 accepte la [syntaxe PDF 1.0–2.0 et les chaînes UTF-8 PDF 2.0](packages.md), avec ses autres limites explicites.

## Source et vérifications

L’[original `ISO_32000-2_sponsored_EC3.pdf`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/ISO_32000-2_sponsored_EC3.pdf)
est conservé dans le dépôt public du core avec son nom et ses octets d’origine,
après autorisation de redistribution confirmée par le propriétaire du projet.
Les [métadonnées du catalogue](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/iso32000-2-2020/metadata.json)
et l’[inventaire de couverture](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/iso32000-2-2020/coverage.json)
consignent son identité, ses pages physiques et son empreinte. Le fichier fourni
provient de la **PDF Association**, via son [accès sponsorisé officiel](https://www.pdfa.org/sponsored-standards/).
Les deux copies fournies de la norme principale et tous les originaux complémentaires restent dans le dépôt.

Les [errata publics](https://pdf-issues.pdfa.org/32000-2-2020/) présentent les
[règles corrigées des fichiers associés](https://pdf-issues.pdfa.org/32000-2-2020/clause14.html#14135-associated-files-linked-to-graphics-objects).
Les résumés existants rédigés pour le projet possèdent une traduction française.
Les extraits supplémentaires de la source conservent leur anglais d’origine
et sont signalés comme texte normatif. Les générateurs vérifient la reproductibilité ;
les tests exercent les domaines invalides, collisions d’éditions et provenances
de corrections. Des implémentations indépendantes examinent les octets PDF réels,
la cryptographie, les métadonnées et la structure. La [couverture](coverage.md) et
le [guide du bundle](pdf-2-0-bundle.md) précisent les domaines vérifiés et leurs limites.
