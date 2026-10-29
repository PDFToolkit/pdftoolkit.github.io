"""Published documentation pins and each consumer's lock are distinct identities."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import test_opentype_sources as fixtures
from build_docs import prepare_reader_oracle_autoload
from check_sources import check, html_dependencies, select_reader


class ReaderSourcesTest(unittest.TestCase):
    setUp = fixtures.OpenTypeSourcesTest.setUp
    save_manifest = fixtures.OpenTypeSourcesTest.save_manifest
    save_composer = fixtures.OpenTypeSourcesTest.save_composer
    git = fixtures.OpenTypeSourcesTest.git

    def alter(self, consumer, name, *, version=None, source=None, dist=None, inventories=("composer.lock", "vendor/composer/installed.json")):
        for relative in inventories:
            path = consumer / relative
            data = json.loads(path.read_text())
            for record in data["packages"] + data.get("packages-dev", []):
                if record["name"] == name:
                    if version is not None:
                        record["version"] = version
                    if source is not None:
                        record["source"]["reference"] = source
                    if dist is not None:
                        record["dist"]["reference"] = dist
            path.write_text(json.dumps(data), encoding="utf-8")

    def verify(self):
        with patch("check_sources.git", side_effect=self.git), redirect_stdout(io.StringIO()):
            return check(self.core, self.manifest, opentype_root=self.opentype, pdf_to_html_root=self.html, codecs_root=self.codecs, images_root=self.images)

    def test_core_preferred_when_both_consumers_exactly_match(self):
        self.verify()
        self.assertEqual(self.core, select_reader(self.core, self.html, self.selected))

    def test_html_keeps_its_older_core_and_reader_without_changing_published_locks(self):
        for name in ("roukmoute/pdf", "pdftoolkit/pdf-reader"):
            self.alter(self.html, name, version="v0.0.9", source="a" * 40, dist="a" * 40)
        paths = [root / "composer.lock" for root in (self.core, self.html)]
        before = [path.read_bytes() for path in paths]
        self.verify()
        self.assertEqual(self.core, select_reader(self.core, self.html, self.selected))
        self.assertEqual(["0.0.9", "0.0.9"], [item["version"] for item in html_dependencies(self.html)])
        self.assertEqual(before, [path.read_bytes() for path in paths])

    def test_older_core_reader_uses_exact_html_fallback_and_its_real_autoload(self):
        self.alter(self.core, "pdftoolkit/pdf-reader", version="0.0.9", source="a" * 40, dist="a" * 40)
        self.verify()
        consumer = select_reader(self.core, self.html, self.selected)
        self.assertEqual(self.html, consumer)
        reader = consumer / "vendor/pdftoolkit/pdf-reader"
        prepare_reader_oracle_autoload(reader, consumer)
        self.assertIn(str(self.html / "vendor/autoload.php"), (reader / "vendor/autoload.php").read_text())
        prepare_reader_oracle_autoload(reader, consumer)
        with self.assertRaisesRegex(ValueError, "Refusing to replace"):
            prepare_reader_oracle_autoload(reader, self.core)

    def test_no_candidate_may_substitute_a_different_version_or_commit(self):
        for consumer in (self.core, self.html):
            self.alter(consumer, "pdftoolkit/pdf-reader", version="0.0.9")
        with self.assertRaisesRegex(ValueError, "No installed Reader matches"):
            self.verify()
        for consumer in (self.core, self.html):
            self.alter(consumer, "pdftoolkit/pdf-reader", version="0.1.0", source="f" * 40, dist="f" * 40)
        with self.assertRaisesRegex(ValueError, "No installed Reader matches"):
            self.verify()

    def test_installed_release_must_match_its_actual_lock_even_when_other_candidate_matches(self):
        self.alter(self.core, "pdftoolkit/pdf-reader", version="0.0.9", inventories=("vendor/composer/installed.json",))
        with self.assertRaisesRegex(ValueError, "differs from its consumer lock"):
            self.verify()

    def test_html_runtime_core_cannot_silently_substitute_the_documented_core(self):
        self.alter(self.html, "roukmoute/pdf", version="0.0.9", source="a" * 40, dist="a" * 40,
                   inventories=("composer.lock",))
        with self.assertRaisesRegex(ValueError, "differs from its consumer lock"):
            self.verify()

    def test_dist_reference_is_checked_independently_in_lock_and_installation(self):
        for inventory in ("composer.lock", "vendor/composer/installed.json"):
            with self.subTest(inventory=inventory):
                self.alter(self.html, "pdftoolkit/pdf-reader", dist="f" * 40, inventories=(inventory,))
                with self.assertRaisesRegex(ValueError, "source/distribution commit"):
                    self.verify()
                self.alter(self.html, "pdftoolkit/pdf-reader", dist=self.selected["pdftoolkit/pdf-reader"]["revision"], inventories=(inventory,))

    def test_duplicate_installed_identity_is_rejected(self):
        path = self.html / "vendor/composer/installed.json"
        data = json.loads(path.read_text())
        data["packages"].append(dict(data["packages"][0]))
        path.write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Duplicate Composer"):
            self.verify()

    def test_missing_selected_tree_and_wrong_package_identity_are_rejected(self):
        reader = self.core / "vendor/pdftoolkit/pdf-reader"
        (reader / "src").rmdir()
        with self.assertRaisesRegex(ValueError, "Missing selected Reader source"):
            self.verify()
        (reader / "src").mkdir()
        (reader / "composer.json").write_text('{"name":"some/other-package"}')
        with self.assertRaisesRegex(ValueError, "package identity differs"):
            self.verify()


if __name__ == "__main__":
    unittest.main()
