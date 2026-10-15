# Core and optional modules

PDFToolkit separates the PDF model from external-file processing. The
**0.10.0 core**, **0.5.1 PDF reader**, **0.1.11 image/font modules**, independent **0.2.0 OpenType model** and **0.4.2 PDF-to-HTML module**
require PHP 8.3 or later and are checked on PHP 8.3, 8.4 and 8.5.
Core **0.10** and OpenType **0.2** require 64-bit PHP; OpenType remains independent of the
PDF core. The core retains its Composer name `roukmoute/pdf`
after transfer to the organization; new modules use the `pdftoolkit/` prefix.

## The core boundary

The [core](https://github.com/PDFToolkit/pdf) represents the objects and
mechanisms described by **PDF 1.7 / ISO 32000-1:2008** and the
[Adobe level 3 supplement](adobe-supplement.md), plus [PDF 2.0 / ISO 32000-2:2020 EC3](pdf-2-0.md) and its [companion specifications](pdf-2-0-bundle.md): values, references,
dictionaries, streams, operators, pages, fonts, images, functions, writing
and revisions. Definitions retain their PDF names and references to the
Adobe document.

For example, PDF describes `/Width`, `/ColorSpace`, `/SMask`, `/FontFile2`,
`/CIDToGIDMap` and `/ToUnicode` entries. It allows font programs and DCT bytes
to be embedded; it does not define the entire PNG or OpenType format. Their
readers require other specifications and belong to modules. Writing remains
in the core because it produces PDF syntax and structure.

Version 0.4 adds native constructions for AcroForm and FDF fields, logical
structure, color spaces, patterns and all seven shading types, normalized
images, forms, transparency, layers, fonts and CMaps. It also provides LZW
and predictors, ISO and Adobe encryption mechanisms, signatures and
linearization. [Detailed coverage](coverage.md) separates these verified
behaviors from rules still to complete.

Version 0.5 adds revision generations and free lists, updates after
linearization, native navigation, embedded files and collections. Signature
field policies apply to written snapshots, and cryptographic results are
verified before finalization.

| Repository and package | Input | Produced objects or data |
| --- | --- | --- |
| [PDFToolkit/pdf](https://github.com/PDFToolkit/pdf) — `roukmoute/pdf` | PDF objects assembled by the application | PDF file, cross-references and revisions |
| [PDFToolkit/pdf-images](https://github.com/PDFToolkit/pdf-images) — `pdftoolkit/pdf-images` | PNG or JPEG bytes and explicit limits | Color/alpha samples or core DCT representation |
| [PDFToolkit/pdf-fonts](https://github.com/PDFToolkit/pdf-fonts) — `pdftoolkit/pdf-fonts` | TrueType bytes, text and explicit parameters | Embeddable program, metrics and mappings for the core |
| [PDFToolkit/pdf-reader](https://github.com/PDFToolkit/pdf-reader) — `pdftoolkit/pdf-reader` | PDF bytes and reading budgets | Read graph, pages and inherited attributes, references to resolve and encoded or decoded streams |
| [PDFToolkit/opentype](https://github.com/PDFToolkit/opentype) — `pdftoolkit/opentype` | OpenType SFNT bytes and explicit limits | Tables, metrics, Unicode mappings, GSUB substitutions and GPOS positioning |
| [PDFToolkit/pdf-to-html](https://github.com/PDFToolkit/pdf-to-html) — `pdftoolkit/pdf-to-html` | Tagged PDF bytes or an explicit logical source model | Semantic HTML, CSS, assets and diagnostics |

The reader, images and fonts modules depend on the core without depending on one another. PDF-to-HTML additionally depends on the reader. The core knows none of their parsers: an application can directly
construct its PDF objects or feed them through another converter. The object
model is shared, without parallel copies of primitives or a global registry.

The [OpenType model](https://github.com/PDFToolkit/opentype) is independent: it depends on neither the core nor `pdf-fonts`. It analyzes a font into its own objects without constructing PDF dictionaries. The `pdf-fonts` converter remains the entry point for current TrueType embedding in PDF. OpenType 0.2 implements GSUB 1–8, GPOS 1–9, GDEF classes/mark filters/carets and explicit normalized variation coordinates. Its [positioning guide](https://github.com/PDFToolkit/opentype/blob/v0.2.0/docs/positioning.md) explains immutable positioned sequences, device adjustments and native ItemVariationStore interpolation. The [coverage](https://github.com/PDFToolkit/opentype/blob/v0.2.0/docs/coverage.md) retains limits: Unicode shaping/bidi/line breaking, full variable-outline instantiation, CFF/CFF2, additional tables, containers, writing and subsetting remain separate work.

Core 0.8.0 retains PDF 2.0 writing with modern cryptography and PDF MAC, metadata, document parts, encrypted payload wrappers and qualified structure. It adds [executed source rules and reviewed corrections](source-audits.md), conservative native [redaction](tutorials/36-applied-redaction.md) and optional WTPDF XML rich-text comparison. WTPDF remains a partial mechanical audit without certification. Reader authentication and OpenType layout have their own input boundaries; these core changes do not implement PNG/JPEG conversion or variable-font embedding.

## Installing what the application needs

All six packages are available on Packagist:
[core](https://packagist.org/packages/roukmoute/pdf),
[reader](https://packagist.org/packages/pdftoolkit/pdf-reader),
[images](https://packagist.org/packages/pdftoolkit/pdf-images),
[PDF fonts](https://packagist.org/packages/pdftoolkit/pdf-fonts) and
[OpenType](https://packagist.org/packages/pdftoolkit/opentype) and
[PDF to HTML](https://packagist.org/packages/pdftoolkit/pdf-to-html).
Stable constraints are `roukmoute/pdf:^0.10.0` for the core and
`pdftoolkit/pdf-reader:^0.5.1`, `pdftoolkit/pdf-images:^0.1.11` or
`pdftoolkit/pdf-fonts:^0.1.11` for PDF modules, and `pdftoolkit/opentype:^0.2.0` for the independent font model. Older core tags `v0.1.0` and
`v0.1.1` retain their PHP 8.5 constraint.

To generate PDFs only:

```sh
composer require "roukmoute/pdf:^0.10.0"
```

To add reading of existing PDFs:

```sh
composer require "roukmoute/pdf:^0.10.0" "pdftoolkit/pdf-reader:^0.5.1"
```

To convert images:

```sh
composer require "roukmoute/pdf:^0.10.0" "pdftoolkit/pdf-images:^0.1.11"
```

To analyze TrueType fonts:

```sh
composer require "roukmoute/pdf:^0.10.0" "pdftoolkit/pdf-fonts:^0.1.11"
```

To analyze a font independently of PDF:

```sh
composer require "pdftoolkit/opentype:^0.2.0"
```

This command installs only OpenType, without the PDF core or converters.

Composer resolves these packages from Packagist and downloads their published
distributions. The three PDF modules require the stable core transitively; installing the
core alone installs no module. Keep the application's `composer.lock` to
pin versions and revisions.

Applications that added GitHub repositories under `repositories` can remove
those entries from `composer.json`. Composer package names remain identical.

Before 1.0, a new minor release may change names and signatures. The
`^0.10.0`, `^0.5.1` and `^0.1.11` constraints allow patches within their series and
exclude the next minor release. Consult changelogs before switching series.
To work with upcoming development, explicitly request `dev-master` for the
relevant packages.

Reader 0.5.1 requires core `^0.9 || ^0.10`; image/font modules 0.1.11 retain
their accepted older core series through `^0.10`. The commands above explicitly
select core 0.10.0 or a compatible patch. The core retains
mandatory PHP extensions `ctype`, `iconv` and `zlib`. AES, CMS and signature
backends using OpenSSL also require `openssl` when selected by the application.

## Reading an external PDF

The reader receives bytes; the application chooses how to obtain them.
`DocumentReader`, `FileBytes` and page readers belong to the module's
`PDF\Reading` namespace, while dictionaries and numbers use the same
`PDF\Syntax\Object` classes as the writer.

```php
use PDF\Reading\DocumentReader;
use PDF\Reading\FileBytes;
use PDF\Reading\PageContentLimits;
use PDF\Reading\PageContentsReader;
use PDF\Reading\PageTreeLimits;
use PDF\Reading\PageTreeReader;
use PDF\Reading\ReaderLimits;

$reader = new DocumentReader(new ReaderLimits(maxFileBytes: 8_388_608));
$document = $reader->read(new FileBytes($pdfBytes));
$tree = (new PageTreeReader($document, new PageTreeLimits(
    maxDepth: 64,
    maxNodes: 10_000,
    maxPages: 5_000,
)))->read();
$contentsReader = new PageContentsReader($document, new PageContentLimits(
    maxStreams: 128,
));

printf("Validated page count: %d\n", count($tree));
foreach ($tree as $index => $page) {
    printf(
        "Page %d; rotation: %d; content streams: %d\n",
        $index + 1,
        $page->attributes->rotate->integer(),
        count($contentsReader->read($page)),
    );
}
```

`PageTreeReader::read()` checks the entire tree: leaf counts, parents, cycles
and repeated identities. It returns a countable, iterable `ReadPageTree`,
with `ReadPage` objects retaining their document, reference and source
dictionary. Their `PageAttributes` provide effective resources, MediaBox,
CropBox and rotation after inheritance from the nearest ancestor. A local
resource dictionary replaces its inherited counterpart without merging;
Contents remains local.

`PageContentsReader` supplies `EncodedStream` objects in document order,
without concatenation or decoding. Traversal and stream-count limits are
explicit objects; cumulative `ReadDocument` budgets continue to apply.
To obtain decoded bytes, separately request
`$document->streamData($stream)`. The
[page-reading guide](https://github.com/PDFToolkit/pdf-reader/blob/v0.5.1/docs/pages.md)
explains every step and supplies an executable example with three inherited
pages.

PDF values remain objects: `get()` preserves a reference as a reference,
and `resolve()` requests its loading within this document. Read objects
are retained in a document-specific cache; there is no singleton or hidden
resolution inside values.

The reader supports xref tables and streams, hybrid references, `/Prev`
revisions, object streams and explicitly bounded filter decoding.
Loading a stream preserves its encoded bytes; `streamData()` requests
decoding. It does not render a page or interpret operators to extract text.
PDF 1.0–2.0 syntax and PDF 2.0 UTF-8 strings remain supported. Reader 0.3 adds
LZW and further TIFF/PNG predictor decoding alongside existing lossless filters.
DCT, JPX, CCITT and JBIG2 codecs remain explicitly unsupported by this reader;
the HTML adapter's separately selected decoders have their own boundary.

### Select password authentication

```php
use PDF\Reading\Security\StandardPasswordAuthentication;
use PDF\Security\Saslprep;

$reader = new DocumentReader(authentication: new StandardPasswordAuthentication(
    (new Saslprep())->prepare($rawUtf8Password),
));
$document = $reader->read(new FileBytes($pdfBytes));
$permissions = $document->permissions();
```

R=5–7 receives explicitly prepared Unicode credentials; historical R=2–4 instead
uses `PdfDocEncodedPassword` with PDFDocEncoding bytes. The
[authentication guide](https://github.com/PDFToolkit/pdf-reader/blob/v0.5.1/docs/authentication.md)
details R=2–7, named `StrF`/`StmF`/`EFF` filters and AES-GCM tag checks. The default
reader opens no encrypted input without that selection. Reader 0.4 verifies
indicated source PDF MACs before returning protected content. Select
`SourceIntegrityPolicy::RequirePdfMac` when the application must also reject
ordinary unprotected or stripped PDFs; the compatible default accepts them.
`requiringSourceIntegrity()` preserves or strengthens a reader's existing
policy without replacing its credentials or limits. The
[source MAC guide](https://pdftoolkit.github.io/modules/reader/source-mac.html)
explains exact byte coverage and supported framing. Reader 0.5 also accepts
explicit `PublicKeyAuthentication` with application-supplied CMS decryption and
permission byte order. Its [public-key guide](https://pdftoolkit.github.io/modules/reader/public-key-authentication.html)
describes Adobe.PubSec s3/s4/s5, independently keyed filters and deferred attachment
access. `DocumentPermissions::effectiveMask()` covers Standard user/owner and
authenticated recipient rights; the receiving application enforces them.
Authentication does not validate signature mathematics or confer certificate trust.

Read values cannot be directly passed back to the writer: their references
belong to the original file. Graph import and remapping, rewriting, merging
and repair remain to be built. Consult the
[reader documentation](https://github.com/PDFToolkit/pdf-reader#readme)
and [its security checks](https://github.com/PDFToolkit/pdf-reader/blob/v0.5.1/docs/security.md)
when choosing budgets. By default, retained binary bytes and total decoded
stream bytes are each bounded to 128 MiB, in addition to other limits.

## Central documentation, independent installations

This documentation presents the API of all six packages. Module pages carry
an **optional** badge, and their source links use the module commit pinned
by the build lock, or by the separate release tag and checkout for OpenType. This adds no dependency to applications installing only
the core.

The core development checkout installs modules in `require-dev` to generate
the [TrueType](tutorials/09-embedded-font.md) and
[PNG/JPEG](tutorials/10-image-files.md) tutorials and export all signatures.
The corresponding PDF objects remain in the core; only external-format
readers and their conversion services are in modules.

The core receives ICC profiles, font programs, already-encoded image data,
certificates and media as explicit data. It checks their PDF relationships
in the relevant native components; their presence does not implement an
ICC engine, codec, page rendering, script execution or signature trust
policy. These boundaries are detailed in the [component guide](components.md)
and [coverage guide](coverage.md).

## Derive HTML from a tagged PDF

The optional [PDF-to-HTML module](https://pdftoolkit.github.io/modules/to-html/index.html) follows the retained PDF Association **Deriving HTML from PDF 1.2** usage specification. Version 0.4.2 requires core `^0.9 || ^0.10` and reader `^0.4.1 || ^0.5`, with 64-bit PHP 8.3+, DOM and mbstring. The site documents core 0.10.0 and Reader 0.5.1, while the HTML release’s original lock retains core 0.9.1 and Reader 0.5.0 for its own validation. The command below explicitly requests core 0.10.0 or a compatible patch. It derives semantic HTML from logical structure; it does not infer untagged structure, run OCR or reproduce PDF page layout. Model coverage, file-adapter coverage and browser/runtime integration are distinct.

```sh
composer require "roukmoute/pdf:^0.10.0" "pdftoolkit/pdf-to-html:^0.4.2"
```

[Follow the executable tutorial](tutorials/35-derive-html.md) and inspect diagnostics before publishing HTML. ParentTree associations, table-header identities, destinations, Unicode mappings, inline images and form actions have tests and independent oracles. The [requirements ledger](https://pdftoolkit.github.io/modules/to-html/requirements.html) links each rule to decisions and evidence; it does not certify universal PDF acceptance.

The [default profile](https://pdftoolkit.github.io/modules/to-html/policies.html) executes neither PDF scripts nor ResetForm/SubmitForm actions and fetches no external resources. `FormActionPolicy` enables targeted reset to `/DV` or supported HTML submissions separately, without enabling PDF ECMAScript. Keep every returned asset with the HTML.

[Graphics](https://pdftoolkit.github.io/modules/to-html/graphics.html) retain their programs and resources: `GraphicPdfExporter` produces an isolated PDF, then `RasterContentRenderer` calls the application's `GraphicsRasterizer`. Rendering engines, encrypted-input authentication, additional codecs and HTML-viewer permission enforcement remain explicit capabilities. A requested visual profile fails explicitly when its engine is unavailable.

Native password authentication is now selectable through an explicit reader
passed to `PdfToHtml`; the [authentication guide](https://pdftoolkit.github.io/modules/to-html/authentication.html)
shows the operation and verified permission propagation. The default still
requires an explicit credential, and the browser must enforce exported rights.

[Packagist: pdftoolkit/pdf-to-html](https://packagist.org/packages/pdftoolkit/pdf-to-html).
