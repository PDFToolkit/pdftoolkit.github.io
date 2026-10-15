# Coverage by PDF edition

The ISO1, Adobe and ISO2 dictionary inventories retain separate source identities.
Dictionary definitions, native algorithms, document relationships and conformance
are different dimensions. A complete table inventory does not establish every
conditional rule, rendering operation or external profile requirement.

## Executable source rules and reviewed EC3 corrections

The [source-audit guide](source-audits.md) distinguishes 197 executed intrinsic
dictionary rules (98 PDF 1.7, 99 PDF 2.0), six reviewed EC3 corrections and a
65-record classification covering all correction-bearing pages of the Adobe
errata. Counts describe those exact domains, not a percentage of PDF conformance.
The native appearance-placement algorithm and choice-index semantics preserve
the applicable edition and source correction.

The [redaction tutorial](tutorials/36-applied-redaction.md) demonstrates actual
conservative deletion from a normalized graph and a fresh single-revision file.
WTPDF can optionally compare parsed XML rich text with the canonical field value.
Unreviewed EC3 annotations, other conditional/resource relationships, general
authenticated DocMDP/FieldMDP/UR change authorization, rendering and external or
human conformance evidence remain explicit work.

Core 0.8.1 enforces a complete-delta guard at every native incremental entry
point for verified emitted history. Only terminal signing and PDF 2.0
DSS/document timestamp maintenance are classified; existing field locks apply.
Unclassified form, annotation and UR changes are refused even under P2/P3.
It also rejects redaction font entries outside their actual simple/composite/CID
domain. The [security review](security.md) and [redaction tutorial](tutorials/36-applied-redaction.md)
describe the exact runtime provenance, verification and input boundaries.

## Ordered barcode appearances, graph relations and source integrity

Native barcode construction now preserves the exact encoded field value,
compresses the whole value before partitioning, binds ordered parts to their
serialized PMD and constructs full-widget `AP.N` from an explicitly supplied
image encoder. The [Adobe supplement guide](adobe-supplement.md) explains
empty/binary values, budgets, separate or merged single widgets and the source
ambiguity. Five PDFs, ten widgets and 45 pixel checks use an announced test
image. PDF417/QR/Data Matrix algorithms, quiet zones and scanner behavior remain
the encoder's responsibility.

The [source-audit guide](source-audits.md) adds effective annotation ownership,
reply/popup relationships, remote-action targets and rectilinear measure checks.
The dedicated 84 tests and 132 assertions remain separate from the 197 intrinsic
dictionary rules. They do not execute actions, open remote targets or implement
every annotation/measurement condition.

Core 0.9.1 also enforces PDF 2.0's required annotation `AP` on actual native
and retained graphs. Exceptions are a point rectangle and `Popup`/`Projection`/
`Link`; a horizontal or vertical zero-area rectangle still requires its
appearance. Forms, states and a name-valued `AS` are checked without rejecting
the legal unmatched-state case. The source ledger includes exact approved EC3
issues #22 and #124. Projection annotations separately prohibit `AP` when either
rectangle dimension is zero. Eight PDFs, eleven native refusals and 28 independent pixel
checks exercise this domain; no implicit appearance is invented.

WTPDF follows actual selected native Type 3 glyph programs and their auxiliary
fonts, with ISO2 rendering-mode 3/7 semantics and explicit Poppler differences.
Contextual deprecation checks distinguish `Recommendation` findings from
failures and retain pending opaque/file-context evidence. Neither addition
certifies arbitrary font programs or WTPDF/PDF/UA conformance.

