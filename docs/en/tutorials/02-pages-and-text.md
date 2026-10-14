# 02. Multiple pages and text positioning

[Tutorial index](README.md) · [Previous: first document](01-first-document.md) · [Next: paths and colors](03-graphics.md)

This lesson builds three A4 pages that share resources. It shows how to position text, choose leading and compose a footer. The complete script is [pages-and-text.php](https://github.com/PDFToolkit/pdf/blob/v0.5.4/examples/pages-and-text.php).

## Run the example

Use PHP 8.3 or later and the dependencies installed by `composer install`, as in the [first tutorial](01-first-document.md). From the root of a core checkout:

```sh
php examples/pages-and-text.php pages-and-text.pdf
```

The first argument names the output file. Without an argument, the script writes `examples/pages-and-text.pdf`. Its parent directory must already exist.

## What you get

Three A4 pages, each with a title, subtitle, several lines of text and a page number. The body uses a size of 13 units and leading of 22 units. Displayed strings are deliberately ASCII; the document title in the metadata contains accented characters.

![First page of the pages and text tutorial](../../tutorials/previews/pages-and-text.png)

## 1. Share resources and page dimensions

The two `Type1Font` instances represent Helvetica and Helvetica-Bold. The resources' `Font` dictionary associates these objects with names `/F1` and `/F2`. `SetTextFontAndSize` targets this local name: `/F1` is not the font's commercial name.

`PageTreeNode` receives the `/MediaBox` and `/Resources` entries. The three `PageObject` instances supply only their `/Contents` streams. When a page has no local value for an inheritable entry, the PDF reader follows the `/Pages` tree upwards: here it finds the same rectangle and resources.

```php
$page = new PageObject(contents: new StreamObject($contents));
$pages->addKid($page);
```

The tree model produces `/Kids`, `/Parent` and `/Count`. Each page belongs to one parent. References to fonts and resources target the same instances; the serializer assigns each a single object number.

Reference: ISO 32000-1, **7.7.3** for the page tree and inheritable attributes, **7.8.3** for resource dictionaries, **9.6.2.2** for the fourteen standard fonts.

## 2. Understand coordinates

The `/MediaBox` is `[0 0 595.28 841.89]`. In this document, a user-space unit is **1/72 inch**. The rectangle therefore represents approximately an A4 sheet of 210 × 297 mm.

The origin is at the lower left. Position `(54, 778)` places the title near the top edge. Increasing `y` moves text upwards on this page, which has no rotation or additional initial transformation.

`BeginTextObject` (`BT`) initializes the text matrices to the identity. The first `MoveTextPosition` (`Td`) translates the text line matrix by `(54, 692)`. In this initial state, the position therefore directly matches page coordinates. Another `Td` in the same object would be a relative movement in the line's coordinate system, not a new absolute position on the paper.

Reference: **8.3.2.3** for user space, **9.4.1–9.4.2** for text objects and positioning.

## 3. Move down one line

The body is a single text object: `BT`, font selection, leading selection, initial positioning, several text-showing instructions, then `ET`.

| Object | Operator | Effect in this example |
| --- | --- | --- |
| `SetTextFontAndSize` | `Tf` | Select `/F1` at size 13. |
| `SetTextLeading` | `TL` | Set leading to 22 units. |
| `MoveToNextTextLine` | `T*` | Return to the start of the line and move down 22 units. |
| `ShowText` | `Tj` | Draw the string's glyphs. |

Each line is added with `ContentStreams::with()`. The sequence is immutable: assign the result to `$contents`. The blank line is an empty string preceded by `T*`, so it occupies one line of leading.

A `\n` inside `LiteralString` does not compose a paragraph or trigger `T*`. Line widths and breaks are chosen in the script. The footer opens another text object and displays a string built in PHP, such as `Page 1 / 3`. The tree's child count and this string are separate pieces of information.

Reference: **9.3.5** for leading, **9.4.2–9.4.3** for positioning and showing text.

## 4. Distinguish glyphs from metadata

`LiteralString` carries **bytes**. With a simple font, these bytes act as character codes interpreted according to the font's encoding. Supplying a UTF-8 string with accented characters does not automatically select the corresponding glyphs. This example therefore keeps visible text in ASCII.

`TextString` is used here for the metadata title, following PDF text-string rules. It encodes Unicode characters when necessary. It does not convert text intended for `ShowText` into font glyphs.

For French text restricted to WinAnsi, a variation can explicitly declare `/Encoding /WinAnsiEncoding` in `Type1Font` and convert strings to Windows-1252 before creating `LiteralString`. This encoding cannot represent every Unicode character; check the conversion result. General Unicode text needs a suitable font and mapping tables, with embedding and text extraction handled explicitly.

Reference: **7.9.2.2** for metadata text strings and **9.6.6** for simple-font encodings.

## Try it

- Change leading from 22 to 28 to observe the movement caused by each `T*`.
- Give one page an explicit `/MediaBox` to see how it overrides the inherited value.
- Add a fourth chapter and observe that `/Count` and the footers follow their respective constructions.

The script does not measure glyphs, break lines or create a new page when content overflows. These calculations must precede PDF operators; the [table recipe](../recipes/table.md) demonstrates a composition calculated in PHP.

[Tutorial index](README.md) · [Previous: first document](01-first-document.md) · [Next: paths and colors](03-graphics.md)
