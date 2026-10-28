# 09 — Embed a TrueType font and preserve Unicode

This tutorial accompanies [`examples/embedded-font.php`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/examples/embedded-font.php).
It builds a `/Type0` composite font using `/Identity-H`, a `/CIDFontType2`
descendant font and every TrueType glyph in Noto Sans. The PDF displays French
and Greek; the reader can select and extract the original characters thanks to
the `/ToUnicode` stream.

This tutorial uses the optional [`pdftoolkit/pdf-fonts`](https://github.com/PDFToolkit/pdf-fonts)
module with the core, at the published versions selected by the
[source manifest](../../../resources/sources.json), to analyze TrueType. The embedded
program, dictionaries and PDF mappings remain core objects. `composer install`
in the core checkout installs the module as a development dependency; an
application installs it from Packagist using
`composer require "pdftoolkit/pdf-fonts:^0.2.0"`. The [package guide](../packages.md)
also explains how to select the core release series.

The demonstration font and its SIL Open Font License are preserved in the
[font module's resources](https://github.com/PDFToolkit/pdf-fonts/blob/v0.2.0/examples/assets/fonts/README.md).
Composer installs them with the module; the core does not distribute the TrueType file.

## Run the example

From the root of a core checkout, after `composer install`:

```sh
php examples/embedded-font.php embedded-font.pdf
```

The output path is optional; the script defaults to `examples/embedded-font.pdf`.
Noto Sans and its license are installed in
`vendor/pdftoolkit/pdf-fonts/examples/assets/fonts/`. The reader can search and
copy French and Greek thanks to the Unicode mappings constructed by the script.

## 1. The font program is a separate object

The application reads the file and supplies its **bytes** to
[`FontProgram`](https://github.com/PDFToolkit/pdf-fonts/blob/v0.2.0/src/TrueType/FontProgram.php).
The model reads no paths and contacts no URLs. The program retains the complete
bytes, its PostScript name, `cmap`, horizontal metrics and glyph bounding boxes.

```php
use PDF\Fonts\TrueType\FontProgram;
use PDF\Fonts\TrueType\UnicodeText;

$program = new FontProgram($fontBytes);
$heading = new UnicodeText('Une police incorporée, objet par objet.');
$body = new UnicodeText('Français : été, cœur, Noël. Ελληνικά : Αθήνα.');
```

The input budget is an explicit
[`FontProgramLimits`](https://github.com/PDFToolkit/pdf-fonts/blob/v0.2.0/src/TrueType/FontProgramLimits.php)
object, defaulting to 32 MiB. The application can impose a lower limit, for example:

```php
$program = new FontProgram($fontBytes, new FontProgramLimits(maxBytes: 1048576));
```

[`UnicodeText`](https://github.com/PDFToolkit/pdf-fonts/blob/v0.2.0/src/TrueType/UnicodeText.php)
validates UTF-8 and retains a list of Unicode scalar values. It does not normalize
text or transform its direction or typographic composition.

Font units are not directly the PDF dictionary's units. An advance of 1,024 in
a font with 2,048 units per em becomes a PDF width of 500. Fractional widths are
preserved. The parser also respects `hmtx` when the last advance record applies
to several glyphs.

## 2. Declare the repertoire before building the graph

The CID program is first prepared and embedded in a core
[`FontFile2`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Fonts/FontFile2.php).
The [`CharacterMapFactory`](https://github.com/PDFToolkit/pdf-fonts/blob/v0.2.0/src/TrueType/CharacterMapFactory.php)
service receives the CID program and produces a core
[`CharacterMap`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Fonts/CharacterMap.php)
from the embedded stream and all characters that will be encoded with this instance.
Each distinct Unicode character receives a distinct CID, starting at 1; CID 0
is reserved for the `.notdef` glyph. A repeated character reuses its CID. Two
characters sharing a glyph retain two CIDs to preserve their identity during extraction.

```php
use PDF\Document\Fonts\FontFile2;
use PDF\Fonts\TrueType\CIDFontProgram;
use PDF\Fonts\TrueType\CharacterMapFactory;
use PDF\Fonts\TrueType\TextEncoder;

$cidProgram = new CIDFontProgram($program);
$fontFile = new FontFile2($cidProgram->bytes, new FlateDecode());
$map = (new CharacterMapFactory($cidProgram))->create(
    $fontFile,
    new UnicodeText($heading->utf8 . $body->utf8),
);
$encoder = new TextEncoder($map);
```

A character absent from the font raises an exception when the repertoire is
constructed. A character present in the font but absent from the repertoire
raises an exception during encoding. There is no implicit addition, silent
replacement by `.notdef` or state shared between documents.

## 3. Assemble the objects defined by PDF

[`CIDFontProgram`](https://github.com/PDFToolkit/pdf-fonts/blob/v0.2.0/src/TrueType/CIDFontProgram.php)
prepares the program for a CID font. ISO 32000-1, 9.9 requires removing the `cmap`
table from a TrueType program embedded through `/FontFile2` for a CID font:
glyph mapping comes from `/CIDToGIDMap`. All glyphs and other tables are retained,
except a possible `DSIG` signature invalidated by the transformation. The sfnt
directory, offsets, checksums and `checksumAdjustment` are recalculated.

The program is embedded by
[`FontFile2`](https://github.com/PDFToolkit/pdf/blob/v0.11.0/src/Document/Fonts/FontFile2.php),
with its uncompressed `/Length1`. The `/FlateDecode` filter compresses the stream
without changing the CID program recovered after decoding.

```php
use PDF\Fonts\TrueType\FontDescriptorFactory;

$descriptor = (new FontDescriptorFactory($cidProgram))->create(
    $fontFile,
    new FontDescriptorFlags(4),
    new NumericType(80),
);
$glyphMap = new CIDToGIDMap($map, new FlateDecode());
$widths = new CIDWidths($map);
$descendant = new CIDFontType2($descriptor, $glyphMap, $widths);
$toUnicode = new ToUnicodeCMap($map, new FlateDecode());
$font = new Type0Font($descendant, $toUnicode);
```

Responsibilities are separate:

| Object | PDF entry or role |
| --- | --- |
| `CIDFontProgram` (module) | TrueType program with every glyph, prepared for a CID font |
| `FontFile2` | Embedded TrueType CID program and `/Length1` |
| `FontDescriptor` | Name, box, ascent, descent, angle, flags and `/FontFile2` |
| `CIDToGIDMap` | CID → glyph-index mapping in two-byte big-endian words |
| `CIDWidths` | `/W`, expressed in the PDF glyph system's 1,000 units |
| `CIDFontType2` | Descendant font, metrics and glyph mapping |
| `ToUnicodeCMap` | Character-code → UTF-16BE mapping for extraction |
| `Type0Font` | `/Identity-H` composite font linking the descendant and `/ToUnicode` |

`StemV` is explicitly supplied: 80 PDF units in this example. TrueType defines
no universal field for vertical stem thickness. This value therefore does not
come from a hidden constructor estimate. `CapHeight` comes from `OS/2` or the
`H` glyph's box; when unavailable, the factory requires an explicit value.
The core's `FontDescriptor` receives PDF values directly: name, box, angle and
metrics. It does not read TrueType tables. Flags are explicit too: 4 is the
`Symbolic` bit in Table 123, appropriate for this repertoire containing Greek.
The `Symbolic` and `Nonsymbolic` bits cannot be combined.

Core objects check consistency of the **same FontFile2 stream and repertoire**.
Module services connect those objects to program data. The entries they determine
(`/Encoding`, `/FontFile2`, `/W`, `/ToUnicode`, etc.) cannot be replaced or removed
with `with()` or `without()`. Extension entries remain explicit, immutable objects.

## 4. Encode the string supplied to Tj

`/Identity-H` takes a two-byte character code. Here that code is the CID assigned
in the repertoire, not the Unicode code point or GID.

```php
new ShowText($encoder->encode($heading));
```

[`TextEncoder`](https://github.com/PDFToolkit/pdf-fonts/blob/v0.2.0/src/TrueType/TextEncoder.php)
returns a `HexadecimalString`. Objects `Tf`, `Td`, `Tj`, `/Resources`, `/Page`,
`/Pages` and `/Catalog` are then assembled as in the first tutorials. No layout
engine intervenes in this graph.

The `/ToUnicode` stream converts codes to UTF-16BE. Characters outside the Basic
Multilingual Plane use a surrogate pair. `beginbfchar` blocks contain at most
100 mappings, following the CMap syntax used by the specification.

## 5. Explicit limits of this initial embedding support

This example’s TrueType path embeds **every glyph**, without subsetting. It accepts a static sfnt with `glyf`, Unicode cmap 4/12 and horizontal metrics; its `TextEncoder` retains the supplied order without executing GSUB/GPOS. This example is no longer the entire module scope: Fonts 0.2 adds [OpenType layout and CFF embedding](https://pdftoolkit.github.io/modules/fonts/opentype-layout.html), with explicit ligatures, kerning, marks and feature ranges, also for TrueType. CFF1 may come from a selected collection face; a TrueType face is first selected/serialized with OpenType. CFF2/variable embedding, static-instance generation, WOFF and automatic Unicode/bidi composition remain absent.

Tables, segments, groups, metrics, `loca` boundaries and outline structures are
bounded. Composite-glyph references are checked, along with cycles and depth.
Default limits are 32 MiB per font, 256 tables, 65,535 composite-glyph references,
1,024 components per glyph, depth 64 and 1 MiB per `UnicodeText` object.
`/Identity-H` permits 65,535 distinct characters in the repertoire in addition to
CID 0. Table readers use bounded views of program bytes without copying every
table or subtable. Format 12 `cmap` groups and the glyph graph remain in compact
binary storage; their count does not multiply PHP-array allocations. The byte
limit concerns the input program, not the process heap: the application must
also budget memory for the graph and writing.

TrueType instructions are retained as data; the module does not execute them
and is neither a font engine nor a sanitizer for all OpenType tables. An
application accepting external fonts must choose its trust policy and, if
needed, specialized sanitization before supplying bytes to the converter.

`OS/2.fsType` is checked: fonts with restricted embedding or bitmap-only
embedding are rejected. The no-subsetting restriction is respected by full
embedding. `Preview & Print` and `Editable` modes permit embedding and remain
exposed through `embeddingRights`; the application must respect permitted uses
and the font license. This field does not replace the license for redistributing
font files.

`fsType` interpretation follows the OS/2 version: v0/v1 ignore reserved high bits; v0–v2 choose the least restrictive declared permission, while v3+ require exclusive permission bits. These checks do not replace the font licence.

## References

- ISO 32000-1:2008, 9.7.4, 9.7.6, 9.8, 9.9 and 9.10.3; Tables 117, 121–123, 126 and 127.
- [Microsoft OpenType: cmap](https://learn.microsoft.com/en-us/typography/opentype/spec/cmap).
- [Microsoft OpenType: horizontal metrics](https://learn.microsoft.com/en-us/typography/opentype/spec/hmtx).
- [Microsoft OpenType: OS/2 and embedding rights](https://learn.microsoft.com/en-us/typography/opentype/spec/os2).
- [Microsoft OpenType: glyf](https://learn.microsoft.com/en-us/typography/opentype/spec/glyf).

[← 08. Compressed objects](08-object-stream.md) · [All tutorials](README.md) · [10. JPEG and PNG images →](10-image-files.md)
