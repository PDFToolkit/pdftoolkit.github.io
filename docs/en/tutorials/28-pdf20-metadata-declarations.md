# 28. XMP metadata, declarations and document parts

The [complete script](https://github.com/PDFToolkit/pdf/blob/v0.7.0/examples/pdf20-metadata-declarations.php)
produces a PDF 2.0 file with a bilingual title, an author's declaration, an
embedded report and separate metadata for the document, one document part and
one drawing sequence. The coloured rectangle uses black point compensation.
These values are written into the corresponding PDF objects; they are more
than explanatory text on the page.

## Run the example

From a core **0.7.0** checkout with its dependencies installed:

```bash
php examples/pdf20-metadata-declarations.php metadata.pdf
```

PHP 8.3 or later is sufficient. This script uses native core objects and needs
no image or font converter. The preview and download below come from the
actual generated file.

## Construct an XMP packet with explicit values

`XmpPacket` serializes RDF properties into a UTF-8 XML packet. `XmpName` supplies
the prefix, namespace URI and local name separately; `XmlText` checks XML
characters and escapes text. The UTF-8 BOM in the XMP marker does not turn the
packet into a PDF text string: it is an XML stream's content.

```php
$title = new XmpLanguageAlternative(
    new XmpName('dc', new MetadataUri('http://purl.org/dc/elements/1.1/'), 'title'),
    new XmlText('PDF 2.0 metadata and document parts'),
    new XmpLocalizedText('fr', new XmlText('Métadonnées PDF 2.0 et parties de document')),
);
$metadata = new MetadataStream(new XmpPacket($title, $review));
$catalogMetadata = new MetadataEntry($metadata);
```

`XmpLanguageAlternative` writes an `rdf:Alt` whose first value is `x-default`.
Language choices are unique even when their casing differs. `MetadataStream`
provides `/Type /Metadata` and `/Subtype /XML`; `MetadataEntry` then creates its
indirect reference. XML metadata streams have existed since PDF 1.4; this
example explicitly selects PDF 2.0 for its other mechanisms. Conflicting
properties or namespace prefixes are rejected.

## Declare a document property without inventing a certification

A `Declaration` contains the URI identifying the claimed specification or
profile. `Declarations` writes the unordered `pdfd:declarations` array in the
exact `http://pdfa.org/declarations/` namespace. Each declaration can contain
an unordered `ClaimData` array: claimant, explicit date, credentials and report
URL.

```php
$review = new Declarations(new Declaration(
    new MetadataUri('https://example.org/pdf/reviewed'),
    new ClaimData(
        new XmlText('PDFToolkit example'),
        new ClaimDate('2026-10-14'),
        claimReport: new ClaimReport('#ef=review.txt'),
    ),
));
```

The `example.org` identifier describes a demonstration workflow. Having that
declaration does not prove PDF/A, PDF/UA or WTPDF conformance, and the core adds
none of those claims. `DeclarationsPdfaExtensionSchema` lets the caller supply
the vocabulary description required in a PDF/A context explicitly; that
description alone does not make a document PDF/A conforming.

The `#ef=review.txt` fragment identifies an embedded report by name. The example
supplies its bytes, MIME type and source date, adds it to `Names.EmbeddedFiles`
and associates it using `AFRelationship /Supplement`. Readers that expose
attachments can therefore discover the report. URIs and filenames cause no
external loading.

## Give each metadata stream its owner

The catalog declaration applies to the document; it does not extend to embedded
or referenced files. The document part's XMP stream describes that part, while
another stream describes only the rectangle's drawing sequence. The three
streams retain distinct identities and vocabularies.

The drawing sequence uses a `MetadataPropertyList` under
`Resources.Properties.ColourInfo`, followed by `/Sample /ColourInfo BDC ... EMC`.
The named list keeps its indirect XML stream reference outside content-stream
syntax. A `Metadata` property written directly inside a content operand is
rejected. References are resolved against the actual owner's resources,
including when the content belongs to an already emitted revision.

`MetadataResourceLocation` also expresses the application note's locations:
embedded font program rather than font descriptor, tiling-pattern stream,
shading dictionary rather than its pattern wrapper, structure element,
annotation, optional-content group or 3D stream. The application chooses the
location because it knows which information resource the metadata describes.

## Separate DPM, document parts and graphics state

The `DocumentPart` contains a `DocumentPartMetadata` dictionary with `Job
(Proof 42)` and an XMP stream under `Metadata`. **DPM and XMP are separate
mechanisms.** DPM holds typed application data; its keys and level names follow
XML Name syntax. Its values are text/date strings, arrays, dictionaries,
booleans and numbers.

`DocumentPartRoot` links the catalog to the node. The page refers to its part
through `DocumentPartEntry`; `setPageRange()` then sets that same page as the
range. The hierarchy builder manages parent links. Graph validation checks
reciprocal references, page order, nonoverlapping ranges, page coverage and
declared levels. DPM is not implicitly inherited from a parent.

Finally, `UseBlackPointCompensation(BlackPointCompensation::On)` writes
`UseBlackPtComp /ON` into a `GraphicsStateParameters` resource selected by `gs`.
The other two exact values are `/OFF` and `/Default`. The rectangle uses a
`CalRGB` colour space; compensation participates in CIE colour conversions
performed by a PDF 2.0 processor. Its appearance depends on the output profile
and viewer, and `/Default` leaves the choice to them.

## Inspect the evidence and sources

`tools/validate_pdf20_metadata.py` checks XML with an independent parser and uses
pypdf to inspect RDF arrays, AF and DPart identities, MIME types and source
dates, BPC state and content operators. qpdf checks the file. Native tests cover
invalid XML characters, impossible dates, missing properties and inconsistent
incremental replacements. Rendering checks the visible page separately.

The packet constructor does not parse user-supplied XML. An application that
manually constructs a raw XML stream remains responsible for its content; the
graph validates its references and PDF type. This lesson is not a general
validator for every ISO 32000-2 rule.

Preserved sources: [PDF Declarations, pages 7–10](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/iso32000-2-bundle/documents/PDF-Declarations.pdf#page=7),
[black point compensation, page 4](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/iso32000-2-bundle/documents/PDF20_AN001-BPC.pdf#page=4),
[associated files, pages 7 and 12–13](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/iso32000-2-bundle/documents/PDF20_AN002-AF.pdf#page=7)
and [metadata locations, pages 4–10](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/iso32000-2-bundle/documents/PDF20_AN003-ObjectMetadataLocations.pdf#page=4).
Document parts are defined in [ISO 32000-2, physical pages 850–853](https://github.com/PDFToolkit/pdf/blob/v0.7.0/ISO_32000-2_sponsored_EC3.pdf#page=850).
The bundle comes from the [PDF Association's sponsored access](https://pdfa.org/sponsored-standards/).

[Tutorial path](README.md) · [PDF 2.0 guide](../pdf-2-0.md)
