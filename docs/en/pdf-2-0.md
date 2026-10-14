# PDF 2.0: first mechanisms and edition-specific objects

Core **0.6.0** introduces the first ISO 32000-2:2020 mechanisms, with reviewed
corrections from Errata Collection 3 (EC3, 2026-06-01). It retains PHP 8.3 minimum
and explicit construction, with document-scoped objects and no global registry.
This release does not claim complete PDF 2.0 implementation or conformance.

## Scope of this release

| Area | Implemented construction | Limit |
| --- | --- | --- |
| File version | `PdfVersion::PDF20`, header and effective catalog version | A version declaration alone does not establish conformance. |
| Dictionary text | Encoding objects for PDFDoc/UTF-16BE and UTF-8 with BOM, explicit decoding and version checks | Page text still uses the selected font's character codes. |
| Associated files | `AFRelationship`, AF arrays on supported owners, named MCAF property resources, graph and revision checks | No automatic file or URL loading. |
| Specification model | Four ISO 32000-2 EC3 dictionary tables and 53 typed entries | The complete catalogue remains pending. |
| Applicability and security | Introduced/deprecated/prohibited distinctions, PDF 2.0 rejection of R=5 and public-key permission constraints | R=6 password encryption is not implemented. |

The [worked example](tutorials/27-pdf20-associated-files.md) connects these
objects to a real generated PDF, including Unicode metadata and a CSV.

## Edition, corrections and file version

`SourceEdition` identifies the logical standard independently of the source
copy's SHA-256 and the output file version. `ErrataCollection` selects EC3
without renaming the 2020 base edition. A `SourceReference` records the physical
PDF page, table and clause, copy identity and selected edition.

ISO 32000-1:2008, the Adobe PDF 1.7 supplement and ISO 32000-2:2020 remain
separate corpora. Repeated table numbers have different meanings: table 29 is
a page-tree node in ISO 32000-1 and the catalog in ISO 32000-2. `Catalogue`
rejects mixed ISO1/ISO2 families and mixed ISO2 correction profiles, while the
existing ISO1 + Adobe extension composition remains available.

EC3 is an overlay, not merely new page text. The supplied PDF contains review
annotations, their replies and appended replacement pages. `Completed` records
ISO TC 171 SC 2 WG 8 approval; `Accepted` records PDF Association PDF Technical
Working Group approval. `ErrataResolution` preserves this distinction. These
states must not be collapsed into a generic claim of ISO approval.

## Unicode text strings

`TextString` receives valid Unicode application text and an encoding object.
Its default `PdfDocOrUtf16TextStringEncoding` preserves the PDFDocEncoding
strategy with UTF-16BE fallback. `Utf16BETextStringEncoding` chooses UTF-16BE
explicitly; `Utf8TextStringEncoding` chooses PDF 2.0 UTF-8 and its three-byte BOM.

```php
$title = new TextString('Résumé – fichiers associés', new Utf8TextStringEncoding());
```

The writer checks the effective version of actual text-string objects. UTF-8
text strings require PDF 2.0. `TextStringDecoder` interprets encoded dictionary
text explicitly; raw `LiteralString` and `HexadecimalString` remain bytes.

A dictionary text string and a `Tj`/`TJ` font string serve different purposes.
Writing UTF-8 bytes after `Tj` does not give a PDF reader a Unicode font mapping.
The example separately embeds a TrueType program and uses its CID encoding and
ToUnicode CMap for visible page text. See [embedded fonts](tutorials/09-embedded-font.md).

## Associated files and corrected marked content

A file specification describes a supplied file; an associated-file relationship
explains how it relates to a PDF object. `AssociatedFileRelationship` wraps a
PDF name, with the standard values exposed by `AFRelationship`: Source,
Data, Alternative, Supplement, EncryptedPayload, FormData, Schema and Unspecified.
Custom relationship names remain explicit values.

`AssociatedFiles` contains file-specification dictionaries, and
`AssociatedFilesEntry` supplies `/AF`. The graph validator checks the actual
owner, the nonempty array, its members and each `AFRelationship`. Ordinary
attachments and associated files remain distinct: `Names.EmbeddedFiles` makes
an attachment discoverable, while `/AF` expresses its relationship to an owner.
The same file specification may participate in both constructions.

