"""Build the GitHub Pages documentation from repository guides and PHP metadata."""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
from html import escape
import json
from pathlib import Path
import posixpath
import re
import shutil
import subprocess
from urllib.parse import quote, unquote, urlsplit

import markdown
from check_sources import select_reader
from localization import LANGUAGES, ENGLISH_ROUTES, canonical_source, localized_source, route_for, translate, translate_interface, ISO2_DESCRIPTIONS_FR, iso2_description


REPOSITORY = 'https://github.com/PDFToolkit/pdf'
DOCUMENTATION_REPOSITORY = 'https://github.com/PDFToolkit/pdftoolkit.github.io'
SITE_ORIGIN = 'https://pdftoolkit.github.io'
CORE_PACKAGE = 'roukmoute/pdf'


def publish_derivation_assets(report_path: Path, html_path: Path, target: Path) -> list[dict]:
    """Publish only the exact basename/hash inventory returned by the real CLI."""
    report = json.loads(report_path.read_text(encoding='utf-8'))
    if report.get('htmlSha256') != hashlib.sha256(html_path.read_bytes()).hexdigest():
        raise ValueError('Derived HTML does not match its CLI report')
    assets = report.get('assets')
    if not isinstance(assets, list):
        raise ValueError('Missing derived asset inventory')
    records, seen = [], set()
    for asset in assets:
        name = asset.get('filename', '')
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', name) or '..' in name or name in seen:
            raise ValueError('Invalid or duplicate derived asset filename: ' + name)
        seen.add(name)
        source = html_path.parent / name
        if source.resolve().parent != html_path.parent.resolve() or not source.is_file():
            raise ValueError('Missing or external derived asset: ' + name)
        data = source.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != asset.get('sha256') or not isinstance(asset.get('mediaType'), str):
            raise ValueError('Derived asset does not match its CLI report: ' + name)
        destination = target / name
        if destination.exists() and destination.read_bytes() != data:
            raise ValueError('Derived asset collides with another example: ' + name)
        shutil.copyfile(source, destination)
        records.append({'filename': name, 'path': 'examples/' + name,
                        'mediaType': asset['mediaType'], 'sha256': digest, 'bytes': len(data)})
    return records


GUIDES = [
    ('docs/coverage.md', 'guides/mecanismes.html', 'Couverture des éditions PDF', 'Guides'),
    ('docs/source-audits.md', 'guides/source-audits.html', 'Règles de source et corrections vérifiées', 'Guides'),
    ('docs/pdf-2-0.md', 'guides/pdf-2-0.html', 'PDF 2.0 : objets et mécanismes', 'Guides'),
    ('docs/pdf-2-0-bundle.md', 'guides/pdf-2-0-bundle.html', 'Bundle PDF 2.0 : mécanismes et vérifications', 'Guides'),
    ('docs/adobe-supplement.md', 'guides/supplement-adobe.html', 'Supplément Adobe et extensions', 'Guides'),
    ('docs/adobe-references.md', 'guides/references-adobe.html', 'Références Adobe conservées', 'Guides'),
    ('docs/getting-started.md', 'guides/demarrer.html', 'Démarrer', 'Guides'),
    ('docs/components.md', 'guides/composants.html', 'Comprendre les composants', 'Guides'),
    ('docs/architecture.md', 'guides/architecture.html', 'Architecture', 'Guides'),
    ('docs/packages.md', 'guides/modules.html', 'Core et modules optionnels', 'Guides'),
    ('docs/migration-0.11.md', 'guides/migration-0-11.html', 'Migration vers le core 0.11', 'Guides'),
    ('docs/migration-0.5.md', 'guides/migration-0-5.html', 'Migration vers le core 0.5', 'Guides'),
    ('docs/migration-0.4.md', 'guides/migration-0-4.html', 'Migration vers le core 0.4', 'Guides'),
    ('docs/specification.md', 'guides/couverture.html', 'Couverture de la norme', 'Guides'),
    ('docs/security.md', 'guides/securite.html', 'Sécurité', 'Guides'),
    ('docs/protected-revisions.md', 'guides/revisions-protegees.html', 'Révisions natives protégées', 'Guides'),
    ('SECURITY.md', 'guides/signalements.html', 'Signaler une vulnérabilité', 'Guides'),
    ('CHANGELOG.md', 'guides/versions.html', 'Versions et changements', 'Guides'),
    ('docs/tutorials/README.md', 'tutorials/index.html', 'Parcours des tutoriels', 'Tutoriels'),
    ('docs/recipes/README.md', 'recipes/index.html', 'Recettes pratiques', 'Recettes'),
    ('docs/recipes/table.md', 'recipes/table.html', 'Un tableau explicite', 'Recettes'),
]
LESSONS = [
    ('01-first-document', '01-premier-document', 'Premier document', 'hello-world', 'Police, contenu, page et catalogue.'),
    ('02-pages-and-text', '02-pages-et-texte', 'Pages et texte', 'pages-and-text', 'Ressources partagées, héritage et lignes explicites.'),
    ('03-graphics', '03-dessin', 'Dessin et transformations', 'graphics', 'Chemins, couleurs, courbes et matrices.'),
    ('04-navigation', '04-navigation', 'Signets et destinations', 'navigation', 'Un plan hiérarchique et des destinations nommées.'),
    ('05-links', '05-liens', 'Liens cliquables', 'links', 'Annotations internes et actions URI.'),
    ('06-images', '06-images', 'Images', 'images', 'Un motif RGB en XObject et en image inline.'),
    ('07-gradient', '07-degrade', 'Dégradé et fonction', 'gradient', 'Une fonction de type 2 alimente un shading axial.'),
    ('08-object-stream', '08-objets-compresses', 'Objets compressés', 'object-stream', 'Filtres, flux d’objets et références croisées.'),
    ('09-embedded-font', '09-police-incorporee', 'Police TrueType et Unicode', 'embedded-font', 'Programme incorporé, CID, métriques et correspondance Unicode.'),
    ('10-image-files', '10-images-jpeg-png', 'Images JPEG et PNG', 'image-files', 'Fichiers image, couleurs, échantillons et transparence.'),
    ('11-incremental-update', '11-revisions-incrementales', 'Révisions incrémentales', 'incremental-update', 'Octets conservés, remplacements explicites et chaînage des xref.'),
    ('12-reading-pages', '12-lire-pages-pdf', 'Lire les pages d’un PDF externe', 'reading-pages', 'Arbre vérifié, attributs hérités et flux décodés explicitement.'),
    ('13-adobe-extensions', '13-extensions-adobe', 'Extensions Adobe et numérotation Bates', 'adobe-extensions', 'Déclaration des extensions, artefacts et numéros documentaires.'),
    ('14-acroform-fields', '14-champs-acroform', 'Champs et apparences AcroForm', 'acroform-fields', 'Arbres de champs, widgets, valeurs et apparences.'),
    ('15-tagged-structure', '15-structure-logique', 'Structure logique et contenu balisé', 'tagged-structure', 'Ordre de lecture, MCID, ParentTree et liens vers les annotations.'),
    ('16-linearization', '16-linearisation', 'Linéarisation', 'linearized', 'Ordre physique des objets, dépendances et indices binaires.'),
    ('17-colours-patterns', '17-couleurs-motifs', 'Couleurs, motifs et dégradés', 'colours-patterns', 'Espaces couleur, cellules répétées et sept types de shading.'),
    ('18-cmaps', '18-cmaps', 'CMaps et Unicode', 'cmap-font', 'Encodage composé, CID, UseCMap et extraction Unicode.'),
    ('19-filters-predictors', '19-filtres-predicteurs', 'Filtres et prédicteurs', 'filters-predictors', 'LZW et prédiction TIFF/PNG des lignes avant compression.'),
    ('20-signed-document', '20-signatures', 'Signatures PDF', 'signed-document', 'Réservation Contents, ByteRange et signature CMS explicite.'),
    ('21-native-graphics', '21-images-transparence-calques', 'Images, transparence et calques', 'native-graphics', 'Profondeurs, masques, groupes, ExtGState et contenu optionnel.'),
    ('22-native-fonts', '22-fontes-natives', 'Fontes natives et écriture verticale', 'native-fonts', 'Type3, fontes simples, programmes PDF et métriques verticales.'),
    ('23-native-navigation', '23-navigation-native', 'Navigation, articles et présentation', 'native-navigation', 'Labels, cadrages, anneaux de lecture et séquences.'),
    ('24-embedded-files', '24-fichiers-incorpores', 'Fichiers incorporés et collections', 'embedded-files', 'Octets, métadonnées, EF/RF/CI et présentation de collection.'),
    ('25-object-lifecycle', '25-generations-objets', 'Suppression et générations', 'object-lifecycle', 'Liste libre, réutilisation et identités historiques.'),
    ('26-signature-field-policy', '26-politique-signature', 'Politique du champ signé', 'signature-field-policy', 'Seeds, verrou, apparence et preuve du résultat effectivement signé.'),
    ('27-pdf20-associated-files', '27-pdf20-fichiers-associes', 'PDF 2.0 et fichiers associés', 'pdf20-associated-files', 'Métadonnées UTF-8, fichiers AF et propriétés MCAF nommées.'),
    ('28-pdf20-metadata-declarations', '28-pdf20-metadonnees-declarations', 'Métadonnées, déclarations et parties documentaires', 'pdf20-metadata-declarations', 'XMP, portée des déclarations, compensation du point noir et DPart.'),
    ('29-pdf20-encrypted-payload', '29-pdf20-enveloppe-chiffree', 'Une enveloppe pour un PDF chiffré', 'pdf20-encrypted-payload', 'Collection masquée, fichier associé EncryptedPayload et protection du contenu.'),
    ('30-pdf20-tagged-namespaces', '30-pdf20-structure-espaces-noms', 'Espaces de noms et PDF bien balisé', 'pdf20-tagged-namespaces', 'Rôles qualifiés, règles d’inclusion et rapport de vérification WTPDF.'),
    ('31-pdf20-modern-signature', '31-pdf20-signatures-modernes', 'Algorithmes modernes et intégrité PDF', 'pdf20-modern-signature', 'Signature SHA-3, AES-GCM et MAC vérifiés indépendamment.'),
    ('32-pdf20-timestamp-dss', '32-pdf20-horodatages-dss', 'Horodatages et preuves de validation', 'pdf20-timestamp-dss', 'RFC3161, révisions signées, DSS et VRI explicites.'),
    ('33-pdf20-geospatial', '33-pdf20-geospatial', 'Objets géospatiaux et mesures', 'pdf20-geospatial', 'Systèmes de coordonnées, points appariés, viewports et nuages de points.'),
    ('34-pdf20-structure-destinations', '34-pdf20-destinations-structure', 'Destinations vers la structure logique', 'pdf20-structure-destinations', 'Cibles sémantiques, parcours du contenu et destinations de page de repli.'),
    ('35-derive-html', '35-deriver-html', 'Dériver du HTML depuis un PDF balisé', 'derive-html', 'Structure logique, contenu Unicode et HTML sémantique avec diagnostics explicites.'),
    ('36-applied-redaction', '36-caviardisation', 'Appliquer une caviardisation', 'pdf17-secure-redaction', 'Suppression conservatrice des données et écriture d’un nouveau fichier.'),
    ('37-protected-form-fill', '37-remplissage-protege', 'Remplir un formulaire certifié', 'protected-form-fill', 'DocMDP, FieldMDP et remplacement isolé de l’apparence à texte variable.'),
]
EXTERNAL_EXAMPLES = {
    'reading-pages': {
        'package': 'pdftoolkit/pdf-reader',
        'source': 'examples/pages.php',
        'input': 'tests/Fixtures/page-tree/classic.pdf',
        'expectedPages': 3,
    },
    'derive-html': {
        'package': 'pdftoolkit/pdf-to-html',
        'source': 'examples/01-derive-tagged-pdf.php',
        'input': 'tests/Fixtures/tagged.pdf',
        'kind': 'conversion',
    },
}
GROUPS = [
    ('objets', 'Objets et références'), ('fichier', 'Écriture et fichier'),
    ('contenu', 'Contenu, texte et graphisme'), ('document', 'Structure documentaire'),
    ('fonctions', 'Fonctions PDF'), ('filtres', 'Filtres'), ('lexique', 'Conventions lexicales'),
    ('norme', 'Modèle de norme'), ('dictionnaires', 'Dictionnaires normalisés'),
    ('entrees', 'Entrées normalisées'), ('definitions', 'Définitions normalisées'),
    ('adobe', 'Extensions Adobe : dictionnaires, entrées et définitions'),
    ('iso2', 'PDF 2.0 : ISO 32000-2'),
    ('securite', 'Chiffrement, certificats et signatures'),
    ('polices-externes', 'Module optionnel : fontes externes'),
    ('images-externes', 'Module optionnel : images externes'),
    ('lecture', 'Module optionnel : lecture de PDF'),
    ('fontes-opentype', 'Modèle objet OpenType indépendant'),
    ('conversion-html', 'Module optionnel : dérivation HTML'),
]
MODULE_GROUPS = {
    'pdftoolkit/pdf-fonts': 'polices-externes',
    'pdftoolkit/pdf-images': 'images-externes',
    'pdftoolkit/pdf-reader': 'lecture',
    'pdftoolkit/opentype': 'fontes-opentype',
    'pdftoolkit/pdf-to-html': 'conversion-html',
}
MODULES = {
    'pdftoolkit/pdf-reader': ('reader', 'Lire un PDF', [('docs/architecture.md', 'architecture', 'Architecture du lecteur'), ('docs/pages.md', 'pages', 'Pages, héritage et flux'), ('docs/revision-history.md', 'revision-history', 'Historique physique des révisions'), ('docs/structural-policy.md', 'structural-policy', 'Politique structurelle PDF 2.0'), ('docs/authentication.md', 'authentication', 'Authentification des PDF chiffrés'), ('docs/public-key-authentication.md', 'public-key-authentication', 'Authentification par clé publique'), ('docs/source-mac.md', 'source-mac', 'Authentifier le MAC du PDF source'), ('docs/components.md', 'components', 'Composants du lecteur'), ('docs/security.md', 'security', 'Limites et sécurité du lecteur')]),
    'pdftoolkit/pdf-images': ('images', 'Convertir des images', [('docs/architecture.md', 'architecture', 'Contrats des convertisseurs d’images')]),
    'pdftoolkit/pdf-fonts': ('fonts', 'Analyser des fontes', [('docs/true-type-to-pdf.md', 'true-type-to-pdf', 'Du programme TrueType aux objets PDF')]),
    'pdftoolkit/opentype': ('opentype', 'Modèle objet OpenType indépendant', [('docs/architecture.md', 'architecture', 'Architecture OpenType'), ('docs/coverage.md', 'coverage', 'Couverture OpenType'), ('docs/substitutions.md', 'substitutions', 'Substitutions de glyphes'), ('docs/positioning.md', 'positioning', 'Positionnement et variations OpenType'), ('docs/font-axes.md', 'font-axes', 'Axes des fontes variables'), ('docs/font-metadata.md', 'font-metadata', 'Noms et métadonnées OS/2'), ('docs/variable-metrics.md', 'variable-metrics', 'Métriques verticales et variables'), ('docs/truetype-outlines.md', 'truetype-outlines', 'Contours TrueType'), ('docs/cff-outlines.md', 'cff-outlines', 'Contours CFF et CFF2'), ('docs/truetype-variations.md', 'truetype-variations', 'Variations des contours TrueType'), ('docs/font-headers-and-styles.md', 'font-headers-and-styles', 'En-têtes et styles des fontes'), ('docs/device-metrics.md', 'device-metrics', 'Métriques pré-calculées')]),
    'pdftoolkit/pdf-to-html': ('to-html', 'Dériver du HTML depuis un PDF', [
        ('docs/architecture.md', 'architecture', 'Architecture de la dérivation HTML'),
        ('docs/coverage.md', 'coverage', 'Couverture de la dérivation HTML'),
        ('docs/authentication.md', 'authentication', 'Authentification des PDF chiffrés'),
        ('docs/requirements.md', 'requirements', 'Exigences de la dérivation HTML'),
        ('docs/policies.md', 'policies', 'Politiques de dérivation HTML'),
        ('docs/graphics.md', 'graphics', 'Graphiques PDF et rendu de figures'),
        ('docs/security.md', 'security', 'Sécurité du HTML dérivé'),
        ('docs/reference.md', 'reference', 'Référence Deriving HTML from PDF'),
    ]),
}


