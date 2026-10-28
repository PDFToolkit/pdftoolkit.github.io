"""Publish the separately released browser demo without extending package pins."""
from __future__ import annotations

import argparse
import base64
from dataclasses import asdict, dataclass
from hashlib import sha256
import gzip
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
from urllib.parse import urlsplit


@dataclass(frozen=True)
class DemoSource:
    repository: str
    version: str
    tag: str
    revision: str

    @classmethod
    def load(cls, path: Path) -> DemoSource:
        if path.stat().st_size > 16384:
            raise ValueError('Demo source manifest exceeds its size limit')
        value = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(value, dict) or value.get('schemaVersion') != 1:
            raise ValueError('Unsupported demo source manifest')
        source = cls(**{key: value.get(key, '') for key in ('repository', 'version', 'tag', 'revision')})
        source.validate()
        return source

    def validate(self) -> None:
        if any(not isinstance(value, str) for value in (self.repository, self.version, self.tag, self.revision)):
            raise ValueError('Demo source identity fields must be strings')
        if self.repository != 'https://github.com/PDFToolkit/pdf-to-html-demo':
            raise ValueError('Unexpected demo source repository')
        if not re.fullmatch(r'\d+\.\d+\.\d+', self.version) or self.tag != 'v' + self.version:
            raise ValueError('Demo source must select a stable release tag')
        if not re.fullmatch(r'[0-9a-f]{40}', self.revision):
            raise ValueError('Demo source must select an exact commit')

    def check(self, root: Path, remote: bool = False) -> None:
        def git(*arguments: str) -> str:
            return subprocess.run(['git', '-C', str(root), *arguments], check=True,
                                  capture_output=True, text=True).stdout.strip()
        if git('rev-parse', 'HEAD') != self.revision:
            raise ValueError('Demo checkout differs from the released source pin')
        if git('cat-file', '-t', self.tag) != 'tag' or git('rev-parse', self.tag + '^{commit}') != self.revision:
            raise ValueError('Demo annotated tag differs from the released source pin')
        if git('diff', 'HEAD', '--name-only'):
            raise ValueError('Demo checkout has modified tracked release inputs')
        if remote:
            tag = 'refs/tags/' + self.tag
            references = dict(line.split('\t', 1)[::-1] for line in git('ls-remote', self.repository, tag, tag + '^{}').splitlines())
            if references.get(tag + '^{}') != self.revision or tag not in references:
                raise ValueError('Published demo annotated tag differs from the source pin')

    def manifest(self) -> dict:
        return {'schemaVersion': 1, **asdict(self)}


