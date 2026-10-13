"""Validate compatibility files, preserved bytes and actual redirect JavaScript."""

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import quote, urlsplit


class RedirectDocument(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.headings = 0
        self.canonicals = []
        self.scripts = []
        self.links = []
        self.refreshes = []
        self.noindex = False
        self.noscript_depth = 0
        self.heading_text = []
        self.destination_text = []
        self.inline_script_text = []
        self.in_heading = False
        self.in_destination = False
        self.in_script = False
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == 'noscript':
            self.noscript_depth += 1
        if tag == 'h1':
            self.headings += 1
            self.in_heading = True
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs.get('href'))
        if tag == 'script':
            self.scripts.append(attrs)
            self.in_script = True
        if tag == 'a':
            self.links.append(attrs)
            self.in_destination = attrs.get('id') == 'destination'
        if tag == 'meta' and attrs.get('http-equiv', '').lower() == 'refresh':
            self.refreshes.append((attrs.get('content'), self.noscript_depth > 0))
        if tag == 'meta' and attrs.get('name') == 'robots' and attrs.get('content') == 'noindex':
            self.noindex = True

    def handle_endtag(self, tag):
        if tag == 'noscript':
            self.noscript_depth -= 1
        if tag == 'h1':
            self.in_heading = False
        if tag == 'a':
            self.in_destination = False
        if tag == 'script':
            self.in_script = False

    def handle_data(self, data):
        if self.in_heading:
            self.heading_text.append(data)
        if self.in_destination:
            self.destination_text.append(data)
        if self.in_script:
            self.inline_script_text.append(data)


def file_path(root, relative):
    if (not isinstance(relative, str) or not relative or '\\' in relative or ':' in relative or
            relative.startswith('/') or any(part in {'', '.', '..'} for part in relative.split('/')) or
            any(ord(char) < 32 or ord(char) == 127 for char in relative)):
        raise ValueError('Invalid compatibility path: ' + repr(relative))
    path = root / relative
    if not path.is_relative_to(root):
        raise ValueError('Compatibility path leaves the output: ' + relative)
    for part in [path, *path.parents]:
        if part.is_symlink() or part.is_junction():
            raise ValueError('Unexpected symbolic link or junction: ' + relative)
        if part == root:
            break
    return path


def verify_bytes(root, record):
    if not isinstance(record, dict) or set(record) != {'path', 'bytes', 'sha256'}:
        raise ValueError('Malformed file integrity record')
    if type(record['bytes']) is not int or record['bytes'] < 0 or not re.fullmatch(r'[0-9a-f]{64}', record['sha256']):
        raise ValueError('Invalid file integrity record')
    path = file_path(root, record['path'])
    if path.stat().st_size != record['bytes']:
        raise ValueError('Asset bytes or SHA-256 mismatch: ' + record['path'])
    digest = hashlib.sha256()
    with path.open('rb') as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    if path.stat().st_size != record['bytes'] or digest.hexdigest() != record['sha256']:
        raise ValueError('Asset bytes or SHA-256 mismatch: ' + record['path'])
    return path


def source_pages(source):
    values = source.get('pages')
    if not isinstance(values, list) or 'index.html' not in values or len(set(values)) != len(values):
        raise ValueError('Invalid source page inventory')
    if any(not isinstance(value, str) or not value.endswith('.html') for value in values):
        raise ValueError('Source page inventory contains non-HTML paths')
    return set(values)


