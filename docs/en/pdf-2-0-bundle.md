# PDF 2.0 companion specifications: objects, algorithms and validation

Core **0.7** extends the PDF 2.0 foundation with the companion specifications
distributed by the [PDF Association](https://www.pdfa.org/sponsored-standards/).
The mechanisms remain explicit PDF objects. Applications choose their file
version, algorithms, namespaces, metadata, relationships and validation policy.
There is no global registry or implicit conversion of an external file.

## Scope by document

| Document | Executable mechanisms | Validation and limits |
| --- | --- | --- |
| ISO 32000-2:2020 EC3 | Edition-specific base dictionary inventory, text encodings, associated files, R=6, namespaces, document parts, encrypted wrappers, DSS and document timestamps | 306 dictionary tables and 1,709 entry objects; selected EC3 overlays and explicit semantic limits remain separate. |
| ISO/TS 32001:2022 EC3 | SHA3-256/384/512 and fixed 64-byte SHAKE256; explicit ISO extension declaration and signature digest objects | Independent digest/CMS checks; EC3 deletion of clause 5.1.3 is respected rather than extending the struck-out signature-reference rule. |
| ISO/TS 32002:2022 EC3 | Named P-256/P-384/P-521 and Brainpool curves, Ed25519/Ed448, exact curve/digest combinations and CMS construction | Independent verification of 23 supported curve/digest signatures. Certificate trust and revocation remain application policies. |
| ISO/TS 32003:2023 | AES-GCM/AESV4 with V=6/R=7, authentication tag, per-key nonce sequence and R=6 credential algorithms | pyHanko decrypts native files; altered ciphertext is rejected. R=6 AES-CBC remains a separate selection. |
| ISO/TS 32004:2024 | KDFSalt, permission bit 13, HKDF, AES key wrap, CMS AuthenticatedData, autonomous and signature-attached MAC | pyHanko verifies actual initial, incremental and linearized files; MAC output has an exact DER length without padding. |
| ISO/TS 32005:2023 | Qualified roles, standard/custom namespaces, role-map resolution, common PDF 2.0 roles and table 5 inclusion rules | Full source matrix is reproducible. Published issue resolutions are selected explicitly; source ambiguities are not silently guessed. |
| PDF Declarations | Declaration/ClaimData objects, dates and optional PDF/A XMP extension schema | Declarations are author assertions with a precise metadata scope; they are not audit certificates. |
| WTPDF 1.0.0 | Explicit reuse/accessibility audit levels, structural, metadata, annotation and font-use checks | Reports distinguish detected failures from pending semantic and external font-program checks. No automatic PDF/UA-2 certification is claimed. |
| Application Note 001 | `UseBlackPtComp` with exactly `ON`, `OFF` or `Default` | PDF 2.0 version and value checks, including raw graphics-state resources without a Type entry. The output device performs colour management. |
| Application Note 002 | Associated files on information objects, marked content, encrypted payload descriptor and document wrapper | Effective graph checks cover discoverability, relationships, hidden collection and the unencrypted outer document. |
| Application Note 003 | Object metadata streams, correct resource scope, named marked-content properties, document parts and DPM | Native XMP serialization is escaped UTF-8 XML. Opaque caller-supplied XML and content bytes require their own validation. |

The base ISO 32000-2 catalogue inventories 440 tables and models 306 dictionary
tables with 1,709 fixed or variable entries. Source continuation pages and
extraction corrections are traceable. This coverage and these companion
mechanisms do not establish complete conformance to every clause of the base
standard. The [PDF 2.0 guide](pdf-2-0.md) and [coverage guide](coverage.md) retain
that distinction. The optional reader's supported input scope is unchanged;
the writer’s new mechanisms are distinct from reader 0.2’s PDF 2.0 syntax and UTF-8 support.

## Algorithms are selected independently

`ModernStandardSecurityHandler` constructs R=6 AES-CBC or R=7 AES-GCM credentials
from explicitly prepared user and owner passwords. `ModernFileEncryption` binds
the credentials, file key and cryptographic operation. `Pdf20Permissions` keeps
the permission word and the MAC requirement consistent. An ISO extension is an
array member under `Extensions.ISO_`; declaring level 32004 does not implicitly
declare levels 32001, 32002 or 32003.

`PdfMacTokenComposer` binds the actual file encryption key and the 32-byte
`KDFSalt`. The writer reserves an exact hexadecimal slot, fixes the byte range,
hashes the final serialized bytes and inserts the DER token without shifting
offsets. Incremental writing preserves earlier bytes and requires a fresh MAC
operation for the new revision. The same rules apply to linearized output.

```php
$mac = new PdfMacTokenComposer($encryption->key, $salt, new SystemRandomSource());
$revision = (new FileWriter(encryption: $encryption, mac: $mac))->revision($file);

$nextMac = new PdfMacTokenComposer($encryption->key, $salt, new SystemRandomSource());
$next = (new IncrementalWriter(mac: $nextMac))->serialize(
    new IncrementalUpdate($revision, $explicitDelta),
);
```

For a signed revision, select `macSignature: $pending` on the writer and pass
`mac: $mac` to `PreparedSignature`. The MAC becomes a CMS unsigned attribute
bound to both the PDF byte range and the actual SignerInfo signature octets.
A standalone MAC cannot be carried forward unchanged when signing changes the
reserved signature bytes. Capacity includes the attached MAC; overflow requires
a new reservation and a new signature.

PHP's OpenSSL extension handles the supported RSA/ECDSA primitives. Ed25519 and
Ed448 use an explicitly selected OpenSSL executable through the dedicated
provider because PHP 8.3 does not expose the needed EdDSA operation. This provider
receives the executable and key explicitly; selecting other algorithms does not
start a process. See the [signature and integrity tutorial](tutorials/31-pdf20-modern-signature.md).

## Metadata and declarations have an owner

`XmpPacket` composes properties, RDF bags/sequences, localized alternatives and
declarations. `MetadataStream` writes the XML stream; `MetadataEntry` links it
indirectly to its PDF owner. A declaration in document metadata concerns the
document. The same declaration on an object or marked sequence has that narrower
scope. Metadata properties do not automatically become visible page text.

Named marked-content properties resolve in the page, Form XObject, tiling
pattern or Type 3 font resource scope. Emission facts are frozen with the actual
serialized stream, so an unstaged builder change cannot rewrite an earlier
revision's meaning. Direct inline metadata stream references are rejected.

`DocumentPart`, `DocumentPartRoot` and `DocumentPartMetadata` represent document
parts and their data. Native graph validation checks hierarchy, page ranges and
the bidirectional page-to-part association. An encrypted payload uses a separate
outer document, an associated file with `EncryptedPayload` relationship, an EP
descriptor and a hidden collection. The outer document remains readable without
decrypting its inner PDF. The tutorials explain [metadata and parts](tutorials/28-pdf20-metadata-declarations.md)
and [the encrypted wrapper](tutorials/29-pdf20-encrypted-payload.md).

## Structure rules and WTPDF auditing

`StructureNamespace`, `StructureRole` and `NamespaceRoleMap` make namespace
identity part of the role. `NamespaceRoleResolver` follows qualified mappings
and rejects unresolved targets and cycles. The effective document must be PDF
2.0 when these mechanisms are used, including retained incremental objects.

`StructureInclusionRules` applies the source matrix to real parent/child roles,
including the PDF 1.7-only exemption and mixed-namespace rules. Corrections 336
and 440 are an explicit correction selection. The retained source's literal
`c` occurrence is preserved in the source inventory; the selected published
resolution supplies its interpretation.

`WtPdfAudit` produces findings for the selected conformance level. Its report
does not equate "no detected failure" with "conformant": meaningful reading
order, appropriate alternate descriptions, faithful Unicode mapping and
external font-program facts still need evidence. The [namespace tutorial](tutorials/30-pdf20-tagged-namespaces.md)
shows a concrete report next to the actual tagged PDF.

## Preserve signatures with timestamps and validation data

`PendingDocumentTimestamp` owns a `/DocTimeStamp` dictionary with the
`ETSI.RFC3161` SubFilter. `Rfc3161TimestampBackend` sends an explicit provider
the actual document imprint and nonce, then checks the returned token, authority
binding and CMS signature. `LocalTimestampAuthority` is an explicitly selected
offline provider; it performs no network request and establishes no public trust.

`DocumentSecurityStore` contains indirect certificate, CRL and OCSP streams.
`ValidationRelatedInformation` requires a successful caller-selected validation
policy and identifies the exact earlier signature Contents, including padding.
The graph rejects VRI introduced before its signature or evidence absent from
the matching DSS arrays. A later timestamp covers the appended evidence too.

ISO 32000-2 excludes document timestamps and DSS from DocMDP evaluation.
`DocumentTimestampRevisionPolicy` proves a narrow maintenance delta against all
frozen previous objects before allowing it under P1: pages, content, widgets and
ordinary signatures cannot change alongside it. FieldMDP and additional field
locks remain binding. The [timestamp tutorial](tutorials/32-pdf20-timestamp-dss.md)
explains three actual revisions; the independent oracle also checks certified,
encrypted and linearized histories.

## Geospatial measurements retain their coordinate system

`GeographicCoordinateSystem` and `ProjectedCoordinateSystem` identify an explicit
EPSG code or WKT string. `GeospatialControlPoints` pairs local and world positions
and derives the matching LPTS/GPTS arrays. `GeospatialMeasure`, `Viewport` and
`Viewports` attach those measurements to their actual page, Form or image owner.
`PreferredDisplayUnits`, `ProjectedCoordinateSystemMatrix` and `PointDataCollection`
complete the display preferences, affine calculation and point-cloud objects.

Native and effective-graph validation checks contexts, finite values, matching
dimensions, normalized bounds and version requirements. It does not fetch a GIS
registry or convert projections. The [geospatial tutorial](tutorials/33-pdf20-geospatial.md)
explains two independently declared sample regions and their serialized data.

## Navigation can target a logical element

`StructureDestination` identifies a real member of the structure tree and an
explicit `DestinationView`. Page resolution follows the first content item in
declared child order, with a first-page fallback when no content item qualifies.
GoTo actions and named destination dictionaries preserve their page fallback
alongside `SD`. Remote and embedded forms use explicit byte-string IDs without
opening another file. Effective-graph checks preserve these relationships in
retained revisions. The [structure-destination tutorial](tutorials/34-pdf20-structure-destinations.md)
shows semantic links and their actual PDF objects.

## Independent checks

The PHP suite runs under PHP 8.3, 8.4 and 8.5. The companion checks use separate
implementations:

- pyHanko validates password/public-key AES-CBC and AES-GCM files, standalone
  and attached MACs, historical revisions and tampering rejection.
- cryptography and ASN.1 tooling verify curve/digest signatures and MAC tokens.
- pyHanko and OpenSSL verify RFC3161 tokens, DSS/VRI, certification and every
  signed historical prefix rather than only the last file revision.
- qpdf validates the emitted structures and independently decrypts the example
  encrypted payload; pypdf and an XML parser inspect the metadata and relations.
- The TS 32005 source matrix is regenerated from all its table pages and checked
  against the committed resource and PHP representation.

These checks establish the tested behaviour. They do not promise that arbitrary
application input is safe or that an author-supplied conformance claim is true.

## Retained originals and provenance

All eleven originals retain their supplied names and bytes under
`resources/reference-documents/` in the core repository. The [source manifest](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/iso32000-2-bundle/sources.json)
records fingerprints, byte counts, physical pages and correction collections.
They are linked from the site rather than copied into Composer installations
or duplicated as large documentation assets.

- [ISO 32000-2:2020 EC3, newly supplied copy](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/ISO_32000-2_sponsored_EC3%281%29.pdf)
- [ISO/TS 32001:2022 EC3](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/ISO_TS_32001-2022_sponsored_EC3.pdf)
- [ISO/TS 32002:2022 EC3](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/ISO_TS_32002-2022_sponsored_EC3.pdf)
- [ISO/TS 32003:2023](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/ISO_TS_32003-2023_sponsored.pdf)
- [ISO/TS 32004:2024](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/ISO-TS-32004-2024_sponsored.pdf)
- [ISO/TS 32005:2023](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/ISO-TS-32005-2023-sponsored.pdf)
- [PDF Declarations](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/PDF-Declarations.pdf)
- [Well-Tagged PDF 1.0](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/Well-Tagged-PDF-WTPDF-1.0.pdf)
- [Application Note 001: black point compensation](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/PDF20_AN001-BPC.pdf)
- [Application Note 002: associated files](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/PDF20_AN002-AF.pdf)
- [Application Note 003: metadata locations](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/PDF20_AN003-ObjectMetadataLocations.pdf)
