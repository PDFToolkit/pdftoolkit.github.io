"""Explicit site translations and stable locale routes.

Markdown prose is translated in source files. This catalogue only translates the
site's generated interface; PHP snippets and original normative text are kept.
"""

from html import escape
from html.parser import HTMLParser
import re

LANGUAGES = ('en', 'fr')
ENGLISH_ROUTES = {
    'guides/mecanismes.html': 'guides/mechanisms.html',
    'guides/supplement-adobe.html': 'guides/adobe-supplement.html',
    'guides/references-adobe.html': 'guides/adobe-references.html',
    'guides/demarrer.html': 'guides/getting-started.html',
    'guides/composants.html': 'guides/components.html',
    'guides/modules.html': 'guides/packages.html',
    'guides/couverture.html': 'guides/specification.html',
    'guides/securite.html': 'guides/security.html',
    'guides/signalements.html': 'guides/reporting.html',
    'guides/versions.html': 'guides/changelog.html',
}
GROUP_ROUTES = {
    'objets': 'objects', 'fichier': 'file', 'contenu': 'content',
    'document': 'document', 'fonctions': 'functions', 'filtres': 'filters',
    'lexique': 'lexical-conventions', 'norme': 'specification',
    'dictionnaires': 'dictionaries', 'entrees': 'entries', 'definitions': 'definitions',
    'adobe': 'adobe', 'iso2': 'pdf-2-0', 'securite': 'security', 'polices-externes': 'external-fonts',
    'images-externes': 'external-images', 'lecture': 'reader', 'fontes-opentype': 'opentype', 'conversion-html': 'to-html',
}
ENGLISH_ROUTES.update({f'reference/groups/{old}.html': f'reference/groups/{new}.html' for old, new in GROUP_ROUTES.items()})
for module in ('reader', 'images', 'fonts', 'opentype', 'to-html'):
    ENGLISH_ROUTES[f'modules/{module}/signalements.html'] = f'modules/{module}/reporting.html'
    ENGLISH_ROUTES[f'modules/{module}/versions.html'] = f'modules/{module}/changelog.html'