def load_sources(path: Path) -> dict[str, dict]:
    inventory = json.loads(path.read_text(encoding='utf-8'))
    packages = {item['name']: item for item in inventory['packages']}
    if inventory.get('schemaVersion') != 1 or len(packages) != len(inventory['packages']) or set(packages) != {CORE_PACKAGE, *MODULES}:
        raise ValueError('The released-source manifest must describe every package exactly once')
    for name, package in packages.items():
        if not re.fullmatch(r'\d+\.\d+\.\d+', package.get('version', '')) or not re.fullmatch(r'[0-9a-f]{40}', package.get('revision', '')):
            raise ValueError('Every documented package needs a stable version and exact commit: ' + name)
        expected_repository = REPOSITORY if name == CORE_PACKAGE else 'https://github.com/PDFToolkit/' + name.split('/')[-1]
        if package.get('repository') != expected_repository or package.get('optional') is not (name != CORE_PACKAGE):
            raise ValueError('Incorrect released-source package identity: ' + name)
    return packages


def e(value: object) -> str:
    return escape(str(value), quote=True)


def number(value: int) -> str:
    return format(value, ',').replace(',', '\u202f')


def component_route(name: str) -> str:
    short = name.rsplit('\\', 1)[-1]
    slug = re.sub(r'[^a-z0-9]+', '-', short.lower()).strip('-')[:48]
    digest = hashlib.sha256(name.encode()).hexdigest()[:12]
    return f'reference/components/{slug}-{digest}.html'


def group_for(component: dict) -> str:
    if component['package'] in MODULE_GROUPS:
        return MODULE_GROUPS[component['package']]
    path = component['source']
    if path.startswith('src/Security/'):
        return 'securite'
    if path.startswith('src/Specification/Iso32000_2/'):
        return 'iso2'
    if path.startswith('src/Specification/Adobe/'):
        return 'adobe'
    if path.startswith('src/Specification/Definition/'):
        return 'definitions'
    if path.startswith('src/Specification/Dictionary/'):
        return 'entrees' if len(Path(path).parts) > 4 else 'dictionnaires'
    if path.startswith('src/Specification/'):
        return 'norme'
    if path.startswith('src/Syntax/Object/'):
        return 'objets'
    if path.startswith(('src/Serialization/', 'src/Syntax/FileStructure/', 'src/Syntax/Linearization/')) or path == 'src/FileStructure.php':
        return 'fichier'
    if path.startswith(('src/Graphics/', 'src/Text/', 'src/Syntax/ContentStreamsResources/')):
        return 'contenu'
    if path.startswith('src/Functions/'):
        return 'fonctions'
    if path.startswith('src/Syntax/Filters/'):
        return 'filtres'
    if path.startswith('src/Syntax/LexicalConvention/'):
        return 'lexique'
    return 'document'


