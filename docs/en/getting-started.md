# PDF

An explicit object model of **PDF 1.7 and PDF 2.0**, including ISO 32000-2:2020 EC3 and its companion specifications, for **64-bit PHP 8.3 or later**.

This library represents the format's syntax and structures, down to its names, numbers, references, dictionary entries and operators. It does not aim to provide a layout API. A higher-level library can construct these objects while retaining control of their composition.

The project belongs to the [PDFToolkit](https://github.com/PDFToolkit) organization. The [PDFToolkit/pdf](https://github.com/PDFToolkit/pdf) repository is the **core**: it contains the objects and mechanisms described by the Adobe/ISO standard, including writing. Reading external PDFs, converting PNG/JPEG files and analyzing TrueType fonts belong to three optional packages. Each module depends on the core; installing the core to generate a PDF installs none of these modules.

The [online documentation](https://pdftoolkit.github.io/) brings together guides, a reference for every component and tutorials with their code and viewable PDFs. The [PDFToolkit/pdftoolkit.github.io](https://github.com/PDFToolkit/pdftoolkit.github.io) repository retains the text, assets and build tools. This documentation presents the published core and module versions selected in the source manifest. The documentation commit is identified separately from package versions.

The `0.x` series is intended for developers who want to construct and explore this model. Before `1.0`, a new minor version may change names and signatures; patch releases preserve their series' API. The implemented scope and limits appear in [specification coverage](specification.md).

Definitions are based on the Adobe/ISO documents `PDF32000_2008.pdf` and `adobe_supplement_iso32000.pdf`, retained in the core repository. The [supplement guide](adobe-supplement.md) explains Adobe PDF 1.7 level 3 extensions, their provenance and mechanisms. The [Adobe reference guide](adobe-references.md) also introduces the 2006 reference, its errata, the redaction addendum and their portfolio. Adobe references archived in the core retain their original names and bytes; the four archived references are excluded from Composer archives.

Core 0.7.0 extends [PDF 2.0 writing](pdf-2-0.md) with the [companion specifications](pdf-2-0-bundle.md): R=6 AES-CBC, R=7 AES-GCM, modern digests/signatures, PDF MAC, XMP/declarations, metadata ownership, associated files, document parts and qualified structure roles. The eleven bundle originals retain their supplied names, bytes and source fingerprints in the core; they are excluded from Composer archives. The PDF Association supplies the [sponsored standards](https://www.pdfa.org/sponsored-standards/). WTPDF offers a partial audit, not certification; complete PDF 2.0 or PDF/A, PDF/X and PDF/UA conformance is not inferred from a definition catalogue.

## Installation

Core **0.7.0** requires 64-bit PHP 8.3 or later and the `ctype`, `iconv` and `zlib` extensions. AES and CMS backends are optional and require `openssl`. The [`roukmoute/pdf`](https://packagist.org/packages/roukmoute/pdf) package is available on Packagist. From the consuming project:

```sh
composer require "roukmoute/pdf:^0.7.0"
```

API changes appear in the [changelog](../../CHANGELOG.md) and the
[0.5 migration guide](migration-0.5.md). Keep the consuming project's
`composer.lock` to pin installed versions.

## Optional modules

| Package | Responsibility |
| --- | --- |
| [`pdftoolkit/pdf-reader`](https://pdftoolkit.github.io/modules/reader/index.html) | Read objects and revisions from an external PDF, check pages and their inheritance, inspect their streams. |
| [`pdftoolkit/pdf-images`](https://pdftoolkit.github.io/modules/images/index.html) | Inspect JPEG files and decode PNG files into core image objects. |
| [`pdftoolkit/pdf-fonts`](https://pdftoolkit.github.io/modules/fonts/index.html) | Analyze a static TrueType font and prepare its metrics and mappings for core font objects. |

Version **0.1.8** of the PDF modules accepts core series 0.2, 0.3, 0.4, 0.5, 0.6 and 0.7 on PHP 8.3 or later. The reader still accepts PDF 1.0–1.7 input; image conversion remains PNG/JPEG and font conversion remains static TrueType. All three packages are available on Packagist: [reader](https://packagist.org/packages/pdftoolkit/pdf-reader), [images](https://packagist.org/packages/pdftoolkit/pdf-images) and [fonts](https://packagist.org/packages/pdftoolkit/pdf-fonts). For example, to import image files with core 0.7:

```sh
composer require "roukmoute/pdf:^0.7.0" "pdftoolkit/pdf-images:^0.1.8"
```

The module installs the core with its stable constraint. The [package guide](packages.md) explains boundaries, installation and reader behavior. Keep the application's `composer.lock` to pin the versions and commits used.


The [independent OpenType model](https://pdftoolkit.github.io/modules/opentype/index.html), [`pdftoolkit/opentype`](https://packagist.org/packages/pdftoolkit/opentype), represents font tables, Unicode mappings, metrics and initial GSUB substitutions. It depends on no PDF package. Its [coverage](https://github.com/PDFToolkit/opentype/blob/v0.1.0/docs/coverage.md) details the implemented mechanisms and work remaining.

```sh
composer require "pdftoolkit/opentype:^0.1.0"
```

## Development and checks

From a clone of the [PDFToolkit/pdf](https://github.com/PDFToolkit/pdf) repository:

```sh
export COMPOSER_ROOT_VERSION=0.7.x-dev
composer install
composer check
php examples/hello-world.php hello-world.pdf
php examples/object-stream.php object-stream.pdf
```

Production code depends only on PHP and these three extensions. PHPUnit 12, PHPStan, PHP-CS-Fixer and the modules used by examples and documentation are development dependencies locked in `composer.lock`. Their presence in this checkout adds no production dependency to applications using the core. Core CI runs tests and validates example PDFs on PHP 8.3, 8.4 and 8.5. Tests also fail on PHP deprecations and warnings. The [changelog](../../CHANGELOG.md) describes every published release.

To validate this checkout, including from its tag, set
`COMPOSER_ROOT_VERSION=0.7.x-dev` before `composer install`. This variable
identifies the current core as belonging to the 0.7 series expected by the
modules. Development dependencies use stable 0.1 modules, whose exact versions
and sources are locked in `composer.lock`. CI also defines this variable for
branches, tags and pull requests.

## Construction object by object

```php
$helvetica = new Type1Font(StandardFont::Helvetica);
$resources = new ResourceDictionary(
    new Font(new DictionaryType(
        new Entry(new NameType('F1'), new IndirectReference($helvetica)),
    )),
);
$contents = new StreamObject(new ContentStreams(
    new BeginTextObject(),
    new SetTextFontAndSize(new NameType('F1'), new NumericType(18)),
    new MoveTextPosition(new NumericType(72), new NumericType(720)),
    new ShowText(new LiteralString('Super !')),
    new EndTextObject(),
));
$page = new PageObject(
    new Rectangle(new NumericType(0), new NumericType(0), new NumericType(612), new NumericType(792)),
    $resources,
    $contents,
);
$pages = (new PageTreeNode())->addKid($page);
$catalog = new DocumentCatalog($pages);
$file = new FileStructure(new FileHeader('1.7'), new FileBody($catalog));
$file->writeTo('hello-world.pdf');
```

The complete example, with imports and metadata, is in [`examples/hello-world.php`](https://github.com/PDFToolkit/pdf/blob/v0.7.0/examples/hello-world.php).

## Tutorials and recipes

The [34 tutorials](tutorials/README.md) accompany each script with an explanation, a preview and variants to try. Code comments connect the objects to PDF instructions and structures.

| Topic | What the example explains |
| --- | --- |
| [First document](tutorials/01-first-document.md) | Font, resources, content, page, catalog and document information. |
| [Pages and text](tutorials/02-pages-and-text.md) | Resource inheritance, multiple pages, positions and leading. |
| [Drawing](tutorials/03-graphics.md) | Colors, paths, curves and graphics-state transformations. |
| [Navigation](tutorials/04-navigation.md) | Hierarchical bookmarks and page destinations. |
| [Links](tutorials/05-links.md) | Internal clickable annotations and URI actions. |
| [Images](tutorials/06-images.md) | Image XObject, inline image, RGB bytes and filters. |
| [Shading](tutorials/07-gradient.md) | PDF type 2 function and axial shading. |
| [Compressed objects](tutorials/08-object-stream.md) | Content stream, object container and cross-references. |
| [TrueType font and Unicode](tutorials/09-embedded-font.md) | Embedded program, CID, widths and ToUnicode mapping. |
| [JPEG and PNG images](tutorials/10-image-files.md) | Colors, PNG decoding, preserved JPEG and transparency mask. |
| [Incremental revisions](tutorials/11-incremental-update.md) | Explicit replacements, preserved historical bytes and xref chaining. |

The PDF 2.0 sequence adds [UTF-8 and associated files](tutorials/27-pdf20-associated-files.md), [metadata, declarations and document parts](tutorials/28-pdf20-metadata-declarations.md), [encrypted payload wrappers](tutorials/29-pdf20-encrypted-payload.md), [qualified structure roles and WTPDF reports](tutorials/30-pdf20-tagged-namespaces.md), [modern signatures and integrity](tutorials/31-pdf20-modern-signature.md), and [timestamps and DSS/VRI evidence](tutorials/32-pdf20-timestamp-dss.md). [Geospatial measurements](tutorials/33-pdf20-geospatial.md) and [structure destinations](tutorials/34-pdf20-structure-destinations.md) complete the path. The [bundle guide](pdf-2-0-bundle.md) connects them to their retained specifications and independent checks.

The [table recipe](recipes/table.md) assembles these concepts into a concrete presentation. The [recipe collection](recipes/README.md) also explains how to contribute new examples.

## Identity and responsibilities

- PDF values are objects. Strings represent bytes; `TextString` explicitly encodes Unicode text.
- An `IndirectReference` targets an instance. A `SerializationContext` assigns identifiers while writing a single file. There is no singleton or global counter.
- `FileStructure` describes the file; `FileWriter` writes it. Each write creates a fresh context and derives offsets and lengths from actually emitted bytes.
- Dictionaries use `Entry` objects. `with()` and `without()` construct copies and preserve specialized models' constraints.
- Page trees and outlines use mutable graph builders with a single parent and explicit references. Their structure calculates links and counters; standard definition objects are immutable.
- Filters are applied in the reverse of their decoding order. Streams are always referenced as indirect objects.

See the [architecture](architecture.md) for construction choices and [specification coverage](specification.md) for traceability and limits.

The [component guide](components.md) explains every object family. The [API reference](https://pdftoolkit.github.io/reference/index.html) gives signatures and links to code and the standard. The [site build instructions](site/README.md) describe generation and local checks.

## Coverage and limits

The ISO 32000-1 catalogue inventories the reference's **392 tables**, **823 indexed sections** and **73 operator tokens**. Dictionary tables produce named classes for dictionaries, entries and immutable definitions. PDF names retain their exact case, which is significant in the format.

Executable implementations cover fundamental objects, file writing, cross-reference tables and streams, compressed objects, content operators, page/name/number trees, destinations and outlines, standard fonts and all four PDF function representations.

**A definition's presence is not a declaration of full compliance.** The catalogue validates types, required references, unconditional requirements and some value forms. Conditions, relationships between dictionaries and version rules without specialized validation remain in their definitions and the coverage document.

The core composes font objects, CMaps, images and their masks, forms, tagged structure and incremental revisions. It also writes filters, explicitly selected encryption, byte-range signatures, hybrid references and linearization. Optional modules provide TrueType analysis, JPEG/PNG conversion and external-PDF reading. Verified mechanisms and remaining rules appear in the [coverage inventory](coverage.md). Creating font program subsets, complex-script shaping and importing an external graph with remapping require dedicated components. `EncodedData` explicitly declares already-encoded bytes. Unsupported security obligations are rejected.

The writer currently assembles the file in memory. The reader is supplied by `pdftoolkit/pdf-reader`. A rendering engine and a layout API are outside the core.

## Security

The [security policy](https://github.com/PDFToolkit/pdf/blob/v0.7.0/SECURITY.md) describes private reporting and trust boundaries. The [security review](security.md) explains serialization protections and application responsibilities for paths, PDF actions and resource limits.

## Generating definitions

Structured resources and generated classes are versioned in the core repository. From that repository, generation is reproducible from those resources; the PDF does not need to be read again at library runtime.

```sh
python tools/generate_specification.py
```

The `tools/extract_spec.py` extractor retains the source and PDF locations. Using it requires the Python dependencies listed in the specification documentation. Normative descriptions trace constraints still to implement; class generation does not replace algorithms.
