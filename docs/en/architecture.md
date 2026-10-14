# Architecture

This architecture describes the core and optional modules at the published versions
selected in the [source manifest](../../resources/sources.json).
The [component guide](components.md) introduces their concrete objects; the
[coverage guide](coverage.md) distinguishes native constructions, verified rules
and remaining work in the two retained references.

## PDF domain

The `PDF\Syntax` namespace follows the reference's terminology. `BasicType` is the contract for PDF values. Its subtypes represent the eight object families; indirect objects and their references have separate classes. Specialized classes such as `Rectangle` add constraints to these values without converting their contents into PHP scalars.

Scalar arguments are limited to leaves: a numeric value, byte sequence, name or boolean. Compositions use objects. A dictionary entry has a `NameType` and a `BasicType`; a content instruction has typed operands.

Each class has its own responsibility in the PDF model. Names and abstractions follow the standard; the API may evolve to respect that model. Composition shortcuts and layout functions belong to future convenience libraries.

## Package boundaries

The `roukmoute/pdf` core contains the PDF objects and mechanisms described by the Adobe/ISO reference. `pdftoolkit/pdf-reader`, `pdftoolkit/pdf-images` and `pdftoolkit/pdf-fonts` are separate optional modules. They depend on the core, which depends on none of them. Their parsers are not loaded by an application that installs only the core.

Names, values, references and structures are shared through composition. In particular, the core defines image samples and streams, the embedded `/FontFile2` program, metrics, CID fonts and PDF CMaps. JPEG inspection, PNG decoding and TrueType table analysis are external-format processing in their respective modules. The [package guide](packages.md) details these boundaries and installation.

## Definitions and instances

`PDF\Specification` separates a standard definition from a PDF object. `SourceReference`, `Requirement`, `ObjectTypeConstraint`, `EntryDefinition` and `TableDefinition` are immutable values. Generated definitions are constructed through instances, without runtime JSON reading or a global registry.

Generated dictionaries and entries carry the terms of their original table. Table numbers stabilize class names when several tables have similar titles. PHP class names are unique without regard to case; PDF names remain case-sensitive. Tests verify this distinction.

An “additional entries” table can compose its type's common definitions. Unknown entries remain accessible through an explicit `Entry` object to allow format extensions. This mechanism does not allow a known entry's constraints to be bypassed.

`DocumentCatalog` and `ResourceDictionary` compose the definitions of tables 28 and 33 to validate their entries. The catalog adds page-graph ownership rules. These supplement the definition's constraints, which also apply to generic entries.

## Graph assembly

Values and definitions do not manage identity within a file. References target their objects. During writing, `SerializationContext` traverses reachable objects and reserves explicit identifiers before assigning automatic ones. A given object receives a single identifier in that file.

Indirect cycles, such as `Parent`/`Kids` links, are allowed. Direct cycles are rejected. Two distinct instances cannot claim the same number, and one instance cannot claim two identifiers.

Page trees and outlines are assembled by builders that enforce attachment to a single parent. Structural fields cannot be replaced or removed through a generic entry. Name and number trees sort their keys and check their descendants' ranges.

Field trees and logical structure trees follow the same ownership rule.
A widget belongs to its field and a page; marked content belongs to its elements
and its page or form context. Identities allow ParentTree/IDTree links to be
derived and references to be checked. Optional content groups have their own
objects, configurations and document states; two groups with the same name
remain two different identities.

Value constructors remain immutable. Builders that assemble a graph explicitly
own their local state; they are not global registries and do not select pages
or resources on the caller's behalf.

## Native mechanisms

Specialized components compose PDF definitions with their coupled constraints:
image dimensions and components, color spaces and tint functions, mesh
coordinates and bits, Type3 programs, codespaces and CMaps, field states,
structure classes and attributes. Produced streams contain the mechanism's
bytes, such as a mesh, LZW data or linearization hints.
A dictionary declaration alone retains a separate role.

Available PDF arithmetic functions receive explicit objects: calibrated color
transformation, Decode quantization, Matte precomposition, local blending or
visibility-condition evaluation. They are not a rendering engine, a layout
system or an external-format parser. An ICC profile, font program or media
asset remains supplied data.

## Writing