class Site:
    def __init__(self, content_root: Path, source_root: Path, output: Path, api: Path, pdfs: Path, pdf_previews: Path, base: str, docs_revision: str, sources: Path, opentype_root: Path | None = None, pdf_to_html_root: Path | None = None):
        self.root, self.content_root, self.output, self.pdfs = source_root, content_root, output, pdfs
        root = source_root
        self.pdf_previews = pdf_previews
        self.pdf_pages = {}
        self.base = '/' + base.strip('/') + '/' if base.strip('/') else '/'
        self.language = 'en'
        self.translations = {}
        self.anchor_maps = {}
        self.docs_revision = docs_revision
        self.stylesheet_revision = hashlib.sha256((content_root / 'docs/site/assets/site.css').read_bytes()).hexdigest()[:12]
        self.script_revision = hashlib.sha256((content_root / 'docs/site/assets/site.js').read_bytes()).hexdigest()[:12]
        self.packages = load_sources(sources)
        self.revision = self.packages[CORE_PACKAGE]['revision']
        self.release = self.packages[CORE_PACKAGE]['version']
        checkout_revision = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'], check=True, capture_output=True, text=True).stdout.strip()
        if checkout_revision != self.revision:
            raise ValueError('Core checkout does not match the released-source manifest')
        locked = json.loads((root / 'composer.lock').read_text(encoding='utf-8'))
        locked_packages = {item['name']: item for item in locked['packages'] + locked['packages-dev']}
        for name in MODULES:
            if name in {"pdftoolkit/opentype", "pdftoolkit/pdf-to-html", "pdftoolkit/pdf-reader"}:
                continue
            item = locked_packages.get(name, {})
            if item.get('version', '').removeprefix('v') != self.packages[name]['version'] or item.get('source', {}).get('reference') != self.packages[name]['revision']:
                raise ValueError('Core Composer lock differs from the selected released source: ' + name)
        module_versions = {self.packages[name]['version'] for name in MODULES}
        self.module_versions = ', '.join(sorted(module_versions))
        inventory = json.loads(api.read_text(encoding='utf-8'))
        api_packages = {item['name']: item for item in inventory['packages']}
        if api_packages != self.packages:
            raise ValueError('API export and released-source manifest disagree')
        if opentype_root is None:
            raise ValueError('The independent OpenType checkout is required')
        opentype_revision = subprocess.run(['git', '-C', str(opentype_root), 'rev-parse', 'HEAD'], check=True, capture_output=True, text=True).stdout.strip()
        if opentype_revision != self.packages['pdftoolkit/opentype']['revision']:
            raise ValueError('OpenType checkout differs from the released-source manifest')
        if pdf_to_html_root is None:
            raise ValueError('The released PDF-to-HTML checkout is required')
        html_revision = subprocess.run(['git', '-C', str(pdf_to_html_root), 'rev-parse', 'HEAD'], check=True, capture_output=True, text=True).stdout.strip()
        if html_revision != self.packages['pdftoolkit/pdf-to-html']['revision']:
            raise ValueError('PDF-to-HTML checkout differs from the released-source manifest')
        reader_consumer = select_reader(root, pdf_to_html_root, self.packages)
        self.package_roots = {CORE_PACKAGE: root, **{name: root / 'vendor' / name for name in MODULES if name not in {'pdftoolkit/opentype', 'pdftoolkit/pdf-to-html', 'pdftoolkit/pdf-reader'}}, 'pdftoolkit/opentype': opentype_root, 'pdftoolkit/pdf-to-html': pdf_to_html_root, 'pdftoolkit/pdf-reader': reader_consumer / 'vendor/pdftoolkit/pdf-reader'}
        self.html_reference = json.loads((pdf_to_html_root / 'resources/reference.json').read_text(encoding='utf-8'))
        reference_path = self.html_reference['source']
        if reference_path != 'resources/reference-documents/Deriving_HTML_from_PDF_1-2.pdf':
            raise ValueError('The supplied derivation reference must preserve its original filename')
        reference_file = pdf_to_html_root / reference_path
        if reference_file.stat().st_size != self.html_reference['bytes'] or hashlib.sha256(reference_file.read_bytes()).hexdigest() != self.html_reference['sha256'] or self.html_reference['physicalPdfPages'] != 74:
            raise ValueError('The supplied derivation reference must preserve its original bytes and physical pages')
        self.documentation = {'repository': DOCUMENTATION_REPOSITORY, 'revision': docs_revision}
        self.documentation_sources = []
        self.components = inventory['components']
        for item in self.components:
            package = self.packages.get(item['package'])
            if package is None or any(item[key] != package[key] for key in ('repository', 'revision', 'optional', 'version')):
                raise ValueError('Inconsistent API package metadata: ' + item['name'])
            if item['optional'] and not re.fullmatch(r'[0-9a-f]{40}', item['revision'] or ''):
                raise ValueError('Optional API sources must use their locked commit: ' + item['name'])
            if not item['source'].startswith('src/') or '..' in Path(item['source']).parts:
                raise ValueError('Invalid API source path: ' + item['name'])
        self.by_name = {item['name']: item for item in self.components}
        if len(self.by_name) != len(self.components):
            raise ValueError('Duplicate API component names')
        self.by_source = {item['source']: item for item in self.components if not item['optional']}
        self.by_package_source = {(item['package'], item['source']): item for item in self.components}
        self.routes = {item['name']: component_route(item['name']) for item in self.components}
        self.groups = defaultdict(list)
        for item in self.components:
            self.groups[group_for(item)].append(item)
        self.pages = [(CORE_PACKAGE if source in {'SECURITY.md', 'CHANGELOG.md'} else 'documentation', source, route, title, category) for source, route, title, category in GUIDES]
        for name, (slug, title, guides) in MODULES.items():
            for source, page_slug, page_title in [('README.md', 'index', title), *guides, ('SECURITY.md', 'signalements', 'Signaler une vulnérabilité'), ('CHANGELOG.md', 'versions', 'Versions et changements')]:
                self.pages.append((name, source, f'modules/{slug}/{page_slug}.html', page_title, title))
        self.examples = {'table': 'recipes/table.html'}
        for source, slug, title, example, _ in LESSONS:
            route = f'tutorials/{slug}.html'
            self.pages.append(('documentation', f'docs/tutorials/{source}.md', route, title, 'Tutoriels'))
            self.examples[example] = route
        if not set(EXTERNAL_EXAMPLES) <= set(self.examples):
            raise ValueError('Every external example needs a documented site page')
        self.example_sources = {}
        for example, route in self.examples.items():
            external = EXTERNAL_EXAMPLES.get(example)
            package_name = external['package'] if external else 'roukmoute/pdf'
            package = self.packages.get(package_name)
            if package is None:
                raise ValueError('Missing example source package: ' + package_name)
            source = external['source'] if external else f'examples/{example}.php'
            directory = self.package_roots[package_name]
            record = {
                'kind': external.get('kind', 'input') if external else 'generated',
                'package': package_name,
                'page': route,
                'source': source,
                'sourceUrl': self.source_url(source, owner=package),
                'path': directory / source,
            }
            if external:
                if not package['optional'] or not re.fullmatch(r'[0-9a-f]{40}', package['revision'] or ''):
                    raise ValueError('External examples need an installed package pinned to a commit')
                record.update(
                    input=external['input'],
                    inputPath=directory / external['input'],
                    inputSourceUrl=self.source_url(external['input'], owner=package),
                    expectedPages=external.get('expectedPages'),
                )
            self.example_sources[example] = record
        self.markdown_routes = {(owner, source): route for owner, source, route, _, _ in self.pages}
        self.markdown_routes.update({(CORE_PACKAGE, source): route for owner, source, route, _, _ in self.pages if owner == 'documentation'})
        self.markdown_routes[(CORE_PACKAGE, 'README.md')] = 'guides/demarrer.html'
        ENGLISH_ROUTES.update({f'tutorials/{slug}.html': f'tutorials/{source}.html' for source, slug, _, _, _ in LESSONS})
        resources = root / 'resources' / 'iso32000-1'
        self.metadata = json.loads((resources / 'metadata.json').read_text(encoding='utf-8'))
        self.tables = {item['id']: item for item in json.loads((resources / 'dictionaries.json').read_text(encoding='utf-8'))}
        self.catalogue = json.loads((resources / 'classes.json').read_text(encoding='utf-8'))
        self.table_classes = {item['table']: item for item in self.catalogue}
        self.spec_by_name = {}
        self.entry_classes = {}
        for item in self.catalogue:
            self.spec_by_name[item['class']] = (item['table'], None)
            self.spec_by_name[item['definition_class']] = (item['table'], None)
            for entry in item['entries']:
                self.spec_by_name[entry['class']] = (item['table'], entry['name'])
                self.entry_classes[(item['table'], entry['name'])] = entry['class']
        self.corrections = json.loads((resources / 'corrections.json').read_text(encoding='utf-8'))
        adobe = root / 'resources' / 'adobe-supplement-iso32000'
        self.adobe_metadata = json.loads((adobe / 'metadata.json').read_text(encoding='utf-8'))
        archival = json.loads((root / 'resources/adobe-references/metadata.json').read_text(encoding='utf-8'))
        self.reference_sources = {item['document']: item for item in archival['documents']}
        self.adobe_tables = {item['id']: item for item in json.loads((adobe / 'dictionaries.json').read_text(encoding='utf-8'))}
        self.adobe_classes = {item['table']: item for item in json.loads((adobe / 'classes.json').read_text(encoding='utf-8'))}
        self.adobe_corrections = json.loads((adobe / 'corrections.json').read_text(encoding='utf-8'))
        self.adobe_spec_by_name = {}
        self.adobe_entry_classes = {}
        for item in self.adobe_classes.values():
            self.adobe_spec_by_name[item['class']] = (item['table'], None)
            self.adobe_spec_by_name[item['definition_class']] = (item['table'], None)
            for entry in item['entries']:
                self.adobe_spec_by_name[entry['class']] = (item['table'], entry['name'])
                self.adobe_entry_classes[(item['table'], entry['name'])] = entry['class']
        iso2 = root / 'resources' / 'iso32000-2-2020'
        self.iso2_metadata = json.loads((iso2 / 'metadata.json').read_text(encoding='utf-8'))
        bundle = json.loads((root / 'resources/iso32000-2-bundle/sources.json').read_text(encoding='utf-8'))
        self.bundle_sources = bundle['documents']
        for original in self.bundle_sources:
            path = root / original['path']
            if path.name != original['filename'] or not path.resolve().is_relative_to(root.resolve()) or path.stat().st_size != original['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest() != original['sha256']:
                raise ValueError('Modified ISO 32000-2 bundle original: ' + original['filename'])
        self.iso2_tables = {item['id']: item for item in json.loads((iso2 / 'dictionaries.json').read_text(encoding='utf-8'))}
        self.iso2_classes = {item['table']: item for item in json.loads((iso2 / 'classes.json').read_text(encoding='utf-8'))}
        missing_summaries = sorted({entry['description'] for table in self.iso2_tables.values() for entry in [*table['entries'], *table.get('variable_entries', [])] if entry.get('description_origin', 'project-authored') == 'project-authored'} - set(ISO2_DESCRIPTIONS_FR))
        if missing_summaries:
            raise ValueError('Missing authored French ISO2 summaries: ' + repr(missing_summaries))
        self.iso2_spec_by_name = {}
        self.iso2_entry_classes = {}
        for item in self.iso2_classes.values():
            self.iso2_spec_by_name[item['class']] = (item['table'], None)
            self.iso2_spec_by_name[item['definition_class']] = (item['table'], None)
            for entry in item['entries']:
                self.iso2_spec_by_name[entry['class']] = (item['table'], entry['name'])
                self.iso2_entry_classes[(item['table'], entry['name'])] = entry['class']
        # Native implementations declare their reviewed table explicitly. A
        # bare TABLE number cannot identify an edition (ISO1/ISO2 both use 29).
        self.iso2_spec_by_name['PDF\\Document\\Files\\AssociatedFilesPropertyList'] = ('409a', None)
        self.iso2_spec_by_name.update({
            'PDF\\Document\\Files\\EncryptedPayload': ('28', None),
            'PDF\\Document\\Parts\\DocumentPartRoot': ('408', None),
            'PDF\\Document\\Parts\\DocumentPart': ('409', None),
            'PDF\\Document\\Parts\\DocumentPartMetadata': ('409', 'DPM'),
            'PDF\\Document\\Signatures\\PendingDocumentTimestamp': ('255', None),
            'PDF\\Document\\Signatures\\DocumentSecurityStore': ('261', None),
            'PDF\\Document\\Signatures\\ValidationRelatedInformation': ('262', None),
            'PDF\\Document\\Structure\\StructureNamespace': ('356', None),
            'PDF\\Document\\Structure\\NamespaceRoleMap': ('356', 'RoleMapNS'),
            'PDF\\Graphics\\GraphicsState\\UseBlackPointCompensation': ('57', 'UseBlackPtComp'),
            'PDF\\Document\\Geospatial\\Viewport': ('265', None),
            'PDF\\Document\\Geospatial\\GeospatialMeasure': ('269', None),
            'PDF\\Document\\Geospatial\\GeographicCoordinateSystem': ('270', None),
            'PDF\\Document\\Geospatial\\ProjectedCoordinateSystem': ('271', None),
            'PDF\\Document\\Geospatial\\PointData': ('272', None),
        })
        self.children = defaultdict(list)
        for item in self.components:
            if item['parent']:
                self.children[item['parent']].append(item)
        self.written = []

    def url(self, route: str, language: str | None = None) -> str:
        return self.base + route_for(route, language or self.language)

    def prepare_anchors(self) -> None:
        """Pair translated headings in order, failing on incomplete structure."""
        def headings(text):
            renderer = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc', 'sane_lists'])
            renderer.convert(text)
            def flatten(tokens):
                return [value for token in tokens for value in [token, *flatten(token.get('children', []))]]
            return flatten(renderer.toc_tokens)
        for owner, source, route, _, _ in self.pages:
            root = self.content_root if owner == 'documentation' else self.package_roots[owner]
            tokens = {language: headings((root / localized_source(owner, source, language)).read_text(encoding='utf-8')) for language in LANGUAGES}
            if [token['level'] for token in tokens['en']] != [token['level'] for token in tokens['fr']]:
                raise ValueError('Translated heading structure differs: ' + owner + ':' + source)
            self.anchor_maps[route] = {
                'en': {en['id']: fr['id'] for en, fr in zip(tokens['en'], tokens['fr']) if en['level'] > 1},
                'fr': {fr['id']: en['id'] for en, fr in zip(tokens['en'], tokens['fr']) if fr['level'] > 1},
            }

    def fragment_for(self, route: str, fragment: str, language: str | None = None) -> str:
        language = language or self.language
        other = 'fr' if language == 'en' else 'en'
        return self.anchor_maps.get(route, {}).get(other, {}).get(unquote(fragment), fragment)

    def source_url(self, source: str, line: int | None = None, owner: dict | None = None) -> str:
        package = owner if owner is not None else self.packages[CORE_PACKAGE]
        repository = package['repository']
        revision = package['revision']
        url = f'{repository}/blob/{revision}/{quote(source, safe="/")}'
        return url + (f'#L{line}' if line else '')

    def link_type(self, value: str | None) -> str:
        if value is None:
            return ''
        parts, previous = [], 0
        for match in re.finditer(r'\b(?:PDF|PDFToolkit\\OpenType)\\[A-Za-z_][A-Za-z0-9_\\]*', value):
            parts.append(e(value[previous:match.start()]))
            name = match.group()
            if name in self.routes:
                parts.append(f'<a href="{e(self.url(self.routes[name]))}">{e(name)}</a>')
            else:
                parts.append(e(name))
            previous = match.end()
        return ''.join(parts) + e(value[previous:])

    def write(self, route: str, html: str) -> None:
        route = route_for(route, self.language)
        file = self.output / route
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(html, encoding='utf-8', newline='\n')
        self.written.append(route)

    def sidebar(self, current: str) -> str:
        groups = [
            ('Découvrir', [('index.html', 'Accueil'), ('guides/demarrer.html', 'Démarrer'), ('guides/modules.html', 'Core et modules'), ('guides/pdf-2-0.html', 'PDF 2.0'), ('guides/composants.html', 'Les composants'), ('guides/architecture.html', 'Architecture')]),
            ('Packages', [('modules/core/index.html', 'Core : objets et écriture'), *[(f'modules/{slug}/index.html', title) for slug, title, _ in MODULES.values()]]),
            ('Explorer', [('reference/index.html', 'Référence des composants'), ('guides/couverture.html', 'Couverture de la norme'), ('guides/mecanismes.html', 'Couverture des éditions PDF'), ('guides/source-audits.html', 'Règles de source et corrections vérifiées'), ('guides/pdf-2-0-bundle.html', 'Spécifications complémentaires PDF 2.0'), ('guides/supplement-adobe.html', 'Supplément Adobe'), ('guides/references-adobe.html', 'Références Adobe conservées'), ('guides/securite.html', 'Sécurité'), ('guides/revisions-protegees.html', 'Révisions natives protégées'), ('guides/versions.html', 'Versions')]),
            ('Apprendre', [('tutorials/index.html', 'Tous les tutoriels'), *[(f'tutorials/{slug}.html', f'{i:02d}. {title}') for i, (_, slug, title, _, _) in enumerate(LESSONS, 1)], ('recipes/table.html', 'Recette : tableau')]),
        ]
        html = ''
        for label, links in groups:
            html += f'<div class="nav-group"><h2>{e(label)}</h2>'
            for route, title in links:
                active = current == route
                selected = ' aria-current="page"' if active else ''
                html += f'<a class="nav-link{" active" if active else ""}" href="{e(self.url(route))}"{selected}>{e(title)}</a>'
            html += '</div>'
        return html

    def page(self, route: str, title: str, category: str, body: str, toc: list[dict] | None = None, description: str = '') -> None:
        self.translations[route] = {language: route_for(route, language) for language in LANGUAGES}
        alternates = ''.join(f'<link rel="alternate" hreflang="{language}" href="{e(SITE_ORIGIN + self.base + route_for(route, language))}">' for language in LANGUAGES)
        alternates += f'<link rel="alternate" hreflang="x-default" href="{e(SITE_ORIGIN + self.base + route_for(route, "en"))}">'
        other = 'fr' if self.language == 'en' else 'en'
        anchor_map = self.anchor_maps.get(route, {}).get(self.language, {})
        switch = f'<nav class="language-switch" aria-label="Language / Langue"><span lang="{self.language}" aria-current="true">{"English" if self.language == "en" else "Français"}</span><a lang="{other}" hreflang="{other}" href="{e(self.base + route_for(route, other))}" data-language-link data-anchor-map="{e(json.dumps(anchor_map, ensure_ascii=False, separators=(",", ":")))}">{"Français" if other == "fr" else "English"}</a></nav>'
        toc_html = ''
        if toc:
            links = ''.join(f'<li><a href="#{e(item["id"])}">{e(item["name"])}</a></li>' for item in toc if item['level'] == 2)
            if links:
                toc_html = f'<aside class="toc" aria-label="Sur cette page"><h2>Sur cette page</h2><ul>{links}</ul></aside>'
        header = '' if route == 'index.html' else f'<header class="page-header"><p class="eyebrow">{e(category)}</p><h1>{e(title)}</h1></header>'
        html = f'''<!doctype html>
<html lang="{self.language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} · PDFToolkit</title><meta name="description" content="{e(description or title + ' — modèle objet PDF pour PHP 8.3+.')}">
<link rel="canonical" href="{e(SITE_ORIGIN + self.url(route))}">
{alternates}
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; frame-src 'self'; object-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'">
<link rel="icon" href="{e(self.url('assets/favicon.svg'))}" type="image/svg+xml">
<link rel="stylesheet" href="{e(self.url('assets/site.css') + '?v=' + self.stylesheet_revision)}"><script defer src="{e(self.url('assets/site.js') + '?v=' + self.script_revision)}"></script></head>
<body><a class="skip-link" href="#main">Aller au contenu</a>
<header class="site-header"><a class="brand" href="{e(self.url('index.html'))}"><span class="brand-mark" aria-hidden="true">◈</span> PDFToolkit <small>objet par objet</small></a>
<nav class="top-nav" aria-label="Navigation principale"><a href="{e(self.url('guides/modules.html'))}">Packages</a><a href="{e(self.url('guides/pdf-2-0.html'))}">PDF 2.0</a><a href="{e(self.url('tutorials/index.html'))}">Tutoriels</a><a href="{e(self.url('reference/index.html'))}">Référence</a><a href="{DOCUMENTATION_REPOSITORY}">GitHub ↗</a></nav>
{switch}
<button id="menu-button" class="menu-button" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button></header>
<div class="site-shell"><aside id="site-nav" class="sidebar" aria-label="Documentation">{self.sidebar(route)}<p class="sidebar-version">Core <strong>{e(self.release)}</strong> · modules {e(self.module_versions)}<br>PHP 8.3+ 64 bits · PDF 1.7 et 2.0</p></aside>
<main id="main" data-root="{e(self.base)}">{header}<div class="content-grid"><article class="prose">{body}</article>{toc_html}</div>
<footer class="site-footer"><span>PDFToolkit · ISO 32000-1:2008 · ISO 32000-2:2020 · MIT</span><span><a href="{REPOSITORY}/releases/tag/v{e(self.release)}">Core {e(self.release)}</a> · <a href="{DOCUMENTATION_REPOSITORY}/commit/{e(self.docs_revision)}">Documentation {e(self.docs_revision[:7])}</a></span></footer></main></div></body></html>'''
        self.write(route, translate_interface(html) if self.language == 'en' else html)

    def package_link(self, package_name: str, target: str, fragment: str = '', query: str = '', language: str | None = None) -> str | None:
        suffix = ('?' + query if query else '') + ('#' + fragment if fragment else '')
        canonical = canonical_source(package_name, target)
        route = self.markdown_routes.get((package_name, canonical))
        if route:
            fragment = self.fragment_for(route, fragment, language)
            return self.url(route, language) + ('?' + query if query else '') + ('#' + fragment if fragment else '')
        item = self.by_package_source.get((package_name, target))
        if item and not fragment:
            return self.url(self.routes[item['name']]) + suffix
        for name, record in self.example_sources.items():
            if record['package'] == package_name and not fragment:
                if record['source'] == target:
                    return self.url(self.examples[name]) + ('?' + query if query else '') + '#code-source'
                if record.get('input') == target:
                    return self.url(f'examples/{name}.pdf') + suffix
        if package_name == CORE_PACKAGE:
            if target == self.adobe_metadata['path']:
                return self.url('downloads/adobe-supplement-iso32000.pdf') + suffix
            if target == self.metadata['source_path']:
                return self.url('downloads/iso-32000-1.pdf') + suffix
            for filename, original in self.reference_sources.items():
                if target == original['path']:
                    return self.url('downloads/adobe-references/' + quote(filename, safe='')) + suffix
        root = self.package_roots[package_name]
        package = self.packages[package_name]
        if (root / target).is_file():
            return self.source_url(target, owner=package) + suffix
        if (root / target).is_dir():
            return f'{package["repository"]}/tree/{package["revision"]}/{quote(target, safe="/")}' + suffix
        return None

    def rewrite_link(self, source: str, href: str, owner: str = 'documentation') -> str:
        parsed = urlsplit(href)
        if parsed.netloc == 'github.com':
            match = re.fullmatch(r'/PDFToolkit/(pdf|pdf-fonts|pdf-images|pdf-reader|pdf-to-html|opentype)/(?:blob|tree)/[^/]+/(.+)', parsed.path)
            if match:
                package_name = CORE_PACKAGE if match.group(1) == 'pdf' else 'pdftoolkit/' + match.group(1)
                target = posixpath.normpath(unquote(match.group(2), errors='strict'))
                if target.startswith('../') or target in {'..', '.'} or target.startswith('/') or '\\' in target or ':' in target:
                    raise ValueError(f'GitHub source link escapes its source package: {source} -> {href}')
                language = 'fr' if target.endswith('.fr.md') or target.startswith('docs/fr/') else self.language
                if owner == package_name and canonical_source(owner, source) == canonical_source(owner, target) and source != target:
                    language = 'fr' if self.language == 'en' else 'en'
                result = self.package_link(package_name, target, parsed.fragment, parsed.query, language)
                if result:
                    return result
                raise ValueError(f'Unresolved package source link: {source} -> {href}')
            match = re.fullmatch(r'/PDFToolkit/(pdf|pdf-fonts|pdf-images|pdf-reader|pdf-to-html|opentype)/?', parsed.path)
            if match and parsed.fragment in {'', 'readme'}:
                package_name = CORE_PACKAGE if match.group(1) == 'pdf' else 'pdftoolkit/' + match.group(1)
                route = 'modules/core/index.html' if package_name == CORE_PACKAGE else self.markdown_routes[(package_name, 'README.md')]
                return self.url(route) + ('?' + parsed.query if parsed.query else '')
        if parsed.netloc == 'pdftoolkit.github.io':
            route = parsed.path.removeprefix('/pdf/').lstrip('/') if parsed.path.startswith('/pdf/') else parsed.path.lstrip('/')
            route = route.removeprefix('fr/')
            route = next((old for old, new in ENGLISH_ROUTES.items() if new == route), route) or 'index.html'
            fragment = self.fragment_for(route, parsed.fragment)
            return self.url(route) + ('?' + parsed.query if parsed.query else '') + ('#' + fragment if fragment else '')
        if parsed.scheme or parsed.netloc or not parsed.path:
            return href
        if parsed.path.startswith('/'):
            return self.url(parsed.path.lstrip('/')) + ('?' + parsed.query if parsed.query else '') + ('#' + parsed.fragment if parsed.fragment else '')
        target = posixpath.normpath(posixpath.join(posixpath.dirname(source), unquote(parsed.path, errors='strict')))
        if target.startswith('../') or target == '..' or target.startswith('/') or '\\' in target or ':' in target:
            raise ValueError(f'Markdown link escapes its source package: {source} -> {href}')
        suffix = ('?' + parsed.query if parsed.query else '') + ('#' + parsed.fragment if parsed.fragment else '')
        canonical = canonical_source(owner, target)
        route = self.markdown_routes.get((owner, canonical))
        if route:
            language = self.language
            if canonical_source(owner, source) == canonical and source != target:
                language = 'fr' if self.language == 'en' else 'en'
            fragment = self.fragment_for(route, parsed.fragment, language)
            return self.url(route, language) + ('?' + parsed.query if parsed.query else '') + ('#' + fragment if fragment else '')
        if owner == 'documentation':
            if canonical in {'README.md', 'SECURITY.md', 'CHANGELOG.md'}:
                return self.package_link(CORE_PACKAGE, canonical, parsed.fragment, parsed.query)
            if target.startswith('docs/tutorials/previews/'):
                return self.url('assets/previews/' + Path(target).name) + suffix
            if (self.content_root / target).is_file():
                return self.source_url(target, owner=self.documentation) + suffix
            package_name = CORE_PACKAGE
        else:
            package_name = owner
        result = self.package_link(package_name, target, parsed.fragment, parsed.query)
        if result:
            return result
        raise ValueError(f'Unresolved Markdown link: {owner}:{source} -> {href}')

    def render_markdown(self, owner: str, source: str) -> tuple[str, list[dict]]:
        renderer = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc', 'sane_lists'])
        root = self.content_root if owner == 'documentation' else self.package_roots[owner]
        html = renderer.convert((root / source).read_text(encoding='utf-8'))
        html = re.sub(r'<h1\b[^>]*>.*?</h1>\s*', '', html, count=1, flags=re.S)
        # Keep published French section links usable on English routes as well.
        logical = self.markdown_routes.get((owner, canonical_source(owner, source)))
        if self.language == 'en' and logical:
            existing_ids = set(re.findall(r'\bid="([^"]+)"', html))
            for french, english in self.anchor_maps.get(logical, {}).get('fr', {}).items():
                if french != english and french not in existing_ids:
                    pattern = r'(<h[2-6]\b[^>]*\bid="' + re.escape(english) + r'"[^>]*>)'
                    html, count = re.subn(pattern, lambda match: f'<span class="legacy-anchor" id="{e(french)}" aria-hidden="true"></span>' + match.group(0), html, count=1)
                    if count:
                        existing_ids.add(french)
        def rewrite(match):
            from html import unescape
            value = self.rewrite_link(source, unescape(match.group(2)), owner)
            return match.group(1) + e(value) + match.group(3)
        html = re.sub(r'((?:href|src)=")([^"]+)(")', rewrite, html)
        # The first tutorial's simple flowchart is rendered locally, without a CDN.
        def flowchart(match):
            from html import unescape
            code = unescape(match.group(1))
            nodes, edges = {}, []
            for line in code.splitlines():
                parts = re.match(r'\s*(\w+)(?:\[([^\]]+)\])?\s*-->\s*(\w+)(?:\[([^\]]+)\])?', line)
                if parts:
                    left, left_text, right, right_text = parts.groups()
                    nodes.setdefault(left, left_text or left)
                    nodes.setdefault(right, right_text or right)
                    edges.append((left, right))
            if not edges:
                return match.group(0)
            levels = {key: 0 for key in nodes}
            for _ in range(len(nodes)):
                for left, right in edges:
                    levels[right] = max(levels[right], levels[left] + 1)
            if max(levels.values()) >= len(nodes):
                return match.group(0)
            by_level = defaultdict(list)
            for key, level in levels.items():
                by_level[level].append(key)
            positions = {}
            width, height = 700, (max(levels.values()) + 1) * 90
            for level, keys in by_level.items():
                for i, key in enumerate(keys):
                    positions[key] = ((i + 0.5) * width / len(keys), level * 90 + 32)
            parts = [f'<svg class="object-graph" viewBox="0 0 {width} {height}" role="img" aria-label="Le catalogue relie l’arbre des pages, les contenus et les ressources">']
            for left, right in edges:
                x, y = positions[left]
                xx, yy = positions[right]
                parts.append(f'<path d="M{x} {y+23} L{xx} {yy-23}" stroke="#0a7166" stroke-width="2" fill="none"/>')
            for key, (x, y) in positions.items():
                parts.append(f'<rect x="{x-105}" y="{y-23}" width="210" height="46" rx="8" fill="#edf5f2" stroke="#a3c3bb"/><text x="{x}" y="{y+5}" text-anchor="middle" font-family="system-ui,sans-serif" font-size="14" fill="#17212d">{e(nodes[key])}</text>')
            return ''.join(parts) + '</svg>'
        html = re.sub(r'<pre><code class="language-mermaid">(.*?)</code></pre>', flowchart, html, flags=re.S)
        def flatten(items):
            return [token for item in items for token in [item, *flatten(item.get('children', []))]]
        return html, flatten(renderer.toc_tokens)

    def example_panel(self, example: str) -> str:
        record = self.example_sources[example]
        code = record['path'].read_text(encoding='utf-8')
        pdf = self.url(f'examples/{example}.pdf')
        source = self.url(f'examples/{example}.php.txt')
        pages = self.pdf_pages[example]
        is_input = record['kind'] in {'input', 'conversion'}
        is_conversion = record['kind'] == 'conversion'
        pdf_label = 'PDF d’entrée' if is_input else 'Résultat PDF'
        heading = 'Voir le PDF d’entrée' if is_input else 'Voir le résultat PDF'
        source_name = Path(record['source']).name
        page_images = ''.join(
            f'<figure class="pdf-page"><a href="{e(self.url("assets/pdf-pages/" + image["file"]))}" target="_blank" rel="noopener" aria-label="Agrandir la page {number} sur {len(pages)}">'
            f'<img src="{e(self.url("assets/pdf-pages/" + image["file"]))}" alt="{pdf_label} {e(example)} : page {number} sur {len(pages)}" width="{image["width"]}" height="{image["height"]}" loading="lazy"></a>'
            f'<figcaption>Page {number} sur {len(pages)}</figcaption></figure>'
            for number, image in enumerate(pages, 1)
        )
        description = 'Ce PDF balisé est l’entrée de la conversion. Le résultat HTML est produit par le script exécuté pendant la construction du site ; l’aperçu conserve la structure sémantique plutôt que la mise en page du PDF.' if is_conversion else (
            'Ce PDF est l’entrée du lecteur : une fixture originale créée avec pypdf et qpdf, indépendamment du writer PHP. '
            'Ses trois pages sont reproduites ci-dessous ; le résultat de la lecture figure ensuite dans la sortie console.'
            if is_input else
            'Ce fichier a été généré avec le code de cette documentation. Toutes ses pages sont reproduites ci-dessous ; ouvrir le PDF pour utiliser ses liens et ses signets.'
        )
        provenance = f'<p>Code de <code>{e(record["package"])}</code> · <a href="{e(record["sourceUrl"])}">Consulter la source au commit documenté ↗</a>'
        if is_input:
            provenance += f' · <a href="{e(record["inputSourceUrl"])}">Origine du PDF d’entrée ↗</a>'
        provenance += '</p>'
        console = ''
        if is_input:
            result = (self.pdfs / (example + '.txt')).read_text(encoding='utf-8')
            console = f'''<section class="source-panel" id="resultat-lecture"><div class="panel-intro"><h2>Résultat de la lecture</h2>
<p>Sortie réelle du script exécuté sur le PDF d’entrée pendant la construction de cette documentation.
<a href="{e(self.url(f"examples/{example}.txt"))}" download>Télécharger la sortie console</a>.</p></div>
<pre><code class="language-text">{e(result)}</code></pre></section>'''
        if is_conversion:
            html_result = self.url(f'examples/{example}.html')
            console += f'''<section class="source-panel" id="resultat-html"><div class="panel-intro"><h2>Résultat HTML</h2>
<p>Sortie réelle de la dérivation, isolée dans une frame sans autorisation de script, de formulaire ou de navigation de la page principale.</p>
<p><a href="{e(html_result)}" download>Télécharger le HTML</a></p></div>
<iframe class="pdf-viewer" sandbox="" src="{e(html_result)}" title="Résultat HTML" loading="lazy"></iframe>
<details><summary>Lire la source HTML</summary><pre><code class="language-html">{e((self.pdfs / (example + '.html')).read_text(encoding='utf-8'))}</code></pre></details></section>'''
        return f'''<section class="pdf-panel" id="resultat-pdf"><div class="panel-intro"><h2>{heading}</h2>
<p>{description}</p></div>
<div class="pdf-actions"><a class="button" href="{e(pdf)}" target="_blank" rel="noopener">Ouvrir le PDF ↗</a><a class="button secondary" href="{e(pdf)}" download>Télécharger</a><a class="button secondary" href="{e(source)}" download="{e(source_name)}">Télécharger le code PHP</a></div>
<div class="pdf-pages" role="region" aria-label="Aperçu des {len(pages)} pages du PDF {e(example)}" tabindex="0">{page_images}</div>
<details class="pdf-native"><summary>Utiliser le lecteur PDF du navigateur</summary>
<p class="search-hint">Ce lecteur dépend du navigateur. Si le document ne s’affiche pas, utiliser « Ouvrir le PDF » ou « Télécharger ».</p>
<iframe class="pdf-viewer" src="{e(pdf)}#view=FitH" title="{pdf_label} : {e(example)}" loading="lazy"></iframe>
</details></section>
{console}<section class="source-panel" id="code-source"><div class="panel-intro"><h2>Code source complet</h2>{provenance}</div><details><summary>Lire le script commenté : {e(source_name)}</summary><pre><code class="language-php">{e(code)}</code></pre></details></section>'''

    def tutorial_cards(self) -> str:
        html = '<div class="cards">'
        for i, (_, slug, title, example, text) in enumerate(LESSONS, 1):
            preview = 'assets/pdf-pages/' + self.pdf_pages[example][0]['file']
            html += f'<a class="card" href="{e(self.url("tutorials/" + slug + ".html"))}"><div class="card-preview"><img src="{e(self.url(preview))}" alt="Aperçu : {e(title)}" loading="lazy"></div><div class="card-body"><span class="eyebrow">Tutoriel {i:02d}</span><h3>{e(title)}</h3><p>{e(text)}</p><span class="card-link">Lire et voir le PDF →</span></div></a>'
        return html + '</div>'

    def component_cards(self, components: list[dict]) -> str:
        html = '<div class="reference-grid">'
        for item in components:
            description = item['description'].split('\n')[0][:200]
            package = f'<span class="badge">Optionnel · {e(item["package"])}</span>' if item['optional'] else ''
            html += f'<a class="component-card" href="{e(self.url(self.routes[item["name"]]))}"><span class="badge">{e(item["kind"])}</span>{package}<h3>{e(item["shortName"])}</h3><code>{e(item["namespace"])}</code><p lang="en">{e(description)}</p></a>'
        return html + '</div>'

    def search(self) -> str:
        index = 'assets/search-index.fr.json' if self.language == 'fr' else 'assets/search-index.json'
        return f'''<div class="search-field"><label for="component-search">Rechercher un composant<input id="component-search" type="search" placeholder="NameType, /MediaBox, FlateDecode…" data-search-index="{e(self.url(index))}" autocomplete="off"></label><label for="component-kind">Type de composant<select id="component-kind"><option value="">Tous les types</option><option value="class">Classes</option><option value="interface">Interfaces</option><option value="enum">Enums</option><option value="trait">Traits</option></select></label></div><p id="search-status" class="search-hint" role="status" aria-live="polite">{number(len(self.components))} composants dans le code, dont les définitions et entrées normalisées.</p><div id="search-results" class="search-results" hidden></div>'''

    def package_route(self, name: str) -> str:
        slug = 'core' if name == CORE_PACKAGE else MODULES[name][0]
        return f'reference/packages/{slug}.html'

    def packagist_link(self, name: str) -> str:
        return f'<a href="https://packagist.org/packages/{quote(name, safe="/")}">Installer avec Composer · Packagist ↗</a>'

    def package_cards(self) -> str:
        cards = ''
        for name, package in self.packages.items():
            guide = 'modules/core/index.html' if name == CORE_PACKAGE else f'modules/{MODULES[name][0]}/index.html'
            count = sum(item['package'] == name for item in self.components)
            cards += f'<div class="card"><div class="card-body"><span class="eyebrow">{"Module optionnel" if package["optional"] else "Core"} · {e(package["version"])}</span><h3><code>{e(name)}</code></h3><p>{number(count)} composants</p><p><a href="{e(self.url(guide))}">Guide du package →</a></p><p><a href="{e(self.url(self.package_route(name)))}">Référence API →</a></p><p>{self.packagist_link(name)}</p></div></div>'
        return '<div class="cards">' + cards + '</div>'

    def module_navigation(self, name: str) -> str:
        slug, title, guides = MODULES[name]
        links = [(f'modules/{slug}/index.html', 'Présentation'), *[(f'modules/{slug}/{route}.html', label) for _, route, label in guides], (self.package_route(name), 'Référence API'), (f'modules/{slug}/signalements.html', 'Signalements privés'), (f'modules/{slug}/versions.html', 'Changelog')]
        return '<nav class="module-navigation" aria-label="Guides du module"><h2>' + e(title) + '</h2><ul>' + ''.join(f'<li><a href="{e(self.url(route))}">{e(label)}</a></li>' for route, label in links) + '</ul></nav>'

    def core_hub(self) -> None:
        package = self.packages[CORE_PACKAGE]
        body = f'<p><span class="badge">Core · <code>{CORE_PACKAGE}</code> {e(package["version"])}</span></p><p>Le core représente les objets et mécanismes de PDF 1.7 et PDF 2.0 et les compose en fichiers PDF. Il fournit la syntaxe, les dictionnaires, les flux, les pages, les images et les polices PDF, ainsi que l’écriture et les révisions. Les lecteurs de PDF externes, PNG/JPEG et TrueType sont des modules optionnels.</p>'
        install_command = f'composer require "{CORE_PACKAGE}:^{package["version"]}"'
        body += f'<h2>Installer le core</h2><p>{self.packagist_link(CORE_PACKAGE)}</p><pre><code class="language-sh">{e(install_command)}</code></pre><p>Composer installe uniquement le core et vérifie ses extensions PHP requises. Les modules optionnels sont choisis par l’application.</p>'
        body += '<h2>Commencer et construire</h2><ul>'
        for route, title in [('guides/demarrer.html', 'Installation et premier document'), ('tutorials/index.html', 'Tutoriels avec code et PDF'), ('guides/composants.html', 'Responsabilités des composants'), ('guides/architecture.html', 'Architecture'), ('recipes/index.html', 'Recettes')]:
            body += f'<li><a href="{e(self.url(route))}">{e(title)}</a></li>'
        body += '</ul><h2>Référence et versions</h2><ul>'
        for route, title in [(self.package_route(CORE_PACKAGE), 'API du core'), ('guides/couverture.html', 'Définitions et couverture de la norme'), ('guides/mecanismes.html', 'Mécanismes vérifiés et limites'), ('guides/source-audits.html', 'Règles de source et corrections vérifiées'), ('tutorials/36-caviardisation.html', 'Appliquer une caviardisation'), ('guides/securite.html', 'Sécurité et responsabilités'), ('guides/signalements.html', 'Signalements privés'), ('guides/versions.html', 'Changelog')]:
            body += f'<li><a href="{e(self.url(route))}">{e(title)}</a></li>'
        body += f'</ul><p><a href="{e(package["repository"] + "/releases/tag/v" + package["version"])}">Version publiée {e(package["version"])}</a> · <a href="{e(package["repository"] + "/commit/" + package["revision"])}">Source {e(package["revision"][:7])}</a></p>'
        self.page('modules/core/index.html', 'Core : objets PDF et écriture', 'Packages', body)

    def home(self) -> None:
        body = f'''<section class="hero"><div class="hero-copy"><p class="eyebrow">PHP 8.3+ 64 bits · PDF 1.7 et 2.0</p><h1>Le format PDF.<br>Objet par objet.</h1><p class="hero-description">Comprendre les structures, composer les objets, maîtriser les octets. Une documentation pour explorer le format et construire vos propres fichiers PDF.</p><div class="pdf-actions"><a class="button" href="{e(self.url('tutorials/01-premier-document.html'))}">Créer mon premier PDF →</a><a class="button secondary" href="{e(self.url('reference/index.html'))}">Explorer les composants</a></div></div><div class="hero-visual" aria-label="Du catalogue à la page"><div class="graph-card"><span class="badge">01 / point d’entrée</span><code>DocumentCatalog</code></div><div class="graph-connector" aria-hidden="true">↓</div><div class="graph-card"><span class="badge">02 / arbre du document</span><code>PageTreeNode</code></div><div class="graph-connector" aria-hidden="true">↓</div><div class="graph-card"><span class="badge">03 / contenu & ressources</span><code>PageObject</code><span class="graph-leaves">StreamObject · ResourceDictionary</span></div></div></section>
<div class="stats"><div class="stat"><strong>{number(len(self.components))}</strong><span>composants documentés</span></div><div class="stat"><strong>{self.metadata['dictionary_table_count'] + self.adobe_metadata['dictionary_tables'] + len(self.iso2_tables)}</strong><span>dictionnaires ISO et Adobe</span></div><div class="stat"><strong>{len(self.examples)}</strong><span>exemples PDF à explorer</span></div><div class="stat"><strong>{self.metadata['operator_count']}</strong><span>tokens d’opérateurs PDF</span></div></div>
<section><p class="eyebrow">Apprendre avec les objets</p><h2>Construire un document et explorer ses pages</h2><p>Chaque tutoriel relie les explications aux objets PHP et au PDF créé ou lu. Consultez ses pages, le script et le résultat de son exécution.</p>{self.tutorial_cards()}</section>
<section><h2>Un core PDF, des modules au choix</h2><p>Le core représente les objets et les mécanismes de la norme Adobe. Les modules de lecture PDF et de conversion d’images ou de fontes dépendent du core. Le modèle OpenType est indépendant et s’installe sans aucun package PDF.</p><p><a href="{e(self.url('guides/modules.html'))}">Choisir les packages et comprendre leur frontière →</a></p>{self.package_cards()}</section>
<section><h2>Trois chemins pour explorer le projet</h2><div class="cards"><a class="card" href="{e(self.url('guides/composants.html'))}"><div class="card-body"><h3>Comprendre les responsabilités</h3><p>Valeurs, graphes, ressources, fonctions et écriture : comment les familles se composent.</p></div></a><a class="card" href="{e(self.url('reference/index.html'))}"><div class="card-body"><h3>Consulter la référence</h3><p>Les signatures et l’héritage de chaque composant, avec les sources et les tableaux de la norme.</p></div></a><a class="card" href="{e(self.url('recipes/table.html'))}"><div class="card-body"><h3>Assembler un exemple pratique</h3><p>Un tableau explicite : cellules, couleurs, grille et positionnement du texte.</p></div></a></div></section>
<aside class="callout"><strong>Core {e(self.release)} · Modules {e(self.module_versions)}.</strong> Les signatures, exemples et guides des modules proviennent de ces versions publiées, fixées à leurs commits exacts. La couverture et les traitements restant à implémenter sont détaillés dans <a href="{e(self.url('guides/couverture.html'))}">la couverture de la norme</a>.</aside>'''
        self.page('index.html', 'Le format PDF, objet par objet', 'Accueil', body)

    def spec_entries(self, table: str, seen: set[str] | None = None) -> list[dict]:
        seen = set() if seen is None else seen
        if table in seen:
            raise ValueError('Cyclic common specification tables')
        seen.add(table)
        entries = {}
        for common in self.table_classes[table]['common_tables']:
            for entry in self.spec_entries(common, seen.copy()):
                entries[entry['name']] = entry
        record = self.tables[table]
        for entry in [*record['entries'], *record['variable_entries']]:
            entries[entry['name']] = dict(entry, table=table, section=record['section'])
        return list(entries.values())

    def spec_panel(self, component: dict) -> str:
        iso2_spec = self.iso2_spec_by_name.get(component['name'])
        if iso2_spec is not None:
            return self.iso2_spec_panel(*iso2_spec)
        if component['source'].startswith('src/Specification/Iso32000_2/') and any(item['name'] == 'TABLE' for item in component['constants']):
            raise ValueError('Missing edition-specific catalogue provenance: ' + component['name'])
        adobe_spec = self.adobe_spec_by_name.get(component['name'])
        if adobe_spec is None:
            for constant in component['constants']:
                if constant['name'] == 'TABLE' and constant['value'].strip("'\"") in self.adobe_tables:
                    adobe_spec = (constant['value'].strip("'\""), None)
                    break
        if adobe_spec is not None:
            return self.adobe_spec_panel(*adobe_spec)
        spec = self.spec_by_name.get(component['name'])
        if spec is None:
            for constant in component['constants']:
                if constant['name'] == 'TABLE':
                    table = constant['value'].strip("'\"")
                    if table in self.tables:
                        spec = (table, None)
                    break
        if spec is None:
            return ''
        table, key = spec
        record = self.tables[table]
        entries = self.spec_entries(table)
        if key is not None:
            entries = [entry for entry in entries if entry['name'] == key]
        page = entries[0]['pdf_page'] if key is not None and entries else record['pdf_pages'][0]
        norm = self.url('downloads/iso-32000-1.pdf')
        html = f'<section id="norme"><h2>Définition dans la norme</h2><p><strong>Tableau {e(table)}</strong> · {e(record["title"])}<br>ISO 32000-1:2008, §{e(record["section"])} · <a href="{e(norm)}#page={page}">page PDF {page} ↗</a></p>'
        if key is not None:
            for entry in entries:
                constraints = []
                if entry['indirect']:
                    constraints.append('Référence indirecte exigée')
                if entry['direct']:
                    constraints.append('Objet direct exigé')
                if entry['array_elements_direct']:
                    constraints.append('Éléments directs dans le tableau')
                if entry['fixed_name']:
                    constraints.append('Nom fixe /' + entry['fixed_name'])
                html += f'<p><span class="badge">/{e(entry["name"])}</span> <span class="badge">{e(entry["type"])}</span></p><p lang="en">{e(entry["description"])}</p><p><strong>Qualificateur :</strong> {e(entry["qualifier"] or "Non précisé")}</p>'
                if constraints:
                    html += '<ul>' + ''.join(f'<li>{e(value)}</li>' for value in constraints) + '</ul>'
        else:
            html += '<div class="table-scroll"><table><thead><tr><th>Entrée</th><th>Type PDF</th><th>Exigence de la source</th><th>Tableau</th></tr></thead><tbody>'
            for entry in entries:
                name = self.entry_classes.get((entry['table'], entry['name']))
                label = '/' + entry['name']
                link = f'<a href="{e(self.url(self.routes[name]))}"><code>{e(label)}</code></a>' if name in self.routes else e(label)
                html += f'<tr><td>{link}</td><td>{e(entry["type"])}</td><td>{e(entry["qualifier"] or "Non précisé")}</td><td>{e(entry["table"])}</td></tr>'
            html += '</tbody></table></div>'
        for correction in self.corrections:
            if correction['table'] == table and (key is None or correction['entry'] == key):
                evidence = self.rewrite_link('README.md', correction['evidence_url'], owner=CORE_PACKAGE)
                html += f'<aside class="callout"><strong>Correction d’implémentation /{e(correction["entry"])}.</strong><p>{e(correction["rationale"])}</p><a href="{e(evidence)}">{e(correction["evidence_locator"])}</a></aside>'
        html += f'<p class="search-hint">Les descriptions conditionnelles restent traçables. La présence d’une définition ne réalise pas à elle seule un codec, une signature ou tous les traitements du format. <a href="{e(self.url("guides/couverture.html"))}">Lire la couverture.</a></p></section>'
        return html

    def iso2_spec_panel(self, table: str, key: str | None) -> str:
        record = self.iso2_tables[table]
        entries = [entry for entry in [*record['entries'], *record.get('variable_entries', [])] if key is None or entry['name'] == key]
        page = entries[0]['pdf_page'] if key is not None and entries else record['pdf_pages'][0]
        source = self.source_url('resources/iso32000-2-2020/metadata.json')
        original = self.source_url(self.iso2_metadata['source']['path']) + f'#page={page}'
        errata = self.iso2_metadata['official_references']['public_errata']
        html = f'<section id="norme" data-specification-edition="iso32000-2:2020" data-specification-table="{e(table)}"><h2>Définition ISO 32000-2:2020 EC3</h2><p><strong>Tableau {e(table)}</strong> · {e(record["title"])}<br>§{e(record["section"])} · page PDF {page}</p>'
        html += f'<p><a href="{e(original)}">Original PDF au commit documenté ↗</a> · <a href="{e(source)}">Métadonnées de la source au commit documenté ↗</a> · <a href="{e(errata)}">Errata publics ↗</a></p><p>Original conservé dans le dépôt du core. Inventaire des tableaux et contrôles sémantiques restent distincts.</p>'
        common = self.iso2_classes.get(table, {}).get('common_tables', [])
        if common:
            html += '<p>Définitions communes : ' + ' · '.join(f'<a href="{e(self.url(self.routes[self.iso2_classes[identifier]["class"]]))}">Table {e(identifier)}</a>' for identifier in common) + '</p>'
        if key is not None:
            for entry in entries:
                normative = entry.get('description_origin') == 'normative-source'
                summary, summary_language = (entry['description'], 'en') if normative else iso2_description(entry['description'], self.language)
                if normative:
                    html += '<p class="search-hint">Extrait normatif original en anglais.</p>'
                html += f'<p><span class="badge">/{e(entry["name"])}</span> <span class="badge">{e(entry["type"])}</span></p><p lang="{summary_language}">{e(summary)}</p>'
                constraints = []
                if entry['indirect']:
                    constraints.append('Référence indirecte exigée')
                if entry['direct']:
                    constraints.append('Objet direct exigé')
                if entry['fixed_name']:
                    constraints.append('Nom fixe /' + entry['fixed_name'])
                if entry.get('allowed_names'):
                    constraints.append('Noms permis : ' + ', '.join('/' + name for name in entry['allowed_names']))
                if entry.get('array_length') is not None:
                    constraints.append('Longueur exacte du tableau : ' + str(entry['array_length']))
                if entry.get('array_elements_direct'):
                    constraints.append('Éléments directs dans le tableau')
                if entry.get('array_elements_indirect'):
                    constraints.append('Éléments indirects dans le tableau')
                if entry.get('variable') or entry in record.get('variable_entries', []):
                    constraints.append('Clé fournie explicitement')
                if constraints:
                    html += '<ul>' + ''.join(f'<li>{e(item)}</li>' for item in constraints) + '</ul>'
        else:
            html += '<div class="table-scroll"><table><thead><tr><th>Entrée</th><th>Type PDF</th><th>Page PDF physique</th><th>Exigence</th></tr></thead><tbody>'
            for entry in entries:
                name = self.iso2_entry_classes[(table, entry['name'])]
                label = '/' + entry['name']
                link = f'<a href="{e(self.url(self.routes[name]))}"><code>{e(label)}</code></a>' if name in self.routes else e(label)
                requirement = 'Requis' if entry['required'] else 'Facultatif'
                if entry['conditional']:
                    requirement += '; conditionnel'
                html += f'<tr><td>{link}</td><td>{e(entry["type"])}</td><td>{entry["pdf_page"]}</td><td>{e(requirement)}</td></tr>'
            html += '</tbody></table></div>'
        for entry in entries:
            correction = entry.get('errata')
            if correction:
                authority = 'ISO TC 171 SC 2 WG 8' if correction['review_status'] == 'Completed' else 'PDF Association PDF Technical Working Group'
                issue = correction.get('issue_number')
                link = f' · <a href="https://github.com/pdf-association/pdf-issues/issues/{issue}">Issue #{issue}</a>' if issue else ''
                html += f'<p><strong>Correction EC3 /{e(entry["name"])}</strong> · {e(correction["review_status"])} · {e(authority)} · page PDF {correction["pdf_page"]}{link}</p>'
        html += f'<p class="search-hint"><a href="{e(self.url("guides/pdf-2-0.html"))}">Périmètre et limites PDF 2.0.</a></p></section>'
        return html

    def adobe_spec_entries(self, table: str, seen: set | None = None) -> list[dict]:
        seen = set() if seen is None else seen
        if table in seen:
            raise ValueError('Cyclic Adobe specification tables')
        seen.add(table)
        entries = {}
        for common in self.adobe_classes[table]['iso_base_tables']:
            for entry in self.spec_entries(common):
                entries[entry['name']] = dict(entry, document='PDF32000_2008.pdf')
        for common in self.adobe_classes[table]['adobe_base_tables']:
            for entry in self.adobe_spec_entries(common, seen.copy()):
                entries[entry['name']] = entry
        record = self.adobe_tables[table]
        for entry in [*record['entries'], *record.get('variable_entries', [])]:
            entries[entry['name']] = dict(entry, table=table, section=record['section'], document='adobe_supplement_iso32000.pdf')
        return list(entries.values())

    def adobe_spec_panel(self, table: str, key: str | None) -> str:
        record = self.adobe_tables[table]
        url = self.url('downloads/adobe-supplement-iso32000.pdf')
        entries = self.adobe_spec_entries(table)
        if key is not None:
            entries = [entry for entry in entries if entry['name'] == key]
        page = record['pdf_pages'][0]
        source = url
        source_table = table
        source_record = record
        heading = 'Définition dans le supplément Adobe'
        standard = 'PDF 1.7 · Adobe ExtensionLevel 3'
        if key is not None and entries:
            entry = entries[0]
            page = entry['pdf_page']
            source_table = entry['table']
            if entry['document'] == 'adobe_supplement_iso32000.pdf':
                source_record = self.adobe_tables[source_table]
            else:
                source = self.url('downloads/iso-32000-1.pdf')
                source_record = self.tables[source_table]
                heading = 'Définition dans la norme ISO'
                standard = 'ISO 32000-1:2008'
        html = f'<section id="norme"><h2>{heading}</h2><p><strong>Tableau {e(source_table)}</strong> · {e(source_record["title"])}<br>{standard} · §{e(source_record["section"])} · <a href="{e(source)}#page={page}">page PDF {page} ↗</a></p>'
        if key is not None:
            for entry in entries:
                html += f'<p><span class="badge">/{e(entry["name"])}</span> <span class="badge">{e(entry["type"])}</span></p><p lang="en">{e(entry["description"])}</p><p><strong>Qualificateur :</strong> {e(entry["qualifier"] or "Non précisé")}</p>'
        else:
            html += '<div class="table-scroll"><table><thead><tr><th>Entrée</th><th>Type PDF</th><th>Exigence</th><th>Source</th></tr></thead><tbody>'
            for entry in entries:
                adobe = entry['document'] == 'adobe_supplement_iso32000.pdf'
                classes = self.adobe_entry_classes if adobe else self.entry_classes
                name = classes.get((entry['table'], entry['name']))
                label = '/' + entry['name']
                link = f'<a href="{e(self.url(self.routes[name]))}"><code>{e(label)}</code></a>' if name in self.routes else e(label)
                source = url if adobe else self.url('downloads/iso-32000-1.pdf')
                title = 'Adobe' if adobe else 'ISO'
                html += f'<tr><td>{link}</td><td>{e(entry["type"])}</td><td>{e(entry["qualifier"] or "Non précisé")}</td><td><a href="{e(source)}#page={entry["pdf_page"]}">{title} · {e(entry["table"])} · p.{entry["pdf_page"]}</a></td></tr>'
            html += '</tbody></table></div>'
        for correction in self.adobe_corrections:
            if correction['table'] == table and (key is None or correction['entry'] == key):
                evidence = self.rewrite_link('README.md', correction['evidence_url'], owner=CORE_PACKAGE)
                html += f'<aside class="callout"><strong>Correction /{e(correction["entry"])}.</strong><p>{e(correction["rationale"])}</p><a href="{e(evidence)}">{e(correction["evidence_locator"])}</a></aside>'
        html += f'<p>Chaque entrée conserve sa source ISO ou Adobe. Les règles et traitements associés figurent dans <a href="{e(self.url("guides/supplement-adobe.html"))}">la couverture du supplément</a>.</p></section>'
        return html

    def method_html(self, method: dict, component: dict) -> str:
        parameters = []
        for parameter in method['parameters']:
            text = (self.link_type(parameter['type']) + ' ') if parameter['type'] else ''
            text += ('&amp;' if parameter['byReference'] else '') + ('...' if parameter['variadic'] else '') + '$' + e(parameter['name'])
            if parameter['default'] is not None:
                text += ' = ' + self.link_type(parameter['default'])
            parameters.append(text)
        modifiers = method['visibility'] + (' static' if method['static'] else '') + (' abstract' if method['abstract'] else '') + (' final' if method['final'] else '')
        signature = e(modifiers) + ' function ' + e(method['name']) + '(' + ', '.join(parameters) + ')'
        if method['returnType']:
            signature += ': ' + self.link_type(method['returnType'])
        owner = self.by_name.get(method['declaringClass'], component)
        source = self.source_url(method.get('source') or owner['source'], method['line'], method if 'package' in method else owner)
        description = f'<pre class="member-doc" lang="en">{e(method["description"])}</pre>' if method['description'] else ''
        return f'<section class="member" id="method-{e(method["name"])}"><h3>{e(method["name"])}()</h3><div class="api-signature"><code>{signature}</code></div>{description}<p class="member-meta">Déclarée par {self.link_type(method["declaringClass"])} · <a href="{e(source)}">Voir le code ↗</a></p></section>'

    def api_pages(self) -> None:
        labels = dict(GROUPS)
        records = []
        for item in self.components:
            name = item['name']
            group = group_for(item)
            spec = self.iso2_spec_by_name.get(name) or self.adobe_spec_by_name.get(name) or self.spec_by_name.get(name)
            search_extra = (' /' + spec[1] + ' tableau ' + spec[0]) if spec and spec[1] else ''
            records.append({'title': name, 'shortName': item['shortName'], 'namespace': item['namespace'], 'kind': item['kind'], 'url': route_for(self.routes[name], self.language), 'description': item['description'].split('\n')[0][:240] + search_extra, 'group': translate(labels[group]) if self.language == 'en' else labels[group], 'package': item['package'], 'optional': item['optional'], 'sourceUrl': self.source_url(item['source'], item['line'], item)})
            if name in self.iso2_spec_by_name:
                table, key = self.iso2_spec_by_name[name]
                records[-1].update(specificationEdition='iso32000-2:2020', specificationTable=table, specificationKey=key)
            flags = [item['kind'], *[flag for flag in ['abstract', 'final', 'readonly'] if item[flag]]]
            flags.append(('Optionnel · ' if item['optional'] else 'Core · ') + item['package'] + ' ' + item['version'])
            body = f'<p class="breadcrumbs"><a href="{e(self.url("reference/index.html"))}">Référence</a> / <a href="{e(self.url("reference/groups/" + group + ".html"))}">{e(labels[group])}</a></p><p>' + ' '.join(f'<span class="badge">{e(flag)}</span>' for flag in flags) + f'</p><div class="api-signature"><code>{e(name)}</code></div>'
            if item['description']:
                body += f'<pre class="member-doc" lang="en">{e(item["description"])}</pre>'
            body += f'<p><a href="{e(self.source_url(item["source"], item["line"], item))}">Lire la déclaration source ↗</a></p>'
            if item['optional']:
                module_route = f'modules/{MODULES[item["package"]][0]}/index.html'
                body += f'<aside class="callout">Ce composant appartient à <code>{e(item["package"])}</code>, un module installé séparément du core. <a href="{e(self.url(module_route))}">Guide du module.</a> <a href="{e(self.url(self.package_route(item["package"])))}">API du package.</a></aside>'
            body += '<section id="relations"><h2>Héritage et contrats</h2>'
            relations = [('Parent', [item['parent']] if item['parent'] else []), ('Interfaces', item['interfaces']), ('Traits', item['traits'])]
            for label, values in relations:
                if values:
                    body += f'<p><strong>{e(label)} :</strong> ' + ', '.join(self.link_type(value) for value in values) + '</p>'
            if not any(values for _, values in relations):
                body += '<p>Ce type ne déclare pas de parent, d’interface ou de trait.</p>'
            children = self.children[name]
            if children:
                body += f'<details><summary>{len(children)} types dérivés directement</summary><ul>' + ''.join(f'<li>{self.link_type(child["name"])}</li>' for child in children) + '</ul></details>'
            body += '</section>' + self.spec_panel(item)
            if item['constructor']:
                body += '<section id="construction"><h2>Construction</h2>' + self.method_html(item['constructor'], item) + '</section>'
            if item['methods']:
                body += '<section id="methodes"><h2>Méthodes déclarées</h2>' + ''.join(self.method_html(method, item) for method in item['methods']) + '</section>'
            if item['inheritedMethods']:
                body += f'<section id="methodes-heritees"><h2>Méthodes héritées</h2><details><summary>{len(item["inheritedMethods"])} méthodes des parents et contrats</summary>' + ''.join(self.method_html(method, item) for method in item['inheritedMethods']) + '</details></section>'
            if item['properties']:
                body += '<section id="proprietes"><h2>Propriétés</h2><div class="table-scroll"><table><thead><tr><th>Déclaration</th><th>Provenance et documentation</th></tr></thead><tbody>'
                for prop in item['properties']:
                    signature = e(prop['visibility'] + (' static' if prop['static'] else '') + (' readonly' if prop['readonly'] else '')) + ' ' + self.link_type(prop['type']) + ' $' + e(prop['name'])
                    body += f'<tr><td><code>{signature}</code></td><td>{self.link_type(prop["declaringClass"])}<pre class="member-doc" lang="en">{e(prop["description"])}</pre></td></tr>'
                body += '</tbody></table></div></section>'
            if item['constants']:
                body += '<section id="constantes"><h2>Constantes</h2><div class="table-scroll"><table><thead><tr><th>Nom</th><th>Valeur PHP</th><th>Provenance</th></tr></thead><tbody>'
                for constant in item['constants']:
                    body += f'<tr><td><code>{e(constant["name"])}</code></td><td><pre><code>{e(constant["value"])}</code></pre></td><td>{self.link_type(constant["declaringClass"])}</td></tr>'
                body += '</tbody></table></div></section>'
            if item['cases']:
                body += '<section id="cas"><h2>Cas de l’enum</h2><ul>' + ''.join(f'<li><code>{e(case["name"])}</code>' + (f' = <code>{e(json.dumps(case["value"], ensure_ascii=False))}</code>' if case['value'] is not None else '') + '</li>' for case in item['cases']) + '</ul></section>'
            toc = [{'id': key, 'name': label, 'level': 2} for key, label in [('relations', 'Héritage'), ('norme', 'Norme'), ('construction', 'Construction'), ('methodes', 'Méthodes'), ('methodes-heritees', 'Méthodes héritées'), ('proprietes', 'Propriétés'), ('constantes', 'Constantes'), ('cas', 'Cas de l’enum')] if f'id="{key}"' in body]
            self.page(self.routes[name], item['shortName'], labels[group], body, toc)
        index_file = 'search-index.json' if self.language == 'en' else 'search-index.fr.json'
        (self.output / 'assets' / index_file).write_text(json.dumps(records, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
        for name, package in self.packages.items():
            items = [item for item in self.components if item['package'] == name]
            package_body = f'<p><code>{e(name)}</code> · version <a href="{e(package["repository"] + "/releases/tag/v" + package["version"])}">{e(package["version"])}</a> · <a href="{e(package["repository"] + "/commit/" + package["revision"])}">source {e(package["revision"][:7])}</a></p>'
            package_body += f'<p>{self.packagist_link(name)}</p>'
            guide = 'modules/core/index.html' if name == CORE_PACKAGE else f'modules/{MODULES[name][0]}/index.html'
            package_body += f'<p><a href="{e(self.url(guide))}">Lire le guide du package →</a></p>' + self.component_cards(items)
            self.page(self.package_route(name), 'API de ' + name, 'Référence par package', package_body)
        body = '<p>Chaque classe, interface, enum et trait du core et des modules installés pour cette documentation possède une fiche. Les composants optionnels portent leur nom de package ; les installer dépend des traitements nécessaires à votre application. Les signatures sont extraites par Reflection ; les descriptions normalisées proviennent du catalogue de la référence PDF.</p>' + self.search() + '<h2>Explorer par package</h2>' + self.package_cards()
        body += '<div id="component-list"><h2>Explorer par famille</h2><div class="cards">'
        for group, label in GROUPS:
            items = self.groups[group]
            if items:
                body += f'<a class="card" href="{e(self.url("reference/groups/" + group + ".html"))}"><div class="card-body"><span class="eyebrow">{len(items)} composants</span><h3>{e(label)}</h3><span class="card-link">Consulter la famille →</span></div></a>'
                group_body = '<p>Les composants de cette famille sont tous accessibles ci-dessous. La recherche globale permet aussi de retrouver une entrée PDF ou un nom de type.</p>' + self.component_cards(items)
                self.page('reference/groups/' + group + '.html', label, 'Référence', group_body)
        body += '</div><h2>Repères pour commencer</h2>'
        featured_names = ['PDF\\FileStructure', 'PDF\\Syntax\\Object\\NameType', 'PDF\\Syntax\\Object\\DictionaryType', 'PDF\\Syntax\\Object\\StreamObject', 'PDF\\Syntax\\DocumentStructure\\DocumentCatalog', 'PDF\\Syntax\\DocumentStructure\\PageTree\\PageObject', 'PDF\\Syntax\\ContentStreamsResources\\ContentStreams', 'PDF\\Serialization\\SerializationContext']
        body += self.component_cards([self.by_name[name] for name in featured_names]) + '</div>'
        self.page('reference/index.html', 'Tous les composants', 'Référence API', body)

    def build(self) -> None:
        for root in (self.content_root, *self.package_roots.values()):
            if self.output == root or root in self.output.parents and self.output.relative_to(root).parts[0] in {'src', 'docs', 'examples', 'tools', 'resources', 'vendor'}:
                raise ValueError('Build output must be separate from source directories')
        self.output.mkdir(parents=True, exist_ok=True)
        for asset in ['site.css', 'site.js']:
            target = self.output / 'assets' / asset
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.content_root / 'docs' / 'site' / 'assets' / asset, target)
        previews = self.output / 'assets' / 'previews'
        previews.mkdir(parents=True, exist_ok=True)
        for image in (self.content_root / 'docs' / 'tutorials' / 'previews').glob('*.png'):
            shutil.copyfile(image, previews / image.name)
        downloads = self.output / 'downloads'
        downloads.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(self.root / self.metadata['source_path'], downloads / 'iso-32000-1.pdf')
        shutil.copyfile(self.root / self.adobe_metadata['path'], downloads / 'adobe-supplement-iso32000.pdf')
        archival_downloads = downloads / 'adobe-references'
        archival_downloads.mkdir(exist_ok=True)
        for filename, original in self.reference_sources.items():
            shutil.copyfile(self.root / original['path'], archival_downloads / filename)
        examples = self.output / 'examples'
        examples.mkdir(parents=True, exist_ok=True)
        expected = set(self.examples)
        actual = {path.stem for path in (self.root / 'examples').glob('*.php')}
        core_examples = expected - set(EXTERNAL_EXAMPLES)
        if actual != core_examples:
            raise ValueError('Every writer example needs a documented site page: ' + str(actual ^ core_examples))
        for example in sorted(expected):
            record = self.example_sources[example]
            source_pdf = self.pdfs / (example + '.pdf')
            if not source_pdf.is_file() or not source_pdf.read_bytes().startswith(b'%PDF-'):
                raise ValueError('Generate the example PDF first: ' + example)
            shutil.copyfile(source_pdf, examples / source_pdf.name)
            if not record['path'].is_file():
                raise ValueError('Missing example source in its package: ' + example)
            shutil.copyfile(record['path'], examples / (example + '.php.txt'))
            record['sourceSha256'] = hashlib.sha256(record['path'].read_bytes()).hexdigest()
            record['pdfSha256'] = hashlib.sha256(source_pdf.read_bytes()).hexdigest()
            if record['kind'] in {'input', 'conversion'}:
                if not record['inputPath'].is_file() or source_pdf.read_bytes() != record['inputPath'].read_bytes():
                    raise ValueError('The reader example PDF must preserve its original input: ' + example)
                console_path = self.pdfs / (example + '.txt')
                if not console_path.is_file() or not console_path.read_text(encoding='utf-8').strip():
                    raise ValueError('Run the reader example and retain its console result first: ' + example)
                shutil.copyfile(console_path, examples / console_path.name)
                record['console'] = f'examples/{example}.txt'
                record['consoleSha256'] = hashlib.sha256(console_path.read_bytes()).hexdigest()
            if record['kind'] == 'conversion':
                html_path = self.pdfs / (example + '.html')
                if not html_path.is_file():
                    raise ValueError('Run the PDF-to-HTML conversion first: ' + example)
                shutil.copyfile(html_path, examples / html_path.name)
                record['html'] = f'examples/{example}.html'
                record['htmlSha256'] = hashlib.sha256(html_path.read_bytes()).hexdigest()
                record['assets'] = publish_derivation_assets(console_path, html_path, examples)
                css_path = self.pdfs / (example + '.css')
                if css_path.is_file():
                    shutil.copyfile(css_path, examples / css_path.name)
                    record['css'] = f'examples/{example}.css'
                    record['cssSha256'] = hashlib.sha256(css_path.read_bytes()).hexdigest()
            images = {}
            for image in self.pdf_previews.glob(example + '-*.png'):
                match = re.fullmatch(re.escape(example) + r'-(\d+)\.png', image.name)
                if not match:
                    raise ValueError('Unexpected PDF preview filename: ' + image.name)
                number = int(match.group(1))
                if number < 1 or number in images:
                    raise ValueError('Duplicate or invalid PDF preview page: ' + image.name)
                images[number] = image
            if not images or sorted(images) != list(range(1, len(images) + 1)):
                raise ValueError('Render every PDF page in sequence first: ' + example)
            if record['kind'] == 'input' and len(images) != record['expectedPages']:
                raise ValueError('Render every page of the external input PDF: ' + example)
            self.pdf_pages[example] = []
            for number, image in sorted(images.items()):
                with image.open('rb') as stream:
                    header = stream.read(24)
                if len(header) != 24 or header[:8] != b'\x89PNG\r\n\x1a\n' or header[12:16] != b'IHDR':
                    raise ValueError('Invalid PDF page PNG: ' + image.name)
                width, height = int.from_bytes(header[16:20], 'big'), int.from_bytes(header[20:24], 'big')
                if not width or not height:
                    raise ValueError('Empty PDF page PNG: ' + image.name)
                filename = f'{example}-{number}.png'
                target = self.output / 'assets' / 'pdf-pages' / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(image, target)
                self.pdf_pages[example].append({'file': filename, 'width': width, 'height': height})
        self.write('assets/favicon.svg', '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="#0a7166"/><path d="M9 7h10l5 5v13H9z" fill="none" stroke="white" stroke-width="2"/><path d="M19 7v6h5" fill="none" stroke="white" stroke-width="2"/></svg>')
        self.prepare_anchors()
        for language in LANGUAGES:
            self.language = language
            self.build_language_pages()
        self.build_aliases()
        (self.output / '.nojekyll').write_text('')
        packages = [dict(package, components=sum(item['package'] == name for item in self.components)) for name, package in self.packages.items()]
        sources = {example: {key: value for key, value in record.items() if key not in {'path', 'inputPath'}} for example, record in self.example_sources.items()}
        for record in sources.values():
            record['pages'] = {language: route_for(record['page'], language) for language in LANGUAGES}
        manifest = {'basePath': self.base, 'revision': self.revision, 'docsRevision': self.docs_revision, 'documentation': self.documentation, 'documentationSources': self.documentation_sources, 'packages': packages, 'components': len(self.components), 'examples': sorted(expected), 'exampleSources': sources, 'pdfPages': {example: ['assets/pdf-pages/' + image['file'] for image in images] for example, images in self.pdf_pages.items()}, 'pages': sorted(route for route in self.written if route.endswith('.html'))}
        manifest['derivedHtml'] = [{'example': name, 'path': record['html'], 'sha256': record['htmlSha256'], 'package': record['package'], 'revision': self.packages[record['package']]['revision']} for name, record in sources.items() if record['kind'] == 'conversion']
        html_package = self.packages['pdftoolkit/pdf-to-html']
        manifest['htmlDerivationReference'] = {**self.html_reference, 'repository': html_package['repository'], 'revision': html_package['revision'], 'sourceUrl': self.source_url(self.html_reference['source'], owner=html_package), 'metadataUrl': self.source_url('resources/reference.json', owner=html_package)}
        manifest.update(defaultLanguage='en', languages=list(LANGUAGES), translations=self.translations, aliases=self.aliases, searchIndexes={'en': 'assets/search-index.json', 'fr': 'assets/search-index.fr.json'})
        manifest['specificationSources'] = [
            {'source': 'PDF32000_2008.pdf', 'download': 'downloads/iso-32000-1.pdf', 'sha256': self.metadata['sha256'], 'pdfPages': self.metadata['pdf_pages']},
            {'source': self.adobe_metadata['document'], 'download': 'downloads/adobe-supplement-iso32000.pdf', 'sha256': self.adobe_metadata['document_sha256'], 'pdfPages': self.adobe_metadata['pdf_pages']},
        ]
        original = self.iso2_metadata['source']
        source_file = self.root / original['path']
        if not original['public_copy_included'] or not source_file.is_file() or hashlib.sha256(source_file.read_bytes()).hexdigest() != original['sha256']:
            raise ValueError('The public ISO 32000-2 reference must preserve its supplied original bytes')
        manifest['repositorySpecificationSources'] = [{
            'source': original['document'], 'standard': self.iso2_metadata['standard'],
            'editionIdentifier': self.iso2_metadata['edition_identifier'],
            'specifiedPdfVersion': self.iso2_metadata['specified_pdf_version'],
            'errataCollection': self.iso2_metadata['errata_collection'],
            'sha256': original['sha256'], 'pdfPages': original['physical_pdf_pages'],
            'bytes': source_file.stat().st_size,
            'repository': self.packages[CORE_PACKAGE]['repository'],
            'revision': self.revision,
            'sourceUrl': self.source_url(original['path']),
            'publicCopyIncluded': original['public_copy_included'],
            'provider': original['provider'], 'providerUrl': original['provider_url'],
            'catalogueSourceUrl': self.source_url('resources/iso32000-2-2020/metadata.json'),
            'dictionaryTables': len(self.iso2_tables),
            'entryClasses': sum(len(item['entries']) for item in self.iso2_classes.values()),
            'completeCatalogue': self.iso2_metadata.get('dictionary_catalogue', {}).get('status') == 'complete-base-table-inventory-with-explicit-reviewed-overrides',
            'completeConformance': False,
            'dictionaryTableIdentifiers': list(self.iso2_tables),
            'variableEntryClasses': sum(len(item.get('variable_entries', [])) for item in self.iso2_tables.values()),
        }]
        manifest['referenceSources'] = [
            {'source': item['document'], 'role': item['role'], 'download': 'downloads/adobe-references/' + item['document'], 'sha256': item['document_sha256'], 'bytes': item['bytes'], 'pdfPages': item['pdf_pages']}
            for item in self.reference_sources.values()
        ]
        manifest['bundleSpecificationSources'] = [{
            'source': item['filename'], 'identifier': item['identifier'], 'title': item['title'],
            'sha256': item['sha256'], 'bytes': item['bytes'], 'pdfPages': item['physical_pdf_pages'],
            'provider': item['provider'], 'providerUrl': item['provider_url'],
            'repository': self.packages[CORE_PACKAGE]['repository'], 'revision': self.revision,
            'sourceUrl': self.source_url(item['path']),
            'catalogueSourceUrl': self.source_url('resources/iso32000-2-bundle/sources.json'),
        } for item in self.bundle_sources]
        manifest['staticAssets'] = [{'path': path.relative_to(self.output).as_posix(), 'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()} for path in sorted(self.output.rglob('*')) if path.is_file() and path.suffix != '.html' and path.name not in {'site-manifest.json', '.nojekyll'}]
        (self.output / 'site-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(f'Built {len(manifest["pages"])} pages, {len(self.components)} API components and {len(expected)} PDF examples into {self.output}')

    def build_language_pages(self) -> None:
        self.home()
        self.core_hub()
        for owner, original, route, title, category in self.pages:
            source = localized_source(owner, original, self.language)
            body, toc = self.render_markdown(owner, source)
            package = self.documentation if owner == 'documentation' else self.packages[owner]
            root = self.content_root if owner == 'documentation' else self.package_roots[owner]
            source_url = self.source_url(source, owner=package)
            self.documentation_sources.append({'page': route_for(route, self.language), 'language': self.language, 'package': owner, 'source': source, 'repository': package['repository'], 'revision': package['revision'], 'sourceUrl': source_url, 'sourceSha256': hashlib.sha256((root / source).read_bytes()).hexdigest()})
            if owner in MODULES:
                body = f'<p><span class="badge">Module optionnel · {e(owner)} {e(package["version"])}</span></p>' + self.module_navigation(owner) + body
                if route == f'modules/{MODULES[owner][0]}/index.html':
                    body = f'<p>{self.packagist_link(owner)}</p>' + body
            if route == 'tutorials/index.html':
                body = self.tutorial_cards() + body
            example = next((name for name, target in self.examples.items() if target == route), None)
            if example:
                body += self.example_panel(example)
                if example in EXTERNAL_EXAMPLES:
                    toc += [{'id': 'resultat-pdf', 'name': 'PDF d’entrée', 'level': 2}, {'id': 'resultat-lecture', 'name': 'Résultat de la lecture', 'level': 2}]
                    if self.example_sources[example]['kind'] == 'conversion':
                        toc += [{'id': 'resultat-html', 'name': 'Résultat HTML', 'level': 2}]
                else:
                    toc += [{'id': 'resultat-pdf', 'name': 'Résultat PDF', 'level': 2}]
                toc += [{'id': 'code-source', 'name': 'Code source', 'level': 2}]
            body += f'<p class="search-hint"><a href="{e(source_url)}">Source de ce guide au commit documenté ↗</a></p>'
            self.page(route, title, category, body, toc)
        self.api_pages()
        self.page('404.html', 'Page introuvable', 'Documentation', f'<p>Cette adresse ne correspond pas à une page publiée.</p><p><a href="{e(self.url("reference/index.html"))}">Rechercher un composant</a> ou <a href="{e(self.url("index.html"))}">revenir à l’accueil</a>.</p>')

    def build_aliases(self) -> None:
        """Old French root addresses continue to their French equivalents."""
        canonical_pages = {page for translations in self.translations.values() for page in translations.values()}
        self.aliases = {logical: variants['fr'] for logical, variants in self.translations.items() if logical not in canonical_pages}
        for route, destination in self.aliases.items():
            url = self.base + destination
            html = f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Documentation PDFToolkit</title><link rel="canonical" href="{e(SITE_ORIGIN + url)}">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; base-uri 'none'; form-action 'none'">
<script defer src="{e(self.base + 'assets/site.js?v=' + self.script_revision)}"></script></head>
<body><main data-root="{e(self.base)}" data-redirect-to="{e(url)}"><h1>Documentation PDFToolkit</h1><p>Cette page est disponible en français et en anglais.</p><a id="destination" href="{e(url)}">Continuer en français</a></main></body></html>'''
            path = self.output / route
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(html, encoding='utf-8', newline='\n')
            self.written.append(route)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--content-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--opentype-root', type=Path, required=True, help='Independent released OpenType checkout')
    parser.add_argument('--pdf-to-html-root', type=Path, required=True, help='Released PDF-to-HTML checkout and its locked reader')
    parser.add_argument('--sources', type=Path, help='Released-source manifest; defaults to content-root/resources/sources.json')
    parser.add_argument('--api', type=Path, required=True)
    parser.add_argument('--pdf-dir', type=Path, required=True)
    parser.add_argument('--pdf-preview-dir', type=Path, required=True, help='PNG pages rendered with pdftoppm: <example>-1.png, <example>-2.png, ...')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--base-path', default='/')
    parser.add_argument('--docs-revision', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}', args.docs_revision):
        parser.error('docs-revision must be an exact commit SHA')
    if not re.fullmatch(r'(?:/[A-Za-z0-9_.-]+)*/?', args.base_path):
        parser.error('base-path must contain only URL path segments')
    content_root = args.content_root.resolve()
    sources = args.sources.resolve() if args.sources else content_root / 'resources' / 'sources.json'
    Site(content_root, args.source_root.resolve(), args.output.resolve(), args.api.resolve(), args.pdf_dir.resolve(), args.pdf_preview_dir.resolve(), args.base_path, args.docs_revision, sources, args.opentype_root.resolve(), args.pdf_to_html_root.resolve()).build()
