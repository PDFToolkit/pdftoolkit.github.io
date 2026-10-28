"""Executable paths retain their caller meaning when package oracles change cwd."""
from pathlib import Path
import os
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from build_docs import executable_path


class BuildExecutablesTest(unittest.TestCase):
    def test_relative_renderer_is_anchored_before_package_directory_change(self):
        supplied = '_build/poppler/build/utils/pdftoppm'
        original = Path.cwd()
        selected = executable_path(supplied)
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                self.assertEqual(str(original / supplied), selected)
                self.assertTrue(Path(selected).is_absolute())
            finally:
                os.chdir(original)

    def test_virtual_environment_symlink_is_not_resolved_to_base_python(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / 'base-python'
            target.write_bytes(b'fixture interpreter')
            link = root / 'venv/bin/python'
            link.parent.mkdir(parents=True)
            link.symlink_to(target)
            self.assertEqual(str(link), executable_path(link))
            self.assertNotEqual(str(target), executable_path(link))

    def test_path_search_names_and_missing_optional_capability_are_unchanged(self):
        self.assertEqual('php', executable_path('php'))
        self.assertEqual('pdftoppm', executable_path('pdftoppm'))
        self.assertIsNone(executable_path(None))


if __name__ == '__main__':
    unittest.main()
