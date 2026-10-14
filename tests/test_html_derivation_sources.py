"""Keep HTML outputs distinct from documentation pages and script execution."""
import unittest
import test_opentype_sources as fixtures
from contextlib import redirect_stdout
import io
import hashlib
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
from build_site import MODULES, group_for, publish_derivation_assets
from check_sources import check
from check_site import validate_derived_html
from localization import localized_source, route_for, translate_interface


class HtmlDerivationSourcesTest(unittest.TestCase):
    setUp = fixtures.OpenTypeSourcesTest.setUp
    save_manifest = fixtures.OpenTypeSourcesTest.save_manifest
    save_composer = fixtures.OpenTypeSourcesTest.save_composer
    git = fixtures.OpenTypeSourcesTest.git

    def test_html_checkout_and_its_reader_are_selected_without_changing_core_lock(self):
        with patch('check_sources.git', side_effect=self.git), redirect_stdout(io.StringIO()):
            packages = check(self.core, self.manifest, opentype_root=self.opentype, pdf_to_html_root=self.html)
        self.assertIn('pdftoolkit/pdf-to-html', packages)
        self.assertFalse((self.core / 'vendor/pdftoolkit/pdf-to-html').exists())

    def test_wrong_html_release_commit_is_rejected(self):
        def wrong_git(*arguments, root=None):
            return 'f' * 40 if root == self.html else self.git(*arguments, root=root)
        with patch('check_sources.git', side_effect=wrong_git):
            with self.assertRaisesRegex(ValueError, 'PDF-to-HTML checkout differs'):
                check(self.core, self.manifest, opentype_root=self.opentype, pdf_to_html_root=self.html)

    def test_bilingual_html_guides_and_group(self):
        owner = 'pdftoolkit/pdf-to-html'
        self.assertEqual('to-html', MODULES[owner][0])
        self.assertEqual('conversion-html', group_for({'package': owner, 'source': 'src/HtmlDeriver.php'}))
        self.assertEqual('docs/fr/coverage.md', localized_source(owner, 'docs/coverage.md', 'fr'))
        self.assertEqual('modules/to-html/reporting.html', route_for('modules/to-html/signalements.html', 'en'))
        self.assertIn('HTML derivation', translate_interface('<h2>Architecture de la dérivation HTML</h2>'))


class DerivedHtmlBoundaryTest(unittest.TestCase):
    def test_semantic_html_is_validated_separately(self):
        validate_derived_html('<!doctype html><html lang="en"><head><title>Example</title></head><body><h1>Heading</h1><p>Text &amp; content.</p></body></html>')

    def test_active_content_is_rejected(self):
        for value in ('<script>alert(1)</script>', '<img src=x onerror="alert(1)">', '<a href="javascript:alert(1)">Link</a>', '<iframe srcdoc="test"></iframe>', '<meta http-equiv="refresh" content="0;url=https://example.test">'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_derived_html('<html><body>' + value + '</body></html>')


class DerivedAssetPublicationTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.output = self.root / 'site'
        self.output.mkdir()
        self.html = self.root / 'derived.html'
        self.html.write_bytes(b'<!doctype html><html lang="en"></html>')
        self.report = self.root / 'report.json'
        self.asset = self.root / 'image.png'
        self.asset.write_bytes(b'reproducible asset bytes')
        self.metadata = {'htmlSha256': hashlib.sha256(self.html.read_bytes()).hexdigest(),
                         'assets': [{'filename': self.asset.name, 'mediaType': 'image/png',
                                     'sha256': hashlib.sha256(self.asset.read_bytes()).hexdigest()}]}

    def publish(self):
        self.report.write_text(json.dumps(self.metadata), encoding='utf-8')
        return publish_derivation_assets(self.report, self.html, self.output)

    def test_reported_asset_is_published_with_its_exact_bytes_and_inventory(self):
        assets = self.publish()
        self.assertEqual(self.asset.read_bytes(), (self.output / self.asset.name).read_bytes())
        self.assertEqual('examples/image.png', assets[0]['path'])
        self.assertEqual(self.asset.stat().st_size, assets[0]['bytes'])

    def test_parent_and_duplicate_asset_names_are_rejected(self):
        self.metadata['assets'][0]['filename'] = '../image.png'
        with self.assertRaisesRegex(ValueError, 'filename'):
            self.publish()
        self.metadata['assets'][0]['filename'] = 'image.png'
        self.metadata['assets'].append(dict(self.metadata['assets'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.publish()

    def test_modified_html_asset_and_output_collision_are_rejected(self):
        self.metadata['htmlSha256'] = 'f' * 64
        with self.assertRaisesRegex(ValueError, 'HTML does not match'):
            self.publish()
        self.metadata['htmlSha256'] = hashlib.sha256(self.html.read_bytes()).hexdigest()
        self.metadata['assets'][0]['sha256'] = 'f' * 64
        with self.assertRaisesRegex(ValueError, 'asset does not match'):
            self.publish()
        self.metadata['assets'][0]['sha256'] = hashlib.sha256(self.asset.read_bytes()).hexdigest()
        (self.output / self.asset.name).write_bytes(b'another example')
        with self.assertRaisesRegex(ValueError, 'collides'):
            self.publish()


if __name__ == '__main__':
    unittest.main()
