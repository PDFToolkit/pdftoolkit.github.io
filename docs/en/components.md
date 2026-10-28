# Component guide

This guide explains object families, their responsibilities and their composition. The [complete API reference](https://pdftoolkit.github.io/reference/index.html) then provides the signatures of every class, interface, enum, method and property. [Tutorials](tutorials/README.md) show complete documents, their PDF instructions and visual result; [recipes](recipes/README.md) combine several families for a concrete use case.

This documentation describes the published core and module versions selected in the [source manifest](../../resources/sources.json). The API reference identifies each component's package and connects its declaration to the exact commit of the documented version. Core 0.11.0, PDF reader 0.6.0, image/font modules 0.1.12 and independent OpenType 0.3.0 require PHP 8.3 or later and are checked on PHP 8.3, 8.4 and 8.5. Core 0.11 and OpenType 0.3 require 64-bit PHP; OpenType remains independent of the PDF core. Reader 0.6.0 accepts core 0.9, 0.10 or 0.11; image/font modules retain their earlier accepted series through 0.11. The reader provides explicit password/public-key authentication, source MAC verification and bounded PDF 1.0–2.0 syntax decoding. Before 1.0, new minor releases may change names and signatures to improve the model; patch releases preserve their series' API.

The model covers **PDF 1.7 / ISO 32000-1:2008**, the [Adobe level 3 supplement](adobe-supplement.md), [PDF 2.0 / ISO 32000-2:2020 EC3](pdf-2-0.md) and its [companion specifications](pdf-2-0-bundle.md). Original reference PDFs retain their supplied names and bytes under `resources/reference-documents/` in the core. Large bundle originals are linked from this site and excluded from Composer archives. The PHP runtime version is independent of the PDF format version. [Coverage](coverage.md) distinguishes definitions, native constructions, verified semantic rules and external processing.

## Reading the model

A file is constructed by connecting objects: a page has content and resources, a tree has pages, a catalog points to that tree, and a writer serializes the graph. Object numbers and positions in the file are determined during writing.

| Family | Question it answers | Entry point |
| --- | --- | --- |
| PDF values | Which value is written: number, name, string, array…? | `BasicType`, `PDF\Syntax\Object` |
| Dictionaries and definitions | Which entries describe this object, and which types are allowed? | `Entry`, `SchemaDictionary`, `PDF\Specification` |
| Identity and file | Where do indirect objects live, and how does a reader find them? | `IndirectReference`, `FileStructure`, `FileWriter` |
| Streams and filters | Which bytes are stored, and how are they encoded? | `StreamObject`, `Filter` |
| Content instructions | What should the PDF reader draw or display? | `ContentStreams`, `Operator` |
| Documents and pages | How are pages, resources and information connected? | `DocumentCatalog`, `PageTreeNode`, `PageObject` |
| Navigation | Where do bookmarks, links and named destinations lead? | `Destination`, `OutlineItem`, `NameTree` |
| Functions | Which numerical transformation should the reader apply? | `FunctionObject`, `PDF\Functions` |
| Forms and structure | Which fields, pages and logical elements own the objects? | `AcroForm`, `FieldTree`, `StructureTreeRoot` |
| Native graphics | Which spaces, samples, patterns, masks and layers are declared? | `ColourSpace`, `ImageXObject`, `FormXObject`, `OptionalContentProperties` |
| Specialized writing | How are the file's bytes organized, encrypted or signed? | `LinearizedWriter`, `FileEncryption`, `SignatureWriter` |

Values compose other PDF objects. PHP scalars mainly appear at a leaf: a number, boolean, name or string bytes. The [architecture](architecture.md) describes construction rules more precisely.

## 1. Primitive values and lexical conventions

### The `BasicType` contract

[`BasicType`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/FileStructure/BasicType.php) is the contract for PDF values. It exposes `toPdf(SerializationContext $context): string` and PHP's `Stringable` contract. The context allows serialization of a value containing references and prevents direct cycles.

The contract's location in `Syntax\FileStructure` does not make every value a file. A `NameType` remains a name, and an `ArrayType` remains an array of values. A complete document is written through `FileStructure`.

### The eight PDF object families

| PDF term | Classes | Role and main constraints |
| --- | --- | --- |
| Boolean | [`BooleanType`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Object/BooleanType.php) | A `true` or `false` value. |
| Numeric | [`NumericType`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Object/NumericType.php), [`IntegerType`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Object/IntegerType.php), [`RealType`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Object/RealType.php) | A finite numeric value, written without exponential notation. Subtypes express an integer or real when that distinction is useful. |
| String | [`StringType`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Object/StringType.php), [`LiteralString`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Object/StringObject/LiteralString.php), [`HexadecimalString`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Object/StringObject/HexadecimalString.php) | A byte sequence represented as a literal or hexadecimal string. |
| Name | [`NameType`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Object/NameType.php) | A case-sensitive PDF identifier; `/` and byte escaping are produced during writing. |
| Array | [`ArrayType`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Object/ArrayType.php) | An ordered sequence of `BasicType` values. |
| Dictionary | [`DictionaryType`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Object/DictionaryType.php) | A collection of named entries; a key cannot be declared twice in the constructor. |
| Stream | [`StreamObject`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Object/StreamObject.php) | A dictionary accompanied by bytes; the stream is written as an indirect object. |
| Null | [`NullType`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Object/NullType.php) | The PDF `null` value, notably used for some destination parameters. |

For example, a PDF rectangle contains four numbers; its dedicated type expresses that structure:

```php
use PDF\Syntax\DataStructure\Rectangle;
use PDF\Syntax\Object\NumericType;

$mediaBox = new Rectangle(
    new NumericType(0),
    new NumericType(0),
    new NumericType(612),
    new NumericType(792),
);
```

[`Rectangle`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/DataStructure/Rectangle.php) describes `[x_min y_min x_max y_max]`, rather than `[x y width height]`. Content coordinates then depend on the current space and its transformations. The [drawing tutorial](tutorials/03-graphics.md) explains this distinction with a rendering.

### String bytes and Unicode text

A `LiteralString` receives **bytes**. It escapes parentheses, backslashes and characters required by the syntax. A `HexadecimalString` also receives bytes and produces their hexadecimal representation. These classes do not select a font's encoding.

[`TextString`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/DataStructure/TextString.php) represents the standard's *text string*: it accepts valid UTF-8 and converts it to ASCII or UTF-16BE with a BOM. It is suitable, for example, for document titles and bookmark titles.

The string displayed by the `Tj` operator must match the selected font's encoding. Passing a Unicode `TextString` to `ShowText` therefore does not automatically supply a Unicode font or encode its glyphs. The [pages and text tutorial](tutorials/02-pages-and-text.md) explains the examples' encoding choices.

[`Date`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/DataStructure/Date.php) constructs a PDF date from a `DateTimeImmutable`, retaining its UTC offset. [`LexicalConvention`](https://github.com/PDFToolkit/pdf/tree/v0.11.0/src/Syntax/LexicalConvention) types represent line endings, whitespace and delimiters in the PDF language. They are syntax elements; an application usually composes higher-level objects that use them.

## 2. Entries, dictionaries and schemas

### An entry is itself an object

[`Entry`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Object/DictionaryObject/Entry.php) connects a `NameType` to a `BasicType`. The key has its own PDF value identity; the value may be a dictionary, array or reference.

```php
use PDF\Syntax\Object\DictionaryObject\Entry;
use PDF\Syntax\Object\DictionaryType;
use PDF\Syntax\Object\NameType;
use PDF\Syntax\Object\NumericType;

$original = new DictionaryType(
    new Entry(new NameType('ExampleNumber'), new NumericType(12)),
);
$modified = $original->with(
    new Entry(new NameType('ExampleNumber'), new NumericType(24)),
);
```

`with()` replaces or adds the entry in a **new instance**. `$original` retains its value 12. `without()` also produces a new instance. You must retain the returned value. `get()` returns a PDF value; `entries()` lets you inspect `Entry` objects.

The generic dictionary accepts arbitrary names. A specialized dictionary adds constraints for its role: allowed types, calculated structural fields or required entries.

### Standard definition and PDF instance

[`SchemaDictionary`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Specification/SchemaDictionary.php) composes a [`TableDefinition`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Specification/TableDefinition.php). It checks known-entry types in the constructor, when adding through `with()` and during `validate()`. Serialization calls `validate()` and checks unconditional requirements. Core 0.8 also executes inherited immutable `SemanticRule` relations; the [source-audit guide](source-audits.md) identifies the source-authored domains and remaining conditions.

[`SchemaEntry`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Specification/SchemaEntry.php) composes an [`EntryDefinition`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Specification/EntryDefinition.php). It checks the value before associating it with the standardized key. Variable-key entries require an explicit `NameType`.

A generic entry allows an explicit extension. When it uses an already-defined key, that key's constraint still applies. Conditional and inherited requirements, and relationships between objects, must be handled by specialized components and by the application when their validation is not yet implemented.

### Reading and composing generated classes

The three parts of a table have distinct roles:

| Example class | Responsibility |
| --- | --- |
| [`AnnotationDictionaryTable164Definition`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Specification/Definition/AnnotationDictionaryTable164Definition.php) | Immutable definition of table 164, with sources and constraints. |
| [`AnnotationDictionaryTable164`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Specification/Dictionary/AnnotationDictionaryTable164.php) | PDF instance of common annotation entries. |
| [`SubtypeEntry`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Specification/Dictionary/AnnotationDictionaryTable164/SubtypeEntry.php), [`RectEntry`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Specification/Dictionary/AnnotationDictionaryTable164/RectEntry.php) | Named `/Subtype` and `/Rect` entries, with their allowed types. |

A common annotation dictionary can therefore be constructed with entry objects:

```php
use PDF\Specification\Dictionary\AnnotationDictionaryTable164;
use PDF\Specification\Dictionary\AnnotationDictionaryTable164\ContentsEntry;
use PDF\Specification\Dictionary\AnnotationDictionaryTable164\RectEntry;
use PDF\Specification\Dictionary\AnnotationDictionaryTable164\SubtypeEntry;
use PDF\Syntax\DataStructure\Rectangle;
use PDF\Syntax\DataStructure\TextString;
use PDF\Syntax\Object\NameType;
use PDF\Syntax\Object\NumericType;

$annotation = new AnnotationDictionaryTable164(
    new SubtypeEntry(new NameType('Text')),
    new RectEntry(new Rectangle(
        new NumericType(72), new NumericType(600),
        new NumericType(96), new NumericType(624),
    )),
    new ContentsEntry(new TextString('Une note associée à cette page.')),
);
```

This snippet constructs the object; it must still be inserted, by reference, into a page's `/Annots` array to make it accessible to the reader. The [links tutorial](tutorials/05-links.md) shows this complete assembly with another annotation subtype.

The table in a class name connects it to the standard and distinguishes tables with similar titles. Additional-entry dictionaries compose their common definitions: for example, [`Type2ShadingDictionaryTable80`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Specification/Dictionary/Type2ShadingDictionaryTable80.php) uses the common entries of table 78 and specific entries of table 80. The [shading tutorial](tutorials/07-gradient.md) assembles them.

The 263 dictionaries and their 1,405 entry classes cover the inventoried ISO 32000-1 entry tables. ISO 32000-2 has its own catalogue: 306 dictionary models and 1,711 entries, including 1,704 fixed and seven variable. PDF names remain case-sensitive: `/OP` and `/op` are different keys, even when PHP classes must use a suffix to retain that distinction.

## 3. References, identity and serialization

### A reference targets an instance

[`IndirectReference`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Object/IndirectReference.php) targets an object. Two references to **the same instance** allow that object to be shared within the file. Two objects with identical contents remain distinct instances; the writer does not deduplicate by comparing values.

```php
use PDF\Document\Fonts\StandardFont;
use PDF\Document\Fonts\Type1Font;
use PDF\Syntax\Object\IndirectReference;

$font = new Type1Font(StandardFont::Helvetica);
$firstUse = new IndirectReference($font);
$secondUse = new IndirectReference($font);
```

When these references are reachable in the same file graph, they target the same object number. That number is assigned during writing. A reference can also receive an explicit [`ObjectIdentifier`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Object/IndirectObject/ObjectIdentifier.php), composed of an [`ObjectNumber`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Object/IndirectObject/ObjectNumber.php) and a [`GenerationNumber`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Object/IndirectObject/GenerationNumber.php).

[`IndirectObject`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Object/IndirectObject.php) represents a value with its identifier when explicit control of the file body is needed.

### The context belongs to a write operation

[`SerializationContext`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Serialization/SerializationContext.php) tracks the mapping between instances and identifiers. It reserves explicit identifiers before assigning automatic ones and checks conflicts. It exists for a particular write operation; no global registry shares numbers between documents.

Cycles use indirect references. For example, a page references its parent, and the parent references its children. A cycle of directly nested values is rejected. The context also checks that two instances do not claim the same number and one instance does not claim two identifiers.

Graph objects must be configured before writing. Modifying the tree during serialization would prevent a consistent file from being produced.

## 4. File, cross-references and compressed objects

[`FileStructure`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/FileStructure.php) composes a [`FileHeader`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/FileStructure/FileHeader.php), a [`FileBody`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/FileStructure/FileBody.php), the root reference and optional trailer entries. The header expresses the PDF version; [`PdfVersion`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/FileStructure/PdfVersion.php) exposes versions 1.0–1.7.

[`FileWriter`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Serialization/FileWriter.php) transforms this graph into bytes. It traverses reachable references, writes objects and measures offsets. It produces cross-references and the trailer. `startxref` identifies the actual position of the corresponding section.

`FileStructure::toPdf()` returns file bytes. `writeTo()` writes them to a file path chosen by the application. These operations construct the document in memory; the application's memory limit therefore remains relevant to capacity planning.

### Revisions and historical identities

[`FileRevision`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/FileStructure/FileRevision.php) is the snapshot produced by `FileStructure::toRevision()`. Its bytes remain frozen. Its [`RevisionObject`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/FileStructure/RevisionObject.php) objects retain the effective value, identity aliases and a copy of dictionary entries at write time. A mutable builder is therefore not traversed again when a historical reference is reused.

[`IncrementalUpdate`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/FileStructure/IncrementalUpdate.php) composes the previous revision, a `FileBody` of explicit changes and optional trailer entries. [`IncrementalWriter`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Serialization/IncrementalWriter.php) adds new objects, keeps replacement numbers, inherits the trailer and produces `/Prev`. [`CrossReferenceSection`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/FileStructure/CrossReferenceSection.php) represents the section's records; [`CrossReferenceLimits`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/FileStructure/CrossReferenceLimits.php) bounds cumulative capacity. See the [revision tutorial](tutorials/11-incremental-update.md).

| Component | PDF representation |
| --- | --- |
| [`CrossReferenceFormat`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/FileStructure/CrossReferenceFormat.php) | Explicit choice between table, stream and hybrid references. |
| [`CrossReferenceTable`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/FileStructure/CrossReferenceTable.php), [`CrossReferenceEntry`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/FileStructure/CrossReferenceEntry.php) | Classic `xref` section and its entries. |
| [`CrossReferenceStream`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/FileStructure/CrossReferenceStream.php) | Cross-reference stream. |
| [`CrossReferenceStreamFreeEntry`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/FileStructure/CrossReferenceStreamFreeEntry.php), [`CrossReferenceStreamInUseEntry`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/FileStructure/CrossReferenceStreamInUseEntry.php), [`CrossReferenceStreamCompressedEntry`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/FileStructure/CrossReferenceStreamCompressedEntry.php) | Type 0, 1 and 2 entries: free, standalone object or object-stream member. |
| [`ByteOffset`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/FileStructure/ByteOffset.php) | Position measured in bytes. |
| [`FileTrailer`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/FileStructure/FileTrailer.php) | Trailer dictionary and file ending. |
| [`ObjectStream`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/FileStructure/ObjectStream.php), [`ObjectStreamEntry`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/FileStructure/ObjectStreamEntry.php) | Group of objects embedded in an `/ObjStm` stream. |

An `ObjectStream` requires PDF 1.5 or later and stream or hybrid cross-references. Its members receive corresponding type 2 entries and are not written a second time as standalone objects. The [compressed-object tutorial](tutorials/08-object-stream.md) shows the file body and these relationships.

### Linearized writing

[`LinearizedWriter`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Serialization/LinearizedWriter.php) calculates the document's physical order and Annex F binary hint tables. Objects in [`Syntax\Linearization`](https://github.com/PDFToolkit/pdf/tree/v0.11.0/src/Syntax/Linearization) represent dependencies, offsets, shared references and page hints. This writer produces the bytes itself; [tutorial 16](tutorials/16-linearization.md) explains checking them with qpdf. Supported variants and those still to complete are recorded in [coverage](coverage.md).

The [first tutorial](tutorials/01-first-document.md) explains classic assembly through the `writeTo()` call.

## 5. Streams and filters

A [`StreamObject`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Object/StreamObject.php) receives bytes or a `ContentStreams`, a dictionary and a sequence of [`Filter`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Filters/Filter.php) objects. It calculates `/Length`, `/Filter` and `/DecodeParms`. The stream manages these entries; supplying them manually is rejected.

`/Length` counts bytes **after encoding**, excluding the delimiting line ending. [`StreamExtent`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Object/StreamObject/StreamExtent.php) carries this number. A stream is written indirectly; use an `IndirectReference` when it is a dictionary entry's value. `PageObject` creates this reference for the content stream received directly in its constructor.

Native filters are [`ASCIIHexDecode`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Filters/ASCIIHexDecode.php), [`ASCII85Decode`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Filters/ASCII85Decode.php), [`FlateDecode`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Filters/FlateDecode.php), [`RunLengthDecode`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Filters/RunLengthDecode.php) and [`LZWDecode`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Filters/LZWDecode.php). Their names express the **decoding performed by the PDF reader**; their objects apply the encoding needed for writing.

[`TiffPredictor`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Filters/TiffPredictor.php) and [`PngPredictor`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Filters/PngPredictor.php) transform sample rows before Flate or LZW, with an explicit [`PredictorLayout`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Filters/PredictorLayout.php) at depths of 1/2/4/8/16 bits. These PDF predictors do not decode a PNG file; [tutorial 19](tutorials/19-filters-predictors.md) shows the necessary bytes and parameters.

The filter sequence is supplied in decoding order. Encodings are applied in reverse. For example, ASCII85 followed by Flate declares that the reader first removes ASCII85, then decompresses Flate.

[`EncodedData`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Filters/EncodedData.php) declares **already-encoded** data with a [`FilterName`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/Filters/FilterName.php). For example, it can declare JPEG bytes associated with `DCTDecode`. It does not read an image, apply a codec or convert a bitmap to JPEG. It must be the final decoding filter and receive binary data; `Crypt` processing requires document-security support.

The [images tutorial](tutorials/06-images.md) compares a reusable image XObject and an inline image. An [`InlineImage`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/ContentStreamsResources/Operators/InlineImage.php) groups `BI`, `ID` and `EI` into an atomic object; restrictions on its dictionary and bytes prevent ambiguous delimitation.

### JPEG and PNG files

Components in [`Document\Images`](https://github.com/PDFToolkit/pdf/tree/v0.11.0/src/Document/Images) are core PDF objects. [`ImageSamples`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Images/ImageSamples.php) associates dimensions, component layout and bytes; [`SampledImage`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Images/SampledImage.php) separates color and alpha. [`DCTImage`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Images/DCTImage.php) retains encoded bytes, their dimensions, layout and explicit color transform without inspecting an external file format.

The optional [`pdftoolkit/pdf-images`](https://github.com/PDFToolkit/pdf-images) module receives an [`ImageFileBytes`](https://github.com/PDFToolkit/pdf-images/blob/v0.1.12/src/ImageFileBytes.php) without reading a path or URL. [`ImageImportLimits`](https://github.com/PDFToolkit/pdf-images/blob/v0.1.12/src/ImageImportLimits.php) bounds bytes, pixels, dimensions and chunks. [`PngImageDecoder`](https://github.com/PDFToolkit/pdf-images/blob/v0.1.12/src/PngImageDecoder.php) reconstructs color and alpha samples; [`JpegImageReader`](https://github.com/PDFToolkit/pdf-images/blob/v0.1.12/src/JpegImageReader.php) inspects file markers and colors, then produces a core `DCTImage`.

[`ImageXObjectFactory`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Images/ImageXObjectFactory.php) composes table 89's standardized dictionary and its streams. It creates an indirect `/SMask` for alpha and supplies appropriate DCT or Flate parameters. It selects neither the resource name nor the painting matrix. The [image-file tutorial](tutorials/10-image-files.md) shows these operations and supported modes.

### Native samples and XObjects

[`SampleLayout`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Images/SampleLayout.php) accepts depths of 1/2/4/8/16 bits and an explicit color space. [`SamplePacker`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Graphics/XObjects/SamplePacker.php) packs values, aligning each row to a byte. [`ImageXObject`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Graphics/XObjects/ImageXObject.php) composes these data with Decode, a stencil, an interval mask or a soft mask. `MatteColour` carries precomposition calculations; parent relationships and dimensions are checked.

[`EncodedImageXObject`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Graphics/XObjects/EncodedImageXObject.php) receives already-encoded bytes and their PDF declarations. It does not verify DCT/JPX/JBIG2/CCITT codec content. [`FormXObject`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Graphics/XObjects/FormXObject.php) owns its instructions, resources, BBox and Matrix, with optional Group, Ref and OC. Resource names in typed instructions and components of explicitly selected spaces are checked; graphics state inherited from the caller remains a parameter of this composition. [Tutorial 21](tutorials/21-native-graphics.md) shows these objects together.

## 6. Content instructions, drawing and text

### `ContentStreams` contains instructions

[`ContentStreams`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/ContentStreamsResources/ContentStreams.php) composes an ordered sequence of [`Operator`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/ContentStreamsResources/Operator.php) objects. It does not represent a stream dictionary. `StreamObject` handles storage of its instructions in the file.

Every operator describes a PDF token and its typed operands. `with()` returns a new `ContentStreams` containing the additional instructions. `validate()` checks states and nesting before byte emission.

```php
use PDF\Syntax\ContentStreamsResources\ContentStreams;
use PDF\Syntax\ContentStreamsResources\Operators\BeginTextObject;
use PDF\Syntax\ContentStreamsResources\Operators\EndTextObject;
use PDF\Syntax\ContentStreamsResources\Operators\MoveTextPosition;
use PDF\Syntax\ContentStreamsResources\Operators\SetTextFontAndSize;
use PDF\Syntax\ContentStreamsResources\Operators\ShowText;
use PDF\Syntax\Object\NameType;
use PDF\Syntax\Object\NumericType;
use PDF\Syntax\Object\StreamObject;
use PDF\Syntax\Object\StringObject\LiteralString;

$instructions = new ContentStreams(
    new BeginTextObject(),
    new SetTextFontAndSize(new NameType('F1'), new NumericType(18)),
    new MoveTextPosition(new NumericType(72), new NumericType(720)),
    new ShowText(new LiteralString('Bonjour PDF')),
    new EndTextObject(),
);
$contents = new StreamObject($instructions);
```

This snippet produces `BT`, `/F1 18 Tf`, `72 720 Td`, `(Bonjour PDF) Tj`, then `ET`. `/F1` must be defined in page resources. Content validation does not resolve every resource name or check every relationship with a color space; assembly remains explicit.

### Operator families

| Family | Example classes and tokens | Effect |
| --- | --- | --- |
| Graphics state | `SaveGraphicsState` (`q`), `RestoreGraphicsState` (`Q`), `SetLineWidth` (`w`), `SetGraphicsStateParameters` (`gs`) | Save, restore or configure graphics state. |
| Transformations | `ConcatenateMatrix` (`cm`) | Modify the current transformation. |
| Path construction | `MoveTo` (`m`), `LineTo` (`l`), `CurveTo` (`c`), `AppendRectangle` (`re`), `CloseSubpath` (`h`) | Construct a path without painting it yet. |
| Path painting and clipping | `StrokePath` (`S`), `FillPathNonzero` (`f`), `ClipPathNonzero` (`W`), `EndPath` (`n`) | Paint a path or finish applying clipping. |
| Colors | `SetStrokingRGBColor` (`RG`), `SetNonstrokingRGBColor` (`rg`), gray, CMYK, space and pattern variants | Set stroke and fill colors. |
| Text state | `SetTextFontAndSize` (`Tf`), `SetCharacterSpacing` (`Tc`), `SetWordSpacing` (`Tw`), `SetTextLeading` (`TL`) | Configure font, size, spacing and leading. |
| Text positioning and showing | `SetTextMatrix` (`Tm`), `MoveTextPosition` (`Td`), `ShowText` (`Tj`), `ShowTextWithIndividualGlyphPositioning` (`TJ`) | Position and display text bytes. |
| XObjects and shadings | `InvokeXObject` (`Do`), `PaintShading` (`sh`) | Invoke a named resource. |
| Marked content | `BeginMarkedContent` (`BMC`), `BeginMarkedContentWithProperties` (`BDC`), `EndMarkedContent` (`EMC`) | Associate marked structure with a content sequence. |
| Compatibility | `BeginCompatibilitySection` (`BX`), `EndCompatibilitySection` (`EX`) | Represent PDF compatibility sections. |
| Type 3 glyph metrics | `SetGlyphWidth` (`d0`), `SetGlyphWidthAndBoundingBox` (`d1`) | Declare initial metrics of a Type 3 glyph stream. |

Classes are in [`Operators`](https://github.com/PDFToolkit/pdf/tree/v0.11.0/src/Syntax/ContentStreamsResources/Operators). The API reference details each signature. The inventory represents all 73 tokens, including historical `F` and the three inline-image delimiters.

Validation notably prevents nested text objects, unfinished paths, `Q` restores without a `q` save, crossing marked scopes and drawing instructions incompatible with a text object. `W` or `W*` clipping must be followed by a path-ending operator.

[`Type3GlyphContentStream`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/ContentStreamsResources/Type3GlyphContentStream.php) represents a `CharProcs` stream. It requires `d0` or `d1` at the start and applies uncolored-glyph constraints when `d1` is used. This component does not by itself construct an entire Type 3 font.

### Graphics-state and text-state values

[`Matrix`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Graphics/CoordinateSystems/Matrix.php) contains a transformation's six components. [`LineDashPattern`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Graphics/GraphicsState/LineDashPattern.php), [`LineCapStyle`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Graphics/GraphicsState/LineCapStyle.php), [`LineJoinStyle`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Graphics/GraphicsState/LineJoinStyle.php) and [`RenderingIntent`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Graphics/GraphicsState/RenderingIntent.php) provide objects or enums for the corresponding parameters. [`TextRenderingMode`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Text/TextRenderingMode.php) expresses text painting and clipping modes.

These objects describe values passed to instructions. They do not calculate layout or draw on a PHP canvas. The PDF reader executes instructions once the document opens. The [drawing](tutorials/03-graphics.md) and [text](tutorials/02-pages-and-text.md) tutorials show their effects.

### Color spaces, patterns and shading

Objects in [`Graphics\ColourSpaces`](https://github.com/PDFToolkit/pdf/tree/v0.11.0/src/Graphics/ColourSpaces) construct CalGray, CalRGB, Lab, ICCBased, Indexed, Separation, DeviceN and Pattern. They check component counts, ranges, palettes, tint functions and NChannel relationships. CalGray/CalRGB/Lab calculations are available; an ICC profile remains supplied by the application, without an implicit ICC management engine.

[`TilingPattern`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Graphics/Patterns/TilingPattern.php) represents a cell and its repeat steps. [`ShadingPattern`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Graphics/Patterns/ShadingPattern.php) composes a shading. The seven types in [`Shadings`](https://github.com/PDFToolkit/pdf/tree/v0.11.0/src/Graphics/Patterns/Shadings) include actual triangle and patch streams, with Decode quantization, bit packing and geometric reuse. [Tutorial 17](tutorials/17-colours-patterns.md) presents their renderings.

Stencil-pattern validation follows typed content, including forms, alternate images and Type3 programs. It conservatively examines all CharProcs of the selected font; it does not interpret actually displayed characters or instructions supplied as opaque bytes.

### Transparency, halftones and optional content

[`GraphicsStateParameters`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Graphics/GraphicsState/GraphicsStateParameters.php) constructs ExtGState with its values, functions and priorities. `GraphicsStateScope` explicitly retains saved states. `BlendFunction` supplies local calculations for blending and compositing modes; `SoftMask` associates a transparency form with an alpha or luminosity mask. Objects in [`Halftones`](https://github.com/PDFToolkit/pdf/tree/v0.11.0/src/Graphics/Halftones) construct types 1/5/6/10/16 and their actual threshold data. This describes PDF operations; group rendering, ICC profile application and device screening remain external.

[`OptionalContentProperties`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Graphics/OptionalContent/OptionalContentProperties.php) declares catalog groups and their configurations. OCG, OCMD and visibility expressions compose their identities; `GroupStates` and `UsageEvaluator` calculate states from explicitly supplied parameters. Catalog references, intents, radio groups and usage conditions are checked. [Tutorial 21](tutorials/21-native-graphics.md) shows visible and hidden content.

## 7. Catalog, pages and inheritance

[`DocumentCatalog`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/DocumentStructure/DocumentCatalog.php) is the root `/Catalog` dictionary. Its constructor receives the page-tree root and creates `/Type` and `/Pages`. It composes table 28's definition to check other entries. The graph protects structural fields against replacement or removal through generic entries.

[`PageTree`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/DocumentStructure/PageTree.php) is the tree-element contract: [`PageTreeNode`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/DocumentStructure/PageTree/PageTreeNode.php) represents `/Pages`, and [`PageObject`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/DocumentStructure/PageTree/PageObject.php) represents a `/Page` leaf.

`PageTreeNode::addKid()` attaches a child to the existing builder. Every child belongs to a single parent. The tree produces `/Kids`, `/Parent` and `/Count`, and prevents cycles. Configure a page before attachment: afterwards it cannot be cloned or receive a dictionary modification through `with()`.

`PageObject` receives its `/MediaBox` `Rectangle`, resources and content. `/MediaBox` and `/Resources` can also be inherited from an ancestor. Their effective resolution is checked when the page is traversed for writing. A `/Contents` array must contain references to streams.

Entry objects in [`PageDictionary`](https://github.com/PDFToolkit/pdf/tree/v0.11.0/src/Syntax/DocumentStructure/PageDictionary) notably express `MediaBox`, `CropBox`, `BleedBox`, `TrimBox`, `ArtBox`, `Rotate`, `UserUnit` and `Resources`. Specialized constructors retain responsibility for the fields they manage themselves.

Entries in [`CatalogDictionary`](https://github.com/PDFToolkit/pdf/tree/v0.11.0/src/Syntax/DocumentStructure/CatalogDictionary) connect document structures: `Names`, `Outlines`, `Metadata`, `PageLabels`, `AcroForm`, `ViewerPreferences` and other standardized keys. [`PageLayout`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/PageLayout.php) and [`PageMode`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/PageMode.php) represent catalog display values. An `AcroForm` definition, for example, allows its entries to be constructed; it does not automatically implement every form behavior rule.

### Fields and logical structure

[`AcroForm`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Forms/AcroForm.php) composes a `FieldTree` with inherited values, qualified names, flags and calculation order. Text, button, choice and signature fields have their objects; separate or merged widgets connect these fields to pages and appearances. `WidgetAppearance` composes N/R/D; an AS state is required whenever one of these branches contains a state dictionary. [Tutorial 14](tutorials/14-acroform-fields.md) shows their construction. [`Forms\Fdf`](https://github.com/PDFToolkit/pdf/tree/v0.11.0/src/Document/Forms/Fdf) also constructs FDF files and exports explicitly selected fields. XFA processing and JavaScript action execution remain separate responsibilities.

[`StructureTreeRoot`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Structure/StructureTreeRoot.php) connects logical elements, their parents, MCID/MCR content and OBJR references. The graph derives ParentTree and IDTree, composes RoleMap/ClassMap and resolves Layout/List/PrintField/Table attributes according to supported rules. `PageContentSequence` represents fragments of the same logical page content. Validation checks their identities, MarkInfo properties and tagged relationships described in [coverage](coverage.md). [Tutorial 15](tutorials/15-tagged-structure.md) constructs three pages with a paragraph, table and link. Instructions are typed; visual reading order, reflow and PDF/UA certification are not automatically inferred.

The [first document](tutorials/01-first-document.md) introduces a page; the [pages and text tutorial](tutorials/02-pages-and-text.md) shows pages sharing resources and inherited properties.

To inspect pages of an existing PDF, the optional [`PageTreeReader`](https://github.com/PDFToolkit/pdf-reader/blob/v0.6.0/src/PageTreeReader.php) module component traverses and checks its tree. It produces a [`ReadPageTree`](https://github.com/PDFToolkit/pdf-reader/blob/v0.6.0/src/ReadPageTree.php) whose [`ReadPage`](https://github.com/PDFToolkit/pdf-reader/blob/v0.6.0/src/ReadPage.php) objects retain their source dictionaries and effective [`PageAttributes`](https://github.com/PDFToolkit/pdf-reader/blob/v0.6.0/src/PageAttributes.php). [`PageContentsReader`](https://github.com/PDFToolkit/pdf-reader/blob/v0.6.0/src/PageContentsReader.php) separately resolves each page's local streams without implicit decoding. The [module guide](packages.md#reading-an-external-pdf) shows this construction; these reading views do not replace core generation objects.

## 8. Resources, fonts and document information

### Named resources

[`ResourceDictionary`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/ResourceDictionary.php) composes table 33. Objects in [`Document\Resources`](https://github.com/PDFToolkit/pdf/tree/v0.11.0/src/Document/Resources) define the `ExtGState`, `ColorSpace`, `Pattern`, `Shading`, `XObject`, `Font`, `Properties` and `ProcSet` categories.

Each category associates local names with PDF objects. The name `/F1` in a `Tf` operator therefore identifies an entry in the `/Font` dictionary of resources accessible to that page. It does not directly identify the font's `/Helvetica` base name.

Reusing the same font, image or shading instance by reference allows sharing between pages. Resource names and their target objects remain explicit. `ProcSet` represents an entry provided by PDF 1.7 and deprecated in that specification; new examples need not use it.

### Fonts

[`StandardFont`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Fonts/StandardFont.php) enumerates the fourteen standard Type 1 fonts. [`Type1Font`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Fonts/Type1Font.php) constructs their `/Type /Font`, `/Subtype /Type1` and `/BaseFont` dictionary while allowing explicit additional entries. The three managed fields cannot be replaced or removed.

For an embedded font, the optional [`pdftoolkit/pdf-fonts`](https://github.com/PDFToolkit/pdf-fonts) module analyzes static TrueType through [`FontProgram`](https://github.com/PDFToolkit/pdf-fonts/blob/v0.1.12/src/TrueType/FontProgram.php). Its [`CharacterMapFactory`](https://github.com/PDFToolkit/pdf-fonts/blob/v0.1.12/src/TrueType/CharacterMapFactory.php) produces a core [`CharacterMap`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Fonts/CharacterMap.php), composed of explicit [`CharacterMapping`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Fonts/CharacterMapping.php) objects. Distinct Unicode values retain distinct CIDs even if they target the same glyph, preserving extraction. The [`TextEncoder`](https://github.com/PDFToolkit/pdf-fonts/blob/v0.1.12/src/TrueType/TextEncoder.php) service produces the two-byte codes expected by Identity-H.

[`CIDFontProgram`](https://github.com/PDFToolkit/pdf-fonts/blob/v0.1.12/src/TrueType/CIDFontProgram.php) prepares full-program bytes for [`FontFile2`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Fonts/FontFile2.php), with appropriate CIDFont tables and checksums. [`FontDescriptor`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Fonts/FontDescriptor.php), [`CIDFontType2`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Fonts/CIDFontType2.php) and [`Type0Font`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Fonts/Type0Font.php) compose standardized core dictionaries. [`CIDToGIDMap`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Fonts/CIDToGIDMap.php), widths and [`ToUnicodeCMap`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Fonts/ToUnicodeCMap.php) provide their respective mappings. The module supplies a `FontDescriptorFactory` that converts TrueType metrics into descriptor values; the core accepts those PDF values directly. The [TrueType and Unicode tutorial](tutorials/09-embedded-font.md) shows the complete graph.

[`Type3Font`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Fonts/Type3Font.php) composes drawn CharProcs, encoding Differences, widths, Matrix and resources. Simple Type1, MMType1 and TrueType fonts have explicitly associated metrics and programs; Type0/Type2 CID fonts carry their maps and horizontal or vertical `DW2`/`W2` widths. [Tutorial 22](tutorials/22-native-fonts.md) shows these native constructions.

[`CMaps`](https://github.com/PDFToolkit/pdf/tree/v0.11.0/src/Document/Fonts/CMaps) compose codespaces, CID mappings, notdef ranges, Unicode sequences, writing mode and UseCMap inheritance. `ToUnicodeCMap` writes corresponding programs; [tutorial 18](tutorials/18-cmaps.md) uses an encoding other than Identity-H. PDF names and constraints are distinct from a font-program reader. The core also checks subset-tag identity within the document; it does not create program subsets or shape complex scripts. The application supplies fonts and their usage rights.

### `/Info` and metadata streams

[`DocumentInformation`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/DocumentInformation.php) composes objects in [`Document\Information`](https://github.com/PDFToolkit/pdf/tree/v0.11.0/src/Document/Information): `Title`, `Author`, `Subject`, `Keywords`, `Creator`, `Producer`, `CreationDate`, `ModDate` and `Trapped`. Text fields use a `TextString`, dates a `Date`, and `Trapped` a dedicated enum. A reference to this dictionary is added under `/Info` in the trailer.

`XmpPacket` composes explicit properties, bags, sequences and localized alternatives; `XmpLanguageAlternative` represents `dc:title` with `x-default` and chosen languages. `MetadataStream` writes escaped UTF-8 RDF/XML, and `MetadataEntry` links the stream indirectly to its owner. Declarations and `ClaimData` can describe the document, an information object or a marked sequence according to that owner. `DeclarationsPdfaExtensionSchema` supplies an explicitly chosen extension schema. These author assertions are not conformance certificates or a general XMP vocabulary validator; opaque caller XML and consistency with `/Info` need their own checks.

### PDF 2.0 ownership and qualified structure

Named metadata properties resolve in the actual page, Form, tiling-pattern or Type 3 CharProc resource scope. The writer freezes facts from the emitted typed content, including incremental revisions. Inline metadata stream references, unresolved resource names and wrong target types are rejected. Associated-file checks use information-object scope rather than a fixed list of supported owners.

`DocumentPart`, `DocumentPartRoot`, `DocumentPartEntry` and `DocumentPartMetadata` construct `/DPartRoot`, the hierarchy, page ranges and `/DPM`. Core 0.11 uses flat DParts arrays with explicit parents, UTF-8 DPM names and XMP only on DPartRoot. Graph validation checks reciprocal parent/page links, range ordering and permitted DPM values; see the [migration guide](migration-0.11.md). `EncryptedPayload` and a file specification construct an unencrypted outer PDF around a supplied encrypted inner PDF, with AF, EmbeddedFiles and a hidden Collection; the wrapper neither decrypts nor parses its payload. `UseBlackPointCompensation` writes precisely `ON`, `OFF` or `Default`; a PDF reader and output device perform the colour operation.

`StructureNamespace`, `StructureRole` and `NamespaceRoleMap` qualify structure roles. `NamespaceRoleResolver` resolves mappings with cycle checks, and `StructureInclusionRules` applies TS 32005 to actual parent/child roles. `WtPdfAudit` returns failures and pending findings for an explicitly selected reuse or accessibility level. Its bounded checks cover typed text use, metadata, structure and annotations; reading order, useful alternate text, faithful Unicode meaning and external font-program evidence still need verification. No automatic WTPDF or PDF/UA certification is claimed.

The tutorials explain [metadata/declarations and parts](tutorials/28-pdf20-metadata-declarations.md), [encrypted payloads](tutorials/29-pdf20-encrypted-payload.md) and [qualified structure with audit reports](tutorials/30-pdf20-tagged-namespaces.md).

## 9. Destinations, outlines and key trees

### Destinations and actions

[`Destination`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Destinations/Destination.php) is the base of explicit destinations. [`XYZ`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Destinations/XYZ.php), [`Fit`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Destinations/Fit.php), [`FitH`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Destinations/FitH.php), [`FitV`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Destinations/FitV.php), [`FitR`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Destinations/FitR.php), [`FitB`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Destinations/FitB.php), [`FitBH`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Destinations/FitBH.php) and [`FitBV`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Destinations/FitBV.php) describe a target page and viewport mode.

The target page is an object, received directly by the constructor or identified by a reference. Missing `XYZ` parameters become PDF `null` values, whose meaning is defined by the standard.

A destination describes a view; an action describes an operation to perform. Generated tables model action dictionaries and link annotations. The [links tutorial](tutorials/05-links.md) connects an annotation to an internal destination and an external URI.

`StructureDestination` and `DestinationView` add PDF 2.0 semantic targets.
Resolution follows actual content in child order; a target without content
falls back to the first page. Actions and named destination dictionaries keep
their page fallback alongside `SD`. `RemoteStructureDestination` represents an
external ID as bytes without opening another file. The [structure-destination tutorial](tutorials/34-pdf20-structure-destinations.md)
shows the actual links and the frozen graph checks.

### Document outline

[`OutlineDictionary`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/OutlineDictionary.php) represents the outline root. [`OutlineItem`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/OutlineItem.php) receives a `TextString` title, a destination or action dictionary, its expanded or collapsed state and additional entries. [`OutlineParent`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/OutlineParent.php) carries the outline-parent contract.

`addItem()` attaches items and subitems. Builders calculate `/Parent`, `/Prev`, `/Next`, `/First`, `/Last` links and visible-descendant counts; these fields must not be fabricated through generic entries. An item cannot attach to several parents, and cycles are rejected. The [navigation tutorial](tutorials/04-navigation.md) explains the result in the bookmarks pane.

### Name trees and number trees

[`NameTree`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/DataStructure/NameTree.php) and [`NameTreeEntry`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/DataStructure/NameTreeEntry.php) associate `StringType` keys with PDF values. [`NumberTree`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/DataStructure/NumberTree.php) and [`NumberTreeEntry`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/DataStructure/NumberTreeEntry.php) use `IntegerType` keys.

The constructor receives leaf entries or a [`NameTreeChildren`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/DataStructure/NameTreeChildren.php) / [`NumberTreeChildren`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/DataStructure/NumberTreeChildren.php) collection for a branch. Keys and ranges are sorted; duplicates, empty descendants and overlaps are rejected. `/Kids` and `/Limits` derive from these objects; `with()` and `without()` cannot alter this structure.

[`NameDictionary`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Syntax/DocumentStructure/NameDictionary.php) associates named categories with name trees. For example, it can connect named destinations to the catalog. Number trees serve, among other uses, page labels. These are PDF-defined indexing structures, distinct from local names in the resource dictionary.

## 10. The four PDF function types

[`FunctionObject`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Functions/FunctionObject.php) exposes the domain, optional range, and input and output component counts. [`Domain`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Functions/Domain.php) and [`Range`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Functions/Range.php) compose [`NumberInterval`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Functions/NumberInterval.php) objects. [`NumberArray`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Functions/NumberArray.php) expresses additional numeric arrays.

These components produce a function definition interpreted by the PDF reader. The library does not provide a universal numerical function-evaluation engine.

| FunctionType | Class | Composition and main checks |
| --- | --- | --- |
| 0 — Sampled | [`SampledFunction`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Functions/SampledFunction.php) | Multidimensional grid, output count and sample values. [`SamplingSize`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Functions/SamplingSize.php), [`SampleBitDepth`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Functions/SampleBitDepth.php), [`SampleValues`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Functions/SampleValues.php) and [`InterpolationOrder`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Functions/InterpolationOrder.php) describe the grid and packing. Component count must match the product of sizes and outputs. |
| 2 — Exponential interpolation | [`ExponentialInterpolationFunction`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Functions/ExponentialInterpolationFunction.php) | One input and equally sized `C0`, `C1` vectors; `N` defines the exponent. Domain restrictions account for fractional and negative exponents. |
| 3 — Stitching | [`StitchingFunction`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Functions/StitchingFunction.php) | One input shared among compatible subfunctions; `Bounds` and `Encode` describe subdivisions and mappings. Functions must have the same output count. |
| 4 — PostScript calculator | [`PostScriptCalculatorFunction`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Functions/PostScriptCalculatorFunction.php) | A stream containing a typed procedure from PDF's allowed calculator subset. |

For type 2, interpolation from 0 to 1 is written as:

```php
use PDF\Functions\Domain;
use PDF\Functions\ExponentialInterpolationFunction;
use PDF\Functions\NumberInterval;
use PDF\Syntax\Object\NumericType;

$function = new ExponentialInterpolationFunction(
    new Domain(new NumberInterval(new NumericType(0), new NumericType(1))),
    new NumericType(1),
);
```

Default values are `C0 = [0]` and `C1 = [1]`. With `N = 1`, the function is linear. The [shading tutorial](tutorials/07-gradient.md) uses three output components to produce an RGB color.

For type 4, [`Calculator\Procedure`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Functions/Calculator/Procedure.php) composes [`Instruction`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Functions/Calculator/Instruction.php) objects, including [`Number`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Functions/Calculator/Number.php), the [`Operator`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Functions/Calculator/Operator.php) enum and nested procedures. There is no execution of PHP code or unrestricted PostScript programs; objects produce allowed calculator instructions. Full validity of a calculation, its stack effects and results nevertheless requires additional semantic validation.

## 11. Sources and definition objects

Definitions retain the information needed to trace back to the standard:

| Component | Information carried |
| --- | --- |
| [`SourceReference`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Specification/SourceReference.php) | Standard, table, optional clause, document name, physical PDF page and source-document hash. |
| [`Requirement`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Specification/Requirement.php) | Presence requirement, including whether it is unconditional or conditional. |
| [`ObjectTypeConstraint`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Specification/ObjectTypeConstraint.php) | Value families, direct/indirect object rules and other supported type constraints. |
| [`EntryDefinition`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Specification/EntryDefinition.php) | An entry's name, type, presence, description and source. |
| [`TableDefinition`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Specification/TableDefinition.php) | Entry collection and explicit composition of common tables. |
| [`ImplementationCorrection`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Specification/ImplementationCorrection.php) | Documented implementation decision where source wording is inconsistent. |
| [`Catalogue`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Specification/Catalogue.php) | Immutable collection of definitions selected and constructed by the caller. |

These objects do not load JSON at runtime. Inventories under [`resources/iso32000-1`](https://github.com/PDFToolkit/pdf/tree/v0.11.0/resources/iso32000-1) serve generation and verification tools. Generated classes construct themselves with their immutable definitions. The [specification documentation](specification.md) explains reproducible generation and the documented `/Prev` correction.

The `PDF\Specification\Adobe` namespace composes ISO definitions and supplement additions. Every entry retains its own origin. `DeveloperPrefix`, `DeveloperExtension`, `DeveloperExtensionEntry` and `DeveloperExtensions` construct the catalog's extension declaration; all its values are direct, following ISO 7.12.1. `BatesArtifact` represents Bates pagination, and `WindowDimension` resolved, consistent dimensions. [Tutorial 13](tutorials/13-adobe-extensions.md) shows declaration and pagination in a complete PDF.

### Security and signatures

[`HistoricalStandardSecurityHandler`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Security/HistoricalStandardSecurityHandler.php) constructs ISO R=2/3/4 password mechanisms, with RC4 or AESV2 depending on the revision. Adobe R=5 adds Unicode 3.2 SASLprep preparation and AES-256. [`PublicKeySecurityHandler`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Security/PublicKeySecurityHandler.php) composes CMS recipients and filter keys. `FileWriter` and incremental writers receive the `FileEncryption` selected by the application; AES and CMS backends using OpenSSL are optional. The [security guide](security.md) and [Adobe guide](adobe-supplement.md#historical-aes-256-encryption) explain protocols, validation and limits.

[`PendingSignature`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Signatures/PendingSignature.php) reserves Contents and ByteRange. [`SignatureWriter`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Serialization/SignatureWriter.php) fixes byte ranges before calculation; `PreparedSignature` then fills the reservation without moving objects. The three ISO signature formats and successive signatures are checked by independent tools. [Tutorial 20](tutorials/20-signed-document.md) shows detached CMS. Identity, certificate chain and trust policy are explicitly chosen; the cryptographic result does not alone certify that trust.

`ModernStandardSecurityHandler`, `ModernFileEncryption` and `ModernEncryptionDictionary` provide PDF 2.0 R=6 AES-CBC and TS 32003 R=7 AES-GCM. `SignatureDigestMethod` and `ModernCmsSignatureBackend` select SHA-3/SHAKE and supported RSA, named ECDSA or EdDSA operations with exact combination checks. `IsoExtensions` declares each chosen ISO technical specification separately. `PdfMacTokenComposer` authenticates actual initial, incremental or linearized file bytes, either autonomously or attached to the CMS signature. Each revision needs its own MAC operation.

`PendingDocumentTimestamp` and `Rfc3161TimestampBackend` add RFC 3161 document timestamps through an explicit token provider and authority verifier. `DocumentSecurityStore`, `ValidationDataStream` and `ValidationRelatedInformation` store DSS/VRI evidence without automatically fetching or trusting it. The narrow `DocumentTimestampRevisionPolicy` checks the frozen maintenance delta before applying the DocMDP timestamp/DSS exception; other revision changes and FieldMDP remain constrained. These mechanisms do not establish general long-term validation or PKI trust. The [modern-signature tutorial](tutorials/31-pdf20-modern-signature.md), [timestamp/DSS tutorial](tutorials/32-pdf20-timestamp-dss.md), [bundle guide](pdf-2-0-bundle.md) and [security review](security.md) explain algorithm, provider and evidence boundaries.

An encryption, signature, font descriptor, multimedia or tagged-structure dictionary class describes format entries. Processing belongs to dedicated mechanisms where available, such as the TrueType program and CID embedding. A dictionary's presence does not perform encryption, signing, multimedia playback or tagged-structure compliance. The API reference documents available objects; stated coverage remains that of their actually implemented behaviors.

### Geospatial measurements

`GeographicCoordinateSystem` and `ProjectedCoordinateSystem` declare the reference
system. `GeospatialControlPoints` owns paired local/world coordinates;
`GeospatialMeasure`, `Viewport` and `Viewports` associate those values with page,
Form and image objects. Display units, the twelve-value projected affine matrix
and typed point clouds have separate objects. Effective-graph validation also
checks raw dictionaries and retained revisions. The [geospatial tutorial](tutorials/33-pdf20-geospatial.md)
explains these relationships without implying a GIS projection converter.

## 12. Choosing a component and continuing

To create a document, start with domain objects: pages, resources, content and catalog. Use generated entries for concepts still lacking a specialized object or to add an explicit standardized entry. Use a generic `Entry` for an extension whose name and meaning are controlled by the application.

Constructors check local values, builders check graph ownership, and writing checks states requiring a complete graph. The application chooses data, paths, accessible resources and accepted actions. The [security documentation](security.md) details available protections and limits.

To progress to complete documents, follow the [tutorials](tutorials/README.md), compare previews with downloadable PDFs on the site, then study the [table recipe](recipes/table.md). To read an external PDF, use the [reader module](packages.md#reading-an-external-pdf) with explicit resolution and decoding. To add behavior to the model, consult the [architecture](architecture.md), [specification coverage](specification.md) and [API reference](https://pdftoolkit.github.io/reference/index.html).

To derive logical content into HTML, the optional PDF-to-HTML 0.5.1 module builds immutable source objects and document-scoped processors using the selected reader 0.6.0. `HtmlDeriver` produces HTML, CSS, assets and diagnostics; `GraphicPdfExporter` preserves programs and prepares an isolated PDF for the application's `GraphicsRasterizer` engine. `FormActionPolicy` separates form reset/submission from PDF ECMAScript permission. The [requirements](https://pdftoolkit.github.io/modules/to-html/requirements.html), [policies](https://pdftoolkit.github.io/modules/to-html/policies.html) and [graphics](https://pdftoolkit.github.io/modules/to-html/graphics.html) guides document native rules and these explicit capabilities; [tutorial 35](tutorials/35-derive-html.md) shows actual output.
