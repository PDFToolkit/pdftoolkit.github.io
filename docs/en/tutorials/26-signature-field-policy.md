# 26. Apply signature-field conditions

The [complete script](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/signature-field-policy.php)
produces one page, a text field `Reference` and a signature field `Approval`.
The detached CMS signature is actually calculated and verified. The field's
widget displays an explicit appearance while its FieldMDP lock selects `Reference`.

```bash
php examples/signature-field-policy.php signature-field-policy.pdf
```

This tutorial uses the API introduced in **0.5.0**, PHP 8.3 or later and OpenSSL.
The certificate and key are the repository's **public test fixtures**. They
reproduce a mathematical signature; they identify no trusted person.

## Describe obligations, then choose how to satisfy them

`SignatureSeedValue` represents `/SV`, the field's conditions.
`SignatureSeedFlags` indicates which are required. Here the four selected bits require:

- `/Filter /Adobe.PPKLite`, the chosen handler's identity;
- the first supported `/SubFilter`, here `/adbe.pkcs7.detached`;
- `/DigestMethod [/SHA256]` for the RSA key actually used;
- a `/Reason` belonging to `/Reasons`, here `Étudié et approuvé`.

```php
$seed = new SignatureSeedValue(
    new SignatureSeedFlags(
        SignatureSeedFlag::Filter,
        SignatureSeedFlag::SubFilter,
        SignatureSeedFlag::DigestMethod,
        SignatureSeedFlag::Reasons,
    ),
    new Entry(new NameType('Filter'), new NameType('Adobe.PPKLite')),
    new Entry(new NameType('SubFilter'), new ArrayType(new NameType('adbe.pkcs7.detached'))),
    new Entry(new NameType('DigestMethod'), new ArrayType(new NameType('SHA256'))),
    new Entry(new NameType('Reasons'), new ArrayType($reason)),
);
```

`SignatureSigningIntent` supplies application choices: reason, optional digest,
certification, document lock, appearance and evidence requests. A requested
reason must be the one in the signed dictionary. Conditions are also reread
from the prepared file: changing a construction object after writing does not
change obligations already emitted.

A `SubFilter` array retains its order: the first supported format is chosen
even if the preference is optional. If none matches and the bit is optional,
another explicitly supported format can be selected. An optional reason list
permits another reason. With the required bit, absence of `Reasons` or special
value `[.]` requires omission of `Reason`.

## Build the field and its lock

`SignatureFieldSigning` composes the `/Contents` reservation, `/Sig` field,
its `/V` value and necessary transformation references. It retains distinct
objects for resources, appearances, widgets and conditions.

```php
$lock = new SignatureFieldLock(
    SignatureLockAction::Include,
    new ArrayType(new TextString('Reference')),
);
$signing = new SignatureFieldSigning(
    $backend,
    new PartialFieldName(new TextString('Approval')),
    new SignatureCapacity(8192),
    new SignatureSigningIntent(reason: $reason),
    $seed,
    $lock,
);
```

The lock selects another field in the actual form. The operation copies its
`Action` and `Fields` entries into **direct** `FieldMDP` parameters. `All`,
`Include` and `Exclude` retain their meaning; selecting a group name also
selects its descendants.

The script supplies a `FormAppearanceStream` and `WidgetAppearance`, then
attaches the widget to `Approval` with `addWidget()`. The page references the
widget in `Annots`, and `bindToPage()` defines its actual `P`. Visible text does
not replace the CMS in `/V/Contents`.

`SignatureAppearanceSelection` gives an application name to a supplied
appearance. The contract checks that it is the selected normal appearance for
every widget of the field, including merged field/widgets and state dictionaries.
It neither draws an appearance nor reproduces a PDF reader's dialog.

The `Reference` text-field appearance also follows the variable-text procedure
in the [AcroForm tutorial](14-acroform-fields.md): `/Tx BMC ... EMC` encloses text
and clipping while the frame remains outside. It is distinct from the static
signature appearance. Marking does not make the field editable after signing
when the reader applies its FieldMDP lock.

## Bind the catalog, freeze bytes and sign

