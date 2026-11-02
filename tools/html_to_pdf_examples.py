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
HTML_TO_PDF_EXAMPLES = tuple(HTML_TO_PDF_SAMPLES)
HTML_TO_PDF_EXAMPLE_TITLES = {name: sample.title for name, sample in HTML_TO_PDF_SAMPLES.items()}
HTML_TO_PDF_STANDARD_EXAMPLES = tuple(name for name in HTML_TO_PDF_EXAMPLES if name != 'w3c-css1')
