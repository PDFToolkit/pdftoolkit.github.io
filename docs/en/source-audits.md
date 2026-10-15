# Source rules, errata and reviewed corrections

An archived specification, a dictionary definition and an executable rule are
three different kinds of evidence. Core 0.8.0 adds source-authored checks to the
dictionary model and records which corrections were actually reviewed. The
original PDFs remain unchanged in `resources/reference-documents/`.

## Execute relations between dictionary entries

The two inventories now carry **197 intrinsic semantic rules**: 98 for PDF 1.7
and 99 for PDF 2.0, across 33 source tables in each edition. A table exposes
immutable `SemanticRule` objects, each retaining its identifier, source and
typed `DictionaryConstraint`. Derived dictionaries inherit applicable rules.
`SchemaDictionary::validate()` and serialization execute them; listing a rule
does not replace its execution.

The checks include numeric domains and array dimensions, function inputs and
outputs, filter/`DecodeParms` alignment, cross-reference stream ranges and direct
objects, calibrated/ICC colour relationships, image samples and masks, annotation
geometry and choice options. They concern their declared dictionary domain;
resource interpretation and all document-wide conditions remain separate.

The [PDF 1.7 rule data](https://github.com/PDFToolkit/pdf/blob/v0.9.1/resources/iso32000-1/semantic-rules.json)
and [PDF 2.0 rule data](https://github.com/PDFToolkit/pdf/blob/v0.9.1/resources/iso32000-2-2020/semantic-rules.json)
retain source tables and physical pages. Their generators reproduce the PHP
definitions from those reviewed resources.

## Check the effective annotation, action and measurement graph

The new native checks concern relationships across actual document objects,
separately from the 197 intrinsic dictionary rules. They resolve references
against the effective graph and retain the applicable PDF version, including
objects inherited from an earlier native revision. The dedicated regression
suite has 84 tests and 132 assertions; these are test counts, not normative-rule
counts. The [source-bound record](https://github.com/PDFToolkit/pdf/blob/v0.9.1/resources/graph-semantics/coverage.json)
retains source pages, counterexamples and implementation boundaries.

Markup replies must identify an annotation on the same page. Group replies,
popup ownership and optional reciprocal `Parent` links have their own rules;
a Popup cannot supply its own appearance or actions. Page ownership and unique
annotation names are checked against the actual `Annots` arrays. `GoToR` and
`GoToE` check file specifications, `D`/`SD` destination branches, remote page
indices, `NewWindow` and bounded embedded-target paths. These checks do not open
remote files or prove that an external target exists.

Rectilinear `RL` measures validate required `X`/`D`/`A` arrays, optional
`Y`/`T`/`S`, origin, conversion factor and each number-format dictionary.
Fraction controls are interpreted in their last-array-element context.
`Y` without `CYX` remains a legal declaration: it makes the corresponding
calculations unavailable rather than universally invalidating the dictionary.
This validates the measurement declaration; it is not a coordinate engine or
display-formatting algorithm. Other annotation families, multimedia graphs and
external target semantics retain their separate coverage boundaries.

## Preserve the exact EC3 correction

The [EC3 review record](https://github.com/PDFToolkit/pdf/blob/v0.9.1/resources/iso32000-2-2020/ec3-semantic-reviews.json)
binds each reviewed annotation to the retained document hash, physical page,
annotation identity and approval thread. The checker verifies those bindings.
These six corrections do not establish a review of every EC3 annotation.

| Reviewed correction | Implemented behaviour |
| --- | --- |
| #246, physical page 81 | Common stream entries in an xref stream are recursively direct; external `F` data is excluded. Trailer `Root` and `Encrypt` references retain their own rules. |
| #403, physical page 81 | Xref streams reject `Metadata` and `AF`. |
| #444, physical pages 506–507 | Annotation `Path` takes precedence over accompanying `Vertices`; the vertices are ignored rather than making the pair invalid. |
| #468, physical page 558 | PDF 2.0 choice indices can be supplied without `MultiSelect`. Different display names sharing an export value require indices. An array-valued `V` alone does not require them. |
| #22, physical page 483 | `AP` is required with its stated exceptions for actual PDF 2.0 page annotations, while PDF 1.2–1.7 keeps its optional-appearance contract. |
| #124, physical page 483 | Rectangle indices are zero-based: only `Rect[0]==Rect[2]` **and** `Rect[1]==Rect[3]` supplies the point exception. A horizontal or vertical line is not exempt. |

Five reviewed threads end as completed; #468 is accepted. The record
retains that distinction. Native `ChoiceField` construction selects its edition
explicitly with `ChoiceIndexSemantics::Pdf17` (the default) or
`ChoiceIndexSemantics::Pdf20Ec3`. The latter requires an effective PDF 2.0 version.
When migrating positional arguments, pass this enum before any variadic `Entry`
arguments, or use named arguments. See the [form tutorial](tutorials/14-acroform-fields.md).

## Apply the corrected appearance placement

`AnnotationAppearanceTransform` computes the transformed appearance bounding box
from all four corners, the fitting matrix for the annotation rectangle and the
effective appearance matrix. Rotation and shear therefore participate in the
fit. Composition follows the corrected **Matrix × A** order; it is not
interchangeable for noncommuting transforms. A degenerate source extent is
rejected, while a zero-size destination can collapse to finite coordinates.
Selecting the appropriate appearance, borders and annotation relationships is a
separate responsibility.

The writer also rejects an empty page `Contents` array. Omit `Contents` for a
page without a content stream, or supply an explicit empty stream.

## Require the native PDF 2.0 annotation appearance

Table 166, physical page 483, requires an annotation `AP` in PDF 2.0 except for
`Popup`, `Projection`, `Link`, or a rectangle reduced to a **single point**:
both pairs of coordinates coincide. A vertical or horizontal zero-area
rectangle still needs `AP`. Native graph validation applies the effective
version to fresh objects and retained frozen objects; this is separate from
rendering an imported arbitrary PDF.

Projection annotations have an additional subtype rule (§12.5.6.24, physical
page 520): `AP` is forbidden when either rectangle dimension is zero. This does
not turn the point-only exception for ordinary annotations into an area test.

A supplied appearance dictionary requires its normal `N` entry. `N`, `R` and
`D` identify Form XObject streams or state dictionaries containing such streams.
When any entry uses a state dictionary, the annotation's `AS` must be a name.
If that name has no matching
stream, physical page 491 asks the consumer to attempt reasonable behavior,
such as displaying nothing; it does not guarantee a particular fallback.
The writer preserves that legal case. Declaring appearances does not execute
actions or establish a particular viewer's rendering behavior.

The [appearance source and evidence record](https://github.com/PDFToolkit/pdf/blob/v0.9.1/resources/annotation-appearances/README.md)
describes migration when upgrading a retained PDF 1.7 graph to PDF 2.0. Its
independent oracle examines eight PDFs, eleven native refusals and 28 Poppler
pixels. It does not count a viewer's unmatched-state fallback as a guaranteed
appearance image.

## Review the Adobe errata without mixing editions

The [Adobe errata review](https://github.com/PDFToolkit/pdf/blob/v0.9.1/resources/adobe-references/errata-review.json)
classifies **65 correction records**, covering every correction-bearing physical
page from 3 through 18 of the retained 18-page document. Thirty-one records link
native mechanisms, including ones implemented in earlier releases. Other records
describe editorial changes, consumer operations, legacy viewer behaviour,
external formats, definitions or partially implemented mechanisms.

An exhaustive classification is not an exhaustive implementation claim. For
example, the 2007 removal of signature seed flag `DigestMethod` must not erase
the distinct later Adobe level 3 extension contract. The ledger preserves both
source identities and their applicable editions.

## Read the remaining boundaries

Core 0.8.1 adds a conservative guard on every native incremental writer path.
It requires actual emitted-revision provenance and verified signature history,
then classifies the entire delta for terminal signing or PDF 2.0 DSS/timestamp
maintenance. Existing field restrictions still bind. General form filling,
annotation changes and UR authority are not inferred from P2/P3 and remain
rejected when unclassified. See the [security review](security.md) for migration
from opaque finalization or caller-supplied snapshots and the PKI boundary.

The [coverage guide](coverage.md) and source ledgers still identify unreviewed EC3
annotations, additional conditional/resource relationships and incomplete
authenticated DocMDP/FieldMDP/UR revision-difference authorization. Rendering,
external font and codec semantics, certificate trust and human accessibility
assessment require their own evidence.

The Adobe redaction addendum now has a conservative native processor for an
explicitly normalized graph. Its [dedicated tutorial](tutorials/36-applied-redaction.md)
explains deletion, shared resources, fresh output and rejected inputs. WTPDF also
has optional native XML rich-text comparison, described in the
[bundle guide](pdf-2-0-bundle.md); neither addition certifies arbitrary files.

[Coverage by edition](coverage.md) · [Adobe references](adobe-references.md) · [PDF 2.0](pdf-2-0.md)
