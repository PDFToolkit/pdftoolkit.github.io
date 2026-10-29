"""The cheap preflight and rendered language anchors enforce one strict structure."""
from pathlib import Path
import tempfile
import unittest
from build_site import Site, guide_pages
from guide_headings import translated_anchors


class GuideHeadingsTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / 'docs/fr').mkdir(parents=True)
        self.pages = [('pdftoolkit/pdf-images', 'docs/architecture.md', 'modules/images/architecture.html', 'Architecture', 'Images')]
        self.roots = {'pdftoolkit/pdf-images': self.root}
        (self.root / 'docs/architecture.md').write_text('# Images\n\n## PNG\n\n### Profiles\n')
        (self.root / 'docs/fr/architecture.md').write_text('# Images\n\n## PNG\n\n### Profils\n')

    def test_preflight_and_rendering_share_reciprocal_nested_anchor_maps(self):
        site = Site.__new__(Site)
        site.pages, site.package_roots, site.content_root = self.pages, self.roots, self.root
        site.prepare_anchors()
        self.assertEqual(translated_anchors(self.pages, self.roots), site.anchor_maps)
        self.assertEqual({'en': {'png': 'png', 'profiles': 'profils'}, 'fr': {'png': 'png', 'profils': 'profiles'}}, site.anchor_maps[self.pages[0][2]])
        inventory = guide_pages()
        self.assertEqual(len(inventory), len({(owner, source) for owner, source, *_ in inventory}))

    def test_extra_or_relevelled_translated_section_is_rejected(self):
        for text in ('# Images\n\n## PNG\n\n### Profils\n\n## Extra\n', '# Images\n\n## PNG\n\n## Profils\n'):
            with self.subTest(text=text):
                (self.root / 'docs/fr/architecture.md').write_text(text)
                with self.assertRaisesRegex(ValueError, 'Translated heading structure differs: pdftoolkit/pdf-images:docs/architecture.md'):
                    translated_anchors(self.pages, self.roots)

    def test_missing_translation_is_rejected(self):
        (self.root / 'docs/fr/architecture.md').unlink()
        with self.assertRaises(FileNotFoundError):
            translated_anchors(self.pages, self.roots)
