# Delete and reuse an indirect object

An indirect object is identified by its **number and generation**. An update
can free its number, then assign it to a new identity. The old reference must
not designate that new value.

Run [object-lifecycle.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/object-lifecycle.php):

```bash
php examples/object-lifecycle.php /tmp/object-lifecycle.pdf
```

The generated PDF contains three revisions, one page and two private document
references. The page remains visible; console output displays both generations.

## Write the first revision

The catalog references a string under `PrivateOriginal`.
`FileStructure::toRevision()` returns bytes and their frozen objects.
`binding($old)->identifier` returns the identifier assigned to the string.

```php
$initial = $file->toRevision();
$identifier = $initial->binding($old)->identifier;
```

The application still constructs PDF objects. The serialization context assigns
their identifiers in this file; no global registry connects different documents.

## Release the number

`ReleaseIndirectObject` requests release of the exact identifier. The writer
adds an xref section; it removes no bytes from the first revision. The free
generation becomes `1` and the number enters the free list.

```php
$released = (new IncrementalUpdate(
    $initial,
    new FileBody(),
    objectOperations: new ReleaseIndirectObject($identifier),
))->toRevision();
```

`PrivateOriginal` keeps its old generation `0` reference. In PDF, a reference
to a nonexistent object has value `null`. Dictionaries can therefore retain
an obsolete optional reference. Required graph links, such as necessary page
resources, are checked separately.

Native protections reject releasing the root catalog, pages, xref structure
or encryption dictionary. Deleting an `ObjStm` container requires releasing
all its still-compressed members first.

## Assign the number to a new identity

`ReuseObjectNumber` receives the free number and a new value. Here the value
is a dictionary; it does not inherit the old string's PHP aliases. The new
reference uses free generation `1`.

```php
objectOperations: new ReuseObjectNumber($identifier->objectNumber, $new)
```

The example also replaces the catalog under its existing identifier to add
`PrivateCurrent`, a reference to that dictionary. `reference($old)` keeps the
original pair; `reference($new)` supplies the new pair. Their numbers match
and their generations differ.

A second deletion would increment the free generation to `2`. Generation
`65535` is permanent and cannot be reused. Never-assigned gaps are distinguished
from deleted objects: their generation is `0`. A free-list number cannot serve
as a new `ObjStm` container or member, even when it came from a generation `0` gap.

## Preserve evidence of what was written

Each `FileRevision` exposes `previous`, effective objects, retired generations
and an immutable `FreeListState`. Snapshots retain remapped references and
dictionaries actually emitted. For a stream, they retain encoded bytes before
encryption from the same write call. These snapshots are evidence; a
`RevisionStreamSnapshot` cannot be serialized as a new stream. A new write
requires a new explicit stream object.

`LinearizedWriter::revision()` also supplies this snapshot. An incremental
revision can be added; following Annex F, the resulting file ceases to be
linearized. Initial bytes, their `/L` and hint ranges remain unchanged. These
mechanisms concern generated files; reading an external PDF's history belongs
to the reader module.

## Verification and references

The release-and-reuse corpus verifies 90 histories, or 450 PDFs, under PHP 8.3,
8.4 and 8.5. It checks free lists, generations, physical xref sections, old and
new references, compressed objects and nine security variations. The oracle
uses unmodified qpdf and checks effective values. A pypdf cache limitation for
some obsolete generations is identified; new values and streams remain verified
without a blanket exception.

Revisions after linearization have a separate corpus of 90 histories, or 270
PDFs, with exact checks of prefixes, references and hints.

Preserved sources: [indirect objects and null, page 29](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/PDF32000_2008.pdf#page=29),
[xref, pages 48–50](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/PDF32000_2008.pdf#page=48),
[updates and ObjStm, pages 52–55](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/PDF32000_2008.pdf#page=52),
[Annex F, page 683](https://github.com/PDFToolkit/pdf/blob/v0.7.1/resources/reference-documents/PDF32000_2008.pdf#page=683).

[Tutorial path](README.md) · [Incremental revisions](11-incremental-update.md)
