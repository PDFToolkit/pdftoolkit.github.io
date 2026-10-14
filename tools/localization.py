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
    'adobe': 'adobe', 'securite': 'security', 'polices-externes': 'external-fonts',
    'images-externes': 'external-images', 'lecture': 'reader',
}
ENGLISH_ROUTES.update({f'reference/groups/{old}.html': f'reference/groups/{new}.html' for old, new in GROUP_ROUTES.items()})
for module in ('reader', 'images', 'fonts'):
    ENGLISH_ROUTES[f'modules/{module}/signalements.html'] = f'modules/{module}/reporting.html'
    ENGLISH_ROUTES[f'modules/{module}/versions.html'] = f'modules/{module}/changelog.html'


def route_for(route, language):
    if not route.endswith('.html'):
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
    'Le core représente les objets et mécanismes de PDF 1.7 et les compose en fichiers PDF. Il fournit la syntaxe, les dictionnaires, les flux, les pages, les images et les polices PDF, ainsi que l’écriture et les révisions. Les lecteurs de PDF externes, PNG/JPEG et TrueType sont des modules optionnels.': 'The core represents PDF 1.7 objects and mechanisms and assembles them into PDF files. It provides syntax, dictionaries, streams, pages, PDF images and fonts, writing and revisions. External PDF, PNG/JPEG and TrueType readers are optional modules.',
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
    'Le core représente les objets et les mécanismes de la norme Adobe. La lecture de PDF externes et la conversion de fichiers image ou de fontes sont des dépendances optionnelles : chaque module dépend du core.': 'The core represents the objects and mechanisms in the Adobe specification. Reading external PDFs and converting image or font files are optional dependencies: each module depends on the core.',
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
