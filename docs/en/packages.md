# Core and optional modules

PDFToolkit separates the PDF model from external-file processing. The
**0.5-series core** and three **0.1-series modules** use PHP 8.3 or later and CI
on PHP 8.3, 8.4 and 8.5. The core retains its Composer name `roukmoute/pdf`
after transfer to the organization; new modules use the `pdftoolkit/` prefix.

## The core boundary

The [core](https://github.com/PDFToolkit/pdf) represents the objects and
mechanisms described by **PDF 1.7 / ISO 32000-1:2008** and the
[Adobe level 3 supplement](adobe-supplement.md): values, references,
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

Dependencies go **from modules to the core**. Modules do not depend on one
another. The core knows none of their parsers: an application can directly
construct its PDF objects or feed them through another converter. The object
model is shared, without parallel copies of primitives or a global registry.

## Installing what the application needs

All four packages are available on Packagist:
[core](https://packagist.org/packages/roukmoute/pdf),
[reader](https://packagist.org/packages/pdftoolkit/pdf-reader),
[images](https://packagist.org/packages/pdftoolkit/pdf-images) and
[fonts](https://packagist.org/packages/pdftoolkit/pdf-fonts).
Stable constraints are `roukmoute/pdf:^0.5.4` for the core and
`pdftoolkit/pdf-reader:^0.1.5`, `pdftoolkit/pdf-images:^0.1.5` or
`pdftoolkit/pdf-fonts:^0.1.5` for modules. Older core tags `v0.1.0` and
`v0.1.1` retain their PHP 8.5 constraint.

To generate PDFs only:

```sh
composer require "roukmoute/pdf:^0.5.4"
```

To add reading of existing PDFs:

```sh
composer require "roukmoute/pdf:^0.5.4" "pdftoolkit/pdf-reader:^0.1.5"
```

To convert images:

```sh
composer require "roukmoute/pdf:^0.5.4" "pdftoolkit/pdf-images:^0.1.5"
```

To analyze TrueType fonts:

```sh
composer require "roukmoute/pdf:^0.5.4" "pdftoolkit/pdf-fonts:^0.1.5"
```

Composer resolves these packages from Packagist and downloads their published
distributions. Modules require the stable core transitively; installing the
core alone installs no module. Keep the application's `composer.lock` to
pin versions and revisions.

Applications that added GitHub repositories under `repositories` can remove
those entries from `composer.json`. Composer package names remain identical.

Before 1.0, a new minor release may change names and signatures. The
`^0.5.4` and `^0.1.5` constraints allow patches within their series and
exclude the next minor release. Consult changelogs before switching series.
To work with upcoming development, explicitly request `dev-master` for the
relevant packages.

Module releases 0.1.5 accept core series `^0.2 || ^0.3 || ^0.4 || ^0.5`.
An application remaining on 0.2, 0.3 or 0.4 can therefore update them; the
commands above explicitly select core 0.5 constructions. The core retains
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
[page-reading guide](https://github.com/PDFToolkit/pdf-reader/blob/v0.1.5/docs/pages.md)
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
PDF 2.0, encryption, hybrid references and unimplemented codecs are
explicitly rejected.

Read values cannot be directly passed back to the writer: their references
belong to the original file. Graph import and remapping, rewriting, merging
and repair remain to be built. Consult the
[reader documentation](https://github.com/PDFToolkit/pdf-reader#readme)
and [its security checks](https://github.com/PDFToolkit/pdf-reader/blob/v0.1.5/docs/security.md)
when choosing budgets. By default, retained binary bytes and total decoded
stream bytes are each bounded to 128 MiB, in addition to other limits.

## Central documentation, independent installations

This documentation presents the API of all four packages. Module pages carry
an **optional** badge, and their source links use the module commit pinned
by the build lock. This adds no dependency to applications installing only
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
