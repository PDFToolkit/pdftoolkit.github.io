# 05. Internal and external links

[Tutorial path](README.md) · [Previous: navigation](04-navigation.md) · [Next: images](06-images.md)

## Goal and prerequisites

Create two clickable areas on a page: one opens the GitHub repository, the other displays a second page. This tutorial composes classes derived from specification tables to show how to use a feature without a specialized domain facade.

Read [pages and text](02-pages-and-text.md) and [destinations](04-navigation.md), then install dependencies with `composer install`. The script [examples/links.php](https://github.com/PDFToolkit/pdf/blob/v0.9.1/examples/links.php) runs independently on PHP 8.3 or later with the extensions required by Composer.

## Run and inspect

From the root of a core checkout:

```sh
php examples/links.php
php examples/links.php links-demo.pdf
```

The first call produces `examples/links.pdf`. The first page displays two blue text strings; the second leads to the page “Vous avez suivi le lien interne”. The GitHub link offers to open an external address, according to the reader's settings.

![Preview of the page with two links](../../tutorials/previews/links.png)

The image helps locate the text. Test links in the original PDF with an interactive reader: a page image does not carry annotations.

## Drawing and interaction

`ShowText` produces visible glyphs. Neither their color nor their content creates a link. Interaction belongs to another object: an annotation with `/Subtype /Link`, referenced in the page's `/Annots` array.

Its `/Rect` is the active area, in page coordinates. The four numbers give two opposite corners, **lower x, lower y, upper x, upper y**, whereas the graphics operator `re` uses **x, y, width, height**. The script places text inside these areas and uses `/Border [0 0 0]` to suppress the border drawn by the reader.

## Read the construction

1. **Create the target page.** The script first builds the second `PageObject`. The internal link targets this instance; final order is still determined by calls to `addKid()`.
2. **Describe the external action.** `URIActionTable206` contains `SEntry(new NameType('URI'))` and `URIEntry(new LiteralString(...))`. `/S` is the action type; `/URI` contains its ASCII address. The annotation references this dictionary through its `/A` entry.
3. **Describe the internal destination.** The second annotation receives `DestEntry(new Fit($targetPage))`. There is no `/A` action here: `/Dest` is an explicit destination. The specification forbids adding `/Dest` when `/A` is present on the same link; the script follows that composition rule.
4. **Compose common entries.** `TypeEntry`, `RectEntry`, `BorderEntry` and `ContentsEntry` come from Table 164. `SubtypeEntry`, `AEntry` and `DestEntry` come from Table 173. `LinkAnnotationTable173` composes the common Table 164 definition, including its required entries.
5. **Attach annotations.** `AnnotsEntry` belongs to Table 30, which describes the page. Its `ArrayType` contains `IndirectReference` instances to both annotations. Each annotation therefore retains its own PDF object identity.
6. **Assemble the page tree.** The first `PageObject` receives `/Annots` before attachment. The page containing the links is added first, followed by the target, to the same `PageTreeNode`.

`ContentsEntry(new TextString(...))` supplies a text description of each annotation. This description helps interpret the object; by itself, it does not constitute a complete PDF accessibility structure.

## Why these class names?

The names `LinkAnnotationTable173` and `URIActionTable206` retain the connection to ISO tables. Their entries and definitions are PHP objects, and known constraints are checked during construction or serialization. The number distinguishes tables with similar titles and makes their source easier to find.

Definitions also expose conditional rules in their descriptions. They do not automatically guarantee every possible relationship between entries. Here, the code deliberately chooses only one of the two targets `/A` and `/Dest`, supplies the correct names `/Link` and `/URI`, and uses indirect references in `/Annots`.

## Mapping to ISO 32000-1:2008

| Object or entry | Reference |
| --- | --- |
| Page `/Annots` | §7.7.3.3, Table 30 |
| Common annotation entries | §12.5.2, Table 164 |
| `/Link` annotation | §12.5.6.5, Table 173 |
| Explicit `/Fit` destination | §12.3.2.2, Table 151 |
| `/URI` action | §12.6.4.7, Table 206 |

See the [specification preserved in the core](https://github.com/PDFToolkit/pdf/blob/v0.9.1/resources/reference-documents/PDF32000_2008.pdf) and the [definitions guide](../specification.md).

## Variations and limitations

To target a named destination, replace `Fit` with a `LiteralString` containing a key published in `/Names /Dests`, as in the [navigation tutorial](04-navigation.md). To move a link, change both text position and annotation rectangle: their association is a layout decision in this script.

The active area is rectangular; it is not calculated from font metrics. The visible text's ASCII values avoid encoding issues with standard fonts here. There is no automatic line wrapping or custom annotation appearance. The reader may request confirmation before following an external link.

[Back to the tutorial path](README.md) · [Continue: images](06-images.md)
