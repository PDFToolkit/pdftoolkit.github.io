# 32. Document timestamps and validation evidence

The [complete script](https://github.com/PDFToolkit/pdf/blob/v0.7.0/examples/pdf20-timestamp-dss.php) writes a readable PDF with two genuine RFC3161 document timestamps. Between them it appends certificate evidence in a Document Security Store (DSS) and signature-specific Validation Related Information (VRI). The visible page lists these steps; the evidence lives in PDF objects and signed historical byte ranges.

The demonstration authority operates offline with a **public test key**. Its mathematical signatures are real, but its identity and local clock are not a trusted timestamp service. Applications explicitly choose a provider and the certificate, time and revocation policy they accept.

## Run the example

From a core 0.7.0 checkout with locked development dependencies, supply the OpenSSL executable explicitly:

```bash
php examples/pdf20-timestamp-dss.php timestamps.pdf /usr/bin/openssl
```

The example supplies Courier through [explicit metrics](https://github.com/PDFToolkit/pdf/blob/v0.7.0/examples/fixtures/pdf20-courier-font.php): FirstChar/LastChar, ASCII widths and a FontDescriptor. PDF 2.0 no longer permits omitting these entries for the fourteen standard fonts. This construction does not embed a font program; profiles requiring embedding need an explicitly embedded font.


On Windows, quote a path containing spaces. The example also accepts `PDFTOOLKIT_OPENSSL` instead of its second argument. It does not fetch a certificate, private key, revocation response or timestamp over the network.

## Prepare the first document timestamp

`PendingDocumentTimestamp` is distinct from `PendingSignature`. It owns `/Type /DocTimeStamp`, `/SubFilter /ETSI.RFC3161`, `/ByteRange` and the reserved `/Contents`. Its exact indirect identity is connected to one `SignatureField` in the AcroForm.

```php
$pending = new PendingDocumentTimestamp(new SignatureCapacity(8192));
$field = new SignatureField(
    new PartialFieldName(new TextString('FirstTimestamp')),
    value: new IndirectReference($pending),
);
```

`SignatureWriter` prepares the complete file range. `Rfc3161TimestampBackend` hashes those covered bytes and constructs a `TimestampRequest` with the message imprint and a nonce. The provider receives that request rather than the complete PDF. Before inserting the returned token, the backend verifies its imprint, nonce, policy when requested, CMS signature and binding to the selected authority certificate. The certificate must have the timestamping extended key usage.

`LocalTimestampAuthority` receives the executable, certificate chain, private key, serial source and policy OID explicitly. A production integration can implement `TimestampTokenProvider` without changing the PDF dictionary or byte-range mechanism.

## Append validation data in another revision

The first timestamp signs the original file. Its VRI must therefore be added in a later incremental revision, after a successful validation decision:

```php
$information = new ValidationRelatedInformation(
    $first,
    $policy,
    certificates: $references,
);
$store = new DocumentSecurityStore(
    certificates: $references,
    validation: $information,
);
```

`SignatureValidationEvidence` is the application's explicit policy boundary. The example's policy verifies the public fixture mathematically. A production policy must also establish its required certificate trust, validity time and revocation facts. Embedding a certificate does not establish those facts.

`ValidationDataStream` stores supplied DER bytes; `ValidationDataReferences` associates indirect evidence with its kind. DSS supports certificate, CRL and OCSP arrays. VRI references the corresponding evidence already present in those DSS arrays. Its key is the uppercase SHA-1 of the earlier signature's actual `/Contents`, **including the reserved padding**. It is not the hash of the unpadded CMS token or the whole document.

The writer checks actual frozen historical bytes and rejects a VRI without a matching earlier completed signature. It also rejects mismatched evidence kinds and VRI evidence absent from the document-wide store. The catalog change is staged explicitly with `IndirectObject` and the existing catalog identifier; the previous bytes remain intact.

## Seal the appended evidence

The script appends a second timestamp field to the effective AcroForm, then prepares and signs a third revision. This timestamp covers the earlier document, first timestamp and DSS/VRI update. The first timestamp still validates its original prefix; it does not retroactively cover the added evidence.

ISO 32000-2 permits document timestamps and DSS to be ignored when evaluating DocMDP restrictions. The native P1 exception requires a strict comparison of the maintenance revision: it cannot hide page, content, widget or ordinary-signature changes. FieldMDP restrictions and additional field locks remain binding. The independent validator separately exercises certified P1 histories; the visible example concentrates on the three evidence-preservation steps.

## Verify historical bytes independently

`tools/validate_pdf20_timestamps.py` validates every signed historical prefix with pyHanko and OpenSSL. It checks actual RFC3161 message imprints, CMS signatures, ESS certificate identifiers, VRI keys and evidence references. The matrix includes classic, stream and hybrid cross-references, linearized output, clear/R=6/R=7 files, PDF MAC and certified histories.

```bash
python tools/validate_pdf20_timestamps.py \
  --php php --qpdf qpdf --openssl /usr/bin/openssl \
  --work-dir /tmp/pdf20-timestamps
```

The pinned validation dependencies belong to development tooling. None becomes a Composer production dependency. Checking the file syntax or last signature alone would not verify the complete history or the application's trust policy.

## References

ISO 32000-2:2020 clauses 12.8.4 and 12.8.5 describe DSS/VRI and document timestamps; physical page 606 states their DocMDP treatment. The [retained main standard](https://github.com/PDFToolkit/pdf/blob/v0.7.0/ISO_32000-2_sponsored_EC3.pdf) and the [bundle catalogue](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/iso32000-2-bundle/sources.json) identify the supplied PDF Association source and its correction collection. `TimestampRequest`, `TimestampResponse` and `TimestampToken` model RFC3161 data explicitly.

[Tutorial path](README.md) · [Modern signatures](31-pdf20-modern-signature.md) · [Bundle guide](../pdf-2-0-bundle.md)
