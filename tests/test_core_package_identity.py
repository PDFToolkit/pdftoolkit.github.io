"""Canonical documentation and historical consumer locks retain separate identities."""
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

import test_opentype_sources as fixtures
from build_site import CORE_PACKAGE, Site, component_route, load_sources
from check_sources import check, core_dependency, execution_dependencies, load_manifest


class CorePackageIdentityTest(unittest.TestCase):
    setUp = fixtures.OpenTypeSourcesTest.setUp
    save_manifest = fixtures.OpenTypeSourcesTest.save_manifest
    save_composer = fixtures.OpenTypeSourcesTest.save_composer
    git = fixtures.OpenTypeSourcesTest.git

    def verify(self):
        with patch('check_sources.git', side_effect=self.git), redirect_stdout(io.StringIO()):
            return check(self.core, self.manifest, opentype_root=self.opentype,
                         pdf_to_html_root=self.html, codecs_root=self.codecs,
                         images_root=self.images, html_to_pdf_root=self.from_html)

    def rename_core(self, consumer, name, paths=('composer.lock', 'vendor/composer/installed.json')):
        for relative in paths:
            path = consumer / relative
            data = json.loads(path.read_text())
            for record in data['packages'] + data.get('packages-dev', []):
                if record['name'] in {'pdftoolkit/pdf', 'roukmoute/pdf'}:
                    record['name'] = name
            path.write_text(json.dumps(data))

    def test_selected_core_requires_canonical_manifest_and_composer_names(self):
        self.verify()
        (self.core / 'composer.json').write_text('{"name":"roukmoute/pdf"}')
        with self.assertRaisesRegex(ValueError, 'canonical package identity'):
            self.verify()
        self.records[0]['name'] = 'roukmoute/pdf'
        self.save_manifest()
        for loader in (load_manifest, load_sources):
            with self.subTest(loader=loader.__name__), self.assertRaisesRegex(ValueError, 'exactly once'):
                loader(self.manifest)

    def test_historical_consumer_names_are_retained_without_rewriting_locks(self):
        for consumer in (self.images, self.html, self.from_html):
            self.rename_core(consumer, 'roukmoute/pdf')
        paths = [consumer / 'composer.lock' for consumer in (self.core, self.images, self.html, self.from_html)]
        before = [path.read_bytes() for path in paths]
        packages = self.verify()
        provenance = execution_dependencies(self.core, self.images, self.html, packages, self.from_html)
        self.assertEqual(CORE_PACKAGE, provenance['coreExamples']['package']['name'])
        for key in ('imagesValidation', 'htmlValidation', 'htmlToPdfValidation'):
            self.assertEqual('roukmoute/pdf', provenance[key]['dependencies'][0]['name'])
        self.assertEqual(before, [path.read_bytes() for path in paths])

    def test_core_installation_name_cannot_silently_differ_from_lock(self):
        self.rename_core(self.images, 'roukmoute/pdf', ('vendor/composer/installed.json',))
        with self.assertRaisesRegex(ValueError, 'name differs from its consumer lock'):
            core_dependency(self.images)

    def test_documented_core_cannot_hide_another_core_in_its_vendor(self):
        for relative in ('composer.lock', 'vendor/composer/installed.json'):
            path = self.core / relative
            original = path.read_text()
            for name in ('pdftoolkit/pdf', 'roukmoute/pdf'):
                data = json.loads(original)
                data['packages'].append({'name': name, 'version': '0.12.1'})
                path.write_text(json.dumps(data))
                with self.subTest(inventory=relative, name=name), self.assertRaisesRegex(ValueError, 'must not install a second core'):
                    self.verify()
            path.write_text(original)

    def test_missing_or_two_core_packages_are_rejected(self):
        for relative in ('composer.lock', 'vendor/composer/installed.json'):
            path = self.images / relative
            original = path.read_text()
            for names in ([], ['pdftoolkit/pdf', 'roukmoute/pdf']):
                data = json.loads(original)
                data['packages'] = [{**data['packages'][0], 'name': name} for name in names]
                path.write_text(json.dumps(data))
                with self.subTest(inventory=relative, names=names), self.assertRaisesRegex(ValueError, 'Exactly one core package identity'):
                    core_dependency(self.images)
            path.write_text(original)

    def test_historical_pdf_dependencies_still_break_independent_module_boundary(self):
        for name in ('pdftoolkit/pdf', 'roukmoute/pdf'):
            self.save_composer({'php': '^8.3', name: '^0.12'})
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'independent from PDF packages'):
                self.verify()

    def test_php_api_identity_contract_rejects_substitution_and_coinstallation(self):
        cases = [
            (['pdftoolkit/pdf'], ['pdftoolkit/pdf'], 'pdftoolkit/pdf'),
            (['roukmoute/pdf'], ['roukmoute/pdf'], 'roukmoute/pdf'),
            (['pdftoolkit/pdf'], ['roukmoute/pdf'], 'rejected'),
            (['pdftoolkit/pdf', 'roukmoute/pdf'], ['pdftoolkit/pdf'], 'rejected'),
            (['pdftoolkit/pdf'], ['pdftoolkit/pdf', 'roukmoute/pdf'], 'rejected'),
            ([], ['pdftoolkit/pdf'], 'rejected'),
            (['pdftoolkit/pdf'], [], 'rejected'),
            (['pdftoolkit/pdf', 'pdftoolkit/pdf'], ['pdftoolkit/pdf'], 'rejected'),
        ]
        input_path = self.root / 'identities.json'
        input_path.write_text(json.dumps([[[{'name': name} for name in locked], [{'name': name} for name in installed]] for locked, installed, _ in cases]))
        script = self.root / 'identities.php'
        script.write_text(r'''<?php
require $argv[1];
$results = [];
foreach (json_decode(file_get_contents($argv[2]), true) as [$locked, $installed]) {
    try { $results[] = (new PDF\Tools\Documentation\CorePackageIdentity($locked, $installed))->name; }
    catch (RuntimeException) { $results[] = 'rejected'; }
}
echo json_encode($results);
''')
        helper = Path(__file__).resolve().parents[1] / 'tools/CorePackageIdentity.php'
        result = subprocess.run([os.environ.get('PDFTOOLKIT_TEST_PHP', 'php'), str(script), str(helper), str(input_path)], capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertEqual([expected for _, _, expected in cases], json.loads(result.stdout))

    def test_canonical_core_retains_existing_api_addresses(self):
        legacy = json.loads((Path(__file__).resolve().parents[1] / 'resources/legacy-site-manifest.json').read_text())
        route = component_route('PDF\\Syntax\\Object\\NameType')
        self.assertIn(route, legacy['pages'])
        site = Site.__new__(Site)
        self.assertEqual('reference/packages/core.html', site.package_route(CORE_PACKAGE))