# Project-authored pilot summaries, translated independently of original normative prose.
ISO2_DESCRIPTIONS_FR = {'Identifies the document catalog.': 'Identifie le catalogue du document.',
 'A catalog-level PDF version declaration later than the file header.': 'Déclare dans le catalogue une version '
                                                                        'PDF plus récente que celle de l’en-tête.',
 'Developer extension declarations, held in a direct dictionary.': 'Déclarations d’extensions des développeurs, '
                                                                   'conservées dans un dictionnaire direct.',
 'An indirect reference to the root page-tree node.': 'Référence indirecte vers le nœud racine de l’arbre des '
                                                      'pages.',
 'Page-label ranges with an entry for the first page.': 'Plages de libellés de pages, avec une entrée pour la '
                                                        'première page.',
 'Document name trees; the encrypted-wrapper conditions are separate graph rules.': 'Arbres de noms du document ; '
                                                                                    'les conditions des '
                                                                                    'enveloppes chiffrées '
                                                                                    'relèvent de règles de graphe '
                                                                                    'séparées.',
 'An indirect dictionary of named destinations.': 'Dictionnaire indirect de destinations nommées.',
 'Preferences controlling document presentation.': 'Préférences de présentation du document.',
 'Initial arrangement of displayed pages.': 'Disposition initiale des pages affichées.',
 'Initial document viewing mode.': 'Mode initial de consultation du document.',
 'An indirect reference to the outline hierarchy root.': 'Référence indirecte vers la racine de la hiérarchie des '
                                                         'signets.',
 'An indirect array of article-thread dictionaries.': 'Tableau indirect de dictionnaires de fils de lecture '
                                                      'd’articles.',
 'Initial action or destination.': 'Action ou destination initiale.',
 'Document-wide additional actions.': 'Actions supplémentaires portant sur tout le document.',
 'Document-level URI action information.': 'Informations documentaires pour les actions URI.',
 'Interactive form root.': 'Racine du formulaire interactif.',
 'An indirectly referenced document metadata stream.': 'Flux de métadonnées du document référencé indirectement.',
 'An indirect reference to the logical structure tree root.': 'Référence indirecte vers la racine de l’arbre de '
                                                              'structure logique.',
 'Information about tagged-PDF conventions.': 'Informations sur les conventions du PDF balisé.',
 'Default natural language for document text.': 'Langue naturelle par défaut du texte documentaire.',
 'Historical web-capture information; deprecated in PDF 2.0.': 'Informations historiques de capture web, '
                                                               'dépréciées en PDF 2.0.',
 'Output-intent dictionaries describing rendering conditions.': 'Dictionnaires d’intentions de sortie décrivant '
                                                                'les conditions de rendu.',
 'Document-associated private application data.': 'Données privées d’application associées au document.',
 'Optional-content configuration, required when optional content exists.': 'Configuration du contenu optionnel, '
                                                                           'requise lorsque ce contenu existe.',
 'Document access-permission information.': 'Informations sur les permissions d’accès au document.',
 'Digital-signature legal-content attestations.': 'Attestations de contenu juridique pour les signatures '
                                                  'numériques.',
 'Document requirement dictionaries.': 'Dictionnaires d’exigences documentaires.',
 'Portable-collection presentation; wrapper-specific requirements are separate.': 'Présentation de collection '
                                                                                  'portable ; les exigences des '
                                                                                  'enveloppes sont séparées.',
 'Historical XFA display-regeneration hint; deprecated in PDF 2.0.': 'Indication historique de régénération de '
                                                                     'l’affichage XFA, dépréciée en PDF 2.0.',
 'Document Security Store; validation-data semantics are not implemented by this schema.': 'Document Security '
                                                                                           'Store ; ce schéma '
                                                                                           'n’implémente pas la '
                                                                                           'sémantique des '
                                                                                           'données de '
                                                                                           'validation.',
 'Associated file specifications; their relationships are validated by the native mechanism.': 'Spécifications de '
                                                                                               'fichiers '
                                                                                               'associés, dont '
                                                                                               'les relations '
                                                                                               'sont vérifiées '
                                                                                               'par le mécanisme '
                                                                                               'natif.',
 'An indirect reference to the document-parts hierarchy root.': 'Référence indirecte vers la racine de la '
                                                                'hiérarchie des parties documentaires.',
 'Filespec identifies a file-specification dictionary; EF, EP and RF trigger the required Type entry.': 'Filespec '
                                                                                                        'identifie '
                                                                                                        'une '
                                                                                                        'spécification '
                                                                                                        'de '
                                                                                                        'fichier '
                                                                                                        '; EF, EP '
                                                                                                        'et RF '
                                                                                                        'rendent '
                                                                                                        'l’entrée '
                                                                                                        'Type '
                                                                                                        'obligatoire.',
 'File system used to interpret the specification.': 'Système de fichiers utilisé pour interpréter la '
                                                     'spécification.',
 'Fallback file name, required when platform-specific names are absent.': 'Nom de fichier de repli, requis en '
                                                                          'l’absence de noms propres aux '
                                                                          'plateformes.',
 'Unicode file name preferred over F when present.': 'Nom Unicode préféré à F lorsqu’il est présent.',
 'A historical platform-specific file name, deprecated in PDF 2.0.': 'Nom de fichier historique propre à une '
                                                                     'plateforme, déprécié en PDF 2.0.',
 'Two byte-string identifiers of the referenced file.': 'Deux identifiants du fichier référencé, exprimés comme '
                                                        'chaînes d’octets.',
 'Whether the referenced file is volatile.': 'Indique si le fichier référencé est volatil.',
 'Embedded-file stream bindings; required with related-file bindings.': 'Liaisons de flux de fichiers incorporés, '
                                                                        'requises avec des liaisons de fichiers '
                                                                        'liés.',
 'Related-file arrays matching embedded-file bindings.': 'Tableaux de fichiers liés correspondant aux liaisons '
                                                         'des fichiers incorporés.',
 'Description of the file specification.': 'Description de la spécification de fichier.',
 'An indirect reference to portable-collection item metadata.': 'Référence indirecte vers les métadonnées d’un '
                                                                'élément de collection portable.',
 'An indirectly referenced file thumbnail image.': 'Image de miniature du fichier référencée indirectement.',
 'Encrypted-payload identification; required for encrypted-wrapper payloads.': 'Identification de la charge '
                                                                               'chiffrée, requise pour les '
                                                                               'charges des enveloppes chiffrées.',
 'Relationship between the referring PDF object or marked content and its associated file.': 'Relation entre '
                                                                                             'l’objet PDF ou le '
                                                                                             'contenu marqué '
                                                                                             'référent et son '
                                                                                             'fichier associé.',
 'Identifies a namespace dictionary when present.': 'Identifie un dictionnaire d’espace de noms lorsque cette '
                                                    'entrée est présente.',
 'Namespace identity, conventionally a URI.': 'Identité de l’espace de noms, généralement une URI.',
 'File specification of the namespace schema.': 'Spécification de fichier du schéma de l’espace de noms.',
 'Namespace-specific role mappings; cross-namespace graph semantics remain separate.': 'Correspondances de rôles '
                                                                                       'propres à l’espace de '
                                                                                       'noms ; la sémantique du '
                                                                                       'graphe entre espaces '
                                                                                       'reste séparée.',
 'One or more associated file specifications, each carrying AFRelationship; use a named property resource.': 'Une '
                                                                                                             'ou '
                                                                                                             'plusieurs '
                                                                                                             'spécifications '
                                                                                                             'de '
                                                                                                             'fichiers '
                                                                                                             'associés, '
                                                                                                             'chacune '
                                                                                                             'avec '
                                                                                                             'AFRelationship '
                                                                                                             '; '
                                                                                                             'utiliser '
                                                                                                             'une '
                                                                                                             'ressource '
                                                                                                             'de '
                                                                                                             'propriétés '
                                                                                                             'nommée.'}


