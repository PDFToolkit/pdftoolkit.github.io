# 20. Sign without moving objects

The [complete script](https://github.com/PDFToolkit/pdf/blob/v0.9.1/examples/signed-document.php)
produces a visible page and a detached CMS signature associated with an invisible `/Sig` field.

```sh
php examples/signed-document.php signed-document.pdf
```

The PHP OpenSSL extension is required. The script's certificate and key are
**public and for testing only**: they make a signature reproducible without
proving identity or trust.

`X509Certificate`, `CertificateChain` and `OpenSslIdentity` receive bytes. The
identity checks that certificate and key match; the backend searches for no
files or URLs. The script chooses fixtures. A real application supplies its
own credentials and trust policy.

`PendingSignature` reserves capacity for `/Contents` and `/ByteRange`.
`SignatureField` associates it with `/V`; `AcroForm` references the field. A
visible appearance is a separate object and is not required for this association.

`SignatureWriter::prepare()` writes the file and fixes ByteRange before the
cryptographic calculation. Ranges cover the entire revision except the Contents
token and its delimiters. `PreparedSignature::sign()` signs those bytes and
fills only the reservation. Oversized signatures are rejected; offsets and
file length stay fixed.

`SignatureBackend` permits choosing another component. The three ISO formats
have their own requirements. `prepareRevision()` can sign an incremental
revision while preserving the first signature's bytes.

The PHP OpenSSL backend uses SHA-256 for CMS messages and SHA-1 for the offered
PKCS#1 format. Its API cannot select every digest listed in the specification.
Key parameters and the effective PDF version are checked: this CMS backend
requires PDF 1.6; an RSA key larger than 1,024 bits requires at least PDF 1.5.
The catalog can raise the header's version.

Required seeds and field locks use the `SignatureFieldSigning` orchestration
presented in [lesson 26](26-signature-field-policy.md). This API checks written
policies and the actual cryptographic result; the simple signature in this lesson
rejects requirements needing that contract. General comparison of revision changes
under DocMDP, FieldMDP or UR remains a separate mechanism.

Mathematical verification and trust are distinct. Certificates, revocation,
timestamps and revision permissions require their own checks. CI independently
verifies ByteRange, CMS, digests and RSA signatures, and rejects a modified message.

Reference: ISO 12.8, physical pages 474–487.

[Index](README.md) · [Complete code](https://github.com/PDFToolkit/pdf/blob/v0.9.1/examples/signed-document.php)
