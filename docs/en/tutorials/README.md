# Tutorials: build and read a PDF object by object

These tutorials explain how a PDF file connects its values, dictionaries,
resources and drawing instructions. Each lesson accompanies a complete,
commented, executable script. Examples use the published core and module
versions selected by the [source manifest](../../../resources/sources.json).
The build verifies their exact commits and agreement with the core source
checkout's `composer.lock`.

Lessons 09, 10 and 27 use the optional `pdftoolkit/pdf-fonts` and
`pdftoolkit/pdf-images` modules, installed as development dependencies in the
core checkout. Their PDF objects remain in the core. The [package guide](../packages.md)
explains how to install only the mechanisms an application needs and presents
the external reader `pdftoolkit/pdf-reader`, used in lesson 12.

The learning path takes inspiration from the organization of the
[FPDF tutorials](https://www.fpdf.org/en/tutorial/index.php) and
[script collection](https://www.fpdf.org/en/script/index.php). Here, format objects
remain visible: a font is a resource, a page belongs to a tree and a line of
text is a sequence of operators.

## Install the libraries in an application

The core and modules are available on Packagist. From your project:

```sh
composer require "roukmoute/pdf:^0.7.1"
```

Lessons 09, 10 and 12 use `pdftoolkit/pdf-fonts`, `pdftoolkit/pdf-images` and
`pdftoolkit/pdf-reader` respectively. The
[package guide](../packages.md#installing-what-the-application-needs) gives their
installation commands. The application loads its own `vendor/autoload.php`
and assembles the objects presented in the lessons.

## Prepare the repository

PHP 8.3 or later and the `ctype`, `iconv` and `zlib` extensions are required.
Lesson commands run from the root of a `PDFToolkit/pdf` core checkout.
Markdown files and site construction belong to `PDFToolkit/pdftoolkit.github.io`;
see the [build instructions](../site/README.md) to prepare sources at the
documented versions. From the core checkout:

```sh
export COMPOSER_ROOT_VERSION=0.7.x-dev
composer install
php examples/hello-world.php
```

Under PowerShell, set `$env:COMPOSER_ROOT_VERSION = '0.7.x-dev'` before
`composer install`. The checkout uses its `composer.lock` to install development
tools and all three modules at the documented versions.

Lessons 20 and 26 also require the `openssl` extension used by the signing
backend. The demonstration certificate and key are public test fixtures; the
guide explains how to supply an application-specific identity and trust policy.

The script writes `examples/hello-world.pdf` and displays its path. Open this
file in a PDF reader to compare output with code. Generation scripts under
`examples/` accept an output path as their first argument:

```sh
php examples/hello-world.php mon-premier-document.pdf
```

The chosen path's parent directory must already exist. Scripts load
`vendor/autoload.php`; they can be run from another directory by supplying
their full path. Generated PDFs in `examples/` are ignored by Git.

Lesson 12 uses a script installed with the reader module. Its argument names
the PDF to read; the result is console output. Its tutorial presents the input
PDF, all three pages and the objects read.

## Learning path

| Step | Result and concepts | Complete code |
| --- | --- | --- |
| [01. First document](01-first-document.md) | A sentence, font, page, catalog and document title. | [hello-world.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/hello-world.php) |
| [02. Pages and text](02-pages-and-text.md) | Multiple pages, shared resources, inheritance, positions and leading. | [pages-and-text.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/pages-and-text.php) |
| [03. Drawing and transformations](03-graphics.md) | Colors, paths, curves, graphics state and matrices. | [graphics.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/graphics.php) |
| [04. Bookmarks and destinations](04-navigation.md) | A hierarchical outline and destinations targeting pages. | [navigation.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/navigation.php) |
| [05. Clickable links](05-links.md) | Annotations with an internal destination and URI action. | [links.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/links.php) |
| [06. Images](06-images.md) | The same pattern as an image XObject and an image inline in content. | [images.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/images.php) |
| [07. Gradient and function](07-gradient.md) | A type 2 function supplies an axial shading. | [gradient.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/gradient.php) |
| [08. Compressed objects](08-object-stream.md) | Filters, object streams and cross-reference streams. | [object-stream.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/object-stream.php) |
| [09. TrueType font and Unicode](09-embedded-font.md) | Embedded program, CIDs, widths and ToUnicode mapping. | [embedded-font.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/embedded-font.php) |
| [10. JPEG and PNG images](10-image-files.md) | JPEG inspection, PNG decoding, samples and transparency. | [image-files.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/image-files.php) |
| [11. Incremental revisions](11-incremental-update.md) | Preserved bytes, replacements and xref chaining. | [incremental-update.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/incremental-update.php) |
| [12. Read an external PDF](12-reading-pages.md) | Verified tree, inherited values and content streams inspected then decoded. | [reader module's pages.php](https://github.com/PDFToolkit/pdf-reader/blob/v0.2.3/examples/pages.php) |
| [13. Adobe extensions and Bates numbering](13-adobe-extensions.md) | Extension declarations, artifact properties and Bates footer. | [adobe-extensions.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/adobe-extensions.php) |
| [14. AcroForm fields](14-acroform-fields.md) | Tree, values, widgets and appearances. | [acroform-fields.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/acroform-fields.php) |
| [15. Logical structure](15-tagged-structure.md) | Marked content, ParentTree, IDTree and annotations. | [tagged-structure.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/tagged-structure.php) |
| [16. Linearization](16-linearization.md) | Dependencies, physical order and binary hints. | [linearized.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/linearized.php) |
| [17. Colors and patterns](17-colours-patterns.md) | Spaces, repeating cells and seven shadings. | [colours-patterns.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/colours-patterns.php) |
| [18. CMaps](18-cmaps.md) | UseCMap, CIDs and Unicode mappings. | [cmap-font.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/cmap-font.php) |
| [19. Filters and predictors](19-filters-predictors.md) | LZW compression, TIFF and PNG prediction. | [filters-predictors.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/filters-predictors.php) |
| [20. Signatures](20-signed-document.md) | ByteRange, reservation and detached CMS. | [signed-document.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/signed-document.php) |
| [21. Images, transparency and layers](21-native-graphics.md) | Samples, masks, groups and visibility. | [native-graphics.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/native-graphics.php) |
| [22. Native fonts](22-native-fonts.md) | Type3, simple fonts and vertical metrics. | [native-fonts.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/native-fonts.php) |
| [23. Native navigation](23-native-navigation.md) | Labels, articles, view fitting and presentation. | [native-navigation.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/native-navigation.php) |
| [24. Embedded files](24-embedded-files.md) | EF, RF, metadata and collections. | [embedded-files.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/embedded-files.php) |
| [25. Object generations](25-object-lifecycle.md) | Deletion, free list and reuse. | [object-lifecycle.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/object-lifecycle.php) |
| [26. Signature policy](26-signature-field-policy.md) | Field, seeds, lock and an actually signed result. | [signature-field-policy.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/signature-field-policy.php) |
| [27. PDF 2.0 and associated files](27-pdf20-associated-files.md) | Unicode metadata, AF relationships and corrected named MCAF resources. | [pdf20-associated-files.php](https://github.com/PDFToolkit/pdf/blob/v0.6.2/examples/pdf20-associated-files.php) |
| [28. Metadata, declarations and document parts](28-pdf20-metadata-declarations.md) | XMP scope, AF, black point compensation and DPart relationships. | [pdf20-metadata-declarations.php](https://github.com/PDFToolkit/pdf/blob/v0.7.1/examples/pdf20-metadata-declarations.php) |
| [29. An encrypted-payload wrapper](29-pdf20-encrypted-payload.md) | A readable outer document, hidden collection and independently encrypted inner PDF. | [pdf20-encrypted-payload.php](https://github.com/PDFToolkit/pdf/blob/v0.7.1/examples/pdf20-encrypted-payload.php) |
| [30. Namespaces and WTPDF checks](30-pdf20-tagged-namespaces.md) | Qualified roles, PDF 1.7/2.0 types, reciprocal ParentTree and mechanical-audit boundaries. | [pdf20-tagged-namespaces.php](https://github.com/PDFToolkit/pdf/blob/v0.7.1/examples/pdf20-tagged-namespaces.php) |
| [31. Modern signatures and integrity](31-pdf20-modern-signature.md) | Named curves, SHA-3, exact byte ranges and PDF MAC. | [pdf20-modern-signature.php](https://github.com/PDFToolkit/pdf/blob/v0.7.1/examples/pdf20-modern-signature.php) |
| [32. Document timestamps and DSS](32-pdf20-timestamp-dss.md) | RFC3161, explicit validation policy, VRI and preserved historical signatures. | [pdf20-timestamp-dss.php](https://github.com/PDFToolkit/pdf/blob/v0.7.1/examples/pdf20-timestamp-dss.php) |
| [33. Geospatial objects and measurements](33-pdf20-geospatial.md) | Coordinate systems, paired control points, viewports, matrices and point clouds. | [pdf20-geospatial.php](https://github.com/PDFToolkit/pdf/blob/v0.7.1/examples/pdf20-geospatial.php) |
| [34. Structure destinations](34-pdf20-structure-destinations.md) | Semantic targets, content traversal, named SD entries and explicit page fallbacks. | [pdf20-structure-destinations.php](https://github.com/PDFToolkit/pdf/blob/v0.7.1/examples/pdf20-structure-destinations.php) |
| [35. Derive HTML from tagged PDF](35-derive-html.md) | Tested rules, object-based graphics rendering, targeted reset and actual HTML. | [01-derive-tagged-pdf.php](https://github.com/PDFToolkit/pdf-to-html/blob/v0.2.1/examples/01-derive-tagged-pdf.php) |

After the first document, lessons 03 to 07 can be read in any order matching
your interests. Lessons 08 and 11 concern file organization; lessons 09 and 10
add actual font programs and image files to the graph. Lesson 12 examines an
existing PDF's structures using reader objects.

Lessons 14 and 15 construct form and tagged-content relationships. Lessons 16
and 20 demonstrate specialized writing: organizing bytes for linearization
and reserving signature ranges. Lessons 17 to 19, 21 and 22 go further into
colors, meshes, CMaps, filters, images, transparency and native fonts. Every
PDF object and its resources remain explicitly assembled in the script.

## A few terms before reading the code

| Object or term | Role |
| --- | --- |
| `NameType('F1')` | PDF name `/F1`. In a font resource, it is a local key chosen by the author. |
| `NumericType(72)` | A PDF number. In default user space, 72 units correspond to one inch. |
| `LiteralString` | Bytes intended for a PDF string. For `Tj`, the font and its encoding determine glyphs. |
| `TextString` | A document text string with explicit Unicode encoding when necessary, used for a title or bookmark, for example. |
| `Entry` | A `NameType` key and PDF value in a dictionary. Specialized entries express further constraints. |
| `IndirectReference` | A reference to an object instance. The writer determines its identifier in the file. |
| `ContentStreams` | The operator sequence describing page drawing or text. |
| `StreamObject` | A byte stream with its dictionary and optional filters. Its length is calculated during writing. |
| `ResourceDictionary` | Named resources operators can use: fonts, images, shadings, etc. |
| `PageTreeNode` / `DocumentCatalog` | The page tree and the document's entry point. |

A new page normally has its origin at the lower left and a vertical axis
pointing upwards. A matrix or page rotation can change the relationship between
coordinates and displayed results. Examples show coordinates explicitly.

`with()` constructs a new value: retain its return value. Page and bookmark
trees are assembled with `addKid()` and `addItem()`, which attach a child to
only one parent. The [architecture guide](../architecture.md) explains this
difference in responsibilities.

## Recipes and contributions

The [recipe collection](../recipes/README.md) starts with a [table](../recipes/table.md)
combining text, rectangles and lines. It demonstrates a concrete presentation
using objects already covered. The script calculates positions; the library's
core remains the PDF model.

To propose a generation example, add a standalone script to the core's
`examples/`, then its guide and an index entry to the documentation repository.
Publish the package version and update the source manifest before documenting
new examples. A reading example keeps its script and fixtures in the module
repository; the site build declares their provenance. The guide must explain
expected output, objects used, parameters to change and limitations. A community
example may credit its author and cite its sources. Examples presented here
belong to the project; the list can welcome contributions through pull requests.

CI runs every `examples/*.php` script, then checks each PDF with qpdf. Locally,
with qpdf installed:

```sh
qpdf --check examples/hello-world.pdf
qpdf --qdf --object-streams=disable examples/hello-world.pdf document-lisible.pdf
```

The second command rewrites the PDF into a form useful for examining its
objects. Syntax checks must be complemented by opening the document: a valid
PDF can still have text outside the page or poor layout.

## Go to the specification

Guides cite sections of [PDF 1.7 / ISO 32000-1:2008](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/PDF32000_2008.pdf)
and the [Adobe supplement](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/adobe_supplement_iso32000.pdf).
[Coverage](../coverage.md) distinguishes definitions, constructions and rules
actually verified. Signatures are part of the learning path;
[encryption](../components.md) objects have their own documentation. Font-program
subsetting, complex-script composition, automatic line wrapping and importing
external PDFs with remapping remain to be built. Previews demonstrate example
rendering; they do not certify a document's full conformance, accessibility or
certificate trust.

[Start with the first document](01-first-document.md) · [Back to the README](../../../README.md)


Lesson 35 uses a separate released PDF-to-HTML checkout and its locked reader; see the [build instructions](../site/README.md).
