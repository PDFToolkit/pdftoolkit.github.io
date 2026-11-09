"""Published source identities and stable routes for the native HTML examples."""

from dataclasses import dataclass
from pathlib import PurePosixPath


@dataclass(frozen=True)
class HtmlToPdfExample:
    title: str
    guide: str
    generator: str
    source: str
    anchor: str = ''

    @property
    def route(self):
        return 'modules/from-html/' + self.guide + '.html'

    @property
    def preview(self):
        return 'examples/previews/' + PurePosixPath(self.source).stem + '.png'

    @property
    def pdf_anchor(self):
        return self.anchor or 'resultat-pdf'

    @property
    def source_anchor(self):
        return self.anchor + '-source-html' if self.anchor else 'source-html'

    @property
    def code_anchor(self):
        return self.anchor + '-code-source' if self.anchor else 'code-source'


HTML_TO_PDF_SAMPLES = {
    name: HtmlToPdfExample(title, name, 'examples/generate.php', 'examples/sources/' + name + '.html')
    for name, title in {
        'invoice': 'Facture HTML vers PDF',
        'catalogue': 'Catalogue HTML vers PDF',
        'multipage': 'Document HTML sur plusieurs pages',
        'css1': 'Bordures et cascade CSS1',
    }.items()
}
HTML_TO_PDF_SAMPLES['w3c-css1'] = HtmlToPdfExample(
    'Témoin historique W3C CSS1', 'css1', 'examples/generate-w3c.php',
    'resources/css1/w3c/test5526c.htm', 'w3c-css1')
HTML_TO_PDF_SAMPLES['text-spacing'] = HtmlToPdfExample(
    'Espacements et retraits CSS1', 'css1', 'examples/generate-text-spacing.php',
    'examples/sources/text-spacing.html', 'text-spacing')
HTML_TO_PDF_EXAMPLES = tuple(HTML_TO_PDF_SAMPLES)
HTML_TO_PDF_EXAMPLE_TITLES = {name: sample.title for name, sample in HTML_TO_PDF_SAMPLES.items()}
HTML_TO_PDF_STANDARD_EXAMPLES = tuple(name for name, sample in HTML_TO_PDF_SAMPLES.items()
                                    if sample.generator == 'examples/generate.php')