def iso2_description(value, language):
    if language == 'fr' and value in ISO2_DESCRIPTIONS_FR:
        return ISO2_DESCRIPTIONS_FR[value], 'fr'
    # Original normative excerpts remain English. Complete site builds require
    # French translations for every project-authored summary.
    return value, 'en'


def route_for(route, language):
    # Generated example documents are shared artifacts, including HTML outputs.
    if route.startswith('examples/') or not route.endswith('.html'):
        return route
    if language == 'fr':
        return 'fr/' + route
    return ENGLISH_ROUTES.get(route, route)


def localized_source(owner, source, language):
    if owner == 'documentation':
        return source.replace('docs/', 'docs/en/', 1) if language == 'en' else source
    if language == 'fr':
        if source in {'README.md', 'SECURITY.md', 'CHANGELOG.md'}:
            return source.replace('.md', '.fr.md')
        return source.replace('docs/', 'docs/fr/', 1)
    return source


def canonical_source(owner, source):
    if owner == 'documentation':
        return source.replace('docs/en/', 'docs/', 1).replace('.fr.md', '.md')
    return source.replace('docs/fr/', 'docs/', 1).replace('.fr.md', '.md')


TEXT = {
    'Dériver du HTML depuis un PDF': 'Derive HTML from PDF',
    'Dériver du HTML depuis un PDF balisé': 'Derive HTML from tagged PDF',
    'Structure logique, contenu Unicode et HTML sémantique avec diagnostics explicites.': 'Logical structure, Unicode content and semantic HTML with explicit diagnostics.',
    'Architecture de la dérivation HTML': 'HTML derivation architecture',
    'Couverture de la dérivation HTML': 'HTML derivation coverage',
    'Sécurité du HTML dérivé': 'Derived HTML security',
    'Référence Deriving HTML from PDF': 'Deriving HTML from PDF reference',
    'Module optionnel : dérivation HTML': 'Optional module: HTML derivation',
    'Résultat HTML': 'HTML result',
    'Télécharger le HTML': 'Download the HTML',
    'Lire la source HTML': 'Read the HTML source',
    'Ce PDF balisé est l’entrée de la conversion. Le résultat HTML est produit par le script exécuté pendant la construction du site ; l’aperçu conserve la structure sémantique plutôt que la mise en page du PDF.': 'This tagged PDF is the conversion input. The HTML result is produced by the script run during the site build; its preview preserves semantic structure rather than the PDF layout.',
    'Sortie réelle de la dérivation, isolée dans une frame sans autorisation de script, de formulaire ou de navigation de la page principale.': 'Actual derivation output, isolated in a frame without permission to run scripts, submit forms or navigate the parent page.',
    'Bundle PDF 2.0 : mécanismes et vérifications': 'PDF 2.0 bundle: mechanisms and validation',
    'Métadonnées, déclarations et parties documentaires': 'Metadata, declarations and document parts',
    'XMP, portée des déclarations, compensation du point noir et DPart.': 'XMP, declaration scope, black point compensation and DPart.',
    'Une enveloppe pour un PDF chiffré': 'A wrapper for an encrypted PDF',
    'Collection masquée, fichier associé EncryptedPayload et protection du contenu.': 'Hidden collection, EncryptedPayload associated file and content protection.',
    'Espaces de noms et PDF bien balisé': 'Namespaces and well-tagged PDF',
    'Rôles qualifiés, règles d’inclusion et rapport de vérification WTPDF.': 'Qualified roles, inclusion rules and WTPDF audit report.',
    'Algorithmes modernes et intégrité PDF': 'Modern algorithms and PDF integrity',
    'Signature SHA-3, AES-GCM et MAC vérifiés indépendamment.': 'Independently verified SHA-3 signatures, AES-GCM and PDF MAC.',
    'Couverture des éditions PDF': 'Coverage by PDF edition',
    'PDF 2.0 : objets et mécanismes': 'PDF 2.0: objects and mechanisms',
    'Horodatages et preuves de validation': 'Timestamps and validation evidence',
    'RFC3161, révisions signées, DSS et VRI explicites.': 'RFC3161, signed revisions, explicit DSS and VRI.',
    'Objets géospatiaux et mesures': 'Geospatial objects and measurements',
    'Systèmes de coordonnées, points appariés, viewports et nuages de points.': 'Coordinate systems, paired points, viewports and point clouds.',
    'Destinations vers la structure logique': 'Destinations targeting logical structure',
    'Cibles sémantiques, parcours du contenu et destinations de page de repli.': 'Semantic targets, content traversal and fallback page destinations.',
    'PHP 8.3+ 64 bits · PDF 1.7 et 2.0': '64-bit PHP 8.3+ · PDF 1.7 and 2.0',
    'PDF 2.0 et fichiers associés': 'PDF 2.0 and associated files',
    'Métadonnées UTF-8, fichiers AF et propriétés MCAF nommées.': 'UTF-8 metadata, AF files and named MCAF properties.',
    'PDF 2.0 : ISO 32000-2': 'PDF 2.0: ISO 32000-2',
    'Original conservé dans le dépôt du core. Inventaire des tableaux et contrôles sémantiques restent distincts.': 'Original retained in the core repository. Table inventory and semantic validation remain distinct.',
    'Extrait normatif original en anglais.': 'Original normative excerpt in English.',
    'Définitions communes :': 'Common definitions:',
    'Clé fournie explicitement': 'Explicitly supplied key',
    'Éléments indirects dans le tableau': 'Indirect array elements required',
    'Premiers mécanismes PDF 2.0': 'First PDF 2.0 mechanisms',
    'PHP 8.3+ · PDF 1.7 · Premiers mécanismes PDF 2.0': 'PHP 8.3+ · PDF 1.7 · First PDF 2.0 mechanisms',
    'Requis': 'Required', 'Facultatif': 'Optional',
    'Définition ISO 32000-2:2020 EC3': 'ISO 32000-2:2020 EC3 definition',
    'Métadonnées de la source au commit documenté ↗': 'Source metadata at the documented commit ↗',
    'Errata publics ↗': 'Public errata ↗',
    'Original conservé dans le dépôt du core. Catalogue pilote — couverture complète en attente.': 'Original retained in the core repository. Pilot catalogue — complete coverage pending.',
    'Original PDF au commit documenté ↗': 'Original PDF at the documented commit ↗',
    'Page PDF physique': 'Physical PDF page',
    'Correction EC3': 'EC3 correction',
    'Résumé d’implémentation rédigé pour le projet.': 'Project-authored implementation summary.',
    'Périmètre et limites PDF 2.0.': 'PDF 2.0 scope and limits.',
    'Guides': 'Guides', 'Tutoriels': 'Tutorials', 'Recettes': 'Recipes',
    'Couverture des deux références': 'Coverage of both references',
    'Supplément Adobe et extensions': 'Adobe supplement and extensions',
    'Références Adobe conservées': 'Preserved Adobe references',
    'Démarrer': 'Getting started', 'Comprendre les composants': 'Understanding the components',
    'Core et modules optionnels': 'Core and optional modules',
    'Migration vers le core 0.5': 'Migrating to core 0.5',
    'Migration vers le core 0.4': 'Migrating to core 0.4',
    'Couverture de la norme': 'Specification coverage', 'Sécurité': 'Security',
    'Signaler une vulnérabilité': 'Reporting a vulnerability',
    'Versions et changements': 'Releases and changes', 'Parcours des tutoriels': 'Tutorial learning path',
    'Recettes pratiques': 'Practical recipes', 'Un tableau explicite': 'An explicit table',
    'Premier document': 'First document', 'Pages et texte': 'Pages and text',
    'Dessin et transformations': 'Drawing and transformations', 'Signets et destinations': 'Bookmarks and destinations',
    'Liens cliquables': 'Clickable links', 'Dégradé et fonction': 'Gradient and function',
    'Objets compressés': 'Compressed objects', 'Police TrueType et Unicode': 'TrueType font and Unicode',
    'Images JPEG et PNG': 'JPEG and PNG images', 'Révisions incrémentales': 'Incremental revisions',
    'Lire les pages d’un PDF externe': 'Reading pages from an external PDF',
    'Extensions Adobe et numérotation Bates': 'Adobe extensions and Bates numbering',
    'Champs et apparences AcroForm': 'AcroForm fields and appearances',
    'Structure logique et contenu balisé': 'Logical structure and tagged content',
    'Linéarisation': 'Linearization', 'Couleurs, motifs et dégradés': 'Colours, patterns and gradients',
    'CMaps et Unicode': 'CMaps and Unicode', 'Filtres et prédicteurs': 'Filters and predictors',
    'Signatures PDF': 'PDF signatures', 'Images, transparence et calques': 'Images, transparency and layers',
    'Fontes natives et écriture verticale': 'Native fonts and vertical writing',
    'Navigation, articles et présentation': 'Navigation, articles and presentation',
    'Fichiers incorporés et collections': 'Embedded files and collections',
    'Suppression et générations': 'Deletion and generations', 'Politique du champ signé': 'Signature field policy',
    'Police, contenu, page et catalogue.': 'Font, content, page and catalog.',
    'Ressources partagées, héritage et lignes explicites.': 'Shared resources, inheritance and explicit lines.',
    'Chemins, couleurs, courbes et matrices.': 'Paths, colours, curves and matrices.',
    'Un plan hiérarchique et des destinations nommées.': 'A hierarchical outline and named destinations.',
    'Annotations internes et actions URI.': 'Internal annotations and URI actions.',
    'Un motif RGB en XObject et en image inline.': 'An RGB pattern as an XObject and an inline image.',
    'Une fonction de type 2 alimente un shading axial.': 'A type 2 function drives axial shading.',
    'Filtres, flux d’objets et références croisées.': 'Filters, object streams and cross-references.',
    'Programme incorporé, CID, métriques et correspondance Unicode.': 'Embedded program, CID, metrics and Unicode mapping.',
    'Fichiers image, couleurs, échantillons et transparence.': 'Image files, colours, samples and transparency.',
    'Octets conservés, remplacements explicites et chaînage des xref.': 'Preserved bytes, explicit replacements and chained cross-references.',
    'Arbre vérifié, attributs hérités et flux décodés explicitement.': 'Validated tree, inherited attributes and explicitly decoded streams.',
    'Déclaration des extensions, artefacts et numéros documentaires.': 'Extension declarations, artifacts and document numbering.',
    'Arbres de champs, widgets, valeurs et apparences.': 'Field trees, widgets, values and appearances.',
    'Ordre de lecture, MCID, ParentTree et liens vers les annotations.': 'Reading order, MCID, ParentTree and annotation links.',
    'Ordre physique des objets, dépendances et indices binaires.': 'Physical object order, dependencies and binary hints.',
    'Espaces couleur, cellules répétées et sept types de shading.': 'Colour spaces, repeated cells and seven shading types.',
    'Encodage composé, CID, UseCMap et extraction Unicode.': 'Composite encoding, CID, UseCMap and Unicode extraction.',
    'LZW et prédiction TIFF/PNG des lignes avant compression.': 'LZW and TIFF/PNG row prediction before compression.',
    'Réservation Contents, ByteRange et signature CMS explicite.': 'Reserved Contents, ByteRange and an explicit CMS signature.',
    'Profondeurs, masques, groupes, ExtGState et contenu optionnel.': 'Bit depths, masks, groups, ExtGState and optional content.',
    'Type3, fontes simples, programmes PDF et métriques verticales.': 'Type3, simple fonts, PDF programs and vertical metrics.',
    'Labels, cadrages, anneaux de lecture et séquences.': 'Labels, viewports, article rings and sequences.',
    'Octets, métadonnées, EF/RF/CI et présentation de collection.': 'Bytes, metadata, EF/RF/CI and collection presentation.',
    'Liste libre, réutilisation et identités historiques.': 'Free list, reuse and historical identities.',
    'Seeds, verrou, apparence et preuve du résultat effectivement signé.': 'Seed values, lock, appearance and evidence of the actual signed result.',
    'Objets et références': 'Objects and references', 'Écriture et fichier': 'Writing and file structure',
    'Contenu, texte et graphisme': 'Content, text and graphics', 'Structure documentaire': 'Document structure',
    'Fonctions PDF': 'PDF functions', 'Filtres': 'Filters', 'Conventions lexicales': 'Lexical conventions',
    'Modèle de norme': 'Specification model', 'Dictionnaires normalisés': 'Standard dictionaries',
    'Entrées normalisées': 'Standard entries', 'Définitions normalisées': 'Standard definitions',
    'Extensions Adobe : dictionnaires, entrées et définitions': 'Adobe extensions: dictionaries, entries and definitions',
    'Chiffrement, certificats et signatures': 'Encryption, certificates and signatures',
    'Module optionnel : fontes externes': 'Optional module: external fonts',
    'Module optionnel : images externes': 'Optional module: external images',
    'Module optionnel : lecture de PDF': 'Optional module: PDF reading',
    'Modèle objet OpenType indépendant': 'Independent OpenType object model',
    'Architecture OpenType': 'OpenType architecture',
    'Couverture OpenType': 'OpenType coverage',
    'Substitutions de glyphes': 'Glyph substitutions',
    'Lire un PDF': 'Reading a PDF', 'Architecture du lecteur': 'Reader architecture',
    'Pages, héritage et flux': 'Pages, inheritance and streams', 'Composants du lecteur': 'Reader components',
    'Limites et sécurité du lecteur': 'Reader limits and security', 'Convertir des images': 'Converting images',
    'Contrats des convertisseurs d’images': 'Image converter contracts', 'Analyser des fontes': 'Inspecting fonts',
    'Du programme TrueType aux objets PDF': 'From a TrueType program to PDF objects',
    'Découvrir': 'Discover', 'Accueil': 'Home', 'Core et modules': 'Core and modules',
    'Les composants': 'Components', 'Core : objets et écriture': 'Core: objects and writing',
    'Apprendre': 'Learn', 'Tous les tutoriels': 'All tutorials', 'Recette : tableau': 'Recipe: table',
    'Explorer': 'Explore', 'Référence des composants': 'Component reference', 'Supplément Adobe': 'Adobe supplement',
    'Versions': 'Releases', 'Sur cette page': 'On this page', 'Aller au contenu': 'Skip to content',
    'objet par objet': 'object by object', 'Navigation principale': 'Main navigation', 'Référence': 'Reference',
    'Le catalogue relie l’arbre des pages, les contenus et les ressources': 'The catalog connects the page tree, content and resources',
    'PDF d’entrée': 'Input PDF', 'Résultat PDF': 'PDF result', 'Voir le PDF d’entrée': 'View the input PDF',
    'Voir le résultat PDF': 'View the PDF result',
    'Ce PDF est l’entrée du lecteur : une fixture originale créée avec pypdf et qpdf, indépendamment du writer PHP. Ses trois pages sont reproduites ci-dessous ; le résultat de la lecture figure ensuite dans la sortie console.': 'This PDF is the reader input: an original fixture created with pypdf and qpdf, independently of the PHP writer. All three pages appear below, followed by the reader output.',
    'Ce fichier a été généré avec le code de cette documentation. Toutes ses pages sont reproduites ci-dessous ; ouvrir le PDF pour utiliser ses liens et ses signets.': 'This file was generated with the code in this documentation. All pages appear below; open the PDF to use its links and bookmarks.',
    'Code de': 'Code from', 'Consulter la source au commit documenté ↗': 'View the source at the documented commit ↗',
    'Origine du PDF d’entrée ↗': 'Input PDF source ↗', 'Résultat de la lecture': 'Reader output',
    'Sortie réelle du script exécuté sur le PDF d’entrée pendant la construction de cette documentation.': 'Actual script output from reading the input PDF while building this documentation.',
    'Télécharger la sortie console': 'Download the console output', 'Ouvrir le PDF ↗': 'Open the PDF ↗',
    'Télécharger': 'Download', 'Télécharger le code PHP': 'Download the PHP code',
    'Utiliser le lecteur PDF du navigateur': 'Use the browser PDF viewer',
    'Ce lecteur dépend du navigateur. Si le document ne s’affiche pas, utiliser « Ouvrir le PDF » ou « Télécharger ».': 'This viewer depends on your browser. If the document does not appear, use “Open the PDF” or “Download”.',
    'Code source complet': 'Complete source code', 'Code source': 'Source code', 'Lire et voir le PDF →': 'Read and view the PDF →',
    'Rechercher un composant': 'Search for a component', 'Type de composant': 'Component type', 'Tous les types': 'All types',
    'Installer avec Composer · Packagist ↗': 'Install with Composer · Packagist ↗',
    'Guide du package →': 'Package guide →', 'Référence API →': 'API reference →',
    'Présentation': 'Overview', 'Référence API': 'API reference', 'Signalements privés': 'Private reports',
    'Guides du module': 'Module guides', 'Installer le core': 'Install the core',
    'Le core représente les objets et mécanismes de PDF 1.7 et PDF 2.0 et les compose en fichiers PDF. Il fournit la syntaxe, les dictionnaires, les flux, les pages, les images et les polices PDF, ainsi que l’écriture et les révisions. Les lecteurs de PDF externes, PNG/JPEG et TrueType sont des modules optionnels.': 'The core represents PDF 1.7 and PDF 2.0 objects and mechanisms and assembles them into PDF files. It provides syntax, dictionaries, streams, pages, PDF images and fonts, writing and revisions. External PDF, PNG/JPEG and TrueType readers are optional modules.',
    'Composer installe uniquement le core et vérifie ses extensions PHP requises. Les modules optionnels sont choisis par l’application.': 'Composer installs the core and checks its required PHP extensions. The application chooses which optional modules to install.',
    'Commencer et construire': 'Get started and build', 'Installation et premier document': 'Installation and first document',
    'Tutoriels avec code et PDF': 'Tutorials with code and PDFs', 'Responsabilités des composants': 'Component responsibilities',
    'Référence et versions': 'Reference and releases', 'API du core': 'Core API',
    'Définitions et couverture de la norme': 'Definitions and specification coverage',
    'Mécanismes vérifiés et limites': 'Verified mechanisms and limits', 'Sécurité et responsabilités': 'Security and responsibilities',
    'Core : objets PDF et écriture': 'Core: PDF objects and writing',
    'Le format PDF.': 'The PDF format.', 'Objet par objet.': 'Object by object.',
    'Comprendre les structures, composer les objets, maîtriser les octets. Une documentation pour explorer le format et construire vos propres fichiers PDF.': 'Understand structures, compose objects and control the bytes. Explore the format and build your own PDF files.',
    'Créer mon premier PDF →': 'Create my first PDF →', 'Explorer les composants': 'Explore the components',
    'Du catalogue à la page': 'From catalog to page', '01 / point d’entrée': '01 / entry point',
    '02 / arbre du document': '02 / document tree', '03 / contenu & ressources': '03 / content & resources',
    'composants documentés': 'documented components', 'dictionnaires ISO et Adobe': 'ISO and Adobe dictionaries',
    'exemples PDF à explorer': 'PDF examples to explore', 'tokens d’opérateurs PDF': 'PDF operator tokens',
    'Apprendre avec les objets': 'Learn with objects', 'Construire un document et explorer ses pages': 'Build a document and explore its pages',
    'Chaque tutoriel relie les explications aux objets PHP et au PDF créé ou lu. Consultez ses pages, le script et le résultat de son exécution.': 'Each tutorial connects the explanations to PHP objects and the PDF being created or read. Explore its pages, script and execution result.',
    'Un core PDF, des modules au choix': 'A PDF core, optional modules',
    'Le core représente les objets et les mécanismes de la norme Adobe. Les modules de lecture PDF et de conversion d’images ou de fontes dépendent du core. Le modèle OpenType est indépendant et s’installe sans aucun package PDF.': 'The core represents the objects and mechanisms in the Adobe specification. PDF reading and image or font conversion modules depend on the core. The OpenType model is independent and installs without any PDF package.',
    'Choisir les packages et comprendre leur frontière →': 'Choose packages and understand their scope →',
    'Trois chemins pour explorer le projet': 'Three ways to explore the project', 'Comprendre les responsabilités': 'Understand responsibilities',
    'Valeurs, graphes, ressources, fonctions et écriture : comment les familles se composent.': 'Values, graphs, resources, functions and writing: how the component families fit together.',
    'Consulter la référence': 'Browse the reference',
    'Les signatures et l’héritage de chaque composant, avec les sources et les tableaux de la norme.': 'Signatures and inheritance for every component, with source code and specification tables.',
    'Assembler un exemple pratique': 'Assemble a practical example',
    'Un tableau explicite : cellules, couleurs, grille et positionnement du texte.': 'An explicit table: cells, colours, grid and text positioning.',
    'Les signatures, exemples et guides des modules proviennent de ces versions publiées, fixées à leurs commits exacts. La couverture et les traitements restant à implémenter sont détaillés dans': 'Signatures, examples and module guides come from these published releases, pinned to their exact commits. Coverage and remaining mechanisms are detailed in',
    'la couverture de la norme': 'specification coverage', 'Le format PDF, objet par objet': 'The PDF format, object by object',
    'Définition dans la norme': 'Definition in the specification', 'Référence indirecte exigée': 'Indirect reference required',
    'Objet direct exigé': 'Direct object required', 'Éléments directs dans le tableau': 'Direct array elements required',
    'Qualificateur :': 'Qualifier:', 'Non précisé': 'Unspecified', 'Entrée': 'Entry', 'Type PDF': 'PDF type',
    'Exigence de la source': 'Source requirement', 'Tableau': 'Table',
    'Les descriptions conditionnelles restent traçables. La présence d’une définition ne réalise pas à elle seule un codec, une signature ou tous les traitements du format.': 'Conditional descriptions remain traceable. A definition alone does not implement a codec, a signature or every format mechanism.',
    'Lire la couverture.': 'Read the coverage.', 'Définition dans le supplément Adobe': 'Definition in the Adobe supplement',
    'Définition dans la norme ISO': 'Definition in the ISO specification', 'Exigence': 'Requirement',
    'Chaque entrée conserve sa source ISO ou Adobe. Les règles et traitements associés figurent dans': 'Each entry preserves its ISO or Adobe source. Related rules and mechanisms are described in',
    'la couverture du supplément': 'supplement coverage', 'Déclarée par': 'Declared by', 'Voir le code ↗': 'View the code ↗',
    'Lire la déclaration source ↗': 'Read the source declaration ↗', 'Ce composant appartient à': 'This component belongs to',
    ', un module installé séparément du core.': ', a module installed separately from the core.',
    'Guide du module.': 'Module guide.', 'API du package.': 'Package API.',
    'Héritage et contrats': 'Inheritance and contracts', 'Ce type ne déclare pas de parent, d’interface ou de trait.': 'This type declares no parent, interface or trait.',
    'Méthodes déclarées': 'Declared methods', 'Méthodes héritées': 'Inherited methods', 'Propriétés': 'Properties',
    'Déclaration': 'Declaration', 'Provenance et documentation': 'Origin and documentation',
    'Constantes': 'Constants', 'Nom': 'Name', 'Valeur PHP': 'PHP value', 'Provenance': 'Origin',
    'Cas de l’enum': 'Enum cases', 'Héritage': 'Inheritance', 'Norme': 'Specification', 'Méthodes': 'Methods',
    'Lire le guide du package →': 'Read the package guide →', 'Référence par package': 'Reference by package',
    'Chaque classe, interface, enum et trait du core et des modules installés pour cette documentation possède une fiche. Les composants optionnels portent leur nom de package ; les installer dépend des traitements nécessaires à votre application. Les signatures sont extraites par Reflection ; les descriptions normalisées proviennent du catalogue de la référence PDF.': 'Every class, interface, enum and trait in the core and documented modules has a reference page. Optional components show their package name; install them according to your application’s needs. Signatures are extracted through Reflection; standard descriptions come from the PDF reference catalogue.',
    'Explorer par package': 'Explore by package', 'Explorer par famille': 'Explore by family', 'Consulter la famille →': 'Browse the family →',
    'Les composants de cette famille sont tous accessibles ci-dessous. La recherche globale permet aussi de retrouver une entrée PDF ou un nom de type.': 'All components in this family are available below. Global search also finds PDF entries and type names.',
    'Repères pour commencer': 'Starting points', 'Tous les composants': 'All components',
    'Source de ce guide au commit documenté ↗': 'Guide source at the documented commit ↗',
    'Page introuvable': 'Page not found', 'Cette adresse ne correspond pas à une page publiée.': 'This address does not match a published page.',
    'ou': 'or', 'revenir à l’accueil': 'return home',
}

