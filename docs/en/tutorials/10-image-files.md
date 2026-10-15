# 10. Import JPEG and PNG bytes

The [image tutorial](06-images.md) constructs pixels directly. This lesson starts
from encoded files: it separates importing them from their PDF representation
and then their positioning. The example uses the core and image module at the
published versions selected by the [source manifest](../../../resources/sources.json).

Reading these files belongs to the optional
[`pdftoolkit/pdf-images`](https://github.com/PDFToolkit/pdf-images) module. Samples,
DCT images and XObject streams belong to the core. `composer install` in the
core checkout installs the module for examples; an application installs it from
Packagist using `composer require "pdftoolkit/pdf-images:^0.1.12"`. The
[package guide](../packages.md) also explains how to select the core release series.

- **Complete example:** [image-files.php](https://github.com/PDFToolkit/pdf/blob/v0.11.0/examples/image-files.php).
- **Result:** four images on a Letter page, with a checkerboard revealing transparency.
- **Data:** [MIT-licensed synthetic patterns](https://github.com/PDFToolkit/pdf-images/blob/v0.1.12/examples/assets/images/README.md), distributed with the module in `vendor/pdftoolkit/pdf-images/examples/assets/images/`.
- **Prerequisites:** [first document](01-first-document.md), [drawing](03-graphics.md) and [images](06-images.md).

## 1. Supply bytes without delegating file access

`ImageFileBytes` represents the file's byte sequence. Importers receive no paths
and load no URLs. In this example, the application reads four known files from
its own resources, checks for read failure and constructs this object. A web
application decides how to authenticate and limit an upload before supplying its bytes.

```php
use PDF\Images\ImageFileBytes;
use PDF\Images\ImageImportLimits;
use PDF\Images\JpegImageReader;
use PDF\Images\PngImageDecoder;

$limits = new ImageImportLimits(maxEncodedBytes: 1_048_576, maxPixels: 262_144);
$jpeg = (new JpegImageReader($limits))->read(new ImageFileBytes($jpegBytes));
$png = (new PngImageDecoder($limits))->decode(new ImageFileBytes($pngBytes));
```

Limits are objects specific to each importer. Defaults are 16 MiB encoded,
16 MiB decoded, 4,194,304 pixels, 32,768 pixels per dimension and 65,536 chunks
or markers. PNG also counts filter bytes and expanded palette indices. These
ceilings bound codec data; the PHP process also needs memory for temporary
strings and the final document. Dimension products are checked before allocation.

## 2. JPEG: preserve the DCT representation

`JpegImageReader` checks the file's start and end, segment lengths, frame,
components, tables and scan headers. It accepts baseline and progressive 8-bit
Huffman DCT JPEG. It does not decode DCT coefficients or claim to check every
entropy-coded bit: that step belongs to the PDF reader. The encoded file remains unchanged.

The core's `DCTImage` result exposes dimensions, `SampleLayout`, color transform
and bytes. Grayscale uses `/DeviceGray`. RGB JPEG uses `/DeviceRGB` and an explicit
`/ColorTransform`: YCbCr for JFIF, or the Adobe marker's value. Without a marker,
only known component identifiers `1,2,3` or `R,G,B` are accepted.

CMYK requires an Adobe marker with transform 0. Adobe components are inverted,
so the dictionary contains `/Decode [1 0 1 0 1 0 1 0]`. YCCK, depths other than
8 bits, arithmetic coding, lossless frames and embedded ICC profiles are explicitly
rejected. EXIF metadata, including orientation, are not applied automatically.

## 3. PNG: reconstruct samples

`PngImageDecoder` checks the signature, framing, CRC, critical chunks, order of
`IHDR`, `PLTE`, `tRNS`, `IDAT` and `IEND`, and absence of data after the file ends.
Consecutive `IDAT` chunks form one zlib stream. Decompression is bounded by the
exact expected scanline length. Missing zlib endings, extra bytes and unknown
filters are rejected.

`PngScanlineDecoder` reconstructs the None, Sub, Up, Average and Paeth filters.
The result is a `SampledImage`: color `ImageSamples` and, when needed, opacity
`ImageSamples`. Each object describes dimensions, color space, depth and interleaved
bytes. Rows follow file order from the top of the image. Colors are not premultiplied
by alpha.

The decoder supports static **non-interlaced 8-bit** PNG: grayscale, RGB, palette,
gray with alpha and RGBA. Palette indices become RGB samples; `tRNS` becomes an
alpha channel, including color keys for gray and RGB PNG. Alpha 0 is transparent,
255 opaque.

Interlaced PNG, depths of 1, 2, 4 or 16 bits, APNG and ICC profiles are rejected.
Gamma, chromaticity and sRGB indications are not transformed into calibrated PDF
spaces: samples are represented in Device spaces. Other ancillary metadata are
not imported into the PDF.

## 4. Compose the image XObject and its mask

```php
use PDF\Document\Images\ImageXObjectFactory;

$factory = new ImageXObjectFactory();
$jpegStream = $factory->create($jpeg);
$pngStream = $factory->create($png);
```

The service composes a `StreamObject` with Table 89 entry objects: `/Type /XObject`,
`/Subtype /Image`, dimensions, color space and depth. JPEG uses `EncodedData(DCTDecode)`;
PNG samples are compressed with `FlateDecode`. A different Flate compression
level can be injected per object.

`ImageXObjectFactory` is a core component. It receives explicit `DCTImage` or
`SampledImage` values; it parses no PNG or JPEG files. Another library or the
application can construct these objects without installing the module.

Alpha becomes another image stream, eight bits and `/DeviceGray`. An
`IndirectReference` under `/SMask` links it to the main image. The writer discovers
it in the graph and assigns its number without a global registry. The mask must
have matching dimensions; the constructor checks this.

This composition manages entries describing samples and masks: an additional
entry cannot replace `/Width`, `/ColorSpace`, `/Decode` or `/SMask`. Other choices,
such as `/Interpolate`, remain explicit entry objects. As with every stream,
`StreamObject` manages `/Length`, `/Filter` and `/DecodeParms`.

## 5. Reference and paint images

The service adds no page, resource or operator. The example constructs
`/XObject << /JpegRGB … /PngRGBA … >>` in the `ResourceDictionary`, then four
groups of `q`, `cm`, `Do`, `Q`. Matrices set a size of 216 × 162 points and the
position. The 48 × 36 pixel resolution therefore does not determine the PDF's physical size.

The checkerboard is drawn with rectangles and fills before the image. It remains
visible beneath partly transparent PNGs. The two JPEGs show the same pattern in
RGB and CMYK, allowing the direction of `/Decode` to be checked.

## Run

```sh
php examples/image-files.php /tmp/image-files.pdf
qpdf --check /tmp/image-files.pdf
```

Tests compare reconstructed samples to original patterns and exercise the five
filters, masks, CRCs, truncated lengths, invalid palette indices and excessive
zlib data. The PDF result also needs an independent reader; syntax validation
alone cannot confirm colors and opacity.

References: [PNG, W3C](https://www.w3.org/TR/png/),
[JPEG, ITU T.81](https://www.w3.org/Graphics/JPEG/itu-t81.pdf) and ISO 32000-1,
sections 7.4.8 and 8.9.