Reader 0.4 verifies standalone and signature-attached source PDF MACs before
protected content is interpreted, using the original bytes and exact token
span. Its [MAC guide](https://pdftoolkit.github.io/modules/reader/source-mac.html)
distinguishes the compatible unprotected-input policy from `RequirePdfMac`,
latest-file authentication from historical per-revision verification, and MAC
integrity from signature mathematics or certificate trust. Public-key source
authentication remains unsupported.

Reader 0.4 also treats optional dictionary null values as absent, including
unavailable reference terminals. `ReadDocument::resolve()` follows physical
indirect-reference chains with shared depth and cycle bounds. PDF 2.0 permits
these chains outside object streams; a compressed member containing only another
reference remains rejected. Optional null MAC entries are absent, while actual
non-null security values retain their required directness. These rules do not
turn arbitrary graph traversal or malformed source recovery into an implicit operation.

Reader 0.4.1 retains the terminal `Encrypt`/`Root`/catalog `Metadata` identities
through these chains. Encryption credentials stay unchanged on reaccess, and
implicit clear metadata remains limited to the actual correctly typed catalog
stream. Its four additional alias cases preserve original ciphertext; the
[security guide](security.md) explains their independent validation and
high-level reader limitations.

## ISO 32000-2:2020 EC3 and companion bundle in 0.7.1

The [PDF 2.0 guide](pdf-2-0.md) documents edition-specific dictionary objects,
including continued tables, fixed and variable entries, common definitions and
reviewed corrections. The [ISO2 inventory](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/iso32000-2-2020/coverage.json)
records exact counts and the remaining semantic/EC3 review. It is not merged
with ISO1 or Adobe into a single conformance percentage.

The [bundle guide](pdf-2-0-bundle.md) covers eleven retained sources. Executable
mechanisms include R=6 credentials, AES-GCM, SHA-3/SHAKE256, named-curve CMS,
PDF MAC, RFC3161 document timestamps, DSS/VRI, qualified structure namespaces,
ISO/TS 32005 inclusion, XMP declarations, object and marked-content metadata,
black point compensation, document parts and encrypted-payload wrappers.
Geospatial measurements include coordinate systems, paired control points,
viewports, affine matrices and typed point clouds.
Initial, incremental and linearized output are checked through the actual
emitted graph and immutable revision snapshots.

The [per-document coverage record](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/iso32000-2-bundle/coverage.json)
links implementation files, tests and independent oracles to each original.
The [WTPDF record](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/wtpdf-1.0/coverage.json)
distinguishes mechanical failures from human review and additional validation.
Its [requirement inventory](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/wtpdf-1.0/requirements.json)
records each assessed aspect, source clause, execution boundary and evidence path.
The reproducible checker rejects omitted clauses and missing evidence files.
No automatic WTPDF/PDF/UA-2 certification or complete base-standard conformance
is claimed. Reader 0.3 adds opt-in R=2–7 password authentication, hybrid xrefs
and further filter decoding to PDF 1.0–2.0 input. Its
[authentication guide](https://github.com/PDFToolkit/pdf-reader/blob/v0.3.1/docs/authentication.md)
states the supported crypt filters. Reader 0.4 adds the source MAC boundary
described above; public-key source authentication remains unsupported.
These input mechanisms remain distinct from writing and rendering.

The [original main standard](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/ISO_32000-2_sponsored_EC3.pdf)
and all eleven newly supplied originals remain unchanged in the public core
repository, with source identities and physical pages. The provider is the
[PDF Association](https://www.pdfa.org/sponsored-standards/). The Adobe downloads
below remain available unchanged.

## Retained references

| Document | Inventory | Source |
| --- | --- | --- |
| ISO 32000-1:2008, PDF 1.7 | 756 pages; 392 tables; 263 dictionary tables; 1,405 entry classes; 73 content operators | [PDF32000_2008.pdf](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/PDF32000_2008.pdf) |
| Adobe supplement, extension level 3 | 140 pages; 66 tables, including 61 dictionary tables | [adobe_supplement_iso32000.pdf](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/adobe_supplement_iso32000.pdf) |
| ISO 32000-2:2020 EC3, PDF 2.0 | 1,023 physical pages; edition-specific base dictionary inventory and reviewed EC3 overlays | [ISO_32000-2_sponsored_EC3.pdf](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/ISO_32000-2_sponsored_EC3.pdf) |

Original files remain in the core repository. Catalogues record their SHA-256
hashes and physical page numbers; interpretation corrections retain the
printed wording and state their justification.

The [2006 Adobe reference, its errata and redaction addendum](adobe-references.md)
are also retained, with their portfolio and a hash catalogue. These are sources
for comparison and audit; their archival does not change the counts of the
two active inventories or implementation statuses.

`Redact` definitions exist in ISO table 192. Core 0.8.0 also applies redaction
through a native conservative processor for supported normalized content. It
removes affected payloads and ancillary channels and writes a fresh graph;
unsupported content requires explicit normalization or is rejected. An
annotation or incremental update alone still does not erase source data.

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
| Signature policies | DocMDP, FieldMDP, usage-rights, seed and certificate-criteria objects; intrinsic checks. Signed-field orchestration and the narrow native 0.8.1 guard are implemented; general permitted-change classification remains open. |
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
the remaining annotation relationships and measurement rules,
multimedia/RichMedia graphs, some function rules and external barcode
symbology codecs. Conditions, version thresholds and resources must
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
