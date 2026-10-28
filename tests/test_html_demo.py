"""Verify published demo boundaries independently of browser application behavior."""
from copy import deepcopy
import base64
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from html_demo import DemoArtifact, DemoFragment, DemoGallery, DemoSource
from build_site import Site
from check_site import Document
from localization import route_for, translate_interface


class DemoPublicationTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.source = self.root / 'source'
        self.build = self.root / 'build'
        self.output = self.root / 'site'
        (self.source / 'public').mkdir(parents=True)
        self.build.mkdir()
        self.pin = DemoSource('https://github.com/PDFToolkit/pdf-to-html-demo', '0.1.0', 'v0.1.0', 'a' * 40)
        self.html = {'version': '0.6.0', 'revision': 'b' * 40}
        for language in ('en', 'fr'):
            (self.source / 'public' / ('fragment.' + language + '.html')).write_text('<section data-demo-root data-demo-base="{{ASSET_ROOT}}" data-demo-language="{{LANGUAGE}}"><iframe sandbox="" title="Preview"></iframe></section>')
        self.gallery_assets = []
        self.assets = []
        for path, data, media in (
            ('app.js', b'export const app = true;', 'text/javascript'),
            ('app.css', b'.demo-app { display: block; }', 'text/css'),
            ('assets/conversion-worker.js', b'export const worker = true;', 'text/javascript'),
        ):
            self.assets.append(self.asset(path, data, media))
        runtime_files = {}
        for path in ('runtime/application.zip', 'runtime/application-manifest.json', 'fflate.js', 'runtime/jspi/php.js', 'runtime/jspi/php.wasm', 'runtime/asyncify/php.js', 'runtime/asyncify/php.wasm'):
            artifact = self.asset('assets/' + path, b'unit runtime fixture', 'application/octet-stream')
            self.assets.append(artifact)
            runtime_files[path] = {key: artifact[key] for key in ('bytes', 'sha256')}
        worker = self.assets[2]
        runtime_files['conversion-worker.js'] = {key: worker[key] for key in ('bytes', 'sha256')}
        packages = [{'name': name, 'version': 'v0.6.0', 'source': {'reference': 'b' * 40}, 'dist': {'reference': 'b' * 40}} for name in ('pdftoolkit/pdf-to-html', 'pdftoolkit/pdf-reader', 'roukmoute/pdf')]
        self.runtime = {'schema': 1, 'phpIntegerBytes': 8, 'maximumInputBytes': 8 * 1024 * 1024,
                        'maximumDurationMs': 30000, 'phpMemoryLimitBytes': 128 * 1024 * 1024,
                        'packages': packages, 'files': runtime_files, 'application': 'runtime/application.zip',
                        'runtimes': {variant: {'loader': 'runtime/' + variant + '/php.js', 'wasm': 'runtime/' + variant + '/php.wasm'} for variant in ('jspi', 'asyncify')}}
        self.assets.append(self.asset('assets/runtime-manifest.json', json.dumps(self.runtime).encode(), 'application/json'))
        files = {}
        for role, filename, data, media in (
            ('pdf', 'source.pdf', b'%PDF-1.7\nfixture\n', 'application/pdf'),
            ('html', 'result.html.txt', b'<!doctype html><html><body><p>Example</p></body></html>', 'text/plain'),
            ('preview', 'page-1.png', b'\x89PNG\r\n\x1a\n' + b'\x00\x00\x00\rIHDR' + (100).to_bytes(4, 'big') + (200).to_bytes(4, 'big'), 'image/png'),
            ('htmlPreview', 'html-preview.png', b'\x89PNG\r\n\x1a\n' + b'\x00\x00\x00\rIHDR' + (100).to_bytes(4, 'big') + (200).to_bytes(4, 'big'), 'image/png'),
            ('code', 'example.php.txt', b'<?php // an explicitly published example\n', 'text/plain'),
            ('diagnostics', 'diagnostics.json', b'{"status":"converted"}\n', 'application/json'),
        ):
            asset = self.asset('gallery/sample/' + filename, data, media)
            self.assets.append(asset)
            files[role] = {**asset, 'path': 'sample/' + filename}
            self.gallery_assets.append(files[role])
        files['htmlPreview'] = {**files['htmlPreview'], 'width': 100, 'height': 200}
        self.case = {'id': 'sample', 'profile': 'basic',
                     'title': {'en': 'Sample <PDF>', 'fr': 'Exemple <PDF>'},
                     'description': {'en': 'Actual source and result.', 'fr': 'Source et résultat réels.'},
                     'observations': {'en': ['Check the output.'], 'fr': ['Vérifier le résultat.']},
                     'source': {'kind': 'generated', 'package': 'pdftoolkit/pdf-to-html-demo', 'version': '0.1.0', 'commit': 'a' * 40, 'path': 'src/Sample.php'},
                     'files': files, 'pages': [{**files['preview'], 'width': 100, 'height': 200}]}
        self.gallery = {'schemaVersion': 1, 'draft': False, 'htmlPackage': self.html,
                        'browserPreview': {'engine': 'chromium', 'version': '151.0.0.0', 'viewportWidth': 1000},
                        'generator': {'package': 'pdftoolkit/pdf-to-html-demo', 'version': '0.1.0', 'commit': 'a' * 40},
                        'cases': [self.case], 'assets': self.gallery_assets}
        self.save()

    def asset(self, path, data, media):
        output = self.build / path
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
        return {'path': path, 'bytes': len(data), 'sha256': sha256(data).hexdigest(), 'mediaType': media}

    def save(self):
        data = (json.dumps(self.gallery) + '\n').encode()
        artifact = self.asset('gallery/gallery-manifest.json', data, 'application/json')
        assets = [item for item in self.assets if item['path'] != artifact['path']] + [artifact]
        self.manifest = {'schemaVersion': 1, 'htmlPackage': self.html,
                         'application': {'repository': self.pin.repository, 'version': self.pin.version, 'revision': self.pin.revision, 'draft': False},
                         'runtime': 'assets/runtime-manifest.json', 'worker': 'assets/conversion-worker.js', 'trustedScriptHashes': getattr(self, 'trusted_hashes', []),
                         'gallery': 'gallery/gallery-manifest.json', 'assets': assets}
        (self.build / 'demo-manifest.json').write_text(json.dumps(self.manifest) + '\n')

    def load(self):
        return DemoGallery(self.pin, self.source, self.build, self.html)

    def test_exact_publication_bilingual_fallback_and_manifest_revalidation(self):
        gallery = self.load()
        record = gallery.publish(self.output)
        DemoGallery.validate_published(self.output, record, self.html)
        for language in ('en', 'fr'):
            body = gallery.body(language)
            self.assertIn('data-demo-language="' + language + '"', body)
            self.assertIn('/assets/html-demo/gallery/sample/source.pdf', body)
            self.assertIn('<noscript>', body)
            self.assertIn('&lt;PDF&gt;', body)
            self.assertNotIn('<PDF>', body)
        self.assertIn('type="module"', gallery.head())
        self.assertEqual('modules/to-html/demo/index.html', record['pages']['en'])
        self.assertEqual('fr/modules/to-html/demo/index.html', record['pages']['fr'])
        self.assertTrue((self.output / 'assets/html-demo/gallery/sample/result.html.txt').is_file())
        self.assertFalse(any(self.output.rglob('*.html')))

    def test_only_native_demo_pages_receive_worker_and_blob_permissions(self):
        gallery = self.load()
        site = Site.__new__(Site)
        site.base = '/'
        site.translations, site.anchor_maps = {}, {}
        site.docs_revision = 'c' * 40
        site.release, site.module_versions = '0.11.0', '0.6.0'
        site.stylesheet_revision = site.script_revision = 'd' * 12
        output = {}
        site.write = lambda route, value: output.update({route: value})
        for language in ('en', 'fr'):
            site.language = language
            site.page(DemoGallery.route, 'Galerie et démo HTML', 'Dérivation HTML', gallery.body(language), extra_head=gallery.head(), browser_demo=True)
            demo = Document(output[DemoGallery.route])
            self.assertEqual(1, demo.heading_count)
            self.assertEqual([language], demo.languages)
            self.assertIn("worker-src 'self'", demo.policies[0])
            self.assertIn("style-src 'self' data: blob: 'unsafe-inline'", demo.policies[0])
            self.assertEqual('', demo.frames[0]['sandbox'])
            self.assertEqual(2, len(demo.scripts))
            site.page('guides/example.html', 'Example', 'Guides', '<p>Other documentation.</p>')
            ordinary = Document(output['guides/example.html'])
            self.assertNotIn('wasm-unsafe-eval', ordinary.policies[0])
            self.assertNotIn('blob:', ordinary.policies[0])
            self.assertEqual(1, len(ordinary.scripts))

    def test_guides_compare_verified_pdf_and_html_previews_without_scripts(self):
        gallery = self.load()
        for language in ('en', 'fr'):
            teaser = gallery.teaser(language, '/', ('sample',))
            document = Document(teaser)
            self.assertEqual([], document.scripts)
            self.assertIn('/assets/html-demo/gallery/sample/page-1.png', document.links)
            self.assertIn('/assets/html-demo/gallery/sample/html-preview.png', document.links)
            self.assertIn('/' + ('fr/' if language == 'fr' else '') + DemoGallery.route + '?sample=sample', document.links)
            self.assertIn('/assets/html-demo/gallery/sample/example.php.txt', document.links)
        with self.assertRaisesRegex(ValueError, 'unique published'):
            gallery.teaser('en', '/', ('not-in-the-release',))
        self.case['files']['htmlPreview']['width'] = 201
        self.save()
        with self.assertRaisesRegex(ValueError, 'dimensions differ'):
            self.load()

    def test_modified_bytes_and_stale_output_are_rejected(self):
        gallery = self.load()
        record = gallery.publish(self.output)
        (self.output / 'assets/html-demo/app.js').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'Modified demo artifact'):
            DemoGallery.validate_published(self.output, record, self.html)
        (self.build / 'unexpected.txt').write_text('not declared')
        with self.assertRaisesRegex(ValueError, 'cover every build asset'):
            self.load()

    def test_missing_locale_duplicate_case_and_wrong_package_are_rejected(self):
        original = deepcopy(self.gallery)
        self.case['title'].pop('fr')
        self.save()
        with self.assertRaisesRegex(ValueError, 'bilingual'):
            self.load()
        self.gallery = deepcopy(original)
        self.gallery['cases'].append(deepcopy(self.gallery['cases'][0]))
        self.save()
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.load()
        self.gallery = deepcopy(original)
        self.gallery['htmlPackage'] = {'version': '0.6.0', 'revision': 'c' * 40}
        self.save()
        with self.assertRaisesRegex(ValueError, 'provenance'):
            self.load()

    def test_missing_case_file_and_tampered_inventory_are_rejected(self):
        self.case['files']['pdf'] = {**self.case['files']['pdf'], 'sha256': 'f' * 64}
        self.save()
        with self.assertRaisesRegex(ValueError, 'case file'):
            self.load()
        self.case['files']['pdf'] = self.gallery_assets[0]
        self.gallery_assets[0]['sha256'] = 'f' * 64
        self.save()
        with self.assertRaisesRegex(ValueError, 'complete demo inventory'):
            self.load()

    def test_symlinks_and_output_collisions_are_rejected(self):
        gallery = self.load()
        target = self.output / 'assets/html-demo/app.js'
        target.parent.mkdir(parents=True)
        target.write_text('other asset')
        with self.assertRaisesRegex(ValueError, 'collides'):
            gallery.publish(self.output)
        source = self.build / 'app.js'
        original = source.read_bytes()
        source.unlink()
        external = self.root / 'external.js'
        external.write_bytes(original)
        source.symlink_to(external)
        with self.assertRaisesRegex(ValueError, 'Symbolic links'):
            self.load()

    def test_draft_provenance_and_runtime_package_substitution_are_rejected(self):
        self.manifest['application']['draft'] = True
        (self.build / 'demo-manifest.json').write_text(json.dumps(self.manifest))
        with self.assertRaisesRegex(ValueError, 'never a draft'):
            self.load()
        self.runtime['packages'][0]['version'] = 'v0.5.1'
        runtime = self.asset('assets/runtime-manifest.json', json.dumps(self.runtime).encode(), 'application/json')
        self.assets = [record for record in self.assets if record['path'] != runtime['path']] + [runtime]
        self.save()
        with self.assertRaisesRegex(ValueError, 'selected HTML package'):
            self.load()

    def test_reset_permission_is_bound_to_exact_published_script_bytes(self):
        script = b'console.log("bounded reset fixture");'
        digest = sha256(script).hexdigest()
        path = 'sample/pdf-script-' + digest + '.js'
        asset = self.asset('gallery/' + path, script, 'text/javascript')
        self.assets.append(asset)
        record = {**asset, 'path': path}
        self.gallery_assets.append(record)
        self.case['files']['assets'] = [record]
        self.case['profile'] = 'reset'
        self.save()
        with self.assertRaisesRegex(ValueError, 'Trusted script hashes'):
            self.load()
        self.trusted_hashes = ['sha256-' + base64.b64encode(bytes.fromhex(digest)).decode()]
        self.save()
        gallery = self.load()
        self.assertEqual(tuple(self.trusted_hashes), gallery.script_hashes)
        published = gallery.publish(self.output)
        self.assertEqual(self.trusted_hashes, published['trustedScriptHashes'])
        DemoGallery.validate_published(self.output, published, self.html)
        self.case['profile'] = 'basic'
        self.save()
        with self.assertRaisesRegex(ValueError, 'Trusted script hashes'):
            self.load()

    def test_compressed_runtime_requires_exact_bounded_decoded_bytes(self):
        decoded = b'unit WebAssembly bytes'
        encoded = gzip.compress(decoded, mtime=0)
        original_path = 'runtime/jspi/php.wasm'
        path = original_path + '.gz'
        (self.build / 'assets' / original_path).unlink()
        asset = self.asset('assets/' + path, encoded, 'application/gzip')
        self.assets = [record for record in self.assets if record['path'] != 'assets/' + original_path] + [asset]
        del self.runtime['files'][original_path]
        self.runtime['files'][path] = {'bytes': len(encoded), 'sha256': sha256(encoded).hexdigest(), 'compression': 'gzip', 'decodedBytes': len(decoded), 'decodedSha256': sha256(decoded).hexdigest()}
        self.runtime['runtimes']['jspi']['wasm'] = path
        def save_runtime():
            runtime = self.asset('assets/runtime-manifest.json', json.dumps(self.runtime).encode(), 'application/json')
            self.assets = [record for record in self.assets if record['path'] != runtime['path']] + [runtime]
            self.save()
        save_runtime()
        self.load()
        self.runtime['files'][path]['decodedSha256'] = 'f' * 64
        save_runtime()
        with self.assertRaisesRegex(ValueError, 'Decoded browser runtime'):
            self.load()

    def test_demo_source_commit_and_preview_dimensions_must_match(self):
        self.case['source']['commit'] = 'c' * 40
        self.save()
        with self.assertRaisesRegex(ValueError, 'released provenance'):
            self.load()
        self.case['source']['commit'] = self.pin.revision
        self.case['pages'][0]['width'] = 999
        self.save()
        with self.assertRaisesRegex(ValueError, 'dimensions differ'):
            self.load()

    def test_fragment_rejects_inline_code_and_privileged_initial_frame(self):
        for fragment in ('<script src="{{ASSET_ROOT}}app.js"></script>', '<img onerror="alert(1)">', '<iframe sandbox="allow-same-origin"></iframe>', '<iframe sandbox="" srcdoc="x"></iframe>', '<img src="https://example.test/a.png">'):
            with self.subTest(fragment=fragment), self.assertRaises(ValueError):
                DemoFragment('<section data-demo-root>' + fragment + '</section>')