def check(root, node='node'):
    root = root.resolve()
    manifest = json.loads((root / 'legacy-manifest.json').read_text(encoding='utf-8'))
    if manifest.get('schemaVersion') != 1 or manifest.get('identity') != 'pdftoolkit-legacy-compatibility':
        raise ValueError('Not a supported legacy compatibility artifact')
    site_url = manifest['siteUrl']
    parsed = urlsplit(site_url)
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or
            parsed.path != '/' or parsed.query or parsed.fragment):
        raise ValueError('Legacy destination must be an HTTPS site root')
    base = manifest['legacyBase']
    if not re.fullmatch(r'(?:/[A-Za-z0-9_.-]+)+', base) or any(part in {'.', '..'} for part in base.split('/')):
        raise ValueError('Invalid legacy base')
    for field in ['sourceDocsRevision', 'sourceRevision', 'previousRevision']:
        if not isinstance(manifest[field], str) or not re.fullmatch(r'[0-9a-f]{40}', manifest[field]):
            raise ValueError('Expected exact source commit in ' + field)
    current = json.loads(verify_bytes(root, manifest['sourceManifest']).read_text(encoding='utf-8'))
    previous = json.loads(verify_bytes(root, manifest['previousManifest']).read_text(encoding='utf-8'))
    if (current.get('docsRevision') != manifest['sourceDocsRevision'] or current.get('revision') != manifest['sourceRevision'] or
            previous.get('revision') != manifest['previousRevision'] or current.get('basePath') != '/' or previous.get('basePath') != base + '/'):
        raise ValueError('Source identity differs from the compatibility manifest')
    if manifest['assets'] != sorted(current['staticAssets'], key=lambda record: record['path']):
        raise ValueError('Preserved assets differ from the documentation source inventory')
    asset_paths = [record['path'] for record in manifest['assets']]
    if len(set(asset_paths)) != len(asset_paths):
        raise ValueError('Duplicate preserved asset paths')
    for record in manifest['assets']:
        if record['path'].lower().endswith('.html'):
            raise ValueError('HTML is incorrectly declared as a binary asset')
        verify_bytes(root, record)
    script = verify_bytes(root, manifest['redirectScript'])
    if manifest['redirectScript']['path'] != 'assets/legacy-redirect.js':
        raise ValueError('Unexpected redirect runtime path')
    expected_routes = source_pages(current) | source_pages(previous)
    expected_routes.discard('404.html')
    redirects = manifest['redirects']
    if [record['path'] for record in redirects] != sorted(expected_routes):
        raise ValueError('Redirect routes omit old or current pages, or include duplicates')
    if manifest['notFound'] != '404.html':
        raise ValueError('Missing custom 404 fallback')
    if set(path.relative_to(root).as_posix() for path in root.rglob('*.html')) != expected_routes | {'404.html'}:
        raise ValueError('Stale or missing redirect HTML files')
    for record in [*redirects, {'path': '404.html', 'canonical': site_url}]:
        relative = record['path']
        canonical = site_url if relative in {'index.html', '404.html'} else site_url + quote(relative, safe='/')
        if record['canonical'] != canonical:
            raise ValueError('Wrong full canonical URL: ' + relative)
        document = RedirectDocument(file_path(root, relative).read_text(encoding='utf-8'))
        expected_canonicals = [] if relative == '404.html' else [canonical]
        if document.headings != 1 or not ''.join(document.heading_text).strip() or document.canonicals != expected_canonicals:
            raise ValueError('Expected one heading and exact canonical URL: ' + relative)
        if relative == '404.html' and not document.noindex:
            raise ValueError('Unknown-route fallback must be marked noindex')
        if ''.join(document.inline_script_text).strip() or len(document.scripts) != 1 or document.scripts[0] != {
            'src': base + '/' + manifest['redirectScript']['path'],
            'data-legacy-base': base, 'data-site-url': site_url, 'defer': None,
        }:
            raise ValueError('Unexpected runtime resource or inline script: ' + relative)
        if document.refreshes != [(f'0; url={canonical}', True)]:
            raise ValueError('Refresh fallback must be inside noscript: ' + relative)
        links = [link for link in document.links if link.get('id') == 'destination']
        if len(links) != 1 or links[0].get('href') != canonical or not ''.join(document.destination_text).strip():
            raise ValueError('Missing accessible fallback link: ' + relative)
    expected_files = set(asset_paths) | expected_routes | {
        '404.html', 'legacy-manifest.json', '.nojekyll', manifest['redirectScript']['path'],
        manifest['sourceManifest']['path'], manifest['previousManifest']['path'],
    }
    actual_files = set()
    for path in root.rglob('*'):
        if path.is_symlink() or path.is_junction():
            raise ValueError('Unexpected symbolic link or junction: ' + str(path))
        if path.is_file():
            actual_files.add(path.relative_to(root).as_posix())
    if actual_files != expected_files or (root / '.nojekyll').read_bytes() != b'':
        raise ValueError('Unexpected, missing or stale compatibility files')
    runtime_test = Path(__file__).resolve().parents[1] / 'tests' / 'legacy_redirect.cjs'
    subprocess.run([node, str(runtime_test), str(root)], check=True)
    print(f'Checked {len(redirects)} full canonical redirects, {len(asset_paths)} preserved assets and redirect runtime behavior')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('site', type=Path)
    parser.add_argument('--node', default='node', help='Node.js executable for the isolated JavaScript checks')
    args = parser.parse_args()
    try:
        check(args.site, args.node)
    except (ValueError, OSError, subprocess.CalledProcessError, KeyError, TypeError) as error:
        parser.exit(1, f'Legacy site verification failed: {error}\n')


if __name__ == '__main__':
    main()
