"""Regression checks for the independent OpenType documentation package."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from build_site import MODULES, Site, group_for, load_sources
from check_sources import PACKAGES, check, load_manifest
from localization import canonical_source, localized_source, route_for, translate_interface


class OpenTypeSourcesTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.core = self.root / "core"
        self.opentype = self.root / "opentype"
        self.core.mkdir()
        self.opentype.mkdir()
        # Synthetic unit fixtures do not identify published source releases.
        self.records = [
            {"name": name, "repository": repository, "version": "0.1.0",
             "revision": str(index) * 40, "optional": name != "roukmoute/pdf"}
            for index, (name, repository) in enumerate(PACKAGES.items(), start=1)
        ]
        self.selected = {item["name"]: item for item in self.records}
        self.manifest = self.root / "sources.json"
        self.save_manifest()
        modules = []
        for item in self.records:
            if item["name"] in {"roukmoute/pdf", "pdftoolkit/opentype"}:
                continue
            modules.append({"name": item["name"], "version": item["version"],
                            "source": {"reference": item["revision"]},
                            "dist": {"reference": item["revision"]}})
            (self.core / "vendor" / item["name"] / "docs").mkdir(parents=True)
        (self.core / "vendor/composer").mkdir()
        (self.core / "composer.lock").write_text(
            json.dumps({"packages": [], "packages-dev": modules}), encoding="utf-8")
        (self.core / "vendor/composer/installed.json").write_text(
            json.dumps({"packages": modules}), encoding="utf-8")
        (self.opentype / "docs").mkdir()
        self.save_composer({"php": "^8.3"})

    def save_manifest(self):
        self.manifest.write_text(json.dumps({"schemaVersion": 1, "packages": self.records}), encoding="utf-8")

    def save_composer(self, requirements):
        (self.opentype / "composer.json").write_text(
            json.dumps({"name": "pdftoolkit/opentype", "require": requirements}), encoding="utf-8")

    def git(self, *arguments, root=None):
        package = "pdftoolkit/opentype" if root == self.opentype else "roukmoute/pdf"
        return self.selected[package]["revision"]

    def test_manifest_requires_all_five_unique_released_package_identities(self):
        self.assertEqual(set(PACKAGES), set(load_manifest(self.manifest)))
        self.assertEqual(set(PACKAGES), set(load_sources(self.manifest)))
        self.records.append(dict(self.records[-1]))
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, "exactly once"):
            load_manifest(self.manifest)
        with self.assertRaisesRegex(ValueError, "exactly once"):
            load_sources(self.manifest)

    def test_opentype_checkout_is_separate_from_core_lock_and_vendor(self):
        with patch("check_sources.git", side_effect=self.git), redirect_stdout(io.StringIO()):
            packages = check(self.core, self.manifest, opentype_root=self.opentype)
        self.assertIn("pdftoolkit/opentype", packages)
        self.assertFalse((self.core / "vendor/pdftoolkit/opentype").exists())

    def test_missing_independent_checkout_is_rejected(self):
        with patch("check_sources.git", side_effect=self.git):
            with self.assertRaisesRegex(ValueError, "independent OpenType source checkout"):
                check(self.core, self.manifest)

    def test_wrong_opentype_release_commit_is_rejected(self):
        def wrong_git(*arguments, root=None):
            return "f" * 40 if root == self.opentype else self.git(*arguments, root=root)
        with patch("check_sources.git", side_effect=wrong_git):
            with self.assertRaisesRegex(ValueError, "OpenType checkout differs"):
                check(self.core, self.manifest, opentype_root=self.opentype)

    def test_wrong_opentype_release_tag_is_rejected(self):
        def wrong_git(*arguments, root=None):
            if root == self.opentype and arguments[-1] != "HEAD":
                return "f" * 40
            return self.git(*arguments, root=root)
        with patch("check_sources.git", side_effect=wrong_git):
            with self.assertRaisesRegex(ValueError, "OpenType tag differs"):
                check(self.core, self.manifest, opentype_root=self.opentype)

    def test_opentype_pdf_dependency_is_rejected(self):
        self.save_composer({"php": "^8.3", "roukmoute/pdf": "^0.6"})
        with patch("check_sources.git", side_effect=self.git):
            with self.assertRaisesRegex(ValueError, "independent from PDF packages"):
                check(self.core, self.manifest, opentype_root=self.opentype)

    def test_api_signatures_link_both_pdf_and_independent_opentype_types(self):
        site = Site.__new__(Site)
        site.language = "en"
        site.base = "/"
        site.routes = {
            "PDF\\Syntax\\Object\\NameType": "reference/components/name.html",
            "PDFToolkit\\OpenType\\Value\\GlyphId": "reference/components/glyph-id.html",
        }
        signature = site.link_type("PDF\\Syntax\\Object\\NameType|PDFToolkit\\OpenType\\Value\\GlyphId|null")
        self.assertIn('href="/reference/components/name.html"', signature)
        self.assertIn('href="/reference/components/glyph-id.html"', signature)
        self.assertTrue(signature.endswith("|null"))

    def test_opentype_has_distinct_api_family_and_bilingual_guides(self):
        owner = "pdftoolkit/opentype"
        self.assertEqual("fontes-opentype", group_for({"package": owner, "source": "src/Layout/GlyphSubstitution.php"}))
        self.assertEqual("opentype", MODULES[owner][0])
        self.assertEqual("docs/fr/coverage.md", localized_source(owner, "docs/coverage.md", "fr"))
        self.assertEqual("docs/coverage.md", canonical_source(owner, "docs/fr/coverage.md"))
        self.assertEqual("modules/opentype/reporting.html", route_for("modules/opentype/signalements.html", "en"))
        self.assertEqual("fr/reference/groups/fontes-opentype.html", route_for("reference/groups/fontes-opentype.html", "fr"))
        self.assertEqual("reference/groups/opentype.html", route_for("reference/groups/fontes-opentype.html", "en"))
        translated = translate_interface("<h2>Modèle objet OpenType indépendant</h2><h3>Substitutions de glyphes</h3>")
        self.assertIn("Independent OpenType object model", translated)
        self.assertIn("Glyph substitutions", translated)


if __name__ == "__main__":
    unittest.main()
