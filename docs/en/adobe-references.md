# Adobe PDF 1.7 references and errata

These documents complement the core sources: they help explain the origin of
definitions, verify corrections and distinguish the PDF format from the
behavior of a particular Acrobat version. They concern PDF 1.7 and belong
in the `PDFToolkit/pdf` repository.

The active definition reference remains [ISO 32000-1:2008](https://github.com/PDFToolkit/pdf/blob/v0.5.4/PDF32000_2008.pdf),
with the extensions in the [Adobe supplement](adobe-supplement.md). Archiving
the documents below changes neither generated classes, version rules nor
mechanism implementation status. The [coverage guide](coverage.md)
distinguishes these dimensions.

## Retained documents

Page numbers in this guide refer to physical PDF pages, starting at 1.
The [reference catalogue](https://github.com/PDFToolkit/pdf/blob/v0.5.4/resources/adobe-references/metadata.json)
records their identities, sizes, SHA-256 hashes and relationships between
attachments. Files retain their original names and bytes in Git and can be
downloaded from the documentation. They are excluded from Composer archives
so installing the library does not add these documentation volumes.

| Document | Edition and pages | Purpose |
| --- | --- | --- |
| [PDF Reference, version 1.7](https://github.com/PDFToolkit/pdf/blob/v0.5.4/pdf_reference_1-7.pdf) | Sixth edition, November 2006; 1,310 pages | Adobe reference preceding ISO 32000-1, with examples, historical notes and implementation notes. |
| [Errata for the PDF Reference](https://github.com/PDFToolkit/pdf/blob/v0.5.4/pdf_17_errata.pdf) | October 2007; 18 pages | Corrections to the sixth edition, to compare with ISO rules and executable checks. |
| [PDF Redaction: Addendum](https://github.com/PDFToolkit/pdf/blob/v0.5.4/pdf_reference1-7_addendum_redaction.pdf) | November 2006; 4 pages | Introduction of `Redact` annotations and the distinction between designating an area and destroying its content. |
| [PDF Reference and Related Documentation](https://github.com/PDFToolkit/pdf/blob/v0.5.4/pdf_reference.pdf) | Acrobat SDK 8.1 portfolio, April 2007 cover; 1 page and 4 embedded PDFs | Original container grouping the previous three documents and Acrobat 8.1 implementation notes. |

The [PDF Association's historical archive](https://pdfa.org/resource/pdf-specification-archive/)
places the 2006 Adobe reference and its errata before the standardization of
PDF 1.7 by ISO in 2008. Adobe pagination and table numbers must not be reused
as ISO references.

The ISO foreword, PDF page 6, explains the revision and adoption of the November
2006 Adobe reference. The latter remains useful for its examples and Annex H
on implementations. PDF pages 25–27 already distinguish the format from
products that process it. Its Annex G examples, PDF pages 1,057 and 1,058,
warn that illustrated stream lengths and offsets may be inaccurate: they
require reconstruction before becoming executable fixtures.

## The portfolio and its duplicates

The portfolio's cover page lists its four embedded documents. The portfolio
itself is not an additional 1,310-page reference.

| Name in the portfolio | Embedded document pages | Relationship to retained files |
| --- | --- | --- |
| `pdf_reference.pdf` | 1,310 | Byte-for-byte identical to `pdf_reference_1-7.pdf`. |
| `PDF17Errata.pdf` | 18 | Byte-for-byte identical to `pdf_17_errata.pdf`, dated October 2007. |
| `pdf_reference_addendum_redaction.pdf` | 4 | Byte-for-byte identical to `pdf_reference1-7_addendum_redaction.pdf`. |
| `pdf_implementation.pdf` | 11 | April 2007 Acrobat 8.1 notes; no separate file among the four supplied sources. |

The catalogue retains these correspondences. The portfolio's April 2007 cover
and its attached errata's October 2007 edition are distinct dates. A reader
displaying only the cover may not show attachments; use a reader capable of
opening them to consult the implementation notes. Their pagination starts
at 1 inside the attachment.

## Using errata for audits

The errata correct the 2006 Adobe reference. They must not automatically
replace ISO tables or newer Adobe extensions. Each correction must be matched
with its ISO clause, the object that implements it and evidence checking
its behavior.

Examples of explicitly corrected topics:

- Page 3: unique dictionary keys, position of the `Crypt` filter and the
  distinction of its decryption key.
- Pages 4–6: direct, unencrypted file identifiers, encryption exclusions,
  permissions, cryptographic filter names and sizes.
- Pages 6 and 7: prohibition of an empty `Contents` array, date syntax,
  uncompressed embedded-file size and collection data types.
- Pages 8 and 9: `T*` line movement and organization of embedded OpenType
  programs.

This topic inventory does not declare an exhaustive audit of all 18 pages
complete. A rule already present in ISO 32000-1 may have a core definition
without all its constraints being checked. Current validations and remaining
work are listed in the [coverage guide](coverage.md).

Concrete correspondences have been checked in the existing code: dictionary
keys are unique; an explicit `Crypt` filter is unique and comes first; its key
follows the explicit encryption-backend path. `EmbeddedFileParameters`
calculates size from uncompressed bytes, and `PartialFieldName` rejects a dot
in a partial name (errata page 12). These checks concern their stated domain,
not every variant of an arbitrary document.

The audit also led to a correction in core 0.5.2: `OutlineDictionary` now omits
the root `Count` when all top-level bookmarks have `expanded=false` (errata
page 10 and ISO table 152, PDF page 376). An open descendant hidden beneath
a closed parent does not trigger this entry. An explicitly open top-level
bookmark retains the visible-count calculation; signed item counts do not
change. This check concerns those explicit states without redefining how
leaves are opened.

### Preserving differences between editions

Errata page 13 removes bit 7, `DigestMethod`, from signature seed flags. ISO
table 234, PDF page 455, retains it: the core follows that ISO contract.
Similarly, errata page 14 deprecates old signature-reference digests, whereas
ISO table 253, PDF pages 477 and 478, retains an optional `DigestMethod`.
These differences justify explicit source references rather than globally
applying a 2007 correction.

## Redaction: annotating and removing

Addendum pages 2–4 describe two distinct steps. A `Redact` annotation designates
content to remove and allows selected areas to be reviewed. Applying that
annotation must then remove the affected content and the annotation, and
produce the replacement appearance.

The core already contains the
[redaction annotation dictionary](https://github.com/PDFToolkit/pdf/blob/v0.5.4/src/Specification/Dictionary/RedactionAnnotationTable192.php),
from ISO table 192, PDF pages 421 and 422. The addendum's eight entries
(`Subtype`, `QuadPoints`, `IC`, `RO`, `OverlayText`, `Repeat`, `DA` and `Q`)
appear in that definition. This allows dictionary construction; it is not
a redaction application engine.

Addendum page 3 requires removal of the data, including the affected portion
of an image: a mask or opaque rectangle is insufficient. Metadata and other
forms of content must also be examined. An incremental update preserves the
bytes of previous revisions and therefore cannot ensure this destruction
on its own.

A future redaction processor must build on reading, interpreting and
rewriting content in a dedicated module. `Redact` objects, coordinates and
PDF appearances remain in the core. Adding documentary references does not
implement this processor.

## Acrobat implementation notes

The `pdf_implementation.pdf` attachment documents Acrobat 8.1 behavior:
PRC on pages 6–8, U3D on pages 8 and 9, XFA on pages 9 and 10, collections
on page 10 and discontinued SVG slide shows on page 11. These topics also
appear in the retained Adobe supplement, notably PDF pages 55–58 for PRC
and its product notes.

These notes explain historical behavior rather than imposing Acrobat 8.1's
limits on all PDFs. The format can describe an object or action without the
core executing its script, rendering its media or processing its XFA.

## Checking the sources

After installing the Python validation dependencies:

```sh
python tools/validate_adobe_references.py
```

Validation uses an independent reader to check page counts, the four
attachments and their correspondences, as well as original sizes and hashes.
Quality and documentation workflows run it before publication. Source-file
validation is not evidence of coverage of the algorithms they describe.

[Definitions](specification.md) · [Coverage](coverage.md) · [Adobe supplement](adobe-supplement.md)
