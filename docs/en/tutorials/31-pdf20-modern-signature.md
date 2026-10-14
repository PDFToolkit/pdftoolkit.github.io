# 31. PDF 2.0: modern signatures and integrity

The [complete script](https://github.com/PDFToolkit/pdf/blob/v0.7.0/examples/pdf20-modern-signature.php) produces a readable PDF 2.0 page and a real CMS signature using P-256 and SHA3-256. The page explains the selected algorithms. Its signature field has no widget: the visible text describes the operation, while the cryptographic signature covers the actual file bytes.

The certificate and private key are **public test credentials**, committed for reproducible examples. Their signature demonstrates the mathematical operation and does not establish a trusted identity. Applications supply their own credentials and trust policy explicitly.

## Run the example

From a core 0.7.0 checkout with the locked development dependencies, on 64-bit PHP 8.3 or later:

```bash
php examples/pdf20-modern-signature.php modern-signature.pdf
```

The example supplies Courier through [explicit metrics](https://github.com/PDFToolkit/pdf/blob/v0.7.0/examples/fixtures/pdf20-courier-font.php): FirstChar/LastChar, ASCII widths and a FontDescriptor. PDF 2.0 no longer permits omitting these entries for the fourteen standard fonts. This construction does not embed a font program; profiles requiring embedding need an explicitly embedded font.


This example uses PHP's OpenSSL extension for ECDSA. Ed25519 and Ed448 use a separate, explicitly selected executable provider; merely loading the library starts no process. The PDF remains unencrypted so that its page can be previewed in the browser.

## Select the credential and digest

`X509Certificate` receives the certificate's DER bytes. `CertificateChain` and `OpenSslIdentity` associate that certificate with the supplied private key. No filename, remote certificate URL or operating-system trust store is inferred.

```php
$identity = new OpenSslIdentity(new CertificateChain($certificate), $privateKeyPem);
$backend = new ModernCmsSignatureBackend(
    $identity,
    SignatureDigestMethod::SHA3_256,
);
```

The backend reads the named curve from the actual certificate and checks the curve/digest pair. P-256 with SHA3-256 is supported; P-256 with SHA-512 is rejected. ECDSA uses the selected digest for both the document and the DER CMS signed attributes. EdDSA has its own prescribed algorithm rules. An algorithm name alone does not override these constraints.

## Declare the extensions independently

```php
$extensions = new IsoExtensions(
    IsoTechnicalSpecification::HashAlgorithms,
    IsoTechnicalSpecification::DigitalSignatures,
);
```

These objects write separate developer-extension dictionaries in `Extensions.ISO_`. ISO/TS 32001 supplies the additional digests; ISO/TS 32002 supplies the signature algorithms and combinations. Selecting the larger extension number does not declare the smaller one. The file also explicitly uses `new FileHeader('2.0')`.

SHA3-256, SHA3-384, SHA3-512 and SHAKE256 with a fixed 64-byte output are represented by `SignatureDigestMethod`. EC3 deletes ISO/TS 32001 clause 5.1.3: the implementation therefore does not extend that deleted signature-reference rule.

## Reserve, prepare and sign exact bytes

`PendingSignature` owns `/Contents`, `/ByteRange`, `/Type`, `/Filter` and `/SubFilter`. Its `SignatureCapacity(4096)` reserves 4,096 signature bytes, encoded as a hexadecimal string in the PDF. `SignatureField` connects that exact dictionary to the AcroForm.

```php
$prepared = (new SignatureWriter())->prepare($file, $pending);
$signed = $prepared->sign($backend);
$signed->writeTo($path);
```

Preparation freezes the object identities, byte positions and complete-file range. Signing hashes those bytes, creates the CMS container and fills only the reserved region. The file length and object offsets remain unchanged. If the result exceeds its capacity, prepare another document with a larger reservation and sign its new bytes; truncation is never used.

A later signature requires a new incremental revision. The previous byte prefix and historical signature policies remain part of the frozen history. Certificate trust, expiry, revocation and suitable algorithms for a particular deployment require the application's validation policy.

## Add encryption and PDF MAC explicitly

Encryption, approval signatures and PDF MAC solve different problems. `ModernStandardSecurityHandler` selects R=6 AES-CBC or R=7 AES-GCM. AES-GCM authenticates each encrypted value. ISO/TS 32004 adds a MAC over the complete serialized revision, including its structural bytes.

For an encrypted revision with a signature-attached MAC:

```php
$writer = new FileWriter(
    encryption: $encryption,
    mac: $mac,
    macSignature: $pending,
);
$prepared = new PreparedSignature($writer->revision($file), $pending, mac: $mac);
$signed = $prepared->sign($backend);
```

`PdfMacTokenComposer` receives the actual encryption key, the 32-byte KDF salt and an explicit random source. The matching ISO extension declarations and encryption permission bit are required. The MAC is attached as a CMS unsigned attribute and binds both the covered PDF bytes and the actual SignerInfo signature bytes. A standalone MAC uses a distinct trailer location. Every incremental revision needs a new MAC; an earlier token cannot authenticate appended bytes.

The [bundle guide](../pdf-2-0-bundle.md) explains these constructors and boundaries. The preview below demonstrates the unencrypted signature example, so it does not require a password or claim to demonstrate encryption.

## Verify with independent implementations

`tools/validate_iso32000_crypto.py` generates encrypted and MAC-protected fixtures through the native writers. It uses pyHanko to decrypt and validate them, OpenSSL and Python cryptography to verify CMS signatures, and qpdf for the supported structural combinations. It exercises classic, stream and hybrid cross-references, initial and incremental revisions, linearization and deliberate tampering.

```bash
python tools/validate_iso32000_crypto.py \
  --php php --qpdf qpdf --openssl /usr/bin/openssl \
  --work-dir /tmp/pdf20-crypto
```

Install the validation dependencies pinned by the repository before running that development command. They are not Composer production dependencies. The tests verify emitted bytes independently; their success does not make the public demonstration certificate trusted or certify every PDF profile.

## References

The retained [ISO/TS 32001 EC3](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/iso32000-2-bundle/documents/ISO_TS_32001-2022_sponsored_EC3.pdf), [ISO/TS 32002 EC3](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/iso32000-2-bundle/documents/ISO_TS_32002-2022_sponsored_EC3.pdf), [ISO/TS 32003](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/iso32000-2-bundle/documents/ISO_TS_32003-2023_sponsored.pdf) and [ISO/TS 32004](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/iso32000-2-bundle/documents/ISO-TS-32004-2024_sponsored.pdf) come from the [PDF Association](https://www.pdfa.org/sponsored-standards/). Their source identities, physical pages and correction annotations are recorded in the [bundle catalogue](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/iso32000-2-bundle/sources.json).

[Tutorial path](README.md) · [Bundle guide](../pdf-2-0-bundle.md) · [Security](../security.md)
