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

The [PDF 1.7 rule data](https://github.com/PDFToolkit/pdf/blob/v0.8.0/resources/iso32000-1/semantic-rules.json)
and [PDF 2.0 rule data](https://github.com/PDFToolkit/pdf/blob/v0.8.0/resources/iso32000-2-2020/semantic-rules.json)
retain source tables and physical pages. Their generators reproduce the PHP
definitions from those reviewed resources.

## Preserve the exact EC3 correction

The [EC3 review record](https://github.com/PDFToolkit/pdf/blob/v0.8.0/resources/iso32000-2-2020/ec3-semantic-reviews.json)
binds each reviewed annotation to the retained document hash, physical page,
annotation identity and approval thread. The checker verifies those bindings.
These four corrections do not establish a review of every EC3 annotation.

| Reviewed correction | Implemented behaviour |
| --- | --- |
| #246, physical page 81 | Common stream entries in an xref stream are recursively direct; external `F` data is excluded. Trailer `Root` and `Encrypt` references retain their own rules. |
| #403, physical page 81 | Xref streams reject `Metadata` and `AF`. |
| #444, physical pages 506–507 | Annotation `Path` takes precedence over accompanying `Vertices`; the vertices are ignored rather than making the pair invalid. |
| #468, physical page 558 | PDF 2.0 choice indices can be supplied without `MultiSelect`. Different display names sharing an export value require indices. An array-valued `V` alone does not require them. |

The first three reviewed threads end as completed; #468 is accepted. The record
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

## Review the Adobe errata without mixing editions

The [Adobe errata review](https://github.com/PDFToolkit/pdf/blob/v0.8.0/resources/adobe-references/errata-review.json)
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
