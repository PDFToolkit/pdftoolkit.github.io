# Coverage by PDF edition

The ISO1, Adobe and ISO2 dictionary inventories retain separate source identities.
Dictionary definitions, native algorithms, document relationships and conformance
are different dimensions. A complete table inventory does not establish every
conditional rule, rendering operation or external profile requirement.

## Executable source rules and reviewed EC3 corrections

The [source-audit guide](source-audits.md) distinguishes executed intrinsic
rules for each edition, EC3 corrections bound to exact annotations and the
65 classified Adobe errata records. Versioned ledgers retain scope and evidence;
their size is not a PDF conformance percentage. Editorial classification or a
dictionary definition does not establish execution of an algorithm.

The incremental guard compares complete frozen native revisions and requires
their provenance and verified historical signatures. Core 0.11 adds bounded
rich text and exclusively owned indirect values to Tx/Ch/Btn filling, with
complete normal-appearance replacement. It permits historical page templates
without annotations and retains the listed P3 annotation operations. Encrypted
UR3 histories require explicit password or certificate authentication, every
named key and per-update granting authority. The signed PDF version determines
saving rights and PDF 2.0 `P=false`/absent cases. Field locks, encryption rights
and application scope continue to apply together. The
[protected-revisions guide](protected-revisions.md) explains contracts,
intersections and oracle differences; the [migration guide](migration-0.11.md)
covers DParts, Type3 descriptors and explicit PDF 2.0 semantics.