@dataclass(frozen=True)
class DemoArtifact:
    path: str
    bytes: int
    sha256: str
    mediaType: str

    @classmethod
    def parse(cls, value: dict) -> DemoArtifact:
        if not isinstance(value, dict):
            raise ValueError('Demo artifact record must be an object')
        artifact = cls(**{key: value.get(key) for key in ('path', 'bytes', 'sha256', 'mediaType')})
        if not isinstance(artifact.path, str) or not re.fullmatch(r'[A-Za-z0-9_@-][A-Za-z0-9_./@+-]*', artifact.path):
            raise ValueError('Invalid demo artifact path')
        parts = PurePosixPath(artifact.path).parts
        if any(part in {'.', '..'} or part.startswith('.') for part in parts) or str(PurePosixPath(artifact.path)) != artifact.path:
            raise ValueError('Invalid demo artifact path')
        if artifact.path.lower().endswith(('.html', '.htm', '.php')):
            raise ValueError('Executable demo documents must not be published as raw pages')
        if type(artifact.bytes) is not int or not 0 < artifact.bytes <= 128 * 1024 * 1024:
            raise ValueError('Demo artifact exceeds its size limit')
        if not isinstance(artifact.sha256, str) or not re.fullmatch(r'[0-9a-f]{64}', artifact.sha256):
            raise ValueError('Invalid demo artifact hash')
        if not isinstance(artifact.mediaType, str) or not re.fullmatch(r'[a-z0-9.+-]+/[a-z0-9.+-]+', artifact.mediaType):
            raise ValueError('Invalid demo artifact media type')
        return artifact

    def verify(self, root: Path) -> Path:
        file = root / self.path
        if any(parent.is_symlink() for parent in [file, *file.parents] if parent != root.parent):
            raise ValueError('Symbolic links are not demo artifacts: ' + self.path)
        if not file.is_file() or not file.resolve().is_relative_to(root.resolve()):
            raise ValueError('Missing or external demo artifact: ' + self.path)
        if file.stat().st_size != self.bytes or sha256(file.read_bytes()).hexdigest() != self.sha256:
            raise ValueError('Modified demo artifact: ' + self.path)
        return file

    def verify_png(self, root: Path, width: int, height: int) -> None:
        if self.mediaType != 'image/png' or any(type(value) is not int or not 0 < value <= 32768 for value in (width, height)):
            raise ValueError('Invalid demo preview dimensions')
        with self.verify(root).open('rb') as stream:
            header = stream.read(24)
        if len(header) != 24 or header[:8] != b'\x89PNG\r\n\x1a\n' or header[12:16] != b'IHDR' or int.from_bytes(header[16:20], 'big') != width or int.from_bytes(header[20:24], 'big') != height:
            raise ValueError('Demo preview dimensions differ from its PNG bytes')

    def record(self, prefix: str = '') -> dict:
        return {**asdict(self), 'path': prefix + self.path}


class DemoFragment(HTMLParser):
    """A released UI fragment may reference assets, never inline executable code."""
    def __init__(self, value: str):
        super().__init__(convert_charrefs=True)
        self.roots = 0
        self.feed(value)
        if self.roots != 1:
            raise ValueError('Demo fragment must have one application root')

    def handle_starttag(self, tag: str, attributes: list[tuple[str, str | None]]) -> None:
        attrs = dict(attributes)
        if 'data-demo-root' in attrs:
            self.roots += 1
        if tag in {'script', 'style', 'base', 'html', 'head', 'body', 'h1', 'object', 'embed'}:
            raise ValueError('Unexpected executable element in demo fragment: ' + tag)
        if tag == 'iframe' and (attrs.get('sandbox') != '' or attrs.get('src') or attrs.get('srcdoc')):
            raise ValueError('Initial demo frame must be empty and sandboxed')
        for name, value in attributes:
            if name.lower().startswith('on') or name == 'srcdoc':
                raise ValueError('Inline executable code in demo fragment')
            if name in {'href', 'src', 'action', 'formaction'} and value:
                url = urlsplit(value)
                documentation_link = tag == 'a' and name == 'href' and url.scheme == 'https' and url.netloc == 'pdftoolkit.github.io' and not url.username and not url.password
                if not value.startswith(('{{ASSET_ROOT}}', '#')) and not documentation_link:
                    raise ValueError('Demo fragment runtime URLs must stay inside the selected assets')