`FileWriter` and the `CrossReferenceTable`, `CrossReferenceStream` and `ObjectStream` objects carry the file representation. An enum object, `CrossReferenceFormat`, selects the cross-reference format: table, stream or hybrid. Object streams require stream or hybrid references and PDF 1.5 or later.

The serializer counts bytes, not Unicode characters. The header uses the required ASCII hyphen, strings escape their syntax, names escape their bytes, and numbers never use exponential notation. A stream's length is calculated after applying filters.

Object-stream members receive type 2 entries in the cross-reference stream and are not written a second time as standalone objects. `startxref` targets the actual start of the cross-reference section.

`LinearizedWriter` plans dependencies, physical ordering and the hint tables of
Annex F. `SignatureWriter` prepares a revision whose ByteRange values are fixed
before cryptographic calculation; the signature then fills its reservation.
String and stream encryption uses a `FileEncryption` and explicitly selected
backends. Offsets refer to the written bytes, including the applicable filters,
reservations and security parameters.

## Validation

Constructors reject locally invalid states. Graph validation takes place during serialization, when parents and resources can be established. Conditional requirements in the standard are not presented as automatically covered until dedicated validation and tests handle them.

`DocumentGraphValidation` traverses the writer's actual graph, including stream
dictionaries and typed operands. The `CatalogComponent` contract lets a
component check its relationships with the catalog; `VersionedComponent`
checks selected features against the effective PDF version in the header
and catalog. Adobe declarations and font subset identities also undergo
document-level checks. Validation uses the frozen effective values when a
revision is reused.

These contracts cover the stated families and conditions without claiming to
check every sentence of the standard. Graph tests are not PDF/UA certification;
a valid signature does not replace a certificate trust policy. The
[inventories](coverage.md) retain these boundaries and open constraints.

PHPUnit tests check behaviors and counterexamples; independent readers also validate produced files. PHPStan level 8 analysis and PSR-12 formatting are part of `composer check`.

The model requires PHP 8.3 or later, with typed constants, `readonly` classes and enums. CI runs checks on PHP 8.3, 8.4 and 8.5. On PHP 8.5, the native `NoDiscard` attribute flags ignored results from immutable methods that declare it; those methods construct the same objects on all three versions.

## Extension

A convenience library can transform its own layout objects into this model. A new standardized entry can receive a specialized type and validation while retaining its definition and source. A new filter must perform the encoding it declares; a filter name or dictionary definition is not enough to claim a codec.

In `pdftoolkit/pdf-fonts`, TrueType fonts consist of a program, tables and metrics, a character/CID mapping and an embeddable CIDFont program. These data feed the core objects: FontFile2, descriptor, CID font, Type0 font, metrics and ToUnicode. Text encoding remains a separate service. The module supplies bytes; it does not select a system font or shape complex scripts.

In `pdftoolkit/pdf-images`, image readers receive an `ImageFileBytes`. PNG becomes color samples and, where present, alpha; JPEG becomes a core `DCTImage` with its encoded bytes and color transform. `ImageXObjectFactory`, in the core, composes their dictionaries and streams without knowing the original file. Resource names and painting matrices remain explicit. An `ImageImportLimits` from the module supplies read limits.

In `pdftoolkit/pdf-reader`, `DocumentReader` reads a `FileBytes` with `ReaderLimits` budgets. A `ReadDocument` owns its references, xref index and cache; the application explicitly calls `resolve()` and `streamData()`. PDF values reuse core primitives. External references and streams cannot be serialized into a new document without import and remapping, mechanisms that remain distinct from reading.

`FileRevision` freezes a document's bytes and identity bindings. `RevisionObject` retains its historical aliases and a copy of its dictionary entries, so a mutable builder is not traversed again after writing. `IncrementalUpdate` selects changes in a `FileBody`; `IncrementalWriter` appends new bytes, inherits the trailer and links xref sections. A historical reference does not trigger new serialization. Old structural containers are preserved, and replaced compressed members use a new container or a standalone object.

Password and certificate handlers, identities, permissions and signatures have
their objects in `PDF\Security` and `PDF\Document\Signatures`. OpenSSL backends
are explicitly selected; the core does not automatically search for
certificates or keys on disk or the network. External-file reading, text
composition, ICC/XFA/3D/multimedia engines and certificate trust retain their
own responsibilities.
