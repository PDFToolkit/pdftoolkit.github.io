# Coverage by PDF edition

The ISO1, Adobe and ISO2 dictionary inventories retain separate source identities.
Dictionary definitions, native algorithms, document relationships and conformance
are different dimensions. A complete table inventory does not establish every
conditional rule, rendering operation or external profile requirement.

## ISO 32000-2:2020 EC3 and companion bundle in 0.7.0

The [PDF 2.0 guide](pdf-2-0.md) documents edition-specific dictionary objects,
including continued tables, fixed and variable entries, common definitions and
reviewed corrections. The [ISO2 inventory](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/iso32000-2-2020/coverage.json)
records exact counts and the remaining semantic/EC3 review. It is not merged
with ISO1 or Adobe into a single conformance percentage.

The [bundle guide](pdf-2-0-bundle.md) covers eleven retained sources. Executable
mechanisms include R=6 credentials, AES-GCM, SHA-3/SHAKE256, named-curve CMS,
PDF MAC, RFC3161 document timestamps, DSS/VRI, qualified structure namespaces,
ISO/TS 32005 inclusion, XMP declarations, object and marked-content metadata,
black point compensation, document parts and encrypted-payload wrappers.
Initial, incremental and linearized output are checked through the actual
emitted graph and immutable revision snapshots.

The [per-document coverage record](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/iso32000-2-bundle/coverage.json)
links implementation files, tests and independent oracles to each original.
The [WTPDF record](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/wtpdf-1.0/coverage.json)
distinguishes mechanical failures from human review and additional validation.
No automatic WTPDF/PDF/UA-2 certification or complete base-standard conformance
is claimed. The reader retains its PDF 1.0–1.7 input scope.

