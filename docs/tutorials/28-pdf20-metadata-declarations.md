# 28. Métadonnées XMP, déclarations et parties de document

Le [script complet](https://github.com/PDFToolkit/pdf/blob/v0.9.1/examples/pdf20-metadata-declarations.php)
produit un PDF 2.0 avec un titre bilingue, une déclaration de l'auteur, un rapport
incorporé et des métadonnées distinctes pour le document, une partie documentaire
et une séquence de dessin. Le rectangle coloré utilise la compensation du point
noir. Ces informations sont écrites dans les objets PDF correspondants ; elles
ne se limitent pas aux phrases visibles sur la page.

## Exécuter l'exemple

Depuis un checkout du core **0.7.1**, avec ses dépendances installées :

```bash
php examples/pdf20-metadata-declarations.php metadata.pdf
```

L’exemple fournit Courier avec des [métriques explicites](https://github.com/PDFToolkit/pdf/blob/v0.9.1/examples/fixtures/pdf20-courier-font.php) : FirstChar/LastChar, largeurs ASCII et FontDescriptor. PDF 2.0 ne permet plus d’omettre ces entrées pour les quatorze polices standard. Cette construction n’incorpore pas de programme de fonte ; un profil exigeant l’incorporation demande une fonte explicitement incorporée.


PHP 8.3 ou supérieur suffit. Ce script utilise les objets natifs du core ; aucun
convertisseur d'images ou de fontes n'est nécessaire. L'aperçu et le téléchargement
ci-dessous proviennent du fichier réellement généré.

## Construire un paquet XMP avec des valeurs explicites

`XmpPacket` sérialise des propriétés RDF dans un paquet XML UTF-8. `XmpName`
associe séparément préfixe, URI d'espace de noms et nom local ; `XmlText` contrôle
les caractères XML et échappe le texte. Le BOM UTF-8 du marqueur XMP ne transforme
pas ce paquet en chaîne textuelle PDF : il s'agit du contenu d'un flux XML.

```php
$title = new XmpLanguageAlternative(
    new XmpName('dc', new MetadataUri('http://purl.org/dc/elements/1.1/'), 'title'),
    new XmlText('PDF 2.0 metadata and document parts'),
    new XmpLocalizedText('fr', new XmlText('Métadonnées PDF 2.0 et parties de document')),
);
$metadata = new MetadataStream(new XmpPacket($title, $review));
$catalogMetadata = new MetadataEntry($metadata);
```

`XmpLanguageAlternative` écrit un `rdf:Alt` dont `x-default` est la première
valeur. Les langues sont distinctes, y compris lorsque leur casse diffère.
`MetadataStream` fournit `/Type /Metadata` et `/Subtype /XML`, puis
`MetadataEntry` établit sa référence indirecte. Les flux XML existent depuis
PDF 1.4 ; le fichier de cet exemple choisit explicitement PDF 2.0 pour ses autres
mécanismes. Les propriétés ou préfixes contradictoires sont refusés.

## Déclarer une propriété du document sans inventer une certification

Une `Declaration` contient l'URI de la spécification ou du profil revendiqué.
`Declarations` écrit le tableau non ordonné `pdfd:declarations`, dans l'espace de
noms exact `http://pdfa.org/declarations/`. Chaque déclaration peut contenir un
tableau non ordonné de `ClaimData` : auteur de la revendication, date explicite,
qualifications et URL du rapport.

```php
$review = new Declarations(new Declaration(
    new MetadataUri('https://example.org/pdf/reviewed'),
    new ClaimData(
        new XmlText('PDFToolkit example'),
        new ClaimDate('2026-10-14'),
        claimReport: new ClaimReport('#ef=review.txt'),
    ),
));
```

L'identifiant `example.org` décrit ici un processus de démonstration. La présence
de cette déclaration ne prouve pas une conformité PDF/A, PDF/UA ou WTPDF. Le core
n'ajoute aucune revendication de ce type. `DeclarationsPdfaExtensionSchema` permet
de fournir explicitement la description du vocabulaire exigée dans un contexte
PDF/A ; cette description ne rend pas, à elle seule, un document conforme à PDF/A.

Le fragment `#ef=review.txt` désigne un rapport incorporé par son nom. L'exemple
fournit ses octets, son type MIME et sa date source, l'ajoute à l'arbre
`Names.EmbeddedFiles` et l'associe avec `AFRelationship /Supplement`. Le rapport
devient ainsi accessible aux lecteurs qui affichent les pièces jointes. Les URI
et les noms de fichiers ne déclenchent aucun chargement externe.

## Donner à chaque métadonnée son propriétaire

La déclaration du catalogue porte sur le document ; elle ne s'étend pas à ses
fichiers incorporés ou référencés. Le flux XMP d'une partie documentaire décrit
cette partie, tandis qu'un autre flux décrit uniquement la séquence du rectangle.
Les trois flux gardent des identités et des vocabulaires distincts.

La séquence de dessin utilise une `MetadataPropertyList` sous
`Resources.Properties.ColourInfo`, puis `/Sample /ColourInfo BDC ... EMC`.
La liste est nommée pour que sa référence indirecte vers le flux XML reste hors
de la syntaxe du contenu. Une propriété `Metadata` placée directement dans un
opérande de contenu est refusée. Les références sont résolues dans les ressources
du vrai propriétaire, y compris lorsque le contenu appartient à une révision
déjà émise.

`MetadataResourceLocation` exprime aussi les emplacements précisés par la note
d'application : programme de fonte incorporé plutôt que descripteur de fonte,
flux de motif répétitif, dictionnaire de shading plutôt que son enveloppe de
motif, élément de structure, annotation, groupe de contenu optionnel ou flux 3D.
Le choix appartient à l'application qui connaît la ressource décrite.

## Séparer DPM, parties de document et état graphique

`DocumentPart` porte ici un dictionnaire `DocumentPartMetadata` avec `Job
(Proof 42)` et un flux XMP sous `Metadata`. **DPM et XMP sont deux mécanismes
distincts.** DPM contient des données applicatives typées ; ses clés et les noms
de niveaux suivent la syntaxe XML Name. Ses valeurs sont des chaînes textuelles
ou dates, tableaux, dictionnaires, booléens et nombres.

`DocumentPartRoot` relie le catalogue au nœud. La page référence sa partie via
`DocumentPartEntry`, puis `setPageRange()` définit les bornes de cette même page.
Le constructeur d'arbre gère les parents ; la validation du graphe contrôle les
liens réciproques, l'ordre des pages, l'absence de chevauchement, la couverture
des pages et les niveaux déclarés. DPM n'est pas hérité implicitement d'un parent.

Enfin, `UseBlackPointCompensation(BlackPointCompensation::On)` écrit
`UseBlackPtComp /ON` dans une ressource `GraphicsStateParameters`, sélectionnée
par `gs`. Les deux autres valeurs exactes sont `/OFF` et `/Default`. La couleur
du rectangle appartient à un espace `CalRGB` ; la compensation intervient dans
les conversions de couleur CIE réalisées par le processeur PDF 2.0. Son apparence
dépend du profil de sortie et du lecteur, et `/Default` leur laisse le choix.

## Inspecter les preuves et les sources

`tools/validate_pdf20_metadata.py` vérifie les XML avec un parseur indépendant,
les tableaux RDF, les identités AF et DPart, les types MIME et dates source,
l'état BPC et les opérateurs du contenu avec pypdf. qpdf contrôle le fichier.
Les tests natifs couvrent notamment les caractères XML invalides, les dates
impossibles, les propriétés manquantes et les remplacements incrémentaux
incohérents. Le rendu permet de vérifier séparément la page visible.

Le constructeur de paquets n'analyse aucun XML fourni par l'utilisateur. Une
application qui construit manuellement un flux XML brut reste responsable de
son contenu ; le graphe contrôle ses références et son type PDF. Cette leçon
ne constitue pas une validation générale de toutes les règles ISO 32000-2.

Sources conservées : [PDF Declarations, pages 7–10](https://github.com/PDFToolkit/pdf/blob/v0.9.1/resources/reference-documents/PDF-Declarations.pdf#page=7),
[compensation du point noir, page 4](https://github.com/PDFToolkit/pdf/blob/v0.9.1/resources/reference-documents/PDF20_AN001-BPC.pdf#page=4),
[fichiers associés, pages 7 et 12–13](https://github.com/PDFToolkit/pdf/blob/v0.9.1/resources/reference-documents/PDF20_AN002-AF.pdf#page=7)
et [emplacements des métadonnées, pages 4–10](https://github.com/PDFToolkit/pdf/blob/v0.9.1/resources/reference-documents/PDF20_AN003-ObjectMetadataLocations.pdf#page=4).
Les parties de document sont définies dans [ISO 32000-2, pages physiques 850–853](https://github.com/PDFToolkit/pdf/blob/v0.9.1/resources/reference-documents/ISO_32000-2_sponsored_EC3.pdf#page=850).
La provenance du bundle est l'[accès sponsorisé de la PDF Association](https://pdfa.org/sponsored-standards/).

[Parcours des tutoriels](README.md) · [Guide PDF 2.0](../pdf-2-0.md)
