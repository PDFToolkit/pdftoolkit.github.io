# Derive semantic HTML from tagged PDF

A PDF page describes what to paint. Its logical structure describes what the
content means and in which order to read it. The optional `pdftoolkit/pdf-to-html`
module uses that second description to derive HTML according to **Deriving HTML
from PDF 1.2**, the PDF Association publication retained with its source code.

This tutorial runs the real `examples/01-derive-tagged-pdf.php` example from the
selected module release. The input PDF, every rendered page, actual HTML output,
JSON diagnostics and complete PHP source appear below. The HTML is produced
during the documentation build; it is not a handwritten substitute for a result.

## Install the optional module

```sh
composer require "pdftoolkit/pdf-to-html:^0.1.0"
```

This installs the core and reader dependencies. Core-only applications acquire
no HTML conversion dependency. PHP 8.3+ with DOM and mbstring is required.

## Supply the PDF and keep each processing step explicit

The executable example receives input and output paths:

```sh
php examples/01-derive-tagged-pdf.php tests/Fixtures/tagged.pdf _build/derived.html
```

The application reads the chosen file and supplies its bytes to `DocumentReader`.
`ReadPdfSource` traverses the supported logical structure and content to build a
`TaggedDocument`. It preserves the distinction between structure, Unicode text,
properties and annotations rather than inferring a document from coordinates.

## Derive the document and inspect diagnostics

`HtmlDeriver` resolves roles and namespaces, derives attributes and content, and
serializes semantic HTML. The result exposes HTML, CSS, assets and diagnostics
explicitly. The script writes the selected output and reports its operation in
JSON. Applications choose storage and publication themselves.

The script also writes **every returned asset beside the HTML**, and reports each
filename, media type and SHA-256. Keep those files with the HTML when copying a
conversion. In application code, persist `$result->assets` explicitly or remap
resource URLs consistently. Trusted scripts, when deliberately enabled, are
external `pdf-script-<sha256>.js` assets; the safe example exports none.

Read diagnostics before publishing. A source model capable of representing a
mechanism does not imply that the file adapter accepts every font encoding,
operator, filter or encryption mechanism found in external PDFs.

## Compare semantic output rather than page layout

Inspect headings, paragraphs and reading order in the HTML preview, then compare
them with the PDF. Browser reflow and PDF pagination have different goals. The
module does not infer missing structure, run OCR or promise pixel-identical output.
The preview is sandboxed without permission to execute scripts or submit forms.

The fixture's red image contains one sample pixel but is painted at **20 PDF
points** on each side. The adapter follows its transformation matrix and derives
**27 × 27 CSS pixels** after rounding, using 96 CSS pixels per 72 PDF points.
This preserves logical size without equating image samples with painted size or
reproducing every PDF positioning/clipping operation.

The default profile exports no script runtime and permits no remote resource
loads. Applications may explicitly supply rendering/authentication capabilities
or enable trusted active content. The opt-in field/event bridge covers common
validation, calculation and reset operations; it does not implement the complete
Acrobat/ISO 21757-1 API. See the module's coverage matrix for the source classes,
individual tests, independent HTML5/PDF oracle and Node runtime harness.

MathML fragments retain a checked vocabulary of 192 element names, including
Presentation and Content MathML. Preserved Content/elementary markup does not
guarantee native browser rendering; extended vocabulary produces a diagnostic,
and the package supplies no rendering polyfill or mathematical evaluator.

See the [module architecture](https://github.com/PDFToolkit/pdf-to-html/blob/v0.1.0/docs/architecture.md),
[coverage](https://github.com/PDFToolkit/pdf-to-html/blob/v0.1.0/docs/coverage.md) and
[security guide](https://github.com/PDFToolkit/pdf-to-html/blob/v0.1.0/docs/security.md)
for the model/file/runtime boundaries. Semantic HTML does not automatically
certify accessibility or PDF/UA.
