"""Keep optional codecs independent, accurately pinned and visible in both languages."""
from contextlib import redirect_stdout
import io
import json
import unittest
from unittest.mock import patch
import test_opentype_sources as fixtures
from build_site import MODULES, Site, group_for
from check_sources import check
from localization import localized_source, route_for, translate_interface


class CodecSourcesTest(unittest.TestCase):
    setUp = fixtures.OpenTypeSourcesTest.setUp
    save_manifest = fixtures.OpenTypeSourcesTest.save_manifest
    save_composer = fixtures.OpenTypeSourcesTest.save_composer
    git = fixtures.OpenTypeSourcesTest.git

    def verify(self, codecs=True):
        with patch('check_sources.git', side_effect=self.git), redirect_stdout(io.StringIO()):
            return check(self.core, self.manifest, opentype_root=self.opentype,
                         pdf_to_html_root=self.html, codecs_root=self.codecs if codecs else None, images_root=self.images)

    def test_independent_codec_checkout_does_not_require_a_core_dependency(self):
        self.verify()
        self.assertFalse((self.core / 'vendor/pdftoolkit/pdf-codecs').exists())

    def test_missing_checkout_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'independent image codecs checkout'):
            self.verify(False)

    def test_wrong_tag_or_commit_is_rejected(self):
        for reference in ('HEAD', 'v0.1.0^{commit}'):
            def wrong_git(*arguments, root=None):
                return 'f' * 40 if root == self.codecs and arguments[-1] == reference else self.git(*arguments, root=root)
            with self.subTest(reference=reference), patch('check_sources.git', side_effect=wrong_git), redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(ValueError, 'Codecs (checkout|tag) differs'):
                    check(self.core, self.manifest, opentype_root=self.opentype,
                          pdf_to_html_root=self.html, codecs_root=self.codecs, images_root=self.images)

    def test_reader_dependency_is_rejected(self):
        path = self.codecs / 'composer.json'
        data = json.loads(path.read_text())
        data['require']['pdftoolkit/pdf-reader'] = '^0.7'
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'independent from PDFToolkit packages'):
            self.verify()

    def test_bilingual_guides_and_api_type_links(self):
        owner = 'pdftoolkit/pdf-codecs'
        self.assertEqual('codecs-images', group_for({'package': owner, 'source': 'src/DecodedImage.php'}))
        self.assertEqual('codecs', MODULES[owner][0])
        self.assertEqual('docs/fr/jpeg.md', localized_source(owner, 'docs/jpeg.md', 'fr'))
        self.assertEqual('modules/codecs/reporting.html', route_for('modules/codecs/signalements.html', 'en'))
        self.assertIn('JPEG 2000 decoding', translate_interface('<h2>Décodage JPEG 2000</h2>'))
        site = Site.__new__(Site)
        site.language, site.base = 'en', '/'
        site.routes = {'PDFToolkit\\Codecs\\DecodedImage': 'reference/components/decoded-image.html'}
        self.assertIn('href="/reference/components/decoded-image.html"', site.link_type('PDFToolkit\\Codecs\\DecodedImage|null'))
