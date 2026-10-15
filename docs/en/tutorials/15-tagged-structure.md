# 15. Connect content to its logical structure

The [complete script](https://github.com/PDFToolkit/pdf/blob/v0.11.0/examples/tagged-structure.php)
builds three pages: a title, a paragraph continuing onto the second page, a table
with an identified header, and a link associating its text with its annotation.

```sh
php examples/tagged-structure.php tagged-structure.pdf
```

Operators draw visible content. A `BDC`/`EMC` sequence assigns an `MCID` to a
portion of content. This integer is local to its container; another page can
have the same integer. Multiple `/Contents` streams on one page are read in
order, even when a sequence begins in one and ends in another.

`StructureTreeRoot` and `StructureElement` compose logical reading order
independently of positions. `/K` children can be other elements, page content,
an `MCR` specifying another page or an `OBJR` to an annotation. The example uses
an `MCR` for the continuing paragraph and an `OBJR` for the link's interactive area.

`ParentTree` establishes reverse links from `StructParents` and `StructParent`.
`IDTree` identifies the table header; the cell's `Headers` uses that identifier.
`ClassMap` shares attributes while retaining revisions specific to each association.

Footers are artifacts. Language `fr-FR` and `MarkInfo.Marked` declare the chosen
conventions. Objects check roles, associations and identities; reading-order
quality and alternatives remain editorial responsibilities. This example is
not a PDF/UA certification.

Changing MCIDs, page links or header identifiers shows why these values depend
on the entire graph.

Reference: ISO 14.7–14.9, physical pages 564–628.

[Index](README.md) · [Complete code](https://github.com/PDFToolkit/pdf/blob/v0.11.0/examples/tagged-structure.php)
