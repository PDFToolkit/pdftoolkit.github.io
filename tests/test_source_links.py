"""Resolve URL-encoded source filenames against actual package files and pins."""
from pathlib import Path
import sys
import tempfile
import unittest
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from build_site import CORE_PACKAGE, Site


class SourceLinksTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.core = self.root / 'core'
        self.core.mkdir()
        self.site = Site.__new__(Site)
        self.site.language = 'en'
        self.site.base = '/'
        self.site.markdown_routes = {}
        self.site.by_package_source = {}
        self.site.example_sources = {}
        self.site.reference_sources = {}
        self.site.routes = {}
        self.site.anchor_maps = {}
        self.site.package_roots = {CORE_PACKAGE: self.core}
        self.site.packages = {CORE_PACKAGE: {
            'repository': 'https://github.com/PDFToolkit/pdf', 'revision': 'a' * 40,
        }}

    def source_file(self, relative):
        path = self.core / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'%PDF-2.0\n% source-link unit fixture\n')

    def upstream_url(self, relative):
        return 'https://github.com/PDFToolkit/pdf/blob/v0.7.0/' + quote(relative, safe='/')

    def pinned_url(self, relative):
        return 'https://github.com/PDFToolkit/pdf/blob/' + 'a' * 40 + '/' + quote(relative, safe='/')

    def test_supplied_iso_filename_with_encoded_parentheses_resolves_in_both_languages(self):
        relative = 'resources/iso32000-2-bundle/documents/ISO_32000-2_sponsored_EC3(1).pdf'
        self.source_file(relative)
        for language in ['en', 'fr']:
            with self.subTest(language=language):
                self.site.language = language
                self.assertEqual(self.pinned_url(relative) + '?raw=1#page=458', self.site.rewrite_link('docs/en/pdf-2-0-bundle.md', self.upstream_url(relative) + '?raw=1#page=458'))

    def test_spaces_unicode_and_url_delimiters_keep_the_original_filename(self):
        relative = 'resources/guide é (review) #1.pdf'
        self.source_file(relative)
        self.assertEqual(self.pinned_url(relative), self.site.rewrite_link('README.md', self.upstream_url(relative)))

    def test_percent_escapes_in_the_actual_filename_are_decoded_once(self):
        relative = 'resources/ISO%28original%29.pdf'
        self.source_file(relative)
        self.assertEqual(self.pinned_url(relative), self.site.rewrite_link('README.md', self.upstream_url(relative)))

    def test_relative_source_filename_is_decoded_before_filesystem_lookup(self):
        relative = 'resources/ISO(1).pdf'
        self.source_file(relative)
        self.assertEqual(self.pinned_url(relative) + '#page=2', self.site.rewrite_link('docs/guide.md', '../resources/ISO%281%29.pdf#page=2', owner=CORE_PACKAGE))

    def test_encoded_repository_escape_does_not_link_a_real_file_outside_the_package(self):
        (self.root / 'outside.pdf').write_bytes(b'outside the source package')
        for path in ['%2e%2e/outside.pdf', '..%5Coutside.pdf', '%2FC%3A/outside.pdf']:
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'escapes its source package'):
                self.site.rewrite_link('README.md', 'https://github.com/PDFToolkit/pdf/blob/v0.7.0/' + path)

    def test_encoded_relative_escape_is_rejected_after_decoding(self):
        (self.root / 'outside.pdf').write_bytes(b'outside the source package')
        with self.assertRaisesRegex(ValueError, 'escapes its source package'):
            self.site.rewrite_link('docs/guide.md', '%2e%2e/%2e%2e/outside.pdf', owner=CORE_PACKAGE)

    def test_source_link_with_an_unknown_file_still_fails_the_build(self):
        with self.assertRaisesRegex(ValueError, 'Unresolved package source link'):
            self.site.rewrite_link('README.md', self.upstream_url('resources/missing(1).pdf'))


if __name__ == '__main__':
    unittest.main()
