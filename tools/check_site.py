"""Check all generated documentation links, API coverage and PDF downloads."""

import argparse
import hashlib
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
import struct
from urllib.parse import quote, unquote, urlsplit


DOCUMENTATION_REPOSITORY = 'https://github.com/PDFToolkit/pdftoolkit.github.io'
SITE_ORIGIN = 'https://pdftoolkit.github.io'
MODULE_GUIDES = {
    'reader': ['index', 'architecture', 'components', 'pages', 'authentication', 'source-mac', 'security', 'signalements', 'versions'],
    'images': ['index', 'architecture', 'signalements', 'versions'],
    'fonts': ['index', 'true-type-to-pdf', 'signalements', 'versions'],
    'opentype': ['index', 'architecture', 'coverage', 'substitutions', 'positioning', 'signalements', 'versions'],
    'to-html': ['index', 'architecture', 'coverage', 'authentication', 'requirements', 'policies', 'graphics', 'security', 'reference', 'signalements', 'versions'],
}


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.duplicates = set()
        self.links = []
        self.heading_count = 0
        self.canonicals = []
        self.languages = []
        self.alternates = []
        self.language_links = []
        self.current_languages = []
        self.redirect_targets = []
        self.search_indexes = []
        self.specification_panels = []
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                self.duplicates.add(attrs['id'])
            self.ids.add(attrs['id'])
        if tag == 'h1':
            self.heading_count += 1
        if tag == 'html':
            self.languages.append(attrs.get('lang'))
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs.get('href'))
        if tag == 'link' and attrs.get('rel') == 'alternate':
            self.alternates.append((attrs.get('hreflang'), attrs.get('href')))
        if tag == 'a' and 'data-language-link' in attrs:
            self.language_links.append(attrs)
        if tag == 'span' and attrs.get('aria-current') == 'true' and attrs.get('lang'):
            self.current_languages.append(attrs['lang'])
        if tag == 'main' and 'data-redirect-to' in attrs:
            self.redirect_targets.append(attrs['data-redirect-to'])
        if tag == 'section' and 'data-specification-edition' in attrs:
            self.specification_panels.append((attrs['data-specification-edition'], attrs.get('data-specification-table')))
        if 'data-search-index' in attrs:
            self.search_indexes.append(attrs['data-search-index'])
        for key in ['href', 'src']:
            if attrs.get(key):
                self.links.append(attrs[key])
        if tag in {'script', 'iframe'} and attrs.get('src', '').startswith(('https://', 'http://', '//')):
            raise ValueError('Unexpected third-party runtime resource: ' + attrs['src'])


