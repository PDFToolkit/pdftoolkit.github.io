# Adobe extensions and Bates numbering

The [June 2008 Adobe supplement](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/adobe_supplement_iso32000.pdf)
extends PDF 1.7 to Adobe level 3. An extension retains the base PDF format and
declares additional properties a reader may encounter.

This example uses extension declarations and a Bates artifact. Bates numbers
are identifiers chosen by the application to index documents, for example
`DOC-000001` and `EXH-000019`. They are not necessarily the file's page numbers.

## Run the example

```sh
php examples/adobe-extensions.php adobe-extensions.pdf
```

The [complete script](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/adobe-extensions.php)
is commented step by step. The result contains one page and two identifiers
displayed in its footer. This tutorial depends only on the core.

## Declare the extension

```php
$extensions = new DeveloperExtensions(new DeveloperExtensionEntry(
    new DeveloperPrefix(new NameType('ADBE')),
    new DeveloperExtension(new NameType('1.7'), new IntegerType(3)),
));
$catalog = new DocumentCatalog($pages, new Extensions($extensions));
```

`DeveloperPrefix` retains the case-sensitive prefix. `ADBE` identifies Adobe.
`DeveloperExtension` assembles `/BaseVersion /1.7` and `/ExtensionLevel 3`.
`DeveloperExtensionEntry` associates the prefix with this instance. Extension
declarations and all their entries remain direct, as ISO 32000-1, §7.12.1 requires:
no indirect objects occur in this part of the catalog. Finally, `Extensions`
places this dictionary in the document catalog.

The declared base version describes the specification being extended. It is
not calculated from the file header. The model supports several prefixes with
independent base versions and levels. The library does not automatically register
prefixes in a registry.

## Build the Bates artifact

```php
$numbers = new ArrayType(
    new LiteralString('DOC-000001'),
    new LiteralString('EXH-000019'),
);
$bates = new BatesArtifact($numbers);
```

The object produces `/Type /Pagination`, `/Subtype /BatesN` and `/Contents`.
`Contents` accepts a string for one identifier or an array of strings for several.
Their order remains the application's choice. Values are PDF objects; a generic
entry cannot replace them with integers or dictionaries.

## Connect properties to drawing

```php
new BeginMarkedContentWithProperties(new NameType('Artifact'), $bates),
// BT, Tf, Td and Tj draw the footer here.
new EndMarkedContent(),
```

`BDC` opens the `/Artifact` marked sequence with its properties; `EMC` closes it.
Ordinary text operators position and draw the identifiers. Bates properties
describe that content but create no visible text by themselves. The example
therefore supplies numbers both to properties and to displayed text.

`ContentStreams` checks marked-sequence balance during writing. The independent
example check also verifies the `/ADBE` declaration, `/BatesN` classification,
order of the two strings and their visible presence.

## Experiments and references

- Replace the string array with one string and change the displayed text.
- Add a developer prefix with its own level to observe both declarations.
- Move the footer by changing coordinates supplied to `MoveTextPosition`.

The declaration mechanism appears on pages 23–25 of the supplement and in
ISO 32000-1, §7.12. The Bates artifact appears in Table 10.17, page 100 of the
[supplement preserved in the core](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/adobe_supplement_iso32000.pdf#page=100).
The [supplement guide](../adobe-supplement.md) details coverage of other extensions
and provenance rules.
