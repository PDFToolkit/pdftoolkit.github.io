# 19. Predict rows before compression

The [complete script](https://github.com/PDFToolkit/pdf/blob/v0.11.0/examples/filters-predictors.php)
draws the same RGB pixels three times: Flate/Paeth, LZW/TIFF and adaptive LZW/PNG.

```sh
php examples/filters-predictors.php filters-predictors.pdf
```

Bytes are PDF samples, three eight-bit components per pixel, row by row. They
are not a PNG or TIFF file. `PredictorLayout` expresses `Colors`, `Columns` and
`BitsPerComponent`.

TIFF subtracts the preceding sample of the same component, including at depths
of 1, 2, 4 and 16 bits. PNG works on bytes and prefixes each row with the selected
filter. Paeth uses the left, upper and upper-left neighbors; adaptive selection
examines possibilities for each row.

`FlateDecode` or `LZWDecode` composes prediction before compression.
`StreamObject` uses those same objects to write `/Filter`, `/DecodeParms` and
length. LZW grows codes from 9 to 12 bits, then resets its dictionary.
`EarlyChange` selects boundaries according to the two permitted conventions;
decompressed pixels remain identical.

Changing depth requires adapting data, packing and the image dictionary together.
Changing `BitsPerComponent` alone does not convert bytes. CI compares a large
corpus against an independent oracle and qpdf: width changes, resets, depths
and partial rows.

Reference: ISO 7.4.4, physical pages 28–33.

[Index](README.md) · [Complete code](https://github.com/PDFToolkit/pdf/blob/v0.11.0/examples/filters-predictors.php)
