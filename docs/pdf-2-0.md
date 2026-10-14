# PDF 2.0 : premiers mécanismes et objets propres à l'édition

Le core **0.6.0** introduit les premiers mécanismes ISO 32000-2:2020, avec des
corrections vérifiées d'Errata Collection 3 (EC3, 2026-06-01). Il conserve PHP 8.3
minimum et la construction explicite, avec des objets propres au document et
sans registre global. Cette version ne prétend pas implémenter tout PDF 2.0
ni garantir sa conformité complète.

## Périmètre de cette version

| Domaine | Construction implémentée | Limite |
| --- | --- | --- |
| Version du fichier | `PdfVersion::PDF20`, en-tête et version effective du catalogue | Déclarer une version ne garantit pas la conformité. |
| Texte des dictionnaires | Objets d'encodage PDFDoc/UTF-16BE et UTF-8 avec BOM, décodage explicite et contrôles de version | Le texte des pages utilise toujours les codes de la police choisie. |
| Fichiers associés | `AFRelationship`, tableaux AF sur les propriétaires pris en charge, ressources MCAF nommées, contrôles de graphe et de révision | Aucun chargement automatique de fichier ou d'URL. |
| Modèle de spécification | Quatre tableaux ISO 32000-2 EC3 et 53 entrées typées | Le catalogue complet reste à construire. |
| Applicabilité et sécurité | Distinction introduit/déprécié/interdit, refus de R=5 en PDF 2.0 et contraintes des permissions à clé publique | Le chiffrement par mot de passe R=6 n'est pas implémenté. |

L'[exemple expliqué](tutorials/27-pdf20-associated-files.md) relie ces objets à
un PDF réel, avec des métadonnées Unicode et un CSV.

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
antérieurs ; PDF 2.0 refuse cette combinaison. R=6 reste à implémenter. Les permissions CMS à clé publique portant sur le document
exigent l’ordre de l’octet le plus significatif en premier, le bit d’accessibilité
10 et les bits réservés 13–32 à 1. Des octets opaques de destinataire seuls ne
prouvent pas ces faits de permissions. Le chiffrement natif AES-256 à clé publique
est disponible en PDF 2.0 sans déclaration d’extension Adobe historique ; il
est distinct du gestionnaire par mot de passe R=6 restant à implémenter. Le chiffrement n'authentifie pas à lui seul
le contenu des pages et ne définit pas la confiance envers le document.

## Implémentations restantes

Le pilote couvre le tableau 29 (32 entrées, pages physiques 113–117), le tableau 43
(16 entrées, pages 149–152), le tableau 356 (quatre entrées, page 744) et le
tableau 409a (une entrée, page 1015). Les classes générées utilisent
`PDF\Specification\Iso32000_2`, séparément des classes ISO1 et Adobe.
Les types, noms Type fixes, entrées requises sans condition et certaines contraintes
de références vérifiées sont exécutables. Les règles contextuelles demandent
des mécanismes natifs.

Le catalogue complet, le chiffrement R=6, les mappings de rôles et graphes natifs
d'espaces de noms, DSS/informations de validation/horodatages, arbres de parties
documentaires, sémantique des enveloppes chiffrées, fonctions géospatiales et autres
mécanismes PDF 2.0 restent à implémenter. Un schéma d'entrée Namespace, DSS ou
DPartRoot n'implémente pas son mécanisme. Le lecteur optionnel reste limité à
son [périmètre PDF 1.0–1.7 documenté](packages.md) ; cette étape du writer ne l'étend pas.

## Source et vérifications

L'original fourni `ISO_32000-2_sponsored_EC3.pdf` est conservé en privé, avec
son nom et ses octets d'origine. Sa copie personnalisée n'est pas un téléchargement
public. Son identité, ses pages physiques et son empreinte figurent dans les
[métadonnées du pilote](https://github.com/PDFToolkit/pdf/blob/v0.6.1/resources/iso32000-2-2020/metadata.json)
et l'[inventaire de couverture](https://github.com/PDFToolkit/pdf/blob/v0.6.1/resources/iso32000-2-2020/coverage.json).
La norme est accessible par l'[accès sponsorisé officiel](https://pdfa.org/sponsored-standards/).

Les [errata publics](https://pdf-issues.pdfa.org/32000-2-2020/) présentent les
[règles corrigées des fichiers associés](https://pdf-issues.pdfa.org/32000-2-2020/clause14.html#14135-associated-files-linked-to-graphics-objects).
Les descriptions du pilote sont des résumés concis rédigés pour le projet,
sans recopier les paragraphes normatifs. Le générateur compare les fichiers
reproductibles ; les tests exercent les types invalides, collisions d'éditions
et provenance des corrections. La validation PDF indépendante contrôle les
objets émis et les octets incorporés. Voir la [couverture des mécanismes](coverage.md)
pour les autres corpus et leurs limites.
