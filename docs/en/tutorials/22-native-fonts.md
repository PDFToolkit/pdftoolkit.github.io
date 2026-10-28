# 22. Simple fonts, Type3 and vertical writing

The [complete script](https://github.com/PDFToolkit/pdf/blob/v0.11.0/examples/native-fonts.php)
combines Type3 glyphs drawn with PDF operators, an embedded simple font and a
composite font whose metrics position glyphs vertically.

```sh
php examples/native-fonts.php native-fonts.pdf
```

A Type3 font contains `CharProcs`, each a drawing stream. `d0` or `d1` declares
its width and, where applicable, its box. `Type3CharProcs`, `EncodingDifferences`
and `SimpleWidths` connect names, codes and metrics. The font matrix transforms
glyph coordinates into text space. The drawing program does not become a layout engine.

Since core 0.11, `FontDescriptor` accepts `fontName: null` for a Type3 font.
Other subtypes still require a name; `requiredName()` expresses that precondition.
When `Type3Font.Name` and the descriptor's `FontName` are both present, they must
agree (EC3 #11). A Type3 font used in Tagged PDF still requires its indirect
descriptor. The [migration guide](../migration-0.11.md) explains this API change.

`Type3Font` may omit `Resources`. Its glyph program then uses the resources
provided by its PDF context, which the reader must be able to resolve (EC3 #128).
Supplying an empty dictionary is different from omitting the entry. Glyphs can
contain permitted PDF graphics operators, including text and nested Forms.
WTPDF inspection follows only actually selected glyphs, with shared budgets and
cycle rejection; it is not a rasterizer and does not validate opaque programs.

A simple font uses one-byte codes, `FirstChar`, `LastChar` and corresponding
widths. Its `FontDescriptor` describes metrics and references an embedded program.
`FontFile`, `FontFile2` and `FontFile3` have distinct formats and lengths; the
program is supplied normalized. The script uses the optional module to prepare
TrueType data, then composes them into the core's PDF objects.

A composite font uses CIDs. `DW`/`W` supplies horizontal widths; `DW2`/`W2`
supplies vertical displacement and origin position. Their range representation
does not expand every CID in memory. Encoding selects vertical mode;
`/ToUnicode` preserves characters for extraction.

Subset names have a `SubsetFontName` object and explicit tag. The writer shares
a per-document registry and rejects a collision between distinct programs.
The core neither automatically subsets programs nor shapes complex scripts.

Change Type3 glyphs or vertical metrics to see their roles directly. CI verifies
encodings, programs, CID/GID mappings and extracted text with pypdf and Poppler.
Some readers classify FontFile3/OpenType with glyf outlines as TrueType; Table
126 permits that declaration, and the example's rendering is checked separately.

Fonts 0.2 supplies a separate [OpenType layout example](https://github.com/PDFToolkit/pdf-fonts/blob/v0.2.0/examples/opentype-layout.php) for static TrueType/CFF1, selected ligatures/kerning/marks and real PDF placement. Its [guide](https://pdftoolkit.github.io/modules/fonts/opentype-layout.html) distinguishes CID/GID mappings, aliases and CFF container interoperability. It does not add automatic script itemization, bidi or a vertical compositor to this native-font example.

Reference: ISO 9.5–9.10, Tables 110–127, physical pages 261–303; Annex D.

[Index](README.md) · [Complete code](https://github.com/PDFToolkit/pdf/blob/v0.11.0/examples/native-fonts.php)