class DemoSourceBoundaryTest(unittest.TestCase):
    def test_stable_source_identity_and_annotated_tag_are_required(self):
        source = DemoSource('https://github.com/PDFToolkit/pdf-to-html-demo', '0.1.0', 'v0.1.0', 'a' * 40)
        with patch('html_demo.subprocess.run', side_effect=[SimpleNamespace(stdout='a' * 40), SimpleNamespace(stdout='commit')]):
            with self.assertRaisesRegex(ValueError, 'annotated tag'):
                source.check(Path('/demo'))
        for changed in (dict(version='dev-main'), dict(tag='main'), dict(repository='https://example.test/demo'), dict(revision='main')):
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                DemoSource(**{**source.__dict__, **changed}).validate()

    def test_paths_raw_documents_sizes_and_duplicate_inventory_are_bounded(self):
        base = {'path': 'runtime/app.wasm', 'bytes': 42, 'sha256': 'a' * 64, 'mediaType': 'application/wasm'}
        for path in ('../secret.txt', '/absolute.txt', 'a//b.txt', 'a/./b.txt', 'a/../b.txt', '.hidden', 'raw.html', 'server.php', 'a\\b.txt'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                DemoArtifact.parse({**base, 'path': path})
        with self.assertRaises(ValueError):
            DemoArtifact.parse({**base, 'bytes': 128 * 1024 * 1024 + 1})
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            DemoGallery.inventory([base, base])

    def test_demo_route_is_localized_but_assets_are_shared(self):
        site = Site.__new__(Site)
        site.base = '/'
        for language in ('en', 'fr'):
            site.language = language
            navigation = site.module_navigation('pdftoolkit/pdf-to-html')
            self.assertIn('/' + ('fr/' if language == 'fr' else '') + DemoGallery.route, navigation)
            self.assertEqual('assets/html-demo/app.js', route_for('assets/html-demo/app.js', language))
        self.assertIn('HTML gallery and demo', translate_interface(navigation))


if __name__ == '__main__':
    unittest.main()
