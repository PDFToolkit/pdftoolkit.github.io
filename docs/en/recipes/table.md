# Recipe: an explicitly drawn table

[Practical examples](README.md) · [Tutorial path](../tutorials/README.md)

## Goal and prerequisites

Draw a small table of five items with a dark header, alternating rows, a grid
and two fonts. Layout remains in
[examples/table.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/table.php):
the core receives PDF operator objects.

Read the [pages and text](../tutorials/02-pages-and-text.md) and
[graphics](../tutorials/03-graphics.md) tutorials. Install dependencies with
`composer install`, then use PHP 8.3 or later and the extensions required by Composer.

## Run and inspect

From the root of a core checkout:

```sh
php examples/table.php
php examples/table.php table-demo.pdf
```

The first call produces `examples/table.pdf`. The result fits on one page,
with four columns and a total line below the grid. Data are fictional; monetary
values are preformatted demonstration strings.

![Preview of the table recipe](../../tutorials/previews/table.png)

## What the script builds

The page is 595 units wide and 842 high. The table starts at `x = 54`, `y = 716`,
is 487 units wide and has six rows of 34 units, including the header. Its bottom
is therefore `716 - 6 × 34 = 512`. With this example's page settings, one unit
is 1/72 inch; these values resemble typographic points.

| Step | Objects used | Purpose |
| --- | --- | --- |
| Data and geometry | PHP arrays, widths and row height | Calculate drawing specific to this example |
| Resources | Two `Type1Font` objects, a `/Font` entry | Select Helvetica and Helvetica-Bold through `/F1` and `/F2` |
| Backgrounds | `SetNonstrokingRGBColor`, `AppendRectangle`, `FillPathNonzero` | Fill the header and alternating rows |
| Grid | `SetStrokingRGBColor`, `SetLineWidth`, `MoveTo`, `LineTo`, `StrokePath` | Build every segment, then stroke them |
| Cells | `BeginTextObject`, `SetTextFontAndSize`, `MoveTextPosition`, `ShowText`, `EndTextObject` | Explicitly position each line of text |
| File | `ContentStreams`, `StreamObject`, `PageObject`, `DocumentCatalog`, `FileStructure` | Turn instructions into a PDF document |

PHP lists help calculate repeated elements. Resulting instructions remain
objects: every number is a `NumericType`, every resource name a `NameType` and
every string a `LiteralString`.

## Color, paths and text

`rg` sets the fill color, also used for glyphs. The header first receives a dark
background; its text then receives a white fill. `RG` sets outline color, here
for the grid. Changing color draws nothing by itself.

`AppendRectangle` corresponds to `re`: its parameters are **x, y, width, height**.
After each background rectangle, `FillPathNonzero` (`f`) fills and ends the path.
Grid segments can share one path: each `MoveTo` (`m`) starts a subpath, each
`LineTo` (`l`) adds a segment, and the final `StrokePath` (`S`) strokes them.

For cells, `y` decreases while moving down the table. Horizontal offset 10 is
the chosen inner margin. Vertical offset 22 places the text **baseline**; it
does not measure glyph height. Each cell opens its own `BT`/`ET`, so its `Td`
starts from the identity text matrix rather than accumulating previous cells' movements.

## Mapping to ISO 32000-1:2008

| Concept | Reference |
| --- | --- |
| Coordinate systems and units | §8.3.2 |
| Line width | §8.4.3.2 |
| Path construction and painting | §8.5.2 and §8.5.3 |
| Color operators | §8.6.8 |
| Type 1 fonts and standard fonts | §9.6.2 |
| Text state and positioning | §9.3 and §9.4 |

“Table” describes the visual result here. A semantic, accessible table requires
additional PDF logical structure (§14.7), which this recipe does not build.
The [specification preserved in the core](https://github.com/PDFToolkit/pdf/blob/v0.5.4/PDF32000_2008.pdf)
and [architecture guide](../architecture.md) explain the framework for these objects.

## Adapt the recipe

Adding a row to `$rows` extends the grid and moves the final note. Adjusting
`$columnWidths` moves separators and cell origins. `$rowHeight` changes backgrounds,
the grid and baselines together; reconsider the text offset if height becomes
too small. Changing RGB triples, whose components here range from 0 to 1,
changes the palette.

The recipe assumes all values fit on one line and one page. It does not measure
glyphs, calculate amounts, align decimals, hyphenate or trigger page breaks.
A layout library can calculate those decisions before producing the same core objects.

[Back to practical examples](README.md) · [Review graphics operators](../tutorials/03-graphics.md)
