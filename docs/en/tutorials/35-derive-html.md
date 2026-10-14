# Derive semantic HTML from tagged PDF

[English](35-derive-html.md) · [Français](../../tutorials/35-derive-html.md)

A PDF page describes what to paint. Its logical structure describes what the
content means and in which order to read it. The optional `pdftoolkit/pdf-to-html`
module uses that second description to derive HTML according to **Deriving HTML
from PDF 1.2**, the PDF Association publication retained with its source code.

The [PDFToolkit/pdf-to-html repository](https://github.com/PDFToolkit/pdf-to-html/tree/v0.2.0)
was created specifically to implement the rules in this
[reference document](https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.0/resources/reference-documents/Deriving_HTML_from_PDF_1-2.pdf).
Version **0.2.0** distinguishes executable rules, security decisions,
browser adaptations and capabilities supplied by the application. The
[requirements ledger](https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.0/docs/requirements.md)
links the document's clauses to decisions and tests; the
[coverage guide](https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.0/docs/coverage.md)
describes accepted inputs and independent evidence.

This tutorial runs the real `examples/01-derive-tagged-pdf.php` example from the
selected module release. The input PDF, every rendered page, actual HTML output,
JSON diagnostics and complete PHP source appear below. The HTML is produced
during the documentation build; it is not a handwritten substitute for a result.

## Install the optional module

```sh
composer require "pdftoolkit/pdf-to-html:^0.2.0"
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
external `pdf-script-<sha256>.js` assets; example 01 shown here exports none.

Read diagnostics before publishing. A source model capable of representing a
mechanism does not imply that the file adapter accepts every font encoding,
operator, filter or encryption mechanism found in external PDFs.

## Understand the tested rules and choose a profile

Tests cover inverse `ParentTree` associations, namespaces, `ActualText`
replacements, table header/cell relationships and the precedence of explicit
HTML/CSS attributes. A `Lbl` nested inside a `Form` remains associated with the
right field; the `PDF-Page-X` navigation identifier belongs to the parent of
the content actually derived for that page. Pages with no retained content
produce a diagnostic without being assigned another page's content.

The selected profile determines which capabilities to provide:

| Need | Explicit construction |
| --- | --- |
| Reuse headings, text, tables and images | The default semantic profile and inspection of diagnostics. |
| Preserve a complete figure's appearance | `preferVisualFigures: true` and a `ContentRenderer` backed by your application's engine. |
| Restore selected fields to their PDF default values | `FormActionPolicy(allowReset: true)`, without enabling PDF scripts. |
| Export embedded ECMAScript from a trusted document | `allowActiveContent: true`, following the application's trust decision. |

Strict reading rejects inconsistent inverse associations. Permissive reading
reports them; it does not disable cycle checks or budgets. Encrypted PDFs require
an explicit authentication capability, and the receiving HTML viewer must
enforce verified permissions. The
[policies guide](https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.0/docs/policies.md)
explains these objects and their responsibilities.

## Export a figure and supply the rendering engine

[Example 02](https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.0/examples/02-export-figure.php)
reads a tagged PDF, finds a `Figure` and passes its `ContentGroup` to
`GraphicPdfExporter`:

```sh
php examples/02-export-figure.php tests/Fixtures/tagged.pdf figure.pdf
```

The exporter builds a real isolated one-page PDF in memory. It retains the
resources, transformations, clipping and text advances the figure needs while
omitting unselected painting operations. The CLI writes `figure.pdf` and reports
its source page, dimensions in points and SHA-256. The rendering document contains
no catalog actions, AcroForm or scripts from the source document.

To obtain an image in the HTML, supply an object implementing
`GraphicsRasterizer::rasterize(RenderingDocument): ImageContent`. This object
receives the isolated PDF and returns PNG, JPEG or GIF bytes produced by your
engine:

```php
use PDF\Html\DerivationPolicy;
use PDF\Html\HtmlDeriver;
use PDF\Html\PdfToHtml;
use PDF\Html\Rendering\RasterContentRenderer;
use PDF\Reading\FileBytes;

// $rasterizer is the application's explicit GraphicsRasterizer object.
$renderer = new RasterContentRenderer($rasterizer);
$converter = new PdfToHtml(deriver: new HtmlDeriver(
    policy: new DerivationPolicy(preferVisualFigures: true),
    renderer: $renderer,
));
$result = $converter->convert(new FileBytes($pdfBytes), 'chart.pdf');
```

`RasterContentRenderer` connects the exporter and that engine; it preserves the
rendering viewport's logical dimensions independently of raster resolution. The
requested visual profile fails explicitly when its engine is missing or declines
the group. Applications choose installation, isolation and execution limits.
See the [graphics guide](https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.0/docs/graphics.md)
for retained `GraphicProgram` objects and Poppler pixel checks.

## Reset a field group without executing PDF scripts

[Example 03](https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.0/examples/03-safe-form-reset.php)
constructs an object source model and produces a standalone HTML form:

```sh
php examples/03-safe-form-reset.php safe-form-reset.html
```

The `Person.Name` field starts with “Grace Hopper” as `/V` and has “Ada Lovelace”
as `/DV`. The button selects the `Person` group:

```php
use PDF\Html\Forms\FormActionPolicy;
use PDF\Html\Forms\ResetFormAction;

$resetAction = new ResetFormAction(['Person']);
$policy = new \PDF\Html\DerivationPolicy(
    formActions: new FormActionPolicy(allowReset: true),
);
```

In the complete script, this `ResetFormAction` object belongs to the button's
field. Its selection includes `Person.Name` and other descendants of `Person`,
without including `Personality.Name`. `exclude: true` reverses the selection;
an explicitly empty list does not mean “all fields”. An absent `/DV` clears
the value instead of restoring its initial `/V`.

This policy exports only the library-owned form runtime. PDF document, page and
widget scripts remain disabled, and submissions remain disabled too. The example
writes the returned JavaScript beside the HTML. Keep both to try the reset in
your browser; this site's sandboxed preview executes no runtime.

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

The default profile exports no runtime and permits no remote resource loads.
Enabling the library-owned reset behavior is separate from allowing PDF
ECMAScript. The optional field/event bridge covers tested validation,
calculation and page events; it does not implement the complete
Acrobat/ISO 21757-1 API. The requirements ledger and coverage matrix link source
classes, individual tests, HTML5/PDF oracles and Node runtime checks.

MathML fragments retain a checked vocabulary of 192 element names, including
Presentation and Content MathML. Preserved Content/elementary markup does not
guarantee native browser rendering; extended vocabulary produces a diagnostic,
and the package supplies no rendering polyfill or mathematical evaluator.

See the [module architecture](https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.0/docs/architecture.md),
[coverage](https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.0/docs/coverage.md) and
[security guide](https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.0/docs/security.md)
for the model/file/runtime boundaries. Semantic HTML does not automatically
certify accessibility or PDF/UA.
