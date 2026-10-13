"""Build the old /pdf Pages site from the published documentation inventory.

Only Python's standard library is needed. --site-dir replaces HTTP reads with
local files for reproducible offline validation; publication uses --site-url.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
from html import escape
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


MAX_MANIFEST_BYTES = 16 * 1024 * 1024
MAX_ASSET_BYTES = 512 * 1024 * 1024
MAX_TOTAL_BYTES = 8 * 1024 * 1024 * 1024
MAX_FILES = 100_000
SCRIPT_PATH = 'assets/legacy-redirect.js'
MANIFEST_PATH = 'legacy-manifest.json'
CURRENT_SOURCE_PATH = 'legacy-documentation-source.json'
PREVIOUS_SOURCE_PATH = 'legacy-previous-source.json'
IDENTITY = 'pdftoolkit-legacy-compatibility'
SHA = re.compile(r'[0-9a-f]{64}')
REVISION = re.compile(r'[0-9a-f]{40}')

REDIRECT_SCRIPT = '''"use strict";
(() => {
  const script = document.currentScript;
  if (!script) return;
  const base = script.getAttribute("data-legacy-base");
  const site = script.getAttribute("data-site-url");
  let root;
  try { root = new URL(site); } catch { return; }
  if (root.protocol !== "https:" || root.pathname !== "/" || root.search || root.hash ||
      root.username || root.password || location.origin !== root.origin) return;
  if (!base || !base.startsWith("/") || base.endsWith("/") || base.includes("//")) return;
  const path = location.pathname;
  if (path !== base && !path.startsWith(base + "/")) return;
  const suffix = path.slice(base.length) || "/";
  // Concatenating an absolute origin keeps even a // suffix on the same host.
  const destination = root.origin + suffix + location.search + location.hash;
  try { if (new URL(destination).origin !== root.origin) return; } catch { return; }
  const link = document.getElementById("destination");
  if (link) link.setAttribute("href", destination);
  location.replace(destination);
})();
'''


def route_path(value):
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError(f'Invalid relative file path: {value!r}')
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise ValueError(f'Control character in file path: {value!r}')
    path = PurePosixPath(value)
    if path.is_absolute() or ':' in value or any(part in {'', '.', '..'} for part in value.split('/')):
        raise ValueError(f'Unbounded relative file path: {value!r}')
    return value


def bounded_file(root, relative):
    relative = route_path(relative)
    result = root.joinpath(*PurePosixPath(relative).parts)
    if not result.is_relative_to(root):
        raise ValueError('File path escapes its directory: ' + relative)
    for part in [result, *result.parents]:
        if part.is_symlink() or part.is_junction():
            raise ValueError('Symbolic links and junctions are not supported: ' + relative)
        if part == root:
            break
    return result


def metadata(path, data):
    return {'path': path, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def validate_asset(record):
    if not isinstance(record, dict) or set(record) != {'path', 'bytes', 'sha256'}:
        raise ValueError('Asset records need exactly path, bytes and sha256')
    route_path(record['path'])
    if record['path'].lower().endswith('.html'):
        raise ValueError('HTML cannot be declared as a static asset: ' + record['path'])
    if type(record['bytes']) is not int or not 0 <= record['bytes'] <= MAX_ASSET_BYTES:
        raise ValueError('Asset exceeds the byte limit: ' + record['path'])
    if not isinstance(record['sha256'], str) or not SHA.fullmatch(record['sha256']):
        raise ValueError('Invalid asset SHA-256: ' + record['path'])


def pages(manifest):
    values = manifest.get('pages')
    if not isinstance(values, list) or not values or len(values) > MAX_FILES:
        raise ValueError('Source manifest needs a bounded nonempty page inventory')
    if len(set(values)) != len(values):
        raise ValueError('Source manifest has duplicate pages')
    for value in values:
        route_path(value)
        if not value.endswith('.html'):
            raise ValueError('Page inventory contains a non-HTML route: ' + value)
    if 'index.html' not in values:
        raise ValueError('Source manifest is missing index.html')
    return set(values)


class SameOriginRedirect(HTTPRedirectHandler):
    def __init__(self, origin):
        self.origin = origin

    def redirect_request(self, request, response, code, message, headers, new_url):
        parsed = urlsplit(new_url)
        if parsed.scheme + '://' + parsed.netloc != self.origin:
            raise ValueError('Download redirects outside the documentation origin')
        return super().redirect_request(request, response, code, message, headers, new_url)


class Source:
    def __init__(self, site_url, directory):
        self.site_url = site_url
        self.directory = directory.resolve() if directory else None
        parsed = urlsplit(site_url)
        self.origin = parsed.scheme + '://' + parsed.netloc

    def open(self, relative):
        route_path(relative)
        if self.directory:
            return bounded_file(self.directory, relative).open('rb')
        request = Request(self.site_url + quote(relative, safe='/'), headers={
            'User-Agent': 'PDFToolkit-legacy-site-builder', 'Accept-Encoding': 'identity',
        })
        return build_opener(SameOriginRedirect(self.origin)).open(request, timeout=30)

    def manifest(self):
        with self.open('site-manifest.json') as source:
            data = source.read(MAX_MANIFEST_BYTES + 1)
        if len(data) > MAX_MANIFEST_BYTES:
            raise ValueError('Documentation manifest exceeds the byte limit')
        return data

    def copy_asset(self, output, record):
        destination = bounded_file(output, record['path'])
        destination.parent.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256()
        size = 0
        with self.open(record['path']) as source, destination.open('xb') as target:
            while chunk := source.read(min(1024 * 1024, record['bytes'] - size + 1)):
                size += len(chunk)
                if size > record['bytes']:
                    raise ValueError('Download exceeds its declared bytes: ' + record['path'])
                digest.update(chunk)
                target.write(chunk)
        if size != record['bytes'] or digest.hexdigest() != record['sha256']:
            raise ValueError('Downloaded asset differs from its declared bytes or SHA-256: ' + record['path'])


def redirect_html(canonical, site_url, base, not_found=False):
    title = 'La documentation a déménagé'
    canonical_tag = '' if not_found else f'<link rel="canonical" href="{escape(canonical, quote=True)}">'
    robots = '<meta name="robots" content="noindex">' if not_found else ''
    return f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · PDFToolkit</title>{canonical_tag}{robots}
<script src="{escape(base + '/' + SCRIPT_PATH, quote=True)}" data-legacy-base="{escape(base, quote=True)}" data-site-url="{escape(site_url, quote=True)}" defer></script>
<noscript><meta http-equiv="refresh" content="0; url={escape(canonical, quote=True)}"></noscript>
</head><body><main><h1>{title}</h1><p>La documentation PDFToolkit est maintenant publiée à la racine du site.</p>
<p><a id="destination" href="{escape(canonical, quote=True)}">Consulter la documentation à sa nouvelle adresse</a></p>
<noscript><p>Activez JavaScript pour conserver les paramètres et l’ancre de votre ancienne adresse lors de la redirection.</p></noscript>
</main></body></html>
'''


def write(output, relative, data):
    destination = bounded_file(output, relative)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)


def build(site_url, output, base, legacy_manifest, site_dir=None):
    parsed = urlsplit(site_url)
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or
            parsed.path not in {'', '/'} or parsed.query or parsed.fragment):
        raise ValueError('site-url must be an HTTPS origin without credentials, query or fragment')
    site_url = parsed.scheme + '://' + parsed.netloc + '/'
    if not re.fullmatch(r'(?:/[A-Za-z0-9_.-]+)+', base) or any(part in {'.', '..'} for part in base.split('/')):
        raise ValueError('legacy-base must be a bounded path without a trailing slash')
    source = Source(site_url, site_dir)
    current_data = source.manifest()
    current = json.loads(current_data)
    with legacy_manifest.open('rb') as source_file:
        previous_data = source_file.read(MAX_MANIFEST_BYTES + 1)
    if len(previous_data) > MAX_MANIFEST_BYTES:
        raise ValueError('Previous manifest exceeds the byte limit')
    previous = json.loads(previous_data)
    if current.get('basePath') != '/':
        raise ValueError('Documentation source must be built at the site root')
    if previous.get('basePath') != base + '/':
        raise ValueError('Previous manifest does not match legacy-base')
    for value in [current.get('revision'), current.get('docsRevision'), previous.get('revision')]:
        if not isinstance(value, str) or not REVISION.fullmatch(value):
            raise ValueError('Source revisions must be exact commit SHAs')
    redirects = sorted((pages(current) | pages(previous)) - {'404.html'})
    if len(redirects) > MAX_FILES:
        raise ValueError('Combined page inventory exceeds the file limit')
    records = current.get('staticAssets')
    if not isinstance(records, list) or not records or len(records) > MAX_FILES:
        raise ValueError('Documentation source needs a bounded staticAssets inventory')
    for record in records:
        validate_asset(record)
    asset_paths = [record['path'] for record in records]
    if len(set(asset_paths)) != len(asset_paths):
        raise ValueError('Duplicate static asset paths')
    if sum(record['bytes'] for record in records) > MAX_TOTAL_BYTES:
        raise ValueError('Static assets exceed the total byte limit')
    reserved = set(redirects) | {'404.html', SCRIPT_PATH, MANIFEST_PATH, CURRENT_SOURCE_PATH, PREVIOUS_SOURCE_PATH, '.nojekyll'}
    if reserved.intersection(asset_paths):
        raise ValueError('Static assets collide with compatibility output files')
    if output.is_symlink() or (output.exists() and (not output.is_dir() or any(output.iterdir()))):
        raise ValueError('Output directory must be empty; existing files are never removed')
    output.mkdir(parents=True, exist_ok=True)
    output = output.resolve()
    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(lambda record: source.copy_asset(output, record), records))
    write(output, SCRIPT_PATH, REDIRECT_SCRIPT.encode('utf-8'))
    redirect_records = []
    for relative in redirects:
        canonical = site_url if relative == 'index.html' else site_url + quote(relative, safe='/')
        write(output, relative, redirect_html(canonical, site_url, base).encode('utf-8'))
        redirect_records.append({'path': relative, 'canonical': canonical})
    write(output, '404.html', redirect_html(site_url, site_url, base, not_found=True).encode('utf-8'))
    write(output, CURRENT_SOURCE_PATH, current_data)
    write(output, PREVIOUS_SOURCE_PATH, previous_data)
    write(output, '.nojekyll', b'')
    manifest = {
        'schemaVersion': 1, 'identity': IDENTITY, 'legacyBase': base, 'siteUrl': site_url,
        'sourceDocsRevision': current['docsRevision'], 'sourceRevision': current['revision'],
        'previousRevision': previous['revision'],
        'sourceManifest': metadata(CURRENT_SOURCE_PATH, current_data),
        'previousManifest': metadata(PREVIOUS_SOURCE_PATH, previous_data),
        'redirectScript': metadata(SCRIPT_PATH, REDIRECT_SCRIPT.encode('utf-8')),
        'assets': sorted(records, key=lambda record: record['path']),
        'redirects': redirect_records, 'notFound': '404.html',
    }
    write(output, MANIFEST_PATH, (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    print(f'Built {len(redirects)} legacy redirects and {len(records)} unchanged assets into {output}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site-url', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--legacy-base', default='/pdf')
    parser.add_argument('--legacy-manifest', type=Path, required=True)
    parser.add_argument('--site-dir', type=Path, help='Read a built root site locally instead of HTTP')
    args = parser.parse_args()
    try:
        build(args.site_url, args.output, args.legacy_base, args.legacy_manifest, args.site_dir)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'Legacy site build failed: {error}\n')


if __name__ == '__main__':
    main()
