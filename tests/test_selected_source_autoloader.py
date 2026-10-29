"""Exercise actual PHP autoload order against an older consumer's fallback tree."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


class SelectedSourceAutoloaderTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.selected, self.old = self.root / 'selected', self.root / 'old'
        for root in (self.selected, self.old):
            (root / 'Nested').mkdir(parents=True)
        self.helper = Path(__file__).resolve().parents[1] / 'tools/SelectedSourceAutoloader.php'

    def declaration(self, root, name, value):
        path = root / (name.replace('\\', '/') + '.php')
        parts = ('PDF\\Images\\' + name).rsplit('\\', 1)
        path.write_text('<?php namespace ' + parts[0] + '; final class ' + parts[1] + ' { public const SOURCE = ' + json.dumps(value) + '; }')
        return path

    def run_php(self, body):
        script = self.root / 'check.php'
        script.write_text('''<?php
require $argv[1];
spl_autoload_register(static function (string $name): void {
    $path = $GLOBALS['argv'][3] . '/' . str_replace('\\\\', '/', substr($name, strlen('PDF\\\\Images\\\\'))) . '.php';
    if (is_file($path)) require $path;
});
''' + body)
        return subprocess.run([os.environ.get('PDFTOOLKIT_TEST_PHP', 'php'), str(script), str(self.helper), str(self.selected), str(self.old)], capture_output=True, text=True)

    def test_selected_nested_declaration_precedes_older_vendor_and_reflects_exact_file(self):
        selected = self.declaration(self.selected, 'Nested\\Image', 'selected')
        self.declaration(self.old, 'Nested\\Image', 'old')
        result = self.run_php("(new PDF\\Tools\\Documentation\\SelectedSourceAutoloader('PDF\\\\Images\\\\', $argv[2]))->register();\necho json_encode([PDF\\Images\\Nested\\Image::SOURCE, (new ReflectionClass(PDF\\Images\\Nested\\Image::class))->getFileName()]);")
        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertEqual(['selected', str(selected)], json.loads(result.stdout))

    def test_missing_selected_declaration_cannot_fall_back_to_older_vendor(self):
        self.declaration(self.old, 'Missing', 'old')
        result = self.run_php("(new PDF\\Tools\\Documentation\\SelectedSourceAutoloader('PDF\\\\Images\\\\', $argv[2]))->register();\nclass_exists('PDF\\\\Images\\\\Missing');")
        self.assertNotEqual(0, result.returncode)
        self.assertIn('Declaration missing from the selected source', result.stderr + result.stdout)

    def test_incorrect_selected_file_cannot_fall_back_to_older_vendor(self):
        self.declaration(self.old, 'Requested', 'old')
        (self.selected / 'Requested.php').write_text('<?php namespace PDF\\Images; class Different {}')
        result = self.run_php("(new PDF\\Tools\\Documentation\\SelectedSourceAutoloader('PDF\\\\Images\\\\', $argv[2]))->register();\nclass_exists('PDF\\\\Images\\\\Requested');")
        self.assertNotEqual(0, result.returncode)
        self.assertIn('Selected source did not declare the requested symbol', result.stderr + result.stdout)

    def test_already_loaded_older_declaration_is_rejected_before_reflection(self):
        self.declaration(self.old, 'Loaded', 'old')
        result = self.run_php("class_exists('PDF\\\\Images\\\\Loaded');\n(new PDF\\Tools\\Documentation\\SelectedSourceAutoloader('PDF\\\\Images\\\\', $argv[2]))->register();")
        self.assertNotEqual(0, result.returncode)
        self.assertIn('Declarations were loaded before source selection', result.stderr + result.stdout)

    def test_symlink_outside_selected_tree_cannot_supply_a_declaration(self):
        old = self.declaration(self.old, 'Escaped', 'old')
        (self.selected / 'Escaped.php').symlink_to(old)
        result = self.run_php("(new PDF\\Tools\\Documentation\\SelectedSourceAutoloader('PDF\\\\Images\\\\', $argv[2]))->register();\nclass_exists('PDF\\\\Images\\\\Escaped');")
        self.assertNotEqual(0, result.returncode)
        self.assertIn('Declaration missing from the selected source', result.stderr + result.stdout)
