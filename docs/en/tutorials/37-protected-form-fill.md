# 37. Fill a certified form

This tutorial uses core 0.10.0. Its complete PHP source and generated PDF are
supplied by the core checkout selected for the site;
there is no second implementation in the documentation repository.

The example signs a PDF with DocMDP P2, locks the `Reference` field using FieldMDP,
then changes `Response` from `Pending` to `Reviewed`. The second revision also
replaces its visible text appearance. Page content, the original appearance,
resources and every signed byte remain unchanged.

## Run the native example

From a core checkout containing `examples/protected-form-fill.php`, its locked
development dependencies and public signing fixtures, with PHP 8.3+ and OpenSSL:

```sh
php examples/protected-form-fill.php protected-form-fill.pdf
qpdf --check protected-form-fill.pdf
```

The result has one page showing `Reviewed` inside its original grey frame. The
source is displayed below from the selected core package, with that package's
exact source link. Its certificate and private key are public test fixtures;
the example demonstrates signature mathematics, not certificate trust.

## Establish the signed restrictions

```php
$author = new SignatureFieldSigning(
    $backend,
    new PartialFieldName(new TextString('Certification')),
    new SignatureCapacity(8192),
    new SignatureSigningIntent(
        certification: DocMdpPermissions::FormFillingTemplatesAndSigning,
    ),
    lock: new SignatureFieldLock(
        SignatureLockAction::Include,
        new ArrayType(new TextString('Reference')),
    ),
);
```

The full script binds this policy to the actual catalog and AcroForm before
signing. P2 permits the implemented filling operation; FieldMDP still protects
`Reference`. The native `SignedRevision` retains actual output verification.
Keep its `revision` object in the same runtime. Reconstructing a `FileRevision`
from these bytes or completing an opaque `finalize()` call cannot recreate that
verified authority.

## Stage only the classified replacements

```php
$fieldRecord = $signed->revision->binding($field);
$widgetRecord = $signed->revision->binding($widget);
$fieldDictionary = $fieldRecord->dictionary ?? throw new LogicException('The signed field retains its dictionary.');
$widgetDictionary = $widgetRecord->dictionary ?? throw new LogicException('The signed widget retains its dictionary.');
$update = new IncrementalUpdate($signed->revision, new FileBody(
    new IndirectObject(
        $fieldDictionary->with($entry('V', new TextString('Reviewed'))),
        $fieldRecord->identifier,
    ),
    new IndirectObject(
        $widgetDictionary->with($entry('AP', new DictionaryType(
            $entry('N', new IndirectReference($appearance('Reviewed'))),
        ))),
        $widgetRecord->identifier,
    ),
));
$filled = $update->toRevision();
```

`$entry` and `$appearance` are the explicit constructors in the full script.
The field and widget keep their object identities. The replacement appearance
receives a fresh identity and refers to the unchanged historical font. The guard
compares every other frozen object too: listing two replacements does not permit
an unrelated content-stream or resource change.

The original signed bytes remain an exact prefix. The new xref section selects
the updated value and widget appearance while preserving the previous revision.
An incremental update retains old content and is unsuitable for erasing secrets.

## Isolate the changed text

The appearance draws its grey frame before the `/Tx BMC`…`EMC` region. The region
owns a balanced `q`, `BT`…`ET`, `Q` sequence for `Reviewed`. The old and new
programs preserve every decoded byte outside it and keep the geometry and
resource-name bindings. `BMC`/`EMC` alone do not save graphics state. Paths,
pending clipping and text objects cannot cross the protected boundaries.

The operation does not rebuild button appearances or add states/alternatives
without a comparable historical program. It also does not prove that arbitrary
glyph programs visually match a value. The [protected-revisions guide](../protected-revisions.md)
lists supported fields, markup subtypes, lexical limits and explicit UR3 authority.

## Check what the result proves

qpdf checks syntax; rendering shows the replacement text and preserved frame.
Independent CMS/ByteRange verification checks the signature over its original
bytes. pyHanko's unchanged modification policy reports `OTHER` for this example
because the changed AP belongs to a widget child without `/T`. This is recorded
as an oracle limitation, not presented as a pyHanko DocMDP approval.

Change the `Response` value and its Tx appearance together to try another fill.
Attempting to fill `Reference`, change page text or mutate the historical font
must be refused. P1 does not authorize filling, and adding a signature or DSS to
the same staged fill is outside the classifier's separate operation proofs.
External-chain import, templates, rich text, new resources, PKI validation and
human interpretation remain outside this example.

[← 36. Apply redaction](36-applied-redaction.md) · [Protected native revisions](../protected-revisions.md) · [All tutorials](README.md)