The [redaction tutorial](tutorials/36-applied-redaction.md) demonstrates real
deletion from a normalized graph into a fresh file without history. WTPDF can
compare parsed XML with the canonical field value. These operations and EC3
corrections do not establish general conformance, rendering or properties
requiring human assessment.

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
The dedicated 84 tests and 132 assertions remain separate from the intrinsic
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
integrity from signature mathematics or certificate trust. Reader 0.5 adds explicit
[public-key authentication](https://pdftoolkit.github.io/modules/reader/public-key-authentication.html)
for Adobe.PubSec s3/s4/s5, independent filter keys and deferred EFOpen access.
Effective recipient rights come from authenticated CMS payloads, not `Encrypt.P`;
modern PubSec MAC verification uses the authenticated DefaultCryptFilter key.

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

Reader 0.6 exposes [physical revisions](https://pdftoolkit.github.io/modules/reader/revision-history.html)
and exact source prefixes within shared budgets. These views remain
unauthenticated; read them separately with explicit credentials and integrity
policies to access protected content. Reading history does not verify signatures
or supply a native writer `FileRevision`.

## ISO 32000-2:2020 EC3 and companion bundle in 0.7.1

The [PDF 2.0 guide](pdf-2-0.md) documents edition-specific dictionary objects,
including continued tables, fixed and variable entries, common definitions and
reviewed corrections. The [ISO2 inventory](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/iso32000-2-2020/coverage.json)
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

The [per-document coverage record](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/iso32000-2-bundle/coverage.json)
links implementation files, tests and independent oracles to each original.
The [WTPDF record](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/wtpdf-1.0/coverage.json)
distinguishes mechanical failures from human review and additional validation.
Its [requirement inventory](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/wtpdf-1.0/requirements.json)
records each assessed aspect, source clause, execution boundary and evidence path.
The reproducible checker rejects omitted clauses and missing evidence files.
No automatic WTPDF/PDF/UA-2 certification or complete base-standard conformance
is claimed. Reader 0.3 adds opt-in R=2–7 password authentication, hybrid xrefs
and further filter decoding to PDF 1.0–2.0 input. Its
[authentication guide](https://github.com/PDFToolkit/pdf-reader/blob/v0.7.0/docs/authentication.md)
states the supported crypt filters. Reader 0.4 adds the source MAC boundary
described above; Reader 0.5 adds bounded public-key source authentication.
These input mechanisms remain distinct from writing and rendering.

The [original main standard](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/ISO_32000-2_sponsored_EC3.pdf)
and all eleven newly supplied originals remain unchanged in the public core
repository, with source identities and physical pages. The provider is the
[PDF Association](https://www.pdfa.org/sponsored-standards/). The Adobe downloads
below remain available unchanged.

## Retained references

| Document | Inventory | Source |
| --- | --- | --- |
| ISO 32000-1:2008, PDF 1.7 | 756 pages; 392 tables; 263 dictionary tables; 1,405 entry classes; 73 content operators | [PDF32000_2008.pdf](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/PDF32000_2008.pdf) |
| Adobe supplement, extension level 3 | 140 pages; 66 tables, including 61 dictionary tables | [adobe_supplement_iso32000.pdf](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/adobe_supplement_iso32000.pdf) |
| ISO 32000-2:2020 EC3, PDF 2.0 | 1,023 physical pages; edition-specific base dictionary inventory and reviewed EC3 overlays | [ISO_32000-2_sponsored_EC3.pdf](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/reference-documents/ISO_32000-2_sponsored_EC3.pdf) |

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

The [ISO inventory](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/iso32000-1/coverage.json) examines 98 mechanism families.
The [Adobe inventory](https://github.com/PDFToolkit/pdf/blob/v0.11.0/resources/adobe-supplement-iso32000/coverage.json)
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
| Signature policies | DocMDP, FieldMDP, usage-rights, seed and certificate-criteria objects; intrinsic checks. Signed-field orchestration and native provenance/delta guards are implemented. Core 0.11.0 adds the bounded form/template/P3/UR3 operations in [the dedicated guide](protected-revisions.md); general classification remains open. |
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

These additions do not declare complete coverage. General classification of
external PDF changes, arbitrary page/content/resource edits, templates with
annotations or fields and legacy UR handlers remain outside the permitted
native operations. Ledgers also distinguish conditional rules, multimedia
graphs, resources and barcode symbologies needing other processors or evidence.
Supported cases have tests and independent oracles; they do not certify every
revision or document.

## Editable appearances corrected in version 0.5.1

The AcroForm and signature-policy examples delimit their three variable-text
appearances with `/Tx BMC ... EMC`. The frame stays outside; text, clipping
and list selections stay in the replaceable part. Without this marker, the
ISO procedure allows new text to be appended to the old stream, explaining
the overlap observed in Acrobat Reader.

The [regression oracle](https://github.com/PDFToolkit/pdf/blob/v0.11.0/tools/validate_variable_text_appearances.py)
parses actual operators with pypdf and exercises two successive replacements
for every appearance. It verifies that old text disappears, frames remain
and the negative case without a marker behaves as expected. These checks
pass on all three PHP versions; they are not interactive Acrobat validation.
Static drawings, buttons and signatures retain freely constructed appearances.

## External-format mechanisms in the current modules

Images 0.2 reconstructs every legal static PNG colour/depth combination, including Adam7, with exact sixteen-bit colour/alpha. It preserves bounded ICC profiles and maps gAMA/cHRM/sRGB metadata through explicit colour policies. JPEG import retains the original DCT bytes, including qualified Adobe CMYK/YCCK and ICC profiles. APNG, HDR metadata and ambiguous colour semantics remain rejected; EXIF orientation is not applied.

Reader 0.7 adds explicit graph import/remapping, external stream capabilities and CCITT decoding. Its [image codec guide](https://pdftoolkit.github.io/modules/reader/image-codecs.html) separates native Ghostscript profiles from the optional pure-PHP Codecs library. JPEG 2000 planes retain precision, signedness, sampling, ICC/colour choices and alpha/channel associations; the PDF consumer applies `ColorSpace`, `Decode` and `SMaskInData`. Parsing alone does not execute image codecs. A malformed stream or exhausted budget never causes fallback to a second engine.

Codecs 0.1 implements eight-bit sequential/progressive Huffman JPEG, bounded JPEG 2000 profiles and JBIG2 segment algorithms. Its [module guides](https://pdftoolkit.github.io/modules/codecs/) enumerate exact mechanisms, unsupported features and independent/normative vector evidence. This does not provide image encoding, a colour-management engine or universal conformance. Native profiles known to alter samples or mishandle particular JBIG2 mechanisms are routed to PHP before processing.

OpenType 0.4 adds TTC/OTC face selection/serialization, all Unicode cmap formats, optical/style parameters and source-range feature masks that preserve run context. Fonts 0.2 connects static TrueType and CFF1 to explicit GSUB/GPOS and PDF placement, preserving aliases and ligature extraction. The [font guide](https://pdftoolkit.github.io/modules/fonts/opentype-layout.html) distinguishes name-keyed and CID-keyed CFF and documents the Poppler CID/OpenType rendering difference. CFF2/variable embedding, static-instance generation, subsetting, a TrueType VM and automatic Unicode shaping/bidi remain absent. `avar` 2 is a proposal outside the retained published OpenType 1.9.1 scope.

The supplied Adobe OTGuide is a 13-page usage guide, not the binary specification. OpenType's [page-by-page map](https://pdftoolkit.github.io/modules/opentype/collections-and-feature-parameters.html) separates supported font features from application UI, font discovery and installation. Retaining uninterpreted tables does not count as implementing them.

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