For marked content, EC3 erratum 374 replaces the contradictory array property
list with a **dictionary containing `/MCAF`**. Store that dictionary under a named
`Resources.Properties` entry and reference it with `/AF /name BDC … EMC`.
Indirect references cannot appear directly inside a content stream.
The single-point operators `DP` and `MP` do not describe an associated sequence.
The native validation applies these rules to effective generated revisions too.

`PDF\Document\Files\BeginAssociatedFilesMarkedContent` composes the existing
BDC operator with `/AF` and a property resource name; it adds no Annex A token.
Native emission facts are frozen with the written bytes, so later unstaged
builder changes or filter callbacks cannot rewrite the meaning of an earlier
revision. Effective resource and Filespec replacements are still revalidated.
Caller-declared opaque stream bytes are outside this native operator interpretation.

PDF 2.0 Form XObjects require their own resource dictionary. MCAF in a form
resolves through those effective resources, including indirect dictionaries.
Associated-file `Params`, when supplied, require a valid source `ModDate`;
`PdfDateValidation` checks bounded syntax, calendar and offset values while
preserving the original representation. No source date is invented.

## Security and version applicability

`FeatureApplicability` distinguishes a feature's introduction, deprecation and
prohibition. A deprecated feature is not automatically forbidden. Conversely,
an explicitly prohibited feature cannot be made valid by emitting a newer header.
The graph and writer use the effective version after the catalog override.

ISO 32000-2 explicitly prohibits the historical standard-security revision 5.
The Adobe R=5 backend remains available for earlier files; PDF 2.0 rejects that
combination. Revision 6 support is pending. Document-wide CMS public-key permission payloads require most-significant-byte-first
order, the accessibility bit 10 and reserved bits 13–32 set to 1. Opaque recipient
bytes alone cannot establish those permission facts. Native AES-256 public-key
encryption can be selected for PDF 2.0 without the earlier Adobe extension
declaration; it is distinct from the pending R=6 password-security handler.
Encryption does not itself authenticate page contents or establish document trust.

## Remaining implementation

The pilot covers table 29 (32 entries, physical pages 113–117), table 43
(16 entries, pages 149–152), table 356 (four entries, page 744) and table 409a
(one entry, page 1015). Their generated classes use
`PDF\Specification\Iso32000_2`, separately from ISO1 and Adobe classes.
Types, fixed Type names, unconditional required entries and selected reviewed
reference constraints are executable. Contextual rules need native mechanisms.

The complete dictionary inventory, R=6 encryption, native namespace role maps
and structure graphs, DSS/validation information/timestamps, document-parts trees,
encrypted wrapper semantics, geospatial features and other PDF 2.0 mechanisms
remain to be implemented. A namespace, DSS or DPartRoot entry schema does not
implement its associated mechanism. The optional reader remains limited to its
[documented PDF 1.0–1.7 scope](packages.md); this writer increment does not expand it.

## Source and checks

The [supplied original `ISO_32000-2_sponsored_EC3.pdf`](https://github.com/PDFToolkit/pdf/blob/v0.6.2/ISO_32000-2_sponsored_EC3.pdf) is preserved in the public core repository with its original name and bytes, following redistribution authorization confirmed by the project owner. Its identity, physical pages and fingerprint appear in the
[pilot metadata](https://github.com/PDFToolkit/pdf/blob/v0.6.2/resources/iso32000-2-2020/metadata.json)
and [coverage inventory](https://github.com/PDFToolkit/pdf/blob/v0.6.2/resources/iso32000-2-2020/coverage.json).
The supplied file comes from the **PDF Association**, through its [official sponsored access](https://www.pdfa.org/sponsored-standards/).

The [public errata](https://pdf-issues.pdfa.org/32000-2-2020/) provide the
[corrected associated-files rules](https://pdf-issues.pdfa.org/32000-2-2020/clause14.html#14135-associated-files-linked-to-graphics-objects).
The pilot descriptions are concise project-authored summaries, not copied
normative paragraphs. The generator verifies reproducible files; unit tests
exercise invalid domains, edition collisions and correction provenance.
Independent PDF validation checks emitted objects and attachment bytes.
See [mechanism coverage](coverage.md) for the other corpora and their limits.
