# Security review

This review documents security checks performed on the PHP generator and its locked dependencies: code review, regression tests, dependency audit and PDF validation by independent readers. It covers PDF value serialization, inline images, binary resources, graphs, numeric limits and file writing. The results below concern the verified surfaces and scenarios; they are not a guarantee of the absence of every vulnerability.

TrueType and PNG/JPEG converter checks are now maintained in the optional
[pdf-fonts](https://github.com/PDFToolkit/pdf-fonts) and
[pdf-images](https://github.com/PDFToolkit/pdf-images) modules. PDF objects
and their invariants remain in the core. The
[pdf-reader](https://github.com/PDFToolkit/pdf-reader) module has its own
[security documentation](https://github.com/PDFToolkit/pdf-reader/blob/v0.4.1/docs/security.md)
for reading external files; this generator review does not replace it.

The documented versions are core **0.9.1**, PDF reader **0.4.1**, image/font modules **0.1.10** and independent
OpenType **0.2.0**, with PDF-to-HTML **0.4.0**. These packages require **PHP 8.3 or later** and are checked on
PHP 8.3, 8.4 and 8.5. Core **0.9** and OpenType **0.2** require 64-bit PHP; OpenType
remains independent of the PDF core. The review includes the [PDF 2.0 companion mechanisms](pdf-2-0-bundle.md);
individual source definitions and conformance declarations are not security
certificates. OpenType's independent parser has its own
[security boundaries](https://github.com/PDFToolkit/opentype/blob/v0.2.0/SECURITY.md).

The **0.4.0** PDF-to-HTML module with reader **0.4.1+** retains its own
[security checks](https://pdftoolkit.github.io/modules/to-html/security.html)
and [explicit policies](https://pdftoolkit.github.io/modules/to-html/policies.html).
Independent tests verify HTML/CSS/URL filtering, associations and IDs,
cumulative budgets, inline images and runtime confinement to bound controls.
PDF scripts, remote resources and ResetForm/SubmitForm actions are disabled
by default. Enabling the library-owned reset does not enable source scripts.
Rendering remains application-supplied. Native password authentication is an
explicit reader selection; the [HTML authentication guide](https://pdftoolkit.github.io/modules/to-html/authentication.html)
shows its construction. The receiving HTML viewer must enforce verified
permissions. A wrong native password does not fall back to another provider.

Reader 0.3.1 limits the `EncryptMetadata=false` exemption to the actual catalog
metadata object; page and Form metadata remain encrypted unless they explicitly
select Identity. It resolves indirect stream types before selecting `EFF`, uses
the fixed 128-bit V4 file key and ignores attempts to redefine the standard
Identity filter. Its [seven additional regression cases](https://github.com/PDFToolkit/pdf-reader/blob/v0.4.1/tools/validate_metadata_security.py)
use qpdf and cryptography with the specific oracle boundaries explained in the
[authentication guide](https://pdftoolkit.github.io/modules/reader/authentication.html).

Reader 0.4.1 preserves terminal object numbers and generations through `Encrypt`,
`Root` and catalog `Metadata` reference chains. Re-reading O/U credentials does
not decrypt them, and only the actual correctly typed catalog metadata receives
the implicit cleartext exemption. Four additional encrypted-alias cases use
pyHanko's unchanged strict parser and Standard handler with cryptography.
The high-level qpdf/pypdf/pyHanko decryptors do not follow these Encrypt chains;
their earlier independent checks remain intact. The module guide states those
oracle limits without extending the exemption to page or object metadata.

## Bounded mechanisms and explicit capabilities

- Core dictionary rules execute source-linked domains and entry relationships;
  they do not sanitize arbitrary graphs or certify every normative condition.
- Native [redaction](tutorials/36-applied-redaction.md) deletes affected content,
  shared payloads and ancillary channels before writing a fresh file. Default
  preservation requires normalized device samples and trusted resource semantics;
  unsupported content is rejected, and retained complex resources need an explicit
  sanitizer. The process intentionally permits excess deletion.
  Reverse Mask/SMask/Form dependencies are excluded globally; font descriptor
  metadata is stripped, and retained values require validated types and context.
  Rotation/shear bounds use four rectangle corners, and unpainted source paths
  crossing a region are removed as recoverable geometry.
- The optional WTPDF XML parser forbids DTDs, external entities, remote resources
  and active content and applies byte/node/depth budgets. Unsupported rich text
  remains pending; XML comparison does not establish accessibility.
- Reader 0.3 authenticates explicit R=2–7 credentials and decrypts each payload
  once. Named crypt filters, object streams and AES-GCM tags have independent
  fixtures. Retained plaintext shares cumulative budgets; original ciphertext is
  separately available. Reader 0.4 additionally verifies indicated source PDF
  MACs before protected content is interpreted. `RequirePdfMac` rejects
  unprotected or stripped input; the compatible default also accepts ordinary
  unprotected PDFs. Exact lexical token identity, full-current-file byte coverage
  and CMS framing are checked. This does not verify signature mathematics or
  certificate trust; a holder of the file key can construct a new MAC.
  [The source MAC guide](https://pdftoolkit.github.io/modules/reader/source-mac.html)
  explains policies, budgets and rejection boundaries. Public-key source
  authentication remains unsupported.
- Barcode preparation compresses the whole explicit value before ordered
  partitioning and checks cumulative budgets before invoking the next supplied
  encoder. The core constructs native full-rectangle `AP.N` images; symbology,
  quiet zones and the encoder's own execution remain its explicit capability.
- WTPDF Type 3 inspection follows actual selected glyph programs and bounded
  nested resources. Contextual deprecation checks distinguish recommendations
  from failures; opaque programs and missing file context stay pending.
- OpenType 0.2 bounds contextual lookups, glyph expansion and variation stores.
  Native positioning/substitution is compared with HarfBuzz; it does not execute
  font hints or provide a complete Unicode shaping engine.

## Results and protections

| Surface | Review result |
| --- | --- |
| Names, strings, numbers, header | Separators and bytes are escaped, literal strings preserve data, numbers are finite and header versions are limited by an enum. Payloads attempting to close a string or introduce other objects remain data. |
| PDF streams | `/Length` is calculated from encoded bytes. `endstream` markers within data do not change this length. `StreamObject` rejects external `/F`, `/FFilter` and `/FDecodeParms` entries. |
| Inline images | An `EI` ambiguity was corrected: a tolerant reader may recognize the terminator without preceding whitespace. Bytes could then be read as content operators. Such sequences are now rejected; an image XObject provides a separate representation with an explicit length. |
| Image dimensions | Checked integer calculation of row bytes and the total. Overflow is rejected rather than passing through a float and an incorrect length. |
| PNG/JPEG import — pdf-images module | Explicitly supplied bytes, without path/URL loading. Limits on bytes, pixels, dimensions and segments; PNG CRC/order/filters/bounded zlib; JPEG markers, tables and colors inspected. The PDF reader decodes JPEG coefficients. |
| TrueType program — pdf-fonts module | Validation of explicitly supplied binary data: tables, offsets, metrics, cmap and glyphs checked; composite-glyph cycles and depth bounded. Unsupported CFF, variable fonts and collections are rejected. |
| Shared operands | Validation visits each identity once, with a separate set for active ancestors. It preserves cycle rejection without exponentially revisiting a shared subgraph. |
| Cross-references | Initial gaps receive free records as required by the standard. `CrossReferenceLimits` bounds cumulative capacity before allocation. Incremental sections remain partial; additions for `/Size` and the xref stream number are checked. |
| Revisions | Old-number reservations, preserved generations and aliases; structural-container replacement rejected even through a new object stream. Catalog and page-tree metadata are checked against effective values. Old bytes remain in the file: an update cannot erase a secret. |
| File output | Path validation before serialization, rejection of stream URIs, write exception without path disclosure. A graph validation error occurs before opening an existing destination. |
| Dependencies | No known advisory or abandoned package reported by `composer audit --locked` during the review. This check runs in every CI build. |
| Historical Adobe R=5 encryption | Official AES vectors, qpdf fixtures and independent string/stream decryption, with user/owner passwords and incorrect-password rejection. Checks of lengths after filtering and encryption, absence of double encryption and structural exceptions. |
| Password preparation | Fixed Unicode 3.2 SASLprep/NFKC, compared with an independent oracle: mappings, prohibited and unassigned characters, bidirectional rules and truncation after normalization. |
| ISO R=2/3/4 encryption | Algorithms 1–7, user/owner credentials, RC4 and AESV2, 40–128-bit keys, implicit and explicit filters and incremental revisions. Explicit Crypt filters use their key directly according to 7.4.10; implicit streams use per-object derivation. |
| Certificate encryption | CMS messages, recipient grouping, s3/s4/s5 formats and distinct document and attachment keys. Independent verification of CMS data, keys and decryption. Permission byte order is an explicit choice. |
| Encrypted-writer boundary | Direct trailer strings outside ID rejected; Encrypt dictionary and xref remain clear. Only catalog metadata may be exempted; replacement follows the revision's effective binding. A new PHP identity cannot replace Encrypt inside an object stream. |
| Signatures | ByteRange fixed before signing, Contents reservation with explicit capacity, delimiter checking and filling without shifting offsets. The three ISO formats undergo independent verification of digests, CMS messages and RSA signatures. |

Explicit stream-URI rejection hardens the `writeTo()` contract rather than correcting demonstrated PHP execution: `LOCK_EX` already blocked common wrappers on the verified PHP 8.5 runtime. A native destination may still follow a symbolic link or point to a network share depending on the system. The application must control its location and permissions.

## Using data in the right place

`ShowText(new LiteralString($text))` escapes string syntax. `NameType($name)` escapes name syntax. However, `StreamObject($rawContent)` writes supplied bytes: when used as `/Contents`, they are PDF drawing code. Use `ContentStreams` and its typed operators to compose content from external text.

A PDF can represent a JavaScript action, launch action or URI. The library does not execute them in PHP and retains these definitions because they belong to the format. A reader may interpret them later. An application accepting user choices must allowlist action types and destinations rather than freely accepting an arbitrary graph or entries.

`EncodedData` passes already-encoded bytes. It does not analyze or decompress an incoming PNG, JPEG or PDF. The `PngImageDecoder` and `JpegImageReader` in `pdftoolkit/pdf-images` perform their dedicated validations and receive explicit limits; they do not replace an upload service's quotas or access controls. The core's `DCTImage` accepts an explicitly declared DCT representation without inspecting its markers. Font programs are also binary data; their analysis belongs to `pdftoolkit/pdf-fonts`. Hinting engines and DCT decoding remain executed by the reader opening the document.

## Writing or serving a document

The application must choose the `writeTo()` path in a controlled location. The method overwrites an existing destination and does not create its parent directory. It is neither a path sandbox nor an atomic write: a hardware failure during writing may leave an incomplete file.

For an HTTP response, the application can send `toPdf()` bytes with its own access controls and appropriate headers:

```php
$bytes = $document->toPdf();
header('Content-Type: application/pdf');
header('Content-Disposition: attachment; filename="document.pdf"');
header('X-Content-Type-Options: nosniff');
echo $bytes;
```

The download filename is fixed here. Request data must not be interpolated directly into headers or paths. Repository examples are CLI scripts; their first argument is a path selected by the person running the command.

## Availability and coverage

Numeric checks prevent identified overflows; operand validation avoids unnecessary revisits. They do not replace service quotas. A shared direct graph can represent very large output when expanded into PDF syntax. A filter chain can also greatly increase byte counts. An input-size limit alone therefore does not bound all serialization.

[SecuritySerializationTest](https://github.com/PDFToolkit/pdf/blob/v0.9.1/tests/SecuritySerializationTest.php), [SecurityLimitsTest](https://github.com/PDFToolkit/pdf/blob/v0.9.1/tests/SecurityLimitsTest.php) and [FileOutputTest](https://github.com/PDFToolkit/pdf/blob/v0.9.1/tests/FileOutputTest.php) cover injection payloads, all 256 byte values, inline terminators, numeric bounds, shared graphs and output. [ImageObjectsTest](https://github.com/PDFToolkit/pdf/blob/v0.9.1/tests/ImageObjectsTest.php), [CrossReferenceSectionTest](https://github.com/PDFToolkit/pdf/blob/v0.9.1/tests/CrossReferenceSectionTest.php) and [IncrementalUpdateTest](https://github.com/PDFToolkit/pdf/blob/v0.9.1/tests/IncrementalUpdateTest.php) cover core PDF invariants. Image-decoding regressions are in the module's [ImageImportTest](https://github.com/PDFToolkit/pdf-images/blob/v0.1.10/tests/ImageImportTest.php). TrueType validation remains in [font module tests](https://github.com/PDFToolkit/pdf-fonts/tree/v0.1.10/tests). Independent pypdf reads confirmed binary vectors and reproduction of the inline ambiguity. qpdf checks every example in CI.

This review is not an audit of PDF readers, PHP, the HTTP server or a future layout library. Generated definition files express standard constraints; they are not a general document-sanitization policy.

Cross-review of new mechanisms identified two defects in development
versions: a metadata exemption attached to an old identity and replacement
of Encrypt by an object-stream member.
[EncryptedRevisionInvariantTest](https://github.com/PDFToolkit/pdf/blob/v0.9.1/tests/EncryptedRevisionInvariantTest.php)
checks their corrections, including actually written XML content.

The [ISO](https://github.com/PDFToolkit/pdf/blob/v0.9.1/tools/validate_iso_security.py),
[certificate](https://github.com/PDFToolkit/pdf/blob/v0.9.1/tools/validate_public_key_security.py)
and [signature](https://github.com/PDFToolkit/pdf/blob/v0.9.1/tools/validate_pdf_signatures.py)
validators are development dependencies with locked versions and hashes.
Every oracle states its reader's limitations: qpdf 12.4.2 also derives a
per-object key for explicit Crypt; pyHanko verifies the ISO rule without
modifying its algorithms. For some older RC4 variants, pypdf uses its own
general provider to accept every permitted integer length.

A mathematical signature does not establish trust in its signer. Certificate
policy, revocation, timestamping and interpretation of permitted changes
require separate checks. Private keys in fixtures are public and exclusively
intended for tests.

The native backend checks table 257 algorithms and key sizes against the
effective PDF version. The historical CMS backend uses SHA-256;
`ModernCmsSignatureBackend` provides its own explicit digest/curve selection
and independently checked PDF 2.0 operations. `SignatureFieldSigning`
orchestration applies actually written seeds, locks, certificates and
appearances, then mathematically verifies the result before filling the
reservation. An unavailable digest or evidence requirement remains rejected.
Simple signing rejects policies that require this dedicated contract.
A certificate chain declared for a PKCS#1 signature must start with the
certificate actually used by this backend.

The [output verification](https://github.com/PDFToolkit/pdf/blob/v0.9.1/tests/SignatureOutputVerificationTest.php),
[field-policy](https://github.com/PDFToolkit/pdf/blob/v0.9.1/tests/SignatureFieldPolicySigningTest.php)
and [historical-permission](https://github.com/PDFToolkit/pdf/blob/v0.9.1/tests/SignaturePermissionHistoryTest.php)
tests cover altered output, mismatched certificates, replayed facts, locks
and permissions. The [policy oracle](https://github.com/PDFToolkit/pdf/blob/v0.9.1/tools/validate_signature_field_policies.py)
verifies eight PDFs and nine RSA/DSA signatures without modifying readers.
General comparison of MDP/UR-permitted modifications remains separate.

Core **0.9.1** also applies historical DocMDP/FieldMDP restrictions at the common
incremental writer boundary, even without `PreparedSignature`. It compares the
entire frozen delta, not only the selected signature field. Supported protected
operations are terminal signing and PDF 2.0 DSS/document timestamp maintenance.
Historical field locks remain binding; P2/P3 do not authorize unclassified form
filling, annotation edits or unrelated changes. UR updates are refused. Existing
`/Lock` and `/Reference` entries may remain unchanged in a permitted operation.

Use the original native `FileRevision` emitted in the current runtime. Supplied
snapshots, clones and PHP serialization cannot preserve its emission authority.
Completed historical signatures must have actual verification bound to the final
bytes, `ByteRange`, `Contents`, signature dictionary and signing credential,
including the final CMS/MAC when applicable. Opaque `finalize()` bytes alone do
not establish this evidence. The checks establish mathematical integrity, not
PKI trust or arbitrary external-PDF change classification. The
[incremental-permission regressions](https://github.com/PDFToolkit/pdf/blob/v0.9.1/tests/IncrementalSignaturePermissionsTest.php)
and [independent permission oracle](https://github.com/PDFToolkit/pdf/blob/v0.9.1/tools/validate_incremental_permissions.py)
exercise both permitted native operations and rejected unrelated changes.
The [retained-source guide](https://github.com/PDFToolkit/pdf/blob/v0.9.1/resources/signature-revisions/README.md)
records exact source pages, supported operations and migration choices.

[AdobeEncryptionTest](https://github.com/PDFToolkit/pdf/blob/v0.9.1/tests/AdobeEncryptionTest.php)
and [validate_adobe_encryption.py](https://github.com/PDFToolkit/pdf/blob/v0.9.1/tools/validate_adobe_encryption.py)
cover historical R=5. This protocol is explicitly selected for
interoperability: its password derivation is old and AES-CBC does not
authenticate content. SASLprep preparation does not strengthen a weak
password. The [Adobe guide](adobe-supplement.md) states the mechanisms
actually available and their limits.

## PDF 2.0 cryptography, metadata and audit boundaries

`ModernStandardSecurityHandler` keeps R=6 AES-CBC separate from TS 32003
R=7 AES-GCM. The latter authenticates encrypted values and uses an explicit
per-key nonce sequence, rejecting duplicates and bounding invocations. The
application must preserve that allocation for the lifetime of the key, including
across processes. TS 32004 PDF MAC authenticates the covered serialized revision,
including structural bytes. Native writers compute a fresh standalone or
signature-attached MAC for initial, incremental and linearized output. Altered
ciphertext, wrong passwords, tampered MAC data and inconsistent key/salt/permission
relationships are regression cases. AES-CBC alone does not authenticate content,
and historical Adobe R=5 is rejected for effective PDF 2.0.

SHA3-256/384/512, fixed-output SHAKE256 and supported modern curve/digest pairs
are explicit selections with separate ISO extension declarations. RSA/ECDSA
uses PHP OpenSSL. Ed25519/Ed448 requires an explicitly selected executable
provider with an explicit key and executable; other operations do not launch a
process. The tests' certificates and private keys are public fixtures, not
production credentials. Independent pyHanko, cryptography, ASN.1 and OpenSSL
checks validate actual output; see
[the crypto oracle](https://github.com/PDFToolkit/pdf/blob/v0.9.1/tools/validate_iso32000_crypto.py).

RFC 3161 document timestamps require a caller-selected token provider and
authority verifier. DSS/VRI objects store supplied certificate, CRL and OCSP
evidence; storage alone does not establish freshness, revocation status or trust.
The timestamp-maintenance policy compares the frozen incremental delta before
allowing the narrow DocMDP timestamp/DSS exception. It does not permit arbitrary
page/content changes, override FieldMDP or replace general authenticated revision
analysis. Network retrieval, trusted roots and validation policy remain explicit
application decisions; no URL in metadata triggers a fetch.
The [timestamp/DSS tutorial](tutorials/32-pdf20-timestamp-dss.md) shows the actual
revisions and the evidence-validation boundary.

Native XMP objects validate UTF-8/XML characters and escape RDF/XML values.
Metadata owners, marked-content resource scopes, associated files, DPart page
ranges and encrypted-wrapper discovery are checked against the effective graph.
Caller-supplied opaque XML/content and embedded payload bytes are not parsed or
trusted by this model. Declarations state an author's claim at the chosen scope;
they do not prove that claim. The
[metadata oracle](https://github.com/PDFToolkit/pdf/blob/v0.9.1/tools/validate_pdf20_metadata.py)
uses independent XML/PDF readers and decrypts the example's inner PDF separately.

`WtPdfAudit` is a **partial mechanical audit, not certification**. Malformed
references, unresolved roles and invalid structures become failed findings;
legitimate indirect booleans are resolved. Traversals reject cycles, and explicit
budgets bound structure/font inspection, cumulative Unicode mappings, operations
and text bytes. A budget exhaustion aborts the audit rather than returning a
successful report. An absence of detected failures does not discharge pending
checks for reading order, useful descriptions, Unicode meaning or external
font-program evidence. The [namespace tutorial](tutorials/30-pdf20-tagged-namespaces.md)
shows both failures and remaining evidence requirements.

[Policy and private reporting](https://github.com/PDFToolkit/pdf/blob/v0.9.1/SECURITY.md) · [Architecture](architecture.md) · [Standard coverage](specification.md)
