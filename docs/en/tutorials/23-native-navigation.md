# 23. Labels, articles and presentation

The [complete script](https://github.com/PDFToolkit/pdf/blob/v0.9.1/examples/native-navigation.php)
builds three pages identified by `i`, `AA` and `A-8`. Two articles and a presentation
list connect these pages without changing their drawing instructions. Bookmarks
demonstrate an explicit destination, a PDF name and a destination string.

```sh
php examples/native-navigation.php native-navigation.pdf
```

## Labels independent of indices

Page indices remain `0`, `1`, `2` in tree order. `PageLabels` composes a real
`NumberTree` with a `LabelRange` for each range start. The range at index zero
is required; the writer checks starts against pages actually present in the catalog.

`PageLabel` distinguishes style, prefix and initial number `St`, which is at
least one. `D`, `R`, `r`, `A`, `a` represent decimal numbers, Roman numerals and
letters. Alphabetic style repeats the same letter: `A…Z`, `AA…ZZ`, then
`AAA…ZZZ`. The script starts the second range at 27, giving `AA`.

Absence of a style produces only the prefix, even if `St` is supplied; without
a prefix, the label is an empty string. `label()` calculates a range label and
`labelsFor($catalog)` supplies labels for this document's pages. Output limits
are explicit to avoid allocating enormous text for a very large alphabetic or
Roman number.

## A destination describes a view

`LocalDestination` composes the eight existing objects `XYZ`, `Fit`, `FitH`,
`FitV`, `FitR`, `FitB`, `FitBH`, `FitBV`. The first element is a reference to a
page in this document. Validation checks parameters and actual membership; an
outside page cannot become a local destination merely by being added to the file body.

`NamedDestinations` builds string mappings in `Names.Dests`. `LegacyDestinations`
builds name mappings in `Catalog.Dests`, with the indirect reference required
by the catalog. The two spaces are distinct: in the example, name `/details`
targets page `AA`, whereas string `(details)` targets a rectangle on `A-8`.

`NamedDestination` expresses that reference without converting names into strings.
`toObject()` returns the corresponding primitive when the application constructs
an entry itself. `GoToDestination` composes a local `/GoTo` that verifies name
resolution during writing. `DestinationDictionary` can also associate explicit
attributes with a tree destination. The `GoToDestination` constructor accepts
a `next` action or action array too, without imposing a tree structure on references.

View fitting is a separate operation:

```php
$view = $destination->resolve(
    new DestinationViewport($windowWidth, $windowHeight, $currentView),
    new DestinationGeometry($cropBox, $contentBounds),
);
```

Window dimensions and current position are supplied as numeric objects. `null`
parameters preserve current values; zero `XYZ` zoom has the same meaning.
`FitB` explicitly requests the content box and restricts it to CropBox. The
core does not infer drawing bounds from bytes. Calculated positions use default
user-space axes; physical screen transformations and interface rotation belong
to the reader. A box with no area cannot define a fitting zoom.

## An article traverses page regions

`ArticleThread::addBead()` chooses reading order. Each `ArticleBead` has a
rectangle; its `N` and `V` references are derived from that order. The last
returns to the first, and the first to the last. For a single-bead article,
both references target that same bead.

The first bead always has `T`, a reference to its article. Others may also
supply it starting with PDF 1.2 using `includeThread: true`. `ArticleThreads`
constructs the indirect `Catalog.Threads` reference. Article titles may be
identical: order remains the author's choice.

`PageBeads` separately supplies drawing order in each page's `B` array. On `AA`,
the script lists the note before the article continuation while retaining both
rings. To resolve the cyclic relationship with `P`:

1. Construct beads, articles and page collections.
2. Supply `PageBeads::pageEntry()` to each page constructor.
3. Attach pages to the tree.
4. Call `bindToPage()` on the collections with those same pages.

The writer checks that each bead occurs exactly once in `B`, its article is
registered and its true owner is `P`. No page clone or global registry replaces
this association.

## Transitions and presentation steps

`PagePresentation` distinguishes display duration `Dur` from incoming transition
`Trans`. The first page declares a 3.5-second Split transition, vertical and
outward, followed by a 5-second display. Absence of display duration disables
automatic advancement; duration zero is immediate.

`Transition` checks style-specific parameters: `Dm` for Split/Blinds, `M` for
Split/Box/Fly, `Di` angles depending on style and `SS`/`B` for Fly. Angles are
measured counterclockwise from the right, unlike `Page.Rotate`. The second
page's Fly uses `None` and scale 0.25. Style `R` replaces the page without an
effect and ignores transition duration.

`PresentationSequence` builds the `PresSteps` `NavigationNode` objects as a
doubly linked list. Its ends remain open: they do not form an article ring.
The primary node can be chosen in the middle. The script supplies its entry
to the page, then binds the sequence after attachment to the tree.

A forward or direct-access request selects `NA`, then `Next`; a backward
request selects `PA`, then `Prev`. `enter()` and `request()` return that explicit
plan without executing actions. The example's last node leaves the page through
a local destination and therefore has no `Next`.

Relationships are checked in the document's effective view, including during
incremental writing. Changing an old builder without submitting it to the new
revision does not change the written PDF. Replacing an object preserves its
PDF identity in historical references; deleting an article also requires
removing the affected `B` arrays. Old unreachable dictionaries may remain in
earlier cross-reference sections.

Verification inspects declared navigation actions, including `Next` chains,
with bounded traversal. It does not infer the effects of opaque scripts.
Action cycles are not treated as forbidden tree cycles: the specification
describes how readers handle them. The typed list remains a finite construction,
frozen when attached to a page.

## Versions and verification

Articles and names require PDF 1.1, destination strings PDF 1.2, labels PDF 1.3
and PresSteps PDF 1.5. The five Fly/Push/Cover/Uncover/Fade styles also require
PDF 1.5. The writer considers the effective header and catalog version.

```sh
qpdf --check native-navigation.pdf
php tools/fixtures/native_navigation.php > navigation-vectors.json
python tools/validate_native_navigation.py native-navigation.pdf navigation-vectors.json
```

The independent oracle inspects all three pages, labels, rings, `P`/`B`, both
destination spaces and `PresSteps` links. It also compares 55 labels and ten
view fittings with Python calculations, then reads three revisions of another
document to verify replacements and deletions. Static rendering shows regions;
article reading, timers and animations remain functions of the PDF application.

References: ISO 12.3.2, physical pages 373–375; ISO 12.4.2–12.4.4, physical pages
382–389; GoTo, ISO 12.6.4.2, physical page 426.

[Index](README.md) · [Complete code](https://github.com/PDFToolkit/pdf/blob/v0.9.1/examples/native-navigation.php)