# Variable interface messages have bounded, explicit sentence templates.
PATTERNS = [
    (r'Correction EC3 /(.+)', lambda m: 'EC3 correction /' + m[1]),
    (r'§(.+) · page PDF (\d+)', lambda m: '§' + m[1] + ' · PDF page ' + m[2]),
    (r'(Requis|Facultatif); conditionnel', lambda m: translate(m[1]) + '; conditional'),
    (r'(\d{2})\. (.+)', lambda m: m[1] + '. ' + translate(m[2])),
    (r'Tutoriel (\d{2})', lambda m: 'Tutorial ' + m[1]),
    (r'Aperçu : (.+)', lambda m: 'Preview: ' + translate(m[1])),
    (r'(\d[\d\u202f,]*) composants', lambda m: m[1] + ' components'),
    (r'(\d[\d\u202f,]*) composants dans le code, dont les définitions et entrées normalisées\.', lambda m: m[1] + ' components in the code, including standard definitions and entries.'),
    (r'Module optionnel(.*)', lambda m: 'Optional module' + m[1]),
    (r'Optionnel · (.+)', lambda m: 'Optional · ' + m[1]),
    (r'Version publiée (.+)', lambda m: 'Published release ' + m[1]),
    (r'API de (.+)', lambda m: 'API for ' + m[1]),
    (r'Nom fixe /(.+)', lambda m: 'Fixed name /' + m[1]),
    (r'Noms permis : (.+)', lambda m: 'Allowed names: ' + m[1]),
    (r'Longueur exacte du tableau : (\d+)', lambda m: 'Exact array length: ' + m[1]),
    (r'Tableau (.+)', lambda m: 'Table ' + m[1]),
    (r'page PDF (\d+) ↗', lambda m: 'PDF page ' + m[1] + ' ↗'),
    (r'Correction d’implémentation /(.+)', lambda m: 'Implementation correction /' + m[1]),
    (r'(\d+) types dérivés directement', lambda m: m[1] + ' directly derived types'),
    (r'(\d+) méthodes des parents et contrats', lambda m: m[1] + ' methods from parents and contracts'),
    (r'Agrandir la page (\d+) sur (\d+)', lambda m: 'Enlarge page ' + m[1] + ' of ' + m[2]),
    (r'Page (\d+) sur (\d+)', lambda m: 'Page ' + m[1] + ' of ' + m[2]),
    (r'(PDF d’entrée|Résultat PDF) (.+) : page (\d+) sur (\d+)', lambda m: translate(m[1]) + ' ' + m[2] + ': page ' + m[3] + ' of ' + m[4]),
    (r'(PDF d’entrée|Résultat PDF) : (.+)', lambda m: translate(m[1]) + ': ' + m[2]),
    (r'Aperçu des (\d+) pages du PDF (.+)', lambda m: 'Preview of all ' + m[1] + ' pages in PDF ' + m[2]),
    (r'Lire le script commenté : (.+)', lambda m: 'Read the commented script: ' + m[1]),
    (r'(.+) — modèle objet PDF pour PHP 8\.3\+\.', lambda m: translate(m[1]) + ' — PDF object model for PHP 8.3+.'),
    (r'(.+) · PDFToolkit', lambda m: translate(m[1]) + ' · PDFToolkit'),
]


