# 16. Organize a PDF for progressive access

The [complete script](https://github.com/PDFToolkit/pdf/blob/v0.9.1/examples/linearized.php)
writes three pages, two shared fonts, document information and bookmarks. The
first page and its dependencies appear near the start of the file.

```sh
php examples/linearized.php linearized.pdf
qpdf --check-linearization linearized.pdf
```

The graph remains explicit: resources, content, pages and catalog are built
before the writer. `LinearizedWriter` organizes their bytes according to Annex F.
A shared font retains a single identity.

The dictionary declares length `/L`, first-page object number `/O`, hint-stream
ranges `/H` and main-section position `/T`. These values depend on actual written
bytes. The writer calculates binary hints and offsets using fixed-width fields.

Inherited values become available in page dictionaries. Hints distinguish the
first page's resources from objects shared later. The outline and document
information have their own ranges too.

Linearization facilitates HTTP byte-range requests; it does not supply an HTTP
server. An incremental update invalidates the old file's hints and must be
handled separately.

CI compares hints against a binary oracle and qpdf. Annex F permits an initial
page other than zero; qpdf's limitation for that variation is reported, and
verification uses the separate oracle.

Reference: ISO Annex F, physical pages 683–702.

[Index](README.md) · [Complete code](https://github.com/PDFToolkit/pdf/blob/v0.9.1/examples/linearized.php)