The [original main standard](https://github.com/PDFToolkit/pdf/blob/v0.7.0/ISO_32000-2_sponsored_EC3.pdf)
and all eleven newly supplied originals remain unchanged in the public core
repository, with source identities and physical pages. The provider is the
[PDF Association](https://www.pdfa.org/sponsored-standards/). The Adobe downloads
below remain available unchanged.

## Retained references

| Document | Inventory | Source |
| --- | --- | --- |
| ISO 32000-1:2008, PDF 1.7 | 756 pages; 392 tables; 263 dictionary tables; 1,405 entry classes; 73 content operators | [PDF32000_2008.pdf](https://github.com/PDFToolkit/pdf/blob/v0.5.4/PDF32000_2008.pdf) |
| Adobe supplement, extension level 3 | 140 pages; 66 tables, including 61 dictionary tables | [adobe_supplement_iso32000.pdf](https://github.com/PDFToolkit/pdf/blob/v0.5.4/adobe_supplement_iso32000.pdf) |
| ISO 32000-2:2020 EC3, PDF 2.0 | 1,023 physical pages; edition-specific base dictionary inventory and reviewed EC3 overlays | [ISO_32000-2_sponsored_EC3.pdf](https://github.com/PDFToolkit/pdf/blob/v0.7.0/ISO_32000-2_sponsored_EC3.pdf) |

Original files remain in the core repository. Catalogues record their SHA-256
hashes and physical page numbers; interpretation corrections retain the
printed wording and state their justification.

The [2006 Adobe reference, its errata and redaction addendum](adobe-references.md)
are also retained, with their portfolio and a hash catalogue. These are sources
for comparison and audit; their archival does not change the counts of the
two active inventories or implementation statuses.

`Redact` definitions exist in ISO table 192. Applying redaction, which must
destroy content and its traces, remains a mechanism to build with a content
processor. An annotation or an incremental update does not perform that
removal.

In version 0.5.2, comparison with the Adobe errata also corrects the root
`Count` of bookmarks all explicitly closed at the top level. The
[reference guide](adobe-references.md) details this rule and differences
between editions' signature digest contracts.

## Reading the coverage

The [ISO inventory](https://github.com/PDFToolkit/pdf/blob/v0.5.4/resources/iso32000-1/coverage.json) examines 98 mechanism families.
The [Adobe inventory](https://github.com/PDFToolkit/pdf/blob/v0.5.4/resources/adobe-supplement-iso32000/coverage.json)
distinguishes its tables, algorithms, requirements, product notes and external
standards. Their initial baseline is version 0.3.0; subsequent additions must
include implementation files and validation evidence.

The dimensions are distinct:

- **Definition**: the dictionary and its entries have named objects, their
  types, known requirements and source references.
- **Writing**: objects actually execute the mechanism and produce its PDF
  bytes, such as an LZW stream or a linearization hint table.
- **Semantic rules**: ranges, dimensions, conditions, inheritance and
  relationships between objects are checked for the stated domain.
- **Validation**: tests and, where possible, another implementation check
  produced documents. A syntax check alone does not prove their rendering,
  accessibility or cryptographic validity.

A single percentage would mix these dimensions. The inventories therefore
list verified mechanisms and remaining work rather than a completeness figure.

## Native constructions in version 0.4.0

| Family | Constructions and checks |
| --- | --- |
| AcroForm forms | Field trees, inheritance, qualified names, values and flags, separate or merged widgets, appearances and membership of the actual catalog. |
| FDF | Native writing, field hierarchy, explicitly selected export and page-template references. |
| Logical structure and tagged PDF | Hierarchy, roles, classes, attributes, MCID/MCR/OBJR, ParentTree and IDTree; verification of a multipage document. |
| Colors, patterns and shadings | Calibrated and special spaces, tiling cells, seven shadings and actual binary mesh streams; byte and rendering checks. |
| CMaps | Codespaces, CID and Unicode mappings, ranges, notdef, writing modes and UseCMap; extraction from an encoding other than Identity-H. |
| Fonts and strings | Type1, MMType1, TrueType, Type3, CIDFont and Type0; declared programs, horizontal and vertical metrics, subset names and PDFDoc/UTF-16 encodings. |
| Images and transparency | 1/2/4/8/16-bit samples, masks, Decode, Matte, groups, graphics states, blending, soft masks and halftones; JPX/JBIG2 codecs remain external. |
| Optional content | Groups and memberships, visibility expressions, configurations, usage and document-specific states. |
| Compression | LZW EarlyChange 0/1, size transitions and resets; TIFF/PNG predictors at depths 1/2/4/8/16, composed with Flate or LZW. |
| Password encryption | ISO R=2/3/4 algorithms, RC4 and AESV2, with filters and incremental updates; Adobe R=5 remains explicitly available. |
| Certificate encryption | CMS recipient groups, distinct filter keys and s3/s4/s5 formats; key, data and permission-interpretation checks. |
| Signatures | Contents reservation, ByteRange fixed before signing and filling without shifting; independent verification of the three ISO formats and successive signatures. |
| Signature policies | DocMDP, FieldMDP, usage-rights, seed and certificate-criteria objects; intrinsic checks. Orchestration and comparison of permitted revisions remain open. |
| Hybrid references | Classic table and auxiliary xref stream, historical references, compressed objects and reading by older and newer readers. |
| Linearization | Native ordering, page and shared-resource hints, thumbnails and attachments, compressed objects, three xref formats and encrypted variants. |

## Native constructions added in version 0.5.0

| Family | Constructions and checks |
| --- | --- |
| Exact history | `FileRevision.previous`, snapshots of remapped references, actually written dictionaries and encoded stream bytes from the same call, before encryption. |
| Revisions after linearization | Usable initial snapshot and updates preserving bytes, hint ranges and `/Prev`; 90 histories, or 270 independently checked PDFs. |
| Free list and generations | Release, reuse, initial gaps, retired generations, 65535 saturation and ObjStm restrictions; 90 histories, or 450 independently checked PDFs on the three PHP versions. |
| Navigation | Labels, eight destination modes and viewports, distinct name/string spaces, articles and bead rings, transitions and sequences; 77 tests and an oracle with three pages, 55 labels, 10 viewports and three revisions. |
| Files and collections | Embedded bytes, Size/MD5, Mac metadata, EF/RF/CI, attachment trees, typed schemas and items, sort prefixes and directions; 90 histories, or 180 independently checked PDFs. |
| Signed-field policies | Written seeds, backend/digest/certificate selection, copied locks, effective appearances and required evidence. Mathematical output verification before finalization; eight PDFs and nine RSA/DSA signatures in the permanent oracle. |
| Historical signing permissions | First certification, uniqueness, UR cardinality, historical P1, FieldMDP descendant selection and no Adobe permission elevation for a new field signature. |
| Effective graph | Inherited page resources, boxes and rotation, name-tree order and limits, nonexistent generations and native relationships checked on snapshots. |

These additions are not yet a declaration of complete coverage. General
comparison of authenticated changes permitted by DocMDP, FieldMDP and UR
remains open: pages, content, shared resources, annotations, inherited values
and template instantiation need their own analysis. Other priorities include
annotation families and their relationships, 2D/geospatial measurements,
multimedia/RichMedia graphs, some function rules and barcode appearance
preparation procedures. Conditions, version thresholds and resources must
also continue to be audited family by family. The inventories distinguish
these tasks from constructions and evidence already delivered.

## Editable appearances corrected in version 0.5.1

The AcroForm and signature-policy examples delimit their three variable-text
appearances with `/Tx BMC ... EMC`. The frame stays outside; text, clipping
and list selections stay in the replaceable part. Without this marker, the
ISO procedure allows new text to be appended to the old stream, explaining
the overlap observed in Acrobat Reader.

The [regression oracle](https://github.com/PDFToolkit/pdf/blob/v0.5.4/tools/validate_variable_text_appearances.py)
parses actual operators with pypdf and exercises two successive replacements
for every appearance. It verifies that old text disappears, frames remain
and the negative case without a marker behaves as expected. These checks
pass on all three PHP versions; they are not interactive Acrobat validation.
Static drawings, buttons and signatures retain freely constructed appearances.

## Core boundary

The core constructs PDF objects and their writing mechanisms. Font programs,
ICC profiles, encoded image data, certificates, CMS messages, XFA or media
are explicitly supplied. Their processing can be delegated to dedicated
components; it is never assumed to be implemented merely because their
dictionary exists.

Reading an external PDF belongs to [pdf-reader](https://github.com/PDFToolkit/pdf-reader).
Image-file and font conversion belong to [pdf-images](https://github.com/PDFToolkit/pdf-images)
and [pdf-fonts](https://github.com/PDFToolkit/pdf-fonts). Rendering, JavaScript
execution, XFA/3D/multimedia engines and certificate trust policy require
their own processors or standards.

[Definition coverage](specification.md) · [Adobe supplement](adobe-supplement.md)
· [Security](security.md) · [Tutorials](tutorials/README.md)
