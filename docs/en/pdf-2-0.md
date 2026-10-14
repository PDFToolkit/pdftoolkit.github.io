# PDF 2.0: objects, writing and companion specifications

Core **0.7.0** implements ISO 32000-2:2020 objects and mechanisms, with reviewed
corrections from Errata Collection 3 (EC3, 2026-06-01). It requires 64-bit PHP 8.3
or later and keeps explicit construction, document-scoped objects and no global
registry. Table coverage does not establish complete conditional, algorithmic or
semantic conformance.

## Scope of this release

| Area | Implemented construction | Limit |
| --- | --- | --- |
| File version | `PdfVersion::PDF20`, header and effective catalog version | A version declaration alone does not establish conformance. |
| Dictionary text | PDFDoc/UTF-16BE and UTF-8 with BOM, explicit decoding and version checks | Page text uses the selected font's character codes. |
| Associated files | AF on information objects, relationships and named MCAF properties | No automatic loading of a file or URL. |
| Specification model | Edition-specific dictionary inventory, fixed and variable entry objects, common tables and reviewed EC3 overlays | Contextual and algorithmic rules remain distinct from table definitions. |
| Security | R=6 password security, R=7 AES-GCM, modern CMS signatures and PDF MAC | Trust, revocation policy and deployment choices remain explicit. |
| Metadata and structure | XMP, declarations, object/marked-content metadata, document parts, encrypted wrappers, qualified namespaces and ISO/TS 32005 rules | Declarations do not prove conformance; WTPDF reports retain human and external checks. |
| Signature preservation | Document timestamps, DSS and VRI with actual revision ordering | Supplied certificates and revocation responses are evidence, not automatically trusted validation. |

The [associated-files example](tutorials/27-pdf20-associated-files.md) connects
these objects to a real file. The [companion bundle guide](pdf-2-0-bundle.md)
describes all eleven sources and the additional executable tutorials.

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
combination. `ModernStandardSecurityHandler` implements R=6 credentials and R=7 AES-GCM. Document-wide CMS public-key permission payloads require most-significant-byte-first
order, the accessibility bit 10 and reserved bits 13–32 set to 1. Opaque recipient
bytes alone cannot establish those permission facts. Native AES-256 public-key
encryption can be selected for PDF 2.0 without the earlier Adobe extension
declaration; the R=6 password-security handler remains a distinct selection.
AES-GCM authenticates encrypted values; PDF MAC authenticates a serialized revision. Neither establishes certificate trust.

## Explicit metrics for standard fonts

PDF 2.0 table 109, physical pages 328–329, requires `FirstChar`, `LastChar`,
`Widths` and `FontDescriptor` for simple fonts. The historical omission allowed
for the fourteen standard fonts applies only to PDF 1.0–1.7. A PDF 2.0 header
does not make a minimal `Type1Font(StandardFont::Helvetica)` complete.

Construct `SimpleFontMetrics` from explicit `SimpleWidths` and `FontDescriptor`
objects, or select an explicitly embedded program with its actual metrics.
The examples' Courier helper supplies declared ASCII widths and descriptor
values without adding a font parser or a registry to the core. Embedding remains
a distinct choice. The effective-graph checks also cover generic dictionaries
and frozen font/resource replacements in later revisions.

## Remaining implementation

The dictionary catalogue includes the base table inventory, continuation pages,
fixed and variable keys, common-table relationships and selected reviewed EC3
overlays. Its classes use `PDF\Specification\Iso32000_2`, separately from ISO1
and Adobe. Types, fixed names, unconditional requirements and reviewed reference
constraints are executable; native mechanisms implement contextual relationships.

Complete conditional and semantic conformance, exhaustive EC3 review, external
rendering/colour processing and automatic accessibility certification are not
established by this inventory. The [coverage record](coverage.md) distinguishes
native mechanisms, declarative objects and remaining work. The optional reader
retains its [documented PDF 1.0–1.7 input scope](packages.md).

## Source and checks

The [original `ISO_32000-2_sponsored_EC3.pdf`](https://github.com/PDFToolkit/pdf/blob/v0.7.0/ISO_32000-2_sponsored_EC3.pdf)
is preserved in the public core repository with its original filename and bytes,
following the project owner's confirmed redistribution authorization.
[Catalogue metadata](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/iso32000-2-2020/metadata.json)
and the [coverage inventory](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/iso32000-2-2020/coverage.json)
record its identity, physical pages and hash. The supplied file comes from the
**PDF Association**, through its [official sponsored access](https://www.pdfa.org/sponsored-standards/).
Both supplied main-standard copies and all companion originals remain in the repository.

The [public errata](https://pdf-issues.pdfa.org/32000-2-2020/) include the
[corrected associated-files rules](https://pdf-issues.pdfa.org/32000-2-2020/clause14.html#14135-associated-files-linked-to-graphics-objects).
Existing project-authored summaries have French translations. Additional source
excerpts retain their original English and are labelled as normative text.
Generators check reproducibility; tests exercise invalid domains, edition
collisions and correction provenance. Independent implementations inspect actual
PDF bytes, cryptography, metadata and structure. See [coverage](coverage.md) and
the [bundle guide](pdf-2-0-bundle.md) for the verified domains and their limits.
