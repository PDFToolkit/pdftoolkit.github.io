# Embedded files and collections

This example builds a PDF portfolio with a CSV, notes and a JSON export related
to the CSV. The container page explains their relationships; files are actually
embedded and can be extracted by a compatible reader.

Run [embedded-files.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/embedded-files.php):

```bash
php examples/embedded-files.php /tmp/embedded-files.pdf
```

## Supply bytes, then describe the file

`EmbeddedFileStream` receives original bytes and a MIME subtype name. Its `Params`
dictionary calculates `Size` and the MD5 checksum from those bytes before filters
and encryption. This checksum is format data; it certifies neither the file's
origin nor its trustworthiness.

```php
$csv = new EmbeddedFileStream(
    "article,montant\nA,12.50\nB,7.25\n",
    new NameType('text/csv'),
    filters: new FlateDecode(),
);
```

`FileSpecification` then describes name `F`. `EmbeddedFileBindings` supplies
indirect references for `EF`. If `EF.UF` is chosen, also supply Unicode name
`UF` with `FileSpecificationName`. Several names may point to the same stream.
Names remain PDF values; the core opens no paths to guess their content.

Optional information remains in separate objects: description, identifiers,
dates, volatility and Mac information. `MacFileCode` explicitly interprets four
ASCII bytes as a most-significant-byte-first integer. The resource fork is
also a stream supplied by the application.

## Connect an export to its primary file

`RelatedFiles` constructs the name/stream pairs in `RF.F`. The example places
`total.json` there. Key `F` must already be present in `EF`, and every `RF` value
contains complete pairs whose streams are indirect.

`EmbeddedFiles` builds the actual `NameTree` in `Names.EmbeddedFiles`. Its keys
`Mesures` and `Notes` identify file specifications that are themselves indirect.
Those keys are distinct from filenames `mesures.csv` and `notes.txt`. Key order
and branch limits are checked against the effective graph, including after an
incremental update.

## Build collection metadata

`CollectionSchema` associates field names with `CollectionField` objects. The
example distinguishes text, number and date. A `CollectionItem` is built with
that schema; unknown field names or text in the numeric field are rejected.
`FileSpecificationOptions` records the item under `CI` through an indirect reference.

`CollectionSubitem` separates data `D` from display prefix `P`. For measurements,
`D` is `19.75` and `P` is `EUR `. The prefix is not added to the number. For
notes, the prefix exists without `D`: the specification permits this absence,
and no amount is invented.

`CollectionSort` names its fields in `S`. Boolean `A` applies to all fields;
an array supplies individual directions. Missing directions default to `true`
and extra directions are ignored. Here, `Amount` descends while `Title` takes
the default ascending direction.

`Collection.D` is `Mesures`, a key in the actual embedded-file tree. If this
key is absent, initial selection falls back to the container, as the specification
requires. View mode and schema describe an interface the PDF reader may present;
the drawn page remains available even in a reader without that interface.

## Declare a stream with external data

`ExternalStreamObject` handles the other case in Table 5: `F` designates an
external file, and `FFilter` and `FDecodeParms` describe its decoding. The core
does not load this file or execute an `ExternalStreamFilters` encoder. Local
bytes between `stream` and `endstream` are ignored, but their length remains exact.
They remain cleartext under PDF encryption; dictionary strings, including the
filename, follow normal encryption.

Tests cover this mechanism; the viewable example uses embedded files so its
data travel with the downloaded PDF.

## Verification and references

The independent corpus verifies 90 histories, or 180 PDFs, with three xref
formats, compressed objects, linearization and R2 to R5 encryption. Extracted
content, `Size`, MD5, Mac forks, `EF`/`RF`/`CI` links, tree limits and value
updates are checked using pypdf, `hashlib` and qpdf. The example's pages and
rendering are inspected too.

Preserved sources: [Table 5, page 28](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/PDF32000_2008.pdf#page=28),
[file specifications and streams, pages 107–115](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/PDF32000_2008.pdf#page=107),
[collections, pages 378–381](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/PDF32000_2008.pdf#page=378).

[Tutorial path](README.md) · [Verified coverage](../coverage.md)
