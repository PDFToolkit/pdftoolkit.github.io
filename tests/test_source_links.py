"""Resolve URL-encoded source filenames against actual package files and pins."""
from pathlib import Path
import sys
import tempfile
import unittest
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from build_site import CORE_PACKAGE, MODULES, Site


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
        self.site.metadata = {'source_path': 'resources/reference-documents/PDF32000_2008.pdf'}
        self.site.adobe_metadata = {'path': 'resources/reference-documents/adobe_supplement_iso32000.pdf'}
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
        return 'https://github.com/PDFToolkit/pdf/blob/v0.7.1/' + quote(relative, safe='/')

    def pinned_url(self, relative):
        return 'https://github.com/PDFToolkit/pdf/blob/' + 'a' * 40 + '/' + quote(relative, safe='/')

    def test_supplied_iso_filename_with_encoded_parentheses_resolves_in_both_languages(self):
        relative = 'resources/reference-documents/ISO_32000-2_sponsored_EC3(1).pdf'
        self.source_file(relative)
        for language in ['en', 'fr']:
            with self.subTest(language=language):
                self.site.language = language
                self.assertEqual(self.pinned_url(relative) + '?raw=1#page=458', self.site.rewrite_link('docs/en/pdf-2-0-bundle.md', self.upstream_url(relative) + '?raw=1#page=458'))

    def test_spaces_unicode_and_url_delimiters_keep_the_original_filename(self):
        relative = 'resources/guide é (review) #1.pdf'
        self.source_file(relative)
        self.assertEqual(self.pinned_url(relative), self.site.rewrite_link('README.md', self.upstream_url(relative)))

    def test_relocated_reference_documents_preserve_public_downloads_in_both_languages(self):
        downloads = {
            'PDF32000_2008.pdf': 'downloads/iso-32000-1.pdf',
            'adobe_supplement_iso32000.pdf': 'downloads/adobe-supplement-iso32000.pdf',
        }
        for filename in ['pdf_17_errata.pdf', 'pdf_reference.pdf', 'pdf_reference1-7_addendum_redaction.pdf', 'pdf_reference_1-7.pdf']:
            path = 'resources/reference-documents/' + filename
            self.site.reference_sources[filename] = {'path': path}
            downloads[filename] = 'downloads/adobe-references/' + filename
        for language in ['en', 'fr']:
            self.site.language = language
            for filename, download in downloads.items():
                with self.subTest(language=language, filename=filename):
                    relative = 'resources/reference-documents/' + filename
                    self.assertEqual('/' + download + '?raw=1#page=4', self.site.rewrite_link('README.md', self.upstream_url(relative) + '?raw=1#page=4'))

    def test_unrelated_source_with_matching_reference_filename_is_not_a_download(self):
        relative = 'examples/fixtures/PDF32000_2008.pdf'
        self.source_file(relative)
        self.assertEqual(self.pinned_url(relative), self.site.rewrite_link('README.md', self.upstream_url(relative)))

    def test_correction_evidence_resolves_relocated_files_in_iso_and_adobe_panels(self):
        self.site.iso2_spec_by_name = {}
        self.site.adobe_spec_by_name = {}
        self.site.spec_by_name = {}
        self.site.tables = {'1': {'title': 'Unit source table', 'pdf_pages': [2], 'section': '1'}}
        self.site.adobe_tables = {}
        self.site.spec_entries = lambda table: []
        self.site.adobe_spec_entries = lambda table: []
        component = {'name': 'UnitSourceTable', 'source': 'src/UnitSourceTable.php', 'constants': [{'name': 'TABLE', 'value': "'1'"}]}
        for language in ['en', 'fr']:
            self.site.language = language
            for path, download in [
                (self.site.metadata['source_path'], '/downloads/iso-32000-1.pdf'),
                (self.site.adobe_metadata['path'], '/downloads/adobe-supplement-iso32000.pdf'),
                ('https://example.invalid/official-errata', 'https://example.invalid/official-errata'),
            ]:
                with self.subTest(language=language, path=path):
                    correction = {'table': '1', 'entry': 'Value', 'rationale': 'Unit correction evidence', 'evidence_url': path + '#page=4', 'evidence_locator': 'Page 4'}
                    self.site.corrections = [correction]
                    iso_panel = self.site.spec_panel(component)
                    self.site.adobe_corrections = [correction]
                    self.site.adobe_tables = self.site.tables
                    adobe_panel = self.site.adobe_spec_panel('1', None)
                    self.site.adobe_tables = {}
                    self.assertIn('href="' + download + '#page=4"', iso_panel)
                    self.assertIn('href="' + download + '#page=4"', adobe_panel)

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
                self.site.rewrite_link('README.md', 'https://github.com/PDFToolkit/pdf/blob/v0.7.1/' + path)

    def test_encoded_relative_escape_is_rejected_after_decoding(self):
        (self.root / 'outside.pdf').write_bytes(b'outside the source package')
        with self.assertRaisesRegex(ValueError, 'escapes its source package'):
            self.site.rewrite_link('docs/guide.md', '%2e%2e/%2e%2e/outside.pdf', owner=CORE_PACKAGE)

    def test_source_link_with_an_unknown_file_still_fails_the_build(self):
        with self.assertRaisesRegex(ValueError, 'Unresolved package source link'):
            self.site.rewrite_link('README.md', self.upstream_url('resources/missing(1).pdf'))

    def register_html_guides(self):
        owner = 'pdftoolkit/pdf-to-html'
        slug, _, guides = MODULES[owner]
        for source, route, _ in guides:
            self.site.markdown_routes[(owner, source)] = f'modules/{slug}/{route}.html'
        return owner, guides

    def test_new_and_historic_html_guides_resolve_to_the_central_site(self):
        _, guides = self.register_html_guides()
        self.assertEqual({'architecture', 'coverage', 'authentication', 'requirements', 'policies', 'graphics', 'signatures', 'security', 'reference'}, {route for _, route, _ in guides})
        for language in ('en', 'fr'):
            self.site.language = language
            for base in ('/', '/pdf/'):
                self.site.base = base
                for source, route, _ in guides:
                    with self.subTest(language=language, base=base, source=source):
                        localized = source.replace('docs/', 'docs/fr/', 1) if language == 'fr' else source
                        upstream = 'https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.0/' + localized
                        expected = base + ('fr/' if language == 'fr' else '') + f'modules/to-html/{route}.html?view=compact'
                        self.assertEqual(expected, self.site.rewrite_link('docs/tutorials/35-derive-html.md', upstream + '?view=compact'))

    def test_html_guide_translation_switch_uses_the_target_language_and_heading(self):
        owner, _ = self.register_html_guides()
        route = 'modules/to-html/requirements.html'
        self.site.anchor_maps[route] = {'en': {'requirements': 'exigences'}, 'fr': {'exigences': 'requirements'}}
        for language, source, target, fragment, expected in [
            ('en', 'docs/requirements.md', 'docs/fr/requirements.md', 'exigences', '/fr/' + route + '#exigences'),
            ('fr', 'docs/fr/requirements.md', 'docs/requirements.md', 'requirements', '/' + route + '#requirements'),
        ]:
            with self.subTest(language=language):
                self.site.language = language
                upstream = 'https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.0/' + target + '#' + fragment
                self.assertEqual(expected, self.site.rewrite_link(source, upstream, owner=owner))


if __name__ == '__main__':
    unittest.main()
