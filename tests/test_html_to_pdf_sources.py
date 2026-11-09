"""Keep HTML-to-PDF sources, generated files and CSS-level guides attributable."""
from contextlib import redirect_stdout
import copy
import hashlib
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import test_opentype_sources as fixtures
import test_reader_sources as reader_fixtures
from build_docs import validate_html_to_pdf_module
from build_site import HTML_TO_PDF_EXAMPLES, MODULES, Site, group_for, publish_html_to_pdf_source
from html_to_pdf_examples import HTML_TO_PDF_SAMPLES, HTML_TO_PDF_STANDARD_EXAMPLES
from check_sources import check, execution_dependencies
from check_site import Document, module_package, validate_html_to_pdf_source
from localization import localized_source, route_for, translate_interface


class HtmlToPdfSourcesTest(unittest.TestCase):
    setUp = fixtures.OpenTypeSourcesTest.setUp
    save_manifest = fixtures.OpenTypeSourcesTest.save_manifest
    save_composer = fixtures.OpenTypeSourcesTest.save_composer
    git = fixtures.OpenTypeSourcesTest.git
    alter = reader_fixtures.ReaderSourcesTest.alter

    def verify(self, selected=True):
        with patch('check_sources.git', side_effect=self.git), redirect_stdout(io.StringIO()):
            return check(self.core, self.manifest, opentype_root=self.opentype,
                         pdf_to_html_root=self.html, codecs_root=self.codecs, images_root=self.images,
                         html_to_pdf_root=self.from_html if selected else None)

    def test_checkout_has_own_release_and_execution_dependencies(self):
        before = (self.core / 'composer.lock').read_bytes()
        packages = self.verify()
        provenance = execution_dependencies(self.core, self.images, self.html, packages, self.from_html)
        self.assertEqual(self.selected['pdftoolkit/html-to-pdf'], provenance['htmlToPdfValidation']['package'])
        dependencies = provenance['htmlToPdfValidation']['dependencies']
        self.assertEqual(8, len(dependencies))
        self.assertIn('masterminds/html5', {item['name'] for item in dependencies})
        self.assertFalse((self.core / 'vendor/pdftoolkit/html-to-pdf').exists())
        self.assertEqual(before, (self.core / 'composer.lock').read_bytes())

    def test_missing_checkout_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'separate released HTML-to-PDF'):
            self.verify(False)

    def test_checkout_tag_and_dirty_source_are_rejected(self):
        for command in [('rev-parse', 'HEAD'), ('rev-parse', 'v0.1.0^{commit}'), ('status', '--porcelain')]:
            def wrong_git(*arguments, root=None):
                return 'f' * 40 if root == self.from_html and arguments == command else self.git(*arguments, root=root)
            with self.subTest(command=command), patch('check_sources.git', side_effect=wrong_git), self.assertRaisesRegex(ValueError, 'HTML-to-PDF checkout'):
                check(self.core, self.manifest, opentype_root=self.opentype, pdf_to_html_root=self.html,
                      codecs_root=self.codecs, images_root=self.images, html_to_pdf_root=self.from_html)

    def test_parser_installation_cannot_substitute_its_published_lock(self):
        self.alter(self.from_html, 'masterminds/html5', source='f' * 40, dist='f' * 40, inventories=('vendor/composer/installed.json',))
        with self.assertRaisesRegex(ValueError, 'differs from its consumer lock'):
            self.verify()

    def test_module_guides_include_css_levels_and_real_examples_in_both_languages(self):
        owner = 'pdftoolkit/html-to-pdf'
        self.assertEqual('creation-html', group_for({'package': owner, 'source': 'src/Converter.php'}))
        self.assertEqual('from-html', MODULES[owner][0])
        self.assertEqual(owner, module_package('from-html'))
        site = Site.__new__(Site)
        site.base = '/'
        for language in ('en', 'fr'):
            site.language = language
            menu = site.module_navigation(owner)
            for page in ('usage', 'coverage', 'css-levels', *(sample.guide for sample in HTML_TO_PDF_SAMPLES.values())):
                self.assertIn(site.url('modules/from-html/' + page + '.html'), menu)
            self.assertEqual('docs/fr/css-levels.md', localized_source(owner, 'docs/css-levels.md', 'fr'))
        self.assertEqual('modules/from-html/reporting.html', route_for('modules/from-html/signalements.html', 'en'))
        self.assertIn('Validation by CSS level', translate_interface(menu))

    def test_generated_downloads_are_inert_and_match_exact_source_pdf_receipt(self):
        source = self.from_html / 'examples/sources'
        source.mkdir(parents=True)
        html = b'<p>Text</p><script>not executed by documentation</script>'
        (source / 'invoice.html').write_bytes(html)
        pdfs = self.root / 'pdfs'
        pdfs.mkdir()
        pdf = b'%PDF-1.7 synthetic unit fixture'
        (pdfs / 'from-html-invoice.pdf').write_bytes(pdf)
        receipt = {'engine': 'native-php', 'documents': {name: {} for name in HTML_TO_PDF_STANDARD_EXAMPLES}}
        receipt['documents']['invoice'] = {'pages': 1, 'bytes': len(pdf), 'sourceSha256': hashlib.sha256(html).hexdigest(), 'pdfSha256': hashlib.sha256(pdf).hexdigest()}
        manifest = pdfs / 'html-to-pdf-manifest.json'
        manifest.write_text(json.dumps(receipt))
        output = self.root / 'site/examples'
        output.mkdir(parents=True)
        package = self.selected['pdftoolkit/html-to-pdf']
        url = package['repository'] + '/blob/' + package['revision'] + '/examples/sources/invoice.html'
        record = {'source': 'examples/generate.php', 'htmlSource': 'examples/sources/invoice.html', 'htmlSourceUrl': url}
        publish_html_to_pdf_source(self.from_html, pdfs, output, 'from-html-invoice', record)
        self.assertEqual(html, (output / 'from-html-invoice.html.txt').read_bytes())
        self.assertFalse((output / 'from-html-invoice.html').exists())
        docs = {'invoice.html': SimpleNamespace(links=[url])}
        validate_html_to_pdf_source(output.parent, 'from-html-invoice', record, package, docs, {'en': 'invoice.html'})
        record['htmlSourceUrl'] = url.replace(package['revision'], 'main')
        with self.assertRaisesRegex(ValueError, 'source identity'):
            validate_html_to_pdf_source(output.parent, 'from-html-invoice', record, package, docs, {'en': 'invoice.html'})
        (source / 'invoice.html').write_bytes(b'modified')
        with self.assertRaisesRegex(ValueError, 'does not match'):
            publish_html_to_pdf_source(self.from_html, pdfs, output, 'from-html-invoice', record)

    def test_oracle_runs_in_selected_checkout_and_retains_all_pages(self):
        output = self.root / 'html-to-pdf-validation'
        (output / 'renders').mkdir(parents=True)
        for name in HTML_TO_PDF_STANDARD_EXAMPLES:
            (output / (name + '.pdf')).write_bytes(b'%PDF-1.7 fixture')
            for page in (1, 2):
                (output / 'renders' / f'{name}-{page}.png').write_bytes(b'PNG fixture')
        (output / 'manifest.json').write_text('{}')
        historical = output / 'w3c'
        (historical / 'validation').mkdir(parents=True)
        (historical / 'test5526c.pdf').write_bytes(b'%PDF-1.7 historical fixture')
        (historical / 'manifest.json').write_text('{}')
        (historical / 'validation/pdf-report.json').write_text('{}')
        (historical / 'validation/native-96dpi.png').write_bytes(b'PNG historical fixture')
        pdfs, previews = self.root / 'pdfs', self.root / 'previews'
        pdfs.mkdir()
        previews.mkdir()
        text = output / 'text-spacing'
        (text / 'validation').mkdir(parents=True)
        (text / 'browser').mkdir()
        (text / 'text-spacing.pdf').write_bytes(b'%PDF-1.7 text fixture')
        for relative in ('manifest.json', 'validation/pdf-report.json', 'browser/browser-report.json'):
            (text / relative).write_text('{}')
        for page in range(1, 4):
            (text / 'validation' / f'native-{page}.png').write_bytes(b'PNG text fixture')
        args = SimpleNamespace(php='php', qpdf='qpdf', pdftoppm='pdftoppm', pdftotext='pdftotext', node='node', demo_root=self.root / 'demo')
        with patch('build_docs.run') as run:
            validate_html_to_pdf_module(args, self.from_html, self.root, pdfs, previews)
        self.assertEqual('tools/check_css_coverage.py', run.call_args_list[0].args[0][1])
        self.assertNotIn('--require-stage', run.call_args_list[0].args[0])
        self.assertEqual(['php', '-d', 'memory_limit=512M', 'examples/generate.php', output], run.call_args_list[1].args[0])
        self.assertEqual(['php', '-d', 'memory_limit=512M', 'examples/generate-w3c.php', historical], run.call_args_list[3].args[0])
        self.assertEqual('tools/validate_w3c_css1.py', run.call_args_list[4].args[0][1])
        self.assertIn(historical / 'test5526c.pdf', run.call_args_list[4].args[0])
        self.assertTrue(all(call.args[1] == self.from_html for call in run.call_args_list))
        self.assertEqual(['php', '-d', 'memory_limit=512M', 'examples/generate-text-spacing.php', text], run.call_args_list[5].args[0])
        self.assertEqual(['node', 'tools/validate_text_spacing.cjs', text / 'browser'], run.call_args_list[6].args[0])
        self.assertEqual(str(args.demo_root / 'node_modules'), run.call_args_list[6].kwargs['env']['NODE_PATH'])
        self.assertEqual('tools/validate_text_spacing.py', run.call_args_list[7].args[0][1])
        self.assertIn(text / 'browser/browser-report.json', run.call_args_list[7].args[0])
        self.assertEqual(2 * len(HTML_TO_PDF_STANDARD_EXAMPLES) + 1 + 3, len(list(previews.glob('*.png'))))
        self.assertEqual(len(HTML_TO_PDF_EXAMPLES), len(list(pdfs.glob('*.pdf'))))

    def test_example_guides_use_one_generated_preview_panel_and_preserve_package_sources(self):
        owner = 'pdftoolkit/html-to-pdf'
        site = Site.__new__(Site)
        site.base = '/'
        site.package_roots = {owner: self.from_html}
        site.markdown_routes = {}
        site.rewrite_link = lambda source, href, package: href
        generator = self.from_html / 'generate.php'
        generator.write_text('<?php // Published generator fixture.')
        css1_panels = {'en': [], 'fr': []}
        for sample in HTML_TO_PDF_EXAMPLES:
            example = 'from-html-' + sample
            definition = HTML_TO_PDF_SAMPLES[sample]
            html_source = self.from_html / definition.source
            html_source.parent.mkdir(parents=True, exist_ok=True)
            html_source.write_text('<p>Fresh source</p>')
            site.example_sources = {example: {'kind': 'html-to-pdf', 'path': generator, 'source': definition.generator,
                'package': owner, 'sourceUrl': 'https://example.test/generate.php', 'htmlSourceUrl': 'https://example.test/' + sample + '.html',
                'htmlSource': definition.source, 'htmlSourceDownload': 'examples/' + example + '.html.txt',
                'generationReceipt': 'examples/' + example + '.manifest.json', 'validationReport': 'examples/' + example + '.validation.json',
                'browserReport': 'examples/' + example + '.browsers.json'}}
            site.pdf_pages = {example: [{'file': example + '-' + str(number) + '.png', 'width': 794, 'height': 1123} for number in (1, 2)]}
            for language in ('en', 'fr'):
                with self.subTest(sample=sample, language=language):
                    site.language = language
                    relative = ('docs/' if language == 'en' else 'docs/fr/') + definition.guide + '.md'
                    source = self.from_html / relative
                    source.parent.mkdir(parents=True, exist_ok=True)
                    previews = [('..' if language == 'en' else '../..') + '/' + sample.preview
                                for sample in HTML_TO_PDF_SAMPLES.values() if sample.guide == definition.guide]
                    original = '# Example\n\n' + '\n\n'.join('![Repository preview](' + preview + ')' for preview in previews) + '\n\nKeep this explanation.\n'
                    source.write_text(original)
                    guide, _ = site.render_markdown(owner, relative)
                    rendered = guide + site.example_panel(example)
                    self.assertIn('Keep this explanation.', guide)
                    self.assertNotIn('<img', guide)
                    self.assertEqual(1, rendered.count('class="pdf-pages"'))
                    self.assertEqual(2, rendered.count('<img '))
                    document = Document(rendered)
                    for number in (1, 2):
                        self.assertEqual(2, document.links.count('/assets/pdf-pages/' + example + '-' + str(number) + '.png'))
                    self.assertIn('/examples/' + example + '.pdf', document.links)
                    if definition.guide == 'css1':
                        css1_panels[language].append(site.example_panel(example))
                    self.assertEqual(original, source.read_text())
                    other = source.with_name('coverage.md')
                    other.write_text(original)
                    other_guide, _ = site.render_markdown(owner, str(other.relative_to(self.from_html)))
                    self.assertIn('<img', other_guide)
        for language, panels in css1_panels.items():
            with self.subTest(combined_css1_panels=language):
                rendered = ''.join(panels)
                if language == 'en':
                    rendered = translate_interface(rendered)
                document = Document(rendered)
                self.assertFalse(document.duplicates)
                self.assertEqual(3, rendered.count('class="pdf-pages"'))
                self.assertTrue({'resultat-pdf', 'source-html', 'code-source', 'w3c-css1',
                                 'w3c-css1-source-html', 'w3c-css1-code-source', 'text-spacing',
                                 'text-spacing-source-html', 'text-spacing-code-source'} <= document.ids)
                self.assertIn('Historical W3C CSS1 sample' if language == 'en' else 'Témoin historique W3C CSS1', rendered)
                self.assertIn('/examples/from-html-w3c-css1.manifest.json', document.links)
                self.assertIn('/examples/from-html-w3c-css1.validation.json', document.links)
                self.assertIn('/examples/from-html-text-spacing.browsers.json', document.links)

    def test_css1_has_a_localized_gallery_card_and_navigation_route(self):
        self.assertEqual(('invoice', 'catalogue', 'multipage', 'css1', 'w3c-css1', 'text-spacing'), HTML_TO_PDF_EXAMPLES)
        site = Site.__new__(Site)
        site.base = '/'
        site.examples = {'from-html-' + name: sample.route for name, sample in HTML_TO_PDF_SAMPLES.items()}
        site.pdf_pages = {'from-html-' + name: [{'file': 'from-html-' + name + '-1.png', 'width': 794, 'height': 1123}] for name in HTML_TO_PDF_EXAMPLES}
        for language in ('en', 'fr'):
            with self.subTest(language=language):
                site.language = language
                cards = site.html_to_pdf_cards()
                if language == 'en':
                    cards = translate_interface(cards)
                document = Document(cards)
                self.assertEqual(6, cards.count('class="card"'))
                self.assertIn(site.url('modules/from-html/css1.html'), document.links)
                self.assertIn(site.url('examples/from-html-css1.pdf'), document.links)
                self.assertIn(site.url('modules/from-html/css1.html') + '#w3c-css1', document.links)
                self.assertIn(site.url('examples/from-html-w3c-css1.pdf'), document.links)
                self.assertIn(site.url('modules/from-html/css1.html') + '#text-spacing', document.links)
                self.assertIn(site.url('examples/from-html-text-spacing.pdf'), document.links)
                self.assertIn('CSS1 text spacing and indentation' if language == 'en' else 'Espacements et retraits CSS1', cards)
                self.assertIn('CSS1 borders and cascade' if language == 'en' else 'Bordures et cascade CSS1', cards)

    def test_a_generation_receipt_without_the_css1_sample_is_incomplete(self):
        pdfs = self.root / 'pdfs'
        pdfs.mkdir()
        (pdfs / 'html-to-pdf-manifest.json').write_text(json.dumps({'engine': 'native-php', 'documents': {name: {} for name in ('invoice', 'catalogue', 'multipage')}}))
        with self.assertRaisesRegex(ValueError, 'receipt is incomplete'):
            publish_html_to_pdf_source(self.from_html, pdfs, self.root, 'from-html-css1', {'source': 'examples/generate.php', 'htmlSource': 'examples/sources/css1.html'})

    def test_historical_source_and_proof_keep_their_generator_bytes_and_page_identity(self):
        name = 'from-html-w3c-css1'
        definition = HTML_TO_PDF_SAMPLES['w3c-css1']
        original = b'<!DOCTYPE html>\r\n<p>Unmodified source bytes</p>\r\n'
        source = self.from_html / definition.source
        source.parent.mkdir(parents=True)
        source.write_bytes(original)
        pdf = b'%PDF-1.7 synthetic historical fixture'
        pdfs = self.root / 'pdfs'
        output = self.root / 'site/examples'
        pdfs.mkdir()
        output.mkdir(parents=True)
        (pdfs / (name + '.pdf')).write_bytes(pdf)
        (output / (name + '.pdf')).write_bytes(pdf)
        receipt = {'engine': 'native-php', 'pages': 1, 'diagnostics': [], 'formControls': 'static-snapshot',
                   'sourceSha256': hashlib.sha256(original).hexdigest(), 'pdfSha256': hashlib.sha256(pdf).hexdigest()}
        preview = output.parent / 'assets/pdf-pages' / (name + '-1.png')
        preview.parent.mkdir(parents=True)
        image = b'PNG unit fixture'
        preview.write_bytes(image)
        report = {'status': 'pass', 'sourceUnmodified': True, 'sourceSha256': receipt['sourceSha256'], 'receipt': receipt,
                  'render': {'file': 'native-96dpi.png', 'dpi': 96, 'sha256': hashlib.sha256(image).hexdigest()}}
        (pdfs / 'html-to-pdf-w3c-manifest.json').write_text(json.dumps(receipt))
        (pdfs / 'html-to-pdf-w3c-validation.json').write_text(json.dumps(report))
        package = self.selected['pdftoolkit/html-to-pdf']
        source_url = package['repository'] + '/blob/' + package['revision'] + '/' + definition.source
        record = {'source': definition.generator, 'htmlSource': definition.source, 'htmlSourceUrl': source_url}
        publish_html_to_pdf_source(self.from_html, pdfs, output, name, record)
        self.assertEqual(original, (output / (name + '.html.txt')).read_bytes())
        document = SimpleNamespace(ids={'w3c-css1'}, links=[source_url, '/' + record['generationReceipt'], '/' + record['validationReport']])
        validate_html_to_pdf_source(output.parent, name, record, package, {'css1.html': document}, {'en': 'css1.html'})
        preview.write_bytes(image + b'modified')
        with self.assertRaisesRegex(ValueError, 'preview differs'):
            validate_html_to_pdf_source(output.parent, name, record, package, {'css1.html': document}, {'en': 'css1.html'})
        preview.write_bytes(image)
        record['source'] = 'examples/generate.php'
        with self.assertRaisesRegex(ValueError, 'provenance'):
            validate_html_to_pdf_source(output.parent, name, record, package, {'css1.html': document}, {'en': 'css1.html'})
        record['source'] = definition.generator
        (output / (name + '.pdf')).write_bytes(pdf + b'modified')
        with self.assertRaisesRegex(ValueError, 'does not bind'):
            validate_html_to_pdf_source(output.parent, name, record, package, {'css1.html': document}, {'en': 'css1.html'})
        report['status'] = 'fail'
        (pdfs / 'html-to-pdf-w3c-validation.json').write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError, 'independent validation'):
            publish_html_to_pdf_source(self.from_html, pdfs, output, name, record)


    def text_spacing_fixture(self):
        """Synthetic evidence binds bytes and page identity, without impersonating a renderer run."""
        name = 'from-html-text-spacing'
        definition = HTML_TO_PDF_SAMPLES['text-spacing']
        original, pdf, font = b'<p>Signed spacing fixture</p>', b'%PDF-1.7 text unit fixture', b'font unit fixture'
        source = self.from_html / definition.source
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(original)
        font_path = self.from_html / 'tests/Fixtures/fonts/NotoSans-Regular.ttf'
        font_path.parent.mkdir(parents=True, exist_ok=True)
        font_path.write_bytes(font)
        pdfs, output = self.root / 'pdfs', self.root / 'site/examples'
        pdfs.mkdir()
        output.mkdir(parents=True)
        (pdfs / (name + '.pdf')).write_bytes(pdf)
        (output / (name + '.pdf')).write_bytes(pdf)
        receipt = {'engine': 'native-php', 'pages': 3, 'diagnostics': [],
                   'sourceSha256': hashlib.sha256(original).hexdigest(), 'pdfSha256': hashlib.sha256(pdf).hexdigest(),
                   'fonts': [{'family': 'Noto Sans (explicit fallback)', 'sha256': hashlib.sha256(font).hexdigest()}]}
        renders = []
        previews = output.parent / 'assets/pdf-pages'
        previews.mkdir(parents=True)
        for number in range(1, 4):
            image = f'PNG unit page {number}'.encode()
            (previews / f'{name}-{number}.png').write_bytes(image)
            renders.append({'file': f'native-{number}.png', 'sha256': hashlib.sha256(image).hexdigest()})
        report = {'status': 'pass', 'receipt': receipt, 'comparisons': 125,
                  'checks': [{'passed': True} for _ in range(125)], 'renders': renders}
        browsers = {'status': 'pass', 'sourceSha256': receipt['sourceSha256'], 'fontSha256': receipt['fonts'][0]['sha256'],
                    'browsers': {engine: {'version': 'unit fixture', 'passed': True, 'comparisons': 43,
                                         'checks': [{'passed': True} for _ in range(43)],
                                         'fontBinding': {'family': 'ExplicitWitness', 'status': 'loaded', 'faces': 1}}
                                 for engine in ('chromium', 'firefox')}}
        for label, contents in [('manifest', receipt), ('validation', report), ('browsers', browsers)]:
            (pdfs / f'html-to-pdf-text-spacing-{label}.json').write_text(json.dumps(contents))
        package = self.selected['pdftoolkit/html-to-pdf']
        url = package['repository'] + '/blob/' + package['revision'] + '/' + definition.source
        record = {'source': definition.generator, 'htmlSource': definition.source, 'htmlSourceUrl': url}
        return SimpleNamespace(name=name, pdfs=pdfs, output=output, receipt=receipt, report=report, browsers=browsers,
                               package=package, record=record, source_url=url, previews=previews)

    def test_text_example_keeps_three_native_pages_and_all_downloadable_evidence(self):
        fixture = self.text_spacing_fixture()
        publish_html_to_pdf_source(self.from_html, fixture.pdfs, fixture.output, fixture.name, fixture.record)
        record = fixture.record
        self.assertEqual(3, record['expectedPages'])
        self.assertEqual(fixture.receipt['fonts'][0]['sha256'], record['fontSha256'])
        document = SimpleNamespace(ids={'text-spacing'}, links=[fixture.source_url] +
                                   ['/' + record[key] for key in ('generationReceipt', 'validationReport', 'browserReport')])
        validate_html_to_pdf_source(fixture.output.parent, fixture.name, record, fixture.package,
                                    {'css1.html': document}, {'en': 'css1.html'})
        (fixture.previews / (fixture.name + '-3.png')).write_bytes(b'modified last page')
        with self.assertRaisesRegex(ValueError, 'preview differs'):
            validate_html_to_pdf_source(fixture.output.parent, fixture.name, record, fixture.package,
                                        {'css1.html': document}, {'en': 'css1.html'})

    def test_text_example_rejects_incomplete_or_mismatched_independent_evidence(self):
        fixture = self.text_spacing_fixture()
        mutations = [
            ('manifest', lambda value: value.update(pages=2)),
            ('manifest', lambda value: value.update(pdfSha256='f' * 64)),
            ('manifest', lambda value: value.update(sourceSha256='f' * 64)),
            ('manifest', lambda value: value['fonts'][0].update(sha256='f' * 64)),
            ('validation', lambda value: value.update(status='fail')),
            ('validation', lambda value: value['checks'][0].update(passed=False)),
            ('validation', lambda value: value.update(comparisons=0, checks=[])),
            ('validation', lambda value: value.update(comparisons=1, checks=value['checks'][:1])),
            ('validation', lambda value: value.update(comparisons=124, checks=value['checks'][:-1])),
            ('validation', lambda value: value['renders'].pop()),
            ('validation', lambda value: value['renders'][0].update(file='../native-1.png')),
            ('browsers', lambda value: value['browsers'].pop('firefox')),
            ('browsers', lambda value: value.update(sourceSha256='f' * 64)),
            ('browsers', lambda value: value.update(fontSha256='f' * 64)),
            ('browsers', lambda value: value['browsers']['firefox']['checks'][0].update(passed=False)),
            ('browsers', lambda value: value['browsers']['firefox'].update(comparisons=1, checks=[{'passed': True}])),
            ('browsers', lambda value: value['browsers']['chromium'].update(comparisons=42, checks=value['browsers']['chromium']['checks'][:-1])),
            ('browsers', lambda value: value['browsers']['firefox'].pop('fontBinding')),
            ('browsers', lambda value: value['browsers']['firefox']['fontBinding'].update(family='sans-serif')),
            ('browsers', lambda value: value['browsers']['chromium']['fontBinding'].update(status='unloaded')),
            ('browsers', lambda value: value['browsers']['firefox']['fontBinding'].update(faces=0)),
            ('browsers', lambda value: value['browsers']['firefox']['fontBinding'].update(faces=2)),
            ('browsers', lambda value: value['browsers']['firefox']['fontBinding'].update(faces=True)),
        ]
        originals = {'manifest': fixture.receipt, 'validation': fixture.report, 'browsers': fixture.browsers}
        for label, mutation in mutations:
            with self.subTest(label=label, mutation=mutations.index((label, mutation))):
                changed = copy.deepcopy(originals[label])
                mutation(changed)
                path = fixture.pdfs / f'html-to-pdf-text-spacing-{label}.json'
                path.write_text(json.dumps(changed))
                with self.assertRaisesRegex(ValueError, 'Text-spacing'):
                    publish_html_to_pdf_source(self.from_html, fixture.pdfs, fixture.output, fixture.name, fixture.record)
                path.write_text(json.dumps(originals[label]))
