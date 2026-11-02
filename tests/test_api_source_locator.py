"""Inherited parser methods retain dependency provenance, not the module's vendor path."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


class ApiSourceLocatorTest(unittest.TestCase):
    def test_inherited_dependency_sources_are_distinct_from_the_eight_package_inventory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            module = root / 'module'
            dependency = module / 'vendor/masterminds/html5'
            (dependency / 'src/HTML5/Parser').mkdir(parents=True)
            (module / 'src').mkdir()
            external = dependency / 'src/HTML5/Parser/DOMTreeBuilder.php'
            external.write_text('<?php')
            own = module / 'src/BoundedTreeBuilder.php'
            own.write_text('<?php')
            unselected = module / 'vendor/unknown.php'
            unselected.write_text('<?php')
            identity = {'root': str(module), 'repository': 'https://github.com/PDFToolkit/html-to-pdf', 'revision': 'a' * 40, 'version': '0.1.0', 'optional': True}
            identity['externalSources'] = {'masterminds/html5': {**identity, 'root': str(dependency), 'repository': 'https://github.com/Masterminds/html5-php', 'revision': 'b' * 40, 'version': '2.12.0'}}
            manifest = root / 'packages.json'
            manifest.write_text(json.dumps({'pdftoolkit/html-to-pdf': identity}))
            script = root / 'check.php'
            script.write_text('''<?php
require $argv[1];
$locator = new PDF\\Tools\\Documentation\\ApiSourceLocator(json_decode(file_get_contents($argv[2]), true));
try { echo json_encode($locator->locate($argv[3])); }
catch (RuntimeException $error) { fwrite(STDERR, $error->getMessage()); exit(2); }
''')
            helper = Path(__file__).resolve().parents[1] / 'tools/ApiSourceLocator.php'
            def locate(path):
                return subprocess.run([os.environ.get('PDFTOOLKIT_TEST_PHP', 'php'), str(script), str(helper), str(manifest), str(path)], capture_output=True, text=True)
            result = locate(external)
            self.assertEqual(0, result.returncode, result.stderr)
            record = json.loads(result.stdout)
            self.assertEqual('masterminds/html5', record['package'])
            self.assertEqual('b' * 40, record['revision'])
            self.assertEqual('src/HTML5/Parser/DOMTreeBuilder.php', record['source'])
            self.assertEqual('pdftoolkit/html-to-pdf', json.loads(locate(own).stdout)['package'])
            result = locate(unselected)
            self.assertEqual(2, result.returncode)
            self.assertIn('unselected dependency', result.stderr)
