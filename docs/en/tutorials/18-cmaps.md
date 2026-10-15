# 18. A composite encoding different from Identity-H

The [complete script](https://github.com/PDFToolkit/pdf/blob/v0.9.1/examples/cmap-font.php)
displays `ABCDEF éΩ fi` with a one-byte encoding in an embedded CMap. The font
comes from the optional conversion module; PDF objects and CMaps remain in the core.

```sh
php examples/cmap-font.php cmap-font.pdf
```

The Type0 font maps codes to CIDs through `/Encoding`. Its descendant maps CIDs
to glyphs and metrics. `/ToUnicode` maps original codes to Unicode text for search
and extraction. These are three distinct relationships.

The base CMap defines a codespace, a CID range and `notdef` mappings. The extended
CMap references it through `/UseCMap`, then adds codes. Codespace boundaries are
checked byte by byte; an ordinary integer interval cannot correctly represent
every multibyte range.

The Unicode CMap demonstrates `bfchar`, a sequential `bfrange` and a range using
an array of destinations. The `fi` code produces two Unicode characters: extracted
text can differ from glyph count. UTF-16BE and surrogate pairs are explicitly checked.

Changing codes requires consistent changes to content and `ToUnicode`. A CMap
does not rewrite the font program. Vertical mode and its metrics are explicit choices too.

CI verifies extracted text with pypdf and Poppler.

Reference: ISO 9.7 and 9.10, physical pages 268–292 and 299–302.

[Index](README.md) · [Complete code](https://github.com/PDFToolkit/pdf/blob/v0.9.1/examples/cmap-font.php)
