# Adobe supplement to ISO 32000

The core repository retains two distinct reference documents:

- [ISO 32000-1:2008, PDF 1.7](https://github.com/PDFToolkit/pdf/blob/v0.5.4/PDF32000_2008.pdf), 756 pages;
- [Adobe Supplement to the ISO 32000](https://github.com/PDFToolkit/pdf/blob/v0.5.4/adobe_supplement_iso32000.pdf), edition 1.0,
  June 2008, 140 pages, `BaseVersion 1.7`, `ExtensionLevel 3`.

All Adobe PDFs supplied by the project owner are retained with their original
names and bytes. Hashes, physical pages, tables and clauses connect the code to
the document. The supplement's SHA-256 hash is
`50d0bbc96028dca1a54cf3c671054536d26e9494dc52877061763b4aed08ac48`.

## Constructing extension objects

Classes in `PDF\Specification\Adobe\Dictionary` represent dictionaries and
their entries. Classes in `PDF\Specification\Adobe\Definition` represent their
immutable definitions. They explicitly compose existing ISO definitions and
common Adobe definitions: an unchanged field retains its ISO source; an added
or modified field retains its Adobe source.

The 61 dictionary tables produce 61 dictionary classes, 61 definition classes
and 282 entry classes: 276 table entries and six subtypes prescribed in prose.
This gives 404 generated components. The separate catalogue also retains the
four value tables and the XML attribute table, algorithms, prose requirements,
external references and implementation notes.

The supplement retains chapter-based PDF Reference numbering, such as `8.6c`
and `9.51a`. These are not renamed to ISO numbers. `SourceReference` also
contains the document name: supplement page 88 does not mean ISO document
page 88.

| Family | Represented properties | Supplement pages |
| --- | --- | --- |
| Declarations and structure | Extensions, levels, tab order, XFAResources, RelatedFiles | 23–26 |
| Collections | Folders, colors, presentation, views, path and identifier fields | 28–36 |
| Annotations and actions | Polygon/PolyLine, Redact, SetOCGState, GoToE, actions and tab order | 37–41 |
| Forms and signatures | Barcode, PaperMetaData, symbology parameters, Lock and seed values | 42–48 |
| Geospatial data and measurements | GEO, GCS/DCS, coordinates, units, PtData and Viewport | 48–54 |
| 3D content | PRC, views and nodes, cross-section attributes, linear/perpendicular/angular/radial measurements, notes | 55–76 |
| Rich media | Annotations, windows, activation/deactivation, content, configurations, instances, assets, parameters and cue points | 76–99 |
| Artifacts | Bates numbering and Contents | 100–101 |

Entries check their PDF types, fixed names, indirect references and, where
the source requires it, references of array members. A direct array of
indirect references and an indirect reference to an array are different
constructions. Unions, including `text string or array of text string`, also
check the domain of their members.

The schemas allow these structures to be constructed in a PDF. They do not
provide a multimedia, Flash or 3D playback engine, a barcode codec, an XFA
engine or a geodetic transformation. Signatures have explicit construction
and backends independent of the schemas. Conditional requirements and
semantic relationships without a specialized mechanism remain identified
in the descriptions and coverage.

## Specialized objects and example

`DeveloperPrefix`, `DeveloperExtension`, `DeveloperExtensionEntry` and
`DeveloperExtensions` compose the catalog declaration. `BatesArtifact`
constructs pagination properties; `WindowDimension` constructs resolved,
consistent Default/Min/Max dimensions in default user-space units.

[Tutorial 13](tutorials/13-adobe-extensions.md) explains every step of an Adobe
declaration and a Bates footer. CI generates the PDF; an independent reader
checks the declaration, artifact properties, visible numbers and BDC/EMC
balance.

## 3D measurements and barcode preparation

`ThreeDUnitMapping` composes creation scales `TSm/TSn`, their optional user
overrides `USm/USn`, then display scales `DSm/DSn`, following pages 59–61.
`map()` returns a `MeasuredDistance`, with its PDF value and unit label.
Conditionally required labels are checked, as are division by zero and
numeric overflow.

The prose “m model units = n displayed units” and the printed equation
`Y = (m/n) X` contradict each other. The caller must select
`UnitMappingInterpretation::PrintedEquation` or `::UnitDescription`; no
implicit interpretation hides this ambiguity in the document.

`BarcodeModuleWidth` calculates `ceil(distanceInches × Resolution)` and
constructs the integer `XSymWidth` entry. `BarcodeDataPreparation` preserves
bytes for `DataPrep = 0` and applies Flate for `DataPrep = 1`. These objects
implement the preparation and formula on pages 46–47. They do not choose
text encoding or draw a PDF417, QR or Data Matrix symbol: codecs for those
symbologies depend on external standards.

## Historical AES-256 encryption

The supplement describes the Standard Security Handler `V=5`, `R=5` with
`AESV3`. Objects in `PDF\Security` implement Unicode 3.2 SASLprep preparation,
UTF-8 truncation to 127 bytes, user and owner credentials, the file key,
permissions and the corresponding AES-CBC/ECB operations. Unicode tables
are fixed and reproducible; neither locale settings nor an installed ICU
version determine their result.

`HistoricalRevision5Encryption` explicitly selects this old protocol.
The `OpenSslAes256Backend` requires PHP's `openssl` extension, which is
optional for the core. Producing encrypted PDFs requires PDF 1.7, the Adobe
level 3 declaration and explicit file identifiers. Cross-references,
identifiers and the Encrypt dictionary remain clear; strings and streams
are encrypted within their domain, after filters, without double encryption.
Metadata follows `EncryptMetadata`.

After constructing a `FileStructure` with the Adobe level 3 declaration and
two direct 16-byte identifiers in `/ID`, select the handler:

```php
use PDF\Security\EncryptMetadata;
use PDF\Security\HistoricalRevision5SecurityHandler;
use PDF\Security\OpenSslAes256Backend;
use PDF\Security\Revision5Permissions;
use PDF\Security\Saslprep;
use PDF\Security\SystemRandomSource;
use PDF\Serialization\FileWriter;

$profile = new Saslprep();
$encryption = (new HistoricalRevision5SecurityHandler(
    new OpenSslAes256Backend(),
    new SystemRandomSource(),
))->create(
    $profile->prepare($userPassword),
    $profile->prepare($ownerPassword),
    new Revision5Permissions(-3904),
    new EncryptMetadata(false),
);
$bytes = (new FileWriter(encryption: $encryption))->serialize($file);
```

Permissions are the PDF bits declared by the application; they do not replace
access control over decrypted bytes. With `EncryptMetadata(false)`, only
catalog metadata stays clear; page and image metadata remain encrypted.
Direct trailer strings outside `/ID` are rejected: additional private data
must belong to an encrypted indirect object. `revision()` retains the
encryption operation in a document-specific snapshot; `IncrementalUpdate`
reuses it while preserving old bytes, the Encrypt dictionary and the first
file identifier.

R=5 is a historical format whose password derivation lacks the protections
of modern revisions. AES-CBC does not guarantee content authenticity.
This API serves interoperability with the retained specification; it is
not a modern default security setting.

`HistoricalStandardKeyDerivation` (R=2–R=4) and
`HistoricalPublicKey256KeyDerivation` are primitives separate from the R=5
writer. The former receives password bytes already encoded in PDFDocEncoding;
the latter receives already-produced CMS bytes in their explicit order.
`HistoricalStandardSecurityHandler` now provides complete R=2–R=4 operations;
`PublicKeySecurityHandler` composes CMS recipients and filter keys for
s3/s4/s5 formats. OpenSSL backends are explicitly selected, with certificate
and key bytes supplied by the caller. The core does not search for key files
or decide certificate trust. For R=2–R=4, 32-byte padding is retained from
ISO 7.6.3.3, algorithm 2 (pages 69–70), although Adobe's restatement of step 1
omits it: qpdf vectors check this interoperability decision.

Explicit Crypt filters follow ISO 7.4.10: their key is not modified by the
object identifier. For public-key permissions, the 2008 text specifies
least-significant-byte-first ordering; a later clarification specifies
the opposite order. `PublicKeyPermissionByteOrder` makes this choice
mandatory. The original wording is retained; the
[published clarification](https://pdf-issues.pdfa.org/32000-2-2020/clause07.html)
is a separate reference.

The [coverage guide](coverage.md) distinguishes native constructions from
reader behavior and external standards that remain separate.

## Source errors and Acrobat behavior

Inconsistencies are retained and documented. For example, `Name` in a
RichMediaConfiguration is printed as `text tree` although the example supplies
a string; PtData is described in one cell as a dictionary although the prose
also allows an array. Corrections applied to the model have an
`ImplementationCorrection`, with the page and example motivating the choice.

Part II describes what Acrobat does or does not do. It is retained in the
coverage and references, with pages and note identifiers. These product
notes do not automatically become general format restrictions. Titles and
numbers remain those of the supplied text, including anomalies.

## Reproducing and checking

```sh
python tools/extract_adobe_supplement.py
python tools/generate_adobe_supplement.py
python tools/generate_adobe_supplement.py --check
python tools/build_saslprep_tables.py --check
php examples/adobe-extensions.php adobe-extensions.pdf
```

Extraction uses the columns and positions in the retained PDF. Generation
uses the versioned catalogue; PHP classes do not load that JSON at runtime.
Tests check the domains of all generated entries, base composition,
corrections and negative constraints. Independent AES and SASLprep checks
are detailed in the test code and CI. The site's API reference connects
each entry to its Adobe or ISO page.
