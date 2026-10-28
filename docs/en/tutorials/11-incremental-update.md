# 11. Update a PDF through revisions

An incremental update appends objects and a new cross-reference section to the
file. Previously written bytes remain intact. This example creates a document,
replaces its content stream twice and preserves the original font, page and catalog.

## Run the example

```sh
php examples/incremental-update.php incremental-update.pdf
```

The [complete script](https://github.com/PDFToolkit/pdf/blob/v0.11.0/examples/incremental-update.php)
produces a page displaying “Revision 2 : contenu mis a jour.” The file also
contains bytes from revisions 0 and 1, but the reader uses the latest xref
records to resolve the page's stream.

![Preview of the latest revision](../../tutorials/previews/incremental-update.png)

## 1. Freeze an initial revision

`FileStructure::toRevision()` passes the graph to `FileWriter` and receives a
`FileRevision`. This object contains serialized bytes, the last xref position,
`/Size`, catalog, additional trailer entries and document identities. It does
not read an existing PDF file.

```php
$initial = $file->toRevision();
$identifier = $initial->binding($initialContents)->identifier;
```

An object number belongs to that revision. `binding()` retrieves its identifier
from an instance or explicit `ObjectIdentifier`. `reference()` returns an ordinary
`IndirectReference` to the effective value, so dictionary type constraints remain available.

## 2. Select the replacement

A new `StreamObject` instance represents new content. `IndirectObject` preserves
the old stream's number and generation:

```php
$update = new IncrementalUpdate(
    $initial,
    new FileBody(new IndirectObject($newContents, $identifier)),
);
$next = $update->toRevision();
```

`FileBody` selects objects to write. A reference to an object in an earlier
revision produces only `n g R`: it does not traverse or rewrite that graph.
A historical instance explicitly placed in `FileBody`, however, is rewritten
under its existing identifier. Changing a builder after the snapshot does not
change already frozen bytes.

Historical aliases are retained during replacement. An old PHP reference to
the initial stream remains a reference to the same PDF number, even after
several updates; `reference()` now returns the new effective value. Newly
referenced objects receive numbers starting at the previous `/Size`, without
reusing old gaps, and begin with generation zero. A replacement preserves the
value's PDF family and its `/Type` if defined: historical references cannot
silently turn a stream into a number or a page tree into another dictionary.

## 3. Link cross-references

`IncrementalWriter` starts with `$initial`'s bytes. It measures new offsets from
the beginning of the complete file. The new `/Prev` entry targets exactly the
previous revision's xref section; `startxref` targets the newly appended section.

The xref format is inherited from the initial revision. This example uses xref
streams; traditional tables are supported too. A new `ObjectStream` can contain
new or replaced objects with generation zero. An old container is not replaced:
a new one is constructed. A previously compressed member can also become a
standalone object under the same number.

`CrossReferenceSection` distinguishes the complete initial index from partial
incremental sections. Unused new numbers are represented by free entries and
linked to the existing free list. `CrossReferenceLimits` bounds cumulative
capacity to 100,000 entries by default; a writer can receive an explicitly different limit.

## 4. Inherit the trailer

All additional entries from the previous trailer are carried forward, including
private extensions. Entries supplied by the new revision replace them individually.
In the example, `/Info` targets a new title while the catalog stays unchanged.

Writers manage `/Size`, `/Root`, `/Prev` and xref structures. Original `/ID[0]`
is preserved. If `/ID` exists and is not explicitly replaced, its second identifier
is renewed using a deterministic fingerprint of revision content. This fingerprint
is a file identifier, not a signature. An explicit `/ID` must preserve the first identifier.

## Try it

- Use `CrossReferenceFormat::Table` to obtain textual `xref` sections.
- Add a third update and count `startxref` and `/Prev` occurrences.
- Replace only `/Info` to change metadata without rewriting page content.
- Keep an old stream reference and use it in a new value to observe its number being preserved.

## Verification and limitations

```sh
qpdf --check incremental-update.pdf
qpdf --show-xref incremental-update.pdf
```

Editable revisions come from the library’s own `FileRevision` objects. Reader 0.7 inspects external PDFs and can import/remap an explicitly selected graph into a new document. Import does not convert source history into editable native revisions or transfer signature authority. Object release/reuse, xref/hybrid formats, encryption, signatures and linearization have their own core mechanisms. Incremental updates retain old bytes and must not be used to erase confidential information.

References: ISO 32000-1:2008, **7.5.4–7.5.8** for xref, trailers, revisions and
object containers, and **14.4** for file identifiers.

[← 10. JPEG and PNG images](10-image-files.md) · [All tutorials](README.md)

For bounded filling of an actually certified native revision,
continue with [lesson 37](37-protected-form-fill.md) and the
[protected-revisions guide](../protected-revisions.md).