class DemoGallery:
    route = 'modules/to-html/demo/index.html'
    prefix = 'assets/html-demo/'
    manifest_name = 'demo-manifest.json'

    def __init__(self, source: DemoSource, source_root: Path, build_root: Path, html_package: dict):
        self.source = source
        self.source_root = source_root
        self.build_root = build_root
        self.html_package = {key: html_package[key] for key in ('version', 'revision')}
        self.manifest = self.read_json(build_root / self.manifest_name)
        if self.manifest.get('schemaVersion') != 1 or self.manifest.get('htmlPackage') != self.html_package:
            raise ValueError('Demo build does not use the selected released HTML package')
        self.validate_application(self.manifest, source)
        self.artifacts = self.inventory(self.manifest.get('assets'))
        self.gallery_path = self.manifest.get('gallery')
        if self.gallery_path != 'gallery/gallery-manifest.json' or self.gallery_path not in self.artifacts:
            raise ValueError('Missing bounded demo gallery manifest')
        self.gallery = self.read_json(self.artifacts[self.gallery_path].verify(build_root))
        self.validate_gallery()
        self.validate_runtime()
        self.script_hashes = self.trusted_script_hashes(self.manifest)
        for path in ('app.js', 'app.css', 'assets/conversion-worker.js'):
            if path not in self.artifacts:
                raise ValueError('Missing browser demo application asset: ' + path)
        self.fragments = {}
        for language in ('en', 'fr'):
            path = source_root / 'public' / ('fragment.' + language + '.html')
            if path.is_symlink() or path.stat().st_size > 256 * 1024:
                raise ValueError('Invalid demo fragment source')
            fragment = path.read_text(encoding='utf-8')
            DemoFragment(fragment)
            self.fragments[language] = fragment
        actual = {path.relative_to(build_root).as_posix() for path in build_root.rglob('*') if path.is_file()}
        if actual - {self.manifest_name, 'index.html', 'fr/index.html'} != set(self.artifacts):
            raise ValueError('Demo inventory must cover every build asset exactly once')

    @staticmethod
    def validate_application(manifest: dict, source: DemoSource) -> None:
        expected = {'repository': source.repository, 'version': source.version, 'revision': source.revision, 'draft': False}
        if manifest.get('application') != expected:
            raise ValueError('Demo build must identify the exact published application, never a draft')
        if manifest.get('runtime') != 'assets/runtime-manifest.json' or manifest.get('worker') != 'assets/conversion-worker.js':
            raise ValueError('Demo runtime must use its bounded local entry points')

    @staticmethod
    def read_json(path: Path) -> dict:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 4 * 1024 * 1024:
            raise ValueError('Missing or oversized demo manifest')
        value = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(value, dict):
            raise ValueError('Demo manifest must be an object')
        return value

    @staticmethod
    def inventory(records: list[dict]) -> dict[str, DemoArtifact]:
        if not isinstance(records, list) or not 1 <= len(records) <= 4096:
            raise ValueError('Missing or oversized demo artifact inventory')
        artifacts = {}
        for record in records:
            artifact = DemoArtifact.parse(record)
            if artifact.path in artifacts:
                raise ValueError('Duplicate demo artifact path: ' + artifact.path)
            artifacts[artifact.path] = artifact
        if sum(item.bytes for item in artifacts.values()) > 512 * 1024 * 1024:
            raise ValueError('Demo artifacts exceed the publication size limit')
        return artifacts

    def validate_gallery(self) -> None:
        if self.gallery.get('schemaVersion') != 1 or self.gallery.get('htmlPackage') != self.html_package or self.gallery.get('draft') is not False:
            raise ValueError('Gallery package provenance differs from the selected release')
        browser = self.gallery.get('browserPreview', {})
        if browser.get('engine') != 'chromium' or not re.fullmatch(r'[0-9]+(?:\.[0-9]+){1,3}', browser.get('version', '')) or type(browser.get('viewportWidth')) is not int or not 320 <= browser['viewportWidth'] <= 8192:
            raise ValueError('HTML previews must retain their actual Chromium capture provenance')
        generator = self.gallery.get('generator', {})
        if generator.get('package') != 'pdftoolkit/pdf-to-html-demo' or generator.get('version') != self.source.version or generator.get('commit') != self.source.revision:
            raise ValueError('Gallery generator differs from the selected demo release')
        cases = self.gallery.get('cases')
        if not isinstance(cases, list) or not 1 <= len(cases) <= 64:
            raise ValueError('Missing or oversized demo case inventory')
        gallery_assets = self.inventory(self.gallery.get('assets'))
        for path, artifact in gallery_assets.items():
            global_asset = self.artifacts.get('gallery/' + path)
            if global_asset is None or global_asset.record() != artifact.record('gallery/'):
                raise ValueError('Gallery asset differs from the complete demo inventory: ' + path)
        seen = set()
        for case in cases:
            if not isinstance(case, dict):
                raise ValueError('Demo case must be an object')
            identifier = case.get('id', '')
            if not re.fullmatch(r'[a-z][a-z0-9-]{0,63}', identifier) or identifier in seen:
                raise ValueError('Invalid or duplicate demo case identifier')
            seen.add(identifier)
            for key in ('title', 'description'):
                labels = case.get(key, {})
                if set(labels) != {'en', 'fr'} or any(not isinstance(value, str) or not value.strip() or len(value) > 4096 for value in labels.values()):
                    raise ValueError('Demo cases require complete bilingual text: ' + identifier)
            if case.get('profile') not in {'basic', 'reset', 'signature', 'rendering'}:
                raise ValueError('Unsupported demo profile: ' + identifier)
            observations = case.get('observations', {})
            if set(observations) != {'en', 'fr'} or any(not isinstance(items, list) or len(items) > 32 or any(not isinstance(item, str) or not item.strip() or len(item) > 4096 for item in items) for items in observations.values()):
                raise ValueError('Demo observations require complete bilingual text')
            origin = case.get('source', {})
            if origin.get('kind') == 'generated':
                expected_source = {'package': 'pdftoolkit/pdf-to-html-demo', 'version': self.source.version, 'commit': self.source.revision}
            elif origin.get('kind') == 'published-fixture':
                expected_source = {'package': 'pdftoolkit/pdf-to-html', 'version': self.html_package['version'], 'commit': self.html_package['revision']}
            else:
                raise ValueError('Invalid demo case source kind')
            source_path = origin.get('path', '')
            if any(origin.get(key) != value for key, value in expected_source.items()) or not re.fullmatch(r'[A-Za-z0-9_-][A-Za-z0-9_./-]*', source_path) or '..' in PurePosixPath(source_path).parts or str(PurePosixPath(source_path)) != source_path:
                raise ValueError('Demo case source differs from its released provenance')
            files = case.get('files', {})
            for role, media in (('pdf', 'application/pdf'), ('html', 'text/plain'), ('preview', 'image/png'), ('htmlPreview', 'image/png'), ('code', 'text/plain'), ('diagnostics', 'application/json')):
                artifact = DemoArtifact.parse(files.get(role, {}))
                if gallery_assets.get(artifact.path) != artifact or artifact.mediaType != media:
                    raise ValueError('Missing or inconsistent demo case file: ' + identifier + '/' + role)
            html_preview = DemoArtifact.parse(files['htmlPreview'])
            html_preview.verify_png(self.build_root / 'gallery', files['htmlPreview'].get('width'), files['htmlPreview'].get('height'))
            if not files['html']['path'].endswith('.html.txt') or not files['code']['path'].endswith('.php.txt'):
                raise ValueError('Demo HTML and PHP source must be published as plain text')
            pages = case.get('pages')
            if not isinstance(pages, list) or not 1 <= len(pages) <= 128:
                raise ValueError('Demo case must preserve all rendered preview pages')
            for page in pages:
                artifact = DemoArtifact.parse(page)
                if gallery_assets.get(artifact.path) != artifact or artifact.mediaType != 'image/png' or any(type(page.get(dimension)) is not int or not 0 < page[dimension] <= 32768 for dimension in ('width', 'height')):
                    raise ValueError('Invalid demo preview page')
                artifact.verify_png(self.build_root / 'gallery', page['width'], page['height'])
            for item in files.get('assets', []):
                artifact = DemoArtifact.parse(item)
                if gallery_assets.get(artifact.path) != artifact:
                    raise ValueError('Demo derived asset differs from the gallery inventory')
            if files['preview']['path'] != pages[0]['path']:
                raise ValueError('Demo card must use the first rendered PDF page')
        for artifact in self.artifacts.values():
            path = artifact.verify(self.build_root)
            if artifact.mediaType == 'application/pdf' and not path.read_bytes().startswith(b'%PDF-'):
                raise ValueError('Invalid demo PDF: ' + artifact.path)
            if artifact.mediaType == 'image/png' and not path.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):
                raise ValueError('Invalid demo PNG: ' + artifact.path)

    def trusted_script_hashes(self, manifest: dict) -> tuple[str, ...]:
        hashes = set()
        for case in self.gallery['cases']:
            if case['profile'] != 'reset':
                continue
            for record in case['files'].get('assets', []):
                if record.get('mediaType') not in {'text/javascript', 'application/javascript'}:
                    continue
                artifact = DemoArtifact.parse(record)
                if PurePosixPath(artifact.path).name != 'pdf-script-' + artifact.sha256 + '.js':
                    raise ValueError('Trusted reset scripts must retain their content-addressed library identity')
                artifact.verify(self.build_root / 'gallery')
                hashes.add('sha256-' + base64.b64encode(bytes.fromhex(artifact.sha256)).decode('ascii'))
        expected = tuple(sorted(hashes))
        if manifest.get('trustedScriptHashes') != list(expected):
            raise ValueError('Trusted script hashes must exactly match the verified reset gallery assets')
        return expected

    def validate_runtime(self) -> None:
        path = 'assets/runtime-manifest.json'
        if path not in self.artifacts:
            raise ValueError('Missing inventoried browser runtime manifest')
        runtime = self.read_json(self.artifacts[path].verify(self.build_root))
        if runtime.get('schema') != 1 or runtime.get('phpIntegerBytes') != 8:
            raise ValueError('The demo requires its declared 64-bit PHP runtime')
        for key, maximum in (('maximumInputBytes', 8 * 1024 * 1024), ('maximumDurationMs', 30000), ('phpMemoryLimitBytes', 128 * 1024 * 1024)):
            if type(runtime.get(key)) is not int or not 0 < runtime[key] <= maximum:
                raise ValueError('Missing or excessive browser runtime limit: ' + key)
        packages = runtime.get('packages', [])
        if not isinstance(packages, list) or len(packages) != 3 or {package.get('name') for package in packages} != {'pdftoolkit/pdf-to-html', 'pdftoolkit/pdf-reader', 'roukmoute/pdf'}:
            raise ValueError('Browser runtime must retain its three locked package identities')
        for package in packages:
            version = package.get('version', '').removeprefix('v')
            revision = package.get('source', {}).get('reference', '')
            if not re.fullmatch(r'\d+\.\d+\.\d+', version) or not re.fullmatch(r'[0-9a-f]{40}', revision) or package.get('dist', {}).get('reference') != revision:
                raise ValueError('Browser runtime dependency must identify a released source and distribution')
            if package['name'] == 'pdftoolkit/pdf-to-html' and {'version': version, 'revision': revision} != self.html_package:
                raise ValueError('Browser runtime differs from the selected HTML package')
        files = runtime.get('files')
        if not isinstance(files, dict) or not 1 <= len(files) <= 4096:
            raise ValueError('Missing bounded browser runtime file inventory')
        for path, record in files.items():
            artifact = self.artifacts.get('assets/' + path)
            if artifact is None or not isinstance(record, dict) or record.get('bytes') != artifact.bytes or record.get('sha256') != artifact.sha256:
                raise ValueError('Browser runtime inventory differs from published bytes: ' + path)
            if set(record) == {'bytes', 'sha256', 'compression', 'decodedBytes', 'decodedSha256'}:
                if record['compression'] != 'gzip' or type(record['decodedBytes']) is not int or not 0 < record['decodedBytes'] <= 128 * 1024 * 1024 or not re.fullmatch(r'[0-9a-f]{64}', record['decodedSha256']):
                    raise ValueError('Invalid compressed browser runtime limits')
                with gzip.open(artifact.verify(self.build_root), 'rb') as stream:
                    decoded = stream.read(record['decodedBytes'] + 1)
                if len(decoded) != record['decodedBytes'] or sha256(decoded).hexdigest() != record['decodedSha256']:
                    raise ValueError('Decoded browser runtime differs from its bounded inventory')
            elif set(record) != {'bytes', 'sha256'}:
                raise ValueError('Unsupported browser runtime integrity record')
        variants = runtime.get('runtimes', {})
        if set(variants) != {'jspi', 'asyncify'}:
            raise ValueError('Browser runtime must retain both supported engine variants')
        for variant in variants.values():
            if set(variant) != {'loader', 'wasm'} or any(path not in files for path in variant.values()):
                raise ValueError('Browser runtime variant must use its inventoried local files')
        application = runtime.get('application')
        if application not in {'runtime/application.zip', 'runtime/application.zip.gz'} or any(path not in files for path in (application, 'runtime/application-manifest.json', 'conversion-worker.js', 'fflate.js')):
            raise ValueError('Browser runtime must inventory its exact local application and entry points')

    def publish(self, output: Path) -> dict:
        if any(output.resolve().is_relative_to(root.resolve()) for root in (self.source_root, self.build_root)):
            raise ValueError('Demo publication must not overwrite its source or build inputs')
        target = output / self.prefix
        if any(parent.is_symlink() for parent in [target, *target.parents] if parent != output.parent):
            raise ValueError('Demo publication must not traverse symbolic links')
        for artifact in self.artifacts.values():
            source = artifact.verify(self.build_root)
            destination = target / artifact.path
            if any(parent.is_symlink() for parent in [destination.parent, *destination.parent.parents] if parent != output.parent):
                raise ValueError('Demo publication must not traverse symbolic links')
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.is_symlink() or destination.exists() and destination.read_bytes() != source.read_bytes():
                raise ValueError('Demo asset collides with an existing output: ' + artifact.path)
            shutil.copyfile(source, destination)
        manifest_file = target / self.manifest_name
        data = (self.build_root / self.manifest_name).read_bytes()
        if manifest_file.exists() and manifest_file.read_bytes() != data:
            raise ValueError('Demo manifest collides with an existing output')
        manifest_file.write_bytes(data)
        return {'source': self.source.manifest(), 'htmlPackage': self.html_package,
                'manifest': self.prefix + self.manifest_name, 'manifestSha256': sha256(data).hexdigest(),
                'gallery': self.prefix + self.gallery_path,
                'cases': [case['id'] for case in self.gallery['cases']],
                'trustedScriptHashes': list(self.script_hashes),
                'browserPreview': self.gallery['browserPreview'],
                'pages': {'en': self.route, 'fr': 'fr/' + self.route},
                'fragments': {language: {'source': 'public/fragment.' + language + '.html',
                                        'sha256': sha256(fragment.encode('utf-8')).hexdigest()}
                              for language, fragment in self.fragments.items()},
                'assets': [artifact.record(self.prefix) for artifact in self.artifacts.values()]}

    @classmethod
    def validate_published(cls, root: Path, record: dict, html_package: dict) -> None:
        source_value = record.get('source', {})
        if source_value.get('schemaVersion') != 1:
            raise ValueError('Missing published demo source identity')
        source = DemoSource(**{key: source_value.get(key, '') for key in ('repository', 'version', 'tag', 'revision')})
        source.validate()
        if record.get('manifest') != cls.prefix + cls.manifest_name or record.get('gallery') != cls.prefix + 'gallery/gallery-manifest.json':
            raise ValueError('Invalid published demo manifest path')
        manifest_file = root / cls.prefix / cls.manifest_name
        value = cls.read_json(manifest_file)
        if sha256(manifest_file.read_bytes()).hexdigest() != record.get('manifestSha256'):
            raise ValueError('Published demo manifest differs from its recorded bytes')
        expected_package = {key: html_package[key] for key in ('version', 'revision')}
        if value.get('schemaVersion') != 1 or value.get('htmlPackage') != expected_package or record.get('htmlPackage') != expected_package:
            raise ValueError('Published demo differs from the selected HTML release')
        cls.validate_application(value, source)
        gallery = cls.__new__(cls)
        gallery.source, gallery.build_root, gallery.html_package = source, root / cls.prefix, expected_package
        gallery.artifacts = cls.inventory(value.get('assets'))
        if value.get('gallery') != 'gallery/gallery-manifest.json' or value['gallery'] not in gallery.artifacts:
            raise ValueError('Missing published gallery manifest')
        gallery.gallery = cls.read_json(gallery.artifacts[value['gallery']].verify(gallery.build_root))
        gallery.validate_gallery()
        gallery.validate_runtime()
        script_hashes = gallery.trusted_script_hashes(value)
        if record.get('trustedScriptHashes') != list(script_hashes):
            raise ValueError('Published reset script hashes differ from the verified gallery')
        expected_assets = [artifact.record(cls.prefix) for artifact in gallery.artifacts.values()]
        if record.get('assets') != expected_assets:
            raise ValueError('Published demo asset inventory differs from its build manifest')
        if record.get('browserPreview') != gallery.gallery['browserPreview']:
            raise ValueError('Published HTML preview provenance differs from the verified gallery')
        if record.get('cases') != [case['id'] for case in gallery.gallery['cases']]:
            raise ValueError('Published demo case inventory differs from its gallery')
        if record.get('pages') != {'en': cls.route, 'fr': 'fr/' + cls.route}:
            raise ValueError('Published demo must have paired English and French routes')
        fragments = record.get('fragments', {})
        if set(fragments) != {'en', 'fr'} or any(fragment.get('source') != 'public/fragment.' + language + '.html' or not re.fullmatch(r'[0-9a-f]{64}', fragment.get('sha256', '')) for language, fragment in fragments.items()):
            raise ValueError('Missing bilingual demo fragment provenance')
        actual = {path.relative_to(gallery.build_root).as_posix() for path in gallery.build_root.rglob('*') if path.is_file()}
        if actual != set(gallery.artifacts) | {cls.manifest_name}:
            raise ValueError('Published demo contains stale or uninventoried assets')

    def body(self, language: str, base: str = '/') -> str:
        if language not in self.fragments or not re.fullmatch(r'(?:/[A-Za-z0-9_.-]+)*/', base):
            raise ValueError('Invalid demo locale or site root')
        asset_root = base + self.prefix
        fragment = self.fragments[language].replace('{{ASSET_ROOT}}', escape(asset_root, quote=True)).replace('{{LANGUAGE}}', language)
        if re.search(r'\{\{[A-Z_]+\}\}', fragment):
            raise ValueError('Unresolved demo fragment placeholder')
        return fragment + self.fallback(language, asset_root)

    def fallback(self, language: str, asset_root: str) -> str:
        title = 'Downloadable examples' if language == 'en' else 'Exemples à télécharger'
        labels = ('Input PDF', 'HTML source', 'PHP example', 'Diagnostics') if language == 'en' else ('PDF source', 'Source HTML', 'Exemple PHP', 'Diagnostics')
        cards = []
        for case in self.gallery['cases']:
            files = case['files']
            url = lambda record: escape(asset_root + 'gallery/' + record['path'], quote=True)
            links = ' · '.join(f'<a href="{url(files[role])}" download>{label}</a>' for role, label in zip(('pdf', 'html', 'code', 'diagnostics'), labels))
            cards.append(f'<article class="card"><img class="card-preview" src="{url(files["preview"])}" alt="{escape(case["title"][language], quote=True)}" loading="lazy"><div class="card-body"><h3>{escape(case["title"][language])}</h3><p>{escape(case["description"][language])}</p><p>{links}</p></div></article>')
        return '<noscript><section><h2>' + title + '</h2><div class="cards">' + ''.join(cards) + '</div></section></noscript>'

    def teaser(self, language: str, base: str, identifiers: tuple[str, ...]) -> str:
        if language not in {'en', 'fr'} or not re.fullmatch(r'(?:/[A-Za-z0-9_.-]+)*/', base):
            raise ValueError('Invalid visual gallery locale or site root')
        labels = {'en': ('See the conversion', 'Source PDF', 'Derived HTML', 'Try this example', 'Download PDF', 'PHP example', 'Open full image'),
                  'fr': ('Voir la conversion', 'PDF source', 'HTML dérivé', 'Essayer cet exemple', 'Télécharger le PDF', 'Exemple PHP', 'Ouvrir l’image entière')}[language]
        selected = {case['id']: case for case in self.gallery['cases']}
        if len(set(identifiers)) != len(identifiers) or any(identifier not in selected for identifier in identifiers):
            raise ValueError('Every guide preview must select a unique published gallery case')
        cards = []
        for identifier in identifiers:
            case = selected[identifier]
            route = base + ('fr/' if language == 'fr' else '') + self.route + '?sample=' + identifier
            url = lambda key: base + self.prefix + 'gallery/' + case['files'][key]['path']
            comparisons = ''.join(f'<figure><a href="{escape(url(key), quote=True)}"><img src="{escape(url(key), quote=True)}" alt="{escape(label + " — " + case["title"][language], quote=True)}" loading="lazy"></a><figcaption>{escape(label)} · <a href="{escape(url(key), quote=True)}">{escape(labels[6])}</a></figcaption></figure>' for key, label in (('preview', labels[1]), ('htmlPreview', labels[2])))
            cards.append(f'<article class="demo-teaser-card" data-demo-case="{identifier}"><h3>{escape(case["title"][language])}</h3><div class="demo-teaser-comparison">{comparisons}</div><p>{escape(case["description"][language])}</p><p class="demo-teaser-links"><a href="{escape(route, quote=True)}">{labels[3]} →</a><a href="{escape(url("pdf"), quote=True)}" download>{labels[4]}</a><a href="{escape(url("code"), quote=True)}" download>{labels[5]}</a></p></article>')
        return '<section class="demo-teaser" aria-label="' + labels[0] + '"><h2>' + labels[0] + '</h2><div class="demo-teaser-cards">' + ''.join(cards) + '</div></section>'

    def head(self, base: str = '/') -> str:
        css = self.artifacts['app.css']
        script = self.artifacts['app.js']
        return f'<link rel="stylesheet" href="{escape(base + self.prefix + css.path)}?v={css.sha256[:12]}"><script type="module" src="{escape(base + self.prefix + script.path)}?v={script.sha256[:12]}"></script>'


class DemoBuild:
    def __init__(self, source: DemoSource, root: Path, python: str, php: str, pdftoppm: str, node: str = "node"):
        self.source, self.root, self.python, self.php, self.pdftoppm, self.node = source, root, python, php, pdftoppm, node

    def run(self, output: Path, html_root: Path, remote: bool = False) -> None:
        self.source.check(self.root, remote)
        subprocess.run([self.python, str(self.root / 'tools/build_demo.py'), '--output', str(output),
                        '--html-source', str(html_root), '--pdftoppm', self.pdftoppm, '--php', self.php,
                        '--node', self.node, '--revision', self.source.revision],
                       cwd=self.root, check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1] / 'resources/demo-source.json')
    parser.add_argument('--github-output', type=Path, required=True)
    arguments = parser.parse_args()
    source = DemoSource.load(arguments.source)
    with arguments.github_output.open('a', encoding='utf-8', newline='\n') as stream:
        stream.write(f'demo_revision={source.revision}\ndemo_version={source.version}\n')