def translate(value):
    stripped = value.strip()
    result = TEXT.get(stripped)
    if result is None:
        for pattern, replacement in PATTERNS:
            match = re.fullmatch(pattern, stripped)
            if match:
                result = replacement(match)
                break
    return value if result is None else value[:len(value) - len(value.lstrip())] + result + value[len(value.rstrip()):]


class InterfaceTranslator(HTMLParser):
    """Translate explicit presentation strings without changing markup or code."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.protected = []

    def handle_starttag(self, tag, attrs):
        if tag in {'code', 'pre', 'script', 'style'}:
            self.protected.append(tag)
        rendered = []
        for key, value in attrs:
            if value is None:
                rendered.append(key)
            else:
                if key in {'alt', 'title', 'aria-label'} or tag == 'meta' and key == 'content' and dict(attrs).get('name') == 'description':
                    value = translate(value)
                rendered.append(f'{key}="{escape(value, quote=True)}"')
        self.parts.append('<' + tag + (' ' + ' '.join(rendered) if rendered else '') + '>')

    def handle_endtag(self, tag):
        if self.protected and self.protected[-1] == tag:
            self.protected.pop()
        self.parts.append('</' + tag + '>')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.parts[-1] = self.parts[-1][:-1] + '/>'

    def handle_data(self, value):
        if self.protected and self.protected[-1] in {'script', 'style'}:
            self.parts.append(value)
        else:
            self.parts.append(escape(value if self.protected else translate(value), quote=True))

    def handle_entityref(self, name):
        self.parts.append('&' + name + ';')

    def handle_charref(self, name):
        self.parts.append('&#' + name + ';')

    def handle_decl(self, value):
        self.parts.append('<!' + value + '>')

    def handle_comment(self, value):
        self.parts.append('<!--' + value + '-->')


def translate_interface(html):
    parser = InterfaceTranslator()
    parser.feed(html)
    return ''.join(parser.parts)
