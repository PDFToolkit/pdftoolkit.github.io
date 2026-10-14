# 27. PDF 2.0, Unicode metadata and associated files

The [complete script](https://github.com/PDFToolkit/pdf/blob/v0.6.1/examples/pdf20-associated-files.php)
generates a PDF 2.0 page with an embedded font, Unicode metadata and an embedded
CSV. The CSV is associated with the document and page, and a named MCAF property
list links marked content to the file. These are actual PDF objects, not only
a filename drawn on a page.

## Run the example

From a core 0.6.1 checkout with its locked development dependencies:

```bash
php examples/pdf20-associated-files.php pdf20-associated-files.pdf
```

PHP 8.3 or later and the optional `pdftoolkit/pdf-fonts` module are used. The
checkout installs that module for examples; normal core installation does not.
The build runs this script and renders its pages. The preview below comes from
that actual PDF; download it to inspect associated files in a capable reader.

## Encode visible text and metadata separately

Dictionary metadata uses `TextString` with `Utf8TextStringEncoding`, which
writes a UTF-8 BOM before the encoded value. This is a PDF 2.0 text-string
mechanism. The example retains the deprecated `Info.Title` entry solely to
demonstrate that encoding; it does not claim complete PDF 2.0 conformance.
It allows metadata outside the PDFDocEncoding character set without
pretending that the original UTF-8 bytes are already font codes.

Visible page text follows a separate path. The example reads the demonstration
Noto Sans font with the optional font converter, embeds its PDF font program,
selects a font resource and supplies CID character codes to text operators.
The ToUnicode CMap maps those codes back to Unicode. These objects continue
to matter even when the file's metadata uses UTF-8.

## Supply and describe the CSV

The application supplies the CSV bytes to `EmbeddedFileStream`, with a `text/csv`
MIME name and source modification date `2026-10-14T00:00:00Z`. Its PDF filename
is `F (donnees.csv)` with the preferred Unicode `UF` name `données.csv`.
Both `EF.F` and `EF.UF` point to the same stream. `EmbeddedFileBindings` connects an indirect stream reference to the
file specification's `EF` dictionary. Its name and description remain explicit
PDF values; the core does not fetch an external file or interpret its CSV rows.

`AssociatedFileRelationship` adds `AFRelationship /Data`, declaring the CSV's
relationship to the PDF presentation. The relationship describes semantics,
not a command to execute the embedded file. Size/checksum metadata describes
bytes and does not prove their origin or safety.

## Connect the document, page and marked content

`AssociatedFiles` holds the file specifications and `AssociatedFilesEntry`
writes `/AF` on the document catalog and page. These owners reuse the same
file specification rather than inventing independent copies of the attachment.
An attachment name tree can make the file discoverable separately from its
association with those owners.

The marked-content association uses a named `Resources.Properties` dictionary
containing `/MCAF` under `AFData`, followed by `/AF /AFData BDC … EMC` in the content stream.
The corrected EC3 model keeps the property list a dictionary. It also keeps
indirect stream references outside content-stream syntax. A direct array after
`BDC`, an empty association or a file without `AFRelationship` fails native
validation on supported associations; `DP`/`MP` cannot replace the sequence.

## Select the PDF 2.0 catalog

The example uses the edition-specific `CatalogDictionaryTable29` schema and an
explicit PDF 2.0 `FileHeader`. The catalog requires `Type /Catalog` and its page
tree reference; the selected edition records EC3 independently of output version.
UTF-8 metadata and AF/MCAF require PDF 2.0 and are checked against the effective
version, including catalog overrides and effective revision objects.

The ISO1 table number 29 describes a page-tree node; it must not be substituted
for this ISO2 catalog. A new header alone does not implement all PDF 2.0 rules.

## Inspect the PDF and keep its limits visible

Open the downloaded document in a reader supporting embedded/associated files.
Inspect the catalog and page `/AF`, file specification `/AFRelationship /Data`,
embedded stream bytes, named property dictionary `/MCAF`, PDF 2.0 header and
UTF-8 metadata. Compare visible text with the embedded font and ToUnicode mapping.
Independent checks exercise those bytes and references rather than only accepting
a successful generation call.

The optional `pdf-reader` package still documents PDF 1.0–1.7 reading. The example
uses external validation tools for PDF 2.0. This lesson does not encrypt the file
and does not implement R=6, native namespaces, DSS/timestamps, document parts or
full ISO 32000-2 conformance.

## References

The [PDF 2.0 guide](../pdf-2-0.md) explains editions, applicability and remaining
mechanisms. Physical source pages: text strings 131–132; catalog 113–117;
file specifications 149–152; associated files 853–856; corrected MCAF table 409a
1015. The supplied standard copy is private; use [official sponsored access](https://pdfa.org/sponsored-standards/)
and the [public erratum 374](https://github.com/pdf-association/pdf-issues/issues/374).

[Tutorial path](README.md) · [Coverage](../coverage.md)