```php
$signing->bindCatalog(new IndirectReference($catalog));
$prepared = (new SignatureWriter())->prepare($file, $signing->signature);
$signed = $signing->sign($prepared);
$signed->writeTo($path);
```

`bindCatalog()` explicitly closes the `FieldMDP.Data` reference. It designates
this catalog and form; a reference to another document is rejected. `prepare()`
writes the PDF and fixes `/ByteRange` before the cryptographic calculation.
Covered bytes include the form, seed, lock, resources and appearances; only
the `/Contents` reservation is excluded.

The contract traverses `AcroForm/Fields/Kids` in actually emitted snapshots.
It resolves inherited fields, full names and `Parent` relationships, distinguishes
separate widgets and rejects cycles or inconsistent ownership. An arbitrary
dictionary named `V` outside this tree does not become a signature field.

The backend declares digests it can **emit**. PHP OpenSSL uses SHA-256 for CMS
here; its API cannot arbitrarily select SHA-384 or SHA-512. The verifier reads
the digest from the CMS result, mathematically verifies the message and
identifies the certificate actually selected. It binds those facts to exact
input and output bytes. A substituted certificate, modified CMS or facts
reused from another document are rejected before finalization.

Only this verification permits filling the reservation. If CMS exceeds its
capacity, prepare a new reservation and sign the new bytes. Final file offsets
and length remain fixed.

## History and external components

A `DocMDP` certification must be the first signed field, and a document contains
at most one. Its `Perms/DocMDP` link is optional: the field signature enables
detection; this link adds prevention of changes. `certificationPermissions()`
supplies that explicit catalog contribution.

Each subsequent signature uses a new incremental revision. The core retains
previous snapshots: removing an old field or releasing its signature object
does not erase historical order. A retired value reference resolves to `null`
in the current revision.

For the signing operation, an earlier DocMDP or Adobe `P1` lock forbids a new
`V`. An earlier `FieldMDP` forbids signing a selected field, including descendants.
Adobe permissions remain the historical minimum: a new `P3` does not increase
an old `P2`.

These operation checks do not yet perform a **general comparison of every
revision change**: all field values, removals or moves, page content, shared
resources, appearances, annotations and page-template instantiation. Complete
DocMDP/FieldMDP/UR analysis remains to be developed. A mathematically valid UR
signature also does not prove that its signer is authorized to grant rights.

`PolicySignatureBackend`, `SignatureOutputVerifier` and `SignatureSigningEvidence`
support explicit external integration. `finalizeWithPolicy()` applies the same
contract to a signature calculated elsewhere. An RFC3161 timestamp or OCSP/CRL
evidence requires a component producing and verifying it within the actual CMS.
Declared capability does not replace that evidence; the native backend rejects
these requests. The application must supply PKI trust policies, and the core
performs no implicit network access.

## Evidence and references

The independent policy corpus inspects eight PDFs and verifies nine RSA/DSA
mathematical signatures using qpdf, pypdf, ASN.1 and independent cryptography on
PHP 8.3, 8.4 and 8.5. It covers actually written conditions, certification with
and without `Perms`, two signed revisions, `FieldMDP.Data`, an Adobe lock and an
attached appearance. This script's rendering and form are inspected too.

Preserved sources: [conditions and certificates, pages 455–459](https://github.com/PDFToolkit/pdf/blob/v0.5.4/PDF32000_2008.pdf#page=455),
[transformations and signatures, pages 474–487](https://github.com/PDFToolkit/pdf/blob/v0.5.4/PDF32000_2008.pdf#page=474),
[Adobe locks and appearances, pages 43–45](https://github.com/PDFToolkit/pdf/blob/v0.5.4/adobe_supplement_iso32000.pdf#page=43).
The `DigestMethod` DSA/SHA1 clause is applied when that seed entry exists; an
empty seed or `Reasons` alone creates no additional restriction on Table 257's
general DSA/SHA256 capability. This interpretation is located in both descriptions
without being presented as an official erratum.

[Tutorial path](README.md) · [Complete code](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/signature-field-policy.php)