class DerivedHtml(HTMLParser):
    """Check executable boundaries separately from the documentation interface."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.html = 0
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'html':
            self.html += 1
        if tag == 'style':
            self.in_style = True
        if tag in {'script', 'iframe', 'object', 'embed', 'base'}:
            raise ValueError('Executable or embedding element in derived HTML: ' + tag)
        for name, value in attrs:
            if name.lower().startswith('on') or name.lower() == 'srcdoc':
                raise ValueError('Event handler or embedded document in derived HTML')
            if name in {'href', 'src', 'action', 'formaction', 'xlink:href'} and value:
                normalized = re.sub(r'[\x00-\x20]', '', value)
                scheme = urlsplit(normalized).scheme.lower()
                if name in {'src', 'xlink:href'} and scheme in {'https', 'http'}:
                    raise ValueError('Remote runtime resource in derived HTML')
                if scheme not in {'', 'https', 'http', 'mailto', 'tel'} and not (tag == 'img' and name == 'src' and re.match(r'^data:image/(?:png|jpeg);base64,', normalized)):
                    raise ValueError('Unsafe URL scheme in derived HTML')
            if name == 'style' and value and re.search(r'@import|expression\s*\(|javascript\s*:|url\s*\(', value, re.I):
                raise ValueError('Active or remote inline CSS in derived HTML')
        if tag == 'meta' and attributes.get('http-equiv', '').lower() == 'refresh':
            raise ValueError('Navigation refresh in derived HTML')

    def handle_endtag(self, tag):
        if tag == 'style':
            self.in_style = False

    def handle_data(self, value):
        if self.in_style and re.search(r'@import|expression\s*\(|javascript\s*:|url\s*\(', value, re.I):
            raise ValueError('Active or remote CSS in derived HTML')


def validate_derived_html(value):
    parser = DerivedHtml()
    parser.feed(value)
    if parser.html != 1:
        raise ValueError('Derived output must contain one HTML document')


def check(root):
    root = root.resolve()
    manifest = json.loads((root / 'site-manifest.json').read_text(encoding='utf-8'))
    pages = manifest['pages']
    published_files = {path.relative_to(root).as_posix() for path in root.rglob('*') if path.is_file()}
    derived = manifest.get('derivedHtml', [])
    derived_paths = {item.get('path', '') for item in derived}
    if len(derived_paths) != len(derived) or derived_paths & set(pages):
        raise ValueError('Derived HTML must have unique paths outside documentation pages')
    for item in derived:
        path = item.get('path', '')
        if not re.fullmatch(r'examples/[a-z0-9-]+\.html', path):
            raise ValueError('Invalid derived HTML output path')
        output = root / path
        if not output.is_file() or hashlib.sha256(output.read_bytes()).hexdigest() != item.get('sha256'):
            raise ValueError('Missing or modified derived HTML output: ' + path)
        validate_derived_html(output.read_text(encoding='utf-8'))
    actual = {path for path in published_files if path.endswith('.html')} - derived_paths
    if actual != set(pages):
        raise ValueError('Stale or missing HTML pages: ' + str(actual ^ set(pages)))
    documents = {page: Document((root / page).read_text(encoding='utf-8')) for page in pages}
    errors = []
    if manifest.get('basePath') != '/':
        errors.append('Central documentation must use the root base path')
    languages = manifest.get('languages', [])
    if manifest.get('defaultLanguage') != 'en' or languages != ['en', 'fr']:
        errors.append('Documentation must default to English and publish English and French')
    translations = manifest.get('translations', {})
    aliases = manifest.get('aliases', {})
    page_languages = {}
    for logical, routes in translations.items():
        if set(routes) != {'en', 'fr'} or routes.get('fr') != 'fr/' + logical:
            errors.append('Incorrect translation pair: ' + logical)
            continue
        for language, route in routes.items():
            if route.startswith('/') or '..' in Path(route).parts or not route.endswith('.html'):
                errors.append('Invalid localized route: ' + route)
            if route in page_languages:
                errors.append('Localized page belongs to more than one translation pair: ' + route)
            page_languages[route] = language
            if route not in documents:
                errors.append('Missing localized page: ' + route)
        if routes['en'].startswith('fr/'):
            errors.append('English default route cannot use the French prefix: ' + logical)
    if set(documents) != set(page_languages) | set(aliases):
        errors.append('Translation and alias inventories must cover every HTML page exactly once')
    if set(page_languages) & set(aliases):
        errors.append('A locale page cannot also be a legacy alias')

    def localized(logical, language):
        route = translations.get(logical, {}).get(language)
        if route is None:
            errors.append(f'Missing translation route for {logical}: {language}')
        return route

    for logical, routes in translations.items():
        if set(routes) != {'en', 'fr'}:
            continue
        expected_alternates = {
            'en': SITE_ORIGIN + manifest['basePath'] + routes['en'],
            'fr': SITE_ORIGIN + manifest['basePath'] + routes['fr'],
            'x-default': SITE_ORIGIN + manifest['basePath'] + routes['en'],
        }
        for language, page in routes.items():
            document = documents.get(page)
            if document is None:
                continue
            if len(document.alternates) != 3 or dict(document.alternates) != expected_alternates:
                errors.append(f'{page}: missing, duplicate or nonreciprocal hreflang alternates')
            if document.languages != [language] or document.current_languages != [language]:
                errors.append(f'{page}: incorrect document language or selected locale')
            other = 'fr' if language == 'en' else 'en'
            if len(document.language_links) != 1:
                errors.append(f'{page}: expected one link to the other locale')
                continue
            selector = document.language_links[0]
            if selector.get('lang') != other or selector.get('hreflang') != other or selector.get('href') != manifest['basePath'] + routes[other]:
                errors.append(f'{page}: incorrect language selector target')
            try:
                anchor_map = json.loads(selector.get('data-anchor-map', ''))
            except (ValueError, TypeError):
                errors.append(f'{page}: language selector needs an explicit anchor map')
                continue
            counterpart = documents.get(routes[other])
            if not isinstance(anchor_map, dict) or counterpart is None:
                errors.append(f'{page}: invalid language selector anchor map')
                continue
            try:
                reverse_map = json.loads(counterpart.language_links[0].get('data-anchor-map', '')) if len(counterpart.language_links) == 1 else {}
            except (ValueError, TypeError):
                reverse_map = {}
            for source_anchor, target_anchor in anchor_map.items():
                if source_anchor not in document.ids or target_anchor not in counterpart.ids:
                    errors.append(f'{page}: invalid translated anchor {source_anchor} -> {target_anchor}')
                elif language == 'fr' and logical == routes['en'] and source_anchor not in counterpart.ids:
                    errors.append(f'{page}: published French section must retain its English-route alias: {source_anchor}')
                elif not isinstance(reverse_map, dict) or reverse_map.get(target_anchor) != source_anchor:
                    errors.append(f'{page}: nonreciprocal translated anchor {source_anchor} -> {target_anchor}')
    expected_aliases = {
        logical: routes['fr'] for logical, routes in translations.items()
        if set(routes) == {'en', 'fr'} and logical != routes['en']
    }
    if aliases != expected_aliases:
        errors.append('Legacy French aliases must cover exactly the renamed default routes')
    for alias, destination in aliases.items():
        document = documents.get(alias)
        if document is None or destination not in documents:
            errors.append('Missing legacy alias or French destination: ' + alias)
            continue
        if document.canonicals != [SITE_ORIGIN + manifest['basePath'] + destination]:
            errors.append(f'{alias}: legacy alias must canonicalize to its French destination')
        if manifest['basePath'] + destination not in document.links:
            errors.append(f'{alias}: legacy alias needs an accessible French destination link')
        if document.languages != ['fr']:
            errors.append(f'{alias}: legacy French alias must declare French')
        if document.redirect_targets != [manifest['basePath'] + destination] or 'destination' not in document.ids:
            errors.append(f'{alias}: legacy alias needs its exact redirect target and fallback link')
    docs_revision = manifest.get('docsRevision', '')
    if not re.fullmatch(r'[0-9a-f]{40}', docs_revision) or manifest.get('documentation') != {'repository': DOCUMENTATION_REPOSITORY, 'revision': docs_revision}:
        errors.append('Documentation needs its own exact repository and commit provenance')
    targets = {}
    for page, document in documents.items():
        if document.duplicates:
            errors.append(f'{page}: duplicate IDs {document.duplicates}')
        if page not in aliases and document.heading_count != 1:
            errors.append(f'{page}: expected one main heading, got {document.heading_count}')
        if page not in aliases and document.canonicals != [SITE_ORIGIN + manifest['basePath'] + page]:
            errors.append(f'{page}: missing or incorrect self-canonical URL')
        if page not in aliases:
            language = page_languages.get(page, 'en')
            expected_search = manifest['basePath'] + 'assets/' + ('search-index.json' if language == 'en' else 'search-index.fr.json')
            if any(target != expected_search for target in document.search_indexes):
                errors.append(f'{page}: search widget must use its own locale index')
            for slug in ['core', *MODULE_GUIDES]:
                route = localized(f'modules/{slug}/index.html', language)
                if route is not None and manifest['basePath'] + route not in document.links:
                    errors.append(f'{page}: missing localized module navigation for {slug}')
        for link in document.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            path = unquote(url.path)
            if path.startswith('/') and not path.startswith(manifest['basePath']):
                errors.append(f'{page}: URL escapes the project base path: {link}')
                continue
            context = '' if path.startswith('/') else (str(Path(page).parent) if path else page)
            key = (context, path)
            if key not in targets:
                candidate = path[len(manifest['basePath']):] if path.startswith('/') else posixpath.join(posixpath.dirname(page), path) if path else page
                candidate = posixpath.normpath(candidate)
                if candidate == '.':
                    candidate = 'index.html'
                if candidate.startswith('../') or candidate == '..' or '\\' in candidate:
                    targets[key] = None
                elif candidate in published_files:
                    targets[key] = candidate
                else:
                    directory_index = candidate.rstrip('/') + '/index.html'
                    targets[key] = directory_index if directory_index in published_files else None
            relative = targets[key]
            if relative is None:
                errors.append(f'{page}: missing target {link}')
                continue
            if url.fragment and relative in documents and unquote(url.fragment) not in documents[relative].ids:
                errors.append(f'{page}: missing anchor {link}')
    indexes = {}
    for language in ['en', 'fr']:
        index_path = root / 'assets' / ('search-index.json' if language == 'en' else 'search-index.fr.json')
        if not index_path.is_file():
            errors.append('Missing localized search index: ' + language)
            indexes[language] = []
            continue
        indexes[language] = json.loads(index_path.read_text(encoding='utf-8'))
        index = indexes[language]
        if len(index) != manifest['components'] or len({item['title'] for item in index}) != len(index):
            errors.append('Search index does not cover every unique API component: ' + language)
        if len({item['url'] for item in index}) != len(index):
            errors.append('Search index contains duplicate API targets: ' + language)
        for item in index:
            if page_languages.get(item['url']) != language:
                errors.append(f'{language}: search result targets the wrong locale: ' + item['title'])
    index = indexes['en']
    english_records = {item['title']: item for item in indexes['en']}
    french_records = {item['title']: item for item in indexes['fr']}
    translated_pairs = {(routes.get('en'), routes.get('fr')) for routes in translations.values()}
    if set(english_records) != set(french_records):
        errors.append('English and French search indexes must cover the same API identities')
    for title in english_records.keys() & french_records.keys():
        english = english_records[title]
        french = french_records[title]
        for key in ('package', 'optional', 'sourceUrl', 'specificationEdition', 'specificationTable', 'specificationKey'):
            if english.get(key) != french.get(key):
                errors.append(f'{title}: API provenance differs between locales: {key}')
        if (english['url'], french['url']) not in translated_pairs:
            errors.append('API search records must target their reciprocal translation pair: ' + title)
    packages = {item['name']: item for item in manifest['packages']}
    if len(packages) != len(manifest['packages']) or set(packages) != {'roukmoute/pdf', 'pdftoolkit/pdf-reader', 'pdftoolkit/pdf-images', 'pdftoolkit/pdf-fonts', 'pdftoolkit/opentype', 'pdftoolkit/pdf-to-html'}:
        errors.append('Package inventory must cover every unique package name')
    if packages.get('roukmoute/pdf', {}).get('revision') != manifest.get('revision'):
        errors.append('Core source revision differs from the site source revision')
    if sum(package['components'] for package in packages.values()) != len(index):
        errors.append('Package inventory does not cover every API component')
    for name, package in packages.items():
        if package['components'] != sum(item['package'] == name for item in index):
            errors.append('Incorrect API package component count: ' + name)
        if not re.fullmatch(r'[0-9a-f]{40}', package.get('revision', '')) or not re.fullmatch(r'\d+\.\d+\.\d+', package.get('version', '')):
            errors.append('Package source needs a stable version and exact commit: ' + name)
        optional = name != 'roukmoute/pdf'
        repository = 'https://github.com/PDFToolkit/' + (name.split('/')[-1] if optional else 'pdf')
        if package.get('optional') is not optional or package.get('repository') != repository:
            errors.append('Incorrect source package identity: ' + name)
        slug = ('opentype' if name == 'pdftoolkit/opentype' else name.removeprefix('pdftoolkit/pdf-')) if optional else 'core'
        package_url = 'https://packagist.org/packages/' + name
        for language in ['en', 'fr']:
            for logical in ('index.html', 'reference/index.html', f'reference/packages/{slug}.html', f'modules/{slug}/index.html', 'guides/demarrer.html', 'guides/modules.html'):
                route = localized(logical, language)
                if route not in documents or package_url not in documents[route].links:
                    errors.append(f'{route}: missing published Packagist package link for {name}')
    for language in ['en', 'fr']:
        for logical in ('guides/demarrer.html', 'guides/modules.html'):
            route = localized(logical, language)
            if route in documents and re.search(r'composer\s+config\s+repositories\.', (root / route).read_text(encoding='utf-8')):
                errors.append('Application installation must use the published Packagist packages: ' + route)
    documentation_sources = manifest.get('documentationSources', [])
    guides = {record['page']: record for record in documentation_sources}
    expected_guides = {
        route for logical, routes in translations.items()
        if logical.startswith(('guides/', 'tutorials/', 'recipes/', 'modules/')) and logical != 'modules/core/index.html'
        for route in routes.values()
    }
    if len(guides) != len(documentation_sources) or set(guides) != expected_guides:
        errors.append('Documentation source inventory must cover every guide exactly once')
    for logical, routes in translations.items():
        english = guides.get(routes.get('en'))
        french = guides.get(routes.get('fr'))
        if english is not None and french is not None:
            if english.get('package') != french.get('package'):
                errors.append('Translated guides must retain the same source owner: ' + logical)
            if english.get('source') == french.get('source'):
                errors.append('Translated guides must have distinct authored language sources: ' + logical)
    for page, record in guides.items():
        owner = manifest['documentation'] if record['package'] == 'documentation' else packages.get(record['package'])
        source = record.get('source', '')
        language = record.get('language')
        if language != page_languages.get(page):
            errors.append('Guide source language differs from its page locale: ' + page)
        if owner is None or source.startswith('/') or '..' in Path(source).parts:
            errors.append('Invalid documentation source owner or path: ' + page)
            continue
        expected_source = owner['repository'] + '/blob/' + owner['revision'] + '/' + quote(source, safe='/')
        if any(record.get(key) != owner[key] for key in ('repository', 'revision')) or record.get('sourceUrl') != expected_source or not re.fullmatch(r'[0-9a-f]{64}', record.get('sourceSha256', '')):
            errors.append('Incorrect guide source provenance: ' + page)
        if page not in documents or expected_source not in documents[page].links:
            errors.append('Guide must link its exact source commit: ' + page)
        if page in documents:
            for link in documents[page].links:
                url = urlsplit(link)
                match = re.fullmatch(r'/PDFToolkit/(pdf-reader|pdf-images|pdf-fonts|pdf-to-html|opentype)/(?:blob|tree)/[^/]+/(README(?:\.fr)?\.md|CHANGELOG(?:\.fr)?\.md|SECURITY(?:\.fr)?\.md|docs/.+\.md)', url.path)
                if url.netloc == 'github.com' and match and link != expected_source:
                    errors.append('Module guide navigation must stay on the central site: ' + page + ' -> ' + link)
    for slug, routes in MODULE_GUIDES.items():
        for language in ['en', 'fr']:
            for route in routes:
                page = localized(f'modules/{slug}/{route}.html', language)
                if page not in guides or guides[page].get('package') != ('pdftoolkit/opentype' if slug == 'opentype' else 'pdftoolkit/pdf-' + slug):
                    errors.append('Missing local module guide and provenance: ' + str(page))
    html_reference = manifest.get('htmlDerivationReference', {})
    html_package = packages.get('pdftoolkit/pdf-to-html', {})
    expected_reference = html_package.get('repository', '') + '/blob/' + html_package.get('revision', '') + '/resources/reference-documents/Deriving_HTML_from_PDF_1-2.pdf'
    expected_metadata = html_package.get('repository', '') + '/blob/' + html_package.get('revision', '') + '/resources/reference.json'
    if html_reference.get('sourceUrl') != expected_reference or html_reference.get('metadataUrl') != expected_metadata or html_reference.get('physicalPdfPages') != 74 or html_reference.get('sha256') != '272669b92b073f74ae8ccd75ad35c94f0ee4f907fd8f9ded41fe3d1bc41f0f7d' or html_reference.get('bytes') != 900894 or html_reference.get('version') != '1.2' or html_reference.get('license') != 'CC-BY-4.0':
        errors.append('The HTML derivation reference must retain its supplied identity and released provenance')
    for language in ['en', 'fr']:
        reference_page = localized('modules/to-html/reference.html', language)
        if reference_page not in documents or expected_reference not in documents[reference_page].links or expected_metadata not in documents[reference_page].links:
            errors.append('Missing retained HTML derivation reference links: ' + str(reference_page))
    for language in ['en', 'fr']:
        if localized('modules/core/index.html', language) not in documents:
            errors.append('Missing localized core package hub: ' + language)
    assets = manifest.get('staticAssets', [])
    by_asset = {item['path']: item for item in assets}
    actual_assets = {path.relative_to(root).as_posix() for path in root.rglob('*') if path.is_file() and path.suffix != '.html' and path.name not in {'site-manifest.json', '.nojekyll'}}
    if len(by_asset) != len(assets) or set(by_asset) != actual_assets:
        errors.append('Static asset inventory must cover every published non-HTML file exactly once')
    for name, record in by_asset.items():
        path = root / name
        if name.startswith('/') or '..' in Path(name).parts or not path.is_file() or path.stat().st_size != record.get('bytes') or hashlib.sha256(path.read_bytes()).hexdigest() != record.get('sha256'):
            errors.append('Missing or modified static asset: ' + name)
    for language, records in indexes.items():
        for item in records:
            if item['url'] not in documents:
                errors.append('Missing localized API page: ' + item['title'] + ' / ' + language)
                continue
            package = packages.get(item['package'])
            if package is None or item['optional'] != package['optional']:
                errors.append('Missing or inconsistent API package: ' + item['title'])
                continue
            expected_source = package['repository'] + '/blob/' + package['revision'] + '/src/'
            if not item['sourceUrl'].startswith(expected_source) or item['sourceUrl'] not in documents[item['url']].links:
                errors.append('Incorrect API declaration source link: ' + item['title'] + ' / ' + language)
    examples = manifest['examples']
    sources = manifest.get('exampleSources', {})
    expected_derived = {name for name, record in sources.items() if record.get('kind') == 'conversion'}
    if {item.get('example') for item in derived} != expected_derived or len(derived) != len(expected_derived):
        errors.append('Derived HTML inventory must cover every conversion example exactly once')
    if len(set(examples)) != len(examples) or set(sources) != set(examples):
        errors.append('Example source inventory must cover every example exactly once')
    if set(manifest.get('pdfPages', {})) != set(examples):
        errors.append('Rendered page inventory must cover every example exactly once')
    for name in examples:
        pdf = root / 'examples' / (name + '.pdf')
        if not pdf.is_file() or not pdf.read_bytes().startswith(b'%PDF-'):
            errors.append('Missing PDF download: ' + name)
        source = root / 'examples' / (name + '.php.txt')
        if not source.is_file():
            errors.append('Missing source download: ' + name)
        record = sources.get(name, {})
        package = packages.get(record.get('package'))
        example_pages = record.get('pages', {})
        expected_pages = translations.get(record.get('page'), {})
        if example_pages != expected_pages or set(example_pages) != {'en', 'fr'}:
            errors.append('Example must identify its two translated tutorial pages: ' + name)
        if package is None or any(page not in documents for page in example_pages.values()) or not example_pages:
            errors.append('Missing example package or documented page: ' + name)
        else:
            source_path = record.get('source', '')
            expected_source = package['repository'] + '/blob/' + package['revision'] + '/' + quote(source_path, safe='/')
            if record.get('sourceUrl') != expected_source or any(expected_source not in documents[page].links for page in example_pages.values()):
                errors.append('Incorrect example source link: ' + name)
            if source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest() != record.get('sourceSha256'):
                errors.append('Example source bytes do not match their inventory: ' + name)
            if pdf.is_file() and hashlib.sha256(pdf.read_bytes()).hexdigest() != record.get('pdfSha256'):
                errors.append('Example PDF bytes do not match their inventory: ' + name)
            if record.get('kind') == 'generated':
                if package['name'] != 'roukmoute/pdf' or source_path != f'examples/{name}.php':
                    errors.append('Generated example must retain its core writer source: ' + name)
            elif record.get('kind') in {'input', 'conversion'}:
                input_path = record.get('input', '')
                expected_input = package['repository'] + '/blob/' + package['revision'] + '/' + quote(input_path, safe='/')
                if not package['optional'] or not input_path.startswith('tests/Fixtures/') or '..' in Path(input_path).parts:
                    errors.append('External input must belong to its pinned optional package: ' + name)
                if record.get('inputSourceUrl') != expected_input or any(expected_input not in documents[page].links for page in example_pages.values()):
                    errors.append('Incorrect input PDF source link: ' + name)
                if any('resultat-lecture' not in documents[page].ids for page in example_pages.values()):
                    errors.append('Missing reader console result panel: ' + name)
                console_path = f'examples/{name}.txt'
                console = root / console_path
                if record.get('console') != console_path or not console.is_file():
                    errors.append('Missing reader console download: ' + name)
                else:
                    result = console.read_text(encoding='utf-8')
                    if not result.strip() or hashlib.sha256(console.read_bytes()).hexdigest() != record.get('consoleSha256'):
                        errors.append('Reader console result does not match its inventory: ' + name)
                    for page in example_pages.values():
                        if escape(result, quote=True) not in (root / page).read_text(encoding='utf-8'):
                            errors.append('Reader console result is missing or incorrectly escaped: ' + name + ' / ' + page)
            else:
                errors.append('Unknown example source kind: ' + name)
            if record.get('kind') == 'conversion':
                expected_html = f'examples/{name}.html'
                report = json.loads((root / f'examples/{name}.txt').read_text(encoding='utf-8'))
                if report.get('htmlSha256') != record.get('htmlSha256'):
                    errors.append('Derived HTML differs from its CLI report: ' + name)
                reported_assets = report.get('assets', [])
                assets = record.get('assets', [])
                if len(assets) != len(reported_assets) or len({item.get('filename') for item in assets}) != len(assets):
                    errors.append('Derived assets must cover the CLI inventory exactly once: ' + name)
                for asset, reported in zip(assets, reported_assets):
                    filename = asset.get('filename', '')
                    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', filename) or '..' in filename or asset.get('path') != 'examples/' + filename:
                        errors.append('Invalid derived asset path: ' + name)
                        continue
                    asset_file = root / asset['path']
                    if any(asset.get(key) != reported.get(key) for key in ('filename', 'mediaType', 'sha256')) or not asset_file.is_file() or asset_file.stat().st_size != asset.get('bytes') or hashlib.sha256(asset_file.read_bytes()).hexdigest() != asset.get('sha256'):
                        errors.append('Missing or modified derived asset: ' + filename)
                entries = [item for item in derived if item.get('example') == name]
                if len(entries) != 1 or entries[0].get('path') != expected_html or entries[0].get('sha256') != record.get('htmlSha256') or entries[0].get('package') != package['name'] or entries[0].get('revision') != package['revision'] or record.get('html') != expected_html:
                    errors.append('Derived HTML must retain its example, hash and exact package provenance: ' + name)
                for page in example_pages.values():
                    markup = (root / page).read_text(encoding='utf-8')
                    frame = re.search(r'<iframe\b([^>]*\bsrc="' + re.escape(manifest['basePath'] + expected_html) + r'"[^>]*)>', markup)
                    if 'resultat-html' not in documents[page].ids or frame is None or re.search(r'\bsandbox=""', frame[1]) is None:
                        errors.append('Derived HTML must be isolated in a sandboxed example frame: ' + page)
                if record.get('css'):
                    css = root / record['css']
                    if record['css'] != f'examples/{name}.css' or not css.is_file() or hashlib.sha256(css.read_bytes()).hexdigest() != record.get('cssSha256'):
                        errors.append('Derived CSS must match its inventory: ' + name)
        previews = manifest.get('pdfPages', {}).get(name, [])
        if not previews:
            errors.append('Missing rendered PDF pages: ' + name)
        if record.get('kind') == 'input' and len(previews) != record.get('expectedPages'):
            errors.append('Missing pages from the external input preview: ' + name)
        for page_number, preview in enumerate(previews, start=1):
            expected = f'assets/pdf-pages/{name}-{page_number}.png'
            if preview != expected:
                errors.append(f'{name}: unexpected preview sequence {preview}')
                continue
            path = root / expected
            header = path.read_bytes()[:24] if path.is_file() else b''
            if len(header) < 24 or not header.startswith(b'\x89PNG\r\n\x1a\n'):
                errors.append('Missing PNG preview: ' + expected)
            elif min(struct.unpack('>II', header[16:24])) <= 0:
                errors.append('Invalid PNG dimensions: ' + expected)
    specifications = manifest.get('specificationSources', [])
    if {item['source'] for item in specifications} != {'PDF32000_2008.pdf', 'adobe_supplement_iso32000.pdf'}:
        errors.append('The documentation must retain both original specification sources')
    for source in specifications:
        target = root / source['download']
        if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != source['sha256']:
            errors.append('Missing or modified specification source: ' + source['source'])
    repository_sources = manifest.get('repositorySpecificationSources', [])
    if len(repository_sources) != 1:
        errors.append('ISO 32000-2 needs one distinct repository-source provenance record')
    else:
        source = repository_sources[0]
        core = packages.get('roukmoute/pdf', {})
        metadata_url = core.get('repository', '') + '/blob/' + core.get('revision', '') + '/resources/iso32000-2-2020/metadata.json'
        if source.get('source') != 'ISO_32000-2_sponsored_EC3.pdf' or source.get('editionIdentifier') != 'iso32000-2:2020' or source.get('standard') != 'ISO 32000-2:2020' or source.get('specifiedPdfVersion') != '2.0':
            errors.append('Repository-source identity must remain the distinct ISO 32000-2:2020 edition')
        if source.get('errataCollection') != {'number': 3, 'publication_date': '2026-06-01'} or source.get('pdfPages') != 1023 or source.get('sha256') != '90f4b666d46405dd62630a98d514158b4de5304b749523c4081680ac4fe2e230':
            errors.append('Public EC3 source provenance differs from the reviewed supplied copy')
        source_url = core.get('repository', '') + '/blob/' + core.get('revision', '') + '/resources/reference-documents/ISO_32000-2_sponsored_EC3.pdf'
        if source.get('publicCopyIncluded') is not True or source.get('sourceUrl') != source_url or source.get('repository') != core.get('repository') or source.get('revision') != core.get('revision') or source.get('bytes') != 19205142:
            errors.append('ISO 32000-2 must link the unchanged original in the pinned public core repository')
        if 'download' in source or any(Path(name).name == source.get('source') for name in published_files):
            errors.append('The large ISO 32000-2 original is linked from its source repository without a duplicate site asset')
        if source.get('provider') != 'PDF Association' or source.get('providerUrl') != 'https://www.pdfa.org/sponsored-standards/':
            errors.append('ISO source provider must identify PDF Association sponsored access')
        table_ids = source.get('dictionaryTableIdentifiers', [])
        entry_keys = {(item.get('specificationTable'), item.get('specificationKey')) for item in indexes['en'] if item.get('specificationEdition') == 'iso32000-2:2020' and item.get('specificationKey') is not None}
        if source.get('catalogueSourceUrl') != metadata_url or source.get('dictionaryTables') != len(set(table_ids)) or len(table_ids) < 299 or source.get('entryClasses') != len(entry_keys) or len(entry_keys) < 1600 or source.get('completeCatalogue') is not True or source.get('completeConformance') is not False:
            errors.append('ISO 32000-2 base table inventory or metadata provenance is inconsistent')
        for language in ['en', 'fr']:
            guide = localized('guides/pdf-2-0.html', language)
            if guide not in documents or metadata_url not in documents[guide].links or source_url not in documents[guide].links:
                errors.append('PDF 2.0 guide must identify its published source metadata: ' + guide)
            for item in indexes[language]:
                name = item['title']
                expected_definition = (name.startswith('PDF\\Specification\\Iso32000_2\\') and name != 'PDF\\Specification\\Iso32000_2\\Catalogue') or name == 'PDF\\Document\\Files\\AssociatedFilesPropertyList'
                if expected_definition or item.get('specificationEdition'):
                    table = item.get('specificationTable')
                    document = documents.get(item['url'])
                    if item.get('specificationEdition') != 'iso32000-2:2020' or table not in table_ids or document is None or document.specification_panels != [('iso32000-2:2020', table)] or metadata_url not in document.links or not any(link.startswith(source_url + '#page=') for link in document.links):
                        errors.append('ISO 32000-2 component must retain its own edition/table provenance: ' + name + ' / ' + language)
    bundle_sources = manifest.get('bundleSpecificationSources', [])
    expected_bundle = {
        'PDF-Declarations.pdf', 'Well-Tagged-PDF-WTPDF-1.0.pdf',
        'PDF20_AN003-ObjectMetadataLocations.pdf', 'PDF20_AN002-AF.pdf', 'PDF20_AN001-BPC.pdf',
        'ISO-TS-32005-2023-sponsored.pdf', 'ISO-TS-32004-2024_sponsored.pdf',
        'ISO_TS_32003-2023_sponsored.pdf', 'ISO_TS_32002-2022_sponsored_EC3.pdf',
        'ISO_TS_32001-2022_sponsored_EC3.pdf', 'ISO_32000-2_sponsored_EC3(1).pdf',
    }
    if len(bundle_sources) != 11 or {item.get('source') for item in bundle_sources} != expected_bundle or sum(item.get('pdfPages', 0) for item in bundle_sources) != 1234:
        errors.append('The supplied PDF 2.0 bundle must retain eleven distinct originals and 1234 physical pages')
    core = packages.get('roukmoute/pdf', {})
    bundle_metadata_url = core.get('repository', '') + '/blob/' + core.get('revision', '') + '/resources/iso32000-2-bundle/sources.json'
    for source in bundle_sources:
        path = 'resources/reference-documents/' + source['source']
        expected_url = core.get('repository', '') + '/blob/' + core.get('revision', '') + '/' + quote(path, safe='/')
        if source.get('sourceUrl') != expected_url or source.get('catalogueSourceUrl') != bundle_metadata_url or source.get('repository') != core.get('repository') or source.get('revision') != core.get('revision'):
            errors.append('Bundle original must identify the exact selected package revision: ' + source['source'])
        if source.get('provider') != 'PDF Association' or source.get('providerUrl') != 'https://www.pdfa.org/sponsored-standards/' or not re.fullmatch('[0-9a-f]{64}', source.get('sha256', '')) or source.get('bytes', 0) < 1:
            errors.append('Missing bundle fingerprint or PDF Association provenance: ' + source['source'])
        if 'download' in source or any(Path(name).name == source['source'] for name in published_files):
            errors.append('Bundle originals must be linked from their repository without duplicate site binaries')
        for language in ['en', 'fr']:
            guide = documents.get(localized('guides/pdf-2-0-bundle.html', language))
            if guide is None or expected_url not in guide.links or bundle_metadata_url not in guide.links:
                errors.append('Bundle guide must link each retained source and its exact metadata: ' + source['source'] + ' / ' + language)
    references = manifest.get('referenceSources', [])
    expected_references = {
        'pdf_17_errata.pdf', 'pdf_reference.pdf',
        'pdf_reference1-7_addendum_redaction.pdf', 'pdf_reference_1-7.pdf',
    }
    if len(references) != len(expected_references) or {item['source'] for item in references} != expected_references:
        errors.append('The documentation must retain all four original archival Adobe references')
    reference_guides = [documents.get(localized('guides/references-adobe.html', language)) for language in ['en', 'fr']]
    for source in references:
        download = 'downloads/adobe-references/' + source['source']
        if source.get('role') != 'archival-reference' or source.get('download') != download:
            errors.append('Incorrect archival reference role or download: ' + source['source'])
            continue
        target = root / download
        if not target.is_file() or target.stat().st_size != source['bytes'] or hashlib.sha256(target.read_bytes()).hexdigest() != source['sha256']:
            errors.append('Missing or modified archival reference: ' + source['source'])
        expected_link = manifest['basePath'] + quote(download, safe='/')
        for language, guide in zip(['en', 'fr'], reference_guides):
            if guide is None or not any(link.split('#', 1)[0] == expected_link for link in guide.links):
                errors.append('The archival guide must link the original download: ' + source['source'] + ' / ' + language)
    if errors:
        raise ValueError('\n'.join(errors[:40]) + f'\n{len(errors)} documentation errors')
    print(f'Checked {len(pages)} HTML pages in English and French, {len(index)} unique API records per locale, reciprocal language links, {len(aliases)} legacy aliases, all local anchors and {len(manifest["examples"])} shared PDF/source pairs')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    check(parser.parse_args().directory)
