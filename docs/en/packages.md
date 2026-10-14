# Core and optional modules

PDFToolkit separates the PDF model from external-file processing. The
**0.7.1 core**, **0.2.0 PDF reader**, **0.1.8 image/font modules** and the independent **0.1.0 OpenType model**
require PHP 8.3 or later and are checked on PHP 8.3, 8.4 and 8.5.
Core **0.7** additionally requires 64-bit PHP; OpenType remains independent of the
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
| [PDFToolkit/opentype](https://github.com/PDFToolkit/opentype) — `pdftoolkit/opentype` | OpenType SFNT bytes and explicit limits | Tables, metrics, Unicode mappings and GSUB glyph substitutions |
| [PDFToolkit/pdf-to-html](https://github.com/PDFToolkit/pdf-to-html) — `pdftoolkit/pdf-to-html` | Tagged PDF bytes or an explicit logical source model | Semantic HTML, CSS, assets and diagnostics |

The reader, images and fonts modules depend on the core without depending on one another. PDF-to-HTML additionally depends on the reader. The core knows none of their parsers: an application can directly
construct its PDF objects or feed them through another converter. The object
model is shared, without parallel copies of primitives or a global registry.

The [OpenType model](https://github.com/PDFToolkit/opentype) is independent: it depends on neither the core nor `pdf-fonts`. It analyzes a font into its own objects without constructing PDF dictionaries. The `pdf-fonts` converter remains the entry point for current TrueType embedding in PDF. The first OpenType release does not yet provide full script shaping, GPOS, GDEF, variable fonts or CFF. See its [coverage](https://github.com/PDFToolkit/opentype/blob/v0.1.0/docs/coverage.md).

Core 0.7.1 extends PDF 2.0 writing with modern cryptography and PDF MAC, XMP/declarations and object metadata, document parts, encrypted payload wrappers and namespace-qualified structure. WTPDF auditing reports partial mechanical checks and pending evidence, without certification. These writer mechanisms do not expand the optional reader’s syntax-input scope, PNG/JPEG conversion or static TrueType conversion.

## Installing what the application needs

All six packages are available on Packagist:
[core](https://packagist.org/packages/roukmoute/pdf),
[reader](https://packagist.org/packages/pdftoolkit/pdf-reader),
[images](https://packagist.org/packages/pdftoolkit/pdf-images),
[PDF fonts](https://packagist.org/packages/pdftoolkit/pdf-fonts) and
[OpenType](https://packagist.org/packages/pdftoolkit/opentype).
Stable constraints are `roukmoute/pdf:^0.7.1` for the core and
`pdftoolkit/pdf-reader:^0.2.1`, `pdftoolkit/pdf-images:^0.1.8` or
`pdftoolkit/pdf-fonts:^0.1.8` for PDF modules, and `pdftoolkit/opentype:^0.1.0` for the independent font model. Older core tags `v0.1.0` and
`v0.1.1` retain their PHP 8.5 constraint.

To generate PDFs only:

```sh
composer require "roukmoute/pdf:^0.7.1"
```

To add reading of existing PDFs:

```sh
composer require "roukmoute/pdf:^0.7.1" "pdftoolkit/pdf-reader:^0.2.1"
```

To convert images:

```sh
composer require "roukmoute/pdf:^0.7.1" "pdftoolkit/pdf-images:^0.1.8"
```

To analyze TrueType fonts:

```sh
composer require "roukmoute/pdf:^0.7.1" "pdftoolkit/pdf-fonts:^0.1.8"
```

To analyze a font independently of PDF:

```sh
composer require "pdftoolkit/opentype:^0.1.0"
```

This command installs only OpenType, without the PDF core or converters.

Composer resolves these packages from Packagist and downloads their published
distributions. The three PDF modules require the stable core transitively; installing the
core alone installs no module. Keep the application's `composer.lock` to
pin versions and revisions.

Applications that added GitHub repositories under `repositories` can remove
those entries from `composer.json`. Composer package names remain identical.

Before 1.0, a new minor release may change names and signatures. The
`^0.7.1`, `^0.2.1` and `^0.1.8` constraints allow patches within their series and
exclude the next minor release. Consult changelogs before switching series.
To work with upcoming development, explicitly request `dev-master` for the
relevant packages.

Reader 0.2.0 and image/font modules 0.1.8 accept core series `^0.2 || ^0.3 || ^0.4 || ^0.5 || ^0.6 || ^0.7`.
An application remaining on an accepted older core series can therefore update them; the
commands above explicitly select core 0.7 constructions. The core retains
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
[page-reading guide](https://github.com/PDFToolkit/pdf-reader/blob/v0.2.1/docs/pages.md)
explains every step and supplies an executable example with three inherited
pages.

PDF values remain objects: `get()` preserves a reference as a reference,
and `resolve()` requests its loading within this document. Read objects
are retained in a document-specific cache; there is no singleton or hidden
resolution inside values.

The reader supports xref tables and streams, `/Prev` revisions, object
streams, Flate, ASCIIHex, ASCII85 and RunLength, and some TIFF/PNG predictors.
Loading a stream preserves its encoded bytes; `streamData()` requests
decoding. It does not render a page or interpret operators to extract text.
Reader 0.2 also accepts PDF 2.0 syntax and PDF 2.0 UTF-8 strings. Encryption, hybrid references and unimplemented codecs remain explicitly rejected.

Read values cannot be directly passed back to the writer: their references
belong to the original file. Graph import and remapping, rewriting, merging
and repair remain to be built. Consult the
[reader documentation](https://github.com/PDFToolkit/pdf-reader#readme)
and [its security checks](https://github.com/PDFToolkit/pdf-reader/blob/v0.2.1/docs/security.md)
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

The optional [PDF-to-HTML module](https://github.com/PDFToolkit/pdf-to-html) follows the retained PDF Association **Deriving HTML from PDF 1.2** usage specification. It installs the core and reader transitively. It derives semantic HTML from logical structure; it does not infer untagged structure, run OCR or reproduce PDF page layout. Model coverage, file-adapter coverage and browser/runtime integration are distinct.

```sh
composer require "pdftoolkit/pdf-to-html:^0.1.0"
```

[Follow the executable tutorial](tutorials/35-derive-html.md) and inspect diagnostics before publishing HTML. The safe default does not execute scripts or fetch external resources.

[Packagist: pdftoolkit/pdf-to-html](https://packagist.org/packages/pdftoolkit/pdf-to-html).
