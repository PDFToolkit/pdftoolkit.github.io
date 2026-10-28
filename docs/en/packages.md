# Core and optional modules

PDFToolkit separates the PDF model from external-file processing.
The documented release series are core **0.12**, Reader **0.7**, Images and Fonts **0.2**, OpenType **0.4**, Codecs **0.1** and PDF-to-HTML **0.7**. They require **64-bit PHP 8.3 or later**; qualification covers PHP 8.3, 8.4 and 8.5. The source manifest pins exact versions and revisions. OpenType and Codecs have no PDF core dependency.
The core retains its Composer name `roukmoute/pdf`; modules use `pdftoolkit/`.

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
| [PDFToolkit/pdf-fonts](https://github.com/PDFToolkit/pdf-fonts) — `pdftoolkit/pdf-fonts` | Static TrueType/CFF bytes, text and explicit layout stages | Embeddable programs, Unicode/CID/GID mappings and positioned PDF text |
| [PDFToolkit/pdf-reader](https://github.com/PDFToolkit/pdf-reader) — `pdftoolkit/pdf-reader` | PDF bytes and reading budgets | Read graph, pages and inherited attributes, references to resolve and encoded or decoded streams |
| [PDFToolkit/opentype](https://github.com/PDFToolkit/opentype) — `pdftoolkit/opentype` | OpenType SFNT/TTC/OTC bytes and explicit limits | Tables, outlines, metrics, GSUB substitutions and GPOS positioning |
| [PDFToolkit/pdf-codecs](https://github.com/PDFToolkit/pdf-codecs) — `pdftoolkit/pdf-codecs` | JPEG, JPEG 2000 or JBIG2 bytes | Component planes and exact colour/alpha metadata within the supported profiles |
| [PDFToolkit/pdf-to-html](https://github.com/PDFToolkit/pdf-to-html) — `pdftoolkit/pdf-to-html` | Tagged PDF bytes or an explicit logical source model | Semantic HTML, CSS, assets and diagnostics |

The reader, images and fonts modules depend on the core without depending on one another. Fonts additionally uses OpenType; PDF-to-HTML uses Reader. OpenType and Codecs are independent libraries. Reader discovers the optional PHP codecs only when image decoding is requested. The core knows none of their parsers: applications can construct its PDF objects directly. The object model is shared, without duplicate primitives or global registries.

The [OpenType model](https://github.com/PDFToolkit/opentype) implements explicit GSUB 1–8, GPOS 1–9 and GDEF, variation axes/metrics and unhinted TrueType/CFF/CFF2 geometry. Version 0.4 reads TTC/OTC collections, serializes a selected complete face, executes all defined Unicode cmap formats and exposes optical/style feature parameters. Source-scalar feature ranges retain the entire shaping context. Applications still choose scripts, languages, stages, normalization and bidi.

The [OpenType coverage ledger](https://pdftoolkit.github.io/modules/opentype/coverage.html) distinguishes 27 implemented table scopes, four partial tables and 19 uninterpreted tables. Raw bytes do not implement a TrueType VM, colour/bitmap/math consumers or WOFF decoding. `pdf-fonts` 0.2 embeds static TrueType and CFF1 and emits explicitly shaped/positioned text with Unicode aliases and ligatures preserved. The [layout guide](https://pdftoolkit.github.io/modules/fonts/opentype-layout.html) details CID/GID mappings and CFF container interoperability. CFF2/variable PDF embedding, static-instance generation and subsetting remain absent.

Core 0.8.0 retains PDF 2.0 writing with modern cryptography and PDF MAC, metadata, document parts, encrypted payload wrappers and qualified structure. It adds [executed source rules and reviewed corrections](source-audits.md), conservative native [redaction](tutorials/36-applied-redaction.md) and optional WTPDF XML rich-text comparison. WTPDF remains a partial mechanical audit without certification. Reader authentication and OpenType layout have their own input boundaries; these core changes do not implement PNG/JPEG conversion or variable-font embedding.

## Installing what the application needs

All seven libraries are available on Packagist under `roukmoute/pdf` or the `pdftoolkit/` names above. The documented constraints are core `^0.12`, Reader/HTML `^0.7`, Images/Fonts `^0.2`, OpenType `^0.4` and Codecs `^0.1`. Older core tags `v0.1.0` and `v0.1.1` retain their PHP 8.5 constraint.

To generate PDFs only:

```sh
composer require "roukmoute/pdf:^0.12"
```

To add reading of existing PDFs:

```sh
composer require "roukmoute/pdf:^0.12" "pdftoolkit/pdf-reader:^0.7.0"
```

To convert images:

```sh
composer require "roukmoute/pdf:^0.12" "pdftoolkit/pdf-images:^0.2.0"
```

To embed TrueType/CFF fonts and select layout:

```sh
composer require "roukmoute/pdf:^0.12" "pdftoolkit/pdf-fonts:^0.2.0"
```

To analyze a font independently of PDF:

```sh
composer require "pdftoolkit/opentype:^0.4.0"
```

This command installs only OpenType, without the PDF core or converters.

To make the pure-PHP image fallback available:

```sh
composer require "pdftoolkit/pdf-codecs:^0.1"
```

Ghostscript and `prlimit` are optional system tools, supplied separately. Reader uses only native profiles qualified to preserve the requested samples and metadata. Malformed input and resource-limit failures do not trigger another decoder.

Composer resolves these packages from Packagist and downloads their published
distributions. The three PDF modules require the stable core transitively; installing the
core alone installs no module. Keep the application's `composer.lock` to
pin versions and revisions.

Applications that added GitHub repositories under `repositories` can remove
those entries from `composer.json`. Composer package names remain identical.

Before 1.0, a new minor release may change names and signatures. The
`^0.12`, `^0.7` and `^0.2` constraints allow patches within their series and
exclude the next minor release. Consult changelogs before switching series.
To work with upcoming development, explicitly request `dev-master` for the
relevant packages.

Images 0.2 requires core `^0.12`; Reader 0.7 requires `^0.11 || ^0.12`. Fonts 0.2 accepts its documented core 0.4–0.12 series and requires OpenType `^0.4`. The commands above select core 0.12. The [migration guide](migration-0.11.md) remains relevant to 0.11 API changes. Core needs `ctype`, `iconv` and `zlib`; selected AES, CMS and signature providers also need `openssl`. Exact compatibility is recorded in each published Composer manifest.

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
[page-reading guide](https://github.com/PDFToolkit/pdf-reader/blob/v0.7.0/docs/pages.md)
explains every step and supplies an executable example with three inherited
pages.

PDF values remain objects: `get()` preserves a reference as a reference,
and `resolve()` requests its loading within this document. Read objects
are retained in a document-specific cache; there is no singleton or hidden
resolution inside values.

The reader supports xref tables/streams, hybrid references, `/Prev` histories and object streams. Parsing preserves encoded data without image-decoder execution. Explicit `streamData()` handles bounded filters, predictors and CCITT; `imageData()` preserves exact component planes and colour/alpha metadata for DCT/JPX/JBIG2. Qualified native decoding takes priority, then installed PHP codecs provide the fallback. The [image codec guide](https://pdftoolkit.github.io/modules/reader/image-codecs.html) explains profiles, globals, budgets and lossless interleaving limits. Reader does not render pages or interpret content operators to extract text.

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
[authentication guide](https://github.com/PDFToolkit/pdf-reader/blob/v0.7.0/docs/authentication.md)
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

Read references remain tied to their source document. Reader 0.7 supplies [ImportSession](https://pdftoolkit.github.io/modules/reader/import.html) to copy an explicitly selected graph into new writer objects with remapped identities. The application chooses preserved encoded streams or bounded decoding. Shared identity and cycles survive; transport containers, signatures and source encryption authority do not transfer. This is neither automatic page merging, semantic repair nor an incremental edit of the original. Explicit [external-stream capabilities](https://pdftoolkit.github.io/modules/reader/external-streams.html) supply bytes without implicit file/network access. Reader and import budgets continue to apply.

Reader 0.6 adds [physical revision history](https://pdftoolkit.github.io/modules/reader/revision-history.html): exact prefixes, xrefs and object spans within shared budgets. This view preserves source bytes without authenticating them or verifying signatures. To interpret an encrypted prefix, read it separately with `DocumentReader` and explicit credentials/integrity policies. A physical history does not become a native `FileRevision` authorized for incremental writing.

## Central documentation, independent installations

This documentation presents the API of all seven libraries. Module pages carry
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

The optional [PDF-to-HTML module](https://pdftoolkit.github.io/modules/to-html/index.html) follows the retained PDF Association **Deriving HTML from PDF 1.2** usage specification. Version 0.7 uses Reader 0.7, with 64-bit PHP 8.3+, DOM and mbstring; the source manifest fixes its exact core and module revisions. It derives semantic HTML from logical structure without inferring absent structure, OCR or PDF page layout. Model coverage, file adaptation and browser integration remain distinct.

```sh
composer require "roukmoute/pdf:^0.12" "pdftoolkit/pdf-to-html:^0.7"
```

[Follow the executable tutorial](tutorials/35-derive-html.md) and inspect diagnostics before publishing HTML. ParentTree associations, table-header identities, destinations, Unicode mappings, inline images and form actions have tests and independent oracles. The [requirements ledger](https://pdftoolkit.github.io/modules/to-html/requirements.html) links each rule to decisions and evidence; it does not certify universal PDF acceptance.

The [default profile](https://pdftoolkit.github.io/modules/to-html/policies.html) executes neither PDF scripts nor ResetForm/SubmitForm actions and fetches no external resources. `FormActionPolicy` enables targeted reset to `/DV` or supported HTML submissions separately, without enabling PDF ECMAScript. Keep every returned asset with the HTML.

[Graphics](https://pdftoolkit.github.io/modules/to-html/graphics.html) retain their programs and resources: `GraphicPdfExporter` produces an isolated PDF, then `RasterContentRenderer` calls the application's `GraphicsRasterizer`. Rendering engines, encrypted-input authentication, additional codecs and HTML-viewer permission enforcement remain explicit capabilities. A requested visual profile fails explicitly when its engine is unavailable.

HTML 0.7 consumes Reader’s decoded planes and interprets PDF colour/alpha precedence before producing browser PNG assets. Exact-depth promotion, ICC bytes, `Decode` and `SMaskInData` are kept separate from page rendering. Signed/distinct-grid or unsupported colour/precision cases require the explicit renderer or produce diagnostics/placeholders; no silent eight-bit reduction is claimed. The [image codec guide](https://pdftoolkit.github.io/modules/to-html/image-codecs.html) records browser comparison and colour-engine limits.

Native password or certificate authentication is selected through an explicit reader
passed to `PdfToHtml`; the [authentication guide](https://pdftoolkit.github.io/modules/to-html/authentication.html)
shows the operation and verified permission propagation. The default still
requires an explicit credential, and the browser must enforce exported rights.

[Packagist: pdftoolkit/pdf-to-html](https://packagist.org/packages/pdftoolkit/pdf-to-html).

`ContentAppearanceRenderer` reuses that explicit content engine for complete
normal/down/rollover button appearances. The [signature guide](https://pdftoolkit.github.io/modules/to-html/signatures.html)
shows an application-selected certificate and source-bound validation results;
mathematical integrity, trust and permission for later changes remain distinct.
HTML 0.6 also corrects combined marked-content properties, partial Unicode
fallback, nested Form artifacts and form/list/attribute behavior. The module's
exact-candidate CI checks PHP 8.3/8.4/8.5 and both Chromium and Firefox.
