"""Document Images' published tree without changing the core examples' locked inputs."""
from contextlib import redirect_stdout
import io
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import test_opentype_sources as fixtures
import test_reader_sources as reader_fixtures
from build_docs import validate_image_and_font_modules
from check_sources import check, execution_dependencies


class ImagesSourcesTest(unittest.TestCase):
    setUp = fixtures.OpenTypeSourcesTest.setUp
    save_manifest = fixtures.OpenTypeSourcesTest.save_manifest
    save_composer = fixtures.OpenTypeSourcesTest.save_composer
    git = fixtures.OpenTypeSourcesTest.git
    alter = reader_fixtures.ReaderSourcesTest.alter

    def verify(self, images=True):
        with patch('check_sources.git', side_effect=self.git), redirect_stdout(io.StringIO()):
            return check(self.core, self.manifest, opentype_root=self.opentype,
                         pdf_to_html_root=self.html, codecs_root=self.codecs,
                         images_root=self.images if images else None)

    def test_independent_images_release_and_each_execution_lock_keep_distinct_provenance(self):
        self.alter(self.core, 'pdftoolkit/pdf-images', version='0.0.9', source='b' * 40, dist='b' * 40)
        paths = [consumer / 'composer.lock' for consumer in (self.core, self.images, self.html)]
        before = [path.read_bytes() for path in paths]
        packages = self.verify()
        provenance = execution_dependencies(self.core, self.images, self.html, packages)
        self.assertEqual(self.selected['pdftoolkit/pdf-images'], provenance['imagesValidation']['package'])
        self.assertEqual([{'name': 'roukmoute/pdf', 'version': '0.0.1', 'revision': 'a' * 40}], provenance['imagesValidation']['dependencies'])
        image = next(record for record in provenance['coreExamples']['dependencies'] if record['name'] == 'pdftoolkit/pdf-images')
        self.assertEqual({'name': 'pdftoolkit/pdf-images', 'version': '0.0.9', 'revision': 'b' * 40}, image)
        self.assertEqual(before, [path.read_bytes() for path in paths])

    def test_missing_independent_checkout_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'separate released Images checkout'):
            self.verify(False)

    def test_images_head_tag_and_clean_state_are_checked(self):
        for command, error in ((('rev-parse', 'HEAD'), 'Images checkout differs'),
                               (('rev-parse', 'v0.1.0^{commit}'), 'Images tag differs'),
                               (('status', '--porcelain'), 'modified release inputs')):
            def wrong_git(*arguments, root=None):
                return 'f' * 40 if root == self.images and arguments == command else self.git(*arguments, root=root)
            with self.subTest(command=command), patch('check_sources.git', side_effect=wrong_git):
                with self.assertRaisesRegex(ValueError, error):
                    check(self.core, self.manifest, opentype_root=self.opentype,
                          pdf_to_html_root=self.html, codecs_root=self.codecs, images_root=self.images)

    def test_selected_images_identity_and_own_autoloader_are_required(self):
        (self.images / 'vendor/autoload.php').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing Images consumer autoloader'):
            self.verify()
        (self.images / 'vendor/autoload.php').write_text('<?php')
        (self.images / 'composer.json').write_text('{"name":"another/package"}')
        with self.assertRaisesRegex(ValueError, 'Images source package identity differs'):
            self.verify()

    def test_images_own_installation_must_match_its_lock(self):
        self.alter(self.images, 'roukmoute/pdf', version='0.0.2', inventories=('vendor/composer/installed.json',))
        with self.assertRaisesRegex(ValueError, 'differs from its consumer lock'):
            self.verify()

    def test_images_distribution_must_match_its_own_source(self):
        self.alter(self.images, 'roukmoute/pdf', dist='f' * 40)
        with self.assertRaisesRegex(ValueError, 'source/distribution commit'):
            self.verify()

    def test_image_oracles_run_in_selected_checkout_and_preserve_own_autoloader(self):
        args = SimpleNamespace(php='php', qpdf='qpdf', pdftoppm='pdftoppm', image_pdftoppm='image-pdftoppm', imagemagick='convert')
        autoload = self.images / 'vendor/autoload.php'
        before = autoload.read_bytes()
        with patch('build_docs.run') as run:
            validate_image_and_font_modules(args, self.core, self.opentype, self.codecs, self.images, self.root)
        self.assertEqual(['tools/validate_png.py', 'tools/validate_png_color.py', 'tools/validate_jpeg.py'], [call.args[0][1] for call in run.call_args_list[:3]])
        self.assertTrue(all(call.args[1] == self.images for call in run.call_args_list[:3]))
        self.assertEqual(before, autoload.read_bytes())
