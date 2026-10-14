"""Regression checks for edition-scoped API presentation without publishing a site."""
import sys
from pathlib import Path
import unittest
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from build_site import Site, LESSONS, group_for
from check_site import Document
from localization import route_for, translate_interface, iso2_description


class Iso2ReferenceTest(unittest.TestCase):
    def site(self):
        site = Site.__new__(Site)
        site.language = 'fr'
        site.base = '/'
        site.routes = {}
        site.iso2_entry_classes = {('29', 'Type'): 'PDF\\Specification\\Iso32000_2\\Dictionary\\CatalogDictionaryTable29\\TypeEntry', ('409a', 'MCAF'): 'PDF\\Specification\\Iso32000_2\\Dictionary\\AssociatedFilesPropertyListTable409a\\MCAFEntry'}
        type_entry = {'name': 'Type', 'type': 'name', 'description': 'Identifies the document catalog.', 'required': True, 'conditional': False, 'pdf_page': 113, 'indirect': False, 'direct': False, 'fixed_name': 'Catalog', 'errata': None}
        mcaf = {'name': 'MCAF', 'type': 'array', 'description': 'Associated file specifications.', 'required': False, 'conditional': False, 'pdf_page': 1015, 'indirect': False, 'direct': False, 'fixed_name': None, 'errata': {'review_status': 'Completed', 'pdf_page': 1015, 'issue_number': 374}}
        site.iso2_tables = {'29': {'title': 'Entries in the catalog dictionary', 'section': '7.7.2', 'pdf_pages': [113, 114, 115, 116, 117], 'entries': [type_entry]}, '409a': {'title': 'Property list entries for associated files', 'section': '14.13.5', 'pdf_pages': [1015], 'entries': [mcaf]}}
        site.iso2_metadata = {'official_references': {'public_errata': 'https://pdf-issues.pdfa.org/32000-2-2020/'}}
        site.iso2_spec_by_name = {'PDF\\Specification\\Iso32000_2\\Dictionary\\CatalogDictionaryTable29': ('29', None), 'PDF\\Document\\Files\\AssociatedFilesPropertyList': ('409a', None)}
        site.adobe_spec_by_name = {}
        site.adobe_tables = {}
        site.spec_by_name = {}
        # A unit-fixture URL, never a package pin or generated public site.
        site.source_url = lambda source: 'https://example.invalid/unit-fixture/' + source
        # ISO1 has a different table29, so accidentally reaching this fallback
        # must fail instead of yielding plausible but false source information.
        site.tables = {'29': {'title': 'Page tree node'}}
        site.spec_entries = lambda table: self.fail('ISO2 presentation reached the ISO1 table fallback')
        return site

    def test_catalog_table29_uses_iso2_before_bare_table_number_fallback(self):
        panel = self.site().spec_panel({'name': 'PDF\\Specification\\Iso32000_2\\Dictionary\\CatalogDictionaryTable29', 'source': 'src/Specification/Iso32000_2/Dictionary/CatalogDictionaryTable29.php', 'constants': [{'name': 'TABLE', 'value': "'29'"}]})
        self.assertEqual([('iso32000-2:2020', '29')], Document(panel).specification_panels)
        self.assertIn('page PDF 113', panel)
        self.assertNotIn('Page tree node', panel)
        self.assertNotIn('downloads/iso-32000-1.pdf', panel)
        self.assertIn('resources/iso32000-2-2020/metadata.json', panel)

    def test_native_mcaf_uses_the_reviewed_iso2_table(self):
        panel = self.site().spec_panel({'name': 'PDF\\Document\\Files\\AssociatedFilesPropertyList', 'source': 'src/Document/Files/AssociatedFilesPropertyList.php', 'constants': [{'name': 'TABLE', 'value': "'409a'"}]})
        self.assertEqual([('iso32000-2:2020', '409a')], Document(panel).specification_panels)
        self.assertIn('page PDF 1015', panel)
        self.assertIn('ISO TC 171 SC 2 WG 8', panel)
        self.assertIn('issues/374', panel)

    def test_unmapped_pilot_class_cannot_receive_a_plausible_iso1_panel(self):
        with self.assertRaisesRegex(ValueError, 'Missing edition-specific pilot provenance'):
            self.site().spec_panel({'name': 'PDF\\Specification\\Iso32000_2\\Unknown', 'source': 'src/Specification/Iso32000_2/Unknown.php', 'constants': [{'name': 'TABLE', 'value': "'29'"}]})

    def test_private_source_has_metadata_and_errata_links_without_pdf_download(self):
        panel = self.site().iso2_spec_panel('29', None)
        links = Document(panel).links
        self.assertTrue(any(link.endswith('/metadata.json') for link in links))
        self.assertTrue(any(link.startswith('https://pdf-issues.pdfa.org/') for link in links))
        self.assertFalse(any(urlsplit(link).path.endswith('.pdf') for link in links))

    def test_new_interface_is_translated_while_edition_attributes_are_preserved(self):
        panel = translate_interface(self.site().iso2_spec_panel('409a', None))
        self.assertEqual([('iso32000-2:2020', '409a')], Document(panel).specification_panels)
        self.assertIn('Source copy retained privately', panel)
        self.assertIn('Physical PDF page', panel)
        self.assertIn('EC3 correction /MCAF', panel)
        self.assertNotIn('Copie source', panel)

    def test_project_authored_entry_summary_is_french_in_the_french_api(self):
        panel = self.site().iso2_spec_panel('29', 'Type')
        self.assertIn('<p lang="fr">Identifie le catalogue du document.</p>', panel)
        self.assertNotIn('Identifies the document catalog.', panel)

    def test_unknown_summary_fallback_preserves_english_without_mislabelling_it(self):
        summary = 'An unreviewed future summary.'
        self.assertEqual((summary, 'en'), iso2_description(summary, 'fr'))
        self.assertEqual((summary, 'en'), iso2_description(summary, 'en'))

    def test_lesson27_routes_and_iso2_group_are_distinct(self):
        lesson = next(item for item in LESSONS if item[3] == 'pdf20-associated-files')
        self.assertEqual('27-pdf20-associated-files', lesson[0])
        self.assertEqual('27-pdf20-fichiers-associes', lesson[1])
        self.assertEqual('fr/tutorials/27-pdf20-fichiers-associes.html', route_for('tutorials/' + lesson[1] + '.html', 'fr'))
        self.assertEqual('iso2', group_for({'package': 'roukmoute/pdf', 'source': 'src/Specification/Iso32000_2/Dictionary/CatalogDictionaryTable29.php'}))


if __name__ == '__main__':
    unittest.main()
