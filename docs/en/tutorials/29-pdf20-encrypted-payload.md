# 29. A readable wrapper with an encrypted PDF payload

The [complete script](https://github.com/PDFToolkit/pdf/blob/v0.7.0/examples/pdf20-encrypted-payload.php)
creates two documents: a password-protected PDF and an unencrypted PDF 2.0
wrapper embedding it. The wrapper's page explains how to access the content;
its collection identifies which file to open. The embedded content is actually
encrypted before insertion.

## Run the example

From a core **0.7.0** checkout, with PHP 8.3 or later and OpenSSL:

```bash
php examples/pdf20-encrypted-payload.php wrapper.pdf
```

The demonstration reader password is **`demo-reader`**. It appears on the page
and in the source so the downloaded PDF can be inspected. It is unsuitable for
a confidential document. `SystemRandomSource` supplies keys, salts and
initialization vectors.

## Encrypt the actual document before embedding it

`ModernStandardSecurityHandler` constructs an explicit encryption operation
from prepared passwords, PDF 2.0 permissions and the metadata-encryption choice.
The example uses R=6 with AES-256-CBC. `FileWriter` receives that operation and
writes the encryption dictionary and the inner PDF's encrypted strings and
streams.

```php
$security = (new ModernStandardSecurityHandler(
    new OpenSslAes256Backend(),
    new SystemRandomSource(),
))->create(
    new PreparedPassword('demo-reader'),
    new PreparedPassword('demo-owner'),
    new Pdf20Permissions(-4),
    new EncryptMetadata(true),
);
$encryptedBytes = (new FileWriter(encryption: $security))->serialize($inner);
```

The demonstration's ASCII values are already prepared. `PreparedPassword`
represents that explicit choice; its constructor does not normalize an
arbitrary password. An application's Unicode inputs must follow the selected
handler's preparation contract. The inner PDF also receives its explicit
trailer file identifier.

`EmbeddedFileStream` then receives **the encrypted PDF's bytes**, the
`application/pdf` MIME type and its source date. The wrapper's Flate filter
compresses those bytes; it does not replace their encryption. Adding only an
`EncryptedPayload` name to clear bytes would provide no protection.

## Describe the payload and connect its references

The file specification contains `EF`, `AFRelationship /EncryptedPayload` and
the `EP` dictionary:

```php
$descriptor = new EncryptedPayload(new NameType('Standard'));
$specification = new FileSpecification(
    new LiteralString('payload.pdf'),
    $options,
    new AssociatedFileRelationship(AFRelationship::EncryptedPayload),
    encryptedPayload: $descriptor,
);
```

`EP.Subtype /Standard` identifies the handler actually used by the embedded PDF.
`EP.Version` is an optional version name, distinct from a PDF real number; none
is added here. `EncryptedPayload` describes how to access a file. It does not
invent an algorithm or encrypt its data.

The same indirect file specification appears in `Names.EmbeddedFiles` and in
the catalog's `AF` array. Its name-tree key is `payload.pdf`. The wrapper
contains exactly one file in that tree, as required by the unencrypted-wrapper
mechanism.

## Select the content while keeping instructions readable

`Collection(view: CollectionView::Hidden, initialDocument: ...)` writes
`View /H` and `D (payload.pdf)`. `D` repeats **the name-tree key**, rather than a
disk path or an arbitrary reference. The catalog explicitly links the
collection, names and AF association.

The wrapper itself is written without an encryption operation. Its page
therefore remains readable to a processor unable to open the embedded content.
A capable processor may open the selected document automatically; other viewers
show the instructions and their attachment panel. The example also explains
manual extraction.

The effective graph validates these relationships for complete and incremental
writes: `EP` descriptor, embedded file, unique name entry, `D` selection, hidden
view and absence of wrapper encryption. Removing a required relationship or
replacing the collection with an inconsistent selection fails the operation.

## Verify both levels independently

The preview below renders **the wrapper**, not the decrypted content. Download
the PDF, extract `payload.pdf` and open it with `demo-reader` to view the inner
page. Downloading does not execute any attachment.

`tools/validate_pdf20_metadata.py` uses pypdf to inspect the wrapper, locate the
exact same file in the name tree and `AF`, extract its bytes and check its R=6
dictionary. It decrypts the file with qpdf, then reads the decrypted page text.
Native tests also exercise inconsistent wrappers and incremental changes;
successfully rendering the wrapper alone would not demonstrate inner
encryption.

Preserved sources: [ISO 32000-2, physical pages 109–110](https://github.com/PDFToolkit/pdf/blob/v0.7.0/ISO_32000-2_sponsored_EC3.pdf#page=109)
for the wrapper and table 28;
[file specifications, pages 149–152](https://github.com/PDFToolkit/pdf/blob/v0.7.0/ISO_32000-2_sponsored_EC3.pdf#page=149);
and [associated-files application note, page 10, §4.1.5](https://github.com/PDFToolkit/pdf/blob/v0.7.0/resources/iso32000-2-bundle/documents/PDF20_AN002-AF.pdf#page=10).
The bundle comes from the [PDF Association's sponsored access](https://pdfa.org/sponsored-standards/).

[Tutorial path](README.md) · [Metadata and document parts](28-pdf20-metadata-declarations.md)
