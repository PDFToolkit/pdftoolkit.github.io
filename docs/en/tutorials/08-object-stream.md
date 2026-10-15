# 08. Filters, compressed objects and cross-references

This lesson takes a text page and changes how its objects are stored in the file. It demonstrates the difference between compressing a stream's content and grouping dictionaries inside an object stream.

**Prerequisite:** read the [first document](01-first-document.md). The previous lesson's [gradient](07-gradient.md) is independent of this topic.

## Run the example

```sh
php examples/object-stream.php
```

Open `examples/object-stream.pdf`. The page displays “An explicit object stream and cross-reference stream.” Visually it remains an ordinary page; the object container becomes apparent when inspecting the PDF's structure.

![Preview of the page with compressed objects](../../tutorials/previews/object-stream.png)

The [commented code](https://github.com/PDFToolkit/pdf/blob/v0.11.0/examples/object-stream.php) explains each step. It uses a standard font and text stream like the first tutorial.

## 1. Compress the content stream

`StreamObject` receives a `FlateDecode` in addition to its content. This instance encodes the bytes and produces the `/Filter /FlateDecode` entry. The name describes the operation the reader will use to decode the stream.

`/Length` describes bytes **after** compression. Do not manually provide a length calculated from the original instructions. This compression concerns that specific stream, not every document structure.

## 2. Form an object container

```php
$objects = (new ObjectStream(
    new ObjectStreamEntry(new ObjectNumber(40), $catalog),
    new ObjectStreamEntry(new ObjectNumber(41), $pages),
    new ObjectStreamEntry(new ObjectNumber(42), $page),
    new ObjectStreamEntry(new ObjectNumber(43), $font),
))->withFilters(new FlateDecode());
```

An `ObjectStream` is a stream with `/Type /ObjStm`. The four entries select the objects stored inside. Numbers 40 to 43 are explicit to make the example inspectable; the writer reserves them and assigns other numbers without collisions.

The container carries `/N`, the member count, and `/First`, the offset at which their data start after the internal index, in the container's **decoded** bytes. In contrast, `/Length` measures the encoded bytes written to the file. `withFilters()` returns a new container; the script retains that value. Its `FlateDecode` compresses the index and grouped objects. This is a second compression, independent of page-content compression.

Members have generation zero and cannot themselves be streams. The content stream therefore remains an indirect object outside the container. The catalog and page retain their references to each other regardless of their physical representation.

## 3. Use a cross-reference stream

`CrossReferenceFormat::Stream` requests a `/Type /XRef` stream instead of a textual `xref` table. Cross-reference entries describe, among other things:

| Type | Object location |
| --- | --- |
| 0 | Free object. |
| 1 | Standalone indirect object, identified by its file offset. |
| 2 | Compressed member, identified by its container number and index inside it. |

An `/ObjStm` member requires this type 2 representation. The writer therefore rejects an object stream combined with `CrossReferenceFormat::Table`. `/Root` continues to reference the catalog even when the catalog is compressed.

Object and cross-reference streams have existed since PDF 1.5. The example uses a 1.7 header. A traditional table and a cross-reference stream are two file representations; this choice performs neither linearization nor incremental updating.

## Inspect the file

With qpdf installed:

```sh
qpdf --check examples/object-stream.pdf
qpdf --show-xref examples/object-stream.pdf
qpdf --qdf --object-streams=disable examples/object-stream.pdf objets-decompresses.pdf
```

`--show-xref` lets you locate objects 40 to 43 in the container. The last command rewrites the document with standalone objects and decompressed streams to make them easier to read. Object numbers may change during rewriting.

## Variations

- Remove the content-stream filter to read its instructions directly in the file while retaining the compressed object container.
- Remove `->withFilters(new FlateDecode())` to leave the container's index and members uncompressed while retaining their grouping in `/ObjStm`.
- To return to the first tutorial's file, use `FileBody($catalog)`, remove the container and choose `CrossReferenceFormat::Table`.

**In the specification:** filters (§7.4), object streams (§7.5.7), cross-reference streams and entry types (§7.5.8).

[Previous: gradient and function](07-gradient.md) · [Tutorial index](README.md) · [Recipe: table](../recipes/table.md)
